import chainlit as cl

@cl.set_starters
async def set_starters():
    return [
        cl.Starter(
            id = "iniciante",
            label="Sou um total iniciante em python.",
            message="Sou um total iniciante em python.",
            icon="/public/idea.svg",
            ),

        cl.Starter(
            id = "intermediario",
            label="Sou intermediario em python.",
            message="Sou intermediario em python.",
            icon="/public/learn.svg",
            ),
        cl.Starter(
            id = "Avançado",
            label="sou avançado em python.",
            message="sou avançado em python.",
            icon="/public/terminal.svg",
            ),

        ]


@cl.on_message
async def main(message: cl.Message):
    if "iniciante" in message.content.lower():
        await cl.Message(content="Como você é um iniciante seus conhecimentos devem ser:\n1. Conhecimento Básico de Computação: \nAntes de começar a programar em Python, é importante ter uma compreensão básica do funcionamento dos computadores. Isso inclui entender o que são sistemas operacionais, como navegar por pastas e arquivos, e como usar um editor de texto ou um ambiente de desenvolvimento integrado (IDE).\n\n\n2. Habilidades Básicas em Lógica de Programação: \n\n Uma boa base em lógica de programação é essencial. Isso inclui compreender conceitos como variáveis, operadores, estruturas de controle de fluxo (condicionais e loops) e funções. Embora você possa aprender esses conceitos enquanto estuda Python, ter uma noção básica ajudará a acelerar o processo de aprendizado.\n\n\n 3. Motivação e Curiosidade: \n\nA programação é uma habilidade que exige prática e paciência. Ter motivação e curiosidade para resolver problemas e criar projetos ajudará a manter o interesse e a superar desafios ao longo do aprendizado.\n\n Com esses pré-requisitos em mente, você estará bem preparado para iniciar sua jornada no mundo da programação em Python. Lembre-se de que a prática constante e a curiosidade são chave para o sucesso. Boa sorte!",).send()
    elif "intermediario" in message.content.lower():
        await cl.Message(content="""
Fundamentos Sólidos:

1. Conhecimento avançado dos conceitos básicos, como tipos de dados, controle de fluxo, e funções.
Programação Orientada a Objetos (POO):

2. Habilidade em usar classes, herança e polimorfismo para estruturar o código.
Manipulação de Dados e Banco de Dados:

3. Experiência com bibliotecas como pandas e numpy, e interação com bancos de dados SQL e NoSQL.
Bibliotecas e Frameworks:

4. Familiaridade com ferramentas e frameworks como requests, Flask ou Django, e pytest para testes.
Boas Práticas e Desenvolvimento de Código:

5. Aplicação de boas práticas de codificação, uso de controle de versão (Git), e habilidades em depuração e otimização.

Esses pontos cobrem as competências essenciais que definem um programador intermediário em Python.
""",).send()

# ...

