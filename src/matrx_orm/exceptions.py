import traceback as _tb

from matrx_utils import vcprint

_RED = "\033[91m"
_RESET = "\033[0m"

_ORM_PACKAGE = "matrx_orm"


def _capture_caller_frames() -> list[str]:
    """Walk the stack to find frames outside the matrx_orm package.

    Returns the most recent external caller and a compact chain of up to 3
    frames showing how the user's code reached the ORM, formatted like:

        File "/home/user/app/views.py", line 42, in handle_request
        File "/home/user/app/db/persistence.py", line 204, in persist

    Returns an empty list when no external caller is found.
    """
    frames: list[str] = []
    for fi in reversed(_tb.extract_stack()[:-1]):
        if _ORM_PACKAGE in fi.filename:
            continue
        frames.append(f'  File "{fi.filename}", line {fi.lineno}, in {fi.name}')
        if len(frames) >= 3:
            break
    frames.reverse()
    return frames


class ORMException(Exception):
    """Base exception class for all ORM-related errors."""

    def __init__(
        self, message=None, model=None, details=None, class_name=None, method_name=None
    ):
        self.model = (
            model.__name__
            if hasattr(model, "__name__")
            else str(model)
            if model
            else "Unknown Model"
        )
        self.details = self._sanitize_details(details or {})
        self._message = message
        self.class_name = class_name
        self.method_name = method_name
        self._enriched = False
        self._caller_frames = _capture_caller_frames()
        super().__init__(self.format_message())

    def _format_caller_section(self) -> str | None:
        """Return a 'Your code:' block if external caller frames were captured."""
        if not self._caller_frames:
            return None
        lines = ["Your code (most recent call last):"]
        lines.extend(self._caller_frames)
        return "\n".join(lines)

    def enrich(self, model=None, operation=None, args=None, **extra):
        """Stamp context onto this exception as it bubbles up through layers.

        Each layer that catches an ORMException should call enrich() with
        whatever it knows, then re-raise — never wrap in a new exception.
        Only the first enrichment for each field wins (closest to the error).
        """
        if model and self.model == "Unknown Model":
            self.model = model.__name__ if hasattr(model, "__name__") else str(model)
        if operation and not self.method_name:
            self.method_name = operation
        if args is not None and "args" not in self.details:
            self.details["args"] = args
        for key, value in extra.items():
            if key not in self.details:
                self.details[key] = value
        self._enriched = True
        super().__init__(self.format_message())
        return self

    @staticmethod
    def _sanitize_details(details):
        """Prevent nested ORMException str() output from ballooning error messages."""
        sanitized = {}
        _sep_80 = "-" * 80
        _eq_80 = "=" * 80
        for key, value in details.items():
            if isinstance(value, ORMException):
                sanitized[key] = value.message
            elif isinstance(value, str) and (_sep_80 in value or _eq_80 in value):
                sanitized[key] = "(see chained exception below)"
            else:
                sanitized[key] = value
        return sanitized

    @property
    def message(self):
        """Return the base error message"""
        return self._message or "An error occurred in the ORM"

    def format_message(self):
        """Format the complete error message with all details"""
        error_msg = ["\n" + "=" * 80 + "\n"]

        if self.class_name and self.method_name:
            error_msg.append(
                f"[ERROR in {self.model}: {self.class_name}.{self.method_name}()]\n"
            )
        else:
            error_msg.append(f"[ERROR in {self.model}]\n")

        error_msg.append(f"Message: {self.message}")

        if self.details:
            error_msg.append("\nContext:")
            for key, value in self.details.items():
                if key == "traceback":
                    continue
                str_val = str(value)
                if len(str_val) > 300:
                    str_val = str_val[:300] + "..."
                error_msg.append(f"  {key}: {str_val}")

        error_msg.append("\n" + "=" * 80 + "\n")

        return "\n".join(error_msg)

    def __str__(self):
        msg = self.format_message()
        caller_section = self._format_caller_section()
        if not caller_section:
            return msg
        # Inject caller section before the closing separator line
        # Subclass format_message outputs end with "-" * 80 or "=" * 80
        for sep in ("-" * 80, "=" * 80):
            last_sep_idx = msg.rfind(sep)
            if last_sep_idx > 0:
                return msg[:last_sep_idx] + caller_section + "\n" + msg[last_sep_idx:]
        return msg + "\n" + caller_section


class ValidationError(ORMException):
    """Raised when data validation fails.

    Supports multiple call patterns:
        ValidationError("No data provided for insert")
        ValidationError(reason="...", model=MyModel)
        ValidationError(model=MyModel, reason="...", details={"invalid_fields": [...]})
    """

    def __init__(
        self,
        message=None,
        model=None,
        field=None,
        value=None,
        reason=None,
        details=None,
    ):
        # Support ValidationError("msg") — first positional string is the message
        if message is None and reason:
            message = reason
        elif message is None:
            message = f"Validation failed for {field if field else 'model'}"

        merged_details = {"field": field, "value": value, "reason": reason}
        if details:
            merged_details.update(details)
        super().__init__(message=message, model=model, details=merged_details)

    def format_message(self):
        reason = self.details.get("reason")
        field = self.details.get("field")
        value = self.details.get("value")
        lines = ["\n" + "-" * 80]
        lines.append("Matrx ORM  |  ValidationError")
        lines.append("")
        lines.append(self.message)
        if reason:
            lines.append(f"  Reason:  {reason}")
        if field and field != "multiple":
            lines.append(f"  Field:   {field}")
        if value is not None:
            lines.append(f"  Value:   {value}")
        lines.append("")
        lines.append("Hint:")
        # Contextual hints based on the reason string
        if reason and "no update data" in reason.lower():
            lines.append(
                "  - You called update() or save() without passing any fields to change."
            )
            lines.append(
                "  - Ensure you are passing at least one keyword argument, e.g. update(status='active')."
            )
        elif reason and "invalid field" in reason.lower():
            lines.append(
                "  - One or more field names you passed do not exist on this model."
            )
            lines.append(
                "  - Check the model definition for the exact field names (case-sensitive)."
            )
            lines.append(
                "  - Fields marked is_native=False (computed/virtual) cannot be updated directly."
            )
        elif reason and "no lookup criteria" in reason.lower():
            lines.append(
                "  - You called get() or a cache lookup without any filter arguments."
            )
            lines.append("  - Pass at least one field to match on, e.g. get(id='...').")
        elif reason and "no data provided" in reason.lower():
            lines.append("  - You called create() or insert() with an empty data dict.")
            lines.append(
                "  - Ensure the object has at least the required fields set before saving."
            )
        elif reason and "cannot cache none" in reason.lower():
            lines.append(
                "  - The record returned from the database was None and cannot be cached."
            )
            lines.append(
                "  - Check that your query actually returns a record before caching it."
            )
        else:
            lines.append(
                "  - Verify the field name exists on the model and the value is the correct type."
            )
            lines.append(
                "  - Check that required fields are populated before calling save() or create()."
            )
        lines.append("-" * 80 + "\n")
        body = "\n".join(lines)
        return f"{_RED}{body}{_RESET}"


class QueryError(ORMException):
    """Base class for query-related errors."""

    def format_message(self):
        error = self.details.get("error", "")
        query = self.details.get("query", "")
        operation = self.details.get("operation", "")
        missing_keys = self.details.get("missing_keys", [])
        lines = ["\n" + "-" * 80]
        lines.append("Matrx ORM  |  QueryError")
        lines.append("")
        lines.append(self.message)
        if operation:
            lines.append(f"  Operation: {operation}")
        if missing_keys:
            lines.append(f"  Missing:   {missing_keys}")
        if error:
            lines.append(f"  Detail:    {error}")
            vcprint(error, "Error", color="red")
        if query:
            short_query = str(query)[:300] + ("..." if len(str(query)) > 300 else "")
            lines.append(f"  Query:     {short_query}")
        lines.append("")
        lines.append("Hint:")
        if missing_keys:
            lines.append(
                "  - QueryExecutor requires a properly constructed query dict."
            )
            lines.append(
                "  - Do not instantiate QueryExecutor directly. Use QueryBuilder,"
            )
            lines.append(
                "    which calls QueryBuilder._build_query() to produce the correct dict."
            )
        elif "syntax" in str(error).lower() or "syntax" in self.message.lower():
            lines.append(
                "  - The SQL generated by the ORM was rejected by PostgreSQL for invalid syntax."
            )
            lines.append(
                "  - This is likely an ORM bug. Please report the Query above."
            )
        else:
            lines.append(
                "  - An error occurred while executing a query that was not caught by a"
            )
            lines.append("    more specific exception handler.")
            lines.append("  - Check the Detail and Query above for the root cause.")
        lines.append("-" * 80 + "\n")
        body = "\n".join(lines)
        return f"{_RED}{body}{_RESET}"


class DoesNotExist(QueryError):
    """Raised when a queried object does not exist."""

    def __init__(self, model=None, filters=None, class_name=None, method_name=None):
        details = {"filters": filters or {}}
        filter_str = ", ".join(f"{k}={v}" for k, v in details["filters"].items())
        message = (
            f"No {model.__name__ if model else 'object'} found matching: {filter_str}"
        )
        super().__init__(
            message=message,
            model=model,
            details=details,
            class_name=class_name,
            method_name=method_name,
        )

    def format_message(self):
        lines = ["\n" + "-" * 80]
        lines.append("Matrx ORM  |  DoesNotExist")
        lines.append("")
        lines.append("NOTICE: Requested item not found")
        lines.append("")
        lines.append(self.message)
        if self.details.get("filters"):
            lines.append("")
            lines.append("Search criteria:")
            for k, v in self.details["filters"].items():
                lines.append(f"  {k}: {v}")
        lines.append("")
        lines.append("Hint:")
        lines.append(
            "  - Use get() when the record is expected to exist — this error is intentional."
        )
        lines.append(
            "  - Use get_or_none() when a missing record is a valid, handled outcome."
        )
        lines.append(
            "  - Use filter(...).first() to get the first match or None without raising."
        )
        lines.append("")
        lines.append(
            "This is not an ORM bug. The record does not exist in the database."
        )
        lines.append("-" * 80 + "\n")
        body = "\n".join(lines)
        return f"{_RED}{body}{_RESET}"


class MultipleObjectsReturned(QueryError):
    """Raised when a query returns multiple objects but one was expected."""

    def __init__(self, model=None, count=None, filters=None):
        details = {"count": count, "filters": filters or {}}
        filter_str = ", ".join(f"{k}={v}" for k, v in details["filters"].items())
        message = f"Found {count} objects when expecting one. Filters: {filter_str}"
        super().__init__(message=message, model=model, details=details)

    def format_message(self):
        count = self.details.get("count", "?")
        lines = ["\n" + "-" * 80]
        lines.append("Matrx ORM  |  MultipleObjectsReturned")
        lines.append("")
        lines.append(
            f"ERROR: get() returned {count} records — exactly one was expected"
        )
        lines.append("")
        lines.append(self.message)
        if self.details.get("filters"):
            lines.append("")
            lines.append("Search criteria:")
            for k, v in self.details["filters"].items():
                lines.append(f"  {k}: {v}")
        lines.append("")
        lines.append("Hint:")
        lines.append("  - Your filter criteria matched more than one row.")
        lines.append("  - Use filter(...).all() if multiple results are valid.")
        lines.append("  - Use filter(...).first() to silently take the first match.")
        lines.append(
            "  - Narrow your filter (e.g. add unique fields like id or email)."
        )
        lines.append("-" * 80 + "\n")
        body = "\n".join(lines)
        return f"{_RED}{body}{_RESET}"


class DatabaseError(ORMException):
    """Base class for database-related errors."""

    pass


class ConnectionError(DatabaseError):
    """Raised when database connection fails."""

    def __init__(self, model=None, db_url=None, original_error=None):
        details = {"db_url": db_url, "original_error": str(original_error)}
        message = f"Failed to connect to database: {original_error}"
        super().__init__(message=message, model=model, details=details)

    def format_message(self):
        db_url = self.details.get("db_url", "")
        original = self.details.get("original_error", "")
        lines = ["\n" + "-" * 80]
        lines.append("Matrx ORM  |  ConnectionError")
        lines.append("")
        lines.append(self.message)
        if db_url:
            lines.append(f"  Target:   {db_url}")
        if original:
            lines.append(f"  DB error: {original}")
        lines.append("")
        lines.append("Hint:")
        lines.append("  - asyncpg could not establish a connection to the database.")
        lines.append("  - This is raised in two cases:")
        lines.append(
            "      1. Connection pool creation failed (wrong host/port/credentials)."
        )
        lines.append(
            "      2. A live connection was lost mid-operation (ConnectionDoesNotExistError)."
        )
        lines.append(
            "  - Verify the host, port, database_name, user, and password in your"
        )
        lines.append("    DatabaseProjectConfig registration.")
        lines.append(
            "  - Check that the database server is reachable from this environment."
        )
        lines.append(
            "  - SSL is required — ensure the database accepts SSL connections."
        )
        lines.append("-" * 80 + "\n")
        body = "\n".join(lines)
        return f"{_RED}{body}{_RESET}"


class IntegrityError(DatabaseError):
    """Raised for database integrity violations."""

    def __init__(self, model=None, constraint=None, original_error=None):
        details = {"constraint": constraint, "original_error": str(original_error)}
        message = f"Database integrity error: {original_error}"
        super().__init__(message=message, model=model, details=details)

    def format_message(self):
        constraint = self.details.get("constraint", "unknown")
        original = self.details.get("original_error", "")
        lines = ["\n" + "-" * 80]
        lines.append("Matrx ORM  |  IntegrityError")
        lines.append("")
        lines.append(self.message)
        if constraint and constraint != "unknown":
            lines.append(f"  Constraint: {constraint}")
        if original:
            lines.append(f"  DB error:   {original}")
        lines.append("")
        lines.append("Hint:")
        if constraint == "unique":
            lines.append(
                "  - A record with these values already exists in the database."
            )
            lines.append(
                "  - Use get_or_none() to check before inserting, or update the existing record."
            )
            lines.append(
                "  - If this is expected (e.g. race condition), wrap the call in a try/except IntegrityError."
            )
        elif constraint == "foreign_key":
            lines.append(
                "  - The referenced record does not exist in the related table."
            )
            lines.append("  - Ensure the parent record is created before the child.")
            lines.append(
                "  - Verify the foreign key ID is valid and the related model is saved."
            )
        else:
            lines.append(
                "  - The database rejected the write due to a constraint violation."
            )
            lines.append(
                "  - Check for unique constraints, foreign key references, or NOT NULL fields."
            )
            lines.append(
                "  - Review the DB error above for the specific constraint name."
            )
        lines.append("-" * 80 + "\n")
        body = "\n".join(lines)
        return f"{_RED}{body}{_RESET}"


class TransactionError(DatabaseError):
    """Raised when a database transaction fails."""

    def __init__(self, model=None, operation=None, original_error=None):
        details = {"operation": operation, "original_error": str(original_error)}
        message = f"Transaction failed during {operation}: {original_error}"
        super().__init__(message=message, model=model, details=details)


class ConfigurationError(ORMException):
    """Raised when there's an error in ORM configuration."""

    def __init__(self, model=None, config_key=None, reason=None):
        details = {"config_key": config_key, "reason": reason}
        message = f"Configuration error for {config_key}: {reason}"
        super().__init__(message=message, model=model, details=details)

    def format_message(self):
        config_key = self.details.get("config_key", "")
        reason = self.details.get("reason", "")
        lines = ["\n" + "-" * 80]
        lines.append("Matrx ORM  |  ConfigurationError")
        lines.append("")
        lines.append(self.message)
        if config_key:
            lines.append(f"  Config key: {config_key}")
        if reason:
            lines.append(f"  Reason:     {reason}")
        lines.append("")
        lines.append("Hint:")
        if config_key in ("model_state", "state_registration"):
            lines.append("  - The model failed to initialize with the StateManager.")
            lines.append(
                "  - Ensure the model is registered via model_registry before making queries."
            )
            lines.append(
                "  - Check that the model class defines _meta, _database, and primary_keys."
            )
        else:
            lines.append(
                "  - A database configuration was referenced that has not been registered."
            )
            lines.append(
                "  - Call register_database(DatabaseProjectConfig(...)) at startup before"
            )
            lines.append("    any model queries run.")
            lines.append(
                "  - Verify the config_key matches exactly what was passed to register_database()."
            )
            lines.append(
                "  - Check that all required env vars (host, port, user, password, database_name)"
            )
            lines.append("    are set and non-empty.")
        lines.append("-" * 80 + "\n")
        body = "\n".join(lines)
        return f"{_RED}{body}{_RESET}"


class CacheError(ORMException):
    """Raised when there's an error related to caching."""

    def __init__(self, model=None, operation=None, details=None, original_error=None):
        if original_error:
            details = details or {}
            details["original_error"] = str(original_error)
        message = f"Cache operation '{operation}' failed"
        super().__init__(message=message, model=model, details=details)

    def format_message(self):
        operation = self.details.get("operation") or ""
        original = self.details.get("original_error", "")
        lines = ["\n" + "-" * 80]
        lines.append("Matrx ORM  |  CacheError")
        lines.append("")
        lines.append(self.message)
        if original:
            lines.append(f"  Cause:     {original}")
        lines.append("")
        lines.append("Hint:")
        if operation in ("get_cache_key", "find_in_cache", "check_staleness"):
            lines.append("  - An error occurred inside the in-memory cache lookup.")
            lines.append(
                "  - This is typically caused by a model missing primary_keys in _meta,"
            )
            lines.append(
                "    or a cached record that doesn't have the expected attributes."
            )
        elif operation == "create_lock":
            lines.append(
                "  - asyncio.Lock() creation failed, which should not normally happen."
            )
            lines.append("  - This may indicate an issue with the event loop state.")
        elif operation == "database_fetch":
            lines.append(
                "  - The cache miss triggered a database fetch, which then raised an"
            )
            lines.append(
                "    unexpected error (not a DoesNotExist — that is handled separately)."
            )
            lines.append("  - Check the Cause above for the underlying database error.")
        else:
            lines.append("  - An unexpected error occurred in the cache layer.")
            lines.append(
                "  - CacheErrors do not indicate a data loss problem — the cache is"
            )
            lines.append(
                "    a read-through layer; the database is always the source of truth."
            )
        lines.append("-" * 80 + "\n")
        body = "\n".join(lines)
        return f"{_RED}{body}{_RESET}"


class StateError(ORMException):
    """Raised when there's an error in state management."""

    def __init__(
        self, model=None, operation=None, reason=None, details=None, original_error=None
    ):
        details = details or {}
        if reason:
            details["reason"] = reason
        if original_error:
            details["original_error"] = str(original_error)
        message = f"State operation '{operation}' failed"
        if reason:
            message += f": {reason}"
        super().__init__(message=message, model=model, details=details)

    def format_message(self):
        reason = self.details.get("reason", "")
        original = self.details.get("original_error", "")
        lines = ["\n" + "-" * 80]
        lines.append("Matrx ORM  |  StateError")
        lines.append("")
        lines.append(self.message)
        if reason:
            lines.append(f"  Reason:   {reason}")
        if original:
            lines.append(f"  Cause:    {original}")
        lines.append("")
        lines.append("Hint:")
        if reason and "not registered" in reason.lower():
            lines.append("  - The model has not been registered with the StateManager.")
            lines.append(
                "  - This usually means the model file was not imported before queries ran."
            )
            lines.append(
                "  - Ensure all models are imported in your startup/init sequence so"
            )
            lines.append(
                "    their metaclass registration runs before any query is attempted."
            )
        elif "acquire_connection" in self.message or "pool" in reason.lower():
            lines.append(
                "  - The asyncpg connection pool encountered an interface error."
            )
            lines.append(
                "  - This can happen if you acquire a connection outside an async context,"
            )
            lines.append("    or if the pool was closed and not yet recreated.")
            lines.append(
                "  - The pool auto-recreates when the event loop changes (e.g. asyncio.run())."
            )
        elif "cleanup" in self.message or "close" in reason.lower():
            lines.append(
                "  - A connection pool failed to close cleanly during shutdown."
            )
            lines.append("  - This is usually safe to ignore during process exit.")
            lines.append(
                "  - If it happens during tests, ensure each test cleans up with AsyncDatabaseManager.cleanup()."
            )
        else:
            lines.append(
                "  - An unexpected error occurred in the ORM state/cache layer."
            )
            lines.append("  - Check the Cause above for the underlying exception.")
        lines.append("-" * 80 + "\n")
        body = "\n".join(lines)
        return f"{_RED}{body}{_RESET}"


class RelationshipError(ORMException):
    """Raised when there's an error in model relationships."""

    def __init__(self, model=None, related_model=None, field=None, reason=None):
        details = {
            "related_model": related_model.__name__ if related_model else None,
            "field": field,
            "reason": reason,
        }
        message = f"Relationship error: {reason}"
        super().__init__(message=message, model=model, details=details)


class AdapterError(ORMException):
    """Raised when there's an error specific to a database adapter."""

    def __init__(self, model=None, adapter_name=None, original_error=None):
        details = {"adapter": adapter_name, "original_error": str(original_error)}
        message = f"Error in {adapter_name} adapter: {original_error}"
        super().__init__(message=message, model=model, details=details)


class FieldError(ORMException):
    """Raised when there's an error related to model fields."""

    def __init__(self, model=None, field=None, value=None, reason=None):
        details = {"field": field, "value": value, "reason": reason}
        message = f"Field error for {field}: {reason}"
        super().__init__(message=message, model=model, details=details)


class MigrationError(ORMException):
    """Raised when there's an error during database migration."""

    def __init__(self, model=None, migration=None, original_error=None):
        details = {"migration": migration, "original_error": str(original_error)}
        message = f"Migration '{migration}' failed: {original_error}"
        super().__init__(message=message, model=model, details=details)

    def format_message(self):
        migration = self.details.get("migration", "")
        original = str(self.details.get("original_error", ""))
        lines = ["\n" + "-" * 80]
        lines.append("Matrx ORM  |  MigrationError")
        lines.append("")
        lines.append(self.message)
        if migration:
            lines.append(f"  Migration: {migration}")
        if original:
            lines.append(f"  Detail:    {original}")
            vcprint(original, "Error", color="red")
        lines.append("")
        lines.append("Hint:")
        if "modified after being applied" in original or "checksum" in original.lower():
            lines.append(
                "  - A migration file was edited after it was already applied to the database."
            )
            lines.append(
                "  - NEVER edit applied migration files. The checksums are stored in the"
            )
            lines.append("    matrx_migrations table and will no longer match.")
            lines.append("  - Create a new migration file to make further changes.")
        elif "missing an 'up' function" in original:
            lines.append("  - The migration file does not define an 'up' coroutine.")
            lines.append("  - Every migration file must define:  async def up(db): ...")
            lines.append(
                "  - Optionally define:                 async def down(db): ..."
            )
        elif "no 'down' function" in original:
            lines.append(
                "  - You tried to roll back a migration that has no 'down' function."
            )
            lines.append(
                "  - Add  async def down(db): ...  to the migration file to enable rollback."
            )
        elif "not found on disk" in original:
            lines.append(
                "  - A migration recorded in the database no longer exists as a file."
            )
            lines.append(
                "  - Restore the deleted migration file before attempting rollback."
            )
        elif "circular dependency" in original.lower():
            lines.append(
                "  - Two or more migrations declare each other as dependencies."
            )
            lines.append(
                "  - Review the 'dependencies' lists in those migration files and break the cycle."
            )
        elif "dependency" in original.lower() and "not found" in original.lower():
            lines.append(
                "  - A migration declares a dependency on a migration file that doesn't exist."
            )
            lines.append(
                "  - Check the 'dependencies' list in the failing migration file."
            )
            lines.append(
                "  - Ensure the dependency name exactly matches the filename stem (without .py)."
            )
        elif "could not load" in original.lower():
            lines.append("  - Python could not import the migration file as a module.")
            lines.append(
                "  - Check for syntax errors or invalid imports in that migration file."
            )
        else:
            lines.append(
                "  - The migration SQL itself raised an error when executed against the database."
            )
            lines.append(
                "  - The database was not modified (each migration runs in a transaction)."
            )
            lines.append(
                "  - Fix the SQL in the migration's 'up' function and re-run migrate."
            )
        lines.append("-" * 80 + "\n")
        body = "\n".join(lines)
        return f"{_RED}{body}{_RESET}"


class ParameterError(ORMException):
    """Raised when query parameters are invalid or malformed."""

    def __init__(
        self,
        model=None,
        query=None,
        args=None,
        reason=None,
        class_name=None,
        method_name=None,
    ):
        details = {
            "query": query,
            "args": args if args is not None else [],
            "reason": reason,
        }
        message = f"Invalid query parameter: {reason}"
        super().__init__(
            message=message,
            model=model,
            details=details,
            class_name=class_name,
            method_name=method_name,
        )

    def format_message(self):
        reason = self.details.get("reason", "")
        query = self.details.get("query", "")
        args = self.details.get("args", [])
        lines = ["\n" + "-" * 80]
        lines.append("Matrx ORM  |  ParameterError")
        lines.append("")
        lines.append(self.message)
        if reason:
            lines.append(f"  Reason: {reason}")
        if query:
            short_query = str(query)[:200] + ("..." if len(str(query)) > 200 else "")
            lines.append(f"  Query:  {short_query}")
        if args:
            lines.append(f"  Args:   {args}")
        lines.append("")
        lines.append("Hint:")
        lines.append(
            "  - asyncpg raised a DataError, meaning a bound parameter value is the wrong type"
        )
        lines.append("    or is out of range for the column's PostgreSQL type.")
        lines.append("  - Common causes:")
        lines.append("      - Passing a string where a UUID or integer is expected.")
        lines.append("      - Passing None for a NOT NULL column.")
        lines.append(
            "      - Passing a Python list where a scalar is expected (use field__in=... instead)."
        )
        lines.append(
            "  - Check the Args above and verify each value matches the column's type."
        )
        lines.append("-" * 80 + "\n")
        body = "\n".join(lines)
        return f"{_RED}{body}{_RESET}"


class UnknownDatabaseError(ORMException):
    """Raised when an unexpected database error occurs, capturing full context."""

    def __init__(
        self,
        model=None,
        operation=None,
        query=None,
        args=None,
        traceback=None,
        original_error=None,
    ):
        details = {
            "operation": operation,
            "query": query,
            "args": args if args is not None else [],
            "traceback": traceback,
            "original_error": str(original_error) if original_error else "Unknown",
        }
        message = f"Unexpected database error during {operation}: {str(original_error)}"
        super().__init__(message=message, model=model, details=details)

    def format_message(self):
        operation = self.details.get("operation", "")
        original = self.details.get("original_error", "")
        query = self.details.get("query", "")
        args = self.details.get("args", [])
        lines = ["\n" + "-" * 80]
        lines.append("Matrx ORM  |  UnknownDatabaseError")
        lines.append("")
        lines.append(self.message)
        if operation:
            lines.append(f"  Operation: {operation}")
        if original:
            lines.append(f"  DB error:  {original}")
        if query:
            short_query = str(query)[:300] + ("..." if len(str(query)) > 300 else "")
            lines.append(f"  Query:     {short_query}")
        if args:
            lines.append(f"  Args:      {args}")
        lines.append("")
        lines.append("Hint:")
        lines.append(
            "  - This is the catch-all for any asyncpg exception not handled by a more"
        )
        lines.append(
            "    specific error class (not a syntax error, unique violation, data error,"
        )
        lines.append("    or connection failure).")
        lines.append(
            "  - The full Python traceback was captured at raise time — check your logs."
        )
        lines.append(
            "  - Common causes: permission denied, relation does not exist, column"
        )
        lines.append("    type mismatch, or a Postgres function raising an exception.")
        lines.append(
            "  - The Query and Args above are the exact SQL and parameters that failed."
        )
        lines.append("-" * 80 + "\n")
        body = "\n".join(lines)
        return f"{_RED}{body}{_RESET}"


class OptimisticLockError(ORMException):
    """Raised when an optimistic-lock version conflict is detected.

    This means another process has updated the row since it was last fetched.
    Re-fetch the record and retry the operation.
    """

    def __init__(
        self,
        model=None,
        pk=None,
        expected_version: int | None = None,
        message: str | None = None,
    ) -> None:
        msg = message or (
            f"Optimistic lock conflict on {getattr(model, '__name__', model)} "
            f"(pk={pk}, expected version={expected_version}). "
            "The record was modified by another process — re-fetch and retry."
        )
        super().__init__(
            message=msg,
            model=model,
            details={"pk": pk, "expected_version": expected_version},
        )
