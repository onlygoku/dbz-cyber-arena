from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.user import User

profile_bp = Blueprint("profile", __name__, url_prefix="/profile")

@profile_bp.route("/", methods=["GET", "POST"])
@login_required
def edit():
    if request.method == "POST":
        action = request.form.get("action")

        if action == "update_info":
            username = request.form.get("username", "").strip()
            email    = request.form.get("email", "").strip().lower()

            if not username or not email:
                flash("Username and email are required.", "error")
                return render_template("profile/edit.html")

            if len(username) < 2 or len(username) > 64:
                flash("Username must be 2-64 characters.", "error")
                return render_template("profile/edit.html")

            existing = User.query.filter_by(username=username).first()
            if existing and existing.id != current_user.id:
                flash("Username already taken.", "error")
                return render_template("profile/edit.html")

            existing_email = User.query.filter_by(email=email).first()
            if existing_email and existing_email.id != current_user.id:
                flash("Email already registered.", "error")
                return render_template("profile/edit.html")

            current_user.username = username
            current_user.email    = email
            db.session.commit()
            flash("Profile updated successfully.", "success")

        elif action == "change_password":
            current_password = request.form.get("current_password", "")
            new_password     = request.form.get("new_password", "")
            confirm_password = request.form.get("confirm_password", "")

            if not current_user.check_password(current_password):
                flash("Current password is incorrect.", "error")
                return render_template("profile/edit.html")

            if len(new_password) < 8:
                flash("New password must be at least 8 characters.", "error")
                return render_template("profile/edit.html")

            if new_password != confirm_password:
                flash("New passwords do not match.", "error")
                return render_template("profile/edit.html")

            current_user.set_password(new_password)
            db.session.commit()
            flash("Password changed successfully.", "success")

        return redirect(url_for("profile.edit"))

    return render_template("profile/edit.html")
