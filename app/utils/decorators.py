from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


def verified_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_verified:
            flash('Please verify your email first.', 'warning')
            return redirect(url_for('auth.unverified'))
        return f(*args, **kwargs)
    return decorated


def event_active_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        from app.models.event import EventState
        state = EventState.get()
        if state and state.is_ended:
            flash('The CTF event has ended.', 'info')
            return redirect(url_for('scoreboard.index'))
        if state and not state.is_started:
            flash('The CTF has not started yet.', 'info')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated
