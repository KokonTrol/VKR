from models import *
import pandas as pd
from sqlalchemy import func

def _FillDataEducation():
    dataEducation = {}
    for sub in [r[0] for r in set(db.session.query(Subject.name).all())]:
        dataEducation[sub] = GetTableFromDBSubjectName(db, sub)
    return dataEducation

def _makeTable(loaded, scores, maxTestNumber):
    convert_dict = {"Сдал(-а)": int,
                "id результата": int,
                "Баллы": float
            }
    loaded = loaded.astype(convert_dict)

    for i in range(1, maxTestNumber+1):
            meeting_name = f"Контрольная работа {i}"
            loaded[f"Посещение до {meeting_name}"] = 0
            loaded[f"Баллы до {meeting_name}"] = 0
            loaded[meeting_name] = 0
            convert_dict = {meeting_name: float,
                f"Баллы до {meeting_name}": float,
                f"Посещение до {meeting_name}": float
            }
            loaded = loaded.astype(convert_dict)
    for score in scores:
        if score.result_id not in list(loaded["id результата"]):
            loaded.loc[-1] = [score.result_id, score.comands.name, score.result.score, 1 if score.result.succes_done else 0] + [0.0]*(len(loaded.columns)-4)
            loaded.index = loaded.index + 1  # shifting index
        meeting_name = f"Контрольная работа {score.test_number}"
        loaded.loc[((loaded['id результата'] == score.result_id)), f"Баллы до {meeting_name}"] = score.scores_before
        loaded.loc[((loaded['id результата'] == score.result_id)), f"Посещение до {meeting_name}"] = score.visiting
        loaded.loc[((loaded['id результата'] == score.result_id)), meeting_name] = score.scores_test

    loaded = loaded.drop('id результата', axis=1)
    return loaded

def GetTableFromDBSubjectName(db, subjectName: str):
    loaded = pd.DataFrame(columns=["id результата", "Команда", "Баллы", "Сдал(-а)"])
    subject = db.session.query(Subject).filter_by(name=subjectName).first()
    if subject != None:
        scores = list(db.session.query(Scores).filter_by(subject_id=subject.id))
        maxTestNumber = db.session.query(func.max(Scores.test_number)).filter_by(subject_id=subject.id).scalar()
        loaded = _makeTable(loaded, scores, maxTestNumber)
        
        return loaded
    else:
        return pd.DataFrame()


def GetTableFromDBTestCount(db, testCount: int):
    loaded = pd.DataFrame(columns=["id результата", "Команда", "Баллы", "Сдал(-а)"])
    _ids = [r[0] for r in set(db.session.query(Scores.subject_id).filter_by(test_number=testCount).all())]

    subject = [r[0] for r in set(db.session.query(Subject.id).filter(
        Subject.id.in_(_ids)
        ).all())]
    if subject != None:
        scores = db.session.query(Scores).filter(
            Scores.subject_id.in_(subject)
            ).all()
        maxTestNumber = db.session.query(func.max(Scores.test_number)).filter(
            Scores.subject_id.in_(subject)
            ).scalar()
        
        loaded = _makeTable(loaded, scores, maxTestNumber)
        return loaded
        
    else:
        return pd.DataFrame()