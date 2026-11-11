
// ======================================
// MODAL: CREAR COBERTURA
// ======================================

function abrirModal(id) {
    const modal = document.getElementById(id);
    if (!modal) return;

    modal.classList.remove("hidden");
    modal.classList.add("flex");

    document.body.classList.add("overflow-hidden");

    if (typeof lucide !== "undefined") {
        lucide.createIcons();
    }

    const primerInput = modal.querySelector("input");
    if (primerInput) {
        primerInput.focus();
    }
}

function cerrarModal(id) {
    const modal = document.getElementById(id);
    if (!modal) return;

    modal.classList.add("hidden");
    modal.classList.remove("flex");

    if (!document.querySelector(".modal-overlay.flex")) {
        document.body.classList.remove("overflow-hidden");
    }
}

function cerrarSiFondo(event, id) {
    if (event.target === event.currentTarget) {
        cerrarModal(id);
    }
}


// ======================================
// CERRAR MODAL CON ESCAPE
// ======================================

document.addEventListener("keydown", function(event) {
    if (event.key === "Escape") {
        document.querySelectorAll(".modal-overlay.flex").forEach(function(modal) {
            cerrarModal(modal.id);
        });
    }
});


// ======================================
// BUSCADOR DE COBERTURAS
// ======================================

document.addEventListener("DOMContentLoaded", function() {

    const buscador = document.getElementById("buscar-cobertura");
    const filas = document.querySelectorAll(".fila-cobertura");
    const mensaje = document.getElementById("sin-coberturas");

    if (buscador && mensaje) {

        buscador.addEventListener("input", function() {

            const consulta = buscador.value.trim().toLowerCase();
            let visibles = 0;

            filas.forEach(function(fila) {

                const nombre = fila.dataset.nombre || "";
                const coincide = nombre.includes(consulta);

                fila.classList.toggle("hidden", !coincide);

                if (coincide) {
                    visibles++;
                }
            });

            mensaje.classList.toggle("hidden", visibles > 0);

        });
    }

    // Inicializar iconos
    if (typeof lucide !== "undefined") {
        lucide.createIcons();
    }

});
