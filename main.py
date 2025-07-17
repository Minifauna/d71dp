from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_bootstrap import Bootstrap5
from functools import wraps
import os
from dotenv import load_dotenv, dotenv_values
import pandas as pd
import re
from flaskforms import Login
from projects import translation

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
Bootstrap5(app)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = Login()
    if form.validate_on_submit():
        return redirect(url_for('index'))
    return render_template("login.html", form=form)

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
    'todo list - add datetime for "entered" in db model',
    'todo list - "done" list for last seven days to readd',
    'complete morse code translator with focus on deployment here',
    're-introduce Flask-SQLAlchemy for todo list',
    'expand custom pallete with rgba, Smoky Mountain Sunset']
    return render_template('todo.html', todo=todo_list)

if __name__ == "__main__":
    app.run(debug=False)
