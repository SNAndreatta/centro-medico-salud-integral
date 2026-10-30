CREATE TABLE IF NOT EXISTS rol(
    id_rol INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS especialidad(
    id_especialidad INT PRIMARY KEY AUTO_INCREMENT,
    nombre_especialidad VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS cobertura(
    id_cobertura INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS estado_turno(
    id_estado_turno INT PRIMARY KEY AUTO_INCREMENT,
    estado_turno VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS consultorio(
    id_consultorio INT PRIMARY KEY AUTO_INCREMENT,
    numero INT NOT NULL,
    piso INT
);

CREATE TABLE IF NOT EXISTS usuario(
    id_usuario INT PRIMARY KEY AUTO_INCREMENT,
    id_rol INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    correo_electronico VARCHAR(150) UNIQUE NOT NULL,
    dni VARCHAR(20) NOT NULL,
    fecha_nacimiento DATE,
    contrasenia VARCHAR(255) NOT NULL,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_rol) REFERENCES rol(id_rol)
);

CREATE TABLE IF NOT EXISTS plan(
    id_plan INT PRIMARY KEY AUTO_INCREMENT,
    id_cobertura INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    FOREIGN KEY (id_cobertura) REFERENCES cobertura(id_cobertura)
);

CREATE TABLE IF NOT EXISTS paciente(
    id_paciente INT PRIMARY KEY AUTO_INCREMENT,
    id_plan INT,
    id_usuario INT NOT NULL,
    nro_afiliado VARCHAR(50),
    FOREIGN KEY (id_plan) REFERENCES plan(id_plan),
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
);

CREATE TABLE IF NOT EXISTS medico(
    id_medico INT PRIMARY KEY AUTO_INCREMENT,
    id_especialidad INT NOT NULL,
    id_usuario INT NOT NULL,
    matricula VARCHAR(50) UNIQUE NOT NULL,
    FOREIGN KEY (id_especialidad) REFERENCES especialidad(id_especialidad),
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
);

CREATE TABLE IF NOT EXISTS cobertura_medico(
    id_cobertura_medico INT PRIMARY KEY AUTO_INCREMENT,
    id_cobertura INT NOT NULL,
    id_medico INT NOT NULL,
    FOREIGN KEY (id_cobertura) REFERENCES cobertura(id_cobertura),
    FOREIGN KEY (id_medico) REFERENCES medico(id_medico)
);

CREATE TABLE IF NOT EXISTS agenda(
    id_agenda INT PRIMARY KEY AUTO_INCREMENT,
    id_medico INT NOT NULL,
    id_consultorio INT NOT NULL,
    duracion_turno INT NOT NULL, -- INT para minutos
    fecha_inicio DATE NOT NULL,
    fecha_hasta DATE NOT NULL,
    FOREIGN KEY (id_medico) REFERENCES medico(id_medico),
    FOREIGN KEY (id_consultorio) REFERENCES consultorio(id_consultorio)
);

CREATE TABLE IF NOT EXISTS agenda_dias(
    id_agenda_dias INT PRIMARY KEY AUTO_INCREMENT,
    id_agenda INT NOT NULL,
    dia_semana INT NOT NULL, -- INT (1=Lunes, 2=Martes)
    horario_inicio_jornada TIME NOT NULL,
    horario_final_jornada TIME NOT NULL,
    FOREIGN KEY (id_agenda) REFERENCES agenda(id_agenda)
);

CREATE TABLE IF NOT EXISTS turno(
    id_turno INT PRIMARY KEY AUTO_INCREMENT,
    id_agenda INT NOT NULL,
    id_paciente INT,
    id_estado INT NOT NULL,
    fecha_creacion_turno DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_horario_inicial DATETIME NOT NULL,
    fecha_horario_llegada DATETIME,
    codigo_qr VARCHAR(255) UNIQUE,
    FOREIGN KEY (id_agenda) REFERENCES agenda(id_agenda),
    FOREIGN KEY (id_paciente) REFERENCES paciente(id_paciente),
    FOREIGN KEY (id_estado) REFERENCES estado_turno(id_estado_turno)
);