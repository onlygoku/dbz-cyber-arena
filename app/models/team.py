import secrets
from datetime import datetime
from app import db


class Team(db.Model):
    __tablename__ = 'teams'

    id           = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(64), unique=True, nullable=False, index=True)
    invite_code  = db.Column(db.String(16), unique=True, nullable=False)
    is_banned    = db.Column(db.Boolean, default=False)
    is_paused    = db.Column(db.Boolean, default=False)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    members  = db.relationship('TeamMember', back_populates='team', lazy='dynamic')
    solves   = db.relationship('Solve', back_populates='team', lazy='dynamic')
    submissions = db.relationship('Submission', back_populates='team', lazy='dynamic')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.invite_code:
            self.invite_code = secrets.token_hex(8)

    @property
    def score(self):
        from app.services.score_service import get_team_score
        return get_team_score(self.id)

    @property
    def active_members(self):
        return self.members.filter_by(is_active=True).all()

    @property
    def member_count(self):
        return self.members.filter_by(is_active=True).count()

    def regenerate_invite(self) -> str:
        self.invite_code = secrets.token_hex(8)
        return self.invite_code

    def __repr__(self):
        return f'<Team {self.name}>'


class TeamMember(db.Model):
    __tablename__ = 'team_members'

    id         = db.Column(db.Integer, primary_key=True)
    team_id    = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_captain = db.Column(db.Boolean, default=False)
    is_active  = db.Column(db.Boolean, default=True)
    joined_at  = db.Column(db.DateTime, default=datetime.utcnow)

    team = db.relationship('Team', back_populates='members')
    user = db.relationship('User', back_populates='team_memberships')

    __table_args__ = (
        db.UniqueConstraint('team_id', 'user_id'),
    )

    def __repr__(self):
        return f'<TeamMember team={self.team_id} user={self.user_id}>'
