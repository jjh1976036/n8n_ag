# MCP (Model Context Protocol) 통합 가이드

## 개요

이 프로젝트는 4개의 AutoGen 에이전트가 다양한 MCP 서버를 통해 외부 서비스와 연동할 수 있도록 통합되었습니다.

## MCP 서버 매핑

### 🔍 CollectorAgent
- **firecrawl**: 웹 스크래핑 (Firecrawl API)
- **web_search**: 웹 검색 (Search API)

### 🔧 ProcessorAgent  
- **chart**: 데이터 시각화 차트 생성
- **sqlite**: 데이터베이스 분석 및 쿼리

### 💾 ActionAgent
- **filesystem**: 파일 시스템 조작
- **sqlite**: 메타데이터 저장

### 📊 ReporterAgent
- **gmail**: 이메일 전송
- **slack**: Slack 메시지 발송
- **notion**: Notion 데이터베이스 연동
- **chart**: 보고서 차트 생성
- **markdown**: Markdown 문서 생성

## 설치 및 설정

### 1. Python 패키지 설치

```bash
pip install mcp>=1.0.0
pip install anthropic>=0.25.0
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 다음 API 키들을 설정하세요:

```bash
# 필수 - Claude API
ANTHROPIC_API_KEY=your_anthropic_api_key

# 웹 스크래핑 (CollectorAgent)
FIRECRAWL_API_KEY=your_firecrawl_api_key
SEARCH_API_KEY=your_search_api_key

# 커뮤니케이션 (ReporterAgent)
GMAIL_CLIENT_ID=your_gmail_client_id
GMAIL_CLIENT_SECRET=your_gmail_client_secret
SLACK_BOT_TOKEN=your_slack_bot_token
SLACK_CHANNEL=#general

# 외부 서비스 (ReporterAgent)
NOTION_API_KEY=your_notion_api_key
NOTION_DATABASE_ID=your_notion_database_id

# 보고서 수신자
REPORT_EMAIL_RECIPIENT=user@example.com
```

### 3. MCP 서버 시작

```bash
# 모든 MCP 서버 시작
python mcp_launcher.py

# 또는 특정 에이전트용 서버만 시작
python mcp_launcher.py --agent collector
```

## 사용법

### 1. 기본 애플리케이션 실행

```bash
python chat_main.py
```

### 2. MCP 기능 테스트

```bash
python test_mcp.py
```

### 3. MCP 서버 관리

```bash
python mcp_launcher.py
```

## MCP 통합 기능

### CollectorAgent MCP 기능
- **고급 웹 스크래핑**: Firecrawl API를 통한 정확한 콘텐츠 추출
- **지능형 검색**: 웹 검색 API를 통한 관련 정보 수집
- **자동 소스 발견**: 키워드 기반 추가 정보원 탐색

### ProcessorAgent MCP 기능
- **데이터 시각화**: 키워드 빈도, 카테고리 분포 차트 생성
- **데이터베이스 분석**: SQLite를 통한 콘텐츠 통계 분석
- **고급 패턴 인식**: MCP 도구를 활용한 데이터 패턴 분석

### ActionAgent MCP 기능
- **안전한 파일 저장**: MCP 파일시스템을 통한 보안 파일 조작
- **메타데이터 관리**: SQLite 데이터베이스에 보고서 메타데이터 저장
- **데이터 백업**: 자동 백업 및 버전 관리

### ReporterAgent MCP 기능
- **다중 채널 배포**: Gmail, Slack, Notion에 동시 보고서 전송
- **리치 콘텐츠**: 차트, 표, 서식이 포함된 보고서 생성
- **자동 문서화**: Markdown 형식의 구조화된 보고서
- **알림 시스템**: 실시간 진행 상황 알림

## 문제 해결

### API 키가 없는 경우
- 모든 MCP 서버는 Mock 모드로 동작합니다
- 기본 기능은 정상적으로 작동하지만 실제 외부 서비스 연동은 되지 않습니다

### MCP 서버 연결 실패
```bash
# MCP 설정 확인
python -c "from mcp_config import mcp_manager; print(mcp_manager.get_all_servers())"

# 환경 변수 확인
python -c "import os; print([k for k in os.environ.keys() if 'API' in k])"
```

### 파일 권한 오류
```bash
# 저장 디렉토리 권한 확인
mkdir -p saved_reports
chmod 755 saved_reports
```

## 확장 가능성

### 새로운 MCP 서버 추가
1. `mcp_config.py`에 서버 설정 추가
2. `AGENT_MCP_CONFIG`에 에이전트 매핑 추가
3. 해당 에이전트에 MCP 호출 로직 구현

### 커스텀 에이전트 생성
1. 기존 에이전트를 템플릿으로 사용
2. `MCPClientFactory.create_client_for_agent()` 호출
3. MCP 도구를 활용한 고유 기능 구현

## 성능 최적화

### 비동기 처리
- 모든 MCP 호출은 비동기로 처리됩니다
- 여러 서비스 동시 호출로 성능 향상

### 오류 복구
- Mock 모드 자동 전환
- 실패 시 기본 기능으로 fallback
- 자동 재시도 로직

### 캐싱
- MCP 응답 캐싱 (선택적)
- 반복 요청 최적화

## 보안 고려사항

### API 키 관리
- 환경 변수를 통한 안전한 키 관리
- .env 파일은 git에 포함하지 않음
- 키 마스킹을 통한 로그 보안

### 데이터 보호
- 로컬 파일 시스템에만 데이터 저장
- 외부 전송 시 암호화 (해당하는 경우)
- 사용자 데이터 익명화

## 지원

### 로그 확인
```bash
# 애플리케이션 로그
python chat_main.py --verbose

# MCP 테스트 로그
python test_mcp.py
```

### 개발자 도구
- `mcp_config.py`: MCP 서버 설정 관리
- `utils/mcp_client.py`: MCP 클라이언트 구현
- `test_mcp.py`: 종합 테스트 스위트
- `mcp_launcher.py`: 서버 관리 도구