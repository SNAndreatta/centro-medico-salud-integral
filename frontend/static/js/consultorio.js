document.addEventListener("DOMContentLoaded", function () {

    // Elementos del modal
    const modal = document.getElementById("modalConsultorio");
    const botonAbrir = document.getElementById("abrirModal");
    const botonCerrar = document.getElementById("cerrarModal");

    // Abrir modal
    botonAbrir.addEventListener("click", function () {
        modal.classList.remove("hidden");
        modal.classList.add("flex");
    });

    // Cerrar modal
    function cerrarModal() {
        modal.classList.add("hidden");
        modal.classList.remove("flex");
    }

    botonCerrar.addEventListener("click", cerrarModal);

    // Cerrar al hacer clic fuera del formulario
    modal.addEventListener("click", function (evento) {
        if (evento.target === modal) {
            cerrarModal();
        }
    });

    // Cerrar con Escape
    document.addEventListener("keydown", function (evento) {
        if (evento.key === "Escape") {
            cerrarModal();
        }
    });

    // Buscador
    const buscador = document.getElementById("buscadorConsultorio");
    const filas = document.querySelectorAll(".fila-consultorio");
    const sinResultados = document.getElementById("sinResultados");

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

    // Menú de opciones
    const botonesMenu = document.querySelectorAll(".boton-menu");

    botonesMenu.forEach(function (boton) {
        boton.addEventListener("click", function () {
            const menu = boton.nextElementSibling;
            const estabaAbierto = !menu.classList.contains("hidden");

            // Cerrar todos los menús
            document.querySelectorAll(".menu-consultorio").forEach(function (otroMenu) {
                otroMenu.classList.add("hidden");
            });

            // Abrir el seleccionado si estaba cerrado
            if (!estabaAbierto) {
                menu.classList.remove("hidden");
            }
        });
    });

    // Cerrar los menús al hacer clic fuera de ellos
    document.addEventListener("click", function (evento) {
        if (!evento.target.closest(".boton-menu") &&
            !evento.target.closest(".menu-consultorio")) {

            document.querySelectorAll(".menu-consultorio").forEach(function (menu) {
                menu.classList.add("hidden");
            });
        }
    });

    // Inicializar iconos
    lucide.createIcons();
});