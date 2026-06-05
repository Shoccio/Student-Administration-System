# Student Administration System

A modern, self-hosted course management and student evaluation platform built for educational institutions. Administrators manage courses, curricula, and student evaluations, while students can view their enrolled courses and progress.

This is a fully containerized fork of the original system, enabling self-hosting on any infrastructure while maintaining cloud deployment options.

---

## ✨ Features

- **Admin Dashboard**: Manage students, courses, curricula, and program structures
- **Student Portal**: Students log in to view their courses and progress
- **Relational Database**: PostgreSQL-backed with proper data integrity and foreign key constraints
- **Authentication**: Secure credential management with role-based access control
- **Self-Hosted**: Run entirely on your own infrastructure with Docker
- **Cloud Ready**: Easy deployment to Render, Railway, or any container platform
- **API-Driven**: RESTful backend for extensibility and integration

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React with modern JavaScript |
| **Backend** | Python FastAPI with SQLAlchemy ORM |
| **Database** | PostgreSQL with Alembic migrations |
| **DevOps** | Docker & Docker Compose |
| **Deployment** | Self-hosted (Docker), Render, Railway |

---

## � Quick Start

### Prerequisites

- Docker & Docker Compose

### Setup (Local Docker)

```bash
# Start all services
docker compose up --build

# Initialize database
docker compose exec backend alembic upgrade head

# Seed initial data
docker compose exec backend python seed.py
```

Access the application:
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000

### Reset Database

```bash
# Stop containers
docker compose down

# Remove volumes and reset database
docker compose down -v
```

---

## 🚀 Deployment Options

| Option | Use Case |
|--------|----------|
| **Docker (Local)** | Development, self-hosted on your infrastructure |
| **Render** | Cloud deployment with automated builds (original setup) |
| **Railway** | Simple cloud hosting with environment management |

Configuration files: `render.yaml`, `railway.json`

---

## 🗂️ Project Structure

```
├── backend/              # FastAPI application
│   ├── models/          # SQLAlchemy ORM models
│   ├── routes/          # API endpoints
│   ├── functions/       # Business logic
│   ├── db/              # Database configuration
│   ├── alembic/         # Database migrations
│   └── requirements.txt
│
├── frontend/            # React application
│   ├── src/
│   │   ├── pages/       # Page components
│   │   ├── component/   # Reusable components
│   │   └── lib/         # Utilities & API client
│   └── package.json
│
├── docker-compose.yml   # Multi-environment compose setup
└── docs/               # Setup guides and migration docs
```

---

## 📚 Documentation

- **[MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md)** — Database schema changes and migration details
- **[AUTH_SETUP.md](./backend/AUTH_SETUP.md)** — Authentication configuration
- **[CREATE_ADMIN.md](./backend/CREATE_ADMIN.md)** — Creating admin accounts
- **[SETUP_CHECKLIST.md](./backend/SETUP_CHECKLIST.md)** — Deployment checklist

---

## 🔑 Key Implementation Details

- **RESTful API**: FastAPI backend with structured route organization (auth, students, courses, curricula, programs)
- **Data Integrity**: PostgreSQL with foreign key constraints and relational modeling
- **Authentication**: JWT-based auth with role-based access control (admin/student)
- **Database Versioning**: Alembic migrations for schema management and reproducible deployments
- **Component Architecture**: Modular functions, models, and routes for maintainability

---

## 📌 Acknowledgments

**Original Project**: [course_checklist](https://github.com/Shoccio/course_checklist)

This fork modernizes the deployment architecture through containerization while maintaining the core functionality for educational institution administration.
