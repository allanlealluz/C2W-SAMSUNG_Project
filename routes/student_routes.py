from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from models import get_db, find_user_by_id, get_aulas, inscrever_aluno_curso

student_bp = Blueprint('student', __name__)

@student_bp.route('/dashboard_aluno')
def dashboard_aluno():
    user_id = session.get("user")
    if not user_id:
        return redirect(url_for('auth.login'))

    user_info = find_user_by_id(user_id)

    if not user_info:  # Verificar se o usuário existe
        return redirect(url_for('auth.login'))

    db = get_db()
    try:
        # Aulas de Programação (sem limite de 1)
        cursos_programacao = db.execute('''
            SELECT a.* FROM aulas a
            LEFT JOIN progresso_aulas pa ON a.id = pa.aula_id AND pa.user_id = ?
            WHERE a.topico = 'Programação' AND (pa.concluida IS NULL OR pa.concluida = 0)
        ''', (user_id,)).fetchall()

        # Aulas de Robótica (sem limite de 1)
        cursos_robotica = db.execute('''
            SELECT a.* FROM aulas a
            LEFT JOIN progresso_aulas pa ON a.id = pa.aula_id AND pa.user_id = ?
            WHERE a.topico = 'Robótica' AND (pa.concluida IS NULL OR pa.concluida = 0)
        ''', (user_id,)).fetchall()
        return render_template('dashboard_aluno.html', user=user_info, cursos_programacao=cursos_programacao, cursos_robotica=cursos_robotica)

    except Exception as e:
        print(e)
        return render_template('dashboard_aluno.html', user=user_info)


@student_bp.route('/ver_aula/<int:aula_id>', methods=["GET", "POST"])
def ver_aula(aula_id):
    user_id = session.get("user")
    if not user_id:
        return redirect(url_for('auth.login'))

    db = get_db()
    aula = db.execute('SELECT * FROM aulas WHERE id = ?', (aula_id,)).fetchone()
    perguntas = db.execute('SELECT id, texto FROM perguntas WHERE aula_id = ?', (aula_id,)).fetchall()

    if not aula:
        flash("Aula não encontrada.", "error")
        return redirect(url_for('student.dashboard_aluno'))

    if request.method == "POST":
        respostas = request.form.to_dict()
        
        try:
            # Salvar as respostas
            for pergunta_id, resposta in respostas.items():
                if resposta.strip():
                    exists = db.execute(
                        'SELECT 1 FROM respostas WHERE user_id = ? AND pergunta_id = ? AND aula_id = ?',
                        (user_id, pergunta_id, aula_id)
                    ).fetchone()
                    if not exists:
                        db.execute(
                            'INSERT INTO respostas (user_id, pergunta_id, resposta, aula_id) VALUES (?, ?, ?, ?)',
                            (user_id, pergunta_id, resposta, aula_id)
                        )

            db.execute(
                '''
                INSERT INTO progresso_atividades (user_id, section_id, aula_id, completou)
                VALUES (?, ?, ?, 1)
                ON CONFLICT(user_id, section_id, aula_id) DO UPDATE SET completou=1
                ''',
                (user_id, 2, aula_id)
            )
            
            db.commit()
            flash("Respostas enviadas com sucesso! Progresso atualizado.", "success")

        except Exception as e:
            db.rollback()
            flash(f"Erro ao enviar respostas: {str(e)}", "error")

    return render_template('ver_aula.html', aula=aula, perguntas=perguntas)
@student_bp.route('/inscrever_curso/<int:curso_id>', methods=["POST"])
def inscrever_curso(curso_id):
    if 'user' not in session or session['tipo'] != 'aluno':
        return redirect(url_for('auth.login'))

    aluno_id = session['user']
    resultado = inscrever_aluno_curso(aluno_id, curso_id)

    if resultado == "sucesso":
        flash("Inscrição realizada com sucesso!", "success")
    elif resultado == "inscrito":
        flash("Você já está inscrito neste curso.", "info")
    else:
        flash("Erro ao tentar inscrever-se no curso.", "error")

    return redirect(url_for('student.cursos_disponiveis'))

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

@student_bp.route('/responder_atividade/<int:aula_id>', methods=["POST"])
def responder_atividade(aula_id):
    user_id = session.get("user")
    if not user_id:
        return jsonify({'error': 'Usuário não autenticado.'}), 403

    data = request.json.get('respostas', [])
    
    if not data:
        return jsonify({'error': 'Nenhuma resposta fornecida.'}), 400

    db = get_db()

    try:
        for item in data:
            pergunta_id = item.get('pergunta_id')
            resposta = item.get('resposta', '').strip()

            if resposta:
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
