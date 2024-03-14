from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from models import *
from getTableBD import _FillDataEducation
from prediction import Education
from convertData import Convert as ConvertLoadedData
import pandas as pd
import logging

app = Flask(__name__)
dataEducation = {}
_isFirstRun = True
ALLOWED_EXTENSIONS = {'xls', 'xlsx'}
def allowed_file(filename):
   return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.before_request
def beforeRequest():
	global _isFirstRun, dataEducation
	if _isFirstRun:
		dataEducation = _FillDataEducation()
		_isFirstRun = False

@app.route('/load')
def load_db():
	with app.app_context():
		return str(db.session.query(Scores).filter_by(test_number=1).count())

@app.route('/', methods = ['POST', 'GET'])
def loadData():
	if request.method == 'POST':
		# user = request.form['loadDataForm']
		app.logger.info(request.form)

		if 'formFile' not in request.files:
			return redirect(request.url)
		file = request.files.get('formFile')
		# request.files['dataFile']
		if file and allowed_file(file.filename):
			selectSub = request.form.get('selectSubject')
			selectTest = request.form.get('selectTest')
			# app.logger.info(f"selectSub: {selectSub}, selectTest={selectTest}")
			if selectSub in dataEducation.keys() and not selectTest:
				testsList = list(dataEducation[selectSub][dataEducation[selectSub].columns[pd.Series(dataEducation[selectSub].columns).str.startswith('Контрольная ')]].columns)
				
				# data = pd.read_excel(file)
				return render_template('load_page.html', subjects = dataEducation.keys(), tests=testsList)
			elif selectSub in dataEducation.keys() and selectTest:
				education = Education(dataEducation[selectSub])
				data = ConvertLoadedData(file)
				res = list(education.GetExam(data, selectTest))
				app.logger.info(res)

				return render_template('load_page.html', results = zip(data["ФИО"], res))
		return redirect("/")
	else:
		return render_template('load_page.html', subjects=dataEducation.keys())

if __name__ == '__main__':
	app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{username}:{password}@{host}:{port}/{db}?charset=utf8'.format(username="kokon",
		password="TrOlOlO123))", host="127.0.0.1", port=3306, db="prediction")
	app.config['TEMPLATES_AUTO_RELOAD'] = True
	db.init_app(app)
	app.run(debug=True, port=8000)

