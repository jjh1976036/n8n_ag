#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
간단한 기능 테스트 스크립트 - 실제 채팅 앱 워크플로우 테스트
"""

import sys
import os
import asyncio
from datetime import datetime

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_single_agent():
    """개별 에이전트 테스트"""
    print("\n🤖 개별 에이전트 기능 테스트")
    print("-" * 50)
    
    test_request = "AI 기술 뉴스"
    
    # 1. CollectorAgent 테스트
    print("\n1️⃣ CollectorAgent 테스트")
    try:
        from agents.collector_agent import CollectorAgent
        collector = CollectorAgent()
        print("   ✅ CollectorAgent 초기화 성공")
        
        # Mock 데이터로 테스트
        mock_result = {
            'status': 'success',
            'message': '테스트용 데이터 수집 완료',
            'data': {
                'collection_summary': {
                    'total_sites': 3,
                    'successful_scrapes': 2,
                    'failed_scrapes': 1
                },
                'sites_data': [
                    {
                        'url': 'https://example1.com',
                        'title': 'AI 기술 동향',
                        'content_preview': 'AI 기술이 빠르게 발전하고 있습니다...',
                        'relevance_score': 0.8
                    },
                    {
                        'url': 'https://example2.com', 
                        'title': '머신러닝 최신 소식',
                        'content_preview': '머신러닝 분야의 새로운 breakthrough...',
                        'relevance_score': 0.7
                    }
                ]
            },
            'raw_data': [
                {
                    'status': 'success',
                    'url': 'https://example1.com',
                    'title': 'AI 기술 동향',
                    'content': 'AI 기술이 빠르게 발전하고 있습니다. 특히 자연어처리와 컴퓨터 비전 분야에서...'
                },
                {
                    'status': 'success', 
                    'url': 'https://example2.com',
                    'title': '머신러닝 최신 소식',
                    'content': '머신러닝 분야의 새로운 breakthrough가 발표되었습니다...'
                }
            ]
        }
        print("   ✅ CollectorAgent Mock 테스트 성공")
        return mock_result
        
    except Exception as e:
        print(f"   ❌ CollectorAgent 테스트 실패: {e}")
        return None

async def test_processor_agent(collector_result):
    """ProcessorAgent 테스트"""
    print("\n2️⃣ ProcessorAgent 테스트")
    
    if not collector_result:
        print("   ❌ Collector 결과가 없어 테스트 불가")
        return None
        
    try:
        from agents.processor_agent import ProcessorAgent
        processor = ProcessorAgent()
        print("   ✅ ProcessorAgent 초기화 성공")
        
        result = processor.process_data(collector_result)
        print(f"   ✅ 데이터 처리 완료: {result['status']}")
        return result
        
    except Exception as e:
        print(f"   ❌ ProcessorAgent 테스트 실패: {e}")
        return None

async def test_action_agent(processor_result, user_request):
    """ActionAgent 테스트"""
    print("\n3️⃣ ActionAgent 테스트")
    
    if not processor_result:
        print("   ❌ Processor 결과가 없어 테스트 불가")
        return None
        
    try:
        from agents.action_agent import ActionAgent
        action = ActionAgent()
        print("   ✅ ActionAgent 초기화 성공")
        
        result = action.execute_action(processor_result, user_request)
        print(f"   ✅ 액션 실행 완료: {result['status']}")
        return result
        
    except Exception as e:
        print(f"   ❌ ActionAgent 테스트 실패: {e}")
        return None

async def test_reporter_agent(collector_result, processor_result, action_result, user_request):
    """ReporterAgent 테스트"""
    print("\n4️⃣ ReporterAgent 테스트")
    
    if not all([collector_result, processor_result, action_result]):
        print("   ❌ 이전 단계 결과가 없어 테스트 불가")
        return None
        
    try:
        from agents.reporter_agent import ReporterAgent
        reporter = ReporterAgent()
        print("   ✅ ReporterAgent 초기화 성공")
        
        result = reporter.generate_report(
            collector_result, processor_result, action_result, user_request
        )
        print(f"   ✅ 보고서 생성 완료: {result['status']}")
        return result
        
    except Exception as e:
        print(f"   ❌ ReporterAgent 테스트 실패: {e}")
        return None

async def test_full_workflow():
    """전체 워크플로우 테스트"""
    print("\n🔄 전체 워크플로우 테스트")
    print("=" * 60)
    
    user_request = "AI 기술 뉴스"
    
    # 1단계: 정보 수집
    collector_result = await test_single_agent()
    
    # 2단계: 데이터 처리
    processor_result = await test_processor_agent(collector_result)
    
    # 3단계: 액션 실행
    action_result = await test_action_agent(processor_result, user_request)
    
    # 4단계: 보고서 생성
    reporter_result = await test_reporter_agent(
        collector_result, processor_result, action_result, user_request
    )
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약")
    print("-" * 60)
    
    results = {
        'CollectorAgent': collector_result is not None,
        'ProcessorAgent': processor_result is not None, 
        'ActionAgent': action_result is not None,
        'ReporterAgent': reporter_result is not None
    }
    
    for agent, success in results.items():
        status = "✅ 성공" if success else "❌ 실패"
        print(f"{agent}: {status}")
    
    overall_success = all(results.values())
    print(f"\n전체 워크플로우: {'✅ 성공!' if overall_success else '❌ 일부 실패'}")
    
    if overall_success:
        print("\n🎉 모든 테스트가 성공했습니다!")
        print("💡 이제 실제 채팅 애플리케이션을 실행할 수 있습니다:")
        print("   python chat_main.py")
    else:
        print("\n⚠️ 일부 테스트가 실패했습니다.")
        print("💡 실패한 컴포넌트를 먼저 수정해주세요.")

def test_file_operations():
    """파일 작업 테스트"""
    print("\n📁 파일 작업 테스트")
    print("-" * 50)
    
    # 디렉토리 생성 테스트
    dirs = ["saved_reports", "reports"]
    for dir_name in dirs:
        try:
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
            print(f"✅ {dir_name} 디렉토리 준비 완료")
        except Exception as e:
            print(f"❌ {dir_name} 디렉토리 생성 실패: {e}")
    
    # 테스트 파일 생성
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_file = f"saved_reports/test_{timestamp}.json"
        
        test_data = {
            "test": True,
            "timestamp": datetime.now().isoformat(),
            "message": "파일 작업 테스트"
        }
        
        import json
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
            
        print(f"✅ 테스트 파일 생성 성공: {test_file}")
        
    except Exception as e:
        print(f"❌ 테스트 파일 생성 실패: {e}")

async def main():
    """메인 테스트 함수"""
    print("🧪 간단한 기능 테스트 시작")
    print("=" * 60)
    print("📌 이 테스트는 Mock 데이터를 사용하여 전체 워크플로우를 확인합니다.")
    print("📌 실제 웹 스크래핑이나 API 호출은 수행하지 않습니다.")
    print()
    
    # 파일 작업 테스트
    test_file_operations()
    
    # 전체 워크플로우 테스트
    await test_full_workflow()
    
    print("\n" + "=" * 60)
    print("🏁 간단한 기능 테스트 완료!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 테스트가 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 테스트 실행 중 오류: {e}")
        sys.exit(1)