# RecallAI

RecallAI is an AI-powered study platform that generates structured study guides from any topic.

Users can generate summaries, key concepts, flashcards, and quizzes with AI, then save and manage their study material through a personal account.

### Live Demo

https://recallai-51ba.onrender.com/

> **Note:** RecallAI is hosted on Render's free tier. The initial load may take up to a minute while the server wakes from inactivity.

![RecallAI Dashboard](screenshots/Screenshot%20%281289%29.png)

## About

RecallAI was built as a full-stack project to explore how AI can be integrated into a complete web application rather than used as a standalone tool.

The application combines a FastAPI backend, relational database, user authentication, and the Google Gemini API to generate and persist personalized study material.

## Features

- AI-generated study guides
- Summaries and key concepts
- Flashcards
- Quiz questions
- User registration and login
- Saved study guides
- Search saved material
- Edit and delete saved guides
- Secure per-user data
- Persistent production storage

## Tech Stack

**Frontend:** HTML, CSS, JavaScript

**Backend:** Python, FastAPI

**Database:** PostgreSQL (production), SQLite (local development)

**ORM:** SQLAlchemy

**AI:** Google Gemini

**Authentication:** JWT, Argon2 password hashing

**Testing:** pytest

**Deployment:** Render

**CI:** GitHub Actions

## How It Works

RecallAI follows a client-server architecture:

```text
Browser
   ↓
HTML / CSS / JavaScript
   ↓
HTTP requests + JSON
   ↓
FastAPI REST API
   ↓
Application services
   ↓
SQLAlchemy
   ↓
PostgreSQL / SQLite
```

For AI generation:

```text
User enters a topic
        ↓
Frontend sends request to FastAPI
        ↓
Backend sends request to Google Gemini
        ↓
Gemini generates structured study material
        ↓
FastAPI returns the result as JSON
        ↓
Frontend displays the study guide
```

Generated material is not automatically stored. Users can choose to save a study guide, which persists it to their account in the database.

## Screenshots

### Dashboard

![RecallAI Dashboard](screenshots/Screenshot%20%281289%29.png)

### AI-Generated Study Guide

![RecallAI Generated Study Guide](screenshots/Screenshot%20%281290%29.png)

### Saved Study Guides

![RecallAI Saved Study Guides](screenshots/Screenshot%20%281291%29.png)

### Account

![RecallAI Account](screenshots/Screenshot%20%281292%29.png)

## API & Backend

RecallAI uses FastAPI to expose REST endpoints for authentication, AI generation, and study-guide management.

The backend is separated into routes, services, and repositories to keep HTTP handling, application logic, and database operations organized.

Core operations include:

- Registering and authenticating users
- Generating study material
- Creating and retrieving saved guides
- Searching saved guides
- Editing saved guides
- Deleting saved guides
- Restricting data access to the authenticated owner

## Authentication & Security

RecallAI uses JWT-based authentication.

Passwords are hashed with Argon2 before being stored. After a successful login, the backend issues a signed JWT that identifies the authenticated user for protected requests.

Protected endpoints verify the token and enforce ownership so users can access and modify only their own study guides.

Sensitive configuration such as the Gemini API key, database connection string, and JWT secret is stored in environment variables and is not committed to the repository.

## Database

RecallAI uses a relational database managed through SQLAlchemy.

SQLite is used during local development, while the deployed application uses PostgreSQL on Render.

The database stores users, saved topics, flashcards, and quiz questions, with relationships connecting generated study material to its owner.

## Testing & CI

RecallAI includes **39 automated tests** using pytest.

The test suite covers backend behavior and uses isolated test databases without accessing production credentials or the live Gemini API.

GitHub Actions runs the complete test suite automatically when code is pushed to `main` or when a pull request targets `main`.

A failed test causes the CI workflow to report a failed check, helping catch regressions before changes are considered ready.

## Deployment

RecallAI is deployed on Render.

The production environment uses:

- Render Web Service for the FastAPI application
- Render PostgreSQL for persistent data
- Environment variables for production secrets and configuration
- Automatic deployments from the GitHub `main` branch

The deployment exposes the frontend and API from the same FastAPI application.

## Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/MagdDoleh/RecallAI.git
cd RecallAI
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root and configure the required environment variables.

Use `.env.example` as a reference.

Do not commit your `.env` file.

### 5. Start RecallAI

```bash
uvicorn backend.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000
```

## Testing

Install the development dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

Run the test suite:

```bash
python -m pytest
```

## Project Status

RecallAI's core application is complete and deployed.

Current functionality includes AI study-guide generation, authentication, persistent user data, CRUD operations, automated testing, continuous integration, and production deployment.
