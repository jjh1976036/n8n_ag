from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_core.models import ChatCompletionClient
from typing import List, Dict, Any
import asyncio
from utils.web_scraper import WebScraper
from config.agent_config import AgentConfig
from utils.claude_client import ClaudeChatCompletionClient
from utils.mcp_client import MCPClientFactory

class CollectorAgent:
    """웹 정보 수집 에이전트"""
    
    def __init__(self):
        self.config = AgentConfig()
        self.scraper = WebScraper()
        self.mcp_client = None
        self._initialize_mcp()
        
        # Claude ChatCompletionClient 생성
        self.model_client = None
        
        try:
            self.model_client = ClaudeChatCompletionClient(
                model=self.config.CLAUDE_MODEL,
                api_key=self.config.ANTHROPIC_API_KEY
            )
            print("✅ Claude ChatCompletionClient 생성 성공")
        except Exception as e:
            print(f"⚠️ Claude ChatCompletionClient 생성 실패: {e}")
            print("⚠️ 모의 모델 클라이언트를 사용합니다...")
            
            class MockChatCompletionClient:
                def __init__(self, model, api_key):
                    self.model = model
                    self.api_key = api_key
                
                async def create(self, messages, **kwargs):
                    from autogen_core.models import CreateResult, RequestUsage
                    return CreateResult(
                        content="Mock response from Claude",
                        finish_reason="stop",
                        usage=RequestUsage(prompt_tokens=0, completion_tokens=10)
                    )
            
            self.model_client = MockChatCompletionClient(
                model=self.config.CLAUDE_MODEL,
                api_key=self.config.ANTHROPIC_API_KEY
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
    
    def _initialize_mcp(self):
        """MCP 클라이언트 초기화"""
        try:
            # 비동기 MCP 클라이언트 초기화를 위한 이벤트 루프 처리
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.mcp_client = loop.run_until_complete(
                MCPClientFactory.create_client_for_agent("collector")
            )
            print("✅ CollectorAgent MCP 클라이언트 초기화 성공")
        except Exception as e:
            print(f"⚠️ CollectorAgent MCP 초기화 실패: {e}")
            self.mcp_client = None
        
    def collect_information(self, user_request: str) -> Dict[str, Any]:
        """사용자 요청에 따른 정보 수집"""
        print(f"🔍 정보 수집 시작: {user_request}")
        
        # 1. 관련 웹사이트 검색
        search_query = self._generate_search_query(user_request)
        print(f"📝 검색 쿼리 생성: {search_query}")
        
        # 2. MCP를 활용한 웹 검색 및 스크래핑 시도
        mcp_data = self._collect_with_mcp(search_query) if self.mcp_client else []
        
        # 3. 기존 웹 스크래퍼를 사용한 백업 수집
        fallback_data = []
        if not mcp_data or len(mcp_data) < 3:
            urls = self.scraper.search_websites(search_query, max_results=5)
            print(f"🌐 발견된 URL 수: {len(urls)}")
            
            if urls:
                fallback_data = self.scraper.scrape_multiple_sites(urls)
                print(f"📊 기존 스크래핑 완료: {len(fallback_data)}개 사이트")
        
        # 4. MCP 데이터와 기존 데이터 결합
        scraped_data = mcp_data + fallback_data
        print(f"📈 총 수집된 데이터: {len(scraped_data)}개")
        
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
    
    def _collect_with_mcp(self, search_query: str) -> List[Dict[str, Any]]:
        """MCP를 활용한 고급 웹 데이터 수집"""
        collected_data = []
        
        if not self.mcp_client:
            return collected_data
        
        try:
            # 1. 웹 검색 MCP 서버 사용
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # 웹 검색 실행
            search_result = loop.run_until_complete(
                self.mcp_client.call_tool("web_search", "search", {
                    "query": search_query,
                    "num_results": 10
                })
            )
            
            if search_result.get("success"):
                search_results = search_result.get("result", {}).get("results", [])
                print(f"🔍 MCP 웹 검색 결과: {len(search_results)}개")
                
                # 2. 상위 결과들을 Firecrawl로 스크래핑
                for result in search_results[:5]:  # 상위 5개만 스크래핑
                    url = result.get("url", "")
                    if url:
                        scrape_result = loop.run_until_complete(
                            self.mcp_client.call_tool("firecrawl", "scrape_url", {
                                "url": url,
                                "options": {
                                    "formats": ["markdown", "html"],
                                    "onlyMainContent": True
                                }
                            })
                        )
                        
                        if scrape_result.get("success"):
                            content_data = scrape_result.get("result", {})
                            collected_data.append({
                                "status": "success",
                                "url": url,
                                "title": result.get("title", ""),
                                "content": content_data.get("content", ""),
                                "metadata": content_data.get("metadata", {}),
                                "source": "mcp_firecrawl"
                            })
                            print(f"✅ MCP 스크래핑 성공: {url[:50]}...")
                        else:
                            print(f"⚠️ MCP 스크래핑 실패: {url}")
            
        except Exception as e:
            print(f"❌ MCP 데이터 수집 오류: {e}")
        
        return collected_data
        
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
        
        # MCP 클라이언트 정리
        if self.mcp_client:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.mcp_client.cleanup())
            except Exception as e:
                print(f"⚠️ MCP 클라이언트 정리 중 오류: {e}")
        
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