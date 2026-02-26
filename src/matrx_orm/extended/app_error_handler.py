from functools import wraps
import traceback
import asyncio
from typing import Callable, TypeVar, overload

DEFAULT_CLIENT_MESSAGE = "Oops. Something went wrong. Please reload the page and try again."

_F = TypeVar("_F", bound=Callable[..., object])


class AppError(Exception):
    def __init__(
        self,
        message: str,
        error_type: str = "GenericError",
        client_visible: str | None = None,
        context: dict[str, object] | None = None,
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


@overload
def handle_errors(func: _F) -> _F: ...
@overload
def handle_errors(func: Callable[..., object]) -> Callable[..., object]: ...

def handle_errors(func: _F) -> _F:
    """Smart error handler that works with both sync and async functions.
    
    Preserves the decorated function's type signature for static analysis.
    """
    
    def _handle_exception(e: Exception, cls_or_self: object, func_name: str) -> None:
        """Common error handling logic for both sync and async."""
        if isinstance(e, AppError):
            raise

        from matrx_orm.exceptions import ORMException

        if isinstance(cls_or_self, type):
            class_name = cls_or_self.__name__
        else:
            class_name = cls_or_self.__class__.__name__

        model_name = None
        if hasattr(cls_or_self, 'model') and hasattr(cls_or_self.model, '__name__'):
            model_name = cls_or_self.model.__name__

        context: dict[str, object] = {
            "manager": class_name,
            "method": func_name,
        }
        if model_name:
            context["model"] = model_name

        if hasattr(cls_or_self, "_get_error_context") and callable(cls_or_self._get_error_context):
            try:
                context.update(cls_or_self._get_error_context())
            except Exception:
                pass

        if isinstance(e, ORMException):
            context["orm_model"] = e.model
            if e.details:
                for key in ("query", "params", "filters", "args", "operation"):
                    if key in e.details:
                        context[key] = e.details[key]
            if getattr(e, "_caller_frames", None):
                context["caller_frames"] = e._caller_frames
            error_message = e.message
        else:
            error_message = f"{type(e).__name__}: {e}"

        raise AppError(
            message=error_message,
            error_type=e.__class__.__name__,
            client_visible=DEFAULT_CLIENT_MESSAGE,
            context=context,
        ) from e
    
    if asyncio.iscoroutinefunction(func):
        @wraps(func)
        async def async_wrapper(cls_or_self: object, *args: object, **kwargs: object) -> object:
            try:
                return await func(cls_or_self, *args, **kwargs)
            except Exception as e:
                _handle_exception(e, cls_or_self, func.__name__)
        
        return async_wrapper  # type: ignore[return-value]
    else:
        @wraps(func)
        def sync_wrapper(cls_or_self: object, *args: object, **kwargs: object) -> object:
            try:
                return func(cls_or_self, *args, **kwargs)
            except Exception as e:
                _handle_exception(e, cls_or_self, func.__name__)
        
        return sync_wrapper  # type: ignore[return-value]
