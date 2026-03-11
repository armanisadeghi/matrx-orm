"""Async write queue that gates write operations behind the connection pool.

Instead of every concurrent write racing to ``pool.acquire()`` and timing out,
writes are submitted to an ``asyncio.Queue``, drained through an
``asyncio.Semaphore`` that caps how many writes can hold pool connections at
once, and executed with retry + exponential backoff.

Callers still ``await`` the result — they block on a ``Future`` that resolves
when the write completes or fails.  Reads are **not** affected; they continue
to acquire pool connections directly.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable, Coroutine

from matrx_orm.exceptions import WriteQueueFullError, WriteQueueTimeoutError

logger = logging.getLogger("matrx_orm.write_queue")

_WriteCoroutineFactory = Callable[[], Coroutine[Any, Any, Any]]


class _QueueItem:
    __slots__ = ("coro_factory", "future")

    def __init__(self, coro_factory: _WriteCoroutineFactory, future: asyncio.Future[Any]) -> None:
        self.coro_factory = coro_factory
        self.future = future


class WriteQueue:
    """Per-database async write queue.

    Parameters match the ``DatabaseProjectConfig`` fields:
    - ``write_concurrency`` — max simultaneous writes (semaphore size).
    - ``write_queue_size`` — max pending writes before ``WriteQueueFullError``.
    - ``write_queue_timeout`` — max seconds a write waits before ``WriteQueueTimeoutError``.
    """

    def __init__(
        self,
        config_name: str,
        write_concurrency: int = 10,
        write_queue_size: int = 200,
        write_queue_timeout: float = 30.0,
    ) -> None:
        self.config_name = config_name
        self.write_concurrency = write_concurrency
        self.write_queue_size = write_queue_size
        self.write_queue_timeout = write_queue_timeout

        self._semaphore = asyncio.Semaphore(write_concurrency)
        self._queue: asyncio.Queue[_QueueItem] = asyncio.Queue(maxsize=write_queue_size)
        self._drain_task: asyncio.Task[None] | None = None

    @property
    def pending(self) -> int:
        return self._queue.qsize()

    @property
    def active_writes(self) -> int:
        return self.write_concurrency - self._semaphore._value

    async def submit(self, coro_factory: _WriteCoroutineFactory) -> Any:
        """Enqueue a write and wait for it to execute.

        ``coro_factory`` is a zero-arg callable that returns a new coroutine
        each time it is called (needed so retries can create fresh coroutines).

        Returns the result of the coroutine or raises its exception.
        """
        loop = asyncio.get_running_loop()
        future: asyncio.Future[Any] = loop.create_future()
        item = _QueueItem(coro_factory, future)

        try:
            self._queue.put_nowait(item)
        except asyncio.QueueFull:
            raise WriteQueueFullError(
                config_name=self.config_name,
                queue_size=self.write_queue_size,
            )

        self._ensure_drain_running()

        try:
            return await asyncio.wait_for(future, timeout=self.write_queue_timeout)
        except asyncio.TimeoutError:
            future.cancel()
            raise WriteQueueTimeoutError(
                config_name=self.config_name,
                timeout=self.write_queue_timeout,
            )

    def _ensure_drain_running(self) -> None:
        if self._drain_task is None or self._drain_task.done():
            self._drain_task = asyncio.ensure_future(self._drain_loop())

    async def _drain_loop(self) -> None:
        """Pull items from the queue and execute them, gated by the semaphore."""
        while True:
            try:
                item = self._queue.get_nowait()
            except asyncio.QueueEmpty:
                return

            if item.future.cancelled() or item.future.done():
                self._queue.task_done()
                continue

            asyncio.ensure_future(self._execute_item(item))

    async def _execute_item(self, item: _QueueItem) -> None:
        """Execute a single queued write behind the semaphore."""
        try:
            async with self._semaphore:
                if item.future.cancelled() or item.future.done():
                    return
                try:
                    result = await item.coro_factory()
                    if not item.future.done():
                        item.future.set_result(result)
                except BaseException as exc:
                    if not item.future.done():
                        item.future.set_exception(exc)
        except BaseException as exc:
            if not item.future.done():
                item.future.set_exception(exc)
        finally:
            self._queue.task_done()


class WriteQueueRegistry:
    """Singleton mapping config_name -> WriteQueue, created lazily."""

    _instance: WriteQueueRegistry | None = None
    _queues: dict[str, WriteQueue]

    def __new__(cls) -> WriteQueueRegistry:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._queues = {}
        return cls._instance

    def get_or_create(
        self,
        config_name: str,
        write_concurrency: int = 10,
        write_queue_size: int = 200,
        write_queue_timeout: float = 30.0,
    ) -> WriteQueue:
        if config_name not in self._queues:
            self._queues[config_name] = WriteQueue(
                config_name=config_name,
                write_concurrency=write_concurrency,
                write_queue_size=write_queue_size,
                write_queue_timeout=write_queue_timeout,
            )
        return self._queues[config_name]

    def get(self, config_name: str) -> WriteQueue | None:
        return self._queues.get(config_name)

    def enable(
        self,
        config_name: str,
        write_concurrency: int = 10,
        write_queue_size: int = 200,
        write_queue_timeout: float = 30.0,
    ) -> WriteQueue:
        """Force-enable (or re-create) a queue for a database at runtime."""
        self._queues[config_name] = WriteQueue(
            config_name=config_name,
            write_concurrency=write_concurrency,
            write_queue_size=write_queue_size,
            write_queue_timeout=write_queue_timeout,
        )
        return self._queues[config_name]

    def clear(self) -> None:
        self._queues.clear()


_registry = WriteQueueRegistry()


# Tracks which databases had queuing auto-activated so we only log once.
_auto_activated: set[str] = set()


def maybe_activate_queue(config_name: str, error: BaseException) -> None:
    """Auto-enable the write queue when a connection timeout is detected.

    Called from the ``AsyncDatabaseManager`` timeout handler. If the queue was
    already enabled (via config or a prior auto-activation), this is a no-op.
    """
    if config_name in _auto_activated:
        return

    err_msg = str(error).lower()
    if "timeout" not in err_msg and "too many connections" not in err_msg:
        return

    from matrx_orm.core.config import get_database_config
    try:
        cfg = get_database_config(config_name)
    except Exception:
        return

    _registry.enable(
        config_name=config_name,
        write_concurrency=cfg.get("write_concurrency", 10),
        write_queue_size=cfg.get("write_queue_size", 200),
        write_queue_timeout=cfg.get("write_queue_timeout", 30.0),
    )
    _auto_activated.add(config_name)
    logger.warning(
        "[matrx_orm] Write queue auto-activated for '%s' after pool saturation error: %s",
        config_name,
        error,
    )


def get_write_queue_registry() -> WriteQueueRegistry:
    return _registry
