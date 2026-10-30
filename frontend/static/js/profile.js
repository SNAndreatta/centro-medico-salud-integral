const rolUsuario = document.body.dataset.rol;

if (rolUsuario === "medico") {
    console.log("Profile del médico");
}

if (rolUsuario === "recepcion") {
    console.log("Profile de recepción");
}

if (rolUsuario === "paciente") {
    console.log("Profile de paciente");
}

if (rolUsuario === "admin") {
    console.log("Profile de admin");
}