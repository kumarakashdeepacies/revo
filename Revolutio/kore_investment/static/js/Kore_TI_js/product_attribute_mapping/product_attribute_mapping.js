// Product Mapping
/* global Option,measureMaster */

$('.select2bs4').select2()
$('.duallistbox').bootstrapDualListbox()
const ctoken = document.getElementById('form1').elements[0].value
$.ajaxSetup({
  beforeSend: function (xhr, settings) {
    xhr.setRequestHeader('X-CSRFToken', ctoken)
  }
})
$('#error_exception_modal').on('hidden.bs.modal', function (e) {
  $(this).find('.modal-body').empty()
})
$(document).ready(function () {
  $('card0').ready(function () {
    $('.cardheader0').on('click', function (e) {
      $('.cardbody0').toggle()
      $('.cardfooter0').toggle()
      String($('.cardbody0').css('display')) === 'none' && $('.cardheader0').find('i.fa-minus').addClass('fa-plus').removeClass('fa-minus').end()
      String($('.cardbody0').css('display')) === 'block' && $('.cardheader0').find('i.fa-plus').addClass('fa-minus').removeClass('fa-plus').end()
    })
  })
  $('card1').ready(function () {
    $('.cardheader1').on('click', function (e) {
      $('.cardbody1').toggle()
      $('.cardfooter1').toggle()
      String($('.cardbody1').css('display')) === 'none' && $('.cardheader1').find('i.fa-minus').addClass('fa-plus').removeClass('fa-minus').end()
      String($('.cardbody1').css('display')) === 'block' && $('.cardheader1').find('i.fa-plus').addClass('fa-minus').removeClass('fa-plus').end()
    })
  })
  $('card2').ready(function () {
    $('.cardheader2').on('click', function () {
      $('.cardbody2').toggle()
      $('.cardfooter2').toggle()
      String($('.cardbody2').css('display')) === 'none' && $('.cardheader2').find('i.fa-minus').addClass('fa-plus').removeClass('fa-minus').end()
      String($('.cardbody2').css('display')) === 'block' && $('.cardheader2').find('i.fa-plus').addClass('fa-minus').removeClass('fa-plus').end()
    })
  })
  $('card4').ready(function () {
    $('.cardheader4').on('click', function () {
      $('.cardbody4').toggle()
      $('.cardfooter4').toggle()
      String($('.cardbody4').css('display')) === 'none' && $('.cardheader4').find('i.fa-minus').addClass('fa-plus').removeClass('fa-minus').end()
      String($('.cardbody4').css('display')) === 'block' && $('.cardheader4').find('i.fa-plus').addClass('fa-minus').removeClass('fa-plus').end()
    })
  })
  const allFormElements = document.querySelectorAll('.dynamicForm')
  let filterInputDuallistbox // eslint-disable-line no-unused-vars
  let saveProdButton // eslint-disable-line no-unused-vars
  let saveButton // eslint-disable-line no-unused-vars
  let defaultProdAttrButton // eslint-disable-line no-unused-vars
  let measureButton // eslint-disable-line no-unused-vars
  function currencySelected (e) {
    const productGroup = $('#id_product_group').val()
    const country = $('#id_country').val()
    const currency = $('#id_currency').val()
    $.ajax({
      url: '/users/homePage/showProd/',
      data: { countrySelected: country, currencySelected: currency, productGroupSelected: productGroup, ajaxCallNo: 'minusTwo' },
      type: 'POST',
      dataType: 'json',
      success: function (data) {
        $('#id_product_subtype').empty()
        for (let i = 0; i < data.data.length; i++) {
          $('#id_product_subtype').append(new Option(data.data[i], data.data[i]))
        };
        $('#id_product_subtype').trigger('change')
      },
      error: function () {
        Swal.fire({icon: 'error',text: 'Error! Please try again.'});
      }
    })
  }
  function saveProdFunction (event) {
    const productName = $('#id_product_name').val()
    const productComments = $('#id_product_comments').val()
    const productGroup = $('#id_product_group').val()
    const productSubType = $('#id_product_subtype').val()
    const productCountry = $('#id_country').val()
    const productCurrency = $('#id_currency').val()
    const productActive = $('#id_active:checked').val() ? 1 : 0
    $.ajax({
      url: '/users/homePage/showProd/',
      data: {
        product_name: productName,
        product_comments: productComments,
        active: productActive,
        product_group: productGroup,
        product_subtype: productSubType,
        country: productCountry,
        currency: productCurrency,
        ajaxCallNo: 'zero'
      },
      type: 'POST',
      dataType: 'json',
      success: function (data) {
        if (String(data.condition) === 'success') {
          const newOption = new Option(data.data.product_name, data.data.product_name, !1, !1)
          $('#selectProduct').append(newOption).trigger('change')
          $('#selectProduct').val(data.data.product_name).trigger('select2:select')
          $('#card0').addClass('collapsed-card')
          $('#card0 > div.card-body').css('display', 'none')
          $('#card0 > div.card-footer').css('display', 'none')
          $('#card0').find('i.fa-minus').addClass('fa-plus').removeClass('fa-minus')
          $('#card0').find('i.fa-check-circle').css('display', 'inline-block')
          $('#card1').removeClass('collapsed-card')
          $('#card1 > div.card-body').css('display', 'block')
          $('#card1 > div.card-footer').css('display', 'block')
          $('#card1').find('i.fa-plus').addClass('fa-minus').removeClass('fa-plus')
        } else {
          if (String(data.condition) === 'duplicate') {
            $('#error_exception_modal').find('.modal-body').append('<b>Product Name already exists</b>')
            $('#error_exception_modal').modal('show')
          }
        }
      },
      error: function () {
        Swal.fire({icon: 'error',text: 'Error! Please try again.'});
      }
    })
  }
  function productSelected (event) {
    var measureMasterCopy // eslint-disable-line no-var
    var measureMasterList // eslint-disable-line no-var
    const selectedProduct = $('#selectProduct').find(':selected')[0].value
    let hiddenSelectDropdown = document.getElementById('selectProductAttributes')
    hiddenSelectDropdown.options.length > 0 && $('#selectProductAttributes').empty()
    $('.duallistbox').bootstrapDualListbox('refresh', !0)
    allFormElements.forEach(function (elem) {
      elem.style.display = 'none'
    })
    $('#poolOfSelectedMeasureNames').empty()
    $('#poolOfSelectedMeasureNames').css('display', 'none')
    $('#labelpoolOfSelectedMeasureNames').css('display', 'none')
    if (selectedProduct) {
      $.ajax({
        url: '/users/homePage/showProd/',
        data: { productName: selectedProduct, ajaxCallNo: 'one' },
        type: 'POST',
        dataType: 'json',
        success: function (data) {
          if (String(data.data) !== 'noDataPresent') {
            Swal.fire({icon: 'warning',text:"Attributes have already been assigned to this product." });
            hiddenSelectDropdown = document.getElementById('selectProductAttributes')
            for (let i = 0; i < data.dataSelected.length; i++) {
              const attribute = data.dataSelected[i].attributeName.replace(/_/g, ' ')
              if (
                ($('#selectProductAttributes').append(new Option(attribute, data.dataSelected[i].attributeName, !1, !0)),
                String(data.dataSelected[i].mandatoryAndDefault[0]) === 'Y' && $('#selectProductAttributes').find(`option[value='${data.dataSelected[i].attributeName}']`).prop('disabled', !0),
                String(data.dataSelected[i].mandatoryAndDefault[1]) === 'Y' && String(data.dataSelected[i].defaultValue) !== 'NOTSPECIFIED')
              ) {
                const divTag = $(`[id='${data.dataSelected[i].attributeName}']`)
                if (divTag.find('select').length === 1) {
                  const sTag = divTag.find('select')
                  sTag.val(data.dataSelected[i].defaultValue).trigger('select2:select')
                  sTag.trigger('change')
                }
                if (divTag.find('input').length === 1) {
                  const iTag = divTag.find('input')
                  iTag.val(data.dataSelected[i].defaultValue)
                }
                divTag.css('display', 'block')
              }
            }
            for (let i = 0; i < data.dataNotSelected.length; i++) {
              const attribute = data.dataNotSelected[i].attributeName.replace(/_/g, ' ')
              $('#selectProductAttributes').append(new Option(attribute, data.dataNotSelected[i].attributeName, !1, !1))
            }
            if (String(data.measures) !== 'MEASURESNOTSELECTED') {
              measureMasterCopy = measureMaster
              measureMasterList = []
              $('#selectMeasureType').val('').trigger('select2:select')
              $('#selectMeasureType').trigger('change')
              for (let i = 0; i < measureMasterCopy.length; i++) {
                for (let j = 0; j < data.measures.length; j++) {
                  const name = data.measures[j].name
                  const valueList = data.measures[j].value
                  if (String(name) === String(measureMasterCopy[i].name)) {
                    for (let k = 0; k < measureMasterCopy[i].value.length; k++) {
                      for (let m = 0; m < valueList.length; m++) {
                        if (String(valueList[m]) === String(measureMasterCopy[i].value[k])) {
                          measureMasterCopy[i].value.splice(k, 1)
                          measureMasterList.push({ name: name, value: [valueList[m]] })
                          k--
                        }
                      }
                    }
                  }
                }
                for (let i = 0; i < measureMasterList.length; i++) {
                  for (let k = 0; k < measureMasterList[i].value.length; k++) {
                    $(`<button type='button' class='btn btn-dark m-1' name='${measureMasterList[i].value[k]}'\n                            value='${measureMasterList[i].value[k]}'>\n                            ${measureMasterList[i].value[k]}</button>`
                    ).appendTo('#poolOfSelectedMeasureNames')
                  }
                }
                $('#poolOfSelectedMeasureNames').css('display', 'block')
              }
              $('#card2').removeClass('collapsed-card')
              $('#card2 > div.card-body').css('display', 'block')
              $('#card2 > div.card-footer').css('display', 'block')
              $('#card2').find('i.fa-plus').addClass('fa-minus').removeClass('fa-plus')
              $('#card4').removeClass('collapsed-card')
              $('#card4 > div.card-body').css('display', 'block')
              $('#card4 > div.card-footer').css('display', 'block')
              $('#card4').find('i.fa-plus').addClass('fa-minus').removeClass('fa-plus')
              $('.duallistbox').bootstrapDualListbox('refresh', !0)
            } else {
              Swal.fire({icon: 'success',text: "New Product Assignment"});
              for (let i = 0; i < data.actualData.length; i++) {
                const attribute = data.actualData[i][0].replace(/_/g, ' ')
                if (String(data.actualData[i][1][0]) === 'Y') {
                  $('#selectProductAttributes').append(new Option(attribute, data.actualData[i][0], !1, !0))
                  $('#selectProductAttributes').find(`option[value='${data.actualData[i][0]}']`).prop('disabled', !0)
                } else if (String(data.actualData[i][1][0]) === 'N') {
                  $('#selectProductAttributes').append(new Option(attribute, data.actualData[i][0], !1, !1))
                }
              }
              $('#card2').addClass('collapsed-card')
              $('#card2 > div.card-body').css('display', 'none')
              $('#card2 > div.card-footer').css('display', 'none')
              $('#card2').find('i.fa-plus').addClass('fa-plus').removeClass('fa-minus')
              $('#card3').addClass('collapsed-card')
              $('#card3 > div.card-body').css('display', 'none')
              $('#card3 > div.card-footer').css('display', 'none')
              $('#card3').find('i.fa-plus').addClass('fa-plus').removeClass('fa-minus')
              $('.duallistbox').bootstrapDualListbox('refresh', !0)
            }
          }
        },
        error: function () {
          Swal.fire({icon: 'error',text: 'Error! Please try again.'});
        }
      })
    } else {
      measureMasterCopy = measureMaster
      measureMasterList = []
      $('#selectMeasureType').val('').trigger('select2:select')
      $('#selectMeasureType').trigger('change')
    }
  }
  function prodProdAttrMapping (event) {
    const prodAttributes = []
    $('#bootstrap-duallistbox-selected-list_')
      .find('option')
      .each(function () {
        $(this).prop('disabled', !1)
      })
    const selectProductDropdown = document.getElementById('selectProduct')
    const selectedProduct = selectProductDropdown.options[selectProductDropdown.selectedIndex].value
    const selectedProdAttrs = document.getElementById('bootstrap-duallistbox-selected-list_')
    for (let i = 0; i < selectedProdAttrs.options.length; i++) {
      prodAttributes.push(selectedProdAttrs.options[i].value)
    }
    selectedProdAttrs.multiple = !0
    for (let i = 0; i < selectedProdAttrs.options.length; i++) {
      selectedProdAttrs.options[i].selected = !0
    }
    $.ajax({
      url: '/users/homePage/showProd/',
      data: { productName: selectedProduct, productAttributes: prodAttributes, ajaxCallNo: 'two' },
      type: 'POST',
      dataType: 'json',
      success: function (data) {
        allFormElements.forEach(function (elem) {
          elem.style.display = 'none'
        })
        $('#card1').addClass('collapsed-card')
        $('#card1 > div.card-body').css('display', 'none')
        $('#card1 > div.card-footer').css('display', 'none')
        $('#card1').find('i.fa-minus').addClass('fa-plus').removeClass('fa-minus')
        $('#card1').find('i.fa-check-circle').css('display', 'inline-block')
        $('#card2').removeClass('collapsed-card')
        $('#card2 > div.card-body').css('display', 'block')
        $('#card2 > div.card-footer').css('display', 'block')
        $('#card2').find('i.fa-plus').addClass('fa-minus').removeClass('fa-plus')
        for (let i = 0; i < data.data.length; i++) {
          const dispDivTags = document.getElementById(data.data[i])
          dispDivTags.style.display = 'block'
          dispDivTags.setAttribute('tagSelected', 'YES')
        }
      },
      error: function () {
        Swal.fire({icon: 'error',text: 'Error! Please try again.'});
      }
    })
  }
  function openMeasureAssignment (event) {
    $('#card2').addClass('collapsed-card')
    $('#card2 > div.card-body').css('display', 'none')
    $('#card2 > div.card-footer').css('display', 'none')
    $('#card2').find('i.fa-minus').addClass('fa-plus').removeClass('fa-minus')
    $('#card2').find('i.fa-check-circle').css('display', 'inline-block')
    $('#card4').removeClass('collapsed-card')
    $('#card4 > div.card-body').css('display', 'block')
    $('#card4 > div.card-footer').css('display', 'block')
    $('#card4').find('i.fa-plus').addClass('fa-minus').removeClass('fa-plus')
    const allFormElements = document.querySelectorAll('.dynamicForm')
    const sendDefaultValuesAjaxCall = []
    allFormElements.forEach(function (elem) {
      if (elem.hasAttribute('tagSelected')) {
        elem.removeAttribute('tagSelected')
        const divTag = $(`[id='${elem.id}']`)
        if (divTag.find('select').length === 1) {
          const sTag = divTag.find('select')
          const sTagName = sTag.attr('name')
          const sTagValue = sTag.val()
          sendDefaultValuesAjaxCall.push({ key: sTagName, value: sTagValue })
        }
        if (divTag.find('input').length === 1) {
          const iTag = divTag.find('input')
          const iTagName = iTag.attr('name')
          const iTagValue = iTag.val()
          sendDefaultValuesAjaxCall.push({ key: iTagName, value: iTagValue })
        }
      }
    })
    const selectProductDropdown = document.getElementById('selectProduct')
    const selectedProduct = selectProductDropdown.options[selectProductDropdown.selectedIndex].value
    $.ajax({
      url: '/users/homePage/showProd/',
      data: { productName: selectedProduct, defaultAttributeValues: JSON.stringify(sendDefaultValuesAjaxCall), ajaxCallNo: 'three' },
      type: 'POST',
      dataType: 'json',
      success: function (data) {},
      error: function () {
        Swal.fire({icon: 'error',text: 'Error! Please try again.'});
      }
    })
  }
  function saveMeasureAssignment (event) { // eslint-disable-line no-unused-vars
    const measuresSelectedAjaxCall = []
    const selectProductDropdown = document.getElementById('selectProduct')
    const selectedProduct = selectProductDropdown.options[selectProductDropdown.selectedIndex].value
    $('.classMeasure')
      .find('input')
      .each(function () {
        const id = $(this).attr('id')
        $(this).is(':checked') && measuresSelectedAjaxCall.push(id)
      })
    $.ajax({
      url: '/users/homePage/showProd/',
      data: { productName: selectedProduct, measuresSelected: JSON.stringify(measuresSelectedAjaxCall), ajaxCallNo: 'four' },
      type: 'POST',
      dataType: 'json',
      success: function (data) {
        Swal.fire({icon: 'success',text: 'Operation completed successfully!'});
      },
      error: function () {
        Swal.fire({icon: 'error',text: 'Error! Failure in executing the operation. Please try again.'});
      }
    })
  }
  allFormElements.forEach(function (elem) {
    elem.style.display = 'none'
  })
  document.querySelectorAll('.filter').forEach(function (elem) {
    elem.placeholder = 'Select'
  })
  $('#id_currency').on('select2:select', currencySelected)
  document.getElementById('saveProd').addEventListener('click', saveProdFunction)
  $('#selectProduct').on('select2:select', productSelected)
  document.getElementById('saveProdAttr').addEventListener('click', prodProdAttrMapping)
  document.getElementById('saveDefaultProdAttrValues').addEventListener('click', openMeasureAssignment)
  document.getElementById('saveMeasures').addEventListener('click', saveButtonMeasureAssignment)
  $('#selectMeasureType').on('select2:select', measureTypeSelected)
  let measureMasterCopy = measureMaster
  let measureMasterList = []
  function measureTypeSelected () {
    if ($('#selectMeasureType').val()) {
      $('#toggleArrow').css('display', 'block')
      $('#selectMeasureNameDivTag').css('display', 'block')
      const selectedMeasureType = $('#selectMeasureType').val()
      $('#selectMeasureName').empty()
      for (let i = 0; i < measureMasterCopy.length; i++) {
        if (String(measureMasterCopy[i].name) === String(selectedMeasureType)) {
          for (let k = 0; k < measureMasterCopy[i].value.length; k++) {
            if (String(measureMasterCopy[i].product_subtype[k]) === 'Fixed Coupon Bond') {
              $('#selectMeasureName').append(new Option(measureMasterCopy[i].value[k], measureMasterCopy[i].value[k]))
            }
          }
        }
      }
    } else {
      $('#selectMeasureNameDivTag').css('display', 'none')
      $('#toggleArrow').css('display', 'none')
    }
  }
  function measureNameSelected (e) {
    if ($('#poolOfSelectedMeasureNames').find('button').length === 0) {
      $('#poolOfSelectedMeasureNames').css('display', 'block')
    } else {
      $('#labelpoolOfSelectedMeasureNames').css('display', 'block')
    }
    const selectedMeasureType = $('#selectMeasureType').val()
    const optionTagSelectedValue = e.target.value
    $(`<button type='button' class='btn btn-dark m-1' name='${optionTagSelectedValue}' value='${optionTagSelectedValue}'>\n${optionTagSelectedValue}</button>`).appendTo('#poolOfSelectedMeasureNames')
    for (let i = 0; i < measureMasterCopy.length; i++) {
      if (String(selectedMeasureType) === String(measureMasterCopy[i].name)) {
        for (let k = 0; k < measureMasterCopy[i].value.length; k++) {
          if (String(optionTagSelectedValue) === String(measureMasterCopy[i].value[k])) {
            measureMasterCopy[i].value.splice(k, 1)
            measureMasterList.push({ name: selectedMeasureType, value: [optionTagSelectedValue] })
            k--
            break
          }
        }
      }
    }
    $(`#selectMeasureName option[value='${optionTagSelectedValue}']`).remove()
  }
  function poolOfMeasuresClicked (e) {
    if (String(e.target.nodeName) === 'BUTTON') {
      const clickedMeasureName = e.target.value
      let getMeasureType
      for (let i = 0; i < measureMasterList.length; i++) {
        if (String(measureMasterList[i].value) === String(clickedMeasureName)) {
          getMeasureType = measureMasterList[i].name
          measureMasterList.splice(i, 1)
          break
        }
      }

      for (let i = 0; i < measureMasterCopy.length; i++) {
        if (String(measureMasterCopy[i].name) === getMeasureType) {
          measureMasterCopy[i].value.push(clickedMeasureName)
          break
        }
      }
      $(`button[name='${clickedMeasureName}']`).remove()
      $('#poolOfSelectedMeasureNames').find('button').length === 0 && $('#poolOfSelectedMeasureNames').css('display', 'none') && $('#labelpoolOfSelectedMeasureNames').css('display', 'none')
      $('#selectMeasureType').trigger('select2:select')
    }
  }
  function allMeasuresSelected (e) {
    $('#poolOfSelectedMeasureNames').find('button').length === 0 && $('#poolOfSelectedMeasureNames').css('display', 'block') && $('#labelpoolOfSelectedMeasureNames').css('display', 'block')
    for (let i = 0; i < measureMasterCopy.length; i++) {
      for (let k = 0; k < measureMasterCopy[i].value.length; k++) {
        measureMasterList.push({ name: measureMasterCopy[i].name, value: [measureMasterCopy[i].value[k]] })
        $(`<button type='button' class='btn btn-dark m-1' name='${measureMasterCopy[i].value[k]}' value='${measureMasterCopy[i].value[k]}'>\n${measureMasterCopy[i].value[k]}</button>`).appendTo(
          '#poolOfSelectedMeasureNames'
        )
        measureMasterCopy[i].value.splice(k, 1)
        k--
      }
    }
    $('#selectMeasureName').empty()
  }
  function saveButtonMeasureAssignment (e) {
    const selectedProduct = $('#selectProduct').val()
    $.ajax({
      url: '/users/homePage/showProd/',
      data: { productName: selectedProduct, measuresSelected: JSON.stringify(measureMasterList), ajaxCallNo: 'four' },
      type: 'POST',
      dataType: 'json',
      success: function (data) {
        Swal.fire({icon: 'success',text: 'Operation Completed successfully!'});
        measureMasterCopy = measureMaster
        measureMasterList = []
      },
      error: function () {
        Swal.fire({icon: 'error',text: 'Error! Failure in executing the operation. Please try again.'});
      }
    })
  }
  $('#selectMeasureName').on('change', measureNameSelected)
  $('#poolOfSelectedMeasureNames').on('click', poolOfMeasuresClicked)
  document.getElementById('selectAllMeasures').addEventListener('click', allMeasuresSelected)
})
