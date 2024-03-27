/* eslint-disable comma-dangle */
/* eslint-disable no-use-before-define */
$("input[name='change_alertcolor']").each(function () {
  $(this).on('change', alertStatusChanged)
})

function alertStatusChanged () {
  const alertPk = $(this).parents('div[data-alert_pk]').attr('data-alert_pk')
  // var alert_simple_single_column_limit_value = $(this).parents("div[data-limit_value]").attr("data-limit_value")
  const color = $(this)[0].value
  // trcolor = $(this).parents("div[data-alert_color]").attr("data-alert_color")
  // ($(this).parents("div[data-alert_color]").attr("data-alert_color")).css("backgroundcolor",color)
  // $(this).css("backgroung-color",color)
  // var alert_simple_single_column_limit_value = $(this).parents("div[data-limit_value]").attr("data-limit_value")
  // var smallcardLimitName=alert_simple_single_column_limit_value
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
      operation: 'multi_alert_color',
      color: color,
      pk: alertPk,
      // 'limitname':smallcardLimitName,
    },
    type: 'POST',
    dataType: 'json',
    success: function (data) {},
    error: function () {
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    },
  })
}

$("input[name='change_alertcolor1']").each(function () {
  $(this).on('change', alertStatusChanged1)
})
function alertStatusChanged1 () {
  const alertPk = $(this).parents('div[data-alert_pk]').attr('data-alert_pk')
  const smallcardLimitName = $(this)
    .parents('div[data-limit_value]')
    .attr('data-limit_value')
  const color = $(this)[0].value
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
      operation: 'multi_alert_color1',
      color: color,
      pk: alertPk,
      limitname: smallcardLimitName,
    },
    type: 'POST',
    dataType: 'json',
    success: function (data) {},
    error: function () {
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    },
  })
}
