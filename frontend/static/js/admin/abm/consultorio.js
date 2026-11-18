
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


    // Cerrar todos los menús.
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


    // Cerrar menú al hacer clic fuera.
    document.addEventListener("click", function (event) {

        if (
            !event.target.closest(".menu-consultorio") &&
            !event.target.closest(".boton-menu")
        ) {
            cerrarMenus();
        }

    });


    // =========================================
    // ABRIR MODALES
    // =========================================

    window.abrirModal = function (id) {

        const modal = document.getElementById(id);

        if (!modal) {
            console.error("No se encontró el modal:", id);
            return;
        }

        cerrarMenus();

        // Cerramos otros modales antes de abrir uno nuevo.
        document.querySelectorAll(".modal-overlay").forEach(function (otroModal) {

            otroModal.classList.add("hidden");
            otroModal.classList.remove("flex");

        });

        modal.classList.remove("hidden");
        modal.classList.add("flex");

        document.body.classList.add("overflow-hidden");

        // Inicializar iconos del modal.
        if (window.lucide) {
            window.lucide.createIcons();
        }

    };


    // =========================================
    // CERRAR MODALES
    // =========================================

    window.cerrarModal = function (id) {

        const modal = document.getElementById(id);

        if (!modal) return;

        modal.classList.add("hidden");
        modal.classList.remove("flex");

        // Restaurar scroll si no hay otro modal abierto.
        const modalAbierto = document.querySelector(".modal-overlay.flex");

        if (!modalAbierto) {
            document.body.classList.remove("overflow-hidden");
        }

    };


    // =========================================
    // CERRAR AL HACER CLIC EN EL FONDO
    // =========================================

    window.cerrarSiFondo = function (event, id) {

        if (event.target === event.currentTarget) {
            cerrarModal(id);
        }

    };


    // =========================================
    // CERRAR CON ESCAPE
    // =========================================

    document.addEventListener("keydown", function (event) {

        if (event.key === "Escape") {

            cerrarMenus();

            document.querySelectorAll(".modal-overlay.flex").forEach(function (modal) {
                cerrarModal(modal.id);
            });

        }

    });


    // =========================================
    // BUSCADOR DE CONSULTORIOS
    // =========================================

    const buscador = document.getElementById("buscadorConsultorio");

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
