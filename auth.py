from flask import Blueprint, request, render_template, flash, redirect, url_for
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash
from db import db
from models import User

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        col = db.get_collection("users")
        user = col.find_one({"username": username})

        if not user:
            flash("Det finns ingen användare med det namnet.")
            return render_template("auth/login.html")

        if not check_password_hash(user["password"], password):
            flash("Fel lösenord.")
            return render_template("auth/login.html")

        u = User()
        u.set_id(user.get("_id"))
        u.is_authenticated = True
        u.is_admin = user.get("is_admin", False)

        login_user(u)

        flash("Du är inloggad")

        if u.is_admin:
            return redirect(url_for("admin.admin_start"))
        return redirect(url_for("index"))

    return render_template("auth/login.html")


@auth.route("/logout")
def logout():
    logout_user()
    flash("Du har loggats ut.")
    return redirect(url_for('auth.login'))
