document.addEventListener("DOMContentLoaded", () => {

    // ==========================================
    // ICONOS LUCIDE
    // ==========================================

    if (window.lucide) {
        window.lucide.createIcons();
    }


    // ==========================================
    // ELEMENTOS DEL DOM
    // ==========================================

    const botonFiltros = document.querySelector("#boton-filtros");
    const panelFiltros = document.querySelector("#panel-filtros");

    const filtroFecha = document.querySelector("#filtro-fecha");
    const filtroEstado = document.querySelector("#filtro-estado");
    const filtroEspecialidad = document.querySelector("#filtro-especialidad");

    const aplicarFiltros = document.querySelector("#aplicar-filtros");
    const limpiarFiltros = document.querySelector("#limpiar-filtros");

    const tarjetas = document.querySelectorAll(".turno-card");
    const mensajeVacio = document.querySelector("#sin-resultados");


    // ==========================================
    // ABRIR Y CERRAR PANEL DE FILTROS
    // ==========================================

    function abrirPanelFiltros() {

        if (!panelFiltros || !botonFiltros) return;

        panelFiltros.classList.remove("hidden");

        botonFiltros.setAttribute("aria-expanded", "true");

    }


    function cerrarPanelFiltros() {

        if (!panelFiltros || !botonFiltros) return;

        panelFiltros.classList.add("hidden");

        botonFiltros.setAttribute("aria-expanded", "false");

    }


    function alternarPanelFiltros() {

        if (!panelFiltros) return;

        const estaAbierto = !panelFiltros.classList.contains("hidden");

        if (estaAbierto) {
            cerrarPanelFiltros();
        } else {
            abrirPanelFiltros();
        }

    }


    if (botonFiltros && panelFiltros) {

        botonFiltros.addEventListener("click", (event) => {

            event.preventDefault();
            event.stopPropagation();

            alternarPanelFiltros();

        });

    }


    // ==========================================
    // APLICAR FILTROS
    // ==========================================

    function filtrarTurnos() {

        const fecha = filtroFecha
            ? filtroFecha.value
            : "";

        const estado = filtroEstado
            ? filtroEstado.value.toLowerCase().trim()
            : "";

        const especialidad = filtroEspecialidad
            ? filtroEspecialidad.value.toLowerCase().trim()
            : "";

        let turnosVisibles = 0;


        tarjetas.forEach((tarjeta) => {

            const fechaTurno = (
                tarjeta.dataset.fecha || ""
            ).trim();

            const estadoTurno = (
                tarjeta.dataset.estado || ""
            ).toLowerCase().trim();

            const especialidadTurno = (
                tarjeta.dataset.especialidad || ""
            ).toLowerCase().trim();


            const coincideFecha =
                fecha === "" || fechaTurno === fecha;

            const coincideEstado =
                estado === "" || estadoTurno === estado;

            const coincideEspecialidad =
                especialidad === "" || especialidadTurno === especialidad;


            const coincide =
                coincideFecha &&
                coincideEstado &&
                coincideEspecialidad;


            tarjeta.classList.toggle("hidden", !coincide);


            if (coincide) {
                turnosVisibles++;
            }

        });


        // Mostrar mensaje cuando no hay resultados.

        if (mensajeVacio) {

            mensajeVacio.classList.toggle(
                "hidden",
                turnosVisibles > 0
            );

        }

    }


    // ==========================================
    // BOTÓN APLICAR FILTROS
    // ==========================================

    if (aplicarFiltros) {

        aplicarFiltros.addEventListener("click", (event) => {

            event.preventDefault();

            filtrarTurnos();

            cerrarPanelFiltros();

        });

    }


    // ==========================================
    // BOTÓN LIMPIAR FILTROS
    // ==========================================

    if (limpiarFiltros) {

        limpiarFiltros.addEventListener("click", (event) => {

            event.preventDefault();

            if (filtroFecha) {
                filtroFecha.value = "";
            }

            if (filtroEstado) {
                filtroEstado.value = "";
            }

            if (filtroEspecialidad) {
                filtroEspecialidad.value = "";
            }

            filtrarTurnos();

            cerrarPanelFiltros();

        });

    }


    // ==========================================
    // CERRAR PANEL AL HACER CLIC FUERA
    // ==========================================

    document.addEventListener("click", (event) => {

        if (!panelFiltros || !botonFiltros) return;

        const clicDentroDelPanel = panelFiltros.contains(event.target);
        const clicEnBoton = botonFiltros.contains(event.target);

        if (!clicDentroDelPanel && !clicEnBoton) {
            cerrarPanelFiltros();
        }

    });


    // ==========================================
    // CERRAR PANEL CON ESCAPE
    // ==========================================

    document.addEventListener("keydown", (event) => {

        if (event.key === "Escape") {
            cerrarPanelFiltros();
        }

    });

});
