
//get the config inputs from html 


function update_config(){
    var threashold = document.getElementById('threashold').value
    var objectarea = document.getElementById('objectarea').value
    var roi        = document.getElementById('roi').value
//test if the user gave roi values if not it deafult values will be used
    if (!threashold.trim()) threashold = "140";
    if (!objectarea.trim()) objectarea = "5000";
    
    if (!roi.trim()) {
        const deafultroi = "0,0,640,480"; // Default ROI value
        console.log(`ROI is empty. Using default value: ${deafultroi}`);
        roi=deafultroi; 
    }
    
    //test if the roi values are valid 
    else{ 
    const roivalues = roi.split(',').map(Number);
    if (roivalues.length !== 4 || roivalues.some(isNaN)) {
        console.error('Invalid ROI format. Please enter values as x,y,width,height.');
        roi="0,0,640,480";
    }

 }  //this will has the correct inputs for the roi 
    const finallroivalues = roi.split(',').map(Number);

     fetch('/api/update_config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            "threashold": threashold,
            "objectarea": objectarea,
            "roi": finallroivalues ,

        })
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

// Start polling immediately when script loads
updateDetectionData();
setInterval(updateDetectionData, POLLING_INTERVAL);