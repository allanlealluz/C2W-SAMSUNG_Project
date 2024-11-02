import matplotlib.pyplot as plt
import numpy as np
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
import matplotlib
matplotlib.use('Agg')
from collections import defaultdict

def kmeans_clustering(alunos_data):
    notas = np.array([nota for _, _, nota, _, _ in alunos_data if isinstance(nota, (int, float))]).reshape(-1, 1)

    if notas.size == 0:
        return None, None, None

    num_clusters = min(3, len(set(notas.flatten())))
    kmeans = KMeans(n_clusters=num_clusters, random_state=0, n_init=10)

    labels = kmeans.fit_predict(notas)
    centroids = kmeans.cluster_centers_

    return notas, labels, centroids

def generate_cluster_plot(X, labels, centroids, alunos_data):
    plt.figure(figsize=(16, 12))

    topicos = sorted(set(aluno[4] for aluno in alunos_data if len(aluno) > 4))
    if not topicos:
        return None

    topico_indices = {topico: i for i, topico in enumerate(topicos)}

    unique_alunos = sorted(set(aluno[1] for aluno in alunos_data))
    colors = plt.cm.viridis(np.linspace(0, 1, len(unique_alunos)))
    aluno_colors = {nome: colors[i] for i, nome in enumerate(unique_alunos)}

    jitter_strength_x = 0.1
    jitter_strength_y = 0.1

    notas_por_aluno = defaultdict(list)

    for aluno in alunos_data:
        if len(aluno) < 4:
            continue

        nome = aluno[1]
        nota = aluno[2]
        topico = aluno[4]
        notas_por_aluno[nome].append((nota, topico))

    # Plotar notas de cada aluno
    for aluno, notas in notas_por_aluno.items():
        for nota, topico in notas:
            y_pos = topico_indices[topico]
            x_pos = float(nota) + np.random.uniform(-jitter_strength_x, jitter_strength_x)  # Jitter em X
            y_pos += np.random.uniform(-jitter_strength_y, jitter_strength_y)  # Jitter em Y
            plt.scatter(x_pos, y_pos, color=aluno_colors[aluno], marker='o', edgecolor='k', s=100, alpha=0.7)

    for aluno, color in aluno_colors.items():
        plt.scatter([], [], color=color, label=aluno, marker='o', s=100)
    plt.legend(title="Alunos", loc="upper right", bbox_to_anchor=(1.10, 1))

    plt.title('Notas dos Alunos por Aulas')
    plt.xlabel('Notas')
    plt.ylabel('Aulas')
    plt.yticks(range(len(topicos)), topicos)

    plt.xlim(0, 11)
    plt.grid(True, linestyle='--', linewidth=0.5)

    plot_path = 'mysite/static/images/cluster_plot.png'
    plt.savefig(plot_path)
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

    student_performance_plot_path = 'mysite/static/images/Performance.png'
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

    plot_url = 'mysite/static/images/performance_plot.png'
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

def generate_performance_by_topic_plot(alunos_data):
    if not alunos_data or not isinstance(alunos_data, list):
        raise ValueError("alunos_data deve ser uma lista.")

    notas_por_topico = defaultdict(list)

    for aluno in alunos_data:
        nome = aluno[1]
        nota = aluno[2]
        topico = aluno[4]

        try:
            nota = float(nota)
        except ValueError:
            raise ValueError(f"A nota '{nota}' para o aluno '{nome}' não é um número válido.")

        notas_por_topico[topico].append(nota)

    medias_por_topico = {topico: np.mean(notas) for topico, notas in notas_por_topico.items()}
    topicos = list(medias_por_topico.keys())
    medias = list(medias_por_topico.values())

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(topicos, medias, color='skyblue')
    ax.set_xlabel('Média das Notas')
    ax.set_ylabel('Tópicos')
    ax.set_title('Desempenho dos Alunos por Tópico')

    for index, value in enumerate(medias):
        ax.text(value, index, f"{value:.2f}")

    plot_path = 'mysite/static/images/performance_by_topic_plot.png'
    plt.savefig(plot_path)
    plt.close()

    return 'performance_by_topic_plot.png'

def classificar_alunos_por_grupos(notas):
    media_nota = np.mean(notas) if notas else 0
    if media_nota < 5:
        return "Baixas Notas"
    elif 5 <= media_nota < 7:
        return "Notas Médias"
    else:
        return "Altas Notas"
