import pandas as pd
from math import sqrt
import numpy as np

# конвертирование данных от ИОТ
def GetDataTest(data, ind_pres, ind_score):
    score = -1
    if ind_score != -1:
        score = data.loc[ind_score, "Оценка за предметы контроля"]
        if not pd.isna(score):
            score = (float(score) if "." in str(score) else float(str(score).replace(",", ".")))
    presence = 0
    if (data.loc[ind_pres, "Оценка за предметы контроля"]=="П"):
        presence = 1
    return presence, score
# конвертация данных в формате от ИОТ (one_row - отметка о необходимости считывания одной итоговой строки)
def _ConvertEveryRow(sheet, one_row = False):
    # имя студента
    temp_row = ""
    results = pd.DataFrame(columns=["Баллы", "ФИО", "Команда", "Не сдал(-а)"])

    for name, group in sheet.groupby(["Название РМУП"]):
        # проверка на наличие данных
        if "Предмет контроля" not in group.columns:
            continue
        # название колонки, по которой будет определяться запись о КР
        name_column_test = ""
        if "Контрольная работа" in set(list(group["Предмет контроля"])):
            name_column_test = "Контрольная работа"
        else:
            name_column_test = "Работа на учебной встрече"
        try:
            # проверка на наличие контрольных в дисциплине
            if (group["Название встречи"].str.contains('Контрольная ').sum()==0 and name_column_test!="Контрольная работа"):
                continue
            # обнуление счетчиков (кол-во отметок посещений, кол-во отметок посещений П, сумма баллов до КР, кол-во оценок, количество встреч)
            count_presence = summ_presence = summ_goals_btest = count_goals = count_meetings = 0
            # список баллов
            goals_list = []
            # индексы для данных контрольной
            skip = ind_presence = ind_score = 0
            # номер контрольной
            test_number = 1
            # изменение индексов
            group.reset_index(inplace = True)
            # количество действий с кр (баллы и результаты до)
            for index, row in group.iterrows ():
                # пропуск строк после КР
                if skip > 0:
                    skip-=1
                    continue
                # проверка на смену студента
                if temp_row == "" or temp_row != row["ФИО студента"]:
                    if one_row and temp_row != "":
                        break
                    # обнуление счетчиков
                    test_number = 1
                    count_presence = summ_presence = summ_goals_btest = count_goals = count_meetings = 0
                    # сохранение имени студента
                    temp_row = row["ФИО студента"]
                    # заполнение основной информации студента
                    results.loc[-1] = [row["Итог ТУ"], temp_row, ", ".join(set(group.loc[(group["ФИО студента"] == temp_row), "Команда"])), -1] + [""]*(len(results.columns)-4)
                    results.index = results.index + 1 
                # нахождение отметки о контрольной работе
                if ("Контрольная " in row["Название встречи"] or "Контрольная работа" == row["Предмет контроля"]):
                    meeting_name = f"Контрольная работа {test_number}"
                    # добавление колонок для КР, если их не было
                    if (f"Контрольная работа {test_number}" not in list(results.columns)):
                        if (f"Посещение до {meeting_name}" not in list(results.columns)):
                            results[f"Посещение до {meeting_name}"] = 0.0
                            results[f"Баллы до {meeting_name}"] = 0.0
                            results[f"Количество баллов до {meeting_name}"] = 0.0
                            results[f"Корень дисперсии баллов до {meeting_name}"] = 0.0
                            results[f"Доставленные баллы на {meeting_name}"] = -1
                            results[meeting_name] = 0
                            results[f"Присутствие на {meeting_name}"] = 0.0
                    # если найдены баллы контрольной
                    if (row["Предмет контроля"] == name_column_test):

                        test_score = float(row["Оценка за предметы контроля"]) if row["Оценка за предметы контроля"]!="" else 0
                        results.loc[((results['ФИО'] == temp_row)), f"Контрольная работа {test_number}"] = test_score

                        # определение посещамесоти КР и дополнительных баллов
                        if "Контрольная работа" == row["Предмет контроля"]:
                            if  group.loc[index + 1, "Название встречи"] != row["Название встречи"]:
                                if group.loc[index - 1, "Предмет контроля"] == "Посещение":
                                    ind_presence = index - 1
                                    ind_score = index - 2
                                else:
                                    ind_presence = index - 2
                                    ind_score = index - 1
                            elif group.loc[index + 2, "Название встречи"] != row["Название встречи"]:
                                skip = 1
                                if group.loc[index + 1, "Предмет контроля"] == "Посещение":
                                    ind_presence = index + 1
                                    ind_score = index - 1
                                else:
                                    ind_presence = index - 1
                                    ind_score = index + 1
                            else:
                                skip = 2
                                if group.loc[index + 2, "Предмет контроля"] == "Посещение":
                                    ind_presence = index + 2
                                    ind_score = index + 1
                                else:
                                    ind_presence = index + 1
                                    ind_score = index + 2
                        else:
                            if group.loc[index + 1, "Название встречи"] != row["Название встречи"]:
                                ind_presence, ind_score = index - 1, -1
                            else:
                                skip = 1
                                ind_presence, ind_score = index + 1, -1

                        test_presence, addit_score = GetDataTest(group, ind_presence, ind_score)
                        if ind_presence < index:
                            count_presence -= 1
                            summ_presence -= test_presence
                        if ind_score < index:
                            if addit_score>0:
                                summ_goals_btest -= addit_score
                                count_goals -= 1
                                goals_list.pop()
                        if count_presence == 0:
                            continue
                        # запись посчитанных данных
                        results.loc[((results['ФИО'] == temp_row)), f"Посещение до {meeting_name}"] = round(summ_presence / float(count_presence), 2)
                        results.loc[((results['ФИО'] == temp_row)), f"Баллы до {meeting_name}"] = summ_goals_btest
                        results.loc[((results['ФИО'] == temp_row)), f"Количество баллов до {meeting_name}"] = count_goals
                        results.loc[((results['ФИО'] == temp_row)), f"Корень дисперсии баллов до {meeting_name}"] = sqrt(np.var(goals_list))
                        results.loc[((results['ФИО'] == temp_row)), f"Доставленные баллы на {meeting_name}"] = addit_score
                        results.loc[((results['ФИО'] == temp_row)), f"Присутствие на {meeting_name}"] = test_presence
                        # вычитание доп баллов
                        if addit_score>0:
                            results.loc[((results['ФИО'] == temp_row)), "Баллы"] -= addit_score
                        # обнуление счетчиков
                        count_presence = summ_presence = summ_goals_btest = count_goals = count_meetings = 0
                        goals_list = []
                        test_number+=1
                # подсчет баллов
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
                    # подсчет посещаемости
                    count_presence += 1
                    if row["Оценка за предметы контроля"]=="П":
                        summ_presence += 1
            # заполнение пропусков и удаление ложной контрольной
            results = results.fillna(0)
            results = results.replace("", 0)
            results = results.loc[:, (results != 0).any(axis=0)]
            results = results.replace(-1, 0)
            results.loc[results["Баллы"]<61.0, 'Не сдал(-а)'] = 1
            results.drop(["Баллы"], axis= 1, inplace=True)
            results = results[results.columns[:len(results.columns)-(len(results.columns)-3)%7]]
            return results
        except Exception as e:
            print(e)

# конвертация данных в формате от Modeus (one_row - отметка о необходимости считывания одной итоговой строки)
def _ConvertModeusType(sheet, one_row = False):
    # удаление верхней строки с названием встреч
    sheet.columns = sheet.loc[0, :].values.flatten().tolist()
    sheet.drop(index=[0], inplace=True)
    sheet = sheet.reset_index(drop=True)
    # создание DataFrame и обнуление счетчиков
    results = pd.DataFrame(columns=["Баллы", "ФИО", "Команда", "Не сдал(-а)"])
    count_presence = summ_presence = count_kontr = 0
    summ_goals_btest = count_goals = count_meetings = 0

    try:
        for index, row in sheet.iterrows ():
            # заполнение основной информации о студенте
            results.loc[-1] = [row["Итог текущ."], row["Обучающийся"], row["Учебные команды"], 0] + [""]*(len(results.columns)-4)
            results.index = results.index + 1
            # обнуление счетчиков
            count_presence = summ_presence = count_kontr = 0
            summ_goals_btest = count_goals = count_meetings = 0
            skip = 0
            goals_list = []
            for i in range(5, len(sheet.columns.to_list())):
                if skip>0:
                    skip-=1
                    continue
                
                if sheet.columns.to_list()[i]!="Контрольная работа":
                    # подсчет посещаемости
                    if sheet.columns[i]=="Присутствие":
                        count_presence+=1
                        if (row[i]=="П"):
                            summ_presence+=1
                    # подсчет баллов
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
                    # найдена КР
                    count_kontr+=1
                    meeting_name = f"Контрольная работа {count_kontr}"
                    # добавление колонок для КР, если их не было
                    if (f"Посещение до {meeting_name}" not in list(results.columns)):
                        results[f"Посещение до {meeting_name}"] = 0
                        results[f"Баллы до {meeting_name}"] = 0
                        results[f"Количество баллов до {meeting_name}"] = 0.0
                        results[f"Корень дисперсии баллов до {meeting_name}"] = 0.0
                        results[f"Доставленные баллы на {meeting_name}"] = 0.0
                        results[meeting_name] = 0
                        results[f"Присутствие на {meeting_name}"] = 0.0
                    # определение присутствия на КР
                    count_presence -= 1
                    if (row[i-1]=="П"):
                        summ_presence-=1
                        results.loc[results.index[-1], f"Присутствие на {meeting_name}"] = 1
                    else:
                        results.loc[results.index[-1], f"Присутствие на {meeting_name}"] = 0
                    # запись посчитанных данных
                    results.loc[results.index[-1], f"Посещение до {meeting_name}"] = round(summ_presence / float(count_presence), 2)
                    results.loc[results.index[-1], f"Баллы до {meeting_name}"] = summ_goals_btest
                    results.loc[results.index[-1], f"Количество баллов до {meeting_name}"] = count_goals
                    results.loc[results.index[-1], f"Корень дисперсии баллов до {meeting_name}"] = sqrt(np.var(goals_list))

                    test_score = float(row[i]) if row[i]!="" else 0
                    results.loc[results.index[-1], meeting_name]  = test_score
                    # определение доставленных баллов
                    if sheet.columns[i+1]=="Работа на учебной встрече":
                        if not pd.isna(row[i+1]):
                            results.loc[results.index[-1],f"Доставленные баллы на {meeting_name}"] = (float(row[i+1]) if "." in str(row[i]) else float(str(row[i+1]).replace(",", ".")))
                            results.loc[results.index[-1], "Баллы"] -= results.loc[results.index[-1],f"Доставленные баллы на {meeting_name}"]
                            skip = 1
                    # обнуление счетчиков
                    count_presence = summ_presence = summ_goals_btest = count_goals = 0
            if one_row:
                break
        # заполнение пропусков
        results = results.fillna(0)
        results.loc[results["Баллы"]<61.0, 'Не сдал(-а)'] = 1
        results.drop(["Баллы"], axis= 1, inplace=True)
        return results
    except Exception as e:
        print(e)

# запрос на конвертирование
def Convert(file, one_row = False):
    xls_array = pd.read_excel(file)
    # определение типпа данных для выбора алгоритма
    if "Название РМУП" in xls_array.columns:
        return _ConvertEveryRow(xls_array, one_row)
    else:
        return _ConvertModeusType(xls_array, one_row)
    