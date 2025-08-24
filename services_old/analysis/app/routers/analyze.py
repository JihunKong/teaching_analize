from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
import uuid
from datetime import datetime

from ..database import get_db, create_analysis, get_analysis, update_analysis_results
from ..services.cbil_analyzer import CBILAnalyzer
from ..services.solar_llm import SolarLLMService
from ..models import AnalysisRequest, AnalysisResponse, CBILAnalysisResult

router = APIRouter()

# Initialize services
cbil_analyzer = CBILAnalyzer()
solar_service = SolarLLMService()

@router.post("/cbil", response_model=AnalysisResponse)
async def analyze_transcript(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Analyze transcript for CBIL levels
    """
    # Generate analysis ID
    analysis_id = str(uuid.uuid4())
    
    # Create analysis record
    analysis = create_analysis(
        db=db,
        analysis_id=analysis_id,
        transcript_id=request.transcript_id,
        teacher_name=request.teacher_name,
        subject=request.subject,
        grade_level=request.grade_level
    )
    
    # Start analysis in background
    background_tasks.add_task(
        perform_cbil_analysis,
        analysis_id,
        request.transcript_text,
        request.language
    )
    
    return AnalysisResponse(
        analysis_id=analysis_id,
        status="processing",
        message="Analysis started. Check status endpoint for results."
    )

async def perform_cbil_analysis(
    analysis_id: str,
    transcript_text: str,
    language: str = "ko"
):
    """
    Perform CBIL analysis on transcript
    """
    try:
        # Analyze with CBIL analyzer
        cbil_result = await cbil_analyzer.analyze(transcript_text, language)
        
        # Get recommendations from Solar LLM
        recommendations = await solar_service.get_recommendations(
            cbil_result,
            transcript_text
        )
        
        # Update database with results
        db = next(get_db())
        update_analysis_results(
            db=db,
            analysis_id=analysis_id,
            cbil_distribution=cbil_result.level_distribution,
            average_cbil_level=cbil_result.average_level,
            teacher_talk_ratio=cbil_result.teacher_talk_ratio,
            student_talk_ratio=cbil_result.student_talk_ratio,
            detailed_analysis=cbil_result.to_dict(),
            recommendations=recommendations
        )
        
    except Exception as e:
        # Log error and update status
        print(f"Analysis failed for {analysis_id}: {str(e)}")
        # Update database with error status
        pass

@router.get("/status/{analysis_id}")
async def get_analysis_status(
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """
    Get analysis status and results
    """
    analysis = get_analysis(db, analysis_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return analysis.to_dict()

@router.post("/batch")
async def batch_analyze(
    transcripts: list[AnalysisRequest],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Analyze multiple transcripts
    """
    analysis_ids = []
    
    for request in transcripts:
        analysis_id = str(uuid.uuid4())
        
        # Create analysis record
        create_analysis(
            db=db,
            analysis_id=analysis_id,
            transcript_id=request.transcript_id,
            teacher_name=request.teacher_name,
            subject=request.subject,
            grade_level=request.grade_level
        )
        
        # Start analysis in background
        background_tasks.add_task(
            perform_cbil_analysis,
            analysis_id,
            request.transcript_text,
            request.language
        )
        
        analysis_ids.append(analysis_id)
    
    return {
        "message": f"Started {len(analysis_ids)} analyses",
        "analysis_ids": analysis_ids
    }