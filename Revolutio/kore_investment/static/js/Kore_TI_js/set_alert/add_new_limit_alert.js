/* eslint-disable comma-dangle */
/* global alertModalBodyPopulate:true, originalVerboseColumnNames:true */

$('.add_alert_limit_button_clicked').each(function () {
  // eslint-disable-next-line no-use-before-define
  $(this).on('click', addAlertLimitButtonClickedFunction)
})

// eslint-disable-next-line no-unused-vars
function addAlertLimitButtonClickedFunction (e) {
  const baseAlertCard = $(this).parents('div.card_col_cond')
  const colName = baseAlertCard.find("input[name='name_col_name']").val()
  const colCond = baseAlertCard.find("input[name='name_col_cond']").val()

  const verboseNameOrigName = originalVerboseColumnNames.find(function (
    element
  ) {
    return String(element.originalName) === String(colName)
  })
  const alertListTemp = []
  alertListTemp.push({
    column_verbose_name: verboseNameOrigName.verboseName,
    condition: colCond,
    limit: null,
  })
  alertModalBodyPopulate(alertListTemp)
}
