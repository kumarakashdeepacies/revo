/* global table,dataContainingColumnNames,country_master */
$("button[name='List_view__Data_table__Multi_edit']").on('click', function () {
  if (String($(this).val()) === 'List_view__Data_table__Multi_edit_show_checkboxes') {
    $('#example1 input.multi_column_edit_checkbox').each(function () {
      $(this).show()
    })
    $(this).html('Edit')
    $(this).val('List_view__Data_table__Multi_edit_open_modal')
    return
  }

  if (String($(this).val()) === 'List_view__Data_table__Multi_edit_open_modal') {
    const pkList = []
    $('#example1 input.multi_column_edit_checkbox:checked').each(function () {
      const cellIndex = this.parentElement._DT_CellIndex
      const rowData = table.row(cellIndex.row).data()
      const primaryKeyColumnName = dataContainingColumnNames[1].data
      const primaryKeyId = rowData[primaryKeyColumnName]
      pkList.push(primaryKeyId)
    })

    $('#example1 input.multi_column_edit_checkbox').each(function () {
      $(this).prop('checked', false)
      $(this).hide()
    })

    $.ajax({
      // "url": "{% url 'users:standard_update_master_form' %}",
      url: windowLocation + 'multi_update/',
      // "data": JSON.stringify(data),
      data: {
        operation: 'send_form_data_multiple_rows_from_backend_to_front_end',
        primary_key_list: JSON.stringify(pkList)
      },
      dataType: 'json',
      type: 'POST',
      success: function (data) {
        const formaction = windowLocation + 'multi_update_save/'
        const modalBody = $('#list_view_multi_edit_modal').find('.modal-body')
        modalBody.empty()
        modalBody.append(`<form id="list_view_datatable_multi_edit_form" method="POST" action="${formaction}">

<div class="modal-footer">
  <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
  <button type="submit" class="btn btn-primary">Save changes</button>
</div>
</form> `)

        $('#list_view_datatable_multi_edit_form').prepend(data.formset)
        //   Object.keys(data.formset_data).forEach(function(key) {
        //     modalBody.find(`[name='${key}']`).val(data.formset_data[key])

        // });

        modalBody.find('select.select2').each(function () {
          if (String($(this).attr('class')) !== 'select2-hidden-accessible') {
            $(this).select2()
          }
        })

        // FOR COUNTRY MASTER
        modalBody.find('table tr').each(function () {
          const countryName = $(this).find("select[name$='country_name']")
          const perpetuity = $(this).find("input[name*='perpetuity']")

          let isoCode = $(this).find("input[name$='iso_code']")
          if (Number(isoCode.length) === 0) {
            // this condition is true when the standardised form is being used
            isoCode = $(this).find("select[name*='iso_code']")
          }
          const activeTo = $(this).find("input[name$='active_to']")
          country_master(countryName, perpetuity, isoCode, activeTo)
        })

        $('#list_view_multi_edit_modal').modal('show')
      },
      error: function () {
        Swal.fire({icon: 'error',text: 'Error! Please try again.'});
      }
    })
    $(this).html('Multi edit')
    $(this).val('List_view__Data_table__Multi_edit_show_checkboxes')
  }
})
