let uuid = "";
var myChart = null;

function MakeRowResultExam(valueFio, valueGroup, valueRes){
    var obj = `<tr ${valueRes >= 50 ? 'class="table-danger"' : ''}>
        <td>${valueFio}</td>
        <td>${valueGroup}</td>
        <td>${valueRes}%</td>
        </tr>`;
    return obj;
}

function MakeRowResultTest(valueFio, valueGroup, valueRes){
    var obj = `<tr ${valueRes == 0.0 ? 'class="table-danger"' : ''}>
        <td>${valueFio}</td>
        <td>${valueGroup}</td>
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

function DrawChart(data){
    var groupedData = {};

    // Группируем данные по параметру param1
    for (var i = 0; i < data.length; i++) {
        var item = data[i];
        if (!groupedData[item.group]) {
            groupedData[item.group] = { sum: 0, count: 0 };
        }
        groupedData[item.group].sum += item.result;
        groupedData[item.group].count++;
    }
    $('#MeanResultTableBody').empty();

    // Выводим среднее значение другого параметра для каждого параметра
    for (var key in groupedData) {
        groupedData[key] = (groupedData[key].sum / groupedData[key].count).toFixed(2);
        var obj = `<tr>
        <td>${key}</td>
        <td>${groupedData[key]}</td>
        </tr>`;
        $('#MeanResultTableBody').append(obj);
    }
    $('#meanResults').empty();

    if(myChart){
        myChart.clear();
        myChart.destroy();
    }
    myChart = new Chart($('#meanResults'), {
        type: 'bar',
        data: {
            labels: Object.keys(groupedData),
          datasets: [{
            label: 'Средние показатели',
            data: Object.values(groupedData),
            borderWidth: 1
          }]
        },
        options: {
            indexAxis: 'y',
          scales: {
            // x: {
            //     ticks: {
            //         autoSkip: false,
            //         maxRotation: 90,
            //         minRotation: 90
            //     }
            // },
            y: {
              beginAtZero: true
            }
          }
        }
      });
}

$(document).ready(function (e){
    uuid = $('#uuid').text();
    $('#examPredictionButton').on('click', async function() {
        var data = CollectDataToSend();
        if (data != null) {
            await GetResult("/api/get_exam_prediction", data);
            if (responseData != null){
                $('#tableResultBody').empty();
                $.each(responseData, function(index, value){
                    $('#tableResultBody').append(MakeRowResultExam(value.name, value.group, value.result));
                });
                DrawChart(responseData);
                responseData = null;
            }
        }
    });

    $('#testPredictionButton').on('click', async function() {
        var data = CollectDataToSend();
        console.log(data);
        if (data != null) {
            await GetResult("/api/get_test_prediction", data);
            if (responseData != null){
                $('#tableResultBody').empty();
                $.each(responseData, function(index, value){
                    $('#tableResultBody').append(MakeRowResultTest(value.name, value.group, value.result));
                });
                DrawChart(responseData);
                responseData = null;
            }
        }
    });
});