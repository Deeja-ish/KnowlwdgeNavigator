document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.ai-assistant-section form');
    
    if (form) {
        const responseContainer = document.getElementById('ai-response-container');

        form.addEventListener('submit', function(event) {
            event.preventDefault(); 
            
            const formData = new FormData(form);
            
            responseContainer.innerHTML = '<p>Thinking... <i class="fas fa-spinner fa-spin"></i></p>';

            fetch(form.action, {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    responseContainer.innerHTML = `<p class="flash-error">${data.error}</p>`;
                } else {
                    responseContainer.innerHTML = `<p class="ai-response flash-success">${data.explanation}</p>`;
                }
            })
            .catch(error => {
                responseContainer.innerHTML = `<p class="flash-error">An unexpected error occurred. Please try again.</p>`;
                console.error('Error:', error);
            });
        });
    }
});