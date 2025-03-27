document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('imageUpload');
    const predictBtn = document.getElementById('predictBtn');
    const preview = document.getElementById('preview');
    const predictionText = document.getElementById('predictionText');
    const loader = document.querySelector('.loader');

    // Skin tone labels matching your model's output
    const SKIN_TONES = [
        "Very Light (Type I)",
        "Light (Type II)",
        "Medium (Type III)",
        "Olive (Type IV)",
        "Brown (Type V)",
        "Dark (Type VI)"
    ];

    fileInput.addEventListener('change', function(event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                preview.src = e.target.result;
                preview.style.display = "block";
                predictBtn.disabled = false;
            };
            reader.readAsDataURL(file);
        }
    });

    predictBtn.addEventListener('click', async function() {
        const file = fileInput.files[0];
        
        if (!file) {
            showMessage("Please select an image first!", "error");
            return;
        }

        showLoading();
        
        try {
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('/predict', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();
            
            if (!response.ok || !data.success) {
                throw new Error(data.error || "Prediction failed");
            }

            const confidence = (data.confidence * 100).toFixed(1);
            showMessage(`
                <strong>${SKIN_TONES[data.prediction] || "Unknown"}</strong>
                <div>Confidence: ${confidence}%</div>
            `, "success");
            
        } catch (error) {
            console.error("Error:", error);
            showMessage(error.message, "error");
        } finally {
            hideLoading();
        }
    });

    function showLoading() {
        loader.style.display = "block";
        predictBtn.disabled = true;
        predictionText.innerHTML = '<span class="loading">Analyzing...</span>';
    }

    function hideLoading() {
        loader.style.display = "none";
        predictBtn.disabled = false;
    }

    function showMessage(message, type) {
        predictionText.innerHTML = `<span class="${type}">${message}</span>`;
    }
});
