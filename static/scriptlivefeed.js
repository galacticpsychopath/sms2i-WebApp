/**
 * Live Feed Detection Script
 * Fetches real-time object detection results from backend and updates the UI
 */

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

// Start polling immediately when script loads
updateDetectionData();
setInterval(updateDetectionData, POLLING_INTERVAL);