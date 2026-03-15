# Exam Portal - Online Examination System

A Django-based online examination system for conducting timed MCQ tests. Teachers can upload question papers while students can take exams and view their results.

## Overview

This application provides separate authentication flows for students and teachers, enabling:
- **Students**: Browse courses, take timed tests, review scores
- **Teachers**: Upload test files (questions & answers), manage exam schedules

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Django 5.1 |
| Database | MySQL |
| Frontend | HTML5, CSS3, JavaScript |
| Password Security | PBKDF2 (Django default) |

## Installation & Setup

```bash
# Install dependencies
pip install django mysqlclient

# Configure database in moodle/settings.py

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```

## URL Routes

| Route | Description |
|-------|-------------|
| `/` | Student login |
| `/student/register/` | Student signup |
| `/teacher/login/` | Teacher login |
| `/teacher/register/` | Teacher signup |
| `/home/` | Student dashboard |
| `/upload/` | Teacher file upload |
| `/test/<filename>/` | Take exam |
| `/review/<test_id>/` | View results |

## Database Models

- **Login** - Student records (name, password, email, course)
- **TeacherLogin** - Teacher records  
- **Testfiles** - Uploaded test papers (questions, answers, time window)
- **Scores** - Student test scores
- **StudentTestRecord** - Individual test attempts

## Test File Format

**Question file** (Q-files):
```
What is Git?
A version control system
A programming language
A database
An operating system
```

**Answer file** (A-files):
```
A version control system
```

## Security

- Passwords hashed using PBKDF2-SHA256
- CSRF protection enabled
- Session-based authentication
