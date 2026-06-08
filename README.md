Live Demo

API Documentation:
https://jwt-auth-api-2-6oo7.onrender.com/docs

#  Expense Tracker API

Production-ready backend API built with FastAPI, JWT authentication, SQLAlchemy, and Alembic migrations.

## Features

## Authentication

* JWT Access Tokens
* Refresh Tokens
* Secure Logout
* Password Hashing (bcrypt)
* Protected Routes

## Expense Management

* Create Expenses
* List User Expenses
* User Data Isolation
* Category Tracking

## Analytics

* Total Spending Statistics
* Spending by Category

## Architecture

* FastAPI
* SQLAlchemy ORM
* Alembic Migrations
* Service Layer Pattern
* Modular Project Structure

## Tech Stack

* Python
* FastAPI
* SQLAlchemy
* Alembic
* SQLite (development)
* PostgreSQL Ready
* JWT (python-jose)
* Passlib (bcrypt)
* Docker

## Project Structure

```text
auth/
core/
routers/
services/
alembic/

main.py
database.py
models.py
schemas.py
```

## API Endpoints

## Authentication

| Method | Endpoint |
| ------ | -------- |
| POST   | /login   |
| POST   | /refresh |
| POST   | /logout  |
| GET    | /me      |

### Expenses

| Method | Endpoint  |
| ------ | --------- |
| POST   | /expenses |
| GET    | /expenses |

### Statistics

| Method | Endpoint        |
| ------ | --------------- |
| GET    | /stats/total    |
| GET    | /stats/category |

## Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
uvicorn main:app --reload
```

Open Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## Testing

```bash
pytest
```

## Docker

Build:

```bash
docker build -t expense-api .
```

Run:

```bash
docker run -p 10000:10000 expense-api
```

## Future Improvements

* User Roles (Admin/User)
* Email Verification
* PostgreSQL Production Database
* CI/CD Pipeline
* Automated Test Suite

## Author

Personal backend portfolio project showcasing FastAPI architecture, authentication, and REST API design.

