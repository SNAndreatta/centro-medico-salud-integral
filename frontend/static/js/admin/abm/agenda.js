
document.addEventListener("DOMContentLoaded", () => {

    // ==========================================
    // ELEMENTOS DEL DOM
    // ==========================================

    const datosAgenda = document.getElementById("datosAgenda");

    const selectorFecha = document.getElementById("selectorFecha");
    const contenedorFecha = document.getElementById("contenedorFecha");
    const fechaVisible = document.getElementById("fechaVisible");

    const horarios = document.querySelectorAll(".horario-agenda");

    const horaTurno = document.getElementById("horaTurno");
    const fechaTurno = document.getElementById("fechaTurno");


    // ==========================================
    // FUNCIONES DE FECHAS
    // ==========================================

    function obtenerFechaISO(fecha) {

        const anio = fecha.getFullYear();
        const mes = String(fecha.getMonth() + 1).padStart(2, "0");
        const dia = String(fecha.getDate()).padStart(2, "0");

        return `${anio}-${mes}-${dia}`;
    }


    function obtenerLunes(fecha) {

        const lunes = new Date(fecha);

        const diaSemana = lunes.getDay();

        lunes.setDate(
            lunes.getDate() - (diaSemana === 0 ? 6 : diaSemana - 1)
        );

        lunes.setHours(0, 0, 0, 0);

        return lunes;
    }


    function formatearFecha(fecha) {

        return fecha.toLocaleDateString("es-AR", {
            day: "2-digit",
            month: "2-digit",
            year: "numeric"
        });
    }


    // ==========================================
    // FECHA INICIAL
    // ==========================================

    let fechaInicio =
        selectorFecha?.value ||
        datosAgenda?.dataset.fechaInicio;

    if (!fechaInicio) {
        fechaInicio = obtenerFechaISO(new Date());
    }


    // ==========================================
    // ACTUALIZAR FECHAS DE LA AGENDA
    // ==========================================

    function actualizarFechas(lunes) {

        // Actualizar fecha de cada horario

        horarios.forEach((horario) => {

            const indiceDia = Number(horario.dataset.dia || 0);

            const fecha = new Date(lunes);

            fecha.setDate(lunes.getDate() + indiceDia);

            horario.dataset.fecha = obtenerFechaISO(fecha);

        });


        // Actualizar encabezados de los días

        const encabezados = document.querySelectorAll("[data-fecha-dia]");

        encabezados.forEach((encabezado, indice) => {

            const fecha = new Date(lunes);

            fecha.setDate(lunes.getDate() + indice);

            encabezado.textContent = String(fecha.getDate()).padStart(2, "0");

        });


        // Actualizar fecha visible

        if (fechaVisible) {
            fechaVisible.textContent = formatearFecha(lunes);
        }

    }


    // ==========================================
    // LIMPIAR SELECCIÓN DE HORARIO
    // ==========================================

    function limpiarSeleccion() {

        horarios.forEach((horario) => {

            horario.classList.remove(
                "bg-acento",
                "text-white",
                "seleccionado"
            );

            horario.classList.add(
                "bg-dominante",
                "text-acento"
            );

            horario.removeAttribute("aria-current");

        });


        if (horaTurno) {
            horaTurno.textContent = "—";
        }

        if (fechaTurno) {
            fechaTurno.textContent = "—";
        }

    }


    // ==========================================
    // SELECTOR DE CALENDARIO
    // ==========================================

    if (selectorFecha && contenedorFecha) {

        // Evitar escritura manual

        selectorFecha.addEventListener("keydown", (event) => {
            event.preventDefault();
        });


        selectorFecha.addEventListener("paste", (event) => {
            event.preventDefault();
        });


        selectorFecha.addEventListener("drop", (event) => {
            event.preventDefault();
        });


        // El input ocupa todo el contenedor.
        // El navegador abre el calendario nativo directamente.

        selectorFecha.addEventListener("change", () => {

            if (!selectorFecha.value) return;

            const [anio, mes, dia] = selectorFecha.value
                .split("-")
                .map(Number);

            const fechaSeleccionada = new Date(
                anio,
                mes - 1,
                dia
            );

            // Calcular lunes de la semana seleccionada

            const lunes = obtenerLunes(fechaSeleccionada);

            fechaInicio = obtenerFechaISO(lunes);

            // Actualizar selector al lunes correspondiente

            selectorFecha.value = fechaInicio;

            // Actualizar agenda

            actualizarFechas(lunes);

            // Limpiar turno seleccionado

            limpiarSeleccion();

        });

    }


    // ==========================================
    // SELECCIÓN DE HORARIOS
    // ==========================================

    horarios.forEach((horario) => {

        horario.addEventListener("click", () => {

            // No permitir seleccionar horarios ocupados

            if (
                horario.classList.contains("ocupado") ||
                horario.dataset.disponible === "false"
            ) {
                return;
            }


            // Quitar selección anterior

            limpiarSeleccion();


            // Seleccionar horario actual

            horario.classList.remove(
                "bg-dominante",
                "text-acento"
            );

            horario.classList.add(
                "bg-acento",
                "text-white",
                "seleccionado"
            );

            horario.setAttribute("aria-current", "true");


            // Obtener hora y fecha

            const hora =
                horario.dataset.hora ||
                horario.textContent.trim();

            const fecha = horario.dataset.fecha;


            // Actualizar resumen del turno

            if (horaTurno) {
                horaTurno.textContent = hora;
            }


            if (fechaTurno && fecha) {

                const [anio, mes, dia] = fecha.split("-").map(Number);

                const fechaSeleccionada = new Date(
                    anio,
                    mes - 1,
                    dia
                );

                fechaTurno.textContent = formatearFecha(fechaSeleccionada);

            }

        });

    });


    // ==========================================
    // INICIALIZACIÓN
    // ==========================================

    const [anio, mes, dia] = fechaInicio.split("-").map(Number);

    const fechaInicial = new Date(
        anio,
        mes - 1,
        dia
    );

    const lunesInicial = obtenerLunes(fechaInicial);

    actualizarFechas(lunesInicial);


    if (selectorFecha) {
        selectorFecha.value = fechaInicio;
    }


    // ==========================================
    // ICONOS LUCIDE
    // ==========================================

    if (window.lucide) {
        window.lucide.createIcons();
    }

});
