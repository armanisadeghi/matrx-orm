# This file is intentionally empty.
#
# Entity and field overrides for the schema builder are app-specific configuration
# and must NOT live in the ORM package.
#
# Pass them to the ORM at registration time via DatabaseProjectConfig:
#
#   from matrx_orm import register_database, DatabaseProjectConfig
#
#   register_database(DatabaseProjectConfig(
#       name="my_project",
#       ...,
#       entity_overrides={
#           "recipe": {"defaultFetchStrategy": '"fkAndIfk"'},
#           "broker": {"displayFieldMetadata": '{ fieldName: "displayName", ... }'},
#       },
#       field_overrides={
#           "recipe": {"tags": {"componentProps": {"subComponent": "tagsManager"}}},
#           "broker": {"name": "{isDisplayField: false, ...}"},
#       },
#   ))
#
# The schema builder reads these automatically when generating TypeScript output.
