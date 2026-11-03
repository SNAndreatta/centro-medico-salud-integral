document.addEventListener("DOMContentLoaded", () => {

    const modal = document.getElementById("configuracion-modal");
    const openButton = document.getElementById("configuracion-perfil");
    const changeButton = document.getElementById("toggle-cambiar-password");
    const passwordSection = document.getElementById("seccion-cambiar-password");
    const passwordForm = document.getElementById("form-cambiar-password");

    // Abrir modal
    function openModal() {
        if (!modal) return;

        modal.classList.remove("hidden");
        modal.classList.add("flex");
        modal.setAttribute("aria-hidden", "false");

        document.body.classList.add("overflow-hidden");
    }

    // Cerrar modal
    function closeModal() {
        if (!modal) return;

        modal.classList.add("hidden");
        modal.classList.remove("flex");
        modal.setAttribute("aria-hidden", "true");

        document.body.classList.remove("overflow-hidden");

        openButton?.focus();
    }

    openButton?.addEventListener("click", openModal);

    document.getElementById("cerrar-configuracion")
        ?.addEventListener("click", closeModal);

    modal?.addEventListener("click", (event) => {
        if (event.target === modal) {
            closeModal();
        }
    });

    document.addEventListener("keydown", (event) => {
        if (
            event.key === "Escape" &&
            modal &&
            !modal.classList.contains("hidden")
        ) {
            closeModal();
        }
    });

    // Mostrar u ocultar campos para cambiar contraseña
    changeButton?.addEventListener("click", () => {

        passwordSection?.classList.toggle("hidden");

        const visible =
            passwordSection &&
            !passwordSection.classList.contains("hidden");

        changeButton.textContent = visible
            ? "Cancelar cambio"
            : "Cambiar contraseña";

        if (!visible) {
            passwordSection?.querySelectorAll("input").forEach((input) => {
                input.value = "";
                input.type = "password";
            });
        } else {
            document.getElementById("password-actual")?.focus();
        }
    });

    // Mostrar u ocultar contraseñas
    document.querySelectorAll(".toggle-password").forEach((button) => {

        button.addEventListener("click", () => {

            const input = document.getElementById(button.dataset.target);

            if (!input) return;

            input.type =
                input.type === "password"
                    ? "text"
                    : "password";

        });
    });

    // Validar cambio de contraseña
    passwordForm?.addEventListener("submit", (event) => {

        event.preventDefault();

        const actual = document.getElementById("password-actual");
        const nueva = document.getElementById("nueva-password");
        const repetir = document.getElementById("confirmar-password");

        if (!actual?.value || !nueva?.value || !repetir?.value) {

            alert("Completá todos los campos para cambiar la contraseña.");
            return;
        }

        if (nueva.value !== repetir.value) {

            alert("La contraseña nueva y su confirmación no coinciden.");
            repetir.focus();

            return;
        }

        alert(
            "Los datos son válidos. Falta conectar este formulario con la ruta del backend."
        );

    });

    // Confirmar eliminación de cuenta
    document.getElementById("eliminar-cuenta")
        ?.addEventListener("click", (event) => {

            if (!confirm(
                "¿Seguro que querés eliminar tu cuenta? Esta acción no se puede deshacer."
            )) {
                event.preventDefault();
            }

        });

    // Confirmar cancelación de turnos
    document.querySelectorAll(".cancelar-turno").forEach((button) => {

        button.addEventListener("click", (event) => {

            if (!confirm("¿Estás seguro de que querés cancelar este turno?")) {
                event.preventDefault();
            }

        });

    });

});