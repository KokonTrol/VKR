from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from models import *
app = Flask(__name__)

@app.route('/')
def hello_world():
	return render_template('load_page.html')
@app.route('/load')
def load_db():
	with app.app_context():
		return str(db.session.query(Scores).filter_by(test_number=1).count())

if __name__ == '__main__':
	app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{username}:{password}@{host}:{port}/{db}?charset=utf8'.format(username="kokon",
		password="TrOlOlO123))", host="127.0.0.1", port=3306, db="prediction")
	db.init_app(app)
	app.run(debug=True, port=8000)

