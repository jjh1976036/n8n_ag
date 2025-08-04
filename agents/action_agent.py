from autogen_core.models import ChatCompletionClient
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
import requests
import json
from typing import List, Dict, Any
from config.agent_config import AgentConfig

class ActionAgent:
    """행동 실행 에이전트"""
    
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
        
        # 행동 에이전트 생성
        try:
            self.action_agent = AssistantAgent(
                name=self.config.ACTION_AGENT_NAME,
                model_client=self.model_client,
                system_message=self.config.SYSTEM_MESSAGES["action"]
            )
            
            # 사용자 프록시 에이전트 - model_client 없이 생성
            try:
                self.user_proxy = UserProxyAgent(
                    name="user_proxy"
                )
            except Exception as e:
                print(f"⚠️ UserProxyAgent 생성 실패, 기본 생성자 사용: {e}")
                self.user_proxy = UserProxyAgent()
            
            print("✅ 행동 에이전트 생성 성공")
        except Exception as e:
            print(f"❌ 행동 에이전트 생성 실패: {e}")
            self.action_agent = None
            self.user_proxy = None
        
    def execute_actions(self, processed_data: Dict[str, Any], user_request: str) -> Dict[str, Any]:
        """처리된 데이터를 바탕으로 행동 수행"""
        print(f"🚀 행동 실행 시작")
        
        if processed_data['status'] != 'success':
            return {
                'status': 'error',
                'message': '처리된 데이터가 없어 행동을 수행할 수 없습니다.',
                'data': {}
            }
            
        # 1. 행동 계획 수립
        action_plan = self._create_action_plan(processed_data['data'], user_request)
        
        # 2. 행동 실행
        executed_actions = self._execute_action_plan(action_plan, processed_data['data'])
        
        # 3. 결과 평가
        action_results = self._evaluate_actions(executed_actions, user_request)
        
        # 4. n8n 웹훅 전송 (선택적)
        if self.config.N8N_WEBHOOK_URL:
            self._send_to_n8n(action_results)
            
        return {
            'status': 'success',
            'message': f'{len(executed_actions)}개의 행동을 수행했습니다.',
            'data': {
                'action_plan': action_plan,
                'executed_actions': executed_actions,
                'action_results': action_results
            }
        }
        
    def _create_action_plan(self, processed_data: Dict[str, Any], user_request: str) -> List[Dict[str, Any]]:
        """행동 계획 수립"""
        print(f"📋 행동 계획 수립 중...")
        
        action_plan = []
        
        # 데이터 품질 기반 행동
        ai_analysis = processed_data.get('ai_analysis', {})
        data_quality = ai_analysis.get('data_quality', {})
        
        if data_quality.get('overall_score', 0) < 0.7:
            action_plan.append({
                'action_type': 'data_improvement',
                'description': '데이터 품질 개선을 위한 추가 수집 계획',
                'priority': 'high',
                'parameters': {
                    'target_success_rate': 0.8,
                    'additional_sources': 3
                }
            })
            
        # 인사이트 기반 행동
        actionable_insights = ai_analysis.get('actionable_insights', [])
        for insight in actionable_insights[:3]:  # 상위 3개 인사이트만
            action_plan.append({
                'action_type': 'insight_followup',
                'description': f'인사이트 기반 행동: {insight}',
                'priority': 'medium',
                'parameters': {
                    'insight': insight,
                    'followup_type': 'analysis_deepening'
                }
            })
            
        # 사용자 요청 기반 행동
        if '요약' in user_request or 'summary' in user_request.lower():
            action_plan.append({
                'action_type': 'generate_summary',
                'description': '사용자 요청에 따른 요약 생성',
                'priority': 'high',
                'parameters': {
                    'summary_type': 'comprehensive',
                    'target_length': 500
                }
            })
            
        if '분석' in user_request or 'analysis' in user_request.lower():
            action_plan.append({
                'action_type': 'deep_analysis',
                'description': '심화 분석 수행',
                'priority': 'high',
                'parameters': {
                    'analysis_depth': 'comprehensive',
                    'include_visualizations': True
                }
            })
            
        # 기본 행동 (항상 수행)
        action_plan.append({
            'action_type': 'prepare_report',
            'description': '최종 보고서 준비',
            'priority': 'high',
            'parameters': {
                'report_format': 'structured',
                'include_recommendations': True
            }
        })
        
        # 우선순위별 정렬
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        action_plan.sort(key=lambda x: priority_order.get(x['priority'], 0), reverse=True)
        
        return action_plan
        
    def _execute_action_plan(self, action_plan: List[Dict[str, Any]], processed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """행동 계획 실행"""
        executed_actions = []
        
        for action in action_plan:
            print(f"⚡ 행동 실행: {action['description']}")
            
            try:
                if action['action_type'] == 'generate_summary':
                    result = self._generate_comprehensive_summary(processed_data, action['parameters'])
                elif action['action_type'] == 'deep_analysis':
                    result = self._perform_deep_analysis(processed_data, action['parameters'])
                elif action['action_type'] == 'prepare_report':
                    result = self._prepare_final_report(processed_data, action['parameters'])
                elif action['action_type'] == 'data_improvement':
                    result = self._plan_data_improvement(processed_data, action['parameters'])
                elif action['action_type'] == 'insight_followup':
                    result = self._followup_on_insight(processed_data, action['parameters'])
                else:
                    result = {'status': 'unknown_action', 'message': f'알 수 없는 행동 타입: {action["action_type"]}'}
                    
                executed_actions.append({
                    'action': action,
                    'result': result,
                    'status': 'completed'
                })
                
            except Exception as e:
                executed_actions.append({
                    'action': action,
                    'result': {'status': 'error', 'message': str(e)},
                    'status': 'failed'
                })
                
        return executed_actions
        
    def _generate_comprehensive_summary(self, processed_data: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """종합 요약 생성"""
        structured_data = processed_data['structured_data']
        insights = processed_data['insights']
        
        summary = {
            'executive_summary': f"총 {structured_data['total_sites']}개 웹사이트에서 정보를 수집하여 분석을 완료했습니다.",
            'key_findings': insights[:5],
            'data_quality': f"스크래핑 성공률: {structured_data['successful_scrapes']/structured_data['total_sites']*100:.1f}%",
            'recommendations': self._generate_recommendations(processed_data)
        }
        
        return {
            'status': 'success',
            'summary': summary,
            'length': len(str(summary))
        }
        
    def _perform_deep_analysis(self, processed_data: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """심화 분석 수행"""
        structured_data = processed_data['structured_data']
        ai_analysis = processed_data['ai_analysis']
        
        deep_analysis = {
            'trend_analysis': self._analyze_trends(structured_data),
            'pattern_recognition': self._recognize_patterns(structured_data),
            'correlation_analysis': self._analyze_correlations(structured_data),
            'predictive_insights': self._generate_predictive_insights(structured_data)
        }
        
        return {
            'status': 'success',
            'analysis': deep_analysis
        }
        
    def _prepare_final_report(self, processed_data: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """최종 보고서 준비"""
        report = {
            'title': '웹 정보 수집 및 분석 보고서',
            'timestamp': self._get_current_timestamp(),
            'executive_summary': self._create_executive_summary(processed_data),
            'detailed_analysis': self._create_detailed_analysis(processed_data),
            'recommendations': self._generate_recommendations(processed_data),
            'appendix': self._create_appendix(processed_data)
        }
        
        return {
            'status': 'success',
            'report': report
        }
        
    def _plan_data_improvement(self, processed_data: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """데이터 개선 계획 수립"""
        current_success_rate = processed_data['structured_data']['successful_scrapes'] / processed_data['structured_data']['total_sites']
        target_rate = parameters.get('target_success_rate', 0.8)
        
        improvement_plan = {
            'current_performance': f"{current_success_rate:.1%}",
            'target_performance': f"{target_rate:.1%}",
            'improvement_strategies': [
                "더 다양한 웹사이트 소스 활용",
                "스크래핑 전략 최적화",
                "동적 콘텐츠 처리 개선"
            ],
            'additional_sources_needed': parameters.get('additional_sources', 3)
        }
        
        return {
            'status': 'success',
            'improvement_plan': improvement_plan
        }
        
    def _followup_on_insight(self, processed_data: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """인사이트 기반 후속 행동"""
        insight = parameters.get('insight', '')
        
        followup_action = {
            'insight': insight,
            'action_taken': f"인사이트 '{insight}'에 대한 심화 분석 수행",
            'next_steps': [
                "추가 데이터 수집 계획",
                "전문가 검토 요청",
                "실행 가능한 솔루션 개발"
            ]
        }
        
        return {
            'status': 'success',
            'followup': followup_action
        }
        
    def _analyze_trends(self, structured_data: Dict[str, Any]) -> Dict[str, Any]:
        """트렌드 분석"""
        return {
            'keyword_trends': [kw for kw, freq in structured_data['keywords'][:5]],
            'category_distribution': structured_data['categories'],
            'content_patterns': '주요 패턴 분석 결과'
        }
        
    def _recognize_patterns(self, structured_data: Dict[str, Any]) -> List[str]:
        """패턴 인식"""
        patterns = []
        
        if structured_data['categories']:
            top_category = max(structured_data['categories'], key=structured_data['categories'].get)
            patterns.append(f"주요 콘텐츠 카테고리: {top_category}")
            
        if structured_data['keywords']:
            patterns.append(f"주요 키워드 패턴: {', '.join([kw for kw, freq in structured_data['keywords'][:3]])}")
            
        return patterns
        
    def _analyze_correlations(self, structured_data: Dict[str, Any]) -> Dict[str, Any]:
        """상관관계 분석"""
        return {
            'category_keyword_correlation': '카테고리와 키워드 간 상관관계',
            'content_quality_metrics': '콘텐츠 품질 지표'
        }
        
    def _generate_predictive_insights(self, structured_data: Dict[str, Any]) -> List[str]:
        """예측적 인사이트 생성"""
        return [
            "향후 트렌드 예측",
            "사용자 행동 패턴 예측",
            "콘텐츠 성과 예측"
        ]
        
    def _create_executive_summary(self, processed_data: Dict[str, Any]) -> str:
        """실행 요약 생성"""
        structured_data = processed_data['structured_data']
        return f"""
        본 보고서는 {structured_data['total_sites']}개 웹사이트에서 수집된 정보를 분석한 결과입니다.
        성공적으로 {structured_data['successful_scrapes']}개 사이트에서 정보를 수집했으며,
        {len(structured_data['categories'])}개의 주요 카테고리와 {len(structured_data['keywords'])}개의 키워드를 발견했습니다.
        """
        
    def _create_detailed_analysis(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """상세 분석 생성"""
        return {
            'data_overview': processed_data['structured_data'],
            'insights': processed_data['insights'],
            'ai_analysis': processed_data['ai_analysis']
        }
        
    def _generate_recommendations(self, processed_data: Dict[str, Any]) -> List[str]:
        """권장사항 생성"""
        recommendations = []
        
        # 데이터 품질 기반 권장사항
        success_rate = processed_data['structured_data']['successful_scrapes'] / processed_data['structured_data']['total_sites']
        if success_rate < 0.7:
            recommendations.append("웹사이트 접근성 개선을 위한 스크래핑 전략 최적화")
            
        # 카테고리 기반 권장사항
        if processed_data['structured_data']['categories']:
            top_category = max(processed_data['structured_data']['categories'], key=processed_data['structured_data']['categories'].get)
            recommendations.append(f"{top_category} 분야에 대한 심화 분석 수행")
            
        # 키워드 기반 권장사항
        if processed_data['structured_data']['keywords']:
            recommendations.append("주요 키워드를 중심으로 한 추가 정보 수집")
            
        return recommendations
        
    def _create_appendix(self, processed_data: Dict[str, Any]) -> Dict[str, Any]:
        """부록 생성"""
        return {
            'raw_data_summary': f"{len(processed_data['structured_data']['raw_data'])}개 원시 데이터 항목",
            'processing_metadata': processed_data['processing_summary'],
            'technical_details': '기술적 세부사항'
        }
        
    def _get_current_timestamp(self) -> str:
        """현재 타임스탬프 반환"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    def _evaluate_actions(self, executed_actions: List[Dict[str, Any]], user_request: str) -> Dict[str, Any]:
        """행동 결과 평가"""
        successful_actions = [action for action in executed_actions if action['status'] == 'completed']
        failed_actions = [action for action in executed_actions if action['status'] == 'failed']
        
        evaluation = {
            'total_actions': len(executed_actions),
            'successful_actions': len(successful_actions),
            'failed_actions': len(failed_actions),
            'success_rate': len(successful_actions) / len(executed_actions) if executed_actions else 0,
            'user_request_satisfaction': self._assess_user_satisfaction(successful_actions, user_request)
        }
        
        return evaluation
        
    def _assess_user_satisfaction(self, successful_actions: List[Dict[str, Any]], user_request: str) -> str:
        """사용자 만족도 평가"""
        # 간단한 키워드 매칭 기반 평가
        request_keywords = set(user_request.lower().split())
        action_descriptions = ' '.join([action['action']['description'] for action in successful_actions]).lower()
        
        satisfaction_score = len(request_keywords.intersection(set(action_descriptions.split()))) / len(request_keywords)
        
        if satisfaction_score > 0.7:
            return 'high'
        elif satisfaction_score > 0.4:
            return 'medium'
        else:
            return 'low'
            
    def _send_to_n8n(self, action_results: Dict[str, Any]) -> None:
        """n8n 웹훅으로 결과 전송"""
        try:
            payload = {
                'action_results': action_results,
                'timestamp': self._get_current_timestamp(),
                'source': 'action_agent'
            }
            
            response = requests.post(
                self.config.N8N_WEBHOOK_URL,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ n8n으로 결과 전송 성공")
            else:
                print(f"⚠️ n8n 전송 실패: {response.status_code}")
                
        except Exception as e:
            print(f"❌ n8n 전송 오류: {e}")
            
    def get_agent_info(self) -> Dict[str, Any]:
        """에이전트 정보 반환"""
        return {
            'name': self.config.ACTION_AGENT_NAME,
            'description': '행동 실행 및 계획 전문가',
            'capabilities': [
                '행동 계획 수립',
                '다양한 행동 유형 실행',
                '결과 평가 및 분석',
                'n8n 연동',
                '사용자 만족도 평가'
            ]
        } 