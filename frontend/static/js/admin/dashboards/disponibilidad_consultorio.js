document.addEventListener("DOMContentLoaded", function () {

    const botones = document.querySelectorAll(".boton-consultorio");

    botones.forEach(function (boton) {

        boton.addEventListener("click", function () {

            const idDetalle = boton.getAttribute("aria-controls");
            const detalle = document.getElementById(idDetalle);
            const icono = boton.querySelector(".icono-consultorio");

            const estaAbierto = boton.getAttribute("aria-expanded") === "true";

            // Cierra el consultorio que estuviera abierto.
            botones.forEach(function (otroBoton) {

                if (otroBoton === boton) {
                    return;
                }

                const otroDetalle = document.getElementById(
                    otroBoton.getAttribute("aria-controls")
                );

                if (otroDetalle) {
                    otroDetalle.classList.add("hidden");
                }

                otroBoton.setAttribute("aria-expanded", "false");

                const otroIcono = otroBoton.querySelector(".icono-consultorio");

                if (otroIcono) {
                    otroIcono.classList.remove("rotate-180");
                }

            });

            // Abre o cierra el consultorio seleccionado.
            if (detalle) {
                detalle.classList.toggle("hidden", estaAbierto);
            }

            boton.setAttribute("aria-expanded", String(!estaAbierto));

            if (icono) {
                icono.classList.toggle("rotate-180", !estaAbierto);
            }

        });

    });


    // Inicializar iconos
    if (typeof lucide !== "undefined") {
        lucide.createIcons();
    }

});
