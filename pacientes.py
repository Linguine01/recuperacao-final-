import sqlite3

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from busca import buscar_pacientes
from db import get_db

bp = Blueprint('pacientes', __name__, url_prefix='/pacientes')


def listar_pacientes():
    return get_db().execute(
        'SELECT id, nome FROM pacientes ORDER BY nome COLLATE NOCASE, id'
    ).fetchall()


@bp.get('/')
def lista():
    termo = request.args.get('q', '').strip()[:100]
    pacientes = buscar_pacientes(listar_pacientes(), termo)
    return render_template('pacientes.html', pacientes=pacientes, termo=termo)


@bp.route('/novo', methods=['GET', 'POST'])
@bp.route('/<int:id>/editar', methods=['GET', 'POST'])
def formulario(id=None):
    db = get_db()
    paciente = {'nome': ''}
    if id is not None:
        paciente = db.execute('SELECT nome FROM pacientes WHERE id = ?', (id,)).fetchone()
        if paciente is None:
            abort(404)

    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        if not 2 <= len(nome) <= 100:
            flash('Informe um nome com 2 a 100 caracteres.', 'erro')
            return render_template('paciente_form.html', paciente={'nome': nome}, id=id), 400

        with db:
            if id is None:
                db.execute('INSERT INTO pacientes (nome) VALUES (?)', (nome,))
            else:
                alteracao = db.execute('UPDATE pacientes SET nome = ? WHERE id = ?', (nome, id))
                if not alteracao.rowcount:
                    abort(404)
        flash('Paciente salvo.', 'sucesso')
        return redirect(url_for('pacientes.lista'), code=303)

    return render_template('paciente_form.html', paciente=paciente, id=id)


@bp.post('/<int:id>/excluir')
def excluir(id):
    db = get_db()
    try:
        with db:
            exclusao = db.execute('DELETE FROM pacientes WHERE id = ?', (id,))
            if not exclusao.rowcount:
                abort(404)
    except sqlite3.IntegrityError:
        flash('Exclua as consultas vinculadas antes de excluir este paciente.', 'erro')
    else:
        flash('Paciente excluído.', 'sucesso')
    return redirect(url_for('pacientes.lista'), code=303)
