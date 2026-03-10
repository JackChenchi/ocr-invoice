# OCR Batch Processing System

An intelligent batch image processing system based on FastAPI, Vue 3, Celery, and Tesseract OCR.

## Features

- **Batch Upload**: Drag and drop support for multiple images.
- **Async Processing**: Uses Celery + Redis for reliable background task processing.
- **Real-time Status**: Auto-refreshing task list to show processing progress.
- **OCR Engine**: Powered by Tesseract-OCR with support for English and Chinese.
- **Containerized**: Full Docker support for easy deployment.

## Architecture

- **Frontend**: Vue 3, Element Plus, Vite, Nginx
- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Worker**: Celery, Redis
- **Database**: MySQL 8.0
- **OCR**: Tesseract-OCR

## Quick Start (Docker)

1. **Prerequisites**: Ensure Docker and Docker Compose are installed.
2. **Run**:
   ```bash
   docker compose up --build
   ```
3. **Access**: Open [http://localhost](http://localhost)

## Local Development (Manual Setup)

### Prerequisites
- Python 3.11+
- Node.js 18+
- MySQL 8.0
- Redis
- Tesseract-OCR (must be in PATH)

### Backend Setup
1. `cd backend`
2. `pip install -r requirements.txt`
3. Configure `.env` (copy from example or use defaults)
4. Start API: `uvicorn app.main:app --reload`
5. Start Worker: `celery -A app.core.celery_app worker --loglevel=info -P eventlet`

### Frontend Setup
1. `cd frontend`
2. `npm install`
3. `npm run dev`

## API Documentation

Once backend is running, visit:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## License

MIT
