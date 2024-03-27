/* eslint-disable semi */
$('.card_limit').each(function () {
  // eslint-disable-next-line no-use-before-define
  $(this).on('removed.lte.cardwidget', alertDeleteLimit);
});

function alertDeleteLimit (e) {
  e.stopPropagation();
  const parentPk = $(this).attr('data-parent_pk');
  const innercardLimit = $(this).attr('data-limit_value');
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
      operation: 'delete_innercard',
      innercard_limit: innercardLimit,
      parent_pk: parentPk
    },
    type: 'POST',
    dataType: 'json',
    success: function (data) {
      // eslint-disable-next-line no-console
      console.log(data);
    },
    error: function () {
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    }
  });
}
