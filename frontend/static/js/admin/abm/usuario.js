document.addEventListener("DOMContentLoaded", function () {

    // =================================
    // POPUP CREAR USUARIO
    // =================================

    const modal = document.getElementById("modalCrearUsuario");
    const botonCrear = document.querySelector("button[onclick='abrirModalUsuario()']");

    window.abrirModalUsuario = function () {
        modal.classList.remove("hidden");
        modal.classList.add("flex");
    };

    window.cerrarModalUsuario = function () {
        modal.classList.add("hidden");
        modal.classList.remove("flex");
    };

    // Cerrar al hacer clic fuera del formulario
    modal.addEventListener("click", function (evento) {
        if (evento.target === modal) {
            cerrarModalUsuario();
        }
    });

    // Cerrar con Escape
    document.addEventListener("keydown", function (evento) {
        if (evento.key === "Escape") {
            cerrarModalUsuario();
        }
    });


    // =================================
    // BUSCADOR Y FILTRO POR ROL
    // =================================

    const buscador = document.getElementById("buscadorUsuario");
    const filtroRol = document.getElementById("filtroRol");
    const filas = document.querySelectorAll(".fila-usuario");
    const sinResultados = document.getElementById("sinResultados");

    function filtrarUsuarios() {

        const texto = buscador.value.toLowerCase().trim();
        const rolSeleccionado = filtroRol.value.toLowerCase();

        let cantidadVisibles = 0;

        filas.forEach(function (fila) {

            const nombre = fila.dataset.nombre;
            const rol = fila.dataset.rol;
            const id = fila.dataset.id;

            const coincideNombre =
                nombre.includes(texto) || id.includes(texto);

            const coincideRol =
                rolSeleccionado === "" || rol === rolSeleccionado;

            const mostrar = coincideNombre && coincideRol;

            fila.classList.toggle("hidden", !mostrar);

            if (mostrar) {
                cantidadVisibles++;
            }
        });

        sinResultados.classList.toggle("hidden", cantidadVisibles > 0);
    }

    buscador.addEventListener("input", filtrarUsuarios);
    filtroRol.addEventListener("change", filtrarUsuarios);


    // =================================
    // ICONOS
    // =================================

    lucide.createIcons();

});