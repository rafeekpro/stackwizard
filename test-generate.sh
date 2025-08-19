#!/bin/bash
# Non-interactive project generation for testing

PROJECT_NAME=$1
UI_CHOICE=$2

cat <<EOF | node src/index.js
$PROJECT_NAME
$UI_CHOICE
localhost
5432
testdb
testuser
testpass
8000
3000
EOF

# Check if project was created
if [ -d "$PROJECT_NAME" ]; then
    echo "✅ Project $PROJECT_NAME created successfully"
    exit 0
else
    echo "❌ Failed to create project $PROJECT_NAME"
    exit 1
fi