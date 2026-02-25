# matrx-orm Typing & Quality Tasks

## Done (this session)
- Added `TYPE_CHECKING`-guarded `__get__` overloads to all major field classes so that
  accessing a field on a model instance returns the correct Python type to static
  analysers (pyright, mypy) without any runtime behaviour change:
  - `Field` → `Any`
  - `CharField`, `TextField` → `str | None`
  - `UUIDField` → `str | None`
  - `IntegerField`, `BigIntegerField`, `SmallIntegerField` → `int | None`
  - `FloatField` → `float | None`
  - `BooleanField` → `bool | None`
  - `DateTimeField` → `datetime | None`
  - `DateField` → `date | None`
  - `TimeField` → `time | None`
  - `JSONBField`, `JSONField` → `dict[str, Any] | list[Any] | None`
  - `HStoreField` → `dict[str, str | None] | None`
  - `DecimalField` → `Decimal | None`
  - `BinaryField` → `bytes | None`
  - `TimeDeltaField` → `timedelta | None`
  - `ArrayField` → `list[Any] | None`

---

## High Priority

### 1. Generic field types for precise return typing
Currently `JSONBField` always returns `dict[str, Any] | list[Any] | None`. In practice
a JSONB column that always holds a dict should tell pyright it returns `dict[str, Any]`.
Solution: make the field generic.

```python
class JSONBField(Field, Generic[T]):
    if TYPE_CHECKING:
        @overload
        def __get__(self, obj: None, objtype: type = ...) -> "JSONBField[T]": ...
        @overload
        def __get__(self, obj: object, objtype: type = ...) -> T | None: ...
```

Usage in models:
```python
settings: JSONBField[dict[str, Any]] = JSONBField()
variable_defaults: JSONBField[list[Any]] = JSONBField()
```

### 2. Non-nullable field variants
Fields declared with `null=False` should return `T`, not `T | None`.
This requires either:
  - A `required=True` flag that changes the `__get__` return type via overloads, or
  - Separate `Required`/`Optional` field subclasses, or
  - Generic nullable parameter: `CharField[str, Literal[False]]`

### 3. `__set__` type stubs
Without `__set__` annotations, pyright allows assigning anything to a field. Add stubs:

```python
    if TYPE_CHECKING:
        def __set__(self, obj: object, value: str | None) -> None: ...
```

This enables type-safe assignment: `model.name = 123` would be flagged.

### 4. `py.typed` marker file
Add an empty `py.typed` file to `src/matrx_orm/` so that downstream packages
(e.g. matrx-ai) know this package ships inline types per PEP 561.

---

## Medium Priority

### 5. Model `__init__` signature
The generated `Model.__init__` currently accepts `**kwargs: Any`. Typed `__init__`s
could be generated from field definitions so that:
```python
Prompts(name="foo", settings={})   # OK
Prompts(name=123)                  # Error: name must be str
```
This likely requires a metaclass change or a code-generation step.

### 6. `ArrayField` generic item type
`ArrayField` wraps a `Field` instance but returns `list[Any]`. Make it generic:
```python
class ArrayField(Field, Generic[T]):
    def __get__(self, obj: object, ...) -> list[T] | None: ...
```

### 7. `EnumField` typed returns
`EnumField` can hold either a `PythonEnum` instance or a plain `str`. With generics:
```python
class EnumField(Field, Generic[E]):
    def __get__(self, obj: object, ...) -> E | None: ...
```

### 8. ForeignKey typed returns
`ForeignKey` fields should return the related model type, not `Any`.
```python
class ForeignKey(Field, Generic[M]):
    def __get__(self, obj: object, ...) -> M | None: ...
```

### 9. `to_python` / `get_db_prep_value` return type annotations
All field methods currently lack return type hints. Adding them would catch bugs
in custom subclasses and make the ORM's own internals safer.

---

## Lower Priority

### 10. `.pyi` stub generation
Consider generating `.pyi` stub files for the generated model classes in consuming
projects (e.g. `db/models.py` in matrx-ai). This would give the strongest typing
without requiring any runtime changes.

### 11. Model metaclass `__class_getitem__` support
Allow `Model[Prompts]` style typing patterns for generic manager/queryset APIs.

### 12. `BaseManager` / `BaseDTO` typed return stubs
The manager's query methods (`filter`, `get`, `all`, etc.) return `Any`. With generics
these can be typed: `manager.filter(...) -> list[M]` where `M` is the model type.

### 13. Remove `UUIDFieldREAL` duplication
`UUIDField` and `UUIDFieldREAL` are near-identical. Consolidate into one.

### 14. `JSONBField` vs `JSONField` duplication
Both map to JSONB in the database. Consolidate or clearly document the distinction.

### 15. `validate()` should be synchronous for simple fields
Most fields do synchronous work inside `async def validate()`. This forces callers
to `await` even for trivial CPU-only validation. Consider a sync `validate_sync()`
alternative or restructuring.
