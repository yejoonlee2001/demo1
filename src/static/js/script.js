// 동서대학교 공지사항 알림 시스템 JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // DOM 요소들
    const notificationBtn = document.getElementById('notificationBtn');
    const notificationIcon = document.getElementById('notificationIcon');
    const notificationText = document.getElementById('notificationText');
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    const refreshBtn = document.getElementById('refreshBtn');
    const noticesList = document.getElementById('noticesList');
    const noticeCount = document.getElementById('noticeCount');
    const lastUpdate = document.getElementById('lastUpdate');

    // OneSignal 상태
    let isSubscribed = false;
    let oneSignalInitialized = false;

    // OneSignal 초기화 및 상태 확인
    initializeOneSignal();

    // 이벤트 리스너 등록
    if (notificationBtn) {
        notificationBtn.addEventListener('click', handleNotificationToggle);
    }

    if (searchBtn) {
        searchBtn.addEventListener('click', handleSearch);
    }

    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                handleSearch();
            }
        });
    }

    if (refreshBtn) {
        refreshBtn.addEventListener('click', handleRefresh);
    }

    // OneSignal 초기화
    async function initializeOneSignal() {
        try {
            // OneSignal이 로드될 때까지 대기
            if (typeof OneSignal !== 'undefined') {
                await OneSignal.init({
                    appId: "412bf56c-7f9d-48a5-9bb1-ced8f7f93755",
                });

                oneSignalInitialized = true;
                
                // 구독 상태 확인
                const permission = await OneSignal.getNotificationPermission();
                const isPushSupported = OneSignal.isPushNotificationsSupported();
                
                if (isPushSupported) {
                    if (permission === 'granted') {
                        isSubscribed = await OneSignal.isPushNotificationsEnabled();
                        updateNotificationButton();
                    } else {
                        updateNotificationButton();
                    }
                } else {
                    updateNotificationButtonUnsupported();
                }

                // 구독 상태 변경 이벤트 리스너
                OneSignal.on('subscriptionChange', function(isSubscribed) {
                    updateNotificationButton();
                });

            } else {
                console.warn('OneSignal이 로드되지 않았습니다.');
                updateNotificationButtonError();
            }
        } catch (error) {
            console.error('OneSignal 초기화 오류:', error);
            updateNotificationButtonError();
        }
    }

    // 알림 토글 처리
    async function handleNotificationToggle() {
        if (!oneSignalInitialized) {
            showAlert('OneSignal이 초기화되지 않았습니다.', 'error');
            return;
        }

        try {
            notificationBtn.disabled = true;
            
            if (!isSubscribed) {
                // 구독 요청
                notificationText.textContent = '권한 요청 중...';
                
                const permission = await OneSignal.requestPermission();
                
                if (permission) {
                    // 사용자 태그 설정
                    await OneSignal.sendTag('user_type', 'student');
                    
                    isSubscribed = true;
                    updateNotificationButton();
                    showAlert('✅ 알림 구독이 완료되었습니다!', 'success');
                } else {
                    showAlert('❌ 알림 권한이 거부되었습니다.', 'error');
                    updateNotificationButton();
                }
            } else {
                // 구독 해제
                notificationText.textContent = '구독 해제 중...';
                
                await OneSignal.setSubscription(false);
                
                isSubscribed = false;
                updateNotificationButton();
                showAlert('🔕 알림 구독이 해제되었습니다.', 'info');
            }
        } catch (error) {
            console.error('알림 토글 오류:', error);
            showAlert('❌ 오류가 발생했습니다: ' + error.message, 'error');
            updateNotificationButton();
        } finally {
            notificationBtn.disabled = false;
        }
    }

    // 알림 버튼 상태 업데이트
    function updateNotificationButton() {
        if (!notificationBtn) return;

        if (isSubscribed) {
            notificationIcon.textContent = '🔔';
            notificationText.textContent = '알림 구독 중';
            notificationBtn.style.background = 'rgba(40, 167, 69, 0.2)';
            notificationBtn.style.borderColor = 'rgba(40, 167, 69, 0.5)';
        } else {
            notificationIcon.textContent = '🔔';
            notificationText.textContent = '알림 구독하기';
            notificationBtn.style.background = 'rgba(255, 255, 255, 0.2)';
            notificationBtn.style.borderColor = 'rgba(255, 255, 255, 0.3)';
        }
    }

    // 알림 버튼 - 지원되지 않는 브라우저
    function updateNotificationButtonUnsupported() {
        if (!notificationBtn) return;

        notificationIcon.textContent = '❌';
        notificationText.textContent = '알림 미지원';
        notificationBtn.disabled = true;
        notificationBtn.style.opacity = '0.6';
    }

    // 알림 버튼 - 오류 상태
    function updateNotificationButtonError() {
        if (!notificationBtn) return;

        notificationIcon.textContent = '⚠️';
        notificationText.textContent = '알림 설정 오류';
        notificationBtn.disabled = true;
        notificationBtn.style.opacity = '0.6';
    }

    // 검색 처리
    async function handleSearch() {
        const query = searchInput.value.trim();
        
        try {
            searchBtn.disabled = true;
            searchBtn.textContent = '검색 중...';
            
            const response = await fetch(`/api/notices?search=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            if (data.success) {
                updateNoticesList(data.notices);
                updateNoticeCount(data.count);
                
                if (query) {
                    showAlert(`"${query}" 검색 결과: ${data.count}건`, 'info');
                }
            } else {
                showAlert('검색 중 오류가 발생했습니다.', 'error');
            }
        } catch (error) {
            console.error('검색 오류:', error);
            showAlert('검색 중 오류가 발생했습니다.', 'error');
        } finally {
            searchBtn.disabled = false;
            searchBtn.textContent = '검색';
        }
    }

    // 새로고침 처리
    async function handleRefresh() {
        try {
            refreshBtn.disabled = true;
            refreshBtn.textContent = '업데이트 중...';
            
            const response = await fetch('/api/update');
            const data = await response.json();
            
            if (data.success) {
                // 페이지 새로고침
                location.reload();
            } else {
                showAlert('업데이트 중 오류가 발생했습니다.', 'error');
            }
        } catch (error) {
            console.error('새로고침 오류:', error);
            showAlert('업데이트 중 오류가 발생했습니다.', 'error');
        } finally {
            refreshBtn.disabled = false;
            refreshBtn.textContent = '새로고침';
        }
    }

    // 공지사항 목록 업데이트
    function updateNoticesList(notices) {
        if (!noticesList) return;

        if (notices.length === 0) {
            noticesList.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">🔍</div>
                    <h3>검색 결과가 없습니다</h3>
                    <p>다른 검색어로 시도해보세요.</p>
                </div>
            `;
            return;
        }

        noticesList.innerHTML = notices.map(notice => `
            <div class="notice-item" data-id="${notice.id}">
                <div class="notice-cell number">
                    ${notice.number === '공지' ? 
                        '<span class="notice-badge">공지</span>' : 
                        notice.number
                    }
                </div>
                <div class="notice-cell title">
                    ${notice.url ? 
                        `<a href="${notice.url}" target="_blank" class="notice-link">${notice.title}</a>` :
                        notice.title
                    }
                </div>
                <div class="notice-cell author">${notice.author}</div>
                <div class="notice-cell date">${notice.date}</div>
            </div>
        `).join('');
    }

    // 공지사항 개수 업데이트
    function updateNoticeCount(count) {
        if (noticeCount) {
            noticeCount.textContent = `${count}건의 공지사항`;
        }
    }

    // 마지막 업데이트 시간 업데이트
    function updateLastUpdate() {
    const updateTimeElement = document.getElementById('updateTime');
    if (updateTimeElement) {
        const now = new Date();
        const timeString = now.getFullYear() + '-' + 
                          String(now.getMonth() + 1).padStart(2, '0') + '-' + 
                          String(now.getDate()).padStart(2, '0') + ' ' + 
                          String(now.getHours()).padStart(2, '0') + ':' + 
                          String(now.getMinutes()).padStart(2, '0');
        updateTimeElement.textContent = timeString;
    }
}


    // 알림 메시지 표시
    function showAlert(message, type = 'info') {
        // 기존 알림 제거
        const existingAlert = document.querySelector('.alert-message');
        if (existingAlert) {
            existingAlert.remove();
        }

        // 새 알림 생성
        const alertElement = document.createElement('div');
        alertElement.className = `alert-message alert-${type}`;
        alertElement.textContent = message;
        
        document.body.appendChild(alertElement);
        
        // 애니메이션을 위한 지연
        setTimeout(() => {
            alertElement.classList.add('show');
        }, 100);
        
        // 자동 제거
        setTimeout(() => {
            alertElement.classList.remove('show');
            setTimeout(() => {
                if (alertElement.parentNode) {
                    alertElement.remove();
                }
            }, 300);
        }, 5000);
    }

    // 초기 마지막 업데이트 시간 설정
    updateLastUpdate();

    // OneSignal 상태 정보가 있으면 처리
    if (typeof window.oneSignalStatus !== 'undefined') {
        console.log('OneSignal 상태:', window.oneSignalStatus);
        
        // OneSignal이 설정되지 않은 경우 버튼 상태 업데이트
        if (window.oneSignalStatus.status === 'not_configured') {
            updateNotificationButtonError();
        }
    }
});

