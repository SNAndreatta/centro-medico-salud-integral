document.addEventListener("DOMContentLoaded", function () {

    // =================================
    // ABRIR Y CERRAR POPUPS
    // =================================

    window.abrirModal = function (id) {
        const modal = document.getElementById(id);

        if (modal) {
            modal.classList.remove("hidden");
            modal.classList.add("flex");
        }
    };

    window.cerrarModal = function () {
        document.querySelectorAll(".modal").forEach(function (modal) {
            modal.classList.add("hidden");
            modal.classList.remove("flex");
        });
    };

    // Cerrar al hacer clic fuera del contenido
    document.querySelectorAll(".modal").forEach(function (modal) {
        modal.addEventListener("click", function (evento) {
            if (evento.target === modal) {
                cerrarModal();
            }
        });
    });

    // Cerrar con Escape
    document.addEventListener("keydown", function (evento) {
        if (evento.key === "Escape") {
            cerrarModal();
        }
    });


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
    // SELECTOR DE MÉDICOS
    // =================================

    window.alternarSelector = function (id) {
        const selector = document.getElementById(id);

        if (!selector) return;

        selector.classList.toggle("hidden");
    };

    // Actualizar el texto del selector de creación
    const selectorCrear = document.getElementById("selector-medicos-crear");
    const textoMedicosCrear = document.getElementById("texto-medicos-crear");

    if (selectorCrear && textoMedicosCrear) {

        const casillas = selectorCrear.querySelectorAll('input[name="medicos"]');

        function actualizarTextoMedicos() {
            const seleccionados = Array.from(casillas).filter(function (casilla) {
                return casilla.checked;
            });

            if (seleccionados.length === 0) {
                textoMedicosCrear.textContent = "MÉDICOS";
            } else {
                textoMedicosCrear.textContent =
                    seleccionados.length + " MÉDICO(S) SELECCIONADO(S)";
            }
        }

        casillas.forEach(function (casilla) {
            casilla.addEventListener("change", actualizarTextoMedicos);
        });
    }

    // Cerrar selector al hacer clic fuera
    document.addEventListener("click", function (evento) {
        if (!evento.target.closest(".selector-medicos") &&
            !evento.target.closest("[onclick^='alternarSelector']")) {

            document.querySelectorAll(".selector-medicos").forEach(function (selector) {
                selector.classList.add("hidden");
            });
        }
    });


    // =================================
    // BUSCADOR
    // =================================

    const buscador = document.getElementById("buscadorEspecialidad");
    const filas = document.querySelectorAll(".fila-especialidad");
    const sinResultados = document.getElementById("sinResultados");

    if (buscador) {
        buscador.addEventListener("input", function () {

            const texto = buscador.value.toLowerCase().trim();
            let cantidadVisibles = 0;

            filas.forEach(function (fila) {
                const contenido = fila.dataset.busqueda.toLowerCase();
                const coincide = contenido.includes(texto);

                fila.classList.toggle("hidden", !coincide);

                if (coincide) {
                    cantidadVisibles++;
                }
            });

            sinResultados.classList.toggle("hidden", cantidadVisibles > 0);
        });
    }


    // =================================
    // ICONOS
    // =================================

    lucide.createIcons();

});