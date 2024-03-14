from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from models import *
from getTableBD import _FillDataEducation
app = Flask(__name__)
dataEducation = {}
_isFirstRun = True

@app.before_request
def beforeRequest():
	global _isFirstRun, dataEducation
	if _isFirstRun:
		dataEducation = _FillDataEducation()
		_isFirstRun = False

@app.route('/')
def hello_world():
	global dataEducation
	return render_template('load_page.html', data=dataEducation.keys())
@app.route('/load')
def load_db():
	with app.app_context():
		return str(db.session.query(Scores).filter_by(test_number=1).count())

if __name__ == '__main__':
	app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{username}:{password}@{host}:{port}/{db}?charset=utf8'.format(username="kokon",
		password="TrOlOlO123))", host="127.0.0.1", port=3306, db="prediction")
	db.init_app(app)
	app.run(debug=True, port=8000)

