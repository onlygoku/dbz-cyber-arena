from datetime import datetime
from app import db


class SecurityEvent(db.Model):
    __tablename__ = 'security_events'

    id          = db.Column(db.Integer, primary_key=True)
    event_type  = db.Column(db.String(64), nullable=False)  # excessive_submissions, same_ip, fast_solve, flag_share
    team_id     = db.Column(db.Integer, db.ForeignKey('teams.id'))
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'))
    challenge_id= db.Column(db.Integer, db.ForeignKey('challenges.id'))
    details     = db.Column(db.Text)
    ip_address  = db.Column(db.String(64))
    severity    = db.Column(db.String(16), default='medium')  # low/medium/high/critical
    is_reviewed = db.Column(db.Boolean, default=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    team      = db.relationship('Team')
    user      = db.relationship('User')
    challenge = db.relationship('Challenge')

    def __repr__(self):
        return f'<SecurityEvent {self.event_type} team={self.team_id}>'
