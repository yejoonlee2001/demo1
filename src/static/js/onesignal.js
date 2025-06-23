// OneSignal 전용 JavaScript 파일
// 이 파일은 OneSignal 관련 기능만을 담당합니다.

(function() {
    'use strict';
    
    // OneSignal 설정
    const ONESIGNAL_APP_ID = "412bf56c-7f9d-48a5-9bb1-ced8f7f93755";
    
    // OneSignal 초기화 상태
    let oneSignalReady = false;
    let subscriptionState = {
        isSubscribed: false,
        permission: 'default'
    };
    
    // OneSignal 초기화
    function initOneSignal() {
        if (typeof OneSignal === 'undefined') {
            console.warn('OneSignal SDK가 로드되지 않았습니다.');
            return;
        }
        
        window.OneSignalDeferred = window.OneSignalDeferred || [];
        OneSignalDeferred.push(async function(OneSignal) {
            try {
                await OneSignal.init({
                    appId: ONESIGNAL_APP_ID,
                    allowLocalhostAsSecureOrigin: true
                });
                
                oneSignalReady = true;
                console.log('OneSignal 초기화 완료');
                
                // 초기 상태 확인
                await updateSubscriptionState();
                
                // 구독 상태 변경 이벤트 리스너
                OneSignal.on('subscriptionChange', function(isSubscribed) {
                    console.log('구독 상태 변경:', isSubscribed);
                    subscriptionState.isSubscribed = isSubscribed;
                    notifySubscriptionChange();
                });
                
                // 알림 권한 변경 이벤트 리스너
                OneSignal.on('notificationPermissionChange', function(permission) {
                    console.log('알림 권한 변경:', permission);
                    subscriptionState.permission = permission;
                    notifySubscriptionChange();
                });
                
            } catch (error) {
                console.error('OneSignal 초기화 오류:', error);
            }
        });
    }
    
    // 구독 상태 업데이트
    async function updateSubscriptionState() {
        if (!oneSignalReady) return;
        
        try {
            const permission = await OneSignal.getNotificationPermission();
            const isSubscribed = await OneSignal.isPushNotificationsEnabled();
            
            subscriptionState = {
                isSubscribed: isSubscribed,
                permission: permission
            };
            
            console.log('구독 상태 업데이트:', subscriptionState);
            
        } catch (error) {
            console.error('구독 상태 확인 오류:', error);
        }
    }
    
    // 구독 상태 변경 알림
    function notifySubscriptionChange() {
        // 커스텀 이벤트 발생
        const event = new CustomEvent('oneSignalStateChange', {
            detail: subscriptionState
        });
        document.dispatchEvent(event);
    }
    
    // 알림 구독 요청
    async function requestNotificationPermission() {
        if (!oneSignalReady) {
            throw new Error('OneSignal이 초기화되지 않았습니다.');
        }
        
        try {
            const permission = await OneSignal.requestPermission();
            
            if (permission) {
                // 사용자 태그 설정
                await OneSignal.sendTag('user_type', 'student');
                await OneSignal.sendTag('university', 'dongseo');
                
                await updateSubscriptionState();
                return true;
            } else {
                await updateSubscriptionState();
                return false;
            }
            
        } catch (error) {
            console.error('알림 권한 요청 오류:', error);
            throw error;
        }
    }
    
    // 알림 구독 해제
    async function unsubscribeNotifications() {
        if (!oneSignalReady) {
            throw new Error('OneSignal이 초기화되지 않았습니다.');
        }
        
        try {
            await OneSignal.setSubscription(false);
            await updateSubscriptionState();
            return true;
            
        } catch (error) {
            console.error('알림 구독 해제 오류:', error);
            throw error;
        }
    }
    
    // 테스트 알림 발송 (개발용)
    async function sendTestNotification() {
        if (!oneSignalReady) {
            throw new Error('OneSignal이 초기화되지 않았습니다.');
        }
        
        try {
            // 이 기능은 서버 사이드에서 처리되어야 함
            console.log('테스트 알림 발송은 서버에서 처리됩니다.');
            
        } catch (error) {
            console.error('테스트 알림 발송 오류:', error);
            throw error;
        }
    }
    
    // 공개 API
    window.OneSignalHelper = {
        init: initOneSignal,
        isReady: () => oneSignalReady,
        getState: () => subscriptionState,
        subscribe: requestNotificationPermission,
        unsubscribe: unsubscribeNotifications,
        sendTest: sendTestNotification
    };
    
    // DOM 로드 완료 시 자동 초기화
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initOneSignal);
    } else {
        initOneSignal();
    }
    
})();

