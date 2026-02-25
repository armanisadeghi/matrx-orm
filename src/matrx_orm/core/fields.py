import json
import re
import uuid
from datetime import date, datetime, time, timedelta
from decimal import Decimal, InvalidOperation
from enum import Enum as PythonEnum
from ipaddress import IPv4Address, IPv6Address, ip_network
from typing import TYPE_CHECKING, Any, Generic, List, Type, Union, overload
from typing_extensions import TypeVar
from uuid import UUID

# TypeVar with default (PEP 696) via typing_extensions for Python < 3.13 compatibility.
_JT = TypeVar("_JT", default=dict[str, Any] | list[Any])

if TYPE_CHECKING:
    pass  # overload imports already available via typing


class Field:
    if TYPE_CHECKING:

        @overload
        def __get__(self, obj: None, objtype: type = ...) -> "Field": ...
        @overload
        def __get__(self, obj: object, objtype: type = ...) -> Any: ...
        def __get__(self, obj: object | None, objtype: type = ...) -> Any: ...

    CORE_ATTRS = {
        "db_type",
        "is_native",
        "null",
        "nullable",
        "unique",
        "primary_key",
        "index",
    }

    def __init__(
        self,
        db_type: str,
        is_native: bool = True,
        null: bool = True,
        nullable: bool = None,
        unique: bool = False,
        primary_key: bool = False,
        default=None,
        index: bool = False,
        validators: list = None,
        **kwargs,
    ):
        self.db_type = db_type
        self.is_native = is_native
        self.null = null
        self.nullable = (
            False if primary_key else (nullable if nullable is not None else null)
        )
        self.unique = unique
        self.primary_key = primary_key
        self.default = default
        self.index = index
        self.validators = validators or []
        self.extra = kwargs
        self.name = None
        self.model = None
        self._order_direction = None

    def contribute_to_class(self, model, name):
        """
        Hook for performing additional initialization when the field is added to a model.
        """
        self.name = name
        self.model = model

    def get_default(self):
        """Get the default value for this field."""
        if callable(self.default):
            return self.default()
        return self.default

    async def validate(self, value) -> None:
        """
        Validate the field value.
        Raises ValueError if validation fails.
        """
        if not self.null and value is None:
            raise ValueError(f"Field {self.name} cannot be null")
        for validator in self.validators:
            await validator(value)

    def to_python(self, value):
        """Convert the database value to a Python object."""
        return value

    def get_db_prep_value(self, value):
        """Convert the Python value to a database value."""
        if value is None:
            return None
        return value

    def desc(self):
        """Mark this field for descending order."""
        self._order_direction = "DESC"
        return self

    def asc(self):
        """Mark this field for ascending order (default)."""
        self._order_direction = "ASC"
        return self

    def to_dict(self) -> dict:
        """
        Convert the field configuration to a dictionary.
        Dynamically includes all field attributes, including those from subclasses.

        Returns:
            dict: A dictionary containing all field options and attributes
        """
        # Get all instance attributes
        all_attrs = {
            key: value
            for key, value in vars(self).items()
            if not key.startswith("_")
            and value is not None  # Skip private attrs and None values
        }

        # Start with core attributes
        result = {key: all_attrs[key] for key in self.CORE_ATTRS if key in all_attrs}

        # Special handling for default value
        if self.default is not None:
            if callable(self.default):
                result["default"] = self.default.__name__
            else:
                result["default"] = self.default

        # Special handling for validators
        if self.validators:
            result["validators"] = [
                getattr(validator, "__name__", str(validator))
                for validator in self.validators
            ]

        # Add name and model if set
        if self.name is not None:
            result["name"] = self.name
        if self.model is not None:
            result["model"] = self.model.__name__

        # Add remaining attributes (including subclass-specific ones)
        for key, value in all_attrs.items():
            if key not in result and key != "extra":
                # Special handling for various types
                if isinstance(value, (str, int, float, bool)):
                    result[key] = value
                elif isinstance(value, (list, tuple)):
                    result[key] = list(value)
                elif isinstance(value, dict):
                    result[key] = dict(value)
                else:
                    # For other types, use string representation
                    result[key] = str(value)

        # Add any extra kwargs
        if hasattr(self, "extra") and self.extra:
            result.update(self.extra)

        return result


class UUIDField(Field):
    if TYPE_CHECKING:

        @overload
        def __get__(self, obj: None, objtype: type = ...) -> "UUIDField": ...
        @overload
        def __get__(self, obj: object, objtype: type = ...) -> str | None: ...
        def __get__(
            self, obj: object | None, objtype: type = ...
        ) -> str | "UUIDField" | None: ...

    def __init__(self, **kwargs):
        super().__init__("text", **kwargs)

    def get_default(self):
        if self.default == "gen_random_uuid()":
            return str(uuid.uuid4())
        return self.default

    def to_python(self, value):
        return str(value) if value is not None else None

    def from_db_value(self, value):
        return str(value) if value is not None else None


class UUIDFieldREAL(Field):
    def __init__(self, **kwargs):
        super().__init__("UUID", **kwargs)

    def get_default(self):
        if self.default == "gen_random_uuid()":
            return str(uuid.uuid4())
        return str(self.default) if self.default else None

    def to_python(self, value):
        if value is None:
            return None
        return str(value)

    def from_db_value(self, value):
        if value is None:
            return None
        return str(value)

    async def validate(self, value):
        await super().validate(value)
        if value is not None:
            try:
                str(UUID(str(value)))
            except ValueError:
                raise ValueError("Value must be a valid UUID format")


class CharField(Field):
    if TYPE_CHECKING:

        @overload
        def __get__(self, obj: None, objtype: type = ...) -> "CharField": ...
        @overload
        def __get__(self, obj: object, objtype: type = ...) -> str | None: ...
        def __get__(
            self, obj: object | None, objtype: type = ...
        ) -> str | "CharField" | None: ...

    def __init__(self, max_length: int = 255, **kwargs):
        super().__init__(f"VARCHAR({max_length})", **kwargs)
        self.max_length = max_length

    def get_db_prep_value(self, value):
        if value is None:
            return None
        value = str(value)
        return value[: self.max_length]  # Ensure db value doesn't exceed max_length

    async def validate(self, value: str) -> None:
        await super().validate(value)
        if value is not None:
            if not isinstance(value, str):
                raise ValueError(f"Field {self.name} must be a string")
            if len(value) > self.max_length:
                raise ValueError(f"Value exceeds maximum length of {self.max_length}")


class TextField(Field):
    if TYPE_CHECKING:

        @overload
        def __get__(self, obj: None, objtype: type = ...) -> "TextField": ...
        @overload
        def __get__(self, obj: object, objtype: type = ...) -> str | None: ...
        def __get__(
            self, obj: object | None, objtype: type = ...
        ) -> str | "TextField" | None: ...

    def __init__(self, **kwargs):
        super().__init__("TEXT", **kwargs)

    def get_db_prep_value(self, value):
        if value is None:
            return None
        return str(value)

    async def validate(self, value: str) -> None:
        await super().validate(value)
        if value is not None and not isinstance(value, str):
            raise ValueError(f"Field {self.name} must be a string")


class IntegerField(Field):
    if TYPE_CHECKING:

        @overload
        def __get__(self, obj: None, objtype: type = ...) -> "IntegerField": ...
        @overload
        def __get__(self, obj: object, objtype: type = ...) -> int | None: ...
        def __get__(
            self, obj: object | None, objtype: type = ...
        ) -> int | "IntegerField" | None: ...

    def __init__(self, **kwargs):
        super().__init__("INTEGER", **kwargs)

    def to_python(self, value):
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            raise ValueError(f"Field {self.name} must be convertible to integer")

    def get_db_prep_value(self, value):
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            raise ValueError(f"Field {self.name} must be convertible to integer")

    async def validate(self, value: int) -> None:
        await super().validate(value)
        if value is not None:
            try:
                int(value)  # Ensure value can be converted to int
            except (TypeError, ValueError):
                raise ValueError(f"Field {self.name} must be an integer")


class FloatField(Field):
    if TYPE_CHECKING:

        @overload
        def __get__(self, obj: None, objtype: type = ...) -> "FloatField": ...
        @overload
        def __get__(self, obj: object, objtype: type = ...) -> float | None: ...
        def __get__(
            self, obj: object | None, objtype: type = ...
        ) -> float | "FloatField" | None: ...

    def __init__(self, **kwargs):
        super().__init__("FLOAT", **kwargs)

    def get_db_prep_value(self, value):
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            raise ValueError(f"Field {self.name} must be convertible to float")

    async def validate(self, value: float) -> None:
        await super().validate(value)
        if value is not None and not isinstance(value, (float, int)):
            raise ValueError("Value must be a float")


class BooleanField(Field):
    if TYPE_CHECKING:

        @overload
        def __get__(self, obj: None, objtype: type = ...) -> "BooleanField": ...
        @overload
        def __get__(self, obj: object, objtype: type = ...) -> bool | None: ...
        def __get__(
            self, obj: object | None, objtype: type = ...
        ) -> bool | "BooleanField" | None: ...

    def __init__(self, **kwargs):
        super().__init__("BOOLEAN", **kwargs)

    async def validate(self, value: bool) -> None:
        await super().validate(value)
        if value is not None and not isinstance(value, bool):
            raise ValueError("Value must be a boolean after conversion")

    def to_python(self, value):
        """Convert input value to Python bool."""
        if value is None:
            return None

        # Handle boolean values directly
        if isinstance(value, bool):
            return value

        # Convert common string and integer representations
        if isinstance(value, (str, int)):
            # Normalize strings to lowercase for consistency
            if isinstance(value, str):
                value = value.lower().strip()

            # Explicitly map known true/false values
            if value in (1, "1", "true", "True"):
                return True
            if value in (0, "0", "false", "False"):
                return False

            # Fall back to Python's bool() for other cases (e.g., non-empty string)
            try:
                return bool(value)
            except ValueError:
                pass

        raise ValueError(f"Cannot convert {value} (type: {type(value)}) to boolean")

    def get_db_prep_value(self, value):
        """Prepare value for database, ensuring it's a bool."""
        if value is None:
            return None

        # Convert the input to a Python bool using to_python
        python_value = self.to_python(value)

        # Ensure the result is a bool before sending to the database
        if not isinstance(python_value, bool):
            raise ValueError(
                f"[ORM BooleanField] Expected boolean, got {type(python_value)} after conversion"
            )

        return python_value


class DateTimeField(Field):
    if TYPE_CHECKING:

        @overload
        def __get__(self, obj: None, objtype: type = ...) -> "DateTimeField": ...
        @overload
        def __get__(self, obj: object, objtype: type = ...) -> datetime | None: ...
        def __get__(
            self, obj: object | None, objtype: type = ...
        ) -> datetime | "DateTimeField" | None: ...

    def __init__(self, auto_now: bool = False, auto_now_add: bool = False, **kwargs):
        super().__init__("TIMESTAMP", **kwargs)
        self.auto_now = auto_now
        self.auto_now_add = auto_now_add

    def to_python(self, value):
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        return value

    def get_db_prep_value(self, value):
        if value is None:
            return None
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        return value


class TimeField(Field):
    if TYPE_CHECKING:

        @overload
        def __get__(self, obj: None, objtype: type = ...) -> "TimeField": ...
        @overload
        def __get__(self, obj: object, objtype: type = ...) -> time | None: ...
        def __get__(
            self, obj: object | None, objtype: type = ...
        ) -> time | "TimeField" | None: ...

    def __init__(self, **kwargs):
        super().__init__("TIME", **kwargs)

    def to_python(self, value):
        if isinstance(value, str):
            return time.fromisoformat(value)
        return value

    def get_db_prep_value(self, value):
        if value is None:
            return None
        if isinstance(value, str):
            return time.fromisoformat(value)
        return value


class DateField(Field):
    if TYPE_CHECKING:

        @overload
        def __get__(self, obj: None, objtype: type = ...) -> "DateField": ...
        @overload
        def __get__(self, obj: object, objtype: type = ...) -> date | None: ...
        def __get__(
            self, obj: object | None, objtype: type = ...
        ) -> date | "DateField" | None: ...

    def __init__(self, **kwargs):
        super().__init__("DATE", **kwargs)

    def to_python(self, value):
        if isinstance(value, str):
            return date.fromisoformat(value)
        return value

    def get_db_prep_value(self, value):
        if value is None:
            return None
        if isinstance(value, str):
            return date.fromisoformat(value)
        return value


class JSONField(Field, Generic[_JT]):
    if TYPE_CHECKING:

        @overload
        def __get__(self, obj: None, objtype: type = ...) -> "JSONField[_JT]": ...
        @overload
        def __get__(self, obj: object, objtype: type = ...) -> _JT | None: ...
        def __get__(
            self, obj: object | None, objtype: type = ...
        ) -> _JT | None | "JSONField[_JT]": ...
        def __set__(self, obj: object, value: _JT | None) -> None: ...

    def __init__(self, **kwargs):
        super().__init__("JSONB", **kwargs)

    def to_python(self, value):
        if isinstance(value, str):
            return json.loads(value)
        return value

    def get_db_prep_value(self, value):
        if value is not None and not isinstance(value, str):
            return json.dumps(value)
        return value


class ArrayField(Field):
    if TYPE_CHECKING:

        @overload
        def __get__(self, obj: None, objtype: type = ...) -> "ArrayField": ...
        @overload
        def __get__(self, obj: object, objtype: type = ...) -> list[Any] | None: ...
        def __get__(
            self, obj: object | None, objtype: type = ...
        ) -> list[Any] | "ArrayField" | None: ...

    def __init__(self, item_type: Field, **kwargs):
        super().__init__(f"{item_type.db_type}[]", **kwargs)
        self.item_type = item_type

    async def validate(self, value: list) -> None:
        await super().validate(value)
        if value is not None:
            if not isinstance(value, list):
                raise ValueError("Value must be a list")
            for item in value:
                await self.item_type.validate(item)

    def to_python(self, value) -> list:
        if value is None:
            return value
        return [self.item_type.to_python(item) for item in value]  # Fixed: Expect list

    def get_db_prep_value(self, value: list):
        if value is None:
            return value
        return [
            self.item_type.get_db_prep_value(item) for item in value
        ]  # Fixed: Return list


class EnumField(Field):
    def __init__(
        self,
        enum_class: Type[PythonEnum] = None,
        choices: List[str] = None,
        max_length: int = 255,
        **kwargs,
    ):
        """
        An Enum field that can work with either a Python Enum class or a list of string choices.

        Args:
            enum_class: A Python Enum class to use for validation
            choices: A list of valid string values (alternative to enum_class)
            max_length: Maximum length of the VARCHAR field
            **kwargs: Additional Field arguments
        """
        if enum_class and choices:
            raise ValueError("Cannot specify both enum_class and choices")
        if not enum_class and not choices:
            raise ValueError("Must specify either enum_class or choices")

        # Set db_type to VARCHAR with specified max_length
        super().__init__("VARCHAR", **kwargs)
        self.max_length = max_length

        # Handle enum_class or choices
        if enum_class:
            if not issubclass(enum_class, PythonEnum):
                raise ValueError("enum_class must be a subclass of enum.Enum")
            self.enum_class = enum_class
            self.choices = [e.value for e in enum_class]
        else:
            self.enum_class = None
            self.choices = choices

    def get_db_prep_value(self, value: Union[str, PythonEnum, None]) -> str:
        """Convert Python value to database string."""
        if value is None:
            return None
        if self.enum_class and isinstance(value, self.enum_class):
            return value.value
        return str(value)

    def to_python(self, value: Union[str, None]) -> Union[PythonEnum, str, None]:
        """Convert database value to Python object."""
        if value is None:
            return None
        if self.enum_class:
            try:
                return self.enum_class(value)
            except ValueError:
                if value in self.choices:
                    return value  # Return string if valid but not an enum value
                raise ValueError(
                    f"Invalid value '{value}' for enum {self.enum_class.__name__}"
                )
        return value

    async def validate(self, value: Union[str, PythonEnum, None]) -> None:
        """Validate the value against available choices."""
        await super().validate(value)
        if value is None:
            return

        # Convert enum to string value if needed
        check_value = (
            value.value
            if self.enum_class and isinstance(value, self.enum_class)
            else value
        )

        if check_value not in self.choices:
            raise ValueError(f"Value '{check_value}' must be one of {self.choices}")

    def to_dict(self) -> dict:
        """Add enum-specific attributes to the field dictionary."""
        base_dict = super().to_dict()
        base_dict.update(
            {
                "choices": self.choices,
                "max_length": self.max_length,
                "enum_class": self.enum_class.__name__ if self.enum_class else None,
            }
        )
        return base_dict


class IPv4Field(Field):
    def __init__(self, **kwargs):
        super().__init__("INET", **kwargs)

    async def validate(self, value: str) -> None:
        await super().validate(value)
        try:
            IPv4Address(value)
        except ValueError:
            raise ValueError(f"{value} is not a valid IPv4 address")


class IPv6Field(Field):
    def __init__(self, **kwargs):
        super().__init__("INET", **kwargs)

    async def validate(self, value: str) -> None:
        await super().validate(value)
        try:
            IPv6Address(value)
        except ValueError:
            raise ValueError(f"{value} is not a valid IPv6 address")


class MacAddressField(Field):
    def __init__(self, **kwargs):
        super().__init__("MACADDR", **kwargs)

    async def validate(self, value: str) -> None:
        if not re.match(r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$", value):
            raise ValueError(f"{value} is not a valid MAC address")


class EmailField(CharField):
    def __init__(self, **kwargs):
        super().__init__(max_length=254, **kwargs)
        self.validators.append(self.validate_email)

    @staticmethod
    async def validate_email(value: str) -> None:
        if value and "@" not in value:
            raise ValueError("Invalid email address")


class DecimalField(Field):
    if TYPE_CHECKING:

        @overload
        def __get__(self, obj: None, objtype: type = ...) -> "DecimalField": ...
        @overload
        def __get__(self, obj: object, objtype: type = ...) -> Decimal | None: ...
        def __get__(
            self, obj: object | None, objtype: type = ...
        ) -> Decimal | "DecimalField" | None: ...

    def __init__(self, max_digits: int = None, decimal_places: int = 2, **kwargs):
        column_type = "NUMERIC"
        if max_digits is not None:
            column_type = f"NUMERIC({max_digits},{decimal_places})"

        super().__init__(column_type, **kwargs)
        self.max_digits = max_digits
        self.decimal_places = decimal_places

    def to_python(self, value):
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except InvalidOperation:
            raise ValueError(f"Field {self.name} must be convertible to Decimal")

    def get_db_prep_value(self, value):
        if value is None:
            return None
        try:
            return Decimal(str(value))
        except InvalidOperation:
            raise ValueError(f"Field {self.name} must be convertible to Decimal")

    async def validate(self, value) -> None:
        await super().validate(value)
        if value is not None:
            str_value = str(value)
            if "." in str_value:
                integer_part, decimal_part = str_value.split(".")
                if self.max_digits is not None and (
                    len(integer_part) + len(decimal_part) > self.max_digits
                ):
                    raise ValueError(
                        f"Value exceeds maximum precision of {self.max_digits} digits"
                    )
                if len(decimal_part) > self.decimal_places:
                    raise ValueError(
                        f"Value exceeds allowed {self.decimal_places} decimal places"
                    )


class BigIntegerField(Field):
    if TYPE_CHECKING:

        @overload
        def __get__(self, obj: None, objtype: type = ...) -> "BigIntegerField": ...
        @overload
        def __get__(self, obj: object, objtype: type = ...) -> int | None: ...
        def __get__(
            self, obj: object | None, objtype: type = ...
        ) -> int | "BigIntegerField" | None: ...

    def __init__(self, **kwargs):
        super().__init__("BIGINT", **kwargs)

    def to_python(self, value):
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            raise ValueError(f"Field {self.name} must be convertible to integer")

    def get_db_prep_value(self, value):
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            raise ValueError(f"Field {self.name} must be convertible to integer")

    async def validate(self, value: int) -> None:
        await super().validate(value)
        if value is not None and not isinstance(value, int):
            raise ValueError("Value must be a big integer")


class SmallIntegerField(Field):
    if TYPE_CHECKING:

        @overload
        def __get__(self, obj: None, objtype: type = ...) -> "SmallIntegerField": ...
        @overload
        def __get__(self, obj: object, objtype: type = ...) -> int | None: ...
        def __get__(
            self, obj: object | None, objtype: type = ...
        ) -> int | "SmallIntegerField" | None: ...

    def __init__(self, **kwargs):
        super().__init__("SMALLINT", **kwargs)

    def to_python(self, value):
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            raise ValueError(f"Field {self.name} must be convertible to integer")

    def get_db_prep_value(self, value):
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            raise ValueError(f"Field {self.name} must be convertible to integer")

    async def validate(self, value: int) -> None:
        await super().validate(value)
        if value is not None and not isinstance(value, int):
            raise ValueError("Value must be a small integer")


class BinaryField(Field):
    if TYPE_CHECKING:

        @overload
        def __get__(self, obj: None, objtype: type = ...) -> "BinaryField": ...
        @overload
        def __get__(self, obj: object, objtype: type = ...) -> bytes | None: ...
        def __get__(
            self, obj: object | None, objtype: type = ...
        ) -> bytes | "BinaryField" | None: ...

    def __init__(self, **kwargs):
        super().__init__("BYTEA", **kwargs)

    async def validate(self, value: bytes) -> None:
        await super().validate(value)
        if value is not None and not isinstance(value, (bytes, bytearray)):
            raise ValueError("Value must be binary data")


class SlugField(CharField):
    def __init__(self, max_length: int = 200, **kwargs):
        super().__init__(max_length=max_length, **kwargs)

    async def validate(self, value: str) -> None:
        await super().validate(value)
        if value is not None and not re.match(r"^[-a-zA-Z0-9_]+$", value):
            raise ValueError(
                "Slug can only contain letters, numbers, underscores, and hyphens"
            )


class IPNetworkField(Field):
    def __init__(self, **kwargs):
        super().__init__("CIDR", **kwargs)

    async def validate(self, value: str) -> None:
        await super().validate(value)
        try:
            ip_network(value)
        except ValueError:
            raise ValueError(f"{value} is not a valid CIDR notation")


class MoneyField(DecimalField):
    def __init__(self, max_digits: int = 19, decimal_places: int = 2, **kwargs):
        super().__init__(max_digits, decimal_places, **kwargs)


class HStoreField(Field):
    if TYPE_CHECKING:

        @overload
        def __get__(self, obj: None, objtype: type = ...) -> "HStoreField": ...
        @overload
        def __get__(
            self, obj: object, objtype: type = ...
        ) -> dict[str, str | None] | None: ...
        def __get__(
            self, obj: object | None, objtype: type = ...
        ) -> dict[str, str | None] | "HStoreField" | None: ...

    def __init__(self, **kwargs):
        super().__init__("HSTORE", **kwargs)

    def to_python(self, value):
        if value is None:
            return None
        if isinstance(value, str):
            return json.loads(value)
        return value

    def get_db_prep_value(self, value):
        if value is None:
            return None
        if not isinstance(value, dict):
            raise ValueError(f"Field {self.name} must be a dictionary")
        # asyncpg expects all hstore values as strings
        return {str(k): str(v) if v is not None else None for k, v in value.items()}

    async def validate(self, value: dict) -> None:
        await super().validate(value)
        if value is not None and not isinstance(value, dict):
            raise ValueError("Value must be a dictionary")


class JSONBField(Field, Generic[_JT]):
    if TYPE_CHECKING:

        @overload
        def __get__(self, obj: None, objtype: type = ...) -> "JSONBField[_JT]": ...
        @overload
        def __get__(self, obj: object, objtype: type = ...) -> _JT | None: ...
        def __get__(
            self, obj: object | None, objtype: type = ...
        ) -> _JT | None | "JSONBField[_JT]": ...
        def __set__(self, obj: object, value: _JT | None) -> None: ...

    def __init__(self, **kwargs):
        super().__init__("JSONB", **kwargs)

    def to_python(self, value):
        if isinstance(value, str):
            return json.loads(value)
        return value

    def get_db_prep_value(self, value):
        if value is None:
            return None
        if isinstance(value, str):
            return value
        return json.dumps(value)


class FileField(CharField):
    def __init__(self, max_length: int = 100, **kwargs):
        super().__init__(max_length=max_length, **kwargs)

    async def validate(self, value: str) -> None:
        await super().validate(value)
        if value and not isinstance(value, str):
            raise ValueError("File path must be a string")


class TimeDeltaField(Field):
    if TYPE_CHECKING:

        @overload
        def __get__(self, obj: None, objtype: type = ...) -> "TimeDeltaField": ...
        @overload
        def __get__(self, obj: object, objtype: type = ...) -> timedelta | None: ...
        def __get__(
            self, obj: object | None, objtype: type = ...
        ) -> timedelta | "TimeDeltaField" | None: ...

    def __init__(self, **kwargs):
        super().__init__("INTERVAL", **kwargs)

    def to_python(self, value):
        if value is None:
            return None
        if isinstance(value, timedelta):
            return value
        if isinstance(value, (int, float)):
            return timedelta(seconds=value)
        return value

    def get_db_prep_value(self, value):
        if value is None:
            return None
        if isinstance(value, timedelta):
            return value
        if isinstance(value, (int, float)):
            return timedelta(seconds=value)
        raise ValueError(
            f"Field {self.name} must be a timedelta or numeric seconds value"
        )

    async def validate(self, value) -> None:
        await super().validate(value)
        if value is not None and not isinstance(value, (int, float, timedelta)):
            raise ValueError(
                "Value must be a timedelta or duration in seconds (int/float)"
            )


class UUIDArrayField(ArrayField):
    def __init__(self, **kwargs):
        super().__init__(UUIDField(), **kwargs)


class PointField(Field):
    def __init__(self, **kwargs):
        super().__init__("POINT", **kwargs)

    def to_python(self, value):
        if value is None:
            return None
        if isinstance(value, (list, tuple)) and len(value) == 2:
            return (float(value[0]), float(value[1]))
        return value

    def get_db_prep_value(self, value):
        if value is None:
            return None
        if not (isinstance(value, (list, tuple)) and len(value) == 2):
            raise ValueError(f"Field {self.name} must be a (x, y) tuple")
        return (float(value[0]), float(value[1]))

    async def validate(self, value):
        await super().validate(value)
        if value is not None and (
            not isinstance(value, (tuple, list)) or len(value) != 2
        ):
            raise ValueError(
                "Value must be a tuple of two float numbers representing a point"
            )


class RangeField(Field):
    def __init__(self, range_type: str, **kwargs):
        super().__init__(range_type, **kwargs)

    async def validate(self, value):
        await super().validate(value)
        if value is not None and not (isinstance(value, tuple) and len(value) == 2):
            raise ValueError("Range value must be a tuple of two values")


class CITextField(CharField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_type = "CITEXT"


class PrimitiveArrayField(Field):
    def __init__(self, element_type: str, **kwargs):
        super().__init__(f"{element_type}[]", **kwargs)

    async def validate(self, value: list) -> None:
        await super().validate(value)
        if not isinstance(value, list):
            raise ValueError("Value must be a list of primitive elements")


class JSONBArrayField(ArrayField):
    def __init__(self, **kwargs):
        super().__init__(JSONBField(), **kwargs)


class HStoreArrayField(ArrayField):
    def __init__(self, **kwargs):
        super().__init__(HStoreField(), **kwargs)


class TextArrayField(ArrayField):
    def __init__(self, **kwargs):
        super().__init__(TextField(), **kwargs)


class IntegerArrayField(ArrayField):
    def __init__(self, **kwargs):
        super().__init__(IntegerField(), **kwargs)


class BooleanArrayField(ArrayField):
    def __init__(self, **kwargs):
        super().__init__(BooleanField(), **kwargs)


class DecimalArrayField(ArrayField):
    def __init__(self, max_digits: int, decimal_places: int, **kwargs):
        super().__init__(
            DecimalField(max_digits=max_digits, decimal_places=decimal_places), **kwargs
        )


class DateArrayField(ArrayField):
    def __init__(self, **kwargs):
        super().__init__(DateField(), **kwargs)


class IPv6ArrayField(ArrayField):
    def __init__(self, **kwargs):
        super().__init__(IPv6Field(), **kwargs)


class IPNetworkArrayField(ArrayField):
    def __init__(self, **kwargs):
        super().__init__(IPNetworkField(), **kwargs)


class TimeArrayField(ArrayField):
    def __init__(self, **kwargs):
        super().__init__(TimeField(), **kwargs)


class ImageField(FileField):
    def __init__(self, max_length: int = 100, **kwargs):
        super().__init__(max_length=max_length, **kwargs)

    async def validate(self, value: str) -> None:
        await super().validate(value)
        if value and not value.lower().endswith(
            (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg")
        ):
            raise ValueError(
                "Invalid image format. Supported formats: PNG, JPG, JPEG, GIF, BMP, SVG"
            )


class IPAddressField(Field):
    def __init__(self, **kwargs):
        super().__init__("INET", **kwargs)

    async def validate(self, value: str) -> None:
        await super().validate(value)
        try:
            IPv4Address(value)
        except ValueError:
            try:
                IPv6Address(value)
            except ValueError:
                raise ValueError(f"{value} is not a valid IPv4 or IPv6 address")


# -------- A CRITICAL CHANGE WAS MADE HERE AND COULD CAUSE SYSTEMATIC ISSUES WITH THE FK FIELD NOW CONVERTING TO AND FROM PYTHON --------


class ForeignKey(Field):
    def __init__(
        self,
        to_model: str | type,
        to_column: str,
        related_name: str = None,
        on_delete: str = "CASCADE",
        on_update: str = "CASCADE",
        to_db: str = None,
        to_schema: str = None,
        **kwargs,
    ):
        super().__init__("UUID", **kwargs)
        self.to_model = to_model
        self.to_column = to_column
        self.related_name = related_name
        self.on_delete = on_delete
        self.on_update = on_update
        self.to_db = to_db  # target database project name (cross-database FK)
        self.to_schema = to_schema  # target schema hint (e.g. 'auth' for auth.users)

    def to_python(self, value):
        """Convert database UUID value to Python string (consistent with UUIDField)"""
        return str(value) if value else None

    def from_db_value(self, value):
        """Convert database UUID value to Python string (consistent with UUIDField)"""
        return str(value) if value else None

    def get_db_prep_value(self, value):
        """Convert Python value to database UUID value"""
        if value is None:
            return None
        # Ensure we can handle both string UUIDs and UUID objects
        return str(value)

    async def validate(self, value) -> None:
        await super().validate(value)
        # Optional: Add UUID format validation
        if value is not None:
            try:
                str(UUID(str(value)))
            except ValueError:
                raise ValueError("Foreign key value must be a valid UUID format")


class CompositeField(Field):
    def __init__(self, fields, **kwargs):
        super().__init__("COMPOSITE", **kwargs)
        self.fields = fields
        self.primary_key = True

    async def validate(self, value: tuple) -> None:
        await super().validate(value)
        if value is not None and len(value) != len(self.fields):
            raise ValueError(f"Composite key must have {len(self.fields)} values")

    def to_python(self, value) -> tuple:
        if isinstance(value, str):
            return tuple(json.loads(value))
        return tuple(value) if value else None

    def get_db_prep_value(self, value):
        if value is None:
            return None
        return json.dumps(list(value))


class VersionField(Field):
    """Integer field that provides optimistic locking.

    On every ``save()`` / ``update_instance()`` call the ORM automatically:
      1. Adds ``WHERE version = <current>`` to the UPDATE statement.
      2. Increments the column by 1.
      3. Raises ``OptimisticLockError`` if 0 rows were affected (stale write).

    Usage::

        class Order(Model):
            id = UUIDField(primary_key=True, default=uuid4)
            total = DecimalField()
            version = VersionField()   # starts at 1, auto-increments

        order = await Order.get(id=some_id)
        order.total = Decimal("99.99")
        await order.save()             # raises OptimisticLockError if stale
    """

    def __init__(self, **kwargs) -> None:
        kwargs.setdefault("default", 1)
        kwargs.setdefault("null", False)
        kwargs.setdefault("nullable", False)
        super().__init__("INTEGER", **kwargs)
        self.is_version_field = True

    def to_python(self, value) -> int:
        if value is None:
            return 1
        return int(value)

    def get_db_prep_value(self, value):
        return int(value) if value is not None else 1


class VectorField(Field):
    """Stores a fixed-dimension float vector using pgvector's ``vector(n)`` type.

    Handles serialization between Python ``list[float]`` and the pgvector wire
    format ``[0.1,0.2,...]``.  Validates dimensionality before writing to avoid
    silent truncation errors from the database.

    The ``dtype`` parameter is reserved for forward-compatibility with
    pgvector 0.7+ types (``halfvec``, ``sparsevec``) and does not affect the
    generated DDL in the current release.

    Usage::

        class Document(Model):
            id = UUIDField(primary_key=True, default=uuid4)
            content = TextField()
            embedding = VectorField(dimensions=1536)

        # Similarity search
        results = await Document.nearest("embedding", query_vector, metric="cosine").limit(20).all()
    """

    def __init__(self, dimensions: int, dtype: str = "float32", **kwargs) -> None:
        self.dimensions = dimensions
        self.dtype = dtype
        super().__init__(f"vector({dimensions})", **kwargs)
        self.is_vector_field = True

    def to_python(self, value) -> list[float] | None:
        if value is None:
            return None
        if isinstance(value, list):
            return value
        return [float(x) for x in str(value).strip("[]").split(",")]

    def get_db_prep_value(self, value) -> str | None:
        if value is None:
            return None
        if isinstance(value, (list, tuple)):
            if len(value) != self.dimensions:
                raise ValueError(
                    f"VectorField expects {self.dimensions} dimensions, got {len(value)}"
                )
            return "[" + ",".join(str(float(x)) for x in value) + "]"
        return str(value)

    async def validate(self, value) -> None:
        await super().validate(value)
        if value is not None and isinstance(value, (list, tuple)):
            if len(value) != self.dimensions:
                raise ValueError(
                    f"VectorField expects {self.dimensions} dimensions, got {len(value)}"
                )
