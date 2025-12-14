from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    current_app,
)
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from flask_mail import Message
import requests

from .models import User
from . import db, mail
from .tokens import generate_reset_token, verify_reset_token

auth = Blueprint("auth", __name__)

# --------------------------------------------------
# Google reCAPTCHA verification (BACKEND ONLY)
# --------------------------------------------------
# def verify_recaptcha(response_token):
#     if not response_token:
#         return False

#     secret_key = current_app.config.get("RECAPTCHA_SECRET_KEY")

#     # 🚨 Fail fast if misconfigured
#     if not secret_key:
#         current_app.logger.error("RECAPTCHA_SECRET_KEY is not set")
#         return False

#     payload = {
#         "secret": secret_key,
#         "response": response_token,
#         "remoteip": request.remote_addr,
#     }

#     try:
#         r = requests.post(
#             "https://www.google.com/recaptcha/api/siteverify",
#             data=payload,
#             timeout=5,
#         )
#         result = r.json()
#         return result.get("success", False)
#     except requests.RequestException:
#         return False
def verify_recaptcha(response_token):
    # 🚧 TEMPORARY BYPASS for development / testing
    if current_app.config.get("FLASK_ENV") != "production":
        return True

    if not response_token:
        return False

    secret_key = current_app.config.get("RECAPTCHA_SECRET_KEY")

    payload = {
        "secret": secret_key,
        "response": response_token,
    }

    try:
        r = requests.post(
            "https://www.google.com/recaptcha/api/siteverify",
            data=payload,
            timeout=5,
        )
        result = r.json()
        return result.get("success", False)
    except requests.RequestException:
        return False


# --------------------------------------------------
# LOGIN
# --------------------------------------------------
@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        # 1️⃣ Verify reCAPTCHA FIRST
        recaptcha_response = request.form.get("g-recaptcha-response")
        if not verify_recaptcha(recaptcha_response):
            flash("reCAPTCHA verification failed. Please try again.", "error")
            return redirect(url_for("auth.login"))

        # 2️⃣ Normal login logic
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            flash("Logged in successfully!", "success")
            return redirect(url_for("views.home"))

        flash("Invalid email or password.", "error")

    return render_template(
        "login.html",
        user=current_user,
        recaptcha_site_key=current_app.config.get("RECAPTCHA_SITE_KEY"),
    )


# --------------------------------------------------
# LOGOUT
# --------------------------------------------------
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


# --------------------------------------------------
# SIGN UP
# --------------------------------------------------
@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        first_name = request.form.get("firstName")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")

        user = User.query.filter_by(email=email).first()

        if user:
            flash("Email already exists.", "error")
        elif len(email) < 4:
            flash("Email must be greater than 3 characters.", "error")
        elif len(first_name) < 2:
            flash("First name must be greater than 1 character.", "error")
        elif password1 != password2:
            flash("Passwords do not match.", "error")
        elif len(password1) < 7:
            flash("Password must be at least 7 characters.", "error")
        else:
            new_user = User(
                email=email,
                first_name=first_name,
                password=generate_password_hash(password1),
                role="user",
            )
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user, remember=True)
            flash("Account created successfully!", "success")
            return redirect(url_for("views.home"))

    return render_template("sign_up.html", user=current_user)


# --------------------------------------------------
# FORGOT PASSWORD
# --------------------------------------------------
@auth.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email")
        user = User.query.filter_by(email=email).first()

        if user:
            token = generate_reset_token(user.email)
            reset_url = url_for("auth.reset_password", token=token, _external=True)

            msg = Message("Password Reset Request", recipients=[user.email])
            msg.body = f"""
To reset your password, click the link below:

{reset_url}

If you did not request this, please ignore this email.
"""
            mail.send(msg)

        flash(
            "If the email exists, a password reset link has been sent.",
            "success",
        )
        return redirect(url_for("auth.login"))

    return render_template("forgot_password.html", user=current_user)


# --------------------------------------------------
# RESET PASSWORD
# --------------------------------------------------
@auth.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    email = verify_reset_token(token)
    if not email:
        flash("Invalid or expired reset link.", "error")
        return redirect(url_for("auth.forgot_password"))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not password or password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("auth.reset_password", token=token))

        user.password = generate_password_hash(password)
        db.session.commit()

        flash("Password updated successfully.", "success")
        return redirect(url_for("auth.login"))

    return render_template("reset_password.html", user=current_user)
