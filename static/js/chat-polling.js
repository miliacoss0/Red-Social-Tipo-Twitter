class ChatPolling {
    constructor(conversacionId, interval = 3000) {
        this.conversacionId = conversacionId;
        this.interval = interval;
        this.ultimoMensajeId = null;
        this.intervalId = null;
        this.activo = false;
    }

    iniciar() {
        if (this.activo) return;
        this.activo = true;
        this.obtenerUltimoId();
        this.intervalId = setInterval(() => this.actualizarMensajes(), this.interval);
        console.log(`Polling iniciado para conversación ${this.conversacionId}`);
    }

    detener() {
        this.activo = false;
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
        console.log(`Polling detenido para conversación ${this.conversacionId}`);
    }

    async obtenerUltimoId() {
        try {
            const mensajes = await window.mensajeria.obtenerMensajes(this.conversacionId);
            if (mensajes && mensajes.length > 0) {
                this.ultimoMensajeId = mensajes[mensajes.length - 1].id;
            }
        } catch (error) {
            console.error('Error al obtener último ID:', error);
        }
    }

    async actualizarMensajes() {
        try {
            const mensajes = await window.mensajeria.obtenerMensajes(this.conversacionId);
            if (!mensajes || mensajes.length === 0) return;

            // Encontrar mensajes nuevos
            let inicio = 0;
            if (this.ultimoMensajeId) {
                // Buscar el índice del último mensaje conocido
                for (let i = mensajes.length - 1; i >= 0; i--) {
                    if (mensajes[i].id === this.ultimoMensajeId) {
                        inicio = i + 1;
                        break;
                    }
                }
            }

            // Agregar nuevos mensajes
            for (let i = inicio; i < mensajes.length; i++) {
                const mensaje = mensajes[i];
                // Solo agregar mensajes que no son míos (ya están en el chat)
                if (!mensaje.es_mio) {
                    window.mensajeria.agregarMensajeAlChat(mensaje);
                }
            }

            // Actualizar último ID
            if (mensajes.length > 0) {
                this.ultimoMensajeId = mensajes[mensajes.length - 1].id;
            }
        } catch (error) {
            console.error('Error al actualizar mensajes:', error);
        }
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    const conversacionId = document.getElementById('conversacion-id');
    if (conversacionId) {
        const polling = new ChatPolling(parseInt(conversacionId.value));
        window.polling = polling;
        polling.iniciar();

        // Detener polling cuando se sale de la página
        window.addEventListener('beforeunload', function() {
            if (window.polling) {
                window.polling.detener();
            }
        });
    }
});