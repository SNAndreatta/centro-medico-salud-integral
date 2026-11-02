
document.addEventListener("DOMContentLoaded", function () {

    // =========================================
    // DESPLEGAR / OCULTAR CONSULTORIOS
    // =========================================

    document.addEventListener("click", function (event) {

        const boton = event.target.closest(".boton-consultorio");

        // Si el clic no fue sobre un consultorio, no hacemos nada.
        if (!boton) return;

        // Obtenemos el identificador del panel correspondiente.
        const idDetalle = boton.getAttribute("aria-controls");

        const detalle = document.getElementById(idDetalle);

        // Verificamos que exista el panel.
        if (!detalle) {
            console.error(
                "No se encontró el detalle del consultorio:",
                idDetalle
            );
            return;
        }

        // Comprobamos si el consultorio ya estaba abierto.
        const estabaAbierto =
            boton.getAttribute("aria-expanded") === "true";


        // =========================================
        // CERRAR TODOS LOS CONSULTORIOS
        // =========================================

        document.querySelectorAll(".boton-consultorio").forEach(function (otroBoton) {

            const otroId = otroBoton.getAttribute("aria-controls");

            const otroDetalle = document.getElementById(otroId);

            if (otroDetalle) {
                otroDetalle.classList.add("hidden");
            }

            otroBoton.setAttribute("aria-expanded", "false");

            const otroIcono = otroBoton.querySelector(".icono-consultorio");

            if (otroIcono) {
                otroIcono.classList.remove("rotate-180");
            }

        });


        // =========================================
        // ABRIR EL CONSULTORIO SELECCIONADO
        // =========================================

        if (!estabaAbierto) {

            detalle.classList.remove("hidden");

            boton.setAttribute("aria-expanded", "true");

            const icono = boton.querySelector(".icono-consultorio");

            if (icono) {
                icono.classList.add("rotate-180");
            }

        }

    });


    // =========================================
    // ICONOS LUCIDE
    // =========================================

    if (window.lucide) {
        window.lucide.createIcons();
    }

});
