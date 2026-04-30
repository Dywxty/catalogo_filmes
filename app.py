import os
import uuid
from flask import Flask, request, render_template, redirect, url_for
from psycopg2.extras import RealDictCursor
from database import get_connection

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/')
def home():
    return redirect(url_for("listar_filmes"))


@app.route('/filmes')
def listar_filmes():
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM filmes")
        filmes = cursor.fetchall()
        conn.close()
        return render_template("index.html", filmes=filmes)
    except Exception as ex:
        print("ERRO LISTAR:", ex)
        return "erro ao listar filmes"


@app.route("/novo", methods=["GET", "POST"])
def novo_filme():
    if request.method == "POST":
        try:
            titulo = request.form.get("titulo")
            genero = request.form.get("genero")
            ano = request.form.get("ano")

            imagem = request.files.get("imagem")

            if not imagem or imagem.filename == "":
                return "nenhuma imagem foi enviada"

            extensao = imagem.filename.rsplit('.', 1)[-1].lower()
            if extensao not in ["jpg", "jpeg", "png"]:
                return "formato inválido"

            nome_arquivo = f"{uuid.uuid4()}.{extensao}"
            caminho_arquivo = os.path.join(UPLOAD_FOLDER, nome_arquivo)

            imagem.save(caminho_arquivo)

            caminho_db = f"uploads/{nome_arquivo}"

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO filmes (titulo, genero, ano, url_capa) VALUES (%s, %s, %s, %s)",
                (titulo, genero, ano, caminho_db)
            )

            conn.commit()
            conn.close()

            return redirect(url_for("listar_filmes"))

        except Exception as ex:
            print("ERRO SALVAR:", ex)
            return "erro ao salvar filme"

    return render_template("novo_filme.html")


@app.route("/deletar/<int:id>", methods=["POST"])
def deletar_filme(id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM filmes WHERE id = %s", (id,))
        conn.commit()
        conn.close()
        return redirect(url_for("listar_filmes"))
    except Exception as ex:
        print("ERRO DELETAR:", ex)
        return "erro ao deletar"


if __name__ == "__main__":
    app.run(debug=True)