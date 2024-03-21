from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash,  check_password_hash
from flask_login import LoginManager, UserMixin
db = SQLAlchemy()

class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=True)
    time = db.Column(db.DateTime(timezone=True), nullable=False, server_default=db.text('CURRENT_TIMESTAMP'))

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self,  password):
        return check_password_hash(self.password, password)


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Results(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    succes_done = db.Column(db.Boolean, default=False)
    score = db.Column(db.Float, default=0.0)
    comands_id = db.Column(db.Integer, db.ForeignKey('comands.id'), nullable=False)
    comands = db.relationship('Comands', backref=db.backref('results', lazy=True))
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    subject = db.relationship('Subject', backref=db.backref('results', lazy=True))
    
class Comands(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Scores(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    result_id = db.Column(db.Integer, db.ForeignKey('results.id'), nullable=False)
    result = db.relationship('Results', backref=db.backref('scores', lazy=True))
    
    visiting = db.Column(db.Float, default=0.0)
    scores_before = db.Column(db.Float, default=0.0)
    scores_test = db.Column(db.Float, default=0.0)
    test_number = db.Column(db.Integer, nullable=False)