#!/usr/bin/env python3
"""
CLI wrapper for running StackWizard Kedro pipelines
"""
import sys
import argparse
import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def run_pipeline(pipeline_name="__default__", env="local", params=None):
    """Run a Kedro pipeline
    
    Args:
        pipeline_name: Name of the pipeline to run
        env: Environment to use for configuration
        params: Additional parameters to pass
    """
    cmd = ["kedro", "run", "--pipeline", pipeline_name, "--env", env]
    
    if params:
        for key, value in params.items():
            cmd.extend(["--params", f"{key}={value}"])
    
    logger.info(f"Running pipeline: {pipeline_name}")
    logger.info(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, cwd=Path(__file__).parent, check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        logger.error(f"Pipeline failed with error: {e}")
        return 1
    except FileNotFoundError:
        logger.error("Kedro not found. Please install with: pip install -r requirements.txt")
        return 1


def main():
    parser = argparse.ArgumentParser(description="Run StackWizard validation pipelines")
    parser.add_argument(
        "pipeline",
        choices=["validation", "quick", "release"],
        nargs="?",
        default="validation",
        help="Pipeline to run (default: validation)"
    )
    parser.add_argument(
        "--env",
        default="local",
        help="Environment configuration (default: local)"
    )
    parser.add_argument(
        "--ui",
        choices=["mui", "tailwind", "all"],
        default="all",
        help="UI library to test (default: all)"
    )
    parser.add_argument(
        "--skip-docker",
        action="store_true",
        help="Skip Docker build and run tests"
    )
    parser.add_argument(
        "--project-name",
        default="test-kedro-project",
        help="Name for test project generation"
    )
    
    args = parser.parse_args()
    
    # Map arguments to parameters
    params = {}
    if args.ui != "all":
        params["test.ui_libraries"] = f"[{args.ui}]"
    if args.skip_docker:
        params["test.docker.enabled"] = "false"
    if args.project_name:
        params["generation.project_name"] = args.project_name
    
    # Run the pipeline
    exit_code = run_pipeline(args.pipeline, args.env, params)
    
    if exit_code == 0:
        logger.info("✅ Pipeline completed successfully")
    else:
        logger.error("❌ Pipeline failed")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())