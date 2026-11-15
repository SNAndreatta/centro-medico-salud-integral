document.addEventListener("DOMContentLoaded", function () {

    // =================================
    // POPUP CREAR USUARIO
    // =================================

    const modal = document.getElementById("modalCrearUsuario");

    window.abrirModalUsuario = function () {
        if (!modal) return;

        cerrarDropdownCoberturas();
        modal.classList.remove("hidden");
        modal.classList.add("flex");
    };

    window.cerrarModalUsuario = function () {
        if (!modal) return;

        cerrarDropdownCoberturas();
        modal.classList.add("hidden");
        modal.classList.remove("flex");
    };

    // Cerrar al hacer clic fuera del formulario
    modal?.addEventListener("click", function (evento) {
        if (evento.target === modal) {
            cerrarModalUsuario();
        }
    });

    // Cerrar con Escape (primero el desplegable, después el modal)
    document.addEventListener("keydown", function (evento) {
        if (evento.key !== "Escape") return;

        if (coberturasPanel && !coberturasPanel.classList.contains("hidden")) {
            cerrarDropdownCoberturas();
            return;
        }

        cerrarModalUsuario();
    });


    // =================================
    // DESPLEGABLE DE COBERTURAS
    // =================================

    const coberturasTrigger = document.getElementById("coberturasTrigger");
    const coberturasPanel = document.getElementById("coberturasPanel");
    const coberturasTexto = document.getElementById("coberturasTexto");
    const coberturasCheckboxes = document.querySelectorAll(
        'input[name="coberturas"]'
    );

    function actualizarTextoCoberturas() {
        if (!coberturasTrigger || !coberturasTexto || coberturasTrigger.disabled) {
            return;
        }

        const seleccionadas = [...coberturasCheckboxes].filter(
            (checkbox) => checkbox.checked
        );

        const nombres = seleccionadas
            .map((checkbox) => (checkbox.dataset.nombre || "").trim())
            .filter(Boolean);

        if (nombres.length === 0) {
            coberturasTexto.textContent = "Seleccionar coberturas";
            coberturasTexto.classList.add("text-acento/40");
            coberturasTexto.classList.remove("text-acento");
            coberturasTrigger.title = "";
            return;
        }

        const resumen = nombres.join(", ");

        coberturasTexto.textContent = resumen;
        coberturasTexto.classList.remove("text-acento/40");
        coberturasTexto.classList.add("text-acento");
        coberturasTrigger.title = resumen;
    }

    function cerrarDropdownCoberturas() {
        if (!coberturasPanel) return;

        coberturasPanel.classList.add("hidden");
        coberturasTrigger?.setAttribute("aria-expanded", "false");
        coberturasTrigger?.querySelector("svg")?.classList.remove("rotate-180");
    }

    function alternarDropdownCoberturas() {
        if (!coberturasPanel) return;

        const abierto = !coberturasPanel.classList.toggle("hidden");

        coberturasTrigger?.setAttribute("aria-expanded", String(abierto));
        coberturasTrigger
            ?.querySelector("svg")
            ?.classList.toggle("rotate-180", abierto);
    }

    coberturasTrigger?.addEventListener("click", function (evento) {
        evento.stopPropagation();
        alternarDropdownCoberturas();
    });

    coberturasPanel?.addEventListener("click", function (evento) {
        evento.stopPropagation();
    });

    coberturasCheckboxes.forEach(function (checkbox) {
        checkbox.addEventListener("change", actualizarTextoCoberturas);
    });

    document.addEventListener("click", function (evento) {
        if (!coberturasPanel || coberturasPanel.classList.contains("hidden")) {
            return;
        }

        if (coberturasPanel.contains(evento.target)) return;
        if (coberturasTrigger?.contains(evento.target)) return;

        cerrarDropdownCoberturas();
    });

    actualizarTextoCoberturas();


    // =================================
    // CAMPOS EXTRA SEGÚN EL ROL
    // =================================

    const selectRol = document.getElementById("idRolUsuario");
    const camposMedico = document.getElementById("camposMedico");
    const selectEspecialidad = document.getElementById("id_especialidad");
    const inputMatricula = document.getElementById("matricula");

    function actualizarCamposRol() {
        if (!selectRol || !camposMedico) return;

        // El rol médico (4) es el único que muestra datos adicionales.
        const esMedico = selectRol.value === "4";

        // Se usa display en línea para asegurar el grid (antes solo se
        // quitaba "hidden" y el fieldset quedaba como block).
        camposMedico.style.display = esMedico ? "grid" : "none";
        camposMedico.disabled = !esMedico;

        if (!esMedico) {
            cerrarDropdownCoberturas();
        }

        if (selectEspecialidad) selectEspecialidad.required = esMedico;
        if (inputMatricula) inputMatricula.required = esMedico;
    }

    selectRol?.addEventListener("change", actualizarCamposRol);
    actualizarCamposRol();


    // =================================
    // BUSCADOR Y FILTRO POR ROL
    // =================================

    const buscador = document.getElementById("buscadorUsuario");
    const filtroRol = document.getElementById("filtroRol");
    const filas = document.querySelectorAll(".fila-usuario");
    const sinResultados = document.getElementById("sinResultados");

    function filtrarUsuarios() {
        if (!buscador || !filtroRol) return;

        const texto = buscador.value.toLowerCase().trim();
        const rolSeleccionado = filtroRol.value.toLowerCase();

        let cantidadVisibles = 0;

        filas.forEach(function (fila) {

            const nombre = fila.dataset.nombre || "";
            const dni = fila.dataset.dni || "";
            const rol = fila.dataset.rol || "";
            const id = fila.dataset.id || "";

            const coincideNombre =
                nombre.includes(texto) || dni.includes(texto) || id.includes(texto);

            const coincideRol =
                rolSeleccionado === "" || rol === rolSeleccionado;

            const mostrar = coincideNombre && coincideRol;

            fila.classList.toggle("hidden", !mostrar);

            if (mostrar) {
                cantidadVisibles++;
            }
        });

        sinResultados?.classList.toggle("hidden", cantidadVisibles > 0);
    }

    buscador?.addEventListener("input", filtrarUsuarios);
    filtroRol?.addEventListener("change", filtrarUsuarios);


    // =================================
    // ICONOS
    // =================================

    if (typeof lucide !== "undefined") {
        lucide.createIcons();
    }

});