/* eslint-disable prefer-const */
/* eslint-disable no-use-before-define */
$("input[name='name_checkbox_enable_disable']").each(function () {
  $(this).on('change', alertstatuschanged)
})

function alertstatuschanged () {
  // eslint-disable-next-line prefer-const
  let alertpk = $(this).parents('div[data-alert_pk]').attr('data-alert_pk')
  let alertstatus = ''
  if ($(this).prop('checked')) {
    alertstatus = 'enable'
  } else {
    alertstatus = 'disable'
  }
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
    url: `/users/${app_code2}/${current_dev_mode2}/alertModel/`,

    data: {
      operation: 'multi_alert_status',
      status: alertstatus,
      pk: alertpk
    },
    type: 'POST',
    dataType: 'json',
    // eslint-disable-next-line no-unused-vars
    success: function (data) {},
    error: function () {
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    }
  })
}
$("input[name='name_checkbox_enable_disable1']").each(function () {
  $(this).on('change', alertstatuschanged1)
})
function alertstatuschanged1 () {
  // eslint-disable-next-line prefer-const
  let alertpk = $(this).parents('div[data-alert_pk]').attr('data-alert_pk')
  let alertsimplesinglecolumnlimitvalue = $(this)
    .parents('div[data-limit_value]')
    .attr('data-limit_value')
  let smallcardlimitname = alertsimplesinglecolumnlimitvalue
  let alertstatus = ''
  let url_string = window.location.pathname
  let f_occ = url_string.indexOf('/', url_string.indexOf('/') + 1)
  let s_occ = url_string.indexOf('/', url_string.indexOf('/') + f_occ +1)
  let t_occ = url_string.indexOf('/', url_string.indexOf('/') + s_occ +1)
  let app_code2 = url_string.substring(f_occ+1,s_occ)
  let current_dev_mode2 = url_string.substring(s_occ+1,t_occ)
  if(current_dev_mode2 != "Build" && current_dev_mode2 != "Edit"){
    current_dev_mode2 = "User"
  }
  if ($(this).prop('checked')) {
    alertstatus = 'enable'
  } else {
    alertstatus = 'disable'
  }
  $.ajax({
    url: `/users/${app_code2}/${current_dev_mode2}/alertModel/`,

    data: {
      operation: 'multi_alert_status1',
      status: alertstatus,
      pk: alertpk,
      limitname: smallcardlimitname
    },
    type: 'POST',
    dataType: 'json',
    // eslint-disable-next-line no-unused-vars
    success: function (data) {},
    error: function () {
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    }
  })
}
