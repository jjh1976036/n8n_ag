#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MCP (Model Context Protocol) 서버 런처
각 에이전트가 사용할 MCP 서버들을 시작하고 관리합니다.
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from typing import Dict, List, Any
from mcp_config import mcp_manager, AGENT_MCP_CONFIG

class MCPLauncher:
    """MCP 서버 런처 클래스"""
    
    def __init__(self):
        self.running_servers = {}
        self.server_processes = {}
    
    async def check_requirements(self) -> Dict[str, Any]:
        """MCP 서버 요구사항 확인"""
        print("🔍 MCP 서버 요구사항 확인 중...")
        
        requirements_status = {
            "python_packages": {},
            "npm_packages": {},
            "environment_variables": {},
            "overall_ready": True
        }
        
        # Python 패키지 확인
        python_packages = ["mcp", "anthropic"]
        
        for package in python_packages:
            try:
                __import__(package)
                requirements_status["python_packages"][package] = {"status": "installed", "version": "unknown"}
                print(f"  ✅ Python 패키지 '{package}' 설치됨")
            except ImportError:
                requirements_status["python_packages"][package] = {"status": "missing", "version": None}
                requirements_status["overall_ready"] = False
                print(f"  ❌ Python 패키지 '{package}' 누락")
        
        # 환경 변수 확인
        required_env_vars = [
            "ANTHROPIC_API_KEY",
            "FIRECRAWL_API_KEY", 
            "SEARCH_API_KEY",
            "GMAIL_CLIENT_ID",
            "SLACK_BOT_TOKEN",
            "NOTION_API_KEY"
        ]
        
        for env_var in required_env_vars:
            value = os.getenv(env_var)
            if value:
                requirements_status["environment_variables"][env_var] = {"status": "set", "masked_value": f"{value[:8]}..."}
                print(f"  ✅ 환경변수 '{env_var}' 설정됨")
            else:
                requirements_status["environment_variables"][env_var] = {"status": "missing", "masked_value": None}
                print(f"  ⚠️ 환경변수 '{env_var}' 누락 (선택적)")
        
        return requirements_status
    
    async def launch_server(self, server_name: str) -> bool:
        """개별 MCP 서버 시작"""
        server_config = mcp_manager.get_server_config(server_name)
        if not server_config:
            print(f"❌ 서버 설정을 찾을 수 없습니다: {server_name}")
            return False
        
        print(f"🚀 MCP 서버 시작: {server_name}")
        
        try:
            # 실제 구현에서는 서버별로 다른 시작 방법 사용
            if server_name == "firecrawl":
                success = await self._launch_firecrawl_server(server_config)
            elif server_name == "web_search":
                success = await self._launch_web_search_server(server_config)
            elif server_name == "filesystem":
                success = await self._launch_filesystem_server(server_config)
            elif server_name == "sqlite":
                success = await self._launch_sqlite_server(server_config)
            elif server_name == "chart":
                success = await self._launch_chart_server(server_config)
            elif server_name == "gmail":
                success = await self._launch_gmail_server(server_config)
            elif server_name == "slack":
                success = await self._launch_slack_server(server_config)
            elif server_name == "notion":
                success = await self._launch_notion_server(server_config)
            elif server_name == "markdown":
                success = await self._launch_markdown_server(server_config)
            else:
                print(f"⚠️ 알 수 없는 서버 타입: {server_name}")
                success = False
            
            if success:
                self.running_servers[server_name] = True
                print(f"  ✅ {server_name} 서버 시작 성공")
            else:
                print(f"  ❌ {server_name} 서버 시작 실패")
            
            return success
            
        except Exception as e:
            print(f"❌ {server_name} 서버 시작 오류: {e}")
            return False
    
    async def _launch_firecrawl_server(self, config) -> bool:
        """Firecrawl MCP 서버 시작"""
        if not os.getenv("FIRECRAWL_API_KEY"):
            print("   ⚠️ FIRECRAWL_API_KEY가 설정되지 않음 - Mock 모드로 실행")
        return True  # Mock 서버는 항상 성공
    
    async def _launch_web_search_server(self, config) -> bool:
        """웹 검색 MCP 서버 시작"""
        if not os.getenv("SEARCH_API_KEY"):
            print("   ⚠️ SEARCH_API_KEY가 설정되지 않음 - Mock 모드로 실행")
        return True
    
    async def _launch_filesystem_server(self, config) -> bool:
        """파일시스템 MCP 서버 시작"""
        # 기본 디렉토리 생성
        os.makedirs("saved_reports", exist_ok=True)
        return True
    
    async def _launch_sqlite_server(self, config) -> bool:
        """SQLite MCP 서버 시작"""
        return True
    
    async def _launch_chart_server(self, config) -> bool:
        """차트 생성 MCP 서버 시작"""
        return True
    
    async def _launch_gmail_server(self, config) -> bool:
        """Gmail MCP 서버 시작"""
        if not all([os.getenv("GMAIL_CLIENT_ID"), os.getenv("GMAIL_CLIENT_SECRET")]):
            print("   ⚠️ Gmail 인증 정보 누락 - Mock 모드로 실행")
        return True
    
    async def _launch_slack_server(self, config) -> bool:
        """Slack MCP 서버 시작"""
        if not os.getenv("SLACK_BOT_TOKEN"):
            print("   ⚠️ SLACK_BOT_TOKEN이 설정되지 않음 - Mock 모드로 실행")
        return True
    
    async def _launch_notion_server(self, config) -> bool:
        """Notion MCP 서버 시작"""
        if not os.getenv("NOTION_API_KEY"):
            print("   ⚠️ NOTION_API_KEY가 설정되지 않음 - Mock 모드로 실행")
        return True
    
    async def _launch_markdown_server(self, config) -> bool:
        """Markdown MCP 서버 시작"""
        return True
    
    async def launch_all_servers(self) -> Dict[str, bool]:
        """모든 MCP 서버 시작"""
        print("🚀 모든 MCP 서버 시작 중...")
        print("=" * 50)
        
        all_servers = mcp_manager.get_all_servers()
        results = {}
        
        for server_name in all_servers.keys():
            results[server_name] = await self.launch_server(server_name)
            await asyncio.sleep(0.1)  # 서버 간 시작 간격
        
        successful_servers = [name for name, success in results.items() if success]
        failed_servers = [name for name, success in results.items() if not success]
        
        print(f"\n📊 MCP 서버 시작 결과:")
        print(f"  ✅ 성공: {len(successful_servers)}개")
        print(f"  ❌ 실패: {len(failed_servers)}개")
        
        if successful_servers:
            print(f"  성공한 서버: {', '.join(successful_servers)}")
        if failed_servers:
            print(f"  실패한 서버: {', '.join(failed_servers)}")
        
        return results
    
    async def launch_servers_for_agent(self, agent_name: str) -> Dict[str, bool]:
        """특정 에이전트용 MCP 서버들만 시작"""
        print(f"🤖 {agent_name.upper()} 에이전트용 MCP 서버 시작...")
        
        agent_servers = mcp_manager.get_servers_for_agent(agent_name)
        results = {}
        
        for server in agent_servers:
            results[server.name] = await self.launch_server(server.name)
        
        return results
    
    def get_server_status(self) -> Dict[str, Any]:
        """서버 상태 확인"""
        return {
            "running_servers": list(self.running_servers.keys()),
            "total_running": len(self.running_servers),
            "server_details": {
                name: {
                    "status": "running" if running else "stopped",
                    "config": mcp_manager.get_server_config(name).__dict__ if mcp_manager.get_server_config(name) else None
                }
                for name, running in self.running_servers.items()
            }
        }
    
    async def stop_all_servers(self):
        """모든 서버 중지"""
        print("🛑 모든 MCP 서버 중지 중...")
        
        for server_name in list(self.running_servers.keys()):
            try:
                # 실제 구현에서는 서버별 중지 로직 구현
                print(f"  🛑 {server_name} 서버 중지")
                del self.running_servers[server_name]
            except Exception as e:
                print(f"  ❌ {server_name} 서버 중지 오류: {e}")
        
        print("✅ 모든 서버 중지 완료")


async def main():
    """메인 런처 함수"""
    print("🎯 MCP (Model Context Protocol) 서버 런처")
    print("=" * 60)
    
    launcher = MCPLauncher()
    
    # 요구사항 확인
    requirements = await launcher.check_requirements()
    
    if not requirements["overall_ready"]:
        print("\n⚠️ 일부 요구사항이 충족되지 않았습니다.")
        print("누락된 패키지를 설치하세요:")
        
        for package, info in requirements["python_packages"].items():
            if info["status"] == "missing":
                print(f"  pip install {package}")
    
    print(f"\n🚀 MCP 서버 시작 옵션:")
    print("1. 모든 서버 시작")
    print("2. 에이전트별 서버 시작")
    print("3. 서버 상태 확인")
    print("4. 테스트 실행")
    print("5. 종료")
    
    while True:
        try:
            choice = input("\n선택하세요 (1-5): ").strip()
            
            if choice == "1":
                results = await launcher.launch_all_servers()
                
            elif choice == "2":
                print("\n사용 가능한 에이전트:")
                for agent_name in AGENT_MCP_CONFIG.keys():
                    servers = mcp_manager.get_servers_for_agent(agent_name)
                    print(f"  {agent_name}: {len(servers)}개 서버")
                
                agent_name = input("에이전트 이름을 입력하세요: ").strip().lower()
                if agent_name in AGENT_MCP_CONFIG:
                    results = await launcher.launch_servers_for_agent(agent_name)
                else:
                    print("❌ 유효하지 않은 에이전트 이름")
                    
            elif choice == "3":
                status = launcher.get_server_status()
                print(f"\n📊 서버 상태:")
                print(f"  실행 중인 서버: {status['total_running']}개")
                for server_name in status['running_servers']:
                    print(f"    - {server_name}")
                    
            elif choice == "4":
                print("\n🧪 MCP 테스트 실행...")
                # test_mcp.py 실행
                os.system("python test_mcp.py")
                
            elif choice == "5":
                await launcher.stop_all_servers()
                print("👋 런처를 종료합니다.")
                break
                
            else:
                print("❌ 유효하지 않은 선택입니다.")
                
        except KeyboardInterrupt:
            print("\n\n🛑 중단됨...")
            await launcher.stop_all_servers()
            break
        except Exception as e:
            print(f"❌ 오류 발생: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 런처가 중단되었습니다.")
    except Exception as e:
        print(f"\n❌ 런처 실행 오류: {e}")
        sys.exit(1)