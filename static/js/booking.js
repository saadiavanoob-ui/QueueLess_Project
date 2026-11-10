/**
 * ============================================================================
 * QueueLess - Dynamic Token Booking JavaScript Logic
 * ============================================================================
 * Cascading institution -> branch -> services, dynamic wait preview,
 * real client-side QR Code rendering, and receipt modal.
 */

let currentInstitutionData = null;
let currentBranches = [];
let currentServices = [];
let qrCodeInstance = null;

document.addEventListener('DOMContentLoaded', async () => {
    const instSelect = document.getElementById('institutionSelect');
    if (instSelect) {
        // Load initial institution
        await loadInstitutionDetails(instSelect.value);
    }

    const bookingForm = document.getElementById('tokenBookingForm');
    if (bookingForm) {
        bookingForm.addEventListener('submit', handleFormSubmit);
    }
});

async function onInstitutionChange(instId) {
    await loadInstitutionDetails(instId);
}

async function loadInstitutionDetails(instId) {
    if (!instId) return;
    try {
        const response = await fetch(`/api/institutions/${instId}`);
        const data = await response.json();
        if (data.success && data.institution) {
            currentInstitutionData = data.institution;
            currentBranches = data.institution.branches || [];
            currentServices = data.institution.services || [];
            populateBranches(currentBranches);
            populateServices(currentServices);
        }
    } catch (err) {
        console.error('Failed to load institution details:', err);
    }
}

function populateBranches(branches) {
    const branchSelect = document.getElementById('branchSelect');
    if (!branchSelect) return;

    branchSelect.innerHTML = '';
    if (branches.length === 0) {
        branchSelect.innerHTML = '<option value="">No branches available</option>';
        return;
    }

    branches.forEach((b, idx) => {
        const opt = document.createElement('option');
        opt.value = b.id;
        opt.textContent = `${b.branch_name} (${b.location})`;
        opt.dataset.hours = `${b.opening_time} - ${b.closing_time}`;
        opt.dataset.counters = b.open_counters || 3;
        if (idx === 0) opt.selected = true;
        branchSelect.appendChild(opt);
    });

    onBranchChange(branchSelect);
}

function onBranchChange(selectEl) {
    const selectedOpt = selectEl.options[selectEl.selectedIndex];
    const infoBar = document.getElementById('branchInfoBar');
    const timingText = document.getElementById('branchTimingText');
    const countersText = document.getElementById('branchCountersText');

    if (selectedOpt && infoBar) {
        infoBar.style.display = 'flex';
        if (timingText) timingText.innerHTML = `<i class="fa-solid fa-clock"></i> ${selectedOpt.dataset.hours || '09:00 AM - 05:00 PM'}`;
        if (countersText) countersText.innerHTML = `<i class="fa-solid fa-desktop"></i> ${selectedOpt.dataset.counters || 3} Active Counters`;
    }
}

function populateServices(services) {
    const container = document.getElementById('servicesContainer');
    if (!container) return;

    container.innerHTML = '';
    if (services.length === 0) {
        container.innerHTML = '<p style="color: var(--text-muted); padding: 10px;">No active services found.</p>';
        return;
    }

    services.forEach((s, idx) => {
        const label = document.createElement('label');
        label.className = `service-radio-card ${idx === 0 ? 'selected' : ''}`;
        label.innerHTML = `
            <input type="radio" name="service_id" value="${s.id}" ${idx === 0 ? 'checked' : ''} onchange="onServiceRadioChange(this)">
            <div style="flex: 1;">
                <div style="font-weight: 700; color: var(--dark-green); font-size: 0.96rem;">${s.service_name}</div>
                <small style="color: var(--text-muted); display: block; margin-top: 2px;">
                    <i class="fa-solid fa-stopwatch" style="color: #059669;"></i> ~${s.avg_duration_mins || 10} mins avg per person
                </small>
            </div>
            <span class="inst-badge" style="font-size: 0.75rem;">${s.prefix}</span>
        `;
        container.appendChild(label);
    });
}

function onServiceRadioChange(radio) {
    document.querySelectorAll('.service-radio-card').forEach(c => c.classList.remove('selected'));
    if (radio.checked) {
        radio.closest('.service-radio-card').classList.add('selected');
    }
}

function toggleAppointmentFields(show) {
    const fields = document.getElementById('appointmentFields');
    if (fields) {
        fields.style.display = show ? 'block' : 'none';
    }

    // Toggle pill active class
    document.querySelectorAll('.type-pill').forEach(pill => {
        const input = pill.querySelector('input');
        if (input.checked) {
            pill.classList.add('selected');
        } else {
            pill.classList.remove('selected');
        }
    });
}

async function handleFormSubmit(e) {
    e.preventDefault();

    const submitBtn = document.getElementById('generateTokenBtn');
    const origText = submitBtn.innerHTML;

    const instId = document.getElementById('institutionSelect').value;
    const branchId = document.getElementById('branchSelect').value;
    const serviceRadio = document.querySelector('input[name="service_id"]:checked');
    const serviceId = serviceRadio ? serviceRadio.value : '';
    const customerName = document.getElementById('customerName').value.trim();
    const phone = document.getElementById('customerPhone').value.trim();
    const priority = document.getElementById('priorityCategorySelect').value;
    
    const tokenTypeRadio = document.querySelector('input[name="token_type"]:checked');
    const tokenType = tokenTypeRadio ? tokenTypeRadio.value : 'instant';
    const apptDate = tokenType === 'appointment' ? document.getElementById('appointmentDate').value : null;
    const apptSlot = tokenType === 'appointment' ? document.getElementById('appointmentSlot').value : null;

    if (!instId || !branchId || !serviceId) {
        showToast('Please select Institution, Branch, and Service.', 'error');
        return;
    }
    if (!customerName) {
        showToast('Please enter your full name.', 'error');
        return;
    }
    if (!phone || phone.length < 10) {
        showToast('Please enter a valid 10-digit mobile number.', 'error');
        return;
    }

    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Generating QR Token...';

    try {
        const payload = {
            institution_id: instId,
            branch_id: branchId,
            service_id: serviceId,
            customer_name: customerName,
            phone: phone,
            priority: priority,
            token_type: tokenType,
            appointment_date: apptDate,
            appointment_slot: apptSlot
        };

        const res = await fetch('/api/tokens/book', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await res.json();
        if (result.success && result.token) {
            showToast(`🎉 Token ${result.token.token_number} generated successfully!`, 'success');
            openConfirmationModal(result.token);
            document.getElementById('tokenBookingForm').reset();
            if (currentInstitutionData) {
                populateBranches(currentInstitutionData.branches || []);
                populateServices(currentInstitutionData.services || []);
            }
        } else {
            showToast(result.error || 'Failed to generate token.', 'error');
        }
    } catch (err) {
        console.error('Error generating token:', err);
        showToast('Server communication error. Please try again.', 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = origText;
    }
}

function openConfirmationModal(token) {
    document.getElementById('receiptTokenNumber').textContent = token.token_number;
    document.getElementById('receiptCustomerName').textContent = token.customer_name;
    document.getElementById('receiptInstitution').textContent = token.institution_name;
    document.getElementById('receiptBranch').textContent = token.branch_name;
    document.getElementById('receiptService').textContent = token.service_name;
    document.getElementById('receiptAhead').textContent = `${token.people_ahead} person(s)`;
    document.getElementById('receiptWaitTime').textContent = token.estimated_wait_time_minutes > 0 ? `~${token.estimated_wait_time_minutes} mins` : 'Immediate';
    document.getElementById('receiptVerificationCode').textContent = token.verification_code || 'QL-PASS';

    // Priority badge
    const priorityPill = document.getElementById('receiptPriorityPill');
    if (priorityPill) {
        priorityPill.textContent = (token.priority || 'regular').toUpperCase() + ' PRIORITY';
    }

    // Set Track button URL
    const trackBtn = document.getElementById('receiptTrackBtn');
    if (trackBtn) {
        trackBtn.href = `/track?token=${encodeURIComponent(token.token_number)}`;
    }

    // Generate Real QR Code
    const qrContainer = document.getElementById('receiptQrCodeCanvas');
    if (qrContainer) {
        qrContainer.innerHTML = '';
        const qrPayload = JSON.stringify({
            app: "QueueLess",
            token: token.token_number,
            verify: token.verification_code,
            branch: token.branch_id,
            url: window.location.origin + `/track?token=${token.token_number}`
        });

        if (typeof QRCode !== 'undefined') {
            qrCodeInstance = new QRCode(qrContainer, {
                text: qrPayload,
                width: 140,
                height: 140,
                colorDark: "#064e3b",
                colorLight: "#ffffff"
            });
        }
    }

    const modal = document.getElementById('confirmationModal');
    if (modal) {
        modal.classList.add('show');
    }
}

function closeConfirmationModal() {
    const modal = document.getElementById('confirmationModal');
    if (modal) {
        modal.classList.remove('show');
    }
}
