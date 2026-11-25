
document.addEventListener("DOMContentLoaded", () => {

    if (window.lucide) {
        window.lucide.createIcons();
    }

    const botonFiltros = document.querySelector("#boton-filtros");
    const panelFiltros = document.querySelector("#panel-filtros");
    const filtroEspecialidad = document.querySelector("#filtro-especialidad");
    const filtroMedico = document.querySelector("#filtro-medico");
    const filtroEstado = document.querySelector("#filtro-estado");
    const aplicarFiltros = document.querySelector("#aplicar-filtros");
    const limpiarFiltros = document.querySelector("#limpiar-filtros");
    const tarjetas = document.querySelectorAll(".turno-card");
    const mensajeVacio = document.querySelector("#sin-resultados");

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
        panelFiltros.classList.contains("hidden") ? abrirPanelFiltros() : cerrarPanelFiltros();
    }

    if (botonFiltros && panelFiltros) {
        botonFiltros.addEventListener("click", (event) => {
            event.preventDefault();
            event.stopPropagation();
            alternarPanelFiltros();
        });
    }

    function filtrarTurnos() {
        const especialidad = filtroEspecialidad ? filtroEspecialidad.value.toLowerCase().trim() : "";
        const medico = filtroMedico ? filtroMedico.value.toLowerCase().trim() : "";
        const estado = filtroEstado ? filtroEstado.value.toLowerCase().trim() : "";
        let turnosVisibles = 0;

        tarjetas.forEach((tarjeta) => {
            const especialidadTurno = (tarjeta.dataset.especialidad || "").toLowerCase().trim();
            const medicoTurno = (tarjeta.dataset.medico || "").toLowerCase().trim();
            const estadoTurno = (tarjeta.dataset.estado || "").toLowerCase().trim();
            const coincideEspecialidad = especialidad === "" || especialidadTurno === especialidad;
            const coincideMedico = medico === "" || medicoTurno === medico;
            const coincideEstado = estado === "" || estadoTurno === estado;
            const coincide = coincideEspecialidad && coincideMedico && coincideEstado;
            tarjeta.classList.toggle("hidden", !coincide);
            if (coincide) turnosVisibles++;
        });

        if (mensajeVacio) {
            mensajeVacio.classList.toggle("hidden", turnosVisibles > 0);
        }
    }

    if (aplicarFiltros) {
        aplicarFiltros.addEventListener("click", (event) => {
            event.preventDefault();
            filtrarTurnos();
            cerrarPanelFiltros();
        });
    }

    if (limpiarFiltros) {
        limpiarFiltros.addEventListener("click", (event) => {
            event.preventDefault();
            if (filtroEspecialidad) filtroEspecialidad.value = "";
            if (filtroMedico) filtroMedico.value = "";
            if (filtroEstado) filtroEstado.value = "";
            filtrarTurnos();
            cerrarPanelFiltros();
        });
    }

    document.addEventListener("click", (event) => {
        if (!panelFiltros || !botonFiltros) return;
        if (!panelFiltros.contains(event.target) && !botonFiltros.contains(event.target)) {
            cerrarPanelFiltros();
        }
    });

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape") cerrarPanelFiltros();
    });

});
