CREATE TABLE IF NOT EXISTS pacientes (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL CHECK (length(nome) BETWEEN 2 AND 100)
);

CREATE TABLE IF NOT EXISTS consultas (
    id INTEGER PRIMARY KEY,
    paciente_id INTEGER NOT NULL REFERENCES pacientes(id) ON DELETE RESTRICT,
    data TEXT NOT NULL,
    horario TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('agendada', 'realizada', 'cancelada'))
);

CREATE INDEX IF NOT EXISTS idx_consultas_paciente ON consultas(paciente_id);
CREATE INDEX IF NOT EXISTS idx_consultas_data ON consultas(data, horario, id);
