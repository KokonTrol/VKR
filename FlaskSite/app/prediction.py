from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.svm import SVC
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np

# оценка
Linear_discriminant = LinearDiscriminantAnalysis()
# контрольная
SVC_model = SVC(kernel='rbf')

class Education():
    def __init__(self, _data):
        self.data = _data
        self.exams = [name  for name in self.data.columns.to_list() if name.startswith("Контрольная")]
        self.scores = [name  for name in self.data.columns.to_list() if name.startswith("Баллы ")]
        self.being = [name  for name in self.data.columns.to_list() if name.startswith("Посещение ")]
        convert_dict = {name: float for name in self.being+self.scores+self.exams+["Сдал(-а)"]}
        self.data = self.data.astype(convert_dict)
        self._not_for_prediction = ["ФИО", "Команда", "Направление", "Сдал(-а)", "Пол", "Оценка", "Баллы", "Повышение оценки"]
        self.SVC_model = SVC(kernel='rbf')
        self.Linear_discriminant = LinearDiscriminantAnalysis()

    def GetExam(self, prediction, ex):
        X = self.data[self.data.loc[:,:ex].columns.difference(self._not_for_prediction+[ex])]
        Y = self.data["Сдал(-а)"].to_list()
        self.Linear_discriminant.fit(X, Y)
        prediction = prediction[prediction.loc[:,:ex].columns.difference(self._not_for_prediction+[ex])]
        result = self.Linear_discriminant.predict(prediction)
        return result

    def GetTest(self, prediction, ex):
        X = self.data[self.data.loc[:,:ex].columns.difference(self._not_for_prediction+[ex]+self.scores)] 
        Y = self.data[ex]
        self.SVC_model.fit(X, Y)
        result = self.SVC_model.predict(prediction)
        return result


