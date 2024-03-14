from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Results(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    succes_done = db.Column(db.Boolean, default=False)
    score = db.Column(db.Float, default=0.0)

class Comands(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Scores(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    subject = db.relationship('Subject', backref=db.backref('scores', lazy=True))
    result_id = db.Column(db.Integer, db.ForeignKey('results.id'), nullable=False)
    result = db.relationship('Results', backref=db.backref('scores', lazy=True))
    comands_id = db.Column(db.Integer, db.ForeignKey('comands.id'), nullable=False)
    comands = db.relationship('Comands', backref=db.backref('scores', lazy=True))
    visiting = db.Column(db.Float, default=0.0)
    scores_before = db.Column(db.Float, default=0.0)
    scores_test = db.Column(db.Float, default=0.0)
    test_number = db.Column(db.Integer, nullable=False)