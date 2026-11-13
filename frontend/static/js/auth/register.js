document.addEventListener("DOMContentLoaded", () => {

    lucide.createIcons();

    // Mostrar u ocultar contraseñas.
    document.querySelectorAll(".toggle-password").forEach((button) => {

        button.addEventListener("click", () => {

            const input = document.getElementById(button.dataset.target);
            const mostrar = input.type === "password";

            input.type = mostrar ? "text" : "password";

            button.innerHTML = `
                <i data-lucide="${mostrar ? "eye-off" : "eye"}"
                   class="h-[18px] w-[18px]"></i>
            `;

            button.setAttribute(
                "aria-label",
                mostrar ? "Ocultar contraseña" : "Mostrar contraseña"
            );

            button.setAttribute("aria-pressed", String(mostrar));

            lucide.createIcons();
        });

    });

    const form = document.querySelector("#register-form");
    const submitButton = form?.querySelector('button[type="submit"]');
    const password = document.querySelector("#password");
    const confirmPassword = document.querySelector("#confirm-password");
    const message = document.querySelector("#register-message");

    if (!form || !submitButton || !password || !confirmPassword) {
        return;
    }

    const fechaNacimiento = document.querySelector("#fecha_nacimiento");
    const hoy = new Date();
    hoy.setHours(0, 0, 0, 0);

    if (fechaNacimiento) {
        const mes = String(hoy.getMonth() + 1).padStart(2, "0");
        const dia = String(hoy.getDate()).padStart(2, "0");
        fechaNacimiento.max = `${hoy.getFullYear()}-${mes}-${dia}`;
    }

    const patronEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    const campos = [
        {
            input: document.querySelector("#first-name"),
            validar: (valor) => {
                const nombre = valor.trim();
                if (!nombre) return "Ingresá tu nombre.";
                if (nombre.length > 100) return "El nombre no puede superar los 100 caracteres.";
                return "";
            },
        },
        {
            input: document.querySelector("#last-name"),
            validar: (valor) => {
                const apellido = valor.trim();
                if (!apellido) return "Ingresá tu apellido.";
                if (apellido.length > 100) return "El apellido no puede superar los 100 caracteres.";
                return "";
            },
        },
        {
            input: fechaNacimiento,
            validar: (valor) => {
                if (!valor) return "Ingresá tu fecha de nacimiento.";

                const [anio, mes, dia] = valor.split("-").map(Number);
                const fecha = new Date(anio, mes - 1, dia);

                if (
                    fecha.getFullYear() !== anio ||
                    fecha.getMonth() !== mes - 1 ||
                    fecha.getDate() !== dia
                ) {
                    return "Ingresá una fecha válida.";
                }

                if (fecha > hoy) return "La fecha de nacimiento no puede ser futura.";
                return "";
            },
        },
        {
            input: document.querySelector("#dni"),
            validar: (valor) => {
                if (!/^\d{7,8}$/.test(valor.trim())) {
                    return "El DNI debe tener entre 7 y 8 números.";
                }
                return "";
            },
        },
        {
            input: document.querySelector("#email"),
            validar: (valor) => {
                const correo = valor.trim();
                if (!correo) return "Ingresá tu correo electrónico.";
                if (correo.length > 150 || !patronEmail.test(correo)) {
                    return "Ingresá un correo electrónico válido.";
                }
                return "";
            },
        },
        {
            input: password,
            validar: (valor) => {
                if (valor.length < 8) return "La contraseña debe tener al menos 8 caracteres.";
                if (valor.length > 256) return "La contraseña es demasiado larga.";
                return "";
            },
        },
        {
            input: confirmPassword,
            validar: (valor) => {
                if (!valor) return "Repetí tu contraseña.";
                if (valor !== password.value) return "Las contraseñas no coinciden.";
                return "";
            },
        },
    ].filter((campo) => campo.input);

    const aplicarEstado = (campo) => {
        const error = campo.validar(campo.input.value);
        const mostrarError = campo.touched && Boolean(error);
        const wrapper = campo.input.parentElement;

        wrapper.classList.toggle("border-red-500", mostrarError);
        wrapper.classList.toggle("border-slate-200", !mostrarError);
        wrapper.classList.toggle("bg-red-50", mostrarError);
        wrapper.classList.toggle("bg-white", !mostrarError);

        campo.error.textContent = mostrarError ? error : "";
        campo.error.classList.toggle("hidden", !mostrarError);

        campo.input.setAttribute("aria-invalid", String(mostrarError));

        return !error;
    };

    const actualizarFormulario = () => {
        let formularioValido = true;

        campos.forEach((campo) => {
            if (!aplicarEstado(campo)) {
                formularioValido = false;
            }
        });

        submitButton.disabled = !formularioValido;
        submitButton.classList.toggle("opacity-60", !formularioValido);
        submitButton.classList.toggle("pointer-events-none", !formularioValido);

        return formularioValido;
    };

    campos.forEach((campo) => {
        campo.touched = false;

        campo.error = document.createElement("p");
        campo.error.className = "mt-1 hidden text-xs text-red-600";
        campo.input.parentElement.insertAdjacentElement("afterend", campo.error);

        campo.input.addEventListener("input", actualizarFormulario);
        campo.input.addEventListener("blur", () => {
            campo.touched = true;
            actualizarFormulario();
        });
        campo.input.addEventListener("change", () => {
            campo.touched = true;
            actualizarFormulario();
        });
    });

    form.addEventListener("submit", (event) => {
        message.classList.add("hidden");

        campos.forEach((campo) => {
            campo.touched = true;
        });

        if (!actualizarFormulario()) {
            event.preventDefault();

            const primerCampoInvalido = campos.find((campo) => campo.validar(campo.input.value));

            if (primerCampoInvalido) {
                primerCampoInvalido.input.focus();
            }

            return;
        }

        // Si los datos son válidos, el formulario se envía normalmente
        // mediante POST a frontend/routes/auth.py.
        submitButton.disabled = true;
        submitButton.classList.add("opacity-60", "pointer-events-none");
    });

    actualizarFormulario();
});
