/* eslint camelcase: ["error", {ignoreGlobals: true,properties:'never'}] */
/* eslint valid-typeof: ["error", { "requireStringLiterals": true }] */

/* global  edit_col_list,WebSocket,functionsList,tableList,EBTables,favouriteList,selectedTablesDiv,dataElementParent,stepNumsEb,searchTable,tb_index */

/* eslint-disable  */
var hpCharacters = []
var favFunctionList = []
var currentTab = ''
var draggables = []
var counter = 0
var cDict = {}
var indexCount = 0
var previewOperator = ''
var myTruncatedString = ''
var selectedCol = ''
var funcDic = []
var charactersList = document.getElementById('charactersList')
var searchBar = document.getElementById('searchBar')
var allTables = []
var selectedTables = {}
var uniqueid = ''
var validFlag = true
var listViewComp = false
var listViewModelName = ""
var listViewCompCol = ""
var compValProcess = ""
var compValProcessName = ""
var compValVarName = []
/* eslint-enable */

/* eslint-disable no-var, no-unused-vars  */
var previewString
var cIndex
var iid
var stepCount = 1
var EBtables = []
var idenFlag = ''
var idenFlag2 = ''
var tempdd = {}
var MelementID = ''

const columnList = ['Column 1', 'column 2', 'column 3', 'column 4', 'column 5', 'column 6', 'column 7', 'column 8', 'Column 1', 'column 2', 'column 3', 'column 4', 'column 5', 'column 6', 'column 7', 'column 8', 'Column 1', 'column 2', 'column 3', 'column 4', 'column 5', 'column 6', 'column 7', 'column 8']
/* eslint-enable */

function datatables(id) {
  $('#' + id).DataTable({
    autoWidth: true,
    scrollY: '25vh',
    scrollX: '110%',
    scrollCollapse: true,
    responsive: true,
    deferRender: true,
    paging: false,
    searching: false,
    info: true,
    order: [],
    stripeClasses: false,
    pageLength: 100,
    dom: 'lfBrtip',
    buttons: [],
    columnDefs: [
      {
        targets: '_all',
        className: 'dt-center allColumnClass all'
      },
      {
        targets: 0,
        width: '20%',
        className: 'noVis'
      }
    ]

  }).columns.adjust()
}

// loading all prerequisite data

const loadEBData = () => {
  setTimeout(function () {
    try {

      $.ajax({
        url: `/users/${urlPath}/computationModule/`,
        data: {
          operation: 'fetch_all_ops'
        },
        type: 'POST',
        dataType: 'json',
        success: function (data) {
          for (const i in data.ops) {
            const item = data.ops[i]
            if ((typeof ($('#tname').val()) === 'undefined') || (typeof (computationCondition) == 'function')) {
              funcDic.push(
                {
                  name: item
                }
              )
            } else {
                funcDic.push(
                  {
                    name: item
                  }
                )
            }
          }

          hpCharacters = funcDic
          displayCharacters(funcDic)
          document.querySelectorAll('.tableItemP').forEach(item => EBtables.push(item.innerText))
        },
        error: function () {
          Swal.fire({icon: 'error',text: 'Error! Please try again.'});
        }
      })

      displayTables(EBTables)
    } catch (err) {

    }
  }, 700)
}

loadEBData()

// all search functions
searchBar.addEventListener('keyup', (e) => {
  const searchString = e.target.value
  const filteredCharacters = hpCharacters.filter(item => {
    return item.name.toLowerCase().includes(searchString.toLowerCase())
  })
  displayCharacters(filteredCharacters)
})

searchTable.addEventListener('keyup', (e) => {
  const searchString = e.target.value

  const filteredTables = []
  EBtables.map(item => {
    if (item.toLowerCase().includes(searchString.toLowerCase())) {
      filteredTables.push(item)
    }
    return filteredTables
  })
  displayTables(filteredTables)
})

// adding div to sote data elements
function addColDiv() {
  $('#exampledata1').remove()
  $('#exampledata1_wrapper').remove()
  const div = document.createElement('div')
  let name_ = ""
  if(compValProcess){
    name_ = compValProcessName
  }else{
    name_ = $('#EBDisplayButtonID').attr('data-name')
  }
  let dataID = 'comp'
  let elementName = ''
  let restrictFlag = 0
  let configDictT = {}
  let currentTable = ''
  let currTable
  if (typeof (name_) === 'undefined') {
    name_ = $('#FileName').attr('data-experimentName')
    if (typeof (name_) === 'undefined') {
      dataID = 'datamgm'

      if ($('#tname').val() && String(idenFlag) !== 'add') {
        name_ = $('#tname').val()
      } else if (String(idenFlag) === 'add' || String(idenFlag) === 'edit') {
        name_ = $('.dataElements').find('p').text()
      }
      else if (listViewComp == true) {
        name_ = listViewModelName
      }
    }
  }

  div.className = 'ebDataElementsDiv dragAreaPossible'

  const btn = document.createElement('button')
  btn.className = 'btn btn-primary btn-xs mx-2 rounded px-2'
  btn.innerHTML = 'Data'
  btn.addEventListener('click', function () {
    const columnssList = []
    const columnsList = []
    let tablePC = ""
    let sTableName = []
    let tEleID = []
    const table1 = []
    const table2 = []
    let currTable1
    let a

    const tableName = new Set()
    const eleID = new Set()

    const b = $(this).parent('.ebDataElementsDiv').find('.ColumnItem')
    for (let i = 0; i < b.length; i++) {
      tableName.add(b[i].getAttribute('data-table'))
      eleID.add(b[i].getAttribute('data-element_id'))
    }

    sTableName = Array.from(tableName)
    tEleID = Array.from(eleID)

    if (String(dataID) === 'datamgm') {
      if (String(idenFlag) !== 'add' && String(idenFlag) !== 'edit' && listViewComp == false) {
        currTable1 = $('#tname').val()
      } else if (String(idenFlag) === 'add' || String(idenFlag) === 'edit') {
        currTable1 = $('.dataElements').find('p').text()
      } else if (listViewComp == true) {
        currTable1 = listViewModelName
      }
    } else {
      currTable1 = ''
    }
    const bb = $(this).parent('.ebDataElementsDiv').find('.ColumnItem')

    if (sTableName.length > 1) {
      for (let i = 0; i < sTableName.length - 1; i++) {
        currTable = sTableName[i]

        for (let j = 0; j < bb.length; j++) {
          if (String(bb[j].getAttribute('data-table')) === String(currTable)) {
            table1.push(bb[j].querySelector('p').innerText)
          } else {
            table2.push(bb[j].querySelector('p').innerText)
          }
        }

        columnssList.push(table1)
        columnssList.push(table2)
      }
    } else {
      a = $(this).parent('.ebDataElementsDiv').find('.ColumnItem').find('p')
      for (let i = 0; i < a.length; i++) {
        columnsList.push(a[i].innerText)
      }
      columnssList.push(columnsList)
    }

    if (
      !(sTableName.includes(name_)) && String(dataID) === 'datamgm' && String($(this).parent().index()) === '1'
    ) {
      restrictFlag = 1
    }

    if (restrictFlag) {
      Swal.fire({icon: 'warning',text:"Kindly select the Join operation first with the existing and newly created table." });
    } else {
      for (let j = 0; j < sTableName.length; j++) {
        if (String(sTableName[j]) === String(currTable1)) {
          currentTable = 'Yes'
        } else {
          currentTable = 'No'
        }
        configDictT = {
          function: 'Import Data',
          data_mapper: { current_element_name: sTableName[j] },
          inputs: {
            Data_source: 'Database',
            Table: sTableName[j],
            Columns: columnssList[j],
            global_var: '',
            parent_table_column: '',
            current_table_column: '',
            show_foreignKey_value: false,
            current_table: currentTable
          },
          condition: {}
        }
        configDictT.outputs = {
          name: '',
          save: ''
        }
        tablePC = currentTable

        if (String(dataID) === 'comp') {
          $('#where_condition').attr('data-data', JSON.stringify(({
            data1: name_,
            data2: tEleID[j],
            data3: configDictT,
            elementName: tEleID[j]
          }))
          )
          // eslint-disable-next-line no-undef
          if (typeof (filter_list[tEleID[j]]) !== 'undefined') {
            // eslint-disable-next-line no-undef
            configDictT.condition = filter_list[tEleID[j]]
          } else {
            // eslint-disable-next-line no-undef
            filter_list[tEleID[j]] = []
          }
        }

        if (String(dataID) === 'comp') {
          elementName = tEleID[j]
        } else if (String(dataID) === 'datamgm' && listViewComp == false) {
          elementName = name_ + selectedCol + Math.floor((Math.random() * 10000000000) + 1)
        } else if (String(dataID) === 'datamgm' && listViewComp == true) {
          elementName = name_ + listViewCompCol + Math.floor((Math.random() * 10000000000) + 1)
        }

        $.ajax({
          url: `/users/${urlPath}/computationModule/`,
          data: {
            configList: JSON.stringify({
              data1: name_,
              data2: tEleID[j],
              data3: configDictT,
              elementName: elementName,
              data_id: dataID
            }),
            operation: 'save_import_data',
            data_source: 'Database'
          },
          type: 'POST',
          dataType: 'json',
          success: function (context) {
            if (String(dataID) === 'datamgm') {
              Swal.fire({icon: 'success',text: 'Import Configuration saved successfully!'});
            } else if (String(dataID) === 'comp') {
              if (compValProcess){
                is_create_val = "yes"
              }else{
                is_create_val = "no"
              }
              $.ajax({
                url: `/users/${urlPath}/computationModule/`,
                data: {
                  operation: 'data_reload',
                  element_id: tEleID[j],
                  model_name: name_,
                  model_element_id: MelementID,
                  is_create_val: is_create_val
                },
                type: 'POST',
                dataType: 'json',
                success: function (data) {
                  Swal.fire({icon: 'success',text: 'Import Configuration saved successfully! \n Executing the block. Please wait..'});
                  const jobId = data.job_id
                  const runStepBtnId = ''
                  const runStepBtnLoadId = ''
                  fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)
                },
                error: function () {
                  Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                }
              })
            }
          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          }
        })
      }
    }
  })
  div.append(btn)
  dataElementParent.append(div)

  const dragAreas = document.querySelectorAll('.dragAreaPossible')

  dragAreas.forEach(dragArea => {
    dragArea.addEventListener('dragover', e => {
      e.preventDefault()
      const afterElement = getDragAfterElement1(dragArea, e.clientY)
      const draggable = document.querySelector('.dragging')

      if (afterElement === null) {
        dragArea.appendChild(draggable)

        if (dragArea.querySelector('.EbOverlay')) {
          dragArea.querySelector('.EbOverlay').className = 'EBshow'
        }

        if (dragArea.querySelector('.heartIcon')) {
          dragArea.querySelector('.heartIcon').className = 'EBhide'
        }
      } else {
        dragArea.insertBefore(draggable, afterElement)

        if (dragArea.querySelector('.EbOverlay')) {
          dragArea.querySelector('.EbOverlay').className = 'EBshow'
        }

        if (dragArea.querySelector('.heartIcon')) {
          dragArea.querySelector('.heartIcon').className = 'EBhide'
        }
      }
    })
  })

  function getDragAfterElement1(container, y) {
    const draggableElements = [...container.querySelectorAll('.draggable:not(.dragging)')]
    return draggableElements.reduce((closest, child) => {
      const box = child.getBoundingClientRect()
      const offset = y - box.top - box.height / 2
      if (offset < 0 && offset > closest.offset) {
        return { offset: offset, element: child }
      } else {
        return closest
      }
    }, { offset: Number.POSITIVE_INFINITY }).element
  }
}

// functions
function countSteps(steps) {
  const stepList = []
  for (let i = 1; i <= steps; i++) {
    stepList.push(i)
  }
  const htmlString = stepList.map(item => {
    return `
        <h2 class="stepNumberEB">${item}</h2>
        `
  })
    .join('')
  stepNumsEb.innerHTML = htmlString
}
function displayPreviews() {
  const functionDiv = document.querySelector('.ebFunctions')
  const functions = functionDiv.querySelectorAll('.function')
  const listOfFunctions = []
  let dataID = ''
  functions.forEach(item => {
    listOfFunctions.push(item.querySelector('h2').innerText)
  })
  const multiple = $('.ebDataElementsDiv').length
  indexCount = listOfFunctions.length
  countSteps(listOfFunctions.length)
  if (typeof ($('#tname').val()) === 'undefined' && listViewComp == false) {
    dataID = 'comp'
  } else {
    dataID = 'datamgm'
  }
  if (listOfFunctions.length > counter && multiple < indexCount) {
    addColDiv()
    if (String(counter) === '0') {
      $('.ebFunctions').find('div').eq(counter).find('span').css('display', 'block')
    } else {
      $('.ebFunctions').find('div').eq(counter).find('span').css('display', 'block')
      $('.ebFunctions').find('div').eq(counter - 1).find('span').css('display', 'none')
    }
    counter++
    $('#functionPreviews').append(
      `
            <div class="function" onclick="">

                <h2></h2>
                <p style="display:none;"></p>

            </div>
        `)
  }
}

// display favourites

function displayFav(favFunctionList) { // eslint-disable-line no-unused-vars
  const minm = 1000000000000
  const maxm = 9999999999999
  let dataID
  const uniqueidMaths = 'applyMathOps' + (Math.floor(Math.random() * (maxm - minm + 1)) + minm).toString()
  const uniqueidJoin = 'mergeAndJoin' + (Math.floor(Math.random() * (maxm - minm + 1)) + minm).toString()
  const uniqueidRename = 'renameColumn' + (Math.floor(Math.random() * (maxm - minm + 1)) + minm).toString()
  const uniqueidPivot = 'pivotAndTranspose' + (Math.floor(Math.random() * (maxm - minm + 1)) + minm).toString()
  const uniqueidConcat = 'concatColumn' + (Math.floor(Math.random() * (maxm - minm + 1)) + minm).toString()

  if (typeof ($('#tname').val()) === 'undefined' && listViewComp == false) {
    dataID = 'comp'
  } else {
    dataID = 'datamgm'
  }

  const htmlString = favFunctionList
    .map((func) => {
      if (String(func) === 'Left Join' || String(func) === 'Right Join' || String(func) === 'Inner Join' || String(func) === 'Outer Join' || String(func) === 'Filter' || String(func) === 'Add Column' || String(func) === 'Append and Concatenate' || String(func) === 'Sort' || String(func) === 'Groupby') {
        return `
        <div class="function draggable" draggable="true">
            <h2>${func}</h2>
            <h3 class="RemoveIcon heartIcon" onClick="removeFav('${func}')">&#10006;</h3>
            <a title="configure" href="#" name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueidJoin}" data-element_comp="${dataID}"  onClick="popupOpen();takeFuncInput('${func}','${uniqueidJoin}','${indexCount}',this)">&#11167;</a>
        </div>
    `
      } else if (String(func) === 'Rename and Drop') {
        return `
        <div class="function draggable" draggable="true">
            <h2>${func}</h2>
            <h3 class="RemoveIcon heartIcon" onClick="removeFav('${func}')">&#10006;</h3>
            <a title="configure" href="#" name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueidRename}" data-element_comp="${dataID}" onClick="popupOpen();takeFuncInput('${func}','${uniqueidRename}','${indexCount}',this)">&#11167;</a>
        </div>
    `
      } else if (String(func) === 'Pivot' || String(func) === 'Unpivot') {
        return `
        <div class="function draggable" draggable="true">
            <h2>${func}</h2>
            <h3 class="RemoveIcon heartIcon" onClick="removeFav('${func}')">&#10006;</h3>
            <a title="configure" href="#" name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueidPivot}" data-element_comp="${dataID}" onClick="popupOpen();takeFuncInput('${func}','${uniqueidPivot}','${indexCount}',this)">&#11167;</a>
        </div>
    `

      } else if (String(func) === 'Concat Columns') {
        return `
        <div class="function draggable" draggable="true">
            <h2>${func}</h2>
            <h3 class="RemoveIcon heartIcon" onClick="removeFav('${func}')">&#10006;</h3>
            <a title="configure" href="#" name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueidConcat}" data-element_comp="${dataID}" onClick="popupOpen();takeFuncInput('${func}','${uniqueidConcat}','${indexCount}',this)">&#11167;</a>
        </div>
    `
      } else {
        return `
        <div class="function draggable" draggable="true">
            <h2>${func}</h2>
            <h3 class="RemoveIcon heartIcon" onClick="removeFav('${func}')">&#10006;</h3>
            <a title="configure" href="#" name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueidMaths}" data-element_comp="${dataID}" onClick="popupOpen();takeFuncInput('${func}','${uniqueidMaths}','${indexCount}',this)">&#11167;</a>
        </div>
    `
      }
    })
    .join('')
  favouriteList.innerHTML = htmlString

  draggables = document.querySelectorAll('.draggable')
  draggables.forEach(draggable => {
    draggable.addEventListener('dragstart', (e) => {
      draggable.classList.add('dragging')
    })

    draggable.addEventListener('dragend', (e) => {
      draggable.classList.remove('dragging')
      displayPreviews()
      displayFav(favFunctionList)
      displayCharacters(funcDic)
    })
  })
}
// add functions to favourite
function addToFav(name) { // eslint-disable-line no-unused-vars
  favFunctionList.push(name)
  if (favFunctionList.length > 0) {
    if ($('#favouriteList').attr('data-element_id') === undefined) {
      $('#favouriteList').attr('data-element_id', 'saveFav' + (Math.floor(Math.random() * (9999999999999 - 1000000000000 + 1)) + 1000000000000).toString())
    }
  }
  displayFav(favFunctionList)
}
// remove from fav

function removeFav(remFunc) { // eslint-disable-line no-unused-vars
  const indexFunc = favFunctionList.indexOf(remFunc)

  favFunctionList.splice(indexFunc, 1)
  if (String(favFunctionList.length) === '0') {
    if ($('#favouriteList').attr('data-element_id') !== undefined) {
      $('#favouriteList').removeAttr('data-element_id')
    }
  }
  displayFav(favFunctionList)
}

// everytime a tab div is clicked

function changeTab(tabname) { // eslint-disable-line no-unused-vars
  currentTab = tabname
  const s = tabname.split('-')
  tabname = s[0]
  displaySelectedTables()
  let colList = []
  if (String($('#tname').val()) === String(tabname) && String(idenFlag) !== 'add') {
    $(`#table .hide`).slice(0,tb_index + 1).each(function () {
      colList.push($(this).find('td').find('#fld_name').text())
    })

    displayColumns(colList, tabname)
  } else if (String(idenFlag) === 'edit') {
    colList = edit_col_list
    displayColumns(colList, tabname)
  } else {
    $.ajax({
      url: `/users/${urlPath}/computationModule/`,
      data: {
        table_name: tabname,
        operation: 'fetch_table_columns'
      },
      type: 'POST',
      dataType: 'json',
      success: function (data) {
        $('#selectColumn').empty()
        for (const i in data.columnList) {
          colList.push(data.columnList[i])
        }

        if (String(idenFlag) === 'add') {
          if (!(colList.includes($('#fieldmdl').val()))) {
            colList.push($('#fieldmdl').val())
          }
        }

        displayColumns(colList, tabname)
      },
      error: function () {
        Swal.fire({icon: 'error',text: 'Error! Please try again.'});
      }
    })
  }
}

// displayselectedtables function will check if there is a current tab as well
const displaySelectedTables = () => {
  const htmlString = Object.keys(selectedTables)
    .map(function (key, index) {
      if (String(key) !== String(currentTab)) {
        return `
            <div class="selectedTableItem" data-element_id="${selectedTables[key]}" onClick="changeTab('${key}')">
                <p>${key}</p>
                <pre class="RemoveIcon"  onClick="removeSelectedTable('${key}')">&#10006;</pre>
            </div>
        `
      } else {
        return `
            <div class="selectedTableItem active_table" data-element_id="${selectedTables[key]}" style="background:rgb(206, 206, 206)" onClick="changeTab('${key}')">
                <p>${key}</p>
                <pre class="RemoveIcon"  onClick="removeSelectedTable('${key}')">&#10006;</pre>
            </div>
        `
      }
    })
    .join('')
  selectedTablesDiv.innerHTML = htmlString
}

// add columns

const displayColumns = (columns, tableName) => {
  let dataID = ''
  if (String(typeof ($('#tname').val())) === 'undefined' && listViewComp == false) {
    dataID = 'comp'
  } else {
    dataID = 'datamgm'
  }

  // const currentColumns = columns
  const ss = $('.active_table').find('p')[0].innerText.split('-')
  const sTableName = ss[0]
  const tEleID = $('.active_table').attr('data-element_id')

  const htmlString = columns
    .map((item) => {
      if (String(dataID) === 'datamgm') {
        if (String(idenFlag) === 'attr') {
          return `
                            <div class="ColumnItem" data-table="${sTableName}" data-element_id="${tEleID}" data-element_comp="${dataID}" data-func_id='${indexCount}'>
                                <p>${item}</p>
                            </div>
                        `
        } else {
          return `
                        <div class="ColumnItem draggable" draggable="true" data-table="${sTableName}" data-element_id="${tEleID}" data-element_comp="${dataID}" data-func_id='${indexCount}'>
                            <p>${item}</p>
                        </div>
                    `
        }
      } else {
        return `
                    <div class="ColumnItem draggable" draggable="true" data-table="${sTableName}" data-element_id="${tEleID}" data-element_comp="${dataID}" data-func_id='${indexCount}'>
                        <p>${item}</p>
                    </div>
                `
      }
    })
    .join('')
  document.querySelector('#table-columns').innerHTML = htmlString

  // adding draggable event listeners

  draggables = document.querySelectorAll('.draggable')
  draggables.forEach(draggable => {
    draggable.addEventListener('dragstart', (e) => {
      draggable.classList.add('dragging')
    })

    draggable.addEventListener('dragend', (e) => {
      draggable.classList.remove('dragging')
    })
  })
}

const removeSelectedTable = (table) => { // eslint-disable-line no-unused-vars
  delete selectedTables[table]
  displaySelectedTables()
}
const selectTable = (tableName) => { // eslint-disable-line no-unused-vars
  currentTab = tableName

  const minm = 1000000000000
  const maxm = 9999999999999

  if (currentTab in selectedTables) {
    tableName = tableName + '-' + stepCount.toString()
    stepCount++
  }

  if ((String(idenFlag) === 'edit' && (tableName in tempdd)) || (String(idenFlag2) === "scen_old" && (tableName in tempdd))) {
    selectedTables[tableName] = tempdd[tableName]
  } else {
    selectedTables[tableName] = 'importData' + (Math.floor(Math.random() * (maxm - minm + 1)) + minm).toString()
  }
  displaySelectedTables()
  changeTableandColumns(tableName)
}

// take function inputs in the overlay && set description
const setDesc = (desc) => { // eslint-disable-line no-unused-vars
  const description = document.querySelector('#funcDesc')
  description.innerText = desc
}

const saveData = (name, flag, uID, ind) => { // eslint-disable-line no-unused-vars
  previewString = ''
  let tableName = []
  let currentTable = ''
  let tablePC = currentTable
  let currTable
  let a
  let b
  let tableEleID = ''
  let configDictMergeGroup = ""
  const tabList = $('.ebDataElementsDiv').eq(parseInt(0)).find('.ColumnItem')
  // eslint-disable-next-line no-var
  var configDict = {}
  const tablesList = new Set()
  for (let i = 0; i < tabList.length; i++) {
    tablesList.add(tabList[i].getAttribute('data-table'))
  }

  tableName = Array.from(tablesList)

  if (String(idenFlag) !== 'add') {
    currTable = $('#tname').val()
  } else if (String(idenFlag) === 'add' || String(idenFlag) === 'edit') {
    currTable = $('.dataElements').find('p').text()
  } else if (listViewComp == true) {
    currTable = listViewModelName
  }
  if (typeof (currTable) === 'undefined') {
    currTable = ''
  }

  if (tableName.includes(currTable)) {
    currentTable = 'Yes'
  } else {
    currentTable = 'No'
  }

  a = $('.ebDataElementsDiv').find('div')

  if (String(parseInt(ind)) === '0') {
    try {
      tableEleID = a[parseInt(ind)].getAttribute('data-element_id')
    } catch (err) {
      b = $('.ebFunctions').find('div').find('a')

      tableEleID = b[parseInt(ind - 1)].getAttribute('data-element_id')
    };
  } else {
    a = $('.ebFunctions').find('div').find('a')
    tableEleID = a[parseInt(ind - 1)].getAttribute('data-element_id')
  }
  if (String(cDict.Operation) === 'Column sum' ||
    String(cDict.Operation) === 'Row sum' ||
    String(cDict.Operation) === 'Cell sum' ||
    String(cDict.Operation) === 'Column subtraction' ||
    String(cDict.Operation) === 'Row subtraction' ||
    String(cDict.Operation) === 'Cell subtraction' ||
    String(cDict.Operation) === 'Column multiplication' ||
    String(cDict.Operation) === 'Row multiplication' ||
    String(cDict.Operation) === 'Cell multiplication' ||
    String(cDict.Operation) === 'Column division' ||
    String(cDict.Operation) === 'Row division' ||
    String(cDict.Operation) === 'Cell division'
  ) {
    let number = 0
    let subOP = ''
    let colList1 = ''
    let colList2 = ''
    let Typechoice = ''
    let Datachoice = ''
    let Cell11 = ''
    let Cell12 = ''
    let Cell21 = ''
    let Cell22 = ''
    let Target1 = ''
    let Target2 = ''
    let Dcols = []

    if (String(cDict.Operation) === 'Column sum' || String(cDict.Operation) === 'Row sum' || String(cDict.Operation) === 'Cell sum') {
      subOP = cDict.Operation
      previewOperator = ' + '
    } else if (String(cDict.Operation) === 'Column subtraction' || String(cDict.Operation) === 'Row subtraction' || String(cDict.Operation) === 'Cell subtraction') {
      subOP = cDict.Operation
      previewOperator = ' - '
    } else if (String(cDict.Operation) === 'Column multiplication' || String(cDict.Operation) === 'Row multiplication' || String(cDict.Operation) === 'Cell multiplication') {
      subOP = cDict.Operation
      previewOperator = ' * '
    } else if (String(cDict.Operation) === 'Column division' || String(cDict.Operation) === 'Row division' || String(cDict.Operation) === 'Cell division') {
      subOP = cDict.Operation
      previewOperator = ' / '
    }

    if (String(cDict.Operation) === 'Column sum' || String(cDict.Operation) === 'Column subtraction' ||
      String(cDict.Operation) === 'Column multiplication' || String(cDict.Operation) === 'Column division'
    ) {
      if (cDict.Column_sum1.length >= 1 && String(cDict.Column_sum2) === '') {
        number = ''
        colList1 = cDict.Column_sum1
        Typechoice = 'Column_Sum'
        Datachoice = 'Dataframe_input'
        Dcols = cDict.Column_sum1

        for (let i = 0; i < cDict.Column_sum1.length; i++) {
          if (String(i) === '0') {
            previewString = previewString + cDict.Column_sum1[i]
          } else {
            previewString = previewString + previewOperator + cDict.Column_sum1[i]
          }
        }
      } else if (cDict.Column_sum1.length >= 1 && String(cDict.Column_sum2) !== '') {
        number = parseFloat(cDict.Column_sum2)
        colList1 = cDict.Column_sum1
        Typechoice = 'Column_Sum'
        Datachoice = 'Custom_input'
        Dcols = cDict.Column_sum1

        previewString = cDict.Column_sum1 + previewOperator + cDict.Column_sum2
      }
    } else if (String(cDict.Operation) === 'Row sum' || String(cDict.Operation) === 'Row subtraction' ||
      String(cDict.Operation) === 'Row multiplication' || String(cDict.Operation) === 'Row division'
    ) {
      if (cDict.Row_sum1.length >= 1 && String(cDict.Row_sum2) === '') {
        number = ''
        colList1 = cDict.Row_sum1.map((i) => Number(i))
        Typechoice = 'Row_Sum'
        Datachoice = 'Dataframe_input'

        for (let i = 0; i < cDict.Row_sum1.length; i++) {
          if (String(i) === '0') {
            previewString = previewString + cDict.Row_sum1[i]
          } else {
            previewString = previewString + previewOperator + cDict.Row_sum1[i]
          }
        }
      } else if (cDict.Row_sum1.length >= 1 && String(cDict.Row_sum2) !== '') {
        number = parseFloat(cDict.Row_sum2)
        colList1 = cDict.Row_sum1.map((i) => Number(i))
        Typechoice = 'Row_Sum'
        Datachoice = 'Custom_input'

        previewString = cDict.Row_sum1 + previewOperator + cDict.Row_sum2
      }
    } else {
      if (String(cDict.Cell_11.length) === '1' && String(cDict.Cell_12.length) === '1' && String(cDict.Cell_21.length) === '1' && String(cDict.Cell_22.length) === '1' && String(cDict.Cell_sum3) === '') {
        number = ''
        colList1 = ''
        colList2 = ''
        Typechoice = 'Cell_Sum'
        Datachoice = 'Dataframe_input'
        Cell11 = cDict.Cell_11.map((i) => Number(i))
        Cell12 = cDict.Cell_12
        Cell21 = cDict.Cell_21.map((i) => Number(i))
        Cell22 = cDict.Cell_22
        Target1 = cDict.Target_Cell_11.map((i) => Number(i))
        Target2 = cDict.Target_Cell_22

        previewString = cDict.Cell_11 + cDict.Cell_12 + previewOperator + cDict.Cell_21 + cDict.Cell_22
      } else if (String(cDict.Cell_11.length) === '1' && String(cDict.Cell_12.length) === '1' && String(cDict.Cell_21.length) === '0' && String(cDict.Cell_22.length) === '0' && String(cDict.Cell_sum3) !== '') {
        number = parseFloat(cDict.Cell_sum3)
        colList1 = ''
        colList2 = ''
        Typechoice = 'Cell_Sum'
        Datachoice = 'Custom_input'
        Cell11 = cDict.Cell_11.map((i) => Number(i))
        Cell12 = cDict.Cell_12
        Target1 = cDict.Target_Cell_11.map((i) => Number(i))
        Target2 = cDict.Target_Cell_22

        previewString = cDict.Cell_11 + cDict.Cell_12 + previewOperator + cDict.Cell_sum3
      }
    }

    configDict = {
      function: 'Apply Math Operation',
      inputs: {
        data: { Data1: tableEleID },
        Data_choice: Datachoice,
        Column_1: colList1,
        Column_2: colList2,
        Number: number,
        Operation: 'Basic Operations',
        Sub_Op: subOP,
        Column_name: cDict.Target_Column1,
        Additional_Colns: '',
        Other_Inputs: {
          Type_choice: Typechoice,
          Cell_11: Cell11,
          Cell_12: Cell12,
          Cell_21: Cell21,
          Cell_22: Cell22,
          Target_1: Target1,
          Target_2: Target2,
          previewString: previewString
        },
        D_cols: Dcols,
        table_name: tableName,
        current_table: currentTable
      }
    }
  } else if (String(cDict.Operation) === 'Round') {
    let subOP = ''
    let col1 = ''
    let col2 = ''
    let signifmul = ''
    let decimal = ''
    let Dcols = []

    if (String(cDict.Ceiling1) !== '' && String(cDict.Ceiling_Significance_Multiple2) !== '') {
      subOP = 'Ceiling'
      col1 = cDict.Ceiling1
      col2 = cDict.Ceiling1
      signifmul = cDict.Ceiling_Significance_Multiple2
      decimal = ''
      Dcols = [cDict.Ceiling1]
      previewString = 'Ceiling of ' + cDict.Ceiling1 + ' to the power of ' + cDict.Ceiling_Significance_Multiple2
    } else if (String(cDict.Floor1) !== '' && String(cDict.Floor_Significance_Multiple2) !== '') {
      subOP = 'Floor'
      col1 = cDict.Floor1
      col2 = cDict.Floor1
      signifmul = cDict.Floor_Significance_Multiple2
      decimal = ''
      Dcols = [cDict.Floor1]
      previewString = 'Floor of ' + cDict.Floor1 + ' to the power of ' + cDict.Floor_Significance_Multiple2
    } else if (String(cDict.Odd1) !== '') {
      subOP = 'Odd'
      col1 = cDict.Odd1
      col2 = cDict.Odd1
      signifmul = ''
      decimal = ''
      Dcols = [cDict.Odd1]
      previewString = 'Odd of ' + cDict.Odd1
    } else if (String(cDict.Even1) !== '') {
      subOP = 'Even'
      col1 = cDict.Even1
      col2 = cDict.Even1
      signifmul = ''
      decimal = ''
      Dcols = [cDict.Even1]
      previewString = 'Even of ' + cDict.Even1
    } else if (String(cDict.Round1) !== '' && String(cDict.No_of_Decimals2) !== '') {
      subOP = 'Round'
      col1 = cDict.Round1
      col2 = cDict.Round1
      signifmul = ''
      decimal = cDict.No_of_Decimals2
      Dcols = [cDict.Round1]
      previewString = 'Round of ' + cDict.Round1 + ' by ' + cDict.No_of_Decimals2 + ' places'
    } else if (String(cDict.Round_Up1) !== '') {
      subOP = 'Round_Up'
      col1 = cDict.Round_Up1
      col2 = cDict.Round_Up1
      signifmul = ''
      decimal = ''
      Dcols = [cDict.Round_Up1]
      previewString = 'Round Up of ' + cDict.Round_Up1
    } else if (String(cDict.Round_Down1) !== '') {
      subOP = 'Round_Down'
      col1 = cDict.Round_Down1
      col2 = cDict.Round_Down1
      signifmul = ''
      decimal = ''
      Dcols = [cDict.Round_Down1]
      previewString = 'Round Down of ' + cDict.Round_Down1
    } else if (String(cDict.Truncate1) !== '') {
      subOP = 'Truncate'
      col1 = cDict.Truncate1
      col2 = cDict.Truncate1
      signifmul = ''
      decimal = ''
      Dcols = [cDict.Truncate1]
      previewString = 'Truncate of ' + cDict.Truncate1
    }

    configDict = {
      function: 'Apply Math Operation',
      inputs: {
        data: { Data1: tableEleID },
        Column_1: col1,
        Column_2: col2,
        Operation: 'Rounding Operations',
        Sub_Op: subOP,
        Column_name: cDict.Target_Column1,
        Additional_Colns: [],
        Other_Inputs: {
          Output_choice: 'No_replace',
          Signif_Multiple: signifmul,
          Decimal: decimal,
          previewString: previewString
        },
        D_cols: Dcols,
        table_name: tableName,
        current_table: currentTable
      }
    }
  } else if (String(cDict.Operation) === 'Log') {
    let subOP = ''
    let col1 = ''
    let col2 = ''
    let logBase = ''
    let Dcols = []

    if (String(cDict.Base_Log1) !== '' && String(cDict.Log_Base_value2) !== '') {
      subOP = 'Log_base'
      col1 = cDict.Base_Log1
      col2 = cDict.Base_Log1
      logBase = cDict.Log_Base_value2
      Dcols = [cDict.Base_Log1]
      previewString = 'Log of ' + cDict.Base_Log1 + ' to the base ' + cDict.Log_Base_value2
    } else if (String(cDict.Exponential1) !== '') {
      subOP = 'Exponential'
      col1 = cDict.Exponential1
      col2 = cDict.Exponential1
      logBase = '2'
      Dcols = [cDict.Exponential1]
      previewString = 'Exponential of ' + cDict.Exponential1
    } else if (String(cDict.Natural_Log1) !== '') {
      subOP = 'Natural_Log'
      col1 = cDict.Natural_Log1
      col2 = cDict.Natural_Log1
      Dcols = [cDict.Natural_Log1]
      previewString = 'Natural Log of ' + cDict.Natural_Log1
    }

    configDict = {
      function: 'Apply Math Operation',
      inputs: {
        data: { Data1: tableEleID },
        Column_1: col1,
        Column_2: col2,
        Operation: 'Log and Exponential Functions',
        Sub_Op: subOP,
        Column_name: cDict.Target_Column1,
        Additional_Colns: [],
        Other_Inputs: {
          Log_Base: logBase,
          previewString: previewString
        },
        D_cols: Dcols,
        table_name: tableName,
        current_table: currentTable
      }
    }
  } else if (String(cDict.Operation) === 'Square root') {
    let col1 = ''
    let col2 = ''
    let powerInput = ''
    let Dcols = []

    if (String(cDict.Root_Operation1) !== '' && String(cDict.Root_Operation2) !== '') {
      col1 = cDict.Root_Operation1
      col2 = cDict.Root_Operation1
      powerInput = cDict.Root_Operation2
      Dcols = [cDict.Root_Operation1]
      previewString = cDict.Root_Operation1 + ' ^ ' + cDict.Root_Operation2
    }

    configDict = {
      function: 'Apply Math Operation',
      inputs: {
        data: { Data1: tableEleID },
        Column_1: col1,
        Column_2: col2,
        Operation: 'Power and Root Functions',
        Sub_Op: 'Power',
        Column_name: cDict.Target_Column1,
        Additional_Colns: [],
        Other_Inputs: {
          Power: powerInput,
          previewString: previewString
        },
        D_cols: Dcols,
        table_name: tableName,
        current_table: currentTable
      }
    }
  } else if ((String(cDict.Operation) === 'Left Join') || (String(cDict.Operation) === 'Right Join') || (String(cDict.Operation) === 'Inner Join') || (String(cDict.Operation) === 'Outer Join')) {
    let colDisplayList = ''
    let joinType = ''
    let join1 = ''
    let join2 = ''
    let arrData1 = ''
    let arrData2 = ''

    if (String(cDict.Operation) === 'Left Join') {
      if (String(cDict.Left_join_Data13.length) !== 0 && String(cDict.Left_join_Data24.length) !== 0 && String(cDict.Left_join_on_Data11) !== '' && String(cDict.Left_join_on_Data22) !== '') {
        joinType = 'left'
        colDisplayList = [cDict.Left_join_Data13, cDict.Left_join_Data24]
        join1 = cDict.Left_join_on_Data11
        join2 = cDict.Left_join_on_Data22
        arrData1 = cDict.Left_join_Data13
        arrData2 = cDict.Left_join_Data24
        previewString = 'Left Join Data1 on ' + cDict.Left_join_on_Data11 + ' Data2 on ' + cDict.Left_join_on_Data22
      }
    } else if (String(cDict.Operation) === 'Right Join') {
      if (String(cDict.Right_join_Data13.length) !== 0 && String(cDict.Right_join_Data24.length) !== 0 && String(cDict.Right_join_on_Data22) !== '' && String(cDict.Right_join_on_Data11) !== '') {
        joinType = 'right'
        colDisplayList = [cDict.Right_join_Data13, cDict.Right_join_Data24]
        join1 = cDict.Right_join_on_Data11
        join2 = cDict.Right_join_on_Data22
        arrData1 = cDict.Right_join_Data13
        arrData2 = cDict.Right_join_Data24
        previewString = 'Right Join Data1 on ' + cDict.Right_join_on_Data11 + ' Data2 on ' + cDict.Right_join_on_Data22
      }
    } else if (String(cDict.Operation) === 'Inner Join') {
      if (String(cDict.Inner_join_Data13.length) !== 0 && String(cDict.Inner_join_Data24.length) !== 0 && String(cDict.Inner_join_on_Data11) !== '' && String(cDict.Inner_join_on_Data22) !== '') {
        joinType = 'inner'
        colDisplayList = [cDict.Inner_join_Data13, cDict.Inner_join_Data24]
        join1 = cDict.Inner_join_on_Data11
        join2 = cDict.Inner_join_on_Data22
        arrData1 = cDict.Inner_join_Data13
        arrData2 = cDict.Inner_join_Data24
        previewString = 'Inner Join Data1 on ' + cDict.Inner_join_on_Data22 + ' Data2 on ' + cDict.Inner_join_on_Data11
      }
    } else {
      if (String(cDict.Outer_join_Data13.length) !== 0 && String(cDict.Outer_join_Data24.length) !== 0 && String(cDict.Outer_join_on_Data11) !== '' && String(cDict.Outer_join_on_Data22) !== '') {
        joinType = 'outer'
        colDisplayList = [cDict.Outer_join_Data13, cDict.Outer_join_Data24]
        join1 = cDict.Outer_join_on_Data11
        join2 = cDict.Outer_join_on_Data22
        arrData1 = cDict.Outer_join_Data13
        arrData2 = cDict.Outer_join_Data24
        previewString = 'Outer Join Data1 on ' + cDict.Outer_join_on_Data22 + ' Data2 on ' + cDict.Outer_join_on_Data11
      }
    }

    configDict = {
      function: 'Merge and Join',
      element_name: "merge",
      inputs: {
        data: {
          Data1: cDict.table_data[0],
          Data2: cDict.table_data[1]
        },
        final_config: {
          merge_and_join: {
            function: 'Merge and Join',
            inputs: {
              data: {
                Data1: cDict.table_data[0],
                Data2: cDict.table_data[1]
              },
              option: 'join',
              Col_show: '',
              col_display_list: colDisplayList,
              table_name: tableName,
              current_table: currentTable,
              join_config: {
                join_type: joinType,
                previewString: previewString,
                on: {
                  Data1: join1,
                  Data2: join2
                },
                on_display: {
                  Data1: arrData1,
                  Data2: arrData2
                }
              }
            },
            newly_created: currTable
          },
          groupby: '',
          conditional_merge: '',
          sortby: ''
        }
      },
      outputs: {
        name: '',
        save: {
          source: '',
          table: ''
        }
      }
    }
  } else if ((String(cDict.Operation) === 'Append and Concatenate')) {
    if ($('.Target_Column1').val() == 'append') {
      previewString = "Table Appended"
    }
    else if ($('.Target_Column1').val() == 'concatenate') {
      previewString = "Table Concatenated"
    }
    configDict = {
      function: 'Merge and Join',
      element_name: "append",
      inputs: {
        data: {
          Data1: cDict.table_data[0],
          Data2: cDict.table_data[1]
        },
        final_config: {
          merge_and_join: {
            function: 'Merge and Join',
            inputs: {
              data: {
                Data1: cDict.table_data[0],
                Data2: cDict.table_data[1]
              },
              option: $('.Target_Column1').val(),
              previewString: previewString,
              table_name: tableName,
              current_table: currentTable,

            },
            newly_created: currTable
          },
          groupby: '',
          conditional_merge: '',
          sortby: ''
        }
      },
      outputs: {
        name: '',
        save: {
          source: '',
          table: ''
        }
      }
    }
  } else if (String(cDict.Operation) === 'Rename and Drop') {
    if (String(cDict.Drop_Columns1.length) !== '0') {
      for (let i = 0; i < cDict.Drop_Columns1.length; i++) {
        if (String(i) === '0') {
          previewString = 'Drop Columns ' + cDict.Drop_Columns1[i]
        } else {
          previewString = previewString + ', ' + cDict.Drop_Columns1[i]
        }
      }
    }

    const renameConfig1 = {}
    $('#renameColumnContainer1').find('.renameColumnGroup1').each(function () {
      const currentColName1 = $(this).find('.col-10').find('label').text()
      const newColName1 = $(this).find('.col-10').find('input').val()
      renameConfig1[currentColName1] = newColName1
    })

    if (Object.keys(renameConfig1).length > 0) {
      if (String(previewString) !== '') {
        previewString = previewString + ' and '
      }
      for (const [key, value] of Object.entries(renameConfig1)) {
        previewString = previewString + 'Rename column ' + key + ' to ' + value
      }
    }

    configDict = {
      function: 'Rename Column',
      inputs: {
        Data: [tableEleID],
        rename_config: renameConfig1,
        drop_column: cDict.Drop_Columns1,
        previewString: previewString
      },
      outputs: {
        save: {
          source: '',
          table: ''
        }
      }
    }
  } else if (String(cDict.Operation) === 'Filter') {

    let modelName = ""
    if(compValProcess){
      modelName = compValProcessName
    }else{
      modelName = $('#EBDisplayButtonID').attr('data-name')
    }
    if (typeof (modelName) === 'undefined') {
      modelName = $('#FileName').attr('data-experimentName')
    }
    let selID = ""

    if (parseInt(ind) === 0) {
      let a = $('#dataElementParent').find('div').find('div')
      try {
        selID = a[parseInt(ind)].getAttribute('data-element_id')
      } catch (err) {
        let b = $('.ebFunctions').find('div').find('a')
        selID = b[parseInt(ind - 1)].getAttribute('data-element_id')
      }
    } else {
      let a = $('.ebFunctions').find('div').find('a')
      selID = a[parseInt(ind - 1)].getAttribute('data-element_id')
    }

    let parentElementId = { "Data1": selID }
    let tableDetailsMerge = ""
    let table2 = ($('#filter-table_where_merge1'));
    let whereConditionListMerge = [];
    table2.find('tr').each(function (i, el) {
      if ($(this).find("select").length > 2) {
        tableDetailsMerge = {
          column_name: ($(this).find('select').attr("name")),
          condition: ($(this).find("select").eq(0).val() + " " + $(this).find("select").eq(2).val()).trim(),
          globalVariable: $(this).find("select").eq(1).val(),
        }
        if ($(this).find('input').attr("type") == "number") {
          tableDetailsMerge['input_value'] = Number($(this).find('input').val());
        } else {
          tableDetailsMerge['input_value'] = $(this).find('input').val();
        }
      } else {
        tableDetailsMerge = {
          column_name: ($(this).find('select').eq(0).attr("name")),
          condition: $(this).find("select").eq(0).val(),
          globalVariable: $(this).find("select").eq(1).val(),
        }
        if ($(this).find('input').attr("type") == "number") {
          tableDetailsMerge['input_value'] = Number($(this).find('input').val());
        } else {
          tableDetailsMerge['input_value'] = $(this).find('input').val();
        }
      }
      whereConditionListMerge.push(tableDetailsMerge);
    });

    previewString = 'Filter Data ......'
    configDictMergeGroup = {
      'function': 'Merge and Join',
      'inputs': {
        'data': parentElementId,
        'req_data': selID,
        'option': "where",
        'previewString': previewString,
        'option_config': {
          condition: whereConditionListMerge,
        }
      },
    }

    configDict = {
      function: 'Merge and Join',
      element_name: "filter",
      inputs: {
        data: {
          Data1: selID
        },
        final_config: {
          merge_and_join: "",
          groupby: configDictMergeGroup,
          conditional_merge: '',
          sortby: ''
        }
      },
      outputs: {
        name: '',
        save: {
          source: '',
          table: ''
        }
      }
    }


  } else if (String(cDict.Operation) === 'Add Time Periods') {

    if (String(cDict.Time_Periods1) !== '' && String(cDict.Days2) !== '') {
      previewString = cDict.Time_Periods1 + ' + ' + cDict.Days2 + ' Days'
    }

    if (String(cDict.Time_Periods1) !== '' && String(cDict.Months3) !== '') {
      previewString = cDict.Time_Periods1 + ' + ' + cDict.Months3 + ' Months'
    }

    if (String(cDict.Time_Periods1) !== '' && String(cDict.Years4) !== '') {
      previewString = cDict.Time_Periods1 + ' + ' + cDict.Years4 + ' Years'
    }

    configDict = {
      function: 'Add Time Periods',
      inputs: {
        data: tableEleID,
        Column_1: cDict.Time_Periods1,
        Column_name: cDict.Target_Column1,
        Days: cDict.Days2,
        Months: cDict.Months3,
        Years: cDict.Years4,
        previewString: previewString,
        table_name: tableName,
        current_table: currentTable,
      }
    }
  } else if (String(cDict.Operation) === 'Groupby') {
    let modelName = ""
    if(compValProcess){
      modelName = compValProcessName
    }else{
      modelName = $('#EBDisplayButtonID').attr('data-name')
    }
    if (typeof (modelName) === 'undefined') {
      modelName = $('#FileName').attr('data-experimentName')
    }
    let selID = ""
    if (parseInt(ind) === 0) {
      let a = $('#dataElementParent').find('div').find('div')
      try {
        selID = a[parseInt(ind)].getAttribute('data-element_id')
      } catch (err) {
        let b = $('.ebFunctions').find('div').find('a')
        selID = b[parseInt(ind - 1)].getAttribute('data-element_id')
      }
    } else {
      let a = $('.ebFunctions').find('div').find('a')
      selID = a[parseInt(ind - 1)].getAttribute('data-element_id')
    }
    previewString = "Group by column :"
    let parentElementId = { "Data1": selID }
    let groupColList = []
    let groupAggFields = {}
    groupColList = $('.Target_Column1').val()
    for (i in groupColList) {
      previewString += " " + groupColList[i] + ","
    }
    let list2 = ($('#selectedGroupAggList'));
    list2.find("div.row").each(function (i, el) {
      let field_name = ($(this).find('button').val());
      let aggfunc = ($(this).find('select').val());
      groupAggFields[field_name] = aggfunc;


    });
    previewString = previewString.substr(0, previewString.length - 1)

    configDictMergeGroup = {
      'function': 'Merge and Join',
      'inputs': {
        'data': parentElementId,
        'req_data': selID,
        'option': "group",
        'previewString': previewString,
        'option_config': {
          "group_by": groupColList,
          aggregate_func: groupAggFields,
        }
      },
    }
    configDict = {
      function: 'Merge and Join',
      element_name: 'groupby',
      inputs: {
        data: {
          Data1: selID
        },
        final_config: {
          merge_and_join: "",
          groupby: configDictMergeGroup,
          conditional_merge: '',
          sortby: ''
        }
      },
      outputs: {
        name: '',
        save: {
          source: '',
          table: ''
        }
      }
    }
  } else if (String(cDict.Operation) === 'Sort') {
    let modelName = ""
    if(compValProcess){
      modelName = compValProcessName
    }else{
      modelName = $('#EBDisplayButtonID').attr('data-name')
    }
    if (typeof (modelName) === 'undefined') {
      modelName = $('#FileName').attr('data-experimentName')
    }
    let selID = ""
    if (parseInt(ind) === 0) {
      let a = $('#dataElementParent').find('div').find('div')
      try {
        selID = a[parseInt(ind)].getAttribute('data-element_id')
      } catch (err) {
        let b = $('.ebFunctions').find('div').find('a')
        selID = b[parseInt(ind - 1)].getAttribute('data-element_id')
      }
    } else {
      let a = $('.ebFunctions').find('div').find('a')
      selID = a[parseInt(ind - 1)].getAttribute('data-element_id')
    }
    previewString = "Sort by column :"
    let parentElementId = { "Data1": selID }
    let sortTypeFields = {}
    let list2 = ($('#selectedSortColList'));
    list2.find("div.row").each(function (i, el) {
      let field_name = ($(this).find('button').val());
      let sort_type = ($(this).find('select').val());
      sortTypeFields[field_name] = sort_type;
      previewString += " " + field_name + ","
    });

    previewString = previewString.substring(0, previewString.length - 1);

    configDictMergeGroup = {
      'function': 'Merge and Join',
      'inputs': {
        'data': parentElementId,
        'option': "",
        'option_config': "",
        'previewString': previewString
      },
      "sort": sortTypeFields,
    }
    configDict = {
      function: 'Merge and Join',
      element_name: "sort",
      inputs: {
        data: {
          Data1: selID
        },
        final_config: {
          merge_and_join: "",
          groupby: "",
          conditional_merge: "",
          sortby: configDictMergeGroup
        }
      },
      outputs: {
        name: '',
        save: {
          source: '',
          table: ''
        }
      }
    }
  } else if (String(cDict.Operation) === 'Concat Columns') {
    if (String(cDict.Target_Column2.length) !== '0') {
      for (let i = 0; i < cDict.Target_Column2.length; i++) {
        if (String(i) === '0') {
          previewString = cDict.Target_Column2[i]
        } else {
          previewString = previewString + '+' + cDict.Target_Column2[i]
        }
      }
    }

    configDict = {
      function: 'Concat Columns',
      inputs: {
        data: tableEleID,
        Column_1: cDict.Target_Column2,
        Column_name: cDict.Target_Column1,
        Separator: cDict.Target_Column3,
        previewString: previewString,
        table_name: tableName,
        current_table: currentTable,
      }
    }
  } else if (String(cDict.Operation) === 'Data Utilities') {

    let modelName = ""
    if(compValProcess){
      modelName = compValProcessName
    }else{
      modelName = $('#EBDisplayButtonID').attr('data-name')
    }
    if (typeof (modelName) === 'undefined') {
      modelName = $('#FileName').attr('data-experimentName')
    }
    let selID = ""

    previewString = "Reset Index"

    if (parseInt(ind) === 0) {
      let a = $('#dataElementParent').find('div').find('div')
      try {
        selID = a[parseInt(ind)].getAttribute('data-element_id')
      } catch (err) {
        let b = $('.ebFunctions').find('div').find('a')
        selID = b[parseInt(ind - 1)].getAttribute('data-element_id')
      }
    } else {
      let a = $('.ebFunctions').find('div').find('a')
      selID = a[parseInt(ind - 1)].getAttribute('data-element_id')
    }

    if (cDict.Reset_Index1 == "true") {
      reset_checked = true
    } else {
      reset_checked = false
    }

    if (cDict.Drop_Index2 == "true") {
      drop_checked = true
    } else {
      drop_checked = false
    }

    configDict = {
      'function': 'Data Utilities',
      'inputs': {
        'Data': [selID],
        "element_name": "",
        "reset_checked": reset_checked,
        "drop_checked": drop_checked,
        "previewString": previewString,
      }
    };
  } else if (String(cDict.Operation) === 'Add Column') {

    let modelName = ""
    if(compValProcess){
      modelName = compValProcessName
    }else{
      modelName = $('#EBDisplayButtonID').attr('data-name')
    }
    if (typeof (modelName) === 'undefined') {
      modelName = $('#FileName').attr('data-experimentName')
    }
    let selID = ""
    if (parseInt(ind) === 0) {
      let a = $('#dataElementParent').find('div').find('div')
      try {
        selID = a[parseInt(ind)].getAttribute('data-element_id')
      } catch (err) {
        let b = $('.ebFunctions').find('div').find('a')
        selID = b[parseInt(ind - 1)].getAttribute('data-element_id')
      }
    } else {
      let a = $('.ebFunctions').find('div').find('a')
      selID = a[parseInt(ind - 1)].getAttribute('data-element_id')
    }

    let parentElementId = { "Data1": selID }
    AddColConditionList = {}
    var table2 = ($('#filter-table_addCol_body'));
    var newColName = $('.Target_Column1').val();
    var add_type = $(".Target_Column3").val();
    var field_type = $(".Target_Column2").val();
    var conditionList = new Array();
    table2.find('tr').each(function (i, el) {
      var table_details = {
        column_name: ($(this).find('select').attr("name")),
        condition: ($(this).find("select").eq(0).val()).trim(),
        globalVariable: $(this).find("select").eq(1).val(),
        repr_value: { repr_value: "", global_var: "" }
      }
      if (table_details["globalVariable"] == null) {
        table_details["globalVariable"] = ""
      }
      if ($(this).find('input').eq(0).attr("type") == "number") {
        table_details['condition_value'] = Number($(this).find('input').eq(0).val());
      } else {
        table_details['condition_value'] = $(this).find('input').eq(0).val();
      }
      if (add_type == "static_add") {
        table_details['repr_value']['repr_value'] = $(this).find('input').eq(1).val();
        table_details['repr_value']['global_var'] = $(this).find('select[data-dropdown_purpose="select_global_variable_input"]').eq(0).val();
      }
      else {
        table_details['repr_value']['repr_value'] = $(this).find("select").eq(2).val();
      }
      conditionList.push(table_details);
    });
    AddColConditionList['new_column_name'] = newColName;
    AddColConditionList['condition'] = conditionList;
    AddColConditionList['add_type'] = add_type;
    if (field_type) {
      AddColConditionList['field_type'] = field_type
    }
    previewString = "Added Column : " + cDict.Target_Column1
    configDictMergeGroup = {
      'function': 'Merge and Join',
      'inputs': {
        'data': parentElementId,
        'req_data': selID,
        'previewString': previewString,
        'option': "addCondColumn",
        'option_config': {
          condition: AddColConditionList,
        }
      },
    }
    configDict = {
      function: 'Merge and Join',
      element_name: 'AddColumn',
      inputs: {
        data: {
          Data1: selID
        },
        final_config: {
          merge_and_join: "",
          groupby: configDictMergeGroup,
          conditional_merge: '',
          sortby: ''
        }
      },
      outputs: {
        name: '',
        save: {
          source: '',
          table: ''
        }
      }
    }
  } else if (String(cDict.Operation) === 'Pivot') {
    let modelName = ""
    if(compValProcess){
      modelName = compValProcessName
    }else{
      modelName = $('#EBDisplayButtonID').attr('data-name')
    }
    if (typeof (modelName) === 'undefined') {
      modelName = $('#FileName').attr('data-experimentName')
    }
    let selID = ""
    if (parseInt(ind) === 0) {
      let a = $('#dataElementParent').find('div').find('div')
      try {
        selID = a[parseInt(ind)].getAttribute('data-element_id')
      } catch (err) {
        let b = $('.ebFunctions').find('div').find('a')
        selID = b[parseInt(ind - 1)].getAttribute('data-element_id')
      }
    } else {
      let a = $('.ebFunctions').find('div').find('a')
      selID = a[parseInt(ind - 1)].getAttribute('data-element_id')
    }
    let parentElementId = { "Data1": selID }
    let columns = $(".Target_Column2").val()
    previewString = "Pivot on :"
    for (i in columns) {
      previewString += " " + columns[i] + ","
    }
    previewString = previewString.substr(0, previewString.length - 1)
    configDict = {
      'function': 'Pivot and Transpose',
      'element_name': 'pivot',
      'inputs': {
        'data': parentElementId,
        'option': "pivot",
        'previewString': previewString,
        'option_config': {
          'index': $(".Target_Column1").val(),
          'columns': $(".Target_Column2").val(),
          'values': $(".Target_Column3").val()
        }
      }
    }

  } else if (String(cDict.Operation) === 'Unpivot') {

    let modelName = ""
    if(compValProcess){
      modelName = compValProcessName
    }else{
      modelName = $('#EBDisplayButtonID').attr('data-name')
    }
    if (typeof (modelName) === 'undefined') {
      modelName = $('#FileName').attr('data-experimentName')
    }
    let selID = ""
    if (parseInt(ind) === 0) {
      let a = $('#dataElementParent').find('div').find('div')
      try {
        selID = a[parseInt(ind)].getAttribute('data-element_id')
      } catch (err) {
        let b = $('.ebFunctions').find('div').find('a')
        selID = b[parseInt(ind - 1)].getAttribute('data-element_id')
      }
    } else {
      let a = $('.ebFunctions').find('div').find('a')
      selID = a[parseInt(ind - 1)].getAttribute('data-element_id')
    }

    let parentElementId = { "Data1": selID }
    let columns = $(".Target_Column2").val()
    previewString = "Unpivot on :"
    for (i in columns) {
      previewString += " " + columns[i] + ","
    }
    previewString = previewString.substr(0, previewString.length - 1)


    configDict = {
      'function': 'Pivot and Transpose',
      'element_name': 'unpivot',
      'inputs': {
        'data': parentElementId,
        'option': 'melt',
        'previewString': previewString,
        'option_config': {
          'index': $(".Target_Column1").val(),
          'columns': $(".Target_Column2").val(),
          'variable_column_name': $(".Target_Column3").val(),
          'value_column_name': $(".Target_Column4").val()
        }
      }
    }
  } else if(String(cDict.Operation) === 'Fill Missing Values'){

    let modelName = ""
    if(compValProcess){
      modelName = compValProcessName
    }else{
      modelName = $('#EBDisplayButtonID').attr('data-name')
    }
    if (typeof (modelName) === 'undefined') {
      modelName = $('#FileName').attr('data-experimentName')
    }
    let selID = ""

    previewString = "Fill Missing Values"

    if (parseInt(ind) === 0) {
      let a = $('#dataElementParent').find('div').find('div')
      try {
         selID = a[parseInt(ind)].getAttribute('data-element_id')
      } catch (err) {
        let b = $('.ebFunctions').find('div').find('a')
         selID = b[parseInt(ind - 1)].getAttribute('data-element_id')
      }
    } else {
      let a = $('.ebFunctions').find('div').find('a')
       selID = a[parseInt(ind - 1)].getAttribute('data-element_id')
    }
    var subOpConfig = "";
    if ($('.Select_Operation1').val() == 'custom') {
        var subOpConfig = $('.Custom_value3').val();
    }
     configDict={
      'function':'Missing Values',
      'inputs':{
          "element_name":"",
          'data':{"Data1":selID},
          'Sub_Op':$('.Select_Operation1').val(),
          'Other_Inputs':{
              'Data': $('.Data_Table2').val(),
              'subOpConfig': subOpConfig,
          },
          "previewString":previewString,
      }
  };
} else if(String(cDict.Operation) === 'Sum Product') {

  let modelName = ""
  if(compValProcess){
    modelName = compValProcessName
  }else{
    modelName = $('#EBDisplayButtonID').attr('data-name')
  }
  if (typeof (modelName) === 'undefined') {
    modelName = $('#FileName').attr('data-experimentName')
  }
  let selID = ""
  previewString = "Sum Product"
  if (parseInt(ind) === 0) {
    let a = $('#dataElementParent').find('div').find('div')
    try {
       selID = a[parseInt(ind)].getAttribute('data-element_id')
    } catch (err) {
      let b = $('.ebFunctions').find('div').find('a')
       selID = b[parseInt(ind - 1)].getAttribute('data-element_id')
    }
  } else {
    let a = $('.ebFunctions').find('div').find('a')
     selID = a[parseInt(ind - 1)].getAttribute('data-element_id')
  }
   configDict={
    "function":"Elementary Statistics",
    "inputs":{
    "element_name":"",
    "data":{"Data1":selID},
    "previewString":previewString,
    "Type":"Basic Aggregates",
    "Groupby_column":$('.Column_Group1').val(),
    "agg_config":[
    {"Value_column":$('.Column_Value2').val(),
    "Sum_product_column":$('.Column_Value2').val(),
    "Aggregate":"Sum Product",
    "new_column_name":$('.Column_Name3').val(),
    "Weights":"",
    "Conditional":{},
   }]
  }
};

} else if(String(cDict.Operation) === 'Weighted Average'){

  let modelName = ""
  if(compValProcess){
    modelName = compValProcessName
  }else{
    modelName = $('#EBDisplayButtonID').attr('data-name')
  }
  if (typeof (modelName) === 'undefined') {
    modelName = $('#FileName').attr('data-experimentName')
  }
  let selID = ""

  previewString = "Weighted Average"

  if (parseInt(ind) === 0) {
    let a = $('#dataElementParent').find('div').find('div')
    try {
       selID = a[parseInt(ind)].getAttribute('data-element_id')
    } catch (err) {
      let b = $('.ebFunctions').find('div').find('a')
       selID = b[parseInt(ind - 1)].getAttribute('data-element_id')
    }
  } else {
    let a = $('.ebFunctions').find('div').find('a')
     selID = a[parseInt(ind - 1)].getAttribute('data-element_id')
  }
   configDict={
    'function':'Elementary Statistics',
    'inputs':{
        "element_name":"",
        'data':{"Data1":selID},
        "previewString":previewString,
        'Type':"Basic Aggregates",
        "Groupby_column":$('.Column_Group1').val(),
        "agg_config":[
        {"Value_column":$('.Average_Value2').val(),
        "Weights":$('.Average_Weight3').val(),
        "Sum_product_column":[],
        "Aggregate":"Weighted Average",
        "new_column_name":$('.Column_Name4').val(),
        "Conditional":{},
      }]
    }
};
} else if(String(cDict.Operation) === 'Drop Duplicate'){

  let modelName = ""
  if(compValProcess){
    modelName = compValProcessName
  }else{
    modelName = $('#EBDisplayButtonID').attr('data-name')
  }
  if (typeof (modelName) === 'undefined') {
    modelName = $('#FileName').attr('data-experimentName')
  }
  let selID = ""

  previewString = "Drop Duplicate"

  if (parseInt(ind) === 0) {
    let a = $('#dataElementParent').find('div').find('div')
    try {
       selID = a[parseInt(ind)].getAttribute('data-element_id')
    } catch (err) {
      let b = $('.ebFunctions').find('div').find('a')
       selID = b[parseInt(ind - 1)].getAttribute('data-element_id')
    }
  } else {
    let a = $('.ebFunctions').find('div').find('a')
     selID = a[parseInt(ind - 1)].getAttribute('data-element_id')
  }

   configDict={
    'function':'Drop Duplicate',
    "inputs":{
    "element_name":"",
    'data':{"Data1":selID},
    'Sub_Op': $('.Select_operation1').val(),
     "Other_Inputs":{
       'Data': $('.Data_table2').val(),
     },
     "previewString":previewString,
    }
};
} else if(String(cDict.Operation) === 'Add Fix Column'){
  let modelName = ""
  if(compValProcess){
    modelName = compValProcessName
  }else{
    modelName = $('#EBDisplayButtonID').attr('data-name')
  }
  if (typeof (modelName) === 'undefined') {
    modelName = $('#FileName').attr('data-experimentName')
  }
  let selID = ""

  if (parseInt(ind) === 0) {
    let a = $('#dataElementParent').find('div').find('div')
    try {
       selID = a[parseInt(ind)].getAttribute('data-element_id')
    } catch (err) {
      let b = $('.ebFunctions').find('div').find('a')
       selID = b[parseInt(ind - 1)].getAttribute('data-element_id')
    }
  } else {
    let a = $('.ebFunctions').find('div').find('a')
     selID = a[parseInt(ind - 1)].getAttribute('data-element_id')
  }

  previewString = "Added Column "+cDict.Input_Column2
   configDict={
    'function':'Add Fix Column',
    'inputs':{
        'Data':[selID],
        "input_name": cDict.Input_Column2,
        "input_value" : cDict.Add_Column2,
        "element_name":"",
        "previewString":previewString,
    }
  }
} else if(String(cDict.Operation) === 'Delimit Column'){
  let modelName = ""
  if(compValProcess){
    modelName = compValProcessName
  }else{
    modelName = $('#EBDisplayButtonID').attr('data-name')
  }
  if (typeof (modelName) === 'undefined') {
    modelName = $('#FileName').attr('data-experimentName')
  }
  let selID = ""

  if (parseInt(ind) === 0) {
    let a = $('#dataElementParent').find('div').find('div')
    try {
       selID = a[parseInt(ind)].getAttribute('data-element_id')
    } catch (err) {
      let b = $('.ebFunctions').find('div').find('a')
       selID = b[parseInt(ind - 1)].getAttribute('data-element_id')
    }
  } else {
    let a = $('.ebFunctions').find('div').find('a')
     selID = a[parseInt(ind - 1)].getAttribute('data-element_id')
  }

  previewString = "Delimit Column Values"
   configDict={
    'function':'Delimit Column',
    'inputs':{
        'data':{"Data1":selID},
        "columnName": cDict.Delimit_Column1,
        "delimiter" : cDict.Delimit_Column2,
        "previewString":previewString,
    }
  }
} else if(String(cDict.Operation) === 'Find and Replace'){
  let modelName = ""
  if(compValProcess){
    modelName = compValProcessName
  }else{
    modelName = $('#EBDisplayButtonID').attr('data-name')
  }
  if (typeof (modelName) === 'undefined') {
    modelName = $('#FileName').attr('data-experimentName')
  }
  let selID = ""

  if (parseInt(ind) === 0) {
    let a = $('#dataElementParent').find('div').find('div')
    try {
       selID = a[parseInt(ind)].getAttribute('data-element_id')
    } catch (err) {
      let b = $('.ebFunctions').find('div').find('a')
       selID = b[parseInt(ind - 1)].getAttribute('data-element_id')
    }
  } else {
    let a = $('.ebFunctions').find('div').find('a')
     selID = a[parseInt(ind - 1)].getAttribute('data-element_id')
  }

  previewString = "Find and replace values"
  var fdict = {
    "find": cDict.Find_and_Replace4,
    "replace": cDict.Find_and_Replace5,
    "find_case": cDict.Find_and_Replace3,
    "columnName": cDict.Find_and_Replace1,
    "replacecolumnName": cDict.Find_and_Replace2,
    }
   configDict={
    'function':'Find and Replace',
    'inputs':{
        'data':{"Data1":selID},
        "fdict": fdict,
        "previewString":previewString,
    }
  }
} else if(String(cDict.Operation) === 'Date'){
  let modelName = ""
  if(compValProcess){
    modelName = compValProcessName
  }else{
    modelName = $('#EBDisplayButtonID').attr('data-name')
  }
  if (typeof (modelName) === 'undefined') {
    modelName = $('#FileName').attr('data-experimentName')
  }
  let selID = ""

  if (parseInt(ind) === 0) {
    let a = $('#dataElementParent').find('div').find('div')
    try {
       selID = a[parseInt(ind)].getAttribute('data-element_id')
    } catch (err) {
      let b = $('.ebFunctions').find('div').find('a')
       selID = b[parseInt(ind - 1)].getAttribute('data-element_id')
    }
  } else {
    let a = $('.ebFunctions').find('div').find('a')
     selID = a[parseInt(ind - 1)].getAttribute('data-element_id')
  }

  previewString = "Added new Date"
   configDict={
    'function':'Date',
    'inputs':{
        'data':{"Data1":selID},
        "year": cDict.Date1,
        "month" : cDict.Date2,
        "day": cDict.Date3,
        "colname": cDict.Date4,
        "previewString":previewString,
    }
  }
} else if(String(cDict.Operation) === 'Day'){
  let modelName = ""
  if(compValProcess){
    modelName = compValProcessName
  }else{
    modelName = $('#EBDisplayButtonID').attr('data-name')
  }
  if (typeof (modelName) === 'undefined') {
    modelName = $('#FileName').attr('data-experimentName')
  }
  let selID = ""

  if (parseInt(ind) === 0) {
    let a = $('#dataElementParent').find('div').find('div')
    try {
       selID = a[parseInt(ind)].getAttribute('data-element_id')
    } catch (err) {
      let b = $('.ebFunctions').find('div').find('a')
       selID = b[parseInt(ind - 1)].getAttribute('data-element_id')
    }
  } else {
    let a = $('.ebFunctions').find('div').find('a')
     selID = a[parseInt(ind - 1)].getAttribute('data-element_id')
  }

  previewString = "Extracted day from date"
   configDict={
    'function':'Day',
    'inputs':{
        'data':{"Data1":selID},
        "date": cDict.Day1,
        "colname": cDict.Day2,
        "previewString":previewString,
    }
  }
} else if(String(cDict.Operation) === 'Days'){
  let modelName = ""
  if(compValProcess){
    modelName = compValProcessName
  }else{
    modelName = $('#EBDisplayButtonID').attr('data-name')
  }
  if (typeof (modelName) === 'undefined') {
    modelName = $('#FileName').attr('data-experimentName')
  }
  let selID = ""

  if (parseInt(ind) === 0) {
    let a = $('#dataElementParent').find('div').find('div')
    try {
       selID = a[parseInt(ind)].getAttribute('data-element_id')
    } catch (err) {
      let b = $('.ebFunctions').find('div').find('a')
       selID = b[parseInt(ind - 1)].getAttribute('data-element_id')
    }
  } else {
    let a = $('.ebFunctions').find('div').find('a')
     selID = a[parseInt(ind - 1)].getAttribute('data-element_id')
  }

  previewString = "No of days between two dates"
   configDict={
    'function':'Days',
    'inputs':{
        'data':{"Data1":selID},
        "start_date": cDict.Days1,
        "end_date": cDict.Days2,
        "colname": cDict.Days3,
        "previewString":previewString,
    }
  }
} else if(String(cDict.Operation) === 'Edate'){
  let modelName = ""
  if(compValProcess){
    modelName = compValProcessName
  }else{
    modelName = $('#EBDisplayButtonID').attr('data-name')
  }
  if (typeof (modelName) === 'undefined') {
    modelName = $('#FileName').attr('data-experimentName')
  }
  let selID = ""

  if (parseInt(ind) === 0) {
    let a = $('#dataElementParent').find('div').find('div')
    try {
       selID = a[parseInt(ind)].getAttribute('data-element_id')
    } catch (err) {
      let b = $('.ebFunctions').find('div').find('a')
       selID = b[parseInt(ind - 1)].getAttribute('data-element_id')
    }
  } else {
    let a = $('.ebFunctions').find('div').find('a')
     selID = a[parseInt(ind - 1)].getAttribute('data-element_id')
  }

  previewString = "Edate"
   configDict={
    'function':'Edate',
    'inputs':{
        'data':{"Data1":selID},
        "start_date": cDict.Edate1,
        "months": cDict.Edate2,
        "colname": cDict.Edate3,
        "previewString":previewString,
    }
  }
} else if(String(cDict.Operation) === 'Days360'){
  let modelName = ""
  if(compValProcess){
    modelName = compValProcessName
  }else{
    modelName = $('#EBDisplayButtonID').attr('data-name')
  }
  if (typeof (modelName) === 'undefined') {
    modelName = $('#FileName').attr('data-experimentName')
  }
  let selID = ""

  if (parseInt(ind) === 0) {
    let a = $('#dataElementParent').find('div').find('div')
    try {
       selID = a[parseInt(ind)].getAttribute('data-element_id')
    } catch (err) {
      let b = $('.ebFunctions').find('div').find('a')
       selID = b[parseInt(ind - 1)].getAttribute('data-element_id')
    }
  } else {
    let a = $('.ebFunctions').find('div').find('a')
     selID = a[parseInt(ind - 1)].getAttribute('data-element_id')
  }

  previewString = "Days360"
   configDict={
    'function':'Days360',
    'inputs':{
        'data':{"Data1":selID},
        "start_date": cDict.Days3601,
        "end_date": cDict.Days3602,
        "method": cDict.Days3603,
        "colname": cDict.Days3604,
        "previewString":previewString,
    }
  }
} else if(String(cDict.Operation) === 'Eomonth'){
  let modelName = ""
  if(compValProcess){
    modelName = compValProcessName
  }else{
    modelName = $('#EBDisplayButtonID').attr('data-name')
  }
  if (typeof (modelName) === 'undefined') {
    modelName = $('#FileName').attr('data-experimentName')
  }
  let selID = ""

  if (parseInt(ind) === 0) {
    let a = $('#dataElementParent').find('div').find('div')
    try {
       selID = a[parseInt(ind)].getAttribute('data-element_id')
    } catch (err) {
      let b = $('.ebFunctions').find('div').find('a')
       selID = b[parseInt(ind - 1)].getAttribute('data-element_id')
    }
  } else {
    let a = $('.ebFunctions').find('div').find('a')
     selID = a[parseInt(ind - 1)].getAttribute('data-element_id')
  }

  previewString = "Eomonth"
   configDict={
    'function':'Eomonth',
    'inputs':{
        'data':{"Data1":selID},
        "start_date": cDict.Eomonth1,
        "months": cDict.Eomonth2,
        "colname": cDict.Eomonth3,
        "previewString":previewString,
    }
  }
} else if(String(cDict.Operation) === 'Hour'){
  let modelName = ""
  if(compValProcess){
    modelName = compValProcessName
  }else{
    modelName = $('#EBDisplayButtonID').attr('data-name')
  }
  if (typeof (modelName) === 'undefined') {
    modelName = $('#FileName').attr('data-experimentName')
  }
  let selID = ""

  if (parseInt(ind) === 0) {
    let a = $('#dataElementParent').find('div').find('div')
    try {
       selID = a[parseInt(ind)].getAttribute('data-element_id')
    } catch (err) {
      let b = $('.ebFunctions').find('div').find('a')
       selID = b[parseInt(ind - 1)].getAttribute('data-element_id')
    }
  } else {
    let a = $('.ebFunctions').find('div').find('a')
     selID = a[parseInt(ind - 1)].getAttribute('data-element_id')
  }

  previewString = "Hour"
   configDict={
    'function':'Hour',
    'inputs':{
        'data':{"Data1":selID},
        "date": cDict.Hour1,
        "colname": cDict.Hour2,
        "previewString":previewString,
    }
  }
} else if(String(cDict.Operation) === 'Isoweeknum'){
  let modelName = ""
  if(compValProcess){
    modelName = compValProcessName
  }else{
    modelName = $('#EBDisplayButtonID').attr('data-name')
  }
  if (typeof (modelName) === 'undefined') {
    modelName = $('#FileName').attr('data-experimentName')
  }
  let selID = ""

  if (parseInt(ind) === 0) {
    let a = $('#dataElementParent').find('div').find('div')
    try {
       selID = a[parseInt(ind)].getAttribute('data-element_id')
    } catch (err) {
      let b = $('.ebFunctions').find('div').find('a')
       selID = b[parseInt(ind - 1)].getAttribute('data-element_id')
    }
  } else {
    let a = $('.ebFunctions').find('div').find('a')
     selID = a[parseInt(ind - 1)].getAttribute('data-element_id')
  }

  previewString = "Isoweeknum"
   configDict={
    'function':'Isoweeknum',
    'inputs':{
        'data':{"Data1":selID},
        "date": cDict.Isoweeknum1,
        "colname": cDict.Isoweeknum2,
        "previewString":previewString,
    }
  }
} else if(String(cDict.Operation) === 'Minute'){
  let modelName = ""
  if(compValProcess){
    modelName = compValProcessName
  }else{
    modelName = $('#EBDisplayButtonID').attr('data-name')
  }
  if (typeof (modelName) === 'undefined') {
    modelName = $('#FileName').attr('data-experimentName')
  }
  let selID = ""

  if (parseInt(ind) === 0) {
    let a = $('#dataElementParent').find('div').find('div')
    try {
       selID = a[parseInt(ind)].getAttribute('data-element_id')
    } catch (err) {
      let b = $('.ebFunctions').find('div').find('a')
       selID = b[parseInt(ind - 1)].getAttribute('data-element_id')
    }
  } else {
    let a = $('.ebFunctions').find('div').find('a')
     selID = a[parseInt(ind - 1)].getAttribute('data-element_id')
  }

  previewString = "Minute"
   configDict={
    'function':'Minute',
    'inputs':{
        'data':{"Data1":selID},
        "date": cDict.Minute1,
        "colname": cDict.Minute2,
        "previewString":previewString,
    }
  }
} else if(String(cDict.Operation) === 'Month'){
  let modelName = ""
  if(compValProcess){
    modelName = compValProcessName
  }else{
    modelName = $('#EBDisplayButtonID').attr('data-name')
  }
  if (typeof (modelName) === 'undefined') {
    modelName = $('#FileName').attr('data-experimentName')
  }
  let selID = ""

  if (parseInt(ind) === 0) {
    let a = $('#dataElementParent').find('div').find('div')
    try {
       selID = a[parseInt(ind)].getAttribute('data-element_id')
    } catch (err) {
      let b = $('.ebFunctions').find('div').find('a')
       selID = b[parseInt(ind - 1)].getAttribute('data-element_id')
    }
  } else {
    let a = $('.ebFunctions').find('div').find('a')
     selID = a[parseInt(ind - 1)].getAttribute('data-element_id')
  }

  previewString = "Month"
   configDict={
    'function':'Month',
    'inputs':{
        'data':{"Data1":selID},
        "date": cDict.Month1,
        "colname": cDict.Month2,
        "previewString":previewString,
    }
  }
} else if(String(cDict.Operation) === 'Now'){
  let modelName = ""
  if(compValProcess){
    modelName = compValProcessName
  }else{
    modelName = $('#EBDisplayButtonID').attr('data-name')
  }
  if (typeof (modelName) === 'undefined') {
    modelName = $('#FileName').attr('data-experimentName')
  }
  let selID = ""

  if (parseInt(ind) === 0) {
    let a = $('#dataElementParent').find('div').find('div')
    try {
       selID = a[parseInt(ind)].getAttribute('data-element_id')
    } catch (err) {
      let b = $('.ebFunctions').find('div').find('a')
       selID = b[parseInt(ind - 1)].getAttribute('data-element_id')
    }
  } else {
    let a = $('.ebFunctions').find('div').find('a')
     selID = a[parseInt(ind - 1)].getAttribute('data-element_id')
  }

  previewString = "Now"
   configDict={
    'function':'Now',
    'inputs':{
        'data':{"Data1":selID},
        "colname": cDict.Now1,
        "previewString":previewString,
    }
  }
} else if(String(cDict.Operation) === 'Second'){
  let modelName = ""
  if(compValProcess){
    modelName = compValProcessName
  }else{
    modelName = $('#EBDisplayButtonID').attr('data-name')
  }
  if (typeof (modelName) === 'undefined') {
    modelName = $('#FileName').attr('data-experimentName')
  }
  let selID = ""

  if (parseInt(ind) === 0) {
    let a = $('#dataElementParent').find('div').find('div')
    try {
       selID = a[parseInt(ind)].getAttribute('data-element_id')
    } catch (err) {
      let b = $('.ebFunctions').find('div').find('a')
       selID = b[parseInt(ind - 1)].getAttribute('data-element_id')
    }
  } else {
    let a = $('.ebFunctions').find('div').find('a')
     selID = a[parseInt(ind - 1)].getAttribute('data-element_id')
  }

  previewString = "Second"
   configDict={
    'function':'Second',
    'inputs':{
        'data':{"Data1":selID},
        "date": cDict.Second1,
        "colname": cDict.Second2,
        "previewString":previewString,
    }
  }
} else if(String(cDict.Operation) === 'Time'){
  let modelName = ""
  if(compValProcess){
    modelName = compValProcessName
  }else{
    modelName = $('#EBDisplayButtonID').attr('data-name')
  }
  if (typeof (modelName) === 'undefined') {
    modelName = $('#FileName').attr('data-experimentName')
  }
  let selID = ""

  if (parseInt(ind) === 0) {
    let a = $('#dataElementParent').find('div').find('div')
    try {
       selID = a[parseInt(ind)].getAttribute('data-element_id')
    } catch (err) {
      let b = $('.ebFunctions').find('div').find('a')
       selID = b[parseInt(ind - 1)].getAttribute('data-element_id')
    }
  } else {
    let a = $('.ebFunctions').find('div').find('a')
     selID = a[parseInt(ind - 1)].getAttribute('data-element_id')
  }

  previewString = "Time"
   configDict={
    'function':'Time',
    'inputs':{
        'data':{"Data1":selID},
        "hour": cDict.Time1,
        "minute" : cDict.Time2,
        "second": cDict.Time3,
        "colname": cDict.Time4,
        "previewString":previewString,
    }
  }
} else if(String(cDict.Operation) === 'Today'){
  let modelName = ""
  if(compValProcess){
    modelName = compValProcessName
  }else{
    modelName = $('#EBDisplayButtonID').attr('data-name')
  }
  if (typeof (modelName) === 'undefined') {
    modelName = $('#FileName').attr('data-experimentName')
  }
  let selID = ""

  if (parseInt(ind) === 0) {
    let a = $('#dataElementParent').find('div').find('div')
    try {
       selID = a[parseInt(ind)].getAttribute('data-element_id')
    } catch (err) {
      let b = $('.ebFunctions').find('div').find('a')
       selID = b[parseInt(ind - 1)].getAttribute('data-element_id')
    }
  } else {
    let a = $('.ebFunctions').find('div').find('a')
     selID = a[parseInt(ind - 1)].getAttribute('data-element_id')
  }

  previewString = "Today"
   configDict={
    'function':'Today',
    'inputs':{
        'data':{"Data1":selID},
        "colname": cDict.Today1,
        "previewString":previewString,
    }
  }
} else if(String(cDict.Operation) === 'Weekday'){
  let modelName = ""
  if(compValProcess){
    modelName = compValProcessName
  }else{
    modelName = $('#EBDisplayButtonID').attr('data-name')
  }
  if (typeof (modelName) === 'undefined') {
    modelName = $('#FileName').attr('data-experimentName')
  }
  let selID = ""

  if (parseInt(ind) === 0) {
    let a = $('#dataElementParent').find('div').find('div')
    try {
       selID = a[parseInt(ind)].getAttribute('data-element_id')
    } catch (err) {
      let b = $('.ebFunctions').find('div').find('a')
       selID = b[parseInt(ind - 1)].getAttribute('data-element_id')
    }
  } else {
    let a = $('.ebFunctions').find('div').find('a')
     selID = a[parseInt(ind - 1)].getAttribute('data-element_id')
  }

  previewString = "Weekday"
   configDict={
    'function':'Weekday',
    'inputs':{
        'data':{"Data1":selID},
        "date": cDict.Weekday1,
        "method": cDict.Weekday2,
        "colname": cDict.Weekday3,
        "previewString":previewString,
    }
  }
} else if(String(cDict.Operation) === 'Weeknum'){
  let modelName = ""
  if(compValProcess){
    modelName = compValProcessName
  }else{
    modelName = $('#EBDisplayButtonID').attr('data-name')
  }
  if (typeof (modelName) === 'undefined') {
    modelName = $('#FileName').attr('data-experimentName')
  }
  let selID = ""

  if (parseInt(ind) === 0) {
    let a = $('#dataElementParent').find('div').find('div')
    try {
       selID = a[parseInt(ind)].getAttribute('data-element_id')
    } catch (err) {
      let b = $('.ebFunctions').find('div').find('a')
       selID = b[parseInt(ind - 1)].getAttribute('data-element_id')
    }
  } else {
    let a = $('.ebFunctions').find('div').find('a')
     selID = a[parseInt(ind - 1)].getAttribute('data-element_id')
  }

  previewString = "Weeknum"
   configDict={
    'function':'Weeknum',
    'inputs':{
        'data':{"Data1":selID},
        "date": cDict.Weeknum1,
        "method": cDict.Weeknum2,
        "colname": cDict.Weeknum3,
        "previewString":previewString,
    }
  }
} else if(String(cDict.Operation) === 'Year'){
  let modelName = ""
  if(compValProcess){
    modelName = compValProcessName
  }else{
    modelName = $('#EBDisplayButtonID').attr('data-name')
  }
  if (typeof (modelName) === 'undefined') {
    modelName = $('#FileName').attr('data-experimentName')
  }
  let selID = ""

  if (parseInt(ind) === 0) {
    let a = $('#dataElementParent').find('div').find('div')
    try {
       selID = a[parseInt(ind)].getAttribute('data-element_id')
    } catch (err) {
      let b = $('.ebFunctions').find('div').find('a')
       selID = b[parseInt(ind - 1)].getAttribute('data-element_id')
    }
  } else {
    let a = $('.ebFunctions').find('div').find('a')
     selID = a[parseInt(ind - 1)].getAttribute('data-element_id')
  }

  previewString = "Year"
   configDict={
    'function':'Year',
    'inputs':{
        'data':{"Data1":selID},
        "date": cDict.Year1,
        "colname": cDict.Year2,
        "previewString":previewString,
    }
  }
} else if(String(cDict.Operation) === 'Yearfrac'){
  let modelName = ""
  if(compValProcess){
    modelName = compValProcessName
  }else{
    modelName = $('#EBDisplayButtonID').attr('data-name')
  }
  if (typeof (modelName) === 'undefined') {
    modelName = $('#FileName').attr('data-experimentName')
  }
  let selID = ""

  if (parseInt(ind) === 0) {
    let a = $('#dataElementParent').find('div').find('div')
    try {
       selID = a[parseInt(ind)].getAttribute('data-element_id')
    } catch (err) {
      let b = $('.ebFunctions').find('div').find('a')
       selID = b[parseInt(ind - 1)].getAttribute('data-element_id')
    }
  } else {
    let a = $('.ebFunctions').find('div').find('a')
     selID = a[parseInt(ind - 1)].getAttribute('data-element_id')
  }

  previewString = "Yearfrac"
   configDict={
    'function':'Yearfrac',
    'inputs':{
        'data':{"Data1":selID},
        "start_date": cDict.Yearfrac1,
        "end_date" : cDict.Yearfrac2,
        "basis": cDict.Yearfrac3,
        "colname": cDict.Yearfrac4,
        "previewString":previewString,
    }
  }
} else if(String(cDict.Operation) === 'Networkdays'){
  let modelName = ""
  if(compValProcess){
    modelName = compValProcessName
  }else{
    modelName = $('#EBDisplayButtonID').attr('data-name')
  }
  if (typeof (modelName) === 'undefined') {
    modelName = $('#FileName').attr('data-experimentName')
  }
  let selID = ""

  if (parseInt(ind) === 0) {
    let a = $('#dataElementParent').find('div').find('div')
    try {
       selID = a[parseInt(ind)].getAttribute('data-element_id')
    } catch (err) {
      let b = $('.ebFunctions').find('div').find('a')
       selID = b[parseInt(ind - 1)].getAttribute('data-element_id')
    }
  } else {
    let a = $('.ebFunctions').find('div').find('a')
     selID = a[parseInt(ind - 1)].getAttribute('data-element_id')
  }


  pos_data = cDict.temp_nd[cDict.Networkdays1]
  hol_data = ""

  for(let i=0;i<cDict.table_data.length;i++){
    if(cDict.table_data[i] != pos_data){
      hol_data = cDict.table_data[i]
    }
  }

  if(cDict.Networkdays3 == "-" ||cDict.Networkdays3 == ""){
    hol_data = ""
  }
  previewString = "Networkdays"
   configDict={
    'function':'Networkdays',
    'inputs':{
        'data':{"Data1":selID},
        "pos_data":pos_data,
        "hol_data":hol_data,
        "start_date": cDict.Networkdays1,
        "end_date": cDict.Networkdays2,
        "holiday": cDict.Networkdays3,
        "colname": cDict.Networkdays4,
        "previewString":previewString,
    }
  }
} else if(String(cDict.Operation) === 'Networkdays.Intl'){
  let modelName = ""
  if(compValProcess){
    modelName = compValProcessName
  }else{
    modelName = $('#EBDisplayButtonID').attr('data-name')
  }
  if (typeof (modelName) === 'undefined') {
    modelName = $('#FileName').attr('data-experimentName')
  }
  let selID = ""

  if (parseInt(ind) === 0) {
    let a = $('#dataElementParent').find('div').find('div')
    try {
       selID = a[parseInt(ind)].getAttribute('data-element_id')
    } catch (err) {
      let b = $('.ebFunctions').find('div').find('a')
       selID = b[parseInt(ind - 1)].getAttribute('data-element_id')
    }
  } else {
    let a = $('.ebFunctions').find('div').find('a')
     selID = a[parseInt(ind - 1)].getAttribute('data-element_id')
  }


  pos_data = cDict.temp_nd[cDict.NetworkdaysIntl1]
  hol_data = ""

  for(let i=0;i<cDict.table_data.length;i++){
    if(cDict.table_data[i] != pos_data){
      hol_data = cDict.table_data[i]
    }
  }

  if (cDict.NetworkdaysIntl3 == "-" || cDict.NetworkdaysIntl3 == ""){
    hol_data = ""
  }
  previewString = "Networkdays.Intl"
   configDict={
    'function':'Networkdays.Intl',
    'inputs':{
        'data':{"Data1":selID},
        "pos_data":pos_data,
        "hol_data":hol_data,
        "start_date": cDict.NetworkdaysIntl1,
        "end_date": cDict.NetworkdaysIntl2,
        "holiday": cDict.NetworkdaysIntl3,
        "weekend": cDict.NetworkdaysIntl4,
        "colname": cDict.NetworkdaysIntl5,
        "previewString":previewString,
    }
  }
} else if(String(cDict.Operation) === 'Workdays'){
  let modelName = ""
  if(compValProcess){
    modelName = compValProcessName
  }else{
    modelName = $('#EBDisplayButtonID').attr('data-name')
  }
  if (typeof (modelName) === 'undefined') {
    modelName = $('#FileName').attr('data-experimentName')
  }
  let selID = ""

  if (parseInt(ind) === 0) {
    let a = $('#dataElementParent').find('div').find('div')
    try {
       selID = a[parseInt(ind)].getAttribute('data-element_id')
    } catch (err) {
      let b = $('.ebFunctions').find('div').find('a')
       selID = b[parseInt(ind - 1)].getAttribute('data-element_id')
    }
  } else {
    let a = $('.ebFunctions').find('div').find('a')
     selID = a[parseInt(ind - 1)].getAttribute('data-element_id')
  }


  pos_data = cDict.temp_nd[cDict.Workdays1]
  hol_data = ""

  for(let i=0;i<cDict.table_data.length;i++){
    if(cDict.table_data[i] != pos_data){
      hol_data = cDict.table_data[i]
    }
  }

  if(cDict.Workdays2 == "-" || cDict.Workdays2 == ""){
    hol_data = ""
  }
  previewString = "Workdays"
   configDict={
    'function':'Workdays',
    'inputs':{
        'data':{"Data1":selID},
        "pos_data":pos_data,
        "hol_data":hol_data,
        "start_date": cDict.Workdays1,
        "days": cDict.Workdays3,
        "holiday": cDict.Workdays2,
        "colname": cDict.Workdays4,
        "previewString":previewString,
    }
  }
} else if(String(cDict.Operation) === 'Workdays.Intl'){
  let modelName = ""
  if(compValProcess){
    modelName = compValProcessName
  }else{
    modelName = $('#EBDisplayButtonID').attr('data-name')
  }
  if (typeof (modelName) === 'undefined') {
    modelName = $('#FileName').attr('data-experimentName')
  }
  let selID = ""

  if (parseInt(ind) === 0) {
    let a = $('#dataElementParent').find('div').find('div')
    try {
       selID = a[parseInt(ind)].getAttribute('data-element_id')
    } catch (err) {
      let b = $('.ebFunctions').find('div').find('a')
       selID = b[parseInt(ind - 1)].getAttribute('data-element_id')
    }
  } else {
    let a = $('.ebFunctions').find('div').find('a')
     selID = a[parseInt(ind - 1)].getAttribute('data-element_id')
  }


  pos_data = cDict.temp_nd[cDict.WorkdaysIntl1]
  hol_data = ""

  for(let i=0;i<cDict.table_data.length;i++){
    if(cDict.table_data[i] != pos_data){
      hol_data = cDict.table_data[i]
    }
  }

  if (cDict.WorkdaysIntl2 == "-" || cDict.WorkdaysIntl2 == ""){
    hol_data = ""
  }
  previewString = "Workdays.Intl"
   configDict={
    'function':'Workdays.Intl',
    'inputs':{
        'data':{"Data1":selID},
        "pos_data":pos_data,
        "hol_data":hol_data,
        "start_date": cDict.WorkdaysIntl1,
        "days": cDict.WorkdaysIntl4,
        "holiday": cDict.WorkdaysIntl2,
        "weekend": cDict.WorkdaysIntl3,
        "colname": cDict.WorkdaysIntl5,
        "previewString":previewString,
    }
  }
}

  if (String(cDict.Operation) !== 'Left Join' && String(cDict.Operation) !== 'Right Join' && String(cDict.Operation) !== 'Inner Join' && String(cDict.Operation) !== 'Outer Join' && String(cDict.Operation) !== 'Append and Concatenate') {
    let name_ = ""
    if(compValProcess){
      name_ = compValProcessName
    }else{
      name_ = $('#EBDisplayButtonID').attr('data-name')
    }
    let dataID = 'comp'
    let elementName = ''
    if (typeof (name_) === 'undefined') {
      name_ = $('#FileName').attr('data-experimentName')
      if (typeof (name_) === 'undefined') {
        dataID = 'datamgm'
        if ($('#tname').val() && String(idenFlag) !== 'add') {
          name_ = $('#tname').val()
        } else if (String(idenFlag) === 'add' || String(idenFlag) === 'edit') {
          name_ = $('.dataElements').find('p').text()
        } else if (listViewComp == true) {
          name_ = listViewModelName
        }
      }
    }

    let modelNameP = $('#EBDisplayButtonID').attr('data-p_table_name')
    if (typeof (modelNameP) === "undefined") {
      modelNameP = ""
    }

    if (String(dataID) === 'datamgm' && listViewComp == false) {
      elementName = name_ + selectedCol + Math.floor((Math.random() * 10000000000) + 1)
    } else if (String(dataID) === 'datamgm' && listViewComp == true) {
      elementName = name_ + listViewCompCol + Math.floor((Math.random() * 10000000000) + 1)
    }
    else {
      elementName = cDict.element_id
    }

    if (String(cDict.Operation) !== 'Rename and Drop' && String(cDict.Operation) !== 'Filter' && String(cDict.Operation) !== 'Add Time Periods' && String(cDict.Operation) !== 'Add Column' && String(cDict.Operation) !== 'Sort' && String(cDict.Operation) !== 'Groupby'  && String(cDict.Operation) !== 'Pivot' && String(cDict.Operation) !== 'Unpivot' && String(cDict.Operation) !== 'Data Utilities' && String(cDict.Operation) !== 'Concat Columns' && String(cDict.Operation) !== 'Fill Missing Values' && String(cDict.Operation) !== 'Sum Product' && String(cDict.Operation) !== 'Weighted Average' && String(cDict.Operation) !== 'Drop Duplicate' && String(cDict.Operation) !== 'Add Fix Column' && String(cDict.Operation) !== 'Delimit Column' && String(cDict.Operation) !== 'Find and Replace' && String(cDict.Operation) !== 'Date' && String(cDict.Operation) !== 'Day' && String(cDict.Operation) !== 'Days' && String(cDict.Operation) !== 'Edate' && String(cDict.Operation) !== 'Days360' && String(cDict.Operation) !== 'Eomonth' && String(cDict.Operation) !== 'Hour' && String(cDict.Operation) !== 'Isoweeknum' && String(cDict.Operation) !== 'Minute' && String(cDict.Operation) !== 'Month' && String(cDict.Operation) !== 'Now' && String(cDict.Operation) !== 'Second' && String(cDict.Operation) !== 'Time' && String(cDict.Operation) !== 'Today' && String(cDict.Operation) !== 'Weekday' && String(cDict.Operation) !== 'Weeknum' && String(cDict.Operation) !== 'Year' && String(cDict.Operation) !== 'Yearfrac' && String(cDict.Operation) !== 'Networkdays' && String(cDict.Operation) !== 'Networkdays.Intl' && String(cDict.Operation) !== 'Workdays' && String(cDict.Operation) !== 'Workdays.Intl') {
      $.ajax({
        url: `/users/${urlPath}/computationModule/`,
        data: {
          configList: JSON.stringify({
            data1: name_,
            data2: cDict.element_id,
            data3: configDict,
            elementName: elementName,
            data4: dataID
          }),
          operation: 'save_MathOps_data'
        },
        type: 'POST',
        dataType: 'json',
        success: function (context) {
          Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});

          if (String(dataID) === 'datamgm') {
            if (previewString.length > 30) {
              myTruncatedString = previewString.substring(0, 30) + '...'
              $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
              $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
            } else {
              $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
              $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
              myTruncatedString = previewString
            }
            $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
          }

          if (String(dataID) === 'comp') {
            let name_ = ""
            if(compValProcess){
              name_ = compValProcessName
            }else{
              name_ = $('#EBDisplayButtonID').attr('data-name')
            }
            if (typeof (name_) === 'undefined') {
              name_ = $('#FileName').attr('data-experimentName')
            }
            $.ajax({
              url: `/users/${urlPath}/computationModule/`,
              data: {
                operation: 'run_step_MathOps',
                element_id: uID,
                model_name: name_
              },
              type: 'POST',
              dataType: 'json',
              success: function (data) {
                const jobId = data.job_id
                const runStepBtnId = ''
                const runStepBtnLoadId = ''
                fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

                if (previewString.length > 30) {
                  myTruncatedString = previewString.substring(0, 30) + '...'
                  $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                  $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                } else {
                  $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                  $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                  myTruncatedString = previewString
                }
                $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
              },
              error: function () {
                Swal.fire({icon: 'error',text: 'Error! Please try again.'});
              }
            })
          }
        },
        error: function () {
          Swal.fire({icon: 'error',text: 'Error! Please try again.'});
        }
      })
    } else if (String(cDict.Operation) === 'Rename and Drop') {
      $.ajax({
        url: `/users/${urlPath}/computationModule/`,
        data: {
          configDict: JSON.stringify(configDict),
          model_name: name_,
          element_id: cDict.element_id,
          element_name: elementName,
          operation: 'save_config_data',
          data_id: dataID,
        },
        type: 'POST',
        dataType: 'json',
        success: function (context) {
          Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});

          if (String(dataID) === 'datamgm') {
            if (previewString.length > 30) {
              myTruncatedString = previewString.substring(0, 30) + '...'
              $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
              $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
            } else {
              $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
              $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
              myTruncatedString = previewString
            }
            $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
          }

          if (String(dataID) === 'comp') {
            let name_ = ""
            if(compValProcess){
              name_ = compValProcessName
            }else{
              name_ = $('#EBDisplayButtonID').attr('data-name')
            }
            if (typeof (name_) === 'undefined') {
              name_ = $('#FileName').attr('data-experimentName')
            }
            $.ajax({
              url: `/users/${urlPath}/computationModule/`,
              data: {
                operation: 'run_step_renameColumn',
                element_id: uID,
                model_name: name_
              },
              type: 'POST',
              dataType: 'json',
              success: function (data) {
                const jobId = data.job_id
                const runStepBtnId = ''
                const runStepBtnLoadId = ''
                fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

                if (previewString.length > 30) {
                  myTruncatedString = previewString.substring(0, 30) + '...'
                  $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                  $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                } else {
                  $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                  $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                  myTruncatedString = previewString
                }
                $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
              },
              error: function () {
                Swal.fire({icon: 'error',text: 'Error! Please try again.'});
              }
            })
          }
        },
        error: function () {
          Swal.fire({icon: 'error',text: 'Error! Please try again.'});
        }
      })
    } else if (String(cDict.Operation) === 'Filter') {

      $.ajax({
        url: `/users/${urlPath}/computationModule/`,
        data: {
          'config': JSON.stringify({ model: name_, elementID: uID, config_dict: configDictMergeGroup }),
          'operation': 'save_group_run',
        },
        type: "POST",
        dataType: "json",
        success: function (context) {

          $.ajax({
            url: `/users/${urlPath}/computationModule/`,
            data: {
              model_name: name_,
              element_id: uID,
              element_name: elementName,
              configDict: JSON.stringify(configDict),
              operation: 'save_config_data',
              data_id: dataID
            },
            type: 'POST',
            dataType: 'json',
            success: function (context) {
              Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});

              if (String(dataID) === 'datamgm') {
                if (previewString.length > 30) {
                  myTruncatedString = previewString.substring(0, 30) + '...'
                  $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                  $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                } else {
                  $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                  $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                  myTruncatedString = previewString
                }
                $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
              }

              if (String(dataID) === 'comp') {
                $.ajax({
                  url: `/users/${urlPath}/computationModule/`,
                  data: {
                    operation: 'run_step_merge_and_join',
                    element_id: uID,
                    model_name: name_,
                    model_name_2: modelNameP,
                  },
                  type: 'POST',
                  dataType: 'json',
                  success: function (data) {
                    const jobId = data.job_id
                    const runStepBtnId = ''
                    const runStepBtnLoadId = ''
                    fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

                    if (previewString.length > 30) {
                      myTruncatedString = previewString.substring(0, 30) + '...'
                      $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                      $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                    } else {
                      $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                      $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                      myTruncatedString = previewString
                    }
                    $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
                  },
                  error: function () {
                    Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                  }
                })
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
      });
    } else if (String(cDict.Operation) === 'Add Time Periods') {

      $.ajax({
        url: `/users/${urlPath}/computationModule/`,
        data: {
          configDict: JSON.stringify(configDict),
          model_name: name_,
          element_id: cDict.element_id,
          element_name: elementName,
          operation: 'save_config_data',
          data_id: dataID
        },
        type: 'POST',
        dataType: 'json',
        success: function (context) {
          Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});

          if (String(dataID) === 'datamgm') {
            if (previewString.length > 30) {
              myTruncatedString = previewString.substring(0, 30) + '...'
              $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
              $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
            } else {
              $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
              $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
              myTruncatedString = previewString
            }
            $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
          }

          if (String(dataID) === 'comp') {
            let name_ = ""
            if(compValProcess){
              name_ = compValProcessName
            }else{
              name_ = $('#EBDisplayButtonID').attr('data-name')
            }
            if (typeof (name_) === 'undefined') {
              name_ = $('#FileName').attr('data-experimentName')
            }
            $.ajax({
              url: `/users/${urlPath}/computationModule/`,
              data: {
                operation: 'run_step_timeperiods',
                element_id: uID,
                model_name: name_,
                data_id: dataID
              },
              type: 'POST',
              dataType: 'json',
              success: function (data) {
                const jobId = data.job_id
                const runStepBtnId = ''
                const runStepBtnLoadId = ''
                fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

                if (previewString.length > 30) {
                  myTruncatedString = previewString.substring(0, 30) + '...'
                  $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                  $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                } else {
                  $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                  $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                  myTruncatedString = previewString
                }
                $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
              },
              error: function () {
                Swal.fire({icon: 'error',text: 'Error! Please try again.'});
              }
            })
          }
        },
        error: function () {
          Swal.fire({icon: 'error',text: 'Error! Please try again.'});
        }
      })
    } else if (String(cDict.Operation) === 'Sort') {

      $.ajax({
        url: `/users/${urlPath}/computationModule/`,
        data: {
          model_name: name_,
          element_id: uID,
          element_name: elementName,
          configDict: JSON.stringify(configDict),
          operation: 'save_config_data',
          data_id: dataID
        },
        type: 'POST',
        dataType: 'json',
        success: function (context) {
          Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});

          if (String(dataID) === 'datamgm') {
            if (previewString.length > 30) {
              myTruncatedString = previewString.substring(0, 30) + '...'
              $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
              $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
            } else {
              $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
              $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
              myTruncatedString = previewString
            }
            $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
          }


          if (String(dataID) === 'comp') {
            $.ajax({
              url: `/users/${urlPath}/computationModule/`,
              data: {
                operation: 'run_step_merge_and_join',
                element_id: uID,
                model_name: name_,
                async: true,

              },
              type: "POST",
              dataType: "json",
              success: function (data) {
                var jobId = data.job_id;
                const runStepBtnId = ''
                const runStepBtnLoadId = ''
                fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)
                if (previewString.length > 30) {
                  myTruncatedString = previewString.substring(0, 30) + '...'
                  $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                  $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                } else {
                  $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                  $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                  myTruncatedString = previewString
                }
                $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
              },
              error: function () {
                Swal.fire({icon: 'error',text: 'Error! Please try again.'});

              }
            });
          }
        },
        error: function () {
          Swal.fire({icon: 'error',text: 'Error! Please try again.'});
        }
      })

    } else if (String(cDict.Operation) === 'Add Column') {
      $.ajax({
        url: `/users/${urlPath}/computationModule/`,
        data: {
          'config': JSON.stringify({ model: name_, elementID: uID, config_dict: configDictMergeGroup }),
          'operation': 'save_group_run',
        },
        type: "POST",
        dataType: "json",
        success: function (context) {
          $.ajax({
            url: `/users/${urlPath}/computationModule/`,
            data: {
              model_name: name_,
              element_id: uID,
              element_name: elementName,
              configDict: JSON.stringify(configDict),
              operation: 'save_config_data',
              data_id: dataID
            },
            type: 'POST',
            dataType: 'json',
            success: function (context) {
              Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});

              if (String(dataID) === 'datamgm') {
                if (previewString.length > 30) {
                  myTruncatedString = previewString.substring(0, 30) + '...'
                  $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                  $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                } else {
                  $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                  $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                  myTruncatedString = previewString
                }
                $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
              }

              if (String(dataID) === 'comp') {
                $.ajax({
                  url: `/users/${urlPath}/computationModule/`,
                  data: {
                    operation: 'run_step_merge_and_join',
                    element_id: uID,
                    model_name: name_,
                    async: true,

                  },
                  type: "POST",
                  dataType: "json",
                  success: function (data) {
                    var jobId = data.job_id;
                    const runStepBtnId = ''
                    const runStepBtnLoadId = ''
                    fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

                    if (previewString.length > 30) {
                      myTruncatedString = previewString.substring(0, 30) + '...'
                      $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                      $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                    } else {
                      $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                      $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                      myTruncatedString = previewString
                    }
                    $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
                  },
                  error: function () {
                    Swal.fire({icon: 'error',text: 'Error! Please try again.'});

                  }
                });
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
      });
    } else if (String(cDict.Operation) === 'Pivot') {
      $.ajax({
        url: `/users/${urlPath}/computationModule/`,
        data: {
          'config': JSON.stringify({ model: name_, elementID: uID, config_dict: configDict, elementName: elementName }),
          'operation': 'save_pivot_and_transpose',
        },
        type: "POST",
        dataType: "json",
        success: function (context) {
          Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});

          if (String(dataID) === 'datamgm') {
            if (previewString.length > 30) {
              myTruncatedString = previewString.substring(0, 30) + '...'
              $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
              $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
            } else {
              $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
              $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
              myTruncatedString = previewString
            }
            $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
          }

          if (String(dataID) === 'comp') {
            $.ajax({
              url: `/users/${urlPath}/computationModule/`,
              data: {
                'operation': 'run_step_pivot_and_transpose',
                'element_id': uID,
                'model_name': name_,
              },
              type: "POST",
              dataType: "json",
              success: function (data) {
                var jobId = data.job_id;
                const runStepBtnId = ''
                const runStepBtnLoadId = ''
                fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)
                if (previewString.length > 30) {
                  myTruncatedString = previewString.substring(0, 30) + '...'
                  $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                  $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                } else {
                  $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                  $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                  myTruncatedString = previewString
                }
                $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
              },
              error: function () {
                Swal.fire({icon: 'error',text: 'Error! Please try again.'});

              }
            });
          }
        }
      });

    } else if (String(cDict.Operation) === 'Groupby') {
      $.ajax({
        url: `/users/${urlPath}/computationModule/`,
        data: {
          'config': JSON.stringify({ model: name_, elementID: uID, config_dict: configDictMergeGroup }),
          'operation': 'save_group_run',
        },
        type: "POST",
        dataType: "json",
        success: function (context) {
          $.ajax({
            url: `/users/${urlPath}/computationModule/`,
            data: {
              model_name: name_,
              element_id: uID,
              element_name: elementName,
              configDict: JSON.stringify(configDict),
              operation: 'save_config_data',
              data_id: dataID
            },
            type: 'POST',
            dataType: 'json',
            success: function (context) {
              Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});

              if (String(dataID) === 'datamgm') {
                if (previewString.length > 30) {
                  myTruncatedString = previewString.substring(0, 30) + '...'
                  $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                  $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                } else {
                  $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                  $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                  myTruncatedString = previewString
                }
                $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
              }

              if (String(dataID) === 'comp') {
                $.ajax({
                  url: `/users/${urlPath}/computationModule/`,
                  data: {
                    operation: 'run_step_merge_and_join',
                    element_id: uID,
                    model_name: name_,
                    async: true,

                  },
                  type: "POST",
                  dataType: "json",
                  success: function (data) {
                    var jobId = data.job_id;
                    const runStepBtnId = ''
                    const runStepBtnLoadId = ''
                    fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

                    if (previewString.length > 30) {
                      myTruncatedString = previewString.substring(0, 30) + '...'
                      $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                      $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                    } else {
                      $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                      $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                      myTruncatedString = previewString
                    }
                    $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
                  },
                  error: function () {
                    Swal.fire({icon: 'error',text: 'Error! Please try again.'});

                  }
                });
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
      });
    } else if (String(cDict.Operation) === 'Unpivot') {
      $.ajax({
        url: `/users/${urlPath}/computationModule/`,
        data: {
          'config': JSON.stringify({ model: name_, elementID: uID, config_dict: configDict, elementName: elementName }),
          'operation': 'save_pivot_and_transpose',
        },
        type: "POST",
        dataType: "json",
        success: function (context) {
          Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});
          if (String(dataID) === 'datamgm') {
            if (previewString.length > 30) {
              myTruncatedString = previewString.substring(0, 30) + '...'
              $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
              $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
            } else {
              $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
              $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
              myTruncatedString = previewString
            }
            $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
          }

          if (String(dataID) === 'comp') {
            $.ajax({
              url: `/users/${urlPath}/computationModule/`,
              data: {
                'operation': 'run_step_pivot_and_transpose',
                'element_id': uID,
                'model_name': name_,
              },
              type: "POST",
              dataType: "json",
              success: function (data) {
                var jobId = data.job_id;
                const runStepBtnId = ''
                const runStepBtnLoadId = ''
                fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)
                if (previewString.length > 30) {
                  myTruncatedString = previewString.substring(0, 30) + '...'
                  $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                  $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                } else {
                  $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                  $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                  myTruncatedString = previewString
                }
                $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
              },
              error: function () {
                Swal.fire({icon: 'error',text: 'Error! Please try again.'});

              }
            });
          }

        },
        error: function () {
          Swal.fire({icon: 'error',text: 'Error! Please try again.'});
        }
      });


    } else if (String(cDict.Operation) === 'Concat Columns') {
      $.ajax({
        url: `/users/${urlPath}/computationModule/`,
        data: {
          configDict: JSON.stringify(configDict),
          model_name: name_,
          element_id: cDict.element_id,
          element_name: elementName,
          operation: 'save_config_data'
        },
        type: 'POST',
        dataType: 'json',
        success: function (context) {
          Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});

          if (String(dataID) === 'datamgm') {
            if (previewString.length > 30) {
              myTruncatedString = previewString.substring(0, 30) + '...'
              $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
              $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
            } else {
              $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
              $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
              myTruncatedString = previewString
            }
            $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
          }

          if (String(dataID) === 'comp') {
            let name_ = ""
            if(compValProcess){
              name_ = compValProcessName
            }else{
              name_ = $('#EBDisplayButtonID').attr('data-name')
            }
            if (typeof (name_) === 'undefined') {
              name_ = $('#FileName').attr('data-experimentName')
            }
            $.ajax({
              url: `/users/${urlPath}/computationModule/`,
              data: {
                operation: 'run_step_concatColumns',
                element_id: uID,
                model_name: name_,
                data_id: dataID
              },
              type: 'POST',
              dataType: 'json',
              success: function (data) {
                const jobId = data.job_id
                const runStepBtnId = ''
                const runStepBtnLoadId = ''
                fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

                if (previewString.length > 30) {
                  myTruncatedString = previewString.substring(0, 30) + '...'
                  $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                  $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                } else {
                  $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                  $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                  myTruncatedString = previewString
                }
                $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
              },
              error: function () {
                Swal.fire({icon: 'error',text: 'Error! Please try again.'});
              }
            })
          }
        },
        error: function () {
          Swal.fire({icon: 'error',text: 'Error! Please try again.'});
        }
      })



    } else if (String(cDict.Operation) === 'Concat Columns') {
      $.ajax({
        url: `/users/${urlPath}/computationModule/`,
        data: {
          configDict: JSON.stringify(configDict),
          model_name: name_,
          element_id: cDict.element_id,
          element_name: elementName,
          operation: 'save_config_data'
        },
        type: 'POST',
        dataType: 'json',
        success: function (context) {
          Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});

          if (String(dataID) === 'datamgm') {
            if (previewString.length > 30) {
              myTruncatedString = previewString.substring(0, 30) + '...'
              $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
              $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
            } else {
              $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
              $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
              myTruncatedString = previewString
            }
            $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
          }

          if (String(dataID) === 'comp') {
            let name_ = ""
            if(compValProcess){
              name_ = compValProcessName
            }else{
              name_ = $('#EBDisplayButtonID').attr('data-name')
            }
            if (typeof (name_) === 'undefined') {
              name_ = $('#FileName').attr('data-experimentName')
            }
            $.ajax({
              url: `/users/${urlPath}/computationModule/`,
              data: {
                operation: 'run_step_concatColumns',
                element_id: uID,
                model_name: name_,
                data_id: dataID
              },
              type: 'POST',
              dataType: 'json',
              success: function (data) {
                const jobId = data.job_id
                const runStepBtnId = ''
                const runStepBtnLoadId = ''
                fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

                if (previewString.length > 30) {
                  myTruncatedString = previewString.substring(0, 30) + '...'
                  $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                  $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                } else {
                  $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                  $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                  myTruncatedString = previewString
                }
                $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
              },
              error: function () {
                Swal.fire({icon: 'error',text: 'Error! Please try again.'});
              }
            })
          }
        },
        error: function () {
          Swal.fire({icon: 'error',text: 'Error! Please try again.'});
        }
      })



    } else if (String(cDict.Operation) === 'Data Utilities') {

      $.ajax({
        url: `/users/${urlPath}/computationModule/`,
        data: {
          configDict: JSON.stringify(configDict),
          model_name: name_,
          element_id: cDict.element_id,
          element_name: elementName,
          operation: 'save_config_data',
          data_id: dataID
        },
        type: 'POST',
        dataType: 'json',
        success: function (context) {
          Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});

          if (String(dataID) === 'datamgm') {
            if (previewString.length > 30) {
              myTruncatedString = previewString.substring(0, 30) + '...'
              $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
              $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
            } else {
              $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
              $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
              myTruncatedString = previewString
            }
            $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
          }

          if (String(dataID) === 'comp') {
            let name_ = ""
            if(compValProcess){
              name_ = compValProcessName
            }else{
              name_ = $('#EBDisplayButtonID').attr('data-name')
            }
            if (typeof (name_) === 'undefined') {
              name_ = $('#FileName').attr('data-experimentName')
            }
            $.ajax({
              url:  `/users/${urlPath}/computationModule/`,
              data: {
                operation: 'run_stepResetInd',
                element_id: uID,
                model_name: name_,
                data_id: dataID
              },
              type: 'POST',
              dataType: 'json',
              success: function (data) {
                const jobId = data.job_id
                const runStepBtnId = ''
                const runStepBtnLoadId = ''
                fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

                if (previewString.length > 30) {
                  myTruncatedString = previewString.substring(0, 30) + '...'
                  $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                  $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                } else {
                  $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                  $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                  myTruncatedString = previewString
                }
                $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
              },
              error: function () {
                Swal.fire({icon: 'error',text: 'Error! Please try again.'});
              }
            })
          }
        },
        error: function () {
          Swal.fire({icon: 'error',text: 'Error! Please try again.'});
        }
      })

    } else if(String(cDict.Operation) === 'Fill Missing Values') {

      $.ajax({
        url: `/users/${urlPath}/computationModule/`,
        data: {
          configDict: JSON.stringify(configDict),
          model_name: name_,
          element_id: cDict.element_id,
          element_name: elementName,
          operation: 'save_config_data',
          data_id: dataID
        },
        type: 'POST',
        dataType: 'json',
        success: function (context) {
          Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});

          if (String(dataID) === 'datamgm') {
            if (previewString.length > 30) {
              myTruncatedString = previewString.substring(0, 30) + '...'
              $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
              $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
            } else {
              $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
              $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
              myTruncatedString = previewString
            }
            $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
          }

          if (String(dataID) === 'comp') {
            let name_ = ""
            if(compValProcess){
              name_ = compValProcessName
            }else{
              name_ = $('#EBDisplayButtonID').attr('data-name')
            }
            if (typeof (name_) === 'undefined') {
              name_ = $('#FileName').attr('data-experimentName')
            }
            $.ajax({
              url: `/users/${urlPath}/computationModule/`,
              data: {
                'operation': 'run_step_MissingValues',
                             'element_id': cDict.element_id,
                             'model_name':name_,
              },
              type: 'POST',
              dataType: 'json',
              success: function (data) {
                const jobId = data.job_id
                const runStepBtnId = ''
                const runStepBtnLoadId = ''
                fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

                if (previewString.length > 30) {
                  myTruncatedString = previewString.substring(0, 30) + '...'
                  $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                  $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                } else {
                  $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                  $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                  myTruncatedString = previewString
                }
                $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
              },
              error: function () {
                Swal.fire({icon: 'error',text: 'Error! Please try again.'});
              }
            })
          }
        },
        error: function () {
          Swal.fire({icon: 'error',text: 'Error! Please try again.'});
        }
      })

    } else if(String(cDict.Operation) === 'Sum Product') {

      $.ajax({
          url: `/users/${urlPath}/computationModule/`,
          data: {
            configDict: JSON.stringify(configDict),
            model_name: name_,
            element_id: cDict.element_id,
            element_name: elementName,
            operation: 'save_config_data',
            data_id: dataID
          },
          type: 'POST',
          dataType: 'json',
          success: function (context) {
            Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});

            if (String(dataID) === 'datamgm') {
              if (previewString.length > 30) {
                myTruncatedString = previewString.substring(0, 30) + '...'
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
              } else {
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                myTruncatedString = previewString
              }
              $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
            }

            if (String(dataID) === 'comp') {
              let name_ = ""
              if(compValProcess){
                name_ = compValProcessName
              }else{
                name_ = $('#EBDisplayButtonID').attr('data-name')
              }
              if (typeof (name_) === 'undefined') {
                name_ = $('#FileName').attr('data-experimentName')
              }
              $.ajax({
                url: `/users/${urlPath}/computationModule/`,
                data: {
                  'operation': 'run_step_elementary_stats',
                               'element_id': cDict.element_id,
                               'model_name':name_,
                },
                type: 'POST',
                dataType: 'json',
                success: function (data) {
                  const jobId = data.job_id
                  const runStepBtnId = ''
                  const runStepBtnLoadId = ''
                  fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

                  if (previewString.length > 30) {
                    myTruncatedString = previewString.substring(0, 30) + '...'
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                  } else {
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                    myTruncatedString = previewString
                  }
                  $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
                },
                error: function () {
                  Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                }
              })
            }
          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          }
        })

      } else if (String(cDict.Operation) === 'Weighted Average') {

        $.ajax({
            url: `/users/${urlPath}/computationModule/`,
            data: {
              configDict: JSON.stringify(configDict),
              model_name: name_,
              element_id: cDict.element_id,
              element_name: elementName,
              operation: 'save_config_data',
              data_id: dataID
            },
            type: 'POST',
            dataType: 'json',
            success: function (context) {
              Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});

              if (String(dataID) === 'datamgm') {
                if (previewString.length > 30) {
                  myTruncatedString = previewString.substring(0, 30) + '...'
                  $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                  $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                } else {
                  $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                  $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                  myTruncatedString = previewString
                }
                $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
              }

              if (String(dataID) === 'comp') {
                let name_ = ""
                if(compValProcess){
                  name_ = compValProcessName
                }else{
                  name_ = $('#EBDisplayButtonID').attr('data-name')
                }
                if (typeof (name_) === 'undefined') {
                  name_ = $('#FileName').attr('data-experimentName')
                }
                $.ajax({
                  url: `/users/${urlPath}/computationModule/`,
                  data: {
                    'operation': 'run_step_elementary_stats',
                                 'element_id': cDict.element_id,
                                 'model_name':name_,
                  },
                  type: 'POST',
                  dataType: 'json',
                  success: function (data) {
                    const jobId = data.job_id
                    const runStepBtnId = ''
                    const runStepBtnLoadId = ''
                    fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

                    if (previewString.length > 30) {
                      myTruncatedString = previewString.substring(0, 30) + '...'
                      $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                      $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                    } else {
                      $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                      $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                      myTruncatedString = previewString
                    }
                    $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
                  },
                  error: function () {
                    Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                  }
                })
              }
            },
            error: function () {
              Swal.fire({icon: 'error',text: 'Error! Please try again.'});
            }
          })

      } else if (String(cDict.Operation) === 'Drop Duplicate'){

        $.ajax({
          url: `/users/${urlPath}/computationModule/`,
          data: {
            configDict: JSON.stringify(configDict),
            model_name: name_,
            element_id: cDict.element_id,
            element_name: elementName,
            operation: 'save_config_data',
            data_id: dataID
          },
          type: 'POST',
          dataType: 'json',
          success: function (context) {
            Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});

            if (String(dataID) === 'datamgm') {
              if (previewString.length > 30) {
                myTruncatedString = previewString.substring(0, 30) + '...'
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
              } else {
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                myTruncatedString = previewString
              }
              $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
            }

            if (String(dataID) === 'comp') {
              let name_ = ""
              if(compValProcess){
                name_ = compValProcessName
              }else{
                name_ = $('#EBDisplayButtonID').attr('data-name')
              }
              if (typeof (name_) === 'undefined') {
                name_ = $('#FileName').attr('data-experimentName')
              }
              $.ajax({
                url: `/users/${urlPath}/computationModule/`,
                data: {
                  operation: "run_step_DropDuplicate",
                  element_id: uID,
                  model_name: name_,
                  data_id: dataID
                },
                type: 'POST',
                dataType: 'json',
                success: function (data) {
                  const jobId = data.job_id
                  const runStepBtnId = ''
                  const runStepBtnLoadId = ''
                  fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

                  if (previewString.length > 30) {
                    myTruncatedString = previewString.substring(0, 30) + '...'
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                  } else {
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                    myTruncatedString = previewString
                  }
                  $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
                },
                error: function () {
                  Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                }
              })
            }
          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          }
        })
      } else if (String(cDict.Operation) === 'Add Fix Column') {

        $.ajax({
          url: `/users/${urlPath}/computationModule/`,
          data: {
            configDict: JSON.stringify(configDict),
            model_name: name_,
            element_id: cDict.element_id,
            element_name: elementName,
            operation: 'save_config_data',
            data_id: dataID
          },
          type: 'POST',
          dataType: 'json',
          success: function (context) {
            Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});

            if (String(dataID) === 'datamgm') {
              if (previewString.length > 30) {
                myTruncatedString = previewString.substring(0, 30) + '...'
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
              } else {
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                myTruncatedString = previewString
              }
              $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
            }

            if (String(dataID) === 'comp') {
              let name_ = ""
              if(compValProcess){
                name_ = compValProcessName
              }else{
                name_ = $('#EBDisplayButtonID').attr('data-name')
              }
              if (typeof (name_) === 'undefined') {
                name_ = $('#FileName').attr('data-experimentName')
              }
              $.ajax({
                url: `/users/${urlPath}/computationModule/`,
                data: {
                  operation: 'run_stepAdd_Fix_Column',
                  element_id: uID,
                  model_name: name_,
                  data_id: dataID
                },
                type: 'POST',
                dataType: 'json',
                success: function (data) {
                  const jobId = data.job_id
                  const runStepBtnId = ''
                  const runStepBtnLoadId = ''
                  fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

                  if (previewString.length > 30) {
                    myTruncatedString = previewString.substring(0, 30) + '...'
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                  } else {
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                    myTruncatedString = previewString
                  }
                  $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
                },
                error: function () {
                  Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                }
              })
            }
          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          }
        })
      } else if (String(cDict.Operation) === 'Delimit Column') {

        $.ajax({
          url: `/users/${urlPath}/computationModule/`,
          data: {
            configList: JSON.stringify({data1:name_, data2:cDict.element_id, data3:configDict,elementName:elementName}),
            operation: 'save_buttonCompareColumn',
            data_id: dataID
          },
          type: 'POST',
          dataType: 'json',
          success: function (context) {
            Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});

            if (String(dataID) === 'datamgm') {
              if (previewString.length > 30) {
                myTruncatedString = previewString.substring(0, 30) + '...'
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
              } else {
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                myTruncatedString = previewString
              }
              $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
            }

            if (String(dataID) === 'comp') {
              let name_ = ""
              if(compValProcess){
                name_ = compValProcessName
              }else{
                name_ = $('#EBDisplayButtonID').attr('data-name')
              }
              if (typeof (name_) === 'undefined') {
                name_ = $('#FileName').attr('data-experimentName')
              }
              $.ajax({
                url: `/users/${urlPath}/computationModule/`,
                data: {
                  operation: 'run_stepDelimitColumn',
                  element_id: uID,
                  model_name: name_,
                  data_id: dataID
                },
                type: 'POST',
                dataType: 'json',
                success: function (data) {
                  const jobId = data.job_id
                  const runStepBtnId = ''
                  const runStepBtnLoadId = ''
                  fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

                  if (previewString.length > 30) {
                    myTruncatedString = previewString.substring(0, 30) + '...'
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                  } else {
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                    myTruncatedString = previewString
                  }
                  $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
                },
                error: function () {
                  Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                }
              })
            }
          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          }
        })
      } else if (String(cDict.Operation) === 'Find and Replace') {
        $.ajax({
          url: `/users/${urlPath}/computationModule/`,
          data: {
            configList: JSON.stringify({data1:name_, data2:cDict.element_id, data3:configDict,elementName:elementName}),
            operation: 'save_buttonCompareColumn',
            data_id: dataID
          },
          type: 'POST',
          dataType: 'json',
          success: function (context) {
            Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});

            if (String(dataID) === 'datamgm') {
              if (previewString.length > 30) {
                myTruncatedString = previewString.substring(0, 30) + '...'
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
              } else {
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                myTruncatedString = previewString
              }
              $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
            }

            if (String(dataID) === 'comp') {
              let name_ = ""
              if(compValProcess){
                name_ = compValProcessName
              }else{
                name_ = $('#EBDisplayButtonID').attr('data-name')
              }
              if (typeof (name_) === 'undefined') {
                name_ = $('#FileName').attr('data-experimentName')
              }
              $.ajax({
                url: `/users/${urlPath}/computationModule/`,
                data: {
                  operation: 'run_step_find_replace',
                  element_id: uID,
                  model_name: name_,
                  data_id: dataID
                },
                type: 'POST',
                dataType: 'json',
                success: function (data) {
                  const jobId = data.job_id
                  const runStepBtnId = ''
                  const runStepBtnLoadId = ''
                  fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

                  if (previewString.length > 30) {
                    myTruncatedString = previewString.substring(0, 30) + '...'
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                  } else {
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                    myTruncatedString = previewString
                  }
                  $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
                },
                error: function () {
                  Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                }
              })
            }
          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          }
        })
      }else if (String(cDict.Operation) === 'Date') {

        $.ajax({
          url: `/users/${urlPath}/computationModule/`,
          data: {
            configList: JSON.stringify({data1:name_, data2:cDict.element_id, data3:configDict,elementName:elementName}),
            operation: 'save_buttonCompareColumn',
            data_id: dataID
          },
          type: 'POST',
          dataType: 'json',
          success: function (context) {
            Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});

            if (String(dataID) === 'datamgm') {
              if (previewString.length > 30) {
                myTruncatedString = previewString.substring(0, 30) + '...'
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
              } else {
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                myTruncatedString = previewString
              }
              $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
            }

            if (String(dataID) === 'comp') {
              let name_ = ""
              if(compValProcess){
                name_ = compValProcessName
              }else{
                name_ = $('#EBDisplayButtonID').attr('data-name')
              }
              if (typeof (name_) === 'undefined') {
                name_ = $('#FileName').attr('data-experimentName')
              }
              $.ajax({
                url: `/users/${urlPath}/computationModule/`,
                data: {
                  operation: 'run_stepDelimitColumn',
                  element_id: uID,
                  model_name: name_,
                  data_id: dataID
                },
                type: 'POST',
                dataType: 'json',
                success: function (data) {
                  const jobId = data.job_id
                  const runStepBtnId = ''
                  const runStepBtnLoadId = ''
                  fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

                  if (previewString.length > 30) {
                    myTruncatedString = previewString.substring(0, 30) + '...'
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                  } else {
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                    myTruncatedString = previewString
                  }
                  $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
                },
                error: function () {
                  Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                }
              })
            }
          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          }
        })
      } else if (String(cDict.Operation) === 'Day') {

        $.ajax({
          url: `/users/${urlPath}/computationModule/`,
          data: {
            configList: JSON.stringify({data1:name_, data2:cDict.element_id, data3:configDict,elementName:elementName}),
            operation: 'save_buttonCompareColumn',
            data_id: dataID
          },
          type: 'POST',
          dataType: 'json',
          success: function (context) {
            Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});

            if (String(dataID) === 'datamgm') {
              if (previewString.length > 30) {
                myTruncatedString = previewString.substring(0, 30) + '...'
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
              } else {
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                myTruncatedString = previewString
              }
              $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
            }

            if (String(dataID) === 'comp') {
              let name_ = ""
              if(compValProcess){
                name_ = compValProcessName
              }else{
                name_ = $('#EBDisplayButtonID').attr('data-name')
              }
              if (typeof (name_) === 'undefined') {
                name_ = $('#FileName').attr('data-experimentName')
              }
              $.ajax({
                url: `/users/${urlPath}/computationModule/`,
                data: {
                  operation: 'run_stepDelimitColumn',
                  element_id: uID,
                  model_name: name_,
                  data_id: dataID
                },
                type: 'POST',
                dataType: 'json',
                success: function (data) {
                  const jobId = data.job_id
                  const runStepBtnId = ''
                  const runStepBtnLoadId = ''
                  fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

                  if (previewString.length > 30) {
                    myTruncatedString = previewString.substring(0, 30) + '...'
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                  } else {
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                    myTruncatedString = previewString
                  }
                  $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
                },
                error: function () {
                  Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                }
              })
            }
          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          }
        })
      } else if (String(cDict.Operation) === 'Days') {

        $.ajax({
          url: `/users/${urlPath}/computationModule/`,
          data: {
            configList: JSON.stringify({data1:name_, data2:cDict.element_id, data3:configDict,elementName:elementName}),
            operation: 'save_buttonCompareColumn',
            data_id: dataID
          },
          type: 'POST',
          dataType: 'json',
          success: function (context) {
            Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});

            if (String(dataID) === 'datamgm') {
              if (previewString.length > 30) {
                myTruncatedString = previewString.substring(0, 30) + '...'
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
              } else {
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                myTruncatedString = previewString
              }
              $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
            }

            if (String(dataID) === 'comp') {
              let name_ = ""
              if(compValProcess){
                name_ = compValProcessName
              }else{
                name_ = $('#EBDisplayButtonID').attr('data-name')
              }
              if (typeof (name_) === 'undefined') {
                name_ = $('#FileName').attr('data-experimentName')
              }
              $.ajax({
                url: `/users/${urlPath}/computationModule/`,
                data: {
                  operation: 'run_stepDelimitColumn',
                  element_id: uID,
                  model_name: name_,
                  data_id: dataID
                },
                type: 'POST',
                dataType: 'json',
                success: function (data) {
                  const jobId = data.job_id
                  const runStepBtnId = ''
                  const runStepBtnLoadId = ''
                  fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

                  if (previewString.length > 30) {
                    myTruncatedString = previewString.substring(0, 30) + '...'
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                  } else {
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                    myTruncatedString = previewString
                  }
                  $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
                },
                error: function () {
                  Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                }
              })
            }
          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          }
        })
      } else if (String(cDict.Operation) === 'Edate') {

        $.ajax({
          url: `/users/${urlPath}/computationModule/`,
          data: {
            configList: JSON.stringify({data1:name_, data2:cDict.element_id, data3:configDict,elementName:elementName}),
            operation: 'save_buttonCompareColumn',
            data_id: dataID
          },
          type: 'POST',
          dataType: 'json',
          success: function (context) {
            Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});

            if (String(dataID) === 'datamgm') {
              if (previewString.length > 30) {
                myTruncatedString = previewString.substring(0, 30) + '...'
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
              } else {
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                myTruncatedString = previewString
              }
              $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
            }

            if (String(dataID) === 'comp') {
              let name_ = ""
              if(compValProcess){
                name_ = compValProcessName
              }else{
                name_ = $('#EBDisplayButtonID').attr('data-name')
              }
              if (typeof (name_) === 'undefined') {
                name_ = $('#FileName').attr('data-experimentName')
              }
              $.ajax({
                url: `/users/${urlPath}/computationModule/`,
                data: {
                  operation: 'run_stepDelimitColumn',
                  element_id: uID,
                  model_name: name_,
                  data_id: dataID
                },
                type: 'POST',
                dataType: 'json',
                success: function (data) {
                  const jobId = data.job_id
                  const runStepBtnId = ''
                  const runStepBtnLoadId = ''
                  fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

                  if (previewString.length > 30) {
                    myTruncatedString = previewString.substring(0, 30) + '...'
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                  } else {
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                    myTruncatedString = previewString
                  }
                  $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
                },
                error: function () {
                  Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                }
              })
            }
          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          }
        })
      } else if (String(cDict.Operation) === 'Days360') {

        $.ajax({
          url: `/users/${urlPath}/computationModule/`,
          data: {
            configList: JSON.stringify({data1:name_, data2:cDict.element_id, data3:configDict,elementName:elementName}),
            operation: 'save_buttonCompareColumn',
            data_id: dataID
          },
          type: 'POST',
          dataType: 'json',
          success: function (context) {
            Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});

            if (String(dataID) === 'datamgm') {
              if (previewString.length > 30) {
                myTruncatedString = previewString.substring(0, 30) + '...'
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
              } else {
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                myTruncatedString = previewString
              }
              $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
            }

            if (String(dataID) === 'comp') {
              let name_ = ""
              if(compValProcess){
                name_ = compValProcessName
              }else{
                name_ = $('#EBDisplayButtonID').attr('data-name')
              }
              if (typeof (name_) === 'undefined') {
                name_ = $('#FileName').attr('data-experimentName')
              }
              $.ajax({
                url: `/users/${urlPath}/computationModule/`,
                data: {
                  operation: 'run_stepDelimitColumn',
                  element_id: uID,
                  model_name: name_,
                  data_id: dataID
                },
                type: 'POST',
                dataType: 'json',
                success: function (data) {
                  const jobId = data.job_id
                  const runStepBtnId = ''
                  const runStepBtnLoadId = ''
                  fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

                  if (previewString.length > 30) {
                    myTruncatedString = previewString.substring(0, 30) + '...'
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                  } else {
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                    myTruncatedString = previewString
                  }
                  $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
                },
                error: function () {
                  Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                }
              })
            }
          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          }
        })
      } else if (String(cDict.Operation) === 'Eomonth') {

        $.ajax({
          url: `/users/${urlPath}/computationModule/`,
          data: {
            configList: JSON.stringify({data1:name_, data2:cDict.element_id, data3:configDict,elementName:elementName}),
            operation: 'save_buttonCompareColumn',
            data_id: dataID
          },
          type: 'POST',
          dataType: 'json',
          success: function (context) {
            Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});

            if (String(dataID) === 'datamgm') {
              if (previewString.length > 30) {
                myTruncatedString = previewString.substring(0, 30) + '...'
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
              } else {
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                myTruncatedString = previewString
              }
              $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
            }

            if (String(dataID) === 'comp') {
              let name_ = ""
              if(compValProcess){
                name_ = compValProcessName
              }else{
                name_ = $('#EBDisplayButtonID').attr('data-name')
              }
              if (typeof (name_) === 'undefined') {
                name_ = $('#FileName').attr('data-experimentName')
              }
              $.ajax({
                url: `/users/${urlPath}/computationModule/`,
                data: {
                  operation: 'run_stepDelimitColumn',
                  element_id: uID,
                  model_name: name_,
                  data_id: dataID
                },
                type: 'POST',
                dataType: 'json',
                success: function (data) {
                  const jobId = data.job_id
                  const runStepBtnId = ''
                  const runStepBtnLoadId = ''
                  fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

                  if (previewString.length > 30) {
                    myTruncatedString = previewString.substring(0, 30) + '...'
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                  } else {
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                    myTruncatedString = previewString
                  }
                  $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
                },
                error: function () {
                  Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                }
              })
            }
          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          }
        })
      } else if (String(cDict.Operation) === 'Hour') {

        $.ajax({
          url: `/users/${urlPath}/computationModule/`,
          data: {
            configList: JSON.stringify({data1:name_, data2:cDict.element_id, data3:configDict,elementName:elementName}),
            operation: 'save_buttonCompareColumn',
            data_id: dataID
          },
          type: 'POST',
          dataType: 'json',
          success: function (context) {
            Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});

            if (String(dataID) === 'datamgm') {
              if (previewString.length > 30) {
                myTruncatedString = previewString.substring(0, 30) + '...'
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
              } else {
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                myTruncatedString = previewString
              }
              $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
            }

            if (String(dataID) === 'comp') {
              let name_ = ""
              if(compValProcess){
                name_ = compValProcessName
              }else{
                name_ = $('#EBDisplayButtonID').attr('data-name')
              }
              if (typeof (name_) === 'undefined') {
                name_ = $('#FileName').attr('data-experimentName')
              }
              $.ajax({
                url: `/users/${urlPath}/computationModule/`,
                data: {
                  operation: 'run_stepDelimitColumn',
                  element_id: uID,
                  model_name: name_,
                  data_id: dataID
                },
                type: 'POST',
                dataType: 'json',
                success: function (data) {
                  const jobId = data.job_id
                  const runStepBtnId = ''
                  const runStepBtnLoadId = ''
                  fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

                  if (previewString.length > 30) {
                    myTruncatedString = previewString.substring(0, 30) + '...'
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                  } else {
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                    myTruncatedString = previewString
                  }
                  $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
                },
                error: function () {
                  Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                }
              })
            }
          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          }
        })
      } else if (String(cDict.Operation) === 'Isoweeknum') {

        $.ajax({
          url: `/users/${urlPath}/computationModule/`,
          data: {
            configList: JSON.stringify({data1:name_, data2:cDict.element_id, data3:configDict,elementName:elementName}),
            operation: 'save_buttonCompareColumn',
            data_id: dataID
          },
          type: 'POST',
          dataType: 'json',
          success: function (context) {
            Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});

            if (String(dataID) === 'datamgm') {
              if (previewString.length > 30) {
                myTruncatedString = previewString.substring(0, 30) + '...'
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
              } else {
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                myTruncatedString = previewString
              }
              $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
            }

            if (String(dataID) === 'comp') {
              let name_ = ""
              if(compValProcess){
                name_ = compValProcessName
              }else{
                name_ = $('#EBDisplayButtonID').attr('data-name')
              }
              if (typeof (name_) === 'undefined') {
                name_ = $('#FileName').attr('data-experimentName')
              }
              $.ajax({
                url: `/users/${urlPath}/computationModule/`,
                data: {
                  operation: 'run_stepDelimitColumn',
                  element_id: uID,
                  model_name: name_,
                  data_id: dataID
                },
                type: 'POST',
                dataType: 'json',
                success: function (data) {
                  const jobId = data.job_id
                  const runStepBtnId = ''
                  const runStepBtnLoadId = ''
                  fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

                  if (previewString.length > 30) {
                    myTruncatedString = previewString.substring(0, 30) + '...'
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                  } else {
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                    myTruncatedString = previewString
                  }
                  $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
                },
                error: function () {
                  Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                }
              })
            }
          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          }
        })
      } else if (String(cDict.Operation) === 'Minute') {

        $.ajax({
          url: `/users/${urlPath}/computationModule/`,
          data: {
            configList: JSON.stringify({data1:name_, data2:cDict.element_id, data3:configDict,elementName:elementName}),
            operation: 'save_buttonCompareColumn',
            data_id: dataID
          },
          type: 'POST',
          dataType: 'json',
          success: function (context) {
            Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});

            if (String(dataID) === 'datamgm') {
              if (previewString.length > 30) {
                myTruncatedString = previewString.substring(0, 30) + '...'
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
              } else {
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                myTruncatedString = previewString
              }
              $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
            }

            if (String(dataID) === 'comp') {
              let name_ = ""
              if(compValProcess){
                name_ = compValProcessName
              }else{
                name_ = $('#EBDisplayButtonID').attr('data-name')
              }
              if (typeof (name_) === 'undefined') {
                name_ = $('#FileName').attr('data-experimentName')
              }
              $.ajax({
                url: `/users/${urlPath}/computationModule/`,
                data: {
                  operation: 'run_stepDelimitColumn',
                  element_id: uID,
                  model_name: name_,
                  data_id: dataID
                },
                type: 'POST',
                dataType: 'json',
                success: function (data) {
                  const jobId = data.job_id
                  const runStepBtnId = ''
                  const runStepBtnLoadId = ''
                  fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

                  if (previewString.length > 30) {
                    myTruncatedString = previewString.substring(0, 30) + '...'
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                  } else {
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                    myTruncatedString = previewString
                  }
                  $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
                },
                error: function () {
                  Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                }
              })
            }
          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          }
        })
      } else if (String(cDict.Operation) === 'Month') {

        $.ajax({
          url: `/users/${urlPath}/computationModule/`,
          data: {
            configList: JSON.stringify({data1:name_, data2:cDict.element_id, data3:configDict,elementName:elementName}),
            operation: 'save_buttonCompareColumn',
            data_id: dataID
          },
          type: 'POST',
          dataType: 'json',
          success: function (context) {
            Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});

            if (String(dataID) === 'datamgm') {
              if (previewString.length > 30) {
                myTruncatedString = previewString.substring(0, 30) + '...'
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
              } else {
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                myTruncatedString = previewString
              }
              $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
            }

            if (String(dataID) === 'comp') {
              let name_ = ""
              if(compValProcess){
                name_ = compValProcessName
              }else{
                name_ = $('#EBDisplayButtonID').attr('data-name')
              }
              if (typeof (name_) === 'undefined') {
                name_ = $('#FileName').attr('data-experimentName')
              }
              $.ajax({
                url: `/users/${urlPath}/computationModule/`,
                data: {
                  operation: 'run_stepDelimitColumn',
                  element_id: uID,
                  model_name: name_,
                  data_id: dataID
                },
                type: 'POST',
                dataType: 'json',
                success: function (data) {
                  const jobId = data.job_id
                  const runStepBtnId = ''
                  const runStepBtnLoadId = ''
                  fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

                  if (previewString.length > 30) {
                    myTruncatedString = previewString.substring(0, 30) + '...'
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                  } else {
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                    myTruncatedString = previewString
                  }
                  $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
                },
                error: function () {
                  Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                }
              })
            }
          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          }
        })
      } else if (String(cDict.Operation) === 'Now') {

        $.ajax({
          url: `/users/${urlPath}/computationModule/`,
          data: {
            configList: JSON.stringify({data1:name_, data2:cDict.element_id, data3:configDict,elementName:elementName}),
            operation: 'save_buttonCompareColumn',
            data_id: dataID
          },
          type: 'POST',
          dataType: 'json',
          success: function (context) {
            Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});

            if (String(dataID) === 'datamgm') {
              if (previewString.length > 30) {
                myTruncatedString = previewString.substring(0, 30) + '...'
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
              } else {
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                myTruncatedString = previewString
              }
              $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
            }

            if (String(dataID) === 'comp') {
              let name_ = ""
              if(compValProcess){
                name_ = compValProcessName
              }else{
                name_ = $('#EBDisplayButtonID').attr('data-name')
              }
              if (typeof (name_) === 'undefined') {
                name_ = $('#FileName').attr('data-experimentName')
              }
              $.ajax({
                url: `/users/${urlPath}/computationModule/`,
                data: {
                  operation: 'run_stepDelimitColumn',
                  element_id: uID,
                  model_name: name_,
                  data_id: dataID
                },
                type: 'POST',
                dataType: 'json',
                success: function (data) {
                  const jobId = data.job_id
                  const runStepBtnId = ''
                  const runStepBtnLoadId = ''
                  fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

                  if (previewString.length > 30) {
                    myTruncatedString = previewString.substring(0, 30) + '...'
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                  } else {
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                    myTruncatedString = previewString
                  }
                  $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
                },
                error: function () {
                  Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                }
              })
            }
          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          }
        })
      } else if (String(cDict.Operation) === 'Second') {

        $.ajax({
          url: `/users/${urlPath}/computationModule/`,
          data: {
            configList: JSON.stringify({data1:name_, data2:cDict.element_id, data3:configDict,elementName:elementName}),
            operation: 'save_buttonCompareColumn',
            data_id: dataID
          },
          type: 'POST',
          dataType: 'json',
          success: function (context) {
            Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});

            if (String(dataID) === 'datamgm') {
              if (previewString.length > 30) {
                myTruncatedString = previewString.substring(0, 30) + '...'
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
              } else {
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                myTruncatedString = previewString
              }
              $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
            }

            if (String(dataID) === 'comp') {
              let name_ = ""
              if(compValProcess){
                name_ = compValProcessName
              }else{
                name_ = $('#EBDisplayButtonID').attr('data-name')
              }
              if (typeof (name_) === 'undefined') {
                name_ = $('#FileName').attr('data-experimentName')
              }
              $.ajax({
                url: `/users/${urlPath}/computationModule/`,
                data: {
                  operation: 'run_stepDelimitColumn',
                  element_id: uID,
                  model_name: name_,
                  data_id: dataID
                },
                type: 'POST',
                dataType: 'json',
                success: function (data) {
                  const jobId = data.job_id
                  const runStepBtnId = ''
                  const runStepBtnLoadId = ''
                  fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

                  if (previewString.length > 30) {
                    myTruncatedString = previewString.substring(0, 30) + '...'
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                  } else {
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                    myTruncatedString = previewString
                  }
                  $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
                },
                error: function () {
                  Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                }
              })
            }
          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          }
        })
      } else if (String(cDict.Operation) === 'Time') {

        $.ajax({
          url: `/users/${urlPath}/computationModule/`,
          data: {
            configList: JSON.stringify({data1:name_, data2:cDict.element_id, data3:configDict,elementName:elementName}),
            operation: 'save_buttonCompareColumn',
            data_id: dataID
          },
          type: 'POST',
          dataType: 'json',
          success: function (context) {
            Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});

            if (String(dataID) === 'datamgm') {
              if (previewString.length > 30) {
                myTruncatedString = previewString.substring(0, 30) + '...'
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
              } else {
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                myTruncatedString = previewString
              }
              $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
            }

            if (String(dataID) === 'comp') {
              let name_ = ""
              if(compValProcess){
                name_ = compValProcessName
              }else{
                name_ = $('#EBDisplayButtonID').attr('data-name')
              }
              if (typeof (name_) === 'undefined') {
                name_ = $('#FileName').attr('data-experimentName')
              }
              $.ajax({
                url: `/users/${urlPath}/computationModule/`,
                data: {
                  operation: 'run_stepDelimitColumn',
                  element_id: uID,
                  model_name: name_,
                  data_id: dataID
                },
                type: 'POST',
                dataType: 'json',
                success: function (data) {
                  const jobId = data.job_id
                  const runStepBtnId = ''
                  const runStepBtnLoadId = ''
                  fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

                  if (previewString.length > 30) {
                    myTruncatedString = previewString.substring(0, 30) + '...'
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                  } else {
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                    myTruncatedString = previewString
                  }
                  $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
                },
                error: function () {
                  Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                }
              })
            }
          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          }
        })
      } else if (String(cDict.Operation) === 'Today') {

        $.ajax({
          url: `/users/${urlPath}/computationModule/`,
          data: {
            configList: JSON.stringify({data1:name_, data2:cDict.element_id, data3:configDict,elementName:elementName}),
            operation: 'save_buttonCompareColumn',
            data_id: dataID
          },
          type: 'POST',
          dataType: 'json',
          success: function (context) {
            Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});

            if (String(dataID) === 'datamgm') {
              if (previewString.length > 30) {
                myTruncatedString = previewString.substring(0, 30) + '...'
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
              } else {
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                myTruncatedString = previewString
              }
              $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
            }

            if (String(dataID) === 'comp') {
              let name_ = ""
              if(compValProcess){
                name_ = compValProcessName
              }else{
                name_ = $('#EBDisplayButtonID').attr('data-name')
              }
              if (typeof (name_) === 'undefined') {
                name_ = $('#FileName').attr('data-experimentName')
              }
              $.ajax({
                url: `/users/${urlPath}/computationModule/`,
                data: {
                  operation: 'run_stepDelimitColumn',
                  element_id: uID,
                  model_name: name_,
                  data_id: dataID
                },
                type: 'POST',
                dataType: 'json',
                success: function (data) {
                  const jobId = data.job_id
                  const runStepBtnId = ''
                  const runStepBtnLoadId = ''
                  fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

                  if (previewString.length > 30) {
                    myTruncatedString = previewString.substring(0, 30) + '...'
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                  } else {
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                    myTruncatedString = previewString
                  }
                  $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
                },
                error: function () {
                  Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                }
              })
            }
          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          }
        })
      } else if (String(cDict.Operation) === 'Weekday') {

        $.ajax({
          url: `/users/${urlPath}/computationModule/`,
          data: {
            configList: JSON.stringify({data1:name_, data2:cDict.element_id, data3:configDict,elementName:elementName}),
            operation: 'save_buttonCompareColumn',
            data_id: dataID
          },
          type: 'POST',
          dataType: 'json',
          success: function (context) {
            Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});

            if (String(dataID) === 'datamgm') {
              if (previewString.length > 30) {
                myTruncatedString = previewString.substring(0, 30) + '...'
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
              } else {
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                myTruncatedString = previewString
              }
              $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
            }

            if (String(dataID) === 'comp') {
              let name_ = ""
              if(compValProcess){
                name_ = compValProcessName
              }else{
                name_ = $('#EBDisplayButtonID').attr('data-name')
              }
              if (typeof (name_) === 'undefined') {
                name_ = $('#FileName').attr('data-experimentName')
              }
              $.ajax({
                url: `/users/${urlPath}/computationModule/`,
                data: {
                  operation: 'run_stepDelimitColumn',
                  element_id: uID,
                  model_name: name_,
                  data_id: dataID
                },
                type: 'POST',
                dataType: 'json',
                success: function (data) {
                  const jobId = data.job_id
                  const runStepBtnId = ''
                  const runStepBtnLoadId = ''
                  fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

                  if (previewString.length > 30) {
                    myTruncatedString = previewString.substring(0, 30) + '...'
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                  } else {
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                    myTruncatedString = previewString
                  }
                  $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
                },
                error: function () {
                  Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                }
              })
            }
          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          }
        })
      } else if (String(cDict.Operation) === 'Weeknum') {

        $.ajax({
          url: `/users/${urlPath}/computationModule/`,
          data: {
            configList: JSON.stringify({data1:name_, data2:cDict.element_id, data3:configDict,elementName:elementName}),
            operation: 'save_buttonCompareColumn',
            data_id: dataID
          },
          type: 'POST',
          dataType: 'json',
          success: function (context) {
            Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});

            if (String(dataID) === 'datamgm') {
              if (previewString.length > 30) {
                myTruncatedString = previewString.substring(0, 30) + '...'
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
              } else {
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                myTruncatedString = previewString
              }
              $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
            }

            if (String(dataID) === 'comp') {
              let name_ = ""
              if(compValProcess){
                name_ = compValProcessName
              }else{
                name_ = $('#EBDisplayButtonID').attr('data-name')
              }
              if (typeof (name_) === 'undefined') {
                name_ = $('#FileName').attr('data-experimentName')
              }
              $.ajax({
                url: `/users/${urlPath}/computationModule/`,
                data: {
                  operation: 'run_stepDelimitColumn',
                  element_id: uID,
                  model_name: name_,
                  data_id: dataID
                },
                type: 'POST',
                dataType: 'json',
                success: function (data) {
                  const jobId = data.job_id
                  const runStepBtnId = ''
                  const runStepBtnLoadId = ''
                  fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

                  if (previewString.length > 30) {
                    myTruncatedString = previewString.substring(0, 30) + '...'
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                  } else {
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                    myTruncatedString = previewString
                  }
                  $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
                },
                error: function () {
                  Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                }
              })
            }
          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          }
        })
      } else if (String(cDict.Operation) === 'Year') {

        $.ajax({
          url: `/users/${urlPath}/computationModule/`,
          data: {
            configList: JSON.stringify({data1:name_, data2:cDict.element_id, data3:configDict,elementName:elementName}),
            operation: 'save_buttonCompareColumn',
            data_id: dataID
          },
          type: 'POST',
          dataType: 'json',
          success: function (context) {
            Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});

            if (String(dataID) === 'datamgm') {
              if (previewString.length > 30) {
                myTruncatedString = previewString.substring(0, 30) + '...'
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
              } else {
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                myTruncatedString = previewString
              }
              $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
            }

            if (String(dataID) === 'comp') {
              let name_ = ""
              if(compValProcess){
                name_ = compValProcessName
              }else{
                name_ = $('#EBDisplayButtonID').attr('data-name')
              }
              if (typeof (name_) === 'undefined') {
                name_ = $('#FileName').attr('data-experimentName')
              }
              $.ajax({
                url: `/users/${urlPath}/computationModule/`,
                data: {
                  operation: 'run_stepDelimitColumn',
                  element_id: uID,
                  model_name: name_,
                  data_id: dataID
                },
                type: 'POST',
                dataType: 'json',
                success: function (data) {
                  const jobId = data.job_id
                  const runStepBtnId = ''
                  const runStepBtnLoadId = ''
                  fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

                  if (previewString.length > 30) {
                    myTruncatedString = previewString.substring(0, 30) + '...'
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                  } else {
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                    myTruncatedString = previewString
                  }
                  $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
                },
                error: function () {
                  Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                }
              })
            }
          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          }
        })
      } else if (String(cDict.Operation) === 'Yearfrac') {

        $.ajax({
          url: `/users/${urlPath}/computationModule/`,
          data: {
            configList: JSON.stringify({data1:name_, data2:cDict.element_id, data3:configDict,elementName:elementName}),
            operation: 'save_buttonCompareColumn',
            data_id: dataID
          },
          type: 'POST',
          dataType: 'json',
          success: function (context) {
            Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});

            if (String(dataID) === 'datamgm') {
              if (previewString.length > 30) {
                myTruncatedString = previewString.substring(0, 30) + '...'
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
              } else {
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                myTruncatedString = previewString
              }
              $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
            }

            if (String(dataID) === 'comp') {
              let name_ = ""
              if(compValProcess){
                name_ = compValProcessName
              }else{
                name_ = $('#EBDisplayButtonID').attr('data-name')
              }
              if (typeof (name_) === 'undefined') {
                name_ = $('#FileName').attr('data-experimentName')
              }
              $.ajax({
                url: `/users/${urlPath}/computationModule/`,
                data: {
                  operation: 'run_stepDelimitColumn',
                  element_id: uID,
                  model_name: name_,
                  data_id: dataID
                },
                type: 'POST',
                dataType: 'json',
                success: function (data) {
                  const jobId = data.job_id
                  const runStepBtnId = ''
                  const runStepBtnLoadId = ''
                  fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

                  if (previewString.length > 30) {
                    myTruncatedString = previewString.substring(0, 30) + '...'
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                  } else {
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                    myTruncatedString = previewString
                  }
                  $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
                },
                error: function () {
                  Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                }
              })
            }
          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          }
        })
      } else if (String(cDict.Operation) === 'Networkdays') {

        $.ajax({
          url: `/users/${urlPath}/computationModule/`,
          data: {
            configList: JSON.stringify({data1:name_, data2:cDict.element_id, data3:configDict,elementName:elementName}),
            operation: 'save_buttonCompareColumn',
            data_id: dataID
          },
          type: 'POST',
          dataType: 'json',
          success: function (context) {
            window.alert('Configuration saved successfully')

            if (String(dataID) === 'datamgm') {
              if (previewString.length > 30) {
                myTruncatedString = previewString.substring(0, 30) + '...'
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
              } else {
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                myTruncatedString = previewString
              }
              $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
            }

            if (String(dataID) === 'comp') {
              let name_ = ""
              if(compValProcess){
                name_ = compValProcessName
              }else{
                name_ = $('#EBDisplayButtonID').attr('data-name')
              }
              if (typeof (name_) === 'undefined') {
                name_ = $('#FileName').attr('data-experimentName')
              }
              $.ajax({
                url: `/users/${urlPath}/computationModule/`,
                data: {
                  operation: 'run_stepnetworkdays',
                  element_id: uID,
                  model_name: name_,
                  data_id: dataID
                },
                type: 'POST',
                dataType: 'json',
                success: function (data) {
                  const jobId = data.job_id
                  const runStepBtnId = ''
                  const runStepBtnLoadId = ''
                  fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

                  if (previewString.length > 30) {
                    myTruncatedString = previewString.substring(0, 30) + '...'
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                  } else {
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                    myTruncatedString = previewString
                  }
                  $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
                },
                error: function () {
                  window.alert('Error')
                }
              })
            }
          },
          error: function () {
            window.alert('Error')
          }
        })
      } else if (String(cDict.Operation) === 'Networkdays.Intl') {

        $.ajax({
          url: `/users/${urlPath}/computationModule/`,
          data: {
            configList: JSON.stringify({data1:name_, data2:cDict.element_id, data3:configDict,elementName:elementName}),
            operation: 'save_buttonCompareColumn',
            data_id: dataID
          },
          type: 'POST',
          dataType: 'json',
          success: function (context) {
            window.alert('Configuration saved successfully')

            if (String(dataID) === 'datamgm') {
              if (previewString.length > 30) {
                myTruncatedString = previewString.substring(0, 30) + '...'
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
              } else {
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                myTruncatedString = previewString
              }
              $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
            }

            if (String(dataID) === 'comp') {
              let name_ = ""
              if(compValProcess){
                name_ = compValProcessName
              }else{
                name_ = $('#EBDisplayButtonID').attr('data-name')
              }
              if (typeof (name_) === 'undefined') {
                name_ = $('#FileName').attr('data-experimentName')
              }
              $.ajax({
                url: `/users/${urlPath}/computationModule/`,
                data: {
                  operation: 'run_stepnetworkdays',
                  element_id: uID,
                  model_name: name_,
                  data_id: dataID
                },
                type: 'POST',
                dataType: 'json',
                success: function (data) {
                  const jobId = data.job_id
                  const runStepBtnId = ''
                  const runStepBtnLoadId = ''
                  fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

                  if (previewString.length > 30) {
                    myTruncatedString = previewString.substring(0, 30) + '...'
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                  } else {
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                    myTruncatedString = previewString
                  }
                  $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
                },
                error: function () {
                  window.alert('Error')
                }
              })
            }
          },
          error: function () {
            window.alert('Error')
          }
        })
      } else if (String(cDict.Operation) === 'Workdays') {

        $.ajax({
          url: `/users/${urlPath}/computationModule/`,
          data: {
            configList: JSON.stringify({data1:name_, data2:cDict.element_id, data3:configDict,elementName:elementName}),
            operation: 'save_buttonCompareColumn',
            data_id: dataID
          },
          type: 'POST',
          dataType: 'json',
          success: function (context) {
            window.alert('Configuration saved successfully')

            if (String(dataID) === 'datamgm') {
              if (previewString.length > 30) {
                myTruncatedString = previewString.substring(0, 30) + '...'
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
              } else {
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                myTruncatedString = previewString
              }
              $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
            }

            if (String(dataID) === 'comp') {
              let name_ = ""
              if(compValProcess){
                name_ = compValProcessName
              }else{
                name_ = $('#EBDisplayButtonID').attr('data-name')
              }
              if (typeof (name_) === 'undefined') {
                name_ = $('#FileName').attr('data-experimentName')
              }
              $.ajax({
                url: `/users/${urlPath}/computationModule/`,
                data: {
                  operation: 'run_stepnetworkdays',
                  element_id: uID,
                  model_name: name_,
                  data_id: dataID
                },
                type: 'POST',
                dataType: 'json',
                success: function (data) {
                  const jobId = data.job_id
                  const runStepBtnId = ''
                  const runStepBtnLoadId = ''
                  fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

                  if (previewString.length > 30) {
                    myTruncatedString = previewString.substring(0, 30) + '...'
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                  } else {
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                    myTruncatedString = previewString
                  }
                  $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
                },
                error: function () {
                  window.alert('Error')
                }
              })
            }
          },
          error: function () {
            window.alert('Error')
          }
        })
      } else if (String(cDict.Operation) === 'Workdays.Intl') {

        $.ajax({
          url: `/users/${urlPath}/computationModule/`,
          data: {
            configList: JSON.stringify({data1:name_, data2:cDict.element_id, data3:configDict,elementName:elementName}),
            operation: 'save_buttonCompareColumn',
            data_id: dataID
          },
          type: 'POST',
          dataType: 'json',
          success: function (context) {
            window.alert('Configuration saved successfully')

            if (String(dataID) === 'datamgm') {
              if (previewString.length > 30) {
                myTruncatedString = previewString.substring(0, 30) + '...'
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
              } else {
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                myTruncatedString = previewString
              }
              $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
            }

            if (String(dataID) === 'comp') {
              let name_ = ""
              if(compValProcess){
                name_ = compValProcessName
              }else{
                name_ = $('#EBDisplayButtonID').attr('data-name')
              }
              if (typeof (name_) === 'undefined') {
                name_ = $('#FileName').attr('data-experimentName')
              }
              $.ajax({
                url: `/users/${urlPath}/computationModule/`,
                data: {
                  operation: 'run_stepnetworkdays',
                  element_id: uID,
                  model_name: name_,
                  data_id: dataID
                },
                type: 'POST',
                dataType: 'json',
                success: function (data) {
                  const jobId = data.job_id
                  const runStepBtnId = ''
                  const runStepBtnLoadId = ''
                  fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

                  if (previewString.length > 30) {
                    myTruncatedString = previewString.substring(0, 30) + '...'
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
                  } else {
                    $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                    $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                    myTruncatedString = previewString
                  }
                  $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
                },
                error: function () {
                  window.alert('Error')
                }
              })
            }
          },
          error: function () {
            window.alert('Error')
          }
        })
      }
  } else {
    let name_ = ""
    if(compValProcess){
      name_ = compValProcessName
    }else{
      name_ = $('#EBDisplayButtonID').attr('data-name')
    }
    let dataID = 'comp'
    let elementName = ''

    if (typeof (name_) === 'undefined') {
      name_ = $('#FileName').attr('data-experimentName')
      if (typeof (name_) === 'undefined') {
        dataID = 'datamgm'
        if ($('#tname').val() && String(idenFlag) !== 'add') {
          name_ = $('#tname').val()
        } else if (String(idenFlag) === 'add' || String(idenFlag) === 'edit') {
          name_ = $('.dataElements').find('p').text()
        } else if (listViewComp == true) {
          name_ = listViewModelName
        }
      }
    }

    if (String(dataID) === 'datamgm' && listViewComp == false) {
      elementName = name_ + selectedCol + Math.floor((Math.random() * 10000000000) + 1)
    } else if (String(dataID) === 'datamgm' && listViewComp == true) {
      elementName = name_ + listViewCompCol + Math.floor((Math.random() * 10000000000) + 1)
    }
    else {
      elementName = uID
    }

    $.ajax({
      url: `/users/${urlPath}/computationModule/`,
      data: {
        model_name: name_,
        element_id: uID,
        element_name: elementName,
        configDict: JSON.stringify(configDict),
        operation: 'save_config_data',
        data_id: dataID
      },
      type: 'POST',
      dataType: 'json',
      success: function (context) {
        Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});

        if (String(dataID) === 'datamgm') {
          if (previewString.length > 30) {
            myTruncatedString = previewString.substring(0, 30) + '...'
            $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
            $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
          } else {
            $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
            $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
            myTruncatedString = previewString
          }
          $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
        }
        if (String(dataID) === 'comp') {
          $.ajax({
            url: `/users/${urlPath}/computationModule/`,
            data: {
              operation: 'run_step_merge_and_join',
              element_id: uID,
              model_name: name_
            },
            type: 'POST',
            dataType: 'json',
            success: function (data) {
              const jobId = data.job_id
              const runStepBtnId = ''
              const runStepBtnLoadId = ''
              fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)

              if (previewString.length > 30) {
                myTruncatedString = previewString.substring(0, 30) + '...'
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', `popupOpen();takeFuncInput('${name}','${uID}','${ind}',this)`)
              } else {
                $('#functionPreviews').find('.function').eq(ind).find('p').text(previewString)
                $('#functionPreviews').find('.function').eq(ind).attr('onclick', '')
                myTruncatedString = previewString
              }
              $('#functionPreviews').find('.function').eq(ind).find('h2').text(myTruncatedString)
            },
            error: function () {
              Swal.fire({icon: 'error',text: 'Error! Please try again.'});
            }
          })
        }
      },
      error: function () {
        Swal.fire({icon: 'error',text: 'Error! Please try again.'});
      }
    })
  }
  $("#EBDisplayButtonID").attr("data-tablepc", tableName)
}

const validate = (mDict) => { // eslint-disable-line no-unused-vars
  validFlag = true

  if (String(mDict.Operation) === 'Column sum' || String(mDict.Operation) === 'Column subtraction' || String(mDict.Operation) === 'Column multiplication' || String(mDict.Operation) === 'Column division') {
    if ((String(mDict.Column_sum1.length) === '1' && String(mDict.Column_sum2) === '') || (String(mDict.Column_sum1.length) === '0' && String(mDict.Column_sum2) !== '')) {
      Swal.fire({icon: 'warning',text:"Kindly fill in all the values." });
      validFlag = false
    } else if (mDict.Column_sum1.length > 1 && String(mDict.Column_sum2) !== '') {
      Swal.fire({icon: 'warning',text: 'Kindly remove the input value as two columns are selected.'});
    } else if (String(mDict.Target_Column1) === '') {
      Swal.fire({icon: 'warning',text:"Kindly fill in the target column name." });
    } else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }
  } else if (String(mDict.Operation) === 'Cell sum' || String(mDict.Operation) === 'Cell subtraction' || String(mDict.Operation) === 'Cell multiplication' || String(mDict.Operation) === 'Cell division') {
    if (String(mDict.Cell_sum3) === '') {
      if (String(mDict.Cell_11.length) === '0' || String(mDict.Cell_12.length) === '0' || String(mDict.Cell_21.length) === '0' ||
        String(mDict.Cell_22.length) === '0' || String(mDict.Target_Cell_11.length) === 0 || String(mDict.Target_Cell_22.length) === '0') {
        Swal.fire({icon: 'warning',text:"Kindly fill in all the values" });
        validFlag = false
      }
    } else if (String(mDict.Cell_sum3) !== '') {
      if (String(mDict.Cell_11.length) === '0' || String(mDict.Cell_12.length) === '0' || String(mDict.Target_Cell_11.length) === '0' || String(mDict.Target_Cell_22.length) === '0') {
        Swal.fire({icon: 'warning',text:"Kindly fill in all the values" });
        validFlag = false
      } else {
        Swal.fire({icon: 'success',text: 'Successfully validated!'});
      }
    } else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }
  } else if (String(mDict.Operation) === 'Row sum' || String(mDict.Operation) === 'Row subtraction' || String(mDict.Operation) === 'Row multiplication' || String(mDict.Operation) === 'Row division') {
    if ((String(mDict.Row_sum1.length) === '1' && String(mDict.Row_sum2) === '') || (String(mDict.Row_sum1.length) === '0' && String(mDict.Row_sum2) !== '')) {
      Swal.fire({icon: 'warning',text:"Kindly fill in all the values" });
      validFlag = false
    } else if (String(mDict.Target_Column1) === '') {
      Swal.fire({icon: 'warning',text:"Kindly fill in the target column name" });
    } else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }
  } else if (String(mDict.Operation) === 'Square root') {
    if ((String(mDict.Root_Operation1) !== '' && String(mDict.Root_Operation2) === '') || (String(mDict.Root_Operation1) === '' && String(mDict.Root_Operation2) !== '')) {
      Swal.fire({icon: 'warning',text:'Kindly fill in values for the Root Operation.'});
      validFlag = false
    } else if (String(mDict.Target_Column1) === '') {
      Swal.fire({icon: 'warning',text:"Kindly fill in the target column name" });
    } else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }
  } else if (String(mDict.Operation) === 'Log') {
    if (
      (String(mDict.Exponential1) !== '')
    ) {
      if (
        (String(mDict.Exponential1) === '')
      ) {
        Swal.fire({icon: 'warning',text:'Kindly fill in values for the Exponential Operation.'});
        validFlag = false
      } else if (String(mDict.Target_Column1) === '') {
        Swal.fire({icon: 'warning',text:"Kindly fill in the target column name" });
      } else {
        Swal.fire({icon: 'success',text: 'Successfully validated!'});
      }
    } else
      if (
        (String(mDict.Natural_Log1) !== '')
      ) {
        if (
          (String(mDict.Natural_Log1) === '')
        ) {
          Swal.fire({icon: 'warning',text:'Kindly fill in values for the Natural Log Operation.'});
          validFlag = false
        } else if (String(mDict.Target_Column1) === '') {
          Swal.fire({icon: 'warning',text:"Kindly fill in the target column name." });
        } else {
          Swal.fire({icon: 'success',text: 'Successfully validated!'});
        }
      } else
        if (
          ((String(mDict.Base_Log1) !== '' && String(mDict.Log_Base_value2) !== ''))
        ) {
          if (
            ((String(mDict.Base_Log1) === '' && String(mDict.Log_Base_value2) !== '') || (String(mDict.Base_Log1) !== '' && String(mDict.Log_Base_value2) === ''))
          ) {
            Swal.fire({icon: 'warning',text:'Kindly fill in values for the Base Log Operation.'});
            validFlag = false
          } else if (String(mDict.Target_Column1) === '') {
            Swal.fire({icon: 'warning',text:"Kindly fill in the target column name." });
          } else {
            Swal.fire({icon: 'success',text: 'Successfully validated!'});
          }
        }
  } else if (String(mDict.Operation) === 'Round') {
    if (
      ((String(mDict.Ceiling1) !== '' || String(mDict.Ceiling_Significance_Multiple2) !== ''))
    ) {
      if (
        ((String(mDict.Ceiling1) === '' && String(mDict.Ceiling_Significance_Multiple2) !== '') || (String(mDict.Ceiling1) !== '' && String(mDict.Ceiling_Significance_Multiple2) === ''))
      ) {
        Swal.fire({icon: 'warning',text:'Kindly fill in values for the Ceiling Operation.'});
        validFlag = false
      } else if (String(mDict.Target_Column1) === '') {
        Swal.fire({icon: 'warning',text:"Kindly fill in the target column name." });
      } else {
        Swal.fire({icon: 'success',text: 'Successfully validated!'});
      }
    } else
      if (
        ((String(mDict.Floor1) !== '' || String(mDict.Floor_Significance_Multiple2) !== ''))
      ) {
        if (
          ((String(mDict.Floor1) === '' && String(mDict.Floor_Significance_Multiple2) !== '') || (String(mDict.Floor1) !== '' && String(mDict.Floor_Significance_Multiple2) === ''))
        ) {
          Swal.fire({icon: 'warning',text:'Kindly fill in values for the Floor Operation.'});
          validFlag = false
        } else if (String(mDict.Target_Column1) === '') {
          Swal.fire({icon: 'warning',text:"Kindly fill in the target column name." });
        } else {
          Swal.fire({icon: 'success',text: 'Successfully validated!'});
        }
      } else
        if (
          String(mDict.Odd1) !== ''
        ) {
          if (
            String(mDict.Odd1) === ''
          ) {
            Swal.fire({icon: 'warning',text:'Kindly fill in values for the Odd Operation.'});
            validFlag = false
          } else if (String(mDict.Target_Column1) === '') {
            Swal.fire({icon: 'warning',text:"Kindly fill in the target column name." });
          } else {
            Swal.fire({icon: 'success',text: 'Successfully validated!'});
          }
        } else
          if (
            String(mDict.Even1) !== ''
          ) {
            if (
              String(mDict.Even1) === ''
            ) {
              Swal.fire({icon: 'warning',text:'Kindly fill in values for the Even Operation.'});
              validFlag = false
            } else if (String(mDict.Target_Column1) === '') {
              Swal.fire({icon: 'warning',text:"Kindly fill in the target column name." });
            } else {
              Swal.fire({icon: 'success',text: 'Successfully validated!'});
            }
          } else
            if (
              ((String(mDict.Round1) !== '' || String(mDict.No_of_Decimals2) !== ''))
            ) {
              if (
                ((String(mDict.Round1) === '' && String(mDict.No_of_Decimals2) !== '') || (String(mDict.Round1) !== '' && String(mDict.No_of_Decimals2) === ''))
              ) {
                Swal.fire({icon: 'warning',text:'Kindly fill in values for the Round Operation.'});
                validFlag = false
              } else if (String(mDict.Target_Column1) === '') {
                Swal.fire({icon: 'warning',text:"Kindly fill in the target column name." });
              } else {
                Swal.fire({icon: 'success',text: 'Successfully validated!'});
              }
            } else
              if (
                String(mDict.Round_Up1) !== ''
              ) {
                if (
                  String(mDict.Round_Up1) === ''
                ) {
                  wal.fire({icon: 'warning',text:'Kindly fill in values for the Round Up Operation.'});
                  validFlag = false
                } else if (String(mDict.Target_Column1) === '') {
                  Swal.fire({icon: 'warning',text:"Kindly fill in the target column name." });
                } else {
                  Swal.fire({icon: 'success',text: 'Successfully validated!'});
                }
              } else
                if (
                  String(mDict.Round_Down1) !== ''
                ) {
                  if (
                    String(mDict.Round_Down1) === ''
                  ) {
                    wal.fire({icon: 'warning',text:'Kindly fill in values for the Round down Operation.'});
                    validFlag = false
                  } else if (String(mDict.Target_Column1) === '') {
                    Swal.fire({icon: 'warning',text:"Kindly fill in the target column name." });
                  } else {
                    Swal.fire({icon: 'success',text: 'Successfully validated!'});
                  }
                } else
                  if (
                    String(mDict.Truncate1) !== ''
                  ) {
                    if (
                      String(mDict.Truncate1) === ''
                    ) {
                      Swal.fire({icon: 'warning',text:'Kindly fill in values for the Truncate Operation.'});
                      validFlag = false
                    } else if (String(mDict.Target_Column1) === '') {
                      Swal.fire({icon: 'warning',text:"Kindly fill in the target column name." });
                    } else {
                      Swal.fire({icon: 'success',text: 'Successfully validated!'});
                    }
                  }
  } else if (String(mDict.Operation) === 'Left Join') {
    if (String(mDict.Left_join_Data13.length) === '0' || String(mDict.Left_join_Data24.length) === '0' || String(mDict.Left_join_on_Data11) === '' || String(mDict.Left_join_on_Data22) === '') {
      Swal.fire({icon: 'warning',text:'Kindly fill in values for the Left Join Operation.'});
      validFlag = false
    } else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }
  } else if (String(mDict.Operation) === 'Right Join') {
    if (String(mDict.Right_join_Data13.length) === '0' || String(mDict.Right_join_Data24.length) === '0' || String(mDict.Right_join_on_Data22) === '' || String(mDict.Right_join_on_Data11) === '') {
      Swal.fire({icon: 'warning',text:'Kindly fill values for Right Join Operation.'});
      validFlag = false
    } else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }
  } else if (String(mDict.Operation) === 'Inner Join') {
    if (String(mDict.Inner_join_Data13.length) === '0' || String(mDict.Inner_join_Data24.length) === '0' || String(mDict.Inner_join_on_Data11) === '' || String(mDict.Inner_join_on_Data22) === '') {
      Swal.fire({icon: 'warning',text:'Kindly fill values for Inner Join Operation.'});
      validFlag = false
    } else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }
  } else if (String(mDict.Operation) === 'Outer Join') {
    if (String(mDict.Outer_join_Data13.length) === '0' || String(mDict.Outer_join_Data24.length) === '0' || String(mDict.Outer_join_on_Data11) === '' || String(mDict.Outer_join_on_Data22) === '') {
      Swal.fire({icon: 'warning',text:'Kindly fill values for Outer Join Operation.'});
      validFlag = false
    } else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }
  } else if (String(mDict.Operation) === 'Append and Concatenate') {
    if (String(mDict.Target_Column1.length) === '0') {
      Swal.fire({icon: 'warning',text:'Kindly fill in values for the Append and Concatenate Operation. '});
      validFlag = false
    } else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }
  } else if (String(mDict.Operation) === 'Add Time Periods') {
    if (String(mDict.Days2.length) !== '0' && String(mDict.Months3.length) !== '0') {
      Swal.fire({icon: 'warning',text:'Kindly fill in values for the one option only.'});
    } else if (String(mDict.Days2.length) !== '0' && String(mDict.Years4.length) !== '0') {
      Swal.fire({icon: 'warning',text:'Kindly fill in values for the one option only.'});
    } else if (String(mDict.Months3.length) !== '0' && String(mDict.Years4.length) !== '0') {
      Swal.fire({icon: 'warning',text:'Kindly fill in values for the one option only.'});
    } else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }

  } else if (String(mDict.Operation) === 'Groupby') {
    if (String(mDict.Target_Column1.length) === '0') {
      Swal.fire({icon: 'warning',text:'Kindly fill in column value for the Group by.'});
      validFlag = false
    }
    else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }
  } else if (String(mDict.Operation) === 'Pivot') {
    if (String(mDict.Target_Column1.length) === '0' || String(mDict.Target_Column2.length) === '0' || String(mDict.Target_Column3.length) === '0') {
      Swal.fire({icon: 'warning',text:'Kindly fill in values for the Pivot Operation.'});
      validFlag = false
    }
    else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }
  } else if (String(mDict.Operation) === 'Unpivot') {
    if (String(mDict.Target_Column1.length) === '0'|| String(mDict.Target_Column2.length) === '0' || String(mDict.Target_Column3.length) === '0' || String(mDict.Target_Column4.length) === '0'){
      Swal.fire({icon: 'warning',text:'Kindly fill in values for the Unpivot Operation.'});
      validFlag = false
    }
    else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }

  } else if (String(mDict.Operation) === 'Concat Columns') {
    if (String(mDict.Target_Column1.length) === '0' || String(mDict.Target_Column2.length) === '0' || String(mDict.Target_Column3.length) === '0') {
      Swal.fire({icon: 'warning',text:'Kindly fill values for Concat Column Operation.'});
      validFlag = false
    }
    else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }
  } else if (String(mDict.Operation) === 'Rename and Drop') {
    if (String(mDict.Drop_Columns1.length) === '0' && $('#renameColumnContainer1').find('div.renameColumnGroup1').length == 0) {
      Swal.fire({icon: 'warning',text:'Kindly fill in values for the Rename and the Drop Operation.'});
      validFlag = false
    }
    else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }
  } else if (String(mDict.Operation) === 'Filter') {
    if ($('#filter-table_where_merge1').find('tr').length == 0) {
      Swal.fire({icon: 'warning',text:'Kindly fill in values for the Filter Operation.'});
      validFlag = false
    }
    else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }
  } else if (String(mDict.Operation) === 'Data Utilities') {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
  } else if (String(mDict.Operation) === 'Add Column') {
    if (mDict.Target_Column1 == "" && mDict.Target_Column2 == "" && mDict.Target_Column3 == "" && $('#filter-table_addCol_body').find('tr').length == 0) {
      Swal.fire({icon: 'warning',text:'Kindly fill in values for the Add Column Operation.'});
      validFlag = false
    }
    else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }
  } else if (String(mDict.Operation) === 'Sort') {
    if ($('#selectedSortColList').find('div').length == 0) {
      Swal.fire({icon: 'warning',text:'Kindly fill in values for the Sort Operation.'});
      validFlag = false
    }
    else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }
  } else if (String(mDict.Operation) === 'Fill Missing Values') {
    if (mDict.Select_Operation1 == "-" && mDict.Data_Table2 == "-" && mDict.Custom_value3 == "") {
      Swal.fire({icon: 'warning',text:'Kindly fill values for Missing Values Operation.'});
      validFlag = false
    }
    else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }
  } else if (String(mDict.Operation) === 'Sum Product') {
    if (mDict.Column_Group1.length == 0 && mDict.Column_Value2.length == 0) {
      Swal.fire({icon: 'warning',text:'Kindly fill in values for the Product Operation.'});
      validFlag = false
    }
    else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }
  } else if (String(mDict.Operation) === 'Weighted Average') {
    if (mDict.Column_Group1.length == 0 && mDict.Average_Value2 == "" && mDict.Average_Weight3 == "") {
      Swal.fire({icon: 'warning',text:'Kindly fill in values for the Weighted Average Operation.'});
      validFlag = false
    }
    else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }
  } else if (String(mDict.Operation) === 'Drop Duplicate') {
    if (mDict.Select_operation1 == "" && mDict.Data_table2.length == 0) {
      Swal.fire({icon: 'warning',text:'Kindly fill values for Drop Duplicate Operation.'});
      validFlag = false
    }
    else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }
  } else if (String(mDict.Operation) === 'Add Fix Column') {
    if (mDict.Input_Column2 == "" && mDict.Add_Column2 == "") {
      Swal.fire({icon: 'warning',text:'Kindly fill in values for the Add Fix Column Operation.'});
      validFlag = false
    }
    else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }
  }  else if (String(mDict.Operation) === 'Networkdays.Intl') {
    if (mDict.NetworkdaysIntl1 == "" && mDict.NetworkdaysIntl2 == "") {
      window.alert('Kindly fill values for Networkdays.Intl Operation !! ')
      validFlag = false
    }
    else {
      window.alert('Successfully validated !! ')
    }
  } else if (String(mDict.Operation) === 'Date') {
    if (mDict.Date1 == "" && mDict.Date2 == "" && mDict.Date3 == "") {
      Swal.fire({icon: 'warning',text:'Kindly fill in values for the Date Operation.'});
      validFlag = false
    }
    else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }
  } else if (String(mDict.Operation) === 'Day') {
    if (mDict.Day1 == "" && mDict.Day2 == "") {
      Swal.fire({icon: 'warning',text:'Kindly fill values for Day Operation.'});
      validFlag = false
    }
    else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }
  } else if (String(mDict.Operation) === 'Days') {
    if (mDict.Days1 == "" && mDict.Days2 == "" && mDict.Days3 == "") {
      Swal.fire({icon: 'warning',text:'Kindly fill in values for the Days Operation.'});
      validFlag = false
    }
    else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }
  } else if (String(mDict.Operation) === 'Edate') {
    if (mDict.Edate1 == "" && mDict.Edate2 == "" && mDict.Edate3 == "") {
      Swal.fire({icon: 'warning',text:'Kindly fill in values for the Edate Operation.'});
      validFlag = false
    }
    else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }
  } else if (String(mDict.Operation) === 'Workdays.Intl') {
    if (mDict.WorkdaysIntl1 == "" && mDict.WorkdaysIntl4 == "") {
      window.alert('Kindly fill values for Workdays.Intl Operation !! ')
      validFlag = false
    }
    else {
      window.alert('Successfully validated !! ')
    }
  } else if (String(mDict.Operation) === 'Days360') {
    if (mDict.Days3601 == "" && mDict.Days3602 == "" && mDict.Days3603 == "") {
      Swal.fire({icon: 'warning',text:'Kindly fill in values for the Days360 Operation.'});
      validFlag = false
    }
    else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }
  } else if (String(mDict.Operation) === 'Eomonth') {
    if (mDict.Eomonth1 == "" && mDict.Eomonth2 == "") {
      Swal.fire({icon: 'warning',text:'Kindly fill in values for the Eomonth Operation.'});
      validFlag = false
    }
    else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }
  } else if (String(mDict.Operation) === 'Hour') {
    if (mDict.Hour1 == "" && mDict.Hour2 == "") {
      Swal.fire({icon: 'warning',text:'Kindly fill in values for the Hour Operation.'});
      validFlag = false
    }
    else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }
  } else if (String(mDict.Operation) === 'Isoweeknum') {
    if (mDict.Isoweeknum1 == "" && mDict.Isoweeknum2 == "") {
      Swal.fire({icon: 'warning',text:'Kindly fill in values for the Isoweeknum Operation.'});
      validFlag = false
    }
    else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }
  } else if (String(mDict.Operation) === 'Minute') {
    if (mDict.Minute1 == "" && mDict.Minute2 == "") {
      Swal.fire({icon: 'warning',text:'Kindly fill in values for the Minute Operation.'});
      validFlag = false
    }
    else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }
  } else if (String(mDict.Operation) === 'Month') {
    if (mDict.Month1 == "" && mDict.Month2 == "") {
      Swal.fire({icon: 'warning',text:'Kindly fill in values for the Month Operation.'});
      validFlag = false
    }
    else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }
  } else if (String(mDict.Operation) === 'Now') {
    if (mDict.Now1 == "") {
      Swal.fire({icon: 'warning',text:'Kindly fill in values for the Now Operation.'});
      validFlag = false
    }
    else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }
  } else if (String(mDict.Operation) === 'Second') {
    if (mDict.Second1 == "" && mDict.Second2 == "") {
      Swal.fire({icon: 'warning',text:'Kindly fill in values for the Second Operation'});
      validFlag = false
    }
    else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }
  } else if (String(mDict.Operation) === 'Time') {
    if (mDict.Time1 == "" && mDict.Time2 == "" && mDict.Time3 == "") {
      Swal.fire({icon: 'warning',text:'Kindly fill in values for the Time Operation'});
      validFlag = false
    }
    else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }
  } else if (String(mDict.Operation) === 'Today') {
    if (mDict.Today1 == "") {
      Swal.fire({icon: 'warning',text:'Kindly fill in values for the Today Operation.'});
      validFlag = false
    }
    else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }
  } else if (String(mDict.Operation) === 'Weekday') {
    if (mDict.Weekday1 == "" && mDict.Weekday2 == "" && mDict.Weekday3 == "") {
      Swal.fire({icon: 'warning',text:'Kindly fill in values for the Weekday Operation.'});
      validFlag = false
    }
    else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }
  } else if (String(mDict.Operation) === 'Weeknum') {
    if (mDict.Weeknum1 == "" && mDict.Weeknum2 == "" && mDict.Weeknum3 == "") {
      Swal.fire({icon: 'warning',text:'Kindly fill in values for the Weeknum Operation.'});
      validFlag = false
    }
    else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }
  } else if (String(mDict.Operation) === 'Yearfrac') {
    if (mDict.Yearfrac1 == "" && mDict.Yearfrac2 == "" && mDict.Yearfrac3 == "") {
      Swal.fire({icon: 'warning',text:'Kindly fill in values for the Yearfrac Operation.'});
      validFlag = false
    }
    else {
      Swal.fire({icon: 'success',text: 'Successfully validated!'});
    }
  } else if (String(mDict.Operation) === 'Networkdays') {
    if (mDict.Networkdays1 == "" && mDict.Networkdays2 == "") {
      window.alert('Kindly fill values for Networkdays Operation !! ')
      validFlag = false
    }
    else {
      window.alert('Successfully validated !! ')
    }
  } else if (String(mDict.Operation) === 'Workdays') {
    if (mDict.Workdays1 == "" && mDict.Workdays3 == "") {
      window.alert('Kindly fill values for Workdays Operation !! ')
      validFlag = false
    }
    else {
      window.alert('Successfully validated !! ')
    }
  }
}

function findreplacechangeeb() {
  let dtype = $(".Find_and_Replace1 option:selected").attr("data-datatype");
  if (dtype == undefined) {
      dtype = "";
  }
  $(".Find_and_Replace3").empty()
  if (dtype.startsWith("datetime") || dtype.startsWith("float") || dtype.startsWith("int")) {
    $(".Find_and_Replace3").append(`
      <option value="Equal to" selected>Equal to</option>
      <option value="Not Equal to">Not Equal to</option>
      <option value="Entire Column">Replace entire Column with static value</option>
      <option value="Greater than">Greater than</option>
      <option value="Greater than equal to">Greater than equal to</option>
      <option value="Smaller than">Smaller than</option>
      <option value="Smaller than equal to">Smaller than equal to</option>`);
  } else {
    $(".Find_and_Replace3").append(`
      <option value="Equal to" selected>Equal to</option>
      <option value="Not Equal to">Not Equal to</option>
      <option value="Entire Column">Replace entire Column with static value</option>
      <option value="Greater than">Greater than</option>
      <option value="Greater than equal to">Greater than equal to</option>
      <option value="Smaller than">Smaller than</option>
      <option value="Smaller than equal to">Smaller than equal to</option>
      <option value="Starts with">Starts with</option>
      <option value="Ends with">Ends with</option>
      <option value="Not Starts with">Not Starts with</option>
      <option value="Not Ends with">Not Ends with</option>
      <option value="Contains">Contains</option>
      <option value="Not Contains">Not Contains</option>`);
  }
  if (dtype == undefined) {
      dtype = "";
  }
  if(dtype.startsWith("float") || dtype.startsWith("int")) {
      $(".Find_and_Replace4").attr("type", "number");
  }
  else if(dtype.startsWith("datetime")) {
      $(".Find_and_Replace4").attr("type", "datetime-local");
      $(".Find_and_Replace4").attr("step", "1");
  }
  else {
      $(".Find_and_Replace4").attr("type", "text");
  }
}
function replacechangeeb() {
  let dtype = $(".Find_and_Replace2 option:selected").attr("data-datatype");

  if (dtype == undefined) {
      dtype = "";
  }
  if(dtype.startsWith("float") || dtype.startsWith("int")) {
      $(".Find_and_Replace5").attr("type", "number");
  }
  else if(dtype.startsWith("datetime")) {
      $(".Find_and_Replace5").attr("type", "datetime-local");
      $(".Find_and_Replace5").attr("step", "1");
  }
  else {
      $(".Find_and_Replace5").attr("type", "text");
  }
}
function selectcasechangeeb() {
  if ($(`.Find_and_Replace3`).val() == "Entire Column") {
    $(`.Find_and_Replace4`).parent().css('display', 'none')
  }
  else {
      $(`.Find_and_Replace4`).parent().css('display', 'block')
  }
}

const takeFuncInput = (name, unqID, c, This) => { // eslint-disable-line no-unused-vars
  iid = unqID
  const tname = name // eslint-disable-line no-unused-vars
  cIndex = c // eslint-disable-line no-unused-vars
  const heading = document.querySelector('#funcHeading')
  heading.innerText = name
  const inputDiv = document.querySelector('#funcInput')
  inputDiv.innerHTML = null
  // const description = document.querySelector('#funcDesc')

  let eleIdentifier = $('.ebFunctions').find('div').eq(parseInt(c)).find('a').attr('data-element_comp')
  if ($("#configureFlow")[0] != undefined && listViewCompCol == "") {
    eleIdentifier = ""
  }

  if (listViewComp == true) {
    selectedCol = listViewCompCol
  }
  // cDict = {}
  let finalList
  let a = ''
  let b = ''
  let d
  let cc
  let flag
  let e
  $.ajax({
    url: `/users/${urlPath}/computationModule/`,
    data: {
      Operation_name: name,
      operation: 'fetchFormData'
    },
    type: 'POST',
    dataType: 'json',
    success: function (data) {
      cDict.Operation = name
      for (let i = 0; i < data.element_config.length; i++) {
        if (String(data.element_config[i].input_type) === 'Column range') {
          $("#popup").css("width", "30%")
          $("#popup").css("left", "35%")
          $('.col_data').empty()
          $('#funcInput').append(`
                        <div class="form-group">
                            <label for="">${data.element_config[i].input_label} for ${data.element_config[i].input_name}</label>
                            <select class='${data.element_config[i].dependency_condition.trim().replaceAll(' ', '_') + data.element_config[i].dependency} select2 form-control col_data' multiple>
                            </select>
                        </div>
                    `)

          $('.col_data').select2()

          cDict[`${data.element_config[i].dependency_condition.trim().replaceAll(' ', '_') + data.element_config[i].dependency}`] = $(`.${data.element_config[i].dependency_condition.trim().replaceAll(' ', '_') + data.element_config[i].dependency}`).val()

          $(`.${data.element_config[i].dependency_condition.trim().replaceAll(' ', '_') + data.element_config[i].dependency}`).change(function () {
            cDict[`${data.element_config[i].dependency_condition.trim().replaceAll(' ', '_') + data.element_config[i].dependency}`] = $(`.${data.element_config[i].dependency_condition.trim().replaceAll(' ', '_') + data.element_config[i].dependency}`).val()
          })
        } else if (String(data.element_config[i].input_type) === 'Row range') {
          $("#popup").css("width", "30%")
          $("#popup").css("left", "35%")
          $('.row_data').empty()
          $('#funcInput').append(`
                        <div class="form-group">
                            <label for="">${data.element_config[i].input_label} for ${data.element_config[i].input_name}</label>
                            <select class='${data.element_config[i].dependency_condition.trim().replaceAll(' ', '_') + data.element_config[i].dependency} select2 form-control row_data' multiple>
                            </select>
                        </div>
                    `)

          $('.row_data').select2()

          cDict[`${data.element_config[i].dependency_condition.trim().replaceAll(' ', '_') + data.element_config[i].dependency}`] = $(`.${data.element_config[i].dependency_condition.trim().replaceAll(' ', '_') + data.element_config[i].dependency}`).val()

          $(`.${data.element_config[i].dependency_condition.trim().replaceAll(' ', '_') + data.element_config[i].dependency}`).change(function () {
            cDict[`${data.element_config[i].dependency_condition.trim().replaceAll(' ', '_') + data.element_config[i].dependency}`] = $(`.${data.element_config[i].dependency_condition.trim().replaceAll(' ', '_') + data.element_config[i].dependency}`).val()
          })
        } else if (String(data.element_config[i].input_type) === 'User numeric input') {
          $("#popup").css("width", "30%")
          $("#popup").css("left", "35%")
          $('.num_data').val('')
          $('#funcInput').append(`
                        <div class="form-group">
                            <label for="">${data.element_config[i].input_label} for ${data.element_config[i].input_name}</label>
                            <input class="${data.element_config[i].dependency_condition.trim().replaceAll(' ', '_') + data.element_config[i].dependency} num_data" type="number" min="0">
                        </div>
                    `)

          cDict[`${data.element_config[i].dependency_condition.trim().replaceAll(' ', '_') + data.element_config[i].dependency}`] = $(`.${data.element_config[i].dependency_condition.trim().replaceAll(' ', '_') + data.element_config[i].dependency}`).val()

          $(`.${data.element_config[i].dependency_condition.trim().replaceAll(' ', '_') + data.element_config[i].dependency}`).change(function () {
            cDict[`${data.element_config[i].dependency_condition.trim().replaceAll(' ', '_') + data.element_config[i].dependency}`] = $(`.${data.element_config[i].dependency_condition.trim().replaceAll(' ', '_') + data.element_config[i].dependency}`).val()
          })
        } else if (String(data.element_config[i].input_type) === 'Column value') {
          $("#popup").css("width", "30%")
          $("#popup").css("left", "35%")
          $('.col_data_single').empty()
          $('#funcInput').append(`
                        <div class="form-group">
                            <label for="">${data.element_config[i].input_label} for ${data.element_config[i].input_name}</label>
                            <select class='${data.element_config[i].dependency_condition.trim().replaceAll(' ', '_') + data.element_config[i].dependency} select2 form-control col_data_single'>
                            </select>
                        </div>
                    `)

          $('.col_data_single').select2()

          cDict[`${data.element_config[i].dependency_condition.trim().replaceAll(' ', '_') + data.element_config[i].dependency}`] = ''

          $(`.${data.element_config[i].dependency_condition.trim().replaceAll(' ', '_') + data.element_config[i].dependency}`).change(function () {
            cDict[`${data.element_config[i].dependency_condition.trim().replaceAll(' ', '_') + data.element_config[i].dependency}`] = $(`.${data.element_config[i].dependency_condition.trim().replaceAll(' ', '_') + data.element_config[i].dependency}`).val()
          })
        } else if (String(data.element_config[i].input_type) === 'Text input') {
          $("#popup").css("width", "30%")
          $("#popup").css("left", "35%")
          $('.text_data').val('')

          if (String(eleIdentifier) === 'datamgm' && !(selectedCol.startsWith("document"))) {
            $('#funcInput').append(`
                        <div class="form-group">
                            <label for="">${data.element_config[i].input_label} for ${data.element_config[i].input_name}</label>
                            <input class="${data.element_config[i].dependency_condition.trim().replaceAll(' ', '_') + data.element_config[i].dependency} text_data" type="text" disabled>
                        </div>
                    `)
          } else {
            $('#funcInput').append(`
                            <div class="form-group">
                                <label for="">${data.element_config[i].input_label} for ${data.element_config[i].input_name}</label>
                                <input class="${data.element_config[i].dependency_condition.trim().replaceAll(' ', '_') + data.element_config[i].dependency} text_data" type="text">
                            </div>
                        `)
          }

          cDict[`${data.element_config[i].dependency_condition.trim().replaceAll(' ', '_') + data.element_config[i].dependency}`] = ''

          $(`.${data.element_config[i].dependency_condition.trim().replaceAll(' ', '_') + data.element_config[i].dependency}`).change(function () {
            cDict[`${data.element_config[i].dependency_condition.trim().replaceAll(' ', '_') + data.element_config[i].dependency}`] = $(`.${data.element_config[i].dependency_condition.trim().replaceAll(' ', '_') + data.element_config[i].dependency}`).val()
          })
        } else if (String(data.element_config[i].input_type) === 'Rename Card') {
          $("#popup").css("width", "30%")
          $("#popup").css("left", "35%")
          $('#renameColumnDropdown1').empty()
          $('#funcInput').append(`
                        <div class="btn-group dropdown">
                            <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown">
                            Select Column to Rename
                            <span class="caret"></span>
                            </button>
                            <ul class="dropdown-menu dropdown-menu-sm dropdown-menu-left" id="renameColumnDropdown1" style="height:fit-content; max-height:10rem; min-width:fit-content; max-width:fit-content;">
                            </ul>
                        </div>
                        <br>
                        <br>
                        <div class="card">
                            <div id="renameColumnContainer1" style="max-height:15rem;overflow:scroll;overflow-x:hidden;">

                            </div>
                        </div>
                        <br>
                    `)
        } else if (String(data.element_config[i].input_type) === 'Filter Card') {
          $("#popup").css("width", "50%")
          $("#popup").css("left", "25%")
          $('#condition_dropdownWhereDT_merge1').empty()
          $('#funcInput').append(`
                <br>
                <div class="btn-group dropdown">
                    <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown">
                      Add Filter
                      <span class="caret"></span>
                    </button>
                    <ul class="dropdown-menu dropdown-menu-sm dropdown-menu-left" id="condition_dropdownWhereDT_merge1" style="height:fit-content; max-height:10rem; min-width:fit-content; max-width:fit-content;">
                    </ul>
                </div>
                <br>
                <br>
                <div class="row" id="itemsWhereDT_merge1">
                    <table class="table" id="filter-table_where_merge1">
                    </table>
                </div>
                <br>
                <br>
            `)
        } else if (String(data.element_config[i].input_type) === 'Group Card') {
          $("#popup").css("width", "50%")
          $("#popup").css("left", "25%")
          $('#groupAggList').empty()
          $('#selectedGroupAggList').empty()
          $('#funcInput').append(`
                  <div>
                      <h7 style="font-weight:bold">Grouping Aggregation Selection:</h7> <br> <br>
                  </div>
                  <div class="row">
                      <div class="col-6" id='groupAggFields'>
                          <h7 style="font-weight:bold">All fields</h7> <br> <br>
                          <div class="list-group" id="groupAggList" style="max-height:200px;overflow-y:auto">
                          </div>
                      </div>
                      <!-- Sub sub-elements config -->
                      <div class="col-6 subElementCards">
                          <h7 style="font-weight:bold">Selected fields</h7> <br> <br>
                          <div class="list-group" id="selectedGroupAggList" style="max-height:200px;overflow-y:auto">
                          </div>
                    </div>
                </div>
          `)


        } else if (String(data.element_config[i].input_type) === 'Column Card') {
          $("#popup").css("width", "70%")
          $("#popup").css("left", "15%")
          $("#popup").css("heigth", "15%")
          $('#AddColumnDropdown').empty()
          $('#funcInput').append(`
            <br>
            <div class="btn-group dropdown">
                <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown">
                  Add Condition
                  <span class="caret"></span>
                </button>
                <ul class="dropdown-menu dropdown-menu-sm dropdown-menu-left" id="AddColumnDropdown" style="height:fit-content; max-height:10rem; min-width:fit-content; max-width:fit-content;">
                </ul>
            </div>
            <br>
            <br>
            <div class="row" id="AddCoulmnContainer">
              <table class="table" id="filter-table_AddColumns">
              </table>
            </div>
            <br>
            <br>
            `)

        } else if (String(data.element_config[i].input_type) === 'Sort Card') {
          $("#popup").css("width", "50%")
          $("#popup").css("left", "25%")
          $('#sortColList').empty()
          $('#selectedSortColList').empty()
          $('#funcInput').append(`
                <br>
                <div class="row">
                    <div class="col-6">
                        <h7 style="font-weight:bold">All fields</h7> <br> <br>
                        <div class="list-group" id="sortColList" style="max-height:200px;overflow-y:auto">
                        </div>
                    </div>
                    <div class="col-6 subElementCards">
                        <h7 style="font-weight:bold">Selected fields</h7> <br> <br>
                        <div class="list-group" id="selectedSortColList" style="max-height:200px;overflow-y:auto">

                        </div>
                    </div>
                </div>
          `)
        }
      }
      cDict.element_id = unqID
      if(name == 'Find and Replace') {
        $(".Find_and_Replace3").empty();
        findreplacechangeeb();
        $('.Find_and_Replace1').on('change', findreplacechangeeb);
        $('.Find_and_Replace2').on('change', replacechangeeb);
        $('.Find_and_Replace3').on('change', selectcasechangeeb);
      }
      if (String(eleIdentifier) === 'datamgm') {
        if (String(idenFlag) !== 'attr') {
          $('#funcInput').append(`
                                <button type="button" class="btn btn-primary btn-xs mx-2 rounded px-2" id="val_equation" onClick="validate(cDict)">Validate</button>
                                <br>
                                <button type="button" class="btn btn-primary btn-xs mx-2 rounded px-2" id="save_equation" onClick="saveData('${tname}',validFlag,iid,cIndex)">Save</button>
                            `)
        } else {
          $('#funcInput').append(`
                                <button type="button" class="btn btn-primary btn-xs mx-2 rounded px-2" disabled id="val_equation" onClick="validate(cDict)">Validate</button>
                                <br>
                                <button type="button" class="btn btn-primary btn-xs mx-2 rounded px-2" disabled id="save_equation" onClick="saveData('${tname}',validFlag,iid,cIndex)">Save</button>
                            `)
        }
      } else {
        $('#funcInput').append(`
                            <button type="button" class="btn btn-primary btn-xs mx-2 rounded px-2" id="val_equation" onClick="validate(cDict)">Validate</button>
                            <br>
                            <button type="button" class="btn btn-primary btn-xs mx-2 rounded px-2" id="save_equation" onClick="saveData('${tname}',validFlag,iid,cIndex)">Save and Run</button>
                        `)
      }

      if (listViewComp == true) {
        selectedCol = listViewCompCol
      }

      const funcs = ['Square root', 'Log', 'Round'] // eslint-disable-line no-unused-vars
      if (String(name) !== 'Inner Join' && String(name) !== 'Left Join' && String(name) !== 'Right Join' && String(name) !== 'Outer Join' && String(name) !== 'Append and Concatenate' && String(name) !== 'Networkdays' && String(name) !== 'Networkdays.Intl' && String(name) !== 'Workdays' && String(name) !== 'Workdays.Intl') {
        if (String(eleIdentifier) === 'datamgm') {
          const cols = $('.ebDataElementsDiv').eq(parseInt(0)).find('.ColumnItem').find('p')

          let tablesList = []
          for (let i = 0; i < cols.length; i++) {
            tablesList.push(cols[i].innerText)
          }

          tablesList = [...new Set(tablesList)]

          $('.col_data').empty()
          $('.col_data_single').empty()
          $('#renameColumnDropdown1').empty()
          $('.col_data').append('<option value=\'-\'> -------------- </option>')
          $('.col_data_single').append('<option value=\'-\' selected> -------------- </option>')
          for (let i = 0; i < tablesList.length; i++) {
            if (((String(tablesList[i]) === selectedCol) && (String(c) === '0')) || (c === '1' && $('.ebFunctions').find('.function').eq(0).find('h2').text().includes('Join') && (String(tablesList[i]) === selectedCol))) {
              $('.col_data').append(`<option disabled value='${tablesList[i]}'>${tablesList[i]}</option>`)

              $('.col_data_single').append(`<option disabled value='${tablesList[i]}'>${tablesList[i]}</option>`)
            } else {
              $('.col_data').append(`<option value='${tablesList[i]}'>${tablesList[i]}</option>`)

              $('.col_data_single').append(`<option value='${tablesList[i]}'>${tablesList[i]}</option>`)

              $('#renameColumnDropdown1').append(`<li class="dropdown-item"><a href="javascript:void(0)" name='${tablesList[i]}' class="renameColumnBtn1">${tablesList[i]}</a></li>`)
            }
          };

          $('.renameColumnBtn1').click(function () {
            const name = $(this).attr('name')
            $('#renameColumnContainer1').append(
              `
                                            <div class="row renameColumnGroup1" style="margin-top:0.5rem;">
                                                <div class="col-1" style="color:var(--primary-color); margin:auto;">
                                                    <i class="fas fa-trash-alt removeCol1" style="cursor"></i>
                                                </div>
                                                <div class="col-10" style="margin-left:0.25rem">
                                                    <label>${name}</label>
                                                    <input type="text" class="textinput textInput form-control">
                                                </div>
                                            </div>
                                            `
            )

            $('.removeCol1').on('click', function () {
              $(this).parent().parent().remove()
            })
          })
        } else {

          if (String(name) == 'Add Column') {
            $('.Target_Column2').empty()
            $('.Target_Column2').append(`<option value="" selected disabled>Select Field Type</option>
              <option value="CharField">CharField</option>
              <option value="IntegerField">IntegerField</option>
              <option value="BigIntegerField">BigIntegerField</option>
              <option value="FloatField">FloatField</option>
              <option value="DateField">DateField</option>`)

            $('.Target_Column3').empty()
            $('.Target_Column3').append(`<option value="" selected disabled>Select Value Type</option>
              <option value="static_add">Static</option>
              <option value="dynamic_add">Dynamic</option>`)
          }

          let selID
          let name_ = ""
          if(compValProcess){
            name_ = compValProcessName
          }else{
            name_ = $('#EBDisplayButtonID').attr('data-name')
          }
          if (typeof (name_) === 'undefined') {
            name_ = $('#FileName').attr('data-experimentName')
          }
          let modelNameP = $('#EBDisplayButtonID').attr('data-p_table_name')
          if (typeof (modelNameP) === "undefined") {
            modelNameP = ""
          }

          if (parseInt(c) === 0) {
            a = $('#dataElementParent').find('div').find('div')
            try {
              selID = a[parseInt(c)].getAttribute('data-element_id')
            } catch (err) {
              b = $('.ebFunctions').find('div').find('a')
              selID = b[parseInt(c - 1)].getAttribute('data-element_id')
            }
          } else {
            a = $('.ebFunctions').find('div').find('a')
            selID = a[parseInt(c - 1)].getAttribute('data-element_id')
          }
          $.ajax({
            url: `/users/${urlPath}/computationModule/`,
            data: {
              operation: 'get_column_id',
              element_id: selID
            },
            type: 'POST',
            dataType: 'json',
            success: function (data) {
              $('.row_data').empty()
              for (let i = 0; i < data.element_config.length; i++) {
                $('.row_data').append(`<option value='${data.element_config[i]}'>${data.element_config[i]}</option>`)
              };

              if (String(name) != 'Add Column' && String(name) != 'Groupby' && String(name) != 'Data Utilities' && String(name) != 'Fill Missing Values' && String(name) != 'Sum Product' && String(name) != 'Weighted Average' && String(name) != 'Drop Duplicate' && String(name) != 'Days360' && String(name) != 'Weekday' && String(name) != 'Weeknum' && String(name) != 'Yearfrac') {
                $('.col_data').empty()
                $('.col_data_single').empty()
                $('.col_data').append('<option value="-"> -------------- </option>')
                $('.col_data_single').append('<option value="-" selected> -------------- </option>')
                for (let i = 0; i < data.columns.length; i++) {
                  $('.col_data').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)

                  $('.col_data_single').append(`<option data-datatype='${data.datatypes[i]}' value='${data.columns[i]}'>${data.columns[i]}</option>`)
                };
              }
              else if (name == "Data Utilities") {
                $('.col_data_single').empty()
                $('.col_data_single').append('<option value=\'-\' selected > -------------- </option>')
                $('.col_data_single').append("<option value='true'>Yes</option>")
                $('.col_data_single').append("<option value='false'>No</option>")
              }
              else if(name == "Fill Missing Values"){
                $('.Select_Operation1').empty()
                $('.Select_Operation1').append('<option value=\'-\' selected > -------------- </option>')
                $('.Select_Operation1').append("<option value='previous'>Fill Previous Value</option>")
                $('.Select_Operation1').append("<option value='next'>Fill Next Value</option>")
                $('.Select_Operation1').append("<option value='average'>Fill Average Value</option>")
                $('.Select_Operation1').append("<option value='mode'>Fill Frequent Value</option>")
                $('.Select_Operation1').append("<option value='custom'>Fill with custom value</option>")
                $('.Data_Table2').empty()
                $('.Data_Table2').append('<option value=\'-\' selected > -------------- </option>')
                for (let i = 0; i < data.columns.length; i++) {
                  $('.Data_Table2').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
                };
               }
               else if(name == 'Find and Replace'){
                $(".Find_and_Replace3").empty()
               }
               else if(name == 'Sum Product'){
                $('.Column_Group1').empty()
                $('.Column_Value2').empty()
                $('.Column_Group1').append('<option value=\'-\' disabled > -------------- </option>')
                $('.Column_Value2').append('<option value=\'-\' disabled  > -------------- </option>')
                for (let i = 0; i < data.columns.length; i++) {
                  $('.Column_Group1').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)

                  $('.Column_Value2').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
                };
              }
              else if(name == 'Weighted Average'){
                $('.Column_Group1').empty()
                $('.Average_Value2').empty()
                $('.Average_Weight3').empty()
                $('.Column_Group1').append('<option value=\'-\' disabled > -------------- </option>')
                $('.Average_Value2').append('<option value=\'-\' selected disabled > -------------- </option>')
                $('.Average_Weight3').append('<option value=\'-\' selected disabled > -------------- </option>')
                for (let i = 0; i < data.columns.length; i++) {
                  $('.Column_Group1').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)

                  $('.Average_Value2').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)

                  $('.Average_Weight3').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
                };
              }
              else if(name == "Drop Duplicate"){
                $('.Select_operation1').empty()
                $('.Select_operation1').append('<option value=\'-\' selected > -------------- </option>')
                $('.Select_operation1').append("<option value='first'>First Occurence</option>")
                $('.Select_operation1').append("<option value='last'>Last Occurence</option>")
                $('.Select_operation1').append("<option value='false'>Drop All</option>")
                $('.Data_table2').empty()
                $('.Data_table2').append('<option value=\'-\' disabled > -------------- </option>')
                for (let i = 0; i < data.columns.length; i++) {
                 $('.Data_table2').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
              };
            }
            else if(name == "Yearfrac"){
              $('.Yearfrac3').empty()
              $('.Yearfrac3').append(`<option value='1'>Actual/Actual AFB</option>`)
              $('.Yearfrac3').append(`<option value='2'>Actual/Actual ISDA</option>`)
              $('.Yearfrac3').append(`<option value='3'>30E/360 ISDA</option>`)
              $('.Yearfrac3').append(`<option value='4'>30/365</option>`)

              $('.Yearfrac1').empty()
              $('.Yearfrac2').empty()

              $('.Yearfrac1').append('<option value=\'-\' disabled selected> -------------- </option>')
              $('.Yearfrac2').append('<option value=\'-\' disabled selected> -------------- </option>')
              for (let i = 0; i < data.columns.length; i++) {
               $('.Yearfrac1').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
               $('.Yearfrac2').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
            };
          }
            else if(name == "Weeknum"){
              $('.Weeknum2').empty()
              $('.Weeknum2').append('<option value=\'-\' selected > -------------- </option>')
              $('.Weeknum2').append("<option value='1'>Week begins on Sunday</option>")
              $('.Weeknum2').append("<option value='2'>Week begins on Monday</option>")

              $('.Weeknum1').empty()
              $('.Weeknum1').append('<option value=\'-\' selected disabled > -------------- </option>')
              for (let i = 0; i < data.columns.length; i++) {
               $('.Weeknum1').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
            };
          }
            else if(name == "Weekday"){
              $('.Weekday2').empty()
              $('.Weekday2').append('<option value=\'-\' selected > -------------- </option>')
              $('.Weekday2').append("<option value='1'>Sun=1 through Sat=7</option>")
              $('.Weekday2').append("<option value='2'>Mon=1 through Sun=7</option>")
              $('.Weekday2').append("<option value='3'>Mon=0 through Sun=6</option>")

              $('.Weekday1').empty()
              $('.Weekday1').append('<option value=\'-\' selected disabled > -------------- </option>')
              for (let i = 0; i < data.columns.length; i++) {
               $('.Weekday1').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
            };
          }
              else if(name == "Days360"){
                $('.Days3603').empty()
                $('.Days3603').append('<option value=\'-\' selected > -------------- </option>')
                $('.Days3603').append("<option value='US'>US</option>")
                $('.Days3603').append("<option value='EU'>European</option>")

                $('.Days3601').empty()
                $('.Days3601').append('<option value=\'-\' selected disabled > -------------- </option>')
                $('.Days3602').empty()
                $('.Days3602').append('<option value=\'-\' selected disabled  > -------------- </option>')
                for (let i = 0; i < data.columns.length; i++) {
                  $('.Days3601').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
                  $('.Days3602').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
                };
            }
            },
            error: function () {
              Swal.fire({icon: 'error',text: 'Error! Please try again.'});
            }
          })

          $.ajax({
            url: `/users/${urlPath}/computationModule/`,
            data: {
              operation: 'fetch_redis_data_columns',
              data_element_id: selID
            },
            type: 'POST',
            dataType: 'json',
            success: function (data) {
              $('#renameColumnDropdown1').empty()
              if (Object.keys(data).includes('columnList')) {
                for (let i = 0; i < data.columnList.length; i++) {
                  $('#renameColumnDropdown1').append(`<li class="dropdown-item"><a href="javascript:void(0)" name='${data.columnList[i]}' class="renameColumnBtn1">${data.columnList[i]}</a></li>`)
                }
                $('.renameColumnBtn1').click(function () {
                  const name = $(this).attr('name')
                  $('#renameColumnContainer1').append(
                    `
                                            <div class="row renameColumnGroup1" style="margin-top:0.5rem;">
                                                <div class="col-1" style="color:var(--primary-color); margin:auto;">
                                                    <i class="fas fa-trash-alt removeCol1" style="cursor"></i>
                                                </div>
                                                <div class="col-10" style="margin-left:0.25rem">
                                                    <label>${name}</label>
                                                    <input type="text" class="textinput textInput form-control">
                                                </div>
                                            </div>
                                            `
                  )

                  $('.removeCol1').on('click', function () {
                    $(this).parent().parent().remove()
                  })
                })
              }
            },
            error: function () {
              Swal.fire({icon: 'error',text:"Error! Failure in fetching the connected data's columns. Please try again."});
            }
          })

          if (String(name) == 'Add Column') {
            $(".Target_Column3").off('select2:select').on("select2:select", function () {
              $("#AddColumnDropdown").empty()
              $.ajax({
                url: `/users/${urlPath}/computationModule/`,
                data: {
                  'element_id': "",
                  'model_name': name_,
                  'parent_element_id_list': JSON.stringify({ "Data1": selID }),
                  'req_data': selID,
                  'operation': 'addCondColDT_merge',
                  'type': $(".Target_Column3").val(),
                },
                type: "POST",
                dataType: "json",
                success: function (data) {
                  $('#filter-table_AddColumns').empty()
                  $("#filter-table_AddColumns").append(`
                    <thead>
                        <tr>
                            <th>Condition Check Variable</th>
                            <th>Condition*</th>
                            <th>Condition Value*</th>
                            <th>Set Global Variable</th>
                            <th>Representative Value*</th>
                            <th>Global Variable</th>
                        </tr>
                    </thead>
                    <tbody id = "filter-table_addCol_body"></tbody>
                `)

                  var label_column = data.label_column
                  for (const [key, value] of Object.entries(label_column)) {

                    $("#AddColumnDropdown").append('<li class="dropdown-item"><a href="javascript:void(0)" name=' + key + ' class="filter_btn_addColumn">' + value + '</a></li>');
                  }

                  var form_fields = data.form_fields


                  $('.filter_btn_addColumn').click(function () {
                    var name = $(this).attr('name');
                    var text = $(this).text();
                    var STRING = data.form_fields[name]

                    $('#filter-table_addCol_body').append(STRING)
                    var colDType = $('#filter-table_addCol_body').find('tr').eq(-1).find('select[data-dropdown_purpose="select_global_variable"]').attr('data-type');
                    let gVarNameList = [];
                    var allVarList = data['global_datetime_list'].concat(data['global_date_list'], data['global_text_list'], data['global_number_list'])
                    if (colDType === 'text') {
                      gVarNameList = data['global_text_list'];
                    } else if (colDType === 'number') {
                      gVarNameList = data['global_number_list'];
                    } else if (colDType === 'date') {
                      gVarNameList = data['global_datetime_list'].concat(data['global_date_list']);
                    } else if (colDType === 'datetime-local') {
                      gVarNameList = data['global_datetime_list'].concat(data['global_date_list']);
                    };
                    for (let i = 0; i < gVarNameList.length; i++) {
                      const varName = gVarNameList[i];
                      $('#filter-table_addCol_body').find('tr').eq(-1).find('select[data-dropdown_purpose="select_global_variable"]').append(`<option value='${varName}'>${varName}</option>`)
                    };
                    for (let j = 0; j < allVarList.length; j++) {
                      const varName_input = allVarList[j];
                      $('#filter-table_addCol_body').find('tr').eq(-1).find('select[data-dropdown_purpose="select_global_variable_input"]').append(`<option value='${varName_input}'>${varName_input}</option>`)
                    };
                    $('#filter-table_addCol_body:last-child').find("select").each(function () {
                      $(this).select2()
                    });
                    $('#filter-table_addCol_body').find('tr').each(function () {
                      $(this).find('select[data-dropdown_purpose="select_global_variable"]').off('select2:select').on('select2:select', function () {
                        $(this).closest("tr").find('input').eq(0).val("").trigger('change')
                      })
                    })
                    for (const [key, value] of Object.entries(label_column)) {
                      $('#filter-table_addCol_body').find('tr').eq(-1).find('select[data-dropdown_purpose="add_column"]').append(`<option value='${value}'>${value}</option>`);
                    }
                    $('.remove_filter').on('click', removefilter)

                  });
                  function removefilter() {
                    $(this).closest("tr").remove();
                  }

                },
                error: function () {
                  Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                }
              });
            });
          }
          if(String(name) == 'Filter' || String(name) == 'Sort' || String(name) == 'Groupby' || String(name) == 'Add Column'){
          $.ajax({
            url: `/users/${urlPath}/computationModule/`,
            data: {
              'element_id': "",
              'model_name': name_,
              "model_name_2": modelNameP,
              'parent_element_id_list': JSON.stringify({ "Data1": selID }),
              'req_data': selID,
              'operation': 'whereDT_merge',
            },
            type: "POST",
            dataType: "json",
            success: function (data) {
              $("#condition_dropdownWhereDT_merge1").empty()
              let labelColumn = data.label_column
              for (const [key, value] of Object.entries(labelColumn)) {
                $("#condition_dropdownWhereDT_merge1").append('<li class="dropdown-item"><a href="javascript:void(0)" name=' + key + ' class="filter_btn_1">' + value + '</a></li>');
              }

              $('.filter_btn_1').click(function () {
                let name = $(this).attr('name');
                let text = $(this).text();
                let STRING = data.form_fields[name]
                $('#filter-table_where_merge1').append(STRING)
                let colDType = $('#filter-table_where_merge1').find('tr').eq(-1).find('select[data-dropdown_purpose="select_global_variable"]').attr('data-type');
                let gVarNameList = [];
                if (colDType === 'text') {
                  gVarNameList = data['global_text_list'];
                } else if (colDType === 'number') {
                  gVarNameList = data['global_number_list'];
                } else if (colDType === 'date') {
                  gVarNameList = data['global_date_list'].concat(data['global_datetime_list']);
                } else if (colDType === 'datetime-local') {
                  gVarNameList = data['global_datetime_list'].concat(data['global_date_list']);
                };
                for (let i = 0; i < gVarNameList.length; i++) {
                  const varName = gVarNameList[i];
                  $('#filter-table_where_merge1').find('tr').eq(-1).find('select[data-dropdown_purpose="select_global_variable"]').append(`<option value='${varName}'>${varName}</option>`)
                };
                $('#filter-table_where_merge1:last-child').find("select").each(function () {
                  $(this).select2()
                })
                $('#filter-table_where_merge1').find('tr').each(function () {
                  $(this).find('select[data-dropdown_purpose="select_global_variable"]').off('select2:select').on('select2:select', function () {
                    $(this).closest("tr").find('input').eq(0).val("").trigger('change')
                  });
                });
                $('.remove_filter').on('click', removefilter)
              });
              function removefilter() {
                $(this).closest("tr").remove();
              }

            },
            error: function () {
              Swal.fire({icon: 'error',text: 'Error! Please try again.'});
            }
          });
        }
        if(String(name) == 'Sort'){
          $.ajax({
            url: `/users/${urlPath}/computationModule/`,
            data: {
              'element_id': "",
              'model_name': name_,
              'parent_element_id_list': JSON.stringify({ "Data1": selID }),
              'operation': 'sortByDT_merge',
            },
            type: "POST",
            dataType: "json",
            success: function (data) {
              $('#sortColList').empty();
              $('#selectedSortColList').empty();
              for (j in data.columns) {
                $('#sortColList').append(
                  `<button type="button" class="sortField list-group-item list-group-item-action list-group-item-light" value="${data.columns[j]}">${data.columns[j]}</button>`
                )
              }
              $('.sortField').click(function () {
                fieldname = $(this).val()
                $('#selectedSortColList').append(
                  `
                  <div class="row"><button class="sortFieldSelected list-group-item list-group-item-action list-group-item-light col-7" value="${fieldname}" data-toggle="dropdown" data-hover="dropdown">${fieldname}</button><select class="sortType col-4 select2 form-control" style="float:left;"><option value="" disabled selected>-----</option><option value="True">Ascending</option><option value="False">Descending</option></select></div>
                  `
                )
                $('.sortFieldSelected').off("click").on("click", function () {
                  let element = $(this).closest("div.row");

                  element.remove()
                });
              })
            },
            error: function () {
              Swal.fire({icon: 'error',text: 'Error! Please try again.'});
            }
          });
        }
          if(String(name) == 'Groupby'){
          $.ajax({
            url: `/users/${urlPath}/computationModule/`,
            data: {
              'element_id': "",
              'req_data': selID,
              'model_name': name_,
              'parent_element_id_list': JSON.stringify({ "Data1": selID }),
              'operation': 'groupByDT_merge',
            },
            type: "POST",
            dataType: "json",
            success: function (data) {
              $('#groupAggList').empty();
              $('.Target_Column1').empty();
              $('#selectedGroupAggList').empty();
              for (i in data.char_list) {
                $('.Target_Column1').append(`<option value="${data.char_list[i]}">${data.char_list[i]}</option>`)
              }
              $('.Target_Column1').on("change", function () {

                })
                for (j in data.num_list) {
                  $('#groupAggList').append(
                    `<button type="button" class="groupAggField list-group-item list-group-item-action list-group-item-light" value="${data.num_list[j]}">${data.num_list[j]}</button>`
                  )
                }
                $('.groupAggField').click(selectedGroupFunction)
                function selectedGroupFunction() {
                  let fieldname = $(this).val()
                  $('#selectedGroupAggList').append(`
                  <div class="row"><button class="groupAggFieldSelected list-group-item list-group-item-action list-group-item-light col-7" value="${fieldname}" data-toggle="dropdown" data-hover="dropdown">${fieldname}</button><select class="aggfunc col-4 select2 form-control" style="float:left;"><option value="" disabled selected>-----</option><option value="min">Min</option><option value="max">Max</option><option value="sum">Sum</option><option value="mean">Mean</option></select></div>
                  `)


                  $('.groupAggFieldSelected').click(function () {
                    let element = $(this).closest("div.row");

                    element.remove()

                  });
                }
              },
              error: function () {
                Swal.fire({icon: 'error',text: 'Error! Please try again.'});
              }
            });
          }

        }
      } else {
        if (String(name) == 'Append and Concatenate') {
          $('.Target_Column1').empty()
          $('.Target_Column1').append(`<option value="" disabled selected>Select Operation</option>
          <option value="append">Append</option>
          <option value="concatenate">Concatenation</option>
          `)
        }
        if (String(eleIdentifier) === 'datamgm') {
          a = $('.ebDataElementsDiv').eq(parseInt(c)).find('.ColumnItem')
          b = $('.ebDataElementsDiv').eq(parseInt(c)).find('.ColumnItem').find('p')

          let colsList1 = []
          let colsList2 = []

          const tablesList = new Set()
          for (let i = 0; i < a.length; i++) {
            tablesList.add(a[i].getAttribute('data-element_id'))
          }

          const finalList = Array.from(tablesList)
          if (String(finalList.length) === '1') {
            cc = $('.ebFunctions').find('div').find('a')

            finalList[1] = cc[parseInt(c - 1)].getAttribute('data-element_id')

            for (let i = 0; i < a.length; i++) {
              colsList1.push(b[i].innerText)
            }

            flag = 1
            while (flag) {
              d = $('.ebDataElementsDiv').eq(parseInt(c - 1)).find('.ColumnItem')
              e = $('.ebDataElementsDiv').eq(parseInt(c - 1)).find('.ColumnItem').find('p')

              if (String(d.length) !== '0') {
                for (let i = 0; i < d.length; i++) {
                  colsList2.push(e[i].innerText)
                }
                flag = 0
              }

              c = c - 1
            }
          } else {
            for (let i = 0; i < a.length; i++) {
              if (String(finalList[0]) === String(a[i].getAttribute('data-element_id'))) {
                colsList1.push(b[i].innerText)
              } else {
                colsList2.push(b[i].innerText)
              }
            }
          }

          colsList1 = [...new Set(colsList1)]
          colsList2 = [...new Set(colsList2)]

          if (String(name) != 'Append and Concatenate') {
            $('.col_data').odd().addClass('col_data_table1')
            $('.col_data_single').odd().addClass('col_data_table1')

            $('.col_data').even().addClass('col_data_table2')
            $('.col_data_single').even().addClass('col_data_table2')

            $('.col_data_table1').empty()
            $('.col_data_table1').append('<option value=\'-\'> -------------- </option>')
            for (let i = 0; i < colsList2.length; i++) {
              $('.col_data_table1').append(`<option value='${colsList2[i]}'>${colsList2[i]}</option>`)
            };

            $('.col_data_table2').empty()
            $('.col_data_table2').append('<option value=\'-\'> -------------- </option>')
            for (let i = 0; i < colsList1.length; i++) {
              $('.col_data_table2').append(`<option value='${colsList1[i]}'>${colsList1[i]}</option>`)
            };
          }
          cDict.table_data = finalList
        } else {
          $('.col_data').odd().addClass('col_data_table1')
          $('.col_data_single').odd().addClass('col_data_table1')

          $('.col_data').even().addClass('col_data_table2')
          $('.col_data_single').even().addClass('col_data_table2')

          var temp_nd = {}
          a = $('.ebDataElementsDiv').eq(parseInt(c)).find('.ColumnItem')

          const tablesList = new Set()
          const t_t = new Set()
          for (let i = 0; i < a.length; i++) {
            tablesList.add(a[i].getAttribute('data-element_id'))
            t_t.add(a[i].getAttribute('data-table'))
            temp_nd[a[i].querySelectorAll('p')[0].textContent] = a[i].getAttribute('data-element_id')
          }

          finalList = Array.from(tablesList)
          f2 = Array.from(t_t)
          if (String(finalList.length) === '1') {
            b = $('.ebFunctions').find('div').find('a')

            try{
              finalList[1] = b[parseInt(c - 1)].getAttribute('data-element_id')
            } catch(err) {

            }
          }
          cDict.table_data = finalList
          cDict.t_data = f2
          cDict.temp_nd = temp_nd

          $.ajax({
            url: `/users/${urlPath}/computationModule/`,
            data: {
              operation: 'get_column_id',
              element_id: finalList[0]
            },
            type: 'POST',
            dataType: 'json',
            success: function (data) {
              if (String(name) != 'Append and Concatenate' && String(name) != 'Networkdays' && String(name) != 'Networkdays.Intl' && String(name) != 'Workdays' && String(name) != 'Workdays.Intl') {
                $('.col_data_table2').empty()
                $('.col_data_table2').append('<option value=\'-\'> -------------- </option>')
                for (let i = 0; i < data.columns.length; i++) {
                  $('.col_data_table2').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
                };
              } else if(String(name) == 'Networkdays'){

                $('.Networkdays1').empty()
                $('.Networkdays2').empty()
                $('.Networkdays3').empty()

                $('.Networkdays1').append('<option value=\'-\' selected> -------------- </option>')
                $('.Networkdays2').append('<option value=\'-\' selected> -------------- </option>')
                $('.Networkdays3').append('<option value=\'-\' selected> -------------- </option>')

                for (let i = 0; i < data.columns.length; i++) {
                  $('.Networkdays1').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
                  $('.Networkdays2').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
                  $('.Networkdays3').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
                };
              } else if(String(name) == 'Networkdays.Intl'){

                $('.NetworkdaysIntl1').empty()
                $('.NetworkdaysIntl2').empty()
                $('.NetworkdaysIntl3').empty()

                $('.NetworkdaysIntl1').append('<option value=\'-\' selected> -------------- </option>')
                $('.NetworkdaysIntl2').append('<option value=\'-\' selected> -------------- </option>')
                $('.NetworkdaysIntl3').append('<option value=\'-\' selected> -------------- </option>')

                for (let i = 0; i < data.columns.length; i++) {
                  $('.NetworkdaysIntl1').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
                  $('.NetworkdaysIntl2').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
                  $('.NetworkdaysIntl3').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
                };
              } else if(String(name) == 'Workdays'){

                $('.Workdays1').empty()
                $('.Workdays2').empty()

                $('.Workdays1').append('<option value=\'-\' selected> -------------- </option>')
                $('.Workdays2').append('<option value=\'-\' selected> -------------- </option>')

                for (let i = 0; i < data.columns.length; i++) {
                  $('.Workdays1').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
                  $('.Workdays2').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
                };
              } else if(String(name) == 'Workdays.Intl'){

                $('.WorkdaysIntl1').empty()
                $('.WorkdaysIntl2').empty()
                $('.WorkdaysIntl3').empty()

                $('.WorkdaysIntl1').append('<option value=\'-\' selected> -------------- </option>')
                $('.WorkdaysIntl2').append('<option value=\'-\' selected> -------------- </option>')

                $('.WorkdaysIntl3').append(`<option value='0'> Mon </option>`)
                $('.WorkdaysIntl3').append(`<option value='1'> Tue </option>`)
                $('.WorkdaysIntl3').append(`<option value='2'> Wed </option>`)
                $('.WorkdaysIntl3').append(`<option value='3'> Thu </option>`)
                $('.WorkdaysIntl3').append(`<option value='4'> Fri </option>`)
                $('.WorkdaysIntl3').append(`<option value='5'> Sat </option>`)
                $('.WorkdaysIntl3').append(`<option value='6'> Sun </option>`)

                for (let i = 0; i < data.columns.length; i++) {
                  $('.WorkdaysIntl1').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
                  $('.WorkdaysIntl2').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
                };
              }
            },
            error: function () {
              Swal.fire({icon: 'error',text: 'Error! Please try again.'});
            }
          })

          $.ajax({
            url: `/users/${urlPath}/computationModule/`,
            data: {
              operation: 'get_column_id',
              element_id: finalList[1]
            },
            type: 'POST',
            dataType: 'json',
            success: function (data) {
              if (String(name) != 'Append and Concatenate' && String(name) != 'Networkdays' && String(name) != 'Networkdays.Intl' && String(name) != 'Workdays' && String(name) != 'Workdays.Intl') {
                $('.col_data_table1').empty()
                $('.col_data_table1').append('<option value=\'-\'> -------------- </option>')
                for (let i = 0; i < data.columns.length; i++) {
                  $('.col_data_table1').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
                };
              } else if(String(name) == 'Networkdays'){

                $('.Networkdays1').empty()
                $('.Networkdays2').empty()
                $('.Networkdays3').empty()

                $('.Networkdays1').append('<option value=\'-\' selected> -------------- </option>')
                $('.Networkdays2').append('<option value=\'-\' selected> -------------- </option>')
                $('.Networkdays3').append('<option value=\'-\' selected> -------------- </option>')

                if(Object.keys(data).length > 0) {
                  for (let i = 0; i < data.columns.length; i++) {
                    $('.Networkdays1').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
                    $('.Networkdays2').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
                    $('.Networkdays3').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
                  };
                }

                $.ajax({
                  url: `/users/${urlPath}/computationModule/`,
                  data: {
                    operation: 'get_column_id',
                    element_id: finalList[0]
                  },
                  type: 'POST',
                  dataType: 'json',
                  success: function (data) {
                      for (let i = 0; i < data.columns.length; i++) {
                        $('.Networkdays1').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
                        $('.Networkdays2').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
                        $('.Networkdays3').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
                      };
                  },
                  error: function () {
                    window.alert('Error')
                  }
                })

              } else if(String(name) == 'Networkdays.Intl'){

                $('.NetworkdaysIntl1').empty()
                $('.NetworkdaysIntl2').empty()
                $('.NetworkdaysIntl3').empty()

                $('.NetworkdaysIntl1').append('<option value=\'-\' selected> -------------- </option>')
                $('.NetworkdaysIntl2').append('<option value=\'-\' selected> -------------- </option>')
                $('.NetworkdaysIntl3').append('<option value=\'-\' selected> -------------- </option>')

                if(Object.keys(data).length > 0) {
                  for (let i = 0; i < data.columns.length; i++) {
                    $('.NetworkdaysIntl1').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
                    $('.NetworkdaysIntl2').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
                    $('.NetworkdaysIntl3').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
                  };
                }

                $.ajax({
                  url: `/users/${urlPath}/computationModule/`,
                  data: {
                    operation: 'get_column_id',
                    element_id: finalList[0]
                  },
                  type: 'POST',
                  dataType: 'json',
                  success: function (data) {
                      for (let i = 0; i < data.columns.length; i++) {
                        $('.NetworkdaysIntl1').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
                        $('.NetworkdaysIntl2').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
                        $('.NetworkdaysIntl3').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
                      };
                  },
                  error: function () {
                    window.alert('Error')
                  }
                })

              } else if(String(name) == 'Workdays'){

                $('.Workdays1').empty()
                $('.Workdays2').empty()

                $('.Workdays1').append('<option value=\'-\' selected> -------------- </option>')
                $('.Workdays2').append('<option value=\'-\' selected> -------------- </option>')

                if(Object.keys(data).length > 0) {
                  for (let i = 0; i < data.columns.length; i++) {
                    $('.Workdays1').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
                    $('.Workdays2').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
                  };
                }

                $.ajax({
                  url: `/users/${urlPath}/computationModule/`,
                  data: {
                    operation: 'get_column_id',
                    element_id: finalList[0]
                  },
                  type: 'POST',
                  dataType: 'json',
                  success: function (data) {
                      for (let i = 0; i < data.columns.length; i++) {
                        $('.Workdays1').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
                        $('.Workdays2').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
                      };
                  },
                  error: function () {
                    window.alert('Error')
                  }
                })

              } else if(String(name) == 'Workdays.Intl'){

                $('.WorkdaysIntl1').empty()
                $('.WorkdaysIntl2').empty()

                $('.WorkdaysIntl1').append('<option value=\'-\' selected> -------------- </option>')
                $('.WorkdaysIntl2').append('<option value=\'-\' selected> -------------- </option>')

                if(Object.keys(data).length > 0) {
                  for (let i = 0; i < data.columns.length; i++) {
                    $('.WorkdaysIntl1').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
                    $('.WorkdaysIntl2').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
                  };
                }

                $.ajax({
                  url: `/users/${urlPath}/computationModule/`,
                  data: {
                    operation: 'get_column_id',
                    element_id: finalList[0]
                  },
                  type: 'POST',
                  dataType: 'json',
                  success: function (data) {
                      for (let i = 0; i < data.columns.length; i++) {
                        $('.WorkdaysIntl1').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
                        $('.WorkdaysIntl2').append(`<option value='${data.columns[i]}'>${data.columns[i]}</option>`)
                      };
                  },
                  error: function () {
                    window.alert('Error')
                  }
                })

              }
            },
            error: function () {
              Swal.fire({icon: 'error',text: 'Error! Please try again.'});
            }
          })
        }
      }

      setTimeout(function () {
        let name_ = ""
        if(compValProcess){
          name_ = compValProcessName
        }else{
          name_ = $('#EBDisplayButtonID').attr('data-name')
        }
        let dataID = 'comp'
        if (typeof (name_) === 'undefined') {
          name_ = $('#FileName').attr('data-experimentName')
          if (typeof (name_) === 'undefined') {
            if (String(idenFlag) === 'defn') {
              name_ = $('#tname').val()
            } else if (String(idenFlag) === 'attr' || String(idenFlag) === 'add' || String(idenFlag) === 'edit') {
              name_ = $('.dataElements').find('p').text()
            } else if (listViewComp == true) {
              name_ = listViewModelName
            }

            dataID = 'datamgm'
          }
        }

        $.ajax({
          url: `/users/${urlPath}/computationModule/`,
          data: {
            operation: 'equ_config',
            model_name: name_,
            element_id: iid,
            data_id: dataID
          },
          type: 'POST',
          dataType: 'json',
          success: function (data) {
            if (String(dataID) === 'datamgm' && !(selectedCol.startsWith("document"))) {
              $('.Target_Column1').val(selectedCol).trigger('change')
            }

            if (Object.keys(data).length > 0) {
              if (String(data.element_config.function) === 'Apply Math Operation') {
                if (String(data.element_config.inputs.Operation) === 'Basic Operations') {
                  if (String(data.element_config.inputs.Other_Inputs.Type_choice) === 'Row_Sum') {
                    $('.Row_sum1').val(data.element_config.inputs.Column_1).trigger('change')
                    $('.Row_sum2').val(data.element_config.inputs.Number).trigger('change')
                    $('.Target_Column1').val(data.element_config.inputs.Column_name).trigger('change')
                  } else if (String(data.element_config.inputs.Other_Inputs.Type_choice) === 'Column_Sum') {
                    $('.Column_sum1').val(data.element_config.inputs.Column_1).trigger('change')
                    $('.Column_sum2').val(data.element_config.inputs.Number).trigger('change')
                    $('.Target_Column1').val(data.element_config.inputs.Column_name).trigger('change')
                  } else if (String(data.element_config.inputs.Other_Inputs.Type_choice) === 'Cell_Sum') {
                    $('.Cell_11').val(data.element_config.inputs.Other_Inputs.Cell_11).trigger('change')
                    $('.Cell_12').val(data.element_config.inputs.Other_Inputs.Cell_12).trigger('change')
                    $('.Cell_sum3').val(data.element_config.inputs.Number).trigger('change')
                    $('.Cell_21').val(data.element_config.inputs.Other_Inputs.Cell_21).trigger('change')
                    $('.Cell_22').val(data.element_config.inputs.Other_Inputs.Cell_22).trigger('change')
                    $('.Target_Cell_11').val(data.element_config.inputs.Other_Inputs.Target_1).trigger('change')
                    $('.Target_Cell_22').val(data.element_config.inputs.Other_Inputs.Target_2).trigger('change')
                  }
                } else if (String(data.element_config.inputs.Operation) === 'Rounding Operations') {
                  if (String(data.element_config.inputs.Sub_Op) === 'Ceiling') {
                    $('.Ceiling1').val(data.element_config.inputs.Column_1).trigger('change')
                    $('.Ceiling_Significance_Multiple2').val(data.element_config.inputs.Other_Inputs.Signif_Multiple)
                    $('.Target_Column1').val(data.element_config.inputs.Column_name).trigger('change')
                  } else if (String(data.element_config.inputs.Sub_Op) === 'Floor') {
                    $('.Floor1').val(data.element_config.inputs.Column_1).trigger('change')
                    $('.Floor_Significance_Multiple2').val(data.element_config.inputs.Other_Inputs.Signif_Multiple)
                    $('.Target_Column1').val(data.element_config.inputs.Column_name).trigger('change')
                  } else if (String(data.element_config.inputs.Sub_Op) === 'Odd') {
                    $('.Odd1').val(data.element_config.inputs.Column_1).trigger('change')
                    $('.Target_Column1').val(data.element_config.inputs.Column_name).trigger('change')
                  } else if (String(data.element_config.inputs.Sub_Op) === 'Even') {
                    $('.Even1').val(data.element_config.inputs.Column_1).trigger('change')
                    $('.Target_Column1').val(data.element_config.inputs.Column_name).trigger('change')
                  } else if (String(data.element_config.inputs.Sub_Op) === 'Round') {
                    $('.Round1').val(data.element_config.inputs.Column_1).trigger('change')
                    $('.No_of_Decimals2').val(data.element_config.inputs.Other_Inputs.Decimal)
                    $('.Target_Column1').val(data.element_config.inputs.Column_name).trigger('change')
                  } else if (String(data.element_config.inputs.Sub_Op) === 'Round_Up') {
                    $('.Round_Up1').val(data.element_config.inputs.Column_1).trigger('change')
                    $('.Target_Column1').val(data.element_config.inputs.Column_name).trigger('change')
                  } else if (String(data.element_config.inputs.Sub_Op) === 'Round_Down') {
                    $('.Round_Down1').val(data.element_config.inputs.Column_1).trigger('change')
                    $('.Target_Column1').val(data.element_config.inputs.Column_name).trigger('change')
                  } else if (String(data.element_config.inputs.Sub_Op) === 'Truncate') {
                    $('.Truncate1').val(data.element_config.inputs.Column_1).trigger('change')
                    $('.Target_Column1').val(data.element_config.inputs.Column_name).trigger('change')
                  }
                } else if (String(data.element_config.inputs.Operation) === 'Log and Exponential Functions') {
                  if (String(data.element_config.inputs.Sub_Op) === 'Log_base') {
                    $('.Natural_Log1').val(data.element_config.inputs.Column_1).trigger('change')
                    $('.Target_Column1').val(data.element_config.inputs.Column_name).trigger('change')
                  } else if (String(data.element_config.inputs.Sub_Op) === 'Exponential') {
                    $('.Exponential1').val(data.element_config.inputs.Column_1).trigger('change')
                    $('.Target_Column1').val(data.element_config.inputs.Column_name).trigger('change')
                  } else if (String(data.element_config.inputs.Sub_Op) === 'Natural_Log') {
                    $('.Base_Log1').val(data.element_config.inputs.Column_1).trigger('change')
                    $('.Log_Base_value2').val(data.element_config.inputs.Other_Inputs.Log_Base)
                    $('.Target_Column1').val(data.element_config.inputs.Column_name).trigger('change')
                  }
                } else if (String(data.element_config.inputs.Operation) === 'Power and Root Functions') {
                  $('.Root_Operation1').val(data.element_config.inputs.Column_1).trigger('change')
                  $('.Root_Operation2').val(data.element_config.inputs.Other_Inputs.Power).trigger('change')
                  $('.Target_Column1').val(data.element_config.inputs.Column_name).trigger('change')
                }
              } else if (String(data.element_config.function) === 'Rename Column') {
                $('.Drop_Columns1').val(data.element_config.inputs.drop_column).trigger('change')

                const existingConfigDict = data.element_config
                const existingconfig = existingConfigDict.inputs

                if (Object.keys(existingconfig).includes('rename_config')) {
                  const renameConfig = existingconfig.rename_config
                  for (const [key, value] of Object.entries(renameConfig)) {
                    $('#renameColumnContainer1').append(
                      `
                                                    <div class="row renameColumnGroup1" style="margin-top:0.5rem;">
                                                        <div class="col-1" style="color:var(--primary-color); margin:auto;">
                                                            <i class="fas fa-trash-alt removeCol1" style="cursor"></i>
                                                        </div>
                                                        <div class="col-10" style="margin-left:0.25rem">
                                                            <label>${key}</label>
                                                            <input type="text" class="textinput textInput form-control" value=${value}>
                                                        </div>
                                                    </div>
                                                    `
                    )
                  }
                  $('.removeCol1').on('click', function () {
                    $(this).parent().parent().remove()
                  })
                }
              } else if (String(data.element_config.function) === 'Pivot and Transpose') {
                if ((String(data.element_config.element_name) === 'pivot')) {
                  $('.Target_Column1').val(data.element_config.inputs.option_config.index).trigger('change')
                  $('.Target_Column2').val(data.element_config.inputs.option_config.columns).trigger('change')
                  $('.Target_Column3').val(data.element_config.inputs.option_config.values).trigger('change')
                }
                if ((String(data.element_config.element_name) === 'unpivot')) {
                  $('.Target_Column1').val(data.element_config.inputs.option_config.index).trigger('change')
                  $('.Target_Column2').val(data.element_config.inputs.option_config.columns).trigger('change')
                  $('.Target_Column3').val(data.element_config.inputs.option_config.variable_column_name).trigger('change')
                  $('.Target_Column4').val(data.element_config.inputs.option_config.value_column_name).trigger('change')

                }

              } else if (String(data.element_config.function) === 'Data Utilities') {
                if (data.element_config.inputs.reset_checked) {
                  reset_checked_val = "true"
                } else {
                  reset_checked_val = "false"
                }
                if (data.element_config.inputs.drop_checked) {
                  drop_checked_val = "true"
                } else {
                  drop_checked_val = "false"
                }
                $(".Reset_Index1").val(reset_checked_val).trigger('change')
                $(".Drop_Index2").val(drop_checked_val).trigger('change')
              } else if (String(data.element_config.function) === 'Concat Columns') {
                $('.Target_Column1').val(data.element_config.inputs.Column_name).trigger('change')
                $('.Target_Column2').val(data.element_config.inputs.Column_1).trigger('change')
                $('.Target_Column3').val(data.element_config.inputs.Separator).trigger('change')

              } else if (String(data.element_config.function) === 'Missing Values') {
                $(".Select_Operation1").val(data.element_config.inputs.Sub_Op).trigger('change')
                $(".Data_Table2").val(data.element_config.inputs.Other_Inputs.Data).trigger('change')
                $(".Custom_value3").val(data.element_config.inputs.Other_Inputs.subOpConfig).trigger('change')
              } else if (String(data.element_config.function) === 'Elementary Statistics') {
                if(data.element_config.inputs.previewString == 'Sum Product'){
                  $(".Column_Group1").val(data.element_config.inputs.Groupby_column).trigger('change')
                  $(".Column_Value2").val(data.element_config.inputs.agg_config[0].Value_column).trigger('change')
                  $(".Column_Name3").val(data.element_config.inputs.agg_config[0].new_column_name).trigger('change')
                }
                if(data.element_config.inputs.previewString == 'Weighted Average'){
                  $(".Column_Group1").val(data.element_config.inputs.Groupby_column).trigger('change')
                  $(".Average_Value2").val(data.element_config.inputs.agg_config[0].Value_column).trigger('change')
                  $(".Average_Weight3").val(data.element_config.inputs.agg_config[0].Weights).trigger('change')
                  $(".Column_Name4").val(data.element_config.inputs.agg_config[0].new_column_name).trigger('change')
                }
              } else if (String(data.element_config.function) === 'Drop Duplicate') {
                $(".Select_operation1").val(data.element_config.inputs.Sub_Op).trigger('change')
                $(".Data_table2").val(data.element_config.inputs.Other_Inputs.Data).trigger('change')
              } else if (String(data.element_config.function) === 'Add Fix Column') {
                $(".Input_Column2").val(data.element_config.inputs.input_name).trigger('change')
                $(".Add_Column2").val(data.element_config.inputs.input_value).trigger('change')
              }  else if (String(data.element_config.function) === 'Delimit Column') {
                $(".Delimit_Column1").val(data.element_config.inputs.columnName).trigger('change')
                $(".Delimit_Column2").val(data.element_config.inputs.delimiter).trigger('change')
              }  else if (String(data.element_config.function) === 'Find and Replace') {
                $(".Find_and_Replace1").val(data.element_config.inputs.fdict.columnName).trigger('change')
                $(".Find_and_Replace2").val(data.element_config.inputs.fdict.replacecolumnName).trigger('change')
                $(".Find_and_Replace3").val(data.element_config.inputs.fdict.find_case).trigger('change')
                $(".Find_and_Replace4").val(data.element_config.inputs.fdict.find)
                $(".Find_and_Replace5").val(data.element_config.inputs.fdict.replace)
              } else if (String(data.element_config.function) === 'Workdays.Intl') {
                $(".WorkdaysIntl1").val(data.element_config.inputs.start_date).trigger('change')
                $(".WorkdaysIntl2").val(data.element_config.inputs.holiday).trigger('change')
                $(".WorkdaysIntl3").val(data.element_config.inputs.weekend).trigger('change')
                $(".WorkdaysIntl4").val(data.element_config.inputs.days).trigger('change')
                $(".WorkdaysIntl5").val(data.element_config.inputs.colname).trigger('change')
              } else if (String(data.element_config.function) === 'Workdays') {
                $(".Workdays1").val(data.element_config.inputs.start_date).trigger('change')
                $(".Workdays2").val(data.element_config.inputs.holiday).trigger('change')
                $(".Workdays3").val(data.element_config.inputs.days).trigger('change')
                $(".Workdays4").val(data.element_config.inputs.colname).trigger('change')
              } else if (String(data.element_config.function) === 'Networkdays.Intl') {
                $(".NetworkdaysIntl1").val(data.element_config.inputs.start_date).trigger('change')
                $(".NetworkdaysIntl2").val(data.element_config.inputs.end_date).trigger('change')
                $(".NetworkdaysIntl3").val(data.element_config.inputs.holiday).trigger('change')
                $(".NetworkdaysIntl4").val(data.element_config.inputs.weekend).trigger('change')
                $(".NetworkdaysIntl5").val(data.element_config.inputs.colname).trigger('change')
              } else if (String(data.element_config.function) === 'Networkdays') {
                $(".Networkdays1").val(data.element_config.inputs.start_date).trigger('change')
                $(".Networkdays2").val(data.element_config.inputs.end_date).trigger('change')
                $(".Networkdays3").val(data.element_config.inputs.holiday).trigger('change')
                $(".Networkdays4").val(data.element_config.inputs.colname).trigger('change')
              } else if (String(data.element_config.function) === 'Year') {
                $(".Year1").val(data.element_config.inputs.date).trigger('change')
                $(".Year2").val(data.element_config.inputs.colname).trigger('change')
              } else if (String(data.element_config.function) === 'Weeknum') {
                $(".Weeknum1").val(data.element_config.inputs.date).trigger('change')
                $(".Weeknum2").val(data.element_config.inputs.method).trigger('change')
                $(".Weeknum3").val(data.element_config.inputs.colname).trigger('change')
              } else if (String(data.element_config.function) === 'Weekday') {
                $(".Weekday1").val(data.element_config.inputs.date).trigger('change')
                $(".Weekday2").val(data.element_config.inputs.method).trigger('change')
                $(".Weekday3").val(data.element_config.inputs.colname).trigger('change')
              } else if (String(data.element_config.function) === 'Today') {
                $(".Today1").val(data.element_config.inputs.colname).trigger('change')
              } else if (String(data.element_config.function) === 'Time') {
                $(".Time1").val(data.element_config.inputs.hour).trigger('change')
                $(".Time2").val(data.element_config.inputs.minute).trigger('change')
                $(".Time3").val(data.element_config.inputs.second).trigger('change')
                $(".Time4").val(data.element_config.inputs.colname).trigger('change')
              } else if (String(data.element_config.function) === 'Second') {
                $(".Second1").val(data.element_config.inputs.date).trigger('change')
                $(".Second2").val(data.element_config.inputs.colname).trigger('change')
              } else if (String(data.element_config.function) === 'Now') {
                $(".Now1").val(data.element_config.inputs.colname).trigger('change')
              } else if (String(data.element_config.function) === 'Month') {
                $(".Month1").val(data.element_config.inputs.date).trigger('change')
                $(".Month2").val(data.element_config.inputs.colname).trigger('change')
              } else if (String(data.element_config.function) === 'Minute') {
                $(".Minute1").val(data.element_config.inputs.date).trigger('change')
                $(".Minute2").val(data.element_config.inputs.colname).trigger('change')
              } else if (String(data.element_config.function) === 'Isoweeknum') {
                $(".Isoweeknum1").val(data.element_config.inputs.date).trigger('change')
                $(".Isoweeknum2").val(data.element_config.inputs.colname).trigger('change')
              } else if (String(data.element_config.function) === 'Hour') {
                $(".Hour1").val(data.element_config.inputs.date).trigger('change')
                $(".Hour2").val(data.element_config.inputs.colname).trigger('change')
              } else if (String(data.element_config.function) === 'Eomonth') {
                $(".Eomonth1").val(data.element_config.inputs.start_date).trigger('change')
                $(".Eomonth2").val(data.element_config.inputs.months).trigger('change')
                $(".Eomonth3").val(data.element_config.inputs.colname).trigger('change')
              } else if (String(data.element_config.function) === 'Days360') {
                $(".Days3601").val(data.element_config.inputs.start_date).trigger('change')
                $(".Days3602").val(data.element_config.inputs.end_date).trigger('change')
                $(".Days3603").val(data.element_config.inputs.method).trigger('change')
                $(".Days3604").val(data.element_config.inputs.colname).trigger('change')
              } else if (String(data.element_config.function) === 'Edate') {
                $(".Edate1").val(data.element_config.inputs.start_date).trigger('change')
                $(".Edate2").val(data.element_config.inputs.months).trigger('change')
                $(".Edate3").val(data.element_config.inputs.colname).trigger('change')
              } else if (String(data.element_config.function) === 'Days') {
                $(".Days1").val(data.element_config.inputs.start_date).trigger('change')
                $(".Days2").val(data.element_config.inputs.end_date).trigger('change')
                $(".Days3").val(data.element_config.inputs.colname).trigger('change')
              } else if (String(data.element_config.function) === 'Date') {
                $(".Date1").val(data.element_config.inputs.year).trigger('change')
                $(".Date2").val(data.element_config.inputs.month).trigger('change')
                $(".Date3").val(data.element_config.inputs.day).trigger('change')
                $(".Date4").val(data.element_config.inputs.colname).trigger('change')
              } else if (String(data.element_config.function) === 'Yearfrac') {
                $(".Yearfrac1").val(data.element_config.inputs.start_date).trigger('change')
                $(".Yearfrac2").val(data.element_config.inputs.end_date).trigger('change')
                $(".Yearfrac3").val(data.element_config.inputs.basis).trigger('change')
                $(".Yearfrac4").val(data.element_config.inputs.colname).trigger('change')
              } else if (String(data.element_config.function) === 'Day') {
                $(".Day1").val(data.element_config.inputs.date).trigger('change')
                $(".Day2").val(data.element_config.inputs.colname).trigger('change')
              } else if (String(data.element_config.function) === 'Merge and Join' && String(data.element_config.element_name) !== 'filter' && String(data.element_config.element_name) !== 'AddColumn' && String(data.element_config.element_name) !== 'sort' && String(data.element_config.element_name) !== 'groupby') {
                if (String(data.element_config.element_name) === 'append') {
                  $('.Target_Column1').val(data.element_config.inputs.final_config.merge_and_join.inputs.option).trigger('change')
                } else if (String(data.element_config.inputs.final_config.merge_and_join.inputs.join_config.join_type) === 'left') {
                  $('.Left_join_on_Data11').val(data.element_config.inputs.final_config.merge_and_join.inputs.join_config.on.Data1).trigger('change')
                  $('.Left_join_on_Data22').val(data.element_config.inputs.final_config.merge_and_join.inputs.join_config.on.Data2).trigger('change')
                  $('.Left_join_Data13').val(data.element_config.inputs.final_config.merge_and_join.inputs.join_config.on_display.Data1).trigger('change')
                  $('.Left_join_Data24').val(data.element_config.inputs.final_config.merge_and_join.inputs.join_config.on_display.Data2).trigger('change')
                } else if (String(data.element_config.inputs.final_config.merge_and_join.inputs.join_config.join_type) === 'right') {
                  $('.Right_join_on_Data11').val(data.element_config.inputs.final_config.merge_and_join.inputs.join_config.on.Data1).trigger('change')
                  $('.Right_join_on_Data22').val(data.element_config.inputs.final_config.merge_and_join.inputs.join_config.on.Data2).trigger('change')
                  $('.Right_join_Data13').val(data.element_config.inputs.final_config.merge_and_join.inputs.join_config.on_display.Data1).trigger('change')
                  $('.Right_join_Data24').val(data.element_config.inputs.final_config.merge_and_join.inputs.join_config.on_display.Data2).trigger('change')
                } else if (String(data.element_config.inputs.final_config.merge_and_join.inputs.join_config.join_type) === 'inner') {
                  $('.Inner_join_on_Data11').val(data.element_config.inputs.final_config.merge_and_join.inputs.join_config.on.Data1).trigger('change')
                  $('.Inner_join_on_Data22').val(data.element_config.inputs.final_config.merge_and_join.inputs.join_config.on.Data2).trigger('change')
                  $('.Inner_join_Data13').val(data.element_config.inputs.final_config.merge_and_join.inputs.join_config.on_display.Data1).trigger('change')
                  $('.Inner_join_Data24').val(data.element_config.inputs.final_config.merge_and_join.inputs.join_config.on_display.Data2).trigger('change')
                } else if (String(data.element_config.inputs.final_config.merge_and_join.inputs.join_config.join_type) === 'outer') {
                  $('.Outer_join_on_Data11').val(data.element_config.inputs.final_config.merge_and_join.inputs.join_config.on.Data1).trigger('change')
                  $('.Outer_join_on_Data22').val(data.element_config.inputs.final_config.merge_and_join.inputs.join_config.on.Data2).trigger('change')
                  $('.Outer_join_Data13').val(data.element_config.inputs.final_config.merge_and_join.inputs.join_config.on_display.Data1).trigger('change')
                  $('.Outer_join_Data24').val(data.element_config.inputs.final_config.merge_and_join.inputs.join_config.on_display.Data2).trigger('change')
                }
              } else {
                $('.Target_Column1').val(data.element_config.inputs.Column_name).trigger('change')
                $('.Time_Periods1').val(data.element_config.inputs.Column_1).trigger('change')
                $('.Days2').val(data.element_config.inputs.Days).trigger('change')
                $('.Months3').val(data.element_config.inputs.Months).trigger('change')
                $('.Years4').val(data.element_config.inputs.Years).trigger('change')
              }
            }
          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          }
        });
      }, 250)


      setTimeout(function () {

        let name_ = ""
        if(compValProcess){
          name_ = compValProcessName
        }else{
          name_ = $('#EBDisplayButtonID').attr('data-name')
        }
        let dataID = 'comp'
        if (typeof (name_) === 'undefined') {
          name_ = $('#FileName').attr('data-experimentName')
          if (typeof (name_) === 'undefined') {
            if (String(idenFlag) === 'defn') {
              name_ = $('#tname').val()
            } else if (String(idenFlag) === 'attr' || String(idenFlag) === 'add' || String(idenFlag) === 'edit') {
              name_ = $('.dataElements').find('p').text()
            } else if (listViewComp == true) {
              name_ = listViewModelName
            }

            dataID = 'datamgm'
          }
        }

        let modelNameP = $('#EBDisplayButtonID').attr('data-p_table_name')
        if (typeof (modelNameP) === "undefined") {
          modelNameP = ""
        }
        if(String(name) == 'Filter' || String(name) == 'Sort' || String(name) == 'Groupby' || String(name) == 'Add Column'){
        $.ajax({
          url: `/users/${urlPath}/computationModule/`,
          data: {
            'model_name': name_,
            'model_name_2': modelNameP,
            "element_id": iid,
            'operation': 'merge_config',
          },
          type: "POST",
          dataType: "json",
          success: function (data) {
            if (Object.keys(data).length > 0) {
              if (String(data.element_config.element_name) === 'filter') {
                let element_config_dict = data.element_config
                let final_config = element_config_dict.inputs.final_config
                if (final_config["groupby"] != "") {
                  let groupby_config = final_config["groupby"]
                  let option_config = groupby_config["inputs"]["option_config"]

                  var conditionList = option_config.condition
                  if (conditionList.length > 0) {
                    $('#filter-table_where_merge1').empty()
                    for (var i = 0; i < conditionList.length; i++) {
                      c_name = (conditionList[i].column_name)
                      cond = (conditionList[i].condition)
                      i_val = (conditionList[i].input_value)
                      gVar = (conditionList[i].globalVariable)
                      var STRING = data.form_fields_where[c_name]
                      $('#filter-table_where_merge1').append(STRING)
                      var colDType = $('#filter-table_where_merge1').find('tr').eq(-1).find('select[data-dropdown_purpose="select_global_variable"]').attr('data-type');
                      let gVarNameList = [];
                      if (colDType === 'text') {
                        gVarNameList = data['global_text_list'];
                      } else if (colDType === 'number') {
                        gVarNameList = data['global_number_list'];
                      } else if (colDType === 'date') {
                        gVarNameList = data['global_date_list'].concat(data['global_datetime_list']);
                      } else if (colDType === 'datetime-local') {
                        gVarNameList = data['global_datetime_list'].concat(data['global_date_list']);
                      };
                      for (let i = 0; i < gVarNameList.length; i++) {
                        const varName = gVarNameList[i];
                        $('#filter-table_where_merge1').find('tr').eq(-1).find('select[data-dropdown_purpose="select_global_variable"]').append(`<option value='${varName}'>${varName}</option>`)
                      };
                      if (cond.endsWith(" AND")) {
                        cond = cond.replace(" AND", "")
                        $('#filter-table_where_merge1').find(`tr:nth-child(${i + 1})`).find(`td:nth-child(2) > div > select`).val(cond).trigger('change')
                        $('#filter-table_where_merge1').find(`tr:nth-child(${i + 1})`).find(`td:nth-child(3) > div > input`).val(i_val).trigger('change')
                        $('#filter-table_where_merge1').find(`tr:nth-child(${i + 1})`).find(`td:nth-child(5) > div > select`).val("AND").trigger('change')
                      } else if (cond.endsWith(" OR")) {
                        cond = cond.replace(" OR", "")
                        $('#filter-table_where_merge1').find(`tr:nth-child(${i + 1})`).find(`td:nth-child(2) > div > select`).val(cond).trigger('change')
                        $('#filter-table_where_merge1').find(`tr:nth-child(${i + 1})`).find(`td:nth-child(3) > div > input`).val(i_val).trigger('change')
                        $('#filter-table_where_merge1').find(`tr:nth-child(${i + 1})`).find(`td:nth-child(5) > div > select`).val("OR").trigger('change')
                      } else {
                        $('#filter-table_where_merge1').find(`tr:nth-child(${i + 1})`).find(`td:nth-child(2) > div > select`).val(cond).trigger('change')
                        $('#filter-table_where_merge1').find(`tr:nth-child(${i + 1})`).find(`td:nth-child(3) > div > input`).val(i_val).trigger('change')
                      }
                      $('#filter-table_where_merge1').find(`tr:nth-child(${i + 1})`).find(`td:nth-child(4) > div > select`).val(gVar).trigger('change')

                      $('#filter-table_where_merge1:last-child').find("select").each(function () {
                        $(this).select2()
                      })
                      $('.remove_filter').on('click', removefilter)
                    }
                    function removefilter() {
                      $(this).closest("tr").remove();
                    }
                  }


                }
              }
              else if (String(data.element_config.element_name) === 'sort') {
                let element_config_dict = data.element_config
                let final_config = element_config_dict.inputs.final_config
                var sortTypeFields = final_config["sortby"]["sort"];
                var counter = 0;
                for (let [key, value] of Object.entries(sortTypeFields)) {
                  $(`.sortField[value='${key}']`).trigger('click')
                  $(`.sortType`).eq(counter).val(value).trigger('change')
                  counter++;
                }
              } else if (String(data.element_config.element_name) === 'groupby') {
                let element_config_dict = data.element_config
                let final_config = element_config_dict.inputs.final_config
                if (final_config["groupby"] != "") {
                  let groupby_config = final_config["groupby"]
                  let option_config = groupby_config["inputs"]["option_config"]

                  var groupAggFields = option_config.aggregate_func;
                  var groupColList = option_config.group_by;
                  $('.Target_Column1').val(groupColList).trigger('change');
                  $('.Target_Column1').val(groupColList).trigger('select2:select');
                  var counter = 0;
                  for (let [key, value] of Object.entries(groupAggFields)) {

                    $(`.groupAggField[value='${key}']`).trigger('click')
                    $(`.aggfunc`).eq(counter).val(value).trigger('change')
                    counter++;

                  }

                }
              }

              else if (String(data.element_config.element_name) === 'AddColumn') {

                let element_config_dict = data.element_config
                let final_config = element_config_dict.inputs.final_config
                if (final_config["groupby"] != "") {

                  let groupby_config = final_config["groupby"]
                  let option_config = groupby_config["inputs"]["option_config"]

                  var AddColConditionList = option_config.condition
                  $('.Target_Column1').val(AddColConditionList.new_column_name).trigger('change')
                  $('.Target_Column2').val(AddColConditionList.field_type).trigger('change')
                  $('.Target_Column2').val(AddColConditionList.field_type).trigger('select2:select')
                  $('.Target_Column3').val(AddColConditionList.add_type).trigger('change')
                  $('#filter-table_AddColumns').empty()
                  $("#filter-table_AddColumns").append(`
              <thead>
                  <tr>
                      <th>Condition Check Variable</th>
                      <th>Condition*</th>
                      <th>Condition Value*</th>
                      <th>Set Global Variable</th>
                      <th>Representative Value*</th>
                      <th>Global Variable</th>
                  </tr>
              </thead>
              <tbody id = "filter-table_addCol_body"></tbody>
          `)
                  var ConditionList = AddColConditionList.condition;
                  if (ConditionList.length > 0) {
                    var form_fields_addCondCol = data.form_fields_addCondCol;


                    for (var i = 0; i < ConditionList.length; i++) {
                      var c_name = ConditionList[i].column_name
                      var cond = ConditionList[i].condition;
                      var cond_name = ConditionList[i].condition_value;
                      var global_variable = ConditionList[i].globalVariable;
                      var repr_value = ConditionList[i].repr_value.repr_value;
                      var global_var = ConditionList[i].repr_value.global_var;

                      var STRING = form_fields_addCondCol[c_name]
                      $('#filter-table_addCol_body').append(STRING)

                      var colDType = $('#filter-table_addCol_merge_body').find('tr').eq(-1).find('select[data-dropdown_purpose="select_global_variable"]').attr('data-type');
                      let gVarNameList = [];
                      var allVarList = data['global_datetime_list'].concat(data['global_date_list'], data['global_text_list'], data['global_number_list'])
                      if (colDType === 'text') {
                        gVarNameList = data['global_text_list'];
                      } else if (colDType === 'number') {
                        gVarNameList = data['global_number_list'];
                      } else if (colDType === 'date') {
                        gVarNameList = data['global_date_list'].concat(data['global_datetime_list']);
                      } else if (colDType === 'datetime-local') {
                        gVarNameList = data['global_datetime_list'].concat(data['global_date_list']);
                      };
                      for (let k = 0; k < gVarNameList.length; k++) {
                        const varName = gVarNameList[k];
                        $('#filter-table_addCol_body').find('tr').eq(-1).find('select[data-dropdown_purpose="select_global_variable"]').append(`<option value='${varName}'>${varName}</option>`)
                      };
                      for (let j = 0; j < allVarList.length; j++) {
                        const varName_input = allVarList[j];
                        $('#filter-table_addCol_body').find('tr').eq(-1).find('select[data-dropdown_purpose="select_global_variable_input"]').append(`<option value='${varName_input}'>${varName_input}</option>`)
                      };
                      $('#filter-table_addCol_body').find(`tr:nth-child(${i + 1})`).find(`select[name= ${c_name}]`).val(cond).trigger('change')
                      $('#filter-table_addCol_body').find(`tr:nth-child(${i + 1})`).find(`td:nth-child(3) > div > input`).val(cond_name).trigger('change')
                      $('#filter-table_addCol_body').find(`tr:nth-child(${i + 1})`).find(`select[data-dropdown_purpose="select_global_variable"]`).val(global_variable).trigger('change')
                      $('#filter-table_addCol_body').find(`tr:nth-child(${i + 1})`).find(`select[data-dropdown_purpose="select_global_variable_input"]`).val(global_var).trigger('change')
                      $('#filter-table_addCol_body').find(`tr:nth-child(${i + 1})`).find(`td:nth-child(5) > div > input`).val(repr_value).trigger('change')
                      $('#filter-table_addCol_body:last-child').find("select").each(function () {
                        $(this).select2()
                      }); $('.remove_filter').on('click', removefilter)
                      let selID
                      if (parseInt(c) === 0) {
                        a = $('#dataElementParent').find('div').find('div')
                        try {
                          selID = a[parseInt(c)].getAttribute('data-element_id')
                        } catch (err) {
                          b = $('.ebFunctions').find('div').find('a')
                          selID = b[parseInt(c - 1)].getAttribute('data-element_id')
                        }
                      } else {
                        a = $('.ebFunctions').find('div').find('a')
                        selID = a[parseInt(c - 1)].getAttribute('data-element_id')
                      }

                      $.ajax({
                        url: `/users/${urlPath}/computationModule/`,
                        data: {
                          'element_id': iid,
                          'model_name': name_,
                          'parent_element_id_list': JSON.stringify({ "Data1": selID }),
                          'req_data': selID,
                          'operation': 'addCondColDT_merge',
                          'type': $(".Target_Column3").val(),
                        },
                        type: "POST",
                        dataType: "json",
                        success: function (data) {
                          var label_column = data.label_column
                          $("#AddColumnDropdown").empty()
                          for (const [key, value] of Object.entries(label_column)) {
                            $("#AddColumnDropdown").append('<li class="dropdown-item"><a href="javascript:void(0)" name=' + key + ' class="filter_btn_addColumn">' + value + '</a></li>');
                          }
                          $('#filter-table_addCol_body').find('tr').find('select[data-dropdown_purpose="add_column"]').empty()
                          for (const [key, value] of Object.entries(label_column)) {
                            $('#filter-table_addCol_body').find('tr').each(function () {
                              $(this).find('select[data-dropdown_purpose="add_column"]').append(`<option value='${value}'>${value}</option>`);
                            })
                          }
                          for (let kk = 0; kk < option_config.condition.condition.length; kk++) {
                            reprValue2 = ConditionList[kk].repr_value.repr_value
                            if (option_config.condition.add_type == "static_add") {
                              $('#filter-table_AddColumns').find(`tr`).eq(-1).find(`input`).eq(1).val(reprValue2).trigger('change')
                            } else {
                              $('#filter-table_AddColumns').find(`tr:nth-child(${kk + 1})`).find(`select[data-dropdown_purpose="add_column"]`).val(reprValue2).trigger('change')
                            }
                          }
                          $('.filter_btn_addColumn').click(function () {
                            var name = $(this).attr('name');
                            var text = $(this).text();
                            var STRING = data.form_fields[name]

                            $('#filter-table_addCol_body').append(STRING)
                            var colDType = $('#filter-table_addCol_body').find('tr').eq(-1).find('select[data-dropdown_purpose="select_global_variable"]').attr('data-type');
                            let gVarNameList = [];
                            var allVarList = data['global_datetime_list'].concat(data['global_date_list'], data['global_text_list'], data['global_number_list'])
                            if (colDType === 'text') {
                              gVarNameList = data['global_text_list'];
                            } else if (colDType === 'number') {
                              gVarNameList = data['global_number_list'];
                            } else if (colDType === 'date') {
                              gVarNameList = data['global_datetime_list'].concat(data['global_date_list']);
                            } else if (colDType === 'datetime-local') {
                              gVarNameList = data['global_datetime_list'].concat(data['global_date_list']);
                            };
                            for (let m = 0; m < gVarNameList.length; m++) {
                              const varName = gVarNameList[m];
                              $('#filter-table_addCol_body').find('tr').eq(-1).find('select[data-dropdown_purpose="select_global_variable"]').append(`<option value='${varName}'>${varName}</option>`)
                            };
                            for (let j = 0; j < allVarList.length; j++) {
                              const varName_input = allVarList[j];
                              $('#filter-table_addCol_body').find('tr').eq(-1).find('select[data-dropdown_purpose="select_global_variable_input"]').append(`<option value='${varName_input}'>${varName_input}</option>`)
                            };
                            $('#filter-table_addCol_body:last-child').find("select").each(function () {
                              $(this).select2()
                            });
                            $('#filter-table_addCol_body').find('tr').each(function () {
                              $(this).find('select[data-dropdown_purpose="select_global_variable"]').off('select2:select').on('select2:select', function () {
                                $(this).closest("tr").find('input').eq(0).val("").trigger('change')
                              })
                            })
                            for (const [key, value] of Object.entries(label_column)) {
                              $('#filter-table_addCol_body').find('tr').eq(-1).find('select[data-dropdown_purpose="add_column"]').append(`<option value='${value}'>${value}</option>`);
                            }
                            $('.remove_filter').on('click', removefilter)

                          });
                          function removefilter() {
                            $(this).closest("tr").remove();
                          }
                        },
                        error: function () {
                          Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                        }
                      });
                    }

                    function removefilter() {
                      $(this).closest("tr").remove();
                    }
                  } else {
                    $('#filter-table_addCol_body').empty()
                  }


                }
              }
            }

          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          }
        })
      }
      }, 300)
    },
    error: function () {
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    }
  })
}

// displays all the tables fetched from the backend

const displayTables = (tables) => {
  const htmlString = tables
    .map((table) => {
      return `
            <div onClick="selectTable('${table}')" class="tableItem btn-xs btn">
                <p style="margin-bottom:0">${table}</p>
            </div>
        `
    })
    .join('')
  tableList.innerHTML = htmlString
}

const deleteElement = (This) => { // eslint-disable-line no-unused-vars
  const indexDel = $(This).parent().index() - 1

  $('#stepNumsEb').find('.stepNumberEB').eq(indexDel).remove()
  $('.ebFunctions').find('div').eq(indexDel).remove()
  $('#dataElementParent').find('.ebDataElementsDiv').eq(indexDel).remove()
  $('#functionPreviews').find('div').eq(indexDel).remove()

  counter = counter - 1
  displayPreviews()
  displayCharacters(funcDic)
  displayFav(favFunctionList)

  if (String(counter) === '1') {
    $('.ebFunctions').find('div').eq(counter - 1).find('span').css('display', 'block')
  } else {
    $('.ebFunctions').find('div').eq(counter - 1).find('span').css('display', 'block')
    $('.ebFunctions').find('div').eq(counter - 2).find('span').css('display', 'none')
  }
}

const displayCharacters = (characters) => {
  const minm = 1000000000000
  const maxm = 9999999999999
  let icon = ''
  const uniqueidMaths = 'applyMathOps' + (Math.floor(Math.random() * (maxm - minm + 1)) + minm).toString()
  const uniqueidJoin = 'mergeAndJoin' + (Math.floor(Math.random() * (maxm - minm + 1)) + minm).toString()
  const uniqueidRename = 'renameColumn' + (Math.floor(Math.random() * (maxm - minm + 1)) + minm).toString()
  const uniqueidPivot = 'pivotAndTranspose' + (Math.floor(Math.random() * (maxm - minm + 1)) + minm).toString()
  const uniqueidConcat = 'concatColumn' + (Math.floor(Math.random() * (maxm - minm + 1)) + minm).toString()
  let dataID
  if (typeof ($('#tname').val()) === 'undefined' && listViewComp == false) {
    dataID = 'comp'
  } else {
    dataID = 'datamgm'
  }

  const htmlString = characters
    .map((character) => {
      if ((String(character.name) === 'Column division' || String(character.name) === 'Row division') && String(dataID) === 'datamgm') {
        icon = 'fas fa-divide'
      } else if ((String(character.name) === 'Column multiplication' || String(character.name) === 'Row multiplication') && String(dataID) === 'datamgm') {
        icon = 'fas fa-times'
      } else if ((String(character.name) === 'Column subtraction' || String(character.name) === 'Row subtraction') && String(dataID) === 'datamgm') {
        icon = 'fas fa-minus'
      } else if ((String(character.name) === 'Column sum' || String(character.name) === 'Row sum') && String(dataID) === 'datamgm') {
        icon = 'fas fa-plus'
      } else if (String(character.name) === 'Square root' && String(dataID) === 'datamgm') {
        icon = 'fas fa-square-root-alt'
      } else if ((String(character.name) === 'Inner Join' || String(character.name) === 'Left Join' || String(character.name) === 'Right Join' || String(character.name) === 'Outer Join' || String(character.name) === 'Append and Concatenate') && String(dataID) === 'datamgm') {
        icon = 'fas fa-coins'
      } else if (String(character.name) === 'Round' && String(dataID) === 'datamgm') {
        icon = 'far fa-circle'
      } else {
        icon = 'fas fa-thumbs-up'
      }

      if (String(dataID) === 'datamgm') {
        if ((String(character.name) === 'Left Join' || String(character.name) === 'Right Join' || String(character.name) === 'Inner Join' || String(character.name) === 'Outer Join' || String(character.name) === 'Append and Concatenate' || String(character.name) === 'Filter' || String(character.name) === 'Add Column' || String(character.name) === 'Sort' || String(character.name) === 'Groupby')) {
          return `
                <div class="function draggable" draggable="true">
                    <h2>${character.name}</h2>
                    <h3 class="heartIcon" onClick="addToFav('${character.name}' )" value=${character.name}><i class="${icon}"></i></h3>
                    <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueidJoin}" data-element_comp="${dataID}"  onClick="popupOpen();takeFuncInput('${character.name}','${uniqueidJoin}','${indexCount}',this)">&#11167;</a>
                    <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueidJoin}" data-element_comp="${dataID}"  onClick="deleteElement(this)">&#10006;</span>
                </div>
            `
        } else if (String(character.name) === 'Round') {
          return `
                    <div class="function draggable" draggable="true">
                        <h2>${character.name}</h2>
                        <h3 class="heartIcon" onClick="addToFav('${character.name}' )" value=${character.name}>oO</h3>
                        <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueidMaths}" data-element_comp="${dataID}" onClick="popupOpen();takeFuncInput('${character.name}','${uniqueidMaths}','${indexCount}',this)">&#11167;</a>
                        <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueidMaths}" data-element_comp="${dataID}"  onClick="deleteElement(this)">&#10006;</span>
                    </div>
                `
        } else if (String(character.name) === 'Log') {
          return `
                    <div class="function draggable" draggable="true">
                        <h2>${character.name}</h2>
                        <h3 class="heartIcon" onClick="addToFav('${character.name}' )" value=${character.name}>&#13266;</h3>
                        <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueidMaths}" data-element_comp="${dataID}" onClick="popupOpen();takeFuncInput('${character.name}','${uniqueidMaths}','${indexCount}',this)">&#11167;</a>
                        <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueidMaths}" data-element_comp="${dataID}"  onClick="deleteElement(this)">&#10006;</span>
                    </div>
                `
        } else if (String(character.name) === 'Rename and Drop') {
          return `
                    <div class="function draggable" draggable="true">
                        <h2>${character.name}</h2>
                        <h3 class="heartIcon" onClick="addToFav('${character.name}' )" value=${character.name}>&#13266;</h3>
                        <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueidRename}" data-element_comp="${dataID}" onClick="popupOpen();takeFuncInput('${character.name}','${uniqueidRename}','${indexCount}',this)">&#11167;</a>
                        <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueidRename}" data-element_comp="${dataID}"  onClick="deleteElement(this)">&#10006;</span>
                    </div>
                `
        } else if (String(character.name) === 'Pivot' || String(character.name) === 'Unpivot') {
          return `
                    <div class="function draggable" draggable="true">
                        <h2>${character.name}</h2>
                        <h3 class="heartIcon" onClick="addToFav('${character.name}' )" value=${character.name}>&#13266;</h3>
                        <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueidPivot}" data-element_comp="${dataID}" onClick="popupOpen();takeFuncInput('${character.name}','${uniqueidPivot}','${indexCount}',this)">&#11167;</a>
                        <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueidPivot}" data-element_comp="${dataID}"  onClick="deleteElement(this)">&#10006;</span>
                    </div>
                `

        } else if (String(character.name) === 'Concat Columns') {
          return `
                    <div class="function draggable" draggable="true">
                        <h2>${character.name}</h2>
                        <h3 class="heartIcon" onClick="addToFav('${character.name}' )" value=${character.name}>&#13266;</h3>
                        <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueidConcat}" data-element_comp="${dataID}" onClick="popupOpen();takeFuncInput('${character.name}','${uniqueidConcat}','${indexCount}',this)">&#11167;</a>
                        <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueidConcat}" data-element_comp="${dataID}"  onClick="deleteElement(this)">&#10006;</span>
                    </div>
                `
        } else {
          return `
                <div class="function draggable" draggable="true">
                    <h2>${character.name}</h2>
                    <h3 class="heartIcon" onClick="addToFav('${character.name}' )" value=${character.name}><i class="${icon}"></i></h3>
                    <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueidMaths}" data-element_comp="${dataID}" onClick="popupOpen();takeFuncInput('${character.name}','${uniqueidMaths}','${indexCount}',this)">&#11167;</a>
                    <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueidMaths}" data-element_comp="${dataID}"  onClick="deleteElement(this)">&#10006;</span>
                </div>
            `
        }
      } else {
        if (String(character.name) === 'Left Join' || String(character.name) === 'Right Join' || String(character.name) === 'Inner Join' || String(character.name) === 'Outer Join' || String(character.name) === 'Append and Concatenate' || String(character.name) === 'Filter' || String(character.name) === 'Add Column' || String(character.name) === 'Sort' || String(character.name) === 'Groupby') {
          return `
                <div class="function draggable" draggable="true">
                    <h2>${character.name}</h2>
                    <h3 class="heartIcon" onClick="addToFav('${character.name}' )" value=${character.name}><i class="${icon}"></i></h3>
                    <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueidJoin}" data-element_comp="${dataID}"  onClick="popupOpen();takeFuncInput('${character.name}','${uniqueidJoin}','${indexCount}',this)">&#11167;</a>
                    <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueidJoin}" data-element_comp="${dataID}"  onClick="deleteElement(this)">&#10006;</span>
                </div>
            `
        } else if (String(character.name) === 'Rename and Drop') {
          return `
                    <div class="function draggable" draggable="true">
                        <h2>${character.name}</h2>
                        <h3 class="heartIcon" onClick="addToFav('${character.name}' )" value=${character.name}><i class="${icon}"></i></h3>
                        <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueidRename}" data-element_comp="${dataID}" onClick="popupOpen();takeFuncInput('${character.name}','${uniqueidRename}','${indexCount}',this)">&#11167;</a>
                        <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueidRename}" data-element_comp="${dataID}"  onClick="deleteElement(this)">&#10006;</span>
                    </div>
                `
        } else if (String(character.name) === 'Pivot' || String(character.name) === 'Unpivot') {
          return `
                    <div class="function draggable" draggable="true">
                        <h2>${character.name}</h2>
                        <h3 class="heartIcon" onClick="addToFav('${character.name}' )" value=${character.name}><i class="${icon}"></i></h3>
                        <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueidPivot}" data-element_comp="${dataID}" onClick="popupOpen();takeFuncInput('${character.name}','${uniqueidPivot}','${indexCount}',this)">&#11167;</a>
                        <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueidPivot}" data-element_comp="${dataID}"  onClick="deleteElement(this)">&#10006;</span>
                      </div>
                `

        } else if (String(character.name) === 'Concat Columns') {
          return `
                    <div class="function draggable" draggable="true">
                        <h2>${character.name}</h2>
                        <h3 class="heartIcon" onClick="addToFav('${character.name}' )" value=${character.name}><i class="${icon}"></i></h3>
                        <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueidConcat}" data-element_comp="${dataID}" onClick="popupOpen();takeFuncInput('${character.name}','${uniqueidConcat}','${indexCount}',this)">&#11167;</a>
                        <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueidConcat}" data-element_comp="${dataID}"  onClick="deleteElement(this)">&#10006;</span>
                    </div>
                `
        } else {
          return `
                <div class="function draggable" draggable="true">
                    <h2>${character.name}</h2>
                    <h3 class="heartIcon" onClick="addToFav('${character.name}' )" value=${character.name}><i class="${icon}"></i></h3>
                    <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueidMaths}" data-element_comp="${dataID}" onClick="popupOpen();takeFuncInput('${character.name}','${uniqueidMaths}','${indexCount}',this)">&#11167;</a>
                    <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueidMaths}" data-element_comp="${dataID}"  onClick="deleteElement(this)">&#10006;</span>
                </div>
            `
        }
      }
    })
    .join('')
  functionsList.innerHTML = htmlString
  // adding drag event listeners
  draggables = document.querySelectorAll('.draggable')
  draggables.forEach(draggable => {
    draggable.addEventListener('dragstart', (e) => {
      draggable.classList.add('dragging')
    })

    draggable.addEventListener('dragend', (e) => {
      draggable.classList.remove('dragging')
      displayPreviews()
      displayCharacters(characters)
      displayFav(favFunctionList)
    })
  })
}

// draggable
const dragAreas = document.querySelectorAll('.dragAreaPossible')

dragAreas.forEach(dragArea => {
  dragArea.addEventListener('dragover', e => {
    e.preventDefault()
    const afterElement = getDragAfterElement(dragArea, e.clientY)
    const draggable = document.querySelector('.dragging')

    if (afterElement == null) {
      dragArea.appendChild(draggable)

      if (dragArea.querySelector('.EbOverlay')) {
        dragArea.querySelector('.EbOverlay').className = 'EBshow'
      }

      if (dragArea.querySelector('.heartIcon')) {
        dragArea.querySelector('.heartIcon').className = 'EBhide'
      }

      if (dragArea.querySelector('.RemoveIcon')) {
        dragArea.querySelector('.RemoveIcon').className = 'EBhide'
      }
    } else {
      dragArea.insertBefore(draggable, afterElement)

      if (dragArea.querySelector('.EbOverlay')) {
        dragArea.querySelector('.EbOverlay').className = 'EBshow'
      }

      if (dragArea.querySelector('.heartIcon')) {
        dragArea.querySelector('.heartIcon').className = 'EBhide'
      }

      if (dragArea.querySelector('.RemoveIcon')) {
        dragArea.querySelector('.RemoveIcon').className = 'EBhide'
      }
    }
  })
})

function getDragAfterElement(container, y) {
  const draggableElements = [...container.querySelectorAll('.draggable:not(.dragging)')]

  return draggableElements.reduce((closest, child) => {
    const box = child.getBoundingClientRect()
    const offset = y - box.top - box.height / 2
    if (offset > 0 && offset < closest.offset) {
      return { offset: offset, element: child }
    } else {
      return closest
    }
  }, { offset: Number.NEGATIVE_INFINITY }).element
}

// Popup Open
function popupOpen() { // eslint-disable-line no-unused-vars
  document.getElementById('popup').style.display = 'block'
  document.getElementById('overlay').style.display = 'block'
}
// Popup Close
function popupClose() { // eslint-disable-line no-unused-vars
  document.getElementById('popup').style.display = 'none'
  document.getElementById('overlay').style.display = 'none'
}

// htmlgenerator code starts here

function rebuild() {
  $('#functionsList').empty()
  const functionDiv = document.querySelector('.ebFunctions')
  const functions = functionDiv.querySelectorAll('.function')
  const listOfFunctions = []
  functions.forEach(item => {
    listOfFunctions.push(item.querySelector('h2').innerText)
  })
  const indexCount1 = listOfFunctions.length
  let dataID
  const minm = 1000000000000
  const maxm = 9999999999999
  const uniqueidMaths = 'applyMathOps' + (Math.floor(Math.random() * (maxm - minm + 1)) + minm).toString()
  const uniqueidJoin = 'mergeAndJoin' + (Math.floor(Math.random() * (maxm - minm + 1)) + minm).toString()
  const uniqueidRename = 'renameColumn' + (Math.floor(Math.random() * (maxm - minm + 1)) + minm).toString()
  const uniqueidPivot = 'pivotAndTranspose' + (Math.floor(Math.random() * (maxm - minm + 1)) + minm).toString()
  const uniqueidConcat = 'concatColumn' + (Math.floor(Math.random() * (maxm - minm + 1)) + minm).toString()

  if (typeof ($('#tname').val()) === 'undefined') {
    dataID = 'comp'
  } else {
    dataID = 'datamgm'
  }

  const htmlString = funcDic
    .map((character) => {
      if (String(character.name) === 'Left Join' || String(character.name) === 'Right Join' || String(character.name) === 'Inner Join' || String(character.name) === 'Outer Join' || String(character.name) === 'Append and Concatenate' || String(character.name) === 'Filter' || String(character.name) === 'Add Column' || String(character.name) === 'Sort' || String(character.name) === 'Groupby') {
        return `
                <div class="function draggable" draggable="true">
                    <h2>${character.name}</h2>
                    <h3 class="heartIcon" onClick="addToFav('${character.name}' )" value=${character.name}><i class="fas fa-thumbs-up"></i></h3>
                    <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueidJoin}" data-element_comp="${dataID}"  onClick="popupOpen();takeFuncInput('${character.name}','${uniqueidJoin}','${indexCount1}',this)">&#11167;</a>
                    <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueidJoin}" data-element_comp="${dataID}"  onClick="deleteElement(this)">&#10006;</span>
                    </div>
            `
      } else if (String(character.name) === 'Rename and Drop') {
        return `
                    <div class="function draggable" draggable="true">
                        <h2>${character.name}</h2>
                        <h3 class="heartIcon" onClick="addToFav('${character.name}' )" value=${character.name}><i class="fas fa-thumbs-up"></i></h3>
                        <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueidRename}" data-element_comp="${dataID}"  onClick="popupOpen();takeFuncInput('${character.name}','${uniqueidRename}','${indexCount1}',this)">&#11167;</a>
                        <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueidRename}" data-element_comp="${dataID}"  onClick="deleteElement(this)">&#10006;</span>
                        </div>
                `
      } else if (String(character.name) === 'Pivot' || String(character.name) === 'Unpivot') {
        return `
                    <div class="function draggable" draggable="true">
                        <h2>${character.name}</h2>
                        <h3 class="heartIcon" onClick="addToFav('${character.name}' )" value=${character.name}><i class="fas fa-thumbs-up"></i></h3>
                        <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueidPivot}" data-element_comp="${dataID}"  onClick="popupOpen();takeFuncInput('${character.name}','${uniqueidPivot}','${indexCount1}',this)">&#11167;</a>
                        <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueidPivot}" data-element_comp="${dataID}"  onClick="deleteElement(this)">&#10006;</span>
                        </div>
                `

      } else if (String(character.name) === 'Concat Columns') {
        return `
                    <div class="function draggable" draggable="true">
                        <h2>${character.name}</h2>
                        <h3 class="heartIcon" onClick="addToFav('${character.name}' )" value=${character.name}><i class="fas fa-thumbs-up"></i></h3>
                        <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueidConcat}" data-element_comp="${dataID}"  onClick="popupOpen();takeFuncInput('${character.name}','${uniqueidConcat}','${indexCount1}',this)">&#11167;</a>
                        <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueidConcat}" data-element_comp="${dataID}"  onClick="deleteElement(this)">&#10006;</span>
                        </div>
                `
      } else {
        return `
                <div class="function draggable" draggable="true">
                    <h2>${character.name}</h2>
                    <h3 class="heartIcon" onClick="addToFav('${character.name}' )" value=${character.name}><i class="fas fa-thumbs-up"></i></h3>
                    <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueidMaths}" data-element_comp="${dataID}"  onClick="popupOpen();takeFuncInput('${character.name}','${uniqueidMaths}','${indexCount1}',this)">&#11167;</a>
                    <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueidMaths}" data-element_comp="${dataID}"  onClick="deleteElement(this)">&#10006;</span>
                    </div>
            `
      }
    })
    .join('')
  $('#functionsList').append(htmlString)
  draggables = document.querySelectorAll('.draggable')
  draggables.forEach(draggable => {
    draggable.addEventListener('dragstart', (e) => {
      draggable.classList.add('dragging')
    })

    draggable.addEventListener('dragend', (e) => {
      draggable.classList.remove('dragging')
      rebuild()
      displayPreviews()
      // displayCharacters(characters)
    })
  })
}

function eqBuilder(scenarioName, elementIdentifier, modelelementid) { // eslint-disable-line no-unused-vars
  let dataID
  $('.closeEqBuilder').on('click', function () {
    if(modelelementid == "modelelementid2"){
      $("#where_condition").css("display","block")
      $("#export_data_equ").css("display","block")
    }
    $('#functionsList').empty()
    $('#selectedTablesDiv').empty()
    $('#table-columns').empty()
    selectedTables = {}
    $('#filter-table').empty()
    compValProcess = false
    compValProcessName = ""
    compValVarName = []
    const minm = 1000000000000
    const maxm = 9999999999999
    const uniqueidMaths = 'applyMathOps' + (Math.floor(Math.random() * (maxm - minm + 1)) + minm).toString()
    const uniqueidJoin = 'mergeAndJoin' + (Math.floor(Math.random() * (maxm - minm + 1)) + minm).toString()
    const uniqueidRename = 'renameColumn' + (Math.floor(Math.random() * (maxm - minm + 1)) + minm).toString()
    const uniqueidPivot = 'pivotAndTranspose' + (Math.floor(Math.random() * (maxm - minm + 1)) + minm).toString()
    const uniqueidConcat = 'concatColumn' + (Math.floor(Math.random() * (maxm - minm + 1)) + minm).toString()

    if (typeof ($('#tname').val()) === 'undefined' || compValProcess) {
      dataID = 'comp'
    } else {
      dataID = 'datamgm'
    }

    const htmlString = funcDic
      .map((character) => {
        if (String(character.name) === 'Left Join' || String(character.name) === 'Right Join' || String(character.name) === 'Inner Join' || String(character.name) === 'Outer Join' || String(character.name) === 'Append and Concatenate' || String(character.name) === 'Filter' || String(character.name) === 'Add Column' || String(character.name) === 'Sort' || String(character.name) === 'Groupby' || String(character.name) === 'Networkdays' || String(character.name) === 'Networkdays.Intl' || String(character.name) === 'Workdays' || String(character.name) === 'Workdays.Intl') {
          return `
                <div class="function draggable" draggable="true">
                    <h2>${character.name}</h2>
                    <h3 class="heartIcon" onClick="addToFav('${character.name}' )" value=${character.name}><i class="fas fa-thumbs-up"></i></h3>
                    <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueidJoin}" data-element_comp="${dataID}"  onClick="popupOpen();takeFuncInput('${character.name}','${uniqueidJoin}','${0}',this)">&#11167;</a>
                    <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueidJoin}" data-element_comp="${dataID}"  onClick="deleteElement(this)">&#10006;</span>
                    </div>
            `
        } else if (String(character.name) === 'Rename and Drop') {
          return `
                    <div class="function draggable" draggable="true">
                        <h2>${character.name}</h2>
                        <h3 class="heartIcon" onClick="addToFav('${character.name}' )" value=${character.name}><i class="fas fa-thumbs-up"></i></h3>
                        <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueidRename}" data-element_comp="${dataID}"  onClick="popupOpen();takeFuncInput('${character.name}','${uniqueidRename}','${0}',this)">&#11167;</a>
                        <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueidRename}" data-element_comp="${dataID}"  onClick="deleteElement(this)">&#10006;</span>
                        </div>
                `
        } else if (String(character.name) === 'Pivot' || String(character.name) === 'Unpivot') {
          return `
                    <div class="function draggable" draggable="true">
                        <h2>${character.name}</h2>
                        <h3 class="heartIcon" onClick="addToFav('${character.name}' )" value=${character.name}><i class="fas fa-thumbs-up"></i></h3>
                        <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueidPivot}" data-element_comp="${dataID}"  onClick="popupOpen();takeFuncInput('${character.name}','${uniqueidPivot}','${0}',this)">&#11167;</a>
                        <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueidPivot}" data-element_comp="${dataID}"  onClick="deleteElement(this)">&#10006;</span>
                        </div>
                `
        } else if (String(character.name) === 'Concat Columns') {
          return `
                    <div class="function draggable" draggable="true">
                        <h2>${character.name}</h2>
                        <h3 class="heartIcon" onClick="addToFav('${character.name}' )" value=${character.name}><i class="fas fa-thumbs-up"></i></h3>
                        <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueidConcat}" data-element_comp="${dataID}"  onClick="popupOpen();takeFuncInput('${character.name}','${uniqueidConcat}','${0}',this)">&#11167;</a>
                        <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueidConcat}" data-element_comp="${dataID}"  onClick="deleteElement(this)">&#10006;</span>
                        </div>
                `
        } else {
          return `
                <div class="function draggable" draggable="true">
                    <h2>${character.name}</h2>
                    <h3 class="heartIcon" onClick="addToFav('${character.name}' )" value=${character.name}><i class="fas fa-thumbs-up"></i></h3>
                    <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueidMaths}" data-element_comp="${dataID}"  onClick="popupOpen();takeFuncInput('${character.name}','${uniqueidMaths}','${0}',this)">&#11167;</a>
                    <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueidMaths}" data-element_comp="${dataID}"  onClick="deleteElement(this)">&#10006;</span>
                    </div>
            `
        }
      })
      .join('')
    functionsList.innerHTML = htmlString
    draggables = document.querySelectorAll('.draggable')
    draggables.forEach(draggable => {
      draggable.addEventListener('dragstart', (e) => {
        draggable.classList.add('dragging')
      })

      draggable.addEventListener('dragend', (e) => {
        draggable.classList.remove('dragging')
        rebuild()
        displayPreviews()
        // displayCharacters(characters)
      })
    })
  })
  $('#EBDisplayButtonID').attr('data-name', scenarioName + elementIdentifier)
  MelementID = $(`#modelName_${modelelementid}`).attr('data-model_name')
  $('#EBDisplayButtonID').attr('data-p_table_name', MelementID)
  if(modelelementid == "modelelementid2"){
    $("#where_condition").css("display","none")
    $("#export_data_equ").css("display","none")
  }
  $('#EBDisplayButtonID,.eqbuilder_mul_Cl,.val_based_msg_global_var_eq').off('click').on('click', function () {
    $('#EBDisplayModel').modal('show')
    counter = 0
    $('.ebDataElementsDiv').remove()
    $('.ebFunctions').find('.function').remove()
    $('.ebSteps').find('#stepNumsEb').empty()
    $('#functionPreviews').empty()
    if (typeof ($('#tname').val()) === 'undefined' || compValProcess) {
      dataID = 'comp'
    } else {
      dataID = 'datamgm'
    }
    $.ajax({
      url: `/users/${urlPath}/computationModule/`,
      data: {
        model_name: scenarioName + elementIdentifier,
        operation: 'eq_reload_config'
      },
      type: 'POST',
      dataType: 'json',
      success: function (data) {
        $('#exampledata1').remove()
        $('#exampledata1_wrapper').remove()

        if (Object.keys(data.import_data).length == 0) {
          idenFlag2 = "scen_new"
        } else {
          idenFlag2 = "scen_old"
        }
        for (let [key, value] of Object.entries(data.import_data)) {
          for (let [k, v] of Object.entries(value)) {
            let importID = ""
            if (k == "ele_id") {
              importID = v

                // eslint-disable-next-line no-undef
                filter_list[importID] = []
                // eslint-disable-next-line no-undef
                $.ajax({
                  url: `/users/${urlPath}/computationModule/`,
                  data: {
                    model_name: scenarioName + elementIdentifier,
                    element_id: importID,
                    operation: 'import_config',
                    model_element_id: MelementID
                  },
                  type: 'POST',
                  dataType: 'json',
                  success: function (data1) {
                    $('#elementNameImportD').val('').trigger('change')
                    $('#dropdown1').val('').trigger('change')
                    $('#dropdown1').val('').trigger('select2:select')
                    $('#selectTable').val('').trigger('change')
                    $('#selectTable').val('').trigger('select2:select')
                    $('selectColumn').empty()
                    $('#filter-table').empty()
                    $('#Table').css('display', 'none')
                    $('#Column').css('display', 'none')
                    $('#csvForm').css('display', 'none')
                    $('#where_condition').css('display', 'none')
                    $('#data_btn').css('display', 'none')
                    $('#import_data_global_var_div').css('display', 'none')
                    $('#model_output_selection').css('display', 'none')
                    $('#selectModelName').val('').trigger('change')
                    $('#selectOutputName').val('').trigger('change')
                    $('#apiForm').css('display', 'none')
                    $('#clear-editor').trigger('click')

                  if (Object.keys(data1).length > 0) {
                    for (let i = 0; i < data1.element_config.condition.length; i++) {
                      if (!(data1.element_config.condition[i].hasOwnProperty('table'))) {
                        data1.element_config.condition[i]["table"] = data1.table_name
                      }
                    }
                  }
                  const elementConfigDict = data1.element_config
                  if(compValProcess){
                    $('#where_condition').attr('data-data', JSON.stringify(({
                      elementName: data1.element_id,
                      data3: data1.element_config
                    }))
                    )
                  }else{
                    $('#where_condition').attr('data-data', JSON.stringify(({
                      elementName: scenarioName + elementIdentifier,
                      data3: data1.element_config
                    }))
                    )
                  }

                  const elementID = data1.element_id
                  const dataSource = elementConfigDict.inputs.Data_source
                  const tableName = elementConfigDict.inputs.Table
                  const condition = elementConfigDict.condition
                  // eslint-disable-next-line no-undef
                  filter_list[elementID] = condition

                  if (String(dataSource) === 'Database') {
                    $('#Table').css('display', 'block')
                    $('#Column').css('display', 'block')
                    $('#csvForm').css('display', 'none')
                    $('#where_condition').css('display', 'inline-block')
                    if(modelelementid == "modelelementid2"){
                      $("#where_condition").css("display","none")
                      $("#export_data_equ").css("display","none")
                    }

                    $('#dropdown1').val(dataSource).trigger('change')
                    $('#dropdown1').val(dataSource).trigger('select2:select')

                    $('#selectTable').val(tableName).trigger('change')
                    $('#selectTable').val(tableName).trigger('select2:select')
                    // Where Condition
                    if (condition.length > 0) {
                      const formFields = data1.form_fields
                      $('#filter-table').empty()
                      for (let i = 0; i < condition.length; i++) {
                        const Cname = (condition[i].column_name)
                        const cond = (condition[i].condition)
                        const iVal = (condition[i].input_value)
                        const gVar = (condition[i].globalVariable)
                        const STRING = formFields[Cname]
                        $('#filter-table').append(STRING)
                        if (condition[i].hasOwnProperty("table")) {
                          $('#filter-table').find('tr').eq(-1).attr("data-table", condition[i]["table"])
                        }
                        $('#filter-table').find('tr').eq(-1).find('td').eq(3).remove()
                        const colDType = $('#filter-table').find('tr').eq(-1).find('input').attr('type')
                        $('#filter-table').find('tr').eq(-1).append(
                          `
                            <td class="dt-center">
                            <div class="" style="max-width:25em;">
                              <select class="form-control select2bs4" name=${Cname} data-dropdown_purpose="select_global_variable" data-type="${colDType}">
                                <option value="" selected disabled>Select Global Variable</option>
                              </select>
                            </div>
                            </td>
                            `
                        )
                        if(compValProcess){
                          $('#filter-table').find('tr').eq(-1).append(
                            `<td class="dt-center">
                            <div class="" style="max-width:25em;">
                              <input type="text" placeholder="Default value" name=${Cname} data-type="${colDType}" maxlength="100" class="textinput textInput form-control" required="">
                            </div>
                          </td >`
                          )
                        }
                        let gVarNameList = []
                        if (String(colDType) === 'text') {
                          gVarNameList = data1.global_text_list
                        } else if (String(colDType) === 'number') {
                          gVarNameList = data1.global_number_list
                        } else if (String(colDType) === 'date') {
                          gVarNameList = data1.global_date_list
                        } else if (String(colDType) === 'datetime-local') {
                          gVarNameList = data1.global_datetime_list
                        };
                        for (let i = 0; i < gVarNameList.length; i++) {
                          const varName = gVarNameList[i]
                          $('#filter-table').find('tr').eq(-1).find('select').eq(1).append(`<option value='${varName}'> ${varName}</option>`)
                        };

                        if(compValProcess){
                          for (let i = 0; i < compValVarName.length; i++) {
                            let varName = compValVarName[i]
                            $('#filter-table').find('tr').eq(-1).find('select').eq(1).append(`<option value='${varName}'> ${varName}</option>`)
                          };
                        }

                        $('#filter-table').find(`tr:nth-child(${i + 1})`).find('td:nth-child(2) > div > select').val(cond).trigger('change')
                        $('#filter-table').find(`tr:nth-child(${i + 1})`).find('td:nth-child(3) > div > input').val(iVal).trigger('change')
                        $('#filter-table').find(`tr:nth-child(${i + 1})`).find('td:nth-child(4) > div > select').val(gVar).trigger('change')
                        if(compValProcess){
                          $('#filter-table').find(`tr:nth-child(${i + 1})`).find('td:nth-child(5) > div > input').val(iVal).trigger('change')
                          $('#filter-table').find(`tr:nth-child(${i + 1})`).find('td:nth-child(3) > div > input').val("").trigger('change')
                        }
                        $('#filter-table').find('tr').eq(-1).find('select').each(function () {
                          $(this).select2()
                        })
                        $('.remove_filter').on('click', removefilter)
                      }
                      function removefilter() {
                        $(this).closest('tr').remove()
                      }
                    } else {
                      $('#filter-table').empty()
                    }
                  }
                  else {
                    $('#dropdown1').css('display', 'block')
                  }
                },
                error: function () {
                  Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                }
              })
            }
          }
        }

        let exportflag1 = 0
        // eslint-disable-next-line no-unused-vars
        for (const [key, value] of Object.entries(data.func_data)) {
          // eslint-disable-next-line
          for (const [k, v] of Object.entries(value)) {
            if (String(value.text) === 'Export data') {
              exportflag1 = 1
              break
            }
          }
        }
        if (exportflag1) {
          counter = Object.keys(data.func_data).length - 1
        } else {
          counter = Object.keys(data.func_data).length
        }

        const funcList = []
        let exportElemID = ''

        let count_ = 0
        for (const [key, value] of Object.entries(data.func_data)) { // eslint-disable-line no-unused-vars
          if (String(value.text) !== 'Export data') {
            if (String(value.text) === 'Ceiling' || String(value.text) === 'Floor' || String(value.text) === 'Floor' ||
              String(value.text) === 'Odd' || String(value.text) === 'Even' || String(value.text) === 'Round' ||
              String(value.text) === 'Round_Up' || String(value.text) === 'Round_Down' || String(value.text) === 'Truncate'
            ) {
              value.text = 'Round'
              funcList.push(value.text)
            } else if (String(value.text) === 'Log_base' || String(value.text) === 'Exponential' || String(value.text) === 'Natural_Log') {
              value.text = 'Log'
              funcList.push(value.text)
            } else if (String(value.text) === 'Power') {
              value.text = 'Square root'
              funcList.push(value.text)
            } else if (String(value.text) === 'left') {
              value.text = 'Left Join'
              funcList.push(value.text)
            } else if (String(value.text) === 'right') {
              value.text = 'Right Join'
              funcList.push(value.text)
            } else if (String(value.text) === 'inner') {
              value.text = 'Inner Join'
              funcList.push(value.text)
            } else if (String(value.text) === 'outer') {
              value.text = 'Outer Join'
              funcList.push(value.text)
            } else if (String(value.text) == 'append') {
              value.text = 'Append and Concatenate'
              func_list.push(value.text)
            } else if (String(value.text) === 'filter') {
              value.text = 'Filter'
              funcList.push(value.text)
            } else if (String(value.text) === 'AddColumn') {
              value.text = 'Add Column'
              funcList.push(value.text)
            } else if (String(value.text) === 'unpivot') {
              value.text = 'Unpivot'
              funcList.push(value.text)
            } else if (String(value.text) === 'sort') {
              value.text = 'Sort'
            } else if (String(value.text) === 'groupby') {
              value.text = 'Groupby'
              funcList.push(value.text)
            } else if (String(value.text) === 'pivot') {
              value.text = 'Pivot'
              funcList.push(value.text)
            } else {
              funcList.push(value.text)
            }

            $('.ebFunctions').append(`<div class="function draggable" draggable="true">
                            <h2>${value.text}</h2>
                            <h3 class="EBhide" onclick="addToFav('${value.text}')" value="${value.text}"><i class="fas fa-thumbs-up"></i></h3>
                            <a title="configure" href="#" name="Open" class="EBshow" id="open-overlay" data-element_id="${value.ele_id}" data-element_comp="${dataID}" onclick="popupOpen();takeFuncInput('${value.text}','${value.ele_id}','${value.order}')">⮟</a>
                            <span title="delete" style="display:none;" class="deleteitem" data-element_id="${value.ele_id}"  onClick="deleteElement(this)">&#10006;</span>
                            </div>`)

            $('#stepNumsEb').append(`<h2 class="stepNumberEB"> ${value.order + 1}</h2>`)

            const minm = 1000000000000
            const maxm = 9999999999999
            const uniqueidMaths = 'applyMathOps' + (Math.floor(Math.random() * (maxm - minm + 1)) + minm).toString()
            const uniqueidJoin = 'mergeAndJoin' + (Math.floor(Math.random() * (maxm - minm + 1)) + minm).toString()
            const uniqueidRename = 'renameColumn' + (Math.floor(Math.random() * (maxm - minm + 1)) + minm).toString()
            const uniqueidPivot = 'pivotAndTranspose' + (Math.floor(Math.random() * (maxm - minm + 1)) + minm).toString()
            const uniqueidConcat = 'concatColumn' + (Math.floor(Math.random() * (maxm - minm + 1)) + minm).toString()
            count_++
            const htmlString = funcDic
              .map((character) => {
                if (String(character.name) === 'Left Join' || String(character.name) === 'Right Join' || String(character.name) === 'Inner Join' || String(character.name) === 'Outer Join' || String(character.name) === 'Append and Concatenate' || String(character.name) === 'Filter' || String(character.name) === 'Add Column' || String(character.name) === 'Sort' || String(character.name) === 'Groupby' || String(character.name) === 'Networkdays' || String(character.name) === 'Networkdays.Intl' || String(character.name) === 'Workdays' || String(character.name) === 'Workdays.Intl') {
                  return `<div class="function draggable" draggable="true">
                                <h2>${character.name}</h2>
                                <h3 class="heartIcon" onClick="addToFav('${character.name}' )" value=${character.name}><i class="fas fa-thumbs-up"></i></h3>
                                <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueidJoin}" data-element_comp="${dataID}"  onClick="popupOpen();takeFuncInput('${character.name}','${uniqueidJoin}','${count_}',this)">&#11167;</a>
                                <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueidJoin}" data-element_comp="${dataID}"  onClick="deleteElement(this)">&#10006;</span>
                                </div>
    `
                } else if (String(character.name) === 'Rename and Drop') {
                  return `<div class="function draggable" draggable="true">
                                    <h2>${character.name}</h2>
                                    <h3 class="heartIcon" onClick="addToFav('${character.name}' )" value=${character.name}><i class="fas fa-thumbs-up"></i></h3>
                                    <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueidRename}" data-element_comp="${dataID}"  onClick="popupOpen();takeFuncInput('${character.name}','${uniqueidRename}','${count_}',this)">&#11167;</a>
                                    <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueidRename}" data-element_comp="${dataID}"  onClick="deleteElement(this)">&#10006;</span>
                                    </div>
    `
                } else if (String(character.name) === 'Pivot' || String(character.name) === 'Unpivot') {
                   return `
                    <div class="function draggable" draggable = "true" >
                                    <h2>${character.name}</h2>
                                    <h3 class="heartIcon" onClick="addToFav('${character.name}' )" value=${character.name}><i class="fas fa-thumbs-up"></i></h3>
                                    <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueidPivot}" data-element_comp="${dataID}"  onClick="popupOpen();takeFuncInput('${character.name}','${uniqueidPivot}','${count_}',this)">&#11167;</a>
                                    <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueidPivot}" data-element_comp="${dataID}"  onClick="deleteElement(this)">&#10006;</span>
                                    </div >
                          `

                } else if (String(character.name) === 'Concat Columns') {
                  return `
                                <div class="function draggable" draggable="true">
                                    <h2>${character.name}</h2>
                                    <h3 class="heartIcon" onClick="addToFav('${character.name}' )" value=${character.name}><i class="fas fa-thumbs-up"></i></h3>
                                    <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueidConcat}" data-element_comp="${dataID}"  onClick="popupOpen();takeFuncInput('${character.name}','${uniqueidConcat}','${count_}',this)">&#11167;</a>
                                    <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueidConcat}" data-element_comp="${dataID}"  onClick="deleteElement(this)">&#10006;</span>
                                    </div>
              `
                } else {
                  return `<div class="function draggable" draggable = "true" >
                                <h2>${character.name}</h2>
                                <h3 class="heartIcon" onClick="addToFav('${character.name}' )" value=${character.name}><i class="fas fa-thumbs-up"></i></h3>
                                <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueidMaths}" data-element_comp="${dataID}"  onClick="popupOpen();takeFuncInput('${character.name}','${uniqueidMaths}','${count_}',this)">&#11167;</a>
                                <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueidMaths}" data-element_comp="${dataID}"  onClick="deleteElement(this)">&#10006;</span>
                                </div > `
                }
              })
              .join('')
            functionsList.innerHTML = htmlString

            draggables = document.querySelectorAll('.draggable')
            draggables.forEach(draggable => {
              draggable.addEventListener('dragstart', (e) => {
                draggable.classList.add('dragging')
              })

              draggable.addEventListener('dragend', (e) => {
                draggable.classList.remove('dragging')
                rebuild()
                displayPreviews()
                // displayCharacters(characters)
              })
            })
          } else if (String(value.text) === 'Export data') {
            exportElemID = value.ele_id
            if (exportElemID) {
              $('#exportEqData').attr('data-element_id', exportElemID)
            }
          }
        }

        if (String(counter) === '1') {
          $('.ebFunctions').find('div').eq(counter - 1).find('span').css('display', 'block')
        } else {
          $('.ebFunctions').find('div').eq(counter - 1).find('span').css('display', 'block')
          $('.ebFunctions').find('div').eq(counter - 2).find('span').css('display', 'none')
        }
        for (const [key, value] of Object.entries(data.import_data)) { // eslint-disable-line no-unused-vars
          let tName1, eeId1
          for (const [k, v] of Object.entries(value)) {
            if (String(k) === 'table_name') {
              tName1 = v
            }

            if (String(k) === 'ele_id') {
              eeId1 = v
            }
          }
          tempdd[tName1] = eeId1
        }

        for (let i = 0; i < funcList.length; i++) {
          const div1 = document.createElement('div')
          const btn = document.createElement('button')
          div1.className = 'ebDataElementsDiv dragAreaPossible'
          btn.className = 'btn btn-primary btn-xs mx-2 rounded px-2'
          btn.innerHTML = 'Data'
          btn.addEventListener('click', function () {
            const columnssList = []
            const columnsList = []
            let sTableName = []
            let tEleID = []
            const table1 = []
            const table2 = []

            const tableName = new Set()
            const eleID = new Set()

            const b = $(this).parent('.ebDataElementsDiv').find('.ColumnItem')
            for (let i = 0; i < b.length; i++) {
              tableName.add(b[i].getAttribute('data-table'))
              eleID.add(b[i].getAttribute('data-element_id'))
            }

            sTableName = Array.from(tableName)
            tEleID = Array.from(eleID)

            const bb = $(this).parent('.ebDataElementsDiv').find('.ColumnItem')

            if (sTableName.length > 1) {
              for (let i = 0; i < sTableName.length - 1; i++) {
                const currTable = sTableName[i]

                for (let j = 0; j < bb.length; j++) {
                  if (String(bb[j].getAttribute('data-table')) === currTable) {
                    table1.push(bb[j].querySelector('p').innerText)
                  } else {
                    table2.push(bb[j].querySelector('p').innerText)
                  }
                }

                columnssList.push(table1)
                columnssList.push(table2)
              }
            } else {
              const a = $(this).parent('.ebDataElementsDiv').find('.ColumnItem').find('p')
              for (let i = 0; i < a.length; i++) {
                columnsList.push(a[i].innerText)
              }
              columnssList.push(columnsList)
            }
            let currentTable_flow
            if (typeof (computationCondition) == 'function' && !compValProcess) {
              currentTable_flow = 'Yes'
            } else {
              currentTable_flow = 'No'
            }
            for (let j = 0; j < sTableName.length; j++) {
              const configDictT = {
                function: 'Import Data',
                data_mapper: { current_element_name: sTableName[j] },
                inputs: {
                  Data_source: 'Database',
                  Table: sTableName[j],
                  Columns: columnssList[j],
                  global_var: '',
                  parent_table_column: '',
                  current_table_column: '',
                  show_foreignKey_value: false,
                  current_table_flow: currentTable_flow
                },
                condition: {}
              }
              configDictT.outputs = {
                name: '',
                save: ''
              }
              // eslint-disable-next-line no-undef
              if (typeof (filter_list[tEleID[j]]) !== 'undefined') {
                // eslint-disable-next-line no-undef
                configDictT.condition = filter_list[tEleID[j]]
              }

              $('#where_condition').attr('data-data', JSON.stringify(({
                data1: scenarioName + elementIdentifier,
                data2: tEleID[j],
                data3: configDictT,
                elementName: tEleID[j]
              }))
              )

              $.ajax({
                url: `/users/${urlPath}/computationModule/`,
                data: {
                  configList: JSON.stringify({
                    data1: scenarioName + elementIdentifier,
                    data2: tEleID[j],
                    data3: configDictT,
                    element_name: scenarioName + elementIdentifier + Math.floor((Math.random() * 10000000000) + 1)
                  }),
                  operation: 'save_import_data',
                  data_source: 'Database'
                },
                type: 'POST',
                dataType: 'json',
                success: function (context) {
                  if (String(dataID) === 'datamgm') {
                    Swal.fire({icon: 'success',text: 'Import Configuration saved successfully!'});
                  } else if (String(dataID) === 'comp') {
                    if (compValProcess){
                      is_create_val = "yes"
                    }else{
                      is_create_val = "no"
                    }
                    $.ajax({
                      url: `/users/${urlPath}/computationModule/`,
                      data: {
                        operation: 'data_reload',
                        element_id: tEleID[j],
                        model_name: scenarioName + elementIdentifier,
                        model_element_id: MelementID,
                        is_create_val: is_create_val
                      },
                      type: 'POST',
                      dataType: 'json',
                      success: function (data) {
                        Swal.fire({icon: 'success',text: 'Import Configuration saved successfully! Executing the block. Please wait..'});
                        const jobId = data.job_id
                        const runStepBtnId = ''
                        const runStepBtnLoadId = ''
                        fetchJobOutput1(jobId, runStepBtnId, runStepBtnLoadId)
                      },
                      error: function () {
                        Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                      }
                    })
                  }
                },
                error: function () {
                  Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                }
              })
            }
          })
          div1.append(btn)
          dataElementParent.append(div1)

          const dragAreas1 = document.querySelectorAll('.dragAreaPossible')

          dragAreas1.forEach(dragArea1 => {
            dragArea1.addEventListener('dragover', e => {
              e.preventDefault()
              const afterElement = getDragAfterElement1(dragArea1, e.clientY)
              const draggable = document.querySelector('.dragging')

              if (afterElement == null) {
                dragArea1.appendChild(draggable)

                if (dragArea1.querySelector('.EbOverlay')) {
                  dragArea1.querySelector('.EbOverlay').className = 'EBshow'
                }

                if (dragArea1.querySelector('.heartIcon')) {
                  dragArea1.querySelector('.heartIcon').className = 'EBhide'
                }
              } else {
                dragArea1.insertBefore(draggable, afterElement)

                if (dragArea1.querySelector('.EbOverlay')) {
                  dragArea1.querySelector('.EbOverlay').className = 'EBshow'
                }

                if (dragArea1.querySelector('.heartIcon')) {
                  dragArea1.querySelector('.heartIcon').className = 'EBhide'
                }
              }
            })
          })

          function getDragAfterElement1(container, y) {
            const draggableElements = [...container.querySelectorAll('.draggable:not(.dragging)')]
            return draggableElements.reduce((closest, child) => {
              const box = child.getBoundingClientRect()
              const offset = y - box.top - box.height / 2
              if (offset < 0 && offset > closest.offset) {
                return { offset: offset, element: child }
              } else {
                return closest
              }
            }, { offset: Number.POSITIVE_INFINITY }).element
          }

          let joinFirstCount = 0
          let jointCount = 0

          if (String(i) === '0') {
            if (String(funcList[i]) === 'Left Join' || String(funcList[i]) === 'Right Join' || String(funcList[i]) === 'Inner Join' || String(funcList[i]) === 'Outer Join' || String(funcList[i]) === 'Append and Concatenate' || String(funcList[i]) === 'Networkdays' || String(funcList[i]) === 'Networkdays.Intl' || String(funcList[i]) === 'Workdays' || String(funcList[i]) === 'Workdays.Intl') {
              for (const [key, value] of Object.entries(data.import_data)) { // eslint-disable-line no-unused-vars
                if (String(joinFirstCount) === '2') break

                for (const [k, v] of Object.entries(value.columns)) { // eslint-disable-line no-unused-vars
                  $('.ebDataElementsDiv').eq(i).append(`<div class="ColumnItem draggable" draggable = "true" data-table="${value.table_name}" data-element_id="${value.ele_id}" data-element_comp="${dataID}"><p>${v}</p></div>
              `)

                  draggables = document.querySelectorAll('.draggable')
                  draggables.forEach(draggable => {
                    draggable.addEventListener('dragstart', (e) => {
                      draggable.classList.add('dragging')
                    })

                    draggable.addEventListener('dragend', (e) => {
                      draggable.classList.remove('dragging')
                      displayPreviews($('#modelName_parallelogram001652034276123593').text())
                      // displayCharacters(characters)
                    })
                  })
                }
                delete data.import_data[joinFirstCount]
                joinFirstCount = joinFirstCount + 1
              }
            } else {
              for (const [key, value] of Object.entries(data.import_data)) { // eslint-disable-line no-unused-vars
                if (String(jointCount) === '1') break

                for (const [k, v] of Object.entries(value.columns)) { // eslint-disable-line no-unused-vars
                  $('.ebDataElementsDiv').eq(i).append(`<div class="ColumnItem draggable" draggable = "true" data-table="${value.table_name}" data-element_id="${value.ele_id}" data-element_comp="${dataID}" >
                <p>${v}</p>
                    </div>
              `)

                  draggables = document.querySelectorAll('.draggable')
                  draggables.forEach(draggable => {
                    draggable.addEventListener('dragstart', (e) => {
                      draggable.classList.add('dragging')
                    })

                    draggable.addEventListener('dragend', (e) => {
                      draggable.classList.remove('dragging')
                      displayPreviews()
                    })
                  })
                }
                delete data.import_data[jointCount]
                jointCount = jointCount + 1
              }
            }
          } else {
            if (String(funcList[i]) === 'Left Join' || String(funcList[i]) === 'Right Join' || String(funcList[i]) === 'Inner Join' || String(funcList[i]) === 'Outer Join' || String(funcList[i]) === 'Append and Concatenate' || String(funcList[i]) === 'Networkdays' || String(funcList[i]) === 'Networkdays.Intl' || String(funcList[i]) === 'Workdays' || String(funcList[i]) === 'Workdays.Intl') {
              for (const [key, value] of Object.entries(data.import_data)) { // eslint-disable-line no-unused-vars
                if (String(jointCount) === '1') break

                for (const [k, v] of Object.entries(value.columns)) { // eslint-disable-line no-unused-vars
                  $('.ebDataElementsDiv').eq(i).append(`<div class="ColumnItem draggable" draggable = "true" data-table="${value.table_name}" data-element_id="${value.ele_id}" data-element_comp="${dataID}" >
                <p>${v}</p>
                  </div >
              `)

                  draggables = document.querySelectorAll('.draggable')
                  draggables.forEach(draggable => {
                    draggable.addEventListener('dragstart', (e) => {
                      draggable.classList.add('dragging')
                    })

                    draggable.addEventListener('dragend', (e) => {
                      draggable.classList.remove('dragging')
                      displayPreviews()
                    })
                  })
                }
                delete data.import_data[jointCount]
                jointCount = jointCount + 1
              }
            }
          }
        }

        const functionDiv = document.querySelector('.ebFunctions')
        const functions = functionDiv.querySelectorAll('.function')
        const listOfFunctions = []
        functions.forEach(item => {
          listOfFunctions.push(item.querySelector('h2').innerText)
        })

        for (const [key, value] of Object.entries(data.func_data)) { // eslint-disable-line no-unused-vars
          if (String(value.text) !== 'Export data') {
            let myString = ''
            $('#functionPreviews').append(
              `<div class="function" onclick = "" >
              <h2></h2>
              <p style="display:none;"></p>
              </div >
              `)

            if (value.prevString.length > 30) {
              myString = value.prevString.substring(0, 30) + '...'
              $('#functionPreviews').find('.function').eq(value.order).find('p').text(value.prevString)
              $('#functionPreviews').find('.function').eq(value.order).attr('onclick', `popupOpen(); takeFuncInput('${value.text}', '${value.ele_id}', '${value.order}', this)`)
            } else {
              myString = value.prevString
              $('#functionPreviews').find('.function').eq(value.order).find('p').text(value.prevString)
              $('#functionPreviews').find('.function').eq(value.order).attr('onclick', '')
            }

            $('#functionPreviews').find('.function').eq(value.order).find('h2').text(myString)
          }
        }
      },
      error: function () {
        Swal.fire({icon: 'error',text: 'Error! Please try again.'});
      }
    })
  })
  /** ******************** Save eqbuilder *************************/
  $('#save_workflow_equ').click(function (event) {
    event.stopImmediatePropagation()
    const a = $('.ebFunctions').find('div').find('a')
    const configDict = []
    let funcName = ''
    let curr = ''
    let next = ''
    let cc = ''
    let c = ''
    let bb = ''
    let b = ''
    let iList = []
    let finalList
    let n
    let nameM = ""
    if(compValProcess){
      nameM = compValProcessName
    }else{
      nameM = $('#EBDisplayButtonID').attr('data-name')
    }
    for (let i = 0; i < a.length; i++) {
      try {
        b = $('.ebDataElementsDiv').eq(i).find('.ColumnItem')
        b[0].getAttribute('data-element_id')
        cc = $('.ebFunctions').find('div').find('a').eq(i).attr('data-element_id')

        try {
          n = $('.ebFunctions').find('div').find('a').eq(i + 1).attr('data-element_id')
          next = [n]
        } catch (err) {
          next = '#'
        }

        funcName = $('.ebFunctions').find('div').find('h2').eq(i).text()

        const tablesList = new Set()
        for (let i = 0; i < b.length; i++) {
          tablesList.add(b[i].getAttribute('data-element_id'))
        }
        finalList = Array.from(tablesList)
        iList = finalList.slice()

        if ((String(funcName) === 'Left Join' || String(funcName) === 'Right Join' || String(funcName) === 'Inner Join' || String(funcName) === 'Outer Join' || String(funcName) === 'Append and Concatenate' || String(funcName) === 'Networkdays' || String(funcName) === 'Networkdays.Intl' || String(finalList[i]) === 'Workdays' || String(funcName) === 'Workdays.Intl') && String(finalList.length) === '1') {
          bb = $('.ebFunctions').find('div').find('a').eq(i - 1).attr('data-element_id')
          if(funcName=='Networkdays' || funcName=='Networkdays.Intl' || funcName=='Workdays' || funcName=='Workdays.Intl'){
            if (i==0)
            {   if(bb.includes("import")){
                    finalList.push(bb)
                }
            }else{
                finalList.push(bb)
            }
          }else{
              finalList.push(bb)
          }
        }

        b = finalList
        curr = cc
      } catch (err) {
        b = $('.ebFunctions').find('div').find('a').eq(i - 1).attr('data-element_id')
        curr = $('.ebFunctions').find('div').find('a').eq(i).attr('data-element_id')
        funcName = $('.ebFunctions').find('div').find('h2').eq(i).text()

        try {
          n = $('.ebFunctions').find('div').find('a').eq(i + 1).attr('data-element_id')
          next = [n]
          finalList = [b]
          b = [b]
        } catch (err) {
          next = '#'
          b = [b]
        }
      }

      if (String(funcName) === 'Column sum' || String(funcName) === 'Row sum' || String(funcName) === 'Cell sum' ||
        String(funcName) === 'Column subtraction' || String(funcName) === 'Row subtraction' || String(funcName) === 'Cell subtraction' ||
        String(funcName) === 'Column multiplication' || String(funcName) === 'Row multiplication' || String(funcName) === 'Cell multiplication' ||
        String(funcName) === 'Column division' || String(funcName) === 'Row division' || String(funcName) === 'Cell division'
      ) {
        funcName = 'Basic Operations'
      } else if (String(funcName) === 'Round') {
        funcName = 'Rounding Operations'
      } else if (String(funcName) === 'Square root') {
        funcName = 'Power and Root Functions'
      } else if (String(funcName) === 'Log') {
        funcName = 'Log and Exponential Functions'
      } else if (String(funcName) === 'Rename and Drop') {
        funcName = 'Rename Column'
      } else if (String(funcName) === 'Concat Columns') {
        funcName = 'Concat Columns'
      } else if (String(funcName) === 'Filter') {
        funcName = 'Data Transformation Filter'
      } else if (String(funcName) === 'Add Column') {
        funcName = 'Data Transformation Add Column'
      } else if (String(funcName) === 'Pivot') {
        funcName = 'Data Transformation Pivot'
      } else if (String(funcName) === 'Unpivot') {
        funcName = 'Data Transformation Unpivot'
      } else if (String(funcName) === 'Add Time Periods') {
        funcName = 'Add Time Periods'
      } else if (String(funcName) === 'Data Utilities') {
        funcName = 'Data Utilities'
      } else if (String(funcName) === 'Groupby') {
        funcName = 'Data Transformation Groupby'
      } else if (String(funcName) === 'Sort') {
        funcName = 'Data Transformation Sort'
      } else if (String(funcName) === 'Add Fix Column') {
        funcName = 'Add Fix Column'
      } else if (String(funcName) === 'Drop Duplicate') {
        funcName = 'Drop Duplicate'
      } else if (String(funcName) === 'Weighted Average') {
        funcName = 'Elementary Statistics'
      } else if (String(funcName) === 'Sum Product') {
        funcName = 'Elementary Statistics'
      } else if (String(funcName) === 'Fill Missing Values') {
        funcName = 'Missing Value'
      } else if (String(funcName) === 'Delimit Column') {
        funcName = 'Delimit Column'
      } else if (String(funcName) === 'Days') {
        funcName = 'Days'
      } else if (String(funcName) === 'Date') {
        funcName = 'Date'
      } else if (String(funcName) === 'Find and Replace') {
        funcName = 'Find and Replace'
      } else if (String(funcName) === 'Workdays.Intl') {
        funcName = 'Workdays.Intl'
      } else if (String(funcName) === 'Workdays') {
        funcName = 'Workdays'
      } else if (String(funcName) === 'Networkdays.Intl') {
        funcName = 'Networkdays.Intl'
      } else if (String(funcName) === 'Networkdays') {
        funcName = 'Networkdays'
      } else if (String(funcName) === 'Yearfrac') {
        funcName = 'Yearfrac'
      } else if (String(funcName) === 'Year') {
        funcName = 'Year'
      } else if (String(funcName) === 'Weeknum') {
        funcName = 'Weeknum'
      } else if (String(funcName) === 'Weekday') {
        funcName = 'Weekday'
      } else if (String(funcName) === 'Today') {
        funcName = 'Today'
      } else if (String(funcName) === 'Time') {
        funcName = 'Time'
      } else if (String(funcName) === 'Second') {
        funcName = 'Second'
      } else if (String(funcName) === 'Now') {
        funcName = 'Now'
      } else if (String(funcName) === 'Month') {
        funcName = 'Month'
      } else if (String(funcName) === 'Minute') {
        funcName = 'Minute'
      } else if (String(funcName) === 'Isoweeknum') {
        funcName = 'Isoweeknum'
      } else if (String(funcName) === 'Hour') {
        funcName = 'Hour'
      } else if (String(funcName) === 'Eomonth') {
        funcName = 'Eomonth'
      } else if (String(funcName) === 'Days360') {
        funcName = 'Days360'
      } else if (String(funcName) === 'Edate') {
        funcName = 'Edate'
      } else if (String(funcName) === 'Day') {
        funcName = 'Day'
      } else {
        funcName = 'Data Transformation'
      }
      if (String(i) === '0') {
        for (let j = 0; j < finalList.length; j++) {
          c = {
            element_id: finalList[j],
            text: 'Import Data',
            parent: '#',
            child: [
              cc
            ]
          }
          configDict.push(c)
        }
        if (String(i) === String(a.length - 1)) {
          c = {
            element_id: cc,
            text: funcName,
            parent: finalList,
            child: '#'
          }
          if ($('#exportEqData').attr('data-element_id')) {
            c.child = [$('#exportEqData').attr('data-element_id')]
          }
          configDict.push(c)
        } else {
          c = {
            element_id: cc,
            text: funcName,
            parent: finalList,
            child: next
          }
          configDict.push(c)
        }
      } else {
        if (String(iList.length) === '1' && String(funcName) === 'Data Transformation') {
          c = {
            element_id: iList[0],
            text: 'Import Data',
            parent: '#',
            child: [curr]
          }
          configDict.push(c)
        }

        if (String(i) === String(a.length - 1)) {

          if (funcName == "Data Transformation Filter" || funcName == "Data Transformation Add Column" || funcName == 'Data Transformation Sort' || funcName == 'Data Transformation Groupby' || funcName == 'Data Transformation Pivot' || funcName == 'Data Transformation Unpivot') {
            funcName = "Data Transformation"
          }

          c = {
            element_id: curr,
            text: funcName,
            parent: b,
            child: '#'
          }
          if ($('#exportEqData').attr('data-element_id')) {
            c.child = [$('#exportEqData').attr('data-element_id')]
          }
          configDict.push(c)
        } else {

          if (funcName == "Data Transformation Filter" || funcName == "Data Transformation Add Column" || funcName == 'Data Transformation Sort' || funcName == 'Data Transformation Groupby' || funcName == 'Data Transformation Pivot' || funcName == 'Data Transformation Unpivot') {
            funcName = "Data Transformation"
          }

          c = {
            element_id: curr,
            text: funcName,
            parent: b,
            child: next
          }
          configDict.push(c)
        }
      }
    }

    if ($('#exportEqData').attr('data-element_id')) {
      c = {
        element_id: $('#exportEqData').attr('data-element_id'),
        text: 'Export Data',
        parent: [$('.ebFunctions .function').last().find('a').attr('data-element_id')],
        child: '#'
      }
      configDict.push(c)
    }
    let tableListPC = []
    $("#exampledata1").find("thead").find("th").each(function () {
      tableListPC.push($(this).text())
    })
    $('#EBDisplayButtonID').attr("data-tablelist", JSON.stringify(tableListPC))
    $('#EBDisplayButtonID').attr("data-modelnamepc", nameM)
    $('#EBDisplayButtonID').attr("data-config", JSON.stringify(configDict))
    if (typeof (computationCondition) == 'function') {
      computationCondition()
    }
    $.ajax({
      url: `/users/${urlPath}/computationModule/`,
      data: {
        xml: 'innn',
        model_name: nameM,
        operation: 'save_flowchart',
        configList: JSON.stringify({ data3: configDict })
      },
      type: 'POST',
      dataType: 'json',
      success: function (data) {
        if(modelelementid == "modelelementid2"){
          multable_config_comp[multable_viewname] = nameM
        }
        Swal.fire({icon: 'success',text: 'Model saved successfully!'});
      },
      error: function () {
        Swal.fire({icon: 'error',text: 'Error! Failure in saving the Model. Please try again.'});
      }
    })
  })
  /*************************************************************/
  $('#export_data_equ').click(function () {
    $('#exportEqData').find('select').select2()
    let name_ = ""
    if(compValProcess){
      name_ = compValProcessName
    }else{
      name_ = $('#EBDisplayButtonID').attr('data-name')
    }
    if (typeof (name_) === 'undefined') {
      name_ = $('#FileName').attr('data-experimentName')
    }
    const elementID = $('.ebFunctions .function').last().find('a').attr('data-element_id')

    $.ajax({
      url: `/users/${urlPath}/computationModule/`,
      data: {
        operation: 'get_column_id',
        element_id: elementID
      },
      type: 'POST',
      dataType: 'json',
      success: function (data) {
        $('#exportselectColumn1').empty()
        $('#selectUpdateIdentifierCol1').empty()
        $('#selectUpdateCol1').empty()

        for (let i = 0; i < data.columns.length; i++) {
          $('#exportselectColumn1').append(`<option value = '${data.columns[i]}' > ${ data.columns[i] }</option>`)
          $('#selectUpdateIdentifierCol1').append(`<option value = '${data.columns[i]}' > ${ data.columns[i] }</option>`)
          $('#selectUpdateCol1').append(`<option value = '${data.columns[i]}' > ${ data.columns[i] }</option>`)
        };
        if ($('#exportEqData').attr('data-element_id')) {
          $.ajax({
            url: `/users/${urlPath}/computationModule/`,
            data: {
              model_name: name_,
              element_id: $('#exportEqData').attr('data-element_id'),
              operation: 'export_config'
            },
            type: 'POST',
            dataType: 'json',
            success: function (data) {
              if (Object.keys(data).length > 0) {
                const elementConfigDict = data.element_config
                // element_name = elementConfigDict.function
                // element_id = data.element_id
                // output_type = elementConfigDict.inputs.output_type
                // data_source = elementConfigDict.inputs.exportTo

                const tableName = elementConfigDict.inputs.tableName
                const exportType = elementConfigDict.inputs.exportType

                $('#exportTable1').css('display', 'block')
                $('#selectExportTable1').val(tableName).trigger('change')

                $('#selectUpdateIdentifierCol1').attr("data-reload", "yes")
                $('#selectUpdateIdentifierCol1').attr("data-reloaddata", JSON.stringify(elementConfigDict))
                $('#selectUpdateIdentifierCol1').attr("data-exporttype", exportType)
                $('#selectExportDataType1').val(exportType).trigger('select2:select')
                $('#selectExportDataType1').val(exportType).trigger('change')
                if ($('#selectUpdateIdentifierCol1').attr("data-reload") == "yes") {
                  let data1_ = JSON.parse($('#selectUpdateIdentifierCol1').attr("data-reloaddata"))
                  let exportType_ = JSON.parse($('#selectUpdateIdentifierCol1').attr("data-exporttype"))
                  if (exportType_ === 'update') {
                    $('#selectUpdateIdentifierCol1').val(data1_.inputs.selectUpdateIdentifierCol).trigger('change')
                    $('#selectUpdateCol1').val(data1_.inputs.selectUpdateCol).trigger('change')
                  } else {
                    const columnsName = data1_.inputs.columnList
                    $('#exportselectColumn1').val(columnsName).trigger('select2:select')
                    $('#exportselectColumn1').val(columnsName).trigger('change')
                  }
                }
                $('#exportEquModal').modal('show')
              }
            },
            error: function () {
              Swal.fire({icon: 'error',text: 'Error! Please try again.'});
            }
          })
        }
      },
      error: function () {
        Swal.fire({icon: 'error',text: 'Error! Please try again.'});
      }
    })
  })
  $('#selectExportDataType1').off('select2:select').on('select2:select change', function () {
    if ($(this).val() === 'update') {
      $('#updateIdentifierContainer1').css('display', 'block')
      $('#updateColumnContainer1').css('display', 'block')
      $('#exportColumn1').css('display', 'none')
    } else {
      $('#updateIdentifierContainer1').css('display', 'none')
      $('#updateColumnContainer1').css('display', 'none')
      $('#exportColumn1').css('display', 'block')
    }
  })

  var exportEleID = '' // eslint-disable-line no-var
  $('#save_buttonExportData1').click(function () {
    let name_ = ""
    if(compValProcess){
      name_ = compValProcessName
    }else{
      name_ = $('#EBDisplayButtonID').attr('data-name')
    }
    if (typeof (name_) === 'undefined') {
      name_ = $('#FileName').attr('data-experimentName')
    }
    const exportEleID = 'exportData' + (Math.floor(Math.random() * (9999999999999 - 1000000000000 + 1)) + 1000000000000).toString()
    $('#exportEqData').attr('data-element_id', exportEleID)
    const configDict = {
      function: 'Export Data',
      inputs: {
        data: $('.ebFunctions .function').last().find('a').attr('data-element_id'),
        exportTo: 'Database',
        tableName: $('#selectExportTable1').val(),
        exportType: $('#selectExportDataType1').val(),
        output_type: 'individual_export'
      }
    }

    if ($('#selectExportDataType1').val() === 'update') {
      configDict.inputs.selectUpdateIdentifierCol = $('#selectUpdateIdentifierCol1').val()
      configDict.inputs.selectUpdateCol = $('#selectUpdateCol1').val()
    } else {
      configDict.inputs.columnList = $('#exportselectColumn1').val()
    }

    $.ajax({
      url: `/users/${urlPath}/computationModule/`,
      data: {
        config: JSON.stringify({
          model: name_,
          elementID: exportEleID,
          config_dict: configDict
        }),
        operation: 'save_export_data'
      },
      type: 'POST',
      dataType: 'json',
      success: function (data) {
        Swal.fire({icon: 'success',text: 'Configuration saved successfully!'});
      },
      error: function () {
        Swal.fire({icon: 'error',text: 'Error! Failure in saving the configuration. Please check and try again.'});
      }
    })
  })

  $('#run_stepExportData1').click(function () {
    let name_ = ""
    if(compValProcess){
      name_ = compValProcessName
    }else{
      name_ = $('#EBDisplayButtonID').attr('data-name')
    }
    if (typeof (name_) === 'undefined') {
      name_ = $('#FileName').attr('data-experimentName')
    }
    $.ajax({
      url: `/users/${urlPath}/computationModule/`,
      data: {
        operation: 'run_stepExportData',
        element_id: exportEleID,
        model_name: name_
      },
      type: 'POST',
      dataType: 'json',
      success: function (data) {
        Swal.fire({icon: 'error',text: data.msg});
      },
      error: function () {
        Swal.fire({icon: 'error',text: 'Error! Please try again.'});
      }
    })
  })

  $('#btn_search').click(function () {
    const elID = $(this).attr('data-el_id')
    // eslint-disable-next-line no-undef
    filter_list[elID] = []
    const table2 = $('#filter-table')
    table2.find('tr').each(function (i, el) {
      const dict = {}
      dict.column_name = $(this).find('select').attr('name')
      dict.condition = $(this).find('select').eq(0).val()
      dict.input_value = $(this).find('input').eq(0).val()
      dict.globalVariable = $(this).find('select').eq(1).val()
      dict.table = $(this).attr("data-table")
      if (String(dict.globalVariable) === 'null') {
        dict.globalVariable = ''
      }
      if(compValProcess){
        dict.input_value = $(this).find('input').eq(1).val()
      }
      dict.and_or = 'AND'
      // eslint-disable-next-line no-undef
      filter_list[elID].push(dict)
    })
    // eslint-disable-next-line no-undef
    filter_list[elID][filter_list[elID].length - 1].and_or = ''
  })
  $('#where_condition').off('click').on('click',function () {
    const dataData = JSON.parse($(this).attr('data-data'))
    $('#btn_search').attr('data-el_id', dataData.elementName)
    const sme = dataData.elementName
    let scenwherecondmodelname = $(`#modelName_${ modelelementid } `).attr('data-model_name')
    if(modelelementid == "modelelementid2") {
      scenwherecondmodelname = $('#selectTablePC').val()
    }
    if(modelelementid == "modelelementid" && compValProcess) {
      scenwherecondmodelname = $('#selectFormTable').val()[0]
    }
    $.ajax({
      url: `/users/${urlPath}/computationModule/`,
      data: {
        model_name: dataData.data3.inputs.Table,
        model: scenwherecondmodelname,
        columns_list: JSON.stringify(dataData.data3.inputs.Columns),
        operation: 'condition_check',
        connection_name: 'default'
      },
      type: 'POST',
      dataType: 'json',
      success: function (data) {
        $('#condition_dropdown').empty()
        if(compValProcess){
          $('#where_condition_Modal').modal('show')
          $('#EBDisplayModel').modal('hide')
        }else{
          $('#where_condition_Modal').modal('show')
        }
        const labelColumn = data.label_column
        for (const [key, value] of Object.entries(labelColumn)) {
          $('#condition_dropdown').append('<li class="dropdown-item"><a href="javascript:void(0)" name=' + key + ' class="filter_btn">' + value + '</a></li>')
          $('#condition_dropdown').attr("data-table", data.table_name)
        }

        $('.filter_btn').click(function () {
          const name = $(this).attr('name')
          const STRING = data.form_fields[name]
          $('#filter-table').append(STRING)
          $('#filter-table').find('tr').eq(-1).find('td').eq(3).remove()
          const colDType = $('#filter-table').find('tr').eq(-1).find('input').attr('type')
          $('#filter-table').find('tr').eq(-1).append(
            `<td class="dt-center">
              <div class="" style="max-width:25em;">
                <select class="form-control select2bs4" name=${name} data-dropdown_purpose="select_global_variable" data-type="${colDType}">
                  <option value="" selected disabled>Select Global Variable</option>
                </select>
              </div>
            </td >
              `)
          if(compValProcess){
            $('#filter-table').find('tr').eq(-1).append(
                `<td class="dt-center">
                <div class="" style="max-width:25em;">
                  <input type="text" placeholder="Default value" name=${name} data-type="${colDType}" maxlength="100" class="textinput textInput form-control" required="">
                </div>
              </td >`
            )
          }
          $('#filter-table').find('tr').eq(-1).attr("data-table", $('#condition_dropdown').attr("data-table"))
          let gVarNameList = []
          if (String(colDType) === 'text') {
            gVarNameList = data.global_text_list
          } else if (String(colDType) === 'number') {
            gVarNameList = data.global_number_list
          } else if (String(colDType) === 'date') {
            gVarNameList = data.global_datetime_list.concat(data.global_date_list)
          } else if (String(colDType) === 'datetime-local') {
            gVarNameList = data.global_datetime_list.concat(data.global_date_list)
          };
          for (let i = 0; i < gVarNameList.length; i++) {
            const varName = gVarNameList[i]
            $('#filter-table').find('tr').eq(-1).find('select[data-dropdown_purpose="select_global_variable"]').append(`<option value = '${varName}' > ${ varName }</option>`)
          };

          if(compValProcess){
            for (let i = 0; i < compValVarName.length; i++) {
              let varName = compValVarName[i]
              $('#filter-table').find('tr').eq(-1).find('select[data-dropdown_purpose="select_global_variable"]').append(`<option value = '${varName}' > ${ varName }</option>`)
            };
          }

          $('#filter-table:last-child').find('select').each(function () {
            $(this).select2()
          })
          $('.remove_filter').on('click', removefilter)
        })
        function removefilter() {
          $(this).closest('tr').remove()
        }

        $.ajax({
          url: `/users/${urlPath}/computationModule/`,
          data: {
            model_name: scenarioName + elementIdentifier,
            element_id: sme,
            operation: 'import_config',
            model_element_id: MelementID
          },
          type: 'POST',
          dataType: 'json',
          success: function (data1) {
            $('#dropdown1').val('').trigger('change')
            $('#dropdown1').val('').trigger('select2:select')
            $('#filter-table').empty()
            $('#data_btn').css('display', 'none')

            if (Object.keys(data1).length > 0) {
              for (let i = 0; i < data1.element_config.condition.length; i++) {
                if (!(data1.element_config.condition[i].hasOwnProperty('table'))) {
                  data1.element_config.condition[i]["table"] = data1.table_name
                }
              }
              const elementConfigDict = data1.element_config

              const elementID = data1.element_id
              const dataSource = elementConfigDict.inputs.Data_source
              const tableName = elementConfigDict.inputs.Table
              const condition = elementConfigDict.condition
              // eslint-disable-next-line no-undef
              filter_list[elementID] = condition

              if (String(dataSource) === 'Database') {
                $('#where_condition').css('display', 'inline-block')

                $('#dropdown1').val(dataSource).trigger('change')
                $('#dropdown1').val(dataSource).trigger('select2:select')
                // Where Condition
                if (condition.length > 0) {
                  const formFields = data1.form_fields
                  $('#filter-table').empty()
                  for (let i = 0; i < condition.length; i++) {
                    if (condition[i].table == data1.table_name) {
                      const Cname = (condition[i].column_name)
                      const cond = (condition[i].condition)
                      const iVal = (condition[i].input_value)
                      const gVar = (condition[i].globalVariable)
                      const STRING = formFields[Cname]
                      $('#filter-table').append(STRING)
                      if (condition[i].hasOwnProperty("table")) {
                        $('#filter-table').find('tr').eq(-1).attr("data-table", condition[i]["table"])
                      }
                      $('#filter-table').find('tr').eq(-1).find('td').eq(3).remove()
                      const colDType = $('#filter-table').find('tr').eq(-1).find('input').attr('type')
                      $('#filter-table').find('tr').eq(-1).append(
                        `
                        <td class="dt-center">
                          <div class="" style="max-width:25em;">
                            <select class="form-control select2bs4" name=${Cname} data-dropdown_purpose="select_global_variable" data-type="${colDType}">
                              <option value="" selected disabled>Select Global Variable</option>
                            </select>
                          </div>
                        `)
                      if(compValProcess){
                        $('#filter-table').find('tr').eq(-1).append(`
                        </td>
                          <td class="dt-center">
                            <div class="" style="max-width:25em;">
                              <input type="text" placeholder="Default value" name=${Cname} data-type="${colDType}" maxlength="100" class="textinput textInput form-control" required="">
                            </div>
                          </td >
                        `)
                      }
                      let gVarNameList = []
                      if (String(colDType) === 'text') {
                        gVarNameList = data1.global_text_list
                      } else if (String(colDType) === 'number') {
                        gVarNameList = data1.global_number_list
                      } else if (String(colDType) === 'date') {
                        gVarNameList = data1.global_date_list
                      } else if (String(colDType) === 'datetime-local') {
                        gVarNameList = data1.global_datetime_list
                      };
                      for (let i = 0; i < gVarNameList.length; i++) {
                        const varName = gVarNameList[i]
                        $('#filter-table').find('tr').eq(-1).find('select').eq(1).append(`<option value = '${varName}' > ${ varName }</option>`)
                      };

                      if(compValProcess){
                        for (let i = 0; i < compValVarName.length; i++) {
                          let varName = compValVarName[i]
                          $('#filter-table').find('tr').eq(-1).find('select').eq(1).append(`<option value = '${varName}' > ${ varName }</option>`)
                        };
                      }

                      if ($('#filter-table').find(`tr:nth-child(${ i + 1})`).length == 0) {
                        $('#filter-table').find(`tr:nth-child(${ i + 1 - 1})`).find('td:nth-child(2) > div > select').val(cond).trigger('change')
                        $('#filter-table').find(`tr:nth-child(${ i + 1 - 1})`).find('td:nth-child(3) > div > input').val(iVal).trigger('change')
                        $('#filter-table').find(`tr:nth-child(${ i + 1 - 1})`).find('td:nth-child(4) > div > select').val(gVar).trigger('change')
                        if(compValProcess){
                          $('#filter-table').find(`tr:nth-child(${ i + 1 - 1})`).find('td:nth-child(5) > div > input').val(iVal).trigger('change')
                          $('#filter-table').find(`tr:nth-child(${ i + 1 - 1})`).find('td:nth-child(3) > div > input').val("").trigger('change')
                        }
                      } else {
                        $('#filter-table').find(`tr:nth-child(${ i + 1})`).find('td:nth-child(2) > div > select').val(cond).trigger('change')
                        $('#filter-table').find(`tr:nth-child(${ i + 1})`).find('td:nth-child(3) > div > input').val(iVal).trigger('change')
                        $('#filter-table').find(`tr:nth-child(${ i + 1})`).find('td:nth-child(4) > div > select').val(gVar).trigger('change')
                        if(compValProcess){
                          $('#filter-table').find(`tr:nth-child(${ i + 1})`).find('td:nth-child(5) > div > input').val(iVal).trigger('change')
                          $('#filter-table').find(`tr:nth-child(${ i + 1})`).find('td:nth-child(3) > div > input').val("").trigger('change')
                        }
                      }
                      $('#filter-table').find('tr').eq(-1).find('select').each(function () {
                        $(this).select2()
                      })
                      $('.remove_filter').on('click', removefilter)
                    }
                  }
                  function removefilter() {
                    $(this).closest('tr').remove()
                  }
                } else {
                  $('#filter-table').empty()
                }
              }
            } else {
              $('#dropdown1').css('display', 'block')
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
  })
}

function changeTableandColumns(tablename) { // eslint-disable-line no-unused-vars
  const s = tablename.split('-')
  tablename = s[0]
  let colList = []

  if (String($('#tname').val()) === tablename && String(idenFlag) !== 'add') {
    $(`#table .hide`).slice(0,tb_index + 1).each(function () {
      colList.push($(this).find('td').find('#fld_name').text())
    })

    displayColumns(colList, tablename)
  } else if (String(idenFlag) === 'edit' && (tablename in tempdd)) {
    colList = edit_col_list
    displayColumns(colList, tablename)
  } else {
    $.ajax({
      url: `/users/${urlPath}/computationModule/`,
      data: {
        table_name: tablename,
        operation: 'fetch_table_columns'
      },
      type: 'POST',
      dataType: 'json',
      success: function (data) {
        $('#selectColumn').empty()
        for (const i in data.columnList) {
          colList.push(data.columnList[i])
        }
        if (String(idenFlag) === 'add') {
          if (!(colList.includes($('#fieldmdl').val()))) {
            colList.push($('#fieldmdl').val())
          }
        }

        if (listViewComp == true && !(listViewCompCol.startsWith("document"))) {
          if (!(colList.includes(listViewCompCol))) {
            colList.push(listViewCompCol)
          }
        }

        displayColumns(colList, tablename)
      },
      error: function () {
        Swal.fire({icon: 'error',text: 'Error! Please try again.'});
      }
    })
  }
}

function fetchJobOutput1 (jobId, runStepBtnId = '', runStepBtnLoadId = '', outputType = 'dataframe') {
  let websocketUrlPrefix = 'ws://';
  if (windowLocationAttr.protocol === 'https:') {
      websocketUrlPrefix = 'wss://';
  }
  const jobConnection = new WebSocket(
    websocketUrlPrefix + windowLocationAttr.host +
            `/ws/queued_job_output/${jobId}/`)

jobConnection.onmessage = function (event) {
  const data = JSON.parse(event.data)
  outputSaveResultPrompt1(data)

  displayTabularOutput1(data.content)
  Swal.fire({icon: 'success',text: 'Computation block executed successfully.'});
}

jobConnection.onerror = function () {
  jobConnection.close(1000)
  Swal.fire({icon: 'error',text: 'Error! Failure in executing the computation. Please try again.'});
}
}

function outputSaveResultPrompt1(data) { // eslint-disable-line no-unused-vars
  if (Object.keys(data).includes('result_save')) {
    for (const i of data.result_save) {
      if (i) {
        Swal.fire({icon: 'info',text: i});
      }
    }
  }
}

function displayTabularOutput1(data) {
  $('#exampledata1').remove()
  $('#exampledata1_wrapper').remove()
  $('#viewData1').append(`
        <table id="exampledata1" class="display compact" style="width:100%;" data-parent_group_no="g3">
            <thead>
                <tr>
                    <th id="thid1"></th>
                </tr>
            </thead>
            <tbody>
            </tbody>
        </table>
        `)
  $('#exampledata1 tbody').empty()
  for (let i = 0; i < data.length; i++) {
    let string = '<tr>'
    for (const [key, value] of Object.entries(data[i])) { // eslint-disable-line no-unused-vars
      string += `<td style="text-align:center;">${value}</td>`
    }
    string += '</tr>'
    $('#exampledata1').find('tbody').append(string)
  }

  $('#exampledata1 thead tr').empty()
  $('#thid1').css('display', 'none')
  for (const [key, value] of Object.entries(data[0])) { // eslint-disable-line no-unused-vars
    $('#exampledata1').find('thead tr').eq(0).append(`<th style="text-align:center;">${key}</th>`)
  }
  datatables('exampledata1')
}

function reloadCompConfig(mod_name) {

  $('.ebDataElementsDiv').remove();
  $('.ebFunctions').find('.function').remove();
  $('.ebSteps').find('#stepNumsEb').empty();
  $('#functionPreviews').empty();
  $('#selectedTablesDiv').empty()
  $('#table-columns').empty()
  $('#functionsList').empty()
  $('#favouriteList').empty()
  selectedTables = {}
  indexCount = 0
  counter = 0
  favFunctionList = []
  let curr_table1 = ""
  let tt_name = ""
  let selectedCol = ""

  if ($('#favouriteList').attr('data-element_id') != undefined) {
    $('#favouriteList').removeAttr('data-element_id')
  }


  var minm = 1000000000000;
  var maxm = 9999999999999;
  var icon = "";
  uniqueid_maths = "applyMathOps" + (Math.floor(Math.random() * (maxm - minm + 1)) + minm).toString()
  uniqueid_join = "mergeAndJoin" + (Math.floor(Math.random() * (maxm - minm + 1)) + minm).toString()
  uniqueid_rename = "renameColumn" + (Math.floor(Math.random() * (maxm - minm + 1)) + minm).toString()
  uniqueid_pivot = 'pivotAndTranspose' + (Math.floor(Math.random() * (maxm - minm + 1)) + minm).toString()
  uniqueid_concat = "concatColumn" + (Math.floor(Math.random() * (maxm - minm + 1)) + minm).toString()

  const htmlString = funcDic
    .map((character) => {


      if (character.name == 'Column division' || character.name == 'Row division') {
        icon = "fas fa-divide"
      } else if (character.name == 'Column multiplication' || character.name == 'Row multiplication') {
        icon = "fas fa-times"
      } else if (character.name == 'Column subtraction' || character.name == 'Row subtraction') {
        icon = "fas fa-minus"
      } else if (character.name == 'Column sum' || character.name == 'Row sum') {
        icon = "fas fa-plus"
      } else if (character.name == 'Square root') {
        icon = "fas fa-square-root-alt"
      } else if ((character.name == 'Inner Join' || character.name == 'Left Join' || character.name == 'Right Join' || character.name == 'Outer Join' || character.name == 'Append and Concatenate')) {
        icon = "fas fa-coins"
      } else if (character.name == 'Round') {
        icon = "far fa-circle"
      } else {
        icon = "fas fa-thumbs-up"
      }

      if (character.name == 'Left Join' || character.name == 'Right Join' || character.name == 'Inner Join' || character.name == 'Outer Join' || character.name == 'Append and Concatenate' || character.name == 'Filter' || character.name == 'Add Column' || character.name == 'Groupby' || character.name == 'Networkdays' || character.name == 'Networkdays.Intl' || character.name == 'Workdays' || character.name == 'Workdays.Intl') {
        return `
          <div class="function draggable" draggable="true">
              <h2>${character.name}</h2>
              <h3 class="heartIcon" onClick="addToFav('${character.name}' )" value=${character.name}><i class="${icon}"></i></h3>
              <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueid_join}" data-element_comp="datamgm" onClick="popupOpen();takeFuncInput('${character.name}','${uniqueid_join}','${counter}',this)">&#11167;</a>
              <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueid_join}" onClick="deleteElement(this)">&#10006;</span>
          </div>`;
      } else if (character.name == 'Round') {
        return `
          <div class="function draggable" draggable="true">
              <h2>${character.name}</h2>
              <h3 class="heartIcon" onClick="addToFav('${character.name}' )" value=${character.name}>oO</h3>
              <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueid_maths}" data-element_comp="datamgm" onClick="popupOpen();takeFuncInput('${character.name}','${uniqueid_maths}','${counter}',this)">&#11167;</a>
              <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueid_maths}" onClick="deleteElement(this)">&#10006;</span>
          </div>`;
      } else if (character.name == 'Pivot' || character.name == 'Unpivot') {
        return `
          <div class="function draggable" draggable="true">
              <h2>${character.name}</h2>
              <h3 class="heartIcon" onClick="addToFav('${character.name}' )" value=${character.name}>&#13266;</h3>
              <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueid_pivot}" data-element_comp="datamgm" onClick="popupOpen();takeFuncInput('${character.name}','${uniqueid_pivot}','${counter}',this)">&#11167;</a>
              <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueid_pivot}"   onClick="deleteElement(this)">&#10006;</span>
          </div>
      `;
      } else if (character.name == 'Log') {
        return `
          <div class="function draggable" draggable="true">
              <h2>${character.name}</h2>
              <h3 class="heartIcon" onClick="addToFav('${character.name}')" value=${character.name}>&#13266;</h3>
              <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueid_maths}" data-element_comp="datamgm" onClick="popupOpen();takeFuncInput('${character.name}','${uniqueid_maths}','${counter}',this)">&#11167;</a>
              <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueid_maths}" onClick="deleteElement(this)">&#10006;</span>
          </div>
    `;
      } else if (character.name == 'Rename and Drop') {
        return `
          <div class="function draggable" draggable="true">
              <h2>${character.name}</h2>
              <h3 class="heartIcon" onClick="addToFav('${character.name}')" value=${character.name}>&#13266;</h3>
              <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueid_rename}" data-element_comp="datamgm" onClick="popupOpen();takeFuncInput('${character.name}','${uniqueid_rename}','${counter}',this)">&#11167;</a>
              <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueid_rename}" onClick="deleteElement(this)">&#10006;</span>
          </div>
    `;
      } else if (character.name == 'Concat Columns') {
        return `
            <div class="function draggable" draggable="true">
                <h2>${character.name}</h2>
                <h3 class="heartIcon" onClick="addToFav('${character.name}' )" value=${character.name}>&#13266;</h3>
                <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueid_concat}" data-element_comp="datamgm" onClick="popupOpen();takeFuncInput('${character.name}','${uniqueid_concat}','${counter}',this)">&#11167;</a>
                <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueid_concat}"   onClick="deleteElement(this)">&#10006;</span>
            </div>
        `;
      } else {
        return `
          <div class="function draggable" draggable="true">
              <h2>${character.name}</h2>
              <h3 class="heartIcon" onClick="addToFav('${character.name}')" value=${character.name}><i class="${icon}"></i></h3>
              <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueid_maths}" data-element_comp="datamgm" onClick="popupOpen();takeFuncInput('${character.name}','${uniqueid_maths}','${counter}',this)">&#11167;</a>
              <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueid_maths}" onClick="deleteElement(this)">&#10006;</span>
          </div>
    `;
      }
    })
    .join('');
  functionsList.innerHTML = htmlString;

  draggables = document.querySelectorAll('.draggable')
  draggables.forEach(draggable => {
    draggable.addEventListener('dragstart', (e) => {
      draggable.classList.add('dragging')

    })

    draggable.addEventListener('dragend', (e) => {
      draggable.classList.remove('dragging')
      displayPreviews()
      displayCharacters(funcDic)

    })
  });

  $.ajax({
    url: `/users/${urlPath}/computationModule/`,
    data: {
      'model_name': mod_name,
      'operation': 'eq_reload_config',
      'data_id': 'datamgm',
    },
    type: "POST",
    dataType: "json",
    success: function (data) {
      counter = Object.keys(data.func_data).length
      indexCount = counter
      func_list = []
      var export_elem_id = ""

      for (let [key, value] of Object.entries(data.func_data)) {
        if (value.text != 'Export data') {
          if (value.text == 'Ceiling' || value.text == 'Floor' || value.text == 'Floor'
            || value.text == 'Odd' || value.text == 'Even' || value.text == 'Round'
            || value.text == 'Round_Up' || value.text == 'Round_Down' || value.text == 'Truncate'
          ) {
            value.text = 'Round'
            func_list.push(value.text)
          } else if (value.text == 'Log_base' || value.text == 'Exponential' || value.text == 'Natural_Log') {
            value.text = 'Log'
            func_list.push(value.text)
          } else if (value.text == 'Power') {
            value.text = 'Square root'
            func_list.push(value.text)
          } else if (value.text == 'left') {
            value.text = 'Left Join'
            func_list.push(value.text)
          } else if (value.text == 'right') {
            value.text = 'Right Join'
            func_list.push(value.text)
          } else if (value.text == 'inner') {
            value.text = 'Inner Join'
            func_list.push(value.text)
          } else if (value.text == 'outer') {
            value.text = 'Outer Join'
            func_list.push(value.text)
          } else if (value.text == 'append') {
            value.text = 'Append and Concatenate'
            func_list.push(value.text)
          } else if (value.text == 'filter') {
            value.text = 'Filter'
            func_list.push(value.text)
          } else if (value.text == 'AddColumn') {
            value.text = 'Add Column'
            func_list.push(value.text)
          } else if (value.text == 'sort') {
            value.text = 'Sort'
            func_list.push(value.text)
          } else if (value.text == 'groupby') {
            value.text = 'Groupby'
            func_list.push(value.text)
          } else if (value.text == 'pivot') {
            value.text = 'Pivot'
          } else if (value.text == 'unpivot') {
            value.text = 'Unpivot'
            func_list.push(value.text)
          } else {
            func_list.push(value.text)
          }

          $('.ebFunctions').append(`<div class="function draggable" draggable="true">
                              <h2>${value.text}</h2>
                              <h3 class="EBhide" onclick="addToFav('${value.text}')" value="${value.text}"><i class="fas fa-thumbs-up"></i></h3>
                              <a title="configure" href="#" name="Open" class="EBshow" id="open-overlay" data-element_id="${value.ele_id}" data-element_comp="datamgm" onclick="popupOpen();takeFuncInput('${value.text}','${value.ele_id}','${value.order}')">⮟</a>
                              <span title="delete" style="display:none;" class="deleteitem" data-element_id="${value.ele_id}" data-element_comp="datamgm"  onClick="deleteElement(this)">&#10006;</span>
                              </div>`)

          $('#stepNumsEb').append(`<h2 class="stepNumberEB"> ${value.order + 1}</h2>`)

          var minm = 1000000000000;
          var maxm = 9999999999999;
          uniqueid_maths = "applyMathOps" + (Math.floor(Math.random() * (maxm - minm + 1)) + minm).toString()
          uniqueid_join = "mergeAndJoin" + (Math.floor(Math.random() * (maxm - minm + 1)) + minm).toString()
          uniqueid_rename = "renameColumn" + (Math.floor(Math.random() * (maxm - minm + 1)) + minm).toString()
          uniqueid_pivot = 'pivotAndTranspose' + (Math.floor(Math.random() * (maxm - minm + 1)) + minm).toString()
          uniqueid_concat = "concatColumn" + (Math.floor(Math.random() * (maxm - minm + 1)) + minm).toString()
          const htmlString = funcDic
            .map((character) => {

              if (character.name == 'Column division' || character.name == 'Row division') {
                icon = "fas fa-divide"
              } else if (character.name == 'Column multiplication' || character.name == 'Row multiplication') {
                icon = "fas fa-times"
              } else if (character.name == 'Column subtraction' || character.name == 'Row subtraction') {
                icon = "fas fa-minus"
              } else if (character.name == 'Column sum' || character.name == 'Row sum') {
                icon = "fas fa-plus"
              } else if (character.name == 'Square root') {
                icon = "fas fa-square-root-alt"
              } else if ((character.name == 'Inner Join' || character.name == 'Left Join' || character.name == 'Right Join' || character.name == 'Outer Join' || character.name == 'Append and Concatenate')) {
                icon = "fas fa-coins"
              } else if (character.name == 'Round') {
                icon = "far fa-circle"
              } else {
                icon = "fas fa-thumbs-up"
              }

              if (character.name == 'Left Join' || character.name == 'Right Join' || character.name == 'Inner Join' || character.name == 'Outer Join' || character.name == 'Append and Concatenate' || character.name == 'Filter' || character.name == 'Add Column' || character.name == 'Groupby' || character.name == 'Networkdays' || character.name == 'Networkdays.Intl' || character.name == 'Workdays' || character.name == 'Workdays.Intl') {
                return `
                  <div class="function draggable" draggable="true">
                      <h2>${character.name}</h2>
                      <h3 class="heartIcon" onClick="addToFav('${character.name}' )" value=${character.name}><i class="${icon}"></i></h3>
                      <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueid_join}" data-element_comp="datamgm" onClick="popupOpen();takeFuncInput('${character.name}','${uniqueid_join}','${counter}',this)">&#11167;</a>
                      <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueid_join}" onClick="deleteElement(this)">&#10006;</span>
                  </div>`;
              } else if (character.name == 'Round') {
                return `
                  <div class="function draggable" draggable="true">
                      <h2>${character.name}</h2>
                      <h3 class="heartIcon" onClick="addToFav('${character.name}' )" value=${character.name}>oO</h3>
                      <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueid_maths}" data-element_comp="datamgm" onClick="popupOpen();takeFuncInput('${character.name}','${uniqueid_maths}','${counter}',this)">&#11167;</a>
                      <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueid_maths}" onClick="deleteElement(this)">&#10006;</span>
                  </div>`;
              } else if (character.name == 'Log') {
                return `
                  <div class="function draggable" draggable="true">
                      <h2>${character.name}</h2>
                      <h3 class="heartIcon" onClick="addToFav('${character.name}' )" value=${character.name}>&#13266;</h3>
                      <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueid_maths}" data-element_comp="datamgm" onClick="popupOpen();takeFuncInput('${character.name}','${uniqueid_maths}','${counter}',this)">&#11167;</a>
                      <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueid_maths}" onClick="deleteElement(this)">&#10006;</span>
                  </div>`;
              } else if (character.name == 'Rename and Drop') {
                return `
                  <div class="function draggable" draggable="true">
                      <h2>${character.name}</h2>
                      <h3 class="heartIcon" onClick="addToFav('${character.name}' )" value=${character.name}>&#13266;</h3>
                      <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueid_rename}" data-element_comp="datamgm" onClick="popupOpen();takeFuncInput('${character.name}','${uniqueid_rename}','${counter}',this)">&#11167;</a>
                      <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueid_maths}" onClick="deleteElement(this)">&#10006;</span>
                  </div>`;
              } else if (character.name == 'Unpivot') {
                return `
                              <div class="function draggable" draggable="true">
                                  <h2>${character.name}</h2>
                                  <h3 class="heartIcon" onClick="addToFav('${character.name}' )" value=${character.name}>&#13266;</h3>
                                  <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueid_pivot}" data-element_comp="datamgm" onClick="popupOpen();takeFuncInput('${character.name}','${uniqueid_pivot}','${counter}',this)">&#11167;</a>
                                  <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueid_pivot}"   onClick="deleteElement(this)">&#10006;</span>
                              </div>
                          `;
              } else if (character.name == 'Concat Columns') {
                return `
                                <div class="function draggable" draggable="true">
                                    <h2>${character.name}</h2>
                                    <h3 class="heartIcon" onClick="addToFav('${character.name}' )" value=${character.name}>&#13266;</h3>
                                    <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueid_concat}" data-element_comp="datamgm" onClick="popupOpen();takeFuncInput('${character.name}','${uniqueid_concat}','${counter}',this)">&#11167;</a>
                                    <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueid_concat}"   onClick="deleteElement(this)">&#10006;</span>
                                </div>
                            `;
              } else {
                return `
                  <div class="function draggable" draggable="true">
                      <h2>${character.name}</h2>
                      <h3 class="heartIcon" onClick="addToFav('${character.name}' )" value=${character.name}><i class="${icon}"></i></h3>
                      <a title="configure" href="#"  name="Open" class="EBhide EbOverlay" id="open-overlay" data-element_id="${uniqueid_maths}" data-element_comp="datamgm" onClick="popupOpen();takeFuncInput('${character.name}','${uniqueid_maths}','${counter}',this)">&#11167;</a>
                      <span title="delete" style="display:none;" class="deleteitem" data-element_id="${uniqueid_maths}" onClick="deleteElement(this)">&#10006;</span>
                  </div>`;
              }
            })
            .join('');
          functionsList.innerHTML = htmlString;

          draggables = document.querySelectorAll('.draggable')
          draggables.forEach(draggable => {
            draggable.addEventListener('dragstart', (e) => {
              draggable.classList.add('dragging')

            })

            draggable.addEventListener('dragend', (e) => {
              draggable.classList.remove('dragging')
              displayPreviews()
              displayCharacters(funcDic)

            })
          });
        } else if (value.text == 'Export data') {
          export_elem_id = value.ele_id
          if (export_elem_id) {
            $('#exportEqData').attr('data-element_id', export_elem_id)
          }

        }

      }

      if (idenFlag != 'attr') {

        if (counter == 1) {
          $('.ebFunctions').find('div').eq(counter - 1).find('span').css('display', 'block')
        } else {
          $('.ebFunctions').find('div').eq(counter - 1).find('span').css('display', 'block')
          $('.ebFunctions').find('div').eq(counter - 2).find('span').css('display', 'none')
        }
      }

      for (let [key, value] of Object.entries(data.fav_data)) {

        favFunctionList = data.fav_data[0].text.slice()
        $('#favouriteList').attr('data-element_id', data.fav_data[0].ele_id)
        displayFav(data.fav_data[0].text)

      }


      for (let i = 0; i < func_list.length; i++) {

        let div1 = document.createElement("div")
        let btn = document.createElement("button");
        div1.className = "ebDataElementsDiv dragAreaPossible"
        btn.className = "btn btn-primary btn-xs mx-2 rounded px-2"
        btn.innerHTML = "Data";
        var restrict_flag = 0
        btn.addEventListener("click", function () {

          columnss_list = []
          columns_list = []
          s_table_name = []
          t_ele_id = []
          table1 = []
          table2 = []

          var table_name = new Set();
          var ele_id = new Set();

          b = $(this).parent('.ebDataElementsDiv').find('.ColumnItem')
          for (let i = 0; i < b.length; i++) {
            table_name.add(b[i].getAttribute('data-table'))
            ele_id.add(b[i].getAttribute('data-element_id'))
          }

          s_table_name = Array.from(table_name);
          t_ele_id = Array.from(ele_id);

          if (listViewComp == true) {
            curr_table1 = listViewModelName
            tt_name = listViewModelName
            selectedCol = listViewCompCol
          }

          bb = $(this).parent('.ebDataElementsDiv').find('.ColumnItem')

          if (s_table_name.length > 1) {

            for (let i = 0; i < s_table_name.length - 1; i++) {

              curr_table = s_table_name[i]

              for (let j = 0; j < bb.length; j++) {
                if (bb[j].getAttribute('data-table') == curr_table) {
                  table1.push(bb[j].querySelector('p').innerText)
                } else {
                  table2.push(bb[j].querySelector('p').innerText)
                }

              }
              columnss_list.push(table1)
              columnss_list.push(table2)
            }

          } else {

            a = $(this).parent('.ebDataElementsDiv').find('.ColumnItem').find('p')
            for (let i = 0; i < a.length; i++) {
              columns_list.push(a[i].innerText)
            }
            columnss_list.push(columns_list)
          }

          for (let j = 0; j < s_table_name.length; j++) {

            if (s_table_name[j] == curr_table1) {
              current_table = "Yes"
            } else {
              current_table = "No"
            }

            var configDict_t = {
              'function': 'Import Data',
              'data_mapper': { 'current_element_name': s_table_name[j] },
              'inputs': {
                'Data_source': "Database",
                'Table': s_table_name[j],
                'Columns': columnss_list[j],
                'global_var': "",
                "parent_table_column": "",
                "current_table_column": "",
                'show_foreignKey_value': false,
                "current_table": current_table,
              },
              'condition': {},
            }
            configDict_t['outputs'] = {
              'name': "",
              'save': "",
            };

            $.ajax({
              url: `/users/${urlPath}/computationModule/`,
              data: {
                'configList': JSON.stringify({
                  data1: tt_name,
                  data2: t_ele_id[j],
                  data3: configDict_t,
                  elementName: tt_name + selectedCol + Math.floor((Math.random() * 10000000000) + 1),
                  data_id: 'datamgm',
                }),
                'operation': 'save_import_data',
                'data_source': "Database"
              },
              type: "POST",
              dataType: "json",
              success: function (context) {
                Swal.fire({icon: 'success',text: 'Data import configuration saved successfully!'});

              },
              error: function () {
                Swal.fire({icon: 'error',text: 'Error! Failure in saving the Data import configuration. Please try again.'});
              }
            });


          }


        });
        div1.append(btn)
        dataElementParent.append(div1)

        const dragAreas = document.querySelectorAll('.dragAreaPossible')

        dragAreas.forEach(dragArea => {
          dragArea.addEventListener('dragover', e => {

            e.preventDefault()
            const afterElement = getDragAfterElement1(dragArea, e.clientY)
            const draggable = document.querySelector('.dragging')

            if (afterElement == null) {
              dragArea.appendChild(draggable)

              if (dragArea.querySelector('.EbOverlay')) {
                dragArea.querySelector('.EbOverlay').className = "EBshow"
              }

              if (dragArea.querySelector('.heartIcon')) {
                dragArea.querySelector('.heartIcon').className = "EBhide"
              }



            } else {
              dragArea.insertBefore(draggable, afterElement)

              if (dragArea.querySelector('.EbOverlay')) {
                dragArea.querySelector('.EbOverlay').className = "EBshow"
              }

              if (dragArea.querySelector('.heartIcon')) {
                dragArea.querySelector('.heartIcon').className = "EBhide"
              }

            }

          })
        })


        function getDragAfterElement1(container, y) {
          const draggableElements = [...container.querySelectorAll('.draggable:not(.dragging)')]

          return draggableElements.reduce((closest, child) => {
            const box = child.getBoundingClientRect()
            const offset = y - box.top - box.height / 2
            if (offset < 0 && offset > closest.offset) {
              return { offset: offset, element: child }
            } else {
              return closest
            }
          }, { offset: Number.POSITIVE_INFINITY }).element
        }

        var join_first_count = 0
        var joint_count = 0
        if (i == 0) {
          if (func_list[i] == 'Left Join' || func_list[i] == 'Right Join' || func_list[i] == 'Inner Join' || func_list[i] == 'Outer Join' || func_list[i] == 'Networkdays' || func_list[i] == 'Workdays' || func_list[i] == 'Workdays.Intl') {

            for (let [key, value] of Object.entries(data.import_data)) {

              if (join_first_count == 2) break;

              for (let [k, v] of Object.entries(value.columns)) {

                $('.ebDataElementsDiv').eq(i).append(`
                  <div class= "ColumnItem draggable" draggable="true" data-table="${value.table_name}" data-element_id="${value.ele_id}" data-element_comp="datamgm">
                  <p>${v}</p>
                  </div>
                `)

                draggables = document.querySelectorAll('.draggable')
                draggables.forEach(draggable => {
                  draggable.addEventListener('dragstart', (e) => {
                    draggable.classList.add('dragging')

                  })

                  draggable.addEventListener('dragend', (e) => {
                    draggable.classList.remove('dragging')
                    displayPreviews()
                    displayCharacters(funcDic)

                  })
                });

              }
              delete data.import_data[join_first_count]
              join_first_count = join_first_count + 1
            }
          } else {

            for (let [key, value] of Object.entries(data.import_data)) {

              if (joint_count == 1) break;

              for (let [k, v] of Object.entries(value.columns)) {

                $('.ebDataElementsDiv').eq(i).append(`
                  <div class="ColumnItem draggable" draggable="true" data-table="${value.table_name}" data-element_id="${value.ele_id}" data-element_comp="datamgm">
                  <p>${v}</p>
                  </div>
                `)



                draggables = document.querySelectorAll('.draggable')
                draggables.forEach(draggable => {
                  draggable.addEventListener('dragstart', (e) => {
                    draggable.classList.add('dragging')

                  })

                  draggable.addEventListener('dragend', (e) => {
                    draggable.classList.remove('dragging')
                    displayPreviews()
                    displayCharacters(funcDic)

                  })
                });

              }
              delete data.import_data[joint_count]
              joint_count = joint_count + 1
            }
          }
        } else {

          if (func_list[i] == 'Left Join' || func_list[i] == 'Right Join' || func_list[i] == 'Inner Join' || func_list[i] == 'Outer Join' || func_list[i] == 'Append and Concatenate' || func_list[i] == 'Networkdays' || func_list[i] == 'Networkdays.Intl' || func_list[i] == 'Workdays' || func_list[i] == 'Workdays.Intl') {
            for (let [key, value] of Object.entries(data.import_data)) {
              if (joint_count == 1) break;

              for (let [k, v] of Object.entries(value.columns)) {

                $('.ebDataElementsDiv').eq(i).append(`
                  <div class="ColumnItem draggable" draggable="true" data-table="${value.table_name}" data-element_id="${value.ele_id}" data-element_comp="datamgm">
                    <p>${v}</p>
                  </div>
                `)

                draggables = document.querySelectorAll('.draggable')
                draggables.forEach(draggable => {
                  draggable.addEventListener('dragstart', (e) => {
                    draggable.classList.add('dragging')

                  })

                  draggable.addEventListener('dragend', (e) => {
                    draggable.classList.remove('dragging')
                    displayPreviews()
                    displayCharacters(funcDic)

                  })
                });

              }
              delete data.import_data[joint_count]
              joint_count = joint_count + 1
            }
          }


        }

      }


      var functionDiv = document.querySelector(".ebFunctions");
      var functions = functionDiv.querySelectorAll(".function")
      var listOfFunctions = [];
      functions.forEach(item => {
        listOfFunctions.push(item.querySelector('h2').innerText)
      })

      for (let [key, value] of Object.entries(data.func_data)) {
        if (value.text != 'Export data') {
          var myString = ""
          $('#functionPreviews').append(
            `<div class="function" onclick="">
              <h2></h2>
              <p style="display:none;"></p>
            </div>
          `);

          if (value.prevString.length > 30) {
            myString = value.prevString.substring(0, 30) + '...'
            $('#functionPreviews').find('.function').eq(value.order).find('p').text(value.prevString)
            $('#functionPreviews').find('.function').eq(value.order).attr('onclick', `popupOpen(); takeFuncInput('${value.text}', '${value.ele_id}', '${value.order}', this)`);
          } else {
            myString = value.prevString
            $('#functionPreviews').find('.function').eq(value.order).find('p').text(value.prevString)
            $('#functionPreviews').find('.function').eq(value.order).attr('onclick', "");

          }

          $('#functionPreviews').find('.function').eq(value.order).find('h2').text(myString)
        }
      }

      var table_name11 = new Set();
      var ele_id11 = new Set();

      bce12 = $('#dataElementParent').find('.ebDataElementsDiv').eq(0).find('.ColumnItem')
      for (let i = 0; i < bce12.length; i++) {
        table_name11.add(bce12[i].getAttribute('data-table'))
        ele_id11.add(bce12[i].getAttribute('data-element_id'))
      }

      s_table_name12 = Array.from(table_name11);
      t_ele_id12 = Array.from(ele_id11);

      let taew = {}
      for (let i = 0; i < s_table_name12.length; i++) {
        taew[s_table_name12[i]] = t_ele_id12[i]
      }
      tempdd = taew

    },
    error: function () {
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    }
  });

}

function SaveCompFlow(mod_name) {

const a = $('.ebFunctions').find('div').find('a')
const configDict = []
let funcName = ''
let curr = ''
let next = ''
let cc = ''
let c = ''
let bb = ''
let b = ''
let iList = []
let finalList
let n

for (let i = 0; i < a.length; i++) {
try {
  b = $('.ebDataElementsDiv').eq(i).find('.ColumnItem')
  b[0].getAttribute('data-element_id')
  cc = $('.ebFunctions').find('div').find('a').eq(i).attr('data-element_id')
      try {
        n = $('.ebFunctions').find('div').find('a').eq(i + 1).attr('data-element_id')
        next = [n]
      } catch (err) {
        next = '#'
      }
      funcName = $('.ebFunctions').find('div').find('h2').eq(i).text()

      const tablesList = new Set()
      for (let i = 0; i < b.length; i++) {
        tablesList.add(b[i].getAttribute('data-element_id'))
      }
      finalList = Array.from(tablesList)
      iList = finalList.slice()

      if ((String(funcName) === 'Left Join' || String(funcName) === 'Right Join' || String(funcName) === 'Inner Join' || String(funcName) === 'Outer Join' || String(funcName) === 'Append and Concatenate' || String(funcName) === 'Networkdays' || String(funcName) === 'Networkdays.Intl' || String(funcName) === 'Workdays' || String(funcName) === 'Workdays.Intl') && String(finalList.length) === '1') {
        bb = $('.ebFunctions').find('div').find('a').eq(i - 1).attr('data-element_id')
        if(funcName=='Networkdays' || funcName=='Networkdays.Intl' || funcName=='Workdays' || String(funcName) === 'Workdays.Intl'){
          if (i==0)
          {   if(bb.includes("import")){
                  finalList.push(bb)
              }
          }else{
              finalList.push(bb)
          }
        }else{
            finalList.push(bb)
        }
      }

      b = finalList
      curr = cc
    } catch (err) {
      b = $('.ebFunctions').find('div').find('a').eq(i - 1).attr('data-element_id')
      curr = $('.ebFunctions').find('div').find('a').eq(i).attr('data-element_id')
      funcName = $('.ebFunctions').find('div').find('h2').eq(i).text()

      try {
        n = $('.ebFunctions').find('div').find('a').eq(i + 1).attr('data-element_id')
        next = [n]
        finalList = b
        b = [b]
      } catch (err) {
        next = '#'
        b = [b]
      }
    }

    if (String(funcName) === 'Column sum' || String(funcName) === 'Row sum' || String(funcName) === 'Cell sum' ||
      String(funcName) === 'Column subtraction' || String(funcName) === 'Row subtraction' || String(funcName) === 'Cell subtraction' ||
      String(funcName) === 'Column multiplication' || String(funcName) === 'Row multiplication' || String(funcName) === 'Cell multiplication' ||
      String(funcName) === 'Column division' || String(funcName) === 'Row division' || String(funcName) === 'Cell division'
    ) {
      funcName = 'Basic Operations'
    } else if (String(funcName) === 'Round') {
      funcName = 'Rounding Operations'
    } else if (String(funcName) === 'Square root') {
      funcName = 'Power and Root Functions'
    } else if (String(funcName) === 'Log') {
      funcName = 'Log and Exponential Functions'
    } else if (String(funcName) === 'Rename and Drop') {
      funcName = 'Rename Column'
    } else if (String(funcName) === 'Filter') {
      funcName = 'Data Transformation Filter'
    } else if (String(funcName) === 'Add Time Periods') {
      funcName = 'Add Time Periods'
    } else if (String(funcName) === 'Add Column') {
      funcName = 'Data Transformation Add Column'
    } else if (String(funcName) === 'Sort') {
      funcName = 'Data Transformation Sort'
    } else if (String(funcName) === 'Data Utilities') {
      funcName = 'Data Utilities'
    } else if (String(funcName) === 'Groupby') {
      funcName = 'Data Transformation Groupby'
    } else if (String(funcName) === 'Pivot') {
      funcName = 'Data Transformation Pivot'
    } else if (String(funcName) === 'Unpivot') {
      funcName = 'Data Transformation Unpivot'
    } else if (String(funcName) === 'Add Fix Column') {
      funcName = 'Add Fix Column'
    } else if (String(funcName) === 'Concat Columns') {
      funcName = 'Concat Columns'
    } else if (String(funcName) === 'Drop Duplicate') {
      funcName = 'Drop Duplicate'
    } else if (String(funcName) === 'Weighted Average') {
      funcName = 'Elementary Statistics'
    } else if (String(funcName) === 'Sum Product') {
      funcName = 'Elementary Statistics'
    } else if (String(funcName) === 'Fill Missing Values') {
      funcName = 'Missing Value'
    } else if (String(funcName) === 'Delimit Column') {
      funcName = 'Delimit Column'
    } else if (String(funcName) === 'Days') {
      funcName = 'Days'
    } else if (String(funcName) === 'Date') {
      funcName = 'Date'
    } else if (String(funcName) === 'Find and Replace') {
      funcName = 'Find and Replace'
    } else if (String(funcName) === 'Workdays.Intl') {
      funcName = 'Workdays.Intl'
    } else if (String(funcName) === 'Workdays') {
      funcName = 'Workdays'
    } else if (String(funcName) === 'Networkdays.Intl') {
      funcName = 'Networkdays.Intl'
    } else if (String(funcName) === 'Networkdays') {
      funcName = 'Networkdays'
    } else if (String(funcName) === 'Yearfrac') {
      funcName = 'Yearfrac'
    } else if (String(funcName) === 'Year') {
      funcName = 'Year'
    } else if (String(funcName) === 'Weeknum') {
      funcName = 'Weeknum'
    } else if (String(funcName) === 'Weekday') {
      funcName = 'Weekday'
    } else if (String(funcName) === 'Today') {
      funcName = 'Today'
    } else if (String(funcName) === 'Time') {
      funcName = 'Time'
    } else if (String(funcName) === 'Second') {
      funcName = 'Second'
    } else if (String(funcName) === 'Now') {
      funcName = 'Now'
    } else if (String(funcName) === 'Month') {
      funcName = 'Month'
    } else if (String(funcName) === 'Minute') {
      funcName = 'Minute'
    } else if (String(funcName) === 'Isoweeknum') {
      funcName = 'Isoweeknum'
    } else if (String(funcName) === 'Hour') {
      funcName = 'Hour'
    } else if (String(funcName) === 'Eomonth') {
      funcName = 'Eomonth'
    } else if (String(funcName) === 'Days360') {
      funcName = 'Days360'
    } else if (String(funcName) === 'Edate') {
      funcName = 'Edate'
    } else if (String(funcName) === 'Day') {
      funcName = 'Day'
    } else {
      funcName = 'Data Transformation'
    }

    if (String(i) === '0') {
      for (let j = 0; j < finalList.length; j++) {
        c = {
          element_id: finalList[j],
          text: 'Import Data',
          parent: '#',
          child: [
            cc
          ]
        }
        configDict.push(c)
      }
      if (String(i) === String(a.length - 1)) {
        c = {
          element_id: cc,
          text: funcName,
          parent: finalList,
          child: '#'
        }
        if ($('#exportEqData').attr('data-element_id')) {
          c.child = [$('#exportEqData').attr('data-element_id')]
        }
        configDict.push(c)
      } else {
        c = {
          element_id: cc,
          text: funcName,
          parent: finalList,
          child: next
        }
        configDict.push(c)
      }
    } else {
      if (String(iList.length) === '1' && String(funcName) === 'Data Transformation') {
        c = {
          element_id: iList[0],
          text: 'Import Data',
          parent: '#',
          child: [curr]
        }
        configDict.push(c)
      }

      if (String(i) === String(a.length - 1)) {

        if (funcName == "Data Transformation Filter" || funcName == 'Data Transformation Sort' || funcName == "Data Transformation Add Column" || funcName == 'Data Transformation Groupby' || funcName == 'Data Transformation Pivot' || funcName == 'Data Transformation Unpivot') {
          funcName = "Data Transformation"
        }

        c = {
          element_id: curr,
          text: funcName,
          parent: b,
          child: '#'
        }
        if ($('#exportEqData').attr('data-element_id')) {
          c.child = [$('#exportEqData').attr('data-element_id')]
        }
        configDict.push(c)
      } else {

        if (funcName == "Data Transformation Filter" || funcName == 'Data Transformation Sort' || funcName == "Data Transformation Add Column" || funcName == 'Data Transformation Groupby' || funcName == 'Data Transformation Pivot' || funcName == 'Data Transformation Unpivot') {
          funcName = "Data Transformation"
        }

        c = {
          element_id: curr,
          text: funcName,
          parent: b,
          child: next
        }
        configDict.push(c)
      }
    }
  }

  if ($('#exportEqData').attr('data-element_id')) {
    c = {
      element_id: $('#exportEqData').attr('data-element_id'),
      text: 'Export Data',
      parent: [$('.ebFunctions .function').last().find('a').attr('data-element_id')],
      child: '#'
    }
    configDict.push(c)
  }
  $.ajax({
    url: `/users/${urlPath}/computationModule/`,
    data: {
      xml: 'innn',
      model_name: mod_name,
      operation: 'save_flowchart',
      configList: JSON.stringify({ data3: configDict }),
      data_id: 'datamgm',
    },
    type: 'POST',
    dataType: 'json',
    success: function (data) {
      Swal.fire({icon: 'success',text: 'Model saved successfully!.'});
    },
    error: function () {
      Swal.fire({icon: 'error',text: 'Error! Failure in saving the Model. Please try again.'});
    }
  })

}