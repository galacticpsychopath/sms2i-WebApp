var tableBody = document.getElementById('products-table-body');
var detailsBox = document.getElementById('details-content');

// Save the original empty state markup of your details box on boot
var defaultSidebarHTML = detailsBox.innerHTML;

// ==========================================
// 1. LOAD AND RENDERS THE DATA TABLE
// ==========================================
async function loadProductsTable() {
    // Call Python to get the entire list of products
    var response = await fetch('/api/get_products');
    var productsList = await response.json();

    // Clear out the "Loading..." row
    tableBody.innerHTML = "";

    // If database is completely empty
    if (productsList.length === 0) {
        tableBody.innerHTML = "<tr><td colspan='2' style='padding:10px; text-align:center;'>No products registered yet.</td></tr>";
        return;
    }

    // Loop through every product Python sent us
    productsList.forEach(function(product) {
        // Create a new HTML table row block
        var row = document.createElement('tr');
        row.style.cursor = "pointer";
        row.innerHTML = "<td style='padding: 10px;'>" + product.reference + "</td>" +
                        "<td style='padding: 10px;'>" + product.name + "</td>";

        // When the user clicks this row, show its specific details on the right card
        row.onclick = function() {
            showProductDetails(product);
        };

        // Inject the completed row into our HTML table body
        tableBody.appendChild(row);
    });
}

// ==========================================
// 2. SHOW SELECTED PRODUCT DETAILS ON THE RIGHT
// ==========================================
function showProductDetails(product) {
    // 1. Find our targeted HTML elements
    var nameField = document.getElementById('detail-name');
    var refField = document.getElementById('detail-ref');
    var imgElement = document.getElementById('detail-img');
    var deleteButton = document.getElementById('delete-btn');

    // If the sidebar innerHTML was overridden by a past deletion message, restore original tags
    if (!nameField) {
        detailsBox.innerHTML = defaultSidebarHTML;
        nameField = document.getElementById('detail-name');
        refField = document.getElementById('detail-ref');
        imgElement = document.getElementById('detail-img');
        deleteButton = document.getElementById('delete-btn');
    }

    // 2. Inject text values straight out of the product object keys
    nameField.textContent = product.name;
    refField.textContent = product.reference;

    // 3. Handle the first image placement layout safely
    if (product.image_url) {
        imgElement.src= product.image_url;      //fix this
        imgElement.style.display = "block";       // Make the image visible on screen
    } else {
        imgElement.style.display = "none";        // Keep hidden if no image data was returned
    }

    // 4. FIX: Named the target function match accurately to stop the console crash
    deleteButton.onclick = function() {
        confirmAndKeepDelete(product.reference);
    };
}

// ==========================================
// 3. DELETE THE PRODUCT FROM THE DATABASE
// ==========================================
async function confirmAndKeepDelete(productRef) {
    // Ask the user one quick time if they are sure
    var agree = confirm("Are you sure you want to remove product " + productRef + "?");
    if (agree === false) return; // Stop right here if they hit cancel

    // Send a request to Python telling it to delete this item code
    var response = await fetch('/api/delete_product', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reference: productRef })
    });

    if (response.ok === true) {
        // Reset the details sidebar text block cleanly
        detailsBox.innerHTML = "<p style='color: green; font-weight: bold; padding: 20px 0;'>Product deleted successfully!</p>";
        
        // Instantly reload the table list so it disappears from the list view
        loadProductsTable();
    } else {
        alert("Failed to delete product.");
    }
}

// Start the page by executing the data pull on script initialization
loadProductsTable();