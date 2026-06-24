// ========== VIEW MODE SWITCHING ==========
function switchView(viewName) {
    document.querySelectorAll('.page-view').forEach(page => page.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(item => item.classList.remove('active'));

    const target = document.querySelector(`.nav-item[data-view="${viewName}"]`);
    if (target) target.classList.add('active');

    const viewMap = {
        live: 'live-feed-page',
        add: 'add-product-page',
        dash: 'dashboard-page'
    };
    const view = document.getElementById(viewMap[viewName] || `${viewName}-page`);
    if (view) {
        view.classList.add('active');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', function() {
        switchView(this.dataset.view);
    });
});

// ========== PRODUCT REGISTRATION ==========
const form = document.getElementById('add-product-form');
const registrationMessage = document.getElementById('registration-message');
const fileInput = document.getElementById('product-images');
const uploadLabel = document.querySelector('.file-upload-label');

if (fileInput && uploadLabel) {
    fileInput.addEventListener('change', (event) => {
        const count = event.target.files?.length || 0;
        uploadLabel.textContent = count
            ? `${count} image${count === 1 ? '' : 's'} selected`
            : 'Click to upload reference frames';
    });
}

function clearFormMessage() {
    if (registrationMessage) {
        registrationMessage.textContent = '';
        registrationMessage.className = 'form-message';
    }
}

if (form) {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const btn = e.target.querySelector('.submit-btn');
        const originalText = btn.textContent;

        btn.textContent = 'Registering...';
        btn.disabled = true;
        clearFormMessage();

        try {
            const response = await fetch('/api/add_product', {
                method: 'POST',
                body: formData
            });
            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.message || `Server returned ${response.status}`);
            }

            registrationMessage.textContent = result.message || 'Product registered successfully.';
            registrationMessage.classList.add('success');
            btn.textContent = 'Registered';

            setTimeout(() => {
                btn.textContent = originalText;
                btn.disabled = false;
                form.reset();
                if (uploadLabel) {
                    uploadLabel.textContent = 'Click to upload reference frames';
                }
                switchView('live');
                clearFormMessage();
            }, 1700);
        } catch (error) {
            console.error('Registration API Error:', error);
            registrationMessage.textContent = error.message || 'Could not register product.';
            registrationMessage.classList.add('error');
            btn.textContent = 'Try Again';
            setTimeout(() => {
                btn.textContent = originalText;
                btn.disabled = false;
                clearFormMessage();
            }, 2600);
        }
    });
}

// ========== CONFIGURATION MANAGEMENT ==========
const configInputs = [
    document.getElementById('config-threshold'),
    document.getElementById('config-roi'),
    document.getElementById('config-ioa')
].filter(Boolean);

async function updateConfig() {
    const threshold = parseFloat(document.getElementById('config-threshold')?.value) || 0.5;
    const ioa = parseFloat(document.getElementById('config-ioa')?.value) || 0.0;
    const roiInput = document.getElementById('config-roi')?.value || '[0, 0, 640, 480]';
    let roi = [0, 0, 640, 480];

    try {
        roi = JSON.parse(roiInput.replace(/'/g, '"'));
    } catch (err) {
        console.warn('Invalid ROI format. Using default values.', err);
    }

    try {
        await fetch('/api/configure', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ threshold, ioa, roi })
        });
    } catch (err) {
        console.warn('Configuration update failed:', err);
    }
}

configInputs.forEach(input => input.addEventListener('change', updateConfig));
updateConfig();

// ========== TELEMETRY POLLING ==========
async function loadStats() {
    try {
        const res = await fetch('/api/stats');
        if (!res.ok) return;
        const data = await res.json();

        const nameEl = document.getElementById('res-name');
        const refEl = document.getElementById('res-ref');
        const totalEl = document.getElementById('res-total');
        const nameBox = document.getElementById('item-box-name');
        const refBox = document.getElementById('item-box-ref');
        const imgEl = document.getElementById('res-img');
        const placeholderEl = document.getElementById('img-placeholder');
        const statDetections = document.getElementById('stat-detections');
        const statProducts = document.getElementById('stat-products');
        const statusName = document.getElementById('status-name');
        const statusBattery = document.getElementById('status-battery');
        const dashProducts = document.getElementById('dash-products');
        const dashDetections = document.getElementById('dash-detections');
        const dashStatus = document.getElementById('dash-status');
        const dashBattery = document.getElementById('dash-battery');

        if (statDetections) statDetections.textContent = data.session_total || '0';
        if (statProducts) statProducts.textContent = data.registered_products || '0';
        if (dashProducts) dashProducts.textContent = data.registered_products || '0';
        if (dashDetections) dashDetections.textContent = data.session_total || '0';
        if (dashStatus) dashStatus.textContent = data.robot_status || 'Unknown';
        if (dashBattery) dashBattery.textContent = `${Math.round(data.battery_level || 0)}%`;
        if (statusName) statusName.textContent = data.robot_status || 'Active';
        if (statusBattery) statusBattery.textContent = `${Math.round(data.battery_level || 0)}%`;

        if (data && data.detected_object) {
            const item = data.detected_object;
            if (nameEl) nameEl.textContent = item.name || '--';
            if (refEl) refEl.textContent = item.reference || '--';
            if (totalEl) totalEl.textContent = data.session_total || '0';

            if (nameBox) nameBox.classList.add('active-match');
            if (refBox) refBox.classList.add('active-match');

            if (item.image_url && imgEl && placeholderEl) {
                imgEl.src = item.image_url;
                imgEl.style.display = 'block';
                placeholderEl.style.display = 'none';
            } else if (imgEl && placeholderEl) {
                imgEl.style.display = 'none';
                placeholderEl.style.display = 'flex';
            }
        } else {
            if (nameEl) nameEl.textContent = '--';
            if (refEl) refEl.textContent = '--';
            if (totalEl) totalEl.textContent = data.session_total || '0';

            if (nameBox) nameBox.classList.remove('active-match');
            if (refBox) refBox.classList.remove('active-match');
            if (imgEl && placeholderEl) {
                imgEl.style.display = 'none';
                placeholderEl.style.display = 'flex';
            }
        }
    } catch (error) {
        console.error('Telemetry stream disconnected:', error);
    }
}

loadStats();
const statsInterval = setInterval(loadStats, 1000);
window.addEventListener('beforeunload', () => clearInterval(statsInterval));
