/* eslint-disable no-tabs */
/* eslint-disable semi */
/* eslint-disable comma-dangle */
/* eslint-disable no-use-before-define */
// eslint-disable-next-line no-redeclare
/* global Option,ctoken,FormData,item_code_list,tableName:true,columnsql:true */
/* eslint no-undef: "error" */
// eslint-disable-next-line no-unused-vars
function masterStandardButtonFunc () {
  let elementID = '';
  $('.button_standard_save').click(buttonClickFunction);
  $('.standard_button_click').click(buttonClickNorefresh);
  $('.columnMapperButton').on('click', uploadmapper);
  $('.submitconfigmapper').on('click', SubmitConfigmapper);
  $('.columnconfiguremapper').on('click', columnMapper);
  $('.loadConfigMapper').on('click', loadConfigMapper);
  $('.savecolumnconfiguremapper').on('click', saveColumnMapper);
  $('.fieldUploadMapperButton').off('click').on('click', uploadmapperDev)
  $('.columnconfiguremapperdev').on('click', columnMapperDev);
  $('.savecolumnconfiguremapperdev').on('click', saveColumnMapperDev);
  $('.loadConfigMapperdev').on('click', loadConfigMapperDev);
  $('.columnMapperButtonBulkUpdate').on('click', uploadmapperBU);
  $('.columnconfiguremapperBU').on('click', columnMapperBU);
  $('.savecolumnconfiguremapperBU').on('click', saveColumnMapperBU);

  $('.saveConfigMapper').on('click', function () {
    elementID = $(this).attr('data-elementID');
    saveConfigMapper(elementID);
  });

  // Custom Validation
  $('.customValidationButton').on('click', customTable);

  $('.submitcustomvalidation').on('click', function () {
    elementID = $(this).attr('data-elementID');
    setCondition(elementID);
  });

  function buttonClickFunction () {
    elementID = $(this).attr('id');
    setTimeout(function () {
      $('#' + elementID).prop('disabled', 'disabled');
    }, 100);
  }

  function buttonClickNorefresh () {
    $(this).prop('disabled', 'disabled');
  }

  // Add the following code if you want the name of the file appear on select
  $('.custom-file-input').on('change', function (e) {
    var fileName = ``
    for (let h = 0; h < e.target.files.length; h++){
      fileName += `${e.target.files[h].name} `
    }
    $(this).siblings(".custom-file-label").addClass("selected").html(fileName);
    $(this).siblings(".custom-file-label").attr('data-toggle', "tooltip");
    $(this).siblings(".custom-file-label").attr('title', fileName);
    $(this).attr('data-toggle', "tooltip");
    $(this).attr('title', fileName);
  });

  // Custom Validation Section
  function customTable () {
    const elementID = $(this).attr('data-elementID');
    // Condition Card
    let tableList = $(this).attr('data-table-name');
    if (tableList.startsWith('[')) {
      tableList = JSON.parse(tableList);
    }
    if (tableList.constructor === Array) {
      $(`#custommValidationSelection_${elementID}`).empty();
      $(`#custommValidationSelection_${elementID}`).append(
        "<option value='value'selected disabled>Select Option Name</option>"
      );
      for (let i = 0; i < tableList.length; i++) {
        $(`#custommValidationSelection_${elementID}`).append(
          new Option(tableList[i], tableList[i])
        );
      }
    } else {
      $(`#custommValidationSelection_${elementID}`).empty();
      $(`#custommValidationSelection_${elementID}`).append(
        "<option value='value'selected disabled>Select Option Name</option>"
      );
      $(`#custommValidationSelection_${elementID}`).append(
        new Option(tableList, tableList)
      );
    }
    reloadCustomValidation(elementID);
  }


  function fetch_custom_msg(msg, elementID, modelname, fieldDelName){
    $.ajax({
      url: `/users/${urlPath}/dynamicVal/`,

      data: {'operation': 'fetch_custom_messages','element_id':  elementID, 'message':msg},
      type: "POST",
      dataType: "json",
      success: function (data) {
        var text = ``
        var icon =""
        if(data.data.custom_messages){
          text = data.data.custom_messages.message
          icon = data.data.custom_messages.icon
        }

        if(msg == "custom_val_applied_message"){
          iconHtml = ""
          if (icon){
            iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
          }
          Swal.fire({icon: 'success', iconHtml, text: text || 'Custom Validation applied successfully!'});

          $(`#customValidationList${elementID}`).attr(
            'value',
            data.reload_custom_validation
          );
          $(`#customValidationList1${elementID}`).attr(
            'value',
            data.reload_custom_validation
          );
        }
        else if(msg == "custom_val_removed_message"){
          if ($(`#customValidationList${elementID}`).attr('value')) {
            $(`#customValidationList${elementID}`).attr('value', '');
            $(`#customValidationList1${elementID}`).attr('value', '');

            iconHtml = ""
            if (icon){
              iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
            }
            Swal.fire({icon: 'success', iconHtml, text: text || 'Custom Validation removed successfully!'});

          } else {
            Swal.fire({icon: 'warning',text: "No custom validation is set."});
          }

        }
        else if(msg == "custom_val_load_message"){
          iconHtml = ""
          if (icon){
            iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
          }
          Swal.fire({
            title: modelname,
            icon: 'question',
            iconHtml,
            text: text ||  `Do you wish to load the ${modelname} configuration?\n\n Click 'Yes' to confirm or click 'No' if you do not wish to load it.`,
            showDenyButton: true,
            showCancelButton: true,
            confirmButtonText: 'Yes',
            denyButtonText:'No',
          }).then((result) => {
            if (result.isConfirmed) {
                $.ajax({
                  url: `/users/${urlPath}/constriant_get_data/`,
                  data: {
                    elementID: elementID,
                    operation: 'reload_config_mapper',
                  },
                  type: 'POST',
                  dataType: 'json',
                  success: function (data) {
                    if (
                      Object.prototype.hasOwnProperty.call(
                        data,
                        'reload_custom_validation'
                      )
                    ) {
                      if (data.reload_custom_validation) {
                        const rowData = JSON.parse(data.reload_custom_validation);
                        $.ajax({
                          url: `/users/${urlPath}/constriant_get_data/`,
                          data: {
                            model_name: modelname,
                            operation: 'custom_conditional_table',
                          },
                          type: 'POST',
                          dataType: 'json',
                          success: function (data) {
                            $(`#custommValidationSelection_${elementID}`)
                              .val(modelname)
                              .trigger('change');
                            for (const rowInnerData of rowData[modelname]) {
                              const name = rowInnerData.column_name;
                              const STRING = data.form_fields[name];
                              $(`#custom_validation_table_${elementID}`).append(STRING);
                              $(`#custom_validation_table_${elementID} tr`).eq(-1).find('td').eq(3).find('div').find('select').removeAttr('onchange')
                              $(`#custom_validation_table_${elementID} tr`)
                                .eq(-1)
                                .find('select')
                                .each(function () {
                                  parent = $(this).parent()
                                  $(this).select2({dropdownParent:parent})
                                });
                              $(`#custom_validation_table_${elementID} tr`)
                                .eq(-1)
                                .find('td')
                                .eq(1)
                                .find('div')
                                .find('input')
                                .val(rowInnerData.constraint_name)
                                .trigger('change');
                              $(`#custom_validation_table_${elementID} tr`)
                                .eq(-1)
                                .find('td')
                                .eq(2)
                                .find('div')
                                .find('input')
                                .val(rowInnerData.rule_set)
                                .trigger('change');

                              $(`#custom_validation_table_${elementID} tr`)
                                .eq(-1)
                                .find('td')
                                .eq(3)
                                .find('div')
                                .find('select')
                                .val(rowInnerData.condition_name)
                                .trigger('change');
                              $(`#custom_validation_table_${elementID} tr`)
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
                                $(`#custom_validation_table_${elementID}`).append(STRING);
                                $(`#custom_validation_table_${elementID} tr`).eq(-1).find('td').eq(3).find('div').find('select').attr('data-data',rowInnerData.input_value)
                                $(`#custom_validation_table_${elementID} tr`)
                                  .eq(-1)
                                  .find('select')
                                  .each(function () {
                                    parent = $(this).parent()
                                    $(this).select2({dropdownParent:parent})
                                  });
                                $(`#custom_validation_table_${elementID} tr`)
                                  .eq(-1)
                                  .find('td')
                                  .eq(1)
                                  .find('div')
                                  .find('input')
                                  .val(rowInnerData.constraint_name)
                                  .trigger('change');
                                $(`#custom_validation_table_${elementID} tr`)
                                  .eq(-1)
                                  .find('td')
                                  .eq(2)
                                  .find('div')
                                  .find('input')
                                  .val(rowInnerData.rule_set)
                                  .trigger('change');

                                $(`#custom_validation_table_${elementID} tr`)
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
                  },
                  error: function () {
                    Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                  },
                });
              }

          });


        }
        else if(msg == "custom_val_delete_message"){
          iconHtml = ""
          if (icon){
            iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
          }
          Swal.fire({
            title: fieldDelName,
            icon: 'question',
            iconHtml,
            text: text || `Do you wish to delete ${fieldDelName} configuration ?`,
            showDenyButton: true,
            showCancelButton: true,
            confirmButtonText: 'Yes',
            denyButtonText:'No',
          }).then((result) => {
            if (result.isConfirmed) {

              $.ajax({
                url: `/users/${urlPath}/constriant_get_data/`,
                data: {
                  elementID: elementID,
                  field_delete_name: fieldDelName,
                  operation: 'delete_custom_validation',
                },
                type: 'POST',
                dataType: 'json',
                // eslint-disable-next-line no-unused-vars
                success: function (data) {
                  reloadCustomValidation(elementID);
                },
                error: function () {
                  Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                },
              });
            }
          })

        }

      },
      error: function () {
        Swal.fire({icon: 'error',text: 'Error! Please try again.'});
      }
    })
  }

  // Set Custom Validation
  function setCondition (elementID) {

    $.ajax({
      url: `/users/${urlPath}/constriant_get_data/`,
      data: {
        elementID: elementID,
        operation: 'reload_config_mapper',
      },
      type: 'POST',
      dataType: 'json',
      success: function (data) {
        if (
          Object.prototype.hasOwnProperty.call(data, 'reload_custom_validation')
        ) {
          if (data.reload_custom_validation) {
            fetch_custom_msg("custom_val_applied_message",elementID)
          }
        }
      },
      error: function () {
        Swal.fire({icon: 'error',text: 'Error! Failure in applying custom validation. Please try again.'});
      },
    });
  }

  $(document).on('click', '.removecustomvalidation', function () {
    elementID = $(this).attr('data-elementID');

    fetch_custom_msg("custom_val_removed_message",elementID)

  });

  // Load Custom Validation Of a Existing Table
  $(document).on('click', '.editcustomexist_validation', function () {
    elementID = $(this).attr('data-element-id');
    const modelName = $(this).attr('name');
    fetch_custom_msg("custom_val_load_message", elementID, modelName)


  });

  // Delete Custom Validation Of a Table
  $(document).on('click', '.reconfigurecustomvalidation', function () {
    elementID = $(this).attr('data-element-id');
    const fieldDeleteName = $(this).attr('name');

    fetch_custom_msg("custom_val_delete_message", elementID, null, fieldDeleteName)


  });

  //  Upload Mapper
  function uploadmapper () {
    elementID = $(this).attr('data-elementID');

    $(`.columnconfiguremapper[data-elementid=${elementID}]`).prop(
      'disabled',
      true
    );

    $(`#Columnmapper${elementID}`).on('select2:select', function () {
      if (
        $(this).val() != null &&
				$(`input[data-file-id=${elementID}]`).val()
      ) {
        $(`.columnconfiguremapper[data-elementid=${elementID}]`).prop(
          'disabled',
          false
        );
        $(`.saveConfigMapper[data-elementid=${elementID}]`).prop(
          'disabled',
          false
        );
      }
    });
    let tableList = $(this).attr('data-table-name');
    if (tableList.startsWith('[')) {
      tableList = JSON.parse(tableList);
    }

    $(`#Columnmapper${elementID}`).select2();
    if (tableList.constructor === Array) {
      $(`#Columnmapper${elementID}`).empty();
      $(`#Columnmapper${elementID}`).append(
        "<option value='value'selected disabled>Select Option Name</option>"
      );
      for (let i = 0; i < tableList.length; i++) {
        $(`#Columnmapper${elementID}`).append(
          new Option(tableList[i], tableList[i])
        );
      }
    } else {
      $(`#Columnmapper${elementID}`).empty();
      $(`#Columnmapper${elementID}`).append(
        "<option value='value'selected disabled>Select Option Name</option>"
      );
      $(`#Columnmapper${elementID}`).append(new Option(tableList, tableList));
    }

    let firstTime = false;
    if ($(`#columnmapperDict${elementID}`).attr('data-edit')) {
      reloadConfigData(elementID, firstTime);
    } else {
      firstTime = true;
      reloadConfigData(elementID, firstTime);
    }
  }

  function uploadmapperBU() {
    elementID = $(this).attr('data-elementID');

    $(`.columnconfiguremapperBU[data-elementID=${elementID}]`).prop(
      'disabled',
      true
    );

    $(`#ColumnmapperBU${elementID}`).on('select2:select', function () {
      if (
        $(this).val() != null &&
        $(`input[data-file-id-bk=${elementID}]`).val()
      ) {
        $(`.columnconfiguremapperBU[data-elementID=${elementID}]`).prop(
          'disabled',
          false
        );
        $(`.saveConfigMapperBU[data-elementID=${elementID}]`).prop(
          'disabled',
          false
        );
      }
    });
    let tableList = $(this).attr('data-table-name');
    if (tableList.startsWith('[')) {
      tableList = JSON.parse(tableList);
    }

    $(`#ColumnmapperBU${elementID}`).select2();
    if (tableList.constructor === Array) {
      $(`#ColumnmapperBU${elementID}`).empty();
      $(`#ColumnmapperBU${elementID}`).append(
        "<option value='value'selected disabled>Select table</option>"
      );
      for (let i = 0; i < tableList.length; i++) {
        $(`#ColumnmapperBU${elementID}`).append(
          new Option(tableList[i], tableList[i])
        );
      }
    } else {
      $(`#ColumnmapperBU${elementID}`).empty();
      $(`#ColumnmapperBU${elementID}`).append(
        "<option value='value'selected disabled>Select table</option>"
      );
      $(`#ColumnmapperBU${elementID}`).append(new Option(tableList, tableList));
    }

  }

  // eslint-disable-next-line no-var
  var dataForm = '';
  // eslint-disable-next-line no-var
  var columnsql = [];
  // eslint-disable-next-line no-var
  var tableName = '';
  function columnMapper () {
    elementID = $(this).attr('data-elementid');
    dataForm = new FormData(
      $(`form[data-form-id=uploadfileform${elementID}]`)[0]
    );
    dataForm.append('operation', 'columnmapper_global');
    tableName = $(this).parent().parent().find('select').val();
    dataForm.append('table_name', tableName);
    dataForm.append('elementID', elementID);
    const inputChecker = $(`form[data-form-id=uploadfileform${elementID}]`)
      .find('input[type=file]')
      .val();

    $('.saveConfigMapper').css('display', 'none');

    $.ajaxSetup({
      // eslint-disable-next-line no-unused-vars
      beforeSend: function (xhr, settings) {
        xhr.setRequestHeader('X-CSRFToken', ctoken);
      },
    });

    if (inputChecker) {

      $.ajax({
        url: `/users/${urlPath}/constriant_get_data/`,
        cache: false,
        contentType: false,
        processData: false,
        data: dataForm,
        type: 'POST',
        dataType: 'json',
        success: function (data) {
          $(`.submitconfigmapper[data-elementid=${elementID}]`).css(
            'display',
            'none'
          );

          $(`#modal-table-head${elementID}`).css('display', 'block');
          $(`#modal-table-head-done${elementID}`).css('display', 'none');
          $(`#modal-table-body-columnmapper${elementID}`).empty();

          columnsql = data.columnlist;

          let counter = 0;
          for (const indDict of data.columnlist) {
            let html = '';
            html += `<th id="Columnmapper1${elementID}_${[
							counter,
						]}">${indDict}</th>`;
            html += `<td ><select id="Columnmapper${elementID}_${[
							counter,
						]}" class="select2 form-control" name="Columnmapper"  data-placeholder="Column Mapper" >

                    </select></td>`;
            $(`#modal-table-body-columnmapper${elementID}`).append(
              '<tr>' + html + '</tr>'
            );
            $(`#modal-table-body-columnmapper${elementID}`)
              .find('.select2')
              .select2({ width: '100%' });

            for (let i = 0; i < data.columnlist1.length; i++) {
              $(`#Columnmapper${elementID}_${[counter]}`).append(
                new Option(data.columnlist1[i], data.columnlist1[i])
              );
            }
            $(`#Columnmapper${elementID}_${[counter]}`)
              .val(indDict)
              .trigger('change');

            counter++;
          }

          $(`.savecolumnconfiguremapper[data-elementID=${elementID}]`).css(
            'display',
            'block'
          );
          $(`#columnmapperDict${elementID}`).attr('data-checker', true);
        },
        error: function () {
          Swal.fire({icon: 'error',text: 'Error! Please try again.'});
        },
      });
    } else {
      Swal.fire({icon: 'error',text:"File not found." });
    }
  }


    // eslint-disable-next-line no-var
    var dataFormBU = '';
    // eslint-disable-next-line no-var
    var columnsqlBU = [];
    // eslint-disable-next-line no-var
    var tableNameBU = '';
    function columnMapperBU () {
      elementID = $(this).attr('data-elementID');
      dataFormBU = new FormData(
        $(`form[data-form-id=uploadfileform123${elementID}]`)[0]
      );
      dataFormBU.append('operation', 'columnmapper_global');
      tableNameBU = $(this).parent().parent().find('select').val();
      dataFormBU.append('table_name', tableNameBU);
      dataFormBU.append('elementID', elementID);
      const inputChecker = $(`form[data-form-id=uploadfileform123${elementID}]`)
        .find('input[type=file]')
        .val();

      $.ajaxSetup({
        // eslint-disable-next-line no-unused-vars
        beforeSend: function (xhr, settings) {
          xhr.setRequestHeader('X-CSRFToken', ctoken);
        },
      });

      if (inputChecker) {

        $.ajax({
          url: `/users/${urlPath}/constriant_get_data/`,
          cache: false,
          contentType: false,
          processData: false,
          data: dataFormBU,
          type: 'POST',
          dataType: 'json',
          success: function (data) {

            $(`#modal-table-headBU${elementID}`).css('display', 'block');
            $(`#modal-table-head-doneBU${elementID}`).css('display', 'none');
            $(`#modal-table-body-columnmapperBU${elementID}`).empty();

            columnsqlBU = data.columnlist;

            let counter = 0;
            for (const indDict of data.columnlist) {
              let html = '';
              html += `<th id="Columnmapper1${elementID}_${[
                counter,
              ]}">${indDict}</th>`;
              html += `<td ><select id="ColumnmapperBU${elementID}_${[
                counter,
              ]}" class="select2 form-control" name="Columnmapper"  data-placeholder="Column Mapper" >

                      </select></td>`;
              $(`#modal-table-body-columnmapperBU${elementID}`).append(
                '<tr>' + html + '</tr>'
              );
              $(`#modal-table-body-columnmapperBU${elementID}`)
                .find('.select2')
                .select2({ width: '100%' });

              for (let i = 0; i < data.columnlist1.length; i++) {
                $(`#ColumnmapperBU${elementID}_${[counter]}`).append(
                  new Option(data.columnlist1[i], data.columnlist1[i])
                );
              }
              $(`#ColumnmapperBU${elementID}_${[counter]}`)
                .val(indDict)
                .trigger('change');

              counter++;
            }

            $(`#columnmapperDictBU${elementID}`).attr('data-checker', true);
          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          },
        });
      } else {
        Swal.fire({icon: 'error',text:"File not found." });
      }
    }

  var submitFinalData = []; // eslint-disable-line no-var
  function saveColumnMapper () {
    elementID = $(this).attr('data-elementid');

    let finaldictcolumnmapper = [];

    const checkerDict = document
      .getElementById(`columnmapperDict${elementID}`)
      .getAttribute('data-save-config');

    if (checkerDict && String(checkerDict) !== '[]') {
      finaldictcolumnmapper = JSON.parse(checkerDict);
      for (let i = 0; i < finaldictcolumnmapper.length; i++) {
        const tm = Object.keys(finaldictcolumnmapper[i]);
        if (tm[0] === tableName) {
          const arrindex = finaldictcolumnmapper.indexOf(
            finaldictcolumnmapper[i]
          );
          finaldictcolumnmapper.splice(arrindex, 1);
        }
      }
    }
    const saveColumnDict = {};
    const columnmapperdict = [];
    const columnduplicatescheck = [];
    const duplicateChecker = [];

    for (let i = 0; i < columnsql.length; i++) {
      const columnmapperdict1 = {};
      const column2 = $(`#Columnmapper1${elementID}_${[i]}`).html();
      const column1 = $(`#Columnmapper${elementID}_${[i]}`).val();
      if (
        String(column1) !== 'undefined' &&
				column1 !== '' &&
				column1 !== null
      ) {
        if (columnduplicatescheck.includes(column1)) {
          $(`#samecolumnwarning${elementID}`).html(
						`${[
							column1,
						]} is already assigned to another column, please reconfigure the column mapper.`
          );
          duplicateChecker.push(true);
          $('.saveConfigMapper').css('display', 'none');
        } else {
          columnduplicatescheck.push(column1);
          columnmapperdict1[column1] = column2;
          columnmapperdict.push(columnmapperdict1);
          duplicateChecker.push(false);
        }
      }
    }
    if (!duplicateChecker.includes(true)) {
      $(`#samecolumnwarning${elementID}`).empty();
      $(`#modal-table-body-columnmapper${elementID}`).empty();
      $(`#modal-table-head-done${elementID}`).css('display', 'block');
      $(`#modal-table-head-done${elementID}`).empty();

      let html1 = '';
      html1 +=
				'<th style="text-align: center;font-weight:bold"  disabled>Table Name</th>';
      html1 +=
				'<td style="text-align: center;font-weight:bold" disabled>Reconfigure</td>';
      html1 +=
				'<td style="text-align: center;font-weight:bold" disabled>Apply</td>';
      $(`#modal-table-body-columnmapper${elementID}`).append(
        '<tr>' + html1 + '</tr>'
      );

      let tableSavedList = document
        .getElementById(`columnmapperDict${elementID}`)
        .getAttribute('value');

      if (tableSavedList && String(tableSavedList) !== '[]') {
        tableSavedList = JSON.parse(tableSavedList);

        for (const tableKeys of tableSavedList) {
          if (String(Object.keys(tableKeys)[0]) !== String(tableName)) {
            const tabName = Object.keys(tableKeys)[0];
            let html = '';
            html += `<th style="text-align: center;">${tabName}</th>`;
            html += `<td style="text-align: center;"><button type="button" class="btn-primary reconfigurecolumnmapper" name="${tabName}" id="reconfigurecolumnmapper_${tabName}"><i class="fas fa-trash"></i></button></td>`;
            html += `<td style="align-items: center;"><div class="custom-control custom-checkbox " style="margin-left:45%" >
              <input type="checkbox" class="applyConfig custom-control-input" name="${tabName}"  id=${
							tabName + elementID
						} data-elementid=${elementID} >
              <label for=${tabName + elementID} class="custom-control-label">
              </label>
                </div></td>`;
            $(`#modal-table-body-columnmapper${elementID}`).append(
              '<tr>' + html + '</tr>'
            );
          }
        }
      }

      let html = '';
      html += `<th style="text-align: center;">${[tableName]}</th>`;
      html += `<td style="text-align: center;"><button type="button" class="btn-primary reconfigurecolumnmapper" name="${[
				tableName,
			]}" id="reconfigurecolumnmapper_${[
				tableName,
			]}"><i class="fas fa-trash"></i></button></td>`;
      html += `<td style="align-items: center;"><div class="custom-control custom-checkbox " style="margin-left:45%" >

              <input type="checkbox" class="applyConfig custom-control-input" name="${[
								tableName,
							]}"  id=${[tableName] + elementID} data-elementid=${elementID} >
              <label for=${
								[tableName] + elementID
							} class="custom-control-label">
              </label>
            </div></td>`;
      $('input[type=checkbox]').prop('checked', false);
      $(`input[type=checkbox][name="${[tableName]}"]`).prop('checked', true);
      $(`#modal-table-body-columnmapper${elementID}`).append(
        '<tr>' + html + '</tr>'
      );
      saveColumnDict[tableName] = columnmapperdict;
      finaldictcolumnmapper.push(saveColumnDict);

      $('.applyConfig').change(function () {
        const applyName = $(this).attr('name');

        if ($(this).is(':checked')) {
          $('input[type=checkbox]').each(function () {
            if ($(this).attr('name') === applyName) {
              $(this).removeAttr('checked');
            } else {
              $(this).prop('checked', false);
            }
          });
        } else {
          $('input[type=checkbox]').each(function () {
            $('input[type=checkbox]').prop('checked', false);
            $(`#columnmapperDict${elementID}`).attr('value', '[]');
          });
        }
      });

      $('.reconfigurecolumnmapper').click(function () {
        $(`#samecolumnwarning${elementID}`).empty();
        const tmname = $(this).attr('name');
        $(`#Columnmapper${elementID}`)
          .find(`option[value='${tmname}']`)
          .removeAttr('disabled');
        $(this).closest('tr').remove();
        for (let i = 0; i < finaldictcolumnmapper.length; i++) {
          const tm = Object.keys(finaldictcolumnmapper[i]);
          if (String(tm[0]) === String(tmname)) {
            const arrindex = finaldictcolumnmapper.indexOf(
              finaldictcolumnmapper[i]
            );
            finaldictcolumnmapper.splice(arrindex, 1);
            $(`#columnmapperDict${elementID}`).attr(
              'data-save-config',
              JSON.stringify(finaldictcolumnmapper)
            );
          }
        }
        $(`#columnmapperDict${elementID}`).attr('data-edit', 'true');
      });
      $(this).css('display', 'none');
      $('.saveConfigMapper').css('display', 'block');
      $(`.submitconfigmapper[data-elementid=${elementID}]`).css(
        'display',
        'block'
      );
      $(`#columnmapperDict${elementID}`).attr(
        'data-save-config',
        JSON.stringify(finaldictcolumnmapper)
      );
      $(`#columnmapperDict${elementID}`).attr('data-edit', 'true');
      $(`.saveConfigMapper[data-elementid=${elementID}]`).prop(
        'disabled',
        false
      );
      submitFinalData = finaldictcolumnmapper;
    } else {
      $('.saveConfigMapper').css('display', 'none');
    }
  }


  var submitFinalDataBU = []; // eslint-disable-line no-var
  function saveColumnMapperBU () {
    elementID = $(this).attr('data-elementid');

    let finaldictcolumnmapper = [];

    const checkerDict = document
      .getElementById(`columnmapperDictBU${elementID}`)
      .getAttribute('data-save-config');

    if (checkerDict && String(checkerDict) !== '[]') {
      finaldictcolumnmapper = JSON.parse(checkerDict);
      for (let i = 0; i < finaldictcolumnmapper.length; i++) {
        const tm = Object.keys(finaldictcolumnmapper[i]);
        if (tm[0] === tableName) {
          const arrindex = finaldictcolumnmapper.indexOf(
            finaldictcolumnmapper[i]
          );
          finaldictcolumnmapper.splice(arrindex, 1);
        }
      }
    }
    const saveColumnDict = {};
    const columnmapperdict = [];
    const columnduplicatescheck = [];
    const duplicateChecker = [];

    for (let i = 0; i < columnsqlBU.length; i++) {
      const columnmapperdict1 = {};
      const column2 = $(`#Columnmapper1${elementID}_${[i]}`).html();
      const column1 = $(`#ColumnmapperBU${elementID}_${[i]}`).val();
      if (
        String(column1) !== 'undefined' &&
				column1 !== '' &&
				column1 !== null
      ) {
        if (columnduplicatescheck.includes(column1)) {
          $(`#samecolumnwarningBU${elementID}`).html(
						`${[
							column1,
						]} is already assigned to another column, please reconfigure the column mapper.`
          );
          duplicateChecker.push(true);

        } else {
          columnduplicatescheck.push(column1);
          columnmapperdict1[column1] = column2;
          columnmapperdict.push(columnmapperdict1);
          duplicateChecker.push(false);
        }
      }
    }
    if (!duplicateChecker.includes(true)) {

      saveColumnDict[tableNameBU] = columnmapperdict;
      finaldictcolumnmapper.push(saveColumnDict);

      $(`#columnmapperDictBU${elementID}`).attr(
        'value',
        JSON.stringify(finaldictcolumnmapper)
      );
      $(`#columnmapperDictBU${elementID}`).attr('data-edit', 'true');
      $(`#columnMapperModalBU${elementID}`).modal("hide")

      submitFinalDataBU = finaldictcolumnmapper;
    }
  }

  var finaldictcolumnmapperReload = []; // eslint-disable-line no-var
  var reloadChecker = ''; // eslint-disable-line no-var
  function reloadConfigData (elementID, firstTime) {
    $.ajax({
      url: `/users/${urlPath}/constriant_get_data/`,
      data: {
        elementID: elementID,
        operation: 'reload_config_mapper',
      },
      type: 'POST',
      dataType: 'json',
      success: function (data) {
        if (data.reload_data && firstTime === true) {
          finaldictcolumnmapperReload = JSON.parse(data.reload_data);
          $(`#samecolumnwarning${elementID}`).empty();
          $(`#modal-table-body-columnmapper${elementID}`).empty();
          $(`#modal-table-head-done${elementID}`).css('display', 'block');
          $(`#modal-table-head-done${elementID}`).empty();
          let html1 = '';
          html1 +=
						'<th style="text-align: center;font-weight:bold" disabled>Table Name</th>';
          html1 +=
						'<td style="text-align: center;font-weight:bold" disabled>Reconfigure</td>';
          html1 +=
						'<td style="text-align: center;font-weight:bold" disabled>Apply</td>';
          $(`#modal-table-body-columnmapper${elementID}`).append(
            '<tr>' + html1 + '</tr>'
          );
          for (const tableNamer of finaldictcolumnmapperReload) {
            let html = '';
            html += `<th style="text-align: center;">${
							Object.keys(tableNamer)[0]
						}</th>`;
            html += `<td style="text-align: center;"><button type="button" class="btn-primary reconfigurecolumnmapper" name="${
							Object.keys(tableNamer)[0]
						}" id="reconfigurecolumnmapper_${
							Object.keys(tableNamer)[0]
						}"><i class="fas fa-trash"></i></button></td>`;
            html += `<td style="align-items: center;"><div class="custom-control custom-checkbox " style="margin-left:45%" >
                   <input type="checkbox" class="applyConfig custom-control-input" name="${
											Object.keys(tableNamer)[0]
										}"  id=${
							Object.keys(tableNamer)[0] + elementID
						} data-elementid=${elementID} >
                   <label for=${
											Object.keys(tableNamer)[0] + elementID
										} class="custom-control-label">
                   </label>
                 </div></td>`;
            $(`#modal-table-body-columnmapper${elementID}`).append(
              '<tr>' + html + '</tr>'
            );
          }
          if (reloadChecker) {
            $(`input[type=checkbox][name=${reloadChecker}]`).prop(
              'checked',
              true
            );
          }

          $('.reconfigurecolumnmapper').click(function () {
            $(`#samecolumnwarning${elementID}`).empty();
            const tmname = $(this).attr('name');
            $(`#Columnmapper${elementID}`)
              .find(`option[value='${tmname}']`)
              .removeAttr('disabled');
            $(this).closest('tr').remove();
            for (let i = 0; i < finaldictcolumnmapperReload.length; i++) {
              const tm = Object.keys(finaldictcolumnmapperReload[i]);
              if (tm[0] === tmname) {
                const arrindex = finaldictcolumnmapperReload.indexOf(
                  finaldictcolumnmapperReload[i]
                );
                finaldictcolumnmapperReload.splice(arrindex, 1);
                $(`#columnmapperDict${elementID}`).attr('value', '[]');
                $(`#columnmapperDict${elementID}`).attr(
                  'data-save-config',
                  JSON.stringify(finaldictcolumnmapperReload)
                );
              }
            }
            $(`.columnconfiguremapper[data-elementid=${elementID}]`).prop(
              'disabled',
              false
            );
            $(`.saveConfigMapper[data-elementid=${elementID}]`).prop(
              'disabled',
              false
            );
            $(`.loadConfigMapper[data-elementid=${elementID}]`).prop(
              'disabled',
              false
            );
          });

          $('.applyConfig').change(function () {
            const applyName = $(this).attr('name');
            reloadChecker = applyName;
            if ($(this).is(':checked')) {
              $('input[type=checkbox]').each(function () {
                if ($(this).attr('name') === applyName) {
                  $(this).removeAttr('checked');
                  $(`.submitconfigmapper[data-elementid=${elementID}]`).css(
                    'display',
                    'block'
                  );
                } else {
                  $(this).prop('checked', false);
                }
              });
            } else {
              $('input[type=checkbox]').each(function () {
                $('input[type=checkbox]').prop('checked', false);
                $(`#columnmapperDict${elementID}`).attr('value', '[]');
              });
            }
          });
          $(`#columnmapperDict${elementID}`).attr('data-has-reloaded', 'true');
        }
      },
      error: function () {
        Swal.fire({icon: 'error',text: 'Error! Failure in saving configuration. Please check your configuration and try again.'});
      },
    });
  }

  function saveConfigMapper (elementID) {
    const oldDataLoad = finaldictcolumnmapperReload;
    const newDataLoad = JSON.parse(
      $(`#columnmapperDict${elementID}`).attr('data-save-config')
    );
    for (const j of newDataLoad) {
      for (let i = 0; i < oldDataLoad.length; i++) {
        const tm = Object.keys(oldDataLoad[i]);
        if (String(tm[0]) === String(Object.keys(j)[0])) {
          const arrindex = oldDataLoad.indexOf(oldDataLoad[i]);
          oldDataLoad.splice(arrindex, 1);
        }
      }
    }
    if (oldDataLoad.length > 0) {
      for (const i of oldDataLoad) {
        newDataLoad.push(i);
      }
    }


    $.ajax({
      url: `/users/${urlPath}/constriant_get_data/`,
      data: {
        elementID: elementID,
        mapper_data: JSON.stringify(newDataLoad),
        operation: 'save_config_mapper',
      },
      type: 'POST',
      dataType: 'json',
      // eslint-disable-next-line no-unused-vars
      success: function (data) {
        $.ajax({
          url: `/users/${urlPath}/dynamicVal/`,

          data: { 'operation': 'fetch_upload_view_custom_messages',
                  'element_id':  elementID,
                  'messages' : JSON.stringify(["save_column_mapper_message"]),
                },
          type: "POST",
          dataType: "json",
          success: function (response) {

              message=""
              icon=""
              if(response.save_column_mapper_message){
                message = response.save_column_mapper_message.message
                icon = response.save_column_mapper_message.icon
              }

              iconHtml = ""
              if (icon){
                iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
              }

            Swal.fire({icon: 'success',iconHtml, text: message || 'Configuration saved successfully!'});
          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          },
        });
      },
      error: function () {
        Swal.fire({icon: 'error',text: 'Error! Failure in saving configuration. Please check your configuration and try again.'});
      },
    });
  }

  function SubmitConfigmapper () {
    elementID = $(this).attr('data-elementid');

    $.ajax({
      url: `/users/${urlPath}/dynamicVal/`,

      data: { 'operation': 'fetch_upload_view_custom_messages',
              'element_id':  elementID,
              'messages' : JSON.stringify(["submit_mapper_config_message","select_table_mapper_config_message"]),
            },
      type: "POST",
      dataType: "json",
      success: function (response) {

        const finalTableName = $(
          `input[type=checkbox][data-elementid=${elementID}]:checked`
        ).attr('name');
        if (finalTableName) {

          message=""
          icon=""
          if(response.submit_mapper_config_message){
            message = response.submit_mapper_config_message.message
            icon = response.submit_mapper_config_message.icon
          }

          iconHtml = ""
          if (icon){
            iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
          }

          if (submitFinalData.length > 0) {
            for (let i = 0; i < submitFinalData.length; i++) {
              let tm = Object.keys(submitFinalData[i]);
              if (String(tm[0]) === String(finalTableName)) {
                $(`#columnmapperDict${elementID}`).attr(
                  'value',
                  JSON.stringify([submitFinalData[i]])
                );
              } else {
                for (let i = 0; i < finaldictcolumnmapperReload.length; i++) {
                  tm = Object.keys(finaldictcolumnmapperReload[i]);
                  if (String(tm[0]) === String(finalTableName)) {
                    $(`#columnmapperDict${elementID}`).attr(
                      'value',
                      JSON.stringify([finaldictcolumnmapperReload[i]])
                    );
                  }
                }
              }
            }
            Swal.fire({icon: 'success',iconHtml,text: message || 'Mapper configuration submitted successfully!'});
            $(`#columnMapperModal${elementID}`).modal('hide');
          } else {
            for (let i = 0; i < finaldictcolumnmapperReload.length; i++) {
              const tm = Object.keys(finaldictcolumnmapperReload[i]);
              if (String(tm[0]) === String(finalTableName)) {
                $(`#columnmapperDict${elementID}`).attr(
                  'value',
                  JSON.stringify([finaldictcolumnmapperReload[i]])
                );
              }
            }
            Swal.fire({icon: 'success',iconHtml,text: message ||  'Mapper configuration submitted successfully!'});
            $(`#columnMapperModal${elementID}`).modal('hide');
          }
        } else {
          message=""
          icon=""
          if(response.select_table_mapper_config_message){
            message = response.select_table_mapper_config_message.message
            icon = response.select_table_mapper_config_message.icon
          }

          iconHtml = ""
          if (icon){
            iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
          }

          Swal.fire({icon: 'warning',iconHtml, text: message || "Select the Table Name." });
        }

      },
      error: function () {
        Swal.fire({icon: 'error',text: 'Error! Please try again.'});
      }
    })



  }

  function loadConfigMapper () {
    // eslint-disable-line no-unused-vars
    elementID = $(this).attr('data-elementid');
    const dataForm = new FormData(
      $(`form[data-form-id=uploadfileform${elementID}]`)[0]
    );
    dataForm.append('operation', 'columnmapper_global');
    tableName = $(
			`input[type=checkbox][data-elementid=${elementID}]:checked`
    ).attr('name');
    if (String(tableName) === 'null' || String(tableName) === 'undefined') {
      tableName = $('select').val();
    }

    dataForm.append('table_name', tableName);
    dataForm.append('elementID', elementID);
    const inputChecker = $(`form[data-form-id=uploadfileform${elementID}]`)
      .find('input[type=file]')
      .val();

    if (tableName && inputChecker) {
      $(`.submitconfigmapper[data-elementid=${elementID}]`).css(
        'display',
        'none'
      );
      $.ajax({
        url: `/users/${urlPath}/constriant_get_data/`,
        cache: false,
        contentType: false,
        processData: false,
        data: dataForm,
        type: 'POST',
        dataType: 'json',
        success: function (data) {
          if (data.saved_data) {
            if (data.saved_data.length > 0) {
              $(`#columnmapperDict${elementID}`).attr(
                'value',
                JSON.stringify(data.saved_data)
              );
            }
          }
          for (const save1 of data.saved_data) {
            if (String(tableName) === String(Object.keys(save1)[0])) {
              $('.saveConfigMapper').css('display', 'none');
              $(`#modal-table-head${elementID}`).css('display', 'block');
              $(`#modal-table-head-done${elementID}`).css('display', 'none');
              $(`#modal-table-body-columnmapper${elementID}`).empty();

              columnsql = data.columnlist;

              let counter = 0;
              for (const indDict of data.columnlist) {
                let html = '';
                html += `<th id="Columnmapper1${elementID}_${[
									counter,
								]}">${indDict}</th>`;
                html += `<td ><select id="Columnmapper${elementID}_${[
									counter,
								]}" data-reload-value='${indDict}' class="select2 form-control" name="Columnmapper"  data-placeholder="Column Mapper" >
                    </select></td>`;
                $(`#modal-table-body-columnmapper${elementID}`).append(
                  '<tr>' + html + '</tr>'
                );
                $(`#modal-table-body-columnmapper${elementID}`)
                  .find('.select2')
                  .select2({ width: '100%' });

                for (let i = 0; i < data.columnlist1.length; i++) {
                  $(`#Columnmapper${elementID}_${[counter]}`).append(
                    new Option(data.columnlist1[i], data.columnlist1[i])
                  );
                }
                $(`#Columnmapper${elementID}_${[counter]}`)
                  .val(indDict)
                  .trigger('change');
                counter++;
              }
              for (const save2 of save1[tableName]) {
                $(`select[data-reload-value=${Object.values(save2)[0]}]`)
                  .val(Object.keys(save2)[0])
                  .trigger('change');
              }
              $(`.savecolumnconfiguremapper[data-elementID=${elementID}]`).css(
                'display',
                'block'
              );
            }
          }
        },
        error: function () {
          Swal.fire({icon: 'error',text: 'Error! Please try again.'});
        },
      });
    } else {
      Swal.fire({icon: 'warning',text:"No Table selected / File not found." });
    }
  }
}

// Populate Custom Validation Condition DropDown
// eslint-disable-next-line no-unused-vars
function conditionalTable (elementID) {
  $(`#custom_validation_table_${elementID}`).empty();
  $(`#condition_dropdown${elementID}`).empty();
  $(`#condition_dropdown1${elementID}`).empty();

  $.ajax({
    url: `/users/${urlPath}/constriant_get_data/`,
    data: {
      model_name: $(`#custommValidationSelection_${elementID}`).val(),
      operation: 'custom_conditional_table',
    },
    type: 'POST',
    dataType: 'json',
    success: function (data) {
      const labelColumn = data.label_columns;

      $(`#condition_dropdown${elementID}`).empty();
      $(`#condition_dropdown1${elementID}`).empty();
      for (const [key, value] of Object.entries(labelColumn)) {
        $(`#condition_dropdown${elementID}`).append(
          '<li class="dropdown-item"><a href="javascript:void(0)" name=' +
						key +
						' class="filter_btn">' +
						value +
						'</a></li>'
        );
        $(`#condition_dropdown1${elementID}`).append(
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
        $(`#custom_validation_table_${elementID}`).append(STRING);

        $(`#custom_validation_table_${elementID} tr`)
          .eq(-1)
          .find('select')
          .each(function () {
            parent = $(this).parent()
    $(this).select2({dropdownParent:parent})
          });

        $('.remove_filter').on('click', removefilter);

        function removefilter () {
          $(this).closest('tr').remove();
        }
      });

      $('.filter_btn_master').click(function () {
        const name = $(this).attr('name');
        const STRING = data.form_fields_master[name];
        $(`#custom_validation_table_${elementID}`).append(STRING);

        $(`#custom_validation_table_${elementID} tr`)
          .eq(-1)
          .find('select')
          .each(function () {
            parent = $(this).parent()
    $(this).select2({dropdownParent:parent})
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

// Save Custom Configuration
// eslint-disable-next-line no-unused-vars
function saveCustomValidation (elementID) {
  const tableDict = {};
  const conditionList = [];
  let conditionListMaster = []
  let nullChecker = false;

  $(`#custom_validation_table_${elementID}`)
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
  tableDict[$(`#custommValidationSelection_${elementID}`).val()] =
		conditionList;

    $(`#custom_validation_table_${elementID}`)
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
    $.ajax({
      url: `/users/${urlPath}/constriant_get_data/`,
      data: {
        model_name: $(`#custommValidationSelection_${elementID}`).val(),
        elementID: elementID,
        custom_validation_data: JSON.stringify(tableDict),
        operation: 'save_custom_validation',
      },
      type: 'POST',
      dataType: 'json',
      // eslint-disable-next-line no-unused-vars
      success: function (data) {
        iconHtml = ""
        if (data.custom_icon){
          iconHtml = `<i class="${data.custom_icon}" style="border: 0 !important;"></i>`
        }
        Swal.fire({icon: 'success', iconHtml, text: data.custom_msg || 'Custom validation configuration saved successfully!'});

        $(
					`.carousel-control-prev[href='#carouselCustomValidation${elementID}']`
        ).click();
        setTimeout(function () {
          reloadCustomValidation(elementID);
        }, 250);
      },
      error: function () {
        Swal.fire({icon: 'error',text: 'Error! Please try again.'});
      },
    });
  }
}

// Reload Stored Custom Validation
function reloadCustomValidation (elementID) {
  $.ajax({
    url: `/users/${urlPath}/constriant_get_data/`,
    data: {
      elementID: elementID,
      operation: 'reload_config_mapper',
    },
    type: 'POST',
    dataType: 'json',
    success: function (data) {
      if (
        Object.prototype.hasOwnProperty.call(data, 'reload_custom_validation')
      ) {
        if (data.reload_custom_validation) {
          const rowData = JSON.parse(data.reload_custom_validation);
          $(`#configuration_val_row_${elementID}`).empty();
          let rowHtml = '';
          let count = 1;
          for (const rowName in rowData) {
            if(rowName != "Master_filter"){
              rowHtml += `<tr> <td>${count}</td> <td value='${rowName}'>${rowName}</td> <td><button type="button" class="btn-primary reconfigurecustomvalidation" name="${rowName}" data-element-id="${elementID}" id="reconfigurecustomvalidation_${rowName}"><i class="fas fa-trash"></i></button> <button type="button" class="btn-primary editcustomexist_validation" name="${rowName}" data-element-id="${elementID}" href="#carouselCustomValidation${elementID}" data-slide="next" id="editcustomexist_validation_${rowName}"><i class="fas fa-edit"></i></button></td></tr>`;

              count++;
            }
          }
          $(`#configuration_val_row_${elementID}`).append(rowHtml);
          $(`#customValidationList${elementID}`).attr(
            'value',
            data.reload_custom_validation
          );
          $(`#customValidationList1${elementID}`).attr(
            'value',
            data.reload_custom_validation
          );
        }
      }
    },
    error: function () {
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    },
  });
}

// End Custom Validation Section

// Set Sheet Name
// eslint-disable-next-line no-unused-vars
function setSheetName (elementID) {
  const sheetname = $(`#sheetNameChange_content${elementID}`)
    .find('tr')
    .find('td')
    .eq(0)
    .text();
  const tableName = $(`#configure_sheet${elementID}`).val();
  const dummyDict = {};
  dummyDict[sheetname] = tableName;
  $(`#edit_upload_save${elementID}`).attr(
    'data-sheet-details',
    JSON.stringify(dummyDict)
  );
  $(`#edit_upload_save${elementID}`).click();
}

// eslint-disable-next-line no-unused-vars
function setSkipSheetName (elementID) {
  let sheetname = [
    $(`#sheetNameChange_content${elementID}`)
      .find('tr')
      .find('td')
      .eq(0)
      .text(),
  ];
  if ($(`#SkipSheetInfo${elementID}`).attr('data-skip-sheet')) {
    let oldSheets = $(`#SkipSheetInfo${elementID}`).attr('data-skip-sheet');
    if (oldSheets) {
      oldSheets = JSON.parse(oldSheets);
      sheetname = [...sheetname, ...oldSheets];
    }
  }

  $(`#SkipSheetInfo${elementID}`).attr(
    'data-skip-sheet',
    JSON.stringify(sheetname)
  );
  $(`#edit_upload_save${elementID}`).click();
}


// eslint-disable-next-line no-unused-vars
function UploadDatafunc (dataForm, elementID) {
  const n = windowLocationAttr.href.includes('multiupload/');
  var fileImportEngineConfig = $(`#advance_pandas_settings_upload${elementID}`).attr('data-config')
  if (!fileImportEngineConfig) {
      fileImportEngineConfig = '{}';
  }
  dataForm.append("import_engine_config", fileImportEngineConfig)
  let url = '';
  if (String(n) === 'false') {
    url = windowLocationAttr.href + 'multiupload/';
    if (!url.includes('Pr')) {
      const idEle = elementID;
      // eslint-disable-next-line camelcase
      for (let z = 0; z < item_code_list.length; z++) {
        // eslint-disable-next-line camelcase
        if (Object.prototype.hasOwnProperty.call(item_code_list[z], idEle)) {
          // eslint-disable-next-line camelcase
          const itemCode_ = item_code_list[z][idEle];
          url = `/users/${urlPath}/` + itemCode_ + '/' + 'multiupload/';
          break;
        }
      }
    }
  } else {
    url = windowLocationAttr.href;
    if (!url.includes('Pr')) {
      const idEle = elementID;
      // eslint-disable-next-line camelcase
      for (let z = 0; z < item_code_list.length; z++) {
        // eslint-disable-next-line camelcase
        if (Object.prototype.hasOwnProperty.call(item_code_list[z], idEle)) {
          // eslint-disable-next-line camelcase
          const itemCode_ = item_code_list[z][idEle];
          url = `/users/${urlPath}/` + itemCode_ + '/';
          break;
        }
      }
    }
  }
  if($(`#find_replace_${elementID}`).attr("data-final-index") != "") {
    dataForm.append("edited_index", $(`#find_replace_${elementID}`).attr("data-final-index"))
  }

  var dash_null_dict = {}
  $(".select_dash_null").each(function() {
      if (!dash_null_dict[$(this).attr("data-tablename")]) {dash_null_dict[$(this).attr("data-tablename")] = {}}
      for (i in $(this).val()) {
        dash_null_dict[$(this).attr("data-tablename")][$(this).val()[i]] = $(this).parent().find(".select_dash_value").val()
      }
  })
  dataForm.append('dash_null_dict',JSON.stringify(dash_null_dict));
  if($(`#uploadButton3_preview${elementID}`).attr("ignore_ne") == "true") {
    dataForm.append('dup_col_check_dict', "true");
    $(`#uploadButton3_preview${elementID}`).attr("ignore_ne", "false")
  } else {
    dataForm.append('dup_col_check_dict', "false");
  }
    $.ajax({
    url: url,
    data: dataForm,
    contentType: false,
    cache: false,
    async: false,
    processData: false,
    type: 'POST',
    dataType: 'json',
    success: function (data) {
      if (Object.prototype.hasOwnProperty.call(data, 'no_file_found')) {
        windowLocationAttr.reload();
      } else if (Object.prototype.hasOwnProperty.call(data, 'dup_col_exists')) {
        $(`#bulk_upload_in_progress_${elementID}`).removeClass('show');
        $("body").css("pointer-events", "auto")
        Swal.fire({
          icon : 'warning',
          text: "The uploaded file contains columns that do not exist in the table. The data in these columns will not be considered. Do you still want to proceed?",
          showDenyButton: true,
          showCancelButton: false,
          confirmButtonText: 'Yes',
          denyButtonText: `No`,
        }).then((result) => {
          if (result.isConfirmed) {
            $(`#uploadButton3_preview${elementID}`).attr("ignore_ne", "false")
            $(`#uploadButton3_preview${elementID}`).trigger("click");
          }
          else{
            $(`#uploadButton3_preview${elementID}`).attr("ignore_ne", "true")
          }
        })

      } else if (
        Object.prototype.hasOwnProperty.call(data, 'changeSheetName')
      ) {
        $(`#edit_upload_save${elementID}`).removeAttr('data-sheet-details');
        const sheetname = data.changesheet;
        const tablelist = data.result_listt;
        $(`#sheetNameChange_content${elementID}`)
          .find('tr')
          .find('td')
          .eq(0)
          .text(sheetname)
          .trigger('change');
        $(`#configure_sheet${elementID}`).empty();
        $(`#configure_sheet${elementID}`).append(
          "<option value=' '> Select Table Name</option>"
        );
        if (tablelist) {
          for (const i of tablelist) {
            $(`#configure_sheet${elementID}`).append(
							`<option value='${i}'>${i}</option>`
            );
          }
        }

        setTimeout(function () {
          $(`#sheetNameChangeModal${elementID}`).modal('show');
        }, 1200);

        $(`#configure_sheet${elementID}`).select2({
          dropdownParent: $(`#sheetNameChangeModal${elementID}`),
          theme: 'classic',
          width: '90%',
        });
      } else if (Object.prototype.hasOwnProperty.call(data, 'sheetname')) {
        const sheetlist = JSON.parse(data.sheetname);
        if (Object.prototype.hasOwnProperty.call(data, 'job_id')) {
          Swal.fire({icon: 'success',text: `Validations successful! Uploading in progress for sheet ${sheetlist[sheetlist.length - 1]}...`});
        }
        $(`#edit_upload_save${elementID}`).attr('sheetname', data.sheetname);
        $(`#edit_upload_save${elementID}`).removeAttr('data-edit');
        $(`#edit_upload_save${elementID}`).click();
      } else {
        const colHeaders = JSON.parse(data.columns_header);
        $(`#find_replace_${elementID}`).attr('data-table-name', data.current_table_name);
        if (Object.prototype.hasOwnProperty.call(data, 'model_status')) {
          $(`#bulk_upload_in_progress_${elementID}`).removeClass('show');
          $("body").css("pointer-events", "auto")
          $(`#edit_upload_modal${elementID}`).modal('show');

          $(`#EditModalTab${elementID} li:last`).css("display", "none");
          $(
						`#EditModalTab${elementID} a[href="#upload_error_tab${elementID}"]`
          ).tab('show');

          const dropList = [
            'created_date',
            'modified_by',
            'modified_date',
            'created_by',
            'Error_Details',
            'total_error_count',
            'transaction_id',
          ];

          // Column Header
          let headerCol = '';
          for (let i = 0; i < colHeaders.length; i++) {
            if (dropList.includes(colHeaders[i]) === false) {
              headerCol += `<th value=${colHeaders[i]}>${colHeaders[i]}</th>`;
            }
          }
          // Error Tab

          let validationTable = '';
          if (Object.prototype.hasOwnProperty.call(data, 'validation_list')) {
            const validationList = JSON.parse(data.validation_list);
            for (const valName of validationList) {
              validationTable += `<tr><td>${Object.keys(valName)[0]}</td>`;

              for (let v = 0; v < colHeaders.length; v++) {
                if (dropList.includes(colHeaders[v]) === false) {
                  if (
                    valName[Object.keys(valName)[0]].includes(colHeaders[v])
                  ) {
                    validationTable +=
											"<td ><i class='fa fa-window-close'  style='color:red;'></i></td>";
                  } else {
                    validationTable +=
											"<td><i class='fa fa-check-circle' style='color:var(--primary-color);'></i></td>";
                  }
                }
              }
              validationTable += '</tr>';
            }
          }

          // Custom Validation Row
          let customValidationTable = '';

          if (
            Object.prototype.hasOwnProperty.call(data, 'custom_condition_dict')
          ) {
            if (String(data.custom_condition_dict) !== '{}') {
              const customValidationList = JSON.parse(
                data.custom_condition_dict
              );

              for (const customKey in customValidationList) {
                customValidationTable += `<tr><td>${customKey}</td>`;

                for (let v = 0; v < colHeaders.length; v++) {
                  if (dropList.includes(colHeaders[v]) === false) {
                    if (
                      Object.keys(customValidationList[customKey]).includes(
                        colHeaders[v]
                      )
                    ) {
                      const dictBeta = {};
                      dictBeta[colHeaders[v]] =
												customValidationList[customKey][colHeaders[v]];

                      if (dictBeta[colHeaders[v]].length > 0) {
                        customValidationTable += `<td><i class='fa fa-window-close error_highlight' data-target-index='${JSON.stringify(
													dictBeta
												)}' data-target-column='${
													colHeaders[v]
												}' style='color:red;cursor:pointer'></i></td>`;
                      } else {
                        customValidationTable += `<td><i class='fa fa-check-circle'     data-target-column='${colHeaders[v]}' style='color:var(--primary-color);'></i></td>`;
                      }
                    } else {
                      customValidationTable += `<td><i class='fa fa-check-circle'     data-target-column='${colHeaders[v]}' style='color:var(--primary-color);'></i></td>`;
                    }
                  }
                }
                customValidationTable += '</tr>';
              }
            }
          }

          $(`#upload_error_tab${elementID}`)
            .find('.error_validation_upload_card_content')
            .find('.card-body')
            .find(`#error_upload_modal_datatable${elementID}` + '_wrapper')
            .remove();
          $(`#upload_error_tab${elementID}`)
            .find('.error_validation_upload_card_content')
            .find('.card-body')
            .find(`#error_upload_modal_datatable${elementID}`)
            .remove();

          $('.error_summary_card').remove();

          const customDatatable = `
          <table id="error_upload_modal_datatable${elementID}" class="row-border display table" style="width: 100%;">
          <thead class="error_upload_header">
            <th>Validation Type</th>
            ${headerCol}
          </thead>
          <tbody id="error_upload_content">
            ${validationTable}
            ${customValidationTable}
          </tbody>
          </table>`;
          $(`#upload_error_tab${elementID}`)
            .find('.error_validation_upload_card_content')
            .find('.card-body')
            .append(customDatatable);

          // Count Status
          if (
            Object.prototype.hasOwnProperty.call(data, 'error_val_count_dict')
          ) {
            if (String(data.error_val_count_dict) !== '{}') {
              let errorCountHeader = '';
              let errorCountBody = '';

              const errorDict = JSON.parse(data.error_val_count_dict);

              for (let i = 0; i < colHeaders.length; i++) {
                if (dropList.includes(colHeaders[i]) === false) {
                  errorCountHeader += `<th value=${colHeaders[i]}> ${colHeaders[i]} </th>`;
                }
              }

              // Passed
              errorCountBody += "<tr><td style='font-weight:bold'>Passed</td>";
              for (const i in errorDict) {
                if (dropList.includes(i) === false) {
                  errorCountBody += `<td data-target-col='${errorDict[i]}'>${errorDict[i].Passed}</td>`;
                }
              }
              errorCountBody += '</tr>';

              // Failed
              errorCountBody += "<tr><td style='font-weight:bold'>Failed</td>";
              for (const i in errorDict) {
                if (dropList.includes(i) === false) {
                  errorCountBody += `<td data-target-col='${errorDict[i]}'>${errorDict[i].Failed}</td>`;
                }
              }
              errorCountBody += '</tr>';

              $(`#upload_error_tab${elementID}`)
                .find('.error_validation_upload_card_content')
                .find('.card-body')
                .find(
									`#error_validation_count_modal_datatable${elementID}` +
										'_wrapper'
                )
                .remove();
              $(`#upload_error_tab${elementID}`)
                .find('.error_validation_upload_card_content')
                .find('.card-body')
                .find(`#error_validation_count_modal_datatable${elementID}`)
                .remove();

              const customcountDatatable = `

              <table id="error_validation_count_modal_datatable${elementID}" class="row-border display table" style="width: 100%;">

              <thead class="error_validation_count_header">
                <th> Status </th>
                ${errorCountHeader}

              </thead>
              <tbody id="error_validation_count_content"  style="overflow-x: scroll;max-width: 200px;">
              ${errorCountBody}

              </tbody>
          </table>
              `;
              $(`#upload_error_tab${elementID}`)
                .find('.error_validation_upload_card_content')
                .find('.card-body')
                .append(customcountDatatable);
            }
          }

              if (Object.prototype.hasOwnProperty.call(data, 'job_id')) {

                $.ajax({
                  url: `/users/${urlPath}/dynamicVal/`,

                  data: { 'operation': 'fetch_upload_view_custom_messages',
                          'element_id':  elementID,
                          'messages' : JSON.stringify(["successful_validation_message","successful_upload_message"]),
                        },
                  type: "POST",
                  dataType: "json",
                  success: function (response) {

                    message=""
                    icon=""
                    if(response.successful_validation_message){
                      message = response.successful_validation_message.message
                      icon = response.successful_validation_message.icon
                    }

                    iconHtml = ""
                    if (icon){
                      iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
                    }

                    Swal.fire({icon: 'success', iconHtml, text: message || 'Validations successful! Uploading in progress...\n You may continue with other tasks. You`ll be notified via the notification bell on successful upload.'});

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
                        message=""
                        icon=""
                        if(response.successful_upload_message){
                          message = response.successful_upload_message.message
                          icon = response.successful_upload_message.icon
                        }

                        iconHtml = ""
                        if (icon){
                          iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
                        }
                        let result_string = "Upload successful!";
                        if(data.sheet_list !== undefined){
                          var sheet_list = JSON.parse(data.sheet_list)
                          sheet_list.forEach(function(value, index) {
                            result_string += value;
                              if (index < sheet_list.length - 1) {
                                result_string += ", ";
                              }
                          });
                        }
                        Swal.fire({icon: 'success', iconHtml, text: message || result_string}).then((result) => {
                          if (result.isConfirmed) {
                            windowLocationAttr.reload();
                          };
                        });
                      }
                    }
                  },
                  error: function () {
                    Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                  }
                })

              }else{

                $.ajax({
                  url: `/users/${urlPath}/dynamicVal/`,

                  data:
                  {
                    'operation': 'fetch_upload_view_custom_messages',
                    'element_id':  elementID,
                    'messages' : JSON.stringify(["successful_upload_message"]),
                  },
                  type: "POST",
                  dataType: "json",
                  success: function (response) {
                    message=""
                    icon=""
                    if(response.successful_upload){
                      message = response.successful_upload.message
                      icon = response.successful_upload.icon
                    }

                    iconHtml = ""
                    if (icon){
                      iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
                    }

                    Swal.fire({icon: 'success', iconHtml, text: message || 'Upload successful!'}).then((result) => {
                      if (result.isConfirmed) {
                        windowLocationAttr.reload();
                      };
                    });
                  },
                  error: function () {
                    Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                  }
                })

              }

        } else {
          $(
						`#EditModalTab${elementID} a[href="#edit_data_tab${elementID}"]`
          ).removeClass('disabled');
          const result = JSON.parse(data.result);
          const colHeaders = JSON.parse(data.columns_header);
          const storedUpdateData = data.stored_updated_data;

          let headerCol = '';
          let tableData = '';
          for (let i = 0; i < colHeaders.length; i++) {
            if (String(colHeaders[i]) !== 'Error_Details') {
              headerCol += `<th value=${colHeaders[i]}>${colHeaders[i]}</th>`;
            }
          }
          $(`#bulk_upload_in_progress_${elementID}`).removeClass('show');
          $("body").css("pointer-events", "auto")
          $(`#edit_upload_modal${elementID}`).modal('show');

          $(
						`#EditModalTab${elementID} a[href="#upload_error_tab${elementID}"]`
          ).tab('show');

          $(`#edit_upload_modal_datatable${elementID}` + '_wrapper').remove();
          $(`#edit_upload_modal_datatable${elementID}`).remove();

          $(`#upload_error_tab${elementID}`)
            .find('.error_validation_upload_card_content')
            .find('.error_validation_upload_content')
            .find(`#error_upload_modal_datatable${elementID}` + '_wrapper')
            .remove();
          $(`#upload_error_tab${elementID}`)
            .find('.error_validation_upload_card_content')
            .find('.error_validation_upload_content')
            .find(`#error_upload_modal_datatable${elementID}`)
            .remove();

          $('.error_summary_card').remove();

          // Store Original Data
          $(`#edit_upload_save${elementID}`).attr(
            'data-edit',
            storedUpdateData
          );

          if($(`#find_replace_${elementID}`).attr("data-final-index") == "") {
            $(`#find_replace_${elementID}`).attr("data-final-index", data.error_report_index)
          }
          // Edit Tab
          for (let i = 0; i < Object.keys(result).length; i++) {
            tableData += `<tr data-index=${Object.keys(result)[i]}>`;
            const room = Object.keys(result)[i];
            for (let y = 0; y < Object.keys(result[room]).length; y++) {
              if (String(Object.keys(result[room])[y]) !== 'Error_Details') {
                tableData += `<td data-key='${
									Object.keys(result[room])[y]
								}' style='text-align:center' contenteditable ">${
									result[room][Object.keys(result[room])[y]]
								}</td>`;
              }
            }
            tableData += '</tr>';
          }

          // Error Tab
          let validationTable = '';

          if (Object.prototype.hasOwnProperty.call(data, 'validation_list')) {
            const validationList = JSON.parse(data.validation_list);

            const navigationList = JSON.parse(data.navigation_list);

            for (const valName of validationList) {
              validationTable += `<tr><td>${Object.keys(valName)[0]}</td>`;
              for (let v = 0; v < colHeaders.length - 1; v++) {
                if (valName[Object.keys(valName)[0]].includes(colHeaders[v])) {
                  validationTable += `<td><i class='fa fa-window-close error_highlight' data-target-index='${JSON.stringify(
										navigationList[Object.keys(valName)[0]]
									)}' data-target-column='${
										colHeaders[v]
									}' style='color:red;cursor:pointer'></i></td>`;
                } else {
                  validationTable += `<td><i class='fa fa-check-circle'  data-target-column='${colHeaders[v]}' style='color:var(--primary-color);'></i></td>`;
                }
              }
              validationTable += '</tr>';
            }
          }

          // Count Table

          // Custom Validation Row

          let customValidationTable = '';
          if (
            Object.prototype.hasOwnProperty.call(data, 'custom_validation_list')
          ) {
            if (String(data.custom_validation_list) !== '{}') {
              const customValidationList = JSON.parse(
                data.custom_validation_list
              );

              for (const customKey in customValidationList) {
                customValidationTable += `<tr><td>${customKey}</td>`;

                for (let v = 0; v < colHeaders.length - 1; v++) {
                  if (
                    Object.keys(customValidationList[customKey]).includes(
                      colHeaders[v]
                    )
                  ) {
                    const dictBeta = {};

                    dictBeta[colHeaders[v]] =
											customValidationList[customKey][colHeaders[v]];
                    if (dictBeta[colHeaders[v]].length > 0) {
                      customValidationTable += `<td><i class='fa fa-window-close error_highlight' data-target-index='${JSON.stringify(
												dictBeta
											)}' data-target-column='${
												colHeaders[v]
											}' style='color:red;cursor:pointer'></i></td>`;
                    } else {
                      customValidationTable += `<td><i class='fa fa-check-circle'     data-target-column='${colHeaders[v]}' style='color:var(--primary-color);'></i></td>`;
                    }
                  } else {
                    customValidationTable += `<td><i class='fa fa-check-circle'     data-target-column='${colHeaders[v]}' style='color:var(--primary-color);'></i></td>`;
                  }
                }
                customValidationTable += '</tr>';
              }
            }
          }

          const customDatatable = `
            <table id="error_upload_modal_datatable${elementID}" class="row-border display table" style="width: 100%;">
            <thead class="error_upload_header">
              <th>Validation Type</th>
              ${headerCol}
            </thead>
            <tbody id="error_upload_content">
              ${validationTable}
              ${customValidationTable}
            </tbody>
            </table>`;
          $(`#upload_error_tab${elementID}`)
            .find('.error_validation_upload_card_content')
            .find('.card-body')
            .append(customDatatable);

          if (
            Object.prototype.hasOwnProperty.call(data, 'error_validation_count')
          ) {
            if (String(data.error_validation_count) !== '{}') {
              let errorCountHeader = '';
              let errorCountBody = '';
              const dropList = ['Error_Details', 'total_error_count'];
              const errorDict = JSON.parse(data.error_validation_count);

              for (let i = 0; i < colHeaders.length; i++) {
                if (String(colHeaders[i]) !== 'Error_Details') {
                  errorCountHeader += `<th value=${colHeaders[i]}> ${colHeaders[i]} </th>`;
                }
              }

              // Passed
              errorCountBody += "<tr><td style='font-weight:bold'>Passed</td>";
              for (const i in errorDict) {
                if (dropList.includes(i) === false) {
                  errorCountBody += `<td data-target-col='${errorDict[i]}'>${errorDict[i].Passed}</td>`;
                }
              }

              errorCountBody += '</tr>';

              // Failed
              errorCountBody += "<tr><td style='font-weight:bold'>Failed</td>";
              for (const i in errorDict) {
                if (dropList.includes(i) === false) {
                  errorCountBody += `<td data-target-col='${errorDict[i]}'>${errorDict[i].Failed}</td>`;
                }
              }
              errorCountBody += '</tr>';

              // Count Status Header

              $(`#upload_error_tab${elementID}`)
                .find('.error_validation_upload_card_content')
                .find('.card-body')
                .find(
									`#error_validation_count_modal_datatable${elementID}` +
										'_wrapper'
                )
                .remove();
              $(`#upload_error_tab${elementID}`)
                .find('.error_validation_upload_card_content')
                .find('.card-body')
                .find(`#error_validation_count_modal_datatable${elementID}`)
                .remove();

              const customcountDatatable = `

                <table id="error_validation_count_modal_datatable${elementID}" class="row-border display table" style="width: 100%;">

                <thead class="error_validation_count_header" >
                <th> Status </th>
                ${errorCountHeader}

                </thead>
                <tbody id="error_validation_count_content"  style="overflow-x: scroll;max-width: 200px;">
                ${errorCountBody}
                </tbody>
                </table>`;

              $(`#upload_error_tab${elementID}`)
                .find('.error_validation_upload_card_content')
                .find('.card-body')
                .append(customcountDatatable);
            }
          }

          // Function to Navigation and Highlight
          $(document).on('click', '.error_highlight', function () {
            $(
							`#EditModalTab${elementID} a[href="#edit_data_tab${elementID}"]`
            ).tab('show');

            const currentColumn = $(this).attr('data-target-column');
            const targetIndex = JSON.parse($(this).attr('data-target-index'));

            $(`#edit_upload_modal_datatable${elementID}`)
              .find('#edit_upload_content')
              .find('tr')
              .find('td')
              .css('background', 'white');
            for (let tag = 0; tag < Object.keys(targetIndex).length; tag++) {
              if (
                String(Object.keys(targetIndex)[tag]) === String(currentColumn)
              ) {
                for (
                  let inner = 0;
                  inner < targetIndex[Object.keys(targetIndex)[tag]].length;
                  inner++
                ) {
                  const targetColumn = colHeaders.indexOf(currentColumn);
                  $(`#edit_upload_modal_datatable${elementID}`)
                    .find('#edit_upload_content')
                    .find(
											`tr[data-index="${
												targetIndex[Object.keys(targetIndex)[tag]][inner]
											}"`
                    )
                    .find('td')
                    .eq(targetColumn)
                    .css('background', 'pink');
                }
              }
            }
            $(`#edit_upload_modal_datatable${elementID}`)
              .DataTable()
              .columns.adjust();
          });

          // Summary Table
          let summaryTable = '';
          if (Object.prototype.hasOwnProperty.call(data, 'error_details')) {
            summaryTable += '<ul>';
            const errorDetails = JSON.parse(data.error_details);

            for (let i = 0; i < errorDetails.length; i++) {
              summaryTable += `<li style='list-style-type: square;text-align: start;color:darkred'>${errorDetails[i]}</li><br>`;
            }
            summaryTable += '</ul><br>';
          }

          const customSummaryCard = `
            <table id="edit_upload_modal_datatable${elementID}" class="row-border display " style="width: 100%;">
                <thead class="edit_upload_header">
                  ${headerCol}
                </thead>
                <tbody id="edit_upload_content">
                  ${tableData}
                </tbody>
              </table>`;
                $(`#edit_data_tab${elementID}`).append(customSummaryCard);

                $(`#upload_error_tab${elementID}`)
                  .append(`<div class="card error_summary_card card-default collapsed-card" style="margin-top:10px;">
              <div class="card-header" style='background:#565a5e;'>
                <h6 class="card-title" style='color:white;'>Summary</h6>
                <div class="card-tools">
                  <button type="button" class="btn btn-tool" data-card-widget="collapse"><i class="fas fa-plus"></i></button>
                </div>
              </div>
              <div class="card-body validation_summary" style="max-height: 15rem;overflow-y:auto;">
                  ${summaryTable}
              </div>
            </div>`);
        }

        // DataTable Section

        $(`#error_validation_count_modal_datatable${elementID}`).DataTable({
          autoWidth: true,
          scrollY: 200,
          scrollX: 100,

          scrollCollapse: true,
          sScrollXInner: '100%',
          bInfo: false,
          searching: false,
          destroy: true,
          bRetrieve: true,
          bProcessing: true,
          bDestroy: true,
          ordering: false,
          orderCellsTop: true,
          responsive: true,

          colReorder: {
            fixedColumns: true,
          },

          deferRender: true,
          paging: false,
          lengthMenu: [
            [1, 5, 50, -1],
            [1, 5, 50, 'All'],
          ],
          pageLength: 50,
          buttons: [],
          columnDefs: [
            {
              width: '200px',
              targets: '_all',
              className: 'dt-center allColumnClass all',
            },
            {
              targets: 0,
              width: '2%',
              className: 'noVis',
            },
          ],
        });

        $(`#edit_upload_modal_datatable${elementID}`).DataTable({
          autoWidth: true,
          scrollY: 200,
          scrollX: 100,

          scrollCollapse: true,
          sScrollXInner: '100%',
          bInfo: false,
          searching: false,
          destroy: true,
          bRetrieve: true,
          bProcessing: true,
          bDestroy: true,
          ordering: false,
          orderCellsTop: true,
          responsive: true,

          colReorder: {
            fixedColumns: true,
          },

          deferRender: true,
          paging: false,
          lengthMenu: [
            [1, 5, 50, -1],
            [1, 5, 50, 'All'],
          ],
          pageLength: 50,
          buttons: [],
          columnDefs: [
            {
              width: '200px',
              targets: '_all',
              className: 'dt-center allColumnClass all',
            },
            {
              targets: 0,
              width: '2%',
              className: 'noVis',
            },
          ],
        });

        $(`#error_upload_modal_datatable${elementID}`).DataTable({
          autoWidth: true,
          scrollY: 200,
          scrollX: 200,
          scrollCollapse: true,
          sScrollXInner: '100%',
          bInfo: false,
          searching: false,
          destroy: true,
          bRetrieve: true,
          bProcessing: true,
          bDestroy: true,
          ordering: false,
          orderCellsTop: true,
          responsive: true,

          colReorder: {
            fixedColumns: true,
          },
          deferRender: true,
          paging: false,
          lengthMenu: [
            [1, 5, 50, -1],
            [1, 5, 50, 'All'],
          ],
          pageLength: 50,

          buttons: [],
          columnDefs: [
            {
              width: '200px',
              targets: '_all',
              className: 'dt-center allColumnClass all',
            },
            {
              targets: 0,
              width: '22%',
              className: 'noVis',
            },
          ],
        });

        $(`#EditModalTab${elementID}`).on('click', function () {
          setTimeout(function () {
            $(`#edit_upload_modal_datatable${elementID}`)
              .DataTable()
              .columns.adjust();
            $(`#error_upload_modal_datatable${elementID}`)
              .DataTable()
              .columns.adjust();
            $(`#error_validation_count_modal_datatable${elementID}`)
              .DataTable()
              .columns.adjust();
          }, 500);
        });

        $(`#edit_upload_modal_datatable${elementID}`)
          .DataTable()
          .columns.adjust();
        $(`#error_upload_modal_datatable${elementID}`)
          .DataTable()
          .columns.adjust();
        $(`#error_validation_count_modal_datatable${elementID}`)
          .DataTable()
          .columns.adjust();
      }
    },
    error: function () {
            $(`#bulk_upload_in_progress_${elementID}`).removeClass('show');
            $("body").css("pointer-events", "auto")
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    },
  });
}

//  Upload Mapper
// eslint-disable-next-line no-unused-vars
function uploadmapper () {
  const elementID = $(this).attr('data-elementID');

  $(`.columnconfiguremapper[data-elementid=${elementID}]`).prop(
    'disabled',
    true
  );

  $(`#Columnmapper${elementID}`).on('select2:select', function () {
    if ($(this).val() != null && $(`input[data-file-id=${elementID}]`).val()) {
      $(`.columnconfiguremapper[data-elementid=${elementID}]`).prop(
        'disabled',
        false
      );
      $(`.saveConfigMapper[data-elementid=${elementID}]`).prop(
        'disabled',
        false
      );
    }
  });
  let tableList = $(this).attr('data-table-name');
  if (tableList.startsWith('[')) {
    tableList = JSON.parse(tableList);
  }

  $(`#Columnmapper${elementID}`).select2();
  if (tableList.constructor === Array) {
    $(`#Columnmapper${elementID}`).empty();
    $(`#Columnmapper${elementID}`).append(
      "<option value='value'selected disabled>Select Option Name</option>"
    );
    for (let i = 0; i < tableList.length; i++) {
      $(`#Columnmapper${elementID}`).append(
        new Option(tableList[i], tableList[i])
      );
    }
  } else {
    $(`#Columnmapper${elementID}`).empty();
    $(`#Columnmapper${elementID}`).append(
      "<option value='value'selected disabled>Select Option Name</option>"
    );
    $(`#Columnmapper${elementID}`).append(new Option(tableList, tableList));
  }
  const firstTime = false;
  if ($(`#columnmapperDict${elementID}`).attr('data-edit')) {
    reloadConfigData(elementID, firstTime);
  } else {
    reloadConfigData(elementID, firstTime);
  }
}

// eslint-disable-next-line no-unused-vars
function columnMapper () {
  const elementID = $(this).attr('data-elementid');
  const dataForm = new FormData(
    $(`form[data-form-id=uploadfileform${elementID}]`)[0]
  );
  dataForm.append('operation', 'columnmapper_global');

  // eslint-disable-next-line prefer-const
  let tableName = $(this).parent().parent().find('select').val();
  dataForm.append('table_name', tableName);
  dataForm.append('elementID', elementID);
  const inputChecker = $(`form[data-form-id=uploadfileform${elementID}]`)
    .find('input[type=file]')
    .val();

  $('.saveConfigMapper').css('display', 'none');

  $.ajaxSetup({
    // eslint-disable-next-line no-unused-vars
    beforeSend: function (xhr, settings) {
      xhr.setRequestHeader('X-CSRFToken', ctoken);
    },
  });

  if (inputChecker) {
    $.ajax({
      url: `/users/${urlPath}/constriant_get_data/`,
      cache: false,
      contentType: false,
      processData: false,
      data: dataForm,
      type: 'POST',
      dataType: 'json',
      success: function (data) {
        $(`.submitconfigmapper[data-elementid=${elementID}]`).css(
          'display',
          'none'
        );

        $(`#modal-table-head${elementID}`).css('display', 'block');
        $(`#modal-table-head-done${elementID}`).css('display', 'none');
        $(`#modal-table-body-columnmapper${elementID}`).empty();

        // eslint-disable-next-line no-undef
        columnsql = data.columnlist;

        let counter = 0;
        for (const indDict of data.columnlist) {
          let html = '';
          html += `<th id="Columnmapper1${elementID}_${[
						counter,
					]}">${indDict}</th>`;
          html += `<td ><select id="Columnmapper${elementID}_${[
						counter,
					]}" class="select2 form-control" name="Columnmapper"  data-placeholder="Column Mapper" >

                    </select></td>`;
          $(`#modal-table-body-columnmapper${elementID}`).append(
            '<tr>' + html + '</tr>'
          );
          $(`#modal-table-body-columnmapper${elementID}`)
            .find('.select2')
            .select2({ width: '100%' });

          for (let i = 0; i < data.columnlist1.length; i++) {
            $(`#Columnmapper${elementID}_${[counter]}`).append(
              new Option(data.columnlist1[i], data.columnlist1[i])
            );
          }
          $(`#Columnmapper${elementID}_${[counter]}`)
            .val(indDict)
            .trigger('change');

          counter++;
        }

        $(`.savecolumnconfiguremapper[data-elementID=${elementID}]`).css(
          'display',
          'block'
        );
        $(`#columnmapperDict${elementID}`).attr('data-checker', true);
      },
      error: function () {
        Swal.fire({icon: 'error',text: 'Error! Please try again.'});
      },
    });
  } else {
    Swal.fire({icon: 'warning',text:"File not found" });
  }
}

var submitFinalData = []; // eslint-disable-line no-var
// eslint-disable-next-line no-unused-vars
function saveColumnMapper () {
  const elementID = $(this).attr('data-elementid');

  let finaldictcolumnmapper = [];

  const checkerDict = document
    .getElementById(`columnmapperDict${elementID}`)
    .getAttribute('data-save-config');

  if (checkerDict && String(checkerDict) !== '[]') {
    finaldictcolumnmapper = JSON.parse(checkerDict);
    for (let i = 0; i < finaldictcolumnmapper.length; i++) {
      const tm = Object.keys(finaldictcolumnmapper[i]);
      if (tm[0] === tableName) {
        const arrindex = finaldictcolumnmapper.indexOf(
          finaldictcolumnmapper[i]
        );
        finaldictcolumnmapper.splice(arrindex, 1);
      }
    }
  }
  const saveColumnDict = {};
  const columnmapperdict = [];
  const columnduplicatescheck = [];
  const duplicateChecker = [];

  for (let i = 0; i < columnsql.length; i++) {
    const columnmapperdict1 = {};
    const column2 = $(`#Columnmapper1${elementID}_${[i]}`).html();
    const column1 = $(`#Columnmapper${elementID}_${[i]}`).val();
    if (
      String(column1) !== 'undefined' &&
			column1 !== '' &&
			String(column1) !== 'null'
    ) {
      if (columnduplicatescheck.includes(column1)) {
        $(`#samecolumnwarning${elementID}`).html(
					`${[
						column1,
					]} is already assigned to another column, please reconfigure the column mapper.`
        );
        duplicateChecker.push(true);
        $('.saveConfigMapper').css('display', 'none');
      } else {
        columnduplicatescheck.push(column1);
        columnmapperdict1[column1] = column2;
        columnmapperdict.push(columnmapperdict1);
        duplicateChecker.push(false);
      }
    }
  }
  if (!duplicateChecker.includes(true)) {
    $(`#samecolumnwarning${elementID}`).empty();
    $(`#modal-table-body-columnmapper${elementID}`).empty();
    $(`#modal-table-head-done${elementID}`).css('display', 'block');
    $(`#modal-table-head-done${elementID}`).empty();

    let html1 = '';
    html1 +=
			'<th style="text-align: center;font-weight:bold"  disabled>Table Name</th>';
    html1 +=
			'<td style="text-align: center;font-weight:bold" disabled>Reconfigure</td>';
    html1 +=
			'<td style="text-align: center;font-weight:bold" disabled>Apply</td>';
    $(`#modal-table-body-columnmapper${elementID}`).append(
      '<tr>' + html1 + '</tr>'
    );

    let tableSavedList = document
      .getElementById(`columnmapperDict${elementID}`)
      .getAttribute('value');

    if (tableSavedList && String(tableSavedList) !== '[]') {
      tableSavedList = JSON.parse(tableSavedList);

      for (const tableKeys of tableSavedList) {
        if (String(Object.keys(tableKeys)[0]) !== tableName) {
          const tabName = Object.keys(tableKeys)[0];
          let html = '';
          html += `<th style="text-align: center;">${tabName}</th>`;
          html += `<td style="text-align: center;"><button type="button" class="btn-primary reconfigurecolumnmapper" name="${tabName}" id="reconfigurecolumnmapper_${tabName}"><i class="fas fa-trash"></i></button></td>`;
          html += `<td style="align-items: center;"><div class="custom-control custom-checkbox " style="margin-left:45%" >
              <input type="checkbox" class="applyConfig custom-control-input" name="${tabName}"  id=${
						tabName + elementID
					} data-elementid=${elementID} >
              <label for=${tabName + elementID} class="custom-control-label">
              </label>
                </div></td>`;
          $(`#modal-table-body-columnmapper${elementID}`).append(
            '<tr>' + html + '</tr>'
          );
        }
      }
    }

    let html = '';
    html += `<th style="text-align: center;">${[tableName]}</th>`;
    html += `<td style="text-align: center;"><button type="button" class="btn-primary reconfigurecolumnmapper" name="${[
			tableName,
		]}" id="reconfigurecolumnmapper_${[
			tableName,
		]}"><i class="fas fa-trash"></i></button></td>`;
    html += `<td style="align-items: center;"><div class="custom-control custom-checkbox " style="margin-left:45%" >

              <input type="checkbox" class="applyConfig custom-control-input" name="${[
								tableName,
							]}"  id=${[tableName] + elementID} data-elementid=${elementID} >
              <label for=${
								[tableName] + elementID
							} class="custom-control-label">
              </label>
            </div></td>`;
    $('input[type=checkbox]').prop('checked', false);
    $(`input[type=checkbox][name="${[tableName]}"]`).prop('checked', true);
    $(`#modal-table-body-columnmapper${elementID}`).append(
      '<tr>' + html + '</tr>'
    );
    saveColumnDict[tableName] = columnmapperdict;
    finaldictcolumnmapper.push(saveColumnDict);

    $('.applyConfig').change(function () {
      const applyName = $(this).attr('name');

      if ($(this).is(':checked')) {
        $('input[type=checkbox]').each(function () {
          if ($(this).attr('name') === applyName) {
            $(this).removeAttr('checked');
          } else {
            $(this).prop('checked', false);
          }
        });
      } else {
        $('input[type=checkbox]').each(function () {
          $('input[type=checkbox]').prop('checked', false);
          $(`#columnmapperDict${elementID}`).attr('value', '[]');
        });
      }
    });

    $('.reconfigurecolumnmapper').click(function () {
      $(`#samecolumnwarning${elementID}`).empty();
      const tmname = $(this).attr('name');
      $(`#Columnmapper${elementID}`)
        .find(`option[value='${tmname}']`)
        .removeAttr('disabled');
      $(this).closest('tr').remove();
      for (let i = 0; i < finaldictcolumnmapper.length; i++) {
        const tm = Object.keys(finaldictcolumnmapper[i]);
        if (String(tm[0]) === String(tmname)) {
          const arrindex = finaldictcolumnmapper.indexOf(
            finaldictcolumnmapper[i]
          );
          finaldictcolumnmapper.splice(arrindex, 1);
          $(`#columnmapperDict${elementID}`).attr(
            'data-save-config',
            JSON.stringify(finaldictcolumnmapper)
          );
        }
      }
      $(`#columnmapperDict${elementID}`).attr('data-edit', 'true');
    });
    $(this).css('display', 'none');
    $('.saveConfigMapper').css('display', 'block');
    $(`.submitconfigmapper[data-elementid=${elementID}]`).css(
      'display',
      'block'
    );
    $(`#columnmapperDict${elementID}`).attr(
      'data-save-config',
      JSON.stringify(finaldictcolumnmapper)
    );
    $(`#columnmapperDict${elementID}`).attr('data-edit', 'true');
    $(`.saveConfigMapper[data-elementid=${elementID}]`).prop('disabled', false);
    submitFinalData = finaldictcolumnmapper;
  } else {
    $('.saveConfigMapper').css('display', 'none');
  }
}

var finaldictcolumnmapperReload = []; // eslint-disable-line no-var
var reloadChecker = ''; // eslint-disable-line no-var
function reloadConfigData (elementID, firstTime) {
  $.ajax({
    url: `/users/${urlPath}/constriant_get_data/`,
    data: {
      elementID: elementID,
      operation: 'reload_config_mapper',
    },
    type: 'POST',
    dataType: 'json',
    success: function (data) {
      if (data.reload_data && firstTime === true) {
        finaldictcolumnmapperReload = JSON.parse(data.reload_data);
        $(`#samecolumnwarning${elementID}`).empty();
        $(`#modal-table-body-columnmapper${elementID}`).empty();
        $(`#modal-table-head-done${elementID}`).css('display', 'block');
        $(`#modal-table-head-done${elementID}`).empty();
        let html1 = '';
        html1 +=
					'<th style="text-align: center;font-weight:bold" disabled>Table Name</th>';
        html1 +=
					'<td style="text-align: center;font-weight:bold" disabled>Reconfigure</td>';
        html1 +=
					'<td style="text-align: center;font-weight:bold" disabled>Apply</td>';
        $(`#modal-table-body-columnmapper${elementID}`).append(
          '<tr>' + html1 + '</tr>'
        );
        for (const tableNamer of finaldictcolumnmapperReload) {
          let html = '';
          html += `<th style="text-align: center;">${
						Object.keys(tableNamer)[0]
					}</th>`;
          html += `<td style="text-align: center;"><button type="button" class="btn-primary reconfigurecolumnmapper" name="${
						Object.keys(tableNamer)[0]
					}" id="reconfigurecolumnmapper_${
						Object.keys(tableNamer)[0]
					}"><i class="fas fa-trash"></i></button></td>`;
          html += `<td style="align-items: center;"><div class="custom-control custom-checkbox " style="margin-left:45%" >
                   <input type="checkbox" class="applyConfig custom-control-input" name="${
											Object.keys(tableNamer)[0]
										}"  id=${
						Object.keys(tableNamer)[0] + elementID
					} data-elementid=${elementID} >
                   <label for=${
											Object.keys(tableNamer)[0] + elementID
										} class="custom-control-label">
                   </label>
                 </div></td>`;
          $(`#modal-table-body-columnmapper${elementID}`).append(
            '<tr>' + html + '</tr>'
          );
        }
        if (reloadChecker) {
          $(`input[type=checkbox][name=${reloadChecker}]`).prop(
            'checked',
            true
          );
        }

        $('.reconfigurecolumnmapper').click(function () {
          $(`#samecolumnwarning${elementID}`).empty();
          const tmname = $(this).attr('name');
          $(`#Columnmapper${elementID}`)
            .find(`option[value='${tmname}']`)
            .removeAttr('disabled');
          $(this).closest('tr').remove();
          for (let i = 0; i < finaldictcolumnmapperReload.length; i++) {
            const tm = Object.keys(finaldictcolumnmapperReload[i]);
            if (tm[0] === tmname) {
              const arrindex = finaldictcolumnmapperReload.indexOf(
                finaldictcolumnmapperReload[i]
              );
              finaldictcolumnmapperReload.splice(arrindex, 1);
              $(`#columnmapperDict${elementID}`).attr('value', '[]');
              $(`#columnmapperDict${elementID}`).attr(
                'data-save-config',
                JSON.stringify(finaldictcolumnmapperReload)
              );
            }
          }
          $(`.columnconfiguremapper[data-elementid=${elementID}]`).prop(
            'disabled',
            false
          );
          $(`.saveConfigMapper[data-elementid=${elementID}]`).prop(
            'disabled',
            false
          );
          $(`.loadConfigMapper[data-elementid=${elementID}]`).prop(
            'disabled',
            false
          );
        });

        $('.applyConfig').change(function () {
          const applyName = $(this).attr('name');
          reloadChecker = applyName;
          if ($(this).is(':checked')) {
            $('input[type=checkbox]').each(function () {
              if ($(this).attr('name') === applyName) {
                $(this).removeAttr('checked');
                $(`.submitconfigmapper[data-elementid=${elementID}]`).css(
                  'display',
                  'block'
                );
              } else {
                $(this).prop('checked', false);
              }
            });
          } else {
            $('input[type=checkbox]').each(function () {
              $('input[type=checkbox]').prop('checked', false);
              $(`#columnmapperDict${elementID}`).attr('value', '[]');
            });
          }
        });
        $(`#columnmapperDict${elementID}`).attr('data-has-reloaded', 'true');
      }
    },
    error: function () {
      Swal.fire({icon: 'error',text: 'Error! Failure in saving configuration. Please check your configuration and try again.'});
    },
  });
}

// eslint-disable-next-line no-unused-vars
function saveConfigMapper (elementID) {
  const oldDataLoad = finaldictcolumnmapperReload;
  const newDataLoad = JSON.parse(
    $(`#columnmapperDict${elementID}`).attr('data-save-config')
  );

  for (const j of newDataLoad) {
    for (let i = 0; i < oldDataLoad.length; i++) {
      const tm = Object.keys(oldDataLoad[i]);
      if (String(tm[0]) === String(Object.keys(j)[0])) {
        const arrindex = oldDataLoad.indexOf(oldDataLoad[i]);
        oldDataLoad.splice(arrindex, 1);
      }
    }
  }
  if (oldDataLoad.length > 0) {
    for (const i of oldDataLoad) {
      newDataLoad.push(i);
    }
  }

  $.ajax({
    url: `/users/${urlPath}/constriant_get_data/`,
    data: {
      elementID: elementID,
      mapper_data: JSON.stringify(newDataLoad),
      operation: 'save_config_mapper',
    },
    type: 'POST',
    dataType: 'json',
    // eslint-disable-next-line no-unused-vars
    success: function (data) {

      Swal.fire({icon: 'success', text: 'Configuration saved successfully!'});

    },
    error: function () {
      Swal.fire({icon: 'error',text: 'Error! Failure in saving configuration. Please check your configuration and try again.'});
    },
  });
}

// eslint-disable-next-line no-unused-vars
function SubmitConfigmapper () {
  const elementID = $(this).attr('data-elementid');
  const finalTableName = $(
		`input[type=checkbox][data-elementid=${elementID}]:checked`
  ).attr('name');
  if (finalTableName) {
    if (submitFinalData.length > 0) {
      for (let i = 0; i < submitFinalData.length; i++) {
        const tm = Object.keys(submitFinalData[i]);
        if (String(tm[0]) === String(finalTableName)) {
          $(`#columnmapperDict${elementID}`).attr(
            'value',
            JSON.stringify([submitFinalData[i]])
          );
        } else {
          for (let i = 0; i < finaldictcolumnmapperReload.length; i++) {
            const tm = Object.keys(finaldictcolumnmapperReload[i]);
            if (String(tm[0]) === String(finalTableName)) {
              $(`#columnmapperDict${elementID}`).attr(
                'value',
                JSON.stringify([finaldictcolumnmapperReload[i]])
              );
            }
          }
        }
      }
      Swal.fire({icon: 'success',text: 'Mapper configuration submitted successfully!'});
      $(`#columnMapperModal${elementID}`).modal('hide');
    } else {
      for (let i = 0; i < finaldictcolumnmapperReload.length; i++) {
        const tm = Object.keys(finaldictcolumnmapperReload[i]);
        if (String(tm[0]) === String(finalTableName)) {
          $(`#columnmapperDict${elementID}`).attr(
            'value',
            JSON.stringify([finaldictcolumnmapperReload[i]])
          );
        }
      }
      Swal.fire({icon: 'success',text: 'Mapper configuration submitted successfully!'});
      $(`#columnMapperModal${elementID}`).modal('hide');
    }
  } else {
    Swal.fire({icon: 'warning',text:"Select the Table Name." });
  }
}

// eslint-disable-next-line no-unused-vars
function loadConfigMapper () {
  const elementID = $(this).attr('data-elementid');
  const dataForm = new FormData(
    $(`form[data-form-id=uploadfileform${elementID}]`)[0]
  );
  dataForm.append('operation', 'columnmapper_global');
  tableName = $(
		`input[type=checkbox][data-elementid=${elementID}]:checked`
  ).attr('name');
  if (String(tableName) === 'null' || String(tableName) === 'undefined') {
    tableName = $('select').val();
  }

  dataForm.append('table_name', tableName);
  dataForm.append('elementID', elementID);
  const inputChecker = $(`form[data-form-id=uploadfileform${elementID}]`)
    .find('input[type=file]')
    .val();
  if (tableName && inputChecker) {
    $(`.submitconfigmapper[data-elementid=${elementID}]`).css(
      'display',
      'none'
    );
    $.ajax({
      url: `/users/${urlPath}/constriant_get_data/`,
      cache: false,
      contentType: false,
      processData: false,
      data: dataForm,
      type: 'POST',
      dataType: 'json',
      success: function (data) {
        if (data.saved_data) {
          if (data.saved_data.length > 0) {
            $(`#columnmapperDict${elementID}`).attr(
              'value',
              JSON.stringify(data.saved_data)
            );
          }
        }
        for (const save1 of data.saved_data) {
          if (String(tableName) === String(Object.keys(save1)[0])) {
            $('.saveConfigMapper').css('display', 'none');
            $(`#modal-table-head${elementID}`).css('display', 'block');
            $(`#modal-table-head-done${elementID}`).css('display', 'none');
            $(`#modal-table-body-columnmapper${elementID}`).empty();

            columnsql = data.columnlist;

            let counter = 0;
            for (const indDict of data.columnlist) {
              let html = '';
              html += `<th id="Columnmapper1${elementID}_${[
								counter,
							]}">${indDict}</th>`;
              html += `<td ><select id="Columnmapper${elementID}_${[
								counter,
							]}" data-reload-value='${indDict}' class="select2 form-control" name="Columnmapper"  data-placeholder="Column Mapper" >
                    </select></td>`;
              $(`#modal-table-body-columnmapper${elementID}`).append(
                '<tr>' + html + '</tr>'
              );
              $(`#modal-table-body-columnmapper${elementID}`)
                .find('.select2')
                .select2({ width: '100%' });

              for (let i = 0; i < data.columnlist1.length; i++) {
                $(`#Columnmapper${elementID}_${[counter]}`).append(
                  new Option(data.columnlist1[i], data.columnlist1[i])
                );
              }
              $(`#Columnmapper${elementID}_${[counter]}`)
                .val(indDict)
                .trigger('change');
              counter++;
            }
            for (const save2 of save1[tableName]) {
              $(`select[data-reload-value=${Object.values(save2)[0]}]`)
                .val(Object.keys(save2)[0])
                .trigger('change');
            }
            $(`.savecolumnconfiguremapper[data-elementID=${elementID}]`).css(
              'display',
              'block'
            );
          }
        }
      },
      error: function () {
        Swal.fire({icon: 'error',text: 'Error! Please try again.'});
      },
    });
  } else {
    Swal.fire({icon: 'warning',text:"No Table selected / File not found." });
  }
}
// Upload Mapper Ends

// Table Generator
// eslint-disable-next-line no-unused-vars
function generateTable (elementID) {
  const row_data = $(
		`textarea[name=excel_data_table_generator2][data-element-id=${elementID}]`
  ).val();
  var doc = new DOMParser().parseFromString(row_data, 'text/html');
  let data = doc.body.textContent || ""
  var validateString = data.replaceAll('"', '').replaceAll(" ", "").replaceAll("\n", "");
  if (!validateString) {
    data = "";
  }

  const rows = data.split('\n');
  const cells = rows[0].split('\t');
  let theadrow = '';
  for (const x in cells) {
    theadrow += `<th>${cells[x]}</th>`;
  }
  rows.shift();
  let htmlRow = '';
  for (const y in rows) {
    if (rows[y]) {
      const cells = rows[y].split('\t');

      htmlRow += '<tr>';
      for (const x in cells) {
        htmlRow += `<td contenteditable>${cells[x]}</td>`;
      }
      htmlRow += '</tr>';
    }
  }
  $(`#save_generated_table_${elementID}` + '_wrapper').remove();
  $(`#save_generated_table_${elementID}`).remove();
  $(document).find(`#savetablegenerator_${elementID}`).prop('disabled', false);
  const customTable = `
<table id="save_generated_table_${elementID}"  class="row-border display" style="display: none;">
<thead class="table_generator_header">
${theadrow}
</thead>
<tbody id='save_generated_table_body_${elementID}'>
${htmlRow}
</tbody>
</table>`;
  $(`#result_table_generated_${elementID}`).append(customTable);

  $(`#result_table_generated_${elementID}`).css('display', 'block');
  $(`#save_generated_table_${elementID}`).css('display', 'block');

  $(`#save_generated_table_${elementID}`).DataTable({
    autoWidth: true,
    scrollY: 200,
    scrollX: 200,
    scrollCollapse: true,
    sScrollXInner: '100%',
    bInfo: false,
    searching: true,
    destroy: true,
    bRetrieve: true,
    bProcessing: true,
    bDestroy: true,
    ordering: false,
    orderCellsTop: true,
    responsive: true,

    colReorder: {
      fixedColumns: true,
    },
    deferRender: true,
    paging: false,
    lengthMenu: [
      [1, 5, 50, -1],
      [1, 5, 50, 'All'],
    ],
    pageLength: 50,

    buttons: [],
    columnDefs: [
      {
        width: '200px',
        targets: '_all',
        className: 'dt-center allColumnClass all',
      },
      {
        targets: 0,
        width: '22%',
        className: 'noVis',
      },
    ],
  });
  setTimeout(function () {
    $(`#save_generated_table_${elementID}`).DataTable().columns.adjust();
  }, 1000);
}

// eslint-disable-next-line no-unused-vars
function savegeneratorData (elementID,prCode) {
  const modelName = $(`#savetablegenerator_${elementID}`).attr(
    'data-current-table'
  );
  const dataList = [];
  const itemCode = prCode;

  $(`#save_generated_table_${elementID} tbody tr`).each(function () {
    const dataDict = {};
    $(this)
      .find('td')
      .each(function () {
        const indexVal = $(this).index();
        const colName = $(this)
          .closest('table')
          .find('thead')
          .find('th')
          .eq(indexVal)
          .text()
          .trim();

        dataDict[colName] = $(this).text();
      });
    dataList.push(dataDict);
  });

  $.ajax({
    url: `/users/${urlPath}/${itemCode}/`,
    data: {
      model_name: modelName,
      table_data: JSON.stringify(dataList),
      element_id: elementID,
      operation: 'save_tablegenerator_data',
    },
    type: 'POST',
    dataType: 'json',
    // eslint-disable-next-line no-unused-vars
    success: function (data) {
      windowLocationAttr.reload();
    },
    error: function () {
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    },
  });
}

// Refresh table generator textarea
// eslint-disable-next-line no-unused-vars
function refreshTablegenerator (elementID) {
  $(`textarea[name=excel_data_table_generator2][data-element-id=${elementID}]`)
    .val(' ')
    .trigger('change');
  $(`#save_generated_table_${elementID}`).css('display', 'none');
  $(`#result_table_generated_${elementID}`).css('display', 'none');
  $(`save_generated_table_body_${elementID}`).empty();
}

// Preview Upload Elememt Data
// eslint-disable-next-line no-unused-vars
function previewUploadElementData (elementID, dataForm) {
  $(`#previewUploadModal${elementID}`).modal('show');
  $(`#previewUploadBody${elementID}`).empty();
  $(`#previewUpload_unknownsheet${elementID}`).remove();
  const itemCode = windowLocation.split('/')[4];
  dataForm.append('operation', 'previewUploadData');

  $.ajax({
    url: `/users/${urlPath}/${itemCode}/`,
    data: dataForm,
    contentType: false,
    cache: false,
    async: false,
    processData: false,
    type: 'POST',
    dataType: 'json',
    success: function (data) {
      const context = JSON.parse(data.context);
      if (context.length > 0) {
        for (const tab of context) {
          $(`#previewUploadBody${elementID}`).append(tab);
        }
      }

      // For XLSX
      if (Object.prototype.hasOwnProperty.call(data, 'unknown_sheet')) {
        const unknownSheet = JSON.parse(data.unknown_sheet);
        if (unknownSheet.length > 0) {
          $(
						`<div id='previewUpload_unknownsheet${elementID}' ><ul><li style="color:red;text-align: justify;"><h6>Sheet ${unknownSheet.join(
							', '
						)} does not exist.</h6></li></ul></div>`
          ).insertBefore(`#previewUpload_footer${elementID}`);
        }
      }

      $('table.previewUploadTable').DataTable({
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
      });

      $(document)
        .find('.cardUploadtoggle')
        .on('click', function () {
          setTimeout(function () {
            $('table.previewUploadTable').DataTable().columns.adjust();
          }, 300);
        });
    },
    error: function () {
      Swal.fire({icon: 'error',text: 'Error! Failure in displaying data. Please try again.'});
    },
  });
}

function CompMapper (This) {
  let elementID = $(This).attr("data-elementID")
  let tableList = $(This).attr("data-table-name")
  let tList = []
  let uni = $('a[data-toggle="tab"].active.l3items').find('span').eq(0).text()

  $.ajax({
    url: `/users/${urlPath}/processGraphModule/`,
    data: {
            element_id: elementID,
            operation: 'get_fields_comp_upload'
          },
    type: 'POST',
    dataType: 'json',
    success: function (data) {

      tList = Object.keys(data.tablelist)
      $(`#modal-table-body-computedFieldMapper_main_table_${elementID}`).empty()

      if(Object.keys(data).length > 0){

        for(let [key,value] of Object.entries(data.tablelist) ){

        $(`#modal-table-body-computedFieldMapper_main_table_${elementID}`).append(
          `
          <tr>
            <td style="text-align:center;" class="${key}_table_${elementID}">
                ${key}
            </td>
            <td style="text-align:center;">
                <span>
                <a data-toggle="tooltip" class="delete_actions_upload_eq" title="Delete" value="eq" id="delete_${key}_EBDisplayButtonID_${elementID}"><i name="actions1" value="eq" class="far fa-trash-alt ihover javaSC thin-icontrash" style="font-size: 18px;"></i></a>
              </span>
            </td>
            <td style="align-items: center;">
                <div class="custom-control custom-checkbox" style="margin-left:45%">
                <input type="checkbox" id="everyrun_${key}_${elementID}" data-elementID="${elementID}" name="everyrun_${key}_${elementID}" class="checkboxinput custom-control-input" value="new">
                <label for="everyrun_${key}_${elementID}" class="custom-control-label"></label>
              </div>
            </td>
          </tr>
          `
        )

        if(value){
          $(`#everyrun_${key}_${elementID}`).prop('checked', true);
        }
      }

      }

    },
    error: function () {
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    },
  });

  if (tableList.startsWith('[')) {
    tableList = JSON.parse(tableList);
  }

  $(`#computedFieldMapper_table_${elementID}`).select2();
  if (tableList.constructor === Array) {
    $(`#computedFieldMapper_table_${elementID}`).empty();
    $(`#computedFieldMapper_table_${elementID}`).append(
      "<option value='value'selected disabled>Select Table</option>"
    );
    for (let i = 0; i < tableList.length; i++) {
      $(`#computedFieldMapper_table_${elementID}`).append(
        new Option(tableList[i], tableList[i])
      );
    }
  } else {
    $(`#computedFieldMapper_table_${elementID}`).empty();
    $(`#computedFieldMapper_table_${elementID}`).append(
      "<option value='value'selected disabled>Select Table</option>"
    );
    $(`#computedFieldMapper_table_${elementID}`).append(new Option(tableList, tableList));
  }


  $(`#FieldMapper_EBDisplayButtonID_${elementID}`).off("click").on("click",function(){
    listViewComp = true
    listViewModelName = $(`#computedFieldMapper_table_${elementID}`).val()
    listViewCompCol = elementID
    $("#EBDisplayModel").css('z-index',1051)
    $("#EBDisplayModel").modal("show")
    reloadCompConfig(listViewModelName+"_devcomp_"+uni)
  })

  $('#EBDisplayModel').off('hide.bs.modal').on('hide.bs.modal', function() {
    listViewComp = false
    $("#EBDisplayModel").css('z-index',1050)
    $("#where_condition").css("display","block")
    $("#export_data_equ").css("display","block")


    let config = {}

    $(`#modal-table-body-computedFieldMapper_main_table_${elementID}`).find('tr').each(function() {
        name_t = $(this).find('td').eq(0).text().trim()
        if (name_t != undefined){
          config[name_t] = $(`#everyrun_${name_t}_${elementID}`).is(':checked')
        }
    })

    $(`#modal-table-body-computedFieldMapper_main_table_${elementID}`).empty()

    let tab_list = []
    tab_list = Object.keys(config)

    tab_list.push($(`#computedFieldMapper_table_${elementID}`).val())
    tab_list = new Set(tab_list);
    tab_list = Array.from(tab_list);

    for(let i=0;i<tab_list.length;i++){
    $.ajax({
      url: `/users/${urlPath}/processGraphModule/`,
      data: {
              element_id: tab_list[i]+"_devcomp_"+uni,
              operation: 'get_fields_comp_upload2'
            },
      type: 'POST',
      dataType: 'json',
      success: function (data) {

        tList = Object.keys(data.tablelist)

        let bk_config = {}

        for(let i=0;i<tList.length;i++){
          tList[i] = tList[i].replace("_devcomp","").replace(`_${uni}`,"")
          bk_config[tList[i]] = $(`#everyrun_${tList[i]}_${elementID}`).is(':checked')
        }

        if(Object.keys(data).length > 0){

          for(let [key,value] of Object.entries(data.tablelist) ){

          $(`#modal-table-body-computedFieldMapper_main_table_${elementID}`).append(
            `
            <tr>
              <td style="text-align:center;" class="${key.replace("_devcomp","").replace(`_${uni}`,"")}_table_${elementID}">
                  ${key.replace("_devcomp","").replace(`_${uni}`,"")}
              </td>
              <td style="text-align:center;">
                  <span>
                  <a data-toggle="tooltip" class="delete_actions_upload_eq" title="Delete" value="eq" id="delete_${key.replace("_devcomp","").replace(`_${uni}`,"")}_EBDisplayButtonID_${elementID}"><i name="actions1" value="eq" class="far fa-trash-alt ihover javaSC thin-icontrash" style="font-size: 18px;"></i></a>
                </span>
              </td>
              <td style="align-items: center;">
                  <div class="custom-control custom-checkbox" style="margin-left:45%">
                  <input type="checkbox" id="everyrun_${key.replace("_devcomp","").replace(`_${uni}`,"")}_${elementID}" data-elementID="${elementID}" name="everyrun_${key.replace("_devcomp","").replace(`_${uni}`,"")}_${elementID}" class="checkboxinput custom-control-input" value="new">
                  <label for="everyrun_${key.replace("_devcomp","").replace(`_${uni}`,"")}_${elementID}" class="custom-control-label"></label>
                </div>
              </td>
            </tr>
            `
          )

          if(value){
            $(`#everyrun_${key.replace("_devcomp","").replace(`_${uni}`,"")}_${elementID}`).prop('checked', true);
          }
        }

        }

        if(Object.keys(config).length > 0){

          for(let [key,value] of Object.entries(config) ){
            if(value){
              $(`#everyrun_${key.replace("_devcomp","").replace(`_${uni}`,"")}_${elementID}`).prop('checked', true);
            }
          }

        }


      },
      error: function () {
        Swal.fire({icon: 'error',text: 'Error! Please try again.'});
      },
    });
  }

  })

  $('#EBDisplayModel').on('show.bs.modal', function() {

    $("#where_condition").css("display","none")
    $("#export_data_equ").css("display","none")
    $('#functionsList').find('div').find('a').attr('data-element_comp','datamgm')

  })

  $('#save_workflow_equ').off("click").on("click",function(){

    SaveCompFlow(listViewModelName+"_devcomp_"+uni)

  });

  $(`#savecomputedFieldMapper_button_${elementID}`).off("click").on("click", function () {

    let config = {}

    $(`#modal-table-body-computedFieldMapper_main_table_${elementID}`).find('tr').each(function() {
      name_t = $(this).find('td').eq(0).text().trim()
      config[name_t] = $(`#everyrun_${name_t}_${elementID}`).is(':checked')
    })

    $.ajax({
      url: `/users/${urlPath}/processGraphModule/`,
      data: {
              element_id: elementID,
              operation: 'save_fields_comp_upload',
              data:JSON.stringify(config),
            },
      type: 'POST',
      dataType: 'json',
      success: function (data) {

        $.ajax({
          url: `/users/${urlPath}/dynamicVal/`,

          data:
          {
            'operation': 'fetch_upload_view_custom_messages',
            'element_id':  elementID,
            'messages' : JSON.stringify(["computation_configured_message"]),
          },
          type: "POST",
          dataType: "json",
          success: function (response) {
            message=""
            icon=""
            if(response.computation_configured_message){
              message = response.computation_configured_message.message
              icon = response.computation_configured_message.icon
            }

            iconHtml = ""
            if (icon){
              iconHtml = `<i class="${icon}" style="border: 0 !important;"></i>`
            }

            Swal.fire({icon: 'success', iconHtml, text: message || 'Configuration saved successfully!'}).then((result) => {
              if (result.isConfirmed) {
                windowLocationAttr.reload();
              };
            });
          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          }
        })

      },
      error: function () {
        Swal.fire({icon: 'error',text: 'Error! Failure in saving configuration. Please check your configuration and try again.'});
      },
    });

  })

  $(document).on('click', '.delete_actions_upload_eq', function (event) {
    event.stopImmediatePropagation()
    let id = $(this).attr("id")
    let tableName = id.replace("delete_","").replace(`_EBDisplayButtonID_${elementID}`,"")

    const confirmDelete = window.confirm("Remove the computation logic ?")

    if(confirmDelete){

      $.ajax({
        url: `/users/${urlPath}/processGraphModule/`,
        data: {
          'tablename': tableName+"_devcomp_"+uni,
          'element_id': elementID,
          'operation': "removeCompCal"
        },
        type: "POST",
        dataType: "json",
        success: function () {

          $.ajax({
            url: `/users/${urlPath}/processGraphModule/`,
            data: {
                    element_id: elementID,
                    operation: 'get_fields_comp_upload'
                  },
            type: 'POST',
            dataType: 'json',
            success: function (data) {

              tList = Object.keys(data.tablelist)
              $(`#modal-table-body-computedFieldMapper_main_table_${elementID}`).empty()

              if(Object.keys(data).length > 0){

                for(let [key,value] of Object.entries(data.tablelist) ){

                $(`#modal-table-body-computedFieldMapper_main_table_${elementID}`).append(
                  `
                  <tr>
                    <td style="text-align:center;" class="${key}_table_${elementID}">
                        ${key}
                    </td>
                    <td style="text-align:center;">
                        <span>
                        <a data-toggle="tooltip" class="delete_actions_upload_eq" title="Delete" value="eq" id="delete_${key}_EBDisplayButtonID_${elementID}"><i name="actions1" value="eq" class="far fa-trash-alt ihover javaSC thin-icontrash" style="font-size: 18px;"></i></a>
                      </span>
                    </td>
                    <td style="align-items: center;">
                        <div class="custom-control custom-checkbox" style="margin-left:45%">
                        <input type="checkbox" id="everyrun_${key}_${elementID}" data-elementID="${elementID}" name="everyrun_${key}_${elementID}" class="checkboxinput custom-control-input" value="new">
                        <label for="everyrun_${key}_${elementID}" class="custom-control-label"></label>
                      </div>
                    </td>
                  </tr>
                  `
                )

                if(value){
                  $(`#everyrun_${key}_${elementID}`).prop('checked', true);
                }
              }

              }

            },
            error: function () {
              Swal.fire({icon: 'error',text: 'Error! Please try again.'});
            },
          });

        },
        error: function () {
          Swal.fire({icon: 'error',text: 'Error! Please try again.'});
        }
      });

    }

  })

}

function fetchColVals(){

    col = $(this).parent().parent().parent().find('.master_column_vals')
    col_index = $(this).parent().parent().parent().index()
    elementID = $(this).parent().parent().parent().parent().attr("id").replace("custom_validation_table_","")

    reload_data = $(this).attr("data-data")
    if(reload_data == undefined){
      reload_data = ""
    }

    $.ajax({
        url: `/users/${urlPath}/processGraphModule/`,
        data: {
          'tablename': $(this).val(),
          'col_index': col_index,
          'elementID': elementID,
          'reload_data':reload_data,
          'operation': "fetchcols"
        },
        type: "POST",
        dataType: "json",
        success: function (data) {

          $(`#custom_validation_table_${data.elementID} tr`).eq(data.col_index).find('td').eq(4).find('div').find('select').empty()
          $(`#custom_validation_table_${data.elementID} tr`).eq(data.col_index).find('td').eq(4).find('div').find('select').append(`<option value ="" selected disabled>Column</option>`)
          for (const [key, value] of Object.entries(data.data)) {
            $(`#custom_validation_table_${data.elementID} tr`).eq(data.col_index).find('td').eq(4).find('div').find('select').append(`<option value = "${key}">${value}</option>`)
          }

          $(`#custom_validation_table_${data.elementID} tr`).eq(data.col_index).find('td').eq(4).find('div').find('select').val(data.reload_data).trigger('change');

        },
        error:function () {
          Swal.fire({icon: 'error',text: 'Error! Please try again.'});
        }
    })

}


function CompMapperDev (This) {
  $("#documentModal").modal("hide")
  let tableList = $("#selectDocumentTable").val()
  let tList = []
  let uni = $('#tabHeaderDocument').val()

  $("#computedFieldMapper_table").val("").trigger("change")
  $(`#modal-table-body-computedFieldMapper_main_table`).empty()

  let reload_data = $(".computedFieldMapperButton").attr("data-data_config")
  if(reload_data != undefined){
    reload_data = JSON.parse(reload_data)
    reload_data = {"tablelist": reload_data}
  }else{
    reload_data = {"tablelist": {}}
  }

    tList = Object.keys(reload_data.tablelist)
    $('#modal-table-body-computedFieldMapper_main_table').empty()

    if(Object.keys(reload_data).length > 0){

      for(let [key,value] of Object.entries(reload_data.tablelist) ){

      $(`#modal-table-body-computedFieldMapper_main_table`).append(
        `
        <tr>
          <td style="text-align:center;" class="${key}_table">
              ${key}
          </td>
          <td style="text-align:center;">
              <span>
              <a data-toggle="tooltip" class="delete_actions_upload_eq" title="Delete" value="eq" id="delete_${key}_EBDisplayButtonID_${uni}"><i name="actions1" value="eq" class="far fa-trash-alt ihover javaSC thin-icontrash" style="font-size: 18px;"></i></a>
            </span>
          </td>
          <td style="align-items: center;">
              <div class="custom-control custom-checkbox" style="margin-left:45%">
              <input type="checkbox" id="everyrun_${key}" data-elementID="" name="everyrun_${key}" class="checkboxinput custom-control-input" value="new">
              <label for="everyrun_${key}" class="custom-control-label"></label>
            </div>
          </td>
        </tr>
        `
      )

      if(value){
        $(`#everyrun_${key}`).prop('checked', true);
      }
    }

    }

  $(`#computedFieldMapper_table`).select2();
  if (tableList.constructor === Array) {
    $(`#computedFieldMapper_table`).empty();
    $(`#computedFieldMapper_table`).append(
      "<option value='value'selected disabled>Select Table</option>"
    );
    for (let i = 0; i < tableList.length; i++) {
      $(`#computedFieldMapper_table`).append(
        new Option(tableList[i], tableList[i])
      );
    }
  } else {
    $(`#computedFieldMapper_table`).empty();
    $(`#computedFieldMapper_table`).append(
      "<option value='value'selected disabled>Select Table</option>"
    );
    $(`#computedFieldMapper_table`).append(new Option(tableList, tableList));
  }


  $(`#FieldMapper_EBDisplayButtonID`).off("click").on("click",function(){
    listViewComp = true
    listViewModelName = $(`#computedFieldMapper_table`).val()
    listViewCompCol = "document"
    $("#EBDisplayModel").css('z-index',1051)
    $("#EBDisplayModel").modal("show")
    reloadCompConfig(listViewModelName+"_devcomp_"+uni)
  })

  $('#EBDisplayModel').off('hide.bs.modal').on('hide.bs.modal', function() {
    listViewComp = false
    $("#EBDisplayModel").css('z-index',1050)
    $("#where_condition").css("display","block")
    $("#export_data_equ").css("display","block")
    listViewCompCol = ""

    let config = {}

    $('#modal-table-body-computedFieldMapper_main_table').find('tr').each(function() {
        name_t = $(this).find('td').eq(0).text().trim()
        if (name_t != undefined){
          config[name_t] = $(`#everyrun_${name_t}`).is(':checked')
        }
    })

    $('#modal-table-body-computedFieldMapper_main_table').empty()

    let tab_list = []
    tab_list = Object.keys(config)

    tab_list.push($("#computedFieldMapper_table").val())
    tab_list = new Set(tab_list);
    tab_list = Array.from(tab_list);

    for(let i=0;i<tab_list.length;i++){
      $.ajax({
        url: `/users/${urlPath}/processGraphModule/`,
        data: {
                element_id: tab_list[i]+"_devcomp_"+uni,
                operation: 'get_fields_comp_upload2'
              },
        type: 'POST',
        dataType: 'json',
        success: function (data) {

          tList = Object.keys(data.tablelist)

          let bk_config = {}

          for(let i=0;i<tList.length;i++){
            tList[i] = tList[i].replace("_devcomp","").replace(`_${uni}`,"")
            bk_config[tList[i]] = $(`#everyrun_${tList[i]}`).is(':checked')
          }

          if(Object.keys(data).length > 0){

            for(let [key,value] of Object.entries(data.tablelist) ){

            $(`#modal-table-body-computedFieldMapper_main_table`).append(
              `
              <tr>
                <td style="text-align:center;" class="${key.replace("_devcomp","").replace(`_${uni}`,"")}_table">
                    ${key.replace("_devcomp","").replace(`_${uni}`,"")}
                </td>
                <td style="text-align:center;">
                    <span>
                    <a data-toggle="tooltip" class="delete_actions_upload_eq" title="Delete" value="eq" id="delete_${key.replace("_devcomp","").replace(`_${uni}`,"")}_EBDisplayButtonID_${uni}"><i name="actions1" value="eq" class="far fa-trash-alt ihover javaSC thin-icontrash" style="font-size: 18px;"></i></a>
                  </span>
                </td>
                <td style="align-items: center;">
                    <div class="custom-control custom-checkbox" style="margin-left:45%">
                    <input type="checkbox" id="everyrun_${key.replace("_devcomp","").replace(`_${uni}`,"")}" data-elementID="" name="everyrun_${key.replace("_devcomp","").replace(`_${uni}`,"")}" class="checkboxinput custom-control-input" value="new">
                    <label for="everyrun_${key.replace("_devcomp","").replace(`_${uni}`,"")}" class="custom-control-label"></label>
                  </div>
                </td>
              </tr>
              `
            )

            if(value){
              $(`#everyrun_${key.replace("_devcomp","").replace(`_${uni}`,"")}`).prop('checked', true);
            }
          }

          }

          if(Object.keys(config).length > 0){

            for(let [key,value] of Object.entries(config) ){
              if(value){
                $(`#everyrun_${key.replace("_devcomp","").replace(`_${uni}`,"")}`).prop('checked', true);
              }
            }

          }


        },
        error: function () {
          Swal.fire({icon: 'error',text: 'Error! Please try again.'});
        },
      });
    }

  })

  $('#EBDisplayModel').on('show.bs.modal', function() {

    $("#where_condition").css("display","none")
    $("#export_data_equ").css("display","none")
    $('#functionsList').find('div').find('a').attr('data-element_comp','datamgm')

  })

  $('#save_workflow_equ').off("click").on("click",function(){

    SaveCompFlow(listViewModelName+"_devcomp_"+uni)

  });

  $(`#savecomputedFieldMapper_button`).off("click").on("click", function () {

    let config = {}

    $('#modal-table-body-computedFieldMapper_main_table').find('tr').each(function() {
      name_t = $(this).find('td').eq(0).text().trim()
      config[name_t] = $(`#everyrun_${name_t}`).is(':checked')
    })

    $(".computedFieldMapperButton").attr("data-data_config", JSON.stringify(config))

    $("#computedFieldMapper").modal('hide')
    $("#documentModal").modal('show')

  })

  $(document).on('click', '.delete_actions_upload_eq', function (event) {
    event.stopImmediatePropagation()
    let id = $(this).attr("id")
    let tableName = id.replace("delete_","").replace(`_EBDisplayButtonID_${uni}`,"")

    const confirmDelete = window.confirm("Remove the computation logic ?")

    if(confirmDelete){

      let config = $(".computedFieldMapperButton").attr("data-data_config")
      if(config == undefined || config == '' || config == '{}' ){
        config = {}
      }else{
        config = JSON.parse(config)
      }

      delete config[tableName]

      reload_data = {"tablelist": config}

      $(".computedFieldMapperButton").attr("data-data_config", JSON.stringify(config))


      $.ajax({
        url: `/users/${urlPath}/processGraphModule/`,
        data: {
          'tablename': tableName+"_devcomp_"+uni,
          'operation': "removeCompCal_dev"
        },
        type: "POST",
        dataType: "json",
        success: function () {

                tList = Object.keys(reload_data.tablelist)
                $('#modal-table-body-computedFieldMapper_main_table').empty()

                if(Object.keys(reload_data).length > 0){

                  for(let [key,value] of Object.entries(reload_data.tablelist) ){

                  $(`#modal-table-body-computedFieldMapper_main_table`).append(
                    `
                    <tr>
                      <td style="text-align:center;" class="${key}_table">
                          ${key}
                      </td>
                      <td style="text-align:center;">
                          <span>
                          <a data-toggle="tooltip" class="delete_actions_upload_eq" title="Delete" value="eq" id="delete_${key}_EBDisplayButtonID_${uni}"><i name="actions1" value="eq" class="far fa-trash-alt ihover javaSC thin-icontrash" style="font-size: 18px;"></i></a>
                        </span>
                      </td>
                      <td style="align-items: center;">
                          <div class="custom-control custom-checkbox" style="margin-left:45%">
                          <input type="checkbox" id="everyrun_${key}" data-elementID="" name="everyrun_${key}" class="checkboxinput custom-control-input" value="new">
                          <label for="everyrun_${key}" class="custom-control-label"></label>
                        </div>
                      </td>
                    </tr>
                    `
                  )

                  if(value){
                    $(`#everyrun_${key}`).prop('checked', true);
                  }
                }

                }

        },
        error: function () {
          Swal.fire({icon: 'error',text: 'Error! Please try again.'});
        }
      });

    }

  })

}

function uploadmapperDev () {
  $("#documentModal").modal("hide")
  $("#Columnmapper").val("").trigger("change")
  $(`#samecolumnwarning`).empty();
  $(`#modal-table-body-columnmapper`).empty();
  $(`#modal-table-head-done`).css('display', 'block');
  $(`#modal-table-head-done`).empty();
  $('#uploadFileColMapper').val("").trigger('change')
  let html1 = '';
  html1 +=
    '<th style="text-align: center;font-weight:bold" disabled>Table Name</th>';
  html1 +=
    '<td style="text-align: center;font-weight:bold" disabled>Reconfigure</td>';
  html1 +=
    '<td style="text-align: center;font-weight:bold" disabled>Apply</td>';
  $(`#modal-table-body-columnmapper`).append(
    '<tr>' + html1 + '</tr>'
  );

  $('.columnconfiguremapperdev').prop(
    'disabled',
    true
  );

  $('#Columnmapper').on('select2:select', function () {
    if (
      $(this).val() != null && $(this).val() != "" && $(this).val() != undefined
    ) {
      $('.columnconfiguremapperdev').prop(
        'disabled',
        false
      );
      tableNameDev = $('#Columnmapper').val();
    }
  });
  let tableList = $('#selectDocumentTable').val();

  $(`#Columnmapper`).select2();
  if (tableList.constructor === Array) {
    $(`#Columnmapper`).empty();
    $(`#Columnmapper`).append(
      "<option value='value'selected disabled>Select Option Name</option>"
    );
    for (let i = 0; i < tableList.length; i++) {
      $(`#Columnmapper`).append(
        new Option(tableList[i], tableList[i])
      );
    }
  } else {
    $(`#Columnmapper`).empty();
    $(`#Columnmapper`).append(
      "<option value='value'selected disabled>Select Option Name</option>"
    );
    $(`#Columnmapper`).append(new Option(tableList, tableList));
  }

  reloadConfigDataDev();
}

  var finaldictcolumnmapperDevReload = []; // eslint-disable-line no-var
  var reloadDevChecker = ''; // eslint-disable-line no-var
  function reloadConfigDataDev () {

    let data = $(".fieldUploadMapperButton").attr("data-data_config")
    if(data != undefined && data != "" && data != "[]"){
      data = JSON.parse(data)
      data = {"reload_data": data}
    }else{
      data = {"reload_data": []}
    }

    if (data.reload_data) {
      finaldictcolumnmapperDevReload = data.reload_data;

      let config = {}

      $(`#modal-table-body-columnmapper`).find('tr').slice(1).each(function() {
          name_t = $(this).find('th').eq(0).text().trim()
          if (name_t != undefined){
            config[name_t] = $('#'+name_t).is(':checked')
          }
      })

      $(`#samecolumnwarning`).empty();
      $(`#modal-table-body-columnmapper`).empty();
      $(`#modal-table-head-done`).css('display', 'block');
      $(`#modal-table-head-done`).empty();
      let html1 = '';
      html1 +=
        '<th style="text-align: center;font-weight:bold" disabled>Table Name</th>';
      html1 +=
        '<td style="text-align: center;font-weight:bold" disabled>Reconfigure</td>';
      html1 +=
        '<td style="text-align: center;font-weight:bold" disabled>Apply</td>';
      $(`#modal-table-body-columnmapper`).append(
        '<tr>' + html1 + '</tr>'
      );
      for (const tableNamer of finaldictcolumnmapperDevReload) {
        let html = '';
        html += `<th style="text-align: center;">${
          Object.keys(tableNamer)[0]
        }</th>`;
        html += `<td style="text-align: center;"><button type="button" class="btn-primary reconfigurecolumnmapperdev" name="${
          Object.keys(tableNamer)[0]
        }" id="reconfigurecolumnmapper_${
          Object.keys(tableNamer)[0]
        }"><i class="fas fa-trash"></i></button></td>`;
        html += `<td style="align-items: center;"><div class="custom-control custom-checkbox " style="margin-left:45%" >
                <input type="checkbox" class="applyConfig custom-control-input" name="${
                  Object.keys(tableNamer)[0]
                }"  id=${
          Object.keys(tableNamer)[0]
        } data-elementid='' >
                <label for=${
                  Object.keys(tableNamer)[0]
                } class="custom-control-label">
                </label>
              </div></td>`;
        $(`#modal-table-body-columnmapper`).append(
          '<tr>' + html + '</tr>'
        );
      }
      if (reloadDevChecker) {
        $(`input[type=checkbox][name=${reloadDevChecker}]`).prop(
          'checked',
          true
        );
      }

      $('.reconfigurecolumnmapperdev').click(function () {
        $(`#samecolumnwarning`).empty();
        const tmname = $(this).attr('name');
        $(`#Columnmapper`)
          .find(`option[value='${tmname}']`)
          .removeAttr('disabled');
        $(this).closest('tr').remove();
        for (let i = 0; i < finaldictcolumnmapperDevReload.length; i++) {
          const tm = Object.keys(finaldictcolumnmapperDevReload[i]);
          if (tm[0] === tmname) {
            const arrindex = finaldictcolumnmapperDevReload.indexOf(
              finaldictcolumnmapperDevReload[i]
            );
            finaldictcolumnmapperDevReload.splice(arrindex, 1);
            $('.fieldUploadMapperButton').attr("data-data_config",JSON.stringify(finaldictcolumnmapperDevReload))
          }
        }
        $(`.columnconfiguremapperdev`).prop(
          'disabled',
          false
        );
        $(`.loadConfigMapper`).prop(
          'disabled',
          false
        );
      });

      if(Object.keys(config).length > 0){

        for(let [key,value] of Object.entries(config) ){
          if(value){
            $(`#${key}`).prop('checked', true);
          }
        }

      }
    }
  }


    // eslint-disable-next-line no-var
    var dataFormDev = '';
    // eslint-disable-next-line no-var
    var columnsqlDev = [];
    // eslint-disable-next-line no-var
    var tableNameDev = '';
    function columnMapperDev () {
      tableNameS = $('#Columnmapper').val();
      tableNameDev = tableNameS
      const inputChecker = $("#uploadFileColMapper").val()
        if (inputChecker) {

          dataForm = new FormData(
            $('#uploadfileformColMapper')[0]
          );
          dataForm.append('operation', 'columnmapper_global_dev');
          dataForm.append('table_name', tableNameDev);
          dataForm.append('elementID', "elementID");

          $.ajaxSetup({
            // eslint-disable-next-line no-unused-vars
            beforeSend: function (xhr, settings) {
              xhr.setRequestHeader('X-CSRFToken', ctoken);
            },
          });

          $.ajax({
            url: `/users/${urlPath}/constriant_get_data/`,
            cache: false,
            contentType: false,
            processData: false,
            data: dataForm,
            type: 'POST',
            dataType: 'json',
            success: function (data) {

              $(`#modal-table-head`).css('display', 'block');
              $(`#modal-table-head-done`).css('display', 'none');
              $(`#modal-table-body-columnmapper`).empty();

              columnsqlDev = data.columnlist;

              let counter = 0;
              for (const indDict of data.columnlist) {
                let html = '';
                html += `<th id="Columnmapper1_${[
                  counter,
                ]}">${indDict}</th>`;
                html += `<td ><select id="Columnmapper_${[
                  counter,
                ]}" class="select2 form-control" name="Columnmapper"  data-placeholder="Column Mapper" >

                        </select></td>`;
                $(`#modal-table-body-columnmapper`).append(
                  '<tr>' + html + '</tr>'
                );
                $(`#modal-table-body-columnmapper`)
                  .find('.select2')
                  .select2({ width: '100%' });

                for (let i = 0; i < data.columnlist1.length; i++) {
                  $(`#Columnmapper_${[counter]}`).append(
                    new Option(data.columnlist1[i], data.columnlist1[i])
                  );
                }
                $(`#Columnmapper_${[counter]}`)
                  .val(indDict)
                  .trigger('change');

                counter++;
              }

              $(`.savecolumnconfiguremapperdev`).css(
                'display',
                'block'
              );
            },
            error: function () {
              Swal.fire({icon: 'error',text: 'Error! Please try again.'});
            },
          });
        }else{
          if(tableNameS != "" && tableNameS != undefined){
            $.ajax({
              url: `/users/${urlPath}/constriant_get_data/`,
              data: {
                "table_name": tableNameDev,
                "operation": 'columnmapper_global_dev2',
              },
              type: 'POST',
              dataType: 'json',
              success: function (data) {

                $(`#modal-table-head`).css('display', 'block');
                $(`#modal-table-head-done`).css('display', 'none');
                $(`#modal-table-body-columnmapper`).empty();

                columnsqlDev = data.columnlist;

                let counter = 0;
                for (const indDict of data.columnlist) {
                  let html = '';
                  html += `<th id="Columnmapper1_${[
                    counter,
                  ]}">${indDict}</th>`;
                  html += `<td ><select id="Columnmapper_${[
                    counter,
                  ]}" class="select2 form-control" name="Columnmapper"  data-placeholder="Column Mapper" >

                          </select></td>`;
                  $(`#modal-table-body-columnmapper`).append(
                    '<tr>' + html + '</tr>'
                  );
                  $(`#modal-table-body-columnmapper`)
                    .find('.select2')
                    .select2({ width: '100%',tags:true });

                  for (let i = 0; i < data.columnlist1.length; i++) {
                    $(`#Columnmapper_${[counter]}`).append(
                      new Option(data.columnlist1[i], data.columnlist1[i])
                    );
                  }
                  $(`#Columnmapper_${[counter]}`)
                    .val(indDict)
                    .trigger('change');

                  counter++;
                }

                $(`.savecolumnconfiguremapperdev`).css(
                  'display',
                  'block'
                );
              },
              error: function () {
                Swal.fire({icon: 'error',text: 'Error! Please try again.'});
              },
            });
          }
        }
    }

    var submitFinalDataDev = []; // eslint-disable-line no-var
    function saveColumnMapperDev () {

      let finaldictcolumnmapper = [];
      if(tableNameDev != "" && tableNameDev != undefined){

        const checkerDict = $('.fieldUploadMapperButton').attr("data-data_config")

        if (checkerDict && String(checkerDict) !== '[]') {
          finaldictcolumnmapper = JSON.parse(checkerDict);
          for (let i = 0; i < finaldictcolumnmapper.length; i++) {
            const tm = Object.keys(finaldictcolumnmapper[i]);
            if (tm[0] === tableNameDev) {
              const arrindex = finaldictcolumnmapper.indexOf(
                finaldictcolumnmapper[i]
              );
              finaldictcolumnmapper.splice(arrindex, 1);
            }
          }
        }
        const saveColumnDict = {};
        const columnmapperdict = [];
        const columnduplicatescheck = [];
        const duplicateChecker = [];

        for (let i = 0; i < columnsqlDev.length; i++) {
          const columnmapperdict1 = {};
          const column2 = $(`#Columnmapper1_${[i]}`).html();
          const column1 = $(`#Columnmapper_${[i]}`).val();
          if (
            String(column1) !== 'undefined' &&
            column1 !== '' &&
            column1 !== null
          ) {
            if (columnduplicatescheck.includes(column1)) {
              $(`#samecolumnwarning`).html(
                `${[
                  column1,
                ]} is already assigned to another column, please reconfigure the column mapper.`
              );
              duplicateChecker.push(true);
            } else {
              columnduplicatescheck.push(column1);
              columnmapperdict1[column1] = column2;
              columnmapperdict.push(columnmapperdict1);
              duplicateChecker.push(false);
            }
          }
        }
        if (!duplicateChecker.includes(true)) {

          let config = {}

          $(`#modal-table-body-columnmapper`).find('tr').slice(1).each(function() {
              name_t = $(this).find('th').eq(0).text().trim()
              if (name_t != undefined){
                config[name_t] = $('#'+name_t).is(':checked')
              }
          })

          $(`#samecolumnwarning`).empty();
          $(`#modal-table-body-columnmapper`).empty();
          $(`#modal-table-head-done`).css('display', 'block');
          $(`#modal-table-head-done`).empty();

          let html1 = '';
          html1 +=
            '<th style="text-align: center;font-weight:bold"  disabled>Table Name</th>';
          html1 +=
            '<td style="text-align: center;font-weight:bold" disabled>Reconfigure</td>';
          html1 +=
            '<td style="text-align: center;font-weight:bold" disabled>Apply</td>';
          $(`#modal-table-body-columnmapper`).append(
            '<tr>' + html1 + '</tr>'
          );

          let tableSavedList = $('.fieldUploadMapperButton').attr("data-data_config")

          if (tableSavedList && String(tableSavedList) !== '[]') {
            tableSavedList = JSON.parse(tableSavedList);

            for (const tableKeys of tableSavedList) {
              if (String(Object.keys(tableKeys)[0]) !== String(tableNameDev)) {
                const tabName = Object.keys(tableKeys)[0];
                let html = '';
                html += `<th style="text-align: center;">${tabName}</th>`;
                html += `<td style="text-align: center;"><button type="button" class="btn-primary reconfigurecolumnmapperdev" name="${tabName}" id="reconfigurecolumnmapper_${tabName}"><i class="fas fa-trash"></i></button></td>`;
                html += `<td style="align-items: center;"><div class="custom-control custom-checkbox " style="margin-left:45%" >
                  <input type="checkbox" class="applyConfig custom-control-input" name="${tabName}"  id=${
                  tabName
                } >
                  <label for=${tabName} class="custom-control-label">
                  </label>
                    </div></td>`;
                $(`#modal-table-body-columnmapper`).append(
                  '<tr>' + html + '</tr>'
                );
              }
            }
          }

          let html = '';
          html += `<th style="text-align: center;">${[tableNameDev]}</th>`;
          html += `<td style="text-align: center;"><button type="button" class="btn-primary reconfigurecolumnmapperdev" name="${[
            tableNameDev,
          ]}" id="reconfigurecolumnmapper_${[
            tableNameDev,
          ]}"><i class="fas fa-trash"></i></button></td>`;
          html += `<td style="align-items: center;"><div class="custom-control custom-checkbox " style="margin-left:45%" >

                  <input type="checkbox" class="applyConfig custom-control-input" name="${[
                    tableNameDev,
                  ]}"  id=${[tableNameDev]}>
                  <label for=${
                    [tableNameDev]
                  } class="custom-control-label">
                  </label>
                </div></td>`;

          $(`input[type=checkbox][name="${[tableNameDev]}"]`).prop('checked', true);
          $(`#modal-table-body-columnmapper`).append(
            '<tr>' + html + '</tr>'
          );
          saveColumnDict[tableNameDev] = columnmapperdict;
          finaldictcolumnmapper.push(saveColumnDict);

          if(Object.keys(config).length > 0){

            for(let [key,value] of Object.entries(config) ){
              if(value){
                $(`#${key}`).prop('checked', true);
              }
            }

          }

          $('.reconfigurecolumnmapperdev').click(function () {
            $(`#samecolumnwarning`).empty();
            const tmname = $(this).attr('name');
            $(`#Columnmapper`)
              .find(`option[value='${tmname}']`)
              .removeAttr('disabled');
            $(this).closest('tr').remove();
            for (let i = 0; i < finaldictcolumnmapper.length; i++) {
              const tm = Object.keys(finaldictcolumnmapper[i]);
              if (String(tm[0]) === String(tmname)) {
                const arrindex = finaldictcolumnmapper.indexOf(
                  finaldictcolumnmapper[i]
                );
                finaldictcolumnmapper.splice(arrindex, 1);

                $('.fieldUploadMapperButton').attr("data-data_config",JSON.stringify(finaldictcolumnmapper))
              }
            }
          });
          $(this).css('display', 'none');

          $('.fieldUploadMapperButton').attr("data-data_config",JSON.stringify(finaldictcolumnmapper))

          submitFinalDataDev = finaldictcolumnmapper;
        }
      }
    }


function loadConfigMapperDev () {
      tableName = $('#Columnmapper').val();

      const dataForm = new FormData(
        $('#uploadfileformColMapper')[0]
      );
      dataForm.append('operation', 'columnmapper_global_dev');

      dataForm.append('table_name', tableName);
      dataForm.append('elementID', "elementID");
      const inputChecker = $("#uploadFileColMapper").val();

      if (tableName != "" && tableName != undefined && inputChecker) {

        $.ajax({
          url: `/users/${urlPath}/constriant_get_data/`,
          cache: false,
          contentType: false,
          processData: false,
          data: dataForm,
          type: 'POST',
          dataType: 'json',
          success: function (data) {

            let reload_data = $(".fieldUploadMapperButton").attr("data-data_config")
            if(reload_data != undefined && reload_data != "[]" && reload_data != ""){
              reload_data = JSON.parse(reload_data)
              reload_data = {"saved_data": reload_data}
            }else{
              reload_data = {"saved_data": []}
            }

            for (const save1 of reload_data.saved_data) {
              if (String(tableName) === String(Object.keys(save1)[0])) {
                $(`#modal-table-head`).css('display', 'block');
                $(`#modal-table-head-done`).css('display', 'none');
                $(`#modal-table-body-columnmapper`).empty();

                columnsqlDev = data.columnlist;

                let counter = 0;
                for (const indDict of data.columnlist) {
                  let html = '';
                  html += `<th id="Columnmapper1_${[
                    counter,
                  ]}">${indDict}</th>`;
                  html += `<td ><select id="Columnmapper_${[
                    counter,
                  ]}" data-reload-value='${indDict}' class="select2 form-control" name="Columnmapper"  data-placeholder="Column Mapper" >
                        </select></td>`;
                  $(`#modal-table-body-columnmapper`).append(
                    '<tr>' + html + '</tr>'
                  );
                  $(`#modal-table-body-columnmapper`)
                    .find('.select2')
                    .select2({ width: '100%' });

                  for (let i = 0; i < data.columnlist1.length; i++) {
                    $(`#Columnmapper_${[counter]}`).append(
                      new Option(data.columnlist1[i], data.columnlist1[i])
                    );
                  }
                  $(`#Columnmapper_${[counter]}`)
                    .val(indDict)
                    .trigger('change');
                  counter++;
                }
                for (const save2 of save1[tableName]) {
                  $(`select[data-reload-value=${Object.values(save2)[0]}]`)
                    .val(Object.keys(save2)[0])
                    .trigger('change');
                }
                $(`.savecolumnconfiguremapperdev`).css(
                  'display',
                  'block'
                );
              }
            }
          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          },
        });
      }else if(tableName != "" && tableName != undefined){
        $.ajax({
          url: `/users/${urlPath}/constriant_get_data/`,
          data: {
            "table_name": tableName,
            "operation": 'columnmapper_global_dev2',
          },
          type: 'POST',
          dataType: 'json',
          success: function (data) {

            let reload_data = $(".fieldUploadMapperButton").attr("data-data_config")
            if(reload_data != undefined && reload_data != "[]" && reload_data != ""){
              reload_data = JSON.parse(reload_data)
              reload_data = {"saved_data": reload_data}
            }else{
              reload_data = {"saved_data": []}
            }

            for (const save1 of reload_data.saved_data) {
              if (String(tableName) === String(Object.keys(save1)[0])) {
                $(`#modal-table-head`).css('display', 'block');
                $(`#modal-table-head-done`).css('display', 'none');
                $(`#modal-table-body-columnmapper`).empty();

                columnsqlDev = data.columnlist;

                let counter = 0;
                for (const indDict of data.columnlist) {
                  let html = '';
                  html += `<th id="Columnmapper1_${[
                    counter,
                  ]}">${indDict}</th>`;
                  html += `<td ><select id="Columnmapper_${[
                    counter,
                  ]}" data-reload-value='${indDict}' class="select2 form-control" name="Columnmapper"  data-placeholder="Column Mapper" >
                        </select></td>`;
                  $(`#modal-table-body-columnmapper`).append(
                    '<tr>' + html + '</tr>'
                  );
                  $(`#modal-table-body-columnmapper`)
                    .find('.select2')
                    .select2({ width: '100%' });

                  for (let i = 0; i < data.columnlist1.length; i++) {
                    $(`#Columnmapper_${[counter]}`).append(
                      new Option(data.columnlist1[i], data.columnlist1[i])
                    );
                  }
                  $(`#Columnmapper_${[counter]}`)
                    .val(indDict)
                    .trigger('change');
                  counter++;
                }
                for (const save2 of save1[tableName]) {
                  $(`select[data-reload-value=${Object.values(save2)[0]}]`)
                    .val(Object.keys(save2)[0])
                    .trigger('change');
                }
                $(`.savecolumnconfiguremapperdev`).css(
                  'display',
                  'block'
                );
              }
            }

          },
          error: function () {
            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
          },
        });
      }else {
        Swal.fire({icon: 'warning',text:"No Table selected / File not found." });
      }
    }
