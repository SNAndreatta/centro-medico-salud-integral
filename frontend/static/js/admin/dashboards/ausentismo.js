document.addEventListener("DOMContentLoaded", function () {

    // ==========================================
    // ELEMENTOS DEL BUSCADOR DE MÉDICOS
    // ==========================================

    const buscarMedico = document.getElementById("buscarMedico");
    const sinMedicos = document.getElementById("sinMedicos");


    // ==========================================
    // ELEMENTOS DEL BUSCADOR DE ESPECIALIDADES
    // ==========================================

    const buscarEspecialidad = document.getElementById("buscarEspecialidad");
    const sinEspecialidades = document.getElementById("sinEspecialidades");


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
    // BUSCAR MÉDICOS
    // ==========================================

    if (buscarMedico) {

        buscarMedico.addEventListener("input", function () {

            const busqueda = normalizarTexto(buscarMedico.value);

            const tarjetas = document.querySelectorAll("[data-filtro-medico]");

            let encontrados = 0;

            tarjetas.forEach(function (tarjeta) {

                const nombre = normalizarTexto(tarjeta.dataset.texto || "");

                const coincide = nombre.includes(busqueda);

                tarjeta.classList.toggle("hidden", !coincide);

                if (coincide) {
                    encontrados++;
                }

            });

            if (sinMedicos) {
                sinMedicos.classList.toggle("hidden", encontrados > 0);
            }

        });

    }


    // ==========================================
    // BUSCAR ESPECIALIDADES
    // ==========================================

    if (buscarEspecialidad) {

        buscarEspecialidad.addEventListener("input", function () {

            const busqueda = normalizarTexto(buscarEspecialidad.value);

            const tarjetas = document.querySelectorAll("[data-filtro-especialidad]");

            let encontrados = 0;

            tarjetas.forEach(function (tarjeta) {

                const nombre = normalizarTexto(tarjeta.dataset.texto || "");

                const coincide = nombre.includes(busqueda);

                tarjeta.classList.toggle("hidden", !coincide);

                if (coincide) {
                    encontrados++;
                }

            });

            if (sinEspecialidades) {
                sinEspecialidades.classList.toggle("hidden", encontrados > 0);
            }

        });

    }

});