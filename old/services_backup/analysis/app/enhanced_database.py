"""
Enhanced Database with SQLite Fallback + Advanced Business Features
Ultra Think approach: Fix critical issue while adding business value
"""

from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
import os
from datetime import datetime
from typing import Optional, Dict, List
import logging
import json

logger = logging.getLogger(__name__)

# Smart database URL selection (PostgreSQL with SQLite fallback)
def get_database_url():
    """Get database URL with automatic fallback"""
    postgres_url = os.getenv("DATABASE_URL")
    
    if postgres_url and postgres_url.startswith("postgresql://"):
        try:
            # Test PostgreSQL connection
            test_engine = create_engine(postgres_url)
            test_engine.connect().close()
            logger.info("Using PostgreSQL database")
            return postgres_url
        except Exception as e:
            logger.warning(f"PostgreSQL connection failed: {e}, falling back to SQLite")
    
    # Fallback to SQLite
    sqlite_path = "/app/data/aiboa_analysis.db"
    os.makedirs(os.path.dirname(sqlite_path), exist_ok=True)
    sqlite_url = f"sqlite:///{sqlite_path}"
    logger.info("Using SQLite database")
    return sqlite_url

DATABASE_URL = get_database_url()

# Create engine
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool if "postgresql" in DATABASE_URL else None,
    echo=False
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Enhanced Analysis Model with Business Intelligence
class AnalysisResultDB(Base):
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(String, unique=True, index=True, nullable=False)
    transcript_id = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    
    # Analysis metadata
    teacher_name = Column(String)
    subject = Column(String)
    grade_level = Column(String)
    class_duration = Column(Integer)
    school_name = Column(String)
    
    # Enhanced CBIL Analysis Results
    cbil_scores = Column(JSON)  # Raw scores: {level_1: 2, level_2: 3, ...}
    cbil_distribution = Column(JSON)  # Percentages: {level1: 15%, level2: 25%, ...}
    average_cbil_level = Column(Float)
    cognitive_complexity_score = Column(Float)  # New: Overall complexity metric
    
    # Advanced Interaction Analysis
    teacher_talk_ratio = Column(Float)
    student_talk_ratio = Column(Float)
    interaction_count = Column(Integer)
    wait_time_average = Column(Float)  # New: Average wait time after questions
    
    # Enhanced Question Analysis
    total_questions = Column(Integer)
    open_questions = Column(Integer)
    closed_questions = Column(Integer)
    higher_order_questions = Column(Integer)  # New: Levels 5-7
    
    # Business Intelligence Data
    text_analyzed = Column(Text)  # Original text for reanalysis
    detailed_analysis = Column(JSON)  # Full analysis data
    recommendations = Column(JSON)  # Enhanced recommendations with action items
    improvement_score = Column(Float)  # New: Overall improvement potential
    benchmark_comparison = Column(JSON)  # New: Comparison with database averages
    
    # Report generation tracking
    report_generated_count = Column(Integer, default=0)
    last_report_generated = Column(DateTime)
    
    def to_dict(self):
        """Enhanced dictionary representation"""
        return {
            "id": self.analysis_id,
            "analysis_id": self.analysis_id,
            "transcript_id": self.transcript_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "teacher_name": self.teacher_name,
            "subject": self.subject,
            "grade_level": self.grade_level,
            "school_name": self.school_name,
            "class_duration": self.class_duration,
            
            # Core CBIL data
            "cbil_scores": self.cbil_scores or {},
            "cbil_distribution": self.cbil_distribution or {},
            "average_cbil_level": self.average_cbil_level,
            "cognitive_complexity_score": self.cognitive_complexity_score,
            
            # Interaction data
            "teacher_talk_ratio": self.teacher_talk_ratio,
            "student_talk_ratio": self.student_talk_ratio,
            "interaction_count": self.interaction_count,
            "wait_time_average": self.wait_time_average,
            
            # Question analysis
            "total_questions": self.total_questions,
            "open_questions": self.open_questions,
            "closed_questions": self.closed_questions,
            "higher_order_questions": self.higher_order_questions,
            
            # Business intelligence
            "text": self.text_analyzed,
            "detailed_analysis": self.detailed_analysis or {},
            "recommendations": self.recommendations or [],
            "improvement_score": self.improvement_score,
            "benchmark_comparison": self.benchmark_comparison or {},
            
            # Report tracking
            "report_generated_count": self.report_generated_count,
            "last_report_generated": self.last_report_generated.isoformat() if self.last_report_generated else None
        }

# Enhanced Business Intelligence Functions
class AdvancedAnalytics:
    """Advanced analytics for business intelligence"""
    
    @staticmethod
    def calculate_benchmark_comparison(db: Session, cbil_scores: Dict[str, float]) -> Dict:
        """Compare analysis against database averages"""
        try:
            # Get all analyses for benchmarking
            all_analyses = db.query(AnalysisResultDB).all()
            
            if len(all_analyses) < 3:  # Not enough data for meaningful comparison
                return {
                    "status": "insufficient_data",
                    "message": "더 많은 데이터가 축적되면 벤치마킹이 가능합니다.",
                    "analyses_count": len(all_analyses)
                }
            
            # Calculate averages
            level_averages = {}
            for level in range(1, 8):
                level_key = f"level_{level}"
                scores = []
                for analysis in all_analyses:
                    if analysis.cbil_scores and level_key in analysis.cbil_scores:
                        scores.append(analysis.cbil_scores[level_key])
                
                if scores:
                    level_averages[level_key] = {
                        "average": sum(scores) / len(scores),
                        "current": cbil_scores.get(level_key, 0),
                        "percentile": AdvancedAnalytics._calculate_percentile(
                            cbil_scores.get(level_key, 0), scores
                        )
                    }
            
            return {
                "status": "success",
                "level_comparisons": level_averages,
                "database_size": len(all_analyses),
                "overall_performance": AdvancedAnalytics._calculate_overall_performance(level_averages)
            }
            
        except Exception as e:
            logger.error(f"Benchmark calculation failed: {e}")
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    def _calculate_percentile(value: float, all_values: List[float]) -> int:
        """Calculate percentile ranking"""
        if not all_values:
            return 50
        
        sorted_values = sorted(all_values)
        rank = sum(1 for v in sorted_values if v <= value)
        return int((rank / len(sorted_values)) * 100)
    
    @staticmethod
    def _calculate_overall_performance(level_averages: Dict) -> str:
        """Calculate overall performance rating"""
        if not level_averages:
            return "평가 불가"
        
        percentiles = [data["percentile"] for data in level_averages.values()]
        avg_percentile = sum(percentiles) / len(percentiles)
        
        if avg_percentile >= 80:
            return "우수 (상위 20%)"
        elif avg_percentile >= 60:
            return "양호 (상위 40%)"
        elif avg_percentile >= 40:
            return "보통 (중간 수준)"
        elif avg_percentile >= 20:
            return "개선 필요 (하위 40%)"
        else:
            return "집중 개선 필요 (하위 20%)"
    
    @staticmethod
    def generate_enhanced_recommendations(
        cbil_scores: Dict[str, float],
        benchmark_data: Dict,
        text_length: int
    ) -> List[Dict]:
        """Generate enhanced recommendations with action items"""
        recommendations = []
        
        total_items = sum(cbil_scores.values()) if cbil_scores else 0
        if total_items == 0:
            return [{"type": "error", "text": "분석할 데이터가 충분하지 않습니다.", "actions": []}]
        
        # Calculate percentages
        percentages = {k: (v/total_items)*100 for k, v in cbil_scores.items()}
        
        # Low-level analysis (levels 1-3)
        low_level = sum(percentages.get(f"level_{i}", 0) for i in [1, 2, 3])
        mid_level = percentages.get("level_4", 0)
        high_level = sum(percentages.get(f"level_{i}", 0) for i in [5, 6, 7])
        
        # Enhanced recommendations with specific actions
        if low_level > 60:
            recommendations.append({
                "type": "improvement",
                "priority": "high",
                "text": f"🔍 현재 수업이 단순 확인과 사실 회상 중심입니다 ({low_level:.1f}%)",
                "insight": "학습자의 분석적 사고를 촉진하는 질문 기법이 필요합니다.",
                "actions": [
                    "Why와 How로 시작하는 질문을 30% 이상 포함하세요",
                    "학생들에게 최소 5초의 사고 시간을 제공하세요", 
                    "예/아니오로 답할 수 없는 개방형 질문을 늘려보세요",
                    "학생들의 답변에 '왜 그렇게 생각하나요?' 추가 질문하기"
                ],
                "target_metric": "분석적 사고 질문 비율 30% → 50%"
            })
        
        if high_level < 20:
            recommendations.append({
                "type": "enhancement",
                "priority": "medium",
                "text": f"📈 고차원적 사고 활동이 부족합니다 ({high_level:.1f}%)",
                "insight": "창의적 사고와 평가적 판단을 요구하는 활동이 필요합니다.",
                "actions": [
                    "실제 문제 상황을 제시하고 해결책을 찾게 하세요",
                    "학생들에게 서로 다른 의견을 비교/평가하게 하세요",
                    "새로운 상황에 배운 내용을 적용하는 과제 제시",
                    "창의적 대안을 제시하도록 격려하세요"
                ],
                "target_metric": "고차원 사고 질문 비율 → 25% 이상"
            })
        
        if mid_level > 30:
            recommendations.append({
                "type": "optimization",
                "priority": "low",
                "text": f"✨ 분석적 사고 활동이 활발합니다 ({mid_level:.1f}%)",
                "insight": "이를 종합적 이해로 연결하는 브리지 활동이 효과적입니다.",
                "actions": [
                    "분석한 내용들을 연결하여 전체 그림을 그려보게 하세요",
                    "여러 개념 간의 관계를 설명하게 하세요",
                    "학습한 내용을 실생활 예시와 연결해보세요"
                ],
                "target_metric": "종합적 이해 활동 증대"
            })
        
        # Benchmark-based recommendations
        if benchmark_data.get("status") == "success":
            overall_perf = benchmark_data.get("overall_performance", "")
            if "하위" in overall_perf:
                recommendations.append({
                    "type": "benchmark",
                    "priority": "high", 
                    "text": f"📊 현재 성과는 {overall_perf}입니다",
                    "insight": "체계적인 개선 계획이 필요합니다.",
                    "actions": [
                        "매주 한 가지 질문 기법을 집중 연습하세요",
                        "동료 교사와 수업 관찰 및 피드백 교환",
                        "월별 CBIL 분석으로 개선 상황 추적"
                    ],
                    "target_metric": "3개월 내 상위 40% 진입 목표"
                })
        
        # General best practices
        recommendations.append({
            "type": "best_practice",
            "priority": "low",
            "text": "🎯 지속적 개선을 위한 일반 권장사항",
            "insight": "체계적인 접근이 장기적 성공의 열쇠입니다.",
            "actions": [
                "학습 목표에 따라 적절한 인지부하 수준을 계획적으로 배치하세요",
                "학습자의 수준을 고려하여 점진적으로 인지부하를 높여가세요", 
                "다양한 인지부하 수준을 균형있게 활용하여 학습 효과를 극대화하세요",
                "정기적인 자기 반성과 개선 계획 수립"
            ],
            "target_metric": "지속적 전문성 개발"
        })
        
        return recommendations[:6]  # Return top 6 recommendations

# Database initialization
async def init_db():
    """Initialize enhanced database"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info(f"Enhanced database initialized successfully with {DATABASE_URL}")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise

# Enhanced helper functions
def create_enhanced_analysis(
    db: Session,
    analysis_id: str,
    text: str,
    cbil_scores: Dict[str, float],
    transcript_id: Optional[str] = None,
    teacher_name: Optional[str] = None,
    subject: Optional[str] = None,
    grade_level: Optional[str] = None,
    school_name: Optional[str] = None
) -> AnalysisResultDB:
    """Create enhanced analysis with business intelligence"""
    
    # Calculate advanced metrics
    total_items = sum(cbil_scores.values()) if cbil_scores else 0
    cbil_distribution = {}
    if total_items > 0:
        cbil_distribution = {f"level_{i}": (cbil_scores.get(f"level_{i}", 0)/total_items)*100 
                           for i in range(1, 8)}
    
    # Calculate cognitive complexity score (weighted average)
    weights = [1, 2, 3, 4, 5, 6, 7]  # Higher levels get more weight
    weighted_sum = sum(cbil_scores.get(f"level_{i}", 0) * weights[i-1] for i in range(1, 8))
    complexity_score = weighted_sum / total_items if total_items > 0 else 0
    
    # Generate benchmark comparison
    benchmark_data = AdvancedAnalytics.calculate_benchmark_comparison(db, cbil_scores)
    
    # Generate enhanced recommendations
    recommendations = AdvancedAnalytics.generate_enhanced_recommendations(
        cbil_scores, benchmark_data, len(text)
    )
    
    # Calculate improvement score (potential for growth)
    high_level_ratio = sum(cbil_scores.get(f"level_{i}", 0) for i in [5, 6, 7]) / total_items if total_items > 0 else 0
    improvement_score = (1 - high_level_ratio) * 100  # Higher when more improvement possible
    
    analysis = AnalysisResultDB(
        analysis_id=analysis_id,
        transcript_id=transcript_id,
        created_at=datetime.utcnow(),
        teacher_name=teacher_name,
        subject=subject,
        grade_level=grade_level,
        school_name=school_name,
        
        # Enhanced CBIL data
        cbil_scores=cbil_scores,
        cbil_distribution=cbil_distribution,
        average_cbil_level=complexity_score,
        cognitive_complexity_score=complexity_score,
        
        # Text and analysis
        text_analyzed=text,
        detailed_analysis={"total_items": total_items, "complexity_analysis": "auto-generated"},
        recommendations=recommendations,
        improvement_score=improvement_score,
        benchmark_comparison=benchmark_data,
        
        # Initialize counters
        report_generated_count=0
    )
    
    try:
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        logger.info(f"Enhanced analysis created: {analysis_id}")
        return analysis
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create analysis: {e}")
        raise

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_analysis(db: Session, analysis_id: str) -> Optional[AnalysisResultDB]:
    """Get analysis by ID"""
    return db.query(AnalysisResultDB).filter(
        AnalysisResultDB.analysis_id == analysis_id
    ).first()

def get_recent_analyses(db: Session, limit: int = 10) -> List[AnalysisResultDB]:
    """Get recent analyses"""
    return db.query(AnalysisResultDB).order_by(
        AnalysisResultDB.created_at.desc()
    ).limit(limit).all()

def get_teacher_analyses(db: Session, teacher_name: str, limit: int = 100) -> List[AnalysisResultDB]:
    """Get analyses for specific teacher"""
    return db.query(AnalysisResultDB).filter(
        AnalysisResultDB.teacher_name == teacher_name
    ).order_by(
        AnalysisResultDB.created_at.desc()
    ).limit(limit).all()

def increment_report_count(db: Session, analysis_id: str):
    """Increment report generation count"""
    analysis = get_analysis(db, analysis_id)
    if analysis:
        analysis.report_generated_count = (analysis.report_generated_count or 0) + 1
        analysis.last_report_generated = datetime.utcnow()
        db.commit()
        logger.info(f"Report count incremented for {analysis_id}")