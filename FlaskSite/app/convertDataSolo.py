import re
import pandas as pd

required_params = {"ScoresText": {"text": "Баллы до", "regular": r"[^\d., |]", "input": None, "split_string": ", "},\
     "PresText": {"text": "Посещаемость до", "regular": r"[^НП|]", "input": None, "split_string": ""},\
     "AdditionText": {"text": "Доставленные баллы", "regular": r"[^\d,. |]", "input": None, "split_string": ", "},\
     "TestScoreText": {"text": "Баллы контрольных", "regular": r"[^\d,.|]", "input": None, "split_string": ""}}
# конвертация текстовых данных от студента в формат DataFrame по шаблону
def ConvertDataSolo(request, test_number):
    global required_params
    # список ошибочных полей
    error_inputs = set()
    temp = None
    if all(param in request.form for param in required_params.keys()):
        for param in required_params.keys():
            temp = request.form.get(param)
            if re.search(required_params[param]["regular"], temp) != None:
                error_inputs.add(required_params[param]["text"])
            else:
                required_params[param]["input"] = temp.split("|")
                if len(required_params[param]["input"]) != test_number:
                    error_inputs.add(required_params[param]["text"])
                else:
                    if required_params[param]["split_string"]!="":
                        required_params[param]["input"] = \
                            [text.split(required_params[param]["split_string"]) \
                            for text in  required_params[param]["input"]]
                    else:
                        required_params[param]["input"] = \
                            [list(text) \
                            for text in  required_params[param]["input"]]
                    print(param, required_params[param]["input"])
    else:
        error_inputs.add("Не все данные получены")
    if len(error_inputs) > 0:
        return "Неккоректная запись:\n" + ", ".join(error_inputs)
    
    if not all(len(required_params[param]["input"][i])==len(required_params["ScoresText"]["input"][i]) for i in range(len(required_params[param]["input"])) for param in required_params.keys()):
        return "Данные не совпадают по длине"
    
    results = pd.DataFrame()
    results.append([])
    for i in range(test_number):
        meeting_name = f"Контрольная работа {i}"
        results[f"Посещение до {meeting_name}"] = 0.0
        results[f"Баллы до {meeting_name}"] = 0.0
        results[f"Количество баллов до {meeting_name}"] = 0.0
        results[f"Корень дисперсии баллов до {meeting_name}"] = 0.0
        results[f"Доставленные баллы на {meeting_name}"] = -1
        results[meeting_name] = 0
        results[f"Присутствие на {meeting_name}"] = 0.0


    

    
