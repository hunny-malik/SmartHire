from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import logger
from app.database.session import engine, SessionLocal
from app.database.base import Base
from app.database.seed_data import seed_database

# Routers
from app.api.auth import router as auth_router
from app.api.resume import router as resume_router
from app.api.roles import router as roles_router
from app.api.jobs import router as jobs_router
from app.api.skills import router as skills_router
from app.api.interview import router as interview_router
from app.api.reports import router as reports_router
from app.api.metrics import router as metrics_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing SmartHire Database & seeding standardized ontology...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    logger.info("SmartHire API Gateway initialized successfully.")
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="SmartHire: AI-Powered Resume Analysis, Skill Gap Mapping, Job Matching & Bilingual Voice Mock Interview Platform",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers under API_V1_PREFIX
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(resume_router, prefix=settings.API_V1_PREFIX)
app.include_router(roles_router, prefix=settings.API_V1_PREFIX)
app.include_router(jobs_router, prefix=settings.API_V1_PREFIX)
app.include_router(skills_router, prefix=settings.API_V1_PREFIX)
app.include_router(interview_router, prefix=settings.API_V1_PREFIX)
app.include_router(reports_router, prefix=settings.API_V1_PREFIX)
app.include_router(metrics_router, prefix=settings.API_V1_PREFIX)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception occurred at {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected server error occurred. Please try again or contact support."}
    )

@app.get("/")
def root():
    return {
        "service": "SmartHire API Gateway",
        "version": settings.VERSION,
        "status": "online",
        "docs": "/docs"
    }

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "database": "connected"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
