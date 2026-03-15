from datetime import datetime, timedelta
from app import db


def check_and_release_hints():
    """Call this periodically to auto-release hints based on time or solve count."""
    from app.models.challenge import Hint, Challenge

    hints = Hint.query.filter_by(is_visible=False).all()
    now = datetime.utcnow()

    for hint in hints:
        challenge = hint.challenge
        if challenge.is_hidden:
            continue

        released = False

        # Time-based release
        if hint.auto_release_minutes and challenge.released_at:
            unlock_at = challenge.released_at + timedelta(minutes=hint.auto_release_minutes)
            if now >= unlock_at:
                released = True

        # Solve-count-based release
        if hint.auto_release_solves is not None:
            solve_count = challenge.solves.count()
            if solve_count >= hint.auto_release_solves:
                released = True

        if released:
            hint.is_visible = True

    db.session.commit()
