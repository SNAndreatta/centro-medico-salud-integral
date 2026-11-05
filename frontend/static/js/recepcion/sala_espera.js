document.addEventListener("DOMContentLoaded", () => {

    // ==========================================
    // ELEMENTOS DEL DOM
    // ==========================================

    const botonFiltros = document.getElementById("boton-filtros");
    const panelFiltros = document.getElementById("panel-filtros");

    const filtroEspecialidad = document.getElementById("filtro-especialidad");

    const aplicarFiltros = document.getElementById("aplicar-filtros");
    const limpiarFiltros = document.getElementById("limpiar-filtros");

    const tarjetas = document.querySelectorAll(".tarjeta-paciente");

    const sinResultados = document.getElementById("sinResultados");


    // ==========================================
    // NORMALIZAR TEXTO
    // ==========================================

    function normalizarTexto(texto) {

        return texto
            .toLowerCase()
            .trim()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "");

    }


    // ==========================================
    // ABRIR PANEL
    // ==========================================

    function abrirPanelFiltros() {

        if (!panelFiltros || !botonFiltros) return;

        panelFiltros.classList.remove("hidden");

        botonFiltros.setAttribute("aria-expanded", "true");

    }


    // ==========================================
    // CERRAR PANEL
    // ==========================================

    function cerrarPanelFiltros() {

        if (!panelFiltros || !botonFiltros) return;

        panelFiltros.classList.add("hidden");

        botonFiltros.setAttribute("aria-expanded", "false");

    }


    // ==========================================
    // ALTERNAR PANEL
    // ==========================================

    function alternarPanelFiltros() {

        if (!panelFiltros) return;

        const estaAbierto = !panelFiltros.classList.contains("hidden");

        if (estaAbierto) {
            cerrarPanelFiltros();
        } else {
            abrirPanelFiltros();
        }

    }


    if (botonFiltros) {

        botonFiltros.addEventListener("click", (event) => {

            event.preventDefault();
            event.stopPropagation();

            alternarPanelFiltros();

        });

    }


    // ==========================================
    // FILTRAR PACIENTES
    // ==========================================

    function filtrarPacientes() {

        const especialidadSeleccionada = filtroEspecialidad
            ? normalizarTexto(filtroEspecialidad.value)
            : "";

        let pacientesVisibles = 0;


        tarjetas.forEach((tarjeta) => {

            const especialidadPaciente = normalizarTexto(
                tarjeta.dataset.especialidad || ""
            );


            // Comprobar si coincide la especialidad.
            const coincide =
                especialidadSeleccionada === "" ||
                especialidadPaciente === especialidadSeleccionada;


            // Mostrar u ocultar paciente.
            tarjeta.style.display = coincide ? "" : "none";


            if (coincide) {
                pacientesVisibles++;
            }

        });


        // Mostrar mensaje cuando no hay coincidencias.
        if (sinResultados) {

            if (tarjetas.length > 0 && pacientesVisibles === 0) {

                sinResultados.classList.remove("hidden");
                sinResultados.classList.add("flex");

            } else {

                sinResultados.classList.add("hidden");
                sinResultados.classList.remove("flex");

            }

        }

    }


    // ==========================================
    // APLICAR FILTROS
    // ==========================================

    if (aplicarFiltros) {

        aplicarFiltros.addEventListener("click", (event) => {

            event.preventDefault();

            filtrarPacientes();

            cerrarPanelFiltros();

        });

    }


    // ==========================================
    // LIMPIAR FILTROS
    // ==========================================

    if (limpiarFiltros) {

        limpiarFiltros.addEventListener("click", (event) => {

            event.preventDefault();

            if (filtroEspecialidad) {
                filtroEspecialidad.value = "";
            }

            filtrarPacientes();

            cerrarPanelFiltros();

        });

    }


    // ==========================================
    // CERRAR AL HACER CLICK AFUERA
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
    // CERRAR CON ESCAPE
    // ==========================================

    document.addEventListener("keydown", (event) => {

        if (event.key === "Escape") {
            cerrarPanelFiltros();
        }

    });

});