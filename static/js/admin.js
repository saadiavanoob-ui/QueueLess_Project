/**
 * ============================================================================
 * QueueLess - Admin Dashboard Management Logic
 * ============================================================================
 * Handles queue management: calling next token, changing status,
 * filtering table records, voice announcements, and real-time refresh.
 */

let currentServingToken = null;

document.addEventListener('DOMContentLoaded', () => {
    loadTokensTable();

    // Institution filter change
    const instFilter = document.getElementById('filterInstitution');
    if (instFilter) {
        instFilter.addEventListener('change', () => loadTokensTable());
    }

    // Status filter change
    const statusFilter = document.getElementById('filterStatus');
    if (statusFilter) {
        statusFilter.addEventListener('change', () => loadTokensTable());
    }

    // Call Next Button
    const callNextBtn = document.getElementById('adminCallNextBtn');
    if (callNextBtn) {
        callNextBtn.addEventListener('click', callNextToken);
    }

    // Re-announce Button
    const reannounceBtn = document.getElementById('adminReannounceBtn');
    if (reannounceBtn) {
        reannounceBtn.addEventListener('click', reannounceCurrentToken);
    }

    // Complete Current Button
    const completeCurrentBtn = document.getElementById('adminCompleteCurrentBtn');
    if (completeCurrentBtn) {
        completeCurrentBtn.addEventListener('click', markCurrentComplete);
    }
});

/**
 * Loads tokens from backend and renders the table rows.
 */
async function loadTokensTable() {
    const instVal = document.getElementById('filterInstitution') ? document.getElementById('filterInstitution').value : 'all';
    const statusVal = document.getElementById('filterStatus') ? document.getElementById('filterStatus').value : 'all';

    try {
        const response = await fetch(`/api/tokens?institution=${encodeURIComponent(instVal)}&status=${encodeURIComponent(statusVal)}`);
        const data = await response.json();

        if (data.success) {
            renderTableRows(data.tokens);
            updateDashboardServingCard(data.tokens);
        }
    } catch (err) {
        console.error('Failed to load tokens:', err);
    }
}

/**
 * Renders table rows in the DOM.
 */
function renderTableRows(tokens) {
    const tbody = document.getElementById('adminTokensTbody');
    if (!tbody) return;

    if (tokens.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" style="text-align:center; padding: 30px; color: var(--text-muted);">
                    <i class="fa-solid fa-inbox" style="font-size: 2rem; margin-bottom: 10px; display:block;"></i>
                    No tokens found for the selected filter.
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = tokens.map(token => {
        let badgeClass = 'badge-waiting';
        if (token.status === 'serving') badgeClass = 'badge-serving';
        if (token.status === 'completed') badgeClass = 'badge-completed';
        if (token.status === 'cancelled') badgeClass = 'badge-cancelled';

        return `
            <tr>
                <td class="token-cell">${token.token_number}</td>
                <td>
                    <strong>${token.customer_name}</strong><br>
                    <small style="color: var(--text-muted);"><i class="fa-solid fa-phone"></i> ${token.phone}</small>
                </td>
                <td>
                    <span style="font-weight: 600;">${token.institution_name}</span><br>
                    <small style="color: var(--text-muted);">${token.category}</small>
                </td>
                <td><span class="inst-badge">${token.service_name}</span></td>
                <td>
                    <span class="tracker-badge ${badgeClass}" style="padding: 4px 10px; font-size: 0.78rem;">
                        ${token.status.toUpperCase()}
                    </span>
                </td>
                <td><small style="color: var(--text-muted);">${token.created_at.split(' ')[1] || token.created_at}</small></td>
                <td>
                    <div style="display: flex; gap: 6px;">
                        ${token.status === 'waiting' ? `
                            <button class="btn btn-sm btn-primary" onclick="setTokenStatus(${token.id}, 'serving')" title="Call to Counter">
                                <i class="fa-solid fa-bullhorn"></i> Call
                            </button>
                        ` : ''}
                        ${token.status === 'serving' ? `
                            <button class="btn btn-sm btn-secondary" onclick="setTokenStatus(${token.id}, 'completed')" title="Mark Done">
                                <i class="fa-solid fa-check"></i> Complete
                            </button>
                        ` : ''}
                        ${(token.status === 'waiting' || token.status === 'serving') ? `
                            <button class="btn btn-sm btn-outline" style="color: var(--hospital-red); border-color: var(--hospital-red);" onclick="setTokenStatus(${token.id}, 'cancelled')" title="Cancel">
                                <i class="fa-solid fa-xmark"></i>
                            </button>
                        ` : ''}
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

/**
 * Updates the big "Active Serving" banner card at top of admin dashboard.
 */
function updateDashboardServingCard(tokens) {
    const serving = tokens.find(t => t.status === 'serving');
    currentServingToken = serving || null;

    const tokenDisplay = document.getElementById('currentServingTokenNumber');
    const customerDisplay = document.getElementById('currentServingCustomer');
    const counterDisplay = document.getElementById('currentServingCounterBadge');
    const completeBtn = document.getElementById('adminCompleteCurrentBtn');
    const reannounceBtn = document.getElementById('adminReannounceBtn');

    if (serving) {
        tokenDisplay.textContent = serving.token_number;
        customerDisplay.textContent = `${serving.customer_name} • ${serving.institution_name} (${serving.service_name})`;
        counterDisplay.textContent = `COUNTER 0${serving.counter_number || 1}`;
        if (completeBtn) completeBtn.style.display = 'inline-flex';
        if (reannounceBtn) reannounceBtn.style.display = 'inline-flex';
    } else {
        tokenDisplay.textContent = 'NO ACTIVE TOKEN';
        customerDisplay.textContent = 'Click "Call Next Token" to advance the waiting queue.';
        counterDisplay.textContent = 'STANDBY';
        if (completeBtn) completeBtn.style.display = 'none';
        if (reannounceBtn) reannounceBtn.style.display = 'none';
    }
}

/**
 * Calls the next waiting token.
 */
async function callNextToken() {
    const instFilter = document.getElementById('filterInstitution') ? document.getElementById('filterInstitution').value : 'all';
    const counter = document.getElementById('adminCounterSelect') ? document.getElementById('adminCounterSelect').value : 1;

    try {
        const response = await fetch('/api/tokens/call-next', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ institution: instFilter, counter: counter })
        });
        const data = await response.json();

        if (data.success && data.token) {
            showToast(`Called Token ${data.token.token_number}`, 'success');
            // Speech announcement!
            speakAnnouncement(`Token ${data.token.token_number}, ${data.token.customer_name}, please proceed to Counter ${counter}`);
            refreshStats(data.stats);
            loadTokensTable();
        } else {
            showToast(data.message || 'No waiting customers in the queue.', 'info');
        }
    } catch (err) {
        console.error('Call next error:', err);
        showToast('Error calling next token.', 'error');
    }
}

/**
 * Repeats announcement for the currently serving token.
 */
function reannounceCurrentToken() {
    if (currentServingToken) {
        speakAnnouncement(`Attention please. Token ${currentServingToken.token_number}, ${currentServingToken.customer_name}, please proceed to Counter ${currentServingToken.counter_number || 1}`);
        showToast(`Re-announced ${currentServingToken.token_number}!`, 'info');
    }
}

/**
 * Marks currently active token as completed.
 */
function markCurrentComplete() {
    if (currentServingToken) {
        setTokenStatus(currentServingToken.id, 'completed');
    }
}

/**
 * Updates status of any token.
 */
async function setTokenStatus(tokenId, newStatus) {
    const counter = document.getElementById('adminCounterSelect') ? document.getElementById('adminCounterSelect').value : 1;

    try {
        const response = await fetch(`/api/tokens/${tokenId}/status`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus, counter: counter })
        });
        const data = await response.json();

        if (data.success) {
            showToast(`Token marked as ${newStatus}.`, 'success');
            refreshStats(data.stats);
            loadTokensTable();
        } else {
            showToast(data.error || 'Failed to update token.', 'error');
        }
    } catch (err) {
        console.error('Update status error:', err);
    }
}

/**
 * Updates dashboard summary badges.
 */
function refreshStats(stats) {
    if (!stats) return;
    const totalEl = document.getElementById('statTotal');
    const servingEl = document.getElementById('statServing');
    const waitingEl = document.getElementById('statWaiting');
    const completedEl = document.getElementById('statCompleted');

    if (totalEl) totalEl.textContent = stats.total;
    if (servingEl) servingEl.textContent = stats.serving;
    if (waitingEl) waitingEl.textContent = stats.waiting;
    if (completedEl) completedEl.textContent = stats.completed;
}
