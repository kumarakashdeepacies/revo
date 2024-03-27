/* On clicking upload button, we can access the table name by checking whichever tab is active
for example if its a list view tab, there will be a table associated with it.
Even if there is another tab which has a upload button, we will check which tab is active.
So accordingly in the upload modal, when the uploaded file is submitted or when the download format
button is clicked, we can get the table name by checking which tab is active.
Precommit.
*/
/* global popup:true,FormData:true */

function masterUploadFunc (elementTableIdList) { // eslint-disable-line no-unused-vars
  for (const i in elementTableIdList) {
    const elementIdUpload = elementTableIdList[i]
    $(`#uploadButton2${elementIdUpload}`).off("click").on('click', funcUpload2)
    $(`#uploadButtonBU${elementIdUpload}`).off("click").on('click', funcUploadBU)
    $(`#uploadButton${elementIdUpload}`).off("click").on('click', funcUpload)

    $(`#downloadButton${elementIdUpload}`).off("click").on('click', funcDownload)
  }

  function funcDownload () { // eslint-disable-line no-unused-vars
    const elementTabID = $(this).attr('data-elementID')
    const dataForm = new FormData($(`form[data-form-id=uploadfileform${elementTabID}]`)[0])
    let prCodeU = $(`form[data-form-id=uploadfileform${elementTabID}]`).attr("pr_code")
    dataForm.append('listOrDelete', 'downloadFormat')
    dataForm.append('modelName', $("#downloadButton"+elementTabID).attr('data-modelName'))
    let view_name = ""
    temp_type = $(`#${elementTabID}_tab_content`).attr("data-template-type")
    if(temp_type == 'Multi Dropdown View'){
      view_name = $(`#tableTab${elementTabID}`).find("select").val()
    }
    dataForm.append('view_name',view_name)
    $.ajax({
      url: "/users/"+urlPath+"/"+prCodeU+"/",
      data: dataForm,
      contentType: false,
      cache: false,
      async: false,
      processData: false,
      type: 'POST',
      dataType: 'json',
      success: function (data) {

      },
      error: function(err){

      }
    })
  }

  function funcUpload () { // eslint-disable-line no-unused-vars
    const elementTabID = $(this).attr('data-elementID')
    $(`#popup${elementTabID}`).modal('show')
    $(`#uploadFile${elementTabID}`).on("change", function(){{
      if ($(`#uploadFile${elementTabID}`)[0].files[0] !== undefined) {
        $(`#uploadButton2${elementTabID}`).prop('disabled', false)
        $(".columnMapperButton").prop('disabled', false)
      }
    }})

  }
  /*
    Changes to be made in this function: Check which tab is active and extract the respective table name
    */
  function funcUpload2 () { // eslint-disable-line no-unused-vars
    const elementTabID = $(this).attr('data-elementID')
    $(`#popup${elementTabID}`).modal('hide')
    $(`#validations_in_progress${elementTabID}`).addClass('show');

    setTimeout(() => {
      if($(`#validations_in_progress${elementTabID}`).hasClass('show')){
        $('body').css('pointer-events', 'none')
        const dataForm = new FormData($(`form[data-form-id=uploadfileform${elementTabID}]`)[0])
        let prCodeU = $(`form[data-form-id=uploadfileform${elementTabID}]`).attr("pr_code")
        dataForm.append('listOrDelete', 'U')
        let view_name = ""
        temp_type = $(`#${elementTabID}_tab_content`).attr("data-template-type")
        if(temp_type == 'Multi Dropdown View'){
          view_name = $(`#tableTab${elementTabID}`).find("select").val()
        }
        dataForm.append('view_name',view_name)
        let errorIndicator = 0
        if (errorIndicator === 0) {
          $.ajax({
            url: "/users/"+urlPath+"/"+prCodeU+"/",
            data: dataForm,
            contentType: false,
            cache: false,
            async: false,
            processData: false,
            type: 'POST',
            dataType: 'json',
            success: function (data) {
              if (Object.prototype.hasOwnProperty.call(data, 'job_id')) {

                if (data.job_id !== "not_queued"){
                  $('body').css('pointer-events', 'auto');
                  $(`#validations_in_progress${elementTabID}`).removeClass('show')
                  Swal.fire({ icon: 'success', text: 'Validations successful! Uploading in progress...\n You may continue with other tasks. You`ll be notified via the notification bell on successful upload.' });

                  let jobId = data.job_id;
                  let websocketUrlPrefix = 'ws://';
                  if (windowLocationAttr.protocol === 'https:') {
                      websocketUrlPrefix = 'wss://';
                  }
                  let jobConnection = new WebSocket(
                      websocketUrlPrefix + windowLocationAttr.host +
                      `/ws/queued_upload_output/${jobId}/`);

                  jobConnection.onmessage = function(event){

                    let data1 = JSON.parse(event.data);

                    if (data1.message === "done"){
                      windowLocationAttr.reload();
                    }
                  }
                }else{
                  windowLocationAttr.reload()
                }
              }else{
                windowLocationAttr.reload()
              }
            },
            error () {}
          })
        }
      }
    }, 1000);
  }


  function funcUploadBU () { // eslint-disable-line no-unused-vars
    const elementTabID = $(this).attr('data-elementid')
    const dataForm = new FormData($(`form[data-form-id=uploadfileform123${elementTabID}]`)[0])
    let prCodeU = $(`form[data-form-id=uploadfileform123${elementTabID}]`).attr("pr_code")
    dataForm.append('listOrDelete', 'BU')
    let identifier_cols = JSON.stringify($(`#bulkupdate_iden_${elementTabID}`).val())
    dataForm.append('identifier_cols', identifier_cols)
    let update_cols = JSON.stringify($(`#bulkupdate_cols_${elementTabID}`).val())
    dataForm.append('update_cols', update_cols)
    let view_name = ""
    temp_type = $(`#${elementTabID}_tab_content`).attr("data-template-type")
    if(temp_type == 'Multi Dropdown View'){
      view_name = $(`#tableTab${elementTabID}`).find("select").val()
    }
    dataForm.append('view_name',view_name)
    let errorIndicator = 0

    $.ajax({
      url: `/users/${urlPath}/DataManagement/`,
      data: {
        'element_id': elementTabID.split("__tab__")[0],
        'operation': "fetch_list_view_msgs",
        'messages' : JSON.stringify(["choose_file_bulk_update_message","choose_identifiers_bulk_update_message","select_columns_bulk_update_message"]),
        'view_name' :view_name
      },
      type: "POST",
      dataType: "json",
      success: function (data) {
        if ($(`#uploadFileBulkUpdate${elementTabID}`)[0].files[0] === undefined) {

          message=""
          icon=""
          if(data.choose_file_bulk_update_message){
            message = data.choose_file_bulk_update_message.message
            icon = data.choose_file_bulk_update_message.icon
          }

          iconHtml = ""
          if (icon){
            iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
          }

          Swal.fire({icon: 'warning',iconHtml, text: message ||"Please choose a file to upload." });
          errorIndicator += 1
        }

        if($(`#bulkupdate_iden_${elementTabID}`).val().length == 0){
          message=""
          icon=""
          if(data.choose_identifiers_bulk_update_message){
            message = data.choose_identifiers_bulk_update_message.message
            icon = data.choose_identifiers_bulk_update_message.icon
          }

          iconHtml = ""
          if (icon){
            iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
          }

          Swal.fire({icon: 'warning',iconHtml, text: message ||"Please select identifier columns." });
          errorIndicator += 1
        }

        if($(`#bulkupdate_cols_${elementTabID}`).val().length == 0){
          message=""
          icon=""
          if(data.select_columns_bulk_update_message){
            message = data.select_columns_bulk_update_message.message
            icon = data.select_columns_bulk_update_message.icon
          }

          iconHtml = ""
          if (icon){
            iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
          }

          Swal.fire({icon: 'warning',iconHtml, text: message ||"Please select columns to update" });
          errorIndicator += 1
        }

        if (errorIndicator === 0) {
          $.ajax({
            url: "/users/"+urlPath+"/"+prCodeU+"/",
            data: dataForm,
            contentType: false,
            cache: false,
            async: false,
            processData: false,
            type: 'POST',
            dataType: 'json',
            success: function (data) {

              if(data.error == "custom"){
                iconHtml = `<i class="${data.output_icon}" style="border: 0 !important;"></i>`
                Swal.fire({icon: 'success',iconHtml,text: data.output_msg,confirmButtonText: 'OK',
                  denyButtonText:'No',}).then((result) => {
                  if (result.isConfirmed) {
                    windowLocationAttr.reload();
                  };
                });
              }else{
                if(data.error == "yes"){
                  icon_swal = "error"
                  text_msg = data.output_msg
                }else{
                  icon_swal = "success"
                  text_msg = data.output_msg
                }
                Swal.fire({
                  icon: icon_swal,
                  title: text_msg,
                  showDenyButton: false,
                  showCancelButton: false,
                  confirmButtonText: 'OK',
                  denyButtonText:'No',
                }).then((result) => {
                  if (result.isConfirmed && icon_swal=="success") {
                    windowLocationAttr.reload();
                  };
                });
              }

            },
            error () {}
          })
          $(`#bulkupdate_data_modal_${elementTabID}`).modal('hide')
        }
      },
      error: function () {
       Swal.fire({icon: 'error',text: 'Error! Please try again.'});
      }
    });

  }

  window.onclick = function (event) {
    if (event.target.id === 'popup') {
      popup.style.display = 'none'
    }
  }
  window.onkeyup = function (event) {
    if (event.keyCode === 27) {
      popup.style.display = 'none'
    }
  }
}
