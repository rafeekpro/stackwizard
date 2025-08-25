# StackWizard Kedro Pipeline

Automated validation and testing pipeline for StackWizard project generator using Kedro framework.

## Overview

This Kedro pipeline provides comprehensive testing and validation for StackWizard-generated projects, ensuring:
- Project generation works correctly
- Docker builds succeed without dependency errors
- Containers run without runtime errors
- Unit tests pass
- All configurations are valid

## Installation

```bash
# Install Python dependencies
cd kedro-pipeline
pip install -r requirements.txt
```

## Available Pipelines

### 1. Validation Pipeline (Default)
Full validation including Docker builds and container tests.

```bash
# Run via npm
npm run test:kedro

# Run directly
cd kedro-pipeline
python run_pipeline.py validation

# Run via Make
make kedro-test
```

### 2. Quick Test Pipeline
Fast validation without Docker (unit tests only).

```bash
# Run via npm
npm run test:kedro:quick

# Run directly
cd kedro-pipeline
python run_pipeline.py quick

# Run via Make
make kedro-quick
```

### 3. Release Pipeline
Full validation with release gates.

```bash
# Run via npm
npm run test:kedro:release

# Run directly
cd kedro-pipeline
python run_pipeline.py release

# Run via Make
make kedro-release
```

## Pipeline Nodes

### Validation Pipeline Nodes:
1. **generate_test_project** - Creates a test project using StackWizard CLI
2. **validate_docker_builds** - Builds Docker images and checks for dependency errors
3. **test_docker_containers** - Runs containers and validates runtime behavior
4. **run_unit_tests** - Executes unit tests for backend and frontend
5. **generate_report** - Creates comprehensive validation report
6. **cleanup_artifacts** - Removes test directories and Docker artifacts

### Quick Test Pipeline Nodes:
1. **generate_test_project** - Creates a test project
2. **run_unit_tests** - Runs unit tests only
3. **cleanup_artifacts** - Cleans up test files

## Configuration

### Parameters (conf/base/parameters.yml)
```yaml
test:
  ui_libraries:
    - mui
    - tailwind
  docker:
    build_timeout: 300
    run_timeout: 60

generation:
  project_name: "test-kedro-project"
  database:
    name: "testdb"
    user: "testuser"
    password: "testpass"
```

### Data Catalog (conf/base/catalog.yml)
Defines data inputs/outputs for pipeline nodes.

## Outputs

### Validation Report
Generated at `data/03_primary/validation_report.json`:
```json
{
  "timestamp": "2024-01-15 10:30:00",
  "summary": {
    "total_tests": 10,
    "passed": 10,
    "failed": 0
  },
  "docker_builds": {...},
  "container_tests": {...},
  "unit_tests": {...},
  "success": true
}
```

### Run Summary
Generated at `data/08_reporting/last_run_summary.json` after each run.

## Visualization

Launch Kedro-Viz to visualize the pipeline:
```bash
make kedro-viz
# or
cd kedro-pipeline && kedro viz
```

## Integration with CI/CD

The pipeline is integrated with GitHub Actions:
- Automatically runs on pushes to main/develop
- Runs on pull requests
- Can be manually triggered via workflow dispatch

## Troubleshooting

### Missing Dependencies
```bash
cd kedro-pipeline
pip install -r requirements.txt
```

### Docker Issues
Ensure Docker is running and you have sufficient permissions:
```bash
docker info
```

### Clean Pipeline Outputs
```bash
make kedro-clean
# or
rm -rf kedro-pipeline/data/*
```

## Migration to Airflow

If needed, the pipeline can be converted to Airflow DAGs using:
```bash
pip install kedro-airflow
kedro airflow create
```

This will generate Airflow DAGs in the `airflow_dags/` directory.

## Development

### Adding New Nodes
1. Create node function in `src/stackwizard_pipeline/nodes/`
2. Add node to pipeline in `src/stackwizard_pipeline/pipelines/`
3. Update parameters and catalog as needed

### Custom Hooks
Hooks are defined in `src/stackwizard_pipeline/hooks.py` for:
- Pre/post pipeline execution
- Pre/post node execution
- Error handling

## Support

For issues or questions, please open an issue on GitHub.