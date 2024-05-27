import pandas as pd
from math import sqrt
import numpy as np
# import re
# import pymorphy2
# genders = {"masc": 1.0, "femn": 0.0}
# morph = pymorphy2.MorphAnalyzer()

# def GetGender(full_name):
#     name = re.search(r"(?:.* )([^ ]*)(?:[ .]*)", full_name).group(1)
#     gender = morph.parse(name)[0].tag.gender
#     return genders[gender] if gender in genders.keys() else 1.0

def GetInfoLose(row, score_column):
    return 1 if float(row[score_column])<61 else 0

def _ConvertEveryRow(sheet, one_row = False):
    # имя студента
    temp_row = ""
    results = pd.DataFrame(columns=["ФИО", "Команда", "Не сдал(-а)"])
    for name, group in sheet.groupby(["Название РМУП"]):
        if "Предмет контроля" not in group.columns:
            continue
        name_column_test = ""
        if "Контрольная работа" in set(list(group["Предмет контроля"])):
            name_column_test = "Контрольная работа"
        else:
            name_column_test = "Работа на учебной встрече"
        try:
            if (group["Название встречи"].str.contains('Контрольная ').sum()==0 and name_column_test!="Контрольная работа"):
                continue
            count_presence = summ_presence = summ_goals_btest = count_goals = count_meetings = 0

            goals_list = []
            # номер контрольной
            test_number = 1
            # # количество действий с кр (баллы и результаты до)
            for index, row in group.iterrows ():

                if temp_row == "" or temp_row != row["ФИО студента"]:
                    if one_row and temp_row != "":
                        break
                    test_number = 1
                    count_presence = summ_presence = summ_goals_btest = count_goals = count_meetings = 0

                    temp_row = row["ФИО студента"]

                    results.loc[-1] = [temp_row, ", ".join(set(group.loc[(group["ФИО студента"] == temp_row), "Команда"])), GetInfoLose(row, "Итог ТУ")] + [""]*(len(results.columns)-3)
                    results.index = results.index + 1  # shifting index

                if ("Контрольная " in row["Название встречи"] or "Контрольная работа" == row["Предмет контроля"]):
                    meeting_name = f"Контрольная работа {test_number}"

                    if (f"Контрольная работа {test_number}" not in list(results.columns)):
                        if (f"Посещение до {meeting_name}" not in list(results.columns)):
                            results[f"Посещение до {meeting_name}"] = 0.0
                            results[f"Баллы до {meeting_name}"] = 0.0
                            results[f"Количество баллов до {meeting_name}"] = 0.0
                            results[f"Корень дисперсии баллов до {meeting_name}"] = 0.0
                            # results[f"Процент баллов до {meeting_name}"] = 0.0
                        results[meeting_name] = 0.0
                    if (row["Предмет контроля"] == name_column_test):

                        test_score = float(row["Оценка за предметы контроля"]) if row["Оценка за предметы контроля"]!="" else 0
                        results.loc[((results['ФИО'] == temp_row)), f"Контрольная работа {test_number}"] = test_score

                        if count_presence == 0:
                            continue
                        results.loc[((results['ФИО'] == temp_row)), f"Посещение до {meeting_name}"] = round(summ_presence / float(count_presence), 2)
                        results.loc[((results['ФИО'] == temp_row)), f"Баллы до {meeting_name}"] = summ_goals_btest
                        results.loc[((results['ФИО'] == temp_row)), f"Количество баллов до {meeting_name}"] = count_goals
                        results.loc[((results['ФИО'] == temp_row)), f"Корень дисперсии баллов до {meeting_name}"] = sqrt(np.var(goals_list))

                        count_presence = summ_presence = summ_goals_btest = count_goals = count_meetings = 0
                        goals_list = []
                        test_number+=1


                elif (row["Предмет контроля"] != "Посещение"):
                    count_meetings += 1
                    if not pd.isna(row["Оценка за предметы контроля"]):
                        goal = float(row["Оценка за предметы контроля"])
                        goals_list.append(goal)
                        summ_goals_btest += goal
                        if goal>0.0:
                            count_goals += 1
                    else:
                        goals_list.append(0)
                else:
                    count_presence += 1
                    if row["Оценка за предметы контроля"]=="П":
                        summ_presence += 1


            results = results.fillna(0)
            results = results.replace("", 0)
            results = results.drop(results.columns[-5:], axis= 1)
            break
        except Exception as e:
            print(e)
        return results
    
def _ConvertModeusType(sheet, one_row = False):
    sheet.columns = sheet.loc[0, :].values.flatten().tolist()
    sheet.drop(index=[0], inplace=True)
    sheet = sheet.reset_index(drop=True)

    results = pd.DataFrame(columns=["ФИО", "Команда", "Направление", "Не сдал(-а)"])
    count_presence = summ_presence = count_kontr = 0
    summ_goals_btest = count_goals = count_meetings = summ_goals_result = 0

    try:
        for index, row in sheet.iterrows ():
            results.loc[-1] = [row["Обучающийся"], row["Учебные команды"], row["Направление подготовки"], GetInfoLose(row, "Итог текущ.")] + [""]*(len(results.columns)-4)
            results.index = results.index + 1

            count_presence = summ_presence = count_kontr = 0
            summ_goals_btest = count_goals = count_meetings = summ_goals_result = 0

            goals_list = []
            for i in range(5, len(sheet.columns.to_list())):
                if sheet.columns.to_list()[i]!="Контрольная работа":
                    if sheet.columns[i]=="Присутствие":
                        count_presence+=1
                        if (row[i]=="П"):
                            summ_presence+=1
                    elif sheet.columns[i]=="Работа на учебной встрече":
                        count_meetings += 1
                        if not pd.isna(row[i]):
                            goal = (float(row[i]) if "." in str(row[i]) else float(str(row[i]).replace(",", ".")))
                            goals_list.append(goal)
                            summ_goals_btest += goal
                            if goal>0.0:
                                count_goals += 1
                        else:
                            goals_list.append(0)
                else:
                    count_kontr+=1
                    meeting_name = f"Контрольная работа {count_kontr}"

                    if (f"Посещение до {meeting_name}" not in list(results.columns)):
                        results[f"Посещение до {meeting_name}"] = 0
                        results[f"Баллы до {meeting_name}"] = 0
                        results[f"Количество баллов до {meeting_name}"] = 0.0
                        results[f"Корень дисперсии баллов до {meeting_name}"] = 0.0
                        results[meeting_name] = 0

                    results.loc[results.index[-1], f"Посещение до {meeting_name}"] = round(summ_presence / float(count_presence), 2)
                    results.loc[results.index[-1], f"Баллы до {meeting_name}"] = summ_goals_btest
                    results.loc[results.index[-1], f"Количество баллов до {meeting_name}"] = count_goals
                    results.loc[results.index[-1], f"Корень дисперсии баллов до {meeting_name}"] = sqrt(np.var(goals_list))


                    test_score = float(row[i]) if row[i]!="" else 0
                    results.loc[results.index[-1], meeting_name]  = test_score

                    summ_goals_result += summ_goals_btest + test_score

                    count_presence = summ_presence = summ_goals_btest = count_goals = 0
            if one_row:
                break
        results = results.fillna(0)
    except Exception as e:
            print(e)
    return results

    
def Convert(file, one_row = False):
    xls_array = pd.read_excel(file)
    if "Название РМУП" in xls_array.columns:
        return _ConvertEveryRow(xls_array, one_row)
    else:
        return _ConvertModeusType(xls_array, one_row)
    