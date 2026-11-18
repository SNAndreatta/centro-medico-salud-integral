document.addEventListener("DOMContentLoaded", function () {

    // =================================
    // FUNCIONES GENERALES PARA MODALES
    // =================================

    function abrirModal(modal) {
        if (!modal) return;

        modal.classList.remove("hidden");
        modal.classList.add("flex");
        modal.setAttribute("aria-hidden", "false");

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    function cerrarModal(modal) {
        if (!modal) return;

        modal.classList.add("hidden");
        modal.classList.remove("flex");
        modal.setAttribute("aria-hidden", "true");
    }


    // =================================
    // REFERENCIAS A LOS MODALES
    // =================================

    const modalEditar = document.getElementById("modalEditarMedico");
    const modalEliminar = document.getElementById("modalEliminarMedico");
    const modalAgenda = document.getElementById("modalCrearAgenda");


    // =================================
    // MODAL EDITAR MÉDICO
    // =================================

    const botonAbrirEditar = document.getElementById("abrirModalEditarMedico");
    const botonCerrarEditar = document.getElementById("cerrarModalEditarMedico");

    botonAbrirEditar?.addEventListener("click", function (event) {
        event.preventDefault();
        abrirModal(modalEditar);
    });

    botonCerrarEditar?.addEventListener("click", function () {
        cerrarModal(modalEditar);
    });


    // =================================
    // MODAL ELIMINAR MÉDICO
    // =================================

    const botonAbrirEliminar = document.getElementById(
        "abrirConfirmarEliminarMedico"
    );

    const botonCancelarEliminar = document.getElementById(
        "cancelarEliminarMedico"
    );

    botonAbrirEliminar?.addEventListener("click", function () {
        cerrarModal(modalEditar);
        abrirModal(modalEliminar);
    });

    botonCancelarEliminar?.addEventListener("click", function () {
        cerrarModal(modalEliminar);
        abrirModal(modalEditar);
    });


    // =================================
    // MODAL CREAR AGENDA
    // =================================

    const botonAbrirAgenda = document.getElementById("abrirModalCrearAgenda");
    const botonCerrarAgenda = document.getElementById("cerrarModalCrearAgenda");

    botonAbrirAgenda?.addEventListener("click", function () {
        abrirModal(modalAgenda);
    });

    botonCerrarAgenda?.addEventListener("click", function () {
        cerrarModal(modalAgenda);
    });


    // =================================
    // CERRAR MODALES AL HACER CLICK FUERA
    // =================================

    [modalEditar, modalEliminar, modalAgenda].forEach(function (modal) {

        modal?.addEventListener("click", function (event) {

            if (event.target === modal) {
                cerrarModal(modal);
            }

        });

    });


    // =================================
    // CERRAR MODALES CON ESCAPE
    // =================================

    document.addEventListener("keydown", function (event) {

        if (event.key === "Escape") {
            cerrarModal(modalEditar);
            cerrarModal(modalEliminar);
            cerrarModal(modalAgenda);
        }

    });


    // =================================
    // SELECTOR DE COBERTURAS
    // =================================

    const botonSelectorCoberturas = document.getElementById(
        "botonSelectorCoberturas"
    );

    const selectorCoberturas = document.getElementById(
        "selector-coberturas"
    );

    const textoCoberturas = document.getElementById("texto-coberturas");

    // Función utilizada por el onclick del botón en el HTML.
    window.alternarSelector = function (id) {

        const selector = document.getElementById(id);

        if (!selector) return;

        selector.classList.toggle("hidden");
    };


    // Actualizar el texto según las coberturas seleccionadas.
    function actualizarTextoCoberturas() {

        if (!selectorCoberturas || !textoCoberturas) return;

        const seleccionadas = selectorCoberturas.querySelectorAll(
            'input[name="coberturas"]:checked'
        );

        if (seleccionadas.length === 0) {

            textoCoberturas.textContent = "COBERTURAS";

        } else if (seleccionadas.length === 1) {

            const nombre = seleccionadas[0]
                .closest("label")
                ?.querySelector("span")
                ?.textContent.trim();

            textoCoberturas.textContent = nombre || "1 cobertura seleccionada";

        } else {

            textoCoberturas.textContent =
                seleccionadas.length + " coberturas seleccionadas";

        }
    }


    // Escuchar cambios en los checkboxes.
    selectorCoberturas?.querySelectorAll(
        'input[name="coberturas"]'
    ).forEach(function (checkbox) {

        checkbox.addEventListener("change", actualizarTextoCoberturas);

    });


    // Cerrar el selector al hacer clic fuera.
    document.addEventListener("click", function (event) {

        if (
            selectorCoberturas &&
            botonSelectorCoberturas &&
            !selectorCoberturas.contains(event.target) &&
            !botonSelectorCoberturas.contains(event.target)
        ) {
            selectorCoberturas.classList.add("hidden");
        }

    });


    // =================================
    // BUSCADOR DE COBERTURAS
    // =================================

    const buscadorCobertura = document.getElementById("buscadorCobertura");

    const filasCobertura = document.querySelectorAll(".fila-cobertura");

    const sinResultadosCobertura = document.getElementById(
        "sinResultadosCobertura"
    );

    buscadorCobertura?.addEventListener("input", function () {

        const texto = buscadorCobertura.value.toLowerCase().trim();

        let cantidadVisibles = 0;

        filasCobertura.forEach(function (fila) {

            const nombre = (fila.dataset.busqueda || "").toLowerCase();

            const coincide = nombre.includes(texto);

            fila.classList.toggle("hidden", !coincide);

            if (coincide) {
                cantidadVisibles++;
            }

        });

        // Mostrar mensaje cuando no hay coincidencias.
        sinResultadosCobertura?.classList.toggle(
            "hidden",
            cantidadVisibles > 0
        );

    });


    // =================================
    // VALIDAR FECHAS DE LA AGENDA
    // =================================

    const fechaInicio = document.getElementById("fechaInicioAgenda");
    const fechaHasta = document.getElementById("fechaHastaAgenda");

    const errorFechas = document.getElementById("errorFechasAgenda");


    function validarFechasAgenda() {

        if (!fechaInicio || !fechaHasta) {
            return true;
        }

        // La fecha final no puede ser anterior a la inicial.
        fechaHasta.min = fechaInicio.value;

        const fechasInvalidas =
            fechaInicio.value !== "" &&
            fechaHasta.value !== "" &&
            fechaHasta.value < fechaInicio.value;

        errorFechas?.classList.toggle("hidden", !fechasInvalidas);

        fechaHasta.setCustomValidity(
            fechasInvalidas
                ? "La fecha de finalización debe ser igual o posterior a la fecha de inicio."
                : ""
        );

        return !fechasInvalidas;
    }


    fechaInicio?.addEventListener("change", validarFechasAgenda);
    fechaHasta?.addEventListener("change", validarFechasAgenda);


    // =================================
    // VALIDAR FORMULARIO DE CREAR AGENDA
    // =================================

    const formularioAgenda = modalAgenda?.querySelector("form");

    formularioAgenda?.addEventListener("submit", function (event) {

        if (!validarFechasAgenda()) {

            event.preventDefault();

            fechaHasta?.reportValidity();

        }

    });


    // =================================
    // ICONOS LUCIDE
    // =================================

    if (window.lucide) {
        lucide.createIcons();
    }

});