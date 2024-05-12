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
    # df_numeric = df.select_dtypes(include=['float64', 'int']).copy()
    # isf = IsolationForest(contamination=0.1)
    # isf.fit(df_numeric)
    # anomaly_pred = isf.predict(df_numeric)
    # anomaly_indices = df_numeric.index[anomaly_pred == -1]
    # df_cleaned = df.drop(anomaly_indices)
    # df_cleaned = df_cleaned.sample(frac=1).reset_index(drop=True)
    df_cleaned = df
    return df_cleaned

def GetInfoLose(goal):
    return 1 if float(goal)>=61 else 0

def _ConvertEveryRow(sheet, one_row = False):
    # имя студента
    temp_row = ""
    for name, group in sheet.groupby(["Название РМУП"]):
        if "Предмет контроля" not in group.columns:
            continue
        name_column_test = ""
        if "Контрольная работа" in set(list(group["Предмет контроля"])):
            name_column_test = "Контрольная работа"
        else:
            name_column_test = "Работа на учебной встрече"
        results = pd.DataFrame(columns=["ФИО", "Пол", "Не сдал(-а)"])

        try:
            if (group["Название встречи"].str.contains('Контрольная ').sum()==0 and name_column_test!="Контрольная работа"):
                continue
            max_scores_before_test = {}
            percent = 0
            count_presence = 0
            summ_presence = 0
            count_goals = 0
            # номер контрольной
            test_number = 1
            # # количество действий с кр (баллы и результаты до)
            # count_test_item = 0
            for index, row in group.iterrows ():
                if temp_row == "" or temp_row != row["ФИО студента"]:
                    if one_row and temp_row != "":
                        break
                    test_number = 1
                    count_presence = summ_presence = count_goals = 0.0
                    temp_row = row["ФИО студента"]
                    results.loc[-1] = [temp_row, GetGender(temp_row), 1 if row["Итоговая оценка"]=="неудовл." or row["Итоговая оценка"]=="" else 0] + [""]*(len(results.columns)-3)
                    # results.loc[-1] = [temp_row, GetGender(temp_row), row["Команда"], row["Итог ТУ"], GetInfoLose(row["Итог ТУ"])] + [""]*(len(results.columns)-5)
                    results.index = results.index + 1  # shifting index

                if ("Контрольная " in row["Название встречи"] or "Контрольная работа" == row["Предмет контроля"]):
                    meeting_name = f"Контрольная работа {test_number}"

                    if (f"Контрольная работа {test_number}" not in list(results.columns)):
                        if (f"Посещение до {meeting_name}" not in list(results.columns)):
                            results[f"Посещение до {meeting_name}"] = 0.0
                            results[f"Баллы до {meeting_name}"] = 0.0
                            results[f"Процент баллов до {meeting_name}"] = 0.0
                        results[meeting_name] = 0.0
                    if (row["Предмет контроля"] == name_column_test):

                        results.loc[((results['ФИО'] == temp_row)), f"Контрольная работа {test_number}"] = row["Оценка за предметы контроля"] if row["Оценка за предметы контроля"]!="" else 0 # row["Название встречи"]

                        if meeting_name not in max_scores_before_test:
                            max_scores_before_test[meeting_name] = count_goals
                        elif max_scores_before_test[meeting_name] < count_goals:
                            max_scores_before_test[meeting_name] = count_goals

                        if count_presence == 0: #or results.loc[((results['ФИО'] == temp_row)), f"Посещение до {meeting_name}"].values[0]!=""
                            continue
                        results.loc[((results['ФИО'] == temp_row)), f"Посещение до {meeting_name}"] = round(summ_presence / float(count_presence), 2)
                        results.loc[((results['ФИО'] == temp_row)), f"Баллы до {meeting_name}"] = count_goals*1.0
                        results.loc[((results['ФИО'] == temp_row)), f"Процент баллов до {meeting_name}"] = count_goals*1.0
                        count_presence = summ_presence = count_goals = 0.0
                        test_number+=1


                elif (row["Предмет контроля"] != "Посещение"):
                    if not pd.isna(row["Оценка за предметы контроля"]):
                        count_goals += float(row["Оценка за предметы контроля"])
                else:
                    count_presence += 1
                    if row["Оценка за предметы контроля"]=="П":
                        summ_presence += 1
            results = results.fillna(0)
            results = results.replace("", 0)
            results = results.drop(results.columns[-4:], axis= 1)
            # results = DeleteAnomalies(results)

            del max_scores_before_test[f"Контрольная работа {test_number}"]
            for meeting_name, max_score in max_scores_before_test.items():
                if max_score>0:
                    convert_dict = {f"Посещение до {meeting_name}": float,
                                        f"Баллы до {meeting_name}": float,
                                        f"Процент баллов до {meeting_name}": float,
                                        meeting_name: float
                                    }
                    results = results.astype(convert_dict)
                    results[f"Процент баллов до {meeting_name}"] = results[f"Процент баллов до {meeting_name}"].div(max_score*1.0).round(2)
        except Exception as e:
            print(e)
        return results
    
def _ConvertModeusType(sheet, one_row = False):
    list_result_mark = ["удовл.", "хор.", "отл."]

    sheet.columns = sheet.loc[0, :].values.flatten().tolist()
    sheet.drop(index=[0], inplace=True)
    sheet = sheet.reset_index(drop=True)

    def GetInfoLose(row):
        if float(row["Итог текущ."])>=61:
            return 0
        return 1 if row["Итоговая оценка"] not in list_result_mark else 0

    results = pd.DataFrame(columns=["ФИО", "Пол", "Не сдал(-а)"])
    try:
        max_scores_before_test = {}

        for index, row in sheet.iterrows ():
            results.loc[-1] = [row["Обучающийся"], GetGender(row["Обучающийся"]), GetInfoLose(row)] + [""]*(len(results.columns)-3)
            results.index = results.index + 1

            count_presence = summ_presence = count_kontr = 0
            count_goals = 0
            count_kontr = 0
            for i in range(5, len(sheet.columns.to_list())):
                if sheet.columns.to_list()[i]!="Контрольная работа":
                    if sheet.columns[i]=="Присутствие":
                        count_presence+=1
                        if (row[i]=="П"):
                            summ_presence+=1
                    elif sheet.columns[i]=="Работа на учебной встрече":
                        if row[i]!="" and row[i]:
                            goal = (float(row[i]) if "." in str(row[i]) else float(str(row[i]).replace(",", ".")))
                            if not pd.isna(goal):
                                count_goals += goal
                else:
                    count_kontr+=1
                    meeting_name = f"Контрольная работа {count_kontr}"

                    if meeting_name not in max_scores_before_test:
                        max_scores_before_test[meeting_name] = count_goals

                    elif max_scores_before_test[meeting_name] < count_goals:
                        max_scores_before_test[meeting_name] = count_goals

                    if (f"Посещение до {meeting_name}" not in list(results.columns)):
                        results[f"Посещение до {meeting_name}"] = 0
                        results[f"Баллы до {meeting_name}"] = 0
                        results[f"Процент баллов до {meeting_name}"] = 0
                        results[meeting_name] = 0
                        convert_dict = {f"Посещение до {meeting_name}": float,
                                        f"Баллы до {meeting_name}": float,
                                        f"Процент баллов до {meeting_name}": float,
                                        meeting_name: float
                                        }
                        results = results.astype(convert_dict)
                    results.loc[results.index[-1], f"Посещение до {meeting_name}"] = round(summ_presence / float(count_presence), 2)
                    results.loc[results.index[-1], f"Баллы до {meeting_name}"] = count_goals
                    results.loc[results.index[-1], f"Процент баллов до {meeting_name}"] = count_goals
                    results.loc[results.index[-1], meeting_name]  = float(row[i])

                    count_presence = summ_presence = count_goals = 0
            if one_row:
                break

        results = results.fillna(0)
        for meeting_name, max_score in max_scores_before_test.items():
            results[f"Процент баллов до {meeting_name}"] = results[f"Процент баллов до {meeting_name}"].div(max_score*1.0).round(2)

    except Exception as e:
        print("Ошибка:", e)
    return results

    
def Convert(file, one_row = False):
    xls_array = pd.read_excel(file)
    #преобразование
    if "Название РМУП" in xls_array.columns:
        return _ConvertEveryRow(xls_array, one_row)
    else:
        return _ConvertModeusType(xls_array, one_row)
    