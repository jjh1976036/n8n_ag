from autogen_core.models import ChatCompletionClient
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from typing import List, Dict, Any
import asyncio
from config.agent_config import AgentConfig
from utils.claude_client import ClaudeChatCompletionClient
from utils.mcp_client import MCPClientFactory

class ProcessorAgent:
    """데이터 처리 에이전트"""
    
    def __init__(self):
        self.config = AgentConfig()
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
    
    def _initialize_mcp(self):
        """MCP 클라이언트 초기화"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.mcp_client = loop.run_until_complete(
                MCPClientFactory.create_client_for_agent("processor")
            )
            print("✅ ProcessorAgent MCP 클라이언트 초기화 성공")
        except Exception as e:
            print(f"⚠️ ProcessorAgent MCP 초기화 실패: {e}")
            self.mcp_client = None
        
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
        
        # 3. MCP를 활용한 고급 분석
        mcp_analysis = self._perform_mcp_analysis(structured_data) if self.mcp_client else {}
        
        # 4. AI 기반 추가 분석
        ai_analysis = self._perform_ai_analysis(structured_data, collected_data['data']['user_request'])
        
        # 5. MCP 분석 결과와 AI 분석 결과 통합
        if mcp_analysis:
            ai_analysis.update(mcp_analysis)
        
        # 6. 처리 결과 통합
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
    
    def _perform_mcp_analysis(self, structured_data: Dict[str, Any]) -> Dict[str, Any]:
        """MCP를 활용한 고급 데이터 분석"""
        mcp_analysis = {}
        
        if not self.mcp_client:
            return mcp_analysis
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # 1. 시각화 차트 생성 (키워드 분포)
            if structured_data.get('keywords'):
                keyword_data = [
                    {"keyword": kw, "frequency": freq} 
                    for kw, freq in structured_data['keywords'][:10]
                ]
                
                chart_result = loop.run_until_complete(
                    self.mcp_client.call_tool("chart", "create_chart", {
                        "data": keyword_data,
                        "chart_type": "bar",
                        "options": {
                            "title": "Top Keywords Frequency",
                            "x_axis": "keyword",
                            "y_axis": "frequency"
                        }
                    })
                )
                
                if chart_result.get("success"):
                    mcp_analysis["keyword_chart"] = chart_result.get("result", {})
                    print("✅ MCP 키워드 차트 생성 성공")
            
            # 2. 카테고리 분포 차트 생성
            if structured_data.get('categories'):
                category_data = [
                    {"category": cat, "count": count}
                    for cat, count in structured_data['categories'].items()
                ]
                
                pie_chart_result = loop.run_until_complete(
                    self.mcp_client.call_tool("chart", "create_chart", {
                        "data": category_data,
                        "chart_type": "pie",
                        "options": {
                            "title": "Content Categories Distribution"
                        }
                    })
                )
                
                if pie_chart_result.get("success"):
                    mcp_analysis["category_chart"] = pie_chart_result.get("result", {})
                    print("✅ MCP 카테고리 차트 생성 성공")
            
            # 3. 데이터를 파일에 임시 저장하여 SQLite 분석 수행
            if structured_data.get('summaries'):
                # SQLite 데이터베이스에 임시 데이터 저장 및 분석
                analysis_result = loop.run_until_complete(
                    self.mcp_client.call_tool("sqlite", "execute", {
                        "query": """
                        CREATE TEMPORARY TABLE IF NOT EXISTS temp_analysis (
                            id INTEGER PRIMARY KEY,
                            content TEXT,
                            word_count INTEGER,
                            char_count INTEGER
                        )
                        """
                    })
                )
                
                # 콘텐츠 통계 분석
                total_words = sum(len(summary.split()) for summary in structured_data['summaries'])
                avg_words = total_words / len(structured_data['summaries']) if structured_data['summaries'] else 0
                
                mcp_analysis["content_statistics"] = {
                    "total_summaries": len(structured_data['summaries']),
                    "total_words": total_words,
                    "average_words_per_summary": round(avg_words, 2),
                    "analysis_method": "mcp_sqlite"
                }
                print("✅ MCP SQLite 분석 완료")
            
        except Exception as e:
            print(f"❌ MCP 분석 오류: {e}")
        
        return mcp_analysis
        
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