/**
 * menu_perfil.js — menú desplegable del avatar del header.
 *
 * Abre y cierra el cartel con las opciones "Perfil" y "Cerrar sesión".
 * Se cierra al hacer clic afuera, con Escape o al abrir otro modal.
 */
(function () {
    "use strict";

    var boton = document.getElementById("boton-menu-perfil");
    var menu = document.getElementById("menu-perfil-opciones");

    if (!boton || !menu) return;

    function cerrar() {
        menu.classList.add("hidden");
        boton.setAttribute("aria-expanded", "false");
    }

    function alternar() {
        if (!menu.classList.contains("hidden")) {
            cerrar();
            return;
        }

        menu.classList.remove("hidden");
        boton.setAttribute("aria-expanded", "true");

        if (typeof lucide !== "undefined") {
            lucide.createIcons();
        }
    }

    boton.addEventListener("click", function (evento) {
        evento.stopPropagation();
        alternar();
    });

    document.addEventListener("click", function (evento) {
        if (
            !menu.contains(evento.target) &&
            !boton.contains(evento.target)
        ) {
            cerrar();
        }
    });

    document.addEventListener("keydown", function (evento) {
        if (evento.key === "Escape") {
            cerrar();
        }
    });

    document.addEventListener("modal:abierto", cerrar);
})();
