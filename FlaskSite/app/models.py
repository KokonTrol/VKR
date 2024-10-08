from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash,  check_password_hash
from flask_login import UserMixin
db = SQLAlchemy()

# модель администратора
class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=True)
    time = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.text('CURRENT_TIMESTAMP'))

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self,  password):
        return check_password_hash(self.password, password)

# модель дисциплины
class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    results = db.relationship("Results", back_populates="subject", cascade="all, delete-orphan")

# модель результата дисциплины
class Results(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    not_succes_done = db.Column(db.Boolean, default=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    subject = db.relationship("Subject", back_populates="results")
    scores = db.relationship("Scores", back_populates="result", cascade="all, delete-orphan")

# модель результатов контрольных точее
class Scores(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    result_id = db.Column(db.Integer, db.ForeignKey('results.id'), nullable=False)
    result = db.relationship("Results", back_populates="scores")
    visiting = db.Column(db.Float, default=0.0)
    scores_before = db.Column(db.Float, default=0.0)
    scores_count = db.Column(db.Float, default=0.0)
    sqrt_var = db.Column(db.Float, default=0.0)
    additionscores = db.Column(db.Float, default=0.0)
    scores_test = db.Column(db.Float, default=0.0)
    beingtest = db.Column(db.Boolean, default=False)
    test_number = db.Column(db.Integer, nullable=False)