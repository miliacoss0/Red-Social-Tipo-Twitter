class MensajeriaApp {
    constructor() {
        this.csrfToken = this.getCsrfToken();
        this.initializeEventListeners();
    }

    getCsrfToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    // Enviar mensaje usando fetch
    async enviarMensaje(receptorId, contenido) {
        if (!contenido.trim()) {
            this.mostrarError('El mensaje no puede estar vacío');
            return false;
        }

        try {
            const response = await fetch('/mensajes/api/enviar/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({
                    receptor_id: parseInt(receptorId),
                    contenido: contenido.trim()
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Error al enviar mensaje');
            }

            if (data.success) {
                this.agregarMensajeAlChat(data.mensaje);
                this.limpiarInput();
                return true;
            } else {
                this.mostrarError(data.error || 'Error al enviar mensaje');
                return false;
            }
        } catch (error) {
            console.error('Error en enviarMensaje:', error);
            this.mostrarError('Error de conexión al enviar mensaje');
            return false;
        }
    }

    // Obtener mensajes de una conversación
    async obtenerMensajes(conversacionId) {
        try {
            const response = await fetch(`/mensajes/api/mensajes/${conversacionId}/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Error al obtener mensajes');
            }

            if (data.success) {
                return data.mensajes || [];
            } else {
                this.mostrarError(data.error || 'Error al obtener mensajes');
                return [];
            }
        } catch (error) {
            console.error('Error en obtenerMensajes:', error);
            this.mostrarError('Error de conexión al obtener mensajes');
            return [];
        }
    }

    // Marcar mensaje como leído
    async marcarLeido(mensajeId) {
        try {
            const response = await fetch(`/mensajes/api/marcar-leido/${mensajeId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                }
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Error al marcar como leído');
            }

            return data.success;
        } catch (error) {
            console.error('Error en marcarLeido:', error);
            return false;
        }
    }

    // Obtener lista de conversaciones
    async obtenerConversaciones() {
        try {
            const response = await fetch('/mensajes/api/conversaciones/', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Error al obtener conversaciones');
            }

            if (data.success) {
                return data.conversaciones || [];
            } else {
                this.mostrarError(data.error || 'Error al obtener conversaciones');
                return [];
            }
        } catch (error) {
            console.error('Error en obtenerConversaciones:', error);
            this.mostrarError('Error de conexión al obtener conversaciones');
            return [];
        }
    }

    // Agregar mensaje al chat (para UI)
    agregarMensajeAlChat(mensaje) {
        const chatContainer = document.getElementById('chat-messages');
        if (!chatContainer) return;

        const mensajeElement = this.crearElementoMensaje(mensaje);
        chatContainer.appendChild(mensajeElement);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // Crear elemento HTML para un mensaje
    crearElementoMensaje(mensaje) {
        const div = document.createElement('div');
        div.className = `mensaje ${mensaje.es_mio ? 'mensaje-propio' : 'mensaje-otro'}`;
        div.dataset.mensajeId = mensaje.id;

        div.innerHTML = `
            <div class="mensaje-contenido">${this.escapeHTML(mensaje.contenido)}</div>
            <div class="mensaje-info">
                <span class="mensaje-emisor">${mensaje.es_mio ? 'Yo' : mensaje.emisor}</span>
                <span class="mensaje-fecha">${this.formatearFecha(mensaje.fecha)}</span>
                ${mensaje.leido ? '<span class="mensaje-leido">✓✓</span>' : ''}
            </div>
        `;

        return div;
    }

    // Limpiar input de mensaje
    limpiarInput() {
        const input = document.getElementById('mensaje-input');
        if (input) {
            input.value = '';
            input.focus();
        }
    }

    // Mostrar error
    mostrarError(mensaje) {
        const errorContainer = document.getElementById('mensaje-error');
        if (errorContainer) {
            errorContainer.textContent = mensaje;
            errorContainer.style.display = 'block';
            setTimeout(() => {
                errorContainer.style.display = 'none';
            }, 3000);
        } else {
            alert(mensaje);
        }
    }

    // Formatear fecha
    formatearFecha(fechaISO) {
        const fecha = new Date(fechaISO);
        return fecha.toLocaleString('es-ES', {
            hour: '2-digit',
            minute: '2-digit',
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
    }

    // Escapar HTML para prevenir XSS
    escapeHTML(texto) {
        const div = document.createElement('div');
        div.textContent = texto;
        return div.innerHTML;
    }

    // Inicializar event listeners
    initializeEventListeners() {
        // Enviar mensaje con Enter
        const input = document.getElementById('mensaje-input');
        if (input) {
            input.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    const boton = document.getElementById('enviar-boton');
                    if (boton) boton.click();
                }
            });
        }

        // Botón de enviar
        const botonEnviar = document.getElementById('enviar-boton');
        if (botonEnviar) {
            botonEnviar.addEventListener('click', () => {
                const receptorId = document.getElementById('receptor-id');
                const input = document.getElementById('mensaje-input');
                if (receptorId && input) {
                    this.enviarMensaje(receptorId.value, input.value);
                }
            });
        }
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    window.mensajeria = new MensajeriaApp();
});