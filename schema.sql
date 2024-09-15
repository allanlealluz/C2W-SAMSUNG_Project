CREATE TABLE IF NOT EXISTS usuarios (
    id INT,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    senha varchar(255) NOT NULL,
    tipo TEXT NOT NULL,
    PRIMARY KEY (id)
);
CREATE TABLE IF NOT EXISTS respostas (
    id INT,
    user_id INT NOT NULL,
    section VARCHAR(255) NOT NULL,
    response TEXT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (user_id) REFERENCES usuarios(id)
);