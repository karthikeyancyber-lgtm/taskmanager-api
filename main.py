from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.db.database import init_db
from backend.routers import auth, tasks
import os

app = FastAPI(
    title="Task Manager API",
    description="A simple Task Manager built with FastAPI — by Karthikeyan S",
    version="1.0.0",
)

# CORS — allow frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(tasks.router)

# Serve frontend static files
frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

    @app.get("/", include_in_schema=False)
    def serve_frontend():
        return FileResponse(os.path.join(frontend_dir, "index.html"))


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "Task Manager API is running"}


@app.on_event("startup")
def on_startup():
    init_db()
