document.addEventListener("DOMContentLoaded", () => {

    // ==========================================
    // ICONOS LUCIDE
    // ==========================================

    if (window.lucide) {
        window.lucide.createIcons();
    }


    // ==========================================
    // BUSCADOR DE USUARIOS
    // ==========================================

    const buscador = document.querySelector("#buscar-usuario");
    const tarjetas = document.querySelectorAll(".usuario-card");
    const mensajeVacio = document.querySelector("#sin-resultados");

    if (buscador) {

        buscador.addEventListener("input", () => {

            const busqueda = buscador.value.toLowerCase().trim();

            let usuariosVisibles = 0;

            tarjetas.forEach((tarjeta) => {

                const nombre = (
                    tarjeta.dataset.nombre || ""
                ).toLowerCase();

                const cobertura = (
                    tarjeta.dataset.cobertura || ""
                ).toLowerCase();

                const coincide =
                    nombre.includes(busqueda) ||
                    cobertura.includes(busqueda);

                tarjeta.classList.toggle("hidden", !coincide);

                if (coincide) {
                    usuariosVisibles++;
                }

            });

            if (mensajeVacio) {
                mensajeVacio.classList.toggle(
                    "hidden",
                    usuariosVisibles !== 0
                );
            }

        });

    }

});