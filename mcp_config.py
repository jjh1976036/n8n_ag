#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MCP (Model Context Protocol) 서버 설정 및 관리
각 에이전트별로 최적화된 MCP 서버들을 정의하고 관리합니다.
"""

import os
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class MCPServerConfig:
    """MCP 서버 설정"""
    name: str
    command: str
    args: List[str]
    env: Dict[str, str] = None
    description: str = ""
    
class MCPManager:
    """MCP 서버 관리 클래스"""
    
    def __init__(self):
        self.servers = self._initialize_servers()
    
    def _initialize_servers(self) -> Dict[str, MCPServerConfig]:
        """사용 가능한 MCP 서버들 초기화"""
        return {
            # 웹 스크래핑 및 검색 (CollectorAgent용)
            "firecrawl": MCPServerConfig(
                name="firecrawl",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-firecrawl"],
                env={"FIRECRAWL_API_KEY": os.getenv("FIRECRAWL_API_KEY", "")},
                description="Advanced web scraping and data extraction"
            ),
            
            "web_search": MCPServerConfig(
                name="web_search",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-web-search"],
                env={"SEARCH_API_KEY": os.getenv("SEARCH_API_KEY", "")},
                description="Web search capabilities"
            ),
            
            # 파일 시스템 (ProcessorAgent, ActionAgent용)
            "filesystem": MCPServerConfig(
                name="filesystem",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-filesystem", os.getcwd()],
                description="Secure file system operations"
            ),
            
            # 데이터베이스 (ProcessorAgent, ActionAgent용)
            "sqlite": MCPServerConfig(
                name="sqlite",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-sqlite", "--db-path", "data/news_data.db"],
                description="SQLite database operations"
            ),
            
            # 커뮤니케이션 도구들 (ReporterAgent용)
            "gmail": MCPServerConfig(
                name="gmail",
                command="python",
                args=["-m", "mcp_servers.gmail"],
                env={
                    "GMAIL_CLIENT_ID": os.getenv("GMAIL_CLIENT_ID", ""),
                    "GMAIL_CLIENT_SECRET": os.getenv("GMAIL_CLIENT_SECRET", ""),
                },
                description="Gmail integration for sending reports"
            ),
            
            "slack": MCPServerConfig(
                name="slack",
                command="python",
                args=["-m", "mcp_servers.slack"],
                env={"SLACK_BOT_TOKEN": os.getenv("SLACK_BOT_TOKEN", "")},
                description="Slack integration for notifications"
            ),
            
            # 시각화 도구들 (ReporterAgent용)
            "chart": MCPServerConfig(
                name="chart",
                command="npx",
                args=["-y", "@modelcontextprotocol/server-chart"],
                description="Chart generation and visualization"
            ),
            
            # 문서 생성 (ReporterAgent용)
            "markdown": MCPServerConfig(
                name="markdown",
                command="python",
                args=["-m", "mcp_servers.markdown"],
                description="Markdown document generation"
            ),
            
            # 외부 API 연동 (ReporterAgent용)
            "notion": MCPServerConfig(
                name="notion",
                command="python",
                args=["-m", "mcp_servers.notion"],
                env={"NOTION_API_KEY": os.getenv("NOTION_API_KEY", "")},
                description="Notion workspace integration"
            ),
        }
    
    def get_servers_for_agent(self, agent_name: str) -> List[MCPServerConfig]:
        """에이전트별 추천 MCP 서버 목록 반환"""
        agent_server_mapping = {
            "collector": ["firecrawl", "web_search", "filesystem"],
            "processor": ["filesystem", "sqlite", "chart"],
            "action": ["filesystem", "sqlite"],
            "reporter": ["gmail", "slack", "chart", "markdown", "notion", "filesystem"]
        }
        
        recommended_servers = agent_server_mapping.get(agent_name.lower(), [])
        return [self.servers[server_name] for server_name in recommended_servers if server_name in self.servers]
    
    def get_all_servers(self) -> Dict[str, MCPServerConfig]:
        """모든 사용 가능한 MCP 서버 반환"""
        return self.servers
    
    def is_server_available(self, server_name: str) -> bool:
        """MCP 서버가 사용 가능한지 확인"""
        if server_name not in self.servers:
            return False
            
        server = self.servers[server_name]
        
        # 환경변수 확인
        if server.env:
            for key, value in server.env.items():
                if not value or value == "":
                    return False
        
        return True
    
    def validate_server_requirements(self, server_name: str) -> Dict[str, Any]:
        """서버 요구사항 검증"""
        if server_name not in self.servers:
            return {"valid": False, "error": "Server not found"}
        
        server = self.servers[server_name]
        issues = []
        
        # 환경변수 검증
        if server.env:
            for key, value in server.env.items():
                if not value or value == "":
                    issues.append(f"Missing environment variable: {key}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "server": server
        }

# 전역 MCP 매니저 인스턴스
mcp_manager = MCPManager()

# 에이전트별 MCP 설정
AGENT_MCP_CONFIG = {
    "collector": {
        "primary_servers": ["firecrawl", "web_search"],
        "fallback_servers": ["filesystem"],
        "description": "웹 스크래핑 및 검색에 특화"
    },
    "processor": {
        "primary_servers": ["filesystem", "sqlite"],
        "fallback_servers": ["chart"],
        "description": "데이터 처리 및 분석에 특화"
    },
    "action": {
        "primary_servers": ["filesystem", "sqlite"],
        "fallback_servers": [],
        "description": "파일 저장 및 데이터베이스 작업에 특화"
    },
    "reporter": {
        "primary_servers": ["gmail", "slack", "chart", "markdown"],
        "fallback_servers": ["notion", "filesystem"],
        "description": "다중 채널 보고서 생성 및 전송에 특화"
    }
}