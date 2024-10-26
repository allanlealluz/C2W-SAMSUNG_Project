import matplotlib.pyplot as plt
import io
import base64
import os
import numpy as np
from sklearn.cluster import KMeans
import spacy
from sklearn.linear_model import LinearRegression
import matplotlib
matplotlib.use('Agg')
from collections import defaultdict

nlp = spacy.load('pt_core_news_sm')

def generate_cluster_plot(X, labels, centroids, alunos_data):
    # Converter os dados dos alunos para um formato que possa ser plotado
    # Supondo que alunos_data seja uma lista de dicionários ou algo similar
    perguntas = [d['pergunta'] for d in alunos_data]  # Exemplo de como extrair perguntas
    aulas = [d['aula'] for d in alunos_data]  # Exemplo de como extrair aulas
    scores = np.array([d['nota'] for d in alunos_data])  # Extrair notas
    
    # Agrupar por perguntas e aulas
    unique_perguntas = list(set(perguntas))
    unique_aulas = list(set(aulas))
    
    # Criar um dicionário para armazenar as notas por pergunta e aula
    performance_data = {pergunta: [] for pergunta in unique_perguntas}
    
    for pergunta in unique_perguntas:
        for aula in unique_aulas:
            filtered_scores = [scores[i] for i in range(len(perguntas)) if perguntas[i] == pergunta and aulas[i] == aula]
            performance_data[pergunta].append(np.mean(filtered_scores) if filtered_scores else 0)

    # Criar o gráfico de barras
    fig, ax = plt.subplots()
    width = 0.15  # Largura das barras
    x = np.arange(len(unique_aulas))

    for i, pergunta in enumerate(unique_perguntas):
        ax.bar(x + i * width, performance_data[pergunta], width, label=pergunta)

    ax.set_xlabel('Aulas')
    ax.set_ylabel('Média das Notas')
    ax.set_title('Desempenho dos Alunos por Pergunta e Aula')
    ax.set_xticks(x + width / 2)
    ax.set_xticklabels(unique_aulas)
    ax.legend()

    # Salvar o gráfico e retornar a URL
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

    # Aplicar KMeans
    labels = kmeans.fit_predict(notas)
    centroids = kmeans.cluster_centers_

    return notas, labels, centroids


def generate_cluster_plot(X, labels, centroids, alunos_data):
    plt.figure(figsize=(10, 6))

    plt.scatter(X[:, 0], np.zeros_like(X[:, 0]), c=labels, cmap='viridis', marker='o', edgecolor='k', s=100)
    plt.scatter(centroids[:, 0], np.zeros_like(centroids[:, 0]), color='red', s=200, alpha=0.5, marker='X')
    for i, aluno in enumerate(alunos_data):
        aluno_id, nome, nota, topico = aluno
        plt.annotate(f"{nome}", (X[i, 0], 0), textcoords="offset points", xytext=(0, 10), ha='center', fontsize=8)

    plt.title('Distribuição das Notas dos Alunos')
    plt.xlabel('Notas')
    plt.yticks([])  
    plt.colorbar(label='Clusters')
    plt.grid(True)
    plt.savefig('static/images/cluster_plot.png')  
    plt.close()
    
    return 'cluster_plot.png'



def generate_student_performance_plot(alunos_data):
    if not alunos_data or not isinstance(alunos_data, list):
        raise ValueError("alunos_data deve ser uma lista.")
    notas_por_aluno = defaultdict(float)
    for aluno in alunos_data:
        nota = aluno[2]
        nome = aluno[1]  
        
        print(f"Processando aluno: {nome}, Nota: {nota}") 
        
        try:
            nota = float(nota)
        except ValueError:
            raise ValueError(f"A nota '{nota}' para o aluno '{nome}' não é um número válido.")
        
        notas_por_aluno[nome] += nota

    alunos_nomes = list(notas_por_aluno.keys())
    alunos_notas = list(notas_por_aluno.values())
    alunos_data_sorted = zip(alunos_nomes, alunos_notas)
    alunos_nomes_sorted, alunos_notas_sorted = zip(*alunos_data_sorted)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(alunos_nomes_sorted, alunos_notas_sorted, color='skyblue')
    ax.set_xlabel('Notas')
    ax.set_ylabel('Alunos')
    ax.set_title('Desempenho dos Alunos (Soma das Notas)')
    for index, value in enumerate(alunos_notas_sorted):
        ax.text(value, index, str(value))
    student_performance_plot_path = 'static/images/Performance.png'
    plt.savefig(student_performance_plot_path)
    plt.close()

    return 'Performance.png'
def generate_performance_plot(alunos_data):
    plt.figure(figsize=(10, 6))
    
    previsoes = {}
    for nome, progresso in alunos_data.items():
        X = np.arange(1, len(progresso) + 1).reshape(-1, 1) 
        y = np.array(progresso) 
        
        model = LinearRegression()
        model.fit(X, y)
        
        proxima_aula = len(progresso) + 1
        desempenho_previsto = model.predict([[proxima_aula]])[0]
        previsoes[nome] = desempenho_previsto

        plt.plot(X, y, marker='o', label=f'{nome} (Progresso Passado)')
        plt.scatter([proxima_aula], [desempenho_previsto], color='red', label=f'{nome} (Previsto)')

    plt.title('Desempenho dos Alunos e Previsão de Desempenho Futuro')
    plt.xlabel('Aulas')
    plt.ylabel('Progresso (0 = Incompleto, 1 = Completo)')
    plt.legend()

    # Salvar o gráfico
    img_dir = os.path.join(os.getcwd(), 'static', 'images')
    os.makedirs(img_dir, exist_ok=True)

    plot_url= os.path.join('static', 'images','performance_plot.png')
    plt.savefig(plot_url)
    plt.close()

    return plot_url, previsoes
def prever_desempenho_futuro(alunos_data):
    X = np.array([[data[0], data[1]] for data in alunos_data.values()]) 
    y = np.array([data[2] for data in alunos_data.values()])  

    model = LinearRegression()
    model.fit(X, y)

    previsoes = model.predict(X)
    return previsoes