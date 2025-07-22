// 공통 JavaScript 함수들

// 숫자 포맷팅 함수 (천 단위 콤마)
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// 날짜 포맷팅 함수
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// 시간 포맷팅 함수
function formatTime(timeString) {
    if (!timeString) return '시간 미정';
    return timeString;
}

// 모달 닫기 함수
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

// 모달 열기 함수
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
    }
}

// API 호출 함수
async function apiCall(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API 호출 중 오류 발생:', error);
        throw error;
    }
}

// 성공 메시지 표시
function showSuccess(message) {
    // 간단한 토스트 메시지 구현
    const toast = document.createElement('div');
    toast.className = 'toast success';
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #4CAF50;
        color: white;
        padding: 12px 20px;
        border-radius: 4px;
        z-index: 3000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// 에러 메시지 표시
function showError(message) {
    const toast = document.createElement('div');
    toast.className = 'toast error';
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #f44336;
        color: white;
        padding: 12px 20px;
        border-radius: 4px;
        z-index: 3000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// CSS 애니메이션 추가
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style); 

// 일정 추가/수정 폼 제출 이벤트 (여러 날짜 지원)
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('scheduleForm');
    if (form) {
        form.onsubmit = async function(e) {
            e.preventDefault();
            const dates = selectedDates;
            if (!dates.length) {
                showError('날짜를 하나 이상 선택하세요.');
                return;
            }
            const time = document.getElementById('scheduleTime').value;
            const center = document.getElementById('scheduleCenter').value;
            const people_count = parseInt(document.getElementById('schedulePeopleCount').value) || 1;
            const amount = parseInt(document.getElementById('scheduleAmount').value) || 0;
            try {
                const res = await apiCall('/api/schedule/bulk', {
                    method: 'POST',
                    body: JSON.stringify({ dates, time, center, people_count, amount })
                });
                if (res.success) {
                    showSuccess('일정이 등록되었습니다.');
                    window.location.reload();
                } else {
                    showError(res.error || '일정 등록 실패');
                }
            } catch (err) {
                showError('서버 오류: ' + err.message);
            }
        };
    }
}); 