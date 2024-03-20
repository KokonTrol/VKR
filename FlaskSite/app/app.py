from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import *
from getTableBD import _FillDataEducation as _FillDataEducation
from prediction import Education
from convertData import Convert as ConvertLoadedData
import pandas as pd
import io
import logging
import random

app = Flask(__name__)
dataEducation = {}
_isFirstRun = True
ALLOWED_EXTENSIONS = {'xls', 'xlsx'}

test_file = "G:\\Мой диск\\Учёба\\8 семестр\\диплом\\Проект\\VKR\\FlaskSite\\тест алгебра.xlsx"
test_select=[]
@app.route('/test/get_tests')
def getTestsNamestest():
    global test_file, test_select

    select = test_select[random.randrange(4)]
    if select and select in dataEducation.keys():
        resp = jsonify(
            list(dataEducation[select][dataEducation[select].columns[pd.Series(dataEducation[select].columns).str.startswith('Контрольная ')]].columns)
        )
        resp.status_code = 200
    else:
        file = test_file
        if file and allowed_file(file):
            data = ConvertLoadedData(test_file)
            tests = list(data[data.columns[pd.Series(data.columns).str.startswith('Контрольная ')]].columns)
            resp = jsonify(tests)
            resp.status_code = 200
        else:
            resp = jsonify({"message": "Неправильный вид файла"})
            resp.status_code = 400
    return resp

@app.route('/test/get_exam_prediction')
def getExamPredictiontest():
    global test_file, test_select
    subject = test_select[random.randrange(4)]
    test = "Контрольная работа 1"
    if not test or not subject:
        resp = jsonify({"message": "Не загружены файлы для нахождения контрольных или не выбрана контрольная"})
        resp.status_code = 400
    else:
        file = test_file

        if file and allowed_file(file):
            data = ConvertLoadedData(file)
            education = None
            if subject not in dataEducation.keys():
                testsCount = len(list(data[data.columns[pd.Series(data.columns).str.startswith('Контрольная ')]].columns))
                concatData = [d for index, d in dataEducation.items() if (len(d.columns)-3)/3==float(testsCount)]
                education = pd.concat(concatData, axis=0)
            else:
                education = dataEducation[subject]
            educationed = Education(education)

            res = list(educationed.GetExam(data, test))
            pairs = [{"name": data["ФИО"][i], "result": res[i]} for i in range(len(res))]
            resp = jsonify(pairs)
            resp.status_code = 200
        else:
            resp = jsonify({"message": "Неправильный вид файла"})
            resp.status_code = 400
    return resp







def allowed_file(filename):
   return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.before_request
def beforeRequest():
    global _isFirstRun, dataEducation, test_select
    if _isFirstRun:
        dataEducation = _FillDataEducation()
        test_select=list(dataEducation.keys())
        test_select.append("new")
        _isFirstRun = False

@app.route('/api/get_tests/', methods = ['post'])
def getTestsNames():
    select = request.form.get("selectedSubject")
    if select and select in dataEducation.keys():
        resp = jsonify(
            list(dataEducation[select][dataEducation[select].columns[pd.Series(dataEducation[select].columns).str.startswith('Контрольная ')]].columns)
        )
        resp.status_code = 200
        return resp

    elif "formFile" not in request.files or not select:
        resp = jsonify({"message": "Не загружены файлы для нахождения контрольных"})
        resp.status_code = 400
        return resp
    else:
        file = request.files.get("formFile")
        if file and allowed_file(file.filename):
            data = ConvertLoadedData(io.BytesIO(file.read()))
            tests = list(data[data.columns[pd.Series(data.columns).str.startswith('Контрольная ')]].columns)
            resp = jsonify(tests)
            resp.status_code = 200
            return resp
        else:
            resp = jsonify({"message": "Неправильный вид файла"})
            resp.status_code = 400
            return resp

def _getStatusCodeData(request):
    test = request.form.get("selectedTest")
    subject = request.form.get("selectedSubject")
    if "formFile" not in request.files or not test or not subject:
        resp = jsonify({"message": "Не загружены файлы для нахождения контрольных или не выбрана контрольная"})
        resp.status_code = 400
        return resp, None, None, None
    else:
        file = request.files.get("formFile")

        if file and allowed_file(file.filename):
            data = ConvertLoadedData(io.BytesIO(file.read()))
            education = None
            if subject not in dataEducation.keys():
                testsCount = len(list(data[data.columns[pd.Series(data.columns).str.startswith('Контрольная ')]].columns))
                concatData = [d for index, d in dataEducation.items() if (len(d.columns)-2)/3==float(testsCount)] #делать -3, если будет команда снова
                education = pd.concat(concatData, axis=0)
            else:
                education = dataEducation[subject]
            educationed = Education(education)
            resp = jsonify({})
            resp.status_code = 200
            return resp, educationed, data, test
        else:
            resp = jsonify({"message": "Неправильный вид файла"})
            resp.status_code = 400
            return resp, None, None, None

@app.route('/api/get_exam_prediction', methods = ['post'])
def getExamPrediction():
    resp, educationed, data, test = _getStatusCodeData(request)
    if resp.status_code == 400:
        return resp
    else:
        res = list(educationed.GetExam(data, test))
        pairs = [{"name": data["ФИО"][i], "result": res[i]} for i in range(len(res))]
        resp = jsonify(pairs)
        resp.status_code = 200
        return resp

@app.route('/api/get_test_prediction', methods = ['post'])
def getTestPrediction():
    resp, educationed, data, test = _getStatusCodeData(request)
    if resp.status_code == 400:
        return resp
    else:
        res = list(educationed.GetTest(data, test))
        data = data.reset_index(drop=True)
        pairs = [{"name": data["ФИО"][i], "result": int(res[i])} for i in range(len(res))]
        resp = jsonify(pairs)
        resp.status_code = 200
        return resp

@app.route('/', methods = ['POST', 'GET'])
def loadData():
    return render_template('load_page.html', subjects=dataEducation.keys())

if __name__ == '__main__':
	app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{username}:{password}@{host}:{port}/{db}?charset=utf8'.format(username="kokon",
		password="TrOlOlO123))", host="127.0.0.1", port=3306, db="prediction")
	app.config['TEMPLATES_AUTO_RELOAD'] = True
	db.init_app(app)
	app.run(debug=True, port=8000)

