// Manejo de likes
document.querySelectorAll('.like-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const postId = this.dataset.postId;
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        fetch(`/posts/like/${postId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            const countSpan = document.querySelector(`.likes-count-${postId}`);
            if (countSpan) {
                countSpan.textContent = data.likes_count;
            }
            this.classList.toggle('liked');
        })
        .catch(error => console.error('Error:', error));
    });
});