"""
Main validation pipeline for StackWizard
"""
from kedro.pipeline import Pipeline, node, pipeline
from stackwizard_pipeline.nodes.validation import (
    generate_project,
    validate_docker_build,
    run_container_tests,
    run_unit_tests,
    cleanup_test_artifacts,
    generate_validation_report
)


def create_validation_pipeline(**kwargs) -> Pipeline:
    """Create the validation pipeline"""
    
    return pipeline(
        [
            node(
                func=generate_project,
                inputs=["params:generation", "params:test", "params:validation"],
                outputs="project_info",
                name="generate_test_project"
            ),
            node(
                func=validate_docker_build,
                inputs=["project_info", "params:generation", "params:test", "params:validation"],
                outputs="docker_build_results",
                name="validate_docker_builds"
            ),
            node(
                func=run_container_tests,
                inputs=["docker_build_results", "params:generation", "params:test", "params:validation"],
                outputs="container_test_results",
                name="test_docker_containers"
            ),
            node(
                func=run_unit_tests,
                inputs="project_info",
                outputs="unit_test_results",
                name="run_unit_tests"
            ),
            node(
                func=generate_validation_report,
                inputs=[
                    "docker_build_results",
                    "container_test_results", 
                    "unit_test_results"
                ],
                outputs="validation_report",
                name="generate_report"
            ),
            node(
                func=cleanup_test_artifacts,
                inputs="project_info",
                outputs="cleanup_results",
                name="cleanup_artifacts"
            )
        ],
        namespace=None,
        inputs=None,
        outputs="validation_report"
    )


def create_quick_test_pipeline(**kwargs) -> Pipeline:
    """Quick validation pipeline (no Docker)"""
    
    return pipeline(
        [
            node(
                func=generate_project,
                inputs=["params:generation", "params:test", "params:validation"],
                outputs="project_info",
                name="generate_test_project"
            ),
            node(
                func=run_unit_tests,
                inputs="project_info",
                outputs="unit_test_results",
                name="run_unit_tests"
            ),
            node(
                func=cleanup_test_artifacts,
                inputs="project_info",
                outputs="cleanup_results",
                name="cleanup_artifacts"
            )
        ],
        namespace=None,
        inputs=None,
        outputs="unit_test_results"
    )


def create_release_pipeline(**kwargs) -> Pipeline:
    """Full release pipeline"""
    
    validation = create_validation_pipeline()
    
    return pipeline(
        validation,
        namespace="release",
        inputs=None,
        outputs="validation_report"
    ) + pipeline(
        [
            node(
                func=lambda report: report["success"],
                inputs="validation_report",
                outputs="validation_passed",
                name="check_validation"
            )
        ]
    )