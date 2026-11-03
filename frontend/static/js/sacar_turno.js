document.addEventListener("DOMContentLoaded", function () {

    // ==========================================
    // INICIALIZAR ICONOS DE LUCIDE
    // ==========================================

    function inicializarIconos() {
        if (typeof lucide !== "undefined") {
            lucide.createIcons();
        }
    }

    inicializarIconos();


    // ==========================================
    // BUSCADOR DE ESPECIALIDADES
    // ==========================================

    const buscador = document.getElementById("buscar-especialidad");
    const tarjetas = document.querySelectorAll(".tarjeta-especialidad");
    const mensaje = document.getElementById("sin-resultados");

    // Solo se ejecuta en el paso 1, donde existe el buscador.
    if (buscador && mensaje) {

        buscador.addEventListener("input", function () {

            const consulta = buscador.value.trim().toLowerCase();
            let visibles = 0;

            tarjetas.forEach(function (tarjeta) {

                const nombre = tarjeta.dataset.nombre || "";
                const coincide = nombre.includes(consulta);

                tarjeta.classList.toggle("hidden", !coincide);

                if (coincide) {
                    visibles++;
                }

            });

            mensaje.classList.toggle("hidden", visibles !== 0);

        });

    }

});