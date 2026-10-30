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

INSERT IGNORE INTO plan (id_plan, id_cobertura, nombre)
VALUES (1, 1, 'OSDE 210'), (2, 1, 'OSDE 310'), (3, 2, 'SMG 20'), (4, 3, 'Galeno Azul');

INSERT IGNORE INTO paciente (id_paciente, id_plan, id_usuario, nro_afiliado)
VALUES (1, 1, 3, 'OSDE-TEST-001'), (2, 4, 4, 'GAL-TEST-002'), (3, NULL, 5, NULL);

INSERT IGNORE INTO medico (id_medico, id_especialidad, id_usuario, matricula)
VALUES (1, 3, 6, 'MN-TEST-1001'), (2, 4, 7, 'MN-TEST-1002'), (3, 2, 8, 'MN-TEST-1003');

INSERT IGNORE INTO cobertura_medico (id_cobertura_medico, id_cobertura, id_medico)
VALUES (1, 1, 1), (2, 2, 1), (3, 3, 2), (4, 1, 3), (5, 2, 3);

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
    (3, 3, 3, 20, '2026-11-01', '2026-12-31');

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
    (5, 3, 5, '08:00:00', '12:00:00');

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
    (7, 3, NULL, 1, '2026-11-06 08:00:00', NULL, NULL);
