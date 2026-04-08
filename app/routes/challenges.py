from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models.challenge import Challenge, Hint
from app.models.submission import Submission, Solve
from app.models.event import EventState
from app.services.flag_service import validate_submission, format_flag, generate_dynamic_flag
from app.services.security_service import check_submission
from app.services.hint_service import check_and_release_hints
from app.utils.decorators import verified_required
from app.utils.helpers import get_client_ip

challenges_bp = Blueprint('challenges', __name__, url_prefix='/challenges')


def _get_solved_categories(team):
    """Get set of categories the team has solved at least one challenge in."""
    if not team:
        return set()
    solved_ids = {s.challenge_id for s in Solve.query.filter_by(team_id=team.id).all()}
    solved_cats = set()
    for cid in solved_ids:
        ch = Challenge.query.get(cid)
        if ch:
            solved_cats.add(ch.category)
    return solved_cats


def _all_categories_solved(team):
    """Check if team has solved at least 1 challenge from every non-boss category (ignoring pwn)."""
    all_cats = set(
        ch.category for ch in Challenge.query.filter_by(is_hidden=False, is_boss=False).all()
        if ch.category != 'pwn'
    )
    solved_cats = _get_solved_categories(team)
    return all_cats.issubset(solved_cats)


@challenges_bp.route('/')
@login_required
@verified_required
def list():
    check_and_release_hints()

    state = EventState.get()

    # Feature 1 — show waiting page if event not started
    if not state or not state.is_started:
        return render_template('challenges/waiting.html', state=state)

    challenges = Challenge.query.filter_by(is_hidden=False).order_by(
        Challenge.category, Challenge.points
    ).all()

    solved_ids = set()
    team = current_user.team
    if team:
        solved_ids = {s.challenge_id for s in Solve.query.filter_by(team_id=team.id).all()}

    # Feature 2 — check boss unlock
    boss_unlocked = _all_categories_solved(team)

    # Group by category
    categories = {}
    for ch in challenges:
        # Hide boss challenges if not unlocked
        if ch.is_boss and not boss_unlocked:
            continue
        cat = ch.category
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(ch)

    return render_template('challenges/list.html',
                           categories=categories,
                           solved_ids=solved_ids,
                           boss_unlocked=boss_unlocked)


@challenges_bp.route('/<slug>', methods=['GET', 'POST'])
@login_required
@verified_required
def detail(slug):
    challenge = Challenge.query.filter_by(slug=slug, is_hidden=False).first_or_404()
    team = current_user.team

    state = EventState.get()

    # Feature 1 — block if event not started
    if not state or not state.is_started:
        flash('The event has not started yet.', 'warning')
        return redirect(url_for('challenges.list'))

    # Feature 3 — block restricted teams
    if team and team.is_restricted:
        return render_template('challenges/restricted.html')

    # Feature 2 — block boss challenge if not all categories solved
    if challenge.is_boss and not _all_categories_solved(team):
        flash('Complete at least one challenge from every category to unlock this challenge.', 'warning')
        return redirect(url_for('challenges.list'))

    event_active = state and state.is_started and not state.is_ended

    already_solved = False
    attempt_count  = 0
    can_submit     = False
    flag_prefix    = state.flag_prefix if state else current_app.config['FLAG_PREFIX']

    if team:
        already_solved = Solve.query.filter_by(
            team_id=team.id, challenge_id=challenge.id
        ).first() is not None

        attempt_count = Submission.query.filter_by(
            team_id=team.id, challenge_id=challenge.id
        ).count()

        max_attempts = current_app.config['MAX_ATTEMPTS']
        can_submit = event_active and not already_solved and not team.is_paused and not team.is_banned and not team.is_restricted

    hints = Hint.query.filter_by(challenge_id=challenge.id, is_visible=True).all()
    first_blood = challenge.first_blood

    dynamic_flag_display = None
    if challenge.is_dynamic and team:
        inner = generate_dynamic_flag(team.id, challenge.id)
        dynamic_flag_display = format_flag(inner)

    result = None

    if request.method == 'POST':
        if not team:
            flash('You must be in a team to submit flags.', 'error')
            return redirect(url_for('team.dashboard'))

        if not can_submit:
            flash('Submission not allowed.', 'error')
            return redirect(url_for('challenges.detail', slug=slug))

        submitted_flag = request.form.get('flag', '').strip()
        ip = get_client_ip(request)

        last_sub = Submission.query.filter_by(
            team_id=team.id
        ).order_by(Submission.submitted_at.desc()).first()

        if last_sub:
            delta = (datetime.utcnow() - last_sub.submitted_at).total_seconds()
            if delta < 1.0:
                flash('Too fast! Wait 1 second between submissions.', 'warning')
                return redirect(url_for('challenges.detail', slug=slug))

        is_correct = validate_submission(submitted_flag, challenge, team.id)

        sub = Submission(
            team_id=team.id,
            user_id=current_user.id,
            challenge_id=challenge.id,
            submitted_flag=submitted_flag,
            is_correct=is_correct,
            ip_address=ip,
        )
        db.session.add(sub)

        if is_correct:
            current_pts = challenge.current_points()
            is_first_blood = challenge.solves.count() == 0
            if is_first_blood:
                current_pts = int(current_pts * 1.1)

            solve = Solve(
                team_id=team.id,
                challenge_id=challenge.id,
                user_id=current_user.id,
                points=current_pts,
            )
            db.session.add(solve)
            db.session.commit()

            check_submission(team.id, challenge.id, ip, current_user.id)

            new_score = team.score
            result = {
                'correct':        True,
                'challenge_name': challenge.title,
                'points':         current_pts,
                'new_score':      new_score,
                'is_boss':        challenge.is_boss,
                'is_first_blood': is_first_blood,
            }
        else:
            db.session.commit()
            check_submission(team.id, challenge.id, ip, current_user.id)
            attempts_left = max(0, current_app.config['MAX_ATTEMPTS'] - (attempt_count + 1))
            result = {
                'correct': False,
                'attempts_left': attempts_left,
            }

        attempt_count += 1

    return render_template('challenges/detail.html',
                           challenge=challenge,
                           already_solved=already_solved,
                           attempt_count=attempt_count,
                           can_submit=can_submit,
                           hints=hints,
                           first_blood=first_blood,
                           flag_prefix=flag_prefix,
                           dynamic_flag_display=dynamic_flag_display,
                           result=result,
                           max_attempts=current_app.config['MAX_ATTEMPTS'])