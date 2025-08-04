#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
대화형 환경 설정 도구
사용자와 대화를 통해 필요한 API 키와 설정을 수집하고 .env 파일에 저장합니다.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import re

class InteractiveSetup:
    """대화형 설정 클래스"""
    
    def __init__(self):
        self.env_file = Path(".env")
        self.env_example_file = Path("env_example.txt")
        self.current_env = {}
        self.load_existing_env()
    
    def load_existing_env(self):
        """기존 .env 파일 로드"""
        if self.env_file.exists():
            with open(self.env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        self.current_env[key.strip()] = value.strip()
    
    def get_config_sections(self) -> Dict[str, List[Tuple[str, str, bool, str]]]:
        """설정 섹션별 구성 정보 반환
        Format: {section: [(key, description, required, validation_pattern)]}
        """
        return {
            "Claude API (필수)": [
                ("ANTHROPIC_API_KEY", "Anthropic Claude API 키", True, r"^sk-ant-api\d+-.+"),
            ],
            "기본 설정": [
                ("N8N_WEBHOOK_URL", "n8n 웹훅 URL (선택사항)", False, r"^https?://.+"),
                ("PORT", "서버 포트", False, r"^\d+$"),
                ("MAX_PAGES_TO_SCRAPE", "최대 스크래핑 페이지 수", False, r"^\d+$"),
                ("REPORT_EMAIL_RECIPIENT", "보고서 수신 이메일 주소", False, r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"),
            ],
            "웹 스크래핑 MCP (선택사항)": [
                ("FIRECRAWL_API_KEY", "Firecrawl API 키 (고급 웹 스크래핑)", False, r"^fc-.+"),
                ("SEARCH_API_KEY", "웹 검색 API 키", False, r".+"),
            ],
            "커뮤니케이션 MCP (선택사항)": [
                ("GMAIL_CLIENT_ID", "Gmail 클라이언트 ID", False, r".+\.apps\.googleusercontent\.com$"),
                ("GMAIL_CLIENT_SECRET", "Gmail 클라이언트 시크릿", False, r".+"),
                ("SLACK_BOT_TOKEN", "Slack 봇 토큰", False, r"^xoxb-.+"),
                ("SLACK_CHANNEL", "기본 Slack 채널", False, r"^#.+"),
            ],
            "외부 서비스 MCP (선택사항)": [
                ("NOTION_API_KEY", "Notion API 키", False, r"^secret_.+"),
                ("NOTION_DATABASE_ID", "Notion 데이터베이스 ID", False, r"^[a-f0-9\-]{36}$"),
            ]
        }
    
    def validate_input(self, value: str, pattern: str) -> bool:
        """입력값 유효성 검사"""
        if not pattern:
            return True
        return bool(re.match(pattern, value))
    
    def get_user_input(self, key: str, description: str, required: bool, 
                      validation_pattern: str = "") -> Optional[str]:
        """사용자로부터 입력 받기"""
        current_value = self.current_env.get(key, "")
        
        # 현재 값 표시
        if current_value and current_value not in ["YOUR_ANTHROPIC_API_KEY", "your_firecrawl_api_key", 
                                                  "your_gmail_client_id", "your_slack_bot_token", 
                                                  "your_notion_api_key", "user@example.com"]:
            print(f"   현재 값: {self.mask_sensitive_value(key, current_value)}")
        
        # 입력 프롬프트
        required_text = " (필수)" if required else " (선택사항, Enter로 건너뛰기)"
        prompt = f"   {description}{required_text}: "
        
        while True:
            try:
                user_input = input(prompt).strip()
                
                # 빈 입력 처리
                if not user_input:
                    if required and not current_value:
                        print("   ❌ 필수 항목입니다. 값을 입력해주세요.")
                        continue
                    elif not required:
                        return None  # 선택사항이므로 건너뛰기
                    else:
                        return current_value  # 기존 값 유지
                
                # 유효성 검사
                if validation_pattern and not self.validate_input(user_input, validation_pattern):
                    print(f"   ❌ 올바른 형식이 아닙니다. 예상 형식: {self.get_format_hint(key)}")
                    continue
                
                return user_input
                
            except KeyboardInterrupt:
                print("\n\n🛑 설정이 중단되었습니다.")
                return None
            except EOFError:
                return None
    
    def mask_sensitive_value(self, key: str, value: str) -> str:
        """민감한 값 마스킹"""
        if not value or len(value) < 8:
            return value
        
        sensitive_keys = ["API_KEY", "TOKEN", "SECRET", "PASSWORD"]
        if any(sensitive in key for sensitive in sensitive_keys):
            return f"{value[:8]}{'*' * (len(value) - 8)}"
        return value
    
    def get_format_hint(self, key: str) -> str:
        """키별 형식 힌트 제공"""
        hints = {
            "ANTHROPIC_API_KEY": "sk-ant-api03-...",
            "FIRECRAWL_API_KEY": "fc-...",
            "GMAIL_CLIENT_ID": "...apps.googleusercontent.com",
            "SLACK_BOT_TOKEN": "xoxb-...",
            "NOTION_API_KEY": "secret_...",
            "NOTION_DATABASE_ID": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
            "REPORT_EMAIL_RECIPIENT": "user@example.com",
            "N8N_WEBHOOK_URL": "http://localhost:5678/webhook/...",
            "PORT": "5000",
            "MAX_PAGES_TO_SCRAPE": "10"
        }
        return hints.get(key, "적절한 값")
    
    def get_service_info(self, key: str) -> str:
        """서비스별 정보 제공"""
        info = {
            "ANTHROPIC_API_KEY": "https://console.anthropic.com/ 에서 API 키를 발급받으세요.",
            "FIRECRAWL_API_KEY": "https://firecrawl.dev/ 에서 API 키를 발급받으세요. (고급 웹 스크래핑용)",
            "GMAIL_CLIENT_ID": "Google Cloud Console에서 OAuth 2.0 클라이언트를 생성하세요.",
            "SLACK_BOT_TOKEN": "Slack 앱을 생성하고 봇 토큰을 발급받으세요.",
            "NOTION_API_KEY": "Notion 개발자 페이지에서 통합을 생성하세요.",
        }
        return info.get(key, "")
    
    def interactive_setup(self):
        """대화형 설정 시작"""
        print("🔧 대화형 환경 설정 도구")
        print("=" * 60)
        print("📋 이 도구는 프로젝트에 필요한 API 키와 설정을 안내합니다.")
        print("💡 필수 항목만 설정해도 기본 기능이 동작하며, 선택사항은 건너뛸 수 있습니다.")
        print()
        
        # 설정할 값들 저장
        new_config = {}
        
        # 섹션별로 설정 진행
        config_sections = self.get_config_sections()
        
        for section_name, settings in config_sections.items():
            print(f"📦 {section_name}")
            print("-" * 50)
            
            for key, description, required, validation_pattern in settings:
                # 서비스 정보 표시
                service_info = self.get_service_info(key)
                if service_info:
                    print(f"   💡 {service_info}")
                
                # 사용자 입력 받기
                value = self.get_user_input(key, description, required, validation_pattern)
                
                if value is not None:
                    new_config[key] = value
                    print(f"   ✅ {key} 설정됨")
                else:
                    print(f"   ⏭️ {key} 건너뜀")
                
                print()
            
            print()
        
        # 설정 확인
        if new_config:
            print("📋 설정 요약:")
            print("-" * 30)
            for key, value in new_config.items():
                masked_value = self.mask_sensitive_value(key, value)
                print(f"  {key}: {masked_value}")
            print()
            
            # 확인 요청
            confirm = input("🤔 이 설정으로 .env 파일을 업데이트하시겠습니까? (y/N): ").strip().lower()
            
            if confirm in ['y', 'yes', 'ㅇ']:
                self.save_env_file(new_config)
                print("✅ .env 파일이 성공적으로 업데이트되었습니다!")
                
                # 테스트 제안
                print("\n🧪 다음 단계:")
                print("1. python test_setup.py     # 환경 설정 테스트")
                print("2. python test_simple.py    # 기본 기능 테스트")
                print("3. python test_mcp.py       # MCP 통합 테스트")
                print("4. python chat_main.py      # 실제 애플리케이션 실행")
                
                return True
            else:
                print("❌ 설정이 취소되었습니다.")
                return False
        else:
            print("⚠️ 새로운 설정 항목이 없습니다.")
            return False
    
    def save_env_file(self, new_config: Dict[str, str]):
        """새로운 설정으로 .env 파일 저장"""
        # 기존 설정과 새 설정 병합
        merged_config = self.current_env.copy()
        merged_config.update(new_config)
        
        # .env 파일 생성/업데이트
        env_content = []
        
        # 섹션별로 정리해서 저장
        env_content.append("# Claude API 설정 (Anthropic)")
        env_content.append(f"ANTHROPIC_API_KEY={merged_config.get('ANTHROPIC_API_KEY', 'YOUR_ANTHROPIC_API_KEY')}")
        env_content.append("")
        
        env_content.append("# n8n 웹훅 URL (선택사항)")
        env_content.append(f"N8N_WEBHOOK_URL={merged_config.get('N8N_WEBHOOK_URL', 'http://localhost:5678/webhook/autogen-workflow-trigger')}")
        env_content.append("")
        
        env_content.append("# 서버 설정")
        env_content.append(f"PORT={merged_config.get('PORT', '5000')}")
        env_content.append(f"DEBUG={merged_config.get('DEBUG', 'False')}")
        env_content.append("")
        
        env_content.append("# 웹 스크래핑 설정")
        env_content.append(f"MAX_PAGES_TO_SCRAPE={merged_config.get('MAX_PAGES_TO_SCRAPE', '10')}")
        env_content.append(f"REQUEST_TIMEOUT={merged_config.get('REQUEST_TIMEOUT', '30')}")
        env_content.append("")
        
        env_content.append("# 데이터 처리 설정")
        env_content.append(f"MAX_CONTENT_LENGTH={merged_config.get('MAX_CONTENT_LENGTH', '5000')}")
        env_content.append(f"SUMMARIZATION_LENGTH={merged_config.get('SUMMARIZATION_LENGTH', '500')}")
        env_content.append("")
        
        env_content.append("# MCP (Model Context Protocol) 서버 API 키들")
        env_content.append("# 웹 스크래핑 관련")
        env_content.append(f"FIRECRAWL_API_KEY={merged_config.get('FIRECRAWL_API_KEY', 'your_firecrawl_api_key')}")
        env_content.append(f"SEARCH_API_KEY={merged_config.get('SEARCH_API_KEY', 'your_search_api_key')}")
        env_content.append("")
        
        env_content.append("# 커뮤니케이션 도구들")
        env_content.append(f"GMAIL_CLIENT_ID={merged_config.get('GMAIL_CLIENT_ID', 'your_gmail_client_id')}")
        env_content.append(f"GMAIL_CLIENT_SECRET={merged_config.get('GMAIL_CLIENT_SECRET', 'your_gmail_client_secret')}")
        env_content.append(f"SLACK_BOT_TOKEN={merged_config.get('SLACK_BOT_TOKEN', 'your_slack_bot_token')}")
        env_content.append(f"SLACK_CHANNEL={merged_config.get('SLACK_CHANNEL', '#general')}")
        env_content.append("")
        
        env_content.append("# 외부 서비스 연동")
        env_content.append(f"NOTION_API_KEY={merged_config.get('NOTION_API_KEY', 'your_notion_api_key')}")
        env_content.append(f"NOTION_DATABASE_ID={merged_config.get('NOTION_DATABASE_ID', 'your_notion_database_id')}")
        env_content.append("")
        
        env_content.append("# 보고서 수신자 설정")
        env_content.append(f"REPORT_EMAIL_RECIPIENT={merged_config.get('REPORT_EMAIL_RECIPIENT', 'user@example.com')}")
        
        # 파일 저장
        with open(self.env_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(env_content))
    
    def quick_setup(self):
        """빠른 설정 (Claude API만)"""
        print("⚡ 빠른 설정 모드 (Claude API만)")
        print("=" * 40)
        print("📋 기본 기능 사용을 위한 최소 설정입니다.")
        print()
        
        # Claude API 키만 받기
        api_key = self.get_user_input(
            "ANTHROPIC_API_KEY", 
            "Anthropic Claude API 키", 
            True, 
            r"^sk-ant-api\d+-.+"
        )
        
        if api_key:
            new_config = {"ANTHROPIC_API_KEY": api_key}
            
            # 이메일 주소도 받을지 물어보기
            email = input("\n📧 보고서 수신 이메일 주소 (선택사항, Enter로 건너뛰기): ").strip()
            if email and self.validate_input(email, r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"):
                new_config["REPORT_EMAIL_RECIPIENT"] = email
            
            self.save_env_file(new_config)
            print("\n✅ 빠른 설정 완료!")
            print("🚀 이제 python chat_main.py로 애플리케이션을 실행할 수 있습니다.")
            return True
        
        return False


def main():
    """메인 함수"""
    setup = InteractiveSetup()
    
    print("🎯 환경 설정 옵션을 선택하세요:")
    print("1. 🔧 완전한 대화형 설정 (모든 옵션)")
    print("2. ⚡ 빠른 설정 (Claude API만)")
    print("3. 📁 현재 설정 확인")
    print("4. 🚪 종료")
    print()
    
    while True:
        try:
            choice = input("선택하세요 (1-4): ").strip()
            
            if choice == "1":
                setup.interactive_setup()
                break
            elif choice == "2":
                setup.quick_setup()
                break
            elif choice == "3":
                print("\n📋 현재 .env 설정:")
                print("-" * 30)
                if setup.current_env:
                    for key, value in setup.current_env.items():
                        masked_value = setup.mask_sensitive_value(key, value)
                        print(f"  {key}: {masked_value}")
                else:
                    print("  (설정된 환경 변수가 없습니다)")
                print()
            elif choice == "4":
                print("👋 설정을 종료합니다.")
                break
            else:
                print("❌ 올바른 번호를 선택해주세요 (1-4).")
                
        except KeyboardInterrupt:
            print("\n\n🛑 설정이 중단되었습니다.")
            break
        except Exception as e:
            print(f"❌ 오류 발생: {e}")


if __name__ == "__main__":
    main()