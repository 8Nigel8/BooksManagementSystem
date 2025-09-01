# A comprehensive book management system built with FastAPI, PostgreSQL, and asynchronous programming.

## Prerequisites

- Python 3.10+

- Docker and Docker Compose

 - pip (Python package manager)

# Installation & Setup
## 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```
## 2. Start Database with Docker Compose
```bash
# Start PostgreSQL container
docker-compose up -d

# Check container status
docker-compose ps

# Stop containers (when needed)
docker-compose down
```
## 3. Start application
```bash
python -m uvicorn app.main:app --reload
```
### The application will be available at: http://localhost:8000

# API Documentation
After starting the application, API documentation is available at:

- Interactive Swagger UI: http://localhost:8000/docs

- ReDoc documentation: http://localhost:8000/redoc