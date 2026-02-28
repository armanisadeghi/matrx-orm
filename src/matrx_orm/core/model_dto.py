from __future__ import annotations

from enum import Enum
from typing import Any, TypeVar
from uuid import UUID

from matrx_orm.core.base import Model
from matrx_orm.extended.app_error_handler import AppError, handle_errors

ModelT = TypeVar("ModelT", bound=Model)

info = True
debug = False
verbose = False


class BaseDTO:
    """
    Legacy data-transfer object layer.

    .. deprecated::
        BaseDTO is superseded by :class:`matrx_orm.ModelView`.
        ModelView stores results flat on the model instance (no duplication,
        no ``result["dto"]`` nesting), supports declarative prefetch / exclude /
        inline_fk, and runs computed fields concurrently.

        Migration path:

            # Before (DTO)
            class OrderDTO(BaseDTO):
                id: str
                customer_name: str
                async def _initialize_dto(self, model):
                    self.id = str(model.id)
                    customer = await model.fetch_fk("customer_id")
                    self.customer_name = customer.full_name if customer else ""

            # After (ModelView)
            class OrderView(ModelView):
                prefetch = ["customer_id"]
                inline_fk = {"customer_id": "customer"}
                async def customer_name(self, model) -> str:
                    customer = model.get_related("customer_id")
                    return customer.full_name if customer else ""

        Existing BaseDTO subclasses continue to work without any changes.
        Migration is entirely opt-in — move to ModelView when ready.
    """

    id: str
    _model: Model | None = None

    @classmethod
    @handle_errors
    async def from_model(cls, model: Model) -> BaseDTO:
        import inspect
        id_str = str(model.id)
        try:
            sig = inspect.signature(cls.__init__)
            if "id" in sig.parameters:
                instance: BaseDTO = cls(**{"id": id_str})  # type: ignore[call-arg]
            else:
                instance = cls()  # type: ignore[call-arg]
                instance.id = id_str
        except (TypeError, ValueError):
            instance = cls()  # type: ignore[call-arg]
            instance.id = id_str
        instance._model = model
        if hasattr(model, "runtime"):
            model.runtime.dto = instance
        await instance._initialize_dto(model)
        return instance

    async def _initialize_dto(self, model: Model) -> None:
        pass

    def _get_error_context(self) -> dict[str, str]:
        return {
            "dto": self.__class__.__name__,
            "id": self.id if hasattr(self, "id") else "Unknown",
            "model": self._model.__class__.__name__
            if self._model
            else "No model attached",
        }

    def _report_error(
        self,
        message: str,
        error_type: str = "GenericError",
        client_visible: str | None = None,
    ) -> AppError:
        return AppError(
            message=message,
            error_type=error_type,
            client_visible=client_visible,
            context=self._get_error_context(),
        )

    def __getattr__(self, name: str) -> Any:
        if self._model and hasattr(self._model, name):
            return getattr(self._model, name)
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    @handle_errors
    async def fetch_fk(self, field_name: str) -> Model | None:
        if not self._model:
            raise AttributeError("No model instance attached to DTO")
        result = await self._model.fetch_fk(field_name)
        self._model.runtime.set_relationship(field_name, result)
        return result

    @handle_errors
    async def fetch_ifk(self, field_name: str) -> list[Model]:
        if not self._model:
            raise AttributeError("No model instance attached to DTO")
        result = await self._model.fetch_ifk(field_name)
        self._model.runtime.set_relationship(field_name, result)
        return result

    @handle_errors
    async def fetch_one_relation(self, field_name: str) -> Model | list[Model] | None:
        if not self._model:
            raise AttributeError("No model instance attached to DTO")
        result = await self._model.fetch_one_relation(field_name)
        self._model.runtime.set_relationship(field_name, result)
        return result

    @handle_errors
    async def filter_fk(self, field_name: str, **kwargs: Any) -> list[Model]:
        if not self._model:
            raise AttributeError("No model instance attached to DTO")
        result = await self._model.filter_fk(field_name, **kwargs)
        self._model.runtime.set_relationship(field_name, result)
        return result

    @handle_errors
    async def filter_ifk(self, field_name: str, **kwargs: Any) -> list[Model]:
        if not self._model:
            raise AttributeError("No model instance attached to DTO")
        result = await self._model.filter_ifk(field_name, **kwargs)
        self._model.runtime.set_relationship(field_name, result)
        return result

    def _serialize_value(self, value: Any, visited: set[int]) -> Any:
        if value is None:
            return None

        if id(value) in visited:
            return f"<Circular reference to {type(value).__name__}>"
        visited.add(id(value))

        if isinstance(value, (str, int, float, bool)):
            return value

        if isinstance(value, Enum):
            return value.value

        if isinstance(value, UUID):
            return str(value)

        if isinstance(value, (list, tuple)):
            return [self._serialize_value(item, visited.copy()) for item in value]

        if isinstance(value, dict):
            return {
                k: self._serialize_value(v, visited.copy()) for k, v in value.items()
            }

        if isinstance(value, BaseDTO):
            return value.to_dict(visited=visited.copy())

        if hasattr(value, "to_dict") and callable(value.to_dict):
            return value.to_dict()

        return str(value)

    def to_dict(self, visited: set[int] | None = None) -> dict[str, Any]:
        if visited is None:
            visited = set()

        if id(self) in visited:
            return {
                "__circular__": f"<Circular reference to {self.__class__.__name__}>"
            }
        visited.add(id(self))

        base_dict: dict[str, Any] = {}
        for key in self.__annotations__:
            if hasattr(self, key):
                value = getattr(self, key)
                if value is not None:
                    base_dict[key] = self._serialize_value(value, visited.copy())

        return base_dict

    def print_keys(self) -> None:
        print(f"\n{self.__class__.__name__} Keys:")
        for key in self.__annotations__.keys():
            data_type = self.__annotations__[key]
            print(
                f"-> {key}: {data_type.__name__ if hasattr(data_type, '__name__') else str(data_type)}"
            )
        print()

    def __repr__(self) -> str:
        return str(self.to_dict())
