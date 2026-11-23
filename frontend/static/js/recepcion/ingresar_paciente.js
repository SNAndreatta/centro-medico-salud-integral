/**
 * ingresar_paciente.js — ingreso de pacientes por lectura del código QR.
 *
 * 1. El botón "Ingresar paciente" abre el modal con la cámara del dispositivo.
 * 2. Al leer un QR se completa un formulario HTML y Flask lo envía al backend.
 * 3. Se muestra un pop-up con el resultado (correcto / incorrecto).
 * 4. Si el ingreso fue correcto, la sala de espera se recarga para mostrar
 *    al paciente que acaba de llegar.
 */
document.addEventListener("DOMContentLoaded", () => {

    // ==========================================
    // ELEMENTOS DEL DOM
    // ==========================================

    const botonIngresar = document.getElementById("boton-ingresar-paciente");
    const modalEscaner = document.getElementById("modal-escaner-qr");
    const modalResultado = document.getElementById("modal-resultado-ingreso");
    const lector = document.getElementById("lector-qr");
    const video = document.getElementById("video-qr");
    const estadoLector = document.getElementById("estado-lector");
    const mensajeResultado = document.getElementById("mensaje-resultado-ingreso");
    const botonCerrarResultado = document.getElementById("boton-cerrar-resultado-ingreso");

    if (!botonIngresar || !modalEscaner || !modalResultado || !lector || !video) {
        return;
    }

    const formularioCheckin = document.getElementById("form-checkin-qr");
    const tokenCheckin = document.getElementById("token-checkin");

    // Estado del lector.
    let escanerHtml5 = null;
    let streamCamara = null;
    let animacion = null;
    let procesando = false;
    let recargarAlCerrar = false;
    let resultadoResuelto = false;
    let resultadoVisible = false;


    // ==========================================
    // UTILIDADES
    // ==========================================

    function abrirModal(id) {
        if (typeof window.abrirModal === "function") {
            window.abrirModal(id);
            return;
        }

        const modal = document.getElementById(id);

        if (modal) {
            modal.classList.remove("hidden");
            modal.classList.add("flex");
        }
    }

    function mostrarEstado(mensaje) {
        if (estadoLector) {
            estadoLector.textContent = mensaje;
        }
    }


    // ==========================================
    // CÁMARA
    // ==========================================

    async function detenerCamara() {
        if (escanerHtml5) {
            try {
                await escanerHtml5.stop();
                escanerHtml5.clear();
            } catch (error) {
                console.warn("No se pudo detener el lector QR:", error);
            }

            escanerHtml5 = null;
        }

        if (animacion) {
            cancelAnimationFrame(animacion);
            animacion = null;
        }

        if (streamCamara) {
            streamCamara.getTracks().forEach((pista) => pista.stop());
            streamCamara = null;
        }

        video.srcObject = null;
        video.classList.add("hidden");
        lector.innerHTML = "";
    }

    async function iniciarConHtml5QrCode() {
        escanerHtml5 = new Html5Qrcode("lector-qr", {
            fps: 10,
            qrbox: { width: 250, height: 250 },
            aspectRatio: 1,
        });

        await escanerHtml5.start(
            { facingMode: "environment" },
            { fps: 10, qrbox: { width: 250, height: 250 }, aspectRatio: 1 },
            (texto) => registrarIngreso(texto),
            () => { }
        );
    }

    async function iniciarConBarcodeDetector() {
        const detector = new BarcodeDetector({ formats: ["qr_code"] });
        const lienzo = document.createElement("canvas");
        const contexto = lienzo.getContext("2d");

        streamCamara = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: { ideal: "environment" } },
            audio: false,
        });

        video.srcObject = streamCamara;
        video.classList.remove("hidden");

        await video.play();

        const buscar = async () => {
            if (procesando) return;

            if (video.readyState === video.HAVE_ENOUGH_DATA) {
                lienzo.width = video.videoWidth;
                lienzo.height = video.videoHeight;

                contexto.drawImage(video, 0, 0, lienzo.width, lienzo.height);

                try {
                    const codigos = await detector.detect(lienzo);

                    if (codigos.length > 0) {
                        registrarIngreso(codigos[0].rawValue);
                        return;
                    }
                } catch (error) {
                    console.warn("No se pudo leer el código QR:", error);
                }
            }

            animacion = requestAnimationFrame(buscar);
        };

        animacion = requestAnimationFrame(buscar);
    }

    async function iniciarCamara() {
        // Se asegura de que no quede una cámara anterior encendida.
        await detenerCamara();

        mostrarEstado("Iniciando la cámara...");

        try {
            if (window.Html5Qrcode) {
                await iniciarConHtml5QrCode();
            } else if ("BarcodeDetector" in window && navigator.mediaDevices) {
                await iniciarConBarcodeDetector();
            } else {
                throw new Error("Este dispositivo no permite leer códigos QR.");
            }

            mostrarEstado("Apuntá la cámara al código QR del turno.");

        } catch (error) {
            console.warn("No se pudo iniciar la cámara:", error);

            await detenerCamara();

            mostrarEstado(
                "No se pudo acceder a la cámara. Verificá que el dispositivo permita " +
                "su uso y que la página se abra de forma segura (HTTPS)."
            );
        }
    }

    async function abrirEscaner() {
        procesando = false;
        resultadoResuelto = false;

        abrirModal("modal-escaner-qr");

        // La cámara se inicia después de que el modal esté visible.
        setTimeout(iniciarCamara, 80);
    }


    // ==========================================
    // REGISTRO DEL INGRESO
    // ==========================================

    async function registrarIngreso(token) {
        if (procesando) return;

        procesando = true;

        await detenerCamara();
        mostrarEstado("Registrando el ingreso...");

        if (!formularioCheckin || !tokenCheckin) {
            mostrarResultado(false, "No se pudo preparar el formulario de ingreso.");
            return;
        }

        tokenCheckin.value = token;
        formularioCheckin.submit();
    }

    function mostrarResultado(exito, mensaje) {
        recargarAlCerrar = exito;
        resultadoResuelto = false;
        resultadoVisible = true;

        if (mensajeResultado) {
            mensajeResultado.textContent = mensaje;
        }

        if (botonCerrarResultado) {
            botonCerrarResultado.textContent = exito ? "Cerrar" : "Reintentar";
        }

        abrirModal("modal-resultado-ingreso");

        const iconoExitoVisible = modalResultado.querySelector(
            "#icono-resultado-exito, [data-lucide='circle-check']"
        );
        const iconoErrorVisible = modalResultado.querySelector(
            "#icono-resultado-error, [data-lucide='circle-x']"
        );

        if (iconoExitoVisible) {
            iconoExitoVisible.classList.toggle("hidden", !exito);
        }

        if (iconoErrorVisible) {
            iconoErrorVisible.classList.toggle("hidden", exito);
        }
    }

    function cerrarResultado() {
        if (resultadoResuelto) return;

        resultadoResuelto = true;
        resultadoVisible = false;

        if (recargarAlCerrar) {
            window.location.reload();
            return;
        }

        // El ingreso falló: se vuelve a abrir la cámara para reintentar.
        abrirEscaner();
    }


    // ==========================================
    // EVENTOS
    // ==========================================

    botonIngresar.addEventListener("click", (event) => {
        event.preventDefault();
        abrirEscaner();
    });

    // Cierre del modal del lector (botón, fondo oscuro o Escape).
    modalEscaner.addEventListener("click", (event) => {
        if (event.target === modalEscaner) {
            detenerCamara();
        }
    });

    modalEscaner.querySelectorAll("[data-cerrar-modal]").forEach((boton) => {
        boton.addEventListener("click", () => detenerCamara());
    });

    // Cierre del pop-up de resultado.
    if (botonCerrarResultado) {
        botonCerrarResultado.addEventListener("click", () => cerrarResultado());
    }

    modalResultado.addEventListener("click", (event) => {
        if (event.target === modalResultado) {
            cerrarResultado();
        }
    });

    const datosResultado = document.getElementById("datos-resultado-ingreso");
    if (datosResultado && datosResultado.dataset.resultado) {
        mostrarResultado(
            datosResultado.dataset.resultado === "ok",
            datosResultado.dataset.mensaje || "Ingreso registrado correctamente.",
        );
    }

    document.addEventListener("keydown", (event) => {
        if (event.key !== "Escape") return;

        // Se detiene la cámara si el lector estaba activo.
        if (escanerHtml5 || streamCamara) {
            detenerCamara();
        }

        if (resultadoVisible) {
            cerrarResultado();
        }
    });

});