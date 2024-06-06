from models import *

def GetIfSubjectExist(subject_name, db):
    subject_temp = db.session.query(Subject).filter_by(name=subject_name)
    if subject_temp.count()>0:
        return subject_temp.first()
    else:
        return None
def DeleteSubject(subject, db):
    if type(subject)!=Subject:
        subject = GetIfSubjectExist(str(subject), db)
        if subject==None:
            return
    db.session.delete(subject)
    db.session.commit()

def AddDataToDB(data, subject_name, app, db):
    if (len(data)==0):
        return False
    exams = [name  for name in data.columns.to_list() if name.startswith("Контрольная")]

    with app.app_context():
        subject_temp = GetIfSubjectExist(subject_name, db)
        if subject_temp==None:
            subject_temp = Subject(name=subject_name)
            db.session.add_all([subject_temp])
            db.session.commit()

        for index, d in data.iterrows():
            result = Results(not_succes_done= d["Не сдал(-а)"]==1.0, subject=subject_temp)
            db.session.add_all([result])
            db.session.commit()
            for ex in exams:
                score = Scores(result=result, visiting=d[f"Посещение до {ex}"], scores_test = d[ex], test_number=exams.index(ex)+1)
                score.scores_before = d[f"Баллы до {ex}"]
                score.scores_count = d[f"Количество баллов до {ex}"]
                score.sqrt_var = d[f"Корень дисперсии баллов до {ex}"]
                score.additionscores = d[f"Доставленные баллы на {ex}"]
                score.beingtest = d[f"Присутствие на {ex}"]
                db.session.add_all([score])
                db.session.commit()
    return True