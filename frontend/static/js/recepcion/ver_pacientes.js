document.addEventListener("DOMContentLoaded", () => {
    if (window.lucide) {
        window.lucide.createIcons();
    }

    const buscador = document.querySelector("#buscar-paciente");
    const tarjetas = document.querySelectorAll(".paciente-card");
    const mensajeVacio = document.querySelector("#sin-resultados");

    if (buscador) {
        buscador.addEventListener("input", () => {
            const busqueda = buscador.value.toLowerCase().trim();
            let visibles = 0;

            tarjetas.forEach((tarjeta) => {
                const nombre = (tarjeta.dataset.nombre || "").toLowerCase();
                const cobertura = (tarjeta.dataset.cobertura || "").toLowerCase();
                const coincide = nombre.includes(busqueda) || cobertura.includes(busqueda);

                tarjeta.classList.toggle("hidden", !coincide);
                if (coincide) visibles++;
            });

            if (mensajeVacio) {
                mensajeVacio.classList.toggle("hidden", visibles !== 0);
            }
        });
    }
});
