from models import *
import pandas as pd
from sqlalchemy import func
from prediction import PredictClass
def _FillDataEducation():
    dataEducation = {}
    for sub in [r[0] for r in set(db.session.query(Subject.name).all())]:
        print(sub)
        od = GetTableFromDBSubjectName(db, sub)
        dataEducation[sub] = {"original_data": od, "predicting": PredictClass(od)}
    return dataEducation

def _makeTable(loaded, scores, maxTestNumber):
    convert_dict = {"Не сдал(-а)": int,
                "id результата": int
            }
    loaded = loaded.astype(convert_dict)

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
            loaded.loc[-1] = [score.result_id, 1 if score.result.not_succes_done else 0] + [0.0]*(len(loaded.columns)-2) # 2, score.comands.name, 
            loaded.index = loaded.index + 1  # shifting index
        meeting_name = f"Контрольная работа {score.test_number}"
        loaded.loc[((loaded['id результата'] == score.result_id)), f"Баллы до {meeting_name}"] = score.scores_before
        loaded.loc[((loaded['id результата'] == score.result_id)), f"Количество баллов до {meeting_name}"] = score.scores_count
        loaded.loc[((loaded['id результата'] == score.result_id)), f"Корень дисперсии баллов до {meeting_name}"] = score.sqrt_var
        loaded.loc[((loaded['id результата'] == score.result_id)), f"Посещение до {meeting_name}"] = score.visiting
        loaded.loc[((loaded['id результата'] == score.result_id)), meeting_name] = score.scores_test

    loaded = loaded.drop('id результата', axis=1)
    return loaded

def GetTableFromDBSubjectName(db, subjectName: str):
    loaded = pd.DataFrame(columns=["id результата","Не сдал(-а)"]) # 2 "Команда", 
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


def GetTableFromDBTestCount(db, testCount: int):
    loaded = pd.DataFrame(columns=["id результата", "Не сдал(-а)"]) # 2 "Команда", 
    _ids = [r[0] for r in set(db.session.query(Scores.result_id).group_by(Scores.result_id).having(func.count(Scores.test_number) == testCount).all())]

    subject_ids = [r[0] for r in set(db.session.query(Results.subject_id).filter(
        Results.id.in_(_ids)
        ).all())]
    if subject_ids != None:
        scores = db.session.query(Scores).filter(
            Scores.result_id.in_(_ids)
            ).all()
        # maxTestNumber = db.session.query(func.max(Scores.test_number)).filter(
        #     Scores.subject_id.in_(subject)
        #     ).scalar()
        
        loaded = _makeTable(loaded, scores, testCount) #maxTestNumber)
        print(f"Кол-во КР: {testCount}, длина датафрейма: {len(loaded)}")
        return loaded
        
    else:
        return pd.DataFrame()