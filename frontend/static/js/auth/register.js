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

    // Validar que ambas contraseñas coincidan.
    const form = document.querySelector("#register-form");
    const password = document.querySelector("#password");
    const confirmPassword = document.querySelector("#confirm-password");
    const message = document.querySelector("#register-message");

    form.addEventListener("submit", (event) => {

        message.classList.add("hidden");

        if (password.value !== confirmPassword.value) {

            event.preventDefault();

            message.textContent = "Las contraseñas no coinciden.";
            message.classList.remove("hidden");

            return;
        }

        // Si las contraseñas coinciden, el formulario se envía normalmente
        // mediante POST a frontend/routes/auth.py.
    });

});