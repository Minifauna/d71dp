from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from functools import wraps
import os
from dotenv import load_dotenv, dotenv_values
import pandas as pd
import re
from projects import translation

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_KEY')
Bootstrap5(app)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/tropes')
def horror_tropes():
    data = pd.read_json('static/assets/HorrorTropes.json', orient='index')
    df_tropes = data.sample(5)
    trope_names = [' '.join(filter(None, re.split(r'(?=[A-Z])', name))) for name in df_tropes.index]
    trope_urls = [value[0] for value in df_tropes.values]
    trope_zip = zip(trope_names, trope_urls)
    trope_dict = dict(trope_zip)
    num_tropes = len(trope_dict)
    return render_template("tropes.html", tropes=trope_dict, length=num_tropes)

@app.route('/all-tropes')
def all_tropes():
    df_tropes = pd.read_json('static/assets/HorrorTropes.json', orient='index')
    trope_names = [' '.join(filter(None, re.split(r'(?=[A-Z])', name))) for name in df_tropes.index]
    trope_urls = [value[0] for value in df_tropes.values]
    trope_zip = zip(trope_names, trope_urls)
    temp_dict = dict(trope_zip)
    sorted_dict = sorted(temp_dict.items())
    trope_dict = dict(sorted_dict)
    num_tropes = len(trope_dict)
    return render_template("tropes.html", tropes=trope_dict, length=num_tropes)

@app.route('/devtest')
def devtest():
    return render_template('devtest.html')

@app.route('/todo')
def todo_list():
    todo_list = ['undo/redo site styling',
    'complete morse code translator with focus on deployment here',
    're-introduce Flask-SQLAlchemy for todo list',
    'expand custom pallete with rgba']
    return render_template('todo.html', todo=todo_list)

if __name__ == "__main__":
    app.run(debug=False)
