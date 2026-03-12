from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.endpoints import ocr, invoice
from app.core.config import settings
from app.db.base_class import Base
from app.db.session import engine
import os

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

allowed_origins = settings.BACKEND_CORS_ORIGINS or ["*"]
allow_credentials = not ("*" in allowed_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

upload_dir = "uploads"
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)
app.mount("/api/uploads", StaticFiles(directory=upload_dir), name="uploads")

app.include_router(ocr.router, prefix="/api/ocr", tags=["ocr"])
app.include_router(invoice.router, prefix="/api/invoice", tags=["invoice"])

@app.get("/api")
def api_root():
    return {"message": "Welcome to Invoice OCR System"}

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

@app.get("/health")
def health_check_plain():
    return {"status": "healthy"}

# Serve built frontend (Vite) in production deployments.
# Frontend is copied to /app/frontend_dist in Dockerfile.
frontend_dist_dir = os.path.abspath(os.getenv("FRONTEND_DIST_DIR", "/app/frontend_dist"))
try:
    app.mount("/", StaticFiles(directory=frontend_dist_dir, html=True), name="frontend")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa_fallback(full_path: str):
        index_path = os.path.join(frontend_dist_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"detail": "Frontend not built"}
except RuntimeError:
    # Static files directory may not exist in some environments; ignore in that case.
    pass
