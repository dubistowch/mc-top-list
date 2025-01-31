"""Configuration module."""

import yaml
from pathlib import Path

def get_config():
    """Get configuration from YAML file."""
    config_path = Path(__file__).parent / "config.yml"
    with open(config_path) as f:
        return yaml.safe_load(f) 