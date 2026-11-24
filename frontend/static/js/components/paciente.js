// Cerrar popup de reserva
function cerrarPopupReserva() {
    const popup = document.getElementById("popup-reserva");

    if (popup) {
        popup.remove();
    }
}

// Inicializar lucide icons al cargar
document.addEventListener("DOMContentLoaded", function () {
    if (typeof lucide !== "undefined") {
        lucide.createIcons();
    }
});
