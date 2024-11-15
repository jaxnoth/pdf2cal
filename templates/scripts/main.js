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

    document.querySelector('#uploadForm').addEventListener('submit', async function(e) {
        e.preventDefault();

        const file = fileInput.files[0];
        if (!file) {
            status.textContent = 'Please select a file';
            return;
        }

        status.textContent = 'Converting...';

        // Convert file to base64
        const reader = new FileReader();
        reader.onload = async function() {
            const base64File = reader.result.split(',')[1];

            try {
                const response = await fetch('/api/ConvertPDF', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ pdf_content: base64File })
                });

                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'basketball_schedule.ics';
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    status.textContent = 'Conversion successful!';
                } else {
                    const error = await response.text();
                    status.textContent = `Error: ${error}`;
                }
            } catch (error) {
                status.textContent = `Error: ${error.message}`;
            }
        };
        reader.readAsDataURL(file);
    });
});