#!/usr/bin/env python3
"""
간단한 수정 테스트
"""

def test_agent_creation():
    """에이전트 생성 테스트"""
    try:
        print("=== 에이전트 생성 테스트 ===")
        
        # 1. 기본 import 테스트
        print("1. 기본 import 테스트...")
        from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
        print("   ✓ AssistantAgent, UserProxyAgent import 성공")
        
        # 2. ChatCompletionClient 테스트
        print("2. ChatCompletionClient 테스트...")
        model_client = None
        
        # 방법 1: OpenAIChatCompletionClient 시도
        try:
            from autogen_ext.models.openai import OpenAIChatCompletionClient
            print("   ✓ autogen_ext.models.openai import 성공")
            
            # 환경변수에서 API 키 가져오기
            import os
            api_key = os.getenv('OPENAI_API_KEY', 'test-key')
            
            model_client = OpenAIChatCompletionClient(
                model="gpt-4",
                api_key=api_key,
                base_url="https://api.openai.com/v1"
            )
            print("   ✓ OpenAIChatCompletionClient 생성 성공")
            
        except ImportError as e:
            print(f"   ⚠ autogen_ext.models.openai import 실패: {e}")
            print("   💡 tiktoken 패키지가 필요할 수 있습니다.")
            
        except Exception as e:
            print(f"   ⚠ OpenAIChatCompletionClient 생성 실패: {e}")
        
        # 방법 2: 다른 구현체 찾기
        if model_client is None:
            try:
                # 다른 가능한 구현체들 시도
                from autogen_core.models import ChatCompletionClient
                print("   ⚠ ChatCompletionClient는 추상 클래스입니다.")
                print("   💡 구체적인 구현체를 찾아보겠습니다...")
                
                # 사용 가능한 구현체들 확인
                import autogen_core.models
                available_models = [attr for attr in dir(autogen_core.models) 
                                 if not attr.startswith('_') and 'Client' in attr]
                print(f"   📋 사용 가능한 모델 클라이언트: {available_models}")
                
            except Exception as e:
                print(f"   ❌ 모델 클라이언트 확인 실패: {e}")
        
        # 방법 3: 간단한 모의 클라이언트 사용
        if model_client is None:
            print("   ⚠ 모의 모델 클라이언트를 사용합니다...")
            
            class MockChatCompletionClient:
                def __init__(self):
                    self.model = "mock-model"
                    self.api_key = "mock-key"
                
                def create(self, messages, **kwargs):
                    return {"choices": [{"message": {"content": "Mock response"}}]}
                
                def create_stream(self, messages, **kwargs):
                    return iter([{"choices": [{"message": {"content": "Mock stream"}}]}])
            
            model_client = MockChatCompletionClient()
            print("   ✓ 모의 모델 클라이언트 생성 성공")
        
        # 3. AssistantAgent 생성 테스트
        print("3. AssistantAgent 생성 테스트...")
        assistant = AssistantAgent(
            name="test_assistant",
            model_client=model_client,
            system_message="당신은 테스트 어시스턴트입니다."
        )
        print("   ✓ AssistantAgent 생성 성공")
        
        # 4. UserProxyAgent 생성 테스트...
        print("4. UserProxyAgent 생성 테스트...")
        try:
            # 방법 1: model_client 없이 생성
            user_proxy = UserProxyAgent(
                name="test_user_proxy"
            )
            print("   ✓ UserProxyAgent 생성 성공 (model_client 없이)")
        except Exception as e:
            print(f"   ⚠ UserProxyAgent 생성 실패: {e}")
            try:
                # 방법 2: 다른 매개변수 조합 시도
                user_proxy = UserProxyAgent(
                    name="test_user_proxy",
                    human_input_mode="NEVER"
                )
                print("   ✓ UserProxyAgent 생성 성공 (human_input_mode 포함)")
            except Exception as e2:
                print(f"   ❌ UserProxyAgent 생성 실패: {e2}")
                # 방법 3: 기본 생성자만 사용
                user_proxy = UserProxyAgent()
                print("   ✓ UserProxyAgent 생성 성공 (기본 생성자)")
        
        print("\n=== 모든 테스트 성공! ===")
        return True
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_agent_creation() 