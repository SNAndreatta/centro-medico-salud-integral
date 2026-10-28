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
    (1, 1, 'Admin', 'Sistema', 'admin@saludintegral.test', '30000001', '1980-06-15', 'pbkdf2:sha256:600000$seedAdmin2026$7d54073a451544ae4beab9a15177788ac562fa89c66504f5c8b3ba6418699d8c'), --Contrasenia: Admin2026!
    (2, 2, 'Sofia', 'Recepcion', 'recepcion@saludintegral.test', '30000002', '1990-02-10', 'pbkdf2:sha256:600000$seedRecep2026$530075682e67baa878f07b62dc2204a57e19124957defd71c3c08c337c73e155'), --Contrasenia: Recepcion2026!
    (3, 3, 'Ana', 'Rossi', 'ana.rossi@saludintegral.test', '40000001', '1998-04-12', 'pbkdf2:sha256:600000$seedPac0012026$e79588dfa23b312a2c7a39f23d520e65769f1ad6fec830ded5a241034d150033'), --Contrasenia: PacienteAna2026!
    (4, 3, 'Bruno', 'Perez', 'bruno.perez@saludintegral.test', '40000002', 'pbkdf2:sha256:600000$seedPac0022026$6691efe214dbca75f964a7332f569636d47f5d7a3bf8d2d313c7e8d4adbecc52'), --Contrasenia: PacienteBruno2026!
    (5, 3, 'Camila', 'Diaz', 'camila.diaz@saludintegral.test', '40000003', '1994-12-05', 'pbkdf2:sha256:600000$seedPac0032026$23091450de17b2dc6d9001dad91b98078414bda6a8777b17d390f58d993e8f77'), --Contrasenia: PacienteCamila2026!
    (6, 4, 'Ana', 'Gutierrez', 'ana.gutierrez@saludintegral.test', '20000001', '1975-03-18', 'pbkdf2:sha256:600000$seedMed0012026$e3fa408c17da15dc91588469108b3b4ef4f6b6ebb5640de0887959b6ff6dc279'), --Contrasenia: MedicaAna2026!
    (7, 4, 'Martin', 'Lopez', 'martin.lopez@saludintegral.test', '20000002', '1982-09-09', 'pbkdf2:sha256:600000$seedMed0022026$e98ac5466afac82f8dc21b7485a1b9ff2032163739b90936abe54799bf6ac0d3'), --Contrasenia: MedicoMartin2026!
    (8, 4, 'Lucia', 'Fernandez', 'lucia.fernandez@saludintegral.test', '20000003', '1986-01-25', 'pbkdf2:sha256:600000$seedMed0032026$19bdfe861b3e6599debe243c304ad931b8a5cea32a6a7c4de8c56390cb05accc') --Contrasenia: MedicaLucia2026!


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