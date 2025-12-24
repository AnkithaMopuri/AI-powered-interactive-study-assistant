// File Upload Handling
document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    
    if (uploadForm) {
        const fileInput = document.getElementById('fileInput');
        const dropArea = document.getElementById('dropArea');
        const uploadBtn = document.getElementById('uploadBtn');
        const progressBar = document.getElementById('progressBar');
        const resultDiv = document.getElementById('result');
        
        // Drag and drop handlers
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, preventDefaults, false);
        });
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, () => {
                dropArea.style.borderColor = '#667eea';
                dropArea.style.background = '#edf2f7';
            }, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, () => {
                dropArea.style.borderColor = '#cbd5e0';
                dropArea.style.background = '#f7fafc';
            }, false);
        });
        
        dropArea.addEventListener('drop', handleDrop, false);
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length > 0) {
                fileInput.files = files;
                updateFileName(files[0].name);
            }
        }
        
        fileInput.addEventListener('change', function() {
            if (this.files.length > 0) {
                updateFileName(this.files[0].name);
            }
        });
        
        function updateFileName(name) {
            const label = dropArea.querySelector('p');
            label.textContent = `Selected: ${name}`;
        }
        
        // Form submission
        uploadForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(uploadForm);
            
            // Show progress
            uploadBtn.disabled = true;
            progressBar.style.display = 'block';
            resultDiv.innerHTML = '';
            resultDiv.className = 'result-message';
            
            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                progressBar.style.display = 'none';
                
                if (data.success) {
                    resultDiv.className = 'result-message success';
                    resultDiv.innerHTML = `
                        <h3>✓ Document Processed Successfully!</h3>
                        <p>Filename: ${data.filename}</p>
                        <p>Words: ${data.word_count} | Sentences: ${data.sentence_count}</p>
                        <a href="/study/${data.doc_id}" class="btn btn-primary" style="margin-top: 15px;">
                            Start Studying →
                        </a>
                    `;
                } else {
                    resultDiv.className = 'result-message error';
                    resultDiv.innerHTML = `<p>Error: ${data.error}</p>`;
                }
            } catch (error) {
                progressBar.style.display = 'none';
                resultDiv.className = 'result-message error';
                resultDiv.innerHTML = `<p>Error: ${error.message}</p>`;
            } finally {
                uploadBtn.disabled = false;
            }
        });
    }
});