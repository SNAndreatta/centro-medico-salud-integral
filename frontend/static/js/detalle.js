/**
 * detalle_cobertura.js — comportamiento propio de la página de detalle de cobertura:
 *  - menú desplegable (⋮) de cada plan
 *  - buscadores de planes y médicos
 *
 * Requiere modales.js para los pop-ups.
 */
(function () {
    "use strict";

    /* ---------- Menú de opciones de cada plan ---------- */

    function cerrarMenus() {
        document.querySelectorAll("[data-menu]").forEach(function (menu) {
            menu.classList.add("hidden");
        });
    }

    function alternarMenu(id) {
        var menu = document.getElementById(id);
        if (!menu) return;

        var estabaAbierto = !menu.classList.contains("hidden");
        cerrarMenus();

        if (!estabaAbierto) {
            menu.classList.remove("hidden");
        }
    }

    document.addEventListener("click", function (event) {
        var boton = event.target.closest("[data-alternar-menu]");

        if (boton) {
            alternarMenu(boton.dataset.alternarMenu);
            return;
        }

        // Click fuera de un menú: se cierran todos
        if (!event.target.closest("[data-menu]")) {
            cerrarMenus();
        }
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") cerrarMenus();
    });

    // Al abrir cualquier modal (p. ej. desde el menú) se cierran los menús
    document.addEventListener("modal:abierto", cerrarMenus);


    /* ---------- Buscadores ---------- */

    function configurarBuscador(inputId, filaSelector, mensajeId) {
        var input = document.getElementById(inputId);
        var filas = document.querySelectorAll(filaSelector);
        var mensaje = document.getElementById(mensajeId);

        if (!input || !mensaje) return;

        input.addEventListener("input", function () {
            var consulta = input.value.trim().toLowerCase();
            var visibles = 0;

            filas.forEach(function (fila) {
                var coincide = (fila.dataset.nombre || "").includes(consulta);
                fila.classList.toggle("hidden", !coincide);
                if (coincide) visibles++;
            });

            mensaje.classList.toggle("hidden", visibles > 0);
        });
    }

    document.addEventListener("DOMContentLoaded", function () {
        configurarBuscador("buscar-plan", ".fila-plan", "sin-planes");
        configurarBuscador("buscar-medico", ".fila-medico", "sin-medicos");

        if (typeof lucide !== "undefined") {
            lucide.createIcons();
        }
    });
})();