from flask import Blueprint, jsonify, current_app
from flask_login import current_user
from app.models.event import EventState
from app.models.submission import Solve
from app.services.score_service import get_scoreboard
from app.services.cache_service import get as cache_get, set as cache_set

api_bp = Blueprint('api', __name__)


@api_bp.route('/scoreboard')
def scoreboard():
    state = EventState.get()
    is_frozen = state and state.is_frozen
    is_admin  = current_user.is_authenticated and current_user.is_admin

    if is_frozen and not is_admin:
        board = cache_get('scoreboard:frozen') or get_scoreboard(100)
        cache_set('scoreboard:frozen', board, ttl=60)
        return jsonify({'board': board, 'frozen': True})

    board = cache_get('scoreboard:live')
    if not board:
        board = get_scoreboard(100)
        ttl = current_app.config.get('SCOREBOARD_CACHE_TTL', 10)
        cache_set('scoreboard:live', board, ttl=ttl)

    return jsonify({'board': board, 'frozen': False})


@api_bp.route('/feed')
def feed():
    cached = cache_get('scoreboard:feed')
    if cached:
        return jsonify({'feed': cached})

    solves = Solve.query.order_by(Solve.solved_at.desc()).limit(20).all()
    data = []
    for s in solves:
        data.append({
            'team_name':      s.team.name if s.team else '?',
            'challenge_name': s.challenge.title if s.challenge else '?',
            'points':         s.points,
            'solved_at':      s.solved_at.strftime('%H:%M:%S'),
        })
    cache_set('scoreboard:feed', data, ttl=5)
    return jsonify({'feed': data})


@api_bp.route('/event-state')
def event_state():
    state = EventState.get()
    if not state:
        return jsonify({'started': False, 'ended': False, 'frozen': False})
    return jsonify({
        'started':      state.is_started,
        'ended':        state.is_ended,
        'frozen':       state.is_frozen,
        'announcement': state.announcement,
        'ctf_name':     state.ctf_name,
        'flag_prefix':  state.flag_prefix,
    })


@api_bp.route('/team/score')
def team_score():
    if not current_user.is_authenticated:
        return jsonify({'error': 'not authenticated'}), 401
    team = current_user.team
    if not team:
        return jsonify({'score': 0, 'solved': 0})
    return jsonify({
        'score':  team.score,
        'solved': team.solves.count(),
    })
