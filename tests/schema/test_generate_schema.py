from matrx_orm.schema_builder.schema_manager import SchemaManager
from matrx_utils import vcprint, clear_terminal


def get_test_schema_manager(
    schema: str, database_project: str, additional_schemas: list[str]
):
    schema_manager = SchemaManager(
        schema=schema,
        database_project=database_project,
        additional_schemas=additional_schemas,
    )
    schema_manager.initialize()
    return schema_manager


def test_generate_full_schema_system(schema_manager: SchemaManager):
    matrx_schema_entry = schema_manager.schema.generate_schema_files()

    matrx_models = schema_manager.schema.generate_models()

    analysis = schema_manager.analyze_schema()
    vcprint(
        data=analysis,
        title="Schema Analysis",
        pretty=True,
        verbose=False,
        color="yellow",
    )
    schema_manager.schema.code_handler.print_all_batched()

    return {
        "schema": matrx_schema_entry,
        "models": matrx_models,
        "analysis": analysis,
    }


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
        color="cyan",
    )

    example_view = schema_manager.get_view(
        "view_registered_function_all_rels"
    ).to_dict()
    vcprint(
        example_view,
        title="Full Registered Function View",
        color="yellow",
    )

    example_table = schema_manager.get_table("registered_function").to_dict()
    vcprint(
        example_table,
        title="Flashcard History Table",
        color="cyan",
    )

    matrx_schema = schema_manager.schema.to_dict()
    vcprint(matrx_schema, title="Full Schema", color="cyan")

    return matrx_schema


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


if __name__ == "__main__":
    clear_terminal()

    schema = "public"
    database_project = (
        "your_database_project"  # replace with your registered project name
    )
    additional_schemas = ["auth"]

    schema_manager = get_test_schema_manager(
        schema, database_project, additional_schemas
    )

    # Test generate full schema system =================================================
    full_schema_object = test_generate_full_schema_system(schema_manager)

    vcprint(
        data=full_schema_object,
        title="Full Schema Object",
        verbose=False,
        color="cyan",
    )

    # Test example usage =================================================
    matrx_schema = example_usage(schema_manager)
    vcprint(
        data=matrx_schema,
        title="Matrx Schema",
        color="cyan",
    )

    # Test get full schema object =================================================
    full_schema_object = get_full_schema_object(schema, database_project)
    vcprint(
        data=full_schema_object,
        title="Full Schema Object",
        color="cyan",
    )
