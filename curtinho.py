import random, string

from flask import Flask, request, redirect, render_template

import sqlite3

import validators

app = Flask(__name__)



def gerar_string_aleatoria():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))




conexao = sqlite3.connect('curtinho.db')
cursor = conexao.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        curto TEXT UNIQUE,
        url TEXT
    )
''')

conexao.commit()
cursor.close()

def link_curto(url):
    conexao = sqlite3.connect('curtinho.db')
    cursor = conexao.cursor()
    string = gerar_string_aleatoria()
    while cursor.execute('SELECT 1 FROM links WHERE curto = ?', (string,)).fetchone() is not None:
        string = gerar_string_aleatoria()
    
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url


    cursor.execute('INSERT INTO links (curto, url) VALUES (?, ?)', (string, url))
    conexao.commit()
    cursor.close()
    conexao.close()
    print(f"Link curto gerado: {string} para URL: {url}")
    return string




def acessar_link_curto(string):
    conexao = sqlite3.connect('curtinho.db')
    cursor = conexao.cursor()
    cursor.execute('SELECT url FROM links WHERE curto = ?', (string,))
    result = cursor.fetchone()
    cursor.close()
    conexao.close()
    return result[0] if result else "Link não encontrado"


def normalizar_url(url):
    if not url.startswith(("http://", "https://")):
        return "https://" + url
    return url


def buscar_link_existente_por_url(url_normalized):
    conexao = sqlite3.connect('curtinho.db')
    cursor = conexao.cursor()
    cursor.execute('SELECT curto FROM links WHERE url = ?', (url_normalized,))
    result = cursor.fetchone()
    cursor.close()
    conexao.close()
    return result[0] if result else None



@app.route('/', methods=['GET'])
def get():
    return render_template('index.html')





@app.route('/', methods=['POST'])
def post():
    url_raw = request.form.get('url', '').strip()
    link_curto_personalizado = request.form.get('link_curto_personalizado', '').strip()

    if not url_raw:
        return render_template('400.html'), 400

    url_normalized = normalizar_url(url_raw)

    # Valida a URL já normalizada
    if not validators.url(url_normalized):
        return render_template('400.html'), 400

    link_existente = buscar_link_existente_por_url(url_normalized)
    if link_existente:
        link_encurtado = request.host_url.rstrip('/') + '/' + link_existente
        return render_template('resultado.html', link_encurtado=link_encurtado), 200

    # Se o usuário pediu slug personalizado, valide e insira usando a URL normalizada
    if link_curto_personalizado:
        if not link_curto_personalizado.isalnum():
            return render_template('400.html'), 400
        conexao = sqlite3.connect('curtinho.db')
        cursor = conexao.cursor()
        if cursor.execute('SELECT 1 FROM links WHERE curto = ?', (link_curto_personalizado,)).fetchone() is not None:
            cursor.close()
            conexao.close()
            return render_template('400.html'), 400
        cursor.execute('INSERT INTO links (curto, url) VALUES (?, ?)', (link_curto_personalizado, url_normalized))
        conexao.commit()
        cursor.close()
        conexao.close()
        link_encurtado = request.host_url.rstrip('/') + '/' + link_curto_personalizado
        return render_template('resultado.html', link_encurtado=link_encurtado), 201

    # Caso padrão: gera slug aleatório e use a URL normalizada
    link_curto_string = link_curto(url_normalized)
    link_encurtado = request.host_url.rstrip('/') + '/' + link_curto_string
    return render_template('resultado.html', link_encurtado=link_encurtado), 201




@app.route('/<string:link_curto_string>', methods=['GET'])
def acessar_link(link_curto_string):
    url = acessar_link_curto(link_curto_string)
    if url == "Link não encontrado":
        return render_template('404.html'), 404
    else:
        return redirect(url), 302


if __name__ == "__main__":    app.run(debug=True)
