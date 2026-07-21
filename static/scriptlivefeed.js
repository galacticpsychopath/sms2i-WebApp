
//get the config inputs from html 

const searchInput = document.getElementById('search-input');

if (searchInput) {
    searchInput.addEventListener('input', (e) => {
        const searchQuery = e.target.value.trim();
        
        
        fetch(`/api/search_products?query=${encodeURIComponent(searchQuery)}`)
            .then(response => response.json())
            .then(data => {
                const tableBody = document.getElementById('products-table-body');
                if (!tableBody) return;
                
                
                tableBody.innerHTML = '';
                
                if (data.length === 0) {
                    tableBody.innerHTML = `<tr><td colspan="2" style="text-align: center; padding: 20px; color: var(--text-secondary);">No products match this reference.</td></tr>`;
                    return;
                }
                
                
                data.forEach(product => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${product.reference}</td>
                        <td>${product.name}</td>
                    `;
                    
                    
                    row.addEventListener('click', () => {
                        if (typeof displayProductDetails === 'function') {
                            displayProductDetails(product);
                        }
                    });
                    
                    tableBody.appendChild(row);
                });
            })
            .catch(err => console.error('Error during live product search query:', err));
    });
}



// Polling interval in milliseconds
const POLLING_INTERVAL = 1000; // 1 second

/**
 * Fetch current detection data from backend and update UI elements
 */
function updateDetectionData() {
    fetch('/api/current_detection')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Safely extract values from backend response
            const productName = data.name || "No object detected";
            const productReference = data.reference || "--";
            const itemCount = data.count || 0;
            const imageUrl = data.image_url || "";

            // Update product name element
            const nameElement = document.getElementById('res-name');
            if (nameElement) {
                nameElement.textContent = productName;
            }

            // Update reference code element
            const refElement = document.getElementById('res-ref');
            if (refElement) {
                refElement.textContent = productReference;
            }

            // Update item count element
            const countElement = document.getElementById('res-total');
            if (countElement) {
                countElement.textContent = itemCount;
            }

            // Handle image display logic
            const imageElement = document.getElementById('res-img');
            const placeholderElement = document.getElementById('img-placeholder');

            if (imageElement && placeholderElement) {
                if (imageUrl && imageUrl.trim() !== "") {
                    // Image URL exists - show the image and hide placeholder
                    imageElement.src = imageUrl;
                    imageElement.style.display = 'block';
                    if (placeholderElement) {
                        placeholderElement.style.display = 'none';
                    }
                } else {
                    // No image URL - hide image and show placeholder
                    imageElement.style.display = 'none';
                    imageElement.src = ""; // Clear the src to prevent errors
                    if (placeholderElement) {
                        placeholderElement.style.display = 'flex';
                    }
                }
            }
        })
        .catch(error => {
            console.error('Error fetching detection data:', error);
        });
}
function check_product() {
    const btn = document.getElementById('check-product-btn');
    if (btn) {
        btn.disabled = true;
        btn.textContent = 'Inspecting...';
    }

    fetch('/api/check_product', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => {
        // The backend returns a 200 on success and a 400 on verification failures
        return response.json().then(data => ({
            status: response.status,
            body: data
        }));
    })
    .then(res => {
        if (res.status === 200) {
            console.log("Success:", res.body.result);
            alert(`✅ ${res.body.result}`);
            // TODO: Update your UI to show a green "VALID" state
        } else {
            console.warn("Product check failed:", res.body);
            
            // Extract individual filter breakdowns from your backend response
            const exp = res.body.expiration_check ? res.body.expiration_check[1] : 'Unknown';
            const exist = res.body.existence_check ? res.body.existence_check[1] : 'Unknown';
            const form = res.body.form_check ? res.body.form_check[1] : 'Unknown';
            
            alert(`❌ Check Failed!\n• Expiration: ${exp}\n• Existence: ${exist}\n• Form: ${form}`);
            // TODO: Highlight the exact failing step in red on your UI dashboard
        }
    })
    .catch(error => {
        console.error('Error during product checking execution:', error);
        alert('Could not complete product inspection. Check backend console.');
    })
    .finally(() => {
        if (btn) {
            btn.disabled = false;
            btn.textContent = 'Check Product';
        }
    });
}
// Start polling immediately when script loads
updateDetectionData();
setInterval(updateDetectionData, POLLING_INTERVAL);