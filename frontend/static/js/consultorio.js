
document.addEventListener("DOMContentLoaded", function () {

    // Elementos del modal
    const modal = document.getElementById("modalConsultorio");
    const botonAbrir = document.getElementById("abrirModal");
    const botonCerrar = document.getElementById("cerrarModal");

    // Abrir cualquier modal por ID
    window.abrirModal = function (id) {
        const modalSeleccionado = document.getElementById(id);

        if (modalSeleccionado) {
            modalSeleccionado.classList.remove("hidden");
            modalSeleccionado.classList.add("flex");
        }
    };

    // Cerrar todos los modales
    window.cerrarModal = function () {
        document.querySelectorAll('[id^="modal"]').forEach(function (elemento) {
            elemento.classList.add("hidden");
            elemento.classList.remove("flex");
        });
    };

    // Botón crear
    if (botonAbrir) {
        botonAbrir.addEventListener("click", function () {
            window.abrirModal("modalConsultorio");
        });
    }

    // Botón X
    if (botonCerrar) {
        botonCerrar.addEventListener("click", function () {
            window.cerrarModal();
        });
    }

    // Cerrar al hacer clic fuera del modal
    if (modal) {
        modal.addEventListener("click", function (evento) {
            if (evento.target === modal) {
                window.cerrarModal();
            }
        });
    }

    // Cerrar con Escape
    document.addEventListener("keydown", function (evento) {
        if (evento.key === "Escape") {
            window.cerrarModal();
        }
    });

    // Buscador
    const buscador = document.getElementById("buscadorConsultorio");
    const filas = document.querySelectorAll(".fila-consultorio");
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

            if (sinResultados) {
                sinResultados.classList.toggle("hidden", cantidadVisibles > 0);
            }
        });
    }

    // Menú de opciones
    const botonesMenu = document.querySelectorAll(".boton-menu");

    botonesMenu.forEach(function (boton) {
        boton.addEventListener("click", function (evento) {
            evento.stopPropagation();

            const menu = boton.nextElementSibling;
            const estabaAbierto = !menu.classList.contains("hidden");

            document.querySelectorAll(".menu-consultorio").forEach(function (otroMenu) {
                otroMenu.classList.add("hidden");
            });

            if (!estabaAbierto) {
                menu.classList.remove("hidden");
            }
        });
    });

    // Cerrar menús al hacer clic afuera
    document.addEventListener("click", function (evento) {
        if (
            !evento.target.closest(".boton-menu") &&
            !evento.target.closest(".menu-consultorio")
        ) {
            document.querySelectorAll(".menu-consultorio").forEach(function (menu) {
                menu.classList.add("hidden");
            });
        }
    });

    // Inicializar iconos
    if (typeof lucide !== "undefined") {
        lucide.createIcons();
    }

});