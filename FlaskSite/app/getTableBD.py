from models import *
import pandas as pd
from sqlalchemy import func
from prediction import PredictClass

# заполнение тренировочных данных для каждой дисицплины
def _FillDataEducation():
    dataEducation = {}
    for sub in [r[0] for r in set(db.session.query(Subject.name).all())]:
        print(sub)
        od = GetTableFromDBSubjectName(db, sub)
        # каждой дисциплине принадлежит набор данных из БД и объект класса прогнозирования
        dataEducation[sub] = {"original_data": od, "predicting": PredictClass(od)}
    return dataEducation

# заполнение DataFrame нными из БД
def _makeTable(loaded, scores, maxTestNumber):
    convert_dict = {"Не сдал(-а)": int,
                "id результата": int
            }
    loaded = loaded.astype(convert_dict)

    # создание колонок для каждой контрольной работы
    for i in range(1, maxTestNumber+1):
            meeting_name = f"Контрольная работа {i}"
            loaded[f"Посещение до {meeting_name}"] = 0
            loaded[f"Баллы до {meeting_name}"] = 0
            loaded[f"Количество баллов до {meeting_name}"] = 0.0
            loaded[f"Корень дисперсии баллов до {meeting_name}"] = 0.0                            
            loaded[meeting_name] = 0
            convert_dict = {meeting_name: float,
                f"Баллы до {meeting_name}": float,
                f"Корень дисперсии баллов до {meeting_name}": float,
                f"Количество баллов до {meeting_name}": float,
                f"Посещение до {meeting_name}": float
            }
            loaded = loaded.astype(convert_dict)
    for score in scores:
        if score.result_id not in list(loaded["id результата"]):
            loaded.loc[-1] = [score.result_id, 1 if score.result.not_succes_done else 0] + [0.0]*(len(loaded.columns)-2) 
            loaded.index = loaded.index + 1 
        meeting_name = f"Контрольная работа {score.test_number}"
        loaded.loc[((loaded['id результата'] == score.result_id)), f"Баллы до {meeting_name}"] = score.scores_before
        loaded.loc[((loaded['id результата'] == score.result_id)), f"Количество баллов до {meeting_name}"] = score.scores_count
        loaded.loc[((loaded['id результата'] == score.result_id)), f"Корень дисперсии баллов до {meeting_name}"] = score.sqrt_var
        loaded.loc[((loaded['id результата'] == score.result_id)), f"Посещение до {meeting_name}"] = score.visiting
        loaded.loc[((loaded['id результата'] == score.result_id)), meeting_name] = score.scores_test

    loaded = loaded.drop('id результата', axis=1)
    return loaded

# получение данных из БД в виде объектов моделей по названию дисциплины
def GetTableFromDBSubjectName(db, subjectName: str):
    loaded = pd.DataFrame(columns=["id результата","Не сдал(-а)"])
    subject = db.session.query(Subject).filter_by(name=subjectName).first()
    if subject != None:
        results = [r[0] for r in set(db.session.query(Results.id).filter_by(subject_id=subject.id))]
        scores = list(db.session.query(Scores).filter(
                        Scores.result_id.in_(results)
                        ).all())
        
        maxTestNumber = db.session.query(func.max(Scores.test_number)).filter(
                        Scores.result_id.in_(results)
                        ).scalar()
        loaded = _makeTable(loaded, scores, maxTestNumber)
        
        return loaded
    else:
        return pd.DataFrame()