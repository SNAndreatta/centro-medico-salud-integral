document.addEventListener("DOMContentLoaded", function () {

    // Elementos del filtro de médicos
    const botonFiltrarMedicos = document.getElementById("botonFiltrarMedicos");
    const filtroMedicos = document.getElementById("filtroMedicos");
    const buscarMedico = document.getElementById("buscarMedico");

    // Elementos del filtro de especialidades
    const botonFiltrarEspecialidades = document.getElementById("botonFiltrarEspecialidades");
    const filtroEspecialidades = document.getElementById("filtroEspecialidades");
    const buscarEspecialidad = document.getElementById("buscarEspecialidad");


    // Mostrar u ocultar filtros
    botonFiltrarMedicos.addEventListener("click", function () {
        filtroMedicos.classList.toggle("hidden");

        if (!filtroMedicos.classList.contains("hidden")) {
            buscarMedico.focus();
        }
    });

    botonFiltrarEspecialidades.addEventListener("click", function () {
        filtroEspecialidades.classList.toggle("hidden");

        if (!filtroEspecialidades.classList.contains("hidden")) {
            buscarEspecialidad.focus();
        }
    });


    // Buscar médicos
    buscarMedico.addEventListener("input", function () {

        const busqueda = buscarMedico.value.trim().toLowerCase();
        const tarjetas = document.querySelectorAll("[data-filtro-medico]");
        let encontrados = 0;

        tarjetas.forEach(function (tarjeta) {

            const nombre = tarjeta.dataset.texto;
            const coincide = nombre.includes(busqueda);

            tarjeta.classList.toggle("hidden", !coincide);

            if (coincide) {
                encontrados++;
            }

        });

        document.getElementById("sinMedicos").classList.toggle(
            "hidden",
            encontrados > 0
        );

    });


    // Buscar especialidades
    buscarEspecialidad.addEventListener("input", function () {

        const busqueda = buscarEspecialidad.value.trim().toLowerCase();
        const tarjetas = document.querySelectorAll("[data-filtro-especialidad]");
        let encontrados = 0;

        tarjetas.forEach(function (tarjeta) {

            const nombre = tarjeta.dataset.texto;
            const coincide = nombre.includes(busqueda);

            tarjeta.classList.toggle("hidden", !coincide);

            if (coincide) {
                encontrados++;
            }

        });

        document.getElementById("sinEspecialidades").classList.toggle(
            "hidden",
            encontrados > 0
        );

    });


    // Inicializar iconos
    if (typeof lucide !== "undefined") {
        lucide.createIcons();
    }

});