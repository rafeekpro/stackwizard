"""
Project hooks for StackWizard pipeline
"""
from kedro.framework.hooks import hook_impl
from kedro.pipeline import Pipeline
import logging
import time
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class ProjectHooks:
    """Custom hooks for StackWizard pipeline"""
    
    @hook_impl
    def before_pipeline_run(self, run_params, pipeline, catalog):
        """Hook to run before pipeline execution"""
        logger.info("=" * 60)
        logger.info("StackWizard Validation Pipeline Starting")
        logger.info(f"Pipeline: {run_params.get('pipeline_name', 'default')}")
        logger.info(f"Start time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)
        
        # Create output directories if they don't exist
        data_dirs = [
            "data/01_raw",
            "data/02_intermediate", 
            "data/03_primary",
            "data/04_feature",
            "data/05_model_input",
            "data/06_models",
            "data/07_model_output",
            "data/08_reporting"
        ]
        
        for dir_path in data_dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    @hook_impl
    def after_pipeline_run(self, run_params, run_result, pipeline, catalog):
        """Hook to run after pipeline execution"""
        logger.info("=" * 60)
        logger.info("Pipeline Execution Complete")
        logger.info(f"End time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Save summary report
        if run_result:
            summary_path = Path("data/08_reporting/last_run_summary.json")
            summary = {
                "pipeline": run_params.get("pipeline_name", "default"),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "success": True,
                "outputs": list(run_result.keys()) if run_result else []
            }
            summary_path.write_text(json.dumps(summary, indent=2))
            logger.info(f"Summary saved to {summary_path}")
        
        logger.info("=" * 60)
    
    @hook_impl
    def on_pipeline_error(self, error, run_params, pipeline, catalog):
        """Hook to run on pipeline error"""
        logger.error("=" * 60)
        logger.error("Pipeline Execution Failed!")
        logger.error(f"Error: {error}")
        logger.error(f"Pipeline: {run_params.get('pipeline_name', 'default')}")
        logger.error("=" * 60)
        
        # Save error report
        error_path = Path("data/08_reporting/last_error.json")
        error_report = {
            "pipeline": run_params.get("pipeline_name", "default"),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "error": str(error),
            "error_type": type(error).__name__
        }
        error_path.parent.mkdir(parents=True, exist_ok=True)
        error_path.write_text(json.dumps(error_report, indent=2))
    
    @hook_impl
    def before_node_run(self, node, catalog, inputs, is_async):
        """Hook to run before each node"""
        logger.info(f"Running node: {node.name}")
        logger.debug(f"Inputs: {list(inputs.keys())}")
    
    @hook_impl
    def after_node_run(self, node, catalog, outputs, is_async):
        """Hook to run after each node"""
        logger.info(f"✓ Completed node: {node.name}")
        logger.debug(f"Outputs: {list(outputs.keys())}")
    
    @hook_impl
    def on_node_error(self, error, node, catalog, inputs, is_async):
        """Hook to run on node error"""
        logger.error(f"✗ Node failed: {node.name}")
        logger.error(f"Error: {error}")