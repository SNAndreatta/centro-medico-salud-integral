document.addEventListener("DOMContentLoaded", () => {
    const datos = JSON.parse(document.getElementById("datosAgendaJson").textContent);
    const contenedor = document.getElementById("datosAgenda");
    const consultorio = contenedor.dataset.consultorio;
    const porFecha = Object.fromEntries(datos.map(d => [d.fecha, d]));

    const panel = document.getElementById("panelHorarios");
    const titulo = document.getElementById("tituloDia");
    const detalle = document.getElementById("turnoSeleccionado");
    const botonesDia = document.querySelectorAll(".dia-agenda");

    const CLASES_HORARIO = "flex items-center justify-center rounded-full px-2 py-2 text-xs font-semibold transition sm:text-sm";
    let fechaActiva = null;
    let horaActiva = null;

    function formatearFecha(iso) {
        const [y, m, d] = iso.split("-").map(Number);
        const texto = new Date(y, m - 1, d).toLocaleDateString("es-AR", {
            weekday: "long", day: "numeric", month: "long",
        });
        return texto.charAt(0).toUpperCase() + texto.slice(1);
    }

    function mostrarSinTurno() {
        detalle.innerHTML = `
            <i data-lucide="calendar-clock" class="mx-auto mb-4 h-10 w-10 text-gray-400"></i>
            <h3 class="text-lg font-bold text-acento">Ningún turno seleccionado</h3>
            <p class="mt-2 text-sm text-gray-500">Seleccioná un horario ocupado para ver los detalles del turno.</p>`;
        if (window.lucide) lucide.createIcons();
    }

    function mostrarDetalle(fecha, turno) {
        const p = turno.paciente;
        detalle.className = "flex flex-col gap-4 rounded-2xl bg-white p-5 shadow-sm transition hover:shadow-md lg:flex-row lg:items-center lg:gap-0 lg:px-8 lg:py-4";
        detalle.innerHTML = `
            <div class="flex min-w-0 items-center gap-4 lg:w-[42%] lg:pr-5">
                <div class="flex h-14 w-14 shrink-0 items-center justify-center rounded-full text-xl font-medium ${p.color}">${p.iniciales}</div>
                <div class="min-w-0 flex-1">
                    <h3 class="break-words text-xl font-medium leading-tight text-acento sm:text-2xl">${p.nombre}</h3>
                    <p class="truncate text-xs font-medium tracking-wide text-acento/70">${p.cobertura}</p>
                </div>
            </div>
            <div class="border-t border-gray-200 pt-3 sm:pt-4 lg:w-[30%] lg:border-l lg:border-t-0 lg:py-1 lg:pl-5">
                <p class="text-xs font-medium tracking-wide text-acento/70">FECHA Y HORA</p>
                <p class="text-xl font-medium leading-tight text-acento">${turno.hora}</p>
                <p class="text-xs font-medium text-acento">${formatearFecha(fecha)}</p>
            </div>
            <div class="border-t border-gray-200 pt-3 sm:pt-4 lg:w-[28%] lg:border-l lg:border-t-0 lg:py-1 lg:pl-5">
                <p class="text-xs font-medium tracking-wide text-acento/70">CONSULTORIO</p>
                <p class="text-3xl font-bold leading-tight text-acento">${turno.consultorio || consultorio}</p>
            </div>`;
    }

    function renderHorarios(fecha) {
        const dia = porFecha[fecha];
        panel.innerHTML = "";
        horaActiva = null;

        if (!dia || dia.turnos.length === 0) {
            panel.innerHTML = `<p class="col-span-full text-center text-sm text-gray-500">No hay atención este día.</p>`;
            mostrarSinTurno();
            return;
        }

        dia.turnos.forEach(turno => {
            const btn = document.createElement("button");
            btn.type = "button";
            btn.dataset.hora = turno.hora;

            if (turno.disponible) {
                // Disponible: visible pero no seleccionable
                btn.disabled = true;
                btn.className = `${CLASES_HORARIO} cursor-default bg-dominante text-acento`;
                btn.title = "Disponible";
                btn.textContent = turno.hora;
            } else {
                // Ocupado: seleccionable, muestra el detalle
                btn.className = `${CLASES_HORARIO} bg-gray-200 text-gray-600 hover:bg-acento hover:text-white`;
                btn.title = "Ocupado - ver turno";
                btn.textContent = turno.hora;
                btn.addEventListener("click", () => seleccionarHorario(fecha, turno, btn));
            }
            panel.appendChild(btn);
        });

        mostrarSinTurno();
    }

    function seleccionarHorario(fecha, turno, btn) {
        panel.querySelectorAll("button[data-hora]").forEach(b => {
            if (!b.disabled) b.className = `${CLASES_HORARIO} bg-gray-200 text-gray-600 hover:bg-acento hover:text-white`;
        });
        btn.className = `${CLASES_HORARIO} bg-acento text-white`;
        horaActiva = turno.hora;
        mostrarDetalle(fecha, turno);
    }

    function seleccionarDia(fecha) {
        fechaActiva = fecha;
        botonesDia.forEach(b => {
            const activo = b.dataset.fecha === fecha;
            b.classList.toggle("bg-acento", activo);
            b.classList.toggle("text-white", activo);
            b.classList.toggle("hover:bg-acento", activo);
            b.setAttribute("aria-pressed", activo);
        });
        titulo.textContent = formatearFecha(fecha);
        renderHorarios(fecha);
    }

    botonesDia.forEach(b => b.addEventListener("click", () => seleccionarDia(b.dataset.fecha)));

    seleccionarDia(contenedor.dataset.fechaInicial);
});
