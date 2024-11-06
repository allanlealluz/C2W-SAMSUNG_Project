CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    senha VARCHAR(255) NOT NULL,
    tipo TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cursos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT
);
CREATE TABLE IF NOT EXISTS inscricoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_id INTEGER NOT NULL,
    curso_id INTEGER NOT NULL,
    data_inscricao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (aluno_id) REFERENCES usuarios(id),
    FOREIGN KEY (curso_id) REFERENCES cursos(id)
);
CREATE TABLE IF NOT EXISTS modulos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    descricao TEXT,
    curso_id INTEGER,
    professor_id INTEGER,
    FOREIGN KEY (curso_id) REFERENCES cursos(id),
    FOREIGN KEY (professor_id) REFERENCES usuarios(id)
);

CREATE TABLE IF NOT EXISTS aulas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    modulo_id INTEGER NOT NULL,
    titulo TEXT NOT NULL,
    descricao TEXT,
    conteudo_nome TEXT,
    arquivo TEXT,
    FOREIGN KEY (modulo_id) REFERENCES modulos(id)
);

CREATE TABLE IF NOT EXISTS perguntas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aula_id INTEGER NOT NULL,
    texto TEXT NOT NULL,
    FOREIGN KEY (aula_id) REFERENCES aulas(id)
);

CREATE TABLE IF NOT EXISTS respostas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    pergunta_id INTEGER NOT NULL,
    resposta TEXT NOT NULL,
    nota INTEGER,
    FOREIGN KEY (user_id) REFERENCES usuarios(id),
    FOREIGN KEY (pergunta_id) REFERENCES perguntas(id)
);

CREATE TABLE IF NOT EXISTS progresso_atividades (
    user_id INTEGER NOT NULL,
    modulo_id INTEGER NOT NULL,
    aula_id INTEGER NOT NULL,
    completou BOOLEAN NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, modulo_id, aula_id),
    FOREIGN KEY (user_id) REFERENCES usuarios(id),
    FOREIGN KEY (aula_id) REFERENCES aulas(id),
    FOREIGN KEY (modulo_id) REFERENCES modulos(id)
);

CREATE TABLE IF NOT EXISTS progresso_aulas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    aula_id INTEGER NOT NULL,
    concluida BOOLEAN DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES usuarios(id),
    FOREIGN KEY (aula_id) REFERENCES aulas(id)
);

CREATE TABLE IF NOT EXISTS progresso_cursos (
    user_id INTEGER NOT NULL,
    curso_id INTEGER NOT NULL,
    progresso FLOAT DEFAULT 0,
    PRIMARY KEY (user_id, curso_id),
    FOREIGN KEY (user_id) REFERENCES usuarios(id),
    FOREIGN KEY (curso_id) REFERENCES cursos(id)
);
