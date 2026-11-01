document.addEventListener("DOMContentLoaded", function () {

    // =================================
    // BUSCADOR DE MÉDICOS
    // =================================

    const buscador_medico = document.getElementById("buscadorMedico");
    const filas_medico = document.querySelectorAll(".fila-medico");
    const sinResultados_medico = document.getElementById("sinResultados");

    buscador_medico.addEventListener("input", function () {

        const texto = buscador_medico.value.toLowerCase().trim();

        let cantidadVisibles = 0;

        filas_medico.forEach(function (fila) {

            const contenido = fila.dataset.busqueda.toLowerCase();

            const coincide = contenido.includes(texto);

            fila.classList.toggle("hidden", !coincide);

            if (coincide) {
                cantidadVisibles++;
            }

        });

        sinResultados_medico.classList.toggle("hidden", cantidadVisibles > 0);

    });

    // =================================
    // BUSCADOR DE COBERTURAS
    // =================================

    const buscador_cobertura = document.getElementById("buscadorCobertura");
    const filas_cobertura = document.querySelectorAll(".fila-cobertura");
    const sinResultados_cobertura = document.getElementById("sinResultados");

    buscador_cobertura.addEventListener("input", function () {

        const texto = buscador_cobertura.value.toLowerCase().trim();

        let cantidadVisibles = 0;

        filas_cobertura.forEach(function (fila) {

            const nombre = fila.dataset.busqueda;

            const coincide = nombre.includes(texto);

            fila.classList.toggle("hidden", !coincide);

            if (coincide) {
                cantidadVisibles++;
            }

        });

        sinResultados_cobertura.classList.toggle("hidden", cantidadVisibles > 0);

    });


    // =================================
    // ICONOS
    // =================================

    lucide.createIcons();

});
