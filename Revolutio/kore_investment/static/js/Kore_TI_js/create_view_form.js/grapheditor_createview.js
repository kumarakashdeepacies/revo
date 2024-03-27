// eslint-disable-next-line no-unused-vars
/* global scriptMastere_id,scriptMaster,element_id */
/* eslint-disable */
let itemID
var component
var scriptMaster = ''
var scriptMastere_id = {}
var element_id = [];
/* eslint-enable */
$('#gjs').find('.gjs-toolbar').find('div').eq(0).append('<div class="fa fa-clone setting gjs-toolbar-item" style="margin-left:15px;"></div>')
// eslint-disable-next-line no-var,no-unused-vars
var openModal = function () {
  $.ajaxSetup({
    beforeSend: function (xhr, settings) {
      // eslint-disable-next-line no-undef
      xhr.setRequestHeader('X-CSRFToken', ctoken)
    }
  })
  // eslint-disable-next-line no-undef
  component = editor.getSelected()
  if (String(component.getTrait('title').attributes.value) === 'create view') {
    $('#ProcessModal').modal('show')
    itemID = ('whiteSpace=wrap' + Math.random()).replace('.', '').replace('=', '')
  } else if (String(component.getTrait('title').attributes.value) === 'computation') {
    $('#computationModal').modal('show')
  } else if (String(component.getTrait('title').attributes.value) === 'analysis') {
    $('#analysis').modal('show')
  } else if (String(component.getTrait('title').attributes.value) === 'listview') {
    $('#listview').modal('show')
  } else if (String(component.getTrait('title').attributes.value) === 'upload') {
    $('#upload').modal('show')
  }
}
$('.select2').select2()
