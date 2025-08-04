#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MCP (Model Context Protocol) 클라이언트 유틸리티
에이전트들이 MCP 서버와 통신하기 위한 클라이언트 구현
"""

import asyncio
import json
import subprocess
import sys
import os
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager
from dataclasses import asdict

# MCP 관련 패키지 (설치 필요: pip install mcp)
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    print("⚠️ MCP packages not installed. Install with: pip install mcp")
    MCP_AVAILABLE = False

from mcp_config import MCPServerConfig, mcp_manager

class MCPClient:
    """MCP 서버와 통신하는 클라이언트"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.active_sessions = {}
        self.available_servers = mcp_manager.get_servers_for_agent(agent_name)
        
    async def initialize_servers(self) -> Dict[str, bool]:
        """에이전트용 MCP 서버들 초기화"""
        initialization_results = {}
        
        for server_config in self.available_servers:
            try:
                success = await self._initialize_server(server_config)
                initialization_results[server_config.name] = success
                if success:
                    print(f"✅ {server_config.name} MCP 서버 초기화 성공")
                else:
                    print(f"⚠️ {server_config.name} MCP 서버 초기화 실패")
            except Exception as e:
                print(f"❌ {server_config.name} MCP 서버 오류: {e}")
                initialization_results[server_config.name] = False
        
        return initialization_results
    
    async def _initialize_server(self, server_config: MCPServerConfig) -> bool:
        """개별 MCP 서버 초기화"""
        if not MCP_AVAILABLE:
            print(f"📦 MCP 패키지가 설치되지 않아 {server_config.name} 서버를 Mock으로 실행합니다.")
            return self._create_mock_session(server_config.name)
        
        try:
            # 서버 프로세스 시작
            server_params = StdioServerParameters(
                command=server_config.command,
                args=server_config.args,
                env=server_config.env or {}
            )
            
            # 비동기 컨텍스트에서 클라이언트 세션 생성
            session = await self._create_session(server_params)
            if session:
                self.active_sessions[server_config.name] = session
                return True
            
        except Exception as e:
            print(f"❌ {server_config.name} 서버 초기화 실패: {e}")
            # Fallback to mock
            return self._create_mock_session(server_config.name)
        
        return False
    
    async def _create_session(self, server_params: StdioServerParameters):
        """실제 MCP 세션 생성"""
        try:
            async with stdio_client(server_params) as (read, write):
                session = ClientSession(read, write)
                await session.initialize()
                return session
        except Exception as e:
            print(f"⚠️ MCP 세션 생성 실패: {e}")
            return None
    
    def _create_mock_session(self, server_name: str) -> bool:
        """Mock MCP 세션 생성 (실제 MCP가 없을 때)"""
        mock_session = MockMCPSession(server_name)
        self.active_sessions[server_name] = mock_session
        return True
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """MCP 서버의 도구 호출"""
        if server_name not in self.active_sessions:
            return {
                "success": False,
                "error": f"Server {server_name} not initialized"
            }
        
        session = self.active_sessions[server_name]
        
        try:
            if isinstance(session, MockMCPSession):
                return await session.call_tool(tool_name, arguments)
            else:
                # 실제 MCP 호출
                result = await session.call_tool(tool_name, arguments)
                return {
                    "success": True,
                    "result": result
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def list_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """MCP 서버의 사용 가능한 도구 목록"""
        if server_name not in self.active_sessions:
            return []
        
        session = self.active_sessions[server_name]
        
        try:
            if isinstance(session, MockMCPSession):
                return session.list_tools()
            else:
                tools = await session.list_tools()
                return tools.tools if tools else []
        except Exception as e:
            print(f"⚠️ {server_name} 도구 목록 조회 실패: {e}")
            return []
    
    async def cleanup(self):
        """리소스 정리"""
        for server_name, session in self.active_sessions.items():
            try:
                if hasattr(session, 'close'):
                    await session.close()
            except:
                pass
        self.active_sessions.clear()

class MockMCPSession:
    """MCP가 설치되지 않았을 때 사용하는 Mock 세션"""
    
    def __init__(self, server_name: str):
        self.server_name = server_name
        self.mock_tools = self._get_mock_tools()
    
    def _get_mock_tools(self) -> Dict[str, Dict[str, Any]]:
        """서버별 Mock 도구 정의"""
        tools_by_server = {
            "firecrawl": {
                "scrape_url": {
                    "description": "Extract content from a URL",
                    "parameters": ["url", "options"]
                },
                "crawl_site": {
                    "description": "Crawl an entire website",
                    "parameters": ["url", "max_pages"]
                }
            },
            "web_search": {
                "search": {
                    "description": "Search the web",
                    "parameters": ["query", "num_results"]
                }
            },
            "filesystem": {
                "read_file": {
                    "description": "Read file contents",
                    "parameters": ["path"]
                },
                "write_file": {
                    "description": "Write file contents",
                    "parameters": ["path", "content"]
                },
                "list_directory": {
                    "description": "List directory contents",
                    "parameters": ["path"]
                }
            },
            "gmail": {
                "send_email": {
                    "description": "Send email via Gmail",
                    "parameters": ["to", "subject", "body"]
                }
            },
            "slack": {
                "send_message": {
                    "description": "Send message to Slack",
                    "parameters": ["channel", "message"]
                }
            },
            "chart": {
                "create_chart": {
                    "description": "Create data visualization chart",
                    "parameters": ["data", "chart_type", "options"]
                }
            }
        }
        return tools_by_server.get(self.server_name, {})
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """사용 가능한 Mock 도구 목록"""
        tools = []
        for tool_name, tool_info in self.mock_tools.items():
            tools.append({
                "name": tool_name,
                "description": tool_info["description"],
                "parameters": tool_info["parameters"]
            })
        return tools
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Mock 도구 호출"""
        if tool_name not in self.mock_tools:
            return {
                "success": False,
                "error": f"Tool {tool_name} not found in {self.server_name}"
            }
        
        # Mock 응답 생성
        mock_responses = {
            "scrape_url": {
                "success": True,
                "content": f"Mock scraped content from {arguments.get('url', 'unknown URL')}",
                "title": "Mock Page Title",
                "metadata": {"word_count": 150}
            },
            "search": {
                "success": True,
                "results": [
                    {
                        "title": f"Mock search result for: {arguments.get('query', 'unknown query')}",
                        "url": "https://example.com/mock-result",
                        "snippet": "Mock search result snippet..."
                    }
                ]
            },
            "send_email": {
                "success": True,
                "message": f"Mock email sent to {arguments.get('to', 'unknown recipient')}"
            },
            "send_message": {
                "success": True,
                "message": f"Mock Slack message sent to {arguments.get('channel', 'unknown channel')}"
            },
            "create_chart": {
                "success": True,
                "chart_url": "mock-chart-url.png",
                "message": "Mock chart created successfully"
            }
        }
        
        response = mock_responses.get(tool_name, {
            "success": True,
            "message": f"Mock response for {tool_name} with arguments: {arguments}"
        })
        
        print(f"🔧 Mock {self.server_name}.{tool_name}: {response.get('message', 'Executed successfully')}")
        return response

# 에이전트별 MCP 클라이언트 팩토리
class MCPClientFactory:
    """에이전트별 MCP 클라이언트 생성 팩토리"""
    
    @staticmethod
    async def create_client_for_agent(agent_name: str) -> MCPClient:
        """에이전트용 MCP 클라이언트 생성 및 초기화"""
        client = MCPClient(agent_name)
        await client.initialize_servers()
        return client
    
    @staticmethod
    def get_available_servers_for_agent(agent_name: str) -> List[MCPServerConfig]:
        """에이전트별 사용 가능한 서버 목록"""
        return mcp_manager.get_servers_for_agent(agent_name)