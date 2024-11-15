document.addEventListener('DOMContentLoaded', function() {
    const uploadArea = document.querySelector('.upload-area');
    const fileInput = document.querySelector('#pdf_file');
    const status = document.querySelector('#status');

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    uploadArea.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        fileInput.files = files;
    }

    document.getElementById('uploadForm').addEventListener('submit', async function(e) {
        e.preventDefault();

        const fileInput = document.getElementById('pdf_file');
        const file = fileInput.files[0];
        const status = document.getElementById('status');

        if (!file) {
            alert('Please select a file');
            return;
        }

        try {
            status.textContent = 'Converting...';

            // Create FormData
            const formData = new FormData();
            formData.append('file', file);

            const response = await fetch('/api/ConvertPDF', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'schedule.ics';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);

            status.textContent = 'Conversion successful!';
        } catch (error) {
            console.error('Error:', error);
            status.textContent = `Error: ${error.message}`;
        }
    });
});