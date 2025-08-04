#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
환경 설정 마법사
처음 사용하는 사용자를 위한 단계별 설정 가이드
"""

import os
import sys
from pathlib import Path

def main():
    """설정 마법사 메인 함수"""
    print("환경 설정 마법사에 오신 것을 환영합니다!")
    print("=" * 60)
    print("이 도구는 Claude 뉴스 스크래핑 시스템의 초기 설정을 도와드립니다.")
    print("단계별로 안내에 따라 진행하시면 됩니다.")
    print()
    
    # 현재 상태 점검
    check_current_status()
    
    print("\n설정 옵션을 선택하세요:")
    print("1. 빠른 시작 (Claude API만 설정)")
    print("2. 완전한 설정 (모든 기능 포함)")
    print("3. 현재 설정 확인")
    print("4. 설정 테스트")
    print("5. 종료")
    print()
    
    while True:
        try:
            choice = input("선택하세요 (1-5): ").strip()
            
            if choice == "1":
                quick_start()
                break
            elif choice == "2":
                full_setup()
                break
            elif choice == "3":
                check_current_setup()
            elif choice == "4":
                test_setup()
            elif choice == "5":
                print("👋 설정 마법사를 종료합니다.")
                break
            else:
                print("❌ 올바른 번호를 선택해주세요 (1-5).")
                
        except KeyboardInterrupt:
            print("\n\n🛑 설정이 중단되었습니다.")
            break

def check_current_status():
    """현재 상태 점검"""
    print("현재 설정 상태를 점검하는 중...")
    
    # .env 파일 확인
    env_exists = Path(".env").exists()
    print(f"  .env 파일: {'존재함' if env_exists else '없음'}")
    
    # API 키 확인
    if env_exists:
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key and anthropic_key.startswith("sk-ant-api"):
            print("  Claude API 키: 설정됨")
        else:
            print("  Claude API 키: 미설정")
    else:
        print("  Claude API 키: 미설정")
    
    # 필수 파일들 확인
    required_files = ["chat_main.py", "interactive_setup.py", "agents/", "utils/"]
    for file_path in required_files:
        exists = Path(file_path).exists()
        print(f"  {file_path}: {'OK' if exists else 'Missing'}")

def quick_start():
    """빠른 시작 설정"""
    print("\n🚀 빠른 시작 설정")
    print("=" * 30)
    print("📋 Claude API 키만 설정하여 기본 기능을 사용할 수 있습니다.")
    print()
    
    try:
        from interactive_setup import InteractiveSetup
        setup = InteractiveSetup()
        
        if setup.quick_setup():
            print("\n🎉 빠른 설정이 완료되었습니다!")
            suggest_next_steps()
        else:
            print("❌ 설정이 취소되었습니다.")
            
    except ImportError:
        print("❌ 설정 도구를 찾을 수 없습니다.")
        manual_guide()

def full_setup():
    """완전한 설정"""
    print("\n🔧 완전한 설정")
    print("=" * 20)
    print("📋 모든 MCP 서비스를 포함한 완전한 설정을 진행합니다.")
    print()
    
    try:
        from interactive_setup import InteractiveSetup
        setup = InteractiveSetup()
        
        if setup.interactive_setup():
            print("\n🎉 완전한 설정이 완료되었습니다!")
            suggest_next_steps()
        else:
            print("❌ 설정이 취소되었습니다.")
            
    except ImportError:
        print("❌ 설정 도구를 찾을 수 없습니다.")
        manual_guide()

def check_current_setup():
    """현재 설정 확인"""
    print("\n📊 현재 설정 확인")
    print("=" * 25)
    
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env 파일이 존재하지 않습니다.")
        return
    
    print("📄 .env 파일 내용:")
    print("-" * 30)
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        # 민감한 정보 마스킹
                        if any(sensitive in key.upper() for sensitive in ['KEY', 'TOKEN', 'SECRET', 'PASSWORD']):
                            if len(value) > 8:
                                value = f"{value[:8]}{'*' * (len(value) - 8)}"
                        print(f"  {key}: {value}")
                elif line.startswith('#'):
                    print(f"  {line}")
                    
    except Exception as e:
        print(f"❌ 파일 읽기 오류: {e}")

def test_setup():
    """설정 테스트"""
    print("\n🧪 설정 테스트")
    print("=" * 15)
    print("📋 현재 설정으로 시스템 테스트를 실행합니다.")
    print()
    
    # 기본 테스트 순서 제안
    print("🔄 권장 테스트 순서:")
    print("1. python test_setup.py     # 환경 설정 테스트")
    print("2. python test_simple.py    # 기본 기능 테스트")
    print("3. python test_mcp.py       # MCP 통합 테스트")
    print()
    
    choice = input("🤔 지금 바로 환경 설정 테스트를 실행하시겠습니까? (Y/n): ").strip().lower()
    
    if choice in ['', 'y', 'yes', 'ㅇ']:
        print("\n🧪 test_setup.py 실행 중...")
        try:
            os.system("python test_setup.py")
        except Exception as e:
            print(f"❌ 테스트 실행 오류: {e}")
    else:
        print("💡 나중에 직접 실행하시면 됩니다.")

def suggest_next_steps():
    """다음 단계 제안"""
    print("\n🎯 다음 단계:")
    print("=" * 15)
    print("1. 📊 python test_setup.py      # 설정 확인")
    print("2. 🧪 python test_simple.py     # 기능 테스트")
    print("3. 🔗 python test_mcp.py        # MCP 테스트")
    print("4. 🚀 python chat_main.py       # 실제 실행")
    print()
    
    choice = input("🤔 지금 바로 애플리케이션을 시작하시겠습니까? (Y/n): ").strip().lower()
    
    if choice in ['', 'y', 'yes', 'ㅇ']:
        print("\n🚀 chat_main.py 실행 중...")
        try:
            os.system("python chat_main.py")
        except Exception as e:
            print(f"❌ 실행 오류: {e}")
    else:
        print("💡 python chat_main.py로 언제든 시작할 수 있습니다.")

def manual_guide():
    """수동 설정 가이드"""
    print("\n📋 수동 설정 가이드")
    print("=" * 25)
    print("1. .env 파일을 생성하세요:")
    print("   touch .env")
    print()
    print("2. 다음 내용을 .env 파일에 추가하세요:")
    print("   ANTHROPIC_API_KEY=sk-ant-api03-YOUR_ACTUAL_API_KEY")
    print()
    print("3. API 키 발급:")
    print("   https://console.anthropic.com/ 방문")
    print("   Account Settings > API Keys > Create Key")
    print()
    print("4. 설정 완료 후:")
    print("   python chat_main.py")

if __name__ == "__main__":
    main()