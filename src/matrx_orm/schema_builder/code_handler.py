from __future__ import annotations

import os

from matrx_utils.file_handling.specific_handlers.code_handler import CodeHandler

from matrx_orm.schema_builder.common import OutputConfig


class SchemaCodeHandler(CodeHandler):
    """
    Thin subclass of CodeHandler that gates file writes based on OutputConfig.

    - generate_and_save_code_from_object: skipped when the file extension is
      .py (python=False) or .ts (typescript=False).
    - write_to_json: skipped when json=False.

    Everything else — including the temp/direct routing — is handled by the
    parent class exactly as before.
    """

    def __init__(self, output_config: OutputConfig):
        super().__init__(save_direct=output_config.save_direct)
        self.output_config = output_config

    def _is_allowed(self, path: str) -> bool:
        ext = os.path.splitext(path)[-1].lower()
        if ext == ".py":
            return self.output_config.python
        if ext == ".ts":
            return self.output_config.typescript
        if ext == ".json":
            return self.output_config.json
        return True

    def generate_and_save_code_from_object(self, config_obj, main_code, additional_code=None):
        temp_path: str = config_obj.get("temp_path", "")
        if not self._is_allowed(temp_path):
            return
        super().generate_and_save_code_from_object(config_obj, main_code, additional_code)

    def save_code_file(self, file_path: str, content: str) -> None:
        if not self._is_allowed(file_path):
            return
        super().save_code_file(file_path, content)

    def write_to_json(self, path, data, root="temp", clean=True):
        if not self.output_config.json:
            return
        super().write_to_json(path, data, root=root, clean=clean)
