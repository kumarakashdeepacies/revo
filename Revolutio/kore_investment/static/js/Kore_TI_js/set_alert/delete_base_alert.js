/* eslint-disable semi */
/* eslint-disable comma-dangle */
$('.card_col_cond').each(function () {
  // eslint-disable-next-line no-use-before-define
  $(this).on('removed.lte.cardwidget', alertDeleteColumnCondition);
});
function alertDeleteColumnCondition (e) {
  e.stopPropagation();
  let url_string = window.location.pathname
  let f_occ = url_string.indexOf('/', url_string.indexOf('/') + 1)
  let s_occ = url_string.indexOf('/', url_string.indexOf('/') + f_occ +1)
  let t_occ = url_string.indexOf('/', url_string.indexOf('/') + s_occ +1)
  let app_code2 = url_string.substring(f_occ+1,s_occ)
  let current_dev_mode2 = url_string.substring(s_occ+1,t_occ)
  if(current_dev_mode2 != "Build" && current_dev_mode2 != "Edit"){
    current_dev_mode2 = "User"
  }
  const outerAlertcardPk = $(this).attr('data-alert_pk');
  $.ajax({
    url:`/users/${app_code2}/${current_dev_mode2}/alertModel/`,

    data: {
      operation: 'delete_outer_alertcard',
      outer_alertcard_pk: outerAlertcardPk,
    },
    type: 'POST',
    dataType: 'json',
    // eslint-disable-next-line no-unused-vars
    success: function (data) {},
    error: function () {
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    },
  });
  $(this).remove();
}
