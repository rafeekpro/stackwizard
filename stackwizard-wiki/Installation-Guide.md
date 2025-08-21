# 📦 Installation Guide

Complete step-by-step guide for installing and setting up StackWizard CLI and generated projects.

## 📋 Prerequisites

### System Requirements

| Component | Minimum Version | Recommended Version | Check Command |
|-----------|----------------|-------------------|---------------|
| **Node.js** | 16.0.0 | 18.0.0+ | `node --version` |
| **npm** | 7.0.0 | 9.0.0+ | `npm --version` |
| **Docker** | 20.10.0 | 24.0.0+ | `docker --version` |
| **Docker Compose** | 2.0.0 | 2.20.0+ | `docker compose version` |
| **Git** | 2.0.0 | 2.40.0+ | `git --version` |
| **Python** | 3.9 | 3.11+ | `python --version` |

### Operating System Support

- ✅ **macOS** (10.15+)
- ✅ **Linux** (Ubuntu 20.04+, Debian 11+, Fedora 35+)
- ✅ **Windows** (10/11 with WSL2)

## 🚀 StackWizard CLI Installation

### Method 1: NPM Global Installation (Recommended)

```bash
# Install globally from NPM
npm install -g @rafeekpro/stackwizard

# Verify installation
stackwizard --version

# Run the CLI
stackwizard
```

### Method 2: NPX (No Installation)

```bash
# Run directly without installation
npx @rafeekpro/stackwizard

# Or create a project directly
npx @rafeekpro/stackwizard my-project
```

### Method 3: GitHub Packages

```bash
# Configure npm for GitHub Packages
npm config set @rafeekpro:registry https://npm.pkg.github.com

# Install from GitHub Packages
npm install -g @rafeekpro/stackwizard

# Run the CLI
stackwizard
```

### Method 4: From Source

```bash
# Clone the repository
git clone https://github.com/rafeekpro/stackwizard.git
cd stackwizard

# Install dependencies
npm install

# Run locally
npm start

# Or install globally from source
npm install -g .
```

## 🎯 Creating Your First Project

### Interactive Mode

```bash
# Run the CLI
stackwizard

# You'll be prompted for:
# 1. Project name
# 2. UI framework (Material-UI or Tailwind CSS)
# 3. Database configuration
# 4. Port settings
# 5. Git initialization
# 6. Dependency installation
```

### Command Line Mode

```bash
# Create project with options
stackwizard \
  --name my-awesome-app \
  --ui mui \
  --db-name myapp_db \
  --db-user myapp_user \
  --db-password secure_password \
  --api-port 8000 \
  --frontend-port 3000 \
  --install

# Quick mode with defaults
stackwizard --quick --name my-app
```

### Available CLI Options

```bash
Options:
  -V, --version           Output version number
  -n, --name <name>       Project name
  -u, --ui <ui>           UI library (mui or tailwind)
  --db-name <name>        Database name
  --db-user <user>        Database username
  --db-password <pass>    Database password
  --api-port <port>       Backend API port (default: 8000)
  --frontend-port <port>  Frontend port (default: 3000)
  -s, --skip-git          Skip git initialization
  -i, --install           Install dependencies after creation
  -q, --quick             Quick mode - use all defaults
  -h, --help              Display help
```

## 🐳 Docker & Docker Compose Setup

### Installing Docker

#### macOS
```bash
# Using Homebrew
brew install --cask docker

# Or download Docker Desktop from:
# https://www.docker.com/products/docker-desktop
```

#### Ubuntu/Debian
```bash
# Update package index
sudo apt-get update

# Install prerequisites
sudo apt-get install ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Set up repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in for group changes to take effect
```

#### Windows (WSL2)
```powershell
# Install Docker Desktop for Windows
# Download from: https://www.docker.com/products/docker-desktop

# Enable WSL2
wsl --install

# Set WSL2 as default
wsl --set-default-version 2

# Install Ubuntu from Microsoft Store
# Then follow Ubuntu instructions inside WSL2
```

### Verifying Docker Installation

```bash
# Check Docker
docker --version
docker run hello-world

# Check Docker Compose
docker compose version

# Check Docker daemon
docker info
```

## 🏃 Running the Generated Project

### Step 1: Navigate to Project

```bash
cd my-awesome-app
```

### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env  # or use your preferred editor
```

### Step 3: Start with Docker Compose

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Step 4: Initialize Database

```bash
# Run database migrations
docker-compose exec backend alembic upgrade head

# Create superuser (optional)
docker-compose exec backend python -c "
from app.core.database import SessionLocal
from app.crud.crud_user import user as crud_user
from app.schemas.user import UserCreate
db = SessionLocal()
superuser = UserCreate(
    email='admin@example.com',
    username='admin',
    password='admin123',
    is_superuser=True
)
crud_user.create(db, obj_in=superuser)
"
```

## 💻 Local Development Setup (Without Docker)

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://user:password@localhost/dbname"
export SECRET_KEY="your-secret-key"

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Set environment variables
export REACT_APP_API_URL="http://localhost:8000"

# Start development server
npm start

# Build for production
npm run build
```

### Database Setup (PostgreSQL)

```bash
# Install PostgreSQL
# macOS:
brew install postgresql
brew services start postgresql

# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql

# Create database and user
sudo -u postgres psql
CREATE DATABASE myapp_db;
CREATE USER myapp_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE myapp_db TO myapp_user;
\q
```

## 🔧 Troubleshooting Installation

### Common Issues and Solutions

#### Issue: Permission Denied (npm)
```bash
# Fix npm permissions
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

#### Issue: Docker Daemon Not Running
```bash
# Start Docker daemon
# macOS: Open Docker Desktop app
# Linux:
sudo systemctl start docker
sudo systemctl enable docker
```

#### Issue: Port Already in Use
```bash
# Find process using port
lsof -i :8000  # or :3000

# Kill process
kill -9 <PID>

# Or change ports in .env file
```

#### Issue: Database Connection Failed
```bash
# Check PostgreSQL is running
docker-compose ps

# Check database logs
docker-compose logs db

# Test connection
docker-compose exec db psql -U myapp_user -d myapp_db
```

#### Issue: Node Version Mismatch
```bash
# Install Node Version Manager (nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Install and use correct Node version
nvm install 18
nvm use 18
```

## 🔍 Verification Steps

### 1. Check CLI Installation
```bash
stackwizard --version
# Should output: 1.0.0 or higher
```

### 2. Check Generated Project Structure
```bash
# List project files
ls -la my-awesome-app/

# Should contain:
# - backend/
# - frontend/
# - docker-compose.yml
# - .env
# - README.md
```

### 3. Check Running Services
```bash
# Check Docker containers
docker-compose ps

# Should show:
# - my-awesome-app_db_1       (running)
# - my-awesome-app_backend_1  (running)
# - my-awesome-app_frontend_1 (running)
```

### 4. Test API Endpoints
```bash
# Health check
curl http://localhost:8000/health

# API documentation
open http://localhost:8000/docs
```

### 5. Test Frontend
```bash
# Open in browser
open http://localhost:3000

# Check console for errors
# Open Developer Tools (F12)
```

## 📝 Post-Installation Steps

1. **Update Environment Variables**
   - Set secure SECRET_KEY
   - Configure database credentials
   - Set production URLs

2. **Initialize Git Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

3. **Set Up CI/CD**
   - Configure GitHub Actions
   - Set up deployment pipeline

4. **Configure Production Settings**
   - SSL certificates
   - Domain configuration
   - Environment-specific configs

5. **Install Additional Dependencies**
   ```bash
   # Backend
   pip install celery redis  # For background tasks
   
   # Frontend
   npm install @sentry/react  # For error tracking
   ```

## 🚢 Production Deployment

### Using Docker Compose
```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale backend=3
```

### Environment Variables for Production
```env
# Production .env
NODE_ENV=production
DATABASE_URL=postgresql://prod_user:prod_pass@prod_db:5432/prod_db
SECRET_KEY=<generated-secret-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ORIGINS=https://yourdomain.com
```

---

**Next**: [Configuration](Configuration) →