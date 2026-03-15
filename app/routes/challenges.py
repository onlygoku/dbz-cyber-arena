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


@challenges_bp.route('/')
@login_required
@verified_required
def list():
    check_and_release_hints()

    challenges = Challenge.query.filter_by(is_hidden=False).order_by(
        Challenge.category, Challenge.points
    ).all()

    solved_ids = set()
    team = current_user.team
    if team:
        solved_ids = {s.challenge_id for s in Solve.query.filter_by(team_id=team.id).all()}

    # Group by category
    categories = {}
    for ch in challenges:
        cat = ch.category
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(ch)

    return render_template('challenges/list.html',
                           categories=categories,
                           solved_ids=solved_ids)


@challenges_bp.route('/<slug>', methods=['GET', 'POST'])
@login_required
@verified_required
def detail(slug):
    challenge = Challenge.query.filter_by(slug=slug, is_hidden=False).first_or_404()
    team = current_user.team

    state = EventState.get()
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
        can_submit = event_active and not already_solved and not team.is_paused and not team.is_banned

    hints = Hint.query.filter_by(challenge_id=challenge.id, is_visible=True).all()
    first_blood = challenge.first_blood

    # Dynamic flag for display (if applicable)
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

        # Check rate limit (1 per second per team) - lightweight check via last submission time
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
            solve = Solve(
                team_id=team.id,
                challenge_id=challenge.id,
                user_id=current_user.id,
                points=challenge.points,
            )
            db.session.add(solve)
            db.session.commit()

            # Run security checks
            check_submission(team.id, challenge.id, ip, current_user.id)

            new_score = team.score
            result = {
                'correct': True,
                'challenge_name': challenge.title,
                'points': challenge.points,
                'new_score': new_score,
                'is_boss': challenge.is_boss,
                'is_first_blood': challenge.solves.count() == 1,
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
