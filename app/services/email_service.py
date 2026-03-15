from flask import current_app, url_for, render_template_string
from flask_mail import Message
from app import mail


def send_verification_email(user):
    token = user.verify_token
    verify_url = url_for('auth.verify_email', token=token, _external=True)

    body = f"""
    <h2>Welcome to {current_app.config['CTF_NAME']}!</h2>
    <p>Click below to verify your email address:</p>
    <a href="{verify_url}" style="background:#f97316;color:#fff;padding:12px 24px;text-decoration:none;border-radius:6px;">
        Verify Email
    </a>
    <p>Or paste this link: {verify_url}</p>
    <p>If you did not register, ignore this email.</p>
    """

    msg = Message(
        subject=f'[{current_app.config["CTF_NAME"]}] Verify your email',
        recipients=[user.email],
        html=body,
    )
    try:
        mail.send(msg)
    except Exception as e:
        current_app.logger.error(f'Failed to send email to {user.email}: {e}')
