document.addEventListener('DOMContentLoaded', () => {
    const formulario = document.getElementById('form-turno');
    if (!formulario) return;

    const campoFecha = document.getElementById('campo-fecha');
    const campoHora = document.getElementById('campo-hora');
    const textoResumen = document.getElementById('texto-resumen-turno');
    const errorCalendario = document.getElementById('error-calendario');
    const btnConfirmar = document.querySelector('#form-turno button[name="accion"][value="continuar"]');

    function actualizarCampos(fecha, hora) {
        campoFecha.value = fecha;
        campoHora.value = hora;
        textoResumen.textContent = fecha + ' a las ' + hora;
        errorCalendario.classList.add('hidden');
        if (btnConfirmar) btnConfirmar.disabled = false;
    }

    function limpiarCampos() {
        campoFecha.value = '';
        campoHora.value = '';
        textoResumen.textContent = 'Todavía no elegiste fecha ni horario';
        errorCalendario.classList.remove('hidden');
        if (btnConfirmar) btnConfirmar.disabled = true;
    }

    // Escuchar selección de horario del componente (evento custom)
    document.addEventListener('turno-seleccionado-paciente', (e) => {
        const { fecha, hora } = e.detail || {};
        if (fecha && hora) actualizarCampos(fecha, hora);
    });

    // Si viene fecha/hora de sesión, aplicarlas
    const { fechaSeleccionada, horaSeleccionada } = formulario.dataset;
    if (fechaSeleccionada && horaSeleccionada) {
        actualizarCampos(fechaSeleccionada, horaSeleccionada);
    } else {
        limpiarCampos();
    }

    // Validación al enviar
    formulario.addEventListener('submit', (evento) => {
        const accion = evento.submitter ? evento.submitter.value : 'continuar';
        if (accion === 'anterior') return;
        if (!campoFecha.value || !campoHora.value) {
            evento.preventDefault();
            errorCalendario.classList.remove('hidden');
        }
    });
});