from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.services.email_service import send_verification_email

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/')
def index():
    return render_template('index.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('challenges.list'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email    = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm  = request.form.get('confirm_password', '')

        if not username or not email or not password:
            flash('All fields are required.', 'error')
            return render_template('auth/register.html')

        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('auth/register.html')

        if len(password) < 8:
            flash('Password must be at least 8 characters.', 'error')
            return render_template('auth/register.html')

        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'error')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('auth/register.html')

        user = User(username=username, email=email)
        user.set_password(password)
        user.generate_verify_token()
        db.session.add(user)
        db.session.commit()

        suppress = current_app.config.get('MAIL_SUPPRESS_SEND', False)
        if not suppress:
            send_verification_email(user)
            flash('Registration successful! Check your email to verify your account.', 'success')
        else:
            # Dev mode: auto-verify
            user.is_verified = True
            db.session.commit()
            flash('Registration successful! (Dev mode: auto-verified)', 'success')

        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('challenges.list'))

    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password   = request.form.get('password', '')
        remember   = request.form.get('remember') == 'on'

        user = User.query.filter(
            (User.email == identifier.lower()) | (User.username == identifier)
        ).first()

        if not user or not user.check_password(password):
            flash('Invalid credentials.', 'error')
            return render_template('auth/login.html')

        if user.is_banned:
            flash('Your account has been banned.', 'error')
            return render_template('auth/login.html')

        if not user.is_verified:
            flash('Please verify your email before logging in.', 'warning')
            return render_template('auth/login.html')

        from datetime import datetime
        user.last_login = datetime.utcnow()
        db.session.commit()

        login_user(user, remember=remember)
        next_page = request.args.get('next')
        return redirect(next_page or url_for('challenges.list'))

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.index'))


@auth_bp.route('/verify/<token>')
def verify_email(token):
    user = User.query.filter_by(verify_token=token).first()
    if not user:
        flash('Invalid or expired verification link.', 'error')
        return redirect(url_for('auth.login'))

    user.is_verified = True
    user.verify_token = None
    db.session.commit()
    flash('Email verified! You can now log in.', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/unverified')
def unverified():
    return render_template('auth/verify.html')
