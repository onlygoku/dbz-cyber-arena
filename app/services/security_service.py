from datetime import datetime, timedelta
from app import db


def check_submission(team_id: int, challenge_id: int, ip: str, user_id: int):
    """Run security checks after each submission."""
    _check_excessive_submissions(team_id, challenge_id)
    _check_same_ip_teams(ip, team_id)
    _check_fast_solve(team_id, challenge_id)


def _check_excessive_submissions(team_id: int, challenge_id: int):
    from app.models.submission import Submission
    from app.models.security import SecurityEvent

    window = datetime.utcnow() - timedelta(minutes=5)
    count = Submission.query.filter(
        Submission.team_id == team_id,
        Submission.challenge_id == challenge_id,
        Submission.submitted_at >= window,
        Submission.is_correct == False
    ).count()

    if count >= 15:
        _log_event('excessive_submissions', team_id=team_id, challenge_id=challenge_id,
                   details=f'{count} wrong attempts in 5 min', severity='high')


def _check_same_ip_teams(ip: str, current_team_id: int):
    from app.models.submission import Submission
    from app.models.security import SecurityEvent

    window = datetime.utcnow() - timedelta(hours=1)
    rows = db.session.query(Submission.team_id).filter(
        Submission.ip_address == ip,
        Submission.submitted_at >= window,
        Submission.team_id != current_team_id
    ).distinct().all()

    if rows:
        other_ids = [r.team_id for r in rows]
        _log_event('same_ip_teams', team_id=current_team_id,
                   details=f'IP {ip} also used by teams {other_ids}', severity='medium')


def _check_fast_solve(team_id: int, challenge_id: int):
    from app.models.submission import Solve
    from app.models.challenge import Challenge

    solve = Solve.query.filter_by(team_id=team_id, challenge_id=challenge_id).first()
    if not solve:
        return

    challenge = Challenge.query.get(challenge_id)
    if not challenge or not challenge.released_at:
        return

    elapsed = (solve.solved_at - challenge.released_at).total_seconds()
    if elapsed < 30:  # solved in under 30 seconds
        _log_event('fast_solve', team_id=team_id, challenge_id=challenge_id,
                   details=f'Solved in {elapsed:.1f}s', severity='high')


def _log_event(event_type, team_id=None, challenge_id=None, user_id=None,
               details=None, ip=None, severity='medium'):
    from app.models.security import SecurityEvent
    ev = SecurityEvent(
        event_type=event_type,
        team_id=team_id,
        challenge_id=challenge_id,
        user_id=user_id,
        details=details,
        ip_address=ip,
        severity=severity,
    )
    db.session.add(ev)
    db.session.commit()
