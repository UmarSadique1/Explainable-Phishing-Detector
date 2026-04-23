from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, logout_user, current_user

from app import db
from app.models import User

auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    error = None

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not full_name or not email or not password or not confirm_password:
            error = "All fields are required."
        elif password != confirm_password:
            error = "Passwords do not match."
        elif User.query.filter_by(email=email).first():
            error = "An account with this email already exists."
        else:
            user = User(full_name=full_name, email=email, role="user")
            user.set_password(password)

            db.session.add(user)
            db.session.commit()

            return redirect(url_for("auth.login"))

    return render_template("register.html", error=error)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    error = None

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("main.index"))

        error = "Invalid email or password."

    return render_template("login.html", error=error)


@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))