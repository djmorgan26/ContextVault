from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import auth, health

app = FastAPI(
    title="Context Vault API",
    description="Privacy-first personal intelligence system",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(health.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Context Vault API", "version": "0.1.0"}
