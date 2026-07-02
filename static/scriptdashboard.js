var tableBody = document.getElementById('products-table-body');
var detailsBox = document.getElementById('details-content');

// Save the original empty state markup of your details box on boot
var defaultSidebarHTML = detailsBox.innerHTML;

function showNotification(message, type = 'success') {
    const container = document.getElementById('notification-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = type === 'success' ? '✅' : '⚠️';
    toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;

    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 4000);
}

async function loadProductsTable() {
    var response = await fetch('/api/get_products');
    var productsList = await response.json();

    tableBody.innerHTML = "";

    if (productsList.length === 0) {
        tableBody.innerHTML = "<tr><td colspan='2' style='padding:10px; text-align:center;'>No products registered yet.</td></tr>";
        return;
    }

    productsList.forEach(function(product) {
        var row = document.createElement('tr');
        row.style.cursor = "pointer";
        row.innerHTML = "<td style='padding: 10px;'>" + product.reference + "</td>" +
                        "<td style='padding: 10px;'>" + product.name + "</td>";

        row.onclick = function() {
            showProductDetails(product);
        };

        tableBody.appendChild(row);
    });
}

function showProductDetails(product) {
    var nameField = document.getElementById('detail-name');
    var refField = document.getElementById('detail-ref');
    var imgElement = document.getElementById('detail-img');
    var deleteButton = document.getElementById('delete-btn');

    if (!nameField || detailsBox.innerHTML !== defaultSidebarHTML) {
        detailsBox.innerHTML = defaultSidebarHTML;
        nameField = document.getElementById('detail-name');
        refField = document.getElementById('detail-ref');
        imgElement = document.getElementById('detail-img');
        deleteButton = document.getElementById('delete-btn');
    }

    nameField.textContent = product.name;
    refField.textContent = product.reference;

    if (product.image_url) {
        imgElement.src = product.image_url;
        imgElement.style.display = "block";
    } else {
        imgElement.style.display = "none";
    }

    deleteButton.onclick = function() {
        confirmAndKeepDelete(product.reference);
    };
}

async function confirmAndKeepDelete(productRef) {
    var agree = confirm("Are you sure you want to remove product " + productRef + "?");
    if (agree === false) return;

    var response = await fetch('/api/delete_product', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reference: productRef })
    });

    if (response.ok === true) {
        detailsBox.innerHTML = defaultSidebarHTML;
        showNotification(`Product ${productRef} removed successfully.`, 'success');
        loadProductsTable();
    } else {
        showNotification("Failed to delete target product structural record.", "error");
    }
}

async function searchProducts() {
    const searchInput = document.getElementById('search-input');
    if (!searchInput) return;

    const searchQuery = searchInput.value.trim();

    var response = await fetch('/api/search_products?query=' + encodeURIComponent(searchQuery));
    var matchedList = await response.json();

    tableBody.innerHTML = "";

    // FIXED: Correctly triggers the error notification if the product doesn't exist
    if (!matchedList || matchedList.length === 0) {
        tableBody.innerHTML = "<tr><td colspan='2' style='padding:20px; text-align:center; color: var(--text-secondary);'>No products match this reference.</td></tr>";
        showNotification("Product does not exist.", "error");
        return;
    }

    showNotification(`Found ${matchedList.length} matching item(s).`, "success");

    matchedList.forEach(function(product) {
        var row = document.createElement('tr');
        row.style.cursor = "pointer";
        row.innerHTML = "<td style='padding: 10px; font-weight: bold;'>" + product.reference + "</td>" +
                        "<td style='padding: 10px;'>" + product.name + "</td>";

        row.onclick = function() {
            showProductDetails(product);
        };

        tableBody.appendChild(row);
    });
}

document.getElementById('search-input')?.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        searchProducts();
    }
});

loadProductsTable();