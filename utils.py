import matplotlib.pyplot as plt
import os
import numpy as np
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
import matplotlib
matplotlib.use('Agg')
from collections import defaultdict

def generate_cluster_plot(X, labels, centroids, alunos_data):
    perguntas = [d['pergunta'] for d in alunos_data]
    aulas = [d['aula'] for d in alunos_data]
    scores = np.array([d['nota'] for d in alunos_data])

    unique_perguntas = list(set(perguntas))
    unique_aulas = list(set(aulas))

    performance_data = {pergunta: [] for pergunta in unique_perguntas}

    for pergunta in unique_perguntas:
        for aula in unique_aulas:
            filtered_scores = [scores[i] for i in range(len(perguntas)) if perguntas[i] == pergunta and aulas[i] == aula]
            performance_data[pergunta].append(np.mean(filtered_scores) if filtered_scores else 0)

    fig, ax = plt.subplots()
    width = 0.15
    x = np.arange(len(unique_aulas))

    for i, pergunta in enumerate(unique_perguntas):
        ax.bar(x + i * width, performance_data[pergunta], width, label=pergunta)

    ax.set_xlabel('Aulas')
    ax.set_ylabel('Média das Notas')
    ax.set_title('Desempenho dos Alunos por Pergunta e Aula')
    ax.set_xticks(x + width / 2)
    ax.set_xticklabels(unique_aulas)
    ax.legend()

    plot_path = 'static/plots/performance_plot.png'
    plt.savefig(plot_path)
    plt.close()
    
    return plot_path

def kmeans_clustering(alunos_data):
    notas = np.array([nota for _, _, nota, _ in alunos_data]).reshape(-1, 1)

    if notas.size == 0:
        return None, None, None

    num_clusters = 3 
    kmeans = KMeans(n_clusters=num_clusters, random_state=0)

    labels = kmeans.fit_predict(notas)
    centroids = kmeans.cluster_centers_

    return notas, labels, centroids

def generate_cluster_plot(X, labels, centroids, alunos_data):
    plt.figure(figsize=(12, 8))

    topicos = sorted(set(aluno[3] for aluno in alunos_data))
    topico_indices = {topico: i for i, topico in enumerate(topicos)}

    unique_alunos = sorted(set(aluno[1] for aluno in alunos_data))
    colors = plt.cm.viridis(np.linspace(0, 1, len(unique_alunos)))
    aluno_colors = {nome: colors[i] for i, nome in enumerate(unique_alunos)}

    jitter_strength_x = 0.1
    jitter_strength_y = 0.2

    notas_por_aluno = defaultdict(list)

    for aluno in alunos_data:
        nome = aluno[1]
        nota = aluno[2]
        topico = aluno[3]
        notas_por_aluno[nome].append((nota, topico))

    for aluno, notas in notas_por_aluno.items():
        for nota, topico in notas:
            y_pos = topico_indices[topico]
            x_pos = nota + np.random.uniform(-jitter_strength_x, jitter_strength_x)
            y_pos += np.random.uniform(-jitter_strength_y, jitter_strength_y)
            plt.scatter(x_pos, y_pos, color=aluno_colors[aluno], marker='o', edgecolor='k', s=100, alpha=0.7)
    
    for aluno, color in aluno_colors.items():
        plt.scatter([], [], color=color, label=aluno, marker='o', s=100)
    plt.legend(title="Alunos", loc="upper right")

    plt.title('Notas dos Alunos por Tópico')
    plt.xlabel('Notas')
    plt.ylabel('Tópicos')
    plt.yticks(range(len(topicos)), topicos)
    plt.grid(True, linestyle='--', linewidth=0.5)

    plot_path = 'static/images/cluster_plot.png'
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

    student_performance_plot_path = 'static/images/Performance.png'
    plt.savefig(student_performance_plot_path)
    plt.close()

    return 'Performance.png'

def generate_performance_plot(alunos_data, previsoes):
    plt.figure(figsize=(10, 6))
    
    cores = plt.cm.viridis(np.linspace(0, 1, len(alunos_data)))

    for i, (nome, dados) in enumerate(alunos_data.items()):
        media_nota = dados['nota']
        progresso = dados['progresso']
        cor_aluno = cores[i]
        
        plt.scatter(media_nota, progresso, color=cor_aluno, label=f'{nome} (Real)', alpha=0.7)

        if nome in previsoes:
            previsao = previsoes[nome]
            plt.scatter(media_nota, previsao, marker='x', color=cor_aluno, s=100, label=f'{nome} (Previsto)', alpha=1)

    plt.title('Desempenho dos Alunos: Média das Notas vs Progresso')
    plt.xlabel('Média das Notas dos Alunos')
    plt.ylabel('Progresso nas aulas')
    plt.legend()
    plt.grid()

    img_dir = os.path.join(os.getcwd(), 'static', 'images')
    os.makedirs(img_dir, exist_ok=True)

    plot_url = os.path.join('static', 'images', 'performance_plot.png')
    plt.savefig(plot_url)
    plt.close()

    return plot_url, previsoes

def prever_notas(alunos_data):
    previsoes = {}

    for nome, dados in alunos_data.items():
        progresso = []
        notas = []
        
        if 'historico' in dados:
            for entrada in dados['historico']:
                progresso.append(entrada['progresso'])
                notas.append(entrada['nota'])

        if len(progresso) >= 2 and len(set(progresso)) > 1:
            X = np.array(progresso).reshape(-1, 1)
            y = np.array(notas)

            model = LinearRegression()
            model.fit(X, y)
            
            proxima_nota = model.predict(np.array([[dados['progresso']]]))[0]
            previsoes[nome] = proxima_nota
        else:
            previsoes[nome] = np.mean(notas) if notas else dados.get('nota', None)

    return previsoes
