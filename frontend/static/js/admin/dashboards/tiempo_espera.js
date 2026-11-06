
document.addEventListener('DOMContentLoaded', () => {

    // ==========================================
    // NORMALIZAR TEXTO
    // ==========================================

    function normalizarTexto(texto) {
        return texto
            .toLowerCase()
            .trim()
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "");
    }


    // ==========================================
    // BUSCADOR DE MÉDICOS
    // ==========================================

    const buscarMedico = document.getElementById('buscarMedico');
    const medicos = document.querySelectorAll('.medico-card');
    const sinMedicos = document.getElementById('sin-medicos');

    if (buscarMedico) {

        buscarMedico.addEventListener('input', () => {

            const busqueda = normalizarTexto(buscarMedico.value);
            let encontrados = 0;

            medicos.forEach(medico => {

                const nombre = normalizarTexto(medico.dataset.search || "");
                const coincide = nombre.includes(busqueda);

                medico.classList.toggle('hidden', !coincide);

                if (coincide) {
                    encontrados++;
                }

            });

            if (sinMedicos) {
                sinMedicos.classList.toggle('hidden', encontrados > 0);
            }

        });

    }


    // ==========================================
    // BUSCADOR DE ESPECIALIDADES
    // ==========================================

    const buscarEspecialidad = document.getElementById('buscarEspecialidad');
    const especialidades = document.querySelectorAll('.especialidad-card');
    const sinEspecialidades = document.getElementById('sin-especialidades');

    if (buscarEspecialidad) {

        buscarEspecialidad.addEventListener('input', () => {

            const busqueda = normalizarTexto(buscarEspecialidad.value);
            let encontrados = 0;

            especialidades.forEach(especialidad => {

                const nombre = normalizarTexto(especialidad.dataset.search || "");
                const coincide = nombre.includes(busqueda);

                especialidad.classList.toggle('hidden', !coincide);

                if (coincide) {
                    encontrados++;
                }

            });

            if (sinEspecialidades) {
                sinEspecialidades.classList.toggle('hidden', encontrados > 0);
            }

        });

    }

});
