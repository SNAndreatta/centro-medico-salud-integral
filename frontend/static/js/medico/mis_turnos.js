
document.addEventListener("DOMContentLoaded", () => {

    // ==========================================
    // ELEMENTOS DEL DOM
    // ==========================================

    const botonFiltros = document.querySelector("#boton-filtros");
    const panelFiltros = document.querySelector("#panel-filtros");
    const contenedorTurnos = document.querySelector("#turnos");

    const filtroFecha = document.querySelector("#filtro-fecha");
    const filtroCobertura = document.querySelector("#filtro-cobertura");
    const filtroEstado = document.querySelector("#filtro-estado");

    const aplicarFiltros = document.querySelector("#aplicar-filtros");
    const limpiarFiltros = document.querySelector("#limpiar-filtros");

    const tarjetas = document.querySelectorAll(".turno-card");
    const mensajeVacio = document.querySelector("#sin-resultados");
    const cantidadTurnos = document.querySelector("#cantidad-turnos");

    // Fecha de hoy (hora local del centro médico).
    const hoy = contenedorTurnos ? contenedorTurnos.dataset.hoy || "" : "";



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

        const cobertura = filtroCobertura
            ? filtroCobertura.value.toLowerCase().trim()
            : "";
        const estado = filtroEstado
            ? filtroEstado.value.toLowerCase().trim()
            : "";

        let turnosVisibles = 0;


        tarjetas.forEach((tarjeta) => {

            const fechaTurno = (
                tarjeta.dataset.fecha || ""
            ).trim();

            const coberturaTurno = (
                tarjeta.dataset.cobertura || ""
            ).toLowerCase().trim();
            const estadoTurno = (
                tarjeta.dataset.estado || ""
            ).toLowerCase().trim();


            const coincideFecha =
                fecha === "" || fechaTurno === fecha;

            const coincideCobertura =
                cobertura === "" || coberturaTurno === cobertura;
            const coincideEstado =
                estado === "" || estadoTurno === estado;


            const coincide =
                coincideFecha &&
                coincideCobertura &&
                coincideEstado;


            tarjeta.classList.toggle("hidden", !coincide);


            if (coincide) {
                turnosVisibles++;
            }


            // "Marcar como atendido" sólo se muestra para los turnos del día
            // de la fecha filtrada (hoy si no se filtró por fecha).

            const botonMarcar = tarjeta.querySelector(".boton-marcar-atendido");

            if (botonMarcar) {

                const dentroDeRango =
                    tarjeta.dataset.marcable === "true";

                const esDelDia =
                    fecha === ""
                        ? fechaTurno === hoy
                        : fechaTurno === fecha;

                botonMarcar.classList.toggle(
                    "hidden",
                    !(dentroDeRango && esDelDia)
                );

            }

        });


        // Actualizar cantidad de turnos.

        if (cantidadTurnos) {
            cantidadTurnos.textContent = turnosVisibles;
        }


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

            if (filtroCobertura) {
                filtroCobertura.value = "";
            }

            if (filtroEstado) {
                filtroEstado.value = "";
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


    // ==========================================
    // FILTRADO INICIAL
    // ==========================================
    // Deja los botones de "Marcar como atendido" según la fecha de hoy
    // (o la que esté filtrada).

    filtrarTurnos();

});

