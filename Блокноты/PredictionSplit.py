def SplitTestTrainTest(data, exam, not_for_prediction, test_data = False):
    if test_data:
        return data[data.loc[data[f"Присутствие на {exam}"] == 1,:exam].columns.difference(not_for_prediction+[exam, "Не сдал(-а)"])], data[exam]
    else:
        return data[data.loc[:,:exam].columns.difference(not_for_prediction+[exam, "Не сдал(-а)"])], data[exam]


def SplitTestTrainPass(data, exam, not_for_prediction):
    return data[data.loc[:,:exam].columns.difference(["Не сдал(-а)"]+not_for_prediction)], data["Не сдал(-а)"]
