/**
 * medico_agenda.js — formulario de creación de agenda del médico.
 *
 * - Al marcar un día se habilitan sus horarios (inicio y fin).
 * - Al desmarcarlo se deshabilitan y se limpian.
 * - Antes de enviar se validan las fechas del rango y que la duración de
 *   cada jornada sea múltiplo de la duración del turno.
 */
document.addEventListener("DOMContentLoaded", () => {

    const form = document.getElementById("form-crear-agenda");

    if (!form) {
        return;
    }

    const checkboxes = form.querySelectorAll("[data-dia-checkbox]");
    const selectDuracion = document.getElementById("duracionTurno");
    const inputFechaInicio = document.getElementById("fechaInicioAgenda");
    const inputFechaHasta = document.getElementById("fechaHastaAgenda");

    const errorFechas = document.getElementById("errorFechasAgenda");
    const errorDias = document.getElementById("errorDiasAgenda");


    // ==========================================
    // DÍAS Y HORARIOS
    // ==========================================

    function filaDelDia(checkbox) {
        return checkbox.closest("[data-dia]");
    }

    function actualizarDia(checkbox) {
        const fila = filaDelDia(checkbox);

        if (!fila) {
            return;
        }

        const horaInicio = fila.querySelector("[data-hora-inicio]");
        const horaFin = fila.querySelector("[data-hora-fin]");

        [horaInicio, horaFin].forEach((input) => {
            if (!input) {
                return;
            }

            input.disabled = !checkbox.checked;

            if (!checkbox.checked) {
                input.value = "";
            }
        });
    }

    checkboxes.forEach((checkbox) => {
        checkbox.addEventListener("change", () => actualizarDia(checkbox));
    });


    // ==========================================
    // VALIDACIONES
    // ==========================================

    function mostrarError(elemento, mensaje) {
        if (!elemento) {
            return;
        }

        if (mensaje) {
            elemento.textContent = mensaje;
            elemento.classList.remove("hidden");
        } else {
            elemento.textContent = "";
            elemento.classList.add("hidden");
        }
    }

    function minutos(hora) {
        const [horas, minutos_hora] = hora.split(":").map(Number);

        return (horas * 60) + minutos_hora;
    }

    function nombreDelDia(checkbox) {
        const fila = filaDelDia(checkbox);
        const etiqueta = fila ? fila.querySelector("label") : null;

        return etiqueta ? etiqueta.textContent.trim() : "";
    }

    function validarFechas() {
        if (!inputFechaInicio.value || !inputFechaHasta.value) {
            return true;
        }

        if (inputFechaHasta.value < inputFechaInicio.value) {
            mostrarError(
                errorFechas,
                "La fecha de finalización debe ser igual o posterior a la fecha de inicio."
            );
            return false;
        }

        mostrarError(errorFechas, "");
        return true;
    }

    function validarDias() {
        const duracion = Number(selectDuracion ? selectDuracion.value : 0);
        const seleccionados = Array.from(checkboxes).filter((c) => c.checked);

        if (seleccionados.length === 0) {
            mostrarError(errorDias, "Elegí al menos un día de atención.");
            return false;
        }

        for (const checkbox of seleccionados) {
            const fila = filaDelDia(checkbox);
            const horaInicio = fila.querySelector("[data-hora-inicio]").value;
            const horaFin = fila.querySelector("[data-hora-fin]").value;
            const dia = nombreDelDia(checkbox);

            if (!horaInicio || !horaFin) {
                mostrarError(
                    errorDias,
                    `Indicá de qué hora a qué hora atiende el ${dia.toLowerCase()}.`
                );
                return false;
            }

            if (minutos(horaFin) <= minutos(horaInicio)) {
                mostrarError(
                    errorDias,
                    `La hora de fin del ${dia.toLowerCase()} debe ser posterior a la de inicio.`
                );
                return false;
            }

            if (duracion > 0 && (minutos(horaFin) - minutos(horaInicio)) % duracion !== 0) {
                mostrarError(
                    errorDias,
                    `La jornada del ${dia.toLowerCase()} tiene que ser múltiplo de ${duracion} minutos.`
                );
                return false;
            }
        }

        mostrarError(errorDias, "");
        return true;
    }


    // ==========================================
    // ENVÍO DEL FORMULARIO
    // ==========================================

    form.addEventListener("submit", (evento) => {
        const fechasOk = validarFechas();
        const diasOk = validarDias();

        if (!fechasOk || !diasOk) {
            evento.preventDefault();
        }
    });

});
