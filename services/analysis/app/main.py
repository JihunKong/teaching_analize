from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import APIKeyHeader
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import datetime
from contextlib import asynccontextmanager

from .routers import analyze, reports
from .models import HealthCheck
from .database import init_db

API_KEY = os.getenv("API_KEY", "development-key")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title="AIBOA Analysis Service",
    description="CBIL 7-level analysis service for classroom teaching evaluation",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key

@app.get("/", tags=["root"])
async def root():
    return {
        "service": "AIBOA Analysis Service",
        "version": "1.0.0",
        "status": "operational",
        "cbil_levels": 7
    }

@app.get("/health", response_model=HealthCheck, tags=["health"])
async def health_check():
    return HealthCheck(
        status="healthy",
        service="analysis",
        timestamp=datetime.utcnow().isoformat()
    )

app.include_router(
    analyze.router,
    prefix="/api/analyze",
    tags=["analysis"],
    dependencies=[Depends(verify_api_key)]
)

app.include_router(
    reports.router,
    prefix="/api/reports",
    tags=["reports"],
    dependencies=[Depends(verify_api_key)]
)

@app.get("/api/cbil/levels", tags=["cbil"])
async def get_cbil_levels():
    """Get CBIL level definitions"""
    return {
        "levels": [
            {
                "level": 1,
                "name": "단순 확인",
                "description": "Simple confirmation - Yes/No answers",
                "examples": ["네", "아니오", "맞아요"],
                "characteristics": "5 words or less, simple acknowledgment"
            },
            {
                "level": 2,
                "name": "사실 회상",
                "description": "Fact recall - Simple information repetition",
                "examples": ["책상입니다", "3 더하기 2는 5입니다"],
                "characteristics": "5-15 words, direct repetition of facts"
            },
            {
                "level": 3,
                "name": "개념 설명",
                "description": "Concept explanation - Restating in own words",
                "examples": ["이것은 물체가 떨어지는 현상을 말해요"],
                "characteristics": "15-30 words, paraphrasing concepts"
            },
            {
                "level": 4,
                "name": "분석적 사고",
                "description": "Analytical thinking - Comparison and classification",
                "examples": ["이 두 개념의 차이점은..."],
                "characteristics": "Compare, contrast, categorize"
            },
            {
                "level": 5,
                "name": "종합적 이해",
                "description": "Comprehensive understanding - Integrating concepts",
                "examples": ["여러 요인들이 함께 작용하여..."],
                "characteristics": "Synthesis, cause-effect relationships"
            },
            {
                "level": 6,
                "name": "평가적 판단",
                "description": "Evaluative judgment - Critical thinking",
                "examples": ["이 방법이 더 효과적인 이유는..."],
                "characteristics": "Evidence-based reasoning, critique"
            },
            {
                "level": 7,
                "name": "창의적 적용",
                "description": "Creative application - Novel solutions",
                "examples": ["새로운 상황에 적용하면..."],
                "characteristics": "Innovation, original thinking"
            }
        ]
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc) if os.getenv("DEBUG") == "true" else "An error occurred"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)