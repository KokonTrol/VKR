exams = []
scores = []
being = []
before = []
countscores = []

def FillColumnsList(data):
    global before, being, scores, exams, countscores
    exams = [name  for name in data.columns.to_list() if name.startswith("Контрольная")]
    scores = [name  for name in data.columns.to_list() if name.startswith("Баллы ")]
    being = [name  for name in data.columns.to_list() if name.startswith("Посещение ")]
    before = [name  for name in data.columns.to_list() if name.startswith("Процент ")]
    countscores = [name  for name in data.columns.to_list() if name.startswith("Количество ")]

def MakeFloat(data, addition_list_columns):
    if len(exams) == 0:
        FillColumnsList(data)
    convert_dict = {}
    for i, lst in enumerate([exams, scores, being, before, countscores]):
        for name in lst:
            convert_dict[name] = float
    for column in addition_list_columns:
        convert_dict[column] = float

    return data.astype(convert_dict)


def ModColumns100(data, columns):
    return data[columns].div(100)


def CountMarkColumn(data):
    if "Баллы" not in data.columns:
        return data
    data["Оценка"] = 0
    data.loc[data["Баллы"]<61.0, "Оценка"] = 2
    data.loc[data["Баллы"]>=91.0, "Оценка"] = 5
    data.loc[(data["Баллы"]<91) & (data["Баллы"]>=76.0), "Оценка"] = 4
    data.loc[(data["Баллы"]<76.0) & (data["Баллы"]>=61.0), "Оценка"] = 3
    return data.drop("Баллы", axis=1)

from matplotlib import pyplot as plt
import seaborn as sns
def DrawPlots(data):
    if len(exams) == 0:
        FillColumnsList(data)
    for i, lst in enumerate([exams, scores, being, before]):
        for name in lst:
            # Subset to the airline
            subset = data[name]

            # Draw the density plot
            sns.distplot(a=subset, hist = True, kde = True,
                        kde_kws = {'linewidth': 1},
                        label = name)
            print(f"{name}: Max: {data[name].max()}, Min: {data[name].min()}, Mean: {round(data[name].mean(), 2)}")
        # Plot formatting
        plt.legend(prop={'size': 11})
        plt.tight_layout()
        plt.show()
    display(data[exams+scores+being+before+countscores].boxplot(vert=False))

import scipy.stats as stats
def DeleteByQuantile(data, q1 = 0.15):
    Q1 = data.quantile(q=q1)
    Q3 = data.quantile(q=1.0-q1)
    IQR = data.apply(stats.iqr)

    data_Q = data[~((data < (Q1-1.5*IQR)) | (data > (Q3+1.5*IQR))).any(axis=1)]
    
    if len(exams) == 0:
        FillColumnsList(data)

    for meeting_name in exams:
        data_Q[f"Процент баллов до {meeting_name}"] = data_Q[f"Баллы до {meeting_name}"].div(0.01).round(2)
        max_score = data_Q[f"Баллы до {meeting_name}"].div(0.01).max()
        data_Q[f"Процент баллов до {meeting_name}"] = data_Q[f"Процент баллов до {meeting_name}"].div(max_score*1.0).round(2)
    return data_Q

import numpy as np
def DeleteByZ(data):
    z = np.abs(stats.zscore(data))
    data_Z = data[(z<3).all(axis=1)]
    for meeting_name in exams:
        data_Z[f"Процент баллов до {meeting_name}"] = data_Z[f"Баллы до {meeting_name}"].div(0.01).round(2)
        max_score = data_Z[f"Баллы до {meeting_name}"].div(0.01).max()
        data_Z[f"Процент баллов до {meeting_name}"] = data_Z[f"Процент баллов до {meeting_name}"].div(max_score*1.0).round(2)
    return data_Z