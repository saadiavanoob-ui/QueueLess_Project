/**
 * ============================================================================
 * QueueLess - Live Real-Time Token Tracking JavaScript Logic
 * ============================================================================
 * Features:
 * - Real-time auto-polling (every 4 seconds)
 * - Airport chime & Web Speech voice announcement on turn
 * - Dynamic QR code rendering for counter arrival verification
 * - Dynamic status: Waiting, Almost Your Turn (<=2), Called, Serving, Completed, Cancelled
 * - Customer token cancellation with confirmation
 * - 5-star feedback rating modal
 * - Browser Web Notifications API
 */

let activeTrackingToken = null;
let pollInterval = null;
let previousStatus = null;
let trackerQrInstance = null;
let currentRating = 5;

document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.getElementById('trackSearchForm');
    const tokenInput = document.getElementById('trackTokenInput');

    if (searchForm) {
        searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const tokenNum = tokenInput.value.trim().toUpperCase();
            if (tokenNum) {
                fetchTokenStatus(tokenNum);
            }
        });
    }

    // Auto-search if token query parameter is present in URL
    const urlParams = new URLSearchParams(window.location.search);
    const tokenFromUrl = urlParams.get('token');
    if (tokenFromUrl) {
        if (tokenInput) tokenInput.value = tokenFromUrl;
        fetchTokenStatus(tokenFromUrl);
    }
});

async function fetchTokenStatus(tokenNumber) {
    const trackerContainer = document.getElementById('trackerResultsContainer');
    const notFoundBox = document.getElementById('trackerNotFound');
    const welcomeBox = document.getElementById('trackerWelcome');

    try {
        const response = await fetch(`/api/tokens/track/${encodeURIComponent(tokenNumber.trim().toUpperCase())}`);
        const data = await response.json();

        if (data.success && data.token) {
            activeTrackingToken = data.token.token_number;
            if (welcomeBox) welcomeBox.style.display = 'none';
            if (notFoundBox) notFoundBox.style.display = 'none';
            if (trackerContainer) trackerContainer.style.display = 'block';

            renderTokenDetails(data.token);

            // Start auto polling if waiting or serving
            startAutoPolling(tokenNumber, data.token.status);
        } else {
            if (welcomeBox) welcomeBox.style.display = 'none';
            if (trackerContainer) trackerContainer.style.display = 'none';
            if (notFoundBox) {
                notFoundBox.style.display = 'block';
                document.getElementById('notFoundMsg').textContent = 
                    data.error || `No record found for "${tokenNumber}". Please verify your token number.`;
            }
            stopAutoPolling();
        }
    } catch (err) {
        console.error('Error fetching token:', err);
        showToast('Unable to reach server. Please check your connection.', 'error');
    }
}

function renderTokenDetails(token) {
    // 1. Text labels
    document.getElementById('dispTokenNumber').textContent = token.token_number;
    document.getElementById('dispCustomerName').textContent = token.customer_name;
    document.getElementById('dispInstitution').textContent = token.institution_name;
    document.getElementById('dispBranchBadge').textContent = token.branch_name;
    document.getElementById('dispService').textContent = token.service_name;
    document.getElementById('dispCurrentServing').textContent = token.current_serving || 'None';
    document.getElementById('dispPeopleAhead').textContent = token.people_ahead;
    document.getElementById('dispVerifyCode').textContent = token.verification_code || 'QL-PASS';
    
    // Priority badge
    const pBadge = document.getElementById('dispPriorityBadge');
    if (pBadge) {
        pBadge.textContent = (token.priority || 'regular').toUpperCase() + ' PRIORITY';
    }

    // Checkin badge
    const cBadge = document.getElementById('dispCheckinBadge');
    if (cBadge) {
        if (token.checkin_status === 'checked_in') {
            cBadge.style.display = 'inline-flex';
            cBadge.innerHTML = '<i class="fa-solid fa-circle-check" style="color: #10b981;"></i> Arrival Confirmed';
        } else {
            cBadge.style.display = 'inline-flex';
            cBadge.innerHTML = '<i class="fa-solid fa-clock"></i> Check-in Pending';
            cBadge.style.background = '#fef3c7';
            cBadge.style.color = '#b45309';
        }
    }

    // Active counters count
    const countersCountEl = document.getElementById('dispCountersCount');
    if (countersCountEl) {
        countersCountEl.textContent = `(Calculated across ${token.active_counters || 1} active counter(s))`;
    }

    // Estimated wait time
    const waitElement = document.getElementById('dispWaitTime');
    if (token.status === 'serving') {
        waitElement.textContent = 'At Counter';
    } else if (token.status === 'completed') {
        waitElement.textContent = 'Completed';
    } else if (token.status === 'cancelled') {
        waitElement.textContent = 'Cancelled';
    } else if (token.status === 'skipped') {
        waitElement.textContent = 'Skipped';
    } else {
        waitElement.textContent = token.estimated_wait_time_minutes > 0 ? `~${token.estimated_wait_time_minutes} mins` : 'Immediate';
    }

    // 2. Status Badge & Stepper
    const badge = document.getElementById('dispStatusBadge');
    badge.className = 'tracker-badge';
    badge.classList.add(`badge-${token.status}`);

    let statusText = (token.display_status || token.status).toUpperCase();
    if (token.status === 'serving') {
        statusText = `⚡ NOW SERVING (COUNTER ${token.serving_counter || 1})`;
    } else if (token.status === 'waiting' && token.people_ahead <= 2 && token.people_ahead > 0) {
        statusText = `🔔 ALMOST YOUR TURN (${token.people_ahead} AHEAD)`;
        badge.classList.add('badge-almost');
    }
    badge.innerHTML = `<i class="fa-solid fa-circle-dot"></i> ${statusText}`;

    // Cancel Button visibility (Only available if waiting or almost turn)
    const cancelBtn = document.getElementById('btnCancelToken');
    if (cancelBtn) {
        cancelBtn.style.display = (token.status === 'waiting' || token.status === 'called') ? 'inline-flex' : 'none';
    }

    // Feedback Button (Only if completed)
    const feedbackBtn = document.getElementById('btnFeedbackModal');
    if (feedbackBtn) {
        feedbackBtn.style.display = (token.status === 'completed') ? 'inline-flex' : 'none';
    }

    // 3. Audio & Voice Alerts on status transition to 'serving'
    if (previousStatus && previousStatus !== 'serving' && token.status === 'serving') {
        if (window.I18n) {
            window.I18n.announceTokenVoice(token.token_number, token.serving_counter || 1, token.customer_name);
        }
        showToast(`🎉 Attention! Token ${token.token_number} is now being served at Counter ${token.serving_counter || 1}!`, 'success');
        sendBrowserNotification(
            `Token ${token.token_number} Called!`,
            `Please proceed to Counter ${token.serving_counter || 1} at ${token.institution_name}.`
        );
    }
    previousStatus = token.status;

    // 4. Update Stepper Nodes
    updateStepper(token.status);

    // 5. Render Dynamic Arrival QR Code
    const qrContainer = document.getElementById('trackerQrContainer');
    if (qrContainer && typeof QRCode !== 'undefined') {
        qrContainer.innerHTML = '';
        const qrPayload = JSON.stringify({
            app: "QueueLess",
            token: token.token_number,
            verify: token.verification_code,
            branch: token.branch_id
        });
        trackerQrInstance = new QRCode(qrContainer, {
            text: qrPayload,
            width: 84,
            height: 84,
            colorDark: "#064e3b",
            colorLight: "#ffffff"
        });
    }
}

function updateStepper(status) {
    const step1 = document.getElementById('stepBooked');
    const step2 = document.getElementById('stepWaiting');
    const step3 = document.getElementById('stepServing');
    const step4 = document.getElementById('stepCompleted');

    [step1, step2, step3, step4].forEach(el => {
        if (el) el.classList.remove('active', 'completed');
    });

    if (status === 'waiting') {
        step1.classList.add('completed');
        step2.classList.add('active');
    } else if (status === 'serving' || status === 'called') {
        step1.classList.add('completed');
        step2.classList.add('completed');
        step3.classList.add('active');
    } else if (status === 'completed') {
        step1.classList.add('completed');
        step2.classList.add('completed');
        step3.classList.add('completed');
        step4.classList.add('active');
    } else if (status === 'cancelled') {
        step1.classList.add('completed');
        // Marked cancelled
    }
}

function startAutoPolling(tokenNumber, currentStatus) {
    stopAutoPolling();
    // Do not auto-poll if terminal status
    if (currentStatus === 'completed' || currentStatus === 'cancelled') return;

    pollInterval = setInterval(() => {
        fetchTokenStatus(tokenNumber);
    }, 4000);
}

function stopAutoPolling() {
    if (pollInterval) {
        clearInterval(pollInterval);
        pollInterval = null;
    }
}

// Token Cancellation Action (Feature #4)
async function promptCancelToken() {
    if (!activeTrackingToken) return;
    const confirmed = confirm(`Are you sure you want to cancel token ${activeTrackingToken}? This cannot be undone.`);
    if (!confirmed) return;

    try {
        const res = await fetch(`/api/tokens/${encodeURIComponent(activeTrackingToken)}/cancel`, {
            method: 'POST'
        });
        const data = await res.json();
        if (data.success) {
            showToast(`Token ${activeTrackingToken} has been cancelled.`, 'info');
            fetchTokenStatus(activeTrackingToken);
        } else {
            showToast(data.error || 'Failed to cancel token.', 'error');
        }
    } catch (err) {
        console.error('Cancellation error:', err);
        showToast('Error communicating with server.', 'error');
    }
}

// Browser Web Notifications (Feature #10)
function requestNotificationPermission() {
    if (!('Notification' in window)) {
        showToast('Web Notifications not supported on this browser.', 'info');
        return;
    }
    Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
            showToast('Turn notifications enabled! You will be alerted when called.', 'success');
            const btn = document.getElementById('enableNotificationsBtn');
            if (btn) btn.style.display = 'none';
        } else {
            showToast('Notification permission denied.', 'info');
        }
    });
}

function sendBrowserNotification(title, body) {
    if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(title, {
            body: body,
            icon: '/static/images/logo.svg'
        });
    }
}

// Feedback Modal Actions (Feature #5)
function openFeedbackModal() {
    const modal = document.getElementById('feedbackModal');
    if (modal) modal.classList.add('show');
}

function closeFeedbackModal() {
    const modal = document.getElementById('feedbackModal');
    if (modal) modal.classList.remove('show');
}

function setRating(rating) {
    currentRating = rating;
    document.getElementById('selectedRatingVal').value = rating;
    const stars = document.querySelectorAll('#starRatingGroup .star-btn');
    stars.forEach(star => {
        const val = parseInt(star.getAttribute('data-rating'));
        if (val <= rating) {
            star.classList.add('active');
        } else {
            star.classList.remove('active');
        }
    });
}

async function submitCustomerFeedback(e) {
    e.preventDefault();
    if (!activeTrackingToken) return;

    const rating = document.getElementById('selectedRatingVal').value;
    const comment = document.getElementById('feedbackComment').value;
    const customerName = document.getElementById('dispCustomerName').textContent;

    try {
        const res = await fetch('/api/feedback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                token_number: activeTrackingToken,
                customer_name: customerName,
                rating: parseInt(rating),
                comment: comment
            })
        });
        const data = await res.json();
        if (data.success) {
            showToast('Thank you! Your rating has been submitted.', 'success');
            closeFeedbackModal();
            const btn = document.getElementById('btnFeedbackModal');
            if (btn) btn.disabled = true;
        }
    } catch (err) {
        console.error('Feedback submit error:', err);
    }
}
