from flask import Flask, render_template, request, jsonify
import sqlite3
import os
import logging
from datetime import datetime
import json

# 로컬 모듈 import
from crawler import DongseoCrawler
from notification_service import OneSignalService

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 데이터베이스 경로 설정
DB_PATH = 'notices.db'

# 서비스 인스턴스 생성
crawler = DongseoCrawler(DB_PATH)
notification_service = OneSignalService()

# 애플리케이션 시작 시 데이터베이스 초기화
crawler.init_database()

@app.route('/')
def index():
    """메인 페이지"""
    try:
        # 공지사항 업데이트
        crawler.update_notices()
        
        # 공지사항 조회
        notices = crawler.get_notices(limit=50)
        
        # OneSignal 설정 상태 확인
        onesignal_status = notification_service.get_notification_status()
        
        return render_template('index.html', 
                             notices=notices, 
                             onesignal_status=onesignal_status)
    except Exception as e:
        logger.error(f"메인 페이지 오류: {e}")
        return render_template('index.html', 
                             notices=[], 
                             onesignal_status={"status": "error", "message": str(e)})

@app.route('/api/notices')
def api_notices():
    """공지사항 API"""
    try:
        search_query = request.args.get('search', '')
        limit = int(request.args.get('limit', 50))
        
        notices = crawler.get_notices(search_query, limit)
        
        return jsonify({
            'success': True,
            'notices': notices,
            'count': len(notices)
        })
    except Exception as e:
        logger.error(f"공지사항 API 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/update')
def api_update():
    """공지사항 업데이트 API"""
    try:
        count = crawler.update_notices()
        return jsonify({
            'success': True,
            'message': f'{count}건의 공지사항을 업데이트했습니다.',
            'count': count
        })
    except Exception as e:
        logger.error(f"업데이트 API 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/onesignal/status')
def api_onesignal_status():
    """OneSignal 상태 확인 API"""
    try:
        status = notification_service.get_notification_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"OneSignal 상태 확인 오류: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/demo')
def demo():
    """시연용 관리 페이지"""
    try:
        # OneSignal 상태 확인
        onesignal_status = notification_service.get_notification_status()
        
        # 시연용 공지사항 조회
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute('''
                SELECT * FROM demo_notices 
                ORDER BY created_at DESC LIMIT 10
            ''')
            demo_notices = [dict(row) for row in cursor.fetchall()]
        
        return render_template('demo.html', 
                             onesignal_status=onesignal_status,
                             demo_notices=demo_notices)
    except Exception as e:
        logger.error(f"시연 페이지 오류: {e}")
        return render_template('demo.html', 
                             onesignal_status={"status": "error", "message": str(e)},
                             demo_notices=[])

@app.route('/api/demo/create-notice', methods=['POST'])
def api_demo_create_notice():
    """시연용 공지사항 생성 및 알림 발송"""
    try:
        # 시연용 공지사항 생성
        demo_title = f"[시연] 새로운 공지사항 - {datetime.now().strftime('%m/%d %H:%M')}"
        demo_content = f"시연용으로 생성된 공지사항입니다. 생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # 데이터베이스에 저장
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.execute('''
                INSERT INTO demo_notices (title, content)
                VALUES (?, ?)
            ''', (demo_title, demo_content))
            demo_id = cursor.lastrowid
            
            # 실제 공지사항 테이블에도 추가 (메인 페이지에서 보이도록)
            conn.execute('''
                INSERT INTO notices (number, title, author, date, url)
                VALUES (?, ?, ?, ?, ?)
            ''', ('시연', demo_title, '시스템', datetime.now().strftime('%Y-%m-%d'), '#'))
            
        # 알림 발송
        notification_sent = notification_service.send_new_notice_notification(demo_title)
        
        return jsonify({
            'success': True,
            'message': '시연용 공지사항이 생성되고 알림이 발송되었습니다.',
            'demo_id': demo_id,
            'title': demo_title,
            'notification_sent': notification_sent
        })
        
    except Exception as e:
        logger.error(f"시연용 공지사항 생성 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/demo/send-notification', methods=['POST'])
def api_demo_send_notification():
    """시연용 테스트 알림 발송"""
    try:
        data = request.get_json() or {}
        title = data.get('title', '')
        message = data.get('message', '')
        
        # 알림 발송
        success = notification_service.send_test_notification(title, message)
        
        return jsonify({
            'success': success,
            'message': '테스트 알림이 발송되었습니다.' if success else '알림 발송에 실패했습니다.'
        })
        
    except Exception as e:
        logger.error(f"테스트 알림 발송 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/demo/clear', methods=['POST'])
def api_demo_clear():
    """시연용 공지사항 삭제"""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            # 시연용 공지사항 삭제
            conn.execute("DELETE FROM demo_notices")
            
            # 실제 공지사항에서 시연용 항목 삭제
            conn.execute("DELETE FROM notices WHERE number = '시연'")
            
        return jsonify({
            'success': True,
            'message': '시연용 공지사항이 삭제되었습니다.'
        })
        
    except Exception as e:
        logger.error(f"시연용 공지사항 삭제 오류: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # 개발 환경에서는 디버그 모드로 실행
    app.run(host='0.0.0.0', port=5000, debug=True)

