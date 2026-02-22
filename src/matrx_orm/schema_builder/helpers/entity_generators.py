from matrx_orm.schema_builder.generator import get_default_component_props
from copy import deepcopy
from collections import OrderedDict
import re
import json


def generate_imports():
    #     return """import { EntityKeys } from '@/types';
    # import { EntityOverrides } from './overrideTypes';
    # """
    return ""


def generate_typescript_entity(entity_name, overrides=None):
    overrides = overrides or {}
    ts_template = f"""
const {entity_name}EntityOverrides: EntityOverrides<'{entity_name}'> = {{
    schemaType: {overrides.get("schemaType", "null")},
    entityName: {overrides.get("entityName", "null")},
    uniqueTableId: {overrides.get("uniqueTableId", "null")},
    uniqueEntityId: {overrides.get("uniqueEntityId", "null")},
    primaryKey: {overrides.get("primaryKey", "null")},
    primaryKeyMetadata: {overrides.get("primaryKeyMetadata", "null")},
    displayFieldMetadata: {overrides.get("displayFieldMetadata", "null")},
    defaultFetchStrategy: {overrides.get("defaultFetchStrategy", "null")},
    componentProps: {overrides.get("componentProps", "null")},
    entityNameFormats: {overrides.get("entityNameFormats", "null")},
    relationships: {overrides.get("relationships", "null")},
    entityFields: {overrides.get("entityFields", "null")}
}};
"""
    return ts_template


def generate_multiple_entities(entity_names, system_overrides):
    imports = generate_imports()
    entities_code = "\n\n".join(
        generate_typescript_entity(name, system_overrides.get(name, {}))
        for name in entity_names
    )

    entity_overrides_list = "\n".join(
        f"    {name}: {name}EntityOverrides," for name in entity_names
    )

    entity_overrides_block = f"""

export const ENTITY_OVERRIDES: Record<EntityKeys, EntityOverrides<EntityKeys>> = {{
{entity_overrides_list}
}};
"""

    return imports + "\n" + entities_code + entity_overrides_block


def merge_component_props(overrides=None):
    """
    Merges provided overrides with the default componentProps while retaining order.
    Returns a TypeScript-friendly string.
    """
    props_without_required_entry = get_default_component_props()
    props_without_required_entry.pop("required", None)  # Avoid KeyError if missing

    merged_props = deepcopy(props_without_required_entry)

    if overrides:  # Ensure overrides is not None
        merged_props.update(overrides)  # Apply overrides

    # Ensure "required" is always last in the object
    merged_props["required"] = False

    # Convert to an OrderedDict to maintain key order
    ordered_props = OrderedDict(merged_props)

    # Convert to a formatted TypeScript object string
    formatted_props = json.dumps(ordered_props, indent=4)

    # Remove quotes from keys to match TypeScript syntax
    formatted_props = re.sub(r'"(\w+)"\s*:', r"\1:", formatted_props)

    return formatted_props


def format_ts_object(ts_object_str):
    """
    Formats a JSON-like string to remove quotes from keys for TypeScript compatibility.
    Ensures TypeScript style object notation.
    """
    return re.sub(r'"(\w+)"\s*:', r"\1:", ts_object_str)


def generate_typescript_field_overrides(entity_name, overrides):
    """
    Generates a TypeScript field overrides object for a given entity.
    If no overrides exist, returns an empty object.
    """
    if not overrides:
        return f"const {entity_name}FieldOverrides: AllFieldOverrides = {{}};"

    ts_template = f"const {entity_name}FieldOverrides: AllFieldOverrides = {{\n"

    for field, value in overrides.items():
        if isinstance(value, str):
            # Handle string-based field overrides (non-componentProps)
            formatted_value = format_ts_object(value)
            ts_template += f"    {field}: {formatted_value},\n"
        elif isinstance(value, dict):
            # Handle componentProps while keeping other field properties
            component_props_override = value.get("componentProps", {})
            merged_component_props = (
                merge_component_props(component_props_override)
                if component_props_override
                else None
            )

            # Start field object
            ts_template += f"    {field}: {{\n"

            # Add other field properties (excluding componentProps)
            for key, val in value.items():
                if key != "componentProps":
                    ts_template += f"        {key}: {json.dumps(val)},\n"

            # Add merged componentProps if it exists
            if merged_component_props:
                ts_template += f"        componentProps: {merged_component_props},\n"

            # Close field object
            ts_template += f"    }},\n"

    ts_template += "};\n"
    return ts_template


def generate_full_typescript_file(entity_names, system_overrides):
    """
    Generates the entire TypeScript file as a string, including all entity field overrides
    and the final `ENTITY_FIELD_OVERRIDES` export.
    """
    entity_overrides_blocks = "\n\n".join(
        generate_typescript_field_overrides(name, system_overrides.get(name, {}))
        for name in entity_names
    )

    entity_overrides_list = "\n".join(
        f"    {name}: {name}FieldOverrides," for name in entity_names
    )

    entity_overrides_export = f"""
export const ENTITY_FIELD_OVERRIDES: AllEntityFieldOverrides = {{
{entity_overrides_list}
}};
"""

    return entity_overrides_blocks + "\n\n" + entity_overrides_export


def to_camel_case(snake_str):
    components = snake_str.split("_")
    return components[0] + "".join(x.capitalize() for x in components[1:])


def to_pascal_case(snake_str):
    components = snake_str.split("_")
    return "".join(x.capitalize() for x in components)


def generate_entity_main_hook(entity_name_snake):
    camel_case = to_camel_case(entity_name_snake)
    pascal_case = to_pascal_case(entity_name_snake)

    type_template = f"""type Use{pascal_case}WithFetchReturn = {{
    {camel_case}Selectors: EntitySelectors<"{camel_case}">;
    {camel_case}Actions: EntityActions<"{camel_case}">;
    {camel_case}Records: Record<MatrxRecordId, {pascal_case}Data>;
    {camel_case}RecordsById: Record<string, {pascal_case}Data>;
    {camel_case}UnsavedRecords: Record<MatrxRecordId, Partial<{pascal_case}Data>>;
    {camel_case}SelectedRecordIds: MatrxRecordId[];
    {camel_case}IsLoading: boolean;
    {camel_case}IsError: boolean;
    {camel_case}QuickRefRecords: QuickReferenceRecord[];
    add{pascal_case}MatrxId: (recordId: MatrxRecordId) => void;
    add{pascal_case}MatrxIds: (recordIds: MatrxRecordId[]) => void;
    remove{pascal_case}MatrxId: (recordId: MatrxRecordId) => void;
    remove{pascal_case}MatrxIds: (recordIds: MatrxRecordId[]) => void;
    add{pascal_case}PkValue: (pkValue: string) => void;
    add{pascal_case}PkValues: (pkValues: Record<string, unknown>) => void;
    remove{pascal_case}PkValue: (pkValue: string) => void;
    remove{pascal_case}PkValues: (pkValues: Record<string, unknown>) => void;
    is{pascal_case}MissingRecords: boolean;
    set{pascal_case}ShouldFetch: (shouldFetch: boolean) => void;
    set{pascal_case}FetchMode: (fetchMode: FetchMode) => void;
    fetch{pascal_case}QuickRefs: () => void;
    fetch{pascal_case}One: (recordId: MatrxRecordId) => void;
    fetch{pascal_case}OneWithFkIfk: (recordId: MatrxRecordId) => void;
    fetch{pascal_case}All: () => void;
    fetch{pascal_case}Paginated: (page: number, pageSize: number, options?: {{
        maxCount?: number;
        filters?: FilterPayload;
        sort?: SortPayload;
    }}) => void
}};

export const use{pascal_case}WithFetch = (): Use{pascal_case}WithFetchReturn => {{
    const {{
        selectors: {camel_case}Selectors,
        actions: {camel_case}Actions,
        allRecords: {camel_case}Records,
        recordsById: {camel_case}RecordsById,
        unsavedRecords: {camel_case}UnsavedRecords,
        selectedRecordIds: {camel_case}SelectedRecordIds,
        isLoading: {camel_case}IsLoading,
        isError: {camel_case}IsError,
        quickRefRecords: {camel_case}QuickRefRecords,
        addMatrxId: add{pascal_case}MatrxId,
        addMatrxIds: add{pascal_case}MatrxIds,
        removeMatrxId: remove{pascal_case}MatrxId,
        removeMatrxIds: remove{pascal_case}MatrxIds,
        addPkValue: add{pascal_case}PkValue,
        addPkValues: add{pascal_case}PkValues,
        removePkValue: remove{pascal_case}PkValue,
        removePkValues: remove{pascal_case}PkValues,
        isMissingRecords: is{pascal_case}MissingRecords,
        setShouldFetch: set{pascal_case}ShouldFetch,
        setFetchMode: set{pascal_case}FetchMode,
        fetchQuickRefs: fetch{pascal_case}QuickRefs,
        fetchOne: fetch{pascal_case}One,
        fetchOneWithFkIfk: fetch{pascal_case}OneWithFkIfk,
        fetchAll: fetch{pascal_case}All,
        fetchPaginated: fetch{pascal_case}Paginated,

    }} = useEntityWithFetch("{camel_case}");

    return {{
        {camel_case}Selectors,
        {camel_case}Actions,
        {camel_case}Records,
        {camel_case}RecordsById,
        {camel_case}UnsavedRecords,
        {camel_case}SelectedRecordIds,
        {camel_case}IsLoading,
        {camel_case}IsError,
        {camel_case}QuickRefRecords,
        add{pascal_case}MatrxId,
        add{pascal_case}MatrxIds,
        remove{pascal_case}MatrxId,
        remove{pascal_case}MatrxIds,
        add{pascal_case}PkValue,
        add{pascal_case}PkValues,
        remove{pascal_case}PkValue,
        remove{pascal_case}PkValues,
        is{pascal_case}MissingRecords,
        set{pascal_case}ShouldFetch,
        set{pascal_case}FetchMode,
        fetch{pascal_case}QuickRefs,
        fetch{pascal_case}One,
        fetch{pascal_case}OneWithFkIfk,
        fetch{pascal_case}All,
        fetch{pascal_case}Paginated,
    }};
}};
"""
    return type_template


def generate_all_entity_main_hooks(entity_names):
    entries = [generate_entity_main_hook(name) for name in entity_names]
    return "\n\n\n".join(entries)


def generate_main_hook_imports(entity_names):
    """Generate complete imports including dynamic Data types based on entity names"""

    # Generate dynamic Data type imports from entity names
    dynamic_data_imports = []
    for entity_name in entity_names:
        pascal_case = to_pascal_case(entity_name)
        data_type = f"{pascal_case}Data"
        dynamic_data_imports.append(f"    {data_type},")

    # Sort the data imports for consistency
    dynamic_data_imports.sort()

    # Create the complete import statement
    all_data_imports = "\n".join(dynamic_data_imports)

    complete_imports = f"""import {{
{all_data_imports}
}} from "@/types";
import {{ MatrxRecordId, QuickReferenceRecord, FilterPayload, SortPayload }} from "@/lib/redux/entity/types/stateTypes";
import {{ EntitySelectors }} from "@/lib/redux/entity/selectors";
import {{ EntityActions }} from "@/lib/redux/entity/slice";
import {{ FetchMode }} from "@/lib/redux/entity/actions";
import {{ useEntityWithFetch }} from "@/lib/redux/entity/hooks/useAllData";"""

    return complete_imports


def generate_complete_main_hooks_file(entity_names):
    """Generate the complete main hooks file with dynamic imports and all entity hooks"""
    imports = generate_main_hook_imports(entity_names)
    hooks = generate_all_entity_main_hooks(entity_names)

    return f"{imports}\n\n{hooks}"
