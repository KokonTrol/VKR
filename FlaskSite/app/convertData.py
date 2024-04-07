import pandas as pd
from sklearn.ensemble import IsolationForest
import re
import pymorphy2
genders = {"masc": 1.0, "femn": 0.0}
morph = pymorphy2.MorphAnalyzer()

def GetGender(full_name):
    name = re.search(r"(?:.* )([^ ]*)(?:[ .]*)", full_name).group(1)
    gender = morph.parse(name)[0].tag.gender
    return genders[gender] if gender in genders.keys() else 1.0

def DeleteAnomalies(df):
    df_numeric = df.select_dtypes(include=['float64', 'int']).copy()
    isf = IsolationForest(contamination=0.1)
    isf.fit(df_numeric)
    anomaly_pred = isf.predict(df_numeric)
    anomaly_indices = df_numeric.index[anomaly_pred == -1]
    df_cleaned = df.drop(anomaly_indices)
    df_cleaned = df_cleaned.sample(frac=1).reset_index(drop=True)
    return df_cleaned

def GetInfoLose(goal):
    return 1 if float(goal)>=61 else 0

def _ConvertEveryRow(sheet, one_row = False):
    # имя студента
    temp_row = ""
    for name, group in sheet.groupby(["Название РМУП"]):
        if "Предмет контроля" not in group.columns:
            continue
        # получение названия предмета контроля для контрольной работы
        name_column_test = ""
        if "Контрольная работа" in set(list(group["Предмет контроля"])):
            name_column_test = "Контрольная работа"
        else:
            name_column_test = "Работа на учебной встрече"
        # создание пустого Dataframe с базовыми колонками
        results = pd.DataFrame(columns=["ФИО", "Пол", "Команда", "Сдал(-а)"])

        try:
            # проверка на наличие контрольной работы в таблице
            if (group["Название встречи"].str.contains('Контрольная ').sum()==0 \
                and name_column_test!="Контрольная работа"):
                continue
            # переменные для подсчета количества присутствий на занятиях, общее количество отметок посещений,баллы
            count_presence = 0
            summ_presence = 0
            count_goals = 0
            # номер контрольной
            test_number = 1
            for index, row in group.iterrows ():
                # проверка на смену имени студента в строке
                if temp_row == "" or temp_row != row["ФИО студента"]:
                    # если необходимо создать только одну строку для нахождения количества контрольных, прерываем цикл обработки
                    if one_row and  temp_row != "":
                        break
                    # обнуление счетчиков
                    test_number = 1
                    count_presence = summ_presence = 0
                    # добавление записи в Dataframe
                    temp_row = row["ФИО студента"]
                    results.loc[-1] = [temp_row, GetGender(temp_row), row["Команда"], \
                        GetInfoLose(row["Итог ТУ"])] + [""]*(len(results.columns)-4)
                    results.index = results.index + 1
                    #получение только одной записи в датафрейме
                    
                # проверка строки начальной таблицы на соответсвие отметки контрольной
                if ("Контрольная " in row["Название встречи"] or "Контрольная работа" == row["Предмет контроля"]):
                    # проверка наличия контрольных точек в Dataframe
                    if (f"Контрольная работа {test_number}" not in list(results.columns)):
                        # добавление колонок для контрольной точки
                        meeting_name = f"Контрольная работа {test_number}"
                        if (f"Посещение до {meeting_name}" not in list(results.columns)):
                            results[f"Посещение до {meeting_name}"] = 0
                            results[f"Баллы до {meeting_name}"] = 0
                        results[meeting_name] = 0
                        # конвертирование типов данных
                        convert_dict = {f"Посещение до {meeting_name}": float,
                                        f"Баллы до {meeting_name}": float,
                                        meeting_name: float
                                    }
                        results = results.astype(convert_dict)
                    # провоерка на оценку контрольной работы
                    if (row["Предмет контроля"] == name_column_test):
                        # запись баллов за контрольную
                        results.loc[((results['ФИО'] == temp_row)), \
                            f"Контрольная работа {test_number}"] = \
                                row["Оценка за предметы контроля"] if row["Оценка за предметы контроля"] else 0
                        meeting_name = f"Контрольная работа {test_number}"
                        if count_presence == 0:
                            continue
                        # заполнение посещаемости и баллов до КР
                        results.loc[((results['ФИО'] == temp_row)), \
                            f"Посещение до {meeting_name}"] = round(summ_presence / float(count_presence), 2)
                        results.loc[((results['ФИО'] == temp_row)), f"Баллы до {meeting_name}"] = count_goals
                        # обнуление счетчиков
                        count_presence = summ_presence = count_goals = 0
                        test_number+=1

                # если строка соответствует баллам за встречу
                elif (row["Предмет контроля"] != "Посещение"):
                    # если ячейка не пустая, добавлять в счетчик баллов
                    if not pd.isna(row["Оценка за предметы контроля"]):
                        count_goals += float(row["Оценка за предметы контроля"])
                else:
                    # увеличение счетчика количества отметок посещения
                    count_presence += 1
                    if row["Оценка за предметы контроля"]=="П":
                        summ_presence += 1
            # удаление пустых колонок лишней контрольной работы
            results.drop(results.columns[-3:], axis= 1 , inplace= True ) 
            
        except Exception as e:
            print(e)
        # заполнение пустых ячеек нулями
        results.fillna(0, inplace=True)
        results.replace("", 0, inplace=True)
        return results

def Convert(file, one_row = False):
    xls_array = pd.read_excel(file)
    return _ConvertEveryRow(xls_array, one_row)
    #преобразование
    