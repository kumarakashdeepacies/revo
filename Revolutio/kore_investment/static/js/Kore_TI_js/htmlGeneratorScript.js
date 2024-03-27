
/* global  FormData,eqBuilder,Option,ctoken:true,CKEDITOR, datatables,Treant,initialiseTableResults */
ctoken = $('form').find('input[name=\'csrfmiddlewaretoken\']').attr('value')
$.ajaxSetup({
  beforeSend: function (xhr, settings) {
    xhr.setRequestHeader('X-CSRFToken', ctoken)
  }
})


function showTool () { // eslint-disable-line no-unused-vars
  $(this).find('.row').css('display', 'flex')
}
function hideTool () { // eslint-disable-line no-unused-vars
  $(this).find('.row').css('display', 'none')
}

function viewCompScenario () { // eslint-disable-line no-unused-vars
  const modelElementID = $(this).attr('data-element_id')
  const modelName = $(`#modelName_${modelElementID}`).attr('data-model_name')
  let scenarioID
  let replaceIdentifierList
  let replaceColumnList
  $('#run_saved_scenario').attr('data-element_id', modelElementID)
  $('#save_edited_scenario').attr('data-element_id', modelElementID)

  $.ajax({
    url: `/users/${urlPath}/computationModule/`,
    data: {
      s_id: $(this).attr('data-scenario_id'),
      operation: 'fetch_saved_scenarios_view'
    },
    type: 'POST',
    dataType: 'json',
    success: function (data) {
      $('#element_incremental_data_').empty()
      $('#viewCompScenario').find('input').val('').trigger('change')
      if (Object.keys(data.scenarios).length > 0) {
        for (const scn of data.scenarios) {
          $('#scenario_name_').val(scn.scenario_name).trigger('change')
          $('#scenario_configuration_date_').val(scn.configuration_date).trigger('change')
          $('#run_saved_scenario').attr('data-scenario_id', scn.scenario_id)
          $('#run_saved_scenario').attr('data-scenario_config', scn.scenario_config)
          $('#save_edited_scenario').attr('data-scenario_id', scn.scenario_id)
          scenarioID = scn.scenario_id
          $('#save_edited_scenario').attr('data-scenario_config', scn.scenario_config)
          if (String(scn.run_with_base_model) === 'false') {
            $('#runWithBaseModel_').prop('checked', false)
          } else {
            $('#runWithBaseModel_').prop('checked', true)
          }
          const config = JSON.parse(scn.scenario_config)
          for (let i = 0; i < config.length; i++) {
            if ('replace_identifier_list' in config[i]) {
              replaceIdentifierList = config[i].replace_identifier_list
              replaceColumnList = config[i].replace_column_list
            } else {
              replaceIdentifierList = []
              replaceColumnList = []
            }
            $('#element_incremental_data_').append(
                    `<tr>
                      <td style="text-align: center;" data-scenario_type="${config[i].scenario_type}" data-scenario_type_scenarioData="${config[i].scenario_type_scenarioData}" data-scenario_data_type="${config[i].scenario_data_type}" data-element_component_id="${config[i].element_id}" data-equation_editor_model="${config[i].equation_editor_model}" data-replace_identifier_list=${JSON.stringify(replaceIdentifierList)} data-replace_column_list=${JSON.stringify(replaceColumnList)}>${config[i].element_name}</td>
                      <td style="text-align: center;" >${config[i].scenario_type}</td>
                      <td style="text-align: center;">${config[i].scenario_type_scenarioData}</td>
                      <td style="text-align: center;" ><i class="fas fa-edit"" onclick="editCompScenario.call(this)" style="color:var(--primary-color);" data-element_name= "${config[i].element_name}" data-scenario_id="${scn.scenario_id}" data-element_id="${modelElementID}" data-title="Edit element"></i>&nbsp;<i class="fas fa-trash"" onclick="deleteScenarioElement.call(this)" style="color:var(--primary-color);" data-element_name= "${config[i].element_name}" data-scenario_id="${scn.scenario_id}" data-element_id="${modelElementID}" data-title="Delete element"></i></td>
                    </tr>`
            )
          }
        }

        $.ajax({
          url: `/users/${urlPath}/computationModule/`,
          data: {
            model: modelName,
            type: 'saved_scenario',
            operation: 'computation_scenario_tree'
          },
          type: 'POST',
          dataType: 'json',
          success: function (data) {
            $('.EBDisplayButtonIDDiv').empty()
            $('#viewCompScenario').modal('show')
            const chartConfig2 = {
              chart: {
                container: '#model_inputs_scenario_',
                levelSeparation: 100,
                siblingSeparation: 200,
                subTeeSeparation: 100,
                nodeAlign: 'CENTER',
                connectors: {
                  type: 'step'
                },
                node: {
                  HTMLclass: 'nodeExample1'
                }
              },
              nodeStructure: data.nodes
            }
            const chart2 = new Treant(chartConfig2) // eslint-disable-line no-unused-vars
            $('.nodeExample1').css('background', 'black')
            $('.nodeExample1').css('color', 'white')
            $('.nodeExample1').css('border-radius', '0.5rem')
            $('.data_model_input_saved_scenario').hover(
              function () {
                $(this).addClass('shadow').css('cursor', 'pointer')
              }, function () {
                $(this).removeClass('shadow')
              }
            )
            $('.csv_input').css('background', 'grey')
            $('.node-title').css('margin', '1rem')
            $('.node-name').css('margin', '1rem')
            $('.model_names').css('background', 'var(--primary-color)')
            $('#viewCompScenario').modal('show')
            const scenarioName = $('#scenario_name_').val()
            if (String(scenarioName) !== '') {
              $('.data_model_input_saved_scenario').click(function () {
                $('.existingDataHeader').text('Existing Data')
                const elementIdentifier = $(this).attr('data-element_id')
                const elementNameComponent = $(this).attr('data-element_name')

                $.ajax({
                  url: `/users/${urlPath}/computationModule/`,
                  data: {
                    model: $(this).attr('data-model_name'),
                    element_id: elementIdentifier,
                    operation: 'computation_element_data'
                  },
                  type: 'POST',
                  dataType: 'json',
                  success: function (data) {
                    $(`#viewScenarioData_${modelElementID}`).empty()
                    $(`#viewScenarioData_${modelElementID}`).append(
                                `<div class="card shadow-sm  bg-white rounded;">
                                  <div class="card-body" style="padding:0.9rem;max-height:90">
                                      <table id="exampledataResultsScenario_${modelElementID}" class="display compact" style="width:100%;">
                                          <thead>
                                              <tr></tr>
                                          </thead>
                                          <tbody>
                                          </tbody>
                                      </table>
                                  </div>
                                </div>
                                <div class="card shadow-sm  bg-white rounded;">
                                <form id="incremental_data_${modelElementID}">
                                  <div class="card-header" style="color:var(--primary-color);">
                                    <h5 class="mb-0" style="text-align:center;">
                                      Configure Scenario Data
                                    </h5>
                                  </div>
                                  <div class="card-body" style="padding:0.9rem;">
                                    <div class="row">
                                      <div class="form-group col-4">
                                          <label for="selectScenarioDataType_${modelElementID}">Select scenario data type:</label>
                                          <select id="selectScenarioDataType_${modelElementID}" class="select2 form-control" name="selectScenarioDataType_${modelElementID}">
                                            <option value="upload_data">Upload data</option>
                                            <option value="equation_builder">Create with equation builder</option>
                                          </select>
                                        </div>
                                      </div>
                                    </div>
                                    <div class="row">
                                      <div class="form-group col-4" id="uploadData_${modelElementID}">
                                        <div class="custom-file" style="margin-left: 0.5rem;">
                                          <input type="file" class="custom-file-input"  accept=".csv" name="customFile">
                                          <label class="custom-file-label" for="customFile">Choose file</label>
                                        </div>
                                        <br>
                                        <br>
                                      </div>
                                      <div class="form-group col-4 EBDisplayButtonIDDiv" id="equationBuilder_${modelElementID}" style="display:none">
                                        <button style="color:aliceblue; margin-left: 0.5rem;" type="button" id="EBDisplayButtonID" class="btn btn-primary btn-xs rounded">Equation builder</button>
                                      </div>
                                    </div>
                                    <div class="form-group col-4" style="display:flex">
                                      <label style="margin-left: 0.5rem;">Scenario type : </label>
                                      <div id="" class="custom-control custom-checkbox" style="margin-left:1%;">
                                        <input type="checkbox" name="defaultValueConfig" data-scenario_type="append" id="append${modelElementID}" class="checkboxinput custom-control-input" value="0">
                                        <label for="append${modelElementID}" class="custom-control-label">
                                          Append
                                        </label>
                                      </div>
                                      <div id="" class="custom-control custom-checkbox" style="margin-left:1%;">
                                        <input type="checkbox" name="defaultValueConfig" data-scenario_type="replace" id="replace${modelElementID}" class="checkboxinput custom-control-input" value="0">
                                        <label for="replace${modelElementID}" class="custom-control-label">
                                          Replace
                                        </label>
                                      </div>
                                    </div>
                                    <div class="form-group col-4" style="margin-left:0.4rem;display:None;">
                                      <label for="selectIdentifierColumns_${modelElementID}">Select identifier columns:</label>
                                      <select id="selectIdentifierColumns_${modelElementID}" class="select2 form-control" name="selectIdentifierColumns_${modelElementID}" multiple>
                                      </select>
                                    </div>
                                    <div class="form-group col-4" style="margin-left:0.4rem;display:None;">
                                      <label for="selectUpdateColumns_${modelElementID}">Select columns to update:</label>
                                      <select id="selectUpdateColumns_${modelElementID}" class="select2 form-control" name="selectUpdateColumns_${modelElementID}" multiple>
                                      </select>
                                    </div>
                                  </div>
                                  <div style="float:right;">
                                    <button type="button" id="addScenarioData_${modelElementID}" data-element_id = "${modelElementID}"  data-form_id = "incremental_data_${modelElementID}" data-element_id_component = "${elementIdentifier}" data-scenario_name = "${scenarioName}" data-element_name = "${elementNameComponent}" class="btn btn-primary btn-xs mx-1 my-1 rounded px-2">Add scenario &nbsp;<i class="fas fa-plus"></i></button>
                                    <button type="button" id="quitScenarioData_${modelElementID}" class="btn btn-primary btn-xs mx-2 rounded px-2" data-dismiss="modal">Close</button>
                                  </div>
                                </form>
                                </div>
                                `
                    )
                    $('select.select2:not(.modal select.select2)').each(function(){
                      parent = $(this).parent()
                      $(this).select2({dropdownParent:parent})
                    })
                    $('.modal select.select2').each(function(){
                      $(this).select2()
                    })
                    for (const i in data.columns_list) {
                      $(`#selectIdentifierColumns_${modelElementID}`).append(`<option value="${data.columns_list[i]}">${data.columns_list[i]}</option>`)
                      $(`#selectUpdateColumns_${modelElementID}`).append(`<option value="${data.columns_list[i]}">${data.columns_list[i]}</option>`)
                    }
                    $(`#selectIdentifierColumns_${modelElementID}`).off('select2:select select2:unselect').on('select2:select select2:unselect', function () {
                      $(`#selectUpdateColumns_${modelElementID}`).empty()
                      const selIdentifier = $(this).val()
                      for (const i in data.columns_list) {
                        if (selIdentifier.includes(data.columns_list[i]) === false) {
                          $(`#selectUpdateColumns_${modelElementID}`).append(new Option(data.columns_list[i], data.columns_list[i], false, false))
                        };
                      };
                    })
                    $(`#selectScenarioDataType_${modelElementID}`).select2()
                    $(`#selectScenarioDataType_${modelElementID}`).off('select2:select').on('select2:select', function () {
                      if (String($(this).val()) === 'upload_data') {
                        $(`#uploadData_${modelElementID}`).css('display', '')
                        $(`#equationBuilder_${modelElementID}`).css('display', 'none')
                      } else {
                        $(`#uploadData_${modelElementID}`).css('display', 'none')
                        $(`#equationBuilder_${modelElementID}`).css('display', '')
                      }
                    })
                    $('[type="checkbox"]').change(function () {
                      if (String($(this).attr('data-scenario_type')) === 'replace') {
                        $(`#selectIdentifierColumns_${modelElementID}`).parent().css('display', '')
                        $(`#selectUpdateColumns_${modelElementID}`).parent().css('display', '')
                      } else {
                        $(`#selectIdentifierColumns_${modelElementID}`).parent().css('display', 'none')
                        $(`#selectUpdateColumns_${modelElementID}`).parent().css('display', 'none')
                      }
                      if (this.checked) {
                        $('[type="checkbox"]').not(this).prop('checked', false)
                      }
                    })
                    $('#EBDisplayButtonID').attr('data-name', scenarioName + elementIdentifier)
                    eqBuilder(scenarioName, elementIdentifier, modelElementID)

                    $('.custom-file-input').on('change', function () {
                      const fileName = $(this).val().split('\\').pop()
                      $(this).siblings('.custom-file-label').addClass('selected').html(fileName)
                    })
                    for (let i = 0; i < data.table[data.table_headers[0]].length; i++) {
                      let string = '<tr>'
                      for (const j in data.table_headers) {
                        string += `<td style="text-align:center;">${data.table[data.table_headers[j]][i]}</td>`
                      }
                      string += '</tr>'
                      $(`#exampledataResultsScenario_${modelElementID}`).find('tbody').append(string)
                    }

                    $(`#exampledataResultsScenario_${modelElementID} thead tr`).empty()
                    for (const j in data.table_headers) {
                      $(`#exampledataResultsScenario_${modelElementID}`).find('thead tr').eq(0).append(`<th style="text-align:center;">${data.table_headers[j]}</th>`)
                    }
                    $(`#scenarioDataOutputModal_${modelElementID}`).modal('show')
                    initialise_table_results('exampledataResultsScenario', modelElementID)
                    $(`#addScenarioData_${modelElementID}`).attr('data-scenario_data_source', 'saved_scenario')
                    $(`#addScenarioData_${modelElementID}`).attr('data-scenario_id', scenarioID)
                    $(`#addScenarioData_${modelElementID}`).click(saveIncrementalData)
                  },
                  error: function () {
                    Swal.fire({icon: 'error',text: 'Error! Failure in fetching the Table Data. Please try again.'});
                  }
                })
              })
            }
          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Failure in loading the scenario configuration. Please try again.'});
          }
        })
      }
    },
    error: () => {
      Swal.fire({icon: 'error',text: 'Error! Failure in fetching the saved scenarios. Please try again.'});
    }
  })
}

/* eslint-disable */
    var filter_list = {}
      var cellIndex1
      var cellIndex2
      var cellIndex3
      var cellColLen3
      var cellColLen4
      var cellColLen5
      var freezeDict2 = {"left":0,"right":0}
      var freezeDict3 = {"left":0,"right":0}
      var freezeDict4 = {"left":0,"right":0}
      /* eslint-enable */

var adjustTable = function () { // eslint-disable-line no-unused-vars
  setTimeout(() => {
    $(`#${$(this).attr('data-id')}`).DataTable().columns.adjust()
  }, 500)
}
function approval_table_configs(){
  $('#approval_table_Modal').find('.modal-body').empty()
  $('#approval_table_Modal').find('.modal-header').find('h5').text("Approval Table")
  var parsedData = JSON.parse($(this).attr('data-data'))
  let rtf_data = $(this).attr("data-rtf_data")
  let fileFieldData = $(this).attr("data-file_field_data");
  if(rtf_data){
    rtf_data = JSON.parse(rtf_data)
  }else{
    rtf_data = []
  }
  if(fileFieldData){
    fileFieldData = JSON.parse(fileFieldData)
  }else{
    fileFieldData = []
  }
  var flag = false
  var flag2 = false
  var flag3 = false
  let json_data = false
  let approvalInfo = false;
  let approvalInfoCols = [];
  if ($(this).attr('data-data').startsWith('{') && $(this).attr('data-data').endsWith('}')){
    parsedData = [parsedData]
    flag = true
  }else if ($(this).attr('data-data').startsWith('[')){
    if($(this).attr('data-data')[1] == '{'){
      flag = true
    }else{
      flag2 = true
    }
  }else if ($(this).attr('data-data')[0] == '"'){
    parsedData = JSON.parse(JSON.parse($(this).attr('data-data')))
    flag2 = true
  }

  let columnAlignment = {};
  let columnAlignmentDef = [];
  if ($(this).attr('data-column-alignment')) {
    columnAlignment = JSON.parse($(this).attr('data-column-alignment'));
    if (Object.keys(columnAlignment).length == 0) {
      columnAlignmentDef.push(
        {
          targets: "_all",
          className: 'dt-center allColumnClass all',
        }
      )
    }
  } else {
    columnAlignmentDef.push(
      {
        targets: "_all",
        className: 'dt-center allColumnClass all',
      }
    )
  }

  if ($(this).attr('data-name') == 'approval_level_config'){
    var parsedData = JSON.parse($(this).attr('data-data'))
    flag= false
    flag2 = false
    flag3 = true
    var html =`
    <table id="aproval1${$(this).attr('data-s_id')}" class="row-border display" style="width: 100%;">
                        <thead>
                        <tr>
                        </tr>
                        </thead>
                        <tbody>
                        </tbody>
                      </table>`
    $('#approval_table_Modal').find('.modal-body').append(html)
    for (let k in parsedData['level_config']){
      string=`<tr>`
      for (let i in parsedData['level_config'][k]){
        string += `<td class="view_details_wrap">${String(parsedData['level_config'][k][i]).replaceAll(",", ", ")}</td>`
      }
      string+=`</tr>`
      $('#approval_table_Modal').find('.modal-body').find('table').find('tbody').append(string)
    }
    for (let k in parsedData['level_config'][0]){
      $('#approval_table_Modal').find('.modal-body').find('table').find('thead tr').eq(0).append(`<th>${String(k).replaceAll(",", ", ")}</th>`)
    }
  }
  if ($(this).attr('data-name') == 'approval_information'){
    approvalInfo = true;
    var parsedData = JSON.parse($(this).attr('data-data'))
    flag= false
    flag2 = false
    flag3 = true
    var html =`
    <table id="aproval1${$(this).attr('data-s_id')}" class="row-border display" style="width: 100%;">
      <thead>
        <tr>
        </tr>
      </thead>
      <tbody>
      </tbody>
    </table>`
    $('#approval_table_Modal').find('.modal-body').append(html)
    if (Object.keys(parsedData).length>0) {
      let approvalType = parsedData.type;
      let approverDetails = parsedData.approval_details;
      if (approvalType == "multi_level") {
        theadHTML = '';
        theadHTML += '<th>Level</th>'
        theadHTML += '<th>Level - Approval Type</th>'
        theadHTML += '<th>Level - Approver Type</th>'
        theadHTML += '<th>Approver(s)</th>'
        theadHTML += '<th>Approved By</th>'
        theadHTML += '<th>Rejected By</th>'
        approvalInfoCols.push('Level')
        approvalInfoCols.push('Level - Approval Type')
        approvalInfoCols.push('Level - Approver Type')
        approvalInfoCols.push('Approver(s)')
        approvalInfoCols.push('Approved By')
        approvalInfoCols.push('Rejected By')
        $('#approval_table_Modal').find('.modal-body').find(`#aproval1${$(this).attr('data-s_id')}`).find('thead > tr').append(theadHTML);
        tbodyHTML = '';
        for (i in approverDetails.level_config) {
          levelDetails = approverDetails.level_config[i];
          tbodyHTML += "<tr>";
          tbodyHTML += `<td>Level ${i}</td>`;
          var lvlApprovalType = "";
          var approvers = "";
          if (levelDetails.user_list) {
            lvlApprovalType = "User Based";
            approvers = levelDetails.user_list;
          } else if (levelDetails.group_list) {
            lvlApprovalType = "Group Based";
            approvers = levelDetails.group_list;
          }
          tbodyHTML += `<td>${lvlApprovalType}</td>`;
          tbodyHTML += `<td>${levelDetails.approver_type}</td>`;
          tbodyHTML += `<td>${approvers}</td>`;
          if (levelDetails.approved_by) {
            tbodyHTML += `<td>${levelDetails.approved_by}</td>`;
          } else {
            tbodyHTML += `<td>-</td>`;
          }
          if (levelDetails.rejected_by) {
            tbodyHTML += `<td>${levelDetails.rejected_by}</td>`;
          } else {
            tbodyHTML += `<td>-</td>`;
          }
          tbodyHTML += "</tr>";
        }
        $('#approval_table_Modal').find('.modal-body').find(`#aproval1${$(this).attr('data-s_id')}`).find('tbody').append(tbodyHTML);
      } else {
        theadHTML = '';
        theadHTML += '<th>Approval Type</th>'
        theadHTML += '<th>Approver Type</th>'
        theadHTML += '<th>Approver(s)</th>'
        theadHTML += '<th>Approved By</th>'
        theadHTML += '<th>Rejected By</th>'
        approvalInfoCols.push('Approval Type')
        approvalInfoCols.push('Approver Type')
        approvalInfoCols.push('Approver(s)')
        approvalInfoCols.push('Approved By')
        approvalInfoCols.push('Rejected By')
        $('#approval_table_Modal').find('.modal-body').find(`#aproval1${$(this).attr('data-s_id')}`).find('thead > tr').append(theadHTML);
        var approvalTypeFR = '';
        approvers = '';
        approvedBy = '';
        rejectedBy = '';
        if (approverDetails.user_list) {
          approvalTypeFR = "User Based";
          approvers = approverDetails.user_list;
        } else if (approverDetails.group_list) {
          approvalTypeFR = "Group Based";
          approvers = approverDetails.group_list;
        }
        if (approverDetails.approved_by) {
          approvedBy = `<td>${approverDetails.approved_by}</td>`;
        } else {
          approvedBy = `<td>-</td>`;
        }
        if (approverDetails.rejected_by) {
          rejectedBy = `<td>${approverDetails.rejected_by}</td>`;
        } else {
          rejectedBy = `<td>-</td>`;
        }
        tbodyHTML = `
        <tr>
        <td>${approvalTypeFR}</td>
        <td>${approverDetails.approver_type}</td>
        <td>${approvers}</td>
        ${approvedBy}
        ${rejectedBy}
        </tr>`;
        $('#approval_table_Modal').find('.modal-body').find(`#aproval1${$(this).attr('data-s_id')}`).find('tbody').append(tbodyHTML);
      }
    }
  }
  if (flag2){
    var html =`
    <table id="aproval1${$(this).attr('data-s_id')}" class="row-border display" style="width: 100%;">
                        <thead>
                        <tr>
                        </tr>
                        </thead>
                        <tbody>
                        </tbody>
                      </table>`
    $('#approval_table_Modal').find('.modal-body').append(html)
    $('#approval_table_Modal').find('.modal-body').find('thead tr').append(`<td>${$(this).attr('data-name')}</td>`)
    for (let i in parsedData){
      string=`<tr>`
      string += `<td class="view_details_wrap">${String(parsedData[i]).replaceAll(",", ", ")}</td>`
      string+=`</tr>`
      $('#approval_table_Modal').find('.modal-body').find('table').find('tbody').append(string)
    }
  }

  if (flag){
    if($(this).attr('data-name') == 'approver_user'){
      var html =`
        <table id="aproval1${$(this).attr('data-s_id')}" class="row-border display" style="width: 100%;">
                            <thead>
                            </thead>
                            <tbody>
                            </tbody>
                          </table>`
        $('#approval_table_Modal').find('.modal-body').append(html)
        for (let i in parsedData){
          tm_head = "<tr>"
          for(let [key,value] of Object.entries(parsedData[i]) ){
            tm_head += `<th>${key.toUpperCase()}</th>`
          }
          tm_head+="</tr>"
          break
        }
        $('#approval_table_Modal').find('.modal-body > table > thead').append(tm_head)
        for (let i in parsedData){
          string=`<tr>`
          for(let [key,value] of Object.entries(parsedData[i]) ){
            string+=`<td class="view_details_wrap">${String(value)}</td>`
          }
          string+=`</tr>`
          $('#approval_table_Modal').find('.modal-body > table > tbody').append(string)
      }
    }else if($(this).attr('data-name') == 'json_data'){
      $('#approval_table_Modal').find('.modal-header').find('h5').text("Approval Details")
      json_data = true
      var html =`
        <table id="aproval1${$(this).attr('data-s_id')}" class="row-border display" style="width: 100%;">
                            <thead>
                            <tr>
                              <th>Column</th>
                              <th>Value</th>
                            </tr>
                            </thead>
                            <tbody>
                            </tbody>
                          </table>`
        $('#approval_table_Modal').find('.modal-body').append(html)
        var supported_formats =  [".PNG", ".JPEG", ".JPG", ".BMP",".MP4",".OGV",".WEBM",".PDF"]
        var image_formats = [".PNG", ".JPEG", ".JPG", ".BMP"]
        var video_formats = [".MP4",".WEBM",".OGV"]
        for (let i in parsedData){
          string = ""
          for(let [key,value] of Object.entries(parsedData[i]) ){
            string+=`<tr><td class="view_details_wrap">${String(key)}</td>`
            if (fileFieldData.includes(key)){
              if(value){
                var fileNames = value.split(", ");
                string += `<td class="view_details_wrap">`
                for (file of fileNames) {
                  let format = String(value).slice(-4)
                  if (image_formats.includes(format.toUpperCase())){
                    string+=`<a class="mr-1" onclick="FilePreviewButton(this)" style="display:block;">
                    <i class="fa fa-image mr-2 ihover" style="font-size:15px;cursor:pointer;"></i>
                    <u>${String(file)}</u></a>`
                  }else if (video_formats.includes(format.toUpperCase())){
                    string+=`<a class="mr-1" onclick="FilePreviewButton(this)" style="display:block;">
                  <i class="fa fa-video-camera mr-2 ihover" style="font-size:15px;cursor:pointer;"></i>
                  <u>${String(file)}</u></a>`
                  }else{
                    string+=`<a class="mr-1" onclick="FilePreviewButton(this)" style="display:block;">
                  <i class="fa fa-file mr-2 ihover" style="font-size:15px;cursor:pointer;"></i>
                  <u>${String(file)}</u></a>`
                  }
                }
                string += "</td></tr>"
              }else{
                string+=`<td class="view_details_wrap">${String(value)}</td></tr>`
              }
            } else{
              if(String(value).startsWith('[')){
                string += `<td><button class="view_data_btn table_field_show_button view_listview_data" style="background-color: transparent; border: transparent;" onclick="approval_template_json_in_tabular.call(this)" data-column-alignment-config='${JSON.stringify(columnAlignment)}' data-json='${String(value)}'>View Data</button></td>`
              }
              else{
                string+=`<td class="view_details_wrap">${String(value)}</td></tr>`
              }

            }

          }
          $('#approval_table_Modal').find('.modal-body > table > tbody').append(string)
      }
    }else if($(this).attr('data-name') == 'approved_by'){

      var html =`
        <table id="aproval1${$(this).attr('data-s_id')}" class="row-border display" style="width: 100%;">
                            <thead>
                            <tr>
                              <th>Level</th>
                              <th>Approved By</th>
                            </tr>
                            </thead>
                            <tbody>
                            </tbody>
                          </table>`
      $('#approval_table_Modal').find('.modal-body').append(html)
      for (let [key, value] of Object.entries(parsedData[0])){
        string=`
        <tr>
          <td class="view_details_wrap">${String(key)}</td>
          <td class="view_details_wrap">${value.join(", ")}</td>
        </tr>`
        $('#approval_table_Modal').find('.modal-body').find('table').find('tbody').append(string)
      }
    }else{
      var html =`
      <table id="approval_table${$(this).attr('data-s_id')}" class="row-border display" style="width: 100%;">
                          <thead>
                          <tr>
                          </tr>
                          </thead>
                          <tbody>
                          </tbody>
                        </table>`
      $('#approval_table_Modal').find('.modal-body').append(html)
      for (let i in parsedData){
        string=`<tr>`
        for(let [key,value] of Object.entries(parsedData[i]) ){
          string+=`<td class="view_details_wrap">${String(value)}</td>`
        }
        string+=`</tr>`
        $('#approval_table_Modal').find('.modal-body').find('table').find('tbody').append(string)

      for(let [key,value] of Object.entries(parsedData[0])){
        $('#approval_table_Modal').find('.modal-body').find('table').find('thead tr').eq(0).append(`<th>${key}</th>`)
      }
    }
  }
}
  $('#approval_table_Modal').modal('show');
  if (!flag && !flag2 && !flag3){
    $('#approval_table_Modal').find('.modal-body').append(`<p>No data to show</p>`)
  }else{
    if (Object.keys(columnAlignment).length) {
      var globalHeader = "center";
      var globalContent = "center";
      if (columnAlignment.global_header) {
        globalHeader = columnAlignment['global_header'];
      }
      if (columnAlignment.global_content) {
        globalContent = columnAlignment['global_content'];
      }
      if (json_data) {
        if (columnAlignment.field_level_config) {
          if (columnAlignment.field_level_config['Column'].header && columnAlignment.field_level_config['Column'].content) {
            var header = columnAlignment.field_level_config['Column']['header'];
            var content = columnAlignment.field_level_config['Column']['content'];
            columnAlignmentDef.push(
              {
                targets: [0],
                className: `dt-head-${header} dt-body-${content} allColumnClass all`,
              }
            )
          } else {
            columnAlignmentDef.push(
              {
                targets: [0],
                className: `dt-head-${globalHeader} dt-body-${globalContent} allColumnClass all`,
              }
            )
          }
          if (columnAlignment.field_level_config['Value'].header && columnAlignment.field_level_config['Value'].content) {
            var header = columnAlignment.field_level_config['Value']['header'];
            var content = columnAlignment.field_level_config['Value']['content'];
            columnAlignmentDef.push(
              {
                targets: [1],
                className: `dt-head-${header} dt-body-${content} allColumnClass all`,
              }
            )
          } else {
            columnAlignmentDef.push(
              {
                targets: [1],
                className: `dt-head-${globalHeader} dt-body-${globalContent} allColumnClass all`,
              }
            )
          }
        } else {
          columnAlignmentDef.push(
            {
              targets: [1],
              className: `dt-head-${globalHeader} dt-body-${globalContent} allColumnClass all`,
            }
          )
        }
      } else if (approvalInfo) {
        for (let index = 0; index < approvalInfoCols.length; index++) {
          const k = approvalInfoCols[index];
          if (columnAlignment.field_level_config) {
            if (columnAlignment.field_level_config[k]) {
              if (columnAlignment.field_level_config[k].header && columnAlignment.field_level_config[k].header) {
                var header = value['header'];
                var content = value['content'];
                columnAlignmentDef.push(
                  {
                    targets: [index],
                    className: `dt-head-${header} dt-body-${content} allColumnClass all`,
                  }
                )
              } else {
                columnAlignmentDef.push(
                  {
                    targets: [index],
                    className: `dt-head-${globalHeader} dt-body-${globalContent} allColumnClass all`,
                  }
                )
              }
            } else {
              columnAlignmentDef.push(
                {
                  targets: [index],
                  className: `dt-head-${globalHeader} dt-body-${globalContent} allColumnClass all`,
                }
              )
            }
          } else {
            columnAlignmentDef.push(
              {
                targets: [index],
                className: `dt-head-${globalHeader} dt-body-${globalContent} allColumnClass all`,
              }
            )
          }
        }
      } else {
        for (let [k,v] of Object.entries(parsedData[0])) {
          var index = Array(Object.keys(parsedData[0])).indexOf(k);
          if (columnAlignment.field_level_config) {
            if (columnAlignment.field_level_config[k]) {
              if (columnAlignment.field_level_config[k].header && columnAlignment.field_level_config[k].header) {
                var header = value['header'];
                var content = value['content'];
                columnAlignmentDef.push(
                  {
                    targets: [index],
                    className: `dt-head-${header} dt-body-${content} allColumnClass all`,
                  }
                )
              } else {
                columnAlignmentDef.push(
                  {
                    targets: [index],
                    className: `dt-head-${globalHeader} dt-body-${globalContent} allColumnClass all`,
                  }
                )
              }
            } else {
              columnAlignmentDef.push(
                {
                  targets: [index],
                  className: `dt-head-${globalHeader} dt-body-${globalContent} allColumnClass all`,
                }
              )
            }
          } else {
            columnAlignmentDef.push(
              {
                targets: [index],
                className: `dt-head-${globalHeader} dt-body-${globalContent} allColumnClass all`,
              }
            )
          }
        }
      }
    }
    if(json_data){
      var table = $('#approval_table_Modal').find('.modal-body > table').DataTable(
        {
          autoWidth: true,
          scrollCollapse: true,
          responsive: true,
          scrollY: '50vh',
          scrollX: '300',
          bLengthChange: false,
          searching: false,
          info: false,
          paging: false,
          columnDefs: columnAlignmentDef,
          ordering: false,
        }
      );
      setTimeout(() => {
        table.columns.adjust();
      }, 200);
    }else{
      var table = $('#approval_table_Modal').find('.modal-body > table').DataTable(
        {
          autoWidth: true,
          scrollCollapse: true,
          responsive: true,
          autoWidth: true,
          scrollY: '50vh',
          scrollX: true,
          autoWidth: false,
          columnDefs: columnAlignmentDef,
        }
      );
      setTimeout(() => {
        table.columns.adjust();
      }, 200);
    }
  }
}

function approval_template_json_in_tabular(){
  let data = $(this).attr("data-json")
  let nestedTableColumnAlignment;
  if ($(this).attr('data-column-alignment-config')) {
    nestedTableColumnAlignment = JSON.parse($(this).attr('data-column-alignment-config'));
  } else {
    nestedTableColumnAlignment = {};
  }
  $('#approval_template_json_data_tabular').find('.modal-body').empty()
  let columnAlignmentArray = [];
  if (data){
    var jsonData = JSON.parse(data)
    var table = "<table id='table-as-field-history-table'><thead><tr>";

    for (var key in jsonData[0]) {
      if (jsonData[0].hasOwnProperty(key)) {
        table += "<th>" + key + "</th>";
      }
    }

    table += "</tr></thead><tbody>";

    for (var i = 0; i < jsonData.length; i++) {
        table += "<tr>";
        for (var key in jsonData[i]) {
            if (jsonData[i].hasOwnProperty(key)) {
                table += "<td>" + jsonData[i][key] + "</td>";
            }
        }
        table += "</tr>";
    }

    table += "</tbody></table>";

    $('#approval_template_json_data_tabular').find('.modal-body').append(table)
    if (Object.keys(nestedTableColumnAlignment).length) {
      var globalHeader = "center";
      var globalContent = "center";
      if (nestedTableColumnAlignment.global_header) {
        globalHeader = nestedTableColumnAlignment['global_header'];
      }
      if (nestedTableColumnAlignment.global_content) {
        globalContent = nestedTableColumnAlignment['global_content'];
      }
      columnAlignmentArray.push(
        {
          targets: "_all",
          className: `dt-head-${globalHeader} dt-body-${globalContent} allColumnClass all`,
        }
      )
    } else {
      columnAlignmentArray.push(
        {
          targets: "_all",
          className: `dt-head-center dt-body-center allColumnClass all`,
        }
      )
    }
  }

  var table = $('#approval_template_json_data_tabular').find('.modal-body > table').DataTable(
    {
      autoWidth: true,
      scrollCollapse: true,
      responsive: true,
      autoWidth: true,
      scrollY: '50vh',
      scrollX: true,
      autoWidth: false,
      ordering: false,
      columnDefs: columnAlignmentArray,
    }
  );
  setTimeout(() => {
    table.columns.adjust();
  }, 200);


  $('#approval_template_json_data_tabular').modal('show')

}

var scenarioDetail = function () { // eslint-disable-line no-unused-vars
  const dataScenario = $(this).attr('data-data')
  const sID = $(this).attr('data-s_id')
  $.ajax({
    url: `/users/${urlPath}/dynamicVal/`,
    data: {
      operation: 'fetch_scenario_detail',
      data: dataScenario,
      s_id: sID
    },
    type: 'POST',
    dataType: 'json',
    success: function (data) {
      $('#scenarioModal').find('.modal-body').empty()
      const listOfTable = []
      for (const [key, value] of Object.entries(data)) {
        const html = `
                <div class="card card-default collapsed-card">
                  <div class="card-header">
                    <h6 class="card-title" style="font-size: medium; color:var(--primary-color); font-weight: bold;">${key}</h6>

                    <div class="card-tools">

                      <button type="button" class="btn btn-tool" onclick="adjustTable.call(this)" data-id="${key}" data-card-widget="collapse"><i class="fas fa-plus"></i></button>

                    </div>
                  </div>
                  <div class="card-body">
                    <table id="${key}" class="row-border display" style="width: 100%;">
                      <thead>
                      </thead>
                      <tbody>
                      </tbody>
                    </table>
                  </div>
                </div>
                `
        $('#scenarioModal').find('.modal-body').append(html)
        let htmlHead = ''
        let htmlBody = ''
        for (let i = 0; i < value.length; i++) {
          htmlBody = htmlBody + '<tr>'
          htmlHead = ''
          for (let [key1, value1] of Object.entries(value[i])) { // eslint-disable-line no-unused-vars
            htmlHead = htmlHead + `<th>${key1}</th>`
            if (value1 === 'null') {
              value1 = ''
            }
            htmlBody = htmlBody + `<td class="view_details_wrap">${value1.toString()}</td>`
          }
          htmlBody = htmlBody + '</tr>'
        }
        $('#scenarioModal').find('.modal-body').find('#' + key).find('thead').append('<tr>' + htmlHead + '</tr>')
        $('#scenarioModal').find('.modal-body').find('#' + key).find('tbody').append(htmlBody)
        datatables(key)
        listOfTable.push(key)
      }
      $('#scenarioModal').modal('show')
      setTimeout(() => {
        for (let j = 0; j < listOfTable.length; j++) {
          $(`#${listOfTable[j]}`).DataTable().columns.adjust()
        }
      }, 500)
    },
    error: () => {
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    }
  })
}

function editCompScenario () { // eslint-disable-line no-unused-vars
  const modelElementID = $(this).attr('data-element_id')
  const elementNameComponent = $(this).attr('data-element_name')
  const scenarioName = $('#scenario_name_').val()
  const scenarioID = $(this).attr('data-scenario_id')
  const scenID = $(this).parent().parent().find('td').attr('data-equation_editor_model')
  let replaceIdentifierList
  let replaceColumnList
  $(`#viewScenarioData_${modelElementID}`).empty()
  $.ajax({
    url: `/users/${urlPath}/computationModule/`,
    data: {
      scenario_name: scenarioName,
      scenario_id: scenarioID,
      element_name: elementNameComponent,
      operation: 'computation_element_scenario_data'
    },
    type: 'POST',
    dataType: 'json',
    success: function (data) {
      $('.existingDataHeader').text('Existing Scenario Data')
      $(`#viewScenarioData_${modelElementID}`).empty()
      $(`#viewScenarioData_${modelElementID}`).append(
        `<div class="card shadow-sm  bg-white rounded;">
          <div class="card-body" style="padding:0.9rem;max-height:90">
              <table id="exampledataResultsScenario_${modelElementID}" class="display compact" style="width:100%;">
                  <thead>
                      <tr></tr>
                  </thead>
                  <tbody>
                  </tbody>
              </table>
          </div>
        </div>
        <div class="card shadow-sm  bg-white rounded;">
        <form id="incremental_data_${modelElementID}">
          <div class="card-header" style="color:var(--primary-color);">
            <h5 class="mb-0" style="text-align:center;">
              Configure Scenario Data
            </h5>
          </div>
          <div class="card-body" style="padding:0.9rem;">
            <div class="row">
              <div class="form-group col-4">
                  <label for="selectScenarioDataType_${modelElementID}">Select scenario data type:</label>
                  <select id="selectScenarioDataType_${modelElementID}" class="select2 form-control" name="selectScenarioDataType_${modelElementID}">
                    <option value="upload_data">Upload data</option>
                    <option value="equation_builder">Create with equation builder</option>
                  </select>
                </div>
              </div>
            </div>
            <div class="row">
              <div class="form-group col-4" id="uploadData_${modelElementID}">
                <div class="custom-file" style="margin-left: 0.5rem;">
                  <input type="file" class="custom-file-input"  accept=".csv" name="customFile">
                  <label class="custom-file-label" for="customFile">Choose file</label>
                </div>
                <br>
                <br>
              </div>
              <div class="form-group col-4 EBDisplayButtonIDDiv" id="equationBuilder_${modelElementID}" style="display:none">
                <button style="color:aliceblue; margin-left: 0.5rem;" type="button" id="EBDisplayButtonID" class="btn btn-primary btn-xs rounded">Equation builder</button>
              </div>
            </div>
            <div class="form-group col-7" style="display:flex">
              <label style="margin-left: 0.5rem;">Scenario type (Base Data) : </label>
              <div id="" class="custom-control custom-checkbox" style="margin-left:1%;">
                <input type="checkbox" name="defaultValueConfig" data-scenario_type="append" id="append${modelElementID}" class="checkboxinput custom-control-input" value="0">
                <label for="append${modelElementID}" class="custom-control-label">
                  Append
                </label>
              </div>
              <div id="" class="custom-control custom-checkbox" style="margin-left:1%;">
                <input type="checkbox" name="defaultValueConfig" data-scenario_type="replace" id="replace${modelElementID}" class="checkboxinput custom-control-input" value="0">
                <label for="replace${modelElementID}" class="custom-control-label">
                  Replace
                </label>
              </div>
            </div>
            <div class="form-group col-4" style="margin-left:0.4rem;display:None;">
              <label for="selectIdentifierColumns_${modelElementID}">Select identifier columns:</label>
              <select id="selectIdentifierColumns_${modelElementID}" class="select2 form-control" name="selectIdentifierColumns_${modelElementID}" multiple>
              </select>
            </div>
            <div class="form-group col-4" style="margin-left:0.4rem;display:None;">
              <label for="selectUpdateColumns_${modelElementID}">Select columns to update:</label>
              <select id="selectUpdateColumns_${modelElementID}" class="select2 form-control" name="selectUpdateColumns_${modelElementID}" multiple>
              </select>
            </div>
            <div class="form-group col-7" style="display:flex">
              <label style="margin-left: 0.5rem;">Scenario type (Scenario Data) : </label>
              <div id="" class="custom-control custom-checkbox" style="margin-left:1%;">
                <input type="checkbox" name="defaultValueConfig_1" id="appendScenarioData${modelElementID}" class="checkboxinput custom-control-input" value="0">
                <label for="appendScenarioData${modelElementID}" class="custom-control-label">
                  Append
                </label>
              </div>
              <div id="" class="custom-control custom-checkbox" style="margin-left:1%;">
                <input type="checkbox" name="defaultValueConfig_1" id="replaceScenarioData${modelElementID}" class="checkboxinput custom-control-input" value="0">
                <label for="replaceScenarioData${modelElementID}" class="custom-control-label">
                  Replace
                </label>
              </div>
            </div>
          </div>
          <div style="float:right;">
            <button type="button" id="addScenarioData_${modelElementID}" data-element_id = "${modelElementID}"  data-form_id = "incremental_data_${modelElementID}" data-element_id_component = "${data.element_identifier}" data-scenario_name = "${scenarioName}" data-element_name = "${elementNameComponent}" class="btn btn-primary btn-xs mx-1 my-1 rounded px-2">Save scenario &nbsp;<i class="fas fa-save"></i></button>
            <button type="button" id="quitScenarioData_${modelElementID}" class="btn btn-primary btn-xs mx-2 rounded px-2" data-dismiss="modal">Close</button>
          </div>
        </form>
        </div>
        `
      )
      $('select.select2:not(.modal select.select2)').each(function(){
        parent = $(this).parent()
        $(this).select2({dropdownParent:parent})
      })
      $('.modal select.select2').each(function(){
        $(this).select2()
      })
      for (const i in data.columns_list) {
        $(`#selectIdentifierColumns_${modelElementID}`).append(`<option value="${data.columns_list[i]}">${data.columns_list[i]}</option>`)
        $(`#selectUpdateColumns_${modelElementID}`).append(`<option value="${data.columns_list[i]}">${data.columns_list[i]}</option>`)
      }
      $(`#selectIdentifierColumns_${modelElementID}`).off('select2:select select2:unselect').on('select2:select select2:unselect', function () {
        $(`#selectUpdateColumns_${modelElementID}`).empty()
        const selIdentifier = $(this).val()
        for (const i in data.columns_list) {
          if (selIdentifier.includes(data.columns_list[i]) === false) {
            $(`#selectUpdateColumns_${modelElementID}`).append(new Option(data.columns_list[i], data.columns_list[i], false, false))
          };
        };
      })
      $(`#selectScenarioDataType_${modelElementID}`).select2()
      setTimeout(function () {
        for (const [key, value] of Object.entries(data.scenario_config_dict)) { // eslint-disable-line no-unused-vars
          if (String(value.equation_editor_model) === scenID) {
            $(`#selectScenarioDataType_${modelElementID}`).val(value.scenario_data_type).trigger('change')
            $(`#selectScenarioDataType_${modelElementID}`).val(value.scenario_data_type).trigger('select2:select')
          }
        }
      }, 1000)
      $(`#selectScenarioDataType_${modelElementID}`).off('select2:select').on('select2:select', function () {
        if (String($(this).val()) === 'upload_data') {
          $(`#uploadData_${modelElementID}`).css('display', '')
          $(`#equationBuilder_${modelElementID}`).css('display', 'none')
        } else {
          $(`#uploadData_${modelElementID}`).css('display', 'none')
          $(`#equationBuilder_${modelElementID}`).css('display', '')
        }
      })
      for (const i in data.scenario_config_dict) {
        if (String(data.scenario_config_dict[i].element_name) === String(elementNameComponent)) {
          const scenarioType = data.scenario_config_dict[i].scenario_type
          if (String(scenarioType) === 'replace') {
            $(`#replace${modelElementID}`).prop('checked', true)
            if ('replace_identifier_list' in data.scenario_config_dict[i]) {
              replaceIdentifierList = data.scenario_config_dict[i].replace_identifier_list
              replaceColumnList = data.scenario_config_dict[i].replace_column_list
            } else {
              replaceIdentifierList = []
              replaceColumnList = []
            }
            $(`#selectIdentifierColumns_${modelElementID}`).parent().css('display', '')
            $(`#selectUpdateColumns_${modelElementID}`).parent().css('display', '')
            $(`#selectIdentifierColumns_${modelElementID}`).val(replaceIdentifierList).trigger('change')
            $(`#selectUpdateColumns_${modelElementID}`).val(replaceColumnList).trigger('change')
          } else {
            $(`#append${modelElementID}`).prop('checked', true)
          }
          const scenarioTypeScenarioData = data.scenario_config_dict[i].scenario_type_scenarioData
          if (String(scenarioTypeScenarioData) === 'replace') {
            $(`#replaceScenarioData${modelElementID}`).prop('checked', true)
          } else {
            $(`#appendScenarioData${modelElementID}`).prop('checked', true)
          }
          break
        }
      }
      $('[name="defaultValueConfig"]').change(function () {
        if ($(this).attr('data-scenario_type') === 'replace') {
          $(`#selectIdentifierColumns_${modelElementID}`).parent().css('display', '')
          $(`#selectUpdateColumns_${modelElementID}`).parent().css('display', '')
        } else {
          $(`#selectIdentifierColumns_${modelElementID}`).parent().css('display', 'none')
          $(`#selectUpdateColumns_${modelElementID}`).parent().css('display', 'none')
        }
        if (this.checked) {
          $('[name="defaultValueConfig"]').not(this).prop('checked', false)
        }
      })
      $('[name="defaultValueConfig_1"]').change(function () {
        if (this.checked) {
          $('[name="defaultValueConfig_1"]').not(this).prop('checked', false)
        }
      })
      $('#EBDisplayButtonID').attr('data-name', scenarioName + data.element_identifier)
      eqBuilder(scenarioName, data.element_identifier, modelElementID)

      $('.custom-file-input').on('change', function () {
        const fileName = $(this).val().split('\\').pop()
        $(this).siblings('.custom-file-label').addClass('selected').html(fileName)
      })
      for (let i = 0; i < data.table[data.table_headers[0]].length; i++) {
        let string = '<tr>'
        for (const j in data.table_headers) {
          string += `<td style="text-align:center;">${data.table[data.table_headers[j]][i]}</td>`
        }
        string += '</tr>'
        $(`#exampledataResultsScenario_${modelElementID}`).find('tbody').append(string)
      }

      $(`#exampledataResultsScenario_${modelElementID} thead tr`).empty()
      for (const j in data.table_headers) {
        $(`#exampledataResultsScenario_${modelElementID}`).find('thead tr').eq(0).append(`<th style="text-align:center;">${data.table_headers[j]}</th>`)
      }
      $(`#scenarioDataOutputModal_${modelElementID}`).modal('show')
      initialise_table_results('exampledataResultsScenario', modelElementID)
      $(`#addScenarioData_${modelElementID}`).attr('data-scenario_data_source', 'saved_scenario')
      $(`#addScenarioData_${modelElementID}`).attr('data-scenario_id', scenarioID)
      $(`#addScenarioData_${modelElementID}`).click(saveIncrementalData)
    },
    error: function () {
      Swal.fire({icon: 'error',text: 'Error! Failure in fetching the table data. Please try again.'});
    }
  })
}
function saveIncrementalData () { // eslint-disable-line no-unused-vars
  const source = $(this).attr('data-scenario_data_source')
  const modelElementID = $(this).attr('data-element_id')
  const scenarioDataType = $(`#selectScenarioDataType_${modelElementID}`).val()
  const scenarioID = $(this).attr('data-scenario_id')
  const elementIDComponent = $(this).attr('data-element_id_component')
  const scenarioName = $(this).attr('data-scenario_name')
  const elementNameComponent = $(this).attr('data-element_name')
  let scenarioType = 'append'
  let scenarioTypeScenarioData = 'append'
  let replaceIdentifierList = []
  let replaceColumnList = []
  if ($(`#replace${modelElementID}`).prop('checked')) {
    scenarioType = 'replace'
    replaceIdentifierList = $(`#selectIdentifierColumns_${modelElementID}`).val()
    replaceColumnList = $(`#selectUpdateColumns_${modelElementID}`).val()
  };
  if ($(`#replaceScenarioData${modelElementID}`).prop('checked')) {
    scenarioTypeScenarioData = 'replace'
  };
  if (String(scenarioDataType) === 'upload_data') {
    const formData = new FormData($(`#${$(this).attr('data-form_id')}`)[0])
    formData.append('element_id_component', elementIDComponent)
    formData.append('model', $(`#modelName_${modelElementID}`).attr('data-model_name'))
    formData.append('scenario_data_type', scenarioDataType)
    formData.append('scenario_type', scenarioType)
    formData.append('scenario_type_scenarioData', scenarioTypeScenarioData)
    formData.append('replace_identifier_list', JSON.stringify(replaceIdentifierList))
    formData.append('replace_column_list', JSON.stringify(replaceColumnList))
    formData.append('scenario_name', scenarioName)
    formData.append('operation', 'scenario_incremental_data')
    $.ajax({
      url: `/users/${urlPath}/computationModule/`,
      data: formData,
      type: 'POST',
      cache: false,
      contentType: false,
      processData: false,
      success: function (data) {
        if (String(data.message) === 'success') {
          $(`#scenarioDataOutputModal_${modelElementID}`).modal('hide')
          if (String(source) === 'saved_scenario') {
            $('#element_incremental_data_').find('tr').each(function () {
              if (String($(this).find('td').eq(0).text()) === String(elementNameComponent)) {
                $(this).remove()
              }
            })
            $('#element_incremental_data_').append(
              `<tr>
                <td style="text-align: center;" data-scenario_type="${scenarioType}" data-scenario_type_scenarioData = "${scenarioTypeScenarioData}" data-scenario_data_type="${scenarioDataType}" data-element_component_id="${elementIDComponent}" data-replace_identifier_list=${JSON.stringify(replaceIdentifierList)} data-replace_column_list=${JSON.stringify(replaceColumnList)}>${elementNameComponent}</td>
                <td style="text-align: center;">${scenarioType}</td>
                <td style="text-align: center;">${scenarioTypeScenarioData}</td>
                <td style="text-align: center;" ><i class="fas fa-edit"" onclick="editCompScenario.call(this)" style="color:var(--primary-color);" data-element_name= "${elementNameComponent}" data-scenario_id="${scenarioID}" data-element_id="${modelElementID}" data-title="Edit element"></i>&nbsp;<i class="fas fa-trash"" onclick="deleteScenarioElement.call(this)" style="color:var(--primary-color);" data-element_name= "${elementNameComponent}" data-scenario_id="${scenarioID}" data-element_id="${modelElementID}" data-title="Delete element"></i></td>
              </tr>`
            )
          } else {
            $(`#element_incremental_data_${modelElementID}`).find('tr').each(function () {
              if (String($(this).find('td').eq(0).attr('data-element_component_id')) === String(elementIDComponent)) {
                $(this).remove()
              }
            })
            $(`#element_incremental_data_${modelElementID}`).append(
              `<tr>
                <td style="text-align: center;" data-scenario_type="${scenarioType}" data-scenario_type_scenarioData = "${scenarioTypeScenarioData}" data-scenario_data_type="${scenarioDataType}" data-element_component_id="${elementIDComponent}" data-replace_identifier_list=${JSON.stringify(replaceIdentifierList)} data-replace_column_list=${JSON.stringify(replaceColumnList)}>${elementNameComponent}</td>
                <td style="text-align: center;">${scenarioType}</td>
              </tr>`
            )
          }
        } else {
          Swal.fire({icon: 'error',text: 'Error! Failure in adding the scenario. Please check your configuration and try again.'});
        }
      },
      error: function () {
        Swal.fire({icon: 'error',text: 'Error! Failure in adding the scenario. Please check your configuration and try again.'});
      }
    })
  } else {
    const equationEditorModel = $(`#equationBuilder_${modelElementID}`).find('button#EBDisplayButtonID').eq(0).attr('data-name')
    $.ajax({
      url: `/users/${urlPath}/computationModule/`,
      data: {
        model: $(`#modelName_${modelElementID}`).attr('data-model_name'),
        element_id_component: elementIDComponent,
        scenario_data_type: scenarioDataType,
        scenario_type: scenarioType,
        scenario_type_scenarioData: scenarioTypeScenarioData,
        replace_identifier_list: JSON.stringify(replaceIdentifierList),
        replace_column_list: JSON.stringify(replaceColumnList),
        scenario_name: scenarioName,
        equation_editor_model: equationEditorModel,
        operation: 'scenario_incremental_data'
      },
      type: 'POST',
      dataType: 'json',
      success: function (data) {
        if (String(data.message) === 'success') {
          $(`#scenarioDataOutputModal_${modelElementID}`).modal('hide')
          if (String(source) === 'saved_scenario') {
            $('#element_incremental_data_').find('tr').each(function () {
              if (String($(this).find('td').eq(0).attr('data-element_component_id')) === String(elementIDComponent)) {
                $(this).remove()
              }
            })
            $('#element_incremental_data_').append(
              `<tr>
                <td style="text-align: center;" data-scenario_type="${scenarioType}" data-scenario_type_scenarioData = "${scenarioTypeScenarioData}" data-scenario_data_type="${scenarioDataType}" data-element_component_id="${elementIDComponent}" data-equation_editor_model="${equationEditorModel}" data-replace_identifier_list=${JSON.stringify(replaceIdentifierList)} data-replace_column_list=${JSON.stringify(replaceColumnList)}>${elementNameComponent}</td>
                <td style="text-align: center;">${scenarioType}</td>
                <td style="text-align: center;">${scenarioTypeScenarioData}</td>
                <td style="text-align: center;" ><i class="fas fa-edit"" onclick="editCompScenario.call(this)" style="color:var(--primary-color);" data-element_name= "${elementNameComponent}" data-scenario_id="${scenarioID}" data-element_id="${modelElementID}" data-title="Edit element"></i>&nbsp;<i class="fas fa-trash"" onclick="deleteScenarioElement.call(this)" style="color:var(--primary-color);" data-element_name= "${elementNameComponent}" data-scenario_id="${scenarioID}" data-element_id="${modelElementID}" data-title="Delete element"></i></td>
              </tr>`
            )
          } else {
            $(`#element_incremental_data_${modelElementID}`).find('tr').each(function () {
              if (String($(this).find('td').eq(0).attr('data-element_component_id')) === String(elementIDComponent)) {
                $(this).remove()
              }
            })
            $(`#element_incremental_data_${modelElementID}`).append(
              `<tr>
                <td style="text-align: center;" data-scenario_type="${scenarioType}" data-scenario_type_scenarioData = "${scenarioTypeScenarioData}" data-scenario_data_type="${scenarioDataType}" data-element_component_id="${elementIDComponent}" data-equation_editor_model="${equationEditorModel}" data-replace_identifier_list=${JSON.stringify(replaceIdentifierList)} data-replace_column_list=${JSON.stringify(replaceColumnList)}>${elementNameComponent}</td>
                <td style="text-align: center;">${scenarioType}</td>
              </tr>`
            )
          }
        } else {
          Swal.fire({icon: 'error',text: 'Error! Failure in adding the scenario. Please check the configuration and try again.'});
        }
      },
      error: () => {
        Swal.fire({icon: 'error',text: 'Error! Failure in adding the scenario. Please check the configuration and try again.'});
      }
    })
  }
}
function deleteScenarioElement () { // eslint-disable-line no-unused-vars
  $(this).parent().parent().remove()
}
$('#run_saved_scenario').click(function () {
  const savedScenarioID = $(this).attr('data-scenario_id')
  const savedScenarioConfig = $(this).attr('data-scenario_config')
  const modelElementID = $(this).attr('data-element_id')
  const savedScenarioName = $('#scenario_name_').val()
  const variableList = []
  // let elementIDGVar
  let varDict = {}
  $(`#computationForm_${modelElementID}`).find('div.form-row').each(function () {
    // elementIDGVar = $(this).attr('data-parent_element_id')
    $(this).find('div.form-group').each(function () {
      if (String($(this).find('select').length) === '0') {
        varDict = {
          varName: $(this).find('label').text(),
          inputValue: $(this).find('input').val()
        }
      } else {
        varDict = {
          varName: $(this).find('label').text(),
          inputValue: $(this).find('select').val()
        }
      }
      variableList.push(varDict)
    })
  })
  $(`#computationForm_${modelElementID}`).find('div.form-row').each(function () {
    const elementIDGVar = $(this).attr('data-parent_element_id')
    $(this).find('div.form-group').each(function () {
      if ($(this).find('input[name=gVarFileRM]').attr('type') === 'file') {
        const formData = new FormData($(this).find('form.gVarFileInput')[0])
        formData.append('operation', 'gVarFileRunModel')
        formData.append('gVarName', $(this).find('label.gVarNameLabel').text())
        formData.append('elementID', elementIDGVar)
        $.ajax({
          url: `/users/${urlPath}/computationModule/`,
          data: formData,
          type: 'POST',
          cache: false,
          contentType: false,
          processData: false,
          success: function (data) {
          },
          error: () => {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          }
        })
      };
    })
  })
  $.ajax({
    url: `/users/${urlPath}/computationModule/`,
    data: {
      config: JSON.stringify({
        model: $(`#modelName_${modelElementID}`).attr('data-model_name'),
        configGlobalDict: variableList,
        configGlobalFunc: []
      }),
      scenario_name: savedScenarioName,
      scenario_id: savedScenarioID,
      scenario_config: savedScenarioConfig,
      operation: 'run_scenario'
    },
    type: 'POST',
    dataType: 'json',
    success: function (data) {
      $(`#viewRunScenarioData_${modelElementID}`).empty()
      $(`#viewRunScenarioData_${modelElementID}`).append(
        `<div class="card shadow-sm  bg-white rounded;">
          <div class="card-body" style="padding:0.9rem;">
              <table id="exampledataResultsScenarioRun_${modelElementID}" class="display compact" style="width:100%;">
                  <thead>
                      <tr></tr>
                  </thead>
                  <tbody>
                  </tbody>
              </table>
          </div>
        </div>
        <div style="float:right;">
            <button type="button" id="quitRunScenarioData_${modelElementID}" class="btn btn-primary btn-xs mx-2 rounded px-2" data-dismiss="modal">Close</button>
        </div>
        `)
      $(`#exampledataResultsScenarioRun_${modelElementID} tbody`).empty()
      $(`#exampledataResultsScenarioRun_${modelElementID} thead tr`).empty()
      if(data.hasOwnProperty('content')){
        for (const [key, value] of Object.entries(data.content[0])) { // eslint-disable-line no-unused-vars
          $(`#exampledataResultsScenarioRun_${modelElementID}`).find('thead tr').eq(0).append(`<th>${key}</th>`)
        };
        for (let i = 0; i < data.content.length; i++) {
          let string = '<tr>'
          for (const [key, value] of Object.entries(data.content[i])) { // eslint-disable-line no-unused-vars
            string += `<td>${value}</td>`
          }
          string += '</tr>'
          $(`#exampledataResultsScenarioRun_${modelElementID}`).find('tbody').append(string)
        };
        $(`#runscenarioDataOutputModal_${modelElementID}`).modal('show')
        initialise_table_results('exampledataResultsScenarioRun', modelElementID)
      }
    },
    error: function () {
      Swal.fire({icon: 'error',text: 'Error! Failure in running the scenario. Please try again.'});
    }
  })
})
$(document).ready(function () {
  $('#ckEditorModal').on('shown.bs.modal', function () {
    $(document).off('focusin.modal')
  })

  $('.copy_class_to_apply').bind({
		copy : function(){
			return false
		}
	});

  $('.paste_class_to_apply').bind({
		paste : function(){
			return false
		}
	});

  $('.dtrangepicker').daterangepicker({
    locale: {
              format: 'YYYY-MM-DD',
          }
   });
   $('.dtrangepicker').val('')

   $('.dttrangepicker').daterangepicker({
    timePicker: true,
    timePicker24Hour: true,
    timePickerSeconds: true,
    locale: {
              format: 'YYYY-MM-DD HH:mm:ss',
          }
   });
   $('.dttrangepicker').val('')

   $('.ttrangepicker').daterangepicker({
    timePicker: true,
    timePicker24Hour: true,
    timePickerIncrement: 1,
    timePickerSeconds: true,
    locale: {
        format: 'HH:mm:ss'
    }
   }).on('show.daterangepicker', function (ev, picker) {
        picker.container.find(".calendar-table").hide();
    });

   $('.ttrangepicker').val('')
   $('.ttrangepicker_sec').daterangepicker({
    timePicker: true,
    timePicker24Hour: true,
    timePickerIncrement: 1,
    locale: {
        format: 'HH:mm'
    }
   }).on('show.daterangepicker', function (ev, picker) {
        picker.container.find(".calendar-table").hide();
    });

   $('.ttrangepicker_sec').val('')
   $('.dttrangepicker_sec').daterangepicker({
    timePicker: true,
    timePicker24Hour: true,
    locale: {
              format: 'YYYY-MM-DD HH:mm',
          }
   });
   $('.dttrangepicker_sec').val('')
   $('.popoverclass_card').popover({
    trigger: 'focus'
  })

  $(".user_logo").select2({
    templateResult: formatState1,
    templateSelection: formatState2
  });

})

$(document).ready(function() {
  $(".mandatory").on("change", function () {
    let man=($(this).attr("data-mandatory_list"))
    man=man.replaceAll("'",'"')
    if (man.length>0){
      mandatory = JSON.parse(man)
    }
    else{
      mandatory=[]
    }
    let var_list=[]
    let shape_id = $(this).attr("data-id")
    let ele_id =  $(this).attr("data-elementid")
    $(`#computationForm_${shape_id}`).find('input,select').each(function(){
      if (mandatory.includes($(this).attr('data-var_name'))){
          var_value=$(this).val()
          if (var_value!=null && var_value!=""){
            var_list.push(var_value)
          }
      }
    })
    var final_list = Array.from(new Set(var_list));
    if ((final_list.length)==(mandatory.length)){
      $(`#runModel_${shape_id}`).prop('disabled',false)
    }
    else{
      $(`#runModel_${shape_id}`).prop('disabled',true)
    }
  });
});

  $(".validation").on("change",function (){
    let condition_list = []
    let constraint_dict = {}
    let current_ans = -1
    let previous_ans = -1
    let previous_ruleset = -1
    if ($(this).attr("data-val") != "null"){
      let validation = $(this).attr("data-val")
      let custom_message = $(this).attr("data-custom_message")
      let shape_id = $(this).attr("data-id")
      if (validation.length>0){
        validation = JSON.parse(validation)
        current_ans = $(this).val()
        for (let i=0;i<validation.length;i++){
          if (validation[i]["varConst"] in constraint_dict){
            constraint_dict[validation[i]["varConst"]].push(validation[i])
          }else{
            constraint_dict[validation[i]["varConst"]] = [validation[i]]
          }
        }
        constraint_dict_copy = constraint_dict

        for(let [constraint,configs] of Object.entries(constraint_dict_copy)){

          ruleset_dict = {}
          for(let i=0;i<configs.length;i++){
            if(configs[i]["varRule"] in ruleset_dict){
              ruleset_dict[configs[i]["varRule"]].push(configs[i])
            }else{
              ruleset_dict[configs[i]["varRule"]] = [configs[i]]
            }
          }
          constraint_dict[constraint] = ruleset_dict
        }
        for(let [constraint,ruleset_configs] of Object.entries(constraint_dict)){
          temp_test = []
          for(let [ruleSet,configs] of Object.entries(ruleset_configs)){
            previous_ans = -1
            previous_ruleset = -1
            for(let i=0;i<configs.length;i++){
              column_value=$(this).val()
              var value_to_compare= configs[i]['varValue']
              var dtype=$(this).attr('type')
              if (dtype=='number'){
                if(column_value.constructor === Array){
                  column_value = column_value.map(function (x) { return parseFloat(x); });
                }else{
                  column_value = parseFloat(column_value)
                }
                if(value_to_compare.constructor === Array){
                  value_to_compare = value_to_compare.map(function (x) { return parseFloat(x); });
                }else{
                  value_to_compare = parseFloat(value_to_compare)
                }
              }
              condition = configs[i]["varCond"]
              rule_set = configs[i]["varRule"]

              if(condition == "IN"){

                if(value_to_compare.includes(column_value)){
                  current_ans = true
                }else{
                  current_ans = false
                }

              }else if(condition == "Not IN"){

                if(!(value_to_compare.includes(column_value))){
                  current_ans = true
                }else{
                  current_ans = false
                }

              }else if(condition == "Equal"){

                if(value_to_compare == column_value){
                  current_ans = true
                }else{
                  current_ans = false
                }
              }else if(condition == "Unequal"){

                if(value_to_compare != column_value){
                  current_ans = true
                }else{
                  current_ans = false
                }
              }else if(condition == "Starts"){

                if(column_value.startsWith(value_to_compare)){
                  current_ans = true
                }else{
                  current_ans = false
                }
              }else if(condition == "Neg_Start"){

                if(!(column_value.startsWith(value_to_compare))){
                  current_ans = true
                }else{
                  current_ans = false
                }
              }else if(condition == "Ends"){

                if(column_value.endsWith(value_to_compare)){
                  current_ans = true
                }else{
                  current_ans = false
                }
              }else if(condition == "Neg_End"){

                if(!(column_value.endsWith(value_to_compare))){
                  current_ans = true
                }else{
                  current_ans = false
                }
              }else if(condition == "Contains"){

                if(column_value.includes(value_to_compare)){
                  current_ans = true
                }else{
                  current_ans = false
                }
              }else if(condition == "Neg_Contains"){

                if(column_value.includes(value_to_compare)){
                  current_ans = true
                }else{
                  current_ans = false
                }
              }else if(condition == "Greater"){

                if(column_value > value_to_compare){
                  current_ans = true
                }else{
                  current_ans = false
                }
              }else if(condition == "Greater_Than"){

                if(column_value >= value_to_compare){
                  current_ans = true
                }else{
                  current_ans = false
                }

              }else if(condition == "Smaller"){

                if(column_value < value_to_compare){
                  current_ans = true
                }else{
                  current_ans = false
                }
              }else if(condition == "Smaller_Than"){

                if(column_value <= value_to_compare){
                  current_ans = true
                }else{
                  current_ans = false
                }

              }
              if(previous_ans != -1 && previous_ruleset != -1){
                if(previous_ruleset == rule_set){
                  current_ans = current_ans && previous_ans
                }else{
                  current_ans = current_ans || previous_ans
                }
                previous_ruleset = rule_set
                previous_ans = current_ans
              }else{
                previous_ans = current_ans
                previous_ruleset = rule_set
              }
            }
            temp_test.push(current_ans)
          }
          condition_list.push(temp_test.some(Boolean))
        }
        evaluate = condition_list.every(Boolean);
        if (evaluate === false){
          if (custom_message.length>0){
            Swal.fire({icon: 'error',text: custom_message})
            $(`#runModel_${shape_id}`).prop('disabled',true)
          }
          else{
            Swal.fire({icon: 'error',text: 'Validation Failed! Please enter a valid input.'})
            $(`#runModel_${shape_id}`).prop('disabled',true)
          }
        }
        else{
          $(`#runModel_${shape_id}`).prop('disabled',false)
        }
      }
    }
  })




function freezePrevcardPane (This) { // eslint-disable-line no-unused-vars
  const elementID = $(This).attr('id').replace('btnFreezePanePrevRun', '')
  if ($(`#freezeprev_left_${elementID}`).is(':checked') && $(`#freezeprev_right_${elementID}`).is(':checked')) {
    Swal.fire({icon: 'warning',text: 'Error! Kindly select only one checkbox to freeze panes.'});
  } else {
    if ($(`#freezeprev_left_${elementID}`).is(':not(:checked)') && $(`#freezeprev_right_${elementID}`).is(':not(:checked)')) {
      Swal.fire({icon: 'warning',text: 'Error! Kindly select atleast one checkbox to freeze panes.'});
    }

    if ($(`#freezeprev_left_${elementID}`).is(':checked')) {
      freezeDict2.left = parseInt(cellIndex1)
    }

    if ($(`#freezeprev_right_${elementID}`).is(':checked')) {
      freezeDict2.right = parseInt(cellColLen3 - cellIndex1 + 1)
    }

    $('.cell_highlighted').removeClass('cell_selected')
    $('.cell_highlighted').removeClass('cell_highlighted')

    const table = $(`#previousRunTable_${elementID}`).DataTable()

    new $.fn.dataTable.FixedColumns(table, // eslint-disable-line no-new
      freezeDict2
    )

    $(`#freezePrevRunCard_computation${elementID}`).modal('hide')
  }
}

function freezeRuncardPane (This) { // eslint-disable-line no-unused-vars
  const elementID = $(This).attr('id').replace('btnFreezePaneRun', '')

  if ($(`#freezerun_left_${elementID}`).is(':checked') && $(`#freezerun_right_${elementID}`).is(':checked')) {
    Swal.fire({icon: 'warning',text: 'Error! Kindly select only one checkbox to freeze panes.'});
  } else {
    if ($(`#freezerun_left_${elementID}`).is(':not(:checked)') && $(`#freezerun_right_${elementID}`).is(':not(:checked)')) {
      Swal.fire({icon: 'warning',text: 'Error! Kindly select atleast one checkbox to freeze panes. '});
    }

    if ($(`#freezerun_left_${elementID}`).is(':checked')) {
      freezeDict3.left = parseInt(cellIndex2)
    }

    if ($(`#freezerun_right_${elementID}`).is(':checked')) {
      freezeDict3.right = parseInt(cellColLen4 - cellIndex2 + 1)
    }

    $('.cell_highlighted').removeClass('cell_selected')
    $('.cell_highlighted').removeClass('cell_highlighted')

    const table = $(`#runModelTable_${elementID}`).DataTable()

    new $.fn.dataTable.FixedColumns(table, // eslint-disable-line no-new
      freezeDict3
    )

    $(`#freezeRunCard_computation${elementID}`).modal('hide')
  }
}

function unfreezePrevcardPane (This) { // eslint-disable-line no-unused-vars
  const elementID = $(This).attr('id').replace('btnFreezePanePrevRun', '')

  if ($(`#freezeprev_left_${elementID}`).is(':checked')) {
    freezeDict2.left = 0
  }

  if ($(`#freezeprev_right_${elementID}`).is(':checked')) {
    freezeDict2.right = 0
  }

  const table = $(`#previousRunTable_${elementID}`).DataTable()

  new $.fn.dataTable.FixedColumns(table, // eslint-disable-line no-new
    freezeDict2
  )

  $(`#freezePrevRunCard_computation${elementID}`).modal('hide')
}

function unfreezeRuncardPane (This) { // eslint-disable-line no-unused-vars
  const elementID = $(This).attr('id').replace('btnFreezePaneRun', '')

  if ($(`#freezerun_left_${elementID}`).is(':checked')) {
    freezeDict3.left = 0
  }

  if ($(`#freezerun_right_${elementID}`).is(':checked')) {
    freezeDict3.right = 0
  }

  const table = $(`#runModelTable_${elementID}`).DataTable()

  new $.fn.dataTable.FixedColumns(table, // eslint-disable-line no-new
    freezeDict3
  )

  $(`#freezeRunCard_computation${elementID}`).modal('hide')
}

function freezeRunscecardPane (This) { // eslint-disable-line no-unused-vars
  const elementID2 = $(This).attr('id').replace('btnFreezePaneRunsec', '')

  if ($(`#freezerunsec_left_${elementID2}`).is(':checked') && $(`#freezerunsec_right_${elementID2}`).is(':checked')) {
    Swal.fire({icon: 'warning',text: 'Kindly select only one checkbox to freeze panes.'});
  } else {
    if ($(`#freezerunsec_left_${elementID2}`).is(':not(:checked)') && $(`#freezerunsec_right_${elementID2}`).is(':not(:checked)')) {
      Swal.fire({icon: 'warning',text: 'Kindly select atleast one checkbox to freeze panes.'});
    }

    if ($(`#freezerunsec_left_${elementID2}`).is(':checked')) {
      freezeDict4.left = parseInt(cellIndex3)
    }

    if ($(`#freezerunsec_right_${elementID2}`).is(':checked')) {
      freezeDict4.right = parseInt(cellColLen5 - cellIndex3 + 1)
    }

    $('.cell_highlighted').removeClass('cell_selected')
    $('.cell_highlighted').removeClass('cell_highlighted')

    const table = $(`#runModelTable_multi_run${elementID2}`).DataTable()

    new $.fn.dataTable.FixedColumns(table, // eslint-disable-line no-new
      freezeDict4
    )

    $(`#freezeRunCard_computation${elementID2}`).modal('hide')
  }
}

function unfreezeRunscecardPane (This) { // eslint-disable-line no-unused-vars
  const elementID2 = $(This).attr('id').replace('btnFreezePaneRunsec', '')

  if ($(`#freezerunsec_left_${elementID2}`).is(':checked')) {
    freezeDict4.left = 0
  }

  if ($(`#freezerunsec_right_${elementID2}`).is(':checked')) {
    freezeDict4.right = 0
  }

  const table = $(`#runModelTable_multi_run${elementID2}`).DataTable()

  new $.fn.dataTable.FixedColumns(table, // eslint-disable-line no-new
    freezeDict4
  )

  $(`#freezeRunCard_computation${elementID2}`).modal('hide')
}

$('.run_draw_carousel').on('slid.bs.carousel', function () {
  const eID = $(this).find('.carousel-item.active').parent().attr('id').replace('MultiRunCarouselInn_', '')
  const runID = $(this).find('.carousel-item.active').attr('id').replace(`_carousel_${eID}`, '').replace('run_', '')
  $(`#runModelTable_multi_run${eID}_${runID}`).DataTable().draw()
})
function populateValue(element_id){
  $(`#identifier_column_${element_id}`).off('select2:select select2:unselect').on('select2:select select2:unselect', function () {
    $(`#comparative_column_${element_id}`).empty()
    const selIdentifier = $(this).val()
    const columns_list_comparative = JSON.parse($(`#identifier_column_${element_id}`).attr("data-output_columns"))
    for (const i in columns_list_comparative) {
      if (selIdentifier.includes(columns_list_comparative[i]) === false) {
        $(`#comparative_column_${element_id}`).append(new Option(columns_list_comparative[i], columns_list_comparative[i], false, false))
      };
    };
  })
  let data = $(this).closest("#configure_comparative_"+element_id).attr("data-data")
  if(data != undefined){
    if(data[0] = "["){
      data = JSON.parse(data);
      if($("#config_type_"+element_id).val() != "column_level"){
        let value = $("#identifier_column_"+element_id).val();
        $("#configure_parameter_"+element_id).empty()
        if(value.length > 0) {
          for(let i = 0; i < value.length; i++) {
            $("#configure_parameter_"+element_id).append(`
              <div class="col-4">
                <label>${value[i]}</label>
                <select data-column="${value[i]}" id="${value[i]}_${element_id}" class="select2" multiple>

                </select>
              </div>
            `)
            $("#configure_parameter_"+element_id).find("select").each(function(){
              $(this).select2()
            })
            $("#configure_parameter_"+element_id).find(".select2-container").css("width","");
            for(let key = 0; key < data.length; key++){
              let check = 0
              $("#configure_parameter_"+element_id).find("#"+value[i]+"_"+element_id).find(`option`).each(function() {
                if($(this).attr("value") == data[key][value[i]]){
                  check = 1
                }
              })
              if(check == 0){
                $("#configure_parameter_"+element_id).find("#"+value[i]+"_"+element_id).append(`
                  <option value="${data[key][value[i]]}">${data[key][value[i]]}</option>
                `)
              }
            }
          }
        }
      } else {
        $("#configure_parameter_"+element_id).html(`<span>Select configuration type as row level to configure parameters</span>`);
      }
    }
  }
}
function saveComparative(element_id) {
  let dic = {
    "element_id":element_id,
    "model_name":$("#configure_comparative_"+element_id).attr("data-model_name"),
  }
  dic["parameters"] = {}
  if($("#config_type_"+element_id).val() != "column_type") {
    let value = $("#identifier_column_"+element_id).val();
    for(let i = 0; i < value.length; i++){
      dic["parameters"][value[i]] = $("#configure_parameter_"+element_id).find("#"+value[i]+"_"+element_id).val();
    }
  }
  dic["comparative"] = $("#comparative_column_"+element_id).val()
  dic["identifier"] = $("#identifier_column_"+element_id).val()

  $.ajax({
    url:`/users/${urlPath}/dynamicVal/`,
      data: {
        'operation':'addComparative',
        'model_name':dic["model_name"],
        "data": JSON.stringify(dic)
      },
      type: 'POST',
      dataType: "json",
      success: function (data) {
        Swal.fire({icon: 'success',text: 'Comparative analysis saved successfully!'});
      },
      error: ()=>{
        Swal.fire({icon: 'error',text: 'Error! Failure in Saving the Comparative analysis. Please check and try again.'});
      }
    });
}
function closeScenario(element_id){
  $("#configure_comparative_"+element_id).css("display","none");
  $("#save_comparative_"+element_id).parent().css("display","none");
}

function datatablesFuncL3(id) {
  $('#'+id).DataTable( {
    "autoWidth": true,
    "scrollY": "40vh",
    "scrollCollapse": true,
    "order":[[ 1, 'desc' ]],
    "scrollX": true,
    // "serverSide":true,
    orderCellsTop: true,
    //fixedHeader: true,
    responsive: true,
    // stateSave: true,
    "deferRender": true,
    "paging": true,
    "searching": true,
    "info": true,
    "lengthMenu": [[1, 5, 50, -1], [1, 5, 50, "All"]],
    "stripeClasses": false,
    "pageLength": 50,
    dom: 'lfBrtip',
    "sScrollX": "100%",
    "scrollX": true,
    buttons: [
          {
              extend: 'collection',
              text: 'Export',
              buttons: [
              {
                  extend: 'copy', title: '', exportOptions: {
                  }
              },
              {
                  extend: 'excel', title: '', exportOptions: {
                  }
              },
              {
                  extend: 'csv', title: '', exportOptions: {
                  }
              },
              {
                  extend: 'pdf', title: '', exportOptions: {
                  }
              },
              ],
          },

        ],
        columnDefs: [
        {
            targets: "_all",
            className: 'dt-center allColumnClass all'
        },
        {
            targets: 0,
            width: "20%",
            className: 'noVis'
        }
    ],

    }).columns.adjust();
  }
function viewDetail() {
  var transaction_id = $(this).attr('data-t_id');
  $('#flowDetail').find('.indDetail').css('display','none');

  $.ajax({
        url:`/users/${urlPath}/FlowMonitor/`,
        data: {
        "operation":"fetchFlowDetail",
        "transaction_id":transaction_id,
        },
        type: "POST",
        dataType: "json",
        success: function (data) {
            $('#flowDetailBody').find('.row').empty();
            var color
            for(let i = 0; i < data.data.length; i++) {
              $('#flowDetailBody').find('.row').append(`${shapes[data.data[i].tab_type]}`);
              if(data.data[i]["current_status"] == "Fail"){
                color = "red"
              } else if(data.data[i]["current_status"] == "Pass"){
                color = "green"
              } else if(data.data[i]["current_status"] == "Not started" || data.data[i]["current_status"] == "Not required" || data.data[i]["current_status"] == "Ongoing"){
                color = "#FFD700"
              }
              if(i != (data.data.length - 1)) {
                $('#flowDetailBody').find('.row').append(`${shapes1["arrow"]}`);
                $('#flowDetailBody').find('.row').find(".col-1").eq(-1).children().css('color',`${color}`)
              }
              $('#flowDetailBody').find('.row').find(".col-2").eq(-1).find('path').attr('stroke',`${color}`)
              $('#flowDetailBody').find('.row').find(".col-2").eq(-1).children().css('border-color',`${color}`)
              $('#flowDetailBody').find('.row').find(".col-2").eq(-1).children().css('text-align',`center`)
              if(color != "green"){
                $('#flowDetailBody').find('.row').find(".col-2").eq(-1).attr('data-link',`${data.data[i]["subprocess"]}`)
              }
              $('#flowDetailBody').find('.row').find(".col-2").eq(-1).attr('data-title',`${data.data[i]["detailed_status"]}`)
              $('#flowDetailBody').find('.row').find(".col-2").eq(-1).attr('data-status',`${data.data[i]["current_status"]}`)
              $('#flowDetailBody').find('.row').find(".col-2").eq(-1).attr('data-name',`${data.data[i]["element_name"]}`)
              $('#flowDetailBody').find('.row').find(".col-2").eq(-1).attr('data-date',`${data.data[i]["modified_date"]}`)
              $('#flowDetailBody').find('.row').find(".col-2").eq(-1).attr('onclick',`giveDetail.call(this)`)
              if(data.data[i].tab_type != "decision_box"){
                $('#flowDetailBody').find('.row').find(".col-2").eq(-1).find('.name').html(data.data[i]["element_name"])
              }
            }

        },
        failure: function () {
          Swal.fire({icon: 'warning',text:"No custom homepage exists" });
        },
    });
}
function giveDetail() {
  $(this).closest('.modal-body').find('.indDetail').css('display','block');
  let detail = $(this).attr('data-title');
  let status = $(this).attr('data-status');
  let name = $(this).attr('data-name');
  let link = $(this).attr('data-link')
  let date = $(this).attr("data-date")
  if (link == undefined){
    link = ""
  } else {
    link = `<a data-toggle="tooltip" title="Go to subprocess" href="/users/${link}/" style="color:var(--primary-color)">Sub-process</a>`
  }
  $('#flowDetail').find('#flowDetailTable').find('table').find('tbody').empty();
  html = `
    <tr>
    <td>${name}</td>
    <td style="padding-left:10px;">${status}</td>
    <td style="width:70%"><div style='white-space: normal;width: 100%;'>${detail}</div></td>
    <td>${date.replace("T"," ")}</td>
    </tr>
  `
  $('#flowDetail').find('#flowDetailTable').find('table').find('tbody').append(html)
}
function showTransactions(element_id) {
  var thisHtml = $(this).html()
  $(this).html(`<i class="fa fa-circle-notch fa-spin"></i>`)
  let thiss = $(this)

  $.ajax({
    url:`/users/${urlPath}/dynamicVal/`,
    data: {
    "operation":"filterFlowDetailL3",
    "transaction_id":"",
    "prg_code": "",
    "pr_code": "",
    "element_id": element_id
    },
    type: "POST",
    dataType: "json",
    success: function (data) {
      thiss.html(thisHtml)
      html = `<table id="flowMonitorTableL3" class="display" style="width:100%;overflow-x: scroll;overflow-y:scroll;">
        <thead style="border-bottom:1px solid var(--primary-color)">
        <tr>
            <th>Transaction id</th>
            <th>Created date</th>
            <th>View detail</th>
            <th>Flow status</th>
        </tr>
        </thead>
        <tbody style="height: 80px;border-bottom:1px solid var(--primary-color);">`
      if(data.data.length > 0) {
        transaction_id = data.data[0]["transaction_id"]
        var fail = 0;
        var success = 0;
        var not_started = 0
        data.data.push({"transaction_id":"yoyoy"})
        for(let i = 0; i < data.data.length; i++) {
            html_ = `
            `
            t_id = data.data[i]["transaction_id"]
            if(data.data[i+1]){
                if(data.data[i]["transaction_id"] == data.data[i+1]["transaction_id"]) {
                    if (Object.values(data.data[i]).includes("Fail")) {
                        html_ = `<i class="fa fa-close" style="color:red"></i>`
                        fail = 1;
                    } else if (Object.values(data.data[i]).includes("Not started") || Object.values(data.data[i]).includes("Not required")) {
                        html_ = `<i class="" style="color:yellow"></i>`
                        not_started = 1;
                    } else if (Object.values(data.data[i]).includes("Pass")) {
                        success = 1;
                    }

                } else {
                    html = html + `<tr>`
                      if (Object.values(data.data[i]).includes("Fail")) {
                        html_ = `<i class="fa fa-close" style="color:red"></i>`
                        fail = 1;
                    } else if (Object.values(data.data[i]).includes("Not started") || Object.values(data.data[i]).includes("Not required")) {
                        html_ = `<i class="" style="color:yellow"></i>`
                        not_started = 1;
                    } else if (Object.values(data.data[i]).includes("Pass")) {
                        success = 1;
                    }
                    if (fail == 1) {
                      html_ = `<i class="fa fa-close" style="color:red"></i>`
                    } else if(not_started == 1) {
                      html_ = `<i class="fa fa-dot-circle-o" style="color:#FFD700"></i>`
                    } else if(success == 1) {
                      html_ = `<i class="fa fa-check" style="color:green"></i>`
                    }
                    fail = 0
                    success = 0
                    not_started = 0
                    html = html + `
                        <td>${data.data[i]["transaction_id"]}</td>
                        <td>${data.data[i]["created_date"].replace("T"," ")}</td>
                        <td onclick="viewDetail.call(this)" data-t_id="${data.data[i]["transaction_id"]}" data-toggle="modal" data-target="#flowDetail" style="cursor:pointer">View detail</td>
                        <td>${html_}</td>
                    `
                  }
                  transaction_id = data.data[i]["transaction_id"]

                }
                  }
                  if($("#card0").find('#prCode').val() == "") {
                    $('#card0').find('#prCode').empty()
                    $('#card0').find('#prCode').append(`<option value="">Sub-process</option>`)
                    for(let [key,value] of Object.entries(data.code)){
                      if(!key.includes("Prg")) {
                        $('#card0').find('#prCode').append(`<option value="${key}">${value}</option>`)
                      }
                    }
                  }
                  if($("#card0").find('#prgCode').val() == "") {
                    $('#card0').find('#prCode').empty()
                    $('#card0').find('#prCode').append(`<option value="">Sub-process</option>`)
                  }

                }
                $('#flowMonitorTableL3_wrapper').remove()
                $('#flowMonitorTableL3').remove()
                $('#flowMonitorModalL3').find(".modal-body").empty()
                html = html + '</tr></tbody></table>';
                $('#flowMonitorModalL3').find(".modal-body").append(html);
                $('#flowMonitorTableL3').find('tbody').each(function(){
                    var list = $(this).children('tr');
                    $(this).html(list.get().reverse())
                });
                $('#flowMonitorModalL3').modal("show")
                datatablesFuncL3('flowMonitorTableL3')
    },
      failure: function () {
        thiss.html(thisHtml)
        Swal.fire({icon: 'warning',text:"No custom homepage exists" });
      },
  });
}

var findreplaceData // eslint-disable-line no-var
// eslint-disable-next-line no-unused-vars
function findReplaceButton(obj) {
  // eslint-disable-line no-unused-vars
  const elementID = obj.getAttribute('data-elementID')
  $(`#findtext${elementID}`).empty()
  $(`#selectcase${elementID}`).prop('disabled', false)
  $(`#find${elementID}`).css('display', 'none')
  $(`#replace${elementID}`).css('display', 'none')
  $(`.text_based_div${elementID}`).css('display', 'none')
  $(`#findlabel${elementID}`).css('display', 'none')
  $(`#findlistL3${elementID}`).empty()
  $(`#replacelistL3${elementID}`).empty()
  $(`#replacelabel${elementID}`).css('display', 'none')
  $(`#find_replace_modal_${elementID}`).modal('show')
  $(`#findreplacesave_${elementID}`).attr('confirmed', 'False')
  $('#text_basedip_' + elementID).prop('checked', true);
  const itemCode = $(this).attr("pr_code");
  $(`#find${elementID}`).val('')
  $(`#replace${elementID}`).val('')
  const modelName = obj.getAttribute('data-table-name')
  $.ajax({
    url: `/users/${urlPath}/${itemCode}/`,
    data: { model_name: modelName, element_id: elementID, operation: 'get_listview_column' },
    type: 'POST',
    dataType: 'json',
    success: function (data) {
      findreplaceData = data
      $(`#selectcolumn${elementID}`).empty()
      $(`#selectreplacecolumn${elementID}`).empty()
      $(`#find${elementID}`).empty()
      $(`#replace${elementID}`).empty()
      $(`#selectcolumn${elementID}`).append(
        '<option value="" selected disabled>Select Column</option>'
      )
      $(`#selectreplacecolumn${elementID}`).append(
        '<option value="" selected disabled>Select Column</option>'
      )
      $.each(Object.keys(data), function (key, value) {
        const ftype = data[value].internal_type
        const vname = data[value].verbose_name
        if (!["FileField", "UniqueIDField"].includes(ftype)) {
          $(`#selectcolumn${elementID}`).append(
            `<option data-type="${ftype}" name="${value}" value="${vname}">${vname}</option>`
          )
          $(`#selectreplacecolumn${elementID}`).append(
            `<option data-type="${ftype}" name="${value}" value="${vname}">${vname}</option>`
          )
        }
      })
    },
    error: function () {
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    },
  })
}

function selectcasechange(obj) {
  const elementID = obj.getAttribute('data-elementID')
  if ($(obj).val() == "Entire Column") {
    $(`#findlabel${elementID}`).css('display', 'none')
    $(`#findlistL3${elementID}`).css('display', 'none')
    $(`.text_based_div${elementID}`).css('display', 'none')
  }
  else {
    $(`#findlabel${elementID}`).css('display', 'block')
    $(`#findlistL3${elementID}`).css('display', 'block')
    $(`.text_based_div${elementID}`).css('display', 'flex')
  }
}

function closeviewdetails(elementID) {
  $(`#view_details_modal_${elementID}`).modal('hide');
}

function findreplacemultiselect(obj) {
  var element_id = $(obj).attr("element_id");
  var msdata = $(obj).attr("data-col");
  var msdata_name = JSON.parse($(obj).attr("data-name"));

  var masterColumn = $(obj).attr("data-masterColumn");
  var add_cols = JSON.parse($(obj).attr("data-add"));
  var thead = `<tr><td>${masterColumn}</td>`;
  for (i in add_cols) { thead += `<td>${add_cols[i]}</td>` }
  thead += '</tr>'
  var tbody = "";
  for (let i = 0; i < $(`#formModalListL${element_id}_${msdata}`).find('.ioL').length; i++) {
    if (Object.keys(msdata_name).includes($('#masterListTablei'+element_id + '_' + msdata).find('tbody').find('tr').eq(i).find('td').eq(-1).text())) {
      tbody += `<tr>`;
      for (let j = 1; j < $('#masterListTablei'+element_id + '_' + msdata).find('tbody').find('tr').eq(0).find("td").length - 1; j++) {
        rr = $('#masterListTablei'+element_id + '_' + msdata).find('tbody').find('tr').eq(i).find('td').eq(j).text();
        rr = rr.trim()
        tbody += `<td>${rr}</td>`
      }
      tbody += '</tr>'
    }
  }
  $(`#view_details_modal_${element_id}_wrapper`).empty();
  $(`#view_details_modal_${element_id}_wrapper`).append(`
  <div class="overflow:auto;">
  <table style="width:100%; max-height:250px" class="table-responsive">
  <thead>
  ${thead}
  </thead>
  <tbody>
  ${tbody}
  </tbody>
  </table></div>`)

  $(`#view_details_modal_${element_id}`).modal('show');
  $(`#view_details_modal_${element_id}_wrapper`).find("table").DataTable({
    autoWidth: false,
    scrollCollapse: true,
    sScrollXInner: "100%",
    ordering: false,
    orderCellsTop: true,
    responsive: true,
    colReorder: {
      fixedColumnsLeft: 1,
    },
    stateSave: true,
    deferRender: true,
    paging: true,
    lengthMenu: [
      [1, 5, 50, -1],
      [1, 5, 50, "All"],
    ],
    stripeClasses: false,
    pageLength: 50,
    dom: "lfBrtip",
    buttons: [],
    columnDefs: [
      {
        targets: "_all",
        className: "dt-center allColumnClass all",
      },
    ],
  });

}

// eslint-disable-next-line no-unused-vars
function findreplacechange(obj) {
  // eslint-disable-line no-unused-vars
  const elementID = obj.getAttribute('data-elementID')
  const datatype = $('option:selected', `#selectcolumn${elementID}`).attr(
    'data-type'
  )
  const dvalue = $('option:selected', `#selectcolumn${elementID}`).attr('value')
  const columnName = $('option:selected', `#selectcolumn${elementID}`).attr(
    'name'
  )
  $(`#selectreplacecolumn${elementID}`).val(dvalue).trigger("change")
  $(`#findlabel${elementID}`).css('display', 'block')
  $(`#replacelabel${elementID}`).css('display', 'block')
  $(`.text_based_div${elementID}`).css('display', 'flex')
  $(`#findlistL3${elementID}`).empty()
  $(`#find${elementID}`).val('')
  let settype;
  if (String(datatype) === 'ForeignKey') {
    settype = 'text'
    $(`#findlistL3${elementID}`).append(`
        <select data-elementID="${elementID}" id="find${elementID}" form="columnform" class="form-control select2">
        </select>
        <script>$("#find${elementID}").select2()</script>
        `)
    $.each(Object.keys(findreplaceData), function (key, value) {
      if (String(findreplaceData[value].internal_type) === 'ForeignKey') {
        const choice = findreplaceData[value].Choices
        for (const [k, v] of Object.entries(choice)) {
          $(`#find${elementID}`).append(
						`<option name="${k}" value="${v}">${v}</option>`
          )
        }
      }
    })
  } else if (String(datatype) === 'MultiSelect') {
    $(`#findlistL3${elementID}`).append(`
        <select data-elementID="${elementID}" id="find${elementID}" form="columnform" class="form-control select2">
        </select>
        <script>$("#find${elementID}").select2({tags: true})</script>
        `)
        for (let i = 0; i < $(`#formModalListL${elementID}_${columnName}`).find('.ioL').length; i++) {
            el = $('#masterListTablei'+elementID + '_' + columnName).find('tbody').find('tr').eq(i).find('td');
            idr = el.eq(-1).text().trim();
            vdr = el.eq(1).text().trim();
            $(`#find${elementID}`).append(`
            <option value=${idr}>${vdr}</option>`)
          }
  } else {
    if (String(datatype) === 'CharField' || String(datatype) === 'TextField' || String(datatype) === 'URLField') {
      settype = 'text'
    } else if (String(datatype) === 'DateTimeField') {
      settype = 'datetime-local'
      $(`#find${elementID}`).attr('step', '1')
      $(`#find${elementID}`).addClass('datetimepickerinput form-control')
    } else if (String(datatype) === 'DateField') {
      settype = 'date'
      $(`#find${elementID}`).attr('step', '1')
      $(`#find${elementID}`).addClass('datetimepickerinput form-control')
    } else if (String(datatype) === 'TimeField') {
      settype = 'time'
      $(`#find${elementID}`).attr('step', '1')
      $(`#find${elementID}`).addClass('datetimepickerinput form-control')
    } else {
      settype = 'number'
    }

    $(`#findlistL3${elementID}`).append(`
      <input type="${settype}" step="1" class="form-control" id="find${elementID}">
      `)
  }
  if ($(`#selectcase${elementID}`).val() == "Entire Column") {
    $(`#findlabel${elementID}`).css('display', 'none')
    $(`#findlistL3${elementID}`).css('display', 'none')
    $(`.text_based_div${elementID}`).css('display', 'none')
  }
  else {
    $(`#findlabel${elementID}`).css('display', 'block')
    $(`#findlistL3${elementID}`).css('display', 'block')
    $(`.text_based_div${elementID}`).css('display', 'flex')
  }

  if (["IntegerField","BigIntegerField", "FloatField"].includes(datatype)) {
    for (let inx = 0; inx <= 12; inx++) {
      $(`#selectcase${elementID}`).children().eq(inx).prop('disabled', false)
    }
  }
  else if(['DateTimeField','TimeField', 'DateField'].includes(datatype)) {
    $(`#selectcase${elementID}`).val('Equal to').change()
    $(`#selectcase${elementID}`).children().eq(3).prop('disabled', false)
    $(`#selectcase${elementID}`).children().eq(4).prop('disabled', false)
    $(`#selectcase${elementID}`).children().eq(5).prop('disabled', false)
    $(`#selectcase${elementID}`).children().eq(6).prop('disabled', false)
    $(`#selectcase${elementID}`).children().eq(7).prop('disabled', true)
    $(`#selectcase${elementID}`).children().eq(8).prop('disabled', true)
    $(`#selectcase${elementID}`).children().eq(9).prop('disabled', true)
    $(`#selectcase${elementID}`).children().eq(10).prop('disabled', true)
    $(`#selectcase${elementID}`).children().eq(11).prop('disabled', true)
    $(`#selectcase${elementID}`).children().eq(12).prop('disabled', true)
  }
  else if (!['DateTimeField','TimeField','DateField'].includes(datatype)) {
    $(`#selectcase${elementID}`).children().eq(3).prop('disabled', true)
    $(`#selectcase${elementID}`).children().eq(4).prop('disabled', true)
    $(`#selectcase${elementID}`).children().eq(5).prop('disabled', true)
    $(`#selectcase${elementID}`).children().eq(6).prop('disabled', true)
    $(`#selectcase${elementID}`).children().eq(7).prop('disabled', false)
    $(`#selectcase${elementID}`).children().eq(8).prop('disabled', false)
    $(`#selectcase${elementID}`).children().eq(9).prop('disabled', false)
    $(`#selectcase${elementID}`).children().eq(10).prop('disabled', false)
    $(`#selectcase${elementID}`).children().eq(11).prop('disabled', false)
    $(`#selectcase${elementID}`).children().eq(12).prop('disabled', false)
  }
}

// eslint-disable-next-line no-unused-vars
function replacechange(obj) {
  // eslint-disable-line no-unused-vars
  const elementID = obj.getAttribute('data-elementID')
  const datatype = $('option:selected', `#selectreplacecolumn${elementID}`).attr(
    'data-type'
  )
  const dvalue = $('option:selected', `#selectreplacecolumn${elementID}`).attr('value')
  const columnName = $('option:selected', `#selectcolumn${elementID}`).attr(
    'name'
  )
  $(`#replacelabel${elementID}`).css('display', 'block')
  $(`#replacelistL3${elementID}`).empty()
  $(`#replace${elementID}`).val('')
  let settype;
  if (String(datatype) === 'ForeignKey') {
    settype = 'text'
    $(`#replacelistL3${elementID}`).append(`
        <select data-elementID="${elementID}" id="replace${elementID}" form="columnform" class="form-control select2">
        </select>
        <script>$("#replace${elementID}").select2()</script>
        `)
    $.each(Object.keys(findreplaceData), function (key, value) {
      if (String(findreplaceData[value].internal_type) === 'ForeignKey') {
        const choice = findreplaceData[value].Choices
        for (const [k, v] of Object.entries(choice)) {
          $(`#replace${elementID}`).append(
						`<option name="${k}" value="${v}">${v}</option>`
          )
        }
      }
    })
  } else if (String(datatype) === 'MultiSelect') {
    $(`#replacelistL3${elementID}`).append(`
        <select data-elementID="${elementID}" id="replace${elementID}" form="columnform" class="form-control select2">
        </select>
        <script>$("#replace${elementID}").select2()</script>
        `)
        for (let i = 0; i < $(`#formModalListL${elementID}_${columnName}`).find('.ioL').length; i++) {
            el = $('#masterListTablei'+elementID + '_' + columnName).find('tbody').find('tr').eq(i).find('td');
            idr = el.eq(-1).text().trim();
            vdr = el.eq(1).text().trim();
            $(`#replace${elementID}`).append(`
            <option value=${idr}>${vdr}</option>`)
          }

  } else {
    if (String(datatype) === 'CharField' || String(datatype) === 'TextField' || String(datatype) === 'URLField') {
      settype = 'text'
    } else if (String(datatype) === 'DateTimeField') {
      settype = 'datetime-local'
      $(`#replace${elementID}`).attr('step', '1')
      $(`#replace${elementID}`).addClass('datetimepickerinput form-control')
    } else if (String(datatype) === 'DateField') {
      settype = 'date'
      $(`#replace${elementID}`).attr('step', '1')
      $(`#replace${elementID}`).addClass('datetimepickerinput form-control')
    } else if (String(datatype) === 'TimeField') {
      settype = 'time'
      $(`#replace${elementID}`).attr('step', '1')
      $(`#replace${elementID}`).addClass('datetimepickerinput form-control')
    } else {
      settype = 'number'
    }

    $(`#replacelistL3${elementID}`).append(`
        <input type="${settype}" step="1" class="form-control" id="replace${elementID}">
        `)
  }


  if (["IntegerField","BigIntegerField", "FloatField"].includes(datatype)) {
    for (let inx = 0; inx <= 12; inx++) {
      $(`#selectcase${elementID}`).children().eq(inx).prop('disabled', false)
    }
  }
  else if(['DateTimeField','TimeField', 'DateField'].includes(datatype)) {
    $(`#selectcase${elementID}`).val('Equal to').change()
    $(`#selectcase${elementID}`).children().eq(3).prop('disabled', false)
    $(`#selectcase${elementID}`).children().eq(4).prop('disabled', false)
    $(`#selectcase${elementID}`).children().eq(5).prop('disabled', false)
    $(`#selectcase${elementID}`).children().eq(6).prop('disabled', false)
    $(`#selectcase${elementID}`).children().eq(7).prop('disabled', true)
    $(`#selectcase${elementID}`).children().eq(8).prop('disabled', true)
    $(`#selectcase${elementID}`).children().eq(9).prop('disabled', true)
    $(`#selectcase${elementID}`).children().eq(10).prop('disabled', true)
    $(`#selectcase${elementID}`).children().eq(11).prop('disabled', true)
    $(`#selectcase${elementID}`).children().eq(12).prop('disabled', true)
  }
  else if (!['DateTimeField','TimeField','DateField'].includes(datatype)) {
    $(`#selectcase${elementID}`).children().eq(3).prop('disabled', true)
    $(`#selectcase${elementID}`).children().eq(4).prop('disabled', true)
    $(`#selectcase${elementID}`).children().eq(5).prop('disabled', true)
    $(`#selectcase${elementID}`).children().eq(6).prop('disabled', true)
    $(`#selectcase${elementID}`).children().eq(7).prop('disabled', false)
    $(`#selectcase${elementID}`).children().eq(8).prop('disabled', false)
    $(`#selectcase${elementID}`).children().eq(9).prop('disabled', false)
    $(`#selectcase${elementID}`).children().eq(10).prop('disabled', false)
    $(`#selectcase${elementID}`).children().eq(11).prop('disabled', false)
    $(`#selectcase${elementID}`).children().eq(12).prop('disabled', false)
  }
}

function checkRequired() {

  let inpReq = $(this).parent().parent().parent().find('.carousel-item.active').find('input,textarea,select').filter(':visible')
  let id = ""
  let flag_submit = 0
  try{
     id = $(this).attr("id").replace("savebutton_","")
     flag_submit = 1
     $('#savebutton_' + id).attr("type","button")
     $('#savebutton_' + id).attr("name","button1")
  } catch(err){
     id = $(this).attr("href").replace("#carouselExampleIndicators","")
  }


  let flag = 0
  let flag2 = 0
  let minCount = 0
  let minNoCols = 0
  let minNoColTotal = 0
  let colsfire = []
  let rows_left = 0

  let all_v_present = {}
  let minDict = $(this).attr("data_min_fields")
  if(minDict != undefined){
    minDict = JSON.parse(minDict)
  }else{
    minDict = {}
  }
  let rest_cols = []
  for(let [key,value] of Object.entries(minDict)){
    for(let k=0; k<value["fields"].length; k++){
      rest_cols.push(value["fields"][k])
    }
    minNoColTotal = minNoColTotal + parseInt(value["no_req_fields"])

  }
  if(Object.keys(minDict).length > 0){
    ind = $(this).parent().parent().parent().find('.carousel-item.active').index() + 1
    minNoCols = parseInt(minDict[ind]["no_req_fields"])

    for(let i=0;i<inpReq.length;i++){
      let rqVal = $(inpReq[i]).val()
      let col = $(inpReq[i]).attr("data-field_name");

      if (rqVal == "" || rqVal == null){
        if(Object.values(minDict[ind]["fields"]).length > 0){
          if(Object.values(minDict[ind]["fields"]).includes(String(col))){
            if(minCount >= minNoCols){
              flag2 = 0
              break;
            }else{
              flag2 = 1
              colsfire.push(col)
            }
            $(this).removeAttr('data-slide')
          }
        }else{
          if(minCount >= minNoCols){
            flag2 = 0
            break;
          }else{
            flag2 = 1
            colsfire.push(col)
          }
          $(this).removeAttr('data-slide')
        }
      }
      else{
        if(Object.values(minDict[ind]["fields"]).length > 0){
          if(Object.values(minDict[ind]["fields"]).includes(String(col))){
            minCount = minCount + 1
          }
        }else{
          minCount = minCount + 1
        }
        if(flag2 == 0){
          if ($.trim($(this).text()) == "Next"){
            $(this).attr('data-slide','next')
          }else{
            $(this).attr('data-slide','prev')
          }
        }
      }

    }

    if(minCount >= minNoCols){
      flag2 = 0
      if ($.trim($(this).text()) == "Next"){
        $(this).attr('data-slide','next')
      }else{
        $(this).attr('data-slide','prev')
      }
    }else{
      Swal.fire({icon: 'warning',text:`Kindly fill in the value for field atleast ${minNoCols} !!!` });
    }

  let inpReq2 = $(this).parent().parent().parent().find('.carousel-item').find('input,textarea,select')
  for(let i=0;i<inpReq2.length;i++){
    let rqVal = $(inpReq2[i]).val()
    let col = $(inpReq2[i]).parent().parent().parent().find('label').text().replace('*','').trim();
    all_v_present[col] = rqVal
  }

  for(let [k1,v1] of Object.entries(all_v_present)){
    if(v1 != ""){
      rows_left = rows_left + 1
      colsfire.push(k1)
    }
  }

  if(flag2 == 0 && (rows_left >= minNoColTotal)){
      const type = $(`#savebutton_${id}`).val()
      let currentUrl = window.location.href
      if (currentUrl.includes(`#carouselExampleIndicators${id}`)){
        currentUrl = currentUrl.replace(`#carouselExampleIndicators${id}`,"")
      }
      let idEle = $(`#savebutton_${id}`).attr('id').split('whiteSpacewrap')[1]
      idEle = 'whiteSpacewrap' + idEle
      // eslint-disable-next-line camelcase
      if (item_code_list) {
        // eslint-disable-next-line camelcase
        for (let j = 0; j < item_code_list.length; j++) {
          // eslint-disable-next-line camelcase
          currentUrl = '/users/' + item_code_list[j][idEle] + '/'
        }
      }
      const submitFormUrl = currentUrl + 'create/'
      const submitFormDraftUrl = currentUrl + 'createDraft/'
      if (String(type) === 'Save') {
        $(`#savebutton_${id}`).attr('formaction', submitFormUrl)
      } else if (String(type) === 'Save as Draft') {
        $(`#savebutton_${id}`).attr('formaction', submitFormDraftUrl)
      }

    $('#savebutton_' + id).attr("type","submit")
    $('#savebutton_' + id).attr("name","submit")
  }else{
    if(flag_submit == 1){
      Swal.fire({icon: 'warning',text:`Kindly fill in the values for required fields !!` });
    }
  }
}

  for(let i=0;i<inpReq.length;i++){
    let requiredVar = $(inpReq[i]).prop('required')
    let classCheck = $(inpReq[i]).attr('data-car_mand')
    let labelName = $(inpReq[i]).parent().parent().find('label').text().replace('*','')

    if (classCheck == "restrict_mand"){
      if(requiredVar){
        let rqVal = $(inpReq[i]).val()
        if (rqVal == ""){
          Swal.fire({icon: 'warning',text:`Kindly fill in the value for mandatory field ${labelName} !!` });
          $(this).removeAttr('data-slide')
          flag = 1
        }
        else{
          if(flag == 0){
            if ($.trim($(this).text()) == "Next"){
              $(this).attr('data-slide','next')
            }else{
              $(this).attr('data-slide','prev')
            }
          }
        }
      }else{
        if(flag == 0 && flag2 == 0){
          if ($.trim($(this).text()) == "Next"){
            $(this).attr('data-slide','next')
          }else{
            $(this).attr('data-slide','prev')
          }
        }
      }
    }
  }
}

async function listviewPdfEditView(obj){
  const elementId = obj.getAttribute('data-element-id')
  $(obj).html(`<i class="fa fa-circle-notch fa-spin"></i>`)
  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
    await sleep(500);
    var wid = document.getElementById(`edit_list_preview_body${elementId}`).offsetWidth
    var hei = document.getElementById(`edit_list_preview_body${elementId}`).offsetHeight
    let tabtitle = $(`#${elementId}-tab`).find('.span_content_editable').text()
      await html2canvas(document.getElementById(`edit_list_preview_body${elementId}`), { allowTaint: true }).then(function(canvas) {

        var imgData = canvas.toDataURL('image/png');
        var doc = new jsPDF("l","px",[wid,hei]);
        doc.addImage(imgData, 'PNG',0,0,doc.internal.pageSize.width, doc.internal.pageSize.height);
        doc.save(`${tabtitle}.pdf`);
        $(obj).html(`Download Pdf`)
  })


}
function editPreviewMode(obj){
  const elementId = obj.getAttribute('data-element-id')
  let dataId = obj.closest('.modal-body').getAttribute('id')
  dataId = dataId.replace('modalBody','')

  modalHtml = '<div class="form-row">'
  $(`#modalBody${dataId}`).find('.form-row').each(function(){
    modalHtml += $(this).html()
  })
  modalHtml = modalHtml + "</div>"
  let tabtitle = $(`#${elementId}-tab`).find('.span_content_editable').text()
  $(`#edit_list_preview_header${dataId}`).empty()
  $(`#edit_list_preview_header${dataId}`).append(`<h5 class="modal-title">${tabtitle}</h5>
  <button type="button" class="close" data-dismiss="modal" aria-label="Close">
    <span aria-hidden="true">&times;</span>
  </button>`)

  let dictOfInputvalues = {}
  let arrayOfInputs = $(`#modalBody${dataId}`).find('.form-row').find("input , select , textarea").each(function(){
    dictOfInputvalues[$(this).attr('id')] = $(this).val()
  })


  $(`#edit_list_preview_body${dataId}`).empty();
  $(`#edit_list_preview_body${dataId}`).append(modalHtml);
  $(`#edit_list_preview_body${dataId}`).css('pointer-events', 'none');
  for (var key in dictOfInputvalues){
    $(`#edit_list_preview_body${dataId}`).find("#"+key).removeAttr("onclick")
    $(`#edit_list_preview_body${dataId}`).find("#"+key).val(dictOfInputvalues[key]).trigger("change")
  }
  $(`#edit_list_preview_body${dataId}`).find("input , select , textarea").each(function(){
    $(this).attr("id",$(this).attr("id") + "modal")
    $(this).parent().find(".select2-container").css("width","");
  });

    $(`#edit_list_preview_modal${dataId}`).find(`#edit_list_preview_footer${dataId}`).empty()
    $(`#edit_list_preview_modal${dataId}`).find(`#edit_list_preview_footer${dataId}`).append(`
  <button type="button" class="btn btn-primary btn-xs mx-2 rounded px-2" data-dismiss="modal" id='savebuttonpreview_${dataId}'>Confirm</button>
  <button onclick = "listviewPdfEditView(this)" type="button" data-element-id="${dataId}" class="btn btn-primary btn-xs mx-2 rounded px-2">Download Pdf</button>
  <button type="button" class="btn btn-primary btn-xs mx-2 rounded px-2" data-dismiss="modal">Close</button>
  `)
  $(`#edit_list_preview_modal${dataId}`).modal('show')

  $(`#savebuttonpreview_${dataId}`).on('click', function () {

    $(`#savebutton_${elementId}`).attr('type', 'submit')
    $(`#savebutton_${elementId}`).removeAttr('onclick')
    $(`#savebutton_${elementId}`).click()
  })
}

function checkValidationNow(){
  let tableName = $(this).attr("data-tablename")
  let fieldVal = $(this).val()
  if ((fieldVal !== "") && (fieldVal !== "---") && (fieldVal !== "----") && (fieldVal !== "{}") && fieldVal) {
    let process_id = $(this).attr("id").split('_').slice(-1)[0]
    let fieldName = $(this).attr("id").replace(`id_`,"").replace(`_${process_id}`,"")

    customdict = $(`#customValidationList1${process_id}`).val()
    if (customdict){
      customdict = customdict
    }else{
      customdict = ""
    }

    if(fieldVal.constructor === Array){
      fieldVal = JSON.stringify(fieldVal)
    }

    $(this).attr("title","")
    $.ajax({
          url:`/users/${urlPath}/dynamicVal/`,
          data: {
          "operation":"check_validations",
          "tableName":tableName,
          "fieldName":fieldName,
          "fieldVal":fieldVal,
          "process_id":process_id,
          "customdict":customdict,
          },
          type: "POST",
          dataType: "json",
          success: function (data) {

            if(data.error == "no"){
              if ($(`#${data.ele_id}`).hasClass('select2')){
                $(`#${data.ele_id}`).parent().find('span').find(".select2-selection.select2-selection--single").css("background-color","#dbf0db")
              }else if($(`#${data.ele_id}`).attr('data-fieldtype') == "MultiselectField"){
                let mulid = $(`#${data.ele_id}`).attr('data-connectedselectfield')
                $(`#${mulid}`).parent().find(".select2-selection--multiple").css("background-color","#dbf0db")
              }else if($(`#${data.ele_id}`).is(':-webkit-autofill')){
                var clone = $(`#${data.ele_id}`).clone(true, true);
                $(`#${data.ele_id}`).after(clone);
                $(`#${data.ele_id}`).remove();
                $(`#${data.ele_id}`).css("background-color","#dbf0db")
              }else{
                $(`#${data.ele_id}`).css("background-color","#dbf0db")
              }
            }else{
              if ($(`#${data.ele_id}`).hasClass('select2')){
                $(`#${data.ele_id}`).parent().find('span').find(".select2-selection.select2-selection--single").css("background-color","#eed3d9")
              }else if($(`#${data.ele_id}`).attr('data-fieldtype') == "MultiselectField"){
                let mulid = $(`#${data.ele_id}`).attr('data-connectedselectfield')
                $(`#${mulid}`).parent().find(".select2-selection--multiple").css("background-color","#eed3d9")
              }else if($(`#${data.ele_id}`).is(':-webkit-autofill')){
                var clone = $(`#${data.ele_id}`).clone(true, true);
                $(`#${data.ele_id}`).after(clone);
                $(`#${data.ele_id}`).remove();
                $(`#${data.ele_id}`).css("background-color","#eed3d9")
              }else{
                $(`#${data.ele_id}`).css("background-color","#eed3d9")
              }
              data.error_msg = data.error_msg.replace("Error while uploading:","")
              data.error_msg = data.error_msg.replace("Error while uploading,","")

              $(`#${data.ele_id}`).attr("data-toggle","tooltip")
              $(`#${data.ele_id}`).attr("title",data.error_msg)

            }

          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          },
      });
  } else {
    $(this).css("background-color", "");
    if ($(this).hasClass('select2')) {
        parent = $(this).parent()
        $(this).select2({dropdownParent:parent})
    }
  }
}

function checkValidationNowCol(){
  let tableName = $(this).attr("data-tablename")
  let fieldValidationMapper = $(this).attr("data-columnb_val");

  if (fieldValidationMapper != undefined){
    fieldValidationMapper = JSON.parse(fieldValidationMapper)
  }else{
    fieldValidationMapper = {}
  }

  let process_id = $(this).attr("id").split('_').slice(-1)[0];
  let fieldName = $(this).attr("id").replace(`id_`,"").replace(`_${process_id}`,"");
  let fieldVal = $(this).val()

  let cols_filled = [];
  let val_filled = [];

  if (fieldVal && !(["", "---", "----", "{}"].includes(fieldVal))) {
    if (fieldValidationMapper.hasOwnProperty(fieldName)) {
      let dependentField = fieldValidationMapper[fieldName];
      let dependentFieldValue = $(`#id_${dependentField}_${process_id}`).val();
      if (dependentFieldValue && !(["", "---", "----", "{}"].includes(dependentFieldValue))) {
        cols_filled.push(dependentField);
        val_filled.push(dependentFieldValue);
      }
    }
    if (Object.values(fieldValidationMapper).includes(fieldName)) {
      let validationSourceField = Object.keys(fieldValidationMapper).find(key => fieldValidationMapper[key] === fieldName);
      let validationSourceFieldValue = $(`#id_${validationSourceField}_${process_id}`).val();
      if (validationSourceFieldValue && !(["", "---", "----", "{}"].includes(validationSourceFieldValue))) {
        cols_filled.push(validationSourceField);
        val_filled.push(validationSourceFieldValue);
      }
    }
    if (cols_filled.length && val_filled.length) {
      cols_filled.push(fieldName);
      val_filled.push(fieldVal);
    }

    $(this).attr("title","")
    if (cols_filled.length > 1){
      let customdict = $(`#customValidationList1${process_id}`).val();
      if (!customdict){
        customdict = "";
      }
      $.ajax({
        url:`/users/${urlPath}/dynamicVal/`,
        data: {
        "operation":"check_validations_col",
        "tableName":tableName,
        "fieldName":JSON.stringify(cols_filled),
        "fieldVal":JSON.stringify(val_filled),
        "process_id":process_id,
        "customdict":customdict,
        },
        type: "POST",
        dataType: "json",
        success: function (data) {
          if(data.error == "no"){
            for(let i in data.ele_id){
              if ($(`#${data.ele_id[i]}`).hasClass('select2')){
                $(`#${data.ele_id[i]}`).parent().find('span').find(".select2-selection.select2-selection--single").css("background-color","#dbf0db")
              }else if($(`#${data.ele_id[i]}`).attr('data-fieldtype') == "MultiselectField"){
                let mulid = $(`#${data.ele_id[i]}`).attr('data-connectedselectfield')
                $(`#${mulid}`).parent().find(".select2-selection--multiple").css("background-color","#dbf0db")
              }else if($(`#${data.ele_id[i]}`).is(':-webkit-autofill')){
                var clone = $(`#${data.ele_id[i]}`).clone(true, true);
                $(`#${data.ele_id[i]}`).after(clone);
                $(`#${data.ele_id[i]}`).remove();
                $(`#${data.ele_id[i]}`).css("background-color","#dbf0db")
              }else{
                $(`#${data.ele_id[i]}`).css("background-color","#dbf0db")
              }
            }
          }else{
            for (let [element, status] of Object.entries(data.validation_status)) {
              if (status == "success") {
                if ($(`#${element}`).hasClass('select2')){
                  $(`#${element}`).parent().find('span').find(".select2-selection.select2-selection--single").css("background-color","#dbf0db")
                }else if($(`#${element}`).attr('data-fieldtype') == "MultiselectField"){
                  let mulid = $(`#${element}`).attr('data-connectedselectfield')
                  $(`#${mulid}`).parent().find(".select2-selection--multiple").css("background-color","#dbf0db")
                }else if($(`#${element}`).is(':-webkit-autofill')){
                  var clone = $(`#${element}`).clone(true, true);
                  $(`#${element}`).after(clone);
                  $(`#${element}`).remove();
                  $(`#${element}`).css("background-color","#dbf0db")
                }else{
                  $(`#${element}`).css("background-color","#dbf0db")
                }
              } else {
                if ($(`#${element}`).hasClass('select2')){
                  $(`#${element}`).parent().find('span').find(".select2-selection.select2-selection--single").css("background-color","#eed3d9")
                }else if($(`#${element}`).attr('data-fieldtype') == "MultiselectField"){
                  let mulid = $(`#${element}`).attr('data-connectedselectfield')
                  $(`#${mulid}`).parent().find(".select2-selection--multiple").css("background-color","#eed3d9")
                }else if($(`#${element}`).is(':-webkit-autofill')){
                  var clone = $(`#${element}`).clone(true, true);
                  $(`#${element}`).after(clone);
                  $(`#${element}`).remove();
                  $(`#${element}`).css("background-color","#eed3d9")
                }else{
                  $(`#${element}`).css("background-color","#eed3d9")
                }
                $(`#${element}`).attr("data-toggle","tooltip")
                $(`#${element}`).attr("title", status)
              }
            }
          }
        },
        error: function () {
          Swal.fire({icon: 'error',text: 'Error! Please try again.'});
        },
      });
    }
  } else {
    $(this).css("background-color", "");
    if ($(this).hasClass('select2')) {
      parent = $(this).parent()
      $(this).select2({dropdownParent:parent})
    }
  }
}

$(".check_validForm_now").on("change dp.change", checkValidationNow)
$(".column_validator").on("change dp.change", checkValidationNowCol)

function tableOrdering(obj){
  const elementId = obj.getAttribute('data-element-id')

  var attrData = $(`#tableOrderingBtn${elementId}`).attr('data_list')

  if (attrData == ''){
    var inputs = []
    $(`.card-title`).find(`.${elementId}_editable`).each(function(){
      inputs.push($(this).attr('data-table'))
    });
    let uniqueChars = [...new Set(inputs)];
    var tabNames = uniqueChars

    var order_id = {}
      for(let i = 0; i <tabNames.length;i++){
        order_id[i] = tabNames[i]
      }
    length_order_id = Object.keys(order_id).length
    var tableBody = ''
    for (let i in order_id){
      tableNumber = parseInt(i)+1
      tableBody += '<tr>'
      tableBody += `<td class="multiple_table_name">${order_id[i]}</td>`
      tableBody +=  `<td><input oninput='validation.call(this)' class='input form-control multiple_table_order' style='width:55px;margin:auto;text-align:center' minimum=1 maximum='${length_order_id}' type="integer" value="${tableNumber}"</span></td>`
      tableBody += '</tr>'
    }
  }else{
    var attrData = JSON.parse($(`#tableOrderingBtn${elementId}`).attr('data_list'))
    var order_id = attrData;
    length_order_id = Object.keys(order_id).length
    var tableBody = ''
    for (let i in order_id){
      tableNumber = parseInt(i)
      tableBody += '<tr>'
      tableBody += `<td class="multiple_table_name">${order_id[i]}</td>`
      tableBody +=  `<td><input oninput='validation.call(this)' class='input form-control multiple_table_order' style='width:55px;margin:auto;text-align:center' minimum=1 maximum='${length_order_id}' type="integer" value="${tableNumber}"</span></td>`
      tableBody += '</tr>'
    }
  }

  $(`#tableOrderBodyTable${elementId}`).empty()
  $(`#tableOrderBodyTable${elementId}`).append(tableBody)
  $(`#tableOrderModal${elementId}`).modal('show')
}
function tableOrderSaveBtn(obj){
  const elementId = obj.getAttribute('data-element-id')
  const itemCode = window.location.pathname.split('/')[4]
  var tableOrder ={}
  $(`#tableOrderBodyTable${elementId}`).find('tr').each(function(){
    tableOrder[$(this).find('.multiple_table_order').val()] = $(this).find('.multiple_table_name').text()
  })
  var attrData = $(`#tableOrderingBtn${elementId}`).attr('data_list',JSON.stringify(tableOrder));
  var tableNameOrder =[]
        for (key in tableOrder){
          tableNameOrder.push(tableOrder[key])
        }
  tableNameOrder = JSON.stringify(tableNameOrder)
  $(`#tableOrderSave${elementId}`).html(`<i class="fa fa-circle-notch fa-spin"></i>`)
  $.ajax({
    url: `/users/${urlPath}/dynamicVal/`,
    data: {
      table_order: tableNameOrder,
      element_id:elementId,
      operation: 'tableOrdering',
      'pr_code':window.location.pathname.split('/')[4],
    },
    type: 'POST',
    dataType: 'json',
    success: function (data) {
      location.reload()
    },
    error: function () {
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    }
  })
}
var validation = function() {
  if(parseInt($(this).val()) < 1) {
    $(this).val(1).trigger('change')
  }
  if(parseInt($(this).val()) > parseInt($(this).attr('maximum'))) {
    $(this).val(parseInt($(this).attr('maximum'))).trigger('change')
  }
}

var recurrElementID = ""
function showRecurrModal(){
  recurrElementID = $(this).attr("data-elementid")
  if($(`#hidden_recurr_${recurrElementID}`).attr('value') != undefined){
    data = $(`#hidden_recurr_${recurrElementID}`).attr('value')
    data = JSON.parse(data)
    recurrLoad(data)
  }
  $("#RecurrenceModal").modal('show');
}

$('.recpattern').off('select2:select').on('select2:select',function(){
  if($(this).val() == "Daily"){
    $('.daily_div').css('display',"block")
    $('.weekly_div').css('display',"none")
    $('.monthly_div').css('display',"none")
    $('.yearly_div').css('display',"none")
  }else if($(this).val() == "Weekly"){
    $('.daily_div').css('display',"none")
    $('.weekly_div').css('display',"block")
    $('.monthly_div').css('display',"none")
    $('.yearly_div').css('display',"none")
  }else if($(this).val() == "Monthly"){
    $('.daily_div').css('display',"none")
    $('.weekly_div').css('display',"none")
    $('.monthly_div').css('display',"block")
    $('.yearly_div').css('display',"none")
  }else if($(this).val() == "Yearly"){
    $('.daily_div').css('display',"none")
    $('.weekly_div').css('display',"none")
    $('.monthly_div').css('display',"none")
    $('.yearly_div').css('display',"block")
  }
})

$('.daily_div input[name=data_choice1]').on('change', function() {
  checked_val = $('input[name=data_choice1]:checked', '.daily_div').val()

  if(checked_val != "Everyday"){
    $('.rec_daily_days_no').attr('disabled',true)
  }else{
    $('.rec_daily_days_no').attr('disabled',false)
  }
});

$('.range_div input[name=data_choice2]').on('change', function() {
  checked_val = $('input[name=data_choice2]:checked', '.range_div').val()

  if(checked_val != "endafter"){
    $('.rec_occurr').attr('disabled',true)
  }else{
    $('.rec_occurr').attr('disabled',false)
  }
});


function saveRecurrButton(){
  var rec_dic = {}
  if($('.recpattern').val() == "Daily"){
    rec_dic['type'] = "Daily"
    if($('input[name=data_choice1]:checked', '.daily_div').val() == "Everyday"){
      rec_dic['daily_day'] = "Everyday"
      rec_dic['rec_daily_days_no'] = $('.rec_daily_days_no').val()
    }else{
      rec_dic['daily_day'] = "Everyweekday"
      rec_dic['rec_daily_days_no'] = ""
    }
  }
  else if($('.recpattern').val() == "Weekly"){
    rec_dic['type'] = "Weekly"
    rec_dic['rec_weekly_days_no'] = $('.rec_weekly_days_no').val()
    rec_dic['rec_weekly_days'] = $('.rec_weekly_days').val()
  }
  else if($('.recpattern').val() == "Monthly"){
    rec_dic['type'] = "Monthly"
    rec_dic['rec_monthly_days_no'] = $('.rec_monthly_days_no').val()
    rec_dic['rec_monthly_months_no'] = $('.rec_monthly_months_no').val()
  }
  else if($('.recpattern').val() == "Yearly"){
    rec_dic['type'] = "Yearly"
    rec_dic['rec_yearly_year_no'] = $('.rec_yearly_year_no').val()
    rec_dic['rec_yearly_month_no'] = $('.rec_yearly_month_no').val()
    rec_dic['rec_yearly_day_no'] = $('.rec_yearly_day_no').val()
  }

  rec_dic['daterange'] = $('.dtrangepicker').val()
  rec_dic['end_date'] = $('input[name=data_choice2]:checked', '.range_div').val()
  if($('input[name=data_choice2]:checked', '.range_div').val() == "endafter"){
    rec_dic['end_no_occ'] = $('.rec_occurr').val()
  }else if($('input[name=data_choice2]:checked', '.range_div').val() == "onenddate"){
    rec_dic['end_no_occ'] = "end"
  }else{
    rec_dic['end_no_occ'] = ""
  }

  $(`#hidden_recurr_${recurrElementID}`).attr('value',JSON.stringify(rec_dic))
  Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});
}

function recurrLoad(data){
  if(data){
    $('.recpattern').val(data.type).trigger("select2:select")
    $('.recpattern').val(data.type).trigger("change")
    if(data.type == "Daily"){
      $(`input[value=${data.daily_day}]`, '.daily_div').prop("checked", true).trigger('change')
      $('.rec_daily_days_no').val(data.rec_daily_days_no)
    }else if(data.type == "Weekly"){
      $('.rec_weekly_days_no').val(data.rec_weekly_days_no)
      $('.rec_weekly_days').val(data.rec_weekly_days).trigger('change')
    }else if(data.type == "Monthly"){
      $('.rec_monthly_days_no').val(data.rec_monthly_days_no)
      $('.rec_monthly_months_no').val(data.rec_monthly_months_no).trigger('change')
    }else if(data.type == "Yearly"){
      $('.rec_yearly_year_no').val(data.rec_yearly_year_no)
      $('.rec_yearly_month_no').val(data.rec_yearly_month_no)
      $('.rec_yearly_day_no').val(data.rec_yearly_month_no)
    }

      $('.dtrangepicker').val(data.daterange)
      startdate = data.daterange.split(' - ')[0]
      enddate = data.daterange.split(' - ')[1]
      $('.dtrangepicker').data('daterangepicker').setStartDate(startdate)
      $('.dtrangepicker').data('daterangepicker').setEndDate(enddate)
      $(`input[value=${data.end_date}]`, '.range_div').prop("checked", true).trigger('change')
      $('.rec_occurr').val(data.end_no_occ)
  }else{

    $('.daily_div').css('display',"none")
    $('.weekly_div').css('display',"none")
    $('.monthly_div').css('display',"none")
    $('.yearly_div').css('display',"none")

    $('.recpattern').val("").trigger("select2:select")
    $('.recpattern').val("").trigger("change")

    $('input[name=data_choice1]', '.daily_div').prop("checked", false).trigger('change')
    $('.rec_daily_days_no').val("").trigger("change")
    $('.rec_weekly_days_no').val("")
    $('.rec_weekly_days').val("").trigger('change')
    $('.rec_monthly_days_no').val("")
    $('.rec_monthly_months_no').val("").trigger('change')
    $('.rec_yearly_year_no').val("")
    $('.rec_yearly_month_no').val("")
    $('.rec_yearly_day_no').val("")
    $('.dtrangepicker').val("")
    $('input[name=data_choice2]', '.range_div').prop("checked", false).trigger('change')
    $('.rec_occurr').val("")
  }
}



function customTableDev (obj) {
  let processType = $(obj).attr("data-process_type")
  let tableList = ""

  if(processType == "create"){
    tableList = $('#selectFormTable').val()
  }else if(processType == "list"){
    tableList = $('#selectTablePC').val()
  }else if(processType == "upload"){
    tableList = $('#selectDocumentTable').val()
  }

  if (tableList.constructor === Array) {
    $(`#custommValidationSelection_dev`).empty();
    $(`#custommValidationSelection_dev`).append(
      "<option value='value'selected disabled>Select Option Name</option>"
    );
    for (let i = 0; i < tableList.length; i++) {
      $(`#custommValidationSelection_dev`).append(
        new Option(tableList[i], tableList[i])
      );
    }
  } else {
    $(`#custommValidationSelection_dev`).empty();
    $(`#custommValidationSelection_dev`).append(
      "<option value='value'selected disabled>Select Option Name</option>"
    );
    $(`#custommValidationSelection_dev`).append(
      new Option(tableList, tableList)
    );
  }

  data = $('.customValbtnDev').attr('data-data_config')
  if(data != undefined){
    data = JSON.parse(data)
  }else{
    data = {}
  }
  reloadCustomValidationDev(data);
}

function conditionalTableDev () {
  $(`#custom_validation_table_dev`).empty();
  $(`#condition_dropdown_dev`).empty();
  $(`#condition_dropdown1_dev`).empty();
  if($(`#custommValidationSelection_dev`).val()){
    $.ajax({
      url: `/users/${urlPath}/constriant_get_data/`,
      data: {
        model_name: $(`#custommValidationSelection_dev`).val(),
        operation: 'custom_conditional_table',
      },
      type: 'POST',
      dataType: 'json',
      success: function (data) {
        const labelColumn = data.label_columns;

        $(`#condition_dropdown_dev`).empty();
        $(`#condition_dropdown1_dev`).empty();
        for (const [key, value] of Object.entries(labelColumn)) {
          $(`#condition_dropdown_dev`).append(
            '<li class="dropdown-item"><a href="javascript:void(0)" name=' +
              key +
              ' class="filter_btn">' +
              value +
              '</a></li>'
          );
          $(`#condition_dropdown1_dev`).append(
            '<li class="dropdown-item"><a href="javascript:void(0)" name=' +
              key +
              ' class="filter_btn_master" style="color:var(--primary-color);font-size:11px;">' +
              value +
              '</a></li>'
          );
        }
        $('.filter_btn').click(function () {
          const name = $(this).attr('name');
          const STRING = data.form_fields[name];
          $(`#custom_validation_table_dev`).append(STRING);

          $(`#custom_validation_table_dev tr`)
            .eq(-1)
            .find('select')
            .each(function () {
              $(this).select2()
            });

          $('.remove_filter').on('click', removefilter);

          function removefilter () {
            $(this).closest('tr').remove();
          }
        });

        $('.filter_btn_master').click(function () {
          const name = $(this).attr('name');
          const STRING = data.form_fields_master[name];
          $(`#custom_validation_table_dev`).append(STRING);

          $(`#custom_validation_table_dev tr`)
            .eq(-1)
            .find('select')
            .each(function () {
              $(this).select2()
            });

          $('.remove_filter').on('click', removefilter);

          function removefilter () {
            $(this).closest('tr').remove();
          }
        });
      },
      error: function () {
        Swal.fire({icon: 'error',text: 'Error! Please try again.'});
      },
    });
  }
}

function saveCustomValidationdev () {
  const tableDict = {};
  const conditionList = [];
  let conditionListMaster = []
  let nullChecker = false;

  $(`#custom_validation_table_dev`)
    .find('tr:not(.master_filter)')
    .each(function () {
      const conditionDict = {};

      const constraintName = $(this)
        .find('td')
        .find("input[name='Constraint_name']")
        .val();
      const ruleSet = $(this).find('td').find("input[name='Rule_set']").val();
      conditionDict.column_name = $(this)
        .find('td')
        .find('.select2bs4')
        .attr('name');
      conditionDict.condition_name = $(this)
        .find('td')
        .find('.select2bs4 option:selected')
        .val();
      conditionDict.input_value = $(this)
        .find('td')
        .eq(4)
        .find('div')
        .find('input')
        .val();
      conditionDict.constraint_name = constraintName;
      conditionDict.rule_set = ruleSet;
      if (!constraintName && !ruleSet) {
        nullChecker = true;
      }
      conditionList.push(conditionDict);
    });
  tableDict[$(`#custommValidationSelection_dev`).val()] =
		conditionList;

    $(`#custom_validation_table_dev`)
    .find('tr.master_filter')
    .each(function () {
      const conditionDict1 = {};

      const constraintName = $(this)
        .find('td')
        .find("input[name='Constraint_name']")
        .val();
      const ruleSet = $(this).find('td').find("input[name='Rule_set']").val();
      conditionDict1.column_name = $(this)
        .find('td')
        .find('.select2bs4')
        .attr('name');
      conditionDict1.condition_name = "Isin"
      conditionDict1.input_value = $(this)
        .find('td')
        .find('.master_column_vals')
        .val();
      conditionDict1.constraint_name = constraintName;
      conditionDict1.rule_set = ruleSet;
      conditionDict1.table_name = $(this).find('td').find('.master_col_table').val()
      if (!constraintName && !ruleSet) {
        nullChecker = true;
      }
      conditionListMaster.push(conditionDict1);
    });

    tableDict["Master_filter"] = conditionListMaster

  if (nullChecker) {
    Swal.fire({icon: 'warning',text:"Constraint Name and Rule Set are mandatory to proceed further." });
  } else {
    let datav = {}
    datav['reload_custom_validation'] = tableDict
    $('.customValbtnDev').attr('data-data_config',JSON.stringify(datav))
    Swal.fire({icon: 'success',text: 'Custom validation configuration saved successfully!'});
    $(`.carousel-control-prev[href='#carouselCustomValidation']`).click();
    setTimeout(function () {
      reloadCustomValidationDev(datav);
    }, 250);

  }
}

function reloadCustomValidationDev(data) {
  if (
    Object.prototype.hasOwnProperty.call(data, 'reload_custom_validation')
  ) {
    if (data.reload_custom_validation) {
      const rowData = data.reload_custom_validation
      $(`#configuration_val_row_dev`).empty();
      let rowHtml = '';
      let count = 1;
      for (const rowName in rowData) {
        if(rowName != "Master_filter"){
          rowHtml += `<tr> <td>${count}</td> <td value='${rowName}'>${rowName}</td> <td><button type="button" class="btn-primary reconfigurecustomvalidationdev" onclick="deleteValDev()" name="${rowName}"><i class="fas fa-trash"></i></button> <button type="button" class="btn-primary editcustomexist_validationdev" onclick="editValDev.call(this)" name="${rowName}" href="#carouselCustomValidation" data-slide="next" ><i class="fas fa-edit"></i></button></td></tr>`;

          count++;
        }
      }
      $(`#configuration_val_row_dev`).append(rowHtml);

    }
  }else{
    $(`#configuration_val_row_dev`).empty();
  }
}

function editValDev() {
  const modelName = $(this).attr('name');
  let confirmCustomEdit = null
  Swal.fire({
    icon:'question',
    title: `Do you wish to load the configuration?\n\n Click 'Yes' to confirm or click 'No' if you do not wish to load it.`,
    showDenyButton: true,
    showCancelButton: true,
    confirmButtonText: 'Yes',
    denyButtonText:'No',
  }).then((result) => {
    if (result.isConfirmed) {
      confirmCustomEdit = true
      if (confirmCustomEdit) {

        data = $('.customValbtnDev').attr('data-data_config')
        if(data != undefined){
          data = JSON.parse(data)
        }else{
          data = {}
        }

        if (
          Object.prototype.hasOwnProperty.call(
            data,
            'reload_custom_validation'
          )
        ) {
          if (data.reload_custom_validation) {
            const rowData = data.reload_custom_validation;
            $.ajax({
              url: `/users/${urlPath}/constriant_get_data/`,
              data: {
                model_name: modelName,
                operation: 'custom_conditional_table',
              },
              type: 'POST',
              dataType: 'json',
              success: function (data) {
                $(`#custommValidationSelection_dev`)
                  .val(modelName)
                  .trigger('change');
                for (const rowInnerData of rowData[modelName]) {
                  const name = rowInnerData.column_name;
                  const STRING = data.form_fields[name];
                  $(`#custom_validation_table_dev`).append(STRING);
                  $(`#custom_validation_table_dev tr`).eq(-1).find('td').eq(3).find('div').find('select').removeAttr('onchange')
                  $(`#custom_validation_table_dev tr`)
                    .eq(-1)
                    .find('select')
                    .each(function () {
                      $(this).select2()
                    });
                  $(`#custom_validation_table_dev tr`)
                    .eq(-1)
                    .find('td')
                    .eq(1)
                    .find('div')
                    .find('input')
                    .val(rowInnerData.constraint_name)
                    .trigger('change');
                  $(`#custom_validation_table_dev tr`)
                    .eq(-1)
                    .find('td')
                    .eq(2)
                    .find('div')
                    .find('input')
                    .val(rowInnerData.rule_set)
                    .trigger('change');

                  $(`#custom_validation_table_dev tr`)
                    .eq(-1)
                    .find('td')
                    .eq(3)
                    .find('div')
                    .find('select')
                    .val(rowInnerData.condition_name)
                    .trigger('change');
                  $(`#custom_validation_table_dev tr`)
                    .eq(-1)
                    .find('td')
                    .eq(4)
                    .find('div')
                    .find('input')
                    .val(rowInnerData.input_value)
                    .trigger('change');

                  $('.remove_filter').on('click', removefilter);

                  function removefilter () {
                    $(this).closest('tr').remove();
                  }
                }

                if(rowData.hasOwnProperty('Master_filter')){
                  for (const rowInnerData of rowData["Master_filter"]) {
                    const name = rowInnerData.column_name;
                    const STRING = data.form_fields_master[name];
                    $(`#custom_validation_table_dev`).append(STRING);
                    $(`#custom_validation_table_dev tr`).eq(-1).find('td').eq(3).find('div').find('select').attr('data-data',rowInnerData.input_value)
                    $(`#custom_validation_table_dev tr`)
                      .eq(-1)
                      .find('select')
                      .each(function () {
                        $(this).select2()
                      });
                    $(`#custom_validation_table_dev tr`)
                      .eq(-1)
                      .find('td')
                      .eq(1)
                      .find('div')
                      .find('input')
                      .val(rowInnerData.constraint_name)
                      .trigger('change');
                    $(`#custom_validation_table_dev tr`)
                      .eq(-1)
                      .find('td')
                      .eq(2)
                      .find('div')
                      .find('input')
                      .val(rowInnerData.rule_set)
                      .trigger('change');

                    $(`#custom_validation_table_dev tr`)
                      .eq(-1)
                      .find('td')
                      .eq(3)
                      .find('div')
                      .find('select')
                      .val(rowInnerData.table_name)
                      .trigger('change');

                    $('.remove_filter').on('click', removefilter);

                    function removefilter () {
                      $(this).closest('tr').remove();
                    }
                  }
                }
              },
              error: function () {
                Swal.fire({icon: 'error',text: 'Error! Please try again.'});
              },
            });
          }
        }

      }
    }
    else if (result.isDenied) {
      confirmCustomEdit = false
    }});
};

function deleteValDev () {
  const fieldDeleteName = $(this).attr('name');

  Swal.fire({icon: "question", text: `Do you wish to delete ${fieldDeleteName} configuration ?`,
  showDenyButton: true,
  showCancelButton: true,
  confirmButtonText: 'Yes',
  denyButtonText: `No`,}).then((result) => {
    if (result.isConfirmed) {
      $('.customValbtnDev').attr('data-data_config', JSON.stringify('{}'))
      reloadCustomValidationDev({});
    }
  })

};


function ExtractDataButton(This){ // eslint-disable-line no-unused-vars
  let elementID = $(This).attr('data-elementid')
  let modelName = $(This).attr('data-table-name')

  $(`#exDataColumn1_${elementID}`).val("").trigger("change")

$.ajax({
    url: `/users/${urlPath}/processGraphModule/`,

    data: {
      'operation': 'dropFieldList',
      'tableName':modelName,
    },
    type: "POST",
    dataType: "json",
    success: function (data) {
      $(`#exDataColumn1_${elementID}`).empty()
      for (let i = 0; i < data.fieldList.length; i++) {
        $(`#exDataColumn1_${elementID}`).append(new Option(data.fieldList[i], data.fieldNameList[i]));
          }
      },
    error: function () {
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    }

})

  $(`#extract_data_modal_${elementID}`).modal('show')

}

function downloadexdData(){

  let eleID = $(this).attr("id").replace("btn_exDataDownload_","")
  let tablename = $(`#extract_data_${eleID}`).attr("data-table-name")
  let cols = $(`#exDataColumn1_${eleID}`).val()
  let file_name = $(this).attr("data-filename");

  $.ajax({
    url: `/users/${urlPath}/processGraphModule/`,

    data: {
      'operation': 'download_extract_data',
      'cols': JSON.stringify(cols),
      'tableName':tablename,
    },
    type: "POST",
    success: function (data) {
                var a = window.document.createElement('a');
        a.href = window.URL.createObjectURL(new Blob([data], {type: 'text/csv'}));
        if (file_name === "" || file_name === undefined){
          a.download = `${tablename}.csv`;
        } else{
          a.download = `${file_name}.csv`;
        }

        window.document.body.appendChild(a);
        a.click();
        window.document.body.removeChild(a);
      },
    error: function () {
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    }

})
}

function formatCreditCardOnKey(event, ccid) {
  //on keyup, check for backspace to skip processing
  var code = (event.which) ? event.which : event.keyCode;
  if(code != 8)
      formatCreditCard(ccid);
  else{
      //trim whitespace from end; trimEnd() doesn't work in IE
      document.getElementById(ccid).value = document.getElementById(ccid).value.replace(/\s+$/, '');
  }
}

function formatCreditCard(ccid) {
  var cardField = document.getElementById(ccid);
  //remove all non-numeric characters
  var realNumber = cardField.value.replace(/\D/g,'');
  var newNumber = "";
  for(var x = 1; x <= realNumber.length; x++){
      //make sure input is a digit
      if (isNumeric(realNumber.charAt(x-1)))
          newNumber += realNumber.charAt(x-1);
      //add space every 4 numeric digits
      if(x % 4 == 0 && x > 0 && x < 15)
          newNumber += " ";
  }
  cardField.value = newNumber;
}

function isNumeric(char){
  return('0123456789'.indexOf(char) !== -1);
}

function checkvalidCC(){

  let card_config = $(this).attr("data-issuer_type")
  if(card_config != undefined){
    card_config = JSON.parse(card_config)
  }else{
    card_config = {}
  }

  fieldVal = $(this).val()
  let process_id = $(this).attr("id").split('_').slice(-1)[0]

  $(`#id_${card_config['cvv_field_create_fname']}_${process_id}`).attr("data-cvv_card", $(this).attr("id"))

  if ((fieldVal !== "") && (fieldVal !== "---") && (fieldVal !== "----") && fieldVal) {
    let err_card = isValid(fieldVal);

    if(err_card){
      $(this).parent().parent().find('.fa-check').css("display","block")
      $(this).parent().parent().find('.fa-times').css("display","none")
      card_type = getCreditCardNameByNumber(fieldVal)
      if($(this).hasClass("card_style")){
        $(this).css('background', `url('/static/images/Base_theme/Card_Logos/${card_type}.png') no-repeat right 1rem top 0.5rem`);
        $(this).css('background-size','39px');
      }
      $(`#id_${card_config['cardtype_field_create_fname']}_${process_id}`).val(card_type).trigger('change')
    }else{
      if($(this).hasClass("card_style")){
        $(this).css('background', `url('') no-repeat right 1rem top 0.5rem`);
        $(this).css('background-size','39px');
      }
      $(this).parent().parent().find('.fa-check').css("display","none")
      $(this).parent().parent().find('.fa-times').css("display","block")
      $(`#id_${card_config['cardtype_field_create_fname']}_${process_id}`).val("Invalid card type").trigger('change')

    }
  }else{
    if($(this).hasClass("card_style")){
      $(this).css('background', `url('') no-repeat right 1rem top 0.5rem`);
      $(this).css('background-size','39px');
    }
    $(`#id_${card_config['cardtype_field_create_fname']}_${process_id}`).val("").trigger('change')
    $(this).parent().parent().find('.fa-check').css("display","none")
    $(this).parent().parent().find('.fa-times').css("display","none")
  }

    $(`#id_${card_config['cvv_field_create_fname']}_${process_id}`).trigger("change")
}


function checkvalidCCV(){

  let cardno_col = $(this).attr("data-cvv_card")

  fieldVal = $(this).val()
  fieldValCard = $(`#${cardno_col}`).val()

  if ((fieldVal !== "") && (fieldVal !== "---") && (fieldVal !== "----") && fieldVal &&
      (fieldValCard !== "") && (fieldValCard !== "---") && (fieldValCard !== "----") && fieldValCard) {

    let err_card = isSecurityCodeValid(fieldValCard, fieldVal);

    if(err_card){
      $(this).parent().parent().find('.fa-check').css("display","block")
      $(this).parent().parent().find('.fa-times').css("display","none")
      $(this).parent().parent().find('.fa-check').attr("data-content", "Valid cvv no")
    }else{
      $(this).parent().parent().find('.fa-check').css("display","none")
      $(this).parent().parent().find('.fa-times').css("display","block")
      $(this).parent().parent().find('.fa-times').attr("data-content", "Invalid cvv no")
    }
  }else if((fieldVal != "") && (fieldVal != "---") && (fieldVal != "----")){

    $(this).parent().parent().find('.fa-check').css("display","none")
    $(this).parent().parent().find('.fa-times').css("display","block")
    $(this).parent().parent().find('.fa-times').attr("data-content", "Please enter Card no first")

  }else{

    $(this).parent().parent().find('.fa-check').css("display","none")
    $(this).parent().parent().find('.fa-times').css("display","none")
    $(this).parent().parent().find('.fa-check').attr("data-content", "Valid cvv no")
    $(this).parent().parent().find('.fa-times').attr("data-content", "Invalid cvv no")
  }

}

function checkvalidExpiry(){

  fieldVal = $(this).val()

  let process_id = $(this).attr("id").split('_').slice(-1)[0]

  if ((fieldVal !== "") && (fieldVal !== "---") && (fieldVal !== "----") && fieldVal) {
    let err_card = isExpirationDateValid(fieldVal.split('-')[1],fieldVal.split('-')[0]);

    if(err_card){
      $(this).parent().parent().find('.fa-check').css("display","block")
      $(this).parent().parent().find('.fa-times').css("display","none")
    }else{
      $(this).parent().parent().find('.fa-check').css("display","none")
      $(this).parent().parent().find('.fa-times').css("display","block")

    }
  }else{
    $(this).parent().parent().find('.fa-check').css("display","none")
    $(this).parent().parent().find('.fa-times').css("display","none")
  }
}

function downloadexdData_compL3(){

  let elementID = $(this).attr("data-elementid")
  let data_element_id = $(this).attr('data-elementid_redis')
  let submitname = $(this).attr('data-submitname')
  let cols = $(`#${submitname}${elementID}`).val()

  $.ajax({
      url: `/users/${urlPath}/computationModule/`,

      data: {
        'operation': 'download_extract_data_comp',
        'cols': JSON.stringify(cols),
        'data_element_id':data_element_id,
      },
      type: "POST",
      success: function (data) {
          var a = window.document.createElement('a');
          a.href = window.URL.createObjectURL(new Blob([data], {type: 'text/csv'}));
          a.download = 'data.csv';

          window.document.body.appendChild(a);
          a.click();
          window.document.body.removeChild(a);
        },
      error: function () {
        Swal.fire({icon: 'error',text: 'Error! Please try again.'});
      }
  })
}


var tableFieldData

function tableselectShow(fieldname,elementID,table,viewOnly=false){
  const itemCode = window.location.pathname.split('/')[4];
  const modelName = table
  let tables_f = ""
  let tablefield_modal = ""
  let add_newtblf = ""
  let save_table_field = ""
  let edit = ""

  if(viewOnly){
    tables_f = `#tables_f${elementID}_list`
    tablefield_modal = `#tablefield_modal_${elementID}_list`
    add_newtblf = `.add_newtblf_${elementID}_list`
    save_table_field = `#save_table_field_${elementID}_list`
    edit = "view"
  }else{

    tables_f = `#tables_f${elementID}`
    tablefield_modal = `#tablefield_modal_${elementID}`
    add_newtblf = `.add_newtblf_${elementID}`
    save_table_field = `#save_table_field_${elementID}`
    edit = "edit"
  }

  var ColumnIndex = 0

  $.ajax({
    url: `/users/${urlPath}/${itemCode}/`,
    data: { model_name: modelName, element_id: elementID, operation: 'get_listview_column' },
    type: 'POST',
    dataType: 'json',
    success: function (data) {
      tableFieldData = data
      if ($.fn.dataTable.isDataTable(tables_f)){
        $(tables_f).DataTable().destroy();
      }

      $(tables_f).find('.constraint_tblef_tableHeader').empty()
      $(tables_f).find('tbody').empty()

      $.each(Object.keys(data), function (key, value) {
        if(data[value].internal_type != "UniqueIDField"){
          const vname = data[value].verbose_name
          $(tables_f).find('.constraint_tblef_tableHeader').append(`<th data-fname=${Object.keys(data)[key]} style="text-align:center;border-bottom: 1px solid var(--primary-color); border-top: 1px solid var(--primary-color); padding: 5px 0;">${vname}</th>`)
          ColumnIndex = ColumnIndex + 1
        }
      })
      if(!viewOnly){
        $(tables_f).find('.constraint_tblef_tableHeader').append(`<th style="text-align:center;border-bottom: 1px solid var(--primary-color); border-top: 1px solid var(--primary-color); padding: 5px 0;">Actions</th>`)
        ColumnIndex = ColumnIndex + 1
      }

    },
    error: function () {
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    },
  })

  var lastColumnIndex = ColumnIndex-1

  $(add_newtblf).off('click').on('click', function(){
    $(tables_f).DataTable().destroy();
    $(tables_f).find('tbody').append('<tr style="padding: 5px 0;"></tr>')
    $.each(Object.keys(tableFieldData), function (key, value) {
      const ftype = tableFieldData[value].internal_type
      if(ftype != "UniqueIDField"){
        let settype;
        if (String(ftype) === 'ForeignKey') {
          settype = 'text'
          $(tables_f).find('tbody').find('tr').last().append(`
          <td style="border-top: 1px solid #e9ecef;max-width:35rem;min-width:5rem;">
              <select data-fname="${Object.keys(tableFieldData)[key]}" form="columnform" style="width:100%;" class="form-control textInput select2 p-2 ${elementID}_${edit}_${Object.keys(tableFieldData)[key]}">
              </select>
          </td>
              `)
          $.each(Object.keys(tableFieldData), function (key1, value1) {
            if (String(tableFieldData[value1].internal_type) === 'ForeignKey') {
              const choice = tableFieldData[value1].Choices
              for (const [k, v] of Object.entries(choice)) {
                $(`.${elementID}_${edit}_${Object.keys(tableFieldData)[key]}`).last().append(
                  `<option name="${v}" value="${k}">${v}</option>`
                )
              }
            }
          })
        } else {
          if (String(ftype) === 'TextField' || String(ftype) === 'ConcatenationField' || String(ftype) === 'CardField' || String(ftype) === 'CardCvvField' || String(ftype) === 'CardTypeField') {
            settype = 'text'
            $(tables_f).find('tbody').find('tr').last().append(`<td style="border-top: 1px solid #e9ecef;min-width:5rem;">
            <input data-fname="${Object.keys(tableFieldData)[key]}" type="${settype}" class="form-control p-2 textInput" style="width:100%;">
            </td>
            `)
          } else if (String(ftype) === 'DateTimeField') {
            settype = 'datetime-local'
            $(tables_f).find('tbody').find('tr').last().append(`<td style="border-top: 1px solid #e9ecef;min-width:5rem;">
            <input data-fname="${Object.keys(tableFieldData)[key]}" type="${settype}" step="1" class="form-control datetimepickerinput p-2" style="width:100%;">
            </td>
            `)
          } else if (String(ftype) === 'DateField') {
            settype = 'date'
            $(tables_f).find('tbody').find('tr').last().append(`<td style="border-top: 1px solid #e9ecef;min-width:5rem;">
            <input data-fname="${Object.keys(tableFieldData)[key]}" type="${settype}" step="1" class="form-control datetimepickerinput p-2" style="width:100%;">
            </td>
            `)
          } else if (String(ftype) === 'TimeField') {
            settype = 'time'
            use_sec = tableFieldData[value].use_seconds
            if(use_sec == "false"){
              $(tables_f).find('tbody').find('tr').last().append(`<td style="border-top: 1px solid #e9ecef;min-width:5rem;">
              <input data-fname="${Object.keys(tableFieldData)[key]}" type="${settype}" class="form-control timepickerinput p-2" style="width:100%;" data-dp-format="HH:mm">
              </td>
              `)
            }else{
                $(tables_f).find('tbody').find('tr').last().append(`<td style="border-top: 1px solid #e9ecef;min-width:5rem;">
              <input data-fname="${Object.keys(tableFieldData)[key]}" type="${settype}" class="form-control timepickerinput p-2" style="width:100%;" data-dp-format="HH:mm:ss">
              </td>
              `)
            }
          } else if (String(ftype) === 'EmailTypeField') {
            settype = 'email'
            $(tables_f).find('tbody').find('tr').last().append(`<td style="border-top: 1px solid #e9ecef;min-width:5rem;">
            <input data-fname="${Object.keys(tableFieldData)[key]}" type="${settype}" class="form-control textInput p-2" style="width:100%;">
            </td>
            `)
          } else if (String(ftype) === 'UniqueIDField') {
            settype = 'text'
            $(tables_f).find('tbody').find('tr').last().append(`<td style="border-top: 1px solid #e9ecef;min-width:5rem;">
            <input data-fname="${Object.keys(tableFieldData)[key]}" type="${settype}" class="form-control textInput p-2" style="width:100%;" disabled>
            </td>
            `)
          } else if (String(ftype) === 'BooleanField') {
            settype = "checkbox"
            $(tables_f).find('tbody').find('tr').last().append(`<td style="padding-left:3rem;padding-right:3rem;min-width:5rem;">
            <input type='checkbox' data-fname="${Object.keys(tableFieldData)[key]}" class="form-control p-2">
            </td>
            `)
          } else if (String(ftype) === 'CharField') {
            settype = 'text'
            if(tableFieldData[value].hasOwnProperty("choices")){
              choices = tableFieldData[value].choices
            }else{
              choices = []
            }
            const temp = new Set()
            for(let i=0;i<choices.length;i++){
                for(let j=0;j<choices[i].length;j++){
                    temp.add(choices[i][j])
                }
            }
            const temp1 = [...temp];
            if(choices.length > 0){
              $(tables_f).find('tbody').find('tr').last().append(`<td style="border-top: 1px solid #e9ecef;max-width:35rem;min-width:5rem;">
              <select data-fname="${Object.keys(tableFieldData)[key]}" form="columnform" style="width:100%;" class="form-control textInput select2 p-2 ${elementID}_${edit}_${Object.keys(tableFieldData)[key]}">
              </select>
              `)

              for (let i=0;i<temp1.length;i++) {
                $(`.${elementID}_${edit}_${Object.keys(tableFieldData)[key]}`).last().append(
                  `<option name="${temp1[i]}" value="${temp1[i]}">${temp1[i]}</option>`
                )
              }


            }else{
              $(tables_f).find('tbody').find('tr').last().append(`<td style="border-top: 1px solid #e9ecef;min-width:5rem;">
              <input data-fname="${Object.keys(tableFieldData)[key]}" type="${settype}" class="form-control textInput p-2" style="width:100%;">
              </td>
              `)
            }

          } else if (String(ftype) === 'URLField') {
            settype = 'url'
            $(tables_f).find('tbody').find('tr').last().append(`<td style="border-top: 1px solid #e9ecef;min-width:5rem;">
            <input data-fname="${Object.keys(tableFieldData)[key]}" type="${settype}" class="form-control p-2" textInput style="width:100%;">
            </td>
            `)
          } else if (String(ftype) === 'FileField') {
            settype = 'file'
            accept = "*"
            if (tableFieldData[value].file_extension){
              if (tableFieldData[value].file_extension == "Any"){
                accept = "*"
              }
              else if (tableFieldData[value].file_extension == "Images"){
                accept = "image/*"
              }
              else if (tableFieldData[value].file_extension == "Document"){
                accept=".doc,.docx,.rtf,.pdf,.csv,xlsx,.odt,.docx,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              }
              else if (tableFieldData[value].file_extension == "PDF"){
                accept=".pdf"
              }
            }

            $(tables_f).find('tbody').find('tr').last().append(`<td style="border-top: 1px solid #e9ecef;min-width:5rem;">
            <input accept=${accept} type='file' data-fname="${Object.keys(tableFieldData)[key]}" class='form-control p-2' style="width:100%;" multiple>
            </td>
            `)
          } else if (String(ftype) === 'UserField') {
            settype = 'text'
            $(tables_f).find('tbody').find('tr').last().append(`
            <td style="border-top: 1px solid #e9ecef;">
                <select data-fname="${Object.keys(tableFieldData)[key]}" style="width:100%;" form="columnform" class="form-control textInput select2 p-2 ${elementID}_${edit}_${Object.keys(tableFieldData)[key]}">
                </select>
            </td>
                `)
            $.each(Object.keys(tableFieldData), function (key1, value1) {
              if (String(tableFieldData[value1].internal_type) === 'UserField') {
                const choice = tableFieldData[value1].Choices
                for (let i in choice) {
                  $(`.${elementID}_${edit}_${Object.keys(tableFieldData)[key]}`).last().append(
                    `<option name="${choice[i]}" value="${choice[i]}">${choice[i]}</option>`
                  )
                }
              }
            })
          } else {
            settype = 'number'
            $(tables_f).find('tbody').find('tr').last().append(`<td style="border-top: 1px solid #e9ecef;min-width:5rem;">
            <input data-fname="${Object.keys(tableFieldData)[key]}" type="${settype}" step="1" class="form-control textInput p-2" style="width:100%;">
            </td>
            `)
          }

        }

        $(tables_f).find("tbody").find('tr').last().find('select').each(function() {
          $(this).select2();
        })

        $(tables_f).find("tbody").find('tr').last().find('.timepickerinput').each(function() {
          var config = $(this).attr('data-dp-format');
          $(this).datetimepicker({
              "showClose": true,
              "showClear": true,
              "showTodayButton": true,
              "format": config,
              "locale": "en"
          });
        })
      }
    })

    if(!viewOnly){
      $(tables_f).find('tbody').find('tr').last().append(`<td style="border-top: 1px solid #e9ecef;">
        <a href="#"  class="remove_tbl_row fa fa-times" style="color:var(--primary-color);width:100%"></a>
      </td>`)
    }

    $(tables_f).find("tbody").find('tr').eq(-1).on('click','.remove_tbl_row',function() {
      $(tables_f).DataTable().destroy();
      $(this).closest("tr").remove()

      $(tables_f).DataTable(
        {
          searching: false,
          paging: false,
          info: true,
          "bAutoWidth": true,
          "bScrollAutoCss": true,
          lengthChange: false,
          autoWidth: true,
          scrollCollapse: true,
          responsive: true,
          autoWidth: true,
          scrollY: '50vh',
          scrollX: true,
          "sScrollX": "auto",
          "sScrollXInner": "auto",
          ordering: false,
          columnDefs: [
            {
              targets: "_all",
              className: "dt-center allColumnClass all",
            },
            {
              targets: "_all",
              'max-width': "35rem",
            },
            {
              targets: [lastColumnIndex],
              width: '100px',
            },
          ],
        }
      );
    })


    if(viewOnly){
      var table= $(tables_f).DataTable(
        {
          searching: false,
          paging: false,
          info: true,
          "bAutoWidth": true,
          "bScrollAutoCss": true,
          lengthChange: false,
          autoWidth: true,
          scrollCollapse: true,
          responsive: true,
          autoWidth: true,
          scrollY: '50vh',
          scrollX: true,
          "sScrollX": "auto",
          "sScrollXInner": "auto",
          ordering: false,
          columnDefs: [
            {
              targets: "_all",
              className: "dt-center allColumnClass all",
            },
            {
              targets: "_all",
              'max-width': "35rem",
            },
          ],
        }
      );
      setTimeout(() => {
        table.columns.adjust();
      }, 200);
    }
    else{
      var table= $(tables_f).DataTable(
        {
          searching: false,
          paging: false,
          info: true,
          "bAutoWidth": true,
          "bScrollAutoCss": true,
          lengthChange: false,
          autoWidth: true,
          scrollCollapse: true,
          responsive: true,
          autoWidth: true,
          scrollY: '50vh',
          scrollX: true,
          "sScrollX": "auto",
          "sScrollXInner": "auto",
          ordering: false,
          columnDefs: [
            {
              targets: "_all",
              className: "dt-center allColumnClass all",
            },
            {
              targets: "_all",
              'max-width': "35rem",
            },
            {
              targets: [lastColumnIndex],
              width: '100px',
            },
          ],
        }
      );
      setTimeout(() => {
        table.columns.adjust();
      }, 200);
    }
  })

  if(viewOnly){
    data_reload_list = $(this).attr('data-name')
  }else{
    data_reload_list = $(`#id_${fieldname}_${elementID}`).val()
  }

  if(data_reload_list && data_reload_list != ""){
    data_reload_list = JSON.parse(data_reload_list)
    setTimeout(() => {
      for(let i in data_reload_list){
          $(add_newtblf).trigger('click')
          reload_d = data_reload_list[i]
          $(tables_f).find('tbody').find('tr').last().find('td').find('input,select').each(function(){

            if($(this).is(':checkbox')){
              if(reload_d[$(this).attr('data-fname')] == 1){
                $(this).prop("checked",true)
              }else{
                $(this).prop("checked",false)
              }
            } else if ($(this).attr('type') === 'file') {
              $(this).val('').trigger('change');
            }else{
              $(this).val(reload_d[$(this).attr('data-fname')]).trigger('change');
            }

            if(viewOnly){
              $(this).attr("disabled",true)
              $(tablefield_modal).find('.modal-title').text('View Details')
              $(add_newtblf).css('display','none')
              $('.remove_tbl_row').css('display','none')
              $(save_table_field).css('display','none')
            }else{
              $(this).attr("disabled",false)
              $(tablefield_modal).find('.modal-title').text('Add Records')
              $(add_newtblf).css('display','block')
              $('.remove_tbl_row').css('display','block')
              $(save_table_field).css('display','block')
            }
          })
      }
      $(tablefield_modal).modal('show')
    },1000)
  }else{
    $(tablefield_modal).modal('show')
  }

  $(save_table_field).off('click').on('click', function(){

    header_list = []
    $(tables_f).find("thead").find('tr').find('th').each(function(){
            val = $(this).attr('data-fname')
            if(val != undefined){
              header_list.push(val)
            }
    })

    v_dict = []
    temp_dict = {}
    $(tables_f).find("tbody").find('tr').each(function(){
        temp_dict = {}
        $(this).find('td').each(function(idx){
            if($(this).find('input').is(':checkbox')){
              if($(this).find('input').is(":checked")){
                val = 1
              }else{
                val = 0
              }
            }else{
              val = $(this).find('input,select').val()
            }

            if(val != undefined){
                temp_dict[header_list[idx]] = val
            }
        })
        v_dict.push(temp_dict)
    })

    $(`#id_${fieldname}_${elementID}`).val(JSON.stringify(v_dict))
    $(tablefield_modal).modal('hide')
  })
}
  $(".user_logo").select2({
    templateResult: formatState1,
    templateSelection: formatState2
  });

  //drop-down options
  function formatState1 (opt) {
    if (!opt.id) {
        return opt.text;
    }

    var $opt=""
    var optemail = $(opt.element).attr('data-email');
    var optfname = $(opt.element).attr('data-fname');
    if(optfname == undefined || optfname == ''){
      optfname = 'Rev'
    }
    var optlname = $(opt.element).attr('data-lname');
    if(optlname == undefined || optlname == ''){
      optlname = 'Admin'
    }
    var optpic = $(opt.element).attr('data-pic');

    if(opt.text != "----"){
      if(optpic == undefined || optpic == ""){
        if(optfname == "Rev" || optlname == "Admin"){
          $opt = $(
              `<div class="optdiv1">
                <i class="fa fa-user profile_user ddpic"></i>
                <div>
                  <label class="ddpiclabel">${opt.text}</h6>
                  <small>${optemail}</small>
                </div>
              </div>`
          );
        }else{
          $opt = $(
            `<div class="optdiv1">
              <h6 class="ddpic">${optfname[0]}${optlname[0]}</h6>
              <div>
                <label class="ddpiclabel">${opt.text}</h6>
                <small>${optemail}</small>
              </div>
            </div>`
        );
        }
      }else{
        $opt = $(
            `<div class="optdiv1">
            <img class="ddorig" src="${'/media/' + optpic}"/>
            <div>
              <label class="ddoriglabel">${opt.text}</h6>
              <small>${optemail}</small>
            </div>
          </div>`
        );
      }
    }else{
      $opt = opt.text;
    }
    return $opt;
  };

  //on selection of option
  function formatState2 (opt) {
    if (!opt.id) {
        return opt.text;
    }

    var $opt=""
    var optfname = $(opt.element).attr('data-fname');
    if(optfname == undefined || optfname == ''){
      optfname = 'Rev'
    }
    var optlname = $(opt.element).attr('data-lname');
    if(optlname == undefined || optlname == ''){
      optlname = 'Admin'
    }
    var optpic = $(opt.element).attr('data-pic');

    if(opt.text != "----"){
      if(optpic == undefined || optpic == ""){
        if(optfname == "Rev" || optlname == "Admin"){
          $opt = $(
              `<div class="optdiv1">
                <h6 class="fa fa-user profile_user sopic"></h6>
                <label class="solabel">${opt.text}</label>
              </div>`
          );
        }else{
          $opt = $(
            `<div class="optdiv1">
              <h6 class="sopic">${optfname[0]}${optlname[0]}</h6>
              <label class="solabel">${opt.text}</label>
            </div>`
        );
        }
      }else{
        $opt = $(
            `<div class="optdiv2">
            <img src="${'/media/' + optpic}" class="soorig"/>
            <label class="solabel">${opt.text}</label>
          </div>`
        );
      }
    }else{
      $opt = opt.text;
    }
    return $opt;
  };

  function addHtml (sheet_mapping,upload_tables) {

      let name = $(this).attr('name');
      let element_id = $(this).attr("class").replace("renameRemoteColumnBtnExl","")
      let html = ''
      if (Object.keys(sheet_mapping).length > 0){
        html = `
          <div class="row renameColumnGroup" style="margin-top:0.5rem;">
              <div class="col-1" style="color:var(--primary-color); margin:auto;">
                  <i class="fas fa-trash-alt removeRemoteCol" style="cursor"></i>
              </div>
              <div class="col-10" style="margin-left:0.25rem">
                  <label>${name}</label>
                  <div class='row'>
                    <div class='col-6'>
                      <select class="select2 form-control" name="">
                        <option value='' selected disabled>select sheet</option>
          `
        sheetlist = sheet_mapping[name]
        for(let i=0;i<sheetlist.length;i++){
          html = html + `<option value='${sheetlist[i]}'>${sheetlist[i]}</option>`
        }

        html = html + `
            </select>
            </div>
            <div class='col-6'>
              <select class="select2 form-control" name="">
                <option value='' selected disabled>select table</option>
        `
        for(let i=0;i<upload_tables.length;i++){
          html = html + `<option value='${upload_tables[i]}'>${upload_tables[i]}</option>`
        }

        html = html +
            `
                </select>
              </div>
          </div>
          </div>
        `
      }

      $(`#renameRemoteColumnContainer${element_id}`).append(html);
      $(`#renameRemoteColumnContainer${element_id}`).find('.renameColumnGroup').last().find('select.select2').each(function(){
        $(this).select2()
      })

      $('.removeRemoteCol').on('click', function(){
          $(this).parent().parent().remove();
      });
  }

  function sftpUpload(){
    let element_id = $(this).attr("data-elementID")
    let tab_name = $(this).attr("data-tab_name")
    $(`#sftpUploadMapper${element_id}`).find('select.select2').each(function(){
      $(this).select2()
    })
    let upload_tables = []
    let sheet_mapping = {}
    $(`#${element_id}_tab_content`).find('#documenttableUS').find('tbody').find('tr').each(function(){
      upload_tables.push($(this).find('td').eq(0).find('input').val())
    })
      $(`#dropdown1${element_id}`).off('select2:select').on('select2:select',function(){
      if ($(`#dropdown1${element_id}`).val()==='SFTP' || $(`#dropdown1${element_id}`).val()==='FTP' || $(`#dropdown1${element_id}`).val()==='AWS_S3' || $(`#dropdown1${element_id}`).val()==='AZURE'){


        $(`#remote_connection_div${element_id}`).css('display','block')
        $(`#remote_connectionpre_div${element_id}`).css('display','none')
        $(`#remote_connectionfile_div${element_id}`).css('display','none')
        $(`#remote_conn_filepath_div${element_id}`).css('display','none')
        $(`#remote_conn_filetype_div${element_id}`).css('display','none')
        $(`#remote_conn_fileregex_div${element_id}`).css('display','none')
        $(`#remote_connection_name_div${element_id}`).css('display','none')
        $(`#remote_conn_localpath_div${element_id}`).css('display','none')
        $(`#configure_remote_connection${element_id}`).css('display','none')
        $(`.remoteConnectiondropdown${element_id}`).css('display','none')
        $(`.remoteConnectionRenameCard${element_id}`).css('display','none')
        if($(`#dropdown1${element_id}`).val()==='SFTP' || $(`#dropdown1${element_id}`).val()==='FTP'){
            $(`#remote_conn_filepath_div${element_id}`).find('label').text('File path:')
        }else if($(`#dropdown1${element_id}`).val()==='AWS_S3'){
            $(`#remote_conn_filepath_div${element_id}`).find('label').text('Bucket name:')
        }else if($(`#dropdown1${element_id}`).val()==='AZURE'){
            $(`#remote_conn_filepath_div${element_id}`).find('label').text('Container name:')
        }

    }else if ($(`#dropdown1${element_id}`).val()==='LOCAL'){

        $(`#remote_connection_div${element_id}`).css("display","none")
        $(`#configure_remote_connection${element_id}`).css('display','none')
        $(`#remote_conn_filepath_div${element_id}`).css("display","none")
        $(`#remote_conn_filetype_div${element_id}`).css("display","block")
        $(`#remote_conn_fileregex_div${element_id}`).css("display","none")
        $(`#remote_connectionpre_div${element_id}`).css("display","none")
        $(`#remote_connectionfile_div${element_id}`).css("display","none")
        $(`#remote_conn_localpath_div${element_id}`).css("display","block")
        $(`#remote_connection_name_div${element_id}`).css('display','none')
        $(`.remoteConnectiondropdown${element_id}`).css('display','inline-block')
        $(`.remoteConnectionRenameCard${element_id}`).css('display','block')
        $(`#sftpUploadMapper${element_id}`).find('select.select2').each(function(){
          $(this).select2()
        })

    }
  })

    $(`#remote_filetype${element_id}`).off('select2:select').on('select2:select',function(){
        let option_sel = $(`#dropdown1${element_id}`).val()
        let file_sel = $(this).val()

        if(option_sel == "LOCAL" && file_sel){
            if(file_sel == "csv"){
                $(`#customFileLocal${element_id}`).attr("accept",".csv")
            }else if(file_sel == "xlsx"){
                $(`#customFileLocal${element_id}`).attr("accept",".xlsx")
            }

        }
    })

    $(`#customFileLocal${element_id}`).off('change').on('change', function(){
      let file_type = $(`#remote_filetype${element_id}`).val()

      if(file_type == "csv"){
        let files = $(`#customFileLocal${element_id}`).prop('files')
        let names = []
        names = $.map(files, function(val) { return val.name; });
        connectionList = names;

        $(`#renameRemoteColumnDropdown${element_id}`).empty()
        for (let i = 0; i < connectionList.length; i++)
        {
            let displayName = connectionList[i]
            let lastIndex = displayName.lastIndexOf('.');
            let val = displayName.slice(0, lastIndex);
            $(`#renameRemoteColumnDropdown${element_id}`).append(`<li class="dropdown-item"><a href="javascript:void(0)" name='${connectionList[i]}' class="renameRemoteColumnBtn${element_id}">${val}</a></li>`)

        }

        $(`.renameRemoteColumnBtn${element_id}`).off('click').on('click', function () {
            let name = $(this).attr('name');
            html = `
              <div class="row renameColumnGroup" style="margin-top:0.5rem;">
                  <div class="col-1" style="color:var(--primary-color); margin:auto;">
                      <i class="fas fa-trash-alt removeRemoteCol" style="cursor"></i>
                  </div>
                  <div class="col-10" style="margin-left:0.25rem">
                      <label>${name}</label>
                      <select class="select2 form-control" name="">
                      <option value='' selected disabled>select one</option>
              `
              for(let i=0;i<upload_tables.length;i++){
                html = html + `<option value='${upload_tables[i]}'>${upload_tables[i]}</option>`
              }
              html = html +
                `
                      </select>
                  </div>
              </div>
            `
            $(`#renameRemoteColumnContainer${element_id}`).append(html)
            $(`#renameRemoteColumnContainer${element_id}`).find('.renameColumnGroup').last().find('select.select2').each(function(){
              $(this).select2()
            })

            $('.removeRemoteCol').on('click', function(){
                $(this).parent().parent().remove();
            });
        });
      }else if(file_type == "xlsx"){

          let file_input = new FormData($(`#import_data_csv_remote${element_id}`)[0])
          file_input.append('operation', 'get_xlsx_sheetname_sftp')

          $.ajax({
              url: window.location.pathname,
              data: file_input,
              type: 'POST',
              cache: false,
              contentType: false,
              processData: false,
              success: function (data) {
                if(data.hasOwnProperty('sheet_mapping')){
                  sheet_mapping = data["sheet_mapping"]
                }else{
                  sheet_mapping = {}
                }
                sheet_mapping = JSON.stringify(sheet_mapping)
                let files = $(`#customFileLocal${element_id}`).prop('files')
                let names = []
                names = $.map(files, function(val) { return val.name; });
                connectionList = names;
                upload_tables_xl = JSON.stringify(upload_tables)
                $(`#renameRemoteColumnDropdown${element_id}`).empty()
                for (let i = 0; i < connectionList.length; i++)
                {
                    let displayName = connectionList[i]
                    let lastIndex = displayName.lastIndexOf('.');
                    let val = displayName.slice(0, lastIndex);
                    $(`#renameRemoteColumnDropdown${element_id}`).append(`<li class="dropdown-item"><a href="javascript:void(0)" name='${connectionList[i]}' class="renameRemoteColumnBtnExl${element_id}" onclick='addHtml.call(this,${sheet_mapping},${upload_tables_xl})'>${val}</a></li>`)

                }
              },
              error: function () {
                Swal.fire({icon: 'error',text: 'Error! Please try again.'});
              }
          });
      }

  })

    $(`#remote_connection_list${element_id}`).off('select2:select').on('select2:select',function(){
        if ($(`#remote_connection_list${element_id}`).val()==='new_connection')
        {
            $(`#configure_remote_connection${element_id}`).css('display','block')
            $(`#remote_connectionpre_div${element_id}`).css('display','none')
            $(`#remote_connectionfile_div${element_id}`).css('display','none')
            $(`.remoteConnectiondropdown${element_id}`).css('display','none')
            $(`.remoteConnectionRenameCard${element_id}`).css('display','none')
            $(`#remote_conn_filepath_div${element_id}`).css('display','none')
            $(`#remote_conn_filetype_div${element_id}`).css('display','none')
            $(`#remote_conn_fileregex_div${element_id}`).css('display','none')
            $(`#remote_connection_name_div${element_id}`).css('display','block')
        }
        else if($(`#remote_connection_list${element_id}`).val()==='defined_connection')
        {
            $(`#configure_remote_connection${element_id}`).css('display','none')
            $(`#remote_connectionpre_div${element_id}`).css('display','block')
            $(`#remote_connectionfile_div${element_id}`).css('display','block')
            $(`.remoteConnectiondropdown${element_id}`).css('display','inline-block')
            $(`.remoteConnectionRenameCard${element_id}`).css('display','block')
            $(`#remote_conn_filepath_div${element_id}`).css('display','block')
            $(`#remote_conn_filetype_div${element_id}`).css('display','block')
            $(`#remote_conn_fileregex_div${element_id}`).css('display','block')
            $(`#remote_connection_name_div${element_id}`).css('display','none')
            $(`#remote_connectionpre_list${element_id}`).empty()
            $(`#remote_filetype${element_id}`).select2()
            $(`#remote_connectionpre_list${element_id}`).select2()

            $.ajax(
                {
                    url: `/users/${urlPath}/computationModule/`,
                    data: {
                            'operation': 'fetch_remote_connection_list',
                            'remote_type': $(`#dropdown1${element_id}`).val()
                        },
                    type: "POST",
                    dataType: "json",
                    success: function (data)
                    {
                        let connectionList = data["connectionList"];
                        $(`#remote_connectionpre_list${element_id}`).empty()
                        $(`#remote_connectionpre_list${element_id}`).append(`<option value = "" selected disabled>Select Connection</option>`)
                        for (let i = 0; i < connectionList.length; i++)
                        {
                            $(`#remote_connectionpre_list${element_id}`).append(`<option value='${connectionList[i]}'>${connectionList[i]}</option>`)
                        }

                        let reload_data = $(`#remote_connectionpre_list${element_id}`).attr('data-data')
                        if (reload_data){
                            $(`#remote_connectionpre_list${element_id}`).val(reload_data).trigger('change')
                            $(`#remote_connectionpre_list${element_id}`).val(reload_data).trigger('select2:select')
                            $(`#remote_connectionpre_list${element_id}`).removeAttr('data-data')
                        }
                    },
                    error: function ()
                    {
                        Swal.fire({icon: 'error',text: 'Error! Failure in fetching the connection name list. Please try again.'});
                    }
                }
            );

        }

    })

    $(`#remote_connectionpre_list${element_id},.remote_fetchlist`).off('change').on('change',function(){
        $(`#remote_connectionfile_list${element_id}`).empty()
        $(`#renameRemoteColumnDropdown${element_id}`).empty()
        $(`#renameRemoteColumnContainer${element_id}`).empty()
        remote_type = $(`#dropdown1${element_id}`).val()
        call_flag = ""
        if(remote_type == "SFTP" || remote_type == "FTP" || remote_type == "AWS_S3" || remote_type == "AZURE"){
            call_flag = $(`#remote_connectionpre_list${element_id}`).val() && $(`#remote_filetype${element_id}`).val() && $(`#remote_filepath${element_id}`).val()
        }
        if (call_flag)
        {
            $.ajax(
                    {
                        url: `/users/${urlPath}/computationModule/`,
                        data: {
                                'operation': 'fetch_remote_file_list',
                                'connection_name': $(`#remote_connectionpre_list${element_id}`).val(),
                                'file_type': $(`#remote_filetype${element_id}`).val(),
                                'file_path': $(`#remote_filepath${element_id}`).val(),
                                'file_regex': $(`#remote_fileregex${element_id}`).val(),
                                'remote_type': $(`#dropdown1${element_id}`).val(),
                                'upload_comp': "yes",
                            },
                        type: "POST",
                        dataType: "json",
                        success: function (data)
                        {
                            if(data.status != "error"){
                                connectionList = data["file_list"];
                                if(data.hasOwnProperty('sheet_mapping')){
                                  sheet_mapping = data["sheet_mapping"]
                                }else{
                                  sheet_mapping = {}
                                }
                                $(`#remote_connectionfile_list${element_id}`).empty()
                                $(`#renameRemoteColumnDropdown${element_id}`).empty()
                                for (let i = 0; i < connectionList.length; i++)
                                {
                                    let displayName = connectionList[i]
                                    let lastIndex = displayName.lastIndexOf('.');
                                    let val = displayName.slice(0, lastIndex);
                                    $(`#remote_connectionfile_list${element_id}`).append(`<option value='${connectionList[i]}'>${val}</option>`)

                                }
                                $(`#remote_connectionfile_list${element_id}`).select2()

                            }
                        },
                        error: function ()
                        {
                            Swal.fire({icon: 'error',text: 'Error! Failure in fetching the file list. Please try again.'});
                        }
                    }
                );
        }
    })


    $(`#remote_connectionfile_list${element_id}`).off('change').on('change', function(){
      connectionList = $(`#remote_connectionfile_list${element_id}`).val()
      $(`#renameRemoteColumnDropdown${element_id}`).empty()
      for (let i = 0; i < connectionList.length; i++)
      {
          let displayName = connectionList[i]
          let lastIndex = displayName.lastIndexOf('.');
          let val = displayName.slice(0, lastIndex);
          $(`#renameRemoteColumnDropdown${element_id}`).append(`<li class="dropdown-item"><a href="javascript:void(0)" name='${connectionList[i]}' class="renameRemoteColumnBtn${element_id}">${val}</a></li>`)

      }
      $(`.renameRemoteColumnBtn${element_id}`).off('click').on('click', function () {
        let name = $(this).attr('name');
        let html = ''
        if (Object.keys(sheet_mapping).length > 0){
           html = `
            <div class="row renameColumnGroup" style="margin-top:0.5rem;">
                <div class="col-1" style="color:var(--primary-color); margin:auto;">
                    <i class="fas fa-trash-alt removeRemoteCol" style="cursor"></i>
                </div>
                <div class="col-10" style="margin-left:0.25rem">
                    <label>${name}</label>
                    <div class='row'>
                      <div class='col-6'>
                        <select class="select2 form-control" name="">
                          <option value='' selected disabled>select sheet</option>
            `
          sheetlist = sheet_mapping[name]
          for(let i=0;i<sheetlist.length;i++){
            html = html + `<option value='${sheetlist[i]}'>${sheetlist[i]}</option>`
          }

          html = html + `
              </select>
              </div>
              <div class='col-6'>
                <select class="select2 form-control" name="">
                  <option value='' selected disabled>select table</option>
          `
          for(let i=0;i<upload_tables.length;i++){
            html = html + `<option value='${upload_tables[i]}'>${upload_tables[i]}</option>`
          }

          html = html +
              `
                  </select>
                </div>
            </div>
            </div>
          `
        }
        else{
           html = `
            <div class="row renameColumnGroup" style="margin-top:0.5rem;">
                <div class="col-1" style="color:var(--primary-color); margin:auto;">
                    <i class="fas fa-trash-alt removeRemoteCol" style="cursor"></i>
                </div>
                <div class="col-10" style="margin-left:0.25rem">
                    <label>${name}</label>
                    <select class="select2 form-control" name="">
                    <option value='' selected disabled>select one</option>
            `
            for(let i=0;i<upload_tables.length;i++){
              html = html + `<option value='${upload_tables[i]}'>${upload_tables[i]}</option>`
            }
            html = html +
              `
                    </select>
                </div>
            </div>
          `
        }

        $(`#renameRemoteColumnContainer${element_id}`).append(html);
        $(`#renameRemoteColumnContainer${element_id}`).find('.renameColumnGroup').last().find('select.select2').each(function(){
          $(this).select2()
        })

        $('.removeRemoteCol').on('click', function(){
            $(this).parent().parent().remove();
        });
    });
    })

    $(`#remoteConnectionButtonID${element_id}`).off('click').on('click', function(){
        $(`#remote_hostname${element_id}`).val("").trigger('change')
        $(`#remote_username${element_id}`).val("").trigger('change')
        $(`#remote_password${element_id}`).val("").trigger('change')
        if($(`#dropdown1${element_id}`).val() == "SFTP"){
            $(`#remote_username${element_id}`).parent().css("display","block")
            $(`#remote_password${element_id}`).parent().css("display","block")
            $(`#remote_hostname${element_id}`).parent().css("display","block")
            $(`#remote_username${element_id}`).parent().find("label").text("Username")
            $(`#remote_password${element_id}`).parent().find("label").text("Password")
        }else if($(`#dropdown1${element_id}`).val() == "FTP"){
            $(`#remote_username${element_id}`).parent().css("display","none")
            $(`#remote_password${element_id}`).parent().css("display","none")
            $(`#remote_hostname${element_id}`).parent().css("display","block")
            $(`#remote_username${element_id}`).parent().find("label").text("Username")
            $(`#remote_password${element_id}`).parent().find("label").text("Password")
        }else if($(`#dropdown1${element_id}`).val() == "AWS_S3"){
            $(`#remote_hostname${element_id}`).parent().css("display","none")
            $(`#remote_username${element_id}`).parent().css("display","block")
            $(`#remote_password${element_id}`).parent().css("display","block")
            $(`#remote_username${element_id}`).parent().find("label").text("Access key ID")
            $(`#remote_password${element_id}`).parent().find("label").text("Secret access key")
        }else if($(`#dropdown1${element_id}`).val() == "AZURE"){
            $(`#remote_hostname${element_id}`).parent().css("display","none")
            $(`#remote_username${element_id}`).parent().css("display","block")
            $(`#remote_password${element_id}`).parent().css("display","block")
            $(`#remote_username${element_id}`).parent().find("label").text("AccountName")
            $(`#remote_password${element_id}`).parent().find("label").text("AccountKey")
        }
        $(`#remoteConnectionModal${element_id}`).modal('show');
    });

    $(`#validate_remote_connection${element_id}`).off('click').on('click', function() {
        $(`#validate_remote_connection${element_id}`).css('display','none');
        $(`#validate_remote_load${element_id}`).css('display','block');
        $.ajax({
            url: `/users/${urlPath}/computationModule/`,
            data: {
                'operation': 'validate_remote_string',
                'element_id': "",
                'model_name':"upload",
                'connection_name': $(`#remote_connection_name${element_id}`).val(),
                'hostname': $(`#remote_hostname${element_id}`).val(),
                'username': $(`#remote_username${element_id}`).val(),
                'password': $(`#remote_password${element_id}`).val(),
                'remote_type': $(`#dropdown1${element_id}`).val(),
            },
            type: "POST",
            dataType: "json",
            success: function (data) {

              $.ajax({
                url: `/users/${urlPath}/dynamicVal/`,

                data: { 'operation': 'fetch_upload_view_custom_messages',
                        'element_id':  element_id,
                        'messages' : JSON.stringify(["connection_validation_message","invalid_credentials_message"]),
                      },
                type: "POST",
                dataType: "json",
                success: function (response) {

                  if (data.status != "error"){
                    message=""
                    icon=""
                    if(response.connection_validation_message){
                      message = response.connection_validation_message.message
                      icon = response.connection_validation_message.icon
                    }

                    iconHtml = ""
                    if (icon){
                      iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
                    }
                    Swal.fire({icon: 'success',iconHtml,text: message || data.msg});
                    $(`#remoteConnectionModal${element_id}`).modal('hide')
                    $(`#remote_connection_list${element_id}`).val("defined_connection").trigger("change")
                    $(`#remote_connection_list${element_id}`).val("defined_connection").trigger("select2:select")
                    $(`#remote_connectionpre_list${element_id}`).attr('data-data',data.connection_name)
                  }
                  else{
                    message=""
                    icon=""
                    if(response.invalid_credentials_message){
                      message = response.invalid_credentials_message.message
                      icon = response.invalid_credentials_message.icon
                    }

                    iconHtml = ""
                    if (icon){
                      iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
                    }
                    Swal.fire({icon: 'error',iconHtml,text: message || data.msg});
                  }
                  $(`#validate_remote_connection${element_id}`).css('display','block');
                  $(`#validate_remote_load${element_id}`).css('display','none');

                },
                error: function () {
                  Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                }
              })


            },
            error: function () {
                Swal.fire({icon: 'error',text: data.msg});
                $(`#validate_remote_connection${element_id}`).css('display','block');
                $(`#validate_remote_load${element_id}`).css('display','none');
            }
        });
    });

    $(`#savesftpUpload_button_${element_id}`).off('click').on('click', function() {

      let mappingConfig = {};
      let datasource = $(`#dropdown1${element_id}`).val()
      let file_path = $(`#remote_filepath${element_id}`).val()
      let file_type = $(`#remote_filetype${element_id}`).val()
      let connection_name = $(`#remote_connectionpre_list${element_id}`).val()
      let file_regex = $(`#remote_fileregex${element_id}`).val()

      if(file_type == "csv"){
        $(`#renameRemoteColumnContainer${element_id}`).find(".renameColumnGroup").each(function(){
            let currentColName = $(this).find('.col-10').find('label').text();
            let newColName = $(this).find('.col-10').find('select').val();
            mappingConfig[currentColName] = newColName;
        })
      }else{
        let finalmapping = []
        $(`#renameRemoteColumnContainer${element_id}`).find(".renameColumnGroup").each(function(){
            let currentColName = $(this).find('div').eq(1).find('label').text();
            let sheetname = $(this).find('div').eq(1).find('.row').find('div').eq(0).find('select').val();
            let tablename = $(this).find('div').eq(1).find('.row').find('div').eq(1).find('select').val();
            let temp = {}
            mappingConfig = {}
            temp[sheetname] = tablename
            mappingConfig[currentColName] = temp;
            finalmapping.push(mappingConfig)
        })
        mappingConfig = finalmapping
      }

      if(datasource=="SFTP" || datasource=="FTP" || datasource=="AWS_S3" || datasource=="AZURE"){
        $.ajax({
            url:window.location.pathname,
            data: {
                'operation': 'upload_sftp_data',
                'datasource': datasource,
                'file_path': file_path,
                'file_type': file_type,
                'connection_name': connection_name,
                'mappingConfig': JSON.stringify(mappingConfig),
                'file_regex':file_regex,
                'element_id': element_id,
                'tab_name':tab_name,
            },
            type: "POST",
            dataType: "json",
            success: function (data) {

              $(`#sftpUploadMapper${element_id}`).modal('hide');

              $.ajax({
                url: `/users/${urlPath}/dynamicVal/`,

                data: { 'operation': 'fetch_upload_view_custom_messages',
                        'element_id':  element_id,
                        'messages' : JSON.stringify(["validation_failure_message","sent_approval_upload_message","export_successful_message"]),
                      },
                type: "POST",
                dataType: "json",
                success: function (response) {
                  var message =""
                  if(data.icon == "success"){
                    message=""
                    icon=""
                    if(response.export_successful_message){
                      message = response.export_successful_message.message
                      message.replaceAll("{Table Name}", data.table_name)
                      icon = response.export_successful_message.icon
                    }

                    iconHtml = ""
                    if (icon){
                      iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
                    }
                  }
                  else if(data.icon == "info"){
                    message=""
                    icon=""
                    if(response.sent_approval_upload_message){
                      message = response.sent_approval_upload_message.message
                      message.replaceAll("{Table Name}", data.table_name)
                      icon = response.sent_approval_upload_message.icon
                    }

                    iconHtml = ""
                    if (icon){
                      iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
                    }
                  }
                  else if(data.icon == "error"){
                    message=""
                    icon=""
                    if(response.validation_failure_message){
                      message = response.validation_failure_message.message
                      icon = response.validation_failure_message.icon
                    }

                    iconHtml = ""
                    if (icon){
                      iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
                    }
                  }

                  Swal.fire({icon: data.icon,iconHtml, text: message || data.msg}).then((result) => {
                    if (result.isConfirmed) {
                      window.location.reload()
                    }
                  })

                },
                error: function () {
                    Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                }
            })


            },
            error: function () {
                Swal.fire({icon: 'error',text: 'Error! Please try again.'});
            }
        })
      }

    })
  }

  function rftField(){
    let elementID = $(this).parent().find('input').attr("data-element_id")
    let table_name = $(this).parent().find('input').attr("data-tablename")
    let field_name = $(this).parent().find('input').attr("name").replace(table_name+"__","")
    let data_reload = $(this).attr('data-data')

    $('#rtf_field_dialog').attr("data-element_id",elementID)
    $('#rtf_field_dialog').attr("data-table_name",table_name)
    $('#rtf_field_dialog').attr("data-field_name",field_name)
    $('#rtf_field_dialog').modal('show')
    $(`#list_view_edit_modal_${elementID}`).modal('hide')
    if (data_reload){
      CKEDITOR.instances['rtf_field_message'].setData(data_reload)
    } else {
      CKEDITOR.instances['rtf_field_message'].setData('')
    }
  }

  function save_rtf_field_data() {

    let elementID = $('#rtf_field_dialog').attr("data-element_id")
    let field_name = $('#rtf_field_dialog').attr("data-field_name")
    let content = CKEDITOR.instances['rtf_field_message'].getData();
    $(`#id_${field_name}_${elementID}`).val(content).trigger('change')
    $(`#id_${field_name}_${elementID}`).siblings('p[title="RTF editor"]').attr('data-data', content);
    $('#rtf_field_dialog').removeAttr("data-element_id")
    $('#rtf_field_dialog').removeAttr("data-table_name")
    $('#rtf_field_dialog').removeAttr("data-field_name")
    $('#rtf_field_dialog').modal('hide')
    $(`#list_view_edit_modal_${elementID}`).modal('show')
  }

  function showRTFDataListView(){
    let data = $(this).attr("data-data")
    $('#rtf_field_listview_dialog').modal('show')
    if(data){
      CKEDITOR.instances['rtf_field_message_listview'].setData(data)
      let editor = CKEDITOR.instances['rtf_field_message_listview'];
      if (editor) { editor.destroy(true); }
      CKEDITOR.replace('rtf_field_message_listview',{height: 300, removeButtons:'CreateDiv,Anchor,Language,About,PasteText,PasteFromWord,Find,Replace,SelectAll,Scayt,Blockquote,Outdent,Indent,BulletedList,NumberedList,CopyFormatting,RemoveFormat,Bold,Italic,Underline,Strike,Subscript,Superscript,TextColor,BidiLtr,BidiRtl,Templates,Link,Unlink,Source,Save,NewPage,ExportPdf,Preview,Print,Styles,Format,Font,FontSize,BGColor,ShowBlocks,Maximize,JustifyLeft,JustifyCenter,JustifyRight,JustifyBlock,HorizontalRule,SpecialChar,PageBreak,Iframe,Flash,Table,Image,Smiley,Source,Save,Templates,CreateDiv,Unlink,Anchor,Language,Link,Image,Flash,Table,HorizontalRule,SpecialChar,PageBreak,Iframe,ShowBlocks,Maximize,About,Print,Preview,ExportPdf,NewPage,Form,Checkbox,Radio,TextField,Textarea,Select,Button,ImageButton,HiddenField,Smiley,Flash,About,Templates,Cut,Copy,Paste,PasteText,PasteFromWord,Redo,Undo,Find,Replace,SelectAll,Scayt,Form,Checkbox,Radio,TextField,Textarea,Select,Button,ImageButton,HiddenField,Bold,Italic,Underline,Strike,Subscript,Superscript,CopyFormatting,RemoveFormat,Outdent,NumberedList,BulletedList,Indent,Blockquote,JustifyLeft,CreateDiv,JustifyCenter,JustifyRight,JustifyBlock,Language,BidiRtl,BidiLtr,Link,Unlink,Anchor,Image,Table,HorizontalRule,Smiley,SpecialChar,PageBreak,Iframe,Styles,Format,Font,FontSize,TextColor,BGColor,Source,Save,NewPage,ExportPdf,Preview,Print,Templates,PasteText,PasteFromWord,Replace,Find,SelectAll,Scayt,Form,Checkbox,Radio,TextField,Textarea,Select,Button,ImageButton,HiddenField,Bold,BidiLtr,BidiRtl,Language,JustifyRight,JustifyBlock,JustifyCenter,CreateDiv,Indent,BulletedList,NumberedList,Outdent,Blockquote,JustifyLeft,CopyFormatting,RemoveFormat,Styles,Format,Font,FontSize,TextColor,BGColor,ShowBlocks,Maximize,About,Italic,Underline,Strike,Subscript,Superscript'});
      CKEDITOR.config.removePlugins = 'exportpdf,elementspath';
      CKEDITOR.config.resize_enabled = false;
      setTimeout(()=>{CKEDITOR.instances['rtf_field_message_listview'].insertHtml(data, mode="unfiltered_html")
      CKEDITOR.instances['rtf_field_message_listview'].setReadOnly(true);}, 300)
    }
  }
  function showRTFDataCreateView(){
    let data = $(this).attr("data-data")
    $('#rtf_field_createView_dialog').modal('show')
    if(data){
      CKEDITOR.instances['rtf_field_message_createView'].setData(data)
      let editor = CKEDITOR.instances['rtf_field_message_createView'];
      if (editor) { editor.destroy(true); }
      CKEDITOR.replace('rtf_field_message_createView',{height: 300, removeButtons:'CreateDiv,Anchor,Language,About,PasteText,PasteFromWord,Find,Replace,SelectAll,Scayt,Blockquote,Outdent,Indent,BulletedList,NumberedList,CopyFormatting,RemoveFormat,Bold,Italic,Underline,Strike,Subscript,Superscript,TextColor,BidiLtr,BidiRtl,Templates,Link,Unlink,Source,Save,NewPage,ExportPdf,Preview,Print,Styles,Format,Font,FontSize,BGColor,ShowBlocks,Maximize,JustifyLeft,JustifyCenter,JustifyRight,JustifyBlock,HorizontalRule,SpecialChar,PageBreak,Iframe,Flash,Table,Image,Smiley,Source,Save,Templates,CreateDiv,Unlink,Anchor,Language,Link,Image,Flash,Table,HorizontalRule,SpecialChar,PageBreak,Iframe,ShowBlocks,Maximize,About,Print,Preview,ExportPdf,NewPage,Form,Checkbox,Radio,TextField,Textarea,Select,Button,ImageButton,HiddenField,Smiley,Flash,About,Templates,Cut,Copy,Paste,PasteText,PasteFromWord,Redo,Undo,Find,Replace,SelectAll,Scayt,Form,Checkbox,Radio,TextField,Textarea,Select,Button,ImageButton,HiddenField,Bold,Italic,Underline,Strike,Subscript,Superscript,CopyFormatting,RemoveFormat,Outdent,NumberedList,BulletedList,Indent,Blockquote,JustifyLeft,CreateDiv,JustifyCenter,JustifyRight,JustifyBlock,Language,BidiRtl,BidiLtr,Link,Unlink,Anchor,Image,Table,HorizontalRule,Smiley,SpecialChar,PageBreak,Iframe,Styles,Format,Font,FontSize,TextColor,BGColor,Source,Save,NewPage,ExportPdf,Preview,Print,Templates,PasteText,PasteFromWord,Replace,Find,SelectAll,Scayt,Form,Checkbox,Radio,TextField,Textarea,Select,Button,ImageButton,HiddenField,Bold,BidiLtr,BidiRtl,Language,JustifyRight,JustifyBlock,JustifyCenter,CreateDiv,Indent,BulletedList,NumberedList,Outdent,Blockquote,JustifyLeft,CopyFormatting,RemoveFormat,Styles,Format,Font,FontSize,TextColor,BGColor,ShowBlocks,Maximize,About,Italic,Underline,Strike,Subscript,Superscript'});
      CKEDITOR.config.removePlugins = 'exportpdf,elementspath';
      CKEDITOR.config.resize_enabled = false;
      setTimeout(()=>{CKEDITOR.instances['rtf_field_message_createView'].insertHtml(data, mode="unfiltered_html")
      CKEDITOR.instances['rtf_field_message_createView'].setReadOnly(true);}, 300)
    }
  }

  function showRejected_in_tabular(){
    let data = $(this).attr("data-json")
    $('#rejected_records_tabular').find('.modal-body').empty()
    if (data){
      var jsonData = JSON.parse(data)
      var table = "<table id='table-as-field-draft-table'><thead><tr>";

        for (var key in jsonData[0]) {
            if (jsonData[0].hasOwnProperty(key)) {
                table += "<th>" + key + "</th>";
            }
        }

        table += "</tr></thead><tbody>";

        for (var i = 0; i < jsonData.length; i++) {
            table += "<tr>";
            for (var key in jsonData[i]) {
                if (jsonData[i].hasOwnProperty(key)) {
                    table += "<td>" + jsonData[i][key] + "</td>";
                }
            }
            table += "</tr>";
        }

        table += "</tbody></table>";

        $('#rejected_records_tabular').find('.modal-body').append(table)
    }

    var table = $('#rejected_records_tabular').find('.modal-body > table').DataTable(
      {
        autoWidth: true,
        scrollCollapse: true,
        responsive: true,
        autoWidth: true,
        scrollY: '50vh',
        scrollX: true,
        autoWidth: false,
        ordering: false,
        columnDefs: [
          {
            targets: "_all",
            className: "dt-center allColumnClass all",
          },
        ],
      }
    );
    setTimeout(() => {
      table.columns.adjust();
    }, 200);


    $('#rejected_records_tabular').modal('show')

  }

  function showTableDataCreateView(){
    let data = $(this).attr("data-json")
    $('#table_field_createView_dialog').find('.modal-body').empty()
    if (data){
      var jsonData = JSON.parse(data)
      var table = "<table id='table_field_tabular'><thead><tr>";

        for (var key in jsonData[0]) {
            if (jsonData[0].hasOwnProperty(key)) {
                table += "<th>" + key + "</th>";
            }
        }

        table += "</tr></thead><tbody>";

        for (var i = 0; i < jsonData.length; i++) {
            table += "<tr>";
            for (var key in jsonData[i]) {
                if (jsonData[i].hasOwnProperty(key)) {
                    table += "<td>" + jsonData[i][key] + "</td>";
                }
            }
            table += "</tr>";
        }

        table += "</tbody></table>";

        $('#table_field_createView_dialog').find('.modal-body').append(table)
    }
    var table = $('#table_field_createView_dialog').find('.modal-body > table').DataTable(
      {
        autoWidth: true,
        scrollCollapse: true,
        responsive: true,
        autoWidth: true,
        scrollY: '50vh',
        scrollX: true,
        autoWidth: false,
        ordering: false,
        columnDefs: [
          {
            targets: "_all",
            className: "dt-center allColumnClass all",
          },
        ],
      }
    );
    setTimeout(() => {
      table.columns.adjust();
    }, 200);
    $("#draftModal").modal('hide')
    $('#table_field_createView_dialog').modal('show')
  }

  function approval_table_comments_configs(){
    parsedData = JSON.parse($(this).attr('data-data'))
    $('#approval_table_Modal').find('.modal-body').empty()
    var html =`
    <table id="approval_table${$(this).attr('data-s_id')}" class="row-border display" style="width: 100%;">
                        <thead>
                          <tr>
                            <th>Level</th>
                            <th>Approver</th>
                            <th>Comments</th>
                          </tr>
                        </thead>
                        <tbody>
                        </tbody>
                      </table>`
    $('#approval_table_Modal').find('.modal-body').append(html)
    $('#approval_table_Modal').modal("show")

    for (let [key, value] of Object.entries(parsedData)) {
      string =`<tr>`
      string += `<td class="view_details_wrap">${key.split("___")[1]}</td><td class="view_details_wrap">${key.split("___")[0]}</td><td class="view_details_wrap">${value.replaceAll("&rsquo;","'").replaceAll("&rdquo;",'"').replaceAll("&rsquo;","’").replaceAll("&rdquo;",'”').replaceAll("&lsquo;","‘").replaceAll("&ldquo;",'“').replaceAll("\u00a0", " ")}</td>`
      string+=`</tr>`
      $('#approval_table_Modal').find('.modal-body').find('table').find('tbody').append(string)
    }

    var table = $('#approval_table_Modal').find('.modal-body').find('table').DataTable(
      {
        autoWidth: true,
        scrollCollapse: true,
        responsive: true,
        autoWidth: true,
        scrollY: '50vh',
        scrollX: true,
        autoWidth: false,
        ordering: false,
        columnDefs: [
          {
            targets: "_all",
            className: "dt-center allColumnClass all",
          },
        ],
      }
    );
    setTimeout(() => {
      table.columns.adjust();
    }, 200);
  }

  function showHistory_in_tabular(){
    let data = $(this).attr("data-json")
    $('#view_history_tabular').find('.modal-body').empty()
    if (data){
      var jsonData = JSON.parse(data)
      var table = "<table id='table-as-field-history-table'><thead><tr>";

        for (var key in jsonData[0]) {
            if (jsonData[0].hasOwnProperty(key)) {
                table += "<th>" + key + "</th>";
            }
        }

        table += "</tr></thead><tbody>";

        for (var i = 0; i < jsonData.length; i++) {
            table += "<tr>";
            for (var key in jsonData[i]) {
                if (jsonData[i].hasOwnProperty(key)) {
                    table += "<td>" + jsonData[i][key] + "</td>";
                }
            }
            table += "</tr>";
        }

        table += "</tbody></table>";

        $('#view_history_tabular').find('.modal-body').append(table)
    }

    var table = $('#view_history_tabular').find('.modal-body > table').DataTable(
      {
        autoWidth: true,
        scrollCollapse: true,
        responsive: true,
        autoWidth: true,
        scrollY: '50vh',
        scrollX: true,
        autoWidth: false,
        ordering: false,
        columnDefs: [
          {
            targets: "_all",
            className: "dt-center allColumnClass all",
          },
        ],
      }
    );
    setTimeout(() => {
      table.columns.adjust();
    }, 200);


    $('#view_history_tabular').modal('show')

  }

  function EditApprovalData(){
    let elementID = $(this).attr("data-elementID")
    const itemCode = window.location.pathname.split('/')[4];
    let data_to_edit = $(this).parent().find('textarea').val()
    let tablename = $(this).parent().parent().parent().parent().find(`#id_tablename_${elementID}`).val()
    let editapproval_fields = $(this).attr("data-editapproval_fields")
    if (editapproval_fields){
      editapproval_fields = JSON.parse(editapproval_fields)
    }else{
      editapproval_fields = []
    }
    let editapproval_table = $(this).attr("data-editapproval_table")
    let This = $(this)
    if(data_to_edit){
      data_to_edit = JSON.parse(data_to_edit.replaceAll("\\'", "'"))
      data_to_edit = data_to_edit[0]
    }else{
      data_to_edit = []
    }
    let editIndex = []
    let indexCount = 0

    if(data_to_edit){

      $.ajax({
        url: `/users/${urlPath}/${itemCode}/`,
        data: { model_name: tablename,element_id:elementID, operation: 'get_listview_column' },
        type: 'POST',
        dataType: 'json',
        success: function (data) {

          $(`#tables_edit_json_${elementID}`).find('.editjson_tblef_tableHeader').empty()
          $(`#tables_edit_json_${elementID}`).find('tbody').empty()

          $.each(Object.keys(data), function (key, value) {
            if(data[value].internal_type != "UniqueIDField" && data_to_edit.hasOwnProperty(Object.keys(data)[key])){
              const vname = data[value].verbose_name
              $(`#tables_edit_json_${elementID}`).find('.editjson_tblef_tableHeader').append(`<th data-fname=${Object.keys(data)[key]} style="width:150px;text-align: center;white-space: pre-line;">&nbsp;&nbsp;${vname}</th>`)

              if(editapproval_table && editapproval_fields.length){
                if(editapproval_fields.includes(Object.keys(data)[key]))
                  editIndex.push(indexCount)
                  indexCount++
              }
            }
          })


          $(`#tables_edit_json_${elementID}`).find('tbody').append('<tr style="display: flex;justify-content: space-around;align-items:flex-start"></tr>')
          $.each(Object.keys(data), function (key, value) {
            const ftype = data[value].internal_type
            if(ftype != "UniqueIDField"){
              let settype;
              if (String(ftype) === 'ForeignKey' && data_to_edit.hasOwnProperty(Object.keys(data)[key])) {
                settype = 'text'
                $(`#tables_edit_json_${elementID}`).find('tbody').find('tr').last().append(`
                <td>
                    <select data-fname="${Object.keys(data)[key]}" style="width:150px;" form="columnform" class="form-control select2 p-2 ${elementID}_${Object.keys(data)[key]}">
                    </select>
                </td>
                    `)
                $.each(Object.keys(data), function (key1, value1) {
                  if (String(data[value1].internal_type) === 'ForeignKey') {
                    const choice = data[value1].Choices
                    for (const [k, v] of Object.entries(choice)) {
                      $(`.${elementID}_${Object.keys(data)[key]}`).last().append(
                        `<option name="${v}" value="${k}">${v}</option>`
                      )
                    }
                  }
                })

                if(data_to_edit.hasOwnProperty(Object.keys(data)[key])){
                  $(`#tables_edit_json_${elementID}`).find('tbody').find('tr').last().find(`select[data-fname="${Object.keys(data)[key]}"]`).val(data_to_edit[Object.keys(data)[key]]).trigger("change")
                }

              } else {
                if ((String(ftype) === 'TextField' || String(ftype) === 'ConcatenationField' || String(ftype) === 'CardField' || String(ftype) === 'CardCvvField' || String(ftype) === 'CardTypeField' || String(ftype) === 'RTFField' || String(ftype) === 'MultiselectField') && data_to_edit.hasOwnProperty(Object.keys(data)[key])) {
                  settype = 'text'
                  $(`#tables_edit_json_${elementID}`).find('tbody').find('tr').last().append(`<td>
                  <input data-fname="${Object.keys(data)[key]}" type="${settype}" class="form-control p-2" style="width:150px;">
                  </td>
                  `)

                  if(data_to_edit.hasOwnProperty(Object.keys(data)[key])){
                    $(`#tables_edit_json_${elementID}`).find('tbody').find('tr').last().find(`input[data-fname="${Object.keys(data)[key]}"]`).val(data_to_edit[Object.keys(data)[key]]).trigger("change")
                  }
                } else if (String(ftype) === 'DateTimeField' && data_to_edit.hasOwnProperty(Object.keys(data)[key])) {
                  settype = 'datetime-local'
                  $(`#tables_edit_json_${elementID}`).find('tbody').find('tr').last().append(`<td>
                  <input data-fname="${Object.keys(data)[key]}" type="${settype}" step="1" class="form-control datetimepickerinput p-2" style="width:150px;">
                  </td>
                  `)

                  if(data_to_edit.hasOwnProperty(Object.keys(data)[key])){
                    $(`#tables_edit_json_${elementID}`).find('tbody').find('tr').last().find(`input[data-fname="${Object.keys(data)[key]}"]`).val(data_to_edit[Object.keys(data)[key]]).trigger("change")
                  }
                } else if (String(ftype) === 'DateField' && data_to_edit.hasOwnProperty(Object.keys(data)[key])) {
                  settype = 'date'
                  $(`#tables_edit_json_${elementID}`).find('tbody').find('tr').last().append(`<td>
                  <input data-fname="${Object.keys(data)[key]}" type="${settype}" step="1" class="form-control datetimepickerinput p-2" style="width:150px;">
                  </td>
                  `)

                  if(data_to_edit.hasOwnProperty(Object.keys(data)[key])){
                    $(`#tables_edit_json_${elementID}`).find('tbody').find('tr').last().find(`input[data-fname="${Object.keys(data)[key]}"]`).val(data_to_edit[Object.keys(data)[key]]).trigger("change")
                  }
                } else if (String(ftype) === 'TimeField' && data_to_edit.hasOwnProperty(Object.keys(data)[key])) {
                  settype = 'time'
                  use_sec = data[value].use_seconds
                  if(use_sec == "false"){
                    $(`#tables_edit_json_${elementID}`).find('tbody').find('tr').last().append(`<td>
                    <input data-fname="${Object.keys(data)[key]}" type="${settype}" class="form-control timepickerinput p-2" style="width:150px;" data-dp-format="HH:mm">
                    </td>
                    `)
                  }else{
                      $(`#tables_edit_json_${elementID}`).find('tbody').find('tr').last().append(`<td>
                    <input data-fname="${Object.keys(data)[key]}" type="${settype}" class="form-control timepickerinput p-2" style="width:150px;" data-dp-format="HH:mm:ss">
                    </td>
                    `)
                  }

                  if(data_to_edit.hasOwnProperty(Object.keys(data)[key])){
                    $(`#tables_edit_json_${elementID}`).find('tbody').find('tr').last().find(`input[data-fname="${Object.keys(data)[key]}"]`).val(data_to_edit[Object.keys(data)[key]]).trigger("change")
                  }
                } else if (String(ftype) === 'EmailTypeField' && data_to_edit.hasOwnProperty(Object.keys(data)[key])) {
                  settype = 'email'
                  $(`#tables_edit_json_${elementID}`).find('tbody').find('tr').last().append(`<td>
                  <input data-fname="${Object.keys(data)[key]}" type="${settype}" class="form-control p-2" style="width:150px;">
                  </td>
                  `)

                  if(data_to_edit.hasOwnProperty(Object.keys(data)[key])){
                    $(`#tables_edit_json_${elementID}`).find('tbody').find('tr').last().find(`input[data-fname="${Object.keys(data)[key]}"]`).val(data_to_edit[Object.keys(data)[key]]).trigger("change")
                  }
                } else if (String(ftype) === 'UniqueIDField' && data_to_edit.hasOwnProperty(Object.keys(data)[key])) {
                  settype = 'text'
                  $(`#tables_edit_json_${elementID}`).find('tbody').find('tr').last().append(`<td>
                  <input data-fname="${Object.keys(data)[key]}" type="${settype}" class="form-control p-2" style="width:150px;" disabled>
                  </td>
                  `)

                  if(data_to_edit.hasOwnProperty(Object.keys(data)[key])){
                    $(`#tables_edit_json_${elementID}`).find('tbody').find('tr').last().find(`input[data-fname="${Object.keys(data)[key]}"]`).val(data_to_edit[Object.keys(data)[key]]).trigger("change")
                  }
                } else if (String(ftype) === 'BooleanField' && data_to_edit.hasOwnProperty(Object.keys(data)[key])) {
                  settype = "checkbox"
                  $(`#tables_edit_json_${elementID}`).find('tbody').find('tr').last().append(`<td style="padding-left:3rem;padding-right:3rem;">
                  <input type='checkbox' data-fname="${Object.keys(data)[key]}" class="form-control p-2">
                  </td>
                  `)

                  if(data_to_edit.hasOwnProperty(Object.keys(data)[key])){
                    if(data_to_edit[Object.keys(data)[key]]){
                      $(`#tables_edit_json_${elementID}`).find('tbody').find('tr').last().find(`input[data-fname="${Object.keys(data)[key]}"]`).prop("checked",true)
                    }
                  }
                } else if (String(ftype) === 'CharField' && data_to_edit.hasOwnProperty(Object.keys(data)[key])) {
                  settype = 'text'
                  choices = []
                  if(data[value].hasOwnProperty("choices")){
                    choices = data[value].choices
                  }else{
                    choices = []
                  }
                  const temp = new Set()
                  for(let i=0;i<choices.length;i++){
                      for(let j=0;j<choices[i].length;j++){
                          temp.add(choices[i][j])
                      }
                  }
                  const temp1 = [...temp];
                  if(choices.length > 0){
                    $(`#tables_edit_json_${elementID}`).find('tbody').find('tr').last().append(`<td>
                    <select data-fname="${Object.keys(data)[key]}" style="width:150px;" form="columnform" class="form-control select2 p-2 ${elementID}_${Object.keys(data)[key]}">
                    </select>
                    `)

                    for (let i=0;i<temp1.length;i++) {
                      $(`.${elementID}_${Object.keys(data)[key]}`).last().append(
                        `<option name="${temp1[i]}" value="${temp1[i]}">${temp1[i]}</option>`
                      )
                    }

                    if(data_to_edit.hasOwnProperty(Object.keys(data)[key])){
                      $(`#tables_edit_json_${elementID}`).find('tbody').find('tr').last().find(`select[data-fname="${Object.keys(data)[key]}"]`).val(data_to_edit[Object.keys(data)[key]]).trigger("change")
                    }

                  }else{
                    $(`#tables_edit_json_${elementID}`).find('tbody').find('tr').last().append(`<td>
                    <input data-fname="${Object.keys(data)[key]}" type="${settype}" class="form-control p-2" style="width:150px;">
                    </td>
                    `)

                    if(data_to_edit.hasOwnProperty(Object.keys(data)[key])){
                      $(`#tables_edit_json_${elementID}`).find('tbody').find('tr').last().find(`input[data-fname="${Object.keys(data)[key]}"]`).val(data_to_edit[Object.keys(data)[key]]).trigger("change")
                    }
                  }

                } else if (String(ftype) === 'URLField' && data_to_edit.hasOwnProperty(Object.keys(data)[key])) {
                  settype = 'url'
                  $(`#tables_edit_json_${elementID}`).find('tbody').find('tr').last().append(`<td>
                  <input data-fname="${Object.keys(data)[key]}" type="${settype}" class="form-control p-2" style="width:150px;">
                  </td>
                  `)

                  if(data_to_edit.hasOwnProperty(Object.keys(data)[key])){
                    $(`#tables_edit_json_${elementID}`).find('tbody').find('tr').last().find(`input[data-fname="${Object.keys(data)[key]}"]`).val(data_to_edit[Object.keys(data)[key]]).trigger("change")
                  }
                } else if (String(ftype) === 'FileField' && data_to_edit.hasOwnProperty(Object.keys(data)[key])) {
                  settype = 'file'
                  accept = "*"
                  if (data[value].file_extension){
                    if (data[value].file_extension == "Any"){
                      accept = "*"
                    }
                    else if (data[value].file_extension == "Images"){
                      accept = "image/*"
                    }
                    else if (data[value].file_extension == "Document"){
                      accept=".doc,.docx,.rtf,.pdf,.csv,xlsx,.odt,.docx,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    }
                    else if (data[value].file_extension == "PDF"){
                      accept=".pdf"
                    }
                  }

                  $(`#tables_edit_json_${elementID}`).find('tbody').find('tr').last().append(`<td>
                  <input accept=${accept} type='file' data-fname="${Object.keys(data)[key]}" data-existing-value="${data_to_edit[Object.keys(data)[key]]}" class='form-control p-2' style="width:150px;" multiple>
                  </td>
                  `)

                } else if (String(ftype) === 'UserField' && data_to_edit.hasOwnProperty(Object.keys(data)[key])) {
                  settype = 'text'
                  $(`#tables_edit_json_${elementID}`).find('tbody').find('tr').last().append(`
                  <td>
                      <select data-fname="${Object.keys(data)[key]}" style="width:150px;" form="columnform" class="form-control select2 p-2 ${elementID}_${Object.keys(data)[key]}">
                      </select>
                  </td>
                      `)
                  $.each(Object.keys(data), function (key1, value1) {
                    if (String(data[value1].internal_type) === 'UserField') {
                      const choice = data[value1].Choices
                      for (let i in choice) {
                        $(`.${elementID}_${Object.keys(data)[key]}`).last().append(
                          `<option name="${choice[i]}" value="${choice[i]}">${choice[i]}</option>`
                        )
                      }
                    }
                  })

                  if(data_to_edit.hasOwnProperty(Object.keys(data)[key])){
                    $(`#tables_edit_json_${elementID}`).find('tbody').find('tr').last().find(`select[data-fname="${Object.keys(data)[key]}"]`).val(data_to_edit[Object.keys(data)[key]]).trigger("change")
                  }
                } else {
                  if(data_to_edit.hasOwnProperty(Object.keys(data)[key])){
                    settype = 'number'
                    $(`#tables_edit_json_${elementID}`).find('tbody').find('tr').last().append(`<td>
                    <input data-fname="${Object.keys(data)[key]}" type="${settype}" step="1" class="form-control p-2" style="width:150px;">
                    </td>
                    `)

                    if(data_to_edit.hasOwnProperty(Object.keys(data)[key])){
                      $(`#tables_edit_json_${elementID}`).find('tbody').find('tr').last().find(`input[data-fname="${Object.keys(data)[key]}"]`).val(data_to_edit[Object.keys(data)[key]]).trigger("change")
                    }
                  }
                }

              }

              $(`#tables_edit_json_${elementID}`).find("tbody").find('tr').last().find('select').each(function() {
                $(this).select2()
              })

              $(`#tables_edit_json_${elementID}`).find("tbody").find('tr').last().find('.timepickerinput').each(function() {
                var config = $(this).attr('data-dp-format');
                $(this).datetimepicker({
                    "showClose": true,
                    "showClear": true,
                    "showTodayButton": true,
                    "format": config,
                    "locale": "en"
                });
              })
            }
          })

          if(editIndex.length > 0){
            for(let i=0;i<editIndex.length;i++){
              $(`#tables_edit_json_${elementID}`).find('thead').find('tr').find('th').eq(editIndex[i]).css("display","none")
              $(`#tables_edit_json_${elementID}`).find('tbody').find('tr').find('td').eq(editIndex[i]).css("display","none")
            }
          }

          $(`#list_view_edit_json_modal_${elementID}`).modal('show')

        },
        error: function () {
          Swal.fire({icon: 'error',text: 'Error! Please try again.'});
        },
      })

    }

    $(`#save_editjson_field_${elementID}`).off("click").on("click", function(){

      header_list = []
      $(`#tables_edit_json_${elementID}`).find("thead").find('tr').find('th').each(function(){
              val = $(this).attr('data-fname')
                header_list.push(val)
      })

      v_dict = []
      temp_dict = {}
      $(`#tables_edit_json_${elementID}`).find("tbody").find('tr').each(function(){
          temp_dict = {}
          $(this).find('td').each(function(idx){
              if($(this).find('input').is(':checkbox')){
                if($(this).find('input').is(":checked")){
                  val = 1
                }else{
                  val = 0
                }
              }else{
                if ($(this).find('input[type="file"]').length) {
                  if (!$(this).find('input').val()) {
                    val = $(this).find('input').attr('data-existing-value');
                  } else {
                    val = $(this).find('input,select').val();
                  }
                } else {
                  val = $(this).find('input,select').val()
                }
              }

              temp_dict[header_list[idx]] = val
          })
          v_dict.push(temp_dict)
      })

      temp_v_dict = v_dict[0]
      data_to_edit_temp = data_to_edit

      for (let [key, value] of Object.entries(data_to_edit_temp)) {
        if(!(key in temp_v_dict)){
          temp_v_dict[key] = value
        }
      }

      $(This).parent().find('textarea').val(JSON.stringify([temp_v_dict]))
      $(`#list_view_edit_json_modal_${elementID}`).modal('hide')

    })
  }

function EditApprovalGroupUser(){

  let elementID = $(this).attr("data-elementID")
  let ug_iden = $(this).attr("data-ug_iden")
  maximum_levels_allowed = $(`#list_view_edit_modal_${elementID}`).attr("data-maximum_levels_allowed")
  maximum_approvers_allowed = $(`#list_view_edit_modal_${elementID}`).attr("data-maximum_approvers_allowed")

  $(`#select_edit_user_${elementID}`).select2({
    maximumSelectionLength: maximum_approvers_allowed,
  })
  $(`#select_edit_group_${elementID}`).select2({
    maximumSelectionLength: maximum_approvers_allowed,
  })

  if(ug_iden == "approver group"){

    let approver_group_val = $(this).parent().find("input").val()
    if (approver_group_val){
      approver_group_val = JSON.parse(approver_group_val)
    }

    $(`#select_edit_user_${elementID}`).parent().css("display","none")
    $(`#select_edit_group_${elementID}`).parent().css("display","block")
    $(`#select_edit_group_${elementID}`).val(approver_group_val).trigger("change")

  }else{

    let approver_user_val = $(this).parent().find("input").val()
    if (approver_user_val){
      approver_user_val = JSON.parse(approver_user_val)
    }

    $(`#select_edit_user_${elementID}`).parent().css("display","block")
    $(`#select_edit_group_${elementID}`).parent().css("display","none")
    $(`#select_edit_user_${elementID}`).val(approver_user_val).trigger("change")

  }
  $(`#list_view_edit_approver_data_modal_${elementID}`).modal('show')

  $(`#save_editapprover_data_field_${elementID}`).off('click').on('click', function(){
    $(`#list_view_edit_approver_data_modal_${elementID}`).modal('hide')
    $(`#approvalCommentModal_${elementID}`).find('.modal-title').text('Approval Level Change Comment');
    $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').text('Save comment');
    $(`#approvalCommentModal_${elementID}`).css('display', 'block')
    $(`#approvalCommentModal_${elementID}`).css('opacity', 1)
    $(`#approvalCommentModal_${elementID}`).css('z-index', 2000)
    $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').removeAttr('onclick');

    $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').off('click').on('click', function(){
      let approval_comment = CKEDITOR.instances[`approvalCommentText${elementID}`].getData().replaceAll("&#39;", "&rsquo;").replaceAll("&quot", "&rdquo;");
      $(`#list_view_edit_modal_${elementID}`).find('input[name="approval_level_change_comment_edit"]').attr('value',approval_comment)
      if(ug_iden == "approver group"){
        new_group_vals = $(`#select_edit_group_${elementID}`).val()
        $(`#id_approver_group_${elementID}`).val(JSON.stringify(new_group_vals)).trigger("change")
      }else{
        new_user_vals = $(`#select_edit_user_${elementID}`).val()
        $(`#id_approver_user_${elementID}`).val(JSON.stringify(new_user_vals)).trigger("change")
      }
      $(`#approvalCommentModal_${elementID}`).css('z-index', 1050)
      $(`#approvalCommentModal_${elementID}`).css('opacity', 0)
      $(`#approvalCommentModal_${elementID}`).css('display', 'none')
      $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("onclick","approve_ind.call(this)")
    })

    $(`#approvalCommentModal_${elementID}`).find('.close').on('click', function () {
      $(`#approvalCommentModal_${elementID}`).css('z-index', 1050)
      $(`#approvalCommentModal_${elementID}`).css('opacity', 0)
      $(`#approvalCommentModal_${elementID}`).css('display', 'none')
      $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("onclick","approve_ind.call(this)")
      $(`#list_view_edit_approver_data_modal_${elementID}`).modal('show')
    })


  })

}
  function approval_table_audit_logs(user_list,reorderAuditDict) {
    pdata = $(this).attr('data-data').replaceAll("'",'"')
    pdata = pdata.replaceAll('\\\\"',"'")
    pdata = pdata.replaceAll("\\'",'"')
    parsedData = JSON.parse(pdata)
    let main_dict = {"Time":"time", "Action":"action", "User":"user", "Value":"value", "Level":"level"}
    let def_header_list = ["Level","Action","User","Time","Value"]

    if (Object.keys(reorderAuditDict).length > 0){
      def_header_list = Object.values(reorderAuditDict)
    }

    for(let i=0; i<parsedData.length; i++){
      for (let [key, value] of Object.entries(parsedData[i])) {

        for (let j=0; j<value.length; j++) {
          value[j]["level"] = key
        }
      }
    }

    if (Object.keys(reorderAuditDict).length > 0){
      let newPdata = []
      let newdict = {}
      for(let i=0; i<parsedData.length; i++){
        for (let [key, value] of Object.entries(parsedData[i])) {
          newdict = {}
          newdict[key] = []
            for (let j=0;j<value.length;j++){
              tt = {}
              for (let [key1, value1] of Object.entries(reorderAuditDict)) {

                tt[main_dict[value1]] = value[j][main_dict[value1]]

            }

            newdict[key].push(tt)
          }
          newPdata.push(newdict)
        }
      }

      parsedData = newPdata
    }

    let columnAlignment = {};
    let columnAlignmentDef = [];
    if ($(this).attr('data-column-alignment')) {
      columnAlignment = JSON.parse($(this).attr('data-column-alignment'));
    } else {
      columnAlignmentDef.push(
        {
          targets: "_all",
          className: 'dt-center allColumnClass all',
        }
      )
    }
    $('#approval_table_Modal').find('.modal-header').find('h5').text("Approval Table")
    $('#approval_table_Modal').find('.modal-body').empty()

    var html =`
    <table id="approval_table${$(this).attr('data-s_id')}" class="row-border display" style="width: 100%;">
                        <thead>
                          <tr>`
    for(let i=0;i<def_header_list.length;i++){
      if(def_header_list[i] == "Value"){
        html = html + `<th style="width: 15rem;">${def_header_list[i]}</th>`
      } else {
        html = html + `<th>${def_header_list[i]}</th>`
      }
    }

    html = html + `
                          </tr>
                        </thead>
                        <tbody>
                        </tbody>
                      </table>`
    $('#approval_table_Modal').find('.modal-body').append(html)
    $('#approval_table_Modal').find('.modal-header').find('h5').text("Approval audit log")
    $('#approval_table_Modal').modal("show")

    for(let i=0; i<parsedData.length; i++){
      for (let [key, value] of Object.entries(parsedData[i])) {
        string =`<tr>`
        string_bk = string
        for(let j=0; j<value.length; j++){
          string2 = ""
          for (let [k, v] of Object.entries(value[j])) {
            if (k == "value" && v && v.constructor !== Array) {
              if (v.indexOf(" from ") != -1 && v.indexOf(" to ") != -1 && value[j].action != "Comment") {
                var htmlString = '';
                var fromIndex = v.indexOf("from ");
                var toIndex = v.indexOf(" to ");
                var fieldText = v.slice(0, fromIndex);
                var fromContent = v.slice(fromIndex, toIndex).split("from ")[1];
                var toContent = v.slice(toIndex).split(" to ")[1];
                if (v.startsWith("approval_level_config")) {
                  var fromObject = JSON.parse(fromContent.replaceAll("'", '"'));
                  var toObject = JSON.parse(toContent.replaceAll("'", '"'));
                  var fromTHeadString = '';
                  var fromTBodyString = '';
                  for (let levelNumber in fromObject['level_config']) {
                    fromTBodyString += `<tr><td>${levelNumber}</td>`;
                    for (let [kLevel, valLevel] of Object.entries(fromObject["level_config"][levelNumber])){
                      if(kLevel == "user_list"){
                        tmp = []
                        for(let jLevel=0;jLevel<valLevel.length;jLevel++){
                          if(valLevel[jLevel] in user_list){
                            tmp.push(user_list[valLevel[jLevel]])
                          } else {
                            tmp.push(valLevel[jLevel])
                          }
                        }
                        valLevel = tmp
                      }
                      fromTBodyString += `<td style="text-align:left;">${valLevel}</td>`
                    }
                    fromTBodyString += '</tr>';
                  }
                  fromTHeadString += `<th>Level</th>`;
                  for (let header of Object.keys(fromObject['level_config'][0])) {
                    fromTHeadString += `<th>${header}</th>`;
                  }
                  var fromHTML = `<table class="row-border"><thead><tr>${fromTHeadString}</tr></thead><tbody>${fromTBodyString}</tbody></table>`;

                  var toTHeadString = '';
                  var toTBodyString = '';
                  for (let levelNumber in toObject['level_config']) {
                    toTBodyString += `<tr><td>${levelNumber}</td>`;
                    for (let [kLevel, valLevel] of Object.entries(toObject["level_config"][levelNumber])){
                      if(kLevel == "user_list"){
                        tmp = []
                        for(let jLevel=0;jLevel<valLevel.length;jLevel++){
                          if(valLevel[jLevel] in user_list){
                            tmp.push(user_list[valLevel[jLevel]])
                          } else {
                            tmp.push(valLevel[jLevel])
                          }
                        }
                        valLevel = tmp
                      }
                      toTBodyString += `<td style="text-align:left;">${valLevel}</td>`
                    }
                    toTBodyString += '</tr>';
                  }
                  toTHeadString += `<th>Level</th>`;
                  for (let header of Object.keys(toObject['level_config'][0])) {
                    toTHeadString += `<th>${header}</th>`;
                  }
                  var toHTML = `<table class="row-border"><thead><tr>${toTHeadString}</tr></thead><tbody>${toTBodyString}</tbody></table>`;

                  var fromHTML = `<table class="row-border"><thead><tr>${fromTHeadString}</tr></thead><tbody>${fromTBodyString}</tbody></table>`;
                } else {
                  var fromHTML = fromContent;
                  var toHTML = toContent;
                }
                htmlString = `<div><p style="text-align:center;">${fieldText}</p><p style="text-align:center;margin-bottom:0;">From</p><p>${fromHTML}</p><p style="text-align:center;margin-bottom:0;">To</p><p>${toHTML}</p></div>`;
                v = htmlString;
              }
            }
            if(k == "value"){
              v = String(v).replaceAll(/\\r/g, '<br>');
              v = v.replaceAll(/\\n/g, '<br>');
              v = v.replaceAll(/\\t/g, '&nbsp;&nbsp;');
              v = String(v).replaceAll(/<p><\/p>/g, '');
              v = v.replaceAll(/<br><br>/g, '<br>');
              string2 += `<td><div style="white-space: normal;max-width: 47rem; display:flex; flex-direction:column;word-break: break-word;"><p>${v}</p></div></td>`
            }else{
              if(k == "user"){
                if(v in user_list){
                  string2 += `<td>${user_list[v]}</td>`
                }else{
                  string2 += `<td>${v}</td>`
                }
              }else{
                string2 += `<td>${v}</td>`
              }
            }
          }
          string = string_bk + string2 + `</tr>`
          $('#approval_table_Modal').find('.modal-body > table > tbody').append(string)
        }
      }
    }

    if (Object.keys(columnAlignment).length > 0) {
      var globalHeader = "center";
      var globalContent = "center";
      if (columnAlignment.global_header) {
        globalHeader = columnAlignment['global_header'];
      }
      if (columnAlignment.global_content) {
        globalContent = columnAlignment['global_content'];
      }
      if (columnAlignment.field_level_config['Level'].header && columnAlignment.field_level_config['Level'].content) {
        var header = columnAlignment.field_level_config['Level']['header'];
        var content = columnAlignment.field_level_config['Level']['content'];
        columnAlignmentDef.push(
          {
            targets: [0],
            className: `dt-head-${header} dt-body-${content} allColumnClass all`,
          }
        )
      } else {
        columnAlignmentDef.push(
          {
            targets: [0],
            className: `dt-head-${globalHeader} dt-body-${globalContent} allColumnClass all`,
          }
        )
      }
      if (columnAlignment.field_level_config['Action'].header && columnAlignment.field_level_config['Action'].content) {
        var header = columnAlignment.field_level_config['Action']['header'];
        var content = columnAlignment.field_level_config['Action']['content'];
        columnAlignmentDef.push(
          {
            targets: [1],
            className: `dt-head-${header} dt-body-${content} allColumnClass all`,
          }
        )
      } else {
        columnAlignmentDef.push(
          {
            targets: [1],
            className: `dt-head-${globalHeader} dt-body-${globalContent} allColumnClass all`,
          }
        )
      }
      if (columnAlignment.field_level_config['User'].header && columnAlignment.field_level_config['User'].content) {
        var header = columnAlignment.field_level_config['User']['header'];
        var content = columnAlignment.field_level_config['User']['content'];
        columnAlignmentDef.push(
          {
            targets: [2],
            className: `dt-head-${header} dt-body-${content} allColumnClass all`,
          }
        )
      } else {
        columnAlignmentDef.push(
          {
            targets: [2],
            className: `dt-head-${globalHeader} dt-body-${globalContent} allColumnClass all`,
          }
        )
      }
      if (columnAlignment.field_level_config['Time'].header && columnAlignment.field_level_config['Time'].content) {
        var header = columnAlignment.field_level_config['Time']['header'];
        var content = columnAlignment.field_level_config['Time']['content'];
        columnAlignmentDef.push(
          {
            targets: [3],
            className: `dt-head-${header} dt-body-${content} allColumnClass all`,
          }
        )
      } else {
        columnAlignmentDef.push(
          {
            targets: [3],
            className: `dt-head-${globalHeader} dt-body-${globalContent} allColumnClass all`,
          }
        )
      }
      if (columnAlignment.field_level_config['Value'].header && columnAlignment.field_level_config['Value'].content) {
        var header = columnAlignment.field_level_config['Value']['header'];
        var content = columnAlignment.field_level_config['Value']['content'];
        columnAlignmentDef.push(
          {
            targets: [4],
            className: `dt-head-${header} dt-body-${content} allColumnClass all`,
          }
        )
      } else {
        columnAlignmentDef.push(
          {
            targets: [4],
            className: `dt-head-${globalHeader} dt-body-${globalContent} allColumnClass all`,
          }
        )
      }
    }else{
      columnAlignmentDef.push(
        {
          targets: "_all",
          className: 'dt-center allColumnClass all',
        }
      )
    }

    var table = $('#approval_table_Modal').find('.modal-body > table').DataTable(
      {
        autoWidth: true,
        scrollCollapse: true,
        responsive: true,
        scrollY: '50vh',
        scrollX: true,
        ordering: false,
        columnDefs: columnAlignmentDef,
      }
    );
    setTimeout(() => {
      table.columns.adjust();
    }, 200);
  }

  function EditAppLevelConfig(){

    let elementID = $(this).attr("data-elementID")
    let jdata = $(this).parent().find("textarea").val()
    let group_present = false
    if(jdata){
      jdata = JSON.parse(jdata)
    }
    let app_table_sep = $(this).attr("data-app_table_sep")
    if(app_table_sep == undefined){
      app_table_sep = " "
    }
    let app_table_cols = $(this).attr("data-app_table_cols")
    if(app_table_cols == undefined){
      app_table_cols = JSON.stringify(["username","first_name","last_name"])
    }
    $(`#modalBody${elementID}_applevel`).find('.card-body').find(".newlevel").remove()
    $.ajax({
        url: `/users/${urlPath}/dynamicVal/`,
        data: {
            'operation': 'get_user_group_list',
            'app_table_sep':app_table_sep,
            'app_table_cols':app_table_cols,
        },
        type: "POST",
        dataType: "json",
        success: function (data) {
          user_list = data.user_list
          group_list = data.group_list
          maximum_levels_allowed = $(`#list_view_edit_modal_${elementID}`).attr("data-maximum_levels_allowed")
          maximum_approvers_allowed = $(`#list_view_edit_modal_${elementID}`).attr("data-maximum_approvers_allowed")

          $(`#modalBody${elementID}_applevel`).find('.card-body').find(".disabled_lists").empty()
          $(`#modalBody${elementID}_applevel`).find('.card-body').find("#approval-reorder-div").find(".approval-list").empty()

          $(`#addRow_app_level${elementID}`).off('click').on('click', function(){
            levels = $('#approval-reorder-div ul li').find('.newlevel').length;
            if(maximum_levels_allowed != '' && levels == maximum_levels_allowed){
              level_html = `
              <div class="row" id="maximum_level_count_app_level_config" style="color:red;display:block;">
              <div class="form-group col-12">
                <span>
                  Maximum Approver Levels count : ${maximum_levels_allowed}.
                </span>
              </div>
            </div>
              `
              $(level_html).insertAfter(`#addRow_app_level${elementID}`);
              $(`#addRow_app_level${elementID}`).prop('disabled', true)
            }
            else{
              $(`#modalBody${elementID}_applevel`).find('.card-body').find("#approval-reorder-div").find(".approval-list").append(`
              <li class="btn btn-sm btn-light col" style="height:auto;margin: 5px auto;">
                <div class="form-group row newlevel">
                  <div class="col-1"><input class="input form-control" name="level_no" style="width:55px;margin:auto;text-align:center" type="integer"></div>
                  <div class="col-2">
                    <select class="form-control select2 approval_type_applvl" name="approval_type">
                      <option value="" selected disabled>Select One</option>
                      <option value="static">Static Group Based</option>
                      <option value="static_user">Static User Based</option>
                    </select>
                  </div>
                  <div class="col-2"><select class="form-control select2" name="group_list" disabled multiple></select></div>
                  <div class="col-2"><select class="form-control select2" name="user_list" disabled multiple></select></div>
                  <div class="col-3">
                    <select class="form-control select2" name="approver_type">
                      <option value="several">Several Approvers</option>
                      <option value="joint">Joint Approvers</option>
                    </select>
                  </div>
                  <div class="col-1">
                    <a href="javascript:void(0)" class="remove_app_level fa fa-times" data-approved="no"></a>
                  </div>
                  <div class="col-1">
                    <span class="ui-icon ui-icon-arrowthick-2-n-s float-right mt-1"></span>
                  </div>
                </div>
              </li>
            `)
            }

            $(".approval-list").sortable({
              update: function( event, ui ) {
                node_list = document.getElementById('approval-lists').querySelectorAll(`input[name=level_no]`)  
                for (var i = 0; i < node_list.length; ++i) {
                  input = node_list[i];
                  input.value = i
                }
              },
            });

            $(".remove_app_level").off("click").on("click", function(){
              let appr = 0
              let not_appr = 0
              let not_ele = []
              $('#maximum_level_count_app_level_config').css('display', 'none');
              $(`#addRow_app_level${elementID}`).prop('disabled', false);
              $(`#modalBody${elementID}_applevel`).find('.newlevel').find('a').each(function(){
                  if($(this).attr("data-approved") == "no"){
                      not_appr += 1
                      not_ele.push($(this))
                  }else{
                      appr += 1
                  }
              })

              if(not_appr == 1){
                for(let k=0;k<not_ele.length;k++){
                  $(not_ele[k]).css('pointer-events', 'none')
                }
              }else{
                $(this).parent().parent().parent().remove()
              }
            })

            for(let i=0;i<group_list.length;i++){
              $(`#modalBody${elementID}_applevel`).find('.card-body').find('.newlevel').last().find('div').eq(2).find('select').append(`<option value="${group_list[i]}">${group_list[i]}</option>`)
            }

            for(let [key,value] of Object.entries(user_list) ){
              $(`#modalBody${elementID}_applevel`).find('.card-body').find('.newlevel').last().find('div').eq(3).find('select').append(`<option value="${key}">${value}</option>`)
            }

            $(`#modalBody${elementID}_applevel`).find('.card-body').find('.newlevel').last().find('select.select2').each(function(){
              $(this).select2()
            })
            $(`[name=group_list]`).select2({
              maximumSelectionLength: maximum_approvers_allowed
            })
            $(`[name=user_list]`).select2({
              maximumSelectionLength: maximum_approvers_allowed
            })

            $('.approval_type_applvl').off("select2:select").on('select2:select',function(){
                if($(this).val() == "static"){
                  $(this).parent().parent().find('div').eq(2).find("select").prop("disabled",false)
                  $(this).parent().parent().find('div').eq(3).find("select").prop("disabled",true)
                }else if($(this).val() == "static_user"){
                  $(this).parent().parent().find('div').eq(2).find("select").prop("disabled",true)
                  $(this).parent().parent().find('div').eq(3).find("select").prop("disabled",false)
                }
            })

            $(`#modalBody${elementID}_applevel`).find('.newlevel').find('a').each(function(){
              if($(this).attr("data-approved") == "no"){
                  $(this).css('pointer-events', 'all')
              }
            })

          })

          if(jdata){
            let current_level = jdata["current_level"]
            let level_config = jdata["level_config"]
            $(`#edit_app_level_current_level${elementID}`).text(`Current level: ${current_level}`)

            for(let i=0;i<level_config.length;i++){
              $(`#addRow_app_level${elementID}`).trigger('click')

              $(`#modalBody${elementID}_applevel`).find('.card-body').find('.newlevel').last().find('div').eq(0).find("input").val(i).trigger("change")
              $(`#modalBody${elementID}_applevel`).find('.card-body').find('.newlevel').last().find('div').eq(0).find("input").prop("disabled",true)

              $(`#modalBody${elementID}_applevel`).find('.card-body').find('.newlevel').last().find('div').eq(1).find("select").val(level_config[i]["approval_type"]).trigger("change")
              $(`#modalBody${elementID}_applevel`).find('.card-body').find('.newlevel').last().find('div').eq(1).find("select").prop("disabled",true)

              if(level_config[i].hasOwnProperty("group_list")){
                group_present = true
                $(`#modalBody${elementID}_applevel`).find('.card-body').find('.newlevel').last().find('div').eq(2).find("select").prop("disabled",true)
                $(`#modalBody${elementID}_applevel`).find('.card-body').find('.newlevel').last().find('div').eq(3).find("select").prop("disabled",true)

                $(`#modalBody${elementID}_applevel`).find('.card-body').find('.newlevel').last().find('div').eq(2).find("select").val(level_config[i]["group_list"]).trigger("change")
              }

              if(level_config[i].hasOwnProperty("user_list")){
                $(`#modalBody${elementID}_applevel`).find('.card-body').find('.newlevel').last().find('div').eq(2).find("select").prop("disabled",true)
                $(`#modalBody${elementID}_applevel`).find('.card-body').find('.newlevel').last().find('div').eq(3).find("select").prop("disabled",true)

                $(`#modalBody${elementID}_applevel`).find('.card-body').find('.newlevel').last().find('div').eq(3).find("select").val(level_config[i]["user_list"]).trigger("change")
              }

              $(`#modalBody${elementID}_applevel`).find('.card-body').find('.newlevel').last().find('div').eq(4).find("select").val(level_config[i]["approver_type"]).trigger("change")
              $(`#modalBody${elementID}_applevel`).find('.card-body').find('.newlevel').last().find('div').eq(4).find("select").prop("disabled",true)

              $(`#modalBody${elementID}_applevel`).find('.card-body').find('.newlevel').last().find('div').eq(5).find("input").val(i).trigger("change")
              $(`#modalBody${elementID}_applevel`).find('.card-body').find('.newlevel').last().find('div').eq(5).find("input").prop("disabled",true)
              $(`#modalBody${elementID}_applevel`).find('.card-body').find('.newlevel').last().find('div').eq(6).find("a").css('pointer-events', 'none')
              $(`#modalBody${elementID}_applevel`).find('.card-body').find('.newlevel').last().find('div').eq(6).find("a").attr("data-approved","yes")

              if(i>=current_level){

                if(level_config[i].hasOwnProperty("group_list")){
                  $(`#modalBody${elementID}_applevel`).find('.card-body').find('.newlevel').last().find('div').eq(2).find("select").prop("disabled",false)
                }

                if(level_config[i].hasOwnProperty("user_list")){
                  $(`#modalBody${elementID}_applevel`).find('.card-body').find('.newlevel').last().find('div').eq(3).find("select").prop("disabled",false)
                }
                $(`#modalBody${elementID}_applevel`).find('.card-body').find('.newlevel').last().find('div').eq(4).find("select").prop("disabled",false)
                $(`#modalBody${elementID}_applevel`).find('.card-body').find('.newlevel').last().find('div').eq(5).find("input").prop("disabled",false)

                $(`#modalBody${elementID}_applevel`).find('.card-body').find('.newlevel').last().find('div').eq(6).find("a").css('pointer-events', 'all')
                $(`#modalBody${elementID}_applevel`).find('.card-body').find('.newlevel').last().find('div').eq(6).find("a").attr("data-approved","no")
              }
              else{
                element = $(`#modalBody${elementID}_applevel`).find('.card-body').find('.newlevel').last().parent()
                $(`#modalBody${elementID}_applevel`).find('.card-body').find(".disabled_lists").find(".disabled_lists").append(element)
                element.find(".ui-icon.ui-icon-arrowthick-2-n-s").remove()
              }
            }


          }

          $(`#list_view_edit_applevel_modal_${elementID}`).modal('show')

          $(`#save_editapp_level_field_${elementID}`).off('click').on('click', function(){

            $(`#list_view_edit_applevel_modal_${elementID}`).modal('hide')

            $('#' + elementID + '_tab_content').find(`#approvalCommentModal_${elementID}`).find('.modal-title').text('Approval Level Change Comment');
            $('#' + elementID + '_tab_content').find(`#approvalCommentModal_${elementID}`).find('#approval_final_send').text('Save comment');
            $('#' + elementID + '_tab_content').find(`#approvalCommentModal_${elementID}`).css('display', 'block')
            $('#' + elementID + '_tab_content').find(`#approvalCommentModal_${elementID}`).css('opacity', 1)
            $('#' + elementID + '_tab_content').find(`#approvalCommentModal_${elementID}`).css('z-index', 2000)

            $('#' + elementID + '_tab_content').find(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("data-approval_type","app_lvl_change")
            $('#' + elementID + '_tab_content').find(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("onclick",`SaveAppLevelChange.call(this,'${elementID}',${group_present})`)

            $('#' + elementID + '_tab_content').find(`#approvalCommentModal_${elementID}`).find('.close').on('click', function () {
              $('#' + elementID + '_tab_content').find(`#approvalCommentModal_${elementID}`).css('display', 'none')
              $('#' + elementID + '_tab_content').find(`#approvalCommentModal_${elementID}`).css('opacity', 0)
              $('#' + elementID + '_tab_content').find(`#approvalCommentModal_${elementID}`).css('z-index', 1050)
              $('#' + elementID + '_tab_content').find(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("onclick","approve_ind.call(this)")
              $(`#list_view_edit_applevel_modal_${elementID}`).modal('show')
            })

          })

          $(`[name=group_list]`).select2({
            maximumSelectionLength: maximum_approvers_allowed
          })
          $(`[name=user_list]`).select2({
            maximumSelectionLength: maximum_approvers_allowed
          })

        },
        error: function () {
            Swal.fire({icon: 'error',text: "Error while getting the users/group list."});
        }
    });

  }

  function SaveAppLevelChange(elementID,group_present){
    temp_list = []
    relevel = []
    final_save_dict = {}
    curr_level = parseInt($(`#edit_app_level_current_level${elementID}`).text().split(': ')[1])
    let approval_comment = CKEDITOR.instances[`approvalCommentText${elementID}`].getData().replaceAll("&#39;", "&rsquo;").replaceAll("&quot", "&rdquo;");
    $(`#modalBody${elementID}_applevel`).find('.newlevel').each(function(){
        temp_dict = {}
      $(this).find('div').find('select,input').each(function(){
            if($(this).attr('name') == "group_list" || $(this).attr('name') == "user_list"){

              if($(this).attr('name') == "group_list" && group_present){
                if($(this).val().length != 0){
                  temp_dict[$(this).attr('name')] = $(this).val()
                }
              }
              else if(($(this).attr('name') == "user_list") && !(group_present)){
                if($(this).val().length != 0){
                  temp_dict[$(this).attr('name')] = $(this).val()
                }
              }

            }
            else if($(this).attr('name') != undefined){
              if($(this).attr('name') != "relevel" && $(this).attr('name') != "level_no"){
                temp_dict[$(this).attr('name')] = $(this).val()
              }
              if($(this).attr('name') == "relevel"){
                relevel.push(parseInt($(this).val()))
              }
            }
        })
        temp_list.push(temp_dict)
    })

    final_save_dict["level_config"] = temp_list
    final_save_dict["current_level"] = curr_level

    temp_lvl_conf = final_save_dict["level_config"][curr_level]
    new_approver_group = ""
    new_approver_user = ""
    new_approver_type = temp_lvl_conf["approver_type"]
    if("user_list" in temp_lvl_conf){
      new_approver_user = temp_lvl_conf["user_list"]
    }
    if("group_list" in temp_lvl_conf){
      new_approver_group = temp_lvl_conf["group_list"]
    }

    if(new_approver_group){
      $(`#id_approver_group_${elementID}`).val(JSON.stringify(new_approver_group)).trigger("change")
    }

    if(new_approver_user){
      $(`#id_approver_user_${elementID}`).val(JSON.stringify(new_approver_user)).trigger("change")
    }

    if(new_approver_type){
      $(`#id_approver_type_${elementID}`).val(new_approver_type).trigger("change")
    }

    $(`#id_approval_level_config_${elementID}`).val(JSON.stringify(final_save_dict)).trigger("change")
    $(`#list_view_edit_modal_${elementID}`).find('input[name="approval_level_change_comment_edit"]').attr('value',approval_comment)
    $('#' + elementID + '_tab_content').find(`#approvalCommentModal_${elementID}`).css('display', 'none')
    $('#' + elementID + '_tab_content').find(`#approvalCommentModal_${elementID}`).css('opacity', 0)
    $('#' + elementID + '_tab_content').find(`#approvalCommentModal_${elementID}`).css('z-index', 1050)
    $('#' + elementID + '_tab_content').find(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("onclick","approve_ind.call(this)")
  }

  // edit approval

  function editApprovalLevels(id, approval_level_configs){
    $.ajax({
      url: `/users/${urlPath}/dynamicVal/`,
      data: {
        'operation': 'get_user_group_list',
      },
      type: "POST",
      dataType: "json",
      success: function (data) {
        user_list = data.user_list
        group_list = data.group_list
        maximum_levels_allowed = $(`#approvalWallModalBody_${elementID}`).attr("data-maximum_levels_allowed")
        maximum_approvers_allowed = $(`#approvalWallModalBody_${elementID}`).attr("data-maximum_approvers_allowed")
        $(`#approvalWallModalBody_${elementID}`).find(`#view_at_all_levels_${elementID}`).sortable(
          {
            items:"> div:not(.approval_level_divs.no_sort)",
            forcePlaceholderSize: true,
            update: function(event, ui){
              updataDataLevelAttributes();
            }
          }
        )

        function updataDataLevelAttributes(){
          $(`#approvalWallModalBody_${elementID}`).find(`#view_at_all_levels_${elementID}`).attr("approval_level_reordered","true")
          $(`#approvalWallModalBody_${elementID}`).find(`#view_at_all_levels_${elementID}`).find(".approval_level_divs").each(function(index){
            old_data_level = $(this).attr("data-level")
            $(this).attr("old-data-level",old_data_level)
            $(this).attr("data-level",index)
            $(this).find(".remove-level").attr("data-level",index)
            $(this).find(".levelclass").html(`Level ${index}`)
            $(this).find("input.input_change,select.input_change").each(function(){
              old_name = $(this).attr("name")
              new_name = old_name.split("__")[0] + "__" + index
              $(this).attr("name",new_name)
              $(this).attr("id",new_name)

            })
          })
        }

        approval_levels = approval_level_config["level_config"]
        current_level = approval_level_config.current_level

        for (let i in approval_levels){
          if(!(i<current_level)){
            parent_div = $(`#approvalWallModalBody_${elementID}`).find(`#view_at_all_levels_${elementID}`).find(`div[data-level='${i}']`)

            drag_html = `
            <div style="width: fit-content;float: right;color:red;font-size:17px" data-level='${i}' data-toggle="tooltip" onclick="removeApprovaLevel(this,${current_level})" title="Remove Level">
              <span><i class="fa fa-times-circle"></i></span>
            </div>
            <div style="width: fit-content;cursor:move;" data-toggle="tooltip" title="Drag to Reorder Level">
              <span class="ui-icon ui-icon-arrowthick-2-n-s mt-1 mb-1"></span>
            </div>`
            $(parent_div).prepend(drag_html)
            for(let [key,value] of Object.entries(approval_levels[i]) ){
              select_html=""
              if(key == "approver_type"){
                select_html = `
                  <select name="edit_${key}__${i}" id="edit_${key}__${i}" onchange="$(this).siblings('[data-col=${key}]').text($(this).val());" data-edit-col="${key}__${i}" class="select2 input_change">
                    <option data-toggle="tooltip" title="Please note: Several Approvers implies that the approval decision can be undertaken by any single member from the list of approvers" value="several">Several Approvers</option>
                    <option data-toggle="tooltip" title="Please note: Joint Approvers implies that the approval decision will need to be individually undertaken by all members from the list of approvers" value="joint">Joint Approvers</option>
                  </select>
                `

                $(select_html).insertAfter($(parent_div).find(`[data-col=${key}]`))
                $(parent_div).find(`[data-col=${key}]`).css("display","none")
                $(`[name=edit_${key}__${i}]`).select2({width: "100%"})
                $(`[name=edit_${key}__${i}]`).val(value).trigger("change")

              }
              else if(key == "user_list"){
                select_html = `
                  <select multiple name="edit_${key}__${i}" id="edit_${key}__${i}" onchange="$(this).siblings('[data-col=${key}]').text($(this).val());" data-edit-col="${key}__${i}" class="select2 input_change" style="width:100%">
                    `
                  for(let [name,info] of Object.entries(user_list) ){
                    if(value.includes(name)){
                      select_html += `<option selected value="${name}">${info.replace("( )","")}</option>`
                    }
                    else{
                      select_html += `<option value="${name}">${info.replace("( )","")}</option>`
                    }
                  }

                select_html +=  `</select>`
                $(select_html).insertAfter($(parent_div).find(`[data-col=${key}]`))
                $(parent_div).find(`[data-col=${key}]`).css("display","none")
                $(`[name=edit_${key}__${i}]`).select2({
                  width: "100%",
                  maximumSelectionLength: maximum_approvers_allowed
                })

              }
              else if(key == "group_list"){
                select_html = `
                  <select multiple name="edit_${key}__${i}" id="edit_${key}__${i}" onchange="$(this).siblings('[data-col=${key}]').text($(this).val());" data-edit-col="${key}__${i}" class="select2 input_change" style="width:100%">
                    `
                  for(group of group_list){
                    if(value.includes(group)){
                      select_html += `<option selected value="${group}">${group}</option>`
                    }
                    else{
                      select_html += `<option value="${group}">${group}</option>`
                    }
                  }

                select_html +=  `</select>`
                $(select_html).insertAfter($(parent_div).find(`[data-col=${key}]`))
                $(parent_div).find(`[data-col=${key}]`).css("display","none")
                $(`[name=edit_${key}__${i}]`).select2({
                  width: "100%",
                  maximumSelectionLength: maximum_approvers_allowed
                })

              }
              else if(key =="approval_type"){
                input_html = `<input type="text" class="form-control textInput input_change" name="edit_${key}__${i}" value="${value}" id="edit_${key}__${i}" data-edit-col="${key}__${i}" disabled>`
                $(input_html).insertAfter($(parent_div).find(`[data-col=${key}]`))
                $(parent_div).find(`[data-col=${key}]`).css("display","none")
              }

            }
          }
        }

        $(`#approvalWallModalBody_${elementID}`).find(`.levelclass`).css("margin-top","25%")
        $(`#approvalWallModalBody_${elementID}`).find(`#edit_approval_levels_${elementID}`).css("display","none")
        $(`#approvalWallModalBody_${elementID}`).find(`#save_approval_levels_${elementID}`).css("display","block")
        $(`#approvalWallModalBody_${elementID}`).find(`#add_levels_div_${elementID}`).css("display","block")
        approval_level_configs = JSON.stringify(approval_level_configs)
        $(`#approvalWallModalBody_${elementID}`).find(`#add_approval_levels_${elementID}`).attr("onclick",`addApprovalLevel(this,'${id}',${approval_level_configs}, '${maximum_levels_allowed}', '${maximum_approvers_allowed}')`)


      },
      error: function () {
          Swal.fire({icon: 'error',text: "Error while getting the users/group list."});
      }
    });

  }

  function removeApprovaLevel(element,current_level){
    $("#maximum_level_count_aw").css('display', 'none')
    $(`#add_approval_levels_${elementID}`).prop('disabled', false);
    if($(element).attr("removed-old-data-level")){
      removed_old_data_level = $(element).attr("removed-old-data-level")
      removed_data_level = $(element).attr("data-level")
    }
    else{
      removed_data_level = $(element).attr("data-level")
    }

    levels_length = $(`#approvalWallModalBody_${elementID}`).find(`#view_at_all_levels_${elementID}`).find(".approval_level_divs").length;
    levels_length = levels_length - parseInt(current_level)

    if(levels_length > 1){

      if($(element).attr("data-added-level") == "true"){
        $(`#approvalWallModalBody_${elementID}`).find(`#view_at_all_levels_${elementID}`).find(`div[data-level='${removed_data_level}']`).remove()

        $(`#approvalWallModalBody_${elementID}`).find(`#view_at_all_levels_${elementID}`).find(".approval_level_divs").each(function(index){
          removed_old_data_level = $(this).attr("data-level")
          $(this).attr("removed-old-data-level",removed_old_data_level)
          $(this).attr("data-level",index)
          $(this).find(".remove-level").attr("data-level",index)
          $(this).find(".levelclass").html(`Level ${index}`)
          $(this).find(`[data-level=${removed_old_data_level}]`).attr("data-level",index)
          $(this).find("input.input_change,select.input_change").each(function(){
            old_name = $(this).attr("name")
            new_name = old_name.split("__")[0] + "__" + index
            $(this).attr("name",new_name)
            $(this).attr("id",new_name)

          })
        })
      }
      else{

        $(`#approvalWallModalBody_${elementID}`).find(`#view_at_all_levels_${elementID}`).find(`div[data-level='${removed_data_level}']`).remove()

        let levels_removed = ""
        removed_levels_list = $(`#approvalWallModalBody_${elementID}`).find(`#view_at_all_levels_${elementID}`).attr("approval_level_removed")
        if(removed_levels_list == undefined || removed_levels_list == "" || removed_levels_list == '[]'){
          levels_removed = [removed_data_level]
        }
        else{
          removed_levels_list = JSON.parse(removed_levels_list)
          removed_levels_list.push(removed_old_data_level)
          levels_removed = removed_levels_list
        }

        if(levels_removed){
          $(`#approvalWallModalBody_${elementID}`).find(`#view_at_all_levels_${elementID}`).attr("approval_level_removed", JSON.stringify(levels_removed))
        }

        $(`#approvalWallModalBody_${elementID}`).find(`#view_at_all_levels_${elementID}`).find(".approval_level_divs").each(function(index){
          removed_old_data_level = $(this).attr("data-level")
          $(this).attr("removed-old-data-level",removed_old_data_level)
          $(this).attr("data-level",index)
          $(this).find(".remove-level").attr("data-level",index)
          $(this).find(".levelclass").html(`Level ${index}`)
          $(this).find(`[data-level=${removed_old_data_level}]`).attr("data-level",index)
          $(this).find("input.input_change,select.input_change").each(function(){
            old_name = $(this).attr("name")
            new_name = old_name.split("__")[0] + "__" + index
            $(this).attr("name",new_name)
            $(this).attr("id",new_name)

          })
        })

      }

    }
  }

  function addApprovalLevel(element, id, approval_level_configs, maximum_levels_allowed, maximum_approvers_allowed){
    current_level = approval_level_configs.current_level
    total_level = $(`#approvalWallModalBody_${elementID}`).find(`#view_at_all_levels_${elementID}`).find(".approval_level_divs:last-child").attr("data-level")

    levels = $(`#approvalWallModalBody_${elementID}`).find(`#view_at_all_levels_${elementID}`).find(".approval_level_divs").length
    if((maximum_levels_allowed != '' && levels == maximum_levels_allowed)){
      add_level_html = `
      <div class="row" id="maximum_level_count_aw" style="color:red;display:block;">
      <div class="form-group col-12">
        <span>
          Maximum Approver Levels count : ${maximum_levels_allowed}.
        </span>
      </div>
    </div>`
    $(add_level_html).insertAfter(`#header_div_${elementID}`);
    $(`#add_approval_levels_${elementID}`).prop('disabled', true);
    }
    else{
      add_level_html = `
      <div data-level="${parseInt(total_level)+1}" class="approval_level_divs">
        <div style="width: fit-content;float: right;color:red;font-size:17px;cursor:pointer;" class="remove-level" class="remove-level" data-added-level="true" data-level='${parseInt(total_level)+1}' data-toggle="tooltip" onclick="removeApprovaLevel(this,${current_level})" title="Remove Level">
          <span><i class="fa fa-times-circle"></i></span>
        </div>
        <div style="width: fit-content;cursor:move;" data-toggle="tooltip" title="Drag to Reorder Level">
          <span class="ui-icon ui-icon-arrowthick-2-n-s mt-1 mb-1"></span>
        </div>

        <div class="row">
          <div class="col-3">
            <div class="levelclass" style="background: darkgrey;color:white;">Level ${parseInt(total_level)+1}</div>
          </div>
          <div class="col-9" style="border-left: 1px solid lightgrey;">
            <div style="border-radius: 0.5rem;margin-left: 6px;padding: 4px;text-align: left;">
              <div>
                <select class="form-control select2 input_change approver_type__${parseInt(total_level)+1}" data-col="approver_type" style="width:100%" name="edit_approver_type__${parseInt(total_level)+1}" id="edit_approver_type__${parseInt(total_level)+1}" data-edit-col="approver_type__${parseInt(total_level)+1}">
                  <option value="several">Several Approvers</option>
                  <option value="joint">Joint Approvers</option>
                </select>
              </div>
            </div>
            <div style="border-radius: 0.5rem;padding: 10px;text-align: left;">
              <h6 style="margin-bottom: 0.5rem;font-size:13px;text-transform: capitalize;text-align: left;">Approval Type</h6>
              <select class="form-control select2 input_change approval_type__${parseInt(total_level)+1}" data-col="approval_type" style="width:100%" name="edit_approval_type__${parseInt(total_level)+1}" id="edit_approval_type__${parseInt(total_level)+1}" data-edit-col="approval_type__${parseInt(total_level)+1}">
                <option value="" selected>Select One</option>
                <option value="static">Static Group Based</option>
                <option value="static_user">Static User Based</option>
              </select>
            </div>
            <div style="border-radius: 0.5rem;padding: 10px;text-align: left;" class="div_user_list__${parseInt(total_level)+1}">
              <h6 style="margin-bottom: 0.5rem;font-size:13px;text-transform: capitalize;text-align: left;">Approvers</h6>
              <select class="form-control select2 input_change user_list__${parseInt(total_level)+1}" data-col="user_list" style="width:100%" name="edit_user_list__${parseInt(total_level)+1}" id="edit_user_list__${parseInt(total_level)+1}" data-edit-col="user_list__${parseInt(total_level)+1}"disabled multiple>
                `
                for(let [name,info] of Object.entries(user_list) ){
                  add_level_html += `<option value="${name}">${info}</option>`
                }
                add_level_html += `
              </select>
            </div>
            <div style="border-radius: 0.5rem;padding: 10px;text-align: left;" class="div_group_list__${parseInt(total_level)+1}">
              <h6 style="margin-bottom: 0.5rem;font-size:13px;text-transform: capitalize;text-align: left;">Group Approvers</h6>
              <select class="form-control select2 input_change group_list__${parseInt(total_level)+1}" data-col="group_list" style="width:100%" name="edit_group_list__${parseInt(total_level)+1}" id="edit_group_list__${parseInt(total_level)+1}" data-edit-col="group_list__${parseInt(total_level)+1}" disabled multiple>
                `
                for(group of group_list){
                  add_level_html += `<option value="${group}">${group}</option>`
                }
                add_level_html += `
              </select>
            </div>
          </div>
        </div>
      </div>
      `
      $(`#approvalWallModalBody_${elementID}`).find(`#view_at_all_levels_${elementID}`).append(add_level_html)
    }

    $(`#approvalWallModalBody_${elementID}`).find(`#view_at_all_levels_${elementID}`).attr("data-level-added", "true")
    $(`[data-level="${parseInt(total_level)+1}"]`).find(".select2").select2()
    $(`#edit_group_list__${parseInt(total_level)+1}`).select2({
      maximumSelectionLength: maximum_approvers_allowed
    })
    $(`#edit_user_list__${parseInt(total_level)+1}`).select2({
      maximumSelectionLength: maximum_approvers_allowed
    })


    $(`.approval_type__${parseInt(total_level)+1}`).change(function(){
      if(this.value == "static" ){
        $(this).closest(".approval_level_divs").find(`.div_group_list__${parseInt(total_level)+1}`).css("display","block")
        $(this).closest(".approval_level_divs").find(`.group_list__${parseInt(total_level)+1}`).prop("disabled", false)
        $(this).closest(".approval_level_divs").find(`.user_list__${parseInt(total_level)+1}`).prop("disabled", true)
        $(this).closest(".approval_level_divs").find(`.user_list__${parseInt(total_level)+1}`).val("").trigger("change")
        $(this).closest(".approval_level_divs").find(`.div_user_list__${parseInt(total_level)+1}`).css("display","none")
      }
      else if(this.value == "static_user" ){
        $(this).closest(".approval_level_divs").find(`.div_user_list__${parseInt(total_level)+1}`).css("display","block")
        $(this).closest(".approval_level_divs").find(`.user_list__${parseInt(total_level)+1}`).prop("disabled", false)
        $(this).closest(".approval_level_divs").find(`.group_list__${parseInt(total_level)+1}`).prop("disabled", true)
        $(this).closest(".approval_level_divs").find(`.group_list__${parseInt(total_level)+1}`).val("").trigger("change")
        $(this).closest(".approval_level_divs").find(`.div_group_list__${parseInt(total_level)+1}`).css("display","none")

      }
    })
  }

  function saveLevelChangeComment(id, approval_level_configs){

    $('#' + elementID + '_tab_content').find(`#approvalCommentModal_${elementID}`).find('.modal-title').text('Approval Level Change Comment');
    $('#' + elementID + '_tab_content').find(`#approvalCommentModal_${elementID}`).find('.modal-title').css('color','black');
    $('#' + elementID + '_tab_content').find(`#approvalCommentModal_${elementID}`).find('.approvers_edit_data').css('margin-bottom','unset');
    $('#' + elementID + '_tab_content').find(`#approvalCommentModal_${elementID}`).find('#approval_final_send').text('Save comment');
    $('#' + elementID + '_tab_content').find(`#approvalCommentModal_${elementID}`).modal("show")
    $('#' + elementID + '_tab_content').find(`#approvalCommentModal_${elementID}`).css('z-index', 2000)

    $('#' + elementID + '_tab_content').find(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("data-approval_type","app_lvl_change")

    approval_level_configs = JSON.stringify(approval_level_configs)
    $('#' + elementID + '_tab_content').find(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("onclick",`saveApprovalLevels.call(this,'${id}',${approval_level_configs})`)

  }

  function saveApprovalLevels(id,approval_level_configs){
    var old_approval_level_configs = JSON.parse(JSON.stringify(approval_level_configs.level_config))
    var listOfChangedLevel = []

    temp_list = []
    final_save_dict = {}
    curr_level = approval_level_configs["current_level"]
    let approval_comment = CKEDITOR.instances[`approvalCommentText${elementID}`].getData().replaceAll("&#39;", "&rsquo;").replaceAll("&quot", "&rdquo;");

    var approval_level_reordered = $(`#approvalWallModalBody_${elementID}`).find(`#view_at_all_levels_${elementID}`).attr("approval_level_reordered")
    if(approval_level_reordered == undefined || approval_level_reordered == "" ){
      approval_level_reordered = false
    }
    else if(approval_level_reordered == "true"){
      approval_level_reordered = true
    }

    var level_added = $(`#approvalWallModalBody_${elementID}`).find(`#view_at_all_levels_${elementID}`).attr("data-level-added")
    if(level_added == undefined || level_added == "" ){
      level_added = false
    }
    else if(level_added == "true"){
      level_added = true
    }

    var all_removed_levels = $(`#approvalWallModalBody_${elementID}`).find(`#view_at_all_levels_${elementID}`).attr("approval_level_removed")
    if(all_removed_levels == undefined || all_removed_levels == "" || all_removed_levels == '[]'){
      all_removed_levels = []
    }
    else {
      all_removed_levels = JSON.parse(all_removed_levels)
    }

    for (let level in all_removed_levels){
      approval_level_configs["level_config"].splice(parseInt(level), 1)
    }

    $(`#approvalWallModalBody_${elementID}`).find('.approval_level_divs').each(function(){
      level = $(this).attr("data-level")
      old_data_level = $(this).attr("old-data-level")

      parent_div = $(this)

      if(level>=curr_level){
        temp_dict = {}
        $(this).find("[data-col]").each(function(){
          key = $(this).attr("data-col")
          if($(parent_div).find(`[name=edit_${key}__${level}]`).val() != "" && $(parent_div).find(`[name=edit_${key}__${level}]`).val() != "[]"){
            temp_dict[key] = $(parent_div).find(`[name=edit_${key}__${level}]`).val()
          }

        })
        approval_level_configs["level_config"][level] = temp_dict
      }
    })

    // comparing old vs new

    for(index=0;index < old_approval_level_configs.length;index++){
      data = old_approval_level_configs[index]

      if(all_removed_levels.includes(index)){
        var changedStatus = {
          index :index,
          userChanged: null,
          groupChanged: null,
          approverTypeChanged: null,
          approvalChanged: null,
          isDeleted:true
        }
        listOfChangedLevel[index] = changedStatus
        continue;
      }
      else{
        var changedStatus = {
          index :index,
          userChanged: null,
          groupChanged: null,
          approverTypeChanged: null,
          approvalChanged: null,
          isDeleted:false
        }
      }

      if(all_removed_levels.length==0){
        if(data.approver_type != approval_level_configs.level_config[index].approver_type){
          changedStatus.approverTypeChanged = data.approver_type
        }
        if(data.approval_type != approval_level_configs.level_config[index].approval_type){
          changedStatus.approvalChanged = data.approval_type
        }
        if(JSON.stringify(data.user_list) != JSON.stringify(approval_level_configs.level_config[index].user_list)){
          changedStatus.userChanged = data.user_list
        }
        if(JSON.stringify(data.group_list) != JSON.stringify(approval_level_configs.level_config[index].group_list)){
          changedStatus.groupChanged = data.group_list
        }
      }

      if(changedStatus.userChanged || changedStatus.groupChanged || changedStatus.approverTypeChanged || changedStatus.approvalChanged){
        listOfChangedLevel[index] = changedStatus
      }
      else{
        listOfChangedLevel[index] = null
      }

    }


    $.ajax({
      url: `/users/${urlPath}/dynamicVal/`,
      data: {
        'operation': 'editApprovalLevelsAprrovalWall',
        'listOfChangedLevel' :JSON.stringify(listOfChangedLevel),
        'new_approval_level_configs' : JSON.stringify({"level_config" : approval_level_configs.level_config,"current_level":curr_level}),
        'old_approval_level_configs' : JSON.stringify({"level_config" : old_approval_level_configs,"current_level":curr_level}),
        'id' : id,
        'edit_comment': approval_comment,
        'current_level': curr_level,
        'approval_level_reordered' : JSON.stringify(approval_level_reordered),
        'level_added' : JSON.stringify(level_added),
        'all_removed_levels' : JSON.stringify(all_removed_levels)

      },
      type: "POST",
      dataType: "json",
      success: function (data) {
        $('#' + elementID + '_tab_content').find(`#approvalCommentModal_${elementID}`).modal("hide")
        Swal.fire({icon: 'success',text: "Approval Level configurations updated successfully!"}).then((result) => {
          if (result.isConfirmed) {
            location.reload()
          }
        })
      },
      error: function () {
        Swal.fire({icon: 'error',text: "Error! Please try again."});
      }
    });

  }

  function editApprovers(id,approver_group,type_of_approval){

    $(`#approvalWallModalBody_${elementID}`).find(`#edit_approvers_${elementID}`).css("display","none")
    $(`#approvalWallModalBody_${elementID}`).find(`#save_approvers_${elementID}`).css("display","block")

    $.ajax({
      url: `/users/${urlPath}/dynamicVal/`,
      data: {
        'operation': 'get_user_group_list',
      },
      type: "POST",
      dataType: "json",
      success: function (data) {
        user_list = data.user_list
        group_list = data.group_list
        maximum_levels_allowed = $(`#approvalWallModalBody_${elementID}`).attr("data-maximum_levels_allowed")
        maximum_approvers_allowed = $(`#approvalWallModalBody_${elementID}`).attr("data-maximum_approvers_allowed")

        if(type_of_approval == "static_user" || type_of_approval == "dynamic_user"){
          selected_approvers = []
          $(`#approvalWallModalBody_${elementID}`).find(`#approver_users_${element_id}`).find("ul").find("li.li_approvers").each(function(){
            username = $(this).find(".approvers_username").text()
            selected_approvers.push(username)
            $(this).css("display","none")
          })

          select_html = `
            <select class="edit_approvers_select select2 form-control" multiple style="width:100%">
          `
          for(let [name,info] of Object.entries(user_list) ){
            if(selected_approvers.includes(name)){
              select_html += `<option selected value="${name}">${info.replace("( )","")}</option>`
            }
            else{
              select_html += `<option value="${name}">${info.replace("( )","")}</option>`
            }
          }
          select_html +=  `</select>`

          $(`#approver_users_${elementID}`).append(select_html)
          $(`#approver_users_${elementID}`).find(".edit_approvers_select").select2({
            maximumSelectionLength: maximum_approvers_allowed
          })
        }
        else if(type_of_approval == "static" || type_of_approval == "dynamic_group"){

          $(`#approvalWallModalBody_${elementID}`).find(`#approver_users_${element_id}`).find("ul").find("li.li_approvers").each(function(){
            $(this).css("display","none")
          })

          select_html = `
            <select class="edit_approvers_select select2 form-control" multiple style="width:100%">
          `
          for(group of group_list){
            if(approver_group.includes(group)){
              select_html += `<option selected value="${group}">${group}</option>`
            }
            else{
              select_html += `<option value="${group}">${group}</option>`
            }
          }
          select_html +=  `</select>`

          $(`#approver_users_${elementID}`).append(select_html)
          $(`#approver_users_${elementID}`).find(".edit_approvers_select").select2({
            maximumSelectionLength: maximum_approvers_allowed
          })
        }



      },
      error: function () {
          Swal.fire({icon: 'error',text: "Error while getting the users/group list."});
      }
    });
  }

  function saveApprovers(id, approver_group, approver_user_data_list, approval_audit_log, type_of_approval, approver_type){

    var new_approvers = $(`#approver_users_${elementID}`).find(".edit_approvers_select").val()

    if(type_of_approval == "static_user" || type_of_approval == "dynamic_user"){
      old_approvers = []
      for(var i = 0; i < approver_user_data_list.length; i++){
        old_approvers.push(approver_user_data_list[i].username)
      }
    }
    else if(type_of_approval == "static" || type_of_approval == "dynamic_group"){
      old_approvers = approver_group
    }

    $.ajax({
      url: `/users/${urlPath}/dynamicVal/`,
      data: {
        'operation': 'saveStaticApprovers',
        'new_approvers' : JSON.stringify(new_approvers),
        'old_approvers' : JSON.stringify(old_approvers),
        'old_approval_audit_log' : JSON.stringify(approval_audit_log),
        'id' : id,
        'type_of_approval':type_of_approval,
        'approver_type': approver_type
      },
      type: "POST",
      dataType: "json",
      success: function (data) {
        Swal.fire({icon: 'success',text: "Approvers configurations updated successfully!"}).then((result) => {
          if (result.isConfirmed) {
            location.reload()
          }
        })
      },
      error: function () {
        Swal.fire({icon: 'error',text: "Error! Please try again."});
      }
    });



  }


  function listview_auto_compute(listview_elementID){

    const autoComputeBtn = $(`#autoCompute_${listview_elementID}`)
  if  (autoComputeBtn.length > 0){
    const elementId = $(autoComputeBtn).attr('data-elementID')
    const computedValueList = []
    let main_config_dict = {}
    let source_dict = {}
    const valuesDic = {}
    const datatypeList = []
    $('#list_view_edit_modal_' + elementId)
    .find('div')
    .find('form')
    .find('.form-row')
    .find('[data-computed-field="true"]')
    .each(function () {
      computedValueList.push(
        $(this)
          .attr('id')
          .replace('id_', '')
          .replace('_' + elementId, '')
      )

      main_config_dict[$(this).attr('id').replace('id_', '').replace('_' + elementId, '')] = JSON.parse($(this).attr("data-comp_input"))
    })

    const tableName = $(autoComputeBtn)
    .attr('data-table-name')
    .replace('["', '')
    .replace('"]', '')
    var ctoken = $('form').find(`input[name='csrfmiddlewaretoken']`).attr('value');
    $.ajaxSetup({

    beforeSend: function (xhr, settings) {
                      xhr.setRequestHeader('X-CSRFToken', ctoken);
                  }

              });

    for(let[col,config] of Object.entries(main_config_dict)){
      for(let kk=0;kk<config.length;kk++){
        if(config[kk] in source_dict){
          source_dict[config[kk]].push(col)
        }else{
          source_dict[config[kk]] = [col]
        }
      }
    }


    for (let [key,value] of Object.entries(source_dict)){

      $(`#id_${key}_${listview_elementID}`).on("change dp.change", function(){

          for(let i in value){
              let cols_list = main_config_dict[value[i]]
              let allok = 'no'

              for(let ii=0;ii<cols_list.length;ii++){

                  if($(`#id_${cols_list[ii]}_${elementId}`).val() == '' || $(`#id_${cols_list[ii]}_${elementId}`).val() == null || $(`#id_${cols_list[ii]}_${elementId}`).val() == "---" || $(`#id_${cols_list[ii]}_${elementId}`).val() == "----"){
                      allok = 'no'
                      break

                  }else{
                      allok = "yes"
                  }
              }

              if(allok=="yes"){

                $('#list_view_edit_modal_' + elementId)
                .find('div')
                .find('form')
                .find('.form-row')
                .find('input[data-field_name],select[data-field_name]')
                .each(function () {
                  let compVal = $(this).val()
                  if (String(compVal) === '') {
                    compVal = 'NaN'
                  }
                  const compCol = $(this)
                    .attr('id')
                    .replace('id_', '')
                    .replace('_' + elementId, '')

                  const compDatatype = $(this).attr('datatype')

                  valuesDic[compCol] = compVal
                  datatypeList.push(compDatatype)
                })

                $.ajax({
                  url: `/users/${urlPath}/dynamicVal/`,
                  data: {
                    element_id: elementId,
                    operation: 'calculate_computed_value_auto',
                    values_dic: JSON.stringify(valuesDic),
                    datatype_list: JSON.stringify(datatypeList),
                    table_name: JSON.stringify(tableName),
                    field_name: value[i],
                  },
                  type: 'POST',
                  dataType: 'json',
                  success: function (context) {
                    if (String(context.error_msg) === 'yes') {
                      for (let i = 0; i < context.f_list.length; i++) {
                        Swal.fire({icon: 'error',text: `Error while calculating : ${context.f_list[i]} - ${context.e_list[i]}`});
                      }
                    } else {
                      for (const [key, value] of Object.entries(context.data[0])) {
                        for (let i = 0; i < computedValueList.length; i++) {
                          if (String(key) === computedValueList[i]) {
                            $('#id_' + computedValueList[i] + '_' + elementId)
                              .val(value)
                              .trigger('change')
                          }
                        }
                      }
                    }
                  },
                  error: function () {
                    Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                  },
                })
              }

          }
      })
  }

  }

  }