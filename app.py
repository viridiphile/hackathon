import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
import requests
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
import re
import random
from flask_cors import CORS
import openai

from helpers import apology, login_required

# Configure application
app = Flask(__name__)
CORS(app)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///hackathon.db")

# Create tables
db.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        iin TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
''')

db.execute('''
    CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        type TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
''')

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():

    return render_template("index.html")


@app.route("/account")
@login_required
def account():
    """Show portfolio of stocks"""
    user_id = session["user_id"]
    
    return render_template("account.html")


@app.route("/oracle", methods=["GET", "POST"])
@login_required
def oracle():
    """Get stock quote."""
    # 2
    # Allows to look up a stock's current price
    # input of stock's symbol required, html name="symbol"
    # submit input via "post" to "/quote"
    # 2 new templates quote.html, quoted.html

    """Odds are you’ll want to create two new templates (e.g., quote.html and quoted.html). When a user visits /quote via GET, render one of those templates, inside of which should be an HTML form that submits to /quote via POST. In response to a POST, quote can render that second template, embedding within it one or more values from lookup."""

    return render_template("oracle.html")# from backend to frontend


@app.route("/loan-form", methods=["GET", "POST"])
@login_required
def loan():
    """Buy shares of stock"""
    # 3
    if request.method == "POST":

        user_id = session["user_id"]

        flash("The purchase has been made!")

        return redirect("/account")

    else:
        return render_template("loan_form.html")


@app.route("/autoloan-form", methods=["GET", "POST"])
@login_required
def autoloan():
    """Sell shares of stock"""
    if request.method == "POST":
      
        return redirect("/account")

    else:
        user_id = session["user_id"]
        return render_template("autoloan_form.html")


@app.route("/mortgage-form")
@login_required
def mortgage():
    """Show history of transactions"""
    user_id = session["user_id"]

    return render_template("mortgage_form.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    if request.method == "POST":
        # Ensure email was submitted
        if not request.form.get("email"):
            return apology("must provide email", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for the email
        rows = db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email"))

        # Ensure email exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return apology("invalid email and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/account")

    else:
        return render_template("login.html")
    

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Get the form inputs
        full_name = request.form.get("full_name")
        iin = request.form.get("iin")
        email = request.form.get("email")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Check for blank inputs
        if not full_name:
            return apology("Full name required")
        
        if not iin:
            return apology("IIN required")

        if not email:
            return apology("Email required")

        if not password:
            return apology("Password required")

        if not confirmation:
            return apology("Confirmation required")

        if password != confirmation:
            return apology("Passwords do not match")

        # Password validation (same logic as before)
        check = True
        while check:
            if len(password) < 8:
                break
            elif not re.search("[a-z]", password):
                break
            elif not re.search("[0-9]", password):
                break
            else:
                check = False

        if check:
            return apology("Password does not meet requirements")

        # Hash the password
        hash = generate_password_hash(password)

        # Insert user into the new 'users' table of 'hackathon' database
        try:
            new_user = db.execute("INSERT INTO users (full_name, iin, email, password) VALUES (?, ?, ?, ?)",
                                  full_name, iin, email, hash)
        except:
            return apology("Email is taken")

        # Start session
        session["user_id"] = new_user
        return redirect("/account")
    
    else:
        return render_template("register.html")


# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY") 

@app.route("/chat", methods=["POST"])
def chat():
    try:
        request_data = request.get_json()
        user_message = request_data.get("message", "")  # Извлекаем сообщение из тела запроса

        response = requests.post('https://chatbot.tim-space.kz/chat', json={
            # "message": "Привет, меня зовут Галина! Мой ИИН: 12345797697, у меня чистая кредитная история. Могу ли я взять кредит?"
            "message": user_message
        })

        # Логируем текст ответа для отладки
        print(response.text)

        if response.status_code == 200:
            # Извлекаем ответ от AI из вложенного словаря
            bot_response = response.json().get("data", {}).get("responseFromAi", "Нет ответа от AI")
        else:
            bot_response = f"Ошибка: {response.status_code}"

    except Exception as e:
        bot_response = f"Произошла ошибка: {str(e)}"
        
    return jsonify({"reply": bot_response})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
