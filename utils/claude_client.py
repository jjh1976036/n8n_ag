from typing import List, Dict, Any, Union, Optional
from autogen_core.models import ChatCompletionClient, CreateResult
from autogen_core.models._types import (
    ChatCompletionTokenLogprob,
    FinishReason,
    FunctionCall,
    RequestUsage,
    TopLogprobs,
    SystemMessage,
    UserMessage,
    AssistantMessage,
    FunctionExecutionResult,
    FunctionExecutionResultMessage,
)
import anthropic
import json


class ClaudeChatCompletionClient(ChatCompletionClient):
    """Claude API를 위한 ChatCompletionClient 구현"""
    
    def __init__(self, model: str, api_key: str):
        self.model = model
        self.client = anthropic.Anthropic(api_key=api_key)
    
    async def create(
        self,
        messages: List[Union[SystemMessage, UserMessage, AssistantMessage, FunctionExecutionResultMessage]],
        *,
        frequency_penalty: Optional[float] = None,
        logit_bias: Optional[dict[str, int]] = None,
        logprobs: Optional[bool] = None,
        max_tokens: Optional[int] = None,
        n: Optional[int] = None,
        presence_penalty: Optional[float] = None,
        response_format: Optional[dict[str, Any]] = None,
        seed: Optional[int] = None,
        stop: Union[Optional[str], List[str]] = None,
        stream: Optional[bool] = None,
        temperature: Optional[float] = None,
        tool_choice: Optional[Union[str, dict[str, Any]]] = None,
        tools: Optional[List[dict[str, Any]]] = None,
        top_logprobs: Optional[int] = None,
        top_p: Optional[float] = None,
        user: Optional[str] = None,
        **kwargs,
    ) -> CreateResult:
        """Claude API를 사용하여 채팅 완성 생성"""
        
        # 메시지를 Claude 형식으로 변환
        claude_messages = self._convert_messages_to_claude_format(messages)
        
        # 시스템 메시지 추출
        system_message = self._extract_system_message(messages)
        
        try:
            # Claude API 호출
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens or 4096,
                temperature=temperature or 0.7,
                system=system_message if system_message else "",
                messages=claude_messages
            )
            
            # AutoGen 형식으로 응답 변환
            return self._convert_claude_response_to_autogen_format(response)
            
        except Exception as e:
            print(f"Claude API 호출 실패: {e}")
            # 실패 시 기본 응답 반환
            return CreateResult(
                content="죄송합니다. AI 응답을 생성하는 중 오류가 발생했습니다.",
                finish_reason="error",
                usage=RequestUsage(prompt_tokens=0, completion_tokens=0)
            )
    
    def _convert_messages_to_claude_format(
        self, 
        messages: List[Union[SystemMessage, UserMessage, AssistantMessage, FunctionExecutionResultMessage]]
    ) -> List[Dict[str, str]]:
        """AutoGen 메시지를 Claude 형식으로 변환"""
        claude_messages = []
        
        for message in messages:
            if isinstance(message, SystemMessage):
                # 시스템 메시지는 별도로 처리
                continue
            elif isinstance(message, UserMessage):
                claude_messages.append({
                    "role": "user",
                    "content": message.content
                })
            elif isinstance(message, AssistantMessage):
                claude_messages.append({
                    "role": "assistant", 
                    "content": message.content
                })
            elif isinstance(message, FunctionExecutionResultMessage):
                # 함수 실행 결과를 사용자 메시지로 변환
                claude_messages.append({
                    "role": "user",
                    "content": f"Function execution result: {message.content}"
                })
        
        return claude_messages
    
    def _extract_system_message(
        self, 
        messages: List[Union[SystemMessage, UserMessage, AssistantMessage, FunctionExecutionResultMessage]]
    ) -> Optional[str]:
        """메시지에서 시스템 메시지 추출"""
        for message in messages:
            if isinstance(message, SystemMessage):
                return message.content
        return None
    
    def _convert_claude_response_to_autogen_format(self, response) -> CreateResult:
        """Claude 응답을 AutoGen 형식으로 변환"""
        content = ""
        if response.content and len(response.content) > 0:
            content = response.content[0].text if hasattr(response.content[0], 'text') else str(response.content[0])
        
        usage = RequestUsage(
            prompt_tokens=response.usage.input_tokens,
            completion_tokens=response.usage.output_tokens
        )
        
        return CreateResult(
            content=content,
            finish_reason="stop",
            usage=usage
        )

    @property
    def capabilities(self) -> dict[str, Any]:
        """클라이언트 기능 정보 반환"""
        return {
            "vision": True,
            "function_calling": False,
            "json_output": True
        }
    
    def count_tokens(self, messages: List[Union[SystemMessage, UserMessage, AssistantMessage, FunctionExecutionResultMessage]]) -> int:
        """메시지의 토큰 수 추정 (근사치)"""
        total_chars = 0
        for message in messages:
            if hasattr(message, 'content'):
                total_chars += len(str(message.content))
        
        # 대략적인 토큰 수 계산 (영어 기준 4글자당 1토큰)
        return total_chars // 4
    
    def remaining_tokens(self, messages: List[Union[SystemMessage, UserMessage, AssistantMessage, FunctionExecutionResultMessage]]) -> int:
        """남은 토큰 수 추정"""
        used_tokens = self.count_tokens(messages)
        max_tokens = 200000  # Claude 3.5 Sonnet의 컨텍스트 윈도우
        return max(0, max_tokens - used_tokens)
    
    def total_tokens(self) -> int:
        """총 사용 가능한 토큰 수"""
        return 200000  # Claude 3.5 Sonnet의 컨텍스트 윈도우