from sqlalchemy import func
from app import db


def get_team_score(team_id: int) -> int:
    from app.models.submission import Solve, Submission

    # Sum points from correct solves
    solve_total = db.session.query(
        func.coalesce(func.sum(Solve.points), 0)
    ).filter(Solve.team_id == team_id).scalar() or 0

    # Penalty: wrong submissions beyond MAX_ATTEMPTS
    from flask import current_app
    max_attempts = current_app.config.get('MAX_ATTEMPTS', 10)
    penalty_pts  = current_app.config.get('PENALTY_POINTS', 10)

    # Get challenges where team exceeded attempts
    challenge_attempt_counts = db.session.query(
        Submission.challenge_id,
        func.count(Submission.id).label('cnt')
    ).filter(
        Submission.team_id == team_id,
        Submission.is_correct == False
    ).group_by(Submission.challenge_id).all()

    total_penalty = 0
    for row in challenge_attempt_counts:
        if row.cnt > max_attempts:
            excess = row.cnt - max_attempts
            total_penalty += excess * penalty_pts

    return max(0, solve_total - total_penalty)


def get_scoreboard(limit: int = 50):
    from app.models.team import Team
    from app.models.submission import Solve
    from sqlalchemy import desc

    results = db.session.query(
        Team.id,
        Team.name,
        func.coalesce(func.sum(Solve.points), 0).label('score'),
        func.min(Solve.solved_at).label('last_solve')
    ).outerjoin(Solve, Team.id == Solve.team_id)\
     .filter(Team.is_banned == False)\
     .group_by(Team.id, Team.name)\
     .order_by(desc('score'), 'last_solve')\
     .limit(limit)\
     .all()

    board = []
    for rank, row in enumerate(results, 1):
        board.append({
            'rank': rank,
            'team_id': row.id,
            'team_name': row.name,
            'score': row.score,
        })
    return board
