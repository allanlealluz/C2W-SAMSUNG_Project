CREATE TABLE IF NOT EXISTS usuarios (
    id INT,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    senha varchar(255) NOT NULL,
    PRIMARY KEY (id)
)