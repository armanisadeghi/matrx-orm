from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, TYPE_CHECKING

from matrx_orm.core.registry import get_model_by_name
from .fields import Field
from functools import cached_property

if TYPE_CHECKING:
    from matrx_orm.core.base import Model


@dataclass
class ForeignKeyReference:
    column_name: str
    to_model: str | type[Model]
    to_column: str
    related_name: str | None = None
    is_native: bool = False
    on_delete: str = "CASCADE"
    on_update: str = "CASCADE"

    @cached_property
    def _related_model(self) -> type[Model]:
        return get_model_by_name(self.to_model) if isinstance(self.to_model, str) else self.to_model

    @property
    def model(self) -> type[Model]:
        """Returns the related model class"""
        return self._related_model

    @property
    def field(self) -> str:
        """Returns the field name on this model"""
        return self.column_name

    @property
    def field_name(self) -> str:
        return self.column_name

    @property
    def related_model(self) -> type[Model]:
        return self._related_model

    @property
    def related_column(self) -> str:
        return self.to_column

    async def fetch_data(self, instance: Model, column_value: Any) -> Model | None:
        """
        Fetches the related object based on the foreign key value and stores it in the instance

        Args:
            instance: The model instance we're fetching related data for
            column_value: The value stored in this model's foreign key field
        """
        filter_kwargs = {self.to_column: column_value}
        related_object = await self.related_model.get(**filter_kwargs)
        instance.set_related(self.column_name, related_object)
        return related_object


@dataclass
class InverseForeignKeyReference:
    """Tracks an inverse foreign key relationship"""

    from_model: str | type[Model]
    from_field: str
    referenced_field: str
    related_name: str | None = None
    is_native: bool = False

    @cached_property
    def _related_model(self) -> type[Model]:
        return get_model_by_name(self.from_model) if isinstance(self.from_model, str) else self.from_model

    @property
    def model(self) -> type[Model]:
        """Returns the related model class"""
        return self._related_model

    @property
    def field(self) -> str:
        """Returns the field name on the related model"""
        return self.from_field

    @property
    def related_model(self) -> type[Model]:
        return self._related_model

    async def fetch_data(self, instance: Model, referenced_value: Any = None) -> list[Model]:
        """
        Fetches all related objects based on the foreign key value and stores them in the instance

        Args:
            instance: The model instance we're fetching related data for
            referenced_value: Optional value override. If not provided, gets from referenced_field
        """
        if referenced_value is None:
            referenced_value = getattr(instance, self.referenced_field)

        if referenced_value is not None:
            filter_kwargs = {self.from_field: referenced_value}
            related_objects = await self.related_model.filter(**filter_kwargs).all()

            relation_name = self.related_name or self.from_field
            instance.set_related(relation_name, related_objects, is_inverse=True)
            return related_objects
        return []


class LazyRelation:
    instance: Model
    field: Any
    cache_name: str

    def __init__(self, instance: Model, field: Any) -> None:
        self.instance = instance
        self.field = field
        self.cache_name = f"_{field.name}_cache"

    async def __call__(self) -> Any:
        if hasattr(self.instance, self.cache_name):
            return getattr(self.instance, self.cache_name)
        related = await self.field.get_related_objects(self.instance)
        setattr(self.instance, self.cache_name, related)
        return related


class RelationDescriptor:
    field: Any
    cache_name: str

    def __init__(self, field: Any) -> None:
        self.field = field
        self.cache_name = f"_{field.name}_cache"

    def __get__(self, instance: Model | None, owner: type[Model]) -> Any:
        if instance is None:
            return self
        if hasattr(instance, self.cache_name):
            return getattr(instance, self.cache_name)
        if not self.field.lazy:
            return RelationLoader(instance, self.field).load
        return LazyRelation(instance, self.field)

    def __set__(self, instance: Model, value: Any) -> None:
        if value is None:
            setattr(instance, self.cache_name, None)
            return
        if isinstance(value, dict):
            if self.field.composite:
                setattr(instance, self.cache_name, value)
            else:
                raise ValueError("Cannot assign dictionary to non-composite foreign key")
        elif isinstance(value, self.field.resolve_model()):
            setattr(instance, self.cache_name, value)
        else:
            raise ValueError(f"Invalid value type for relation field: {type(value)}")


class RelationField(Field):
    to_model: str | type[Model]
    related_name: str | None
    on_delete: str
    on_update: str
    lazy: bool
    through: str | None
    _related_model: type[Model] | None

    def __init__(self, to_model: str | type[Any], **kwargs: Any) -> None:
        kwargs["is_native"] = kwargs.get("is_native", False)
        super().__init__("", **kwargs)
        self.to_model = to_model
        self.related_name = kwargs.get("related_name")
        self.on_delete = kwargs.get("on_delete", "CASCADE")
        self.on_update = kwargs.get("on_update", "CASCADE")
        self.lazy = kwargs.get("lazy", True)
        self.through = kwargs.get("through")
        self._related_model = None

    def contribute_to_class(self, model: type[Model], name: str) -> None:
        self.model = model
        self.name = name
        setattr(model, name, RelationDescriptor(self))

    def resolve_model(self) -> type[Model]:
        if self._related_model is None:
            if isinstance(self.to_model, str):
                from .registry import get_model_by_name

                self._related_model = get_model_by_name(self.to_model)
            else:
                self._related_model = self.to_model
        return self._related_model

    def get_field_type(self) -> str:
        related_model = self.resolve_model()
        primary_keys = related_model._meta.primary_keys
        if len(primary_keys) == 1:
            pk_field = related_model._fields[primary_keys[0]]
            return pk_field.db_type
        else:
            return "JSONB"


class ForeignKey(RelationField):
    composite: bool

    def __init__(self, to_model: str | type[Any], **kwargs: Any) -> None:
        super().__init__(to_model, **kwargs)
        self.composite = False
        self.db_type = None

    def contribute_to_class(self, model: type[Model], name: str) -> None:
        super().contribute_to_class(model, name)
        self.db_type = self.get_field_type()
        related_model = self.resolve_model()
        self.composite = len(related_model._meta.primary_keys) > 1

    async def get_related_objects(self, instance: Model) -> Model | None:
        related_model = self.resolve_model()
        if self.composite:
            key_values = getattr(instance, self.name)
            if not key_values:
                return None
            filter_kwargs = {key: key_values[key] for key in related_model._meta.primary_keys}
        else:
            key_value = getattr(instance, self.name)
            if not key_value:
                return None
            filter_kwargs = {related_model._meta.primary_keys[0]: key_value}
        return await related_model.get(**filter_kwargs)

    async def handle_on_delete(self, instance: Model) -> None:
        if self.on_delete == "CASCADE":
            related_instance = await self.get_related_objects(instance)
            if related_instance:
                await related_instance.delete()
        elif self.on_delete == "SET_NULL":
            if self.composite:
                setattr(instance, self.name, {})
            else:
                setattr(instance, self.name, None)
            await instance.save()

    def get_db_prep_value(self, value: Any) -> Any:
        if value is None:
            return None
        if self.composite:
            related_model = self.resolve_model()
            if not all(key in value for key in related_model._meta.primary_keys):
                raise ValueError(f"Missing required keys for composite foreign key: {related_model._meta.primary_keys}")
            return value
        return value

    def from_db_value(self, value: Any) -> Any:
        if value is None:
            return None
        if self.composite:
            if isinstance(value, str):
                return json.loads(value)
            return value
        return value


class RelationLoader:
    instance: Model
    field: Any

    def __init__(self, instance: Model, field: Any) -> None:
        self.instance = instance
        self.field = field

    @cached_property
    async def load(self) -> Any:
        return await self.field.get_related_objects(self.instance)


class OneToOneField(ForeignKey):
    def __init__(self, to_model: str | type[Any], **kwargs: Any) -> None:
        kwargs["unique"] = True
        super().__init__(to_model, **kwargs)
