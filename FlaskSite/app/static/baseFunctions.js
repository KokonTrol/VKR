// UUID со страницы пользователя
let uuid = "";
// id элементов, которые необходимо блокировать при отправке запроса
let componentsToDisable = []
// результаты запросов
let responseData;
// функция получения результатов
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
}
// смена состояний компонентов
function ChangeDisabled(is_disabled){
    $.each(componentsToDisable, function(index, value){
        $(value).prop("disabled", is_disabled);
    });
}
// считывание uuid
$(document).ready(function (e){
    uuid = $('#uuid').text();
})