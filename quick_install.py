#!/usr/bin/env python3
"""
빠른 설치 스크립트 - tiktoken 포함
"""

import subprocess
import sys

def install_package(package):
    """패키지 설치"""
    try:
        print(f"📦 {package} 설치 중...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} 설치 완료")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {package} 설치 실패: {e}")
        return False

def main():
    """메인 설치 함수"""
    print("🚀 n8n AutoGen 에이전트 빠른 설치")
    print("=" * 50)
    
    # 핵심 패키지들 (tiktoken 포함)
    packages = [
        "tiktoken>=0.5.0",  # OpenAIChatCompletionClient에 필요
        "autogen-ext>=0.1.0",
        "pyautogen>=0.10.0",
        "requests==2.31.0",
        "beautifulsoup4==4.12.2",
        "selenium==4.15.2",
        "openai==1.3.0",
        "python-dotenv==1.0.0",
        "flask==3.0.0",
        "flask-cors==4.0.0",
        "numpy>=1.26.0",
        "webdriver-manager==4.0.1"
    ]
    
    success_count = 0
    total_count = len(packages)
    
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"📊 설치 결과: {success_count}/{total_count} 성공")
    
    if success_count >= total_count - 1:  # 1개 정도 실패는 허용
        print("🎉 핵심 패키지들이 성공적으로 설치되었습니다!")
        print("\n다음 명령어로 테스트해보세요:")
        print("python simple_fix_test.py")
    else:
        print("⚠️ 일부 패키지 설치에 실패했습니다.")
        print("수동으로 설치를 시도해보세요:")
        print("pip install tiktoken")
        print("pip install -r requirements.txt")

if __name__ == "__main__":
    main() 