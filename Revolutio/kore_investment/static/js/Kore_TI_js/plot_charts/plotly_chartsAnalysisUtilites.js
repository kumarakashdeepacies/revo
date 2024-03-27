    //Standardised Listeners
//Set Border Properties
 function setBorderProperties(id6,id_border,id_border_color,id_border_thickness,id_border_style){

  if(id_border){
    $(`#${id_border}`).on('change',function(){
      let div = document.getElementById(id6)
      let checkBox_border = document.getElementById(id_border)
      let borderColor = document.getElementById(id_border_color).value
      let borderThickness = document.getElementById(id_border_thickness).value
      let borderStyle = document.getElementById(id_border_style).value
      change_border_color(div,checkBox_border,borderColor,borderThickness,borderStyle)
    })
  }

  if(id_border_color){
    $(`#${id_border_color}`).on('change',function(){
      let div = document.getElementById(id6)
      let checkBox_border = document.getElementById(id_border)
      let borderColor = document.getElementById(id_border_color).value
      let borderThickness = document.getElementById(id_border_thickness).value
      let borderStyle = document.getElementById(id_border_style).value
      change_border_color(div,checkBox_border,borderColor,borderThickness,borderStyle)
    })
  }

  if(id_border_thickness){
    $(`#${id_border_thickness}`).on('change',function(){
      let div = document.getElementById(id6)
      let borderThickness = document.getElementById(id_border_thickness).value
      let checkBox_border = document.getElementById(id_border)
      let borderColor = document.getElementById(id_border_color).value
      let borderStyle = document.getElementById(id_border_style).value
      change_border_color(div,checkBox_border,borderColor,borderThickness,borderStyle)
    })
  }

  if(id_border_style){
    $(`#${id_border_style}`).on('change',function(){
      let div = document.getElementById(id6)
      let checkBox_border = document.getElementById(id_border)
      let borderColor = document.getElementById(id_border_color).value
      let borderThickness = document.getElementById(id_border_thickness).value
      let borderStyle = document.getElementById(id_border_style).value
      change_border_color(div,checkBox_border,borderColor,borderThickness,borderStyle)
    })
  }}


  // Set Shadow Properties
  function setShadowProperties(id6,id_shadow,id_shadow_color,id_xshadow,id_yshadow,id_blurshadow,id_shadow_thickness){
    if(id_shadow){
      $(`#${id_shadow}`).on('change',function(){
        let div = document.getElementById(id6)
        let checkBox = document.getElementById(id_shadow)
        let shadowColor = document.getElementById(id_shadow_color).value
        let shadowXOffset = document.getElementById(id_xshadow).value
        let shadowYOffset = document.getElementById(id_yshadow).value
        let shadowBlur = document.getElementById(id_blurshadow).value
        let shadowThickness = document.getElementById(id_shadow_thickness).value
        change_shadow_color(div,checkBox,shadowColor,shadowXOffset,shadowYOffset,shadowBlur,shadowThickness)
      })
    }
    if(id_shadow_color){
      $(`#${id_shadow_color}`).on('change',function(){
        let div = document.getElementById(id6)
        let checkBox = document.getElementById(id_shadow)
        let shadowColor = document.getElementById(id_shadow_color).value
        let shadowXOffset = document.getElementById(id_xshadow).value
        let shadowYOffset = document.getElementById(id_yshadow).value
        let shadowBlur = document.getElementById(id_blurshadow).value
        let shadowThickness = document.getElementById(id_shadow_thickness).value
        change_shadow_color(div,checkBox,shadowColor,shadowXOffset,shadowYOffset,shadowBlur,shadowThickness)
      })
    }

    if(id_xshadow){
      $(`#${id_xshadow}`).on('change',function(){
        let div = document.getElementById(id6)
        let checkBox = document.getElementById(id_shadow)
        let shadowColor = document.getElementById(id_shadow_color).value
        let shadowXOffset = document.getElementById(id_xshadow).value
        let shadowYOffset = document.getElementById(id_yshadow).value
        let shadowBlur = document.getElementById(id_blurshadow).value
        let shadowThickness = document.getElementById(id_shadow_thickness).value
        change_shadow_color(div,checkBox,shadowColor,shadowXOffset,shadowYOffset,shadowBlur,shadowThickness)
      })
    }

    if(id_yshadow){
      $(`#${id_yshadow}`).on('change',function(){
        let div = document.getElementById(id6)
        let checkBox = document.getElementById(id_shadow)
        let shadowColor = document.getElementById(id_shadow_color).value
        let shadowXOffset = document.getElementById(id_xshadow).value
        let shadowYOffset = document.getElementById(id_yshadow).value
        let shadowBlur = document.getElementById(id_blurshadow).value
        let shadowThickness = document.getElementById(id_shadow_thickness).value
        change_shadow_color(div,checkBox,shadowColor,shadowXOffset,shadowYOffset,shadowBlur,shadowThickness)
      })
    }

    if(id_blurshadow){
      $(`#${id_blurshadow}`).on('change',function(){
        let div = document.getElementById(id6)
        let checkBox = document.getElementById(id_shadow)
        let shadowColor = document.getElementById(id_shadow_color).value
        let shadowXOffset = document.getElementById(id_xshadow).value
        let shadowYOffset = document.getElementById(id_yshadow).value
        let shadowBlur = document.getElementById(id_blurshadow).value
        let shadowThickness = document.getElementById(id_shadow_thickness).value
        change_shadow_color(div,checkBox,shadowColor,shadowXOffset,shadowYOffset,shadowBlur,shadowThickness)
      })
    }

    if(id_shadow_thickness){
      $(`#${id_shadow_thickness}`).on('change',function(){
        let div = document.getElementById(id6)
        let checkBox = document.getElementById(id_shadow)
        let shadowColor = document.getElementById(id_shadow_color).value
        let shadowXOffset = document.getElementById(id_xshadow).value
        let shadowYOffset = document.getElementById(id_yshadow).value
        let shadowBlur = document.getElementById(id_blurshadow).value
        let shadowThickness = document.getElementById(id_shadow_thickness).value
        change_shadow_color(div,checkBox,shadowColor,shadowXOffset,shadowYOffset,shadowBlur,shadowThickness)
      })
    }

    if(id_shadow){
      $(`#${id_shadow_thickness}`).on('change',function(){
        let div = document.getElementById(id6)
        let checkBox = document.getElementById(id_shadow)
        let shadowColor = document.getElementById(id_shadow_color).value
        let shadowXOffset = document.getElementById(id_xshadow).value
        let shadowYOffset = document.getElementById(id_yshadow).value
        let shadowBlur = document.getElementById(id_blurshadow).value
        let shadowThickness = document.getElementById(id_shadow_thickness).value
        change_shadow_color(div,checkBox,shadowColor,shadowXOffset,shadowYOffset,shadowBlur,shadowThickness)
      })

    }

    }

    //Standardised Functions

    function change_border_color(div,checkBox_border,borderColor,borderThickness,borderStyle){
        if(String(div) !== "null")
        {
        if (String(checkBox_border.checked) === "true"){
            $(`#${div.id}`).css('border',borderThickness+"px " + borderStyle+" "  + borderColor)

           }
        else{
            $(`#${div.id}`).css('border','none')
        }
        $(`#${div.id}`).attr("data-borderon", checkBox_border.checked )
        $(`#${div.id}`).attr("data-borderColor", borderColor)
        $(`#${div.id}`).attr("data-borderThickness", borderThickness)
        $(`#${div.id}`).attr("data-borderStyle", borderStyle)
        }
      }

    function change_shadow_color(div,checkBox,shadowColor,shadowXOffset,shadowYOffset,shadowBlur,shadowThickness){
        if(String(div) !== 'null')
        {
        if (String(checkBox.checked) === "true"){
            $(`#${div.id}`).css('boxShadow',shadowXOffset+"px " + shadowYOffset+"px "  + shadowBlur+"px "  + shadowThickness +"px " + shadowColor)

           }
        else{
            let imtype = ($(`#${div.id}`).attr("data-xaxis")).split(".");
            let imgtype = imtype[imtype.length - 1];
            if(String(imgtype) === "ico"){
                $(`#${div.id}`).css('boxShadow',"none")
            }
            else{
            $(`#${div.id}`).css('boxShadow','0 0 1px rgb(0 0 0 / 13%), 0 1px 3px rgb(0 0 0 / 20%)')
            }
        }

        $(`#${div.id}`).attr("data-shadecolor", shadowColor)
        $(`#${div.id}`).attr("data-shadowon", checkBox.checked)
        $(`#${div.id}`).attr("data-shadowX", shadowXOffset)
        $(`#${div.id}`).attr("data-shadowY", shadowYOffset)
        $(`#${div.id}`).attr("data-shadowblurry", shadowBlur)
        $(`#${div.id}`).attr("data-shadowThick", shadowThickness)
        }
      }




      function change_shadow_global(div,checkBox,shadowColor,shadowXOffset,shadowYOffset,shadowBlur,shadowThickness){
        if(String(div) !== "null")
       {
        if (String(checkBox) === 'true'){
            $(`#${div.id}`).css('boxShadow',shadowXOffset+"px " + shadowYOffset+"px "  + shadowBlur+"px "  + shadowThickness +"px " + shadowColor)

           }

        else{
            let imtype = ($(`#${div.id}`).attr("data-xaxis")).split(".");
            let imgtype = imtype[imtype.length - 1];
            if(String(imgtype) === "ico"){
                $(`#${div.id}`).css('boxShadow',"none")
            }
            else{
            $(`#${div.id}`).css('boxShadow','0 0 1px rgb(0 0 0 / 13%), 0 1px 3px rgb(0 0 0 / 20%)')
            }
        }

        $(`#${div.id}`).attr("data-shadecolor", shadowColor)
        $(`#${div.id}`).attr("data-shadowon", checkBox)
        $(`#${div.id}`).attr("data-shadowX", shadowXOffset)
        $(`#${div.id}`).attr("data-shadowY", shadowYOffset)
        $(`#${div.id}`).attr("data-shadowblurry", shadowBlur)
        $(`#${div.id}`).attr("data-shadowThick", shadowThickness)
        }
      }

      function change_border_global(div,checkBox_border,borderColor,borderThickness,borderStyle){
       if(String(div) !== "null")
       {
        if (String(checkBox_border) === "true"){
            $(`#${div.id}`).css('border',borderThickness+"px " + borderStyle+" "  + borderColor)
            $('.myDiv').css('border',borderThickness+"px " + borderStyle+" "  + borderColor)

           }
        $(`#${div.id}`).attr("data-borderon", checkBox_border )
        $(`#${div.id}`).attr("data-borderColor", borderColor)
        $(`#${div.id}`).attr("data-borderThickness", borderThickness)
        $(`#${div.id}`).attr("data-borderStyle", borderStyle)
       }
      }

      function change_header_color(maindiv,div,color) {
        if(String(div) !== "null" || String(maindiv) !== "null")
        {

            $(`#${div.id}`).closest('.card-header').css('color',color)
            $(`#${maindiv.id}`).attr("data-header_color", color )
        }
      }


      function change_header_bgcolor(maindiv,div,color) {
        if(String(div) !== "null" || String(maindiv) !== "null")
        {
            $(`#${div.id}`).closest('.card-header').css('background-color',color)
            $(`#${maindiv.id}`).attr("data-header_bgcolor", color )
        }
      }


      function change_header_fontsize(maindiv,div,font_size) {
        if(String(div) !== "null" || String(maindiv) !== "null")
        {
            $(`#${div.id}`).find("h5").css('font-size',font_size + 'px')
            $(`#${maindiv.id}`).attr("data-header_fontsize", font_size )
        }
      }

      function change_header_fontweight(maindiv,div,font_weight){
        ((String(div) !== "null") && (String(maindiv) != "null"))
        {
          if((div) != null){
            $(`#${div.id}`).find("h5").css('font-weight',font_weight)
          }
          if(maindiv != null){
            $(`#${maindiv.id}`).attr("data-header_fontweight", font_weight )
          }
        }
      }

      function change_header_fontstyle(maindiv,div,font_style){
        (String(div) !== "null" || String(maindiv) !== "null")
        {
          if((div) != null){
            $(`#${div.id}`).find("h5").css('font-family',font_style)
          }
          if(maindiv != null){
            $(`#${maindiv.id}`).attr("data-header_fontstyle", font_style )
          }
        }
      }

      function change_header_alignment(maindiv,div,alignment){
        if(String(div) !== "null" || String(maindiv) !== "null"){
          if((div) != null){
            $(`#${div.id}`).find("h5").css('text-align',alignment)
          }
          if(maindiv != null){
            $(`#${maindiv.id}`).attr("data-header_alignment", alignment )
          }
        }
      }

  // Toggle Gridlines
  function toggleGridlines(id9,tester){
    document.getElementById(id9).onclick = function () {
        let gridlinesvalue = document.getElementById(id9).value
        var xaxistitle = tester.layout.xaxis.title.text
        let layout2=''
        if (String(gridlinesvalue) === "show_gridlines") {
            layout2 = {
                yaxis: {
                    showgrid: true, automargin: true
                }, xaxis: {
                    showgrid: true, automargin: true, title: {
                        standoff: 20,
                        text: xaxistitle, font: {
                            family: "Arial"
                        }
                    }
                }
            };
            document.getElementById(id9).value = "hide_gridlines"
            document.getElementById(id9).innerHTML = "Hide Gridlines"
        }
        if (String(gridlinesvalue) === "hide_gridlines") {
            layout2 = {
                yaxis: {
                    showgrid: false, automargin: true
                }, xaxis: {
                    showgrid: false, automargin: true, title: {
                        standoff: 20,
                        text: xaxistitle, font: {
                            family: "Arial"
                        }
                    }
                }
            };
            document.getElementById(id9).value = "show_gridlines"
            document.getElementById(id9).innerHTML = "Show Gridlines"

        }
        Plotly.relayout(tester, layout2)
        $(`#${id6}`).attr("data-layout", JSON.stringify(tester.layout))
        let config_gridlines = $(`#${id9}`).val()
        $(`#${id6}`).attr("data-config_gridlines", config_gridlines)
    };
  }


// Set Header Properties PlotFunction
  function setPlotConfigHeaderProperties(id_header,id6,id_header_alignment,id_header_fontstyle,id_header_bgcolor,id_header_color,id_header_fontsize,id_header_fontweight,){
    let div = ''
    let main_div = ''
    document.getElementById(id_header_alignment).onchange = function () {

        div = document.getElementById(id_header)
        main_div = document.getElementById(id6)
        let alignment = $(this).val()
        change_header_alignment(main_div,div,alignment)
    };
    document.getElementById(id_header_fontstyle).onchange = function () {
        div = document.getElementById(id_header)
        main_div = document.getElementById(id6)
        let font_style = $(this).val()
        change_header_fontstyle(main_div,div,font_style)
    };

    document.getElementById(id_header_bgcolor).onchange = function () {
        div = document.getElementById(id_header)
        main_div = document.getElementById(id6)
        let color = $(this).val()
        change_header_bgcolor(main_div,div,color)
    };
    document.getElementById(id_header_color).onchange = function () {
        div = document.getElementById(id_header)
        let color = $(this).val()
        main_div = document.getElementById(id6)
        change_header_color(main_div,div,color)
    };
    document.getElementById(id_header_fontsize).onchange = function () {
        div = document.getElementById(id_header)
        let font_size = $(this).val()
        main_div = document.getElementById(id6)
        change_header_fontsize(main_div,div,font_size)
    };
    document.getElementById(id_header_fontweight).onchange = function () {
        div = document.getElementById(id_header)
        let font_weight = $(this).val()
        main_div = document.getElementById(id6)
        change_header_fontweight(main_div,div,font_weight)
    };
  }
  //for change label color and font size of the charts
  var graph_subtype_array = ["Bubble_Chart", "Vertical_Bar","Vertical_Bar_Stacked","Vertical_Bar_Grouped","Horizontal_Bar","Horizontal_Bar_Stacked","Horizontal_Bar_Grouped","Scatter","Scatter_with_Straight_Lines_and_Markers","Horizontal_Dot_Plot","Line","Vertical_Line_Stacked","Stepped_Line",
  "Vertical_Area","Vertical_Area_Stacked", "Horizontal_Area","Horizontal_Area_Stacked","Vertical_Waterfall","Vertical_Waterfall_Grouped","Horizontal_Waterfall_Grouped","Horizontal_Waterfall","Vertical_Box","Vertical_Grouped_Box","Horizontal_Box","Horizontal_Grouped_Box",
  "Vertical_Histogram","Cumulative_Histogram","Horizontal_Histogram","2D_Histogram_Contour","Stacked_Histogram","Vertical_Violin","Horizontal_Violin","Vertical_Grouped_Violin","Horizontal_Grouped_Violin","Bar_Grouped_and_Line","Bar_Stacked_and_Line","Bar_Stacked_and_Multiple_Line",'Multiple_Line_Chart','Funnel','Funnel_Stacked']

  function setPlotConfigLabelProperties(id6,id,id_label_color,id_label_fontsize,graph_subtype, dataplot, layout){
    let color
    let fontsize
    // let maindiv
    if(graph_subtype_array.includes(graph_subtype)){
      if(layout){
        if(layout.xaxis.title){
          if (layout.xaxis.title.font.color) {
            let id_label_color_value = layout.xaxis.title.font.color;
            document.getElementById(id_label_color).value = id_label_color_value;
            document.getElementById(id_label_color).dispatchEvent(new Event('change'));
          }
          if(layout.xaxis.title.font.size){
            let id_label_fontsize_value = layout.xaxis.title.font.size;
            document.getElementById(id_label_fontsize).value = id_label_fontsize_value;
            document.getElementById(id_label_fontsize).dispatchEvent(new Event('change'));
          }
        }else if(layout.yaxis.title){
          if (layout.yaxis.title.font.color) {
            let id_label_color_value = layout.yaxis.title.font.color;
            document.getElementById(id_label_color).value = id_label_color_value;
            document.getElementById(id_label_color).dispatchEvent(new Event('change'));
          }
          if(layout.yaxis.title.font.size){
            let id_label_fontsize_value = layout.yaxis.title.font.size;
            document.getElementById(id_label_fontsize).value = id_label_fontsize_value;
            document.getElementById(id_label_fontsize).dispatchEvent(new Event('change'));
          }
        }

      }
      document.getElementById(id_label_color).onchange = function () {
        var div = document.getElementById(id)
        color = $(this).val()
        main_div = document.getElementById(id6)
        changePlotConfigLabelProperties(main_div, div, graph_subtype, color, fontsize, id, dataplot, layout)
      };
      document.getElementById(id_label_fontsize).onchange = function () {
        var div = document.getElementById(id)
        fontsize = $(this).val()
        main_div = document.getElementById(id6)
        changePlotConfigLabelProperties(main_div,div,graph_subtype, color, fontsize,id,dataplot, layout)
      };
  }
}


function changePlotConfigLabelProperties(maindiv, div, graph_subtype, color, fontsize, id, dataplot, layout){
  if(graph_subtype_array.includes(graph_subtype) && graph_subtype!=="Funnel" && graph_subtype!=="Funnel_Stacked" && graph_subtype!=="Multiple_Line_Chart"){
    var data_layout = JSON.parse($("#"+maindiv.id).attr('data-layout'))
    if(color){
      if(maindiv){
        if(layout.yaxis.title){
          layout.yaxis.title.font.color = color;
          data_layout.yaxis.title.font['color']=color
        }
        if(layout.xaxis.title){
          layout.xaxis.title.font.color = color;
          data_layout.xaxis.title.font['color']=color
        }
        $("#"+maindiv.id).attr('data-layout', JSON.stringify(data_layout))
        Plotly.update(id, dataplot, layout);
      }
    }if(fontsize){
      if(maindiv){
        if(layout.yaxis.title){
          layout.yaxis.title.font.size = fontsize;
          data_layout.yaxis.title.font['size']=fontsize
        }
        if(layout.xaxis.title){
          layout.xaxis.title.font.size = fontsize;
          data_layout.xaxis.title.font['size']=fontsize
        }

        $("#"+maindiv.id).attr('data-layout',JSON.stringify(data_layout))
        Plotly.update(id, dataplot, layout);
      }
    }
  }
  if(graph_subtype==="Funnel" || graph_subtype==="Funnel_Stacked"){
    var data_layout = JSON.parse($("#"+maindiv.id).attr('data-layout'))
    if(color){
      if(maindiv){
        if(layout.yaxis.title){
          layout.yaxis.title.font.color = color;
          data_layout.yaxis.title.font['color']=color
        }
        $("#"+maindiv.id).attr('data-layout', JSON.stringify(data_layout))
        Plotly.update(id, dataplot, layout);
      }
    }if(fontsize){
      if(maindiv){
        if(layout.yaxis.title){
          layout.yaxis.title.font.size = fontsize;
          data_layout.yaxis.title.font['size']=fontsize
        }
        $("#"+maindiv.id).attr('data-layout',JSON.stringify(data_layout))
        Plotly.update(id, dataplot, layout);
      }
    }
  }

  if(graph_subtype==="Multiple_Line_Chart"){
   var data_layout = JSON.parse($("#"+maindiv.id).attr('data-layout'))
    if(color){
      if(maindiv){
        if(layout.xaxis.title){
          layout.xaxis.title.font.color = color;
          data_layout.xaxis.title.font['color']=color
        }
        $("#"+maindiv.id).attr('data-layout', JSON.stringify(data_layout))
        Plotly.update(id, dataplot, layout);
      }
    }if(fontsize){
      if(maindiv){
        if(layout.xaxis.title){
          layout.xaxis.title.font.size = fontsize;
          data_layout.xaxis.title.font['size']=fontsize
        }
        $("#"+maindiv.id).attr('data-layout',JSON.stringify(data_layout))
        Plotly.update(id, dataplot, layout);
      }
    }
  }
}

  function TableColunmReorder(id6, id_tableColunm_Rearrange, x_axisdata3, id, data, id_tableColunm_Rearrange_ul, id_tableColunm_Rearrange_checkbox,id_tableColunm_Rearrange_div){
     var main_id= id_tableColunm_Rearrange
     var ul2 = $(`#${main_id}`).find('ul')
      for (var i = 0; i < x_axisdata3.length; i++) {
        for (let key in data.mappingDict){
        if(x_axisdata3[i]=== key){
        $(`<li class="btn btn-sm btn-light col" name="${x_axisdata3[i]}" style="height:auto;margin:5px auto;overflow: auto;"> <span class="ui-icon ui-icon-arrowthick-2-n-s float-left mt-1"></span>${data.mappingDict[key]}</li>`).appendTo(ul2)
      }
      }
      }
      ul2.sortable();
      ul2.sortable({
      stop: function(){
        var column_reorder = [];
        var column_reorder1 = [];
        $("#"+id_tableColunm_Rearrange_div).find(".sortable-order").children().each(function() {
          column_reorder.push($(this).attr('name'));
          column_reorder1.push($(this).text().trim())
        });

        ul2.attr("data-column-reorder", JSON.stringify(column_reorder));
        ul2.attr("data-column-reorder1", JSON.stringify(column_reorder1));
      }
     });
      const checkbox = document.getElementById(id_tableColunm_Rearrange_checkbox);
      const TableColumnReorder = document.getElementById(id_tableColunm_Rearrange_div);
      checkbox.addEventListener('change', function() {
          if (this.checked) {
            TableColumnReorder.style.display = 'block';

          } else {
            TableColumnReorder.style.display = 'none';
          }
        });
        var condition_table =  document.getElementById(id_tableColunm_Rearrange)
        if(condition_table ){
          $(`#${main_id} .saveBtn_order`).on("click", function () {
          var TableCol = $(`#${main_id} #${id_tableColunm_Rearrange_ul}`).attr("data-column-reorder")
          var TableCol1 = JSON.parse($(`#${main_id} #${id_tableColunm_Rearrange_ul}`).attr("data-column-reorder1"))
          main_div = document.getElementById(id6)
          function Tablecol_reorder(maindiv) {
            if(String(maindiv) !== "null")
            {
            $(`#${maindiv.id}`).attr("data-xaxis", TableCol)
            }
          }Tablecol_reorder(main_div);

        var label_color =  $(`#${main_div.id}`).attr('data-label_color')
        var label_fontsize =  $(`#${main_div.id}`).attr('data-label_fontsize')
        $(`#table_example${id}`).DataTable().destroy()
        var thead = $(`#table_example${id}`).find('thead tr')
        var tbody = $(`#table_example${id}`).find('tbody')
        thead.empty()
        for (let i = 0; i <  TableCol1.length; i++) {
          $(`<th>${ TableCol1[i]}</th>`).appendTo(thead).css({"color": label_color, "font-size":label_fontsize + "px"})
          }
          tbody.empty();
            for (var i = 0; i < data["content"].length; i++) {
              var tr = $('<tr>');
              for(let j=0; j<TableCol1.length; j++){
                tr.append('<td>' + data["content"][i][TableCol1[j]] + '</td>');
              }
              $(tr).appendTo(tbody);
            }
        var columns = []
        for(let i=0;i<TableCol1.length; i++){
          columns.push({ title: TableCol1[i]})
        }
        $(`#table_example${id}`).DataTable({
          "columns": columns,
          "autoWidth": false,
          "scrollY": "50vh",
          "scrollCollapse": true,
          "scrollX": "110%",
          orderCellsTop: true,
          responsive: true,
          stateSave: true,
          "deferRender": true,
          "paging": true,
          "lengthMenu": [[1, 5, 10, 25, 50, 75, 100, -1], [1, 5, 10, 25, 50, 75, 100, "All"]],
          "pageLength": 10,
          dom: "lfBrtip",
          "sScrollX": "100%",
          "scrollX": true,
          buttons: [
            {
              extend: "collection",
              text: "Export",
              buttons: [
                {
                  extend: "copy",
                  title: "",
                  exportOptions: {
                    columns: ":visible:not(.noVis)"
                  }
                },
                {
                  extend: "excel",
                  title: "",
                  exportOptions: {
                    columns: ":visible:not(.noVis)"
                  }
                },
                {
                  extend: "csv",
                  title: "",
                  exportOptions: {
                    columns: ":visible:not(.noVis)"
                  }
                },
                {
                  extend: "pdf",
                  title: "",
                  exportOptions: {
                    columns: ":visible:not(.noVis)"
                  }
                },
              ],
            },
          ],
          columnDefs: [
            {
              targets: "_all",
              className: "dt-center allColumnClass all buttons_export_class"

            },
          ],
          colReorder: {
            reorderCallback: function () {
            }
          },
        });
        })
      }
      }

function nestedTableColunmReorder(id6,id_nestedtableColunm_Rearrange, y_axisdata3, id, data, id_nestedtableColunm_Rearrange_ul,id_nestedtableColunm_Rearrange_checkbox,id_nestedtableColunm_Rearrange_div ){

    var main_id= id_nestedtableColunm_Rearrange
    var ul2 = $(`#${main_id}`).find('ul')
    for (var i = 0; i < y_axisdata3.length; i++) {
      for (let key in data.mappingDict){
        if(y_axisdata3[i]=== key){
        $(`<li class="btn btn-sm btn-light col" name="${y_axisdata3[i]}" style="height:auto;margin:5px auto;overflow: auto;"> <span class="ui-icon ui-icon-arrowthick-2-n-s float-left mt-1"></span>${data.mappingDict[key]}</li>`).appendTo(ul2)
      }
      }
    }
      ul2.sortable();
      ul2.sortable({
      stop: function(){
        var column_reorder = [];
        var column_reorder1 = [];
        $("#"+id_nestedtableColunm_Rearrange_div).find(".sortable-order").children().each(function() {
          column_reorder.push($(this).attr('name'));
          column_reorder1.push($(this).text().trim())
        });

        ul2.attr("data-column-reorder", JSON.stringify(column_reorder));
        ul2.attr("data-column-reorder1", JSON.stringify(column_reorder1));

      }
    });
        const checkbox = document.getElementById(id_nestedtableColunm_Rearrange_checkbox);
        const TableColumnReorder = document.getElementById(id_nestedtableColunm_Rearrange_div);
        checkbox.addEventListener('change', function() {
          if (this.checked) {
            TableColumnReorder.style.display = 'block';

          } else {
            TableColumnReorder.style.display = 'none';
          }
        });
        var condition_table =  document.getElementById(id_nestedtableColunm_Rearrange)
        if(condition_table ){
          $(`#${main_id} .saveBtn_order1`).on("click", function () {
            let TableCol = $(`#${main_id} #${id_nestedtableColunm_Rearrange_ul}`).attr("data-column-reorder");
            let TableCol1 = JSON.parse($(`#${main_id} #${id_nestedtableColunm_Rearrange_ul}`).attr("data-column-reorder1"));
            let main_div = document.getElementById(id6);
            var label_color =  $(`#${main_div.id}`).attr('data-label_color')
            var label_fontsize =  $(`#${main_div.id}`).attr('data-label_fontsize')
            let b = JSON.parse($(`#${main_div.id}`).attr('data-operation'));
            let selectedCols = JSON.parse(TableCol);
            function Tablecol_reorder(maindiv,b, selectedCols) {
              if(maindiv) {
                $(`#${maindiv.id}`).attr("data-yaxis", TableCol);
                let newA = [];
                let a = y_axisdata3;
                let operation_data1 = [];
                for (let i = 0; i < selectedCols.length; i++) {
                  const col = selectedCols[i];
                  const colIndex = a.indexOf(col);
                  if (colIndex !== -1) {
                    newA.push(col);
                    operation_data1.push(b[colIndex]);
                  }
                }
                $(`#${maindiv.id}`).attr('data-operation', JSON.stringify(operation_data1));
                y_axisdata3 = newA;
                b = operation_data1;
              }
            }
          Tablecol_reorder(main_div, b, selectedCols);
          var columns = [  {title:"Category", field: "Category", width: 150}];
          for(let i=0; i<TableCol1.length; i++){
            columns.push({title:TableCol1[i], field: TableCol1[i]})
          }
          var table = new Tabulator(`#${id}`, {
                            data: data.table_data,
                            layout: "fitDataFill",
                            dataTree:true,
                            dataTreeCollapseElement: "<i class='fas fa-minus tab_minus' style='font-size:0.8rem;color:var(--primary-color)'></i>&nbsp;&nbsp;",
                            dataTreeExpandElement: "<i class='fas fa-plus tab_minus' style='font-size:0.8rem;color:var(--primary-color)'></i>&nbsp;&nbsp;",
                            movableColumns: false,
                            resizableRows: true,
                            columns: columns,

           });
           setTimeout(() => {
            $(`#${id}`).find(".tabulator-sortable").css('color', label_color);
            $(`#${id}`).find(".tabulator-headers").css('font-size', label_fontsize +"px");
           }, 0);
              });
             }
         }


// Change Aces Title
function ChangeAxesTitle(id11,id12,x_axis_title,y_axis_title){
let ChangeAxesTitle=` <label style="font-size:1.1rem">Change the title of the axes:</label>
<input type="text" placeholder="X Axis Title" id="${id11}" size="7" value="${x_axis_title}">
<input type="text" placeholder="Y Axis Title" id="${id12}" size="7" value="${y_axis_title}">`
return ChangeAxesTitle
}

//Global shadow Properties
$('.global_shadow').change(globalShadowFunction)
$('.global_shadow_x').change(globalShadowFunction)
$('.global_shadow_y').change(globalShadowFunction)
$('.global_shadow_blur').change(globalShadowFunction)
$('.global_shadow_thickness').change(globalShadowFunction)
$('.global_shadow_color').change(globalShadowFunction)
function globalShadowFunction () {
  const globalcheckBox = $('.global_shadow').prop('checked')
  const gshadowXOffset = $('.global_shadow_x').val()
  const gshadowYOffset = $('.global_shadow_y').val()
  const gshadowBlur = $('.global_shadow_blur').val()
  const gshadowThickness = $('.global_shadow_thickness').val()
  const gshadowColor = $('.global_shadow_color').val()
  if (String(globalcheckBox) === 'true') {
    $('.myDiv').css('boxShadow', gshadowXOffset + 'px ' + gshadowYOffset + 'px ' + gshadowBlur + 'px ' + gshadowThickness + 'px ' + gshadowColor)
  } else if (String(globalcheckBox) === 'true') {
    $('.myDiv').css('boxShadow', gshadowXOffset + 'px ' + gshadowYOffset + 'px ' + gshadowBlur + 'px ' + gshadowThickness + 'px ' + gshadowColor)
  } else {
    $('.myDiv').css('boxShadow', 'none')
  }
}


// Global Border Properties
$('.global_border').change(globalBorderFunction)
$('.global_border_thickness').change(globalBorderFunction)
$('.global_border_style').change(globalBorderFunction)
$('.global_border_color').change(globalBorderFunction)
function globalBorderFunction () {
  const globalcheckBox = $('.global_border').prop('checked')
  const gborderThickness = $('.global_border_thickness').val()
  const gborderStyle = $('.global_border_style').val()
  const gborderColor = $('.global_border_color').val()
  if (String(globalcheckBox) === 'true') {
    $('.myDiv').css('border', gborderThickness + 'px ' + gborderStyle + ' ' + gborderColor)
  } else if (String(globalcheckBox) === 'true') {
    $('.myDiv').css('border', gborderThickness + 'px ' + gborderStyle + ' ' + gborderColor)
  } else {
    $('.myDiv').css('border', 'none')
  }
}


// Chart Movement Property
$('.charts').draggable({
    containment: 'parent',
    handle: '.handle_for_draggable_charts',
    opacity: 0.5,
    scrollSpeed: 200,
    scrollSensitivity: 100,
    zIndex: 100,
    drag: function (event, ui) {
      const drag_speed = 1 / 0.94
      const initial_left_pos = ui.position.left
      const initial_right_pos = ui.position.right
      const initial_top_pos = ui.position.top
      const initial_bottom_pos = ui.position.bottom
      __dx = (ui.position.left - ui.originalPosition.left) * drag_speed
      __dx1 = (ui.position.right - ui.originalPosition.right) * drag_speed
      __dy = (ui.position.top - ui.originalPosition.top) * drag_speed
      __dy1 = (ui.position.bottom - ui.originalPosition.bottom) * drag_speed
      ui.position.left = ui.originalPosition.left + (__dx)
      ui.position.right = ui.originalPosition.right + (__dx1)
      ui.position.top = ui.originalPosition.top + (__dy)
      ui.position.bottom = ui.originalPosition.bottom + (__dy1)
    }
  })

  $('.draggable_div').draggable({
  containment: 'parent',
  opacity: 0.5,
  scrollSpeed: 200,
  scrollSensitivity: 100

})
$('.datacards').draggable({
  containment: 'parent',
  handle: '.handle_for_draggable_charts',
  opacity: 0.5,
  scrollSpeed: 200,
  scrollSensitivity: 100

})

$('.contentEditable').each(function () {
  $(this).on('click', function () {
    $(this).attr('contenteditable', 'true')
    $(this).focus()
  })
  $(this).focusout(function () {
    $(this).removeAttr('contenteditable')
  })
})

// Jquery draggable
$('.modal-dialog').draggable({
  handle: '.modal-header',
  scrollSpeed: 200,
  scrollSensitivity: 100

})

$('ul.nav-tabs a').click(function (e) {
  e.preventDefault()
  $(this).tab('show')
})


// Container Overflow
  function overflowContainer () {
    const layout = $('.chartDivSection').attr('data-layout')
    let idID
    let idparent = $(this).attr('data-id_parent')
    let topH = ''
    let fullHeight = ''
    let totalHeight = ''
    let fixedHeight = ''
    if (String(layout) === 'Portrait') {
      fixedHeight = 1105
    } else {
      fixedHeight = 715
    }
    if (String($(this).attr('data-event')) === 'hover') {
      $(this).parent().find('.dropdown-content').css('top', '1.5rem')
      idID = $(this).attr('data-id')
      idparent = $(this).attr('data-id_parent')
      topH = parseInt($('#' + idparent).css('top'))
      fullHeight = parseInt($(this).parent().find('.dropdown-content').css('height'))
      totalHeight = topH + fullHeight + 10
      if (totalHeight > fixedHeight) {
        $(this).parent().find('.dropdown-content').css('top', `-${((totalHeight - fixedHeight)) + 3}px`)
      } else {
        $(this).parent().find('.dropdown-content').css('top', '1.5rem')
      }
    } else {
      idID = $(this).attr('data-id')
      idparent = $(this).attr('data-id_parent')
      topH = parseInt($('#' + idparent).css('top'))
      fullHeight = parseInt($('#' + idID).css('height'))
      totalHeight = topH + fullHeight
      if (totalHeight > fixedHeight) {
        setTimeout(() => {
          $('#' + idID).css('top', `${(topH - (totalHeight - fixedHeight)) - 40}px`)
        }, 100)
      }
    }
  }
// Global Apply button
  $('.global_applyButton').on("click",globalApplyButtonClick)
  function globalApplyButtonClick () {
    let elementID = $(this).attr("data_elementid");
    const x = document.getElementById(`myColor${elementID}`).value
    $(`#analysisTabContent${elementID}`).find('.chartDivSection').css('background-color', x)
    $(`#analysisTabContent${elementID}`).find('.chartDivSection').attr('config_background-color', x)
    $(`#analysisDashboard${elementID} .tab-content`).attr('config_background-color', x)
    $(`#analysisTab${elementID}`).find('.nav-link').attr('config_background-color', x)
    if (String($(`#global_bg${elementID}`).val()) === 'background_image') {
      if (String($(`#bg_image_url${elementID}`).html()) !== '' || String($(`#bg_image_url${elementID}`).html()) !== 'undefined') {
        if (String($(`#analysisTabContent${elementID}`).find('.chartDivSection').attr('data-layout')) === 'Landscape') {
          $(`#analysisTabContent${elementID}`).find('.chartDivSection').css('background-size', '1125px 715px')
        } else if (String($(`#analysisTabContent${elementID}`).find('.chartDivSection').attr('data-layout')) === 'Portrait') {
          $(`#analysisTabContent${elementID}`).find('.chartDivSection').css('background-size', '900px 1105px')
        } else {
          $(`#analysisTabContent${elementID}`).find('.chartDivSection').css('background-size', '100%')
        }
        $(`#analysisTabContent${elementID}`).find('.chartDivSection').css('background-image', 'url(data:image/png;base64,' + $(`#bg_image_url${elementID}`).html())
      }
    } else {
      $(`#analysisTabContent${elementID}`).find('.chartDivSection').css('background-size', '14.26% 10em')
      $(`#analysisTabContent${elementID}`).find('.chartDivSection').css({ 'background-image': 'linear-gradient(rgba(0, 0, 0, 1) 0.07px, transparent 0.36%), linear-gradient(90deg, rgba(0, 0, 0, 1) 0.07px, transparent 0.46px)' })
    }
  }

//Gridline Option
function gridLine () {
    let listId = $(this).attr("id");
    if ((String($('.global_bg_selection').val()) === 'background_color') || listId.includes("process")) {
      const grid = $(this).closest('.tab-pane').find('.chartDivSection').css('background-image')
      if (String(grid) === 'none') {
        $(this).closest('.tab-pane').find('.chartDivSection').css({ 'background-image': 'linear-gradient(rgba(0, 0, 0, 1) 0.07px, transparent 0.36%), linear-gradient(90deg, rgba(0, 0, 0, 1) 0.07px, transparent 0.46px)' })
      } else {
        $(this).closest('.tab-pane').find('.chartDivSection').css('background-image', 'none')
      }
    }
  }

// Other Function
function componentToHex (c) {
    const hex = c.toString(16)
    return String(hex.length) === '1' ? '0' + hex : hex
  }

function rgb2hex (red, green, blue) {
    const rgb = blue | (green << 8) | (red << 16)
    return '#' + (0x1000000 + rgb).toString(16).slice(1)
  }

function hex2rgb (colour) {
    let r = ''
    let g = ''
    let b = ''
    if (String(colour.charAt(0)) === '#') {
      colour = colour.substr(1)
    }
    r = colour.charAt(0) + '' + colour.charAt(1)
    g = colour.charAt(2) + '' + colour.charAt(3)
    b = colour.charAt(4) + '' + colour.charAt(5)
    r = parseInt(r, 16)
    g = parseInt(g, 16)
    b = parseInt(b, 16)
    return 'rgb(' + r + ',' + g + ',' + b + ')'
  }


  function gradient_filter (color, length) {
    const colordata = []
    const backRGB = color
    colordata.push(backRGB)
    for (let i = 0; i < length - 1; i++) {
      const previousHex = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(colordata[colordata.length - 1])
      const r = parseInt(previousHex[1], 16) * 0.8
      const g = parseInt(previousHex[2], 16) * 0.8
      const b = parseInt(previousHex[3], 16) * 0.8

      const newHex = '#' + componentToHex(Math.round(r)) + componentToHex(Math.round(g)) + componentToHex(Math.round(b))
      colordata.push(newHex)
    }
    return colordata
  }


  function resetOpacity(modaldiv,typeClass='charts'){
    let chartModal = '.charts'
    if(typeClass==="card_charts"){
        chartModal = '.card charts'
    }
    document.getElementById(modaldiv).style.display = "none"

    $('.charts').each(function () {

        $(this).css('opacity', '')
    })

  }


//   Filter Modal close
  function closeFilterModal(id_filter_close){
    document.getElementById(id_filter_close).onclick = function () {
    let modaldiv = document.getElementById(id_filter_close).parentElement.parentElement.parentElement.id
    document.getElementById(modaldiv).style.display = "none"
    $('.charts').each(function () {
        $(this).css('opacity', '')
    })
  };
  }


//   Conditional Modal close
  function closeConditionModal(id_condition_close){
    document.getElementById(id_condition_close).onclick = function () {
        let modaldiv = document.getElementById(id_condition_close).parentElement.parentElement.parentElement.id
        document.getElementById(modaldiv).style.display = "none"
        $('.charts').each(function () {
            $(this).css('opacity', '')
        })
    };
  }

// Card Resizable Code
function chartResizeable(id6,tester){
        $(`#${id6}`).resizable({
        start: function (event, size) {
            document.getElementById(id6).className = "card charts ui-resizable ui-draggable ui-resizable-resizing"
        },
        stop: function (event, size) {
            let graphheight=''
            if(size.size.height<=250){
              graphheight = size.size.height * 0.700
         }
         else if(size.size.height>250 && size.size.height<=275){
          graphheight = size.size.height * 0.785
          }
            else if(size.size.height>275 && size.size.height<=300){
          graphheight = size.size.height * 0.800
          }
          else if(size.size.height>300 && size.size.height<=350){
            graphheight = size.size.height * 0.820
            }

            else if(size.size.height>350 && size.size.height<=420){
                 graphheight = size.size.height * 0.850
            }
            else if(size.size.height>420 && size.size.height<=450){
              graphheight = size.size.height * 0.870
         }
         else if(size.size.height>450 && size.size.height<=500){
          graphheight = size.size.height * 0.880
     }
         else if(size.size.height>500 && size.size.height<=550){
          graphheight = size.size.height * 0.890
     }
            else if(size.size.height>550 && size.size.height<=650){
              graphheight = size.size.height * 0.900
         }

            else if(size.size.height>650 && size.size.height<=730){
                 graphheight = size.size.height * 0.920
            }
            else if(size.size.height>730){
                 graphheight = size.size.height * 0.945
            }
            else{
                graphheight = size.size.height * 0.895
            }
            let graphwidth = size.size.width * 0.9950
            let layout = { 'height': graphheight, 'width': graphwidth }
            Plotly.relayout(tester, layout)
            $(`#${id6}`).attr("data-layout", JSON.stringify(tester.layout))

        },
    });
}

function myFunction () {
    document.getElementById('myDropdown').classList.toggle('show')
  }


// Reset Cross Filter Fuction
function reset_function (crossfilterdict, axis) {
    const points = crossfilterdict.points

    for (const [key, value] of Object.entries(crossFilterDict1)) {
      if (String(key) === String(crossfilterdict['tab-id'])) {
        for (let i = 0; i < value.length; i++) {
          if (String(value[i].id) === String(crossfilterdict.id)) {
            // var tester1 = JSON.parse($('#'+value[i].id+'card').attr('data-data'))
            const table = $('#' + value[i].id + 'card').attr('data-table_name')
            const col = $('#' + value[i].id + 'card').attr('data-' + axis + 'axis')
            $.ajax({
              url: `/users/${urlPath}/plotly_interaction/`,
              data: {
                operation: 'interaction',
                table: table,
                column: col,
                val: JSON.stringify(crossfilterdict.points)
              },
              type: 'POST',
              dataType: 'json',
              success: function (data) {
                crossfilterFunction(crossfilterdict, data.data, axis, table,data.data2)
              },
              error: function (e) {}
            })
          }
        }
        break
      }
    }
  }


  $('.card_global').click(function () {
    $(this).find('i').toggleClass('fas fa-plus fas fa-minus')
  })

  $('.global_header_color').change(function () {
    const theme = $(this).val()
    $('.inner-div_title').css('color', theme)
  })
  $('.global_header_fontsize').change(function () {
    const theme = $(this).val() + 'px'
    const themeheight = (parseInt($(this).val()) + 20) + 'px'
    $('.inner-div_title').css('font-size', theme)
    $('.inner-div_header').css('height', themeheight)
  })
  $('.global_header_fontstyle').change(function () {
    const theme = $(this).val()
    $('.inner-div_title').css('font-family', theme)
  })
  $('.global_header_alignment').change(function () {
    const theme = $(this).val()
    $('.inner-div_title').css('text-align', theme)
  })
  $('.global_header_fontweight').change(function () {
    const theme = $(this).val()
    $('.inner-div_title').css('font-weight', theme)
  })
  $('.global_header_bgcolor').change(function () {
    const theme = $(this).val()
    $('.inner-div_header').css('background-color', theme)
  })


// Cross Filter Block
function crossfilterFunction (crossfilterdict, data, axis, table,data2) {
    const points = crossfilterdict.points
    for (const [key, value] of Object.entries(crossFilterDict1)) {
      if (String(key) === String(crossfilterdict['tab-id'])) {

        for (let i = 0; i < value.length; i++) {
          try {
            let datadata = ''
            let bool
           let tester1
            if(String(value[i].plot_type) === 'Table'){
              const arr_values = value.map(object => object.plot_type)
            const filtered_values =arr_values.filter(function(value){
              return value != 'Table' && value != 'Aggregation';
          });
          const random = Math.floor(Math.random() * filtered_values.length);
            const index =arr_values.indexOf(filtered_values[random])
                var colName1 = $('#' + value[index].id + 'card').attr('data-' + 'x' + 'axis')
                var colName=Object.keys(data2).find(key => data2[key] === colName1)
            }
            else{
              let response = $('#' + value[i].id + 'card').attr('data-data')
if(response) {
    try {
      tester1 = JSON.parse(response);
    } catch(e) {
      console.log(e)
    }
}

              var colName1 = $('#' + value[i].id + 'card').attr('data-' + 'x' + 'axis')
              var colName=Object.keys(data2).find(key => data2[key] === colName1)
            }
            if (String(value[i].id) !== String(crossfilterdict.id) && $('#' + value[i].id + 'interaction').is(':checked') && (String(table) === String($('#' + value[i].id + 'card').attr('data-table_name')))) {


              if (String(value[i].plot_type) === 'Vertical_Bar' || String(value[i].plot_type) === 'Vertical_Histogram' || String(value[i].plot_type) === 'Cumulative_Histogram' || String(value[i].plot_type) === 'Vertical_Waterfall' || String(value[i].plot_type) === 'Vertical_Area') {
                if (String(value[i].plot_type) === 'Vertical_Area') {

                  for (let j = 0; j < tester1[0].x.length; j++) {
                    if (1) {
                      if (data[colName].includes((tester1[0].x[j]).toString())) {
                        $('#' + value[i].id + 'card').find('.lines').find('path').eq(j).css('opacity', 1)
                      } else {
                        $('#' + value[i].id + 'card').find('.lines').find('path').eq(j).css('opacity', 0.4)
                      }
                    }
                  }
                } else {

                  for (let j = 0; j < tester1[0].x.length; j++) {
                    if (1) {
                      if(data[colName]!=undefined){
                      if (data[colName].includes((tester1[0].x[j]).toString())) {
                        $('#' + value[i].id + 'card').find('.points').find('path').eq(j).css('opacity', 1)
                      } else {
                        $('#' + value[i].id + 'card').find('.points').find('path').eq(j).css('opacity', 0.4)
                      }
                    }
                    }
                  }
                }
              }


              if (String(value[i].plot_type) === 'Bubble_Chart') {

                for (let j = 0; j < tester1[0].x.length; j++) {
                  if (1) {
                    if (data[colName].includes((tester1[0].x[j]).toString())) {
                      $('#' + value[i].id + 'card').find('.points').find('path').eq(j).css('opacity', 0.7)
                      bool = 0
                    } else {
                      $('#' + value[i].id + 'card').find('.points').find('path').eq(j).css('opacity', 0.2)
                    }
                  }
                }
                if (bool) {
                  for (let j = 0; j < tester1[0].y.length; j++) {
                    if (1) {
                      if (data[colName].includes(tester1[0].y[j])) {
                        $('#' + value[i].id + 'card').find('.points').find('path').eq(j).css('opacity', 0.7)
                      } else {
                        $('#' + value[i].id + 'card').find('.points').find('path').eq(j).css('opacity', 0.2)
                      }
                    }
                  }
                }
              }  if (String(value[i].plot_type) === 'Scatter') {
                bool = 1
                for (let j = 0; j < tester1[0].x.length; j++) {
                  if (1) {
                    if (data[colName].includes(tester1[0].x[j])) {
                      $('#' + value[i].id + 'card').find('.points').find('path').eq(j).css('opacity', 1)
                      bool = 0
                    } else {
                      $('#' + value[i].id + 'card').find('.points').find('path').eq(j).css('opacity', 0.2)
                    }
                  }
                }
                if (bool) {
                  for (let j = 0; j < tester1[0].y.length; j++) {
                    if (1) {
                      if (data[colName].includes(tester1[0].y[j])) {
                        $('#' + value[i].id + 'card').find('.points').find('path').eq(j).css('opacity', 1)
                        bool = 0
                      } else {
                        $('#' + value[i].id + 'card').find('.points').find('path').eq(j).css('opacity', 0.2)
                      }
                    }
                  }
                }
              } if (String(value[i].plot_type) === 'Horizontal_Dot_Plot') {
                let bool = 1
                for (let j = 0; j < tester1[0].y.length; j++) {
                  if (1) {
                    if (data[colName].includes(tester1[0].y[j])) {
                      $('#' + value[i].id + 'card').find('.points').find('path').eq(j).css('opacity', 1)
                      bool = 0
                    } else {
                      $('#' + value[i].id + 'card').find('.points').find('path').eq(j).css('opacity', 0.2)
                    }
                  }
                }
                if (bool) {
                  for (let j = 0; j < tester1[0].x.length; j++) {
                    if (1) {
                      if (data[colName].includes(tester1[0].x[j])) {
                        $('#' + value[i].id + 'card').find('.points').find('path').eq(j).css('opacity', 1)
                        bool = 0
                      } else {
                        $('#' + value[i].id + 'card').find('.points').find('path').eq(j).css('opacity', 0.2)
                      }
                    }
                  }
                }
              } if (String(value[i].plot_type) === 'Vertical_Box') {
                let bool = 1
                datadata = [...new Set(tester1[0].x)]
                for (let j = 0; j < datadata.length; j++) {
                  if (1) {
                    if (data[colName].includes((datadata[j]).toString())) {
                      $('#' + value[i].id + 'card').find('.boxes').find('path').eq(j).css('opacity', 1)
                      bool = 0
                    } else {
                      $('#' + value[i].id + 'card').find('.boxes').find('path').eq(j).css('opacity', 0.4)
                    }
                  }
                }
                if (bool) {
                  datadata = [...new Set(tester1[0].y)]
                  for (let j = 0; j < datadata.length; j++) {
                    if (1) {
                      if (data[colName].includes(datadata[j]).toString()) {
                        $('#' + value[i].id + 'card').find('.boxes').find('path').eq(j).css('opacity', 1)
                        bool = 0
                      } else {
                        $('#' + value[i].id + 'card').find('.boxes').find('path').eq(j).css('opacity', 0.4)
                      }
                    }
                  }
                }
              }  if (String(value[i].plot_type) === 'Vertical_Grouped_Box') {
                datadata = [...new Set(tester1[0].x)]
                for (let j = 0; j < datadata.length; j++) {
                  if (1) {
                    if (data[colName].includes((datadata[j]).toString())) {
                      $('#' + value[i].id + 'card').find('.boxes').eq(0).find('path').eq(j).css('opacity', 1)
                      $('#' + value[i].id + 'card').find('.boxes').eq(1).find('path').eq(j).css('opacity', 1)
                    } else {
                      $('#' + value[i].id + 'card').find('.boxes').eq(0).find('path').eq(j).css('opacity', 0.4)
                      $('#' + value[i].id + 'card').find('.boxes').eq(1).find('path').eq(j).css('opacity', 0.4)
                    }
                  }
                }
              }  if (String(value[i].plot_type) === 'Vertical_Grouped_Violin') {
                datadata = [...new Set(tester1[0].x)]
                for (let j = 0; j < datadata.length; j++) {
                  if (1) {
                    if (data[colName].includes((datadata[j]).toString())) {
                      $('#' + value[i].id + 'card').find('.violins').eq(0).find('path').eq(j).css('opacity', 1)
                      $('#' + value[i].id + 'card').find('.violins').eq(1).find('path').eq(j).css('opacity', 1)
                    } else {
                      $('#' + value[i].id + 'card').find('.violins').eq(0).find('path').eq(j).css('opacity', 0.4)
                      $('#' + value[i].id + 'card').find('.violins').eq(1).find('path').eq(j).css('opacity', 0.4)
                    }
                  }
                }
              }  if (String(value[i].plot_type) === 'Horizontal_Grouped_Box') { datadata = [...new Set(tester1[0].y)] }
              for (let j = 0; j < datadata.length; j++) {
                if (1) {
                  if (data[colName].includes(datadata[j])) {
                    $('#' + value[i].id + 'card').find('.boxes').eq(0).find('path').eq(j).css('opacity', 1)
                    $('#' + value[i].id + 'card').find('.boxes').eq(1).find('path').eq(j).css('opacity', 1)
                  } else {
                    $('#' + value[i].id + 'card').find('.boxes').eq(0).find('path').eq(j).css('opacity', 0.4)
                    $('#' + value[i].id + 'card').find('.boxes').eq(1).find('path').eq(j).css('opacity', 0.4)
                  }
                }
              }
            }  if (String(value[i].plot_type) === 'Horizontal_Grouped_Violin') {
              datadata = [...new Set(tester1[0].y)]
              for (let j = 0; j < datadata.length; j++) {
                if (1) {
                  if (data[colName].includes(datadata[j])) {
                    $('#' + value[i].id + 'card').find('.violins').eq(0).find('path').eq(j).css('opacity', 1)
                    $('#' + value[i].id + 'card').find('.violins').eq(1).find('path').eq(j).css('opacity', 1)
                  } else {
                    $('#' + value[i].id + 'card').find('.violins').eq(0).find('path').eq(j).css('opacity', 0.4)
                    $('#' + value[i].id + 'card').find('.violins').eq(1).find('path').eq(j).css('opacity', 0.4)
                  }
                }
              }
            }  else if (String(value[i].plot_type) === 'Horizontal_Box') {
              datadata = [...new Set(tester1[0].y)]
              let bool = 1
              for (let j = 0; j < datadata.length; j++) {
                if (1) {
                  if (data[colName].includes(datadata[j])) {
                    $('#' + value[i].id + 'card').find('.boxes').find('path').eq(j).css('opacity', 1)
                    bool = 0
                  } else {
                    $('#' + value[i].id + 'card').find('.boxes').find('path').eq(j).css('opacity', 0.4)
                  }
                }
              }
              if (bool) {
                datadata = [...new Set(tester1[0].x)]
                for (let j = 0; j < datadata.length; j++) {
                  if (1) {
                    if (data[colName].includes(datadata[j])) {
                      $('#' + value[i].id + 'card').find('.boxes').find('path').eq(j).css('opacity', 1)
                      bool = 0
                    } else {
                      $('#' + value[i].id + 'card').find('.boxes').find('path').eq(j).css('opacity', 0.4)
                    }
                  }
                }
              }
            }  else if (String(value[i].plot_type) === 'Horizontal_Violin') {
              datadata = [...new Set(tester1[0].y)]
              let bool = 1
              for (let j = 0; j < datadata.length; j++) {
                if (1) {
                  if (data[colName].includes(datadata[j])) {
                    $('#' + value[i].id + 'card').find('.violins').find('path').eq(j).css('opacity', 1)
                    bool = 0
                  } else {
                    $('#' + value[i].id + 'card').find('.violins').find('path').eq(j).css('opacity', 0.4)
                  }
                }
              }
            }  else if (String(value[i].plot_type) === 'Vertical_Violin') {
              datadata = [...new Set(tester1[0].x)]
              let bool = 1
              for (let j = 0; j < datadata.length; j++) {
                if (1) {
                  if (data[colName].includes((datadata[j]).toString())) {
                    $('#' + value[i].id + 'card').find('.violins').find('path').eq(j).css('opacity', 1)
                    bool = 0
                  } else {
                    $('#' + value[i].id + 'card').find('.violins').find('path').eq(j).css('opacity', 0.4)
                  }
                }
              }
            } else if (String(value[i].plot_type) === 'Horizontal_Bar' || String(value[i].plot_type) === 'Horizontal_Histogram' || String(value[i].plot_type) === 'Horizontal_Waterfall' || String(value[i].plot_type) === 'Horizontal_Area') {
              if (String(value[i].plot_type) === 'Horizontal_Area') {
                for (let j = 0; j < tester1[0].y.length; j++) {
                  if (1) {
                    if (data[colName].includes(tester1[0].y[j])) {
                      $('#' + value[i].id + 'card').find('.lines').find('path').eq(j).css('opacity', 1)
                    } else {
                      $('#' + value[i].id + 'card').find('.lines').find('path').eq(j).css('opacity', 0.4)
                    }
                  }
                }
              } else {
                for (let j = 0; j < tester1[0].y.length; j++) {
                  if (1) {
                    if (data[colName].includes(tester1[0].y[j])) {
                      $('#' + value[i].id + 'card').find('.points').find('path').eq(j).css('opacity', 1)
                    } else {
                      $('#' + value[i].id + 'card').find('.points').find('path').eq(j).css('opacity', 0.4)
                    }
                  }
                }
              }
            }  else if (String(value[i].plot_type) === 'Vertical_Waterfall_Grouped') {
              for (let j = 0; j < tester1[0].x.length; j++) {
                if (1) {
                  if (data[colName].includes((tester1[0].x[j]).toString())) {
                    $('#' + value[i].id + 'card').find('.bars').eq(0).find('.points').find('path').eq(j).css('opacity', 1)
                    $('#' + value[i].id + 'card').find('.bars').eq(0).find('.regions').find('path').eq(j).css('opacity', 1)
                    $('#' + value[i].id + 'card').find('.bars').eq(1).find('.points').find('path').eq(j).css('opacity', 1)
                    $('#' + value[i].id + 'card').find('.bars').eq(1).find('.regions').find('path').eq(j).css('opacity', 1)
                  } else {
                    $('#' + value[i].id + 'card').find('.bars').eq(0).find('.points').find('path').eq(j).css('opacity', 0.4)
                    $('#' + value[i].id + 'card').find('.bars').eq(0).find('.regions').find('path').eq(j).css('opacity', 0.4)
                    $('#' + value[i].id + 'card').find('.bars').eq(1).find('.points').find('path').eq(j).css('opacity', 0.4)
                    $('#' + value[i].id + 'card').find('.bars').eq(1).find('.regions').find('path').eq(j).css('opacity', 0.4)
                  }
                }
              }
            }  else if (String(value[i].plot_type) === 'Horizontal_Waterfall_Grouped') {
              for (let j = 0; j < tester1[0].y.length; j++) {
                if (1) {
                  if (data[colName].includes(tester1[0].y[j])) {
                    $('#' + value[i].id + 'card').find('.bars').eq(0).find('.points').find('path').eq(j).css('opacity', 1)
                    $('#' + value[i].id + 'card').find('.bars').eq(0).find('.lines').find('path').eq(j).css('opacity', 1)
                    $('#' + value[i].id + 'card').find('.bars').eq(1).find('.points').find('path').eq(j).css('opacity', 1)
                    $('#' + value[i].id + 'card').find('.bars').eq(1).find('.lines').find('path').eq(j).css('opacity', 1)
                  } else {
                    $('#' + value[i].id + 'card').find('.bars').eq(0).find('.points').find('path').eq(j).css('opacity', 0.4)
                    $('#' + value[i].id + 'card').find('.bars').eq(0).find('.lines').find('path').eq(j).css('opacity', 0.4)
                    $('#' + value[i].id + 'card').find('.bars').eq(1).find('.points').find('path').eq(j).css('opacity', 0.4)
                    $('#' + value[i].id + 'card').find('.bars').eq(1).find('.lines').find('path').eq(j).css('opacity', 0.4)
                  }
                }
              }
            }  else if (String(value[i].plot_type) === 'Vertical_Bar_Grouped' || String(value[i].plot_type) === 'Vertical_Bar_Stacked' || String(value[i].plot_type) === 'Bar_Grouped_and_Line' || String(value[i].plot_type) === 'Bar_Stacked_and_Line' || String(value[i].plot_type) === 'Bar_Stacked_and_Multiple_Line') {
              for (let j = 0; j < (tester1[0].x.length); j++) {
                if (1) {
                  if (data[colName].includes((tester1[0].x[j]).toString())) {
                    $('#' + value[i].id + 'card').find('.bars').eq(0).find('path').eq(j).css('opacity', 1)
                    $('#' + value[i].id + 'card').find('.bars').eq(1).find('path').eq(j).css('opacity', 1)
                  } else {
                    $('#' + value[i].id + 'card').find('.bars').eq(0).find('path').eq(j).css('opacity', 0.4)
                    $('#' + value[i].id + 'card').find('.bars').eq(1).find('path').eq(j).css('opacity', 0.4)
                  }
                }
              }
            } else if (String(value[i].plot_type) === 'Funnel_Stacked') {
              for (let j = 0; j < tester1[0].y.length; j++) {
                if (1) {
                  if (data[colName].includes(tester1[0].y[j])) {
                    $('#' + value[i].id + 'card').find('.bars').eq(0).find('.points').find('path').eq(j).css('opacity', 1)
                    $('#' + value[i].id + 'card').find('.bars').eq(0).find('.regions').find('path').eq(j).css('opacity', 1)
                    $('#' + value[i].id + 'card').find('.bars').eq(1).find('.points').find('path').eq(j).css('opacity', 1)
                    $('#' + value[i].id + 'card').find('.bars').eq(1).find('.regions').find('path').eq(j).css('opacity', 1)
                  } else {
                    $('#' + value[i].id + 'card').find('.bars').eq(0).find('.points').find('path').eq(j).css('opacity', 0.4)
                    $('#' + value[i].id + 'card').find('.bars').eq(0).find('.regions').find('path').eq(j).css('opacity', 0.4)
                    $('#' + value[i].id + 'card').find('.bars').eq(1).find('.points').find('path').eq(j).css('opacity', 0.4)
                    $('#' + value[i].id + 'card').find('.bars').eq(1).find('.regions').find('path').eq(j).css('opacity', 0.4)
                  }
                }
              }
            }  else if (String(value[i].plot_type) === 'Horizontal_Bar_Grouped' || String(value[i].plot_type) === 'Horizontal_Bar_Stacked') {
              for (let j = 0; j < tester1[0].y.length; j++) {
                if (1) {
                  if (data[colName].includes(tester1[0].y[j])) {
                    $('#' + value[i].id + 'card').find('.bars').eq(0).find('path').eq(j).css('opacity', 1)
                    $('#' + value[i].id + 'card').find('.bars').eq(1).find('path').eq(j).css('opacity', 1)
                  } else {
                    $('#' + value[i].id + 'card').find('.bars').eq(0).find('path').eq(j).css('opacity', 0.4)
                    $('#' + value[i].id + 'card').find('.bars').eq(1).find('path').eq(j).css('opacity', 0.4)
                  }
                }
              }
            }
            else if (String(value[i].plot_type) === 'Pie_Chart' || String(value[i].plot_type) === 'Treemap' || String(value[i].plot_type) === 'Donut_Chart' || String(value[i].plot_type) === 'Sunburst' || String(value[i].plot_type) === 'Funnel_Area' || String(value[i].plot_type) === 'Funnel') {
              if (String(value[i].plot_type) === 'Funnel') {
                for (let j = 0; j < tester1[0].y.length; j++) {
                  if (1) {
                    if (data[colName].includes(tester1[0].y[j])) {
                      $('#' + value[i].id + 'card').find('.points').find('path').eq(j).css('opacity', 1)
                    } else {
                      $('#' + value[i].id + 'card').find('.points').find('path').eq(j).css('opacity', 0.2)
                    }
                  }
                }
              }

              else if (String(value[i].plot_type) === 'Funnel_Area' ) {
                for (let j = 0; j < tester1[0].text.length; j++) {
                  if (1) {
                    if (data[colName].includes(tester1[0].text[j])) {
                      $('#' + value[i].id + 'card').find('path').eq(j).css('opacity', 1)
                    } else {
                      $('#' + value[i].id + 'card').find('path').eq(j).css('opacity', 0.2)
                    }
                  }
                }

              }
              else if (String(value[i].plot_type) === 'Treemap') {
                for (let j = 0; j < tester1[0].labels.length; j++) {
                  if (1) {
                    if (data[colName].includes(tester1[0].labels[j])) {
                      $('#' + value[i].id + 'card').find('.treemap').find('path').eq(j + 1).css('opacity', 1)
                    } else {
                      $('#' + value[i].id + 'card').find('.treemap').find('path').eq(j + 1).css('opacity', 0.2)
                    }
                  }
                }
              }
              else {
                for (let j = 0; j < tester1[0].labels.length; j++) {
                  if (1) {
                    if (data[colName].includes(tester1[0].labels[j])) {
                      $('#' + value[i].id + 'card').find('path').eq(j).css('opacity', 1)
                    } else {
                      $('#' + value[i].id + 'card').find('path').eq(j).css('opacity', 0.2)
                    }
                  }
                }
              }


            }
            else if(String(value[i].plot_type) === 'Table'){

              let unique_data = [...new Set(data[colName])];
              let regex = ""
              for(let j=0;j<unique_data.length;j++){
                if (j<unique_data.length-1){
                regex += '\\b' + unique_data[j] + '\\b' + '|'
                }
                else{
                  regex += '\\b' + unique_data[j] + '\\b'
                }
              }
              var oTable = $('#table_example' + value[i].id).DataTable();
              var col2 = JSON.parse($('#' + value[i].id + 'card').attr('data-' + 'x' + 'axis'))
              var ind=col2.indexOf(colName1)

oTable.column(ind).search(regex,true,false).draw();

            }
            else if(String(value[i].plot_type) === 'Aggregation'){

              let arr=JSON.parse($('#' + value[i].id + 'card').attr("data-filter_input_final"))

              let obj={...data}


              if(arr.length>0){
              for(let item=0;item<arr.length;item++){
                let col=arr[item]["column_name"]
                 let column=Object.keys(data2).find(key => data2[key] ===col)
                let condition=arr[item]["condition_name"]
                let filter_value =arr[item]["filter_value"]
                let data_category=arr[item]["data_category"]
                let ind =[]
                if(data_category === 'Numerical' && filter_value != ""){
                  if(condition === "Equal to"){
                    ind =obj[column].map((elm, idx) => elm == filter_value ? idx : '').filter(String);
                  }
                  if(condition === "Not Equal to"){

                    ind =obj[column].map((elm, idx) => elm != filter_value ? idx : '').filter(String);
                  }
                  if(condition === "Greater than"){
                    ind =obj[column].map((elm, idx) => elm > filter_value ? idx : '').filter(String);

                  }
                  if(condition === "Smaller than"){
                    ind =obj[column].map((elm, idx) => elm < filter_value ? idx : '').filter(String);

                  }

                }
                else{

                  let cond=''
                  if(filter_value != ""){
                  for(let c=0;c<filter_value.length;c++){
                  if(c!=filter_value.length-1){
                  cond+=`elm == filter_value[${c}] || `
                  }else{
                  cond+=`elm == filter_value[${c}] `
                  }
                  }

                   ind =obj[column].map((elm, idx) => eval(cond) ? idx : '').filter(String);

                }
              }

                 if(filter_value != ""){
                  for (let key in obj) {
                    let newarr=[]
                    if(ind.length>0){
                    for(let a=0;a<obj[key].length;a++){
                    for(let b=0;b<ind.length;b++){
                    if(a==ind[b]){
                    newarr.push(obj[key][a])
                    }

                    }

                    }
                    obj[key]=newarr
                    }
                    else{
                      obj[key]=newarr
                    }
                  }

                }

              }
            }

              let count = obj[colName]
              let unique_data = [...new Set(count)];
              let data_operation =$('#' + value[i].id + 'card').attr('data-' + 'operation')
              if(data_operation === "Count"){
              $('#' + value[i].id + 'card').find('#' + value[i].id + 'xtitle').eq(0).text(count.length)
              }
              else if(data_operation === "Sum"){
                let sum=0
                for(let j=0;j<count.length;j++){
                  sum+=count[j]
                }
                $('#' + value[i].id + 'card').find('#' + value[i].id + 'xtitle').eq(0).text(sum)

              }
              else if(data_operation === "Maximum"){
                let maximum=Math.max(...count)
                $('#' + value[i].id + 'card').find('#' + value[i].id + 'xtitle').eq(0).text(maximum)
              }
              else if(data_operation === "Minimum"){
                let minimum=Math.min(...count)
                $('#' + value[i].id + 'card').find('#' + value[i].id + 'xtitle').eq(0).text(minimum)
              }
              else if(data_operation === "Average"){
                let sum=0
                for(let j=0;j<count.length;j++){
                  sum+=count[j]
                }
                let average=(sum/count.length).toFixed(2)
                $('#' + value[i].id + 'card').find('#' + value[i].id + 'xtitle').eq(0).text(average)

              }
              else if(data_operation === "Median"){
                const median=(values)=>{
                  values.sort(function(a,b){
                    return a-b;
                  });
                  var half = Math.floor(values.length / 2);

                  if (values.length % 2)
                    return values[half];
                  else
                    return (values[half - 1] + values[half]) / 2.0;
                }
                $('#' + value[i].id + 'card').find('#' + value[i].id + 'xtitle').eq(0).text(median(count))

              }
              else if(data_operation === "Count Distinct"){

                let count_dist=unique_data.length
                $('#' + value[i].id + 'card').find('#' + value[i].id + 'xtitle').eq(0).text(count_dist)
              }
              else if(data_operation === "Variance"){
                const findVariance = (arr = []) => {
                  if(!arr.length){
                     return 0;
                  };
                  const sum = arr.reduce((acc, val) => acc + val);
                  const { length: num } = arr;
                  const median = sum / num;
                  let variance = 0;
                  arr.forEach(num => {
                     variance += ((num - median) * (num - median));
                  });
                  variance /= num;
                  return variance;
               };

               $('#' + value[i].id + 'card').find('#' + value[i].id + 'xtitle').eq(0).text(findVariance(count))

              }
              else if(data_operation ==="Standard Deviation"){
                const getStandardDeviation = (array)=> {
                  const n = array.length
                  const mean = array.reduce((a, b) => a + b) / n
                  return Math.sqrt(array.map(x => Math.pow(x - mean, 2)).reduce((a, b) => a + b) / n)
                }
                $('#' + value[i].id + 'card').find('#' + value[i].id + 'xtitle').eq(0).text(getStandardDeviation (count))
              }
              else if(data_operation ==="Kurtosis"){
                const findKurtosis=(x) =>{
                  var n = x.length;
                var sum = x.reduce((partialSum, a) => partialSum + a, 0);
                  var meanValue = sum / x.length;
                  var tempValue;
                  var secondCentralMoment = 0;
                  var fourthCentralMoment = 0;
                  for (var j = 0; j < n; j++) {
                      tempValue = x[j] - meanValue;
                      secondCentralMoment += tempValue * tempValue;
                      fourthCentralMoment += tempValue * tempValue * tempValue * tempValue;
                  }
                  return (
                      ((n - 1) / ((n - 2) * (n - 3))) *
                      ((n * (n + 1) * fourthCentralMoment) /
                          (secondCentralMoment * secondCentralMoment) -
                          3 * (n - 1))
                  )
                }
                $('#' + value[i].id + 'card').find('#' + value[i].id + 'xtitle').eq(0).text(findKurtosis(count))
              }
              else if(data_operation ==="Skewness"){
                const findSkewness=(x)=> {

                  var sum = x.reduce((partialSum, a) => partialSum + a, 0);
                    var meanValue = sum / x.length;
                      var tempValue;
                      var sumSquaredDeviations = 0;
                      var sumCubedDeviations = 0;

                      for (var j = 0; j < x.length; j++) {
                          tempValue = x[j] - meanValue;
                          sumSquaredDeviations += tempValue * tempValue;
                          sumCubedDeviations += tempValue * tempValue * tempValue;
                      }
                      var besselsCorrection = x.length - 1;
                      var theSampleStandardDeviation = Math.sqrt(
                          sumSquaredDeviations / besselsCorrection
                      );
                      var n = x.length;
                      var cubedS = Math.pow(theSampleStandardDeviation, 3);

                      return (n * sumCubedDeviations) / ((n - 1) * (n - 2) * cubedS);
                  }
                $('#' + value[i].id + 'card').find('#' + value[i].id + 'xtitle').eq(0).text(findSkewness(count))
              }
              else if(data_operation ==="First"){
                let first = count[0]
                $('#' + value[i].id + 'card').find('#' + value[i].id + 'xtitle').eq(0).text(first)
              }
              else if(data_operation ==="Last"){
               let last = count[count.length-1]
                $('#' + value[i].id + 'card').find('#' + value[i].id + 'xtitle').eq(0).text(last)

              }
              else if(data_operation ==="Top N" || data_operation ==="Bottom N"){
                let count_sort
                let unique_sort
                if(data_operation ==="Top N"){
                   count_sort=count.sort((a,b)=>{return b-a});
                   unique_sort=unique_data.sort((a,b)=>{return b-a});

                }
                else{
                   count_sort=count.sort((a,b)=>{return a-b});
                   unique_sort=unique_data.sort((a,b)=>{return a-b});
                }

                let data_operation_n =$('#' + value[i].id + 'card').attr('data-' + 'operation_n') //sum
                let data_computed_number=$('#' + value[i].id + 'card').attr('data-' + 'computed_number') //5
                let data_agg_distinct=JSON.parse($('#' + value[i].id + 'card').attr('data-' + 'agg_distinct'))//true
                if(data_operation_n === "Sum"){
                  let sum=0
                  if(data_agg_distinct){
                    if(data_computed_number>unique_sort.length){
                    for(let j=0;j<unique_sort.length;j++){
                      sum+=unique_sort[j]
                      }
                    }
                    else{
                      for(let j=0;j<data_computed_number;j++){
                        sum+=unique_sort[j]
                        }
                    }
                  }
                  else{
                    if(data_computed_number>count_sort.length){
                    for(let j=0;j<count_sort.length;j++){
                      sum+=count_sort[j]
                      }
                    }
                    else{
                      for(let j=0;j<data_computed_number;j++){
                        sum+=count_sort[j]
                        }
                      }
                  }
                  $('#' + value[i].id + 'card').find('#' + value[i].id + 'xtitle').eq(0).text(sum)

                }
                else if(data_operation_n === "Maximum" || data_operation_n === "Minimum"){
                  if(data_operation_n === "Maximum"){
                    let max=count_sort[0]
                  $('#' + value[i].id + 'card').find('#' + value[i].id + 'xtitle').eq(0).text(max)
                }else{
                  let min
                  if(data_agg_distinct){
                    min=unique_sort.slice(0,data_computed_number)
                  }
                  else{
                   min=count_sort.slice(0,data_computed_number)
                  }
                  $('#' + value[i].id + 'card').find('#' + value[i].id + 'xtitle').eq(0).text(min[min.length-1])
                }

                }
                else if(data_operation_n === "Count" || data_operation_n === "Count Distinct"){
                  let sub_count
                  if(data_agg_distinct || data_operation_n === "Count Distinct"){
                    sub_count=unique_sort.slice(0,data_computed_number)
                  }
                  else{
                    sub_count=count_sort.slice(0,data_computed_number)
                  }
                  $('#' + value[i].id + 'card').find('#' + value[i].id + 'xtitle').eq(0).text(sub_count.length)
                  }
                  else if(data_operation_n === "Average"){
                    let sum=0
                    let average
                    let avg_arr
                    if(data_agg_distinct){
                      avg_arr=unique_sort.slice(0,data_computed_number)
                      for (let j=0;j<avg_arr.length;j++){
                        sum+=avg_arr[j]
                      }
                      average=(sum/avg_arr.length).toFixed(2)

                    }
                    else{
                      avg_arr=count_sort.slice(0,data_computed_number)
                      for (let j=0;j<avg_arr.length;j++){
                        sum+=avg_arr[j]
                      }
                      average=(sum/avg_arr.length).toFixed(2)

                    }
                    $('#' + value[i].id + 'card').find('#' + value[i].id + 'xtitle').eq(0).text(average)
                    }
                    else if(data_operation_n === "Median"){
                      let med_arr
                      const median=(values)=>{
                        values.sort(function(a,b){
                          return a-b;
                        });
                        var half = Math.floor(values.length / 2);

                        if (values.length % 2)
                          return values[half];
                        else
                          return (values[half - 1] + values[half]) / 2.0;
                      }
                      if(data_agg_distinct){
                        med_arr=unique_sort.slice(0,data_computed_number)
                      }
                      else{
                        med_arr=count_sort.slice(0,data_computed_number)
                      }
                      $('#' + value[i].id + 'card').find('#' + value[i].id + 'xtitle').eq(0).text(median(med_arr))

                    }

                    else if(data_operation_n === "Variance"){
                      let var_arr
                      const findVariance = (arr = []) => {
                        if(!arr.length){
                           return 0;
                        };
                        const sum = arr.reduce((acc, val) => acc + val);
                        const { length: num } = arr;
                        const median = sum / num;
                        let variance = 0;
                        arr.forEach(num => {
                           variance += ((num - median) * (num - median));
                        });
                        variance /= num;
                        return variance;
                     };
                      if(data_agg_distinct){
                        var_arr=unique_sort.slice(0,data_computed_number)
                      }
                      else{
                        var_arr=count_sort.slice(0,data_computed_number)
                      }
                      $('#' + value[i].id + 'card').find('#' + value[i].id + 'xtitle').eq(0).text(findVariance(var_arr))

                    }
                    else if(data_operation_n === "Standard Deviation"){
                      let std_dev
                      const getStandardDeviation = (array)=> {
                        const n = array.length
                        const mean = array.reduce((a, b) => a + b) / n
                        return Math.sqrt(array.map(x => Math.pow(x - mean, 2)).reduce((a, b) => a + b) / n)
                      }
                      if(data_agg_distinct){
                        std_dev=unique_sort.slice(0,data_computed_number)
                      }
                      else{
                        std_dev=count_sort.slice(0,data_computed_number)
                      }
                      $('#' + value[i].id + 'card').find('#' + value[i].id + 'xtitle').eq(0).text(getStandardDeviation(std_dev))
                    }
                    else if(data_operation_n === "Kurtosis"){
                      let kurtosis
function findKurtosis(x) {
  var n = x.length;
var sum = x.reduce((partialSum, a) => partialSum + a, 0);
  var meanValue = sum / x.length;
  var tempValue;
  var secondCentralMoment = 0;
  var fourthCentralMoment = 0;
  for (var j = 0; j < n; j++) {
      tempValue = x[j] - meanValue;
      secondCentralMoment += tempValue * tempValue;
      fourthCentralMoment += tempValue * tempValue * tempValue * tempValue;
  }

  return (
      ((n - 1) / ((n - 2) * (n - 3))) *
      ((n * (n + 1) * fourthCentralMoment) /
          (secondCentralMoment * secondCentralMoment) -
          3 * (n - 1))
  )
}
if(data_agg_distinct){
  kurtosis=unique_sort.slice(0,data_computed_number)
}
else{
  kurtosis=count_sort.slice(0,data_computed_number)
}
$('#' + value[i].id + 'card').find('#' + value[i].id + 'xtitle').eq(0).text(findKurtosis(kurtosis))

                    }
                    else if(data_operation_n === "Skewness"){
                      let skewness
                      const findSkewness=(x)=> {
                        var sum = x.reduce((partialSum, a) => partialSum + a, 0);
                          var meanValue = sum / x.length;
                            var tempValue;
                            var sumSquaredDeviations = 0;
                            var sumCubedDeviations = 0;

                            for (var j = 0; j < x.length; j++) {
                                tempValue = x[j] - meanValue;
                                sumSquaredDeviations += tempValue * tempValue;
                                sumCubedDeviations += tempValue * tempValue * tempValue;
                            }
                            var besselsCorrection = x.length - 1;
                            var theSampleStandardDeviation = Math.sqrt(
                                sumSquaredDeviations / besselsCorrection
                            );
                            var n = x.length;
                            var cubedS = Math.pow(theSampleStandardDeviation, 3);

                            return (n * sumCubedDeviations) / ((n - 1) * (n - 2) * cubedS);
                        }
if(data_agg_distinct){
  skewness=unique_sort.slice(0,data_computed_number)
}
else{
  skewness=count_sort.slice(0,data_computed_number)
}
$('#' + value[i].id + 'card').find('#' + value[i].id + 'xtitle').eq(0).text(findSkewness(skewness))
                    }

               }

            }

          } finally {}
        }
      }
      break
    }
  }


// Save Group Plot
function saveGroupConfigAnalysis (analysisElementID, groupname) {
  const analysisFinalJson = {}
  let drange = "";
  let url_string = window.location.pathname
  let f_occ = url_string.indexOf('/', url_string.indexOf('/') + 1)
  let s_occ = url_string.indexOf('/', url_string.indexOf('/') + f_occ +1)
  let t_occ = url_string.indexOf('/', url_string.indexOf('/') + s_occ +1)
  let app_code2 = url_string.substring(f_occ+1,s_occ)
  let current_dev_mode2 = url_string.substring(s_occ+1,t_occ)
  if(current_dev_mode2 != "Build" && current_dev_mode2 != "Edit"){
    current_dev_mode2 = "User"
  }
  analysisFinalJson.ElementID = analysisElementID
  if ($(`#${analysisElementID + '-tab'}`).children()[0] != undefined) {
    analysisFinalJson.ParentL3Name = $(`#${analysisElementID + '-tab'}`).children()[0].innerText
  } else {
    analysisFinalJson.ParentL3Name = $(`#${analysisElementID + '_tab_content'}`).attr('data-header_name')
  }
  analysisFinalJson.ParentULID = 'analysisTab' + analysisElementID
  analysisFinalJson.ParentTabContainerID = 'analysisTabContent' + analysisElementID
  const analysisSubTabDetails = []
  const interaction = []
  let indexTab_ = false;
  $(`#analysisTab${analysisElementID}`).find('.nav-link').each(function () {
    if(($(this).attr("id")).includes("indexTab")){
      indexTab_ = true;
    }
  })
  analysisFinalJson.indexTab = indexTab_;
  $(`#analysisTab${analysisElementID}`).find('.nav-link').each(function () {
    const parentId = $(this).closest('.nav-tabs').attr('id').split('analysisTab')[1]
    const tabID = $(this).attr('id').replace('analysistab' + parentId, '')
    let grid = $(`#analysisrow${analysisElementID}${tabID}`).css('background-image')
    if (String(grid) === 'none') {
      grid = 'no'
    } else {
      grid = 'yes'
    }
    const tab_bg = $(`#analysisDashboard${analysisElementID} .tab-content`).attr('config_background-color')
    const indexCardBGColor = $('.indextabBG').val()
    const indexCardFontColor = $('.indextabFC').val()
    const outercolor = $('.themeColor').val()
    const innercolor = $('.themeColor1').val()
    const headercolor = $('.global_header_color').val()
    const headerbgcolor = $('.global_header_bgcolor').val()
    const headerfontsize = $('.global_header_fontsize').val()
    const headerfontweight = $('.global_header_fontweight').val()
    const headerfontstyle = $('.global_header_fontstyle').val()
    const globalheaderalignment = $('.global_header_alignment').val()
    const globalcheckBox = $('.global_shadow').prop('checked')
    const globalcheckBoxborder = $('.global_border').prop('checked')
    const globalshadowColor = $('.global_shadow_color').val()
    const globalshadowXOffset = $('.global_shadow_x').val()
    const globalshadowYOffset = $('.global_shadow_y').val()
    const globalshadowBlur = $('.global_shadow_blur').val()
    const globalshadowThickness = $('.global_shadow_thickness').val()
    const globalborderColor = $('.global_border_color').val()
    const globalborderThickness = $('.global_border_thickness').val()
    const globalborderStyle = $('.global_border_style').val()
    const n = ((windowLocationAttr.href).split('/'))
    const globalbgfolder = n[n.length - 2]
    const globalbgname = $(`#bg_image_name${analysisElementID}`).html()
    const globalbgvalue = $(`#global_bg${analysisElementID}`).val()
    let gcolor = 'no'
    if (String($('.global_gradient_color').prop('checked')) === 'true') {
      gcolor = 'yes'
    }
    let subName = "Index"
    if($(this).find('.tabname')[0] != undefined){
      subName = $(this).find('.tabname')[0].innerText
    }
    const analysisSubTabDict = {
      aID: $(this).attr('id'),
      grid: grid,
      aHref: $(this).attr('href'),
      chartDivContainer: $(this).find('.tabname').attr('data-tab_ct'),
      subTabName: subName,
      commentButtonID: `AddComment${analysisElementID}` + tabID,
      pdfButtonID: `analysisPDF${analysisElementID}` + tabID,
      deleteButtonID: 'removeTab' + analysisElementID + tabID,
      tabHeaderID: `tabHeader${analysisElementID}` + tabID,
      slicerConfigButtonId: `slicerConfig${analysisElementID}` + tabID,
      'tab_background-color': tab_bg,
      outer_color: outercolor,
      inner_color: innercolor,
      g_color: gcolor,
      header_color: headercolor,
      header_bg_color: headerbgcolor,
      header_fontsize: headerfontsize,
      header_fontweight: headerfontweight,
      header_fontstyle: headerfontstyle,
      global_header_alignment: globalheaderalignment,
      global_checkBox: globalcheckBox,
      indexCard_BGColor :indexCardBGColor,
      indexCard_FontColor :indexCardFontColor,
      global_checkBox_border: globalcheckBoxborder,
      global_shadowColor: globalshadowColor,
      global_shadowXOffset: globalshadowXOffset,
      global_shadowYOffset: globalshadowYOffset,
      global_shadowBlur: globalshadowBlur,
      global_shadowThickness: globalshadowThickness,
      global_borderColor: globalborderColor,
      global_borderThickness: globalborderThickness,
      global_borderStyle: globalborderStyle,
      global_bg_name: globalbgname,
      global_bg_value: globalbgvalue,
      global_bg_folder: globalbgfolder
    }
    const tabSlicerConfig = {
      slicerTable: [],
      slicerParameter: [],
      slicerBoolean: [],
      slicerReload : [],
      multipleSlicer:[],
    }
    $(`.selectSlicerConfig_${analysisElementID}${tabID}`).each(function () {
      const slicer_table = $(this).attr('data-slicertable')
      const slicer_param = $(this).attr('data-slicerColumn')
      tabSlicerConfig.slicerTable.push(slicer_table)
      tabSlicerConfig.slicerParameter.push(slicer_param)
      const slicer_reload = $(this).val()
      if ($(this).find("option[value='']").length > 0){
        tabSlicerConfig.slicerBoolean.push("True")
      } else {
        tabSlicerConfig.slicerBoolean.push("False")
      }
      tabSlicerConfig.slicerReload.push(slicer_reload)
      if($(this).attr("multiple")){
        tabSlicerConfig["multipleSlicer"].push(true);
      }else{
        tabSlicerConfig["multipleSlicer"].push(false);
      }
    })
    $('#analysisrow' + analysisElementID + tabID).find('.charts').each(function () {
      const a = $(this).attr('id').split('card')[0]
      interaction.push($('#' + a + 'interaction').prop('checked'))
    })
    analysisSubTabDict.crossFilter = interaction
    analysisSubTabDict.tabSlicerConfig = tabSlicerConfig
    $(`${$(this).attr('href')}`).css('display', 'block')
    const chartDivContainerHeight = $(`#${$(this).find('.tabname').attr('data-tab_ct')}`).height()
    analysisSubTabDict.chartDivContainerHeight = chartDivContainerHeight
    analysisSubTabDetails.push(analysisSubTabDict)
    $(`${$(this).attr('href')}`).css('display', '')
  })
  analysisFinalJson.subTabContent = analysisSubTabDetails
  analysisFinalJson.slicerTabConnectDict = slicerTabConnectDict
  const chartConfigDetails = []
  $(`#analysisTabContent${analysisElementID}`).find('.chartDivSection').each(function () {
    const chartConfigDict = {}
    chartConfigDict.ParentTabID = $(this).parent().attr('id')
    $(`#${$(this).parent().attr('id')}`).css('display', 'block')
    chartConfigDict.ParentContainerID = $(this).attr('id')
    const chartConfigSaveListNew = []
    $(this).find('.charts').each(function () {
      const charttab = $(this).parent().attr('id')
      const fontsize = $(this).find('h5').css('font-size')
      let chartheader = $(this).find('h5')[0].innerText
      const conditionaltable = $(this).attr('data-conditional_table')
      const conditionalcolumnsvalue = $(this).attr('data-conditional_columns_value')
      const headerfontsize = parseInt($(this).attr('data-header_fontsize'))
      const headerfontweight = $(this).attr('data-header_fontweight')
      const headerfontstyle = $(this).attr('data-header_fontstyle')
      const headercolor = $(this).attr('data-header_color')
      const headerbgcolor = $(this).attr('data-header_bgcolor')
      const headeralignment = $(this).attr('data-header_alignment')
      const uniqueid = $(this).attr('data-id')
      const graphsubtype = $(this).attr('data-subtype')
      const tabheight = document.querySelector(`#${charttab}`).offsetHeight
      const tableName = $(this).attr('data-table_name')
      let filtercolumns = ''
      let linecolumn
      let titlefontsize = ''
      let charttitle = ''
      let datavalue = ''
      const bgcolor = $(this).css('background-color')
      let color = $(this).attr('data-color')
      const plotbgcolor = $(this).attr('data-bgcolor')
      const globalbg = $(this).attr('data-globalbg')
      const gradcolor = $(this).attr('data-grad_color')
      const globalbgcolor = $(this).attr('data-global_bg_color')
      const globalindcolor = $(this).attr('data-global_ind_color')
      const configdatavalue = $(this).attr('data-config_data_value')
      const configvaluesize = $(this).attr('data-config_valuesize')
      const configtitlesize = $(this).attr('data-config_titlesize')
      const configcolor = $(this).attr('data-config_color')
      const configgridlines = $(this).attr('data-config_gridlines')
      const configlabels = $(this).attr('data-config_labels')
      let configxrange = $(this).attr('data-config_xrange')
      const configxaxistitle = $(this).attr('data-config_x_axis_title')
      const configyaxistitle = $(this).attr('data-config_y_axis_title')
      const legendx = $(this).attr('data-legend_x')
      const configlabelplacement = $(this).attr('data-config_label_placement')
      const legendy = $(this).attr('data-legend_y')
      const configelementcolor = $(this).attr('data-config_element_color')
      const elementlabel = $(this).attr('data-element_label')
      let filterinputfinal = ''
      if (String(configxrange) === 'undefined') {
        configxrange = ''
      }
      let configyrange = $(this).attr('data-config_yrange')
      if (String(configyrange) === 'undefined') {
        configyrange = ''
      }
      color = $(this).css('background-color')
      const datashadecolor = $(this).attr('data-shadecolor')
      const datashadowX = $(this).attr('data-shadowX')
      const datashadowY = $(this).attr('data-shadowY')
      const datashadowblurry = $(this).attr('data-shadowblurry')
      const datashadowThick = $(this).attr('data-shadowThick')
      const datashadowon = $(this).attr('data-shadowon')
      const databorderColor = $(this).attr('data-borderColor')
      const databorderStyle = $(this).attr('data-borderStyle')
      const databorderThickness = $(this).attr('data-borderThickness')
      const databorderon = $(this).attr('data-borderon')
      let cardheight = $(this).height()
      let cardwidth = $(this).width()
      let layout = ''
      let graphdata = ''
      const changed_text = ''
      if ($(this).attr('data-borderon') == 'true') {
        cardheight = $(this).height() + (2 * databorderThickness)
        cardwidth = $(this).width() + (2 * databorderThickness)
      }

      if ($(this).attr('data-filter_columns') != undefined) {
        filtercolumns = JSON.parse($(this).attr('data-filter_columns'))
      }
      if ($(this).attr('data-filter_input_final') != undefined) {
        filterinputfinal = JSON.parse($(this).attr('data-filter_input_final'))
      }
      if ($(this).attr('data-filter_dtrange') != undefined) {
        drange = JSON.parse($(this).attr('data-filter_dtrange'))
      }
      if (!((String(graphsubtype) === 'Nested_Table') || (String(graphsubtype) === 'Aggregation') || (String(graphsubtype) === 'Image') || (String(graphsubtype) === 'Table'))) {
        layout = $(this).attr('data-layout')
        graphdata = JSON.parse($(this).attr('data-data'))
        changedtext = $(this).attr('data-changed_text')
        if (String($(this).attr('data-line_column')) !== 'undefined') {
          linecolumn = $(this).attr('data-line_column')
        }
      }

      if (String(graphsubtype) === 'Aggregation') {
        titlefontsize = $(this).find('p').css('font-size')
        chartheader = $(this).find('h5')[0].innerText
        charttitle = $(this).find('p')[0].innerText
        datavalue = $(this).find('h5').attr('data_value')
      }
      if (String(graphsubtype) === 'Pie_Chart' || String(graphsubtype) === 'Treemap' || String(graphsubtype) === 'Donut_Chart') {
        graphdata[0].labels = []
        graphdata[0].values = []
      }
      if (String(graphsubtype) === 'Sunburst') {
        graphdata[0].labels = []
        graphdata[0].values = []
        graphdata[0].ids = []
        graphdata[0].parents = []
      }
      if (String(graphsubtype) === 'Vertical_Bar' || String(graphsubtype) === 'Funnel' || String(graphsubtype) === 'Horizontal_Bar' || String(graphsubtype) === 'Line' || String(graphsubtype) === 'Stepped_Line' || String(graphsubtype) === 'Area' || String(graphsubtype) === 'Horizontal_Area' || String(graphsubtype) === 'Scatter' || String(graphsubtype) === '2D_Histogram_Contour' || String(graphsubtype) === 'Vertical_Box' || String(graphsubtype) === 'Horizontal_Box' || String(graphsubtype) === 'Horizontal_Dot_Plot' || String(graphsubtype) === 'Scatter_with_Straight_Lines_and_Markers' || String(graphsubtype) === 'Vertical_Violin' || String(graphsubtype) === 'Horizontal_Violin' || String(graphsubtype) === '3D_Scatter_Plot') {
        graphdata[0].x = []
        graphdata[0].y = []
      }
      if (String(graphsubtype) === '3D_Scatter_Plot') {
        graphdata[0].z = []
      }
      if (String(graphsubtype) === 'Vertical_Waterfall' || String(graphsubtype) === 'Horizontal_Waterfall') {
        graphdata[0].x = []
        graphdata[0].y = []
        graphdata[0].measure = []
      }
      if (String(graphsubtype) === 'Funnel_Area') {
        graphdata[0].text = []
        graphdata[0].values = []
      }
      if (String(graphsubtype) === 'Vertical_Histogram' || String(graphsubtype) === 'Cumulative_Histogram') {
        graphdata[0].x = []
      }
      if (String(graphsubtype) === 'Horizontal_Histogram') {
        graphdata[0].y = []
      }
      if (String(graphsubtype) === 'Angular_Gauge') {
        graphdata[0].value = []
        graphdata[0].title = []
        graphdata[0].gauge.axis.range = []
      }
      if (String(graphsubtype) === 'Bullet_Gauge') {
        graphdata[0].value = []
        graphdata[0].gauge.axis.range = []
      }
      if (String(graphsubtype) === 'Vertical_Bar_Stacked' || String(graphsubtype) === 'Vertical_Grouped_Box' || String(graphsubtype) === 'Vertical_Bar_Grouped' || String(graphsubtype) === 'Vertical_Line_Stacked' || String(graphsubtype) === 'Vertical_Area_Stacked' || String(graphsubtype) === 'Horizontal_Area_Stacked' || String(graphsubtype) === 'Vertical_Waterfall_Grouped' || String(graphsubtype) === 'Horizontal_Bar_Stacked' || String(graphsubtype) === 'Horizontal_Grouped_Box' || String(graphsubtype) === 'Horizontal_Bar_Grouped' || String(graphsubtype) === 'Horizontal_Waterfall_Grouped' || String(graphsubtype) === 'Funnel_Stacked') {
        graphdata[0].x = []
        graphdata[1].x = []
        graphdata[0].y = []
        graphdata[1].y = []
      }
      if (String(graphsubtype) === 'Vertical_Waterfall_Grouped') {
        graphdata[0].measure = []
        graphdata[1].measure = []
      }

      const xaxis = $(this).attr('data-xaxis')
      const yaxis = $(this).attr('data-yaxis')
      const secondcolumn = $(this).attr('data-secondcolumn')
      const computednumber = $(this).attr('data-computed_number')
      const istitle = $(this).attr('data-is_title')
      const titlevalue = $(this).attr('data-title_value')
      const totaly = $(this).attr('data-total_y')
      const operationn = $(this).attr('data-operation_n')
      const aggdistinct = $(this).attr('data-agg_distinct')
      const operation = $(this).attr('data-operation')


      if (!((String(graphsubtype) === 'Nested_Table') || (String(graphsubtype) === 'Aggregation') || (String(graphsubtype) === 'Image') || (String(graphsubtype) === 'Table'))) {
        chartConfigSaveListNew.push({ is_title: istitle, title_value: titlevalue, conditional_columns_value: conditionalcolumnsvalue, conditional_table: conditionaltable, header_alignment: headeralignment, header_fontstyle: headerfontstyle, header_fontsize: headerfontsize, header_fontweight: headerfontweight, header_color: headercolor, header_bgcolor: headerbgcolor, data_shadowon: datashadowon, data_shadecolor: datashadecolor, data_shadowX: datashadowX, data_shadowY: datashadowY, data_shadowblurry: datashadowblurry, data_shadowThick: datashadowThick, data_borderColor: databorderColor, data_borderStyle: databorderStyle, data_borderon: databorderon, data_borderThickness: databorderThickness, total_y: totaly, color: color, plot_bg_color: plotbgcolor, global_bg: globalbg, grad_color: gradcolor, global_bgcolor: globalbgcolor, global_ind_color: globalindcolor, element_label: elementlabel, config_element_color: configelementcolor, config_data_value: configdatavalue, config_valuesize: configvaluesize, config_titlesize: configtitlesize, config_label_placement: configlabelplacement, legend_x: legendx, legend_y: legendy, computed_number: computednumber, operation_n: operationn, agg_distinct: aggdistinct, operation: operation, tableName: tableName, chartheader: chartheader, config_x_axis_title: configxaxistitle, config_y_axis_title: configyaxistitle, config_yrange: configyrange, config_xrange: configxrange, config_gridlines: configgridlines, config_labels: configlabels, x_axis: xaxis, y_axis: yaxis, second_column: secondcolumn, filters: filtercolumns, filter_input_final: filterinputfinal, line_column: linecolumn, height: cardheight, width: cardwidth, position: $(this).position(), layout: JSON.parse(layout), data: graphdata, id: uniqueid, graph_subtype: graphsubtype, changed_text: JSON.parse(changedtext), config_color: configcolor, backgroundcolor: color, drange:drange})
      } else {
        chartConfigSaveListNew.push({ is_title: istitle, title_value: titlevalue, conditional_columns_value: conditionalcolumnsvalue, conditional_table: conditionaltable, header_alignment: headeralignment, header_fontstyle: headerfontstyle, header_fontsize: headerfontsize, header_fontweight: headerfontweight, header_color: headercolor, header_bgcolor: headerbgcolor, data_shadowon: datashadowon, data_shadecolor: datashadecolor, data_shadowX: datashadowX, data_shadowY: datashadowY, data_shadowblurry: datashadowblurry, data_shadowThick: datashadowThick, data_borderColor: databorderColor, data_borderStyle: databorderStyle, data_borderon: databorderon, data_borderThickness: databorderThickness, total_y: totaly, color: color, plot_bg_color: plotbgcolor, global_bg: globalbg, grad_color: gradcolor, global_bgcolor: globalbgcolor, global_ind_color: globalindcolor, element_label: elementlabel, config_element_color: configelementcolor, config_data_value: configdatavalue, config_valuesize: configvaluesize, config_titlesize: configtitlesize, config_label_placement: configlabelplacement, legend_x: legendx, legend_y: legendy, computed_number: computednumber, operation_n: operationn, agg_distinct: aggdistinct, operation: operation, tableName: tableName, chartheader: chartheader, config_x_axis_title: configxaxistitle, config_y_axis_title: configyaxistitle, chart_title: charttitle, config_yrange: configyrange, config_xrange: configxrange, config_gridlines: configgridlines, config_labels: configlabels, data_value: datavalue, x_axis: xaxis, y_axis: yaxis, second_column: secondcolumn, height: cardheight, filters: filtercolumns, filter_input_final: filterinputfinal, height: cardheight, width: cardwidth, position: $(this).position(), id: uniqueid, graph_subtype: graphsubtype, backgroundcolor: color, config_color: configcolor, font_size: fontsize, titlefontsize: titlefontsize, drange:drange})
      }
    })

    $(this).find('.commentboxcard').each(function () {
      const textboxvalue = $(this).find('.commentbox').html()
      const height = $(this).height()
      const width = $(this).width()
      if (String($(this).attr('data-id')) === 'undefined') {
        chartConfigSaveListNew.push({ chartType: 'Textbox', height: height, width: width, position: $(this).position(), textboxvalue: textboxvalue })
      } else {
        const idtexteditor = $(this).attr('data-id')
        chartConfigSaveListNew.push({ chartType: 'Textbox', height: height, width: width, position: $(this).position(), textboxvalue: textboxvalue, id_text_editor: idtexteditor })
      }
    })
    chartConfigDict.chartJson = chartConfigSaveListNew
    chartConfigDetails.push(chartConfigDict)
    $(`#${$(this).parent().attr('id')}`).css('display', '')
  })
  analysisFinalJson.subTabChartDetails = chartConfigDetails

  if ($(`#saveShare${analysisElementID}`).attr('data-custom-message') != undefined){
    custom_messages_in_analysis = $(`#saveShare${analysisElementID}`).attr('data-custom-message')
  } else {
    custom_messages_in_analysis = JSON.stringify({})
  }

  $.ajax({
    url: `/users/${urlPath}/userConfigSave/`,
    data: {
      operation: 'saveGroupAnalysisTab',
      analysisDataDict: JSON.stringify(analysisFinalJson),
      groupname: JSON.stringify(groupname),
      screenURL: windowLocation,
      element_id: analysisElementID,
      custom_messages_in_analysis: custom_messages_in_analysis
    },
    type: 'POST',
    dataType: 'json',
    success: function (data) {
      if($(`#saveShare${analysisElementID}`).attr('data-custom-message') != undefined && $(`#saveShare${analysisElementID}`).attr('data-custom-message') != ''){
        var custom_analysis_message = JSON.parse($(`#saveShare${analysisElementID}`).attr('data-custom-message'))
        Swal.fire({icon: 'success',iconHtml : `<i class = "${custom_analysis_message.icon}"></i>`,text: data["data"]}).then(function(){
          location.reload();
        });
      }else{
        Swal.fire({icon: 'success',text: data["data"]}).then(function(){
          location.reload();
        });
      }
    },
    error: function () {
      Swal.fire({icon: 'error',text: 'Error! Please try again.'});
    }
  })
}

// Plot Filter Function

function plotFilterFunction (tablename, filters) {
  const ajaxdata = {
    tableName: tablename,
    filters: filters,
    operation: 'filter_data'
  }

  $.ajax({
    url: `/users/${urlPath}/create_filter_inputs/`,

    data: ajaxdata,
    type: 'POST',
    dataType: 'json',
    success: function (data) {
      if (data.filter_inputs != undefined) {
        let STRING = `<div class="row"><div class="col-12 card-header" style="font-size: medium; color:var(--primary-color); font-weight: bold;"><input type="checkbox" id="filter_dtrange" onclick="showDaterange.call(this)" class="float-right mt-2 checkboxinput custom-checkbox" style="margin: 0px; margin-left:-11px"><p style="margin:0px;margin-left:-11px">Date Range</p></div><div class="col-12 showrange" style="display:none;">
        <select class="select2 form-control seldatecol"><option value="" disabled selected>------</option></select><div>
        <div style="margin-left:-0.7em;">
        <div class="col-6"> <div class="input-group date">
        <b style="margin-right:1em;font-weight:600;color:var(--primary-color);margin-top: 1rem;">Start Date:</b>
                                <div style="display:flex;">
                                <input type="text" style="width:11rem;" id="startdate" class="datepickerinput p-2 " data-dp-config="{&quot;id&quot;: &quot;dp_2&quot;, &quot;picker_type&quot;: &quot;DATE&quot;, &quot;linked_to&quot;: null, &quot;options&quot;: {&quot;showClose&quot;: true, &quot;showClear&quot;: true, &quot;showTodayButton&quot;: true, &quot;format&quot;: &quot;YYYY-MM-DD&quot;}}">
                                <div class="input-group-addon input-group-append input-group-text" style="padding: 0.40rem .30rem"> <i class="glyphicon glyphicon-calendar"></i></div></div></div></div>

                                <div class="col-6"> <div class="input-group date">
                                <b style="margin-right:1em;font-weight:600;color:var(--primary-color);margin-top: 1rem;">End Date:</b>
                                <div style="display:flex;">
                                                        <input style="width:11rem;" type="text" id="enddate" class="datepickerinput p-2 " data-dp-config="{&quot;id&quot;: &quot;dp_2&quot;, &quot;picker_type&quot;: &quot;DATE&quot;, &quot;linked_to&quot;: null, &quot;options&quot;: {&quot;showClose&quot;: true, &quot;showClear&quot;: true, &quot;showTodayButton&quot;: true, &quot;format&quot;: &quot;YYYY-MM-DD&quot;}}">
                                                        <div class="input-group-addon input-group-append input-group-text" style="padding: 0.40rem .30rem"> <i class="glyphicon glyphicon-calendar"></i></div></div></div></div>
         </div>
     </div></div>`
        cols = []
        cols_ver = []
        for (i in data.filter_inputs) {
          const column_name = data.filter_inputs[i].field_name
          const column_verbose = data.filter_inputs[i].column_name
          const data_type = data.filter_inputs[i].data_type
          if (['CharField', 'TextField', 'DateField', 'DateTimeField', 'TimeField', 'BooleanField'].includes(data_type)) {
            STRING += `<div class="col-12 form-group">
                        <label class="acies_label col-md-12" style="color:var(--primary-color);font-size:larger;margin-left:-0.2rem">${column_verbose}:</label>
                        <select  class="select2 categorical_filter_inputs form-control" name="${column_name}" data-data_type="${data_type}"
                          required multiple>`

            for (j in data.filter_inputs[i].unique_data) {
              STRING += `<option value="${data.filter_inputs[i].unique_data[j]}">${data.filter_inputs[i].unique_data[j]}</option>`
            }
            STRING += '</select></div>'
          }
          if (['AutoField', 'IntegerField','BigIntegerField', 'FloatField'].includes(data_type)) {
            STRING += `<div class="col-12 form-group">
                        <div class=""><b style="font-weight:bold;font-size:larger;color:var(--primary-color)" class="numerical_column_name">${column_verbose}:</b></div>
                        <br>
                        <div class="row">
                        <div class="col-6">
                        <select class="select2 numerical_column_condition" name="${column_name}" data-data_type="${data_type}" required>
                        <option value="Equal to">Equal to</option>
                        <option value="Not Equal to">Not Equal to</option>
                        <option value="Greater than">Greater than</option>
                        <option value="Smaller than">Smaller than</option>
                        <option value="Top N">Top N</option>
                        </select>
                        </div>
                        <div class="col-5">
                        <input type="number" placeholder="${column_verbose}" name="${column_name}_input" style="padding-left:0.5rem" step="any" class="numberinput numerical_column_value form-control">
                        </div>
                        </div>
                        </div>`
          }
          if (['DateField', 'DateTimeField'].includes(data_type)) {
            cols.push(column_name)
            cols_ver.push(column_verbose)
          }
        }
        STRING += '<br></div>'

        $(`.filter_card_body${elementID}`).append(STRING)
        for(let i=0;i<cols.length;i++){
          $('.seldatecol').append(`<option value="${cols[i]}">${cols_ver[i]}</option>`)
        }
        var config = JSON.parse($("#startdate").attr('data-dp-config'));
        $("#startdate").datetimepicker({
            "showClose": true,
            "showClear": true,
            "showTodayButton": true,
            "format": config.options.format,
            "locale": "en"
        });
        $("#enddate").datetimepicker({
          "showClose": true,
          "showClear": true,
          "showTodayButton": true,
          "format": config.options.format,
          "locale": "en"
      });
      $('select.select2:not(.modal select.select2)').each(function(){
        parent = $(this).parent()
        $(this).select2({dropdownParent:parent})
      })
      $('.modal select.select2').each(function(){
        $(this).select2()
      })
      }
    },
    error: function () {

    }
  })
}

// //Gradient Apply Function
function gradientColorApply(id1,id6,id24,tester,colorlength =''){
  $(`#${id24}`).click(function() {
    if(String($(this).prop("checked")) === "true"){
        let color =$(`#${id1}`).val()
        let colordata2 = [];
        let backRGB = $(`#${id1}`).val()
        colordata2.push(backRGB);
        for (let i = 0; i < colorlength-1; i++) {
                let previousHex = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(colordata2[colordata2.length - 1]);
                let r = parseInt(previousHex[1], 16) * 0.8;
                let g = parseInt(previousHex[2], 16) * 0.8;
                let b = parseInt(previousHex[3], 16) * 0.8;
                let newHex = '#' + componentToHex(Math.round(r)) + componentToHex(Math.round(g)) + componentToHex(Math.round(b));
                colordata2.push(newHex)
            }
        let update = { 'marker': { color: colordata2 } };
        Plotly.restyle(tester, update)
        $(`#${id6}`).attr("data-data", JSON.stringify(tester.data))
        $(`#${id6}`).attr("data-grad_color", "yes")
    }
    else{
        let colordata2 = [];
        let backRGB = $(`#${id1}`).val();
        for (let i = 0; i < colorlength; i++) {
            colordata2.push(backRGB);
        }
        let update = { 'marker': { color: colordata2 } };
        Plotly.restyle(tester, update)
        $(`#${id6}`).attr("data-data", JSON.stringify(tester.data))
        $(`#${id6}`).attr("data-grad_color", "no")
    }
    });
}

// Save All Graph Plots

$('#saveall').click(function () {
  let url_string = windowLocation
  let f_occ = url_string.indexOf('/', url_string.indexOf('/') + 1)
  let s_occ = url_string.indexOf('/', url_string.indexOf('/') + f_occ +1)
  let t_occ = url_string.indexOf('/', url_string.indexOf('/') + s_occ +1)
  let app_code2 = url_string.substring(f_occ+1,s_occ)
  let current_dev_mode2 = url_string.substring(s_occ+1,t_occ)
  if(current_dev_mode2 != "Build" && current_dev_mode2 != "Edit"){
    current_dev_mode2 = "User"
  }
  $('.savealltab').each(function () {
    const tabID = $(this).attr('id')
    let chartsavedata = []
    const display = $(this).parent().css('display')
    $(this).parent().css('display', 'block')
    const tabheight = document.querySelector(`#${tabID}`).offsetHeight
    const analysisID = 'analysistab' + tabID.split('w')[1]
    const tabname = $(`#${analysisID}`).children()[0].children[0].innerText
    $('.charts').each(function () {
      const charttab = $(this).parent().attr('id')
      if (String(charttab) === String(tabID)) {
        const chartheader = $(this).find('h5')[0].innerText

        const layout = $(this).attr('data-layout')
        const graphdata = JSON.parse($(this).attr('data-data'))
        const unique_id = $(this).attr('data-id')
        const graphsubtype = $(this).attr('data-subtype')
        const changed_text = $(this).attr('data-changed_text')

        if (String(graphsubtype) === 'Pie_Chart' || String(graphsubtype) === 'Treemap' || String(graphsubtype) === 'Donut_Chart') {
          graphdata[0].labels = []
          graphdata[0].values = []
        }
        if (String(graphsubtype) === 'Sunburst') {
          graphdata[0].labels = []
          graphdata[0].values = []
          graphdata[0].ids = []
          graphdata[0].parents = []
        }
        if (String(graphsubtype) === 'Vertical_Bar' || String(graphsubtype) === 'Funnel' || String(graphsubtype) === 'Horizontal_Bar' || String(graphsubtype) === 'Line' || String(graphsubtype) === 'Stepped_Line' || String(graphsubtype) === 'Area' || String(graphsubtype) === 'Horizontal_Area' || String(graphsubtype) === 'Scatter' || String(graphsubtype) === '2D_Histogram_Contour' || String(graphsubtype) === 'Vertical_Box' || String(graphsubtype) === 'Horizontal_Box' || String(graphsubtype) === 'Horizontal_Dot_Plot' || String(graphsubtype) === 'Scatter_with_Straight_Lines_and_Markers' || String(graphsubtype) === 'Vertical_Violin' || String(graphsubtype) === 'Horizontal_Violin' || String(graphsubtype) === '3D_Scatter_Plot') {
          graphdata[0].x = []
          graphdata[0].y = []
        }
        if (String(graphsubtype) === '3D_Scatter_Plot') {
          graphdata[0].z = []
        }
        if (String(graphsubtype) === 'Vertical_Waterfall' || String(graphsubtype) === 'Horizontal_Waterfall') {
          graphdata[0].x = []
          graphdata[0].y = []
          graphdata[0].measure = []
        }
        if (String(graphsubtype) === 'Funnel_Area') {
          graphdata[0].text = []
          graphdata[0].values = []
        }
        if (String(graphsubtype) === 'Vertical_Histogram' || String(graphsubtype) === 'Cumulative_Histogram') {
          graphdata[0].x = []
        }
        if (String(graphsubtype) === 'Horizontal_Histogram') {
          graphdata[0].y = []
        }
        if (String(graphsubtype) === 'Angular_Gauge') {
          graphdata[0].value = []
          graphdata[0].title = []
          graphdata[0].gauge.axis.range = []
        }
        if (String(graphsubtype) === 'Bullet_Gauge') {
          graphdata[0].value = []
          graphdata[0].gauge.axis.range = []
        }
        if (String(graphsubtype) === 'Vertical_Bar_Stacked' || String(graphsubtype) === 'Vertical_Grouped_Box' || String(graphsubtype) === 'Vertical_Bar_Grouped' || String(graphsubtype) === 'Vertical_Line_Stacked' || String(graphsubtype) === 'Vertical_Area_Stacked' || String(graphsubtype) === 'Horizontal_Area_Stacked' || String(graphsubtype) === 'Vertical_Waterfall_Grouped' || String(graphsubtype) === 'Horizontal_Bar_Stacked' || String(graphsubtype) === 'Horizontal_Grouped_Box' || String(graphsubtype) === 'Horizontal_Bar_Grouped' || String(graphsubtype) === 'Horizontal_Waterfall_Grouped' || String(graphsubtype) === 'Funnel_Stacked') {
          graphdata[0].x = []
          graphdata[1].x = []
          graphdata[0].y = []
          graphdata[1].y = []
        }
        if (String(graphsubtype) === 'Vertical_Waterfall_Grouped') {
          graphdata[0].measure = []
          graphdata[1].measure = []
        }
        const x_axis = $(this).attr('data-xaxis')
        const y_axis = $(this).attr('data-yaxis')
        const second_column = $(this).attr('data-secondcolumn')
        const operation = $(this).attr('data-operation')
        chartsavedata.push({ entity: entity, date: date, model: model, operation: operation, tabheight: tabheight, tab_name: tabname, chartheader: chartheader, x_axis: x_axis, y_axis: y_axis, second_column: second_column, tab_id: tabID, height: $(this).height(), width: $(this).width(), position: $(this).position(), layout: JSON.parse(layout), data: graphdata, id: unique_id, graph_subtype: graphsubtype, changed_text: JSON.parse(changed_text) })
      }
    })
    $('.draggable_charts').each(function () {
      const charttab = $(this).parent().attr('id')
      if (charttab == tabID) {
        const xaxis = $(this).attr('data-xaxis')
        const yaxis = $(this).attr('data-yaxis')
        const secondcolumn = $(this).attr('data-secondcolumn')
        const entity = $(this).attr('data-entity')
        const date = $(this).attr('data-date')
        const model = $(this).attr('data-model')
        const operation = $(this).attr('data-operation')
        const layout = $(this).attr('data-layout')
        const graphdata = $(this).attr('data-data')
        const uniqueid = $(this).attr('data-id')
        const graphsubtype = $(this).attr('data-subtype')
        const backgroundcolor = $(this).css('background-color')
        const valuefontsize = $(this).find('h5').css('font-size')
        const titlefontsize = $(this).find('p').css('font-size')
        chartsavedata.push({ entity: entity, date: date, model: model, operation: operation, tabheight: tabheight, tab_name: tabname, x_axis: xaxis, y_axis: yaxis, second_column: secondcolumn, tab_id: tabID, height: $(this).height(), width: $(this).width(), position: $(this).position(), layout: layout, data: graphdata, id: uniqueid, graph_subtype: graphsubtype, backgroundcolor: backgroundcolor, titlefontsize: titlefontsize, valuefontsize: valuefontsize })
      }
    })
    $('.commentboxcard').each(function () {
      const charttab = $(this).parent().attr('id')
      if (String(charttab) === String(tabID)) {
        const textboxid = $(this).attr('data-tab')
        const textboxvalue = document.getElementById(textboxid).value
        const height = $(`#${textboxid}`).height()
        const width = $(`#${textboxid}`).width()
        chartsavedata.push({ graph_subtype: 'Textbox', tabheight: tabheight, tab_name: tabname, tab_id: tabID, height: height, width: width, position: $(this).position(), textboxvalue: textboxvalue, textboxid: textboxid })
      }
    })
    $(this).parent().css('display', '')

    $.ajax({
      url: '/dashboard/save_plot',
      data: {
        operation: 'savePlotHomePage',
        plotDataList: JSON.stringify(chartsavedata),
        tab_id: tabID,
        tab_name: tabname,
        tabheight: tabheight
      },
      type: 'POST',
      dataType: 'json',
      success: function (data) {
        chartsavedata = []
      },
      error: function () {

      }
    })
  })
})

function showDaterange(){
  if($(this).is(":checked")){
    $(this).parent().parent().find('.showrange').css("display","block")
  }else{
    $(this).parent().parent().find('.showrange').css("display","none")
  }
}