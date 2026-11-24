document.addEventListener("DOMContentLoaded", () => {
    const datos = JSON.parse(document.getElementById("datosAgendaJson").textContent);
    const contenedor = document.getElementById("datosAgenda");
    const modo = contenedor.dataset.modo; // 'medico' | 'paciente'
    const porFecha = Object.fromEntries(datos.map(d => [d.fecha, d]));

    const panel = document.getElementById("panelHorarios");
    const titulo = document.getElementById("tituloDia");
    const detalle = document.getElementById("turnoSeleccionado"); // null en modo paciente
    const botonesDia = document.querySelectorAll(".dia-agenda");

    const CLASES_HORARIO = "flex items-center justify-center rounded-full px-2 py-2 text-xs font-semibold transition sm:text-sm";
    const CLASES_VACIO = detalle ? detalle.className : "";
    const HTML_VACIO = detalle ? detalle.innerHTML : "";

    let onSeleccionarHorario = null; // callback para modo paciente

    function formatearFecha(iso) {
        const [y, m, d] = iso.split("-").map(Number);
        const texto = new Date(y, m - 1, d).toLocaleDateString("es-AR", {
            weekday: "long", day: "numeric", month: "long",
        });
        return texto.charAt(0).toUpperCase() + texto.slice(1);
    }

    function mostrarSinTurno() {
        if (!detalle) return;
        detalle.className = CLASES_VACIO;
        detalle.innerHTML = HTML_VACIO;
        if (window.lucide) lucide.createIcons();
    }

    function mostrarDetalle(fecha, turno) {
        if (!detalle) return;
        const plantilla = document.querySelector(
            `template[data-fecha="${fecha}"][data-hora="${turno.hora}"]`
        );
        if (!plantilla) return;

        // La card ya trae su propio fondo y padding
        detalle.className = "";
        detalle.replaceChildren(plantilla.content.cloneNode(true));
        if (window.lucide) lucide.createIcons();
    }

    function renderHorariosMedico(dia, fecha) {
        dia.turnos.forEach(turno => {
            const btn = document.createElement("button");
            btn.type = "button";
            btn.dataset.hora = turno.hora;
            btn.textContent = turno.hora;

            if (!turno.disponible) {
                // Ocupado (con paciente): seleccionable
                btn.className = `${CLASES_HORARIO} bg-acento/20 text-acento hover:bg-acento/30 border border-acento`;
                btn.title = "Ocupado - ver turno";
                btn.addEventListener("click", () => seleccionarHorario(fecha, turno, btn));
            } else {
                // Disponible (sin paciente): deshabilitado
                btn.className = `${CLASES_HORARIO} cursor-default bg-white text-gray-400 border border-gray-300`;
                btn.title = "Disponible";
                btn.disabled = true;
            }
            panel.appendChild(btn);
        });

        mostrarSinTurno();
    }

    function renderHorariosPaciente(dia, fecha) {
        const disponibles = dia.turnos.filter(t => t.disponible);

        if (disponibles.length === 0) {
            panel.innerHTML = `<p class="col-span-full text-center text-sm text-gray-500">No hay horarios disponibles para este día.</p>`;
            return;
        }

        disponibles.forEach(turno => {
            const btn = document.createElement("button");
            btn.type = "button";
            btn.dataset.hora = turno.hora;
            btn.className = `${CLASES_HORARIO} bg-white text-acento border border-acento`;
            btn.title = "Seleccionar horario";
            btn.textContent = turno.hora;
            btn.addEventListener("click", () => seleccionarHorarioPaciente(fecha, turno.hora, btn));
            panel.appendChild(btn);
        });
    }

    function seleccionarHorario(fecha, turno, btn) {
        panel.querySelectorAll("button[data-hora]").forEach(b => {
            if (!b.disabled) b.className = `${CLASES_HORARIO} bg-acento/20 text-acento hover:bg-acento/30 border border-acento`;
        });
        btn.className = `${CLASES_HORARIO} bg-acento text-white border border-acento`;
        mostrarDetalle(fecha, turno);
    }

    function seleccionarHorarioPaciente(fecha, hora, btn) {
        panel.querySelectorAll("button[data-hora]").forEach(b => {
            b.className = `${CLASES_HORARIO} bg-white text-acento border border-acento`;
        });
        btn.className = `${CLASES_HORARIO} bg-acento text-white border border-acento ring-2 ring-acento`;

        document.dispatchEvent(new CustomEvent("turno-seleccionado-paciente", { detail: { fecha, hora } }));
        if (onSeleccionarHorario) onSeleccionarHorario(fecha, hora);
    }

    function renderHorarios(fecha) {
        const dia = porFecha[fecha];
        panel.innerHTML = "";

        if (!dia || dia.turnos.length === 0) {
            panel.innerHTML = `
            <div
                class="w-full col-span-full rounded-2xl bg-white px-4 py-8 text-center shadow-sm sm:px-6 grid-1">

                <i
                    data-lucide="calendar-off"
                    class="mx-auto mb-4 h-10 w-10 text-gray-400 sm:h-12 sm:w-12"
                ></i>

                <h3 class="text-base font-bold text-acento sm:text-lg">
                    No hay atención en el día seleccionado.
                </h3>

            </div>`;
            if (modo === "medico") mostrarSinTurno();
            return;
        }

        if (modo === "paciente") {
            renderHorariosPaciente(dia, fecha);
        } else {
            renderHorariosMedico(dia, fecha);
        }
    }

    function seleccionarDia(fecha) {
        botonesDia.forEach(b => {
            const activo = b.dataset.fecha === fecha;
            b.setAttribute("aria-pressed", activo);
        });
        titulo.textContent = formatearFecha(fecha);
        renderHorarios(fecha);
    }

    botonesDia.forEach(b => b.addEventListener("click", () => seleccionarDia(b.dataset.fecha)));

    seleccionarDia(contenedor.dataset.fechaInicial);

    // API para que fecha.html se registre en modo paciente
    window.agendaMensualPaciente = {
        onSeleccionarHorario: (cb) => { onSeleccionarHorario = cb; },
    };
});