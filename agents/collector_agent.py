from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_core.models import ChatCompletionClient
from typing import List, Dict, Any
from utils.web_scraper import WebScraper
from config.agent_config import AgentConfig

class CollectorAgent:
    """웹 정보 수집 에이전트"""
    
    def __init__(self):
        self.config = AgentConfig()
        self.scraper = WebScraper()
        
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
        
        # 수집 에이전트 생성
        try:
            self.collector = AssistantAgent(
                name=self.config.COLLECTOR_AGENT_NAME,
                model_client=self.model_client,
                system_message=self.config.SYSTEM_MESSAGES["collector"]
            )
            
            # 사용자 프록시 에이전트 - model_client 없이 생성
            try:
                self.user_proxy = UserProxyAgent(
                    name="user_proxy"
                )
            except Exception as e:
                print(f"⚠️ UserProxyAgent 생성 실패, 기본 생성자 사용: {e}")
                self.user_proxy = UserProxyAgent()
            
            print("✅ 에이전트 생성 성공")
        except Exception as e:
            print(f"❌ 에이전트 생성 실패: {e}")
            self.collector = None
            self.user_proxy = None
        
    def collect_information(self, user_request: str) -> Dict[str, Any]:
        """사용자 요청에 따른 정보 수집"""
        print(f"🔍 정보 수집 시작: {user_request}")
        
        # 1. 관련 웹사이트 검색
        search_query = self._generate_search_query(user_request)
        print(f"📝 검색 쿼리 생성: {search_query}")
        
        # 2. 웹사이트 URL 수집
        urls = self.scraper.search_websites(search_query, max_results=5)
        print(f"🌐 발견된 URL 수: {len(urls)}")
        
        if not urls:
            return {
                'status': 'error',
                'message': '관련 웹사이트를 찾을 수 없습니다.',
                'data': []
            }
            
        # 3. 웹사이트 스크래핑
        scraped_data = self.scraper.scrape_multiple_sites(urls)
        print(f"📊 스크래핑 완료: {len(scraped_data)}개 사이트")
        
        # 4. 데이터 정리 및 구조화
        structured_data = self._structure_collected_data(scraped_data, user_request)
        
        return {
            'status': 'success',
            'message': f'{len(urls)}개 웹사이트에서 정보를 수집했습니다.',
            'data': structured_data,
            'raw_data': scraped_data
        }
        
    def _generate_search_query(self, user_request: str) -> str:
        """사용자 요청을 바탕으로 검색 쿼리 생성"""
        # AutoGen을 사용하여 검색 쿼리 최적화
        prompt = f"""
        사용자의 요청: {user_request}
        
        위 요청에 대한 효과적인 웹 검색 쿼리를 생성해주세요.
        쿼리는 구체적이고 관련성 높은 결과를 얻을 수 있도록 작성되어야 합니다.
        
        검색 쿼리만 반환하세요.
        """
        
        # 실제 구현에서는 AutoGen 대화를 통해 쿼리 생성
        # 여기서는 간단한 키워드 추출로 대체
        keywords = self._extract_keywords(user_request)
        return " ".join(keywords)
        
    def _extract_keywords(self, text: str) -> List[str]:
        """텍스트에서 주요 키워드 추출"""
        # 간단한 키워드 추출 (실제로는 더 정교한 NLP 사용)
        import re
        words = re.findall(r'\b\w+\b', text.lower())
        
        # 불용어 제거
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her',
            'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their',
            '정보', '수집', '찾기', '검색', '알려', '보여', '분석', '요약'
        }
        
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        return keywords[:5]  # 상위 5개 키워드만 사용
        
    def _structure_collected_data(self, scraped_data: List[Dict[str, Any]], user_request: str) -> Dict[str, Any]:
        """수집된 데이터 구조화"""
        structured_data = {
            'user_request': user_request,
            'collection_summary': {
                'total_sites': len(scraped_data),
                'successful_scrapes': sum(1 for data in scraped_data if data['status'] == 'success'),
                'failed_scrapes': sum(1 for data in scraped_data if data['status'] == 'error')
            },
            'sites_data': []
        }
        
        for data in scraped_data:
            if data['status'] == 'success':
                site_data = {
                    'url': data['url'],
                    'title': data.get('title', ''),
                    'description': data.get('description', ''),
                    'content_preview': data.get('content', '')[:200] + "..." if len(data.get('content', '')) > 200 else data.get('content', ''),
                    'relevance_score': self._calculate_relevance(data.get('content', ''), user_request)
                }
                structured_data['sites_data'].append(site_data)
                
        # 관련성 점수로 정렬
        structured_data['sites_data'].sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return structured_data
        
    def _calculate_relevance(self, content: str, user_request: str) -> float:
        """콘텐츠와 사용자 요청 간의 관련성 점수 계산"""
        if not content or not user_request:
            return 0.0
            
        # 간단한 키워드 매칭 기반 관련성 계산
        request_keywords = set(self._extract_keywords(user_request))
        content_keywords = set(self._extract_keywords(content))
        
        if not request_keywords:
            return 0.0
            
        # Jaccard 유사도 계산
        intersection = len(request_keywords.intersection(content_keywords))
        union = len(request_keywords.union(content_keywords))
        
        if union == 0:
            return 0.0
            
        return intersection / union
        
    def cleanup(self):
        """리소스 정리"""
        self.scraper.close_selenium()
        
    def get_agent_info(self) -> Dict[str, Any]:
        """에이전트 정보 반환"""
        return {
            'name': self.config.COLLECTOR_AGENT_NAME,
            'description': '웹 정보 수집 전문가',
            'capabilities': [
                '웹사이트 검색 및 발견',
                '웹 콘텐츠 스크래핑',
                '데이터 구조화 및 정리',
                '관련성 분석'
            ]
        } 