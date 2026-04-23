import os
import uuid
from flask import Flask, render_template, request, redirect
import psycopg2

app = Flask(__name__)

# configuração e limitação no ‘upload’
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# cria a pasta se não existir
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

conn = psycopg2.connect(
    host="ep-rapid-truth-amjduagq-pooler.c-5.us-east-1.aws.neon.tech",
    database="neondb",
    user="neondb_owner",
    password="npg_Qnv4i7XHwbUd",
    sslmode="require"
)

cursor = conn.cursor()

# PGHOST='ep-rapid-truth-amjduagq-pooler.c-5.us-east-1.aws.neon.tech'
# PGDATABASE='neondb'
# PGUSER='neondb_owner'
# PGPASSWORD='npg_Qnv4i7XHwbUd'
# PGSSLMODE='require'
# PGCHANNELBINDING='require'

cursor = conn.cursor()

# funções
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def gerar_nome_unico(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    return f"{uuid.uuid4().hex}.{ext}"

# rotas de navegação
@app.route('/')
def index():
    cursor.execute("SELECT * FROM filmes ORDER BY id DESC")
    filmes = cursor.fetchall()
    return render_template('index.html', filmes=filmes)

@app.route('/add_filme', methods=['GET', 'POST'])
def add_filme():

    # 👉 ABRIR A PÁGINA
    if request.method == 'GET':
        return render_template('templates/add_filmes.html')

    # 👉 ENVIAR FORMULÁRIO
    titulo = request.form.get('titulo')
    genero = request.form.get('genero')
    ano = request.form.get('ano')

    if 'capa' not in request.files:
        return "Nenhuma imagem enviada"

    file = request.files['capa']

    if file.filename == '':
        return "Arquivo sem nome"

    if file and allowed_file(file.filename):
        nome_arquivo = gerar_nome_unico(file.filename)
        caminho = os.path.join(app.config['UPLOAD_FOLDER'], nome_arquivo)

        file.save(caminho)

        caminho_db = f"static/uploads/{nome_arquivo}"

        cursor.execute(
            "INSERT INTO filmes (titulo, genero, ano, imagem) VALUES (%s, %s, %s, %s)",
            (titulo, genero, ano, caminho_db)
        )
        conn.commit()

        return redirect('/')

    return "Formato inválido (apenas jpg, jpeg, png)"

@app.route('/listar_filmes')
def listar_filmes():
    return redirect('/')

@app.route('/delete/<int:id>')
def delete_filme(id):
    # pega o caminho da imagem
    cursor.execute("SELECT imagem FROM filmes WHERE id = %s", (id,))
    filme = cursor.fetchone()

    if filme:
        caminho = filme[0]

        # remove arquivo do servidor
        if os.path.exists(caminho):
            os.remove(caminho)

        # remove do banco
        cursor.execute("DELETE FROM filmes WHERE id = %s", (id,))
        conn.commit()


    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)