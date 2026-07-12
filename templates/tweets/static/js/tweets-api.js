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
    // Configurar headers para todas las peticiones
    const headers = {
        'Accept': 'application/json'  // Forzar respuesta JSON
    };
    
    // Agregar headers especificos para POST, PUT, DELETE
    if (method === 'POST' || method === 'PUT' || method === 'DELETE') {
        headers['Content-Type'] = 'application/json';
        const csrfToken = getCSRFToken();
        if (csrfToken) {
            headers['X-CSRFToken'] = csrfToken;  // Token CSRF para seguridad
        }
    }
    
    // Configurar opciones de la peticion
    const options = {
        method: method,
        headers: headers,
        credentials: 'same-origin'  // Enviar cookies
    };
    
    // Agregar cuerpo si hay datos
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    // Realizar la peticion fetch
    return fetch(url, options)
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.error || 'Error HTTP: ' + response.status);
                });
            }
            return response.json();  // Parsear respuesta JSON
        });
}

function highlightMentions(text) {
    /**
     * Convierte @usuario en un enlace clickeable a su perfil.
     */
    if (!text) return text;
    
    // Buscar patrones @usuario (acepta letras, números, guiones y guión bajo)
    return text.replace(/@([\w\-]+)/g, function(match, username) {
        return `<a href="/tweets/perfil/${username}/" class="mention-link">@${username}</a>`;
    });
}

// Funcion para cargar todos los tweets
function cargarTweets(containerId = 'tweets-container') {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = '<div style="text-align: center; padding: 20px;">Cargando tweets...</div>';
    
    apiRequest('/tweets/api/tweets/')
        .then(data => {
            container.innerHTML = '';
            
            if (data.tweets.length === 0) {
                container.innerHTML = '<p style="text-align: center; color: #586069;">No hay tweets todavia. ¡Se el primero en publicar!</p>';
                return;
            }
            
            data.tweets.forEach(tweet => {
                const div = document.createElement('div');
                div.className = 'tweet-card';
                div.style.cssText = 'border: 1px solid #e1e4e8; border-radius: 8px; padding: 15px; margin-bottom: 15px;';
                
                // RESALTAR MENCIONES EN EL CONTENIDO
                const contenidoConMenciones = highlightMentions(tweet.content);
                
                let hashtagsHtml = '';
                if (tweet.hashtags && tweet.hashtags.length > 0) {
                    hashtagsHtml = '<div style="margin-top: 10px;">';
                    tweet.hashtags.forEach(tag => {
                        hashtagsHtml += `<a href="/tweets/tag/${tag}/" style="color: #0366d6; text-decoration: none; margin-right: 10px; font-size: 14px;">#${tag}</a>`;
                    });
                    hashtagsHtml += '</div>';
                }
                
                div.innerHTML = `
                    <div style="margin-bottom: 10px; color: #0366d6;">
                        <a href="/tweets/perfil/${tweet.author}/" style="color: #0366d6; text-decoration: none; font-weight: bold;">
                            ${tweet.author}
                        </a>
                        <small style="color: #586069;">${tweet.created_at}</small>
                    </div>
                    <div style="margin-bottom: 10px; font-size: 16px; line-height: 1.5;">
                        ${contenidoConMenciones}
                    </div>
                    ${hashtagsHtml}
                `;
                container.appendChild(div);
            });
        })
        .catch(error => {
            console.error('Error:', error);
            container.innerHTML = `<p style="color: red; text-align: center;">Error al cargar tweets: ${error.message}</p>`;
        });
}


// Funcion para crear un tweet via API
function crearTweet(content, containerId = 'tweets-container') {
    if (!content || content.trim() === '') {
        alert('El contenido no puede estar vacio');
        return;
    }
    
    if (content.length > 280) {
        alert('El tweet excede los 280 caracteres');
        return;
    }
    
    apiRequest('/tweets/api/tweets/', 'POST', { content: content.trim() })
        .then(data => {
            if (data.ok) {
                console.log('Tweet creado:', data.id);
                // Recargar tweets con fetch
                cargarTweets(containerId);
                // Limpiar textarea
                const textarea = document.getElementById('tweet-content');
                if (textarea) {
                    textarea.value = '';
                }
                // Actualizar contador
                const contador = document.getElementById('caracteres-contador');
                if (contador) {
                    contador.textContent = '280 caracteres disponibles';
                    contador.style.color = '#586069';
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al crear tweet: ' + error.message);
        });
}

// Funcion para cargar tweets de un usuario especifico
function cargarTweetsUsuario(username, containerId = 'tweets-usuario-container') {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = '<div style="text-align: center; padding: 20px;">Cargando tweets...</div>';
    
    apiRequest(`/tweets/api/tweets/usuario/${username}/`)
        .then(data => {
            container.innerHTML = '';
            
            if (data.tweets.length === 0) {
                container.innerHTML = `<p style="text-align: center; color: #586069;">@${data.usuario} no tiene tweets todavia.</p>`;
                return;
            }
            
            data.tweets.forEach(tweet => {
                const div = document.createElement('div');
                div.className = 'tweet-card';
                div.style.cssText = 'border: 1px solid #e1e4e8; border-radius: 8px; padding: 15px; margin-bottom: 15px;';
                
                // RESALTAR MENCIONES EN EL CONTENIDO
                const contenidoConMenciones = highlightMentions(tweet.content);
                
                let hashtagsHtml = '';
                if (tweet.hashtags && tweet.hashtags.length > 0) {
                    hashtagsHtml = '<div style="margin-top: 10px;">';
                    tweet.hashtags.forEach(tag => {
                        hashtagsHtml += `<a href="/tweets/tag/${tag}/" style="color: #0366d6; text-decoration: none; margin-right: 10px; font-size: 14px;">#${tag}</a>`;
                    });
                    hashtagsHtml += '</div>';
                }
                
                div.innerHTML = `
                    <div style="margin-bottom: 10px; color: #0366d6;">
                        <a href="/tweets/perfil/${tweet.author}/" style="color: #0366d6; text-decoration: none; font-weight: bold;">
                            ${tweet.author}
                        </a>
                        <small style="color: #586069;">${tweet.created_at}</small>
                    </div>
                    <div style="margin-bottom: 10px; font-size: 16px; line-height: 1.5;">
                        ${contenidoConMenciones}
                    </div>
                    ${hashtagsHtml}
                `;
                container.appendChild(div);
            });
        })
        .catch(error => {
            console.error('Error:', error);
            container.innerHTML = `<p style="color: red; text-align: center;">Error al cargar tweets: ${error.message}</p>`;
        });
}

// Funcion para cargar tweets de un hashtag especifico
function cargarTweetsHashtag(tagName, containerId = 'tweets-hashtag-container') {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = '<div style="text-align: center; padding: 20px;">Cargando tweets...</div>';
    
    apiRequest(`/tweets/api/tweets/hashtag/${tagName}/`)
        .then(data => {
            container.innerHTML = '';
            
            if (data.tweets.length === 0) {
                container.innerHTML = `<p style="text-align: center; color: #586069;">No hay tweets con #${data.hashtag} todavia.</p>`;
                return;
            }
            
            data.tweets.forEach(tweet => {
                const div = document.createElement('div');
                div.className = 'tweet-card';
                div.style.cssText = 'border: 1px solid #e1e4e8; border-radius: 8px; padding: 15px; margin-bottom: 15px;';
                
                div.innerHTML = `
                    <div style="margin-bottom: 10px; color: #0366d6;">
                        <strong>${tweet.author}</strong>
                        <small style="color: #586069;">${tweet.created_at}</small>
                    </div>
                    <div style="margin-bottom: 10px; font-size: 16px; line-height: 1.5;">
                        ${tweet.content}
                    </div>
                `;
                container.appendChild(div);
            });
        })
        .catch(error => {
            console.error('Error:', error);
            container.innerHTML = `<p style="color: red; text-align: center;">Error al cargar tweets: ${error.message}</p>`;
        });
}

// Funcion para cargar menciones del usuario autenticado
function cargarMenciones(containerId = 'menciones-container') {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = '<div style="text-align: center; padding: 20px;">Cargando menciones...</div>';
    
    apiRequest('/tweets/api/menciones/')
        .then(data => {
            container.innerHTML = '';
            
            if (data.menciones.length === 0) {
                container.innerHTML = '<p style="text-align: center; color: #586069;">No te han mencionado todavia.</p>';
                return;
            }
            
            data.menciones.forEach(mencion => {
                const div = document.createElement('div');
                div.className = 'mencion-card';
                div.style.cssText = 'border: 1px solid #e1e4e8; border-radius: 8px; padding: 15px; margin-bottom: 15px;';
                
                // RESALTAR MENCIONES EN EL CONTENIDO DEL TWEET
                const contenidoConMenciones = highlightMentions(mencion.tweet_content);
                
                div.innerHTML = `
                    <div style="margin-bottom: 10px;">
                        <strong style="color: #0366d6;">
                            <a href="/tweets/perfil/${mencion.mentioned_by}/" style="color: #0366d6; text-decoration: none;">
                                @${mencion.mentioned_by}
                            </a>
                        </strong>
                        <small style="color: #586069;">te mencionó en un tweet</small>
                        <small style="color: #586069; display: block; font-size: 12px;">
                            ${mencion.created_at}
                        </small>
                    </div>
                    <div style="margin-bottom: 10px; padding: 10px; background: #f6f8fa; border-radius: 8px;">
                        ${contenidoConMenciones}
                    </div>
                    <div>
                        <a href="/tweets/tweet/${mencion.tweet_id}/" style="color: #0366d6; text-decoration: none;">
                            Ver tweet →
                        </a>
                        ${!mencion.is_read ? `
                            <button class="marcar-leido-btn" data-id="${mencion.id}" style="background: #0366d6; color: white; border: none; padding: 5px 15px; border-radius: 15px; cursor: pointer; margin-left: 10px; font-size: 12px;">
                                Marcar como leído
                            </button>
                        ` : `
                            <span style="background: #17BF63; color: white; padding: 3px 12px; border-radius: 15px; font-size: 12px; margin-left: 10px;">✓ Leído</span>
                        `}
                    </div>
                `;
                container.appendChild(div);
            });
            
            // Agregar event listeners para marcar como leído
            document.querySelectorAll('.marcar-leido-btn').forEach(btn => {
                btn.addEventListener('click', async function() {
                    const id = this.dataset.id;
                    const card = this.closest('.mencion-card');
                    
                    try {
                        const response = await apiRequest(`/tweets/api/marcar-leida/${id}/`, 'POST');
                        if (response.success) {
                            this.replaceWith('<span style="background: #17BF63; color: white; padding: 3px 12px; border-radius: 15px; font-size: 12px; margin-left: 10px;">✓ Leído</span>');
                        }
                    } catch (error) {
                        console.error('Error:', error);
                    }
                });
            });
        })
        .catch(error => {
            console.error('Error:', error);
            container.innerHTML = `<p style="color: red; text-align: center;">Error al cargar menciones: ${error.message}</p>`;
        });
}

// Funcion para buscar tweets via API
function buscarTweets(query, containerId = 'resultados-container') {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    if (!query || query.trim() === '') {
        container.innerHTML = '<p style="text-align: center; color: #586069;">Ingresa un termino de busqueda.</p>';
        return;
    }
    
    container.innerHTML = '<div style="text-align: center; padding: 20px;">Buscando...</div>';
    
    apiRequest(`/tweets/api/buscar/?q=${encodeURIComponent(query)}`)
        .then(data => {
            container.innerHTML = '';
            
            if (data.results.length === 0) {
                container.innerHTML = `<p style="text-align: center; color: #586069;">No se encontraron resultados para "${data.query}"</p>`;
                return;
            }
            
            data.results.forEach(tweet => {
                const div = document.createElement('div');
                div.className = 'tweet-card';
                div.style.cssText = 'border: 1px solid #e1e4e8; border-radius: 8px; padding: 15px; margin-bottom: 15px;';
                
                let hashtagsHtml = '';
                if (tweet.hashtags && tweet.hashtags.length > 0) {
                    hashtagsHtml = '<div style="margin-top: 10px;">';
                    tweet.hashtags.forEach(tag => {
                        hashtagsHtml += `<a href="/tweets/tag/${tag}/" style="color: #0366d6; text-decoration: none; margin-right: 10px; font-size: 14px;">#${tag}</a>`;
                    });
                    hashtagsHtml += '</div>';
                }
                
                div.innerHTML = `
                    <div style="margin-bottom: 10px; color: #0366d6;">
                        <strong>${tweet.author}</strong>
                        <small style="color: #586069;">${tweet.created_at}</small>
                    </div>
                    <div style="margin-bottom: 10px; font-size: 16px; line-height: 1.5;">
                        ${tweet.content}
                    </div>
                    ${hashtagsHtml}
                `;
                container.appendChild(div);
            });
        })
        .catch(error => {
            console.error('Error:', error);
            container.innerHTML = `<p style="color: red; text-align: center;">Error en la busqueda: ${error.message}</p>`;
        });
}

// Funcion para verificar sesion via API
function verificarSesionTweets() {
    apiRequest('/tweets/api/session/')
        .then(data => {
            console.log('Sesion activa (tweets):', data.usuario);
        })
        .catch(error => {
            console.warn('Sesion no activa (tweets):', error.message);
        });
}

//Inicializacion automatica al cargar la pagina
document.addEventListener('DOMContentLoaded', function() {
    // Verificar sesion al cargar la pagina
    verificarSesionTweets();
    
    // Si existe contenedor de tweets, cargarlos automaticamente
    if (document.getElementById('tweets-container')) {
        cargarTweets('tweets-container');
    }
    
    // Si existe contenedor de menciones, cargarlas automaticamente
    if (document.getElementById('menciones-container')) {
        cargarMenciones('menciones-container');
    }
    
    // Interceptar formulario de crear tweet para usar fetch
    const tweetForm = document.getElementById('tweet-form');
    if (tweetForm) {
        tweetForm.addEventListener('submit', function(e) {
            e.preventDefault();  // Evitar envio tradicional
            const textarea = document.getElementById('tweet-content');
            if (textarea) {
                crearTweet(textarea.value, 'tweets-container');
            }
        });
    }
});



//Exponer funciones globalmente para uso en otros scripts
window.cargarTweets = cargarTweets;
window.crearTweet = crearTweet;
window.cargarTweetsUsuario = cargarTweetsUsuario;
window.cargarTweetsHashtag = cargarTweetsHashtag;
window.cargarMenciones = cargarMenciones;
window.buscarTweets = buscarTweets;
window.apiRequest = apiRequest;
window.highlightMentions = highlightMentions; 