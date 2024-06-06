function CollectDataToSend(){
    var form_data = new FormData();
    var fileCount = $('#formFileInput').prop('files').length;
    if (fileCount!=1){
        alert('Необходимо выбрать 1 файл формата XLS(XLSX)');
        return null;
    }
    else {
        form_data.append("selectedSubject", $('select[name="selectSubject"]').val());
        form_data.append("subjectInput", $('input[name="formSubjectInput"]').val());
        form_data.append("formFile", $('#formFileInput').prop('files')[0]);
        form_data.append("uuid", uuid);
        return form_data;
    }
}
$(document).ready(function (e){
    $("#deleteSubject").prop("disabled", true);
    componentsToDisable = ["#selectSubject", "#formSubjectInput", "#formFileInput", "#deleteSubject", "#addEducationdata"]
    $('#addEducationdata').on('click', async function() {
        ChangeDisabled(true);
        var data = CollectDataToSend();
        if (data != null) {
            await GetResult("/admin_panel", data);
            alert(responseData.message);
        }
        ChangeDisabled(false);
    });
    $('#deleteSubject').on('click', async function() {
        ChangeDisabled(true);
        var form_data = new FormData();
        form_data.append("selectedSubject", $('select[name="selectSubject"]').val());
        await GetResult("/admin_panel_delete", form_data);
        alert(responseData.message);

        ChangeDisabled(false);
    });

    $('#selectSubject').on('change', function (e) {
        if ($('select[name="selectSubject"]').val() == "Не выбрано")
        {
            $("#formSubjectInput").prop("disabled", false);
            $("#deleteSubject").prop("disabled", true);
        }
        else{
            $("#formSubjectInput").prop("disabled", true);
            $("#deleteSubject").prop("disabled", false);
        }
    });
});