/**
 * usuario_profile.js — lógica propia del perfil de usuario (vista admin).
 *
 * Abrir/cerrar modales lo maneja modales.js (data-abrir-modal / data-cerrar-modal).
 * Este archivo reemplaza a medico.js en esta página.
 */
document.addEventListener("DOMContentLoaded", function () {

    // =================================
    // SELECTOR DE COBERTURAS (popup editar)
    // =================================

    const botonSelector = document.getElementById("botonSelectorCoberturas");
    const selector = document.getElementById("selector-coberturas");
    const textoCoberturas = document.getElementById("texto-coberturas");

    // La usa el onclick del botón en el HTML.
    window.alternarSelector = function (id) {
        const panel = document.getElementById(id);
        if (!panel) return;

        panel.classList.toggle("hidden");
    };

    function actualizarTextoCoberturas() {
        if (!selector || !textoCoberturas) return;

        const seleccionadas = selector.querySelectorAll(
            'input[name="coberturas"]:checked'
        );

        if (seleccionadas.length === 0) {
            textoCoberturas.textContent = "Coberturas";
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

    selector
        ?.querySelectorAll('input[name="coberturas"]')
        .forEach(function (checkbox) {
            checkbox.addEventListener("change", actualizarTextoCoberturas);
        });

    // Cerrar el desplegable al hacer clic fuera.
    document.addEventListener("click", function (evento) {
        if (!selector || !botonSelector) return;

        if (
            !selector.contains(evento.target) &&
            !botonSelector.contains(evento.target)
        ) {
            selector.classList.add("hidden");
        }
    });

    // Cerrarlo también cuando se abre otro modal.
    document.addEventListener("modal:abierto", function () {
        selector?.classList.add("hidden");
    });


    // =================================
    // CANCELAR ELIMINAR -> VUELVE A EDITAR
    // =================================

    document.addEventListener("click", function (evento) {
        const cancelar = evento.target.closest(
            '[data-cerrar-modal="modalEliminarUsuario"]'
        );

        if (cancelar && window.abrirModal && document.getElementById("modalEditarUsuario")) {
            window.abrirModal("modalEditarUsuario");
        }
    });


    // =================================
    // BUSCADOR DE COBERTURAS DEL MÉDICO
    // =================================

    const buscadorCobertura = document.getElementById("buscadorCobertura");
    const filasCobertura = document.querySelectorAll(".fila-cobertura");
    const sinResultadosCobertura = document.getElementById("sinResultadosCobertura");

    buscadorCobertura?.addEventListener("input", function () {
        const texto = buscadorCobertura.value.toLowerCase().trim();
        let visibles = 0;

        filasCobertura.forEach(function (fila) {
            const nombre = (fila.dataset.busqueda || "").toLowerCase();
            const coincide = nombre.includes(texto);

            fila.classList.toggle("hidden", !coincide);

            if (coincide) visibles++;
        });

        sinResultadosCobertura?.classList.toggle("hidden", visibles > 0);
    });


    // =================================
    // VALIDAR FECHAS DE LA AGENDA
    // =================================

    const fechaInicio = document.getElementById("fechaInicioAgenda");
    const fechaHasta = document.getElementById("fechaHastaAgenda");
    const errorFechas = document.getElementById("errorFechasAgenda");

    function validarFechasAgenda() {
        if (!fechaInicio || !fechaHasta) return true;

        // La fecha final no puede ser anterior a la inicial.
        fechaHasta.min = fechaInicio.value;

        const invalidas =
            fechaInicio.value !== "" &&
            fechaHasta.value !== "" &&
            fechaHasta.value < fechaInicio.value;

        errorFechas?.classList.toggle("hidden", !invalidas);

        fechaHasta.setCustomValidity(
            invalidas
                ? "La fecha de finalización debe ser igual o posterior a la fecha de inicio."
                : ""
        );

        return !invalidas;
    }

    fechaInicio?.addEventListener("change", validarFechasAgenda);
    fechaHasta?.addEventListener("change", validarFechasAgenda);

    const formularioAgenda = document
        .getElementById("modalCrearAgenda")
        ?.querySelector("form");

    formularioAgenda?.addEventListener("submit", function (evento) {
        if (!validarFechasAgenda()) {
            evento.preventDefault();
            fechaHasta?.reportValidity();
        }
    });


    // =================================
    // ICONOS LUCIDE
    // =================================

    if (typeof lucide !== "undefined") {
        lucide.createIcons();
    }

});