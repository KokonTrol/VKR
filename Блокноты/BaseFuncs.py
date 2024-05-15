
import pandas as pd
def GetDataFrameListFromFileRaw(file_name):
    xl2 = None
    if file_name.endswith('.xlsx'):
        xl2 = pd.ExcelFile(
            file_name,
            engine='openpyxl'
        )
    elif file_name.endswith('.xls'):
        xl2 = pd.ExcelFile(
            file_name,
            engine='xlrd'
        )
    else:
        return []
    return [xl2.parse(sheet) for sheet in xl2.sheet_names]


def GetDataFrameListFromFileConverted(file_name):
    return pd.read_csv(file_name, delimiter=";", encoding='cp1251', decimal=",")


# получить имя файла (и его путь) из диалогового окна
import tkinter.filedialog as tkFileDialog
def OpenFileNameWindows():
    return tkFileDialog.askopenfilename( title='Выберите файл:')


# сохранить файл
import os
def SaveFileCSV(path, filename, results, csv = True):
    if not os.path.exists(path):
        os.makedirs(path)
    if csv:
        results.to_csv(f"{path}/{filename}.csv", index=False, sep=';', encoding='cp1251')
    else:
        results.to_excel(f"{path}/{filename}.xlsx")


# получить пол из имени
import re
import pymorphy2
genders = {"masc": 1, "femn": 0}
morph = pymorphy2.MorphAnalyzer()
def GetGender(full_name):
    name = re.search(r"(?:.* )([^ ]*)(?:[ .]*)", full_name).group(1)
    gender = morph.parse(name)[0].tag.gender
    return genders[gender] if gender in genders.keys() else 1


def ConvertFloatByTestName(data, meeting_name):
    convert_dict = {f"Посещение до {meeting_name}": float,
                    f"Баллы до {meeting_name}": float,
                    f"Количество баллов до {meeting_name}": float,
                    f"Процент баллов до {meeting_name}": float,
                    meeting_name: float
                }
    return data.astype(convert_dict)


list_result_mark = ["удовл.", "хор.", "отл."]
def GetInfoLose(row, score_column):
    return 1 if float(row[score_column])<61 else 0
    if float(row[score_column])>=61:
        return 0
    return 1 if row[score_column] not in list_result_mark else 0