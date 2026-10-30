const rolUsuario = document.body.dataset.rol;

if (rolUsuario === "medico") {
    console.log("Home del médico");
}

if (rolUsuario === "recepcion") {
    console.log("Home de recepción");
}