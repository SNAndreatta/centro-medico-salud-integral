document.addEventListener("DOMContentLoaded", function () {

    // =================================
    // MENÚ DE TRES PUNTOS
    // =================================

    window.cerrarMenus = function () {
        document.querySelectorAll(".menu-especialidad").forEach(function (menu) {
            menu.classList.add("hidden");
        });
    };

    window.alternarMenu = function (id) {
        const menu = document.getElementById(id);

        if (!menu) return;

        const estabaAbierto = !menu.classList.contains("hidden");

        cerrarMenus();

        if (!estabaAbierto) {
            menu.classList.remove("hidden");
        }
    };

    // Cerrar menú al hacer clic fuera
    document.addEventListener("click", function (evento) {
        if (!evento.target.closest(".menu-especialidad") &&
            !evento.target.closest("[onclick^='alternarMenu']")) {
            cerrarMenus();
        }
    });


    // =================================
    // BUSCADOR
    // =================================

    const buscador = document.getElementById("buscadorEspecialidad");
    const filas = document.querySelectorAll(".fila-especialidad");
    const sinResultados = document.getElementById("sinResultados");

    if (buscador && sinResultados) {
        buscador.addEventListener("input", function () {

            const texto = normalizarTexto(buscador.value);
            let cantidadVisibles = 0;

            filas.forEach(function (fila) {
                const contenido = normalizarTexto(fila.dataset.busqueda || "");
                const coincide = contenido.includes(texto);

                fila.classList.toggle("hidden", !coincide);

                if (coincide) {
                    cantidadVisibles++;
                }
            });

            sinResultados.classList.toggle("hidden", cantidadVisibles > 0);
        });
    }

    function normalizarTexto(texto) {
        return texto
            .toLowerCase()
            .trim()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "");
    }


    // =================================
    // ICONOS
    // =================================

    if (typeof lucide !== "undefined") {
        lucide.createIcons();
    }

});
