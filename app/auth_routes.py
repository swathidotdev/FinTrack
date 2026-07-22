from flask import Blueprint, render_template, request, redirect, url_for, session

from app.auth import register_user, login_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        
        success, message = register_user(username, email, password)
        
        if success:
            return redirect(url_for("auth.login"))
        else:
            return render_template("signup.html", error=message)
    
    return render_template("signup.html", error=None)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        success, message, user_id = login_user(username, password)
        
        if success:
            session["user_id"] = user_id
            session["username"] = username
            return redirect(url_for("main.index"))
        else:
            return render_template("login.html", error=message)
    
    return render_template("login.html", error=None)


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
