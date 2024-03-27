// JS STANDARDIZATION SCRIPT
/* global createViewIdList */
for (const i in createViewIdList) {
  $(`#${createViewIdList[i]}_tab_content`).find('[data-jsattr]').each(function () {
    const jsvalue = this.getAttribute('data-jsattr')
    const id = this.getAttribute('id')
    const elementIdArray = id.split('_')
    let elementID = elementIdArray[elementIdArray.length - 1]
    $.each(eval(jsvalue), function () { // eslint-disable-line no-eval
      if ((String(this.parentattr) === 'data-jsfunction') && (String(this.parentvalue) === 'Dependent_field_autopopulate')) {
        const data = {}
        let chilFieldName
        let referenceTableName
        let parentColumn
        let childColumn
        let parentFieldName
        $.each(eval(this.finaljsattr), function (key, value) { // eslint-disable-line no-eval
          data[value[0].attr] = value[0].value
        })
        for (const i in data) {
          if (String(i) === 'data-child_field_name') {
            chilFieldName = data[i]
          }
          if (String(i) === 'data-parent_field_name') {
            parentFieldName = data[i]
          }

          if (String(i) === 'data-reference_table_name') {
            referenceTableName = data[i]
          }
          if (String(i) === 'data-parent_column') {
            parentColumn = data[i]
          }
          if (String(i) === 'data-child_column') {
            childColumn = data[i]
          }
        }

        const x = '#id_' + parentFieldName + '_' + elementID

        $(x).change(function () {
          const id = this.getAttribute('id')
          const elementIdArray = id.split('_')
          elementID = elementIdArray[elementIdArray.length - 1]
          const parentFieldValue = $(x).find('option:selected').val()
          $.ajax({
            url: windowLocationAttr.href + 'create/',
            data: {
              operation_name: 'Dependent_field_autopopulate',
              value: parentFieldValue,
              reference_table_name: referenceTableName,
              parent_column: parentColumn,
              child_column: childColumn
            },
            type: 'POST',
            dataType: 'json',
            success: function (data) {
              const idChild = 'id_' + chilFieldName + '_' + elementID
              const result = data.data[0][childColumn]
              const elem = document.getElementById(idChild)
              elem.value = result
            },
            error: function () {
              Swal.fire({icon: 'error',text: 'Error! Please try again.'});
            }
          })
        })
      };
      // JS code part-2
      if ((String(this.parentattr) === 'data-jsfunction') && (String(this.parentvalue) === 'Multi-field-autopopulate')) {
        const data1 = {}
        let chilFieldName
        let referenceMasterTableColumn
        let referenceChildTableColumn

        $.each(eval(this.finaljsattr), function (key, value) { // eslint-disable-line no-eval
          data1[value[0].attr] = value[0].value
        })
        for (const i in data1) {
          if (String(i) === 'data-child_field_name') {
            chilFieldName = data1[i]
          }
          if (String(i) === 'data-reference_master_table_column') {
            referenceMasterTableColumn = data1[i]
          }
          if (String(i) === 'data-reference_child_table_column') {
            referenceChildTableColumn = data1[i]
          }
        }

        const var1 = '#id_' + referenceMasterTableColumn + '_' + elementID
        const var2 = '#id_' + referenceChildTableColumn + '_' + elementID
        $(var1).on('click', autofunction)
        $(var2).on('click', autofunction)
        function autofunction (event) {
          let val1 = $(var1).find('option:selected').text()
          if (String(val1) === '') {
            val1 = $(var1).val()
          }
          let val2 = $(var2).find('option:selected').text()
          if (String(val2 === '')) {
            val2 = $(var2).val()
          }

          const idChild = 'id_' + chilFieldName + '_' + elementID
          const result = val1 + '-' + val2
          const elem = document.getElementById(idChild)
          elem.value = result
          $(elem).prop('readonly', true)
        };
      };
    })
  })
};
// <!-- JS Standardization ends-->
