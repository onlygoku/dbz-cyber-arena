from datetime import datetime
from app import db


class Challenge(db.Model):
    __tablename__ = 'challenges'

    id           = db.Column(db.Integer, primary_key=True)
    title        = db.Column(db.String(128), unique=True, nullable=False)
    slug         = db.Column(db.String(128), unique=True, nullable=False)
    description  = db.Column(db.Text, nullable=False)
    category     = db.Column(db.String(64), nullable=False)
    points       = db.Column(db.Integer, nullable=False)
    difficulty   = db.Column(db.String(16), nullable=False)  # easy/medium/hard/extreme
    flag         = db.Column(db.String(256), nullable=False)  # inner value only
    is_dynamic   = db.Column(db.Boolean, default=False)
    is_hidden    = db.Column(db.Boolean, default=False)
    is_boss      = db.Column(db.Boolean, default=False)

    # External server (pwn)
    connection_info = db.Column(db.String(256))  # e.g. nc pwn.server.com 1337

    # Files
    files_json   = db.Column(db.Text)  # JSON list of file paths

    # Automatic hint schedule (JSON)
    hint_schedule_json = db.Column(db.Text)

    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    released_at  = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    hints       = db.relationship('Hint', back_populates='challenge', lazy='dynamic')
    solves      = db.relationship('Solve', back_populates='challenge', lazy='dynamic')
    submissions = db.relationship('Submission', back_populates='challenge', lazy='dynamic')

    @property
    def solve_count(self):
        return self.solves.count()

    @property
    def attempt_count(self):
        return self.submissions.count()

    @property
    def solve_rate(self):
        if self.attempt_count == 0:
            return 0.0
        return round(self.solve_count / self.attempt_count * 100, 1)

    @property
    def first_blood(self):
        return self.solves.order_by('solved_at').first()

    def __repr__(self):
        return f'<Challenge {self.title}>'


class Hint(db.Model):
    __tablename__ = 'hints'

    id             = db.Column(db.Integer, primary_key=True)
    challenge_id   = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=False)
    content        = db.Column(db.Text, nullable=False)
    cost           = db.Column(db.Integer, default=0)
    auto_release_minutes = db.Column(db.Integer)  # minutes after challenge release
    auto_release_solves  = db.Column(db.Integer)  # release after N solves
    is_visible     = db.Column(db.Boolean, default=False)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    challenge = db.relationship('Challenge', back_populates='hints')

    def __repr__(self):
        return f'<Hint {self.id} challenge={self.challenge_id}>'
