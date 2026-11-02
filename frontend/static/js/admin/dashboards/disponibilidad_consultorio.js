document.addEventListener("DOMContentLoaded", function () {

    const botones = document.querySelectorAll(".boton-consultorio");

    botones.forEach(function (boton) {

        boton.addEventListener("click", function () {

            const idDetalle = boton.getAttribute("aria-controls");
            const detalle = document.getElementById(idDetalle);
            const icono = boton.querySelector(".icono-consultorio");

            const estaAbierto = boton.getAttribute("aria-expanded") === "true";

            detalle.classList.toggle("hidden");
            boton.setAttribute("aria-expanded", String(!estaAbierto));

            icono.classList.toggle("rotate-180");

        });

    });


    // Inicializar iconos
    if (typeof lucide !== "undefined") {
        lucide.createIcons();
    }

});