import matplotlib.pyplot as plt
import io
import base64

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
