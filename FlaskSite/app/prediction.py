from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.preprocessing import MinMaxScaler
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
from itertools import chain
import re
group_reg = r"([А-Яа-яA-Za-z]+ П-[^,\n]+)"

# преобразование всех колонок в тип float + int
def MakeFloat(data):
    convert_dict = {}
    for name in data.columns.difference(["Не сдал(-а)"]):
        convert_dict[name] = float
    convert_dict["Не сдал(-а)"] = int
    return data.astype(convert_dict)

# преобразование выбранных колонок по MinMax
def MinMaxColumns(data, columns: list):
    scaler = MinMaxScaler()
    return scaler.fit_transform(data[columns])

# разделение данных на X и Y, где Y - результаты контрольных
def SplitTestTrainTest(data, exam, not_for_prediction):
    return data[data.loc[:,:exam].columns.difference(not_for_prediction+[exam, "Не сдал(-а)"])], data[exam]

# разделение данных на X и Y, где Y - результаты сдачи
def SplitTestTrainPass(data, exam, not_for_prediction):
    return data[data.loc[:,:exam].columns.difference(["Не сдал(-а)"]+not_for_prediction)], data["Не сдал(-а)"]

# выделение в каждой строке колонки названия группы практики
def GetListGroup(data):
    return data["Команда"].str.extract("([А-Яа-яA-Za-z]+ П-[^,\n]+)")

# класс прогнозирования
class PredictClass():
    def __init__(self, _data):
        # список названий колонок по типу данных
        self.exams = []
        self.scores = []
        self.being = []
        self.countscores = []
        self.sqrt_vars = []

        self.data = None
        
        # список колонок, которые не будут учитываться в прогнозе
        self._not_for_prediction = ["ФИО", "Команда", "Команды", "Направление", "Не сдал(-а)","Баллы"]

        # словари моделей для каждой из контрольной работы
        self.models_pass = {}
        self.models_test = {}
        
        # заполнение данных
        self.SetData(_data)

    # очистка и преобразование данных
    def ClearData(self, prediction):
        prediction = MakeFloat(prediction.drop(prediction.columns.difference(["Не сдал(-а)"]+self.exams+self.scores+self.being+self.countscores+self.sqrt_vars), axis=1))
        prediction[self.countscores+self.sqrt_vars] = MinMaxColumns(prediction, self.countscores+self.sqrt_vars)
        return prediction

    # заполнение данных
    def SetData(self, _data):
        self.exams = [name  for name in _data.columns.to_list() if name.startswith("Контрольная")]
        self.scores = [name  for name in _data.columns.to_list() if name.startswith("Баллы ")]
        self.being = [name  for name in _data.columns.to_list() if name.startswith("Посещение ")]
        self.countscores = [name  for name in _data.columns.to_list() if name.startswith("Количество ")]
        self.sqrt_vars = [name  for name in _data.columns.to_list() if name.startswith("Корень ")]

        self.data = self.ClearData(_data)

        self.models_pass = {}
        self.models_test = {}

        # каждой КР соответствует своя модель прогнозирования
        for ex in self.exams:
            X, Y = SplitTestTrainPass(self.data, ex, [])
            ab = LogisticRegression()
            self.models_pass[ex] = ab.fit(X, Y)

            X, Y = SplitTestTrainTest(self.data, ex, [])
            lr = LinearRegression()
            self.models_test[ex] = lr.fit(X, Y)

    # прогнозирование сдачи по заданной контрольной
    def GetExam(self, prediction, ex):
        # получение X данных из загруженного DataFrame
        x_, _ = SplitTestTrainPass(self.ClearData(prediction), ex, [])
        # выделение вероятностей несдачи дисциплины
        class_index = np.where(self.models_pass[ex].classes_ == 1)
        result = self.models_pass[ex].predict_proba(x_)
        result = list(chain(*chain(*result[:,class_index])))
        return result
    # прогнозирование баллов для заданной контрольной
    def GetTest(self, prediction, ex):
        # получение X данных из загруженного DataFrame
        x_, _ = SplitTestTrainTest(self.ClearData(prediction), ex, [])
        result = self.models_test[ex].predict(x_).round(1)
        result[result < 0] = 0
        return result
    
    def SplitAlreadyPassed(self, data, ex):
        ex_ind = self.exams.index(ex) + 1
        passed = data[(data[self.exams[:ex_ind]].sum(axis=1) * 20 + data[self.scores[:ex_ind]].sum(axis=1) * 100) >= 61.0]
        return data.drop(passed.index, axis=0), passed
    



