document.addEventListener("DOMContentLoaded", function () {

    // =================================
    // MENÚ DE FILTRO
    // =================================

    const botonFiltro = document.getElementById("botonFiltro");
    const menuFiltro = document.getElementById("menuFiltro");

    botonFiltro.addEventListener("click", function (evento) {
        evento.stopPropagation();
        menuFiltro.classList.toggle("hidden");
    });

    document.addEventListener("click", function (evento) {
        if (!menuFiltro.contains(evento.target) &&
            !botonFiltro.contains(evento.target)) {
            menuFiltro.classList.add("hidden");
        }
    });


    // =================================
    // FILTRAR TURNOS POR ESTADO
    // =================================

    const filtroEstado = document.getElementById("filtroEstado");
    const filas = document.querySelectorAll(".fila-turno");
    const sinResultados = document.getElementById("sinResultadosTurnos");

    filtroEstado.addEventListener("change", function () {

        const estadoSeleccionado = filtroEstado.value;

        let cantidadVisibles = 0;

        filas.forEach(function (fila) {

            const estado = fila.dataset.estado;

            const coincide =
                estadoSeleccionado === "" ||
                estado === estadoSeleccionado;

            fila.classList.toggle("hidden", !coincide);

            if (coincide) {
                cantidadVisibles++;
            }

        });

        sinResultados.classList.toggle("hidden", cantidadVisibles > 0);
    });


    // =================================
    // ICONOS
    // =================================

    lucide.createIcons();

});