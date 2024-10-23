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

nlp = spacy.load('pt_core_news_sm')

def generate_plot(data, title, x_label, y_label):
    fig, ax = plt.subplots()
    ax.bar(data.keys(), data.values(), color='blue')
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    
    # Converte o gráfico para base64
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close(fig)
    
    return plot_url

def kmeans_clustering(alunos_data):
    if len(alunos_data) >= 3:
        # Adicionamos as notas ao array de dados
        X = np.array([[data[0], data[1], data[2]] for data in alunos_data.values()])
        kmeans = KMeans(n_clusters=3, random_state=42)
        labels = kmeans.fit_predict(X)
        centroids = kmeans.cluster_centers_
        return X, labels, centroids
    return None, None, None


def generate_cluster_plot(X, labels, centroids, nomes_alunos):
    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(X[:, 0], X[:, 1], c=labels, cmap='viridis', marker='o', edgecolor='k', s=100)

    plt.scatter(centroids[:, 0], centroids[:, 1], c='red', marker='X', s=200, label='Centroides')
    for i, nome in enumerate(nomes_alunos):
        plt.annotate(nome, (X[i, 0], X[i, 1]), fontsize=9, ha='right')

    plt.title('Perfis de Alunos Baseados em Progresso e Feedbacks')
    plt.xlabel('Progresso Médio (%)')
    plt.ylabel('Quantidade de Feedbacks')
    plt.grid()
    plt.legend()

    img_dir = os.path.join(os.getcwd(), 'static', 'images')
    os.makedirs(img_dir, exist_ok=True)

    plot_url = os.path.join(img_dir, 'cluster_plot.png')
    plt.savefig(plot_url)
    plt.close()
    
    return plot_url

def extract_keywords(text):
    doc = nlp(text)
    keywords = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct][:3]
    return keywords

def generate_performance_plot(alunos_data):
    plt.figure(figsize=(10, 6))
    
    previsoes = {}
    for nome, progresso in alunos_data.items():
        # Preparar dados para regressão
        X = np.arange(1, len(progresso) + 1).reshape(-1, 1)  # Aulas (1, 2, 3, ...)
        y = np.array(progresso)  # Progresso do aluno (0 ou 1)
        
        # Modelo de Regressão Linear
        model = LinearRegression()
        model.fit(X, y)
        
        # Previsão do desempenho na próxima aula
        proxima_aula = len(progresso) + 1
        desempenho_previsto = model.predict([[proxima_aula]])[0]
        previsoes[nome] = desempenho_previsto

        # Plotar desempenho passado e previsão
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
    X = np.array([[data[0], data[1]] for data in alunos_data.values()])  # Progresso médio e feedbacks
    y = np.array([data[2] for data in alunos_data.values()])  # Notas atuais

    model = LinearRegression()
    model.fit(X, y)

    previsoes = model.predict(X)  # Previsão de desempenho futuro com base no progresso e feedbacks
    return previsoes