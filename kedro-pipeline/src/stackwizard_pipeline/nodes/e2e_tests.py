"""
End-to-end testing nodes
"""
import subprocess
import time
import json
from pathlib import Path
from typing import Dict, Any
import requests
from requests.exceptions import RequestException


def test_health_endpoints(project_info: Dict[str, Any], generation_params: Dict[str, Any]) -> Dict[str, Any]:
    """Test health check endpoints"""
    
    results = {
        "test_name": "health_endpoints",
        "success": True,
        "errors": [],
        "warnings": [],
        "endpoints_tested": []
    }
    
    if not project_info.get("success"):
        results["success"] = False
        results["errors"].append("Project generation failed")
        return results
    
    project_path = Path(project_info["project_path"])
    project_name = project_path.name.lower().replace("-", "")
    api_port = generation_params.get("ports", {}).get("api", 8000)
    frontend_port = generation_params.get("ports", {}).get("frontend", 3000)
    
    try:
        # Start services
        subprocess.run(
            ["docker", "compose", "-p", f"test-{project_name}", "up", "-d"],
            cwd=project_path,
            capture_output=True,
            timeout=120
        )
        
        # Wait for services to start
        time.sleep(20)
        
        # Test backend health endpoint
        try:
            response = requests.get(f"http://localhost:{api_port}/health", timeout=5)
            results["endpoints_tested"].append("/health")
            
            if response.status_code == 200:
                data = response.json()
                if not data.get("status") == "healthy":
                    results["warnings"].append("Health endpoint returned but status not 'healthy'")
            else:
                results["errors"].append(f"Health endpoint returned {response.status_code}")
                results["success"] = False
                
        except RequestException as e:
            results["errors"].append(f"Cannot reach health endpoint: {str(e)}")
            results["success"] = False
        
        # Test API docs endpoint
        try:
            response = requests.get(f"http://localhost:{api_port}/docs", timeout=5)
            results["endpoints_tested"].append("/docs")
            
            if response.status_code != 200:
                results["warnings"].append(f"API docs endpoint returned {response.status_code}")
                
        except RequestException as e:
            results["warnings"].append(f"Cannot reach docs endpoint: {str(e)}")
        
        # Test frontend
        try:
            response = requests.get(f"http://localhost:{frontend_port}", timeout=5)
            results["endpoints_tested"].append("frontend")
            
            if response.status_code == 200:
                if "<div id=\"root\">" not in response.text:
                    results["warnings"].append("Frontend response missing React root element")
            else:
                results["errors"].append(f"Frontend returned {response.status_code}")
                results["success"] = False
                
        except RequestException as e:
            results["errors"].append(f"Cannot reach frontend: {str(e)}")
            results["success"] = False
        
    except Exception as e:
        results["errors"].append(f"Error during health check: {str(e)}")
        results["success"] = False
    finally:
        # Cleanup
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


def test_login_flow(project_info: Dict[str, Any], generation_params: Dict[str, Any]) -> Dict[str, Any]:
    """Test user login flow"""
    
    results = {
        "test_name": "login_flow",
        "success": True,
        "errors": [],
        "warnings": [],
        "steps_completed": []
    }
    
    if not project_info.get("success"):
        results["success"] = False
        results["errors"].append("Project generation failed")
        return results
    
    project_path = Path(project_info["project_path"])
    project_name = project_path.name.lower().replace("-", "")
    api_port = generation_params.get("ports", {}).get("api", 8000)
    
    try:
        # Start services
        subprocess.run(
            ["docker", "compose", "-p", f"test-{project_name}", "up", "-d"],
            cwd=project_path,
            capture_output=True,
            timeout=120
        )
        
        # Wait for services
        time.sleep(20)
        
        # Test user registration
        register_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
        
        try:
            response = requests.post(
                f"http://localhost:{api_port}/api/users/register",
                json=register_data,
                timeout=5
            )
            
            if response.status_code in [200, 201]:
                results["steps_completed"].append("user_registration")
            else:
                results["warnings"].append(f"Registration returned {response.status_code}")
                
        except RequestException as e:
            results["warnings"].append(f"Registration failed: {str(e)}")
        
        # Test user login
        login_data = {
            "username": "test@example.com",
            "password": "testpassword123"
        }
        
        try:
            response = requests.post(
                f"http://localhost:{api_port}/api/users/login",
                data=login_data,  # Form data for OAuth2
                timeout=5
            )
            
            if response.status_code == 200:
                results["steps_completed"].append("user_login")
                data = response.json()
                
                if "access_token" in data:
                    results["steps_completed"].append("token_received")
                    token = data["access_token"]
                    
                    # Test authenticated endpoint
                    headers = {"Authorization": f"Bearer {token}"}
                    response = requests.get(
                        f"http://localhost:{api_port}/api/users/me",
                        headers=headers,
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        results["steps_completed"].append("authenticated_request")
                    else:
                        results["warnings"].append("Could not access authenticated endpoint")
                else:
                    results["warnings"].append("Login response missing access_token")
            else:
                results["errors"].append(f"Login failed with status {response.status_code}")
                results["success"] = False
                
        except RequestException as e:
            results["errors"].append(f"Login request failed: {str(e)}")
            results["success"] = False
        
    except Exception as e:
        results["errors"].append(f"Error during login flow test: {str(e)}")
        results["success"] = False
    finally:
        # Cleanup
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


def test_crud_operations(project_info: Dict[str, Any], generation_params: Dict[str, Any]) -> Dict[str, Any]:
    """Test CRUD operations for items"""
    
    results = {
        "test_name": "crud_operations",
        "success": True,
        "errors": [],
        "warnings": [],
        "operations_tested": []
    }
    
    if not project_info.get("success"):
        results["success"] = False
        results["errors"].append("Project generation failed")
        return results
    
    project_path = Path(project_info["project_path"])
    project_name = project_path.name.lower().replace("-", "")
    api_port = generation_params.get("ports", {}).get("api", 8000)
    
    try:
        # Start services
        subprocess.run(
            ["docker", "compose", "-p", f"test-{project_name}", "up", "-d"],
            cwd=project_path,
            capture_output=True,
            timeout=120
        )
        
        # Wait for services
        time.sleep(20)
        
        # First, login to get token
        login_data = {
            "username": "admin@example.com",
            "password": "admin123"
        }
        
        token = None
        try:
            response = requests.post(
                f"http://localhost:{api_port}/api/users/login",
                data=login_data,
                timeout=5
            )
            
            if response.status_code == 200:
                token = response.json().get("access_token")
        except:
            pass
        
        if not token:
            # Try to register first
            register_data = {
                "email": "admin@example.com",
                "password": "admin123",
                "full_name": "Admin User"
            }
            
            try:
                requests.post(
                    f"http://localhost:{api_port}/api/users/register",
                    json=register_data,
                    timeout=5
                )
                
                # Try login again
                response = requests.post(
                    f"http://localhost:{api_port}/api/users/login",
                    data=login_data,
                    timeout=5
                )
                
                if response.status_code == 200:
                    token = response.json().get("access_token")
            except:
                pass
        
        if token:
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test CREATE
            item_data = {
                "title": "Test Item",
                "description": "Test Description",
                "price": 99.99
            }
            
            try:
                response = requests.post(
                    f"http://localhost:{api_port}/api/items/",
                    json=item_data,
                    headers=headers,
                    timeout=5
                )
                
                if response.status_code in [200, 201]:
                    results["operations_tested"].append("CREATE")
                    created_item = response.json()
                    item_id = created_item.get("id")
                    
                    # Test READ
                    response = requests.get(
                        f"http://localhost:{api_port}/api/items/{item_id}",
                        headers=headers,
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        results["operations_tested"].append("READ")
                    
                    # Test UPDATE
                    update_data = {"title": "Updated Item"}
                    response = requests.put(
                        f"http://localhost:{api_port}/api/items/{item_id}",
                        json=update_data,
                        headers=headers,
                        timeout=5
                    )
                    
                    if response.status_code == 200:
                        results["operations_tested"].append("UPDATE")
                    
                    # Test DELETE
                    response = requests.delete(
                        f"http://localhost:{api_port}/api/items/{item_id}",
                        headers=headers,
                        timeout=5
                    )
                    
                    if response.status_code in [200, 204]:
                        results["operations_tested"].append("DELETE")
                        
                else:
                    results["warnings"].append(f"Create item failed: {response.status_code}")
                    
            except RequestException as e:
                results["warnings"].append(f"CRUD operations failed: {str(e)}")
        else:
            results["warnings"].append("Could not obtain auth token for CRUD tests")
        
        if len(results["operations_tested"]) < 4:
            results["success"] = False
            results["errors"].append("Not all CRUD operations succeeded")
        
    except Exception as e:
        results["errors"].append(f"Error during CRUD test: {str(e)}")
        results["success"] = False
    finally:
        # Cleanup
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