import resend
from flask import current_app


def send_verification_email(user, verify_url=None):
    resend.api_key = current_app.config.get('RESEND_API_KEY')

    if verify_url is None:
        from flask import url_for
        verify_url = url_for('auth.verify_email', token=user.verify_token, _external=True)

    body = f"""
    <!DOCTYPE html>
    <html>
    <body style="background:#0a0a0f;color:#e2e8f0;font-family:Arial,sans-serif;padding:40px;">
      <div style="max-width:500px;margin:0 auto;background:#0f0f1a;border:1px solid #1e1e3a;border-radius:8px;padding:40px;">
        <div style="text-align:center;margin-bottom:24px;">
          <div style="font-size:48px;">🐉</div>
          <h1 style="color:#f97316;font-size:20px;letter-spacing:4px;text-transform:uppercase;margin:8px 0;">
            Dragon Ball Z Cyber Arena
          </h1>
        </div>
        <h2 style="color:#fbbf24;font-size:16px;">Verify Your Email</h2>
        <p style="color:#9ca3af;margin:16px 0;">
          Welcome to the arena! Click the button below to verify your email address and activate your account.
        </p>
        <div style="text-align:center;margin:32px 0;">
          <a href="{verify_url}"
             style="background:linear-gradient(135deg,#f97316,#dc2626);color:#fff;
                    padding:14px 32px;text-decoration:none;border-radius:4px;
                    font-weight:bold;letter-spacing:2px;text-transform:uppercase;
                    font-size:13px;display:inline-block;">
            Verify Email →
          </a>
        </div>
        <p style="color:#6b7280;font-size:12px;margin-top:24px;">
          Or paste this link in your browser:<br/>
          <a href="{verify_url}" style="color:#f97316;word-break:break-all;">{verify_url}</a>
        </p>
        <p style="color:#4b5563;font-size:11px;margin-top:24px;border-top:1px solid #1e1e3a;padding-top:16px;">
          If you did not register for Dragon Ball Z Cyber Arena, please ignore this email.
        </p>
      </div>
    </body>
    </html>
    """

    try:
        resend.Emails.send({
            "from": current_app.config.get('MAIL_DEFAULT_SENDER', 'onboarding@resend.dev'),
            "to": user.email,
            "subject": "[DBZ Cyber Arena] Verify your email",
            "html": body,
        })
        current_app.logger.info(f'Verification email sent to {user.email}')
        return True
    except Exception as e:
        current_app.logger.error(f'Failed to send email to {user.email}: {e}')
        return False


def send_password_reset_email(user):
    resend.api_key = current_app.config.get('RESEND_API_KEY')

    from flask import url_for
    reset_url = url_for('auth.reset_password', token=user.reset_token, _external=True)

    body = f"""
    <!DOCTYPE html>
    <html>
    <body style="background:#0a0a0f;color:#e2e8f0;font-family:Arial,sans-serif;padding:40px;">
      <div style="max-width:500px;margin:0 auto;background:#0f0f1a;border:1px solid #1e1e3a;border-radius:8px;padding:40px;">
        <div style="text-align:center;margin-bottom:24px;">
          <div style="font-size:48px;">🔑</div>
          <h1 style="color:#f97316;font-size:20px;letter-spacing:4px;text-transform:uppercase;margin:8px 0;">
            Password Reset
          </h1>
        </div>
        <p style="color:#9ca3af;margin:16px 0;">
          You requested a password reset. Click below to set a new password.
          This link expires in <strong style="color:#fbbf24;">1 hour</strong>.
        </p>
        <div style="text-align:center;margin:32px 0;">
          <a href="{reset_url}"
             style="background:linear-gradient(135deg,#8b5cf6,#6d28d9);color:#fff;
                    padding:14px 32px;text-decoration:none;border-radius:4px;
                    font-weight:bold;letter-spacing:2px;text-transform:uppercase;
                    font-size:13px;display:inline-block;">
            Reset Password →
          </a>
        </div>
        <p style="color:#6b7280;font-size:12px;margin-top:24px;">
          Or paste this link:<br/>
          <a href="{reset_url}" style="color:#8b5cf6;word-break:break-all;">{reset_url}</a>
        </p>
        <p style="color:#4b5563;font-size:11px;margin-top:24px;border-top:1px solid #1e1e3a;padding-top:16px;">
          If you did not request a reset, ignore this email.
        </p>
      </div>
    </body>
    </html>
    """

    try:
        resend.Emails.send({
            "from": current_app.config.get('MAIL_DEFAULT_SENDER', 'onboarding@resend.dev'),
            "to": user.email,
            "subject": "[DBZ Cyber Arena] Password Reset Request",
            "html": body,
        })
        current_app.logger.info(f'Password reset email sent to {user.email}')
        return True
    except Exception as e:
        current_app.logger.error(f'Failed to send reset email to {user.email}: {e}')
        return False