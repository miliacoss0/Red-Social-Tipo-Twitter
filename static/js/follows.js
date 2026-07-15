document.addEventListener('DOMContentLoaded', function() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    
    // Función para mostrar notificaciones
    function mostrarNotificacion(mensaje, tipo = 'success') {
        // Eliminar notificaciones existentes
        const existing = document.querySelector('.notificacion-flotante');
        if (existing) {
            existing.remove();
        }
        
        const notificacion = document.createElement('div');
        notificacion.className = `notificacion-flotante ${tipo}`;
        notificacion.textContent = mensaje;
        document.body.appendChild(notificacion);
        
        setTimeout(() => {
            notificacion.classList.add('ocultar');
            setTimeout(() => notificacion.remove(), 300);
        }, 3000);
    }
    
    // Función para actualizar contadores
    function actualizarContador(userId, nuevoContador) {
        const counters = document.querySelectorAll(`.followers-count-${userId}`);
        counters.forEach(counter => {
            counter.textContent = nuevoContador;
        });
    }
    
    // Función para actualizar botón
    function actualizarBoton(btn, isFollowing) {
        if (isFollowing) {
            btn.textContent = 'Dejar de seguir';
            btn.classList.add('following');
        } else {
            btn.textContent = 'Seguir';
            btn.classList.remove('following');
        }
    }
    
    // Manejar click en botones de follow
    document.querySelectorAll('.follow-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            
            const userId = this.dataset.userId;
            const btnElement = this;
            
            // Guardar estado anterior para poder restaurar en caso de error
            const previousText = btnElement.textContent;
            const previousClass = btnElement.classList.contains('following');
            
            // Deshabilitar botón mientras se procesa
            btnElement.disabled = true;
            btnElement.textContent = 'Procesando...';
            
            fetch(`/follows/toggle/${userId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({})
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => {
                        throw new Error(err.error || 'Error al procesar');
                    });
                }
                return response.json();
            })
            .then(data => {
                // Actualizar botón
                actualizarBoton(btnElement, data.is_following);
                
                // Actualizar contador
                if (data.followers_count !== undefined) {
                    actualizarContador(userId, data.followers_count);
                }
                
                // Mostrar notificación
                if (data.is_following) {
                    mostrarNotificacion(` Siguiendo a ${data.username || 'usuario'}`, 'success');
                } else {
                    mostrarNotificacion(` Dejaste de seguir`, 'info');
                }
                
                // Disparar evento para actualizar otros componentes (ej: perfil)
                document.dispatchEvent(new CustomEvent('followToggle', {
                    detail: {
                        userId: userId,
                        isFollowing: data.is_following,
                        followersCount: data.followers_count
                    }
                }));
            })
            .catch(error => {
                console.error('Error:', error);
                mostrarNotificacion(`❌ ${error.message || 'Error al procesar'}`, 'error');
                
                // Restaurar estado anterior
                btnElement.textContent = previousText;
                if (previousClass) {
                    btnElement.classList.add('following');
                } else {
                    btnElement.classList.remove('following');
                }
            })
            .finally(() => {
                btnElement.disabled = false;
            });
        });
    });
    
    // Escuchar evento de followToggle para actualizar contadores en otras partes de la página
    document.addEventListener('followToggle', function(e) {
        const detail = e.detail;
        // Actualizar cualquier contador que no tenga la clase específica
        document.querySelectorAll(`[data-followers-count="${detail.userId}"]`).forEach(el => {
            el.textContent = detail.followersCount;
        });
    });
});