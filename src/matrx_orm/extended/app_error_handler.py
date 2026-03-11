from collections.abc import Mapping
from functools import wraps
import inspect
import sys
import traceback
from typing import Callable, Protocol, TypeVar, runtime_checkable

DEFAULT_CLIENT_MESSAGE = "Oops. Something went wrong. Please reload the page and try again."

_F = TypeVar("_F", bound=Callable[..., object])


@runtime_checkable
class _HasErrorContext(Protocol):
    def _get_error_context(self) -> Mapping[str, object]: ...


@runtime_checkable
class _HasModel(Protocol):
    model: type


class AppError(Exception):
    def __init__(
        self,
        message: str,
        error_type: str = "GenericError",
        client_visible: str | None = None,
        context: Mapping[str, object] | None = None,
    ):
        self.error: dict[str, object] = {
            "status": "error",
            "type": error_type,
            "message": message,
            "client_visible": client_visible if client_visible is not None else DEFAULT_CLIENT_MESSAGE,
            "context": context or {},
            "traceback": traceback.format_exc() if traceback.format_exc() != "None\n" else "No traceback available",
        }
        super().__init__(message)


def handle_errors(func: _F) -> _F:
    """Smart error handler that works with both sync and async functions.

    Preserves the decorated function's type signature for static analysis.
    """

    def _make_app_error(e: Exception, cls_or_self: object, func_name: str) -> AppError:
        """Wrap an exception in an AppError. Returns (never raises) the AppError."""
        from matrx_orm.exceptions import ORMException

        if isinstance(cls_or_self, type):
            class_name = cls_or_self.__name__
        else:
            class_name = type(cls_or_self).__name__

        context: dict[str, object] = {
            "manager": class_name,
            "method": func_name,
        }

        if isinstance(cls_or_self, _HasModel):
            context["model"] = cls_or_self.model.__name__

        if isinstance(cls_or_self, _HasErrorContext):
            try:
                extra = cls_or_self._get_error_context()
                context.update(extra)
            except Exception:
                pass

        if isinstance(e, ORMException):
            context["orm_model"] = e.model
            if e.details:
                for key in ("query", "params", "filters", "args", "operation"):
                    if key in e.details:
                        context[key] = e.details[key]
            caller_frames = getattr(e, "_caller_frames", None)
            if caller_frames:
                context["caller_frames"] = caller_frames
            error_message = e.message
        else:
            error_message = f"{type(e).__name__}: {e}"

        app_error = AppError(
            message=error_message,
            error_type=e.__class__.__name__,
            client_visible=DEFAULT_CLIENT_MESSAGE,
            context=context,
        )
        # Always print — the caller may swallow the exception, but the error
        # must never be invisible.
        print(
            f"\n[ORM ERROR] {e.__class__.__name__} in {class_name}.{func_name}(): {error_message}",
            file=sys.stderr,
        )
        if context.get("query"):
            print(f"  Query:  {context['query']}", file=sys.stderr)
        if context.get("args"):
            print(f"  Args:   {context['args']}", file=sys.stderr)
        if context.get("operation"):
            print(f"  Op:     {context['operation']}", file=sys.stderr)
        return app_error

    if inspect.iscoroutinefunction(func):
        @wraps(func)
        async def async_wrapper(cls_or_self: object, *args: object, **kwargs: object) -> object:
            try:
                return await func(cls_or_self, *args, **kwargs)
            except AppError:
                raise
            except Exception as e:
                raise _make_app_error(e, cls_or_self, func.__name__) from e

        return async_wrapper  # type: ignore[return-value]
    else:
        @wraps(func)
        def sync_wrapper(cls_or_self: object, *args: object, **kwargs: object) -> object:
            try:
                return func(cls_or_self, *args, **kwargs)
            except AppError:
                raise
            except Exception as e:
                raise _make_app_error(e, cls_or_self, func.__name__) from e

        return sync_wrapper  # type: ignore[return-value]
