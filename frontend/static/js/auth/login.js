document.addEventListener("DOMContentLoaded", () => {

    lucide.createIcons();

    // Mostrar u ocultar contraseña.
    const password = document.querySelector("#password");
    const togglePassword = document.querySelector("#toggle-password");

    togglePassword.addEventListener("click", () => {

        const mostrar = password.type === "password";

        password.type = mostrar ? "text" : "password";

        togglePassword.innerHTML = `
            <i data-lucide="${mostrar ? "eye-off" : "eye"}"
               class="h-[18px] w-[18px]"></i>
        `;

        togglePassword.setAttribute(
            "aria-label",
            mostrar ? "Ocultar contraseña" : "Mostrar contraseña"
        );

        togglePassword.setAttribute("aria-pressed", String(mostrar));

        lucide.createIcons();
    });

});