document.addEventListener('DOMContentLoaded', () => {

    // ==========================================
    // BUSCADOR DE MÉDICOS
    // ==========================================

    const buscarMedico = document.getElementById('buscar-medico');
    const medicos = document.querySelectorAll('.medico-card');
    const sinMedicos = document.getElementById('sin-medicos');

    buscarMedico.addEventListener('input', () => {

        const busqueda = buscarMedico.value.toLowerCase().trim();
        let encontrados = 0;

        medicos.forEach(medico => {

            const nombre = medico.dataset.search;
            const coincide = nombre.includes(busqueda);

            medico.classList.toggle('hidden', !coincide);

            if (coincide) {
                encontrados++;
            }

        });

        sinMedicos.classList.toggle('hidden', encontrados > 0);

    });


    // ==========================================
    // BUSCADOR DE ESPECIALIDADES
    // ==========================================

    const buscarEspecialidad = document.getElementById('buscar-especialidad');
    const especialidades = document.querySelectorAll('.especialidad-card');
    const sinEspecialidades = document.getElementById('sin-especialidades');

    buscarEspecialidad.addEventListener('input', () => {

        const busqueda = buscarEspecialidad.value.toLowerCase().trim();
        let encontrados = 0;

        especialidades.forEach(especialidad => {

            const nombre = especialidad.dataset.search;
            const coincide = nombre.includes(busqueda);

            especialidad.classList.toggle('hidden', !coincide);

            if (coincide) {
                encontrados++;
            }

        });

        sinEspecialidades.classList.toggle('hidden', encontrados > 0);

    });

});