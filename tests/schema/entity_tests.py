from matrx_orm.schema_builder.helpers import (
    generate_full_typescript_file,
    generate_complete_main_hooks_file,
    generate_multiple_entities,
)

from matrx_orm.schema_builder.helpers import check_git_status
from matrx_utils import clear_terminal


def test_check_git_status():
    save_direct = False

    if save_direct:
        check_git_status(save_direct)
        input(
            "WARNING: This will overwrite the existing schema files. Press Enter to continue..."
        )


def test_generate_entity_hooks():
    entity_names = [
        "workflow",
        "registered_function",
        "arg",
    ]

    result = generate_complete_main_hooks_file(entity_names)
    print(result)

    # Optionally, write to a file
    with open("generated_types.ts", "w") as f:
        f.write(result)
    return result


def test_generate_entity_overrides():
    # Example: pass your app-specific entity_overrides from DatabaseProjectConfig here
    example_overrides = {
        "recipe": {"defaultFetchStrategy": '"fkAndIfk"'},
    }
    entity_names = ["projects", "recipe", "wc_impairment_definition"]
    ts_code = generate_multiple_entities(entity_names, example_overrides)
    print(ts_code)
    return ts_code


def test_generate_typescript_files():
    field_overrides = {
        "dataInputComponent": {
            "options": {"componentProps": {"subComponent": "optionsManager"}}
        },
        "aiSettings": {
            "temperature": {
                "defaultComponent": "SPECIAL",
                "componentProps": {
                    "subComponent": "SLIDER",
                    "className": "w-full",
                    "min": 0,
                    "max": 2,
                    "step": 0.01,
                    "numberType": "real",
                },
            }
        },
        "messageTemplate": {
            "role": """{
                isDisplayField: true
            }""",
            "type": """{
                isDisplayField: false
            }""",
        },
    }

    entity_names = [
        "dataInputComponent",
        "aiSettings",
        "messageTemplate",
        "broker",  # No overrides, should generate an empty object
        "unknownEntity",  # Completely unknown entity, should generate an empty object
    ]

    ts_code = generate_full_typescript_file(entity_names, field_overrides)
    print(ts_code)  # Prints the generated TypeScript file content
    return ts_code


if __name__ == "__main__":
    clear_terminal()

    # Test Git Status Checker =================================================
    test_check_git_status()

    # Test Entity Hook Generator =================================================
    entity_hooks_code = test_generate_entity_hooks()

    # Test Entity Overrides Generator =================================================
    entity_overrides_code = test_generate_entity_overrides()

    # Test Entity Field Overrides Generator =================================================
    typescript_files_code = test_generate_typescript_files()
