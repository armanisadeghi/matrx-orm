from matrx_utils import vcprint
from matrx_orm.schema_builder.common import DEBUG_CONFIG, dt_utils


class View:
    def __init__(
        self,
        oid,
        name,
        type_,
        schema,
        database,
        owner,
        size_bytes,
        description,
        view_definition,
        column_data,
    ):
        self.utils = dt_utils
        self.oid = oid
        self.name = name
        self.type = type_
        self.schema = schema
        self.database = database
        self.owner = owner
        self.size_bytes = size_bytes
        self.description = description
        self.view_definition = view_definition
        self.column_data = column_data
        self.verbose = DEBUG_CONFIG["verbose"]
        self.debug = DEBUG_CONFIG["debug"]
        self.info = DEBUG_CONFIG["info"]

        self.initialized = False

        self.name_snake = self.utils.to_snake_case(self.name)
        self.name_camel = self.utils.to_camel_case(self.name)
        self.name_pascal = self.utils.to_pascal_case(self.name)
        self.name_kebab = self.utils.to_kebab_case(self.name)
        self.name_title = self.utils.to_title_case(self.name)

        self.unique_name_lookups = None

    def __repr__(self):
        return f"<View name={self.name}>"

    def initialize_code_generation(self):
        if self.initialized:
            return
        self.generate_unique_name_lookups()
        self.initialized = True

    def generate_unique_name_lookups(self):
        name_variations = {
            self.name,
            self.name_camel,
            self.name_snake,
            self.name_title,
            self.name_pascal,
            self.name_kebab,
            f"p_{self.name_snake}",
        }

        unique_names = set(name_variations)

        formatted_unique_names = {
            f'"{name}"' if " " in name or "-" in name else name: self.name_camel
            for name in unique_names
        }

        self.unique_name_lookups = formatted_unique_names

    def to_dict(self):
        return {
            "oid": self.oid,
            "name": self.name,
            "type": self.type,
            "schema": self.schema,
            "database": self.database,
            "owner": self.owner,
            "size_bytes": self.size_bytes,
            "description": self.description,
            "view_definition": self.view_definition,
            "column_data": self.column_data,
        }
