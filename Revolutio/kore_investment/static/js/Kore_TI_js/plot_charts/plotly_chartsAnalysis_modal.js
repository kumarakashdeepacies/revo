function plotlyGraphmodalSelection(modalDataConfig={}){
    let global_bg_checked = "checked='checked'"
    if (modalDataConfig.global_bg == "no") {
        global_bg_checked = ""
    }
    if(modalDataConfig.graph_subtype === 'Image'){
        return $(`
        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right; margin:0em !important;position: absolute;right: 0 ;top : 10px;z-index: 1050">
        <div class="modal-content">
            <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
                <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
                <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close"><span aria-hidden="true">&times;</span></button>
            </div>
            <div class="modal-body" style="max-height:26rem;overflow:auto">
            <label style="font-size:1.1rem">Delete:</label>
            <button type="button" class="btn" id="${modalDataConfig.id5}" data-toggle="button" role="tab" title="Delete Image"
            aria-pressed="false" style="margin-left:-0.2em;line-height: 1.1;" data-second_column="${modalDataConfig.second_column}" data-e_id="${modalDataConfig.e_id}" data-x_axis="${modalDataConfig.mappingDict[modalDataConfig.x_axis]}" data-id="${modalDataConfig.id7}" data-id_parent="${modalDataConfig.id6}"><i class="fa fa-trash"  style="font-size:1.4rem;color:var(--primary-color)"></i></button>
            <label style="font-size:1.1rem">Move:</label>
            <select class="select2" name="move_tab" data-id="${modalDataConfig.id17}" data-id_parent="${modalDataConfig.id6}" id="${modalDataConfig.id16}" style="font-size:1.1rem" >
            </select>
            <br>
                <label style="font-size:1.1rem">Visualization Theme:</label>
                <div class="custom-control custom-checkbox">
                    <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                    <label for="${modalDataConfig.id23}" class="custom-control-label">
                    Global Settings
                    </label>
                </div><br>
            <label style="font-size:1.1rem">Box Shadow</label>
                <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br>
            <label style="font-size:1.1rem">Choose the shadow color:</label>
                <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
            <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
                <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
            <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
                <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
            <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
                <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
            <label style="font-size:1.1rem">Set Shadow Thickness:</label>
                <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
            <label style="font-size:1.1rem">Box Border</label>
                <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br>
            <label style="font-size:1.1rem">Choose the border color:</label>
                <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
            <label style="font-size:1.1rem">Set border thickness</label>
                <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
            <label style="font-size:1.1rem">Choose border style:</label>
                <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
                <option value="solid">Solid</option>
                <option value="dotted">Dotted</option>
                <option value="double">Double</option>
                <option value="dashed">Dashed</option>
                </select>
                <br>
            </div>
        </div>
        </div>
    `)
    }else if(modalDataConfig.graph_subtype === 'Vertical_Bar'){
        return  $(`
                    <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
                    right: 0 ;top : 10px;z-index: 1050">
                    <div class="modal-content">
                    <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
                    <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
                    <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                    </button>
                    </div>
                    <div class="modal-body" style="max-height:26rem;overflow:auto">
                    <label style="font-size:1.1rem">Change the graph color:</label>
                    <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br>
                    <br>
                    <div class="custom-control custom-checkbox">
                        <input type="checkbox" checked="checked" name="defaultValueColorConfig" id="${modalDataConfig.id24}" class="checkboxinput custom-control-input">
                        <label for="${modalDataConfig.id24}" class="custom-control-label">
                        Gradient Color
                        </label>
                    </div><br>
                    <label style="font-size:1.1rem">Change the color or an element:</label>
                    <input type="color" id="${modalDataConfig.id4}" name="favcolor1" value="${modalDataConfig.element_color}">
                    <label style="font-size:1.1rem">Change the graph background:</label>
                    <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                    <label style="font-size:1.1rem">Visualization Theme:</label>
                    <div class="custom-control custom-checkbox">
                        <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                        <label for="${modalDataConfig.id23}" class="custom-control-label">
                        Global Settings
                        </label>
                    </div><br><br>
                    <label style="font-size:1.1rem">Change X and Y axis gridlines:</label>
                        <button type="button" class="btn btn-primary" id="${modalDataConfig.id9}" data-toggle="button" role="tab"
                        aria-pressed="false" autocomplete="off" value="${modalDataConfig.grid_id}" style="line-height: 1.1;">${modalDataConfig.value}</button><br><br>
                        <label style="font-size:1.1rem">Change the range of the axis:</label>
                    <input type="text" placeholder="Y Axis Start" id="${modalDataConfig.id2}" size="7" value="${modalDataConfig.y_axis_start}">
                    <input type="text" placeholder="Y Axis End " id="${modalDataConfig.id3}" size="7" value="${modalDataConfig.y_axis_end}">
                    <br><br>
                    <label style="font-size:1.1rem">Change the title of the axes:</label>
                    <input type="text" placeholder="X Axis Title" id="${modalDataConfig.id11}" size="7" value="${modalDataConfig.x_axis_title}">
                    <input type="text" placeholder="Y Axis Title" id="${modalDataConfig.id12}" size="7" value="${modalDataConfig.y_axis_title}">
                    <br><br>
                    <label style="font-size:1.1rem">Change the label of an element:</label><br>
                    <input type="text" placeholder="X Axis Label" id="${modalDataConfig.id13}" size="9" value="${modalDataConfig.element_label}"> &nbsp;&nbsp;
                    <label style="font-size:1.1rem">Chart interaction:</label>
                    <div class="custom-control custom-checkbox">
                        <input type="checkbox" checked="checked" name="defaultValueConfig" id="${modalDataConfig.id21}" class="checkboxinput custom-control-input">
                        <label for="${modalDataConfig.id21}" class="custom-control-label">
                        Cross-filter
                        </label>
                    </div>
                    <label style="font-size:1.1rem">Connected slicers:</label>
                    <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">
                    </div>
                    <button type="button" class="btn btn-primary" id="${modalDataConfig.id18}" data-toggle="button" role="tab"
                            aria-pressed="false" autocomplete="off" style="line-height: 1.1;">Reset Axis Labels</button><br><br>
                            <label style="font-size:1.1rem">Change Plot Labels:</label>
                    <button type="button" class="btn btn-primary" id="${modalDataConfig.id_labels}" data-toggle="button" role="tab"
                            aria-pressed="false" autocomplete="off" value="${modalDataConfig.label_value}" style="line-height: 1.1;">${modalDataConfig.label_text}</button>
                    <br><br>
                    <label style="font-size:1.1rem">Label Placement:</label>
            <select class="select2" name="position_legends" id="${modalDataConfig.id_label_placement}" style="font-size:1.1rem">
            <option value="">-----</option>
            <option value="inside">Inside</option>
            <option value="outside">Outside</option>
            </select>
            <br><br>
            <label style="font-size:1.1rem">Box Shadow</label>
            <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
            <label style="font-size:1.1rem">Choose the shadow color:</label>
            <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
            <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
            <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
            <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
            <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
            <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
            <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
            <label style="font-size:1.1rem">Set Shadow Thickness:</label>
            <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
            <label style="font-size:1.1rem">Box Border</label>
            <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
            <label style="font-size:1.1rem">Choose the border color:</label>
            <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
            <label style="font-size:1.1rem">Set border thickness</label>
            <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
            <label style="font-size:1.1rem">Choose border style:</label>
            <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
            <option value="solid">Solid</option>
            <option value="dotted">Dotted</option>
            <option value="double">Double</option>
            <option value="dashed">Dashed</option>
            </select>
            <br><br>
            <label style="font-size:1.1rem">Change the header color:</label>
            <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
            <br>
            <label style="font-size:1.1rem">Change the background color of header:</label>
            <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
            <label style="font-size:1.1rem">Set header font size:</label>
            <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
            <label style="font-size:1.1rem">Set header font weight:</label>
            ${modalDataConfig.borderStylehtml}
            <br>
            ${modalDataConfig.setheaderFontHTML}
            <br>
            <label style="font-size:1.1rem">Set header alignment:</label>
            <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
            <option value="">----------</option>
            <option value="left">Left</option>
            <option value="center">Center</option>
            <option value="right">Right</option>
            </select>
            <br>
            <label style="font-size:1.1rem">Set order for X Axis:</label>
            <select class="select2" name="border_style" id="${modalDataConfig.id_axis_order}" style="font-size:1.1rem" onchange="changeOrder.call(this)" data-chart-id = "${modalDataConfig.id6}" datatype_dict = '${JSON.stringify(modalDataConfig.datatype_dict)}' mappingDict = '${JSON.stringify(modalDataConfig.mappingDict)}' order_type = 'Vertical' >
            <option value="" selected>----------</option>
            <option value="asc">Ascending</option>
            <option value="desc">Descending</option>
            <option value="cust">Custom</option>
            </select>
            <br>
            <button class="btn btn-primary btn-xs rounded px-2" id="${modalDataConfig.idOrderModal}Button" data-modal_id="${modalDataConfig.idOrderModal}" data-chart-id = "${modalDataConfig.id6}" data-sorted-values = "" onclick="orderModal.call(this)" datatype_dict = '${JSON.stringify(modalDataConfig.datatype_dict)}' order_type = 'Vertical' style="display:none; height : 30px;">Set preferred order
            </button>
            ${modalDataConfig.optionvaluesHTML}

            <br>
            <label style="font-size:1.1rem">Change labels color:</label>
            <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
            <br>
            <label style="font-size:1.1rem">Set labels font size:</label>
            <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>

            </div>
            </div>
                    `)
    }else if(modalDataConfig.graph_subtype === 'Bubble_Chart'){
        return  $(`

            <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
            right: 0 ;top : 10px;z-index: 1050">
            <div class="modal-content">
            <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
            <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
            <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
                <span aria-hidden="true">&times;</span>
            </button>
            </div>
            <div class="modal-body" style="max-height:26rem;overflow:auto">
            <label style="font-size:1.1rem">Change the graph color:</label>
            <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br>
            <label style="font-size:1.1rem">Change the color or an element:</label>
            <input type="color" id="${modalDataConfig.id4}" name="favcolor1" value="${modalDataConfig.element_color}"><br><br>
            <label style="font-size:1.1rem">Change the graph background:</label>
            <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
            <label style="font-size:1.1rem">Visualization Theme:</label>
            <div class="custom-control custom-checkbox">
            <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
            <label for="${modalDataConfig.id23}" class="custom-control-label">
            Global Settings
            </label></div><br><br>
            <label style="font-size:1.1rem">Change X and Y axis gridlines:</label>
            <button type="button" class="btn btn-primary" id="${modalDataConfig.id9}" data-toggle="button" role="tab"
                aria-pressed="false" autocomplete="off" value="${modalDataConfig.grid_id}" style="line-height: 1.1;">${modalDataConfig.value}</button><br><br>
                <label style="font-size:1.1rem">Change the range of the axis:</label>
                <input type="text" placeholder="Y Axis Start" id="${modalDataConfig.id2}" size="7" value="${modalDataConfig.y_axis_start}">
                <input type="text" placeholder="Y Axis End " id="${modalDataConfig.id3}" size="7" value="${modalDataConfig.y_axis_end}">
                <br><br>
                <label style="font-size:1.1rem">Change the title of the axes:</label>
                <input type="text" placeholder="X Axis Title" id="${modalDataConfig.id11}" size="7" value="${modalDataConfig.x_axis_title}">
                <input type="text" placeholder="Y Axis Title" id="${modalDataConfig.id12}" size="7" value="${modalDataConfig.y_axis_title}">
                <br><br>
                <label style="font-size:1.1rem">Chart interaction:</label>
                <div class="custom-control custom-checkbox">
                    <input type="checkbox" checked="checked" name="defaultValueConfig" id="${modalDataConfig.id21}" class="checkboxinput custom-control-input">
                    <label for="${modalDataConfig.id21}" class="custom-control-label">
                    Cross-filter
                    </label>
                </div>
                <label style="font-size:1.1rem">Change Plot Labels:</label>
                <button type="button" class="btn btn-primary" id="${modalDataConfig.id_labels}" data-toggle="button" role="tab"

                aria-pressed="false" autocomplete="off" value="${modalDataConfig.label_value}" style="line-height: 1.1;">${modalDataConfig.label_text}</button>
                <br><br>
                <label style="font-size:1.1rem">Label Placement:</label>
            <select class="select2" name="position_legends" id="${modalDataConfig.id_label_placement}" style="font-size:1.1rem">
            <option value="">-----</option>
            <option value="top">Top</option>
            <option value="bottom">Bottom</option>
            <option value="center">Center</option>
            </select>
            <br><br>
            <label style="font-size:1.1rem">Box Shadow</label>
            <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
            <label style="font-size:1.1rem">Choose the shadow color:</label>
            <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
            <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
            <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
            <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
            <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
            <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
            <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
            <label style="font-size:1.1rem">Set Shadow Thickness:</label>
            <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
            <label style="font-size:1.1rem">Box Border</label>
            <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
            <label style="font-size:1.1rem">Choose the border color:</label>
            <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
            <label style="font-size:1.1rem">Set border thickness</label>
            <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
            <label style="font-size:1.1rem">Choose border style:</label>
            <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
            <option value="solid">Solid</option>
            <option value="dotted">Dotted</option>
            <option value="double">Double</option>
            <option value="dashed">Dashed</option>
            </select>
            <br><br>
            <label style="font-size:1.1rem">Change the header color:</label>
            <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
            <br>
            <label style="font-size:1.1rem">Change the background color of header:</label>
            <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
            <label style="font-size:1.1rem">Set header font size:</label>
            <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
            <label style="font-size:1.1rem">Set header font weight:</label>

            ${modalDataConfig.borderStylehtml}<br>
            ${modalDataConfig.setheaderFontHTML}
            <br>
            <label style="font-size:1.1rem">Set header alignment:</label>
            <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
            <option value="">----------</option>
            <option value="left">Left</option>
            <option value="center">Center</option>
            <option value="right">Right</option>
            </select>
            <br><br>
            <label style="font-size:1.1rem">Change labels color:</label>
            <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
            <br>
            <label style="font-size:1.1rem">Set labels font size:</label>
            <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>
            </div>
            </div>
            `)
        }else if(modalDataConfig.graph_subtype === 'Vertical_Histogram'){
           return $(`
            <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
            right: 0 ;top : 10px;z-index: 1050">
            <div class="modal-content">
            <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
              <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
              <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
                <span aria-hidden="true">&times;</span>
              </button>
            </div>
            <div class="modal-body" style="max-height:26rem;overflow:auto">
              <label style="font-size:1.1rem">Change the graph color:</label>

            <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br>
            <div class="custom-control custom-checkbox">
                          <input type="checkbox" checked="checked" name="defaultValueColorConfig" id="${modalDataConfig.id24}" class="checkboxinput custom-control-input">
                          <label for="${modalDataConfig.id24}" class="custom-control-label">
                          Gradient Color
                          </label></div>
                      <br>
            <label style="font-size:1.1rem">Change the graph background:</label>
                      <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                      <label style="font-size:1.1rem">Visualization Theme:</label>
                      <div class="custom-control custom-checkbox">
                          <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                          <label for="${modalDataConfig.id23}" class="custom-control-label">
                          Global Settings
                          </label></div><br><br>

            <label style="font-size:1.1rem">Change X and Y axis gridlines:</label>
              <button type="button" class="btn btn-primary" id="${modalDataConfig.id9}" data-toggle="button" role="tab"
                              aria-pressed="false" autocomplete="off" value="${modalDataConfig.grid_id}" style="line-height: 1.1;">${modalDataConfig.value}</button><br><br>
                              <label style="font-size:1.1rem">Change the range of the axis:</label>
            <input type="text" placeholder="Y Axis Start" id="${modalDataConfig.id2}" value="${modalDataConfig.y_axis_start}" size="7">
            <input type="text" placeholder="Y Axis End " id="${modalDataConfig.id3}" value="${modalDataConfig.y_axis_end}" size="7">
            <br><br>
            <label style="font-size:1.1rem">Change the title of the axes:</label>
            <input type="text" placeholder="X Axis Title" id="${modalDataConfig.id11}" value="${modalDataConfig.x_axis_title}" size="7">
            <br><br>
            <label style="font-size:1.1rem">Change the label of an element:</label><br>
            <input type="text" placeholder="X Axis Label" id="${modalDataConfig.id13}" size="9" value="${modalDataConfig.element_label}"> &nbsp;&nbsp;
            <label style="font-size:1.1rem">Connected slicers:</label>
            <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

            </div>
            <button type="button" class="btn btn-primary" id="${modalDataConfig.id18}" data-toggle="button" role="tab"
                              aria-pressed="false" autocomplete="off" style="line-height: 1.1;">Reset Axis Labels</button>
                              <br><br>
                              <label style="font-size:1.1rem">Box Shadow</label>
                              <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                              <label style="font-size:1.1rem">Choose the shadow color:</label>
                              <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
                              <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
                              <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
                              <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
                              <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
                              <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
                              <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
                              <label style="font-size:1.1rem">Set Shadow Thickness:</label>
                              <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
                              <label style="font-size:1.1rem">Box Border</label>
                              <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                              <label style="font-size:1.1rem">Choose the border color:</label>
                              <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
                              <label style="font-size:1.1rem">Set border thickness</label>
                              <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
                              <label style="font-size:1.1rem">Choose border style:</label>
                              <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
                              <option value="solid">Solid</option>
                              <option value="dotted">Dotted</option>
                              <option value="double">Double</option>
                              <option value="dashed">Dashed</option>
                              </select>
                              <br><br>
                              <label style="font-size:1.1rem">Change the header color:</label>
            <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
            <br>
            <label style="font-size:1.1rem">Change the background color of header:</label>
            <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
            <label style="font-size:1.1rem">Set header font size:</label>
            <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
            <label style="font-size:1.1rem">Set header font weight:</label>

            ${modalDataConfig.borderStylehtml}<br>
            ${modalDataConfig.setheaderFontHTML}
            <br>
            <label style="font-size:1.1rem">Set header alignment:</label>
            <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
            <option value="">----------</option>
            <option value="left">Left</option>
            <option value="center">Center</option>
            <option value="right">Right</option>
            </select>
            <br><br>
            <label style="font-size:1.1rem">Change labels color:</label>
            <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
            <br>
            <label style="font-size:1.1rem">Set labels font size:</label>
            <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>
            </div>
            </div>
            `)
        }else if(modalDataConfig.graph_subtype === 'Scatter'){
        return $(`
        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">
        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>

        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br>
        <div class="custom-control custom-checkbox">
                      <input type="checkbox" checked="checked" name="defaultValueColorConfig" id="${modalDataConfig.id24}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id24}" class="custom-control-label">
                      Gradient Color
                      </label>
                  </div><br>
        <label style="font-size:1.1rem">Change the color or an element:</label>
        <input type="color" id="${modalDataConfig.id4}" name="favcolor1" value="${modalDataConfig.element_color}"><br>
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label></div><br>
        <label style="font-size:1.1rem">Change X and Y axis gridlines:</label>

        <button type="button" class="btn btn-primary" id="${modalDataConfig.id9}" data-toggle="button" role="tab"
                        aria-pressed="false" autocomplete="off" value="${modalDataConfig.grid_id}" style="line-height: 0.7;">${modalDataConfig.value}</button><br><br>
                        <label style="font-size:1.1rem">Change the range of the axis:</label>
        <input type="text" placeholder="Y Axis Start" id="${modalDataConfig.id2}" value="${modalDataConfig.y_axis_start}" size="7">
        <input type="text" placeholder="Y Axis End " id="${modalDataConfig.id3}" value="${modalDataConfig.y_axis_end}" size="7">
        <br><br>
        <label style="font-size:1.1rem">Change the title of the axes:</label>
        <input type="text" placeholder="X Axis Title" id="${modalDataConfig.id11}" value="${modalDataConfig.x_axis_title}" size="7">
        <input type="text" placeholder="Y Axis Title" id="${modalDataConfig.id12}" size="7" value="${modalDataConfig.y_axis_title}">
        <br><br>
        <label style="font-size:1.1rem">Change the label of an element:</label><br>
        <input type="text" placeholder="X Axis Label" id="${modalDataConfig.id13}" size="9" value="${modalDataConfig.element_label}"> &nbsp;&nbsp;
        <label style="font-size:1.1rem">Chart interaction:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" checked="checked" name="defaultValueConfig" id="${modalDataConfig.id21}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id21}" class="custom-control-label">
                      Cross-filter
                      </label>
                  </div>
        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id18}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" style="line-height: 1.1;">Reset Axis Labels</button><br><br>
                          <label style="font-size:1.1rem">Change Plot Labels:</label>
                          <button type="button" class="btn btn-primary" id="${modalDataConfig.id_labels}" data-toggle="button" role="tab"

                          aria-pressed="false" autocomplete="off" value="${modalDataConfig.label_value}" style="line-height: 1.1;">${modalDataConfig.label_text}</button>
                          <br><br>
                          <label style="font-size:1.1rem">Label Placement:</label>
        <select class="select2" name="position_legends" id="${modalDataConfig.id_label_placement}" style="font-size:1.1rem">
        <option value="">-----</option>
        <option value="top">Top</option>
        <option value="bottom">Bottom</option>
        <option value="center">Center</option>
        </select>
        <br><br>
        <label style="font-size:1.1rem">Box Shadow</label>
        <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the shadow color:</label>
        <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
        <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
        <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
        <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
        <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Thickness:</label>
        <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
        <label style="font-size:1.1rem">Box Border</label>
        <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the border color:</label>
        <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
        <label style="font-size:1.1rem">Set border thickness</label>
        <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
        <label style="font-size:1.1rem">Choose border style:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
        <option value="solid">Solid</option>
        <option value="dotted">Dotted</option>
        <option value="double">Double</option>
        <option value="dashed">Dashed</option>
        </select><br><br>
        <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}<br>
        ${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        <br>
        <label style="font-size:1.1rem">Set order for X Axis:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_axis_order}" style="font-size:1.1rem" onchange="changeOrder.call(this)" data-chart-id = "${modalDataConfig.id6}" datatype_dict = '${JSON.stringify(modalDataConfig.datatype_dict)}' mappingDict = '${JSON.stringify(modalDataConfig.mappingDict)}' order_type = 'Vertical' >
        <option value="" selected>----------</option>
        <option value="asc">Ascending</option>
        <option value="desc">Descending</option>
        <option value="cust">Custom</option>
        </select>
        <br>
        <button class="btn btn-primary btn-xs rounded px-2" id="${modalDataConfig.idOrderModal}Button" data-modal_id="${modalDataConfig.idOrderModal}" data-chart-id = "${modalDataConfig.id6}" data-sorted-values = "" onclick="orderModal.call(this)" datatype_dict = '${JSON.stringify(modalDataConfig.datatype_dict)}' order_type = 'Vertical' style="display:none; height : 30px;">Set preferred order
        </button>
        <br>
        <label style="font-size:1.1rem">Change labels color:</label>
        <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
        <br>
        <label style="font-size:1.1rem">Set labels font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>
        </div>
        </div>
        `)


    }else if(modalDataConfig.graph_subtype === 'Cumulative_Histogram'){
        return $(`
        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">
        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
          <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
          <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
            <span aria-hidden="true">&times;</span>
          </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
          <label style="font-size:1.1rem">Change the graph color:</label>

        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br>
        <div class="custom-control custom-checkbox">
                      <input type="checkbox" checked="checked" name="defaultValueColorConfig" id="${modalDataConfig.id24}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id24}" class="custom-control-label">
                      Gradient Color
                      </label>
                  </div><br>
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label></div><br><br>

        <label style="font-size:1.1rem">Change X and Y axis gridlines:</label>
          <button type="button" class="btn btn-primary" id="${modalDataConfig.id9}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" value="${modalDataConfig.grid_id}" style="line-height: 1.1;">${modalDataConfig.value}</button><br><br>
                          <label style="font-size:1.1rem">Change the range of the axis:</label>
        <input type="text" placeholder="Y Axis Start" id="${modalDataConfig.id2}" size="7" value="${modalDataConfig.y_axis_start}">
        <input type="text" placeholder="Y Axis End " id="${modalDataConfig.id3}" size="7" value="${modalDataConfig.y_axis_end}">
        <br><br>
        <label style="font-size:1.1rem">Change the title of the axes:</label>
        <input type="text" placeholder="X Axis Title" id="${modalDataConfig.id11}" value="${modalDataConfig.x_axis_title}" size="7">

        <br><br>
        <label style="font-size:1.1rem">Change the label of an element:</label><br>
        <input type="text" placeholder="X Axis Label" id="${modalDataConfig.id13}" size="9" value="${modalDataConfig.element_label}"> &nbsp;&nbsp;
        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id18}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" style="line-height: 1.1;">Reset Axis Labels</button>
                          <br><br>
        <label style="font-size:1.1rem">Box Shadow</label>
        <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the shadow color:</label>
        <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
        <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
        <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
        <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
        <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Thickness:</label>
        <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
        <label style="font-size:1.1rem">Box Border</label>
        <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the border color:</label>
        <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
        <label style="font-size:1.1rem">Set border thickness</label>
        <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
        <label style="font-size:1.1rem">Choose border style:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
        <option value="solid">Solid</option>
        <option value="dotted">Dotted</option>
        <option value="double">Double</option>
        <option value="dashed">Dashed</option>
        </select>
        <br><br>
        <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}<br>
        ${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        <br><br>
        <label style="font-size:1.1rem">Change labels color:</label>
        <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
        <br>
        <label style="font-size:1.1rem">Set labels font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>
        </div>
        </div>
        `)
    }
    else if(modalDataConfig.graph_subtype === 'Vertical_Waterfall'){
        return $(`
            <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
            right: 0 ;top : 10px;z-index: 1050">


            <div class="modal-content">
            <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
                <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
                <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
                <span aria-hidden="true">&times;</span>
                </button>
            </div>
            <div class="modal-body" style="max-height:26rem;overflow:auto">
            <label style="font-size:1.1rem">Change the graph color:</label>

                        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br>
                        <br>
            <label style="font-size:1.1rem">Change the graph background:</label>
                        <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                        <label style="font-size:1.1rem">Visualization Theme:</label>
                        <div class="custom-control custom-checkbox">
                            <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                            <label for="${modalDataConfig.id23}" class="custom-control-label">
                            Global Settings
                            </label></div>
            <label style="font-size:1.1rem">Change X and Y axis gridlines:</label>
                <button type="button" class="btn btn-primary" id="${modalDataConfig.id9}" data-toggle="button" role="tab"
                                aria-pressed="false" autocomplete="off" value="${modalDataConfig.grid_id}" style="line-height: 1.1;">${modalDataConfig.value}</button><br><br>
                                <label style="font-size:1.1rem">Change the range of the axis:</label>
            <input type="text" placeholder="Y Axis Start" id="${modalDataConfig.id2}" value="${modalDataConfig.y_axis_start}" size="7">
            <input type="text" placeholder="Y Axis End " id="${modalDataConfig.id3}" value="${modalDataConfig.y_axis_end}" size="7">
            <br><br>
            ${ChangeAxesTitle(modalDataConfig.id11,modalDataConfig.id12,modalDataConfig.x_axis_title,modalDataConfig.y_axis_title)}
            <br><br>
            <label style="font-size:1.1rem">Change the label of an element:</label><br>
            <input type="text" placeholder="X Axis Label" id="${modalDataConfig.id13}" size="9" value="${modalDataConfig.element_label}"> &nbsp;&nbsp;
            <label style="font-size:1.1rem">Chart interaction:</label>
            <div class="custom-control custom-checkbox">
                                <input type="checkbox" checked="checked" name="defaultValueConfig" id="${modalDataConfig.id21}" class="checkboxinput custom-control-input">
                                <label for="${modalDataConfig.id21}" class="custom-control-label">
                                    Cross-filter
                                </label>
                                </div>
            <label style="font-size:1.1rem">Connected slicers:</label>
            <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

            </div>
            <button type="button" class="btn btn-primary" id="${modalDataConfig.id18}" data-toggle="button" role="tab"
                                aria-pressed="false" autocomplete="off" style="line-height: 1.1;">Reset Axis Labels</button><br><br>
                                <label style="font-size:1.1rem">Change Plot Labels:</label>
                <button type="button" class="btn btn-primary" id="${modalDataConfig.id_labels}"  data-toggle="button" role="tab"
                                aria-pressed="false" autocomplete="off" value="${modalDataConfig.label_value}" style="line-height: 1.1;">${modalDataConfig.label_text}</button>
                                <br><br>
                                <label style="font-size:1.1rem">Box Shadow</label>
                                <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                                <label style="font-size:1.1rem">Choose the shadow color:</label>
                                <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
                                <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
                                <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
                                <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
                                <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
                                <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
                                <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
                                <label style="font-size:1.1rem">Set Shadow Thickness:</label>
                                <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
                                <label style="font-size:1.1rem">Box Border</label>
                                <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                                <label style="font-size:1.1rem">Choose the border color:</label>
                                <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
                                <label style="font-size:1.1rem">Set border thickness</label>
                                <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
                                <label style="font-size:1.1rem">Choose border style:</label>
                                <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
                                <option value="solid">Solid</option>
                                <option value="dotted">Dotted</option>
                                <option value="double">Double</option>
                                <option value="dashed">Dashed</option>
                                </select><br><br>
                                <label style="font-size:1.1rem">Change the header color:</label>
            <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
            <br>
            <label style="font-size:1.1rem">Change the background color of header:</label>
            <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
            <label style="font-size:1.1rem">Set header font size:</label>
            <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
            <label style="font-size:1.1rem">Set header font weight:</label>

            ${modalDataConfig.borderStylehtml}<br>
            ${modalDataConfig.setheaderFontHTML}
            <br>
            <label style="font-size:1.1rem">Set header alignment:</label>
            <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
            <option value="">----------</option>
            <option value="left">Left</option>
            <option value="center">Center</option>
            <option value="right">Right</option>
            </select>
            <br>
            <label style="font-size:1.1rem">Set order for X Axis:</label>
            <select class="select2" name="border_style" id="${modalDataConfig.id_axis_order}" style="font-size:1.1rem" onchange="changeOrder.call(this)" data-chart-id = "${modalDataConfig.id6}" datatype_dict = '${JSON.stringify(modalDataConfig.datatype_dict)}' mappingDict = '${JSON.stringify(modalDataConfig.mappingDict)}' order_type = 'Vertical' >
            <option value="" selected>----------</option>
            <option value="asc">Ascending</option>
            <option value="desc">Descending</option>
            <option value="cust">Custom</option>
            </select>
            <br>
            <button class="btn btn-primary btn-xs rounded px-2" id="${modalDataConfig.idOrderModal}Button" data-modal_id="${modalDataConfig.idOrderModal}" data-chart-id = "${modalDataConfig.id6}" data-sorted-values = "" onclick="orderModal.call(this)" datatype_dict = '${JSON.stringify(modalDataConfig.datatype_dict)}' order_type = 'Vertical' style="display:none; height : 30px;">Set preferred order
            </button>
            ${modalDataConfig.optionvaluesHTML}
            <br><br>
        <label style="font-size:1.1rem">Change labels color:</label>
        <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
        <br>
        <label style="font-size:1.1rem">Set labels font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>
            </div>
            </div>
            `)
    }else if(modalDataConfig.graph_subtype === 'Horizontal_Waterfall'){
        return $(`
                <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
                right: 0 ;top : 10px;z-index: 1050">


                <div class="modal-content">
                <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
                    <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
                    <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                    </button>
                </div>
                <div class="modal-body" style="max-height:26rem;overflow:auto">
                <label style="font-size:1.1rem">Change the graph color:</label>

                            <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br>
                            <br>
                <label style="font-size:1.1rem">Change the graph background:</label>
                            <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                            <label style="font-size:1.1rem">Visualization Theme:</label>
                            <div class="custom-control custom-checkbox">
                                <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                                <label for="${modalDataConfig.id23}" class="custom-control-label">
                                Global Settings
                                </label></div><br><br>
                <label style="font-size:1.1rem">Change X and Y axis gridlines:</label>
                    <button type="button" class="btn btn-primary" id="${modalDataConfig.id9}" data-toggle="button" role="tab"
                                    aria-pressed="false" autocomplete="off" value="${modalDataConfig.grid_id}" style="line-height: 1.1;">${modalDataConfig.value}</button><br><br>
                                    <label style="font-size:1.1rem">Change the range of the axis:</label>
                <input type="text" placeholder="Y Axis Start" id="${modalDataConfig.id2}" value="${modalDataConfig.y_axis_start}" size="7">
                <input type="text" placeholder="Y Axis End " id="${modalDataConfig.id3}" value="${modalDataConfig.y_axis_end}" size="7">
                <br><br>
                ${ChangeAxesTitle(modalDataConfig.id11,modalDataConfig.id12,modalDataConfig.x_axis_title,modalDataConfig.y_axis_title)}
                <br><br>
                <label style="font-size:1.1rem">Change the label of an element:</label><br>
                <input type="text" placeholder="X Axis Label" id="${modalDataConfig.id13}" size="9" value="${modalDataConfig.element_label}"> &nbsp;&nbsp;
                <label style="font-size:1.1rem">Chart interaction:</label>
                            <div class="custom-control custom-checkbox">
                                <input type="checkbox" checked="checked" name="defaultValueConfig" id="${modalDataConfig.id21}" class="checkboxinput custom-control-input">
                                <label for="${modalDataConfig.id21}" class="custom-control-label">
                                Cross-filter
                                </label>
                            </div>
                <label style="font-size:1.1rem">Connected slicers:</label>
                <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

                </div>
                <button type="button" class="btn btn-primary" id="${modalDataConfig.id18}" data-toggle="button" role="tab"
                                    aria-pressed="false" autocomplete="off" style="line-height: 1.1;">Reset Axis Labels</button><br><br>
                                    <label style="font-size:1.1rem">Change Plot Labels:</label>
                    <button type="button" class="btn btn-primary" id="${modalDataConfig.id_labels}" data-toggle="button" role="tab"
                                    aria-pressed="false" autocomplete="off" value="${modalDataConfig.label_value}" style="line-height: 1.1;">${modalDataConfig.label_text}</button>
                                    <br><br>
                                    <label style="font-size:1.1rem">Box Shadow</label>
                                    <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                                    <label style="font-size:1.1rem">Choose the shadow color:</label>
                                    <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
                                    <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
                                    <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
                                    <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
                                    <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
                                    <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
                                    <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
                                    <label style="font-size:1.1rem">Set Shadow Thickness:</label>
                                    <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
                                    <label style="font-size:1.1rem">Box Border</label>
                                    <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                                    <label style="font-size:1.1rem">Choose the border color:</label>
                                    <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
                                    <label style="font-size:1.1rem">Set border thickness</label>
                                    <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
                                    <label style="font-size:1.1rem">Choose border style:</label>
                                    <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
                                    <option value="solid">Solid</option>
                                    <option value="dotted">Dotted</option>
                                    <option value="double">Double</option>
                                    <option value="dashed">Dashed</option>
                                    </select><br><br>
                                    <label style="font-size:1.1rem">Change the header color:</label>
                <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
                <br>
                <label style="font-size:1.1rem">Change the background color of header:</label>
                <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
                <label style="font-size:1.1rem">Set header font size:</label>
                <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
                <label style="font-size:1.1rem">Set header font weight:</label>

                ${modalDataConfig.borderStylehtml}<br>
                ${modalDataConfig.setheaderFontHTML}
                <br>
                <label style="font-size:1.1rem">Set header alignment:</label>
                <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
                <option value="">----------</option>
                <option value="left">Left</option>
                <option value="center">Center</option>
                <option value="right">Right</option>
                </select>
                ${modalDataConfig.optionvaluesHTML}
                <br><br>
                <label style="font-size:1.1rem">Change labels color:</label>
                <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
                <br>
                <label style="font-size:1.1rem">Set labels font size:</label>
                <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>
                </div>
                </div>
                `)
    }else if(modalDataConfig.graph_subtype === '3D_Scatter'){
        return $(`
            <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
            right: 0 ;top : 10px;z-index: 1050">
            <div class="modal-content">
            <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
            <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
            <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
                <span aria-hidden="true">&times;</span>
            </button>
            </div>
            <div class="modal-body" style="max-height:26rem;overflow:auto">
            <label style="font-size:1.1rem">Change the graph color:</label>

            <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br>
            <label style="font-size:1.1rem">Change the graph background:</label>
                        <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                        <label style="font-size:1.1rem">Visualization Theme:</label>
                        <div class="custom-control custom-checkbox">
                            <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                            <label for="${modalDataConfig.id23}" class="custom-control-label">
                            Global Settings
                            </label></div><br><br>

            <br><br><label style="font-size:1.1rem">Change X and Y axis gridlines:</label>
            <button type="button" class="btn btn-primary" id="${modalDataConfig.id9}" data-toggle="button" role="tab"
                            aria-pressed="false" autocomplete="off" value="${modalDataConfig.grid_id}" style="line-height: 0.7;">${modalDataConfig.value}</button><br><br>
                            <label style="font-size:1.1rem">Change the range of the axis:</label>
            <input type="text" placeholder="Y Axis Start" id="${modalDataConfig.id2}" size="7">
            <input type="text" placeholder="Y Axis End " id="${modalDataConfig.id3}" size="7">
            <br><br>
            ${ChangeAxesTitle(modalDataConfig.id11,modalDataConfig.id12,modalDataConfig.x_axis_title,modalDataConfig.y_axis_title)}
            <br><br>
            <label style="font-size:1.1rem">Change the label of an element:</label><br>
            <input type="text" placeholder="X Axis Label" id="${modalDataConfig.id13}" size="9" value="${modalDataConfig.element_label}"> &nbsp;&nbsp;
            <label style="font-size:1.1rem">Connected slicers:</label>
            <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

            </div>
            <button type="button" class="btn btn-primary" id="${modalDataConfig.id18}" data-toggle="button" role="tab"
                                aria-pressed="false" autocomplete="off" style="line-height: 1.1;">Reset Axis Labels</button><br><br>
                                <label style="font-size:1.1rem">Change Plot Labels:</label>
                                <button type="button" class="btn btn-primary" id="${modalDataConfig.id_labels}" data-toggle="button" role="tab"
                                aria-pressed="false" autocomplete="off" value="${modalDataConfig.label_value}" style="line-height: 1.1;">${modalDataConfig.label_text}</button>
                                <br><br>
                                <label style="font-size:1.1rem">Box Shadow</label>
                                <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                                <label style="font-size:1.1rem">Choose the shadow color:</label>
                                <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
                                <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
                                <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
                                <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
                                <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
                                <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
                                <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
                                <label style="font-size:1.1rem">Set Shadow Thickness:</label>
                                <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
                                <label style="font-size:1.1rem">Box Border</label>
                                <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                                <label style="font-size:1.1rem">Choose the border color:</label>
                                <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
                                <label style="font-size:1.1rem">Set border thickness</label>
                                <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
                                <label style="font-size:1.1rem">Choose border style:</label>
                                <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
                                <option value="solid">Solid</option>
                                <option value="dotted">Dotted</option>
                                <option value="double">Double</option>
                                <option value="dashed">Dashed</option>
                                </select><br><br>
                                <label style="font-size:1.1rem">Change the header color:</label>
            <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
            <br>
            <label style="font-size:1.1rem">Change the background color of header:</label>
            <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
            <label style="font-size:1.1rem">Set header font size:</label>
            <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
            <label style="font-size:1.1rem">Set header font weight:</label>

            ${modalDataConfig.borderStylehtml}<br>
            ${modalDataConfig.setheaderFontHTML}
            <br>
            <label style="font-size:1.1rem">Set header alignment:</label>
            <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
            <option value="">----------</option>
            <option value="left">Left</option>
            <option value="center">Center</option>
            <option value="right">Right</option>
            </select>

            </div>
            </div>
            `)
    }else if(modalDataConfig.graph_subtype === '3D_Mesh'){
        return $(`
            <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
            right: 0 ;top : 10px;z-index: 1050">
            <div class="modal-content">
            <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
            <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
            <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
            <span aria-hidden="true">&times;</span>
            </button>
            </div>
            <div class="modal-body" style="max-height:26rem;overflow:auto">
            <label style="font-size:1.1rem">Change the graph color:</label>
            <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}">
            <label style="font-size:1.1rem">Change the graph background:</label>
                        <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                        <label style="font-size:1.1rem">Visualization Theme:</label>
                        <div class="custom-control custom-checkbox">
                            <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                            <label for="${modalDataConfig.id23}" class="custom-control-label">
                            Global Settings
                            </label></div>
            <br><br><label style="font-size:1.1rem">Change X and Y axis gridlines:</label>
            <button type="button" class="btn btn-primary" id="${modalDataConfig.id9}" data-toggle="button" role="tab"
            aria-pressed="false" autocomplete="off" value="${modalDataConfig.grid_id}" style="line-height: 0.7;">${modalDataConfig.value}</button><br><br>
            <label style="font-size:1.1rem">Change the range of the axis:</label>
            <input type="text" placeholder="Y Axis Start" id="${modalDataConfig.id2}" size="7">
            <input type="text" placeholder="Y Axis End " id="${modalDataConfig.id3}" size="7">
            <br><br>
            ${ChangeAxesTitle(modalDataConfig.id11,modalDataConfig.id12,modalDataConfig.x_axis_title,modalDataConfig.y_axis_title)}
            <br><br>
            <label style="font-size:1.1rem">Change the label of an element:</label><br>
            <input type="text" placeholder="X Axis Label" id="${modalDataConfig.id13}" size="9" value="${modalDataConfig.element_label}"> &nbsp;&nbsp;
            <label style="font-size:1.1rem">Connected slicers:</label>
            <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">
            </div>
            <button type="button" class="btn btn-primary" id="${modalDataConfig.id18}" data-toggle="button" role="tab"
            aria-pressed="false" autocomplete="off" style="line-height: 1.1;">Reset Axis Labels</button><br><br>
            <label style="font-size:1.1rem">Change Plot Labels:</label>
            <button type="button" class="btn btn-primary" id="${modalDataConfig.id_labels}" data-toggle="button" role="tab"
                                aria-pressed="false" autocomplete="off" value="${modalDataConfig.label_value}" style="line-height: 1.1;">${modalDataConfig.label_text}</button>
                                <br><br>
                                <label style="font-size:1.1rem">Box Shadow</label>
                                <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                                <label style="font-size:1.1rem">Choose the shadow color:</label>
                                <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
                                <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
                                <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
                                <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
                                <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
                                <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
                                <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
                                <label style="font-size:1.1rem">Set Shadow Thickness:</label>
                                <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
                                <label style="font-size:1.1rem">Box Border</label>
                                <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                                <label style="font-size:1.1rem">Choose the border color:</label>
                                <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
                                <label style="font-size:1.1rem">Set border thickness</label>
                                <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
                                <label style="font-size:1.1rem">Choose border style:</label>
                                <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
                                <option value="solid">Solid</option>
                                <option value="dotted">Dotted</option>
                                <option value="double">Double</option>
                                <option value="dashed">Dashed</option>
                                </select><br><br>
                                <label style="font-size:1.1rem">Change the header color:</label>
            <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
            <br>
            <label style="font-size:1.1rem">Change the background color of header:</label>
            <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
            <label style="font-size:1.1rem">Set header font size:</label>
            <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
            <label style="font-size:1.1rem">Set header font weight:</label>
            ${modalDataConfig.borderStylehtml}<br>
            ${modalDataConfig.setheaderFontHTML}
            <br>
            <label style="font-size:1.1rem">Set header alignment:</label>
            <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
            <option value="">----------</option>
            <option value="left">Left</option>
            <option value="center">Center</option>
            <option value="right">Right</option>
            </select>
            </div>
            </div>
            `)
    }else if(modalDataConfig.graph_subtype === '2D_Histogram_Contour'){
        return $(`

        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">


        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>

        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br>
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label></div>

                        <label style="font-size:1.1rem">Change the range of the axis:</label>
        <input type="text" placeholder="Y Axis Start" id="${modalDataConfig.id2}" value="${modalDataConfig.y_axis_start}" size="7">
        <input type="text" placeholder="Y Axis End " id="${modalDataConfig.id3}" value="${modalDataConfig.y_axis_end}"  size="7">
        <br><br>
        <label style="font-size:1.1rem">Change the title of the axes:</label>
        <input type="text" placeholder="X Axis Title" id="${modalDataConfig.id11}" value="${modalDataConfig.x_axis_title}"  size="7">
        <input type="text" placeholder="Y Axis Title" id="${modalDataConfig.id12}" value="${modalDataConfig.x_axis_title}"  size="7">
        <br><br>
        <label style="font-size:1.1rem">Change the label of an element:</label><br>
        <input type="text" placeholder="X Axis Label" id="${modalDataConfig.id13}" size="9" value="${modalDataConfig.element_label}"> &nbsp;&nbsp;
        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id18}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" style="line-height: 1.1;">Reset Axis Labels</button>
                          <br><br>
        <label style="font-size:1.1rem">Box Shadow</label>
        <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the shadow color:</label>
        <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
        <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
        <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
        <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
        <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Thickness:</label>
        <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
        <label style="font-size:1.1rem">Box Border</label>
        <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the border color:</label>
        <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
        <label style="font-size:1.1rem">Set border thickness</label>
        <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
        <label style="font-size:1.1rem">Choose border style:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
        <option value="solid">Solid</option>
        <option value="dotted">Dotted</option>
        <option value="double">Double</option>
        <option value="dashed">Dashed</option>
        </select><br><br>
        <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}<br>
        ${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        <br><br>
        <label style="font-size:1.1rem">Change labels color:</label>
        <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
        <br>
        <label style="font-size:1.1rem">Set labels font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>
                          </div>
        </div>
        `)
    }else if(modalDataConfig.graph_subtype === 'Vertical_Box'){
        return $(`

        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">


        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>

        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br>
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label></div>

        <label style="font-size:1.1rem">Change X and Y axis gridlines:</label>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id9}" data-toggle="button" role="tab"
                        aria-pressed="false" autocomplete="off" value="${modalDataConfig.grid_id}" style="line-height: 0.7;">${modalDataConfig.value}</button><br><br>
                        <label style="font-size:1.1rem">Change the range of the axis:</label>
        <input type="text" placeholder="Y Axis Start" id="${modalDataConfig.id2}" value="${modalDataConfig.y_axis_start}" size="7">
        <input type="text" placeholder="Y Axis End " id="${modalDataConfig.id3}" value="${modalDataConfig.y_axis_end}" size="7">
        <br><br>
        <label style="font-size:1.1rem">Change the title of the axes:</label>
        <input type="text" placeholder="X Axis Title" id=${modalDataConfig.id11} value="${modalDataConfig.x_axis_title}" size="7">
        <input type="text" placeholder="Y Axis Title" id=${modalDataConfig.id12} value="${modalDataConfig.y_axis_title}" size="7">
        <br><br>
        <label style="font-size:1.1rem">Change the label of an element:</label><br>
        <input type="text" placeholder="X Axis Label" id="${modalDataConfig.id13}" size="9" value="${modalDataConfig.element_label}"> &nbsp;&nbsp;
        <label style="font-size:1.1rem">Chart interaction:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" checked="checked" name="defaultValueConfig" id="${modalDataConfig.id21}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id21}" class="custom-control-label">
                      Cross-filter
                      </label>
                  </div>
        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id18}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" style="line-height: 1.1;">Reset Axis Labels</button>
                          <br><br>
                          <label style="font-size:1.1rem">Box Shadow</label>
                          <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the shadow color:</label>
                          <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
                          <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
                          <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
                          <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Thickness:</label>
                          <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Box Border</label>
                          <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the border color:</label>
                          <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
                          <label style="font-size:1.1rem">Set border thickness</label>
                          <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
                          <label style="font-size:1.1rem">Choose border style:</label>
                          <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
                          <option value="solid">Solid</option>
                          <option value="dotted">Dotted</option>
                          <option value="double">Double</option>
                          <option value="dashed">Dashed</option>
                          </select><br><br>
                          <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}<br>
        ${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        <br><br>
        <label style="font-size:1.1rem">Change labels color:</label>
        <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
        <br>
        <label style="font-size:1.1rem">Set labels font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>
        </div>
        </div>
        `)
    }else if(modalDataConfig.graph_subtype === 'Vertical_Violin'){
        return $(`

        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">


        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>

        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br>
        <label style="font-size:1.1rem">Change the color or an element:</label>
        <input type="color" id="${modalDataConfig.id4}" name="favcolor1" value="${modalDataConfig.element_color}">
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label></div><br><label style="font-size:1.1rem">Change X and Y axis gridlines:</label>

        <button type="button" class="btn btn-primary" id="${modalDataConfig.id9}" data-toggle="button" role="tab"
                        aria-pressed="false" autocomplete="off" value="${modalDataConfig.grid_id}" style="line-height: 0.7;">${modalDataConfig.value}</button><br><br>
                        <label style="font-size:1.1rem">Change the range of the axis:</label>
        <input type="text" placeholder="Y Axis Start" id="${modalDataConfig.id2}" value="${modalDataConfig.y_axis_start}" size="7">
        <input type="text" placeholder="Y Axis End " id="${modalDataConfig.id3}" value="${modalDataConfig.y_axis_end}" size="7">
        <br><br>
        ${ChangeAxesTitle(modalDataConfig.id11,modalDataConfig.id12,modalDataConfig.x_axis_title,modalDataConfig.y_axis_title)}
        <br><br>
        <label style="font-size:1.1rem">Change the label of an element:</label><br>
        <input type="text" placeholder="X Axis Label" id="${modalDataConfig.id13}" value="${modalDataConfig.element_label}" size="9"> &nbsp;&nbsp;
        <label style="font-size:1.1rem">Chart interaction:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" checked="checked" name="defaultValueConfig" id="${modalDataConfig.id21}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id21}" class="custom-control-label">
                      Cross-filter
                      </label>
                  </div>
        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id18}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" style="line-height: 1.1;">Reset Axis Labels</button>
                          <br><br>
        <label style="font-size:1.1rem">Box Shadow</label>
        <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the shadow color:</label>
        <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
        <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
        <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
        <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
        <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Thickness:</label>
        <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
        <label style="font-size:1.1rem">Box Border</label>
        <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the border color:</label>
        <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
        <label style="font-size:1.1rem">Set border thickness</label>
        <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
        <label style="font-size:1.1rem">Choose border style:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
        <option value="solid">Solid</option>
        <option value="dotted">Dotted</option>
        <option value="double">Double</option>
        <option value="dashed">Dashed</option>
        </select><br><br>
        <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}
        <br>${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        <br><br>
        <label style="font-size:1.1rem">Change labels color:</label>
        <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
        <br>
        <label style="font-size:1.1rem">Set labels font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>
        </div>
        </div>
        `)
    }else if(modalDataConfig.graph_subtype === 'Horizontal_Dot_Plot'){
        return $(`
        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">


        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>

        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br>
        <div class="custom-control custom-checkbox">
                      <input type="checkbox" checked="checked" name="defaultValueColorConfig" id="${modalDataConfig.id24}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id24}" class="custom-control-label">
                      Gradient Color
                      </label>
                  </div><br>
        <label style="font-size:1.1rem">Change the color or an element:</label>
        <input type="color" id="${modalDataConfig.id4}" name="favcolor1" value="${modalDataConfig.element_color}">
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label></div>
                  <br><br>
                  <label style="font-size:1.1rem">Change X and Y axis gridlines:</label><br><br>

        <button type="button" class="btn btn-primary" id="${modalDataConfig.id9}" data-toggle="button" role="tab"
                        aria-pressed="false" autocomplete="off" value="${modalDataConfig.grid_id}" style="line-height: 0.7;">${modalDataConfig.value}</button><br><br>
                        <label style="font-size:1.1rem">Change the range of the axis:</label>
        <input type="text" placeholder="Y Axis Start" id="${modalDataConfig.id2}" value="${modalDataConfig.y_axis_start}" size="7">
        <input type="text" placeholder="Y Axis End " id="${modalDataConfig.id3}" value="${modalDataConfig.y_axis_end}" size="7">
        <br><br>
        ${ChangeAxesTitle(modalDataConfig.id11,modalDataConfig.id12,modalDataConfig.x_axis_title,modalDataConfig.y_axis_title)}
        <br><br>
        <label style="font-size:1.1rem">Change the label of an element:</label><br>
        <input type="text" placeholder="Y Axis Label" id="${modalDataConfig.id13}" value="${modalDataConfig.element_label}" size="9"> &nbsp;&nbsp;<br><br>
        <label style="font-size:1.1rem">Chart interaction:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" checked="checked" name="defaultValueConfig" id="${modalDataConfig.id21}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id21}" class="custom-control-label">
                      Cross-filter
                      </label>
                  </div>
        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id18}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" style="line-height: 1.1;">Reset Axis Labels</button><br><br>
                          <label style="font-size:1.1rem">Change Plot Labels:</label>
                          <button type="button" class="btn btn-primary" id="${modalDataConfig.id_labels}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" value="${modalDataConfig.label_value}" style="line-height: 1.1;">${modalDataConfig.label_text}</button>
                          <br><br>
                          <label style="font-size:1.1rem">Label Placement:</label>
        <select class="select2" name="position_legends" id="${modalDataConfig.id_label_placement}" style="font-size:1.1rem">
        <option value="">-----</option>
        <option value="top">Top</option>
        <option value="bottom">Bottom</option>
        <option value="center">Center</option>
        </select>
        <br><br>
        <label style="font-size:1.1rem">Box Shadow</label>
        <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the shadow color:</label>
        <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
        <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
        <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
        <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
        <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Thickness:</label>
        <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
        <label style="font-size:1.1rem">Box Border</label>
        <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the border color:</label>
        <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
        <label style="font-size:1.1rem">Set border thickness</label>
        <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
        <label style="font-size:1.1rem">Choose border style:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
        <option value="solid">Solid</option>
        <option value="dotted">Dotted</option>
        <option value="double">Double</option>
        <option value="dashed">Dashed</option>
        </select><br><br>
        <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}
        <br>${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        <br><br>
        <label style="font-size:1.1rem">Change labels color:</label>
        <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
        <br>
        <label style="font-size:1.1rem">Set labels font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>
        </div>
        </div>
        `)
    }else if(modalDataConfig.graph_subtype === 'Horizontal_Box'){
        return $(`

        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">


        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>

        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br>
        <label style="font-size:1.1rem">Change the color or an element:</label>
        <input type="color" id="${modalDataConfig.id4}" name="favcolor1" value="${modalDataConfig.element_color}"><br>
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label>
                  </div>
                  <br><br>
        <label style="font-size:1.1rem">Change X and Y axis gridlines:</label>

        <button type="button" class="btn btn-primary" id="${modalDataConfig.id9}" data-toggle="button" role="tab"
                        aria-pressed="false" autocomplete="off" value="${modalDataConfig.grid_id}" style="line-height: 0.7;">${modalDataConfig.value}</button><br><br>
                        <label style="font-size:1.1rem">Change the range of the axis:</label>
        <input type="text" placeholder="Y Axis Start" id="${modalDataConfig.id2}" value="${modalDataConfig.y_axis_start}" size="7">
        <input type="text" placeholder="Y Axis End " id="${modalDataConfig.id3}" value="${modalDataConfig.y_axis_end}" size="7">
        <br><br>
        ${ChangeAxesTitle(modalDataConfig.id11,modalDataConfig.id12,modalDataConfig.x_axis_title,modalDataConfig.y_axis_title)}
        <br><br>
        <label style="font-size:1.1rem">Change the label of an element:</label><br>
        <input type="text" placeholder="Y Axis Label" id="${modalDataConfig.id13}" value="${modalDataConfig.element_label}" size="9"> &nbsp;&nbsp;<br><br>
        <label style="font-size:1.1rem">Chart interaction:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" checked="checked" name="defaultValueConfig" id="${modalDataConfig.id21}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id21}" class="custom-control-label">
                      Cross-filter
                      </label>
                  </div>
        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id18}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" style="line-height: 1.1;">Reset Axis Labels</button>
                          <br><br>
                          <label style="font-size:1.1rem">Box Shadow</label>
                          <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the shadow color:</label>
                          <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
                          <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
                          <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
                          <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Thickness:</label>
                          <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Box Border</label>
                          <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the border color:</label>
                          <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
                          <label style="font-size:1.1rem">Set border thickness</label>
                          <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
                          <label style="font-size:1.1rem">Choose border style:</label>
                          <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
                          <option value="solid">Solid</option>
                          <option value="dotted">Dotted</option>
                          <option value="double">Double</option>
                          <option value="dashed">Dashed</option>
                          </select><br><br>
                          <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}
        <br>${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        <br><br>
        <label style="font-size:1.1rem">Change labels color:</label>
        <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
        <br>
        <label style="font-size:1.1rem">Set labels font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>
        </div>
        </div>
        `)
    }else if(modalDataConfig.graph_subtype === 'Horizontal_Violin'){
        return $(`

        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">


        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>

        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br>
        <label style="font-size:1.1rem">Change the color or an element:</label>
        <input type="color" id="${modalDataConfig.id4}" name="favcolor1" value="${modalDataConfig.element_color}"><br>
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label></div>
                  <br><br><label style="font-size:1.1rem">Change X and Y axis gridlines:</label>

        <button type="button" class="btn btn-primary" id="${modalDataConfig.id9}" data-toggle="button" role="tab"
                        aria-pressed="false" autocomplete="off" value="${modalDataConfig.grid_id}" style="line-height: 0.7;">${modalDataConfig.value}</button><br><br>
                        <label style="font-size:1.1rem">Change the range of the axis:</label>
        <input type="text" placeholder="Y Axis Start" value="${modalDataConfig.y_axis_start}" id="${modalDataConfig.id2}" size="7">
        <input type="text" placeholder="Y Axis End " value="${modalDataConfig.y_axis_end}" id="${modalDataConfig.id3}" size="7">
        <br><br>
        <label style="font-size:1.1rem">Change the title of the axes:</label>
        <input type="text" placeholder="X Axis Title" value="${modalDataConfig.x_axis_title}" id="${modalDataConfig.id11}" size="7">
        <input type="text" placeholder="Y Axis Title" value="${modalDataConfig.y_axis_title}" id="${modalDataConfig.id12}" size="7">
        <br><br>
        <label style="font-size:1.1rem">Change the label of an element:</label><br>
        <input type="text" placeholder="Y Axis Label" id="${modalDataConfig.id13}" size="9" value="${modalDataConfig.element_label}"> &nbsp;&nbsp;<br><br>
        <label style="font-size:1.1rem">Chart interaction:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" checked="checked" name="defaultValueConfig" id="${modalDataConfig.id21}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id21}" class="custom-control-label">
                      Cross-filter
                      </label>
                  </div>
        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id18}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" style="line-height: 1.1;">Reset Axis Labels</button>
                          <br><br>
                          <label style="font-size:1.1rem">Box Shadow</label>
                          <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the shadow color:</label>
                          <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
                          <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
                          <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
                          <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Thickness:</label>
                          <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Box Border</label>
                          <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the border color:</label>
                          <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
                          <label style="font-size:1.1rem">Set border thickness</label>
                          <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
                          <label style="font-size:1.1rem">Choose border style:</label>
                          <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
                          <option value="solid">Solid</option>
                          <option value="dotted">Dotted</option>
                          <option value="double">Double</option>
                          <option value="dashed">Dashed</option>
                          </select><br><br>
                          <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}
        <br>${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        <br><br>
        <label style="font-size:1.1rem">Change labels color:</label>
        <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
        <br>
        <label style="font-size:1.1rem">Set labels font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>
        </div>
        </div>
        `)
    }else if(modalDataConfig.graph_subtype === 'Scatter_with_Straight_Lines_and_Markers'){
        return  $(`

        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">


        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>

        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br>
        <label style="font-size:1.1rem">Change the color or an element:</label>
        <input type="color" id="${modalDataConfig.id4}" name="favcolor1" value="${modalDataConfig.element_color}"><br>
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label></div>
                  <br><br><label style="font-size:1.1rem">Change X and Y axis gridlines:</label>

        <button type="button" class="btn btn-primary" id="${modalDataConfig.id9}" data-toggle="button" role="tab"
                        aria-pressed="false" autocomplete="off" value="${modalDataConfig.grid_id}" style="line-height: 0.7;">${modalDataConfig.value}</button><br><br>
                        <label style="font-size:1.1rem">Change the range of the axis:</label>
        <input type="text" placeholder="Y Axis Start" value="${modalDataConfig.y_axis_start}" id="${modalDataConfig.id2}" size="7">
        <input type="text" placeholder="Y Axis End " value="${modalDataConfig.y_axis_end}" id="${modalDataConfig.id3}" size="7">

        <br><br>
        ${ChangeAxesTitle(modalDataConfig.id11,modalDataConfig.id12,modalDataConfig.x_axis_title,modalDataConfig.y_axis_title)}
        <br><br>
        <label style="font-size:1.1rem">Change the label of an element:</label><br>
        <input type="text" placeholder="X Axis Label" id="${modalDataConfig.id13}" size="9" value="${modalDataConfig.element_label}"> &nbsp;&nbsp;
        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id18}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" style="line-height: 1.1;">Reset Axis Labels</button><br><br>
                          <label style="font-size:1.1rem">Change Plot Labels:</label>
                          <button type="button" class="btn btn-primary" id="${modalDataConfig.id_labels}" data-toggle="button" role="tab"

                          aria-pressed="false" autocomplete="off" value="${modalDataConfig.label_value}" style="line-height: 1.1;">${modalDataConfig.label_text}</button>
                          <br><br>
                          <label style="font-size:1.1rem">Label Placement:</label>
        <select class="select2" name="position_legends" id="${modalDataConfig.id_label_placement}" style="font-size:1.1rem">
        <option value="">-----</option>
        <option value="top">Top</option>
        <option value="bottom">Bottom</option>
        <option value="center">Center</option>
        </select>
        <br><br>
        <label style="font-size:1.1rem">Box Shadow</label>
        <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the shadow color:</label>
        <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
        <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
        <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
        <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
        <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Thickness:</label>
        <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
        <label style="font-size:1.1rem">Box Border</label>
        <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the border color:</label>
        <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
        <label style="font-size:1.1rem">Set border thickness</label>
        <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
        <label style="font-size:1.1rem">Choose border style:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
        <option value="solid">Solid</option>
        <option value="dotted">Dotted</option>
        <option value="double">Double</option>
        <option value="dashed">Dashed</option>
        </select><br><br>
        <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}
        <br>${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        <br>
        <label style="font-size:1.1rem">Set order for X Axis:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_axis_order}" style="font-size:1.1rem" onchange="changeOrder.call(this)" data-chart-id = "${modalDataConfig.id6}" datatype_dict = '${JSON.stringify(modalDataConfig.datatype_dict)}' mappingDict = '${JSON.stringify(modalDataConfig.mappingDict)}' order_type = 'Vertical' >
        <option value="" selected>----------</option>
        <option value="asc">Ascending</option>
        <option value="desc">Descending</option>
        <option value="cust">Custom</option>
        </select>
        <br>
        <button class="btn btn-primary btn-xs rounded px-2" id="${modalDataConfig.idOrderModal}Button" data-modal_id="${modalDataConfig.idOrderModal}" data-chart-id = "${modalDataConfig.id6}" data-sorted-values = "" onclick="orderModal.call(this)" datatype_dict = '${JSON.stringify(modalDataConfig.datatype_dict)}' order_type = 'Vertical' style="display:none; height : 30px;">Set preferred order
        </button>
        <br><br>
        <label style="font-size:1.1rem">Change labels color:</label>
        <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
        <br>
        <label style="font-size:1.1rem">Set labels font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>
        </div>
        </div>
        `)
    }else if(modalDataConfig.graph_subtype === 'Pie_Chart'){
        return $(`

        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">


        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>

        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br>
        <label style="font-size:1.1rem">Change the color or an element:</label>
        <input type="color" id="${modalDataConfig.id4}" name="favcolor1" value="${modalDataConfig.element_color}">
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label></div>
        <br><br>
        <label style="font-size:1.1rem">Chart interaction:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" checked="checked" name="defaultValueConfig" id="${modalDataConfig.id21}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id21}" class="custom-control-label">
                      Cross-filter
                      </label>
                  </div>
          <label style="font-size:1.1rem">Connected slicers:</label>
          <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

          </div>
          <label style="font-size:1.1rem">Show/Hide Labels:</label>
          <button id="${modalDataConfig.id_showlabel}" type="button" class="btn btn-primary" data-toggle="button" role="tab"
          aria-pressed="false" autocomplete="off" value="${modalDataConfig.label_value}" style="line-height: 0.7;">${modalDataConfig.label_text}</button><br><br>
          <label style="font-size:1.1rem">Position Legends:</label>
        <select class="select2" name="position_legends" id="${modalDataConfig.id_position_legends}" style="font-size:1.1rem">
        <option value="">-----</option>
        <option value="top_centre">Top Centre</option>
        <option value="top_left">Top Left</option>
        <option value="top_right">Top Right</option>
        <option value="bottom_centre">Bottom Centre</option>
        <option value="bottom_left">Bottom Left</option>
        <option value="bottom_right">Bottom Right</option>
        </select><br><br>
        <label style="font-size:1.1rem">Label Placement:</label>
        <select class="select2" name="position_legends" id="${modalDataConfig.id_label_placement}" style="font-size:1.1rem">
        <option value="">-----</option>
        <option value="inside">Inside</option>
        <option value="outside">Outside</option>
        </select>
        <br><br>
        <label style="font-size:1.1rem">Box Shadow</label>
        <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the shadow color:</label>
        <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
        <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
        <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
        <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
        <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Thickness:</label>
        <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
        <label style="font-size:1.1rem">Box Border</label>
        <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the border color:</label>
        <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
        <label style="font-size:1.1rem">Set border thickness</label>
        <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
        <label style="font-size:1.1rem">Choose border style:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
        <option value="solid">Solid</option>
        <option value="dotted">Dotted</option>
        <option value="double">Double</option>
        <option value="dashed">Dashed</option>
        </select><br><br>
        <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}
        <br>${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        ${modalDataConfig.optionvaluesHTML}
        </div>
        </div>
        `)
    }else if(modalDataConfig.graph_subtype === 'Bubble_Map'){
        return $(`

        <div class="modal-dialog modalgraphs modal-full-height modal-right" id=${modalDataConfig.id7} role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">


        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id=${modalDataConfig.id10} aria-label="Close">
        <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>
        <input type="color" id=${modalDataConfig.id1} name="favcolor" value="#b8860b"><br><br>
        <label style="font-size:1.1rem">Change the color or an element:</label>
        <input type="color" id=${modalDataConfig.id4} name="favcolor1" value="#b8860b">
        <br><br>
        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        </div>
        </div>
        `)
    }else if(modalDataConfig.graph_subtype === 'Chloropeth_Map'){
        return $(`
        <div class="modal-dialog modalgraphs modal-full-height modal-right" id=${modalDataConfig.id7} role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">


        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id=${modalDataConfig.id10} aria-label="Close">
        <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>
        <input type="color" id=${modalDataConfig.id1} name="favcolor" value="#b8860b"><br><br>
        <label style="font-size:1.1rem">Change the color or an element:</label>
        <input type="color" id=${modalDataConfig.id4} name="favcolor1" value="#b8860b">
        <br><br>
        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        </div>
        </div>
        `)
    }else if(modalDataConfig.graph_subtype === 'Sunburst'){
        return $(`
        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">
        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>

        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br>
        <label style="font-size:1.1rem">Change the color or an element:</label>
        <input type="color" id="${modalDataConfig.id4}" name="favcolor1" value="${modalDataConfig.element_color}">
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label></div>

        <br><br>
        <label style="font-size:1.1rem">Chart interaction:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" checked="checked" name="defaultValueConfig" id="${modalDataConfig.id21}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id21}" class="custom-control-label">
                      Cross-filter
                      </label>
                  </div>
        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        <label style="font-size:1.1rem">Show/Hide Labels:</label>
        <button id="${modalDataConfig.id_showlabel}" type="button" class="btn btn-primary" data-toggle="button" role="tab"
        aria-pressed="false" autocomplete="off" value="${modalDataConfig.label_value}" style="line-height: 0.7;">${modalDataConfig.label_text}</button>
        <br><br>
        <label style="font-size:1.1rem">Box Shadow</label>
        <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the shadow color:</label>
        <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
        <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
        <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
        <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
        <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Thickness:</label>
        <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
        <label style="font-size:1.1rem">Box Border</label>
        <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the border color:</label>
        <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
        <label style="font-size:1.1rem">Set border thickness</label>
        <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
        <label style="font-size:1.1rem">Choose border style:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
        <option value="solid">Solid</option>
        <option value="dotted">Dotted</option>
        <option value="double">Double</option>
        <option value="dashed">Dashed</option>
        </select><br><br>
        <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}
        <br>${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        ${modalDataConfig.optionvaluesHTML}
        </div>
        </div>
        `)
    }else if(modalDataConfig.graph_subtype === 'Donut_Chart'){
        return $(`
        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">
        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>
        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br>
        <label style="font-size:1.1rem">Change the color or an element:</label>
        <input type="color" id="${modalDataConfig.id4}" name="favcolor1" value="${modalDataConfig.element_color}">
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label></div>

        <br><br>
        <label style="font-size:1.1rem">Chart interaction:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" checked="checked" name="defaultValueConfig" id="${modalDataConfig.id21}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id21}" class="custom-control-label">
                      Cross-filter
                      </label>
                  </div>
        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        <label style="font-size:1.1rem">Show/Hide Labels:</label>
          <button id="${modalDataConfig.id_showlabel}" type="button" class="btn btn-primary" data-toggle="button" role="tab"
          aria-pressed="false" autocomplete="off" value="${modalDataConfig.label_value}" style="line-height: 0.7;">${modalDataConfig.label_text}</button><br><br>
          <label style="font-size:1.1rem">Position Legends:</label>
        <select class="select2" name="position_legends" id="${modalDataConfig.id_position_legends}" style="font-size:1.1rem">
        <option value="">-----</option>
        <option value="top_centre">Top Centre</option>
        <option value="top_left">Top Left</option>
        <option value="top_right">Top Right</option>
        <option value="bottom_centre">Bottom Centre</option>
        <option value="bottom_left">Bottom Left</option>
        <option value="bottom_right">Bottom Right</option>
        </select><br><br>
        <label style="font-size:1.1rem">Label Placement:</label>
        <select class="select2" name="position_legends" id="${modalDataConfig.id_label_placement}" style="font-size:1.1rem">
        <option value="">-----</option>
        <option value="inside">Inside</option>
        <option value="outside">Outside</option>
        </select>
        <br><br>
        <label style="font-size:1.1rem">Box Shadow</label>
        <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the shadow color:</label>
        <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
        <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
        <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
        <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
        <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Thickness:</label>
        <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
        <label style="font-size:1.1rem">Box Border</label>
        <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the border color:</label>
        <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
        <label style="font-size:1.1rem">Set border thickness</label>
        <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
        <label style="font-size:1.1rem">Choose border style:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
        <option value="solid">Solid</option>
        <option value="dotted">Dotted</option>
        <option value="double">Double</option>
        <option value="dashed">Dashed</option>
        </select><br><br>
        <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>
        ${modalDataConfig.borderStylehtml}
        <br>${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        ${modalDataConfig.optionvaluesHTML}
        </div>
        </div>
        `)

    }else if(modalDataConfig.graph_subtype === 'Treemap'){
        return $(`
        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">
        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>
        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br>
        <label style="font-size:1.1rem">Change the color or an element:</label>
        <input type="color" id="${modalDataConfig.id4}" name="favcolor1" value="${modalDataConfig.element_color}">
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label>
                      </div>

        <br><br>
        <label style="font-size:1.1rem">Chart interaction:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" checked="checked" name="defaultValueConfig" id="${modalDataConfig.id21}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id21}" class="custom-control-label">
                      Cross-filter
                      </label>
                  </div>
        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        <br><br>
        <label style="font-size:1.1rem">Box Shadow</label>
        <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the shadow color:</label>
        <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
        <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
        <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
        <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
        <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Thickness:</label>
        <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
        <label style="font-size:1.1rem">Box Border</label>
        <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the border color:</label>
        <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
        <label style="font-size:1.1rem">Set border thickness</label>
        <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
        <label style="font-size:1.1rem">Choose border style:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
        <option value="solid">Solid</option>
        <option value="dotted">Dotted</option>
        <option value="double">Double</option>
        <option value="dashed">Dashed</option>
        </select><br><br>
        <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>
        ${modalDataConfig.borderStylehtml}
        <br>${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        ${modalDataConfig.optionvaluesHTML}
        </div>
        </div>
        `)
    }else if(modalDataConfig.graph_subtype === 'Line'){
        return $(`

        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">


        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>

        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br>
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label>
                      </div>
        <br><br>

        <label style="font-size:1.1rem">Change X and Y axis gridlines:</label>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id9}" data-toggle="button" role="tab"
                        aria-pressed="false" autocomplete="off" value="${modalDataConfig.grid_id}" style="line-height: 0.7;">${modalDataConfig.value}</button><br><br>
                        <label style="font-size:1.1rem">Change the range of the axis:</label>
        <input type="text" placeholder="Y Axis Start" id="${modalDataConfig.id2}" value="${modalDataConfig.y_axis_start}" size="7">
        <input type="text" placeholder="Y Axis End " id="${modalDataConfig.id3}" value="${modalDataConfig.y_axis_end}" size="7">
        <br><br>
        <label style="font-size:1.1rem">Change the title of the axes:</label>
        <input type="text" placeholder="X Axis Title" id="${modalDataConfig.id11}" value="${modalDataConfig.x_axis_title}" size="7">
        <input type="text" placeholder="Y Axis Title" id='${modalDataConfig.id12}' value="${modalDataConfig.y_axis_title}" size="7">
        <br><br>
        <label style="font-size:1.1rem">Change the label of an element:</label><br>
        <input type="text" placeholder="X Axis Label" id="${modalDataConfig.id13}" size="9" value="${modalDataConfig.element_label}"> &nbsp;&nbsp;
        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id18}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" style="line-height: 1.1;">Reset Axis Labels</button>
                          <label style="font-size:1.1rem">Change Plot Labels:</label>
                          <button type="button" class="btn btn-primary" id="${modalDataConfig.id_labels}" data-toggle="button" role="tab"

                          aria-pressed="false" autocomplete="off" value="${modalDataConfig.label_value}" style="line-height: 1.1;">${modalDataConfig.label_text}</button>
                          <br><br>
                          <label style="font-size:1.1rem">Label Placement:</label>
        <select class="select2" name="position_legends" id="${modalDataConfig.id_label_placement}" style="font-size:1.1rem">
        <option value="">-----</option>
        <option value="top">Top</option>
        <option value="bottom">Bottom</option>
        <option value="center">Center</option>
        </select>
        <br><br>
        <label style="font-size:1.1rem">Box Shadow</label>
        <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the shadow color:</label>
        <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
        <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
        <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
        <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
        <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Thickness:</label>
        <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
        <label style="font-size:1.1rem">Box Border</label>
        <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the border color:</label>
        <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
        <label style="font-size:1.1rem">Set border thickness</label>
        <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
        <label style="font-size:1.1rem">Choose border style:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
        <option value="solid">Solid</option>
        <option value="dotted">Dotted</option>
        <option value="double">Double</option>
        <option value="dashed">Dashed</option>
        </select><br><br>
        <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}
        <br>${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        <br>
        <label style="font-size:1.1rem">Set order for X Axis:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_axis_order}" style="font-size:1.1rem" onchange="changeOrder.call(this)" data-chart-id = "${modalDataConfig.id6}" datatype_dict = '${JSON.stringify(modalDataConfig.datatype_dict)}' mappingDict = '${JSON.stringify(modalDataConfig.mappingDict)}' order_type = 'Vertical' >
        <option value="" selected>----------</option>
        <option value="asc">Ascending</option>
        <option value="desc">Descending</option>
        <option value="cust">Custom</option>
        </select>
        <br>
        <button class="btn btn-primary btn-xs rounded px-2" id="${modalDataConfig.idOrderModal}Button" data-modal_id="${modalDataConfig.idOrderModal}" data-chart-id = "${modalDataConfig.id6}" data-sorted-values = "" onclick="orderModal.call(this)" datatype_dict = '${JSON.stringify(modalDataConfig.datatype_dict)}' order_type = 'Vertical' style="display:none; height : 30px;">Set preferred order
        </button>
        ${modalDataConfig.optionvaluesHTML}
        <br><br>
        <label style="font-size:1.1rem">Change labels color:</label>
        <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
        <br>
        <label style="font-size:1.1rem">Set labels font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>
        </div>
        </div>
        `)
    }else if(modalDataConfig.graph_subtype === 'Multiple_Line_Chart'){
        return $(`
        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">
        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
            <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>

        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br>
        <label style="font-size:1.1rem">Change the graph background:</label>
                    <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                    <label style="font-size:1.1rem">Visualization Theme:</label>
                    <div class="custom-control custom-checkbox">
                        <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                        <label for="${modalDataConfig.id23}" class="custom-control-label">
                        Global Settings
                        </label>
                        </div>
        <br><br>
        <label style="font-size:1.1rem">Change X and Y axis gridlines:</label>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id9}" data-toggle="button" role="tab"
                        aria-pressed="false" autocomplete="off" value="${modalDataConfig.grid_id}" style="line-height: 0.7;">${modalDataConfig.value}</button><br><br>
                        <label style="font-size:1.1rem">Change the range of the axis:</label>
        <input type="text" placeholder="Y Axis Start" id="${modalDataConfig.id2}" value="${modalDataConfig.y_axis_start}" size="7">
        <input type="text" placeholder="Y Axis End " id="${modalDataConfig.id3}" value="${modalDataConfig.y_axis_end}" size="7">
        <br><br>
        <label style="font-size:1.1rem">Change the title of the axes:</label>
        <input type="text" placeholder="X Axis Title" id="${modalDataConfig.id11}" value="${modalDataConfig.x_axis_title}" size="7">
        <br><br>
        <label style="font-size:1.1rem">Change the label of an element:</label><br>
        <input type="text" placeholder="X Axis Label" id="${modalDataConfig.id13}" size="9" value="${modalDataConfig.element_label}"> &nbsp;&nbsp;
        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id18}" data-toggle="button" role="tab"
                            aria-pressed="false" autocomplete="off" style="line-height: 1.1;">Reset Axis Labels</button>
                            <label style="font-size:1.1rem">Change Plot Labels:</label>
                            <button type="button" class="btn btn-primary" id="${modalDataConfig.id_labels}" data-toggle="button" role="tab"

                            aria-pressed="false" autocomplete="off" value="${modalDataConfig.label_value}" style="line-height: 1.1;">${modalDataConfig.label_text}</button>
                            <br><br>
                            <label style="font-size:1.1rem">Label Placement:</label>
        <select class="select2" name="position_legends" id="${modalDataConfig.id_label_placement}" style="font-size:1.1rem">
        <option value="">-----</option>
        <option value="top">Top</option>
        <option value="bottom">Bottom</option>
        <option value="center">Center</option>
        </select>
        <br><br>
        <label style="font-size:1.1rem">Box Shadow</label>
        <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the shadow color:</label>
        <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
        <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
        <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
        <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
        <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Thickness:</label>
        <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
        <label style="font-size:1.1rem">Box Border</label>
        <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the border color:</label>
        <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
        <label style="font-size:1.1rem">Set border thickness</label>
        <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
        <label style="font-size:1.1rem">Choose border style:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
        <option value="solid">Solid</option>
        <option value="dotted">Dotted</option>
        <option value="double">Double</option>
        <option value="dashed">Dashed</option>
        </select><br><br>
        <label style="font-size:1.1rem">Change header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}
        <br>${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        <br>
        <label style="font-size:1.1rem">Set order for X Axis:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_axis_order}" style="font-size:1.1rem" onchange="changeOrder.call(this)" data-chart-id = "${modalDataConfig.id6}" datatype_dict = '${JSON.stringify(modalDataConfig.datatype_dict)}' mappingDict = '${JSON.stringify(modalDataConfig.mappingDict)}' order_type = 'Vertical' >
        <option value="" selected>----------</option>
        <option value="asc">Ascending</option>
        <option value="desc">Descending</option>
        <option value="cust">Custom</option>
        </select>
        <br>
        <button class="btn btn-primary btn-xs rounded px-2" id="${modalDataConfig.idOrderModal}Button" data-modal_id="${modalDataConfig.idOrderModal}" data-chart-id = "${modalDataConfig.id6}" data-sorted-values = "" onclick="orderModal.call(this)" datatype_dict = '${JSON.stringify(modalDataConfig.datatype_dict)}' order_type = 'Vertical' style="display:none; height : 30px;">Set preferred order
        </button>
        ${modalDataConfig.optionvaluesHTML}
        <br><br>
        <label style="font-size:1.1rem">Change labels color:</label>
        <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
        <br>
        <label style="font-size:1.1rem">Set labels font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>
        </div>
        </div>
        `)
    }else if(modalDataConfig.graph_subtype === 'Vertical_Area'){
        return $(`
        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">
        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>

        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br>
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label></div>
                  <br><br>

        <label style="font-size:1.1rem">Change X and Y axis gridlines:</label>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id9}" data-toggle="button" role="tab"
                        aria-pressed="false" autocomplete="off" value="${modalDataConfig.grid_id}" style="line-height: 0.7;">${modalDataConfig.value}</button><br><br>
                        <label style="font-size:1.1rem">Change the range of the axis:</label>
        <input type="text" placeholder="Y Axis Start" id="${modalDataConfig.id2}" size="7" value="${modalDataConfig.y_axis_start}">
        <input type="text" placeholder="Y Axis End " id="${modalDataConfig.id3}" size="7" value="${modalDataConfig.y_axis_end}">
        <br><br>
        <label style="font-size:1.1rem">Change the title of the axes:</label>
        <input type="text" placeholder="X Axis Title" id="${modalDataConfig.id11}" size="7" value="${modalDataConfig.x_axis_title}">
        <input type="text" placeholder="Y Axis Title" id="${modalDataConfig.id12}" size="7" value="${modalDataConfig.y_axis_title}">
        <br><br>
        <label style="font-size:1.1rem">Change the label of an element:</label><br>
        <input type="text" placeholder="X Axis Label" id="${modalDataConfig.id13}" size="9" value="${modalDataConfig.element_label}"> &nbsp;&nbsp;
        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id18}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" style="line-height: 1.1;">Reset Axis Labels</button><br><br>
                          <label style="font-size:1.1rem">Change Plot Labels:</label>
                          <button type="button" class="btn btn-primary" id="${modalDataConfig.id_labels}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" value="${modalDataConfig.label_value}" style="line-height: 1.1;">${modalDataConfig.label_text}</button>
                          <br><br>
                          <label style="font-size:1.1rem">Box Shadow</label>
                          <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the shadow color:</label>
                          <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
                          <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
                          <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
                          <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Thickness:</label>
                          <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Box Border</label>
                          <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the border color:</label>
                          <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
                          <label style="font-size:1.1rem">Set border thickness</label>
                          <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
                          <label style="font-size:1.1rem">Choose border style:</label>
                          <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
                          <option value="solid">Solid</option>
                          <option value="dotted">Dotted</option>
                          <option value="double">Double</option>
                          <option value="dashed">Dashed</option>
                          </select><br><br>
                          <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}
        <br>${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        <br>
        <label style="font-size:1.1rem">Set order for X Axis:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_axis_order}" style="font-size:1.1rem" onchange="changeOrder.call(this)" data-chart-id = "${modalDataConfig.id6}" datatype_dict = '${JSON.stringify(modalDataConfig.datatype_dict)}' mappingDict = '${JSON.stringify(modalDataConfig.mappingDict)}' order_type = 'Vertical' >
        <option value="" selected>----------</option>
        <option value="asc">Ascending</option>
        <option value="desc">Descending</option>
        <option value="cust">Custom</option>
        </select>
        <br>
        <button class="btn btn-primary btn-xs rounded px-2" id="${modalDataConfig.idOrderModal}Button" data-modal_id="${modalDataConfig.idOrderModal}" data-chart-id = "${modalDataConfig.id6}" data-sorted-values = "" onclick="orderModal.call(this)" datatype_dict = '${JSON.stringify(modalDataConfig.datatype_dict)}' order_type = 'Vertical' style="display:none; height : 30px;">Set preferred order
        </button>
        ${modalDataConfig.optionvaluesHTML}
        <br><br>
        <label style="font-size:1.1rem">Change labels color:</label>
        <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
        <br>
        <label style="font-size:1.1rem">Set labels font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>
        </div>
        </div>
        `)
    }else if(modalDataConfig.graph_subtype === 'Horizontal_Area'){
        return $(`

        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">


        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
        <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>

        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br>
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label>
                      </div>
                  <br><br>
        <label style="font-size:1.1rem">Change X and Y axis gridlines:</label>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id9}" data-toggle="button" role="tab"
        aria-pressed="false" autocomplete="off" value="${modalDataConfig.grid_id}" style="line-height: 0.7;">${modalDataConfig.value}</button><br><br>
        <label style="font-size:1.1rem">Change the range of the axis:</label>
        <input type="text" placeholder="Y Axis Start" id="${modalDataConfig.id2}" size="7" value="${modalDataConfig.y_axis_start}">
        <input type="text" placeholder="Y Axis End " id="${modalDataConfig.id3}" size="7" value="${modalDataConfig.y_axis_end}">
        <br><br>
        <label style="font-size:1.1rem">Change the title of the axes:</label>
        <input type="text" placeholder="X Axis Title" id="${modalDataConfig.id11}" size="7" value="${modalDataConfig.y_axis_title}">
        <input type="text" placeholder="Y Axis Title" id="${modalDataConfig.id12}" size="7" value="${modalDataConfig.y_axis_title}">
        <br><br>
        <label style="font-size:1.1rem">Change the label of an element:</label><br>
        <input type="text" placeholder="Y Axis Label" id="${modalDataConfig.id13}' size="9" value="${modalDataConfig.element_label}"> &nbsp;&nbsp;<br><br>
        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id18}" data-toggle="button" role="tab"
        aria-pressed="false" autocomplete="off" style="line-height: 1.1;">Reset Axis Labels</button><br><br>
        <label style="font-size:1.1rem">Change Plot Labels:</label>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id_labels}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" value="${modalDataConfig.label_value}" style="line-height: 1.1;">${modalDataConfig.label_text}</button>
                          <br><br>
                          <label style="font-size:1.1rem">Box Shadow</label>
                          <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the shadow color:</label>
                          <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
                          <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
                          <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
                          <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Thickness:</label>
                          <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Box Border</label>
                          <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the border color:</label>
                          <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
                          <label style="font-size:1.1rem">Set border thickness</label>
                          <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
                          <label style="font-size:1.1rem">Choose border style:</label>
                          <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
                          <option value="solid">Solid</option>
                          <option value="dotted">Dotted</option>
                          <option value="double">Double</option>
                          <option value="dashed">Dashed</option>
                          </select><br><br>
                          <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}
        <br>${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        <br>
        <label style="font-size:1.1rem">Set order for Y Axis:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_axis_order}" style="font-size:1.1rem" onchange="changeOrder.call(this)" data-chart-id = "${modalDataConfig.id6}" datatype_dict = '${JSON.stringify(modalDataConfig.datatype_dict)}' mappingDict = '${JSON.stringify(modalDataConfig.mappingDict)}' order_type = 'Horizontal'>
        <option value="" selected>----------</option>
        <option value="asc">Ascending</option>
        <option value="desc">Descending</option>
        <option value="cust">Custom</option>
        </select>
        <br>
        <button class="btn btn-primary btn-xs rounded px-2" id="${modalDataConfig.idOrderModal}Button" data-modal_id="${modalDataConfig.idOrderModal}" data-chart-id = "${modalDataConfig.id6}" data-sorted-values = "" onclick="orderModal.call(this)" datatype_dict = '${JSON.stringify(modalDataConfig.datatype_dict)}' order_type = 'Horizontal' style="display:none; height : 30px;">Set preferred order
        </button>
        ${modalDataConfig.optionvaluesHTML}
        <br><br>
        <label style="font-size:1.1rem">Change labels color:</label>
        <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
        <br>
        <label style="font-size:1.1rem">Set labels font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>
        </div>
        </div>
        `)

    }else if(modalDataConfig.graph_subtype === 'Stepped_Line'){
        return $(`

            <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
            right: 0 ;top : 10px;z-index: 1050">


            <div class="modal-content">
            <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
            <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
            <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
                <span aria-hidden="true">&times;</span>
            </button>
            </div>
            <div class="modal-body" style="max-height:26rem;overflow:auto">
            <label style="font-size:1.1rem">Change the graph color:</label>

            <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br>
            <label style="font-size:1.1rem">Change the graph background:</label>
                        <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                        <label style="font-size:1.1rem">Visualization Theme:</label>
                        <div class="custom-control custom-checkbox">
                            <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                            <label for="${modalDataConfig.id23}" class="custom-control-label">
                            Global Settings
                            </label>
                            </div>
                        <br><br>

            <label style="font-size:1.1rem">Change X and Y axis gridlines:</label>
            <button type="button" class="btn btn-primary" id="${modalDataConfig.id9}" data-toggle="button" role="tab"
                            aria-pressed="false" autocomplete="off" value="${modalDataConfig.grid_id}" style="line-height: 0.7;">${modalDataConfig.value}</button><br><br>
                            <label style="font-size:1.1rem">Change the range of the axis:</label>
            <input type="text" placeholder="Y Axis Start" id="${modalDataConfig.id2}" size="7" value="${modalDataConfig.y_axis_start}">
            <input type="text" placeholder="Y Axis End " id="${modalDataConfig.id3}" size="7" value="${modalDataConfig.y_axis_end}">
            <br><br>
            <label style="font-size:1.1rem">Change the title of the axes:</label>
            <input type="text" placeholder="X Axis Title" id="${modalDataConfig.id11}" size="7" value="${modalDataConfig.x_axis_title}">
            <input type="text" placeholder="Y Axis Title" id='${modalDataConfig.id12}' size="7" value="${modalDataConfig.y_axis_title}">
            <br><br>
            <label style="font-size:1.1rem">Change the label of an element:</label><br>
            <input type="text" placeholder="X Axis Label" id="${modalDataConfig.id13}" size="9" value="${modalDataConfig.element_label}"> &nbsp;&nbsp;
            <label style="font-size:1.1rem">Connected slicers:</label>
            <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

            </div>
            <button type="button" class="btn btn-primary" id="${modalDataConfig.id18}" data-toggle="button" role="tab"
                                aria-pressed="false" autocomplete="off" style="line-height: 1.1;">Reset Axis Labels</button><br><br>
                                <label style="font-size:1.1rem">Change Plot Labels:</label>
                                <button type="button" class="btn btn-primary" id="${modalDataConfig.id_labels}" data-toggle="button" role="tab"
                                aria-pressed="false" autocomplete="off" value="${modalDataConfig.label_value}" style="line-height: 1.1;">${modalDataConfig.label_text}</button><br><br>
                                <label style="font-size:1.1rem">Label Placement:</label>
            <select class="select2" name="position_legends" id="${modalDataConfig.id_label_placement}" style="font-size:1.1rem">
            <option value="">-----</option>
            <option value="top">Top</option>
            <option value="bottom">Bottom</option>
            <option value="center">Center</option>
            </select>
            <br><br>
            <label style="font-size:1.1rem">Box Shadow</label>
            <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
            <label style="font-size:1.1rem">Choose the shadow color:</label>
            <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
            <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
            <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
            <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
            <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
            <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
            <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
            <label style="font-size:1.1rem">Set Shadow Thickness:</label>
            <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
            <label style="font-size:1.1rem">Box Border</label>
            <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
            <label style="font-size:1.1rem">Choose the border color:</label>
            <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
            <label style="font-size:1.1rem">Set border thickness</label>
            <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
            <label style="font-size:1.1rem">Choose border style:</label>
            <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
            <option value="solid">Solid</option>
            <option value="dotted">Dotted</option>
            <option value="double">Double</option>
            <option value="dashed">Dashed</option>
            </select><br><br>
            <label style="font-size:1.1rem">Change the header color:</label>
            <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
            <br>
            <label style="font-size:1.1rem">Change the background color of header:</label>
            <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
            <label style="font-size:1.1rem">Set header font size:</label>
            <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
            <label style="font-size:1.1rem">Set header font weight:</label>

            ${modalDataConfig.borderStylehtml}
            <br>${modalDataConfig.setheaderFontHTML}
            <br>
            <label style="font-size:1.1rem">Set header alignment:</label>
            <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
            <option value="">----------</option>
            <option value="left">Left</option>
            <option value="center">Center</option>
            <option value="right">Right</option>
            </select>
            <br>
            <label style="font-size:1.1rem">Set order for X Axis:</label>
            <select class="select2" name="border_style" id="${modalDataConfig.id_axis_order}" style="font-size:1.1rem" onchange="changeOrder.call(this)" data-chart-id = "${modalDataConfig.id6}" datatype_dict = '${JSON.stringify(modalDataConfig.datatype_dict)}' mappingDict = '${JSON.stringify(modalDataConfig.mappingDict)}' order_type = 'Vertical' >
            <option value="" selected>----------</option>
            <option value="asc">Ascending</option>
            <option value="desc">Descending</option>
            <option value="cust">Custom</option>
            </select>
            <br>
            <button class="btn btn-primary btn-xs rounded px-2" id="${modalDataConfig.idOrderModal}Button" data-modal_id="${modalDataConfig.idOrderModal}" data-chart-id = "${modalDataConfig.id6}" data-sorted-values = "" onclick="orderModal.call(this)" datatype_dict = '${JSON.stringify(modalDataConfig.datatype_dict)}' order_type = 'Vertical' style="display:none; height : 30px;">Set preferred order
            </button>
            ${modalDataConfig.optionvaluesHTML}
            <br><br>
        <label style="font-size:1.1rem">Change labels color:</label>
        <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
        <br>
        <label style="font-size:1.1rem">Set labels font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>
            </div>
            </div>
            `)
    }else if(modalDataConfig.graph_subtype === 'Vertical_Line_Stacked'){
        return $(`

        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">


        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>

        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br>
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label>
                      </div>
                  <br><br>

        <label style="font-size:1.1rem">Change X and Y axis gridlines:</label>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id9}" data-toggle="button" role="tab"
                        aria-pressed="false" autocomplete="off" value="${modalDataConfig.grid_id}" style="line-height: 0.7;">${modalDataConfig.value}</button><br><br>
                        <label style="font-size:1.1rem">Change the range of the axis:</label>
        <input type="text" placeholder="Y Axis Start" id="${modalDataConfig.id2}" size="7" value="${modalDataConfig.y_axis_start}">
        <input type="text" placeholder="Y Axis End " id="${modalDataConfig.id3}" size="7" value="${modalDataConfig.y_axis_end}">
        <br><br>
        <label style="font-size:1.1rem">Change the title of the axes:</label>
        <input type="text" placeholder="X Axis Title" id="${modalDataConfig.id11}" size="7" value="${modalDataConfig.x_axis_title}">
        <br><br>
        <label style="font-size:1.1rem">Change the legend labels:</label>
        <input type="text" placeholder=${modalDataConfig.mappingDict[modalDataConfig.y_axis]} id="${modalDataConfig.id14}" size="7" value="${modalDataConfig.legend_x}">
        <input type="text" placeholder=${modalDataConfig.mappingDict[modalDataConfig.second_column]} id="${modalDataConfig.id15}" size="7" value="${modalDataConfig.legend_y}">
        <br><br>
        <label style="font-size:1.1rem">Change the label of an element:</label><br>
        <input type="text" placeholder="X Axis Label" id="${modalDataConfig.id13}" size="9" value="${modalDataConfig.element_label}"> &nbsp;&nbsp;
        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>


        <button type="button" class="btn btn-primary" id="${modalDataConfig.id18}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" style="line-height: 1.1;">Reset Axis Labels</button><br><br>
                          <label style="font-size:1.1rem">Change Plot Labels:</label>
                          <button type="button" class="btn btn-primary" id="${modalDataConfig.id_labels}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" value="${modalDataConfig.label_value}" style="line-height: 1.1;">${modalDataConfig.label_text}</button>
                          <br><br>
        <label style="font-size:1.1rem">Label Placement:</label>
        <select class="select2" name="position_legends" id="${modalDataConfig.id_label_placement}" style="font-size:1.1rem">
        <option value="">-----</option>
        <option value="top">Top</option>
        <option value="bottom">Bottom</option>
        <option value="center">Center</option>
        </select>
        <br><br>
        <label style="font-size:1.1rem">Box Shadow</label>
        <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the shadow color:</label>
        <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
        <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
        <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
        <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
        <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Thickness:</label>
        <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
        <label style="font-size:1.1rem">Box Border</label>
        <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the border color:</label>
        <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
        <label style="font-size:1.1rem">Set border thickness</label>
        <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
        <label style="font-size:1.1rem">Choose border style:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
        <option value="solid">Solid</option>
        <option value="dotted">Dotted</option>
        <option value="double">Double</option>
        <option value="dashed">Dashed</option>
        </select><br><br>
        <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}
        <br>${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        <br>
        <label style="font-size:1.1rem">Set order for X Axis:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_axis_order}" style="font-size:1.1rem" onchange="changeOrder.call(this)" data-chart-id = "${modalDataConfig.id6}" datatype_dict = '${JSON.stringify(modalDataConfig.datatype_dict)}' mappingDict = '${JSON.stringify(modalDataConfig.mappingDict)}' order_type = 'Vertical' >
        <option value="" selected>----------</option>
        <option value="asc">Ascending</option>
        <option value="desc">Descending</option>
        <option value="cust">Custom</option>
        </select>
        <br>
        <button class="btn btn-primary btn-xs rounded px-2" id="${modalDataConfig.idOrderModal}Button" data-modal_id="${modalDataConfig.idOrderModal}" data-chart-id = "${modalDataConfig.id6}" data-sorted-values = "" onclick="orderModal.call(this)" datatype_dict = '${JSON.stringify(modalDataConfig.datatype_dict)}' order_type = 'Vertical' style="display:none; height : 30px;">Set preferred order
        </button>
        ${modalDataConfig.optionvaluesHTML}
        <br><br>
        <label style="font-size:1.1rem">Change labels color:</label>
        <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
        <br>
        <label style="font-size:1.1rem">Set labels font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>
        </div>
        </div>
        `)

    }else if(modalDataConfig.graph_subtype === 'Vertical_Grouped_Box'){
        return $(`

        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">


        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>

        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br>
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label>
                      </div>
                  <br><br>

        <label style="font-size:1.1rem">Change X and Y axis gridlines:</label>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id9}" data-toggle="button" role="tab"
                        aria-pressed="false" autocomplete="off" value="${modalDataConfig.grid_id}" style="line-height: 0.7;">${modalDataConfig.value}</button><br><br>
                        <label style="font-size:1.1rem">Change the range of the axis:</label>
        <input type="text" placeholder="Y Axis Start" id="${modalDataConfig.id2}" size="7" value="${modalDataConfig.y_axis_start}">
        <input type="text" placeholder="Y Axis End " id="${modalDataConfig.id3}" size="7" value="${modalDataConfig.y_axis_end}">
        <br><br>
        <label style="font-size:1.1rem">Change the title of the axes:</label>
        <input type="text" placeholder="X Axis Title" id="${modalDataConfig.id11}" size="7" value="${modalDataConfig.x_axis_title}">
        <br><br>
        <label style="font-size:1.1rem">Change the legend labels:</label>
        <input type="text" placeholder=${modalDataConfig.mappingDict[modalDataConfig.y_axis]} id="${modalDataConfig.id14}" size="7" value="${modalDataConfig.legend_x}">
        <input type="text" placeholder=${modalDataConfig.mappingDict[modalDataConfig.second_column]} id="${modalDataConfig.id15}" size="7" value="${modalDataConfig.legend_y}">
        <br><br>
        <label style="font-size:1.1rem">Change the label of an element:</label><br>
        <input type="text" placeholder="X Axis Label" id="${modalDataConfig.id13}" size="9" value="${modalDataConfig.element_label}"> &nbsp;&nbsp;
        <label style="font-size:1.1rem">Chart interaction:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" checked="checked" name="defaultValueConfig" id="${modalDataConfig.id21}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id21}" class="custom-control-label">
                      Cross-filter
                      </label>
                  </div>
        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id18}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" style="line-height: 1.1;">Reset Axis Labels</button>
                          <br><br>
                          <label style="font-size:1.1rem">Box Shadow</label>
                          <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the shadow color:</label>
                          <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
                          <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
                          <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
                          <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Thickness:</label>
                          <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Box Border</label>
                          <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the border color:</label>
                          <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
                          <label style="font-size:1.1rem">Set border thickness</label>
                          <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
                          <label style="font-size:1.1rem">Choose border style:</label>
                          <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
                          <option value="solid">Solid</option>
                          <option value="dotted">Dotted</option>
                          <option value="double">Double</option>
                          <option value="dashed">Dashed</option>
                          </select><br><br>
                          <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}
        <br>${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        <br><br>
        <label style="font-size:1.1rem">Change the labels color:</label>
        <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
        <br>
        <label style="font-size:1.1rem">Set labels font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>
        </div>
        </div>
        `)
    }else if(modalDataConfig.graph_subtype === 'Vertical_Grouped_Violin'){
        return $(`
        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">


        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>

        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br>
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label></div><br><br>

        <label style="font-size:1.1rem">Change X and Y axis gridlines:</label>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id9}" data-toggle="button" role="tab"
                        aria-pressed="false" autocomplete="off" value="${modalDataConfig.grid_id}" style="line-height: 0.7;">${modalDataConfig.value}</button><br><br>
                        <label style="font-size:1.1rem">Change the range of the axis:</label>
        <input type="text" placeholder="Y Axis Start" id="${modalDataConfig.id2}" size="7" value="${modalDataConfig.y_axis_start}">
        <input type="text" placeholder="Y Axis End " id="${modalDataConfig.id3}" size="7" value="${modalDataConfig.y_axis_end}">
        <br><br>
        <label style="font-size:1.1rem">Change the title of the axes:</label>
        <input type="text" placeholder="X Axis Title" id="${modalDataConfig.id11}" size="7" value="${modalDataConfig.x_axis_title}">
        <br><br>
        <label style="font-size:1.1rem">Change the legend labels:</label>
        <input type="text" placeholder=${modalDataConfig.mappingDict[modalDataConfig.y_axis]} id="${modalDataConfig.id14}" size="7" value="${modalDataConfig.legend_x}">
        <input type="text" placeholder=${modalDataConfig.mappingDict[modalDataConfig.second_column]} id="${modalDataConfig.id15}" size="7" value="${modalDataConfig.legend_y}">
        <br><br>
        <label style="font-size:1.1rem">Change the label of an element:</label><br>
        <input type="text" placeholder="X Axis Label" id="${modalDataConfig.id13}" size="9" value="${modalDataConfig.element_label}"> &nbsp;&nbsp;
        <label style="font-size:1.1rem">Chart interaction:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" checked="checked" name="defaultValueConfig" id="${modalDataConfig.id21}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id21}" class="custom-control-label">
                      Cross-filter
                      </label>
                  </div>
        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id18}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" style="line-height: 1.1;">Reset Axis Labels</button>
                          <br><br>
                          <label style="font-size:1.1rem">Box Shadow</label>
                          <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the shadow color:</label>
                          <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
                          <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
                          <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
                          <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Thickness:</label>
                          <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Box Border</label>
                          <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the border color:</label>
                          <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
                          <label style="font-size:1.1rem">Set border thickness</label>
                          <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
                          <label style="font-size:1.1rem">Choose border style:</label>
                          <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
                          <option value="solid">Solid</option>
                          <option value="dotted">Dotted</option>
                          <option value="double">Double</option>
                          <option value="dashed">Dashed</option>
                          </select><br><br>
                          <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}
        <br>${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        <br><br>
        <label style="font-size:1.1rem">Change labels color:</label>
        <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
        <br>
        <label style="font-size:1.1rem">Set labels font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>
        </div>
        </div>
        `)
    }else if(modalDataConfig.graph_subtype === 'Vertical_Area_Stacked'){
        return $(`
        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">


        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>

        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br>
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label></div><br><br>

        <label style="font-size:1.1rem">Change X and Y axis gridlines:</label>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id9}" data-toggle="button" role="tab"
                        aria-pressed="false" autocomplete="off" value="${modalDataConfig.grid_id}" style="line-height: 0.7;">${modalDataConfig.value}</button><br><br>
                        <label style="font-size:1.1rem">Change the range of the axis:</label>
        <input type="text" placeholder="Y Axis Start" id="${modalDataConfig.id2}" size="7" value="${modalDataConfig.y_axis_start}">
        <input type="text" placeholder="Y Axis End " id="${modalDataConfig.id3}" size="7" value="${modalDataConfig.y_axis_end}">
        <br><br>
        <label style="font-size:1.1rem">Change the title of the axes:</label>
        <input type="text" placeholder="X Axis Title" id="${modalDataConfig.id11}" size="7" value="${modalDataConfig.x_axis_title}">
        <br><br>
        <label style="font-size:1.1rem">Change the legend labels:</label>
        <input type="text" placeholder=${modalDataConfig.mappingDict[modalDataConfig.y_axis]} id="${modalDataConfig.id14}" size="7" value="${modalDataConfig.legend_x}">
        <input type="text" placeholder=${modalDataConfig.mappingDict[modalDataConfig.second_column]} id="${modalDataConfig.id15}" size="7" value="${modalDataConfig.legend_y}">
        <br><br>
        <label style="font-size:1.1rem">Change the label of an element:</label><br>
        <input type="text" placeholder="X Axis Label" id="${modalDataConfig.id13}" size="9" value="${modalDataConfig.element_label}"> &nbsp;&nbsp;
        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id18}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" style="line-height: 1.1;">Reset Axis Labels</button><br><br>
                          <label style="font-size:1.1rem">Change Plot Labels:</label>
                          <button type="button" class="btn btn-primary" id="${modalDataConfig.id_labels}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" value="${modalDataConfig.label_value}" style="line-height: 1.1;">${modalDataConfig.label_text}</button>
                          <br><br>
                          <label style="font-size:1.1rem">Box Shadow</label>
                          <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the shadow color:</label>
                          <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
                          <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
                          <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
                          <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Thickness:</label>
                          <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Box Border</label>
                          <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the border color:</label>
                          <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
                          <label style="font-size:1.1rem">Set border thickness</label>
                          <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
                          <label style="font-size:1.1rem">Choose border style:</label>
                          <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
                          <option value="solid">Solid</option>
                          <option value="dotted">Dotted</option>
                          <option value="double">Double</option>
                          <option value="dashed">Dashed</option>
                          </select><br><br>
                          <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}
        <br>${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        <br>
        <label style="font-size:1.1rem">Set order for X Axis:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_axis_order}" style="font-size:1.1rem" onchange="changeOrder.call(this)" data-chart-id = "${modalDataConfig.id6}" datatype_dict = '${JSON.stringify(modalDataConfig.datatype_dict)}' mappingDict = '${JSON.stringify(modalDataConfig.mappingDict)}' order_type = 'Vertical' >
        <option value="" selected>----------</option>
        <option value="asc">Ascending</option>
        <option value="desc">Descending</option>
        <option value="cust">Custom</option>
        </select>
        <br>
        <button class="btn btn-primary btn-xs rounded px-2" id="${modalDataConfig.idOrderModal}Button" data-modal_id="${modalDataConfig.idOrderModal}" data-chart-id = "${modalDataConfig.id6}" data-sorted-values = "" onclick="orderModal.call(this)" datatype_dict = '${JSON.stringify(modalDataConfig.datatype_dict)}' order_type = 'Vertical' style="display:none; height : 30px;">Set preferred order
        </button>
        ${modalDataConfig.optionvaluesHTML}
        <br><br>
        <label style="font-size:1.1rem">Change labels color:</label>
        <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
        <br>
        <label style="font-size:1.1rem">Set labels font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>
        </div>
        </div>
        `)
    }else if(modalDataConfig.graph_subtype === 'Horizontal_Bar'){
     return $(`
        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">
        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>

        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br>
        <div class="custom-control custom-checkbox">
                      <input type="checkbox" checked="checked" name="defaultValueColorConfig" id="${modalDataConfig.id24}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id24}" class="custom-control-label">
                      Gradient Color
                      </label>
                  </div>
                  <br><br><label style="font-size:1.1rem">Change the color or an element:</label>
        <input type="color" id="${modalDataConfig.id4}" name="favcolor1" value="${modalDataConfig.element_color}"><br><br>
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label></div><br><br>

        <label style="font-size:1.1rem">Change X and Y axis gridlines:</label>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id9}" data-toggle="button" role="tab"
                        aria-pressed="false" autocomplete="off" value="${modalDataConfig.grid_id}" style="line-height: 0.7;">${modalDataConfig.value}</button><br><br>
                        <label style="font-size:1.1rem">Change the range of the axis:</label>
        <input type="text" placeholder="Y Axis Start" id="${modalDataConfig.id2}" size="7" value="${modalDataConfig.y_axis_start}">
        <input type="text" placeholder="Y Axis End " id="${modalDataConfig.id3}" size="7" value="${modalDataConfig.y_axis_end}">
        <br><br>
        <label style="font-size:1.1rem">Change the title of the axes:</label>
        <input type="text" placeholder="X Axis Title" id="${modalDataConfig.id11}" size="7" value="${modalDataConfig.x_axis_title}">
        <input type="text" placeholder="Y Axis Title" id="${modalDataConfig.id12}" size="7" value="${modalDataConfig.y_axis_title}">
        <br><br>
        <label style="font-size:1.1rem">Change the label of an element:</label><br>
        <input type="text" placeholder="Y Axis Label" id="${modalDataConfig.id13}" size="9" value="${modalDataConfig.element_label}"> &nbsp;&nbsp;<br><br>
        <label style="font-size:1.1rem">Chart interaction:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" checked="checked" name="defaultValueConfig" id="${modalDataConfig.id21}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id21}" class="custom-control-label">
                      Cross-filter
                      </label>
                  </div>
        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id18}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" style="line-height: 1.1;">Reset Axis Labels</button><br><br>
                          <label style="font-size:1.1rem">Change Plot Labels:</label>
          <button type="button" class="btn btn-primary" id="${modalDataConfig.id_labels}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" value="${modalDataConfig.label_value}" style="line-height: 1.1;">${modalDataConfig.label_text}</button><br><br>
                          <label style="font-size:1.1rem">Label Placement:</label>
        <select class="select2" name="position_legends" id="${modalDataConfig.id_label_placement}" style="font-size:1.1rem">
        <option value="">-----</option>
        <option value="inside">Inside</option>
        <option value="outside">Outside</option>
        </select>
        <br><br>
        <label style="font-size:1.1rem">Box Shadow</label>
        <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the shadow color:</label>
        <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
        <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
        <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
        <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
        <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Thickness:</label>
        <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
        <label style="font-size:1.1rem">Box Border</label>
        <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the border color:</label>
        <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
        <label style="font-size:1.1rem">Set border thickness</label>
        <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
        <label style="font-size:1.1rem">Choose border style:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
        <option value="solid">Solid</option>
        <option value="dotted">Dotted</option>
        <option value="double">Double</option>
        <option value="dashed">Dashed</option>
        </select><br><br>
        <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}
        <br>${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        <br>
        <label style="font-size:1.1rem">Set order for Y Axis:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_axis_order}" style="font-size:1.1rem" onchange="changeOrder.call(this)" data-chart-id = "${modalDataConfig.id6}" datatype_dict = '${JSON.stringify(modalDataConfig.datatype_dict)}' mappingDict = '${JSON.stringify(modalDataConfig.mappingDict)}' order_type = 'Horizontal'>
        <option value="" selected>----------</option>
        <option value="asc">Ascending</option>
        <option value="desc">Descending</option>
        <option value="cust">Custom</option>
        </select>
        <br>
        <button class="btn btn-primary btn-xs rounded px-2" id="${modalDataConfig.idOrderModal}Button" data-modal_id="${modalDataConfig.idOrderModal}" data-chart-id = "${modalDataConfig.id6}" data-sorted-values = "" onclick="orderModal.call(this)" datatype_dict = '${JSON.stringify(modalDataConfig.datatype_dict)}' order_type = 'Horizontal' style="display:none; height : 30px;">Set preferred order
        </button>
        ${modalDataConfig.optionvaluesHTML}
        <br><br>
        <label style="font-size:1.1rem">Change labels color:</label>
        <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
        <br>
        <label style="font-size:1.1rem">Set labels font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>
        </div>
        </div>
        `)
    }else if(modalDataConfig.graph_subtype === 'Horizontal_Histogram'){

        return $(`

        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">


        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>

        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}">
        <div class="custom-control custom-checkbox">
          <input type="checkbox" checked="checked" name="defaultValueColorConfig" id="${modalDataConfig.id24}" class="checkboxinput custom-control-input">
          <label for="${modalDataConfig.id24}" class="custom-control-label">
          Gradient Color
          </label>
        </div>
        <br><label style="font-size:1.1rem">
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label></div><br><br><label style="font-size:1.1rem"> <label style="font-size:1.1rem">Change X and Y axis gridlines:</label>

        <button type="button" class="btn btn-primary" id="${modalDataConfig.id9}" data-toggle="button" role="tab"
                        aria-pressed="false" autocomplete="off" value="${modalDataConfig.grid_id}" style="line-height: 0.7;">${modalDataConfig.value}</button><br><br>
                        <label style="font-size:1.1rem">Change the range of the axis:</label>
        <input type="text" placeholder="Y Axis Start" id="${modalDataConfig.id2}" size="7" value="${modalDataConfig.y_axis_start}">
        <input type="text" placeholder="Y Axis End " id="${modalDataConfig.id3}" size="7" value="${modalDataConfig.y_axis_end}">
        <br><br>
        <label style="font-size:1.1rem">Change the title of the axes:</label>
        <input type="text" placeholder="X Axis Title" id="${modalDataConfig.id11}" size="7" value="${modalDataConfig.x_axis_title}">

        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        <br><br>
        <label style="font-size:1.1rem">Box Shadow</label>
        <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the shadow color:</label>
        <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
        <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
        <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
        <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
        <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Thickness:</label>
        <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
        <label style="font-size:1.1rem">Box Border</label>
        <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the border color:</label>
        <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
        <label style="font-size:1.1rem">Set border thickness</label>
        <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
        <label style="font-size:1.1rem">Choose border style:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
        <option value="solid">Solid</option>
        <option value="dotted">Dotted</option>
        <option value="double">Double</option>
        <option value="dashed">Dashed</option>
        </select><br><br>
        <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}
        <br>${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        <br><br>
        <label style="font-size:1.1rem">Change labels color:</label>
        <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
        <br>
        <label style="font-size:1.1rem">Set labels font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>
        </div>
        </div>
        `)
    }else if(modalDataConfig.graph_subtype === 'Funnel'){
        return $(`

        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">


        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>

        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br>
        <div class="custom-control custom-checkbox">
          <input type="checkbox" checked="checked" name="defaultValueColorConfig" id="${modalDataConfig.id24}" class="checkboxinput custom-control-input">
          <label for="${modalDataConfig.id24}" class="custom-control-label">
          Gradient Color
          </label>
        </div>
        <br><br><label style="font-size:1.1rem">Change the color or an element:</label>
        <input type="color" id="${modalDataConfig.id4}" name="favcolor1" value="${modalDataConfig.element_color}">
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label></div>

        <br><br>
        <label style="font-size:1.1rem">Change the title of the axes:</label>
        <input type="text" placeholder="Y Axis Title" id="${modalDataConfig.id12}" size="7" value="${modalDataConfig.y_axis_title}">
        <br><br>
        <label style="font-size:1.1rem">Change the label of an element:</label><br>
        <input type="text" placeholder="Y Axis Label" id="${modalDataConfig.id13}" size="9" value="${modalDataConfig.element_label}"> &nbsp;&nbsp;<br><br>
        <label style="font-size:1.1rem">Chart interaction:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" checked="checked" name="defaultValueConfig" id="${modalDataConfig.id21}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id21}" class="custom-control-label">
                      Cross-filter
                      </label>
                  </div>
        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id18}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" style="line-height: 1.1;">Reset Axis Labels</button>
                          <br><br>
                          <label style="font-size:1.1rem">Box Shadow</label>
                          <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the shadow color:</label>
                          <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
                          <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
                          <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
                          <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Thickness:</label>
                          <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Box Border</label>
                          <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the border color:</label>
                          <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
                          <label style="font-size:1.1rem">Set border thickness</label>
                          <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
                          <label style="font-size:1.1rem">Choose border style:</label>
                          <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
                          <option value="solid">Solid</option>
                          <option value="dotted">Dotted</option>
                          <option value="double">Double</option>
                          <option value="dashed">Dashed</option>
                          </select><br><br>
                          <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}
        <br>${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        ${modalDataConfig.optionvaluesHTML}\
        <br><br>
        <label style="font-size:1.1rem">Change labels color:</label>
        <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
        <br>
        <label style="font-size:1.1rem">Set labels font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>
        </div>
        </div>
        `)
    }else if(modalDataConfig.graph_subtype === 'Funnel_Stacked'){
        return $(`

        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">


        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>
        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br>

        <br><label style="font-size:1.1rem">Change the color or an element:</label>
        <input type="color" id="${modalDataConfig.id4}" name="favcolor1" value="${modalDataConfig.element_color}">
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label></div>
        <br><br>
        <label style="font-size:1.1rem">Change the title of the axes:</label>
        <input type="text" placeholder="Y Axis Title" id="${modalDataConfig.id12}" size="7" value="${modalDataConfig.y_axis_title}">
        <br><br>
        <label style="font-size:1.1rem">Change the label of an element:</label><br>
        <input type="text" placeholder="Y Axis Label" id="${modalDataConfig.id13}" size="9" value="${modalDataConfig.element_label}"> &nbsp;&nbsp;<br><br>
        <label style="font-size:1.1rem">Chart interaction:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" checked="checked" name="defaultValueConfig" id="${modalDataConfig.id21}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id21}" class="custom-control-label">
                      Cross-filter
                      </label>
                  </div>
        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id18}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" style="line-height: 1.1;">Reset Axis Labels</button>
                          <br><br>
                          <label style="font-size:1.1rem">Box Shadow</label>
                          <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the shadow color:</label>
                          <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
                          <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
                          <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
                          <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Thickness:</label>
                          <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Box Border</label>
                          <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the border color:</label>
                          <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
                          <label style="font-size:1.1rem">Set border thickness</label>
                          <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
                          <label style="font-size:1.1rem">Choose border style:</label>
                          <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
                          <option value="solid">Solid</option>
                          <option value="dotted">Dotted</option>
                          <option value="double">Double</option>
                          <option value="dashed">Dashed</option>
                          </select><br><br>
                          <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}
        <br>${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        ${modalDataConfig.optionvaluesHTML}
        <br><br>
        <label style="font-size:1.1rem">Change labels color:</label>
        <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
        <br>
        <label style="font-size:1.1rem">Set labels font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>
        </div>
        </div>
        `)

    }else if(modalDataConfig.graph_subtype === 'Funnel_Area'){
        return $(`

        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">


        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>

        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br><label style="font-size:1.1rem">Change the color or an element:</label>
        <input type="color" id="${modalDataConfig.id4}" name="favcolor1" value="${modalDataConfig.element_color}">
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label></div>

        <label style="font-size:1.1rem">Connected slicers:</label>
        <br><br>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        <br><br>
        <label style="font-size:1.1rem">Box Shadow</label>
        <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the shadow color:</label>
        <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
        <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
        <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
        <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
        <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Thickness:</label>
        <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
        <label style="font-size:1.1rem">Box Border</label>
        <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the border color:</label>
        <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
        <label style="font-size:1.1rem">Set border thickness</label>
        <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
        <label style="font-size:1.1rem">Choose border style:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
        <option value="solid">Solid</option>
        <option value="dotted">Dotted</option>
        <option value="double">Double</option>
        <option value="dashed">Dashed</option>
        </select><br><br>
        <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}
        <br>${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        ${modalDataConfig.optionvaluesHTML}
        </div>
        </div>
        `)
    }else if(modalDataConfig.graph_subtype === 'Horizontal_Area_Stacked'){
        return $(`

        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">


        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>

        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br><label style="font-size:1.1rem">Change the color or an element:</label>
        <input type="color" id="${modalDataConfig.id4}" name="favcolor1" value="${modalDataConfig.element_color}"><br><br>
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label></div><br><br>

        <label style="font-size:1.1rem">Change X and Y axis gridlines:</label>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id9}" data-toggle="button" role="tab"
                        aria-pressed="false" autocomplete="off" value="${modalDataConfig.grid_id}" style="line-height: 0.7;">${modalDataConfig.value}</button><br><br>
                        <label style="font-size:1.1rem">Change the range of the axis:</label>
        <input type="text" placeholder="Y Axis Start" id="${modalDataConfig.id2}" size="7" value="${modalDataConfig.y_axis_start}">
        <input type="text" placeholder="Y Axis End " id="${modalDataConfig.id3}" size="7" value="${modalDataConfig.y_axis_end}">
        <br><br>
        <label style="font-size:1.1rem">Change the title of the axes:</label>
        <input type="text" placeholder="Y Axis Title" id="${modalDataConfig.id12}" size="7" value="${modalDataConfig.y_axis_title}">
        <br><br>
        <label style="font-size:1.1rem">Change the legend labels:</label>
        <input type="text" placeholder=${modalDataConfig.mappingDict[modalDataConfig.x_axis]} id="${modalDataConfig.id14}" size="7" value="${modalDataConfig.legend_x}">
        <input type="text" placeholder=${modalDataConfig.mappingDict[modalDataConfig.second_column]} id="${modalDataConfig.id15}" size="7" value="${modalDataConfig.legend_y}">
        <br><br>
        <label style="font-size:1.1rem">Change the label of an element:</label><br>
        <input type="text" placeholder="Y Axis Label" id="${modalDataConfig.id13}" size="9" value="${modalDataConfig.element_label}"> &nbsp;&nbsp;<br><br>
        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id18}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" style="line-height: 1.1;">Reset Axis Labels</button><br><br>
                          <label style="font-size:1.1rem">Change Plot Labels:</label>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id_labels}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" value="${modalDataConfig.label_value}" style="line-height: 1.1;">${modalDataConfig.label_text}</button>
                          <br><br>
                          <label style="font-size:1.1rem">Box Shadow</label>
                          <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the shadow color:</label>
                          <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
                          <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
                          <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
                          <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Thickness:</label>
                          <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Box Border</label>
                          <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the border color:</label>
                          <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
                          <label style="font-size:1.1rem">Set border thickness</label>
                          <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
                          <label style="font-size:1.1rem">Choose border style:</label>
                          <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
                          <option value="solid">Solid</option>
                          <option value="dotted">Dotted</option>
                          <option value="double">Double</option>
                          <option value="dashed">Dashed</option>
                          </select><br><br>
                          <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}
        <br>${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        <br>
        <label style="font-size:1.1rem">Set order for Y Axis:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_axis_order}" style="font-size:1.1rem" onchange="changeOrder.call(this)" data-chart-id = "${modalDataConfig.id6}" datatype_dict = '${JSON.stringify(modalDataConfig.datatype_dict)}' mappingDict = '${JSON.stringify(modalDataConfig.mappingDict)}' order_type = 'Horizontal'>
        <option value="" selected>----------</option>
        <option value="asc">Ascending</option>
        <option value="desc">Descending</option>
        <option value="cust">Custom</option>
        </select>
        <br>
        <button class="btn btn-primary btn-xs rounded px-2" id="${modalDataConfig.idOrderModal}Button" data-modal_id="${modalDataConfig.idOrderModal}" data-chart-id = "${modalDataConfig.id6}" data-sorted-values = "" onclick="orderModal.call(this)" datatype_dict = '${JSON.stringify(modalDataConfig.datatype_dict)}' order_type = 'Horizontal' style="display:none; height : 30px;">Set preferred order
        </button>
        ${modalDataConfig.optionvaluesHTML}
        <br><br>
        <label style="font-size:1.1rem">Change labels color:</label>
        <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
        <br>
        <label style="font-size:1.1rem">Set labels font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>
        </div>
        </div>
        `)
    }else if(modalDataConfig.graph_subtype === 'Horizontal_Bar_Stacked'){
        return $(`

        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">


        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>

        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br><label style="font-size:1.1rem">Change the color or an element:</label>
        <input type="color" id="${modalDataConfig.id4}" name="favcolor1" value="${modalDataConfig.element_color}"><br><br>
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label></div><br><br>
        <label style="font-size:1.1rem">Change X and Y axis gridlines:</label>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id9}" data-toggle="button" role="tab"
                        aria-pressed="false" autocomplete="off" value="${modalDataConfig.grid_id}" style="line-height: 0.7;">${modalDataConfig.value}</button><br><br>
                        <label style="font-size:1.1rem">Change the range of the axis:</label>
        <input type="text" placeholder="Y Axis Start" id="${modalDataConfig.id2}" size="7" value="${modalDataConfig.y_axis_start}">
        <input type="text" placeholder="Y Axis End " id="${modalDataConfig.id3}" size="7" value="${modalDataConfig.y_axis_end}">
        <br><br>
        <label style="font-size:1.1rem">Change the title of the axes:</label>
        <input type="text" placeholder="Y Axis Title" id="${modalDataConfig.id12}" size="7" value="${modalDataConfig.y_axis_title}">
        <br><br>
        <label style="font-size:1.1rem">Change the legend labels:</label>
        <input type="text" placeholder=${modalDataConfig.mappingDict[modalDataConfig.x_axis]} id="${modalDataConfig.id14}" size="7" value="${modalDataConfig.legend_x}">
        <input type="text" placeholder=${modalDataConfig.mappingDict[modalDataConfig.second_column]} id="${modalDataConfig.id15}" size="7" value="${modalDataConfig.legend_y}">
        <br><br>
        <label style="font-size:1.1rem">Change the label of an element:</label><br>
        <input type="text" placeholder="Y Axis Label" id="${modalDataConfig.id13}" size="9" value="${modalDataConfig.element_label}"> &nbsp;&nbsp;<br><br>
        <label style="font-size:1.1rem">Chart interaction:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" checked="checked" name="defaultValueConfig" id="${modalDataConfig.id21}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id21}" class="custom-control-label">
                      Cross-filter
                      </label>
                  </div>
        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id18}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" style="line-height: 1.1;">Reset Axis Labels</button><br><br>
                          <label style="font-size:1.1rem">Change Plot Labels:</label>
          <button type="button" class="btn btn-primary" id="${modalDataConfig.id_labels}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" value="${modalDataConfig.label_value}" style="line-height: 1.1;">${modalDataConfig.label_text}</button>
                          <br><br>
                          <label style="font-size:1.1rem">Box Shadow</label>
                          <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the shadow color:</label>
                          <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
                          <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
                          <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
                          <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Thickness:</label>
                          <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Box Border</label>
                          <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the border color:</label>
                          <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
                          <label style="font-size:1.1rem">Set border thickness</label>
                          <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
                          <label style="font-size:1.1rem">Choose border style:</label>
                          <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
                          <option value="solid">Solid</option>
                          <option value="dotted">Dotted</option>
                          <option value="double">Double</option>
                          <option value="dashed">Dashed</option>
                          </select><br><br>
                          <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}
        <br>${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        <br>
        <label style="font-size:1.1rem">Set order for Y Axis:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_axis_order}" style="font-size:1.1rem" onchange="changeOrder.call(this)" data-chart-id = "${modalDataConfig.id6}" datatype_dict = '${JSON.stringify(modalDataConfig.datatype_dict)}' mappingDict = '${JSON.stringify(modalDataConfig.mappingDict)}' order_type = 'Horizontal'>
        <option value="" selected>----------</option>
        <option value="asc">Ascending</option>
        <option value="desc">Descending</option>
        <option value="cust">Custom</option>
        </select>
        <br>
        <button class="btn btn-primary btn-xs rounded px-2" id="${modalDataConfig.idOrderModal}Button" data-modal_id="${modalDataConfig.idOrderModal}" data-chart-id = "${modalDataConfig.id6}" data-sorted-values = "" onclick="orderModal.call(this)" datatype_dict = '${JSON.stringify(modalDataConfig.datatype_dict)}' order_type = 'Horizontal' style="display:none; height : 30px;">Set preferred order
        </button>
        ${modalDataConfig.optionvaluesHTML}
        <br><br>
        <label style="font-size:1.1rem">Change labels color:</label>
        <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
        <br>
        <label style="font-size:1.1rem">Set labels font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>
        </div>
        </div>
        `)
    }else if(modalDataConfig.graph_subtype === 'Horizontal_Grouped_Box'){
        return $(`
        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">


        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>

        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br><label style="font-size:1.1rem">Change the color or an element:</label>
        <input type="color" id="${modalDataConfig.id4}" name="favcolor1" value="${modalDataConfig.element_color}"><br><br>
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label></div><br><br>

        <label style="font-size:1.1rem">Change X and Y axis gridlines:</label>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id9}" data-toggle="button" role="tab"
                        aria-pressed="false" autocomplete="off" value="${modalDataConfig.grid_id}" style="line-height: 0.7;">${modalDataConfig.value}</button><br><br>
                        <label style="font-size:1.1rem">Change the range of the axis:</label>
        <input type="text" placeholder="Y Axis Start" id="${modalDataConfig.id2}" size="7" value="${modalDataConfig.y_axis_start}">
        <input type="text" placeholder="Y Axis End " id="${modalDataConfig.id3}" size="7" value="${modalDataConfig.y_axis_end}">
        <br><br>
        <label style="font-size:1.1rem">Change the title of the axes:</label>
        <input type="text" placeholder="Y Axis Title" id="${modalDataConfig.id12}" size="7" value="${modalDataConfig.y_axis_title}">
        <br><br>
        <label style="font-size:1.1rem">Change the legend labels:</label>
        <input type="text" placeholder=${modalDataConfig.mappingDict[modalDataConfig.x_axis]} id="${modalDataConfig.id14}" size="7" value="${modalDataConfig.legend_x}">
        <input type="text" placeholder=${modalDataConfig.mappingDict[modalDataConfig.second_column]} id="${modalDataConfig.id15}" size="7" value="${modalDataConfig.legend_y}">
        <br><br>
        <label style="font-size:1.1rem">Change the label of an element:</label><br>
        <input type="text" placeholder="Y Axis Label" id="${modalDataConfig.id13}" size="9" value="${modalDataConfig.element_label}"> &nbsp;&nbsp;<br><br>
        <label style="font-size:1.1rem">Chart interaction:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" checked="checked" name="defaultValueConfig" id="${modalDataConfig.id21}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id21}" class="custom-control-label">
                      Cross-filter
                      </label>
                  </div>
        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id18}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" style="line-height: 1.1;">Reset Axis Labels</button>
                          <br><br>
                          <label style="font-size:1.1rem">Box Shadow</label>
                          <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the shadow color:</label>
                          <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
                          <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
                          <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
                          <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Thickness:</label>
                          <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Box Border</label>
                          <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the border color:</label>
                          <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
                          <label style="font-size:1.1rem">Set border thickness</label>
                          <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
                          <label style="font-size:1.1rem">Choose border style:</label>
                          <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
                          <option value="solid">Solid</option>
                          <option value="dotted">Dotted</option>
                          <option value="double">Double</option>
                          <option value="dashed">Dashed</option>
                          </select><br><br>
                          <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}
        <br>${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        <br><br>
        <label style="font-size:1.1rem">Change labels color:</label>
        <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
        <br>
        <label style="font-size:1.1rem">Set labels font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>
        </div>
        </div>
        `)
    }else if(modalDataConfig.graph_subtype === 'Horizontal_Grouped_Violin'){
        return $(`

        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">


        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>

        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br><label style="font-size:1.1rem">Change the color or an element:</label>
        <input type="color" id="${modalDataConfig.id4}" name="favcolor1" value="${modalDataConfig.element_color}"><br><br>
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label>
                  </div><br><br>

        <label style="font-size:1.1rem">Change X and Y axis gridlines:</label>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id9}" data-toggle="button" role="tab"
                        aria-pressed="false" autocomplete="off" value="${modalDataConfig.grid_id}" style="line-height: 0.7;">${modalDataConfig.value}</button><br><br>
                        <label style="font-size:1.1rem">Change the range of the axis:</label>
        <input type="text" placeholder="Y Axis Start" id="${modalDataConfig.id2}" size="7" value="${modalDataConfig.y_axis_start}">
        <input type="text" placeholder="Y Axis End " id="${modalDataConfig.id3}" size="7" value="${modalDataConfig.y_axis_end}">
        <br><br>
        <label style="font-size:1.1rem">Change the title of the axes:</label>
        <input type="text" placeholder="Y Axis Title" id="${modalDataConfig.id12}" size="7" value="${modalDataConfig.y_axis_title}">
        <br><br>
        <label style="font-size:1.1rem">Change the legend labels:</label>
        <input type="text" placeholder=${modalDataConfig.mappingDict[modalDataConfig.x_axis]} id="${modalDataConfig.id14}" size="7" value="${modalDataConfig.legend_x}">
        <input type="text" placeholder=${modalDataConfig.mappingDict[modalDataConfig.second_column]} id="${modalDataConfig.id15}" size="7" value="${modalDataConfig.legend_y}">
        <br><br>
        <label style="font-size:1.1rem">Change the label of an element:</label><br>
        <input type="text" placeholder="Y Axis Label" id="${modalDataConfig.id13}" size="9" value="${modalDataConfig.element_label}"> &nbsp;&nbsp;<br><br>
        <label style="font-size:1.1rem">Chart interaction:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" checked="checked" name="defaultValueConfig" id="${modalDataConfig.id21}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id21}" class="custom-control-label">
                      Cross-filter
                      </label>
                  </div>
        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id18}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" style="line-height: 1.1;">Reset Axis Labels</button>
                          <br><br>
                          <label style="font-size:1.1rem">Box Shadow</label>
                          <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the shadow color:</label>
                          <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
                          <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
                          <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
                          <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Thickness:</label>
                          <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Box Border</label>
                          <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the border color:</label>
                          <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
                          <label style="font-size:1.1rem">Set border thickness</label>
                          <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
                          <label style="font-size:1.1rem">Choose border style:</label>
                          <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
                          <option value="solid">Solid</option>
                          <option value="dotted">Dotted</option>
                          <option value="double">Double</option>
                          <option value="dashed">Dashed</option>
                          </select><br><br>
                          <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}
        <br>${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        <br><br>
        <label style="font-size:1.1rem">Change labels color:</label>
        <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
        <br>
        <label style="font-size:1.1rem">Set labels font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>
        </div>
        </div>
        `)
    }else if(modalDataConfig.graph_subtype === 'Horizontal_Waterfall_Grouped'){
        return $(`

        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">


        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>

                  <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br>
                  <br>
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label></div>
        <label style="font-size:1.1rem">Change X and Y axis gridlines:</label>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id9}" data-toggle="button" role="tab"
                        aria-pressed="false" autocomplete="off" value="${modalDataConfig.grid_id}" style="line-height: 0.7;">${modalDataConfig.value}</button><br><br>
                        <label style="font-size:1.1rem">Change the range of the axis:</label>
        <input type="text" placeholder="Y Axis Start" id="${modalDataConfig.id2}" size="7" value="${modalDataConfig.y_axis_start}">
        <input type="text" placeholder="Y Axis End " id="${modalDataConfig.id3}" size="7" value="${modalDataConfig.y_axis_end}">
        <br><br>
        <label style="font-size:1.1rem">Change the title of the axes:</label>
        <input type="text" placeholder="Y Axis Title" id="${modalDataConfig.id12}" size="7" value="${modalDataConfig.y_axis_title}">
        <br><br>
        <label style="font-size:1.1rem">Change the legend labels:</label>
        <input type="text" placeholder=${modalDataConfig.mappingDict[modalDataConfig.x_axis]} id="${modalDataConfig.id14}" size="7" value="${modalDataConfig.legend_x}">
        <input type="text" placeholder=${modalDataConfig.mappingDict[modalDataConfig.second_column]} id="${modalDataConfig.id15}" size="7" value="${modalDataConfig.legend_y}">
        <br><br>
        <label style="font-size:1.1rem">Change the label of an element:</label><br>
        <input type="text" placeholder="Y Axis Label" id="${modalDataConfig.id13}" size="9" value="${modalDataConfig.element_label}"> &nbsp;&nbsp;<br><br>
        <label style="font-size:1.1rem">Chart interaction:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" checked="checked" name="defaultValueConfig" id="${modalDataConfig.id21}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id21}" class="custom-control-label">
                      Cross-filter
                      </label>
                  </div>
        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id18}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" style="line-height: 1.1;">Reset Axis Labels</button><br><br>
                          <label style="font-size:1.1rem">Change Plot Labels:</label>
          <button type="button" class="btn btn-primary" id="${modalDataConfig.id_labels}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" value="${modalDataConfig.label_value}" style="line-height: 1.1;">${modalDataConfig.label_text}</button>
                          <br><br>
                          <label style="font-size:1.1rem">Box Shadow</label>
                          <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the shadow color:</label>
                          <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
                          <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
                          <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
                          <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Thickness:</label>
                          <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Box Border</label>
                          <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the border color:</label>
                          <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
                          <label style="font-size:1.1rem">Set border thickness</label>
                          <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
                          <label style="font-size:1.1rem">Choose border style:</label>
                          <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
                          <option value="solid">Solid</option>
                          <option value="dotted">Dotted</option>
                          <option value="double">Double</option>
                          <option value="dashed">Dashed</option>
                          </select><br><br>
                          <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}
        <br>${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        ${modalDataConfig.optionvaluesHTML}
        <br><br>
        <label style="font-size:1.1rem">Change labels color:</label>
        <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
        <br>
        <label style="font-size:1.1rem">Set labels font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>
        </div>
        </div>
        `)
    }else if(modalDataConfig.graph_subtype === 'Horizontal_Bar_Grouped'){
        return $(`
        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">
        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>
        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br>
        <label style="font-size:1.1rem">Change the color or an element:</label>

        <input type="color" id="${modalDataConfig.id4}" name="favcolor1" value="${modalDataConfig.element_color}"><br><br>
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label></div>
                      <br><br>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id9}" data-toggle="button" role="tab"
                        aria-pressed="false" autocomplete="off" value="${modalDataConfig.grid_id}" style="line-height: 0.7;">${modalDataConfig.value}</button><br><br>
                        <label style="font-size:1.1rem">Change the range of the axis:</label>
        <input type="text" placeholder="Y Axis Start" id="${modalDataConfig.id2}" size="7" value="${modalDataConfig.y_axis_start}">
        <input type="text" placeholder="Y Axis End " id="${modalDataConfig.id3}" size="7" value="${modalDataConfig.y_axis_end}">
        <br><br>
        <label style="font-size:1.1rem">Change the title of the axes:</label>
        <input type="text" placeholder="Y Axis Title" id="${modalDataConfig.id12}" size="7" value="${modalDataConfig.y_axis_title}">
        <br><br>
        <label style="font-size:1.1rem">Change the legend labels:</label>
        <input type="text" placeholder=${modalDataConfig.mappingDict[modalDataConfig.x_axis]} id="${modalDataConfig.id14}" size="7" value="${modalDataConfig.legend_x}">
        <input type="text" placeholder=${modalDataConfig.mappingDict[modalDataConfig.second_column]} id="${modalDataConfig.id15}" size="7" value="${modalDataConfig.legend_y}">
        <br><br>
        <label style="font-size:1.1rem">Change the label of an element:</label><br>
        <input type="text" placeholder="Y Axis Label" id="${modalDataConfig.id13}" size="9" value="${modalDataConfig.element_label}"> &nbsp;&nbsp;<br><br>
        <label style="font-size:1.1rem">Chart interaction:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" checked="checked" name="defaultValueConfig" id="${modalDataConfig.id21}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id21}" class="custom-control-label">
                      Cross-filter
                      </label>
                  </div>
        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id18}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" style="line-height: 1.1;">Reset Axis Labels</button><br><br>
                          <label style="font-size:1.1rem">Change Plot Labels:</label>
          <button type="button" class="btn btn-primary" id="${modalDataConfig.id_labels}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" value="${modalDataConfig.label_value}" style="line-height: 1.1;">${modalDataConfig.label_text}</button>
                          <br><br>
                          <label style="font-size:1.1rem">Box Shadow</label>
                          <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the shadow color:</label>
                          <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
                          <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
                          <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
                          <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Thickness:</label>
                          <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Box Border</label>
                          <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the border color:</label>
                          <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
                          <label style="font-size:1.1rem">Set border thickness</label>
                          <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
                          <label style="font-size:1.1rem">Choose border style:</label>
                          <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
                          <option value="solid">Solid</option>
                          <option value="dotted">Dotted</option>
                          <option value="double">Double</option>
                          <option value="dashed">Dashed</option>
                          </select><br><br>
                          <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}
        <br>${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        <br>
        <label style="font-size:1.1rem">Set order for Y Axis:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_axis_order}" style="font-size:1.1rem" onchange="changeOrder.call(this)" data-chart-id = "${modalDataConfig.id6}" datatype_dict = '${JSON.stringify(modalDataConfig.datatype_dict)}' mappingDict = '${JSON.stringify(modalDataConfig.mappingDict)}' order_type = 'Horizontal'>
        <option value="" selected>----------</option>
        <option value="asc">Ascending</option>
        <option value="desc">Descending</option>
        <option value="cust">Custom</option>
        </select>
        <br>
        <button class="btn btn-primary btn-xs rounded px-2" id="${modalDataConfig.idOrderModal}Button" data-modal_id="${modalDataConfig.idOrderModal}" data-chart-id = "${modalDataConfig.id6}" data-sorted-values = "" onclick="orderModal.call(this)" datatype_dict = '${JSON.stringify(modalDataConfig.datatype_dict)}' order_type = 'Horizontal' style="display:none ; height : 30px;">Set preferred order
        </button>
        ${modalDataConfig.optionvaluesHTML}
        <br><br>
        <label style="font-size:1.1rem">Change labels color:</label>
        <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
        <br>
        <label style="font-size:1.1rem">Set labels font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>
        </div>
        </div>
        `)
    }else if(modalDataConfig.graph_subtype === 'Vertical_Bar_Grouped'){
        return $(`

        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">


        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>
        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br>
        <label style="font-size:1.1rem">Change the color or an element:</label>

        <input type="color" id="${modalDataConfig.id4}" name="favcolor1" value="${modalDataConfig.element_color}"><br><br>
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label></div><br><br><label style="font-size:1.1rem">Change X and Y axis gridlines:</label>

        <button type="button" class="btn btn-primary" id="${modalDataConfig.id9}" data-toggle="button" role="tab"
                        aria-pressed="false" autocomplete="off" value="${modalDataConfig.grid_id}" style="line-height: 0.7;">${modalDataConfig.value}</button><br><br>
                        <label style="font-size:1.1rem">Change the range of the axis:</label>
        <input type="text" placeholder="Y Axis Start" id="${modalDataConfig.id2}" size="7" value="${modalDataConfig.y_axis_start}">
        <input type="text" placeholder="Y Axis End " id="${modalDataConfig.id3}" size="7" value="${modalDataConfig.y_axis_end}">
        <br><br>
        <label style="font-size:1.1rem">Change the title of the axes:</label>
        <input type="text" placeholder="X Axis Title" id="${modalDataConfig.id11}" size="7" value="${modalDataConfig.x_axis_title}">
        <br><br>
        <label style="font-size:1.1rem">Change the legend labels:</label>
        <input type="text" placeholder=${modalDataConfig.mappingDict[modalDataConfig.y_axis]} id="${modalDataConfig.id14}" size="7" value="${modalDataConfig.legend_x}">
        <input type="text" placeholder=${modalDataConfig.mappingDict[modalDataConfig.second_column]} id="${modalDataConfig.id15}" size="7" value="${modalDataConfig.legend_y}">
        <br><br>
        <label style="font-size:1.1rem">Change the label of an element:</label><br>
        <input type="text" placeholder="X Axis Label" id="${modalDataConfig.id13}" size="9" value="${modalDataConfig.element_label}"> &nbsp;&nbsp;
        <label style="font-size:1.1rem">Chart interaction:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" checked="checked" name="defaultValueConfig" id="${modalDataConfig.id21}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id21}" class="custom-control-label">
                      Cross-filter
                      </label>
                  </div>
        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id18}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" style="line-height: 1.1;">Reset Axis Labels</button><br><br>
                          <label style="font-size:1.1rem">Change Plot Labels:</label>
          <button type="button" class="btn btn-primary" id="${modalDataConfig.id_labels}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" value="${modalDataConfig.label_value}" style="line-height: 1.1;">${modalDataConfig.label_text}</button>
                          <br><br>
                          <label style="font-size:1.1rem">Box Shadow</label>
                          <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the shadow color:</label>
                          <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
                          <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
                          <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
                          <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Thickness:</label>
                          <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Box Border</label>
                          <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the border color:</label>
                          <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
                          <label style="font-size:1.1rem">Set border thickness</label>
                          <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
                          <label style="font-size:1.1rem">Choose border style:</label>
                          <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
                          <option value="solid">Solid</option>
                          <option value="dotted">Dotted</option>
                          <option value="double">Double</option>
                          <option value="dashed">Dashed</option>
                          </select><br><br>
                          <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}
        <br>${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        <br>
        <label style="font-size:1.1rem">Set order for X Axis:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_axis_order}" style="font-size:1.1rem" onchange="changeOrder.call(this)" data-chart-id = "${modalDataConfig.id6}" datatype_dict = '${JSON.stringify(modalDataConfig.datatype_dict)}' mappingDict = '${JSON.stringify(modalDataConfig.mappingDict)}' order_type = 'Vertical'>
        <option value="" selected>----------</option>
        <option value="asc">Ascending</option>
        <option value="desc">Descending</option>
        <option value="cust">Custom</option>
        </select>
        <br>
        <button class="btn btn-primary btn-xs rounded px-2" id="${modalDataConfig.idOrderModal}Button" data-modal_id="${modalDataConfig.idOrderModal}" data-chart-id = "${modalDataConfig.id6}" data-sorted-values = "" onclick="orderModal.call(this)" datatype_dict = '${JSON.stringify(modalDataConfig.datatype_dict)}' order_type = 'Vertical' style="display:none; height : 30px;">Set preferred order
        </button>
        ${modalDataConfig.optionvaluesHTML}
        <br><br>
        <label style="font-size:1.1rem">Change labels color:</label>
        <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
        <br>
        <label style="font-size:1.1rem">Set labels font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>
        </div>
        </div>
        `)
    }else if(modalDataConfig.graph_subtype === 'Bar_Grouped_and_Line' || modalDataConfig.graph_subtype  === 'Bar_Stacked_and_Line'){
        return $(`

        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">


        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>
        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br>
        <label style="font-size:1.1rem">Change the color or an element:</label>

        <input type="color" id="${modalDataConfig.id4}" name="favcolor1" value="${modalDataConfig.element_color}"><br><br>
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label></div>
                      <br><br><label style="font-size:1.1rem">Change X and Y axis gridlines:</label>

        <button type="button" class="btn btn-primary" id="${modalDataConfig.id9}" data-toggle="button" role="tab"
                        aria-pressed="false" autocomplete="off" value="${modalDataConfig.grid_id}" style="line-height: 0.7;">${modalDataConfig.value}</button><br><br>
                        <label style="font-size:1.1rem">Change the range of the axis:</label>
        <input type="text" placeholder="Y Axis Start" id="${modalDataConfig.id2}" size="7" value="${modalDataConfig.y_axis_start}">
        <input type="text" placeholder="Y Axis End " id="${modalDataConfig.id3}" size="7" value="${modalDataConfig.y_axis_end}">
        <br><br>
        <label style="font-size:1.1rem">Change the title of the axes:</label>
        <input type="text" placeholder="X Axis Title" id="${modalDataConfig.id11}" size="7" value="${modalDataConfig.x_axis_title}">
        <br><br>
        <label style="font-size:1.1rem">Change the legend labels:</label>
        <input type="text" placeholder=${modalDataConfig.mappingDict[modalDataConfig.y_axis]} id="${modalDataConfig.id14}" size="7" value="${modalDataConfig.legend_x}">
        <input type="text" placeholder=${modalDataConfig.mappingDict[modalDataConfig.second_column]} id="${modalDataConfig.id15}" size="7" value="${modalDataConfig.legend_y}">
        <br><br>
        <label style="font-size:1.1rem">Change the label of an element:</label><br>
        <input type="text" placeholder="X Axis Label" id="${modalDataConfig.id13}" size="9" value="${modalDataConfig.element_label}"> &nbsp;&nbsp;
        <label style="font-size:1.1rem">Chart interaction:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" checked="checked" name="defaultValueConfig" id="${modalDataConfig.id21}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id21}" class="custom-control-label">
                      Cross-filter
                      </label>
                  </div>
        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id18}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" style="line-height: 1.1;">Reset Axis Labels</button><br><br>
                          <label style="font-size:1.1rem">Change Plot Labels:</label>
          <button type="button" class="btn btn-primary" id="${modalDataConfig.id_labels}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" value="${modalDataConfig.label_value}" style="line-height: 1.1;">${modalDataConfig.label_text}</button>
                          <br><br>
                          <label style="font-size:1.1rem">Box Shadow</label>
                          <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the shadow color:</label>
                          <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
                          <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
                          <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
                          <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Thickness:</label>
                          <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Box Border</label>
                          <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the border color:</label>
                          <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
                          <label style="font-size:1.1rem">Set border thickness</label>
                          <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
                          <label style="font-size:1.1rem">Choose border style:</label>
                          <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
                          <option value="solid">Solid</option>
                          <option value="dotted">Dotted</option>
                          <option value="double">Double</option>
                          <option value="dashed">Dashed</option>
                          </select><br><br>
                          <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}
        <br>${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        <br>
        <label style="font-size:1.1rem">Set order for X Axis:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_axis_order}" style="font-size:1.1rem" onchange="changeOrder.call(this)" data-chart-id = "${modalDataConfig.id6}" datatype_dict = '${JSON.stringify(modalDataConfig.datatype_dict)}' mappingDict = '${JSON.stringify(modalDataConfig.mappingDict)}' order_type = 'Vertical' >
        <option value="" selected>----------</option>
        <option value="asc">Ascending</option>
        <option value="desc">Descending</option>
        <option value="cust">Custom</option>
        </select>
        <br>
        <button class="btn btn-primary btn-xs rounded px-2" id="${modalDataConfig.idOrderModal}Button" data-modal_id="${modalDataConfig.idOrderModal}" data-chart-id = "${modalDataConfig.id6}" data-sorted-values = "" onclick="orderModal.call(this)" datatype_dict = '${JSON.stringify(modalDataConfig.datatype_dict)}' order_type = 'Vertical' style="display:none; height : 30px;">Set preferred order
        </button>
        ${modalDataConfig.optionvaluesHTML}
        ${modalDataConfig.optionvalues_lineHTML}
        <br><br>
        <label style="font-size:1.1rem">Change labels color:</label>
        <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
        <br>
        <label style="font-size:1.1rem">Set labels font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>

        </div>
        </div>
        `)
    }else if(modalDataConfig.graph_subtype === 'Bar_Stacked_and_Multiple_Line'){
        return $(`

        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">


        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>
        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br>
        <label style="font-size:1.1rem">Change the color or an element:</label>

        <input type="color" id="${modalDataConfig.id4}" name="favcolor1" value="${modalDataConfig.element_color}"><br><br>
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label></div>
                      <br><br><label style="font-size:1.1rem">Change X and Y axis gridlines:</label>

        <button type="button" class="btn btn-primary" id="${modalDataConfig.id9}" data-toggle="button" role="tab"
                        aria-pressed="false" autocomplete="off" value="${modalDataConfig.grid_id}" style="line-height: 0.7;">${modalDataConfig.value}</button><br><br>
                        <label style="font-size:1.1rem">Change the range of the axis:</label>
        <input type="text" placeholder="Y Axis Start" id="${modalDataConfig.id2}" size="7" value="${modalDataConfig.y_axis_start}">
        <input type="text" placeholder="Y Axis End " id="${modalDataConfig.id3}" size="7" value="${modalDataConfig.y_axis_end}">
        <br><br>
        <label style="font-size:1.1rem">Change the title of the axes:</label>
        <input type="text" placeholder="X Axis Title" id="${modalDataConfig.id11}" size="7" value="${modalDataConfig.x_axis_title}">
        <br><br>
        <label style="font-size:1.1rem">Change the legend labels:</label>
        <input type="text" placeholder=${modalDataConfig.mappingDict[modalDataConfig.y_axis]} id="${modalDataConfig.id14}" size="7" value="${modalDataConfig.legend_x}">
        <input type="text" placeholder=${modalDataConfig.mappingDict[modalDataConfig.second_column]} id="${modalDataConfig.id15}" size="7" value="${modalDataConfig.legend_y}">
        <br><br>
        <label style="font-size:1.1rem">Change the label of an element:</label><br>
        <input type="text" placeholder="X Axis Label" id="${modalDataConfig.id13}" size="9" value="${modalDataConfig.element_label}"> &nbsp;&nbsp;
        <label style="font-size:1.1rem">Chart interaction:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" checked="checked" name="defaultValueConfig" id="${modalDataConfig.id21}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id21}" class="custom-control-label">
                      Cross-filter
                      </label>
                  </div>
        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id18}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" style="line-height: 1.1;">Reset Axis Labels</button><br><br>
                          <label style="font-size:1.1rem">Change Plot Labels:</label>
          <button type="button" class="btn btn-primary" id="${modalDataConfig.id_labels}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" value="${modalDataConfig.label_value}" style="line-height: 1.1;">${modalDataConfig.label_text}</button>
                          <br><br>
                          <label style="font-size:1.1rem">Label Placement:</label>
            <select class="select2" name="position_legends" id="${modalDataConfig.id_label_placement}" style="font-size:1.1rem">
            <option value="">-----</option>
            <option value="top">Top</option>
            <option value="bottom">Bottom</option>
            <option value="center">Center</option>
            </select>
            <br><br>
                          <label style="font-size:1.1rem">Box Shadow</label>
                          <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the shadow color:</label>
                          <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
                          <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
                          <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
                          <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Thickness:</label>
                          <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Box Border</label>
                          <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the border color:</label>
                          <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
                          <label style="font-size:1.1rem">Set border thickness</label>
                          <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
                          <label style="font-size:1.1rem">Choose border style:</label>
                          <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
                          <option value="solid">Solid</option>
                          <option value="dotted">Dotted</option>
                          <option value="double">Double</option>
                          <option value="dashed">Dashed</option>
                          </select><br><br>
                          <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}
        <br>${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        <br>
        <label style="font-size:1.1rem">Set order for X Axis:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_axis_order}" style="font-size:1.1rem" onchange="changeOrder.call(this)" data-chart-id = "${modalDataConfig.id6}" datatype_dict = '${JSON.stringify(modalDataConfig.datatype_dict)}' mappingDict = '${JSON.stringify(modalDataConfig.mappingDict)}' order_type = 'Vertical' >
        <option value="" selected>----------</option>
        <option value="asc">Ascending</option>
        <option value="desc">Descending</option>
        <option value="cust">Custom</option>
        </select>
        <br>
        <button class="btn btn-primary btn-xs rounded px-2" id="${modalDataConfig.idOrderModal}Button" data-modal_id="${modalDataConfig.idOrderModal}" data-chart-id = "${modalDataConfig.id6}" data-sorted-values = "" onclick="orderModal.call(this)" datatype_dict = '${JSON.stringify(modalDataConfig.datatype_dict)}' order_type = 'Vertical' style="display:none; height : 30px;">Set preferred order
        </button>
        ${modalDataConfig.optionvaluesHTML}
        ${modalDataConfig.optionvalues_lineHTML}
        <br><br>
        <label style="font-size:1.1rem">Change labels color:</label>
        <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
        <br>
        <label style="font-size:1.1rem">Set labels font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>
        </div>
        </div>
        `)
    }else if(modalDataConfig.graph_subtype === 'Stacked_Histogram'){
        return $(`
        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">

        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>
        <input type="color" id='${modalDataConfig.id1}' name="favcolor" value="${modalDataConfig.color}"><br><br>
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label></div>
                      <br><label style="font-size:1.1rem">Change X and Y axis gridlines:</label>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id9}" data-toggle="button" role="tab"
                        aria-pressed="false" autocomplete="off" value="${modalDataConfig.grid_id}" style="line-height: 0.7;">${modalDataConfig.value}</button><br><br>
                        <label style="font-size:1.1rem">Change the range of the axis:</label>
        <input type="text" placeholder="Y Axis Start" id='${modalDataConfig.id2}' size="7" value="${modalDataConfig.y_axis_start}">
        <input type="text" placeholder="Y Axis End " id='${modalDataConfig.id3}' size="7" value="${modalDataConfig.y_axis_end}">
        <br><br>
        <label style="font-size:1.1rem">Change the title of the axes:</label>
        <input type="text" placeholder="X Axis Title" id='${modalDataConfig.id11}' size="7" value="${modalDataConfig.x_axis_title}">
        <br><br>
        <label style="font-size:1.1rem">Change the legend labels:</label>
        <input type="text" placeholder='${modalDataConfig.mappingDict[modalDataConfig.x_axis]}' id='${modalDataConfig.id14}' size="7" value="${modalDataConfig.legend_x}">
        <input type="text" placeholder='${modalDataConfig.mappingDict[modalDataConfig.y_axis]}' id='${modalDataConfig.id15}' size="7" value="${modalDataConfig.legend_y}">
        <br><br>
        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
                          <br><br>
                          <label style="font-size:1.1rem">Box Shadow</label>
                          <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the shadow color:</label>
                          <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
                          <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
                          <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
                          <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Thickness:</label>
                          <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Box Border</label>
                          <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the border color:</label>
                          <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
                          <label style="font-size:1.1rem">Set border thickness</label>
                          <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
                          <label style="font-size:1.1rem">Choose border style:</label>
                          <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
                          <option value="solid">Solid</option>
                          <option value="dotted">Dotted</option>
                          <option value="double">Double</option>
                          <option value="dashed">Dashed</option>
                          </select><br><br>
                          <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}
        <br>${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        <br><br>
        <label style="font-size:1.1rem">Change labels color:</label>
        <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
        <br>
        <label style="font-size:1.1rem">Set labels font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>
        </div>
        </div>
        `)
    }else if(modalDataConfig.graph_subtype === 'Vertical_Waterfall_Grouped'){
        return $(`
        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">


        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>

                  <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br>
                  <br>
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label></div>
        <label style="font-size:1.1rem">Change X and Y axis gridlines:</label>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id9}" data-toggle="button" role="tab"
                        aria-pressed="false" autocomplete="off" value="${modalDataConfig.grid_id}" style="line-height: 0.7;">${modalDataConfig.value}</button><br><br>
                        <label style="font-size:1.1rem">Change the range of the axis:</label>
        <input type="text" placeholder="Y Axis Start" id="${modalDataConfig.id2}" size="7" value="${modalDataConfig.y_axis_start}">
        <input type="text" placeholder="Y Axis End " id="${modalDataConfig.id3}" size="7" value="${modalDataConfig.y_axis_end}">
        <br><br>
        <label style="font-size:1.1rem">Change the title of the axes:</label>
        <input type="text" placeholder="X Axis Title" id="${modalDataConfig.id11}" size="7" value="${modalDataConfig.x_axis_title}">
        <br><br>
        <label style="font-size:1.1rem">Change the legend labels:</label>
        <input type="text" placeholder=${modalDataConfig.mappingDict[modalDataConfig.y_axis]} id="${modalDataConfig.id14}" size="7" value="${modalDataConfig.legend_x}">
        <input type="text" placeholder=${modalDataConfig.mappingDict[modalDataConfig.second_column]} id="${modalDataConfig.id15}" size="7" value="${modalDataConfig.legend_y}">
        <br><br>
        <label style="font-size:1.1rem">Change the label of an element:</label><br>
        <input type="text" placeholder="X Axis Label" id="${modalDataConfig.id13}" size="9" value="${modalDataConfig.element_label}"> &nbsp;&nbsp;
        <label style="font-size:1.1rem">Chart interaction:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" checked="checked" name="defaultValueConfig" id="${modalDataConfig.id21}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id21}" class="custom-control-label">
                      Cross-filter
                      </label>
                  </div>
        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id18}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" style="line-height: 1.1;">Reset Axis Labels</button><br><br>
                          <label style="font-size:1.1rem">Change Plot Labels:</label>
          <button type="button" class="btn btn-primary" id="${modalDataConfig.id_labels}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" value="${modalDataConfig.label_value}" style="line-height: 1.1;">${modalDataConfig.label_text}</button>
                          <br><br>
                          <label style="font-size:1.1rem">Box Shadow</label>
                          <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the shadow color:</label>
                          <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
                          <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
                          <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
                          <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
                          <label style="font-size:1.1rem">Set Shadow Thickness:</label>
                          <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
                          <label style="font-size:1.1rem">Box Border</label>
                          <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
                          <label style="font-size:1.1rem">Choose the border color:</label>
                          <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
                          <label style="font-size:1.1rem">Set border thickness</label>
                          <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
                          <label style="font-size:1.1rem">Choose border style:</label>
                          <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
                          <option value="solid">Solid</option>
                          <option value="dotted">Dotted</option>
                          <option value="double">Double</option>
                          <option value="dashed">Dashed</option>
                          </select><br><br>
                          <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}
        <br>${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        ${modalDataConfig.optionvaluesHTML}
        <br><br>
        <label style="font-size:1.1rem">Change labels color:</label>
        <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
        <br>
        <label style="font-size:1.1rem">Set labels font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>
        </div>
        </div>
        `)
    }else if(modalDataConfig.graph_subtype === 'Vertical_Bar_Stacked'){
        return $(`

        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">


        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>
        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br>
        <label style="font-size:1.1rem">Change the color or an element:</label>
        <input type="color" id="${modalDataConfig.id4}" name="favcolor1" value="${modalDataConfig.element_color}"><br><br>
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label></div>
                      <br><label style="font-size:1.1rem">Change X and Y axis gridlines:</label>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id9}" data-toggle="button" role="tab"
                        aria-pressed="false" autocomplete="off" value="${modalDataConfig.grid_id}" style="line-height: 0.7;">${modalDataConfig.value}</button><br><br>
                        <label style="font-size:1.1rem">Change the range of the axis:</label>
        <input type="text" placeholder="Y Axis Start" id="${modalDataConfig.id2}" size="7" value="${modalDataConfig.y_axis_start}">
        <input type="text" placeholder="Y Axis End " id="${modalDataConfig.id3}" size="7" value="${modalDataConfig.y_axis_end}">
        <br><br>
        <label style="font-size:1.1rem">Change the title of the axes:</label>
        <input type="text" placeholder="X Axis Title" id="${modalDataConfig.id11}" size="7" value="${modalDataConfig.x_axis_title}">
        <br><br>
        <label style="font-size:1.1rem">Change the legend labels:</label>
        <input type="text" placeholder=${modalDataConfig.mappingDict[modalDataConfig.y_axis]} id="${modalDataConfig.id14}" size="7" value="${modalDataConfig.legend_x}">
        <input type="text" placeholder=${modalDataConfig.mappingDict[modalDataConfig.second_column]} id="${modalDataConfig.id15}" size="7" value="${modalDataConfig.legend_y}">
        <br><br>
        <label style="font-size:1.1rem">Change the label of an element:</label><br>
        <input type="text" placeholder="X Axis Label" id="${modalDataConfig.id13}" size="9" value="${modalDataConfig.element_label}"> &nbsp;&nbsp;
        <label style="font-size:1.1rem">Chart interaction:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" checked="checked" name="defaultValueConfig" id="${modalDataConfig.id21}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id21}" class="custom-control-label">
                      Cross-filter
                      </label>
                  </div>
        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        <button type="button" class="btn btn-primary" id="${modalDataConfig.id18}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" style="line-height: 1.1;">Reset Axis Labels</button><br><br>
                          <label style="font-size:1.1rem">Change Plot Labels:</label>
          <button type="button" class="btn btn-primary" id="${modalDataConfig.id_labels}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" value="${modalDataConfig.label_value}" style="line-height: 1.1;">${modalDataConfig.label_text}</button>
                          <br><br>
        <label style="font-size:1.1rem">Box Shadow</label>
        <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the shadow color:</label>
        <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
        <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
        <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
        <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
        <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Thickness:</label>
        <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
        <label style="font-size:1.1rem">Box Border</label>
        <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the border color:</label>
        <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
        <label style="font-size:1.1rem">Set border thickness</label>
        <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
        <label style="font-size:1.1rem">Choose border style:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
        <option value="solid">Solid</option>
        <option value="dotted">Dotted</option>
        <option value="double">Double</option>
        <option value="dashed">Dashed</option>
        </select><br><br>
        <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}
        <br>${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        <br>
        <label style="font-size:1.1rem">Set order for X Axis:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_axis_order}" style="font-size:1.1rem" onchange="changeOrder.call(this)" data-chart-id = "${modalDataConfig.id6}" datatype_dict = '${JSON.stringify(modalDataConfig.datatype_dict)}' mappingDict = '${JSON.stringify(modalDataConfig.mappingDict)}' order_type = 'Vertical'>
        <option value="" selected>----------</option>
        <option value="asc">Ascending</option>
        <option value="desc">Descending</option>
        <option value="cust">Custom</option>
        </select>
        <br>
        <button class="btn btn-primary btn-xs rounded px-2" id="${modalDataConfig.idOrderModal}Button" data-modal_id="${modalDataConfig.idOrderModal}" data-chart-id = "${modalDataConfig.id6}" data-sorted-values = "" onclick="orderModal.call(this)" datatype_dict = '${JSON.stringify(modalDataConfig.datatype_dict)}' order_type = 'Vertical' style="display:none; height : 30px;">Set preferred order
        </button>
        ${modalDataConfig.optionvaluesHTML}
        <br><br>
            <label style="font-size:1.1rem">Change labels color:</label>
            <input type="color" id="${modalDataConfig.id_label_color}" name="favcolor" value="${modalDataConfig.label_color}" class="form-control"><br>
            <br>
            <label style="font-size:1.1rem">Set labels font size:</label>
            <input type="number" placeholder="font-size" id="${modalDataConfig.id_label_fontsize}" value="${modalDataConfig.label_fontsize}" size="7" class="form-control" style="padding-left: 1rem;"><br><br>
        </div>
        </div>
        `)
    }else if(modalDataConfig.graph_subtype === 'Angular_Gauge'){
        return $(`

        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">


        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>

        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br>
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label></div><br><br>

        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        <br><br>
        <label style="font-size:1.1rem">Box Shadow</label>
        <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the shadow color:</label>
        <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
        <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
        <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
        <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
        <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Thickness:</label>
        <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
        <label style="font-size:1.1rem">Box Border</label>
        <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the border color:</label>
        <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
        <label style="font-size:1.1rem">Set border thickness</label>
        <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
        <label style="font-size:1.1rem">Choose border style:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
        <option value="solid">Solid</option>
        <option value="dotted">Dotted</option>
        <option value="double">Double</option>
        <option value="dashed">Dashed</option>
        </select><br><br>
        <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}
        <br>${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        <br>
        <label style="font-size:1.1rem">Set threshold:</label>
        <input type="number" id="${modalDataConfig.id25}">
        <label style="font-size:1.1rem">Set threshold color:</label>
        <input type="color" id="${modalDataConfig.id26}">
        <label style="font-size:1.1rem">Set Delta:</label>
        <input type="number" id="${modalDataConfig.id27}">
        <button class="btn btn-primary btn-xs rounded px-2" id="${modalDataConfig.idGaugeModal}Button" data-modal_id="${modalDataConfig.idGaugeModal}" onclick="gaugeModal.call(this)">Conditional formatting</button>
        <button class="btn btn-primary btn-xs rounded px-2" id="${modalDataConfig.idGaugeModal}RangeButton" data-modal_id="${modalDataConfig.idGaugeModal}Range" onclick="gaugeModalRange.call(this)">Range based formatting</button>
        ${modalDataConfig.optionvaluesHTML}
        </div>
        </div>
        `)
    }else if(modalDataConfig.graph_subtype === 'Bullet_Gauge'){

        return $(`

        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">


        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the graph color:</label>

        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.color}"><br><br>
        <label style="font-size:1.1rem">Change the graph background:</label>
                  <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                  <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label></div><br><br>

        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        <br><br>
        <label style="font-size:1.1rem">Box Shadow</label>
        <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the shadow color:</label>
        <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
        <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
        <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
        <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
        <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Thickness:</label>
        <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
        <label style="font-size:1.1rem">Box Border</label>
        <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the border color:</label>
        <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
        <label style="font-size:1.1rem">Set border thickness</label>
        <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
        <label style="font-size:1.1rem">Choose border style:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
        <option value="solid">Solid</option>
        <option value="dotted">Dotted</option>
        <option value="double">Double</option>
        <option value="dashed">Dashed</option>
        </select><br><br>
        <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}
        <br>${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        ${modalDataConfig.optionvaluesHTML}
        </div>
        </div>
        `)
    }

    else if(["Pivot_Table","Table_Barchart","Heatmap","Row_Heatmap","Col_Heatmap","Line_Chart","Bar_Chart","Stacked_Bar_Chart","Area_Chart","Scatter_Chart"].includes(modalDataConfig.graph_subtype)){
        return $(`
        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">
        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
        <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <div class=" form-row">
            <div class="col-12" id="">
                <div class="form-group">
                    <label class="acies_label col-md-12">Chart Type:</label>
                    <select id="${modalDataConfig.id_configure_pivot_charttype}" class="select2 plotAjax form-control" name="sel"
                    required>
                    <option value="" disabled>--------------------</option>
                    </select>
                </div>
            </div>
            <div class="col-12">
                <div class="form-group">
                    <label class="acies_label col-md-12">Operation:</label>
                    <select id="${modalDataConfig.id_configure_pivot_operation}" class="select2 plotAjax form-control" name="sel"
                    required>
                    <option value="" disabled selected>--------------------</option>
                    </select>
                </div>
            </div>
        </div>
        <label style="font-size:1.1rem">Visualization Theme:</label>
        <div class="custom-control custom-checkbox">
            <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
            <label for="${modalDataConfig.id23}" class="custom-control-label">
            Global Settings
            </label></div><br><br>
            <label style="font-size:1.1rem">Connected slicers:</label>
            <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">
        </div><br><br>
        <label style="font-size:1.1rem">Box Shadow</label>
        <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the shadow color:</label>
        <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
        <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
        <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
        <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
        <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Thickness:</label>
        <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
        <label style="font-size:1.1rem">Box Border</label>
        <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the border color:</label>
        <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
        <label style="font-size:1.1rem">Set border thickness</label>
        <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
        <label style="font-size:1.1rem">Choose border style:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
        <option value="solid">Solid</option>
        <option value="dotted">Dotted</option>
        <option value="double">Double</option>
        <option value="dashed">Dashed</option>
        </select>
        <br><br>
        <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        <select class="select2" name="border_style" id="${modalDataConfig.id_header_fontweight}" style="font-size:1.1rem" >
        <option value="100">100</option>
        <option value="200">200</option>
        <option value="300">300</option>
        <option value="400">400</option>
        <option value="500">500</option>
        <option value="600">600</option>
        <option value="700">700</option>
        <option value="800">800</option>
        <option value="900">900</option>
        <option value="bold">Bold</option>
        <option value="bolder">Bolder</option>
        <option value="inherit">Inherit</option>
        <option value="lighter">Lighter</option>
        <option value="Normal">Normal</option>
        </select>
        <br>
        <label style="font-size:1.1rem">Set header font style:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_fontstyle}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="Arial">Arial</option>
        <option value="Times New Roman">Times New Roman</option>
        <option value="Helvetica">Helvetica</option>
        <option value="Lucida Console">Lucida Console</option>
        <option value="Courier New">Courier New</option>
        <option value="Verdana">Verdana</option>
        <option value="Trebuchet MS">Trebuchet MS</option>
        <option value="auto">auto</option>
        <option value="emoji">emoji</option>
        <option value="cursive">cursive</option>
        <option value="inherit">inherit</option>
        <option value="initial">initial</option>
        <option value="none">none</option>
        <option value="math">math</option>
        <option value="monospace">monospace</option>
        <option value="serif">serif</option>
        <option value="fangsong">fangsong</option>
        <option value="fantasy">fantasy</option>
        <option value="revert">revert</option>
        <option value="FontAwesome">FontAwesome</option>
        <option value="system-ui">system-ui</option>
        <option value="ui-monospace">ui-monospace</option>
        <option value="-webkit-pictograph">-webkit-pictograph</option>
        <option value="-webkit-body">-webkit-body</option>
        <option value="Trebuchet MS">Trebuchet MS</option>
        <option value="Courier New">Courier New</option>
        <option value="Andale Mono">Andale Mono</option>
        <option value="Trebuchet MS">Trebuchet MS</option>
        <option value="Comic Sans MS">Comic Sans MS</option>
        </select>
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
                        </div>
                        </div>
        `)
    }
    else if(modalDataConfig.graph_subtype === 'Table'){
        return $(`
        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">
        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
        <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Visualization Theme:</label>
        <div class="custom-control custom-checkbox">
            <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
            <label for="${modalDataConfig.id23}" class="custom-control-label">
            Global Settings
            </label></div><br><br>
            <label style="font-size:1.1rem">Connected slicers:</label>
            <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">
        </div><br><br>
        <button class="btn btn-primary conditional_table_edit" id="${modalDataConfig.id_condition_modal_edit}">Set Conditional-formatting</button>
        <br><br>
        <button class="btn btn-primary column_alignment_table_edit" id="${modalDataConfig.id_columnAlignmentModal_edit}">Configure Column Alignment</button>
        <button class="btn btn-primary Formatters" id="${modalDataConfig.id_Formatters_edit}">Formatters</button>
        <br><br>
        <button class="btn btn-primary" id="${modalDataConfig.id_freeze_pane}">Freeze Panes</button>
        <br><br>
                <div class='HighlightColHeaders card col-12' id="${modalDataConfig.id_HighlightColHeaders}">
                    <div class='card-header form-group col-order' style="color:var(--primary-color); font-weight: 700;">Configure Header's Styling
                        <button class ="btn btn-primary text-light saveBtn_HighlightColHeaders" id="${modalDataConfig.id_saveBtn_HighlightColHeaders}"style="margin-left:1.8rem;">save</button>
                        <input type="checkbox" id="${modalDataConfig.id_HighlightColHeaders_checkbox}" class="float-right checkboxinput custom-checkbox" style ="margin-top:10px;">
                    </div>
                    <div id="${modalDataConfig.id_HighlightColHeaders_div}" class = "form-group"  style = "display:none">
                        <ul class="sortable-order table_HighlightColHeaders plotAjax pt-1 col" id="${modalDataConfig.id_HighlightColHeaders_ul}" style="list-style: none; max-height:150px;overflow:auto;margin-bottom:-10px;">
                    </div>
                </div>
        <label style="font-size:1.1rem">Box Shadow</label>
        <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the shadow color:</label>
        <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
        <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
        <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
        <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
        <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Thickness:</label>
        <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
        <label style="font-size:1.1rem">Box Border</label>
        <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the border color:</label>
        <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
        <label style="font-size:1.1rem">Set border thickness</label>
        <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
        <label style="font-size:1.1rem">Choose border style:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
        <option value="solid">Solid</option>
        <option value="dotted">Dotted</option>
        <option value="double">Double</option>
        <option value="dashed">Dashed</option>
        </select>
        <br><br>
        <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        <select class="select2" name="border_style" id="${modalDataConfig.id_header_fontweight}" style="font-size:1.1rem" >
        <option value="100">100</option>
        <option value="200">200</option>
        <option value="300">300</option>
        <option value="400">400</option>
        <option value="500">500</option>
        <option value="600">600</option>
        <option value="700">700</option>
        <option value="800">800</option>
        <option value="900">900</option>
        <option value="bold">Bold</option>
        <option value="bolder">Bolder</option>
        <option value="inherit">Inherit</option>
        <option value="lighter">Lighter</option>
        <option value="Normal">Normal</option>
        </select>
        <br>
        <label style="font-size:1.1rem">Set header font style:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_fontstyle}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="Arial">Arial</option>
        <option value="Times New Roman">Times New Roman</option>
        <option value="Helvetica">Helvetica</option>
        <option value="Lucida Console">Lucida Console</option>
        <option value="Courier New">Courier New</option>
        <option value="Verdana">Verdana</option>
        <option value="Trebuchet MS">Trebuchet MS</option>
        <option value="auto">auto</option>
        <option value="emoji">emoji</option>
        <option value="cursive">cursive</option>
        <option value="inherit">inherit</option>
        <option value="initial">initial</option>
        <option value="none">none</option>
        <option value="math">math</option>
        <option value="monospace">monospace</option>
        <option value="serif">serif</option>
        <option value="fangsong">fangsong</option>
        <option value="fantasy">fantasy</option>
        <option value="revert">revert</option>
        <option value="FontAwesome">FontAwesome</option>
        <option value="system-ui">system-ui</option>
        <option value="ui-monospace">ui-monospace</option>
        <option value="-webkit-pictograph">-webkit-pictograph</option>
        <option value="-webkit-body">-webkit-body</option>
        <option value="Trebuchet MS">Trebuchet MS</option>
        <option value="Courier New">Courier New</option>
        <option value="Andale Mono">Andale Mono</option>
        <option value="Trebuchet MS">Trebuchet MS</option>
        <option value="Comic Sans MS">Comic Sans MS</option>
        </select>
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        <br>
        <div class='fieldColOrder card col-12' id="${modalDataConfig.id_tableColunm_Rearrange}">
        <div class='card-header form-group col-order' style="color:var(--primary-color); font-weight: 700;">Column re-ordering
        <button class ="btn btn-primary text-light saveBtn_order" style="margin-left:80px;">save</button>
        <input type="checkbox" id="${modalDataConfig.id_tableColunm_Rearrange_checkbox}" class="float-right checkboxinput custom-checkbox" style ="margin-top:10px;">
        </div>
        <div id="${modalDataConfig.id_tableColunm_Rearrange_div}" class = "form-group"  style = "display:none">
        <ul class="sortable-order table_columns_re-order1 plotAjax pt-1 col" id="${modalDataConfig.id_tableColunm_Rearrange_ul}" style="list-style: none; max-height:150px;overflow:auto;margin-bottom:-10px;">
         </div>
          </div>
                        </div>
                        </div>
        `)
    }
    else if(modalDataConfig.graph_subtype === "Nested_Table"){
        return $(`

                    <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
                    right: 0 ;top : 10px;z-index: 1050">


                    <div class="modal-content">
                    <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
                    <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
                    <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                    </button>
                    </div>
                    <div class="modal-body" style="max-height:26rem;overflow:auto">
                    <label style="font-size:1.1rem">Change the graph background:</label>
                <input type="color" id="${modalDataConfig.id22}" name="favcolor" value="${modalDataConfig.plot_bg_color}"><br><br>
                <label style="font-size:1.1rem">Visualization Theme:</label>
                <div class="custom-control custom-checkbox">
                    <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                    <label for="${modalDataConfig.id23}" class="custom-control-label">
                    Global Settings
                    </label></div>
                    <br><br>
                    <button class="btn btn-primary conditional_table_edit" id="${modalDataConfig.id_condition_modal_edit}">Set Conditional-formatting</button>
                    <br><br>
                    <label style="font-size:1.1rem">Connected slicers:</label>
                    <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">
                    </div>
                    <br><br>
            <label style="font-size:1.1rem">Box Shadow</label>
            <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
            <label style="font-size:1.1rem">Choose the shadow color:</label>
            <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
            <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
            <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
            <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
            <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
            <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
            <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
            <label style="font-size:1.1rem">Set Shadow Thickness:</label>
            <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
            <label style="font-size:1.1rem">Box Border</label>
            <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
            <label style="font-size:1.1rem">Choose the border color:</label>
            <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
            <label style="font-size:1.1rem">Set border thickness</label>
            <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
            <label style="font-size:1.1rem">Choose border style:</label>
            <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
            <option value="solid">Solid</option>
            <option value="dotted">Dotted</option>
            <option value="double">Double</option>
            <option value="dashed">Dashed</option>
            </select>
            <br><br>
            <label style="font-size:1.1rem">Change the header color:</label>
            <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
            <br>
            <label style="font-size:1.1rem">Change the background color of header:</label>
            <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
            <label style="font-size:1.1rem">Set header font size:</label>
            <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
            <label style="font-size:1.1rem">Set header font weight:</label>

            ${modalDataConfig.borderStylehtml}
            <br>
            ${modalDataConfig.setheaderFontHTML}
            <br>
            <label style="font-size:1.1rem">Set header alignment:</label>
            <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
            <option value="">----------</option>
            <option value="left">Left</option>
            <option value="center">Center</option>
            <option value="right">Right</option>
            </select>
            ${modalDataConfig.optionvaluesHTML}
            <br>
            <div class='fieldColOrder card col-12' id="${modalDataConfig.id_nestedtableColunm_Rearrange}">
            <div class='card-header form-group col-order' style="color:var(--primary-color); font-weight: 700;">Column re-ordering
            <button class ="btn btn-primary text-light saveBtn_order1" style="margin-left:80px;">save</button>
            <input type="checkbox" id="${modalDataConfig.id_nestedtableColunm_Rearrange_checkbox}" class="float-right checkboxinput custom-checkbox" style ="margin-top:10px;">
            </div>
            <div id="${modalDataConfig.id_nestedtableColunm_Rearrange_div}" class = "form-group"  style = "display:none">
            <ul class="sortable-order table_columns_re-order1 plotAjax pt-1 col" id="${modalDataConfig.id_nestedtableColunm_Rearrange_ul}" style="list-style: none; max-height:150px;overflow:auto;margin-bottom:-10px;">
            </ul>
            </div>
            </div>
                    </div>
                    </div>
                    `)
    }else if(modalDataConfig.graph_subtype === "Aggregation"){
        return $(`

        <div class="modal-dialog modalgraphs modal-full-height modal-right" id="${modalDataConfig.id7}" role="document" style="display:none;float:right;  position: absolute;
        right: 0 ;top : 10px;z-index: 1050">


        <div class="modal-content">
        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Configure</span>
        <button type="button" class="close" data-dismiss="modal" id="${modalDataConfig.id10}" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
        </div>
        <div class="modal-body" style="max-height:26rem;overflow:auto">
        <label style="font-size:1.1rem">Change the card color:</label>
        <input type="color" id="${modalDataConfig.id1}" name="favcolor" value="${modalDataConfig.newcolor}">
        <br><br>
        <label style="font-size:1.1rem">Change the size of the font:</label>
        <input type="text" placeholder="value" id="${modalDataConfig.id2}" size="7" value="${modalDataConfig.config_valuesize}">
        <input type="text" placeholder="category" id="${modalDataConfig.id3}" size="7" value="${modalDataConfig.config_titlesize}">
        <br><br>

        <label style="font-size:1.1rem">Choose value unit:</label>
        <select name="cars" id="${modalDataConfig.id18}" datavalue = "${modalDataConfig.value}" style="font-size:1.1rem">
        <option value="----">----</option>
        <option value="Units">Units</option>
        <option value="Hundreds">Hundreds</option>
        <option value="Thousands">Thousands</option>
        <option value="Millions">Millions</option>
        <option value="Billions">Billions</option>
        </select>
        <label style="font-size:1.1rem">Visualization Theme:</label>
                  <div class="custom-control custom-checkbox">
                      <input type="checkbox" ${global_bg_checked} name="defaultValueColorConfig" id="${modalDataConfig.id23}" class="checkboxinput custom-control-input">
                      <label for="${modalDataConfig.id23}" class="custom-control-label">
                      Global Settings
                      </label>
                  </div><br><br>
        <label style="font-size:1.1rem">Connected slicers:</label>
        <div id="${modalDataConfig.id20}" style="max-height:5rem;overflow:auto;overflow-x:hidden;">

        </div>
        <br><br>
        <label style="font-size:1.1rem">Add/Remove Title:</label>
        <button type="button" class="btn btn-primary" value=${modalDataConfig.title_name_value} id="${modalDataConfig.id_agg_title}" data-toggle="button" role="tab"
                          aria-pressed="false" autocomplete="off" style="line-height: 1.1;">${modalDataConfig.title_name}</button>
                          <br><br>
        <label style="font-size:1.1rem">Box Shadow</label>
        <label class="switch"><input type="checkbox"  id ="${modalDataConfig.id_shadow}" ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the shadow color:</label>
        <input  type="color" id="${modalDataConfig.id_shadow_color}"  value="${modalDataConfig.shadowColor}" name="favcolor3" ><br><br>
        <label style="font-size:1.1rem">Set Shadow X-Offset:</label>
        <input type="number" placeholder="X-Offset" id="${modalDataConfig.id_xshadow}" value="${modalDataConfig.shadowXOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Y-Offset:</label>
        <input type="number" placeholder="Y-Offset" id="${modalDataConfig.id_yshadow}" value= "${modalDataConfig.shadowYOffset}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Blur Radius:</label>
        <input type="number" placeholder="Radius value" id="${modalDataConfig.id_blurshadow}" value= "${modalDataConfig.shadowBlur}" size="7" min = "0" ><br><br>
        <label style="font-size:1.1rem">Set Shadow Thickness:</label>
        <input type="number" placeholder="Thickness value" id="${modalDataConfig.id_shadow_thickness}" value= "${modalDataConfig.shadowThickness}" size="7" ><br><br>
        <label style="font-size:1.1rem">Box Border</label>
        <label class="switch"  ><input type="checkbox" id ="${modalDataConfig.id_border}"  ><span class="slider round" style="border-radius: 30px"></span></label><br><br>
        <label style="font-size:1.1rem">Choose the border color:</label>
        <input  type="color" id="${modalDataConfig.id_border_color}" "name="favcolor3" value="${modalDataConfig.borderColor}"><br><br>
        <label style="font-size:1.1rem">Set border thickness</label>
        <input type="number" placeholder="Thickness" id="${modalDataConfig.id_border_thickness}" size="7" value= "${modalDataConfig.borderThickness}" min = "1"><br><br>
        <label style="font-size:1.1rem">Choose border style:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_border_style}" style="font-size:1.1rem" >
        <option value="solid">Solid</option>
        <option value="dotted">Dotted</option>
        <option value="double">Double</option>
        <option value="dashed">Dashed</option>
        </select>
        <br><br>
        <label style="font-size:1.1rem">Change the header color:</label>
        <input type="color" id="${modalDataConfig.id_header_color}" name="favcolor" value="${modalDataConfig.header_color}"><br>
        <br>
        <label style="font-size:1.1rem">Change the background color of header:</label>
        <input type="color" id="${modalDataConfig.id_header_bgcolor}" name="favcolor1" value="${modalDataConfig.header_bgcolor}"><br><br>
        <label style="font-size:1.1rem">Set header font size:</label>
        <input type="number" placeholder="font-size" id="${modalDataConfig.id_header_fontsize}" value="${modalDataConfig.header_fontsize}" size="7" ><br><br>
        <label style="font-size:1.1rem">Set header font weight:</label>

        ${modalDataConfig.borderStylehtml}
        <br>
        ${modalDataConfig.setheaderFontHTML}
        <br>
        <label style="font-size:1.1rem">Set header alignment:</label>
        <select class="select2" name="border_style" id="${modalDataConfig.id_header_alignment}" style="font-size:1.1rem" >
        <option value="">----------</option>
        <option value="left">Left</option>
        <option value="center">Center</option>
        <option value="right">Right</option>
        </select>
        <br>
        <label style="font-size:1.1rem">Choose icon image:</label>
        <select class="select2" name="iconimg" id="${modalDataConfig.id_img_icon}" style="font-size:1.1rem" onchange="changeIcon.call(this)" data-chart-id = "${modalDataConfig.id6}" data-img-id = "${modalDataConfig.id4}">
        <option value="" disabled selected>--------------------</option>
        <option value="/static/images/Base_theme/barchart.png" selected>Bar Chart</option>
        <option value="/static/images/Base_theme/piechart.png">Pie Chart</option>
        <option value="/static/images/Base_theme/linechart.png">Line Chart</option>
        <option value="/static/images/Base_theme/histogram.png">Histogram</option>
        <option value="/static/images/Base_theme/doughnutchart.png">Doughnut Chart</option>
        <option value="/static/images/Base_theme/scatterplot.png">Scatter Plot</option>
        <option value="/static/images/Base_theme/radarplot.png">Radar Plot</option>
        <option value="/static/images/Base_theme/ganttchart.png">Gantt Chart Plot</option>
        <option value="/static/images/Base_theme/flowchart.png">Flow Chart</option>
        <option value="/static/images/Base_theme/combochart.png">Combo Chart</option>
        <option value="/static/images/Base_theme/hierarchy.png">Hierarchy</option>
        <option value="/static/images/Base_theme/normaldistribution.png">Normal Distribution</option>
        <option value="/static/images/Base_theme/sum.png">Sum</option>
        <option value="/static/images/Base_theme/average.png">Average</option>
        <option value="/static/images/Base_theme/counter.png">Counter</option>
        <option value="/static/images/Base_theme/alphabeticalsorting.png">Alphabetical Sorting</option>
        <option value="/static/images/Base_theme/reversealphabeticalsorting.png">Reverse Alphabetical Sorting</option>
        <option value="/static/images/Base_theme/numericalsorting.png">Numerical Sorting</option>
        <option value="/static/images/Base_theme/reversednumericalsorting.png">Reverse Numerical Sorting</option>
        <option value="/static/images/Base_theme/increasing.png">Increasing</option>
        <option value="/static/images/Base_theme/decreasing.png">Decreasing</option>
        <option value="/static/images/Base_theme/updownarrow.png">Up and Down Arrow</option>
        <option value="/static/images/Base_theme/venndiagram.png">Venn Diagram</option>
        <option value="/static/images/Base_theme/schedule.png">Schedule</option>
        <option value="/static/images/Base_theme/unavailable.png">Unavailable</option>
        <option value="/static/images/Base_theme/clock.png">Waitng</option>
        <option value="/static/images/Base_theme/approved_2.png">Approved</option>
        <option value="/static/images/Base_theme/disapproved.png">Disapproved</option>
        <option value="/static/images/Base_theme/expired.png">Expired</option>
        <option value="/static/images/Base_theme/highpriority.png">High Priority</option>
        <option value="/static/images/Base_theme/notification.png">Notification</option>
        <option value="/static/images/Base_theme/idea.png">Idea</option>
        <option value="/static/images/Base_theme/filter.png">Filter</option>
        <option value="/static/images/Base_theme/privacy.png">Privacy</option>
        <option value="/static/images/Base_theme/questionmark.png">Question Mark</option>
        <option value="/static/images/Base_theme/conflict.png">Conflict</option>
        <option value="/static/images/Base_theme/feedback.png">Feedback</option>
        <option value="/static/images/Base_theme/settings.png">Setting</option>
        <option value="/static/images/Base_theme/menu.png">Menu</option>
        <option value="/static/images/Base_theme/bookmark.png">Bookmark</option>
        <option value="/static/images/Base_theme/synchronize.png">Synchronize</option>
        <option value="/static/images/Base_theme/share.png">Share</option>
        <option value="/static/images/Base_theme/search.png">Search</option>
        <option value="/static/images/Base_theme/users.png">Users</option>
        <option value="/static/images/Base_theme/process.png">Process Flow</option>
        <option value="/static/images/Base_theme/slider.png">Slider</option>
        <option value="/static/images/Base_theme/document.png">Document</option>
        <option value="/static/images/Base_theme/file.png">File</option>
        <option value="/static/images/Base_theme/folder.png">Folder</option>
        <option value="/static/images/Base_theme/broadcasting.png">Broadcasting</option>
        <option value="/static/images/Base_theme/blockchain.png">Blockchain</option>
        <option value="/static/images/Base_theme/datasheet.png">Datasheet</option>
                </select>
        ${modalDataConfig.optionvaluesHTML}
        <br>
        <div id="${modalDataConfig.id_optionvalues}operation_n" style="display:none;">
        <label style="font-size:1.1rem">Change sub-operation for Aggregation:</label>
        <select class="select2" name="change_operation" id="${modalDataConfig.id_optionvalues}operation_ndropdown" data-chart-id = "${modalDataConfig.id6}" tabSlicerId = "${modalDataConfig.tabSlicerId}" onchange="changeChartOperation.call(this, 'data-operation_n')" style="font-size:1.1rem;" >
            <option value="Sum">Sum</option>
            <option value="Maximum">Maximum</option>
            <option value="Minimum">Minimum</option>
            <option value="Count">Count</option>
            <option value="Count Distinct">Count Distinct</option>
            <option value="Average">Average</option>
            <option value="Median">Median</option>
            <option value="Variance">Variance</option>
            <option value="Skewness">Skewness</option>
            <option value="Kurtosis">Kurtosis</option>
            <option value="Standard Deviation">Standard Deviation</option>
        </select>
        <br>
        <label style="font-size:1.1rem">Change N:</label>
        <input id="${modalDataConfig.id_optionvalues}operation_ncomputed_number" data-chart-id = "${modalDataConfig.id6}" tabSlicerId = "${modalDataConfig.tabSlicerId}"  oninput="changeChartOperation.call(this, 'data-computed_number')"  type="number" value="0" min="0" style="width:19em;height:2.2em;">
        </div>
        </div>
        </div>`)
    }
}



