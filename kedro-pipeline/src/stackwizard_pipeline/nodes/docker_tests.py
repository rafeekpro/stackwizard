"""
Docker and container validation nodes
"""
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, Any, List
import re


def test_docker_compose_validity(project_info: Dict[str, Any]) -> Dict[str, Any]:
    """Validate docker-compose.yml syntax and structure"""
    
    results = {
        "test_name": "docker_compose_validity",
        "success": True,
        "errors": [],
        "warnings": [],
        "services": []
    }
    
    if not project_info.get("success"):
        results["success"] = False
        results["errors"].append("Project generation failed")
        return results
    
    project_path = Path(project_info["project_path"])
    
    try:
        # Validate docker-compose syntax
        result = subprocess.run(
            ["docker", "compose", "config", "--quiet"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            results["success"] = False
            results["errors"].append(f"Invalid docker-compose.yml: {result.stderr}")
            return results
        
        # Get services list
        result = subprocess.run(
            ["docker", "compose", "config", "--services"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            services = result.stdout.strip().split('\n')
            results["services"] = services
            
            # Check for required services
            required_services = ["backend", "frontend", "postgres"]
            missing_services = [s for s in required_services if s not in services]
            
            if missing_services:
                results["errors"].append(f"Missing required services: {missing_services}")
                results["success"] = False
        
    except subprocess.TimeoutExpired:
        results["errors"].append("Docker compose validation timed out")
        results["success"] = False
    except Exception as e:
        results["errors"].append(f"Error validating docker-compose: {str(e)}")
        results["success"] = False
    
    return results


def test_dockerfile_best_practices(project_info: Dict[str, Any]) -> Dict[str, Any]:
    """Check Dockerfiles for best practices"""
    
    results = {
        "test_name": "dockerfile_best_practices",
        "success": True,
        "errors": [],
        "warnings": [],
        "dockerfiles_checked": []
    }
    
    if not project_info.get("success"):
        results["success"] = False
        results["errors"].append("Project generation failed")
        return results
    
    project_path = Path(project_info["project_path"])
    
    # Check backend Dockerfile
    backend_dockerfile = project_path / "backend" / "Dockerfile"
    if backend_dockerfile.exists():
        content = backend_dockerfile.read_text()
        results["dockerfiles_checked"].append("backend/Dockerfile")
        
        # Check for multi-stage build
        if content.count("FROM") < 2:
            results["warnings"].append("Backend Dockerfile should use multi-stage build")
        
        # Check for non-root user
        if "USER" not in content:
            results["warnings"].append("Backend Dockerfile should run as non-root user")
        
        # Check for COPY instead of ADD
        if "ADD " in content and not "ADD http" in content:
            results["warnings"].append("Backend Dockerfile should use COPY instead of ADD")
        
        # Check for specific version tags
        if ":latest" in content:
            results["errors"].append("Backend Dockerfile should not use :latest tag")
            results["success"] = False
        
        # Check for pip cache cleanup
        if "pip install" in content and "--no-cache-dir" not in content:
            results["warnings"].append("Backend Dockerfile should use --no-cache-dir with pip")
    
    # Check frontend Dockerfile
    frontend_dockerfile = project_path / "frontend" / "Dockerfile"
    if frontend_dockerfile.exists():
        content = frontend_dockerfile.read_text()
        results["dockerfiles_checked"].append("frontend/Dockerfile")
        
        # Check for multi-stage build
        if content.count("FROM") < 2:
            results["warnings"].append("Frontend Dockerfile should use multi-stage build")
        
        # Check for production build
        if "npm run build" not in content and "yarn build" not in content:
            results["errors"].append("Frontend Dockerfile should build for production")
            results["success"] = False
        
        # Check for nginx or serve
        if "nginx" not in content.lower() and "serve" not in content.lower():
            results["warnings"].append("Frontend Dockerfile should use nginx or serve for production")
        
        # Check for npm ci instead of npm install
        if "npm install" in content and "npm ci" not in content:
            results["warnings"].append("Frontend Dockerfile should use 'npm ci' for production")
    
    return results


def test_docker_build_success(project_info: Dict[str, Any], test_params: Dict[str, Any]) -> Dict[str, Any]:
    """Test that Docker images can be built successfully"""
    
    results = {
        "test_name": "docker_build_success",
        "success": True,
        "errors": [],
        "warnings": [],
        "images_built": [],
        "build_times": {}
    }
    
    if not project_info.get("success"):
        results["success"] = False
        results["errors"].append("Project generation failed")
        return results
    
    project_path = Path(project_info["project_path"])
    
    # Build backend image
    backend_path = project_path / "backend"
    if backend_path.exists():
        start_time = time.time()
        try:
            result = subprocess.run(
                ["docker", "build", "-t", "test-backend:latest", "."],
                cwd=backend_path,
                capture_output=True,
                text=True,
                timeout=test_params.get("docker", {}).get("build_timeout", 300)
            )
            
            build_time = time.time() - start_time
            results["build_times"]["backend"] = build_time
            
            if result.returncode == 0:
                results["images_built"].append("test-backend:latest")
            else:
                results["errors"].append(f"Backend build failed: {result.stderr[-500:]}")
                results["success"] = False
                
        except subprocess.TimeoutExpired:
            results["errors"].append("Backend Docker build timed out")
            results["success"] = False
        except Exception as e:
            results["errors"].append(f"Backend build error: {str(e)}")
            results["success"] = False
    
    # Build frontend image
    frontend_path = project_path / "frontend"
    if frontend_path.exists():
        start_time = time.time()
        try:
            result = subprocess.run(
                ["docker", "build", "-t", "test-frontend:latest", "."],
                cwd=frontend_path,
                capture_output=True,
                text=True,
                timeout=test_params.get("docker", {}).get("build_timeout", 300)
            )
            
            build_time = time.time() - start_time
            results["build_times"]["frontend"] = build_time
            
            if result.returncode == 0:
                results["images_built"].append("test-frontend:latest")
            else:
                # Check for specific dependency errors
                stderr = result.stderr + result.stdout
                if "Module not found" in stderr or "Can't resolve" in stderr:
                    # Extract the missing module
                    match = re.search(r"Module not found.*?['\"]([^'\"]+)['\"]", stderr)
                    if match:
                        missing_module = match.group(1)
                        results["errors"].append(f"Missing dependency: {missing_module}")
                    else:
                        results["errors"].append("Missing dependencies detected")
                else:
                    results["errors"].append(f"Frontend build failed: {result.stderr[-500:]}")
                results["success"] = False
                
        except subprocess.TimeoutExpired:
            results["errors"].append("Frontend Docker build timed out")
            results["success"] = False
        except Exception as e:
            results["errors"].append(f"Frontend build error: {str(e)}")
            results["success"] = False
    
    # Cleanup built images
    for image in results["images_built"]:
        try:
            subprocess.run(
                ["docker", "rmi", "-f", image],
                capture_output=True,
                timeout=10
            )
        except:
            pass
    
    return results


def test_docker_compose_up(project_info: Dict[str, Any], test_params: Dict[str, Any]) -> Dict[str, Any]:
    """Test that docker-compose can start all services"""
    
    results = {
        "test_name": "docker_compose_up",
        "success": True,
        "errors": [],
        "warnings": [],
        "services_status": {}
    }
    
    if not project_info.get("success"):
        results["success"] = False
        results["errors"].append("Project generation failed")
        return results
    
    project_path = Path(project_info["project_path"])
    project_name = project_path.name.lower().replace("-", "")
    
    try:
        # Start services in detached mode
        result = subprocess.run(
            ["docker", "compose", "-p", f"test-{project_name}", "up", "-d"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            results["errors"].append(f"docker-compose up failed: {result.stderr[-500:]}")
            results["success"] = False
            return results
        
        # Wait for services to start
        time.sleep(15)
        
        # Check service status
        result = subprocess.run(
            ["docker", "compose", "-p", f"test-{project_name}", "ps", "--format", "json"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout:
            try:
                services = json.loads(result.stdout)
                for service in services:
                    service_name = service.get("Service", "unknown")
                    state = service.get("State", "unknown")
                    results["services_status"][service_name] = state
                    
                    if state != "running":
                        results["errors"].append(f"Service {service_name} is not running: {state}")
                        results["success"] = False
            except json.JSONDecodeError:
                # Try parsing line by line
                for line in result.stdout.strip().split('\n'):
                    if line:
                        try:
                            service = json.loads(line)
                            service_name = service.get("Service", "unknown")
                            state = service.get("State", "unknown")
                            results["services_status"][service_name] = state
                            
                            if state != "running":
                                results["errors"].append(f"Service {service_name} is not running: {state}")
                                results["success"] = False
                        except:
                            pass
        
        # Check container logs for errors
        result = subprocess.run(
            ["docker", "compose", "-p", f"test-{project_name}", "logs", "--tail=50"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.stdout:
            logs = result.stdout
            
            # Check for common errors
            error_patterns = [
                "Module not found",
                "Can't resolve",
                "Failed to compile",
                "Connection refused",
                "ECONNREFUSED"
            ]
            
            for pattern in error_patterns:
                if pattern in logs:
                    results["warnings"].append(f"Error pattern found in logs: {pattern}")
        
    except subprocess.TimeoutExpired:
        results["errors"].append("docker-compose operations timed out")
        results["success"] = False
    except Exception as e:
        results["errors"].append(f"Error testing docker-compose: {str(e)}")
        results["success"] = False
    finally:
        # Always cleanup
        try:
            subprocess.run(
                ["docker", "compose", "-p", f"test-{project_name}", "down", "-v"],
                cwd=project_path,
                capture_output=True,
                timeout=30
            )
        except:
            pass
    
    return results