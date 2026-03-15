import os
import json
import zipfile
import tempfile
from flask import current_app
from app import db


def import_challenge_from_dir(challenge_dir: str) -> bool:
    """Import a challenge from a directory containing challenge.json, description.md, flag.txt."""
    try:
        json_path = os.path.join(challenge_dir, 'challenge.json')
        desc_path = os.path.join(challenge_dir, 'description.md')
        flag_path = os.path.join(challenge_dir, 'flag.txt')

        if not os.path.exists(json_path):
            return False

        with open(json_path) as f:
            meta = json.load(f)

        description = ''
        if os.path.exists(desc_path):
            with open(desc_path) as f:
                description = f.read()

        flag = ''
        if os.path.exists(flag_path):
            with open(flag_path) as f:
                flag = f.read().strip()
        else:
            flag = meta.get('flag', '')

        from app.models.challenge import Challenge, Hint
        from app.utils.helpers import slugify

        title = meta.get('title', os.path.basename(challenge_dir))
        slug  = slugify(title)

        existing = Challenge.query.filter_by(slug=slug).first()
        if existing:
            return False  # Already imported

        challenge = Challenge(
            title       = title,
            slug        = slug,
            description = description or meta.get('description', ''),
            category    = meta.get('category', 'misc'),
            points      = int(meta.get('points', 100)),
            difficulty  = meta.get('difficulty', 'easy'),
            flag        = flag,
            is_dynamic  = meta.get('is_dynamic', False),
            is_hidden   = meta.get('is_hidden', False),
            is_boss     = meta.get('is_boss', False),
            connection_info = meta.get('connection_info'),
        )
        db.session.add(challenge)
        db.session.flush()

        # Import hints
        for h in meta.get('hints', []):
            hint = Hint(
                challenge_id=challenge.id,
                content=h.get('content', ''),
                cost=h.get('cost', 0),
                auto_release_minutes=h.get('auto_release_minutes'),
                auto_release_solves=h.get('auto_release_solves'),
                is_visible=h.get('is_visible', False),
            )
            db.session.add(hint)

        db.session.commit()
        current_app.logger.info(f'Imported challenge: {title}')
        return True

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error importing challenge from {challenge_dir}: {e}')
        return False


def import_challenge_from_zip(zip_path: str) -> bool:
    """Extract ZIP and import challenge."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(tmpdir)
        return import_challenge_from_dir(tmpdir)


def import_all_challenges(challenges_dir: str):
    """Scan a directory for challenge sub-directories and import each."""
    for entry in os.scandir(challenges_dir):
        if entry.is_dir():
            import_challenge_from_dir(entry.path)
