"""Level 1: ORMException hierarchy — init, enrich, format_message, sanitize."""

import pytest

from matrx_orm.exceptions import (
    ORMException,
    ValidationError,
    QueryError,
    DoesNotExist,
    MultipleObjectsReturned,
    DatabaseError,
    ConnectionError,
    IntegrityError,
    TransactionError,
    ConfigurationError,
    CacheError,
    StateError,
    RelationshipError,
    AdapterError,
    FieldError,
    MigrationError,
    ParameterError,
    UnknownDatabaseError,
)


class FakeModel:
    __name__ = "FakeModel"


class TestORMExceptionBase:
    def test_default_message(self):
        e = ORMException()
        assert e.message == "An error occurred in the ORM"

    def test_custom_message(self):
        e = ORMException(message="oops")
        assert e.message == "oops"

    def test_model_name(self):
        e = ORMException(model=FakeModel)
        assert e.model == "FakeModel"

    def test_model_default(self):
        e = ORMException()
        assert e.model == "Unknown Model"

    def test_format_message_contains_model(self):
        e = ORMException(message="boom", model=FakeModel)
        formatted = e.format_message()
        assert "FakeModel" in formatted
        assert "boom" in formatted

    def test_format_message_with_class_method(self):
        e = ORMException(message="fail", class_name="Executor", method_name="run")
        formatted = e.format_message()
        assert "Executor.run()" in formatted

    def test_str_equals_format_message(self):
        e = ORMException(message="test")
        assert str(e) == e.format_message()


class TestEnrich:
    def test_enrich_sets_model(self):
        e = ORMException(message="err")
        e.enrich(model=FakeModel)
        assert e.model == "FakeModel"

    def test_enrich_sets_operation(self):
        e = ORMException(message="err")
        e.enrich(operation="create")
        assert e.method_name == "create"

    def test_enrich_sets_args(self):
        e = ORMException(message="err")
        e.enrich(args={"id": 1})
        assert e.details["args"] == {"id": 1}

    def test_enrich_extra_kwargs(self):
        e = ORMException(message="err")
        e.enrich(table="users")
        assert e.details["table"] == "users"

    def test_enrich_does_not_overwrite(self):
        e = ORMException(message="err", model=FakeModel)
        e.enrich(model=type("Other", (), {"__name__": "Other"}))
        assert e.model == "FakeModel"

    def test_enrich_returns_self(self):
        e = ORMException(message="err")
        assert e.enrich(model=FakeModel) is e


class TestSanitizeDetails:
    def test_nested_orm_exception_flattened(self):
        inner = ORMException(message="inner error")
        result = ORMException._sanitize_details({"cause": inner})
        assert result["cause"] == "inner error"

    def test_normal_values_passed_through(self):
        result = ORMException._sanitize_details({"key": "value"})
        assert result["key"] == "value"


class TestSubclasses:
    def test_validation_error(self):
        e = ValidationError(model=FakeModel, field="email", value="bad", reason="invalid format")
        assert "invalid format" in e.message
        assert e.details["field"] == "email"

    def test_validation_error_positional_message(self):
        """Regression: ValidationError("msg") must work — string was wrongly interpreted as model."""
        e = ValidationError("No data provided for insert")
        assert e.message == "No data provided for insert"
        assert e.model == "Unknown Model"

    def test_validation_error_with_details(self):
        """ValidationError supports details kwarg for extra context."""
        e = ValidationError(
            model=FakeModel,
            reason="Data must be a list of dictionaries",
            details={"provided_type": "str"},
        )
        assert "list of dictionaries" in e.message
        assert e.details["provided_type"] == "str"

    def test_does_not_exist(self):
        e = DoesNotExist(model=FakeModel, filters={"id": 1})
        assert "No FakeModel found" in e.message
        formatted = e.format_message()
        assert "NOTICE" in formatted

    def test_multiple_objects_returned(self):
        e = MultipleObjectsReturned(model=FakeModel, count=3, filters={"active": True})
        assert "Found 3" in e.message

    def test_connection_error(self):
        e = ConnectionError(model=FakeModel, db_url="localhost", original_error=Exception("refused"))
        assert "connect" in e.message.lower()

    def test_integrity_error(self):
        e = IntegrityError(model=FakeModel, constraint="unique_email", original_error=Exception("dup"))
        assert "integrity" in e.message.lower()

    def test_transaction_error(self):
        e = TransactionError(model=FakeModel, operation="commit", original_error=Exception("fail"))
        assert "Transaction" in e.message

    def test_configuration_error(self):
        e = ConfigurationError(config_key="host", reason="missing")
        assert "Configuration" in e.message

    def test_cache_error(self):
        e = CacheError(operation="get", original_error=Exception("timeout"))
        assert "Cache" in e.message

    def test_state_error(self):
        e = StateError(operation="register", reason="already exists")
        assert "State" in e.message
        assert "already exists" in e.message

    def test_relationship_error(self):
        e = RelationshipError(model=FakeModel, field="user_id", reason="not found")
        assert "Relationship" in e.message

    def test_adapter_error(self):
        e = AdapterError(adapter_name="pg", original_error=Exception("crash"))
        assert "pg adapter" in e.message

    def test_field_error(self):
        e = FieldError(field="email", reason="too long")
        assert "Field error" in e.message

    def test_migration_error(self):
        e = MigrationError(migration="0001_init", original_error=Exception("bad SQL"))
        assert "Migration" in e.message

    def test_parameter_error(self):
        e = ParameterError(query="SELECT *", args=[1], reason="type mismatch")
        assert "Invalid query parameter" in e.message

    def test_unknown_database_error(self):
        e = UnknownDatabaseError(operation="insert", original_error=Exception("unknown"))
        assert "Unexpected database error" in e.message


class TestInheritance:
    def test_query_error_is_orm_exception(self):
        assert issubclass(QueryError, ORMException)

    def test_does_not_exist_is_query_error(self):
        assert issubclass(DoesNotExist, QueryError)

    def test_database_error_is_orm_exception(self):
        assert issubclass(DatabaseError, ORMException)

    def test_connection_error_is_database_error(self):
        assert issubclass(ConnectionError, DatabaseError)

    def test_all_subclasses_are_orm_exception(self):
        for cls in [
            ValidationError, QueryError, DoesNotExist, MultipleObjectsReturned,
            DatabaseError, ConnectionError, IntegrityError, TransactionError,
            ConfigurationError, CacheError, StateError, RelationshipError,
            AdapterError, FieldError, MigrationError, ParameterError,
            UnknownDatabaseError,
        ]:
            assert issubclass(cls, ORMException), f"{cls.__name__} not subclass of ORMException"
