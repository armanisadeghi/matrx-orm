from matrx_orm.schema_builder.helpers import save_manager_class
from matrx_utils import vcprint, clear_terminal


def test_generate_manager_class():
    ai_model_auto_config = {
        "model_pascal": "AiModel",
        "model_name": "ai_model",
        "model_name_plural": "ai_models",
        "model_name_snake": "ai_model",
        "relations": [
            "ai_provider",
            "ai_model_endpoint",
            "ai_settings",
            "recipe_model",
        ],
        "filter_fields": [
            "name",
            "common_name",
            "provider",
            "model_class",
            "model_provider",
        ],
        "include_core_relations": True,
        "include_active_relations": False,
        "include_filter_fields": True,
        "include_active_methods": False,
        "include_or_not_methods": False,
        "include_to_dict_methods": True,
        "include_to_dict_relations": True,
    }

    model_class_str, file_path = save_manager_class(**ai_model_auto_config)
    print(model_class_str)
    print(file_path)
    return {
        "model_class_str": model_class_str,
        "file_path": file_path,
    }


if __name__ == "__main__":
    clear_terminal()

    base_generation_object = test_generate_manager_class()
    vcprint(
        data=base_generation_object,
        title="Base Generation Object",
        verbose=False,
        color="cyan",
    )
