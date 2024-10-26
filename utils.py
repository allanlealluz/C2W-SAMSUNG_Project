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



def extract_keywords(text):
    doc = nlp(text)
    keywords = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct][:3]
    return keywords

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