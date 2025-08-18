# 🧙‍♂️ StackWizard

**Magical Full-Stack Project Generator with Configurable UI**

An interactive command-line tool (CLI) that generates complete full-stack application boilerplates with FastAPI, React, PostgreSQL, and Docker Compose.

## ✨ Features

- **🪄 Interactive CLI**: User-friendly interface with step-by-step configuration
- **🎨 Configurable Frontend**: Choose between Material UI or Tailwind CSS
- **⚡ Complete Backend**: FastAPI with SQLAlchemy, Pydantic, and auto-documentation
- **🐳 Containerization**: Ready-to-use Docker Compose configuration
- **📝 CRUD Examples**: User and item management ready to use
- **📱 Responsive Design**: Mobile-first UI in both variants

## 🏗️ Generated Project Structure

```
your-project/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── api/      # REST API endpoints
│   │   ├── models/   # SQLAlchemy models
│   │   ├── schemas/  # Pydantic schemas
│   │   └── crud/     # Database operations
│   └── Dockerfile
├── frontend/         # React frontend (Material UI or Tailwind)
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   └── Dockerfile
├── database/         # PostgreSQL initialization
├── docker-compose.yml
└── .env
```

## 🚀 Quick Start

### Installation and Usage

```bash
# Clone or download the generator code
cd stackwizard-cli

# Install dependencies
npm install

# Run the generator
npm start

# Or install globally
npm install -g .
stackwizard
```

### Using the Generated Project

```bash
# Navigate to your generated project
cd your-project-name

# Start all services
docker-compose up -d

# Open in browser
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## 🎯 Available UI Options

### 🎨 Material UI
- Professional Material Design components
- Rich component ecosystem
- Built-in icons and theming
- Perfect for business applications

### 🎯 Tailwind CSS  
- Utility-first CSS framework
- Headless UI for accessibility
- Heroicons for icons
- Maximum styling flexibility

## 📚 Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework
- **SQLAlchemy**: Advanced Python ORM
- **PostgreSQL**: Powerful relational database
- **Pydantic**: Data validation and serialization
- **Uvicorn**: High-performance ASGI server

### Frontend
- **React 18**: Modern UI library
- **React Router v6**: SPA routing
- **Axios**: HTTP client for API calls
- **Material UI v5** or **Tailwind CSS v3**: UI styling

### DevOps
- **Docker & Docker Compose**: Containerization
- **PostgreSQL 15**: Containerized database
- **Hot Reload**: Automatic reloading during development

## 🔧 Development Commands

### Backend (Local)
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend (Local)
```bash
cd frontend
npm install
npm start
```

### Docker (Recommended)
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild containers
docker-compose up -d --build
```

## 📋 Example API Endpoints

The generated backend includes these endpoints:

- `GET /api/health` - Application status
- `GET /api/health/db` - Database status
- `GET /api/users` - List users
- `POST /api/users` - Create user
- `GET /api/items` - List items  
- `POST /api/items` - Create item
- `GET /docs` - Interactive API documentation

## 🎨 UI Examples

### Material UI
- Navigation with AppBar and Menu
- Tables with DataGrid
- Modal dialogs for forms
- Cards for displaying items
- Snackbar for notifications

### Tailwind CSS
- Responsive navigation
- Grid layouts for cards
- Modals with Headless UI
- Utility classes for styling
- Hover and focus states

## 🔐 Environment Configuration

The generator automatically creates `.env` files with configuration:

```env
# Database
DB_NAME=your_project
DB_USER=postgres
DB_PASSWORD=postgres

# API
API_PORT=8000
SECRET_KEY=your-secret-key

# Frontend  
FRONTEND_PORT=3000
REACT_APP_API_URL=http://localhost:8000
```

## 📖 Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **React Documentation**: https://react.dev/
- **Material UI**: https://mui.com/
- **Tailwind CSS**: https://tailwindcss.com/
- **Docker Compose**: https://docs.docker.com/compose/

## 🤝 Contributing

To add new features or fix bugs:

1. Fork the repository
2. Create a feature branch
3. Implement changes
4. Add tests if possible
5. Submit a Pull Request

## 📄 License

MIT License - see LICENSE file for details.

---

**[🇵🇱 Polish README](README_PL.md)** | **[📚 Developer Guide](CLAUDE.md)**