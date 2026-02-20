from __future__ import annotations

import asyncio
import time
from enum import Enum
from typing import Any, Generic, TypeVar
from uuid import UUID

from matrx_utils import vcprint

from matrx_orm.core.base import Model, RuntimeContainer
from matrx_orm.extended.app_error_handler import AppError, handle_errors

ModelT = TypeVar("ModelT", bound=Model)

info = True
debug = False
verbose = False


class BaseDTO:
    id: str
    _model: Model | None = None

    @classmethod
    @handle_errors
    async def from_model(cls, model: Model) -> BaseDTO:
        instance = cls(id=str(model.id))
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


class BaseManager(Generic[ModelT]):
    model: type[ModelT]
    dto_class: type[BaseDTO] | None
    fetch_on_init_limit: int
    _FETCH_ON_INIT_WITH_WARNINGS_OFF: str | None
    _active_items: set[Any]
    computed_fields: set[str]
    relation_fields: set[str]

    def __init__(
        self,
        model: type[ModelT],
        dto_class: type[BaseDTO] | None = None,
        fetch_on_init_limit: int = 0,
        FETCH_ON_INIT_WITH_WARNINGS_OFF: str | None = None,
    ) -> None:
        self.model = model
        self.dto_class = dto_class
        self.fetch_on_init_limit = fetch_on_init_limit
        self._FETCH_ON_INIT_WITH_WARNINGS_OFF = FETCH_ON_INIT_WITH_WARNINGS_OFF
        self._active_items: set[Any] = set()
        self.computed_fields: set[str] = set()
        self.relation_fields: set[str] = set()
        self._initialize_manager()

    def _initialize_manager(self) -> None:
        """Initialize the manager and trigger auto-fetch if configured.

        Auto-fetch now works correctly in all contexts thanks to automatic
        event loop detection and pool recreation in AsyncDatabaseManager.
        """
        if self.fetch_on_init_limit > 0:
            try:
                asyncio.get_running_loop()
                asyncio.create_task(self._auto_fetch_on_init_async())
                vcprint(
                    f"[{self.model.__name__}] Auto-fetching on init (async)",
                    verbose=info,
                    color="yellow",
                )
            except RuntimeError:
                vcprint(
                    f"[{self.model.__name__}] Auto-fetching on init (sync)",
                    verbose=info,
                    color="yellow",
                )
                self._auto_fetch_on_init_sync()

    def _get_error_context(self) -> dict[str, str]:
        return {
            "manager": self.__class__.__name__,
            "model": self.model.__name__ if self.model else "Unknown",
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

    async def _initialize_dto_runtime(self, dto: BaseDTO, item: ModelT) -> None:
        """Hook for subclasses to add runtime data to DTO"""
        pass

    async def _initialize_item_runtime(self, item: ModelT | None) -> ModelT | None:
        if not item:
            return None
        if not hasattr(item, "runtime"):
            item.runtime = RuntimeContainer()
        if self.dto_class:
            dto = await self.dto_class.from_model(item)
            await self._initialize_dto_runtime(dto, item)
            item.runtime.dto = dto
            item.dto = dto
        return item

    async def initialize(self) -> BaseManager[ModelT]:
        """Explicitly initialize the manager with auto-fetch in async contexts.

        This should be called after manager creation if you want to trigger auto-fetch
        in an async context.

        Example:
            manager = MyManager()
            await manager.initialize()
        """
        if self.fetch_on_init_limit > 0:
            await self._auto_fetch_on_init_async()
        return self

    def initialize_sync(self) -> BaseManager[ModelT]:
        """Explicitly initialize the manager with auto-fetch in sync contexts.

        This should be called after manager creation if you want to trigger auto-fetch
        in a synchronous context.

        Example:
            manager = MyManager()
            manager.initialize_sync()
        """
        if self.fetch_on_init_limit > 0:
            self._auto_fetch_on_init_sync()
        return self

    def add_computed_field(self, field: str) -> None:
        self.computed_fields.add(field)

    def add_relation_field(self, field: str) -> None:
        self.relation_fields.add(field)

    @handle_errors
    async def _process_item(self, item: ModelT | None) -> ModelT | None:
        if item:
            await self._initialize_item_runtime(item)
            self._add_to_active(item.id)
        return item

    @handle_errors
    async def _get_item_or_raise(self, use_cache: bool = True, **kwargs: Any) -> ModelT:
        """Fetch a single item from the model and raise"""
        item = await self.model.get(use_cache=use_cache, **kwargs)
        if not item:
            raise AppError(
                message="Item not found",
                error_type="NotFoundError",
                client_visible="The requested item could not be found.",
            )
        return await self._initialize_item_runtime(item)  # type: ignore[return-value]

    @handle_errors
    async def _get_item_or_none(
        self, use_cache: bool = True, **kwargs: Any
    ) -> ModelT | None:
        """Fetch a single item from the model."""
        item = await self.model.get_or_none(use_cache=use_cache, **kwargs)
        if not item:
            return None
        return await self._initialize_item_runtime(item)

    @handle_errors
    async def _get_item_with_retry(
        self, use_cache: bool = True, **kwargs: Any
    ) -> ModelT:
        """Fetch a single item from the model with retry."""
        item = await self.model.get_or_none(use_cache=use_cache, **kwargs)
        if not item:
            vcprint(
                f"[BASE MANAGER _get_item_with_retry] FIRST ATTEMPT FAILED! Item not found for {kwargs}. Trying again...",
                verbose=info,
                color="yellow",
            )
            return await self._get_item_or_raise(use_cache=use_cache, **kwargs)
        return await self._initialize_item_runtime(item)  # type: ignore[return-value]

    @handle_errors
    async def _get_items(
        self, order_by: str | None = None, **kwargs: Any
    ) -> list[ModelT]:
        """Fetch multiple items from the model with filters."""
        if order_by:
            items = await self.model.filter(**kwargs).order_by(order_by).all()
        else:
            items = await self.model.filter(**kwargs).all()
        return [await self._initialize_item_runtime(item) for item in items]  # type: ignore[misc]

    @handle_errors
    async def _get_first_item(
        self, order_by: str | None = None, **kwargs: Any
    ) -> ModelT | None:
        """Fetch first item from the model with filters."""
        if order_by:
            item = await self.model.filter(**kwargs).order_by(order_by).first()
        else:
            item = await self.model.filter(**kwargs).first()
        return await self._process_item(item)

    @handle_errors
    async def _get_last_item(
        self, order_by: str | None = None, **kwargs: Any
    ) -> ModelT | None:
        """Fetch last item from the model with filters."""
        item = await self.model.filter(**kwargs).order_by(order_by).last()
        return await self._process_item(item)

    @handle_errors
    async def _create_item(self, **data: Any) -> ModelT:
        """Create a new item."""
        item = await self.model.create(**data)
        return await self._initialize_item_runtime(item)  # type: ignore[return-value]

    @handle_errors
    async def _create_items(
        self,
        items_data: list[dict[str, Any]],
        batch_size: int = 1000,
        ignore_conflicts: bool = False,
    ) -> list[ModelT]:
        """
        Create multiple items using TRUE bulk operations.
        Now uses the enhanced Model.bulk_create() method that follows the same
        data processing pipeline as individual operations.
        """
        if not items_data:
            return []

        try:
            created_items = await self.model.bulk_create(items_data)

            initialized_items: list[ModelT] = []
            for item in created_items:
                if item:
                    await self._initialize_item_runtime(item)
                    initialized_items.append(item)

            vcprint(
                f"✓ Created {len(initialized_items)} items with TRUE bulk operations",
                color="green",
            )
            return initialized_items

        except Exception as e:
            vcprint(f"Error in _create_items: {e}", color="red")
            raise

    @handle_errors
    async def _update_item(self, item: ModelT, **updates: Any) -> ModelT:
        """Update an existing item."""
        if not item:
            raise AppError(
                message="Cannot update non-existent item",
                error_type="NotFoundError",
                client_visible="The item to update could not be found.",
            )
        await item.update(**updates)
        return await self._initialize_item_runtime(item)  # type: ignore[return-value]

    @handle_errors
    async def _delete_item(self, item: ModelT) -> bool:
        """Delete an item."""
        if not item:
            raise AppError(
                message="Cannot delete non-existent item",
                error_type="NotFoundError",
                client_visible="The item to delete could not be found.",
            )
        await item.delete()
        return True

    async def _delete_items(self, item: ModelT) -> None:
        """Placeholder for :Delete multiple items!."""

    def _add_to_active(self, item_id: Any) -> Any:
        """Add an item ID to the active set."""
        self._active_items.add(item_id)
        return item_id

    def _remove_from_active(self, item_id: Any) -> None:
        """Remove an item ID from the active set."""
        self._active_items.discard(item_id)

    @handle_errors
    async def _fetch_related(
        self, item: ModelT, relation_name: str
    ) -> Model | list[Model] | None:
        """Fetch a single relationship for an item."""
        if not item:
            raise AppError(
                message="Cannot fetch relation for non-existent item",
                error_type="NotFoundError",
                client_visible="The item could not be found.",
            )
        related = await item.fetch_one_relation(relation_name)
        vcprint(
            related,
            "[BASE MANAGER _fetch_related] Related",
            verbose=debug,
            pretty=True,
            color="yellow",
        )
        return related

    @handle_errors
    async def _fetch_all_related(self, item: ModelT) -> dict[str, dict[str, Any]]:
        """Fetch all relationships for an item."""
        if not item:
            raise AppError(
                message="Cannot fetch relations for non-existent item",
                error_type="NotFoundError",
                client_visible="The item could not be found.",
            )
        return await item.fetch_all_related()

    @handle_errors
    async def load_item(self, use_cache: bool = True, **kwargs: Any) -> ModelT:
        """Load and initialize a single item."""
        return await self._get_item_or_raise(use_cache=use_cache, **kwargs)

    @handle_errors
    async def load_item_or_none(
        self, use_cache: bool = True, **kwargs: Any
    ) -> ModelT | None:
        """Load and initialize a single item or None."""
        return await self._get_item_or_none(use_cache=use_cache, **kwargs)

    @handle_errors
    async def load_item_with_retry(
        self, use_cache: bool = True, **kwargs: Any
    ) -> ModelT:
        """Load and initialize a single item with retry."""
        return await self._get_item_with_retry(use_cache=use_cache, **kwargs)

    @handle_errors
    async def load_items(self, **kwargs: Any) -> list[ModelT]:
        """Load and initialize multiple items."""
        items = await self._get_items(**kwargs)
        self._active_items.update([item.id for item in items if item])
        return [await self._initialize_item_runtime(item) for item in items if item]  # type: ignore[misc]

    async def load_by_id(self, item_id: Any) -> ModelT:
        """Load an item by ID."""
        return await self.load_item(id=item_id)

    async def load_by_id_with_retry(self, item_id: Any) -> ModelT:
        """Load an item by ID with retry."""
        return await self.load_item_with_retry(id=item_id)

    async def load_items_by_ids(self, item_ids: list[Any]) -> list[ModelT]:
        """Load multiple items by IDs."""
        # TODO: FAULTY METHOD : Does not work.

        return await self.load_items(id__in=item_ids)

    async def add_active_by_id(self, item_id: Any) -> ModelT:
        """Add an item to active set and return it."""
        self._add_to_active(item_id)
        return await self.load_by_id(item_id)

    async def add_active_by_ids(self, item_ids: list[Any]) -> list[ModelT]:
        """Add multiple items to active set."""
        # TODO: FAULTY METHOD USED: load_items_by_ids
        for item_id in item_ids:
            self._add_to_active(item_id)
        return await self.load_items_by_ids(item_ids)

    async def remove_active_by_id(self, item_id: Any) -> None:
        """Remove an item from active set."""
        self._remove_from_active(item_id)

    async def remove_active_by_ids(self, item_ids: list[Any]) -> None:
        """Remove multiple items from active set."""
        for item_id in item_ids:
            self._remove_from_active(item_id)

    async def remove_all_active(self) -> None:
        """Clear all active items."""
        self._active_items.clear()

    @handle_errors
    async def get_active_items(self) -> list[ModelT]:
        """Get all active items, initialized."""
        items = await asyncio.gather(
            *(self._get_item_or_raise(id=item_id) for item_id in self._active_items)
        )
        return list(items)

    async def create_item(self, **data: Any) -> ModelT:
        """Create and initialize an item."""
        item = await self._create_item(**data)
        vcprint(item, "BASE MANAGER Created item", verbose=debug, color="yellow")
        return await self._initialize_item_runtime(item)  # type: ignore[return-value]

    async def create_items(
        self,
        items_data: list[dict[str, Any]],
        batch_size: int = 1000,
        ignore_conflicts: bool = False,
    ) -> list[ModelT]:
        """Create multiple items at once using TRUE bulk operations.

        Args:
            items_data: A list of dictionaries, where each dictionary contains
                        the data for a single item to be created.
            batch_size: Number of items to create in each batch (default: 1000)
            ignore_conflicts: Whether to ignore conflicts during bulk creation (default: False)

        Returns:
            A list of created and initialized items.
        """
        return await self._create_items(
            items_data, batch_size=batch_size, ignore_conflicts=ignore_conflicts
        )

    async def update_item(self, item_id: Any, **updates: Any) -> ModelT:
        """Update an item by ID."""
        item = await self._get_item_or_raise(id=item_id)
        return await self._update_item(item, **updates)

    async def update_items(
        self, objects: list[ModelT], fields: list[str], batch_size: int = 1000
    ) -> int:
        """
        Update multiple items at once using TRUE bulk operations.
        Follows the same patterns as create_items().

        Args:
            objects: A list of model instances to update
            fields: List of field names to update
            batch_size: Number of items to update in each batch (default: 1000)

        Returns:
            Number of rows affected.
        """
        if not objects or not fields:
            return 0

        try:
            rows_affected = await self.model.bulk_update(objects, fields)

            initialized_items: list[ModelT | None] = []
            for item in objects:
                initialized_item = await self._initialize_item_runtime(item)
                initialized_items.append(initialized_item)

            vcprint(
                f"Updated {rows_affected} items with bulk operations through manager",
                color="green",
            )
            return rows_affected

        except Exception as e:
            vcprint(f"Error in bulk update: {e}", color="red")
            vcprint(
                "Attempting fallback to individual updates...",
                color="yellow",
            )

            success_count = 0
            for item in objects:
                try:
                    update_data = {
                        field: getattr(item, field, None) for field in fields
                    }
                    await self._update_item(item, **update_data)
                    success_count += 1
                except Exception as individual_error:
                    vcprint(
                        f"Failed to update individual item: {individual_error}",
                        color="red",
                    )
                    continue

            return success_count

    async def delete_item(self, item_id: Any) -> bool:
        """Delete an item by ID or raises an error if items does not exist"""
        item = await self._get_item_or_raise(id=item_id)

        success = await self._delete_item(item)
        if success:
            self._remove_from_active(item_id)
        return success

    async def delete_items(self, objects: list[ModelT], batch_size: int = 1000) -> int:
        """
        Delete multiple items at once using TRUE bulk operations.
        Follows the same patterns as create_items().

        Args:
            objects: A list of model instances to delete
            batch_size: Number of items to delete in each batch (default: 1000)

        Returns:
            Number of rows affected.
        """
        if not objects:
            return 0

        try:
            rows_affected = await self.model.bulk_delete(objects)

            for item in objects:
                if hasattr(item, "id") and item.id:
                    self._remove_from_active(item.id)

            vcprint(
                f"Deleted {rows_affected} items with bulk operations through manager",
                color="green",
            )
            return rows_affected

        except Exception as e:
            vcprint(f"Error in bulk delete: {e}", color="red")
            vcprint(
                "Attempting fallback to individual deletes...",
                color="yellow",
            )

            success_count = 0
            for item in objects:
                try:
                    success = await self._delete_item(item)
                    if success and hasattr(item, "id") and item.id:
                        self._remove_from_active(item.id)
                        success_count += 1
                except Exception as individual_error:
                    vcprint(
                        f"Failed to delete individual item: {individual_error}",
                        color="red",
                    )
                    continue

            return success_count

    async def exists(self, item_id: Any) -> bool:
        """Check if an item exists."""
        return bool(await self._get_item_or_none(id=item_id))

    async def get_or_create(
        self, defaults: dict[str, Any] | None = None, **kwargs: Any
    ) -> ModelT | None:
        """Get an item or create it if it doesn't exist."""
        item = await self._get_item_or_none(**kwargs)
        if not item and defaults:
            item = await self._create_item(**{**kwargs, **defaults})
        return await self._initialize_item_runtime(item)

    def _item_to_dict(self, item: ModelT | None) -> dict[str, Any] | None:
        """Convert an item to a dict using DTO if available."""
        if not item:
            return None
        if hasattr(item, "runtime") and hasattr(item.runtime, "dto"):
            return item.runtime.dto.to_dict()
        return item.to_dict()

    def _print_item_keys(self, item: ModelT | None) -> None:
        if not item:
            return

        print(f"\n{item.__class__.__name__} Item Keys:")
        if hasattr(item, "__annotations__"):
            for key in item.__annotations__.keys():
                data_type = item.__annotations__[key]
                print(
                    f"-> {key}: {data_type.__name__ if hasattr(data_type, '__name__') else str(data_type)}"
                )
        elif hasattr(item, "to_dict"):
            item_dict = item.to_dict()
            for key in item_dict.keys():
                value = item_dict[key]
                print(f"-> {key}: {type(value).__name__}")
        else:
            print("No keys available to display")

        if hasattr(item, "runtime") and hasattr(item.runtime, "dto"):
            print("\nDTO Keys:")
            item.runtime.dto.print_keys()

        print()

    async def get_item_dict(self, item_id: Any) -> dict[str, Any] | None:
        """Get an item's dict by ID."""
        item = await self.load_by_id(item_id)
        return self._item_to_dict(item)

    async def get_items_dict(self, **kwargs: Any) -> list[dict[str, Any] | None]:
        """Get dicts for multiple items."""
        items = await self.load_items(**kwargs)
        return [self._item_to_dict(item) for item in items if item]

    async def get_active_items_dict(self) -> list[dict[str, Any] | None]:
        """Get dicts for all active items."""
        items = await self.get_active_items()
        return [self._item_to_dict(item) for item in items if item]

    async def create_item_get_dict(self, **data: Any) -> dict[str, Any] | None:
        """Create an item and return its dict."""
        item = await self.create_item(**data)
        return self._item_to_dict(item)

    async def update_item_get_dict(
        self, item_id: Any, **updates: Any
    ) -> dict[str, Any] | None:
        """Update an item and return its dict."""
        item = await self.update_item(item_id, **updates)
        return self._item_to_dict(item)

    async def get_item_with_related(
        self, item_id: Any, relation_name: str
    ) -> tuple[ModelT, Model | list[Model] | None]:
        """Get an item with a specific relationship."""
        item = await self.load_by_id(item_id)
        vcprint(
            item,
            "[BASE MANAGER get_item_with_related] Item",
            verbose=debug,
            pretty=True,
            color="yellow",
        )
        if item:
            related_items = await self._fetch_related(item, relation_name)
            vcprint(
                related_items,
                "[BASE MANAGER get_item_with_related ] Related",
                verbose=debug,
                pretty=True,
                color="yellow",
            )
            return item, related_items
        return item, None

    async def get_item_with_related_with_retry(
        self, item_id: Any, relation_name: str
    ) -> tuple[ModelT, Model | list[Model] | None]:
        """Get an item with a specific relationship with retry."""
        item = await self.load_by_id_with_retry(item_id)
        vcprint(
            item,
            "[BASE MANAGER get_item_with_related] Item",
            verbose=debug,
            pretty=True,
            color="yellow",
        )
        if item:
            related_items = await self._fetch_related(item, relation_name)
            vcprint(
                related_items,
                "[BASE MANAGER get_item_with_related ] Related",
                verbose=debug,
                pretty=True,
                color="yellow",
            )
            return item, related_items
        return item, None

    async def get_items_with_related(self, relation_name: str) -> list[ModelT]:
        """Get all active items with a specific relationship."""
        items = await self.load_items()
        await asyncio.gather(
            *(self._fetch_related(item, relation_name) for item in items if item)
        )
        return items

    async def get_item_with_all_related(
        self, item_id: Any
    ) -> tuple[ModelT, dict[str, dict[str, Any]] | None]:
        """Get an item with all relationships."""
        item = await self.load_by_id(item_id)
        if item:
            related_items = await self._fetch_all_related(item)
            return item, related_items
        return item, None  # type: ignore[return-value]

    async def get_items_with_all_related(self) -> list[ModelT]:
        """Get all active items with all relationships."""
        items = await self.get_active_items()
        await asyncio.gather(*(self._fetch_all_related(item) for item in items if item))
        return items

    @handle_errors
    async def get_item_with_m2m(
        self, item_id: Any, relation_name: str
    ) -> tuple[ModelT | None, list[Model] | None]:
        """Load an item and fetch one M2M relationship."""
        item = await self.load_by_id(item_id)
        if item:
            m2m_items = await item.fetch_m2m(relation_name)
            return item, m2m_items
        return item, None  # type: ignore[return-value]

    @handle_errors
    async def add_m2m(self, item_id: Any, relation_name: str, *target_ids: Any) -> int:
        """Add M2M targets for an item."""
        item = await self.load_by_id(item_id)
        return await item.add_m2m(relation_name, *target_ids)

    @handle_errors
    async def remove_m2m(
        self, item_id: Any, relation_name: str, *target_ids: Any
    ) -> int:
        """Remove M2M targets for an item."""
        item = await self.load_by_id(item_id)
        return await item.remove_m2m(relation_name, *target_ids)

    @handle_errors
    async def set_m2m(
        self, item_id: Any, relation_name: str, target_ids: list[Any]
    ) -> None:
        """Replace all M2M targets for an item."""
        item = await self.load_by_id(item_id)
        await item.set_m2m(relation_name, target_ids)

    @handle_errors
    async def clear_m2m(self, item_id: Any, relation_name: str) -> int:
        """Clear all M2M targets for an item."""
        item = await self.load_by_id(item_id)
        return await item.clear_m2m(relation_name)

    @handle_errors
    async def get_items_with_related_list(
        self, relation_names: list[str]
    ) -> list[ModelT]:
        """Get all active items with multiple specific relationships."""
        items = await self.get_active_items()
        for item in items:
            if item:
                await asyncio.gather(
                    *(self._fetch_related(item, name) for name in relation_names)
                )
        return items

    async def get_item_through_fk(
        self, item_id: Any, first_relation: str, second_relation: str
    ) -> tuple[ModelT | None, Model | list[Model] | None, Model | list[Model] | None]:
        """Get an item through two FK hops."""
        item = await self.load_by_id(item_id)
        if item:
            fk_instance = await self._fetch_related(item, first_relation)
            if fk_instance and not isinstance(fk_instance, list):
                target = await self._fetch_related(fk_instance, second_relation)
                return item, fk_instance, target
            return item, fk_instance, None
        return None, None, None

    async def get_items_with_related_dict(
        self, relation_name: str
    ) -> list[dict[str, Any] | None]:
        """Get dicts for items with a specific relationship."""
        items = await self.get_items_with_related(relation_name)
        return [self._item_to_dict(item) for item in items if item]

    async def get_items_with_all_related_dict(self) -> list[dict[str, Any] | None]:
        """Get dicts for items with all relationships."""
        items = await self.get_items_with_all_related()
        return [self._item_to_dict(item) for item in items if item]

    async def create_item_get_object(self, **data: Any) -> ModelT:
        """Create an item and return it without runtime initialization."""
        item = await self._create_item(**data)
        return item

    async def add_active_by_id_or_not(self, item_id: Any = None) -> ModelT | None:
        """Add an item to active set if ID provided, else return None."""
        item = await self._get_item_or_none(id=item_id)

        if item:
            self._add_to_active(item_id)
            return await self._process_item(item)
        return None

    async def add_active_by_item_or_not(
        self, item: ModelT | None = None
    ) -> ModelT | None:
        """Add an item to active set if provided, else return None."""
        if item:
            self._add_to_active(item.id)
            return await self._process_item(item)
        return None

    async def add_active_by_ids_or_not(
        self, item_ids: list[Any] | None = None
    ) -> list[ModelT] | None:
        """Add items to active set by IDs if provided, else return None."""
        if item_ids:
            items: list[ModelT] = []
            for item_id in item_ids:
                self._add_to_active(item_id)
                item = await self._get_item_or_none(id=item_id)
                if item:
                    processed = await self._process_item(item)
                    if processed:
                        items.append(processed)
            return items
        return None

    async def add_active_by_items_or_not(
        self, items: list[ModelT] | None = None
    ) -> list[ModelT] | None:
        """Add items to active set if provided, else return None."""
        if items:
            processed_items: list[ModelT] = []
            for item in items:
                self._add_to_active(item.id)
                processed = await self._process_item(item)
                if processed:
                    processed_items.append(processed)
            return processed_items
        return None

    async def get_active_item(self, item_id: Any) -> ModelT | None:
        """Get an active item by ID."""
        # TODO: Doesnt look for whether item is currently active.
        item = await self._get_item_or_raise(id=item_id)
        return await self._process_item(item)

    async def get_active_item_dict(self, item_id: Any) -> dict[str, Any] | None:
        """Get an active item's dict by ID."""
        item = await self.get_active_item(item_id)
        return item.to_dict() if item else None

    async def load_item_get_dict(
        self, use_cache: bool = True, **kwargs: Any
    ) -> dict[str, Any] | None:
        """Load an item and return its dict."""
        item = await self.load_item(use_cache=use_cache, **kwargs)
        return item.to_dict() if item else None

    async def load_items_by_ids_get_dict(
        self, item_ids: list[Any]
    ) -> list[dict[str, Any]]:
        """Load items by IDs and return their dicts."""
        # TODO: FAULTY METHOD USED: load_items_by_ids
        items = await self.load_items_by_ids(item_ids)
        return [item.to_dict() for item in items if item]

    @handle_errors
    async def filter_items(self, **kwargs: Any) -> list[ModelT]:
        """Filter items directly from the model."""
        items = await self.model.filter(**kwargs).all()
        return [await self._process_item(item) for item in items if item]  # type: ignore[misc]

    async def filter_items_by_ids(self, item_ids: list[Any]) -> list[ModelT]:
        """Filter items by IDs directly from the model."""
        items = await self.model.filter(id__in=item_ids).all()
        return [await self._process_item(item) for item in items if item]  # type: ignore[misc]

    async def filter_items_get_dict(self, **kwargs: Any) -> list[dict[str, Any]]:
        """Filter items and return their dicts."""
        items = await self.filter_items(**kwargs)
        return [item.to_dict() for item in items if item]

    async def get_active_item_with_fk(
        self, item_id: Any, related_model: str
    ) -> tuple[ModelT | None, Model | list[Model] | None]:
        """Get an active item with a foreign key relation."""
        item = await self._get_item_or_raise(id=item_id)
        item = await self._process_item(item)
        related = await self._fetch_related(item, related_model) if item else None
        return item, related

    @handle_errors
    async def get_active_items_with_fks(self) -> list[ModelT]:
        """Get active items with all foreign key relations."""
        items = await self.get_active_items()
        for item in items:
            if item:
                await self._fetch_related(item, "all")
        return items

    @handle_errors
    async def get_active_item_with_ifk(self, related_model: str) -> ModelT | None:
        """Get an active item with an inverse foreign key relation."""
        item = await self.add_active_item()
        if item:
            await item.fetch_ifk(related_model)
        return item

    @handle_errors
    async def get_active_items_with_ifks(self) -> list[ModelT]:
        """Get active items with all inverse foreign key relations."""
        items = await self.get_active_items()
        for item in items:
            if item:
                await item.fetch_ifks()
        return items

    async def get_active_items_with_ifks_dict(self) -> list[dict[str, Any]]:
        """Get dicts for active items with all inverse foreign key relations."""
        return [
            item.to_dict() for item in await self.get_active_items_with_ifks() if item
        ]

    async def get_active_item_with_all_related(self) -> ModelT | None:
        """Get an active item with all relations."""
        item = await self.add_active_item()
        if item:
            await item.fetch_all_related()
        return item

    async def get_active_items_with_all_related(self) -> list[ModelT]:
        """Get active items with all relations."""
        items = await self.get_active_items()
        for item in items:
            if item:
                await item.fetch_all_related()
        return items

    async def get_active_items_with_all_related_dict(self) -> list[dict[str, Any]]:
        """Get dicts for active items with all relations."""
        return [
            item.to_dict()
            for item in await self.get_active_items_with_all_related()
            if item
        ]

    @handle_errors
    async def get_active_item_with_one_relation(
        self, relation_name: str
    ) -> list[ModelT]:
        """Get an active item with one specific relation."""
        items = await self.get_active_items()
        for item in items:
            if item:
                await item.fetch_one_relation(relation_name)
        return items

    @handle_errors
    async def get_active_items_with_one_relation(
        self, relation_name: str
    ) -> list[ModelT]:
        """Get active items with one specific relation."""
        items = await self.get_active_items()
        for item in items:
            if item:
                await item.fetch_one_relation(relation_name)
        return items

    async def get_active_item_with_one_relation_dict(
        self, relation_name: str
    ) -> list[dict[str, Any]]:
        """Get dicts for an active item with one specific relation."""
        return [
            item.to_dict()
            for item in await self.get_active_item_with_one_relation(relation_name)
            if item
        ]

    @handle_errors
    async def get_active_item_with_related_models_list(
        self, related_models_list: list[str]
    ) -> list[ModelT]:
        """Get an active item with multiple specific related models."""
        items = await self.get_active_items()
        for item in items:
            for related_model in related_models_list:
                await item.fetch_one_relation(related_model)
        return items

    @handle_errors
    async def get_active_items_with_related_models_list(
        self, related_models_list: list[str]
    ) -> list[ModelT]:
        """Get active items with multiple specific related models."""
        items = await self.get_active_items()
        for item in items:
            for related_model in related_models_list:
                await item.fetch_one_relation(related_model)
        return items

    async def get_active_item_with_related_models_list_dict(
        self, related_models_list: list[str]
    ) -> list[dict[str, Any]]:
        """Get dicts for an active item with multiple specific related models."""
        return [
            item.to_dict()
            for item in await self.get_active_item_with_related_models_list(
                related_models_list
            )
            if item
        ]

    async def get_active_item_with_through_fk(
        self, item_id: Any, first_relationship: str, second_relationship: str
    ) -> tuple[ModelT | None, Model | None, Model | None]:
        """Get an active item through two FK hops."""
        item, fk_instance = await self.get_active_item_with_fk(
            item_id, first_relationship
        )
        if fk_instance and not isinstance(fk_instance, list):
            target_instance = await fk_instance.fetch_fk(second_relationship)
            return item, fk_instance, target_instance
        elif item:
            return item, None, None
        else:
            return None, None, None

    @handle_errors
    async def get_active_item_through_ifk(
        self, item_id: Any, first_relationship: str, second_relationship: str
    ) -> tuple[ModelT | None, Model | list[Model] | None, Any]:
        """Get an active item through two inverse FK hops."""
        item, ifk_instance = await self.get_active_item_with_ifk(
            item_id, first_relationship
        )
        if ifk_instance:
            target_instance = await ifk_instance.fetch_ifk(second_relationship)
            return item, ifk_instance, target_instance
        elif item:
            return item, None, None
        else:
            return None, None, None

    @property
    def active_item_ids(self) -> set[Any]:
        """Return a copy of active item IDs."""
        return self._active_items.copy()

    def get_all_attributes(self) -> dict[str, Any]:
        """Get all non-method attributes of the manager instance."""
        attributes: dict[str, Any] = {"model": self.model}
        if hasattr(self, "__dict__"):
            attributes.update(
                {k: v for k, v in self.__dict__.items() if not callable(v)}
            )
        for attr in dir(self):
            if not attr.startswith("__") and attr not in attributes:
                value = getattr(self, attr)
                if not callable(value):
                    attributes[attr] = value
        return attributes

    def get_item_attributes(self, item: ModelT | None) -> dict[str, Any]:
        """Get all attributes of an item, including computed and relation fields."""
        if not item:
            return {}
        attributes: dict[str, Any] = getattr(item, "__dict__", {}).copy()
        for field in self.computed_fields | self.relation_fields:
            if hasattr(item, field):
                attributes[field] = getattr(item, field)
        for attr in dir(item):
            if not attr.startswith("__") and attr not in attributes:
                try:
                    attributes[attr] = getattr(item, attr)
                except Exception:
                    attributes[attr] = "Error retrieving attribute"
        return attributes

    @handle_errors
    def _auto_fetch_on_init_sync(self) -> None:
        """Fetch items on initialization (synchronous version).
        Runs the async fetch using asyncio.run() since we're in a pure sync context.
        All logic is handled by the async version.
        """
        if self.fetch_on_init_limit <= 0:
            return

        asyncio.run(self._auto_fetch_on_init_async())

    async def _auto_fetch_on_init_async(self) -> None:
        """Fetch items on initialization (async version with full DTO support)."""
        if self.fetch_on_init_limit <= 0:
            return

        start_time = time.perf_counter()

        items = await self.model.filter().limit(self.fetch_on_init_limit).all()
        initialized_items = [
            await self._initialize_item_runtime(item) for item in items
        ]
        count = len(initialized_items)

        elapsed_time = time.perf_counter() - start_time

        if elapsed_time < 1.0:
            time_str = f"{elapsed_time * 1000:.2f}ms"
        else:
            time_str = f"{elapsed_time:.3f}s"

        if not self._FETCH_ON_INIT_WITH_WARNINGS_OFF:
            vcprint(initialized_items, "FETCHED ITEMS:", color="red", pretty=True)

        vcprint(
            f"[{self.model.__name__}] AUTOMATED FETCH ON INIT: {count} items in {time_str}",
            color="red",
            background="yellow",
            style="bold",
        )

        warnings_suppressed = False
        warning_limit_threshold = 100
        if self._FETCH_ON_INIT_WITH_WARNINGS_OFF:
            suppression_prefix = "YES_I_KNOW_WHAT_IM_DOING_TURN_OFF_WARNINGS_FOR_LIMIT_"
            if self._FETCH_ON_INIT_WITH_WARNINGS_OFF.startswith(suppression_prefix):
                try:
                    warning_limit_threshold = int(
                        self._FETCH_ON_INIT_WITH_WARNINGS_OFF[len(suppression_prefix) :]
                    )
                    warnings_suppressed = (
                        warning_limit_threshold >= self.fetch_on_init_limit
                    )
                except ValueError:
                    vcprint(
                        f"Invalid FETCH_ON_INIT_WITH_WARNINGS_OFF format: {self._FETCH_ON_INIT_WITH_WARNINGS_OFF}",
                        "[ERROR] Expected format: YES_I_KNOW_WHAT_IM_DOING_TURN_OFF_WARNINGS_FOR_LIMIT_<number>",
                        color="red",
                    )

        if count >= (self.fetch_on_init_limit - 5):
            self._trigger_limit_reached_warning(count, initialized_items)

        if not warnings_suppressed and count > warning_limit_threshold:
            self._trigger_fetch_warnings(
                count, initialized_items, warning_limit_threshold
            )

        self._active_items.update(initialized_items)

    def _trigger_fetch_warnings(
        self, count: int, items: list[ModelT | None], warning_limit_threshold: int
    ) -> None:
        """Trigger escalating warnings based on the number of fetched items."""
        if count <= warning_limit_threshold:
            return  # No warning if below or at the custom threshold
        elif count <= 500:
            # Moderate warning for exceeding threshold
            vcprint(
                f"AUTOFETCH COUNT: {count}",
                f"[WARNING!!!!] INIT method for model {self.model.__name__} fetched {count} items (>{warning_limit_threshold})! "
                f"To suppress, set FETCH_ON_INIT_WITH_WARNINGS_OFF='YES_I_KNOW_WHAT_IM_DOING_TURN_OFF_WARNINGS_FOR_LIMIT_{self.fetch_on_init_limit}'",
                color="red",
            )
            vcprint(
                items,
                "FETCHED ITEMS (LOOK AT WHAT YOU DID):",
                color="yellow",
                pretty=True,
            )
        elif count <= 1000:
            # Big, screen-filling warning
            warning_lines = [
                "=" * 80,
                f" AUTOFETCH COUNT: {count} ".center(80, "="),
                f"[WARNING!!!!] INIT method for model {self.model.__name__} fetched {count} items (>500)!".center(
                    80
                ),
                f"Threshold was {warning_limit_threshold}. ARE YOU SURE?".center(80),
                "To suppress this warning, set:".center(80),
                f"FETCH_ON_INIT_WITH_WARNINGS_OFF='YES_I_KNOW_WHAT_IM_DOING_TURN_OFF_WARNINGS_FOR_LIMIT_{self.fetch_on_init_limit}'".center(
                    80
                ),
                "=" * 80,
                "ITEMS FETCHED:".center(80),
            ]
            vcprint("\n".join(warning_lines), color="orange")
            vcprint(items, pretty=True, color="yellow")
        else:
            # Dramatic, fear-inducing warning
            scary_warning = [
                "!" * 80,
                f"!!! AUTOFETCH COUNT: {count} !!!".center(80),
                f"!!! [DANGER ZONE] INIT method for model {self.model.__name__} fetched {count} items (>1000) !!!".center(
                    80
                ),
                "!!! THIS IS INSANE! YOU MIGHT CRASH EVERYTHING !!!".center(80),
                f"!!! Threshold was {warning_limit_threshold}. PROCEED WITH EXTREME CAUTION !!!".center(
                    80
                ),
                "To suppress this madness, set:".center(80),
                f"FETCH_ON_INIT_WITH_WARNINGS_OFF='YES_I_KNOW_WHAT_IM_DOING_TURN_OFF_WARNINGS_FOR_LIMIT_{self.fetch_on_init_limit}'".center(
                    80
                ),
                "!" * 80,
                "FETCHED ITEMS (GOOD LUCK):".center(80),
            ]
            vcprint("\n".join(scary_warning), color="red")
            vcprint(items, pretty=True, color="yellow")

    def _trigger_limit_reached_warning(
        self, count: int, items: list[ModelT | None]
    ) -> None:
        """Trigger a non-suppressible warning if the fetch count approaches or hits the limit."""
        warning_lines = [
            "*" * 80,
            f"!!! AUTOFETCH LIMIT REACHED OR NEAR: {count} vs LIMIT {self.fetch_on_init_limit} !!!".center(
                80
            ),
            f"!!! [CRITICAL ERROR] INIT method for model {self.model.__name__} fetched {count} items !!!".center(
                80
            ),
            "!!! THIS IS WITHIN 5 OF YOUR SET LIMIT OR AT IT !!!".center(80),
            "!!! YOU MAY NOT HAVE ALL DATA - THIS IS DANGEROUS !!!".center(80),
            "!!! THIS WARNING CANNOT BE SUPPRESSED - FIX YOUR LIMIT OR LOGIC !!!".center(
                80
            ),
            "*" * 80,
            "FETCHED ITEMS (CHECK FOR COMPLETENESS):".center(80),
        ]
        vcprint("\n".join(warning_lines), color="magenta")
        vcprint(items, pretty=True, color="yellow")

    def _validation_error(
        self, class_name: str, data: Any, field: str, message: str
    ) -> None:
        vcprint(
            data,
            f"[{class_name} ERROR!] Invalid or missing '{field}' field. You provided",
            verbose=True,
            pretty=True,
            color="red",
        )
        vcprint("Sorry. Here comes the ugly part:\n", verbose=True, color="yellow")
        raise ValueError(message)

    # ==================== SYNCHRONOUS WRAPPER METHODS ====================

    def load_item_sync(self, use_cache: bool = True, **kwargs: Any) -> ModelT:
        """Synchronous wrapper for load_item()."""
        try:
            asyncio.get_running_loop()
            raise RuntimeError(
                "load_item_sync() called in async context. Use await load_item() instead."
            )
        except RuntimeError as e:
            if "no running event loop" not in str(e):
                raise
        return asyncio.run(self.load_item(use_cache=use_cache, **kwargs))

    def load_item_or_none_sync(
        self, use_cache: bool = True, **kwargs: Any
    ) -> ModelT | None:
        """Synchronous wrapper for load_item_or_none()."""
        try:
            asyncio.get_running_loop()
            raise RuntimeError(
                "load_item_or_none_sync() called in async context. Use await load_item_or_none() instead."
            )
        except RuntimeError as e:
            if "no running event loop" not in str(e):
                raise
        return asyncio.run(self.load_item_or_none(use_cache=use_cache, **kwargs))

    def load_items_sync(self, **kwargs: Any) -> list[ModelT]:
        """Synchronous wrapper for load_items()."""
        try:
            asyncio.get_running_loop()
            raise RuntimeError(
                "load_items_sync() called in async context. Use await load_items() instead."
            )
        except RuntimeError as e:
            if "no running event loop" not in str(e):
                raise
        return asyncio.run(self.load_items(**kwargs))

    def load_by_id_sync(self, item_id: Any) -> ModelT:
        """Synchronous wrapper for load_by_id()."""
        try:
            asyncio.get_running_loop()
            raise RuntimeError(
                "load_by_id_sync() called in async context. Use await load_by_id() instead."
            )
        except RuntimeError as e:
            if "no running event loop" not in str(e):
                raise
        return asyncio.run(self.load_by_id(item_id))

    def filter_items_sync(self, **kwargs: Any) -> list[ModelT]:
        """Synchronous wrapper for filter_items()."""
        try:
            asyncio.get_running_loop()
            raise RuntimeError(
                "filter_items_sync() called in async context. Use await filter_items() instead."
            )
        except RuntimeError as e:
            if "no running event loop" not in str(e):
                raise
        return asyncio.run(self.filter_items(**kwargs))

    def create_item_sync(self, **data: Any) -> ModelT:
        """Synchronous wrapper for create_item()."""
        try:
            asyncio.get_running_loop()
            raise RuntimeError(
                "create_item_sync() called in async context. Use await create_item() instead."
            )
        except RuntimeError as e:
            if "no running event loop" not in str(e):
                raise
        return asyncio.run(self.create_item(**data))

    def update_item_sync(self, item_id: Any, **updates: Any) -> ModelT:
        """Synchronous wrapper for update_item()."""
        try:
            asyncio.get_running_loop()
            raise RuntimeError(
                "update_item_sync() called in async context. Use await update_item() instead."
            )
        except RuntimeError as e:
            if "no running event loop" not in str(e):
                raise
        return asyncio.run(self.update_item(item_id, **updates))

    def delete_item_sync(self, item_id: Any) -> bool:
        """Synchronous wrapper for delete_item()."""
        try:
            asyncio.get_running_loop()
            raise RuntimeError(
                "delete_item_sync() called in async context. Use await delete_item() instead."
            )
        except RuntimeError as e:
            if "no running event loop" not in str(e):
                raise
        return asyncio.run(self.delete_item(item_id))

    def get_or_create_sync(
        self, defaults: dict[str, Any] | None = None, **kwargs: Any
    ) -> ModelT | None:
        """Synchronous wrapper for get_or_create()."""
        try:
            asyncio.get_running_loop()
            raise RuntimeError(
                "get_or_create_sync() called in async context. Use await get_or_create() instead."
            )
        except RuntimeError as e:
            if "no running event loop" not in str(e):
                raise
        return asyncio.run(self.get_or_create(defaults=defaults, **kwargs))

    def exists_sync(self, item_id: Any) -> bool:
        """Synchronous wrapper for exists()."""
        try:
            asyncio.get_running_loop()
            raise RuntimeError(
                "exists_sync() called in async context. Use await exists() instead."
            )
        except RuntimeError as e:
            if "no running event loop" not in str(e):
                raise
        return asyncio.run(self.exists(item_id))

    def get_active_items_sync(self) -> list[ModelT]:
        """Synchronous wrapper for get_active_items()."""
        try:
            asyncio.get_running_loop()
            raise RuntimeError(
                "get_active_items_sync() called in async context. Use await get_active_items() instead."
            )
        except RuntimeError as e:
            if "no running event loop" not in str(e):
                raise
        return asyncio.run(self.get_active_items())

    def get_item_dict_sync(self, item_id: Any) -> dict[str, Any] | None:
        """Synchronous wrapper for get_item_dict()."""
        try:
            asyncio.get_running_loop()
            raise RuntimeError(
                "get_item_dict_sync() called in async context. Use await get_item_dict() instead."
            )
        except RuntimeError as e:
            if "no running event loop" not in str(e):
                raise
        return asyncio.run(self.get_item_dict(item_id))

    def get_items_dict_sync(self, **kwargs: Any) -> list[dict[str, Any] | None]:
        """Synchronous wrapper for get_items_dict()."""
        try:
            asyncio.get_running_loop()
            raise RuntimeError(
                "get_items_dict_sync() called in async context. Use await get_items_dict() instead."
            )
        except RuntimeError as e:
            if "no running event loop" not in str(e):
                raise
        return asyncio.run(self.get_items_dict(**kwargs))
