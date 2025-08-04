#!/usr/bin/env python3
"""
n8n AutoGen 에이전트 테스트 스크립트
각 에이전트의 기능을 개별적으로 테스트할 수 있습니다.
"""

import os
import sys
import json
import time
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.collector_agent import CollectorAgent
from agents.processor_agent import ProcessorAgent
from agents.action_agent import ActionAgent
from agents.reporter_agent import ReporterAgent
from config.agent_config import AgentConfig

def test_collector_agent():
    """수집 에이전트 테스트"""
    print("🧪 수집 에이전트 테스트 시작")
    print("=" * 50)
    
    collector = CollectorAgent()
    
    # 테스트 요청
    test_request = "인공지능 기술 동향 분석"
    
    try:
        result = collector.collect_information(test_request)
        
        print(f"✅ 수집 결과:")
        print(f"  상태: {result['status']}")
        print(f"  메시지: {result['message']}")
        
        if result['status'] == 'success':
            data = result['data']
            print(f"  수집된 사이트 수: {data['collection_summary']['total_sites']}")
            print(f"  성공적 스크래핑: {data['collection_summary']['successful_scrapes']}")
            
            if data['sites_data']:
                print(f"  첫 번째 사이트: {data['sites_data'][0]['url']}")
                
        return result
        
    except Exception as e:
        print(f"❌ 수집 에이전트 테스트 실패: {e}")
        return None
    finally:
        collector.cleanup()

def test_processor_agent():
    """처리 에이전트 테스트"""
    print("\n🧪 처리 에이전트 테스트 시작")
    print("=" * 50)
    
    processor = ProcessorAgent()
    
    # 가짜 수집 데이터 생성
    mock_collection_data = {
        'status': 'success',
        'data': {
            'user_request': '인공지능 기술 동향 분석',
            'collection_summary': {
                'total_sites': 3,
                'successful_scrapes': 2,
                'failed_scrapes': 1
            },
            'sites_data': [
                {
                    'url': 'https://example1.com',
                    'title': 'AI Technology Trends',
                    'content_preview': 'Artificial intelligence is rapidly evolving...',
                    'relevance_score': 0.8
                },
                {
                    'url': 'https://example2.com',
                    'title': 'Machine Learning Advances',
                    'content_preview': 'Recent developments in machine learning...',
                    'relevance_score': 0.7
                }
            ]
        },
        'raw_data': [
            {
                'url': 'https://example1.com',
                'title': 'AI Technology Trends',
                'content': 'Artificial intelligence is rapidly evolving with new breakthroughs in deep learning and neural networks.',
                'status': 'success'
            },
            {
                'url': 'https://example2.com',
                'title': 'Machine Learning Advances',
                'content': 'Recent developments in machine learning show significant improvements in accuracy and efficiency.',
                'status': 'success'
            },
            {
                'url': 'https://example3.com',
                'error': 'Connection timeout',
                'status': 'error'
            }
        ]
    }
    
    try:
        result = processor.process_data(mock_collection_data)
        
        print(f"✅ 처리 결과:")
        print(f"  상태: {result['status']}")
        print(f"  메시지: {result['message']}")
        
        if result['status'] == 'success':
            data = result['data']
            summary = data['processing_summary']
            print(f"  처리된 항목: {summary['total_processed']}")
            print(f"  성공적 처리: {summary['successful_processing']}")
            print(f"  발견된 카테고리: {summary['categories_found']}")
            print(f"  추출된 키워드: {summary['keywords_extracted']}")
            
            # 요약 생성 테스트
            summary_text = processor.generate_summary(data)
            print(f"  생성된 요약:\n{summary_text}")
            
        return result
        
    except Exception as e:
        print(f"❌ 처리 에이전트 테스트 실패: {e}")
        return None

def test_action_agent():
    """행동 에이전트 테스트"""
    print("\n🧪 행동 에이전트 테스트 시작")
    print("=" * 50)
    
    action_executor = ActionAgent()
    
    # 가짜 처리 데이터 생성
    mock_processing_data = {
        'status': 'success',
        'data': {
            'structured_data': {
                'total_sites': 3,
                'successful_scrapes': 2,
                'failed_scrapes': 1,
                'categories': {'technology': 2},
                'keywords': [('ai', 5), ('machine learning', 3), ('technology', 2)],
                'summaries': [
                    {
                        'url': 'https://example1.com',
                        'title': 'AI Technology Trends',
                        'summary': 'AI is rapidly evolving...',
                        'category': 'technology',
                        'keywords': ['ai', 'technology', 'trends']
                    }
                ]
            },
            'insights': [
                '스크래핑 성공률: 66.7%',
                '주요 카테고리: technology',
                '주요 키워드: ai, machine learning, technology'
            ],
            'ai_analysis': {
                'data_quality': {
                    'overall_score': 0.67,
                    'coverage': 'moderate',
                    'completeness': 0.67
                },
                'actionable_insights': [
                    "'ai' 키워드를 중심으로 추가 정보 수집 권장",
                    "technology 분야에 대한 심화 분석 필요"
                ]
            },
            'processing_summary': {
                'total_processed': 3,
                'successful_processing': 2,
                'categories_found': 1,
                'keywords_extracted': 3
            }
        }
    }
    
    try:
        result = action_executor.execute_actions(mock_processing_data, '인공지능 기술 동향 분석')
        
        print(f"✅ 행동 실행 결과:")
        print(f"  상태: {result['status']}")
        print(f"  메시지: {result['message']}")
        
        if result['status'] == 'success':
            data = result['data']
            action_results = data['action_results']
            print(f"  총 행동 수: {action_results['total_actions']}")
            print(f"  성공적 행동: {action_results['successful_actions']}")
            print(f"  성공률: {action_results['success_rate']:.1%}")
            print(f"  사용자 만족도: {action_results['user_request_satisfaction']}")
            
        return result
        
    except Exception as e:
        print(f"❌ 행동 에이전트 테스트 실패: {e}")
        return None

def test_reporter_agent():
    """보고서 에이전트 테스트"""
    print("\n🧪 보고서 에이전트 테스트 시작")
    print("=" * 50)
    
    reporter = ReporterAgent()
    
    # 가짜 전체 데이터 생성
    mock_all_data = {
        'user_request': '인공지능 기술 동향 분석',
        'collection_data': {
            'status': 'success',
            'message': '3개 웹사이트에서 정보를 수집했습니다.',
            'data': {
                'collection_summary': {
                    'total_sites': 3,
                    'successful_scrapes': 2,
                    'failed_scrapes': 1
                }
            }
        },
        'processing_data': {
            'status': 'success',
            'message': '데이터 처리가 완료되었습니다.',
            'data': {
                'processing_summary': {
                    'total_processed': 3,
                    'successful_processing': 2,
                    'categories_found': 1,
                    'keywords_extracted': 3
                }
            }
        },
        'action_data': {
            'status': 'success',
            'message': '3개의 행동을 수행했습니다.',
            'data': {
                'action_results': {
                    'total_actions': 3,
                    'successful_actions': 3,
                    'success_rate': 1.0
                }
            }
        }
    }
    
    try:
        result = reporter.generate_report(mock_all_data, '인공지능 기술 동향 분석')
        
        print(f"✅ 보고서 생성 결과:")
        print(f"  상태: {result['status']}")
        print(f"  메시지: {result['message']}")
        
        if result['status'] == 'success':
            data = result['data']
            report = data['report']
            export_formats = data['export_formats']
            
            print(f"  보고서 제목: {report['title']}")
            print(f"  섹션 수: {report['summary']['total_sections']}")
            print(f"  주요 하이라이트: {report['summary']['key_highlights']}")
            
            print(f"  내보내기 형식:")
            for format_name, format_data in export_formats.items():
                print(f"    - {format_name}: {format_data['filename']}")
                
        return result
        
    except Exception as e:
        print(f"❌ 보고서 에이전트 테스트 실패: {e}")
        return None

def test_full_workflow():
    """전체 워크플로우 테스트"""
    print("\n🧪 전체 워크플로우 테스트 시작")
    print("=" * 50)
    
    # 각 에이전트 테스트 실행
    collection_result = test_collector_agent()
    
    if collection_result and collection_result['status'] == 'success':
        processing_result = test_processor_agent()
        
        if processing_result and processing_result['status'] == 'success':
            action_result = test_action_agent()
            
            if action_result and action_result['status'] == 'success':
                # 전체 데이터 통합
                all_data = {
                    'user_request': '인공지능 기술 동향 분석',
                    'collection_data': collection_result,
                    'processing_data': processing_result,
                    'action_data': action_result
                }
                
                report_result = test_reporter_agent()
                
                if report_result and report_result['status'] == 'success':
                    print("\n✅ 전체 워크플로우 테스트 성공!")
                    return True
                    
    print("\n❌ 전체 워크플로우 테스트 실패")
    return False

def test_configuration():
    """설정 테스트"""
    print("🧪 설정 테스트")
    print("=" * 50)
    
    config = AgentConfig()
    
    print(f"OpenAI API Key 설정: {'✅' if config.OPENAI_API_KEY else '❌'}")
    print(f"n8n Webhook URL 설정: {'✅' if config.N8N_WEBHOOK_URL else '❌'}")
    print(f"최대 스크래핑 페이지: {config.MAX_PAGES_TO_SCRAPE}")
    print(f"요청 타임아웃: {config.REQUEST_TIMEOUT}초")
    print(f"최대 콘텐츠 길이: {config.MAX_CONTENT_LENGTH}")
    print(f"요약 길이: {config.SUMMARIZATION_LENGTH}")
    
    return config.OPENAI_API_KEY is not None

def main():
    """메인 테스트 함수"""
    print("🚀 n8n AutoGen 에이전트 테스트 시작")
    print("=" * 60)
    
    # 설정 테스트
    if not test_configuration():
        print("\n⚠️  OpenAI API Key가 설정되지 않았습니다.")
        print("   .env 파일에 OPENAI_API_KEY를 설정하세요.")
        return
        
    # 개별 에이전트 테스트
    test_collector_agent()
    test_processor_agent()
    test_action_agent()
    test_reporter_agent()
    
    # 전체 워크플로우 테스트
    test_full_workflow()
    
    print("\n" + "=" * 60)
    print("🎉 모든 테스트 완료!")

if __name__ == '__main__':
    main() 