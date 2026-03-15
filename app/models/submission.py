from datetime import datetime
from app import db


class Submission(db.Model):
    __tablename__ = 'submissions'

    id           = db.Column(db.Integer, primary_key=True)
    team_id      = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)
    submitted_flag = db.Column(db.String(512), nullable=False)
    is_correct   = db.Column(db.Boolean, default=False)
    ip_address   = db.Column(db.String(64))
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    team      = db.relationship('Team', back_populates='submissions')
    challenge = db.relationship('Challenge', back_populates='submissions')
    user      = db.relationship('User')

    def __repr__(self):
        return f'<Submission team={self.team_id} challenge={self.challenge_id} correct={self.is_correct}>'


class Solve(db.Model):
    __tablename__ = 'solves'

    id           = db.Column(db.Integer, primary_key=True)
    team_id      = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    points       = db.Column(db.Integer, nullable=False)
    solved_at    = db.Column(db.DateTime, default=datetime.utcnow)

    team      = db.relationship('Team', back_populates='solves')
    challenge = db.relationship('Challenge', back_populates='solves')
    user      = db.relationship('User')

    __table_args__ = (
        db.UniqueConstraint('team_id', 'challenge_id'),
    )

    def __repr__(self):
        return f'<Solve team={self.team_id} challenge={self.challenge_id}>'
