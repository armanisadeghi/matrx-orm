from contextlib import asynccontextmanager
from matrx_orm.exceptions import (
    ORMException,
    CacheError,
)
from matrx_utils import vcprint


@asynccontextmanager
async def handle_orm_operation(operation_name, model=None, **context):
    """Context manager for handling ORM operations with proper error encapsulation.

    ORM exceptions pass through without re-printing — they're already formatted.
    Only truly unexpected (non-ORM) errors get logged and wrapped here.
    """
    try:
        yield
    except ORMException:
        raise
    except Exception as e:
        model_name = model.__name__ if model else "Unknown"
        vcprint(
            f"[{model_name}] Unexpected error in {operation_name}: {e.__class__.__name__}: {e}",
            "UnexpectedError",
            color="red",
        )
        raise CacheError(
            model=model, operation=operation_name, details=context, original_error=e
        )
