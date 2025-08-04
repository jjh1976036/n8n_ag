#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import os
import sys
from datetime import datetime
from typing import Dict, Any

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.collector_agent import CollectorAgent
from agents.processor_agent import ProcessorAgent
from agents.action_agent import ActionAgent
from agents.reporter_agent import ReporterAgent
from config.agent_config import AgentConfig


class NewsScrapingChatApp:
    """뉴스 스크래핑 채팅 애플리케이션"""
    
    def __init__(self):
        self.config = AgentConfig()
        
        # 에이전트 초기화
        print("🤖 에이전트들을 초기화하는 중...")
        try:
            self.collector = CollectorAgent()
            self.processor = ProcessorAgent()
            self.action = ActionAgent()
            self.reporter = ReporterAgent()
            print("✅ 모든 에이전트 초기화 완료!")
        except Exception as e:
            print(f"❌ 에이전트 초기화 실패: {e}")
            sys.exit(1)
    
    def display_welcome(self):
        """환영 메시지 출력"""
        print("\n" + "="*60)
        print("🗞️  뉴스 스크래핑 & 분석 시스템")
        print("="*60)
        print("📝 사용법:")
        print("  - 뉴스 키워드나 주제를 입력하세요")
        print("  - 'quit' 또는 'exit' 입력 시 종료")
        print("  - 'help' 입력 시 도움말 표시")
        print("="*60)
    
    def display_help(self):
        """도움말 출력"""
        print("\n📖 도움말:")
        print("  🔍 예시 입력:")
        print("    - 'AI 기술 동향 뉴스'")
        print("    - '삼성전자 주가 관련 뉴스'")
        print("    - '코로나19 최신 소식'")
        print("    - '암호화폐 비트코인 뉴스'")
        print("\n  💡 시스템이 자동으로:")
        print("    1. 관련 뉴스 사이트 검색")
        print("    2. 뉴스 기사 내용 수집")
        print("    3. 데이터 분석 및 정리")
        print("    4. 종합 보고서 생성")
        print()
    
    async def process_user_request(self, user_input: str) -> Dict[str, Any]:
        """사용자 요청 처리"""
        print(f"\n🔄 처리 시작: '{user_input}'")
        print("-" * 50)
        
        workflow_results = {
            'user_request': user_input,
            'timestamp': datetime.now().isoformat(),
            'collector_result': None,
            'processor_result': None,
            'action_result': None,
            'reporter_result': None,
            'status': 'started'
        }
        
        try:
            # 1단계: 정보 수집
            print("\n1️⃣ 뉴스 정보 수집 중...")
            collector_result = self.collector.collect_information(user_input)
            workflow_results['collector_result'] = collector_result
            
            if collector_result['status'] != 'success':
                workflow_results['status'] = 'failed'
                workflow_results['error'] = '정보 수집 실패'
                return workflow_results
            
            print(f"   ✅ {collector_result['message']}")
            
            # 2단계: 데이터 처리
            print("\n2️⃣ 수집된 데이터 분석 중...")
            processor_result = self.processor.process_data(collector_result)
            workflow_results['processor_result'] = processor_result
            
            if processor_result['status'] != 'success':
                workflow_results['status'] = 'failed'
                workflow_results['error'] = '데이터 처리 실패'
                return workflow_results
                
            print(f"   ✅ {processor_result['message']}")
            
            # 3단계: 액션 실행 (저장)
            print("\n3️⃣ 결과 저장 중...")
            action_result = self.action.execute_action(processor_result, user_input)
            workflow_results['action_result'] = action_result
            
            if action_result['status'] != 'success':
                workflow_results['status'] = 'failed' 
                workflow_results['error'] = '액션 실행 실패'
                return workflow_results
                
            print(f"   ✅ {action_result['message']}")
            
            # 4단계: 보고서 생성
            print("\n4️⃣ 최종 보고서 생성 중...")
            reporter_result = self.reporter.generate_report(
                collector_result, 
                processor_result, 
                action_result,
                user_input
            )
            workflow_results['reporter_result'] = reporter_result
            
            if reporter_result['status'] != 'success':
                workflow_results['status'] = 'failed'
                workflow_results['error'] = '보고서 생성 실패'
                return workflow_results
                
            print(f"   ✅ {reporter_result['message']}")
            
            workflow_results['status'] = 'completed'
            
        except Exception as e:
            print(f"❌ 처리 중 오류 발생: {e}")
            workflow_results['status'] = 'error'
            workflow_results['error'] = str(e)
        
        return workflow_results
    
    def display_results(self, results: Dict[str, Any]):
        """결과 출력"""
        print("\n" + "="*60)
        print("📊 최종 결과")
        print("="*60)
        
        if results['status'] == 'completed':
            print("✅ 모든 작업이 성공적으로 완료되었습니다!")
            
            # 수집 결과 요약
            if results['collector_result']:
                collector_data = results['collector_result']['data']
                print(f"\n📈 수집 요약:")
                print(f"  - 수집된 사이트: {collector_data['collection_summary']['total_sites']}개")
                print(f"  - 성공적 수집: {collector_data['collection_summary']['successful_scrapes']}개")
            
            # 처리 결과 요약
            if results['processor_result']:
                processing_summary = results['processor_result']['data']['processing_summary']
                print(f"\n🔧 분석 요약:")
                print(f"  - 처리된 항목: {processing_summary['total_processed']}개")
                print(f"  - 발견된 카테고리: {processing_summary['categories_found']}개")
                print(f"  - 추출된 키워드: {processing_summary['keywords_extracted']}개")
            
            # 저장 결과
            if results['action_result']:
                print(f"\n💾 저장 결과:")
                print(f"  - {results['action_result']['message']}")
            
            # 보고서 생성 결과
            if results['reporter_result']:
                print(f"\n📝 보고서:")
                print(f"  - {results['reporter_result']['message']}")
                
                # 보고서 내용 미리보기 (처음 500자)
                if 'data' in results['reporter_result'] and 'report_content' in results['reporter_result']['data']:
                    content = results['reporter_result']['data']['report_content']
                    preview = content[:500] + "..." if len(content) > 500 else content
                    print(f"\n📄 보고서 미리보기:")
                    print("-" * 40)
                    print(preview)
                    print("-" * 40)
                    
                    if 'saved_path' in results['reporter_result']['data']:
                        print(f"\n📁 저장 위치: {results['reporter_result']['data']['saved_path']}")
        
        elif results['status'] == 'failed':
            print(f"❌ 작업 실패: {results.get('error', '알 수 없는 오류')}")
        
        elif results['status'] == 'error': 
            print(f"🚨 시스템 오류: {results.get('error', '알 수 없는 오류')}")
        
        print("="*60)
    
    async def run(self):
        """메인 실행 루프"""
        self.display_welcome()
        
        while True:
            try:
                # 사용자 입력 받기
                print("\n💬 원하는 뉴스 주제나 키워드를 입력하세요:")
                user_input = input("👤 입력: ").strip()
                
                # 종료 명령 처리
                if user_input.lower() in ['quit', 'exit', '종료', 'q']:
                    print("\n👋 시스템을 종료합니다. 감사합니다!")
                    break
                
                # 도움말 처리
                if user_input.lower() in ['help', '도움말', 'h']:
                    self.display_help()
                    continue
                
                # 빈 입력 처리
                if not user_input:
                    print("⚠️ 입력이 비어있습니다. 뉴스 주제나 키워드를 입력해주세요.")
                    continue
                
                # 사용자 요청 처리
                results = await self.process_user_request(user_input)
                
                # 결과 출력
                self.display_results(results)
                
            except KeyboardInterrupt:
                print("\n\n👋 Ctrl+C로 중단되었습니다. 시스템을 종료합니다.")
                break
            except Exception as e:
                print(f"\n❌ 예상치 못한 오류가 발생했습니다: {e}")
                print("다시 시도해주세요.")
    
    def __del__(self):
        """리소스 정리"""
        try:
            if hasattr(self, 'collector'):
                self.collector.cleanup()
        except:
            pass


def main():
    """메인 함수"""
    try:
        app = NewsScrapingChatApp()
        asyncio.run(app.run())
    except Exception as e:
        print(f"❌ 애플리케이션 실행 실패: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()