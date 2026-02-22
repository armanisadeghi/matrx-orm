def get_schema_structure(schema_manager, table_name):
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
                    "junctionTable": mm[
                        "junction_table"
                    ],  # The junction table that joins the two tables
                    "localColumn": mm[
                        "local_column"
                    ],  # Column in the junction table for the current table
                    "relatedColumn": mm[
                        "related_column"
                    ],  # Column in the junction table for the related table
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
        schema_structure["defaultFetchStrategy"] = (
            "simple"  # No relationships, basic fetch
        )

    return schema_structure


def get_default_component_props():
    return {
        "subComponent": "default",
        "variant": "default",
        "section": "default",
        "placeholder": "default",
        "size": "default",
        "textSize": "default",
        "textColor": "default",
        "rows": "default",
        "animation": "default",
        "fullWidthValue": "default",
        "fullWidth": "default",
        "disabled": "default",
        "className": "default",
        "type": "default",
        "onChange": "default",
        "onBlur": "default",
        "formatString": "default",
        "min": "default",
        "max": "default",
        "step": "default",
        "numberType": "default",
        "options": "default",
    }


# Method to generate the AutomationSchema
def generate_automation_schema():  # TODO: Currently not used.
    lines = [
        "export type AutomationSchema = {",
        "    [tableName in AutomationTableName]: {",
        "        entityNameFormats: {",
        "            frontend: string;",
        "            backend: string;",
        "            database: string;",
        "            pretty: string;",
        "            component: string;",
        "            kebab: string;",
        "            [key: string]: string;",
        "        };",
        "        schemaType: 'table' | 'view' | 'dynamic' | 'other';",
        "        entityFields: {",
        "            [fieldName: string]: {",
        "                fieldNameFormats: {",
        "                    frontend: string;",
        "                    backend: string;",
        "                    database: string;",
        "                    pretty: string;",
        "                    component: string;",
        "                    kebab: string;",
        "                    [key: string]: string;",
        "                };",
        "                dataType: DataType;",
        "                isRequired?: boolean;",
        "                maxLength?: number | null;",
        "                isArray?: boolean;",
        "                defaultValue?: any;",
        "                isPrimaryKey?: boolean;",
        "                defaultGeneratorFunction?: string | null;",
        "                validationFunctions?: string[];",
        "                exclusionRules?: string[];",
        "                defaultComponent?: string;",
        "                structure: 'single' | 'array' | 'object' | 'foreignKey' | 'inverseForeignKey' | 'manyToMany';",
        "                isNative: boolean;",
        "                typeReference: TypeBrand<any>;",
        "                databaseTable: string;",
        "            };",
        "        };",
        "        defaultFetchStrategy: 'simple' | 'fk' | 'ifk' | 'm2m' | 'fkAndIfk' | 'm2mAndFk' | 'm2mAndIfk' | 'fkIfkAndM2M';",
        "        relationships: Array<{",
        "            relationshipType: 'foreignKey' | 'inverseForeignKey' | 'manyToMany';",
        "            column: string;",
        "            relatedTable: string;",
        "            relatedColumn: string;",
        "            junctionTable: string | null;",
        "        }>;",
        "    };",
        "};",
    ]

    return "\n".join(lines)


def get_relationship_data_model_types():
    ts_code_content = """

    import { AnyEntityDatabaseTable, EntityKeys } from "@/types";

    export type EntityRelationshipType =
        | "self-referential"
        | "one-to-one"
        | "one-to-many"
        | "many-to-one"
        | "many-to-many";

    export type ForeignKeyDetails = {
        foreignTable: AnyEntityDatabaseTable;
        foreignEntity: EntityKeys;
        column: string;
        fieldName: string;
        foreignField: string;
        foreignColumn: string;
        relationshipType: EntityRelationshipType;
        constraintName: string;
    };

    export type ReferencedByDetails = {
        foreignTable: AnyEntityDatabaseTable;
        foreignEntity: EntityKeys;
        field: string;
        column: string;
        foreignField: string;
        foreignColumn: string;
        constraintName: string;
    };

    export type RelationshipDetails = {
        entityName: EntityKeys;
        tableName: AnyEntityDatabaseTable;
        foreignKeys: Partial<Record<EntityKeys, ForeignKeyDetails>> | Record<string, never>;
        referencedBy: Partial<Record<EntityKeys, ReferencedByDetails>> | Record<string, never>;
    };

    export type FullEntityRelationships = {
        selfReferential: EntityKeys[];
        manyToMany: EntityKeys[];
        oneToOne: EntityKeys[];
        manyToOne: EntityKeys[];
        oneToMany: EntityKeys[];
        undefined: EntityKeys[];
        inverseReferences: EntityKeys[];
        relationshipDetails: RelationshipDetails;
    };

    export const asEntityRelationships = (data: any): Record<EntityKeys, FullEntityRelationships> => {
        return data as Record<EntityKeys, FullEntityRelationships>;
    };

    """
    return ts_code_content


def generate_dto_and_manager(name, name_camel):
    return f"""

@dataclass
class {name_camel}DTO(BaseDTO):
    id: str

    @classmethod
    async def from_model(cls, model):
        return cls(id=str(model.id))


class {name_camel}Manager(BaseManager):
    def __init__(self):
        super().__init__({name_camel}, {name_camel}DTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, {name}):
        pass
    """
