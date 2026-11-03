document.addEventListener("DOMContentLoaded", function () {
        if (typeof lucide !== "undefined") {
            lucide.createIcons();
        }

        const configuracion = document.getElementById("configuracion-perfil");

        if (configuracion) {
            configuracion.addEventListener("click", function () {
                const datos = document.getElementById("datos-perfil");

                if (datos) {
                    datos.scrollIntoView({
                        behavior: "smooth",
                        block: "start"
                    });
                } else {
                    window.scrollTo({
                        top: document.body.scrollHeight,
                        behavior: "smooth"
                    });
                }
            });
        }

        document.querySelectorAll(".cancelar-turno").forEach(function (boton) {
            boton.addEventListener("click", function () {
                alert("La cancelación de turnos todavía no está conectada al backend.");
            });
        });
    });