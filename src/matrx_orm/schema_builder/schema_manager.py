from datetime import datetime
from matrx_utils import vcprint

from matrx_orm.schema_builder.common import DEBUG_CONFIG, OutputConfig, dt_utils
from matrx_orm.schema_builder.generator import get_relationship_data_model_types
from matrx_orm.python_sql.db_objects import get_db_objects
from matrx_orm.schema_builder.relationships import Relationship
from matrx_orm.schema_builder.schema import Schema
from matrx_orm.schema_builder.tables import Table
from matrx_orm.schema_builder.views import View


class SchemaManager:
    def __init__(
        self,
        database="postgres",
        schema="public",
        database_project=None,
        additional_schemas=None,
        output_config: OutputConfig = None,
        save_direct=False,
        include_tables=None,
        exclude_tables=None,
        manager_flags: dict | None = None,
    ):
        if additional_schemas is None:
            # Read from the registered database config if a project name is provided;
            # fall back to ["auth"] for backward compatibility when no project is set.
            if database_project:
                try:
                    from matrx_orm.core.config import get_database_config

                    cfg = get_database_config(database_project)
                    additional_schemas = cfg.get("additional_schemas", [])
                except Exception:
                    additional_schemas = ["auth"]
            else:
                additional_schemas = ["auth"]

        if include_tables is not None and exclude_tables is not None:
            raise ValueError(
                "SchemaManager accepts either 'include_tables' or 'exclude_tables', not both."
            )

        # Resolve output_config — explicit object wins; bare save_direct is the
        # legacy fallback so existing call sites don't break.
        if output_config is None:
            output_config = OutputConfig(save_direct=save_direct)
        self.output_config = output_config

        self.utils = dt_utils
        self.database = database
        self.schema = Schema(
            name=schema,
            database_project=database_project,
            output_config=output_config,
            manager_flags=manager_flags,
        )
        self.additional_schemas = additional_schemas
        self.database_project = database_project
        self.processed_objects = None
        self.full_relationships = None
        self.full_junction_analysis = None
        self.all_enum_base_types = None
        self.overview_analysis = None
        self.frontend_full_relationships = []
        self.initialized = False
        self.save_direct = output_config.save_direct
        self.verbose = DEBUG_CONFIG["verbose"]
        self.debug = DEBUG_CONFIG["debug"]
        self.info = DEBUG_CONFIG["info"]
        self._include_tables: set[str] | None = (
            set(include_tables) if include_tables is not None else None
        )
        self._exclude_tables: set[str] | None = (
            set(exclude_tables) if exclude_tables is not None else None
        )

        vcprint(self.schema, title=f"SCHEMA MANAGER] with schema", verbose=self.verbose, color="blue")
        vcprint(self.database_project, title=f"SCHEMA MANAGER] with database project", verbose=self.verbose, color="blue")
        vcprint(self.additional_schemas, title=f"SCHEMA MANAGER] with additional schemas", verbose=self.verbose, color="blue")

        # Propagate filter to the Schema so generate_models() can apply it at
        # write-time without touching any loading or relationship logic.
        self.schema._include_tables = self._include_tables
        self.schema._exclude_tables = self._exclude_tables

    def _is_table_included(self, table_name: str) -> bool:
        """Return True if *table_name* should be processed given the current filter."""
        if self._include_tables is not None:
            return table_name in self._include_tables
        if self._exclude_tables is not None:
            return table_name not in self._exclude_tables
        return True

    def initialize(self):
        """Orchestrates the initialization of the SchemaManager."""
        self.set_all_schema_data()
        self.load_objects()
        self.load_table_relationships()
        self.initialized = True
        self.analyze_schema()
        self.get_full_relationship_analysis()

    def execute_all_initit_level_1(self):
        pass

    def execute_all_initit_level_2(self):
        pass

    def execute_all_initit_level_3(self):
        pass

    def execute_all_initit_level_4(self):
        pass

    def execute_all_initit_level_5(self):
        pass

    def execute_all_initit_level_6(self):
        pass

    def set_all_schema_data(self):
        (
            self.processed_objects,
            self.full_relationships,
            self.full_junction_analysis,
            self.all_enum_base_types,
            self.overview_analysis,
        ) = get_db_objects(self.schema.name, self.database_project)

        # NOTE: no filtering here — all relationship/overview data loads in full so
        # that topological sort, FK resolution, and relationship analysis are always
        # correct.  The filter is applied in Schema.generate_models() just before
        # code is written.

        self.utils.set_and_update_ts_enum_list(self.all_enum_base_types)

        vcprint(
            self.full_relationships,
            title="Full relationships",
            pretty=True,
            verbose=self.verbose,
            color="yellow",
        )
        vcprint(
            self.processed_objects,
            title="Processed objects",
            pretty=True,
            verbose=self.verbose,
            color="green",
        )
        vcprint(
            self.overview_analysis,
            title="Relationship Overview analysis",
            pretty=True,
            verbose=self.verbose,
            color="green",
        )

    def load_objects(self):
        """Loads all database objects (tables and views) into the schema."""
        vcprint(
            f"Loaded {len(self.processed_objects)} objects from {self.database_project}.",
            verbose=self.verbose,
            color="blue",
        )

        for obj in self.processed_objects:
            if obj["type"] == "table":
                self.load_table(obj)
            elif obj["type"] == "view":
                self.load_view(obj)

        self.schema.add_all_table_instances()

        vcprint(
            f"Loaded {len(self.schema.tables)} tables.",
            verbose=self.verbose,
            color="blue",
        )
        vcprint(
            f"Loaded {len(self.schema.views)} views.",
            verbose=self.verbose,
            color="green",
        )

    def load_table(self, obj):
        table = Table(
            oid=obj["oid"],
            database_project=obj["database_project"],
            unique_table_id=obj["unique_table_id"],
            name=obj["name"],
            type_=obj["type"],
            schema=obj["schema"],
            database=obj["database"],
            owner=obj["owner"],
            size_bytes=obj["size_bytes"],
            index_size_bytes=obj["index_size_bytes"],
            rows=obj["rows"],
            last_vacuum=obj["last_vacuum"],
            last_analyze=obj["last_analyze"],
            description=obj["description"],
            estimated_row_count=obj["estimated_row_count"],
            total_bytes=obj["total_bytes"],
            has_primary_key=obj["has_primary_key"],
            index_count=obj["index_count"],
            table_columns=obj["table_columns"],
            junction_analysis_ts=obj["junction_analysis_ts"],
        )
        self.schema.add_table(table)

    def load_view(self, obj):
        view = View(
            oid=obj["oid"],
            name=obj["name"],
            # database_project=self.database_project,
            type_=obj["type"],
            schema=obj["schema"],
            database=obj["database"],
            owner=obj["owner"],
            size_bytes=obj["size_bytes"],
            description=obj["description"],
            view_definition=obj["view_definition"],
            column_data=obj["columns"],
        )
        self.schema.add_view(view)

    def load_table_relationships(self):
        """Loads relationship information for tables."""

        # Remove self-references from referenced_by
        for table_data in self.full_relationships:
            if table_data["referenced_by"] and table_data["referenced_by"] != "None":
                table_data["referenced_by"].pop(table_data["table_name"], None)

        for table_data in self.full_relationships:
            table_name = table_data["table_name"]
            table = self.schema.get_table(table_name)
            if table:
                # Process foreign keys
                if table_data["foreign_keys"] and table_data["foreign_keys"] != "None":
                    for target_table_name, fk_data in table_data[
                        "foreign_keys"
                    ].items():
                        target_table_instance = self.schema.get_table(target_table_name)
                        relationship = Relationship(
                            fk_data["constraint_name"],
                            fk_data["column"],
                            fk_data["foreign_column"],
                            target_table=target_table_instance,
                            source_table=table,
                        )
                        # Important: Use table_name as key to maintain backward compatibility
                        table.add_foreign_key(target_table_name, relationship)

                # Process referenced_by
                if (
                    table_data["referenced_by"]
                    and table_data["referenced_by"] != "None"
                ):
                    for source_table_name, ref_data in table_data[
                        "referenced_by"
                    ].items():
                        source_table_instance = self.schema.get_table(source_table_name)
                        relationship = Relationship(
                            ref_data["constraint_name"],
                            ref_data["column"],
                            ref_data["foreign_column"],
                            target_table=table,
                            source_table=source_table_instance,
                        )
                        # Important: Use table_name as key to maintain backward compatibility
                        table.add_referenced_by(source_table_name, relationship)

        # Detect many-to-many relationships
        self.detect_many_to_many_relationships()
        if self.verbose:
            vcprint(
                f"Loaded relationships for {len(self.full_relationships)} tables.",
                color="green",
            )

    def detect_many_to_many_relationships(self):
        """Detects and sets many-to-many relationships."""
        for table in self.schema.tables.values():
            if len(table.foreign_keys) == 2 and len(table.referenced_by) == 0:
                related_tables = list(table.foreign_keys.keys())
                for related_table_name in related_tables:
                    related_table = self.schema.get_table(related_table_name)
                    if related_table:
                        other_table = self.schema.get_table(
                            related_tables[1]
                            if related_tables[0] == related_table_name
                            else related_tables[0]
                        )
                        if other_table:
                            related_table.add_many_to_many(table, other_table)
                            table.add_many_to_many(table, other_table)

    def analyze_relationships(self):
        """Analyzes relationships in the schema."""
        analysis = {
            "tables_with_foreign_keys": sum(
                1 for table in self.schema.tables.values() if table.foreign_keys
            ),
            "tables_referenced_by_others": sum(
                1 for table in self.schema.tables.values() if table.referenced_by
            ),
            "many_to_many_relationships": sum(
                len(table.many_to_many) for table in self.schema.tables.values()
            )
            // 2,
            "most_referenced_tables": sorted(
                [
                    (table.name, len(table.referenced_by))
                    for table in self.schema.tables.values()
                ],
                key=lambda x: x[1],
                reverse=True,
            )[:5],
        }
        return analysis

    def get_table(self, table_name):
        """Returns a specific table."""
        return self.schema.get_table(table_name)

    def get_view(self, view_name):
        """Returns a specific view."""
        return self.schema.get_view(view_name)

    def get_column(self, table_name, column_name):
        """Returns a specific column."""
        table = self.get_table(table_name)
        if table:
            for column in table.columns:
                if column.name == column_name:
                    return column
        return None

    def get_related_tables(self, table_name):
        """Returns tables related to a specific table."""
        return self.schema.get_related_tables(table_name)

    def get_all_tables(self):
        """Returns all tables."""
        return list(self.schema.tables.values())

    def get_all_views(self):
        """Returns all views."""
        return list(self.schema.views.values())

    def analyze_schema(self):
        """Performs a comprehensive analysis of the schema."""
        table_fetch_strategy = {}  # A dictionary of fetch strategies with their corresponding tables
        primary_key_count = 0
        tables_with_fk = 0
        tables_with_ifk = 0
        tables_with_m2m = 0
        no_primary_key_tables = []
        column_type_count = {}
        unique_column_types = set()
        default_component_count = {}
        calc_validation_functions_count = {}
        calc_exclusion_rules_count = {}
        sub_component_props_count = {}
        estimated_row_counts = {}
        foreign_key_relationships_total = 0
        referenced_by_relationships_total = 0
        many_to_many_relationships_total = 0

        for table in self.schema.tables.values():
            # Fetch strategy analysis
            strategy = table.schema_structure.get("defaultFetchStrategy", "simple")
            if strategy == "simple":
                table_fetch_strategy["simple"] = (
                    table_fetch_strategy.get("simple", 0) + 1
                )
            else:
                if strategy not in table_fetch_strategy:
                    table_fetch_strategy[strategy] = []
                table_fetch_strategy[strategy].append(table.name)

            # Count tables with primary keys
            if table.has_primary_key:
                primary_key_count += 1
            else:
                no_primary_key_tables.append(table.name)

            # Count tables with foreign keys
            if table.foreign_keys:
                tables_with_fk += 1

            # Count tables with inverse foreign keys
            if table.referenced_by:
                tables_with_ifk += 1

            # Count tables with many-to-many relationships
            if table.many_to_many:
                tables_with_m2m += 1

            # Total relationships
            foreign_key_relationships_total += len(table.foreign_key_relationships)
            referenced_by_relationships_total += len(table.referenced_by_relationships)
            many_to_many_relationships_total += len(table.many_to_many_relationships)

            # Estimated row count
            estimated_row_counts[table.name] = table.estimated_row_count

            # Analyze column data
            for column in table.columns:
                col_type = column.base_type
                column_type_count[col_type] = column_type_count.get(col_type, 0) + 1
                unique_column_types.add(col_type)

                if column.default_component:
                    default_component_count[column.default_component] = (
                        default_component_count.get(column.default_component, 0) + 1
                    )

                if "typescript" in column.calc_validation_functions:
                    validation_function = column.calc_validation_functions["typescript"]
                    calc_validation_functions_count[validation_function] = (
                        calc_validation_functions_count.get(validation_function, 0) + 1
                    )

                if "typescript" in column.calc_exclusion_rules:
                    exclusion_rule = column.calc_exclusion_rules["typescript"]
                    calc_exclusion_rules_count[exclusion_rule] = (
                        calc_exclusion_rules_count.get(exclusion_rule, 0) + 1
                    )

                if "sub_component" in column.component_props:
                    sub_component = column.component_props["sub_component"]
                    sub_component_props_count[sub_component] = (
                        sub_component_props_count.get(sub_component, 0) + 1
                    )

        # General analysis summary
        analysis = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "table_count": len(self.schema.tables),
            "view_count": len(self.schema.views),
            "tables_with_primary_key": primary_key_count,
            "tables_without_primary_key": len(no_primary_key_tables),
            "no_primary_key_tables": no_primary_key_tables,
            "total_columns": sum(
                len(table.columns) for table in self.schema.tables.values()
            ),
            "unique_column_types": list(
                unique_column_types - set(self.all_enum_base_types)
            ),  # Exclude enums
            "most_common_column_types": dict(
                sorted(
                    column_type_count.items(), key=lambda item: item[1], reverse=True
                )[:10]
            ),
            "all_enum_base_types": list(self.all_enum_base_types),
            "tables_by_size": sorted(
                self.schema.tables.values(), key=lambda t: t.size_bytes, reverse=True
            )[:5],
            "views_by_size": sorted(
                self.schema.views.values(), key=lambda v: v.size_bytes, reverse=True
            )[:5],
            "fetch_strategies": table_fetch_strategy,
            "tables_with_foreign_keys": tables_with_fk,
            "tables_with_inverse_foreign_keys": tables_with_ifk,
            "tables_with_many_to_many": tables_with_m2m,
            "default_component_count": default_component_count,
            "calc_validation_functions_count": calc_validation_functions_count,
            "calc_exclusion_rules_count": calc_exclusion_rules_count,
            "sub_component_props_count": sub_component_props_count,
            "estimated_row_counts": dict(
                sorted(estimated_row_counts.items(), key=lambda x: x[1], reverse=True)
            ),
            "foreign_key_relationships_total": foreign_key_relationships_total,
            "referenced_by_relationships_total": referenced_by_relationships_total,
            "many_to_many_relationships_total": many_to_many_relationships_total,
            "database_table_names": [
                table.name for table in self.schema.tables.values()
            ],
            "database_view_names": [view.name for view in self.schema.views.values()],
            "allEntities": [table.name_camel for table in self.schema.tables.values()],
        }
        self.schema.save_analysis_json(analysis)
        return analysis

    def get_table_instance(self, table_name):
        return (
            self.schema.tables[table_name] if table_name in self.schema.tables else None
        )

    def get_view_instance(self, view_name):
        return self.schema.views[view_name] if view_name in self.schema.views else None

    def get_column_instance(self, table_name, column_name):
        return (
            self.schema.tables[table_name].columns[column_name]
            if table_name in self.schema.tables
            and column_name in self.schema.tables[table_name].columns
            else None
        )

    def get_table_frontend_name(self, table_name):
        return (
            self.get_table_instance(table_name).name_camel
            if table_name in self.schema.tables
            else table_name
        )

    def get_view_frontend_name(self, view_name):
        return (
            self.get_view_instance(view_name).name_camel
            if view_name in self.schema.views
            else view_name
        )

    def get_column_frontend_name(self, table_name, column_name):
        return (
            self.get_column_instance(table_name, column_name).name_camel
            if table_name in self.schema.tables
            and column_name in self.schema.tables[table_name].columns
            else self.utils.to_camel_case(column_name)
        )

    def transform_foreign_keys(self, main_table_name, entry):
        if not entry:
            return {}
        transformed = {}
        for key, fk_data in (entry.get("foreign_keys") or {}).items():
            transformed[self.get_table_frontend_name(key)] = {
                "foreign_table": key,
                "foreign_entity": self.get_table_frontend_name(key),
                "column": fk_data["column"],
                "fieldName": self.get_column_frontend_name(
                    main_table_name, fk_data["column"]
                ),
                "foreign_field": self.get_column_frontend_name(
                    key, fk_data["foreign_column"]
                ),
                "foreign_column": fk_data["foreign_column"],
                "relationship_type": fk_data["relationship_type"],
                "constraint_name": fk_data["constraint_name"],
            }

        vcprint(
            transformed,
            title="Transformed Foreign Keys",
            verbose=self.debug,
            pretty=True,
            color="yellow",
        )
        return transformed

    def transform_referenced_by(self, table_name, entry):
        if not entry:
            return {}
        transformed = {}
        for key, ref_data in (entry.get("referenced_by") or {}).items():
            transformed[self.get_table_frontend_name(key)] = {
                "foreign_table": key,
                "foreign_entity": self.get_table_frontend_name(key),
                "field": self.get_column_frontend_name(key, ref_data["column"]),
                "column": ref_data["column"],
                "foreign_field": self.get_column_frontend_name(
                    table_name, ref_data["foreign_column"]
                ),
                "foreign_column": ref_data["foreign_column"],
                "constraint_name": ref_data["constraint_name"],
            }
        return transformed

    def get_frontend_full_relationships(self):
        self.frontend_full_relationships = []

        for info_object in self.full_relationships:
            database_table = info_object["table_name"]
            entity_name = self.get_table_frontend_name(database_table)

            transformed_foreign_keys = self.transform_foreign_keys(
                database_table, info_object
            )
            transformed_referenced_by = self.transform_referenced_by(
                database_table, info_object
            )

            updated_relationship = {
                "entityName": entity_name,
                "table_name": database_table,
                "foreignKeys": transformed_foreign_keys,
                "referencedBy": transformed_referenced_by,
            }
            self.frontend_full_relationships.append(updated_relationship)

        vcprint(
            self.frontend_full_relationships,
            title="Frontend Full Relationships",
            pretty=True,
            verbose=self.verbose,
            color="yellow",
        )
        return self.frontend_full_relationships

    def get_full_relationship_analysis(self):
        frontend_relationships = self.get_frontend_full_relationships()
        relationship_details = {
            rel["table_name"]: rel for rel in frontend_relationships
        }

        self.full_relationship_analysis = {}

        for table_name, analysis in self.overview_analysis.items():
            frontend_name = self.get_table_frontend_name(table_name)

            transformed_analysis = {
                "selfReferential": [
                    self.get_table_frontend_name(name)
                    for name in analysis["self-referential"]
                ],
                "manyToMany": [
                    self.get_table_frontend_name(name)
                    for name in analysis["many-to-many"]
                ],
                "oneToOne": [
                    self.get_table_frontend_name(name)
                    for name in analysis["one-to-one"]
                ],
                "manyToOne": [
                    self.get_table_frontend_name(name)
                    for name in analysis["many-to-one"]
                ],
                "oneToMany": [
                    self.get_table_frontend_name(name)
                    for name in analysis["one-to-many"]
                ],
                "undefined": [
                    self.get_table_frontend_name(name) for name in analysis["undefined"]
                ],
                "inverseReferences": [
                    self.get_table_frontend_name(name)
                    for name in analysis["inverse_references"]
                ],
                "relationshipDetails": relationship_details.get(table_name, {}),
            }

            self.full_relationship_analysis[frontend_name] = transformed_analysis

        self.schema.save_frontend_full_relationships_json(
            self.full_relationship_analysis
        )

        ts_types_string = get_relationship_data_model_types()

        ts_code_content = self.utils.python_dict_to_ts_with_updates(
            name="entityRelationships",
            obj=self.full_relationship_analysis,
            keys_to_camel=True,
            export=True,
            as_const=True,
            ts_type=None,
        )

        ts_code_content = ts_types_string + ts_code_content
        self.schema.code_handler.save_code_file("fullRelationships.ts", ts_code_content)

        vcprint(
            self.full_relationship_analysis,
            title="Full Relationship Analysis",
            pretty=True,
            verbose=self.verbose,
            color="blue",
        )

    def get_frontend_junction_analysis(self):
        frontend_junction_analysis = {}

        for table_key, table_value in self.full_junction_analysis.items():
            table_instance = self.schema.tables.get(table_key)
            entity_name = table_instance.name_camel if table_instance else table_key

            updated_table = {
                "entityName": entity_name,
                "schema": table_value["schema"],
                "connectedTables": [],
                "additionalFields": [],
            }

            for connected_table in table_value["connected_tables"]:
                connected_instance = self.schema.tables.get(connected_table["table"])
                updated_table["connectedTables"].append(
                    {
                        "schema": connected_table["schema"],
                        "entity": connected_instance.name_camel
                        if connected_instance
                        else connected_table["table"],
                        "connectingColumn": self.schema.tables[table_key]
                        .columns[connected_table["connecting_column"]]
                        .name_camel
                        if table_instance
                        and connected_table["connecting_column"]
                        in table_instance.columns
                        else connected_table["connecting_column"],
                        "referencedColumn": connected_instance.columns[
                            connected_table["referenced_column"]
                        ].name_camel
                        if connected_instance
                        and connected_table["referenced_column"]
                        in connected_instance.columns
                        else connected_table["referenced_column"],
                    }
                )

            for field in table_value["additional_fields"]:
                field_instance = (
                    table_instance.columns.get(field) if table_instance else None
                )
                updated_table["additionalFields"].append(
                    field_instance.name_camel if field_instance else field
                )

            frontend_junction_analysis[entity_name] = updated_table

        self.schema.save_frontend_junction_analysis_json(frontend_junction_analysis)
        return frontend_junction_analysis

    def __repr__(self):
        return f"<SchemaManager database={self.database}, schema={self.schema.name}, initialized={self.initialized}>"
