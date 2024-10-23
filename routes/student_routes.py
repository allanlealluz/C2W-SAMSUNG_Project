from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from models import get_db, find_user_by_id, get_aulas

student_bp = Blueprint('student', __name__)

@student_bp.route('/dashboard_aluno')
def dashboard_aluno():
    user_id = session.get("user")
    if not user_id:
        return redirect(url_for('auth.login'))

    userData = find_user_by_id(user_id)
    aula = get_aulas(user_id)

    if not aula:
        flash("Nenhuma aula disponível no momento.", "info")

    return render_template("dashboard_aluno.html", user=userData, aula=aula)

@student_bp.route('/ver_aula/<int:aula_id>', methods=["GET", "POST"])
def ver_aula(aula_id):
    user_id = session.get("user")
    if not user_id:
        return redirect(url_for('auth.login'))

    db = get_db()
    aula = db.execute('SELECT * FROM aulas WHERE id = ?', (aula_id,)).fetchone()
    perguntas = db.execute('SELECT id, texto FROM perguntas WHERE aula_id = ?', (aula_id,)).fetchall()
    if request.method == "POST":
        respostas = request.form.to_dict()
        print(respostas) 

    if not aula:
        flash("Aula não encontrada.", "error")
        return redirect(url_for('student.dashboard_aluno'))

    if request.method == "POST":
        respostas = request.form.to_dict()

        for pergunta_id, resposta in respostas.items():
            if resposta.strip():  # Ignora respostas vazias
                # Verifica se a resposta já existe
                exists = db.execute(
                    'SELECT 1 FROM respostas WHERE user_id = ? AND pergunta_id = ? AND aula_id = ?',
                    (user_id, pergunta_id, aula_id)
                ).fetchone()
                if not exists:
                    db.execute(
                        'INSERT INTO respostas (user_id, pergunta_id, resposta, aula_id) VALUES (?, ?, ?, ?)',
                        (user_id, pergunta_id, resposta, aula_id)
                    )
                else:
                    flash(f"Resposta já enviada para a pergunta {pergunta_id}.", "info")

        db.commit()
        flash("Respostas enviadas com sucesso!", "success")

    return render_template('ver_aula.html', aula=aula, perguntas=perguntas)

@student_bp.route('/concluir_aula/<int:aula_id>', methods=["POST"])
def concluir_aula(aula_id):
    user_id = session.get("user")
    if not user_id:
        return redirect(url_for('auth.login'))

    db = get_db()
    
    progresso = db.execute(
        'SELECT * FROM progresso_aulas WHERE user_id = ? AND aula_id = ?', 
        (user_id, aula_id)
    ).fetchone()

    if not progresso:
        db.execute('INSERT INTO progresso_aulas (user_id, aula_id, concluida) VALUES (?, ?, ?)', 
                   (user_id, aula_id, 1))
        db.commit()
        flash("Aula concluída com sucesso!", "success")
    else:
        flash("Aula já foi concluída anteriormente.", "info")
    
    return redirect(url_for('student.dashboard_aluno'))

@student_bp.route('/responder_aula/<int:aula_id>', methods=["POST"])
def responder_atividade(aula_id):
    user_id = session.get("user")
    if not user_id:
        return redirect(url_for('auth.login'))

    respostas = request.json.get('respostas', {})

    if not respostas:
        return jsonify({'error': 'Nenhuma resposta fornecida.'}), 400

    db = get_db()

    try:
        for pergunta_id, resposta in respostas.items():
            if resposta.strip():
                # Verifica se a resposta já existe
                exists = db.execute(
                    'SELECT 1 FROM respostas WHERE user_id = ? AND pergunta_id = ? AND aula_id = ?',
                    (user_id, pergunta_id, aula_id)
                ).fetchone()
                if not exists:
                    db.execute(
                        'INSERT INTO respostas (user_id, aula_id, pergunta_id, resposta) VALUES (?, ?, ?, ?)',
                        (user_id, aula_id, pergunta_id, resposta)
                    )
                else:
                    return jsonify({'error': f'Resposta já enviada para a pergunta {pergunta_id}.'}), 400

        db.commit()
        return jsonify({'message': 'Respostas enviadas com sucesso!'}), 200

    except Exception as e:
        db.rollback()
        return jsonify({'error': 'Erro ao enviar respostas: ' + str(e)}), 500

@student_bp.route('/update_progress', methods=['POST'])
def update_progress():
    user_id = session.get("user")
    if not user_id:
        return jsonify({'error': 'Usuário não autenticado'}), 403

    data = request.get_json()
    section_id = data.get('section')
    aula_id = data.get('aula_id')

    if not section_id or not aula_id:
        return jsonify({'error': 'Dados insuficientes para processar o progresso'}), 400

    db = get_db()
    try:
        exists = db.execute(
            'SELECT 1 FROM progresso_atividades WHERE user_id = ? AND aula_id = ? AND section_id = ?',
            (user_id, aula_id, section_id)
        ).fetchone()

        if not exists:
            db.execute(
                'INSERT INTO progresso_atividades (user_id, aula_id, section_id, completou) VALUES (?, ?, ?, ?)',
                (user_id, aula_id, section_id, 1)
            )
            db.commit()

        total_sections = db.execute(
            'SELECT COUNT(*) FROM perguntas WHERE aula_id = ?',
            (aula_id,)
        ).fetchone()[0]

        completed_sections = db.execute(
            'SELECT COUNT(*) FROM progresso_atividades WHERE user_id = ? AND aula_id = ? AND completou = 1',
            (user_id, aula_id)
        ).fetchone()[0]

        if completed_sections == total_sections:
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
        db.rollback()
        return jsonify({'error': 'Erro ao atualizar progresso: ' + str(e)}), 500
