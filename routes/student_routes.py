from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from models import get_db, find_user_by_id, get_aulas

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

    if request.method == "POST":
        # Verificar se há progresso e, se não, marcar aula como concluída
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

    return render_template('ver_aula.html', aula=aula)


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

    resposta = request.form.get('resposta')
    if not resposta:
        flash("Por favor, insira uma resposta.", "danger")
        return redirect(url_for('student.ver_aula', aula_id=aula_id))

    db = get_db()
    
    # Salvar a resposta no banco de dados
    db.execute(
        'INSERT INTO respostas_aulas (user_id, aula_id, resposta) VALUES (?, ?, ?)', 
        (user_id, aula_id, resposta)
    )
    db.commit()

    flash("Resposta enviada com sucesso!", "success")
    return redirect(url_for('student.ver_aula', aula_id=aula_id))


# Rota para atualizar o progresso do aluno em uma seção da aula
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
        # Verifica se o progresso da seção já foi registrado
        exists = db.execute(
            'SELECT 1 FROM progresso_atividades WHERE user_id = ? AND aula_id = ? AND section_id = ?',
            (user_id, aula_id, section_id)
        ).fetchone()

        if not exists:
            # Insere o progresso da seção no banco de dados
            db.execute(
                'INSERT INTO progresso_atividades (user_id, aula_id, section_id, completou) VALUES (?, ?, ?, ?)',
                (user_id, aula_id, section_id, 1)
            )
            db.commit()

        # Verifica se todas as seções dessa aula foram concluídas
        total_sections = db.execute(
            'SELECT COUNT(*) FROM sections WHERE aula_id = ?',
            (aula_id,)
        ).fetchone()[0]

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
        db.rollback()  # Em caso de erro, reverte a operação
        return jsonify({'error': str(e)}), 500
