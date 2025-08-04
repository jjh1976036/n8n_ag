from autogen_core.models import ChatCompletionClient
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
import json
from typing import List, Dict, Any
from config.agent_config import AgentConfig

class ReporterAgent:
    """보고서 생성 에이전트"""
    
    def __init__(self):
        self.config = AgentConfig()
        
        # ChatCompletionClient 생성 - 올바른 API 사용
        self.model_client = None
        
        # 방법 1: OpenAIChatCompletionClient 시도
        try:
            from autogen_ext.models.openai import OpenAIChatCompletionClient
            self.model_client = OpenAIChatCompletionClient(
                model=self.config.OPENAI_MODEL,
                api_key=self.config.OPENAI_API_KEY,
                base_url="https://api.openai.com/v1"
            )
            print("✅ OpenAIChatCompletionClient 생성 성공")
        except ImportError as e:
            print(f"⚠️ autogen_ext.models.openai import 실패: {e}")
            print("💡 tiktoken 패키지가 필요할 수 있습니다.")
        except Exception as e:
            print(f"⚠️ OpenAIChatCompletionClient 생성 실패: {e}")
        
        # 방법 2: 모의 클라이언트 사용 (fallback)
        if self.model_client is None:
            print("⚠️ 모의 모델 클라이언트를 사용합니다...")
            
            class MockChatCompletionClient:
                def __init__(self, model, api_key, base_url):
                    self.model = model
                    self.api_key = api_key
                    self.base_url = base_url
                
                def create(self, messages, **kwargs):
                    return {"choices": [{"message": {"content": "Mock response"}}]}
                
                def create_stream(self, messages, **kwargs):
                    return iter([{"choices": [{"message": {"content": "Mock stream"}}]}])
            
            self.model_client = MockChatCompletionClient(
                model=self.config.OPENAI_MODEL,
                api_key=self.config.OPENAI_API_KEY,
                base_url="https://api.openai.com/v1"
            )
            print("✅ 모의 모델 클라이언트 생성 성공")
        
        # 보고서 에이전트 생성
        try:
            self.reporter = AssistantAgent(
                name=self.config.REPORTER_AGENT_NAME,
                model_client=self.model_client,
                system_message=self.config.SYSTEM_MESSAGES["reporter"]
            )
            
            # 사용자 프록시 에이전트 - model_client 없이 생성
            try:
                self.user_proxy = UserProxyAgent(
                    name="user_proxy"
                )
            except Exception as e:
                print(f"⚠️ UserProxyAgent 생성 실패, 기본 생성자 사용: {e}")
                self.user_proxy = UserProxyAgent()
            
            print("✅ 보고서 에이전트 생성 성공")
        except Exception as e:
            print(f"❌ 보고서 에이전트 생성 실패: {e}")
            self.reporter = None
            self.user_proxy = None
        
    def generate_report(self, all_data: Dict[str, Any], user_request: str) -> Dict[str, Any]:
        """전체 데이터를 바탕으로 최종 보고서 생성"""
        print(f"📊 보고서 생성 시작")
        
        # 1. 데이터 통합 및 정리
        integrated_data = self._integrate_all_data(all_data)
        
        # 2. 보고서 구조 생성
        report_structure = self._create_report_structure(integrated_data, user_request)
        
        # 3. 각 섹션 작성
        report_content = self._write_report_sections(report_structure, integrated_data)
        
        # 4. 최종 보고서 조합
        final_report = self._compile_final_report(report_content, user_request)
        
        # 5. 다양한 형식으로 내보내기
        export_formats = self._export_report(final_report)
        
        return {
            'status': 'success',
            'message': '보고서 생성이 완료되었습니다.',
            'data': {
                'report': final_report,
                'export_formats': export_formats
            }
        }
        
    def _integrate_all_data(self, all_data: Dict[str, Any]) -> Dict[str, Any]:
        """모든 에이전트의 데이터 통합"""
        integrated = {
            'user_request': all_data.get('user_request', ''),
            'collection_data': all_data.get('collection_data', {}),
            'processing_data': all_data.get('processing_data', {}),
            'action_data': all_data.get('action_data', {}),
            'metadata': {
                'timestamp': self._get_current_timestamp(),
                'total_agents': 4,
                'workflow_status': 'completed'
            }
        }
        
        return integrated
        
    def _create_report_structure(self, integrated_data: Dict[str, Any], user_request: str) -> Dict[str, Any]:
        """보고서 구조 생성"""
        structure = {
            'title': f"웹 정보 수집 및 분석 보고서 - {user_request[:50]}...",
            'sections': [
                {
                    'id': 'executive_summary',
                    'title': '실행 요약',
                    'type': 'summary',
                    'priority': 'high'
                },
                {
                    'id': 'methodology',
                    'title': '방법론',
                    'type': 'process',
                    'priority': 'medium'
                },
                {
                    'id': 'findings',
                    'title': '주요 발견사항',
                    'type': 'analysis',
                    'priority': 'high'
                },
                {
                    'id': 'insights',
                    'title': '인사이트 및 분석',
                    'type': 'insights',
                    'priority': 'high'
                },
                {
                    'id': 'recommendations',
                    'title': '권장사항',
                    'type': 'recommendations',
                    'priority': 'high'
                },
                {
                    'id': 'technical_details',
                    'title': '기술적 세부사항',
                    'type': 'technical',
                    'priority': 'low'
                },
                {
                    'id': 'appendix',
                    'title': '부록',
                    'type': 'appendix',
                    'priority': 'low'
                }
            ]
        }
        
        return structure
        
    def _write_report_sections(self, structure: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
        """각 섹션 작성"""
        report_content = {}
        
        for section in structure['sections']:
            section_id = section['id']
            print(f"📝 섹션 작성 중: {section['title']}")
            
            if section_id == 'executive_summary':
                report_content[section_id] = self._write_executive_summary(data)
            elif section_id == 'methodology':
                report_content[section_id] = self._write_methodology(data)
            elif section_id == 'findings':
                report_content[section_id] = self._write_findings(data)
            elif section_id == 'insights':
                report_content[section_id] = self._write_insights(data)
            elif section_id == 'recommendations':
                report_content[section_id] = self._write_recommendations(data)
            elif section_id == 'technical_details':
                report_content[section_id] = self._write_technical_details(data)
            elif section_id == 'appendix':
                report_content[section_id] = self._write_appendix(data)
                
        return report_content
        
    def _write_executive_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """실행 요약 작성"""
        collection_data = data.get('collection_data', {})
        processing_data = data.get('processing_data', {})
        action_data = data.get('action_data', {})
        
        # 수집 요약
        collection_summary = collection_data.get('data', {}).get('collection_summary', {})
        total_sites = collection_summary.get('total_sites', 0)
        successful_scrapes = collection_summary.get('successful_scrapes', 0)
        
        # 처리 요약
        processing_summary = processing_data.get('data', {}).get('processing_summary', {})
        categories_found = processing_summary.get('categories_found', 0)
        keywords_extracted = processing_summary.get('keywords_extracted', 0)
        
        # 행동 요약
        action_results = action_data.get('data', {}).get('action_results', {})
        total_actions = action_results.get('total_actions', 0)
        successful_actions = action_results.get('successful_actions', 0)
        
        summary = {
            'overview': f"본 보고서는 사용자 요청 '{data.get('user_request', '')}'에 대한 웹 정보 수집 및 분석 결과입니다.",
            'key_metrics': {
                'websites_analyzed': total_sites,
                'successful_scrapes': successful_scrapes,
                'success_rate': f"{successful_scrapes/total_sites*100:.1f}%" if total_sites > 0 else "0%",
                'categories_discovered': categories_found,
                'keywords_extracted': keywords_extracted,
                'actions_executed': successful_actions
            },
            'main_conclusions': [
                f"{total_sites}개 웹사이트에서 정보를 성공적으로 수집했습니다.",
                f"{categories_found}개의 주요 카테고리를 발견했습니다.",
                f"{keywords_extracted}개의 키워드를 추출하여 분석했습니다.",
                f"{successful_actions}개의 행동을 성공적으로 수행했습니다."
            ]
        }
        
        return summary
        
    def _write_methodology(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """방법론 작성"""
        methodology = {
            'workflow_overview': {
                'step1': '정보 수집 (Collection)',
                'step2': '데이터 처리 (Processing)',
                'step3': '행동 수행 (Action)',
                'step4': '보고서 생성 (Reporting)'
            },
            'agents_used': [
                {
                    'name': 'WebCollector',
                    'role': '웹 정보 수집',
                    'capabilities': ['웹사이트 검색', '콘텐츠 스크래핑', '데이터 구조화']
                },
                {
                    'name': 'DataProcessor',
                    'role': '데이터 처리 및 분석',
                    'capabilities': ['키워드 추출', '카테고리 분류', '인사이트 생성']
                },
                {
                    'name': 'ActionExecutor',
                    'role': '행동 계획 및 실행',
                    'capabilities': ['행동 계획 수립', '다양한 행동 실행', '결과 평가']
                },
                {
                    'name': 'ReportGenerator',
                    'role': '보고서 생성',
                    'capabilities': ['데이터 통합', '보고서 작성', '다양한 형식 내보내기']
                }
            ],
            'technologies': [
                'AutoGen (AI 에이전트 프레임워크)',
                'BeautifulSoup (웹 스크래핑)',
                'Selenium (동적 콘텐츠 처리)',
                'OpenAI GPT-4 (자연어 처리)',
                'n8n (워크플로우 자동화)'
            ]
        }
        
        return methodology
        
    def _write_findings(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """주요 발견사항 작성"""
        processing_data = data.get('processing_data', {}).get('data', {})
        structured_data = processing_data.get('structured_data', {})
        insights = processing_data.get('insights', [])
        
        findings = {
            'data_collection_findings': {
                'total_sites_analyzed': structured_data.get('total_sites', 0),
                'successful_scrapes': structured_data.get('successful_scrapes', 0),
                'failed_scrapes': structured_data.get('failed_scrapes', 0),
                'success_rate': f"{structured_data.get('successful_scrapes', 0)/structured_data.get('total_sites', 1)*100:.1f}%"
            },
            'content_analysis_findings': {
                'categories_discovered': structured_data.get('categories', {}),
                'top_keywords': [kw for kw, freq in structured_data.get('keywords', [])[:10]],
                'content_summaries': structured_data.get('summaries', [])[:5]  # 상위 5개만
            },
            'key_insights': insights[:5] if insights else []
        }
        
        return findings
        
    def _write_insights(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """인사이트 및 분석 작성"""
        processing_data = data.get('processing_data', {}).get('data', {})
        ai_analysis = processing_data.get('ai_analysis', {})
        
        insights = {
            'data_quality_insights': {
                'overall_score': ai_analysis.get('data_quality', {}).get('overall_score', 0),
                'coverage_level': ai_analysis.get('data_quality', {}).get('coverage', 'unknown'),
                'completeness': ai_analysis.get('data_quality', {}).get('completeness', 0)
            },
            'trend_analysis': {
                'patterns_identified': ai_analysis.get('trends_patterns', []),
                'correlation_findings': '주요 키워드와 카테고리 간 상관관계 분석 결과'
            },
            'relevance_assessment': {
                'keyword_overlap': ai_analysis.get('relevance_assessment', {}).get('keyword_overlap', 0),
                'relevance_score': ai_analysis.get('relevance_assessment', {}).get('relevance_score', 0),
                'coverage_level': ai_analysis.get('relevance_assessment', {}).get('coverage_level', 'unknown')
            },
            'actionable_insights': ai_analysis.get('actionable_insights', []),
            'gaps_identified': ai_analysis.get('gaps_identified', [])
        }
        
        return insights
        
    def _write_recommendations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """권장사항 작성"""
        processing_data = data.get('processing_data', {}).get('data', {})
        action_data = data.get('action_data', {}).get('data', {})
        
        # 처리된 데이터에서 권장사항 추출
        structured_data = processing_data.get('structured_data', {})
        ai_analysis = processing_data.get('ai_analysis', {})
        
        # 행동 결과에서 추가 권장사항 추출
        executed_actions = action_data.get('executed_actions', [])
        
        recommendations = {
            'immediate_actions': [
                "주요 키워드를 중심으로 한 추가 정보 수집",
                "발견된 카테고리에 대한 심화 분석 수행"
            ],
            'strategic_recommendations': [
                "웹사이트 접근성 개선을 위한 스크래핑 전략 최적화",
                "더 다양한 소스에서 정보 수집 확대"
            ],
            'long_term_improvements': [
                "AI 모델 성능 향상을 위한 데이터 품질 개선",
                "자동화된 모니터링 시스템 구축"
            ],
            'technical_recommendations': [
                "동적 콘텐츠 처리 능력 강화",
                "실시간 데이터 업데이트 시스템 구축"
            ]
        }
        
        # 데이터 품질 기반 권장사항 추가
        success_rate = structured_data.get('successful_scrapes', 0) / structured_data.get('total_sites', 1)
        if success_rate < 0.7:
            recommendations['immediate_actions'].append("스크래핑 성공률 개선을 위한 기술적 최적화")
            
        return recommendations
        
    def _write_technical_details(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """기술적 세부사항 작성"""
        technical_details = {
            'system_architecture': {
                'framework': 'AutoGen Multi-Agent System',
                'language': 'Python 3.8+',
                'ai_model': 'OpenAI GPT-4',
                'web_scraping': 'BeautifulSoup + Selenium',
                'workflow_automation': 'n8n'
            },
            'performance_metrics': {
                'processing_time': '실행 시간 측정 결과',
                'memory_usage': '메모리 사용량',
                'api_calls': 'API 호출 횟수'
            },
            'data_flow': {
                'collection_phase': '웹 스크래핑 및 데이터 수집',
                'processing_phase': '데이터 정리 및 분석',
                'action_phase': '행동 계획 및 실행',
                'reporting_phase': '보고서 생성 및 내보내기'
            },
            'error_handling': {
                'scraping_errors': '스크래핑 오류 처리 방식',
                'processing_errors': '데이터 처리 오류 처리',
                'recovery_strategies': '오류 복구 전략'
            }
        }
        
        return technical_details
        
    def _write_appendix(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """부록 작성"""
        collection_data = data.get('collection_data', {}).get('data', {})
        processing_data = data.get('processing_data', {}).get('data', {})
        
        appendix = {
            'raw_data_samples': {
                'scraped_sites': collection_data.get('sites_data', [])[:3],  # 상위 3개만
                'processing_results': processing_data.get('structured_data', {}).get('summaries', [])[:3]
            },
            'metadata': {
                'timestamp': data.get('metadata', {}).get('timestamp', ''),
                'total_agents': data.get('metadata', {}).get('total_agents', 0),
                'workflow_status': data.get('metadata', {}).get('workflow_status', '')
            },
            'configuration': {
                'max_sites': AgentConfig.MAX_PAGES_TO_SCRAPE,
                'timeout': AgentConfig.REQUEST_TIMEOUT,
                'max_content_length': AgentConfig.MAX_CONTENT_LENGTH
            }
        }
        
        return appendix
        
    def _compile_final_report(self, report_content: Dict[str, Any], user_request: str) -> Dict[str, Any]:
        """최종 보고서 조합"""
        final_report = {
            'title': f"웹 정보 수집 및 분석 보고서",
            'subtitle': f"사용자 요청: {user_request}",
            'timestamp': self._get_current_timestamp(),
            'version': '1.0',
            'sections': report_content,
            'summary': {
                'total_sections': len(report_content),
                'report_length': sum(len(str(content)) for content in report_content.values()),
                'key_highlights': self._extract_key_highlights(report_content)
            }
        }
        
        return final_report
        
    def _extract_key_highlights(self, report_content: Dict[str, Any]) -> List[str]:
        """주요 하이라이트 추출"""
        highlights = []
        
        # 실행 요약에서 주요 지표 추출
        exec_summary = report_content.get('executive_summary', {})
        key_metrics = exec_summary.get('key_metrics', {})
        
        if key_metrics:
            highlights.append(f"분석된 웹사이트: {key_metrics.get('websites_analyzed', 0)}개")
            highlights.append(f"스크래핑 성공률: {key_metrics.get('success_rate', '0%')}")
            highlights.append(f"발견된 카테고리: {key_metrics.get('categories_discovered', 0)}개")
            
        # 주요 발견사항에서 하이라이트 추출
        findings = report_content.get('findings', {})
        if findings.get('key_insights'):
            highlights.extend(findings['key_insights'][:2])
            
        return highlights
        
    def _export_report(self, final_report: Dict[str, Any]) -> Dict[str, Any]:
        """다양한 형식으로 보고서 내보내기"""
        export_formats = {}
        
        # JSON 형식
        export_formats['json'] = {
            'content': json.dumps(final_report, ensure_ascii=False, indent=2),
            'filename': f"report_{self._get_timestamp_for_filename()}.json"
        }
        
        # 텍스트 형식
        text_content = self._convert_to_text(final_report)
        export_formats['text'] = {
            'content': text_content,
            'filename': f"report_{self._get_timestamp_for_filename()}.txt"
        }
        
        # 마크다운 형식
        markdown_content = self._convert_to_markdown(final_report)
        export_formats['markdown'] = {
            'content': markdown_content,
            'filename': f"report_{self._get_timestamp_for_filename()}.md"
        }
        
        return export_formats
        
    def _convert_to_text(self, report: Dict[str, Any]) -> str:
        """보고서를 텍스트 형식으로 변환"""
        text_lines = []
        
        # 제목
        text_lines.append(f"제목: {report['title']}")
        text_lines.append(f"부제목: {report['subtitle']}")
        text_lines.append(f"생성일시: {report['timestamp']}")
        text_lines.append("=" * 50)
        text_lines.append("")
        
        # 각 섹션
        for section_name, section_content in report['sections'].items():
            text_lines.append(f"[{section_name.upper()}]")
            text_lines.append("-" * 30)
            
            if isinstance(section_content, dict):
                for key, value in section_content.items():
                    if isinstance(value, list):
                        text_lines.append(f"{key}:")
                        for item in value:
                            text_lines.append(f"  - {item}")
                    elif isinstance(value, dict):
                        text_lines.append(f"{key}:")
                        for sub_key, sub_value in value.items():
                            text_lines.append(f"  {sub_key}: {sub_value}")
                    else:
                        text_lines.append(f"{key}: {value}")
            else:
                text_lines.append(str(section_content))
                
            text_lines.append("")
            
        return "\n".join(text_lines)
        
    def _convert_to_markdown(self, report: Dict[str, Any]) -> str:
        """보고서를 마크다운 형식으로 변환"""
        md_lines = []
        
        # 제목
        md_lines.append(f"# {report['title']}")
        md_lines.append(f"## {report['subtitle']}")
        md_lines.append(f"**생성일시:** {report['timestamp']}")
        md_lines.append("")
        
        # 목차
        md_lines.append("## 목차")
        for section_name in report['sections'].keys():
            md_lines.append(f"- [{section_name.title()}](#{section_name})")
        md_lines.append("")
        
        # 각 섹션
        for section_name, section_content in report['sections'].items():
            md_lines.append(f"## {section_name.title()}")
            md_lines.append("")
            
            if isinstance(section_content, dict):
                for key, value in section_content.items():
                    md_lines.append(f"### {key}")
                    md_lines.append("")
                    
                    if isinstance(value, list):
                        for item in value:
                            md_lines.append(f"- {item}")
                    elif isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            md_lines.append(f"**{sub_key}:** {sub_value}")
                    else:
                        md_lines.append(str(value))
                        
                    md_lines.append("")
            else:
                md_lines.append(str(section_content))
                md_lines.append("")
                
        return "\n".join(md_lines)
        
    def _get_current_timestamp(self) -> str:
        """현재 타임스탬프 반환"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def _get_timestamp_for_filename(self) -> str:
        """파일명용 타임스탬프 반환"""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def get_agent_info(self) -> Dict[str, Any]:
        """에이전트 정보 반환"""
        return {
            'name': self.config.REPORTER_AGENT_NAME,
            'description': '보고서 생성 및 문서화 전문가',
            'capabilities': [
                '데이터 통합 및 정리',
                '구조화된 보고서 작성',
                '다양한 형식 내보내기',
                '자동화된 문서 생성',
                '사용자 친화적 보고서 작성'
            ]
        } 