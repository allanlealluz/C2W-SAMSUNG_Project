CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    senha varchar(255) NOT NULL,
    tipo TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS respostas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INT NOT NULL,
    section VARCHAR(255) NOT NULL,
    response TEXT NOT NULL,
    aula_id INTEGER NOT NULL,  -- Adicionando coluna aula_id
    FOREIGN KEY (user_id) REFERENCES usuarios(id)
);

CREATE TABLE IF NOT EXISTS progresso_atividades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    section_id INTEGER NOT NULL,
    aula_id INTEGER NOT NULL,  -- Adicionando coluna aula_id
    completou BOOLEAN NOT NULL DEFAULT 0,
    UNIQUE(user_id, section_id, aula_id),  -- Atualizando a restrição UNIQUE
    FOREIGN KEY(user_id) REFERENCES usuarios(id)
);
CREATE TABLE IF NOT EXISTS aulas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(255) NOT NULL,
    descricao TEXT
);