// ========== VIEW ENGINE ENGINE MANAGMENT ==========
function switchView(viewName) {
    document.querySelectorAll('.page-view').forEach(page => page.classList.remove('active'));
    
    switch(viewName) {
        case 'live':
            document.getElementById('live-feed-page').classList.add('active');
            break;
        case 'add':
            document.getElementById('add-product-page').classList.add('active');
            break;
        case 'dash':
            document.getElementById('dashboard-page').classList.add('active');
            break;
        default:
            console.warn(`Target routing view not handled: ${viewName}`);
            return;
    }

    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.view === viewName) item.classList.add('active');
    });
}

document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', function() { switchView(this.dataset.view); });
});

// ========== API INTEGRATION: PRODUCT REGISTRATION FORM ==========
const form = document.getElementById('add-product-form');
if (form) {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const btn = e.target.querySelector('.submit-btn');
        const originalText = btn.textContent;
        
        btn.textContent = 'Processing Pipeline...';
        btn.disabled = true;

        try {
            // API ENDPOINT MATCH: Maps to backend route managing registration upload arrays
            const response = await fetch('/api/add_product', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) throw new Error(`Server Pipeline Failure: ${response.status}`);
            const result = await response.json();
            
            btn.textContent = '✓ Registered into Registry';
            btn.style.background = 'var(--success)';
            
            setTimeout(() => {
                btn.textContent = originalText;
                btn.style.background = '';
                btn.disabled = false;
                e.target.reset();
                switchView('live');
            }, 1800);
        } catch (error) {
            console.error('Registration API Error:', error);
            btn.textContent = '✕ Pipeline Rejection';
            btn.style.background = 'var(--accent)';
            setTimeout(() => {
                btn.textContent = originalText;
                btn.style.background = '';
                btn.disabled = false;
            }, 2000);
        }
    });
}

// ========== API INTEGRATION: RUNTIME STATISTICS REALTIME POLLING ==========
const statsInterval = setInterval(async () => {
    try {
        // API ENDPOINT MATCH: Fetch updates from your tracking session pipeline state
        const res = await fetch('/api/stats');
        if (!res.ok) return;

        const data = await res.json();

        if (data && data.detected_object) {
            const item = data.detected_object;
            
            const nameEl = document.getElementById('res-name');
            const refEl = document.getElementById('res-ref');
            const totalEl = document.getElementById('res-total');
            const nameBox = document.getElementById('item-box-name');
            const refBox = document.getElementById('item-box-ref');

            // Dynamic text values insertion
            if (nameEl) nameEl.textContent = item.name || '--';
            if (refEl) refEl.textContent = item.reference || '--';
            if (totalEl) totalEl.textContent = data.session_total || '0';

            // High-visibility border highlight when values update successfully
            if (item.name && nameBox) nameBox.classList.add('active-match');
            if (item.reference && refBox) refBox.classList.add('active-match');
            
            // Dynamic Image Source switch logic
            if (item.image_url) {
                const imgEl = document.getElementById('res-img');
                const placeholderEl = document.getElementById('img-placeholder');
                
                if (imgEl && placeholderEl) {
                    imgEl.src = item.image_url;
                    imgEl.style.display = 'block';
                    placeholderEl.style.display = 'none';
                }
            }
        } else {
            // Return interface to looking/scanning baseline state if no target is actively hit
            document.getElementById('item-box-name').classList.remove('active-match');
            document.getElementById('item-box-ref').classList.remove('active-match');
        }
    } catch (error) {
        console.error('Telemetry stream disconnected:', error);
    }
}, 1000);

window.addEventListener('beforeunload', () => clearInterval(statsInterval));