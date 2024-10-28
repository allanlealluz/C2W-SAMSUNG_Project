import matplotlib.pyplot as plt
import os
import numpy as np
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
import matplotlib
matplotlib.use('Agg')
from collections import defaultdict

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
    plt.figure(figsize=(14, 10))

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
    plt.legend(title="Alunos", loc="upper right",bbox_to_anchor=(2, 2))

    plt.title('Notas dos Alunos por Aulas')
    plt.xlabel('Notas')
    plt.ylabel('Aulas')
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
        progresso = [entrada['progresso'] for entrada in dados['historico']]
        notas = [entrada['nota'] for entrada in dados['historico']]
        cor_aluno = cores[i]
        
        plt.plot(progresso, notas, color=cor_aluno, marker='o', label=f'{nome} (Real)', alpha=0.7)

        # Previsão de próxima nota e progresso
        if nome in previsoes:
            previsao = previsoes[nome]
            plt.scatter(previsao['proximo_progresso'], previsao['proxima_nota'], 
                        color=cor_aluno, marker='x', s=100, label=f'{nome} (Previsto)', alpha=1)

    plt.title('Desempenho dos Alunos: Progresso vs Notas')
    plt.xlabel('Progresso nas Aulas')
    plt.ylabel('Notas')
    plt.legend()
    plt.grid()

    img_dir = os.path.join(os.getcwd(), 'static', 'images')
    os.makedirs(img_dir, exist_ok=True)

    plot_url = os.path.join('static', 'images', 'performance_plot.png')
    plt.savefig(plot_url)
    plt.close()

    return plot_url

def prever_notas(alunos_data):
    previsoes = {}

    for nome, dados in alunos_data.items():
        progresso = []
        notas = []
        aulas = []

        # Extrai os dados de progresso, nota e aula
        historico = dados.get('historico', [])
        
        for entrada in historico:
            if 'progresso' in entrada and 'nota' in entrada and 'aula' in entrada:
                progresso.append(entrada['progresso'])
                notas.append(entrada['nota'])
                aulas.append(entrada['aula'])

        # Confere se há dados suficientes para treinar o modelo
        if len(progresso) >= 2 and len(set(progresso)) > 1:
            # Predição da nota
            X_nota = np.array(progresso).reshape(-1, 1)
            y_nota = np.array(notas)
            modelo_nota = LinearRegression()
            modelo_nota.fit(X_nota, y_nota)

            progresso_atual = dados.get('progresso', progresso[-1])
            proxima_nota = modelo_nota.predict(np.array([[progresso_atual]]))[0]

            # Predição da aula usando o progresso como referência
            X_aula = np.array(progresso).reshape(-1, 1)
            y_aula = np.array(aulas)
            modelo_aula = LinearRegression()
            modelo_aula.fit(X_aula, y_aula)

            proxima_aula = round(modelo_aula.predict(np.array([[progresso_atual]]))[0])

            previsoes[nome] = {
                'proxima_nota': proxima_nota,
                'proxima_aula': proxima_aula
            }
        else:
            # Usa a média se não houver dados suficientes
            previsoes[nome] = {
                'proxima_nota': np.mean(notas) if notas else dados.get('nota', None),
                'proxima_aula': max(aulas) + 1 if aulas else None
            }

    return previsoes
def generate_performance_by_topic_plot(alunos_data):
    if not alunos_data or not isinstance(alunos_data, list):
        raise ValueError("alunos_data deve ser uma lista.")

    notas_por_topico = defaultdict(list)

    for aluno in alunos_data:
        nome = aluno[1]
        nota = aluno[2]
        topico = aluno[3]

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

    plot_path = 'static/images/performance_by_topic_plot.png'
    plt.savefig(plot_path)
    plt.close()

    return 'performance_by_topic_plot.png'
