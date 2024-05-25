let uuid = "";

function MakeRowResultExam(valueFio, valueRes){
    var obj = `<tr ${valueRes >= 0.5 ? 'class="table-danger"' : ''}>
        <td>${valueFio}</td>
        <td>${(valueRes*100).toFixed(2)}%</td>
        </tr>`;
    return obj;
}

function MakeRowResultTest(valueFio, valueRes){
    var obj = `<tr ${valueRes == 0.0 ? 'class="table-danger"' : ''}>
        <td>${valueFio}</td>
        <td>${valueRes}</td>
        </tr>`;
    return obj;
}
let responseData;
async function GetResult(url, formdata){
    await $.ajax({
        url: url,
        type: 'POST',
        dataType: 'json',
        cache: false, 
        contentType: false,
        processData: false,
        data: formdata,
        success: function(response){
            responseData =  response;
        },
        error: function(response){
            responseData =  response;
        },
    });
    console.log(responseData);
}

function CollectDataToSend(){
    var form_data = new FormData();
    var fileCount = $('#formFileInput').prop('files').length;
    if (fileCount!=1){
        alert('Необходимо выбрать 1 файл формата XLS(XLSX)');
        return null;
    }
    else {
        form_data.append("selectedSubject", $('select[name="selectSubject"]').val());
        form_data.append("selectedTest", $('select[name="selectTest"]').val());
        form_data.append("formFile", $('#formFileInput').prop('files')[0]);
        form_data.append("uuid", uuid);
        return form_data;
    }
}

$(document).ready(function (e){
    uuid = $('#uuid').text();
    console.log(uuid);
    $('#examPredictionButton').on('click', async function() {
        var data = CollectDataToSend();
        if (data != null) {
            await GetResult("/api/get_exam_prediction", data);
            if (responseData != null){
                $('#tableResultBody').empty();
                $.each(responseData, function(index, value){
                    $('#tableResultBody').append(MakeRowResultExam(value.name, value.result));
                });
                console.log(responseData);
                responseData = null;
            }
        }
    });

    $('#testPredictionButton').on('click', async function() {
        var data = CollectDataToSend();
        console.log(data);
        if (data != null) {
            await GetResult("/api/get_test_prediction", data);
            console.log(responseData);
            if (responseData != null){
                $('#tableResultBody').empty();
                $.each(responseData, function(index, value){
                    $('#tableResultBody').append(MakeRowResultTest(value.name, value.result));
                });
                responseData = null;
            }
        }
    });
});