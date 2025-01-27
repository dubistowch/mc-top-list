"""
JSON Schema validation for resource data.
"""

import json
from pathlib import Path
from typing import Dict

import jsonschema
from jsonschema import ValidationError

from scraper.utils.logger import setup_logger
from scraper.utils.paths import SCHEMA_DIR


class SchemaValidator:
    """Handles JSON schema validation for resource data"""

    def __init__(self):
        """Initialize the schema validator"""
        self.logger = setup_logger()
        self.schemas: Dict[str, dict] = self._load_schemas()

    def _load_schemas(self) -> Dict[str, dict]:
        """Load all JSON schemas from the schema directory"""
        schemas = {}
        schema_dir = Path(SCHEMA_DIR)
        
        # 確保 schema 目錄存在
        if not schema_dir.exists():
            self.logger.error(f"Schema directory not found: {schema_dir}")
            raise FileNotFoundError(f"Schema directory not found: {schema_dir}")
        
        # 列出所有 schema 檔案
        schema_files = list(schema_dir.glob("*.json"))
        if not schema_files:
            self.logger.error(f"No schema files found in {schema_dir}")
            raise FileNotFoundError(f"No schema files found in {schema_dir}")
        
        # 載入所有 schema
        for schema_file in schema_files:
            schema_name = schema_file.stem
            try:
                with open(schema_file, "r", encoding="utf-8") as f:
                    schemas[schema_name] = json.load(f)
                    self.logger.info(f"Loaded schema: {schema_name}")
            except Exception as e:
                self.logger.error(f"Failed to load schema {schema_file}: {e}")
                raise
        
        return schemas

    def validate(self, data: dict, resource_type: str) -> None:
        """
        Validate resource data against its schema
        
        Args:
            data: The resource data to validate
            resource_type: The type of resource (determines which schema to use)
            
        Raises:
            ValidationError: If the data does not match the schema
        """
        if resource_type not in self.schemas:
            self.logger.error(f"No schema found for resource type: {resource_type}")
            self.logger.error(f"Available schemas: {list(self.schemas.keys())}")
            raise ValueError(f"No schema found for resource type: {resource_type}")
            
        try:
            jsonschema.validate(instance=data, schema=self.schemas[resource_type])
        except ValidationError as e:
            self.logger.error(f"Validation failed for {resource_type}: {e}")
            raise 