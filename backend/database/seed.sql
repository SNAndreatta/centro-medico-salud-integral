USE SistemaMedico;

INSERT INTO Rol (IDRol, Nombre) 
VALUES (1, 'Administrador'), (2, 'Recepcionista'), (3, 'Paciente'), (4, 'Medico');

INSERT INTO Especialidad (IDEspecialidad, Nombre_Especialidad) 
VALUES (1, 'Clinica medica'), (2, 'Pediatria'), (3, 'Cardiologia'), (4, 'Dermatologia'), (5, 'Traumatologia');

INSERT INTO Cobertura (IDCobertura, Nombre) 
VALUES (1, 'OSDE'), (2, 'Swiss Medical'), (3, 'Galeno');

INSERT INTO Estado_Turno (IDEstadoTurno, Estado_Turno) 
VALUES (1, 'disponible'), (2, 'reservado'), (3, 'confirmado'), (4, 'atendido'), (5, 'cancelado'), (6, 'ausente');

INSERT INTO Consultorio (IDConsultorio, IDEstadoConsultorio, Numero, Piso) 
VALUES (1, NULL, 101, 1), (2, NULL, 102, 1), (3, NULL, 201, 2);

INSERT INTO Usuario (IDUsuario, IDRol, Nombre, Apellido, Correo_Electronico, DNI, Fecha_Nacimiento, Contrasenia) 
VALUES
    (1, 1, 'Admin', 'Sistema', 'admin@saludintegral.test', '30000001', '1980-06-15', 'pbkdf2:sha256:600000$seedAdmin2026$4aefecb22614f8fd70b74b12ac5f78d55cb50946031cf91d3301d45a6d898564'),
    (2, 2, 'Sofia', 'Recepcion', 'recepcion@saludintegral.test', '30000002', '1990-02-10', 'pbkdf2:sha256:600000$seedRecep2026$ec08e727e82765edd5d68e0d39b7dd60487f4c154ebdefb0dd70b832b0591b21'),
    (3, 3, 'Ana', 'Rossi', 'ana.rossi@saludintegral.test', '40000001', '1998-04-12', 'pbkdf2:sha256:600000$seedPac0012026$8a667f16954a00880245950611e981e1ca60d95137afe97aab66fd840b621b82'),
    (4, 3, 'Bruno', 'Perez', 'bruno.perez@saludintegral.test', '40000002', '1987-08-20', 'pbkdf2:sha256:600000$seedPac0022026$5f824863b59124f3c7eb6f4a79c56ffc34e9c66fca6d37dabbc0758369cf41e1'),
    (5, 3, 'Camila', 'Diaz', 'camila.diaz@saludintegral.test', '40000003', '1994-12-05', 'pbkdf2:sha256:600000$seedPac0032026$9e61a870f4c0c829d9aa689d34aae6b126cf2786a21c6769f9a9e67ad7b3eba8'),
    (6, 4, 'Ana', 'Gutierrez', 'ana.gutierrez@saludintegral.test', '20000001', '1975-03-18', 'pbkdf2:sha256:600000$seedMed0012026$1b11a615868608ece1fd614034c72aaba3ec859f4e8ce9827becff4523368510'),
    (7, 4, 'Martin', 'Lopez', 'martin.lopez@saludintegral.test', '20000002', '1982-09-09', 'pbkdf2:sha256:600000$seedMed0022026$56b8ab07f217876aea35f3cc9af9378108c8285ad89e4b48a2a6bf8906814daa'),
    (8, 4, 'Lucia', 'Fernandez', 'lucia.fernandez@saludintegral.test', '20000003', '1986-01-25', 'pbkdf2:sha256:600000$seedMed0032026$4273b21fe678fc438bbeaba6f15292482b658fb246f13066c11d85819406690e')


INSERT INTO Plan (IDPlan, IDCobertura, Nombre) 
VALUES (1, 1, 'OSDE 210'), (2, 1, 'OSDE 310'), (3, 2, 'SMG 20'), (4, 3, 'Galeno Azul');

INSERT INTO Paciente (IDPaciente, IDPlan, IDUsuario, NroAfiliado) 
VALUES (1, 1, 3, 'OSDE-TEST-001'), (2, 4, 4, 'GAL-TEST-002'), (3, NULL, 5, NULL);

INSERT INTO Medico (IDMedico, IDEspecialidad, IDUsuario, Matricula) 
VALUES (1, 3, 6, 'MN-TEST-1001'), (2, 4, 7, 'MN-TEST-1002'), (3, 2, 8, 'MN-TEST-1003');

INSERT INTO Cobertura_Medico (IDCoberturaMedico, IDCobertura, IDMedico) 
VALUES (1, 1, 1), (2, 2, 1), (3, 3, 2), (4, 1, 3), (5, 2, 3);

INSERT INTO Agenda (IDAgenda, IDMedico, IDConsultorio, Duracion_Turno, Fecha_Inicio, Fecha_Hasta)
VALUES 
    (1, 1, 1, '00:30:00', '2026-11-01', '2026-12-31'),
    (2, 2, 2, '00:45:00', '2026-11-01', '2026-12-31'), 
    (3, 3, 3, '00:20:00', '2026-11-01', '2026-12-31');

INSERT INTO Agenda_Dias (IDAgendaDias, IDAgenda, Dia_Semana, Fecha_Horario_Inicio_Jornada, Fecha_Horario_Final_Jornada)
VALUES (1, 1, 'Lunes',     '2026-11-02 09:00:00', '2026-11-02 12:00:00'), 
    (2, 1, 'Miercoles', '2026-11-04 14:00:00', '2026-11-04 18:00:00'), 
    (3, 2, 'Martes',    '2026-11-03 09:00:00', '2026-11-03 13:00:00'), 
    (4, 2, 'Jueves',    '2026-11-05 13:00:00', '2026-11-05 17:00:00'), 
    (5, 3, 'Viernes',   '2026-11-06 08:00:00', '2026-11-06 12:00:00');

INSERT INTO Turno (IDTurno, IDAgenda, IDPaciente, IDEstado, Fecha_Horario_Inicial, Fecha_Horario_Llegada, Codigo_QR)
VALUES (1, 1, NULL, 1, '2026-11-02 09:00:00', NULL, NULL),
    (2, 1, 1, 2, '2026-11-02 09:30:00', NULL, 'QR-DEMO-002'),
    (3, 1, 1, 3, '2026-11-02 10:00:00', '2026-11-02 09:50:00', 'QR-DEMO-003'),
    (4, 2, 2, 4, '2026-11-03 09:00:00', '2026-11-03 08:45:00', 'QR-DEMO-004'),
    (5, 1, 1, 5, '2026-11-04 14:00:00', NULL, 'QR-DEMO-005'),
    (6, 2, 2, 6, '2026-11-05 13:00:00', NULL, NULL),
    (7, 3, NULL, 1, '2026-11-06 08:00:00', NULL, NULL);