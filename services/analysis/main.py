from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, status
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
import os
import uuid
import logging
import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any
import requests
import json

# Local imports
from config import settings
from database import (
    get_db, init_db, AnalysisJob, AnalysisStatus as DBAnalysisStatus,
    UtteranceAnalysis, CBILLevel, SessionLocal
)
from schemas import (
    TextAnalysisRequest,
    TranscriptAnalysisRequest,
    AnalysisJobResponse,
    AnalysisStatusResponse,
    AnalysisResultResponse,
    UtteranceAnalysisResult,
    CBILDistribution,
    ReportResponse,
    StatisticsResponse,
    HealthResponse,
    ErrorResponse,
    AnalysisStatus,
    CBIL_DESCRIPTIONS
)
from auth import verify_api_key, get_optional_api_key
from cbil_analyzer import CBILAnalyzer
from llm_client import SolarLLMClient
from report_generator import ReportGenerator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.SERVICE_NAME,
    version=settings.SERVICE_VERSION,
    description="AI-powered CBIL analysis service for teaching quality assessment",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Initialize services
cbil_analyzer = CBILAnalyzer()
llm_client = SolarLLMClient()
report_generator = ReportGenerator()

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    logger.info(f"{settings.SERVICE_NAME} started on port {settings.PORT}")
    logger.info(f"Storage path: {settings.RAILWAY_VOLUME_PATH}")

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint"""
    return HealthResponse(
        status="healthy",
        service=settings.SERVICE_NAME,
        version=settings.SERVICE_VERSION
    )

@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service=settings.SERVICE_NAME,
        version=settings.SERVICE_VERSION
    )

@app.post("/api/analyze/text", response_model=AnalysisJobResponse)
async def analyze_text(
    request: TextAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Analyze text directly for CBIL levels
    
    - **text**: Korean teaching transcript text
    - **metadata**: Optional metadata
    - **subject**: Subject (국어, 수학, 영어, etc.)
    - **grade**: Grade level
    """
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Create job record
    job = AnalysisJob(
        id=job_id,
        status=DBAnalysisStatus.PENDING,
        text=request.text,
        source_type="text",
        subject=request.subject,
        grade=request.grade,
        teacher_name=request.teacher_name,
        api_key=api_key
    )
    db.add(job)
    db.commit()
    
    # Process in background
    background_tasks.add_task(
        process_text_analysis,
        job_id=job_id,
        text=request.text,
        metadata={
            "subject": request.subject,
            "grade": request.grade,
            "teacher_name": request.teacher_name,
            **(request.metadata or {})
        }
    )
    
    return AnalysisJobResponse(
        job_id=job_id,
        status=AnalysisStatus.PENDING,
        message="Analysis started successfully",
        created_at=job.created_at
    )

@app.post("/api/analyze/transcript", response_model=AnalysisJobResponse)
async def analyze_transcript(
    request: TranscriptAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Analyze transcription result from Transcription Service
    
    - **transcript_job_id**: Job ID from Transcription Service
    - **metadata**: Optional metadata
    - **subject**: Subject
    - **grade**: Grade level
    """
    # Fetch transcript from Transcription Service
    try:
        headers = {"X-API-Key": api_key}
        response = requests.get(
            f"{settings.TRANSCRIPTION_SERVICE_URL}/api/transcripts/{request.transcript_job_id}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to fetch transcript: {response.text}"
            )
        
        transcript_data = response.json()
        text = transcript_data.get("text", "")
        
        if not text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transcript is empty"
            )
    
    except requests.RequestException as e:
        logger.error(f"Failed to fetch transcript: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to connect to Transcription Service"
        )
    
    # Generate job ID
    job_id = str(uuid.uuid4())
    
    # Create job record
    job = AnalysisJob(
        id=job_id,
        status=DBAnalysisStatus.PENDING,
        text=text,
        transcript_job_id=request.transcript_job_id,
        source_type="transcript",
        subject=request.subject,
        grade=request.grade,
        api_key=api_key
    )
    db.add(job)
    db.commit()
    
    # Process in background
    background_tasks.add_task(
        process_text_analysis,
        job_id=job_id,
        text=text,
        metadata={
            "subject": request.subject,
            "grade": request.grade,
            "transcript_data": transcript_data,
            **(request.metadata or {})
        }
    )
    
    return AnalysisJobResponse(
        job_id=job_id,
        status=AnalysisStatus.PENDING,
        message="Transcript analysis started successfully",
        created_at=job.created_at
    )

@app.get("/api/analysis/{job_id}", response_model=AnalysisStatusResponse)
async def get_analysis_status(
    job_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get analysis job status"""
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check API key matches
    if job.api_key != api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return AnalysisStatusResponse(
        job_id=job.id,
        status=AnalysisStatus(job.status.value),
        created_at=job.created_at,
        updated_at=job.updated_at,
        error_message=job.error_message
    )

@app.get("/api/analysis/{job_id}/result", response_model=AnalysisResultResponse)
async def get_analysis_result(
    job_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get completed analysis results"""
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check API key matches
    if job.api_key != api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    if job.status != DBAnalysisStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Analysis not completed. Current status: {job.status.value}"
        )
    
    # Get utterance analyses
    utterances = db.query(UtteranceAnalysis).filter(
        UtteranceAnalysis.job_id == job_id
    ).order_by(UtteranceAnalysis.utterance_number).all()
    
    utterance_results = []
    for utterance in utterances:
        utterance_results.append(UtteranceAnalysisResult(
            utterance_number=utterance.utterance_number,
            text=utterance.text,
            speaker=utterance.speaker,
            cbil_level=utterance.cbil_level,
            cbil_level_name=CBIL_DESCRIPTIONS[utterance.cbil_level],
            confidence=utterance.cbil_confidence,
            reasoning=utterance.cbil_reasoning,
            keywords=utterance.keywords
        ))
    
    # Create distribution
    distribution = CBILDistribution(
        level_1=job.level_1_count,
        level_2=job.level_2_count,
        level_3=job.level_3_count,
        level_4=job.level_4_count,
        level_5=job.level_5_count,
        level_6=job.level_6_count,
        level_7=job.level_7_count
    )
    
    return AnalysisResultResponse(
        job_id=job.id,
        status=AnalysisStatus.COMPLETED,
        total_utterances=job.total_utterances,
        average_cbil_level=job.average_level or 0,
        cbil_distribution=distribution,
        utterances=utterance_results,
        statistics=job.statistics or {},
        processing_time=job.processing_time or 0,
        report_available=bool(job.report_path)
    )

@app.get("/api/reports/{job_id}")
async def get_analysis_report(
    job_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Download PDF analysis report"""
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check API key matches
    if job.api_key != api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    if job.status != DBAnalysisStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Analysis not completed"
        )
    
    if not job.report_path or not os.path.exists(job.report_path):
        # Generate report if not exists
        report_path = await generate_report(job_id, db)
        job.report_path = report_path
        db.commit()
    else:
        report_path = job.report_path
    
    filename = f"analysis_report_{job_id}.pdf"
    
    return FileResponse(
        path=report_path,
        media_type="application/pdf",
        filename=filename
    )

@app.get("/api/statistics", response_model=StatisticsResponse)
async def get_statistics(
    db: Session = Depends(get_db),
    api_key: Optional[str] = Depends(get_optional_api_key)
):
    """Get analysis statistics dashboard"""
    # Get total counts
    total_analyses = db.query(AnalysisJob).filter(
        AnalysisJob.status == DBAnalysisStatus.COMPLETED
    ).count()
    
    total_utterances = db.query(UtteranceAnalysis).count()
    
    # Calculate average CBIL by subject
    subjects = ["국어", "수학", "영어", "과학", "사회"]
    avg_by_subject = {}
    
    for subject in subjects:
        jobs = db.query(AnalysisJob).filter(
            AnalysisJob.subject == subject,
            AnalysisJob.status == DBAnalysisStatus.COMPLETED
        ).all()
        
        if jobs:
            avg_level = sum(j.average_level or 0 for j in jobs) / len(jobs)
            avg_by_subject[subject] = round(avg_level, 2)
    
    # Get recent trends (last 7 days)
    from datetime import timedelta
    week_ago = datetime.now() - timedelta(days=7)
    recent_jobs = db.query(AnalysisJob).filter(
        AnalysisJob.created_at >= week_ago,
        AnalysisJob.status == DBAnalysisStatus.COMPLETED
    ).all()
    
    daily_counts = {}
    for job in recent_jobs:
        date = job.created_at.date().isoformat()
        daily_counts[date] = daily_counts.get(date, 0) + 1
    
    return StatisticsResponse(
        total_analyses=total_analyses,
        total_utterances=total_utterances,
        average_cbil_by_subject=avg_by_subject,
        recent_trends={"daily_analyses": daily_counts}
    )

# Background processing functions
async def process_text_analysis(job_id: str, text: str, metadata: Dict[str, Any]):
    """Process text analysis in background"""
    db = SessionLocal()
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    
    if not job:
        logger.error(f"Job {job_id} not found")
        return
    
    try:
        # Update status to processing
        job.status = DBAnalysisStatus.PROCESSING
        db.commit()
        
        start_time = datetime.now()
        
        # Split text into utterances
        utterances = split_into_utterances(text)
        job.total_utterances = len(utterances)
        
        # Analyze each utterance with rule-based analyzer
        base_analyses = cbil_analyzer.analyze_batch(utterances, metadata)
        
        # Enhance with LLM if available
        if settings.SOLAR_API_KEY or settings.UPSTAGE_API_KEY:
            try:
                enhanced_analyses = await llm_client.enhance_analysis_batch(
                    utterances, base_analyses, metadata
                )
                analyses = enhanced_analyses
            except Exception as e:
                logger.warning(f"LLM enhancement failed: {str(e)}, using base analysis")
                analyses = base_analyses
        else:
            analyses = base_analyses
        
        # Store utterance analyses
        level_counts = {i: 0 for i in range(1, 8)}
        total_level = 0
        
        for i, analysis in enumerate(analyses):
            utterance_obj = UtteranceAnalysis(
                job_id=job_id,
                utterance_number=i + 1,
                text=utterances[i],
                speaker="teacher",  # Default, can be enhanced
                cbil_level=analysis["cbil_level"],
                cbil_confidence=analysis["confidence"],
                cbil_reasoning=analysis["reasoning"],
                features=analysis.get("features"),
                keywords=analysis.get("keywords")
            )
            db.add(utterance_obj)
            
            # Update counts
            level = analysis["cbil_level"]
            level_counts[level] += 1
            total_level += level
        
        # Update job with results
        job.level_1_count = level_counts[1]
        job.level_2_count = level_counts[2]
        job.level_3_count = level_counts[3]
        job.level_4_count = level_counts[4]
        job.level_5_count = level_counts[5]
        job.level_6_count = level_counts[6]
        job.level_7_count = level_counts[7]
        job.average_level = total_level / len(analyses) if analyses else 0
        
        # Generate summary
        if settings.SOLAR_API_KEY or settings.UPSTAGE_API_KEY:
            try:
                summary = await llm_client.generate_summary(analyses, metadata)
            except:
                summary = generate_basic_summary(level_counts, job.average_level, len(analyses))
        else:
            summary = generate_basic_summary(level_counts, job.average_level, len(analyses))
        
        job.statistics = {
            "summary": summary,
            "metadata": metadata,
            "enhanced_with_llm": any(a.get("enhanced") for a in analyses)
        }
        job.analysis_results = analyses
        job.status = DBAnalysisStatus.COMPLETED
        job.processing_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"Analysis completed for job {job_id}")
        
    except Exception as e:
        logger.error(f"Analysis failed for job {job_id}: {str(e)}")
        job.status = DBAnalysisStatus.FAILED
        job.error_message = str(e)
    
    finally:
        db.commit()
        db.close()

def split_into_utterances(text: str) -> List[str]:
    """Split text into individual utterances"""
    # Simple splitting by sentences
    # Can be enhanced with better Korean NLP
    import re
    
    # Split by common sentence endings in Korean
    sentences = re.split(r'[.!?]\s+', text)
    
    # Filter out empty sentences and clean
    utterances = []
    for sentence in sentences:
        cleaned = sentence.strip()
        if cleaned and len(cleaned) > 5:  # Minimum length
            utterances.append(cleaned)
    
    return utterances

def generate_basic_summary(level_counts: Dict[int, int], avg_level: float, total: int) -> str:
    """Generate basic summary without LLM"""
    summary = f"총 {total}개 발화 분석 완료\n"
    summary += f"평균 CBIL 레벨: {avg_level:.2f}\n\n"
    
    # Find dominant level
    max_count = max(level_counts.values())
    dominant_levels = [k for k, v in level_counts.items() if v == max_count]
    
    if avg_level < 3:
        summary += "💡 제안: 더 높은 수준의 사고를 요구하는 질문을 추가해보세요."
    elif avg_level < 5:
        summary += "✅ 적절한 인지 수준의 수업이 진행되고 있습니다."
    else:
        summary += "🌟 높은 인지 수준의 수업입니다. 학생 이해도를 확인하세요."
    
    return summary

async def generate_report(job_id: str, db: Session) -> str:
    """Generate PDF report for analysis"""
    # This would use the report_generator module
    # For now, return a placeholder
    report_dir = settings.get_storage_path("reports")
    report_path = os.path.join(report_dir, f"report_{job_id}.pdf")
    
    # TODO: Implement actual PDF generation
    # report_generator.generate(job_id, report_path)
    
    return report_path

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.RAILWAY_ENVIRONMENT == "development" else None,
            "status_code": 500
        }
    )