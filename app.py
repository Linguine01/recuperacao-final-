import os
import secrets
from datetime import datetime
from hmac import compare_digest

from flask import Flask, abort, jsonify, redirect, render_template, request, session, url_for

import consultas
import db
import pacientes

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('RENDER') == 'true'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
db.init_app(app)
app.register_blueprint(pacientes.bp)
app.register_blueprint(consultas.bp)


@app.context_processor
def formulario_seguro():
    if 'csrf' not in session:
        session['csrf'] = secrets.token_urlsafe(32)
    return {'csrf_token': session['csrf']}


@app.before_request
def validar_formulario():
    if request.method == 'POST':
        token = session.get('csrf')
        enviado = request.form.get('csrf_token', '').encode('utf-8')
        if token is None or not compare_digest(token.encode('utf-8'), enviado):
            abort(400, description='Atualize a página para reenviar o formulário.')


@app.template_filter('data_br')
def data_br(valor):
    return datetime.strptime(valor, '%Y-%m-%d').strftime('%d/%m/%Y')


@app.get('/')
def inicio():
    return redirect(url_for('consultas.lista'))


@app.get('/api/pacientes')
def api_pacientes():
    return jsonify([dict(paciente) for paciente in pacientes.listar_pacientes()])


@app.get('/health')
def health():
    db.get_db().execute('SELECT 1 FROM pacientes LIMIT 1')
    return {'status': 'ok'}


@app.errorhandler(400)
@app.errorhandler(404)
def erro(error):
    return render_template('erro.html', error=error), error.code


if __name__ == '__main__':
    app.run()
