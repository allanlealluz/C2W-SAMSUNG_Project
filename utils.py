import matplotlib.pyplot as plt
import io
import base64
import os
import numpy as np
from sklearn.cluster import KMeans
import spacy

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
        X = np.array([data for data in alunos_data.values()])
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
