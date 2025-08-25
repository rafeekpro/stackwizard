"""
Project structure validation nodes
"""
import subprocess
import os
from pathlib import Path
from typing import Dict, Any, List
import json


def test_generated_structure(project_info: Dict[str, Any]) -> Dict[str, Any]:
    """Test the structure of generated projects"""
    
    results = {
        "test_name": "generated_structure",
        "success": True,
        "errors": [],
        "warnings": [],
        "checked_paths": []
    }
    
    if not project_info.get("success"):
        results["success"] = False
        results["errors"].append("Project generation failed - cannot test structure")
        return results
    
    project_path = Path(project_info["project_path"])
    
    # Define expected structure
    expected_structure = {
        "backend": {
            "type": "directory",
            "required_files": [
                "Dockerfile",
                "requirements.txt",
                "app/main.py",
                "app/models/user.py",
                "app/models/item.py",
                "app/api/users.py",
                "app/api/items.py",
                "app/api/health.py",
                "app/core/config.py",
                "app/db/database.py",
                "alembic.ini",
                "alembic/env.py"
            ]
        },
        "frontend": {
            "type": "directory",
            "required_files": [
                "Dockerfile",
                "package.json",
                "src/index.js",
                "src/App.js",
                "src/components/Navbar.js",
                "src/pages/HomePage.js",
                "src/pages/LoginPage.js",
                "src/services/api.js",
                "public/index.html"
            ]
        },
        "database": {
            "type": "directory",
            "required_files": [
                "init.sql"
            ]
        },
        "root_files": [
            "docker-compose.yml",
            ".env",
            "README.md"
        ]
    }
    
    # Check backend structure
    backend_path = project_path / "backend"
    if not backend_path.exists():
        results["errors"].append("Backend directory missing")
        results["success"] = False
    else:
        for file_path in expected_structure["backend"]["required_files"]:
            full_path = backend_path / file_path
            if not full_path.exists():
                results["errors"].append(f"Missing backend file: {file_path}")
                results["success"] = False
            else:
                results["checked_paths"].append(str(full_path))
    
    # Check frontend structure
    frontend_path = project_path / "frontend"
    if not frontend_path.exists():
        results["errors"].append("Frontend directory missing")
        results["success"] = False
    else:
        for file_path in expected_structure["frontend"]["required_files"]:
            full_path = frontend_path / file_path
            if not full_path.exists():
                results["errors"].append(f"Missing frontend file: {file_path}")
                results["success"] = False
            else:
                results["checked_paths"].append(str(full_path))
    
    # Check database structure
    database_path = project_path / "database"
    if not database_path.exists():
        results["errors"].append("Database directory missing")
        results["success"] = False
    else:
        for file_path in expected_structure["database"]["required_files"]:
            full_path = database_path / file_path
            if not full_path.exists():
                results["errors"].append(f"Missing database file: {file_path}")
                results["success"] = False
            else:
                results["checked_paths"].append(str(full_path))
    
    # Check root files
    for file_name in expected_structure["root_files"]:
        full_path = project_path / file_name
        if not full_path.exists():
            results["errors"].append(f"Missing root file: {file_name}")
            results["success"] = False
        else:
            results["checked_paths"].append(str(full_path))
    
    results["total_files_checked"] = len(results["checked_paths"])
    results["total_errors"] = len(results["errors"])
    
    return results


def test_file_contents(project_info: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the contents of key generated files"""
    
    results = {
        "test_name": "file_contents",
        "success": True,
        "errors": [],
        "warnings": [],
        "validations": []
    }
    
    if not project_info.get("success"):
        results["success"] = False
        results["errors"].append("Project generation failed - cannot test file contents")
        return results
    
    project_path = Path(project_info["project_path"])
    
    # Check docker-compose.yml
    docker_compose_path = project_path / "docker-compose.yml"
    if docker_compose_path.exists():
        content = docker_compose_path.read_text()
        
        # Check for required services
        required_services = ["backend", "frontend", "postgres"]
        for service in required_services:
            if f"{service}:" not in content:
                results["errors"].append(f"Service '{service}' not found in docker-compose.yml")
                results["success"] = False
        
        results["validations"].append("docker-compose.yml")
    
    # Check .env file
    env_path = project_path / ".env"
    if env_path.exists():
        content = env_path.read_text()
        
        # Check for required environment variables
        required_vars = [
            "DATABASE_URL",
            "POSTGRES_DB",
            "POSTGRES_USER",
            "POSTGRES_PASSWORD",
            "JWT_SECRET_KEY",
            "REACT_APP_API_URL"
        ]
        
        for var in required_vars:
            if f"{var}=" not in content:
                results["errors"].append(f"Missing environment variable: {var}")
                results["success"] = False
        
        results["validations"].append(".env")
    
    # Check backend main.py
    main_py_path = project_path / "backend" / "app" / "main.py"
    if main_py_path.exists():
        content = main_py_path.read_text()
        
        # Check for FastAPI setup
        if "FastAPI" not in content:
            results["errors"].append("FastAPI not imported in main.py")
            results["success"] = False
        
        if "app = FastAPI" not in content:
            results["errors"].append("FastAPI app not initialized in main.py")
            results["success"] = False
        
        # Check for CORS middleware
        if "CORSMiddleware" not in content:
            results["warnings"].append("CORS middleware not configured")
        
        results["validations"].append("backend/app/main.py")
    
    # Check frontend package.json
    frontend_package_path = project_path / "frontend" / "package.json"
    if frontend_package_path.exists():
        try:
            with open(frontend_package_path) as f:
                package_data = json.load(f)
            
            # Check for required dependencies
            deps = package_data.get("dependencies", {})
            required_deps = ["react", "react-dom", "react-router-dom", "axios"]
            
            for dep in required_deps:
                if dep not in deps:
                    results["errors"].append(f"Missing frontend dependency: {dep}")
                    results["success"] = False
            
            # Check for UI library specific deps
            if "@mui/material" in deps:
                results["validations"].append("MUI dependencies found")
            elif "tailwindcss" in deps or "tailwindcss" in package_data.get("devDependencies", {}):
                results["validations"].append("Tailwind dependencies found")
            else:
                results["warnings"].append("No UI library dependencies detected")
            
            results["validations"].append("frontend/package.json")
            
        except Exception as e:
            results["errors"].append(f"Error parsing frontend package.json: {str(e)}")
            results["success"] = False
    
    results["total_validations"] = len(results["validations"])
    
    return results


def test_gitignore_generation(project_info: Dict[str, Any]) -> Dict[str, Any]:
    """Test that .gitignore is properly generated"""
    
    results = {
        "test_name": "gitignore_generation",
        "success": True,
        "errors": [],
        "warnings": []
    }
    
    if not project_info.get("success"):
        results["success"] = False
        results["errors"].append("Project generation failed")
        return results
    
    project_path = Path(project_info["project_path"])
    gitignore_path = project_path / ".gitignore"
    
    if not gitignore_path.exists():
        # It's ok if .gitignore doesn't exist (user might not select it)
        results["warnings"].append(".gitignore not generated (might not be selected)")
        return results
    
    content = gitignore_path.read_text()
    
    # Check for essential patterns
    essential_patterns = [
        "node_modules",
        ".env",
        "__pycache__",
        "*.pyc",
        ".DS_Store",
        "*.log",
        "dist/",
        "build/"
    ]
    
    missing_patterns = []
    for pattern in essential_patterns:
        if pattern not in content:
            missing_patterns.append(pattern)
    
    if missing_patterns:
        results["warnings"].append(f"Missing patterns in .gitignore: {missing_patterns}")
    
    results["gitignore_lines"] = len(content.splitlines())
    
    return results