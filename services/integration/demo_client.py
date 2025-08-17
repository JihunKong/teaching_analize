#!/usr/bin/env python3
"""
Demo Client
통합 워크플로우 데모 클라이언트
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any, Optional

class IntegrationClient:
    """
    통합 서비스 클라이언트
    
    YouTube URL을 입력받아 전사 → 분석 → 결과까지 전체 프로세스 실행
    """
    
    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def analyze_youtube_video(
        self,
        youtube_url: str,
        language: str = "ko",
        analysis_types: list = None
    ) -> str:
        """
        YouTube 영상 분석 시작
        
        Args:
            youtube_url: YouTube URL
            language: 전사 언어
            analysis_types: 분석 유형 목록
            
        Returns:
            str: 워크플로우 ID
        """
        if analysis_types is None:
            analysis_types = ["comprehensive"]
        
        payload = {
            "youtube_url": youtube_url,
            "language": language,
            "analysis_types": analysis_types
        }
        
        async with self.session.post(
            f"{self.base_url}/api/analyze-youtube",
            json=payload
        ) as response:
            if response.status == 200:
                result = await response.json()
                print(f"🚀 분석 시작됨: {result['workflow_id']}")
                print(f"📅 예상 완료 시간: {result['estimated_completion_time']}")
                return result['workflow_id']
            else:
                error_text = await response.text()
                raise Exception(f"분석 시작 실패: {response.status}, {error_text}")
    
    async def wait_for_completion(
        self,
        workflow_id: str,
        max_wait_minutes: int = 10,
        check_interval: int = 10
    ) -> Dict[str, Any]:
        """
        워크플로우 완료 대기
        
        Args:
            workflow_id: 워크플로우 ID
            max_wait_minutes: 최대 대기 시간 (분)
            check_interval: 확인 간격 (초)
            
        Returns:
            Dict: 최종 결과
        """
        start_time = time.time()
        max_wait_seconds = max_wait_minutes * 60
        
        print(f"⏳ 워크플로우 완료 대기 중... (최대 {max_wait_minutes}분)")
        
        while time.time() - start_time < max_wait_seconds:
            # 상태 확인
            status = await self.get_workflow_status(workflow_id)
            
            print(f"📊 진행률: {status.get('progress_percentage', 0)}% - {status.get('current_step', '처리 중...')}")
            
            if status['status'] == 'completed':
                print("✅ 워크플로우 완료!")
                return await self.get_workflow_results(workflow_id)
            elif status['status'] == 'failed':
                error_msg = status.get('error_message', '알 수 없는 오류')
                raise Exception(f"워크플로우 실패: {error_msg}")
            
            # 대기
            await asyncio.sleep(check_interval)
        
        raise Exception(f"워크플로우 시간 초과 ({max_wait_minutes}분)")
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """워크플로우 상태 조회"""
        async with self.session.get(
            f"{self.base_url}/api/workflow/{workflow_id}/status"
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                raise Exception(f"상태 조회 실패: {response.status}, {error_text}")
    
    async def get_workflow_results(self, workflow_id: str) -> Dict[str, Any]:
        """워크플로우 결과 조회"""
        async with self.session.get(
            f"{self.base_url}/api/workflow/{workflow_id}/results"
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                raise Exception(f"결과 조회 실패: {response.status}, {error_text}")
    
    async def test_services(self) -> Dict[str, Any]:
        """연결된 서비스 상태 테스트"""
        async with self.session.get(
            f"{self.base_url}/api/test/services"
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                raise Exception(f"서비스 테스트 실패: {response.status}, {error_text}")

def print_results_summary(results: Dict[str, Any]):
    """결과 요약 출력"""
    print("\n" + "="*60)
    print("📊 분석 결과 요약")
    print("="*60)
    
    # 기본 정보
    summary = results.get('summary', {})
    print(f"🆔 워크플로우 ID: {summary.get('workflow_id', 'N/A')}")
    print(f"⏱️  처리 시간: {summary.get('processing_time', 'N/A')}")
    print(f"📹 YouTube URL: {summary.get('youtube_url', 'N/A')}")
    print(f"✅ 완료 시각: {summary.get('completed_at', 'N/A')}")
    
    # 분석 결과
    analyses = results.get('results', {}).get('analyses', {})
    print(f"\n📈 수행된 분석: {len(analyses)}개")
    
    for analysis_type, analysis_data in analyses.items():
        print(f"\n📋 {analysis_type.upper()} 분석:")
        
        if analysis_type == "comprehensive":
            # 종합 분석 결과
            if "executive_summary" in analysis_data:
                print(f"   📝 요약: {analysis_data['executive_summary'][:200]}...")
            
            if "key_insights" in analysis_data:
                print(f"   💡 주요 인사이트:")
                for i, insight in enumerate(analysis_data['key_insights'][:3], 1):
                    print(f"      {i}. {insight}")
        
        elif "average_score" in analysis_data:
            # CBIL 분석
            print(f"   🎯 평균 점수: {analysis_data['average_score']}/3")
            print(f"   📊 개념 중심도: {analysis_data.get('concept_centered_percentage', 'N/A')}%")
        
        elif "summary_text" in analysis_data:
            # 대화 패턴 분석
            print(f"   💬 대화 패턴: {analysis_data['summary_text'][:150]}...")
    
    # 차트 및 시각화
    chart_urls = results.get('results', {}).get('analyses', {}).get('comprehensive', {}).get('dashboard_url')
    if chart_urls:
        print(f"\n📊 대시보드: {chart_urls}")
    
    print("\n" + "="*60)

async def main():
    """메인 데모 함수"""
    print("🎓 교육 분석 통합 시스템 데모")
    print("="*50)
    
    # YouTube URL 입력
    youtube_url = input("YouTube URL을 입력하세요: ").strip()
    
    if not youtube_url:
        youtube_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # 기본값
        print(f"기본 URL 사용: {youtube_url}")
    
    # 분석 유형 선택
    print("\n분석 유형을 선택하세요:")
    print("1. 종합 분석 (comprehensive)")
    print("2. 교육 코칭 분석 (teaching-coach)")
    print("3. 대화 패턴 분석 (dialogue-patterns)")
    print("4. CBIL 평가 (cbil-evaluation)")
    print("5. 전체 분석 (모든 유형)")
    
    choice = input("선택 (1-5, 기본값: 1): ").strip() or "1"
    
    analysis_types_map = {
        "1": ["comprehensive"],
        "2": ["teaching-coach"],
        "3": ["dialogue-patterns"],
        "4": ["cbil-evaluation"],
        "5": ["teaching-coach", "dialogue-patterns", "cbil-evaluation", "comprehensive"]
    }
    
    analysis_types = analysis_types_map.get(choice, ["comprehensive"])
    print(f"선택된 분석: {', '.join(analysis_types)}")
    
    async with IntegrationClient() as client:
        try:
            # 1. 서비스 상태 확인
            print("\n🔍 서비스 연결 상태 확인 중...")
            service_status = await client.test_services()
            
            transcription_status = service_status['transcription_service']['status']
            analysis_status = service_status['analysis_service']['status']
            
            print(f"📝 전사 서비스: {transcription_status}")
            print(f"🎯 분석 서비스: {analysis_status}")
            
            if transcription_status != "healthy":
                print("⚠️  전사 서비스에 문제가 있을 수 있습니다.")
            
            if analysis_status != "healthy":
                print("⚠️  분석 서비스에 문제가 있을 수 있습니다.")
            
            # 2. 분석 시작
            print(f"\n🚀 YouTube 영상 분석 시작...")
            workflow_id = await client.analyze_youtube_video(
                youtube_url=youtube_url,
                analysis_types=analysis_types
            )
            
            # 3. 완료 대기
            results = await client.wait_for_completion(workflow_id, max_wait_minutes=10)
            
            # 4. 결과 출력
            print_results_summary(results)
            
            # 5. 결과 저장 (옵션)
            save_results = input("\n결과를 JSON 파일로 저장하시겠습니까? (y/N): ").strip().lower()
            if save_results == 'y':
                filename = f"analysis_results_{workflow_id}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                print(f"💾 결과가 {filename}에 저장되었습니다.")
            
        except Exception as e:
            print(f"❌ 오류 발생: {e}")
            return 1
    
    print("\n🎉 데모 완료!")
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))