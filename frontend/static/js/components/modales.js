/**
 * modales.js — manejo genérico de pop-ups.
 * Reutilizable en cualquier página que use los macros de components/modales.html
 *
 * Atributos soportados (event delegation, no hace falta onclick):
 *   data-abrir-modal="id"   -> abre el modal
 *   data-cerrar-modal="id"  -> cierra el modal
 * Además cierra con Escape y al hacer click en el fondo oscuro.
 *
 * Dispara el evento "modal:abierto" en document por si otra página
 * necesita reaccionar (por ejemplo, cerrar menús desplegables).
 */
(function () {
    "use strict";

    function refrescarIconos() {
        if (typeof lucide !== "undefined") {
            lucide.createIcons();
        }
    }

    function abrirModal(id) {
        var modal = document.getElementById(id);
        if (!modal) return;

        // Un solo modal abierto a la vez
        document.querySelectorAll(".modal-overlay.flex").forEach(function (abierto) {
            if (abierto.id !== id) {
                abierto.classList.add("hidden");
                abierto.classList.remove("flex");
            }
        });

        modal.classList.remove("hidden");
        modal.classList.add("flex");
        document.body.classList.add("overflow-hidden");

        document.dispatchEvent(new CustomEvent("modal:abierto", { detail: { id: id } }));
        refrescarIconos();
    }

    function cerrarModal(id) {
        var modal = document.getElementById(id);
        if (!modal) return;

        modal.classList.add("hidden");
        modal.classList.remove("flex");

        if (!document.querySelector(".modal-overlay.flex")) {
            document.body.classList.remove("overflow-hidden");
        }
    }

    function cerrarTodos() {
        document.querySelectorAll(".modal-overlay.flex").forEach(function (modal) {
            cerrarModal(modal.id);
        });
    }

    // Disponibles globalmente por si se necesitan desde otro script
    window.abrirModal = abrirModal;
    window.cerrarModal = cerrarModal;

    document.addEventListener("click", function (event) {
        var abrir = event.target.closest("[data-abrir-modal]");
        if (abrir) {
            abrirModal(abrir.dataset.abrirModal);
            return;
        }

        var cerrar = event.target.closest("[data-cerrar-modal]");
        if (cerrar) {
            cerrarModal(cerrar.dataset.cerrarModal);
            return;
        }

        // Click en el fondo oscuro (el overlay en sí, no la tarjeta)
        if (event.target.classList.contains("modal-overlay")) {
            cerrarModal(event.target.id);
        }
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            cerrarTodos();
        }
    });
})();
