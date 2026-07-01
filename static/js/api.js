// Funcion para obtener el token CSRF de las cookies
function getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return value;
        }
    }
    return null;
}

// Funcion generica para hacer peticiones API
function apiRequest(url, method = 'GET', data = null) {
    const headers = {
        'Accept': 'application/json'
    };
    
    if (method === 'POST' || method === 'PUT' || method === 'DELETE') {
        headers['Content-Type'] = 'application/json';
        const csrfToken = getCSRFToken();
        if (csrfToken) {
            headers['X-CSRFToken'] = csrfToken;
        }
    }
    
    const options = {
        method: method,
        headers: headers,
        credentials: 'same-origin'
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    return fetch(url, options)
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.error || 'Error HTTP: ' + response.status);
                });
            }
            return response.json();
        });
}

// Funcion para verificar sesion
function verificarSesion() {
    return apiRequest('/posts/api/session/')
        .then(data => {
            console.log('Sesion activa:', data.usuario);
            return data;
        })
        .catch(error => {
            console.warn('Sesion no activa:', error.message);
            return null;
        });
}

// Funcion para cargar temas de interes en la barra lateral
function cargarTemasInteres(containerId = 'temas-interes') {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    fetch('/posts/api/hashtags/', {
        headers: {
            'Accept': 'application/json'
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error HTTP: ' + response.status);
        }
        return response.json();
    })
    .then(data => {
        container.innerHTML = '';
        // Mostrar todos los temas ordenados por popularidad
        const temasOrdenados = data.hashtags.sort((a, b) => b.cantidad - a.cantidad);
        
        temasOrdenados.forEach(hashtag => {
            const link = document.createElement('a');
            link.href = `/posts/hashtags/${hashtag.nombre}/`;
            link.style.cssText = 'display: block; padding: 5px 10px; color: #0366d6; text-decoration: none; font-size: 14px; border-bottom: 1px solid #e1e4e8;';
            link.textContent = `#${hashtag.nombre} (${hashtag.cantidad} posts)`;
            container.appendChild(link);
        });
        
        if (container.children.length === 0) {
            container.innerHTML = '<p style="font-size: 12px; color: #586069; padding: 10px;">No hay temas populares</p>';
        }
    })
    .catch(error => {
        console.error('Error cargando temas:', error);
        container.innerHTML = '<p style="font-size: 12px; color: #586069; padding: 10px;">Error al cargar temas</p>';
    });
}

// Funcion para mostrar mensajes de error
function showError(message, containerId = 'error-message') {
    const container = document.getElementById(containerId);
    if (container) {
        container.textContent = message;
        container.style.display = 'block';
        setTimeout(() => {
            container.style.display = 'none';
        }, 5000);
    } else {
        alert(message);
    }
}

// Funcion para mostrar loading
function showLoading(containerId, message = 'Cargando...') {
    const container = document.getElementById(containerId);
    if (container) {
        container.innerHTML = `<div style="text-align: center; padding: 20px;">${message}</div>`;
    }
}

// Inicializar al cargar la pagina
document.addEventListener('DOMContentLoaded', function() {
    // Verificar sesion
    verificarSesion();
    
    // Cargar temas de interes si existe el contenedor
    if (document.getElementById('temas-interes')) {
        cargarTemasInteres('temas-interes');
    }
});

// Exponer funciones globalmente
window.getCSRFToken = getCSRFToken;
window.apiRequest = apiRequest;
window.verificarSesion = verificarSesion;
window.cargarTemasInteres = cargarTemasInteres;
window.showError = showError;
window.showLoading = showLoading;