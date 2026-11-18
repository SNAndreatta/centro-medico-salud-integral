document.addEventListener("DOMContentLoaded", function () {

    // ==========================================
    // INICIALIZAR ICONOS DE LUCIDE
    // ==========================================

    function inicializarIconos() {
        if (typeof lucide !== "undefined") {
            lucide.createIcons();
        }
    }

    inicializarIconos();


    // ==========================================
    // BUSCADOR DE ESPECIALIDADES
    // ==========================================

    const buscador = document.getElementById("buscar-especialidad");
    const tarjetas = document.querySelectorAll(".tarjeta-especialidad");
    const mensaje = document.getElementById("sin-resultados");

    // Solo se ejecuta en el paso 1, donde existe el buscador.
    if (buscador && mensaje) {

        buscador.addEventListener("input", function () {

            const consulta = buscador.value.trim().toLowerCase();
            let visibles = 0;

            tarjetas.forEach(function (tarjeta) {

                const nombre = tarjeta.dataset.nombre || "";
                const coincide = nombre.includes(consulta);

                tarjeta.classList.toggle("hidden", !coincide);

                if (coincide) {
                    visibles++;
                }

            });

            mensaje.classList.toggle("hidden", visibles !== 0);

        });

    }


    // ==========================================
    // CALENDARIO DE TURNOS (PASO 3)
    // ==========================================

    const calendario = document.getElementById("calendario-turno");

    // Solo se ejecuta en el paso 3, donde existe la agenda.
    if (calendario) {

        const datosEl = document.getElementById("horarios-turno-json");
        const horariosPorFecha = datosEl ? JSON.parse(datosEl.textContent) : {};

        const panel = document.getElementById("panel-horarios-turno");
        const titulo = document.getElementById("titulo-dia-turno");
        const resumen = document.getElementById("texto-resumen-turno");
        const campoFecha = document.getElementById("campo-fecha");
        const campoHora = document.getElementById("campo-hora");
        const formulario = document.getElementById("form-turno");
        const error = document.getElementById("error-calendario");
        const botonesDia = calendario.querySelectorAll(".dia-calendario");

        const CLASE_HORA = "rounded-full border border-gray-200 px-1.5 py-2 text-[11px] font-semibold text-acento transition hover:border-acento sm:px-2 sm:text-xs";
        const CLASE_HORA_ACTIVA = "rounded-full border border-acento bg-acento px-1.5 py-2 text-[11px] font-semibold text-white transition sm:px-2 sm:text-xs";

        let fechaActiva = campoFecha ? campoFecha.value : "";
        let horaActiva = campoHora ? campoHora.value : "";

        function formatearFecha(iso) {
            const [anio, mes, dia] = iso.split("-").map(Number);
            const texto = new Date(anio, mes - 1, dia).toLocaleDateString("es-AR", {
                weekday: "long", day: "numeric", month: "long",
            });
            return texto.charAt(0).toUpperCase() + texto.slice(1);
        }

        function marcarDia(iso) {
            botonesDia.forEach(function (boton) {
                const activo = boton.dataset.fecha === iso;
                boton.classList.toggle("bg-acento", activo);
                boton.classList.toggle("text-white", activo);
                boton.setAttribute("aria-pressed", activo ? "true" : "false");
            });
        }

        function actualizarResumen() {
            if (!resumen) return;

            if (fechaActiva && horaActiva) {
                resumen.textContent = formatearFecha(fechaActiva) + " · " + horaActiva + " hs";
            } else if (fechaActiva) {
                resumen.textContent = formatearFecha(fechaActiva) + " · elegí un horario";
            } else {
                resumen.textContent = "Todavía no elegiste fecha ni horario";
            }
        }

        function seleccionarHora(hora, boton) {
            horaActiva = hora;
            campoHora.value = hora;

            panel.querySelectorAll("button[data-hora]").forEach(function (b) {
                b.className = b === boton ? CLASE_HORA_ACTIVA : CLASE_HORA;
            });

            actualizarResumen();
        }

        function renderHorarios(iso) {
            panel.innerHTML = "";
            horaActiva = "";
            campoHora.value = "";

            const horas = horariosPorFecha[iso] || [];

            if (titulo) {
                titulo.textContent = formatearFecha(iso);
            }

            if (horas.length === 0) {
                panel.innerHTML = '<p class="col-span-full text-center text-xs text-acento/70">No hay horarios disponibles para este día.</p>';
                actualizarResumen();
                return;
            }

            horas.forEach(function (hora) {
                const boton = document.createElement("button");
                boton.type = "button";
                boton.dataset.hora = hora;
                boton.className = CLASE_HORA;
                boton.textContent = hora;
                boton.addEventListener("click", function () {
                    seleccionarHora(hora, boton);
                });
                panel.appendChild(boton);
            });

            actualizarResumen();
        }

        function seleccionarDia(boton) {
            fechaActiva = boton.dataset.fecha;
            campoFecha.value = fechaActiva;
            marcarDia(fechaActiva);
            renderHorarios(fechaActiva);

            if (error) {
                error.classList.add("hidden");
            }
        }

        botonesDia.forEach(function (boton) {
            if (boton.disabled) return;
            boton.addEventListener("click", function () {
                seleccionarDia(boton);
            });
        });

        // Al volver desde la confirmación se recupera la fecha y hora elegidas.
        if (fechaActiva) {
            const boton = Array.from(botonesDia).find(function (b) {
                return b.dataset.fecha === fechaActiva;
            });

            if (boton && !boton.disabled) {
                marcarDia(fechaActiva);
                const horaInicial = horaActiva;
                renderHorarios(fechaActiva);

                if (horaInicial) {
                    const botonHora = Array.from(
                        panel.querySelectorAll("button[data-hora]")
                    ).find(function (b) {
                        return b.dataset.hora === horaInicial;
                    });

                    if (botonHora) {
                        seleccionarHora(horaInicial, botonHora);
                    }
                }
            } else {
                fechaActiva = "";
                horaActiva = "";
                campoFecha.value = "";
                campoHora.value = "";
                actualizarResumen();
            }
        }

        if (formulario) {
            formulario.addEventListener("submit", function (evento) {
                const accion = evento.submitter ? evento.submitter.value : "continuar";

                if (accion === "anterior") return;

                if (!campoFecha.value || !campoHora.value) {
                    evento.preventDefault();
                    if (error) error.classList.remove("hidden");
                }
            });
        }

    }

});