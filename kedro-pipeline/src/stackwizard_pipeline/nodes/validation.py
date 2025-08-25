"""
Validation nodes for StackWizard pipeline
"""
import subprocess
import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Any
import tempfile
import time


def generate_project(generation_params: Dict[str, Any], test_params: Dict[str, Any], validation_params: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a test project using StackWizard CLI"""
    
    # Combine parameters
    params = {
        "generation": generation_params,
        "test": test_params,
        "validation": validation_params
    }
    
    test_dir = tempfile.mkdtemp(prefix="kedro-test-")
    project_name = generation_params["project_name"]
    
    # Create expect script for automation
    expect_script = f"""#!/usr/bin/expect -f
set timeout 30
spawn node {Path.cwd().parent / 'src' / 'index.js'}
expect "What is your project name?"
send "{project_name}\\r"
expect "Choose your UI library"
send "\\r"
expect "Database name:"
send "{params['generation']['database']['name']}\\r"
expect "Database user:"
send "{params['generation']['database']['user']}\\r"
expect "Database password:"
send "{params['generation']['database']['password']}\\r"
expect "API port:"
send "{params['generation']['ports']['api']}\\r"
expect "Frontend port:"
send "{params['generation']['ports']['frontend']}\\r"
expect "Select additional features:"
send "\\r"
expect eof
"""
    
    expect_file = Path(test_dir) / "generate.exp"
    expect_file.write_text(expect_script)
    expect_file.chmod(0o755)
    
    try:
        result = subprocess.run(
            str(expect_file),
            cwd=test_dir,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        return {
            "success": result.returncode == 0,
            "project_path": str(Path(test_dir) / project_name),
            "test_dir": test_dir,
            "output": result.stdout,
            "error": result.stderr
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "test_dir": test_dir
        }


def validate_docker_build(project_info: Dict[str, Any], generation_params: Dict[str, Any], test_params: Dict[str, Any], validation_params: Dict[str, Any]) -> Dict[str, Any]:
    """Build Docker images and validate dependencies"""
    
    # Combine parameters
    params = {
        "generation": generation_params,
        "test": test_params,
        "validation": validation_params
    }
    
    if not project_info.get("success"):
        return {"success": False, "error": "Project generation failed"}
    
    results = {}
    project_path = Path(project_info["project_path"])
    
    for ui_type in test_params["ui_libraries"]:
        frontend_path = project_path / "frontend"
        
        if not frontend_path.exists():
            results[ui_type] = {
                "success": False,
                "error": "Frontend directory not found"
            }
            continue
            
        try:
            # Build Docker image
            build_result = subprocess.run(
                ["docker", "build", "-t", f"kedro-test-{ui_type}", "."],
                cwd=frontend_path,
                capture_output=True,
                text=True,
                timeout=params["test"]["docker"]["build_timeout"]
            )
            
            # Check for dependency errors
            build_output = build_result.stdout + build_result.stderr
            missing_deps = []
            
            for dep in params["validation"]["required_dependencies"].get(ui_type, []):
                if f"Module not found.*{dep}" in build_output or \
                   f"Can't resolve '{dep}'" in build_output:
                    missing_deps.append(dep)
            
            results[ui_type] = {
                "success": build_result.returncode == 0 and not missing_deps,
                "missing_dependencies": missing_deps,
                "build_output": build_output[:1000]  # First 1000 chars
            }
            
        except Exception as e:
            results[ui_type] = {
                "success": False,
                "error": str(e)
            }
    
    return results


def run_container_tests(docker_results: Dict[str, Any], generation_params: Dict[str, Any], test_params: Dict[str, Any], validation_params: Dict[str, Any]) -> Dict[str, Any]:
    """Run containers and check for runtime errors"""
    
    results = {}
    
    for ui_type, build_info in docker_results.items():
        if not build_info.get("success"):
            results[ui_type] = {
                "success": False,
                "error": "Docker build failed"
            }
            continue
            
        container_name = f"kedro-test-container-{ui_type}"
        
        try:
            # Stop any existing container
            subprocess.run(
                ["docker", "stop", container_name],
                capture_output=True,
                timeout=10
            )
            subprocess.run(
                ["docker", "rm", container_name],
                capture_output=True,
                timeout=10
            )
            
            # Run container
            subprocess.run(
                ["docker", "run", "-d", "--name", container_name,
                 "-p", f"{generation_params['ports']['frontend']}:3000",
                 f"kedro-test-{ui_type}"],
                capture_output=True,
                check=True,
                timeout=30
            )
            
            # Wait for container to start
            time.sleep(15)
            
            # Get logs
            logs_result = subprocess.run(
                ["docker", "logs", container_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            logs = logs_result.stdout + logs_result.stderr
            
            # Check for errors
            has_errors = any([
                "Module not found" in logs,
                "Can't resolve" in logs,
                "Failed to compile" in logs
            ])
            
            # Check for successful compilation
            compiled = "Compiled successfully" in logs or "webpack compiled" in logs
            
            # Cleanup
            subprocess.run(["docker", "stop", container_name], capture_output=True)
            subprocess.run(["docker", "rm", container_name], capture_output=True)
            
            results[ui_type] = {
                "success": compiled and not has_errors,
                "has_errors": has_errors,
                "compiled": compiled,
                "logs": logs[:2000]  # First 2000 chars
            }
            
        except Exception as e:
            results[ui_type] = {
                "success": False,
                "error": str(e)
            }
    
    return results


def run_unit_tests(project_info: Dict[str, Any]) -> Dict[str, Any]:
    """Run unit tests on the generated project"""
    
    if not project_info.get("success"):
        return {"success": False, "error": "Project generation failed"}
    
    project_path = Path(project_info["project_path"])
    results = {}
    
    # Test backend
    backend_path = project_path / "backend"
    if backend_path.exists():
        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "-v"],
                cwd=backend_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            results["backend"] = {
                "success": result.returncode == 0,
                "output": result.stdout
            }
        except Exception as e:
            results["backend"] = {"success": False, "error": str(e)}
    
    # Test frontend
    frontend_path = project_path / "frontend"
    if frontend_path.exists():
        try:
            result = subprocess.run(
                ["npm", "test", "--", "--watchAll=false"],
                cwd=frontend_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            results["frontend"] = {
                "success": result.returncode == 0,
                "output": result.stdout
            }
        except Exception as e:
            results["frontend"] = {"success": False, "error": str(e)}
    
    return results


def cleanup_test_artifacts(project_info: Dict[str, Any], *args) -> Dict[str, Any]:
    """Clean up test directories and Docker artifacts
    
    Args:
        project_info: Project information containing paths to clean
        *args: Additional test results (used only to enforce execution order)
    """
    
    cleanup_results = {
        "directories_removed": [],
        "containers_removed": [],
        "images_removed": []
    }
    
    # Remove test directory
    if project_info.get("test_dir"):
        try:
            shutil.rmtree(project_info["test_dir"])
            cleanup_results["directories_removed"].append(project_info["test_dir"])
        except Exception as e:
            cleanup_results["error"] = str(e)
    
    # Remove Docker containers and images
    try:
        # Get all test containers
        result = subprocess.run(
            ["docker", "ps", "-a", "--filter", "name=kedro-test", "--format", "{{.Names}}"],
            capture_output=True,
            text=True
        )
        containers = result.stdout.strip().split('\n')
        
        for container in containers:
            if container:
                subprocess.run(["docker", "rm", "-f", container], capture_output=True)
                cleanup_results["containers_removed"].append(container)
        
        # Remove test images
        result = subprocess.run(
            ["docker", "images", "--filter", "reference=kedro-test-*", "--format", "{{.Repository}}:{{.Tag}}"],
            capture_output=True,
            text=True
        )
        images = result.stdout.strip().split('\n')
        
        for image in images:
            if image and image != ":":
                subprocess.run(["docker", "rmi", "-f", image], capture_output=True)
                cleanup_results["images_removed"].append(image)
                
    except Exception as e:
        cleanup_results["docker_error"] = str(e)
    
    return cleanup_results


def generate_validation_report(
    docker_results: Dict[str, Any],
    container_results: Dict[str, Any],
    test_results: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate comprehensive validation report"""
    
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "summary": {
            "total_tests": 0,
            "passed": 0,
            "failed": 0
        },
        "docker_builds": docker_results,
        "container_tests": container_results,
        "unit_tests": test_results,
        "recommendations": []
    }
    
    # Count results
    for category in [docker_results, container_results, test_results]:
        for test_name, result in category.items():
            report["summary"]["total_tests"] += 1
            if result.get("success"):
                report["summary"]["passed"] += 1
            else:
                report["summary"]["failed"] += 1
    
    # Generate recommendations
    if report["summary"]["failed"] > 0:
        report["recommendations"].append("Fix failing tests before release")
        
        # Check for specific issues
        for ui_type, result in docker_results.items():
            if result.get("missing_dependencies"):
                report["recommendations"].append(
                    f"Install missing dependencies for {ui_type}: {', '.join(result['missing_dependencies'])}"
                )
    
    report["success"] = report["summary"]["failed"] == 0
    
    return report