from flask import Blueprint, render_template, current_app
from flask_login import current_user
from app.models.event import EventState
from app.models.submission import Solve
from app.models.challenge import Challenge
from app.services.score_service import get_scoreboard
from app.services.cache_service import get as cache_get, set as cache_set

scoreboard_bp = Blueprint('scoreboard', __name__, url_prefix='/scoreboard')


@scoreboard_bp.route('/')
def index():
    state = EventState.get()
    is_frozen = state and state.is_frozen
    is_admin  = current_user.is_authenticated and current_user.is_admin

    # Admins always see live board
    if is_frozen and not is_admin:
        board = _get_frozen_board()
        frozen = True
    else:
        board = _get_live_board()
        frozen = False

    # Live solve feed (last 20 solves)
    feed = _get_solve_feed()

    return render_template('scoreboard/index.html',
                           board=board,
                           frozen=frozen,
                           feed=feed,
                           state=state)


def _get_live_board():
    cached = cache_get('scoreboard:live')
    if cached:
        return cached
    board = get_scoreboard(limit=100)
    ttl = current_app.config.get('SCOREBOARD_CACHE_TTL', 10)
    cache_set('scoreboard:live', board, ttl=ttl)
    return board


def _get_frozen_board():
    cached = cache_get('scoreboard:frozen')
    if cached:
        return cached
    board = get_scoreboard(limit=100)
    cache_set('scoreboard:frozen', board, ttl=60)
    return board


def _get_solve_feed(limit=20):
    cached = cache_get('scoreboard:feed')
    if cached:
        return cached

    from app.models.team import Team
    solves = Solve.query.order_by(Solve.solved_at.desc()).limit(limit).all()
    feed = []
    for s in solves:
        feed.append({
            'team_name': s.team.name if s.team else '?',
            'challenge_name': s.challenge.title if s.challenge else '?',
            'points': s.points,
            'solved_at': s.solved_at.strftime('%H:%M:%S'),
        })
    cache_set('scoreboard:feed', feed, ttl=5)
    return feed
