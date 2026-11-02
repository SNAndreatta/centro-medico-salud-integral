document.addEventListener("DOMContentLoaded", function () {

    // =================================
    // ELEMENTOS
    // =================================

    const botonAnterior = document.getElementById("semanaAnterior");
    const botonSiguiente = document.getElementById("semanaSiguiente");
    const rangoSemana = document.getElementById("rangoSemana");

    const horarios = document.querySelectorAll(".horario-agenda");

    const horaTurno = document.getElementById("horaTurno");
    const fechaTurno = document.getElementById("fechaTurno");

    const datosAgenda = document.getElementById("datosAgenda");

    let fechaInicio = new Date(
        datosAgenda.dataset.fechaInicio + "T12:00:00"
    );


    // =================================
    // FORMATEAR FECHAS
    // =================================

    function formatearFecha(fecha) {
        const dia = String(fecha.getDate()).padStart(2, "0");
        const mes = String(fecha.getMonth() + 1).padStart(2, "0");
        const anio = fecha.getFullYear();

        return dia + " - " + mes + " - " + anio;
    }

    function formatearRango() {

        const fin = new Date(fechaInicio);
        fin.setDate(fin.getDate() + 5);

        const opciones = {
            day: "2-digit",
            month: "short"
        };

        const inicioTexto = fechaInicio
            .toLocaleDateString("es-AR", opciones)
            .toUpperCase();

        const finTexto = fin
            .toLocaleDateString("es-AR", opciones)
            .toUpperCase();

        rangoSemana.textContent = inicioTexto + " - " + finTexto;
    }


    // =================================
    // ACTUALIZAR FECHAS DE LOS HORARIOS
    // =================================

    function actualizarFechas() {

        horarios.forEach(function (horario) {

            const indiceDia = Number(horario.dataset.dia);

            const fecha = new Date(fechaInicio);
            fecha.setDate(fecha.getDate() + indiceDia);

            horario.dataset.fecha = formatearFecha(fecha);

        });

        formatearRango();
    }


    // =================================
    // CAMBIAR DE SEMANA
    // =================================

    botonAnterior.addEventListener("click", function () {

        fechaInicio.setDate(fechaInicio.getDate() - 7);

        actualizarFechas();

    });

    botonSiguiente.addEventListener("click", function () {

        fechaInicio.setDate(fechaInicio.getDate() + 7);

        actualizarFechas();

    });


    // =================================
    // SELECCIONAR HORARIO
    // =================================

    horarios.forEach(function (horario) {

        horario.addEventListener("click", function () {

            if (horario.dataset.disponible !== "true") {
                return;
            }

            // Quitar selección anterior
            horarios.forEach(function (otroHorario) {
                otroHorario.classList.remove("bg-[#003B5C]", "text-white");
                otroHorario.classList.add("bg-[#e7ecef]", "text-[#073B57]");
            });

            // Marcar horario seleccionado
            horario.classList.remove("bg-[#e7ecef]", "text-[#073B57]");
            horario.classList.add("bg-[#003B5C]", "text-white");

            // Actualizar turno seleccionado
            horaTurno.textContent = horario.dataset.hora;
            fechaTurno.textContent = horario.dataset.fecha;

        });

    });


    // =================================
    // INICIALIZAR
    // =================================

    actualizarFechas();
    lucide.createIcons();

});