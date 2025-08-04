#!/usr/bin/env python3
"""
tiktoken 설치 전용 스크립트
"""

import subprocess
import sys

def install_tiktoken():
    """tiktoken 설치"""
    print("🚀 tiktoken 설치 시작")
    print("=" * 40)
    
    # 1. pip 업그레이드
    print("1. pip 업그레이드 중...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        print("   ✅ pip 업그레이드 완료")
    except Exception as e:
        print(f"   ⚠️ pip 업그레이드 실패: {e}")
    
    # 2. tiktoken 설치 시도
    print("\n2. tiktoken 설치 중...")
    try:
        # 방법 1: 기본 설치
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tiktoken"])
        print("   ✅ tiktoken 설치 성공!")
        return True
    except Exception as e:
        print(f"   ❌ 기본 설치 실패: {e}")
        
        try:
            # 방법 2: 특정 버전 설치
            print("   🔄 특정 버전으로 재시도...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "tiktoken==0.5.0"])
            print("   ✅ tiktoken 0.5.0 설치 성공!")
            return True
        except Exception as e2:
            print(f"   ❌ 특정 버전 설치도 실패: {e2}")
            
            try:
                # 방법 3: 바이너리 wheel 설치
                print("   🔄 바이너리 wheel으로 재시도...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--only-binary=all", "tiktoken"])
                print("   ✅ tiktoken 바이너리 설치 성공!")
                return True
            except Exception as e3:
                print(f"   ❌ 바이너리 설치도 실패: {e3}")
                return False

def main():
    """메인 함수"""
    success = install_tiktoken()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 tiktoken 설치 성공!")
        print("\n다음 명령어로 테스트해보세요:")
        print("python simple_fix_test.py")
    else:
        print("⚠️ tiktoken 설치 실패")
        print("\n대안 방법:")
        print("1. Visual Studio Build Tools 설치")
        print("2. Rust 컴파일러 설치: https://rustup.rs")
        print("3. 모의 클라이언트 사용 (이미 작동 중)")
        print("\n현재 상태: 모의 클라이언트로 정상 작동 중")

if __name__ == "__main__":
    main() 