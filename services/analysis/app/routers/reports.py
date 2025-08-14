from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from ..database import get_db, get_analysis, get_recent_analyses, get_teacher_analyses

router = APIRouter()

@router.get("/analysis/{analysis_id}")
async def get_analysis_report(
    analysis_id: str,
    format: str = "json",
    db: Session = Depends(get_db)
):
    """
    Get detailed analysis report
    """
    analysis = get_analysis(db, analysis_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    if format == "json":
        return analysis.to_dict()
    elif format == "pdf":
        # Generate PDF report (placeholder)
        return {"message": "PDF generation not implemented yet"}
    else:
        raise HTTPException(status_code=400, detail="Invalid format")

@router.get("/teacher/{teacher_name}")
async def get_teacher_reports(
    teacher_name: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get all reports for a specific teacher
    """
    analyses = get_teacher_analyses(db, teacher_name, limit)
    
    return {
        "teacher": teacher_name,
        "total_analyses": len(analyses),
        "analyses": [a.to_dict() for a in analyses]
    }

@router.get("/recent")
async def get_recent_reports(
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get recent analysis reports
    """
    analyses = get_recent_analyses(db, limit)
    
    return {
        "total": len(analyses),
        "analyses": [a.to_dict() for a in analyses]
    }

@router.get("/statistics")
async def get_statistics(
    db: Session = Depends(get_db)
):
    """
    Get overall statistics
    """
    from sqlalchemy import func
    from ..database import AnalysisResultDB
    
    # Get overall statistics
    total_analyses = db.query(func.count(AnalysisResultDB.id)).scalar()
    
    avg_cbil = db.query(func.avg(AnalysisResultDB.average_cbil_level)).scalar()
    
    avg_teacher_talk = db.query(func.avg(AnalysisResultDB.teacher_talk_ratio)).scalar()
    
    # Get CBIL distribution across all analyses
    # This would need more complex aggregation in production
    
    return {
        "total_analyses": total_analyses or 0,
        "average_cbil_level": avg_cbil or 0,
        "average_teacher_talk_ratio": avg_teacher_talk or 0,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/trends/{teacher_name}")
async def get_teacher_trends(
    teacher_name: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get trend analysis for a teacher over time
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    from ..database import AnalysisResultDB
    
    analyses = db.query(AnalysisResultDB).filter(
        AnalysisResultDB.teacher_name == teacher_name,
        AnalysisResultDB.created_at >= cutoff_date
    ).order_by(AnalysisResultDB.created_at).all()
    
    if not analyses:
        return {"message": "No data available for the specified period"}
    
    # Calculate trends
    cbil_trend = [a.average_cbil_level for a in analyses if a.average_cbil_level]
    talk_ratio_trend = [a.teacher_talk_ratio for a in analyses if a.teacher_talk_ratio]
    
    return {
        "teacher": teacher_name,
        "period_days": days,
        "total_analyses": len(analyses),
        "cbil_trend": cbil_trend,
        "talk_ratio_trend": talk_ratio_trend,
        "improvement": {
            "cbil": cbil_trend[-1] - cbil_trend[0] if len(cbil_trend) > 1 else 0,
            "talk_ratio": talk_ratio_trend[-1] - talk_ratio_trend[0] if len(talk_ratio_trend) > 1 else 0
        }
    }

@router.get("/export/{analysis_id}")
async def export_report(
    analysis_id: str,
    format: str = "csv",
    db: Session = Depends(get_db)
):
    """
    Export analysis report in various formats
    """
    analysis = get_analysis(db, analysis_id)
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    if format == "csv":
        # Generate CSV export
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(["Metric", "Value"])
        
        # Write data
        writer.writerow(["Analysis ID", analysis.analysis_id])
        writer.writerow(["Teacher", analysis.teacher_name])
        writer.writerow(["Subject", analysis.subject])
        writer.writerow(["Average CBIL Level", analysis.average_cbil_level])
        writer.writerow(["Teacher Talk Ratio", analysis.teacher_talk_ratio])
        
        # Return as response
        return JSONResponse(
            content={
                "csv_data": output.getvalue(),
                "filename": f"analysis_{analysis_id}.csv"
            }
        )
    
    else:
        raise HTTPException(status_code=400, detail="Unsupported export format")