const rolUsuario = document.body.dataset.rol;

if (rolUsuario === "medico") {
    console.log("Home del médico");
}

if (rolUsuario === "recepcion") {
    console.log("Home de recepción");
}

if (rolUsuario === "paciente") {
    console.log("Home de paciente");
}

if (rolUsuario === "admin") {
    console.log("Home de admin");
}