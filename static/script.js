document.getElementById("imageUpload").addEventListener("change", function(event) {
    const file = event.target.files[0];
    const preview = document.getElementById("preview");
    const predictBtn = document.getElementById("predictBtn");
    
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

document.getElementById("predictBtn").addEventListener("click", async function() {
    const fileInput = document.getElementById("imageUpload");
    const file = fileInput.files[0];
    const predictionText = document.getElementById("predictionText");
    const preview = document.getElementById("preview");
    
    if (!file) {
        predictionText.textContent = "Please select an image first!";
        return;
    }
    
    predictionText.textContent = "Analyzing...";
    preview.style.opacity = "0.7";  // Visual feedback
    
    try {
        const formData = new FormData();
        formData.append("file", file);
        
        // Use relative path for local development
        // For production, you might need the full URL
        const response = await fetch("/predict", {
            method: "POST",
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || "Request failed");
        }
        
        const data = await response.json();
        
        // Map predictions to human-readable labels
        const skinTones = ["Light", "Medium-Light", "Medium-Dark", "Dark"];
        const confidence = (data.confidence * 100).toFixed(1);
        
        predictionText.innerHTML = `
            <strong>${skinTones[data.prediction] || "Unknown"}</strong>
            <br><small>${confidence}% confidence</small>
        `;
        
    } catch (error) {
        console.error("Prediction error:", error);
        predictionText.textContent = `Error: ${error.message}`;
    } finally {
        preview.style.opacity = "1";
    }
});