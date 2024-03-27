/* eslint-disable semi */
/* eslint-disable comma-dangle */
/* global  originalVerboseColumnNames:true,model_name:true */

$('.edit_alert_limit_button_clicked').click(function () {
  const baseAlertCard = $(this).parents('div.card_col_cond');
  const innerCardLimit = baseAlertCard.find('div.card_limit');

  const alertRowPk = baseAlertCard.attr('data-alert_pk');

  const colName = baseAlertCard.find("input[name='name_col_name']").val();

  const alertName = baseAlertCard.find("input[name='name_alert_name']").val();

  const colTag = baseAlertCard.find("input[name='name_alert_type']").val();
  const comments = baseAlertCard.find("input[name='name_comments']").val();
  let url_string = window.location.pathname
let f_occ = url_string.indexOf('/', url_string.indexOf('/') + 1)
let s_occ = url_string.indexOf('/', url_string.indexOf('/') + f_occ +1)
let t_occ = url_string.indexOf('/', url_string.indexOf('/') + s_occ +1)
let app_code2 = url_string.substring(f_occ+1,s_occ)
let current_dev_mode2 = url_string.substring(s_occ+1,t_occ)
if(current_dev_mode2 != "Build" && current_dev_mode2 != "Edit"){
  current_dev_mode2 = "User"
}

  const verboseNameOrigName = originalVerboseColumnNames.find(function (
    element
  ) {
    return element.originalName === colName;
  });

  const alertDetailsList = [];
  let status = '';
  innerCardLimit.each(function () {
    const limit = $(this).find("input[name='name_limit']").val();

    const color = $(this).find("input[name='change_alertcolor1']").val();

    if ($("input[name='name_checkbox_enable_disable1']").prop('checked')) {
      status = 'enable';
    } else {
      status = 'disable';
    }

    alertDetailsList.push({
      verbose_name: verboseNameOrigName.verboseName,
      limit: limit,
      color_active: color,
      status: status,
    });
  });
  $.ajax({
    url: `/users/${app_code2}/${current_dev_mode2}/alertModel/`,

    data: {
      operation: 'updateAlert1',
      // eslint-disable-next-line camelcase
      model_name: model_name,
      comments: comments,
      alert_name: alertName,
      alert_tag: colTag,
      alert_config: JSON.stringify(alertDetailsList),
      primary_key: alertRowPk,
    },
    type: 'POST',
    dataType: 'json',
    // eslint-disable-next-line no-unused-vars
    success: function (data) {
      return true;
    },
    error: function () {
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    },
  });

  // }
});

// function edit_alert_limit_button_clicked_function1(e) {
//   var baseAlertCard = ($('.limitname')).parents("div.card_col_cond")
//   var innerCardLimit = baseAlertCard.find("div.card_limit")
//   var alertRowPk = baseAlertCard.attr("data-alert_pk")
//   var colName = baseAlertCard.find("input[name='name_col_name']").val()
//   var verboseNameOrigName = originalVerboseColumnNames.find(function (element) {
//     return element.originalName == colName
//   })
//   var alertDetailsList = []
//   innerCardLimit.each(function () {
//     var limit = $(this).find("input[name='name_limit']").val()
//     var color = $(this).find("input[name='change_alertcolor1']").val()
//     if (($("input[name='name_checkbox_enable_disable1']")).prop("checked")) {
//       status = "enable";

//     }
//     else {
//       status = "disable";
//     }

//     alertDetailsList.push({
//       "verbose_name": verboseNameOrigName.verboseName,
//       "limit": limit,
//       "color_active": color,
//       "status": status
//     })

//   })
//   $.ajax({
//     url: "{% url 'users:alert_model' %}",

//     data: {
//       'operation': "updateAlert1",
//       'model_name': model_name,
//       'alert_config': JSON.stringify(alertDetailsList),
//       'primary_key': alertRowPk
//     },
//     type: "POST",
//     dataType: "json",
//     success: function (data) {
//       console.log(data)
//       return
//     },
//     error: function () {
//       Swal.fire({icon: 'error',text: 'Error! Please try again.'});
//     }
//   })

//   //}

// }
