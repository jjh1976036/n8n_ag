#!/usr/bin/env python3
"""
n8n AutoGen 웹 정보 수집 에이전트 서버
수집 - 처리 - 행동 - 보고 워크플로우를 관리하는 메인 서버
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS

# 에이전트 임포트
from agents.collector_agent import CollectorAgent
from agents.processor_agent import ProcessorAgent
from agents.action_agent import ActionAgent
from agents.reporter_agent import ReporterAgent

# 설정 임포트
from config.agent_config import AgentConfig

app = Flask(__name__)
CORS(app)

class AgentOrchestrator:
    """에이전트 오케스트레이터 - 전체 워크플로우 관리"""
    
    def __init__(self):
        self.config = AgentConfig()
        self.collector = CollectorAgent()
        self.processor = ProcessorAgent()
        self.action_executor = ActionAgent()
        self.reporter = ReporterAgent()
        
        # 워크플로우 상태 추적
        self.workflow_status = {}
        
    def execute_workflow(self, user_request: str, request_id: Optional[str] = None) -> Dict[str, Any]:
        """전체 워크플로우 실행"""
        if not request_id:
            request_id = f"req_{int(time.time())}"
            
        print(f"🚀 워크플로우 시작: {request_id}")
        print(f"📝 사용자 요청: {user_request}")
        
        # 워크플로우 상태 초기화
        self.workflow_status[request_id] = {
            'status': 'running',
            'start_time': datetime.now().isoformat(),
            'current_step': 'initialization',
            'progress': 0,
            'steps': []
        }
        
        try:
            # 1단계: 정보 수집 (Collection)
            self._update_status(request_id, 'collection', 25)
            print(f"🔍 1단계: 정보 수집 시작")
            collection_result = self.collector.collect_information(user_request)
            self._log_step(request_id, 'collection', collection_result)
            
            if collection_result['status'] != 'success':
                return self._handle_error(request_id, "정보 수집 실패", collection_result)
                
            # 2단계: 데이터 처리 (Processing)
            self._update_status(request_id, 'processing', 50)
            print(f"🔧 2단계: 데이터 처리 시작")
            processing_result = self.processor.process_data(collection_result)
            self._log_step(request_id, 'processing', processing_result)
            
            if processing_result['status'] != 'success':
                return self._handle_error(request_id, "데이터 처리 실패", processing_result)
                
            # 3단계: 행동 수행 (Action)
            self._update_status(request_id, 'action', 75)
            print(f"🚀 3단계: 행동 수행 시작")
            action_result = self.action_executor.execute_actions(processing_result, user_request)
            self._log_step(request_id, 'action', action_result)
            
            if action_result['status'] != 'success':
                return self._handle_error(request_id, "행동 수행 실패", action_result)
                
            # 4단계: 보고서 생성 (Reporting)
            self._update_status(request_id, 'reporting', 90)
            print(f"📊 4단계: 보고서 생성 시작")
            
            # 모든 데이터 통합
            all_data = {
                'user_request': user_request,
                'collection_data': collection_result,
                'processing_data': processing_result,
                'action_data': action_result
            }
            
            report_result = self.reporter.generate_report(all_data, user_request)
            self._log_step(request_id, 'reporting', report_result)
            
            if report_result['status'] != 'success':
                return self._handle_error(request_id, "보고서 생성 실패", report_result)
                
            # 워크플로우 완료
            self._update_status(request_id, 'completed', 100)
            print(f"✅ 워크플로우 완료: {request_id}")
            
            # 최종 결과 반환
            final_result = {
                'request_id': request_id,
                'status': 'success',
                'message': '워크플로우가 성공적으로 완료되었습니다.',
                'timestamp': datetime.now().isoformat(),
                'workflow_summary': {
                    'total_steps': 4,
                    'completed_steps': 4,
                    'execution_time': self._calculate_execution_time(request_id),
                    'user_request': user_request
                },
                'results': {
                    'collection': collection_result,
                    'processing': processing_result,
                    'action': action_result,
                    'report': report_result
                }
            }
            
            self.workflow_status[request_id]['status'] = 'completed'
            self.workflow_status[request_id]['end_time'] = datetime.now().isoformat()
            self.workflow_status[request_id]['result'] = final_result
            
            return final_result
            
        except Exception as e:
            return self._handle_error(request_id, f"워크플로우 실행 중 오류: {str(e)}", None)
            
    def _update_status(self, request_id: str, current_step: str, progress: int):
        """워크플로우 상태 업데이트"""
        if request_id in self.workflow_status:
            self.workflow_status[request_id]['current_step'] = current_step
            self.workflow_status[request_id]['progress'] = progress
            
    def _log_step(self, request_id: str, step_name: str, result: Dict[str, Any]):
        """단계 실행 결과 로깅"""
        if request_id in self.workflow_status:
            self.workflow_status[request_id]['steps'].append({
                'step': step_name,
                'status': result.get('status', 'unknown'),
                'timestamp': datetime.now().isoformat(),
                'message': result.get('message', '')
            })
            
    def _handle_error(self, request_id: str, error_message: str, error_data: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """오류 처리"""
        print(f"❌ 오류 발생: {error_message}")
        
        error_result = {
            'request_id': request_id,
            'status': 'error',
            'message': error_message,
            'timestamp': datetime.now().isoformat(),
            'error_data': error_data
        }
        
        if request_id in self.workflow_status:
            self.workflow_status[request_id]['status'] = 'error'
            self.workflow_status[request_id]['end_time'] = datetime.now().isoformat()
            self.workflow_status[request_id]['error'] = error_result
            
        return error_result
        
    def _calculate_execution_time(self, request_id: str) -> float:
        """실행 시간 계산"""
        if request_id in self.workflow_status:
            start_time = datetime.fromisoformat(self.workflow_status[request_id]['start_time'])
            end_time = datetime.now()
            return (end_time - start_time).total_seconds()
        return 0.0
        
    def get_workflow_status(self, request_id: str) -> Dict[str, Any]:
        """워크플로우 상태 조회"""
        return self.workflow_status.get(request_id, {'status': 'not_found'})
        
    def get_all_statuses(self) -> Dict[str, Any]:
        """모든 워크플로우 상태 조회"""
        return self.workflow_status
        
    def cleanup(self):
        """리소스 정리"""
        self.collector.cleanup()

# 전역 오케스트레이터 인스턴스
orchestrator = AgentOrchestrator()

@app.route('/health', methods=['GET'])
def health_check():
    """헬스 체크 엔드포인트"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'n8n-autogen-agent-server'
    })

@app.route('/workflow/execute', methods=['POST'])
def execute_workflow():
    """워크플로우 실행 엔드포인트"""
    try:
        data = request.get_json()
        
        if not data or 'user_request' not in data:
            return jsonify({
                'status': 'error',
                'message': 'user_request 필드가 필요합니다.'
            }), 400
            
        user_request = data['user_request']
        request_id = data.get('request_id')
        
        # 워크플로우 실행
        result = orchestrator.execute_workflow(user_request, request_id)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'서버 오류: {str(e)}'
        }), 500

@app.route('/workflow/status/<request_id>', methods=['GET'])
def get_workflow_status(request_id):
    """워크플로우 상태 조회 엔드포인트"""
    try:
        status = orchestrator.get_workflow_status(request_id)
        return jsonify(status)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'상태 조회 오류: {str(e)}'
        }), 500

@app.route('/workflow/status', methods=['GET'])
def get_all_statuses():
    """모든 워크플로우 상태 조회 엔드포인트"""
    try:
        statuses = orchestrator.get_all_statuses()
        return jsonify(statuses)
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'상태 조회 오류: {str(e)}'
        }), 500

@app.route('/agents/info', methods=['GET'])
def get_agents_info():
    """에이전트 정보 조회 엔드포인트"""
    try:
        agents_info = {
            'collector': orchestrator.collector.get_agent_info(),
            'processor': orchestrator.processor.get_agent_info(),
            'action_executor': orchestrator.action_executor.get_agent_info(),
            'reporter': orchestrator.reporter.get_agent_info()
        }
        
        return jsonify({
            'status': 'success',
            'agents': agents_info
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'에이전트 정보 조회 오류: {str(e)}'
        }), 500

@app.route('/test', methods=['POST'])
def test_workflow():
    """테스트용 워크플로우 실행"""
    try:
        data = request.get_json()
        user_request = data.get('user_request', '인공지능 기술 동향 분석')
        
        print(f"🧪 테스트 워크플로우 실행: {user_request}")
        
        # 간단한 테스트 실행
        result = orchestrator.execute_workflow(user_request, f"test_{int(time.time())}")
        
        return jsonify({
            'status': 'success',
            'message': '테스트 완료',
            'result': result
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'테스트 오류: {str(e)}'
        }), 500

@app.errorhandler(404)
def not_found(error):
    """404 오류 처리"""
    return jsonify({
        'status': 'error',
        'message': '요청한 엔드포인트를 찾을 수 없습니다.'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """500 오류 처리"""
    return jsonify({
        'status': 'error',
        'message': '내부 서버 오류가 발생했습니다.'
    }), 500

def main():
    """메인 함수"""
    print("🚀 n8n AutoGen 웹 정보 수집 에이전트 서버 시작")
    print("=" * 60)
    print("📋 사용 가능한 엔드포인트:")
    print("  GET  /health                    - 헬스 체크")
    print("  POST /workflow/execute          - 워크플로우 실행")
    print("  GET  /workflow/status/<id>      - 워크플로우 상태 조회")
    print("  GET  /workflow/status           - 모든 워크플로우 상태")
    print("  GET  /agents/info               - 에이전트 정보")
    print("  POST /test                      - 테스트 실행")
    print("=" * 60)
    
    # 환경 변수 확인
    if not AgentConfig.OPENAI_API_KEY:
        print("⚠️  경고: OPENAI_API_KEY가 설정되지 않았습니다.")
        print("   .env 파일에 OPENAI_API_KEY를 설정하세요.")
        
    if not AgentConfig.N8N_WEBHOOK_URL:
        print("ℹ️  정보: N8N_WEBHOOK_URL이 설정되지 않았습니다.")
        print("   n8n 연동을 원한다면 .env 파일에 N8N_WEBHOOK_URL을 설정하세요.")
        
    # 서버 시작
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    try:
        app.run(host='0.0.0.0', port=port, debug=debug)
    except KeyboardInterrupt:
        print("\n🛑 서버 종료 중...")
        orchestrator.cleanup()
        print("✅ 서버가 안전하게 종료되었습니다.")
    except Exception as e:
        print(f"❌ 서버 시작 오류: {e}")
        orchestrator.cleanup()

if __name__ == '__main__':
    main() 