from sklearn.ensemble import AdaBoostClassifier
from sklearn.linear_model import LogisticRegression, LinearRegression
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np
from itertools import chain

class PredictClass():
    def __init__(self, _data):
        self.exams = [name  for name in _data.columns.to_list() if name.startswith("Контрольная")]
        self.scores = [name  for name in _data.columns.to_list() if name.startswith("Баллы ")]
        self.before = [name  for name in _data.columns.to_list() if name.startswith("Процент ")]
        self.being = [name  for name in _data.columns.to_list() if name.startswith("Посещение ")]
        self.data = _data.drop(_data.columns.difference(["Не сдал(-а)", "Пол"]+self.exams+self.scores+self.being+self.before), axis=1)
        convert_dict = {name: float for name in self.being+self.scores+self.exams+self.before+["Не сдал(-а)"]}
        self.data = self.data.astype(convert_dict)
        self._not_for_prediction = ["ФИО", "Команда", "Направление", "Не сдал(-а)", "Оценка", "Баллы", "Повышение оценки"]
        # self.DTR_model = LinearDiscriminantAnalysis()
        self.ab = AdaBoostClassifier(estimator=LogisticRegression(), learning_rate=2.0, n_estimators=48)
        self.lr = LinearRegression()

    def GetExam(self, prediction, ex):
        temp_data = self.data.loc[:,:ex]
        X = temp_data[temp_data.columns.difference(["Не сдал(-а)"])]
        Y = self.data["Не сдал(-а)"].to_list()
        self.ab.fit(X, Y)
        prediction = prediction[prediction.loc[:,:ex].columns.difference(self._not_for_prediction)]
        # result = self.knn.predict(prediction)
        class_index = np.where(self.ab.classes_ == 0)
        result = list(chain(*chain(*self.ab.predict_proba(prediction)[:,class_index])))
        print(result[:10])
        return result

    def GetTest(self, prediction, ex):
        temp_data = self.data.loc[:,:ex]
        X = temp_data[temp_data.columns.difference(["Не сдал(-а)", ex])]
        Y = self.data[ex].to_list()
        self.lr.fit(X, Y)
        data_prediction = self.lr.predict(prediction[prediction.loc[:,:ex].columns.difference(self._not_for_prediction+[ex])])
        # data_prediction = [y_train_original[list(y_train).index(i)] for i in data_prediction]
        # print(accuracy_score(data_prediction, y_test))  
        return data_prediction


