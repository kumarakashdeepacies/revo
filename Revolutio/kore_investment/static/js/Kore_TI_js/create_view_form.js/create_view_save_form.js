/* eslint-disable no-mixed-spaces-and-tabs */
/* eslint-disable no-tabs */
/* eslint-disable comma-dangle */
// eslint-disable-next-line no-redeclare,camelcase
/* global createViewIdList:true,item_code_list:true,FormData:true */
var NaN = '' // eslint-disable-line no-unused-vars,no-shadow-restricted-names,no-var

for (let i = 0; i < createViewIdList.length; i++) {
  const submitButtonCreateForm = $(`#${createViewIdList[i]}_tab_content`).find(
    'form button[name="submit"]'
  )
  submitButtonCreateForm.on('click', function () {
    let idEle = $(this).attr('id').split('whiteSpacewrap')[1]
    idEle = 'whiteSpacewrap' + idEle
    const connectedListviewId = $(this).attr('connected_listview_id')
    if (connectedListviewId) {
      const linkedListview = $(this).attr('connected_listview_id')
      localStorage.setItem('activeTabs', linkedListview)
    } else {
      localStorage.setItem('activeTabs', createViewIdList[i])
    }
    const type = $(this).val()
    let currentUrl = window.location.pathname

    // eslint-disable-next-line camelcase
    if (item_code_list) {
      // eslint-disable-next-line camelcase
      for (let j = 0; j < item_code_list.length; j++) {
        // eslint-disable-next-line camelcase
        currentUrl = '/users/' + item_code_list[j][idEle] + '/'
      }
    }
    let pr_code = $(this).parent().parent().find('input[name="pr_code"]').attr("value")
    if(window.location.pathname.includes('homePage')){

      let windowLocation1 = window.location.pathname
      let f_occ1 = windowLocation1.indexOf('/', windowLocation1.indexOf('/') + 1)
      let s_occ1 = windowLocation1.indexOf('/', windowLocation1.indexOf('/') + f_occ1 +1)
      let t_occ1 = windowLocation1.indexOf('/', windowLocation1.indexOf('/') + s_occ1 +1)
      let app_code2_ = windowLocation1.substring(f_occ1+1,s_occ1)
      let current_dev_mode2_ = windowLocation1.substring(s_occ1+1,t_occ1)
      if(current_dev_mode2_ != "Build" && current_dev_mode2_ != "Edit"){
          current_dev_mode2_ = "User"
      }
      currentUrl = `/users/${app_code2_}/${current_dev_mode2_}/${pr_code}/`
    }
    const submitFormUrl = currentUrl + 'create/'
    const submitFormDraftUrl = currentUrl + 'createDraft/'
    if (String(type) === 'Save') {
      $(this).attr('formaction', submitFormUrl)
      const approvalAssignmentConfig = $(`#${createViewIdList[i]}_tab_content`)
      .find('form input[name="approvalAssignmentConfig"]');
      if (approvalAssignmentConfig.length > 0) {
        const approvalAssignmentConfigValue = approvalAssignmentConfig.val();
        const approvalAssignmentConfigJSON = JSON.parse(approvalAssignmentConfigValue);
        if (Object.keys(approvalAssignmentConfigJSON).length === 0 && approvalAssignmentConfigJSON.constructor === Object) {
          Swal.fire({icon: 'warning', text: 'Approver details have not been added.'});
          return false;
        }
      }

      let jsvalidation_createview_config = $(this).attr("data-jsvalidation_createview_config")
      if(jsvalidation_createview_config.length != 0){
        jsvalidation_createview_config = JSON.parse(jsvalidation_createview_config)
        val = jsValidationScenario(jsvalidation_createview_config, $(this), createViewIdList[i], pr_code)
        if(!val){
          Swal.fire({icon: 'warning', text: jsvalidation_createview_config["val_message"]});
          return val
        }
        else{
          var isValid = true;
          $(`#createview${idEle} [required]`).each(function() {
              if ($(this).val().trim() === "") {
                  isValid = false;
                  return false;
              }
          });  
          if (isValid) {
            $(`#creation_in_progress_${idEle}`).modal('show');
            $(this).closest('body').css('pointer-events', 'none')
          }
        }
      }else{
        jsvalidation_createview_config = []
      }
      setTimeout('', 50000);
    } else if (String(type) === 'Save as Draft') {
      $(this).attr('formaction', submitFormDraftUrl)
    }

    $(this).attr('type', 'submit')

  })
}

function fetchDataFromMaster(data, itemCode, callback) {
  $.ajax({
    url: `/users/${urlPath}/${itemCode}/`,
    async: false,
    data: data,
    type: "POST",
    dataType: "json",
    success: function (data) {
      callback(data.data);
    },
    error: function () {
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    }
  })
}

function jsValidationScenario(config, This, elementId, pr_code){

  let condition_list = []
  let constraint_dict = {}
  let current_ans = -1
  let previous_ans = -1
  let previous_ruleset = -1
  if(config.length != 0){
    config = config["config"]
  }else{
    config = []
  }
  const itemCode = pr_code
  let dtype_dict = JSON.parse($(This).attr("data-dtype"))
  for(let i =0;i<config.length;i++){

    if(config[i]["constraint_name"] in constraint_dict){
      constraint_dict[config[i]["constraint_name"]].push(config[i])
    }else{
      constraint_dict[config[i]["constraint_name"]] = [config[i]]
    }

  }

  constraint_dict_copy = constraint_dict

  for(let [constraint,configs] of Object.entries(constraint_dict_copy)){

    ruleset_dict = {}
    for(let i=0;i<configs.length;i++){
      if(configs[i]["rule_set"] in ruleset_dict){
        ruleset_dict[configs[i]["rule_set"]].push(configs[i])
      }else{
        ruleset_dict[configs[i]["rule_set"]] = [configs[i]]
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

        let datatype = dtype_dict[configs[i]["column_name"]]
        if(configs[i]["jstype"] == "static" || configs[i]["jstype"] == "master_based" || configs[i]["jstype"] == "master_field" || configs[i]["jstype"] == "field_based"){

          if(configs[i]["jstype"] == "master_based"){

            data = {
              'operation': 'get_master_based_value',
              'config':JSON.stringify(configs[i]),
            }
            fetchDataFromMaster(data, itemCode, function (result) {
              value_to_compare = result;
            });
          }else if(configs[i]["jstype"] == "master_field"){
            input_dic = {}
            value_to_compare = ""

            inner_config = configs[i]["filter_config"]["config"]
            for(let i=0;i<inner_config.length;i++){
              input_dic[inner_config[i]["input_value"]] = $(`#id_${inner_config[i]["input_value"]}_${elementId}`).val()
            }
            data = {
              'operation': 'get_master_field_value',
              'input_value_dic': JSON.stringify(input_dic),
              'config':JSON.stringify(configs[i]["filter_config"]),
              'table': configs[i]["table_name"],
              'columnname': configs[i]["columnname"],
            };
            fetchDataFromMaster(data, itemCode, function (result) {
              value_to_compare = result;
            });

          }else if(configs[i]["jstype"] == "field_based"){
            value_to_compare = $(`#id_${configs[i]["input_value"]}_${elementId}`).val()
          }else{
            value_to_compare = configs[i]["input_value"]
          }

          if(datatype == "IntegerField" || datatype == "BigIntegerField"){
            if(value_to_compare.constructor === Array){
              value_to_compare = value_to_compare.map(function (x) { return parseInt(x); });
            }else{
              value_to_compare = parseInt(value_to_compare);
            }
          }else if(datatype == "FloatField"){
            if(value_to_compare.constructor === Array){
              value_to_compare = value_to_compare.map(function (x) { return parseFloat(x); });
            }else{
              value_to_compare = parseFloat(value_to_compare)
            }
          }
        }else if(configs[i]["jstype"] == "dynamic"){
          value_to_compare = configs[i]["input_value"]

          if(value_to_compare == "curr_date"){

            var today = new Date();
            var dd = String(today.getDate()).padStart(2, '0');
            var mm = String(today.getMonth() + 1).padStart(2, '0');
            var yyyy = today.getFullYear();

            value_to_compare =  yyyy + '-' + mm + '-' + dd;
          }

          if(value_to_compare == "curr_user"){
            let curr_user = $(This).attr("data-curr_user")
            value_to_compare = curr_user
          }
        }

        column_value = $(`#id_${configs[i]["column_name"]}_${elementId}`).val()
        if(datatype == "IntegerField" || datatype == "BigIntegerField"){
          if(column_value.constructor === Array){
            column_value = column_value.map(function (x) { return parseInt(x); });
          }else{
            column_value = parseInt(column_value);
          }
        }else if(datatype == "FloatField"){
          if(column_value.constructor === Array){
            column_value = column_value.map(function (x) { return parseFloat(x); });
          }else{
            column_value = parseFloat(column_value)
          }
        } else if (datatype == "MultiselectField") {
          column_value = [];
          $(`#${elementId}_${configs[i]["column_name"]}_unique option:selected`).each(function(){
            column_value.push($(this).text());
          });
        }

        condition = configs[i]["condition"]
        rule_set = configs[i]["rule_set"]

        if(condition == "IN"){
          if (value_to_compare.constructor !== Array) {
            value_to_compare = [value_to_compare];
          }
          if(column_value.constructor === Array){
            current_ans = column_value.some(v => value_to_compare.includes(v));
          } else {
            if(value_to_compare.includes(column_value)){
              current_ans = true
            }else{
              current_ans = false
            }
          }

        }else if(condition == "NOT IN"){
          if (value_to_compare.constructor !== Array) {
            value_to_compare = [value_to_compare];
          }
          if(column_value.constructor === Array){
            current_ans = !column_value.some(v => value_to_compare.includes(v));
          } else {
            if(!(value_to_compare.includes(column_value))){
              current_ans = true
            }else{
              current_ans = false
            }
          }
        }else if(condition == "Equal to"){
          if (value_to_compare.constructor === Array) {
            value_to_compare = value_to_compare[0];
          }
          if(column_value.constructor === Array){
            current_ans = column_value.includes(value_to_compare);
          } else {
            if(value_to_compare == column_value){
              current_ans = true
            }else{
              current_ans = false
            }
          }
        }else if(condition == "Not Equal to"){
          if (value_to_compare.constructor === Array) {
            value_to_compare = value_to_compare[0];
          }
          if(column_value.constructor === Array){
            current_ans = !column_value.includes(value_to_compare);
          } else {
            if(value_to_compare != column_value){
              current_ans = true
            }else{
              current_ans = false
            }
          }
        }else if(condition == "Starts with"){
          if (value_to_compare.constructor === Array) {
            value_to_compare = value_to_compare[0];
          }
          if(column_value.startsWith(value_to_compare)){
            current_ans = true
          }else{
            current_ans = false
          }
        }else if(condition == "Not Starts with"){
          if (value_to_compare.constructor === Array) {
            value_to_compare = value_to_compare[0];
          }
          if(!(column_value.startsWith(value_to_compare))){
            current_ans = true
          }else{
            current_ans = false
          }
        }else if(condition == "Ends with"){
          if (value_to_compare.constructor === Array) {
            value_to_compare = value_to_compare[0];
          }
          if(column_value.endsWith(value_to_compare)){
            current_ans = true
          }else{
            current_ans = false
          }
        }else if(condition == "Not Ends with"){
          if (value_to_compare.constructor === Array) {
            value_to_compare = value_to_compare[0];
          }
          if(!(column_value.endsWith(value_to_compare))){
            current_ans = true
          }else{
            current_ans = false
          }
        }else if(condition == "Contains"){
          if (value_to_compare.constructor === Array) {
            value_to_compare = value_to_compare[0];
          }
          if(column_value.includes(value_to_compare)){
            current_ans = true
          }else{
            current_ans = false
          }
        }else if(condition == "Not Contains"){
          if (value_to_compare.constructor === Array) {
            value_to_compare = value_to_compare[0];
          }
          if(column_value.includes(value_to_compare)){
            current_ans = true
          }else{
            current_ans = false
          }
        }else if(condition == "Greater than"){
          if (value_to_compare.constructor === Array) {
            value_to_compare = value_to_compare[0];
          }
          if(column_value > value_to_compare){
            current_ans = true
          }else{
            current_ans = false
          }
        }else if(condition == "Greater than equal to"){
          if (value_to_compare.constructor === Array) {
            value_to_compare = value_to_compare[0];
          }
          if(column_value >= value_to_compare){
            current_ans = true
          }else{
            current_ans = false
          }

        }else if(condition == "Smaller than"){
          if (value_to_compare.constructor === Array) {
            value_to_compare = value_to_compare[0];
          }
          if(column_value < value_to_compare){
            current_ans = true
          }else{
            current_ans = false
          }
        }else if(condition == "Smaller than equal to"){
          if (value_to_compare.constructor === Array) {
            value_to_compare = value_to_compare[0];
          }
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

  return condition_list.every(Boolean);

}

function checkRequired_save(){
  id = $(this).attr("id").replace("savebutton_","")
  minCols = $(this).attr("data_min_fields")
  minNoCols = parseInt($(this).attr("data_min_no"))
  flag = 0
  if(minCols != undefined){
    minCols = JSON.parse(minCols)
    if(minCols.includes(-1)){
      minCols = []
    }
  }else{
    minCols = []
  }
  let minCount = 0
  let inpReq = ""
  if(minCols.length > 0){
    inpReq = $(`#createview${id}`).find('.restict_min_class').filter(':visible')
  }else{
    inpReq = $(`#createview${id}`).find('input,textarea,select').filter(':visible')
  }
  let colsfire = []

  if(minCols.length > 0){

    for(let i=0;i<inpReq.length;i++){
      let rqVal = $(inpReq[i]).val()
      let col = $(inpReq[i]).attr("data-field_name")

      if (rqVal == "" || rqVal == null){
        if(minCols.includes(String(col))){
          if(minCount >= minNoCols){
            flag = 0
            break;
          }else{
            flag = 1
            colsfire.push(col)
          }
          $('#savebutton_' + id).prop('disabled', false)
        }
      }else{
        minCount = minCount + 1
      }
    }

    if(minCount >= minNoCols){
      flag = 0
    }else{
      Swal.fire({icon: 'warning',text:`Kindly fill in the value for atleast ${minNoCols} fields out of ${minCols.join()} columns !!` });
    }

  }else{

      for(let i=0;i<inpReq.length;i++){
        let rqVal = $(inpReq[i]).val()

        if (rqVal == "" || rqVal == null){
            if(minCount >= minNoCols){
              flag = 0
              break;
            }else{
              flag = 1
            }
            $('#savebutton_' + id).prop('disabled', false)
        }else{
          minCount = minCount + 1
        }
      }

      if(minCount >= minNoCols){
        flag = 0
      }else{
        Swal.fire({icon: 'warning',text:`Kindly fill in the values for atleast ${minNoCols} fields !!` });
      }

  }

    if(flag == 0){

      const type = $(`#savebutton_${id}`).val()
      let currentUrl = window.location.pathname
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
      $('#savebutton_' + id).removeAttr("onclick")
      $(`#savebutton_${id}`).click()
    }

}

let saveFileButtonCreateForm = ''
for (let i = 0; i < createViewIdList.length; i++) {
  saveFileButtonCreateForm = $(`#savefiledata_${createViewIdList[i]}`)
  saveFileButtonCreateForm.attr('disabled', true)
  let input = $(`#uploadFileInput_${createViewIdList[i]}`)
  $(`#uploadCSVBtn_${createViewIdList[i]}`).on('click', function (e) {
    e.preventDefault()
    localStorage.setItem('activeTabs', createViewIdList[i])
    const dataForm = new FormData(
      $(`#uploadCSVForm_${createViewIdList[i]}`)[0]
    )

    $(document)
      .find(`#comparable_file_card_${createViewIdList[i]}`)
      .removeAttr('hidden')
    $(document)
      .find(`#comparable_card_${createViewIdList[i]}`)
      .attr('hidden', 'hidden')
    $.ajax({
      url: `/users/${urlPath}/comparable_get_data/`,
      data: dataForm,
      type: 'POST',
      cache: false,
      contentType: false,
      processData: false,
      success: function (data) {
        if (
          $.fn.dataTable.isDataTable(
						// eslint-disable-next-line no-tabs
						`#comparable_file_table_${createViewIdList[i]}`
          )
        ) {
          $(`#comparable_file_table_${createViewIdList[i]}`)
            .DataTable()
            .clear()
            .destroy()
        }

        $(`#comparable_file_table_body_${createViewIdList[i]}`).empty()
        $(`#comparable_file_table_head_${createViewIdList[i]}`).empty()
        const data1 = JSON.parse(data)
        let html = ''
        for (const [columnName, colVal] of Object.entries(data1[0])) {
          const colName = columnName.replace('_', ' ')
          html += `<th data-value='${colVal}'>${colName}</th>`
        }
        $(`#comparable_file_table_head_${createViewIdList[i]}`).append(
          '<tr>' + html + '</tr>'
        )
        for (const row in data1) {
          let html = ''
          for (const [columnName, colVal] of Object.entries(data1[row])) {
            if (
              columnName.endsWith('For The Period') ||
							columnName.endsWith('Deviation')
            ) {
              html += `<td bgcolor="#f6f6f6">${colVal}</td>`
            } else {
              html += `<td>${colVal}</td>`
            }
          }
          $(`#comparable_file_table_body_${createViewIdList[i]}`).append(
            '<tr>' + html + '</tr>'
          )
        }

        let compFileTable = $(
					`#comparable_file_table_${createViewIdList[i]}`
        ).DataTable()

        if (
          !$.fn.dataTable.isDataTable(
						`#comparable_file_table_${createViewIdList[i]}`
          )
        ) {
          compFileTable = $(
						`#comparable_file_table_${createViewIdList[i]}`
          ).DataTable({
            autoWidth: false,
            scrollY: '50vh',
            scrollCollapse: true,
            scrollX: '110%',
            sScrollXInner: '100%',
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
              [1, 5, 50, 'All'],
            ],
            pageLength: 50,
            dom: 'lfBrtip',
            buttons: [
              {
                extend: 'collection',
                text: 'Export',
                buttons: [
                  {
                    extend: 'copy',
                    title: '',
                    exportOptions: {
                      columns: ':visible:not(.noVis)',
                    },
                  },
                  {
                    extend: 'excel',
                    title: '',
                    exportOptions: {
                      columns: ':visible:not(.noVis)',
                    },
                  },
                  {
                    extend: 'csv',
                    title: '',
                    exportOptions: {
                      columns: ':visible:not(.noVis)',
                    },
                  },
                  {
                    extend: 'pdf',
                    title: '',
                    exportOptions: {
                      columns: ':visible:not(.noVis)',
                    },
                  },
                ],
              },
              {
                extend: 'colvis',
                className: 'scroller',
              },
            ],
            columnDefs: [
              {
                targets: '_all',
                className: 'dt-center allColumnClass all',
              },
              {
                targets: 0,
                width: '20%',
                className: 'noVis',
              },
            ],
          })
          $(`#comparable_file_card_${createViewIdList[i]}`).attr(
            'hidden',
            false
          )
          $(`#savefiledata_${createViewIdList[i]}`).prop('disabled', false)
        } else {
          compFileTable.destroy()
          compFileTable = $(
						`#comparable_file_table_${createViewIdList[i]}`
          ).DataTable({
            autoWidth: false,
            scrollY: '50vh',
            scrollCollapse: true,
            scrollX: '110%',
            sScrollXInner: '100%',
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
              [1, 5, 50, 'All'],
            ],
            pageLength: 50,
            dom: 'lfBrtip',
            buttons: [
              {
                extend: 'collection',
                text: 'Export',
                buttons: [
                  {
                    extend: 'copy',
                    title: '',
                    exportOptions: {
                      columns: ':visible:not(.noVis)',
                    },
                  },
                  {
                    extend: 'excel',
                    title: '',
                    exportOptions: {
                      columns: ':visible:not(.noVis)',
                    },
                  },
                  {
                    extend: 'csv',
                    title: '',
                    exportOptions: {
                      columns: ':visible:not(.noVis)',
                    },
                  },
                  {
                    extend: 'pdf',
                    title: '',
                    exportOptions: {
                      columns: ':visible:not(.noVis)',
                    },
                  },
                ],
              },
              {
                extend: 'colvis',
                className: 'scroller',
              },
            ],
            columnDefs: [
              {
                targets: '_all',
                className: 'dt-center allColumnClass all',
              },
              {
                targets: 0,
                width: '20%',
                className: 'noVis',
              },
            ],
          })

          setTimeout(function () {
            $('.dt-center').eq(0).removeClass('sorting_asc')
            $(`#comparable_file_table_${createViewIdList[i]}`)
              .DataTable()
              .columns.adjust()
          }, 200)
          $(`#comparable_file_card_${createViewIdList[i]}`).attr(
            'hidden',
            false
          )
          $(`#savefiledata_${createViewIdList[i]}`).prop('disabled', false)
        }
      },
      error: function () {
        Swal.fire({icon: 'error',text: 'Error! Failure in exporting data. Please try again.'});
      },
    })
  })

  $(document)
    .find(`#savefiledata_${createViewIdList[i]}`)
    .off('click')
    .on('click', function (e) {
      input = $(`#uploadFileInput_${createViewIdList[i]}`)
      e.preventDefault()
      if (String(input.val()) !== '') {
        const itemCode = windowLocation.split('/')[4]
        const dataForm = new FormData(
          $(`#uploadCSVForm_${createViewIdList[i]}`)[0]
        )
        dataForm.append(
          'customValidationList',
          $(`#customValidationList${createViewIdList[i]}`).attr('value')
        )
        $.ajax({
          url: `/users/${urlPath}/${itemCode}/create_file/`,
          data: dataForm,
          type: 'POST',
          cache: false,
          contentType: false,
          processData: false,
          // eslint-disable-next-line no-unused-vars
          success: function (data) {
            window.location.reload()
          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Failure in saving data. Please try again.'});
          },
        })
      }
    })

  $(document)
    .find(`#${createViewIdList[i]}_tab_content`)
    .find('form button[name="save"]')
    .on('click', function () {
      $(document)
        .find(`#comparable_file_card_${createViewIdList[i]}`)
        .attr('hidden', 'hidden')
      $(document)
        .find(`#comparable_card_${createViewIdList[i]}`)
        .removeAttr('hidden')
      $(`#${createViewIdList[i]}_tab_content`)
        .find("form input[datatype='CharField']")
        .each(function () {
          // eslint-disable-next-line no-use-before-define
          $(this).on('change', compareFetchData)
        })
      localStorage.setItem('activeTabs', createViewIdList[i])
      // eslint-disable-next-line no-use-before-define
      compareFetchData()
      function compareFetchData () {
        const compareContext = $(document)
          .find(`#${createViewIdList[i]}_tab_content`)
          .find('form button[name="save"]')
          .attr('data-compare-context')
        let compareColumns = {}
        $(`#${createViewIdList[i]}_tab_content`)
          .find("form input[datatype='CharField']")
          .each(function () {
            compareColumns[$(this).attr('name')] = $(this).val()
          })
        $(`#comparable_card_${createViewIdList[i]}`).attr('hidden', false)
        compareColumns = JSON.stringify(compareColumns)
        $.ajax({
          url: `/users/${urlPath}/comparable_get_data/`,

          data: {
            operation: 'fetchComparables',
            comparable_dict: compareContext,
            character_value: compareColumns,
          },
          type: 'POST',
          dataType: 'json',
          success: function (data) {
            $(`#comparable_table_body_${createViewIdList[i]}`).empty()
            $(`#comparable_table_head_${createViewIdList[i]}`).empty()
            if (data !== 'empty') {
              $(`#comparable_table_head_${createViewIdList[i]}`).append(
                '<tr style=text-align:center><th>Column Name</th><th>Input Value</th><th>Existing Value</th><th>Deviation</th></tr>'
              )
              for (const columnName in data) {
                let html = ''
                const aggInputFieldValue = $(
									`#${createViewIdList[i]}_tab_content`
                )
                  .find(`form input[name="${columnName}"]`)
                  .val()
                const aggSummaryValue = data[columnName]
                const aggDeviationValue =
									Math.round(
									  Math.abs(
									    ((aggInputFieldValue - aggSummaryValue) /
												aggSummaryValue) *
												100
									  )
									) + '%'
                let colName = columnName.replace('_', ' ')
                colName = colName.charAt(0).toUpperCase() + colName.slice(1)

                html += `<td>${colName}</td>`
                html += `<td>${aggInputFieldValue}</td>`
                html += `<td bgcolor="#f6f6f6">${aggSummaryValue}</td>`
                html += `<td bgcolor="#f6f6f6">${aggDeviationValue}</td>`

                $(`#comparable_table_body_${createViewIdList[i]}`).append(
                  '<tr>' + html + '</tr>'
                )
              }
              if (
                !$.fn.dataTable.isDataTable(
									`#comparable_table_${createViewIdList[i]}`
                )
              ) {
                $(`#comparable_table_${createViewIdList[i]}`).DataTable({
                  autoWidth: true,
                  scrollY: '50vh',
                  scrollCollapse: true,
                  scrollX: '110%',
                  sScrollXInner: '100%',
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
                    [1, 5, 50, 'All'],
                  ],
                  pageLength: 50,
                  dom: 'lfBrtip',
                  sScrollX: '120%',
                  buttons: [
                    {
                      extend: 'colvis',
                      className: 'scroller',
                    },
                  ],
                  columnDefs: [
                    {
                      targets: '_all',
                      className: 'dt-center allColumnClass all',
                    },
                    {
                      targets: 0,
                      width: '27%',
                      className: 'noVis',
                    },
                  ],
                })
              } else {
                $(`#comparable_table_body_${createViewIdList[i]}`)
                  .find('tr')
                  .each(function () {
                    $(this).find('td:nth-child(1)').attr('tabindex', '0')
                    $(this)
                      .find('td')
                      .each(function () {
                        $(this).addClass('dt-center allColumnClass all')
                      })
                  })
                $(`#comparable_table_head_${createViewIdList[i]}`)
                  .find('tr')
                  .each(function () {
                    $(this)
                      .find('td')
                      .each(function () {
                        $(this).addClass('dt-center allColumnClass all')
                      })
                  })
              }
            } else {
              $(`#comparable_table_head_${createViewIdList[i]}`).empty()
              $(`#comparable_table_head_${createViewIdList[i]}`).append(
                '<tr><th>No Records Exists</th></tr>'
              )
            }

            $(`#${createViewIdList[i]}_tab_content`)
              .find('form button[name="submit"]')
              .prop('disabled', false)
          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          },
        })
      }
      // end
    })
}

// Preview Create View
// eslint-disable-next-line no-unused-vars


async function viewPdfCreateView(obj){
  const elementId = obj.getAttribute('data-element-id')
  $(obj).html(`<i class="fa fa-circle-notch fa-spin"></i>`)
  function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
    await sleep(500);
    var wid = document.getElementById('previewCreateViewBody').offsetWidth
    var hei = document.getElementById('previewCreateViewBody').offsetHeight
    let tabtitle = $(`#${elementId}-tab`).find('.span_content_editable').text()
      await html2canvas(document.getElementById('previewCreateViewBody'), { allowTaint: true }).then(function(canvas) {

        var imgData = canvas.toDataURL('image/png');
        var doc = new jsPDF("l","px",[wid,hei]);
        doc.addImage(imgData, 'PNG',0,0,doc.internal.pageSize.width, doc.internal.pageSize.height);
        doc.save(`${tabtitle}.pdf`);
        $(obj).html(`Download Pdf`)
  })


}
function previewCreateViewPdfSave(obj){

  const elementId = obj.getAttribute('data-element-id')
  const templateName = obj.getAttribute('data-template-name')
  const tableName = obj.getAttribute('data-table-name')
  const itemCode = windowLocation.split('/')[4]
  const templateListType = ['Constraint', 'Asset Grouping']
  let tabtitle = $(`#${elementId}-tab`).find('.span_content_editable').text()
  $('#previewCreateviewHeader').empty()
  $('#previewCreateviewHeader').append(`<h6 class="modal-title"  style="width:100%;color:white;margin:auto;font-weight:bold;">${tabtitle}</h6>
  <button type="button" class="close" data-dismiss="modal">&times;</button>`)




  event.preventDefault();

  let final_html = "<div class='form-row'>"
  let html_data = $(`#createview${elementId}`).find('.form-row').each(function(){
    final_html += $(this).html()
  })
  final_html = final_html + "</div>"


  let dictOfInputvalues = {}
  let arrayOfInputs = $(`#createview${elementId}`).find('.form-row').find("input , select , textarea").each(function(){
    dictOfInputvalues[$(this).attr('id')+"modal"] = $(this).val()
  })

    $('#previewCreateViewBody').empty();
    $('#previewCreateViewBody').append(final_html);
    $('#previewCreateViewBody').css('pointer-events','none');
    $('#previewCreateViewBody').find("input , select , textarea").each(function(){
      $(this).attr("id",$(this).attr("id") + "modal")
      $(this).parent().find(".select2-container").css("width","");
    });
    for (var key in dictOfInputvalues){
      $('#previewCreateViewBody').find("#"+key).removeAttr("onclick");
      $('#previewCreateViewBody').find("#"+key).removeAttr("onchange");
      $('#previewCreateViewBody').find("#"+key).val(dictOfInputvalues[key]).trigger("change")
    }


    $('#previewCreateViewModal').find('#previewCreateView_footer').empty()
      $('#previewCreateViewModal').find('#previewCreateView_footer').append(`
    <button type="button" class="btn btn-primary btn-xs mx-2 rounded px-2" data-dismiss="modal" id='savebuttonpreview_${elementId}'>Submit</button>
    <button onclick = "viewPdfCreateView(this)" type="button" class="btn btn-primary btn-xs mx-2 rounded px-2">Download Pdf</button>
    <button type="button" class="btn btn-primary btn-xs mx-2 rounded px-2" data-dismiss="modal">Close</button>
    `)
    $('#previewCreateViewModal').modal('show')
    $(`#savebuttonpreview_${elementId}`).on('click', function () {
      if (String(templateName) === 'Constraint') {
        $(`#savebuttoninfo${elementId}`).removeAttr('onclick')
        $(`#savebuttoninfo${elementId}`).removeAttr('data-preview-mode')
        $(`#savebuttoninfo${elementId}`).click()
      } else if (String(templateName) === 'Asset Grouping') {
        $(`#savebuttonasset${elementId}`).removeAttr('onclick')
        $(`#savebuttonasset${elementId}`).removeAttr('data-preview-mode')
        $(`#savebuttonasset${elementId}`).click()
      } else {
        $(`#savebutton_${elementId}`).removeAttr('onclick')
        const connectedListviewId = $(`#savebutton_${elementId}`).attr('connected_listview_id')
        if (connectedListviewId) {
          const linkedListview = $(`#savebutton_${elementId}`).attr('connected_listview_id')
          localStorage.setItem('activeTabs', linkedListview)
        } else {
          localStorage.setItem('activeTabs', elementId)
        }
        const type = $(`#savebutton_${elementId}`).val()
        let currentUrl = window.location.pathname
        let idEle = $(`#savebutton_${elementId}`).attr('id').split('whiteSpacewrap')[1]
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
          $(`#savebutton_${elementId}`).attr('formaction', submitFormUrl)
        } else if (String(type) === 'Save as Draft') {
          $(`#savebutton_${elementId}`).attr('formaction', submitFormDraftUrl)
        }


        $(`#savebutton_${elementId}`).attr('type', 'submit')
        $(`#savebutton_${elementId}`).attr('name', 'submit')
        $(`#savebutton_${elementId}`).click()
      }
    })

}


function previewCreateViewSave (obj) {
  // eslint-disable-line no-unused-vars
  const elementId = obj.getAttribute('data-element-id')
  const templateName = obj.getAttribute('data-template-name')
  const tableName = obj.getAttribute('data-table-name')
  const itemCode = windowLocation.split('/')[4]
  const templateListType = ['Constraint', 'Asset Grouping']
  let tabtitle = $(`#${elementId}-tab`).find('.span_content_editable').text();

  $('#previewCreateviewHeader').empty()
  $('#previewCreateviewHeader').append(`<h6 class="modal-title"  style="width:100%;color:white;margin:auto;font-weight:bold;">${tabtitle}</h6>
  <button type="button" class="close" data-dismiss="modal">&times;</button>`)
  $.ajax({
    url: `/users/${urlPath}/${itemCode}/`,
    data: {
      model_name: tableName,
      operation: 'previewCreateViewData',
    },
    type: 'POST',
    dataType: 'json',
    success: function (data) {
      const finalContext = JSON.parse(data.context)
      const context = finalContext.context_data
      $('#previewCreateViewBody').empty()
      for (const tableKey in context) {
        let theadHtml = ''
        let trowHtml = ''
        $('#previewCreateViewBody').append(
					`<table id='previewCreateViewTable_${tableKey}'></table>`
        )
        if ($.fn.dataTable.isDataTable(`#previewCreateView_${tableKey}`)) {
          $(`#previewCreateViewTable_${tableKey}`)
            .DataTable()
            .clear()
            .destroy()
        }
        $(`#previewCreateViewTable_${tableKey}`).empty()

        // Create Header
        for (const fieldKey in context[tableKey]) {
          theadHtml += `<th>${context[tableKey][fieldKey]}</th>`
        }
        // Create Rows
        trowHtml += '<tr>'
        let rowVal = ''
        for (const fieldKey in context[tableKey]) {
          if (templateListType.includes(templateName)) {
            rowVal = $(`#createview${elementId}`)
              .find(`input[data-name='${fieldKey}']`)
              .val()
            if (!rowVal) {
              rowVal = $(`#createview${elementId}`)
                .find(`select[data-name='${fieldKey}']`)
                .val()
            }
          } else {
            if(templateName == "Multi Select"){
              rowVal = $(`#createview${elementId}`)
              .find(
								`textarea[data-tablename='${tableKey}']`
              ).parent().parent().find(`[id='${elementId}_${fieldKey}_unique']`)
              .val()
            }else{
              rowVal = $(`#createview${elementId}`)
              .find(
								`textarea[data-tablename='${tableKey}'][id='id_${fieldKey}_${elementId}']`
              )
              .val()
            }

            if (!rowVal) {
              rowVal = $(`#createview${elementId}`)
                .find(
									`input[data-tablename='${tableKey}'][id='id_${fieldKey}_${elementId}']`
                )
                .attr('type')
              if (String(rowVal) === 'undefined') {
                rowVal = $(`#createview${elementId}`)
                  .find(`input[id='id_${fieldKey}_${elementId}']`)
                  .attr('type')
                if (!rowVal) {
                  rowVal = $(`#createview${elementId}`)
                    .find(
											`select[data-tablename='${tableKey}'][id='id_${fieldKey}_${elementId}']`
                    )
                    .val()
                } else {
                  if (String(rowVal) === 'checkbox') {
                    rowVal = $(`#createview${elementId}`).find(
											`input[id='id_${fieldKey}_${elementId}']`
                    )
                    if (rowVal.prop('checked')) {
                      rowVal = 'on'
                    } else {
                      rowVal = 'off'
                    }
                  } else {
                    rowVal = $(`#createview${elementId}`)
                      .find(`input[id='id_${fieldKey}_${elementId}']`)
                      .val()
                  }
                }
              } else {
                if(templateName == "Multi Select"){
                  rowVal = $(`#createview${elementId}`)
                    .find(
                      `input[data-tablename='${tableKey}'][id='id_${fieldKey}_${elementId}']`
                    )
                    .val()

                    if(rowVal.startsWith("{")){
                      rowVal = $(`#createview${elementId}`)
                        .find(
                          `[id='${elementId}_${fieldKey}_unique']`
                        )
                        .val()
                    }
                }else{
                  rowVal = $(`#createview${elementId}`)
                    .find(
                      `input[data-tablename='${tableKey}'][id='id_${fieldKey}_${elementId}']`
                    )
                    .val()
                }
                if (!rowVal) {
                  rowVal = $(`#createview${elementId}`)
                    .find(
											`select[data-tablename='${tableKey}'][id='id_${fieldKey}_${elementId}']`
                    )
                    .val()
                }
              }
            }
          }

          if (rowVal && String(rowVal) !== '') {
            trowHtml += `<td>${rowVal}</td>`
          } else {
            trowHtml += '<td> --- </td>'
          }
        }
        trowHtml += '</tr>'

        $(`#previewCreateViewTable_${tableKey}`)
          .append(`<thead><tr id='header_column_${tableKey}' style='border-bottom:2px solid var(--primary-color);width:100%'>
      ${theadHtml}</tr></thead>
      <tbody>${trowHtml}</tbody>`)
        $(`#previewCreateViewTable_${tableKey}`).DataTable({
          autoWidth: false,
          scrollY: 200,
          scrollX: 500,
          scrollCollapse: true,
          sScrollXInner: '100%',
          bInfo: false,
          bRetrieve: true,
          bProcessing: true,
          bDestroy: true,
          ordering: false,
          orderCellsTop: true,
          responsive: true,

          colReorder: {
            fixedColumnsLeft: 1,
          },
          deferRender: true,
          paging: true,
          lengthMenu: [
            [1, 5, 50, -1],
            [1, 5, 50, 'All'],
          ],
          pageLength: 50,
          dom: 'lfBrtip',
          buttons: [],
          columnDefs: [
            {
              targets: '_all',
              className: 'dt-center allColumnClass all',
            },
            {
              targets: 0,
              width: '20%',
              className: 'noVis',
            },
          ],
        })
      }

      $('#previewCreateViewModal').find('#previewCreateView_footer').empty()
      $('#previewCreateViewModal').find('#previewCreateView_footer').append(`
    <button type="button" class="btn btn-primary btn-xs mx-2 rounded px-2" data-dismiss="modal" id='savebuttonpreview_${elementId}'>Submit</button>
    <button type="button" class="btn btn-primary btn-xs mx-2 rounded px-2" data-dismiss="modal">Close</button>
    `)

      setTimeout(function () {
        $(document).find('.standard_button_click').prop('disabled', false)
        $(document).find('.button_standard_save').prop('disabled', false)
      }, 200)
      $('#previewCreateViewModal').modal('show')

      $(`#savebuttonpreview_${elementId}`).on('click', function () {
        if (String(templateName) === 'Constraint') {
          $(`#savebuttoninfo${elementId}`).removeAttr('onclick')
          $(`#savebuttoninfo${elementId}`).removeAttr('data-preview-mode')
          $(`#savebuttoninfo${elementId}`).click()
        } else if (String(templateName) === 'Asset Grouping') {
          $(`#savebuttonasset${elementId}`).removeAttr('onclick')
          $(`#savebuttonasset${elementId}`).removeAttr('data-preview-mode')
          $(`#savebuttonasset${elementId}`).click()
        } else {
          $(`#savebutton_${elementId}`).removeAttr('onclick')
          const connectedListviewId = $(`#savebutton_${elementId}`).attr('connected_listview_id')
          if (connectedListviewId) {
            const linkedListview = $(`#savebutton_${elementId}`).attr('connected_listview_id')
            localStorage.setItem('activeTabs', linkedListview)
          } else {
            localStorage.setItem('activeTabs', elementId)
          }
          const type = $(`#savebutton_${elementId}`).val()
          let currentUrl = window.location.pathname
          let idEle = $(`#savebutton_${elementId}`).attr('id').split('whiteSpacewrap')[1]
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
            $(`#savebutton_${elementId}`).attr('formaction', submitFormUrl)
          } else if (String(type) === 'Save as Draft') {
            $(`#savebutton_${elementId}`).attr('formaction', submitFormDraftUrl)
          }


          $(`#savebutton_${elementId}`).attr('type', 'submit')
          $(`#savebutton_${elementId}`).attr('name', 'submit')
          $(`#savebutton_${elementId}`).trigger("click")
        }
      })
      // Adjust the Columns of Created datatable
      setTimeout(function () {
        for (const tableKey in context) {
          $(`#previewCreateViewTable_${tableKey}`).DataTable().columns.adjust()
        }
      }, 200)
    },
    error: function () {
      Swal.fire({icon: 'error',text: 'Error! Failure in displaying data. Please try again.'});
    },
  })
}

// Preview Draft Saved
for (let i = 0; i < createViewIdList.length; i++) {

  $(document)
    .find(`#${createViewIdList[i]}_tab_content`)
    .find('form button[name="previewButton"]')
    .off('click')
    .on('click', function () {
      const tableName = $(this).attr('data-table-name')
      const tabId = $(this).attr('id')
      const createViewId = tabId.substring(tabId.indexOf('_') + 1)
      let viewrtfcb_mode = $(this).attr('viewrtfcb_mode')
      let draftCols = $(this).attr("data-draft_cols")
      let columnAlignment = {};
      let columnAlignmentDef = [];
      if ($(this).attr("data-column-alignment")) {
        columnAlignment = JSON.parse($(this).attr("data-column-alignment"));
      } else {
        columnAlignmentDef.push(
          {
            targets: "_all",
            className: 'dt-center allColumnClass all',
          }
        );
      }
      if(draftCols){
        draftCols = JSON.parse(draftCols)
        if(tableName in draftCols){
          draftCols = draftCols[tableName]
        }else{
          draftCols = []
        }
      }else{
        draftCols = []
      }
      const saveDraftpath = '#saveDraftbutton_' + createViewId

      $.ajax({
        url: `/users/${urlPath}/constriant_get_data/`,
        data: {
          operation: 'preview_data_fetch',
          table_name: tableName,
          create_viewID: createViewId,
        },
        type: 'POST',
        dataType: 'json',
        success: function (data) {

          if ($.fn.dataTable.isDataTable('#previewTable')) {
            $('#previewTable').DataTable().clear().destroy()
          }

          $('#previewTable').empty()

          if (data.previewList.length > 0) {
            $('#previewTable').append(
              "<thead><tr class='header_column' style='border-bottom:2px solid var(--primary-color);width:100%'>"
            )
            $('#previewTable')
              .find('.header_column')
              .append('<td style="font-weight:bolder">Actions</td>')
            for(let [key,value] of Object.entries(data.verboseName)){
              if(draftCols.length > 0){
                if(draftCols.includes(key)){
                  $('#previewTable')
                  .find('.header_column')
                  .append(
                    `<td style="font-weight:bolder">${value}</td>`
                  )
                }
              }else{
                $('#previewTable')
                .find('.header_column')
                .append(
									`<td style="font-weight:bolder">${value}</td>`
                )
              }
            }

            $('#previewTable').append('</thead></tr>')

            $('#previewTable').append('<tbody class="tbody"></tbody>')
            for (let i = 0; i < data.previewList.length; i++) {
              $('#previewTable')
                .find('.tbody')
                .append(`<tr class="column_${i}">`)

                $('#previewTable')
                .find(`.column_${i}`)
                .append(
									`<td>
                    <a data-toggle="tooltip" title="Save As Final" class"SaveAsFinal" id="SaveAsFinal${data.table_id[i]}" data-elementID="${data.table_id[i]}" data-table_model_name="${tableName}" value="detail">
                      <i name="actions" value="Save" class="fa-solid fa-floppy-disk ihover javaSC thin-icon" style="font-size: 15px"></i>
                    </a>&nbsp;
                    <a data-toggle="tooltip" class="edit_button" title="Edit record" data-elementID="${data.table_id[i]}" data-table_name="${tableName}" id="EditRecord${data.table_id[i]}" value="update">
                      <i name="actions" value="Edit" class="fa fa-edit ihover javaSC thin-icon" style="font-size:15px"></i>
                    </a>&nbsp;
                    <a data-toggle="tooltip" class="delete_button" title="Delete record" data-elementID="${data.table_id[i]}" data-table_name="$(this).attr('data-table-name')" value="delete"
                    id="deletedraft${data.table_id[i]}"><i name="actions" value="Delete" class="far fa-trash-alt ihover javaSC" style="font-size:15px"></i></a>
                  </td>`
                )

              for (
                let vi = 0;
                vi < Object.keys(data.verboseName).length;
                vi++
              ) {
                const previewKeys = Object.keys(data.previewList[i])
                const verbAns = Object.keys(data.verboseName)[vi]
                const colVerb = tableName + '__' + verbAns
                var fieldArray = [];
                if(draftCols.length > 0){

                  if(draftCols.includes(verbAns)){
                    fieldArray.push(verbAns);
                    if (previewKeys.includes(colVerb)) {
                      if (data.previewList[i][colVerb]) {
                        const colVerbValue = data.previewList[i][colVerb];
                        const startsWithBracket = colVerbValue.startsWith('<');
                        let tdContent = startsWithBracket
                          ? viewrtfcb_mode === 'True'
                            ? `<button class="view_data_btn" style="background-color: transparent; border: transparent;" onclick="showRTFDataCreateView.call(this)" data-data="${colVerbValue}">View Data</button>`
                            : colVerbValue
                          : colVerbValue;
                          if (colVerbValue.startsWith('<')) {
                          }

                          if ((typeof(data.previewList[i][colVerb])==='string') && data.previewList[i][colVerb].startsWith('[')){
                            $('#previewTable')
                            .find(`.column_${i}`)
                            .append(`<td class="view_details_wrap"> <button class="view_data_btn table_field_show_button" style="background-color: transparent; border: transparent;" onclick="showTableDataCreateView.call(this)" data-json = '${data.previewList[i][colVerb]}'>View Data</button> </td>`);
                          }
                          else{
                            const tdElement = `<td class="view_details_wrap" data-preview-name="${colVerb}">${tdContent}</td>`;;

                            $('#previewTable')
                              .find(`.column_${i}`)
                              .append(tdElement);
                          }
                      } else {
                        $('#previewTable')
                          .find(`.column_${i}`)
                          .append(`<td class="view_details_wrap" data-preview-name="${colVerb}"> - </td>`)
                      }
                    } else if (previewKeys.includes(verbAns)) {
                      if (data.previewList[i][verbAns]) {
                        $('#previewTable')
                          .find(`.column_${i}`)
                          .append(
                            `<td class="view_details_wrap" data-preview-name="${verbAns}">${data.previewList[i][verbAns]}</td>`
                          )
                      } else {
                        $('#previewTable')
                          .find(`.column_${i}`)
                          .append(`<td class="view_details_wrap" data-preview-name="${verbAns}"> - </td>`)
                      }
                    } else {
                      $('#previewTable')
                        .find(`.column_${i}`)
                        .append('<td class="view_details_wrap"> - </td>')
                    }
                  }

                }else{
                  fieldArray.push(verbAns);
                  if (previewKeys.includes(colVerb)) {
                    if (data.previewList[i][colVerb]) {
                      const colVerbValue = data.previewList[i][colVerb];
                      const startsWithBracket = colVerbValue.startsWith('<');
                      let tdContent = startsWithBracket
                      ? viewrtfcb_mode === 'True'
                        ? `<button class="view_data_btn" style="background-color: transparent; border: transparent;" onclick="showRTFDataCreateView.call(this)" data-data="${colVerbValue}">View Data</button>`
                        : colVerbValue
                      : colVerbValue;
                      if (colVerbValue.startsWith('<')) {

                      }

                      if ((typeof(data.previewList[i][colVerb])==='string') && data.previewList[i][colVerb].startsWith('[')){
                        $('#previewTable')
                        .find(`.column_${i}`)
                        .append(`<td class="view_details_wrap"> <button class="view_data_btn table_field_show_button" style="background-color: transparent; border: transparent;" onclick="showTableDataCreateView.call(this)" data-json = '${data.previewList[i][colVerb]}'>View Data</button> </td>`);
                      }
                      else{
                        const tdElement = `<td class="view_details_wrap" data-preview-name="${colVerb}">${tdContent}</td>`;;

                        $('#previewTable')
                          .find(`.column_${i}`)
                          .append(tdElement);
                      }

                    }else {
                      $('#previewTable')
                        .find(`.column_${i}`)
                        .append(`<td class="view_details_wrap" data-preview-name="${colVerb}"> - </td>`)
                    }
                  } else if (previewKeys.includes(verbAns)) {


                    if (data.previewList[i][verbAns]) {

                      $('#previewTable')
                        .find(`.column_${i}`)
                        .append(
                          `<td class="view_details_wrap" data-preview-name="${verbAns}">${data.previewList[i][verbAns]}</td>`
                        )
                    } else {

                      $('#previewTable')
                        .find(`.column_${i}`)
                        .append(`<td class="view_details_wrap" data-preview-name="${verbAns}"> - </td>`)
                    }
                  } else {


                    $('#previewTable')
                      .find(`.column_${i}`)
                      .append('<td class="view_details_wrap"> - </td>')
                  }
                }


              }

              if (Object.keys(columnAlignment).length) {
                let globalHeader = columnAlignment.global_header;
                let globalContent = columnAlignment.global_content;
                if (columnAlignment.field_level_config) {
                  columnAlignmentDef = [];
                  for (index in draftCols) {
                    var fieldChar = draftCols[index];
                    var fieldName = fieldChar.replace(`${tableName}__`, '');
                    if (columnAlignment.field_level_config[fieldName]) {
                      var header = columnAlignment.field_level_config[fieldName].header;
                      var content = columnAlignment.field_level_config[fieldName].content;
                      columnAlignmentDef.push(
                        {
                          targets: [Number(index) + 1],
                          className: `dt-head-${header} dt-body-${content} allColumnClass all`,
                        }
                      )
                    } else {
                      columnAlignmentDef.push(
                        {
                          targets: [Number(index) + 1],
                          className: `dt-head-${globalHeader} dt-body-${globalContent} allColumnClass all`,
                        }
                      )
                    }
                  }
                }
              }
              columnAlignmentDef.push(
                {
                  targets: [0],
                  className: `dt-center allColumnClass all`,
                }
              )

              $('#previewTable').append('</tr>')

              $('#previewTable').find(`#deletedraft${data.table_id[i]}`).on('click', function (){
                const dataElementID = $(this).attr('data-elementid')
                const its_tr = $(this).closest('tr');
                its_tr.remove();

                $.ajax({
                  url: `/users/${urlPath}/constriant_get_data/`,
                  data: {
                    element_id: dataElementID,
                    operation: 'remove_from_draft_table',
                  },
                  type: 'POST',
                  dataType: 'json',
                  // eslint-disable-next-line no-unused-vars
                  success: function (data) {
                    Swal.fire({icon: 'success',text: 'Deleted successfully!'});
                  },
                  error: function () {
                    Swal.fire({icon: 'error',text: 'Error! Failure in executing request. Please try again.'});
                  },
                })
              })

              $('#previewTable').find(`#EditRecord${data.table_id[i]}`).on('click', function (){
                const dataElementID = $(this).attr('data-elementid')
                $('#draftModal').modal('hide')

                $(saveDraftpath).attr('data-table-id', dataElementID)
                $(saveDraftpath).attr('data-entry', 'Existing')

                const currentDataElementID = dataElementID
                for (const n in data.completeData) {
                  if (
                    Object.keys(data.completeData[n])[0] ===
                    currentDataElementID
                  ) {
                    const userInfo =
                      data.completeData[n][currentDataElementID]
                    if ('approvalAssignmentConfig' in userInfo){
                      const approvalAssignmentConfig_1 = JSON.parse(userInfo['approvalAssignmentConfig'])
                      if (Object.keys(approvalAssignmentConfig_1).length > 0){
                        $(`#approvalAssignmentConfig${createViewId}`).val(JSON.stringify(approvalAssignmentConfig_1));
                        $(`#approvalAssignmentParameterModal${createViewId}`).find(`#selectNatureOfApproval${createViewId}`).val(approvalAssignmentConfig_1['approval_type']).trigger("change")
                        $(`#approvalAssignmentParameterModal${createViewId}`).find(`#selectNatureOfApproval${createViewId}`).val(approvalAssignmentConfig_1['approval_type']).trigger("select2:select")
                        if (approvalAssignmentConfig_1['approval_type'] =='multi_level'){
                          if ('level_config' in approvalAssignmentConfig_1){
                            $(`#multi_level_parameter${createViewId}`).find(".multi_approval_levels").empty();
                            for (let d in approvalAssignmentConfig_1['level_config']){
                              $(`#approvalAssignmentParameterModal${createViewId}`).find(`#add_levels_button${createViewId}`).click();
                              var singleCard = $(`#approvalAssignmentParameterModal${createViewId}`).find('.multi_level_form_group').eq(-1)
                              $(singleCard).find('.selectApproverType').val(approvalAssignmentConfig_1['level_config'][d]['approver_type']).trigger('change')
                              $(singleCard).find('.selectApproverLevel').val(approvalAssignmentConfig_1['level_config'][d]['approver_list']).trigger('change')
                            }
                          }
                        }else{
                          $(`#approvalAssignmentParameterModal${createViewId}`).find(`#selectApproverTypeUAA${createViewId}`).val(approvalAssignmentConfig_1['approver_type']).trigger('change')
                          $(`#approvalAssignmentParameterModal${createViewId}`).find(`#selectApproverUsersUAA${createViewId}`).val(approvalAssignmentConfig_1['approver_list']).trigger('change')
                        }
                      }else{
                        $(`#approvalAssignmentParameterModal${createViewId}`).find(`#selectApproverUsersUAA${createViewId}`).val([]).trigger('change')
                      }
                    }
                    for (const i in userInfo) {
                      let colName = ''
                      if (i.startsWith(tableName + '__')) {
                        colName = i.split(tableName + '__')
                        colName = colName[1]
                      } else {
                        colName = i
                      }

                      if(draftCols.length > 0){
                        if(draftCols.includes(colName)){

                          if (
                            String(
                              $(`#id_${colName}_${createViewId}`).attr('type')
                            ) === 'checkbox' &&
                            String(userInfo[i]) === 'on'
                          ) {
                            $(`#id_${colName}_${createViewId}`)
                              .val('')
                              .trigger('change')
                            $(`#id_${colName}_${createViewId}`)
                              .val(userInfo[i])
                              .trigger('select2:select')
                            $(`#id_${colName}_${createViewId}`)
                              .val(userInfo[i])
                              .trigger('change')
                            $(`#id_${colName}_${createViewId}`).click()
                          } else {
                            if(userInfo[i].startsWith("{")){
                              $(`#id_${colName}_${createViewId}`)
                                .val(userInfo[i])
                                .trigger('change')
                              mulval = JSON.parse(userInfo[i])
                              mulval = Object.keys(mulval)
                              try{
                                $(`#${createViewId}_${colName}_unique`)
                                .val(mulval)
                                .trigger('change')
                              }catch(err) {}
                            } else if($(`#id_${colName}_${createViewId}`).hasClass("select2")){
                                $(`#id_${colName}_${createViewId}`).attr("data-reload",userInfo[i])
                                $(`#id_${colName}_${createViewId}`)
                                .val(userInfo[i])
                                .trigger('select2:select')
                                try{
                                  $(`#id_${colName}_${createViewId}`)
                                  .val(userInfo[i])
                                  .trigger('change')
                                }catch(err) {}
                            } else if($(`#id_${colName}_${createViewId}[data-tablename='${tableName}']`).parent().find("p[title='RTF editor']").length > 0){
                              if(userInfo[i]){
                                $(`#id_${colName}_${createViewId}[data-tablename='${tableName}']`).parent().find("p[title='RTF editor']").attr('data-data',userInfo[i])
                                $(`#id_${colName}_${createViewId}[data-tablename='${tableName}']`).val(userInfo[i])
                              }
                            } else if ($(`#id_${colName}_${createViewId}`).attr('datatype') == 'FileField') {
                              $(`#id_${colName}_${createViewId}`)
                                .val(userInfo[i])
                                .trigger('change')
                              var existingFiles = userInfo[i].split(", ");
                              if (existingFiles.length) {
                                var uploadedFileContainerElement = $(`#${colName}_${createViewId}_upload_modal`).find('.uploaded-files-gallery');
                                for (key of existingFiles) {
                                  uploadedFileContainerElement.append(`
                                  <li class="list-group-item d-flex justify-content-between align-items-center">
                                    ${key}
                                    <span class="badge previewUploadedFile" style="margin-right:0; margin-left:auto;" data-file-name="${key}"><a href='/media/uploaded_files/${key}' target="_blank"><i class="fas fa-eye fa-2x"></i></a></span>
                                    <span class="badge downloadUploadedFile" style="margin-right:0;" data-file-name="${key}"><a href='/media/uploaded_files/${key}' target="_blank" download="${key}"><i class="fas fa-download fa-2x"></i></a></span>
                                    <span class="badge removeUploadedFile" data-file-name="${key}"><i class="fas fa-trash-alt fa-2x" style="color:red;"></i></span>
                                  </li>
                                  `);
                                  uploadedFileContainerElement.find('.list-group-item').eq(-1).find('.removeUploadedFile').on('click', function(){
                                    $(this).parent().remove();
                                  });
                                }
                              }
                            } else {
                              $(`#id_${colName}_${createViewId}`)
                                .val(userInfo[i])
                                .trigger('change')
                            }

                            $(`#${createViewIdList[i]}_tab_content`)
                              .find('form input[type="checkbox"]')
                              .trigger('click')
                          }
                        }
                      }else{

                        if (
                          String(
                            $(`#id_${colName}_${createViewId}`).attr('type')
                          ) === 'checkbox' &&
                          String(userInfo[i]) === 'on'
                        ) {
                          $(`#id_${colName}_${createViewId}`)
                            .val(userInfo[i])
                            .trigger('change')
                          $(`#id_${colName}_${createViewId}`).click()
                        } else {
                          if(userInfo[i].startsWith("{")){
                            $(`#id_${colName}_${createViewId}`)
                              .val(userInfo[i])
                              .trigger('change')
                            mulval = JSON.parse(userInfo[i])
                            mulval = Object.keys(mulval)
                            try{
                              $(`#${createViewId}_${colName}_unique`)
                              .val(mulval)
                              .trigger('change')
                            }catch(err) {}
                          } else if($(`#id_${colName}_${createViewId}`).hasClass("select2")){
                              $(`#id_${colName}_${createViewId}`).attr("data-reload",userInfo[i])
                              $(`#id_${colName}_${createViewId}`).find(`option[value="${userInfo[i]}"]`).prop('disabled', false);
                              $(`#id_${colName}_${createViewId}`)
                              .val(userInfo[i])
                              .trigger('select2:select')
                              try{
                                $(`#id_${colName}_${createViewId}`)
                                .val(userInfo[i])
                                .trigger('change')
                              }catch(err) {}
                          } else if($(`#id_${colName}_${createViewId}[data-tablename='${tableName}']`).parent().find("p[title='RTF editor']").length > 0){
                            if(userInfo[i]){
                              $(`#id_${colName}_${createViewId}[data-tablename='${tableName}']`).parent().find("p[title='RTF editor']").attr('data-data',userInfo[i])
                              $(`#id_${colName}_${createViewId}[data-tablename='${tableName}']`).val(userInfo[i])
                            }
                          } else if($(`#id_${colName}_${createViewId}`).attr('datatype') == 'FileField') {
                            $(`#id_${colName}_${createViewId}`)
                              .val(userInfo[i])
                              .trigger('change')
                            var existingFiles = userInfo[i].split(", ");
                            if (existingFiles.length) {
                              var uploadedFileContainerElement = $(`#${colName}_${createViewId}_upload_modal`).find('.uploaded-files-gallery');
                              for (key of existingFiles) {
                                uploadedFileContainerElement.append(`
                                <li class="list-group-item d-flex justify-content-between align-items-center">
                                  ${key}
                                  <span class="badge previewUploadedFile" style="margin-right:0; margin-left:auto;" data-file-name="${key}"><a href='/media/uploaded_files/${key}' target="_blank"><i class="fas fa-eye fa-2x"></i></a></span>
                                  <span class="badge downloadUploadedFile" style="margin-right:0;" data-file-name="${key}"><a href='/media/uploaded_files/${key}' target="_blank" download="${key}"><i class="fas fa-download fa-2x"></i></a></span>
                                  <span class="badge removeUploadedFile" data-file-name="${key}"><i class="fas fa-trash-alt fa-2x" style="color:red;"></i></span>
                                </li>
                                `);
                                uploadedFileContainerElement.find('.list-group-item').eq(-1).find('.removeUploadedFile').on('click', function(){
                                  $(this).parent().remove();
                                });
                              }
                            }
                          } else {
                            $(`#id_${colName}_${createViewId}`)
                              .val(userInfo[i])
                              .trigger('change')
                          }

                          $(`#${createViewIdList[i]}_tab_content`)
                            .find('form input[type="checkbox"]')
                            .trigger('click')
                        }
                      }
                    }
                  }
                }
              })

              $('#previewTable').find(`#SaveAsFinal${data.table_id[i]}`).on('click', function (){
                const dataElementID = $(this).attr('data-elementid')
                $(`#savebutton_${dataElementID}`).removeAttr('onclick')
                $('#draftModal').modal('hide')

                const currentDataElementID = dataElementID
                let colName = ''
                for (const n in data.completeData) {
                  if (
                    String(Object.keys(data.completeData[n])[0]) ===
                    currentDataElementID
                  ) {
                    const userInfo =
                      data.completeData[n][currentDataElementID];
                    if ('approvalAssignmentConfig' in userInfo){
                      const approvalAssignmentConfig_1 = JSON.parse(userInfo['approvalAssignmentConfig'])
                      if (Object.keys(approvalAssignmentConfig_1).length > 0){
                        $(`#approvalAssignmentConfig${createViewId}`).val(JSON.stringify(approvalAssignmentConfig_1));
                        $(`#approvalAssignmentParameterModal${createViewId}`).find(`#selectNatureOfApproval${createViewId}`).val(approvalAssignmentConfig_1['approval_type']).trigger("change")
                        $(`#approvalAssignmentParameterModal${createViewId}`).find(`#selectNatureOfApproval${createViewId}`).val(approvalAssignmentConfig_1['approval_type']).trigger("select2:select")
                        if (approvalAssignmentConfig_1['approval_type'] =='multi_level'){
                          if ('level_config' in approvalAssignmentConfig_1){
                            $(`#multi_level_parameter${createViewId}`).find(".multi_approval_levels").empty();
                            for (let d in approvalAssignmentConfig_1['level_config']){
                              $(`#approvalAssignmentParameterModal${createViewId}`).find(`#add_levels_button${createViewId}`).click();
                              var singleCard = $(`#approvalAssignmentParameterModal${createViewId}`).find('.multi_level_form_group').eq(-1)
                              $(singleCard).find('.selectApproverType').val(approvalAssignmentConfig_1['level_config'][d]['approver_type']).trigger('change')
                              $(singleCard).find('.selectApproverLevel').val(approvalAssignmentConfig_1['level_config'][d]['approver_list']).trigger('change')
                            }
                          }
                        }else{
                          $(`#approvalAssignmentParameterModal${createViewId}`).find(`#selectApproverTypeUAA${createViewId}`).val(approvalAssignmentConfig_1['approver_type']).trigger('change')
                          $(`#approvalAssignmentParameterModal${createViewId}`).find(`#selectApproverUsersUAA${createViewId}`).val(approvalAssignmentConfig_1['approver_list']).trigger('change')
                        }
                      }else{
                        $(`#approvalAssignmentParameterModal${createViewId}`).find(`#selectApproverUsersUAA${createViewId}`).val([]).trigger('change')
                      }
                    }
                    for (const i in userInfo) {
                      if (i.startsWith(tableName + '__')) {
                        colName = i.split(tableName + '__')
                        colName = colName[1]
                      } else {
                        colName = i
                      }

                      if(draftCols.length > 0){
                        if(draftCols.includes(colName)){

                          if (
                            String(
                              $(`#id_${colName}_${createViewId}`).attr('type')
                            ) === 'checkbox' &&
                            String(userInfo[i]) === 'on'
                          ) {
                            $(`#id_${colName}_${createViewId}`)
                              .val(userInfo[i])
                              .trigger('change')
                            $(`#id_${colName}_${createViewId}`).click()
                          } else {
                            if(userInfo[i].startsWith("{")){
                              $(`#id_${colName}_${createViewId}`)
                                .val(userInfo[i])
                                .trigger('change')
                              mulval = JSON.parse(userInfo[i])
                              mulval = Object.keys(mulval)
                              try{
                                $(`#${createViewId}_${colName}_unique`)
                                .val(mulval)
                                .trigger('change')
                              }catch(err) {}
                            } else if($(`#id_${colName}_${createViewId}`).hasClass("select2")){
                                $(`#id_${colName}_${createViewId}`).attr("data-reload",userInfo[i])
                                $(`#id_${colName}_${createViewId}`).find(`option[value="${userInfo[i]}"]`).prop('disabled', false);
                                $(`#id_${colName}_${createViewId}`)
                                .val(userInfo[i])
                                .trigger('select2:select')
                                $(`#id_${colName}_${createViewId}`)
                                .val(userInfo[i])
                            } else if($(`#id_${colName}_${createViewId}[data-tablename='${tableName}']`).parent().find("p[title='RTF editor']").length > 0){
                              if(userInfo[i]){
                                $(`#id_${colName}_${createViewId}[data-tablename='${tableName}']`).parent().find("p[title='RTF editor']").attr('data-data',userInfo[i])
                                $(`#id_${colName}_${createViewId}[data-tablename='${tableName}']`).val(userInfo[i])
                              }
                            } else if ($(`#id_${colName}_${createViewId}`).attr('datatype') == 'FileField') {
                              $(`#id_${colName}_${createViewId}`)
                                .val(userInfo[i])
                              var existingFiles = userInfo[i].split(", ");
                              if (existingFiles.length) {
                                var uploadedFileContainerElement = $(`#${colName}_${createViewId}_upload_modal`).find('.uploaded-files-gallery');
                                for (key of existingFiles) {
                                  uploadedFileContainerElement.append(`
                                  <li class="list-group-item d-flex justify-content-between align-items-center">
                                    ${key}
                                    <span class="badge previewUploadedFile" style="margin-right:0; margin-left:auto;" data-file-name="${key}"><a href='/media/uploaded_files/${key}' target="_blank"><i class="fas fa-eye fa-2x"></i></a></span>
                                    <span class="badge downloadUploadedFile" style="margin-right:0;" data-file-name="${key}"><a href='/media/uploaded_files/${key}' target="_blank" download="${key}"><i class="fas fa-download fa-2x"></i></a></span>
                                    <span class="badge removeUploadedFile" data-file-name="${key}"><i class="fas fa-trash-alt fa-2x" style="color:red;"></i></span>
                                  </li>
                                  `);
                                  uploadedFileContainerElement.find('.list-group-item').eq(-1).find('.removeUploadedFile').on('click', function(){
                                    $(this).parent().remove();
                                  });
                                }
                              }
                            } else {
                              $(`#id_${colName}_${createViewId}`)
                                .val(userInfo[i])
                            }

                            $(`#${createViewIdList[i]}_tab_content`)
                              .find('form input[type="checkbox"]')
                              .trigger('click')
                          }
                        }
                      }else{

                        if (
                          String(
                            $(`#id_${colName}_${createViewId}`).attr('type')
                          ) === 'checkbox' &&
                          String(userInfo[i]) === 'on'
                        ) {
                          $(`#id_${colName}_${createViewId}`)
                            .val(userInfo[i])
                          $(`#id_${colName}_${createViewId}`).click()
                        } else {
                          if(userInfo[i].startsWith("{")){
                            $(`#id_${colName}_${createViewId}`)
                              .val(userInfo[i])
                              .trigger('change')
                            mulval = JSON.parse(userInfo[i])
                            mulval = Object.keys(mulval)
                            try{
                              $(`#${createViewId}_${colName}_unique`)
                              .val(mulval)
                              .trigger('change')
                            }catch(err) {}
                          } else if($(`#id_${colName}_${createViewId}`).hasClass("select2")){
                              $(`#id_${colName}_${createViewId}`).attr("data-reload",userInfo[i])
                              $(`#id_${colName}_${createViewId}`).find(`option[value="${userInfo[i]}"]`).prop('disabled', false);
                              $(`#id_${colName}_${createViewId}`)
                              .val(userInfo[i])
                              .trigger('select2:select')
                          } else if($(`#id_${colName}_${createViewId}[data-tablename='${tableName}']`).parent().find("p[title='RTF editor']").length > 0){
                            if(userInfo[i]){
                              $(`#id_${colName}_${createViewId}[data-tablename='${tableName}']`).parent().find("p[title='RTF editor']").attr('data-data',userInfo[i])
                              $(`#id_${colName}_${createViewId}[data-tablename='${tableName}']`).val(userInfo[i])
                            }
                          } else if ($(`#id_${colName}_${createViewId}`).attr('datatype') == 'FileField') {
                            $(`#id_${colName}_${createViewId}`)
                              .val(userInfo[i])
                              .trigger('change')
                            var existingFiles = userInfo[i].split(", ");
                            if (existingFiles.length) {
                              var uploadedFileContainerElement = $(`#${colName}_${createViewId}_upload_modal`).find('.uploaded-files-gallery');
                              for (key of existingFiles) {
                                uploadedFileContainerElement.append(`
                                <li class="list-group-item d-flex justify-content-between align-items-center">
                                  ${key}
                                  <span class="badge previewUploadedFile" style="margin-right:0; margin-left:auto;" data-file-name="${key}"><a href='/media/uploaded_files/${key}' target="_blank"><i class="fas fa-eye fa-2x"></i></a></span>
                                  <span class="badge downloadUploadedFile" style="margin-right:0;" data-file-name="${key}"><a href='/media/uploaded_files/${key}' target="_blank" download="${key}"><i class="fas fa-download fa-2x"></i></a></span>
                                  <span class="badge removeUploadedFile" data-file-name="${key}"><i class="fas fa-trash-alt fa-2x" style="color:red;"></i></span>
                                </li>
                                `);
                                uploadedFileContainerElement.find('.list-group-item').eq(-1).find('.removeUploadedFile').on('click', function(){
                                  $(this).parent().remove();
                                });
                              }
                            }
                          } else {
                            $(`#id_${colName}_${createViewId}`)
                              .val(userInfo[i])
                          }

                          $(`#${createViewIdList[i]}_tab_content`)
                            .find('form input[type="checkbox"]')
                            .trigger('click')
                        }

                      }
                    }
                  }
                }

                if ($(`#savebutton_${createViewId}`).trigger('click')) {
                  $.ajax({
                    url: `/users/${urlPath}/constriant_get_data/`,
                    data: {
                      element_id: dataElementID,
                      operation: 'remove_from_draft_to_final',
                    },
                    type: 'POST',
                    dataType: 'json',
                    // eslint-disable-next-line no-unused-vars
                    success: function (data) {
                    },
                    error: function () {
                      Swal.fire({icon: 'error',text: 'Error! Failure in executing request. Please try again.'});
                    },
                  })
                }
              })
            }
            $('#previewTable thead tr').eq(0)
              .clone(true)
              .appendTo('#previewTable thead')
            $('#previewTable thead tr').eq(1).find("td").eq(0).html('')
            $('#previewTable thead tr').eq(0).find("td").eq(0).css('cursor', 'default')
            $('#previewTable thead tr').eq(0).find("td").eq(0).css(
              'background-image',
              'none'
            )
            $('#previewTable thead tr').eq(1).find('td').css('padding', '5px')
            $('#previewTable thead tr').eq(1).find('td').each(function () {
              $(this).addClass('dt-center')
              const title = $(this).text()
              $(this).html(
                '<input type="text" data-input_value="" style="text-align:center;border-bottom:none;border:1px solid #ced4da;width:190px;"placeholder="Search ' +
                  title +
                  '" />'
              )
              $('input', this).on('keyup change', function () {
                $(this).attr('data-input_value', this.value.trim())
                const regEx1 = /^[\w]/
                const regEx2 = /^[^=^\w^\s]|^[==]/
                const tables = $('#previewTable').DataTable()
                if (regEx1.test(this.value) || String(this.value) === '') {
                  const indexOfTheElement = $(this).parent().index()
                  const colIndexInt = parseInt(indexOfTheElement)
                  if (
                    String(tables.column(colIndexInt).search()) !==
                    String(this.value)
                  ) {
                    tables.column(colIndexInt).search(this.value).draw()
                  }
                } else if (regEx2.test(this.value)) {
                  tables.draw()
                  const regEx3 = /^\W+/
                  if (regEx3.test(this.value)) {
                    const condition = this.value.match(/\W+/g)
                    const refinedCondition = this.value.replace(/^\W+/, '')
                    const refinedSearchParam = refinedCondition.trim()
                    const rhs = parseInt(refinedSearchParam)
                    const indexOfTheElement = $(this).parent().index()
                    const colIndexInt = parseInt(indexOfTheElement)
                    if (!isNaN(rhs)) {
                      $.fn.dataTable.ext.search.push(function (
                        settings,
                        /* eslint-disable no-unused-vars */
                        searchData,
                        index,
                        rowData,
                        counter
                        /* eslint-enable no-unused-vars */
                      ) {
                        if (String(settings.nTable.id) !== 'previewTable') {
                          return true
                        }
                        const evalString =
                          `searchData[${colIndexInt}]` + condition[0] + rhs

                        if (eval(evalString)) {
                          // eslint-disable-line no-eval
                          return true
                        }
                        return false
                      })
                      tables.draw()
                      $.fn.dataTable.ext.search.pop()
                      tables.search.pop()
                    }
                  }
                }
              })
            })
            if (!$.fn.dataTable.isDataTable('#previewTable')) {
              $('#previewTable').DataTable({
                autoWidth: true,
                scrollY: 200,
                scrollX: 500,
                scrollCollapse: true,
                sScrollXInner: '100%',
                bInfo: false,
                bRetrieve: true,
                bProcessing: true,
                bDestroy: true,
                ordering: false,
                orderCellsTop: true,
                responsive: true,
                colReorder: {
                  fixedColumnsLeft: 1,
                },
                deferRender: true,
                paging: true,
                lengthMenu: [
                  [1, 5, 50, -1],
                  [1, 5, 50, 'All'],
                ],
                pageLength: 50,
                dom: 'lfBrtip',
                buttons: [],
                columnDefs: columnAlignmentDef,
              })
            }
            $('#draftModal').modal('show')
          } else {
            Swal.fire({icon: 'warning',text:"No draft records exists!" });
          }
        },
        error: function () {
          Swal.fire({icon: 'warning',text:"No draft records exists!" });
        },
      })
      $(this).attr('type', 'button')
    })
}

// Draft Save
for (let i = 0; i < createViewIdList.length; i++) {
  const saveDraftButtonCreateForm = $(
		`#${createViewIdList[i]}_tab_content`
  ).find('form button[name="submit"]')
  // eslint-disable-next-line no-unused-vars

  saveDraftButtonCreateForm.on('click', function (event) {
    const type = $(this).val()
    let currentUrl = window.location.pathname
    // eslint-disable-next-line camelcase
    if (item_code_list) {
      // eslint-disable-next-line camelcase
      for (let j = 0; j < item_code_list.length; j++) {
        // eslint-disable-next-line camelcase
        currentUrl = `/users/${urlPath}/` + item_code_list[j][createViewIdList[i]] + '/'
      }
    }
    const dataTableId = $(this).attr('data-table-id')
    const dataEntry = $(this).attr('data-entry')
    const submitFormDraftUrl = currentUrl + 'createDraft/' + dataEntry
    if (String(type) === 'Save as Draft') {
      if (String($(this).attr('data-entry')) === 'New') {
        $(this).attr('formaction', submitFormDraftUrl + '/id/')
      } else if (String($(this).attr('data-entry')) === 'Existing') {
        $(this).attr(
          'formaction',
          submitFormDraftUrl + '/' + dataTableId + '/'
        )
      }
    }
    $(this).attr('type', 'submit')
  })
}

// Reset Draft

for (let i = 0; i < createViewIdList.length; i++) {
  const resetDraftButtonCreateForm = $(
		`#${createViewIdList[i]}_tab_content`
  ).find('form button[name="resetDraft"]')

  resetDraftButtonCreateForm.off('click').on('click', function () {
    const tabId = $(this).attr('id')
    const createViewId = tabId.substring(tabId.indexOf('_') + 1)
    const saveDraft = $(`#${createViewId}_tab_content`).find(
      'form button[value="Save as Draft"]'
    )
    const pastVal = saveDraft.attr('data-entry')
    let resetStatus = 'New'
    if (String(pastVal) === 'New') {
      resetStatus = 'Existing'
    }



    $.ajax({
      url: `/users/${urlPath}/dynamicVal/`,

      data: {'operation': 'fetch_custom_messages','element_id':  createViewIdList[i], 'message':'reset_draft_message'},
      type: "POST",
      dataType: "json",
      success: function (data) {
        var text = `Click 'Yes' to confirm or click 'No' if you do not wish to reset it.`
        if(data.data.custom_messages){
          text = data.data.custom_messages.message
          icon = data.data.custom_messages.icon
        }

        resetAlert(text,icon)
      },
        error: function () {
          Swal.fire({icon: 'error',text: 'Error! Please try again.'});
        }
    })
    var resetAlert = (text,icon) =>{
      const confirmReset = null
      iconHtml = ""
      if (icon){
        iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
      }
      Swal.fire({
        icon: 'question',
        iconHtml,
        title:`Reset Draft Status: ${pastVal}  => ${resetStatus}.`,
        text,
        showDenyButton: true,
        showCancelButton: true,
        confirmButtonText: 'Yes',
        denyButtonText:'No',
      }).then((result) => {
        if (result.isConfirmed) {
          confirmReset = true
        }else if (result.isDenied) {
          confirmReset = false
        }
      })
      if (confirmReset) {
        saveDraft.attr('data-entry', 'New')
        saveDraft.removeAttr('data-table-id')
      }
      $(this).attr('type', 'button')
    }
  })
}
for (let i = 0; i < createViewIdList.length; i++) {
  const autoComputeBtn = $(`#autoCompute_${createViewIdList[i]}`)
  if  (autoComputeBtn.length > 0){
    const elementId = $(autoComputeBtn).attr('data-elementID')
    const computedValueList = []
    let main_config_dict = {}
    let source_dict = {}
    const valuesDic = {}
    const datatypeList = []
    $('#createview' + elementId)
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

      $(`#id_${key}_${createViewIdList[i]}`).on("change dp.change", function(){

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

                $('#createview' + elementId)
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
                      if (Object.keys(context.data[0]).includes(value[i])) {
                        let outputValue = context.data[0][value[i]]
                        $('#id_' + value[i] + '_' + elementId)
                          .val(outputValue)
                          .trigger('change')
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
// eslint-disable-next-line no-unused-vars
function calVal () {
  // eslint-disable-line no-unused-vars
  const valuesDic = {}
  const elementId = $(this).attr('data-elementID')
  const datatypeList = []
  const tableName = $(this)
    .attr('data-table-name')
    .replace('["', '')
    .replace('"]', '')
  const computedValueList = []
  let allOkFlag = 1

  $('#createview' + elementId)
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
    })

  $('#createview' + elementId)
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
      operation: 'find_comp_necessary_fields',
      table_name: JSON.stringify(tableName),
      comp_fields: JSON.stringify(computedValueList),
    },
    type: 'POST',
    dataType: 'json',
    success: function (context) {
      if(Object.keys(context).length > 0){
        for (let i = 0; i < context.data.length; i++) {
          if ($('#id_' + context.data[i] + '_' + elementId).val() === '') {
            Swal.fire({icon: 'warning',text:`kindly fill in the value in the field ${context.data[i]}.` });
            allOkFlag = 0
          }
        }
      }

      if (allOkFlag) {
        $.ajax({
          url: `/users/${urlPath}/dynamicVal/`,
          data: {
            element_id: elementId,
            operation: 'calculate_computed_value',
            values_dic: JSON.stringify(valuesDic),
            datatype_list: JSON.stringify(datatypeList),
            table_name: JSON.stringify(tableName),
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
    },
    error: function () {
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    },
  })
}

// Histry Create View Function
// eslint-disable-next-line no-unused-vars
function HistoryViewTable (obj) {
  // eslint-disable-line no-unused-vars
  const itemCode = windowLocation.split('/')[4]
  const viewrtfcb_mode = obj.getAttribute('viewrtfcb_mode')
  const elementId = obj.getAttribute('data-elementid')
  const tableName = obj.getAttribute('data-table-name')
  let view_history_display_cols = obj.getAttribute('data_history_display_cols')
  let columnAlignment = {};
  let columnAlignmentDef = [];
  if (obj.getAttribute('data-column-alignment')) {
    columnAlignment = JSON.parse(obj.getAttribute('data-column-alignment'));
  } else {
    columnAlignmentDef.push(
      {
        targets: "_all",
        className: 'dt-center allColumnClass all',
      }
    );
  }

  if(view_history_display_cols){
    view_history_display_cols = JSON.parse(view_history_display_cols)
    if(tableName in view_history_display_cols){
      view_history_display_cols = view_history_display_cols[tableName]
    }else{
      view_history_display_cols = []
    }
  }else{
    view_history_display_cols = []
  }
  const queryData = {}
  let tableList = obj.getAttribute('data-table-name')
  if (tableList) {
    if (tableList.startsWith('[') && tableList.endsWith(']')) {
      tableList = JSON.parse(tableList)
    } else {
      tableList = [tableList]
    }
  }
  if (obj.hasAttribute('data_history_cols')) {
    let createQueryData = obj.getAttribute('data_history_cols')

    if (String(createQueryData) !== '{}') {
      createQueryData = JSON.parse(createQueryData)

      for (const tname of tableList) {
        if (Object.keys(createQueryData).includes(tname)) {
          if (createQueryData[tname].length > 0) {
            for (let rc = 0; rc < createQueryData[tname].length; rc++) {
              const field = createQueryData[tname][rc]
              if (
                $(`#id_${field}_${elementId}[data-tablename='${tname}']`)
                  .length > 0 &&
								String(
								  $(`#id_${field}_${elementId}[data-tablename='${tname}']`).css(
								    'display'
								  )
								) !== 'none' &&
								String(
								  $(`#id_${field}_${elementId}[data-tablename='${tname}']`)
								    .closest(`#div_id_${field}`)
								    .css('display')
								) !== 'none' &&
								String(
								  $(`#id_${field}_${elementId}[data-tablename='${tname}']`)
								    .closest(`#div_id_${field}`)
								    .parent()
								    .css('display')
								) !== 'none'
              ) {
                let rowVal = $(
									`#id_${field}_${elementId}[data-tablename='${tname}']`
                ).val()
                if (!rowVal) {
                  rowVal = 'NULL'
                }

                if (rowVal) {
                  if (!Object.prototype.hasOwnProperty.call(queryData, tname)) {
                    queryData[tname] = []
                  }
                  queryData[tname].push({
                    column_name: field,
                    condition: 'Equal to',
                    input_value: rowVal,
                  })
                }
              } else if (
                $(`input[data-name='${field}']`).length > 0 &&
								String($(`input[data-name='${field}']`).css('display')) !==
									'none'
              ) {
                let rowVal = $(`input[data-name='${field}']`).val()

                if (!rowVal) {
                  rowVal = 'NULL'
                }

                if (rowVal) {
                  if (!Object.prototype.hasOwnProperty.call(queryData, tname)) {
                    queryData[tname] = []
                  }
                  queryData[tname].push({
                    column_name: field,
                    condition: 'Equal to',
                    input_value: rowVal,
                  })
                }
              } else if (
                String(
                  $(`select[data-name='${field}']`).length > 0 &&
										$(`select[data-name='${field}']`).parent().css('display')
                ) !== 'none'
              ) {
                let rowVal = $(`select[data-name='${field}']`).val()

                if (!rowVal) {
                  rowVal = 'NULL'
                }

                if (rowVal) {
                  if (!Object.prototype.hasOwnProperty.call(queryData, tname)) {
                    queryData[tname] = []
                  }
                  queryData[tname].push({
                    column_name: field,
                    condition: 'Equal to',
                    input_value: rowVal,
                  })
                }
              }
            }
          } else {
            queryData[tname] = []
          }
        } else {
          queryData[tname] = []
        }
      }
    }
  }
  const template = obj.getAttribute('data-template')
  $(`#createHistoryView${elementId}`)
    .find('.card-header')
    .find('.card-title')
    .text('View History')
  $.ajax({
    url: `/users/${urlPath}/${itemCode}/`,
    data: {
      create_form_data: JSON.stringify(queryData),
      element_id: elementId,
      operation: 'create_history_view',
    },
    type: 'POST',
    dataType: 'json',
    success: function (data) {
      const context = JSON.parse(data.context)
      const verboseList = JSON.parse(data.verboseList)
      var columnsToDisplay = []

      if (view_history_display_cols.length >0 && tableName in verboseList){
        for (let i in verboseList[tableName]){
          if (view_history_display_cols.includes(verboseList[tableName][i])){
            columnsToDisplay.push(i)
          }
        }
      }
      let firstKey = Object.keys(context)[0];
        let viewRejectedRecordsData = ""
        if (context.hasOwnProperty(firstKey)) {
          viewRejectedRecordsData = context[firstKey];
        } else {
        }
        if (viewRejectedRecordsData.length > 0) {
          const firstRow = viewRejectedRecordsData[0];

          let tableHTML = `
            <table id="createhistory_datatable_${firstKey}_${elementId}" class="createhistory_datatable row-border display">
              <thead>
                <tr>
          `;
          if (columnsToDisplay.length>0){
            for (const key of Object.keys(firstRow)) {
              if (columnsToDisplay.includes(key) || key == 'Actions'){
                tableHTML += `<th>${key}</th>`;
              }
            }
          }else{
            for (const key of Object.keys(firstRow)) {
                tableHTML += `<th>${key}</th>`
            }
          }


          tableHTML += `
                </tr>
              </thead>
              <tbody>
          `;

          for (const dataRow of viewRejectedRecordsData) {
            tableHTML += "<tr>";
            if(columnsToDisplay.length>0){
              for (const value in dataRow) {
                if (columnsToDisplay.includes(value) || value == 'Actions'){
                  if((typeof(dataRow[value]) === 'string') && dataRow[value].startsWith('[')){
                    tableHTML += `<td><button class="view_data_btn table_field_show_button" style="background-color: transparent; border: transparent;" onclick="showHistory_in_tabular.call(this)" data-json='${dataRow[value]}'>View Data</button></td>`;
                  }
                  else{
                    tableHTML += `<td>${dataRow[value]}</td>`;
                  }
                }
              }
            }
            else{
              for (const value in dataRow) {
                if((typeof(dataRow[value]) === 'string') && dataRow[value].startsWith('[')){
                  tableHTML += `<td><button class="view_data_btn table_field_show_button" style="background-color: transparent; border: transparent;" onclick="showHistory_in_tabular.call(this)" data-json='${dataRow[value]}'>View Data</button></td>`;
                }
                else{
                  tableHTML += `<td>${dataRow[value]}</td>`;
                }
              }
            }
            tableHTML += "</tr>";
          }

          tableHTML += `
              </tbody>
            </table>
          `;
          const targetElement = $(`#createHistoryView${elementId}`).find('.card-body').find('.card-table_insertion');
          targetElement.empty();
          targetElement.append(tableHTML);
          $(`#createhistory_datatable_${firstKey}_${elementId}`)
          .find('tbody tr')
          .each(function() {
            const firstCell = $(this).find('td:first-child');
            const linkContent = `<a data-toggle="tooltip" data-template="${template}" onclick="addTransactionToForm.call(this)" data-element-id="${elementId}" data-verboselist='${JSON.stringify(verboseList)}' class="create_history_edit" data-table-name='${firstKey}' title="Edit record" value="update"><i name="actions" value="Edit" class="fa fa-edit ihover javaSC thin-icon" style="font-size:15px"></i></a>`;
            firstCell.html(linkContent);
            $(this).find('td').each(function() {
              const cellContent = $(this).html();
              if (cellContent.startsWith('<') && !cellContent.toLowerCase().startsWith('<a')) {
                const buttonContent = viewrtfcb_mode === 'True'
                  ? `<button class="view_data_btn" style="background-color: transparent; border: transparent;" onclick="showRTFDataCreateView.call(this)" data-data="${cellContent.replace(/"/g, '&quot;')}">View Data</button>`
                  : cellContent;
                $(this).html(buttonContent);
              }
            });

          });
          $(`#createhistory_datatable_${firstKey}_${elementId}`).find("tbody").find("td").addClass("view_details_wrap");
          if (Object.keys(columnAlignment).length) {
            let globalHeader = columnAlignment.global_header;
            let globalContent = columnAlignment.global_content;
            if (columnAlignment.field_level_config) {
              columnAlignmentDef = [];
              for (index in columnsToDisplay) {

                var fieldName = columnsToDisplay[index];
                if (columnAlignment.field_level_config[fieldName]) {
                  var header = columnAlignment.field_level_config[fieldName].header;
                  var content = columnAlignment.field_level_config[fieldName].content;
                  columnAlignmentDef.push(
                    {
                      targets: [Number(index)],
                      className: `dt-head-${header} dt-body-${content} allColumnClass all`,
                    }
                  )
                } else {
                  columnAlignmentDef.push(
                    {
                      targets: [Number(index)],
                      className: `dt-head-${globalHeader} dt-body-${globalContent} allColumnClass all`,
                    }
                  )
                }
              }
            }
          }

          columnAlignmentDef.push(
            {
              targets: ['_all'],
              className: `dt-center allColumnClass all`,
            }

          )

          var historyTable = $(`#createhistory_datatable_${firstKey}_${elementId}`).DataTable({
            autoWidth: true,
            scrollY: '40vh',
            scrollX: '500vh',
            scrollCollapse: true,
            sScrollXInner: '100%',
            bRetrieve: true,
            bProcessing: true,
            bDestroy: true,
            orderCellsTop: true,
            responsive: true,

            colReorder: {
              fixedColumnsLeft: 1,
            },
            deferRender: true,
            paging: true,
            lengthMenu: [
              [1, 5, 50, -1],
              [1, 5, 50, 'All'],
            ],
            pageLength: 50,
            dom: 'lfBrtip',
            buttons: [],
            columnDefs: columnAlignmentDef,
          }).columns.adjust()
          $(`#createHistoryView${elementId}`).css('display', 'block');
          targetElement.css('display', 'block');
          historyTable.columns.adjust()
        }
    },
    error: function () {
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    },
  })
}

function addTransactionToForm() {
  const currentRow = $(this).closest('tr').find('td')
  const currentTable = $(this).attr('data-table-name')
  var verboseList = JSON.parse($(this).attr('data-verboselist'));
  var template = $(this).attr('data-template');
  var elementId = $(this).attr('data-element-id');
  const constraintList = []
  currentRow.each(function () {
    var currentVal = $(this).text()
    const button = document.querySelector('.view_data_btn');

    if(currentVal=="View Data" && button.classList.contains('table_field_show_button')){

      if (button.innerHTML === 'View Data') {

          const jsonData = button.getAttribute('data-json');
          currentVal = jsonData
      }
    }

    let colName = $(this)
      .closest('tbody')
      .prev('thead')
      .find('> tr > th').eq($(this).index())
      .text()
    if (Object.keys(verboseList[currentTable]).includes(colName)) {
      colName = verboseList[currentTable][colName]
    }

    if (String(template) === 'Constraint') {
      if (colName === 'constraint_parameter') {
        constraintList.push({ col_name: colName, value: currentVal })
      } else if (colName === 'constraint_parameter_value') {
        constraintList.push({ col_name: colName, value: currentVal })
      } else {
        $(`input[data-name='${colName}']`)
          .val(currentVal)
          .trigger('change')
        setTimeout(() => {
          $(`select[data-name='${colName}']`)
            .val(currentVal)
            .trigger('change')
          $(`select[data-name='${colName}']`)
            .val(currentVal)
            .trigger('select2:select')
        }, 1000)
      }
    } else if (String(template) === 'Asset Grouping') {
      $(`input[data-name='${colName}']`)
        .val(currentVal)
        .trigger('change')
      setTimeout(() => {
        $(`select[data-name='${colName}']`)
          .val(currentVal)
          .trigger('change')
        $(`select[data-name='${colName}']`)
          .val(currentVal)
          .trigger('select2:select')
      }, 1000)
    } else {
      if (
        String($(`#id_${colName}_${elementId}`).attr('type')) ===
        'checkbox'
      ) {
        $(`#id_${colName}_${elementId}`).prop('checked', false)
        if (String(currentVal) === 'True' || String(currentVal) === 'on' || String(currentVal) === '1') {
          $(`#id_${colName}_${elementId}`).prop('checked', true)
        }
      } else if (
        String(
          $(`#${elementId}_unique[data-column='${colName}']`).attr('type')
        ) === 'text'
      ) {
        if (
          currentVal &&
          currentVal.startsWith('{') &&
          currentVal.endsWith('}')
        ) {
          const multiData = JSON.parse(currentVal)
          $(`#${elementId}_unique[data-column='${colName}']`).click()
          setTimeout(function () {
            $(`#masterTable${elementId}`)
              .find('tbody')
              .find('.io')
              .prop('checked', false)
            $(`#masterTable${elementId}`)
              .find('tbody')
              .find('.ioI')
              .val()
            $(`#masterTable${elementId}`)
              .find('tbody')
              .find('tr')
              .each(function () {
                const currentRow = $(this).find('td').eq(-1).text()
                if (Object.keys(multiData).includes(currentRow)) {
                  $(this)
                    .find('td')
                    .eq(0)
                    .find('input')
                    .prop('checked', true)
                  $(this)
                    .find('td')
                    .find('.ioI')
                    .val(multiData[currentRow])
                }
              })
            $(`#formModal${elementId}`)
              .find('.modal-footer')
              .find('.savebutton')
              .click()
          }, 130)
        } else {
          setTimeout(function () {
            $(`#masterTable${elementId}`)
              .find('tbody')
              .find('.io')
              .prop('checked', false)
            $(`#masterTable${elementId}`)
              .find('tbody')
              .find('.ioI')
              .val()
            $(`#formModal${elementId}`)
              .find('.modal-footer')
              .find('.savebutton')
              .click()
          }, 130)
        }
      } else {
        if($(`#id_${colName}_${elementId}[data-tablename='${currentTable}']`).hasClass("select2")){
          $(`#id_${colName}_${elementId}[data-tablename='${currentTable}']`)
          .val(currentVal)
          .trigger('select2:select')
          try{
            $(`#id_${colName}_${elementId}[data-tablename='${currentTable}']`)
            .val(currentVal)
            .trigger('change')
          }catch(err) {}
        }else if($(`#id_${colName}_${elementId}[data-tablename='${currentTable}']`).parent().find("p[title='RTF editor']").length > 0){
          if(currentVal){
            const dataToSet = $(this).find('button').length ? $(this).find('button').attr('data-data') : $(this).html();
            $(`#id_${colName}_${elementId}[data-tablename='${currentTable}']`).parent().find("p[title='RTF editor']").attr('data-data',dataToSet)
            $(`#id_${colName}_${elementId}[data-tablename='${currentTable}']`).val($(this).find('button').attr('data-data'))
          }
        }else{
          $(`#id_${colName}_${elementId}[data-tablename='${currentTable}']`)
          .val(currentVal)
          .trigger('change')
        }
      }
    }
  })

  if (constraintList.length > 0) {
    if (String(template) === 'Constraint') {
      setTimeout(function () {
        $('.constraint_row_column')
          .val(constraintList[0].value)
          .trigger('select2:select')
        $('.constraint_row_column')
          .val(constraintList[0].value)
          .trigger('change')
      }, 1200)
      setTimeout(function () {
        $('.constraint_row_value')
          .val(constraintList[1].value)
          .trigger('select2:select')
        $('.constraint_row_value')
          .val(constraintList[1].value)
          .trigger('change')
      }, 1600)
    }
  }
}

// Rejected Entry Function
// eslint-disable-next-line no-unused-vars
function ViewRejectedEntryTable (obj) {
  // eslint-disable-line no-unused-vars'
  const itemCode = windowLocation.split('/')[4]
  const elementID = obj.getAttribute('data-elementid')
  const viewrtfcb_mode = obj.getAttribute('viewrtfcb_mode')
  const tableName = obj.getAttribute('data-table-name')
  let view_rejected_records_display_cols = obj.getAttribute('data_rejected_records_display_cols')
  let tableList = obj.getAttribute('data-table-name')
  let columnAlignment = {};
  let columnAlignmentDef = [];

  if(view_rejected_records_display_cols){
    view_rejected_records_display_cols = JSON.parse(view_rejected_records_display_cols)
    if(tableName in view_rejected_records_display_cols){
      view_rejected_records_display_cols = view_rejected_records_display_cols[tableName]
    }else{
      view_rejected_records_display_cols = []
    }
  }else{
    view_rejected_records_display_cols = []
  }
  if (obj.getAttribute('data-column-alignment')) {
    columnAlignment = JSON.parse(obj.getAttribute('data-column-alignment'));
  } else {
    columnAlignmentDef.push(
      {
        targets: "_all",
        className: 'dt-center allColumnClass all',
      }
    );
  }

  if (tableList) {
    if (!tableList.startsWith('[') && !tableList.endsWith(']')) {
      tableList = JSON.stringify([tableList])
    }
  }
  const template = obj.getAttribute('data-template')
  $(`#createHistoryView${elementID}`)
    .find('.card-header')
    .find('.card-title')
    .text('View Rejected Records')
  $.ajax({
    url: `/users/${urlPath}/${itemCode}/`,
    data: {
      table_list: tableList,
      element_id: elementID,
      operation: 'create_view_rejected_entries',
    },
    type: 'POST',
    dataType: 'json',
    success: function (data) {
      if (data.Error) {
          Swal.fire({icon: 'error',text:"Error! Workflow cannot be executed. Please check the workflow configuration." });
        } else{
          let context = JSON.parse(data.context)
          let verboseList = JSON.parse(data.verboseList)
          let commentList = JSON.parse(data.commentList)
          let firstKey = Object.keys(context)[0];
          let viewRejectedRecordsData = ""
          var columnsToDisplay_Rejected = []

          if (view_rejected_records_display_cols.length >0 && tableName in verboseList){
            for (let i in verboseList[tableName]){
              if (view_rejected_records_display_cols.includes(verboseList[tableName][i])){
                columnsToDisplay_Rejected.push(i)
              }
            }
          }

          if (context.hasOwnProperty(firstKey)) {
            viewRejectedRecordsData = context[firstKey];
          } else {
          }
          if (viewRejectedRecordsData.length > 0) {
            const firstRow = viewRejectedRecordsData[0];

            let tableHTML = `
              <table id="createhistory_datatable_${firstKey}_${elementID}" class="createhistory_datatable row-border display" style="width:100%;">
                <thead>
                  <tr>
            `;

            if (columnsToDisplay_Rejected.length>0){
              for (const key of Object.keys(firstRow)) {
                if (columnsToDisplay_Rejected.includes(key) || key == 'Actions' || key == 'Rejected By' || key == 'Comment'){
                  tableHTML += `<th>${key}</th>`;
                }
              }
            }else{
              for (const key of Object.keys(firstRow)) {
                  tableHTML += `<th>${key}</th>`
              }
            }

            tableHTML += `
                  </tr>
                </thead>
                <tbody>
            `;

            for (const dataRow of viewRejectedRecordsData) {
              tableHTML += "<tr>";
              if(columnsToDisplay_Rejected.length>0){
                for (const value in dataRow) {
                  if (columnsToDisplay_Rejected.includes(value) || value == 'Actions' || value == 'Rejected By' || value == 'Comment'){
                    if((typeof(dataRow[value]) === 'string') && dataRow[value].startsWith('[')){
                      tableHTML += `<td><button class="view_data_btn table_field_show_button" style="background-color: transparent; border: transparent;" onclick="showRejected_in_tabular.call(this)" data-json='${dataRow[value]}'>View Data</button></td>`;
                    }
                    else{
                      tableHTML += `<td>${dataRow[value]}</td>`;
                    }
                  }
                }
              }
              else{
                for (const value in dataRow) {
                  if((typeof(dataRow[value]) === 'string') && dataRow[value].startsWith('[')){
                    tableHTML += `<td><button class="view_data_btn table_field_show_button" style="background-color: transparent; border: transparent;" onclick="showRejected_in_tabular.call(this)" data-json='${dataRow[value]}'>View Data</button></td>`;
                  }
                  else{
                    tableHTML += `<td>${dataRow[value]}</td>`;
                  }
                }
              }
              tableHTML += "</tr>";
            }


            tableHTML += `
                </tbody>
              </table>
            `;

            const targetElement = $(`#createHistoryView${elementID}`).find('.card-body').find('.card-table_insertion');
            targetElement.empty();
            targetElement.append(tableHTML);
            $(`#createhistory_datatable_${firstKey}_${elementID}`)
            .find('tbody tr')
            .each(function() {
              const firstCell = $(this).find('td:first-child');
              const linkContent = `<a data-toggle="tooltip" data-template="${template}" onclick="addTransactionToForm.call(this)" data-element-id="${elementID}" data-verboselist='${JSON.stringify(verboseList)}' class="create_history_edit" data-table-name='${firstKey}' title="Edit record" value="update"><i name="actions" value="Edit" class="fa fa-edit ihover javaSC thin-icon" style="font-size:15px"></i></a>`;
              firstCell.html(linkContent);
              $(this).find('td').each(function() {
                const cellContent = $(this).html();
                if (cellContent.startsWith('<') && !cellContent.toLowerCase().startsWith('<a')) {
                  const buttonContent = viewrtfcb_mode === 'True'
                    ? `<button class="view_data_btn" style="background-color: transparent; border: transparent;" onclick="showRTFDataCreateView.call(this)" data-data="${cellContent.replace(/"/g, '&quot;')}">View Data</button>`
                    : cellContent;
                  $(this).html(buttonContent);
                }
              });

            });
            if (Object.keys(commentList).length > 0) {
              for (const tab in commentList) {
                if (commentList[tab].length > 0) {
                  for (let i = 0; i < commentList[tab].length; i++) {
                    $(`#createhistory_datatable_${tab}_${elementID}`).find('tbody').find('tr').eq(i).find('td').eq(-1).html(`<p style='word-break: break-all;white-space: pre-wrap;'>${commentList[tab][i]}</p>`)
                  }
                }
              }
            }
            $(`#createhistory_datatable_${firstKey}_${elementID}`).find("tbody").find("td").addClass("view_details_wrap");
            var fieldArray = [];
            for (let [k, v] of Object.entries(verboseList[firstKey])) {
              $(`#createhistory_datatable_${firstKey}_${elementID} > thead > tr > th`).each(function(){
                if ($(this).text().trim() == k.trim()) {
                  fieldArray.push(v);
                }
              });
            }
            fieldArray.push("Rejected By");
            fieldArray.push("Comment");
            if (Object.keys(columnAlignment).length) {
              let globalHeader = columnAlignment.global_header;
              let globalContent = columnAlignment.global_content;
              if (columnAlignment.field_level_config) {
                columnAlignmentDef = [];
                for (index in columnsToDisplay_Rejected) {
                  var fieldName = columnsToDisplay_Rejected[index];
                  if (columnAlignment.field_level_config[fieldName]) {
                    var header = columnAlignment.field_level_config[fieldName].header;
                    var content = columnAlignment.field_level_config[fieldName].content;
                    columnAlignmentDef.push(
                      {
                        targets: [Number(index)],
                        className: `dt-head-${header} dt-body-${content} allColumnClass all`,
                      }
                    )
                  } else {
                    columnAlignmentDef.push(
                      {
                        targets: [Number(index)],
                        className: `dt-head-${globalHeader} dt-body-${globalContent} allColumnClass all`,
                      }
                    )
                  }
                }
              }
            }
            columnAlignmentDef.push(
              {
                targets: ['_all'],
                className: `dt-center allColumnClass all`,
              }
            )

            $(`#createhistory_datatable_${firstKey}_${elementID}`).DataTable({
              autoWidth: true,
              scrollY: '200vh',
              scrollX: true,
              scrollCollapse: true,
              sScrollXInner: '100%',
              bInfo: false,
              bRetrieve: true,
              bProcessing: true,
              bDestroy: true,
              ordering: true,
              orderCellsTop: true,
              responsive: true,

              colReorder: {
                fixedColumnsLeft: 1,
              },
              deferRender: true,
              paging: true,
              lengthMenu: [
                [1, 5, 50, -1],
                [1, 5, 50, 'All'],
              ],
              pageLength: 50,
              dom: 'lfBrtip',
              buttons: [],
              columnDefs: columnAlignmentDef,
            }).columns.adjust()
            $(`#createHistoryView${elementID}`).css('display', 'block');
            targetElement.css('display', 'block');
          }
        }
    },
    error: function () {
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    },
  })
}
function showFieldInfo(obj){
  const elementId = $(obj).attr('data-id')
  var dataList = $(obj).attr('data-col')
  var text = $(obj).parent().find('input, select, textarea').val()
  var extractedValues =JSON.parse(dataList)
  var masterColumn = extractedValues['column']
  var linkedTable = extractedValues['linkedTable']
  var linkedColumn = extractedValues['linkedTableColumn']
  var addlinkedColumn = JSON.stringify(extractedValues['linkedAddColumns'])
  $.ajax({
    url:`/users/${urlPath}/dynamicVal/`,
    data: {
    "operation":"hyperLinkingTables",
    "value":text,
    "masterColumn":masterColumn,
    "linkedTable":linkedTable,
    "linkedColumn":linkedColumn,
    "addlinkedColumn":addlinkedColumn,
    },
    type: "POST",
    dataType: "json",
    success: function (data) {
      if (data['data'].length != 0){
        $(`#show_info_header${elementId}`).empty()
        $(`#show_info_header${elementId}`).append(`<h5 class="modal-title">${linkedTable}</h5>
        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>`)
        var data = data['data']
        $(`#show_info_body${elementId}`).empty();
        $(`#show_info_body${elementId}`).append(
            `
            <table id="exampledata${elementId}">
                <thead>
                    <tr>
                    </tr>
                </thead>
                <tbody>
                </tbody>
            </table>
            `
        )
        for (var i = 0; i < data.length; i++) {
          string=`<tr>`
          for(let [key,value] of Object.entries(data[i]) ){
            string+=`<td>${value}</td>`
          }
          string+=`</tr>`
          $(`#exampledata${elementId}`).find('tbody').append(string)
        }
        for(let [key,value] of Object.entries(data[0]) ){
            $(`#exampledata${elementId}`).find('thead tr').eq(0).append(`<th>${key}</th>`)
        }
        $(`#show_info_${elementId}`).modal('show')
        $(`#exampledata${elementId}`).DataTable();
      }else{
        Swal.fire({icon: 'error',text: 'No Records found!'});
      }
    },
    failure: function () {
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    },
  })

}
function formatState (state) {
  if (!state.id) {
    return state.text;
  }
  var $state = $(
    "<span onclick='showFieldPopup(this)' ><span></span></span>"
  );

  // Use .text() instead of HTML string concatenation to avoid script injection issues
  $state.find("span").text(state.text);

  return $state;
};
function showFieldPopup(obj){
  const elementId = $(obj).parent().parent().parent().parent().parent().parent().find('select').attr('data-id')
  var dataList = $(obj).parent().parent().parent().parent().parent().parent().find('select').attr('data-table')
  var text = $(obj).text()
  var extractedValues =JSON.parse(dataList)
  var masterColumn = $(obj).parent().parent().parent().parent().parent().parent().find('select').attr('data-master')
  var linkedTable = extractedValues['linkedTable']
  var linkedColumn = extractedValues['linkedColumn']
  var addlinkedColumn = JSON.stringify(extractedValues['linkedAddColumns'])
  $.ajax({
    url:`/users/${urlPath}/dynamicVal/`,
    data: {
    "operation":"hyperLinkingTables",
    "value":text,
    "masterColumn":masterColumn,
    "linkedTable":linkedTable,
    "linkedColumn":linkedColumn,
    "addlinkedColumn":addlinkedColumn,
    },
    type: "POST",
    dataType: "json",
    success: function (data) {
      if (data['data'].length != 0){
        $(`#show_info_header${elementId}`).empty()
        $(`#show_info_header${elementId}`).append(`<h5 class="modal-title">${linkedTable}</h5>
        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>`)
        var data = data['data']
        $(`#show_info_body${elementId}`).empty();
        $(`#show_info_body${elementId}`).append(
            `
            <table id="exampledata${elementId}">
                <thead>
                    <tr>
                    </tr>
                </thead>
                <tbody>
                </tbody>
            </table>
            `
        )
        for (var i = 0; i < data.length; i++) {
          string=`<tr>`
          for(let [key,value] of Object.entries(data[i]) ){
            string+=`<td>${value}</td>`
          }
          string+=`</tr>`
          $(`#exampledata${elementId}`).find('tbody').append(string)
        }
        for(let [key,value] of Object.entries(data[0]) ){
            $(`#exampledata${elementId}`).find('thead tr').eq(0).append(`<th>${key}</th>`)
        }
        $(`#show_info_${elementId}`).modal('show')
        $(`#exampledata${elementId}`).DataTable();
      }else{
        Swal.fire({icon: 'error',text: 'No Records found!'});
      }
      $(obj).parent().parent().parent().parent().parent().parent().find('select').select2('close');
    },
    failure: function () {
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    },
  })

}
function concatenationField(event){
  var singleField = event.data
  var singleCardColumns = $(singleField).attr('data-concatfield')
  var singleCardDivider = $(singleField).attr('data-divider')
  var parsedSingleCardColumns = JSON.parse(singleCardColumns)
  var elementId = $(singleField).attr('data-id')
  var val = ``
    for (let p in parsedSingleCardColumns){
      if ($('#id_' + parsedSingleCardColumns[p] + '_' + elementId).val() == '' ){
        allOkFlag = 0
        break
      }else{
        allOkFlag = 1
        val += `${$('#id_' + parsedSingleCardColumns[p] + '_' + elementId).val()}${singleCardDivider}`
      }
    }
    if (allOkFlag == 1){
      $(singleField).val(val.slice(0, -1)).trigger('change')
    }
  }


for (let i = 0; i < createViewIdList.length; i++) {
  var conCatfields = $(`#${createViewIdList[i]}_tab_content`).find(
    '[data-concatfield]'
  )
  if (conCatfields.length > 0){
    for (let k = 0; k < conCatfields.length; k++){
      var singleField = $(conCatfields).eq(k)
      var singleCardColumns = $(singleField).attr('data-concatfield')
      var singleCardDivider = $(singleField).attr('data-divider')
      var parsedSingleCardColumns = JSON.parse(singleCardColumns)
      var allOkFlag = 1
      for (let p in parsedSingleCardColumns){
        $('#id_' + parsedSingleCardColumns[p] + '_' + createViewIdList[i]).change(singleField,concatenationField)
      }
    }
  }


}
function flowUICreator(elementsArray,container,element_id,data,configs) {
  var count = 0
  for (let k in elementsArray){
    if (elementsArray[k]['group'] =='nodes'){
      if (elementsArray[k]['data']['id'] in configs){
        elementsArray[k]['data']['text'] = configs[elementsArray[k]['data']['id']]
      }
      count ++
    }
  }
  if (count >= 5){
    container.css('height','20rem');
  }
  if (configs['shapes_options_text'] =='inside'){
    var styles = {
      'shape': configs['shapes_options'],
      'label': 'data(text)',
      'text-valign': 'center',
      'font-size': configs['font-size'],
      'color':configs['font-color'],
      'width': configs['shape_width'],
      'height': configs['shape_height'],
      'text-wrap': 'wrap',
      'text-max-width': `${String(configs['shape_width'])}px`,
    }
  }else{
    var styles = {
      'shape': configs['shapes_options'],
      'label': 'data(text)',
      'font-size': configs['font-size'],
      'color':configs['font-color'],
      'width': configs['shape_width'],
      'height': configs['shape_height'],
      'text-wrap': 'wrap',
      'text-max-width': `${String(configs['shape_width'])}px`,
    }
  }
  var cy = cytoscape({
    container: container,
    zoomingEnabled: false,
    userZoomingEnabled: false,
    elements: elementsArray,
    style: [
      {
        selector: 'node',
        style: styles,
      },
      {
        selector: 'edge',
        style: {
          width: 1
        }
      }
    ],
    layout: {
      name: "dagre",
      rankDir: "LR",
      padding: 10,
      spacingFactor: 1.25,
      fit: true,
      nodeDimensionsIncludeLabels: true,
      avoidOverlap: true,
      pan: { x: 200, y: 100 }
    }
  });
  if (data != undefined){
    cy.nodes().forEach(function(ele, i, eles){
       for (let k in data){
        if (data[k]['element_id'] == ele.id()){
          if (data[k]['current_status'] == 'Pass'){
            ele.css('background-color','#4bb543')
          }
        }
       }
     });
  }else{
    flag = true
    cy.nodes().forEach(function(ele, i, eles){
      if(flag){
        ele.css('background-color','#4bb543')
      }
      if (element_id == ele.id()){
        flag = false
      }
    });
  }
}
function processDesignDiv_createview(obj){
  var eleId = $(obj).attr('data-id')
  $(obj).parent().parent().find('.processflowdiv').toggleClass("displaynone")

  if ($(obj).parent().parent().find('.processflowdiv').hasClass("displaynone") === false){
    $(obj).prev().find('.stepper-wrapper').empty()
    if ($(obj).attr('data-trans')!= undefined){
      if ($(obj).attr('data-trans')!=''){
        var trans_code = $(obj).attr('data-trans')
        var flag = true
        if (trans_code.startsWith("[")){
          trans_code = JSON.parse(trans_code)
          trans_code = trans_code[0]
          flag = true
        }else if (trans_code == "NULL") {
          trans_code = ''
          flag = false
        }
        if (flag){
          $.ajax({
            url:`/users/${urlPath}/dynamicVal/`,
            data: {
            "operation":"fetch_process_flow_model_trans",
            'trans_code':trans_code,
            },
            type: "POST",
            dataType: "json",
            success: function (data) {
             flowUICreator(data.data,$(obj).closest('.modal-body').find('.processflowdiv'),eleId,data.flow,JSON.parse($(obj).attr('data-list')))
            },
            failure: function () {
              Swal.fire({icon: 'error',text: 'Error! Please try again.'});
            },
          })
        }

      }
    }else{
      $.ajax({
        url:`/users/${urlPath}/dynamicVal/`,
        data: {
        "operation":"fetch_process_flow_model_xml",
        'sub_pr_code':$(obj).attr('data-sub-process'),
        'pr_code':$(obj).attr('data-process'),
        },
        type: "POST",
        dataType: "json",
        success: function (data) {
          flowUICreator(data.elements_list,$(obj).closest('.card-body').find('.processflowdiv'),eleId,undefined,JSON.parse($(obj).attr('data-list')))
        },
        failure: function () {
          Swal.fire({icon: 'error',text: 'Error! Please try again.'});
        },
      })
    }

  }

  $(obj).toggleClass("rotate")
}
function boolean_slider_onchange(obj,id,slide,bgColor_notSelected,bgColor_Selected){
  if (slide == 'yes'){
    $(id).prop('checked',true)
    $(obj).next().css('color',bgColor_Selected)
    $(obj).closest('.radioGroup').find('.no_bool').next().css('color',`${bgColor_notSelected}`)
  }else{
    $(id).prop('checked',false)
    $(obj).next().css('color',bgColor_Selected)
    $(obj).closest('.radioGroup').find('.yes_bool').next().css('color',`${bgColor_notSelected}`)
  }
}
function charfield_field_type_settings_onchange(obj,id,val,bg_selcted,not_bg_selected){
  $(`#${id}`).val(val).trigger('change')
  $(obj).closest('.charfield_field_type_settings').find('label').css('color',`${not_bg_selected}`)
  $(obj).next().css('color',`${bg_selcted}`)
}
