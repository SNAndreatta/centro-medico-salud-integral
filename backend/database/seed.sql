INSERT IGNORE INTO rol (id_rol, nombre)
VALUES (1, 'Administrador'), (2, 'Recepcionista'), (3, 'Paciente'), (4, 'Medico');

INSERT IGNORE INTO especialidad (id_especialidad, nombre_especialidad)
VALUES
    (1, 'Clinica medica'),
    (2, 'Pediatria'),
    (3, 'Cardiologia'),
    (4, 'Dermatologia'),
    (5, 'Traumatologia');

INSERT IGNORE INTO cobertura (id_cobertura, nombre)
VALUES (1, 'OSDE'), (2, 'Swiss Medical'), (3, 'Galeno');

INSERT IGNORE INTO estado_turno (id_estado_turno, estado_turno)
VALUES
    (1, 'disponible'),
    (2, 'reservado'),
    (3, 'confirmado'),
    (4, 'atendido'),
    (5, 'cancelado'),
    (6, 'ausente');

INSERT IGNORE INTO consultorio (id_consultorio, numero, piso)
VALUES (1, 101, 1), (2, 102, 1), (3, 201, 2);

INSERT IGNORE INTO usuario (
    id_usuario,
    id_rol,
    nombre,
    apellido,
    correo_electronico,
    dni,
    fecha_nacimiento,
    contrasenia
)
VALUES
    (1, 1, 'Admin', 'Sistema', 'admin@saludintegral.test', '30000001', '1980-06-15', 'pbkdf2:sha256:600000$bbb2232b0bdaeebf$ae6ce40e24f7a7db5b8cc0a6bd679f0a90ffd897305920298f1111eee62c3178'),
    (2, 2, 'Sofia', 'Recepcion', 'recepcion@saludintegral.test', '30000002', '1990-02-10', 'pbkdf2:sha256:600000$4a5196950b065f67$f243dfcaf428f6bb558c1279f621ba329ee22320e0b053922fa64e2176cbb883'),
    (3, 3, 'Ana', 'Rossi', 'ana.rossi@saludintegral.test', '40000001', '1998-04-12', 'pbkdf2:sha256:600000$7613960be6fa97a6$81cd403dc462ed5e34c0b4bb3067a3fccf3a5a099e0a7694a97aab6dd8d20faa'),
    (4, 3, 'Bruno', 'Perez', 'bruno.perez@saludintegral.test', '40000002', NULL, 'pbkdf2:sha256:600000$7e0e10f11f4711c1$e5cc21bb97dab7ac5dedfa6918f2e8e368dfb2886db0808dcfe242fedc8e6c6c'),
    (5, 3, 'Camila', 'Diaz', 'camila.diaz@saludintegral.test', '40000003', '1994-12-05', 'pbkdf2:sha256:600000$6f9311d8b6d2cd0f$2f41445f217948e0587fa1f0a6c37e6078296af87b5f53127067f14a195f3198'),
    (6, 4, 'Ana', 'Gutierrez', 'ana.gutierrez@saludintegral.test', '20000001', '1975-03-18', 'pbkdf2:sha256:600000$1d1b4552548da5c5$abef5c248bae8fa7131073d880bf82779499845ae5cbb08e40dbae940f30df35'),
    (7, 4, 'Martin', 'Lopez', 'martin.lopez@saludintegral.test', '20000002', '1982-09-09', 'pbkdf2:sha256:600000$062a597c05329416$b748f7b1e42f6724b17c56349e104212ae689121da2706f75ad11c65b90970d4'),
    (8, 4, 'Lucia', 'Fernandez', 'lucia.fernandez@saludintegral.test', '20000003', '1986-01-25', 'pbkdf2:sha256:600000$054686320dec1783$fa475b38eec857f31ff9b9bb50285ead56191be995941d0bc4a2af738cd3813b');

-- Cuentas demo (contraseña: 12345678)
INSERT IGNORE INTO usuario (
    id_usuario,
    id_rol,
    nombre,
    apellido,
    correo_electronico,
    dni,
    fecha_nacimiento,
    contrasenia
)
VALUES
    (101, 1, 'Admin', 'Demo', 'admin.demo@saludintegral.test', '39000001', '1985-01-15', 'pbkdf2:sha256:600000$DO5EUaODnAq4I0GN$3d8102d0356ee962095c657f924917feb8002688aff9953e12f6307a273444a7'),
    (102, 2, 'Recepcion', 'Demo', 'recepcion.demo@saludintegral.test', '39000002', '1992-03-22', 'pbkdf2:sha256:600000$TUDkmZwqaVY8fXsg$e25d95ee122179969e31508e9bec8251477c70d010753e14fefd9a70722a0036'),
    (103, 3, 'Paciente', 'Demo', 'paciente.demo@saludintegral.test', '49000001', '1995-05-20', 'pbkdf2:sha256:600000$n4lOZ9gTHmkrDxxm$0a95c295f46e3bb5b676b71957a6b7d990b7b1fb4705378c9f050483dddbfb6e'),
    (104, 4, 'Medico', 'Demo', 'medico.demo@saludintegral.test', '29000001', '1980-08-10', 'pbkdf2:sha256:600000$zqsa36FSCzXby3bi$2fee86dbc83bb6b5edfdbd787e401d5d51161e6c385379b3a9316b6b42aa4196');

INSERT IGNORE INTO paciente (id_paciente, id_cobertura, id_usuario, nro_afiliado)
VALUES (1, 1, 3, 'OSDE-TEST-001'), (2, 3, 4, 'GAL-TEST-002'), (3, NULL, 5, NULL),
       (101, 1, 103, 'OSDE-DEMO-001');

INSERT IGNORE INTO medico (id_medico, id_especialidad, id_usuario, matricula)
VALUES (1, 3, 6, 'MN-TEST-1001'), (2, 4, 7, 'MN-TEST-1002'), (3, 2, 8, 'MN-TEST-1003'),
       (101, 1, 104, 'MN-DEMO-1001');

INSERT IGNORE INTO cobertura_medico (id_cobertura_medico, id_cobertura, id_medico)
VALUES (1, 1, 1), (2, 2, 1), (3, 3, 2), (4, 1, 3), (5, 2, 3),
       (101, 1, 101), (102, 2, 101);

INSERT IGNORE INTO agenda (
    id_agenda,
    id_medico,
    id_consultorio,
    duracion_turno,
    fecha_inicio,
    fecha_hasta
)
VALUES
    (1, 1, 1, 30, '2026-11-01', '2026-12-31'),
    (2, 2, 2, 45, '2026-11-01', '2026-12-31'),
    (3, 3, 3, 20, '2026-11-01', '2026-12-31'),
    (101, 101, 1, 30, '2026-11-01', '2026-12-31');

INSERT IGNORE INTO agenda_dias (
    id_agenda_dias,
    id_agenda,
    dia_semana,
    horario_inicio_jornada,
    horario_final_jornada
)
VALUES
    (1, 1, 1, '09:00:00', '12:00:00'),
    (2, 1, 3, '14:00:00', '18:00:00'),
    (3, 2, 2, '09:00:00', '13:00:00'),
    (4, 2, 4, '13:00:00', '17:00:00'),
    (5, 3, 5, '08:00:00', '12:00:00'),
    (101, 101, 1, '09:00:00', '13:00:00'),
    (102, 101, 3, '14:00:00', '18:00:00');

INSERT IGNORE INTO turno (
    id_turno,
    id_agenda,
    id_paciente,
    id_estado,
    fecha_horario_inicial,
    fecha_horario_llegada,
    codigo_qr
)
VALUES
    (1, 1, NULL, 1, '2026-11-02 09:00:00', NULL, NULL),
    (2, 1, 1, 2, '2026-11-02 09:30:00', NULL, 'QR-DEMO-002'),
    (3, 1, 1, 3, '2026-11-02 10:00:00', '2026-11-02 09:50:00', 'QR-DEMO-003'),
    (4, 2, 2, 4, '2026-11-03 09:00:00', '2026-11-03 08:45:00', 'QR-DEMO-004'),
    (5, 1, 1, 5, '2026-11-04 14:00:00', NULL, 'QR-DEMO-005'),
    (6, 2, 2, 6, '2026-11-05 13:00:00', NULL, NULL),
    (7, 3, NULL, 1, '2026-11-06 08:00:00', NULL, NULL),
    -- Turnos disponibles generados para testing (semana del 23 al 29 de Nov 2026)
    -- Agenda 1: Dr. Gutierrez (Cardiologia), Lunes y Miércoles 9-12 y 14-18, turno 30 min
    (1041, 1, NULL, 1, '2026-11-25 09:00:00', NULL, NULL),
    (1042, 1, NULL, 1, '2026-11-25 09:30:00', NULL, NULL),
    (1043, 1, NULL, 1, '2026-11-25 10:00:00', NULL, NULL),
    (1044, 1, NULL, 1, '2026-11-25 10:30:00', NULL, NULL),
    (1045, 1, NULL, 1, '2026-11-25 11:00:00', NULL, NULL),
    (1046, 1, NULL, 1, '2026-11-25 11:30:00', NULL, NULL),
    (1047, 1, NULL, 1, '2026-11-25 14:00:00', NULL, NULL),
    (1048, 1, NULL, 1, '2026-11-25 14:30:00', NULL, NULL),
    (1049, 1, NULL, 1, '2026-11-25 15:00:00', NULL, NULL),
    (1050, 1, NULL, 1, '2026-11-25 15:30:00', NULL, NULL),
    (1051, 1, NULL, 1, '2026-11-27 09:00:00', NULL, NULL),
    (1052, 1, NULL, 1, '2026-11-27 09:30:00', NULL, NULL),
    (1053, 1, NULL, 1, '2026-11-27 10:00:00', NULL, NULL),
    (1054, 1, NULL, 1, '2026-11-27 10:30:00', NULL, NULL),
    (1055, 1, NULL, 1, '2026-11-27 11:00:00', NULL, NULL),
    (1056, 1, NULL, 1, '2026-11-27 11:30:00', NULL, NULL),
    (1057, 1, NULL, 1, '2026-11-27 14:00:00', NULL, NULL),
    (1058, 1, NULL, 1, '2026-11-27 14:30:00', NULL, NULL),
    (1059, 1, NULL, 1, '2026-11-27 15:00:00', NULL, NULL),
    (1060, 1, NULL, 1, '2026-11-27 15:30:00', NULL, NULL),
    -- Agenda 2: Dr. Lopez (Dermatologia), Martes y Jueves 9-13 y 13-17, turno 45 min
    (2001, 2, NULL, 1, '2026-11-26 09:00:00', NULL, NULL),
    (2002, 2, NULL, 1, '2026-11-26 09:45:00', NULL, NULL),
    (2003, 2, NULL, 1, '2026-11-26 10:30:00', NULL, NULL),
    (2004, 2, NULL, 1, '2026-11-26 11:15:00', NULL, NULL),
    (2005, 2, NULL, 1, '2026-11-26 13:00:00', NULL, NULL),
    (2006, 2, NULL, 1, '2026-11-26 13:45:00', NULL, NULL),
    (2007, 2, NULL, 1, '2026-11-26 14:30:00', NULL, NULL),
    (2008, 2, NULL, 1, '2026-11-26 15:15:00', NULL, NULL),
    (2009, 2, NULL, 1, '2026-11-28 09:00:00', NULL, NULL),
    (2010, 2, NULL, 1, '2026-11-28 09:45:00', NULL, NULL),
    (2011, 2, NULL, 1, '2026-11-28 10:30:00', NULL, NULL),
    (2012, 2, NULL, 1, '2026-11-28 11:15:00', NULL, NULL),
    (2013, 2, NULL, 1, '2026-11-28 13:00:00', NULL, NULL),
    (2014, 2, NULL, 1, '2026-11-28 13:45:00', NULL, NULL),
    (2015, 2, NULL, 1, '2026-11-28 14:30:00', NULL, NULL),
    (2016, 2, NULL, 1, '2026-11-28 15:15:00', NULL, NULL),
    -- Agenda 3: Dr. Fernandez (Pediatria), Viernes 8-12, turno 20 min
    (3001, 3, NULL, 1, '2026-11-29 08:00:00', NULL, NULL),
    (3002, 3, NULL, 1, '2026-11-29 08:20:00', NULL, NULL),
    (3003, 3, NULL, 1, '2026-11-29 08:40:00', NULL, NULL),
    (3004, 3, NULL, 1, '2026-11-29 09:00:00', NULL, NULL),
    (3005, 3, NULL, 1, '2026-11-29 09:20:00', NULL, NULL),
    (3006, 3, NULL, 1, '2026-11-29 09:40:00', NULL, NULL),
    (3007, 3, NULL, 1, '2026-11-29 10:00:00', NULL, NULL),
    (3008, 3, NULL, 1, '2026-11-29 10:20:00', NULL, NULL),
    (3009, 3, NULL, 1, '2026-11-29 10:40:00', NULL, NULL),
    (3010, 3, NULL, 1, '2026-11-29 11:00:00', NULL, NULL),
    (3011, 3, NULL, 1, '2026-11-29 11:20:00', NULL, NULL),
    (3012, 3, NULL, 1, '2026-11-29 11:40:00', NULL, NULL),
    (3013, 3, NULL, 1, '2026-11-29 12:00:00', NULL, NULL),
    -- Agenda 101: Médico Demo (Clinica medica), Lunes y Miércoles 9-13, turno 30 min
    (4001, 101, NULL, 1, '2026-11-25 09:00:00', NULL, NULL),
    (4002, 101, NULL, 1, '2026-11-25 09:30:00', NULL, NULL),
    (4003, 101, NULL, 1, '2026-11-25 10:00:00', NULL, NULL),
    (4004, 101, NULL, 1, '2026-11-25 10:30:00', NULL, NULL),
    (4005, 101, NULL, 1, '2026-11-25 11:00:00', NULL, NULL),
    (4006, 101, NULL, 1, '2026-11-25 11:30:00', NULL, NULL),
    (4007, 101, NULL, 1, '2026-11-27 09:00:00', NULL, NULL),
    (4008, 101, NULL, 1, '2026-11-27 09:30:00', NULL, NULL),
    (4009, 101, NULL, 1, '2026-11-27 10:00:00', NULL, NULL),
    (4010, 101, NULL, 1, '2026-11-27 10:30:00', NULL, NULL),
    (4011, 101, NULL, 1, '2026-11-27 11:00:00', NULL, NULL),
    (4012, 101, NULL, 1, '2026-11-27 11:30:00', NULL, NULL);

INSERT IGNORE INTO turno (
    id_turno,
    id_agenda,
    id_paciente,
    id_estado,
    fecha_horario_inicial,
    fecha_horario_llegada,
    codigo_qr
)
VALUES
    (1001, 101, NULL, 1, '2026-11-23 09:00:00', NULL, NULL),
    (1002, 101, NULL, 1, '2026-11-23 09:30:00', NULL, NULL),
    (1003, 101, NULL, 1, '2026-11-23 10:00:00', NULL, NULL),
    (1004, 101, NULL, 1, '2026-11-23 10:30:00', NULL, NULL),
    (1005, 101, NULL, 1, '2026-11-23 11:00:00', NULL, NULL),
    (1006, 101, NULL, 1, '2026-11-23 11:30:00', NULL, NULL),
    (1007, 101, NULL, 1, '2026-11-23 12:00:00', NULL, NULL),
    (1008, 101, NULL, 1, '2026-11-23 12:30:00', NULL, NULL),
    (1009, 101, NULL, 1, '2026-11-25 14:00:00', NULL, NULL),
    (1010, 101, NULL, 1, '2026-11-25 14:30:00', NULL, NULL),
    (1011, 101, NULL, 1, '2026-11-25 15:00:00', NULL, NULL),
    (1012, 101, NULL, 1, '2026-11-25 15:30:00', NULL, NULL),
    (1013, 101, NULL, 1, '2026-11-25 16:00:00', NULL, NULL),
    (1014, 101, NULL, 1, '2026-11-25 16:30:00', NULL, NULL),
    (1015, 101, NULL, 1, '2026-11-25 17:00:00', NULL, NULL),
    (1016, 101, NULL, 1, '2026-11-25 17:30:00', NULL, NULL),
    (1017, 101, NULL, 1, '2026-11-30 09:00:00', NULL, NULL),
    (1018, 101, NULL, 1, '2026-11-30 09:30:00', NULL, NULL),
    (1019, 101, NULL, 1, '2026-11-30 10:00:00', NULL, NULL),
    (1020, 101, NULL, 1, '2026-11-30 10:30:00', NULL, NULL),
    (1021, 101, NULL, 1, '2026-11-30 11:00:00', NULL, NULL),
    (1022, 101, NULL, 1, '2026-11-30 11:30:00', NULL, NULL),
    (1023, 101, NULL, 1, '2026-11-30 12:00:00', NULL, NULL),
    (1024, 101, NULL, 1, '2026-11-30 12:30:00', NULL, NULL),
    (1025, 101, NULL, 1, '2026-12-02 14:00:00', NULL, NULL),
    (1026, 101, NULL, 1, '2026-12-02 14:30:00', NULL, NULL),
    (1027, 101, NULL, 1, '2026-12-02 15:00:00', NULL, NULL),
    (1028, 101, NULL, 1, '2026-12-02 15:30:00', NULL, NULL),
    (1029, 101, NULL, 1, '2026-12-02 16:00:00', NULL, NULL),
    (1030, 101, NULL, 1, '2026-12-02 16:30:00', NULL, NULL),
    (1031, 101, NULL, 1, '2026-12-02 17:00:00', NULL, NULL),
    (1032, 101, NULL, 1, '2026-12-02 17:30:00', NULL, NULL),
    (1041, 1, NULL, 1, '2026-11-23 09:00:00', NULL, NULL),
    (1042, 1, NULL, 1, '2026-11-23 09:30:00', NULL, NULL),
    (1043, 1, NULL, 1, '2026-11-23 10:00:00', NULL, NULL),
    (1044, 1, NULL, 1, '2026-11-23 10:30:00', NULL, NULL),
    (1045, 1, NULL, 1, '2026-11-23 11:00:00', NULL, NULL),
    (1046, 1, NULL, 1, '2026-11-23 11:30:00', NULL, NULL),
    (1047, 1, NULL, 1, '2026-11-25 14:00:00', NULL, NULL),
    (1048, 1, NULL, 1, '2026-11-25 14:30:00', NULL, NULL),
    (1049, 1, NULL, 1, '2026-11-25 15:00:00', NULL, NULL),
    (1050, 1, NULL, 1, '2026-11-25 15:30:00', NULL, NULL),
    (1061, 3, NULL, 1, '2026-11-27 08:00:00', NULL, NULL),
    (1062, 3, NULL, 1, '2026-11-27 08:20:00', NULL, NULL),
    (1063, 3, NULL, 1, '2026-11-27 08:40:00', NULL, NULL),
    (1064, 3, NULL, 1, '2026-11-27 09:00:00', NULL, NULL),
    (1065, 3, NULL, 1, '2026-11-27 09:20:00', NULL, NULL),
    (1066, 3, NULL, 1, '2026-11-27 09:40:00', NULL, NULL);
