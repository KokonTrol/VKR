function MakeOptionToSelectTest(value){
    var obj = `<option value="${value}">${value}</option>`;
    return obj;
}

$(document).ready(function (e){
    $('#selectSubject').on('change', function (e) {
        var form_data = new FormData();
            var fileCount = $('#formFileInput').prop('files').length;
            if (fileCount!=1){
                alert('Необходимо выбрать 1 файл формата XLS(XLSX)');
                return;
            }
            else {
                form_data.append("selectedSubject", $('select[name="selectSubject"]').val());
    
                form_data.append("formFile", $('#formFileInput').prop('files')[0]);
                $.ajax({
                    url: "/api/get_tests",
                    type: 'POST',
                    dataType: 'json',
                    cache: false, 
                    contentType: false,
                    processData: false,
                    data: form_data,
                    success: function(response){
                        $('#selectTest').empty();
                        $.each(response, function(index, value){
                            $('#selectTest').append(MakeOptionToSelectTest(value));
                        });
                    },
                    error: function(response){
                        alert(response.message);
                    },
                    
                });
            }
    });
    // $('#getTestName').on('click', function() {
    //     var form_data = new FormData();
    //     var fileCount = $('#formFileInput').prop('files').length;
    //     if (fileCount!=1){
    //         alert('Необходимо выбрать 1 файл формата XLS(XLSX)');
    //         return;
    //     }
    //     else {
    //         form_data.append("selectedSubject", $('select[name="selectSubject"]').val());

    //         form_data.append("formFile", $('#formFileInput').prop('files')[0]);
    //         $.ajax({
    //             url: "/api/get_tests",
    //             type: 'POST',
    //             dataType: 'json',
    //             cache: false, 
    //             contentType: false,
    //             processData: false,
    //             data: form_data,
    //             success: function(response){
    //                 $('#selectTest').empty();
    //                 $.each(response, function(index, value){
    //                     $('#selectTest').append(MakeOptionToSelectTest(value));
    //                 });
    //             },
    //             error: function(response){
    //                 alert(response.message);
    //             },
                
    //         });
    //     }
    // });
});