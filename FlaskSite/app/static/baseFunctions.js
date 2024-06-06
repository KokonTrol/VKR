let uuid = "";
let componentsToDisable = []
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

function ChangeDisabled(is_disabled){
    $.each(componentsToDisable, function(index, value){
        $(value).prop("disabled", is_disabled);
    });
}
$(document).ready(function (e){
    uuid = $('#uuid').text();
})