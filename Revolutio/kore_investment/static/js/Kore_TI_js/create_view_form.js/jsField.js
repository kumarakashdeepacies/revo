
/* eslint no-redeclare: ["error", { "builtinGlobals": true }]  */

/* global injectScript */
/* eslint-env browser */

/* eslint-disable  no-unused-vars,camelcase,no-shadow-restricted-names */
var listViewTableDict = {}
var listViewEditTemplate = {}
var createViewIdList = []
var crossFilterDict = {}
var element_table_IDList = []
var chartSaveEleIdList = []
var chartSaveEleId = {}
var analysiselementIDList = [];
var names = {}
var element_page = [];
var app_code_home = ''
var item_code_list = [];
var user_home = '';
var ctoken1 = $('form').find('input[name="csrfmiddlewaretoken"]').val()
var url_string = window.location.pathname
var f_occ = url_string.indexOf('/', url_string.indexOf('/') + 1)
var s_occ = url_string.indexOf('/', url_string.indexOf('/') + f_occ +1)
var t_occ = url_string.indexOf('/', url_string.indexOf('/') + s_occ +1)
var app_code2 = url_string.substring(f_occ+1,s_occ)
var current_dev_mode2 = url_string.substring(s_occ+1,t_occ)
if(current_dev_mode2 != "Build" && current_dev_mode2 != "Edit"){
  current_dev_mode2 = "User"
}
/* eslint-enable */
$.ajaxSetup({
  beforeSend: function (xhr, settings) {
    xhr.setRequestHeader('X-CSRFToken', ctoken1)
  }
})
function toggle () { // eslint-disable-line no-unused-vars
  $('.tab-content').find('.tab-pane').css('display', 'none')
  $('.tab-content').find('.tab-pane').css('opacity', 0)
  $(`#${($(this).attr('aria-controls'))}`).css('display', 'block')
  $(`#${($(this).attr('aria-controls'))}`).css('opacity', 1)
  $('.tab-content').eq(1).find('.tab-pane').css('display', 'block')
  $('.tab-content').eq(1).find('.tab-pane').css('opacity', 1)
}
