import random, string

from flask import Flask, request, redirect, render_template

import sqlite3

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
    return string




def acessar_link_curto(string):
    conexao = sqlite3.connect('curtinho.db')
    cursor = conexao.cursor()
    cursor.execute('SELECT url FROM links WHERE curto = ?', (string,))
    result = cursor.fetchone()
    cursor.close()
    conexao.close()
    return result[0] if result else "Link não encontrado"



@app.route('/', methods=['GET'])
def get():
    return render_template('index.html')
@app.route('/', methods=['POST'])
def post():
    url = request.form['url']
    link_curto_string = link_curto(url)
    link_encurtado = request.host_url.rstrip('/') + '/' + link_curto_string
    return render_template('resultado.html', link_encurtado=link_encurtado)

@app.route('/<string:link_curto_string>', methods=['GET'])
def acessar_link(link_curto_string):
    url = acessar_link_curto(link_curto_string)
    if url == "Link não encontrado":
        return url
    else:
        return redirect(url)


if __name__ == "__main__":    app.run(debug=True)
