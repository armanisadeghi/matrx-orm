from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass
from typing import Any, ClassVar
from uuid import UUID

from matrx_utils import vcprint
from matrx_orm.exceptions import (
    DoesNotExist,
    MultipleObjectsReturned,
    ORMException,
    ValidationError,
)
from matrx_orm.operations import create, delete, update
from matrx_orm.state import CachePolicy, StateManager

from ..query.builder import QueryBuilder
from .async_db_manager import run_sync
from .fields import Field, ForeignKey
from .relations import (
    ForeignKeyReference,
    InverseForeignKeyReference,
    ManyToManyReference,
    ManyToManyField,
)

file_name = "matrx_orm/orm/core/base.py"


def _to_snake_case(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def formated_error(
    message: str,
    class_name: str | None = None,
    method_name: str | None = None,
    context: Any = None,
) -> None:
    vcprint("\n" + "=" * 80 + "\n", color="red")
    if class_name and method_name:
        vcprint(f"[ERROR in {file_name}: {class_name}.{method_name}()]\n", color="red")
        if context:
            vcprint(context, "Context", color="red", pretty=True)
    else:
        vcprint(f"[ERROR in {file_name}]\n", color="red")
        if context:
            vcprint(context, "Context", color="red", pretty=True)
    print()
    vcprint(message, color="red")
    vcprint("\n" + "=" * 80 + "\n", color="red")


class RuntimeContainer:
    _data: dict[str, Any]
    _relationships: dict[str, Any]
    dto: Any

    def __init__(self) -> None:
        self._data = {}
        self._relationships = {}
        self.dto = None

    def __getattr__(self, name: str) -> Any:
        if name in self._relationships:
            return self._relationships[name]
        return self._data.get(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name in ("_data", "_relationships", "dto"):
            super().__setattr__(name, value)
        elif name in self._relationships:
            self._relationships[name] = value
        else:
            self._data[name] = value

    def set_relationship(self, name: str, value: Any) -> None:
        """Store a fetched relationship."""
        self._relationships[name] = value
        if self.dto:
            setattr(self.dto, name, value)

    def to_dict(self) -> dict[str, Any]:
        data_dict: dict[str, Any] = {
            k: str(v) if isinstance(v, UUID) else v for k, v in self._data.items()
        }
        rel_dict: dict[str, Any] = {}
        for k, v in self._relationships.items():
            if isinstance(v, list):
                rel_dict[k] = [
                    item.to_dict() if hasattr(item, "to_dict") else str(item)
                    for item in v
                ]
            elif v and hasattr(v, "to_dict"):
                rel_dict[k] = v.to_dict()
            else:
                rel_dict[k] = str(v) if v else None
        return {**data_dict, **rel_dict}


class RuntimeMixin:
    runtime: RuntimeContainer

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.runtime = RuntimeContainer()
        self._initialize_runtime()

    def _initialize_runtime(self) -> None:
        """Override in model-specific classes"""
        pass

    def to_dict(self) -> dict[str, Any]:
        base_dict: dict[str, Any] = super().to_dict()  # type: ignore[misc]
        runtime_dict = self.runtime.to_dict()
        return {**base_dict, **runtime_dict}


@dataclass
class ModelOptions:
    table_name: str
    database: str
    fields: dict[str, Field]
    primary_keys: list[str]
    unique_fields: set[str]
    foreign_keys: dict[str, ForeignKeyReference]
    inverse_foreign_keys: dict[str, InverseForeignKeyReference]
    indexes: list[Any]
    unique_together: list[Any]
    constraints: list[Any]
    db_schema: str | None = None
    unfetchable: bool = False
    many_to_many_keys: dict[str, ManyToManyReference] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.many_to_many_keys is None:
            self.many_to_many_keys = {}

    @property
    def qualified_table_name(self) -> str:
        if self.db_schema:
            return f"{self.db_schema}.{self.table_name}"
        return self.table_name


class ModelMeta(type):
    def __new__(
        mcs, name: str, bases: tuple[type, ...], attrs: dict[str, Any]
    ) -> ModelMeta:
        if name == "Model":
            return super().__new__(mcs, name, bases, attrs)

        # ------------------------------------------------------------------
        # Abstract models: skip table/field wiring entirely.
        # Subclasses of an abstract model inherit its field definitions via
        # normal Python class inheritance — ModelMeta will process them when
        # the concrete subclass is created.
        # ------------------------------------------------------------------
        meta_inner = attrs.get("Meta") or attrs.get("_meta_class")
        is_abstract = False
        if meta_inner is not None and getattr(meta_inner, "abstract", False):
            is_abstract = True
        if not is_abstract and attrs.get("_abstract", False):
            is_abstract = True
        # Also honour abstract declared on a parent's Meta
        for base in bases:
            base_meta = getattr(base, "_meta", None)
            if base_meta is None:
                continue
            if getattr(base_meta, "abstract", False) or getattr(
                base, "_abstract", False
            ):
                # The parent is abstract; concrete children are fine to continue
                break

        if is_abstract:
            attrs["_abstract"] = True
            # Still process field descriptors so subclasses can inherit them
            cls = super().__new__(mcs, name, bases, attrs)
            return cls

        fields = {}
        foreign_keys = {}
        inverse_foreign_keys = {}
        many_to_many_keys: dict[str, ManyToManyReference] = {}
        unique_fields = set()
        primary_keys = []
        dynamic_fields = set()
        pending_junction_tables: list[dict[str, Any]] = []

        # Collect inherited fields from abstract base classes first so that
        # concrete model attrs can override them.
        inherited_attrs: dict[str, Any] = {}
        for base in reversed(bases):
            if getattr(base, "_abstract", False):
                for k, v in vars(base).items():
                    if isinstance(
                        v, (Field, InverseForeignKeyReference, ManyToManyField)
                    ):
                        inherited_attrs[k] = v

        all_attrs = {**inherited_attrs, **attrs}

        for key, value in all_attrs.items():
            if isinstance(value, ManyToManyField):
                junction_name = value.get_junction_table_name(name)
                source_col = f"{_to_snake_case(name)}_id"
                target_name = (
                    value.to_model
                    if isinstance(value.to_model, str)
                    else value.to_model.__name__
                )
                target_col = f"{_to_snake_case(target_name)}_id"
                many_to_many_keys[key] = ManyToManyReference(
                    junction_table=junction_name,
                    source_column=source_col,
                    target_column=target_col,
                    target_model=value.to_model,
                    related_name=key,
                )
                dynamic_fields.add(f"_{key}_m2m")
                pending_junction_tables.append(
                    {
                        "junction_table": junction_name,
                        "source_column": source_col,
                        "target_column": target_col,
                        "source_table": attrs.get("_table_name")
                        or _to_snake_case(name),
                        "target_table": _to_snake_case(target_name)
                        if isinstance(value.to_model, str)
                        else _to_snake_case(value.to_model.__name__),
                    }
                )

            elif isinstance(value, Field):
                fields[key] = value
                if getattr(value, "unique", False):
                    unique_fields.add(key)
                if getattr(value, "primary_key", False):
                    primary_keys.append(key)
                if isinstance(value, ForeignKey):
                    foreign_keys[key] = ForeignKeyReference(
                        column_name=key,
                        to_model=value.to_model,
                        to_column=value.to_column,
                        related_name=value.related_name,
                        on_delete=value.on_delete,
                        on_update=value.on_update,
                        to_db=getattr(value, "to_db", None),
                        to_schema=getattr(value, "to_schema", None),
                    )
                    dynamic_fields.add(f"_{key}_related")

            elif isinstance(value, InverseForeignKeyReference):
                inverse_foreign_keys[key] = value
                dynamic_fields.add(f"_{key}_relation")

        if "_primary_keys" in attrs and attrs["_primary_keys"]:
            if primary_keys:
                error_message = (
                    f"Model {name} cannot have both fields with primary_key=True "
                    "and _primary_keys defined"
                )
                formated_error(error_message, class_name="Model", method_name="__new__")
                raise ValueError(error_message)

            primary_keys = attrs["_primary_keys"]

            for pk in primary_keys:
                if pk not in fields:
                    error_message = (
                        f"Primary key field '{pk}' not found in model {name}"
                    )
                    formated_error(
                        error_message, class_name="Model", method_name="__new__"
                    )
                    raise ValueError(error_message)

        if not primary_keys:
            error_message = f"Model {name} must define at least one primary key field"
            formated_error(error_message, class_name="Model", method_name="__new__")
            raise ValueError(error_message)

        if "_inverse_foreign_keys" in attrs:
            for key, value in attrs["_inverse_foreign_keys"].items():
                if "referenced_field" not in value:
                    error_message = (
                        f"Inverse foreign key '{key}' must specify 'referenced_field'"
                    )
                    formated_error(
                        error_message, class_name="Model", method_name="__new__"
                    )
                    raise ValueError(error_message)
                inverse_foreign_keys[key] = InverseForeignKeyReference(**value)
                dynamic_field_name = f"_{key}_relation"
                dynamic_fields.add(dynamic_field_name)

        if "_many_to_many" in attrs:
            for key, value in attrs["_many_to_many"].items():
                many_to_many_keys[key] = ManyToManyReference(**value)
                dynamic_fields.add(f"_{key}_m2m")

        table_name = attrs.get("_table_name")
        if not table_name:
            table_name = _to_snake_case(name)

        options = ModelOptions(
            table_name=table_name,
            database=attrs.get("_database"),
            fields=fields,
            primary_keys=primary_keys,
            unique_fields=unique_fields,
            foreign_keys=foreign_keys,
            inverse_foreign_keys=inverse_foreign_keys,
            indexes=attrs.get("_indexes", []),
            unique_together=attrs.get("_unique_together", []),
            constraints=attrs.get("_constraints", []),
            db_schema=attrs.get("_db_schema"),
            unfetchable=attrs.get("_unfetchable", False),
            many_to_many_keys=many_to_many_keys,
        )

        attrs["_meta"] = options
        attrs["_fields"] = fields
        attrs["_dynamic_fields"] = dynamic_fields
        attrs["_pending_junction_tables"] = pending_junction_tables

        def __init__(self: Any, **kwargs: Any) -> None:
            super(Model, self).__init__()
            for field_name, field in self._fields.items():
                value = kwargs.get(field_name, field.get_default())
                if hasattr(field, "to_python"):
                    value = field.to_python(value)
                setattr(self, field_name, value)
            self._extra_data = {
                k: v for k, v in kwargs.items() if k not in self._fields
            }

            self._dynamic_data: dict[str, Any] = {}
            for field in self._dynamic_fields:
                if field.endswith("_related"):
                    self._dynamic_data[field] = {}
                elif field.endswith("_relation"):
                    self._dynamic_data[field] = []
                elif field.endswith("_m2m"):
                    self._dynamic_data[field] = []

        def get_related(self: Any, field_name: str) -> Any:
            regular_field = f"_{field_name}_related"
            if regular_field in self._dynamic_fields:
                return self._dynamic_data[regular_field]

            relation_field = f"_{field_name}_relation"
            if relation_field in self._dynamic_fields:
                return self._dynamic_data[relation_field]

            m2m_field = f"_{field_name}_m2m"
            if m2m_field in self._dynamic_fields:
                return self._dynamic_data[m2m_field]

            error_message = f"No related field for {field_name}"
            formated_error(error_message, class_name="Model", method_name="__init__")
            raise AttributeError(error_message)

        def set_related(
            self: Any,
            field_name: str,
            value: Any,
            is_inverse: bool = False,
            is_m2m: bool = False,
        ) -> None:
            if is_m2m:
                field = f"_{field_name}_m2m"
            elif is_inverse:
                field = f"_{field_name}_relation"
            else:
                field = f"_{field_name}_related"

            if field not in self._dynamic_fields:
                error_message = f"No related field for {field_name}"
                formated_error(
                    error_message, class_name="Model", method_name="__init__"
                )
                raise AttributeError(error_message)
            self._dynamic_data[field] = value

        attrs["__init__"] = __init__
        attrs["get_related"] = get_related
        attrs["set_related"] = set_related

        cls = super().__new__(mcs, name, bases, attrs)
        if name != "Model":
            StateManager.register_model(cls)

        return cls


class Model(RuntimeMixin, metaclass=ModelMeta):
    DoesNotExist: ClassVar[type[DoesNotExist]] = DoesNotExist
    MultipleObjectsReturned: ClassVar[type[MultipleObjectsReturned]] = (
        MultipleObjectsReturned
    )
    ValidationError: ClassVar[type[ValidationError]] = ValidationError

    _meta: ClassVar[ModelOptions]
    _fields: ClassVar[dict[str, Field]]
    _dynamic_fields: ClassVar[set[str]]
    _cache_policy: ClassVar[CachePolicy] = CachePolicy.SHORT_TERM
    _cache_timeout: ClassVar[int | None] = None
    _realtime_updates: ClassVar[bool] = False
    _table_name: ClassVar[str | None] = None
    _database: ClassVar[str | None] = None
    _db_schema: ClassVar[str | None] = None
    _unfetchable: ClassVar[bool] = False
    _indexes: ClassVar[list[Any] | None] = None
    _unique_together: ClassVar[list[Any] | None] = None
    _constraints: ClassVar[list[Any] | None] = None
    _inverse_foreign_keys: ClassVar[dict[str, Any]] = {}
    _many_to_many: ClassVar[dict[str, Any]] = {}
    _pending_junction_tables: ClassVar[list[dict[str, Any]]] = []

    _extra_data: dict[str, Any]
    _dynamic_data: dict[str, Any]

    # Pyright cannot see fields set by the metaclass at class-creation time.
    # Annotating `id` here covers the near-universal primary key pattern used
    # by generated DTOs and managers.  All other fields remain dynamically typed.
    id: Any

    def __init__(self, **kwargs: Any) -> None:
        for field_name, field in self._fields.items():
            value = kwargs.get(field_name, field.get_default())
            setattr(self, field_name, value)
        self._extra_data = {k: v for k, v in kwargs.items() if k not in self._fields}

    @classmethod
    def get_database_name(cls) -> str:
        if not cls._database:
            raise ValueError(f"Database name not set for model {cls.__name__}")
        return cls._database

    @classmethod
    async def create(cls, **kwargs: Any) -> Model:
        instance = await create.create_instance(cls, **kwargs)
        await StateManager.cache(cls, instance)
        return instance

    @classmethod
    async def bulk_create(cls, objects_data: list[dict[str, Any]]) -> list[Model]:
        """
        Bulk create multiple instances using enhanced bulk operations.
        Follows the same data processing pipeline as individual create().
        """
        from matrx_orm.operations.create import bulk_create

        return await bulk_create(cls, objects_data)

    @classmethod
    async def bulk_update(cls, objects: list[Model], fields: list[str]) -> int:
        """
        Bulk update multiple instances with validation like individual operations.
        """
        from matrx_orm.operations.update import bulk_update

        return await bulk_update(cls, objects, fields)

    @classmethod
    async def bulk_delete(cls, objects: list[Model]) -> int:
        """
        Bulk delete multiple instances.
        """
        from matrx_orm.operations.delete import bulk_delete

        return await bulk_delete(cls, objects)

    @classmethod
    async def upsert(
        cls,
        data: dict[str, Any],
        conflict_fields: list[str],
        update_fields: list[str] | None = None,
    ) -> Model:
        """INSERT ... ON CONFLICT (conflict_fields) DO UPDATE SET ... RETURNING *

        Args:
            data: Field values for the row.
            conflict_fields: Column names that form the unique/exclusion constraint
                             (e.g. ["email"] or ["tenant_id", "slug"]).
            update_fields: Columns to update on conflict. Defaults to every column
                           not in conflict_fields.
        """
        from matrx_orm.operations.create import upsert

        return await upsert(cls, data, conflict_fields, update_fields)

    @classmethod
    async def bulk_upsert(
        cls,
        objects_data: list[dict[str, Any]],
        conflict_fields: list[str],
        update_fields: list[str] | None = None,
    ) -> list[Model]:
        """Bulk INSERT ... ON CONFLICT DO UPDATE for multiple rows.

        Args:
            objects_data: List of dicts, one per row.
            conflict_fields: Column names that form the unique/exclusion constraint.
            update_fields: Columns to update on conflict. Defaults to every column
                           not in conflict_fields.
        """
        from matrx_orm.operations.create import bulk_upsert

        return await bulk_upsert(cls, objects_data, conflict_fields, update_fields)

    @classmethod
    async def count(cls, **kwargs: Any) -> int:
        """Lightweight row count without full model hydration.

        Usage:
            total = await MyModel.count()
            active = await MyModel.count(status="active")
        """
        return await QueryBuilder(cls).filter(**kwargs).count()

    @classmethod
    def count_sync(cls, **kwargs: Any) -> int:
        """Synchronous wrapper for count()."""
        try:
            asyncio.get_running_loop()
            raise RuntimeError(
                "Model.count_sync() called in an async context. Use await Model.count() instead."
            )
        except RuntimeError as e:
            if "no running event loop" not in str(e):
                raise
        return run_sync(cls.count(**kwargs))

    @classmethod
    async def exists(cls, **kwargs: Any) -> bool:
        """Check whether at least one row matching the filters exists.

        Usage:
            if await MyModel.exists(email="a@b.com"):
                ...
        """
        return await QueryBuilder(cls).filter(**kwargs).exists()

    @classmethod
    def exists_sync(cls, **kwargs: Any) -> bool:
        """Synchronous wrapper for exists()."""
        try:
            asyncio.get_running_loop()
            raise RuntimeError(
                "Model.exists_sync() called in an async context. Use await Model.exists() instead."
            )
        except RuntimeError as e:
            if "no running event loop" not in str(e):
                raise
        return run_sync(cls.exists(**kwargs))

    @classmethod
    async def update_where(
        cls, filters: dict[str, Any], **updates: Any
    ) -> dict[str, Any]:
        """Bulk-update rows matching filters without fetching them first.

        Args:
            filters: Lookup kwargs (same syntax as filter()).
            **updates: Field=value pairs to SET.

        Returns:
            {"rows_affected": int, "updated_rows": list[dict]}

        Usage:
            result = await MyModel.update_where(
                {"status": "draft", "created_at__lt": cutoff},
                status="archived",
            )
        """
        return await QueryBuilder(cls).filter(**filters).update(**updates)

    @classmethod
    async def delete_where(cls, **filters: Any) -> int:
        """Delete rows matching filters without fetching them first.

        Args:
            **filters: Lookup kwargs (same syntax as filter()).

        Returns:
            Number of rows deleted.

        Usage:
            deleted = await MyModel.delete_where(status="expired")
        """
        return await QueryBuilder(cls).filter(**filters).delete()

    @classmethod
    async def get(cls, use_cache: bool = True, **kwargs: Any) -> Model:
        try:
            if use_cache:
                return await StateManager.get(cls, **kwargs)
            else:
                return await QueryBuilder(cls).filter(**kwargs).get()
        except ORMException as e:
            e.enrich(model=cls, operation="get", args=kwargs)
            raise

    @classmethod
    def get_sync(cls, use_cache: bool = True, **kwargs: Any) -> Model:
        """
        Synchronous wrapper for get(). Runs the async get() method in the current event loop.
        Use this in synchronous contexts to avoid RuntimeWarning for unawaited coroutines.
        """
        try:
            asyncio.get_running_loop()
            raise RuntimeError(
                "Model.get_sync() called in an async context. Use await Model.get() instead."
            )
        except RuntimeError as e:
            if "no running event loop" not in str(e):
                raise

        return run_sync(cls.get(use_cache=use_cache, **kwargs))

    @classmethod
    async def get_or_none(cls, use_cache: bool = True, **kwargs: Any) -> Model | None:
        try:
            if use_cache:
                return await StateManager.get_or_none(cls, **kwargs)
            else:
                return await QueryBuilder(cls).filter(**kwargs).get_or_none()
        except DoesNotExist:
            return None
        except Exception as e:
            vcprint(f"Error in get_or_none for {cls.__name__}: {str(e)}", color="red")
            return None

    @classmethod
    def get_or_none_sync(cls, use_cache: bool = True, **kwargs: Any) -> Model | None:
        """
        Synchronous wrapper for get_or_none().
        Use this in synchronous contexts to avoid RuntimeWarning for unawaited coroutines.
        """
        try:
            asyncio.get_running_loop()
            raise RuntimeError(
                "Model.get_or_none_sync() called in an async context. Use await Model.get_or_none() instead."
            )
        except RuntimeError as e:
            if "no running event loop" not in str(e):
                raise

        return run_sync(cls.get_or_none(use_cache=use_cache, **kwargs))

    @classmethod
    def filter(cls, *args: Any, **kwargs: Any) -> QueryBuilder:
        """Return a QueryBuilder with the given filters applied.

        Accepts Q objects as positional args and/or keyword filters::

            User.filter(Q(status="active") | Q(role="admin"))
            User.filter(status="active", role="admin")
            User.filter(Q(is_active=True), tenant_id=tid)
        """
        return QueryBuilder(cls).filter(*args, **kwargs)

    @classmethod
    async def raw(cls, sql: str, *params: Any) -> list[Model]:
        """Execute raw SQL and hydrate results as model instances.

        Usage::

            users = await User.raw("SELECT * FROM users WHERE age > $1", 18)
        """
        from matrx_orm.core.async_db_manager import AsyncDatabaseManager

        results = await AsyncDatabaseManager.execute_query(cls._database, sql, *params)
        instances = []
        for row in results:
            try:
                instances.append(cls(**dict(row)))
            except Exception:
                instances.append(
                    cls(**{k: v for k, v in dict(row).items() if k in cls._fields})
                )
        return instances

    @classmethod
    async def raw_sql(cls, sql: str, *params: Any) -> list[dict[str, Any]]:
        """Execute raw SQL and return results as plain dicts (no hydration).

        Usage::

            rows = await User.raw_sql("SELECT count(*) as cnt, role FROM users GROUP BY role")
        """
        from matrx_orm.core.async_db_manager import AsyncDatabaseManager

        results = await AsyncDatabaseManager.execute_query(cls._database, sql, *params)
        return [dict(row) for row in results]

    @classmethod
    def filter_sync(cls, **kwargs: Any) -> list[Model]:
        """
        Synchronous wrapper for filter().all().
        Use this in synchronous contexts to fetch filtered results without async/await.
        """
        try:
            asyncio.get_running_loop()
            raise RuntimeError(
                "Model.filter_sync() called in an async context. Use await Model.filter().all() instead."
            )
        except RuntimeError as e:
            if "no running event loop" not in str(e):
                raise

        return run_sync(cls.filter(**kwargs).all())

    @classmethod
    async def all(cls) -> list[Model]:
        try:
            results = await QueryBuilder(cls).all()
            await StateManager.cache_bulk(cls, results)
            return results
        except ORMException as e:
            e.enrich(model=cls, operation="all")
            raise

    @classmethod
    def all_sync(cls) -> list[Model]:
        """
        Synchronous wrapper for all().
        Use this in synchronous contexts to fetch all results without async/await.
        """
        try:
            asyncio.get_running_loop()
            raise RuntimeError(
                "Model.all_sync() called in an async context. Use await Model.all() instead."
            )
        except RuntimeError as e:
            if "no running event loop" not in str(e):
                raise

        return run_sync(cls.all())

    async def save(self, **kwargs: Any) -> Model:
        """Save the current state of the model instance."""
        if kwargs:
            error_message = f"Error for {self.__class__.__name__}: For updating fields, use update() instead of save()"
            formated_error(
                error_message, class_name="Model", method_name="save", context=kwargs
            )
            raise TypeError(error_message)

        try:
            is_update = hasattr(self, "id") and self.id is not None
            if is_update:
                await update.update_instance(self)
            else:
                await create.create_instance(self.__class__, **self.__dict__)
            await StateManager.cache(self.__class__, self)
            return self
        except ORMException as e:
            e.enrich(model=self.__class__, operation="save")
            raise

    async def update(self, **kwargs: Any) -> Model:
        """
        Update specific fields and save in one operation.
        Returns the updated instance.
        """
        invalid_fields = [k for k in kwargs if k not in self._fields]
        if invalid_fields:
            vcprint(self._fields, "Model Fields", color="yellow")
            error_message = (
                f"Invalid fields for {self.__class__.__name__}: {invalid_fields}"
            )
            formated_error(
                error_message, class_name="Model", method_name="update", context=kwargs
            )
            raise ValueError(error_message)

        try:
            for field, value in kwargs.items():
                setattr(self, field, value)

            await update.update_instance(self, fields=kwargs.keys())
            return self
        except ORMException as e:
            e.enrich(model=self.__class__, operation="update", args=kwargs)
            raise

    @classmethod
    async def update_fields(
        cls, instance_or_id: Model | Any, **kwargs: Any
    ) -> Model | None:
        """
        Static method to update an instance or create it if it doesn't exist.
        Merges the provided fields with existing values.
        """
        try:
            if isinstance(instance_or_id, cls):
                instance = instance_or_id
            else:
                instance = await cls.filter(id=instance_or_id).first()
                if instance is None:
                    raise DoesNotExist(
                        model=cls,
                        filters={"id": instance_or_id},
                        class_name="Model",
                        method_name="update_fields",
                    )

            invalid_fields = [k for k in kwargs if k not in cls._fields]
            if invalid_fields:
                raise ValidationError(
                    model=cls,
                    field="multiple",
                    value=invalid_fields,
                    reason="Invalid fields provided",
                    class_name="Model",
                    method_name="update_fields",
                )

            for field, value in kwargs.items():
                setattr(instance, field, value)

            await instance.save()
            return instance

        except DoesNotExist as e:
            print(str(e))
            return None
        except ValidationError as e:
            raise e

    async def delete(self) -> None:
        try:
            await delete.delete_instance(self)
            await StateManager.remove(self.__class__, self)
        except ORMException as e:
            pk = (
                getattr(self, self._meta.primary_keys[0], None)
                if self._meta.primary_keys
                else None
            )
            e.enrich(model=self.__class__, operation="delete", args={"id": pk})
            raise

    def get_cache_key(self) -> str:
        return "_".join(str(getattr(self, pk)) for pk in self._meta.primary_keys)

    @property
    def table_name(
        self,
    ) -> Any:  # Any allows subclass fields named table_name to satisfy pyright
        return self._meta.table_name

    @classmethod
    def get_field(cls, field_name: str) -> Field | None:
        return cls._fields.get(field_name)

    @classmethod
    def get_relation(
        cls, field_name: str
    ) -> ForeignKeyReference | InverseForeignKeyReference:
        field = cls.get_field(field_name)
        if isinstance(field, (ForeignKeyReference, InverseForeignKeyReference)):
            return field
        error_message = f"{field_name} is not a relation field"
        formated_error(error_message, class_name="Model", method_name="get_relation")
        raise ValueError(error_message)

    def _serialize_value(self, value: Any) -> Any:
        """Convert value to a serializable form for to_dict()."""
        from enum import Enum
        from uuid import UUID

        if value is None:
            return None

        if isinstance(value, Enum):
            return value.value

        if isinstance(value, (str, int, float, bool)):
            return value

        if isinstance(value, UUID):
            return str(value)

        if isinstance(value, (list, tuple)):
            return [self._serialize_value(item) for item in value]

        if isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}

        if hasattr(value, "to_dict") and callable(value.to_dict):
            return value.to_dict()

        return str(value)

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        for field_name, field in self._fields.items():
            value = getattr(self, field_name, None)
            if value is not None:
                data[field_name] = self._serialize_value(value)

        if hasattr(self, "runtime"):
            data["runtime"] = self.runtime.to_dict()
        if hasattr(self, "dto"):
            data["dto"] = self.dto.to_dict()
        return data

    def to_flat_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        for field_name, field in self._fields.items():
            value = getattr(self, field_name, None)
            if value is not None:
                data[field_name] = field.to_python(value)

        runtime_data = self.runtime.to_dict() if hasattr(self, "runtime") else {}

        dto_data = self.dto.to_dict() if hasattr(self, "dto") else {}

        return {**data, **runtime_data, **dto_data}

    @classmethod
    def from_db_result(cls, data: dict[str, Any]) -> Model:
        instance = cls()
        for field_name, value in data.items():
            if field_name in cls._fields:
                field = cls._fields[field_name]
                setattr(instance, field_name, field.from_db_value(value))
            else:
                instance._extra_data[field_name] = value
        return instance

    async def fetch_fk(self, field_name: str) -> Model | None:
        """Fetch a single foreign key relationship"""
        if field_name not in self._meta.foreign_keys:
            error_message = f"No foreign key found for field {field_name}"
            formated_error(error_message, class_name="Model", method_name="fetch_fk")
            raise ValueError(error_message)

        fk_ref = self._meta.foreign_keys[field_name]

        related_model = fk_ref.related_model
        if related_model and getattr(related_model._meta, "unfetchable", False):
            import warnings

            warnings.warn(
                f"fetch_fk('{field_name}') skipped: {related_model.__name__} is marked "
                "_unfetchable = True and cannot be queried. "
                "For cross-schema tables on the same database (e.g. auth.users), remove "
                "_unfetchable and ensure _db_schema is set on the model. "
                "For cross-database FKs, add to_db='<project_name>' to the ForeignKey field.",
                UserWarning,
                stacklevel=2,
            )
            return None

        value = getattr(self, field_name)
        if value is not None:
            return await fk_ref.fetch_data(self, value)
        return None

    async def fetch_ifk(self, field_name: str) -> list[Model]:
        """Fetch a single inverse foreign key relationship"""
        if field_name not in self._meta.inverse_foreign_keys:
            error_message = f"No inverse foreign key found for field {field_name}"
            formated_error(error_message, class_name="Model", method_name="fetch_ifk")
            raise ValueError(error_message)

        ifk_ref = self._meta.inverse_foreign_keys[field_name]
        referenced_value = getattr(self, ifk_ref.referenced_field)
        if referenced_value is not None:
            return await ifk_ref.fetch_data(self)
        return []

    async def fetch_one_relation(self, field_name: str) -> Model | list[Model] | None:
        if field_name in self._meta.foreign_keys:
            return await self.fetch_fk(field_name)

        if field_name in self._meta.inverse_foreign_keys:
            return await self.fetch_ifk(field_name)

        if field_name in self._meta.many_to_many_keys:
            return await self.fetch_m2m(field_name)

        all_relations = (
            set(self._meta.foreign_keys)
            | set(self._meta.inverse_foreign_keys)
            | set(self._meta.many_to_many_keys)
        )
        error_message = f"'{field_name}' is not a valid relationship field. Field must be one of: {', '.join(all_relations)}"
        formated_error(
            error_message, class_name="Model", method_name="fetch_one_relation"
        )
        raise ValueError(error_message)

    async def fetch_fks(self) -> dict[str, Model | None]:
        """Fetch all foreign key relationships concurrently, skipping any that fail."""
        fk_names = list(self._meta.foreign_keys.keys())
        if not fk_names:
            return {}

        async def _safe_fetch_fk(field_name: str) -> tuple[str, Model | None]:
            try:
                return field_name, await self.fetch_fk(field_name)
            except Exception as e:
                related = self._meta.foreign_keys[field_name].to_model
                related_name = (
                    related
                    if isinstance(related, str)
                    else getattr(related, "__name__", str(related))
                )
                vcprint(
                    f"[{self.__class__.__name__}] Failed to fetch FK '{field_name}' -> {related_name}: "
                    f"{e.__class__.__name__}: {e.message if hasattr(e, 'message') else e}",
                    color="yellow",
                )
                return field_name, None

        pairs = await asyncio.gather(*(_safe_fetch_fk(name) for name in fk_names))
        return dict(pairs)

    async def fetch_ifks(self) -> dict[str, list[Model] | None]:
        """Fetch all inverse foreign key relationships concurrently, skipping any that fail."""
        ifk_names = list(self._meta.inverse_foreign_keys.keys())
        if not ifk_names:
            return {}

        async def _safe_fetch_ifk(field_name: str) -> tuple[str, list[Model] | None]:
            try:
                return field_name, await self.fetch_ifk(field_name)
            except Exception as e:
                ifk_ref = self._meta.inverse_foreign_keys[field_name]
                related_name = (
                    ifk_ref.from_model
                    if isinstance(ifk_ref.from_model, str)
                    else getattr(ifk_ref.from_model, "__name__", str(ifk_ref.from_model))
                )
                vcprint(
                    f"[{self.__class__.__name__}] Failed to fetch IFK '{field_name}' -> {related_name}: "
                    f"{e.__class__.__name__}: {e.message if hasattr(e, 'message') else e}",
                    color="yellow",
                )
                return field_name, None

        pairs = await asyncio.gather(*(_safe_fetch_ifk(name) for name in ifk_names))
        return dict(pairs)

    async def fetch_m2m(self, relation_name: str) -> list[Model]:
        """Fetch a single many-to-many relationship by name."""
        if relation_name not in self._meta.many_to_many_keys:
            error_message = (
                f"No M2M relationship '{relation_name}' on {self.__class__.__name__}"
            )
            formated_error(error_message, class_name="Model", method_name="fetch_m2m")
            raise ValueError(error_message)
        ref = self._meta.many_to_many_keys[relation_name]
        results = await ref.fetch_related(self)
        self._dynamic_data[f"_{relation_name}_m2m"] = results
        return results

    async def fetch_m2ms(self) -> dict[str, list[Model]]:
        """Fetch all M2M relationships concurrently, skipping any that fail."""
        m2m_names = list(self._meta.many_to_many_keys.keys())
        if not m2m_names:
            return {}

        async def _safe_fetch_m2m(relation_name: str) -> tuple[str, list[Model]]:
            try:
                return relation_name, await self.fetch_m2m(relation_name)
            except Exception as e:
                ref = self._meta.many_to_many_keys[relation_name]
                target = (
                    ref.target_model
                    if isinstance(ref.target_model, str)
                    else getattr(ref.target_model, "__name__", str(ref.target_model))
                )
                vcprint(
                    f"[{self.__class__.__name__}] Failed to fetch M2M '{relation_name}' -> {target}: "
                    f"{e.__class__.__name__}: {e.message if hasattr(e, 'message') else e}",
                    color="yellow",
                )
                return relation_name, []

        pairs = await asyncio.gather(*(_safe_fetch_m2m(name) for name in m2m_names))
        return dict(pairs)

    async def add_m2m(self, relation_name: str, *target_ids: Any) -> int:
        """Add targets to a many-to-many relationship."""
        if relation_name not in self._meta.many_to_many_keys:
            raise ValueError(
                f"No M2M relationship '{relation_name}' on {self.__class__.__name__}"
            )
        ref = self._meta.many_to_many_keys[relation_name]
        return await ref.add(self, *target_ids)

    async def remove_m2m(self, relation_name: str, *target_ids: Any) -> int:
        """Remove targets from a many-to-many relationship."""
        if relation_name not in self._meta.many_to_many_keys:
            raise ValueError(
                f"No M2M relationship '{relation_name}' on {self.__class__.__name__}"
            )
        ref = self._meta.many_to_many_keys[relation_name]
        return await ref.remove(self, *target_ids)

    async def set_m2m(self, relation_name: str, target_ids: list[Any]) -> None:
        """Replace all targets in a many-to-many relationship."""
        if relation_name not in self._meta.many_to_many_keys:
            raise ValueError(
                f"No M2M relationship '{relation_name}' on {self.__class__.__name__}"
            )
        ref = self._meta.many_to_many_keys[relation_name]
        await ref.set(self, target_ids)

    async def clear_m2m(self, relation_name: str) -> int:
        """Remove all targets from a many-to-many relationship."""
        if relation_name not in self._meta.many_to_many_keys:
            raise ValueError(
                f"No M2M relationship '{relation_name}' on {self.__class__.__name__}"
            )
        ref = self._meta.many_to_many_keys[relation_name]
        return await ref.clear(self)

    async def fetch_all_related(self) -> dict[str, dict[str, Any]]:
        """Fetch all related data (FKs, inverse FKs, and M2M) concurrently."""
        fk_results, ifk_results, m2m_results = await asyncio.gather(
            self.fetch_fks(),
            self.fetch_ifks(),
            self.fetch_m2ms(),
        )
        return {
            "foreign_keys": fk_results,
            "inverse_foreign_keys": ifk_results,
            "many_to_many": m2m_results,
        }

    async def filter_fk(self, field_name: str, **kwargs: Any) -> list[Model]:
        if field_name not in self._meta.foreign_keys:
            error_message = f"No foreign key found for field {field_name}"
            formated_error(error_message, class_name="Model", method_name="filter_fk")
            raise ValueError(error_message)
        fk_ref = self._meta.foreign_keys[field_name]
        value = getattr(self, field_name)
        if value is not None:
            return await fk_ref.related_model.filter(
                **{fk_ref.to_column: value}, **kwargs
            ).all()
        return []

    async def filter_ifk(self, field_name: str, **kwargs: Any) -> list[Model]:
        """Filter inverse foreign key relationships with additional criteria"""
        if field_name not in self._meta.inverse_foreign_keys:
            error_message = f"No inverse foreign key found for field {field_name}"
            formated_error(error_message, class_name="Model", method_name="filter_ifk")
            raise ValueError(error_message)

        ifk_ref = self._meta.inverse_foreign_keys[field_name]
        referenced_value = getattr(self, ifk_ref.referenced_field)
        vcprint(referenced_value, pretty=True, color="yellow")
        if referenced_value is not None:
            return await ifk_ref.related_model.filter(
                **{ifk_ref.from_field: referenced_value}, **kwargs
            ).all()
        return []

    async def filter_one_relation(self, field_name: str, **kwargs: Any) -> list[Model]:
        """
        Filter a relationship by field name with additional criteria,
        automatically determining whether it's a FK, IFK, or M2M relationship
        """
        if field_name in self._meta.foreign_keys:
            return await self.filter_fk(field_name, **kwargs)

        if field_name in self._meta.inverse_foreign_keys:
            return await self.filter_ifk(field_name, **kwargs)

        if field_name in self._meta.many_to_many_keys:
            return await self.fetch_m2m(field_name)

        all_relations = (
            set(self._meta.foreign_keys)
            | set(self._meta.inverse_foreign_keys)
            | set(self._meta.many_to_many_keys)
        )
        error_message = f"'{field_name}' is not a valid relationship field. Field must be one of: {', '.join(all_relations)}"
        formated_error(
            error_message, class_name="Model", method_name="filter_one_relation"
        )
        raise ValueError(error_message)

    def get_related(self, field_name: str) -> Any:
        regular_field = f"_{field_name}_related"
        if regular_field in self._dynamic_fields:
            return self._dynamic_data[regular_field]

        inverse_field = f"_{field_name}_relation"
        if inverse_field in self._dynamic_fields:
            return self._dynamic_data[inverse_field]

        m2m_field = f"_{field_name}_m2m"
        if m2m_field in self._dynamic_fields:
            return self._dynamic_data[m2m_field]

        error_message = f"No related field for {field_name}"
        formated_error(error_message, class_name="Model", method_name="get_related")
        raise AttributeError(error_message)

    def has_related(self, field_name: str) -> bool:
        """Check if related data is already loaded"""
        try:
            data = self.get_related(field_name)
            if isinstance(data, dict):
                return bool(data)
            return bool(data)
        except AttributeError:
            return False

    @classmethod
    async def get_by_id(cls, id_value: Any, use_cache: bool = True) -> Model:
        pk_field = cls._meta.primary_keys[0]
        return await cls.get(use_cache=use_cache, **{pk_field: id_value})

    @classmethod
    async def ensure_m2m_tables(cls) -> None:
        """Create any pending junction tables that don't yet exist in the database."""
        if not cls._pending_junction_tables:
            return

        from matrx_orm.core.async_db_manager import AsyncDatabaseManager

        db_name = cls._meta.database
        for jt in cls._pending_junction_tables:
            sql = (
                f"CREATE TABLE IF NOT EXISTS {jt['junction_table']} ("
                f"{jt['source_column']} UUID NOT NULL REFERENCES {jt['source_table']}(id) ON DELETE CASCADE, "
                f"{jt['target_column']} UUID NOT NULL REFERENCES {jt['target_table']}(id) ON DELETE CASCADE, "
                f"PRIMARY KEY ({jt['source_column']}, {jt['target_column']})"
                f")"
            )
            await AsyncDatabaseManager.execute_query(db_name, sql)

    @classmethod
    async def get_many(cls, **kwargs: Any) -> list[Model]:
        return await QueryBuilder(cls).filter(**kwargs).all()
