function showFindTable(
  mainTable,
  columnName,
  find,
  find_case,
  elementID,
  textIndex
) {
  mainTable.children().each(function () {
    let currRow = $(this);
    $(this)
      .find("td")
      .each(function () {
        currRow2 = currRow.clone();
        if ($(this).attr("data-key") == columnName) {
          columnText = $(this).text();
          currRow2
            .children()
            .eq(textIndex)
            .attr("style", "background-color:antiquewhite");
          if (find_case == "Equal to" && columnText == find) {
            currRow2.appendTo(
              $(`#findtext${elementID}`).find("table").find("tbody")
            );
          } else if (find_case == "Not Equal to" && columnText != find) {
            currRow2.appendTo(
              $(`#findtext${elementID}`).find("table").find("tbody")
            );
          } else if (find_case == "Entire Column") {
            currRow2.appendTo(
              $(`#findtext${elementID}`).find("table").find("tbody")
            );
          } else if (
            find_case == "Greater than" &&
            Number(columnText) > Number(find)
          ) {
            currRow2.appendTo(
              $(`#findtext${elementID}`).find("table").find("tbody")
            );
          } else if (
            find_case == "Greater than equal to" &&
            Number(columnText) >= Number(find)
          ) {
            currRow2.appendTo(
              $(`#findtext${elementID}`).find("table").find("tbody")
            );
          } else if (
            find_case == "Smaller than" &&
            Number(columnText) < Number(find)
          ) {
            currRow2.appendTo(
              $(`#findtext${elementID}`).find("table").find("tbody")
            );
          } else if (
            find_case == "Smaller than equal to" &&
            Number(columnText) <= Number(find)
          ) {
            currRow2.appendTo(
              $(`#findtext${elementID}`).find("table").find("tbody")
            );
          } else if (
            find_case == "Starts with" &&
            columnText.startsWith(find)
          ) {
            currRow2.appendTo(
              $(`#findtext${elementID}`).find("table").find("tbody")
            );
          } else if (find_case == "Ends with" && columnText.endsWith(find)) {
            currRow2.appendTo(
              $(`#findtext${elementID}`).find("table").find("tbody")
            );
          } else if (
            find_case == "Not Starts with" &&
            !columnText.startsWith(find)
          ) {
            currRow2.appendTo(
              $(`#findtext${elementID}`).find("table").find("tbody")
            );
          } else if (
            find_case == "Not Ends with" &&
            !columnText.endsWith(find)
          ) {
            currRow2.appendTo(
              $(`#findtext${elementID}`).find("table").find("tbody")
            );
          } else if (find_case == "Contains" && columnText.includes(find)) {
            currRow2.appendTo(
              $(`#findtext${elementID}`).find("table").find("tbody")
            );
          } else if (
            find_case == "Not Contains" &&
            !columnText.includes(find)
          ) {
            currRow2.appendTo(
              $(`#findtext${elementID}`).find("table").find("tbody")
            );
          }
        }
      });
  });
}

// eslint-disable-next-line no-unused-vars
function findreplaceUS(obj) {
  const elementID = obj.getAttribute("data-elementID");
  $(`#findtext${elementID}`).empty();
  const modelName = obj.getAttribute("data-table-name");
  const is_find = obj.getAttribute("is_find");
  let columnName = $("option:selected", `#selectcolumn${elementID}`).attr(
    "name"
  );
  let currRow_bk = ""
  let bk_index = -1
  const replacecolumnName = $("option:selected", `#selectreplacecolumn${elementID}`).attr(
    "name"
  );
  let columnNameVerbose = $(
    "option:selected",
    `#selectcolumn${elementID}`
  ).attr("value");
  let replacecolumnNameVerbose = $(
    "option:selected",
    `#selectreplacecolumn${elementID}`
  ).attr("value");
  let allCols = [];
  $(`#selectcolumn${elementID}`)
    .children()
    .each(function () {
      allCols.push($(this).text());
    });
  allCols.shift();
  const datatype = $("option:selected", `#selectreplacecolumn${elementID}`).attr(
    "data-type"
  );

  let find = ""

  if($('#text_basedip_' + elementID).is(":checked")){
    find = $(`#find${elementID}`).val();
  }else{
    find = $(`#show_textinputfind${elementID}`).val()
  }

  if (find == "") {
    find = "nan";
  }
  let replace = $(`#replace${elementID}`).val();
  if (replace == "") {
    replace = "nan";
  }
  let find_case = $(`#selectcase${elementID}`).val();
  if (String(datatype) === "ForeignKey") {
    find = $("option:selected", `#find${elementID}`).attr("name");
    replace = $("option:selected", `#replace${elementID}`).attr("name");
  }
  if (String(datatype) === "DateTimeField") {
    find = find.replace("T", " ");
    replace = replace.replace("T", " ");
  }
  let mainTable = $(`#edit_upload_modal_datatable${elementID}_wrapper`).find(
    "#edit_upload_content"
  );
  let flag = 0
  $(`#findtext${elementID}`).append(
    "<table><thead><tr></tr></thead><tbody></tbody></table>"
  );
  $(`#edit_upload_modal_datatable${elementID}_wrapper`)
    .find(".edit_upload_header")
    .eq(0)
    .find("tr")
    .children()
    .each(function () {
      $(`#findtext${elementID}`)
        .find("table")
        .find("thead")
        .find("tr")
        .append(`<td>${$(this).text()}</td>`);
    });
  if (is_find != "True") {
    mainTable.children().each(function () {
      let currRow = $(this);
      flag = 0
      $(this)
        .find("td")
        .each(function () {
          if ($(this).attr("data-key") == columnName) {
            columnText = $(this).text();

            if (find_case == "Equal to" && (columnText == find || flag)) {
              if(columnName == replacecolumnName){
                $(this).text(replace);
              }else{
                flag = 1
                bk_index = allCols.indexOf(columnNameVerbose)
                columnName = replacecolumnName
                columnNameVerbose = replacecolumnNameVerbose
                currRow_bk = $(this).parent().children().eq(allCols.indexOf(columnNameVerbose))
              }
            } else if (find_case == "Not Equal to" && (columnText != find && flag)) {
              if(columnName == replacecolumnName){
                $(this).text(replace);
              }else{
                flag = 1
                bk_index = allCols.indexOf(columnNameVerbose)
                columnName = replacecolumnName
                columnNameVerbose = replacecolumnNameVerbose
                currRow_bk = $(this).parent().children().eq(allCols.indexOf(columnNameVerbose))
              }
            } else if (find_case == "Entire Column") {
              $(this).text(replace);
            } else if (
              find_case == "Greater than" &&
              ((Number(columnText) > Number(find)) || flag)
            ) {
              if(columnName == replacecolumnName){
                $(this).text(replace);
              }else{
                flag = 1
                bk_index = allCols.indexOf(columnNameVerbose)
                columnName = replacecolumnName
                columnNameVerbose = replacecolumnNameVerbose
                currRow_bk = $(this).parent().children().eq(allCols.indexOf(columnNameVerbose))
              }
            } else if (
              find_case == "Greater than equal to" &&
              ((Number(columnText) >= Number(find)) || flag)
            ) {
              if(columnName == replacecolumnName){
                $(this).text(replace);
              }else{
                flag = 1
                bk_index = allCols.indexOf(columnNameVerbose)
                columnName = replacecolumnName
                columnNameVerbose = replacecolumnNameVerbose
                currRow_bk = $(this).parent().children().eq(allCols.indexOf(columnNameVerbose))
              }
            } else if (
              find_case == "Smaller than" &&
              ((Number(columnText) < Number(find)) || flag)
            ) {
              if(columnName == replacecolumnName){
                $(this).text(replace);
              }else{
                flag = 1
                bk_index = allCols.indexOf(columnNameVerbose)
                columnName = replacecolumnName
                columnNameVerbose = replacecolumnNameVerbose
                currRow_bk = $(this).parent().children().eq(allCols.indexOf(columnNameVerbose))
              }
            } else if (
              find_case == "Smaller than equal to" &&
              ((Number(columnText) <= Number(find)) || flag)
            ) {
              if(columnName == replacecolumnName){
                $(this).text(replace);
              }else{
                flag = 1
                bk_index = allCols.indexOf(columnNameVerbose)
                columnName = replacecolumnName
                columnNameVerbose = replacecolumnNameVerbose
                currRow_bk = $(this).parent().children().eq(allCols.indexOf(columnNameVerbose))
              }
            } else if (
              find_case == "Starts with" &&
              (columnText.startsWith(find) || flag)
            ) {
              if(columnName == replacecolumnName){
                $(this).text(replace);
              }else{
                flag = 1
                bk_index = allCols.indexOf(columnNameVerbose)
                columnName = replacecolumnName
                columnNameVerbose = replacecolumnNameVerbose
                currRow_bk = $(this).parent().children().eq(allCols.indexOf(columnNameVerbose))
              }
            } else if (find_case == "Ends with" && (columnText.endsWith(find) || flag)) {
              if(columnName == replacecolumnName){
                $(this).text(replace);
              }else{
                flag = 1
                bk_index = allCols.indexOf(columnNameVerbose)
                columnName = replacecolumnName
                columnNameVerbose = replacecolumnNameVerbose
                currRow_bk = $(this).parent().children().eq(allCols.indexOf(columnNameVerbose))
              }
            } else if (
              find_case == "Not Starts with" &&
              (!columnText.startsWith(find) && flag)
            ) {
              if(columnName == replacecolumnName){
                $(this).text(replace);
              }else{
                flag = 1
                bk_index = allCols.indexOf(columnNameVerbose)
                columnName = replacecolumnName
                columnNameVerbose = replacecolumnNameVerbose
                currRow_bk = $(this).parent().children().eq(allCols.indexOf(columnNameVerbose))
              }
            } else if (
              find_case == "Not Ends with" &&
              (!columnText.endsWith(find) && flag)
            ) {
              if(columnName == replacecolumnName){
                $(this).text(replace);
              }else{
                flag = 1
                bk_index = allCols.indexOf(columnNameVerbose)
                columnName = replacecolumnName
                columnNameVerbose = replacecolumnNameVerbose
                currRow_bk = $(this).parent().children().eq(allCols.indexOf(columnNameVerbose))
              }
            } else if (find_case == "Contains" && (columnText.includes(find) || flag)) {
              if(columnName == replacecolumnName){
                $(this).text(replace);
              }else{
                flag = 1
                bk_index = allCols.indexOf(columnNameVerbose)
                columnName = replacecolumnName
                columnNameVerbose = replacecolumnNameVerbose
                currRow_bk = $(this).parent().children().eq(allCols.indexOf(columnNameVerbose))
              }
            } else if (
              find_case == "Not Contains" &&
              (!columnText.includes(find) && flag)
            ) {
              if(columnName == replacecolumnName){
                $(this).text(replace);
              }else{
                flag = 1
                bk_index = allCols.indexOf(columnNameVerbose)
                columnName = replacecolumnName
                columnNameVerbose = replacecolumnNameVerbose
                currRow_bk = $(this).parent().children().eq(allCols.indexOf(columnNameVerbose))
              }
            }
          }
        });
    });

    if(bk_index > allCols.indexOf(columnNameVerbose)){
      currRow_bk.text(replace);
    }
    showFindTable(
      mainTable,
      columnName,
      replace,
      find_case,
      elementID,
      allCols.indexOf(columnNameVerbose)
    );
  } else {
    showFindTable(
      mainTable,
      columnName,
      find,
      find_case,
      elementID,
      allCols.indexOf(columnNameVerbose)
    );
  }
  $(`#findtext${elementID}`)
    .find("table")
    .DataTable({
      autoWidth: false,
      scrollY: "35vh",
      scrollX: "100%",
      scrollCollapse: true,
      sScrollXInner: "100%",
      ordering: false,
      orderCellsTop: true,
      responsive: true,
      colReorder: {
        fixedColumnsLeft: 1,
      },
      stateSave: true,
      deferRender: true,
      paging: true,
      lengthMenu: [
        [1, 5, 50, -1],
        [1, 5, 50, "All"],
      ],
      stripeClasses: false,
      pageLength: 50,
      dom: "lfBrtip",
      buttons: [],
      columnDefs: [
        {
          targets: "_all",
          className: "dt-center allColumnClass all",
        },
      ],
    });
}
