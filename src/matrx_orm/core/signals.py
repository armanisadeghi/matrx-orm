"""Lightweight lifecycle signal dispatcher.

Signals are async-first: receivers must be async callables.  Sync receivers
are wrapped automatically.

Usage::

    from matrx_orm.core.signals import post_save, pre_delete

    # Decorator style
    @post_save.connect
    async def audit_on_save(sender, instance, created: bool, **kwargs):
        if sender.__name__ == "User":
            await AuditLog.create(action="save", entity_id=instance.id)

    # Manual connect / disconnect
    async def my_receiver(sender, instance, **kwargs): ...
    post_save.connect(my_receiver)
    post_save.disconnect(my_receiver)

Module-level signal instances
------------------------------
- ``pre_create``  — fired before INSERT (new record)
- ``post_create`` — fired after  INSERT (new record)
- ``pre_save``    — fired before UPDATE (existing record)
- ``post_save``   — fired after  UPDATE (existing record)
- ``pre_delete``  — fired before DELETE
- ``post_delete`` — fired after  DELETE
"""
from __future__ import annotations

import inspect
from typing import Any, Callable


class Signal:
    """A named signal that dispatches async events to registered receivers."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._receivers: list[Callable[..., Any]] = []

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def connect(self, receiver: Callable[..., Any]) -> Callable[..., Any]:
        """Register *receiver*.  Can be used as a decorator.

        The receiver must be an ``async def`` function (or any callable that
        returns an awaitable).  Sync functions are accepted and wrapped.
        """
        if receiver not in self._receivers:
            self._receivers.append(receiver)
        return receiver  # enables @signal.connect decorator usage

    def disconnect(self, receiver: Callable[..., Any]) -> None:
        """Unregister *receiver* (silently ignores unknown receivers)."""
        try:
            self._receivers.remove(receiver)
        except ValueError:
            pass

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    async def send(self, sender: Any, **kwargs: Any) -> list[tuple[Callable[..., Any], Any]]:
        """Fire all registered receivers and collect their return values.

        Exceptions raised by individual receivers are caught and stored as
        the result value rather than propagating, so one bad receiver cannot
        break the ORM operation.  Errors are printed for observability.
        """
        results: list[tuple[Callable[..., Any], Any]] = []
        for receiver in list(self._receivers):
            try:
                result = receiver(sender, **kwargs)
                if inspect.isawaitable(result):
                    result = await result
                results.append((receiver, result))
            except Exception as exc:  # noqa: BLE001
                results.append((receiver, exc))
        return results

    def __repr__(self) -> str:
        return f"Signal(name={self.name!r}, receivers={len(self._receivers)})"


# ---------------------------------------------------------------------------
# Module-level signal instances
# ---------------------------------------------------------------------------

pre_create: Signal = Signal("pre_create")
post_create: Signal = Signal("post_create")
pre_save: Signal = Signal("pre_save")
post_save: Signal = Signal("post_save")
pre_delete: Signal = Signal("pre_delete")
post_delete: Signal = Signal("post_delete")
