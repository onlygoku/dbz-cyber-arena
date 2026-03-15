from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.team import Team, TeamMember
from app.utils.decorators import verified_required

team_bp = Blueprint('team', __name__, url_prefix='/team')


@team_bp.route('/dashboard')
@login_required
@verified_required
def dashboard():
    team = current_user.team
    if not team:
        return render_template('team/dashboard.html', team=None)

    from app.models.challenge import Challenge
    from app.models.submission import Solve

    all_challenges = Challenge.query.filter_by(is_hidden=False).all()
    solved_ids = {s.challenge_id for s in Solve.query.filter_by(team_id=team.id).all()}

    categories = {}
    for ch in all_challenges:
        cat = ch.category
        if cat not in categories:
            categories[cat] = {'total': 0, 'solved': 0}
        categories[cat]['total'] += 1
        if ch.id in solved_ids:
            categories[cat]['solved'] += 1

    total = len(all_challenges)
    solved = len(solved_ids)

    return render_template('team/dashboard.html',
                           team=team,
                           categories=categories,
                           total=total,
                           solved=solved,
                           solved_ids=solved_ids)


@team_bp.route('/create', methods=['GET', 'POST'])
@login_required
@verified_required
def create():
    if current_user.team:
        flash('You are already in a team.', 'warning')
        return redirect(url_for('team.dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Team name is required.', 'error')
            return render_template('team/create.html')

        if len(name) < 2 or len(name) > 64:
            flash('Team name must be 2-64 characters.', 'error')
            return render_template('team/create.html')

        if Team.query.filter_by(name=name).first():
            flash('Team name already taken.', 'error')
            return render_template('team/create.html')

        team = Team(name=name)
        db.session.add(team)
        db.session.flush()

        member = TeamMember(team_id=team.id, user_id=current_user.id, is_captain=True)
        db.session.add(member)
        db.session.commit()

        flash(f'Team "{name}" created! Share your invite code: {team.invite_code}', 'success')
        return redirect(url_for('team.dashboard'))

    return render_template('team/create.html')


@team_bp.route('/join', methods=['GET', 'POST'])
@login_required
@verified_required
def join():
    if current_user.team:
        flash('You are already in a team.', 'warning')
        return redirect(url_for('team.dashboard'))

    if request.method == 'POST':
        code = request.form.get('invite_code', '').strip()
        team = Team.query.filter_by(invite_code=code).first()

        if not team:
            flash('Invalid invite code.', 'error')
            return render_template('team/join.html')

        max_size = current_app.config.get('MAX_TEAM_SIZE', 3)
        if team.member_count >= max_size:
            flash(f'Team is full (max {max_size} members).', 'error')
            return render_template('team/join.html')

        if team.is_banned:
            flash('This team is banned.', 'error')
            return render_template('team/join.html')

        existing = TeamMember.query.filter_by(
            team_id=team.id, user_id=current_user.id
        ).first()
        if existing:
            if existing.is_active:
                flash('You are already in this team.', 'warning')
            else:
                existing.is_active = True
                db.session.commit()
                flash(f'Rejoined team "{team.name}"!', 'success')
            return redirect(url_for('team.dashboard'))

        member = TeamMember(team_id=team.id, user_id=current_user.id, is_captain=False)
        db.session.add(member)
        db.session.commit()

        flash(f'Joined team "{team.name}"!', 'success')
        return redirect(url_for('team.dashboard'))

    return render_template('team/join.html')


@team_bp.route('/leave', methods=['POST'])
@login_required
def leave():
    team = current_user.team
    if not team:
        return redirect(url_for('team.dashboard'))

    member = TeamMember.query.filter_by(
        team_id=team.id, user_id=current_user.id, is_active=True
    ).first()

    if member and member.is_captain and team.member_count > 1:
        flash('Transfer captaincy before leaving.', 'error')
        return redirect(url_for('team.dashboard'))

    if member:
        member.is_active = False
        db.session.commit()
        flash('You left the team.', 'info')

    return redirect(url_for('team.dashboard'))


@team_bp.route('/remove/<int:user_id>', methods=['POST'])
@login_required
def remove_member(user_id):
    team = current_user.team
    if not team or not current_user.is_team_captain:
        flash('Not authorised.', 'error')
        return redirect(url_for('team.dashboard'))

    if user_id == current_user.id:
        flash('Cannot remove yourself.', 'error')
        return redirect(url_for('team.dashboard'))

    member = TeamMember.query.filter_by(
        team_id=team.id, user_id=user_id, is_active=True
    ).first()

    if member:
        member.is_active = False
        db.session.commit()
        flash('Member removed.', 'success')

    return redirect(url_for('team.dashboard'))


@team_bp.route('/regenerate-invite', methods=['POST'])
@login_required
def regenerate_invite():
    team = current_user.team
    if not team or not current_user.is_team_captain:
        flash('Not authorised.', 'error')
        return redirect(url_for('team.dashboard'))

    new_code = team.regenerate_invite()
    db.session.commit()
    flash(f'New invite code: {new_code}', 'success')
    return redirect(url_for('team.dashboard'))
