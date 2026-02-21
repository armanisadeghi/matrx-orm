"""Table filter for selective migrations — include-only or exclude lists.

Use :class:`TableFilter` to control which tables participate in a ``makemigrations``
diff.  Pass a filter instance to :func:`makemigrations` or directly to
:class:`~matrx_orm.migrations.diff.SchemaDiff`.

Examples::

    from matrx_orm.migrations import TableFilter, makemigrations

    # Include-only: only diff these three tables.
    await makemigrations("mydb", include_tables={"user", "post", "comment"})

    # Exclude: diff everything except these two tables.
    await makemigrations("mydb", exclude_tables={"legacy_audit", "scratch_pad"})

    # Build a filter object manually and reuse it.
    f = TableFilter(include={"user", "post"})
    assert f.is_included("user")     # True
    assert f.is_included("order")    # False
"""

from __future__ import annotations

import warnings
from dataclasses import dataclass

from matrx_orm.exceptions import MigrationError


@dataclass
class TableFilter:
    """Controls which tables participate in a migration diff.

    Provide exactly one of ``include`` or ``exclude`` — not both.

    Parameters
    ----------
    include:
        If given, *only* these table names are diffed; all others are ignored.
    exclude:
        If given, these table names are skipped; everything else is diffed.

    Raises
    ------
    MigrationError
        If both ``include`` and ``exclude`` are supplied simultaneously.

    Examples
    --------
    Include-only::

        f = TableFilter(include={"user", "post", "comment"})

    Exclude::

        f = TableFilter(exclude={"legacy_table", "scratch_pad"})
    """

    include: set[str] | None = None
    exclude: set[str] | None = None

    def __post_init__(self) -> None:
        if self.include is not None and self.exclude is not None:
            raise MigrationError(
                original_error=(
                    "TableFilter accepts either 'include' or 'exclude', not both. "
                    "Use one list to allow specific tables, or one list to block them."
                )
            )
        if self.include is not None:
            self.include = set(self.include)
        if self.exclude is not None:
            self.exclude = set(self.exclude)

    def is_included(self, table_name: str) -> bool:
        """Return ``True`` if *table_name* should participate in the diff."""
        if self.include is not None:
            return table_name in self.include
        if self.exclude is not None:
            return table_name not in self.exclude
        return True

    def apply(self, tables: dict[str, object]) -> dict[str, object]:
        """Return a filtered copy of *tables*, keeping only included names."""
        return {name: state for name, state in tables.items() if self.is_included(name)}

    def warn_cross_references(self, included_tables: dict) -> None:
        """Emit warnings for FK columns that reference tables outside the scope.

        When a migration scope is narrowed via ``include`` or ``exclude``, foreign
        key columns on *included* tables may still reference tables that are not
        being managed.  This is not an error — the referenced table must already
        exist in the database — but it can cause confusion.

        A :class:`UserWarning` is emitted for every such cross-boundary reference
        so that developers notice the dependency.

        Parameters
        ----------
        included_tables:
            A ``dict[str, TableState]`` **after** filtering has been applied.
            Only tables that survived the filter should be passed here.
        """
        included_names = set(included_tables.keys())
        seen: set[tuple[str, str]] = set()

        for table_name, table_state in included_tables.items():
            for col_name, col_state in table_state.columns.items():
                ref_table = getattr(col_state, "fk_table", None)
                if ref_table and ref_table not in included_names:
                    key = (table_name, ref_table)
                    if key in seen:
                        continue
                    seen.add(key)
                    warnings.warn(
                        f"[matrx-orm] Cross-scope FK detected: "
                        f"'{table_name}.{col_name}' references '{ref_table}', "
                        f"which is outside the current migration scope. "
                        f"The FK constraint will be included in the generated SQL, "
                        f"but '{ref_table}' will not be created or managed by this "
                        f"migration set. Ensure it already exists in the target database.",
                        UserWarning,
                        stacklevel=4,
                    )
