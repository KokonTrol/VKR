from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LinearRegression
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import numpy as np


class Education():
    def __init__(self, _data):
        self.data = _data
        self.exams = [name  for name in self.data.columns.to_list() if name.startswith("Контрольная")]
        self.scores = [name  for name in self.data.columns.to_list() if name.startswith("Баллы ")]
        self.being = [name  for name in self.data.columns.to_list() if name.startswith("Посещение ")]
        convert_dict = {name: float for name in self.being+self.scores+self.exams+["Сдал(-а)"]}
        self.data = self.data.astype(convert_dict)
        self._not_for_prediction = ["ФИО", "Команда", "Направление", "Сдал(-а)", "Оценка", "Баллы", "Повышение оценки"]
        # self.DTR_model = LinearDiscriminantAnalysis()
        self.knn = KNeighborsClassifier(n_neighbors=2)
        self.LinearRegression = LinearRegression()

    def GetExam(self, prediction, ex):
        X = self.data[self.data.loc[:,:ex].columns.difference(self._not_for_prediction)]
        Y = self.data["Сдал(-а)"].to_list()
        self.knn.fit(X, Y)
        prediction = prediction[prediction.loc[:,:ex].columns.difference(self._not_for_prediction)]
        result = self.knn.predict(prediction)
        return result

    def GetTest(self, prediction, ex):
        X = np.array(pd.DataFrame(self.data[self.data.loc[:,:ex].columns.difference(self._not_for_prediction+[ex])]))
        Y = np.array(self.data[ex])
        self.LinearRegression.fit(X, Y)
        data_prediction = self.LinearRegression.predict(prediction[prediction.loc[:,:ex].columns.difference(self._not_for_prediction+[ex])])
        # data_prediction = [y_train_original[list(y_train).index(i)] for i in data_prediction]
        # print(accuracy_score(data_prediction, y_test))  
        return data_prediction
        self.DTR_model.fit(X, Y)
        result = self.SVC_DTR_modelmodel.predict(prediction)
        return result


