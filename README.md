# C2W - Plataforma de Ensino com Inteligência Artificial
![Uploading](logoC2W2.png)
O **C2W** é uma plataforma de ensino inovadora, desenvolvida utilizando o framework **Flask** e alimentada por Inteligência Artificial para proporcionar uma experiência de aprendizado personalizada e eficaz. Este projeto foi criado como parte do **Samsung Innovation Campus** com o objetivo de transformar a educação com o uso de tecnologias avançadas.

## Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Uso](#uso)
- [Contribuindo](#contribuindo)
- [Licença](#licença)
- [Autores](#autores)

## Sobre o Projeto

O **C2W** (Class to World) é uma plataforma de ensino online que utiliza Inteligência Artificial para adaptar o conteúdo educacional de acordo com o estilo de aprendizado do aluno. A plataforma permite a criação de cursos personalizados, que são otimizados continuamente com base no desempenho e nas preferências dos alunos, utilizando algoritmos de machine learning.

### Tecnologias Utilizadas

- Linguagem de Programação: Python
- Framework: Flask
- Inteligência Artificial: [TensorFlow/PyTorch/OpenAI API/Outro]
- Banco de Dados: [SQLite/PostgreSQL/MySQL]
- Outras Ferramentas: Docker, Git

## Funcionalidades

- **Cursos Personalizados:** A plataforma adapta o conteúdo e a dificuldade dos cursos conforme o progresso do aluno.
- **Inteligência Artificial:** O sistema é alimentado por algoritmos de machine learning que recomendam atividades e conteúdos baseados no comportamento do aluno.
- **Gestão de Cursos:** Criação, edição e gerenciamento de cursos para diferentes áreas de conhecimento.
- **Monitoramento de Progresso:** Relatórios detalhados sobre o desempenho dos alunos, com insights gerados por IA.

## Requisitos

Certifique-se de ter os seguintes requisitos instalados:

- Python 3.8 ou superior
- Flask 2.0 ou superior
- [Ferramenta de IA: TensorFlow/PyTorch]
- Docker (opcional para deploy)
- PostgreSQL/MySQL (ou outro banco de dados)

## Instalação

1. Clone o repositório:

    ```bash
    git clone https://github.com/allanlealluz/Projeto_Samsung
    ```

2. Acesse a pasta do projeto:

    ```bash
    cd c2w
    ```

3. Crie e ative o ambiente virtual:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

4. Instale as dependências:

    ```bash
    pip install -r requirements.txt
    ```

5. Configure as variáveis de ambiente:

    ```bash
    cp .env.example .env
    # Edite o arquivo .env conforme necessário
    ```

6. Execute o projeto:

    ```bash
    flask run
    ```

## Uso

Após a instalação, acesse a plataforma em `http://localhost:5000`. Cadastre-se e explore os cursos disponíveis. A plataforma irá monitorar seu progresso e sugerir novas atividades com base no seu desempenho.

## Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do repositório.
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFeature`).
3. Commit suas alterações (`git commit -m 'Adiciona NovaFeature'`).
4. Envie para o branch (`git push origin feature/NovaFeature`).
5. Abra um Pull Request.

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

## Autores

- **Allan Leal** - *Desenvolvedor Principal* - [Meu LinkedIn](https://br.linkedin.com/in/allan-leal-programmer)

## Agradecimentos

Agradecemos ao **Samsung Innovation Campus** por oferecer a oportunidade de desenvolver este projeto e adquirir conhecimentos em IA e desenvolvimento de software.

