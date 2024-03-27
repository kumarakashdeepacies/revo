/* eslint camelcase: ["error", {ignoreGlobals: true,properties:'never'}] */
/* eslint valid-typeof: ["error", { "requireStringLiterals": true }] */

let currentLoginTrailViewName = "Default";
let loginTrailFilterApplied = false;
let currentActivityTrailViewName = "Default";
let activityTrailFilterApplied = false;
let currentDataOpsTrailViewName = "Default";
let dataOpsTrailFilterApplied = false;

function fetchCustomisationParameters() {
  var daterange_list = new Array();
  var dataselected = $(`#reportdate2`).val();

  if (dataselected == "Custom") {
    daterange_list.push("datetime");
    daterange_list.push(dataselected),
      daterange_list.push($(`.logindetails`).val());
  } else if (dataselected == "Advanced") {
    var rec_dic = {};
    if ($(".recpattern").val() == "Daily") {
      rec_dic["type"] = "Daily";
      if (
        $("input[name=data_choice1]:checked", ".daily_div").val() == "Everyday"
      ) {
        rec_dic["daily_day"] = "Everyday";
        rec_dic["rec_daily_days_no"] = $(".rec_daily_days_no").val();
      } else {
        rec_dic["daily_day"] = "Everyweekday";
        rec_dic["rec_daily_days_no"] = "";
      }
    } else if ($(".recpattern").val() == "Weekly") {
      rec_dic["type"] = "Weekly";
      rec_dic["rec_weekly_days_no"] = $(".rec_weekly_days_no").val();
      rec_dic["rec_weekly_days"] = $(".rec_weekly_days").val();
    } else if ($(".recpattern").val() == "Monthly") {
      rec_dic["type"] = "Monthly";
      rec_dic["rec_monthly_days_no"] = $(".rec_monthly_days_no").val();
      rec_dic["rec_monthly_months_no"] = $(".rec_monthly_months_no").val();
    } else if ($(".recpattern").val() == "Yearly") {
      rec_dic["type"] = "Yearly";
      rec_dic["rec_yearly_year_no"] = $(".rec_yearly_year_no").val();
      rec_dic["rec_yearly_month_no"] = $(".rec_yearly_month_no").val();
      rec_dic["rec_yearly_day_no"] = $(".rec_yearly_day_no").val();
    }

    rec_dic["daterange"] = $(".logindtpicker").val();
    rec_dic["end_date"] = $(
      "input[name=data_choice2]:checked",
      ".range_div"
    ).val();
    if (
      $("input[name=data_choice2]:checked", ".range_div").val() == "endafter"
    ) {
      rec_dic["end_no_occ"] = $(".rec_occurr").val();
    } else if (
      $("input[name=data_choice2]:checked", ".range_div").val() == "onenddate"
    ) {
      rec_dic["end_no_occ"] = "end";
    } else {
      rec_dic["end_no_occ"] = "";
    }

    daterange_list.push("datetime");
    daterange_list.push(dataselected);
    daterange_list.push(rec_dic);
  } else {
    daterange_list.push("datetime");
    daterange_list.push(dataselected);
  }
  return daterange_list;
}

function fetchCustomisationParametersActivityTrail() {
  var daterange_list = new Array();
  var dataselected = $(`#reportdate5`).val();

  if (dataselected == "Custom") {
    daterange_list.push("datetime");
    daterange_list.push(dataselected),
      daterange_list.push($(`.actdetails`).val());
  } else if (dataselected == "Advanced") {
    var rec_dic = {};
    if ($(".recpattern_act").val() == "Daily") {
      rec_dic["type"] = "Daily";
      if (
        $("input[name=data_choice1]:checked", ".daily_div_act").val() ==
        "Everyday"
      ) {
        rec_dic["daily_day"] = "Everyday";
        rec_dic["rec_daily_days_no"] = $(".rec_daily_days_no_act").val();
      } else {
        rec_dic["daily_day"] = "Everyweekday";
        rec_dic["rec_daily_days_no"] = "";
      }
    } else if ($(".recpattern_act").val() == "Weekly") {
      rec_dic["type"] = "Weekly";
      rec_dic["rec_weekly_days_no"] = $(".rec_weekly_days_no_act").val();
      rec_dic["rec_weekly_days"] = $(".rec_weekly_days_act").val();
    } else if ($(".recpattern_act").val() == "Monthly") {
      rec_dic["type"] = "Monthly";
      rec_dic["rec_monthly_days_no"] = $(".rec_monthly_days_no_act").val();
      rec_dic["rec_monthly_months_no"] = $(".rec_monthly_months_no_act").val();
    } else if ($(".recpattern_act").val() == "Yearly") {
      rec_dic["type"] = "Yearly";
      rec_dic["rec_yearly_year_no"] = $(".rec_yearly_year_no_act").val();
      rec_dic["rec_yearly_month_no"] = $(".rec_yearly_month_no_act").val();
      rec_dic["rec_yearly_day_no"] = $(".rec_yearly_day_no_act").val();
    }

    rec_dic["daterange"] = $(".actdtpicker").val();
    rec_dic["end_date"] = $(
      "input[name=data_choice2]:checked",
      ".range_div_act"
    ).val();
    if (
      $("input[name=data_choice2]:checked", ".range_div_act").val() ==
      "endafter"
    ) {
      rec_dic["end_no_occ"] = $(".rec_occurr_act").val();
    } else if (
      $("input[name=data_choice2]:checked", ".range_div_act").val() ==
      "onenddate"
    ) {
      rec_dic["end_no_occ"] = "end";
    } else {
      rec_dic["end_no_occ"] = "";
    }

    daterange_list.push("datetime");
    daterange_list.push(dataselected);
    daterange_list.push(rec_dic);
  } else {
    daterange_list.push("datetime");
    daterange_list.push(dataselected);
  }
  return daterange_list;
}

function fetchCustomisationParametersDataOpsTrail() {
  var daterange_list = new Array();
  var dataselected = $(`#reportdate3`).val();

  if (dataselected == "Custom") {
    daterange_list.push("datetime");
    daterange_list.push(dataselected),
      daterange_list.push($(`.opactdetails`).val());
  } else if (dataselected == "Advanced") {
    var rec_dic = {};
    if ($(".recpattern_ops").val() == "Daily") {
      rec_dic["type"] = "Daily";
      if (
        $("input[name=data_choice1]:checked", ".daily_div_ops").val() ==
        "Everyday"
      ) {
        rec_dic["daily_day"] = "Everyday";
        rec_dic["rec_daily_days_no"] = $(".rec_daily_days_no_ops").val();
      } else {
        rec_dic["daily_day"] = "Everyweekday";
        rec_dic["rec_daily_days_no"] = "";
      }
    } else if ($(".recpattern_ops").val() == "Weekly") {
      rec_dic["type"] = "Weekly";
      rec_dic["rec_weekly_days_no"] = $(".rec_weekly_days_no_ops").val();
      rec_dic["rec_weekly_days"] = $(".rec_weekly_days_ops").val();
    } else if ($(".recpattern_ops").val() == "Monthly") {
      rec_dic["type"] = "Monthly";
      rec_dic["rec_monthly_days_no"] = $(".rec_monthly_days_no_ops").val();
      rec_dic["rec_monthly_months_no"] = $(".rec_monthly_months_no_ops").val();
    } else if ($(".recpattern_ops").val() == "Yearly") {
      rec_dic["type"] = "Yearly";
      rec_dic["rec_yearly_year_no"] = $(".rec_yearly_year_no_ops").val();
      rec_dic["rec_yearly_month_no"] = $(".rec_yearly_month_no_ops").val();
      rec_dic["rec_yearly_day_no"] = $(".rec_yearly_day_no_ops").val();
    }

    rec_dic["daterange"] = $(".ops_actdtpicker").val();
    rec_dic["end_date"] = $(
      "input[name=data_choice2]:checked",
      ".range_div_ops"
    ).val();
    if (
      $("input[name=data_choice2]:checked", ".range_div_ops").val() ==
      "endafter"
    ) {
      rec_dic["end_no_occ"] = $(".rec_occurr_ops").val();
    } else if (
      $("input[name=data_choice2]:checked", ".range_div_ops").val() ==
      "onenddate"
    ) {
      rec_dic["end_no_occ"] = "end";
    } else {
      rec_dic["end_no_occ"] = "";
    }

    daterange_list.push("datetime");
    daterange_list.push(dataselected);
    daterange_list.push(rec_dic);
    daterange_list.push(1);
  } else {
    daterange_list.push("datetime");
    daterange_list.push(dataselected);
  }
  return daterange_list;
}

// Handler for User Login insights
function viewLoginTrailDetails(viewName = "Default") {
  if (viewName != currentLoginTrailViewName || !loginTrailFilterApplied) {
    // Update global variables to record the change
    currentLoginTrailViewName = viewName;
    loginTrailFilterApplied = true;
    $("#examplereportDiv").attr("data-active-view", viewName);

    if (viewName == "Default") {
      // Display particular containers
      $("#examplereport_wrapper").css("display", "none");
      $("#examplereportRollUp_wrapper").css("display", "none");
      $("#examplereportRollUp").css("display", "none");
      $("#custom-download-btn1 .buttonfooter").css("display", "");

      // Destroy existing DataTable
      if ($.fn.dataTable.isDataTable("#examplereport")) {
        $("#examplereport").DataTable().clear().destroy();
      }

      // Columns to fetch
      const defaultLoginTrailColumns = [
        { data: "id" },
        { data: "session_id" },
        { data: "user_name" },
        { data: "time_logged_in" },
        { data: "time_logged_out" },
        { data: "logout_type" },
        { data: "ip" },
        { data: "inactivity_time" },
      ];

      // Initialise new DataTable
      $(`#examplereport`)
        .DataTable({
          scrollY: "50vh",
          scrollCollapse: true,
          scrollX: "120%",
          sScrollX: "120%",
          serverSide: true,
          ordering: false,
          orderCellsTop: true,
          responsive: true,
          colReorder: {
            fixedColumnsLeft: 1,
          },
          stateSave: false,
          deferRender: true,
          paging: true,
          lengthMenu: [
            [1, 5, 50, -1],
            [1, 5, 50, "All"],
          ],
          stripeClasses: [],
          pageLength: 50,
          dom: "lfBrtip",
          buttons: [
            "copy",
            "excel",
            "csv",
            {
              extend: 'pdfHtml5',
              title: '',
              // pageSize: 'A4',
              // eslint-disable-next-line no-unused-vars
              customize: function (doc, config) {
                let tableNode
                for (let i = 0; i < doc.content.length; ++i) {
                  if (String(doc.content[i].table) !== 'undefined') {
                    tableNode = doc.content[i]
                    break;
                  }
                }

                const rowIndex = 0
                const tableColumnCount =
                  tableNode.table.body[rowIndex].length

                if (tableColumnCount > 5) {
                  doc.pageOrientation = 'landscape'
                }
                if (tableColumnCount <= 15) {
                  doc.pageSize = 'A4'
                }

                if (tableColumnCount > 15 && tableColumnCount <= 25) {
                  doc.pageSize = 'B3'
                }

                if (tableColumnCount > 25 && tableColumnCount <= 40) {
                  doc.pageSize = 'A1'
                }

                if (tableColumnCount > 40) {
                  doc.pageSize = 'A0'
                }
              },
            },
            "print",
          ],
          language: {
            lengthMenu: "Show entries : ",
          },
          ajax: {
            url: `/users/${app_code2}/${current_dev_mode2}/user_login_insights/`,
            type: "POST",
            data: function (d, settings) {
              const daterange_list = fetchCustomisationParameters();
              d.daterange_list = JSON.stringify(daterange_list);
              d.searchValue = $("#examplereport_filter input").val();
              return d;
            },
          },
          columns: defaultLoginTrailColumns,
          columnDefs: [
            {
              targets: "_all",
              className: "dt-center allColumnClass all",
            },
          ],
          initComplete: function (settings, json) {
            var tableWrapper = $("#examplereport_wrapper");
            var scrollBarWidth =
              tableWrapper.innerWidth() - tableWrapper.prop("clientWidth");
            $(`#examplereport`).DataTable().buttons().container().css("display", "none");
            $("#examplereport .dataTables_scrollBody").css(
              "padding-right",
              scrollBarWidth + "px"
            );
            $(
              "#examplereport > tbody > tr"
            ).css("height", "3rem");
            $(
              "#examplereport .dataTables_scrollBody::-webkit-scrollbar-thumb"
            ).css("height", "50px");
            $(
              "#examplereport .dataTables_scrollBody::-webkit-scrollbar-thumb"
            ).css("background-color", "#ccc");
            $(
              "#examplereport .dataTables_scrollBody::-webkit-scrollbar-thumb"
            ).css("border-radius", "5px");
            $("#examplereport .dataTables_scrollBody::-webkit-scrollbar").css(
              "width",
              "8px"
            );
            var select = $(
              '<select name="examplereport_length" aria-controls="examplereport" class="select2 form-control form-control-sm" style="width: 7rem; margin-left: 0.3rem;"></select>'
            )
              .append('<option value="1">1</option>')
              .append('<option value="5">5</option>')
              .append('<option value="50" selected>50</option>')
              .append('<option value="100">100</option>')
              .append('<option value="-1">All</option>');
            $(".dataTables_length", tableWrapper)
              .empty()
              .append("Show entries : ")
              .append(select);
            $('#examplereport_length > select.select2').select2();
            select.on("select2:select", function () {
              var val = $.fn.dataTable.util.escapeRegex($(this).val());
              if (val === "\\-1") {
                val = -1;
              }
              $("#examplereport").DataTable().page.len(val).draw();
            });

            counts = {};
            counts1 = {};
            graph2value = json.unique_items.graph2Value;
            graph2Key = json.unique_items.graph2Key;
            graph3value = json.unique_items.graph3Value;
            graph3key = json.unique_items.graph3Key;
            json.unique_items.graph1.forEach(function (x) {
              counts[x] = (counts[x] || 0) + 1;
            });
            json.unique_items.graph4.forEach(function (x) {
              counts1[x] = (counts1[x] || 0) + 1;
            });

            key2 = Object.keys(counts1);
            value2 = Object.values(counts1);
            graph4Key = [];
            graph4Value = [];
            arr2 = [];
            for (let m = 0; m < key2.length; m++) {
              arr2.push({ ip: key2[m], counter: value2[m] });
            }

            sorted_by_ip = arr2.sort((a, b) => {
              return b.counter - a.counter;
            });
            for (let l = 0; l < sorted_by_ip.length; l++) {
              if (graph4Key.length < 10) {
                graph4Key.push(sorted_by_ip[l]["ip"]);
                graph4Value.push(sorted_by_ip[l]["counter"]);
              } else break;
            }
            const r = document.querySelector(":root");
            const rs = getComputedStyle(r);
            function toHex(value) {
              return value.toString(16).padStart(2, "0");
            }
            function createLinearShadesArray(color, numShades) {
              const r = parseInt(color.substring(1, 3), 16);
              const g = parseInt(color.substring(3, 5), 16);
              const b = parseInt(color.substring(5, 7), 16);
              const rStep = (255 - r) / (numShades - 1);
              const gStep = (255 - g) / (numShades - 1);
              const bStep = (255 - b) / (numShades - 1);
              return Array(numShades)
                .fill()
                .map((_, i) => {
                  const rShade = Math.round(r + i * rStep);
                  const gShade = Math.round(g + i * gStep);
                  const bShade = Math.round(b + i * bStep);
                  return "#" + toHex(rShade) + toHex(gShade) + toHex(bShade);
                });
            }
            const primecolor =
              rs.getPropertyValue("--primary") ||
              rs.getPropertyValue("--primary-color");
            const primeShadeColorlist = createLinearShadesArray(
              primecolor.trim(),
              11
            );
            $(".avg_session_time").text(`${json.unique_items.graph5} hrs`);

            var trace2 = {
              type: "bar",
              y: Object.keys(counts),
              x: Object.values(counts),
              text: Object.values(counts),
              orientation: "h",
              marker: {
                color: primeShadeColorlist,
                line: {
                  width: 2.5,
                },
              },
            };
            var data1 = [trace2];

            var trace1 = {
              type: "bar",
              y: graph2value.reverse(),
              x: graph2Key,
              text: graph2value,
              marker: {
                color: primeShadeColorlist,
                line: {
                  width: 2.5,
                },
              },
            };
            var data = [trace1];

            var trace4 = {
              type: "bar",
              y: graph4Value.reverse(),
              x: graph4Key.reverse(),

              text: graph4Value,
              marker: {
                color: primeShadeColorlist,
                line: {
                  width: 2.5,
                },
              },
            };
            var data3 = [trace4];

            var trace3 = {
              type: "bar",
              y: graph3value.reverse(),
              x: graph3key,
              text: graph3value,
              marker: {
                color: primeShadeColorlist,
                line: {
                  width: 2.5,
                },
              },
            };
            var data2 = [trace3];

            var layout = {
              font: {
                family: "Arial",
              },
              responsive: true,
              staticPlot: true,
              margin: {
                l: 50,
                r: 50,
                b: 50,
                t: 50,
                pad: 4,
              },
            };
            var layout1 = {
              font: {
                family: "Arial",
              },
              responsive: true,
              staticPlot: true,
              margin: {
                l: 50,
                r: 50,
                b: 50,
                t: 50,
                pad: 4,
              },
            };
            var layout2 = {
              font: {
                family: "Arial",
              },
              responsive: true,
              staticPlot: true,
              margin: {
                l: 50,
                r: 50,
                b: 50,
                t: 50,
                pad: 4,
              },
            };
            var layout3 = {
              font: {
                family: "Arial",
              },
              responsive: true,
              staticPlot: true,
              margin: {
                l: 50,
                r: 50,
                b: 50,
                t: 50,
                pad: 4,
              },
            };
            var config = {
              displayModeBar: false,
            };

            adjustDimensions("totalSessionTimeDiv", "totalSessionTimeDiv1");
            adjustDimensions("NumOfActiveSessions", "NumOfActiveSessions1");
            adjustDimensions("activeSessionTimeDiv", "activeSessionTimeDiv1");
            adjustDimensions("IPsdiv", "IPsdiv1");

            Plotly.newPlot("totalSessionTimeDiv1", data, layout, config);
            Plotly.newPlot("NumOfActiveSessions1", data1, layout1, config);
            Plotly.newPlot("activeSessionTimeDiv1", data2, layout2, config);
            Plotly.newPlot("IPsdiv1", data3, layout3, config);

            $(".plotly-div-unfilter").each(function () {
              const $this = $(this);
              $this.find(".svg-container").css("position", "relative");
            });
            $("#totalSessionTimeDiv1 .cartesianlayer").css(
              "transform",
              "translate(0, -8%)"
            );
            $("#activeSessionTimeDiv1 .cartesianlayer").css(
              "transform",
              "translate(0, -8%)"
            );
            $("#NumOfActiveSessions1 .cartesianlayer").css(
              "transform",
              "translate(16%)"
            );
            $("#IPsdiv1 .cartesianlayer").css(
              "transform",
              "translate(0, -16%)"
            );
          },
          fnDrawCallback: function( oSettings ) {
            $("#user-info1").empty();
              $("#user-info1")
                .append(`<div style="display: flex; align-items: center; width: 95%;">
              <p style="padding-left: 2rem;text-align: left;font-weight: 600;font-size: 1.5rem;margin: 0; flex: 1;">${oSettings.json.unique_items.total_unique_usernames}</p>
              <p style="margin: 0; flex: 2; word-break: break-word;">Total Unique Usernames</p>
            </div>`);
            $("#user-info").empty();
            $("#user-info")
              .append(`<div style="display: flex; align-items: center; width: 95%;">
              <p style="padding-left: 2rem;text-align: left;font-weight: 600;font-size: 1.5rem;margin: 0; flex: 1;">${oSettings.json.unique_items.total_unique_ips}</p>
              <p style="margin: 0; flex: 2; word-break: break-word;">Total Unique IPs</p>
            </div>`);
          }
        })
        .columns.adjust();
      $(`#examplereport`).DataTable().buttons().container().css("display", "none");
      $("#examplereport_filter input").on("change", function () {
        $("#examplereport").DataTable().draw();
      });
    } else {
      // Roll-up view
      if ($("#custom-download-btn1").find(".dropdown").css("display", "flex")) {
        $("#custom-download-btn1").find(".dropdown").css("display", "none");
      }
      $("#custom-download-btn1 .buttonfooter").css("display", "none");
      $("#examplereport_wrapper").css("display", "none");
      $("#examplereportRollUp4_wrapper").css("display", "none");
      $("#examplereportRollUp1_wrapper").css("display", "none");
      $("#examplereportRollUp").css("display", "block");
      $("#examplereportRollUp").find(".main-div-container").hide();
      if ($.fn.dataTable.isDataTable("#examplereportRollUp")) {
        $("#examplereportRollUp").DataTable().clear().destroy();
      }

      // Initialise new DataTable
      var examplereportRollUp = $("#examplereportRollUp")
        .DataTable({
          scrollY: "50vh",
          scrollCollapse: true,
          scrollX: "120%",
          serverSide: true,
          ordering: false,
          orderCellsTop: true,
          responsive: true,
          colReorder: {
            fixedColumnsLeft: 1,
          },
          stateSave: false,
          deferRender: true,
          paging: true,
          lengthMenu: [
            [1, 5, 50, -1],
            [1, 5, 50, "All"],
          ],
          pageLength: 50,
          dom: "lfrtip",
          language: {
            lengthMenu: "Show entries : ",
          },
          ajax: {
            url: `/users/${app_code2}/${current_dev_mode2}/rollup_view_get_data/`,
            type: "POST",
            data: function (d, settings) {
              const dateRangeFilters = fetchCustomisationParameters();
              d.daterange_list = JSON.stringify(dateRangeFilters);
              d.searchValue = $("#examplereportRollUp_filter input").val();
              return d;
            },
            dataSrc: function (json) {
              return json.data;
            },
          },
          sScrollX: "120%",
          columns: [
            {
              data: "user_name",
              className: "dt-center allColumnClass all",
              width: "50px",
              render: function (data, type, row) {
                if (type === "display") {
                  return (
                    '<span class="icon-span"><i class="fa-solid fa-circle-chevron-down" style="float: left; width:16%;"></i></span>' +
                    '<span class="data-span first-column-data">' +
                    data +
                    "</span>"
                  );
                }
                return data;
              },
            },
            {
              data: "session_time",
              className: "dt-center allColumnClass all",
              width: "150px",
            },
            {
              data: "no_of_user",
              className: "dt-center allColumnClass all",
              width: "120px",
            },
          ],
          columnDefs: [
            {
              targets: "_all",
              className: "details-control",
              orderable: false,
              data: null,
              defaultContent: '<i class="fa fa-chevron-right"></i>',
            },
          ],
          initComplete: function (settings, json) {
            var tableWrapper = $("#examplereportRollUp_wrapper");
            var scrollBarWidth =
              tableWrapper.innerWidth() - tableWrapper.prop("clientWidth");
            $("#examplereportRollUp .dataTables_scrollBody").css(
              "padding-right",
              scrollBarWidth + "px"
            );
            $(
              "#examplereportRollUp .dataTables_scrollBody::-webkit-scrollbar-thumb"
            ).css("height", "50px");
            $(
              "#examplereportRollUp .dataTables_scrollBody::-webkit-scrollbar-thumb"
            ).css("background-color", "#ccc");
            $(
              "#examplereportRollUp .dataTables_scrollBody::-webkit-scrollbar-thumb"
            ).css("border-radius", "5px");
            $(
              "#examplereportRollUp .dataTables_scrollBody::-webkit-scrollbar"
            ).css("width", "8px");
            var select = $(
              '<select name="examplereportRollUp_length" aria-controls="examplereportRollUp" class="select2 form-control form-control-sm" style="width: 7rem; margin-left: 0.3rem; "></select>'
            )
              .append('<option value="1">1</option>')
              .append('<option value="5">5</option>')
              .append('<option value="50" selected>50</option>')
              .append('<option value="100">100</option>')
              .append('<option value="-1">All</option>');
            $(".dataTables_length", tableWrapper)
              .empty()
              .append("Show entries : ")
              .append(select);
            $('#examplereportRollUp_length > select.select2').select2();
            select.on("select2:select", function () {
              var val = $.fn.dataTable.util.escapeRegex($(this).val());
              if (val === "\\-1") {
                val = -1;
              }
              $("#examplereportRollUp").DataTable().page.len(val).draw();
            });

            var table = examplereportRollUp;

            $("#examplereportRollUp tbody")
              .off("click")
              .on("click", "td.details-control", function () {
                var tr = $(this).closest("tr");
                var row = table.row(tr);

                if (row.child.isShown()) {
                  row.child.hide();
                  tr.removeClass("shown");
                } else {
                  let dateRangeFilters = fetchCustomisationParameters();
                  $.ajax({
                    url: `/users/${app_code2}/${current_dev_mode2}/rollup_view_get_data/`,
                    data: {
                      username: row.data().user_name,
                      start: examplereportRollUp.page.info().start,
                      length: examplereportRollUp.page.info().length,
                      daterange_list: JSON.stringify(dateRangeFilters),
                    },
                    type: "POST",
                    dataType: "json",
                    success: function (data) {
                      var details = data.data;
                      var rowsContent = "";
                      for (const detail of details) {
                        rowsContent += `
                          <div class="body-row">
                          <div style="width: 5px;">${String(detail.id)}</div>
                          <div>${String(detail.session_id)}</div>
                          <div>${String(detail.time_logged_in)}</div>
                          <div>${String(detail.time_logged_out)}</div>
                          <div>${String(detail.logout_type)}</div>
                          <div>${String(detail.ip.replace(/"$"/g, " "))}</div>
                        </div>`;
                      }

                      var childContent = `
                        <style>
                          .table {
                            display: flex;
                            flex-direction: column;
                            background:var(--font-hover-color);
                          }

                          .header-row{
                            display: flex;
                            border: 0.2em solid var(--primary-color);
                            font-weight: bold;
                            white-space: normal;
                          }
                          .body-row {
                            display: flex;
                          }
                          .header-row > div,
                          .body-row > div {
                            padding: 0.5em;
                            flex: 1;
                            text-align: center;
                            width: 100px;
                            white-space: normal;
                          }

                        </style>
                        <div class="table">
                          <div class="header-row">
                            <div>ID</div>
                            <div>Session ID</div>
                            <div>Time Logged In</div>
                            <div>Time Logged Out</div>
                            <div>Logout Type</div>
                            <div>IP</div>
                          </div>
                          ${rowsContent}
                        </div>`;

                      row.child(childContent).show();
                      tr.addClass("shown");
                    },
                    error: function (data) {
                      Swal.fire({
                        icon: "error",
                        text: "Error! Please try again.",
                      });
                    },
                  });
                }
              });
          },

          drawCallback: function (settings) {
                        var api = this.api();
            var visibleRows = api.rows({ page: "current" }).data();
            if (visibleRows.length > 0) {
              $("#examplereportRollUp_wrapper").find("td").css({
                "background-color": "var(--primary-color)",
                border: "solid white 10px",
                "border-radius": "40px",
                padding: "10px",
                "background-image":
                  "linear-gradient(90deg, var(--primary-color) 0%, rgba(255, 255, 255, 0.4) 0%)",
                color: "white",
                width: "30%",
                cursor: "pointer",
                "white-space": "normal",
              });
              var firstColumn = $(
                "#examplereportRollUp tbody tr td:first-child"
              );
              firstColumn.css({
                "background-image":
                  "linear-gradient(90deg, var(--primary-color) 20%, rgba(255, 255, 255, 0.4) 0%)",
              });
            }
            $("#user-info1").empty();
              $("#user-info1")
                .append(`<div style="display: flex; align-items: center; width: 95%;">
              <p style="padding-left: 2rem;text-align: left;font-weight: 600;font-size: 1.5rem;margin: 0; flex: 1;">${settings.json.unique_items.total_unique_usernames}</p>
              <p style="margin: 0; flex: 2; word-break: break-word;">Total Unique Usernames</p>
            </div>`);
          },
        })
        .columns.adjust();
    }
  }
}

// Handler for User Activity insights
function viewActivityTrailDetails(viewName = "Default") {
  if (viewName != currentActivityTrailViewName || !activityTrailFilterApplied) {
    // Update global variables to record the change
    currentActivityTrailViewName = viewName;
    activityTrailFilterApplied = true;
    $("#examplereport2div").css("display", "block");
    $("#examplereport2div").attr("data-active-view", viewName);

    if (viewName === "Default") {
      $("#examplereport2_wrapper").css("display", "block").css("opacity", "1");
      $("#examplereportRollUp1").css("display", "none");
      $("#examplereportRollUp2").css("display", "none");
      $("#examplereportRollUp4").css("display", "none");
      $("#examplereportRollUp1_wrapper").css("display", "none");
      $("#examplereportRollUp2_wrapper").css("display", "none");
      $("#examplereportRollUp4_wrapper").css("display", "none");

      // Destroy existing DataTable
      if ($.fn.dataTable.isDataTable("#examplereport2")) {
        $("#examplereport2").DataTable().clear().destroy();
      }

      const activityTrailColumnArray = [
        { data: "id" },
        { data: "session_id" },
        { data: "ip" },
        { data: "user_name" },
        { data: "app_code" },
        { data: "url_current" },
        { data: "url_from" },
        { data: "screen" },
        { data: "logged_date" },
        { data: "logged_time" },
        { data: "time_spent" },
      ];
      $(`#examplereport2`)
        .DataTable({
          scrollY: "50vh",
          scrollCollapse: true,
          scrollX: "120%",
          serverSide: true,
          ordering: false,
          orderCellsTop: true,
          responsive: true,
          colReorder: {
            fixedColumnsLeft: 1,
          },
          stateSave: false,
          deferRender: true,
          paging: true,
          lengthMenu: [
            [1, 5, 50, -1],
            [1, 5, 50, "All"],
          ],
          stripeClasses: [],
          pageLength: 50,
          dom: "lfBrtip",
          buttons: [
            "copy",
            "excel",
            "csv",
            {
              extend: 'pdfHtml5',
              title: '',
              // pageSize: 'A4',
              // eslint-disable-next-line no-unused-vars
              customize: function (doc, config) {
                let tableNode
                for (let i = 0; i < doc.content.length; ++i) {
                  if (String(doc.content[i].table) !== 'undefined') {
                    tableNode = doc.content[i]
                    break;
                  }
                }

                const rowIndex = 0
                const tableColumnCount =
                  tableNode.table.body[rowIndex].length

                if (tableColumnCount > 5) {
                  doc.pageOrientation = 'landscape'
                }
                if (tableColumnCount <= 15) {
                  doc.pageSize = 'A4'
                }

                if (tableColumnCount > 15 && tableColumnCount <= 25) {
                  doc.pageSize = 'B3'
                }

                if (tableColumnCount > 25 && tableColumnCount <= 40) {
                  doc.pageSize = 'A1'
                }

                if (tableColumnCount > 40) {
                  doc.pageSize = 'A0'
                }
              },
            },
            "print",
          ],
          language: {
            lengthMenu: "Show entries : ",
          },
          ajax: {
            url: `/users/${app_code2}/${current_dev_mode2}/user_activity_insights/default/`,
            type: "POST",
            data: function (d, settings) {
              const daterange_list =
                fetchCustomisationParametersActivityTrail();
              d.daterange_list = JSON.stringify(daterange_list);
              var searchValue = $("#examplereport2_filter input").val();
              d.searchValue = searchValue;
              return d;
            },
          },
          sScrollX: "120%",
          columns: activityTrailColumnArray,
          columnDefs: [
            {
              targets: "_all",
              className: "dt-center allColumnClass all",
            },
          ],
          initComplete: function (settings, json) {
            var tableWrapper = $("#examplereport2_wrapper");
            var scrollBarWidth =
              tableWrapper.innerWidth() - tableWrapper.prop("clientWidth");
            $("#examplereport2 .dataTables_scrollBody").css(
              "padding-right",
              scrollBarWidth + "px"
            );
            $(
              "#examplereport2 > tbody > tr"
            ).css("height", "3rem");
            $(
              "#examplereport2 .dataTables_scrollBody::-webkit-scrollbar-thumb"
            ).css("height", "50px");
            $(
              "#examplereport2 .dataTables_scrollBody::-webkit-scrollbar-thumb"
            ).css("background-color", "#ccc");
            $(
              "#examplereport2 .dataTables_scrollBody::-webkit-scrollbar-thumb"
            ).css("border-radius", "5px");
            $("#examplereport2 .dataTables_scrollBody::-webkit-scrollbar").css(
              "width",
              "8px"
            );
            var select = $(
              '<select name="examplereport2_length" aria-controls="examplereport2" class="select2 form-control form-control-sm" style="width: 7rem; margin-left: 0.3rem;"></select>'
            )
              .append('<option value="1">1</option>')
              .append('<option value="5">5</option>')
              .append('<option value="50" selected>50</option>')
              .append('<option value="100">100</option>')
              .append('<option value="-1">All</option>');
            $(".dataTables_length", tableWrapper)
              .empty()
              .append("Show entries : ")
              .append(select);
            $('#examplereport2_length > select.select2').select2();
            select.on("select2:select", function () {
              var val = $.fn.dataTable.util.escapeRegex($(this).val());
              if (val === "\\-1") {
                val = -1;
              }
              $("#examplereport2").DataTable().page.len(val).draw();
            });
            $("#user-info2").empty();
            $("#user-info3").empty();
            $("#user-info4").empty();
            $("#user-info5").empty();
            $("#user-info2")
              .append(`<div style="display: flex; align-items: center; width: 95%;">
            <p style="padding-left: 2rem;text-align: left;font-weight: 600;font-size: 1.5rem;margin: 0; flex: 1;">${json.unique_items.total_unique_ips}</p>
          </div>`);
            $("#user-info3")
              .append(`<div style="display: flex; align-items: center; width: 95%;">
            <p style="padding-left: 2rem;text-align: left;font-weight: 600;font-size: 1.5rem;margin: 0; flex: 1;">${json.unique_items.total_unique_usernames}</p>
            <p style="margin: 0; flex: 2; word-break: break-word;">Total Unique Usernames</p>
          </div>`);
            $("#user-info4")
              .append(`<div style="display: flex; align-items: center; width: 95%;">
          <p style="padding-left: 2rem;text-align: left;font-weight: 600;font-size: 1.5rem;margin: 0; flex: 1;">${json.unique_items.total_unique_sessions}</p>
          <p style="margin: 0; flex: 2; word-break: break-word;">Total Unique Session IDs</p>
        </div>`);
            $("#user-info5")
              .append(`<div style="display: flex; align-items: center; width: 95%;">
          <p style="padding-left: 2rem;text-align: left;font-weight: 600;font-size: 1.5rem;margin: 0; flex: 1;">${json.unique_items.total_unique_urls}</p>
          <p style="margin: 0; flex: 2; word-break: break-word;">Total Unique URLs</p>
        </div>`);
          },
          "fnDrawCallback": function( oSettings ) {

          }
        })
        .columns.adjust();
        $(`#examplereport2`).DataTable().buttons().container().css("display", "none");
    } else if (viewName === "examplereportRollUp1") {
      $("#examplereport2div").css("display", "none");
      $("#examplereport2_wrapper").css("display", "none");
      $("#examplereportRollUp1").css("display", "block");
      $("#examplereportRollUp1_wrapper").css("display", "block");
      $("#examplereportRollUp1").find(".accordion").css("display", "none");
      $("#examplereportRollUp2").css("display", "none");
      $("#examplereportRollUp4").css("display", "none");
      $("#examplereportRollUp4_wrapper").css("display", "none");
      $("#examplereportRollUp2_wrapper").css("display", "none");

      // Destroy existing DataTable
      if ($.fn.dataTable.isDataTable("#examplereportRollUp1")) {
        $("#examplereportRollUp1").DataTable().clear().destroy();
      }
      $("#examplereportRollUp2").find(".main-div-container").empty();
      var examplereportRollUp1 = $("#examplereportRollUp1")
        .DataTable({
          scrollY: "50vh",
          scrollCollapse: true,
          scrollX: "120%",
          serverSide: true,
          ordering: false,
          orderCellsTop: true,
          responsive: true,
          colReorder: {
            fixedColumnsLeft: 1,
          },
          stateSave: false,
          deferRender: true,
          paging: true,
          lengthMenu: [
            [1, 5, 50, -1],
            [1, 5, 50, "All"],
          ],
          pageLength: 50,
          dom: "lfrtip",
          language: {
            lengthMenu: "Show entries : ",
          },
          ajax: {
            url: `/users/${app_code2}/${current_dev_mode2}/user_activity_insights/userView/`,
            type: "POST",
            data: function (d, settings) {
              const daterange_list =
                fetchCustomisationParametersActivityTrail();
              d.daterange_list = JSON.stringify(daterange_list);
              var searchValue = $("#examplereportRollUp1_filter input").val();
              d.searchValue = searchValue;
              return d;
            },
            dataSrc: function (json) {
              return json.data;
            },
          },
          sScrollX: "120%",
          columns: [
            {
              data: "user_name",
              className: "dt-center allColumnClass all",
              width: "50px",
              render: function (data, type, row) {
                if (type === "display") {
                  return (
                    '<span class="icon-span"><i class="fa-solid fa-circle-chevron-down" style="float: left; width:16%;"></i></span>' +
                    '<span class="data-span first-column-data">' +
                    data +
                    "</span>"
                  );
                }
                return data;
              },
            },
            {
              data: "session_time",
              className: "dt-center allColumnClass all",
              width: "150px",
            },
            {
              data: "no_of_user",
              className: "dt-center allColumnClass all",
              width: "120px",
            },
          ],
          columnDefs: [
            {
              targets: "_all",
              className: "dt-center allColumnClass all",
            },
            {
              targets: "_all",
              className: "details-control",
              orderable: false,
              data: null,
              defaultContent: '<i class="fa fa-chevron-right"></i>',
            },
          ],
          initComplete: function (settings, json) {
            var tableWrapper = $("#examplereportRollUp1_wrapper");
            var scrollBarWidth =
              tableWrapper.innerWidth() - tableWrapper.prop("clientWidth");
            $("#examplereportRollUp1 .dataTables_scrollBody").css(
              "padding-right",
              scrollBarWidth + "px"
            );
            $(
              "#examplereportRollUp1 .dataTables_scrollBody::-webkit-scrollbar-thumb"
            ).css("height", "50px");
            $(
              "#examplereportRollUp1 .dataTables_scrollBody::-webkit-scrollbar-thumb"
            ).css("background-color", "#ccc");
            $(
              "#examplereportRollUp1 .dataTables_scrollBody::-webkit-scrollbar-thumb"
            ).css("border-radius", "5px");
            $(
              "#examplereportRollUp1 .dataTables_scrollBody::-webkit-scrollbar"
            ).css("width", "8px");
            var select = $(
              '<select name="examplereportRollUp1_length" aria-controls="examplereportRollUp1" class="select2 form-control form-control-sm" style="width: 7rem; margin-left: 0.3rem;"></select>'
            )
              .append('<option value="1">1</option>')
              .append('<option value="5">5</option>')
              .append('<option value="50" selected>50</option>')
              .append('<option value="100">100</option>')
              .append('<option value="-1">All</option>');
            $(".dataTables_length", tableWrapper)
              .empty()
              .append("Show entries : ")
              .append(select);
            $('#examplereportRollUp1_length > select.select2').select2();
            select.on("select2:select", function () {
              var val = $.fn.dataTable.util.escapeRegex($(this).val());
              if (val === "\\-1") {
                val = -1;
              }
              $("#examplereportRollUp1").DataTable().page.len(val).draw();
            });

            var table = examplereportRollUp1;

            $("#examplereportRollUp1 tbody")
              .off("click")
              .on("click", "td.details-control", function () {
                var tr = $(this).closest("tr");
                var row = table.row(tr);

                if (row.child.isShown()) {
                  row.child.hide();
                  tr.removeClass("shown");
                } else {
                  let dateRangeFilters = fetchCustomisationParametersActivityTrail();
                  $.ajax({
                    url: `/users/${app_code2}/${current_dev_mode2}/user_activity_insights/userView/`,
                    data: {
                      username: row.data().user_name,
                      start: examplereportRollUp1.page.info().start,
                      length: examplereportRollUp1.page.info().length,
                      daterange_list: JSON.stringify(dateRangeFilters),
                    },
                    type: "POST",
                    dataType: "json",
                    success: function (data) {
                      var details = data.data;
                      var rowsContent = "";
                      for (const detail of details) {
                        rowsContent += `
                        <div class="body-row">
                          <div style="width: 5px;">${String(detail.id)}</div>
                          <div>${String(detail.session_id)}</div>
                          <div>${String(detail.ip)}</div>
                          <div>${String(detail.app_code)}</div>
                          <div>${String(detail.url_current)}</div>
                          <div>${String(detail.url_from)}</div>
                          <div>${String(detail.screen)}</div>
                          <div>${String(detail.logged_date)}</div>
                          <div>${String(detail.logged_time)}</div>
                          <div>${
                            String(detail.time_spent) === 0 ||
                            String(detail.time_spent) === "-"
                              ? "-"
                              : `${String(detail.time_spent)} hr`
                          }</div>
                        </div>`;
                      }

                      var childContent = `
                <style>
                  .table {
                    display: flex;
                    flex-direction: column;
                    background:var(--font-hover-color);
                  }

                  .header-row{
                    display: flex;
                    border: 0.2em solid var(--primary-color);
                    font-weight: bold;
                    white-space: normal;
                  }
                  .body-row {
                    display: flex;
                  }
                  .header-row > div,
                  .body-row > div {
                    padding: 0.5em;
                    flex: 1;
                    text-align: center;
                    width: 100px;
                    white-space: normal;
                  }

                </style>
                <div class="table">
                  <div class="header-row">
                    <div>ID</div>
                    <div>Session ID</div>
                    <div>IP</div>
                    <div>Application</div>
                    <div>URL Request</div>
                    <div>URL From</div>
                    <div>Screen</div>
                    <div>Date</div>
                    <div>Time</div>
                    <div>Time spent</div>
                  </div>
                  ${rowsContent}
                </div>`;

                      row.child(childContent).show();
                      tr.addClass("shown");
                    },
                    error: function (data) {
                      Swal.fire({
                        icon: "error",
                        text: "Error! Please try again.",
                      });
                    },
                  });
                }
              });
          },
          drawCallback: function (settings) {
                        var api = this.api();
            var visibleRows = api.rows({ page: "current" }).data();
            if (visibleRows.length > 0) {
              $("#examplereportRollUp1_wrapper").find("td").css({
                "background-color": "var(--primary-color)",
                border: "solid white 10px",
                "border-radius": "40px",
                padding: "10px",
                "background-image":
                  "linear-gradient(90deg, var(--primary-color) 0%, rgba(255, 255, 255, 0.4) 0%)",
                color: "white",
                width: "25%",
                cursor: "pointer",
              });

              var firstColumn = $(
                "#examplereportRollUp1 tbody tr td:first-child"
              );
              firstColumn.css({
                "background-image":
                  "linear-gradient(90deg, var(--primary-color) 20%, rgba(255, 255, 255, 0.4) 0%)",
              });
            }
            $("#user-info3 p:first-child").text(settings.json.unique_items.total_unique_usernames);
          },
        })
        .columns.adjust();
    } else if (viewName === "examplereportRollUp2") {
      $("#examplereport2div").css("display", "none");
      $("#examplereport2_wrapper").css("display", "none");
      $("#examplereportRollUp1").css("display", "none");
      $("#examplereportRollUp4").css("display", "none");
      $("#examplereportRollUp2").css("display", "block");
      $("#examplereportRollUp2").find(".accordion1").css("display", "block");
      $("#examplereportRollUp4_wrapper").css("display", "none");
      $("#examplereportRollUp1_wrapper").css("display", "none");
      if ($.fn.dataTable.isDataTable("#examplereportRollUp2")) {
        $("#examplereportRollUp2").DataTable().clear().destroy();
      }
      var examplereportRollUp2 = $("#examplereportRollUp2")
        .DataTable({
          scrollY: "50vh",
          scrollCollapse: true,
          scrollX: "120%",
          serverSide: true,
          ordering: false,
          orderCellsTop: true,
          responsive: true,
          colReorder: {
            fixedColumnsLeft: 1,
          },
          stateSave: false,
          deferRender: true,
          paging: true,
          lengthMenu: [
            [1, 5, 50, -1],
            [1, 5, 50, "All"],
          ],
          pageLength: 50,
          dom: "lfrtip",
          language: {
            lengthMenu: "Show entries : ",
          },
          ajax: {
            url: `/users/${app_code2}/${current_dev_mode2}/user_activity_insights/sessionView/`,
            type: "POST",
            data: function (d, settings) {
              const daterange_list =
                fetchCustomisationParametersActivityTrail();
              d.daterange_list = JSON.stringify(daterange_list);
              d.searchValue = $("#examplereportRollUp2_filter input").val();
              return d;
            },
            dataSrc: function (json) {
              return json.data;
            },
          },
          sScrollX: "120%",
          columns: [
            {
              data: "session_id",
              className: "dt-center allColumnClass all",
              width: "50px",
              render: function (data, type, row) {
                if (type === "display") {
                  return (
                    '<span class="icon-span"><i class="fa-solid fa-circle-chevron-down" style="float: left; width:16%;"></i></span>' +
                    '<span class="data-span first-column-data">' +
                    data +
                    "</span>"
                  );
                }
                return data;
              },
            },
            {
              data: "session_time",
              className: "dt-center allColumnClass all",
              width: "150px",
            },
            {
              data: "no_of_user",
              className: "dt-center allColumnClass all",
              width: "120px",
            },
          ],
          columnDefs: [
            {
              targets: "_all",
              className: "dt-center allColumnClass all",
            },
            {
              targets: "_all",
              className: "details-control",
              orderable: false,
              data: null,
              defaultContent: '<i class="fa fa-chevron-right"></i>',
            },
          ],
          initComplete: function (settings, json) {
            var tableWrapper = $("#examplereportRollUp2_wrapper");
            var scrollBarWidth =
              tableWrapper.innerWidth() - tableWrapper.prop("clientWidth");
            $("#examplereportRollUp2 .dataTables_scrollBody").css(
              "padding-right",
              scrollBarWidth + "px"
            );
            $(
              "#examplereportRollUp2 .dataTables_scrollBody::-webkit-scrollbar-thumb"
            ).css("height", "50px");
            $(
              "#examplereportRollUp2 .dataTables_scrollBody::-webkit-scrollbar-thumb"
            ).css("background-color", "#ccc");
            $(
              "#examplereportRollUp2 .dataTables_scrollBody::-webkit-scrollbar-thumb"
            ).css("border-radius", "5px");
            $(
              "#examplereportRollUp2 .dataTables_scrollBody::-webkit-scrollbar"
            ).css("width", "8px");
            var select = $(
              '<select name="examplereportRollUp2_length" aria-controls="examplereportRollUp2" class="select2 form-control form-control-sm" style="width: 7rem; margin-left: 0.3rem;"></select>'
            )
              .append('<option value="1">1</option>')
              .append('<option value="5">5</option>')
              .append('<option value="50" selected>50</option>')
              .append('<option value="100">100</option>')
              .append('<option value="-1">All</option>');
            $(".dataTables_length", tableWrapper)
              .empty()
              .append("Show entries : ")
              .append(select);
            $('#examplereportRollUp2_length > select.select2').select2();
            select.on("select2:select", function () {
              var val = $.fn.dataTable.util.escapeRegex($(this).val());
              if (val === "\\-1") {
                val = -1;
              }
              $("#examplereportRollUp2").DataTable().page.len(val).draw();
            });

            var table = examplereportRollUp2;

            $("#examplereportRollUp2 tbody")
              .off("click")
              .on("click", "td.details-control", function () {
                var tr = $(this).closest("tr");
                var row = table.row(tr);

                if (row.child.isShown()) {
                  row.child.hide();
                  tr.removeClass("shown");
                } else {
                  let dateRangeFilters = fetchCustomisationParametersActivityTrail();
                  $.ajax({
                    url: `/users/${app_code2}/${current_dev_mode2}/user_activity_insights/sessionView/`,
                    data: {
                      session_id: row.data().session_id,
                      start: examplereportRollUp2.page.info().start,
                      length: examplereportRollUp2.page.info().length,
                      daterange_list: JSON.stringify(dateRangeFilters),
                    },
                    type: "POST",
                    dataType: "json",
                    success: function (data) {
                      var details = data.data;
                      var rowsContent = "";
                      for (const detail of details) {
                        rowsContent += `
                        <div class="body-row">
                          <div>${String(detail.id)}</div>
                          <div>${String(detail.ip)}</div>
                          <div>${String(detail.user_name)}</div>
                          <div>${String(detail.app_code)}</div>
                          <div>${String(detail.url_current)}</div>
                          <div>${String(detail.url_from)}</div>
                          <div>${String(detail.screen)}</div>
                          <div>${String(detail.logged_date)}</div>
                          <div>${String(detail.logged_time)}</div>
                          <div>${
                            String(detail.time_spent) === 0 ||
                            String(detail.time_spent) === "-"
                              ? "-"
                              : `${String(detail.time_spent)} hr`
                          }</div>
                        </div>`;
                      }

                      var childContent = `
                    <style>
                      .table {
                        display: flex;
                        flex-direction: column;
                        background:var(--font-hover-color);
                      }

                      .header-row{
                        display: flex;
                        border: 0.2em solid var(--primary-color);
                        font-weight: bold;
                        white-space: normal;
                      }
                      .body-row {
                        display: flex;
                      }
                      .header-row > div,
                      .body-row > div {
                        padding: 0.5em;
                        flex: 1;
                        text-align: center;
                        width: 100px;
                        white-space: normal;
                      }

                    </style>
                    <div class="table">
                      <div class="header-row">
                        <div>ID</div>
                        <div>IP</div>
                        <div>Username</div>
                        <div>Application</div>
                        <div>URL Request</div>
                        <div>URL From</div>
                        <div>Screen</div>
                        <div>Date</div>
                        <div>Time</div>
                        <div>Time spent</div>
                      </div>
                      ${rowsContent}
                    </div>`;

                      row.child(childContent).show();
                      tr.addClass("shown");
                    },
                    error: function (data) {
                      Swal.fire({
                        icon: "error",
                        text: "Error! Please try again.",
                      });
                    },
                  });
                }
              });
          },
          drawCallback: function (settings) {
            var api = this.api();
            var visibleRows = api.rows({ page: "current" }).data();
            if (visibleRows.length > 0) {
              $(".first-column-data").css({
                "max-width": "80%" /* Adjust the value as needed */,
                "white-space": "normal",
                "text-overflow": "ellipsis",
                display: "inline-block",
              });
              $("#examplereportRollUp2_wrapper").find("td").css({
                "background-color": "var(--primary-color)",
                border: "solid white 10px",
                "border-radius": "40px",
                padding: "10px",
                "background-image":
                  "linear-gradient(90deg, var(--primary-color) 0%, rgba(255, 255, 255, 0.4) 0%)",
                color: "white",
                width: "25%",
                cursor: "pointer",
              });

              var firstColumn = $(
                "#examplereportRollUp2 tbody tr td:first-child"
              );
              firstColumn.css({
                "background-image":
                  "linear-gradient(90deg, var(--primary-color) 20%, rgba(255, 255, 255, 0.4) 0%)",
              });
            }
            $("#user-info4 p:first-child").text(settings.json.unique_items.total_unique_sessions);

          },
        })
        .columns.adjust();
    } else {
      // URL Roll-up View
      $("#examplereport2div").css("display", "none");
      $("#examplereport2_wrapper").css("display", "none");
      $("#examplereportRollUp1").css("display", "none");
      $("#examplereportRollUp2").css("display", "none");
      $("#examplereportRollUp4").css("display", "block");
      $("#examplereportRollUp1_wrapper").css("display", "none");
      $("#examplereportRollUp2_wrapper").css("display", "none");
      $("#examplereportRollUp4_wrapper").css("display", "block");
      $("#examplereportRollUp4").find(".accordion2").css("display", "flex");

      if ($.fn.dataTable.isDataTable("#examplereportRollUp4")) {
        $("#examplereportRollUp4").DataTable().clear().destroy();
      }
      var examplereportRollUp4 = $("#examplereportRollUp4")
        .DataTable({
          scrollY: "50vh",
          scrollCollapse: true,
          scrollX: "120%",
          serverSide: true,
          ordering: false,
          orderCellsTop: true,
          responsive: true,
          colReorder: {
            fixedColumnsLeft: 1,
          },
          stateSave: false,
          deferRender: true,
          paging: true,
          lengthMenu: [
            [1, 5, 50, -1],
            [1, 5, 50, "All"],
          ],
          pageLength: 50,
          dom: "lfrtip",
          language: {
            lengthMenu: "Show entries : ",
          },
          ajax: {
            url: `/users/${app_code2}/${current_dev_mode2}/user_activity_insights/urlView/`,
            type: "POST",
            data: function (d, settings) {
              const daterange_list =
                fetchCustomisationParametersActivityTrail();
              d.daterange_list = JSON.stringify(daterange_list);
              var searchValue = $("#examplereportRollUp4_filter input").val();
              d.searchValue = searchValue;
              return d;
            },
            dataSrc: function (json) {
              return json.data;
            },
          },
          sScrollX: "120%",
          columns: [
            {
              data: "url_current",
              className: "dt-center allColumnClass all",
              width: "50%",
              render: function (data, type, row) {
                if (type === "display") {
                  return (
                    '<span class="icon-span"><i class="fa-solid fa-circle-chevron-down" style="float: left; width:16%;"></i></span>' +
                    '<span class="data-span first-column-data">' +
                    data +
                    "</span>"
                  );
                }
                return data;
              },
            },
            {
              data: "session_time",
              className: "dt-center allColumnClass all",
              width: "25%",
            },
            {
              data: "no_of_user",
              className: "dt-center allColumnClass all",
              width: "25%",
            },
          ],
          columnDefs: [
            {
              targets: "_all",
              className: "details-control",
              orderable: false,
              data: null,
              defaultContent: '<i class="fa fa-chevron-right"></i>',
            },
          ],
          initComplete: function (settings, json) {
            var tableWrapper = $("#examplereportRollUp4_wrapper");
            var scrollBarWidth =
              tableWrapper.innerWidth() - tableWrapper.prop("clientWidth");
            $("#examplereportRollUp4 .dataTables_scrollBody").css(
              "padding-right",
              scrollBarWidth + "px"
            );
            $(
              "#examplereportRollUp4 .dataTables_scrollBody::-webkit-scrollbar-thumb"
            ).css("height", "50px");
            $(
              "#examplereportRollUp4 .dataTables_scrollBody::-webkit-scrollbar-thumb"
            ).css("background-color", "#ccc");
            $(
              "#examplereportRollUp4 .dataTables_scrollBody::-webkit-scrollbar-thumb"
            ).css("border-radius", "5px");
            $(
              "#examplereportRollUp4 .dataTables_scrollBody::-webkit-scrollbar"
            ).css("width", "8px");
            var select = $(
              '<select name="examplereportRollUp4_length" aria-controls="examplereportRollUp4" class="select2 form-control form-control-sm" style="width: 7rem; margin-left: 0.3rem; "></select>'
            )
              .append('<option value="1">1</option>')
              .append('<option value="5">5</option>')
              .append('<option value="50" selected>50</option>')
              .append('<option value="100">100</option>')
              .append('<option value="-1">All</option>');

            $(".dataTables_length", tableWrapper)
              .empty()
              .append("Show entries : ")
              .append(select);
            $('#examplereportRollUp4_length > select.select2').select2();
            select.on("select2:select", function () {
              var val = $.fn.dataTable.util.escapeRegex($(this).val());
              if (val === "\\-1") {
                val = -1;
              }
              $("#examplereportRollUp4").DataTable().page.len(val).draw();
            });

            var table = examplereportRollUp4;

            $("#examplereportRollUp4 tbody")
              .off("click")
              .on("click", "td.details-control", function () {
                var tr = $(this).closest("tr");
                var row = table.row(tr);

                if (row.child.isShown()) {
                  row.child.hide();
                  tr.removeClass("shown");
                } else {
                  let dateRangeFilters = fetchCustomisationParametersActivityTrail();
                  $.ajax({
                    url: `/users/${app_code2}/${current_dev_mode2}/user_activity_insights/urlView/`,
                    data: {
                      url: row.data().url_current,
                      start: examplereportRollUp4.page.info().start,
                      length: examplereportRollUp4.page.info().length,
                      daterange_list: JSON.stringify(dateRangeFilters),
                    },
                    type: "POST",
                    dataType: "json",
                    success: function (data) {
                      var details = data.data;

                      var rowsContent = "";
                      for (const detail of details) {
                        rowsContent += `
                        <div class="body-row">
                          <div style="width: 5px;">${String(detail.id)}</div>
                          <div>${String(detail.session_id)}</div>
                          <div>${String(detail.ip)}</div>
                          <div>${String(detail.user_name)}</div>
                          <div>${String(detail.app_code)}</div>
                          <div>${String(detail.url_from)}</div>
                          <div>${String(detail.screen)}</div>
                          <div>${String(detail.logged_date)}</div>
                          <div>${String(detail.logged_time)}</div>
                          <div>${
                            String(detail.time_spent) === 0 ||
                            String(detail.time_spent) === "-"
                              ? "-"
                              : `${String(detail.time_spent)} hr`
                          }</div>
                        </div>`;
                      }

                      // Join the rows and include in the HTML
                      var childContent = `
                    <style>
                      .table {
                        display: flex;
                        flex-direction: column;
                        background:var(--font-hover-color);
                      }

                      .header-row{
                        display: flex;
                        border: 0.2em solid var(--primary-color);
                        font-weight: bold;
                        white-space: normal;
                      }
                      .body-row {
                        display: flex;
                      }
                      .header-row > div,
                      .body-row > div {
                        padding: 0.5em;
                        flex: 1;
                        text-align: center;
                        width: 100px;
                        white-space: normal;
                      }

                    </style>
                    <div class="table">
                      <div class="header-row">
                        <div>ID</div>
                        <div>Session ID</div>
                        <div>IP</div>
                        <div>Username</div>
                        <div>Application</div>
                        <div>URL From</div>
                        <div>Screen</div>
                        <div>Date</div>
                        <div>Time</div>
                        <div>Time spent</div>
                      </div>
                      ${rowsContent}
                    </div>`;

                      row.child(childContent).show();
                      tr.addClass("shown");
                    },
                    error: function (data) {
                      Swal.fire({
                        icon: "error",
                        text: "Error! Please try again.",
                      });
                    },
                  });
                }
              });
          },
          drawCallback: function (settings) {
            var api = this.api();
            var visibleRows = api.rows({ page: "current" }).data();
            if (visibleRows.length > 0) {
              $(".first-column-data").css({
                "max-width": "80%" /* Adjust the value as needed */,
                "white-space": "normal",
                "text-overflow": "ellipsis",
                display: "inline-block",
                "padding-left": "10px",
              });

              $("#examplereportRollUp4_wrapper").find("td").css({
                "background-color": "var(--primary-color)",
                border: "solid white 10px",
                "border-radius": "40px",
                padding: "10px",
                "background-image":
                  "linear-gradient(90deg, var(--primary-color) 0%, rgba(255, 255, 255, 0.4) 0%)",
                color: "white",
                cursor: "pointer",
                "white-space": "normal",
                width: "25%",
              });

              var firstColumn = $(
                "#examplereportRollUp4 tbody tr td:first-child"
              );
              firstColumn.css({
                "background-image":
                  "linear-gradient(90deg, var(--primary-color) 20%, rgba(255, 255, 255, 0.4) 0%)",
                "width": "50%",
              });
            }
            $("#user-info5 p:first-child").text(settings.json.unique_items.total_unique_urls);

          },
        })
        .columns.adjust();
    }
  }
}

// Handler for Data Operations insights
function viewDataOpsTrailDetails() {
  const dataOpsColumnArray = [
    { data: "id" },
    { data: "url" },
    { data: "operation" },
    { data: "message" },
    { data: "datetime" },
    { data: "username" },
  ];
  $(`#examplereport3`)
    .DataTable({
      scrollY: "50vh",
      scrollCollapse: true,
      scrollX: "120%",
      ordering: false,
      serverSide: true,
      orderCellsTop: true,
      responsive: true,
      colReorder: {
        fixedColumnsLeft: 1,
      },
      stateSave: false,
      deferRender: true,
      paging: true,
      stripeClasses: [],
      pageLength: 50,
      dom: "lfBrtip",
      buttons: [
        "copy",
        "excel",
        "csv",
        {
          extend: 'pdfHtml5',
          title: '',
          // pageSize: 'A4',
          // eslint-disable-next-line no-unused-vars
          customize: function (doc, config) {
            let tableNode
            for (let i = 0; i < doc.content.length; ++i) {
              if (String(doc.content[i].table) !== 'undefined') {
                tableNode = doc.content[i]
                break;
              }
            }

            const rowIndex = 0
            const tableColumnCount =
              tableNode.table.body[rowIndex].length

            if (tableColumnCount > 5) {
              doc.pageOrientation = 'landscape'
            }
            if (tableColumnCount <= 15) {
              doc.pageSize = 'A4'
            }

            if (tableColumnCount > 15 && tableColumnCount <= 25) {
              doc.pageSize = 'B3'
            }

            if (tableColumnCount > 25 && tableColumnCount <= 40) {
              doc.pageSize = 'A1'
            }

            if (tableColumnCount > 40) {
              doc.pageSize = 'A0'
            }
          },
        },
        "print",
      ],
      language: {
        lengthMenu: "Show entries : ",
      },
      ajax: {
        url: `/users/${app_code2}/${current_dev_mode2}/data_operation_insights/`,
        type: "POST",
        data: function (d, settings) {
          const daterange_list = fetchCustomisationParametersDataOpsTrail();
          d.daterange_list = JSON.stringify(daterange_list);
          d.searchValue = $("#examplereport3_filter input").val();
          return d;
        },
      },
      columns: dataOpsColumnArray,
      columnDefs: [
        {
          targets: "_all",
          className: "dt-center allColumnClass all",
        },
      ],
      initComplete: function () {
        var tableWrapper = $("#examplereport3_wrapper");
        var scrollBarWidth =
          tableWrapper.innerWidth() - tableWrapper.prop("clientWidth");
        $("#examplereport3 .dataTables_scrollBody").css(
          "padding-right",
          scrollBarWidth + "px"
        );
        $(
          "#examplereport3 .dataTables_scrollBody::-webkit-scrollbar-thumb"
        ).css("height", "50px");
        $(
          "#examplereport3 .dataTables_scrollBody::-webkit-scrollbar-thumb"
        ).css("background-color", "#ccc");
        $(
          "#examplereport3 .dataTables_scrollBody::-webkit-scrollbar-thumb"
        ).css("border-radius", "5px");
        $("#examplereport3 .dataTables_scrollBody::-webkit-scrollbar").css(
          "width",
          "8px"
        );
        var select = $(
          '<select name="examplereport2_length" aria-controls="examplereport3" class="select2 form-control form-control-sm" style="width: 7rem; margin-left: 0.3rem;"></select>'
        )
          .append('<option value="1">1</option>')
          .append('<option value="5">5</option>')
          .append('<option value="50" selected>50</option>')
          .append('<option value="100">100</option>')
          .append('<option value="-1">All</option>');
        $(".dataTables_length", tableWrapper)
          .empty()
          .append("Show entries : ")
          .append(select);
        $("#examplereport3_length > select.select2").select2();
        select.on("select2:select", function () {
          var val = $.fn.dataTable.util.escapeRegex($(this).val());
          if (val === "\\-1") {
            val = -1;
          }
          $("#examplereport3").DataTable().page.len(val).draw();
        });
      },
      sScrollX: "120%",
      drawCallback: function (settings) {
        $("#examplereport3_wrapper").find("td").css({
          width: "30%",
          "white-space": "normal",
        });
      },
    })
    .columns.adjust();
}

$(`#reportbtn_search_login`).on("click", function () {
  loginTrailFilterApplied = false;
  if ($("#examplereportDiv").attr("data-active-view") == "Default") {
    $("#examplereport").DataTable().draw();
  } else {
    $("#examplereportRollUp").DataTable().draw();
  }
});

$(`#reportbtn_search2`).on("click", function () {
  activityTrailFilterApplied = true;
  if ($("#examplereport2div").attr("data-active-view") == "Default") {
    $("#examplereport2").DataTable().draw();
  } else if (
    $("#examplereport2div").attr("data-active-view") == "examplereportRollUp1"
  ) {
    $("#examplereportRollUp1").DataTable().draw();
  } else if (
    $("#examplereport2div").attr("data-active-view") == "examplereportRollUp2"
  ) {
    $("#examplereportRollUp2").DataTable().draw();
  } else {
    $("#examplereportRollUp4").DataTable().draw();
  }
});

$(`#reportbtn_search3`).on('click',function(){
  $(`#examplereport3`).DataTable().draw().columns.adjust();
})


