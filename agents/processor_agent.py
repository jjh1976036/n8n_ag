from autogen_core.models import ChatCompletionClient
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from typing import List, Dict, Any
from config.agent_config import AgentConfig

class ProcessorAgent:
    """데이터 처리 에이전트"""
    
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
        
        # 처리 에이전트 생성
        try:
            self.processor = AssistantAgent(
                name=self.config.PROCESSOR_AGENT_NAME,
                model_client=self.model_client,
                system_message=self.config.SYSTEM_MESSAGES["processor"]
            )
            
            # 사용자 프록시 에이전트 - model_client 없이 생성
            try:
                self.user_proxy = UserProxyAgent(
                    name="user_proxy"
                )
            except Exception as e:
                print(f"⚠️ UserProxyAgent 생성 실패, 기본 생성자 사용: {e}")
                self.user_proxy = UserProxyAgent()
            
            print("✅ 처리 에이전트 생성 성공")
        except Exception as e:
            print(f"❌ 처리 에이전트 생성 실패: {e}")
            self.processor = None
            self.user_proxy = None
        
    def process_data(self, collected_data: Dict[str, Any]) -> Dict[str, Any]:
        """수집된 데이터 처리 및 분석"""
        print(f"🔧 데이터 처리 시작")
        
        if collected_data['status'] != 'success':
            return {
                'status': 'error',
                'message': '수집된 데이터가 없어 처리할 수 없습니다.',
                'data': {}
            }
            
        # 1. 원시 데이터 구조화
        raw_data = collected_data.get('raw_data', [])
        structured_data = self._structure_data(raw_data)
        
        # 2. 인사이트 생성
        insights = self._generate_insights(structured_data)
        
        # 3. AI 기반 추가 분석
        ai_analysis = self._perform_ai_analysis(structured_data, collected_data['data']['user_request'])
        
        # 4. 처리 결과 통합
        processed_data = {
            'structured_data': structured_data,
            'insights': insights,
            'ai_analysis': ai_analysis,
            'processing_summary': {
                'total_processed': len(raw_data),
                'successful_processing': structured_data['successful_scrapes'],
                'categories_found': len(structured_data['categories']),
                'keywords_extracted': len(structured_data['keywords'])
            }
        }
        
        print(f"✅ 데이터 처리 완료: {processed_data['processing_summary']['successful_processing']}개 항목 처리됨")
        
        return {
            'status': 'success',
            'message': '데이터 처리가 완료되었습니다.',
            'data': processed_data
        }
        
    def _structure_data(self, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """원시 데이터를 구조화된 형태로 변환"""
        structured_data = {
            'total_sites': len(raw_data),
            'successful_scrapes': 0,
            'categories': {},
            'keywords': [],
            'summaries': [],
            'urls': []
        }
        
        # 성공적인 스크래핑 데이터 처리
        for data in raw_data:
            if data['status'] == 'success':
                structured_data['successful_scrapes'] += 1
                structured_data['urls'].append(data['url'])
                
                # 카테고리 분류 (간단한 규칙 기반)
                content = data.get('content', '').lower()
                if 'ai' in content or 'artificial' in content or 'intelligence' in content:
                    structured_data['categories']['AI/ML'] = structured_data['categories'].get('AI/ML', 0) + 1
                elif 'tech' in content or 'technology' in content:
                    structured_data['categories']['Technology'] = structured_data['categories'].get('Technology', 0) + 1
                elif 'business' in content or 'company' in content:
                    structured_data['categories']['Business'] = structured_data['categories'].get('Business', 0) + 1
                else:
                    structured_data['categories']['General'] = structured_data['categories'].get('General', 0) + 1
                
                # 키워드 추출
                keywords = self._extract_keywords(data.get('content', ''))
                for keyword in keywords:
                    # 키워드 빈도 계산
                    found = False
                    for i, (kw, freq) in enumerate(structured_data['keywords']):
                        if kw == keyword:
                            structured_data['keywords'][i] = (kw, freq + 1)
                            found = True
                            break
                    if not found:
                        structured_data['keywords'].append((keyword, 1))
                
                # 요약 생성
                summary = data.get('content', '')[:200] + "..." if len(data.get('content', '')) > 200 else data.get('content', '')
                structured_data['summaries'].append(summary)
        
        # 키워드 빈도순 정렬
        structured_data['keywords'].sort(key=lambda x: x[1], reverse=True)
        
        return structured_data
        
    def _generate_insights(self, structured_data: Dict[str, Any]) -> List[str]:
        """구조화된 데이터에서 인사이트 생성"""
        insights = []
        
        # 성공률 인사이트
        success_rate = structured_data['successful_scrapes'] / structured_data['total_sites']
        if success_rate > 0.8:
            insights.append("높은 스크래핑 성공률로 데이터 품질이 우수합니다.")
        elif success_rate < 0.5:
            insights.append("스크래핑 성공률이 낮아 추가 데이터 수집이 필요합니다.")
        
        # 카테고리 인사이트
        if structured_data['categories']:
            top_category = max(structured_data['categories'], key=structured_data['categories'].get)
            insights.append(f"'{top_category}' 분야가 가장 많이 다뤄지고 있습니다.")
        
        # 키워드 인사이트
        if structured_data['keywords']:
            top_keywords = [kw for kw, freq in structured_data['keywords'][:3]]
            insights.append(f"주요 키워드: {', '.join(top_keywords)}")
        
        return insights
        
    def _perform_ai_analysis(self, structured_data: Dict[str, Any], user_request: str) -> Dict[str, Any]:
        """AI 기반 추가 분석 수행"""
        print(f"🤖 AI 분석 시작")
        
        # AutoGen을 사용한 고급 분석
        analysis_prompt = f"""
        사용자 요청: {user_request}
        
        수집된 데이터 분석 결과:
        - 총 사이트 수: {structured_data['total_sites']}
        - 성공적 스크래핑: {structured_data['successful_scrapes']}
        - 카테고리 분포: {structured_data['categories']}
        - 주요 키워드: {[kw for kw, freq in structured_data['keywords'][:10]]}
        
        다음 항목들을 분석해주세요:
        1. 데이터 품질 평가
        2. 주요 트렌드 및 패턴
        3. 사용자 요청과의 관련성
        4. 추가 수집이 필요한 영역
        5. 실행 가능한 인사이트
        
        JSON 형태로 응답해주세요.
        """
        
        # 실제 구현에서는 AutoGen 대화를 통해 분석 수행
        # 여기서는 규칙 기반 분석으로 대체
        ai_analysis = self._rule_based_analysis(structured_data, user_request)
        
        return ai_analysis
        
    def _rule_based_analysis(self, structured_data: Dict[str, Any], user_request: str) -> Dict[str, Any]:
        """규칙 기반 AI 분석"""
        analysis = {
            'data_quality': {},
            'trends_patterns': [],
            'relevance_assessment': {},
            'gaps_identified': [],
            'actionable_insights': []
        }
        
        # 데이터 품질 평가
        success_rate = structured_data['successful_scrapes'] / structured_data['total_sites']
        analysis['data_quality'] = {
            'overall_score': success_rate,
            'coverage': 'good' if success_rate > 0.7 else 'moderate' if success_rate > 0.5 else 'poor',
            'completeness': len(structured_data['summaries']) / structured_data['total_sites']
        }
        
        # 트렌드 및 패턴 분석
        if structured_data['categories']:
            top_category = max(structured_data['categories'], key=structured_data['categories'].get)
            analysis['trends_patterns'].append(f"주요 카테고리: {top_category}")
            
        if structured_data['keywords']:
            top_keywords = [kw for kw, freq in structured_data['keywords'][:5]]
            analysis['trends_patterns'].append(f"주요 키워드: {', '.join(top_keywords)}")
            
        # 관련성 평가
        request_keywords = set(self._extract_keywords(user_request))
        content_keywords = set([kw for kw, freq in structured_data['keywords'][:20]])
        
        keyword_overlap = len(request_keywords.intersection(content_keywords))
        analysis['relevance_assessment'] = {
            'keyword_overlap': keyword_overlap,
            'relevance_score': keyword_overlap / len(request_keywords) if request_keywords else 0,
            'coverage_level': 'high' if keyword_overlap > 3 else 'moderate' if keyword_overlap > 1 else 'low'
        }
        
        # 격차 식별
        if success_rate < 0.7:
            analysis['gaps_identified'].append("웹사이트 접근성 개선 필요")
            
        if len(structured_data['categories']) < 2:
            analysis['gaps_identified'].append("카테고리 다양성 부족")
            
        # 실행 가능한 인사이트
        if structured_data['keywords']:
            analysis['actionable_insights'].append(
                f"'{structured_data['keywords'][0][0]}' 키워드를 중심으로 추가 정보 수집 권장"
            )
            
        if structured_data['categories']:
            top_cat = max(structured_data['categories'], key=structured_data['categories'].get)
            analysis['actionable_insights'].append(
                f"{top_cat} 분야에 대한 심화 분석 필요"
            )
            
        return analysis
        
    def _extract_keywords(self, text: str) -> List[str]:
        """텍스트에서 키워드 추출"""
        import re
        words = re.findall(r'\b\w+\b', text.lower())
        
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her',
            'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their',
            '정보', '수집', '찾기', '검색', '알려', '보여', '분석', '요약', '처리'
        }
        
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        return keywords[:10]
        
    def generate_summary(self, processed_data: Dict[str, Any]) -> str:
        """처리된 데이터 요약 생성"""
        summary = []
        
        # 처리 요약
        processing_summary = processed_data['processing_summary']
        summary.append(f"📊 처리 요약:")
        summary.append(f"  - 총 처리 항목: {processing_summary['total_processed']}개")
        summary.append(f"  - 성공적 처리: {processing_summary['successful_processing']}개")
        summary.append(f"  - 발견된 카테고리: {processing_summary['categories_found']}개")
        summary.append(f"  - 추출된 키워드: {processing_summary['keywords_extracted']}개")
        
        # 주요 인사이트
        insights = processed_data['insights']
        if insights:
            summary.append(f"\n💡 주요 인사이트:")
            for insight in insights[:3]:
                summary.append(f"  - {insight}")
                
        # AI 분석 결과
        ai_analysis = processed_data['ai_analysis']
        if ai_analysis.get('actionable_insights'):
            summary.append(f"\n🎯 실행 가능한 인사이트:")
            for insight in ai_analysis['actionable_insights'][:2]:
                summary.append(f"  - {insight}")
                
        return "\n".join(summary)
        
    def get_agent_info(self) -> Dict[str, Any]:
        """에이전트 정보 반환"""
        return {
            'name': self.config.PROCESSOR_AGENT_NAME,
            'description': '데이터 처리 및 분석 전문가',
            'capabilities': [
                '데이터 구조화 및 정리',
                '키워드 추출 및 분석',
                '콘텐츠 카테고리 분류',
                '인사이트 생성',
                'AI 기반 고급 분석'
            ]
        } 