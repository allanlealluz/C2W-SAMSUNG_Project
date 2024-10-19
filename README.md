# C2W - Plataforma de Ensino com Inteligência Artificial

![C2W Logo](logoC2W2.png)

**C2W** é uma plataforma inovadora criada para atender às necessidades de ensino de robótica e programação para alunos do ensino fundamental. A plataforma faz a intermediação entre professores e alunos, dispondo de um design UX intuitivo, ferramentas de estatística e uso de IA para predição e análise do desempenho dos alunos, fornecendo feedbacks valiosos para que os professores possam adequar seus conteúdos de maneira mais eficaz.

## Tabela de Conteúdos

- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Uso](#uso)
- [Contribuição](#contribuição)
- [Licença](#licença)
- [Autores](#autores)
- [Agradecimentos](#agradecimentos)

## Sobre o Projeto

**C2W** (Class to World) é uma plataforma de aprendizagem online que utiliza Inteligência Artificial para monitorar e analisar o desempenho dos alunos, fornecendo feedbacks detalhados para os professores. Dessa forma, os professores podem ajustar o conteúdo de ensino para atender melhor às necessidades dos alunos.

### Tecnologias Utilizadas

- Linguagem de Programação: Python
- Framework: Flask
- Inteligência Artificial: Matplotlib, Sklearn
- Banco de Dados: SQLite3
- Outras Ferramentas: Git

## Funcionalidades

- **Monitoramento Personalizado:** A plataforma adapta o acompanhamento do desempenho dos alunos com base no progresso de cada um.
- **Inteligência Artificial:** O sistema é alimentado por algoritmos de aprendizado de máquina que analisam o comportamento dos alunos.
- **Gestão de Cursos:** Ferramentas para auxiliar os professores na criação, edição e gestão de cursos.
- **Análise de Desempenho:** Relatórios detalhados sobre o desempenho dos alunos, com insights gerados por IA.

## Requisitos

Certifique-se de ter os seguintes requisitos instalados:

- Python 3.8 ou superior
- Flask 3.0 ou superior
- Matplotlib, Sklearn
- SQLite3

## Instalação

Clone o repositório:
```bash
https://github.com/allanlealluz/C2W-SAMSUNG_Project
  ```
## Installation

1. Clone the repository:

    ```bash
   https://github.com/allanlealluz/C2W-SAMSUNG_Project
    ```

2. Navigate to the project directory:

    ```bash
    cd C2W-SAMSUNG_Project
    ```

3. Create and activate the virtual environment:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

4. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

5. Configure environment variables:

    ```bash
    cp .env.example .env
    # Edit the .env file as necessary
    ```

6. Run the project:

    ```bash
    python app.py
    ```

## Usage

After installation, access the platform at `127.0.0.1:5000`. Register and explore the available courses. The platform will monitor your progress and suggest new activities based on your performance.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a branch for your feature (`git checkout -b feature/NewFeature`).
3. Commit your changes (`git commit -m 'Add NewFeature'`).
4. Push to the branch (`git push origin feature/NewFeature`).
5. Open a Pull Request.

## License

This project is licensed under the [MIT License](LICENSE).

## Authors

- **Allan Leal** - *Lead Developer* - [My LinkedIn](https://br.linkedin.com/in/allan-leal-programmer)

## Acknowledgments

Thanks to the **Samsung Innovation Campus** for the opportunity to develop this project and gain knowledge in AI and software development.
