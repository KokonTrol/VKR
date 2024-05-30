from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_migrate import Migrate
from flask_login import LoginManager, login_required, login_user, current_user, logout_user

from models import *
from getTableBD import _FillDataEducation as _FillDataEducation
from prediction import PredictClass, GetListGroup
from convertData import Convert as ConvertLoadedData
import pandas as pd
import io
import random

from env import *

app = Flask(__name__)
dataEducation = {}

users_tables = {}

_isFirstRun = True
ALLOWED_EXTENSIONS = {'xls', 'xlsx'}
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{username}:{password}@{host}:{port}/{db}?charset=utf8'.format(username=DBUSER,
		password=DBPASSWORD, host=DBHOST, port=DBPORT, db=DBNAME)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = SECRETKEY
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'
@login_manager.user_loader
def load_user(user_id):
    return db.session.query(Admin).get(user_id)

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

@app.route('/admin_panel', methods = ['get', 'post'])
@login_required
def admin_panel():
    if request.method == "POST":
        pass
    return render_template('admin_panel.html', subjects=dataEducation.keys())

@app.route('/admin_login', methods = ['get', 'post'])
def admin_login():
    msg = []
    if request.method == "POST":
        user = db.session.query(Admin).filter(Admin.username == request.form.get('login')).first()
        if len(request.form.get('password'))<8:
            msg.append("Длина пароля должна быть больше 8 символов")
        elif (user):
            if user.password == None:
                user.set_password(request.form.get('password'))
                db.session.commit()
            if user.check_password(request.form.get('password')):
                login_user(user, remember=False)
                return redirect(url_for('admin_panel'))
        else:
            msg.append("Неверный логин или пароль")
        return render_template('admin_login.html', msg = msg)
    else:
        return render_template('admin_login.html', msg = [])

@app.route('/admin_logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('admin_login'))

def UserTableExist(uuid: str, data):
    global users_tables
    print(uuid)
    if uuid not in users_tables.keys():
        users_tables[uuid] = ConvertLoadedData(data)

@app.route('/api/get_tests/', methods = ['post'])
def getTestsNames():
    select = request.form.get("selectedSubject")
    if select and select in dataEducation.keys():
        resp = jsonify(
            [name  for name in dataEducation[select]["original_data"].columns.to_list() if name.startswith("Контрольная")]
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
            uuid = request.form.get("uuid")
            UserTableExist(uuid, io.BytesIO(file.read()))
            tests = [name  for name in users_tables[uuid].columns.to_list() if name.startswith("Контрольная")]
            resp = jsonify(tests)
            resp.status_code = 200
            del tests, select
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
            uuid = request.form.get("uuid")
            UserTableExist(uuid, io.BytesIO(file.read()))
            education = None
            if subject not in dataEducation.keys():
                testsCount = len([name  for name in users_tables[uuid].columns.to_list() if name.startswith("Контрольная")])
                concatData = [d["original_data"] for index, d in dataEducation.items() if (len(d["original_data"].columns)-1)/5==float(testsCount)]
                education = PredictClass(pd.concat(concatData, axis=0))
            else:
                education = dataEducation[subject]["predicting"]
            resp = jsonify({})
            resp.status_code = 200
            return resp, education, test
        else:
            resp = jsonify({"message": "Неправильный вид файла"})
            resp.status_code = 400
            return resp, None, None, None

@app.route('/api/get_exam_prediction', methods = ['post'])
def getExamPrediction():
    uuid = request.form.get("uuid")
    resp, educationed, test = _getStatusCodeData(request)
    if resp.status_code == 400:
        return resp
    else:
        print(users_tables[uuid].columns)
        res = list(educationed.GetExam(users_tables[uuid], test))
        groups = GetListGroup(users_tables[uuid])[0]
        pairs = [{"name": users_tables[uuid]["ФИО"][i],"group": groups[i], "result": round(res[i]*100, 2)} for i in range(len(res))]
        resp = jsonify(pairs)
        resp.status_code = 200
        del educationed, test
        return resp

@app.route('/api/get_test_prediction', methods = ['post'])
def getTestPrediction():
    uuid = request.form.get("uuid")
    resp, educationed, test = _getStatusCodeData(request)
    if resp.status_code == 400:
        return resp
    else:
        res = list(educationed.GetTest(users_tables[uuid], test))
        groups = GetListGroup(users_tables[uuid])[0]
        pairs = [{"name": users_tables[uuid]["ФИО"][i],"group": groups[i], "result": res[i]} for i in range(len(res))]
        resp = jsonify(pairs)
        resp.status_code = 200
        del educationed, test
        return resp


import uuid
@app.route('/', methods = ['POST', 'GET'])
def loadData():
    return render_template('load_page.html', subjects=dataEducation.keys(), uuid = uuid.uuid4())

@app.route('/solo', methods = ['POST', 'GET'])
def loadDataSolo():
    return render_template('solo_page.html', subjects=dataEducation.keys())

if __name__ == '__main__':
	app.run(debug=True, port=8000)


