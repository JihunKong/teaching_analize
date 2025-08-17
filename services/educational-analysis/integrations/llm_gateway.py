#!/usr/bin/env python3
"""
LLM Gateway
다양한 LLM API를 통합 관리하는 게이트웨이
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

import openai
from anthropic import Anthropic
import aiohttp

logger = logging.getLogger(__name__)

class LLMGateway:
    """
    LLM API 통합 게이트웨이
    
    기능:
    - OpenAI, Anthropic, Solar API 지원
    - 자동 폴백 및 로드 밸런싱
    - 요청 재시도 및 에러 핸들링
    - 비용 최적화 모델 선택
    """
    
    def __init__(self):
        # API 클라이언트 초기화
        self.openai_client = None
        self.anthropic_client = None
        self.solar_api_key = None
        
        self._setup_clients()
        
        # 모델 설정
        self.model_config = {
            "teaching_coach": {
                "primary": "gpt-4o-mini",  # 비용 효율적
                "fallback": "claude-3-haiku-20240307",
                "solar": "solar-1-mini-chat"
            },
            "dialogue_patterns": {
                "primary": "gpt-3.5-turbo",  # 정량 분석용
                "fallback": "claude-3-haiku-20240307",
                "solar": "solar-1-mini-chat"
            },
            "cbil_evaluation": {
                "primary": "gpt-4o-mini",  # 교육 이론 분석용
                "fallback": "claude-3-sonnet-20240229",
                "solar": "solar-1-mini-chat"
            }
        }
        
        # 재시도 설정
        self.max_retries = 3
        self.retry_delay = 1  # seconds
    
    def _setup_clients(self):
        """API 클라이언트 설정"""
        try:
            # OpenAI 설정
            if openai_key := os.getenv("OPENAI_API_KEY"):
                openai.api_key = openai_key
                self.openai_client = openai
                logger.info("✅ OpenAI client initialized")
            
            # Anthropic 설정
            if anthropic_key := os.getenv("ANTHROPIC_API_KEY"):
                self.anthropic_client = Anthropic(api_key=anthropic_key)
                logger.info("✅ Anthropic client initialized")
            
            # Solar API 설정
            if solar_key := os.getenv("UPSTAGE_API_KEY") or os.getenv("SOLAR_API_KEY"):
                self.solar_api_key = solar_key
                logger.info("✅ Solar API key loaded")
            
        except Exception as e:
            logger.error(f"❌ LLM client setup failed: {e}")
    
    async def generate_analysis(
        self,
        prompt: str,
        analysis_type: str,
        max_tokens: int = 4000,
        temperature: float = 0.3
    ) -> str:
        """
        분석 생성 (폴백 포함)
        
        Args:
            prompt: 분석 프롬프트
            analysis_type: 분석 유형
            max_tokens: 최대 토큰 수
            temperature: 창의성 수준
            
        Returns:
            str: LLM 응답
        """
        models = self.model_config.get(analysis_type, self.model_config["teaching_coach"])
        
        # 1차 시도: Primary 모델
        try:
            if self.openai_client and models["primary"].startswith("gpt"):
                logger.info(f"🤖 Using OpenAI {models['primary']}")
                return await self._call_openai(prompt, models["primary"], max_tokens, temperature)
        except Exception as e:
            logger.warning(f"⚠️ OpenAI primary failed: {e}")
        
        # 2차 시도: Fallback 모델
        try:
            if self.anthropic_client and models["fallback"].startswith("claude"):
                logger.info(f"🤖 Using Anthropic {models['fallback']}")
                return await self._call_anthropic(prompt, models["fallback"], max_tokens)
        except Exception as e:
            logger.warning(f"⚠️ Anthropic fallback failed: {e}")
        
        # 3차 시도: Solar API
        try:
            if self.solar_api_key:
                logger.info(f"🤖 Using Solar {models['solar']}")
                return await self._call_solar(prompt, models["solar"], max_tokens, temperature)
        except Exception as e:
            logger.warning(f"⚠️ Solar fallback failed: {e}")
        
        # 모든 API 실패시
        raise Exception("All LLM APIs failed")
    
    async def _call_openai(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """OpenAI API 호출"""
        for attempt in range(self.max_retries):
            try:
                response = await asyncio.to_thread(
                    self.openai_client.chat.completions.create,
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": "당신은 교육 분석 전문가입니다. 주어진 프롬프트에 따라 정확하고 상세한 분석을 제공하세요."
                        },
                        {
                            "role": "user", 
                            "content": prompt
                        }
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    timeout=60
                )
                
                return response.choices[0].message.content.strip()
                
            except Exception as e:
                logger.warning(f"OpenAI attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise
    
    async def _call_anthropic(
        self,
        prompt: str,
        model: str,
        max_tokens: int
    ) -> str:
        """Anthropic API 호출"""
        for attempt in range(self.max_retries):
            try:
                response = await asyncio.to_thread(
                    self.anthropic_client.messages.create,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=0.3,
                    system="당신은 교육 분석 전문가입니다. 주어진 프롬프트에 따라 정확하고 상세한 분석을 제공하세요.",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                
                return response.content[0].text.strip()
                
            except Exception as e:
                logger.warning(f"Anthropic attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise
    
    async def _call_solar(
        self,
        prompt: str,
        model: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Solar API 호출"""
        url = "https://api.upstage.ai/v1/solar/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.solar_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "당신은 교육 분석 전문가입니다. 주어진 프롬프트에 따라 정확하고 상세한 분석을 제공하세요."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, json=data, timeout=60) as response:
                        if response.status == 200:
                            result = await response.json()
                            return result["choices"][0]["message"]["content"].strip()
                        else:
                            error_text = await response.text()
                            raise Exception(f"Solar API error {response.status}: {error_text}")
                            
            except Exception as e:
                logger.warning(f"Solar attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                else:
                    raise
    
    async def test_connectivity(self) -> Dict[str, bool]:
        """
        모든 LLM API 연결 테스트
        
        Returns:
            Dict[str, bool]: API별 연결 상태
        """
        results = {}
        test_prompt = "안녕하세요. 연결 테스트입니다."
        
        # OpenAI 테스트
        try:
            if self.openai_client:
                await self._call_openai(test_prompt, "gpt-3.5-turbo", 50, 0.1)
                results["openai"] = True
            else:
                results["openai"] = False
        except:
            results["openai"] = False
        
        # Anthropic 테스트
        try:
            if self.anthropic_client:
                await self._call_anthropic(test_prompt, "claude-3-haiku-20240307", 50)
                results["anthropic"] = True
            else:
                results["anthropic"] = False
        except:
            results["anthropic"] = False
        
        # Solar 테스트
        try:
            if self.solar_api_key:
                await self._call_solar(test_prompt, "solar-1-mini-chat", 50, 0.1)
                results["solar"] = True
            else:
                results["solar"] = False
        except:
            results["solar"] = False
        
        logger.info(f"🔍 LLM connectivity test results: {results}")
        return results
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """사용 가능한 모델 목록 반환"""
        models = {
            "openai": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo"] if self.openai_client else [],
            "anthropic": [
                "claude-3-opus-20240229", 
                "claude-3-sonnet-20240229", 
                "claude-3-haiku-20240307"
            ] if self.anthropic_client else [],
            "solar": ["solar-1-mini-chat"] if self.solar_api_key else []
        }
        
        return models
    
    async def get_usage_stats(self) -> Dict[str, Any]:
        """사용량 통계 (간단한 구현)"""
        # 실제 구현에서는 DB에서 사용량 조회
        return {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "cost_estimate": 0.0
        }