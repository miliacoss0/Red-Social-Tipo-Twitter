// Gestión de follows
document.addEventListener('DOMContentLoaded', function() {
    // Botones de seguir
    document.querySelectorAll('.follow-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const userId = this.dataset.userId;
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            fetch(`/follows/toggle/${userId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.is_following) {
                    this.textContent = 'Dejar de seguir';
                    this.classList.add('following');
                } else {
                    this.textContent = 'Seguir';
                    this.classList.remove('following');
                }
                // Actualizar contador
                const counter = document.querySelector(`.followers-count-${userId}`);
                if (counter) {
                    counter.textContent = data.followers_count;
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });
});