# Evaluation System - Docker Migration

This branch contains a Dockerized version of the Course Checklist / Evaluation System.  
The application has been configured to run the frontend, backend, and database services inside containers for easier setup and deployment.

---

## 🎯 What's Different in This Version?

This branch introduces a complete Docker-based environment for the system.

Using Docker allows the application to run consistently across different operating systems and development environments with minimal setup.

The following services are containerized:

- Frontend
- Backend API
- PostgreSQL Database

---

## ❓ Why This Migration?

The original version of the project was designed around a cloud-hosted architecture where the frontend, backend, and database services were managed separately.

This version focuses on portability and ease of deployment by allowing the entire system to run locally through Docker.

This setup makes the project:
- Easier to install
- Easier to develop on
- More consistent across machines
- Simpler to deploy and test

The migration also replaces the previous database structure with PostgreSQL, allowing for:
- Proper relational modeling
- Foreign key constraints
- Improved data integrity
- Efficient JOIN operations

---

## 🔗 Repositories

**Original Repository**:  
https://github.com/Shoccio/course_checklist

---

## 🐳 Docker Services

| Service   | Port |
|----------|------|
| Frontend | 3000 |
| Backend  | 8000 |

# 📦 Quick Start

## Prerequisites

Before running the project, install:

- Docker

---

## 🚀 Setup

Run the following commands:

```bash
docker compose up --build

docker compose exec backend alembic revision --autogenerate -m "initial schema"

docker compose exec backend alembic upgrade head

docker compose exec backend python seed.py
```

## 🧹 Reset / Cleanup

Stop containers:
docker compose down

Remove volumes (reset database):
docker compose down -v

## 📚 Documentation

- **[MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md)** - Complete migration documentation

## 🔄 Migration Summary

## 🗄️ Database Changes

- ✅ Firebase Firestore migrated to PostgreSQL
- ✅ NoSQL document collections converted into relational database tables
- ✅ Foreign key relationships implemented for improved data integrity
- ✅ Database indexes added for faster queries and better performance
- ✅ Automatic timestamp handling added for record creation and updates
- ✅ Database schema versioning implemented using Alembic migrations
- ✅ Persistent Docker volumes added for PostgreSQL data storage

---

## 💻 Backend & Application Changes

- ✅ Backend migrated to a containerized Docker environment
- ✅ FastAPI backend integrated with PostgreSQL using SQLAlchemy ORM
- ✅ Authentication and authorization system updated
- ✅ Student, Course, Curriculum, and Program management migrated
- ✅ Database seeding system added for development and testing
- ✅ Docker Compose setup added for multi-container orchestration
- ✅ Frontend production build optimized using Nginx
- ✅ API routing and frontend refresh handling configured for SPA deployment
- ✅ Environment variable support added using `.env` configuration
- ✅ Dependencies and project structure updated

## 🗂️ Database Structure

```
users
├── user_id (PK)
├── hashed_pass
└── role

programs
├── program_id (PK)
├── program_name
└── program_specialization

courses
├── course_id (PK)
├── course_name
├── course_hours
├── course_preq
├── course_sem
├── hours_lab
├── hours_lec
├── units_lab
└── units_lec

students
├── student_id (PK)
├── program_id (FK → programs)
├── f_name, l_name, m_name
├── year
├── status
├── archived
├── evaluated
├── gwa
└── is_transferee

program_course
├── program_id (FK → programs)
├── course_id (FK → courses)
└── sequence
└── PRIMARY KEY(program_id, course_id)

student_courses
├── student_id (FK → students)
├── course_id (FK → courses)
├── grade
└── remark
└── PRIMARY KEY(student_id, course_id)
```

## 🚀 Features

- Student management (CRUD operations)
- Course catalog management
- Program and curriculum management
- Student enrollment management
- Grade recording and GPA calculation
- Student evaluation tracking
- Role-based authentication (admin/student)

## 🔐 Security

- ✅ Database-level constraints and foreign keys used for data integrity
- Service role key required for backend operations
- JWT-based authentication
- Password hashing with bcrypt
- Environment variables for sensitive data

## 🛠️ Technologies Used

### Backend
- FastAPI — Python web framework for building REST APIs
- PostgreSQL — Relational database system
- SQLAlchemy — ORM for database interaction
- Alembic — Database migration and schema versioning
- Pydantic — Data validation and serialization
- PassLib — Password hashing and security utilities
- Python-JOSE — JWT authentication and token handling
- Uvicorn — ASGI server for FastAPI applications

---

### Frontend
- React — Frontend JavaScript library
- React Router — Client-side routing
- Axios — API communication
- React Icons — Icon library for React
- Recharts — Data visualization and chart components

---

### DevOps & Deployment
- Docker — Containerization platform
- Docker Compose — Multi-container orchestration
- Nginx — Frontend production server and reverse proxy

---

### Database & Development Tools
- PostgreSQL Volumes — Persistent database storage
- Environment Variables (`.env`) — Configuration management
- Git & GitHub — Version control and repository management

## 📌 API Structure Overview

- /auth → Authentication
- /student → Student management
- /SC → Student's Courses management
- /course → Course management
- /curriculum → Curriculum management
- /currCourse → Curriculum course mapping
- /program → Program management

## 📝 API Endpoints


## 🔐 Authentication

- `POST /login` - Authenticate user and return JWT token + profile
- `POST /edit-password/{username}` - Change password for a user
- `POST /reset-student-password/{student_id}` - Reset student password to default
- `DELETE /delete-user/{username}` - Delete a user account

---

## 🛠️ Admin Management

- `POST /admin/create` - Create a new admin user
- `PUT /admin-update/{username}` - Update an existing admin user
- `DELETE /admin-delete/{username}` - Delete an admin user
- `GET /admins/search` - Search admins by name or username
- `GET /admin/{name}` - Get admin details by name or username

### Students

- `POST /add` - Add a new student
- `PUT /edit` - Edit student information
- `DELETE /delete/{student_id}` - Delete a student
- `GET /search` - Search students with optional filters
- `GET /get/{student_id}` - Get student details by ID
- `GET /get_all` - Retrieve all students
- `GET /filter/{key}/{value}` - Filter students by specific field and value
- `POST /edit_filter/{key}/{value}` - Edit active student filters
- `PUT /reset_filter` - Reset all student filters
- `POST /evaluate/{student_id}` - Evaluate a student
- `POST /take_off_evaluation/{student_id}` - Remove student from evaluation
- `POST /bulk-upload` - Upload students using CSV file
- `PATCH /archive` - Archive a student
- `PATCH /unarchive` - Unarchive a student

## 📚 Courses

- `GET /getAll` - Retrieve all courses
- `POST /add` - Add a new course
- `PUT /edit/{course_id}` - Edit an existing course
- `DELETE /delete/{course_id}` - Delete a course
- `PUT /update/{program_id}` - Update courses under a specific program
- `GET /get/{program_id}` - Get all courses by program ID

### Programs
- `GET /programs` - List all programs

## 🎓 Curriculum

- `GET /get/{program_id}` - Get curriculum by program ID
- `POST /add` - Add a new curriculum
- `DELETE /delete` - Delete a curriculum
- `PATCH /archive` - Archive a curriculum
- `PATCH /unarchive` - Unarchive a curriculum
- `PUT /toggleArchive` - Toggle archive status for curriculum records

## 📘 Curriculum Courses

- `GET /get_courses?program=&curriculum=` - Get courses under a specific program and curriculum
- `POST /add-course` - Add a course to a curriculum
- `POST /delete-course` - Remove a course from a curriculum
- `POST /reorder-courses` - Reorder courses within a curriculum

### Grades
- `POST /grades` - Update student grades
- `PUT /grades/bulk` - Bulk update grades

## 🤝 Contributing

If you'd like to contribute:
1. Fork this repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project maintains the same license as the original repository.

## 🙏 Acknowledgments

- Original project by [Shoccio](https://github.com/Shoccio)
- Migrated to Supabase by Kenaine
- Configured to Docker by [Shoccio]

---
