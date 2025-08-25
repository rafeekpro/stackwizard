"""
Comprehensive test pipeline for StackWizard
"""
from kedro.pipeline import Pipeline, node, pipeline
from typing import Dict, Any
import time
from stackwizard_pipeline.nodes.validation import (
    generate_project,
    cleanup_test_artifacts,
    generate_validation_report
)
from stackwizard_pipeline.nodes.package_tests import (
    test_npm_package_files,
    test_package_installation,
    validate_package_json
)
from stackwizard_pipeline.nodes.structure_tests import (
    test_generated_structure,
    test_file_contents,
    test_gitignore_generation
)
from stackwizard_pipeline.nodes.docker_tests import (
    test_docker_compose_validity,
    test_dockerfile_best_practices,
    test_docker_build_success,
    test_docker_compose_up
)
from stackwizard_pipeline.nodes.e2e_tests import (
    test_health_endpoints,
    test_login_flow,
    test_crud_operations
)


def create_package_test_pipeline(**kwargs) -> Pipeline:
    """Pipeline for testing npm package"""
    
    return pipeline(
        [
            node(
                func=validate_package_json,
                inputs="params:test",
                outputs="package_json_validation",
                name="validate_package_json"
            ),
            node(
                func=test_npm_package_files,
                inputs="params:test",
                outputs="npm_package_test",
                name="test_npm_package"
            ),
            node(
                func=test_package_installation,
                inputs="params:test",
                outputs="package_install_test",
                name="test_package_installation"
            )
        ],
        namespace=None,
        inputs=None,
        outputs=None
    )


def create_structure_test_pipeline(**kwargs) -> Pipeline:
    """Pipeline for testing generated project structure"""
    
    return pipeline(
        [
            node(
                func=generate_project,
                inputs=["params:generation", "params:test", "params:validation"],
                outputs="structure_project_info",
                name="generate_structure_project"
            ),
            node(
                func=test_generated_structure,
                inputs="structure_project_info",
                outputs="structure_test",
                name="test_structure"
            ),
            node(
                func=test_file_contents,
                inputs="structure_project_info",
                outputs="file_contents_test",
                name="test_file_contents"
            ),
            node(
                func=test_gitignore_generation,
                inputs="structure_project_info",
                outputs="gitignore_test",
                name="test_gitignore"
            ),
            node(
                func=cleanup_test_artifacts,
                inputs=["structure_project_info", "structure_test", "file_contents_test", "gitignore_test"],
                outputs="structure_cleanup",
                name="cleanup_structure_test"
            )
        ],
        namespace=None,
        inputs=None,
        outputs=None
    )


def create_docker_test_pipeline(**kwargs) -> Pipeline:
    """Pipeline for testing Docker configuration"""
    
    return pipeline(
        [
            node(
                func=generate_project,
                inputs=["params:generation", "params:test", "params:validation"],
                outputs="docker_project_info",
                name="generate_docker_project"
            ),
            node(
                func=test_docker_compose_validity,
                inputs="docker_project_info",
                outputs="docker_compose_test",
                name="test_docker_compose"
            ),
            node(
                func=test_dockerfile_best_practices,
                inputs="docker_project_info",
                outputs="dockerfile_test",
                name="test_dockerfiles"
            ),
            node(
                func=test_docker_build_success,
                inputs=["docker_project_info", "params:test"],
                outputs="docker_build_test",
                name="test_docker_build"
            ),
            node(
                func=test_docker_compose_up,
                inputs=["docker_project_info", "params:test"],
                outputs="docker_up_test",
                name="test_docker_up"
            ),
            node(
                func=cleanup_test_artifacts,
                inputs=["docker_project_info", "docker_compose_test", "dockerfile_test", "docker_build_test", "docker_up_test"],
                outputs="docker_cleanup",
                name="cleanup_docker_test"
            )
        ],
        namespace=None,
        inputs=None,
        outputs=None
    )


def create_e2e_test_pipeline(**kwargs) -> Pipeline:
    """Pipeline for end-to-end testing"""
    
    return pipeline(
        [
            node(
                func=generate_project,
                inputs=["params:generation", "params:test", "params:validation"],
                outputs="e2e_project_info",
                name="generate_e2e_project"
            ),
            node(
                func=test_health_endpoints,
                inputs=["e2e_project_info", "params:generation"],
                outputs="health_test",
                name="test_health"
            ),
            node(
                func=test_login_flow,
                inputs=["e2e_project_info", "params:generation"],
                outputs="login_test",
                name="test_login"
            ),
            node(
                func=test_crud_operations,
                inputs=["e2e_project_info", "params:generation"],
                outputs="crud_test",
                name="test_crud"
            ),
            node(
                func=cleanup_test_artifacts,
                inputs=["e2e_project_info", "health_test", "login_test", "crud_test"],
                outputs="e2e_cleanup",
                name="cleanup_e2e_test"
            )
        ],
        namespace=None,
        inputs=None,
        outputs=None
    )


def create_full_test_pipeline(**kwargs) -> Pipeline:
    """Complete test pipeline running all tests"""
    
    # Create individual pipelines
    package_tests = create_package_test_pipeline()
    structure_tests = create_structure_test_pipeline()
    docker_tests = create_docker_test_pipeline()
    e2e_tests = create_e2e_test_pipeline()
    
    # Combine all pipelines
    return package_tests + structure_tests + docker_tests + e2e_tests + pipeline(
        [
            node(
                func=aggregate_test_results,
                inputs=[
                    "package_json_validation",
                    "npm_package_test",
                    "package_install_test",
                    "structure_test",
                    "file_contents_test",
                    "gitignore_test",
                    "docker_compose_test",
                    "dockerfile_test",
                    "docker_build_test",
                    "docker_up_test",
                    "health_test",
                    "login_test",
                    "crud_test"
                ],
                outputs="final_test_report",
                name="generate_final_report"
            )
        ]
    )


def aggregate_test_results(*test_results) -> Dict[str, Any]:
    """Aggregate all test results into a final report"""
    
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "summary": {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "warnings": 0
        },
        "test_results": {},
        "failed_tests": [],
        "tests_with_warnings": [],
        "success": True
    }
    
    for result in test_results:
        if isinstance(result, dict):
            test_name = result.get("test_name", "unknown")
            report["test_results"][test_name] = result
            report["summary"]["total_tests"] += 1
            
            if result.get("success"):
                report["summary"]["passed"] += 1
            else:
                report["summary"]["failed"] += 1
                report["failed_tests"].append(test_name)
                report["success"] = False
            
            if result.get("warnings"):
                report["summary"]["warnings"] += len(result["warnings"])
                report["tests_with_warnings"].append(test_name)
    
    return report