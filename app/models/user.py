import secrets
from datetime import datetime, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email         = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin      = db.Column(db.Boolean, default=False)
    is_verified   = db.Column(db.Boolean, default=False)
    is_banned     = db.Column(db.Boolean, default=False)
    verify_token  = db.Column(db.String(64), unique=True)
    reset_token        = db.Column(db.String(64), unique=True)
    reset_token_expiry = db.Column(db.DateTime)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    last_login    = db.Column(db.DateTime)

    # Relationships
    team_memberships = db.relationship('TeamMember', back_populates='user', lazy='dynamic')

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def generate_verify_token(self) -> str:
        self.verify_token = secrets.token_urlsafe(32)
        return self.verify_token

    def generate_reset_token(self) -> str:
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
        return self.reset_token

    def is_reset_token_valid(self) -> bool:
        if not self.reset_token or not self.reset_token_expiry:
            return False
        return datetime.utcnow() < self.reset_token_expiry

    @property
    def team(self):
        m = self.team_memberships.filter_by(is_active=True).first()
        return m.team if m else None

    @property
    def is_team_captain(self) -> bool:
        m = self.team_memberships.filter_by(is_active=True).first()
        return m.is_captain if m else False

    def __repr__(self):
        return f'<User {self.username}>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))