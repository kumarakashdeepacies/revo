/* eslint-disable semi */
/* eslint-disable comma-dangle */
// function buttonEnabler(){
// console.log("entered the function")
//     if(($('.filter-table tr').length)>0){
//         console.log("noo")
//         $('.id_set_alert_button').removeAttr('disabled');
//     }
//     else{
//       console.log("yes")
//         $('.id_set_alert_button').attr('disabled','disabled');
//     }
// }
//   $('.filter-table').on('update', function(){
  // Swal.fire({icon: 'success',text: 'Table updated, launching kill space goats sequence now.'});
//     alert('Table updated, launching kill space goats sequence now.')
// });
// $("variable").on('change',function(){
//     console.log("Item Selected")
// });

// eslint-disable-next-line no-unused-vars
function buttonEnabler () {
  // eslint-disable-line no-unused-vars
  if ($('.filter-table tr').length > 0) {
    $('#singlealert').css('display', 'none');

    // $('.id_set_alert_button').removeAttr('disabled');
  } else {
    // $('#id_set_alert_button').attr('disabled','disabled');
    // $("#singlealert").modal("hide");
    $('#singlealert').css('display', 'none');
    $('#alert_modal').removeClass('show');
  }
}

// eslint-disable-next-line no-unused-vars
function viewalert (alertItem) {
  // eslint-disable-line no-unused-vars
  // data['alert'] = alertItem;
  const alertTag = alertItem.alert_tag;
  const alertParentCard = $('#alert_view_tab_content').find(
    '.alert_parent_card'
  );
  alertParentCard.find('[data-alert_tag]').each(function () {
    if (String(alertTag) === '') {
      $(this).hide();
      return;
    }
    if (String($(this).attr('data-alert_tag')) !== String(alertTag)) {
      $(this).hide();
    }
    if (String($(this).attr('data-alert_tag')) === String(alertTag)) {
      $(this).show();
    } else {
      $(this).hide();
    }
  });
}

// eslint-disable-next-line no-unused-vars
function addSingleLimit (alertItem) {
  // eslint-disable-line no-unused-vars
  const newColumn = document.getElementById('modal_new_column');
  const newcolcondition = document.getElementById('modal_new_column_condition');
  const newid = document.getElementById('myid');
  newColumn.value = alertItem.column_name;
  newcolcondition.value = alertItem.condition;
  newid.value = alertItem.id;
  // var vname = alertItem.sub_alert_multiple_limit.verbose_name;
}

// eslint-disable-next-line no-unused-vars
function addsinglealert (alertItem) {
  // eslint-disable-line no-unused-vars
  $('.withoutrefresh').css('display', 'block');
  const x = $('.thisform').serializeArray();
  // const vall = (x[0].value)
  // $(".withoutrefresh").find( $("#fname1")).append(vall).show();
  $('.limitname1').val(x[0].value);
  $('.limitcolor1').val(x[1].value);

  // $.each(x, function (i, field) {
  // $(".withoutrefresh").append(field.name + ":" + field.value + " ");
  // });
  const limit = document.getElementById('limit').value;
  const color = document.getElementById('color').value;
  const status = 'enable';
  let url_string = window.location.pathname
  let f_occ = url_string.indexOf('/', url_string.indexOf('/') + 1)
  let s_occ = url_string.indexOf('/', url_string.indexOf('/') + f_occ +1)
  let t_occ = url_string.indexOf('/', url_string.indexOf('/') + s_occ +1)
  let app_code2 = url_string.substring(f_occ+1,s_occ)
  let current_dev_mode2 = url_string.substring(s_occ+1,t_occ)
  if(current_dev_mode2 != "Build" && current_dev_mode2 != "Edit"){
  current_dev_mode2 = "User"
  }
  // $('.limitname').append(limit)
  // $('.limitcolor').append(color)
  const primaryKey = alertItem.value;
  $.ajax({
    url: `/users/${app_code2}/${current_dev_mode2}/alertModel/`,

    data: {
      operation: 'addsingle_alert',
      limit: limit,
      color: color,
      status: status,
      primarykey: primaryKey,
    },
    type: 'POST',
    dataType: 'json',
    // eslint-disable-next-line no-unused-vars
    success: function (data) {
      window.location.reload();
    },
    error: function () {
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    },
  });
}

// function myFunction (ids) { // eslint-disable-line no-unused-vars
//   const checkbox = document.getElementById('switch_' + ids)
//   // const label = document.getElementById('switchLabel_' + ids)
//   if (checkbox.checked === true) {
//     // label.innerText = "enable";
//   } else {
//     // label.innerText = "disable";
//   }
// }
