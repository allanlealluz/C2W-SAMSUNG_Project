from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from models import get_db, find_user_by_id, get_aulas
import json

student_bp = Blueprint('student', __name__)

# Rota para o dashboard do aluno
@student_bp.route('/dashboard_aluno')
def dashboard_aluno():
    user_id = session.get("user")
    if not user_id:
        return redirect(url_for('auth.login'))

    userData = find_user_by_id(user_id)
    aula = get_aulas(user_id)  # Pega a próxima aula disponível

    return render_template("dashboard_aluno.html", user=userData, aula=aula)


# Rota para visualizar a aula
@student_bp.route('/ver_aula/<int:aula_id>', methods=["GET", "POST"])
def ver_aula(aula_id):
    user_id = session.get("user")
    if not user_id:
        return redirect(url_for('auth.login'))

    db = get_db()
    aula = db.execute('SELECT * FROM aulas WHERE id = ?', (aula_id,)).fetchone()

    # Buscar as perguntas com seus respectivos IDs
    perguntas = db.execute('SELECT id, texto FROM perguntas WHERE aula_id = ?', (aula_id,)).fetchall()
    
    if request.method == "POST":
        # Coleta as respostas enviadas no formulário
        respostas = request.form.to_dict()  # Pega todas as respostas do formulário

        for pergunta_id, resposta in respostas.items():
            if resposta.strip():  # Ignora respostas vazias
                db.execute(
                    'INSERT INTO respostas (user_id, pergunta_id, resposta, aula_id) VALUES (?, ?, ?, ?)',
                    (user_id, pergunta_id, resposta, aula_id)
                )
        db.commit()
        flash("Respostas enviadas com sucesso!", "success")
    return render_template('ver_aula.html', aula=aula, perguntas=perguntas)





# Rota para concluir a aula
@student_bp.route('/concluir_aula/<int:aula_id>', methods=["POST"])
def concluir_aula(aula_id):
    user_id = session.get("user")
    if not user_id:
        return redirect(url_for('auth.login'))

    db = get_db()
    
    # Verifica se o progresso já foi registrado
    progresso = db.execute(
        'SELECT * FROM progresso_aulas WHERE user_id = ? AND aula_id = ?', 
        (user_id, aula_id)
    ).fetchone()

    if not progresso:
        db.execute('INSERT INTO progresso_aulas (user_id, aula_id, concluida) VALUES (?, ?, 1)', 
                   (user_id, aula_id))
        db.commit()
        flash("Aula concluída com sucesso!", "success")
    else:
        flash("Aula já foi concluída anteriormente.", "info")
    
    return redirect(url_for('student.dashboard_aluno'))


# Rota para responder a uma atividade da aula
@student_bp.route('/responder_aula/<int:aula_id>', methods=["POST"])
def responder_atividade(aula_id):
    user_id = session.get("user")
    if not user_id:
        return redirect(url_for('auth.login'))

    # Captura o JSON contendo as respostas
    respostas = request.json.get('respostas', {})  # Certifique-se de que isso é um dicionário

    if not respostas:
        return jsonify({'error': 'Nenhuma resposta fornecida.'}), 400

    db = get_db()

    # Itera sobre as respostas e as insere no banco de dados
    for pergunta_id, resposta in respostas.items():
        if resposta.strip():  # Ignora respostas vazias
            db.execute(
                'INSERT INTO respostas (user_id, aula_id, section, response) VALUES (?, ?, ?, ?)',
                (user_id, aula_id, pergunta_id, resposta)
            )

    db.commit()

    return jsonify({'message': 'Respostas enviadas com sucesso!'}), 200




# Rota para atualizar o progresso do aluno em uma seção da aula
@student_bp.route('/update_progress', methods=['POST', 'GET'])
def update_progress():
    user_id = session.get("user")

    # Verifica se o usuário está autenticado
    if not user_id:
        return jsonify({'error': 'Usuário não autenticado'}), 403

    data = request.get_json()
    section_id = data.get('section')
    aula_id = data.get('aula_id')

    # Verifica se os dados necessários foram fornecidos
    if not section_id or not aula_id:
        return jsonify({'error': 'Dados insuficientes para processar o progresso'}), 400

    db = get_db()
    try:
        # Verifica se o progresso da seção já foi registrado
        exists = db.execute(
            'SELECT 1 FROM progresso_atividades WHERE user_id = ? AND aula_id = ? AND section_id = ?',
            (user_id, aula_id, section_id)
        ).fetchone()

        if not exists:
            print(f"Inserindo progresso para user_id: {user_id}, aula_id: {aula_id}, section_id: {section_id}")
            db.execute(
                'INSERT INTO progresso_atividades (user_id, aula_id, section_id, completou) VALUES (?, ?, ?, ?)',
                (user_id, aula_id, section_id, 1)
            )
            db.commit()

        # Verifica o número total de seções dessa aula na tabela 'respostas'
        total_sections = db.execute(
            'SELECT COUNT(DISTINCT section) FROM respostas WHERE aula_id = ?',
            (aula_id,)
        ).fetchone()[0]

        # Verifica quantas seções foram completadas pelo usuário nessa aula
        completed_sections = db.execute(
            'SELECT COUNT(*) FROM progresso_atividades WHERE user_id = ? AND aula_id = ? AND completou = 1',
            (user_id, aula_id)
        ).fetchone()[0]

        if completed_sections == total_sections:
            # Marca a aula como concluída se todas as seções foram completadas
            aula_exists = db.execute(
                'SELECT 1 FROM progresso_aulas WHERE user_id = ? AND aula_id = ?',
                (user_id, aula_id)
            ).fetchone()

            if not aula_exists:
                db.execute(
                    'INSERT INTO progresso_aulas (user_id, aula_id, concluida) VALUES (?, ?, ?)',
                    (user_id, aula_id, 1)
                )
            else:
                db.execute(
                    'UPDATE progresso_aulas SET concluida = 1 WHERE user_id = ? AND aula_id = ?',
                    (user_id, aula_id)
                )
            db.commit()

        return jsonify({'message': 'Progresso atualizado com sucesso!'}), 200

    except Exception as e:
        db.rollback()  # Reverte a transação em caso de erro
        print(f"Erro detectado: {e}")  # Log do erro para depuração
        return jsonify({'error': 'Erro ao atualizar progresso: ' + str(e)}), 500

