import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import generate_password_hash, check_password_hash
import db
import config

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat"
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu"
    
    session["username"] = username
    return redirect("/user_page")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    
    sql = "SELECT id, password_hash FROM users WHERE username = ?"
    password_hash = db.query(sql, [username])
    user_id, password_hash = sql[0]

    if check_password_hash(password_hash, password):
        session["username"] = username
        session["user_id"] = user_id
        return redirect("/user_page")
    else:
        return "VIRHE: väärä tunnus tai salasana"
    
@app.route("/user_page")
def user_page():
    sql = """SELECT id, title, user_id  FROM budgets"""
    budgets = db.query(sql)
    return render_template("user_page.html", budgets=budgets)

@app.route("/new_expense", methods=["POST"])
def new_expense():
    content = request.form["content"]
    budget_id = request.form["budget_id"]
    user_id = request.form["user_id"]

    sql = """INSERT INTO expenses (content, sent_at, user_id, budget_id) VALUES
             (?, datetime('now'), ?, ?)"""
    db.execute(sql, [content, user_id, budget_id])

@app.route("/new_budget", methods=["POST"])
def new_budget():
    title = request.form["title"]
    user_id = request.form["user_id"]

    sql = "INSERT INTO budgets (title, user_id) VALUES (?, ?)"
    db.execute(sql, [title, user_id])
    return redirect("/user_page")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")