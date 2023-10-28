window.onload = function() {
    var formContainer = document.querySelector('.form-container');
    var screenHeight = window.innerHeight;
    var screenWidth = window.innerWidth;
    var screenRatio = screenWidth / screenHeight;

    // Adjust size, shape, padding, and top position based on screen ratio
    if (screenRatio > 1.6) {
        // Wide screens (PCs, laptops)
        formContainer.style.width = '50%';
        formContainer.style.height = '60%';
        formContainer.style.padding = '20px';
        formContainer.style.top = '10%';
    } else if (screenRatio > 1) {
        // Landscape orientation (tablets in landscape mode)
        formContainer.style.width = '70%';
        formContainer.style.height = '70%';
        formContainer.style.padding = '10px';
        formContainer.style.top = '10%';
    } else if (screenRatio > 0.75) {
        // Portrait orientation (phones in portrait mode, tablets in portrait mode)
        formContainer.style.width = '90%';
        formContainer.style.height = 'auto';
        formContainer.style.padding = '5%';
        formContainer.style.top = '10%';
    } else {
        // Very tall screens (phones in portrait mode)
        formContainer.style.width = '90%';
        formContainer.style.height = 'auto';
        formContainer.style.padding = '5%';
        formContainer.style.top = '10%';
    }
}
