import requests
import json
import os
import logging
import time
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OneSignalService:
    def __init__(self):
        self.app_id = os.getenv('ONESIGNAL_APP_ID', '412bf56c-7f9d-48a5-9bb1-ced8f7f93755')
        self.rest_api_key = os.getenv('ONESIGNAL_REST_API_KEY')
        self.api_url = "https://onesignal.com/api/v1/notifications"
        
    def is_configured(self):
        """OneSignal이 올바르게 설정되었는지 확인"""
        return bool(self.app_id and self.rest_api_key)
        
    def send_notification(self, title, message, url=None, user_tags=None):
        """푸시 알림 발송"""
        if not self.is_configured():
            logger.warning("OneSignal이 설정되지 않았습니다. 알림을 발송할 수 없습니다.")
            return False
            
        try:
            headers = {
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": f"Basic {self.rest_api_key}"
            }
            
            # 알림 데이터 구성
            notification_data = {
                "app_id": self.app_id,
                "headings": {"en": title, "ko": title},
                "contents": {"en": message, "ko": message},
                "included_segments": ["All"]
            }
            
            # URL이 있으면 추가
            if url:
                notification_data["url"] = url
                
            # 사용자 태그가 있으면 추가
            if user_tags:
                notification_data["filters"] = [
                    {"field": "tag", "key": "user_type", "relation": "=", "value": user_tags}
                ]
                
            response = requests.post(
                self.api_url,
                headers=headers,
                data=json.dumps(notification_data),
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"알림 발송 성공: {result.get('id', 'Unknown ID')}")
                return True
            else:
                logger.error(f"알림 발송 실패: {response.status_code} - {response.text}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"알림 발송 네트워크 오류: {e}")
            return False
        except Exception as e:
            logger.error(f"알림 발송 오류: {e}")
            return False
            
    def send_new_notice_notification(self, notice_title, notice_url=None):
        """새 공지사항 알림 발송"""
        title = "🔔 새로운 공지사항"
        message = f"동서대학교에 새로운 공지사항이 등록되었습니다: {notice_title}"
        
        return self.send_notification(
            title=title,
            message=message,
            url=notice_url,
            user_tags="student"
        )
        
    def send_test_notification(self, custom_title=None, custom_message=None):
        """테스트 알림 발송 (시연용)"""
        title = custom_title or "🎯 시연용 테스트 알림"
        message = custom_message or f"동서대학교 공지사항 알림 시스템 테스트입니다. 현재 시간: {datetime.now().strftime('%H:%M:%S')}"
        
        return self.send_notification(
            title=title,
            message=message,
            user_tags="student"
        )
        
    def get_notification_status(self):
        """OneSignal 서비스 상태 확인"""
        if not self.is_configured():
            return {
                "status": "not_configured",
                "message": "OneSignal API 키가 설정되지 않았습니다.",
                "app_id": self.app_id,
                "has_api_key": False
            }
            
        try:
            # OneSignal 앱 정보 조회로 연결 상태 확인
            headers = {
                "Authorization": f"Basic {self.rest_api_key}"
            }
            
            response = requests.get(
                f"https://onesignal.com/api/v1/apps/{self.app_id}",
                headers=headers,
                timeout=5
            )
            
            if response.status_code == 200:
                app_info = response.json()
                return {
                    "status": "connected",
                    "message": "OneSignal 서비스가 정상적으로 연결되었습니다.",
                    "app_id": self.app_id,
                    "app_name": app_info.get("name", "Unknown"),
                    "has_api_key": True
                }
            else:
                return {
                    "status": "error",
                    "message": f"OneSignal 연결 오류: {response.status_code}",
                    "app_id": self.app_id,
                    "has_api_key": True
                }
                
        except requests.RequestException as e:
            return {
                "status": "network_error",
                "message": f"네트워크 오류: {str(e)}",
                "app_id": self.app_id,
                "has_api_key": True
            }
        except Exception as e:
            return {
                "status": "unknown_error",
                "message": f"알 수 없는 오류: {str(e)}",
                "app_id": self.app_id,
                "has_api_key": True
            }

