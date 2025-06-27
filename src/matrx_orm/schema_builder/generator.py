import os
from matrx_utils import vcprint
from matrx_orm.schema_builder.helpers.git_checker import check_git_status
from matrx_orm.schema_builder.schema_manager import SchemaManager

generator_verbose = False
generator_debug = False
generator_info = True


def generate_schema_structure(schema_manager, table_name):
    """
    Generates the schema structure with defaultFetchStrategy, foreignKeys, inverseForeignKeys, and manyToMany relationships.

    :param schema_manager: The schema manager object that holds the schema details
    :param table_name: The name of the table for which the schema is being generated
    :return: A dictionary representing the schema structure
    """
    table = schema_manager.get_table(table_name)

    if not table:
        print(f"Table '{table_name}' not found.")
        return None

    schema_structure = {
        "defaultFetchStrategy": None,  # This will be determined based on the relationships present
        "foreignKeys": [],  # List of foreign key relationships
        "inverseForeignKeys": [],  # List of tables that reference the current table
        "manyToMany": [],  # List of many-to-many relationships
    }

    # Populate foreign keys
    if table.foreign_keys:
        for target, rel in table.foreign_keys.items():
            schema_structure["foreignKeys"].append(
                {
                    "column": rel.local_column,  # Assuming local_column holds the FK column in the current table
                    "relatedTable": target,  # Target is the related table name
                    "relatedColumn": rel.related_column,  # Assuming related_column is the column in the target table
                }
            )

    # Populate inverse foreign keys (tables that reference this table)
    if table.referenced_by:
        for source, rel in table.referenced_by.items():
            schema_structure["inverseForeignKeys"].append(
                {
                    "relatedTable": source,  # Source is the table that references the current table
                    "relatedColumn": rel.local_column,  # Assuming local_column holds the FK column in the source table
                }
            )

    # Populate many-to-many relationships
    if table.many_to_many:
        for mm in table.many_to_many:
            schema_structure["manyToMany"].append(
                {
                    "relatedTable": mm["related_table"],  # The related table
                    "junctionTable": mm["junction_table"],  # The junction table that joins the two tables
                    "localColumn": mm["local_column"],  # Column in the junction table for the current table
                    "relatedColumn": mm["related_column"],  # Column in the junction table for the related table
                }
            )

    # Determine fetch strategy based on available relationships
    if schema_structure["manyToMany"]:
        schema_structure["defaultFetchStrategy"] = "m2m"
    elif schema_structure["foreignKeys"] and schema_structure["inverseForeignKeys"]:
        schema_structure["defaultFetchStrategy"] = "fkAndIfk"
    elif schema_structure["foreignKeys"]:
        schema_structure["defaultFetchStrategy"] = "fk"
    elif schema_structure["inverseForeignKeys"]:
        schema_structure["defaultFetchStrategy"] = "ifk"
    else:
        schema_structure["defaultFetchStrategy"] = "simple"  # No relationships, basic fetch

    return schema_structure


def example_usage(schema_manager):
    table = schema_manager.get_table("flashcard_data")
    print()
    if table:
        vcprint(f"Table: {table.name}")
        vcprint("Foreign Keys:")
        for target, rel in table.foreign_keys.items():
            vcprint(f"  - {target}: {rel}")
        vcprint("Referenced By:")
        for source, rel in table.referenced_by.items():
            vcprint(f"  - {source}: {rel}")
        vcprint("Many-to-Many Relationships:")
        for mm in table.many_to_many:
            vcprint(f"  - {mm['related_table']} (via {mm['junction_table']})")

    example_column = schema_manager.get_column("flashcard_data", "id").to_dict()
    vcprint(
        example_column,
        title="Flashcard ID Column",
        pretty=True,
        verbose=generator_verbose,
        color="cyan",
    )

    example_view = schema_manager.get_view("view_registered_function_all_rels").to_dict()
    vcprint(
        example_view,
        title="Full Registered Function View",
        pretty=True,
        verbose=generator_verbose,
        color="yellow",
    )

    example_table = schema_manager.get_table("registered_function").to_dict()
    vcprint(
        example_table,
        title="Flashcard History Table",
        pretty=True,
        verbose=generator_verbose,
        color="cyan",
    )

    # full_schema = schema_manager.schema.to_dict()
    # vcprint(full_schema, title="Full Schema", pretty=True, verbose=verbose, color="cyan")


def get_full_schema_object(schema, database_project):
    schema_manager = SchemaManager(schema=schema, database_project=database_project)
    schema_manager.initialize()
    matrx_schema_entry = schema_manager.schema.generate_schema_files()
    matrx_models = schema_manager.schema.generate_models()
    analysis = schema_manager.analyze_schema()

    full_schema_object = {
        "schema": matrx_schema_entry,
        "models": matrx_models,
        "analysis": analysis,
    }
    return full_schema_object


# ====== IMPORTANT: If save_direct = True in generator.py, live files will be overwritten with auto-generated files ======

# If this environmental variable is set to your actual project root, auto-generated python files will overwrite the live, existing files
ADMIN_PYTHON_ROOT = os.getenv("ADMIN_PYTHON_ROOT", "")

# If this environmental variable is set to your actual project root, auto-generated typescript files will overwrite the live, existing files
ADMIN_TS_ROOT = os.getenv("ADMIN_TS_ROOT", "")

# =========================================================================================================================
