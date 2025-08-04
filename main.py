from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.exc import SQLAlchemyError
from flask_bootstrap import Bootstrap5
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from typing import List
import os
from dotenv import load_dotenv, dotenv_values
import pandas as pd
import re
from flaskforms import Login, AddTask, Register, RemoveTask
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

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True)
    email: Mapped[str] = mapped_column(String(250), unique=True)
    password_hash: Mapped[str] = mapped_column(String(250))
    todo = relationship("Todo", back_populates="user")

class Todo(db.Model):
    __tablename__ = "todo"
    id: Mapped[int] = mapped_column(primary_key=True)
    list_user: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user = relationship("User", back_populates="todo")
    task: Mapped[str] = mapped_column(String(400))


with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = Register()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password_hash = generate_password_hash(form.password.data)
        new_user = User(username=username, email=email, password_hash=password_hash)
        try:
            db.session.add(new_user)
            flash('Thank you!')
            db.session.commit()
            return redirect(url_for('index'))
        except SQLAlchemyError:
            return render_template("login.html", form=form)
    return render_template("login.html", form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = Login()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.username == username))
        user = result.scalar()
        if check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            return render_template("login.html", form=form)
    return render_template("login.html", form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

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

@app.route('/todo', methods=['GET', 'POST'])
@login_required
def todo_list():
    result = db.session.execute(db.select(Todo).where(Todo.user == current_user))
    todo_list = result.scalars()
    form = AddTask()
    task_done = RemoveTask()
    if form.submit.data and form.validate_on_submit():
        new_task_list_user = current_user.get_id()
        new_task_task = form.task.data
        new_task = Todo(list_user=new_task_list_user, task=new_task_task)
        db.session.add(new_task)
        db.session.commit()
        return redirect(url_for('todo_list'))
    if task_done.remove.data and task_done.validate_on_submit():
        task_id = task_done.task_id.data
        result = db.session.execute(db.select(Todo).where(Todo.id == task_id))
        finished_task = result.scalar()
        db.session.delete(finished_task)
        db.session.commit()
        return redirect(url_for('todo_list'))
    return render_template('todo.html', todo=todo_list, form=form, remove=task_done)

if __name__ == "__main__":
    app.run(debug=True)
