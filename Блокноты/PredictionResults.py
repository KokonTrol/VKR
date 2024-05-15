from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, confusion_matrix, recall_score, f1_score, recall_score, r2_score
import numpy as np

accuracy_dict = {
    "recall": recall_score,
    "f1": f1_score,
    "r2": r2_score,
    "mae": mean_absolute_error
}

str_list_keys = '\n'.join(accuracy_dict.keys())
print(f"ДЛЯ ПРОГНОЗИРОВАНИЙ ДОСТУПНЫ СЛЕДУЮЩИЕ ПОДСЧЕТЫ ОШИБОК/ТОЧНОСТЕЙ:\n{str_list_keys}")

def ScoresUnder0(predict, accuracy_type):
    if accuracy_type in ["mae", "r2"]:
        predict[predict < 0] = 0
    return predict

def GetPredict(model, X_train, X_test, y_train, accuracy_type):
    model.fit(X_train, y_train)
    data_prediction = model.predict(X_test)
    data_prediction = ScoresUnder0(data_prediction, accuracy_type)
    return data_prediction

# прогнозирование с разделением выборки на test и train
def PredictionModel(X, Y, models, test_size, accuracy_type):
    global accuracy_dict
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=test_size, random_state=27)
    res = {}
    for key, model in models.items():
        try:
            data_prediction = GetPredict(model, X_train, X_test, y_train, accuracy_type)
            res[key] =round(accuracy_dict[accuracy_type](list(y_test), list(data_prediction)), 3)

        except Exception as e:
            res[key] = 0
    return res

# прогнозирование с разделением выборки на test и train, результат - матрица ошибок
def PredictionModelMatrix(X, Y, models, test_size):
    global accuracy_dict
    X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=test_size, random_state=27)
    res = {}
    for key, model in models.items():
        try:
            data_prediction = GetPredict(model, X_train, X_test, y_train, "")
            res[key] = confusion_matrix(y_test, data_prediction)
        except Exception as e:
            res[key] = 0
    return res

# прогнозирование без разделения
def PredictionModelNew(X, Y, x_, y_, models, accuracy_type):
    global accuracy_dict
    res = {}
    for key, model in models.items():
        try:
            data_prediction = GetPredict(model, X, x_, Y, accuracy_type)
            res[key] =round(accuracy_dict[accuracy_type](list(y_), list(data_prediction)), 3)

        except Exception as e:
            res[key] = 0
    return res

# прогнозирование без разделения, результат - матрица ошибок
def PredictionModelMatrixNew(X, Y, x_, y_, models):
    global accuracy_dict
    res = {}
    for key, model in models.items():
        try:
            model.fit(X, Y)
            data_prediction = GetPredict(model, X, x_, Y, "")
            res[key] = confusion_matrix(y_, data_prediction)
        except Exception as e:
            res[key] = 0
    return res