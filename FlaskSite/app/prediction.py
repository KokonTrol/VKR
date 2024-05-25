from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.preprocessing import MinMaxScaler
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
from itertools import chain

def MakeFloat(data):
    convert_dict = {}
    for name in data.columns.difference(["Не сдал(-а)"]):
        convert_dict[name] = float
    convert_dict["Не сдал(-а)"] = int
    return data.astype(convert_dict)

def MinMaxColumns(data, columns: list):
    scaler = MinMaxScaler()
    return scaler.fit_transform(data[columns])

def SplitTestTrainTest(data, exam, not_for_prediction):
    return data[data.loc[:,:exam].columns.difference(not_for_prediction+[exam, "Не сдал(-а)"])], data[exam]


def SplitTestTrainPass(data, exam, not_for_prediction):
    return data[data.loc[:,:exam].columns.difference(["Не сдал(-а)"]+not_for_prediction)], data["Не сдал(-а)"]


class PredictClass():
    def __init__(self, _data):
        self.exams = []
        self.scores = []
        self.being = []
        self.countscores = []
        self.sqrt_vars = []

        self.data = None
        
        self._not_for_prediction = ["ФИО", "Команда", "Команды", "Направление", "Не сдал(-а)", "Оценка", "Баллы", "Повышение оценки"]

        self.models_pass = {}
        self.models_test = {}
        
        self.SetData(_data)

    def ClearData(self, prediction):
        print(type(prediction), prediction.columns)
        prediction = MakeFloat(prediction.drop(prediction.columns.difference(["Не сдал(-а)"]+self.exams+self.scores+self.being+self.countscores+self.sqrt_vars), axis=1))
        print(type(prediction), prediction.columns)
        prediction[self.countscores+self.sqrt_vars] = MinMaxColumns(prediction, self.countscores+self.sqrt_vars)
        return prediction

    def SetData(self, _data):
        self.exams = [name  for name in _data.columns.to_list() if name.startswith("Контрольная")]
        self.scores = [name  for name in _data.columns.to_list() if name.startswith("Баллы ")]
        self.being = [name  for name in _data.columns.to_list() if name.startswith("Посещение ")]
        self.countscores = [name  for name in _data.columns.to_list() if name.startswith("Количество ")]
        self.sqrt_vars = [name  for name in _data.columns.to_list() if name.startswith("Корень ")]

        print(_data.columns)
        self.data = self.ClearData(_data)

        self.models_pass = {}
        self.models_test = {}
        for ex in self.exams:
            X, Y = SplitTestTrainPass(self.data, ex, [])
            ab = LogisticRegression()
            self.models_pass[ex] = ab.fit(X, Y)

            X, Y = SplitTestTrainTest(self.data, ex, [])
            lr = LinearRegression()
            self.models_test[ex] = lr.fit(X, Y)

    def GetExam(self, prediction, ex):
        x_, _ = SplitTestTrainPass(self.ClearData(prediction), ex, [])
        class_index = np.where(self.models_pass[ex].classes_ == 1)
        result = self.models_pass[ex].predict_proba(x_)
        result = list(chain(*chain(*result[:,class_index])))
        return result

    def GetTest(self, prediction, ex):
        x_, _ = SplitTestTrainTest(self.ClearData(prediction), ex, [])
        result = self.models_test[ex].predict(x_)
        return result
    
    def SplitAlreadyPassed(self, data, ex):
        ex_ind = self.exams.index(ex) + 1
        passed = data[(data[self.exams[:ex_ind]].sum(axis=1) * 20 + data[self.scores[:ex_ind]].sum(axis=1) * 100) >= 61.0]
        return data.drop(passed.index, axis=0), passed
    



