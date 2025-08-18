# 🧙‍♂️ StackWizard

**Generator Projektów Full-Stack z Konfigurowalnym UI**

Interaktywne narzędzie wiersza poleceń (CLI) do generowania kompletnych szkieletów aplikacji full-stack z FastAPI, React, PostgreSQL i Docker Compose.

## ✨ Funkcje

- **Interactive CLI**: Przyjazny dla użytkownika interfejs z konfiguracją krok po kroku
- **Konfigurowalny Frontend**: Wybór między Material UI lub Tailwind CSS
- **Kompletny Backend**: FastAPI z SQLAlchemy, Pydantic i automatyczną dokumentacją
- **Konteneryzacja**: Gotowa konfiguracja Docker Compose
- **Przykłady CRUD**: Zarządzanie użytkownikami i elementami gotowe do użycia
- **Responsywny Design**: Mobile-first UI w obu wariantach

## 🏗️ Struktura Wygenerowanego Projektu

```
your-project/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── api/      # REST API endpoints
│   │   ├── models/   # SQLAlchemy models
│   │   ├── schemas/  # Pydantic schemas
│   │   └── crud/     # Database operations
│   └── Dockerfile
├── frontend/         # React frontend (Material UI lub Tailwind)
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── services/
│   └── Dockerfile
├── database/         # PostgreSQL initialization
├── docker-compose.yml
└── .env
```

## 🚀 Szybki Start

### Instalacja i Uruchomienie

```bash
# Sklonuj lub pobierz kod generatora
cd stackwizard-cli

# Zainstaluj zależności
npm install

# Uruchom generator
npm start

# Lub zainstaluj globalnie
npm install -g .
stackwizard
```

### Używanie Wygenerowanego Projektu

```bash
# Przejdź do wygenerowanego projektu
cd your-project-name

# Uruchom wszystkie usługi
docker-compose up -d

# Otwórz w przeglądarce
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## 🎯 Dostępne Opcje UI

### 🎨 Material UI
- Profesjonalne komponenty Material Design
- Rozbudowany system komponentów
- Wbudowane ikony i style
- Ideal dla aplikacji biznesowych

### 🎯 Tailwind CSS  
- Utility-first CSS framework
- Headless UI dla dostępności
- Heroicons dla ikon
- Maksymalna elastyczność stylowania

## 📚 Stos Technologiczny

### Backend
- **FastAPI**: Nowoczesny, szybki framework web
- **SQLAlchemy**: Zaawansowany ORM Python
- **PostgreSQL**: Potężna relacyjna baza danych
- **Pydantic**: Walidacja danych i serializacja
- **Uvicorn**: Serwer ASGI o wysokiej wydajności

### Frontend
- **React 18**: Nowoczesna biblioteka UI
- **React Router v6**: Routing dla SPA
- **Axios**: HTTP client dla API
- **Material UI v5** lub **Tailwind CSS v3**: Style UI

### DevOps
- **Docker & Docker Compose**: Konteneryzacja
- **PostgreSQL 15**: Baza danych w kontenerze
- **Hot Reload**: Automatyczne przeładowanie podczas rozwoju

## 🔧 Komendy Deweloperskie

### Backend (Lokalne)
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend (Lokalne)
```bash
cd frontend
npm install
npm start
```

### Docker (Zalecane)
```bash
# Uruchom wszystkie usługi
docker-compose up -d

# Wyświetl logi
docker-compose logs -f

# Zatrzymaj usługi
docker-compose down

# Przebuduj kontenery
docker-compose up -d --build
```

## 📋 Przykładowe API Endpoints

Wygenerowany backend zawiera następujące endpoint:

- `GET /api/health` - Status aplikacji
- `GET /api/health/db` - Status bazy danych
- `GET /api/users` - Lista użytkowników
- `POST /api/users` - Tworzenie użytkownika
- `GET /api/items` - Lista elementów  
- `POST /api/items` - Tworzenie elementu
- `GET /docs` - Interaktywna dokumentacja API

## 🎨 Przykłady Interfejsu

### Material UI
- Nawigacja z AppBar i Menu
- Tabele z DataGrid
- Modal dialogi dla formularzy
- Cards dla wyświetlania elementów
- Snackbar dla powiadomień

### Tailwind CSS
- Responsywna nawigacja
- Grid layout dla kart
- Modal z Headless UI
- Utility classes dla stylowania
- Hover i focus states

## 🔐 Konfiguracja Środowiska

Generator automatycznie tworzy pliki `.env` z konfiguracją:

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

## 📖 Dodatkowe Zasoby

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **React Documentation**: https://react.dev/
- **Material UI**: https://mui.com/
- **Tailwind CSS**: https://tailwindcss.com/
- **Docker Compose**: https://docs.docker.com/compose/

## 🤝 Wkład w Projekt

Aby dodać nowe funkcje lub naprawić błędy:

1. Forkuj repozytorium
2. Stwórz branch dla funkcji
3. Zaimplementuj zmiany
4. Dodaj testy jeśli to możliwe
5. Wyślij Pull Request

## 📄 Licencja

MIT License - zobacz plik LICENSE dla szczegółów.