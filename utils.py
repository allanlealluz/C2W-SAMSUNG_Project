import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
import matplotlib
matplotlib.use('Agg')
from collections import defaultdict

def kmeans_clustering(alunos_data):
    notas = np.array([nota for _, _, nota, _, _, _ in alunos_data if isinstance(nota, (int, float))]).reshape(-1, 1)

    if notas.size == 0:
        return None, None, None

    num_clusters = min(3, len(set(notas.flatten())))
    kmeans = KMeans(n_clusters=num_clusters, random_state=0, n_init=10)

    labels = kmeans.fit_predict(notas)
    centroids = kmeans.cluster_centers_

    return notas, labels, centroids

def generate_cluster_plot(X, labels, centroids, alunos_data):
    plt.figure(figsize=(16, 12))
    cursos_modulos = defaultdict(list)
    for aluno in alunos_data:
        if len(aluno) < 6:
            continue
        curso = aluno[5]
        modulo = aluno[4]
        if modulo not in cursos_modulos[curso]:
            cursos_modulos[curso].append(modulo)
    cursos_modulos_indices = {}
    index = 0
    for curso, modulos in sorted(cursos_modulos.items()):
        for modulo in sorted(modulos):
            cursos_modulos_indices[(curso, modulo)] = index
            index += 1
    unique_alunos = sorted(set(aluno[1] for aluno in alunos_data))
    colors = plt.cm.viridis(np.linspace(0, 1, len(unique_alunos)))  
    aluno_colors = {nome: colors[i] for i, nome in enumerate(unique_alunos)}
    jitter_strength_y = 0.1  
    notas_por_aluno = defaultdict(list)

    for aluno in alunos_data:
        if len(aluno) < 6:
            continue

        nome = aluno[1]  
        nota = aluno[2] 
        modulo = aluno[4]  
        curso = aluno[5]  
        notas_por_aluno[nome].append((nota, modulo, curso)) 
    for aluno, notas in notas_por_aluno.items():
        for nota, modulo, curso in notas:
            y_pos = cursos_modulos_indices[(curso, modulo)]
            x_pos = float(nota)
            y_pos += np.random.uniform(-jitter_strength_y, jitter_strength_y)
            plt.scatter(x_pos, y_pos, color=aluno_colors[aluno], marker='o', edgecolor='k', s=100, alpha=0.7)
    for aluno, color in aluno_colors.items():
        plt.scatter([], [], color=color, label=aluno, marker='o', s=100)
    plt.legend(title="Alunos", loc="upper right", bbox_to_anchor=(1.10, 1))
    plt.title('Notas dos Alunos por Cursos e Módulos')
    plt.xlabel('Notas')
    plt.ylabel('Cursos e Módulos')
    y_labels = [f"{curso} - {modulo}" for curso, modulo in sorted(cursos_modulos_indices.keys())]
    plt.yticks(range(len(y_labels)), y_labels)

    plt.xlim(0, 11)
    plt.grid(True, linestyle='--', linewidth=0.5)

    plot_path = 'static/images/cluster_plot.png'
    plt.savefig(plot_path, bbox_inches='tight')
    plt.close()

    return 'cluster_plot.png'

def generate_student_performance_plot(alunos_data):
    if not alunos_data or not isinstance(alunos_data, list):
        raise ValueError("alunos_data deve ser uma lista.")

    notas_por_aluno = defaultdict(float)
    contagem_por_aluno = defaultdict(int)

    for aluno in alunos_data:
        nota = aluno[2]
        nome = aluno[1]

        try:
            nota = float(nota)
        except ValueError:
            raise ValueError(f"A nota '{nota}' para o aluno '{nome}' não é um número válido.")

        notas_por_aluno[nome] += nota
        contagem_por_aluno[nome] += 1

    alunos_nomes = list(notas_por_aluno.keys())
    alunos_notas = [notas_por_aluno[nome] / contagem_por_aluno[nome] for nome in alunos_nomes]

    alunos_data_sorted = sorted(zip(alunos_nomes, alunos_notas), key=lambda x: x[1], reverse=True)
    alunos_nomes_sorted, alunos_notas_sorted = zip(*alunos_data_sorted)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(alunos_nomes_sorted, alunos_notas_sorted, color='skyblue')
    ax.set_xlabel('Notas (Média)')
    ax.set_ylabel('Alunos')
    ax.set_title('Desempenho dos Alunos (Média das Notas)')

    for index, value in enumerate(alunos_notas_sorted):
        ax.text(value, index, f"{value:.2f}")

    student_performance_plot_path = 'static/images/Performance.png'
    plt.savefig(student_performance_plot_path)
    plt.close()

    return 'Performance.png'

def generate_performance_plot(alunos_data, previsoes):
    plt.figure(figsize=(10, 6))

    cores = plt.cm.viridis(np.linspace(0, 1, len(alunos_data)))

    max_aulas = 0

    for i, (nome, dados) in enumerate(alunos_data.items()):
        notas = [entry['nota'] for entry in dados['historico']]
        max_aulas = max(max_aulas, len(notas))
        cor_aluno = cores[i]
        plt.plot(notas, color=cor_aluno, marker='o', label=f'{nome} (Real)', alpha=0.7)

        if nome in previsoes:
            previsao = previsoes[nome]
            plt.scatter(len(notas), previsao['proxima_nota'],
                        color=cor_aluno, marker='x', s=100, label=f'{nome} (Previsto)', alpha=1)

    plt.title('Desempenho dos Alunos: Notas Históricas e Previstas')
    plt.xlabel('Respostas')
    plt.ylabel('Notas')
    plt.xticks(range(max_aulas + 1))
    plt.xlim(-0.5, max_aulas + 0.5)
    plt.ylim(0, 10.5)
    plt.legend()
    plt.grid()

    plot_url = 'static/images/performance_plot.png'
    plt.savefig(plot_url)
    plt.close()

    return "performance_plot.png"



def prever_notas(alunos_data):
    previsoes = {}

    for nome, dados in alunos_data.items():
        historico_progresso = [entry['progresso'] for entry in dados['historico']]
        historico_notas = [entry['nota'] for entry in dados['historico']]

        if len(historico_progresso) >= 3:
            X_hist = np.array(historico_progresso).reshape(-1, 1)
            y_notas = np.array(historico_notas)

            modelo_notas = LinearRegression()
            modelo_notas.fit(X_hist, y_notas)

            tendencia_nota = modelo_notas.coef_[0]

            modelo_progresso = LinearRegression()
            modelo_progresso.fit(X_hist, np.array(historico_progresso))

            tendencia_progresso = modelo_progresso.coef_[0]

            decaimento_nota = tendencia_nota < 0
            decaimento_progresso = tendencia_progresso < 0

            proximo_progresso = historico_progresso[-1] + 1
            proxima_nota = modelo_notas.predict(np.array([[proximo_progresso]]))[0]

            previsoes[nome] = {
                'proxima_nota': proxima_nota,
                'proximo_progresso': proximo_progresso,
                'decaimento_nota': decaimento_nota,
                'decaimento_progresso': decaimento_progresso
            }
        else:
            previsoes[nome] = {
                'proxima_nota': np.mean(historico_notas) if historico_notas else 0,
                'proximo_progresso': (historico_progresso[-1] + 1) if historico_progresso else 1,
                'decaimento_nota': False,
                'decaimento_progresso': False
            }

    return previsoes

def generate_performance_by_module_plot(alunos_data):
    if not alunos_data or not isinstance(alunos_data, list):
        raise ValueError("alunos_data deve ser uma lista.")

    notas_por_curso_modulo = defaultdict(list)

    for aluno in alunos_data:
        nome = aluno[1] 
        nota = aluno[2]   
        curso = aluno[4]  
        modulo = aluno[5] 
        print(f"dados gerais do aluno: {nome}, {nota}, {curso}, {modulo}")
        try:
            nota = float(nota)
        except ValueError:
            raise ValueError(f"A nota '{nota}' para o aluno '{nome}' não é um número válido.")
        notas_por_curso_modulo[(curso, modulo)].append(nota)
        print(f"notas_por_curso_modulo: {notas_por_curso_modulo}")
    medias_por_curso_modulo = {
        (curso, modulo): np.mean(notas) for (curso,modulo), notas in notas_por_curso_modulo.items()
    }
    print(f"medias_por_curso_modulo: {medias_por_curso_modulo}")
    cursos_modulos = [f"{curso} - {modulo}" for curso, modulo in medias_por_curso_modulo.keys()]
    medias = list(medias_por_curso_modulo.values())
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.barh(cursos_modulos, medias, color='skyblue')
    ax.set_xlabel('Média das Notas')
    ax.set_ylabel('Cursos e Módulos')
    ax.set_title('Desempenho dos Alunos por Curso e Módulo')

    for index, value in enumerate(medias):
        ax.text(value, index, f"{value:.2f}")
    plt.subplots_adjust(left=0.2)
    plot_path = 'static/images/performance_by_module_plot.png'
    plt.savefig(plot_path)
    plt.close()

    return 'performance_by_module_plot.png'


def classificar_alunos_por_grupos(notas):
    media_nota = np.mean(notas) if notas else 0
    if media_nota < 5:
        return "Baixas Notas"
    elif 5 <= media_nota < 7:
        return "Notas Médias"
    else:
        return "Altas Notas"
