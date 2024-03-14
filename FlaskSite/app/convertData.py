import pandas as pd

def GetTestName(file):
    pass

def GetInfoLose(goal):
    return 1 if float(goal)>=61 else 0

def _ConvertEveryRow(sheet):
    temp_row = ""
    for name, group in sheet.groupby(["Название РМУП"]):
        results = pd.DataFrame(columns=["ФИО", "Команда", "Баллы", "Сдал(-а)"])

        name_discipline = group.head(1)["Название РМУП"].values[0]
        print(name_discipline, end=":")
        # try:
        if (group["Название встречи"].str.contains('Контрольная ').sum()==0):
            print(" Контрольных не найдено")
            continue
        percent = 0
        count_presence = 0
        summ_presence = 0
        count_goals = 0
        for index, row in group.iterrows ():
            
            if (index%(len(group)//10)==0):
                print(f"{percent}%. Записей в итоге: {len(results)}")
                percent+=10

            if temp_row == "" or temp_row != row["ФИО студента"]:
                count_presence = summ_presence = 0
                temp_row = row["ФИО студента"]
                results.loc[-1] = [temp_row, row["Команда"], row["Итог ТУ"], GetInfoLose(row["Итог ТУ"])] + [""]*(len(results.columns)-4)
                results.index = results.index + 1  # shifting index
            
            if ("Контрольная " in row["Название встречи"]):
                if (row["Название встречи"] not in list(results.columns)):
                    meeting_name = row["Название встречи"]
                    if (f"Посещение до {meeting_name}" not in list(results.columns)):
                        results[f"Посещение до {meeting_name}"] = 0
                        results[f"Баллы до {meeting_name}"] = 0
                    results[meeting_name] = 0
                    convert_dict = {f"Посещение до {meeting_name}": float,
                                    f"Баллы до {meeting_name}": float,
                                    meeting_name: float,
                                    "Баллы": float
                                }
                    results = results.astype(convert_dict)

                if (row["Предмет контроля"] != "Посещение"):
                    results.loc[((results['ФИО'] == temp_row)), row["Название встречи"]] = row["Оценка за предметы контроля"]
                else:
                    meeting_name = row["Название встречи"]
                    if count_presence == 0 or results.loc[((results['ФИО'] == temp_row)), f"Посещение до {meeting_name}"].values[0]!="":
                        continue
                    results.loc[((results['ФИО'] == temp_row)), f"Посещение до {meeting_name}"] = round(summ_presence / float(count_presence), 2)
                    results.loc[((results['ФИО'] == temp_row)), f"Баллы до {meeting_name}"] = count_goals

                    count_presence = summ_presence = count_goals = 0

            elif (row["Предмет контроля"] != "Посещение"):
                if not pd.isna(row["Оценка за предметы контроля"]):
                    t = row["Оценка за предметы контроля"]
                    count_goals += float(row["Оценка за предметы контроля"])
            else:
                count_presence += 1
                if row["Оценка за предметы контроля"]=="П":
                    summ_presence += 1
            
        results = results.fillna(0)
        return results
        # except Exception as e:
        #     print(e)   

def _ConvertOneRow(sheet):
    data_results_presence2 = pd.DataFrame(columns=["Команда", "Баллы", "Сдал(-а)"])
    sheet.columns = sheet.loc[0, :].values.flatten().tolist()
    sheet.drop(index=[0], inplace=True)
    sheet = sheet.reset_index(drop=True)
    try:
        for index, row in sheet.iterrows ():
            data_results_presence2.loc[-1] = [row["Направление подготовки"], row["Итог текущ."], GetInfoLose(row["Итог текущ."])] + [""]*(len(data_results_presence2.columns)-3)
            data_results_presence2.index = data_results_presence2.index + 1

            count_presence = summ_presence = count_kontr = 0

            count_kontr = 0
            for i in range(1, len(sheet.columns.to_list())):
                if sheet.columns.to_list()[i]!="Контрольная работа":
                    count_presence+=1
                    if (row[i]=="П"):
                        summ_presence+=1
                else:
                    count_kontr+=1
                    meeting_name = f"Контрольная работа {count_kontr}"
                    if (f"Посещение до {meeting_name}" not in list(data_results_presence2.columns)):
                        data_results_presence2[f"Посещение до {meeting_name}"] = 0
                        data_results_presence2[f"Баллы до {meeting_name}"] = 0
                        data_results_presence2[meeting_name] = 0
                        convert_dict = {f"Посещение до {meeting_name}": float,
                            f"Баллы до {meeting_name}": float,
                            meeting_name: float,
                            "Баллы": float
                            }
                        data_results_presence2 = data_results_presence2.astype(convert_dict)
                    if count_presence == 0:
                        count_presence = summ_presence = 0
                        continue
                    data_results_presence2.loc[data_results_presence2.index[-1], f"Посещение до {meeting_name}"] = round(summ_presence / float(count_presence), 2)
                    data_results_presence2.loc[data_results_presence2.index[-1], meeting_name]  = float(row[i])
                    data_results_presence2.loc[data_results_presence2.index[-1], f"Баллы до {meeting_name}"]  = 0

                    count_presence = summ_presence = 0
        data_results_presence2 = data_results_presence2.fillna(0)
    
    except Exception as e:
        print("Ошибка:", e)
    return data_results_presence2

def Convert(file):
    #парсинг страниц
    # xl = None
    # if file_name.endswith('.xlsx'):
    #     xl = pd.ExcelFile(
    #         file_name,
    #         engine='openpyxl'
    #     )
    # elif file_name.endswith('.xls'):
    #     xl = pd.ExcelFile(
    #         file_name,
    #         engine='xlrd'
    #     )
    # xls_array = [xl.parse(sheet) for sheet in xl.sheet_names]
    xls_array = pd.read_excel(file)
    if "Название встречи" in xls_array.columns:
        return _ConvertEveryRow(xls_array)
    else:
        return _ConvertOneRow(xls_array)
    #преобразование
    