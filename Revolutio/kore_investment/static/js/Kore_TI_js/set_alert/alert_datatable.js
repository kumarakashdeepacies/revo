/* eslint-disable no-tabs */
/* eslint-disable comma-dangle */
$(document).ready(function () {
  $('#example11 thead tr').eq(0).clone(true).appendTo('#example11 thead')
  $('#example11 thead tr').eq(1).find('th').css('background-color', 'white')
  $('#example11 thead tr').eq(1).find('th').css('color', 'white')
  // $('#example11 thead tr').eq(1).find('th').removeClass("sorting");
  // $('#example11 thead tr').eq(1).find('th').removeClass("sorting_asc");
  // $('#example11 thead tr').eq(1).find('th').removeClass("sorting_desc");
  // $('#example11 thead tr').eq(1).find('th').removeClass("dt-center");
  // $('#example11 thead tr').eq(1).find('th').removeAttr("aria-label");
  // $('#example11 thead tr').eq(1).find('th').removeAttr("aria-sort");
  // $('#example11 thead tr').eq(1).find('th').eq(0).innerHTML='&nbsp;';
  // $('#example11 thead tr').eq(1).find('th').eq(0).empty();
  const table = $('#example11').DataTable()
  $('#example11 thead tr').eq(1).find('th').slice(0,6).each(function (i) {
    $(this).addClass('dt-center')
    const title = $(this).text()
    if ($(this).index() !== 0) {
      $(this).html(
        '<input type="text" style="text-align:center;border-bottom:none;border:1px solid #ced4da;width:190px;font-size:12px;background-color:white;color:black;" placeholder="Search ' +
					title +
					'" />'
      )
    }

    $('input', this).on('keyup change', function () {
      if (table.column(i).search() !== this.value) {
        table.column(i).search(this.value).draw()
      }
    })
  })

  const tablealert = $('#example11').DataTable({
    autoWidth: true,
    scrollY: '50vh',
    scrollCollapse: true,
    scrollX: '110%',
    orderCellsTop: true,
    // fixedHeader: true,
    responsive: true,
    colReorder: {
      fixedColumnsLeft: 1,
    },
    stateSave: true,
    deferRender: true,
    paging: true,
    lengthMenu: [
      [1, 5, 50, -1],
      [1, 5, 50, 'All'],
    ],
    stripeClasses: false,
    pageLength: 50,
    dom: 'lfBrtip',
    sScrollX: '100%',
    buttons: [
      {
        extend: 'collection',
        text: 'Export',
        buttons: [
          {
            extend: 'copy',
            title: '',
            exportOptions: {
              columns: ':visible:not(.noVis)',
            },
          },
          {
            extend: 'excel',
            title: '',
            exportOptions: {
              columns: ':visible:not(.noVis)',
            },
          },
          {
            extend: 'csv',
            title: '',
            exportOptions: {
              columns: ':visible:not(.noVis)',
            },
          },
          {
            extend: 'pdf',
            title: '',
            exportOptions: {
              columns: ':visible:not(.noVis)',
            },
          },
        ],
      },
      {
        extend: 'colvis',
        className: 'scroller',
        // collectionLayout: 'four-column',
        // columns: ':not(.noVis)'
      },
    ],
    columnDefs: [
      {
        targets: '_all',
        className: 'dt-center allColumnClass all',
      },
      {
        targets: 0,
        className: 'noVis',
      },
      // { 'visible': false, 'targets': [1,3] }
    ],
  })
  // var table = $("#example11").DataTable({
  //   // "paging": false,
  //   // "ordering": false,
  //   // "info": false,
  //   dom: 'Bfrtip',
  //   buttons: [
  //   'colvis'

  //   ],
  //   columnDefs: [
  //     {
  //       'targets': [0, 4],
  //       'searchable': false,
  //     },
  //     {
  //       targets: "_all",
  //       orderable: false
  //     }, {
  //       targets: [0],
  //       orderable: false
  //     }
  //   ],

  // });
  // eslint-disable-next-line no-use-before-define
  $('#example11_expand').on('click', fnShowHide11)
  let allowSaveTemplate = false
  // document.getElementById('example11_expand').addEventListener('click', fnShowHide_11)
  function fnShowHide11 () {
    if (this.value === 'Expand') {
      this.value = 'Contract'
      document.getElementById('example11_expand').innerHTML = 'Contract'
      allowSaveTemplate = true
      tablealert.columns('.allColumnClass').visible(allowSaveTemplate)
      tablealert.columns.adjust().draw(false)
      tablealert.state.save()
    } else {
      this.value = 'Expand'
      document.getElementById('example11_expand').innerHTML = 'Expand'
      tablealert.columns('.allColumnClass').visible(false)
      allowSaveTemplate = true
      tablealert.columns([0, 1]).visible(allowSaveTemplate, false)
      tablealert.columns.adjust().draw(false)
      tablealert.state.save()
    }
  }
})
