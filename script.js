const imageInput = document.getElementById("imageInput");
const imagePreview = document.getElementById("imagePreview");
const imagePreviewContainer = document.getElementById("imagePreviewContainer");

const generateButton = document.getElementById("generateButton");
const status = document.getElementById("status");

const resultArea = document.getElementById("resultArea");
const resultPlaceholder = document.getElementById("resultPlaceholder");
const downloadButton = document.getElementById("downloadButton");


// ===============================
// IMAGE SELECT
// ===============================

imageInput.addEventListener("change", function () {

    const file = this.files[0];

    if (!file) {
        generateButton.disabled = true;
        imagePreviewContainer.hidden = true;
        return;
    }

    // Check image
    if (!file.type.startsWith("image/")) {
        status.textContent = "Please select a JPG, JPEG or PNG image.";
        generateButton.disabled = true;
        return;
    }

    // Show preview
    const imageURL = URL.createObjectURL(file);

    imagePreview.src = imageURL;

    imagePreviewContainer.hidden = false;

    // Enable button
    generateButton.disabled = false;

    status.textContent = "Image selected. Ready to generate.";
});


// ===============================
// GENERATE RELIEF
// ===============================

generateButton.addEventListener("click", async function () {

    const file = imageInput.files[0];

    if (!file) {
        status.textContent = "Please select an image first.";
        return;
    }

    generateButton.disabled = true;

    status.textContent = "Generating 3D Relief... Please wait.";

    resultPlaceholder.innerHTML = `
        <div class="result-icon">⏳</div>
        <p>AI is processing your image...</p>
    `;

    try {

        const formData = new FormData();

        formData.append("image", file);

        formData.append(
            "width",
            document.getElementById("modelWidth").value
        );

        formData.append(
            "height",
            document.getElementById("modelHeight").value
        );

        formData.append(
            "depth",
            document.getElementById("reliefDepth").value
        );

        formData.append(
            "base",
            document.getElementById("baseThickness").value
        );

        formData.append(
            "detail",
            document.getElementById("detailLevel").value
        );

        formData.append(
            "background",
            document.getElementById("backgroundMode").value
        );


        // Send to Python Flask
        const response = await fetch("/generate", {
            method: "POST",
            body: formData
        });


        const data = await response.json();


        if (!response.ok) {
            throw new Error(data.error || "Generation failed.");
        }


        // Success
        status.textContent = "3D Relief generated successfully!";

        resultPlaceholder.innerHTML = `
            <div class="result-icon">✓</div>
            <p>3D Relief STL is ready.</p>
        `;


        // Download button
        downloadButton.href = data.download_url;
        downloadButton.download = "cnc-relief.stl";
        downloadButton.hidden = false;


    } catch (error) {

        console.error(error);

        status.textContent = "Error: " + error.message;

        resultPlaceholder.innerHTML = `
            <div class="result-icon">!</div>
            <p>Generation failed.</p>
        `;

    }


    generateButton.disabled = false;

});