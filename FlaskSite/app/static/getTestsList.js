// заполнение названий контрольных
function MakeOptionToSelectTest(value){
    var obj = `<option value="${value}">${value}</option>`;
    return obj;
}
function SetTests(){
    $('#selectTest').empty();
    $.each(responseData, function(index, value){
        $('#selectTest').append(MakeOptionToSelectTest(value));
    });
}
$(document).ready(function (e){
    componentsToDisable = ["#examPredictionButton", "#testPredictionButton", "#formAdditionText", "#formPresText", "#formScoresText", "#selectTest"]
    // действие по смене предмета 
    $('#selectSubject').on('change', async function (e) {
        var form_data = new FormData();
        if ($('#formFileInput').length>0){
            var fileCount = $('#formFileInput').prop('files').length;
            if (fileCount!=1){
                alert('Необходимо выбрать 1 файл формата XLS(XLSX)');
                return;
            }
        }
        ChangeDisabled(true);
        form_data.append("selectedSubject", $('select[name="selectSubject"]').val());
        if ($('#formFileInput').length>0){
            form_data.append("formFile", $('#formFileInput').prop('files')[0]);
        }
        else{
            form_data.append("formFile", null);
        }
        await GetResult("/api/get_tests", form_data);
        if (responseData != null){
            SetTests();
            responseData = null;
        }
        ChangeDisabled(false);
    });
});