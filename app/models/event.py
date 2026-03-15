from datetime import datetime
from app import db


class EventState(db.Model):
    __tablename__ = 'event_state'

    id              = db.Column(db.Integer, primary_key=True)
    flag_prefix     = db.Column(db.String(16), default='THA')
    ctf_name        = db.Column(db.String(128), default='Dragon Ball Z Cyber Arena')
    is_started      = db.Column(db.Boolean, default=False)
    is_ended        = db.Column(db.Boolean, default=False)
    is_frozen       = db.Column(db.Boolean, default=False)
    start_time      = db.Column(db.DateTime)
    end_time        = db.Column(db.DateTime)
    announcement    = db.Column(db.Text)
    updated_at      = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def get(cls):
        return cls.query.first()
