# n8n AutoGen 웹 정보 수집 에이전트 사용법 가이드

## 📋 목차

1. [시작하기](#시작하기)
2. [설치 및 설정](#설치-및-설정)
3. [사용법](#사용법)
4. [n8n 연동](#n8n-연동)
5. [API 엔드포인트](#api-엔드포인트)
6. [문제 해결](#문제-해결)

## 🚀 시작하기

이 프로젝트는 AutoGen을 사용하여 웹 정보를 수집하고 처리하는 에이전트 시스템입니다. **수집 - 처리 - 행동 - 보고**의 4단계 워크플로우로 구성되어 있습니다.

### 주요 기능

- 🔍 **수집 (Collection)**: 사용자 요청에 따른 웹사이트 정보 수집
- 🔧 **처리 (Processing)**: 수집된 데이터 분석 및 가공
- 🚀 **행동 (Action)**: 결과 기반 행동 수행
- 📊 **보고 (Reporting)**: 사용자에게 결과 전달

## 📦 설치 및 설정

### 1. 저장소 클론

```bash
git clone <repository-url>
cd n8n-ag
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

`.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
# OpenAI API 설정 (필수)
OPENAI_API_KEY=your_openai_api_key_here

# n8n 웹훅 URL (선택사항)
N8N_WEBHOOK_URL=http://localhost:5678/webhook/autogen-workflow-trigger

# 서버 설정
PORT=5000
DEBUG=False

# 웹 스크래핑 설정
MAX_PAGES_TO_SCRAPE=10
REQUEST_TIMEOUT=30

# 데이터 처리 설정
MAX_CONTENT_LENGTH=5000
SUMMARIZATION_LENGTH=500
```

### 4. OpenAI API 키 설정

1. [OpenAI API](https://platform.openai.com/api-keys)에서 API 키를 발급받으세요
2. `.env` 파일의 `OPENAI_API_KEY`에 발급받은 키를 입력하세요

## 🎯 사용법

### 1. 서버 시작

```bash
python agent_server.py
```

서버가 시작되면 다음 메시지가 표시됩니다:

```
🚀 n8n AutoGen 웹 정보 수집 에이전트 서버 시작
============================================================
📋 사용 가능한 엔드포인트:
  GET  /health                    - 헬스 체크
  POST /workflow/execute          - 워크플로우 실행
  GET  /workflow/status/<id>      - 워크플로우 상태 조회
  GET  /workflow/status           - 모든 워크플로우 상태
  GET  /agents/info               - 에이전트 정보
  POST /test                      - 테스트 실행
============================================================
```

### 2. 테스트 실행

```bash
python test_agent.py
```

### 3. API를 통한 워크플로우 실행

```bash
curl -X POST http://localhost:5000/workflow/execute \
  -H "Content-Type: application/json" \
  -d '{
    "user_request": "인공지능 기술 동향 분석",
    "request_id": "test_001"
  }'
```

## 🔗 n8n 연동

### 1. n8n 설치 및 실행

```bash
npm install n8n -g
n8n start
```

### 2. 워크플로우 가져오기

1. n8n 웹 인터페이스에 접속 (http://localhost:5678)
2. "Import from file" 클릭
3. `n8n_workflows/example_workflow.json` 파일 선택
4. 워크플로우 활성화

### 3. 웹훅 URL 설정

n8n에서 생성된 웹훅 URL을 `.env` 파일의 `N8N_WEBHOOK_URL`에 설정하세요.

### 4. n8n을 통한 요청 전송

```bash
curl -X POST http://localhost:5678/webhook/autogen-workflow-trigger \
  -H "Content-Type: application/json" \
  -d '{
    "user_request": "인공지능 기술 동향 분석",
    "request_id": "n8n_test_001"
  }'
```

## 📡 API 엔드포인트

### 1. 헬스 체크

```http
GET /health
```

**응답:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "service": "n8n-autogen-agent-server"
}
```

### 2. 워크플로우 실행

```http
POST /workflow/execute
Content-Type: application/json

{
  "user_request": "분석할 주제",
  "request_id": "optional_request_id"
}
```

**응답:**
```json
{
  "request_id": "req_1704110400",
  "status": "success",
  "message": "워크플로우가 성공적으로 완료되었습니다.",
  "timestamp": "2024-01-01T12:00:00",
  "workflow_summary": {
    "total_steps": 4,
    "completed_steps": 4,
    "execution_time": 45.2,
    "user_request": "분석할 주제"
  },
  "results": {
    "collection": { ... },
    "processing": { ... },
    "action": { ... },
    "report": { ... }
  }
}
```

### 3. 워크플로우 상태 조회

```http
GET /workflow/status/{request_id}
```

**응답:**
```json
{
  "status": "completed",
  "start_time": "2024-01-01T12:00:00",
  "end_time": "2024-01-01T12:00:45",
  "current_step": "completed",
  "progress": 100,
  "steps": [
    {
      "step": "collection",
      "status": "success",
      "timestamp": "2024-01-01T12:00:10",
      "message": "정보 수집 완료"
    }
  ]
}
```

### 4. 에이전트 정보 조회

```http
GET /agents/info
```

**응답:**
```json
{
  "status": "success",
  "agents": {
    "collector": {
      "name": "WebCollector",
      "description": "웹 정보 수집 전문가",
      "capabilities": [
        "웹사이트 검색 및 발견",
        "웹 콘텐츠 스크래핑",
        "데이터 구조화 및 정리",
        "관련성 분석"
      ]
    }
  }
}
```

### 5. 테스트 실행

```http
POST /test
Content-Type: application/json

{
  "user_request": "테스트 요청"
}
```

## 🔧 문제 해결

### 1. OpenAI API 키 오류

**증상:** `OpenAI API Key가 설정되지 않았습니다.` 메시지

**해결방법:**
1. `.env` 파일에 올바른 API 키가 설정되어 있는지 확인
2. API 키가 유효한지 확인
3. 환경 변수가 제대로 로드되는지 확인

### 2. 웹 스크래핑 실패

**증상:** 스크래핑 성공률이 낮음

**해결방법:**
1. 네트워크 연결 확인
2. `REQUEST_TIMEOUT` 값 증가
3. `USER_AGENT` 설정 확인
4. 대상 웹사이트의 robots.txt 확인

### 3. n8n 연동 실패

**증상:** n8n에서 워크플로우가 실행되지 않음

**해결방법:**
1. n8n 서버가 실행 중인지 확인
2. 웹훅 URL이 올바른지 확인
3. 방화벽 설정 확인
4. CORS 설정 확인

### 4. 메모리 부족 오류

**증상:** `MemoryError` 또는 성능 저하

**해결방법:**
1. `MAX_PAGES_TO_SCRAPE` 값 감소
2. `MAX_CONTENT_LENGTH` 값 감소
3. 서버 리소스 증가
4. 배치 처리 구현

### 5. Selenium 오류

**증상:** Chrome 드라이버 관련 오류

**해결방법:**
1. Chrome 브라우저 설치 확인
2. `webdriver-manager` 재설치
3. 헤드리스 모드 설정 확인
4. 시스템 권한 확인

## 📊 모니터링 및 로깅

### 1. 로그 확인

서버 실행 시 콘솔에 상세한 로그가 출력됩니다:

```
🚀 워크플로우 시작: req_1704110400
📝 사용자 요청: 인공지능 기술 동향 분석
🔍 1단계: 정보 수집 시작
📝 검색 쿼리 생성: 인공지능 기술 동향 분석
🌐 발견된 URL 수: 5
📊 스크래핑 완료: 5개 사이트
✅ 워크플로우 완료: req_1704110400
```

### 2. 성능 모니터링

워크플로우 실행 시간과 각 단계별 성능을 추적할 수 있습니다:

```json
{
  "execution_time": 45.2,
  "steps": [
    {
      "step": "collection",
      "duration": 15.3
    },
    {
      "step": "processing", 
      "duration": 12.1
    }
  ]
}
```

## 🔄 확장 및 커스터마이징

### 1. 새로운 에이전트 추가

1. `agents/` 디렉토리에 새 에이전트 클래스 생성
2. `AgentOrchestrator`에 새 에이전트 추가
3. 워크플로우에 새 단계 통합

### 2. 웹 스크래핑 전략 커스터마이징

`utils/web_scraper.py`에서 스크래핑 로직을 수정할 수 있습니다:

- 새로운 웹사이트 타입 지원
- 동적 콘텐츠 처리 개선
- 속도 최적화

### 3. 데이터 처리 로직 확장

`utils/data_processor.py`에서 데이터 처리 로직을 확장할 수 있습니다:

- 새로운 분석 알고리즘 추가
- 머신러닝 모델 통합
- 시각화 기능 추가

## 📞 지원 및 문의

문제가 발생하거나 질문이 있으시면:

1. 이슈 트래커에 버그 리포트 작성
2. 문서 확인
3. 커뮤니티 포럼 참여

---

**참고:** 이 시스템은 교육 및 연구 목적으로 개발되었습니다. 상업적 사용 시 관련 법규를 준수하시기 바랍니다. 