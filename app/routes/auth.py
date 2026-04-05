from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
import threading
from app import db
from app.models.user import User
from app.services.email_service import send_verification_email
from app.services.email_validator import is_valid_email_domain

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

        is_valid, email_error = is_valid_email_domain(email)
        if not is_valid:
            flash(email_error, 'error')
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

        user_id  = user.id
        suppress = current_app.config.get('MAIL_SUPPRESS_SEND', False)

        current_app.logger.info(f'Token: {user.verify_token}')
        current_app.logger.info(f'Mail server: {current_app.config.get("MAIL_SERVER")}')
        current_app.logger.info(f'Mail user: {current_app.config.get("MAIL_USERNAME")}')
        current_app.logger.info(f'Suppress: {suppress}')

        if not suppress:
            base_url = current_app.config.get('BASE_URL')
            if base_url:
                 verify_url = f"{base_url.rstrip('/')}/verify/{user.verify_token}"
            else:
                 verify_url = url_for('auth.verify_email', token=user.verify_token, _external=True)

            app_instance = current_app._get_current_object()

            def send_async_email(app, uid, vurl):
                with app.app_context():
                    from app.models.user import User as U
                    from app.services.email_service import send_verification_email as _send
                    try:
                        u = U.query.get(uid)
                        if u:
                            _send(u, verify_url=vurl)
                    except Exception as e:
                        app.logger.error(f'Async email error: {e}')

            thread = threading.Thread(
                target=send_async_email,
                args=(app_instance, user_id, verify_url),
                daemon=False  # keep thread alive even after request ends
            )
            thread.start()

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


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('challenges.list'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        user  = User.query.filter_by(email=email).first()

        flash('If that email is registered, you will receive a password reset link shortly.', 'info')

        if user and user.is_verified:
            from app.services.email_service import send_password_reset_email
            user.generate_reset_token()
            db.session.commit()
            send_password_reset_email(user)

        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('challenges.list'))

    user = User.query.filter_by(reset_token=token).first()

    if not user or not user.is_reset_token_valid():
        flash('This password reset link is invalid or has expired.', 'error')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        new_password     = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if len(new_password) < 8:
            flash('Password must be at least 8 characters.', 'error')
            return render_template('auth/reset_password.html', token=token)

        if new_password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('auth/reset_password.html', token=token)

        user.set_password(new_password)
        user.reset_token        = None
        user.reset_token_expiry = None
        db.session.commit()

        flash('Password reset successfully! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', token=token)