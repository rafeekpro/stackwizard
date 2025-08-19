#!/usr/bin/env python
"""Fix async auth tests to use sync version"""
import re

with open('tests/test_auth.py', 'r') as f:
    content = f.read()

# Replace async markers and functions
replacements = [
    # Remove @pytest.mark.asyncio decorators from test_authenticate methods
    (r'@pytest.mark.asyncio\n(\s+)async def (test_authenticate_[^(]+)', r'\1def \2'),
    
    # Replace await AuthService with AuthServiceSync
    (r'await AuthService\.authenticate_user', r'AuthServiceSync.authenticate_user'),
    (r'AuthService\.get_password_hash', r'AuthServiceSync.get_password_hash'),
    
    # Fix the indentation issues
    (r'    @pytest.mark.asyncio\n    async def (test_authenticate)', r'    def \1'),
]

for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content)

with open('tests/test_auth.py', 'w') as f:
    f.write(content)

print("Fixed auth tests!")