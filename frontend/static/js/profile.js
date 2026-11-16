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

            const isPassword = input.type === "password";
            input.type = isPassword ? "text" : "password";

            // Toggle icons
            const eyeOff = button.querySelector('[data-lucide="eye-off"]');
            const eye = button.querySelector('[data-lucide="eye"]');
            if (eyeOff && eye) {
                eyeOff.classList.toggle("hidden", !isPassword);
                eye.classList.toggle("hidden", isPassword);
            }

        });
    });

    // Validar cambio de contraseña
    passwordForm?.addEventListener("submit", (event) => {
        const actual = document.getElementById("password-actual");
        const nueva = document.getElementById("nueva-password");
        const repetir = document.getElementById("confirmar-password");

        if (!actual?.value || !nueva?.value || !repetir?.value) {
            event.preventDefault();
            alert("Completá todos los campos para cambiar la contraseña.");
            return;
        }

        if (nueva.value !== repetir.value) {
            event.preventDefault();
            alert("La contraseña nueva y su confirmación no coinciden.");
            repetir.focus();
        }
    });

    // Selector de coberturas para médicos (agregar coberturas)
    const botonSelectorCoberturas = document.getElementById("botonSelectorCoberturasPerfil");
    const selectorCoberturas = document.getElementById("selector-coberturas-perfil");
    const textoCoberturas = document.getElementById("texto-coberturas-perfil");

    window.alternarSelector = function (id) {
        const panel = document.getElementById(id);
        if (!panel) return;

        panel.classList.toggle("hidden");
    };

    function actualizarTextoCoberturas() {
        if (!selectorCoberturas || !textoCoberturas) return;

        const seleccionadas = selectorCoberturas.querySelectorAll(
            'input[name="coberturas"]:checked'
        );

        if (seleccionadas.length === 0) {
            textoCoberturas.textContent = "Coberturas";
        } else if (seleccionadas.length === 1) {
            const nombre = seleccionadas[0]
                .closest("label")
                ?.querySelector("span")
                ?.textContent.trim();

            textoCoberturas.textContent = nombre || "1 cobertura seleccionada";
        } else {
            textoCoberturas.textContent =
                seleccionadas.length + " coberturas seleccionadas";
        }
    }

    selectorCoberturas
        ?.querySelectorAll('input[name="coberturas"]')
        .forEach((checkbox) => {
            checkbox.addEventListener("change", actualizarTextoCoberturas);
        });

    // Cerrar el desplegable al hacer clic fuera.
    document.addEventListener("click", (event) => {
        if (!selectorCoberturas || !botonSelectorCoberturas) return;

        if (
            !selectorCoberturas.contains(event.target) &&
            !botonSelectorCoberturas.contains(event.target)
        ) {
            selectorCoberturas.classList.add("hidden");
        }
    });

    // Cerrarlo también cuando se abre el modal.
    document.addEventListener("modal:abierto", () => {
        selectorCoberturas?.classList.add("hidden");
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