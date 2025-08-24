#!/usr/bin/env python3
"""
Visualization Engine
교육 분석 결과를 위한 차트 생성 엔진
"""

import os
import uuid
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
import seaborn as sns
from matplotlib import patheffects

logger = logging.getLogger(__name__)

class VisualizationEngine:
    """
    교육 분석 시각화 엔진
    
    기능:
    - 한국어 폰트 지원
    - 막대 차트, 레이더 차트, 히트맵 생성
    - 고해상도 이미지 저장
    - URL 기반 차트 접근
    """
    
    def __init__(self, static_dir: str = "/static/charts", base_url: str = ""):
        self.static_dir = static_dir
        self.base_url = base_url
        
        # 디렉토리 생성
        os.makedirs(static_dir, exist_ok=True)
        
        # 한국어 폰트 설정
        self._setup_korean_fonts()
        
        # 스타일 설정
        self._setup_plot_style()
    
    def _setup_korean_fonts(self):
        """한국어 폰트 설정"""
        try:
            # macOS/Linux용 한국어 폰트
            korean_fonts = [
                'AppleGothic',       # macOS
                'NanumGothic',       # 나눔고딕
                'Malgun Gothic',     # Windows
                'DejaVu Sans'        # 기본 폰트
            ]
            
            for font_name in korean_fonts:
                try:
                    plt.rcParams['font.family'] = font_name
                    # 테스트용 한글 렌더링
                    fig, ax = plt.subplots(figsize=(1, 1))
                    ax.text(0.5, 0.5, '한글', fontsize=12)
                    plt.close(fig)
                    logger.info(f"✅ Korean font set: {font_name}")
                    break
                except Exception:
                    continue
            else:
                logger.warning("⚠️ No Korean font found, using default")
                
            # 마이너스 기호 깨짐 방지
            plt.rcParams['axes.unicode_minus'] = False
            
        except Exception as e:
            logger.error(f"❌ Font setup failed: {e}")
    
    def _setup_plot_style(self):
        """플롯 스타일 설정"""
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        plt.rcParams.update({
            'figure.figsize': (10, 6),
            'figure.dpi': 150,
            'savefig.dpi': 300,
            'savefig.bbox': 'tight',
            'savefig.transparent': False,
            'axes.grid': True,
            'grid.alpha': 0.3,
            'font.size': 11,
            'axes.titlesize': 14,
            'axes.labelsize': 12,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'legend.fontsize': 10
        })
    
    async def create_bar_chart(
        self,
        data: Dict[str, int],
        title: str,
        labels: List[str],
        filename: Optional[str] = None,
        sort_by_value: bool = True
    ) -> str:
        """
        막대 차트 생성
        
        Args:
            data: 차트 데이터 {label: value}
            title: 차트 제목
            labels: X축 라벨들
            filename: 파일명 (없으면 자동 생성)
            sort_by_value: 값으로 정렬 여부
            
        Returns:
            str: 차트 이미지 URL
        """
        try:
            if not filename:
                filename = f"bar_chart_{uuid.uuid4().hex[:8]}"
            
            # 데이터 정렬
            if sort_by_value:
                sorted_items = sorted(data.items(), key=lambda x: x[1], reverse=True)
                labels, values = zip(*sorted_items)
            else:
                labels = list(data.keys())
                values = list(data.values())
            
            # 차트 생성
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # 막대 그래프
            bars = ax.bar(labels, values, alpha=0.8, edgecolor='black', linewidth=0.5)
            
            # 색상 그라데이션
            colors = plt.cm.viridis(np.linspace(0, 1, len(bars)))
            for bar, color in zip(bars, colors):
                bar.set_color(color)
            
            # 값 라벨 추가
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom', fontweight='bold')
            
            # 스타일링
            ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('분석 항목', fontsize=12)
            ax.set_ylabel('빈도 (회)', fontsize=12)
            
            # X축 라벨 회전
            plt.xticks(rotation=45, ha='right')
            
            # 격자 설정
            ax.grid(True, alpha=0.3, axis='y')
            ax.set_axisbelow(True)
            
            # 레이아웃 조정
            plt.tight_layout()
            
            # 저장
            file_path = os.path.join(self.static_dir, f"{filename}.png")
            plt.savefig(file_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            # URL 반환
            url = f"{self.base_url}/static/charts/{filename}.png"
            logger.info(f"✅ Bar chart created: {url}")
            return url
            
        except Exception as e:
            logger.error(f"❌ Bar chart creation failed: {e}")
            return ""
    
    async def create_radar_chart(
        self,
        data: Dict[str, List[float]],
        labels: List[str],
        title: str,
        filename: Optional[str] = None
    ) -> str:
        """
        레이더 차트 생성
        
        Args:
            data: 차트 데이터 {"scores": [1,2,3,2,1,2,3]}
            labels: 각 축의 라벨
            title: 차트 제목
            filename: 파일명
            
        Returns:
            str: 차트 이미지 URL
        """
        try:
            if not filename:
                filename = f"radar_chart_{uuid.uuid4().hex[:8]}"
            
            scores = data.get("scores", [])
            if not scores or len(scores) != len(labels):
                raise ValueError("Scores and labels length mismatch")
            
            # 각도 계산
            angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
            scores = scores + scores[:1]  # 원형으로 닫기
            angles += angles[:1]
            
            # 차트 생성
            fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
            
            # 레이더 차트 그리기
            ax.fill(angles, scores, color='skyblue', alpha=0.4)
            ax.plot(angles, scores, color='blue', linewidth=2, marker='o', markersize=8)
            
            # 축 라벨 설정
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(labels, fontsize=12)
            
            # Y축 설정 (0-3점)
            ax.set_ylim(0, 3)
            ax.set_yticks([0, 1, 2, 3])
            ax.set_yticklabels(['0점\n미흡', '1점\n보통', '2점\n우수', '3점\n탁월'], fontsize=10)
            ax.grid(True, alpha=0.3)
            
            # 제목
            ax.set_title(title, fontsize=16, fontweight='bold', pad=30)
            
            # 점수 라벨 추가
            for angle, score, label in zip(angles[:-1], scores[:-1], labels):
                ax.text(angle, score + 0.1, f'{score}', ha='center', va='center', 
                       fontweight='bold', fontsize=10,
                       bbox=dict(boxstyle="round,pad=0.1", facecolor="white", alpha=0.8))
            
            # 저장
            file_path = os.path.join(self.static_dir, f"{filename}.png")
            plt.savefig(file_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            # URL 반환
            url = f"{self.base_url}/static/charts/{filename}.png"
            logger.info(f"✅ Radar chart created: {url}")
            return url
            
        except Exception as e:
            logger.error(f"❌ Radar chart creation failed: {e}")
            return ""
    
    async def create_heatmap(
        self,
        data: List[List[float]],
        x_labels: List[str],
        y_labels: List[str],
        title: str,
        filename: Optional[str] = None
    ) -> str:
        """
        히트맵 생성
        
        Args:
            data: 2D 데이터 배열
            x_labels: X축 라벨
            y_labels: Y축 라벨
            title: 차트 제목
            filename: 파일명
            
        Returns:
            str: 차트 이미지 URL
        """
        try:
            if not filename:
                filename = f"heatmap_{uuid.uuid4().hex[:8]}"
            
            # 차트 생성
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # 히트맵
            im = ax.imshow(data, cmap='YlOrRd', aspect='auto')
            
            # 축 설정
            ax.set_xticks(np.arange(len(x_labels)))
            ax.set_yticks(np.arange(len(y_labels)))
            ax.set_xticklabels(x_labels)
            ax.set_yticklabels(y_labels)
            
            # 값 표시
            for i in range(len(y_labels)):
                for j in range(len(x_labels)):
                    text = ax.text(j, i, f'{data[i][j]:.1f}',
                                 ha="center", va="center", color="black", fontweight='bold')
            
            # 제목
            ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
            
            # 컬러바
            cbar = plt.colorbar(im)
            cbar.set_label('점수', rotation=270, labelpad=15)
            
            # 레이아웃
            plt.tight_layout()
            
            # 저장
            file_path = os.path.join(self.static_dir, f"{filename}.png")
            plt.savefig(file_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            # URL 반환
            url = f"{self.base_url}/static/charts/{filename}.png"
            logger.info(f"✅ Heatmap created: {url}")
            return url
            
        except Exception as e:
            logger.error(f"❌ Heatmap creation failed: {e}")
            return ""
    
    async def create_comprehensive_dashboard(
        self,
        teaching_data: Dict[str, Any],
        dialogue_data: Dict[str, Any],
        cbil_data: Dict[str, Any],
        filename: Optional[str] = None
    ) -> str:
        """
        종합 대시보드 생성
        
        Args:
            teaching_data: 교육 코칭 데이터
            dialogue_data: 대화 패턴 데이터
            cbil_data: CBIL 데이터
            filename: 파일명
            
        Returns:
            str: 대시보드 이미지 URL
        """
        try:
            if not filename:
                filename = f"dashboard_{uuid.uuid4().hex[:8]}"
            
            # 서브플롯 생성 (2x2)
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            fig.suptitle('📊 수업 분석 종합 대시보드', fontsize=20, fontweight='bold')
            
            # 1. 교육 코칭 - 강점/개선 영역
            if teaching_data:
                strengths_count = len(teaching_data.get('strengths', []))
                improvements_count = len(teaching_data.get('improvements', []))
                
                ax1.bar(['강점 영역', '개선 영역'], [strengths_count, improvements_count], 
                       color=['green', 'orange'], alpha=0.7)
                ax1.set_title('🎯 교육 코칭 분석', fontweight='bold')
                ax1.set_ylabel('항목 수')
                
                for i, v in enumerate([strengths_count, improvements_count]):
                    ax1.text(i, v + 0.1, str(v), ha='center', fontweight='bold')
            
            # 2. 대화 패턴 - 상위 대화 유형
            if dialogue_data:
                dialogue_types = dialogue_data.get('dialogue_counts', {})
                top_3 = dict(sorted(dialogue_types.items(), key=lambda x: x[1], reverse=True)[:3])
                
                ax2.bar(list(top_3.keys()), list(top_3.values()), 
                       color=['skyblue', 'lightgreen', 'lightcoral'])
                ax2.set_title('💬 대화 패턴 분석 (상위 3개)', fontweight='bold')
                ax2.set_ylabel('빈도')
                plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)
            
            # 3. CBIL 평가 - 단계별 점수
            if cbil_data:
                steps = cbil_data.get('step_names', [])
                scores = cbil_data.get('scores', [])
                
                bars = ax3.bar(range(len(steps)), scores, color='purple', alpha=0.7)
                ax3.set_title('🎓 CBIL 7단계 평가', fontweight='bold')
                ax3.set_ylabel('점수 (0-3)')
                ax3.set_xticks(range(len(steps)))
                ax3.set_xticklabels([s[:10] for s in steps], rotation=45)
                
                # 평균선 추가
                if scores:
                    avg_score = sum(scores) / len(scores)
                    ax3.axhline(y=avg_score, color='red', linestyle='--', 
                               label=f'평균: {avg_score:.1f}')
                    ax3.legend()
            
            # 4. 종합 요약
            ax4.axis('off')
            summary_text = self._generate_dashboard_summary(teaching_data, dialogue_data, cbil_data)
            ax4.text(0.05, 0.95, summary_text, transform=ax4.transAxes, fontsize=12,
                    verticalalignment='top', fontfamily='monospace',
                    bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8))
            
            # 레이아웃 조정
            plt.tight_layout()
            
            # 저장
            file_path = os.path.join(self.static_dir, f"{filename}.png")
            plt.savefig(file_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            # URL 반환
            url = f"{self.base_url}/static/charts/{filename}.png"
            logger.info(f"✅ Dashboard created: {url}")
            return url
            
        except Exception as e:
            logger.error(f"❌ Dashboard creation failed: {e}")
            return ""
    
    def _generate_dashboard_summary(
        self,
        teaching_data: Dict[str, Any],
        dialogue_data: Dict[str, Any],
        cbil_data: Dict[str, Any]
    ) -> str:
        """대시보드 요약 텍스트 생성"""
        summary_lines = ["📋 분석 요약"]
        summary_lines.append("=" * 30)
        
        if teaching_data:
            mode = teaching_data.get('mode', '알 수 없음')
            summary_lines.append(f"🎯 분석 모드: {mode}")
            
        if dialogue_data:
            total_dialogue = sum(dialogue_data.get('dialogue_counts', {}).values())
            summary_lines.append(f"💬 총 대화 참여: {total_dialogue}회")
            
        if cbil_data:
            avg_score = cbil_data.get('average_score', 0)
            summary_lines.append(f"🎓 CBIL 평균: {avg_score:.1f}점")
        
        summary_lines.append("")
        summary_lines.append("📈 주요 특징:")
        
        # 각 분석별 주요 특징 추가
        if teaching_data and teaching_data.get('strengths'):
            summary_lines.append(f"• 강점: {len(teaching_data['strengths'])}개 영역")
            
        if dialogue_data:
            dominant = dialogue_data.get('dominant_patterns', [])
            if dominant:
                summary_lines.append(f"• 지배적 패턴: {dominant[0]}")
        
        if cbil_data:
            concept_pct = cbil_data.get('concept_centered_percentage', 0)
            summary_lines.append(f"• 개념 중심도: {concept_pct:.1f}%")
        
        return "\n".join(summary_lines)
    
    def cleanup_old_charts(self, days_old: int = 7):
        """오래된 차트 파일 정리"""
        try:
            current_time = datetime.now()
            deleted_count = 0
            
            for filename in os.listdir(self.static_dir):
                file_path = os.path.join(self.static_dir, filename)
                if os.path.isfile(file_path):
                    file_age = current_time - datetime.fromtimestamp(os.path.getctime(file_path))
                    if file_age.days > days_old:
                        os.remove(file_path)
                        deleted_count += 1
            
            logger.info(f"🧹 Cleaned up {deleted_count} old chart files")
            
        except Exception as e:
            logger.error(f"❌ Chart cleanup failed: {e}")