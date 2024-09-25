CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,  -- Adicionando restrição UNIQUE ao email
    senha VARCHAR(255) NOT NULL,
    tipo TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS aulas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    professor_id INTEGER NOT NULL,  -- ID do professor que criou a aula
    titulo VARCHAR(255) NOT NULL,
    descricao TEXT,
    conteudo_nome VARCHAR(255), -- Nome do conteúdo (caso seja PDF ou outro arquivo)
    topico VARCHAR(255), -- Tópico da aula
    FOREIGN KEY (professor_id) REFERENCES usuarios(id)
);

CREATE TABLE IF NOT EXISTS respostas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    section VARCHAR(255) NOT NULL,
    response TEXT NOT NULL,
    aula_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES usuarios(id),
    FOREIGN KEY (aula_id) REFERENCES aulas(id) -- Adicionando referência à tabela aulas
);

CREATE TABLE IF NOT EXISTS progresso_atividades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    section_id INTEGER NOT NULL,
    aula_id INTEGER NOT NULL,
    completou BOOLEAN NOT NULL DEFAULT 0,
    UNIQUE(user_id, section_id, aula_id),  -- Atualizando a restrição UNIQUE
    FOREIGN KEY(user_id) REFERENCES usuarios(id),
    FOREIGN KEY(aula_id) REFERENCES aulas(id) -- Adicionando referência à tabela aulas
);
