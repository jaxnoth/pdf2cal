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

        const formData = new FormData(this);

        try {
            status.textContent = 'Converting...';
            const response = await fetch('/convert', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'events.ics';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                status.textContent = 'Conversion successful!';
            } else {
                status.textContent = 'Error converting file';
            }
        } catch (error) {
            status.textContent = 'Error: ' + error.message;
        }
    });
});