// script.js

document.getElementById('uploadForm').addEventListener('submit', function(event) {
    event.preventDefault();
    
    let formData = new FormData();
    formData.append('file', document.getElementById('fileInput').files[0]);
    
    fetch('http://localhost:8080/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        // Display results
        let resultsDiv = document.getElementById('results');
        if (data.error) {
            resultsDiv.innerHTML = `<p>Error: ${data.error}</p>`;
        } else {
            resultsDiv.innerHTML = `
                <h2>Training Results:</h2>
                <pre>${JSON.stringify(data.train_results, null, 2)}</pre>
                <h2>Testing Results:</h2>
                <pre>${JSON.stringify(data.test_results, null, 2)}</pre>
                <h2>Forecast for Next 7 Days:</h2>
                <pre>${JSON.stringify(data.forecast, null, 2)}</pre>
            `;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        let resultsDiv = document.getElementById('results');
        resultsDiv.innerHTML = `<p>Error: ${error.message}</p>`;
    });
});
