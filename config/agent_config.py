import os
from dotenv import load_dotenv

load_dotenv()

class AgentConfig:
    """에이전트 설정 클래스"""
    
    # Claude 설정
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    CLAUDE_MODEL = "claude-3-5-sonnet-20241022"
    
    # n8n 설정
    N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL')
    
    # 에이전트 설정
    COLLECTOR_AGENT_NAME = "WebCollector"
    PROCESSOR_AGENT_NAME = "DataProcessor"
    ACTION_AGENT_NAME = "ActionExecutor"
    REPORTER_AGENT_NAME = "ReportGenerator"
    
    # 웹 스크래핑 설정
    MAX_PAGES_TO_SCRAPE = 10
    REQUEST_TIMEOUT = 30
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    
    # 데이터 처리 설정
    MAX_CONTENT_LENGTH = 5000
    SUMMARIZATION_LENGTH = 500
    
    # 시스템 메시지
    SYSTEM_MESSAGES = {
        "collector": """당신은 웹 정보 수집 전문가입니다. 
        사용자의 요청에 따라 관련 웹사이트를 찾고 정보를 수집하는 것이 주요 임무입니다.
        수집한 정보는 구조화된 형태로 정리하여 다음 단계로 전달하세요.""",
        
        "processor": """당신은 데이터 처리 전문가입니다.
        수집된 웹 정보를 분석하고, 요약하며, 중요한 인사이트를 도출하는 것이 주요 임무입니다.
        처리된 데이터는 명확하고 실행 가능한 형태로 정리하세요.""",
        
        "action": """당신은 행동 실행 전문가입니다.
        처리된 데이터를 바탕으로 구체적인 행동을 계획하고 실행하는 것이 주요 임무입니다.
        행동 결과를 명확하게 기록하세요.""",
        
        "reporter": """당신은 보고서 작성 전문가입니다.
        전체 프로세스의 결과를 종합하여 사용자에게 명확하고 유용한 보고서를 작성하는 것이 주요 임무입니다.
        보고서는 구조화되고 실행 가능한 권장사항을 포함해야 합니다."""
    } 