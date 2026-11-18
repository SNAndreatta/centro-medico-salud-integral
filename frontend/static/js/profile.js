document.addEventListener("DOMContentLoaded", () => {

    const modal = document.getElementById("configuracion-modal");
    const openButton = document.getElementById("configuracion-perfil");
    const changeButton = document.getElementById("toggle-cambiar-password");
    const passwordSection = document.getElementById("seccion-cambiar-password");
    const passwordForm = document.getElementById("form-cambiar-password");
    const formEditarPerfil = document.getElementById("form-editar-perfil");

    // Abrir modal
    function openModal() {
        if (!modal) return;
        formEditarPerfil?.reset();
        modal.classList.remove("hidden");
        modal.classList.add("flex");
        modal.setAttribute("aria-hidden", "false");

        document.body.classList.add("overflow-hidden");
    }

    // Cerrar modal
    function closeModal() {
        if (!modal) return;
        formEditarPerfil?.reset();

        modal.classList.add("hidden");
        modal.classList.remove("flex");
        modal.setAttribute("aria-hidden", "true");

        document.body.classList.remove("overflow-hidden");

        openButton?.focus();
    }

    openButton?.addEventListener("click", openModal);

    document.getElementById("cerrar-configuracion")
        ?.addEventListener("click", closeModal);
    document.querySelector('[data-cerrar-modal="configuracion-modal"]')
        ?.addEventListener("click", () => formEditarPerfil?.reset());

    if (modal && formEditarPerfil) {
        const observer = new MutationObserver(() => {
            if (modal.classList.contains("hidden")) {
                formEditarPerfil.reset();
            }
        });
        observer.observe(modal, { attributes: true, attributeFilter: ["class"] });
    }

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

        if (!passwordSection) return;

        passwordSection.classList.toggle("hidden");

        const visible = !passwordSection.classList.contains("hidden");

        changeButton.textContent = visible
            ? "Cancelar cambio"
            : "Cambiar contraseña";

        if (!visible) {
            passwordSection.querySelectorAll("input").forEach((input) => {
                input.value = "";
                input.type = "password";
            });
        } else {
            document.getElementById("password-actual")?.focus();
            passwordSection.scrollIntoView({ block: "nearest", behavior: "smooth" });
        }
    });

    // Mostrar u ocultar contraseñas (botón del ojo).
    // El ícono se reemplaza en cada clic para que siempre coincida
    // con el estado real del input (eye-off = oculta, eye = muestra).
    document.querySelectorAll(".toggle-password").forEach((button) => {

        button.addEventListener("click", () => {

            const input = document.getElementById(button.dataset.target);

            if (!input) return;

            const mostrar = input.type === "password";

            input.type = mostrar ? "text" : "password";

            button.innerHTML =
                `<i data-lucide="${mostrar ? "eye-off" : "eye"}" class="h-4 w-4"></i>`;

            if (typeof lucide !== "undefined") {
                lucide.createIcons();
            }

            button.setAttribute(
                "aria-label",
                mostrar ? "Ocultar contraseña" : "Mostrar contraseña"
            );

            button.setAttribute("aria-pressed", String(mostrar));

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