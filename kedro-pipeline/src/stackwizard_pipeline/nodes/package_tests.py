"""
NPM Package validation nodes
"""
import subprocess
import json
import os
from pathlib import Path
from typing import Dict, Any, List
import tempfile


def test_npm_package_files(params: Dict[str, Any]) -> Dict[str, Any]:
    """Test that all required files are included in npm package"""
    
    project_root = Path.cwd().parent
    results = {
        "test_name": "npm_package_files",
        "success": True,
        "errors": [],
        "warnings": []
    }
    
    try:
        # Run npm pack to see what would be published
        result = subprocess.run(
            ["npm", "pack", "--dry-run", "--json"],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            results["success"] = False
            results["errors"].append(f"npm pack failed: {result.stderr}")
            return results
            
        # Parse the output
        pack_info = json.loads(result.stdout)
        if pack_info:
            files = pack_info[0].get("files", [])
            file_paths = [f["path"] for f in files]
            
            # Check for required files
            required_files = [
                "src/index.js",
                "templates/common/backend/Dockerfile",
                "templates/common/docker-compose.yml",
                "templates/frontend-mui/package.json",
                "templates/frontend-tailwind/package.json",
                "README.md",
                "LICENSE",
                "package.json"
            ]
            
            missing_files = []
            for req_file in required_files:
                if not any(req_file in path for path in file_paths):
                    missing_files.append(req_file)
            
            if missing_files:
                results["success"] = False
                results["errors"].append(f"Missing required files: {missing_files}")
            
            # Check for files that shouldn't be included
            excluded_patterns = [
                "node_modules",
                ".git",
                ".env",
                "test/",
                "*.test.js",
                ".DS_Store",
                "*.log",
                "kedro-pipeline/"
            ]
            
            unwanted_files = []
            for path in file_paths:
                for pattern in excluded_patterns:
                    if pattern in path:
                        unwanted_files.append(path)
                        break
            
            if unwanted_files:
                results["warnings"].append(f"Unwanted files in package: {unwanted_files[:5]}...")
            
            results["package_size"] = pack_info[0].get("size", 0)
            results["file_count"] = len(file_paths)
            
    except Exception as e:
        results["success"] = False
        results["errors"].append(f"Error testing npm package: {str(e)}")
    
    return results


def test_package_installation(params: Dict[str, Any]) -> Dict[str, Any]:
    """Test that the package can be installed globally"""
    
    results = {
        "test_name": "package_installation",
        "success": True,
        "errors": [],
        "warnings": []
    }
    
    test_dir = tempfile.mkdtemp(prefix="npm-install-test-")
    
    try:
        # Create a test package.json
        package_json = {
            "name": "test-stackwizard-install",
            "version": "1.0.0",
            "dependencies": {}
        }
        
        package_json_path = Path(test_dir) / "package.json"
        package_json_path.write_text(json.dumps(package_json, indent=2))
        
        # Try to install the package
        project_root = Path.cwd().parent
        result = subprocess.run(
            ["npm", "install", str(project_root)],
            cwd=test_dir,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            results["success"] = False
            results["errors"].append(f"Installation failed: {result.stderr}")
        else:
            # Check if the binary is available
            bin_path = Path(test_dir) / "node_modules" / ".bin" / "stackwizard"
            if not bin_path.exists():
                results["success"] = False
                results["errors"].append("Binary 'stackwizard' not found after installation")
            
            # Check if main file is accessible
            main_path = Path(test_dir) / "node_modules" / "@rafeekpro" / "stackwizard" / "src" / "index.js"
            if not main_path.exists():
                results["warnings"].append("Main file not found at expected location")
        
        # Cleanup
        subprocess.run(["rm", "-rf", test_dir], capture_output=True)
        
    except Exception as e:
        results["success"] = False
        results["errors"].append(f"Error testing installation: {str(e)}")
        subprocess.run(["rm", "-rf", test_dir], capture_output=True)
    
    return results


def validate_package_json(params: Dict[str, Any]) -> Dict[str, Any]:
    """Validate package.json configuration"""
    
    results = {
        "test_name": "package_json_validation",
        "success": True,
        "errors": [],
        "warnings": []
    }
    
    try:
        project_root = Path.cwd().parent
        package_json_path = project_root / "package.json"
        
        if not package_json_path.exists():
            results["success"] = False
            results["errors"].append("package.json not found")
            return results
        
        with open(package_json_path) as f:
            package_data = json.load(f)
        
        # Check required fields
        required_fields = ["name", "version", "description", "main", "bin", "scripts", "dependencies"]
        missing_fields = [field for field in required_fields if field not in package_data]
        
        if missing_fields:
            results["success"] = False
            results["errors"].append(f"Missing required fields: {missing_fields}")
        
        # Check bin configuration
        if "bin" in package_data:
            if "stackwizard" not in package_data["bin"]:
                results["errors"].append("Missing 'stackwizard' in bin configuration")
                results["success"] = False
        
        # Check version format
        import re
        if "version" in package_data:
            if not re.match(r'^\d+\.\d+\.\d+', package_data["version"]):
                results["warnings"].append(f"Version format may be invalid: {package_data['version']}")
        
        # Check dependencies
        if "dependencies" in package_data:
            critical_deps = ["inquirer", "chalk", "fs-extra", "commander"]
            missing_deps = [dep for dep in critical_deps if dep not in package_data["dependencies"]]
            if missing_deps:
                results["errors"].append(f"Missing critical dependencies: {missing_deps}")
                results["success"] = False
        
        results["package_name"] = package_data.get("name", "unknown")
        results["package_version"] = package_data.get("version", "unknown")
        
    except Exception as e:
        results["success"] = False
        results["errors"].append(f"Error validating package.json: {str(e)}")
    
    return results