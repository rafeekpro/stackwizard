"""
Integration test to ensure frontend code has no ESLint warnings.
This test is run during project generation to prevent shipping code with warnings.
"""
import subprocess
import json
import os
import sys
from pathlib import Path


def check_eslint_warnings(frontend_path):
    """
    Run ESLint on frontend code and check for warnings/errors.
    Returns tuple (success, warnings_count, errors_count, issues)
    """
    if not os.path.exists(frontend_path):
        return False, 0, 0, ["Frontend directory not found"]
    
    try:
        # Run ESLint with JSON output
        result = subprocess.run(
            ["npx", "eslint", "src", "--format", "json"],
            cwd=frontend_path,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Parse ESLint output
        try:
            results = json.loads(result.stdout or "[]")
        except json.JSONDecodeError:
            return False, 0, 0, ["Failed to parse ESLint output"]
        
        total_warnings = 0
        total_errors = 0
        issues = []
        
        for file_result in results:
            if file_result.get("warningCount", 0) > 0 or file_result.get("errorCount", 0) > 0:
                total_warnings += file_result.get("warningCount", 0)
                total_errors += file_result.get("errorCount", 0)
                
                file_path = Path(file_result["filePath"]).relative_to(Path(frontend_path))
                
                for message in file_result.get("messages", []):
                    severity = "error" if message["severity"] == 2 else "warning"
                    issues.append(
                        f"{severity.upper()}: {file_path}:{message['line']}:{message['column']} - "
                        f"{message['message']} ({message.get('ruleId', 'unknown')})"
                    )
        
        return total_errors == 0 and total_warnings == 0, total_warnings, total_errors, issues
        
    except subprocess.TimeoutExpired:
        return False, 0, 0, ["ESLint check timed out"]
    except Exception as e:
        return False, 0, 0, [f"ESLint check failed: {str(e)}"]


def test_no_eslint_warnings_in_frontend():
    """Test that frontend code has no ESLint warnings or errors."""
    # Get the frontend path relative to this test file
    # This test assumes it's run from the backend directory
    backend_path = Path(__file__).parent.parent
    project_root = backend_path.parent
    frontend_path = project_root / "frontend"
    
    # Skip this test if frontend directory doesn't exist (e.g., when running in template development)
    if not frontend_path.exists():
        import pytest
        pytest.skip("Frontend directory not found - skipping ESLint test (this is normal in template development)")
    
    print(f"\n🔍 Checking ESLint warnings in: {frontend_path}")
    
    success, warnings, errors, issues = check_eslint_warnings(str(frontend_path))
    
    if not success:
        print(f"\n❌ ESLint check failed:")
        print(f"   Warnings: {warnings}")
        print(f"   Errors: {errors}")
        
        if issues:
            print("\n📋 Issues found:")
            for issue in issues[:10]:  # Show first 10 issues
                print(f"   • {issue}")
            if len(issues) > 10:
                print(f"   ... and {len(issues) - 10} more issues")
        
        # This will fail the test
        assert False, f"Frontend has {errors} ESLint errors and {warnings} warnings"
    
    print("✅ No ESLint warnings or errors found in frontend code")


def test_required_eslint_config_exists():
    """Test that ESLint configuration is properly set up."""
    backend_path = Path(__file__).parent.parent
    project_root = backend_path.parent
    frontend_path = project_root / "frontend"
    package_json_path = frontend_path / "package.json"
    
    # Skip this test if frontend directory doesn't exist (e.g., when running in template development)
    if not frontend_path.exists():
        import pytest
        pytest.skip("Frontend directory not found - skipping ESLint config test (this is normal in template development)")
    
    assert package_json_path.exists(), "Frontend package.json not found"
    
    import json
    with open(package_json_path) as f:
        package_data = json.load(f)
    
    # Check for ESLint config
    assert "eslintConfig" in package_data or \
           (frontend_path / ".eslintrc.js").exists() or \
           (frontend_path / ".eslintrc.json").exists(), \
           "No ESLint configuration found"
    
    print("✅ ESLint configuration found")


if __name__ == "__main__":
    # Run tests when script is executed directly
    print("\n" + "=" * 60)
    print("ESLint Warning Detection Test")
    print("=" * 60)
    
    try:
        test_required_eslint_config_exists()
        test_no_eslint_warnings_in_frontend()
        print("\n✨ All ESLint tests passed!")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)