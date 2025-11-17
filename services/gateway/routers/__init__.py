"""
Service routers for API Gateway
"""

from .transcription import router as transcription_router
from .analysis import router as analysis_router
from .evaluation import router as evaluation_router
from .reporting import router as reporting_router
from .workflows import router as workflows_router

__all__ = [
    "transcription_router",
    "analysis_router",
    "evaluation_router",
    "reporting_router",
    "workflows_router"
]
