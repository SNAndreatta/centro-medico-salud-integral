
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

    const filtroCobertura = document.querySelector("#filtro-cobertura");
    const filtroMedico = document.querySelector("#filtro-medico");

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

        const cobertura = filtroCobertura
            ? filtroCobertura.value.toLowerCase().trim()
            : "";

        const medico = filtroMedico
            ? filtroMedico.value.toLowerCase().trim()
            : "";

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
