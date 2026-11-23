import sqlite3
from datetime import date, time

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from db import get_db
from pacientes import listar_pacientes

bp = Blueprint('consultas', __name__, url_prefix='/consultas')
STATUS = {'agendada': 'Agendada', 'realizada': 'Realizada', 'cancelada': 'Cancelada'}


def data_valida(valor):
    try:
        return date.fromisoformat(valor).isoformat() == valor
    except ValueError:
        return False


def horario_valido(valor):
    try:
        return time.fromisoformat(valor).isoformat(timespec='minutes') == valor and len(valor) == 5
    except ValueError:
        return False


@bp.get('/')
def lista():
    data = request.args.get('data', '').strip()
    filtro = request.args.get('status', '').strip()
    if (data and not data_valida(data)) or (filtro and filtro not in STATUS):
        flash('Confira a data e a situação escolhidas.', 'erro')
        return redirect(url_for('consultas.lista'))

    consultas = get_db().execute(
        """
        SELECT c.id, c.data, c.horario, c.status, p.nome AS paciente
        FROM consultas AS c
        JOIN pacientes AS p ON p.id = c.paciente_id
        WHERE (? = '' OR c.data = ?) AND (? = '' OR c.status = ?)
        ORDER BY c.data, c.horario, c.id
        """,
        (data, data, filtro, filtro),
    ).fetchall()
    return render_template('consultas.html', consultas=consultas, data=data, filtro=filtro, status=STATUS)


@bp.route('/nova', methods=['GET', 'POST'])
@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
def formulario(id=None):
    db = get_db()
    consulta = {'paciente_id': '', 'data': '', 'horario': '', 'status': 'agendada'}
    if id is not None:
        consulta = db.execute('SELECT * FROM consultas WHERE id = ?', (id,)).fetchone()
        if consulta is None:
            abort(404)

    pacientes = listar_pacientes()
    if request.method == 'POST':
        consulta = {campo: request.form.get(campo, '').strip() for campo in (
            'paciente_id', 'data', 'horario', 'status'
        )}
        erros = []
        pacientes_validos = {str(paciente['id']) for paciente in pacientes}
        if consulta['paciente_id'] not in pacientes_validos:
            erros.append('Selecione um paciente cadastrado.')
        if not data_valida(consulta['data']) or not horario_valido(consulta['horario']):
            erros.append('Informe uma data e um horário válidos.')
        if consulta['status'] not in STATUS:
            erros.append('Selecione uma situação válida.')

        if not erros:
            dados = (
                int(consulta['paciente_id']), consulta['data'], consulta['horario'], consulta['status']
            )
            try:
                with db:
                    if id is None:
                        db.execute(
                            'INSERT INTO consultas (paciente_id, data, horario, status) VALUES (?, ?, ?, ?)',
                            dados,
                        )
                    else:
                        alteracao = db.execute(
                            'UPDATE consultas SET paciente_id = ?, data = ?, horario = ?, status = ? WHERE id = ?',
                            (*dados, id),
                        )
                        if not alteracao.rowcount:
                            abort(404)
            except sqlite3.IntegrityError:
                erros.append('O paciente selecionado deixou de estar disponível.')
            else:
                flash('Consulta salva.', 'sucesso')
                return redirect(url_for('consultas.lista'), code=303)

        for erro in erros:
            flash(erro, 'erro')
        return render_template(
            'consulta_form.html', consulta=consulta, id=id, pacientes=pacientes, status=STATUS
        ), 400

    return render_template(
        'consulta_form.html', consulta=consulta, id=id, pacientes=pacientes, status=STATUS
    )


@bp.post('/<int:id>/excluir')
def excluir(id):
    db = get_db()
    with db:
        exclusao = db.execute('DELETE FROM consultas WHERE id = ?', (id,))
        if not exclusao.rowcount:
            abort(404)
    flash('Consulta excluída.', 'sucesso')
    return redirect(url_for('consultas.lista'), code=303)
