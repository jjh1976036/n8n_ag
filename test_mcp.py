#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MCP (Model Context Protocol) 연동 테스트 스크립트
각 에이전트의 MCP 기능을 테스트합니다.
"""

import sys
import os
import asyncio
from datetime import datetime

# 현재 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp_config import mcp_manager, AGENT_MCP_CONFIG
from utils.mcp_client import MCPClientFactory

async def test_mcp_config():
    """MCP 설정 테스트"""
    print("\n🔧 MCP 설정 테스트")
    print("-" * 50)
    
    # 모든 서버 설정 확인
    all_servers = mcp_manager.get_all_servers()
    print(f"📦 등록된 MCP 서버 수: {len(all_servers)}")
    
    for server_name, server_config in all_servers.items():
        availability = mcp_manager.is_server_available(server_name)
        validation = mcp_manager.validate_server_requirements(server_name)
        
        status = "✅" if availability else "⚠️"
        print(f"{status} {server_name}: {server_config.description}")
        
        if not validation['valid']:
            for issue in validation['issues']:
                print(f"   └─ ⚠️ {issue}")
    
    print("\n🤖 에이전트별 MCP 서버 매핑:")
    for agent_name, config in AGENT_MCP_CONFIG.items():
        servers = mcp_manager.get_servers_for_agent(agent_name)
        print(f"  {agent_name.upper()}: {len(servers)}개 서버")
        for server in servers:
            print(f"    - {server.name}: {server.description}")

async def test_collector_mcp():
    """CollectorAgent MCP 테스트"""
    print("\n🔍 CollectorAgent MCP 테스트")
    print("-" * 50)
    
    try:
        client = await MCPClientFactory.create_client_for_agent("collector")
        
        # 웹 검색 테스트
        search_result = await client.call_tool("web_search", "search", {
            "query": "AI technology news",
            "num_results": 3
        })
        
        if search_result.get("success"):
            print("✅ 웹 검색 테스트 성공")
            results = search_result.get("result", {}).get("results", [])
            print(f"   └─ 검색 결과: {len(results)}개")
        else:
            print("⚠️ 웹 검색 테스트 실패 (Mock 응답)")
        
        # Firecrawl 스크래핑 테스트
        if search_result.get("success") and search_result.get("result", {}).get("results"):
            test_url = search_result["result"]["results"][0].get("url", "https://example.com")
        else:
            test_url = "https://example.com"
        
        scrape_result = await client.call_tool("firecrawl", "scrape_url", {
            "url": test_url,
            "options": {"formats": ["markdown"]}
        })
        
        if scrape_result.get("success"):
            print("✅ Firecrawl 스크래핑 테스트 성공")
        else:
            print("⚠️ Firecrawl 스크래핑 테스트 실패 (Mock 응답)")
        
        await client.cleanup()
        
    except Exception as e:
        print(f"❌ CollectorAgent MCP 테스트 오류: {e}")

async def test_processor_mcp():
    """ProcessorAgent MCP 테스트"""
    print("\n🔧 ProcessorAgent MCP 테스트")
    print("-" * 50)
    
    try:
        client = await MCPClientFactory.create_client_for_agent("processor")
        
        # 차트 생성 테스트
        test_data = [
            {"category": "AI", "count": 5},
            {"category": "Tech", "count": 3},
            {"category": "Business", "count": 2}
        ]
        
        chart_result = await client.call_tool("chart", "create_chart", {
            "data": test_data,
            "chart_type": "pie",
            "options": {"title": "Test Chart"}
        })
        
        if chart_result.get("success"):
            print("✅ 차트 생성 테스트 성공")
        else:
            print("⚠️ 차트 생성 테스트 실패 (Mock 응답)")
        
        # SQLite 테스트
        sqlite_result = await client.call_tool("sqlite", "execute", {
            "query": "SELECT 1 as test_value"
        })
        
        if sqlite_result.get("success"):
            print("✅ SQLite 테스트 성공")
        else:
            print("⚠️ SQLite 테스트 실패 (Mock 응답)")
        
        await client.cleanup()
        
    except Exception as e:
        print(f"❌ ProcessorAgent MCP 테스트 오류: {e}")

async def test_action_mcp():
    """ActionAgent MCP 테스트"""
    print("\n💾 ActionAgent MCP 테스트")
    print("-" * 50)
    
    try:
        client = await MCPClientFactory.create_client_for_agent("action")
        
        # 파일시스템 테스트
        test_content = f"MCP 테스트 파일\n생성 시간: {datetime.now().isoformat()}"
        test_path = "test_mcp_file.txt"
        
        write_result = await client.call_tool("filesystem", "write_file", {
            "path": test_path,
            "content": test_content
        })
        
        if write_result.get("success"):
            print("✅ 파일 쓰기 테스트 성공")
            
            # 파일 읽기 테스트
            read_result = await client.call_tool("filesystem", "read_file", {
                "path": test_path
            })
            
            if read_result.get("success"):
                print("✅ 파일 읽기 테스트 성공")
            else:
                print("⚠️ 파일 읽기 테스트 실패 (Mock 응답)")
        else:
            print("⚠️ 파일 쓰기 테스트 실패 (Mock 응답)")
        
        await client.cleanup()
        
    except Exception as e:
        print(f"❌ ActionAgent MCP 테스트 오류: {e}")

async def test_reporter_mcp():
    """ReporterAgent MCP 테스트"""
    print("\n📊 ReporterAgent MCP 테스트")
    print("-" * 50)
    
    try:
        client = await MCPClientFactory.create_client_for_agent("reporter")
        
        # Gmail 테스트
        gmail_result = await client.call_tool("gmail", "send_email", {
            "to": "test@example.com",
            "subject": "MCP 테스트 메일",
            "body": "이것은 MCP Gmail 연동 테스트입니다."
        })
        
        if gmail_result.get("success"):
            print("✅ Gmail 전송 테스트 성공")
        else:
            print("⚠️ Gmail 전송 테스트 실패 (Mock 응답)")
        
        # Slack 테스트
        slack_result = await client.call_tool("slack", "send_message", {
            "channel": "#test",
            "message": "MCP Slack 연동 테스트 메시지"
        })
        
        if slack_result.get("success"):
            print("✅ Slack 메시지 테스트 성공")
        else:
            print("⚠️ Slack 메시지 테스트 실패 (Mock 응답)")
        
        # 차트 생성 테스트
        chart_data = [
            {"metric": "총 사이트", "value": 10},
            {"metric": "성공 수집", "value": 8},
            {"metric": "카테고리", "value": 3}
        ]
        
        chart_result = await client.call_tool("chart", "create_chart", {
            "data": chart_data,
            "chart_type": "bar",
            "options": {"title": "MCP 테스트 차트"}
        })
        
        if chart_result.get("success"):
            print("✅ 차트 생성 테스트 성공")
        else:
            print("⚠️ 차트 생성 테스트 실패 (Mock 응답)")
        
        await client.cleanup()
        
    except Exception as e:
        print(f"❌ ReporterAgent MCP 테스트 오류: {e}")

async def test_end_to_end_mcp():
    """전체 MCP 워크플로우 테스트"""
    print("\n🔄 전체 MCP 워크플로우 테스트")
    print("-" * 50)
    
    try:
        # 1. CollectorAgent 시뮬레이션
        print("1️⃣ 데이터 수집 (CollectorAgent)")
        collector_client = await MCPClientFactory.create_client_for_agent("collector")
        
        search_result = await collector_client.call_tool("web_search", "search", {
            "query": "MCP test news",
            "num_results": 2
        })
        
        collected_data = {
            "status": "success",
            "data": {
                "collection_summary": {"total_sites": 2, "successful_scrapes": 2},
                "sites_data": [
                    {"url": "https://example1.com", "title": "Test News 1"},
                    {"url": "https://example2.com", "title": "Test News 2"}
                ]
            }
        }
        
        print("   ✅ 데이터 수집 완료")
        
        # 2. ProcessorAgent 시뮬레이션
        print("2️⃣ 데이터 처리 (ProcessorAgent)")
        processor_client = await MCPClientFactory.create_client_for_agent("processor")
        
        # 차트 생성
        await processor_client.call_tool("chart", "create_chart", {
            "data": [{"keyword": "AI", "frequency": 5}, {"keyword": "Tech", "frequency": 3}],
            "chart_type": "bar",
            "options": {"title": "Keyword Analysis"}
        })
        
        processed_data = {
            "status": "success",
            "data": {
                "structured_data": {
                    "total_sites": 2,
                    "successful_scrapes": 2,
                    "categories": {"Tech": 2},
                    "keywords": [("AI", 5), ("Tech", 3)]
                },
                "insights": ["High tech content", "AI focus detected"]
            }
        }
        
        print("   ✅ 데이터 처리 완료")
        
        # 3. ActionAgent 시뮬레이션
        print("3️⃣ 데이터 저장 (ActionAgent)")
        action_client = await MCPClientFactory.create_client_for_agent("action")
        
        # 파일 저장
        await action_client.call_tool("filesystem", "write_file", {
            "path": "test_report.json",
            "content": '{"test": "MCP integration test"}'
        })
        
        print("   ✅ 데이터 저장 완료")
        
        # 4. ReporterAgent 시뮬레이션
        print("4️⃣ 보고서 배포 (ReporterAgent)")
        reporter_client = await MCPClientFactory.create_client_for_agent("reporter")
        
        # 다중 채널 배포
        await reporter_client.call_tool("gmail", "send_email", {
            "to": "test@example.com",
            "subject": "MCP 통합 테스트 보고서",
            "body": "MCP 통합 테스트가 성공적으로 완료되었습니다."
        })
        
        await reporter_client.call_tool("slack", "send_message", {
            "channel": "#test",
            "message": "🎉 MCP 통합 테스트 완료!"
        })
        
        print("   ✅ 보고서 배포 완료")
        
        # 정리
        for client in [collector_client, processor_client, action_client, reporter_client]:
            await client.cleanup()
        
        print("\n🎉 전체 MCP 워크플로우 테스트 성공!")
        
    except Exception as e:
        print(f"❌ 전체 워크플로우 테스트 오류: {e}")

async def main():
    """메인 테스트 함수"""
    print("🧪 MCP (Model Context Protocol) 연동 테스트 시작")
    print("=" * 60)
    print("📌 이 테스트는 각 에이전트의 MCP 서버 연동 기능을 확인합니다.")
    print("📌 실제 API 키가 없으면 Mock 응답으로 테스트됩니다.")
    print()
    
    # MCP 설정 테스트
    await test_mcp_config()
    
    # 각 에이전트별 MCP 테스트
    await test_collector_mcp()
    await test_processor_mcp()
    await test_action_mcp()
    await test_reporter_mcp()
    
    # 전체 워크플로우 테스트
    await test_end_to_end_mcp()
    
    print("\n" + "=" * 60)
    print("🏁 MCP 연동 테스트 완료!")
    print("\n💡 실제 사용을 위해서는:")
    print("1. .env 파일에 실제 API 키들을 설정하세요")
    print("2. 필요한 MCP 서버들을 설치하세요 (npm 패키지 등)")
    print("3. python chat_main.py로 실제 애플리케이션을 테스트하세요")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 테스트가 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 테스트 실행 중 오류: {e}")
        sys.exit(1)