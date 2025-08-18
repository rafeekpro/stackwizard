#!/usr/bin/env python3
"""
Database migration and initialization script
"""
import asyncio
import subprocess
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.db.init_db import init_db

def run_alembic_upgrade():
    """Run alembic upgrade head"""
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("✅ Database migrations completed successfully")
            return True
        else:
            print(f"❌ Migration failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        return False

def run_alembic_revision(message: str, autogenerate: bool = True):
    """Create new migration"""
    cmd = ["alembic", "revision"]
    if autogenerate:
        cmd.append("--autogenerate")
    cmd.extend(["-m", message])
    
    try:
        result = subprocess.run(
            cmd,
            cwd=project_root,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✅ Created migration: {message}")
            print(result.stdout)
            return True
        else:
            print(f"❌ Migration creation failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error creating migration: {e}")
        return False

async def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python scripts/migrate.py upgrade    - Run migrations")
        print("  python scripts/migrate.py init       - Run migrations and initialize DB")
        print("  python scripts/migrate.py revision 'message'  - Create new migration")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "upgrade":
        success = run_alembic_upgrade()
        sys.exit(0 if success else 1)
    
    elif command == "init":
        print("🚀 Running database migrations...")
        if run_alembic_upgrade():
            print("🔧 Initializing database...")
            await init_db()
            print("✅ Database setup complete!")
        else:
            sys.exit(1)
    
    elif command == "revision":
        if len(sys.argv) < 3:
            print("Please provide a migration message")
            sys.exit(1)
        message = sys.argv[2]
        success = run_alembic_revision(message)
        sys.exit(0 if success else 1)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())