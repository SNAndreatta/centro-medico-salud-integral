CREATE DATABASE SistemaMedico;
USE SistemaMedico;

CREATE TABLE Rol(
    IDRol INT PRIMARY KEY AUTO_INCREMENT,
    Nombre VARCHAR(50) NOT NULL
);

CREATE TABLE Especialidad(
    IDEspecialidad INT PRIMARY KEY AUTO_INCREMENT,
    Nombre_Especialidad VARCHAR(100) NOT NULL
);

CREATE TABLE Cobertura(
    IDCobertura INT PRIMARY KEY AUTO_INCREMENT,
    Nombre VARCHAR(100) NOT NULL
);

CREATE TABLE Estado_Turno(
    IDEstadoTurno INT PRIMARY KEY AUTO_INCREMENT,
    Estado_Turno VARCHAR(50) NOT NULL
);

CREATE TABLE Consultorio(
    IDConsultorio INT PRIMARY KEY AUTO_INCREMENT,
    IDEstadoConsultorio INT,
    Numero INT NOT NULL,
    Piso INT
);

CREATE TABLE Usuario(
    IDUsuario INT PRIMARY KEY AUTO_INCREMENT,
    IDRol INT,
    Nombre VARCHAR(100) NOT NULL,
    Apellido VARCHAR(100) NOT NULL,
    Correo_Electronico VARCHAR(150) UNIQUE NOT NULL,
    DNI VARCHAR(20) UNIQUE NOT NULL,
    Fecha_Nacimiento DATE,
    Contrasenia VARCHAR(255) NOT NULL,
    Fecha_Creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (IDRol) REFERENCES Rol(IDRol)
);

CREATE TABLE Plan(
    IDPlan INT PRIMARY KEY AUTO_INCREMENT,
    IDCobertura INT,
    Nombre VARCHAR(100) NOT NULL,
    FOREIGN KEY (IDCobertura) REFERENCES Cobertura(IDCobertura)
);

CREATE TABLE Paciente(
    IDPaciente INT PRIMARY KEY AUTO_INCREMENT,
    IDPlan INT,
    IDUsuario INT,
    NroAfiliado VARCHAR(50),
    FOREIGN KEY (IDPlan) REFERENCES Plan(IDPlan),
    FOREIGN KEY (IDUsuario) REFERENCES Usuario(IDUsuario)
);

CREATE TABLE Medico(
    IDMedico INT PRIMARY KEY AUTO_INCREMENT,
    IDEspecialidad INT,
    IDUsuario INT,
    Matricula VARCHAR(50) UNIQUE NOT NULL,
    FOREIGN KEY (IDEspecialidad) REFERENCES Especialidad(IDEspecialidad),
    FOREIGN KEY (IDUsuario) REFERENCES Usuario(IDUsuario)
);

CREATE TABLE Cobertura_Medico(
    IDCoberturaMedico INT PRIMARY KEY AUTO_INCREMENT,
    IDCobertura INT,
    IDMedico INT,
    FOREIGN KEY (IDCobertura) REFERENCES Cobertura(IDCobertura),
    FOREIGN KEY (IDMedico) REFERENCES Medico(IDMedico)
);

CREATE TABLE Agenda(
    IDAgenda INT PRIMARY KEY AUTO_INCREMENT,
    IDMedico INT,
    IDConsultorio INT,
    Duracion_Turno TIME,
    Fecha_Inicio DATE,
    Fecha_Hasta DATE,
    FOREIGN KEY (IDMedico) REFERENCES Medico(IDMedico),
    FOREIGN KEY (IDConsultorio) REFERENCES Consultorio(IDConsultorio)

);

CREATE TABLE Agenda_Dias(
    IDAgendaDias INT PRIMARY KEY AUTO_INCREMENT,
    IDAgenda INT,
    Dia_Semana VARCHAR(15),
    Fecha_Horario_Inicio_Jornada DATETIME,
    Fecha_Horario_Final_Jornada DATETIME,
    FOREIGN KEY (IDAgenda) REFERENCES Agenda(IDAgenda)
);

CREATE TABLE Turno(
    IDTurno INT PRIMARY KEY AUTO_INCREMENT,
    IDAgenda INT,
    IDPaciente INT,
    IDEstado INT,
    Fecha_Creacion_Turno DATETIME DEFAULT CURRENT_TIMESTAMP,
    Fecha_Horario_Inicial DATETIME,
    Fecha_Horario_Llegada DATETIME,
    Codigo_QR VARCHAR(255),
    FOREIGN KEY (IDAgenda) REFERENCES Agenda(IDAgenda),
    FOREIGN KEY (IDPaciente) REFERENCES Paciente(IDPaciente),
    FOREIGN KEY (IDEstado) REFERENCES Estado_Turno(IDEstadoTurno)
);