# MedTec 2026

Agenda de um consultório fictício. Permite cadastrar, consultar, editar e excluir
pacientes e consultas. A agenda tem filtros de data e situação. Use nomes
fictícios na demonstração, pois a aplicação acadêmica tem acesso público.

## Como executar

Use Python 3.10 ou superior. No terminal, entre na pasta do projeto e rode:

```bash
python -m venv .venv
```

Ative o ambiente virtual com `.venv\Scripts\Activate.ps1` no PowerShell ou
`source .venv/bin/activate` no Linux e macOS. Em seguida:

```bash
python -m pip install -r requirements.txt
python -m flask --app app run
```

Abra <http://127.0.0.1:5000>. Na primeira execução, o Flask cria o banco em
`instance/medtec.sqlite3`. Defina `MEDTEC_DB` se precisar usar outro caminho.
A agenda começa vazia. Cadastre um paciente fictício e, depois, uma consulta.

## Rotas principais

| Método | Rota | Função |
| --- | --- | --- |
| GET | `/consultas/` | Agenda, com filtros opcionais `data` e `status` |
| GET | `/pacientes/` | Cadastro, com busca opcional `q` |
| GET | `/api/pacientes` | Lista JSON com `id` e `nome` |
| GET | `/health` | Verifica se a aplicação consegue consultar o banco |

Os formulários usam GET para exibição e POST para gravação. A exclusão é POST.
A coluna `consultas.paciente_id` referencia `pacientes.id`. Um paciente pode
ter várias consultas. Para excluir um paciente, exclua suas consultas primeiro.

## Onde encontrar cada UC

| UC | Implementação |
| --- | --- |
| UC30 | `busca.py`, busca linear por trecho do nome, sem distinguir caixa ou acentos |
| UC31 | `templates/` e `static/style.css`, navegação e layout responsivo |
| UC32 | `schema.sql`, `pacientes.py` e `consultas.py`, CRUD e SQL com JOIN, WHERE e ORDER BY |
| UC33 | `app.py` e Blueprints, templates Jinja e API JSON |
| UC34 | Este README, estrutura de arquivos e histórico Git |
| UC35 | `requirements.txt`, `Procfile` e configuração de publicação abaixo |

## Publicação no Render

Use um repositório público no GitHub. Se extraiu o ZIP, a pasta `.git` contém
o histórico local. Envie a branch `main` a um repositório vazio para levar
os commits junto.

```bash
git remote add origin https://github.com/SEU_USUARIO/medtec-2026.git
git push -u origin main
```

No [Render](https://dashboard.render.com/), crie um **Web Service** ligado ao
repositório, selecione o runtime **Python** e configure:

- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn --no-control-socket --bind 0.0.0.0:$PORT app:app`
- Health Check Path: `/health`
- Environment: defina `SECRET_KEY` com um valor aleatório. Você pode gerar um
  com `python -c "import secrets; print(secrets.token_hex(32))"`.

O comando de inicialização é o mesmo do Procfile, sem o prefixo `web:`.
Confira também o material da Geekie para seguir o formato exigido pela escola.

Teste a URL HTTPS gerada no Render e sua rota `/api/pacientes`. No plano
gratuito, o sistema de arquivos é temporário. Cadastros do SQLite podem se
perder quando o serviço reiniciar, suspender por inatividade ou fizer redeploy.
Para persistência no Render, use um serviço com disco persistente e configure
`MEDTEC_DB` para apontar para um arquivo dentro do disco montado.

Referências oficiais: [Flask no Render](https://render.com/docs/deploy-flask) e
[limitações do plano gratuito](https://render.com/docs/free).
