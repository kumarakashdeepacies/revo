/* eslint-disable no-mixed-spaces-and-tabs */
/* eslint-disable no-tabs */
/* eslint-disable comma-dangle */
/* eslint camelcase: ["error", {ignoreGlobals: true,"properties": "never"}] */
/* eslint no-new:"off" */
// eslint-disable-next-line no-unused-vars,no-redeclare
/* global event,mastertableflow,masterColumnflow,names,updateParent,listConstraintID,additionalCol,selectedFields,html4,htmlflow,htmlusers,index,alert_base_table_raw_data,FormData,Option,listflowcolumnname,listflowcolumn,htmlmodeldef,listViewEditTemplate,dataSent,len,listViewTableDict,elementTableIDList,mColBasefilter,item_code_list */
if (
  String($('form').find("input[name='csrfmiddlewaretoken']").attr('value')) !==
	'undefined'
) {
  const ctoken = $('form')
    .find("input[name='csrfmiddlewaretoken']")
    .attr('value')
  if (String(ctoken) !== 'undefined') {
    $.ajaxSetup({
      // eslint-disable-next-line no-unused-vars
      beforeSend: function (xhr, settings) {
        xhr.setRequestHeader('X-CSRFToken', ctoken)
      },
    })
  }
}

var mentions_user_list = []
var modify_column = {}
var edited_data = {}
var parsed_json_data = []
var transaction_data_to_edit = {}
var result_data = {}
var all_users_list = {}
var freeze_comments_option = false
var search_in_comments_cols, display_in_comments_cols;
var all_comments_resolved = false
var all_comments_reopened = false
var resolved_ind_comments_list = []
var resolve_all_comments,reopen_all_comments,resolve_individual_comments,reopen_individual_comments;
var allowed_rejection,allowed_approval,allowed_edit,allowed_resend,allowed_delegate;

/* eslint-disable no-var,init-declarations */
var originalVerboseColumnNames
var elementIDData
var elementID
var primaryKeyId
var tableName
var datatableDict = {}
var fDict2 = {}
var cellIndex
var cellColLen
var formatConfigD1 = {}
let historyViewTemplate
const saveState = {}
let saveListview;
/* eslint-enable no-var */

// eslint-disable-next-line no-unused-vars
function masterBaseDataFilter(elementTableIDList,elementPage) {

  $.ajax({
    url: `/users/${urlPath}/processGraphModule/`,
    data: {
      operation: 'readListview',
      element_id: elementTableIDList[0],
    },
    type: 'POST',
    dataType: 'json',
    success: function (data) {
      const data1 = JSON.parse(data.data[0])

      saveListview = data1
      if (String(document.getElementById('form1')) !== 'undefined') {
        const ctoken = $('form')
          .find("input[name='csrfmiddlewaretoken']")
          .attr('value')
        $.ajaxSetup({
          // eslint-disable-next-line no-unused-vars
          beforeSend: function (xhr, settings) {
            xhr.setRequestHeader('X-CSRFToken', ctoken)
          },
        })
      }
      $('a[data-toggle="tab"]').on('shown.bs.tab', function () {
        $($.fn.dataTable.tables(true)).DataTable().columns.adjust()
      })

      for (const i in elementTableIDList) {
        var listViewElementId = elementTableIDList[i];
        listViewRenderHandler(listViewElementId, elementTableIDList.indexOf(listViewElementId), elementPage);
      }

      $('.table').on('click', '.remove_filter', function () {
        const whichtr = $(this).closest('tr')
        whichtr.remove()
      })

      // eslint-disable-next-line no-unused-vars
      function funn(elementID) {
        $(`#masterListTablei${elementTabID}`).DataTable({
          autoWidth: true,
          scrollY: '100%',
          scrollCollapse: true,
          scrollX: '110%',
          // "serverSide":true,
          orderCellsTop: true,
          // fixedHeader: true,
          responsive: true,
          colReorder: {
            fixedColumnsLeft: 1,
          },
          // stateSave: true,
          deferRender: true,
          paging: true,
          lengthMenu: [
            [1, 5, 50, -1],
            [1, 5, 50, 'All'],
          ],
          stripeClasses: false,
          pageLength: 50,
          dom: 'lfBrtip',
          sScrollX: '100%',
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
      }
    },
    error: function () {
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    },
  })
}


function listViewRenderHandler(elementTabID, i, elementPage) {
  var pagination = elementPage[i];
  var paginationInt = [];
  isAll = false;
  for(let i in pagination){
    if(pagination[i] == 'All'){
      paginationInt.push(-1);
      isAll = true;
    } else {
      paginationInt.push(parseInt(pagination[i]));
    }
  }
  paginationInt.sort(function(a, b){return a - b});
  if(isAll){
    paginationInt.shift()
    paginationInt.push(-1);
    pagination = [...paginationInt];
    pagination[pagination.length - 1] = 'All'
  } else {
    pagination = paginationInt;
  }
  var table // eslint-disable-line no-var
  saveState[elementTabID] = 0
  originalVerboseColumnNames = Array.from(
    listViewTableDict[elementTabID].original_verbose_column_names
  )
  var renamed_columns_names = listViewTableDict[elementTabID].renamed_columns_list
    var dataContainingColumnNames = Array.from(
    listViewTableDict[elementTabID].dataContainingColumnNames
  )
  const allowEditColAlign = listViewTableDict[elementTabID].allowEditColAlign
  let allowEditColConfig = listViewTableDict[elementTabID].allowEditColConfig
  let restcol = listViewTableDict[elementTabID].rest_cols

  var list_table_header_config = listViewTableDict[elementTabID].list_table_header_config
    function getHeader(arr,obj){
  let header=[]
  let subheader = []
  for (let item in obj){
  header.push(item)
  }
  for(let i=0;i<header.length;i++){
  for(let j=0;j<obj[header[i]].length;j++){
  subheader.push(obj[header[i]][j])
  }
  }
  let finalObj={}
  for(let i=0;i<arr.length;i++){
  finalObj[arr[i].data]=arr[i].data
  }
  let tableData={}
  for(let item in finalObj){
  for(let  key in obj){
  if(obj[key].includes(item)){
  tableData[key]=obj[key]
  }
  else{
  tableData[item]=[finalObj[item]]
  }
  }
  }

  for(let i=0;i<subheader.length;i++){
  let cond = tableData.hasOwnProperty(subheader[i])
  if(cond){
  delete tableData[subheader[i]]
  }
  }
  return tableData
  }
  list_table_header_config = getHeader(dataContainingColumnNames,list_table_header_config)

  let tableModelName = listViewTableDict[elementTabID].model_name


  $(`#example1${elementTabID}`).find('thead tr').empty()
  const thead = $(`#example1${elementTabID}`).find('thead tr')
  $( "<tr class='table-header'></tr>" ).insertBefore( thead );
  const thead1 = $(`#example1${elementTabID}`).find('thead tr.table-header')
  const tfoot = $(`#example1${elementTabID}`).find('tfoot tr')



  let allCol_width_def = [
    {
      // eslint-disable-next-line no-unused-vars
      render: function (data, type, full, meta) {
        if ($(`#${meta.settings.sInstance}`).hasClass('card-view-template')){
          if (typeof data === 'string' || data instanceof String) {
            if (data.includes('<td>')) {
              return data
            } else {
              return (
                "<div>" +
                data +
                '</div>'
              )
            }
          } else {
            return data
          }
        }else{
          if (typeof data === 'string' || data instanceof String) {
            if (data.includes('<td>')) {
              return data
            } else {
              return (
                "<div style='white-space: normal;width: 100%;'>" +
                data +
                '</div>'
              )
            }
          } else {
            return data
          }
        }

      },

    },
    {
      targets: 0,
      width: '20%',
      className: 'noVis dt-center',
    },
  ]
  if ($(`#group_by_switch_user_configuration_${elementTabID}`).length>0){
    if ($(`#group_by_switch_user_configuration_${elementTabID}`).attr('data-list2') != 'None' && $(`#group_by_switch_user_configuration_${elementTabID}`).attr('data-list2') != '' ){
      var user_config = JSON.parse($(`#group_by_switch_user_configuration_${elementTabID}`).attr('data-list2'))
      dataContainingColumnNames = []
      for (let b in user_config['levels']){
        dataContainingColumnNames.push({'data':user_config['levels'][b]})
      }
      for (let b in user_config['selected_columns']){
        dataContainingColumnNames.push({'data':user_config['selected_columns'][b]})
      }
    }
  }
  if(Object.keys(list_table_header_config).length === 0){
        if ($(`#example1${elementTabID}`).attr('data-list-group-by') == 'data-list-group-by' ||$(`#example1${elementTabID}`).attr('data-list-group-by1') == 'data-list-group-by'){
            dataContainingColumnNames.unshift({
        title: '',
        className: 'treegrid-control  dt-center allColumnClass all',
        data: function (item) {
          if (item.children) {
            return '<i class="fa-solid fa-plus ihover javaSC"></i>';
          }
          return '';
        }
      })
            for (let i = 0; i < dataContainingColumnNames.length; i++) {
        if (dataContainingColumnNames[i].data in renamed_columns_names){
                    $(`<th orginal-name="${dataContainingColumnNames[i].data}">${renamed_columns_names[dataContainingColumnNames[i].data]}</th>`).appendTo(thead)
          $(`<th orginal-name="${dataContainingColumnNames[i].data}">${renamed_columns_names[dataContainingColumnNames[i].data]}</th>`).appendTo(tfoot)
        }else{
                    $(`<th orginal-name="${dataContainingColumnNames[i].data}">${dataContainingColumnNames[i].data}</th>`).appendTo(thead)
          $(`<th orginal-name="${dataContainingColumnNames[i].data}">${dataContainingColumnNames[i].data}</th>`).appendTo(tfoot)
        }
      }
    }
    else{
      if(allowEditColAlign && allowEditColConfig.length > 0){
        for (let i = 0; i < dataContainingColumnNames.length; i++) {
          if (dataContainingColumnNames[i].data in renamed_columns_names){
                        $(`<th class="${dataContainingColumnNames[i].data}" orginal-name="${dataContainingColumnNames[i].data}">${renamed_columns_names[dataContainingColumnNames[i].data]}</th>`).appendTo(thead)
            $(`<th class="${dataContainingColumnNames[i].data}" orginal-name="${dataContainingColumnNames[i].data}">${renamed_columns_names[dataContainingColumnNames[i].data]}</th>`).appendTo(tfoot)
          }else{
            $(`<th class="${dataContainingColumnNames[i].data}" orginal-name="${dataContainingColumnNames[i].data}">${dataContainingColumnNames[i].data}</th>`).appendTo(thead)
            $(`<th class="${dataContainingColumnNames[i].data}" orginal-name="${dataContainingColumnNames[i].data}">${dataContainingColumnNames[i].data}</th>`).appendTo(tfoot)
          }
        }

        for(let ii=0;ii<allowEditColConfig.length;ii++){
          allCol_width_def.push({
            targets: allowEditColConfig[ii]["target"],
            className: allowEditColConfig[ii]["body"],
          })
          allCol_width_def.push({
            targets: allowEditColConfig[ii]["target"],
            className: allowEditColConfig[ii]["header"],
          })
        }

        allCol_width_def.push({
          targets: restcol,
          className: 'dt-center',
        })

        allCol_width_def.push({
          targets: "_all",
          className: 'allColumnClass all',
        })

      }else{
        for (let i = 0; i < dataContainingColumnNames.length; i++) {
          if (dataContainingColumnNames[i].data in renamed_columns_names){
                        $(`<th orginal-name="${dataContainingColumnNames[i].data}">${renamed_columns_names[dataContainingColumnNames[i].data]}</th>`).appendTo(thead)
            $(`<th orginal-name="${dataContainingColumnNames[i].data}">${renamed_columns_names[dataContainingColumnNames[i].data]}</th>`).appendTo(tfoot)
          }else{
                        $(`<th orginal-name="${dataContainingColumnNames[i].data}">${dataContainingColumnNames[i].data}</th>`).appendTo(thead)
            $(`<th orginal-name="${dataContainingColumnNames[i].data}">${dataContainingColumnNames[i].data}</th>`).appendTo(tfoot)
          }
        }
        allCol_width_def.push({
          targets: "_all",
          className: 'dt-center allColumnClass all',
        })
      }
    }
  }
  else{



    for(let item in list_table_header_config){
      if(list_table_header_config[item].length==1){
        if (list_table_header_config[item][0] in renamed_columns_names){
          list_table_header_config[item][0] = renamed_columns_names[list_table_header_config[item][0]]
        }

        $(`<th rowspan="2">${list_table_header_config[item][0]}</th>`).appendTo(thead1)
      }
      else{
          $(`<th  colspan="${list_table_header_config[item].length}" style="border-right:1px solid rgba(0, 0, 0, 0.15);border-left:1px solid rgba(0, 0, 0, 0.15);text-align:center">${item}</th>`).appendTo(thead1)

        for(let j=0;j<list_table_header_config[item].length;j++){
          if (list_table_header_config[item][j] in renamed_columns_names){
            list_table_header_config[item][j] = renamed_columns_names[list_table_header_config[item][0]]
          }

          $(`<th>${list_table_header_config[item][j]}</th>`).appendTo(thead)

        }
      }
    }
    for (let i = 0; i < dataContainingColumnNames.length; i++) {
      $(`<th>${dataContainingColumnNames[i].data}</th>`).appendTo(tfoot)
            }
          allCol_width_def.push({
      targets: restcol,
      className: 'dt-center',
    })
    allCol_width_def.push({
      targets: "_all",
      className: 'allColumnClass all',
    })

  }


  var buttonTitleRow = $(`#title_row_formatting_${elementTabID}`)
  if (buttonTitleRow.length > 0){
    var attrData = $(buttonTitleRow).attr('data-list')
      if (attrData == ''|| attrData =='{}'){

      }else {
        var parsedAttrdata = JSON.parse(attrData)
        var font1 = parsedAttrdata['main']['font']
        var fontSize = parsedAttrdata['main']['fontSize']
        if (font1 && fontSize) {
          var fontIndex = font1.indexOf('_')
          var font2 = font1.slice(0, fontIndex)
          var font3 = font1.slice(fontIndex+1)
          $(thead).parent().css('font-size',fontSize);
          $(thead).parent().css('font-family',`${font2} , ${font3}`)
          $(thead).find('th').each(function(){
            if (Object.keys(parsedAttrdata['exception']).length === 0){
              $(this).css({'color':parsedAttrdata['main']['textColor'],'background-color':parsedAttrdata['main']['bgColor']})
            }else {
              $(this).css({'color':parsedAttrdata['main']['textColor'],'background-color':parsedAttrdata['main']['bgColor']})
              for (let i in parsedAttrdata['exception']){
                if ($(this).html() == i){
                  $(this).css({'color':parsedAttrdata['exception'][i]['textColor'],'background-color':parsedAttrdata['exception'][i]['bgColor']})
                }
              }
            }
          })
        }
      }
  }
  var columnsHiddenTitleRow = $(`#column_hidden_config_${elementTabID}`)
  if (columnsHiddenTitleRow.length > 0){
    var attrData = $(columnsHiddenTitleRow).attr('data-list')
      if (attrData == ''|| attrData =='{}'){
      }else {
        var parsedAttrdata = JSON.parse(attrData)
        for (let l in parsedAttrdata){
          $(thead).find('th').each(function(){
          if ($(this).html() == parsedAttrdata[l]){
            $(this).css('color','rgba(0,0,0,0)')
          }
          })
        }

      }
  }

  tableModelName = listViewTableDict[elementTabID].model_name
  var drop_down_button =  $(`#drop_down_button_grouping${elementTabID}`)
  if (drop_down_button.length > 0){
    var attrData = JSON.parse(drop_down_button.attr('data-list'))
    for (let j in attrData['dropDown']){
      if ($(`#${attrData['dropDown'][j]}${elementTabID}`).length > 0){
        var cloneHtml = $(`#${attrData['dropDown'][j]}${elementTabID}`).html()
        $(`#${attrData['dropDown'][j]}${elementTabID}`).css('display','none')
        drop_down_button.parent().parent().find('.sortable-order').append(`<button class="btn btn-sm btn-primary col-9" onclick="buttonGroupingCall('#${attrData['dropDown'][j]}${elementTabID}')">${cloneHtml}</button>`)
      }
    }
  }
  $(`#example1${elementTabID} thead tr`).eq(0).find("th").eq(0).css(
    'cursor',
    'default',
    'tfoot'
  )
  $(`#example1${elementTabID} thead tr`).eq(0).find("th").eq(0).css(
    'background-image',
    'none'
  )
  $(`#example1${elementTabID} tfoot tr`).eq(0).find("th").eq(0).css(
    'cursor',
    'default',
    'tfoot'
  )
  $(`#example1${elementTabID} tfoot tr`).eq(0).find("th").eq(0).css(
    'background-image',
    'none'
  )
  temp_type = $(`#${elementTabID}_tab_content`).attr("data-template-type")
  if(temp_type == 'Multi Dropdown View'){
    view_name = $(`#tableTab${elementTabID}`).find("select").val()
  }
  function call() {
    if(temp_type == "Multi Dropdown View"){
      return (
        `/users/${urlPath}/get_datatable_data/` + elementTabID + '/' + tableModelName + '/'+ view_name + '/'
      )
    }else{
      return (
        `/users/${urlPath}/get_datatable_data/` + elementTabID + '/' + tableModelName + '/' + "viewname" + '/'
      )
    }
  }
  function quickFilters(element){
    var mainDiv =  $(`#quickFiltersDiv${element.replace("example1","")}`)
    if (mainDiv.length>0){
      var filters = mainDiv.children()
      var filterPrams ={}
      for (let i = 0; i < filters.length; i++){
        var filterVals = {}
        if ($(filters).eq(i).attr('data-div') =='select_field'){
          filterVals[$(filters).eq(i).find('select').attr('data-column')] =$(filters).eq(i).find('select').attr('data-val')
        }else if ($(filters).eq(i).attr('data-div') =='multi_select'){
          filterVals[$(filters).eq(i).find('select').attr('data-column')] =$(filters).eq(i).find('select').val()
        }
        else if ($(filters).eq(i).attr('data-div') =='DateField'){
          filterVals[$(filters).eq(i).find('.dtrangepicker').attr('data-column')] =$(filters).eq(i).find('.dtrangepicker').attr('data-val')
        }else if ($(filters).eq(i).attr('data-div') =='TimeField'){
          if ($(filters).eq(i).attr('data-sec') == 'true'){
            filterVals[$(filters).eq(i).find('.ttrangepicker').attr('data-column')] =$(filters).eq(i).find('.ttrangepicker').attr('data-val')
          }else{
            filterVals[$(filters).eq(i).find('.ttrangepicker_sec').attr('data-column')] =$(filters).eq(i).find('.ttrangepicker_sec').attr('data-val')
          }
        }else if ($(filters).eq(i).attr('data-div') =='DateTimeRangeField'){
          filterVals[$(filters).eq(i).find('.dttrangepicker').attr('data-column')] =$(filters).eq(i).find('.dttrangepicker').attr('data-val')
        }else if ($(filters).eq(i).attr('data-div') =='DateRangeField'){
          filterVals[$(filters).eq(i).find('.dtrangepicker').attr('data-column')] =$(filters).eq(i).find('.dtrangepicker').attr('data-val')
        }else if ($(filters).eq(i).attr('data-div') =='DateTimeField'){
          if ($(filters).eq(i).attr('data-sec') == 'true'){
            filterVals[$(filters).eq(i).find('.dttrangepicker').attr('data-column')] =$(filters).eq(i).find('.dttrangepicker').attr('data-val')
          }else{
            filterVals[$(filters).eq(i).find('.dttrangepicker_sec').attr('data-column')] =$(filters).eq(i).find('.dttrangepicker_sec').attr('data-val')
          }
        }else if ($(filters).eq(i).attr('data-div') =='TimeRangeField'){
          filterVals[$(filters).eq(i).find('.ttrangepicker').attr('data-column')] =$(filters).eq(i).find('.ttrangepicker').attr('data-val')
        }
        else if ($(filters).eq(i).attr('data-div') =='range_field'){
          filterVals[$(filters).eq(i).find('.js-range-slider').attr('data-column')] =$(filters).eq(i).find('.js-range-slider').attr('data-val')
        }else if ($(filters).eq(i).attr('data-div') =='booleanField'){
          filterVals[$(filters).eq(i).find('.radioGroup').attr('data-column')] = $(filters).eq(i).find('.radioGroup').attr('data-val')
        }

        if ($(filters).eq(i).attr('data-div') in filterPrams){
          Object.assign(filterPrams[$(filters).eq(i).attr('data-div')] , filterVals)
        }else{
          Object.assign(filterPrams, {[$(filters).eq(i).attr('data-div')]:filterVals})
        }
      }
      if (Object.keys(filterPrams).length > 0){
        return JSON.stringify(filterPrams)
      }else{
        return 'null'
      }
    }else{
      return 'null'
    }

  }
  function reportingParametersExtractor(element) {
    if (["Reporting View", "List View With History", "Approval Template"].includes(templateType)) {
      let reportingParameterContainer =  $(`#tableTab${element.replace("example1","")}`)
      let selectedParameters = {};
      reportingParameterContainer.find('select').each(function() {
        selectedParameters[$(this).attr('data-parameter-name')] = $(this).val();
      });
      return JSON.stringify(selectedParameters)
    } else {
      return null
    }
  }
  var flag_datatable_trigger = true
  if ($(`#example1${elementTabID}`).attr('data-list-group-by') == 'data-list-group-by' || $(`#example1${elementTabID}`).attr('data-list-group-by1') == 'data-list-group-by'){
      $(`#editListView${elementTabID}`).css('display','none');
      table = $(`#example1${elementTabID}`)
      .DataTable({
        autoWidth: true,
        scrollY: '50vh',
        scrollCollapse: true,
        scrollX: '110%',
        serverSide: true,
        orderCellsTop: true,
        pageLength: paginationInt[parseInt(paginationInt.length/2)],
        responsive: true,
        stateSave: true,
        stateSaveCallback: function (settings, data) {
          const eId = settings.sInstance.split('example1')[1]
          if (saveState[eId]) {
            if (!saveListview) {
              saveListview = {}
            }
            saveListview[settings.sInstance] = data
            saveListview[`example1${eId}`].freeze_dict =
              fDict2[`example1${eId}`]
            $.ajax({
              url: `/users/${urlPath}/processGraphModule/`,
              data: {
                operation: 'saveListview',
                element_id: settings.sInstance.split('example1')[1],
                dict: JSON.stringify(saveListview),
              },
              type: 'POST',
              dataType: 'json',
              // eslint-disable-next-line no-unused-vars
              success: function (data) {
                saveState[eId] = 0
              },
              error: function () {
                Swal.fire({icon: 'error',text: 'Error! Please try again.'});
              },
            })
          }
        },
        stateLoadCallback: function (settings) {
          const eleId = settings.sInstance
          if (saveListview) {
            if (Object.prototype.hasOwnProperty.call(saveListview, eleId)) {
              if (saveListview[eleId].search.search) {
                $('#removeFilter' + eleId).css('display', 'block')
              }
              for (let i = 0; i < saveListview[eleId].columns.length; i++) {
                if (
                  String(saveListview[eleId].columns[i].search.search) !==
                  ''
                ) {
                  $('#removeFilter' + eleId.split('example1')[1]).css(
                    'display',
                    'inline-block'
                  )
                  break;
                } else {
                  $('#removeFilter' + eleId.split('example1')[1]).css(
                    'display',
                    'none'
                  )
                }
              }
              return saveListview[eleId]
            } else {
              return ''
            }
          } else {
            return ''
          }
        },
        stripeClasses: false,
        bLengthChange: false,
        paging: true,
        "info": false,
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
                extend: 'pdfHtml5',
                title: '',
                // pageSize: 'A4',
                // eslint-disable-next-line no-unused-vars
                customize: function (doc, config) {
                  let tableNode
                  for (let i = 0; i < doc.content.length; ++i) {
                    if (String(doc.content[i].table) !== 'undefined') {
                      tableNode = doc.content[i]
                      break;
                    }
                  }

                  const rowIndex = 0
                  const tableColumnCount =
                    tableNode.table.body[rowIndex].length

                  if (tableColumnCount > 5) {
                    doc.pageOrientation = 'landscape'
                  }
                  if (tableColumnCount <= 15) {
                    doc.pageSize = 'A4'
                  }

                  if (tableColumnCount > 15 && tableColumnCount <= 25) {
                    doc.pageSize = 'B3'
                  }

                  if (tableColumnCount > 25 && tableColumnCount <= 40) {
                    doc.pageSize = 'A1'
                  }

                  if (tableColumnCount > 40) {
                    doc.pageSize = 'A0'
                  }
                },
              },
              {
                text: 'XML',
                attr: {
                  id: elementTabID,
                  model_name: tableModelName,
                },
                exportOptions: { columns: ':visible:not(.noVis)' },
                // eslint-disable-next-line no-unused-vars
                action: function (e, dt, type, indexes) {
                  const nodeData = dt.nodes()[0]
                  const tableDataId = $(nodeData).attr('id')
                  $('#' + tableDataId).tableExport({ type: 'xml' })
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
            // eslint-disable-next-line no-unused-vars
            render: function (data, type, full, meta) {
              if ($(`#${meta.settings.sInstance}`).hasClass('card-view-template')){
                if (typeof data === 'string' || data instanceof String) {
                  if (data.includes('<td>')) {
                    return data
                  } else {
                    return (
                      "<div>" +
                      data +
                      '</div>'
                    )
                  }
                } else {
                  return data
                }
              }else{
                if (typeof data === 'string' || data instanceof String) {
                  if (data.includes('<td>')) {
                    return data
                  } else {
                    return (
                      "<div style='white-space: normal;width: 100%;'>" +
                      data +
                      '</div>'
                    )
                  }
                } else {
                  return data
                }
              }

            },
            targets: '_all',

            className: 'dt-center allColumnClass all',
          },
        ],
        "ajax": {
          "url": call(),
          "type": 'POST',
          "data": function(d,settings) {
            d.filters = quickFilters(`${settings.nTable.id}`);
            d.reportingParameters = reportingParametersExtractor(`${settings.nTable.id}`);
            if ($(`#approval-sort-btn-${settings.nTable.id.replace("example1", "")}`).length > 0) {
              d.approvalSort = $(`#approval-sort-btn-${settings.nTable.id.replace("example1", "")}`).attr('data-sort');
            }
            return d;
          },
        },
        columns: dataContainingColumnNames,
        initComplete: function () {
          try {

            const freezeEId = $(this).closest('table').attr('id')

            const table1 = $(`#${freezeEId}`).DataTable()
            $(`#${freezeEId}`).on('click', 'td', function () {
              const columns = table1.settings().init().columns
              cellColLen = columns.length
              cellIndex = table1.cell(this).index().column + 1

              $(this).click(function () {
                $(this).toggleClass('cell_highlighted')
                $(this).toggleClass('cell_selected')
              })
            })

            if (saveListview[`${freezeEId}`].freeze_dict) {
              fDict2[`${freezeEId}`] =
                saveListview[`${freezeEId}`].freeze_dict

              const table = $(`#${freezeEId}`).DataTable()
              new $.fn.dataTable.FixedColumns(
                table, // eslint-disable-line no-new
                saveListview[`${freezeEId}`].freeze_dict
              )

              setTimeout(() => {
                $(`#${freezeEId}`).DataTable().draw()
              }, 3000)
            }
          } catch (err) {}
          this.api()
            .columns()
            .every(function () {
              const column = this
              const title = $(this).text()
              $(
                `<input type="text" data-inputid='inputtext' data-elementid='${elementTabID}' value="" data-input_value="" class="listViewSearch" style="text-align:center;border-bottom:none;border:1px solid #ced4da;border-radius: .35rem;width:10rem;height:2rem"placeholder="Search ` +
                  title +
                  '" />'
              ) // eslint-disable-line no-unused-vars
                .hover(
                  function () {
                    $(this).css('box-shadow', '0 2px 8px 1px rgb(64 60 67 / 24%)');
                    $(this).css('margin-bottom', '0.25rem');
                  },
                  function () {
                    $(this).css('box-shadow', 'none');
                    $(this).css('margin-bottom', 'unset');
                  }
                )
                .appendTo($(column.footer()).empty())
                .on('keyup change', function () {
                  if (
                    column.search() !== this.value ||
                    String(this.value) === ''
                  ) {
                    const val = this.value
                    if (String(this.value) !== '') {
                      column
                        .search(val === null ? '' : val, true, false)
                        .draw()
                    } else if (String(this.value) === '') {
                      column.search(this.value).draw()
                    }
                  }
                })
                if(column.index() == 0){
                  $(column.footer()).empty()
                }
              return true
            })
            var embededTableId = $(this).closest('table').attr('id')
            $(`#${embededTableId}`).find('.listviewembededcomputation').select2()
        },
        "fnDrawCallback": function( oSettings ) {
          var embededTableId = $(this).closest('table').attr('id')
          $(`#${embededTableId}`).find('.listviewembededcomputation').select2()
          table.buttons().container().children().addClass("btn btn-md mx-2 rounded px-2")
          if ($(`#${oSettings.sInstance}`).hasClass('card-view-template')){
            var labels = [];
              $(`#${oSettings.sInstance} thead th`).each(function () {
                labels.push($(this).text());
              });
              var dataList = $(`#${oSettings.sInstance}`).attr('data-list')
              $(`#${oSettings.sInstance}`).find('tbody').find('tr').each(function () {
                $(this)
                  .find("td")
                  .each(function (column) {
                    $("<span class='colHeader'>" + labels[column] + ":</span>").prependTo(
                      $(this)
                    );
                  });
              });
              $(`#${oSettings.sInstance}`).parent().parent().find('.dataTables_scrollHead').css('display','none')
              if (dataList != ""){
                dataList = JSON.parse(dataList)
                $(`#${oSettings.sInstance}`).find('tbody').attr('style',
                `display: grid;
                gap: ${dataList['card-padding']}px;
                grid-template-columns: repeat(${dataList['card-no-one-row']},1fr);
                `)
                $(`#${oSettings.sInstance}`).find('tbody').find('tr').each(function(){
                  $(this).attr('style',
                  `width: ${dataList['card-wdith']}rem;
                  height:${dataList['card-height']}rem;
                  background-color: transparent !important;
                  box-shadow: ${dataList['card-shadow-h-offset']}px ${dataList['card-shadow-v-offset']}px ${dataList['card-shadow-blur']}px ${dataList['card-shadow-spread']}px ${dataList['card-shadow-color-rgba']};
                  overflow:auto;
                  border-radius:${dataList['card-border-radius']}px;
                  border:${dataList['card-border-width']}px ${dataList['card-border-style']} ${dataList['card-border-color-rgba']};
                  `)
                })
                $(`#${oSettings.sInstance}`).find('tbody').find('tr').find('td').each(function(){
                  $(this).attr('style',`
                  display: flex;
                  white-space: normal;
                  border: ${dataList['field-border-width']}px ${dataList['field-border-style']} ${dataList['field-border-color-rgba']};
                  flex-direction:row;
                  justify-content:${dataList['font-alignment']};
                  color:${dataList['font-value-color']};
                  font-size:${dataList['font-value-size']};
                  `)
                  $(this).find('.colHeader').attr('style',`
                  color:${dataList['font-header-color']};
                  font-size:${dataList['font-header-size']};
                  `)
                })
              }
          }

          template_type = $(`#${oSettings.sInstance}`).attr('data-list_type_template')
          if (template_type && template_type == "Approval Template"){
            $(`#${oSettings.sInstance}`).find('tbody').find('tr').find('td').each(function(){
              $(this).parent().find('td').eq(0).find('a[title="Reject record"]').css("pointer-events","none")
              $(this).parent().find('td').eq(0).find('a[title="Approve record"]').css("pointer-events","none")
              $(this).parent().find('td').eq(0).find('a[title="Delegate Approval"]').css("pointer-events","none")
              $(this).parent().find('td').eq(0).find('a[title="Resend record"]').css("pointer-events","none")
              $(this).parent().find('td').eq(0).find('a[title="Edit record"]').css("pointer-events","none")
              $(this).parent().find('td').eq(0).find('a[title="Approval Wall"]').attr("data-approve","false")
              $(this).parent().find('td').eq(0).find('a[title="Approval Wall"]').attr("data-reject","false")
              $(this).parent().find('td').eq(0).find('a[title="Approval Wall"]').attr("data-resend","false")
              $(this).parent().find('td').eq(0).find('a[title="Approval Wall"]').attr("data-edit","false")
              $(this).parent().find('td').eq(0).find('a[title="Approval Wall"]').attr("data-delegate","false")
            })
            $(`#${oSettings.sInstance}`).find('tbody').find('tr').each(function(){
              $(this).parent().find('tr').find('a[title="Approve record"]').css("pointer-events","none")
              $(this).parent().find('tr').find('a[title="Resend record"]').css("pointer-events","none")
              $(this).parent().find('tr').find('a[title="Reject record"]').css("pointer-events","none")
              $(this).parent().find('tr').find('a[title="Delegate Approval"]').css("pointer-events","none")
            })

            tr_index = []
            tr_index_resend = []
            tr_index_edit = []
            oTableData = oSettings.json.data
            var approvalTemplateTableNameField = oSettings.json.table_name_column_verbose_name;
            $(`#${oSettings.sInstance}`).find('tbody > tr > td').find('a[title="Reject record"]').attr('data-approvalTableNameField', approvalTemplateTableNameField);
            $(`#${oSettings.sInstance}`).find('tbody > tr > td').find('a[title="Approve record"]').attr('data-approvalTableNameField', approvalTemplateTableNameField);
            $(`#${oSettings.sInstance}`).find('tbody > tr').find('a[title="Approve record"]').attr('data-approvalTableNameField', approvalTemplateTableNameField);
            $(`#${oSettings.sInstance}`).find('tbody > tr').find('a[title="Reject record"]').attr('data-approvalTableNameField', approvalTemplateTableNameField);
            for(let i=0;i<oTableData.length;i++){
                for (let [k1, v1] of Object.entries(oTableData[i])) {
                  if(oSettings.json.allow_ids.includes(String(v1))){
                    tr_index.push(i)
                  }

                  if(oSettings.json.allow_ids_resend.includes(String(v1))){
                    tr_index_resend.push(i)
                  }

                  if(oSettings.json.allow_ids_edit.includes(String(v1))){
                    tr_index_edit.push(i)
                  }
              }
            }
            for(let i=0;i<tr_index.length;i++){
              $(`#${oSettings.sInstance}`).find('tbody').find('tr').eq(tr_index[i]).find('td').find('a[title="Reject record"]').css("pointer-events","all")
              $(`#${oSettings.sInstance}`).find('tbody').find('tr').eq(tr_index[i]).find('a[title="Reject record"]').css("pointer-events","all")
              $(`#${oSettings.sInstance}`).find('tbody').find('tr').eq(tr_index[i]).find('td').find('a[title="Approve record"]').css("pointer-events","all")
              $(`#${oSettings.sInstance}`).find('tbody').eq(tr_index[i]).find('tr').find('a[title="Approve record"]').css("pointer-events","all")
              $(`#${oSettings.sInstance}`).find('tbody').eq(tr_index[i]).find('tr').find('a[title="Delegate Approval"]').css("pointer-events","all")
              $(`#${oSettings.sInstance}`).find('tbody').find('tr').eq(tr_index[i]).find('td').find('a[title="Delegate Approval"]').css("pointer-events","all")
              $(`#${oSettings.sInstance}`).find('tbody').find('tr').eq(tr_index[i]).find('td').find('a[title="Approval Wall"]').attr("data-approve","true")
              $(`#${oSettings.sInstance}`).find('tbody').find('tr').eq(tr_index[i]).find('td').find('a[title="Approval Wall"]').attr("data-reject","true")
              $(`#${oSettings.sInstance}`).find('tbody').find('tr').eq(tr_index[i]).find('td').find('a[title="Approval Wall"]').attr("data-delegate","true")

              if (oSettings.json.user_additional_info) {
                $(`#${oSettings.sInstance}`).find('tbody').find('tr').eq(tr_index[i]).find('td').find('a[title="Delegate Approval"]').attr('data-user-info', JSON.stringify(oSettings.json.user_additional_info))
                $(`#${oSettings.sInstance}`).find('tbody').find('tr').eq(tr_index[i]).find('td').find('a[title="Delegate Approval"]').attr('data-current-user', oSettings.json.current_user)
                $(`#${oSettings.sInstance}`).find('tbody').find('tr').eq(tr_index[i]).find('td').find('a[title="Delegate Approval"]').attr('data-current-user', oSettings.json.current_user)
                $(`#${oSettings.sInstance}`).find('tbody').eq(tr_index[i]).find('tr').find('a[title="Delegate Approval"]').attr('data-user-info', JSON.stringify(oSettings.json.user_additional_info))
                $(`#${oSettings.sInstance}`).find('tbody').eq(tr_index[i]).find('tr').find('a[title="Delegate Approval"]').attr('data-current-user', oSettings.json.current_user)
                $(`#${oSettings.sInstance}`).find('tbody').eq(tr_index[i]).find('tr').find('a[title="Delegate Approval"]').attr('data-current-user', oSettings.json.current_user)
                $(`#${oSettings.sInstance}`).find('tbody').find('tr').eq(tr_index[i]).find('td').find('a[title="Approval Wall"]').attr('data-current-user', oSettings.json.current_user)
              }
            }

            for(let i=0;i<tr_index_resend.length;i++){
              $(`#${oSettings.sInstance}`).find('tbody').find('tr').eq(tr_index_resend[i]).find('td').find('a[title="Resend record"]').css("pointer-events","all")
              $(`#${oSettings.sInstance}`).find('tbody').eq(tr_index_resend[i]).find('tr').find('a[title="Resend record"]').css("pointer-events","all")
              $(`#${oSettings.sInstance}`).find('tbody').find('tr').eq(tr_index_resend[i]).find('td').find('a[title="Approval Wall"]').attr("data-resend","true")
            }

            for(let i=0;i<tr_index_edit.length;i++){
              $(`#${oSettings.sInstance}`).find('tbody').find('tr').eq(tr_index_edit[i]).find('td').find('a[title="Edit record"]').css("pointer-events","all")
              $(`#${oSettings.sInstance}`).find('tbody').find('tr').eq(tr_index_edit[i]).find('td').find('a[title="Approval Wall"]').attr("data-edit","true")
            }
          }

        },
        'treeGrid': {
          'left': 20,
          'expandIcon': '<i class="fa-solid fa-plus ihover javaSC"></i>',
          'collapseIcon': '<i class="fa-solid fa-minus ihover javaSC"></i>'
      }
      })
      .columns.adjust()
      flag_datatable_trigger = false
  }else{
    flag_datatable_trigger = true
  }
  row_flag = true
  var extract_file_name = $(`#btn_exDataDownload_${elementTabID}`).find("i").attr("id");
  if (!extract_file_name){
    extract_file_name = 'Revolutio'
  }
  if(flag_datatable_trigger){
    table = $(`#example1${elementTabID}`)
    .DataTable({
      autoWidth: true,
      scrollY: '50vh',
      scrollCollapse: true,
      scrollX: '110%',
      serverSide: true,
      orderCellsTop: true,
      colReorder: {
        fixedColumnsLeft: 1,
      },
      responsive: true,
      stateSave: true,
        stateSaveCallback: function (settings, data) {
        const eId = settings.sInstance.split('example1')[1]
        if (saveState[eId]) {
          if (!saveListview) {
            saveListview = {}
          }
          saveListview[settings.sInstance] = data
          saveListview[`example1${eId}`].freeze_dict =
            fDict2[`example1${eId}`]
          $.ajax({
            url: `/users/${urlPath}/processGraphModule/`,
            data: {
              operation: 'saveListview',
              element_id: settings.sInstance.split('example1')[1],
              dict: JSON.stringify(saveListview),
            },
            type: 'POST',
            dataType: 'json',
            // eslint-disable-next-line no-unused-vars
            success: function (data) {
              saveState[eId] = 0
            },
            error: function () {
              Swal.fire({icon: 'error',text: 'Error! Please try again.'});
            },
          })
        }
      },
      stateLoadCallback: function (settings) {
        const eleId = settings.sInstance
        if (saveListview) {
          if (Object.prototype.hasOwnProperty.call(saveListview, eleId)) {
            if (saveListview[eleId].search.search) {
              $('#removeFilter' + eleId).css('display', 'block')
            }
            for (let i = 0; i < saveListview[eleId].columns.length; i++) {
              if (
                String(saveListview[eleId].columns[i].search.search) !==
                ''
              ) {
                $('#removeFilter' + eleId.split('example1')[1]).css(
                  'display',
                  'inline-block'
                )
                break;
              } else {
                $('#removeFilter' + eleId.split('example1')[1]).css(
                  'display',
                  'none'
                )
              }
            }
            return saveListview[eleId]
          } else {
            return ''
          }
        } else {
          return ''
        }
      },
      deferRender: true,
      paging: true,
      bLengthChange: false,
      stripeClasses: false,
      pageLength: paginationInt[parseInt(paginationInt.length/2)],
      dom: 'lfBrtip',
      sScrollX: '100%',
      destroy: false,
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
              filename: extract_file_name,
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
              extend: 'pdfHtml5',
              title: '',
              filename: extract_file_name,
              // pageSize: 'A4',
              // eslint-disable-next-line no-unused-vars
              customize: function (doc, config) {
                let tableNode
                for (let i = 0; i < doc.content.length; ++i) {
                  if (String(doc.content[i].table) !== 'undefined') {
                    tableNode = doc.content[i]
                    break;
                  }
                }

                const rowIndex = 0
                const tableColumnCount =
                  tableNode.table.body[rowIndex].length

                if (tableColumnCount > 5) {
                  doc.pageOrientation = 'landscape'
                }
                if (tableColumnCount <= 15) {
                  doc.pageSize = 'A4'
                }

                if (tableColumnCount > 15 && tableColumnCount <= 25) {
                  doc.pageSize = 'B3'
                }

                if (tableColumnCount > 25 && tableColumnCount <= 40) {
                  doc.pageSize = 'A1'
                }

                if (tableColumnCount > 40) {
                  doc.pageSize = 'A0'
                }
              },
            },
            {
              text: 'XML',
              attr: {
                id: elementTabID,
                model_name: tableModelName,
              },
              exportOptions: { columns: ':visible:not(.noVis)' },
              // eslint-disable-next-line no-unused-vars
              action: function (e, dt, type, indexes) {
                const nodeData = dt.nodes()[0]
                const tableDataId = $(nodeData).attr('id')
                $('#' + tableDataId).tableExport({ type: 'xml' })
              },
            },
          ],
        },
        {
          extend: 'colvis',
          className: 'scroller',
        },
      ],
      columnDefs: allCol_width_def,
      "ajax": {
        "url": call(),
        "type": 'POST',
        "data": function(d,settings) {
          d.filters = quickFilters(`${settings.nTable.id}`);
          d.reportingParameters = reportingParametersExtractor(`${settings.nTable.id}`);
          if ($(`#approval-sort-btn-${settings.nTable.id.replace("example1", "")}`).length > 0) {
            d.approvalSort = $(`#approval-sort-btn-${settings.nTable.id.replace("example1", "")}`).attr('data-sort');
          }
          return d;
        },
      },
      columns: dataContainingColumnNames,

      initComplete: function () {
        try {

          const freezeEId = $(this).closest('table').attr('id')

          const table1 = $(`#${freezeEId}`).DataTable()
          $(`#${freezeEId}`).on('click', 'td', function () {
            const columns = table1.settings().init().columns
            cellColLen = columns.length
            cellIndex = table1.cell(this).index().column + 1

            $(this).click(function () {
              $(this).toggleClass('cell_highlighted')
              $(this).toggleClass('cell_selected')
            })
          })

          if (saveListview[`${freezeEId}`].freeze_dict) {
            fDict2[`${freezeEId}`] =
              saveListview[`${freezeEId}`].freeze_dict

            const table = $(`#${freezeEId}`).DataTable()
            new $.fn.dataTable.FixedColumns(
              table, // eslint-disable-line no-new
              saveListview[`${freezeEId}`].freeze_dict
            )

            setTimeout(() => {
              $(`#${freezeEId}`).DataTable().draw()
            }, 3000)
          }
        } catch (err) {}
        this.api()
          .columns()
          .every(function () {
            const column = this
            const title = $(this).text()
            $(
              `<input type="text" data-inputid='inputtext' data-elementid='${elementTabID}' value="" data-input_value="" class="listViewSearch" style="text-align:center;border-bottom:none;border:1px solid #ced4da;border-radius: .35rem;width:10rem;height:2rem"placeholder="Search ` +
                title +
                '" />'
            ) // eslint-disable-line no-unused-vars
              .hover(
                function () {
                  $(this).css('box-shadow', '0 2px 8px 1px rgb(64 60 67 / 24%)');
                  $(this).css('margin-bottom', '0.25rem');
                },
                function () {
                  $(this).css('box-shadow', 'none');
                  $(this).css('margin-bottom', 'unset');
                }
              )
              .appendTo($(column.footer()).empty())
              .on('keyup change', function () {
                if (
                  column.search() !== this.value ||
                  String(this.value) === ''
                ) {
                  const val = this.value
                  if (String(this.value) !== '') {
                    column
                      .search(val === null ? '' : val, true, false)
                      .draw()
                  } else if (String(this.value) === '') {
                    column.search(this.value).draw()
                  }
                }
              })
            return true
          })
          var embededTableId = $(this).closest('table').attr('id')
          $(`#${embededTableId}`).find('.listviewembededcomputation').select2()
      },
      "fnDrawCallback": function( oSettings ) {
        $(`#multiple_delete_perm_${elementTabID}`).prop('disabled', false);
        $(`#multiple_delete_temp_${elementTabID}`).prop('disabled', false);
        $(`#reject_multiple_ApprovalTemplate_${elementTabID}`).prop('disabled', false);
        $(`#approve_multiple_ApprovalTemplate_final_${elementTabID}`).css('display', 'none');
        $(`#reject_multiple_ApprovalTemplate_final_${elementTabID}`).css('display', 'none');
        $(`#multiple_delete_perm_final_${elementTabID}`).css('display', 'none');
        $(`#multiple_delete_temp_final_${elementTabID}`).css('display', 'none');
        $(`#multiple_delete_perm_${elementTabID}`).attr('data-edit-status', 'off')
        $(`#multiple_delete_perm_${elementTabID}`).text('Delete Multiple(Permanent): OFF').trigger('change')
        $(`#multiple_delete_temp_${elementTabID}`).attr('data-edit-status', 'off')
        $(`#multiple_delete_temp_${elementTabID}`).text('Delete Multiple(Temporary): OFF').trigger('change')
        $(`#approve_multiple_ApprovalTemplate_${elementTabID}`).attr('data-edit-status', 'off')
        $(`#approve_multiple_ApprovalTemplate_${elementTabID}`).text('Approve Multiple: OFF').trigger('change')
        $(`#reject_multiple_ApprovalTemplate_${elementTabID}`).attr('data-edit-status', 'off')
        $(`#reject_multiple_ApprovalTemplate_${elementTabID}`).text('Reject Multiple: OFF').trigger('change')
        let dt = $(`#example1${elementTabID}`).DataTable();
        let rowCount = dt.data().count();
        if(rowCount === 0){
          row_flag = false
          $(`#approve_all_ApprovalTemplate_${elementTabID}`).prop('disabled', 'true');
          $(`#reject_all_ApprovalTemplate_${elementTabID}`).prop('disabled', 'true');
          $(`#approve_multiple_ApprovalTemplate_${elementTabID}`).prop('disabled', 'true');
          $(`#reject_multiple_ApprovalTemplate_${elementTabID}`).prop('disabled', 'true');
        }
        if (row_flag){
          $(`#approve_multiple_ApprovalTemplate_${elementTabID}`).prop('disabled', false);
          $(`#reject_multiple_ApprovalTemplate_${elementTabID}`).prop('disabled', false);
        }
        var embededTableId = $(this).closest('table').attr('id')
        $(`#${embededTableId}`).find('.listviewembededcomputation').select2()
        table.buttons().container().children().addClass("btn btn-md mx-2 rounded px-2")
        if ($(`#${oSettings.sInstance}`).hasClass('card-view-template')){
          var labels = [];
            $(`#${oSettings.sInstance} thead th`).each(function () {
              labels.push($(this).text());
            });
            var dataList = $(`#${oSettings.sInstance}`).attr('data-list')
            $(`#${oSettings.sInstance}`).find('tbody').find('tr').each(function () {
              $(this)
                .find("td")
                .each(function (column) {
                  $("<span class='colHeader'>" + labels[column] + ":</span>").prependTo(
                    $(this)
                  );
                });
            });
            $(`#${oSettings.sInstance}`).parent().parent().find('.dataTables_scrollHead').css('display','none')
            if (dataList != ""){
              dataList = JSON.parse(dataList)
              $(`#${oSettings.sInstance}`).find('tbody').attr('style',
              `display: grid;
              gap: ${dataList['card-padding']}px;
              grid-template-columns: repeat(${dataList['card-no-one-row']},1fr);
              `)
              $(`#${oSettings.sInstance}`).find('tbody').find('tr').each(function(){
                $(this).attr('style',
                `width: ${dataList['card-wdith']}rem;
                height:${dataList['card-height']}rem;
                background-color: transparent !important;
                box-shadow: ${dataList['card-shadow-h-offset']}px ${dataList['card-shadow-v-offset']}px ${dataList['card-shadow-blur']}px ${dataList['card-shadow-spread']}px ${dataList['card-shadow-color-rgba']};
                overflow:auto;
                border-radius:${dataList['card-border-radius']}px;
                border:${dataList['card-border-width']}px ${dataList['card-border-style']} ${dataList['card-border-color-rgba']};
                `)
              })
              $(`#${oSettings.sInstance}`).find('tbody').find('tr').find('td').each(function(){
                $(this).attr('style',`
                display: flex;
                white-space: normal;
                border: ${dataList['field-border-width']}px ${dataList['field-border-style']} ${dataList['field-border-color-rgba']};
                flex-direction:row;
                justify-content:${dataList['font-alignment']};
                color:${dataList['font-value-color']};
                font-size:${dataList['font-value-size']};
                `)
                $(this).find('.colHeader').attr('style',`
                color:${dataList['font-header-color']};
                font-size:${dataList['font-header-size']};
                `)
              })
            }
        }

        template_type = $(`#${oSettings.sInstance}`).attr('data-list_type_template')
        if (template_type && template_type == "Approval Template"){
          $(`#${oSettings.sInstance}`).find('tbody').find('tr').find('td').each(function(){
            $(this).parent().find('td').eq(0).find('a[title="Reject record"]').css("pointer-events","none")
            $(this).parent().find('td').eq(0).find('a[title="Approve record"]').css("pointer-events","none")
            $(this).parent().find('td').eq(0).find('a[title="Delegate Approval"]').css("pointer-events","none")
            $(this).parent().find('td').eq(0).find('a[title="Resend record"]').css("pointer-events","none")
            $(this).parent().find('td').eq(0).find('a[title="Edit record"]').css("pointer-events","none")
            $(this).parent().find('td').eq(0).find('a[title="Approval Wall"]').attr("data-approve","false")
            $(this).parent().find('td').eq(0).find('a[title="Approval Wall"]').attr("data-reject","false")
            $(this).parent().find('td').eq(0).find('a[title="Approval Wall"]').attr("data-resend","false")
            $(this).parent().find('td').eq(0).find('a[title="Approval Wall"]').attr("data-edit","false")
            $(this).parent().find('td').eq(0).find('a[title="Approval Wall"]').attr("data-delegate","false")
          })

          $(`#${oSettings.sInstance}`).find('tbody').find('tr').each(function(){
            $(this).parent().find('tr').find('a[title="Approve record"]').css("pointer-events","none")
            $(this).parent().find('tr').find('a[title="Resend record"]').css("pointer-events","none")
            $(this).parent().find('tr').find('a[title="Reject record"]').css("pointer-events","none")
            $(this).parent().find('tr').find('a[title="Delegate Approval"]').css("pointer-events","none")
          })

          tr_index = []
          tr_index_resend = []
          tr_index_edit = []
          oTableData = oSettings.json.data
          var approvalTemplateTableNameField = oSettings.json.table_name_column_verbose_name;
          $(`#${oSettings.sInstance}`).find('tbody > tr > td').find('a[title="Reject record"]').attr('data-approvalTableNameField', approvalTemplateTableNameField);
          $(`#${oSettings.sInstance}`).find('tbody > tr > td').find('a[title="Approve record"]').attr('data-approvalTableNameField', approvalTemplateTableNameField);
          $(`#${oSettings.sInstance}`).find('tbody > tr').find('a[title="Approve record"]').attr('data-approvalTableNameField', approvalTemplateTableNameField);
          $(`#${oSettings.sInstance}`).find('tbody > tr').find('a[title="Reject record"]').attr('data-approvalTableNameField', approvalTemplateTableNameField);
          for(let i=0;i<oTableData.length;i++){
              for (let [k1, v1] of Object.entries(oTableData[i])) {
                if(oSettings.json.allow_ids.includes(String(v1))){
                  tr_index.push(i)
                }

                if(oSettings.json.allow_ids_resend.includes(String(v1))){
                  tr_index_resend.push(i)
                }

                if(oSettings.json.allow_ids_edit.includes(String(v1))){
                  tr_index_edit.push(i)
                }
            }
          }
          for(let i=0;i<tr_index.length;i++){
            $(`#${oSettings.sInstance}`).find('tbody').find('tr').eq(tr_index[i]).find('td').find('a[title="Reject record"]').css("pointer-events","all")
            $(`#${oSettings.sInstance}`).find('tbody').find('tr').eq(tr_index[i]).find('a[title="Reject record"]').css("pointer-events","all")
            $(`#${oSettings.sInstance}`).find('tbody').find('tr').eq(tr_index[i]).find('td').find('a[title="Approve record"]').css("pointer-events","all")
            $(`#${oSettings.sInstance}`).find('tbody').eq(tr_index[i]).find('tr').find('a[title="Approve record"]').css("pointer-events","all")
            $(`#${oSettings.sInstance}`).find('tbody').eq(tr_index[i]).find('tr').find('a[title="Delegate Approval"]').css("pointer-events","all")
            $(`#${oSettings.sInstance}`).find('tbody').find('tr').eq(tr_index[i]).find('td').find('a[title="Delegate Approval"]').css("pointer-events","all")
            $(`#${oSettings.sInstance}`).find('tbody').find('tr').eq(tr_index[i]).find('td').find('a[title="Approval Wall"]').attr("data-approve","true")
            $(`#${oSettings.sInstance}`).find('tbody').find('tr').eq(tr_index[i]).find('td').find('a[title="Approval Wall"]').attr("data-reject","true")
            $(`#${oSettings.sInstance}`).find('tbody').find('tr').eq(tr_index[i]).find('td').find('a[title="Approval Wall"]').attr("data-delegate","true")

            if (oSettings.json.user_additional_info) {
              $(`#${oSettings.sInstance}`).find('tbody').find('tr').eq(tr_index[i]).find('a[title="Delegate Approval"]').attr('data-user-info', JSON.stringify(oSettings.json.user_additional_info))
              $(`#${oSettings.sInstance}`).find('tbody').find('tr').eq(tr_index[i]).find('td').find('a[title="Delegate Approval"]').attr('data-user-info', JSON.stringify(oSettings.json.user_additional_info))
              $(`#${oSettings.sInstance}`).find('tbody').find('tr').eq(tr_index[i]).find('td').find('a[title="Approval Wall"]').attr('data-user-info', JSON.stringify(oSettings.json.user_additional_info))
              $(`#${oSettings.sInstance}`).find('tbody').find('tr').eq(tr_index[i]).find('a[title="Delegate Approval"]').attr('data-current-user', oSettings.json.current_user)
              $(`#${oSettings.sInstance}`).find('tbody').find('tr').eq(tr_index[i]).find('td').find('a[title="Delegate Approval"]').attr('data-current-user', oSettings.json.current_user)
              $(`#${oSettings.sInstance}`).find('tbody').find('tr').eq(tr_index[i]).find('td').find('a[title="Approval Wall"]').attr('data-current-user', oSettings.json.current_user)
            }
          }

          for(let i=0;i<tr_index_resend.length;i++){
            $(`#${oSettings.sInstance}`).find('tbody').find('tr').eq(tr_index_resend[i]).find('td').find('a[title="Resend record"]').css("pointer-events","all")
            $(`#${oSettings.sInstance}`).find('tbody').eq(tr_index_resend[i]).find('tr').find('a[title="Resend record"]').css("pointer-events","all")
            $(`#${oSettings.sInstance}`).find('tbody').find('tr').eq(tr_index_resend[i]).find('td').find('a[title="Approval Wall"]').attr("data-resend","true")
          }

          for(let i=0;i<tr_index_edit.length;i++){
            $(`#${oSettings.sInstance}`).find('tbody').find('tr').eq(tr_index_edit[i]).find('td').find('a[title="Edit record"]').css("pointer-events","all")
            $(`#${oSettings.sInstance}`).find('tbody').find('tr').eq(tr_index_edit[i]).find('td').find('a[title="Approval Wall"]').attr("data-edit","true")
          }
        }
      },
    })
    .columns.adjust()
  }

    $(`#example1${elementTabID}`).DataTable().buttons().container().css("display", "none");
  setTimeout(function () {
    $(`#example1${elementTabID}`).DataTable().columns.adjust()
  }, 500)
  $(`#extract_data_modal_${elementTabID} .modal-footer`).find('.buttons-excel').off('click').on('click', function(){
    $(`#example1${elementTabID}`).DataTable().button('.buttons-excel').trigger();
  });
  $(`#extract_data_modal_${elementTabID} .modal-footer`).find('.buttons-pdf').off('click').on('click', function(){
    $(`#example1${elementTabID}`).DataTable().button('.buttons-pdf').trigger();
  });
  $(`#extract_data_modal_${elementTabID} .modal-footer`).find('.buttons-copy').off('click').on('click', function(){
    $(`#example1${elementTabID}`).DataTable().button('.buttons-copy').trigger();
  });
  if (paginationInt.length > 0) {
    $(`#showEntries${elementTabID}`).empty();
    for (let p in paginationInt) {
      if (p == parseInt(paginationInt.length/2)) {
        $(`#showEntries${elementTabID}`).append(`<option value="${paginationInt[p]}" selected>${pagination[p]}</option>`);
      } else {
        $(`#showEntries${elementTabID}`).append(`<option value="${paginationInt[p]}">${pagination[p]}</option>`);
      }
    }
  }
  dataTableColumnsArray = $(`#example1${elementTabID}`).DataTable().settings().init().columns;
  $(`#listViewColumnVisibilityDropdown${elementTabID}`).empty();
  for (let p in dataTableColumnsArray) {
    $(`#listViewColumnVisibilityDropdown${elementTabID}`).append(`<div class="dropdown-item" data-table-id="${elementTabID}" data-column_index="${p}">${dataTableColumnsArray[p]['data']}</div><div class="dropdown-divider" style="margin:0"></div>`);
  }
  $(`#listViewColumnVisibilityDropdown${elementTabID}`).find('.dropdown-item').each(function(){
    $(this).off('click').on('click', function(e) {
      e.stopPropagation();
      $(this).toggleClass('hide');
      if ($(this).hasClass('hide')) {
        $(`#example1${$(this).attr('data-table-id')}`).DataTable().column(parseInt($(this).attr('data-column_index'))).visible(false);
      } else {
        $(`#example1${$(this).attr('data-table-id')}`).DataTable().column(parseInt($(this).attr('data-column_index'))).visible(true);
      }
    });
  });

  $(`#showEntries${elementTabID}`).off('select2:select').on('select2:select', function(){
    let connectedLVElementId = $(this).attr('data-elementid');
    $(`#example1${connectedLVElementId}`).DataTable().page.len(parseInt($(this).val())).draw();
  });

  $('#example1' + elementTabID).on(
    'column-visibility.dt',
    // eslint-disable-next-line no-unused-vars
    function (e, settings, column, state) {
      $('#' + settings.sInstance)
        .DataTable()
        .columns.adjust()
    }
  )
  if(Object.keys(list_table_header_config).length === 0){

    $(`#example1${elementTabID}_wrapper .dataTables_scrollFoot`).css(
      'top',
      '32px'
    )
  }
  else{
    $(`#example1${elementTabID}_wrapper .dataTables_scrollFoot`).css(
      'top',
      '14%'
    )
  }

  $(`#example1${elementTabID}_wrapper .dataTables_scroll`).css(
    'position',
    'relative'
  )
  $(`#example1${elementTabID}_wrapper .dataTables_scrollHead`).css(
    'margin-bottom',
    '40px'
  )
  $(`#example1${elementTabID}_wrapper .dataTables_scrollFoot`).css(
    'position',
    'absolute'
  )


  $(`#example1${elementTabID} thead tr`).eq(1).find('th').on(
    'change paste keyup',
    'input',
    function () {}
  )


  datatableDict[elementTabID] = table
  $(`#example1${elementTabID}_length`).css('display', 'inline-block')
  $(`#example1${elementTabID}_length`).css('float', 'none')
  $(`#example1${elementTabID}_filter`).css('display', 'none')

  var templateType = $(`#${elementTabID}_tab_content`).attr("data-template-type")
  if (["Reporting View", "List View With History", "Approval Template"].includes(templateType)) {
    $(`#tableTab${elementTabID}`).find('select').on('select2:select', function() {
      let parameterParentContainer = $(this).parent().parent().closest('.card.col-12');
      parameterParentContainer.find('select').each(function() {
        if (!($(this).val())) {
          parameterParentContainer.find(`.row.saveReportView`).find('button').prop('disabled', true);
          return false
        } else {
          parameterParentContainer.find(`.row.saveReportView`).find('button').prop('disabled', false);
        }
      });
    })
    if($(`#tableTab${elementTabID}`).find('select').attr('data-dont_show_detail_btn') == 'True'){
      let container = $(`#tableTab${elementTabID}`)
      $(`#tableTab${elementTabID}`).find('select').on('change', function(){
        let selectedParameters = {};
        container.find('select').each(function() {
          selectedParameters[$(this).attr('data-parameter-name')] = $(this).val();
        });
        let listViewElementId = $(this).parent().parent().parent().parent().attr('id').replace('tableTab', '');
        if (!Object.values(selectedParameters).includes(null)) {
          $(`#example1${listViewElementId}`).DataTable().draw();
          $(`#${listViewElementId}_tab_content`).find('.card-body').css('display','block');
        }
      })
    }
    else{
      $(`#tableTab${elementTabID}`).find(`.row.saveReportView`).find('button').on('click', function() {
        let listViewElementId = $(this).parent().attr('id').replace('_tableTabSaveBtn', '');
        $(`#example1${listViewElementId}`).DataTable().draw();
        $(`#${listViewElementId}_tab_content`).find('.card-body').css('display','block');
      });
    }
  } else if (templateType == "Multi Dropdown View") {
    $(`#${elementTabID}_tab_content`).find('.card-body').css('display','block');
    $('#tableTab'+elementTabID).find('select').on("select2:select",function(){
      var element_id = ($(this).closest(".card").attr("id")).replace("tableTab","");
      var viewName = $(this).val();
      getViewTable(element_id, viewName)
      $('#'+element_id+'_tab_content').find('.card').eq(1).css('pointer-events', 'none');
      $('#'+element_id+'_tab_content').find('.card').eq(1).prepend(`
          <div id="backgroundBlock" style="
              z-index: 10;
              height: 100%;
              width: 100%;
              position: fixed;
              text-align: center;
              background-color: rgba(0,0,0,0.2);
          "><i class="fas fa-spinner fa-pulse" style="font-size: xxx-large; top: 50%; position: relative;"></i></div>
      `)
      $('#'+element_id+'_tab_content').find('.card').find('.bodyListview').prepend(`<div class='mul_heading'><h4 style="color: var(--primary-color);font-size: 1.1rem;font-weight: 400;border-bottom: 1px solid #00000020;margin-bottom: .75rem;padding-bottom: 0.75rem;">${viewName}</h4></div>`)
    });
  }

  if ($(`#example1${elementTabID}`).attr('data-list_type_template') == "Approval Template") {
    $(`#approval-sort-btn-${elementTabID}`).on('click', function(){
      if ($(`#approval-sort-btn-${elementTabID}`).attr('data-sort') == "active") {
        $(`#approval-sort-btn-${elementTabID}`).attr('data-sort', 'inactive')
      } else {
        $(`#approval-sort-btn-${elementTabID}`).attr('data-sort', 'active')
      }
      $(`#example1${elementTabID}`).DataTable().draw();
    });
  }

  $(`#example1${elementTabID} tbody`).on('click', 'a', function (e) {
    const idDatatable = $(this).closest('table').attr('id')
    const table = $('#' + idDatatable).DataTable()
    const template_type = $(`#${idDatatable}`).attr("data-list_type_template")
    const tData = $(this.closest('tr'))

    const tab = table.row(tData).data()
    if ('id' in tab){
      primaryKeyId = tab['id']
    }else if ('ID' in tab){
      primaryKeyId = tab['ID']
    }else if ('iD' in tab){
      primaryKeyId = tab['iD']
    }else if ('Id' in tab){
      primaryKeyId = tab['Id']
    }

    let app_tablename = ""
    if(template_type == "Approval Template"){
      var tableFieldName = $(this).attr('data-approvalTableNameField');
      if(tableFieldName in tab){
        app_tablename = tab[tableFieldName]
      }
    }
    elementID = $(this).closest('table').attr('id').split('example1')[1]
    elementIDData = $(this).attr('data-elementID')
    tableName = $(this).attr('data-table_model_name')

    let url = windowLocation
    let url1
    if (e.target.attributes[1] != undefined){
      if (String(e.target.attributes[1].value) === 'detail') {
        const header = []
        const value = []
        const valueRTF = []
        const attrRTF = []
        const dataAttr = []
        $(`#example1${elementID} thead tr th`).each(function () {
          header.push($(this).text())
        })
        const curr = $(this).closest('tr')
        curr.find('td').each(function () {
          if (String($(this).find('button').text()) === 'View Details') {
            value.push($(this).find('button').attr('data-name'))
            dataAttr.push($(this).find('button').attr('data-col'))
            attrRTF.push('')
          } else if (String($(this).find('button').text()) === 'View Data') {
            value.push($(this).find('button').attr('data-data'))
            attrRTF.push($(this).find('button').attr('onclick'))
          } else {
            value.push($(this).text())
            attrRTF.push('')
          }
        })
        const html = `
        <table id="viewDetailOnModalTable" class="row-border" style="width:100%">
        <thead>
          <tr>
            <th>Column</th>
            <th>Value</th>
          </tr>
        </thead>
        <tbody>
        </tbody>
      </table>
        `
        $('#' + elementIDData + '_tab_content')
          .find('#viewDetailOnModal')
          .find('.modal-body')
        $('#' + elementIDData + '_tab_content')
          .find('#viewDetailOnModal')
          .find('.modal-body')
          .empty()
        $('#' + elementIDData + '_tab_content')
          .find('#viewDetailOnModal')
          .find('.modal-body')
          .append(html)
        const ms = []
        let ind = 0
        for (let i = 1; i < header.length; i++) {
          let html = '<tr>'
          html = html + `<td>${header[i]}</td>`
          if (String(value[i][0]) === '{') {
            JSON.parse(value[i])
            html =
              html +
              `<td data-name='${value[i]}' data-col='${dataAttr[ind]}'><button id="element_id" class="view_listview_data"  style="background-color:transparent; border:transparent;">View Details</button></td>`
            ms.push(header[i].replaceAll(' ', '_'))
            ind = ind + 1
          } else if (String(value[i][0]) === '<') {
            html =
              html +
              `<td><button style="background-color:transparent; border:transparent;" class="view_listview_data" data-data='${value[i]}' onclick='${attrRTF[i]}'>View Data</button></td>`
          } else {
            html = html + `<td>${value[i]}</td>`
          }
          html = html + '</tr>'
          $('#' + elementIDData + '_tab_content')
            .find('#viewDetailOnModal')
            .find('.modal-body')
            .find('tbody')
            .append(html)
        }
        viewDetailOnModalTableFunc(elementIDData)
        setTimeout(() => {
          $('#' + elementIDData + '_tab_content')
            .find('#viewDetailOnModalTable')
            .DataTable()
            .columns.adjust()
            .draw()
        }, 300)
        $('#' + elementIDData + '_tab_content')
          .find('#viewDetailOnModal')
          .css('display', 'block')
        $('#' + elementIDData + '_tab_content')
          .find('#viewDetailOnModal')
          .css('opacity', 1)
        if (ind !== 0) {
          for (let z = 0; z < mColBasefilter[elementIDData].length; z++) {
            $('#' + elementIDData + '_tab_content')
              .find('#viewDetailOnModal')
              .find('table tbody')
              .find(`td[data-col=${mColBasefilter[elementIDData][z]}]`)
              .on('click', function () {
                const mCol = mColBasefilter[elementIDData][z]
                const tableTextInd = {}
                tableTextInd[elementID + '_' + mCol] = []
                if ($(this).attr('data-name')) {
                  let ids = []
                  let bool
                  try {
                    const opop = JSON.parse($(this).attr('data-name'))
                    let rr
                    for (
                      let i = 0;
                      i <
                      $(
                        '#formModalListL' + `${elementID}` + '_' + mCol
                      ).find('.ioL').length;
                      i++
                    ) {
                      rr = $('#masterListTablei' + elementID + '_' + mCol)
                        .find('tbody')
                        .find('tr')
                        .eq(i)
                        .find('td')
                        .eq(-1)
                        .text()
                      rr = rr.trim()
                      if (String(opop[rr]) !== 'undefined') {
                        ids = [...ids, rr]
                      }
                    }
                    bool = false
                    for (const i in ids) {
                      if (Number.isInteger(parseInt(ids[i]))) {
                        ids[i] = parseInt(ids[i])
                      }
                    }
                    let r
                    let coun = 0
                    for (const i in ids) {
                      if (Number.isInteger(parseInt(ids[i]))) {
                        for (
                          let j = 0;
                          j <=
                          $(
                            '#masterListTablei' + elementID + '_' + mCol
                          ).find('.ioL').length;
                          j++
                        ) {
                          r = $(
                            '#masterListTablei' + elementID + '_' + mCol
                          )
                            .find('tr')
                            .eq(j)
                            .find('td')
                            .eq(-1)
                            .text()
                          r = r.trim()
                          if (String(r) === String(ids[i])) {
                            coun = coun + 1
                          }
                        }
                      }
                    }
                    if (coun === ids.length) {
                      bool = true
                    }
                  } catch (err) {
                    bool = false
                  }
                  if (bool) {
                    const lenn =
                      tableTextInd[elementID + '_' + mCol].length
                    tableTextInd[elementID + '_' + mCol].splice(0, lenn)
                    for (
                      let i = 0;
                      i <=
                      $('#masterListTablei' + elementID + '_' + mCol).find(
                        '.ioL'
                      ).length;
                      i++
                    ) {
                      let tableText = $(
                        '#masterListTablei' + elementID + '_' + mCol
                      )
                        .find('tr')
                        .eq(i)
                        .find('td')
                        .eq(-1)
                        .text()
                      tableText = tableText.trim()
                      for (const j in ids) {
                        if (String(ids[j]) === String(tableText)) {
                          tableTextInd[elementID + '_' + mCol].push(i)
                        }
                      }
                    }
                    $('#showDetailList' + elementID)
                      .find('#listDetailTable' + elementID + '_wrappper')
                      .remove()
                    $('#showDetailList' + elementID)
                      .find('.card-body')
                      .empty()
                    $('#showDetailList' + elementID)
                      .find('.card-body')
                      .append(
                        `
                <table id="listDetailTable${elementID}" style="width:100%"  class="row-border display compact">
                  <thead style="width:100%">
                  </thead>

                  <tbody>

                  </tbody>

                </table>
                `
                      )
                    $('#listDetailTable' + elementID)
                      .find('thead')
                      .empty()
                    $('#listDetailTable' + elementID)
                      .find('tbody')
                      .empty()
                    let htmlH = '<tr>'
                    for (let j = 1; j < len[elementID + '_' + mCol]; j++) {
                      const d = $(
                        '#masterListTablei' + elementID + '_' + mCol
                      )
                        .find('thead')
                        .find('tr')
                        .eq(0)
                        .find('th')
                        .eq(j)
                        .text()
                      htmlH = htmlH + `<th>${d}</th>`
                    }
                    htmlH = htmlH + '</tr>'
                    $('#listDetailTable' + elementID)
                      .find('thead')
                      .append(htmlH)
                    for (
                      let i = 0;
                      i < tableTextInd[elementID + '_' + mCol].length;
                      i++
                    ) {
                      if (
                        String(
                          $('#example1' + elementID + '_wrapper')
                            .find('table')
                            .find('tbody')
                            .find('tr')
                            .eq(i)
                            .find('td')
                            .eq(index)
                            .text()
                        ) !== 'View Detail'
                      ) {
                        $('#listDetailTable' + elementID)
                          .find('tbody')
                          .append('<tr></tr>')
                        let sent = $(
                          '#masterListTablei' + elementID + '_' + mCol
                        )
                          .find('tr')
                          .eq(tableTextInd[elementID + '_' + mCol][i])
                          .find('td')
                          .eq(1)
                          .text()
                        sent = sent.trim()
                        dataSent.push(sent)
                        for (
                          let j = 1;
                          j < len[elementID + '_' + mCol];
                          j++
                        ) {
                          try {
                            if (
                              String(
                                $(
                                  '#masterListTablei' +
                                    elementID +
                                    '_' +
                                    mCol
                                )
                                  .find('tr')
                                  .eq(0)
                                  .find('th')
                                  .eq(j)
                                  .text()
                                  .trim()
                              ) === 'Default Value'
                            ) {
                              const c = JSON.parse(
                                $(this).attr('data-name')
                              )
                              $('#listDetailTable' + elementID)
                                .find('tbody')
                                .find('tr')
                                .eq(i)
                                .append(
                                  `<td class = "dt-center allColumnClass all">${
                                    c[
                                      $(
                                        '#masterListTablei' +
                                          elementID +
                                          '_' +
                                          mCol
                                      )
                                        .find('tr')
                                        .eq(
                                          tableTextInd[
                                            elementID + '_' + mCol
                                          ][i]
                                        )
                                        .find('td')
                                        .eq(-1)
                                        .text()
                                        .trim()
                                    ]
                                  }</td>`
                                )
                            } else {
                              const c = $(
                                '#masterListTablei' + elementID + '_' + mCol
                              )
                                .find('tr')
                                .eq(tableTextInd[elementID + '_' + mCol][i])
                                .find('td')
                                .eq(j)
                                .text()
                              $('#listDetailTable' + elementID)
                                .find('tbody')
                                .find('tr')
                                .eq(i)
                                .append(
                                  `<td class = "dt-center allColumnClass all">${c}</td>`
                                )
                            }
                          } catch (err) {}
                        }
                      }
                    }
                    viewDetailTableFuncBase(elementID)
                    $('#showDetailList' + elementID).modal('show');
                    $('#' + elementIDData + '_tab_content')
                      .find('#viewDetailOnModal')
                      .css('opacity', 0)
                    setTimeout(() => {
                      $('#listDetailTable' + elementID)
                        .DataTable()
                        .columns.adjust()
                    }, 400)
                  }
                }
              })
          }
        }
      }
    }
    $('#' + elementIDData + '_tab_content')
      .find('#viewDetailOnModal')
      .find('.close')
      .on('click', function () {
        $('#' + elementIDData + '_tab_content')
          .find('#viewDetailOnModal')
          .css('display', 'none')
        $('#' + elementIDData + '_tab_content')
          .find('#viewDetailOnModal')
          .css('opacity', 0)
      })

    // Update
    if (e.target.attributes[1] != undefined){
      if (String(e.target.attributes[1].value) === 'update') {
        $(this).prop('disabled', true);
        var ThisElement = $(this);
        for (let r = 0; r < item_code_list.length; r++) {
          if (
            Object.prototype.hasOwnProperty.call(
              item_code_list[r],
              elementID
            )
          ) {
            url = `/users/${urlPath}/` + item_code_list[r][elementID] + '/'
          }
        }
        url1 = url + tableName + '/update/' + primaryKeyId + '/' // Note the ending slash.Its required for POST request
        let editName = listViewEditTemplate[elementID]
        if (String(editName) !== 'Model Definition') {
          historyViewTemplate = $(`#${elementID}_tab_content`).attr("data-template-type");
        }
        if (!editName) {
          editName = 'Default'
        }
        /* after clicking the edit icon in the datatable, a modal opens to show existing form data */
        // eslint-disable-next-line no-use-before-define
        listViewEditRow(
          url1,
          primaryKeyId,
          elementID,
          elementIDData,
          tableName,
          editName,
          ThisElement,
          template_type
        )
      }

      if (String(e.target.attributes[1].value) === 'delete per') {

        var view_name = ""
        temp_type = $(`#${elementID}_tab_content`).attr("data-template-type")
        if(temp_type == 'Multi Dropdown View'){
          view_name = $(`#tableTab${elementID}`).find("select").val()
        }

        $.ajax({
          url: `/users/${urlPath}/DataManagement/`,
          data: {
            'element_id': elementID.split("__tab__")[0],
            'operation': "fetch_list_view_msgs",
            'messages' : JSON.stringify(["confirm_permanent_delete_message","successful_permanent_delete_message"]),
            'view_name' : view_name
          },
          type: "POST",
          dataType: "json",
          success: function (data) {
            message=""
            icon=""
            if(data.confirm_permanent_delete_message){
              message = data.confirm_permanent_delete_message.message
              icon = data.confirm_permanent_delete_message.icon
            }
            iconHtml = ""
            if (icon){
              iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
            }

            custom_messages = data

            Swal.fire({
              icon : 'question',
              iconHtml,
              text: message || `Are you sure you want to delete this record?`,
              showDenyButton: true,
              showCancelButton: true,
              confirmButtonText: 'Yes',
              denyButtonText: `No`,
            }).then((result) => {
              if (result.isConfirmed) {
                $.ajax({
                  url: url + tableName + '/delete/' + primaryKeyId + '/',
                  data: {elementid: elementID, operation: 'delete_list', custom_messages: JSON.stringify(custom_messages)},
                  type: 'POST',
                  dataType: 'json',
                  success: function () {
                    $(`#deleteMessageChecker${elementID}`).css(
                      'pointer-events',
                      'none'
                    )
                    $(`#btn_delete_operation${elementID}`).prop(
                      'disabled',
                      'disabled'
                    )
                    $(
                      `.close_delete_modal[data-element-id=${elementID}]`
                    ).prop('disabled', 'disabled')
                    windowLocationAttr.reload()
                  },
                  error: function () {
                    Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                  },
                })
              }
            })

          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          },
        });


      } else if (String(e.target.attributes[1].value) === 'delete temp') {

        var view_name = ""
        temp_type = $(`#${elementID}_tab_content`).attr("data-template-type")
        if(temp_type == 'Multi Dropdown View'){
          view_name = $(`#tableTab${elementID}`).find("select").val()
        }

        $.ajax({
          url: `/users/${urlPath}/DataManagement/`,
          data: {
            'element_id': elementID.split("__tab__")[0],
            'operation': "fetch_list_view_msgs",
            'messages' : JSON.stringify(["confirm_temp_delete_message","successful_temp_delete_message"]),
            'view_name' : view_name
          },
          type: "POST",
          dataType: "json",
          success: function (data) {
            message=""
            icon=""
            if(data.confirm_temp_delete_message){
              message = data.confirm_temp_delete_message.message
              icon = data.confirm_temp_delete_message.icon
            }
            iconHtml = ""
            if (icon){
              iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
            }

            custom_messages = data

            Swal.fire({
              icon : 'question',
              iconHtml,
              text: message || `Are you sure you want to delete this record temporarily?`,
              showDenyButton: true,
              showCancelButton: true,
              confirmButtonText: 'Yes',
              denyButtonText: `No`,
            }).then((result) => {
              if (result.isConfirmed) {
                $.ajax({
                  url: url + tableName + '/delete/' + primaryKeyId + '/',
                  data: { operation: 'delete_list_temp', elementid: elementID, custom_messages: JSON.stringify(custom_messages) },
                  type: 'POST',
                  dataType: 'json',
                  success: function () {
                    $(`#deleteMessageChecker${elementID}`).css(
                      'pointer-events',
                      'none'
                    )
                    $(`#btn_delete_operation${elementID}`).prop(
                      'disabled',
                      'disabled'
                    )
                    $(
                      `.close_delete_modal[data-element-id=${elementID}]`
                    ).prop('disabled', 'disabled')
                    windowLocationAttr.reload()
                  },
                  error: function () {
                    Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                  },
                })
              }
            })
          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          },
        })
      } else if (String(e.target.attributes[1].value) === 'approve') {
        $(`#approvalCommentModal_${elementID}`).find('.modal-title').text('Approval Comment');
        $(`#approvalCommentModal_${elementID}`).find('.modal-title').css('color','var(--font-color)');
        $(`#approvalCommentModal_${elementID} .modal-body`).find('.delegateApprovalContainer').css('display', 'none');
        $(`#approvalCommentModal_${elementID} .modal-body`).find(".approvers_edit_data").empty()
        $(`#approvalCommentModal_${elementID} .modal-body`).find(".approvers_edit_data").css("display","none")
        $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("onclick","approve_ind.call(this)")
        CKEDITOR.instances[`approvalCommentText${elementID}`].setData('');
        $(`#approvalCommentModal_${elementID}`).modal('show');
        let approval_type = "approve"
        $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').text('Approve Record');
        $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("data-approval_id",String(primaryKeyId))
        $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("data-tablename",app_tablename)
        $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("data-approval_type",approval_type)
        $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("data-element-id",elementID);
      } else if (String(e.target.attributes[1].value) === 'delegate_approval') {
        $(`#approvalCommentModal_${elementID} .modal-body`).find(".approvers_edit_data").empty()
        $(`#approvalCommentModal_${elementID} .modal-body`).find(".approvers_edit_data").css("display","none")
        $(`#approvalCommentModal_${elementID}`).find('.modal-title').text('Delegate Approval Actions');
        $(`#approvalCommentModal_${elementID}`).find('.modal-title').css('color','var(--font-color)');
        let userInfo = $(this).attr('data-user-info');
        let currentUserName = $(this).attr('data-current-user');
        if (userInfo) {
          userInfo = JSON.parse(userInfo);
        } else {
          userInfo = {};
        }
        let delegateToDropdownElement = $(`#approvalCommentModal_${elementID} .modal-body`).find('.delegateApprovalContainer').find('select');
        delegateToDropdownElement.empty();
        let delegateToHTML = "<option value='' selected disabled>Select User</option>";
        for (let [uName, uLabel] of Object.entries(userInfo)) {
          if (uName != currentUserName) {
            delegateToHTML += `<option value='${uName}'>${uLabel}</option>`;
          } else {
            continue;
          }
        }
        delegateToDropdownElement.append(delegateToHTML);
        $(`#approvalCommentModal_${elementID} .modal-body`).find('.delegateApprovalContainer').css('display', 'block');
        $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("onclick","delegateApproval.call(this)")
        CKEDITOR.instances[`approvalCommentText${elementID}`].setData('');
        $(`#approvalCommentModal_${elementID}`).modal('show');
        let approval_type = "delegateApproval"
        $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').text('Delegate');
        $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("data-approval_id",String(primaryKeyId))
        $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("data-approval_type",approval_type);
        $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("data-element-id",elementID);
      } else if (String(e.target.attributes[1].value) === 'reject') {
        $(`#approvalCommentModal_${elementID} .modal-body`).find(".approvers_edit_data").empty()
        $(`#approvalCommentModal_${elementID} .modal-body`).find(".approvers_edit_data").css("display","none")
        $(`#approvalCommentModal_${elementID}`).find('.modal-title').text('Rejection Comment');
        $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').text('Reject Record');
        $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("onclick","approve_ind.call(this)")
        $(`#approvalCommentModal_${elementID} .modal-body`).find('.delegateApprovalContainer').css('display', 'none');
        CKEDITOR.instances[`approvalCommentText${elementID}`].setData('');
        $(`#approvalCommentModal_${elementID}`).modal('show');
        let approval_type = "reject"
        $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("data-approval_id",String(primaryKeyId))
        $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("data-tablename",app_tablename)
        $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("data-approval_type",approval_type)
        $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("data-element-id",elementID);
      } else if (String(e.target.attributes[1].value) === 'resend') {
        $(`#approvalCommentModal_${elementID} .modal-body`).find(".approvers_edit_data").empty()
        $(`#approvalCommentModal_${elementID} .modal-body`).find(".approvers_edit_data").css("display","none")
        $(`#approvalCommentModal_${elementID}`).find('.modal-title').text('Resend Comment');
        $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').text('Resend Record');
        $(`#approvalCommentModal_${elementID} .modal-body`).find('.delegateApprovalContainer').css('display', 'none');
        CKEDITOR.instances[`approvalCommentText${elementID}`].setData('');
        $(`#approvalCommentModal_${elementID}`).modal('show');
        $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("data-approval_id",String(primaryKeyId))
        $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("data-tablename",app_tablename)
        $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("data-approval_type","resend")
        $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("onclick","resend_ind.call(this)")
        $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("data-element-id",elementID);
      } else if (String(e.target.attributes[1].value) === 'pdf'){
        const header = []
        const value = []
        const dataAttr = []
        var finalJSON = {}
        $(`#example1${elementID} thead tr th`).each(function () {
          header.push($(this).text())
        })
        const curr = $(this).closest('tr')
        curr.find('td').each(function () {
          if (String($(this).find('button').text()) === 'View Details') {
            if ($(this).find('button').attr('data-data')){
              value.push($(this).find('button').attr('data-data'))
            }else{
              value.push($(this).find('button').attr('data-name'))
            }
            dataAttr.push($(this).find('button').attr('data-col'))
          }else if (String($(this).find('button').text()) === 'View Data'){
            if ($(this).find('button').attr('data-data')){
              value.push($(this).find('button').attr('data-data'))
            }
          }else if ($(this).find('.listviewembededcomputation').length >0){

          } else {
            value.push($(this).text())
          }
        })
        for (let i = 1; i < header.length; i++){
          if (value[i] != undefined){
            if (value[i].includes('NULL')){
              finalJSON[header[i]] = '-'
            }else{
              finalJSON[header[i]] = value[i]
            }
          }
        }
        $.ajax({
          url: `/users/${urlPath}/dynamicVal/`,
          data: {
            'final_json':JSON.stringify(finalJSON),
            'data_list':$(e.target).attr('data-list'),
            'table_name':$(e.target).parent().attr('data-table_model_name'),
            'operation': 'pdf_generation_single_record',
          },
          type: "POST",
          success: function (response) {
            var a = document.createElement("a");
            a.href = `data:document/pdf;base64,${response}`;
            a.download = "Transaction Details.pdf";
            a.click();
          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error!. Please try again.'});
          }
        });
      }

      if (String(e.target.attributes[1].value) === 'approval_wall'){

        resolved_ind_comments_list = []

        allowed_rejection = $(e.target).parent().attr("data-reject")
        allowed_approval = $(e.target).parent().attr("data-approve")
        allowed_edit = $(e.target).parent().attr("data-edit")
        allowed_resend = $(e.target).parent().attr("data-resend")
        allowed_delegate = $(e.target).parent().attr("data-delegate")

        if(allowed_approval=="true"){
          $(`#approvalWallModalBody_${elementID}`).find(`#approval_wall_approve_${elementID}`).css("pointer-events","all")
          $(`#approvalWallModalBody_${elementID}`).find(`#approval_wall_approve_${elementID}`).css("opacity","1")
        }else{
          $(`#approvalWallModalBody_${elementID}`).find(`#approval_wall_approve_${elementID}`).css("pointer-events","none")
          $(`#approvalWallModalBody_${elementID}`).find(`#approval_wall_approve_${elementID}`).css("opacity","0.5")
        }

        if(allowed_rejection=="true"){
          $(`#approvalWallModalBody_${elementID}`).find(`#approval_wall_reject_${elementID}`).css("pointer-events","all")
          $(`#approvalWallModalBody_${elementID}`).find(`#approval_wall_reject_${elementID}`).css("opacity","1")
        }else{
          $(`#approvalWallModalBody_${elementID}`).find(`#approval_wall_reject_${elementID}`).css("pointer-events","none")
          $(`#approvalWallModalBody_${elementID}`).find(`#approval_wall_reject_${elementID}`).css("opacity","0.5")
        }

        if(allowed_resend=="true"){
          $(`#approvalWallModalBody_${elementID}`).find(`#approval_sendtoprevious_${elementID}`).css("pointer-events","all")
          $(`#approvalWallModalBody_${elementID}`).find(`#approval_sendtoprevious_${elementID}`).css("opacity","1")
        }else{
          $(`#approvalWallModalBody_${elementID}`).find(`#approval_sendtoprevious_${elementID}`).css("pointer-events","none")
          $(`#approvalWallModalBody_${elementID}`).find(`#approval_sendtoprevious_${elementID}`).css("opacity","0.5")
        }

        if(allowed_delegate=="true"){
          let userInfo = $(e.target).parent().attr('data-user-info');
          let currentUserName = $(e.target).parent().attr('data-current-user');
          $(`#approvalWallModalBody_${elementID}`).find(`#approval_delegate_${elementID}`).css("pointer-events","all")
          $(`#approvalWallModalBody_${elementID}`).find(`#approval_delegate_${elementID}`).css("opacity","1")
          $(`#approvalWallModalBody_${elementID}`).find(`#approval_delegate_${elementID}`).attr("data-user-info",userInfo)
          $(`#approvalWallModalBody_${elementID}`).find(`#approval_delegate_${elementID}`).attr("data-current-user",currentUserName)
        }else{
          $(`#approvalWallModalBody_${elementID}`).find(`#approval_delegate_${elementID}`).css("pointer-events","none")
          $(`#approvalWallModalBody_${elementID}`).find(`#approval_delegate_${elementID}`).css("opacity","0.5")
          $(`#approvalWallModalBody_${elementID}`).find(`#approval_delegate_${elementID}`).removeAttr("data-user-info")
          $(`#approvalWallModalBody_${elementID}`).find(`#approval_delegate_${elementID}`).removeAttr("data-current-user")
        }


        $(`#approvalWallModalBody_${elementID}`).find('.transaction_datatable').empty()

        $(`#approvalWallModalBody_${elementID}`).find(`.approval_outer_${elementID}`).empty()
        $(`#approvalWallModalBody_${elementID}`).find('.created_by_info').empty()
        $(`#approvalWallModalBody_${elementID}`).find(`#approval_status_${elementID}`).find(".card-text").empty()

        $(`#approvalWallModalBody_${elementID}`).find(`#view_at_all_levels_${elementID}`).empty()
        $(`#level_config_${elementID}`).css("display","none")

        $(`#approvalWallModalBody_${elementID}`).find(`#save_transaction_data_${elementID}`).css("display","none")
        $(`#approvalWallModalBody_${elementID}`).find(`#edit_transaction_data_${elementID}`).css("display","block")

        $(`#approvalWallModalBody_${elementID}`).find(`#approver_users_${elementID}`).css("display","block")
        $(`#approvalWallModalBody_${elementID}`).find(`#approval_status_${elementID}`).css("display","block")

        const header = []
        const dataAttr = []
        var approval_audit_log_button = ""
        $(`#example1${elementID} thead tr th`).each(function () {
          header.push($(this).text())
        })
        const curr = $(this).closest('tr')
        curr.find('td').each(function () {

          if (String($(this).find('button').text()) === 'View Details') {
            str_val = $(this).find('button').attr('data-data')

            if($(this).find('button').attr('data-name') == "approval_audit_log"){
              approval_audit_log_button = $(this).find('button')
            }
          }
        })


        $.ajax({
          url: `/users/${urlPath}/approval_table/`,
          data: {
            "approval_id": primaryKeyId,
            "element_id" :elementID,
            'operation': 'fetch_approvalwall_data',
          },
          type: "POST",
          dataType: "json",
          success: function (data) {
            let url_string = window.location.pathname
            let f_occ = url_string.indexOf('/', url_string.indexOf('/') + 1)
            let s_occ = url_string.indexOf('/', url_string.indexOf('/') + f_occ +1)
            let t_occ = url_string.indexOf('/', url_string.indexOf('/') + s_occ +1)
            let app_code = url_string.substring(f_occ+1,s_occ)
            display_sections_approval_wall = data.display_sections_approval_wall
            display_in_comments_cols = data.display_in_comments_cols
            search_in_comments_cols = data.search_in_comments_cols
            all_users_list = data.all_users_list
            var smtpConfigKey = data.smtpConfigKey
            if(display_sections_approval_wall.includes('approval_status')){
              $(`#approvalWallModalBody_${elementID}`).find(`#approval_status_${elementID}`).css("display","none")
            }else{
              $(`#approvalWallModalBody_${elementID}`).find(`#approval_status_${elementID}`).css("display","block")
            }
            if(display_sections_approval_wall.includes('approver_type')){
              $(`#approvalWallModalBody_${elementID}`).find(`#approver_type_${elementID}`).css("display","none")
            }
            else{
              $(`#approvalWallModalBody_${elementID}`).find(`#approver_type_${elementID}`).css("display","block")
            }
            if(display_sections_approval_wall.includes('type_of_approval')){
              $(`#approvalWallModalBody_${elementID}`).find(`#type_of_approval_${elementID}`).css("display","none")
            }
            else{
              $(`#approvalWallModalBody_${elementID}`).find(`#type_of_approval_${elementID}`).css("display","block")
            }
            if(display_sections_approval_wall.includes('approval_code')){
              $(`#approvalWallModalBody_${elementID}`).find(`#approval_code_${elementID}`).css("display","none")
            }
            else{
              $(`#approvalWallModalBody_${elementID}`).find(`#approval_code_${elementID}`).css("display","block")
            }
            mentions_user_list = JSON.parse(data.mentions_user_list)
            if(data.hasOwnProperty("maximum_levels_allowed")){
              $(`#approvalWallModalBody_${elementID}`).attr("data-maximum_levels_allowed",data.maximum_levels_allowed)
            }
            if(data.hasOwnProperty("maximum_approvers_allowed")){
              $(`#approvalWallModalBody_${elementID}`).attr("data-maximum_approvers_allowed",data.maximum_approvers_allowed)
            }

            var itemTemplate = `<li data-id="{id}"><strong class="username"> ${getFormattedName(search_in_comments_cols)}</strong></li>`;
            var outputTemplate = `<a href="">@${display_in_comments_cols.map(prop => `{${prop}}`).join(' ')}</a><span>&nbsp;</span>`;


            var editor1, reply_editor, reply_editor1, new_reply_editor;


              CKEDITOR.on('instanceReady', function(evt) {
                var editor = evt.editor;


                editor.on('focus', function(e) {
                    element = e.editor.container.$
                    $(element).find(".cke_top.cke_reset_all").css("display","block")
                    $(element).find(".cke_contents.cke_reset").css("height","80px")
                });

                editor.on('blur', function(e) {
                  element = e.editor.container.$
                  $(element).find(".cke_top.cke_reset_all").css("display","none")
                  $(element).find(".cke_contents.cke_reset").css("height","44px")
                })

              });


              if(editor1){
                editor1.destroy()
              }

              editor1 = CKEDITOR.replace(`approvalWallCommentText_${elementID}`, {
                height: 44,
                removeButtons: home_rtf[0],
                editorplaceholder: 'Add a comment...',
                plugins: 'mentions,undo,link,list,basicstyles,justify,richcombo,wysiwygarea,toolbar',
                extraPlugins: 'elementspath,editorplaceholder',
                toolbar: [
                  { name: 'document', items: ['Undo'] },
                  { name: 'paragraph', items: ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'] },
                  { name: 'basicstyles', items: ['Bold', 'Italic', 'Underline', 'Strike', '-', 'RemoveFormat'] },
                  { name: 'links', items: ['Mention', 'Link', 'Unlink', 'Anchor'] },
                  { name: 'styles', items: ['Styles', 'Format', 'Font', 'FontSize'] },
                  { name: 'colors', items: ['TextColor', 'BGColor'] },
                  { name: 'elementspath', items: ['ElementPath'] }
                ],
                mentions: [
                  {
                    feed: dataFeed,
                    itemTemplate: itemTemplate,
                    outputTemplate: outputTemplate,
                    minChars: 0
                  }
                ],
                removeButtons: 'PasteFromWord'
              });
              CKEDITOR.config.bodyClass = 'custom_cke_class';
              CKEDITOR.config.removePlugins = 'exportpdf';
              CKEDITOR.config.extraPlugins = 'autocorrect,elementspath';

              CKEDITOR.instances[`approvalWallCommentText_${elementID}`].setData('');

              editor1 = CKEDITOR.instances[`approvalWallCommentText_${elementID}`]
              editor1.on('change',function(){
                const typedText = editor1.getData();
                if(typedText.trim() === ''){
                  $(`#add_comment_${elementID}`).prop("disabled",true)
                }
                else{
                  $(`#add_comment_${elementID}`).prop("disabled",false)
                }
              })

              editor1.on('key',function(event){
                if (event.data.keyCode === CKEDITOR.CTRL + 13){
                  $(`#add_comment_${elementID}`).trigger("click")
                }
              })





            result_data = data.data[0];

            var approver_user_data_list = data.user_list

            var user_additional_info = data.user_additional_info

            var created_user_data = data.created_user_data
            var modified_user_data = data.modified_user_data

            var type_of_approval = result_data["type_of_approval"]
            var approver_type = result_data["approver_type"]
            var approval_code = result_data["approval_code"]
            var approved_by_current_level=[]
            var current_level=0
            var audit_log_configs=[]
            var approved_by = {}

            var approval_status = result_data["approval_status"]
            if(approval_status == "Approved" || approval_status == "Rejected"){
              freeze_comments_option = true
            }
            else{
              freeze_comments_option = false
            }

            var approver_user = JSON.parse(result_data["approver_user"])

            var verbose_table_data = JSON.parse(data.verbose_table_data)

            parsed_json_data = JSON.parse(result_data["json_data"])
            transaction_data_to_edit = JSON.parse(result_data["json_data"])[0]


            resolve_all_comments = data.resolve_all_comments
            reopen_all_comments = data.reopen_all_comments
            resolve_individual_comments = data.resolve_individual_comments
            reopen_individual_comments = data.reopen_individual_comments

            if(resolve_all_comments && (allowed_approval=="true" || allowed_rejection=="true" || allowed_edit=="true")){
              $(`#approvalWallModalBody_${elementID}`).find(`#resolve_all_button_${elementID}`).css("display","block")
              $(`#approvalWallModalBody_${elementID}`).find(`#resolve_all_button_${elementID}`).attr("disabled",false)
            }
            else{
              $(`#approvalWallModalBody_${elementID}`).find(`#resolve_all_button_${elementID}`).css("display","none")
            }


            if(result_data.approval_audit_log){
              audit_log_configs = JSON.parse(result_data.approval_audit_log)
            }


            $(`#resolve_all_button_${elementID}`).off("click").on("click", function() {
              Swal.fire({
                icon: 'question',
                text: `Are you sure you want to resolve all comments?`,
                showDenyButton: true,
                showCancelButton: true,
                confirmButtonText: 'Yes',
                denyButtonText: `No`,
              }).then((result)=>{
                if(result.isConfirmed){
                  var resolve_all = true
                  $.ajax({
                    url: `/users/${urlPath}/approval_table/`,
                    data:{
                      "operation": "update_comments_in_approval_table",
                      "resolve_all": resolve_all,
                      "approval_id": result_data.id,
                      "audit_log_configs":JSON.stringify(audit_log_configs),
                    },
                    type: 'POST',
                    dataType: "json",
                    success: function (data) {

                      $(`#approvalWallModalBody_${elementID}`).find(`#resolve_all_button_${elementID}`).attr("disabled",true)
                      $(`#approvalWallModalBody_${elementID}`).find(`#resolve_all_button_${elementID}`).css("display","none")
                      $(`#approvalWallModalBody_${elementID}`).find(`.new_discussion_${elementID}`).css("display","none")
                      $(`#approvalWallModalBody_${elementID}`).find(`.approval_outer_${elementID}`).addClass("mt-5 mb-3")
                      $(`#approvalWallModalBody_${elementID}`).find(`#comment_status${elementID}`).html("Status: <b>Resolved</b>")
                      $(`#approvalWallModalBody_${elementID}`).find(`#comment_status${elementID}`).attr("class","resolved_comment")

                      $(`#approvalWallModalBody_${elementID}`).find(`#add_comment_${elementID}`).css('display', 'none')
                      $(`#approvalWallModalBody_${elementID}`).find(`.reply_comments`).css('display', 'none')
                      $(`#approvalWallModalBody_${elementID}`).find(`.approval_comment`).css('background', "#f8f8f8")

                      $(`#approvalWallModalBody_${elementID}`).find(`.reply-area`).css('display', "none")

                      $(`#approvalWallModalBody_${elementID}`).find(".resolve_button_ind").attr('disabled', false)
                      $(`#approvalWallModalBody_${elementID}`).find(".resolve_button_ind").css('display', 'none')

                      $(`#approvalWallModalBody_${elementID}`).find(".comment_status_ind").html('Status: <b>Resolved</b>')
                      $(`#approvalWallModalBody_${elementID}`).find(".comment_status_ind").attr("class","comment_status_ind resolved_comment")

                      if(reopen_all_comments && (allowed_approval=="true" || allowed_rejection=="true" || allowed_edit=="true")){
                        $(`#approvalWallModalBody_${elementID}`).find(`#reopen_all_button_${elementID}`).css("display","block")
                        $(`#approvalWallModalBody_${elementID}`).find(`#reopen_all_button_${elementID}`).attr("disabled",false)

                      }
                      else{
                        $(`#approvalWallModalBody_${elementID}`).find(`#reopen_all_button_${elementID}`).css("display","none")
                      }

                      if(reopen_individual_comments && (allowed_approval=="true" || allowed_rejection=="true" || allowed_edit=="true")){
                        $(`#approvalWallModalBody_${elementID}`).find('.reopen_button_ind').css("display","block")
                        $(`#approvalWallModalBody_${elementID}`).find('.reopen_button_ind').attr("disabled",false)

                      }
                      else{
                        $(`#approvalWallModalBody_${elementID}`).find('.reopen_button_ind').css("display","none")
                      }

                      $(".resolve_button_ind").each(function(){
                        ele_id = this.id.split("_ind_")[1]
                        if (!resolved_ind_comments_list.includes(ele_id)) {
                          resolved_ind_comments_list.push(ele_id);
                        }
                      })


                    },
                    error: function () {
                      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                    },
                  })

                }
              })
            })

            $(`#reopen_all_button_${elementID}`).off("click").on("click", function() {
              Swal.fire({
                icon: 'question',
                text: `Are you sure you want to reopen all comments?`,
                showDenyButton: true,
                showCancelButton: true,
                confirmButtonText: 'Yes',
                denyButtonText: `No`,
              }).then((result)=>{
                if(result.isConfirmed){
                  var reopen_all = true
                  $.ajax({
                    url: `/users/${urlPath}/approval_table/`,
                    data:{
                      "operation": "update_comments_in_approval_table",
                      "reopen_all": reopen_all,
                      "approval_id": result_data.id,
                      "audit_log_configs":JSON.stringify(audit_log_configs),
                    },
                    type: 'POST',
                    dataType: "json",
                    success: function (data) {

                      $(`#approvalWallModalBody_${elementID}`).find(`#reopen_all_button_${elementID}`).attr("disabled",true)
                      $(`#approvalWallModalBody_${elementID}`).find(`#reopen_all_button_${elementID}`).css("display","none")
                      $(`#approvalWallModalBody_${elementID}`).find(`.new_discussion_${elementID}`).css("display","block")
                      $(`#approvalWallModalBody_${elementID}`).find(`.new_discussion_${elementID}`).addClass("mt-5 mb-3")
                      $(`#approvalWallModalBody_${elementID}`).find(`.approval_outer_${elementID}`).removeClass("mt-5 mb-3")

                      $(`#approvalWallModalBody_${elementID}`).find(`#add_comment_${elementID}`).css('display', 'block')
                      $(`#approvalWallModalBody_${elementID}`).find(`.reply_comments`).css('display', 'block')
                      $(`#approvalWallModalBody_${elementID}`).find(`.reply-area`).css('display', 'block')
                      $(`#approvalWallModalBody_${elementID}`).find(`.approval_comment`).css('background', "#ffffff")

                      $(`#approvalWallModalBody_${elementID}`).find(".reopen_button_ind").attr('disabled', false)
                      $(`#approvalWallModalBody_${elementID}`).find(".reopen_button_ind").css('display', 'none')

                      $(`#approvalWallModalBody_${elementID}`).find(`#comment_status${elementID}`).html("Status: <b>Reopened</b>")
                        $(`#approvalWallModalBody_${elementID}`).find(`#comment_status${elementID}`).attr("class","reopened_comment")

                        $(`#approvalWallModalBody_${elementID}`).find(".comment_status_ind").html('Status: <b>Reopened</b>')
                        $(`#approvalWallModalBody_${elementID}`).find(".comment_status_ind").attr("class", "comment_status_ind reopened_comment")


                      if(resolve_all_comments && (allowed_approval=="true" || allowed_rejection=="true" || allowed_edit=="true")){
                        $(`#approvalWallModalBody_${elementID}`).find(`#resolve_all_button_${elementID}`).css("display","block")
                        $(`#approvalWallModalBody_${elementID}`).find(`#resolve_all_button_${elementID}`).attr("disabled",false)
                      }
                      else{
                        $(`#approvalWallModalBody_${elementID}`).find(`#resolve_all_button_${elementID}`).css("display","none")
                      }

                      if(resolve_individual_comments && (allowed_approval=="true" || allowed_rejection=="true" || allowed_edit=="true")){
                        $(`#approvalWallModalBody_${elementID}`).find('.resolve_button_ind').css("display","block")
                        $(`#approvalWallModalBody_${elementID}`).find('.resolve_button_ind').attr("disabled",false)

                      }
                      else{
                        $(`#approvalWallModalBody_${elementID}`).find('.resolve_button_ind').css("display","none")
                      }

                      resolved_ind_comments_list = []

                    },
                    error: function () {
                      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                    },
                  })

                }
              })
            })

            if(allowed_edit=="true" && allowed_approval != "true"){
              $(`#approvalWallModalBody_${elementID}`).find(`#edit_transaction_data_${elementID}`).attr("disabled",false)
            }else{
              $(`#approvalWallModalBody_${elementID}`).find(`#edit_transaction_data_${elementID}`).attr("disabled",true)
            }


            if(result_data["modify_column"]){
              modify_column = JSON.parse(result_data["modify_column"])
            }

            $(`#approvalWallModalBody_${elementID}`).find(`#add_levels_div_${elementID}`).css("display","none")

            if(parsed_json_data){

              transaction_data_alignment_class = ""
              if(data.transaction_data_alignment != ""){
                transaction_data_alignment_class = `text-${data.transaction_data_alignment.toLowerCase()}`
              }

              var jsondatahtml =`
                <table id="aprovalwallJsondata_${elementID}" class="table table-striped table-bordered" cellspacing="0" width="100%">
                  <thead>
                    <tr>
                      <th class="${transaction_data_alignment_class}">Particulars</th>
                      <th class="${transaction_data_alignment_class}">Details</th>
                    </tr>
                  </thead>
                  <tbody>
                  </tbody>
                </table>`

              $(`#approvalWallModalBody_${elementID}`).find('.transaction_datatable').append(jsondatahtml)
              var appJSONCols = data.appJSONCols
              for (let i in parsed_json_data){
                string = ""
                for(let [key,value] of Object.entries(parsed_json_data[i]) ){
                  if (!appJSONCols.includes(key)) {

                    if(String(key) == "created_by"){
                      const targetItem = created_user_data[0]
                      let additionalString = '';

                      if (targetItem) {
                        const { username, ...dataWithoutUsername } = targetItem;
                        const dataValues = Object.values(dataWithoutUsername).filter(value => value!="-" && value!="");
                        additionalString = `(${dataValues.join(' ')})`;
                      }
                      string+=`<tr>
                        <td class="view_details_wrap ${transaction_data_alignment_class}" data-columnname="${String(key)}">${verbose_table_data[String(key)]}</td>
                        <td class="view_details_wrap ${transaction_data_alignment_class}">${String(value)} ${additionalString}</td>
                      </tr>`
                    }
                    else if(String(key) == "modified_by"){
                      const targetItem = modified_user_data[0]
                      let additionalString = '';

                      if (targetItem) {
                        const { username, ...dataWithoutUsername } = targetItem;
                        const dataValues = Object.values(dataWithoutUsername).filter(value => value!="-" && value!="");
                        additionalString = `(${dataValues.join(' ')})`;
                      }
                      string+=`<tr>
                        <td class="view_details_wrap ${transaction_data_alignment_class}" data-columnname="${String(key)}">${verbose_table_data[String(key)]}</td>
                        <td class="view_details_wrap ${transaction_data_alignment_class}">${String(value)} ${additionalString}</td>
                      </tr>`
                    }
                    else{
                      string+=`<tr>
                        <td class="view_details_wrap ${transaction_data_alignment_class}" data-columnname="${String(key)}">${verbose_table_data[String(key)]}</td>
                        <td class="view_details_wrap ${transaction_data_alignment_class}">${String(value)}</td>
                      </tr>`
                    }
                  }
                }
              }

              $(`#aprovalwallJsondata_${elementID}`).find('tbody').append(string)

              var table = $(`#aprovalwallJsondata_${elementID}`).DataTable(
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

              $(`#aprovalwallJsondata_${elementID}`).on( 'column-visibility.dt', function ( e, settings, column, state ) {
                $(`#aprovalwallJsondata_${elementID}`).DataTable().columns.adjust()
              });
              $(document).on('shown.bs.modal', function (e) {
                  $.fn.dataTable.tables( {visible: true, api: true} ).columns.adjust();
              });

            }

            if(result_data.approved_by){
              approved_by = JSON.parse(result_data["approved_by"])
              if (approved_by.hasOwnProperty(current_level)){
                approved_by_current_level = approved_by[current_level]
              }
            }


            if(result_data.approval_level_config){
              approval_level_config = JSON.parse(result_data["approval_level_config"])
              $(`#level_config_${elementID}`).css("display","block")
              current_level = approval_level_config.current_level

              approval_levels = approval_level_config["level_config"]

              $(`#approvalWallModalBody_${elementID}`).find(`#approver_users_${elementID}`).css("display","none")

              $(`#approvalWallModalBody_${elementID}`).find(`#edit_approvers_${elementID}`).css("display","none")
              $(`#approvalWallModalBody_${elementID}`).find(`#save_approvers_${elementID}`).css("display","none")

              if(allowed_edit=="true"){
                user_additional = JSON.stringify(user_additional_info)
                $(`#approvalWallModalBody_${elementID}`).find(`#edit_approval_levels_${elementID}`).css("display","block")
                $(`#approvalWallModalBody_${elementID}`).find(`#save_approval_levels_${elementID}`).css("display","none")
                $(`#approvalWallModalBody_${elementID}`).find(`#edit_approval_levels_${elementID}`).attr("onclick",`editApprovalLevels(${result_data.id},${result_data.approval_level_config})`)
                $(`#approvalWallModalBody_${elementID}`).find(`#save_approval_levels_${elementID}`).attr("onclick",`saveLevelChangeComment(${result_data.id},${result_data.approval_level_config})`)
              }else{
                $(`#approvalWallModalBody_${elementID}`).find(`#edit_approval_levels_${elementID}`).css("display","none")
                $(`#approvalWallModalBody_${elementID}`).find(`#save_approval_levels_${elementID}`).css("display","none")
              }


              for (let i in approval_levels){
                let approved_by_level = []
                if(approved_by[parseInt(i)]){
                  approved_by_level = approved_by[parseInt(i)]
                }

                non_sortable_class=""
                bg_color=""

                if(parseInt(i)==current_level){
                  if(result_data["approval_status"]=="Pending"){
                    bg_color="background: #ffd700;color:black;"
                  }
                  else if(result_data["approval_status"] == "Rejected"){
                    bg_color="background: rgba(205,74,69,1);color:white;"
                  }
                  else if(result_data["approval_status"] == "Approved"){
                    bg_color="background: rgba(85,163,98,1);color:white;"
                  }
                }
                if(parseInt(i)<current_level){
                  non_sortable_class ="no_sort"
                  bg_color="background: darkgrey;color:white;"
                }


                string=`<div data-level="${i}" class="approval_level_divs ${non_sortable_class}">
                <div class="row">
                  <div class="col-3"><div class="levelclass" style="${bg_color}">Level ${i}</div></div>
                  <div class="col-9" style="border-left: 1px solid lightgrey;">`

                if(approval_levels[i].hasOwnProperty("approver_type")){
                  string += `<div style="border-radius: 0.5rem;padding: 10px;text-align: left;">`
                  string += `<div><h6 style="margin-bottom:0rem;text-transform:capitalize;font-weight: bold;" data-col="approver_type">${approval_levels[i]["approver_type"]} approvers</h6></div></div>`
                }

                if(approval_levels[i].hasOwnProperty("approval_type")){
                  string += `<div style="border-radius: 0.5rem;padding: 10px;text-align: left;display:none;">`
                  string += `<div><h6 style="margin-bottom:0rem;text-transform:capitalize;font-weight: bold;" data-col="approval_type">${approval_levels[i]["approval_type"]}</h6></div></div>`
                }

                if(approval_levels[i].hasOwnProperty("user_list")){
                  string += `<div style="border-radius: 0.5rem;padding: 10px;"><h6 style="margin-bottom: 0.5rem;font-size:13px;text-transform: capitalize;text-align: left;">Approvers</h6>`
                  string +=`<div data-col="user_list" >`
                  for(user of approval_levels[i]["user_list"]){
                    let user_initials = getInitials(user)
                    const targetItem = user_additional_info.find(item => item.username === user);
                    let additionalString = '';

                    if (targetItem) {
                      const { username, id, ...dataWithoutUsername } = targetItem;
                      const dataValues = Object.values(dataWithoutUsername).filter(value => value!="-" && value!="");
                      additionalString = `(${dataValues.join(' ')})`;
                    }
                    if(approved_by_level.includes(user)){
                      string += `<div class='align-items-center' style="display:flex;background: white;margin: 6px 0;box-shadow: rgba(0, 0, 0, 0.16) 0px 1px 4px;border: 1px solid lightgray;padding: 8px;border-radius: 5px;"><span class='radio mr-2 d-flex align-items-center justify-content-center' style='height: 20px;width: 20px;background: rgba(85,163,98,1);border-radius: 50%;border: 2px solid rgb(76 148 88);'><i class="fa fa-check" style="color:white"></i></span><h5 class="created_title mb-0 mr-2 ml-2" style="width:6%;"><span class="user_initials">${user_initials}</span></h5><div class="name_card"><h6 style="margin-bottom:1px !important;font-size: 14px;" class="text-left ml-2 username">${user}</h6>`

                    }
                    else{
                      string += `<div class='align-items-center' style="display:flex;background: white;margin: 6px 0;box-shadow: rgba(0, 0, 0, 0.16) 0px 1px 4px;border: 1px solid lightgray;padding: 8px;border-radius: 5px;"><span class='radio mr-2 d-flex align-items-center justify-content-center' style='height: 20px;width: 20px;background: #f4f4f4;border-radius: 50%;border: 2px solid grey'></span><h5 class="created_title mb-0 mr-2 ml-2" style="width:6%;"><span class="user_initials">${user_initials}</span></h5><div class="name_card"><h6 style="margin-bottom:1px !important;font-size: 14px;" class="text-left ml-2 username">${user}</h6>`
                    }
                    if(additionalString!="()" && additionalString!=""){
                      string += `<span class="ml-2 user_info" style="color: rgba(0,0,0,.55);font-size: .7rem;">${additionalString}</span></div></div>`
                    }
                    else{
                      string += `</div></div>`
                    }
                  }
                  string += `</div></div>`
                }

                if(approval_levels[i].hasOwnProperty("group_list")){
                  string += `<div style="border-radius: 0.5rem;padding: 10px;"><h6 style="margin-bottom: 0.5rem;font-size:13px;text-transform: capitalize;text-align: left;">Approver Groups</h6>`

                  let groups_list = approval_levels[i]["group_list"]
                  let group_html=""
                  for (group of groups_list){
                    group_html += `<div style="font-size: 15px;background: var(--primary-color);color: white;padding: 3px 10px;border-radius: 8rem;">${group}</div>`
                  }

                  string += `<div>
                  <h6 style="margin-bottom:0rem;box-shadow: rgba(0, 0, 0, 0.16) 0px 1px 4px;background: white;font-size:15px;border: 1px solid lightgray;padding:5px;border-radius:5px;display:flex;align-items:center;justify-content:start;gap:5px;" data-col="group_list">
                  ${group_html}
                  </h6></div></div>`
                }

                if(approved_by_level.length>0){
                  if(!(approval_levels[i].hasOwnProperty("user_list"))){
                    string += `<div style="border-radius: 0.5rem;padding: 10px;"><h6 style="margin-bottom: 0.5rem;font-size:13px;text-transform: capitalize;text-align: left;">Approved By</h6>`
                    for( user of approved_by_level ){
                      let user_initials = getInitials(user)
                      const targetItem = user_additional_info.find(item => item.username === user);
                      let additionalString = '';

                      if (targetItem) {
                        const { username, id, ...dataWithoutUsername } = targetItem;
                        const dataValues = Object.values(dataWithoutUsername).filter(value => value!="-" && value!="");
                        additionalString = `(${dataValues.join(' ')})`;

                      }
                      string += `<div class='d-flex align-items-center' style="margin: 6px 0;background: white;box-shadow: rgba(0, 0, 0, 0.16) 0px 1px 4px;border: 1px solid lightgray;padding: 5px;border-radius: 5px;"><span class='radio mr-2 d-flex align-items-center justify-content-center' style='height: 20px;width: 20px;background: rgba(85,163,98,1);border-radius: 50%;border: 2px solid rgb(76 148 88);'><i class="fa fa-check" style="color:white"></i></span><h5 class="created_title mb-0 mr-2 ml-2" style="width:6%;"><span>${user_initials}</span></h5><div class="name_card"><h6 style="margin-bottom:1px !important;font-size:14px;" class="text-left ml-2">${user}</h6>`
                      if(additionalString!="()" && additionalString!=""){
                        string += `<span class="ml-2" style="color: rgba(0,0,0,.55);font-size: .7rem;">${additionalString}</span></div></div>`
                      }
                      else{
                        string += `</div></div>`
                      }
                    }
                    string+=`</div>`
                  }
                }

                string+=`</div></div></div>`

                $(`#approvalWallModalBody_${elementID}`).find(`#view_at_all_levels_${elementID}`).append(string);

              }
            }



            created_by = result_data["created_by"]
            created_time = result_data["created_date"]

            var [timestamp,tooltipTimestamp] = convertToTimestamp(created_time);
            var small_time = "at" + tooltipTimestamp.split("at")[1]
            var initials = getInitials(created_by)

            const targetItem = created_user_data[0]
            let additionalString = '';

            if (targetItem) {
              const { username, ...dataWithoutUsername } = targetItem;
              const dataValues = Object.values(dataWithoutUsername).filter(value => value!="-" && value!="");
              additionalString = `(${dataValues.join(' ')})`;
            }

            var approval_type =  result_data.approval_type
            var edit_or_create = ""
            if(approval_type == "edit"){
              edit_or_create = "edited the"
            }
            else if(approval_type == "create"){
              edit_or_create = "created a new"
            }

            audit_html = `
              <div class="approval_card">
                <div class="approval_info">
                  <h5 class="approval_title"><span>${initials}</span></h5>
                  <p class="approval_text">${created_by} ${additionalString} ${edit_or_create} transaction.</p>
                  <div>
                    <h6 class="approval_timestamp" data-toggle="tooltip" title="${tooltipTimestamp}">${timestamp}</h6>
                    <small style="color: #929292;">${small_time}</small>
                  </div>
                </div>
              </div>
            `
            $(`#approvalWallModalBody_${elementID}`).find(`.approval_outer_${elementID}`).prepend(audit_html)

            $(`#approvalWallModalBody_${elementID}`).find('.created_by_info').prepend(`<h6 class="approval-created-info text-left mb-1" >${created_by} ${additionalString} ${edit_or_create} transaction on ${tooltipTimestamp}</h6>`)
            $(`#approvalWallModalBody_${elementID}`).find('.created_by_info').prepend(`<h5 class="created_title mb-0 mr-2 ml-2"><span>${initials}</span></h5>`)

            $(`#requester_details`).find(".created_title").html(`<span>${initials}</span>`)
            $(`#requester_details`).find(".approval-created-info").html(`${created_by} ${additionalString} ${edit_or_create} transaction on ${tooltipTimestamp}`)

            approval_status = result_data["approval_status"]

            if(approval_status=="Pending"){
              $(`#approvalWallModalBody_${elementID}`).find('.created_by_info').prepend(`<h6 class="created_title_status" style="background: #ffd700;width: fit-content;padding: 7px 10px;border-radius: 34px;font-size: 0.9rem;color: black;margin:0;">${approval_status}</h6>`)
              $(`#approvalWallModalBody_${elementID}`).find(`#approval_status_${elementID}`).find(".card-text").html(`<h6 class="mr-2" style="background: #ffd700;width: fit-content;padding: 7px 10px;border-radius: 34px;font-size: 0.9rem;color: black;margin:0;">${approval_status}</h6>`)
            }
            else if(approval_status == "Rejected"){
              $(`#approvalWallModalBody_${elementID}`).find('.created_by_info').prepend(`<h6 class="created_title_status" style="background: rgba(205,74,69,1);width: fit-content;padding: 7px 10px;border-radius: 34px;font-size: 0.9rem;color: white;margin:0;">${approval_status}</h6>`)
              $(`#approvalWallModalBody_${elementID}`).find(`#approval_status_${elementID}`).find(".card-text").html(`<h6 class="mr-2" style="background: rgba(205,74,69,1);width: fit-content;padding: 7px 10px;border-radius: 34px;font-size: 0.9rem;color: white;margin:0;">${approval_status}</h6>`)
            }
            else if(approval_status == "Approved"){
              $(`#approvalWallModalBody_${elementID}`).find('.created_by_info').prepend(`<h6 class="created_title_status" style="background: rgba(85,163,98,1);width: fit-content;padding: 7px 10px;border-radius: 34px;font-size: 0.9rem;color: white;margin:0;">${approval_status}</h6>`)
              $(`#approvalWallModalBody_${elementID}`).find(`#approval_status_${elementID}`).find(".card-text").html(`<h6 class="mr-2" style="background: rgba(85,163,98,1);width: fit-content;padding: 7px 10px;border-radius: 34px;font-size: 0.9rem;color: white;margin:0;">${approval_status}</h6>`)
            }

            $(`#approvalWallModalBody_${elementID}`).find(`#type_of_approval_${elementID}`).find(".card-text").text(`${type_of_approval}`)

            $(`#approvalWallModalBody_${elementID}`).find(`#approver_type_${elementID}`).find(".card-text").text(`${approver_type}`)

            $(`#approvalWallModalBody_${elementID}`).find(`#approval_code_${elementID}`).find(".card-text").text(`${approval_code}`)


            li_html = ""
            approver_user_data_list = approver_user_data_list.filter(item=> item.username != created_by)
            for(var i = 0; i < approver_user_data_list.length; i++) {
              const targetItem = user_additional_info.find(item => item.username === approver_user_data_list[i].username);
              let additionalString = '';

              if (targetItem) {
                const { username, id, ...dataWithoutUsername } = targetItem;
                const dataValues = Object.values(dataWithoutUsername).filter(value => value!="-" && value!="");
                additionalString = `(${dataValues.join(' ')})`;
              }

              if(approved_by_current_level.length > 0){
                if(approved_by_current_level.includes(approver_user_data_list[i].username)){
                  var initials = getInitials(approver_user_data_list[i].username)
                  li_html = li_html + `<li class='m-3 align-items-center li_approvers' style="display:flex"><span class='radio mr-2 d-flex align-items-center justify-content-center' style='height: 20px;width: 20px;background: rgba(85,163,98,1);border-radius: 50%;border: 2px solid rgb(76 148 88);'><i class="fa fa-check" style="color:white"></i></span><h5 class="created_title mb-0 mr-2 ml-2" style="width:6%;"><span>${initials}</span></h5><div style="text-align:left"><h6 style="margin-bottom:1px !important; padding-left: 1rem;" class='approver_${approver_user_data_list[i].username} approvers_username text-left ml-2'>${approver_user_data_list[i].username}</h6>`
                  if(additionalString!="()" && additionalString!=""){
                    li_html = li_html + `<span class="ml-2" style="color: rgba(0,0,0,.55);font-size: .7rem;padding-left: 1rem;">${additionalString}</span></div></li>`
                  }

                }
                else{
                  var initials = getInitials(approver_user_data_list[i].username)
                  li_html = li_html + `<li class='m-3 align-items-center li_approvers' style="display:flex"><span class='radio mr-2 d-flex align-items-center justify-content-center' style='height: 20px;width: 20px;background: #f4f4f4;border-radius: 50%;border: 2px solid grey;'></span><h5 class="created_title mb-0 mr-2 ml-2" style="width:6%;"><span>${initials}</span></h5><div style="text-align:left"><h6 style="margin-bottom:1px !important;padding-left: 1rem;" class='approver_${approver_user_data_list[i].username} approvers_username text-left ml-2'>${approver_user_data_list[i].username}</h6>`
                  if(additionalString!="()" && additionalString!=""){
                    li_html = li_html + `<span class="ml-2" style="color: rgba(0,0,0,.55);font-size: .7rem;padding-left: 1rem;">${additionalString}</span></div></li>`
                  }
                }
              }
              else{
                var initials = getInitials(approver_user_data_list[i].username)
                li_html = li_html + `<li class='m-3 align-items-center li_approvers' style="display:flex"><span class='radio mr-2 d-flex align-items-center justify-content-center' style='height: 20px;width: 20px;background: #f4f4f4;border-radius: 50%;border: 2px solid grey;'></span><h5 class="created_title mb-0 mr-2 ml-2" style="width:6%;"><span>${initials}</span></h5><div style="text-align:left"><h6 style="margin-bottom:1px !important;padding-left: 1rem;" class='approver_${approver_user_data_list[i].username} approvers_username text-left ml-2'>${approver_user_data_list[i].username}</h6>`
                if(additionalString!="()" && additionalString!=""){
                  li_html = li_html + `<span class="ml-2" style="color: rgba(0,0,0,.55);font-size: .7rem;padding-left: 1rem;">${additionalString}</span></div></li>`
                }
              }

            }
            $(`#approvalWallModalBody_${elementID}`).find(`#approver_users_${elementID}`).find("ul").html(li_html)

            if(allowed_edit=="true"){
              user_additional = JSON.stringify(user_additional_info)
              $(`#approvalWallModalBody_${elementID}`).find(`#edit_approvers_${elementID}`).css("display","block")
              $(`#approvalWallModalBody_${elementID}`).find(`#save_approvers_${elementID}`).css("display","none")
              $(`#approvalWallModalBody_${elementID}`).find(`#edit_approvers_${elementID}`).attr("onclick",`editApprovers(${result_data.id}, ${result_data.approver_group}, '${result_data.type_of_approval}')`)
              $(`#approvalWallModalBody_${elementID}`).find(`#save_approvers_${elementID}`).attr("onclick",`saveApprovers(${result_data.id}, ${result_data.approver_group}, ${JSON.stringify(approver_user_data_list)}, ${result_data.approval_audit_log}, '${result_data.type_of_approval}', '${result_data.approver_type}')`)
            }else{
              $(`#approvalWallModalBody_${elementID}`).find(`#edit_approvers_${elementID}`).css("display","none")
              $(`#approvalWallModalBody_${elementID}`).find(`#save_approvers_${elementID}`).css("display","none")
            }


            if(result_data.approval_audit_log){

              for(let i=0; i<audit_log_configs.length; i++){
                for (let [key, value] of Object.entries(audit_log_configs[i])) {

                  for (let j=0; j<value.length; j++) {
                    dictt = value[j]

                    var [timestamp,tooltipTimestamp] = convertToTimestamp(dictt["time"]);
                    var small_time = "at" + tooltipTimestamp.split("at")[1]
                    var initials = getInitials(dictt["user"])

                    const targetItem = user_additional_info.find(item => item.username === dictt["user"]);
                    let additionalString = '';

                    if (targetItem) {
                      const { username, id, ...dataWithoutUsername } = targetItem;
                      const dataValues = Object.values(dataWithoutUsername).filter(value => value!="-" && value!="");
                      additionalString = `(${dataValues.join(' ')})`;
                      if (additionalString="()"){
                        additionalString = ""
                      }
                    }

                    if(dictt["action"] == "Comment"){
                      let comment_status = "Active"
                      let comment_class="active_comment"
                      let all_comments_status = ""
                      all_comments_status = dictt["all_comments_status"]
                      let reopen_button_attr, reopen_button_style, resolve_button_attr, resolve_button_style, card_background, reply_display

                      if (all_comments_status == "resolved_for_all"){
                        all_comments_resolved = true

                        resolve_button_attr = "disabled"
                        resolve_button_style = "display:none;"

                        card_background = "background:#f8f8f8;"
                        comment_status = "Resolved"
                        reply_display = "display:none;"
                        comment_class="resolved_comment"

                        reopen_button_attr = "disabled"
                        reopen_button_style = "display:none;"

                        if(reopen_individual_comments  && (allowed_approval=="true" || allowed_rejection=="true" || allowed_edit=="true")){
                          reopen_button_attr = ""
                          reopen_button_style = "display:block;"
                        }

                      }
                      else{
                        all_comments_resolved = false
                      }

                      if(all_comments_status == "reopened_for_all"){
                        all_comments_reopened = true
                        card_background = "background:#ffffff;"
                        comment_status = "Reopened"
                        reply_display = "display:block;"
                        comment_class="reopened_comment"

                        reopen_button_attr = "disabled"
                        reopen_button_style = "display:none;"

                        resolve_button_attr = "disabled"
                        resolve_button_style = "display:none;"

                        if(resolve_individual_comments  && (allowed_approval=="true" || allowed_rejection=="true" || allowed_edit=="true")){
                          resolve_button_attr = ""
                          resolve_button_style = "display:block;"
                        }
                      }
                      else{
                        all_comments_reopened = false
                      }

                      let individual_comment_status = ""
                      individual_comment_status = dictt["individual_comment_status"]

                      if( individual_comment_status == "resolved_individual_comment"){
                        if(!resolved_ind_comments_list.includes(`${i}${j}`) ){
                          resolved_ind_comments_list.push(`${i}${j}`)
                        }

                        resolve_button_attr = "disabled"
                        resolve_button_style = "display:none;"
                        card_background = "background:#f8f8f8;"
                        comment_status = "Resolved"
                        reply_display = "display:none;"
                        comment_class="resolved_comment"

                        reopen_button_attr = "disabled"
                        reopen_button_style = "display:none;"

                        if(reopen_individual_comments && (allowed_approval=="true" || allowed_rejection=="true" || allowed_edit=="true")){
                          reopen_button_attr = ""
                          reopen_button_style = "display:block;"
                        }
                      }
                      else if (individual_comment_status == "reopened_individual_comment"){

                        value_index = resolved_ind_comments_list.indexOf(`${i}${j}`)
                        resolved_ind_comments_list.splice(value_index,1)

                        card_background = "background:#ffffff;"
                        comment_status = "Reopened"
                        reply_display = "display:block;"
                        comment_class="reopened_comment"

                        reopen_button_attr = "disabled"
                        reopen_button_style = "display:none;"

                        resolve_button_attr = "disabled"
                        resolve_button_style = "display:none;"

                        if(resolve_individual_comments  && (allowed_approval=="true" || allowed_rejection=="true" || allowed_edit=="true")){
                          resolve_button_attr = ""
                          resolve_button_style = "display:block;"
                        }
                      }


                      if(all_comments_status === undefined && individual_comment_status===undefined){
                        card_background = "background:#ffffff;"
                        comment_status = "Active"
                        reply_display = "display:block;"
                        comment_class="active_comment"

                        reopen_button_attr = "disabled"
                        reopen_button_style = "display:none;"

                        resolve_button_attr = "disabled"
                        resolve_button_style = "display:none;"

                        if(resolve_individual_comments  && (allowed_approval=="true" || allowed_rejection=="true" || allowed_edit=="true")){
                          resolve_button_attr = ""
                          resolve_button_style = "display:block;"
                        }
                        resolved_ind_comments_list = []
                      }


                      audit_html = `
                      <div>

                        <div class="approval_card approval_comment" style="${card_background}">
                          <div class="" style="margin: 0px 20px 5px 7px;">
                            <button class="btn btn-primary mb-2 resolve_button_ind" id="resolve_button_ind_${i}${j}" ${resolve_button_attr} onclick="resolveIndComments('${i}','${j}','Level ${current_level}','${result_data.id}', '${smtpConfigKey}', '${app_code}')" style="font-size: 0.7rem;float:left;${resolve_button_style}"> Mark as Resolved </button>
                            <button class="btn btn-primary mb-2 reopen_button_ind" id="reopen_button_ind_${i}${j}" ${reopen_button_attr} onclick="reopenIndComments('${i}','${j}','Level ${current_level}','${result_data.id}', '${smtpConfigKey}', '${app_code}')" style="font-size: 0.7rem;float:left;${reopen_button_style}"> Mark as Reopened </button>
                            <h5 class="comment_status_ind ${comment_class}" id="comment_status_ind_${i}${j}" style="font-size: 0.8rem;font-weight: normal;float:right;">Status: <b>${comment_status}</b></h5>
                          </div>
                          <div id="approval_comment_${i}${j}">
                            <div class="approval_comment_card">
                              <div class="approval_info">
                                <h5 class="approval_title"><span>${initials}</span></h5>
                                <p class="approval_text">${dictt["user"]} ${additionalString} sent a comment</p>
                              <div>
                              <h6 class="approval_timestamp" data-toggle="tooltip" title="${tooltipTimestamp}">${timestamp}</h6>
                              <small style="color: #929292;">${small_time}</small>
                            </div>
                          </div>
                          <div class="approval_comment_text"><p>${dictt["value"].replaceAll("\\t", "&nbsp;").replaceAll("\\n", "<br>")}</p></div>
                        </div>
                      `

                      if (dictt.hasOwnProperty("replies")) {
                        replies = dictt["replies"]

                        for(let k=0; k<replies.length;k++){
                          var [reply_timestamp,reply_tooltipTimestamp] = convertToTimestamp(replies[k]["time"]);
                          var reply_initials = getInitials(replies[k]["user"])
                          audit_html = audit_html + `
                          <div class="reply_comment_card approval_comment_card">
                            <div class="approval_info">
                              <h5 class="approval_title"><span>${reply_initials}</span></h5>
                              <p class="approval_text">${replies[k]["user"]} ${additionalString} replied</p>
                              <div>
                                <h6 class="approval_timestamp" data-toggle="tooltip" title="${reply_tooltipTimestamp}">${reply_timestamp}</h6>
                                <small style="color: #929292;">${small_time}</small>
                              </div>
                            </div>
                            <div class="approval_comment_text"><p>${replies[k]["value"].replaceAll("\\t", "&nbsp;").replaceAll("\\n", "<br>")}</p></div>
                          </div>`
                        }
                      }

                      audit_html = audit_html + `</div><div class="reply-area mt-3" style="${reply_display}">
                            <textarea id="replycomment_${i}${j}" name="replycomment_${i}${j}"></textarea>
                            <div style="margin: 15px 0 5px 0;text-align: right;display: flex;align-items: center;justify-content: flex-end;">
                              <button class="btn btn-primary reply_comments" style="font-size:0.9rem;" disabled data-toggle="tooltip" title="Click this button or press Ctrl+Enter" id="replybutton_${i}${j}" onclick="ReplyToComment('${i}','${j}','${key}','${result_data.id}', '${smtpConfigKey}', '${app_code}')">Reply <i class="fa-solid fa-comment-dots ml-2"></i></button>
                            </div>
                          </div>
                        </div>
                      </div>`

                      $(`#approvalWallModalBody_${elementID}`).find(`.approval_outer_${elementID}`).prepend(audit_html)


                        reply_editor = CKEDITOR.replace(`replycomment_${i}${j}`,
                        {
                          height: 44,
                          removeButtons: home_rtf[0],
                          editorplaceholder: "Type your reply here..." ,
                          plugins: 'mentions,undo,link,list,basicstyles,justify,richcombo,wysiwygarea,toolbar',
                          extraPlugins: 'elementspath,editorplaceholder',
                          toolbar: [
                            { name: 'document', items: ['Undo'] },
                            { name: 'paragraph', items: ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'] },
                            { name: 'basicstyles', items: ['Bold', 'Italic', 'Underline', 'Strike', '-', 'RemoveFormat'] },
                            { name: 'links', items: ['Mention', 'Link', 'Unlink', 'Anchor'] },
                            { name: 'styles', items: ['Styles', 'Format', 'Font', 'FontSize'] },
                            { name: 'colors', items: ['TextColor', 'BGColor'] },
                            { name: 'elementspath', items: ['ElementPath'] }
                          ],
                          mentions: [
                            {
                              feed: dataFeed,
                              itemTemplate: itemTemplate,
                              outputTemplate: outputTemplate,
                              minChars: 0
                            }
                          ],
                          removeButtons: 'PasteFromWord'

                        });
                        CKEDITOR.config.removePlugins = 'exportpdf';
                        CKEDITOR.config.extraPlugins = 'autocorrect,elementspath';

                        reply_editor = CKEDITOR.instances[`replycomment_${i}${j}`]
                        reply_editor.on('change',function(){
                          let typedText = reply_editor.getData();
                          if(typedText.trim() === ''){
                            $(`#replybutton_${i}${j}`).prop("disabled",true)
                          }
                          else{
                            $(`#replybutton_${i}${j}`).prop("disabled",false)
                          }
                        })

                        reply_editor.on('key',function(event){
                          if (event.data.keyCode === CKEDITOR.CTRL + 13){
                            $(`#replybutton_${i}${j}`).trigger("click")
                          }
                        })

                        for(var editorId in CKEDITOR.instances){
                          if(editorId.indexOf('replycomment_') === 0){
                            CKEDITOR.instances[editorId].setData('')
                          }
                        }


                    }
                    else if(dictt["action"] == "Mention"){
                      let comment_status = "Active"
                      let comment_class="active_comment"
                      let all_comments_status = ""
                      all_comments_status = dictt["all_comments_status"]
                      let reopen_button_attr, reopen_button_style, resolve_button_attr, resolve_button_style, card_background, reply_display

                      if (all_comments_status == "resolved_for_all"){
                        all_comments_resolved = true

                        resolve_button_attr = "disabled"
                        resolve_button_style = "display:none;"

                        card_background = "background:#f8f8f8;"
                        comment_status = "Resolved"
                        reply_display = "display:none;"
                        comment_class="resolved_comment"

                        reopen_button_attr = "disabled"
                        reopen_button_style = "display:none;"

                        if(reopen_individual_comments  && (allowed_approval=="true" || allowed_rejection=="true" || allowed_edit=="true")){
                          reopen_button_attr = ""
                          reopen_button_style = "display:block;"
                        }

                      }
                      else{
                        all_comments_resolved = false
                      }

                      if(all_comments_status == "reopened_for_all"){
                        all_comments_reopened = true
                        card_background = "background:#ffffff;"
                        comment_status = "Reopened"
                        reply_display = "display:block;"
                        comment_class="reopened_comment"

                        reopen_button_attr = "disabled"
                        reopen_button_style = "display:none;"

                        resolve_button_attr = "disabled"
                        resolve_button_style = "display:none;"

                        if(resolve_individual_comments  && (allowed_approval=="true" || allowed_rejection=="true" || allowed_edit=="true")){
                          resolve_button_attr = ""
                          resolve_button_style = "display:block;"
                        }
                      }
                      else{
                        all_comments_reopened = false
                      }

                      let individual_comment_status = ""
                      individual_comment_status = dictt["individual_comment_status"]

                      if( individual_comment_status == "resolved_individual_comment"){
                        if(!resolved_ind_comments_list.includes(`${i}${j}`) ){
                          resolved_ind_comments_list.push(`${i}${j}`)
                        }

                        resolve_button_attr = "disabled"
                        resolve_button_style = "display:none;"
                        card_background = "background:#f8f8f8;"
                        comment_status = "Resolved"
                        reply_display = "display:none;"
                        comment_class="resolved_comment"

                        reopen_button_attr = "disabled"
                        reopen_button_style = "display:none;"

                        if(reopen_individual_comments && (allowed_approval=="true" || allowed_rejection=="true" || allowed_edit=="true")){
                          reopen_button_attr = ""
                          reopen_button_style = "display:block;"
                        }
                      }
                      else if (individual_comment_status == "reopened_individual_comment"){

                        value_index = resolved_ind_comments_list.indexOf(`${i}${j}`)
                        resolved_ind_comments_list.splice(value_index,1)

                        card_background = "background:#ffffff;"
                        comment_status = "Reopened"
                        reply_display = "display:block;"
                        comment_class="reopened_comment"

                        reopen_button_attr = "disabled"
                        reopen_button_style = "display:none;"

                        resolve_button_attr = "disabled"
                        resolve_button_style = "display:none;"

                        if(resolve_individual_comments  && (allowed_approval=="true" || allowed_rejection=="true" || allowed_edit=="true")){
                          resolve_button_attr = ""
                          resolve_button_style = "display:block;"
                        }
                      }


                      if(all_comments_status === undefined && individual_comment_status===undefined){
                        card_background = "background:#ffffff;"
                        comment_status = "Active"
                        reply_display = "display:block;"
                        comment_class="active_comment"

                        reopen_button_attr = "disabled"
                        reopen_button_style = "display:none;"

                        if(resolve_individual_comments  && (allowed_approval=="true" || allowed_rejection=="true" || allowed_edit=="true")){
                          resolve_button_attr = ""
                          resolve_button_style = "display:block;"
                        }
                        resolved_ind_comments_list = []
                      }


                      audit_html = `
                      <div>

                        <div class="approval_card approval_comment" style="${card_background}">
                          <div class="" style="margin:0 20px 20px 7px;">
                            <button class="btn btn-primary mb-2 resolve_button_ind" id="resolve_button_ind_${i}${j}" ${resolve_button_attr} onclick="resolveIndComments('${i}','${j}','Level ${current_level}','${result_data.id}', '${smtpConfigKey}', '${app_code}')" style="font-size: 0.7rem;float:left;${resolve_button_style}"> Mark as Resolved </button>
                            <button class="btn btn-primary mb-2 reopen_button_ind" id="reopen_button_ind_${i}${j}" ${reopen_button_attr} onclick="reopenIndComments('${i}','${j}','Level ${current_level}','${result_data.id}', '${smtpConfigKey}', '${app_code}')" style="font-size: 0.7rem;float:left;${reopen_button_style}"> Mark as Reopened </button>
                            <h5 class="comment_status_ind ${comment_class}" id="comment_status_ind_${i}${j}" style="font-size: 0.8rem;font-weight: normal;float:right;">Status: <b>${comment_status}</b></h5>
                          </div>
                          <div id="approval_comment_${i}${j}">
                            <div class="approval_comment_card">
                              <div class="approval_info">
                                <h5 class="approval_title"><span>${initials}</span></h5>
                                <p class="approval_text">${dictt["user"]} ${additionalString} mentioned</p>
                                <div>
                                  <h6 class="approval_timestamp" data-toggle="tooltip" title="${tooltipTimestamp}">${timestamp}</h6>
                                  <small style="color: #929292;">${small_time}</small>
                                </div>
                              </div>
                              <div class="approval_comment_text"><p>${dictt["value"].replaceAll("\\t", "&nbsp;").replaceAll("\\n", "<br>")}</p></div>
                            </div>`

                        if (dictt.hasOwnProperty("replies")) {
                          replies = dictt["replies"]
                          for(let k=0; k<replies.length;k++){
                            var [reply_timestamp,reply_tooltipTimestamp] = convertToTimestamp(replies[k]["time"]);
                            let small_time = "at" + reply_tooltipTimestamp.split("at")[1]
                            var reply_initials = getInitials(replies[k]["user"])
                            audit_html = audit_html + `
                            <div class="reply_comment_card approval_comment_card">
                              <div class="approval_info">
                                <h5 class="approval_title"><span>${reply_initials}</span></h5>
                                <p class="approval_text">${replies[k]["user"]} ${additionalString} replied</p>
                                <div>
                                  <h6 class="approval_timestamp" data-toggle="tooltip" title="${reply_tooltipTimestamp}">${reply_timestamp}</h6>
                                  <small style="color: #929292;">${small_time}</small>
                                </div>
                              </div>
                              <div class="approval_comment_text"><p>${replies[k]["value"].replaceAll("\\t", "&nbsp;").replaceAll("\\n", "<br>")}</p></div>
                            </div>`
                          }
                        }


                            audit_html = audit_html + `</div><div class="reply-area mt-3" >

                            <textarea id="replycomment_${i}${j}" name="replycomment_${i}${j}"></textarea>
                            <div style="margin: 15px 0 5px 0;text-align: right;display: flex;align-items: center;justify-content: flex-end;">
                              <button class="btn btn-primary reply_comments" style="font-size:0.9rem;" disabled data-toggle="tooltip" title="Click this button or press Ctrl+Enter" id="replybutton_${i}${j}" onclick="ReplyToComment('${i}','${j}','${key}','${result_data.id}', '${smtpConfigKey}', '${app_code}')">Reply <i class="fa-solid fa-comment-dots ml-2"></i></button>
                            </div>
                          </div>
                        </div>
                      </div>
                      `

                      $(`#approvalWallModalBody_${elementID}`).find(`.approval_outer_${elementID}`).prepend(audit_html)


                        reply_editor1 = CKEDITOR.replace(`replycomment_${i}${j}`,
                        {
                          height: 44,
                          removeButtons: home_rtf[0],
                          editorplaceholder: 'Add a comment...',
                          plugins: 'mentions,undo,link,list,basicstyles,justify,richcombo,wysiwygarea,toolbar',
                          extraPlugins: 'elementspath,editorplaceholder',
                          toolbar: [
                            { name: 'document', items: ['Undo'] },
                            { name: 'paragraph', items: ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'] },
                            { name: 'basicstyles', items: ['Bold', 'Italic', 'Underline', 'Strike', '-', 'RemoveFormat'] },
                            { name: 'links', items: ['Mention', 'Link', 'Unlink', 'Anchor'] },
                            { name: 'styles', items: ['Styles', 'Format', 'Font', 'FontSize'] },
                            { name: 'colors', items: ['TextColor', 'BGColor'] },
                            { name: 'elementspath', items: ['ElementPath'] }
                          ],
                          mentions: [
                            {
                              feed: dataFeed,
                              itemTemplate: itemTemplate,
                              outputTemplate: outputTemplate,
                              minChars: 0
                            }
                          ],
                          removeButtons: 'PasteFromWord'
                        });

                        CKEDITOR.config.removePlugins = 'exportpdf';
                        CKEDITOR.config.extraPlugins = 'autocorrect,elementspath';

                        reply_editor1 = CKEDITOR.instances[`replycomment_${i}${j}`]
                        reply_editor1.on('change',function(){
                          let typedText = reply_editor1.getData();
                          if(typedText.trim() === ''){
                            $(`#replybutton_${i}${j}`).prop("disabled",true)
                          }
                          else{
                            $(`#replybutton_${i}${j}`).prop("disabled",false)
                          }
                        })

                        reply_editor1.on('key',function(event){
                          if (event.data.keyCode === CKEDITOR.CTRL + 13){
                            $(`#replybutton_${i}${j}`).trigger("click")
                          }
                        })

                        for(var editorId in CKEDITOR.instances){
                          if(editorId.indexOf('replycomment_') === 0){
                            CKEDITOR.instances[editorId].setData('')
                          }
                        }

                    }
                    else if(dictt["action"] == "Delegated Approval Actions"){
                      audit_html = `
                        <div class="approval_card">
                          <div class="approval_info">
                            <h5 class="approval_title"><span>${initials}</span></h5>
                            <p class="approval_text"> ${dictt["user"]} ${additionalString} ${dictt["value"]} </p>
                            <div>
                              <h6 class="approval_timestamp" data-toggle="tooltip" title="${tooltipTimestamp}">${timestamp}</h6>
                              <small style="color: #929292;">${small_time}</small>
                            </div>
                          </div>
                        </div>
                      `
                      $(`#approvalWallModalBody_${elementID}`).find(`.approval_outer_${elementID}`).prepend(audit_html)
                    }
                    else if (dictt["action"] == "Approved By"){
                      audit_html = `
                      <div class="approval_card">
                        <div class="approval_info">
                          <h5 class="approval_title approved_title">
                            <span class="radio d-flex align-items-center justify-content-center" style="height: 30px;width: 30px;background: rgba(85,163,98,1);border-radius: 50%;border: 2px solid rgb(76 148 88);"><i class="fa fa-check" style="color:white"></i></span>
                            <span class="ml-2">${initials}</span>
                          </h5>
                          <p class="approval_text text-approved">${dictt["user"]} ${additionalString} approved the transaction.</p>
                          <div>
                            <h6 class="approval_timestamp" data-toggle="tooltip" title="${tooltipTimestamp}">${timestamp}</h6>
                            <small style="color: #929292;">${small_time}</small>
                          </div>
                        </div>
                      </div>
                    `
                    $(`#approvalWallModalBody_${elementID}`).find(`.approval_outer_${elementID}`).prepend(audit_html)
                    }
                    else if (dictt["action"] == "Rejected By"){
                      audit_html = `
                      <div class="approval_card">
                        <div class="approval_info">
                          <h5 class="approval_title approved_title">
                            <span class="radio d-flex align-items-center justify-content-center" style="height: 30px;width: 30px;background: rgba(205,74,69,1);border-radius: 50%;border: 2px solid rgba(205,74,69,1);"><i class="fa fa-times" style="color:white"></i></span>
                            <span class="ml-2">${initials}</span>
                          </h5>
                          <p class="approval_text text-rejected">${dictt["user"]} ${additionalString} rejected the transaction.</p>
                          <div>
                            <h6 class="approval_timestamp" data-toggle="tooltip" title="${tooltipTimestamp}">${timestamp}</h6>
                            <small style="color: #929292;">${small_time}</small>
                          </div>
                        </div>
                      </div>
                    `
                    $(`#approvalWallModalBody_${elementID}`).find(`.approval_outer_${elementID}`).prepend(audit_html)
                    }
                    else if (dictt["action"] == "Edited By"){
                      var htmlString = '';
                      v = dictt["value"]
                      if (v && v.constructor !== Array) {
                        if (v.indexOf(" from ") != -1 && v.indexOf(" to ") != -1) {
                          var fromIndex = v.indexOf("from ");
                          var toIndex = v.indexOf(" to ");
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
                                    if(valLevel[jLevel] in user_additional_info){
                                      tmp.push(user_additional_info[valLevel[jLevel]])
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
                                    if(valLevel[jLevel] in user_additional_info){
                                      tmp.push(user_additional_info[valLevel[jLevel]])
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
                            var fromHTML = fromContent.replaceAll("\\'","");
                            var toHTML = toContent.replaceAll("\\'","");
                          }
                          htmlString = `<div style="padding: 10px 35px;"><p style="text-align:center;margin-bottom:0;font-weight: 600;">From</p><p style="word-break:break-word;">${fromHTML}</p><p style="text-align:center;margin-bottom:0;font-weight: 600;">To</p><p style="word-break:break-word;">${toHTML}</p></div>`;
                        }
                      }

                      column = dictt["value"].split("column")[0]
                      audit_html = `
                        <div class="approval_card edited_content number${j}">
                          <div class="approval_info">
                            <h5 class="approval_title"><span>${initials}</span></h5>
                            <p class="approval_text">${dictt["user"]} ${additionalString} updated the ${column} column. </p>
                            <div>
                              <h6 class="approval_timestamp" data-toggle="tooltip" title="${tooltipTimestamp}">${timestamp}</h6>
                              <small style="color: #929292;">${small_time}</small>
                            </div>
                          </div>
                          <div>
                            ${htmlString}
                          </div>
                        </div>
                      `
                      $(`#approvalWallModalBody_${elementID}`).find(`.approval_outer_${elementID}`).prepend(audit_html)

                      var table = $(`#approvalWallModalBody_${elementID}`).find(`.approval_outer_${elementID}`).find(".edited_content").eq(0).find("table").DataTable(
                        {
                          autoWidth: true,
                          scrollCollapse: true,
                          responsive: true,
                          scrollY: '50vh',
                          bLengthChange: false,
                          searching: false,
                          info: false,
                          paging: false,
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
                    else if (dictt["action"] == "Resent Back To Previous Approver"){
                      let resendInitials = getInitials(dictt["user"])
                      previous_approver = ""
                      if(dictt["value"]){
                        previous_approver = dictt["value"].join(",")
                      }

                      audit_html = `
                      <div class="approval_card">
                        <div class="approval_info">
                          <h5 class="approval_title"><span>${resendInitials}</span></h5>
                          <p class="approval_text">${dictt["user"]} ${additionalString} has sent this transaction back to the previous approver ${previous_approver}</p>
                          <div>
                            <h6 class="approval_timestamp" data-toggle="tooltip" title="${tooltipTimestamp}">${timestamp}</h6>
                            <small style="color: #929292;">${small_time}</small>
                          </div>
                        </div>
                      </div>
                      `
                      $(`#approvalWallModalBody_${elementID}`).find(`.approval_outer_${elementID}`).prepend(audit_html)
                    }
                    else{
                      audit_html = `
                      <div class="approval_card">
                        <div class="approval_info">
                          <h5 class="approval_title"><span>${initials}</span></h5>
                          <p class="approval_text">${dictt["action"]} ${dictt["user"]} ${additionalString}</p>
                          <div>
                            <h6 class="approval_timestamp" data-toggle="tooltip" title="${tooltipTimestamp}">${timestamp}</h6>
                            <small style="color: #929292;">${small_time}</small>
                          </div>
                        </div>
                      </div>
                    `
                    $(`#approvalWallModalBody_${elementID}`).find(`.approval_outer_${elementID}`).prepend(audit_html)
                    }

                  }
                }
              }
            }


            expand_rollup_comments('approvalWallModalBody_')

            $(document).ready(function(){

              var mobile_media = window.matchMedia("(max-width: 500px)")
              if (mobile_media.matches){

                if($(`#level_config_${elementID}`).parent().is($(".lower-container"))){
                  $(`#level_config_${elementID}`).insertAfter(".div_transaction")
                }

                if($(`#approver_users_${elementID}`).parent().is($(".lower-container"))){
                  $(`#approver_users_${elementID}`).insertAfter(".div_transaction")
                }


                if(! $(`#add_levels_div_${elementID}`).parent().is($(".mobile_level_buttons")) ){
                  $(`#add_levels_div_${elementID}`).appendTo(".mobile_level_buttons")
                }

                if(! $(`#edit_approval_levels_${elementID}`).parent().is($(".mobile_level_buttons")) ){
                  $(`#edit_approval_levels_${elementID}`).appendTo(".mobile_level_buttons")
                }

                if(! $(`#save_approval_levels_${elementID}`).parent().is($(".mobile_level_buttons")) ){
                  $(`#save_approval_levels_${elementID}`).appendTo(".mobile_level_buttons")
                }

                if(!$(`#save_approvers_${elementID}`).parent().is($(".mobile_approver_buttons")) ){
                  $(`#save_approvers_${elementID}`).appendTo(".mobile_approver_buttons")
                }

                if(!$(`#edit_approvers_${elementID}`).parent().is($(".mobile_approver_buttons")) ){
                  $(`#edit_approvers_${elementID}`).appendTo(".mobile_approver_buttons")
                }

                if(!$(`#edit_transaction_data_${elementID}`).parent().is($(".mobile_transaction_buttons")) ){
                  $(`#edit_transaction_data_${elementID}`).appendTo(".mobile_transaction_buttons")
                }

                if(!$(`#save_transaction_data_${elementID}`).parent().is($(".mobile_transaction_buttons")) ){
                  $(`#save_transaction_data_${elementID}`).appendTo(".mobile_transaction_buttons")
                }

                if($(".additional_accordion").parent().is($(".upper-container"))){
                  $(".mobile-additional-accordion").empty()
                  $(".mobile-additional-accordion").append($(".additional_accordion"))
                }

                $(".mobile_level_accordion_arrow").off("click").on("click", function(){
                  let target = $(this).attr("data-target")
                  if($(`.${target}`).css("display") == "none"){
                    $(`.${target}`).slideDown()
                    $(this).find("i").attr("class","fas fa-chevron-up")
                  }
                  else{
                    $(`.${target}`).slideUp()
                    $(this).find("i").attr("class","fas fa-chevron-down")
                  }
                })

              }

            })

            $(".closeApprovalWall").on('click', function(){

              var modalElement = document.querySelector(".approvalWallModal");

              for(var instanceName in CKEDITOR.instances){
                if(CKEDITOR.instances.hasOwnProperty(instanceName)){
                  var editorElement = modalElement.querySelector("#"+instanceName)

                  if(editorElement){
                    CKEDITOR.instances[instanceName].destroy()
                  }
                }
              }

              $(`#approvalWallModal_${elementID}`).modal('hide')
            })

            if(all_comments_resolved){
              $(`#approvalWallModalBody_${elementID}`).find(`#resolve_all_button_${elementID}`).attr("disabled",true)
              $(`#approvalWallModalBody_${elementID}`).find(`#resolve_all_button_${elementID}`).css("display","none")
              $(`#approvalWallModalBody_${elementID}`).find(`.new_discussion_${elementID}`).css("display","none")
              $(`#approvalWallModalBody_${elementID}`).find(`.approval_outer_${elementID}`).addClass("mt-5 mb-3")
              $(`#approvalWallModalBody_${elementID}`).find(`#comment_status${elementID}`).html("Status: <b>Resolved</b>")
              $(`#approvalWallModalBody_${elementID}`).find(`#comment_status${elementID}`).attr("class","resolved_comment")
              $(`#approvalWallModalBody_${elementID}`).find(`#add_comment_${elementID}`).css('display', 'none')


              if(reopen_all_comments && (allowed_approval=="true" || allowed_rejection=="true" || allowed_edit=="true")){
                $(`#approvalWallModalBody_${elementID}`).find(`#reopen_all_button_${elementID}`).css("display","block")
                $(`#approvalWallModalBody_${elementID}`).find(`#reopen_all_button_${elementID}`).attr("disabled",false)

              }
              else{
                $(`#approvalWallModalBody_${elementID}`).find(`#reopen_all_button_${elementID}`).css("display","none")
              }

            }
            else if(all_comments_reopened){
              $(`#approvalWallModalBody_${elementID}`).find(`#reopen_all_button_${elementID}`).attr("disabled",true)
              $(`#approvalWallModalBody_${elementID}`).find(`#reopen_all_button_${elementID}`).css("display","none")
              $(`#approvalWallModalBody_${elementID}`).find(`.new_discussion_${elementID}`).css("display","flex")
              $(`#approvalWallModalBody_${elementID}`).find(`.new_discussion_${elementID}`).addClass("mt-5 mb-3")
              $(`#approvalWallModalBody_${elementID}`).find(`.approval_outer_${elementID}`).removeClass("mt-5 mb-3")
              $(`#approvalWallModalBody_${elementID}`).find(`#comment_status${elementID}`).html("Status: <b>Reopened</b>")
              $(`#approvalWallModalBody_${elementID}`).find(`#comment_status${elementID}`).attr("class","reopened_comment")
              $(`#approvalWallModalBody_${elementID}`).find(`#add_comment_${elementID}`).css('display', 'block')

              if(resolve_all_comments === true && (allowed_approval=="true" || allowed_rejection=="true" || allowed_edit=="true")){

                $(`#approvalWallModalBody_${elementID}`).find(`#resolve_all_button_${elementID}`).css("display","block")
                $(`#approvalWallModalBody_${elementID}`).find(`#resolve_all_button_${elementID}`).attr("disabled",false)
              }
              else{
                $(`#approvalWallModalBody_${elementID}`).find(`#resolve_all_button_${elementID}`).css("display","none")
              }

            }

            if (!all_comments_resolved && !all_comments_reopened){

              if(resolve_all_comments === true && (allowed_approval=="true" || allowed_rejection=="true" || allowed_edit=="true")){

                $(`#approvalWallModalBody_${elementID}`).find(`#resolve_all_button_${elementID}`).css("display","block")
                $(`#approvalWallModalBody_${elementID}`).find(`#resolve_all_button_${elementID}`).attr("disabled",false)
              }
              else{
                $(`#approvalWallModalBody_${elementID}`).find(`#resolve_all_button_${elementID}`).css("display","none")
              }

              $(`#approvalWallModalBody_${elementID}`).find(`.new_discussion_${elementID}`).css("display","flex")
              $(`#approvalWallModalBody_${elementID}`).find(`.new_discussion_${elementID}`).addClass("mt-5 mb-3")
              $(`#approvalWallModalBody_${elementID}`).find(`.approval_outer_${elementID}`).removeClass("mt-5 mb-3")
              $(`#approvalWallModalBody_${elementID}`).find(`#comment_status${elementID}`).html("Status: <b>Active</b>")
              $(`#approvalWallModalBody_${elementID}`).find(`#comment_status${elementID}`).attr("class","active_comment")
              $(`#approvalWallModalBody_${elementID}`).find(`#add_comment_${elementID}`).css('display', 'block')
              $(`#approvalWallModalBody_${elementID}`).find(`.reply_comments`).css('display', 'block')
              $(`#approvalWallModalBody_${elementID}`).find(`.approval_comment`).css('background', "#ffffff")

            }


            if(reopen_all_comments && all_comments_resolved){
              if(allowed_approval=="true" || allowed_edit == "true" || allowed_rejection=="true"){
                $(`#approvalWallModalBody_${elementID}`).find(`#reopen_all_button_${elementID}`).css("display","block")
                $(`#approvalWallModalBody_${elementID}`).find(`#reopen_all_button_${elementID}`).attr("disabled",false)
              }
              else{
                $(`#approvalWallModalBody_${elementID}`).find(`#reopen_all_button_${elementID}`).css("display","none")
              }
            }
            else{
              $(`#approvalWallModalBody_${elementID}`).find(`#reopen_all_button_${elementID}`).css("display","none")
            }

            if(freeze_comments_option){

              $(`#approvalWallModalBody_${elementID}`).find(`#resolve_all_button_${elementID}`).attr("disabled",true)
              $(`#approvalWallModalBody_${elementID}`).find(`#resolve_all_button_${elementID}`).css("display","none")
              $(`#approvalWallModalBody_${elementID}`).find(`.new_discussion_${elementID}`).css("display","none")
              $(`#approvalWallModalBody_${elementID}`).find(`.approval_outer_${elementID}`).addClass("mt-5 mb-3")
              $(`#approvalWallModalBody_${elementID}`).find(`#comment_status${elementID}`).html("")
              $(`#approvalWallModalBody_${elementID}`).find(`#comment_status${elementID}`).attr("class","")
              $(`#approvalWallModalBody_${elementID}`).find(`#add_comment_${elementID}`).css('display', 'none')
              $(`#approvalWallModalBody_${elementID}`).find(`.reply_comments`).css('display', 'none')
              $(`#approvalWallModalBody_${elementID}`).find(`.reply-area`).css('display', 'none')
              $(`#approvalWallModalBody_${elementID}`).find(`.approval_comment`).css('background', "#f8f8f8")
              $(`#approvalWallModalBody_${elementID}`).find(`.comment_status_ind`).html("")
              $(`#approvalWallModalBody_${elementID}`).find(`.comment_status_ind`).attr("class","comment_status_ind")

            }



            //approval wall show
            $(`#approvalWallModal_${elementID}`).modal('show');



            $(`#add_comment_${elementID}`).off('click').on('click', function(){
              approval_comment = CKEDITOR.instances[`approvalWallCommentText_${elementID}`].getData()
              if (approval_comment) {
                var usernamesArray = []
                // Regular expression to match mentions (assuming mentions are like @username)
                var mentionPattern = /@(\w+)/g;
                var matches = approval_comment.match(mentionPattern);

                if (matches) {
                  // Create a Set ato store unique usernames
                  var uniqueUsernames = new Set();

                  // Extract usernames and add to the Set
                  matches.forEach(function(match) {
                    uniqueUsernames.add(match.substr(1)); // Remove the "@" symbol
                  });

                  // Convert Set to an array and display the mentioned usernames
                  usernamesArray = Array.from(uniqueUsernames);
                }

                $.ajax({
                  url: `/users/${urlPath}/approval_table/`,
                  data: {
                    "approval_id": result_data.id,
                    "current_level":current_level,
                    'operation': 'add_comment',
                    'audit_log_configs':JSON.stringify(audit_log_configs),
                    "approval_comment":approval_comment,
                    "mentioned_usernames":JSON.stringify(usernamesArray),
                    "smtpConfigKey": smtpConfigKey,
                    "app_code": app_code,
                  },
                  type: "POST",
                  dataType: "json",
                  success: function (data) {
                    var count = audit_log_configs.length
                    all_audit_data = JSON.parse(data["all_audit_data"])
                    audit_log_configs.push(all_audit_data[count])
                    CKEDITOR.instances[`approvalWallCommentText_${elementID}`].setData('');
                    temp_log = data
                    if(approval_audit_log_button){
                      approval_audit_log_button.attr("data-data",data["all_audit_data"])
                    }
                    var [timestamp,tooltipTimestamp] = convertToTimestamp(temp_log["time"]);
                    var small_time = "at" + tooltipTimestamp.split("at")[1]
                    var initials = getInitials(temp_log["user"])
                    audit_html = `
                    <div>

                      <div class="approval_card approval_comment">
                        <div class="" style="margin: 0 20px 20px 7px;">
                          <button class="btn btn-primary mb-2 resolve_button_ind" id="resolve_button_ind_${count}0" onclick="resolveIndComments('${count}','0','Level ${current_level}','${result_data.id}', '${smtpConfigKey}', '${app_code}')" style="font-size: 0.7rem;float:left;"> Mark as Resolved </button>
                          <button class="btn btn-primary mb-2 reopen_button_ind" id="reopen_button_ind_${count}0" style="display: none;font-size: 0.7rem;float:left;" onclick="reopenIndComments('${count}','0','Level ${current_level}','${result_data.id}', '${smtpConfigKey}', '${app_code}')"> Mark as Reopened </button>
                          <h5 class="comment_status_ind active_comment" id="comment_status_ind_${count}0" style="float:right;font-size: 0.8rem;font-weight: normal;">Status: <b>Active</b></h5>
                        </div>

                        <div id="approval_comment_${count}0">
                          <div class="approval_comment_card">
                            <div class="approval_info">
                              <h5 class="approval_title"><span>${initials}</span></h5>
                              <p class="approval_text">${temp_log["user"]} sent a comment</p>
                              <div>
                                <h6 class="approval_timestamp" data-toggle="tooltip" title="${tooltipTimestamp}">${timestamp}</h6>
                                <small style="color: #929292;">${small_time}</small>
                              </div>
                            </div>
                            <div class="approval_comment_text"><p>${temp_log["value"]}</p></div>
                          </div>
                        </div>
                        <div class="reply-area mt-3">
                          <textarea id="replycomment_${count}0" name="replycomment_${count}0"></textarea>
                          <div style="margin: 15px 0 5px 0;text-align: right;display: flex;align-items: center;justify-content: flex-end;">
                            <button class="btn btn-primary reply_comments" style="font-size:0.9rem;" disabled data-toggle="tooltip" title="Click this button or press Ctrl+Enter" id="replybutton_${count}0" onclick="ReplyToComment('${count}','0','Level ${current_level}','${result_data.id}', '${smtpConfigKey}', '${app_code}')">Reply <i class="fa-solid fa-comment-dots ml-2"></i></button>
                          </div>
                        </div>
                      </div>
                    </div>
                    `
                    $(`#approvalWallModalBody_${elementID}`).find(`.approval_outer_${elementID}`).prepend(audit_html)


                      new_reply_editor = CKEDITOR.replace(`replycomment_${count}0`,
                      {
                        height: 44,
                        removeButtons: home_rtf[0],
                        editorplaceholder: "Type your reply here..." ,
                        plugins: 'mentions,undo,link,list,basicstyles,justify,richcombo,wysiwygarea,toolbar',
                        extraPlugins: 'elementspath,editorplaceholder',
                        toolbar: [
                          { name: 'document', items: ['Undo'] },
                          { name: 'paragraph', items: ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'] },
                          { name: 'basicstyles', items: ['Bold', 'Italic', 'Underline', 'Strike', '-', 'RemoveFormat'] },
                          { name: 'links', items: ['Mention', 'Link', 'Unlink', 'Anchor'] },
                          { name: 'styles', items: ['Styles', 'Format', 'Font', 'FontSize'] },
                          { name: 'colors', items: ['TextColor', 'BGColor'] },
                          { name: 'elementspath', items: ['ElementPath'] }
                        ],
                        mentions: [
                            {
                            feed: dataFeed,
                            itemTemplate: itemTemplate,
                            outputTemplate: outputTemplate,
                            minChars: 0
                            }
                        ],
                        removeButtons: 'PasteFromWord'
                      });
                      CKEDITOR.config.removePlugins = 'exportpdf';
                      CKEDITOR.config.extraPlugins = 'autocorrect,elementspath';

                      CKEDITOR.instances[`replycomment_${count}0`].setData('');

                      new_reply_editor = CKEDITOR.instances[`replycomment_${count}0`]
                      new_reply_editor.on('change',function(){
                        let typedText = new_reply_editor.getData();
                        if(typedText.trim() === ''){
                          $(`#replybutton_${count}0`).prop("disabled",true)
                        }
                        else{
                          $(`#replybutton_${count}0`).prop("disabled",false)
                        }
                      })

                      new_reply_editor.on('key',function(event){
                        if (event.data.keyCode === CKEDITOR.CTRL + 13){
                          $(`#replybutton_${count}0`).trigger("click")
                        }
                      })


                  },
                  error: function () {
                    Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                  }
                });
              }
            });

            $(`#approval_wall_approve_${elementID}`).click( function() {

              var modify_column_data = {}
              var tablename = result_data.tablename
              if (modify_column.hasOwnProperty(tablename)){
                modify_column_data = modify_column[tablename]
              }

              if(Object.keys(modify_column_data).length > 0){

                var approval_json_data_from_approver_edit =`
                  <table id="aprovalwallJsondataForApproverEdit_${elementID}" class="table table-striped table-bordered" cellspacing="0" width="100%">
                    <thead>
                    <tr>
                      <th>Particulars</th>
                      <th>Details</th>
                    </tr>
                  </thead>
                  <tbody>
                  </tbody>
                  </table>`


                $(`#approvalCommentModal_${elementID} .modal-body`).find(".approvers_edit_data").css("display","block")
                $(`#approvalCommentModal_${elementID} .modal-body`).find(".approvers_edit_data").html(approval_json_data_from_approver_edit)

                string=""
                for(let [key,value] of Object.entries(parsed_json_data[0]) ){
                  if(modify_column_data.hasOwnProperty(key)){
                    edited_data[result_data.id] = modify_column_data

                    string+=`<tr><td class="view_details_wrap">${String(key)}</td>`

                    let randomId = (Math.random() + "").replace(".","");
                    string+=`
                    <td id="${randomId+"_"+String(key).replaceAll(" ","_")}" class="d-flex align-items-center" style="justify-content:center; gap:10px;">
                      <span>${String(value)}</span>
                      <div class="process_navbar_popover" data-id="${result_data.id}" data-value="${String(value)}" data-index="1" popover="yes" data-description="" data-column="${String(key)}" data-table="${tablename}" data-data=${JSON.stringify(modify_column_data[String(key)])} data-PopOverSelector="baseMasters" data-PopOverTarget="#yourContentHere" style="display:inline-block;position:relative;border: 1px solid rgba(0,0,0,.06);background: rgba(0,0,0,.09);" style="z-index: 2000;">
                        <p class="fontclass" style="margin-bottom:0px;">
                          <i name="actions" value="" data-toggle="tooltip" title="Click to edit" class="far fa-edit ihover javaSC thin-icon" style="font-size: 17px;margin-left:2px;font-weight:800;color:black; " onclick="popoverEdit.call(this)"></i>
                        </p>
                      </div>
                    </td>`

                    string+=`</tr>`
                  }
                }

                $(`#approvalCommentModal_${elementID}  .modal-body`).find(`#aprovalwallJsondataForApproverEdit_${elementID} tbody`).html(string)

                var table = $(`#aprovalwallJsondataForApproverEdit_${elementID}`).DataTable(
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
              else{
                $(`#approvalCommentModal_${elementID} .modal-body`).find(".approvers_edit_data").empty()
                $(`#approvalCommentModal_${elementID} .modal-body`).find(".approvers_edit_data").css("display","none")
              }


              $(`#approvalCommentModal_${elementID}`).find('.modal-title').text('Approval Edit and Comment');
              $(`#approvalCommentModal_${elementID}`).find('.modal-title').css('color','var(--font-color)');
              $(`#approvalCommentModal_${elementID} .modal-body`).find('.delegateApprovalContainer').css('display', 'none');
              $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("onclick","approve_ind.call(this)")
              CKEDITOR.instances[`approvalCommentText${elementID}`].setData('');
              $(`#approvalCommentModal_${elementID}`).modal('show');
              let approval_type = "approve"
              $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').text('Approve Record');
              $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("data-approval_id",String(primaryKeyId))
              $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("data-tablename",result_data.tablename)
              $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("data-approval_type",approval_type)
              $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("data-element-id",elementID);

            })

            $(`#approval_wall_reject_${elementID}`).click( function() {

              $(`#approvalCommentModal_${elementID}`).find('.modal-title').text('Rejection Comment');
              $(`#approvalCommentModal_${elementID} .modal-body`).find(".approvers_edit_data").empty()
              $(`#approvalCommentModal_${elementID} .modal-body`).find(".approvers_edit_data").css("display","none")
              $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').text('Reject Record');
              $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("onclick","approve_ind.call(this)")
              $(`#approvalCommentModal_${elementID} .modal-body`).find('.delegateApprovalContainer').css('display', 'none');
              CKEDITOR.instances[`approvalCommentText${elementID}`].setData('');
              $(`#approvalCommentModal_${elementID}`).modal('show');
              let approval_type = "reject"
              $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("data-approval_id",String(primaryKeyId))
              $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("data-tablename",result_data.tablename)
              $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("data-approval_type",approval_type)
              $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("data-element-id",elementID);

            })

            $(`#approval_sendtoprevious_${elementID}`).click( function() {

              $(`#approvalCommentModal_${elementID}`).find('.modal-title').text('Resend Comment');
              $(`#approvalCommentModal_${elementID} .modal-body`).find(".approvers_edit_data").empty()
              $(`#approvalCommentModal_${elementID} .modal-body`).find(".approvers_edit_data").css("display","none")
              $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').text('Resend Record');
              $(`#approvalCommentModal_${elementID} .modal-body`).find('.delegateApprovalContainer').css('display', 'none');
              CKEDITOR.instances[`approvalCommentText${elementID}`].setData('');
              $(`#approvalCommentModal_${elementID}`).modal('show');
              $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("data-approval_id",String(primaryKeyId))
              $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("data-tablename",result_data.tablename)
              $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("data-approval_type","resend")
              $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("onclick","resend_ind.call(this)")
              $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("data-element-id",elementID);

            })

            $(`#approval_delegate_${elementID}`).click( function() {

              $(`#approvalCommentModal_${elementID}`).find('.modal-title').text('Delegate Approval Actions');
              $(`#approvalCommentModal_${elementID} .modal-body`).find(".approvers_edit_data").empty()
              $(`#approvalCommentModal_${elementID} .modal-body`).find(".approvers_edit_data").css("display","none")
              $(`#approvalCommentModal_${elementID}`).find('.modal-title').css('color','var(--font-color)');
              CKEDITOR.instances[`approvalCommentText${elementID}`].setData('');
              let userInfo = $(this).attr('data-user-info');
              let currentUserName = $(this).attr('data-current-user');
              if (userInfo) {
                userInfo = JSON.parse(userInfo);
              } else {
                userInfo = {};
              }
              let delegateToDropdownElement = $(`#approvalCommentModal_${elementID} .modal-body`).find('.delegateApprovalContainer').find('select');
              delegateToDropdownElement.empty();
              let delegateToHTML = "<option value='' selected disabled>Select User</option>";
              for (let [uName, uLabel] of Object.entries(userInfo)) {
                if (uName != currentUserName) {
                  delegateToHTML += `<option value='${uName}'>${uLabel}</option>`;
                } else {
                  continue;
                }
              }
              delegateToDropdownElement.append(delegateToHTML);
              $(`#approvalCommentModal_${elementID} .modal-body`).find('.delegateApprovalContainer').css('display', 'block');
              $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("onclick","delegateApproval.call(this)")
              $(`#approvalCommentModal_${elementID}`).modal('show');
              let approval_type = "delegateApproval"
              $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').text('Delegate');
              $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("data-approval_id",String(primaryKeyId))
              $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("data-approval_type",approval_type);
              $(`#approvalCommentModal_${elementID}`).find('#approval_final_send').attr("data-element-id",elementID);

            })

          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          }
        });

      }

      if(String(e.target.attributes[1].value) === 'comments'){

        $.ajax({
          url: `/users/${urlPath}/approval_table/`,
          data: {
            "approval_id": primaryKeyId,
            "element_id" :elementID,
            'operation': 'fetch_comments_data',
          },
          type: "POST",
          dataType: "json",
          success: function (data) {

            let url_string = window.location.pathname
            let f_occ = url_string.indexOf('/', url_string.indexOf('/') + 1)
            let s_occ = url_string.indexOf('/', url_string.indexOf('/') + f_occ +1)
            let t_occ = url_string.indexOf('/', url_string.indexOf('/') + s_occ +1)
            let app_code = url_string.substring(f_occ+1,s_occ)

            var current_level=0
            var audit_log_configs=[]

            mentions_user_list = JSON.parse(data.mentions_user_list)

            var approval_audit_log_data = data.data[0];

            all_users_list = data.all_users_list

            display_in_comments_cols = data.display_in_comments_cols
            search_in_comments_cols = data.search_in_comments_cols

            var smtpConfigKey = data.smtpConfigKey

            var itemTemplate = `<li data-id="{id}"><strong class="username"> ${getFormattedName(search_in_comments_cols)}</strong></li>`;
            var outputTemplate = `<a href="">@${display_in_comments_cols.map(prop => `{${prop}}`).join(' ')}</a><span>&nbsp;</span>`;

            var comment_editor, convo_reply_editor, mentions_reply_editor, new_comment_reply_editor;

            if(data.approval_level_config){
              approval_level_config = JSON.parse(data["approval_level_config"])
              current_level = approval_level_config.current_level
            }

            CKEDITOR.on('instanceReady', function(evt) {
              var editor = evt.editor;


              editor.on('focus', function(e) {
                  element = e.editor.container.$
                  $(element).find(".cke_top.cke_reset_all").css("display","block")
                  $(element).find(".cke_contents.cke_reset").css("height","80px")
              });

              editor.on('blur', function(e) {
                element = e.editor.container.$
                $(element).find(".cke_top.cke_reset_all").css("display","none")
                $(element).find(".cke_contents.cke_reset").css("height","44px")
              })

            });

            comment_editor = CKEDITOR.replace(`approvalCommentText_${elementID}`, {
              height: 44,
              removeButtons: home_rtf[0],
              editorplaceholder: 'Add a comment...',
              plugins: 'mentions,undo,link,list,basicstyles,justify,richcombo,wysiwygarea,toolbar',
              extraPlugins: 'elementspath,editorplaceholder',
              toolbar: [
                { name: 'document', items: ['Undo'] },
                { name: 'paragraph', items: ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'] },
                { name: 'basicstyles', items: ['Bold', 'Italic', 'Underline', 'Strike', '-', 'RemoveFormat'] },
                { name: 'links', items: ['Mention', 'Link', 'Unlink', 'Anchor'] },
                { name: 'styles', items: ['Styles', 'Format', 'Font', 'FontSize'] },
                { name: 'colors', items: ['TextColor', 'BGColor'] },
                { name: 'elementspath', items: ['ElementPath'] }
              ],
              mentions: [
                {
                  feed: dataFeed,
                  itemTemplate: itemTemplate,
                  outputTemplate: outputTemplate,
                  minChars: 0
                }
              ],
              removeButtons: 'PasteFromWord'
            });
            CKEDITOR.config.bodyClass = 'custom_cke_class';
            CKEDITOR.config.removePlugins = 'exportpdf';
            CKEDITOR.config.extraPlugins = 'autocorrect,elementspath';

            CKEDITOR.instances[`approvalCommentText_${elementID}`].setData('');

            comment_editor = CKEDITOR.instances[`approvalCommentText_${elementID}`]
            comment_editor.on('change',function(){
              const typedText = comment_editor.getData();
              if(typedText.trim() === ''){
                $(`#convo_add_comment_${elementID}`).prop("disabled",true)
              }
              else{
                $(`#convo_add_comment_${elementID}`).prop("disabled",false)
              }
            })

            comment_editor.on('key',function(event){
              if (event.data.keyCode === CKEDITOR.CTRL + 13){
                $(`#convo_add_comment_${elementID}`).trigger("click")
              }
            })

            $(`#approvalCommentsModalBody_${elementID}`).find(`.approval_outer_${elementID}`).empty()

            if(approval_audit_log_data.approval_audit_log){
              audit_log_configs = JSON.parse(approval_audit_log_data.approval_audit_log)

              for(let i=0; i<audit_log_configs.length; i++){
                for (let [key, value] of Object.entries(audit_log_configs[i])) {

                  for (let j=0; j<value.length; j++) {
                    dictt = value[j]

                    var [timestamp,tooltipTimestamp] = convertToTimestamp(dictt["time"]);
                    var small_time = "at" + tooltipTimestamp.split("at")[1]
                    var initials = getInitials(dictt["user"])

                    const targetItem = all_users_list.find(item => item.username === dictt["user"]);
                    let additionalString = '';

                    if (targetItem) {
                      const { username, id, ...dataWithoutUsername } = targetItem;
                      const dataValues = Object.values(dataWithoutUsername).filter(value => value!="-" && value!="");
                      additionalString = `(${dataValues.join(' ')})`;
                      if (additionalString="()"){
                        additionalString = ""
                      }
                    }

                    if(dictt["action"] == "Comment"){
                      audit_html = `
                      <div class="approval_card approval_comment">
                        <div id="approval_comment_${i}${j}">
                          <div class="approval_comment_card">
                            <div class="approval_info">
                              <h5 class="approval_title"><span>${initials}</span></h5>
                              <p class="approval_text">${dictt["user"]} ${additionalString} sent a comment</p>
                              <div>
                                <h6 class="approval_timestamp" data-toggle="tooltip" title="${tooltipTimestamp}">${timestamp}</h6>
                                <small style="color: #929292;">${small_time}</small>
                              </div>
                            </div>
                            <div class="approval_comment_text"><p>${dictt["value"].replaceAll("\\t", "&nbsp;").replaceAll("\\n", "<br>")}</p></div>
                          </div>`

                      if (dictt.hasOwnProperty("replies")) {
                        replies = dictt["replies"]

                        for(let k=0; k<replies.length;k++){
                          var [reply_timestamp,reply_tooltipTimestamp] = convertToTimestamp(replies[k]["time"]);
                          var reply_initials = getInitials(replies[k]["user"])
                          audit_html = audit_html + `
                          <div class="reply_comment_card approval_comment_card">
                            <div class="approval_info">
                              <h5 class="approval_title"><span>${reply_initials}</span></h5>
                              <p class="approval_text">${replies[k]["user"]} ${additionalString} replied</p>
                              <div>
                                <h6 class="approval_timestamp" data-toggle="tooltip" title="${reply_tooltipTimestamp}">${reply_timestamp}</h6>
                                <small style="color: #929292;">${small_time}</small>
                              </div>
                            </div>
                            <div class="approval_comment_text"><p>${replies[k]["value"].replaceAll("\\t", "&nbsp;").replaceAll("\\n", "<br>")}</p></div>
                          </div>`
                        }
                      }

                      audit_html = audit_html + `</div><div class="reply-area mt-3">
                          <textarea id="convo_replycomment_${i}${j}" name="convo_replycomment_${i}${j}"></textarea>
                          <div style="margin: 15px 0 5px 0;text-align: right;display: flex;align-items: center;justify-content: flex-end;">
                            <button class="btn btn-primary reply_comments" style="font-size:0.9rem;" disabled data-toggle="tooltip" title="Click this button or press Ctrl+Enter" id="convo_replybutton_${i}${j}" onclick="ReplyToConvoComment('${i}','${j}','${key}','${approval_audit_log_data.id}', '${smtpConfigKey}', '${app_code}')">Reply <i class="fa-solid fa-comment-dots ml-2"></i></button>
                          </div>
                        </div>
                        <style>
                        .approval_wall_btn:hover{
                          background-color: var(--secondary-color) !important;
                          color:var(--font-hover-color);
                        }
                      </style>
                      </div>`

                      $(`#approvalCommentsModalBody_${elementID}`).find(`.approval_outer_${element_id}`).prepend(audit_html)

                      convo_reply_editor = CKEDITOR.replace(`convo_replycomment_${i}${j}`,
                      {
                        height: 44,
                        removeButtons: home_rtf[0],
                        editorplaceholder: "Type your reply here..." ,
                        plugins: 'mentions,undo,link,list,basicstyles,justify,richcombo,wysiwygarea,toolbar',
                        extraPlugins: 'elementspath,editorplaceholder',
                        toolbar: [
                          { name: 'document', items: ['Undo'] },
                          { name: 'paragraph', items: ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'] },
                          { name: 'basicstyles', items: ['Bold', 'Italic', 'Underline', 'Strike', '-', 'RemoveFormat'] },
                          { name: 'links', items: ['Mention', 'Link', 'Unlink', 'Anchor'] },
                          { name: 'styles', items: ['Styles', 'Format', 'Font', 'FontSize'] },
                          { name: 'colors', items: ['TextColor', 'BGColor'] },
                          { name: 'elementspath', items: ['ElementPath'] }
                        ],
                        mentions: [
                          {
                            feed: dataFeed,
                            itemTemplate: itemTemplate,
                            outputTemplate: outputTemplate,
                            minChars: 0
                          }
                        ],
                        removeButtons: 'PasteFromWord'

                      });
                      CKEDITOR.config.removePlugins = 'exportpdf';
                      CKEDITOR.config.extraPlugins = 'autocorrect,elementspath';

                      convo_reply_editor = CKEDITOR.instances[`convo_replycomment_${i}${j}`]
                      convo_reply_editor.on('change',function(){
                        let typedText = convo_reply_editor.getData();
                        if(typedText.trim() === ''){
                          $(`#convo_replybutton_${i}${j}`).prop("disabled",true)
                        }
                        else{
                          $(`#convo_replybutton_${i}${j}`).prop("disabled",false)
                        }
                      })

                      convo_reply_editor.on('key',function(event){
                        if (event.data.keyCode === CKEDITOR.CTRL + 13){
                          $(`#convo_replybutton_${i}${j}`).trigger("click")
                        }
                      })

                      for(var editorId in CKEDITOR.instances){
                        if(editorId.indexOf('convo_replycomment_') === 0){
                          CKEDITOR.instances[editorId].setData('')
                        }
                      }

                    }
                    else if(dictt["action"] == "Mention"){
                      audit_html = `
                      <div class="approval_card approval_comment">
                        <div id="approval_comment_${i}${j}">
                          <div class="approval_comment_card">
                            <div class="approval_info">
                              <h5 class="approval_title"><span>${initials}</span></h5>
                              <p class="approval_text">${dictt["user"]} ${additionalString} mentioned</p>
                              <div>
                                <h6 class="approval_timestamp" data-toggle="tooltip" title="${tooltipTimestamp}">${timestamp}</h6>
                                <small style="color: #929292;">${small_time}</small>
                              </div>
                            </div>
                            <div class="approval_comment_text"><p>${dictt["value"].replaceAll("\\t", "&nbsp;").replaceAll("\\n", "<br>")}</p></div>
                          </div>`

                        if (dictt.hasOwnProperty("replies")) {
                          replies = dictt["replies"]
                          for(let k=0; k<replies.length;k++){
                            var [reply_timestamp,reply_tooltipTimestamp] = convertToTimestamp(replies[k]["time"]);
                            let small_time = "at" + reply_tooltipTimestamp.split("at")[1]
                            var reply_initials = getInitials(replies[k]["user"])
                            audit_html = audit_html + `
                            <div class="reply_comment_card approval_comment_card">
                              <div class="approval_info">
                                <h5 class="approval_title"><span>${reply_initials}</span></h5>
                                <p class="approval_text">${replies[k]["user"]} ${additionalString} replied</p>
                                <div>
                                  <h6 class="approval_timestamp" data-toggle="tooltip" title="${reply_tooltipTimestamp}">${reply_timestamp}</h6>
                                  <small style="color: #929292;">${small_time}</small>
                                </div>
                              </div>
                              <div class="approval_comment_text"><p>${replies[k]["value"].replaceAll("\\t", "&nbsp;").replaceAll("\\n", "<br>")}</p></div>
                            </div>`
                          }
                        }


                            audit_html = audit_html + `</div><div class="reply-area mt-3">

                            <textarea id="convo_replycomment_${i}${j}" name="convo_replycomment_${i}${j}"></textarea>
                            <div style="margin: 15px 0 5px 0;text-align: right;display: flex;align-items: center;justify-content: flex-end;">
                              <button class="btn btn-primary reply_comments" style="font-size:0.9rem;" disabled data-toggle="tooltip" title="Click this button or press Ctrl+Enter" id="convo_replybutton_${i}${j}" onclick="ReplyToConvoComment('${i}','${j}','${key}','${approval_audit_log_data.id}', '${smtpConfigKey}', '${app_code}')">Reply <i class="fa-solid fa-comment-dots ml-2"></i></button>
                            </div>
                          </div>
                          <style>
                          .approval_wall_btn:hover{
                            background-color: var(--secondary-color) !important;
                            color:var(--font-hover-color);
                          }
                        </style>
                        </div>
                      `

                      $(`#approvalCommentsModalBody_${elementID}`).find(`.approval_outer_${element_id}`).prepend(audit_html)

                      mentions_reply_editor = CKEDITOR.replace(`convo_replycomment_${i}${j}`,
                      {
                        height: 44,
                        removeButtons: home_rtf[0],
                        editorplaceholder: 'Add a comment...',
                        plugins: 'mentions,undo,link,list,basicstyles,justify,richcombo,wysiwygarea,toolbar',
                        extraPlugins: 'elementspath,editorplaceholder',
                        toolbar: [
                          { name: 'document', items: ['Undo'] },
                          { name: 'paragraph', items: ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'] },
                          { name: 'basicstyles', items: ['Bold', 'Italic', 'Underline', 'Strike', '-', 'RemoveFormat'] },
                          { name: 'links', items: ['Mention', 'Link', 'Unlink', 'Anchor'] },
                          { name: 'styles', items: ['Styles', 'Format', 'Font', 'FontSize'] },
                          { name: 'colors', items: ['TextColor', 'BGColor'] },
                          { name: 'elementspath', items: ['ElementPath'] }
                        ],
                        mentions: [
                          {
                            feed: dataFeed,
                            itemTemplate: itemTemplate,
                            outputTemplate: outputTemplate,
                            minChars: 0
                          }
                        ],
                        removeButtons: 'PasteFromWord'
                      });

                      CKEDITOR.config.removePlugins = 'exportpdf';
                      CKEDITOR.config.extraPlugins = 'autocorrect,elementspath';

                      mentions_reply_editor = CKEDITOR.instances[`convo_replycomment_${i}${j}`]
                      mentions_reply_editor.on('change',function(){
                        let typedText = mentions_reply_editor.getData();
                        if(typedText.trim() === ''){
                          $(`#convo_replybutton_${i}${j}`).prop("disabled",true)
                        }
                        else{
                          $(`#convo_replybutton_${i}${j}`).prop("disabled",false)
                        }
                      })

                      mentions_reply_editor.on('key',function(event){
                        if (event.data.keyCode === CKEDITOR.CTRL + 13){
                          $(`#convo_replybutton_${i}${j}`).trigger("click")
                        }
                      })

                      for(var editorId in CKEDITOR.instances){
                        if(editorId.indexOf('convo_replycomment_') === 0){
                          CKEDITOR.instances[editorId].setData('')
                        }
                      }
                    }


                  }
                }
              }
            }

            expand_rollup_comments('approvalCommentsModalBody_')

            $(".closeCommentsModal").on('click', function(){

              var modalElement = document.querySelector(".approvalCommentsModal");

              for(var instanceName in CKEDITOR.instances){
                if(CKEDITOR.instances.hasOwnProperty(instanceName)){
                  var editorElement = modalElement.querySelector("#"+instanceName)

                  if(editorElement){
                    CKEDITOR.instances[instanceName].destroy()
                  }
                }
              }

              $(`#approvalCommentsModal_${elementID}`).modal('hide')
            })


            $(`#convo_add_comment_${elementID}`).off('click').on('click', function(){
              approval_comment = CKEDITOR.instances[`approvalCommentText_${elementID}`].getData()
              if (approval_comment) {
                var usernamesArray = []
                // Regular expression to match mentions (assuming mentions are like @username)
                var mentionPattern = /@(\w+)/g;
                var matches = approval_comment.match(mentionPattern);

                if (matches) {
                  // Create a Set ato store unique usernames
                  var uniqueUsernames = new Set();

                  // Extract usernames and add to the Set
                  matches.forEach(function(match) {
                    uniqueUsernames.add(match.substr(1)); // Remove the "@" symbol
                  });

                  // Convert Set to an array and display the mentioned usernames
                  usernamesArray = Array.from(uniqueUsernames);
                }

                $.ajax({
                  url: `/users/${urlPath}/approval_table/`,
                  data: {
                    "approval_id": approval_audit_log_data.id,
                    "current_level":current_level,
                    'operation': 'add_comment',
                    'audit_log_configs':JSON.stringify(audit_log_configs),
                    "approval_comment":approval_comment,
                    "mentioned_usernames":JSON.stringify(usernamesArray),
                    "smtpConfigKey": smtpConfigKey,
                    "app_code": app_code,
                  },
                  type: "POST",
                  dataType: "json",
                  success: function (data) {
                    var count = audit_log_configs.length
                    all_audit_data = JSON.parse(data["all_audit_data"])
                    audit_log_configs.push(all_audit_data[count])
                    CKEDITOR.instances[`approvalCommentText_${elementID}`].setData('');
                    temp_log = data

                    var [timestamp,tooltipTimestamp] = convertToTimestamp(temp_log["time"]);
                    var small_time = "at" + tooltipTimestamp.split("at")[1]
                    var initials = getInitials(temp_log["user"])
                    audit_html = `
                      <div class="approval_card approval_comment">
                        <div id="approval_comment_${count}0">
                          <div class="approval_comment_card">
                            <div class="approval_info">
                              <h5 class="approval_title"><span>${initials}</span></h5>
                              <p class="approval_text">${temp_log["user"]} sent a comment</p>
                              <div>
                                <h6 class="approval_timestamp" data-toggle="tooltip" title="${tooltipTimestamp}">${timestamp}</h6>
                                <small style="color: #929292;">${small_time}</small>
                              </div>
                            </div>
                            <div class="approval_comment_text"><p>${temp_log["value"]}</p></div>
                          </div>
                        </div>
                        <div class="reply-area mt-3">
                          <textarea id="convo_replycomment_${count}0" name="convo_replycomment_${count}0"></textarea>
                          <div style="margin: 15px 0 5px 0;text-align: right;display: flex;align-items: center;justify-content: flex-end;">
                            <button class="btn btn-primary reply_comments" style="font-size:0.9rem;" disabled data-toggle="tooltip" title="Click this button or press Ctrl+Enter" id="convo_replybutton_${count}0" onclick="ReplyToConvoComment('${count}','0','Level ${current_level}','${approval_audit_log_data.id}', '${smtpConfigKey}', '${app_code}')">Reply <i class="fa-solid fa-comment-dots ml-2"></i></button>
                          </div>
                        </div>
                      </div>
                    `
                    $(`#approvalCommentsModalBody_${elementID}`).find(`.approval_outer_${elementID}`).prepend(audit_html)


                      new_comment_reply_editor = CKEDITOR.replace(`convo_replycomment_${count}0`,
                      {
                        height: 44,
                        removeButtons: home_rtf[0],
                        editorplaceholder: "Type your reply here..." ,
                        plugins: 'mentions,undo,link,list,basicstyles,justify,richcombo,wysiwygarea,toolbar',
                        extraPlugins: 'elementspath,editorplaceholder',
                        toolbar: [
                          { name: 'document', items: ['Undo'] },
                          { name: 'paragraph', items: ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'] },
                          { name: 'basicstyles', items: ['Bold', 'Italic', 'Underline', 'Strike', '-', 'RemoveFormat'] },
                          { name: 'links', items: ['Mention', 'Link', 'Unlink', 'Anchor'] },
                          { name: 'styles', items: ['Styles', 'Format', 'Font', 'FontSize'] },
                          { name: 'colors', items: ['TextColor', 'BGColor'] },
                          { name: 'elementspath', items: ['ElementPath'] }
                        ],
                        mentions: [
                            {
                            feed: dataFeed,
                            itemTemplate: itemTemplate,
                            outputTemplate: outputTemplate,
                            minChars: 0
                            }
                        ],
                        removeButtons: 'PasteFromWord'
                      });
                      CKEDITOR.config.removePlugins = 'exportpdf';
                      CKEDITOR.config.extraPlugins = 'autocorrect,elementspath';

                      CKEDITOR.instances[`convo_replycomment_${count}0`].setData('');

                      new_comment_reply_editor = CKEDITOR.instances[`convo_replycomment_${count}0`]
                      new_comment_reply_editor.on('change',function(){
                        let typedText = new_comment_reply_editor.getData();
                        if(typedText.trim() === ''){
                          $(`#convo_replybutton_${count}0`).prop("disabled",true)
                        }
                        else{
                          $(`#convo_replybutton_${count}0`).prop("disabled",false)
                        }
                      })

                      new_comment_reply_editor.on('key',function(event){
                        if (event.data.keyCode === CKEDITOR.CTRL + 13){
                          $(`#convo_replybutton_${count}0`).trigger("click")
                        }
                      })


                  },
                  error: function () {
                    Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                  }
                });
              }
            });

            if(!allowed_approval=="true" && !allowed_edit == "true" && !allowed_rejection=="true"){
              $(`#approvalWallModalBody_${elementID}`).find(`#reopen_all_button_${elementID}`).css("display","none")
              $(`#approvalWallModalBody_${elementID}`).find(`#resolve_all_button_${elementID}`).css("display","none")
              $(`#approvalWallModalBody_${elementID}`).find(`.resolve_button_ind`).css("display","none")
              $(`#approvalWallModalBody_${elementID}`).find(`.reopen_button_ind`).css("display","none")
            }


            $(`#approvalCommentsModal_${elementID}`).modal("show")

          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          }
        });
      }

    }

  })

  // eslint-disable-next-line no-unused-vars,no-var
  var allowSaveTemplate = false
  $(`#saveTemplateButton${elementTabID}`).on('click', function () {
    const eID = $(this).attr('id').split('saveTemplateButton')[1]
    allowSaveTemplate = true // eslint-disable-line no-unused-vars
    saveState[eID] = 1
    $(`#example1${eID}`).DataTable().state.save()
  })

  $(`#filter_button_list_view${elementTabID}`).click(function () {
    elementTabID = $(this).attr('data-elementID')
    $(`#filtershow${elementTabID}`).css('display', 'block')
  })
  $(`#close_filter_card_button${elementTabID}`).click(function () {
    elementTabID = $(this).attr('data-elementID')
    $(`#filtershow${elementTabID}`).css('display', 'none')
    $(`.filter-table${elementTabID}`).empty()
    $.fn.dataTable.ext.search.pop()

    const table = $(`#example1${elementTabID}`).DataTable()

    if (elementTabID in fDict2) {
      new $.fn.dataTable.FixedColumns(
        table,
        fDict2[`example1${elementTabID}`]
      )
    }

    table.draw()
  })
  $('.filter-button_listview').on('click', function () {
    $('.standard_button_click').prop('disabled', false)
  })
  $('#removeFilter' + elementTabID).on('click', function () {
    elementTabID = $(this).attr('data-elementid')
    $(`.btn_search${elementTabID}`).removeAttr('data-filter-daterange')
    datatableDict[elementTabID].columns().every(function () {
      const column = this

      const table = $(`#example1${elementTabID}`).DataTable()

      if (elementTabID in fDict2) {
        new $.fn.dataTable.FixedColumns(
          table,
          fDict2[`example1${elementTabID}`]
        )
      }

      column.search('').draw()
      return true
    })
    $('#removeFilter' + elementTabID).css('display', 'none')
  })
  $(`.filter_btn${elementTabID}`).click(function () {
    const elementTabID = $(this).attr('data-elementID')
    const formFields = listViewTableDict[elementTabID].form_fields
    const tableName = listViewTableDict[elementTabID].model_name
    const dataContainingColumnNames = Array.from(
      listViewTableDict[elementTabID].dataContainingColumnNames
    )
    const name = $(this).attr('name')

    const STRING = formFields[name]
    STRING.replace('</tr>', '<select')
    $(`.filter-table${elementTabID}`).append(STRING)

    $(`.filter-table${elementTabID}`)
      .find('tr')
      .eq(-1)
      .find('td:nth-child(3)')
      .before(
        `<td class="div_in_condition dt-center" style='display:none;'><div name='${name}'><select class="form-control select2"  name="${name}" placeholder="${name}" multiple='multiple'></select></div></td>`
      )
    if (
      String(
        $(`.filter-table${elementTabID}`)
          .find('tr')
          .eq(-1)
          .find('input[data-type=ForeignKey]')[0]
      ) !== 'undefined'
    ) {
      const columnName = name
      const tableName = $(`.filter-table${elementTabID}`)
        .find('tr')
        .eq(-1)
        .find('input[data-type=ForeignKey]')
        .attr('data-tablename')
      $.ajax({
        url: `/users/${urlPath}/dynamicVa/`,
        data: {
          model_name: tableName,
          column_name: columnName,
          operation: 'ForeignKeyFilter',
        },
        type: 'POST',
        dataType: 'json',
        success: function (data) {
          if (Number(Object.keys(data).length) !== 0) {
            $(`.filter-table${elementTabID}`)
              .find('tr')
              .eq(-1)
              .find('input[data-type=ForeignKey]')
              .remove()
            $(`.filter-table${elementTabID}`)
              .find('tr')
              .eq(-1)
              .find('td')
              .eq(-1).html(`
          <div style="max-width:25em;">
            <select class="form-control select2" type="int" name="${columnName}" placeholder="${columnName}"></select>
          </div>
          `)
            for (const [key, value] of Object.entries(data)) {
              $(`.filter-table${elementTabID}`)
                .find('tr')
                .eq(-1)
                .find('td')
                .eq(-1)
                .find('select')
                .append(`<option value="${value}">${key}</option>`)
              $(`.filter-table${elementTabID}`)
                .find('tr')
                .eq(-1)
                .find('td')
                .eq(2)
                .find('select')
                .append(`<option value="${value}">${key}</option>`)
            }
            $(`.filter-table${elementTabID}`)
              .find('tr')
              .eq(-1)
              .find('td')
              .eq(-1)
              .find('select')
              .each(function(){
                $(this).select2()
              })

            $(`.filter-table${elementTabID}`)
              .find('tr')
              .eq(-1)
              .find('td')
              .eq(2)
              .find('select')
              .each(function(){
                $(this).select2()
              })

            $(`.filter-table${elementTabID}`)
              .find('tr')
              .eq(-1)
              .find('td')
              .eq(-2)
              .find('select')
              .find('option')
              .each(function () {
                if (
                  String($(this).attr('value')) === 'Greater than' ||
                  String($(this).attr('value')) === 'Smaller than'
                ) {
                  $(this).remove()
                }
              })
          }
        },
        error: function () {
          Swal.fire({icon: 'error',text: 'Error! Please try again.'});
        },
      })
    }

    $(`.filter-table${elementTabID}:last-child`)
      .find('select')
      .each(function () {
        $(this).select2()
      })

    $(`.filter-table${elementTabID}`)
      .find('tr')
      .find('td')
      .eq(2)
      .find('select')
      .select2({ tags: true, width: '50%' })
    $(`.filter-table${elementTabID}`)
      .find('tr')
      .find('td')
      .find("select[data-dropdown_purpose='select_logical_operator']")
      .closest('td')
      .remove()
    $(`.filter-table${elementTabID}`)
      .find('.select2bs4')
      .on('change', function () {
        const conditionName = $(this).val()
        if (['IN', 'NOT IN'].includes(conditionName) === true) {
          $(this)
            .closest('tr')
            .find('td')
          // eslint-disable-next-line no-unused-vars
            .each(function (index, val) {
              if (index > 1) {
                $(this).css('display', 'none')
                if (index === 2) {
                  $(this).css('display', 'block')
                  $(this)
                    .find('select')
                    .select2({ tags: true, width: '70%' })
                }
              }
            })
        } else {
          $(this)
            .closest('tr')
            .find('td')
          // eslint-disable-next-line no-unused-vars
            .each(function (index, val) {
              if (index > 1) {
                $(this).css('display', 'block')
                if (index === 2) {
                  $(this).css('display', 'none')
                  $(this)
                    .find('select')
                    .select2({ tags: true, width: '70%' })
                }
              }
            })
        }
      })

      $(`.btn_search${elementTabID}`).off('click').on('click',function () {
      const elementTabID = $(this).attr('data-elementID')
      const standardfiltertable = datatableDict[elementTabID]
      $('#removeFilter' + elementTabID).css('display', 'inline-block')
      const modelName = tableName
      const table2 = $(`.filter-table${elementTabID}`)
      const filterList = []
      table2.find('tr').each(function () {
        const filterRow = []
        const condition = $(this).find('select').eq(0).val()
                filterRow.push($(this).find('select').eq(0).attr('name'))
                filterRow.push($(this).find('select').eq(0).val())
                if (['IN', 'NOT IN'].includes(condition) === true) {
          filterRow.push($(this).find('td').eq(2).find('select').val())
                  } else {
          if (
            String($(this).find('td').eq(3).find('input').val()) !==
            'undefined'
          ) {
            filterRow.push($(this).find('td').eq(3).find('input').val())
                      } else {
            filterRow.push($(this).find('select').eq(-1).val())
                      }
        }
                filterList.push(filterRow)
      })

            const filterDict = {
        model_name: modelName,
        filter_list: JSON.stringify(filterList),
        filterform: 'f1',
        elementID: elementTabID,
      }
      if ($(this).attr('data-filter-daterange')) {
        filterDict.daterange_list = $(this).attr('data-filter-daterange')
      }

      if ($(`#tableTab${elementTabID}`).length > 0) {
        const reportTableData = $(`#example1${elementTabID}`)
          .DataTable()
          .column(1)
          .data()
          .toArray()
        filterDict.reportview_filter = JSON.stringify(reportTableData)
      }

      filter_list_2 = JSON.parse(filterDict.filter_list)
      filter_blank_values = false
      filter_list_2.forEach((b)=>{
        b.forEach((c)=>{
          if (typeof(c) === 'object'){
            if (c.length === 0){
              filter_blank_values = true
              return;
            }
          }else{
            if (c === ''){
              filter_blank_values = true
              return;
            }
          }
        })
      })
      if (filter_blank_values === false){
        $.ajax({
          url: `/users/${urlPath}/viewfilter/`,
          data: filterDict,
          type: 'POST',
          dataType: 'json',
          // eslint-disable-next-line no-use-before-define
          success: datatableReload,
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
            $('.standard_button_click').prop('disabled', false)
          },
        })
      }else{
        Swal.fire({icon: 'error',text: 'Please fill input values in filter.'});
      }

      function datatableReload(data) {
                $('.standard_button_click').prop('disabled', false)
        let index
        const datareturned = JSON.parse(data)
                const primaryKey = datareturned[0]
        const filteredpk = datareturned[1]

        for (const i in filteredpk) {
          filteredpk[i] = '^' + filteredpk[i] + '$'
        }
        const combinedsearch = filteredpk.join('|')
        for (const x in dataContainingColumnNames) {
          if (
            String(dataContainingColumnNames[x].data) ===
            String(primaryKey)
          ) {
            index = x
          }
        }

        standardfiltertable.columns().every(function () {
          if (String(this.index()) === String(index)) {
            const column = this
            if (String(column.search()) !== String(combinedsearch)) {
              const table = $(`#example1${elementTabID}`).DataTable()
              if (elementTabID in fDict2) {
                new $.fn.dataTable.FixedColumns(
                  table,
                  fDict2[`example1${elementTabID}`]
                )
              }
              column.search(combinedsearch || '', true, false).draw()
            } else {
              column.search(combinedsearch).draw()
            }
          }
          return true
        })
      }
    })

    // eslint-disable-next-line no-use-before-define
    $('.remove_filter').on('click', removefilter)
    function removefilter() {
      $(this).closest('tr').remove()
    }

    $('.table').on('click', '.remove_filter', function () {
      const whichtr = $(this).closest('tr')
      whichtr.remove()
    })
  })

  $(`.conditional_delete${elementTabID}`).click(function () {
    const itemCode = windowLocation.split('/')[4]
    const elementTabID = $(this).attr('data-elementID')
    const formFields = listViewTableDict[elementTabID].form_fields
    const tableName = listViewTableDict[elementTabID].model_name
    const dataContainingColumnNames = Array.from(
      listViewTableDict[elementTabID].dataContainingColumnNames
    )
    const name = $(this).attr('name')

    const STRING = formFields[name]
    STRING.replace('</tr>', '<select')
    $(`.conditional-delete-table${elementTabID}`).append(STRING)

    $(`.conditional-delete-table${elementTabID}`)
      .find('tr')
      .eq(-1)
      .find('td:nth-child(3)')
      .before(
        `<td class="div_in_condition dt-center" style='display:none;'><div name='${name}'><select class="form-control select2"  name="${name}" placeholder="${name}" multiple='multiple'></select></div></td>`
      )
    if (
      String(
        $(`.conditional-delete-table${elementTabID}`)
          .find('tr')
          .eq(-1)
          .find('input[data-type=ForeignKey]')[0]
      ) !== 'undefined'
    ) {
      const columnName = name
      const tableName = $(`.conditional-delete-table${elementTabID}`)
        .find('tr')
        .eq(-1)
        .find('input[data-type=ForeignKey]')
        .attr('data-tablename')
      $.ajax({
        url: `/users/${urlPath}/dynamicVa/`,
        data: {
          model_name: tableName,
          column_name: columnName,
          operation: 'ForeignKeyFilter',
        },
        type: 'POST',
        dataType: 'json',
        success: function (data) {
          if (Number(Object.keys(data).length) !== 0) {
            $(`.conditional-delete-table${elementTabID}`)
              .find('tr')
              .eq(-1)
              .find('input[data-type=ForeignKey]')
              .remove()
            $(`.conditional-delete-table${elementTabID}`)
              .find('tr')
              .eq(-1)
              .find('td')
              .eq(-1).html(`
          <div style="max-width:25em;">
            <select class="form-control select2" type="int" name="${columnName}" placeholder="${columnName}"></select>
          </div>
          `)
            for (const [key, value] of Object.entries(data)) {
              $(`.conditional-delete-table${elementTabID}`)
                .find('tr')
                .eq(-1)
                .find('td')
                .eq(-1)
                .find('select')
                .append(`<option value="${value}">${key}</option>`)
              $(`.conditional-delete-table${elementTabID}`)
                .find('tr')
                .eq(-1)
                .find('td')
                .eq(2)
                .find('select')
                .append(`<option value="${value}">${key}</option>`)
            }
            $(`.conditional-delete-table${elementTabID}`)
              .find('tr')
              .eq(-1)
              .find('td')
              .eq(-1)
              .find('select')
              .each(function(){
                $(this).select2()
              })

            $(`.conditional-delete-table${elementTabID}`)
              .find('tr')
              .eq(-1)
              .find('td')
              .eq(2)
              .find('select')
              .each(function(){
                $(this).select2()
              })

            $(`.conditional-delete-table${elementTabID}`)
              .find('tr')
              .eq(-1)
              .find('td')
              .eq(-2)
              .find('select')
              .find('option')
              .each(function () {
                if (
                  String($(this).attr('value')) === 'Greater than' ||
                  String($(this).attr('value')) === 'Smaller than'
                ) {
                  $(this).remove()
                }
              })
          }
        },
        error: function () {
          Swal.fire({icon: 'error',text: 'Error! Please try again.'});
        },
      })
    }

    $(`.conditional-delete-table${elementTabID}:last-child`)
      .find('select')
      .each(function () {
        $(this).select2()
      })

    $(`.conditional-delete-table${elementTabID}`)
      .find('tr')
      .find('td')
      .eq(2)
      .find('select')
      .select2({ tags: true, width: '50%' })
    $(`.conditional-delete-table${elementTabID}`)
      .find('tr')
      .find('td')
      .find("select[data-dropdown_purpose='select_logical_operator']")
      .closest('td')
      .remove()
    $(`.conditional-delete-table${elementTabID}`)
      .find('.select2bs4')
      .on('change', function () {
        const conditionName = $(this).val()
        if (['IN', 'NOT IN'].includes(conditionName) === true) {
          $(this)
            .closest('tr')
            .find('td')
          // eslint-disable-next-line no-unused-vars
            .each(function (index, val) {
              if (index > 1) {
                $(this).css('display', 'none')
                if (index === 2) {
                  $(this).css('display', 'block')
                  $(this)
                    .find('select')
                    .select2({ tags: true, width: '70%' })
                }
              }
            })
        } else {
          $(this)
            .closest('tr')
            .find('td')
          // eslint-disable-next-line no-unused-vars
            .each(function (index, val) {
              if (index > 1) {
                $(this).css('display', 'block')
                if (index === 2) {
                  $(this).css('display', 'none')
                  $(this)
                    .find('select')
                    .select2({ tags: true, width: '70%' })
                }
              }
            })
        }
      })

      $(`.conditional_delete_search${elementTabID}`).off('click').on('click',function () {
      const elementTabID = $(this).attr('data-elementID')
      const buttonID = $(this).attr('id')
      const standardfiltertable = datatableDict[elementTabID]
      const modelName = tableName
      const table2 = $(`.conditional-delete-table${elementTabID}`)
      const filterList = []
      table2.find('tr').each(function () {
        const filterRow = []
        const condition = $(this).find('select').eq(0).val()
        filterRow.push($(this).find('select').eq(0).attr('name'))
        filterRow.push($(this).find('select').eq(0).val())
        if (['IN', 'NOT IN'].includes(condition) === true) {
          filterRow.push($(this).find('td').eq(2).find('select').val())
        } else {
          if (
            String($(this).find('td').eq(3).find('input').val()) !==
            'undefined'
          ) {
            filterRow.push($(this).find('td').eq(3).find('input').val())
          } else {
            filterRow.push($(this).find('select').eq(-1).val())
          }
        }
        filterList.push(filterRow)
      })

      if(buttonID === `perm_conditional_delete_${elementTabID}`){
        var view_name = ""
        temp_type = $(`#${elementTabID}_tab_content`).attr("data-template-type")
        if(temp_type == 'Multi Dropdown View'){
          view_name = $(`#tableTab${elementTabID}`).find("select").val()
        }
        $.ajax({
          url: `/users/${urlPath}/DataManagement/`,
          data: {
            'element_id': elementTabID.split("__tab__")[0],
            'operation': "fetch_list_view_msgs",
            'messages' : JSON.stringify(["confirm_conditional_perm_delete_message","success_conditional_perm_delete_message"]),
            'view_name' : view_name
          },
          type: "POST",
          dataType: "json",
          success: function (data) {
            message=""
            icon=""
            if(data.confirm_conditional_perm_delete_message){
              message = data.confirm_conditional_perm_delete_message.message
              icon = data.confirm_conditional_perm_delete_message.icon
            }
            iconHtml = ""
            if (icon){
              iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
            }
            custom_messages = data

            Swal.fire({
              icon : 'question',
              text: message || `Are you sure you want to permanently delete these records?`,
              showDenyButton: true,
              showCancelButton: true,
              confirmButtonText: 'Yes',
              denyButtonText: `No`,
            }).then((result) => {
              if (result.isConfirmed) {
                $.ajax({
                  url: `/users/${urlPath}/${itemCode}/`,
                  data: {
                    operation: 'perm_delete_conditional_list',
                    filter_list: JSON.stringify(filterList),
                    model_name: modelName,
                    elementid: elementTabID,
                    custom_messages: JSON.stringify(custom_messages)
                  },
                  type: 'POST',
                  dataType: 'json',

                  success: function(){
                    $(`#conditional_delete_modal_${elementTabID}`).hide()
                    $(`#example1${elementTabID}`).DataTable().draw()
                    message=""
                    icon=""
                    if(custom_messages.success_conditional_perm_delete_message){
                      message = custom_messages.success_conditional_perm_delete_message.message
                      icon = custom_messages.success_conditional_perm_delete_message.icon
                    }
                    iconHtml = ""
                    if (icon){
                      iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
                    }

                    Swal.fire({icon: 'success',iconHtml, text: message || 'Data deleted successfully!'});
                    $('.modal-backdrop').hide()
                  },
                  error: function () {
                    Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                  },
                })
              }
            })

          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          },
        });

      }

      else if(buttonID === `temp_conditional_delete_${elementTabID}`){
        var view_name = ""
        temp_type = $(`#${elementTabID}_tab_content`).attr("data-template-type")
        if(temp_type == 'Multi Dropdown View'){
          view_name = $(`#tableTab${elementTabID}`).find("select").val()
        }
        $.ajax({
          url: `/users/${urlPath}/DataManagement/`,
          data: {
            'element_id': elementTabID.split("__tab__")[0],
            'operation': "fetch_list_view_msgs",
            'messages' : JSON.stringify(["confirm_conditional_temp_delete_message","success_conditional_temp_delete_message"]),
            'view_name' : view_name
          },
          type: "POST",
          dataType: "json",
          success: function (data) {
            message=""
            icon=""
            if(data.confirm_conditional_temp_delete_message){
              message = data.confirm_conditional_temp_delete_message.message
              icon = data.confirm_conditional_temp_delete_message.icon
            }
            iconHtml = ""
            if (icon){
              iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
            }
            custom_messages = data

            Swal.fire({
              icon : 'question',
              text: message || `Are you sure you want to temporarily delete these records?`,
              showDenyButton: true,
              showCancelButton: true,
              confirmButtonText: 'Yes',
              denyButtonText: `No`,
            }).then((result) => {
              if (result.isConfirmed) {
                $.ajax({
                  url: `/users/${urlPath}/${itemCode}/`,
                  data: {
                    operation: 'temp_delete_conditional_list',
                    filter_list: JSON.stringify(filterList),
                    model_name: modelName,
                    elementid: elementTabID,
                    custom_messages: JSON.stringify(custom_messages)
                  },
                  type: 'POST',
                  dataType: 'json',

                  success: function(){
                    $(`#conditional_delete_modal_${elementTabID}`).hide()
                    $(`#example1${elementTabID}`).DataTable().draw()
                    message=""
                    icon=""
                    if(custom_messages.success_conditional_temp_delete_message){
                      message = custom_messages.success_conditional_temp_delete_message.message
                      icon = custom_messages.success_conditional_temp_delete_message.icon
                    }
                    iconHtml = ""
                    if (icon){
                      iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
                    }
                    Swal.fire({icon: 'success',iconHtml, text: message || 'Data has been temporarily deleted.'});
                    $('.modal-backdrop').hide()
                  },
                  error: function () {
                    Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                  },
                })
              }
            })

          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          },
        });

      }

    })

  })
  let dt = $(`#example1${elementTabID}`).DataTable();
  let firstColumnHeader = dt.column(0).header();
  let firstColumnHeaderText = $(firstColumnHeader).text();

  if (firstColumnHeaderText == 'Select'){
    dt.column(0).visible(false);
  }
  var select_status = false
  $(`#multiple_delete_perm_${elementTabID}`).click(function() {
    const delete_checkboxes = $(`#example1${elementTabID}`).find('.multiple_select_checkbox');
    delete_checkboxes.prop('disabled', false);
    const status = $(`#multiple_delete_perm_${elementTabID}`).attr('data-edit-status')
    let dt = $(`#example1${elementTabID}`).DataTable();
    let firstColumnHeader = dt.column(0).header();
    let firstColumnHeaderText = $(firstColumnHeader).text();
    if(String(status) === "off"){
      $(`#multiple_delete_perm_${elementTabID}`).attr('data-edit-status', 'on')
      $(`#multiple_delete_perm_${elementTabID}`).text('Delete Multiple(Permanent): ON').trigger('change')
      $(`#multiple_delete_perm_final_${elementTabID}`).css('display', 'inline-block')
      $(`#multiple_delete_temp_${elementTabID}`).prop('disabled', true)
      $(`#reject_multiple_ApprovalTemplate_${elementTabID}`).prop('disabled', true);
      $(`#approve_multiple_ApprovalTemplate_${elementTabID}`).prop('disabled', true);
    }
    else{
      $(`#multiple_delete_perm_${elementTabID}`).attr('data-edit-status', 'off')
      $(`#multiple_delete_perm_${elementTabID}`).text('Delete Multiple(Permanent): OFF').trigger('change')
      $(`#multiple_delete_perm_final_${elementTabID}`).css('display', 'none')
      $(`#multiple_delete_temp_${elementTabID}`).prop('disabled', false)
      $(`#reject_multiple_ApprovalTemplate_${elementTabID}`).prop('disabled', false);
      $(`#approve_multiple_ApprovalTemplate_${elementTabID}`).prop('disabled', false);
    }
    if (firstColumnHeaderText == 'Select'){
      if (dt.column(0).visible()){
        dt.column(0).visible(false)
      }else{
        dt.column(0).visible(true)
        select_status = true
      }
    }
    if (delete_checkboxes.css('display') === 'none') {
      delete_checkboxes.css('display', 'inline-block');
    } else {
      delete_checkboxes.css('display', 'none');
    }
    if (select_status){
      $(`#example1${elementTabID}`).find('.multiple_select_checkbox').css('display', 'inline-block');
    }
    if($(`#multiple_select_checkbox_SelectAll_div${elementTabID}`).css('display') === 'none'){
      $(`#multiple_select_checkbox_SelectAll_div${elementTabID}`).css('display', 'inline-block');
    } else{
      $(`#multiple_select_checkbox_SelectAll_div${elementTabID}`).css('display', 'none');
    }
  });

  $(`#multiple_delete_perm_final_${elementTabID}`).click(function(){
    const idDatatable = $(`#example1${elementTabID}`).attr('id')
    const table = $('#' + idDatatable).DataTable()
    const delete_checkboxes = $(`#example1${elementTabID}`).find('.multiple_select_checkbox');
    const itemCode = windowLocation.split('/')[4]
    const tableName = listViewTableDict[elementTabID].model_name
    var deletion_list =[]
    let dt = $(`#example1${elementTabID}`).DataTable();
    let firstColumnHeader = dt.column(0).header();
    let firstColumnHeaderText = $(firstColumnHeader).text();
    delete_checkboxes.each(function() {
      if (this.checked) {
        const tData = $(this.closest('tr'))

        const tab = table.row(tData).data()
        if ('id' in tab){
          primaryKeyId = tab['id']
        }else if ('ID' in tab){
          primaryKeyId = tab['ID']
        }else if ('iD' in tab){
          primaryKeyId = tab['iD']
        }else if ('Id' in tab){
          primaryKeyId = tab['Id']
        }
        deletion_list.push(String(primaryKeyId))
      }
    });
    var numbersArray = $.map(deletion_list, function(item) {
        if (item.startsWith('id:')) {
            var match = item.match(/id:(\d+)/);
            return match ? match[1] : null;
        } else {
            return null;
        }
    });
    if(numbersArray.length > 0){
      deletion_list = numbersArray
    }
    var view_name = ""
    temp_type = $(`#${elementTabID}_tab_content`).attr("data-template-type")
    if(temp_type == 'Multi Dropdown View'){
      view_name = $(`#tableTab${elementTabID}`).find("select").val()
    }
    if(deletion_list.length > 0){
      $.ajax({
        url: `/users/${urlPath}/DataManagement/`,
        data: {
          'element_id': elementTabID.split("__tab__")[0],
          'operation': "fetch_list_view_msgs",
          'messages' : JSON.stringify(["confirm_multiple_delete_perm_message","success_multiple_delete_perm_message"]),
          'view_name' : view_name
        },
        type: "POST",
        dataType: "json",
        success: function (data) {
          message=""
          icon=""
          if(data.confirm_multiple_delete_perm_message){
            message = data.confirm_multiple_delete_perm_message.message
            icon = data.confirm_multiple_delete_perm_message.icon
          }
          iconHtml = ""
          if (icon){
            iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
          }
          custom_messages = data

          Swal.fire({
            icon : 'question',
            iconHtml,
            text: message || `Are you sure you want to permanently delete these records?`,
            showDenyButton: true,
            showCancelButton: true,
            confirmButtonText: 'Yes',
            denyButtonText: `No`,
          }).then((result) => {
            if (result.isConfirmed) {
              $.ajax({
                url: `/users/${urlPath}/${itemCode}/`,
                data: {
                  operation: 'multiple_delete_list_perm',
                  deletion_list: JSON.stringify(deletion_list),
                  model_name: tableName,
                  elementid: elementTabID,
                  custom_messages: JSON.stringify(custom_messages)
                },
                type: 'POST',
                dataType: 'json',

                success: function(){
                  message=""
                  icon=""
                  if(custom_messages.success_multiple_delete_perm_message){
                    message = custom_messages.success_multiple_delete_perm_message.message
                    icon = custom_messages.success_multiple_delete_perm_message.icon
                  }
                  iconHtml = ""
                  if (icon){
                    iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
                  }
                  Swal.fire({icon: 'success',iconHtml, text: message || 'Data deleted successfully.'});
                  $(`#example1${elementTabID}`).DataTable().draw()
                  $(`#multiple_select_checkbox_SelectAll_div${elementTabID}`).css('display', 'none');
                  $('.multiple_select_checkbox').css('display', 'none');
                  $(`#multiple_delete_perm_${elementTabID}`).attr('data-edit-status', 'off')
                  $(`#multiple_delete_perm_${elementTabID}`).text('Delete Multiple(Permanent): OFF').trigger('change')
                  $(`#multiple_delete_perm_final_${elementTabID}`).css('display', 'none')
                  $(`#multiple_delete_temp_${elementTabID}`).prop('disabled', false)
                  $(`#reject_multiple_ApprovalTemplate_${elementTabID}`).prop('disabled', false);
                  $(`#approve_multiple_ApprovalTemplate_${elementTabID}`).prop('disabled', false);
                  if (firstColumnHeaderText == 'Select'){
                    dt.column(0).visible(false)
                  }
                },
                error: function () {
                  Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                },
              })
            }
          })

        },
        error: function () {
          Swal.fire({icon: 'error',text: 'Error! Please try again.'});
        },
      });
    }
    else{
      Swal.fire({icon: 'warning', text:'Please select something!'})
    }

  })

  $(`#multiple_delete_temp_${elementTabID}`).click(function() {
    const delete_checkboxes = $(`#example1${elementTabID}`).find('.multiple_select_checkbox');
    delete_checkboxes.prop('disabled', false);
    const status = $(`#multiple_delete_temp_${elementTabID}`).attr('data-edit-status')
    let dt = $(`#example1${elementTabID}`).DataTable();
    let firstColumnHeader = dt.column(0).header();
    var firstColumnHeaderText = $(firstColumnHeader).text();
    var select_status = false
    if(String(status) === "off"){
      $(`#multiple_delete_temp_${elementTabID}`).attr('data-edit-status', 'on')
      $(`#multiple_delete_temp_${elementTabID}`).text('Delete Multiple(Temporary): ON').trigger('change')
      $(`#multiple_delete_temp_final_${elementTabID}`).css('display', 'inline-block')
      $(`#multiple_delete_perm_${elementTabID}`).prop('disabled', true)
      $(`#reject_multiple_ApprovalTemplate_${elementTabID}`).prop('disabled', true);
      $(`#approve_multiple_ApprovalTemplate_${elementTabID}`).prop('disabled', true);
    }
    else{
      $(`#multiple_delete_temp_${elementTabID}`).attr('data-edit-status', 'off')
      $(`#multiple_delete_temp_${elementTabID}`).text('Delete Multiple(Temporary): OFF').trigger('change')
      $(`#multiple_delete_temp_final_${elementTabID}`).css('display', 'none')
      $(`#multiple_delete_perm_${elementTabID}`).prop('disabled', false);
      $(`#reject_multiple_ApprovalTemplate_${elementTabID}`).prop('disabled', false);
      $(`#approve_multiple_ApprovalTemplate_${elementTabID}`).prop('disabled', false);
    }
    if (firstColumnHeaderText == 'Select'){
      if (dt.column(0).visible()){
        dt.column(0).visible(false);
      }else{
        dt.column(0).visible(true);
        select_status = true
      }
    }
    if (delete_checkboxes.css('display') === 'none') {
      delete_checkboxes.css('display', 'inline-block');
    } else {
      delete_checkboxes.css('display', 'none');
    }
    if (select_status){
      $(`#example1${elementTabID}`).find('.multiple_select_checkbox').css('display', 'inline-block');
    }
    var iTag = dt.$('i[value="approve"]');
    var anchor = iTag.parent();
    var pointerEvents = anchor.css('pointer-events');

    $(`#example1${elementTabID}`).find('.multiple_select_checkbox').each(function(){
      if($(this).closest('td').find('a[title="Approve record"]').css("pointer-events") === "none"){
        $(this).prop('disabled', true);
        $(this).css('cursor', 'default');
      }
      if(pointerEvents === "none"){
        $(this).prop('disabled', true);
        $(this).css('cursor', 'default');
      }
    })
    if($(`#multiple_select_checkbox_SelectAll_div${elementTabID}`).css('display') === 'none'){
      $(`#multiple_select_checkbox_SelectAll_div${elementTabID}`).css('display', 'inline-block');
    } else{
      $(`#multiple_select_checkbox_SelectAll_div${elementTabID}`).css('display', 'none');
    }
  });
  $(`#multiple_delete_temp_final_${elementTabID}`).click(function(){
    const idDatatable = $(`#example1${elementTabID}`).attr('id')
    const table = $('#' + idDatatable).DataTable()
    const itemCode = windowLocation.split('/')[4]
    const tableName = listViewTableDict[elementTabID].model_name
    const delete_checkboxes = $(`#example1${elementTabID}`).find('.multiple_select_checkbox');
    var deletion_list =[]
    let dt = $(`#example1${elementTabID}`).DataTable();
    let firstColumnHeader = dt.column(0).header();
    let firstColumnHeaderText = $(firstColumnHeader).text();
    delete_checkboxes.each(function() {
      if (this.checked) {
        const tData = $(this.closest('tr'))

        const tab = table.row(tData).data()
        if ('id' in tab){
          primaryKeyId = tab['id']
        }else if ('ID' in tab){
          primaryKeyId = tab['ID']
        }else if ('iD' in tab){
          primaryKeyId = tab['iD']
        }else if ('Id' in tab){
          primaryKeyId = tab['Id']
        }
        deletion_list.push(String(primaryKeyId))
      }
    });
    var numbersArray = $.map(deletion_list, function(item) {
        if (item.startsWith('id:')) {
            var match = item.match(/id:(\d+)/);
            return match ? match[1] : null;
        } else {
            return null;
        }
    });
    if(numbersArray.length > 0){
      deletion_list = numbersArray
    }
    var view_name = ""
    temp_type = $(`#${elementTabID}_tab_content`).attr("data-template-type")
    if(temp_type == 'Multi Dropdown View'){
      view_name = $(`#tableTab${elementTabID}`).find("select").val()
    }
    if(deletion_list.length > 0){
      $.ajax({
        url: `/users/${urlPath}/DataManagement/`,
        data: {
          'element_id': elementTabID.split("__tab__")[0],
          'operation': "fetch_list_view_msgs",
          'messages' : JSON.stringify(["confirm_multiple_delete_temp_message","success_multiple_delete_temp_message"]),
          'view_name' : view_name
        },
        type: "POST",
        dataType: "json",
        success: function (data) {
          message=""
          icon=""
          if(data.confirm_multiple_delete_temp_message){
            message = data.confirm_multiple_delete_temp_message.message
            icon = data.confirm_multiple_delete_temp_message.icon
          }
          iconHtml = ""
          if (icon){
            iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
          }
          custom_messages = data

          Swal.fire({
            icon : 'question',
            iconHtml,
            text: message || `Are you sure you want to temporarily delete these records?`,
            showDenyButton: true,
            showCancelButton: true,
            confirmButtonText: 'Yes',
            denyButtonText: `No`,
          }).then((result) => {
            if (result.isConfirmed) {
              $.ajax({
                url: `/users/${urlPath}/${itemCode}/`,
                data: {
                  operation: 'multiple_delete_list_temp',
                  deletion_list: JSON.stringify(deletion_list),
                  model_name: tableName,
                  elementid: elementTabID,
                  custom_messages: JSON.stringify(custom_messages)
                },
                type: 'POST',
                dataType: 'json',

                success: function(){
                  message=""
                  icon=""
                  if(custom_messages.success_multiple_delete_temp_message){
                    message = custom_messages.success_multiple_delete_temp_message.message
                    icon = custom_messages.success_multiple_delete_temp_message.icon
                  }
                  iconHtml = ""
                  if (icon){
                    iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
                  }
                  Swal.fire({icon: 'success',iconHtml, text: message || 'Data has been temporarily deleted.'});
                  $(`#example1${elementTabID}`).DataTable().draw()
                  $(`#multiple_select_checkbox_SelectAll_div${elementTabID}`).css('display', 'none');
                  $('.multiple_select_checkbox').css('display', 'none');
                  $(`#multiple_delete_temp_${elementTabID}`).attr('data-edit-status', 'off')
                  $(`#multiple_delete_temp_${elementTabID}`).text('Delete Multiple(Temporary): OFF').trigger('change')
                  $(`#multiple_delete_temp_final_${elementTabID}`).css('display', 'none')
                  $(`#multiple_delete_perm_${elementTabID}`).prop('disabled', false)
                  $(`#reject_multiple_ApprovalTemplate_${elementTabID}`).prop('disabled', false);
                  $(`#approve_multiple_ApprovalTemplate_${elementTabID}`).prop('disabled', false);
                  if (firstColumnHeaderText == 'Select'){
                    dt.column(0).visible(false)
                  }
                },
                error: function () {
                  Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                },
              })
            }
          })

        },
        error: function () {
          Swal.fire({icon: 'error',text: 'Error! Please try again.'});
        },
      });
    }
    else{
      Swal.fire({icon: 'warning', text:'Please select something!'})
    }

  })

  $(`#approve_all_ApprovalTemplate_${elementTabID}`).click(function () {
    var view_name = ""
    temp_type = $(`#${elementTabID}_tab_content`).attr("data-template-type")
    if(temp_type == 'Multi Dropdown View'){
      view_name = $(`#tableTab${elementTabID}`).find("select").val()
    }
    $.ajax({
      url: `/users/${urlPath}/DataManagement/`,
      data: {
        'element_id': elementTabID.split("__tab__")[0],
        'operation': "fetch_list_view_msgs",
        'messages' : JSON.stringify(["confirm_approve_all_message","success_approve_all_message"]),
        'view_name' : view_name
      },
      type: "POST",
      dataType: "json",
      success: function (data) {
        message=""
        icon=""
        if(data.confirm_approve_all_message){
          message = data.confirm_approve_all_message.message
          icon = data.confirm_approve_all_message.icon
        }
        iconHtml = ""
        if (icon){
          iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
        }
        custom_messages = data

        Swal.fire({
          icon : 'question',
          iconHtml,
          text: message || `Are you sure you want to approve all pending records?`,
          showDenyButton: true,
          showCancelButton: true,
          confirmButtonText: 'Yes',
          denyButtonText: `No`,
        }).then((result) => {
          if (result.isConfirmed) {
            $(`#approvalCommentModal_approveAll_${elementTabID}`).modal('show')
            $(`#approval_final_send_approveAll_${elementTabID}`).off('click').on('click', function(){
              let approval_comment = $(`#approvalCommentText_approveAll_${elementTabID}`).val()
              $(`#approvalCommentModal_approveAll_${elementTabID}`).modal('hide')
              $.ajax({
                url: `/users/${urlPath}/approval_table/`,
                data: {
                  'operation': 'approve_all_approvalTemplate',
                  'element_id': elementTabID.split("__tab__")[0],
                  'approval_comment':approval_comment,
                },
                type: 'POST',
                dataType: 'json',

                success: function(data){
                  message=""
                  icon=""
                  if(custom_messages.success_approve_all_message){
                    message = custom_messages.success_approve_all_message.message
                    icon = custom_messages.success_approve_all_message.icon
                  }
                  iconHtml = ""
                  if (icon){
                    iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
                  }
                  Swal.fire({icon: 'success', iconHtml, text: message || `All the records where you are the concerned approver have been approved.`}).then((result) => {
                    if (result.isConfirmed) {
                      windowLocationAttr.reload()
                    }
                  });

                },
                error: function () {
                  Swal.fire({icon: 'warning',text: 'There are no records left to approve for this user.'});
                },
              })
            })

          }
        })

      },
      error: function () {
        Swal.fire({icon: 'error',text: 'Error! Please try again.'});
      },
    });
  })

  $(`#reject_all_ApprovalTemplate_${elementTabID}`).click(function () {
    var view_name = ""
    temp_type = $(`#${elementTabID}_tab_content`).attr("data-template-type")
    if(temp_type == 'Multi Dropdown View'){
      view_name = $(`#tableTab${elementTabID}`).find("select").val()
    }
    $.ajax({
      url: `/users/${urlPath}/DataManagement/`,
      data: {
        'element_id': elementTabID.split("__tab__")[0],
        'operation': "fetch_list_view_msgs",
        'messages' : JSON.stringify(["confirm_reject_all_message","success_reject_all_message"]),
        'view_name' : view_name
      },
      type: "POST",
      dataType: "json",
      success: function (data) {
        message=""
        icon=""
        if(data.confirm_reject_all_message){
          message = data.confirm_reject_all_message.message
          icon = data.confirm_reject_all_message.icon
        }
        iconHtml = ""
        if (icon){
          iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
        }
        custom_messages = data

        Swal.fire({
          icon : 'question',
          iconHtml,
          text: message || `Are you sure you want to reject all pending records?`,
          showDenyButton: true,
          showCancelButton: true,
          confirmButtonText: 'Yes',
          denyButtonText: `No`,
        }).then((result) => {
          if (result.isConfirmed) {
            $(`#approvalCommentModal_rejectAll_${elementTabID}`).modal('show')
            $(`#approval_final_send_rejectAll_${elementTabID}`).off('click').on('click', function(){
              let approval_comment = $(`#approvalCommentText_rejectAll_${elementTabID}`).val()
              $(`#approvalCommentModal_rejectAll_${elementTabID}`).modal('hide')
              $.ajax({
                url: `/users/${urlPath}/approval_table/`,
                data: {
                  'operation': 'reject_all_approvalTemplate',
                  'element_id': elementTabID.split("__tab__")[0],
                  'approval_comment':approval_comment,
                },
                type: 'POST',
                dataType: 'json',

                success: function(){
                  message=""
                  icon=""
                  if(custom_messages.success_reject_all_message){
                    message = custom_messages.success_reject_all_message.message
                    icon = custom_messages.success_reject_all_message.icon
                  }
                  iconHtml = ""
                  if (icon){
                    iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
                  }
                  Swal.fire({icon: 'success', iconHtml, text: message || `All the records where you are the concerned approver have been rejected.`}).then((result) => {
                    if (result.isConfirmed) {
                      windowLocationAttr.reload()
                    }
                  });
                },
                error: function () {
                  Swal.fire({icon: 'warning',text: 'There are no records left to reject for this user.'});
                },
              })
            })

          }
        })

      },
      error: function () {
        Swal.fire({icon: 'error',text: 'Error! Please try again.'});
      },
    });
  })

  $(`#approve_multiple_ApprovalTemplate_${elementTabID}`).off('click').on('click',function() {
    const approve_checkboxes = $(`#example1${elementTabID}`).find('.multiple_select_checkbox');
    let dt = $(`#example1${elementTabID}`).DataTable();
    let firstColumnHeader = dt.column(0).header();
    let firstColumnHeaderText = $(firstColumnHeader).text();
    let select_status = false   
    const status = $(`#approve_multiple_ApprovalTemplate_${elementTabID}`).attr('data-edit-status')
    if(String(status) === "off"){
      $(`#approve_multiple_ApprovalTemplate_${elementTabID}`).attr('data-edit-status', 'on')
      $(`#approve_multiple_ApprovalTemplate_${elementTabID}`).text('Approve Multiple: ON').trigger('change')
      $(`#approve_multiple_ApprovalTemplate_final_${elementTabID}`).css('display', 'inline-block')
      $(`#multiple_delete_perm_${elementTabID}`).prop('disabled', true)
      $(`#multiple_delete_temp_${elementTabID}`).prop('disabled', true)
      $(`#reject_multiple_ApprovalTemplate_${elementTabID}`).prop('disabled', true)
    }
    else{
      $(`#approve_multiple_ApprovalTemplate_${elementTabID}`).attr('data-edit-status', 'off')
      $(`#approve_multiple_ApprovalTemplate_${elementTabID}`).text('Approve Multiple: OFF').trigger('change')
      $(`#approve_multiple_ApprovalTemplate_final_${elementTabID}`).css('display', 'none')
      $(`#multiple_delete_perm_${elementTabID}`).prop('disabled', false)
      $(`#multiple_delete_temp_${elementTabID}`).prop('disabled', false)
      $(`#reject_multiple_ApprovalTemplate_${elementTabID}`).prop('disabled', false)
    }
    if (firstColumnHeaderText == 'Select'){
      if (dt.column(0).visible()){
        dt.column(0).visible(false);
      }else{
        dt.column(0).visible(true);
        select_status = true
      }
    }
    if (select_status){
      $(`#example1${elementTabID}`).find('.multiple_select_checkbox').css('display', 'inline-block');
    }
    if (approve_checkboxes.css('display') === 'none') {
      approve_checkboxes.css('display', 'inline-block');
    } else {
      approve_checkboxes.css('display', 'none');
    }
    var iTag = dt.$('i[value="approve"]');
    var anchor = iTag.parent();
    var pointerEvents = anchor.css('pointer-events');

    $(`#example1${elementTabID}`).find('.multiple_select_checkbox').each(function(){
      if($(this).closest('td').find('a[title="Approve record"]').css("pointer-events") === "none"){
        $(this).prop('disabled', true);
        $(this).css('cursor', 'default');
      }
      if(pointerEvents === "none"){
        $(this).prop('disabled', true);
        $(this).css('cursor', 'default');
      }
    })
    if($(`#multiple_select_checkbox_SelectAll_div${elementTabID}`).css('display') === 'none'){
      $(`#multiple_select_checkbox_SelectAll_div${elementTabID}`).css('display', 'inline-block');
    } else{
      $(`#multiple_select_checkbox_SelectAll_div${elementTabID}`).css('display', 'none');
    }
  });
  $(`#approve_multiple_ApprovalTemplate_final_${elementTabID}`).off('click').on('click', function () {
    const idDatatable = $(`#example1${elementTabID}`).attr('id')
    const table = $('#' + idDatatable).DataTable()
    var view_name = ""
    temp_type = $(`#${elementTabID}_tab_content`).attr("data-template-type")
    if(temp_type == 'Multi Dropdown View'){
      view_name = $(`#tableTab${elementTabID}`).find("select").val()
    }
    const approve_checkboxes = $(`#example1${elementTabID}`).find('.multiple_select_checkbox');
    var approve_list = []
    approve_checkboxes.each(function() {
      if($(this).closest('td').find('a[title="Approve record"]').css("pointer-events") === "none"){
        $(this).prop('disabled', true);
        $(this).css('cursor', 'default');
      }
      if (this.checked) {
        const tData = $(this.closest('tr'))
        const tab = table.row(tData).data()
        if ('id' in tab){
          primaryKeyId = tab['id']
        }else if ('ID' in tab){
          primaryKeyId = tab['ID']
        }else if ('iD' in tab){
          primaryKeyId = tab['iD']
        }else if ('Id' in tab){
          primaryKeyId = tab['Id']
        }
        approve_list.push(String(primaryKeyId))
      }
    });
    if(approve_list.length > 0){
      $.ajax({
        url: `/users/${urlPath}/DataManagement/`,
        data: {
          'element_id': elementTabID.split("__tab__")[0],
          'operation': "fetch_list_view_msgs",
          'messages' : JSON.stringify(["confirm_approve_multiple_message","success_approve_multiple_message"]),
          'view_name' : view_name
        },
        type: "POST",
        dataType: "json",
        success: function (data) {
          message=""
          icon=""
          if(data.confirm_approve_multiple_message){
            message = data.confirm_approve_multiple_message.message
            icon = data.confirm_approve_multiple_message.icon
          }
          iconHtml = ""
          if (icon){
            iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
          }
          custom_messages = data

          Swal.fire({
            icon : 'question',
            iconHtml,
            text: message || `Are you sure you want to approve selected records for this approver?`,
            showDenyButton: true,
            showCancelButton: true,
            confirmButtonText: 'Yes',
            denyButtonText: `No`,
          }).then((result) => {
            if (result.isConfirmed) {
              $(`#approvalCommentModal_approveMultiple_${elementTabID}`).modal('show')
              $(`#approval_final_send_approveMultiple_${elementTabID}`).off('click').on('click', function(){
                let approval_comment = $(`#approvalCommentText_approveMultiple_${elementTabID}`).val()
                $(`#approvalCommentModal_approveMultiple_${elementTabID}`).modal('hide')

                $.ajax({
                  url: `/users/${urlPath}/approval_table/`,
                  data: {
                    'operation': 'approve_all_approvalTemplate',
                    'element_id': elementTabID.split("__tab__")[0],
                    'approval_comment':approval_comment,
                    'approve_list': JSON.stringify(approve_list)
                  },
                  type: 'POST',
                  dataType: 'json',

                  success: function(){
                    message=""
                    icon=""
                    if(custom_messages.success_approve_multiple_message){
                      message = custom_messages.success_approve_multiple_message.message
                      icon = custom_messages.success_approve_multiple_message.icon
                    }
                    iconHtml = ""
                    if (icon){
                      iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
                    }
                    Swal.fire({icon: 'success', iconHtml, text: message || `All selected records where you are the concerned approver have been approved.`});
                    $(`#example1${elementTabID}`).DataTable().draw()
                    $(`#multiple_select_checkbox_SelectAll_div${elementTabID}`).css('display', 'none');
                    $('.multiple_select_checkbox').css('display', 'none');
                    $(`#multiple_delete_perm_${elementTabID}`).prop('disabled', false)
                    $(`#multiple_delete_temp_${elementTabID}`).prop('disabled', false)
                    $(`#reject_multiple_ApprovalTemplate_${elementTabID}`).prop('disabled', false)
                    $(`#approve_multiple_ApprovalTemplate_${elementTabID}`).attr('data-edit-status', 'off')
                    $(`#approve_multiple_ApprovalTemplate_${elementTabID}`).text('Approve Multiple: OFF').trigger('change')
                    $(`#approve_multiple_ApprovalTemplate_final_${elementTabID}`).css('display', 'none');
                  },
                  error: function () {
                    Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                  },
                })
              })

            }
          })

        },
        error: function () {
          Swal.fire({icon: 'error',text: 'Error! Please try again.'});
        },
      });
    }
    else{
      Swal.fire({icon: 'warning', text:'Please select something!'});
    }
  })
  $(`#reject_multiple_ApprovalTemplate_${elementTabID}`).off('click').on('click', function() {
    let dt = $(`#example1${elementTabID}`).DataTable();
    let firstColumnHeader = dt.column(0).header();
    let firstColumnHeaderText = $(firstColumnHeader).text();
    let select_status = false    
    const reject_checkboxes = $(`#example1${elementTabID}`).find('.multiple_select_checkbox');
    
    const status = $(`#reject_multiple_ApprovalTemplate_${elementTabID}`).attr('data-edit-status')
    if(String(status) === "off"){
      $(`#reject_multiple_ApprovalTemplate_${elementTabID}`).attr('data-edit-status', 'on')
      $(`#reject_multiple_ApprovalTemplate_${elementTabID}`).text('Reject Multiple:ON').trigger('change')
      $(`#reject_multiple_ApprovalTemplate_final_${elementTabID}`).css('display', 'inline-block')
      $(`#multiple_delete_perm_${elementTabID}`).prop('disabled', true)
      $(`#multiple_delete_temp_${elementTabID}`).prop('disabled', true)
      $(`#approve_multiple_ApprovalTemplate_${elementTabID}`).prop('disabled', true)
    }
    else{
      $(`#reject_multiple_ApprovalTemplate_${elementTabID}`).attr('data-edit-status', 'off')
      $(`#reject_multiple_ApprovalTemplate_${elementTabID}`).text('Reject Multiple:OFF').trigger('change')
      $(`#reject_multiple_ApprovalTemplate_final_${elementTabID}`).css('display', 'none')
      $(`#multiple_delete_perm_${elementTabID}`).prop('disabled', false)
      $(`#multiple_delete_temp_${elementTabID}`).prop('disabled', false)
      $(`#approve_multiple_ApprovalTemplate_${elementTabID}`).prop('disabled', false)
    }

    if (firstColumnHeaderText == 'Select'){
      if (dt.column(0).visible()){
        dt.column(0).visible(false);
      }else{
        dt.column(0).visible(true);
        select_status = true
      }
    }
    if (select_status){
      $(`#example1${elementTabID}`).find('.multiple_select_checkbox').css('display', 'inline-block');
    }

    if (reject_checkboxes.css('display') === 'none') {
      reject_checkboxes.css('display', 'inline-block');
    } else {
      reject_checkboxes.css('display', 'none');
    }

    var iTag = dt.$('i[value="approve"]');
    var anchor = iTag.parent();
    var pointerEvents = anchor.css('pointer-events');

    $(`#example1${elementTabID}`).find('.multiple_select_checkbox').each(function(){
      if($(this).closest('td').find('a[title="Approve record"]').css("pointer-events") === "none"){
        $(this).prop('disabled', true);
        $(this).css('cursor', 'default');
      }
      if(pointerEvents === "none"){
        $(this).prop('disabled', true);
        $(this).css('cursor', 'default');
      }
    })

    if($(`#multiple_select_checkbox_SelectAll_div${elementTabID}`).css('display') === 'none'){
      $(`#multiple_select_checkbox_SelectAll_div${elementTabID}`).css('display', 'inline-block');
    } else{
      $(`#multiple_select_checkbox_SelectAll_div${elementTabID}`).css('display', 'none');
    }
  });
  $(`#reject_multiple_ApprovalTemplate_final_${elementTabID}`).off('click').on('click', function () {
    const idDatatable = $(`#example1${elementTabID}`).attr('id')
    const table = $('#' + idDatatable).DataTable()
    let firstColumnHeader = table.column(0).header();
    let firstColumnHeaderText = $(firstColumnHeader).text();
    var view_name = ""
    temp_type = $(`#${elementTabID}_tab_content`).attr("data-template-type")
    if(temp_type == 'Multi Dropdown View'){
      view_name = $(`#tableTab${elementTabID}`).find("select").val()
    }
    const reject_checkboxes = $(`#example1${elementTabID}`).find('.multiple_select_checkbox');
    var reject_list = []
    reject_checkboxes.each(function() {
      if($(this).closest('td').find('a[title="Approve record"]').css("pointer-events") === "none"){
        $(this).prop('disabled', true);
        $(this).css('cursor', 'default');
      }
      if (this.checked) {
        const tData = $(this.closest('tr'))
        const tab = table.row(tData).data()
        if ('id' in tab){
          primaryKeyId = tab['id']
        }else if ('ID' in tab){
          primaryKeyId = tab['ID']
        }else if ('iD' in tab){
          primaryKeyId = tab['iD']
        }else if ('Id' in tab){
          primaryKeyId = tab['Id']
        }
        reject_list.push(String(primaryKeyId))
      }
    });

    if(reject_list.length > 0){
      $.ajax({
        url: `/users/${urlPath}/DataManagement/`,
        data: {
          'element_id': elementTabID.split("__tab__")[0],
          'operation': "fetch_list_view_msgs",
          'messages' : JSON.stringify(["confirm_reject_multiple_message","success_reject_multiple_message"]),
          'view_name' : view_name
        },
        type: "POST",
        dataType: "json",
        success: function (data) {
          message=""
          icon=""
          if(data.confirm_reject_multiple_message){
            message = data.confirm_reject_multiple_message.message
            icon = data.confirm_reject_multiple_message.icon
          }
          iconHtml = ""
          if (icon){
            iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
          }
          custom_messages = data

          Swal.fire({
            icon : 'question',
            iconHtml,
            text: message || `Are you sure you want to reject selected records for this approver?`,
            showDenyButton: true,
            showCancelButton: true,
            confirmButtonText: 'Yes',
            denyButtonText: `No`,
          }).then((result) => {
            if (result.isConfirmed) {
              $(`#approvalCommentModal_rejectMultiple_${elementTabID}`).modal('show')
              $(`#approval_final_send_rejectMultiple_${elementTabID}`).off('click').on('click', function(){
                let approval_comment = $(`#approvalCommentText_rejectMultiple_${elementTabID}`).val()
                $(`#approvalCommentModal_rejectMultiple_${elementTabID}`).modal('hide')

                $.ajax({
                  url: `/users/${urlPath}/approval_table/`,
                  data: {
                    'operation': 'reject_all_approvalTemplate',
                    'element_id': elementTabID.split("__tab__")[0],
                    'approval_comment':approval_comment,
                    'reject_list': JSON.stringify(reject_list)
                  },
                  type: 'POST',
                  dataType: 'json',

                  success: function(){
                    message=""
                    icon=""
                    if(custom_messages.success_reject_multiple_message){
                      message = custom_messages.success_reject_multiple_message.message
                      icon = custom_messages.success_reject_multiple_message.icon
                    }
                    iconHtml = ""
                    if (icon){
                      iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
                    }
                    Swal.fire({icon: 'success', iconHtml, text: message || `All selected records where you are the concerned approver have been rejected.`});
                    $(`#example1${elementTabID}`).DataTable().draw()
                    $(`#multiple_select_checkbox_SelectAll_div${elementTabID}`).css('display', 'none');
                    $('.multiple_select_checkbox').css('display', 'none');
                    $(`#multiple_delete_perm_${elementTabID}`).prop('disabled', false)
                    $(`#multiple_delete_temp_${elementTabID}`).prop('disabled', false)
                    $(`#approve_multiple_ApprovalTemplate_${elementTabID}`).prop('disabled', false)
                    $(`#reject_multiple_ApprovalTemplate_${elementTabID}`).attr('data-edit-status', 'off')
                    $(`#reject_multiple_ApprovalTemplate_${elementTabID}`).text('Reject Multiple: OFF').trigger('change')
                    $(`#reject_multiple_ApprovalTemplate_final_${elementTabID}`).css('display', 'none');
                    if (firstColumnHeaderText == 'Select'){
                      dt.column(0).visible(false);
                    }
                  },
                  error: function () {
                    Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                  },
                })
              })

            }
          })

        },
        error: function () {
          Swal.fire({icon: 'error',text: 'Error! Please try again.'});
        },
      });
    }
    else{
      Swal.fire({icon: 'warning', text:'Please select something!'});
    }
  })



  // Date Range Filter

  $(`#filter_date${elementTabID}`).on('change', function () {
    if (String(this.value) === 'Custom') {
      $(`#startandenddate${elementTabID}`).css('display', 'block')
    } else {
      $(`#startandenddate${elementTabID}`).css('display', 'none')
    }
  })

  $(`#daterange_filter${elementTabID}`).off('click').on('click', function () {
    const modelName = listViewTableDict[elementTabID].model_name
    const daterangeList = []
    let datefield = 'created_date'
    let customdatefield = $(this).attr('daterange_field')
    if (
      String($(this).attr('daterange_table')) === String(modelName) &&
      customdatefield
    ) {
      datefield = customdatefield
    }
    $('#removeFilter' + elementTabID).css('display', 'inline-block')
    const dataselected = $(`#filter_date${elementTabID}`).val()
    if (String(dataselected) === 'Custom') {
      daterangeList.push(datefield)
      daterangeList.push(dataselected)
      daterangeList.push($(`#startdate${elementTabID}`).val())
      daterangeList.push($(`#enddate${elementTabID}`).val())
    } else {
      daterangeList.push('created_date')
      daterangeList.push(dataselected)
    }
    const table2 = $(`.filter-table${elementTabID}`)

    const filterList = []
    table2.find('tr').each(function () {
      const filterRow = []
      const condition = $(this).find('select').eq(0).val()
      filterRow.push($(this).find('select').eq(0).attr('name'))
      filterRow.push($(this).find('select').eq(0).val())
      if (['IN', 'NOT IN'].includes(condition) === true) {
        filterRow.push($(this).find('td').eq(2).find('select').val())
      } else {
        if (
          String($(this).find('td').eq(3).find('input').val()) !==
          'undefined'
        ) {
          filterRow.push($(this).find('td').eq(3).find('input').val())
        } else {
          filterRow.push($(this).find('select').eq(-1).val())
        }
      }
      filterList.push(filterRow)
    })
        const filterDict = {
      model_name: modelName,
      filter_list: JSON.stringify(filterList),
      daterange_list: JSON.stringify(daterangeList),
      filterform: 'f1',
      elementID: elementTabID,
      }

    if ($(`#tableTab${elementTabID}`).length > 0) {
      const reportTableData = $(`#example1${elementTabID}`)
        .DataTable()
        .column(1)
        .data()
        .toArray()
      filterDict.reportview_filter = JSON.stringify(reportTableData)
    }

    $(`.btn_search${elementTabID}`).attr(
      'data-filter-daterange',
      JSON.stringify(daterangeList)
    )
        $.ajax({
      url: `/users/${urlPath}/viewfilter/`,
      data: filterDict,
      type: 'POST',
      dataType: 'json',
      // eslint-disable-next-line no-use-before-define
      success: datatableReload,
      error: function () {
        Swal.fire({icon: 'error',text: 'Error! Please try again.'});
      },
    })
    function datatableReload(data) {
            $('.standard_button_click').prop('disabled', false)
      const standardfiltertable = datatableDict[elementTabID]
            const datareturned = JSON.parse(data)
            const primaryKey = datareturned[0]
            const filteredpk = datareturned[1]
            for (const i in filteredpk) {
        filteredpk[i] = '^' + filteredpk[i] + '$'
              }
      const combinedsearch = filteredpk.join('|')
            for (const x in dataContainingColumnNames) {
        if (
          String(dataContainingColumnNames[x].data) === String(primaryKey)
        ) {
          var index = x // eslint-disable-line no-var
                  }
      }

      standardfiltertable.columns().every(function () {
                if (String(this.index()) === String(index)) {
          const column = this
                    if (String(column.search()) !== String(combinedsearch)) {
            column.search(combinedsearch || '', true, false).draw()
                      } else {
            column.search(combinedsearch).draw()
          }
        }
        return true
      })
    }
  })
}

function disable_checkboxes_conditions(elementTabID){
  var checkboxes = $(`#example1${elementTabID}`).find('.multiple_select_checkbox')
  checkboxes.each(function(){
    if($(this).closest('td').find('a[title="Approve record"]').css("pointer-events") === "none"){
      $(this).prop('disabled', true);
      $(this).css('cursor', 'default');
    }
  });
}

function checkforselection(elementTabID, obj){
  var closestTable = $(obj).closest('table')
  var checkboxes = closestTable.find('.multiple_select_checkbox');
  if (checkboxes.filter(':checked').length === checkboxes.length) {
    $(`#multiple_select_checkbox_SelectAll${elementTabID}`).prop('checked', true)
  }
  else{
    $(`#multiple_select_checkbox_SelectAll${elementTabID}`).prop('checked', false)
  }

}

function select_all_multiple(elementTabID, obj){
  var checkboxes = $(`#example1${elementTabID}`).find('.multiple_select_checkbox')
  if($(`#multiple_select_checkbox_SelectAll${elementTabID}`).is(':checked')){
    checkboxes.prop('checked', true)
    checkboxes.each(function(){
      if($(this).prop('disabled') === true){
        $(this).prop('checked', false);
      }
    })
  }
  else{
    checkboxes.prop('checked', false)
  }
}

function listViewEditRow(
  urlForAjax,
  pk,
  elementID,
  elementIDData,
  tableName,
  editName,
  ThisElement,
  template_type
) {
  let view_name = ""
  temp_type = $(`#${elementIDData}_tab_content`).attr("data-template-type")
  if(temp_type == 'Multi Dropdown View'){
    view_name = $(`#tableTab${elementIDData}`).find("select").val()
  }
  $.ajax({
    // "url": "{% url 'users:standard_update_master_form' %}",
    url: urlForAjax,
    // "data": JSON.stringify(data),
    data: {
      operation: 'send_form_data_single_row_from_backend_to_front_end',
      primary_key: pk,
      model_name: tableName,
      element_id: elementIDData,
      edit_name: editName,
      listflowcolumnname: listflowcolumnname,
      view_name:view_name,
    },
    dataType: 'json',
    type: 'POST',
    success: function (data) {
      const modalId = '#list_view_edit_modal_' + elementID
      const modalbody = $(modalId).find('.modal-body')
      ThisElement.prop('disabled', false);
      if(data.hasOwnProperty("maximum_levels_allowed")){
        $(modalId).attr("data-maximum_levels_allowed",data.maximum_levels_allowed)
      }
      if(data.hasOwnProperty("maximum_approvers_allowed")){
        $(modalId).attr("data-maximum_approvers_allowed",data.maximum_approvers_allowed)
      }
      modalbody.empty()
      if (String(editName) === 'Flow Definition') {
        modalbody.append(data.form_render)
        modalbody.find(':submit').closest('div').prepend(htmlflow)
        modalbody.find(`#${listflowcolumn}`).css('display', 'none')

        modalbody.find('select').each(function () {
          $(this).select2({ tags: true })
        })
        function removeFuncflow() {
          $('#flow_table').DataTable().destroy()
          $(this).closest('tr').remove()
          // eslint-disable-next-line no-unused-vars
          const table = $('#flow_table').DataTable({
            rowReorder: { update: false },
            ordering: false,
            paging: false,
            searching: false,
            bPaginate: false,
            info: false,
            bLengthChange: false,
          })
        }
        let flowcolumndata = data.flowcolumndata
        if (String(flowcolumndata) !== '') {
          flowcolumndata = JSON.parse(flowcolumndata)
          for (const i in flowcolumndata) {
            $('#flow_table_body').append(
              '<tr>' +
                '<td class="workflow_steps_table"><center>' +
                flowcolumndata[i] +
                '</center></td>' +
                `<td><center>
              <span class="table_remove_flow" id="removeerow" disabled>
                <a data-toggle="tooltip" title="Delete element" value="delete"><i name="actions" value="delete" class="far fa-trash-alt ihover javaSC thin-icontrash" style="font-size: 18px "></i></a>
              </span>
              </center></td></tr>`
            )
          }
          $('.table_remove_flow').click(removeFuncflow)
        }
        $('#flow_table').DataTable({
          rowReorder: { update: false },
          ordering: false,
          paging: false,
          searching: false,
          bPaginate: false,
          info: false,
          bLengthChange: false,
        })
        $('.selectflow').on('change', function () {
          if ($('#flow_table_body').find('tr').length > 0) {
            $('#flow_table').DataTable().destroy()
          }
          $('#flow_table_body').append(
            '<tr>' +
              '<td class="workflow_steps_table"><center>' +
              $(this).val() +
              '</center></td>' +
              `<td><center>
          <span class="table_remove_flow" id="removeerow" disabled>
            <a data-toggle="tooltip" title="Delete element" value="delete"><i name="actions" value="delete" class="far fa-trash-alt ihover javaSC thin-icontrash" style="font-size: 18px "></i></a>
          </span>
          </center></td></tr>`
          )
          // eslint-disable-next-line no-unused-vars
          const table = $('#flow_table').DataTable({
            rowReorder: { update: false },
            ordering: false,
            paging: false,
            searching: false,
            bPaginate: false,
            info: false,
            bLengthChange: false,
          })
          $('.table_remove_flow').click(removeFuncflow)
        })
        // modalbody.find(":submit").on('click',function(){

        // })
      } else if (String(editName) === 'Model Definition') {
        modalbody.append(htmlmodeldef)
        // modalbody.find('select').each(function(){
        //   $(this).select2();
        // })
        $('#id_model_name_processmodeldef').val(data.model_name)
        $('#id_model_description_processmodeldef').val(
          data.model_description
        )
        const modelsysteminteractions = JSON.parse(
          data.modelsysteminteractions
        )
        const modeldesc = JSON.parse(data.modeldesc)
        const modelstakeholders = JSON.parse(data.modelstakeholders)
        const modelgovdoc = JSON.parse(data.modelgovdoc)

        $(
          '#id_model_methodology_mapping_description_processmodeldef'
        ).val(modeldesc.model_methodology_mapping_description)
        $('#id_model_methodology_parameters_processmodeldef').val(
          modeldesc.model_methodology_parameters
        )
        $('#id_model_data_management_methods_processmodeldef').val(
          modeldesc.model_data_management_methods
        )
        $('#id_model_variables_processmodeldef').val(
          modeldesc.model_variables
        )
        $('#id_model_output_format_processmodeldef').val(
          modeldesc.model_output_format
        )
        $('#id_model_inputs_processmodeldef').val(modeldesc.model_inputs)
        $('#id_recalib_freq_processmodeldef').val(
          modeldesc.model_recalibration_frequency
        )
        $('#id_val_freq_processmodeldef').val(
          modeldesc.model_validation_frequency
        )
        if (modelgovdoc.length > 0) {
          $('#test_tablemodeldefdocument tr').last().remove()
          for (const i in modelgovdoc) {
            const RowNodocument = $('#edit_tablemodeldefdocument')
              .find('table tr')
              .last().prevObject.length
            const templateStringmodeldef = `<tr>
                <td class="pt-3-half" contenteditable="true" id="${
                  'document_model_def' + RowNodocument
                }" required>
                <input type="text" value=${
                  modelgovdoc[i].model_document_type
                }>
                </td>
                <td class="pt-3-half" contenteditable="true" id="${
                  'upload_model_defdocument' + RowNodocument
                }"" required>
                  <div class="custom-file">
                  <input type="file" id="myfile" name="${
                    'myfile' + RowNodocument
                  }" class="custom-file-input modeldeffile">
                  <label class="custom-file-label">Choose file</label>
              </div>
                </td>
                <td><button type="button" name=${
                  modelgovdoc[i].model_document
                } class="downloadmodeldoc" style="background-color:transparent; border:transparent;">Download Existing File</button></td>
                <td>
                    <span class="table-addmodeldefdocument" id=${
                      'adddocument_' + RowNodocument
                    }><button type="button"
                            class="btn  btn-primary btn-rounded btn-sm my-0">+</button></span>
                </td>
                <td><center>
                    <span class="table-removemodeldefdocument" id=${
                      'removedocument_' + RowNodocument
                    }><button type="button" style="background-color:black"
                            class="btn btn-danger btn-rounded btn-sm my-0">-</button></span>
                            </center></td>
                </tr>`
            table = document.getElementById('test_tablemodeldefdocument')
            const index = $(this).parents('tr').index()
            const row = table.insertRow(index)
            row.innerHTML = templateStringmodeldef
            // eslint-disable-next-line no-use-before-define
            $('#remove_' + RowNodocument).click(removeFuncmodel)
            // eslint-disable-next-line no-use-before-define
            $('#add_' + RowNodocument).click(addFuncmodeldocument)
          }
        }
        $('.downloadmodeldoc').on('click', function () {
          const filenamemodel = $(this).attr('name')
          const myForm = document.createElement('FORM')
          myForm.name = 'myForm'
          myForm.id = 'download_pdf'
          myForm.method = 'POST'
          myForm.enctype = 'multipart/form-data'
          const ctoken = $('form')
            .find("input[name='csrfmiddlewaretoken']")
            .attr('value')
          myForm.innerHTML = `<input type="hidden" name="csrfmiddlewaretoken" value=${ctoken}><input type="hidden" name="listOrDelete" value="download_uploaded_file"><input type="hidden" name="filename" value=${filenamemodel}>`
          $('.container-fluid').append(myForm)
          $('#download_pdf').trigger('submit')
          $('#download_pdf').remove()
        })

        if (modelsysteminteractions.length > 0) {
          $('#test_tablemodeldef tr').last().remove()
          for (const i in modelsysteminteractions) {
            const RowNo = $('#edit_tablemodeldef').find('table tr').last()
              .prevObject.length
            const templateStringmodeldef = `<tr>
              <td class="pt-3-half" contenteditable="true" id="${
                'system_type_model_def_' + RowNo
              }" required>
              <input type="text" value=${
                modelsysteminteractions[i].system_type
              } pattern="^[a-zA-Z_.-]*$" title="Only Alphabets, _ ,- are accepted">
              </td>
              <td class="pt-3-half" contenteditable="true" id="${
                'system_name_model_def' + RowNo
              }" required>
              <input type="text" value=${
                modelsysteminteractions[i].system_name
              } pattern="^[a-zA-Z_.-]*$" title="Only Alphabets, _ ,- are accepted">
              </td>
              <td class="pt-3-half" contenteditable="true" id="${
                'steps_model_def' + RowNo
              }" required>
              <input type="text" value=${
                modelsysteminteractions[i].step_number
              } /pattern="^[a-zA-Z_.-]*$" title="Only Alphabets, _ ,- are accepted">
              </td>
              <td>
                  <span class="table-addmodeldef" id=${
                    'add_' + RowNo
                  }><button type="button"
                          class="btn  btn-primary btn-rounded btn-sm my-0">Add</button></span>
              </td>
              <td>
                  <span class="table-removemodeldef" id=${
                    'remove_' + RowNo
                  }><button type="button" style="background-color:black"
                          class="btn btn-danger btn-rounded btn-sm my-0">Remove</button></span>
              </td>
              </tr>`
            const table = document.getElementById('test_tablemodeldef')
            const index = $(this).parents('tr').index()
            const row = table.insertRow(index)
            row.innerHTML = templateStringmodeldef

            // eslint-disable-next-line no-use-before-define
            $('#remove_' + RowNo).click(removeFuncmodel)
            // eslint-disable-next-line no-use-before-define
            $('#add_' + RowNo).click(addFuncmodel)
          }
        } else {
          // eslint-disable-next-line no-use-before-define
          $('.table-removemodeldef').click(removeFuncmodel)
          // eslint-disable-next-line no-use-before-define
          $('.table-addmodeldef').click(addFuncmodel)
        }

        if (modelstakeholders.length > 0) {
          for (const i in modelstakeholders) {
            $('#modeldefstakeholders_table_body').append(
              '<tr>' +
                '<td><center>' +
                `<input type="text" name="steps" value="${modelstakeholders[i].steps}" maxlength="255" id="id_model_description_processmodeldef" class="textinput textInput form-control is-invalid" readonly>` +
                '</center></td>' +
                `<td class="stakeholdersselect" data-selected="${modelstakeholders[i].stakeholders}"><center>` +
                htmlusers +
                '</center></td>' +
                `<td class="stakeholdersselect" data-selected="${modelstakeholders[i].approvers}"><center>` +
                htmlusers +
                '</center></td></tr>'
            )
          }
          $('.stakeholdersselect').each(function () {
            $(this).find('select').val($(this).data('selected'))
          })
        }

        function removeFuncmodel() {
          $(this).closest('tr').detach()
        }
        $('.table-removemodeldefdocument').click(removeFuncmodel)

        // eslint-disable-next-line no-use-before-define
        $('.table-addmodeldefdocument').click(addFuncmodeldocument)
        function addFuncmodeldocument() {
          const RowNodocument = $('#edit_tablemodeldefdocument')
            .find('table tr')
            .last().prevObject.length
          const templateStringmodeldefdocument = `<tr>
              <td class="pt-3-half" contenteditable="true" id="${
                'document_model_def' + RowNodocument
              }" required>
              <input type="text">
              </td>
              <td class="pt-3-half" contenteditable="true" id="${
                'upload_model_defdocument' + RowNodocument
              }"" required>
              <div class="custom-file">
              <input type="file" id="myfile" name="${
                'myfile' + RowNodocument
              }" class="custom-file-input modeldeffile">
              <label class="custom-file-label">Choose file</label>
          </div>
              </td>
              <td></td>
              <td>
                  <span class="table-addmodeldefdocument" id=${
                    'adddocument_' + RowNodocument
                  }><button type="button"
                          class="btn  btn-primary btn-rounded btn-sm my-0">+</button></span>
              </td>
              <td><center>
                  <span class="table-removemodeldefdocument" id=${
                    'removedocument_' + RowNodocument
                  }><button type="button" style="background-color:black"
                          class="btn btn-danger btn-rounded btn-sm my-0">-</button></span>
                          </center></td>
              </tr>`
          const table = document.getElementById(
            'test_tablemodeldefdocument'
          )
          const index = $(this).parents('tr').index() + 1
          const row = table.insertRow(index)
          row.innerHTML = templateStringmodeldefdocument

          $('#removedocument_' + RowNodocument).click(removeFuncmodel)
          $('#adddocument_' + RowNodocument).click(addFuncmodeldocument)
        }

        function addFuncmodel() {
          const RowNo = $('#edit_tablemodeldef').find('table tr').last()
            .prevObject.length
          const templateStringmodeldef = `<tr>
              <td class="pt-3-half" contenteditable="true" id="${
                'system_type_model_def_' + RowNo
              }" required>
              <input type="text" pattern="^[a-zA-Z_.-]*$" title="Only Alphabets, _ ,- are accepted">
              </td>
              <td class="pt-3-half" contenteditable="true" id="${
                'system_name_model_def' + RowNo
              }" required>
              <input type="text" pattern="^[a-zA-Z_.-]*$" title="Only Alphabets, _ ,- are accepted">
              </td>
              <td class="pt-3-half" contenteditable="true" id="${
                'steps_model_def' + RowNo
              }" required>
              <input type="text" pattern="^[a-zA-Z_.-]*$" title="Only Alphabets, _ ,- are accepted">
              </td>
              <td>
                  <span class="table-addmodeldef" id=${
                    'add_' + RowNo
                  }><button type="button"
                          class="btn  btn-primary btn-rounded btn-sm my-0">+</button></span>
              </td>
              <td><center>
                  <span class="table-removemodeldef" id=${
                    'remove_' + RowNo
                  }><button type="button" style="background-color:black"
                          class="btn btn-danger btn-rounded btn-sm my-0">-</button></span>
              </center></td>
              </tr>`
          const table = document.getElementById('test_tablemodeldef')
          const index = $(this).parents('tr').index() + 1
          const row = table.insertRow(index)
          row.innerHTML = templateStringmodeldef

          $('#remove_' + RowNo).click(removeFuncmodel)
          $('#add_' + RowNo).click(addFuncmodel)
        }

        table = $('#model_stakeholders_table').DataTable({
          // eslint-disable-line no-unused-vars
          searching: false,
          ordering: false,
          info: false,
          bPaginate: false,
          bLengthChange: false,
        })
        $('#loadbuttontemplate').on('click', function () {
          $.ajax({
            url: `/users/${urlPath}/model_def_get_data/`,
            data: {
              template_name: $('.selectworkflowtemplate').val(),
              operation: 'fetch_steps_model_def',
            },
            type: 'POST',
            dataType: 'json',
            success: function (data) {
              let templateWorkflowSteps = data.templateWorkflowSteps
              templateWorkflowSteps = JSON.parse(
                templateWorkflowSteps.replace(/&quot;/g, '"')
              )
              $('#modeldefstakeholders_table_body').empty()
              for (const i in templateWorkflowSteps) {
                $('#modeldefstakeholders_table_body').append(
                  '<tr>' +
                    '<td><center>' +
                    `<input type="text" name="steps" value="${templateWorkflowSteps[i]}" maxlength="255" id="id_model_description_processmodeldef" class="textinput textInput form-control is-invalid" readonly>` +
                    '</center></td>' +
                    '<td><center>' +
                    htmlusers +
                    '</center></td>' +
                    '<td><center>' +
                    htmlusers +
                    '</center></td></tr>'
                )
              }
            },
          })
        })

        $('.modeldeffile').change(function (e) {
          const fileName = e.target.files[0].name
          $(this).parent().find('.custom-file-label').html(fileName)
        })

        $('#savebuttontemplate').on('click', function () {
          const datadictdef = {}
          modalbody
            .find(':input[type=text],select,input[type=file]')
            .each(function () {
              datadictdef[$(this).attr('name')] = $(this).val()
            })
          const stakeholdersTableArray = []
          $('table#model_stakeholders_table tr').each(function () {
            const arrayOfThisRow = []
            const tableData = $(this).find(
              ':input[type=text],select,input[type=file]'
            )
            if (tableData.length > 0) {
              tableData.each(function () {
                arrayOfThisRow.push($(this).val())
              })
              stakeholdersTableArray.push(arrayOfThisRow)
            }
          })
          const systeminteractionsTableArray = []
          $('table#test_tablemodeldef tr').each(function () {
            const arrayOfThisRow2 = []
            const tableData2 = $(this).find(
              ':input[type=text],select,input[type=file]'
            )
            if (tableData2.length > 0) {
              tableData2.each(function () {
                arrayOfThisRow2.push($(this).val())
              })
              systeminteractionsTableArray.push(arrayOfThisRow2)
            }
          })
          const modeldocTableArray = []
          $('table#test_tablemodeldefdocument tr').each(function () {
            const arrayOfThisRow3 = []
            const tableData3 = $(this).find(
              ':input[type=text],select,input[type=file]'
            )
            if (tableData3.length > 0) {
              tableData3.each(function () {
                arrayOfThisRow3.push($(this).val())
              })
              modeldocTableArray.push(arrayOfThisRow3)
            }
          })
          const form = $('form#documentform')[0]
          const formData = new FormData(form)

          const filenamearray = []
          $('form#documentform')
            .find(':input[type=file]')
            .each(function () {
              filenamearray.push($(this).attr('name'))
            })

          formData.append('datadictdef', JSON.stringify(datadictdef))
          formData.append(
            'stakeholdersTableArray',
            JSON.stringify(stakeholdersTableArray)
          )
          formData.append(
            'systeminteractionsTableArray',
            JSON.stringify(systeminteractionsTableArray)
          )
          formData.append(
            'modeldocTableArray',
            JSON.stringify(modeldocTableArray)
          )
          formData.append('filenamearray', JSON.stringify(filenamearray))
          $.ajax({
            url: `/users/${urlPath}/standard_update_save_master_form_modeldef/`,
            data: formData,
            type: 'POST',
            contentType: false,
            processData: false,
            // eslint-disable-next-line no-unused-vars
            success: function (data) {
              windowLocationAttr.reload()
            },
            error: function () {
              Swal.fire({icon: 'error',text: 'Error! Please try again.'});
            },
          })
        })
      } else if (String(editName) === 'Constraint') {
        modalbody.append(html4)

        modalbody.find('select').each(function () {
    $(this).select2()
        })

        $('.selectTable').on('change', function () {
          $.ajax({
            url: `/users/${urlPath}/constriant_get_data/`,
            data: {
              table_name: $(this).val(),
              operation: 'fetch_table_columns_constraint',
            },
            type: 'POST',
            dataType: 'json',
            success: function (data) {
              $('.selectColumn').empty()
              $('.selectMapping').empty()
              $('.selectValue').empty()
              for (const i in data.columnList) {
                $('.selectColumn').append(
                  `<option value="${data.columnList[i]}">${data.columnList[i]}</option>`
                )
                $('.selectMapping').append(
                  `<option value="${data.columnList[i]}">${data.columnList[i]}</option>`
                )
              }
            },
            error: function () {
              Swal.fire({icon: 'error',text: 'Error! Please try again.'});
            },
          })
        })

        $('.selectConstraintType').on('change', function () {
          const reader = $('.selectConstraintType option:selected').attr(
            'data-type'
          )
          if (String(reader) === 'Array') {
            $(this)
              .parent()
              .parent()
              .find('div')
              .eq(3)
              .find('select')
              .empty()
            $(this)
              .parent()
              .parent()
              .find('div')
              .eq(3)
              .find('select')
              .attr('disabled', 'disabled')
            $(this)
              .parent()
              .parent()
              .find('div')
              .eq(3)
              .find('select')
              .empty()
            $(this)
              .parent()
              .parent()
              .find('div')
              .eq(1)
              .find('span')
              .show()
          } else {
            $(this)
              .parent()
              .parent()
              .find('div')
              .eq(1)
              .find('span')
              .show()
            $(this)
              .parent()
              .parent()
              .find('div')
              .eq(3)
              .find('select')
              .empty()
            $(this)
              .parent()
              .parent()
              .find('div')
              .eq(3)
              .find('select')
              .removeAttr('disabled')
            if (String(reader) === 'Grouped') {
              $('.selectValue').prop('multiple', true)

              $('.selectValue').css('overflow-y', 'scroll')

              $('.selectValue').select2()
              $(this)
                .parent()
                .parent()
                .find('div')
                .eq(3)
                .find('.select2-selection--multiple')
                .css({ 'max-height': '4rem', overflow: 'auto' })
            } else {
              $('.selectValue').prop('multiple', false)

              $('.selectValue').select2()
              $(this)
                .parent()
                .parent()
                .find('div')
                .eq(3)
                .find('.select2-selection--multiple')
                .css({ 'max-height': '4rem', overflow: 'visible' })
            }
          }
        })

        $('.selectConstraintType')
          .off('select2')
          .on('select2:select', function () {
            $('.selectColumn').append(
              '<option value="" selected disabled>Select Constraint Parameter</option'
            )

            const valuer = $(this)
              .parent()
              .parent()
              .find('.form-group')
              .eq(5)
              .find('select option:selected')
              .attr('data-type')
            if (valuer === 'Array') {
              $(this)
                .parent()
                .parent()
                .find('div')
                .eq(3)
                .find('label')
                .find('span')
                .hide()
            } else {
              $(this)
                .parent()
                .parent()
                .find('div')
                .eq(3)
                .find('label')
                .find('span')
                .show()
              if (
                String(
                  $('.selectColumn:selected') !== null &&
                    $(this).attr('data-type')
                ) === 'Array'
              ) {
                $('.selectValue').append(
                  '<option value=""disabled>Select Constraint Parameter Value</option'
                )
                $(this)
                  .parent()
                  .parent()
                  .find('div')
                  .eq(3)
                  .find('label')
                  .find('span')
                  .hide()
              }
            }
          })

        let rulesSet = ''
        $('.selectColumn').on('change', function () {
          const colvar = $(this).val()

          const columnType = $(this)
            .parent()
            .parent()
            .find('.form-group')
            .eq(5)
            .find('select option:selected')
            .attr('data-type')

          const tableVAR = $('.selectTable').val()
          $.ajax({
            url: `/users/${urlPath}/constriant_get_data/`,
            data: {
              table_name: tableVAR,
              column_name: colvar,
              operation: 'fetch_table_columns_val_constraint',
            },
            type: 'POST',
            dataType: 'json',
            success: function (data) {
              if (columnType === 'Array') {
                $('.selectValue').empty()
              } else {
                $('.selectValue').empty()
                for (const i in data.columnList) {
                  $('.selectValue').append(
                    new Option(
                      data.columnList[i],
                      data.columnList[i],
                      false,
                      false
                    )
                  )
                }
              }
            },
            error: function () {
              Swal.fire({icon: 'error',text: 'Error! Please try again.'});
            },
          })
        })

        rulesSet = data.columnList.rule_set
        $('.constraint_usecase')
          .val(data.columnList.use_case)
          .trigger('change')

        $('.condition_type').on('change', function () {
          const conditionDatatype = $(this).val()
          const conditionAdder = $(this)
            .parent()
            .parent()
            .find('.form-group')
            .eq(7)

          if (String(conditionDatatype) === 'Character') {
            conditionAdder.find('.condition_name').empty()
            conditionAdder
              .find('.condition_name')
              .append(
                new Option('Starts With', 'Starts With', false, false)
              )
            conditionAdder
              .find('.condition_name')
              .append(new Option('Ends With', 'Ends With', false, false))
            conditionAdder
              .find('.condition_name')
              .append(new Option('Contains', 'Contains', false, false))
            conditionAdder
              .find('.condition_name')
              .append(
                new Option('Not Contains', 'Not Contains', false, false)
              )
            conditionAdder
              .find('.condition_name')
              .append(
                new Option('Equal to', 'Equal to', false, false)
            )
            conditionAdder
              .find('.condition_name')
              .append(
                new Option('Not Equal to', 'Not Equal to', false, false)
            )
            conditionAdder
              .find('.condition_name')
              .append(
                new Option('In', 'In', false, false)
            )
            conditionAdder
              .find('.condition_name')
              .append(
                new Option('Not In', 'Not In', false, false)
            )
          } else if (String(conditionDatatype) === 'Numeric') {
            conditionAdder.find('.condition_name').empty()
            conditionAdder
              .find('.condition_name')
              .append(new Option('Equal to', 'Equal to', false, false))
            conditionAdder
              .find('.condition_name')
              .append(
                new Option('Not Equal to', 'Not Equal to', false, false)
              )
            conditionAdder
              .find('.condition_name')
              .append(
                new Option('Greater than', 'Greater than', false, false)
              )
            conditionAdder
              .find('.condition_name')
              .append(
                new Option('Smaller than', 'Smaller than', false, false)
              )
            conditionAdder
              .find('.condition_name')
              .append(
                new Option(
                  'Greater than equal to',
                  'Greater than equal to',
                  false,
                  false
                )
              )
            conditionAdder
              .find('.condition_name')
              .append(
                new Option(
                  'Smaller than equal to',
                  'Smaller than equal to',
                  false,
                  false
                )
              )

            conditionAdder
              .find('.condition_name')
              .append(
                new Option('In', 'In', false, false)
            )
            conditionAdder
              .find('.condition_name')
              .append(
                new Option('Not In', 'Not In', false, false)
            )
          }
        })

        $('.condition_name').on("change",()=>{
          let constraint_condition = $('.condition_name').val()
          let tRow = $('.condition_type').parent().parent().find('.form-group')


          if(constraint_condition == 'In' || constraint_condition == "Not In"){

            if( !(tRow.eq(8).find('.select_input_value').hasClass("select2-hidden-accessible")) ){
              tRow.eq(8).find('.select_input_value').remove()
              tRow.eq(8).append('<select  class="select_input_value select2 form-control" name="inputs[]" multiple="true"></select>')
              tRow.eq(8).find('.select_input_value').select2({tags:true, placeholder: "Enter Threshold",})
            }

          }
          else{
            if( tRow.eq(8).find('.select_input_value').hasClass("select2-hidden-accessible") ){
              tRow.eq(8).find('.select_input_value').select2('destroy')
              tRow.eq(8).find('.select_input_value').remove()
              tRow.eq(8).append('<input style="max-height: 40px;overflow: hidden;" class=" select_input_value form-control p-2 textInput" placeholder="Enter Threshold">')
            }
          }
        })

        if ($('.selectConstraintType').attr('data-type') === 'Array') {
          $('.selectTable')
            .val(data.columnList.table_name)
            .trigger('change')
          $('.selectConstraintName')
            .val(data.columnList.constraint_name)
            .trigger('change')
          $('.selectConstraintType')
            .val(data.columnList.constraint_type)
            .trigger('change')
          $('.select_input_value')
            .val(data.columnList.threshold)
            .trigger('change')
          $('.status_type')
            .val(data.columnList.applicability_status)
            .trigger('change')
          $('.selectValue').val('').trigger('change')
          $('.columnReminder').hide()

          $('.valueReminder').hide()
          $('.condition_name')
            .val(data.columnList.condition)
            .trigger('change')
          setTimeout(function () {
            $('.selectColumn')
              .val(data.columnList.constraint_parameter)
              .trigger('change')
            $('.selectMapping')
              .val(data.columnList.unique_constraint_column)
              .trigger('change')
            $('.valueReminder').hide()
            setTimeout(function () {
              $('.condition_name')
                .val(data.columnList.condition)
                .trigger('change')
              $('.valueReminder').hide()
            }, 500)
          }, 250)
        } else {
          $('.selectTable')
            .val(data.columnList.table_name)
            .trigger('change')
          $('.selectConstraintName')
            .val(data.columnList.constraint_name)
            .trigger('change')
          $('.selectConstraintType')
            .val(data.columnList.constraint_type)
            .trigger('change')

          $('.select_input_value')
            .val(data.columnList.threshold)
            .trigger('change')
          $('.condition_name')
            .val(data.columnList.condition)
            .trigger('change')
          $('.condition_type')
            .val(data.columnList.condition_datatype)
            .trigger('change')
          $('.status_type')
            .val(data.columnList.applicability_status)
            .trigger('change')
          $('.selectValue')
            .val(data.columnList.constraint_parameter_value)
            .trigger('change')
          setTimeout(function () {
            $('.selectColumn')
              .val(data.columnList.constraint_parameter)
              .trigger('change')
            $('.columnReminder').hide()
            $('.valueReminder').hide()
            $('.selectMapping')
              .val(data.columnList.unique_constraint_column)
              .trigger('change')

            $('.condition_type')
              .val(data.columnList.condition_datatype)
              .trigger('change')

            setTimeout(function () {
              if (
                $('.selectConstraintType option:selected').attr(
                  'data-type'
                ) === 'Grouped'
              ) {
                $('.selectValue')
                  .val(data.columnList.constraint_parameter_value)
                  .trigger('change')
              } else {
                $('.selectValue')
                  .val(data.columnList.constraint_parameter_value)
                  .trigger('change')
              }
              $('.condition_type')
                .val(data.columnList.condition_datatype)
                .trigger('change')
              $('.condition_name')
                .val(data.columnList.condition)
                .trigger('change')
            }, 500)
          }, 1000)
        }

        // Constraint Selectable Fields
        const lengthListtable = $(`#listtable${listConstraintID}`)
        lengthListtable.find('div').each(function () {
          if (selectedFields.includes($(this).attr('data-name'))) {
            $(this).hide()
          } else if (additionalCol.includes($(this).attr('data-name'))) {
            $(this).hide()
          }
        })

        if (Object.prototype.hasOwnProperty.call(data, 'drop_list')) {
          const dropList = data.drop_list
          lengthListtable.find('div').each(function () {
            const colName = $(this).attr('data-name')
            if (dropList.includes(colName)) {
              $(this).css('display', 'none')
            }
          })
        }

        $('#savebuttonListinfo').on('click', function () {
          let saveDic = {}
          $(`#listtable${listConstraintID}`)
          $(`#listtable${listConstraintID}`).each(function () {
            let useCaseName = ''
            const columnType = $(this)
              .find('.form-group')
              .eq(5)
              .find('select option:selected')
              .attr('data-type')
            if (
              String(
                $(`#listtable${listConstraintID}`)
                  .find('div')
                  .eq(-1)
                  .attr('data-name')
              ) === 'use_case'
            ) {
              useCaseName = data.columnList.use_case
              useCaseName = $(this)
                .find('.form-group')
                .eq(10)
                .find('input')
                .val()
            } else {
              useCaseName = data.columnList.use_case
            }

            if (String(columnType) === 'Array') {
              saveDic = {
                rule_set: rulesSet,
                table_name: $(this)
                  .find('.form-group')
                  .eq(0)
                  .find('select')
                  .val(),
                constraint_parameter: $(this)
                  .find('.form-group')
                  .eq(1)
                  .find('select')
                  .val(),
                unique_constraint_column: $(this)
                  .find('.form-group')
                  .eq(2)
                  .find('select')
                  .val(),
                constraint_name: $(this)
                  .find('.form-group')
                  .eq(4)
                  .find('input')
                  .val(),
                constraint_type: $(this)
                  .find('.form-group')
                  .eq(5)
                  .find('select')
                  .val(),
                constraint_parameter_value: $(this)
                  .find('.form-group')
                  .eq(1)
                  .find('select')
                  .val(),

                condition_datatype: $(this)
                  .find('.form-group')
                  .eq(6)
                  .find('select')
                  .val(),
                condition: $(this)
                  .find('.form-group')
                  .eq(7)
                  .find('select')
                  .val(),
                threshold: $(this)
                  .find('.form-group')
                  .eq(8)
                  .find('.select_input_value')
                  .val(),
                applicability_status: $(this)
                  .find('.form-group')
                  .eq(9)
                  .find('select')
                  .val(),
                use_case: useCaseName,
              }
            } else if (String(columnType) === 'Grouped') {
              saveDic = {
                rule_set: rulesSet,
                table_name: $(this)
                  .find('.form-group')
                  .eq(0)
                  .find('select')
                  .val(),
                constraint_parameter: $(this)
                  .find('.form-group')
                  .eq(1)
                  .find('select')
                  .val(),
                unique_constraint_column: $(this)
                  .find('.form-group')
                  .eq(2)
                  .find('select')
                  .val(),
                constraint_name: $(this)
                  .find('.form-group')
                  .eq(4)
                  .find('input')
                  .val(),
                constraint_type: $(this)
                  .find('.form-group')
                  .eq(5)
                  .find('select')
                  .val(),
                constraint_parameter_value: JSON.stringify(
                  $(this).find('.form-group').eq(3).find('select').val()
                ),
                use_case: useCaseName,

                condition_datatype: $(this)
                  .find('.form-group')
                  .eq(6)
                  .find('select')
                  .val(),
                condition: $(this)
                  .find('.form-group')
                  .eq(7)
                  .find('select')
                  .val(),
                threshold: $(this)
                  .find('.form-group')
                  .eq(8)
                  .find('.select_input_value')
                  .val(),
                applicability_status: $(this)
                  .find('.form-group')
                  .eq(9)
                  .find('select')
                  .val(),
              }
            } else {
              saveDic = {
                rule_set: rulesSet,
                table_name: $(this)
                  .find('.form-group')
                  .eq(0)
                  .find('select')
                  .val(),
                constraint_parameter: $(this)
                  .find('.form-group')
                  .eq(1)
                  .find('select')
                  .val(),
                unique_constraint_column: $(this)
                  .find('.form-group')
                  .eq(2)
                  .find('select')
                  .val(),
                constraint_name: $(this)
                  .find('.form-group')
                  .eq(4)
                  .find('input')
                  .val(),
                constraint_type: $(this)
                  .find('.form-group')
                  .eq(5)
                  .find('select')
                  .val(),
                constraint_parameter_value: [
                  $(this).find('.form-group').eq(3).find('select').val(),
                ][0],
                use_case: useCaseName,

                condition_datatype: $(this)
                  .find('.form-group')
                  .eq(6)
                  .find('select')
                  .val(),
                condition: $(this)
                  .find('.form-group')
                  .eq(7)
                  .find('select')
                  .val(),
                threshold: $(this)
                  .find('.form-group')
                  .eq(8)
                  .find('.select_input_value')
                  .val(),
                applicability_status: $(this)
                  .find('.form-group')
                  .eq(9)
                  .find('select')
                  .val(),
              }
            }
            for (const key in saveDic) {
              if (selectedFields.includes(key)) {
                delete saveDic[key]
              }
            }
          })

          // Ajax here
          const url = windowLocation

          $.ajax({
            url: url + tableName + '/update_save_constraint/' + pk + '/',
            data: {
              saveDic: JSON.stringify(saveDic),
              operation: 'editConstraintTemplate',
              element_id: elementID,
            },
            type: 'POST',
            dataType: 'json',
            // eslint-disable-next-line no-unused-vars
            success: function (data) {
              window.location.href = url
            },
            error: function () {
              Swal.fire({icon: 'error',text: 'Error! Please try again.'});
            },
          })
        })
      }
      else {
        const data_append = $(data.form.html).find('.container-fluid').find('.font-weight-light').find('.card')
        var str = "<script>"
        str = str +
        `$('#list_view_edit_modal_` + elementID +`').find('input[datatype="DateField"]').each(function () {
          $(this).datepicker({
            dateFormat: 'yy-mm-dd',
            changeMonth: true,
            changeYear: true,
            constrainInput: true,
          }).css('z-index', '1051')
        })

        $('#list_view_edit_modal_` + elementID +`').find('input[datatype="DateTimeField"], input[datatype="TimeField"]').each(function () {
          var config = JSON.parse($(this).attr('data-dp-config'));
          $(this).datetimepicker({
              "showClose": true,
              "showClear": true,
              "showTodayButton": true,
              "format": config.options.format,
              "locale": "en"
          });
          $(this).datetimepicker({
              "showClose": true,
              "showClear": true,
              "showTodayButton": true,
              "format": config.options.format,
              "locale": "en"
          });
        })



        $('#list_view_edit_modal_` + elementID +`').find('.dtrangepicker').each(function () {
          $(this).daterangepicker({
            locale: {
                      format: 'YYYY-MM-DD',
                  }
           });
        })

        $('#list_view_edit_modal_` + elementID +`').find('.dttrangepicker').each(function () {
          $(this).daterangepicker({
            timePicker: true,
            timePicker24Hour: true,
            timePickerSeconds: true,
            locale: {
                      format: 'YYYY-MM-DD HH:mm:ss',
                  }
           })
        });

        $('#list_view_edit_modal_` + elementID +`').find('.ttrangepicker').each(function () {
          $(this).daterangepicker({
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
        })

        $('.popoverclass_card').popover({
          trigger: 'focus'
        })


        listview_auto_compute('`+ elementID + `')
        `
        str = str + "</script>"
        const data_script = $(data.form.script)
        if($(data.form.html).find('style').text() != ''){
        var data_style = $(data.form.html).find('style').text()
        data_style = "<style>" + data_style + "</style>"
        modalbody.append(data_style)
        }
        modalbody.append(data_append)
        $(modalbody).find(`#processFlowDesignDiv${elementID}`).parent().find('.fa-angle-down').attr('data-trans',data.data.transaction_id)
        modalbody.append(data_script)
        modalbody.find("input[data-cases], textarea[data-cases], select[data-cases]").on('change', function() {
          let casesArray = Object.keys(JSON.parse($(this).attr('data-cases')));
          modalbody.find("input[data-jsattr], select[data-jsattr], textarea[data-jsattr]").each(function () {
            let JSAttrConfig = JSON.parse($(this).attr('data-jsattr'));
            if (checkCaseDependence(casesArray, JSAttrConfig)) {
              jsFunc_.call(this);
            };
          });
        });

        let multi_level = false
        for (let [k, v] of Object.entries(data.data)) {
          if(k == "type_of_approval")
            if(v == "multi_level"){
              multi_level = true
            }
        }
        var autoPopulateConstantFields = [];
        modalbody.find('input[data-jsattr], select[data-jsattr], textarea[data-jsattr]').each(function() {
          let JSAttrConfig = JSON.parse($(this).attr('data-jsattr'));
          for (let i = 0; i < JSAttrConfig.length; i++) {
            const attrConfig = JSAttrConfig[i];
            if(["Show-hide", "Styling attribute", "Auto-populate Constant"].includes(attrConfig['parentvalue'])){
              jsFunc_.call(this, initialRun=true);
            }
            if (attrConfig['parentvalue'] == "Auto-populate Constant") {
              autoPopulateConstantFields.push($(this).attr('name').split("__")[1]);
            }
          }
        });

        modalbody.append(str)
        $(modalbody).find('.form-group').find('.form-group, .custom-control.custom-checkbox').each(function (i, el) {
          let fieldName = $(this).attr('id').replace('div_id_', '');
          for (let [key, value] of Object.entries(data.data)) {
            if(key == fieldName){
              if (data.auto_populate_precedence && autoPopulateConstantFields.includes(fieldName) && !data.auto_populate_precedence_on_scenario) {
                if ($(this).find('select') != null) {
                  $(this).find('select').select2();
                }
                continue
              } else {
                if ($(this).find('input') != null){
                  if($(this).find('input').hasClass('dtrangepicker')){
                    if(value != null && value.length > 0){
                      startdate = value.split(' - ')[0]
                      enddate = value.split(' - ')[1]
                      $(this).find('input').data('daterangepicker').setStartDate(startdate)
                      $(this).find('input').data('daterangepicker').setEndDate(enddate)
                    }else {
                      $(this).find('input').val('');
                    }
                  }else if($(this).find('input').hasClass('dttrangepicker')){
                    if(value != null && value.length > 0){
                      startdate = value.split(' - ')[0]
                      enddate = value.split(' - ')[1]
                      $(this).find('input').data('daterangepicker').setStartDate(startdate)
                      $(this).find('input').data('daterangepicker').setEndDate(enddate)
                    }else {
                      $(this).find('input').val('');
                    }
                  }else if($(this).find('input').hasClass('ttrangepicker')){
                    if(value != null && value.length > 0){
                      startdate = value.split(' - ')[0]
                      enddate = value.split(' - ')[1]
                      $(this).find('input').data('daterangepicker').setStartDate(startdate)
                      $(this).find('input').data('daterangepicker').setEndDate(enddate)
                    }else {
                      $(this).find('input').val('');
                    }
                  }else if($(this).find('input').hasClass('custom-file-input')){
                    $(this).find(".custom-file-label").html(value)
                  } else if ($(this).find('input').hasClass('checkboxinput')) {
                    if (value) {
                      $(this).find('input').prop('checked', true);
                    }
                  }else{
                    if (value) {
                      $(this).find('input').val(value).trigger('change');
                      $(this).find('input').attr('data-exisingValueEdit', value);
                    }
                  }
                  if ($(this).find('input').hasClass('check_validForm_now')) {
                    $(this).find('input').on("change", checkValidationNow);
                  }
                  if(template_type == "Approval Template"){
                    $(this).find('input').prop('readonly',true)
                    if(fieldName == "approver_group" || fieldName == "approver_user"){
                      if(multi_level){
                        $(this).find('input').parent().find('p').css('pointer-events', 'none');
                        $(this).find('input').parent().css('cursor', 'not-allowed');
                      }
                      else if(value == '[]'){
                        $(this).find('input').parent().find('p').css('pointer-events', 'none');
                        $(this).find('input').parent().css('cursor', 'not-allowed');
                      }else{
                        $(this).find('input').parent().find('p').css('pointer-events', 'all');
                      }
                    }
                  }
                }
                if ($(this).find('select') != null){
                  if(value){
                    if($(this).find('select').hasClass("user_logo")){
                      $(this).find('select').select2({
                        templateResult: formatState1,
                        templateSelection: formatState2
                      });
                      $(this).find('select').val(value).trigger('change');
                    }else{
                      if(value.startsWith("[") && value.endsWith("]") && !value.startsWith("[{") && !value.endsWith("}]")){
                        value_temp = JSON.parse(value)
                        va_temp = []
                        const contains = value_temp.some(element => {
                          if (element.includes("all")) {
                            va_temp.push("all")
                          }else{
                            va_temp.push(element)
                          }
                        });
                        value_temp = va_temp
                        if(value.length > 0){
                          $(this).find('select').val(value_temp).select2().trigger('change');
                        }
                      }else{
                        if(fieldName !== "approval_audit_log"){
                          if ($(this).find(`select > option[value='${value}']`).length > 0) {
                            $(this).find('select').val(value).select2().trigger('change');
                          } else if ($(this).find("select[data-is-serverside-fetch='yes']")) {
                            serverSideDataSearch(key, elementID);
                            $(this).find('select').append(`<option value="${value}" selected>${value}</option>`)
                            $(this).find('select').select2().trigger('change');
                          } else {
                            $(this).find('select').select2();
                          }
                        }
                      }
                    }
                    $(this).find('select').attr('data-exisingValueEdit', value);
                  } else {
                    if($(this).find('select').hasClass("user_logo")){
                      $(this).find('select').select2({
                        templateResult: formatState1,
                        templateSelection: formatState2
                      });
                    }else{
                      $(this).find('select').each(function(){
                        $(this).select2()
                      });
                    }
                  }
                  if ($(this).find('select').hasClass('check_validForm_now')) {
                    $(this).find('select').on("change.select2", checkValidationNow);
                  }
                  if(template_type == "Approval Template"){
                    $(this).find('select').prop('readonly',true)
                  }
                }
                if ($(this).find('textarea') != null){
                  $(this).find('textarea').val(value).trigger('change');
                  if(template_type == "Approval Template"){
                    $(this).find('textarea').prop('readonly',true)
                    if(fieldName == "approval_level_config"){
                      if(value == ""){
                        $(this).find('textarea').parent().find('p').css('pointer-events', 'none');
                        $(this).find('textarea').parent().css('cursor', 'not-allowed');
                      }else{
                        $(this).find('textarea').parent().find('p').css('pointer-events', 'all');
                      }
                    }
                  }

                  if(fieldName == "approval_level_config"){
                    if(data.hasOwnProperty("app_table_cols")){
                        $(this).find('textarea').parent().find('p').attr("data-app_table_cols",JSON.stringify(data.app_table_cols))
                    }else{
                        $(this).find('textarea').parent().find('p').attr("data-app_table_cols",JSON.stringify(["username", "first_name", "last_name"]))
                    }

                    if(data.hasOwnProperty("app_table_sep")){
                        $(this).find('textarea').parent().find('p').attr("data-app_table_sep",data.app_table_sep)
                    }else{
                        $(this).find('textarea').parent().find('p').attr("data-app_table_sep"," ")
                    }
                  }
                }
                if($(this).find("p[title='RTF editor']").length > 0){
                  if(value){
                    $(this).find("p[title='RTF editor']").attr('data-data',value)
                  }
                }
                if ($(this).find('textarea').hasClass('check_validForm_now')) {
                  $(this).find('textarea').on("change", checkValidationNow);
                }
                if (!data.auto_populate_precedence && autoPopulateConstantFields.includes(fieldName) && value) {
                  $(this).find('input, select, textarea').attr('data-existingValuePrecedence', value);
                }
                if (data.auto_populate_precedence_on_scenario) {
                  $(this).find('input, select, textarea').attr('data-autoPopPrecedenceScenario', "true");
                } else {
                  $(this).find('input, select, textarea').attr('data-autoPopPrecedenceScenario', "false");
                }
              }
            }
          }
        });

        var fileFieldsData  = data.file_fields_data;
        $(modalbody).find('input[datatype="FileField"],input[datatype="ImageField"]').each(function(){
          var identifier = $(this).attr('id').replace("id_", "");
          var fieldName = identifier.replace(`_${elementID}`, "");
          var existingFiles = {};
          if (fileFieldsData[fieldName]) {
            existingFiles = fileFieldsData[fieldName];
          }
          formFileUploadHandlerLV(identifier, existingFiles=existingFiles);
        });
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
          var conCatfields = $(modalbody).find(
            '[data-concatfield]'
          )
          if (conCatfields.length > 0){
            for (let k = 0; k < conCatfields.length; k++){
              var singleField = $(conCatfields).eq(k)
              var singleCardColumns = $(singleField).attr('data-concatfield')
              var singleCardDivider = $(singleField).attr('data-divider')
              var elementId = $(singleField).attr('data-id')
              var parsedSingleCardColumns = JSON.parse(singleCardColumns)
              var allOkFlag = 1
              for (let p in parsedSingleCardColumns){
                $('#id_' + parsedSingleCardColumns[p] + '_' + elementId).change(singleField,concatenationField)
              }
            }
          }
        modalbody.find('input, select, textarea').on('change', function() {
          jsChange.call(this);
        });
        try {
          for (let j = 0; j < names[elementID].length; j++) {
            if ($('#id_' + `${names[elementID][j]}`+ '_' + elementID).attr("data-is-serverside-fetch") == "yes") {
              serverSideDataSearch(names[elementID][j], elementID);
            } else {
              updateParent(elementID, names[elementID][j]) // eslint-disable-line no-unused-vars
            }
          }

          } catch (err) {}
        embeddedComputeHandler(elementID);
      }
      $(modalId).modal({backdrop: 'static', keyboard: false});
      $(modalId).modal('show');

      // list view edit modal save event
      modalbody.find("button[name='submit']").on('click', function () {
        $(`#creation_in_progress_${elementID}`).modal('show');
        $('body').css('pointer-events', 'none')
        let url = windowLocation
        for (let r = 0; r < item_code_list.length; r++) {
          if (
            Object.prototype.hasOwnProperty.call(
              item_code_list[r],
              elementID
            )
          ) {
            url = `/users/${urlPath}/` + item_code_list[r][elementID] + '/'
          }
        }
        modalbody
          .find('form')
          .append(
            `<input type="hidden" name="primary_key" value="${pk}">`
          )

        var view_name = ""
        temp_type = $(`#${elementID}_tab_content`).attr("data-template-type")
        if(temp_type == 'Multi Dropdown View'){
          view_name = $(`#tableTab${elementID}`).find("select").val()

          modalbody
          .find('form')
          .append(
            `<input type="hidden" name="view_name" value="${view_name}">`
          )
        }



        if (String(editName) === 'Flow Definition') {
          const workflowSteps = []
          $('.workflow_steps_table').each(function () {
            workflowSteps.push($(this).text())
          })
          const datadict = {}
          modalbody
            .find(':input[type=text],select,input[type=file]')
            .each(function () {
              datadict[$(this).attr('name')] = $(this).val()
            })

          $.ajax({
            url: url + tableName + '/update_save_flow_def/' + pk + '/',
            data: {
              operation: 'saveflowdef',
              datadict: JSON.stringify(datadict),
              listflowcolumnname: listflowcolumnname,
              mastertableflow: mastertableflow,
              masterColumnflow: masterColumnflow,
              listflowcolumndata: JSON.stringify(workflowSteps),
            },
            type: 'POST',
            dataType: 'json',
            success: function () {},
            error: function () {
              Swal.fire({icon: 'error',text: 'Error! Please try again.'});
            },
          })
        }
        else {
          let editSubmitFormUrl
          if (String(historyViewTemplate) === 'List View With History') {
            editSubmitFormUrl =
              url + tableName + '/update_save_history/' + pk + '/'
          } else {
            editSubmitFormUrl =
              url + tableName + '/update_save/' + pk + '/'
          }
          $(this).attr('formaction', editSubmitFormUrl)
        }
        $(this).attr('type', 'submit')
      })
      // init_reuse()
    },
    error: function () {
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    },
  })
}


// eslint-disable-next-line no-unused-vars
function fnShowHideListView(elementTabID) {
  // eslint-disable-line no-unused-vars
  const table = datatableDict[elementTabID]
  let allowSaveTemplate
  if (String(event.target.value) === 'Expand') {
    event.target.value = 'Contract'
    allowSaveTemplate = true
    document.getElementById(`example1_expand${elementTabID}`).innerHTML =
			'Contract'
    table.columns('.allColumnClass').visible(allowSaveTemplate)
    table.columns.adjust().draw(false)
    table.state.save()
  } else {
    event.target.value = 'Expand'
    document.getElementById(`example1_expand${elementTabID}`).innerHTML =
			'Expand'
    table.columns('.allColumnClass').visible(false)
    allowSaveTemplate = true
    table.columns([0, 1, 2, 3, 4]).visible(allowSaveTemplate, false)
    table.columns.adjust().draw(false)
    table.state.save()
  }
}

// Save Edited Data in List View
// eslint-disable-next-line no-unused-vars
function editModeListView(elementID) {
  const status = $(`#editListView${elementID}`).attr('data-edit-status')

  if (String(status) === 'off') {
    $(`#editListView${elementID}`).attr('data-edit-status', 'on')
    $(`#editListView${elementID}`).text('Edit Mode:ON').trigger('change')
    $(`#saveEditListView${elementID}`).css('display', 'inline-block')
    $(`#example1${elementID}`)
      .find('tbody')
      .find('tr')
      .find('td:not(:nth-child(1),:nth-child(2))')
      .find('div')
      .attr('contenteditable', true)
    $(`#example1${elementID}`)
      .find('tbody')
      .find('tr')
      .find('td:not(:nth-child(1),:nth-child(2))')
      .attr('contenteditable', true)
    $(`#example1${elementID}`)
      .find('tbody')
      .find('tr')
      .find('td:not(:nth-child(1),:nth-child(2))')
      .addClass('edit')
    $(`#example1${elementID}`)
      .find('tbody')
      .find('tr')
      .find('td:not(:nth-child(1),:nth-child(2))')
      .find('div')
      .addClass('edit')
    $(`#example1${elementID}`)
      .find('tbody')
      .find('tr')
      .find('td:not(:nth-child(1),:nth-child(2))')
      .find('div')
      .attr('data-elementID', elementID)
      $(`#example1${elementID}`)
      .find('tbody')
      .find('tr')
      .find('td:not(:nth-child(1),:nth-child(2))')
      .find('[data-button-view-detail]').attr('onclick','')
  } else {
    $(`#example1${elementID}`)
      .find('tbody')
      .find('tr')
      .find('td')
      .find('div')
      .attr('contenteditable', false)
    $(`#example1${elementID}`)
      .find('tbody')
      .find('tr')
      .find('td')
      .attr('contenteditable', false)
    $(`#example1${elementID}`)
      .find('tbody')
      .find('tr')
      .find('td:not(:nth-child(1),:nth-child(2))')
      .find('div')
      .removeAttr('data-elementID')
    $(`#saveEditListView${elementID}`).css('display', 'none')
    $(`#example1${elementID}`)
      .find('tbody')
      .find('tr')
      .find('td:not(:nth-child(1),:nth-child(2))')
      .removeClass('edit')
    $(`#example1${elementID}`)
      .find('tbody')
      .find('tr')
      .find('td:not(:nth-child(1),:nth-child(2))')
      .find('div')
      .removeClass('edit')
    $(`#editListView${elementID}`).attr('data-edit-status', 'off')
    $(`#editListView${elementID}`).text('Edit Mode:OFF').trigger('change')
    $(`#example1${elementID}`)
      .find('tbody')
      .find('tr')
      .find('td:not(:nth-child(1),:nth-child(2))').find('.multi_select_dropdown_listview').remove()
      $(`#example1${elementID}`)
      .find('tbody')
      .find('tr')
      .find('td:not(:nth-child(1),:nth-child(2))').find('.dropdown-content-list-view').remove()
      $(`#example1${elementID}`)
      .find('tbody')
      .find('tr')
      .find('td:not(:nth-child(1),:nth-child(2))')
      .find('div').css('display','block')
    $(`#example1${elementID}`)
    .find('tbody')
    .find('tr')
    .find('td:not(:nth-child(1),:nth-child(2))')
    .find('[data-button-view-detail]').attr('onclick','displayMultiSelectDetailValues.call(this)')
  }
}
// eslint-disable-next-line no-unused-vars
function findreplacesave(obj) {
  const elementID = obj.getAttribute('data-elementID')
  const itemCode = obj.getAttribute('pr_code')
  const modelName = obj.getAttribute('data-table-name')
  const is_find = obj.getAttribute('is_find')
  let columnName = $('option:selected', `#selectcolumn${elementID}`).attr(
    'name'
  )
  let replacecolumnName = $('option:selected', `#selectreplacecolumn${elementID}`).attr('name')
  const column = $('option:selected', `#selectreplacecolumn${elementID}`).val()
  const datatype = $('option:selected', `#selectreplacecolumn${elementID}`).attr(
    'data-type'
  )
  const fdict = {}
  if($('#text_basedip_' + elementID).is(":checked")){
    fdict.find = $(`#find${elementID}`).val()
  }else{
    fdict.find = $(`#show_textinputfind${elementID}`).val()
  }
  fdict.replace = $(`#replace${elementID}`).val()
  fdict.find_case = $(`#selectcase${elementID}`).val()
  if (String(datatype) === 'ForeignKey') {
    fdict.find = $('option:selected', `#find${elementID}`).attr('name')
    fdict.replace = $('option:selected', `#replace${elementID}`).attr('name')
  }
  fdict.is_find = obj.getAttribute('is_find')
  fdict.datatype = datatype
  let check_html_find = /<|>/.test(fdict.find);
  let check_html_replace = /<|>/.test(fdict.replace);
  if (check_html_find | check_html_replace){
    Swal.fire({
      icon: "error",
      text: "Unauthorised input. Please check and try again.",
    });
  }
  else{
    $.ajax({
      url: `/users/${urlPath}/${itemCode}/`,
      data: {
        model_name: modelName,
        element_id: elementID,
        column_name: columnName,
        replacecolumnName:replacecolumnName,
        fdict: JSON.stringify(fdict),
        template:$(obj).attr('template'),
        operation: 'find_and_replace',
      },
      type: 'POST',
      dataType: 'json',
      success: function (data) {
        $(`#findtext${elementID}`).empty()
        $(`#findtext${elementID}`).append(`<p style='color:red;'>${data.message}</p>`)
        $(`#findtext${elementID}`).append(`<div>
        <table class="table" id="findtable${elementID}" style="width:100%">
          <thead>
            <tr>
            </tr>
          </thead>
          <tbody class="font-weight-normal">
          </tbody>
        </table>
        </div>`);
        if (is_find != "True") {
          if (String(data.message) === 'Data updated successfully.') {
            $(`#example1${elementID}`).DataTable().draw()
            for(let rowIndx=0; rowIndx < Object.keys(data.rows[column]).length; rowIndx++) {
              $(`#findtable${elementID}`).find("tbody").append("<tr></tr>")
              for (i in data.rows) {
                if(rowIndx==0) {
                  $(`#findtable${elementID}`).find("thead").find("tr").append(`<th scope="col">${i}</th>`)
                }
                if(i == column) {
                  if (String(datatype) == 'MultiSelect') {
                    $(`#findtable${elementID}`).find("tbody").find("tr").last().append(`<td style="background-color: antiquewhite;">${data.rows[i][rowIndx]}</td>`)
                  }
                  else {
                    $(`#findtable${elementID}`).find("tbody").find("tr").last().append(`<td style="background-color: antiquewhite;"><strike class="text-muted">${data.rows[i][rowIndx]}</strike>&nbsp;${$(`#replace${elementID}`).val()}</td>`)
                  }
                  }
                  else {
                    $(`#findtable${elementID}`).find("tbody").find("tr").last().append(`<td>${data.rows[i][rowIndx]}</td>`)
                  }
              }
            }
          }
        }
        else {
          for(let rowIndx=0; rowIndx < Object.keys(data.rows[column]).length; rowIndx++) {
            $(`#findtable${elementID}`).find("tbody").append("<tr></tr>")
            for (i in data.rows) {
              if(rowIndx==0) {
                $(`#findtable${elementID}`).find("thead").find("tr").append(`<th scope="col">${i}</th>`)
              }
              if(i == column) {
                $(`#findtable${elementID}`).find("tbody").find("tr").last().append(`<td style="background-color: antiquewhite;">${data.rows[i][rowIndx]}</td>`)
              }
              else {
                $(`#findtable${elementID}`).find("tbody").find("tr").last().append(`<td>${data.rows[i][rowIndx]}</td>`)
              }
            }
          }
          $(`#findtable${elementID}`).DataTable({
            scrollX: true,
            autoWidth: true
          });
        }
      },
      // eslint-disable-next-line no-unused-vars
      error: function (data) {
        Swal.fire({icon: 'error',text: 'Error! Please try again.'});
      },
    })
  }

}

// eslint-disable-next-line no-unused-vars
function listviewClearall(elementID) {
  const itemCode = windowLocation.split('/')[4]
  const modelName = $(`#listview_clearall_${elementID}`).attr('model_name')
  var view_name = ""
  temp_type = $(`#${elementID}_tab_content`).attr("data-template-type")
  if(temp_type == 'Multi Dropdown View'){
    view_name = $(`#tableTab${elementID}`).find("select").val()
  }

  $.ajax({
    url: `/users/${urlPath}/DataManagement/`,
    data: {
      'element_id': elementID.split("__tab__")[0],
      'operation': "fetch_list_view_msgs",
      'messages' : JSON.stringify(["confirm_delete_message","successful_delete_message","unable_delete_foreignkey_message","unable_delete_notable_message"]),
      'view_name' : view_name
    },
    type: "POST",
    dataType: "json",
    success: function (data) {
      message=""
      icon=""
      if(data.confirm_delete_message){
        message = data.confirm_delete_message.message
        icon = data.confirm_delete_message.icon
      }
      iconHtml = ""
      if (icon){
        iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
      }

      custom_messages = data

      Swal.fire({
        icon: 'question',
        iconHtml :iconHtml,
        text: message || `This will delete all the records from the table. Are you sure?\n\nClick 'Yes' to confirm or click 'No' if you do not wish to reset it.`,
        showDenyButton: true,
        showCancelButton: true,
        confirmButtonText: 'Yes',
        denyButtonText:'No',
      }).then((result) => {
        if (result.isConfirmed) {
          $.ajax({
            url: `/users/${urlPath}/${itemCode}/`,
            data: {
              operation: 'listview_clearAll',
              model_name: modelName,
              elementid: elementID,
            },
            type: 'POST',
            dataType: 'json',
            success: function (data) {
              if (String(data.status) === 'success') {
                message=""
                icon=""
                if(custom_messages.successful_delete_message){
                  message = custom_messages.successful_delete_message.message
                  icon = custom_messages.successful_delete_message.icon
                }
                iconHtml = ""
                if (icon){
                  iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
                }

                Swal.fire({icon: 'success',iconHtml, text: message || 'Data deleted successfully!'}).then((result) => {
                  if (result.isConfirmed) {
                    windowLocationAttr.reload()
                  }
                })

              } else if (String(data.status) === 'foreignkey_detected') {
                message=""
                icon=""
                if(custom_messages.unable_delete_foreignkey_message){
                  message = custom_messages.unable_delete_foreignkey_message.message
                  icon = custom_messages.unable_delete_foreignkey_message.icon
                }
                iconHtml = ""
                if (icon){
                  iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
                }

                Swal.fire({icon: 'warning',iconHtml, text: message || `Other tables have Foreign Key references to ${modelName}, unable to delete data.` });

              } else {
                message=""
                icon=""
                if(custom_messages.unable_delete_notable_message){
                  message = custom_messages.unable_delete_notable_message.message
                  icon = custom_messages.unable_delete_notable_message.icon
                }
                iconHtml = ""
                if (icon){
                  iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
                }

                Swal.fire({icon: 'warning',iconHtml, text: message || "Table does not exist." });
              }
            },
            error: function () {
              Swal.fire({icon: 'error',text: 'Error! Please try again.'});
            },
          });
        };
      });

    },
    error: function () {
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    },
  });
}
// eslint-disable-line no-unused-vars
// eslint-disable-next-line no-unused-vars
function freezepanesave(This) {
  const elementID = $(This).attr('data-elementid')

  if (
    $(`#freeze_left_${elementID}`).is(':checked') &&
		$(`#freeze_right_${elementID}`).is(':checked')
  ) {
    Swal.fire({icon: 'warning',text:"Kindly select only one checkbox to freeze panes." });
  } else {
    if (
      $(`#freeze_left_${elementID}`).is(':not(:checked)') &&
			$(`#freeze_right_${elementID}`).is(':not(:checked)')
    ) {
      Swal.fire({icon: 'warning',text:"Kindly select atleast one checkbox to freeze panes." });
    }

    if ($(`#freeze_left_${elementID}`).is(':checked')) {
      try {
        fDict2[`example1${elementID}`].left = parseInt(cellIndex)
      } catch (err) {
        fDict2[`example1${elementID}`] = { left: 0, right: 0 }
        fDict2[`example1${elementID}`].left = parseInt(cellIndex)
      }
    }

    if ($(`#freeze_right_${elementID}`).is(':checked')) {
      try {
        fDict2[`example1${elementID}`].right = parseInt(
          cellColLen - cellIndex + 1
        )
      } catch (err) {
        fDict2[`example1${elementID}`] = { left: 0, right: 0 }
        fDict2[`example1${elementID}`].right = parseInt(
          cellColLen - cellIndex + 1
        )
      }
    }

    $('.cell_highlighted').removeClass('cell_selected')
    $('.cell_highlighted').removeClass('cell_highlighted')
    const table = $(`#example1${elementID}`).DataTable()

    new $.fn.dataTable.FixedColumns(table, fDict2[`example1${elementID}`])

    $(`#freeze_pane_modal_${elementID}`).modal('hide')
  }
}

// eslint-disable-next-line no-unused-vars
function freezePaneButton(This) {
  const elementID = $(This).attr('data-elementID')
  $('.freezeCheckbox').prop('checked', false)
  $(`#freeze_pane_modal_${elementID}`).modal('show')
}

// eslint-disable-next-line no-unused-vars
function unfreezepanesave(This) {
  const elementID = $(This).attr('data-elementid')

  if ($(`#freeze_left_${elementID}`).is(':checked')) {
    fDict2[`example1${elementID}`].left = 0
  }

  if ($(`#freeze_right_${elementID}`).is(':checked')) {
    fDict2[`example1${elementID}`].right = 0
  }

  const table = $(`#example1${elementID}`).DataTable()

  new $.fn.dataTable.FixedColumns(table, fDict2[`example1${elementID}`])

  $(`#freeze_pane_modal_${elementID}`).modal('hide')
}

// eslint-disable-next-line no-unused-vars
function datatableAdjustBtn() {
  setTimeout(() => {
    $(`#example1${$(this).attr('data-elementID')}`)
      .DataTable()
      .draw()
  }, 100)
}

// eslint-disable-next-line no-unused-vars
function calValList() {
  const valuesDic = {}
  const elementID = $(this).attr('data-id')
  const datatypeList = []
  const tableName = $(this).attr('data-table-name')
  const computedValueList = []

  $('#modalBody' + elementID)
    .find('form')
    .find('.form-row')
    .find('[data-computed-field="true"]')
    .each(function () {
      computedValueList.push(
        $(this)
          .attr('id')
          .replace('id_', '')
          .replace('_' + elementID, '')
      )
    })

  $('#modalBody' + elementID)
    .find('form')
    .find('.form-row')
    .find('input[data-field_name],select[data-field_name]')
    .each(function () {
      let compVal = $(this).val()
      const compDatatype = $(this).attr('datatype')
      let compCol = $(this)
        .attr('id')
        .replace('id_', '')
        .replace('_' + elementID, '')
      if (String(compVal) === '' || String(compVal) === 'NULL') {
        compVal = 'NaN'
      }
      valuesDic[compCol] = compVal
      datatypeList.push(compDatatype)
    })

  $.ajax({
    url: `/users/${urlPath}/constriant_get_data/`,
    data: {
      element_id: elementID,
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
          Swal.fire({icon: 'error',text: `Calculation error in : ${context.f_list[i]} - ${context.e_list[i]}`});
        }
      } else {
        for (const [key, value] of Object.entries(context.data[0])) {
          for (let i = 0; i < computedValueList.length; i++) {
            if (String(key) === computedValueList[i]) {
              $('#id_' + computedValueList[i] + '_' + elementID)
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

function formatterButton(This){ // eslint-disable-line no-unused-vars
  let elementID = $(This).attr('data-elementid')
  let modelName = $(This).attr('data-table-name')
  let tabHeaderName = $('a[data-toggle="tab"].active.l3items').find('span').text()
  let elementID2 = elementID;
  let itemCode =  $(This).attr('pr_code');
  let view_name = ""
  temp_type = $(`#${elementID}_tab_content`).attr("data-template-type")
  if(temp_type == 'Multi Dropdown View'){
    view_name = $(`#tableTab${elementID}`).find("select").val()
  }
  $(`#formatterTable1_${elementID}`).empty()
$.ajax({
    url: `/users/${urlPath}/processGraphModule/`,

    data: {
      'operation': 'dropFieldList',
      'tableName':modelName,
    },
    type: "POST",
    dataType: "json",
    success: function (data) {
      $(`#formatColumn1_${elementID}`).empty()
      for (let i = 0; i < data.fieldNameList.length; i++) {
        $(`#formatColumn1_${elementID}`).append(new Option(modelName+'-'+data.fieldList[i], modelName+'-'+data.fieldNameList[i]));
          }
      },
    error: function () {
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    }

})

  $.ajax({
    url: `/users/${urlPath}/processGraphModule/`,
    data: {
      'operation': 'load_formatter_config_L3',
      'tab_header_name':tabHeaderName,
      'element_id':elementID2.split('__')[0],
      'itemCode':itemCode,
      'modelName':modelName,
      'view_name':view_name,
    },
    type: "POST",
    dataType: "json",
    success: function (data) {
      if(data.formatter_tables.includes(modelName)) {
          if(data.formatter_tables.length > 0){
            for(let i=0;i<data.formatter_tables.length;i++){
              if(modelName == data.formatter_tables[i]){
              $(`#formatColumn1_${elementID}`).empty()
              for (let j = 0; j < data.fieldList.length; j++) {
                  $(`#formatColumn1_${elementID}`).append(new Option(data.formatter_tables[i]+'-'+data.fieldList[j], data.formatter_tables[i]+'-'+data.fieldNameList[j]));
              }
            }
            }
          }
        }

          if ("formatter_config" in  data){
            let colList = []
            let valList = {}
            $(`#formatterTable1_${elementID}`).empty()
            for(let [key,value] of Object.entries(data.formatter_config) ){

              valList[key] = value
              value = JSON.stringify(value)
              if(modelName == key.split('-')[0]){
                colList.push(key)
              }
              if(modelName == key.split('-')[0]){
              $(`#formatterTable1_${elementID}`).append(
                              `<tr>
                                <td style="text-align: center;" data-col_id="">${key.split("-")[0]}</td>
                                <td style="text-align: center;" data-col_id="">${key.split("-")[1]}</td>
                                <td style="text-align: center;">
                                  <i class="far fa-edit"" onclick="showFormatter.call(this)" style="color:var(--primary-color);cursor: pointer;" data-col_id="${key.split("-")[1]}" data-element_id="${elementID}" data-table_name = "${key.split('-')[0]}" data-title="Add formatter" data-col_config='${value}'></i>
                                </td>
                              </tr>`
                            );
              }
            }
            $(`#formatColumn1_${elementID}`).val(colList)
            $(`#configFormat1_${elementID}`).attr(`data-config_formatter1_${elementID2}`,JSON.stringify(valList))
            formatConfigD1 = valList
          }
      },
    error: function () {
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    }

})

  $(`#fmodal1_${elementID}`).modal('show')
}

function formatterColChange(This){ // eslint-disable-line no-unused-vars
  let dataList = $(This).val()
  let elementID = $(This).attr('id').replace("formatColumn1_","")
  let elementID2 = elementID
  let multi = $('.tab-pane.fade.active.show').find('.changeTab').text()
  let deletedCol = ""

  $(`#formatterTable1_${elementID}`).empty()

  for(let i=0;i<dataList.length;i++){
      $(`#formatterTable1_${elementID}`).append(
                    `<tr>
                      <td style="text-align: center;" data-col_id="">${dataList[i].split("-")[0]}</td>
                      <td style="text-align: center;" data-col_id="">${dataList[i].split("-")[1]}</td>
                      <td style="text-align: center;">
                        <i class="far fa-edit"" onclick="showFormatter.call(this)" style="color:var(--primary-color);cursor: pointer;" data-col_id="${dataList[i].split("-")[1]}" data-col_config='${JSON.stringify(formatConfigD1[dataList[i]])}' data-element_id="${elementID}" data-table_name = "${dataList[i].split("-")[0]}" data-title="Add formatter"></i>
                      </td>
                    </tr>`
                  );
    }

    if(multi){

      $(`#formatColumn1_${elementID}`).off("select2:unselect").on("select2:unselect", function (e) {
        deletedCol =  e.params.data.text
        delete formatConfigD1[deletedCol]

        $(`#configFormat1_${elementID}`).attr(`data-config_formatter1_${elementID2}`,JSON.stringify(formatConfigD1))
      });

    }else{
    let keyList = Object.keys(formatConfigD1)
    let difference = keyList.filter(x => !dataList.includes(x));

      for(let i=0;i<difference.length;i++){
        delete formatConfigD1[difference[i]]
      }

      $(`#configFormat1_${elementID}`).attr(`data-config_formatter1_${elementID2}`,JSON.stringify(formatConfigD1))
  }
}

function showFormatter(){ // eslint-disable-line no-unused-vars

    let colName = $(this).attr('data-col_id')
    let tableName = $(this).attr('data-table_name')
    let elementID = $(this).attr('data-element_id')
    let elementID2 = elementID

    $(`#Dformat1_${elementID}`).css("display","none")
    $(`#SFormat1_${elementID}`).css("display","none")
    $(`#syFormat1_${elementID}`).css("display","none")
    $(`#DTFormat1_${elementID}`).css("display","none")
    $(`#TimefFormat1_${elementID}`).css("display","none")
    $(`#fmodal2_${elementID}`).modal('show')

    $(`#formatOption1_${elementID}`).val("").trigger("change")
    $(`#sepFormat1_${elementID}`).prop('checked', false);
    $(`#decimalFormat1_${elementID}`).val("").trigger("change")
    $(`#formatDate1_${elementID}`).val("").trigger("change")
    $(`#formatTime1_${elementID}`).val("").trigger("change")
    $(`#symbolFormat1_${elementID}`).empty();
    $.ajax({
      url: `/users/${urlPath}/processGraphModule/`,
      data: {
        'operation': 'get_currency_list',
      },
      type: "POST",
      dataType: "json",
      success: function (data) {
        $(`#symbolFormat1_${elementID}`).append(`<option value="" disabled selected> None </option>`)
        for(let i=0;i<data.country_list.length;i++){
          $(`#symbolFormat1_${elementID}`).append(`<option value="${data.country_list[i]}"> ${data.country_list[i]} ${data.curr_list[i]} </option>`)
        }

      },
      error: function () {
        Swal.fire({icon: 'error',text: 'Error! Please try again.'});
      }
    });


    setTimeout(()=>{
    $(`#formatOption1_${elementID}`).val("").trigger("change")
    $(`#formatOption_${elementID}`).val("").trigger("select2:select")
    },200)


    let clickedConfig1 = {}
    let con = $(this).attr('data-col_config')
    if (con != "undefined"){
      clickedConfig1 = JSON.parse($(this).attr('data-col_config'))
      if (clickedConfig1["formatter"] == "number"){

        setTimeout(()=>{
            $(`#formatOption1_${elementID}`).val("number").trigger("change")
            $(`#formatOption1_${elementID}`).val("number").trigger("select2:select")
          },200)

          setTimeout(()=>{

            if (clickedConfig1["decimal"] != ""){
              $(`#decimalFormat1_${elementID}`).val(clickedConfig1["decimal"]).trigger("change")
            }

            if(clickedConfig1["separator"]){
              $(`#sepFormat1_${elementID}`).prop('checked', true);
            }

          },300)

      }

      if (clickedConfig1["formatter"] == "currency"){

        setTimeout(()=>{
            $(`#formatOption1_${elementID}`).val("currency").trigger("change")
            $(`#formatOption1_${elementID}`).val("currency").trigger("select2:select")
          },200)

          setTimeout(()=>{

            if (clickedConfig1["currency"]["decimal"] != ""){
              $(`#decimalFormat1_${elementID}`).val(clickedConfig1["currency"]["decimal"]).trigger("change")
            }

            if(clickedConfig1["currency"]["symbol"]){
              $(`#symbolFormat1_${elementID}`).val(clickedConfig1["currency"]["symbol"]).trigger("change")
            }

          },300)

      }

      if (clickedConfig1["formatter"] == "date"){

        setTimeout(()=>{
            $(`#formatOption1_${elementID}`).val("date").trigger("change")
            $(`#formatOption1_${elementID}`).val("date").trigger("select2:select")
          },200)

          setTimeout(()=>{

            if (clickedConfig1["date"] != ""){
              $(`#formatDate1_${elementID}`).val(clickedConfig1["date"]).trigger("change")
            }

          },300)

      }

      if (clickedConfig1["formatter"] == "time"){

        setTimeout(()=>{
            $(`#formatOption1_${elementID}`).val("time").trigger("change")
            $(`#formatOption1_${elementID}`).val("time").trigger("select2:select")
          },200)

          setTimeout(()=>{

            if (clickedConfig1["time"] != ""){
              $(`#formatTime1_${elementID}`).val(clickedConfig1["time"]).trigger("change")
            }

          },300)

      }

      if (clickedConfig1["formatter"] == "percentage"){

        setTimeout(()=>{
            $(`#formatOption1_${elementID}`).val("percentage").trigger("change")
            $(`#formatOption1_${elementID}`).val("percentage").trigger("select2:select")
          },200)

          setTimeout(()=>{

            if (clickedConfig1["percentage"]["decimal"] != ""){
              $(`#decimalFormat1_${elementID}`).val(clickedConfig1["percentage"]["decimal"]).trigger("change")
            }

          },300)

      }

      if (clickedConfig1["formatter"] == "scientific"){

        setTimeout(()=>{
            $(`#formatOption1_${elementID}`).val("scientific").trigger("change")
            $(`#formatOption1_${elementID}`).val("scientific").trigger("select2:select")
          },200)

          setTimeout(()=>{

            if (clickedConfig1["scientific"]["decimal"] != ""){
              $(`#decimalFormat1_${elementID}`).val(clickedConfig1["scientific"]["decimal"]).trigger("change")
            }

          },300)

      }
    }


    $(`#btn_formatSave1_${elementID}`).off('click').on("click", function(){

    let decimal = ""
    let currency = {}
    let scientific = {}
    let percentage = {}
    let dDate = ""
    let dTime = ""

    if($(`#formatOption1_${elementID}`).val() == "scientific" || $(`#formatOption1_${elementID}`).val() == "percentage" || $(`#formatOption1_${elementID}`).val() == "currency" || $(`#formatOption1_${elementID}`).val() == "date" || $(`#formatOption1_${elementID}`).val() == "time"){
      decimal = null
    }else{
      decimal = $(`#decimalFormat1_${elementID}`).val()
        if (decimal == ""){
          decimal = null
        }
    }

    if($(`#formatOption1_${elementID}`).val() == "currency"){

      currency["decimal"] = $(`#decimalFormat1_${elementID}`).val()
      currency["symbol"] = $(`#symbolFormat1_${elementID}`).val()

    }else{
      currency = null
    }

    if($(`#formatOption1_${elementID}`).val() == "scientific"){

      scientific["decimal"] = $(`#decimalFormat1_${elementID}`).val()

    }else{
      scientific = null
    }

    if($(`#formatOption1_${elementID}`).val() == "percentage"){

      percentage["decimal"] = $(`#decimalFormat1_${elementID}`).val()

    }else{
      percentage = null
    }

    if($(`#formatOption1_${elementID}`).val() == "date"){

      dDate = $(`#formatDate1_${elementID}`).val()

    }else{
      dDate = null
    }

    if($(`#formatOption1_${elementID}`).val() == "time"){

      dTime = $(`#formatTime1_${elementID}`).val()

    }else{
      dTime = null
    }

    formatConfigD1[tableName+'-'+colName] = {
            "formatter": $(`#formatOption1_${elementID}`).val(),
            "decimal": decimal,
            "separator": $(`#sepFormat1_${elementID}`).is(":checked"),
            "currency": currency,
            "scientific":scientific,
            "percentage":percentage,
            "date":dDate,
            "time":dTime,
            "table_name":tableName,

          }

    })

    $(`#fmodal2_${elementID}`).on('hidden.bs.modal', function(){

      $(`#configFormat1_${elementID}`).attr(`data-config_formatter1_${elementID2}`,JSON.stringify(formatConfigD1))

    })
}

function formatOptionChange(){ // eslint-disable-line no-unused-vars

  let elementID = $(this).attr("id").replace("formatOption1_","")

  if ($(this).val() == "number"){
    $(`#Dformat1_${elementID}`).css("display","block")
    $(`#SFormat1_${elementID}`).css("display","block")
    $(`#syFormat1_${elementID}`).css("display","none")
    $(`#DTFormat1_${elementID}`).css("display","none")
    $(`#TimefFormat1_${elementID}`).css("display","none")
  }else if($(this).val() == "currency"){
    $(`#Dformat1_${elementID}`).css("display","block")
    $(`#syFormat1_${elementID}`).css("display","block")
    $(`#SFormat1_${elementID}`).css("display","none")
    $(`#DTFormat1_${elementID}`).css("display","none")
    $(`#TimefFormat1_${elementID}`).css("display","none")
  }else if($(this).val() == "percentage" || $(this).val() == "scientific"){
    $(`#Dformat1_${elementID}`).css("display","block")
    $(`#SFormat1_${elementID}`).css("display","none")
    $(`#syFormat1_${elementID}`).css("display","none")
    $(`#DTFormat1_${elementID}`).css("display","none")
    $(`#TimefFormat1_${elementID}`).css("display","none")
  }else if($(this).val() == "date"){
    $(`#Dformat1_${elementID}`).css("display","none")
    $(`#SFormat1_${elementID}`).css("display","none")
    $(`#syFormat1_${elementID}`).css("display","none")
    $(`#DTFormat1_${elementID}`).css("display","block")
    $(`#TimefFormat1_${elementID}`).css("display","none")
  }else if($(this).val() == "time"){
    $(`#Dformat1_${elementID}`).css("display","none")
    $(`#SFormat1_${elementID}`).css("display","none")
    $(`#syFormat1_${elementID}`).css("display","none")
    $(`#DTFormat1_${elementID}`).css("display","none")
    $(`#TimefFormat1_${elementID}`).css("display","block")
  }else if($(this).val() == ""){
    $(`#Dformat1_${elementID}`).css("display","none")
    $(`#SFormat1_${elementID}`).css("display","none")
    $(`#syFormat1_${elementID}`).css("display","none")
    $(`#DTFormat1_${elementID}`).css("display","none")
    $(`#TimefFormat1_${elementID}`).css("display","none")
  }
}

function saveFormatconfig(){ // eslint-disable-line no-unused-vars

  let elementID = $(this).attr("element_id").split('__')[0];
  let tabHeaderName = $('a[data-toggle="tab"].active.l3items').find('span').text()
  let itemCode =  $(this).attr("pr_code");
  let view_name = ""
  temp_type = $(`#${elementID}_tab_content`).attr("data-template-type")
  if(temp_type == 'Multi Dropdown View'){
    view_name = $(`#tableTab${elementID}`).find("select").val()
  }
  $.ajax({
    url: `/users/${urlPath}/processGraphModule/`,
    data: {
      'operation': 'save_formatter_config_L3',
      'tab_header_name':tabHeaderName,
      'element_id':elementID,
      'itemCode':itemCode,
      'format_config':JSON.stringify(formatConfigD1),
      'view_name':view_name,
    },
    type: "POST",
    dataType: "json",
    success: function (data) {
      message=""
      icon=""
      if(data.save_formatters_message){
        message = data.save_formatters_message.message
        icon = data.save_formatters_message.icon
      }

      iconHtml = ""
      if (icon){
        iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
      }


      Swal.fire({icon: 'success',iconHtml, text: message || 'Configuration saved successfully!'}).then((result) => {
        if (result.isConfirmed) {
          windowLocationAttr.reload()
        };
      });

    },
    error: function () {
      Swal.fire({icon: 'error',text: 'Error! Failure in saving configuration. Please check your configuration and try again try again.'});
    }
  });

}


function addCompButton(This){// eslint-disable-line no-unused-vars

  let elementID = $(This).attr("data-elementID")
  let modelName = $(This).attr("data-table-name")

  $(`#existingComp_${elementID}`).prop('checked', false);
  $(`#newComp_${elementID}`).prop('checked', false);

  $(`#fieldmdl_${elementID}`).val("").trigger("change")
  $(`#compField_verbose_name_${elementID}`).val("").trigger("change")
  $(`#comp_Comp_Field_${elementID}`).val("").trigger("change")
  $(`#compfield_datatype_${elementID}`).val("").trigger("change")
  $(`#comp_null_field_edit_${elementID}`).val("").trigger("change")
  $(`#comp_unique_${elementID}`).val("").trigger("change")
  $(`#dropdown_${elementID}`).css('display','none')

  $(`#addCompFields_${elementID}`).modal('show')

  $(`#existingComp_${elementID}`).change(function() {
    $(`#dropdown1_${elementID}`).val("").trigger("change")

    if(this.checked && $(`#newComp_${elementID}`).is(':checked')) {
      Swal.fire({icon: 'warning',text:"Kindly select only one option." });
      $(`#existingComp_${elementID}`).prop('checked', false);
    } else if(this.checked){
      $(`#dropdown_${elementID}`).css('display','block')
    }else{
      $(`#dropdown_${elementID}`).css('display','none')
    }
});


$(`#newComp_${elementID}`).change(function() {
  if(this.checked && $(`#existingComp_${elementID}`).is(':checked')) {
    Swal.fire({icon: 'warning',text:"Kindly select only one option." });
    $(`#newComp_${elementID}`).prop('checked', false);
  }else if(this.checked){

    $(`#fieldmdl_${elementID}`).val("").trigger("change")
    $(`#compField_verbose_name_${elementID}`).val("").trigger("change")
    $(`#compfield_datatype_${elementID}`).val("").trigger("change")
    $(`#comp_null_field_edit_${elementID}`).val("").trigger("change")
    $(`#comp_unique_${elementID}`).val("").trigger("change")
    $(`#comp_Comp_Field_${elementID}`).val("").trigger("change")

  }
});

$(`#comp_EBDisplayButtonID_${elementID}`).off("click").on("click",function(){
  listViewComp = true
  listViewModelName = modelName
  listViewCompCol = $(this).parent().parent().parent().find(`#fieldmdl_${elementID}`).val()
  $("#EBDisplayModel").css('z-index',1052)
  $("#EBDisplayModel").modal("show")
  reloadCompConfig(listViewModelName+listViewCompCol)
})

$('#EBDisplayModel').on('hide.bs.modal', function() {
  listViewComp = false
  $("#where_condition").css("display","block")
  $("#export_data_equ").css("display","block")
  $("#EBDisplayModel").css('z-index',1050)
})

$('#EBDisplayModel').on('show.bs.modal', function() {

  $("#where_condition").css("display","none")
  $("#export_data_equ").css("display","none")

})

$('#save_workflow_equ').off("click").on("click",function(){

  SaveCompFlow(listViewModelName+listViewCompCol)

});

      $.ajax({
        url: `/users/${urlPath}/processGraphModule/`,
        data: { model_name: modelName,
                operation: 'get_fields_comp'
              },
        type: 'POST',
        dataType: 'json',
        success: function (data) {

          $(`#dropdown1_${elementID}`).empty()
          $(`#dropdown1_${elementID}`).append(
            '<option value="" selected disabled>Select Column</option>'
          )
          $.each(Object.keys(data), function (key, value) {
            const ftype = data[value].internal_type
            const vname = data[value].verbose_name
            if ((ftype == "IntegerField" || ftype == "BigIntegerField" || ftype == "FloatField" )){
              $(`#dropdown1_${elementID}`).append(
                `<option data-type="${ftype}" name="${value}" value="${vname}" data-act-name="${value}">${vname}</option>`
              )
            }
          })
        },
        error: function () {
          Swal.fire({icon: 'error',text: 'Error! Please try again.'});
        },
      });


      $(`#dropdown1_${elementID}`).off('select2:select').on('select2:select',function(){

        $.ajax({
          url: `/users/${urlPath}/DataManagement/`,
          data: { 'model_name': modelName,
                  'field_name': $(this).find(':selected').attr("data-act-name"),
                  'operation': 'attr_details'
                },
          type: "POST",
          dataType: "json",
          success: function (data){
            data = JSON.parse(data)

            let nvalue = ""
            let uvalue = ""

            if(data["Nullable"]){
              nvalue = "Yes"
            }else{
              nvalue = "No"
            }

            if(data["Unique"]){
              uvalue = "Yes"
            }else{
              uvalue = "No"
            }

            if (Object.keys(data).length > 0){
              $(`#fieldmdl_${elementID}`).val(data["Field_name"]).trigger("change")
              $(`#compField_verbose_name_${elementID}`).val(data["Front End Name"]).trigger("change")
              $(`#compfield_datatype_${elementID}`).val(data["Data Type"]).trigger("change")
              $(`#comp_null_field_edit_${elementID}`).val(nvalue).trigger("change")
              $(`#comp_unique_${elementID}`).val(uvalue).trigger("change")

              if(String(data["Computed Value"]) == "true"){
                $(`#comp_Comp_Field_${elementID}`).val("Yes").trigger("change")
              }else if(String(data["Computed Value"]) == "false"){
                $(`#comp_Comp_Field_${elementID}`).val("No").trigger("change")
              }

            }

          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          }
        })

      });

      $(`#btn_removeCompField_${elementID}`).off("click").on("click",function(){
        var view_name = ""
        temp_type = $(`#${elementID}_tab_content`).attr("data-template-type")
        if(temp_type == 'Multi Dropdown View'){
          view_name = $(`#tableTab${elementID}`).find("select").val()
        }

        $.ajax({
          url: `/users/${urlPath}/DataManagement/`,
          data: {
            'element_id': elementID.split("__tab__")[0],
            'operation': "fetch_list_view_msgs",
            'messages' : JSON.stringify(["remove_computed_message","remove_select_column_computed_message","remove_new_computed_message","remove_existing_computed_message","remove_existing_computed_message","confirm_remove_computed_message"]),
            'view_name' : view_name
          },
          type: "POST",
          dataType: "json",
          success: function (data) {

            if ($(`#existingComp_${elementID}`).is(':not(:checked)')){
              message=""
              icon=""
              if(data.remove_existing_computed_message){
                message = data.remove_existing_computed_message.message
                icon = data.remove_existing_computed_message.icon
              }

              iconHtml = ""
              if (icon){
                iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
              }

              Swal.fire({icon: 'warning',iconHtml, text: message || "Please select the existing field checkbox and the field name." });
            }

            if ($(`#newComp_${elementID}`).is(':checked')){
              message=""
              icon=""
              if(data.remove_new_computed_message){
                message = data.remove_new_computed_message.message
                icon = data.remove_new_computed_message.icon
              }

              iconHtml = ""
              if (icon){
                iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
              }

              Swal.fire({icon:'warning',iconHtml, text:message || "Unable to perform the operation in the new field." });
            }

            if($(`#existingComp_${elementID}`).is(':checked') && $(`#dropdown1_${elementID}`).val() == null){

              message=""
              icon=""
              if(data.remove_select_column_computed_message){
                message = data.remove_select_column_computed_message.message
                icon = data.remove_select_column_computed_message.icon
              }

              iconHtml = ""
              if (icon){
                iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
              }

              Swal.fire({icon:'warning',iconHtml,text: message || "Kindly select a column." });
            }

            if($(`#existingComp_${elementID}`).is(':checked') && $(`#dropdown1_${elementID}`).val() != null){
              message=""
              icon=""
              if(data.confirm_remove_computed_message){
                message = data.confirm_remove_computed_message.message
                icon = data.confirm_remove_computed_message.icon
              }

              iconHtml = ""
              if (icon){
                iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
              }

                var confirmDelete = null
                Swal.fire({
                  icon: 'warning',
                  iconHtml,
                  text: message || `Remove the computed field calculation?\n\nClick 'Yes' to confirm or 'No' if you do not wish to remove it.`,
                  showDenyButton: true,
                  showCancelButton: true,
                  confirmButtonText: 'Yes',
                  denyButtonText:'No',
                }).then((result) => {
                  if (result.isConfirmed) {
                     confirmDelete = true
                  }
                  else if (result.isDenied) {
                     confirmDelete = false
                  }
                })

                if(confirmDelete = true){
                  tablename = $(this).parent().parent().find(`#fieldmdl_${elementID}`).val()
                  let fieldDict = {}
                  let fieldList = []
                  fieldDict["fieldName"] = $(`#fieldmdl_${elementID}`).val()
                  fieldDict["fieldVerboseName"] = $(`#compField_verbose_name_${elementID}`).val()
                  fieldDict["fieldDatatype"] = $(`#compfield_datatype_${elementID}`).val()
                  fieldDict["fieldNull"] = $(`#comp_null_field_edit_${elementID}`).val()
                  fieldDict["fieldUnique"] = $(`#comp_unique_${elementID}`).val()
                  fieldDict["computedValue"] = "No"
                  fieldDict["fieldDefault"] = "0"

                  fieldList.push(fieldDict)

                  $.ajax({
                      url: `/users/${urlPath}/DataManagement/`,
                      data: {
                        'tablename': modelName,
                        'fieldDict': JSON.stringify(fieldList),
                        'operation': "removeCompField"
                      },
                      type: "POST",
                      dataType: "json",
                      success: function () {
                          $.ajax({
                            url: `/users/${urlPath}/DataManagement/`,
                            data: {
                              'pr_code': windowLocation.split("/")[4],
                              'operation': "regenCompField"
                            },
                            type: "POST",
                            dataType: "json",
                            success: function () {
                              var view_name = ""
                              temp_type = $(`#${elementID}_tab_content`).attr("data-template-type")
                              if(temp_type == 'Multi Dropdown View'){
                                view_name = $(`#tableTab${elementID}`).find("select").val()
                              }

                              $.ajax({
                                url: `/users/${urlPath}/DataManagement/`,
                                data: {
                                  'element_id': elementID.split("__tab__")[0],
                                  'operation': "fetch_list_view_msgs",
                                  'messages' : JSON.stringify(["remove_computed_message"]),
                                  'view_name' : view_name
                                },
                                type: "POST",
                                dataType: "json",
                                success: function (data) {
                                  message=""
                                  icon=""
                                  if(data.remove_computed_message){
                                    message = data.remove_computed_message.message
                                    icon = data.remove_computed_message.icon
                                  }

                                  iconHtml = ""
                                  if (icon){
                                    iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
                                  }

                                  Swal.fire({icon: 'success',iconHtml, text: message || 'Operation successful!'}).then((result) => {
                                    if (result.isConfirmed) {
                                      windowLocationAttr.reload();
                                    }
                                  })
                                },
                                error: function () {
                                  Swal.fire({icon: 'success',text: 'Error! Please try again.'});
                                }
                              });

                            },
                            error: function () {
                              Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                            }
                          });

                      },
                      error: function () {
                       Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                      }
                    });

                }
            }


          },
          error: function () {
           Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          }
        });


      })

      $(`#btn_formatCompField_${elementID}`).off("click").on("click",function(){

          let operation = ""
          if($(`#existingComp_${elementID}`).is(':checked')){
            operation = "editattributes"
          }

          if($(`#newComp_${elementID}`).is(':checked')){
            operation = "addelement"
          }

          let fieldDict = {}
          let fieldList = []
          fieldDict["fieldName"] = $(`#fieldmdl_${elementID}`).val()
          fieldDict["fieldVerboseName"] = $(`#compField_verbose_name_${elementID}`).val()
          fieldDict["fieldDatatype"] = $(`#compfield_datatype_${elementID}`).val()
          fieldDict["fieldNull"] = $(`#comp_null_field_edit_${elementID}`).val()
          fieldDict["fieldUnique"] = $(`#comp_unique_${elementID}`).val()
          fieldDict["computedValue"] = "Yes"
          fieldDict["fieldDefault"] = "0"

          fieldList.push(fieldDict)

          $.ajax({
              url: `/users/${urlPath}/DataManagement/`,
              data: {
                'tablename': modelName,
                'fieldDict': JSON.stringify(fieldList),
                'operation': operation
              },
              type: "POST",
              dataType: "json",
              success: function () {
                  $.ajax({
                    url: `/users/${urlPath}/DataManagement/`,
                    data: {
                      'pr_code': windowLocation.split("/")[4],
                      'operation': "regenCompField"
                    },
                    type: "POST",
                    dataType: "json",
                    success: function (data) {
                      var view_name = ""
                      temp_type = $(`#${elementID}_tab_content`).attr("data-template-type")
                      if(temp_type == 'Multi Dropdown View'){
                        view_name = $(`#tableTab${elementID}`).find("select").val()
                      }

                      $.ajax({
                        url: `/users/${urlPath}/DataManagement/`,
                        data: {
                          'element_id': elementID.split("__tab__")[0],
                          'operation': "fetch_list_view_msgs",
                          'messages' : JSON.stringify(["add_computed_message"]),
                          'view_name' : view_name
                        },
                        type: "POST",
                        dataType: "json",
                        success: function (data) {
                          message=""
                          icon=""
                          if(data.add_computed_message){
                            message = data.add_computed_message.message
                            icon = data.add_computed_message.icon
                          }

                          iconHtml = ""
                          if (icon){
                            iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
                          }

                          Swal.fire({icon: 'success',iconHtml, text: message || 'Operation successful!'}).then((result) => {
                            if (result.isConfirmed) {
                              windowLocationAttr.reload();
                            }
                          })
                        },
                        error: function () {
                          Swal.fire({icon: 'success',text: 'Error! Please try again.'});
                        }
                      });

                    },
                    error: function () {
                      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                    }
                  });

              },
              error: function () {
                Swal.fire({icon: 'error',text: 'Error! Please try again.'});
              }
            });

      });
}

function FilePreviewButton(e) {
  let prid = String($(e).closest('table').attr("id")).substring(8,);
  let fileName = $(e).find('u').text();
  $(`#FilePreviewModal_${prid}`).find('.modal-header').find('h5').text(fileName)
  $(`#FilePreviewModal_${prid}`).find('.modal-body').text("Loading...");
  $(`#FilePreviewModal_${prid}`).modal('show');

  let format = fileName.substring(fileName.lastIndexOf('.') + 1, fileName.length);
  let imageformats = ["PNG", "JPEG", "JPG", "BMP"]
  $.ajax({
    url: `/users/${urlPath}/processGraphModule/`,
    data: {
      'operation': 'get_file_preview',
      'file_name':fileName,
    },
    type: "POST",
    dataType: "html",
    success: function (data) {
      $(`#FilePreviewModal_${prid}`).find('.modal-body').empty();
      if (fileName.slice(0,5) == "https" ){
        if (fileName.slice(0,24)=='https://www.youtube.com/' || fileName.slice(0,17) =='https://youtu.be/' ){
        let youtubeId = fileName.slice(-11)
        let video = $(`<iframe allowfullscreen width="100%" height="500"
        src="https://www.youtube.com/embed/${youtubeId}">
        </iframe>`)
        video.appendTo('.filetoappend')
        }else if(fileName.slice(0,18) == 'https://vimeo.com/'){
          let vimeoId = fileName.slice(18, 27)
          let video = $(`<iframe allowfullscreen width="100%" height="500"
          src="https://player.vimeo.com/video/${vimeoId}">
          </iframe>`)
          video.appendTo('.filetoappend')
        } else{
          $(`#FilePreviewModal_${prid}`).find('.modal-body').text("Enter Only Youtube or Vimeo video Shareable Links")
        }
        $(`#FilePreviewModal_${prid}`).find('.modal-footer').find('a').prop('disabled',true)
        $(`#FilePreviewModal_${prid}`).find('.modal-footer').find('a').prop('download', '')
        $(`#FilePreviewModal_${prid}`).find('.modal-footer').find('a').removeAttr("href")
      }
      else{
      if (imageformats.includes(format.toUpperCase()))
      {
        let img = $('<img>');
        img.attr('src', `data:image/${format};base64,` + data);
        img.appendTo('.filetoappend');
        $(`#FilePreviewModal_${prid}`).find('.modal-footer').find('a').prop('disabled',false)
        $(`#FilePreviewModal_${prid}`).find('.modal-footer').find('a').prop('download', fileName)
        $(`#FilePreviewModal_${prid}`).find('.modal-footer').find('a').attr('href', `data:image/${format};base64,` + data)
      }else if(format =="mp4"){
        let video = $(`<video width="100%" height="100%" controls controlsList="nodownload">
        <source src="http://127.0.0.1:8080/media/uploaded_files/${fileName}" type="video/mp4">
      Your browser does not support the video tag.
      </video>`)
      video.appendTo('.filetoappend')
      $(`#FilePreviewModal_${prid}`).find('.modal-footer').find('a').prop('disabled',false)
      $(`#FilePreviewModal_${prid}`).find('.modal-footer').find('a').prop('download', fileName)
      $(`#FilePreviewModal_${prid}`).find('.modal-footer').find('a').attr("href",`http://127.0.0.1:8080/media/uploaded_files/${fileName}`)
      }
      else if(format =="webm"){
        let video = $(`<video width="100%" height="100%" controls controlsList="nodownload">
        <source src="http://127.0.0.1:8080/media/uploaded_files/${fileName}" type="video/webm">
      Your browser does not support the video tag.
      </video>`)
      video.appendTo('.filetoappend')
      $(`#FilePreviewModal_${prid}`).find('.modal-footer').find('a').prop('disabled',false)
      $(`#FilePreviewModal_${prid}`).find('.modal-footer').find('a').prop('download', fileName)
      $(`#FilePreviewModal_${prid}`).find('.modal-footer').find('a').attr("href",`http://127.0.0.1:8080/media/uploaded_files/${fileName}`)
      }else if(format =="ogv"){
        let video = $(`<video width="100%" height="100%" controls controlsList="nodownload">
        <source src="http://127.0.0.1:8080/media/uploaded_files/${fileName}" type="video/ogg">
      Your browser does not support the video tag.
      </video>`)
      video.appendTo('.filetoappend')
      $(`#FilePreviewModal_${prid}`).find('.modal-footer').find('a').prop('disabled',false)
      $(`#FilePreviewModal_${prid}`).find('.modal-footer').find('a').prop('download', fileName)
      $(`#FilePreviewModal_${prid}`).find('.modal-footer').find('a').attr("href",`http://127.0.0.1:8080/media/uploaded_files/${fileName}`)
      }
       else if (format == "pdf"){
        let pdfc = $(`<embed
        src="data:application/pdf;base64,${data}#toolbar=0"
        type="application/pdf"
        frameBorder="0"
        scrolling="auto"
        height="100%"
        width="100%"
        ></embed>`)
        pdfc.appendTo('.filetoappend')
        $(`#FilePreviewModal_${prid}`).find('.modal-footer').find('a').prop('disabled',false)
        $(`#FilePreviewModal_${prid}`).find('.modal-footer').find('a').prop('download', fileName)
        $(`#FilePreviewModal_${prid}`).find('.modal-footer').find('a').attr('href', `data:image/${format};base64,` + data)
      } else {
        $(`#FilePreviewModal_${prid}`).find('.modal-body').text(`Preview not available for .${format} file`);
        $(`#FilePreviewModal_${prid}`).find('.modal-footer').find('a').prop('disabled',false)
        $(`#FilePreviewModal_${prid}`).find('.modal-footer').find('a').prop('download', fileName)
        $(`#FilePreviewModal_${prid}`).find('.modal-footer').find('a').attr('href', `data:document/${format};base64,` + data)
      }
    }

    },
    error: function () {
      $(`#FilePreviewModal_${prid}`).find('.modal-body').text("Some error or preview not supported.");
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    }
  });
}
function HyperLinkingTables(obj){
  const elementId = obj.getAttribute('data-id')
  var dataList = obj.getAttribute('data-list')
  var text = $(obj).text()
  var extractedValues =JSON.parse(dataList)
  var masterColumn = extractedValues['masterColumn']
  var linkedTable = extractedValues['linkedTable']
  var linkedColumn = extractedValues['linkedColumn']
  var addlinkedColumn = JSON.stringify(extractedValues['LinkedAdditional'])
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
      $(`#hyper_linking_header${elementId}`).empty()
      $(`#hyper_linking_header${elementId}`).append(`<h5 class="modal-title">${linkedTable}</h5>
      <button type="button" class="close" data-dismiss="modal" aria-label="Close">
        <span aria-hidden="true">&times;</span>
      </button>`)
      var data = data['data']
      $(`#hyper_linking_body${elementId}`).empty();
      $(`#hyper_linking_body${elementId}`).append(
          `
          <table id="exampledata${elementId}" class="display compact" style="width:100%;">
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
      $(`#hyper_linking_modal${elementId}`).modal('show')
      $(`#exampledata${elementId}`).DataTable({
        "autoWidth": false,
        "scrollY": "35vh",
        "scrollX": "100%",
        "scrollCollapse": true,
        "ordering":false,
        orderCellsTop: true,
        responsive: true,
        "deferRender": true,
        "paging": true,
        "lengthMenu": [[1, 5, 50, -1], [1, 5, 50, "All"]],
        stripeClasses: false,
        "pageLength": 50,
        dom: 'lfBrtip',
        buttons: [
            {
                extend: 'collection',
                text: 'Export',
                buttons: [
                    {
                    extend: 'copy', title: '', exportOptions: {
                        columns: ':visible:not(.noVis)'
                    }
                    },
                    {
                    extend: 'excel', title: '', exportOptions: {
                        columns: ':visible:not(.noVis)'
                    }
                    },
                    {
                    extend: 'csv', title: '', exportOptions: {
                        columns: ':visible:not(.noVis)'
                    }
                    },
                    {
                    extend: 'pdf', title: '', exportOptions: {
                        columns: ':visible:not(.noVis)'
                    }
                    },
                ],
            },
            {
                extend: 'colvis',
                className: "scroller",
            }
        ],
        columnDefs: [
            {
                targets: "_all",
                className: 'dt-center allColumnClass all'
            },
        ],
      });
    },
    failure: function () {
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    },
  })

}

function emptyListViewModal(){
  var element_id = $(this).attr('data-element_id');
  const modalId = '#list_view_edit_modal_' + element_id;
  const modalbody = $(modalId).find('.modal-body');
  modalbody.empty();
  let url_string = window.location.pathname
  let f_occ = url_string.indexOf('/', url_string.indexOf('/') + 1)
  let s_occ = url_string.indexOf('/', url_string.indexOf('/') + f_occ +1)
  let t_occ = url_string.indexOf('/', url_string.indexOf('/') + s_occ +1)
  let app_code2 = url_string.substring(f_occ+1,s_occ)
  let current_dev_mode2 = url_string.substring(s_occ+1,t_occ)
  if(current_dev_mode2 != "Build" && current_dev_mode2 != "Edit"){
    current_dev_mode2 = "User"
  }
  $.ajax({
    url: `/users/${app_code2}/${current_dev_mode2}/processGraphModule/`,
    data : {
      operation : 'generate_script',
    },
    type: "POST",
    dataType: "json",
    success: function (data) {
      var script_div = '<div id = "create_view_script">' + data.script + '</div>'
      $('body').append(script_div);
      $('body').removeAttr('modal_pk');
      $('body').removeAttr('modal_table_name');
      $('body').removeAttr('modal_element_id');
      $('body').removeAttr('modal_url');
    },
    failure: function () {
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    },
  })

}

function checkCaseDependence(casesArray, JSAttrConfig) {
  for (let i = 0; i < JSAttrConfig.length; i++) {
    const attrConfig = JSAttrConfig[i];
    if(attrConfig.hasOwnProperty("cases")){
      if (casesArray.some(item => attrConfig.cases.includes(item))) {
        return true
      }
    }
  }
  return false
}

function getViewTable(elementID, view_name){

  let prCode = window.location.pathname.split('/')[4]
  let tabHeaderName = $('a[data-toggle="tab"].active.l3items').find('span').text()
  $.ajax({
    url: `/users/${urlPath}/processGraphModule/`,
   data: {
       'operation': 'fetchviewtable',
       'elementID': elementID,
       'view_name': view_name,
       'prCode': prCode,
       'tabHeaderName':tabHeaderName,
     },
     type: "POST",
     dataType:"json",
     success:function(data){

      $(`#${data.ele_id}_tab_content`).empty()
      $(`#${data.ele_id}_tab_content`).append(data.html)
      $(`#group_by_switch_user_configuration_${data.ele_id}`).attr('data-user',data.user_name)
      if (Object.keys(data.user_config_values).length>0){
        $(`#group_by_switch_user_configuration_${data.ele_id}`).attr('data-list2',JSON.stringify(data.user_config_values))
        $(`#example1${data.ele_id}`).attr('data-list-group-by1','data-list-group-by');
      }else{
        $(`#group_by_switch_user_configuration_${data.ele_id}`).attr('data-list2','')
        $(`#example1${data.ele_id}`).attr('data-list-group-by1','');
      }
      $('#bokehForm1'+data.ele_id).find('select').each(function(){
        parent = $(this).parent()
        $(this).select2({dropdownParent:parent})
      })
      $('#bokehForm1'+data.ele_id).prepend(`<input type="hidden" name="csrfmiddlewaretoken" value="${$('form').find("input[name='csrfmiddlewaretoken']").attr('value')}">`)
      $('#popup'+data.ele_id).find('form').prepend(`<input type="hidden" name="csrfmiddlewaretoken" value="${$('form').find("input[name='csrfmiddlewaretoken']").attr('value')}">`)
      $(`#tableTab${data.ele_id}`).find('div').find('select').val(view_name).trigger('change')
      $('#'+data.ele_id+'_tab_content').find('.card').find('.bodyListview').find('.mul_heading').find('h4').text(view_name)
      masterBaseDataFilter([data.ele_id],[data.pagination])
      masterUploadFunc([data.ele_id])
      masterStandardButtonFunc()
      masterPlotly([data.ele_id]);
      $('select.select2:not(.modal select.select2)').each(function(){
        parent = $(this).parent()
        $(this).select2({dropdownParent:parent})
      })
      $('.modal select.select2').each(function(){
        $(this).select2()
      })
      if((data.html).includes("plotCharts"+data.ele_id)){
        let chartSaveEleIdList_ = [data.ele_id];
        for(let i in chartSaveEleIdList_){
          $.ajax({
            url:`/users/${urlPath}/dynamicVal/`,
            data: {
              'operation':'saveChartConfigList',
              'element_id': chartSaveEleIdList_[i]
              },
              type: 'POST',
              dataType: "json",
              success: function (data) {
                if($(`#plotSection${chartSaveEleIdList_[i]}`).find(".nav-link").length < 2){
                  $(`#analysisAddTab${chartSaveEleIdList_[i]}`).trigger("click");
                }
                if(data["save"] != '' && data["save"] != undefined){
                  let saveData = data["save"];
                  for(let j = 0; j < saveData.length; j++){
                    if(saveData[j]["ElementID"] == chartSaveEleIdList_[i]){
                      if (saveData[j].hasOwnProperty("dropdown")){
                        if(view_name == saveData[j]["dropdown"]){
                          $("#plotSection"+chartSaveEleIdList_[i]).css("display","block");
                          data["save"] = saveData[j];
                          savedChartConfigFunc(data,"",chartSaveEleIdList_[i]);
                        }
                      }
                    }
                  }
                }
            },
            error: ()=>{
                Swal.fire({icon: 'error',text: 'Error! Please try again.'});
            }
          })
        }
      }

      $('#backgroundBlock').remove()
      $('body').css('pointer-events', 'all');
      var quickFiltersDiv = $(`#quickFiltersDiv${elementID}`)
      if (quickFiltersDiv.length>0){
        const itemCode = windowLocation.split('/')[4]
        var quickFiltersDivChildren = quickFiltersDiv.children()
        for (let k = 0; k < quickFiltersDivChildren.length; k++){
          if (quickFiltersDivChildren.eq(k).attr('data-div') == 'range_field'){
            ajaxQuickFilters('range_field',quickFiltersDivChildren.eq(k),elementID)
          }
          else if (quickFiltersDivChildren.eq(k).attr('data-div') == 'date_picker'){
            quickFiltersDivChildren.eq(k).find('.dtrangepicker').on('apply.daterangepicker', function(ev, picker) {
              $(this).val(picker.startDate.format('YYYY-MM-DD') + ' - ' + picker.endDate.format('YYYY-MM-DD'));
              $(this).attr('data-val',$(this).val())
              $(`#example1${elementID}`).DataTable().draw()
              });
              quickFiltersDivChildren.eq(k).find('.dtrangepicker').on('cancel.daterangepicker', function(ev, picker) {
                $(this).val('');
                $(this).attr('data-val',$(this).val())
                $(`#example1${elementID}`).DataTable().draw()
                });

          }
          else if (quickFiltersDivChildren.eq(k).attr('data-div') == 'select_field'){
            ajaxQuickFilters('select_field',quickFiltersDivChildren.eq(k),elementID)
          }else if (quickFiltersDivChildren.eq(k).attr('data-div') == 'multi_select'){
            ajaxQuickFilters('multi_select',quickFiltersDivChildren.eq(k),elementID)
          }
        }
      }
     },
     error: function () {
       Swal.fire({icon: 'error',text: 'Error! Please try again.'});
     }
    });

}

function checkGroupViewname(elementID){

  let prCode = window.location.pathname.split('/')[4]
  let tabHeaderName = $('a[data-toggle="tab"].active.l3items').find('span').text()
  $.ajax({
    url: `/users/${urlPath}/processGraphModule/`,
   data: {
       'operation': 'disable_col_val_multidropdown',
       'elementID': elementID,
       'prCode': prCode,
       'tabHeaderName':tabHeaderName,
     },
     type: "POST",
     dataType:"json",
     success:function(data){
      for(let [key,value] of Object.entries(data) ){
        if(value == "no"){
          $(`#tableTab${elementID}`).find(`select option[value="${key}"]`).attr('disabled',true)
          card_name = $(`#${elementID}_tab_content`).find('.card-body.bodyListview').find('.mul_heading').text()
          if(card_name == key){
            $(`#${elementID}_tab_content`).find('.card-body.bodyListview').empty()
            $(`#${elementID}_tab_content`).find('.card-body.bodyListview').append('<h4 style="font-size: 1.1rem;font-weight: 400;">You do not have access to the view. Please contact your administrator.</h4>')
          }
        }
      }
     },
     error: function () {
       Swal.fire({icon: 'error',text: 'Error! Please try again.'});
     }
    });

}


function showtextinput(obj){
  const elementID = obj.getAttribute('data-elementID')
  let is_selected = $('#text_basedip_' + elementID).is(":checked")

  if(is_selected){
    $('.show_textinput_div_'+elementID).css('display','none')
    $('#findlabel'+elementID).parent().css('display','flex')
    $('#findlabel'+elementID).css('display','block')
    $('#findlistL3'+elementID).css('display','block')
    $('#find'+elementID).css('display','block')
  }else{
    $('.show_textinput_div_'+elementID).css('display','flex')
    $('#findlabel'+elementID).parent().css('display','none')
    $('#findlabel'+elementID).css('display','none')
    $('#findlistL3'+elementID).css('display','none')
    $('#find'+elementID).css('display','none')
  }
}


function multiSelectDatatableInitializer(elementId, columnAlignmentDef=[]) {
  if (!columnAlignmentDef.length) {
    columnAlignmentDef = [
      {
        targets: "_all",
        className: 'dt-center allColumnClass all'
      }
    ]
  }
  $(`#listDetailTable${elementId}`).DataTable( {
    "autoWidth": true,
    "scrollY": "50vh",
    "scrollCollapse": true,
    "scrollX": "300",
    orderCellsTop: true,
    responsive: true,
    colReorder: {
        fixedColumnsLeft: 1,
    },
    "deferRender": true,
    "paging": true,
    "lengthMenu": [[1, 5, 50, -1], [1, 5, 50, "All"]],
    stripeClasses: false,
    "pageLength": 50,
    dom: 'lfrtip',
    "sScrollX": "100%",
    "scrollX": true,
    buttons: [
        {
            extend: 'collection',
            text: 'Export',
            buttons: [
            {
                extend: 'copy', title: '', exportOptions: {
                columns: ':visible:not(.noVis)'
                }
            },
            {
                extend: 'excel', title: '', exportOptions: {
                columns: ':visible:not(.noVis)'
                }
            },
            {
                extend: 'csv', title: '', exportOptions: {
                columns: ':visible:not(.noVis)'
                }
            },
            {
                extend: 'pdf', title: '', exportOptions: {
                columns: ':visible:not(.noVis)'
                }
            },
            ],
        },
        {
            extend: 'colvis',
            className: "scroller",
        }
        ],
        columnDefs: columnAlignmentDef,
  });
}


function displayMultiSelectDetailValues() {
  var m_col = $(this).attr('data-col');
  var columnAlignment = {};
  let columnAlignmentDef = [];
  if ($(this).attr('data-column-alignment')) {
    columnAlignment = $(this).attr('data-column-alignment');
    columnAlignment = JSON.parse(columnAlignment)
  } else {
    columnAlignmentDef.push(
      {
        targets: "_all",
        className: 'dt-center allColumnClass all',
      }
    );
  }
  var element_id = $(this).attr('data-element-id');
  if ($(this).attr('data-name')) {
    for(let k = 0; k < 1; k++){
      let ids = [];
      let bool;
      try{
          let opop = JSON.parse($(this).attr('data-name'));
          let rr
          for (let i = 0; i < $('#formModalListL'+`${element_id}_${m_col}`).find('.ioL').length; i++) {
            rr = $('#masterListTablei' + element_id+'_'+m_col).find('tbody').find('tr').eq(i).find('td').eq(-1).text();
            rr = rr.trim()
            if (opop[rr] != undefined) {
                ids = [...ids, rr];
            }
          }
          bool = false;
          for (i in ids) {
            if(Number.isInteger(parseInt(ids[i]))) {
                ids[i] = parseInt(ids[i])
            }
          }
          let r, coun = 0;
          for (i in ids) {
            if(Number.isInteger(parseInt(ids[i]))) {
              for(let j = 0; j <= $('#masterListTablei' + element_id+'_'+m_col).find('.ioL').length; j++) {
                r = $('#masterListTablei' + element_id+'_'+m_col).find('tr').eq(j).find('td').eq(-1).text();
                r = r.trim()
                if (r == ids[i]) {
                  coun = coun + 1;
                }
              }
            }
          }
          if (coun == ids.length) {
            bool = true;
          }
        } catch(err) {
          bool = false
        }
        if (bool) {
          lenn = tableTextIndex[element_id+`_${m_col}`].length;
          tableTextIndex[element_id+`_${m_col}`].splice(0,lenn);
          for(let i = 0; i <= $('#masterListTablei' + element_id+'_'+m_col).find('.ioL').length; i++) {
            tableText =  $('#masterListTablei' + element_id+'_'+m_col).find('tr').eq(i).find('td').eq(-1).text();
            for (j in ids)
              if (ids[j] == tableText) {
              tableTextIndex[element_id+`_${m_col}`].push(i);
              }
          }
          $('#showDetailList'+element_id).find('#listDetailTable' + element_id + '_wrappper').remove();
          $('#showDetailList'+element_id).find('.card-body').empty()
          $('#showDetailList'+element_id).find('.card-body').append(
            `
            <table id="listDetailTable${element_id}" style="width:100%" class="row-border display compact">
              <thead style="width:100%">
              </thead>

              <tbody>

              </tbody>

            </table>
            `
          )
          $('#listDetailTable' + element_id).find('thead').empty();
          $('#listDetailTable' + element_id).find('tbody').empty();
          var htmlH = '<tr>'
          for (let j = 1; j < len[element_id+`_${m_col}`]; j++) {
          let d = $('#masterListTablei' + element_id+'_'+m_col).find('thead').find('tr').eq(0).find('th').eq(j).text();
            htmlH = htmlH + `<th>${d}</th>`
          }
          htmlH = htmlH + `</tr>`
          $('#listDetailTable' + element_id).find('thead').append(htmlH);
          for(let i = 0; i < (tableTextIndex[element_id+`_${m_col}`].length); i++) {
          if ($('#example1'+element_id+'_wrapper').find('table').find('tbody').find('tr').eq(i).find('td').eq(index).text() != "View Detail") {
          $('#listDetailTable' + element_id).find('tbody').append(`<tr></tr>`)
          let sent = $('#masterListTablei' + element_id+'_'+m_col).find('tr').eq(tableTextIndex[element_id+`_${m_col}`][i]).find('td').eq((1)).text();
          for (let j = 1; j < len[element_id+`_${m_col}`]; j++) {
              try {
              if ($('#masterListTablei' + element_id+'_'+m_col).find('tr').eq(0).find('th').eq(j).text().trim() == 'Default Value') {
                  var c =JSON.parse($(this).attr('data-name'));
                  $('#listDetailTable' + element_id).find('tbody').find('tr').eq(i).append(`<td class = "dt-center allColumnClass all view_details_wrap">${c[ $('#masterListTablei' + element_id  + "_" + m_col).find('tr').eq(tableTextIndex[element_id+`_${m_col}`][i]).find('td').eq(-1).text().trim()]}</td>`)
              } else {
                  var c = $('#masterListTablei' + element_id+'_'+m_col).find('tr').eq(tableTextIndex[element_id+`_${m_col}`][i]).find('td').eq(j).text();
                  $('#listDetailTable' + element_id).find('tbody').find('tr').eq(i).append(`<td class = "dt-center allColumnClass all view_details_wrap">${c}</td>`)
              }
              }
              catch (err) {

              }
          }
          }}
          $('#showDetailList'+element_id).modal('show');
          if (Object.keys(columnAlignment).length > 0) {
            var globalHeader = 'center';
            var globalContent = 'center';
            for (let j = 1; j < len[element_id+`_${m_col}`]; j++) {
              let k = $('#masterListTablei' + element_id+'_'+m_col).find('thead').find('tr').eq(0).find('th').eq(j).text();
              var index = j;
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
          multiSelectDatatableInitializer(element_id, columnAlignmentDef);
      }
    }
  }
}
function buttonGroupingCall(element){
  $(element).click()
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
function processDesignDiv(obj){
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

function quickFiltersDatableTrigger(elementTabID,obj){
  if ($(obj).val() != null){
    if($(obj).attr('multiple') == undefined){
      $(obj).attr('data-val',$(obj).val())
    }
  }
  $(`#example1${elementTabID}`).DataTable().draw()
}
function onChangeBoolQuickFilters(obj,id){
if (id == 'no_bool'){
  $(obj).parent().attr('data-val','false')
}else{
  $(obj).parent().attr('data-val','true')
}
$(`#example1${$(obj).attr('data-id')}`).DataTable().draw()
}
function resetAllQuickFilters(obj){
var element_id = $(obj).attr('data-id')
var mainDiv = $(`#quickFiltersDiv${element_id}`)
var divs = mainDiv.children()
for (let i = 0; i < divs.length; i++){
  if ($(divs).eq(i).attr('data-div') == 'select_field'){
      $(divs).eq(i).find('select').attr('data-val','')
      $(divs).eq(i).find('select').val('').trigger('change')
  }else if ($(divs).eq(i).attr('data-div') == 'multi_select'){
    $(divs).eq(i).find('select').val('').trigger('change')
  }
  else if ($(divs).eq(i).attr('data-div') == 'DateField'){
    $(divs).eq(i).find('.dtrangepicker').attr('data-val','')
    $(divs).eq(i).find('.dtrangepicker').val('')
  }
  else if ($(divs).eq(i).attr('data-div') == 'DateTimeRangeField'){
    $(divs).eq(i).find('.dttrangepicker').attr('data-val','')
    $(divs).eq(i).find('.dttrangepicker').val('')
  }
  else if ($(divs).eq(i).attr('data-div') == 'TimeField'){
    if ($(divs).eq(i).attr('data-sec') == 'true'){
      $(divs).eq(i).find('.ttrangepicker').attr('data-val','')
      $(divs).eq(i).find('.ttrangepicker').val('')
    }else{
      $(divs).eq(i).find('.ttrangepicker_sec').attr('data-val','')
      $(divs).eq(i).find('.ttrangepicker_sec').val('')
    }
  }
  else if ($(divs).eq(i).attr('data-div') == 'DateRangeField'){
    $(divs).eq(i).find('.dtrangepicker').attr('data-val','')
    $(divs).eq(i).find('.dtrangepicker').val('')
  }
  else if ($(divs).eq(i).attr('data-div') == 'DateTimeField'){
    if ($(divs).eq(i).attr('data-sec') == 'true'){
      $(divs).eq(i).find('.dttrangepicker').attr('data-val','')
      $(divs).eq(i).find('.dttrangepicker').val('')
    }else{
      $(divs).eq(i).find('.dttrangepicker_sec').attr('data-val','')
      $(divs).eq(i).find('.dttrangepicker_sec').val('')
    }
  }
  else if ($(divs).eq(i).attr('data-div') == 'TimeRangeField'){
    $(divs).eq(i).find('.ttrangepicker').attr('data-val','')
    $(divs).eq(i).find('.ttrangepicker').val('')
  }

  else if ($(divs).eq(i).attr('data-div') == 'range_field'){
    $(divs).eq(i).find('.js-range-slider').attr('data-val','')
    $(divs).eq(i).find('.js-range-slider').data('ionRangeSlider').reset()
  }else if ($(divs).eq(i).attr('data-div') == 'booleanField'){
    $(divs).eq(i).find('.radioGroup').attr('data-val','')
    $(divs).eq(i).find('input').prop('checked',false)
  }
}
$(`#example1${$(obj).attr('data-id')}`).DataTable().draw()
}
function ajaxQuickFilters(field_id,field,element_id){
const itemCode = windowLocation.split('/')[4]
if (field_id == 'range_field'){
  $.ajax({
    url: `/users/${urlPath}/${itemCode}/`,
    data: {
      columnName:`${field.find('.js-range-slider').attr('data-column')}`,
      tableName:`${field.attr('data-table')}`,
      operation: 'quick_filers_columns',
    },
    type: 'POST',
    dataType: 'json',
    success: function (data) {
      var maxNo = Math.max(...data.data)
      var minNo = Math.min(...data.data)
      field.find('.js-range-slider').ionRangeSlider({
        min: minNo,
        max: maxNo,
        prettify_enabled: true,
        prettify_separator: ",",
        onFinish: function (data) {
          field.find('.js-range-slider').attr('data-val',field.find('.js-range-slider').val())
          $(`#example1${element_id}`).DataTable().draw()
      }
      })
    },
    error: function (data) {
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    },
  })
}else if (field_id=='select_field'){
  $.ajax({
    url: `/users/${urlPath}/${itemCode}/`,
    data: {
      columnName:`${field.find('select').attr('data-column')}`,
      tableName:`${field.attr('data-table')}`,
      operation: 'quick_filers_columns',
    },
    type: 'POST',
    dataType: 'json',
    success: function (data) {
      field.find('select').empty()
      field.find('select').append(`<option value=''disabled selected >Select column</option>`)
      var newData = [...new Set(data.data)]
      for (let j in newData){
        field.find('select').append(`<option value='${newData[j]}'>${newData[j]}</option>`)
      }
    },
    error: function (data) {
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    },
  })
}else if (field_id=='multi_select'){
  $.ajax({
    url: `/users/${urlPath}/${itemCode}/`,
    data: {
      columnName:`${field.find('select').attr('data-column')}`,
      tableName:`${field.attr('data-table')}`,
      operation: 'quick_filers_columns',
    },
    type: 'POST',
    dataType: 'json',
    success: function (data) {
      field.find('select').empty()
      var newData = [...new Set(data.data)]
      for (let j in newData){
        field.find('select').append(`<option value='${newData[j]}'>${newData[j]}</option>`)
      }
    },
    error: function (data) {
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    },
  })
}

}
for (let i in element_table_IDList){
var quickFiltersDiv = $(`#quickFiltersDiv${element_table_IDList[i]}`)
if (quickFiltersDiv.length>0){
  const itemCode = windowLocation.split('/')[4]
  var quickFiltersDivChildren = quickFiltersDiv.children()
  for (let k = 0; k < quickFiltersDivChildren.length; k++){
    if (quickFiltersDivChildren.eq(k).attr('data-div') == 'range_field'){
      ajaxQuickFilters('range_field',quickFiltersDivChildren.eq(k),element_table_IDList[i])
    }
    else if (quickFiltersDivChildren.eq(k).attr('data-div') == 'DateField'){
      quickFiltersDivChildren.eq(k).find('.dtrangepicker').on('apply.daterangepicker', function(ev, picker) {
        $(this).val(picker.startDate.format('YYYY-MM-DD') + ' - ' + picker.endDate.format('YYYY-MM-DD'));
        $(this).attr('data-val',$(this).val())
        $(`#example1${element_table_IDList[i]}`).DataTable().draw()
         });
         quickFiltersDivChildren.eq(k).find('.dtrangepicker').on('cancel.daterangepicker', function(ev, picker) {
          $(this).val('');
          $(this).attr('data-val',$(this).val())
          $(`#example1${element_table_IDList[i]}`).DataTable().draw()
          });

    }
    else if (quickFiltersDivChildren.eq(k).attr('data-div') == 'DateTimeRangeField'){
      quickFiltersDivChildren.eq(k).find('.dttrangepicker').on('apply.daterangepicker', function(ev, picker) {
        $(this).val(picker.startDate.format('YYYY-MM-DD HH:mm:ss') + ' - ' + picker.endDate.format('YYYY-MM-DD HH:mm:ss'));
        $(this).attr('data-val',$(this).val())
        $(`#example1${element_table_IDList[i]}`).DataTable().draw()
         });
         quickFiltersDivChildren.eq(k).find('.dttrangepicker').on('cancel.daterangepicker', function(ev, picker) {
          $(this).val('');
          $(this).attr('data-val',$(this).val())
          $(`#example1${element_table_IDList[i]}`).DataTable().draw()
          });

    }
    else if (quickFiltersDivChildren.eq(k).attr('data-div') == 'TimeField'){
      if (quickFiltersDivChildren.eq(k).attr('data-sec') == 'true'){
        quickFiltersDivChildren.eq(k).find('.ttrangepicker').on('apply.daterangepicker', function(ev, picker) {
          $(this).val(picker.startDate.format('HH:mm:ss') + ' - ' + picker.endDate.format('HH:mm:ss'));
          $(this).attr('data-val',$(this).val())
          $(`#example1${element_table_IDList[i]}`).DataTable().draw()
           });
           quickFiltersDivChildren.eq(k).find('.ttrangepicker').on('cancel.daterangepicker', function(ev, picker) {
            $(this).val('');
            $(this).attr('data-val',$(this).val())
            $(`#example1${element_table_IDList[i]}`).DataTable().draw()
            });
      }else{
        quickFiltersDivChildren.eq(k).find('.ttrangepicker_sec').on('apply.daterangepicker', function(ev, picker) {
          $(this).val(picker.startDate.format('HH:mm') + ' - ' + picker.endDate.format('HH:mm'));
          $(this).attr('data-val',$(this).val())
          $(`#example1${element_table_IDList[i]}`).DataTable().draw()
           });
           quickFiltersDivChildren.eq(k).find('.ttrangepicker_sec').on('cancel.daterangepicker', function(ev, picker) {
            $(this).val('');
            $(this).attr('data-val',$(this).val())
            $(`#example1${element_table_IDList[i]}`).DataTable().draw()
            });
      }

    }
    else if (quickFiltersDivChildren.eq(k).attr('data-div') == 'DateRangeField'){
      quickFiltersDivChildren.eq(k).find('.dtrangepicker').on('apply.daterangepicker', function(ev, picker) {
        $(this).val(picker.startDate.format('YYYY-MM-DD') + ' - ' + picker.endDate.format('YYYY-MM-DD'));
        $(this).attr('data-val',$(this).val())
        $(`#example1${element_table_IDList[i]}`).DataTable().draw()
         });
         quickFiltersDivChildren.eq(k).find('.dtrangepicker').on('cancel.daterangepicker', function(ev, picker) {
          $(this).val('');
          $(this).attr('data-val',$(this).val())
          $(`#example1${element_table_IDList[i]}`).DataTable().draw()
          });

    }
    else if (quickFiltersDivChildren.eq(k).attr('data-div') == 'DateTimeField'){
      if (quickFiltersDivChildren.eq(k).attr('data-sec') == 'true'){
        quickFiltersDivChildren.eq(k).find('.dttrangepicker').on('apply.daterangepicker', function(ev, picker) {
          $(this).val(picker.startDate.format('YYYY-MM-DD HH:mm:ss') + ' - ' + picker.endDate.format('YYYY-MM-DD HH:mm:ss'));
          $(this).attr('data-val',$(this).val())
          $(`#example1${element_table_IDList[i]}`).DataTable().draw()
           });
           quickFiltersDivChildren.eq(k).find('.dttrangepicker').on('cancel.daterangepicker', function(ev, picker) {
            $(this).val('');
            $(this).attr('data-val',$(this).val())
            $(`#example1${element_table_IDList[i]}`).DataTable().draw()
            });
      }else{
        quickFiltersDivChildren.eq(k).find('.dttrangepicker_sec').on('apply.daterangepicker', function(ev, picker) {
          $(this).val(picker.startDate.format('YYYY-MM-DD HH:mm') + ' - ' + picker.endDate.format('YYYY-MM-DD HH:mm'));
          $(this).attr('data-val',$(this).val())
          $(`#example1${element_table_IDList[i]}`).DataTable().draw()
           });
           quickFiltersDivChildren.eq(k).find('.dttrangepicker_sec').on('cancel.daterangepicker', function(ev, picker) {
            $(this).val('');
            $(this).attr('data-val',$(this).val())
            $(`#example1${element_table_IDList[i]}`).DataTable().draw()
            });


      }


    }
    else if (quickFiltersDivChildren.eq(k).attr('data-div') == 'TimeRangeField'){
      quickFiltersDivChildren.eq(k).find('.ttrangepicker').on('apply.daterangepicker', function(ev, picker) {
        $(this).val(picker.startDate.format('HH:mm:ss') + ' - ' + picker.endDate.format('HH:mm:ss'));
        $(this).attr('data-val',$(this).val())
        $(`#example1${element_table_IDList[i]}`).DataTable().draw()
         });
         quickFiltersDivChildren.eq(k).find('.ttrangepicker').on('cancel.daterangepicker', function(ev, picker) {
          $(this).val('');
          $(this).attr('data-val',$(this).val())
          $(`#example1${element_table_IDList[i]}`).DataTable().draw()
          });

    }
    else if (quickFiltersDivChildren.eq(k).attr('data-div') == 'select_field'){
      ajaxQuickFilters('select_field',quickFiltersDivChildren.eq(k),element_table_IDList[i])
    }else if (quickFiltersDivChildren.eq(k).attr('data-div') == 'multi_select'){
      ajaxQuickFilters('multi_select',quickFiltersDivChildren.eq(k),element_table_IDList[i])
    }
  }
}
}
function dropdownContentListView(obj){
  var row_id = $(obj).parent().parent().closest('tr').find('td').eq(1).text()
  var value = $(obj).text();
  var field_name= $(obj).parent().parent('td').closest('table').find('th').eq($(obj).parent().parent().index()).text();

  if(row_edited_dict[row_id]){
    row_edited_dict[row_id][field_name] = value
  }else{
    row_edited_dict[row_id] = {}
    row_edited_dict[row_id][field_name] = value
  }
  $(obj).parent().parent().find('.edit').text($(obj).text())
  $(obj).parent().removeClass('show')
}
function dropdownContentListView_multi_select(obj){
  values = {}
  for (let i in $(obj).val()){
    values[$(obj).val()[i]] = ``
  }
  $(obj).attr('data-val',JSON.stringify(values))
}


function embeddedComputeHandler(listViewElementID) {
  var embededComputationBtn = $(
    `#list_view_edit_modal_${listViewElementID}`
  ).find('.modal-body').find(`#calval_embededComputation_${listViewElementID}`)
  var compjs = $(
    `#list_view_edit_modal_${listViewElementID}`
  ).find('.modal-body').find('.compjs')
  if (embededComputationBtn.length > 0){
  var attrdata = $(embededComputationBtn).attr('data-list')
  const elementId = $(embededComputationBtn).attr('data-elementid')
  if (attrdata != '' ||attrdata != '{}'){
    let compModelName = ''
    let parsedAttrData = JSON.parse(attrdata)
    let allOkFlag = 1
    let allok = ''
    for (let y in parsedAttrData){
      compModelName = y
      for (let j in parsedAttrData[y]){
        if (parsedAttrData[y][j][2] == 'auto_trigger'){
        let tableName = j
        let valuesDic = {}
        let listOfInputs = []
        let datatypeList = []
        let compDatatype = ""
        listOfInputs.push(...parsedAttrData[y][j][0])
        let lastInput = listOfInputs.slice(-1)
        let okay = 'no'
        for (let g in listOfInputs){
            okay = 'no'
            $(`#id_${listOfInputs[g]}_${elementId}`).on('change dp.change',function(){
                okay = 'no'
                for (let r in listOfInputs){
                    allok = 'no'
                    if  ($(`#id_${listOfInputs[r]}_${elementId}`).val() == '' || $(`#id_${listOfInputs[r]}_${elementId}`).val() == null){
                        allok = 'no'
                    }else{
                        allok = 'yes'
                    }
                }
                if (allok == 'yes'){
                    okay = 'yes'
                }else{
                    okay = 'no'
                }
                if (okay == 'yes'){
                    for (let i in listOfInputs){
                      allOkFlag = 1
                    let compCol = $(`#id_${listOfInputs[i]}_${elementId}`)
                    .attr('id')
                    .replace('id_', '')
                    .replace('_' + elementId, '')

                    let compVal = $(`#id_${listOfInputs[i]}_${elementId}`).val()
                    if (compVal == '' || compVal == null){
                        allOkFlag = 0
                        break
                    }
                    compDatatype = $(`#id_${listOfInputs[i]}_${elementId}`).attr('datatype')
                    if (compDatatype == 'IntegerField' || compDatatype == 'BigIntegerField'){
                      valuesDic[compCol] = parseInt(compVal)
                    }else if(compDatatype == 'FloatField'){
                      valuesDic[compCol] = parseFloat(compVal)
                    }else{
                      valuesDic[compCol] = compVal
                    }
                  }
                    datatypeList.push(compDatatype)
                    if (allOkFlag == 1){

                    $.ajax({
                      url: `/users/${urlPath}/dynamicVal/`,
                      data: {
                        element_id: elementId,
                        operation: `calculate_embeded_computation`,
                        values_dic: JSON.stringify(valuesDic),
                        datatype_list: JSON.stringify(datatypeList),
                        table_name: JSON.stringify(tableName),
                        compModelName:JSON.stringify(compModelName),
                      },
                      type: 'POST',
                      dataType: 'json',
                      success: function (context) {
                            if (parsedAttrData[y][j][3] == 'full_output'){
                              if (context.error_msg =='no'){
                              let data = context.data
                              if (data.element_error_message == 'Success') {
                                if (data.output_display_type === 'individual') {

                                }
                              } else {
                                Swal.fire({icon: 'error',text: data.element_error_message});
                              }
                          }else{
                              let error = context.e_list.slice(-1)
                              Swal.fire({icon: 'error',text: error});
                          }
                            }
                              else{
                            if (context.error_msg =='no'){
                                for (let k in parsedAttrData[y][j][1]){
                                  for (let l in context.data.content[0]){
                                    if (parsedAttrData[y][j][1][k] == l){
                                      let targetColumnDataType =  $(`#id_${parsedAttrData[y][j][1][k]}_${elementId}`).attr('datatype')
                                      if (targetColumnDataType == 'IntegerField' || targetColumnDataType == 'BigIntegerField'){
                                        $(`#id_${parsedAttrData[y][j][1][k]}_${elementId}`).val(parseInt(context.data.content[0][l])).trigger('change')
                                      }else if (targetColumnDataType == 'FloatField'){
                                        $(`#id_${parsedAttrData[y][j][1][k]}_${elementId}`).val(parseFloat(context.data.content[0][l])).trigger('change')
                                      }else{
                                        $(`#id_${parsedAttrData[y][j][1][k]}_${elementId}`).val(context.data.content[0][l]).trigger('change')
                                      }
                                    }
                                  }
                                }
                            }else{
                              let error = context.e_list.slice(-1)
                              Swal.fire({icon: 'error',text: error});

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
    }
  }
  }
  if(compjs.length > 0){
  for(let i=0;i<compjs.length;i++){
    let attrdata = $(compjs).attr('data-jsattr')
    const elementId = $(compjs).attr('id').split('_').pop()
    if (attrdata != '' ||attrdata != '[]'){
        let compModelName = ''
        let parsedAttrData = JSON.parse(attrdata)
        let allOkFlag = 1
        let allok = ''
        for (let y in parsedAttrData){
            if(parsedAttrData[y]["parentvalue"] == "Validation based message"){

                let tableName = parsedAttrData[y]["table"]
                let msg_txt = parsedAttrData[y]["msg_text"]
                let condition = parsedAttrData[y]["finaljsattr"][0][0]["condition"]["styleValidation"]
                let normal_txt_color = parsedAttrData[y]["finaljsattr"][0][0]["text_color"]
                let regex = /\{(\w+)\}/g;
                let result = [];
                let match = []
                let valuesDic = {}
                let datatypeList = []
                let compDatatype = ""
                let eq_model_name = parsedAttrData[y]["eqid"]
                let curr_col = parsedAttrData[y]["finaljsattr"][0][0]["table_column"]
                while (match = regex.exec(msg_txt))
                {
                    result.push(match[1]);
                }
                let set = new Set(result);
                result = Array.from(set);

                let listOfInputs = []
                listOfInputs.push(...parsedAttrData[y]["compute_fields"])
                let okay = 'no'
                for (let g in listOfInputs){
                    okay = 'no'
                    $(`#id_${listOfInputs[g]}_${elementId}`).on('change',function(){
                        okay = 'no'
                        for (let r in listOfInputs){
                            allok = 'no'
                            if  ($(`#id_${listOfInputs[r]}_${elementId}`).val() == '' || $(`#id_${listOfInputs[r]}_${elementId}`).val() == null){
                                allok = 'no'
                            }else{
                                allok = 'yes'
                            }
                        }
                        if (allok == 'yes'){
                            okay = 'yes'
                        }else{
                            okay = 'no'
                        }
                        if (okay == 'yes'){
                            for (let i in listOfInputs){
                            allOkFlag = 1
                            let compCol = $(`#id_${listOfInputs[i]}_${elementId}`)
                            .attr('id')
                            .replace('id_', '')
                            .replace('_' + elementId, '')

                            let compVal = $(`#id_${listOfInputs[i]}_${elementId}`).val()
                            if (compVal == '' || compVal == null){
                                allOkFlag = 0
                                break
                            }

                            compDatatype = $(`#id_${listOfInputs[i]}_${elementId}`).attr('datatype')

                            valuesDic[compCol] = compVal

                            datatypeList.push(compDatatype)
                        }
                            if (allOkFlag == 1){

                                $.ajax({
                                url: `/users/${urlPath}/dynamicVal/`,
                                data: {
                                    element_id: elementId,
                                    operation: 'computation_js_execute_model',
                                    column: curr_col,
                                    table_name: tableName,
                                    msg_col: JSON.stringify(result),
                                    msg_txt: msg_txt,
                                    condition: JSON.stringify(condition),
                                    eq_model_name: eq_model_name,
                                    valuesDic: JSON.stringify(valuesDic),
                                    datatypeList: JSON.stringify(datatypeList)
                                },
                                type: 'POST',
                                dataType: 'json',
                                success: function (data) {
                                    if(data.error_msg == "Success"){
                                        if(data.final_msg){
                                            $(`#id_${data.column}_${data.element_id}`).parent().find('small').remove()
                                            $(`#id_${data.column}_${data.element_id}`).parent().append(`<small style='color:${normal_txt_color}'>${data.final_msg}</small>`)
                                        }else{
                                            $(`#id_${data.column}_${data.element_id}`).parent().find('small').remove()
                                            $(`#id_${data.column}_${data.element_id}`).parent().append(`<small style='color:${normal_txt_color}'>No data found for selected inputs</small>`)
                                        }
                                    }else{
                                        $(`#id_${data.column}_${data.element_id}`).parent().find('small').remove()
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
    }
  }
  }
}

function approve_ind(){
  let approveButton = $(this)
  approveButton.prop('disabled', true);
  let tablename = approveButton.attr("data-tablename")
  let id = approveButton.attr("data-approval_id")
  let listViewTabElementId = approveButton.attr('data-element-id');
  let approval_comment = CKEDITOR.instances[`approvalCommentText${listViewTabElementId}`].getData()
  let approval_type = approveButton.attr("data-approval_type")

  if(approval_type == "approve"){
    $.ajax({
      url: `/users/${urlPath}/approval_table/`,
      data: {
        'tableName': tablename,
        "approval_id": id,
        'operation': 'approve_ind',
        'type_of_query':'update',
        'edited_data':JSON.stringify(edited_data),
        'approval_comment':approval_comment,
      },
      type: "POST",
      dataType: "json",
      success: function (data) {
        if (data.response == 'fail') {
          $(`#approvalCommentModal_${listViewTabElementId}`).modal('hide');
          Swal.fire({icon: 'info',text: `Error approving the records! ${data.error}`});
          $(`#approvalWallModal_${elementID}`).modal('hide');
        } else {
          $(`#approvalCommentModal_${listViewTabElementId}`).modal('hide');
          $(`#example1${listViewTabElementId}`).DataTable().draw();
          Swal.fire({icon: 'success',text: `Record approved successfully!`});
          $(`#approvalWallModal_${elementID}`).modal('hide');
        }
        approveButton.prop('disabled', false);
      },
      error: function () {
        approveButton.prop('disabled', false);
        Swal.fire({icon: 'error',text: 'Error! Failure in executing selected approval. Please try again.'});
      }
    });
  }else if(approval_type == "reject"){
    $.ajax({
      url: `/users/${urlPath}/approval_table/`,
      data: {
        'tableName': tablename,
        "approval_id": id,
        'operation': 'reject_ind',
        'type_of_query':"update",
        'approval_comment':approval_comment,
      },
      type: "POST",
      dataType: "json",
      success: function (data) {
        $(`#approvalCommentModal_${listViewTabElementId}`).modal('hide');
        $(`#example1${listViewTabElementId}`).DataTable().draw();
        $(`#approvalWallModal_${elementID}`).modal('hide');
        Swal.fire({icon: 'success',text: 'Record rejected successfully!'})
        approveButton.prop('disabled', false);
      },
      error: function () {
        Swal.fire({icon: 'error',text: 'Error! Failure in executing selected rejection. Please try again.'});
        approveButton.prop('disabled', false);
      }
    });
  }

}

function resend_ind(){
  let approveButton = $(this)
  approveButton.prop('disabled', true);
  let listViewTabElementId = $(this).attr('data-element-id');
  let approval_comment = CKEDITOR.instances[`approvalCommentText${listViewTabElementId}`].getData()
  let primaryKeyId = $(this).attr("data-approval_id")
  $.ajax({
    url: `/users/${urlPath}/approval_table/`,
    data: {
      "approval_id": primaryKeyId,
      'operation': 'resend_ind',
      "approval_comment":approval_comment,
    },
    type: "POST",
    dataType: "json",
    success: function (data) {
      $(`#approvalCommentModal_${listViewTabElementId}`).modal('hide');
      $(`#example1${listViewTabElementId}`).DataTable().draw();
      $(`#approvalWallModal_${elementID}`).modal('hide');
      Swal.fire({icon: 'success',text: 'Record send to previous approver for approval!'});
      approveButton.prop('disabled', false);
    },
    error: function () {
      Swal.fire({icon: 'error',text: 'Error! Failure in sending the transaction back to previous approver(s).'});
      approveButton.prop('disabled', false);
    }
  });

}

function dataCurrentFeed(opts, callback) {
  var matchProperty = 'username',
    data = mentions_user_list.filter(function(item) {
      return item[matchProperty].indexOf(opts.query.toLowerCase()) == 0;
    });

  data = data.sort(function(a, b) {
    return a[matchProperty].localeCompare(b[matchProperty], undefined, {
      sensitivity: 'accent'
    });
  });

  callback(data);
}

function delegateApproval(){
  let approveButton = $(this)
  approveButton.prop('disabled', true);
  let listViewTabElementId = $(this).attr('data-element-id');
  let primaryKeyId = $(this).attr("data-approval_id");
  let delegateTo = $(`#approvalCommentModal_${listViewTabElementId} .modal-body`).find('.delegateApprovalContainer').find('select').val();
  let delegateToLabel = $(`#approvalCommentModal_${listViewTabElementId} .modal-body`).find('.delegateApprovalContainer').find('select > option:selected').text();
  if (delegateTo) {
    let approval_comment = CKEDITOR.instances[`approvalCommentText${listViewTabElementId}`].getData();
    $.ajax({
      url: `/users/${urlPath}/approval_table/`,
      data: {
        "approval_id": primaryKeyId,
        "approval_comment":approval_comment,
        "delegate_to": delegateTo,
        'operation': 'delegate_approval_action',
      },
      type: "POST",
      dataType: "json",
      success: function (data) {
        $(`#approvalCommentModal_${listViewTabElementId}`).modal('hide');
        $(`#example1${listViewTabElementId}`).DataTable().draw();
        $(`#approvalWallModal_${elementID}`).modal('hide');

        Swal.fire({icon: 'success',text: `Approval decision for the record successfully delegated to ${delegateToLabel}!`});
        approveButton.prop('disabled', false);
      },
      error: function () {
        Swal.fire({icon: 'error',text: 'Error! Failure in delegating approval actions.'});
        approveButton.prop('disabled', false);
      }
    });
  } else {
    Swal.fire({icon: 'error',text: 'Error! Please select the user to delegate the approval actions to.'});
  }
}

function popoverEdit() {
  $(document).off('focusin.modal');
  $(this).closest(".process_navbar_popover").popover({
    container: 'body',
    delay: { "show": 10, "hide": 0 },
    //content: 'WASSUP',
    trigger: 'click',
    html:true,
    placement: 'left',
    template: '<div class="popover card" style="z-index:2000;"><div class="arrow"></div><h3 class="popover-header" style="background: #565a5e;color:white;text-align:center"></h3><div class="card-body"</div></div>',
    html: true,
    sanitize: false,
    content: function () {
      $(".popover").find(".card-body").empty()
      var string = `<div class="row" white-space="nowrap">`


      //  var i=0
      var list=["fas fa-compass","fas fa-atom","fas fa-sitemap","fas fa-highlighter","fas fa-globe","fas fa-paperclip","fas fa-project-diagram","fas fa-print","fas fa-table","fas fa-i-cursor","fas fa-indent","fas fa-list-alt","fas fa-list-ul","	fas fa-outdent","	far fa-building","fas fa-compass","fas fa-globe","fas fa-paperclip","fas fa-project-diagram","fas fa-bullseye","fas fa-calendar","far fa-clipboard","far fa-compass"]
      let config_ = JSON.parse($(this).attr("data-data"))
      let data_value = $(this).attr("data-value");
      let id_ = $(this).closest("td").attr("id");
      let index = $(this).attr("data-index")
      let column = $(this).attr("data-column")
      let id = $(this).attr("data-id")
      let url_string = window.location.pathname
      let f_occ = url_string.indexOf('/', url_string.indexOf('/') + 1)
      let s_occ = url_string.indexOf('/', url_string.indexOf('/') + f_occ +1)
      let t_occ = url_string.indexOf('/', url_string.indexOf('/') + s_occ +1)
      let app_code2 = url_string.substring(f_occ+1,s_occ)
      let current_dev_mode2 = url_string.substring(s_occ+1,t_occ)
      let modes = ["Build","Edit"]
      let url = ""
      if(current_dev_mode2 != "Build" && current_dev_mode2 != "Edit"){
        current_dev_mode2 = "User"
      }
      if(config_["data-type"] == "ForeignKey"){
        $.ajax({
          url: `/users/${app_code2}/${current_dev_mode2}/dynamicVal/`,

          data: {
            'operation': "ForeignKeyFilter1",
            'model_name': $(this).attr("data-table"),
            'column_name': $(this).attr("data-column"),
            'populate': 'yes'
          },
          type: "POST",
          dataType: "json",
          success: function (data) {
            $(".popover").find(".card-body").empty();
            string+=`
            <div class="col-12">
              <select class="selectize form-control value">`
            for (const [key, value] of Object.entries(data)) {
              string+=`<option value="${parseInt(value)}">${key}</option>`
            }
            string+=`</select>
            </div>
            <div class="col-12" style="margin-top:7px;">
              <i data-index="${index}" data-id="${id}" data-column="${column}" name="actions" value="" class="far fa-save ihover javaSC " style="font-size: 14px;margin-left:5px; float:right; cursor:pointer;" onclick="changeValue.call(this,'${id_}')"></i>
              <i name="actions" value="" class="fas fa-remove ihover javaSC " style="font-size: 14px;margin-left:5px; float:right; cursor:pointer;" onclick="closePopover.call(this,'${id_}')"></i>
            </div>
          </div>`
          $(".popover").find(".card-body").append(string)
          $(".popover").find(".card-body").find("select").each(function(){
            parent = $(this).parent()
            $(this).select2({dropdownParent:parent})
          })
        ;
          $(".popover").find(".card-body").find(".value").val(parseInt(data_value)).trigger("change")
          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Failure in fetching data options. Please try again.'});
          }
        })

      } else if(config_["data-type"] == "CharField") {
        let url_string = window.location.pathname
        let f_occ = url_string.indexOf('/', url_string.indexOf('/') + 1)
        let s_occ = url_string.indexOf('/', url_string.indexOf('/') + f_occ +1)
        let t_occ = url_string.indexOf('/', url_string.indexOf('/') + s_occ +1)
        let app_code2 = url_string.substring(f_occ+1,s_occ)
        let current_dev_mode2 = url_string.substring(s_occ+1,t_occ)
        let modes = ["Build","Edit"]
        let url = ""
        if(current_dev_mode2 != "Build" && current_dev_mode2 != "Edit"){
          current_dev_mode2 = "User"
        }
        $.ajax({
          url: `/users/${app_code2}/${app_code2}/dynamicVal/`,

          data: {
            'operation': "ChoiceField",
            'model_name': $(this).attr("data-table"),
            'column_name': $(this).attr("data-column"),
            'populate': 'yes'
          },
          type: "POST",
          dataType: "json",
          success: function (data) {
            if(data["choice"] == "yes"){
              $(".popover").find(".card-body").empty();
              string+=`
              <div class="col-12">
                <select class="selectize form-control value">`
              for (const i in (data.data)) {
                string+=`<option value="${data.data[i]}">${data.data[i]}</option>`
              }
              string+=`</select>
              </div>
              <div class="col-12" style="margin-top:7px;">
                <i name="actions" data-id="${id}" data-index="${index}" data-column="${column}" value="" class="far fa-save ihover javaSC " style="font-size: 14px;margin-left:5px; float:right; cursor:pointer;" onclick="changeValue.call(this,'${id_}')"></i>
                <i name="actions" value="" class="fas fa-remove ihover javaSC " style="font-size: 14px;margin-left:5px; float:right; cursor:pointer;" onclick="closePopover.call(this,'${id_}')"></i>
              </div>
            </div>`
            } else {
              string+=`
              <div class="col-12">
                <input class="form-control value" value="${data_value}">
              </div>
              <div class="col-12" style="margin-top:7px;">
                <i name="actions" data-id="${id}" data-index="${index}" data-column="${column}" value="" class="far fa-save ihover javaSC " style="font-size: 14px;margin-left:5px; float:right; cursor:pointer;" onclick="changeValue.call(this,'${id_}')"></i>
                <i name="actions" value="" class="fas fa-remove ihover javaSC " style="font-size: 14px;margin-left:5px; float:right; cursor:pointer;" onclick="closePopover.call(this,'${id_}')"></i>
              </div>
            </div>`
            }
            $(".popover").find(".card-body").empty()
            $(".popover").find(".card-body").append(string)
            $(".popover").find(".card-body").find("select").each(function(){
              parent = $(this).parent()
              $(this).select2({dropdownParent:parent})
            });
            $(".popover").find(".card-body").find(".value").val(data_value).trigger("change")
          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Failure in fetching data options. Please try again.'});
          }
        })

      } else if(config_["data-type"] == "FloatField") {
        string+=`
        <div class="col-12">
          <input type="number" step="0.000000001" class="form-control value" value="${data_value}">
        </div>
        <div class="col-12" style="margin-top:7px;">
          <i name="actions" data-id="${id}" data-index="${index}" data-column="${column}" value="" class="far fa-save ihover javaSC " style="font-size: 14px;margin-left:5px; float:right; cursor:pointer;" onclick="changeValue.call(this,'${id_}')"></i>
          <i name="actions" value="" class="fas fa-remove ihover javaSC " style="font-size: 14px;margin-left:5px; float:right; cursor:pointer;" onclick="closePopover.call(this,'${id_}')"></i>
        </div>
      </div>`
        $(".popover").find(".card-body").append(string)
      } else if(config_["data-type"] == "TextField" || config_["data-type"] == "TextArea") {
        string+=`
        <div class="col-12">
          <textarea class="form-control value" value="${data_value}"></textarea>
        </div>
        <div class="col-12" style="margin-top:7px;">
          <i name="actions" data-id="${id}" data-index="${index}" data-column="${column}" value="" class="far fa-save ihover javaSC " style="font-size: 14px;margin-left:5px; float:right; cursor:pointer;" onclick="changeValue.call(this,'${id_}')"></i>
          <i name="actions" value="" class="fas fa-remove ihover javaSC " style="font-size: 14px;margin-left:5px; float:right; cursor:pointer;" onclick="closePopover.call(this,'${id_}')"></i>
        </div>
      </div>`
        $(".popover").find(".card-body").append(string)
      } else if((config_["data-type"] == "IntegerField") || (config_["data-type"] == "BigIntegerField")) {
        string+=`
        <div class="col-12">
          <input type="number" step=1 class="form-control value" value="${data_value}">
        </div>
        <div class="col-12" style="margin-top:7px;">
          <i name="actions" data-id="${id}" data-index="${index}" data-column="${column}" value="" class="far fa-save ihover javaSC " style="font-size: 14px;margin-left:5px; float:right; cursor:pointer;" onclick="changeValue.call(this,'${id_}')"></i>
          <i name="actions" value="" class="fas fa-remove ihover javaSC " style="font-size: 14px;margin-left:5px; float:right; cursor:pointer;" onclick="closePopover.call(this,'${id_}')"></i>
        </div>
      </div>`
        $(".popover").find(".card-body").append(string)
      } else if(config_["data-type"] == "DateField") {
        string+=`
        <div class="col-12">
          <input type="date" class="form-control value" value="${data_value}">
        </div>
        <div class="col-12" style="margin-top:7px;">
          <i name="actions" data-id="${id}" data-index="${index}" data-column="${column}" value="" class="far fa-save ihover javaSC " style="font-size: 14px;margin-left:5px; float:right; cursor:pointer;" onclick="changeValue.call(this,'${id_}')"></i>
          <i name="actions" value="" class="fas fa-remove ihover javaSC " style="font-size: 14px;margin-left:5px; float:right; cursor:pointer;" onclick="closePopover.call(this,'${id_}')"></i>
        </div>
      </div>`
        $(".popover").find(".card-body").append(string)
      } else if(config_["data-type"] == "DateTimeField") {
        string+=`
        <div class="col-12">
          <input type="date" step="1" class="form-control value" value="${data_value}">
        </div>
        <div class="col-12" style="margin-top:7px;">
          <i name="actions" data-id="${id}" data-index="${index}" data-column="${column}" value="" class="far fa-save ihover javaSC " style="font-size: 14px;margin-left:5px; float:right; cursor:pointer;" onclick="changeValue.call(this,'${id_}')"></i>
          <i name="actions" value="" class="fas fa-remove ihover javaSC " style="font-size: 14px;margin-left:5px; float:right; cursor:pointer;" onclick="closePopover.call(this,'${id_}')"></i>
        </div>
      </div>`
        $(".popover").find(".card-body").append(string)
      }
      if(config_["data-type"] != "ForeignKey"){
        $(".popover").find(".card-body").val(data_value).trigger("change")
      }
      let html_mand = ""
      if(config_["data-null"] == 0 || config_["data-null"] == "0"){
        html_mand = "<span style='color:red;margin-left:5px;'>*</span>"
      }
      $(".popover").find(".popover-header").html(column + html_mand)
      return ""
    }
  }).on('click', function () {
    var self = this;
    if($(this).hasClass("show")){
      $(this).popover("hide");
    } else {
      $(this).popover("show");
    }
  })
}

function changeValue(id){
  let index = parseInt($(this).attr("data-index"))
  let column = $(this).attr("data-column")
  let id_ = $(this).attr("data-id")
  if(edited_data[id_][`${column}`]["data-null"] == "0" || edited_data[id_][`${column}`] == 0){
    if([undefined,null,""," "].includes($(this).closest(".row").find(".value").val())) {
      Swal.fire({icon: 'warning',text: 'The value cannot be empty as it is a mandatory field.'});
    } else {
      $("#"+id).find("span").text(`${$(this).closest(".row").find(".value").val()}`);
      $("#"+id).find(".process_navbar_popover").attr("data-value",$(this).closest(".row").find(".value").val())
      edited_data[id_][`${column}`]["value"] = $(this).closest(".row").find(".value").val()
      $(this).closest(".popover").popover("hide")
    }
  } else {
    $("#"+id).find("span").text(`${$(this).closest(".row").find(".value").val()}`);
    $("#"+id).find(".process_navbar_popover").attr("data-value",$(this).closest(".row").find(".value").val())
    edited_data[id_][`${column}`]["value"] = $(this).closest(".row").find(".value").val()
    $(this).closest(".popover").popover("hide")
  }
}
function closePopover(id) {
  $(this).closest(".popover").popover("hide")
}

function group_by_action_save_user_config(obj){
  var modal = $(`#group_by_switch_user_configuration_modal_${$(obj).attr('data-id')}`)
  var view_name = ''
  if ($(obj).attr('data-template') == 'Multi Dropdown View'){
    view_name = $(`#tableTab${$(obj).attr('data-id')}`).find("select").val()
  }
  if ($(obj).attr('data-template') == 'Approval Template'){
    $(modal).find('.modal-footer').find('button').html(`<i class="fa fa-circle-notch fa-spin"></i>`)
    var values ={}
    values['group_by_switch'] = $(modal).find(`#group_by_action_checkbox_user_config_${$(obj).attr('data-id')}`).prop('checked')
    if (!$(modal).find(`#group_by_action_checkbox_user_config_${$(obj).attr('data-id')}`).prop('checked')){
      var levels = $(modal).find('.group_by_action_levels').find('.levels')
      values['levels'] = []
      for (let i = 0; i < levels.length; i++){
        var singleLevel = $(modal).find('.group_by_action_levels').find('.levels').eq(i)
        var levelName = singleLevel.find('p').text()
        values['levels'].push($(singleLevel).find('select').val())
      }
      values['operations'] = []
      var operation = $(modal).find('.group_by_action_columns').find('.operation_div').find('.operation')
      for (let k = 0; k < operation.length; k++){
        var singleOperation = $(modal).find('.group_by_action_columns').find('.operation_div').find('.operation').eq(k)
        values['operations'].push($(singleOperation).find('select').val())
      }
      values['selected_columns'] = $(modal).find('.group_by_action_columns').find('select').eq(0).val()
      values['data-json-table'] = $(modal).find('.group_by_approval_temp_div').find('select').val()
    }
    var element_id = $(obj).attr('data-id').split("__tab__")[0]
  }else{
    $(modal).find('.modal-footer').find('button').html(`<i class="fa fa-circle-notch fa-spin"></i>`)
  var values ={}
  values['group_by_switch'] = $(modal).find(`#group_by_action_checkbox_user_config_${$(obj).attr('data-id')}`).prop('checked')
  if (!$(modal).find(`#group_by_action_checkbox_user_config_${$(obj).attr('data-id')}`).prop('checked')){
    var levels = $(modal).find('.group_by_action_levels').find('.levels')
    values['levels'] = []
    for (let i = 0; i < levels.length; i++){
      var singleLevel = $(modal).find('.group_by_action_levels').find('.levels').eq(i)
      var levelName = singleLevel.find('p').text()
      values['levels'].push($(singleLevel).find('select').val())
    }
    values['operations'] = []
    var operation = $(modal).find('.group_by_action_columns').find('.operation_div').find('.operation')
    for (let k = 0; k < operation.length; k++){
      var singleOperation = $(modal).find('.group_by_action_columns').find('.operation_div').find('.operation').eq(k)
      values['operations'].push($(singleOperation).find('select').val())
    }
    values['selected_columns'] = $(modal).find('.group_by_action_columns').find('select').eq(0).val()
  }
  var element_id = $(obj).attr('data-id').split("__tab__")[0]
  }
  $.ajax({
    url: `/users/${urlPath}/dynamicVal/`,
    data: {
      'operation': 'update_user_configuration_group_by',
      'values': JSON.stringify(values),
      'table_name':`${$(obj).attr('data-table-name')}`,
      'template':`${$(obj).attr('data-template')}`,
      'view_name':view_name,
      'element_id':element_id,
      'pr_code':windowLocation.split('/')[4],
    },
    type: 'POST',
    success: function (data) {
      $(modal).find('.modal-footer').find('button').html(`Save`);
      window.location.reload();
    },
    error: ()=>{
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    }
  });
}
function group_by_switch_user_configuration(obj){
  var Id_element = $(obj).attr('data-id')
  if ($(obj).attr('data-template') =='Multiple table'){
    Id_element = $(obj).attr('data-modal-id')
  }
  var modal = $(`#group_by_switch_user_configuration_modal_${Id_element}`)
  var selectedTable = $(obj).attr('data-table-name')
  $(modal).find('.group_by_action_levels').find('.levels').remove()
  $(modal).find('.group_by_action_columns').find('.operation_div').find('.operation').remove()
  $.ajax({
    url: `/users/${urlPath}/dynamicVal/`,
    data: {
      'operation': 'reload_user_configuration_group_by',
      'element_id':$(obj).attr('data-id'),
    },
    type: 'POST',
    success: function (data) {
      var else_trigger = false
      if (data.data != ''){
        var data_user_config = data.data
        if ($(obj).attr('data-table-name') in data_user_config){
          $(modal).find(`#group_by_action_checkbox_user_config_${Id_element}`).prop('checked',data_user_config[$(obj).attr('data-table-name')]['group_by_switch'])
          if (!data_user_config[$(obj).attr('data-table-name')]['group_by_switch']){
            $.ajax({
              url: `/users/${urlPath}/processGraphModule/`,
              data: {
                'operation': 'fecthing_verbose_name_group_by',
                'template':$(obj).attr('data-template'),
                'model_name': selectedTable,
              },
              type: "POST",
              dataType: "json",
              success: function (data) {
                var else_tag = false
                if ('data-json-table' in data_user_config[$(obj).attr('data-table-name')]){
                  var table_list = data.table_list
                  $(modal).find('.group_by_approval_temp_div').find('select').empty()
                  $(modal).find('.group_by_approval_temp_div').find('select').append(`<option value="">No Table</option>`)
                  for (let k in table_list){
                    $(modal).find('.group_by_approval_temp_div').find('select').append(`<option value="${table_list[k]}">${table_list[k]}</option>`)
                  }
                  $(modal).find('.group_by_approval_temp_div').find('select').val(data_user_config[$(obj).attr('data-table-name')]['data-json-table']).trigger('change')
                  var data = data.data
                  var columnOptions = ``
                  for (j in data) {
                    columnOptions +=  `<option data-type="${data[j]['data-type']}" value="${data[j]['originalName']}__-ApprovalTable">${data[j]['verboseName']} -ApprovalTable</option>`
                  }
                  var columnOptions1 = ''
                  for (j in data) {
                    columnOptions1 +=  `<option data-type="${data[j]['data-type']}" value="${data[j]['originalName']}__-ApprovalTable">${data[j]['verboseName']} -ApprovalTable</option>`
                  }
                  $.ajax({
                    url: `/users/${urlPath}/processGraphModule/`,

                    data: {
                      'operation': 'fecthing_verbose_name_group_by',
                      'template':$(obj).attr('data-template'),
                      'model_name': data_user_config[$(obj).attr('data-table-name')]['data-json-table'],
                    },
                    type: "POST",
                    dataType: "json",
                    success: function (data) {
                      var data = data.data
                      for (j in data) {
                        columnOptions +=  `<option data-type="${data[j]['data-type']}" value="${data[j]['originalName']}__-${data_user_config[$(obj).attr('data-table-name')]['data-json-table']}">${data[j]['verboseName']} -${data_user_config[$(obj).attr('data-table-name')]['data-json-table']}</option>`
                      }
                      for (j in data) {
                        columnOptions1 +=  `<option data-type="${data[j]['data-type']}" value="${data[j]['originalName']}__-${data_user_config[$(obj).attr('data-table-name')]['data-json-table']}">${data[j]['verboseName']} -${data_user_config[$(obj).attr('data-table-name')]['data-json-table']}</option>`
                      }
                      var lastCard = $(modal).find('.group_by_action_columns').find('select').eq(0)
                      $(lastCard).empty()
                      $(lastCard).append(columnOptions1)
                      $(lastCard).select2()
                      $(lastCard).val(data_user_config[$(obj).attr('data-table-name')]['selected_columns']).trigger('change')
                      for(let k in data_user_config[$(obj).attr('data-table-name')]['operations']){
                        $(modal).find('.group_by_action_columns').find('.operation_div').find('.operation').eq(k).find('select').val(data_user_config[$(obj).attr('data-table-name')]['operations'][k]).trigger('change')
                      }
                      var count = 0
                      for (let m in data_user_config[$(obj).attr('data-table-name')]['levels']){
                        var level2 = `<div class="levels">
                        <p style="font-weight: bold;padding-top:1rem;">Level ${count+1}:</p>
                        <div class="row">
                          <div class="col-11">
                            <select class="select2 form-control"></select>
                          </div>
                          <div class="col-1">
                            <button type="button" class="btn btn-tool" onclick="group_by_remove_content_user_config(this)" data-id="${Id_element}"><i class="fas fa-remove" style="color:var(--primary-color);"></i></button>
                          </div>
                        </div>
                      </div>
                        `
                        $(modal).find('.group_by_action_levels').append(level2)
                        var lastCard = $(modal).find('.group_by_action_levels').find('.levels').eq(-1)
                        $(lastCard).find('select').empty()
                        $(lastCard).find('select').append(`<option value="" disabled selected>Select Columns</option>`)
                        $(lastCard).find('select').append(columnOptions)
                        $(lastCard).find('select').each(function(){
                          $(this).select2()
                        })

                        $(lastCard).find('select').val(data_user_config[$(obj).attr('data-table-name')]['levels'][m]).trigger('change')
                        count ++
                    }
                    },
                    error: function () {
                      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                    }
                  })
                }else{
                  else_tag = true
                }
                  if(else_tag){
                    var data = data.data
                    var columnOptions = ``
                    for (j in data) {
                      columnOptions +=  `<option data-type="${data[j]['data-type']}" value="${data[j]['originalName']}">${data[j]['verboseName']}</option>`
                    }
                    var columnOptions1 = ''
                    for (j in data) {
                      columnOptions1 +=  `<option data-type="${data[j]['data-type']}" value="${data[j]['originalName']}">${data[j]['verboseName']}</option>`
                    }
                    var lastCard = $(modal).find('.group_by_action_columns').find('select').eq(0)
                    $(lastCard).empty()
                    $(lastCard).append(columnOptions1)
                    $(lastCard).select2()
                    $(lastCard).val(data_user_config[$(obj).attr('data-table-name')]['selected_columns']).trigger('change')
                    for(let k in data_user_config[$(obj).attr('data-table-name')]['operations']){
                      $(modal).find('.group_by_action_columns').find('.operation_div').find('.operation').eq(k).find('select').val(data_user_config[$(obj).attr('data-table-name')]['operations'][k]).trigger('change')
                    }
                    var count = 0
                    for (let m in data_user_config[$(obj).attr('data-table-name')]['levels']){
                      var level2 = `<div class="levels">
                      <p style="font-weight: bold;padding-top:1rem;">Level ${count+1}:</p>
                      <div class="row">
                        <div class="col-11">
                          <select class="select2 form-control"></select>
                        </div>
                        <div class="col-1">
                          <button type="button" class="btn btn-tool" onclick="group_by_remove_content_user_config(this)" data-id="${Id_element}"><i class="fas fa-remove" style="color:var(--primary-color);"></i></button>
                        </div>
                      </div>
                    </div>
                      `
                      $(modal).find('.group_by_action_levels').append(level2)
                      var lastCard = $(modal).find('.group_by_action_levels').find('.levels').eq(-1)
                      $(lastCard).find('select').empty()
                      $(lastCard).find('select').append(`<option value="" disabled selected>Select Columns</option>`)
                      $(lastCard).find('select').append(columnOptions)
                      $(lastCard).find('select').each(function(){
                        $(this).select2()
                      })

                      $(lastCard).find('select').val(data_user_config[$(obj).attr('data-table-name')]['levels'][m]).trigger('change')
                      count ++
                  }
                }
              },
              error: function () {
                Swal.fire({icon: 'error',text: 'Error! Please try again.'});
              }
            })
          }else{
            else_trigger = true
            $(modal).find('.add_level').prop('disabled',true);
            $(modal).find('.group_by_action_columns').find('select').eq(0).val([]).trigger('change');
            $(modal).find('.group_by_action_columns').find('select').eq(0).prop('disabled',true);
            $(modal).find('.group_by_approval_temp_div').find('select').prop('disabled',true);
          }
        }else if($(`#tableTab${$(obj).attr('data-id')}`).find("select").val() in data_user_config){
          $(modal).find(`#group_by_action_checkbox_user_config_${Id_element}`).prop('checked',data_user_config[$(`#tableTab${$(obj).attr('data-id')}`).find("select").val()]['group_by_switch'])
          if (!data_user_config[$(`#tableTab${$(obj).attr('data-id')}`).find("select").val()]['group_by_switch']){
            $.ajax({
              url: `/users/${urlPath}/processGraphModule/`,
              data: {
                'operation': 'fecthing_verbose_name_group_by',
                'template':$(obj).attr('data-template'),
                'model_name': selectedTable,
              },
              type: "POST",
              dataType: "json",
              success: function (data) {
                var data = data.data
                var columnOptions = ``
                for (j in data) {
                  columnOptions +=  `<option data-type="${data[j]['data-type']}" value="${data[j]['originalName']}">${data[j]['verboseName']}</option>`
                }
                var columnOptions1 = ''
                for (j in data) {
                  columnOptions1 +=  `<option data-type="${data[j]['data-type']}" value="${data[j]['originalName']}">${data[j]['verboseName']}</option>`
                }
                var lastCard = $(modal).find('.group_by_action_columns').find('select').eq(0)
                $(lastCard).empty()
                $(lastCard).append(columnOptions1)
                $(lastCard).select2()
                $(lastCard).val(data_user_config[$(`#tableTab${$(obj).attr('data-id')}`).find("select").val()]['selected_columns']).trigger('change')
                for(let k in data_user_config[$(`#tableTab${$(obj).attr('data-id')}`).find("select").val()]['operations']){
                  $(modal).find('.group_by_action_columns').find('.operation_div').find('.operation').eq(k).find('select').val(data_user_config[$(`#tableTab${$(obj).attr('data-id')}`).find("select").val()]['operations'][k]).trigger('change')
                }
                var count = 0
                for (let m in data_user_config[$(`#tableTab${$(obj).attr('data-id')}`).find("select").val()]['levels']){
                  var level2 = `<div class="levels">
                  <p style="font-weight: bold;padding-top:1rem;">Level ${count+1}:</p>
                  <div class="row">
                    <div class="col-11">
                      <select class="select2 form-control"></select>
                    </div>
                    <div class="col-1">
                      <button type="button" class="btn btn-tool" onclick="group_by_remove_content_user_config(this)" data-id="${Id_element}"><i class="fas fa-remove" style="color:var(--primary-color);"></i></button>
                    </div>
                  </div>
                </div>
                  `
                  $(modal).find('.group_by_action_levels').append(level2)
                  var lastCard = $(modal).find('.group_by_action_levels').find('.levels').eq(-1)
                  $(lastCard).find('select').empty()
                  $(lastCard).find('select').append(`<option value="" disabled selected>Select Columns</option>`)
                  $(lastCard).find('select').append(columnOptions)
                  $(lastCard).find('select').each(function(){
                    $(this).select2()
                  })

                  $(lastCard).find('select').val(data_user_config[$(`#tableTab${$(obj).attr('data-id')}`).find("select").val()]['levels'][m]).trigger('change')
                  count ++
                }
              },
              error: function () {
                Swal.fire({icon: 'error',text: 'Error! Please try again.'});
              }
            })
          }else{
            else_trigger = true
            $(modal).find('.add_level').prop('disabled',true);
            $(modal).find('.group_by_action_columns').find('select').eq(0).val([]).trigger('change');
            $(modal).find('.group_by_action_columns').find('select').eq(0).prop('disabled',true);
          }
        }else{
          else_trigger = true
        }
      }else{
        else_trigger = true
      }
      if (else_trigger){
        $.ajax({
          url: `/users/${urlPath}/processGraphModule/`,

          data: {
            'operation': 'fecthing_verbose_name_group_by',
            'template':$(obj).attr('data-template'),
            'model_name': selectedTable,
          },
          type: "POST",
          dataType: "json",
          success: function (data) {
            var columnOptions = ''
            var tableList = data.table_list
            var data = data.data
            for (j in data) {
              columnOptions +=  `<option data-type="${data[j]['data-type']}" value="${data[j]['originalName']}">${data[j]['verboseName']}</option>`
            }
            var lastCard = $(modal).find('.group_by_action_columns').find('select').eq(0)
            $(lastCard).empty()
            $(lastCard).append(columnOptions)
            $(lastCard).select2()
            if ($($(obj).attr('data-template') =='Approval Template')){
              $(modal).find('.group_by_approval_temp_div').find('select').empty()
              $(modal).find('.group_by_approval_temp_div').find('select').append(`<option value="">No table</option>`)
              for (let n in tableList){
                $(modal).find('.group_by_approval_temp_div').find('select').append(`<option value="${tableList[n]}">${tableList[n]}</option>`)
              }
            }
          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          }
        })
      }
    },
    error: ()=>{
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    }
  });
  $(modal).find('select').each(function(){
    $(this).select2()
  })

  $(modal).modal('show')
  $(modal).find('.group_by_approval_temp_div').find('select').on('select2:select', function (){
    var obj1 = this
    var elementID = $(obj1).attr('data-id')
    var modal = $(`#group_by_switch_user_configuration_modal_${elementID}`)
    if ($(this).val() != ''){
      $.ajax({
        url: `/users/${urlPath}/processGraphModule/`,

        data: {
          'operation': 'fecthing_verbose_name_group_by',
          'template':$(obj1).attr('data-template'),
          'model_name': 'ApprovalTable',
        },
        type: "POST",
        dataType: "json",
        success: function (data) {
          var columnOptions = ''
          var data = data.data
          for (j in data) {
            columnOptions +=  `<option data-type="${data[j]['data-type']}" value="${data[j]['originalName']}__-ApprovalTable">${data[j]['verboseName']} -ApprovalTable</option>`
          }

          $.ajax({
            url: `/users/${urlPath}/processGraphModule/`,

            data: {
              'operation': 'fecthing_verbose_name_group_by',
              'template':$(obj1).attr('data-template'),
              'model_name': $(obj1).val(),
            },
            type: "POST",
            dataType: "json",
            success: function (data) {
              var lastCard = $(modal).find('.group_by_action_columns').find('select').eq(0)
              var data = data.data
              for (j in data) {
                columnOptions +=  `<option data-type="${data[j]['data-type']}" value="${data[j]['originalName']}__-${$(obj1).val()}">${data[j]['verboseName']} -${$(obj1).val()}</option>`
              }
              $(lastCard).empty()
              $(lastCard).append(columnOptions)
              $(lastCard).select2()
              if($(obj1).attr('data-list') != undefined){
                var data_list = JSON.parse($(obj1).attr('data-list'))
                $(lastCard).val(data_list['selected_columns']).trigger('change')
                var count = $(modal).find('.group_by_action_levels').find('.levels').length
                for (let i in data_list['levels']){
                  var level2 = `<div class="levels">
                    <p style="font-weight: bold;padding-top:1rem;">Level ${parseInt(count)+1}:</p>
                    <div class="row">
                      <div class="col-11">
                        <select class="select2 form-control"></select>
                      </div>
                      <div class="col-1">
                        <button type="button" class="btn btn-tool" onclick="group_by_remove_content(this)"><i class="fas fa-remove" style="color:var(--primary-color);"></i></button>
                      </div>
                    </div>
                    </div>
                    `
                  $(modal).find('.group_by_action_levels').append(level2)
                  var lastCard1 = $(modal).find('.group_by_action_levels').find('.levels').eq(-1)
                  $(lastCard1).find('select').empty()
                  $(lastCard1).find('select').append(`<option value="" disabled selected>Select Columns</option>`)
                  $(lastCard1).find('select').append(columnOptions)
                  $(lastCard1).find('select').each(function(){
                    $(this).select2()
                  })

                  $(lastCard1).find('select').val(data_list['levels'][i]).trigger('change')
                  count ++
                }
                for(let k in data_list['operations']){
                  $('#group_by_action').find('.group_by_action_columns').find('.operation_div').find('.operation').eq(k).find('select').val(data_list['operations'][k]).trigger('change')
                }
              }
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
    }else{
      $.ajax({
        url: `/users/${urlPath}/processGraphModule/`,

        data: {
          'operation': 'fecthing_verbose_name_group_by',
          'template':$(obj1).attr('data-template'),
          'model_name': 'ApprovalTable',
        },
        type: "POST",
        dataType: "json",
        success: function (data) {
          var columnOptions = ''
          var data = data.data
          for (j in data) {
            columnOptions +=  `<option data-type="${data[j]['data-type']}" value="${data[j]['originalName']}">${data[j]['verboseName']}</option>`
          }
          var lastCard = $(modal).find('.group_by_action_columns').find('select').eq(0)
          $(lastCard).empty()
          $(lastCard).append(columnOptions)
          $(lastCard).select2()
        },
        error: function () {
          Swal.fire({icon: 'error',text: 'Error! Please try again.'});
        }
      })
    }
  })
}

function group_by_action_checkbox_onchange_user_config(obj){
  var modal = $(`#group_by_switch_user_configuration_modal_${$(obj).attr('data-id')}`)
  if ($(obj).prop('checked')){
    $(modal).find('.add_level').prop('disabled',true);
    $(modal).find('.group_by_action_levels').find('.levels').remove()
    $(modal).find('.group_by_action_columns').find('.operation_div').find('.operation').remove()
    $(modal).find('.group_by_action_columns').find('.operation_div').find('select').eq(0).val([]).trigger('change');
    $(modal).find('.group_by_action_columns').find('select').eq(0).prop('disabled',true);
    $(modal).find('.group_by_approval_temp_div').find('select').prop('disabled',true);
  }else{
    $(modal).find('.add_level').prop('disabled',false);
    $(modal).find('.group_by_action_columns').find('select').eq(0).val([]).trigger('change');
    $(modal).find('.group_by_action_columns').find('select').eq(0).prop('disabled',false);
    $(modal).find('.group_by_approval_temp_div').find('select').prop('disabled',false);
  }
}
function group_by_action_add_levels_user_config(obj){
  var modal = $(`#group_by_switch_user_configuration_modal_${$(obj).attr('data-id')}`)
  var count = $(modal).find('.group_by_action_levels').find('.levels').length
  var level2 = `<div class="levels">
    <p style="font-weight: bold;padding-top:1rem;">Level ${count+1}:</p>
    <div class="row">
      <div class="col-11">
        <select class="select2 form-control"></select>
      </div>
      <div class="col-1">
        <button type="button" class="btn btn-tool" onclick="group_by_remove_content_user_config(this)" data-id="${$(obj).attr('data-id')}"><i class="fas fa-remove" style="color:var(--primary-color);"></i></button>
      </div>
    </div>
  </div>
    `
  if (count >= 5){
    Swal.fire({text:"Max levels can be only 5",icon:"warning"})
  }else{
      var selectedTable = $(obj).attr('data-table-name')
      $.ajax({
        url: `/users/${urlPath}/processGraphModule/`,
        data: {
          'operation': 'fecthing_verbose_name_group_by',
          'template':$(obj).attr('data-template'),
          'model_name': selectedTable,
        },
        type: "POST",
        dataType: "json",
        success: function (data) {
          if ($(modal).find('.group_by_approval_temp_div').find('select').length > 0 && $(modal).find('.group_by_approval_temp_div').find('select').val()!= ''){
            $(modal).find('.group_by_action_levels').append(level2)
            var data = data.data
            for (j in data) {
              columnOptions +=  `<option data-type="${data[j]['data-type']}" value="${data[j]['originalName']}__-${selectedTable}">${data[j]['verboseName']} -${selectedTable}</option>`
            }
            var lastCard = $(modal).find('.group_by_action_levels').find('.levels').eq(-1)
            $.ajax({
              url: `/users/${urlPath}/processGraphModule/`,
              data: {
                'operation': 'fecthing_verbose_name_group_by',
                'template':$(obj).attr('data-template'),
                'model_name': $(modal).find('.group_by_approval_temp_div').find('select').val(),
              },
              type: "POST",
              dataType: "json",
              success: function (data) {
                var data = data.data
                for (j in data) {
                  columnOptions +=  `<option data-type="${data[j]['data-type']}" value="${data[j]['originalName']}__-${$(modal).find('.group_by_approval_temp_div').find('select').val()}">${data[j]['verboseName']} -${$(modal).find('.group_by_approval_temp_div').find('select').val()}</option>`
                }
                $(lastCard).find('select').empty()
                $(lastCard).find('select').append(`<option value="" disabled selected>Select Columns</option>`)
                $(lastCard).find('select').append(columnOptions)
                $(lastCard).find('select').each(function(){
                  $(this).select2()
                })

              },
              error: function () {
                Swal.fire({icon: 'error',text: 'Error! Please try again.'});
              }
            })
        }else{
          var columnOptions = ''
          $(modal).find('.group_by_action_levels').append(level2)
          var data = data.data
            for (j in data) {
              columnOptions +=  `<option data-type="${data[j]['data-type']}" value="${data[j]['originalName']}">${data[j]['verboseName']}</option>`
            }
          var lastCard = $(modal).find('.group_by_action_levels').find('.levels').eq(-1)
          $(lastCard).find('select').empty()
          $(lastCard).find('select').append(`<option value="" disabled selected>Select Columns</option>`)
          $(lastCard).find('select').append(columnOptions)
          $(lastCard).find('select').each(function(){
            $(this).select2()
          })

        }
        },
        error: function () {
          Swal.fire({icon: 'error',text: 'Error! Please try again.'});
        }
      })
    }
}
function group_by_action_reset_user_config(obj){
  var modal = $(`#group_by_switch_user_configuration_modal_${$(obj).attr('data-id')}`)
  $(modal).find('.group_by_action_levels').find('.levels').remove()
  $(modal).find('.group_by_action_columns').find('.operation_div').find('.operation').remove()
  $(modal).find('.group_by_action_columns').find('select').eq(0).val([]).trigger('change')
}
function group_by_action_columns_operation_user_config(obj){
  var modal = $(`#group_by_switch_user_configuration_modal_${$(obj).attr('data-id')}`)
  var dict_a = {}
  $(modal).find('.group_by_action_columns').find('.operation_div').find('.operation').each(function(){
    dict_a[$(this).find('p').attr('data-list')] = $(this).find('select').val()
  })
  $(modal).find('.group_by_action_columns').find('.operation_div').find('.operation').remove()
  var value = $(obj).val()
  var optionvalues = []
  if (value.length > 0){
    for (let k in value){
      var columnOptions = ``
      var seldatatype = $(modal).find('.group_by_action_columns').find('select').eq(0).find(`option[value='${value[k]}']`).attr('data-type')
      if (!((seldatatype === 'IntegerField') || (seldatatype === 'BigIntegerField') || (seldatatype === 'FloatField') || (seldatatype === 'AutoField'))){
        optionvalues = ['Count', 'Count Distinct', 'First', 'Last', 'Earliest','Latest','Value']
      }else if (((seldatatype === 'IntegerField') || (seldatatype === 'BigIntegerField') || (seldatatype === 'FloatField') || (seldatatype === 'AutoField'))){
        optionvalues = ['Sum', 'Count', 'Count Distinct', 'Average', 'Skewness', 'Kurtosis', 'Median', 'Variance', 'Standard Deviation', 'Minimum', 'Maximum', 'Percentage of Total','Value']
      }
      for (let i in optionvalues){
        columnOptions += `
        <option value="${optionvalues[i]}">${optionvalues[i]}</option>
        `
      }
      var operation = `<div class="operation">
        <p style="font-weight: bold;padding-top:1rem;" data-list="${value[k]}">Operation - ${$(modal).find('.group_by_action_columns').find('select').eq(0).find(`option[value='${value[k]}']`).text()}:</p>
        <select class="select2 form-control">
          <option value="----">----</option>
          ${columnOptions}
        </select>
      </div>
      `
      $(modal).find('.group_by_action_columns').find('.operation_div').append(operation)
    }
    $(modal).find('.group_by_action_columns').find('.operation_div').find('.operation').each(function(){
      if(dict_a.hasOwnProperty($(this).find('p').attr('data-list'))){
        $(this).find('select').val(dict_a[$(this).find('p').attr('data-list')]).trigger('change')
      }
    })
  }
  $(modal).find('.group_by_action_columns').find('.operation_div').find('.operation').find('select').each(function(){
    $(this).select2()
  })

}
function group_by_remove_content_user_config(obj){
  var modal = $(`#group_by_switch_user_configuration_modal_${$(obj).attr('data-id')}`)
  $(obj).closest('.levels').remove()
  var count = 0
  $(modal).find('.group_by_action_levels').find('.levels').each(function(){
    count++
    $(this).find('p').text(`Level ${count}`)
  })
}
function validateUploadedFileLV(file) {
  return true
}

function formFileUploadHandlerLV(fileInputRawId, existingFiles={}) {
  $(`#id_${fileInputRawId}`).on('click', ()=>{
    $(this).closest('.btn-outline-secondary').trigger('click');
  })
  var fileInputId = fileInputRawId + "_upload_input"
  var uploadedFileDropElement = document.getElementById(fileInputId).closest('.file-upload-wrapper');
  var uploadedFileContainerElement = $(`#${fileInputRawId}_upload_modal`).find('.uploaded-files-gallery');

  var uploadedFilesFormData = new FormData();
  uploadedFilesFormData.append("operation", "saveUploadedFiles");

  function addUploadedFilehandler(file, container) {
    uploadedFilesFormData.append(file.name, file);
    container.append(`
    <li class="list-group-item d-flex justify-content-between align-items-center">
      ${file.name}
      <span class="badge previewUploadedFile" style="margin-right:0;margin-left:auto;" data-file-name="${file.name}"><a href='${URL.createObjectURL(file)}' target="_blank"><i class="fas fa-eye fa-2x"></i></a></span>
      <span class="badge downloadUploadedFile" style="margin-right:0;" data-file-name="${file.name}"><a href='${URL.createObjectURL(file)}' target="_blank" download="${file.name}"><i class="fas fa-download fa-2x"></i></a></span>
      <span class="badge removeUploadedFile" data-file-name="${file.name}"><i class="fas fa-trash-alt fa-2x" style="color:red;"></i></span>
    </li>
    `);
    container.find('.list-group-item').eq(-1).find('.removeUploadedFile').on('click', function(){
      uploadedFilesFormData.delete($(this).attr('data-file-name'));
      $(this).parent().remove();
      if (container.find('.list-group-item').length == 0) {
        $(`#${fileInputId}`).val('');
      }
    });
  }

  uploadedFileDropElement.addEventListener('dragover', function(e){
    e.preventDefault();
  });
  uploadedFileDropElement.addEventListener('dragleave', function(e){
    e.preventDefault();
  });
  $(`#${fileInputId}`).on('change', function(e){
    if (e.target.files.length) {
      var uploadedFiles = e.target.files;
      for (upf of uploadedFiles) {
        if (validateUploadedFileLV(upf)) {
          addUploadedFilehandler(upf, uploadedFileContainerElement);
        } else {
          Swal.fire({icon: 'error',text: `Error! ${upf.name} does not conform to the field input rules.`});
        }
      }
    }
  });
  uploadedFileDropElement.addEventListener('drop', function(e){
    e.preventDefault();
    if (e.dataTransfer.files.length) {
      var uploadedFiles = e.dataTransfer.files;
      for (upf of uploadedFiles) {
        if (validateUploadedFileLV(upf)) {
          addUploadedFilehandler(upf, uploadedFileContainerElement);
        } else {
          Swal.fire({icon: 'error',text: `Error! ${upf.name} does not conform to the field input rules.`});
        }
      }
    }
  });
  $(`#${fileInputRawId}_upload_modal`).find('button.resetUploadedFiles').on('click', function(){
    for (const key of uploadedFilesFormData.keys()) {
      if (key !== "operation") {
        uploadedFilesFormData.delete(key);
      }
    }
    uploadedFileContainerElement.empty();
    $(`#${fileInputId}`).val('');
    $(`#id_${fileInputRawId}`).val('').trigger('change');
  });
  $(`#${fileInputRawId}_upload_modal`).find('button.closeUploadedFiles').on('click', function(){
    $(`#${fileInputRawId}_upload_modal`).modal('hide');
  });
  $(`#${fileInputRawId}_upload_modal`).find('button.saveUploadedFiles').on('click', function(){
    var uploadedFileString = "";
    uploadedFileContainerElement.find('li').each(function(){
      uploadedFileString += $(this).text().trim();
      uploadedFileString += ", ";
    });
    uploadedFileString = uploadedFileString.replace(/, $/, '');
    $.ajax({
      url: `/users/${urlPath}/dynamicVal/`,
      data: uploadedFilesFormData,
      type: 'POST',
      cache: false,
      contentType: false,
      processData: false,
      success: function (data) {
        if (data.msg == "file_invalid"){
          Swal.fire({text:"Incorrect file uploaded.",icon:"error"},$('.removeUploadedFile').trigger('click'))
          $(`#${fileInputRawId}_upload_modal`).modal('hide');
          uploadSaveButtonElement.prop('disabled', false);
          $(`#id_${fileInputRawId}`).val('').trigger('change');
        }else{
          $(`#${fileInputRawId}_upload_modal`).modal('hide');
          $(`#id_${fileInputRawId}`).val(uploadedFileString).trigger('change');
        }
      },
      error: ()=>{
        Swal.fire({icon: 'error',text: 'Error! Please try again.'});
      }
    });
  });
  if (Object.keys(existingFiles).length) {
    for (key of Object.keys(existingFiles)) {
      uploadedFileContainerElement.append(`
      <li class="list-group-item d-flex justify-content-between align-items-center">
        ${key}
        <span class="badge previewUploadedFile" style="margin-right:0; margin-left:auto;" data-file-name="${key}"><a href='/media/uploaded_files/${key}' target="_blank"><i class="fas fa-eye fa-2x"></i></a></span>
        <span class="badge downloadUploadedFile" style="margin-right:0;" data-file-name="${key}"><a href='/media/uploaded_files/${key}' target="_blank" download="${key}"><i class="fas fa-download fa-2x"></i></a></span>
        <span class="badge removeUploadedFile" data-file-name="${key}"><i class="fas fa-trash-alt fa-2x" style="color:red;"></i></span>
      </li>
      `);
    }
  }
}

function viewDetailOnModalTableFunc(elementID) {
  $('#' + elementID + '_tab_content')
    .find('#viewDetailOnModalTable')
    .DataTable({
      autoWidth: true,
      scrollY: '50vh',
      scrollCollapse: true,
      scrollX: '300',
      order: [],
      // "serverSide":true,
      orderCellsTop: true,
      // fixedHeader: true,
      responsive: true,
      colReorder: {
        fixedColumnsLeft: 1,
      },
      // stateSave: true,
      deferRender: true,
      paging: true,
      lengthMenu: [
        [1, 5, 50, -1],
        [1, 5, 50, 'All'],
      ],
      stripeClasses: false,
      pageLength: 50,
      dom: 'lfBrtip',
      sScrollX: '100%',
      buttons: [
        {
          extend: 'collection',
          text: 'Export',
          buttons: [
            {
              extend: 'copy',
              title: '',
              exportOptions: {},
            },
            {
              extend: 'excel',
              title: '',
                            exportOptions: {},
            },
            {
              extend: 'csv',
              title: '',
              exportOptions: {},
            },
            {
              extend: 'pdf',
              title: '',
              exportOptions: {},
            },
          ],
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
}
function viewDetailTableFuncBase(elementID) {
  $('#listDetailTable' + elementID).DataTable({
    autoWidth: true,
    scrollY: '50vh',
    scrollCollapse: true,
    scrollX: '300',
    // "serverSide":true,
    orderCellsTop: true,
    // fixedHeader: true,
    responsive: true,
    colReorder: {
      fixedColumnsLeft: 1,
    },
    // stateSave: true,
    deferRender: true,
    paging: true,
    lengthMenu: [
      [1, 5, 50, -1],
      [1, 5, 50, 'All'],
    ],
    stripeClasses: false,
    pageLength: 50,
    dom: 'lfBrtip',
    sScrollX: '100%',
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
}

function serverSideDataSearch(fieldName, blockElementId){
  let fieldIdentifier = `id_${fieldName}_${blockElementId}`;
  let tableIdentifier = `id_${fieldName}_${blockElementId}_serverside_table`;
  let fieldObject = $(`#${fieldIdentifier}`);
  let tableObject = $(`#${tableIdentifier}`);
  let pageLength = fieldObject.attr('data-serverside-page-length');
  pageLength = Number(pageLength);
  let dataType = fieldObject.attr('data-type');

  let fetchConfig = {};
  let isMultiSelect = false
  if (dataType == "ForeignKey") {
    let sourceModelName = fieldObject.attr('data-tablename');
    let sourceFieldName = fieldObject.attr('name');
    let conditionObject = {};
    if (fieldObject.attr('data-jsattr')) {
      var jsAttrArray = JSON.parse(fieldObject.attr('data-jsattr'));
      for(let i = 0; i < jsAttrArray.length; i++) {
        if (jsAttrArray[i]["parentvalue"] == "Foreign-key-relation") {
          if (jsAttrArray[i]['finaljsattr'][2][0].hasOwnProperty('condition')) {
            if (cases(jsAttrArray[i], blockElementId)) {
              conditionObject = jsAttrArray[i]['finaljsattr'][2][0]['condition'];
              break;;
            }
          }
        }
      }
    };
    fetchConfig['type'] = 'foreignkey';
    fetchConfig['field_config'] = {
      model_name: sourceModelName,
      field_name: sourceFieldName,
      condition: conditionObject,
    };
  } else if (fieldObject.attr('data-fieldType') == "MultiselectField") {
    isMultiSelect = true;
    let modelName = fieldObject.attr('name').replace(`__${fieldName}`, '');
    fetchConfig['type'] = 'multi-select';
    fetchConfig['field_config'] = {
      model_name: modelName,
      field_name: fieldName,
    };
  } else if (fieldObject.attr('data-jsattr')) {
    let conditionObject = {};
    let sourceModelName = fieldObject.attr('data-table');
    let sourceFieldName = fieldObject.attr('data-column');
    var jsAttrArray = JSON.parse(fieldObject.attr('data-jsattr'));
    for(let i = 0; i < jsAttrArray.length; i++) {
      if (jsAttrArray[i]["parentvalue"] == "Foreign-key-relation") {
        if (jsAttrArray[i]['finaljsattr'][2][0].hasOwnProperty('condition')) {
          if (cases(jsAttrArray[i], blockElementId)) {
            conditionObject = jsAttrArray[i]['finaljsattr'][2][0]['condition'];
            break;;
          }
        }
      }
    };
    fetchConfig['type'] = 'js-foreignkey';
    fetchConfig['field_config'] = {
      model_name: sourceModelName,
      field_name: sourceFieldName,
      condition: conditionObject,
    };
  }
  if($.fn.dataTable.isDataTable(`#${tableIdentifier}`)){
    tableObject.DataTable().clear().destroy()
  }
  var table = tableObject.DataTable({
    scrollY: "50vh",
    scrollCollapse: true,
    scrollX: "120%",
    sScrollX: "120%",
    serverSide: true,
    ordering: false,
    orderCellsTop: true,
    responsive: true,
    select: true,
    colReorder: {
      fixedColumnsLeft: 1,
    },
    stateSave: false,
    deferRender: true,
    paging: true,
    pageLength: pageLength,
    bLengthChange: false,
    dom: "lfrtip",
    buttons: [],
    ajax: {
      url: `${window.location.pathname}serverside_search/`,
      type: "POST",
      data: function (d, settings) {
        d.fetch_config = JSON.stringify(fetchConfig);
        d.searchValue = $(`#${tableIdentifier}_filter input`).val();
        return d;
      },
    },
    columns: [
      {
        data: null,
        defaultContent: '',
        className: 'select-checkbox',
        orderable: false
      },
      { data: fieldName, title: fieldName },
    ],
    columnDefs: [
      {
        targets: "_all",
        "width": "2%",
        className: "dt-left allColumnClass all",
      },
      {
        targets: 0,
        orderable: false,
        className: 'select-checkbox',
        render: function (data, type, full, meta) {
          let content = '';
          if (isMultiSelect) {
            content = `<input type="checkbox" class="big_data_select_checkbox" data-row-id="${full.id}" data-value="${full[fieldName]}">`;
          } else {
            content = `<input type="checkbox" class="big_data_select_checkbox">`;
          }
          content += `
          <style>
            .big_data_select_checkbox {
              position: relative;
              cursor: pointer;
              accent-color: var(--primary-color);
              transform: scale(1.05);
            }
            .big_data_select_checkbox::before {
                content: '';
                position: absolute;
                left: 1.2px;
                top: 1.2px;
                width: 11px;
                height: 11px;
                border: 0px solid #838383;
                border-radius: 0.8px;
                background-color: transparent;
            }
            .big_data_select_checkbox:hover::before {
                background-color: #f8f9fa;
            }
            .big_data_select_checkbox:checked::before {
                accent-color: var(--primary-color);
            }
            .big_data_select_checkbox:checked:hover::before {
                background-color: transparent;
            }
          </style>`;
          return content;
        }
      }
    ],
    select: {
      style: 'os',
      selector: 'td:first-child'
    }
  })
  .columns.adjust();
  let selectecValuesMS = {};
  let selectecValue = [];
  $(`#${tableIdentifier}`).on('change', '.big_data_select_checkbox', function() {
    if (isMultiSelect) {
      if ($(this).is(':checked')) {
        var value = $(this).attr('data-value');
        selectecValuesMS[$(this).attr('data-row-id')] = "";
        selectecValue.push(value);
      } else {
        delete selectecValuesMS[$(this).attr('data-row-id')];
        var index = selectecValue.indexOf(value);
        if (index > -1) {
          selectecValue.splice(index, 1);
        }
      }
    } else {
      if ($(this).is(':checked')) {
        var value = $(this).closest('td').next('td').text();
        if ($(`#${fieldIdentifier} > option[value='${value}']`).length > 0) {
          $(`#${fieldIdentifier}`).val(value).trigger('change');
        } else {
          $(`#${fieldIdentifier}`).append(`<option value="${value}" selected>${value}</option>`);
          $(`#${fieldIdentifier}`).select2().trigger('change');
        }
      }
      $(`#${fieldIdentifier}_serverside_modal`).modal('hide');
    }
  });
  if (isMultiSelect) {
    $(`#${fieldIdentifier}_serverside_save`).off('click').on('click', function(){
      $(`#${fieldIdentifier}`).val(JSON.stringify(selectecValuesMS)).trigger('change');
      let connectecSelectTag = $(`#${fieldIdentifier}`).attr('data-connectedselectfield');
      for (let i = 0; i < selectecValue.length; i++) {
        const element = selectecValue[i];
        $(`#${connectecSelectTag}`).append(`<option value="${element}" selected>${element}</option>`);
      }
      $(`#${connectecSelectTag}`).select2().trigger('change');
      $(`#${fieldIdentifier}_serverside_modal`).modal('hide');
    });
  }
}


function expandComments(){
  var comment_id = $(this).closest(".approval_comment_card").parent().attr("id").split("approval_comment_")[1]
  $(this).closest(".approval_card.approval_comment").find(".reply_comment_card").slideDown()
  if($(this).closest(`#approvalWallModalBody_${elementID}`).length > 0){
    if( ! resolved_ind_comments_list.includes(comment_id) && !$(this).closest(".approval_card.approval_comment").find(".comment_status_ind").hasClass("resolved_comment")){
      if(! freeze_comments_option){
        $(this).closest(".approval_card.approval_comment").find(".reply-area").slideDown()
      }
    }
  }
  else{
    $(this).closest(".approval_card.approval_comment").find(".reply-area").slideDown()
  }



  $(this).html(`<i class="fas fa-chevron-circle-up"></i>`)
  $(this).attr("class","rollup_comments")
  $(this).attr("data-toggle","tooltip")
  $(this).attr("title","Rollup comment thread")
  $(".rollup_comments").off('click').on("click",rollUpComments)
}

function rollUpComments(){
  $(this).closest(".approval_card.approval_comment").find(".reply_comment_card,.reply-area").slideUp()
  $(this).html(`<i class="fas fa-chevron-circle-down"></i>`)
  $(this).attr("class","expand_comments")
  $(this).attr("data-toggle","tooltip")
  $(this).attr("title","Expand comment thread")
  $(".expand_comments").off('click').on("click",expandComments)
}

function expand_rollup_comments(modalElement){
  var comment_threads_count = $(`#${modalElement}${elementID}`).find(`.approval_outer_${elementID}`).find(".approval_card.approval_comment").length
  if(comment_threads_count == 1){
    let comment_reply_cards = $(`#${modalElement}${elementID}`).find(`.approval_outer_${elementID}`).find(".approval_card.approval_comment").find(".reply_comment_card").length
    if(comment_reply_cards>=2){
      $(`#${modalElement}${elementID}`).find(`.approval_outer_${elementID}`).find(".approval_card.approval_comment").find(".reply_comment_card,.reply-area").slideUp()
      let span_html = `<span class="expand_comments" data-toggle="tooltip" title="Expand comment thread"><i class="fas fa-chevron-circle-down"></i></span>`
      $(`#${modalElement}${elementID}`).find(`.approval_outer_${elementID}`).find(".approval_card.approval_comment").find(".approval_comment_card:not(.reply_comment_card)").find(".approval_info").prepend(span_html)
    }
  }else{
    $(`#${modalElement}${elementID}`).find(`.approval_outer_${elementID}`).find(".approval_card.approval_comment").each(function(){
      let comment_reply_cards = $(this).find(".reply_comment_card").length
      if(comment_reply_cards>=1){
        $(this).find(".reply_comment_card,.reply-area").slideUp()
        let span_html = `<span class="expand_comments" data-toggle="tooltip" title="Expand comment thread"><i class="fas fa-chevron-circle-down"></i></span>`
        $(this).find(".approval_comment_card:not(.reply_comment_card)").find(".approval_info").prepend(span_html)
      }
    })
  }

  $(".expand_comments").off('click').on("click",expandComments)
  $(".rollup_comments").off('click').on("click",rollUpComments)
}


function getFormattedName(data) {
  if (data.includes('first_name') && data.includes('last_name') && data.includes('username') && data.includes('email')) {
    const fullName = [data.includes('first_name') ? '{first_name}' : '', data.includes('last_name') ? '{last_name}' : ''].join(' ');
    const username= [data.includes('username') ? '{username}' : '']
    const email = [data.includes('email') ? '{email}' : '']
    return `${fullName} <br> <span style="font-size: 80%">${username}, ${email}</span>`;
  }
  else if (data.includes('first_name') || data.includes('last_name')) {
    const fullName = [data.includes('first_name') ? '{first_name}' : '', data.includes('last_name') ? '{last_name}' : ''].join(' ');
    const email = data.includes('email') ? '<span style="font-size: 80%">{email}</span>' : '';
    const username = data.includes('username') ? '<span style="font-size: 80%">{username}</span>' : '';
    return `${fullName}<br>${username}${email}`;
  } else if (data.includes('username') && data.includes('email')) {
    const username = data.includes('username') ? '{username}' : '';
    const email = data.includes('email') ? '<span style="font-size: 80%">{email}</span>' : '';
    return `${username} <br> ${email}`;
  } else {
    return data.map(prop => `{${prop}}`).join(' ');
  }
}

function dataFeed(opts, callback) {
  var matchProperties = search_in_comments_cols,
  data = mentions_user_list.filter(function(item) {
    return matchProperties.some(function(property) {

      return item[property].toLowerCase().indexOf(opts.query.toLowerCase()) == 0;
    });
  });


  data = data.sort(function(a, b) {
    return a['username'].localeCompare(b['username'], undefined, {
      sensitivity: 'accent'
    });
  });

  callback(data);
}

function convertToTimestamp(datetimeString) {
  // Define the input and output formats
  const inputFormat1 = "YYYY-MM-DD HH:mm:ss"; // Input format for "YYYY-MM-DD HH:mm:ss"
  const inputFormat2 = "YYYY-MM-DDTHH:mm:ss.SSS"; // Input format for "YYYY-MM-DDTHH:mm:ss.SSS"
  const outputFormat = "DD MMMM YY";

  // for whole timestamp
  const tooltipOutputFormat = {
    day: "2-digit",
    month: "long",
    year: "numeric",
    hour: "numeric",
    minute: "numeric",
    hour12: true,
  };

  // Parse the datetime string into a Date object
  let datetimeObj;
  if (datetimeString.includes('T')) {
    datetimeObj = new Date(datetimeString);
  } else {
    datetimeObj = new Date(datetimeString.replace(/-/g, '/'));
  }

  // Extract the day and month information
  const day = datetimeObj.getDate();
  const month = new Intl.DateTimeFormat('en-US', { month: 'long' }).format(datetimeObj);
  const year = datetimeObj.getFullYear();

  // Format the extracted day and month into the desired timestamp format
  const timestamp = day.toString().padStart(2, '0') + ' ' + month.substring(0, 3) + ' ' +year.toString().substring(2, 4);

  const tooltipTimestamp = datetimeObj.toLocaleString('en-US', tooltipOutputFormat);

  return [timestamp,tooltipTimestamp];
}

function getInitials(username, user_type){
  initials = ""

  user_data_list = all_users_list

  if(user_data_list.length>0) {
    for (const user of user_data_list) {
      const user = user_data_list.find(user => user.username === username);
      if (user && user.first_name && user.first_name !== "") {
        initials = initials + user.first_name[0];
      }
      if (user && user.last_name && user.last_name !== "") {
        initials = initials + user.last_name[0];
      }
      if( initials != "" ){
        return initials.toUpperCase()
      }

    }
    return `${username[0].toUpperCase()}`;
  }
}

function openComments() {
  var elementID =  $(this).closest('table').attr('id').replace("example1", "");
  let rowData = $(this).closest('table').DataTable().row($(this).closest('tr')).data()
  let primaryKeyId = '';
  if ('id' in rowData){
    primaryKeyId = rowData['id'];
  }else if ('ID' in rowData){
    primaryKeyId = rowData['ID'];
  }else if ('iD' in rowData){
    primaryKeyId = rowData['iD'];
  }else if ('Id' in rowData){
    primaryKeyId = rowData['Id'];
  }
  $.ajax({
    url: `/users/${urlPath}/approval_table/`,
    data: {
      "approval_id": primaryKeyId,
      "element_id" :elementID,
      'operation': 'fetch_comments_data',
    },
    type: "POST",
    dataType: "json",
    success: function (data) {

      let url_string = window.location.pathname
      let f_occ = url_string.indexOf('/', url_string.indexOf('/') + 1)
      let s_occ = url_string.indexOf('/', url_string.indexOf('/') + f_occ +1)
      let t_occ = url_string.indexOf('/', url_string.indexOf('/') + s_occ +1)
      let app_code = url_string.substring(f_occ+1,s_occ)

      var current_level=0
      var audit_log_configs=[]

      mentions_user_list = JSON.parse(data.mentions_user_list)

      var approval_audit_log_data = data.data[0];

      all_users_list = data.all_users_list

      display_in_comments_cols = data.display_in_comments_cols
      search_in_comments_cols = data.search_in_comments_cols

      var smtpConfigKey = data.smtpConfigKey

      var itemTemplate = `<li data-id="{id}"><strong class="username"> ${getFormattedName(search_in_comments_cols)}</strong></li>`;
      var outputTemplate = `<a href="">@${display_in_comments_cols.map(prop => `{${prop}}`).join(' ')}</a><span>&nbsp;</span>`;

      var comment_editor, convo_reply_editor, mentions_reply_editor, new_comment_reply_editor;

      if(data.approval_level_config){
        approval_level_config = JSON.parse(data["approval_level_config"])
        current_level = approval_level_config.current_level
      }

      CKEDITOR.on('instanceReady', function(evt) {
        var editor = evt.editor;


        editor.on('focus', function(e) {
            element = e.editor.container.$
            $(element).find(".cke_top.cke_reset_all").css("display","block")
            $(element).find(".cke_contents.cke_reset").css("height","80px")
        });

        editor.on('blur', function(e) {
          element = e.editor.container.$
          $(element).find(".cke_top.cke_reset_all").css("display","none")
          $(element).find(".cke_contents.cke_reset").css("height","44px")
        })

      });

      comment_editor = CKEDITOR.replace(`approvalCommentText_${elementID}`, {
        height: 44,
        removeButtons: home_rtf[0],
        editorplaceholder: 'Add a comment...',
        plugins: 'mentions,undo,link,list,basicstyles,justify,richcombo,wysiwygarea,toolbar',
        extraPlugins: 'elementspath,editorplaceholder',
        toolbar: [
          { name: 'document', items: ['Undo'] },
          { name: 'paragraph', items: ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'] },
          { name: 'basicstyles', items: ['Bold', 'Italic', 'Underline', 'Strike', '-', 'RemoveFormat'] },
          { name: 'links', items: ['Mention', 'Link', 'Unlink', 'Anchor'] },
          { name: 'styles', items: ['Styles', 'Format', 'Font', 'FontSize'] },
          { name: 'colors', items: ['TextColor', 'BGColor'] },
          { name: 'elementspath', items: ['ElementPath'] }
        ],
        mentions: [
          {
            feed: dataFeed,
            itemTemplate: itemTemplate,
            outputTemplate: outputTemplate,
            minChars: 0
          }
        ],
        removeButtons: 'PasteFromWord'
      });
      CKEDITOR.config.bodyClass = 'custom_cke_class';
      CKEDITOR.config.removePlugins = 'exportpdf';
      CKEDITOR.config.extraPlugins = 'autocorrect,elementspath';

      CKEDITOR.instances[`approvalCommentText_${elementID}`].setData('');

      comment_editor = CKEDITOR.instances[`approvalCommentText_${elementID}`]
      comment_editor.on('change',function(){
        const typedText = comment_editor.getData();
        if(typedText.trim() === ''){
          $(`#convo_add_comment_${elementID}`).prop("disabled",true)
        }
        else{
          $(`#convo_add_comment_${elementID}`).prop("disabled",false)
        }
      })

      comment_editor.on('key',function(event){
        if (event.data.keyCode === CKEDITOR.CTRL + 13){
          $(`#convo_add_comment_${elementID}`).trigger("click")
        }
      })

      $(`#approvalCommentsModalBody_${elementID}`).find(`.approval_outer_${elementID}`).empty()

      if(approval_audit_log_data.approval_audit_log){
        audit_log_configs = JSON.parse(approval_audit_log_data.approval_audit_log)

        for(let i=0; i<audit_log_configs.length; i++){
          for (let [key, value] of Object.entries(audit_log_configs[i])) {

            for (let j=0; j<value.length; j++) {
              dictt = value[j]

              var [timestamp,tooltipTimestamp] = convertToTimestamp(dictt["time"]);
              var small_time = "at" + tooltipTimestamp.split("at")[1]
              var initials = getInitials(dictt["user"])

              const targetItem = all_users_list.find(item => item.username === dictt["user"]);
              let additionalString = '';

              if (targetItem) {
                const { username, id, ...dataWithoutUsername } = targetItem;
                const dataValues = Object.values(dataWithoutUsername).filter(value => value!="-" && value!="");
                additionalString = `(${dataValues.join(' ')})`;
                if (additionalString="()"){
                  additionalString = ""
                }
              }

              if(dictt["action"] == "Comment"){
                audit_html = `
                <div class="approval_card approval_comment">
                  <div id="approval_comment_${i}${j}">
                    <div class="approval_comment_card">
                      <div class="approval_info">
                        <h5 class="approval_title"><span>${initials}</span></h5>
                        <p class="approval_text">${dictt["user"]} ${additionalString} sent a comment</p>
                        <div>
                          <h6 class="approval_timestamp" data-toggle="tooltip" title="${tooltipTimestamp}">${timestamp}</h6>
                          <small style="color: #929292;">${small_time}</small>
                        </div>
                      </div>
                      <div class="approval_comment_text"><p>${dictt["value"].replaceAll("\\t", "&nbsp;").replaceAll("\\n", "<br>")}</p></div>
                    </div>`

                if (dictt.hasOwnProperty("replies")) {
                  replies = dictt["replies"]

                  for(let k=0; k<replies.length;k++){
                    var [reply_timestamp,reply_tooltipTimestamp] = convertToTimestamp(replies[k]["time"]);
                    var reply_initials = getInitials(replies[k]["user"])
                    audit_html = audit_html + `
                    <div class="reply_comment_card approval_comment_card">
                      <div class="approval_info">
                        <h5 class="approval_title"><span>${reply_initials}</span></h5>
                        <p class="approval_text">${replies[k]["user"]} ${additionalString} replied</p>
                        <div>
                          <h6 class="approval_timestamp" data-toggle="tooltip" title="${reply_tooltipTimestamp}">${reply_timestamp}</h6>
                          <small style="color: #929292;">${small_time}</small>
                        </div>
                      </div>
                      <div class="approval_comment_text"><p>${replies[k]["value"].replaceAll("\\t", "&nbsp;").replaceAll("\\n", "<br>")}</p></div>
                    </div>`
                  }
                }

                audit_html = audit_html + `</div><div class="reply-area mt-3">
                    <textarea id="convo_replycomment_${i}${j}" name="convo_replycomment_${i}${j}"></textarea>
                    <div style="margin: 15px 0 5px 0;text-align: right;display: flex;align-items: center;justify-content: flex-end;">
                      <button class="btn btn-primary reply_comments" style="font-size:0.9rem;" disabled data-toggle="tooltip" title="Click this button or press Ctrl+Enter" id="convo_replybutton_${i}${j}" onclick="ReplyToConvoComment('${i}','${j}','${key}','${approval_audit_log_data.id}', '${smtpConfigKey}', '${app_code}')">Reply <i class="fa-solid fa-comment-dots ml-2"></i></button>
                    </div>
                  </div>
                  <style>
                  .approval_wall_btn:hover{
                    background-color: var(--secondary-color) !important;
                    color:var(--font-hover-color);
                  }
                </style>
                </div>`

                $(`#approvalCommentsModalBody_${elementID}`).find(`.approval_outer_${element_id}`).prepend(audit_html)

                convo_reply_editor = CKEDITOR.replace(`convo_replycomment_${i}${j}`,
                {
                  height: 44,
                  removeButtons: home_rtf[0],
                  editorplaceholder: "Type your reply here..." ,
                  plugins: 'mentions,undo,link,list,basicstyles,justify,richcombo,wysiwygarea,toolbar',
                  extraPlugins: 'elementspath,editorplaceholder',
                  toolbar: [
                    { name: 'document', items: ['Undo'] },
                    { name: 'paragraph', items: ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'] },
                    { name: 'basicstyles', items: ['Bold', 'Italic', 'Underline', 'Strike', '-', 'RemoveFormat'] },
                    { name: 'links', items: ['Mention', 'Link', 'Unlink', 'Anchor'] },
                    { name: 'styles', items: ['Styles', 'Format', 'Font', 'FontSize'] },
                    { name: 'colors', items: ['TextColor', 'BGColor'] },
                    { name: 'elementspath', items: ['ElementPath'] }
                  ],
                  mentions: [
                    {
                      feed: dataFeed,
                      itemTemplate: itemTemplate,
                      outputTemplate: outputTemplate,
                      minChars: 0
                    }
                  ],
                  removeButtons: 'PasteFromWord'

                });
                CKEDITOR.config.removePlugins = 'exportpdf';
                CKEDITOR.config.extraPlugins = 'autocorrect,elementspath';

                convo_reply_editor = CKEDITOR.instances[`convo_replycomment_${i}${j}`]
                convo_reply_editor.on('change',function(){
                  let typedText = convo_reply_editor.getData();
                  if(typedText.trim() === ''){
                    $(`#convo_replybutton_${i}${j}`).prop("disabled",true)
                  }
                  else{
                    $(`#convo_replybutton_${i}${j}`).prop("disabled",false)
                  }
                })

                convo_reply_editor.on('key',function(event){
                  if (event.data.keyCode === CKEDITOR.CTRL + 13){
                    $(`#convo_replybutton_${i}${j}`).trigger("click")
                  }
                })

                for(var editorId in CKEDITOR.instances){
                  if(editorId.indexOf('convo_replycomment_') === 0){
                    CKEDITOR.instances[editorId].setData('')
                  }
                }

              }
              else if(dictt["action"] == "Mention"){
                audit_html = `
                <div class="approval_card approval_comment">
                  <div id="approval_comment_${i}${j}">
                    <div class="approval_comment_card">
                      <div class="approval_info">
                        <h5 class="approval_title"><span>${initials}</span></h5>
                        <p class="approval_text">${dictt["user"]} ${additionalString} mentioned</p>
                        <div>
                          <h6 class="approval_timestamp" data-toggle="tooltip" title="${tooltipTimestamp}">${timestamp}</h6>
                          <small style="color: #929292;">${small_time}</small>
                        </div>
                      </div>
                      <div class="approval_comment_text"><p>${dictt["value"].replaceAll("\\t", "&nbsp;").replaceAll("\\n", "<br>")}</p></div>
                    </div>`

                  if (dictt.hasOwnProperty("replies")) {
                    replies = dictt["replies"]
                    for(let k=0; k<replies.length;k++){
                      var [reply_timestamp,reply_tooltipTimestamp] = convertToTimestamp(replies[k]["time"]);
                      let small_time = "at" + reply_tooltipTimestamp.split("at")[1]
                      var reply_initials = getInitials(replies[k]["user"])
                      audit_html = audit_html + `
                      <div class="reply_comment_card approval_comment_card">
                        <div class="approval_info">
                          <h5 class="approval_title"><span>${reply_initials}</span></h5>
                          <p class="approval_text">${replies[k]["user"]} ${additionalString} replied</p>
                          <div>
                            <h6 class="approval_timestamp" data-toggle="tooltip" title="${reply_tooltipTimestamp}">${reply_timestamp}</h6>
                            <small style="color: #929292;">${small_time}</small>
                          </div>
                        </div>
                        <div class="approval_comment_text"><p>${replies[k]["value"].replaceAll("\\t", "&nbsp;").replaceAll("\\n", "<br>")}</p></div>
                      </div>`
                    }
                  }


                      audit_html = audit_html + `</div><div class="reply-area mt-3">

                      <textarea id="convo_replycomment_${i}${j}" name="convo_replycomment_${i}${j}"></textarea>
                      <div style="margin: 15px 0 5px 0;text-align: right;display: flex;align-items: center;justify-content: flex-end;">
                        <button class="btn btn-primary reply_comments" style="font-size:0.9rem;" disabled data-toggle="tooltip" title="Click this button or press Ctrl+Enter" id="convo_replybutton_${i}${j}" onclick="ReplyToConvoComment('${i}','${j}','${key}','${approval_audit_log_data.id}', '${smtpConfigKey}', '${app_code}')">Reply <i class="fa-solid fa-comment-dots ml-2"></i></button>
                      </div>
                    </div>
                    <style>
                    .approval_wall_btn:hover{
                      background-color: var(--secondary-color) !important;
                      color:var(--font-hover-color);
                    }
                  </style>
                  </div>
                `

                $(`#approvalCommentsModalBody_${elementID}`).find(`.approval_outer_${element_id}`).prepend(audit_html)

                mentions_reply_editor = CKEDITOR.replace(`convo_replycomment_${i}${j}`,
                {
                  height: 44,
                  removeButtons: home_rtf[0],
                  editorplaceholder: 'Add a comment...',
                  plugins: 'mentions,undo,link,list,basicstyles,justify,richcombo,wysiwygarea,toolbar',
                  extraPlugins: 'elementspath,editorplaceholder',
                  toolbar: [
                    { name: 'document', items: ['Undo'] },
                    { name: 'paragraph', items: ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'] },
                    { name: 'basicstyles', items: ['Bold', 'Italic', 'Underline', 'Strike', '-', 'RemoveFormat'] },
                    { name: 'links', items: ['Mention', 'Link', 'Unlink', 'Anchor'] },
                    { name: 'styles', items: ['Styles', 'Format', 'Font', 'FontSize'] },
                    { name: 'colors', items: ['TextColor', 'BGColor'] },
                    { name: 'elementspath', items: ['ElementPath'] }
                  ],
                  mentions: [
                    {
                      feed: dataFeed,
                      itemTemplate: itemTemplate,
                      outputTemplate: outputTemplate,
                      minChars: 0
                    }
                  ],
                  removeButtons: 'PasteFromWord'
                });

                CKEDITOR.config.removePlugins = 'exportpdf';
                CKEDITOR.config.extraPlugins = 'autocorrect,elementspath';

                mentions_reply_editor = CKEDITOR.instances[`convo_replycomment_${i}${j}`]
                mentions_reply_editor.on('change',function(){
                  let typedText = mentions_reply_editor.getData();
                  if(typedText.trim() === ''){
                    $(`#convo_replybutton_${i}${j}`).prop("disabled",true)
                  }
                  else{
                    $(`#convo_replybutton_${i}${j}`).prop("disabled",false)
                  }
                })

                mentions_reply_editor.on('key',function(event){
                  if (event.data.keyCode === CKEDITOR.CTRL + 13){
                    $(`#convo_replybutton_${i}${j}`).trigger("click")
                  }
                })

                for(var editorId in CKEDITOR.instances){
                  if(editorId.indexOf('convo_replycomment_') === 0){
                    CKEDITOR.instances[editorId].setData('')
                  }
                }
              }


            }
          }
        }
      }

      expand_rollup_comments('approvalCommentsModalBody_')

      $(".closeCommentsModal").on('click', function(){

        var modalElement = document.querySelector(".approvalCommentsModal");

        for(var instanceName in CKEDITOR.instances){
          if(CKEDITOR.instances.hasOwnProperty(instanceName)){
            var editorElement = modalElement.querySelector("#"+instanceName)

            if(editorElement){
              CKEDITOR.instances[instanceName].destroy()
            }
          }
        }

        $(`#approvalCommentsModal_${elementID}`).modal('hide')
      })


      $(`#convo_add_comment_${elementID}`).off('click').on('click', function(){
        approval_comment = CKEDITOR.instances[`approvalCommentText_${elementID}`].getData()
        if (approval_comment) {
          var usernamesArray = []
          // Regular expression to match mentions (assuming mentions are like @username)
          var mentionPattern = /@(\w+)/g;
          var matches = approval_comment.match(mentionPattern);

          if (matches) {
            // Create a Set ato store unique usernames
            var uniqueUsernames = new Set();

            // Extract usernames and add to the Set
            matches.forEach(function(match) {
              uniqueUsernames.add(match.substr(1)); // Remove the "@" symbol
            });

            // Convert Set to an array and display the mentioned usernames
            usernamesArray = Array.from(uniqueUsernames);
          }

          $.ajax({
            url: `/users/${urlPath}/approval_table/`,
            data: {
              "approval_id": approval_audit_log_data.id,
              "current_level":current_level,
              'operation': 'add_comment',
              'audit_log_configs':JSON.stringify(audit_log_configs),
              "approval_comment":approval_comment,
              "mentioned_usernames":JSON.stringify(usernamesArray),
              "smtpConfigKey": smtpConfigKey,
              "app_code": app_code,
            },
            type: "POST",
            dataType: "json",
            success: function (data) {
              var count = audit_log_configs.length
              all_audit_data = JSON.parse(data["all_audit_data"])
              audit_log_configs.push(all_audit_data[count])
              CKEDITOR.instances[`approvalCommentText_${elementID}`].setData('');
              temp_log = data

              var [timestamp,tooltipTimestamp] = convertToTimestamp(temp_log["time"]);
              var small_time = "at" + tooltipTimestamp.split("at")[1]
              var initials = getInitials(temp_log["user"])
              audit_html = `
                <div class="approval_card approval_comment">
                  <div id="approval_comment_${count}0">
                    <div class="approval_comment_card">
                      <div class="approval_info">
                        <h5 class="approval_title"><span>${initials}</span></h5>
                        <p class="approval_text">${temp_log["user"]} sent a comment</p>
                        <div>
                          <h6 class="approval_timestamp" data-toggle="tooltip" title="${tooltipTimestamp}">${timestamp}</h6>
                          <small style="color: #929292;">${small_time}</small>
                        </div>
                      </div>
                      <div class="approval_comment_text"><p>${temp_log["value"]}</p></div>
                    </div>
                  </div>
                  <div class="reply-area mt-3">
                    <textarea id="convo_replycomment_${count}0" name="convo_replycomment_${count}0"></textarea>
                    <div style="margin: 15px 0 5px 0;text-align: right;display: flex;align-items: center;justify-content: flex-end;">
                      <button class="btn btn-primary reply_comments" style="font-size:0.9rem;" disabled data-toggle="tooltip" title="Click this button or press Ctrl+Enter" id="convo_replybutton_${count}0" onclick="ReplyToConvoComment('${count}','0','Level ${current_level}','${approval_audit_log_data.id}', '${smtpConfigKey}', '${app_code}')">Reply <i class="fa-solid fa-comment-dots ml-2"></i></button>
                    </div>
                  </div>
                </div>
              `
              $(`#approvalCommentsModalBody_${elementID}`).find(`.approval_outer_${elementID}`).prepend(audit_html)


                new_comment_reply_editor = CKEDITOR.replace(`convo_replycomment_${count}0`,
                {
                  height: 44,
                  removeButtons: home_rtf[0],
                  editorplaceholder: "Type your reply here..." ,
                  plugins: 'mentions,undo,link,list,basicstyles,justify,richcombo,wysiwygarea,toolbar',
                  extraPlugins: 'elementspath,editorplaceholder',
                  toolbar: [
                    { name: 'document', items: ['Undo'] },
                    { name: 'paragraph', items: ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'] },
                    { name: 'basicstyles', items: ['Bold', 'Italic', 'Underline', 'Strike', '-', 'RemoveFormat'] },
                    { name: 'links', items: ['Mention', 'Link', 'Unlink', 'Anchor'] },
                    { name: 'styles', items: ['Styles', 'Format', 'Font', 'FontSize'] },
                    { name: 'colors', items: ['TextColor', 'BGColor'] },
                    { name: 'elementspath', items: ['ElementPath'] }
                  ],
                  mentions: [
                      {
                      feed: dataFeed,
                      itemTemplate: itemTemplate,
                      outputTemplate: outputTemplate,
                      minChars: 0
                      }
                  ],
                  removeButtons: 'PasteFromWord'
                });
                CKEDITOR.config.removePlugins = 'exportpdf';
                CKEDITOR.config.extraPlugins = 'autocorrect,elementspath';

                CKEDITOR.instances[`convo_replycomment_${count}0`].setData('');

                new_comment_reply_editor = CKEDITOR.instances[`convo_replycomment_${count}0`]
                new_comment_reply_editor.on('change',function(){
                  let typedText = new_comment_reply_editor.getData();
                  if(typedText.trim() === ''){
                    $(`#convo_replybutton_${count}0`).prop("disabled",true)
                  }
                  else{
                    $(`#convo_replybutton_${count}0`).prop("disabled",false)
                  }
                })

                new_comment_reply_editor.on('key',function(event){
                  if (event.data.keyCode === CKEDITOR.CTRL + 13){
                    $(`#convo_replybutton_${count}0`).trigger("click")
                  }
                })


            },
            error: function () {
              Swal.fire({icon: 'error',text: 'Error! Please try again.'});
            }
          });
        }
      });

      if(!allowed_approval=="true" && !allowed_edit == "true" && !allowed_rejection=="true"){
        $(`#approvalWallModalBody_${elementID}`).find(`#reopen_all_button_${elementID}`).css("display","none")
        $(`#approvalWallModalBody_${elementID}`).find(`#resolve_all_button_${elementID}`).css("display","none")
        $(`#approvalWallModalBody_${elementID}`).find(`.resolve_button_ind`).css("display","none")
        $(`#approvalWallModalBody_${elementID}`).find(`.reopen_button_ind`).css("display","none")
      }


      $(`#approvalCommentsModal_${elementID}`).modal("show")

    },
    error: function () {
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    }
  });
}

