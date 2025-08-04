#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
뉴스 스크래핑 채팅 애플리케이션 실행 스크립트
"""

import sys
import os

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chat_main import main

if __name__ == "__main__":
    print("🗞️ 뉴스 스크래핑 & 분석 시스템을 시작합니다...")
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 사용자에 의해 종료되었습니다.")
    except Exception as e:
        print(f"❌ 실행 중 오류 발생: {e}")
        sys.exit(1)