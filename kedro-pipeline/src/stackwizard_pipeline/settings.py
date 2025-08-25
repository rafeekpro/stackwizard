"""
Settings for StackWizard Kedro project
"""
from pathlib import Path
from kedro.config import OmegaConfigLoader
from stackwizard_pipeline.hooks import ProjectHooks

# Project settings
PROJECT_NAME = "stackwizard_pipeline"
PACKAGE_NAME = "stackwizard_pipeline"
PROJECT_VERSION = "0.1.0"

# Hooks configuration
HOOKS = (ProjectHooks(),)

# Config loader settings
CONFIG_LOADER_CLASS = OmegaConfigLoader
CONFIG_LOADER_ARGS = {
    "base_env": "base",
    "default_run_env": "local",
}

# Data catalog settings  
from kedro.io import DataCatalog
DATA_CATALOG_CLASS = DataCatalog