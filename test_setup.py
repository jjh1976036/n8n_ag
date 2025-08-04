#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
시스템 설정 및 기본 기능 테스트 스크립트
"""

import sys
import os
import json
from datetime import datetime

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_environment():
    """환경 설정 테스트"""
    print("\n🔍 환경 설정 테스트")
    print("-" * 50)
    
    # 1. .env 파일 확인
    env_path = ".env"
    if os.path.exists(env_path):
        print("✅ .env 파일 존재")
        with open(env_path, 'r') as f:
            content = f.read()
            if "ANTHROPIC_API_KEY" in content:
                if "your_anthropic_api_key_here" not in content:
                    print("✅ ANTHROPIC_API_KEY 설정됨")
                else:
                    print("⚠️ ANTHROPIC_API_KEY가 기본값입니다. 실제 API 키로 변경하세요.")
            else:
                print("❌ ANTHROPIC_API_KEY가 .env 파일에 없습니다.")
    else:
        print("❌ .env 파일이 없습니다. env_example.txt를 .env로 복사하세요.")
    
    # 2. 필수 패키지 확인
    print("\n📦 필수 패키지 확인:")
    required_packages = ['anthropic', 'requests', 'beautifulsoup4', 'selenium', 'python-dotenv']
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - pip install {package} 필요")

def test_config():
    """설정 파일 테스트"""
    print("\n⚙️ 설정 파일 테스트")
    print("-" * 50)
    
    try:
        from config.agent_config import AgentConfig
        config = AgentConfig()
        
        print(f"✅ AgentConfig 로드 성공")
        print(f"   - Claude 모델: {config.CLAUDE_MODEL}")
        print(f"   - API 키 설정: {'✅ 설정됨' if config.ANTHROPIC_API_KEY else '❌ 미설정'}")
        
    except Exception as e:
        print(f"❌ 설정 파일 로드 실패: {e}")

def test_claude_client():
    """Claude 클라이언트 테스트"""
    print("\n🤖 Claude 클라이언트 테스트")
    print("-" * 50)
    
    try:
        from utils.claude_client import ClaudeChatCompletionClient
        from config.agent_config import AgentConfig
        
        config = AgentConfig()
        
        if not config.ANTHROPIC_API_KEY or config.ANTHROPIC_API_KEY == "your_anthropic_api_key_here":
            print("⚠️ API 키가 설정되지 않아 Mock 클라이언트 테스트만 진행")
            print("✅ ClaudeChatCompletionClient 클래스 로드 성공")
            return
        
        client = ClaudeChatCompletionClient(
            model=config.CLAUDE_MODEL,
            api_key=config.ANTHROPIC_API_KEY
        )
        print("✅ Claude 클라이언트 생성 성공")
        
        # 간단한 API 호출 테스트
        try:
            import asyncio
            from autogen_core.models import UserMessage
            
            async def test_api():
                messages = [UserMessage(content="Hello, respond with just 'OK'")]
                result = await client.create(messages, max_tokens=10)
                return result.content
            
            response = asyncio.run(test_api())
            print(f"✅ API 호출 테스트 성공: {response[:50]}...")
            
        except Exception as e:
            print(f"❌ API 호출 실패: {e}")
            
    except Exception as e:
        print(f"❌ Claude 클라이언트 테스트 실패: {e}")

def test_agents():
    """에이전트 초기화 테스트"""
    print("\n👥 에이전트 초기화 테스트")
    print("-" * 50)
    
    agents = [
        ("CollectorAgent", "agents.collector_agent"),
        ("ProcessorAgent", "agents.processor_agent"), 
        ("ActionAgent", "agents.action_agent"),
        ("ReporterAgent", "agents.reporter_agent")
    ]
    
    for agent_name, module_path in agents:
        try:
            module = __import__(module_path, fromlist=[agent_name])
            agent_class = getattr(module, agent_name)
            agent = agent_class()
            print(f"✅ {agent_name} 초기화 성공")
        except Exception as e:
            print(f"❌ {agent_name} 초기화 실패: {e}")

def test_web_scraper():
    """웹 스크래퍼 테스트"""
    print("\n🕸️ 웹 스크래퍼 테스트")
    print("-" * 50)
    
    try:
        from utils.web_scraper import WebScraper
        scraper = WebScraper()
        print("✅ WebScraper 초기화 성공")
        
        # 간단한 검색 테스트
        try:
            urls = scraper.search_websites("test news", max_results=2)
            print(f"✅ 웹사이트 검색 테스트 성공: {len(urls)}개 URL 발견")
        except Exception as e:
            print(f"⚠️ 웹사이트 검색 테스트 실패: {e}")
            
        scraper.close_selenium()
        
    except Exception as e:
        print(f"❌ WebScraper 테스트 실패: {e}")

def test_directories():
    """디렉토리 생성 테스트"""
    print("\n📁 디렉토리 생성 테스트")
    print("-" * 50)
    
    directories = ["saved_reports", "reports"]
    
    for dir_name in directories:
        try:
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
                print(f"✅ {dir_name} 디렉토리 생성")
            else:
                print(f"✅ {dir_name} 디렉토리 이미 존재")
        except Exception as e:
            print(f"❌ {dir_name} 디렉토리 생성 실패: {e}")

def create_test_report():
    """테스트 보고서 생성"""
    print("\n📊 테스트 보고서 생성")
    print("-" * 50)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f"test_report_{timestamp}.txt"
    
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("시스템 테스트 보고서\n")
            f.write("=" * 50 + "\n")
            f.write(f"테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("테스트 항목:\n")
            f.write("1. 환경 설정 확인\n")
            f.write("2. 설정 파일 로드\n") 
            f.write("3. Claude 클라이언트 테스트\n")
            f.write("4. 에이전트 초기화\n")
            f.write("5. 웹 스크래퍼 테스트\n")
            f.write("6. 디렉토리 생성\n")
            
        print(f"✅ 테스트 보고서 생성: {report_path}")
        
    except Exception as e:
        print(f"❌ 테스트 보고서 생성 실패: {e}")

def main():
    """메인 테스트 함수"""
    print("🧪 시스템 설정 및 기능 테스트 시작")
    print("=" * 60)
    
    test_environment()
    test_config()
    test_claude_client()
    test_agents()
    test_web_scraper()
    test_directories()
    create_test_report()
    
    print("\n" + "=" * 60)
    print("🏁 테스트 완료!")
    print("\n💡 다음 단계:")
    print("1. 모든 테스트가 통과했다면: python chat_main.py 실행")
    print("2. 실패한 항목이 있다면: 해당 오류를 먼저 해결하세요")
    print("3. API 키 관련 경고가 있다면: .env 파일에 실제 Anthropic API 키를 설정하세요")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 테스트가 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 테스트 실행 중 오류: {e}")
        sys.exit(1)