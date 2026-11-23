
document.addEventListener("DOMContentLoaded", function () {

    // =========================================
    // MENÚ DE TRES PUNTOS
    // =========================================

    window.alternarMenu = function (id, boton) {

        const menu = document.getElementById(id);

        if (!menu) return;

        const estabaAbierto = !menu.classList.contains("hidden");

        cerrarMenus();

        if (!estabaAbierto) {

            menu.classList.remove("hidden");

            if (boton) {
                boton.setAttribute("aria-expanded", "true");
            }

        }

    };


    // =========================================
    // CERRAR TODOS LOS MENÚS
    // =========================================

    window.cerrarMenus = function () {

        document.querySelectorAll(".menu-consultorio").forEach(function (menu) {

            menu.classList.add("hidden");

            const contenedor = menu.parentElement;

            if (contenedor) {

                const boton = contenedor.querySelector(".boton-menu");

                if (boton) {
                    boton.setAttribute("aria-expanded", "false");
                }

            }

        });

    };


    // =========================================
    // CERRAR MENÚ AL HACER CLIC AFUERA
    // =========================================

    document.addEventListener("click", function (event) {

        if (
            !event.target.closest(".menu-consultorio") &&
            !event.target.closest(".boton-menu")
        ) {
            cerrarMenus();
        }

    });


    // =========================================
    // CERRAR MENÚ ANTES DE ABRIR UN MODAL
    // =========================================

    document.addEventListener("click", function (event) {

        const botonModal = event.target.closest("[data-abrir-modal]");

        if (botonModal) {
            cerrarMenus();
        }

    });


    // =========================================
    // CERRAR MENÚ CUANDO SE ABRE UN MODAL
    // =========================================

    document.addEventListener("modal:abierto", function () {
        cerrarMenus();
    });


    // =========================================
    // BUSCADOR DE CONSULTORIOS
    // =========================================

    const buscador = document.getElementById("buscar-consultorio");

    const filas = document.querySelectorAll(".fila-consultorio");

    const sinResultados = document.getElementById("sinResultados");


    if (buscador) {

        buscador.addEventListener("input", function () {

            const consulta = normalizarTexto(buscador.value);

            let cantidadVisible = 0;

            filas.forEach(function (fila) {

                const datos = normalizarTexto(
                    fila.dataset.busqueda || ""
                );

                const coincide = datos.includes(consulta);

                fila.classList.toggle("hidden", !coincide);

                if (coincide) {
                    cantidadVisible++;
                }

            });


            // Mostrar mensaje cuando no hay coincidencias.
            if (sinResultados) {

                sinResultados.classList.toggle(
                    "hidden",
                    cantidadVisible > 0
                );

            }

        });

    }


    // =========================================
    // NORMALIZAR TEXTO
    // =========================================

    function normalizarTexto(texto) {

        return texto
            .toLowerCase()
            .trim()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "");

    }


    // =========================================
    // ICONOS LUCIDE
    // =========================================

    if (window.lucide) {
        window.lucide.createIcons();
    }

});
