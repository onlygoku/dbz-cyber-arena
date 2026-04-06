import os
import json
import tempfile
from datetime import datetime
from flask import (Blueprint, render_template, redirect, url_for, flash,
                   request, current_app, jsonify, send_from_directory)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models.user import User
from app.models.team import Team, TeamMember
from app.models.challenge import Challenge, Hint
from app.models.submission import Submission, Solve
from app.models.event import EventState
from app.models.security import SecurityEvent
from app.services.challenge_import import import_challenge_from_zip
from app.services.cache_service import flush as flush_cache
from app.utils.decorators import admin_required
from app.utils.helpers import slugify

admin_bp = Blueprint('admin', __name__)

ALLOWED_EXTENSIONS = {
    'zip', 'tar', 'gz', 'py', 'c', 'cpp', 'elf', 'exe', 'png', 'jpg',
    'jpeg', 'gif', 'pcap', 'pcapng', 'txt', 'pdf', 'bin', 'sh', 'js',
    'html', 'php', 'rb', 'go', 'rs', 'java', 'class', 'jar', 'sql',
}


def _save_challenge_files(challenge_id: int, files) -> list:
    """Upload files to Cloudinary. Returns updated file list."""
    from app.services.storage_service import upload_file
    saved = []
    for f in files:
        if not f or not f.filename:
            continue
        filename = secure_filename(f.filename)
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        if ext not in ALLOWED_EXTENSIONS and ext != '':
            continue
        result = upload_file(f, challenge_id, filename)
        if result:
            saved.append(result)
    return saved


def _get_existing_files(challenge_id: int) -> list:
    """Load existing file list from challenge.files_json."""
    ch = Challenge.query.get(challenge_id)
    if ch and ch.files_json:
        try:
            return json.loads(ch.files_json)
        except Exception:
            pass
    return []


@admin_bp.before_request
def require_admin():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    if not current_user.is_admin:
        from flask import abort
        abort(403)


# â”€â”€ Dashboard â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@admin_bp.route('/')
def dashboard():
    stats = {
        'users':       User.query.count(),
        'teams':       Team.query.count(),
        'challenges':  Challenge.query.count(),
        'solves':      Solve.query.count(),
        'submissions': Submission.query.count(),
        'flags':       Submission.query.filter_by(is_correct=True).count(),
        'security':    SecurityEvent.query.filter_by(is_reviewed=False).count(),
    }
    state = EventState.get()

    health = []
    for ch in Challenge.query.filter_by(is_hidden=False).all():
        health.append({
            'title':      ch.title,
            'attempts':   ch.attempt_count,
            'solves':     ch.solve_count,
            'solve_rate': ch.solve_rate,
            'warning':    ch.attempt_count > 20 and ch.solve_count == 0,
        })

    return render_template('admin/dashboard.html', stats=stats, state=state, health=health)


# â”€â”€ Event Control â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@admin_bp.route('/event', methods=['POST'])
def event_control():
    state = EventState.get()
    action = request.form.get('action')

    if action == 'start':
        state.is_started = True
        state.is_ended   = False
        state.start_time = datetime.utcnow()
        flash('Event started.', 'success')
    elif action == 'end':
        state.is_ended   = True
        state.is_frozen  = False
        state.end_time   = datetime.utcnow()
        flash('Event ended.', 'success')
    elif action == 'freeze':
        state.is_frozen  = True
        flash('Scoreboard frozen.', 'warning')
    elif action == 'unfreeze':
        state.is_frozen  = False
        flash('Scoreboard unfrozen.', 'info')
    elif action == 'update_prefix':
        prefix = request.form.get('flag_prefix', '').strip().upper()
        if prefix:
            state.flag_prefix = prefix
            flash(f'Flag prefix updated to {prefix}.', 'success')
    
    elif action == 'reset_event':
        from app.models.submission import Submission, Solve
        from app.models.security import SecurityEvent
        # Reset all submissions, solves and security events
        SecurityEvent.query.delete()
        Solve.query.delete()
        Submission.query.delete()
        # Reset event state
        state.is_started = False
        state.is_ended   = False
        state.is_frozen  = False
        state.start_time = None
        state.end_time   = None
        state.announcement = None
        db.session.commit()
        flush_cache()
        flash('Event fully reset. All solves, submissions and alerts cleared.', 'warning')
        return redirect(url_for('admin.dashboard'))
    elif action == 'announce':
        msg = request.form.get('announcement', '').strip()
        state.announcement = msg or None
        flash('Announcement updated.', 'success')
    elif action == 'reset':
        state.is_started = False
        state.is_ended   = False
        state.is_frozen  = False
        state.start_time = None
        state.end_time   = None
        flash('Event reset.', 'warning')

    db.session.commit()
    flush_cache()
    return redirect(url_for('admin.dashboard'))


# â”€â”€ Users â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@admin_bp.route('/users')
def users():
    q = request.args.get('q', '')
    query = User.query
    if q:
        query = query.filter(
            (User.username.ilike(f'%{q}%')) | (User.email.ilike(f'%{q}%'))
        )
    users = query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users, q=q)


@admin_bp.route('/users/<int:user_id>/action', methods=['POST'])
def user_action(user_id):
    user = User.query.get_or_404(user_id)
    action = request.form.get('action')

    if action == 'ban':
        user.is_banned = True
        flash(f'User {user.username} banned.', 'warning')
    elif action == 'unban':
        user.is_banned = False
        flash(f'User {user.username} unbanned.', 'success')
    elif action == 'verify':
        user.is_verified = True
        flash(f'User {user.username} verified.', 'success')
    elif action == 'make_admin':
        user.is_admin = True
        flash(f'User {user.username} promoted to admin.', 'success')
    elif action == 'remove_admin':
        user.is_admin = False
        flash(f'Admin removed from {user.username}.', 'info')
    elif action == 'delete':
        if user.id == current_user.id:
            flash('You cannot delete your own account.', 'error')
            return redirect(url_for('admin.users'))
        TeamMember.query.filter_by(user_id=user.id).delete()
        Submission.query.filter_by(user_id=user.id).delete()
        Solve.query.filter_by(user_id=user.id).delete()
        db.session.delete(user)
        flash(f'User {user.username} deleted.', 'warning')
        db.session.commit()
        return redirect(url_for('admin.users'))

    db.session.commit()
    return redirect(url_for('admin.users'))


# â”€â”€ Teams â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@admin_bp.route('/teams')
def teams():
    teams = Team.query.order_by(Team.name).all()
    return render_template('admin/teams.html', teams=teams)


@admin_bp.route('/teams/<int:team_id>/action', methods=['POST'])
def team_action(team_id):
    team = Team.query.get_or_404(team_id)
    action = request.form.get('action')

    if action == 'ban':
        team.is_banned = True
        flash(f'Team {team.name} banned.', 'warning')
    elif action == 'unban':
        team.is_banned = False
        flash(f'Team {team.name} unbanned.', 'success')
    elif action == 'pause':
        team.is_paused = True
        flash(f'Team {team.name} paused.', 'warning')
    elif action == 'unpause':
        team.is_paused = False
        flash(f'Team {team.name} unpaused.', 'success')
    elif action == 'restrict':
        team.is_restricted = True
        flash(f'Team {team.name} restricted from challenges.', 'warning')
    elif action == 'unrestrict':
        team.is_restricted = False
        flash(f'Team {team.name} unrestricted.', 'success')
    elif action == 'reset':
        Solve.query.filter_by(team_id=team.id).delete()
        Submission.query.filter_by(team_id=team.id).delete()
        db.session.commit()
        flush_cache()
        flash(f'Team {team.name} progress reset.', 'warning')
        return redirect(url_for('admin.teams'))
    elif action == 'delete':
        team_name = team.name
        Solve.query.filter_by(team_id=team.id).delete()
        Submission.query.filter_by(team_id=team.id).delete()
        TeamMember.query.filter_by(team_id=team.id).delete()
        db.session.delete(team)
        db.session.commit()
        flush_cache()
        flash(f'Team {team_name} permanently deleted.', 'warning')
        return redirect(url_for('admin.teams'))

    db.session.commit()
    return redirect(url_for('admin.teams'))


# â”€â”€ Challenges â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@admin_bp.route('/challenges')
def challenges():
    chals = Challenge.query.order_by(Challenge.category, Challenge.points).all()
    return render_template('admin/challenges.html', challenges=chals)


@admin_bp.route('/challenges/new', methods=['GET', 'POST'])
def challenge_new():
    if request.method == 'POST':
        title  = request.form.get('title', '').strip()
        slug   = slugify(title)
        if not title:
            flash('Title required.', 'error')
            return render_template('admin/challenge_form.html', challenge=None)

        if Challenge.query.filter_by(slug=slug).first():
            flash('Challenge title already exists.', 'error')
            return render_template('admin/challenge_form.html', challenge=None)

        ch = Challenge(
            title       = title,
            slug        = slug,
            description = request.form.get('description', ''),
            category    = request.form.get('category', 'misc'),
            points      = int(request.form.get('points', 100)),
            difficulty  = request.form.get('difficulty', 'easy'),
            flag        = request.form.get('flag', '').strip(),
            is_dynamic  = 'is_dynamic' in request.form,
            is_hidden   = 'is_hidden' in request.form,
            is_boss     = 'is_boss' in request.form,
            connection_info = request.form.get('connection_info', '').strip() or None,
        )
        db.session.add(ch)
        db.session.flush()

        files = request.files.getlist('challenge_files')
        if files and any(f.filename for f in files):
            saved = _save_challenge_files(ch.id, files)
            if saved:
                ch.files_json = json.dumps(saved)

        db.session.commit()
        flash(f'Challenge "{title}" created.', 'success')
        return redirect(url_for('admin.challenges'))

    return render_template('admin/challenge_form.html', challenge=None)


@admin_bp.route('/challenges/<int:chal_id>/edit', methods=['GET', 'POST'])
def challenge_edit(chal_id):
    ch = Challenge.query.get_or_404(chal_id)
    if request.method == 'POST':
        ch.title        = request.form.get('title', ch.title).strip()
        ch.slug         = slugify(ch.title)
        ch.description  = request.form.get('description', ch.description)
        ch.category     = request.form.get('category', ch.category)
        ch.points       = int(request.form.get('points', ch.points))
        ch.difficulty   = request.form.get('difficulty', ch.difficulty)
        ch.flag         = request.form.get('flag', ch.flag).strip()
        ch.is_dynamic   = 'is_dynamic' in request.form
        ch.is_hidden    = 'is_hidden' in request.form
        ch.is_boss      = 'is_boss' in request.form
        ch.connection_info = request.form.get('connection_info', '').strip() or None

        files = request.files.getlist('challenge_files')
        if files and any(f.filename for f in files):
            existing = _get_existing_files(ch.id)
            new_files = _save_challenge_files(ch.id, files)
            existing_names = {f['name'] for f in existing}
            for nf in new_files:
                if nf['name'] not in existing_names:
                    existing.append(nf)
            ch.files_json = json.dumps(existing) if existing else None

        db.session.commit()
        flash('Challenge updated.', 'success')
        return redirect(url_for('admin.challenges'))

    return render_template('admin/challenge_form.html', challenge=ch)


@admin_bp.route('/challenges/<int:chal_id>/delete-file', methods=['POST', 'GET'])
def challenge_delete_file(chal_id):
    ch = Challenge.query.get_or_404(chal_id)
    filename = request.form.get('filename') or request.args.get('filename', '')
    if filename and ch.files_json:
        files = json.loads(ch.files_json)
        files = [f for f in files if f['name'] != filename]
        ch.files_json = json.dumps(files) if files else None
        from app.services.storage_service import delete_file
        delete_file(chal_id, filename)
        db.session.commit()
        flash(f'File "{filename}" deleted.', 'success')
    return redirect(url_for('admin.challenge_edit', chal_id=chal_id))


@admin_bp.route('/challenges/<int:chal_id>/toggle-hidden', methods=['POST'])
def challenge_toggle_hidden(chal_id):
    ch = Challenge.query.get_or_404(chal_id)
    ch.is_hidden = not ch.is_hidden
    db.session.commit()
    flash(f'Challenge {"hidden" if ch.is_hidden else "visible"}.', 'info')
    return redirect(url_for('admin.challenges'))


@admin_bp.route('/challenges/<int:chal_id>/delete', methods=['POST'])
def challenge_delete(chal_id):
    ch = Challenge.query.get_or_404(chal_id)
    try:
        from app.models.security import SecurityEvent
        SecurityEvent.query.filter_by(challenge_id=chal_id).update({'challenge_id': None})
        Hint.query.filter_by(challenge_id=chal_id).delete()
        Solve.query.filter_by(challenge_id=chal_id).delete()
        Submission.query.filter_by(challenge_id=chal_id).delete()
        db.session.delete(ch)
        db.session.commit()
        flush_cache()
        flash('Challenge deleted.', 'warning')
    except Exception as e:
        db.session.rollback()
        flash(f'Delete failed: {str(e)}', 'error')
    return redirect(url_for('admin.challenges'))


@admin_bp.route('/challenges/import', methods=['POST'])
def challenge_import():
    f = request.files.get('zip_file')
    if not f or not f.filename.endswith('.zip'):
        flash('Please upload a .zip file.', 'error')
        return redirect(url_for('admin.challenges'))

    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
        f.save(tmp.name)
        success = import_challenge_from_zip(tmp.name)

    os.unlink(tmp.name)
    if success:
        flash('Challenge imported successfully.', 'success')
    else:
        flash('Import failed or challenge already exists.', 'error')

    return redirect(url_for('admin.challenges'))


# â”€â”€ Submissions â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@admin_bp.route('/submissions')
def submissions():
    page = request.args.get('page', 1, type=int)
    q    = request.args.get('q', '')
    query = Submission.query.order_by(Submission.submitted_at.desc())
    if q:
        from app.models.team import Team as T
        query = query.join(T).filter(T.name.ilike(f'%{q}%'))
    subs = query.paginate(page=page, per_page=50, error_out=False)
    return render_template('admin/submissions.html', subs=subs, q=q)


# â”€â”€ Security Monitor â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@admin_bp.route('/security')
def security():
    events = SecurityEvent.query.order_by(
        SecurityEvent.created_at.desc()
    ).limit(200).all()
    return render_template('admin/security.html', events=events)


@admin_bp.route('/security/<int:ev_id>/review', methods=['POST'])
def security_review(ev_id):
    ev = SecurityEvent.query.get_or_404(ev_id)
    ev.is_reviewed = True
    db.session.commit()
    flash('Event marked as reviewed.', 'success')
    return redirect(url_for('admin.security'))


# â”€â”€ Settings â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@admin_bp.route('/settings')
def settings():
    state = EventState.get()
    return render_template('admin/settings.html', state=state)
