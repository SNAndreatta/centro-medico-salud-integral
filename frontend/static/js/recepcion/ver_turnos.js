
document.addEventListener("DOMContentLoaded", () => {

    // ==========================================
    // ICONOS LUCIDE
    // ==========================================

    if (window.lucide) {
        window.lucide.createIcons();
    }


    // ==========================================
    // ELEMENTOS DEL PANEL DE FILTROS
    // ==========================================

    const botonFiltros = document.querySelector("#boton-filtros");
    const panelFiltros = document.querySelector("#panel-filtros");

    const filtroCobertura = document.querySelector("#filtro-cobertura");
    const filtroMedico = document.querySelector("#filtro-medico");

    const aplicarFiltros = document.querySelector("#aplicar-filtros");
    const limpiarFiltros = document.querySelector("#limpiar-filtros");

    const tarjetas = document.querySelectorAll(".turno-card");
    const mensajeVacio = document.querySelector("#sin-resultados");


    // ==========================================
    // ABRIR Y CERRAR PANEL DE FILTROS
    // ==========================================

    function cerrarPanelFiltros() {

        if (!panelFiltros || !botonFiltros) return;

        panelFiltros.classList.add("hidden");

        botonFiltros.setAttribute("aria-expanded", "false");

    }


    if (botonFiltros && panelFiltros) {

        botonFiltros.addEventListener("click", (event) => {

            event.stopPropagation();

            panelFiltros.classList.toggle("hidden");

            const abierto = !panelFiltros.classList.contains("hidden");

            botonFiltros.setAttribute("aria-expanded", String(abierto));

        });

    }


    // ==========================================
    // APLICAR FILTROS
    // ==========================================

    function filtrarTurnos() {

        if (!filtroCobertura || !filtroMedico) return;

        const cobertura = filtroCobertura.value.toLowerCase().trim();
        const medico = filtroMedico.value.toLowerCase().trim();

        let turnosVisibles = 0;


        tarjetas.forEach((tarjeta) => {

            const coberturaTurno = (
                tarjeta.dataset.cobertura || ""
            ).toLowerCase().trim();

            const medicoTurno = (
                tarjeta.dataset.medico || ""
            ).toLowerCase().trim();


            const coincideCobertura =
                cobertura === "" || coberturaTurno === cobertura;

            const coincideMedico =
                medico === "" || medicoTurno === medico;

            const coincide = coincideCobertura && coincideMedico;


            tarjeta.classList.toggle("hidden", !coincide);


            if (coincide) {
                turnosVisibles++;
            }

        });


        // Mostrar mensaje si no hay resultados

        if (mensajeVacio) {

            mensajeVacio.classList.toggle(
                "hidden",
                turnosVisibles !== 0
            );

        }

    }


    // ==========================================
    // BOTÓN APLICAR FILTROS
    // ==========================================

    if (aplicarFiltros) {

        aplicarFiltros.addEventListener("click", () => {

            filtrarTurnos();

            cerrarPanelFiltros();

        });

    }


    // ==========================================
    // BOTÓN LIMPIAR FILTROS
    // ==========================================

    if (limpiarFiltros) {

        limpiarFiltros.addEventListener("click", () => {

            if (filtroCobertura) {
                filtroCobertura.value = "";
            }

            if (filtroMedico) {
                filtroMedico.value = "";
            }

            filtrarTurnos();

            cerrarPanelFiltros();

        });

    }


    // ==========================================
    // CERRAR PANEL AL HACER CLIC FUERA
    // ==========================================

    document.addEventListener("click", (event) => {

        if (
            panelFiltros &&
            botonFiltros &&
            !panelFiltros.contains(event.target) &&
            !botonFiltros.contains(event.target)
        ) {

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
