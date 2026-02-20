"""Level 1: Field types — validation, conversion, db_type."""

import asyncio
import json
from datetime import date, datetime, time
from enum import Enum
from uuid import uuid4

import pytest

from matrx_orm.core.fields import (
    ArrayField,
    BooleanField,
    CharField,
    DateField,
    DateTimeField,
    DecimalField,
    EmailField,
    EnumField,
    Field,
    FloatField,
    ForeignKey,
    IntegerField,
    JSONField,
    TextField,
    TimeField,
    UUIDField,
    UUIDFieldREAL,
)


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


# ---------------------------------------------------------------------------
# Base Field
# ---------------------------------------------------------------------------

class TestBaseField:
    def test_db_type(self):
        f = Field("TEXT")
        assert f.db_type == "TEXT"

    def test_to_python_passthrough(self):
        f = Field("TEXT")
        assert f.to_python("hello") == "hello"
        assert f.to_python(None) is None

    def test_get_db_prep_value_none(self):
        f = Field("TEXT")
        assert f.get_db_prep_value(None) is None

    def test_nullable_default(self):
        f = Field("TEXT")
        assert f.null is True

    def test_not_nullable(self):
        f = Field("TEXT", null=False)
        assert f.null is False

    def test_validate_rejects_none_when_not_nullable(self):
        f = Field("TEXT", null=False)
        f.name = "test_field"
        with pytest.raises(ValueError, match="cannot be null"):
            _run(f.validate(None))

    def test_validate_allows_none_when_nullable(self):
        f = Field("TEXT", null=True)
        f.name = "test_field"
        _run(f.validate(None))

    def test_primary_key_flag(self):
        f = Field("UUID", primary_key=True)
        assert f.primary_key is True

    def test_unique_flag(self):
        f = Field("TEXT", unique=True)
        assert f.unique is True

    def test_index_flag(self):
        f = Field("TEXT", index=True)
        assert f.index is True


# ---------------------------------------------------------------------------
# UUIDField (text-based)
# ---------------------------------------------------------------------------

class TestUUIDField:
    def test_db_type(self):
        f = UUIDField()
        assert f.db_type == "text"

    def test_to_python_string(self):
        uid = str(uuid4())
        f = UUIDField()
        assert f.to_python(uid) == uid

    def test_to_python_none(self):
        f = UUIDField()
        assert f.to_python(None) is None


# ---------------------------------------------------------------------------
# UUIDFieldREAL
# ---------------------------------------------------------------------------

class TestUUIDFieldREAL:
    def test_db_type(self):
        f = UUIDFieldREAL()
        assert f.db_type == "UUID"

    def test_to_python_converts_to_str(self):
        uid = uuid4()
        f = UUIDFieldREAL()
        assert f.to_python(uid) == str(uid)

    def test_to_python_none(self):
        f = UUIDFieldREAL()
        assert f.to_python(None) is None

    def test_validate_rejects_bad_uuid(self):
        f = UUIDFieldREAL()
        f.name = "pk"
        with pytest.raises(ValueError, match="valid UUID"):
            _run(f.validate("not-a-uuid"))

    def test_validate_accepts_valid_uuid(self):
        f = UUIDFieldREAL()
        f.name = "pk"
        _run(f.validate(str(uuid4())))


# ---------------------------------------------------------------------------
# CharField
# ---------------------------------------------------------------------------

class TestCharField:
    def test_db_type_default_max_length(self):
        f = CharField()
        assert f.db_type == "VARCHAR(255)"
        assert f.max_length == 255

    def test_db_type_custom_max_length(self):
        f = CharField(max_length=50)
        assert f.db_type == "VARCHAR(50)"

    def test_get_db_prep_value_truncates(self):
        f = CharField(max_length=5)
        assert f.get_db_prep_value("abcdefgh") == "abcde"

    def test_get_db_prep_value_none(self):
        f = CharField()
        assert f.get_db_prep_value(None) is None

    def test_validate_rejects_non_string(self):
        f = CharField()
        f.name = "title"
        with pytest.raises(ValueError, match="must be a string"):
            _run(f.validate(123))

    def test_validate_rejects_too_long(self):
        f = CharField(max_length=3)
        f.name = "title"
        with pytest.raises(ValueError, match="maximum length"):
            _run(f.validate("abcd"))

    def test_validate_accepts_valid(self):
        f = CharField(max_length=10)
        f.name = "title"
        _run(f.validate("ok"))


# ---------------------------------------------------------------------------
# TextField
# ---------------------------------------------------------------------------

class TestTextField:
    def test_db_type(self):
        f = TextField()
        assert f.db_type == "TEXT"

    def test_get_db_prep_value_casts_to_str(self):
        f = TextField()
        assert f.get_db_prep_value(42) == "42"

    def test_get_db_prep_value_none(self):
        f = TextField()
        assert f.get_db_prep_value(None) is None

    def test_validate_rejects_non_string(self):
        f = TextField()
        f.name = "body"
        with pytest.raises(ValueError, match="must be a string"):
            _run(f.validate(999))


# ---------------------------------------------------------------------------
# IntegerField
# ---------------------------------------------------------------------------

class TestIntegerField:
    def test_db_type(self):
        f = IntegerField()
        assert f.db_type == "INTEGER"

    def test_to_python_int(self):
        f = IntegerField()
        f.name = "age"
        assert f.to_python("42") == 42

    def test_to_python_none(self):
        f = IntegerField()
        f.name = "age"
        assert f.to_python(None) is None

    def test_to_python_bad_value(self):
        f = IntegerField()
        f.name = "age"
        with pytest.raises(ValueError, match="convertible to integer"):
            f.to_python("abc")

    def test_get_db_prep_value_int(self):
        f = IntegerField()
        f.name = "age"
        assert f.get_db_prep_value("10") == 10

    def test_get_db_prep_value_none(self):
        f = IntegerField()
        f.name = "age"
        assert f.get_db_prep_value(None) is None

    def test_validate_rejects_non_int(self):
        f = IntegerField()
        f.name = "age"
        with pytest.raises(ValueError, match="must be an integer"):
            _run(f.validate("not_int"))


# ---------------------------------------------------------------------------
# FloatField
# ---------------------------------------------------------------------------

class TestFloatField:
    def test_db_type(self):
        assert FloatField().db_type == "FLOAT"

    def test_validate_accepts_float(self):
        f = FloatField()
        f.name = "score"
        _run(f.validate(3.14))

    def test_validate_accepts_int(self):
        f = FloatField()
        f.name = "score"
        _run(f.validate(3))

    def test_validate_rejects_string(self):
        f = FloatField()
        f.name = "score"
        with pytest.raises(ValueError, match="must be a float"):
            _run(f.validate("nope"))


# ---------------------------------------------------------------------------
# BooleanField
# ---------------------------------------------------------------------------

class TestBooleanField:
    def test_db_type(self):
        assert BooleanField().db_type == "BOOLEAN"

    @pytest.mark.parametrize("input_val,expected", [
        (True, True),
        (False, False),
        (1, True),
        (0, False),
        ("true", True),
        ("false", False),
        ("1", True),
        ("0", False),
    ])
    def test_to_python_coercion(self, input_val, expected):
        f = BooleanField()
        assert f.to_python(input_val) is expected

    def test_to_python_none(self):
        assert BooleanField().to_python(None) is None

    def test_get_db_prep_value_returns_bool(self):
        f = BooleanField()
        assert f.get_db_prep_value("true") is True

    def test_get_db_prep_value_none(self):
        assert BooleanField().get_db_prep_value(None) is None


# ---------------------------------------------------------------------------
# DateTimeField / DateField / TimeField
# ---------------------------------------------------------------------------

class TestDateTimeField:
    def test_db_type(self):
        assert DateTimeField().db_type == "TIMESTAMP"

    def test_to_python_from_string(self):
        f = DateTimeField()
        result = f.to_python("2024-01-15T10:30:00")
        assert isinstance(result, datetime)
        assert result.year == 2024

    def test_to_python_passthrough_datetime(self):
        now = datetime.now()
        assert DateTimeField().to_python(now) is now

    def test_auto_now_flag(self):
        f = DateTimeField(auto_now=True)
        assert f.auto_now is True


class TestDateField:
    def test_db_type(self):
        assert DateField().db_type == "DATE"

    def test_to_python_from_string(self):
        result = DateField().to_python("2024-06-15")
        assert isinstance(result, date)
        assert result.day == 15


class TestTimeField:
    def test_db_type(self):
        assert TimeField().db_type == "TIME"

    def test_to_python_from_string(self):
        result = TimeField().to_python("14:30:00")
        assert isinstance(result, time)
        assert result.hour == 14


# ---------------------------------------------------------------------------
# JSONField
# ---------------------------------------------------------------------------

class TestJSONField:
    def test_db_type(self):
        assert JSONField().db_type == "JSONB"

    def test_to_python_from_string(self):
        f = JSONField()
        result = f.to_python('{"a": 1}')
        assert result == {"a": 1}

    def test_to_python_passthrough_dict(self):
        d = {"key": "val"}
        assert JSONField().to_python(d) is d

    def test_get_db_prep_value_serializes(self):
        f = JSONField()
        result = f.get_db_prep_value({"x": [1, 2]})
        assert json.loads(result) == {"x": [1, 2]}

    def test_get_db_prep_value_none(self):
        assert JSONField().get_db_prep_value(None) is None


# ---------------------------------------------------------------------------
# ArrayField
# ---------------------------------------------------------------------------

class TestArrayField:
    def test_db_type(self):
        f = ArrayField(item_type=IntegerField())
        assert f.db_type == "INTEGER[]"

    def test_to_python_converts_items(self):
        inner = IntegerField()
        inner.name = "num"
        f = ArrayField(item_type=inner)
        assert f.to_python(["1", "2"]) == [1, 2]

    def test_to_python_none(self):
        f = ArrayField(item_type=IntegerField())
        assert f.to_python(None) is None

    def test_validate_rejects_non_list(self):
        f = ArrayField(item_type=IntegerField())
        f.name = "nums"
        with pytest.raises(ValueError, match="must be a list"):
            _run(f.validate("not_a_list"))

    def test_get_db_prep_value_converts_items(self):
        inner = IntegerField()
        inner.name = "num"
        f = ArrayField(item_type=inner)
        assert f.get_db_prep_value(["3", "4"]) == [3, 4]


# ---------------------------------------------------------------------------
# EnumField
# ---------------------------------------------------------------------------

class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


class TestEnumField:
    def test_db_type(self):
        f = EnumField(enum_class=Color)
        assert f.db_type == "VARCHAR"

    def test_init_requires_enum_or_choices(self):
        with pytest.raises(ValueError, match="Must specify"):
            EnumField()

    def test_init_rejects_both(self):
        with pytest.raises(ValueError, match="Cannot specify both"):
            EnumField(enum_class=Color, choices=["a"])

    def test_get_db_prep_value_enum_member(self):
        f = EnumField(enum_class=Color)
        assert f.get_db_prep_value(Color.RED) == "red"

    def test_get_db_prep_value_string(self):
        f = EnumField(enum_class=Color)
        assert f.get_db_prep_value("green") == "green"

    def test_to_python_returns_enum(self):
        f = EnumField(enum_class=Color)
        assert f.to_python("red") == Color.RED

    def test_to_python_none(self):
        f = EnumField(enum_class=Color)
        assert f.to_python(None) is None

    def test_validate_rejects_invalid_choice(self):
        f = EnumField(enum_class=Color)
        f.name = "color"
        with pytest.raises(ValueError, match="must be one of"):
            _run(f.validate("purple"))

    def test_choices_mode(self):
        f = EnumField(choices=["a", "b", "c"])
        assert f.choices == ["a", "b", "c"]
        assert f.get_db_prep_value("b") == "b"

    def test_to_python_choices_mode(self):
        f = EnumField(choices=["x", "y"])
        assert f.to_python("x") == "x"


# ---------------------------------------------------------------------------
# DecimalField
# ---------------------------------------------------------------------------

class TestDecimalField:
    def test_db_type_with_precision(self):
        f = DecimalField(max_digits=10, decimal_places=2)
        assert f.db_type == "NUMERIC(10,2)"

    def test_db_type_no_precision(self):
        f = DecimalField()
        assert f.db_type == "NUMERIC"

    def test_validate_too_many_digits(self):
        f = DecimalField(max_digits=5, decimal_places=2)
        f.name = "price"
        with pytest.raises(ValueError, match="maximum precision"):
            _run(f.validate(12345.67))

    def test_validate_too_many_decimals(self):
        f = DecimalField(max_digits=10, decimal_places=2)
        f.name = "price"
        with pytest.raises(ValueError, match="decimal places"):
            _run(f.validate(1.123))

    def test_validate_accepts_valid(self):
        f = DecimalField(max_digits=10, decimal_places=2)
        f.name = "price"
        _run(f.validate(99.99))


# ---------------------------------------------------------------------------
# ForeignKey (fields.py version)
# ---------------------------------------------------------------------------

class TestForeignKeyField:
    def test_db_type(self):
        fk = ForeignKey(to_model="User", to_column="id")
        assert fk.db_type == "UUID"

    def test_to_python(self):
        fk = ForeignKey(to_model="User", to_column="id")
        uid = str(uuid4())
        assert fk.to_python(uid) == uid

    def test_to_python_none(self):
        fk = ForeignKey(to_model="User", to_column="id")
        assert fk.to_python(None) is None

    def test_validate_rejects_bad_uuid(self):
        fk = ForeignKey(to_model="User", to_column="id")
        fk.name = "user_id"
        with pytest.raises(ValueError, match="valid UUID"):
            _run(fk.validate("bad"))

    def test_on_delete_default(self):
        fk = ForeignKey(to_model="User", to_column="id")
        assert fk.on_delete == "CASCADE"

    def test_on_delete_custom(self):
        fk = ForeignKey(to_model="User", to_column="id", on_delete="SET NULL")
        assert fk.on_delete == "SET NULL"


# ---------------------------------------------------------------------------
# EmailField
# ---------------------------------------------------------------------------

class TestEmailField:
    def test_db_type(self):
        f = EmailField()
        assert "VARCHAR" in f.db_type

    def test_validate_accepts_valid(self):
        f = EmailField()
        f.name = "email"
        _run(f.validate("user@example.com"))

    def test_validate_rejects_invalid(self):
        f = EmailField()
        f.name = "email"
        with pytest.raises(ValueError):
            _run(f.validate("not_an_email"))
