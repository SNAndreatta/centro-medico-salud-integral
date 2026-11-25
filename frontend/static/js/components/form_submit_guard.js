document.addEventListener("submit", (event) => {
    const form = event.target;
    if (!(form instanceof HTMLFormElement) || event.defaultPrevented) return;

    const method = (form.getAttribute("method") || "get").toLowerCase();
    if (!["post", "put", "delete"].includes(method)) return;

    if (form.dataset.submitting === "true") {
        event.preventDefault();
        return;
    }

    form.dataset.submitting = "true";
    form.querySelectorAll(
        'button:not([type]), button[type="submit" i], input[type="submit" i], input[type="image" i]'
    ).forEach((button) => {
        button.disabled = true;
    });
});