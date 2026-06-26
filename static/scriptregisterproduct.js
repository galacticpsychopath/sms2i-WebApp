// read data from html 
var myForm = document.getElementById('add-product-form');
var myLabel = document.querySelector('.file-upload-label');
var myMessageBox = document.getElementById('registration-message');
var myFileInput = document.getElementById('product-images');

// status for when user selects a file 
myFileInput.onchange = function() {
    myLabel.textContent = "Picture is ready!";
};

// when user submit + sending the data to the backed server 
myForm.onsubmit = async function(event) {
    // Stop the page from refreshing and blinking
    event.preventDefault(); 

    // Find the button and change its text
    var submitButton = myForm.querySelector('.submit-btn');
    submitButton.textContent = "Saving...";

    // Collect the Name, Code, and Picture from the form boxes
    var allMyFormData = new FormData(myForm);

    // Send everything over the internet pipeline to Python
    var response = await fetch('/api/register_product', {
        method: 'POST',
        body: allMyFormData
    });

    // Read what the Python server says back to us
    var serverResult = await response.json();

    // Check if the server says everything went good (ok)
    if (response.ok === true) {
        myMessageBox.textContent = "Saved successfully!";
        myMessageBox.style.color = "green";
        submitButton.textContent = "Done!";
        myForm.reset(); // Clear the text boxes
    } else {
        myMessageBox.textContent = serverResult.message || "Error saving product.";
        myMessageBox.style.color = "red";
        submitButton.textContent = "Try Again";
    }
};