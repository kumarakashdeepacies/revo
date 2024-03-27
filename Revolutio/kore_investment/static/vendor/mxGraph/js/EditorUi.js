/**
 * Copyright (c) 2006-2012, JGraph Ltd
 */

//Function use to define icons
let elementConnected = []
let elementConnectedTable = []
let childConnected = []
let childName = []
mxConnectionHandler.prototype.connectImage = new mxImage('images/connector.gif', 16, 16);
mxConnectionHandlerInsertEdge = mxConnectionHandler.prototype.insertEdge;
mxConnectionHandler.prototype.insertEdge = function(parent, id, value, source, target, style)
{
  value = ``;
  id = "flow"+String(Math.random()).replace(".","");
  style = style + "shapeUniqueID="+id+";"
  return mxConnectionHandlerInsertEdge.apply(this, arguments);
};
var yes = 0
mxEdgeHandler.prototype.getSelectionPoints = function(	state	) {
	if(state.style.shape == "connector") {
		this.currentIconSet = null
		mxEdgeHandler.prototype.mouseMove = function(	sender,me) {
			if (this.currentIconSet == null)
			{
				this.currentIconSet = new mxIconSet(state);
				yes = 1;
			}
		}
		mxEdgeHandler.prototype.mouseDown = function(	sender,me){
			if (this.currentIconSet != null)
			yes = 0
			{
				this.currentIconSet.destroy();
			    this.currentIconSet = null;
				$(document).find('.geDiagramContainer').find('img').each(function() {
					if($(this).attr('title') == "Configure line") {
						$(this).remove();
					}
				})

			}
		}

	}
}
		var parent_element_list = []
			// Defines a new class for all icons
		function mxIconSet(state)
		{
			Graph.xml = ""
			this.images = [];
			var graph = state.view.graph;
			var element_main_id = state.cell.style.substr(state.cell.style.search("shapeUniqueID")).substr((state.cell.style.substr(state.cell.style.search("shapeUniqueID"))).search("=")+1)
			let url_string = window.location.pathname
			let f_occ = url_string.indexOf('/', url_string.indexOf('/') + 1)
			let s_occ = url_string.indexOf('/', url_string.indexOf('/') + f_occ +1)
			let t_occ = url_string.indexOf('/', url_string.indexOf('/') + s_occ +1)
			let app_code2 = url_string.substring(f_occ+1,s_occ)
			let current_dev_mode2 = url_string.substring(s_occ+1,t_occ)
			if(current_dev_mode2 != "Build" && current_dev_mode2 != "Edit"){
			current_dev_mode2 = "User"
			}
			// Delete Icon
			if(state.style.shape != "connector") {

				var img = mxUtils.createImage(mxClient.basePath+'/images/delete.gif');
				img.setAttribute('title', 'Delete');
				img.style.position = 'absolute';
				img.style.cursor = 'pointer';
				img.style.width = '16px';
				img.style.height = '16px';
				img.style.left = (state.x + state.width+5) + 'px';
				img.style.top = (state.y) + 'px';

				mxEvent.addListener(img, 'click',
					mxUtils.bind(this, function(evt)
					{
						if(element_main_id){
								Swal.fire({
									title: 'Do you want to delete this element.?',
									icon: 'warning',
									showCancelButton: true,
									confirmButtonText: 'delete'
								  }).then((result) => {
									if (result.isConfirmed) {
										$.ajax({
											url: `/users/${app_code2}/${current_dev_mode2}/processGraphModule/`,
											data: {
											   'element_id':element_main_id,
											  'operation': 'delete_element_configuration',
											},
											type: "POST",
											dataType: "json",
											success: function (data) {
												Swal.fire({
													icon: 'success',
													text: 'Element deleted successfully!'
												  })
												element_main_id=""
											},
											error: function () {
												Swal.fire({
													icon: 'error',
													text: 'Error! Failure in deleting the element. Please try again.'
												  })
											}
										  });
										  graph.removeCells([state.cell]);
										  mxEvent.consume(evt);
										  this.destroy();
									}
								  })
						}

					})
				);
				mxEvent.addGestureListeners(img,
					mxUtils.bind(this, function(evt)
					{
						// Disables dragging the image
						mxEvent.consume(evt);
					})
				);

				state.view.graph.container.appendChild(img);
				this.images.push(img);

				// Duplicate Icon
				var img = mxUtils.createImage(mxClient.basePath+'/images/copy.gif');
				img.setAttribute('title', 'Duplicate');
				img.style.position = 'absolute';
				img.style.cursor = 'pointer';
				img.style.width = '16px';
				img.style.height = '16px';
				img.style.left = (state.x + state.width+5) + 'px';
				img.style.top = (state.y + 25) + 'px';


				mxEvent.addGestureListeners(img,
					mxUtils.bind(this, function(evt)
					{
						var s = graph.gridSize;
						var elementID= ""
						if(state.cell.style.search("shapeUniqueID")>0){
							state.cell.style=state.cell.style.substr(0,state.cell.style.search("shapeUniqueID"))
							elementID= state.cell.style.substr(state.cell.style.search("shapeUniqueID")).substr((state.cell.style.substr(state.cell.style.search("shapeUniqueID"))).search("=")+1)
						}
						graph.setSelectionCells(graph.moveCells([state.cell], s, s, true));
						mxEvent.consume(evt);
						this.destroy();
					})
				);

				state.view.graph.container.appendChild(img);
				this.images.push(img);

				//Configure Icon
				var img = mxUtils.createImage(mxClient.basePath+'/images/wrench.png');
				img.setAttribute('title', 'Configure Elements');
				img.style.position = 'absolute';
				img.style.cursor = 'pointer';
				img.style.width = '16px';
				img.style.height = '16px';
				img.style.left = (state.x + state.width+5) + 'px';
				img.style.top = (state.y + 50) + 'px';
				mxEvent.addGestureListeners(img,
					mxUtils.bind(this, function(evt)
					{
						// Disables dragging the image
						mxEvent.consume(evt);
					})
				);
				mxEvent.addListener(img, 'click',
				mxUtils.bind(this, function(evt)
				{
						var cellStyle=state.cell.style;
						var indexSeparator=cellStyle.indexOf(';');
						var shape=cellStyle.substr(0,indexSeparator);
						if(shape=="whiteSpace=wrap"){
							$('#createViewMainCanvasContainer').css('pointer-events', 'none');
							$('#createViewMainCanvasContainer').css('cursor', 'progress !important');
							$('#loadingSpinnerCreateview').css('display', 'block');
							$("#allField").prop("checked",false);
							$("#selectAllField").empty();
							$("#selectAllField").removeAttr("data-present");
							dic_cases = {};
							resetCases()
							var ind_count = 0
							$(".multiSelectCard").each(function() {
								if(ind_count != 0) {
									$(this).remove()
								}
								ind_count = ind_count + 1;
							})
							ind_count = 0
							$(".indCustomButton").each(function() {
								if(ind_count != 0) {
									$(this).remove()
								}
								ind_count = ind_count + 1;
							})
							$(".customButtonName").val("").trigger("change")
							p_sp_populate();
							$("#master_preview_mode").prop('checked', false);
							previewMaster();
							$('#createViewModal').find('.previewCustomTemplate').css("display",'none');
							$('#createViewModal').css('display','block')
							$('#embededComputationBtnID').attr('data-list','')
							$('#embededComputationModal').find('.topRow').find('.col-3').empty()
							$('#embededComputationModal').find('.computationRow').empty()

							$('#formModal').find('.modal-footer').attr('data-shapeid',state.cell.id)
							graph.getModel().getCell($('#reportModal').find('.modal-footer').attr('data-shapeid'));
							if(state.cell.style.search("shapeUniqueID")>0){
								$('#createViewFormCollectionContainer').css('pointer-events', 'none');
								$('#createViewFormCollectionContainer').css('cursor', 'not-allowed');
								fields = [];
								element_id=state.cell.style.substr(state.cell.style.search("shapeUniqueID")).substr((state.cell.style.substr(state.cell.style.search("shapeUniqueID"))).search("=")+1)
								create_view_config_load(element_id)
							}
							else{
								fieldAttributesCV =[]
								$('#selectedComparableNumList').empty();
								comparable=""
								$('#selectedFormfieldList').empty()
								compareFields={}
								columnSelection = [];
								periodSelection={}
								fields = [];
								pc1=""
								pf=""
								pt=""
								col_data=""
								$('#selectFormTemplate').val("").trigger("change")
								$('.Mulselect_Table').css('display','none')
								$('#selectFormTable').val("").trigger("change")
								$('#selectCharColumn').val("").trigger("change")
								$('#tabHeaderCreateView').val("")
								$('#selectAction').val("").trigger("change")
								$("#save_preview_mode").prop('checked',false)
								col_data="";
								$("#selectPeriodCol").val("").trigger("change")
								periodSelection["period_col"] = "";
								$("#periodFrom").val("")
								periodSelection["periodFrom"] = "";
								$("#periodTo").val("")
								periodSelection["periodTo"] = "";
								$('#loadingSpinnerCreateview').css('display', 'none');
								$('#createViewMainCanvasContainer').css('pointer-events', 'all');
								$('#createViewMainCanvasContainer').css('cursor', 'default');
								$('#createViewFormCollectionContainer').css('pointer-events', 'all');
								$('#createViewFormCollectionContainer').css('cursor', 'default');
								$("#js_filter_btn").attr('data-basicfilter-config','{}')
								$(".jsfilter_master").attr('data-basicfilter-config','{}')
								$(".jsfilter_val_message").val("").trigger("change")
							}
						}

						else if(shape=="shape=process"){
							$('#saveListViewConfig').closest(".modal-footer").find(".previewCustomTemplate").prop('disabled',true);
							$('#dataTableModal').modal('show')
							$('#listViewModalFooterContainer').find('.row').css('pointer-events', 'none');
							$('#listViewModalFooterContainer').css('cursor', 'progress');
							$('#listViewModalFooterContainer').find('button').css('pointer-events', 'none');
							$('#listViewModalFooterContainer').css('cursor', 'not-allowed');
							$('#dataTableModal').find('.modal-footer').attr('data-shapeid',state.cell.id)
							$('#saveBasicfilter').attr('data-shapeid',state.cell.id)
							$('#saveBasicfilter_mul').attr('data-shapeid',state.cell.id)
							$('#dataTableModal').find('#create_view_display_selection').attr('data-connectid',state.cell.id)

							// Connector Check

							let encoder = new mxCodec();
							let result = encoder.encode(graph.getModel());
							Graph.xml  = mxUtils.getXml(result);//generate a skeleton/dummy xml of  graph
							$('#buttonsGroupedTogether').attr('data-list','');
							$('#buttonsGroupedTogetherDiv').css('display','none');
							$('#hyperlinkingBtn').attr('data-list','null');
							$('#hyperlinkingTables').css('display','none');
							$('#configure_action_column_id').attr('data-list','');
							$('#listViewButtonEmbededComputationId').attr('data-list','')
							$("#listViewEmbededComputationModal").find('.masterstyling').remove()
							$('#formattingColumnBtn').attr('data-list','');
							$('#formattingColumnBtn').attr('data-listtwo','');
							$('#group_by_action_btn_sub').attr('data-list','');
							$('#group_by_action').css('display','none');
							$('#formattingColumnBtn').attr('data-listthree','');
							$('#formattingColumnBtn').attr('data-listfour','');
							$('#formattingColumns').find('.title-row-body').empty()
							$('#formattingColumns').find('.formatting-body').empty()
							$('#formattingColumns').css('display','none');
							$('#hyperlinkingBtn_mul').attr('data-list','null');
							$('#hyperlinkingBtn_mul').attr('data-listtwo','');
							$('#hyperlinkingTable_mul').css('display','none');
							$('#formattingColumnBtn_mul').attr('data-list','');
							$('#configure_actionbuttonid_multiple').attr('data-list','')
							$('#actionButtonsConfigurationModalMultiple').find('.main_container').find('.masterstyling').remove()
                          	$('#actionButtonsConfigurationModalMultiple').find('.small_container').find('.masterTableOrder').remove()
							$('#formattingColumns_mul').find('.formatting-body').empty()
							$('#formattingColumns_mul').css('display','none');
							$('#tableNameDiv').css('display','none');
							$('#tableNameDivMultiple').css('display','none');
							$("#titleNameMultipleModal").find('.card').remove()
							$('#titleNameBtn').attr('data-list','')
							$('#titleName_mul').css('display','none');
							$('#titleNameBtn_mul').attr('data-list','')
							$('#actionButtonsConfigurationModal').find('.modal-body').find('.masterstyling').remove()
                        	$('#actionButtonsConfigurationModal').find('#actionBtnOrder').attr('data-list','')
							$('#quick_filters_modal_id').find('.modal-body').find('.quickFilters').find('.masterfomatting').remove()
                        	$('#quickFiltersBtn').attr('data-list','')
							$("#paginationDiv").css("display","none");
							$("#pagination").removeAttr("data-list");
							$('#card_view_div').css("display","none");
							$('#card_view_sub_category').attr('data-list','');
							$('#listViewButtonId').attr('data-list','');
							$('#configure_action_pdf_id').css('display','none');
							$('#columnNamesRenamesButton').attr('data-list','');
							$('#listViewEditButtonModal').find('.masterstyling').remove();
							$.ajax({
								url: `/users/${app_code2}/${current_dev_mode2}/processGraphModule/`,
								data: {
									'operation': 'import_parent_elements_config',
									'xml': Graph.xml,
								},
								type: "POST",
								dataType: "json",
								success: function (data) {
								  $(`#create_view_display_selection`).parent().css('display','none')
								  parent_element_list = []
								for(let i=0;i< data.success.length;i++){
									if(data.success[i]['child'].length >0){
										for(let k=0;k<data.success[i]['child'].length;k++){
											let value_display = data.success[i]['child'][k]
											var cellSelected= graph.getModel().getCell($('#dataTableModal').find('.modal-footer').attr('data-shapeid'));
											if(value_display == cellSelected['id']){
											parent_element_list.push(data.success[i])
											$(`#create_view_display_selection`).parent().css('display','block')
											}
										}

									}

								}},
								error: function () {alert('Error')}})
							// End Connector Event

							if(state.cell.style.search("shapeUniqueID")>0){
								element_id=state.cell.style.substr(state.cell.style.search("shapeUniqueID")).substr((state.cell.style.substr(state.cell.style.search("shapeUniqueID"))).search("=")+1)
								list_view_config_load(element_id)

							}
							else{
								$.ajax({
									url: `/users/${app_code2}/${current_dev_mode2}/processGraphModule/`,
									data: {
									  'process_name': $('#selectProcess option:selected').text(),
									  'sub_process_name':$('#subprocess').val(),
									  'operation': 'fetchRelatedCreateViews',
									},
									type: "POST",
									dataType: "json",
									success: function (data) {
									  $('#selectMultiConfig').empty();
									  $('#selectMultiConfig').append(`<option value='Default' selected>Default</option>`);
									  for (i in data.templateMutiSelect) {
										$('#selectMultiConfig').append(`<option value='${data.templateMutiSelect[i]}'>${data.templateMutiSelect[i]}</option>`);
									  }

									  $('#selectMultiConfig_mul').empty();
									  $('#selectMultiConfig_mul').append(`<option value='Default' selected>Default</option>`);
									  for (i in data.templateMutiSelect) {
										$('#selectMultiConfig_mul').append(`<option value='${data.templateMutiSelect[i]}'>${data.templateMutiSelect[i]}</option>`);
									  }
									},
									error: function(){
									  alert("Error")
									}
								});
								$('#selectTable').val('').trigger("change")
								$('#selectTemplate').val('').trigger("change")
								$('#tabHeaderListView').val("").trigger('change')
								$('#create_view_display_selection').prop('checked',true)
								$('#dropFields').empty()
								$('#groupFields').empty()
								$('#restrictFields').empty()
								$('#dropFields_mul').empty()
								$('#groupFields_mul').empty()
								$('#restrictFields_mul').empty()
								$("#addrow").empty()
								$('.subCategory').each(function () {
								  $(this).css({ backgroundColor: '#565a5e' });
								  $(this).css({ borderColor: '#565a5e' });
								})
								$('.subElementCards').find('input[type=checkbox]').each(function(){
								  $(this)[0].checked=false
								  $(this)[0].disabled=false
								})
								$('#subCategoryButtons').find('.fa-check-circle').each(function(){
								  $(this).css('display','none')
								})
								$('.labelrow_mul').empty()
								$('.default_mul_view').empty()
								multable_config = {}
								multable_config_comp = {}
								$('#Datatable').css('display','none')
								$('#Chart').css('display','none')
								$('#Alert').css('display','none')
								$('#Filter').css('display','none')
								$('#previewCard').empty()
								$('#saveBasicfilter').removeAttr('data-shapeid');
								$('#basicfilter_items').find('.filter-table').empty();

								$('#Datatable_mul').css('display','none')
								$('#Chart_mul').css('display','none')
								$('#Alert_mul').css('display','none')
								$('#Filter_mul').css('display','none')
								$('#previewCard_mul').empty()
								$('#saveBasicfilter_mul').removeAttr('data-shapeid');
								$('#saveBasicfilter_mul').removeAttr('data-basicfilter-config');
								$('#basicfilter_items_mul').find('.filter-table').empty();
								$('#listViewModalFooterContainer').find('.row').css('pointer-events', 'all');
								$('#listViewModalFooterContainer').css('cursor', 'default');
								$('#listViewModalFooterContainer').find('button').css('pointer-events', 'all');
								$('#listViewModalFooterContainer').css('cursor', 'default');
								$("#dropFields_add").attr('data-data','{}')
							}
						}
						else if(shape=="rhombus"){
							$('#decisionModal').modal('show')
							$('#decisionModal').find('.modal-footer').attr('data-shapeid',state.cell.id)
							let encoder = new mxCodec();
							let result = encoder.encode(graph.getModel());
							Graph.xml  = mxUtils.getXml(result);
							getParentChild(Graph.xml,graph,"decisionModal");
							if(state.cell.style.search("shapeUniqueID")>0){
								element_id=state.cell.style.substr(state.cell.style.search("shapeUniqueID")).substr((state.cell.style.substr(state.cell.style.search("shapeUniqueID"))).search("=")+1)
								decision_config_load(element_id)
							}
							else{
								condition_dict={}
								for (let prop in filter_dict) {
									delete filter_dict[prop];
								  }
								$("#config_table tbody tr td:nth-child(2) span").html("")
								$("#configuration_row tr").slice(1).remove()
								$("#config_table tbody tr td:nth-child(2) span").html("")
								$('#decision_name').html("")
								CKEDITOR.instances['email_message'].setData("")
								CKEDITOR.instances['approval_decision_message_approve'].setData("")
								CKEDITOR.instances['approval_decision_message_reject'].setData("")
								$('#decision_purpose').html("")
								$('#decision_config').val('').trigger("change")
								$('#select2multiple').val('').trigger("change")
								$("#carouselExampleIndicators").css("display", "none")
								$("#select_conditionTable").val('').trigger("change")
								$(".filter-table").html("")
								$("#condition_name_append").html("")
								$("#condition_dropdown").empty();
							}
						}

						else if(shape=="ellipse"){
							$('#chartModal').modal('show')
							$('#chartModal').find('.modal-footer').attr('data-shapeid',state.cell.id)
							if(state.cell.style.search("shapeUniqueID")>0){
								element_id=state.cell.style.substr(state.cell.style.search("shapeUniqueID")).substr((state.cell.style.substr(state.cell.style.search("shapeUniqueID"))).search("=")+1)
								analysis_config_load(element_id)
							}
						}
						else if(shape=="shape=parallelogram"){
							$(".previewCustomTemplate").prop('disabled',true)
							$('#computationModal').modal('show')
							$('#computationModal').find('.modal-footer').attr('data-shapeid',state.cell.id)
							if(state.cell.style.search("shapeUniqueID")>0){
								element_id=state.cell.style.substr(state.cell.style.search("shapeUniqueID")).substr((state.cell.style.substr(state.cell.style.search("shapeUniqueID"))).search("=")+1)
								computation_config_load(element_id)
							}
						}
						else if(shape=="shape=document"){
							$(".previewCustomTemplate").prop('disabled',true)
							$('#documentModal').modal('show')
							$('#documentModal').find('.modal-footer').attr('data-shapeid',state.cell.id)
							if(state.cell.style.search("shapeUniqueID")>0){
								element_id=state.cell.style.substr(state.cell.style.search("shapeUniqueID")).substr((state.cell.style.substr(state.cell.style.search("shapeUniqueID"))).search("=")+1)
								upload_config_load(element_id)
							}
							else{
								$('#selectDocumentTable').val('').trigger("change");
								$('#selectDataconnector').val('').trigger("change");
								$('.selectComponents').find('.form-group').find('input[type=checkbox]').each(function(){
								  $(this)[0].checked=false
								});
								document.getElementById('select_All').checked=false;
								$('.selectComponents').css('display','none')
								$('#tabHeaderDocument').val('')
								$("#allow_comp_logic").prop("checked",false);
								$("#allow_map_column").prop("checked",false);
								$(".computedFieldMapperButton").attr('data-data_config','{}')
								$(".fieldUploadMapperButton").attr('data-data_config','[]')
								$("#allow_upload_compute").prop("checked",false);
								$("#allow_upload_compute").trigger('change')
								$('#upload_comp_importEle').empty();
								$('#upload_comp_table').val('').trigger("change");
								$('#upload_comp_model').val('').trigger("change");
							}
						}
						else if(shape=="shape=message"){
							$('#schedulerModal').modal('show')
							$('#schedulerModal').find('.modal-footer').attr('data-shapeid',state.cell.id)
							if(state.cell.style.search("shapeUniqueID")>0){
								element_id=state.cell.style.substr(state.cell.style.search("shapeUniqueID")).substr((state.cell.style.substr(state.cell.style.search("shapeUniqueID"))).search("=")+1)
								scheduler_config_load(element_id)
							}else{
								$("#name_email").val('').trigger("change")
								$("#selectTask").val('').trigger("change")
								$("#selectTask").val('').trigger("select2:select")
								$("#emailCard").css("display","none")
								$("#to_email").empty()
								$("#subject_email").val("").trigger("change")
								$("#trigger_email_for").val('[]').trigger("change")

								$("#approval_mailer_type_main").val("").trigger("change")
								$("#approval_mailer_type_main").val("").trigger("select2:select")
								$("#approval_email_list_main").empty()
								$("#approval_dynamic_email_list_main").empty()
								$("#approval_dynamic_type_table_main").val("").trigger("change")
								$("#approval_dynamic_type_table_main").val("").trigger("select2:select")

								$("#approval_mailer_type_main_cc").val("").trigger("change")
								$("#approval_mailer_type_main_cc").val("").trigger("select2:select")
								$("#approval_email_list_main_cc").empty()
								$("#approval_dynamic_email_list_main_cc").empty()
								$("#approval_dynamic_type_table_main_cc").val("").trigger("change")
								$("#approval_dynamic_type_table_main_cc").val("").trigger("select2:select")

								$("#approval_mailer_type_main_bcc").val("").trigger("change")
								$("#approval_mailer_type_main_bcc").val("").trigger("select2:select")
								$("#approval_email_list_main_bcc").empty()
								$("#approval_dynamic_email_list_main_bcc").empty()
								$("#approval_dynamic_type_table_main_bcc").val("").trigger("change")
								$("#approval_dynamic_type_table_main_bcc").val("").trigger("select2:select")

								$("#insert_attachment_main").attr("data-config","{}")
								$("#schedulerEmailIntervalStartDate").val("").trigger("change")
								$("#schedulerEmailIntervalEndDate").val("").trigger("change")
								$("#selectSchedulerEmailIntervalPeriodicity").val("").trigger("change")
								$("#selectSchedulerEmailIntervalTime").val("").trigger("change")
								$("#saveBasicfilter_schedule").attr('data-basicfilter-config', "[]")
								$("#selectSchedulerCondType").val("").trigger("change")
								$(".schedulerCondRow").empty()
								$("#selectSchRecDecision").empty()
								$("#selectSchRecAction").val("").trigger("change")
								CKEDITOR.instances['text_email'].setData("")
							}

						}
						else if(shape=="shape=cube"){
							$('#ocrModal').modal('show')
							$('#ocrModal').find('.modal-footer').attr('data-shapeid',state.cell.id)
							if(state.cell.style.search("shapeUniqueID")>0){
								element_id=state.cell.style.substr(state.cell.style.search("shapeUniqueID")).substr((state.cell.style.substr(state.cell.style.search("shapeUniqueID"))).search("=")+1)
								ocr_config_load(element_id);
							}
						} else if(shape=='shape=hexagon'){
							$('#pivotReportModal').modal('show')
							$('#pivotReportModal').find('.modal-footer').attr('data-shapeid',state.cell.id)

							if(state.cell.style.search("shapeUniqueID")>0){
								element_id=state.cell.style.substr(state.cell.style.search("shapeUniqueID")).substr((state.cell.style.substr(state.cell.style.search("shapeUniqueID"))).search("=")+1)
								pivotReport_config_load(element_id)
							}else{
								$('#tabHeaderPivotReport').val("").trigger('change')
								$('#pivot_report_name').val("").trigger('change')
								$('#pivot_category_name').val("").trigger('change')
							}
						} else if(shape=='shape=octagon'){
							if(state.cell.style.search("shapeUniqueID")>0){
								element_id=state.cell.style.substr(state.cell.style.search("shapeUniqueID")).substr((state.cell.style.substr(state.cell.style.search("shapeUniqueID"))).search("=")+1)
								$('#staticPage').find('.modal-footer').attr("data-element_id",element_id)
							} else {
								let = itemID = ("indNavPoint" + Math.random()).replace('.', "")
								state.cell.style = state.cell.style + "shapeUniqueID=" + itemID
								$('#staticPage').find('.modal-footer').attr("data-element_id",itemID)
							}
							$.ajax({
								url: window.location.pathname,
								data: {
								  'operation': "reloadConfig",
								  'element_id': $('#staticPage').find('.modal-footer').attr("data-element_id"),
								},
								type: "POST",
								dataType: "json",
								success: function (data) {
								  if(Object.keys(data["payload"]).length != 0) {
									static_page_html = data["html"]
									$("#templateName").val(data.payload.template_name).trigger("change")
									$("#displayType").val(data.payload.display_tab).trigger("change")
									$('#staticPage').modal("show");
									$("#templateName").prop("disabled",true);
								  } else {
									$("#templateName").val("").trigger("change")
									$("#displayType").val("").trigger("change")
									$('#staticPage').modal("show");
									$("#templateName").prop("disabled",false);
								  }
								},
								error: function() {
								  alert("Error")
								}
							  })

						} else if(shape=='shape=flowlink'){
							if(state.cell.style.search("shapeUniqueID")>0){
								element_id=state.cell.style.substr(state.cell.style.search("shapeUniqueID")).substr((state.cell.style.substr(state.cell.style.search("shapeUniqueID"))).search("=")+1)
								$('#flowLinkModal').find('.modal-footer').attr("data-element_id",element_id)
							} else {
								let = itemID = ("link" + Math.random()).replace('.', "")
								state.cell.style = state.cell.style + "shapeUniqueID=" + itemID
								$('#flowLinkModal').find('.modal-footer').attr("data-element_id",itemID)
							}
							if(![null,undefined].includes($('#flowLinkModal').find('.modal-footer').attr("data-element_id"))){
								$("#flowLinkModal").modal("show")
								$('#flowLinkModal').find('.modal-footer').attr('data-shapeid',state.cell.id)
								$.ajax({
									url: `/users/${app_code2}/${current_dev_mode2}/processGraphModule/`,
									data: {
									  'process_code': $("#graphContainerID").attr("data-process_code"),
									  'sub_process_name':$("#graphContainerID").attr("data-sub_process_name"),
									  'operation': 'fetchSubprocess_flow',
									},
									type: "POST",
									dataType: "json",
									success: function (data) {
									  $('#flowLinkSubprocess').empty();
									  for (i in data.data) {
										$('#flowLinkSubprocess').append(`<option value='${data.data[i]["item_code"]}'>${data.data[i]["item_name"]}</option>`);
									  }
									  reloadFlowLinkConfig($('#flowLinkModal').find('.modal-footer').attr("data-element_id"))
									},
									error: function(){
									  alert("Error")
									}
								});
							} else {
								alert("Link some element and configure the arrow")
							}
						} else if(shape=='shape=flowlinkto'){
							if(state.cell.style.search("shapeUniqueID")>0){
								element_id=state.cell.style.substr(state.cell.style.search("shapeUniqueID")).substr((state.cell.style.substr(state.cell.style.search("shapeUniqueID"))).search("=")+1)
								$('#flowLinkModalTo').find('.modal-footer').attr("data-element_id",element_id)
							} else {
								let = itemID = ("linkto" + Math.random()).replace('.', "")
								state.cell.style = state.cell.style + "shapeUniqueID=" + itemID
								$('#flowLinkModalTo').find('.modal-footer').attr("data-element_id",itemID)
							}
							if(![null,undefined].includes($('#flowLinkModalTo').find('.modal-footer').attr("data-element_id"))){
								$("#flowLinkModalTo").modal("show")
								$('#flowLinkModalTo').find('.modal-footer').attr('data-shapeid',state.cell.id)
								$.ajax({
									url: `/users/${app_code2}/${current_dev_mode2}/processGraphModule/`,
									data: {
									  'process_code': $("#graphContainerID").attr("data-process_code"),
									  'sub_process_name':$("#graphContainerID").attr("data-sub_process_name"),
									  'operation': 'fetchFlowLink',
									},
									type: "POST",
									dataType: "json",
									success: function (data) {
									  $('#flowLinkNameOption').empty();
									  for (i in data.payload) {
										$('#flowLinkNameOption').append(`<option data-pr_code="${data.payload[i]["related_item_code"]}" value='${data.payload[i]["element_id"]}'>${data.payload[i]["tab_header_name"]}</option>`);
									  }
									  reloadFlowLinkToConfig($('#flowLinkModalTo').find('.modal-footer').attr("data-element_id"))
									},
									error: function(){
									  alert("Error")
									}
								});
							}
						} else if (shape == "shape=flowcontrol") {
							$('#flowController').modal('show')
							let encoder = new mxCodec();
							let result = encoder.encode(graph.getModel());
							Graph.xml  = mxUtils.getXml(result);
							getParentChild(Graph.xml,graph,"flowController");
							$('#flowController').find('.modal-footer').attr('data-shapeid',state.cell.id)
							if(state.cell.style.search("shapeUniqueID")>0){
								element_id=state.cell.style.substr(state.cell.style.search("shapeUniqueID")).substr((state.cell.style.substr(state.cell.style.search("shapeUniqueID"))).search("=")+1)
								$('#flowController').find('.modal-footer').attr('data-element_id',element_id)
								flowControllerConfigLoad(element_id)
							} else {
								let = itemID1 = ("flowController" + Math.random()).replace('.', "");
								$('#flowController').find('.modal-footer').attr('data-element_id',itemID1);
								state.cell.style = state.cell.style + "shapeUniqueID=" + itemID1
							}
						}
						else{
							alert("Elements not assigned to this shape.")
						}

					})
				);
				state.view.graph.container.appendChild(img);
				this.images.push(img);
			} else {
				mxEdgeHandler.prototype.getSelectionPoints = function(	state	){
					var graph = state.view.graph;
					if(state.style.shape == "connector") {
						graph.connectionHandler.addListener(mxEvent.REMOVE, function(sender, evt)
										{
											graph.removeCells([state.cell]);
											mxEvent.consume(evt);
											this.destroy();
										})
						this.images = [];
						var img = mxUtils.createImage(mxClient.basePath+'/images/wrench.png');
								img.setAttribute('title', 'Configure line');
								img.style.position = 'absolute';
								img.style.cursor = 'pointer';
								img.style.width = '16px';
								img.style.height = '16px';
								img.style.left = (state.x) + 'px';
								img.style.top = (state.y) + 'px';
								mxEvent.addGestureListeners(img,
									mxUtils.bind(this, function(evt)
									{
										// Disables dragging the image
										mxEvent.consume(evt);
									})
								);
								mxEvent.addListener(img, 'click',
									mxUtils.bind(this, function(evt){
										var cellStyle_=state.visibleTargetState.cell.style;
										var indexSeparator_=cellStyle_.indexOf(';');
										var shape_=cellStyle_.substr(0,indexSeparator_);
										if(shape_=='shape=flowlink'){
											if(state.visibleTargetState.cell.style.search("shapeUniqueID")<0){
												cellShapeUniqueID = state.visibleTargetState.cell.style.search("shapeUniqueID")
												let itemID = ""
												if (cellShapeUniqueID < 0) {
												  itemID = ("link" + Math.random()).replace('.', "")
												  state.visibleTargetState.cell.style = state.visibleTargetState.cell.style + "shapeUniqueID=" + itemID
												}
												else {
												  itemID = (state.visibleTargetState.cell.style.substr(cellShapeUniqueID)).substr((cellSelected.style.substr(cellShapeUniqueID)).search("=") + 1)
												}
												$('#flowLinkModal').find('.modal-footer').attr('data-element_id',itemID)
											} else {
												element_id=state.visibleTargetState.cell.style.substr(state.visibleTargetState.cell.style.search("shapeUniqueID")).substr((state.cell.style.substr(state.cell.style.search("shapeUniqueID"))).search("=")+1)
												$('#flowLinkModal').find('.modal-footer').attr('data-element_id',element_id)
											}
										}
										var curr_element_id = state.cell.style.substr(state.cell.style.search("shapeUniqueID")).substr((state.cell.style.substr(state.cell.style.search("shapeUniqueID"))).search("=")+1).split(";")[0]
										$("#configureFlow").find(".modal-footer").find('.save').attr('data-id',`${curr_element_id}`);
										var element_id_source = state.visibleSourceState.cell.style.substr(state.visibleSourceState.cell.style.search("shapeUniqueID")).substr((state.visibleSourceState.cell.style.substr(state.visibleSourceState.cell.style.search("shapeUniqueID"))).search("=")+1)
										var element_id_dest = state.visibleTargetState.cell.style.substr(state.visibleTargetState.cell.style.search("shapeUniqueID")).substr((state.visibleTargetState.cell.style.substr(state.visibleTargetState.cell.style.search("shapeUniqueID"))).search("=")+1)

										if(element_id_source.trim() != ";" && element_id_dest.trim() != ";"){
										$("#configureFlow").modal('show');
										$("#configureFlow").find(".modal-footer").find('.save').attr('data-source_id',`${element_id_source}`);
										$("#configureFlow").find(".modal-footer").find('.save').attr('data-dest_id',`${element_id_dest}`);
										var source;
										var dest;
										$("#customValidation").closest(".col-4").css("display","flex");
										$("#emailValidation").closest(".col-4").css("display","none");
										$("#userValidation").closest(".col-4").css("display","flex");
										$(".flowUserValidation").css("display","flex");
										$("#dataValidation").closest(".col-4").css("display","flex");
										$("#autoRun").prop("checked",false)
										$("#elementHide").prop("checked",false)
										$("#autoRun").closest(".col-4").css("display","none");
										$("#nextElement").prop("disabled",false)
										$("#elementHide").prop("disabled",false)
										$("#autoRun").prop("disabled",false)
										if(element_id_dest.includes('parallelogram')) {
											$("#autoRun").closest(".col-4").css("display","flex");
										}
										$(".computationCondition").css("display","block")
										$("#userValidationCC").prop("checked",false);
										if(element_id_dest.includes('parallelogram') || element_id_dest.includes('ellipse')) {
											$(".flowBodyCardTo").css("display","flex")
											$(".flowBodyCard").removeClass("col-12")
											$(".flowBodyCard").addClass("col-12")
										} else {
											$(".flowBodyCardTo").css("display","none")
											$(".flowBodyCard").removeClass("col-12")
											$(".flowBodyCard").addClass("col-12")
											$("#customValidation").prop("checked",false);
										}
										if(element_id_source.includes('linkto')){
											$("#nextElement").prop("disabled",true)
											$("#elementHide").prop("disabled",true)
											$(".flowBodyCard").css("display","none")
											if(element_id_dest.includes('parallelogram')) {
												$(".computationCondition").css("display","block")
											} else {
												$(".computationCondition").css("display","none")
											}
										}
										if(element_id_dest.includes('link')) {
											$("#nextElement").prop("disabled",true)
											$("#elementHide").prop("disabled",true)
										}
										$(".flowUserValidationCC").css("display","none")
										if(element_id_source.includes('decision')){
											source = "Decision box"
											$("#emailValidation").closest(".col-4").css("display","flex");
											$("#customValidation").closest(".col-4").css("display","none");
											$("#dataValidation").closest(".col-4").css("display","none");
											$("#userValidation").closest(".col-4").css("display","none");
											$(".flowUserValidation").css("display","none");
											$("#userValidation").prop("checked",false)
											$(".computationCondition").css("display","none")
										} else if(element_id_source.includes('ellipse')){
											source = "Analysis"
										} else if(element_id_source.includes('parallelogram')){
											source = "Computation"
										} else if(element_id_source.includes('document')){
											source = "Upload"
										} else if(element_id_source.includes('process')){
											source = "List view"
										} else if(element_id_source.includes('whiteSpace')){
											source = "Create view"
										} else if(element_id_source.includes('link')){
											source = "Flow link To"
										}
										if(element_id_dest.includes('decision')){
											dest = "Decision box"
										} else if(element_id_dest.includes('ellipse')){
											dest = "Analysis"
										} else if(element_id_dest.includes('parallelogram')){
											dest = "Computation"
										} else if(element_id_dest.includes('document')){
											dest = "Upload"
										} else if(element_id_dest.includes('process')){
											dest = "List view"
										} else if(element_id_dest.includes('whiteSpace')){
											dest = "Create view"
										} else if(element_id_dest.includes('link')){
											dest = "Flow link"
										}
										$('#flowLinkModal').find('.modal-footer').attr("data-source_element_id",element_id_source)
										$('#flowLinkModal').find('.modal-footer').attr("data-source_element",source)
										$('#flowLinkModal').find('#flowLinkElement').empty()
										$('#flowLinkModal').find('#flowLinkElement').append(`<option value="${element_id_source}">${source}</option>`)
										$(".flowTable").val("").trigger("change");
										$(".flowTableCC").empty();
										$("#userValidation").prop("checked",false)
										$("#customValidation").prop("checked",true)
										ind = 0;
										$(".indFlow").each(function() {
										if(ind != 0){
											$(this).remove();
										}
										ind++
										})
										ind = 0;
										$(".indFlowTo").each(function() {
										if(ind != 0){
											$(this).remove();
										}
										ind++
										})
										ind = 0
										$(".indFlowCC").each(function() {
											if(ind != 0){
												$(this).remove();
											}
											ind++
										})
										$(".flowColumnCC").val("").trigger("change")
										$(".flowValueCC").empty();
										$("#configureFlow").find('.baseElementClass').find('.baseElement').html(source)
										$("#configureFlow").find('.baseElementClass').find('.nextElement').html(dest)
										flowConfigLoad(curr_element_id);
									}else{
										window.alert("Kindly save the configurations for the elements which are linked first and then try to configure the process flow.")
									}
									}
									)
								)
								state.view.graph.container.appendChild(img);
								this.images.push(img);
					}
				}
			}
			function getParentChild(graphXml,graph,id) {
				elementConnected = []
				elementConnectedTable = [];
				childConnected = [];
				childName = [];
				$.ajax({
					url: `/users/${app_code2}/${current_dev_mode2}/processGraphModule/`,
					data: {
						'operation': 'import_parent_elements_config_',
						'xml': graphXml,
					},
					type: "POST",
					dataType: "json",
					success: function (data) {
					for(let i=0;i< data.success.length;i++){
						if(data.success[i]['child'].length >0){
							for(let k=0;k<data.success[i]['child'].length;k++){
								let value_display = data.success[i]['child'][k]
								var cellSelected= graph.getModel().getCell($('#'+id).find('.modal-footer').attr('data-shapeid'));
								if(value_display == cellSelected['id']){
									elementConnected.push(data.success[i]['element_id'][k])
									if(data.success[i]['table'][data.success[i]['element_id']][0] != "[") {
										elementConnectedTable.push(data.success[i]['table'][data.success[i]['element_id']])
									} else {
										let table = JSON.parse(data.success[i]['table'][data.success[i]['element_id']]);
										for(let y = 0; y < table.length; y++){
											if(!elementConnectedTable.includes(elementConnectedTable[y])) {
												elementConnectedTable.push(table[y])
											}
										}
									}
								}
							}

						}

					}
					$("#modifyColumnTable").empty();
					for(let j = 0; j < elementConnectedTable.length; j++){
						$("#modifyColumnTable").append(`<option value="${elementConnectedTable[j]}">${elementConnectedTable[j]}</option>`);
					}
				},
					error: function () {alert('Error')}})

					$.ajax({
						url: `/users/${app_code2}/${current_dev_mode2}/processGraphModule/`,
						data: {
							'operation': 'import_child_elements_config_',
							'xml': graphXml,
						},
						type: "POST",
						dataType: "json",
						success: function (data) {
						for(let i=0;i< data.success.length;i++){
							if(data.success[i]['child'].length >0){
								for(let k=0;k<data.success[i]['child'].length;k++){
									let value_display = data.success[i]['child'][k]
									var cellSelected= graph.getModel().getCell($('#'+id).find('.modal-footer').attr('data-shapeid'));
									if(value_display == cellSelected['id']){
										childConnected.push(data.success[i]['element_id'][k])
										childName.push(data.success[i]['childName'][k])
									}
								}

							}

						}
						$(".augmentationNextElement").empty();
						for(let j = 0; j < childConnected.length; j++){
							$(".augmentationNextElement").append(`<option value="${childConnected[j]}">${childName[j]}</option>`);
						}
					},
						error: function () {alert('Error')}})
			}
		};

		mxIconSet.prototype.destroy = function()
		{
			if (this.images != null)
			{
				for (var i = 0; i < this.images.length; i++)
				{
					var img = this.images[i];
					img.parentNode.removeChild(img);
				}
			}

			this.images = null;
		};

//Function use to create HoverIcons

		function main(container,graph)
		{
				graph.setConnectable(true);
				// Defines the tolerance before removing the icons
				var iconTolerance = 20;
				// Shows icons if the mouse is over a cell
				graph.addMouseListener(
				{
				    currentState: null,
				    currentIconSet: null,
				    mouseDown: function(sender, me)
				    {
				    	// Hides icons on mouse down
			        	if (this.currentState != null)
			        	{
			          		this.dragLeave(me.getEvent(), this.currentState);

			          		this.currentState = null;
			        	}
				    },
				    mouseMove: function(sender, me)
				    {
				    	if (this.currentState != null && (me.getState() == this.currentState ||
				    		me.getState() == null))
				    	{
				    		var tol = iconTolerance;
				    		var tmp = new mxRectangle(me.getGraphX() - tol,
				    			me.getGraphY() - tol, 2 * tol, 2 * tol);

				    		if (mxUtils.intersects(tmp, this.currentState))
				    		{
				    			return;
				    		}
				    	}
						var tmp = graph.view.getState(me.getCell());

				    	// Ignores everything but vertices
						if (graph.isMouseDown || (tmp != null && !graph.getModel().isVertex(tmp.cell)))
						{
							tmp = null;
						}

				      	if (tmp != this.currentState)
				      	{
				        	if (this.currentState != null)
				        	{
				          		this.dragLeave(me.getEvent(), this.currentState);
			    			this.currentIconSet = null;
				        	}

			        		this.currentState = tmp;

				        	if (this.currentState != null)
				        	{
				          		this.dragEnter(me.getEvent(), this.currentState);

				        	}
				      	}
				    },
				    mouseUp: function(sender, me) { },
				    dragEnter: function(evt, state)
				    {
				    	if (this.currentIconSet == null)
				    	{
			    			this.currentIconSet = new mxIconSet(state);
				    	}
				    },
				    dragLeave: function(evt, state)
				    {
				    	if (this.currentIconSet != null)
				    	{
			    			this.currentIconSet.destroy();
			    			this.currentIconSet = null;
				    	}
				    }
				});


			};

/**
 * Constructs a new graph editor
 */

EditorUi = function (editor, container, lightbox) {
	mxEventSource.call(this);
	this.destroyFunctions = [];
	this.editor = editor || new Editor();
	this.container = container || document.getElementById('graphContainerID');

	var graph = this.editor.graph;
	graph.lightbox = lightbox;

	// Faster scrollwheel zoom is possible with CSS transforms
	if (graph.useCssTransforms) {
		this.lazyZoomDelay = 0;
	}

	// Pre-fetches submenu image or replaces with embedded image if supported
	if (mxClient.IS_SVG) {
		mxPopupMenu.prototype.submenuImage = 'data:image/gif;base64,R0lGODlhCQAJAIAAAP///zMzMyH5BAEAAAAALAAAAAAJAAkAAAIPhI8WebHsHopSOVgb26AAADs=';
	}
	else {
		new Image().src = mxPopupMenu.prototype.submenuImage;
	}

	// Pre-fetches connect image
	if (!mxClient.IS_SVG && mxConnectionHandler.prototype.connectImage != null) {
		new Image().src = mxConnectionHandler.prototype.connectImage.src;
	}

	// Disables graph and forced panning in chromeless mode
	if (this.editor.chromeless && !this.editor.editable) {
		this.footerHeight = 0;
		graph.isEnabled = function () { return false; };
		graph.panningHandler.isForcePanningEvent = function (me) {
			return !mxEvent.isPopupTrigger(me.getEvent());
		};
	}

	// Creates the user interface
	this.actions = new Actions(this);
	this.menus = this.createMenus();

	if (!graph.standalone) {
		this.createDivs();
		this.createUi();
		this.refresh();

		// Disables HTML and text selection
		var textEditing = mxUtils.bind(this, function (evt) {
			if (evt == null) {
				evt = window.event;
			}

			return graph.isEditing() || (evt != null && this.isSelectionAllowed(evt));
		});

		// Disables text selection while not editing and no dialog visible
		if (this.container == document.body) {
			this.menubarContainer.onselectstart = textEditing;
			this.menubarContainer.onmousedown = textEditing;
			this.toolbarContainer.onselectstart = textEditing;
			this.toolbarContainer.onmousedown = textEditing;
			this.diagramContainer.onselectstart = textEditing;
			this.diagramContainer.onmousedown = textEditing;
			this.sidebarContainer.onselectstart = textEditing;
			this.sidebarContainer.onmousedown = textEditing;
			this.formatContainer.onselectstart = textEditing;
			this.formatContainer.onmousedown = textEditing;
			this.footerContainer.onselectstart = textEditing;
			this.footerContainer.onmousedown = textEditing;

			if (this.tabContainer != null) {
				// Mouse down is needed for drag and drop
				this.tabContainer.onselectstart = textEditing;
			}
		}

		// And uses built-in context menu while editing
		if (!this.editor.chromeless || this.editor.editable) {
			// Allows context menu for links in hints
			var linkHandler = function (evt) {
				if (evt != null) {
					var source = mxEvent.getSource(evt);

					if (source.nodeName == 'A') {
						while (source != null) {
							if (source.className == 'geHint') {
								return true;
							}

							source = source.parentNode;
						}
					}
				}

				return textEditing(evt);
			};

			if (mxClient.IS_IE && (typeof (document.documentMode) === 'undefined' || document.documentMode < 9)) {
				mxEvent.addListener(this.diagramContainer, 'contextmenu', linkHandler);
			}
			else {
				// Allows browser context menu outside of diagram and sidebar
				this.diagramContainer.oncontextmenu = linkHandler;
			}
		}
		else {
			graph.panningHandler.usePopupTrigger = false;
		}

		// Contains the main graph instance inside the given panel
		graph.init(this.diagramContainer);

		// Improves line wrapping for in-place editor
		if (mxClient.IS_SVG && graph.view.getDrawPane() != null) {
			var root = graph.view.getDrawPane().ownerSVGElement;

			if (root != null) {
				root.style.position = 'absolute';
			}
		}

		// Creates hover icons
		this.hoverIcons = this.createHoverIcons();

		// Adds tooltip when mouse is over scrollbars to show space-drag panning option
		mxEvent.addListener(this.diagramContainer, 'mousemove', mxUtils.bind(this, function (evt) {
			var off = mxUtils.getOffset(this.diagramContainer);

			if (mxEvent.getClientX(evt) - off.x - this.diagramContainer.clientWidth > 0 ||
				mxEvent.getClientY(evt) - off.y - this.diagramContainer.clientHeight > 0) {
				this.diagramContainer.setAttribute('title', mxResources.get('panTooltip'));
			}
			else {
				this.diagramContainer.removeAttribute('title');
			}
		}));

		// Escape key hides dialogs, adds space+drag panning
		var spaceKeyPressed = false;

		// Overrides hovericons to disable while space key is pressed
		var hoverIconsIsResetEvent = this.hoverIcons.isResetEvent;

		this.hoverIcons.isResetEvent = function (evt, allowShift) {
			return spaceKeyPressed || hoverIconsIsResetEvent.apply(this, arguments);
		};

		this.keydownHandler = mxUtils.bind(this, function (evt) {
			if (evt.which == 32 /* Space */ && !graph.isEditing()) {
				spaceKeyPressed = true;
				this.hoverIcons.reset();
				graph.container.style.cursor = 'move';

				// Disables scroll after space keystroke with scrollbars
				if (!graph.isEditing() && mxEvent.getSource(evt) == graph.container) {
					mxEvent.consume(evt);
				}
			}
			else if (!mxEvent.isConsumed(evt) && evt.keyCode == 27 /* Escape */) {
				this.hideDialog(null, true);
			}
		});

		mxEvent.addListener(document, 'keydown', this.keydownHandler);

		this.keyupHandler = mxUtils.bind(this, function (evt) {
			graph.container.style.cursor = '';
			spaceKeyPressed = false;
		});

		mxEvent.addListener(document, 'keyup', this.keyupHandler);

		// Forces panning for middle and right mouse buttons
		var panningHandlerIsForcePanningEvent = graph.panningHandler.isForcePanningEvent;
		graph.panningHandler.isForcePanningEvent = function (me) {
			// Ctrl+left button is reported as right button in FF on Mac
			return panningHandlerIsForcePanningEvent.apply(this, arguments) ||
				spaceKeyPressed || (mxEvent.isMouseEvent(me.getEvent()) &&
					(this.usePopupTrigger || !mxEvent.isPopupTrigger(me.getEvent())) &&
					((!mxEvent.isControlDown(me.getEvent()) &&
						mxEvent.isRightMouseButton(me.getEvent())) ||
						mxEvent.isMiddleMouseButton(me.getEvent())));
		};

		// Ctrl/Cmd+Enter applies editing value except in Safari where Ctrl+Enter creates
		// a new line (while Enter creates a new paragraph and Shift+Enter stops)
		var cellEditorIsStopEditingEvent = graph.cellEditor.isStopEditingEvent;
		graph.cellEditor.isStopEditingEvent = function (evt) {
			return cellEditorIsStopEditingEvent.apply(this, arguments) ||
				(evt.keyCode == 13 && ((!mxClient.IS_SF && mxEvent.isControlDown(evt)) ||
					(mxClient.IS_MAC && mxEvent.isMetaDown(evt)) ||
					(mxClient.IS_SF && mxEvent.isShiftDown(evt))));
		};

		// Adds space+wheel for zoom
		var graphIsZoomWheelEvent = graph.isZoomWheelEvent;

		graph.isZoomWheelEvent = function () {
			return spaceKeyPressed || graphIsZoomWheelEvent.apply(this, arguments);
		};

		// Switches toolbar for text editing
		var textMode = false;
		var fontMenu = null;
		var sizeMenu = null;
		var nodes = null;

		var updateToolbar = mxUtils.bind(this, function () {
			if (this.toolbar != null && textMode != graph.cellEditor.isContentEditing()) {
				var node = this.toolbar.container.firstChild;
				var newNodes = [];

				while (node != null) {
					var tmp = node.nextSibling;

					if (mxUtils.indexOf(this.toolbar.staticElements, node) < 0) {
						node.parentNode.removeChild(node);
						newNodes.push(node);
					}

					node = tmp;
				}

				// Saves references to special items
				var tmp1 = this.toolbar.fontMenu;
				var tmp2 = this.toolbar.sizeMenu;

				if (nodes == null) {
					this.toolbar.createTextToolbar();
				}
				else {
					for (var i = 0; i < nodes.length; i++) {
						this.toolbar.container.appendChild(nodes[i]);
					}

					// Restores references to special items
					this.toolbar.fontMenu = fontMenu;
					this.toolbar.sizeMenu = sizeMenu;
				}

				textMode = graph.cellEditor.isContentEditing();
				fontMenu = tmp1;
				sizeMenu = tmp2;
				nodes = newNodes;
			}
		});

		var ui = this;

		// Overrides cell editor to update toolbar
		var cellEditorStartEditing = graph.cellEditor.startEditing;
		graph.cellEditor.startEditing = function () {
			cellEditorStartEditing.apply(this, arguments);
			updateToolbar();

			if (graph.cellEditor.isContentEditing()) {
				var updating = false;

				var updateCssHandler = function () {
					if (!updating) {
						updating = true;

						window.setTimeout(function () {
							var selectedElement = graph.getSelectedElement();
							var node = selectedElement;

							while (node != null && node.nodeType != mxConstants.NODETYPE_ELEMENT) {
								node = node.parentNode;
							}

							if (node != null) {
								var css = mxUtils.getCurrentStyle(node);

								if (css != null && ui.toolbar != null) {
									// Strips leading and trailing quotes
									var ff = css.fontFamily;

									if (ff.charAt(0) == '\'') {
										ff = ff.substring(1);
									}

									if (ff.charAt(ff.length - 1) == '\'') {
										ff = ff.substring(0, ff.length - 1);
									}

									ui.toolbar.setFontName(ff);
									ui.toolbar.setFontSize(parseInt(css.fontSize));
								}
							}

							updating = false;
						}, 0);
					}
				};

				mxEvent.addListener(graph.cellEditor.textarea, 'input', updateCssHandler)
				mxEvent.addListener(graph.cellEditor.textarea, 'touchend', updateCssHandler);
				mxEvent.addListener(graph.cellEditor.textarea, 'mouseup', updateCssHandler);
				mxEvent.addListener(graph.cellEditor.textarea, 'keyup', updateCssHandler);
				updateCssHandler();
			}
		};

		// Updates toolbar and handles possible errors
		var cellEditorStopEditing = graph.cellEditor.stopEditing;
		graph.cellEditor.stopEditing = function (cell, trigger) {
			try {
				cellEditorStopEditing.apply(this, arguments);
				updateToolbar();
			}
			catch (e) {
				ui.handleError(e);
			}
		};

		// Enables scrollbars and sets cursor style for the container
		graph.container.setAttribute('tabindex', '0');
		graph.container.style.cursor = 'default';

		// Workaround for page scroll if embedded via iframe
		if (window.self === window.top && graph.container.parentNode != null) {
			try {
				graph.container.focus();
			}
			catch (e) {
				// ignores error in old versions of IE
			}
		}

		// Keeps graph container focused on mouse down
		var graphFireMouseEvent = graph.fireMouseEvent;
		graph.fireMouseEvent = function (evtName, me, sender) {
			if (evtName == mxEvent.MOUSE_DOWN) {
				this.container.focus();
			}

			graphFireMouseEvent.apply(this, arguments);
		};

		// Configures automatic expand on mouseover
		graph.popupMenuHandler.autoExpand = true;

		// Installs context menu
		if (this.menus != null) {
			graph.popupMenuHandler.factoryMethod = mxUtils.bind(this, function (menu, cell, evt) {
				this.menus.createPopupMenu(menu, cell, evt);
			});
		}

		// Hides context menu
		mxEvent.addGestureListeners(document, mxUtils.bind(this, function (evt) {
			graph.popupMenuHandler.hideMenu();
		}));

		// Create handler for key events
		this.keyHandler = this.createKeyHandler(editor);

		// Getter for key handler
		this.getKeyHandler = function () {
			return keyHandler;
		};

		// Stores the current style and assigns it to new cells
		var styles = ['rounded', 'shadow', 'glass', 'dashed', 'dashPattern', 'comic', 'labelBackgroundColor'];
		var connectStyles = ['shape', 'edgeStyle', 'curved', 'rounded', 'elbow', 'comic', 'jumpStyle', 'jumpSize'];

		// Note: Everything that is not in styles is ignored (styles is augmented below)
		this.setDefaultStyle = function (cell) {
			try {
				var state = graph.view.getState(cell);

				if (state != null) {
					// Ignores default styles
					var clone = cell.clone();
					clone.style = ''
					var defaultStyle = graph.getCellStyle(clone);
					var values = [];
					var keys = [];

					for (var key in state.style) {
						if (defaultStyle[key] != state.style[key]) {
							values.push(state.style[key]);
							keys.push(key);
						}
					}

					// Handles special case for value "none"
					var cellStyle = graph.getModel().getStyle(state.cell);
					var tokens = (cellStyle != null) ? cellStyle.split(';') : [];

					for (var i = 0; i < tokens.length; i++) {
						var tmp = tokens[i];
						var pos = tmp.indexOf('=');

						if (pos >= 0) {
							var key = tmp.substring(0, pos);
							var value = tmp.substring(pos + 1);

							if (defaultStyle[key] != null && value == 'none') {
								values.push(value);
								keys.push(key);
							}
						}
					}

					// Resets current style
					if (graph.getModel().isEdge(state.cell)) {
						graph.currentEdgeStyle = {};
					}
					else {
						graph.currentVertexStyle = {}
					}

					this.fireEvent(new mxEventObject('styleChanged', 'keys', keys, 'values', values, 'cells', [state.cell]));
				}
			}
			catch (e) {
				this.handleError(e);
			}
		};

		this.clearDefaultStyle = function () {
			graph.currentEdgeStyle = mxUtils.clone(graph.defaultEdgeStyle);
			graph.currentVertexStyle = mxUtils.clone(graph.defaultVertexStyle);

			// Updates UI
			this.fireEvent(new mxEventObject('styleChanged', 'keys', [], 'values', [], 'cells', []));
		};

		// Keys that should be ignored if the cell has a value (known: new default for all cells is html=1 so
		// for the html key this effecticely only works for edges inserted via the connection handler)
		var valueStyles = ['fontFamily', 'fontSize', 'fontColor'];

		// Keys that always update the current edge style regardless of selection
		var alwaysEdgeStyles = ['edgeStyle', 'startArrow', 'startFill', 'startSize', 'endArrow',
			'endFill', 'endSize'];

		// Keys that are ignored together (if one appears all are ignored)
		var keyGroups = [['startArrow', 'startFill', 'startSize', 'sourcePerimeterSpacing',
			'endArrow', 'endFill', 'endSize', 'targetPerimeterSpacing'],
		['strokeColor', 'strokeWidth'],
		['fillColor', 'gradientColor'],
			valueStyles,
		['opacity'],
		['align'],
		['html']];

		// Adds all keys used above to the styles array
		for (var i = 0; i < keyGroups.length; i++) {
			for (var j = 0; j < keyGroups[i].length; j++) {
				styles.push(keyGroups[i][j]);
			}
		}

		for (var i = 0; i < connectStyles.length; i++) {
			if (mxUtils.indexOf(styles, connectStyles[i]) < 0) {
				styles.push(connectStyles[i]);
			}
		}

		// Implements a global current style for edges and vertices that is applied to new cells
		var insertHandler = function (cells, asText) {
			var model = graph.getModel();

			model.beginUpdate();
			try {
				for (var i = 0; i < cells.length; i++) {
					var cell = cells[i];

					var appliedStyles;

					if (asText) {
						// Applies only basic text styles
						appliedStyles = ['fontSize', 'fontFamily', 'fontColor'];
					}
					else {
						// Removes styles defined in the cell style from the styles to be applied
						var cellStyle = model.getStyle(cell);
						var tokens = (cellStyle != null) ? cellStyle.split(';') : [];
						appliedStyles = styles.slice();

						for (var j = 0; j < tokens.length; j++) {
							var tmp = tokens[j];
							var pos = tmp.indexOf('=');

							if (pos >= 0) {
								var key = tmp.substring(0, pos);
								var index = mxUtils.indexOf(appliedStyles, key);

								if (index >= 0) {
									appliedStyles.splice(index, 1);
								}

								// Handles special cases where one defined style ignores other styles
								for (var k = 0; k < keyGroups.length; k++) {
									var group = keyGroups[k];

									if (mxUtils.indexOf(group, key) >= 0) {
										for (var l = 0; l < group.length; l++) {
											var index2 = mxUtils.indexOf(appliedStyles, group[l]);

											if (index2 >= 0) {
												appliedStyles.splice(index2, 1);
											}
										}
									}
								}
							}
						}
					}

					// Applies the current style to the cell
					var edge = model.isEdge(cell);
					var current = (edge) ? graph.currentEdgeStyle : graph.currentVertexStyle;
					var newStyle = model.getStyle(cell);

					for (var j = 0; j < appliedStyles.length; j++) {
						var key = appliedStyles[j];
						var styleValue = current[key];

						if (styleValue != null && (key != 'shape' || edge)) {
							// Special case: Connect styles are not applied here but in the connection handler
							if (!edge || mxUtils.indexOf(connectStyles, key) < 0) {
								newStyle = mxUtils.setStyle(newStyle, key, styleValue);
							}
						}
					}

					model.setStyle(cell, newStyle);
				}
			}
			finally {
				model.endUpdate();
			}
		};

		graph.addListener('cellsInserted', function (sender, evt) {
			insertHandler(evt.getProperty('cells'));
		});

		graph.addListener('textInserted', function (sender, evt) {
			insertHandler(evt.getProperty('cells'), true);
		});

		graph.connectionHandler.addListener(mxEvent.CONNECT, function (sender, evt) {
			var cells = [evt.getProperty('cell')];

			if (evt.getProperty('terminalInserted')) {
				cells.push(evt.getProperty('terminal'));
			}

			insertHandler(cells);
		});

		this.addListener('styleChanged', mxUtils.bind(this, function (sender, evt) {
			// Checks if edges and/or vertices were modified
			var cells = evt.getProperty('cells');
			var vertex = false;
			var edge = false;

			if (cells.length > 0) {
				for (var i = 0; i < cells.length; i++) {
					vertex = graph.getModel().isVertex(cells[i]) || vertex;
					edge = graph.getModel().isEdge(cells[i]) || edge;

					if (edge && vertex) {
						break;
					}
				}
			}
			else {
				vertex = true;
				edge = true;
			}

			var keys = evt.getProperty('keys');
			var values = evt.getProperty('values');

			for (var i = 0; i < keys.length; i++) {
				var common = mxUtils.indexOf(valueStyles, keys[i]) >= 0;

				// Ignores transparent stroke colors
				if (keys[i] != 'strokeColor' || (values[i] != null && values[i] != 'none')) {
					// Special case: Edge style and shape
					if (mxUtils.indexOf(connectStyles, keys[i]) >= 0) {
						if (edge || mxUtils.indexOf(alwaysEdgeStyles, keys[i]) >= 0) {
							if (values[i] == null) {
								delete graph.currentEdgeStyle[keys[i]];
							}
							else {
								graph.currentEdgeStyle[keys[i]] = values[i];
							}
						}
						// Uses style for vertex if defined in styles
						else if (vertex && mxUtils.indexOf(styles, keys[i]) >= 0) {
							if (values[i] == null) {
								delete graph.currentVertexStyle[keys[i]];
							}
							else {
								graph.currentVertexStyle[keys[i]] = values[i];
							}
						}
					}
					else if (mxUtils.indexOf(styles, keys[i]) >= 0) {
						if (vertex || common) {
							if (values[i] == null) {
								delete graph.currentVertexStyle[keys[i]];
							}
							else {
								graph.currentVertexStyle[keys[i]] = values[i];
							}
						}

						if (edge || common || mxUtils.indexOf(alwaysEdgeStyles, keys[i]) >= 0) {
							if (values[i] == null) {
								delete graph.currentEdgeStyle[keys[i]];
							}
							else {
								graph.currentEdgeStyle[keys[i]] = values[i];
							}
						}
					}
				}
			}

			if (this.toolbar != null) {
				this.toolbar.setFontName(graph.currentVertexStyle['fontFamily'] || Menus.prototype.defaultFont);
				this.toolbar.setFontSize(graph.currentVertexStyle['fontSize'] || Menus.prototype.defaultFontSize);

				if (this.toolbar.edgeStyleMenu != null) {
					// Updates toolbar icon for edge style
					var edgeStyleDiv = this.toolbar.edgeStyleMenu.getElementsByTagName('div')[0];

					if (graph.currentEdgeStyle['edgeStyle'] == 'orthogonalEdgeStyle' && graph.currentEdgeStyle['curved'] == '1') {
						edgeStyleDiv.className = 'geSprite geSprite-curved';
					}
					else if (graph.currentEdgeStyle['edgeStyle'] == 'straight' || graph.currentEdgeStyle['edgeStyle'] == 'none' ||
						graph.currentEdgeStyle['edgeStyle'] == null) {
						edgeStyleDiv.className = 'geSprite geSprite-straight';
					}
					else if (graph.currentEdgeStyle['edgeStyle'] == 'entityRelationEdgeStyle') {
						edgeStyleDiv.className = 'geSprite geSprite-entity';
					}
					else if (graph.currentEdgeStyle['edgeStyle'] == 'elbowEdgeStyle') {
						edgeStyleDiv.className = 'geSprite geSprite-' + ((graph.currentEdgeStyle['elbow'] == 'vertical') ?
							'verticalelbow' : 'horizontalelbow');
					}
					else if (graph.currentEdgeStyle['edgeStyle'] == 'isometricEdgeStyle') {
						edgeStyleDiv.className = 'geSprite geSprite-' + ((graph.currentEdgeStyle['elbow'] == 'vertical') ?
							'verticalisometric' : 'horizontalisometric');
					}
					else {
						edgeStyleDiv.className = 'geSprite geSprite-orthogonal';
					}
				}

				if (this.toolbar.edgeShapeMenu != null) {
					// Updates icon for edge shape
					var edgeShapeDiv = this.toolbar.edgeShapeMenu.getElementsByTagName('div')[0];

					if (graph.currentEdgeStyle['shape'] == 'link') {
						edgeShapeDiv.className = 'geSprite geSprite-linkedge';
					}
					else if (graph.currentEdgeStyle['shape'] == 'flexArrow') {
						edgeShapeDiv.className = 'geSprite geSprite-arrow';
					}
					else if (graph.currentEdgeStyle['shape'] == 'arrow') {
						edgeShapeDiv.className = 'geSprite geSprite-simplearrow';
					}
					else {
						edgeShapeDiv.className = 'geSprite geSprite-connection';
					}
				}

				// Updates icon for optinal line start shape
				if (this.toolbar.lineStartMenu != null) {
					var lineStartDiv = this.toolbar.lineStartMenu.getElementsByTagName('div')[0];

					lineStartDiv.className = this.getCssClassForMarker('start',
						graph.currentEdgeStyle['shape'], graph.currentEdgeStyle[mxConstants.STYLE_STARTARROW],
						mxUtils.getValue(graph.currentEdgeStyle, 'startFill', '1'));
				}

				// Updates icon for optinal line end shape
				if (this.toolbar.lineEndMenu != null) {
					var lineEndDiv = this.toolbar.lineEndMenu.getElementsByTagName('div')[0];

					lineEndDiv.className = this.getCssClassForMarker('end',
						graph.currentEdgeStyle['shape'], graph.currentEdgeStyle[mxConstants.STYLE_ENDARROW],
						mxUtils.getValue(graph.currentEdgeStyle, 'endFill', '1'));
				}
			}
		}));

		// Update font size and font family labels
		if (this.toolbar != null) {
			var update = mxUtils.bind(this, function () {
				var ff = graph.currentVertexStyle['fontFamily'] || 'Helvetica';
				var fs = String(graph.currentVertexStyle['fontSize'] || '12');
				var state = graph.getView().getState(graph.getSelectionCell());

				if (state != null) {
					ff = state.style[mxConstants.STYLE_FONTFAMILY] || ff;
					fs = state.style[mxConstants.STYLE_FONTSIZE] || fs;

					if (ff.length > 10) {
						ff = ff.substring(0, 8) + '...';
					}
				}

				this.toolbar.setFontName(ff);
				this.toolbar.setFontSize(fs);
			});

			graph.getSelectionModel().addListener(mxEvent.CHANGE, update);
			graph.getModel().addListener(mxEvent.CHANGE, update);
		}

		// Makes sure the current layer is visible when cells are added
		graph.addListener(mxEvent.CELLS_ADDED, function (sender, evt) {
			var cells = evt.getProperty('cells');
			var parent = evt.getProperty('parent');

			if (graph.getModel().isLayer(parent) && !graph.isCellVisible(parent) && cells != null && cells.length > 0) {
				graph.getModel().setVisible(parent, true);
			}
		});

		// Global handler to hide the current menu
		this.gestureHandler = mxUtils.bind(this, function (evt) {
			if (this.currentMenu != null && mxEvent.getSource(evt) != this.currentMenu.div) {
				this.hideCurrentMenu();
			}
		});

		mxEvent.addGestureListeners(document, this.gestureHandler);

		// Updates the editor UI after the window has been resized or the orientation changes
		// Timeout is workaround for old IE versions which have a delay for DOM client sizes.
		// Should not use delay > 0 to avoid handle multiple repaints during window resize
		this.resizeHandler = mxUtils.bind(this, function () {
			window.setTimeout(mxUtils.bind(this, function () {
				if (this.editor.graph != null) {
					this.refresh();
				}
			}), 0);
		});

		mxEvent.addListener(window, 'resize', this.resizeHandler);

		this.orientationChangeHandler = mxUtils.bind(this, function () {
			this.refresh();
		});

		mxEvent.addListener(window, 'orientationchange', this.orientationChangeHandler);

		// Workaround for bug on iOS see
		// http://stackoverflow.com/questions/19012135/ios-7-ipad-safari-landscape-innerheight-outerheight-layout-issue
		if (mxClient.IS_IOS && !window.navigator.standalone) {
			this.scrollHandler = mxUtils.bind(this, function () {
				window.scrollTo(0, 0);
			});

			mxEvent.addListener(window, 'scroll', this.scrollHandler);
		}

		/**
		 * Sets the initial scrollbar locations after a file was loaded.
		 */
		this.editor.addListener('resetGraphView', mxUtils.bind(this, function () {
			this.resetScrollbars();
		}));

		/**
		 * Repaints the grid.
		 */
		this.addListener('gridEnabledChanged', mxUtils.bind(this, function () {
			graph.view.validateBackground();
		}));

		this.addListener('backgroundColorChanged', mxUtils.bind(this, function () {
			graph.view.validateBackground();
		}));

		/**
		 * Repaints the grid.
		 */
		graph.addListener('gridSizeChanged', mxUtils.bind(this, function () {
			if (graph.isGridEnabled()) {
				graph.view.validateBackground();
			}
		}));

		// Resets UI, updates action and menu states
		this.editor.resetGraph();
	}

	this.init();

	if (!graph.standalone) {
		this.open();
	}

	function fetchBlockSchedulerDetails(blockElementId, blockData) {
		let schedulerType = $('#selectSchedulerType').val();
		let blockType = elementType(blockElementId);
		if (schedulerType === 'scheduleFlow') {
			$('#blockTriggerDetailContainer').css('display', 'none');
			$('#blockActionDetailContainer').css('display', 'none');
			$('#blockRetryDetailsContainer').css('display', 'none');
			$('#intervalExecutionDetailsContainer').css('display', 'none');
			if (blockData["data-previousElement"] != '') {
				let parentElement = blockData["data-previousElement"];
				let parentBlockType = elementType(parentElement);
				$('#selectSchedulerTriggerAction').empty();
				if (parentBlockType == 'create_view') {
					$('#selectSchedulerTriggerAction').append('<option value="save">Save Record</option>');
				} else if (parentBlockType == 'list_view') {
					$('#selectSchedulerTriggerAction').append('<option value="upload">Upload Data</option>');
					$('#selectSchedulerTriggerAction').append('<option value="update">Update Record</option>');
					$('#selectSchedulerTriggerAction').append('<option value="delete">Delete Record</option>');
				} else if (parentBlockType == 'decision_box') {
					$('#selectSchedulerTriggerAction').append('<option value="approve">Approve Record</option>');
					$('#selectSchedulerTriggerAction').append('<option value="reject">Reject Record</option>');
				} else if (parentBlockType == 'data_connector') {
					$('#selectSchedulerTriggerAction').append('<option value="upload">Upload Data</option>');
				} else if (parentBlockType == 'computation') {
					$('#selectSchedulerTriggerAction').append('<option value="run_model">Model Run</option>');
				}
			}
		} else {
			$('#blockTriggerDetailContainer').css('display', 'block');
			$('#blockActionDetailContainer').css('display', 'block');
			$('#blockRetryDetailsContainer').css('display', '');
			if (blockData["data-previousElement"] == '') {
				$('#selectSchedulerTrigger').val('interval').trigger('change');
				$('#selectSchedulerTrigger').val('interval').trigger('select2:select');
				$('#selectSchedulerTrigger').find('option[value="trigger"]').prop('disabled', true);
				$('#selectSchedulerTrigger').find('option[value="trigger"]').attr('disabled', true);
			} else {
				$('#selectSchedulerTrigger').find('option[value="trigger"]').prop('disabled', false);
			};
		};

		if (blockType == 'computation') {
			$('#selectSchedulerAction').empty();
			$('#selectSchedulerAction').append('<option value="run_model">Execute Computation Model</option>');
			$('#blockActionDetailContainer').find('small').css('display', 'none');
		} else if (blockType == 'decision_box') {
			$('#selectSchedulerAction').empty();
			$('#selectSchedulerAction').append('<option value="approve">Approve All Records</option>');
			$('#selectSchedulerAction').append('<option value="reject">Reject All Records</option>');
			$('#selectSchedulerAction').append('<option value="approve_with_condition">Approve Records Satisfying Condition</option>');
			$('#selectSchedulerAction').append('<option value="reject_with_condition">Reject Records Satisfying Condition</option>');
			$('#blockActionDetailContainer').find('small').css('display', 'none');

		} else {
			$('#selectSchedulerAction').empty();
			$('#blockActionDetailContainer').find('small').css('display', 'block');
		};
		let existingConfig = $('#flowDetailBodyNew').attr('data-config');
		if (existingConfig && existingConfig != '{}') {
			existingConfig = JSON.parse(existingConfig);
			existingConfig = existingConfig[blockElementId];
			if (existingConfig) {
				$('#selectSchedulerTrigger').val(existingConfig['schedulerTrigger']).trigger('change');
				$('#selectSchedulerTrigger').val(existingConfig['schedulerTrigger']).trigger('select2:select');
				$('#selectSchedulerAction').val(existingConfig['schedulerAction']).trigger('change');
				$('#selectSchedulerAction').val(existingConfig['schedulerAction']).trigger('select2:select');
				$('#selectSchedulerRetry').val(existingConfig['noOfRetries'])
				$('#selectSchedulerRetryInterval').val(existingConfig['intervalBetweenRetries'])
				if (existingConfig['schedulerTrigger'] == "interval") {
					$('#schedulerIntervalStartDate').val(existingConfig['blockTriggerConfig']['startDate']).trigger('change');
					$('#schedulerIntervalEndDate').val(existingConfig['blockTriggerConfig']['endDate']).trigger('change');
					$('#selectSchedulerIntervalPeriodicity').val(existingConfig['blockTriggerConfig']['intervalPeriod']).trigger('select2:select');
					$('#selectSchedulerIntervalPeriodicity').val(existingConfig['blockTriggerConfig']['intervalPeriod']).trigger('change');
					$('#selectSchedulerIntervalTime').val(existingConfig['blockTriggerConfig']['intervalTime']).trigger('change');
					if (existingConfig['blockTriggerConfig']['intervalFrequency']) {
						$('#selectSchedulerIntervalFrequency').val(existingConfig['blockTriggerConfig']['intervalFrequency']).trigger('change');
					};
				} else {
					$('#selectSchedulerTriggerAction').val(existingConfig['blockTriggerConfig']['schedulerTriggerAction']);
				}
				if (existingConfig['schedulerActionCondition']) {
					$('#actionConditionDetailButton').attr('data-config', JSON.stringify(existingConfig['schedulerActionCondition']));
				}
			}
		}

		$('#blockDetailContainer').css('display', 'block');
	}

	$('#addBlockJob').off('click').on('click', function() {
		let count = $('#additionalJobConfigContainer > .additionalJobDetails').length;
		$('#additionalJobConfigContainer').append(`
		<br>
		<div class="additionalJobDetails col-12">
			<div class="row">
                <div class="form-group col-5 ml-1 mr-1">
                  <label for="selectSchedulerTrigger">Execute Action On:</label>
                  <select class="select2 form-control selectSchedulerTrigger" name="selectSchedulerTrigger">
                    <option value="trigger">Successful Completion of Preceding Element's Action</option>
                    <option value="interval">An Interval of Time (Auto Run)</option>
                  </select>
                </div>
                <div class="form-group col-5 ml-1 mr-1 blockActionDetailContainer">
                  <label for="selectSchedulerAction">Action To Be Performed:</label>
                  <select class="select2 form-control selectSchedulerAction" name="selectSchedulerAction">
                    <option value="" selected>Select Action</option>
                  </select>
                  <small class="form-text" style="display: none;">Selected block doesnt support any action that can be scheduled.</small>
                </div>
                <div class="form-group col-1 ml-1 mr-1 blockActionConditionDetailContainer" style="margin: auto;">
                  <button type="button" class="btn btn-secondary rounded actionConditionDetailButton" data-index="${count}"><i class="fas fa-filter"></i></button>
                </div>
              </div>
              <div class="row triggerExecutionDetailsContainer">
                <div class="form-group col-4">
                  <label for="selectSchedulerTriggerAction">Preceding Element's Action:</label>
                  <select class="select2 form-control selectSchedulerTriggerAction" name="selectSchedulerTriggerAction">
                    <option value="" selected>Select Action</option>
                  </select>
                </div>
              </div>
              <br>
              <div class="row blockRetryDetailsContainer">
                <div class="form-group col-4">
                  <label for="selectSchedulerRetry">Retry Executing Action For:</label>
                  <input type="number" class="form-control numberinput selectSchedulerRetry" step=1 min=0 name="selectSchedulerRetry" placeholder="Number of Retries">
                </div>
                <div class="form-group col-4">
                  <label for="selectSchedulerRetryInterval">Interval Between Retries (in minutes):</label>
                  <input type="number" class="form-control numberinput selectSchedulerRetryInterval" step=1 min=0 name="selectSchedulerRetryInterval" placeholder="Interval Between Retries">
                </div>
              </div>
              <br>
              <div class="row intervalExecutionDetailsContainer" style="display:none;">
                <div class="form-group col-3">
                  <label for="schedulerIntervalStartDate">Start Date:</label>
                  <div class="input-group date">
                    <input type="date" class="form-control schedulerIntervalStartDate" name="schedulerIntervalStartDate" placeholder="DD-MM-YYYY">
                  </div>
                </div>
                <div class="form-group col-3">
                  <label for="schedulerIntervalEndDate">End Date:</label>
                  <div class="input-group date">
                    <input type="date" class="form-control schedulerIntervalEndDate" name="schedulerIntervalEndDate" placeholder="DD-MM-YYYY">
                  </div>
                </div>
                <div class="form-group col-3">
                  <label for="selectSchedulerIntervalPeriodicity">Period of Execution:</label>
                  <select class="select2 form-control selectSchedulerIntervalPeriodicity" name="selectSchedulerIntervalPeriodicity">
                    <option value="" selected>Select Period</option>
                    <option value="Every N Minutes">Every N Minutes</option>
                    <option value="Hourly">Every N Hours</option>
                    <option value="Daily">Daily</option>
                    <option value="Weekly">Weekly</option>
                    <option value="Monthly">Monthly</option>
                    <option value="Monthly/5th day">Monthly/5th day</option>
                    <option value="Quarterly">Quarterly</option>
                    <option value="Pre-Quarterly">Pre-Quarterly</option>
                    <option value="Yearly">Yearly</option>
                  </select>
                </div>
                <div class="form-group col-3 schedulerIntervalTimeContainer">
                  <label for="selectSchedulerIntervalTime">Time of Execution:</label>
                  <div class="input-group date">
                    <input type="time" class="form-control selectSchedulerIntervalTime" name="selectSchedulerIntervalTime" placeholder="HH:MM">
                  </div>
                </div>
                <div class="form-group col-3 schedulerIntervalFrequencyContainer" style="display: none;">
                  <label for="selectSchedulerIntervalFrequency">Interval:</label>
                  <input type="number" step="1" min="1" max="60" class="form-control numberinput selectSchedulerIntervalFrequency" name="selectSchedulerIntervalFrequency">
                </div>
              </div>
		</div>
		`);
		let addedJobBlock = $('#additionalJobConfigContainer > .additionalJobDetails').eq(-1)
		addedJobBlock.find('.select2').select2();
		$('#selectSchedulerAction > option').each(function(){
			addedJobBlock.find('.selectSchedulerAction').append(`
			<option value='${$(this).val()}'>${$(this).text()}</option>
			`);
		});
		addedJobBlock.find('.selectSchedulerAction').on('select2:select', function() {
			if (['approve_with_condition', 'reject_with_condition'].includes($(this).val())) {
				addedJobBlock.find('.blockActionConditionDetailContainer').css('display', '');
			} else {
				addedJobBlock.find('.blockActionConditionDetailContainer').css('display', 'none');
			}
		});
		addedJobBlock.find('.selectSchedulerTrigger').on('select2:select', function(){
			if ($(this).val() == "interval") {
				addedJobBlock.find('.intervalExecutionDetailsContainer').css('display', '');
				addedJobBlock.find('.triggerExecutionDetailsContainer').css('display', 'none');
			} else {
				let blockData = JSON.parse($('#flowDetailBodyNew').attr('data-currentElement'));
				let parentElement = blockData["data-previousElement"];
				let parentBlockType = elementType(parentElement);
				addedJobBlock.find('.selectSchedulerTriggerAction').empty();
				if (parentBlockType == 'create_view') {
					addedJobBlock.find('.selectSchedulerTriggerAction').append('<option value="save">Save Record</option>');
				} else if (parentBlockType == 'list_view') {
					addedJobBlock.find('.selectSchedulerTriggerAction').append('<option value="upload">Upload Data</option>');
					addedJobBlock.find('.selectSchedulerTriggerAction').append('<option value="update">Update Record</option>');
					addedJobBlock.find('.selectSchedulerTriggerAction').append('<option value="delete">Delete Record</option>');
				} else if (parentBlockType == 'decision_box') {
					addedJobBlock.find('.selectSchedulerTriggerAction').append('<option value="approve">Approve Record</option>');
					addedJobBlock.find('.selectSchedulerTriggerAction').append('<option value="reject">Reject Record</option>');
				} else if (parentBlockType == 'data_connector') {
					addedJobBlock.find('.selectSchedulerTriggerAction').append('<option value="upload">Upload Data</option>');
				} else if (parentBlockType == 'computation') {
					addedJobBlock.find('.selectSchedulerTriggerAction').append('<option value="run_model">Model Run</option>');
				}
				addedJobBlock.find('.intervalExecutionDetailsContainer').css('display', 'none');
				addedJobBlock.find('.triggerExecutionDetailsContainer').css('display', 'block');
			};
		});
		addedJobBlock.find(".selectSchedulerIntervalPeriodicity").on('select2:select', function () {
			if (["Every N Minutes", "Hourly"].includes($(this).val())) {
				addedJobBlock.find('.schedulerIntervalFrequencyContainer').css('display', '');
				let currentDate = new Date();
				currentTime = `${currentDate.getHours()}:${currentDate.getMinutes()}`
				addedJobBlock.find('.selectSchedulerIntervalTime').val(currentTime).trigger('change');
				if ($(this).val() == "Every N Minutes") {
					addedJobBlock.find('.selectSchedulerIntervalFrequency').attr('placeholder', 'N(1-59) Minutes')
				} else {
					addedJobBlock.find('.selectSchedulerIntervalFrequency').attr('placeholder', 'N(1-23) Hours')
				}
			} else {
				addedJobBlock.find('.schedulerIntervalFrequencyContainer').css('display', 'none');
				addedJobBlock.find('.selectSchedulerIntervalFrequency').attr('placeholder','');
			}
		});
		addedJobBlock.find('.actionConditionDetailButton').on('click', actionConditionHandler);

	});

	$('#selectSchedulerAction').on('select2:select', function() {
		if (['approve_with_condition', 'reject_with_condition'].includes($(this).val())) {
			$('#blockActionConditionDetailContainer').css('display', '');
		} else {
			$('#blockActionConditionDetailContainer').css('display', 'none');
		}
	});

	$('#actionConditionDetailButton').on('click', actionConditionHandler);

	function actionConditionHandler() {
		let existingConditionConfig = $(this).attr('data-config');
		if ($(this).hasClass('actionConditionDetailButton')) {
			let index = $(this).attr('data-index');
			$('#saveSchedulerActionConditions').attr('data-add-index', index);
		} else {
			$('#saveSchedulerActionConditions').removeAttr('data-add-index');
		}
		if (existingConditionConfig) {
			existingConditionConfig = JSON.parse(existingConditionConfig);
			if (existingConditionConfig["approval_conditions"]) {
				$('#schedulerApprovalFilterTable').attr('data-config', JSON.stringify(existingConditionConfig["approval_conditions"]));
			}
			if (existingConditionConfig["underlying_table_conditions"]) {
				$('#schedulerUnderlyingFilterTable').attr('data-config', JSON.stringify(existingConditionConfig["underlying_table_conditions"]));
				if (existingConditionConfig['underlying_table']) {
					$('#selectUnderlyingTable').val(existingConditionConfig['underlying_table']).trigger('select2:select');
					$('#selectUnderlyingTable').val(existingConditionConfig['underlying_table']).trigger('change');
				}
			}
		}
		$.ajax({
			url: window.location.pathname,
			data: {
			  'model_name': 'ApprovalTable',
			  'operation': 'conditional_table',
			},
			type: "POST",
			dataType: "json",
			success: function (data) {
				$("#schedulerActionApprovalFilter").empty();
				var label_column = data.label_columns
				for (const [key, value] of Object.entries(label_column)) {
					$("#schedulerActionApprovalFilter").append('<li class="dropdown-item"><a href="javascript:void(0)" class="schedulerApprovalFilterBtn" style="display:block;" name=' + key + '>' + value + '</a></li>');
				}
				$('.schedulerApprovalFilterBtn').click(function(){
					var name = $(this).attr('name');
					var STRING = data.form_fields[name];
					$('#schedulerApprovalFilterTable').append(STRING)
					$('#schedulerApprovalFilterTable').find('tr').eq(-1).find("td").eq(1).off('select2:select').on("select2:select",function(){
						$('#schedulerApprovalFilterTable').find('tr').eq(-1).find("td").eq(2).find('div').eq(0).find('select').eq(0).empty()
					})
					$('#schedulerApprovalFilterTable').find('tr').eq(-1).find("td").eq(3).remove();
					let colDType = $('#schedulerApprovalFilterTable').find('tr').eq(-1).find('input').attr('type');
					$('#schedulerApprovalFilterTable').find('tr').eq(-1).append(
						`
						<td class="dt-center">
						<div class="form-group" style="max-width:25em;">
						<input type="text" name=${name} class="form-control textinput" placeholder="Constraint name" data-type="${colDType}"/>
						</div>
						</td>

						<td class="dt-center">
						<div class="form-group" style="max-width:25em;">
						<input type="text" name=${name} class="form-control textinput" placeholder="Rule set" data-type="${colDType}"/>
						</div>
						</td>
						`
					);
					$('.remove_filter').on('click', function(){
						$(this).closest("tr").remove();
					});

					$('#schedulerApprovalFilterTable:last-child').find("select").each(function () {
						$(this).select2()
					});

				});
				// Existing config check
				if($('#schedulerApprovalFilterTable').attr('data-config')) {
					let existingConfig = JSON.parse($('#schedulerApprovalFilterTable').attr('data-config'));
					for (let cond of existingConfig) {
						let name = cond['column_name'];
						$("#schedulerActionApprovalFilter").find(`a[name='${name}'].schedulerApprovalFilterBtn`).trigger('click');
						let addedRow = $('#schedulerApprovalFilterTable').find('tr').eq(-1);
						addedRow.find('select').eq(0).val(cond['condition']).trigger('select2:select');
						addedRow.find('select').eq(0).val(cond['condition']).trigger('change');
						addedRow.find('input').eq(0).val(cond['input_value']).trigger('change');
						addedRow.find('input').eq(-2).val(cond['constraintName']).trigger('change');
						addedRow.find('input').eq(-1).val(cond['ruleSet']).trigger('change');
					}
				}
			},
			error: function() {
				Swal.fire({icon: 'error',text: 'Error! Please try again.'});
			}
		});
		$('#schedulerConditionConfigModal').modal('show');
	}

	$('#selectUnderlyingTable').on('select2:select', function(){
		$.ajax({
			url: window.location.pathname,
			data: {
			  'model_name': $(this).val(),
			  'operation': 'conditional_table',
			},
			type: "POST",
			dataType: "json",
			success: function (data) {
				$("#schedulerActionUnderlyingFilter").empty();
				var label_column = data.label_columns
				for (const [key, value] of Object.entries(label_column)) {
					$("#schedulerActionUnderlyingFilter").append('<li class="dropdown-item"><a href="javascript:void(0)" class="schedulerFilterBtn" style="display:block;" name=' + key + '>' + value + '</a></li>');
				}
				$('.schedulerFilterBtn').click(function(){
					var name = $(this).attr('name');
					var STRING = data.form_fields[name];
					$('#schedulerUnderlyingFilterTable').append(STRING)
					$('#schedulerUnderlyingFilterTable').find('tr').eq(-1).find("td").eq(1).off('select2:select').on("select2:select",function(){
						$('#schedulerUnderlyingFilterTable').find('tr').eq(-1).find("td").eq(2).find('div').eq(0).find('select').eq(0).empty()
					})
					$('#schedulerUnderlyingFilterTable').find('tr').eq(-1).find("td").eq(3).remove();
					let colDType = $('#schedulerUnderlyingFilterTable').find('tr').eq(-1).find('input').attr('type');
					$('#schedulerUnderlyingFilterTable').find('tr').eq(-1).append(
						`
						<td class="dt-center">
						<div class="form-group" style="max-width:25em;">
						<input type="text" name=${name} class="form-control textinput" placeholder="Constraint name" data-type="${colDType}"/>
						</div>
						</td>

						<td class="dt-center">
						<div class="form-group" style="max-width:25em;">
						<input type="text" name=${name} class="form-control textinput" placeholder="Rule set" data-type="${colDType}"/>
						</div>
						</td>
						`
					);
					$('.remove_filter').on('click', function(){
						$(this).closest("tr").remove();
					});

					$('#schedulerUnderlyingFilterTable:last-child').find("select").each(function () {
						$(this).select2()
					})
				});
				// Existing config check
				if($('#schedulerUnderlyingFilterTable').attr('data-config')) {
					let existingConfig = JSON.parse($('#schedulerUnderlyingFilterTable').attr('data-config'));
					for (let cond of existingConfig) {
						let name = cond['column_name'];
						$("#schedulerActionApprovalFilter").find(`a[name='${name}'].schedulerFilterBtn`).trigger('click');
						let addedRow = $('#schedulerUnderlyingFilterTable').find('tr').eq(-1);
						addedRow.find('select').eq(0).val(cond['condition']).trigger('select2:select');
						addedRow.find('select').eq(0).val(cond['condition']).trigger('change');
						addedRow.find('input').eq(0).val(cond['input_value']).trigger('change');
						addedRow.find('input').eq(-2).val(cond['constraintName']).trigger('change');
						addedRow.find('input').eq(-1).val(cond['ruleSet']).trigger('change');
					}
				}
			},
			error: function() {
				Swal.fire({icon: 'error',text: 'Error! Please try again.'});
			}
		});
	});

	$('#saveSchedulerActionConditions').on('click', function(){
		let filterConditions = {};
		// underlying Table Filters
		let underlyingTableFilters = [];
		$('#schedulerUnderlyingFilterTable').find('tr').each(function(){
			let conditionObject = {};
			conditionObject['column_name'] = $(this).find('select').attr("name");
			conditionObject['condition'] = $(this).find('select').eq(0).val();
			conditionObject['input_value'] = $(this).find('input').eq(0).val();
			conditionObject['type'] = $(this).find('input').eq(0).attr('type');
			conditionObject['constraintName'] = $(this).find('input').eq(-2).val();
			conditionObject['ruleSet'] = $(this).find('input').eq(-1).val();
			underlyingTableFilters.push(conditionObject);
		});
		filterConditions['underlying_table_conditions'] = underlyingTableFilters;
		filterConditions['underlying_table'] = $('#selectUnderlyingTable').val();
		// Approval Filters
		let approvalTableFilters = [];
		$('#schedulerApprovalFilterTable').find('tr').each(function(){
			let conditionObject = {};
			conditionObject['column_name'] = $(this).find('select').attr("name");
			conditionObject['condition'] = $(this).find('select').eq(0).val();
			conditionObject['input_value'] = $(this).find('input').eq(0).val();
			conditionObject['constraintName'] = $(this).find('input').eq(-2).val();
			conditionObject['ruleSet'] = $(this).find('input').eq(-1).val();
			approvalTableFilters.push(conditionObject);
		});
		filterConditions['approval_conditions'] = approvalTableFilters;
		let addIndex = $('#saveSchedulerActionConditions').attr('data-add-index');
		if (addIndex) {
			$('#additionalJobConfigContainer > .additionalJobDetails').eq(Number(addIndex)).find('.actionConditionDetailButton').attr('data-config', JSON.stringify(filterConditions));
		} else {
			$('#actionConditionDetailButton').attr('data-config', JSON.stringify(filterConditions));
		}
		$('#schedulerConditionConfigModal').modal('hide');
	});

	$("#selectSchedulerIntervalPeriodicity").on('select2:select', function () {
		if (["Every N Minutes", "Hourly"].includes($(this).val())) {
			$('#schedulerIntervalFrequencyContainer').css('display', '');
			let currentDate = new Date();
			currentTime = `${currentDate.getHours()}:${currentDate.getMinutes()}`
			$('#selectSchedulerIntervalTime').val(currentTime).trigger('change');
			if ($(this).val() == "Every N Minutes") {
				$('#selectSchedulerIntervalFrequency').attr('placeholder', 'N(1-59) Minutes')
			} else {
				$('#selectSchedulerIntervalFrequency').attr('placeholder', 'N(1-23) Hours')
			}
		} else {
			$('#schedulerIntervalFrequencyContainer').css('display', 'none');
			$('#selectSchedulerIntervalFrequency').attr('placeholder','');
		}
	});


	$("#selectFlowSchedulerIntervalPeriodicity").on('select2:select', function () {
		if (["Every N Minutes", "Hourly"].includes($(this).val())) {
			let currentDate = new Date();
			currentTime = `${currentDate.getHours()} ${currentDate.getMinutes()}`
			$('#selectSchedulerIntervalTime').val(currentTime).trigger('change');
			if ($(this).val() == "Every N Minutes") {
				$('#selectFlowSchedulerIntervalFrequency').attr('placeholder', 'N(1-59) Minutes')
			} else {
				$('#selectFlowSchedulerIntervalFrequency').attr('placeholder', 'N(1-23) Hours')
			}
			$('#flowSchedulerIntervalFrequencyContainer').css('display', '');

		} else {
			$('#flowSchedulerIntervalFrequencyContainer').css('display', 'none');
			$('#selectFlowSchedulerIntervalFrequency').attr('placeholder','');
			$('#selectFlowSchedulerIntervalTime').css('display', '');
		}
	});


	$('#selectSchedulerTrigger').on('select2:select', function(){
		if ($(this).val() == "interval") {
			$('#intervalExecutionDetailsContainer').css('display', '');
			$('#triggerExecutionDetailsContainer').css('display', 'none');
		} else {
			let blockData = JSON.parse($('#flowDetailBodyNew').attr('data-currentElement'));
			let parentElement = blockData["data-previousElement"];
			let parentBlockType = elementType(parentElement);
			$('#selectSchedulerTriggerAction').empty();
			if (parentBlockType == 'create_view') {
				$('#selectSchedulerTriggerAction').append('<option value="save">Save Record</option>');
			} else if (parentBlockType == 'list_view') {
				$('#selectSchedulerTriggerAction').append('<option value="upload">Upload Data</option>');
				$('#selectSchedulerTriggerAction').append('<option value="update">Update Record</option>');
				$('#selectSchedulerTriggerAction').append('<option value="delete">Delete Record</option>');
			} else if (parentBlockType == 'decision_box') {
				$('#selectSchedulerTriggerAction').append('<option value="approve">Approve Record</option>');
				$('#selectSchedulerTriggerAction').append('<option value="reject">Reject Record</option>');
			} else if (parentBlockType == 'data_connector') {
				$('#selectSchedulerTriggerAction').append('<option value="upload">Upload Data</option>');
			} else if (parentBlockType == 'computation') {
				$('#selectSchedulerTriggerAction').append('<option value="run_model">Model Run</option>');
			}
			$('#intervalExecutionDetailsContainer').css('display', 'none');
			$('#triggerExecutionDetailsContainer').css('display', 'block');
		};
	});


	$('#saveBlockSchedulerConfig').on('click', function(){
		let schedulerType = $('#selectSchedulerType').val();
		let currentBlockData = JSON.parse($('#flowDetailBodyNew').attr('data-currentElement'));
		let blockSchedulerConfig = {};
		if (schedulerType == 'scheduleBlock') {
			let schedulerTrigger = $('#selectSchedulerTrigger').val();
			let schedulerAction = $('#selectSchedulerAction').val();
			let noOfRetries = $('#selectSchedulerRetry').val();
			let intervalBetweenRetries = $('#selectSchedulerRetryInterval').val();
			let blockTriggerConfig = {};
			let schedulerActionCondition = {};
			if (schedulerTrigger == 'trigger') {
				blockTriggerConfig['schedulerTriggerAction'] = $('#selectSchedulerTriggerAction').val();
				blockTriggerConfig['previousElement'] = currentBlockData['data-previousElement'];
			} else {
				blockTriggerConfig['previousElement'] = currentBlockData['data-previousElement'];
				blockTriggerConfig['startDate'] = $('#schedulerIntervalStartDate').val();
				blockTriggerConfig['endDate'] = $('#schedulerIntervalEndDate').val();
				blockTriggerConfig['intervalPeriod'] = $('#selectSchedulerIntervalPeriodicity').val();
				blockTriggerConfig['intervalTime'] = $('#selectSchedulerIntervalTime').val();
				if (["Every N Minutes", "Hourly"].includes($('#selectSchedulerIntervalPeriodicity').val())) {
					blockTriggerConfig['intervalFrequency'] = $('#selectSchedulerIntervalFrequency').val();
				};
			};
			if (['approve_with_condition', 'reject_with_condition'].includes(schedulerAction)) {
				if ($('#actionConditionDetailButton').attr('data-config')) {
					schedulerActionCondition = JSON.parse($('#actionConditionDetailButton').attr('data-config'));
				}
			}
			blockSchedulerConfig = {
				'schedulerTrigger': schedulerTrigger,
				'schedulerAction': schedulerAction,
				'noOfRetries': noOfRetries,
				'intervalBetweenRetries': intervalBetweenRetries,
				'blockTriggerConfig': blockTriggerConfig,
				'schedulerActionCondition': schedulerActionCondition,
			};
			var additionalJobsDetails = [];
			$('#additionalJobConfigContainer > .additionalJobDetails').each(function() {
				let schedulerTrigger = $(this).find('.selectSchedulerTrigger').val();
				let schedulerAction = $(this).find('.selectSchedulerAction').val();
				let noOfRetries = $(this).find('.selectSchedulerRetry').val();
				let intervalBetweenRetries = $(this).find('.selectSchedulerRetryInterval').val();
				let blockTriggerConfig = {};
				let schedulerActionCondition = {};
				if (schedulerTrigger == 'trigger') {
					blockTriggerConfig['schedulerTriggerAction'] = $(this).find('.selectSchedulerTriggerAction').val();
					blockTriggerConfig['previousElement'] = currentBlockData['data-previousElement'];
				} else {
					blockTriggerConfig['previousElement'] = currentBlockData['data-previousElement'];
					blockTriggerConfig['startDate'] = $(this).find('.schedulerIntervalStartDate').val();
					blockTriggerConfig['endDate'] = $(this).find('.schedulerIntervalEndDate').val();
					blockTriggerConfig['intervalPeriod'] = $(this).find('.selectSchedulerIntervalPeriodicity').val();
					blockTriggerConfig['intervalTime'] = $(this).find('.selectSchedulerIntervalTime').val();
					if (["Every N Minutes", "Hourly"].includes($(this).find('.selectSchedulerIntervalPeriodicity').val())) {
						blockTriggerConfig['intervalFrequency'] = $(this).find('.selectSchedulerIntervalFrequency').val();
					};
				};
				if (['approve_with_condition', 'reject_with_condition'].includes(schedulerAction)) {
					if ($(this).find('.actionConditionDetailButton').attr('data-config')) {
						schedulerActionCondition = JSON.parse($(this).find('.actionConditionDetailButton').attr('data-config'));
					}
				}
				let additionalblockSchedulerConfig = {
					'schedulerTrigger': schedulerTrigger,
					'schedulerAction': schedulerAction,
					'noOfRetries': noOfRetries,
					'intervalBetweenRetries': intervalBetweenRetries,
					'blockTriggerConfig': blockTriggerConfig,
					'schedulerActionCondition': schedulerActionCondition,
				};
				additionalJobsDetails.push(additionalblockSchedulerConfig);
			});
			blockSchedulerConfig['additionalJobs'] = additionalJobsDetails;

		} else {
			let schedulerAction = $('#selectSchedulerAction').val();
			let blockTriggerConfig = {};
			blockTriggerConfig['previousElement'] = currentBlockData['data-previousElement'];

			blockSchedulerConfig = {
				'schedulerAction': schedulerAction,
				'blockTriggerConfig': blockTriggerConfig,
			};
		}
		if ($('#flowDetailBodyNew').attr('data-config')) {
			var currentConfig = JSON.parse($('#flowDetailBodyNew').attr('data-config'));
			currentConfig[currentBlockData['id']] = blockSchedulerConfig;
			$('#flowDetailBodyNew').attr('data-config', JSON.stringify(currentConfig));
		};
		$('#flowDetailBodyNew').removeAttr('data-currentElement');
		$('#blockDetailContainer').css('display', 'none');
	});


	$('#saveProcessSchedulerConfig').off("click").on("click",function(){
		let schedulerType = $('#selectSchedulerType').val();
		let schedulerConfig = {
			'schedulerType': schedulerType,
		};
		if (schedulerType == 'scheduleBlock') {
			let blockConfig = JSON.parse($('#flowDetailBodyNew').attr('data-config'));
			schedulerConfig['blockConfig'] = blockConfig;
		} else {
			schedulerConfig['schedulerTrigger'] =  $('#selectFlowSchedulerTrigger').val();
			schedulerConfig['noOfRetries'] =  $('#selectFlowSchedulerRetry').val();
			schedulerConfig['intervalBetweenRetries'] =  $('#selectFlowSchedulerRetryInterval').val();
			schedulerConfig['startDate'] =  $('#flowSchedulerIntervalStartDate').val();
			schedulerConfig['endDate'] =  $('#flowSchedulerIntervalEndDate').val();
			schedulerConfig['intervalPeriod'] =  $('#selectFlowSchedulerIntervalPeriodicity').val();
			schedulerConfig['intervalTime'] =  $('#selectFlowSchedulerIntervalTime').val();
			if (["Every N Minutes", "Hourly"].includes($('#selectSchedulerIntervalPeriodicity').val())) {
				schedulerConfig['intervalFrequency'] = $('#selectFlowSchedulerIntervalFrequency').val();
			};
			let blockConfig = JSON.parse($('#flowDetailBodyNew').attr('data-config'));
			schedulerConfig['blockConfig'] = blockConfig;
		}
		$.ajax({
			url: window.location.pathname,
			data: {
				'process_code': $("#graphContainerID").attr("data-process_code"),
				'sub_process_code':$("#graphContainerID").attr("data-subprocess_code"),
				"scheduler_config": JSON.stringify(schedulerConfig),
				"operation":"saveProcessFlowSchedulerConfig",
			},
			type: "POST",
			dataType: "json",
			success: function (data) {
				Swal.fire({icon: 'success',text: 'Process flow scheduled successfuly.'});
			},
			error: ()=>{
				Swal.fire({icon: 'error',text: 'Error! Please try again.'});
			}
		});
	});

	$('#resetProcessSchedulerConfig').on('click', function () {
		$.ajax({
			url: window.location.pathname,
			data: {
				'process_code': $("#graphContainerID").attr("data-process_code"),
				'sub_process_code':$("#graphContainerID").attr("data-subprocess_code"),
				"operation":"resetProcessFlowSchedulerConfig",
			},
			type: "POST",
			dataType: "json",
			success: function (data) {
				$('#flowDetailBodyNew').removeAttr('data-config');
				Swal.fire({icon: 'success',text: 'Process scheduler reset successfuly.'});
			},
			error: ()=>{
				Swal.fire({icon: 'error',text: 'Error! Please try again.'});
			}
		});
	})

	$('#selectSchedulerType').on('select2:select', function () {
		if ($(this).val() == 'scheduleFlow') {
			$('#flowDetailContainer').css('display', 'block');
		} else {
			$('#flowDetailContainer').css('display', 'none');
		}
	});

	function flowUICreator(elementsArray) {
		var cy = cytoscape({
			container: $('#flowDetailBodyNew'),
			zoomingEnabled: false,
			userZoomingEnabled: false,
			elements: elementsArray,
			style: [
				{
					selector: 'node',
					style: {
						'shape': "roundrectangle",
						'label': 'data(text)',
						'font-size': 10,
						'width': 100,
						'height': 50,
					}
				},
				{
					selector: 'edge',
					style: {
					  width: 1
					}
				}
			],
			layout: {
				name: "dagre",
				rankDir: "LR",
				padding: 10,
				spacingFactor: 1.25,
				fit: true,
				nodeDimensionsIncludeLabels: true,
				avoidOverlap: true,
				pan: { x: 200, y: 100 }
			}
		});
		cy.nodes().on('click', function(e){
			var ele = e.target;
			var blockId = ele.id();
			var blockData = ele.data();
			cy.nodes().removeClass('selected');
			ele.addClass('selected');
			$('#flowDetailBodyNew').attr('data-currentElement', JSON.stringify(blockData));
			fetchBlockSchedulerDetails(blockId, blockData);
		});
	}

	$(".schedulerFlowType").off("click").on("click",function(){
		$('#flowDetail').find('.indDetail').css('display','none');
		$('#dependencyChecker').attr("save","no");
		var enc = new mxCodec(mxUtils.createXmlDocument());
		var node = enc.encode(graph.getModel());
		var xml = mxUtils.getPrettyXml(node);
		$.ajax({
			url: window.location.pathname,
			data: {
			"operation":"fetchFlowDetail",
			'process_code': $("#graphContainerID").attr("data-process_code"),
			'sub_process_code': $("#graphContainerID").attr("data-subprocess_code"),
			"xml": xml
			},
			type: "POST",
			dataType: "json",
			success: function (data) {
				let existingConfig = data.existing_config;
				$('#flowDetailBodyNew').attr('data-config', JSON.stringify(existingConfig.existing_block_config));
				$('#saveProcessSchedulerConfig').attr('data-config', JSON.stringify(existingConfig));
				$('#dependencyChecker').removeAttr("save");

				var elementsArray = data.elements_list;
				$("#flowDetail").modal("show");
				flowUICreator(elementsArray);
			},
			error: function(){
				$('#dependencyChecker').removeAttr("save");
			},
		});
	});
};

// Extends mxEventSource
mxUtils.extend(EditorUi, mxEventSource);

/**
 * Global config that specifies if the compact UI elements should be used.
 */
EditorUi.compactUi = true;

/**
 * Specifies the size of the split bar.
 */
EditorUi.prototype.splitSize = (mxClient.IS_TOUCH || mxClient.IS_POINTER) ? 12 : 8;

/**
 * Specifies the height of the menubar. Default is 30.
 */
EditorUi.prototype.menubarHeight = 30;

/**
 * Specifies the width of the format panel should be enabled. Default is true.
 */
EditorUi.prototype.formatEnabled = true;

/**
 * Specifies the width of the format panel. Default is 240.
 */
EditorUi.prototype.formatWidth = 240;

/**
 * Specifies the height of the toolbar. Default is 38.
 */
EditorUi.prototype.toolbarHeight = 38;

/**
 * Specifies the height of the footer. Default is 28.
 */
EditorUi.prototype.footerHeight = 28;

/**
 * Specifies the height of the optional sidebarFooterContainer. Default is 34.
 */
EditorUi.prototype.sidebarFooterHeight = 34;

/**
 * Specifies the position of the horizontal split bar. Default is 240 or 118 for
 * screen widths <= 640px.
 */
EditorUi.prototype.hsplitPosition = (screen.width <= 640) ? 118 : ((urlParams['sidebar-entries'] != 'large') ? 212 : 240);

/**
 * Specifies if animations are allowed in <executeLayout>. Default is true.
 */
EditorUi.prototype.allowAnimation = true;

/**
 * Default is 2.
 */
EditorUi.prototype.lightboxMaxFitScale = 2;

/**
 * Default is 4.
 */
EditorUi.prototype.lightboxVerticalDivider = 4;

/**
 * Specifies if single click on horizontal split should collapse sidebar. Default is false.
 */
EditorUi.prototype.hsplitClickEnabled = false;

/**
 * Installs the listeners to update the action states.
 */
EditorUi.prototype.init = function () {
	var graph = this.editor.graph;

	if (!graph.standalone) {
		// Hides tooltips and connection points when scrolling
		mxEvent.addListener(graph.container, 'scroll', mxUtils.bind(this, function () {
			graph.tooltipHandler.hide();

			if (graph.connectionHandler != null && graph.connectionHandler.constraintHandler != null) {
				graph.connectionHandler.constraintHandler.reset();
			}
		}));

		// Hides tooltip on escape
		graph.addListener(mxEvent.ESCAPE, mxUtils.bind(this, function () {
			graph.tooltipHandler.hide();
			var rb = graph.getRubberband();

			if (rb != null) {
				rb.cancel();
			}
		}));

		mxEvent.addListener(graph.container, 'keydown', mxUtils.bind(this, function (evt) {
			this.onKeyDown(evt);
		}));

		mxEvent.addListener(graph.container, 'keypress', mxUtils.bind(this, function (evt) {
			this.onKeyPress(evt);
		}));

		// Updates action states
		this.addUndoListener();
		this.addBeforeUnloadListener();

		graph.getSelectionModel().addListener(mxEvent.CHANGE, mxUtils.bind(this, function () {
			this.updateActionStates();
		}));

		graph.getModel().addListener(mxEvent.CHANGE, mxUtils.bind(this, function () {
			this.updateActionStates();
		}));

		// Changes action states after change of default parent
		var graphSetDefaultParent = graph.setDefaultParent;
		var ui = this;

		this.editor.graph.setDefaultParent = function () {
			graphSetDefaultParent.apply(this, arguments);
			ui.updateActionStates();
		};

		// Hack to make editLink available in vertex handler
		graph.editLink = ui.actions.get('editLink').funct;

		this.updateActionStates();
		this.initClipboard();
		this.initCanvas();

		if (this.format != null) {
			this.format.init();
		}
	}
};

/**
 * Returns true if the given event should start editing. This implementation returns true.
 */
EditorUi.prototype.onKeyDown = function (evt) {
	var graph = this.editor.graph;

	// Tab selects next cell
	if (evt.which == 9 && graph.isEnabled() && !mxEvent.isAltDown(evt) &&
		(!graph.isEditing() || !mxEvent.isShiftDown(evt))) {
		if (graph.isEditing()) {
			graph.stopEditing(false);
		}
		else {
			graph.selectCell(!mxEvent.isShiftDown(evt));
		}

		mxEvent.consume(evt);
	}
};

/**
 * Returns true if the given event should start editing. This implementation returns true.
 */
EditorUi.prototype.onKeyPress = function (evt) {
	var graph = this.editor.graph;

	// KNOWN: Focus does not work if label is empty in quirks mode
	if (this.isImmediateEditingEvent(evt) && !graph.isEditing() && !graph.isSelectionEmpty() && evt.which !== 0 &&
		evt.which !== 27 && !mxEvent.isAltDown(evt) && !mxEvent.isControlDown(evt) && !mxEvent.isMetaDown(evt)) {
		graph.escape();
		graph.startEditing();

		// Workaround for FF where char is lost if cursor is placed before char
		if (mxClient.IS_FF) {
			var ce = graph.cellEditor;
			ce.textarea.innerHTML = String.fromCharCode(evt.which);

			// Moves cursor to end of textarea
			var range = document.createRange();
			range.selectNodeContents(ce.textarea);
			range.collapse(false);
			var sel = window.getSelection();
			sel.removeAllRanges();
			sel.addRange(range);
		}
	}
};

/**
 * Returns true if the given event should start editing. This implementation returns true.
 */
EditorUi.prototype.isImmediateEditingEvent = function (evt) {
	return true;
};

/**
 * Private helper method.
 */
EditorUi.prototype.getCssClassForMarker = function (prefix, shape, marker, fill) {
	var result = '';

	if (shape == 'flexArrow') {
		result = (marker != null && marker != mxConstants.NONE) ?
			'geSprite geSprite-' + prefix + 'blocktrans' : 'geSprite geSprite-noarrow';
	}
	else {
		// SVG marker sprites
		if (marker == 'box' || marker == 'halfCircle') {
			result = 'geSprite geSvgSprite geSprite-' + marker + ((prefix == 'end') ? ' geFlipSprite' : '');
		}
		else if (marker == mxConstants.ARROW_CLASSIC) {
			result = (fill == '1') ? 'geSprite geSprite-' + prefix + 'classic' : 'geSprite geSprite-' + prefix + 'classictrans';
		}
		else if (marker == mxConstants.ARROW_CLASSIC_THIN) {
			result = (fill == '1') ? 'geSprite geSprite-' + prefix + 'classicthin' : 'geSprite geSprite-' + prefix + 'classicthintrans';
		}
		else if (marker == mxConstants.ARROW_OPEN) {
			result = 'geSprite geSprite-' + prefix + 'open';
		}
		else if (marker == mxConstants.ARROW_OPEN_THIN) {
			result = 'geSprite geSprite-' + prefix + 'openthin';
		}
		else if (marker == mxConstants.ARROW_BLOCK) {
			result = (fill == '1') ? 'geSprite geSprite-' + prefix + 'block' : 'geSprite geSprite-' + prefix + 'blocktrans';
		}
		else if (marker == mxConstants.ARROW_BLOCK_THIN) {
			result = (fill == '1') ? 'geSprite geSprite-' + prefix + 'blockthin' : 'geSprite geSprite-' + prefix + 'blockthintrans';
		}
		else if (marker == mxConstants.ARROW_OVAL) {
			result = (fill == '1') ? 'geSprite geSprite-' + prefix + 'oval' : 'geSprite geSprite-' + prefix + 'ovaltrans';
		}
		else if (marker == mxConstants.ARROW_DIAMOND) {
			result = (fill == '1') ? 'geSprite geSprite-' + prefix + 'diamond' : 'geSprite geSprite-' + prefix + 'diamondtrans';
		}
		else if (marker == mxConstants.ARROW_DIAMOND_THIN) {
			result = (fill == '1') ? 'geSprite geSprite-' + prefix + 'thindiamond' : 'geSprite geSprite-' + prefix + 'thindiamondtrans';
		}
		else if (marker == 'openAsync') {
			result = 'geSprite geSprite-' + prefix + 'openasync';
		}
		else if (marker == 'dash') {
			result = 'geSprite geSprite-' + prefix + 'dash';
		}
		else if (marker == 'cross') {
			result = 'geSprite geSprite-' + prefix + 'cross';
		}
		else if (marker == 'async') {
			result = (fill == '1') ? 'geSprite geSprite-' + prefix + 'async' : 'geSprite geSprite-' + prefix + 'asynctrans';
		}
		else if (marker == 'circle' || marker == 'circlePlus') {
			result = (fill == '1' || marker == 'circle') ? 'geSprite geSprite-' + prefix + 'circle' : 'geSprite geSprite-' + prefix + 'circleplus';
		}
		else if (marker == 'ERone') {
			result = 'geSprite geSprite-' + prefix + 'erone';
		}
		else if (marker == 'ERmandOne') {
			result = 'geSprite geSprite-' + prefix + 'eronetoone';
		}
		else if (marker == 'ERmany') {
			result = 'geSprite geSprite-' + prefix + 'ermany';
		}
		else if (marker == 'ERoneToMany') {
			result = 'geSprite geSprite-' + prefix + 'eronetomany';
		}
		else if (marker == 'ERzeroToOne') {
			result = 'geSprite geSprite-' + prefix + 'eroneopt';
		}
		else if (marker == 'ERzeroToMany') {
			result = 'geSprite geSprite-' + prefix + 'ermanyopt';
		}
		else {
			result = 'geSprite geSprite-noarrow';
		}
	}

	return result;
};

/**
 * Overridden in Menus.js
 */
EditorUi.prototype.createMenus = function () {
	return null;
};

/**
 * Hook for allowing selection and context menu for certain events.
 */
EditorUi.prototype.updatePasteActionStates = function () {
	var graph = this.editor.graph;
	var paste = this.actions.get('paste');
	var pasteHere = this.actions.get('pasteHere');

	paste.setEnabled(this.editor.graph.cellEditor.isContentEditing() || (!mxClipboard.isEmpty() &&
		graph.isEnabled() && !graph.isCellLocked(graph.getDefaultParent())));
	pasteHere.setEnabled(paste.isEnabled());
};

/**
 * Hook for allowing selection and context menu for certain events.
 */
EditorUi.prototype.initClipboard = function () {
	var ui = this;

	var mxClipboardCut = mxClipboard.cut;
	mxClipboard.cut = function (graph) {
		if (graph.cellEditor.isContentEditing()) {
			document.execCommand('cut', false, null);
		}
		else {
			mxClipboardCut.apply(this, arguments);
		}

		ui.updatePasteActionStates();
	};

	var mxClipboardCopy = mxClipboard.copy;
	mxClipboard.copy = function (graph) {
		var result = null;

		if (graph.cellEditor.isContentEditing()) {
			document.execCommand('copy', false, null);
		}
		else {
			result = result || graph.getSelectionCells();
			result = graph.getExportableCells(graph.model.getTopmostCells(result));

			var cloneMap = new Object();
			var lookup = graph.createCellLookup(result);
			var clones = graph.cloneCells(result, null, cloneMap);

			// Uses temporary model to force new IDs to be assigned
			// to avoid having to carry over the mapping from object
			// ID to cell ID to the paste operation
			var model = new mxGraphModel();
			var parent = model.getChildAt(model.getRoot(), 0);

			for (var i = 0; i < clones.length; i++) {
				model.add(parent, clones[i]);
			}

			graph.updateCustomLinks(graph.createCellMapping(cloneMap, lookup), clones);

			mxClipboard.insertCount = 1;
			mxClipboard.setCells(clones);
		}

		ui.updatePasteActionStates();

		return result;
	};

	var mxClipboardPaste = mxClipboard.paste;
	mxClipboard.paste = function (graph) {
		var result = null;

		if (graph.cellEditor.isContentEditing()) {
			document.execCommand('paste', false, null);
		}
		else {
			result = mxClipboardPaste.apply(this, arguments);
		}

		ui.updatePasteActionStates();

		return result;
	};

	// Overrides cell editor to update paste action state
	var cellEditorStartEditing = this.editor.graph.cellEditor.startEditing;

	this.editor.graph.cellEditor.startEditing = function () {
		cellEditorStartEditing.apply(this, arguments);
		ui.updatePasteActionStates();
	};

	var cellEditorStopEditing = this.editor.graph.cellEditor.stopEditing;

	this.editor.graph.cellEditor.stopEditing = function (cell, trigger) {
		cellEditorStopEditing.apply(this, arguments);
		ui.updatePasteActionStates();
	};

	this.updatePasteActionStates();
};

/**
 * Delay between zoom steps when not using preview.
 */
EditorUi.prototype.lazyZoomDelay = 20;

/**
 * Delay before update of DOM when using preview.
 */
EditorUi.prototype.wheelZoomDelay = 400;

/**
 * Delay before update of DOM when using preview.
 */
EditorUi.prototype.buttonZoomDelay = 600;

/**
 * Initializes the infinite canvas.
 */
EditorUi.prototype.initCanvas = function () {
	// Initial page layout view, scrollBuffer and timer-based scrolling
	var graph = this.editor.graph;
	graph.timerAutoScroll = true;

	/**
	 * Returns the padding for pages in page view with scrollbars.
	 */
	graph.getPagePadding = function () {
		return new mxPoint(Math.max(0, Math.round((graph.container.offsetWidth - 34) / graph.view.scale)),
			Math.max(0, Math.round((graph.container.offsetHeight - 34) / graph.view.scale)));
	};

	// Fits the number of background pages to the graph
	graph.view.getBackgroundPageBounds = function () {
		var layout = this.graph.getPageLayout();
		var page = this.graph.getPageSize();

		return new mxRectangle(this.scale * (this.translate.x + layout.x * page.width),
			this.scale * (this.translate.y + layout.y * page.height),
			this.scale * layout.width * page.width,
			this.scale * layout.height * page.height);
	};

	graph.getPreferredPageSize = function (bounds, width, height) {
		var pages = this.getPageLayout();
		var size = this.getPageSize();

		return new mxRectangle(0, 0, pages.width * size.width, pages.height * size.height);
	};

	// Scales pages/graph to fit available size
	var resize = null;
	var ui = this;

	if (this.editor.isChromelessView()) {
		resize = mxUtils.bind(this, function (autoscale, maxScale, cx, cy) {
			if (graph.container != null && !graph.isViewer()) {
				cx = (cx != null) ? cx : 0;
				cy = (cy != null) ? cy : 0;

				var bds = (graph.pageVisible) ? graph.view.getBackgroundPageBounds() : graph.getGraphBounds();
				var scroll = mxUtils.hasScrollbars(graph.container);
				var tr = graph.view.translate;
				var s = graph.view.scale;

				// Normalizes the bounds
				var b = mxRectangle.fromRectangle(bds);
				b.x = b.x / s - tr.x;
				b.y = b.y / s - tr.y;
				b.width /= s;
				b.height /= s;

				var st = graph.container.scrollTop;
				var sl = graph.container.scrollLeft;
				var sb = (mxClient.IS_QUIRKS || document.documentMode >= 8) ? 20 : 14;

				if (document.documentMode == 8 || document.documentMode == 9) {
					sb += 3;
				}

				var cw = graph.container.offsetWidth - sb;
				var ch = graph.container.offsetHeight - sb;

				var ns = (autoscale) ? Math.max(0.3, Math.min(maxScale || 1, cw / b.width)) : s;
				var dx = ((cw - ns * b.width) / 2) / ns;
				var dy = (this.lightboxVerticalDivider == 0) ? 0 : ((ch - ns * b.height) / this.lightboxVerticalDivider) / ns;

				if (scroll) {
					dx = Math.max(dx, 0);
					dy = Math.max(dy, 0);
				}

				if (scroll || bds.width < cw || bds.height < ch) {
					graph.view.scaleAndTranslate(ns, Math.floor(dx - b.x), Math.floor(dy - b.y));
					graph.container.scrollTop = st * ns / s;
					graph.container.scrollLeft = sl * ns / s;
				}
				else if (cx != 0 || cy != 0) {
					var t = graph.view.translate;
					graph.view.setTranslate(Math.floor(t.x + cx / s), Math.floor(t.y + cy / s));
				}
			}
		});

		// Hack to make function available to subclassers
		this.chromelessResize = resize;

		// Hook for subclassers for override
		this.chromelessWindowResize = mxUtils.bind(this, function () {
			this.chromelessResize(false);
		});

		// Removable resize listener
		var autoscaleResize = mxUtils.bind(this, function () {
			this.chromelessWindowResize(false);
		});

		mxEvent.addListener(window, 'resize', autoscaleResize);

		this.destroyFunctions.push(function () {
			mxEvent.removeListener(window, 'resize', autoscaleResize);
		});

		this.editor.addListener('resetGraphView', mxUtils.bind(this, function () {
			this.chromelessResize(true);
		}));

		this.actions.get('zoomIn').funct = mxUtils.bind(this, function (evt) {
			graph.zoomIn();
			this.chromelessResize(false);
		});
		this.actions.get('zoomOut').funct = mxUtils.bind(this, function (evt) {
			graph.zoomOut();
			this.chromelessResize(false);
		});

		// Creates toolbar for viewer - do not use CSS here
		// as this may be used in a viewer that has no CSS
		if (urlParams['toolbar'] != '0') {
			var toolbarConfig = JSON.parse(decodeURIComponent(urlParams['toolbar-config'] || '{}'));

			this.chromelessToolbar = document.createElement('div');
			this.chromelessToolbar.style.position = 'fixed';
			this.chromelessToolbar.style.overflow = 'hidden';
			this.chromelessToolbar.style.boxSizing = 'border-box';
			this.chromelessToolbar.style.whiteSpace = 'nowrap';
			this.chromelessToolbar.style.backgroundColor = '#000000';
			this.chromelessToolbar.style.padding = '10px 10px 8px 10px';
			this.chromelessToolbar.style.left = (graph.isViewer()) ? '0' : '50%';

			if (!mxClient.IS_VML) {
				mxUtils.setPrefixedStyle(this.chromelessToolbar.style, 'borderRadius', '20px');
				mxUtils.setPrefixedStyle(this.chromelessToolbar.style, 'transition', 'opacity 600ms ease-in-out');
			}

			var updateChromelessToolbarPosition = mxUtils.bind(this, function () {
				var css = mxUtils.getCurrentStyle(graph.container);

				if (graph.isViewer()) {
					this.chromelessToolbar.style.top = '0';
				}
				else {
					this.chromelessToolbar.style.bottom = ((css != null) ? parseInt(css['margin-bottom'] || 0) : 0) +
						((this.tabContainer != null) ? (20 + parseInt(this.tabContainer.style.height)) : 20) + 'px';
				}
			});

			this.editor.addListener('resetGraphView', updateChromelessToolbarPosition);
			updateChromelessToolbarPosition();

			var btnCount = 0;

			var addButton = mxUtils.bind(this, function (fn, imgSrc, tip) {
				btnCount++;

				var a = document.createElement('span');
				a.style.paddingLeft = '8px';
				a.style.paddingRight = '8px';
				a.style.cursor = 'pointer';
				mxEvent.addListener(a, 'click', fn);

				if (tip != null) {
					a.setAttribute('title', tip);
				}

				var img = document.createElement('img');
				img.setAttribute('border', '0');
				img.setAttribute('src', imgSrc);

				a.appendChild(img);
				this.chromelessToolbar.appendChild(a);

				return a;
			});

			if (toolbarConfig.backBtn != null) {
				addButton(mxUtils.bind(this, function (evt) {
					window.location.href = toolbarConfig.backBtn.url;
					mxEvent.consume(evt);
				}), Editor.backLargeImage, mxResources.get('back', null, 'Back'));
			}

			var prevButton = addButton(mxUtils.bind(this, function (evt) {
				this.actions.get('previousPage').funct();
				mxEvent.consume(evt);
			}), Editor.previousLargeImage, mxResources.get('previousPage'));

			var pageInfo = document.createElement('div');
			pageInfo.style.display = 'inline-block';
			pageInfo.style.verticalAlign = 'top';
			pageInfo.style.fontFamily = 'Helvetica,Arial';
			pageInfo.style.marginTop = '8px';
			pageInfo.style.fontSize = '14px';
			pageInfo.style.color = '#ffffff';
			this.chromelessToolbar.appendChild(pageInfo);

			var nextButton = addButton(mxUtils.bind(this, function (evt) {
				this.actions.get('nextPage').funct();
				mxEvent.consume(evt);
			}), Editor.nextLargeImage, mxResources.get('nextPage'));

			var updatePageInfo = mxUtils.bind(this, function () {
				if (this.pages != null && this.pages.length > 1 && this.currentPage != null) {
					pageInfo.innerHTML = '';
					mxUtils.write(pageInfo, (mxUtils.indexOf(this.pages, this.currentPage) + 1) + ' / ' + this.pages.length);
				}
			});

			prevButton.style.paddingLeft = '0px';
			prevButton.style.paddingRight = '4px';
			nextButton.style.paddingLeft = '4px';
			nextButton.style.paddingRight = '0px';

			var updatePageButtons = mxUtils.bind(this, function () {
				if (this.pages != null && this.pages.length > 1 && this.currentPage != null) {
					nextButton.style.display = '';
					prevButton.style.display = '';
					pageInfo.style.display = 'inline-block';
				}
				else {
					nextButton.style.display = 'none';
					prevButton.style.display = 'none';
					pageInfo.style.display = 'none';
				}

				updatePageInfo();
			});

			this.editor.addListener('resetGraphView', updatePageButtons);
			this.editor.addListener('pageSelected', updatePageInfo);

			addButton(mxUtils.bind(this, function (evt) {
				this.actions.get('zoomOut').funct();
				mxEvent.consume(evt);
			}), Editor.zoomOutLargeImage, mxResources.get('zoomOut') + ' (Alt+Mousewheel)');

			addButton(mxUtils.bind(this, function (evt) {
				this.actions.get('zoomIn').funct();
				mxEvent.consume(evt);
			}), Editor.zoomInLargeImage, mxResources.get('zoomIn') + ' (Alt+Mousewheel)');

			addButton(mxUtils.bind(this, function (evt) {
				if (graph.isLightboxView()) {
					if (graph.view.scale == 1) {
						this.lightboxFit();
					}
					else {
						graph.zoomTo(1);
					}

					this.chromelessResize(false);
				}
				else {
					this.chromelessResize(true);
				}

				mxEvent.consume(evt);
			}), Editor.actualSizeLargeImage, mxResources.get('fit'));

			// Changes toolbar opacity on hover
			var fadeThread = null;
			var fadeThread2 = null;

			var fadeOut = mxUtils.bind(this, function (delay) {
				if (fadeThread != null) {
					window.clearTimeout(fadeThread);
					fadeThead = null;
				}

				if (fadeThread2 != null) {
					window.clearTimeout(fadeThread2);
					fadeThead2 = null;
				}

				fadeThread = window.setTimeout(mxUtils.bind(this, function () {
					mxUtils.setOpacity(this.chromelessToolbar, 0);
					fadeThread = null;

					fadeThread2 = window.setTimeout(mxUtils.bind(this, function () {
						this.chromelessToolbar.style.display = 'none';
						fadeThread2 = null;
					}), 600);
				}), delay || 200);
			});

			var fadeIn = mxUtils.bind(this, function (opacity) {
				if (fadeThread != null) {
					window.clearTimeout(fadeThread);
					fadeThead = null;
				}

				if (fadeThread2 != null) {
					window.clearTimeout(fadeThread2);
					fadeThead2 = null;
				}

				this.chromelessToolbar.style.display = '';
				mxUtils.setOpacity(this.chromelessToolbar, opacity || 30);
			});

			if (urlParams['layers'] == '1') {
				this.layersDialog = null;

				var layersButton = addButton(mxUtils.bind(this, function (evt) {
					if (this.layersDialog != null) {
						this.layersDialog.parentNode.removeChild(this.layersDialog);
						this.layersDialog = null;
					}
					else {
						this.layersDialog = graph.createLayersDialog();

						mxEvent.addListener(this.layersDialog, 'mouseleave', mxUtils.bind(this, function () {
							this.layersDialog.parentNode.removeChild(this.layersDialog);
							this.layersDialog = null;
						}));

						var r = layersButton.getBoundingClientRect();

						mxUtils.setPrefixedStyle(this.layersDialog.style, 'borderRadius', '5px');
						this.layersDialog.style.position = 'fixed';
						this.layersDialog.style.fontFamily = 'Helvetica,Arial';
						this.layersDialog.style.backgroundColor = '#000000';
						this.layersDialog.style.width = '160px';
						this.layersDialog.style.padding = '4px 2px 4px 2px';
						this.layersDialog.style.color = '#ffffff';
						mxUtils.setOpacity(this.layersDialog, 70);
						this.layersDialog.style.left = r.left + 'px';
						this.layersDialog.style.bottom = parseInt(this.chromelessToolbar.style.bottom) +
							this.chromelessToolbar.offsetHeight + 4 + 'px';

						// Puts the dialog on top of the container z-index
						var style = mxUtils.getCurrentStyle(this.editor.graph.container);
						this.layersDialog.style.zIndex = style.zIndex;

						document.body.appendChild(this.layersDialog);
					}

					mxEvent.consume(evt);
				}), Editor.layersLargeImage, mxResources.get('layers'));

				// Shows/hides layers button depending on content
				var model = graph.getModel();

				model.addListener(mxEvent.CHANGE, function () {
					layersButton.style.display = (model.getChildCount(model.root) > 1) ? '' : 'none';
				});
			}

			this.addChromelessToolbarItems(addButton);

			if (this.editor.editButtonLink != null || this.editor.editButtonFunc != null) {
				addButton(mxUtils.bind(this, function (evt) {
					if (this.editor.editButtonFunc != null) {
						this.editor.editButtonFunc();
					}
					else if (this.editor.editButtonLink == '_blank') {
						this.editor.editAsNew(this.getEditBlankXml());
					}
					else {
						graph.openLink(this.editor.editButtonLink, 'editWindow');
					}

					mxEvent.consume(evt);
				}), Editor.editLargeImage, mxResources.get('edit'));
			}

			if (this.lightboxToolbarActions != null) {
				for (var i = 0; i < this.lightboxToolbarActions.length; i++) {
					var lbAction = this.lightboxToolbarActions[i];
					addButton(lbAction.fn, lbAction.icon, lbAction.tooltip);
				}
			}

			if (toolbarConfig.refreshBtn != null) {
				addButton(mxUtils.bind(this, function (evt) {
					if (toolbarConfig.refreshBtn.url) {
						window.location.href = toolbarConfig.refreshBtn.url;
					}
					else {
						window.location.reload();
					}

					mxEvent.consume(evt);
				}), Editor.refreshLargeImage, mxResources.get('refresh', null, 'Refresh'));
			}

			if (toolbarConfig.fullscreenBtn != null && window.self !== window.top) {
				addButton(mxUtils.bind(this, function (evt) {
					if (toolbarConfig.fullscreenBtn.url) {
						graph.openLink(toolbarConfig.fullscreenBtn.url);
					}
					else {
						graph.openLink(window.location.href);
					}

					mxEvent.consume(evt);
				}), Editor.fullscreenLargeImage, mxResources.get('openInNewWindow', null, 'Open in New Window'));
			}

			if ((toolbarConfig.closeBtn && window.self === window.top) ||
				(graph.lightbox && (urlParams['close'] == '1' || this.container != document.body))) {
				addButton(mxUtils.bind(this, function (evt) {
					if (urlParams['close'] == '1' || toolbarConfig.closeBtn) {
						window.close();
					}
					else {
						this.destroy();
						mxEvent.consume(evt);
					}
				}), Editor.closeLargeImage, mxResources.get('close') + ' (Escape)');
			}

			// Initial state invisible
			this.chromelessToolbar.style.display = 'none';

			if (!graph.isViewer()) {
				mxUtils.setPrefixedStyle(this.chromelessToolbar.style, 'transform', 'translate(-50%,0)');
			}

			graph.container.appendChild(this.chromelessToolbar);

			mxEvent.addListener(graph.container, (mxClient.IS_POINTER) ? 'pointermove' : 'mousemove', mxUtils.bind(this, function (evt) {
				if (!mxEvent.isTouchEvent(evt)) {
					if (!mxEvent.isShiftDown(evt)) {
						fadeIn(30);
					}

					fadeOut();
				}
			}));

			mxEvent.addListener(this.chromelessToolbar, (mxClient.IS_POINTER) ? 'pointermove' : 'mousemove', function (evt) {
				mxEvent.consume(evt);
			});

			mxEvent.addListener(this.chromelessToolbar, 'mouseenter', mxUtils.bind(this, function (evt) {
				if (!mxEvent.isShiftDown(evt)) {
					fadeIn(100);
				}
				else {
					fadeOut();
				}
			}));

			mxEvent.addListener(this.chromelessToolbar, 'mousemove', mxUtils.bind(this, function (evt) {
				if (!mxEvent.isShiftDown(evt)) {
					fadeIn(100);
				}
				else {
					fadeOut();
				}

				mxEvent.consume(evt);
			}));

			mxEvent.addListener(this.chromelessToolbar, 'mouseleave', mxUtils.bind(this, function (evt) {
				if (!mxEvent.isTouchEvent(evt)) {
					fadeIn(30);
				}
			}));

			// Shows/hides toolbar for touch devices
			graph.addMouseListener(
				{
					startX: 0,
					startY: 0,
					scrollLeft: 0,
					scrollTop: 0,
					mouseDown: function (sender, me) {
						this.startX = me.getGraphX();
						this.startY = me.getGraphY();
						this.scrollLeft = graph.container.scrollLeft;
						this.scrollTop = graph.container.scrollTop;
					},
					mouseMove: function (sender, me) { },
					mouseUp: function (sender, me) {
						if (mxEvent.isTouchEvent(me.getEvent())) {
							if ((Math.abs(this.scrollLeft - graph.container.scrollLeft) < tol &&
								Math.abs(this.scrollTop - graph.container.scrollTop) < tol) &&
								(Math.abs(this.startX - me.getGraphX()) < tol &&
									Math.abs(this.startY - me.getGraphY()) < tol)) {
								if (parseFloat(ui.chromelessToolbar.style.opacity || 0) > 0) {
									fadeOut();
								}
								else {
									fadeIn(30);
								}
							}
						}
					},

				});
		} // end if toolbar

		// Installs handling of highlight and handling links to relative links and anchors
		if (!this.editor.editable) {
			this.addChromelessClickHandler();
		}
	}
	else if (this.editor.extendCanvas) {
		/**
		 * Guesses autoTranslate to avoid another repaint (see below).
		 * Works if only the scale of the graph changes or if pages
		 * are visible and the visible pages do not change.
		 */
		var graphViewValidate = graph.view.validate;
		graph.view.validate = function () {
			if (this.graph.container != null && mxUtils.hasScrollbars(this.graph.container)) {
				var pad = this.graph.getPagePadding();
				var size = this.graph.getPageSize();

				// Updating scrollbars here causes flickering in quirks and is not needed
				// if zoom method is always used to set the current scale on the graph.
				var tx = this.translate.x;
				var ty = this.translate.y;
				this.translate.x = pad.x - (this.x0 || 0) * size.width;
				this.translate.y = pad.y - (this.y0 || 0) * size.height;
			}

			graphViewValidate.apply(this, arguments);
		};

		if (!graph.isViewer()) {
			var graphSizeDidChange = graph.sizeDidChange;

			graph.sizeDidChange = function () {
				if (this.container != null && mxUtils.hasScrollbars(this.container)) {
					var pages = this.getPageLayout();
					var pad = this.getPagePadding();
					var size = this.getPageSize();

					// Updates the minimum graph size
					var minw = Math.ceil(2 * pad.x + pages.width * size.width);
					var minh = Math.ceil(2 * pad.y + pages.height * size.height);

					var min = graph.minimumGraphSize;

					// LATER: Fix flicker of scrollbar size in IE quirks mode
					// after delayed call in window.resize event handler
					if (min == null || min.width != minw || min.height != minh) {
						graph.minimumGraphSize = new mxRectangle(0, 0, minw, minh);
					}

					// Updates auto-translate to include padding and graph size
					var dx = pad.x - pages.x * size.width;
					var dy = pad.y - pages.y * size.height;

					if (!this.autoTranslate && (this.view.translate.x != dx || this.view.translate.y != dy)) {
						this.autoTranslate = true;
						this.view.x0 = pages.x;
						this.view.y0 = pages.y;

						// NOTE: THIS INVOKES THIS METHOD AGAIN. UNFORTUNATELY THERE IS NO WAY AROUND THIS SINCE THE
						// BOUNDS ARE KNOWN AFTER THE VALIDATION AND SETTING THE TRANSLATE TRIGGERS A REVALIDATION.
						// SHOULD MOVE TRANSLATE/SCALE TO VIEW.
						var tx = graph.view.translate.x;
						var ty = graph.view.translate.y;
						graph.view.setTranslate(dx, dy);

						// LATER: Fix rounding errors for small zoom
						graph.container.scrollLeft += Math.round((dx - tx) * graph.view.scale);
						graph.container.scrollTop += Math.round((dy - ty) * graph.view.scale);

						this.autoTranslate = false;

						return;
					}

					graphSizeDidChange.apply(this, arguments);
				}
				else {
					// Fires event but does not invoke superclass
					this.fireEvent(new mxEventObject(mxEvent.SIZE, 'bounds', this.getGraphBounds()));
				}
			};
		}
	}

	// Accumulates the zoom factor while the rendering is taking place
	// so that not the complete sequence of zoom steps must be painted
	var bgGroup = graph.view.getBackgroundPane();
	var mainGroup = graph.view.getDrawPane();
	graph.cumulativeZoomFactor = 1;
	var updateZoomTimeout = null;
	var cursorPosition = null;
	var scrollPosition = null;
	var filter = null;

	var scheduleZoom = function (delay) {
		if (updateZoomTimeout != null) {
			window.clearTimeout(updateZoomTimeout);
		}

		window.setTimeout(function () {
			if (!graph.isMouseDown) {
				updateZoomTimeout = window.setTimeout(mxUtils.bind(this, function () {
					if (graph.isFastZoomEnabled()) {
						// Transforms background page
						if (graph.view.backgroundPageShape != null && graph.view.backgroundPageShape.node != null) {
							mxUtils.setPrefixedStyle(graph.view.backgroundPageShape.node.style, 'transform-origin', null);
							mxUtils.setPrefixedStyle(graph.view.backgroundPageShape.node.style, 'transform', null);
						}

						// Transforms graph and background image
						mainGroup.style.transformOrigin = '';
						bgGroup.style.transformOrigin = '';

						// Workaround for no reset of transform in Safari
						if (mxClient.IS_SF) {
							mainGroup.style.transform = 'scale(1)';
							bgGroup.style.transform = 'scale(1)';

							window.setTimeout(function () {
								mainGroup.style.transform = '';
								bgGroup.style.transform = '';
							}, 0)
						}
						else {
							mainGroup.style.transform = '';
							bgGroup.style.transform = '';
						}

						// Shows interactive elements
						graph.view.getDecoratorPane().style.opacity = '';
						graph.view.getOverlayPane().style.opacity = '';
					}

					var sp = new mxPoint(graph.container.scrollLeft, graph.container.scrollTop);
					var offset = mxUtils.getOffset(graph.container);
					var prev = graph.view.scale;
					var dx = 0;
					var dy = 0;

					if (cursorPosition != null) {
						dx = graph.container.offsetWidth / 2 - cursorPosition.x + offset.x;
						dy = graph.container.offsetHeight / 2 - cursorPosition.y + offset.y;
					}

					graph.zoom(graph.cumulativeZoomFactor);
					var s = graph.view.scale;

					if (s != prev) {
						if (scrollPosition != null) {
							dx += sp.x - scrollPosition.x;
							dy += sp.y - scrollPosition.y;
						}

						if (resize != null) {
							ui.chromelessResize(false, null, dx * (graph.cumulativeZoomFactor - 1),
								dy * (graph.cumulativeZoomFactor - 1));
						}

						if (mxUtils.hasScrollbars(graph.container) && (dx != 0 || dy != 0)) {
							graph.container.scrollLeft -= dx * (graph.cumulativeZoomFactor - 1);
							graph.container.scrollTop -= dy * (graph.cumulativeZoomFactor - 1);
						}
					}

					if (filter != null) {
						mainGroup.setAttribute('filter', filter);
					}

					graph.cumulativeZoomFactor = 1;
					updateZoomTimeout = null;
					scrollPosition = null;
					cursorPosition = null;
					filter = null;
				}), (delay != null) ? delay : ((graph.isFastZoomEnabled()) ? ui.wheelZoomDelay : ui.lazyZoomDelay));
			}
		}, 0);
	};

	graph.lazyZoom = function (zoomIn, ignoreCursorPosition, delay) {
		// TODO: Fix ignored cursor position if scrollbars are disabled
		ignoreCursorPosition = ignoreCursorPosition || !graph.scrollbars;

		if (ignoreCursorPosition) {
			cursorPosition = new mxPoint(
				graph.container.offsetLeft + graph.container.clientWidth / 2,
				graph.container.offsetTop + graph.container.clientHeight / 2);
		}

		// Switches to 5% zoom steps below 15%
		if (zoomIn) {
			if (this.view.scale * this.cumulativeZoomFactor <= 0.15) {
				this.cumulativeZoomFactor *= (this.view.scale + 0.05) / this.view.scale;
			}
			else {
				// Uses to 5% zoom steps for better grid rendering in webkit
				// and to avoid rounding errors for zoom steps
				this.cumulativeZoomFactor *= this.zoomFactor;
				this.cumulativeZoomFactor = Math.round(this.view.scale * this.cumulativeZoomFactor * 20) / 20 / this.view.scale;
			}
		}
		else {
			if (this.view.scale * this.cumulativeZoomFactor <= 0.15) {
				this.cumulativeZoomFactor *= (this.view.scale - 0.05) / this.view.scale;
			}
			else {
				// Uses to 5% zoom steps for better grid rendering in webkit
				// and to avoid rounding errors for zoom steps
				this.cumulativeZoomFactor /= this.zoomFactor;
				this.cumulativeZoomFactor = Math.round(this.view.scale * this.cumulativeZoomFactor * 20) / 20 / this.view.scale;
			}
		}

		this.cumulativeZoomFactor = Math.max(0.05, Math.min(this.view.scale * this.cumulativeZoomFactor, 160)) / this.view.scale;

		if (graph.isFastZoomEnabled()) {
			if (filter == null && mainGroup.getAttribute('filter') != '') {
				filter = mainGroup.getAttribute('filter');
				mainGroup.removeAttribute('filter');
			}

			scrollPosition = new mxPoint(graph.container.scrollLeft, graph.container.scrollTop);

			var cx = (ignoreCursorPosition) ? graph.container.scrollLeft + graph.container.clientWidth / 2 :
				cursorPosition.x + graph.container.scrollLeft - graph.container.offsetLeft;
			var cy = (ignoreCursorPosition) ? graph.container.scrollTop + graph.container.clientHeight / 2 :
				cursorPosition.y + graph.container.scrollTop - graph.container.offsetTop;
			mainGroup.style.transformOrigin = cx + 'px ' + cy + 'px';
			mainGroup.style.transform = 'scale(' + this.cumulativeZoomFactor + ')';
			bgGroup.style.transformOrigin = cx + 'px ' + cy + 'px';
			bgGroup.style.transform = 'scale(' + this.cumulativeZoomFactor + ')';

			if (graph.view.backgroundPageShape != null && graph.view.backgroundPageShape.node != null) {
				var page = graph.view.backgroundPageShape.node;

				mxUtils.setPrefixedStyle(page.style, 'transform-origin',
					((ignoreCursorPosition) ? ((graph.container.clientWidth / 2 + graph.container.scrollLeft -
						page.offsetLeft) + 'px') : ((cursorPosition.x + graph.container.scrollLeft -
							page.offsetLeft - graph.container.offsetLeft) + 'px')) + ' ' +
					((ignoreCursorPosition) ? ((graph.container.clientHeight / 2 + graph.container.scrollTop -
						page.offsetTop) + 'px') : ((cursorPosition.y + graph.container.scrollTop -
							page.offsetTop - graph.container.offsetTop) + 'px')));
				mxUtils.setPrefixedStyle(page.style, 'transform',
					'scale(' + this.cumulativeZoomFactor + ')');
			}

			graph.view.getDecoratorPane().style.opacity = '0';
			graph.view.getOverlayPane().style.opacity = '0';

			if (ui.hoverIcons != null) {
				ui.hoverIcons.reset();
			}
		}

		scheduleZoom(delay);
	};

	// Holds back repaint until after mouse gestures
	mxEvent.addGestureListeners(graph.container, function (evt) {
		if (updateZoomTimeout != null) {
			window.clearTimeout(updateZoomTimeout);
		}
	}, null, function (evt) {
		if (graph.cumulativeZoomFactor != 1) {
			scheduleZoom(0);
		}
	});

	// Holds back repaint until scroll ends
	mxEvent.addListener(graph.container, 'scroll', function () {
		if (updateZoomTimeout && !graph.isMouseDown && graph.cumulativeZoomFactor != 1) {
			scheduleZoom(0);
		}
	});

	mxEvent.addMouseWheelListener(mxUtils.bind(this, function (evt, up, force) {
		if (this.dialogs == null || this.dialogs.length == 0) {
			// Scrolls with scrollbars turned off
			if (!graph.scrollbars && graph.isScrollWheelEvent(evt)) {
				var t = graph.view.getTranslate();
				var step = 40 / graph.view.scale;

				if (!mxEvent.isShiftDown(evt)) {
					graph.view.setTranslate(t.x, t.y + ((up) ? step : -step));
				}
				else {
					graph.view.setTranslate(t.x + ((up) ? -step : step), t.y);
				}
			}
			else if (force || graph.isZoomWheelEvent(evt)) {
				var source = mxEvent.getSource(evt);

				while (source != null) {
					if (source == graph.container) {
						graph.tooltipHandler.hideTooltip();
						cursorPosition = new mxPoint(mxEvent.getClientX(evt), mxEvent.getClientY(evt));
						graph.lazyZoom(up);
						mxEvent.consume(evt);

						return false;
					}

					source = source.parentNode;
				}
			}
		}
	}), graph.container);

	// Uses fast zoom for pinch gestures on iOS
	graph.panningHandler.zoomGraph = function (evt) {
		graph.cumulativeZoomFactor = evt.scale;
		graph.lazyZoom(evt.scale > 0, true);
		mxEvent.consume(evt);
	};
};

/**
 * Creates a temporary graph instance for rendering off-screen content.
 */
EditorUi.prototype.addChromelessToolbarItems = function (addButton) {
	addButton(mxUtils.bind(this, function (evt) {
		this.actions.get('print').funct();
		mxEvent.consume(evt);
	}), Editor.printLargeImage, mxResources.get('print'));
};

/**
 * Creates a temporary graph instance for rendering off-screen content.
 */
EditorUi.prototype.createTemporaryGraph = function (stylesheet) {
	var graph = new Graph(document.createElement('div'), null, null, stylesheet);
	graph.resetViewOnRootChange = false;
	graph.setConnectable(false);
	graph.gridEnabled = false;
	graph.autoScroll = false;
	graph.setTooltips(false);
	graph.setEnabled(false);

	// Container must be in the DOM for correct HTML rendering
	graph.container.style.visibility = 'hidden';
	graph.container.style.position = 'absolute';
	graph.container.style.overflow = 'hidden';
	graph.container.style.height = '1px';
	graph.container.style.width = '1px';

	return graph;
};

/**
 *
 */
EditorUi.prototype.addChromelessClickHandler = function () {
	var hl = urlParams['highlight'];

	// Adds leading # for highlight color code
	if (hl != null && hl.length > 0) {
		hl = '#' + hl;
	}

	this.editor.graph.addClickHandler(hl);
};

/**
 *
 */
EditorUi.prototype.toggleFormatPanel = function (forceHide) {
	if (this.format != null) {
		this.formatWidth = (forceHide || this.formatWidth > 0) ? 0 : 240;
		this.formatContainer.style.display = (forceHide || this.formatWidth > 0) ? '' : 'none';
		this.refresh();
		this.format.refresh();
		this.fireEvent(new mxEventObject('formatWidthChanged'));
	}
};

/**
 * Adds support for placeholders in labels.
 */
EditorUi.prototype.lightboxFit = function (maxHeight) {
	if (this.isDiagramEmpty()) {
		this.editor.graph.view.setScale(1);
	}
	else {
		var p = urlParams['border'];
		var border = 60;

		if (p != null) {
			border = parseInt(p);
		}

		// LATER: Use initial graph bounds to avoid rounding errors
		this.editor.graph.maxFitScale = this.lightboxMaxFitScale;
		this.editor.graph.fit(border, null, null, null, null, null, maxHeight);
		this.editor.graph.maxFitScale = null;
	}
};

/**
 * Translates this point by the given vector.
 *
 * @param {number} dx X-coordinate of the translation.
 * @param {number} dy Y-coordinate of the translation.
 */
EditorUi.prototype.isDiagramEmpty = function () {
	var model = this.editor.graph.getModel();

	return model.getChildCount(model.root) == 1 && model.getChildCount(model.getChildAt(model.root, 0)) == 0;
};

/**
 * Hook for allowing selection and context menu for certain events.
 */
EditorUi.prototype.isSelectionAllowed = function (evt) {
	return mxEvent.getSource(evt).nodeName == 'SELECT' || (mxEvent.getSource(evt).nodeName == 'INPUT' &&
		mxUtils.isAncestorNode(this.formatContainer, mxEvent.getSource(evt)));
};

/**
 * Installs dialog if browser window is closed without saving
 * This must be disabled during save and image export.
 */
EditorUi.prototype.addBeforeUnloadListener = function () {
	// Installs dialog if browser window is closed without saving
	// This must be disabled during save and image export
	window.onbeforeunload = mxUtils.bind(this, function () {
		if (!this.editor.isChromelessView()) {
			return this.onBeforeUnload();
		}
	});
};

/**
 * Sets the onbeforeunload for the application
 */
EditorUi.prototype.onBeforeUnload = function () {
	if (this.editor.modified) {
		return mxResources.get('allChangesLost');
	}
};

/**
 * Opens the current diagram via the window.opener if one exists.
 */
EditorUi.prototype.open = function () {
	// Cross-domain window access is not allowed in FF, so if we
	// were opened from another domain then this will fail.
	try {
		if (window.opener != null && window.opener.openFile != null) {
			window.opener.openFile.setConsumer(mxUtils.bind(this, function (xml, filename) {
				try {
					var doc = mxUtils.parseXml(xml);
					this.editor.setGraphXml(doc.documentElement);
					this.editor.setModified(false);
					this.editor.undoManager.clear();

					if (filename != null) {
						this.editor.setFilename(filename);
						this.updateDocumentTitle();
					}

					return;
				}
				catch (e) {
					mxUtils.alert(mxResources.get('invalidOrMissingFile') + ': ' + e.message);
				}
			}));
		}
	}
	catch (e) {
		// ignore
	}

	// Fires as the last step if no file was loaded
	this.editor.graph.view.validate();

	// Required only in special cases where an initial file is opened
	// and the minimumGraphSize changes and CSS must be updated.
	this.editor.graph.sizeDidChange();
	this.editor.fireEvent(new mxEventObject('resetGraphView'));
};

/**
 * Sets the current menu and element.
 */
EditorUi.prototype.setCurrentMenu = function (menu, elt) {
	this.currentMenuElt = elt;
	this.currentMenu = menu;
};

/**
 * Resets the current menu and element.
 */
EditorUi.prototype.resetCurrentMenu = function () {
	this.currentMenuElt = null;
	this.currentMenu = null;
};

/**
 * Hides and destroys the current menu.
 */
EditorUi.prototype.hideCurrentMenu = function () {
	if (this.currentMenu != null) {
		this.currentMenu.hideMenu();
		this.resetCurrentMenu();
	}
};

/**
 * Updates the document title.
 */

EditorUi.prototype.updateDocumentTitle = function () {
	var title = this.editor.getOrCreateFilename();

	if (this.editor.appName != null) {
		title += ' - ' + this.editor.appName;
	}

	document.title = title;
};

/**
 * Updates the document title.
 */
EditorUi.prototype.createHoverIcons = function () {
	main(document.getElementById('graphContainerID'),this.editor.graph)
	return new HoverIcons(this.editor.graph);
};

/**
 * Returns the URL for a copy of this editor with no state.
 */
EditorUi.prototype.redo = function () {
	try {
		var graph = this.editor.graph;

		if (graph.isEditing()) {
			document.execCommand('redo', false, null);
		}
		else {
			this.editor.undoManager.redo();
		}
	}
	catch (e) {
		// ignore all errors
	}
};

/**
 * Returns the URL for a copy of this editor with no state.
 */
EditorUi.prototype.undo = function () {
	try {
		var graph = this.editor.graph;

		if (graph.isEditing()) {
			// Stops editing and executes undo on graph if native undo
			// does not affect current editing value
			var value = graph.cellEditor.textarea.innerHTML;
			document.execCommand('undo', false, null);

			if (value == graph.cellEditor.textarea.innerHTML) {
				graph.stopEditing(true);
				this.editor.undoManager.undo();
			}
		}
		else {
			this.editor.undoManager.undo();
		}
	}
	catch (e) {
		// ignore all errors
	}
};

/**
 * Returns the URL for a copy of this editor with no state.
 */
EditorUi.prototype.canRedo = function () {
	return this.editor.graph.isEditing() || this.editor.undoManager.canRedo();
};

/**
 * Returns the URL for a copy of this editor with no state.
 */
EditorUi.prototype.canUndo = function () {
	return this.editor.graph.isEditing() || this.editor.undoManager.canUndo();
};

/**
 *
 */
EditorUi.prototype.getEditBlankXml = function () {
	return mxUtils.getXml(this.editor.getGraphXml());
};

/**
 * Returns the URL for a copy of this editor with no state.
 */
EditorUi.prototype.getUrl = function (pathname) {
	var href = (pathname != null) ? pathname : window.location.pathname;
	var parms = (href.indexOf('?') > 0) ? 1 : 0;

	// Removes template URL parameter for new blank diagram
	for (var key in urlParams) {
		if (parms == 0) {
			href += '?';
		}
		else {
			href += '&';
		}

		href += key + '=' + urlParams[key];
		parms++;
	}

	return href;
};

/**
 * Specifies if the graph has scrollbars.
 */
EditorUi.prototype.setScrollbars = function (value) {
	var graph = this.editor.graph;
	var prev = graph.container.style.overflow;
	graph.scrollbars = value;
	this.editor.updateGraphComponents();

	if (prev != graph.container.style.overflow) {
		graph.container.scrollTop = 0;
		graph.container.scrollLeft = 0;
		graph.view.scaleAndTranslate(1, 0, 0);
		this.resetScrollbars();
	}

	this.fireEvent(new mxEventObject('scrollbarsChanged'));
};

/**
 * Returns true if the graph has scrollbars.
 */
EditorUi.prototype.hasScrollbars = function () {
	return this.editor.graph.scrollbars;
};

/**
 * Resets the state of the scrollbars.
 */
EditorUi.prototype.resetScrollbars = function () {
	var graph = this.editor.graph;

	if (!this.editor.extendCanvas) {
		graph.container.scrollTop = 0;
		graph.container.scrollLeft = 0;

		if (!mxUtils.hasScrollbars(graph.container)) {
			graph.view.setTranslate(0, 0);
		}
	}
	else if (!this.editor.isChromelessView()) {
		if (mxUtils.hasScrollbars(graph.container)) {
			if (graph.pageVisible) {
				var pad = graph.getPagePadding();
				graph.container.scrollTop = Math.floor(pad.y - this.editor.initialTopSpacing) - 1;
				graph.container.scrollLeft = Math.floor(Math.min(pad.x,
					(graph.container.scrollWidth - graph.container.clientWidth) / 2)) - 1;

				// Scrolls graph to visible area
				var bounds = graph.getGraphBounds();

				if (bounds.width > 0 && bounds.height > 0) {
					if (bounds.x > graph.container.scrollLeft + graph.container.clientWidth * 0.9) {
						graph.container.scrollLeft = Math.min(bounds.x + bounds.width - graph.container.clientWidth, bounds.x - 10);
					}

					if (bounds.y > graph.container.scrollTop + graph.container.clientHeight * 0.9) {
						graph.container.scrollTop = Math.min(bounds.y + bounds.height - graph.container.clientHeight, bounds.y - 10);
					}
				}
			}
			else {
				var bounds = graph.getGraphBounds();
				var width = Math.max(bounds.width, graph.scrollTileSize.width * graph.view.scale);
				var height = Math.max(bounds.height, graph.scrollTileSize.height * graph.view.scale);
				graph.container.scrollTop = Math.floor(Math.max(0, bounds.y - Math.max(20, (graph.container.clientHeight - height) / 4)));
				graph.container.scrollLeft = Math.floor(Math.max(0, bounds.x - Math.max(0, (graph.container.clientWidth - width) / 2)));
			}
		}
		else {
			var b = mxRectangle.fromRectangle((graph.pageVisible) ? graph.view.getBackgroundPageBounds() : graph.getGraphBounds())
			var tr = graph.view.translate;
			var s = graph.view.scale;
			b.x = b.x / s - tr.x;
			b.y = b.y / s - tr.y;
			b.width /= s;
			b.height /= s;

			var dy = (graph.pageVisible) ? 0 : Math.max(0, (graph.container.clientHeight - b.height) / 4);

			graph.view.setTranslate(Math.floor(Math.max(0,
				(graph.container.clientWidth - b.width) / 2) - b.x + 2),
				Math.floor(dy - b.y + 1));
		}
	}
};

/**
 * Loads the stylesheet for this graph.
 */
EditorUi.prototype.setPageVisible = function (value) {
	var graph = this.editor.graph;
	var hasScrollbars = mxUtils.hasScrollbars(graph.container);
	var tx = 0;
	var ty = 0;

	if (hasScrollbars) {
		tx = graph.view.translate.x * graph.view.scale - graph.container.scrollLeft;
		ty = graph.view.translate.y * graph.view.scale - graph.container.scrollTop;
	}

	graph.pageVisible = value;
	graph.pageBreaksVisible = value;
	graph.preferPageSize = value;
	graph.view.validateBackground();

	// Workaround for possible handle offset
	if (hasScrollbars) {
		var cells = graph.getSelectionCells();
		graph.clearSelection();
		graph.setSelectionCells(cells);
	}

	// Calls updatePageBreaks
	graph.sizeDidChange();

	if (hasScrollbars) {
		graph.container.scrollLeft = graph.view.translate.x * graph.view.scale - tx;
		graph.container.scrollTop = graph.view.translate.y * graph.view.scale - ty;
	}

	this.fireEvent(new mxEventObject('pageViewChanged'));
};

/**
 * Change types
 */
function ChangePageSetup(ui, color, image, format, pageScale) {
	this.ui = ui;
	this.color = color;
	this.previousColor = color;
	this.image = image;
	this.previousImage = image;
	this.format = format;
	this.previousFormat = format;
	this.pageScale = pageScale;
	this.previousPageScale = pageScale;

	// Needed since null are valid values for color and image
	this.ignoreColor = false;
	this.ignoreImage = false;
}

/**
 * Implementation of the undoable page rename.
 */
ChangePageSetup.prototype.execute = function () {
	var graph = this.ui.editor.graph;

	if (!this.ignoreColor) {
		this.color = this.previousColor;
		var tmp = graph.background;
		this.ui.setBackgroundColor(this.previousColor);
		this.previousColor = tmp;
	}

	if (!this.ignoreImage) {
		this.image = this.previousImage;
		var tmp = graph.backgroundImage;
		this.ui.setBackgroundImage(this.previousImage);
		this.previousImage = tmp;
	}

	if (this.previousFormat != null) {
		this.format = this.previousFormat;
		var tmp = graph.pageFormat;

		if (this.previousFormat.width != tmp.width ||
			this.previousFormat.height != tmp.height) {
			this.ui.setPageFormat(this.previousFormat);
			this.previousFormat = tmp;
		}
	}

	if (this.foldingEnabled != null && this.foldingEnabled != this.ui.editor.graph.foldingEnabled) {
		this.ui.setFoldingEnabled(this.foldingEnabled);
		this.foldingEnabled = !this.foldingEnabled;
	}

	if (this.previousPageScale != null) {
		var currentPageScale = this.ui.editor.graph.pageScale;

		if (this.previousPageScale != currentPageScale) {
			this.ui.setPageScale(this.previousPageScale);
			this.previousPageScale = currentPageScale;
		}
	}
};

// Registers codec for ChangePageSetup
(function () {
	var codec = new mxObjectCodec(new ChangePageSetup(), ['ui', 'previousColor', 'previousImage', 'previousFormat', 'previousPageScale']);

	codec.afterDecode = function (dec, node, obj) {
		obj.previousColor = obj.color;
		obj.previousImage = obj.image;
		obj.previousFormat = obj.format;
		obj.previousPageScale = obj.pageScale;

		if (obj.foldingEnabled != null) {
			obj.foldingEnabled = !obj.foldingEnabled;
		}

		return obj;
	};

	mxCodecRegistry.register(codec);
})();

/**
 * Loads the stylesheet for this graph.
 */
EditorUi.prototype.setBackgroundColor = function (value) {
	this.editor.graph.background = value;
	this.editor.graph.view.validateBackground();

	this.fireEvent(new mxEventObject('backgroundColorChanged'));
};

/**
 * Loads the stylesheet for this graph.
 */
EditorUi.prototype.setFoldingEnabled = function (value) {
	this.editor.graph.foldingEnabled = value;
	this.editor.graph.view.revalidate();

	this.fireEvent(new mxEventObject('foldingEnabledChanged'));
};

/**
 * Loads the stylesheet for this graph.
 */
EditorUi.prototype.setPageFormat = function (value) {
	this.editor.graph.pageFormat = value;

	if (!this.editor.graph.pageVisible) {
		this.actions.get('pageView').funct();
	}
	else {
		this.editor.graph.view.validateBackground();
		this.editor.graph.sizeDidChange();
	}

	this.fireEvent(new mxEventObject('pageFormatChanged'));
};

/**
 * Loads the stylesheet for this graph.
 */
EditorUi.prototype.setPageScale = function (value) {
	this.editor.graph.pageScale = value;

	if (!this.editor.graph.pageVisible) {
		this.actions.get('pageView').funct();
	}
	else {
		this.editor.graph.view.validateBackground();
		this.editor.graph.sizeDidChange();
	}

	this.fireEvent(new mxEventObject('pageScaleChanged'));
};

/**
 * Loads the stylesheet for this graph.
 */
EditorUi.prototype.setGridColor = function (value) {
	this.editor.graph.view.gridColor = value;
	this.editor.graph.view.validateBackground();
	this.fireEvent(new mxEventObject('gridColorChanged'));
};

/**
 * Updates the states of the given undo/redo items.
 */
EditorUi.prototype.addUndoListener = function () {
	var undo = this.actions.get('undo');
	var redo = this.actions.get('redo');

	var undoMgr = this.editor.undoManager;

	var undoListener = mxUtils.bind(this, function () {
		undo.setEnabled(this.canUndo());
		redo.setEnabled(this.canRedo());
	});

	undoMgr.addListener(mxEvent.ADD, undoListener);
	undoMgr.addListener(mxEvent.UNDO, undoListener);
	undoMgr.addListener(mxEvent.REDO, undoListener);
	undoMgr.addListener(mxEvent.CLEAR, undoListener);

	// Overrides cell editor to update action states
	var cellEditorStartEditing = this.editor.graph.cellEditor.startEditing;

	this.editor.graph.cellEditor.startEditing = function () {
		cellEditorStartEditing.apply(this, arguments);
		undoListener();
	};

	var cellEditorStopEditing = this.editor.graph.cellEditor.stopEditing;

	this.editor.graph.cellEditor.stopEditing = function (cell, trigger) {
		cellEditorStopEditing.apply(this, arguments);
		undoListener();
	};

	// Updates the button states once
	undoListener();
};

/**
* Updates the states of the given toolbar items based on the selection.
*/
EditorUi.prototype.updateActionStates = function () {
	var graph = this.editor.graph;
	var selected = !graph.isSelectionEmpty();
	var vertexSelected = false;
	var edgeSelected = false;

	var cells = graph.getSelectionCells();

	if (cells != null) {
		for (var i = 0; i < cells.length; i++) {
			var cell = cells[i];

			if (graph.getModel().isEdge(cell)) {
				edgeSelected = true;
			}

			if (graph.getModel().isVertex(cell)) {
				vertexSelected = true;
			}

			if (edgeSelected && vertexSelected) {
				break;
			}
		}
	}

	// Updates action states
	var actions = ['cut', 'copy', 'bold', 'italic', 'underline', 'delete', 'duplicate',
		'editStyle', 'editTooltip', 'editLink', 'backgroundColor', 'borderColor',
		'edit', 'toFront', 'toBack', 'lockUnlock', 'solid', 'dashed', 'pasteSize',
		'dotted', 'fillColor', 'gradientColor', 'shadow', 'fontColor',
		'formattedText', 'rounded', 'toggleRounded', 'sharp', 'strokeColor'];

	for (var i = 0; i < actions.length; i++) {
		this.actions.get(actions[i]).setEnabled(selected);
	}

	this.actions.get('setAsDefaultStyle').setEnabled(graph.getSelectionCount() == 1);
	this.actions.get('clearWaypoints').setEnabled(!graph.isSelectionEmpty());
	this.actions.get('copySize').setEnabled(graph.getSelectionCount() == 1);
	this.actions.get('turn').setEnabled(!graph.isSelectionEmpty());
	this.actions.get('curved').setEnabled(edgeSelected);
	this.actions.get('rotation').setEnabled(vertexSelected);
	this.actions.get('wordWrap').setEnabled(vertexSelected);
	this.actions.get('autosize').setEnabled(vertexSelected);
	var oneVertexSelected = vertexSelected && graph.getSelectionCount() == 1;
	this.actions.get('group').setEnabled(graph.getSelectionCount() > 1 ||
		(oneVertexSelected && !graph.isContainer(graph.getSelectionCell())));
	this.actions.get('ungroup').setEnabled(graph.getSelectionCount() == 1 &&
		(graph.getModel().getChildCount(graph.getSelectionCell()) > 0 ||
			(oneVertexSelected && graph.isContainer(graph.getSelectionCell()))));
	this.actions.get('removeFromGroup').setEnabled(oneVertexSelected &&
		graph.getModel().isVertex(graph.getModel().getParent(graph.getSelectionCell())));

	// Updates menu states
	var state = graph.view.getState(graph.getSelectionCell());
	this.menus.get('navigation').setEnabled(selected || graph.view.currentRoot != null);
	this.actions.get('collapsible').setEnabled(vertexSelected &&
		(graph.isContainer(graph.getSelectionCell()) || graph.model.getChildCount(graph.getSelectionCell()) > 0));
	this.actions.get('home').setEnabled(graph.view.currentRoot != null);
	this.actions.get('exitGroup').setEnabled(graph.view.currentRoot != null);
	this.actions.get('enterGroup').setEnabled(graph.getSelectionCount() == 1 && graph.isValidRoot(graph.getSelectionCell()));
	var foldable = graph.getSelectionCount() == 1 && graph.isCellFoldable(graph.getSelectionCell());
	this.actions.get('expand').setEnabled(foldable);
	this.actions.get('collapse').setEnabled(foldable);
	this.actions.get('editLink').setEnabled(graph.getSelectionCount() == 1);
	this.actions.get('openLink').setEnabled(graph.getSelectionCount() == 1 &&
		graph.getLinkForCell(graph.getSelectionCell()) != null);
	this.actions.get('guides').setEnabled(graph.isEnabled());
	this.actions.get('grid').setEnabled(!this.editor.chromeless || this.editor.editable);

	var unlocked = graph.isEnabled() && !graph.isCellLocked(graph.getDefaultParent());
	this.menus.get('layout').setEnabled(unlocked);
	this.menus.get('insert').setEnabled(unlocked);
	this.menus.get('direction').setEnabled(unlocked && vertexSelected);
	this.menus.get('align').setEnabled(unlocked && vertexSelected && graph.getSelectionCount() > 1);
	this.menus.get('distribute').setEnabled(unlocked && vertexSelected && graph.getSelectionCount() > 1);
	this.actions.get('selectVertices').setEnabled(unlocked);
	this.actions.get('selectEdges').setEnabled(unlocked);
	this.actions.get('selectAll').setEnabled(unlocked);
	this.actions.get('selectNone').setEnabled(unlocked);

	this.updatePasteActionStates();
};

EditorUi.prototype.zeroOffset = new mxPoint(0, 0);

EditorUi.prototype.getDiagramContainerOffset = function () {
	return this.zeroOffset;
};

/**
 * Refreshes the viewport.
 */
EditorUi.prototype.refresh = function (sizeDidChange) {
	sizeDidChange = (sizeDidChange != null) ? sizeDidChange : true;

	var quirks = mxClient.IS_IE && (document.documentMode == null || document.documentMode == 5);
	var w = this.container.clientWidth;
	var h = this.container.clientHeight;

	if (this.container == document.body) {
		w = document.body.clientWidth || document.documentElement.clientWidth;
		h = (quirks) ? document.body.clientHeight || document.documentElement.clientHeight : document.documentElement.clientHeight;
	}

	// Workaround for bug on iOS see
	// http://stackoverflow.com/questions/19012135/ios-7-ipad-safari-landscape-innerheight-outerheight-layout-issue
	// FIXME: Fix if footer visible
	var off = 0;

	if (mxClient.IS_IOS && !window.navigator.standalone) {
		if (window.innerHeight != document.documentElement.clientHeight) {
			off = document.documentElement.clientHeight - window.innerHeight;
			window.scrollTo(0, 0);
		}
	}

	var effHsplitPosition = Math.max(0, Math.min(this.hsplitPosition, w - this.splitSize - 20));
	var tmp = 0;

	if (this.menubar != null) {
		this.menubarContainer.style.height = this.menubarHeight + 'px';
		tmp += this.menubarHeight;
	}

	if (this.toolbar != null) {
		this.toolbarContainer.style.top = '10rem';
		this.toolbarContainer.style.height = this.toolbarHeight + 'px';
		tmp += this.toolbarHeight;
	}

	if (tmp > 0 && !mxClient.IS_QUIRKS) {
		tmp += 1;
	}

	var sidebarFooterHeight = 0;

	if (this.sidebarFooterContainer != null) {
		var bottom = this.footerHeight + off;
		sidebarFooterHeight = Math.max(0, Math.min(h - tmp - bottom, this.sidebarFooterHeight));
		this.sidebarFooterContainer.style.width = effHsplitPosition + 'px';
		this.sidebarFooterContainer.style.height = sidebarFooterHeight + 'px';
		this.sidebarFooterContainer.style.bottom = bottom + 'px';
	}

	var fw = (this.format != null) ? this.formatWidth : 0;
	this.sidebarContainer.style.top = '12.5rem';
	this.sidebarContainer.style.width = effHsplitPosition + 'px';
	this.formatContainer.style.top = '10rem';
	this.formatContainer.style.width = fw + 'px';
	this.formatContainer.style.display = (this.format != null) ? '' : 'none';

	var diagContOffset = this.getDiagramContainerOffset();
	var contLeft = (this.hsplit.parentNode != null) ? (effHsplitPosition + this.splitSize) : 0;
	this.diagramContainer.style.left = (contLeft + diagContOffset.x) + 'px';
	this.diagramContainer.style.top = '10rem';
	this.footerContainer.style.height = this.footerHeight + 'px';
	this.hsplit.style.top = this.sidebarContainer.style.top;
	this.hsplit.style.bottom = (this.footerHeight + off) + 'px';
	this.hsplit.style.left = effHsplitPosition + 'px';
	this.footerContainer.style.display = 'none';

	if (this.tabContainer != null) {
		this.tabContainer.style.left = contLeft + 'px';
	}

	if (quirks) {
		this.menubarContainer.style.width = w + 'px';
		this.toolbarContainer.style.width = this.menubarContainer.style.width;
		var sidebarHeight = Math.max(0, h - this.footerHeight - this.menubarHeight - this.toolbarHeight);
		this.sidebarContainer.style.height = (sidebarHeight - sidebarFooterHeight) + 'px';
		this.formatContainer.style.height = sidebarHeight + 'px';
		this.diagramContainer.style.width = (this.hsplit.parentNode != null) ? Math.max(0, w - effHsplitPosition - this.splitSize - fw) + 'px' : w + 'px';
		this.footerContainer.style.width = this.menubarContainer.style.width;
		var diagramHeight = Math.max(0, h - this.footerHeight - this.menubarHeight - this.toolbarHeight);

		if (this.tabContainer != null) {
			this.tabContainer.style.width = this.diagramContainer.style.width;
			this.tabContainer.style.bottom = (this.footerHeight + off) + 'px';
			diagramHeight -= this.tabContainer.clientHeight;
		}

		this.diagramContainer.style.height = diagramHeight + 'px';
		this.hsplit.style.height = diagramHeight + 'px';
	}
	else {
		if (this.footerHeight > 0) {
			this.footerContainer.style.bottom = off + 'px';
		}

		this.diagramContainer.style.right = fw + 'px';
		var th = 0;

		if (this.tabContainer != null) {
			this.tabContainer.style.bottom = (this.footerHeight + off) + 'px';
			this.tabContainer.style.right = this.diagramContainer.style.right;
			th = this.tabContainer.clientHeight;
		}

		this.sidebarContainer.style.bottom = (this.footerHeight + sidebarFooterHeight + off) + 'px';
		this.formatContainer.style.bottom = (this.footerHeight + off) + 'px';
		this.diagramContainer.style.bottom = (this.footerHeight + off + th) + 'px';
	}

	if (sizeDidChange) {
		this.editor.graph.sizeDidChange();
	}
};

/**
 * Creates the required containers.
 */
EditorUi.prototype.createTabContainer = function () {
	return null;
};

/**
 * Creates the required containers.
 */
EditorUi.prototype.createDivs = function () {
	this.menubarContainer = this.createDiv('geMenubarContainer');
	this.toolbarContainer = this.createDiv('geToolbarContainer');
	this.sidebarContainer = this.createDiv('geSidebarContainer');
	this.formatContainer = this.createDiv('geSidebarContainer geFormatContainer');
	this.diagramContainer = this.createDiv('geDiagramContainer');
	this.footerContainer = this.createDiv('geFooterContainer');
	this.hsplit = this.createDiv('geHsplit');
	this.hsplit.setAttribute('title', mxResources.get('collapseExpand'));

	// Sets static style for containers
	this.menubarContainer.style.top = '8rem';
	this.menubarContainer.style.width = '45px';
	this.menubarContainer.style.left = '6%';
	this.menubarContainer.style.right = '0px';
	this.toolbarContainer.style.top = '10rem';
	this.toolbarContainer.style.left = '6%';
	this.toolbarContainer.style.right = '0px';
	this.sidebarContainer.style.top = '10rem';
	this.sidebarContainer.style.left = '6%';
	this.formatContainer.style.top = '10rem';
	this.formatContainer.style.right = '0px';
	this.formatContainer.style.zIndex = '1';
	this.diagramContainer.style.top = '10rem';
	this.diagramContainer.style.right = ((this.format != null) ? this.formatWidth : 0) + 'px';
	this.footerContainer.style.left = '0px';
	this.footerContainer.style.right = '0px';
	this.footerContainer.style.bottom = '0px';
	this.footerContainer.style.zIndex = mxPopupMenu.prototype.zIndex - 2;
	this.hsplit.style.top = '10rem';
	this.hsplit.style.width = this.splitSize + 'px';
	this.sidebarFooterContainer = this.createSidebarFooterContainer();

	if (this.sidebarFooterContainer) {
		this.sidebarFooterContainer.style.left = '0px';
	}

	if (!this.editor.chromeless) {
		this.tabContainer = this.createTabContainer();
	}
	else {
		this.diagramContainer.style.border = 'none';
	}
};

/**
 * Hook for sidebar footer container. This implementation returns null.
 */
EditorUi.prototype.createSidebarFooterContainer = function () {
	return null;
};

/**
 * Creates the required containers.
 */
EditorUi.prototype.createUi = function () {
	// Creates menubar
	this.menubar = (this.editor.chromeless) ? null : this.menus.createMenubar(this.createDiv('geMenubar'));

	if (this.menubar != null) {
		this.menubarContainer.appendChild(this.menubar.container);
	}

	// Adds status bar in menubar
	if (this.menubar != null) {
		this.statusContainer = this.createStatusContainer();

		// Connects the status bar to the editor status
		this.editor.addListener('statusChanged', mxUtils.bind(this, function () {
			this.setStatusText(this.editor.getStatus());
		}));

		this.setStatusText(this.editor.getStatus());
		this.menubar.container.appendChild(this.statusContainer);

		// Inserts into DOM
		this.container.appendChild(this.menubarContainer);
	}

	// Creates the sidebar
	this.sidebar = (this.editor.chromeless) ? null : this.createSidebar(this.sidebarContainer);

	if (this.sidebar != null) {
		this.container.appendChild(this.sidebarContainer);
	}

	// Creates the format sidebar
	this.format = (this.editor.chromeless || !this.formatEnabled) ? null : this.createFormat(this.formatContainer);

	if (this.format != null) {
		this.container.appendChild(this.formatContainer);
	}

	// Creates the footer
	var footer = (this.editor.chromeless) ? null : this.createFooter();

	if (footer != null) {
		this.footerContainer.appendChild(footer);
		this.container.appendChild(this.footerContainer);
	}

	if (this.sidebar != null && this.sidebarFooterContainer) {
		this.container.appendChild(this.sidebarFooterContainer);
	}

	this.container.appendChild(this.diagramContainer);

	if (this.container != null && this.tabContainer != null) {
		this.container.appendChild(this.tabContainer);
	}

	// Creates toolbar
	this.toolbar = (this.editor.chromeless) ? null : this.createToolbar(this.createDiv('geToolbar'));

	if (this.toolbar != null) {
		this.toolbarContainer.appendChild(this.toolbar.container);
		this.container.appendChild(this.toolbarContainer);
	}

	// HSplit
	if (this.sidebar != null) {
		this.container.appendChild(this.hsplit);

		this.addSplitHandler(this.hsplit, true, 0, mxUtils.bind(this, function (value) {
			this.hsplitPosition = value;
			this.refresh();
		}));
	}
};

/**
 * Creates a new toolbar for the given container.
 */
EditorUi.prototype.createStatusContainer = function () {
	var container = document.createElement('a');
	container.className = 'geItem geStatus';

	if (screen.width < 420) {
		container.style.maxWidth = Math.max(20, screen.width - 320) + 'px';
		container.style.overflow = 'hidden';
	}

	return container;
};

/**
 * Creates a new toolbar for the given container.
 */
EditorUi.prototype.setStatusText = function (value) {
	this.statusContainer.innerHTML = value;
};

/**
 * Creates a new toolbar for the given container.
 */
EditorUi.prototype.createToolbar = function (container) {
	return new Toolbar(this, container);
};

/**
 * Creates a new sidebar for the given container.
 */
EditorUi.prototype.createSidebar = function (container) {
	return new Sidebar(this, container);
};

/**
 * Creates a new sidebar for the given container.
 */
EditorUi.prototype.createFormat = function (container) {
	return new Format(this, container);
};

/**
 * Creates and returns a new footer.
 */
EditorUi.prototype.createFooter = function () {
	return this.createDiv('geFooter');
};

/**
 * Creates the actual toolbar for the toolbar container.
 */
EditorUi.prototype.createDiv = function (classname) {
	var elt = document.createElement('div');
	elt.className = classname;

	return elt;
};

/**
 * Updates the states of the given undo/redo items.
 */
EditorUi.prototype.addSplitHandler = function (elt, horizontal, dx, onChange) {
	var start = null;
	var initial = null;
	var ignoreClick = true;
	var last = null;

	// Disables built-in pan and zoom in IE10 and later
	if (mxClient.IS_POINTER) {
		elt.style.touchAction = 'none';
	}

	var getValue = mxUtils.bind(this, function () {
		var result = parseInt(((horizontal) ? elt.style.left : elt.style.bottom));

		// Takes into account hidden footer
		if (!horizontal) {
			result = result + dx - this.footerHeight;
		}

		return result;
	});

	function moveHandler(evt) {
		if (start != null) {
			var pt = new mxPoint(mxEvent.getClientX(evt), mxEvent.getClientY(evt));
			onChange(Math.max(0, initial + ((horizontal) ? (pt.x - start.x) : (start.y - pt.y)) - dx));
			mxEvent.consume(evt);

			if (initial != getValue()) {
				ignoreClick = true;
				last = null;
			}
		}
	};

	function dropHandler(evt) {
		moveHandler(evt);
		initial = null;
		start = null;
	};

	mxEvent.addGestureListeners(elt, function (evt) {
		start = new mxPoint(mxEvent.getClientX(evt), mxEvent.getClientY(evt));
		initial = getValue();
		ignoreClick = false;
		mxEvent.consume(evt);
	});

	mxEvent.addListener(elt, 'click', mxUtils.bind(this, function (evt) {
		if (!ignoreClick && this.hsplitClickEnabled) {
			var next = (last != null) ? last - dx : 0;
			last = getValue();
			onChange(next);
			mxEvent.consume(evt);
		}
	}));

	mxEvent.addGestureListeners(document, null, moveHandler, dropHandler);

	this.destroyFunctions.push(function () {
		mxEvent.removeGestureListeners(document, null, moveHandler, dropHandler);
	});
};

/**
 * Translates this point by the given vector.
 *
 * @param {number} dx X-coordinate of the translation.
 * @param {number} dy Y-coordinate of the translation.
 */
EditorUi.prototype.handleError = function (resp, title, fn, invokeFnOnClose, notFoundMessage) {
	var e = (resp != null && resp.error != null) ? resp.error : resp;

	if (e != null || title != null) {
		var msg = mxUtils.htmlEntities(mxResources.get('unknownError'));
		var btn = mxResources.get('ok');
		title = (title != null) ? title : mxResources.get('error');

		if (e != null && e.message != null) {
			msg = mxUtils.htmlEntities(e.message);
		}

		this.showError(title, msg, btn, fn, null, null, null, null, null,
			null, null, null, (invokeFnOnClose) ? fn : null);
	}
	else if (fn != null) {
		fn();
	}
};

/**
 * Translates this point by the given vector.
 *
 * @param {number} dx X-coordinate of the translation.
 * @param {number} dy Y-coordinate of the translation.
 */
EditorUi.prototype.showError = function (title, msg, btn, fn, retry, btn2, fn2, btn3, fn3, w, h, hide, onClose) {
	var dlg = new ErrorDialog(this, title, msg, btn || mxResources.get('ok'),
		fn, retry, btn2, fn2, hide, btn3, fn3);
	var lines = Math.ceil((msg != null) ? msg.length / 50 : 1);
	this.showDialog(dlg.container, w || 340, h || (100 + lines * 20), true, false, onClose);
	dlg.init();
};

/**
 * Displays a print dialog.
 */
EditorUi.prototype.showDialog = function (elt, w, h, modal, closable, onClose, noScroll, transparent, onResize, ignoreBgClick) {
	this.editor.graph.tooltipHandler.hideTooltip();

	if (this.dialogs == null) {
		this.dialogs = [];
	}

	this.dialog = new Dialog(this, elt, w, h, modal, closable, onClose, noScroll, transparent, onResize, ignoreBgClick);
	this.dialogs.push(this.dialog);
};

/**
 * Displays a print dialog.
 */
EditorUi.prototype.hideDialog = function (cancel, isEsc) {
	if (this.dialogs != null && this.dialogs.length > 0) {
		var dlg = this.dialogs.pop();

		if (dlg.close(cancel, isEsc) == false) {
			//add the dialog back if dialog closing is cancelled
			this.dialogs.push(dlg);
			return;
		}

		this.dialog = (this.dialogs.length > 0) ? this.dialogs[this.dialogs.length - 1] : null;
		this.editor.fireEvent(new mxEventObject('hideDialog'));

		if (this.dialog == null && this.editor.graph.container.style.visibility != 'hidden') {
			window.setTimeout(mxUtils.bind(this, function () {
				if (this.editor.graph.isEditing() && this.editor.graph.cellEditor.textarea != null) {
					this.editor.graph.cellEditor.textarea.focus();
				}
				else {
					mxUtils.clearSelection();
					this.editor.graph.container.focus();
				}
			}), 0);
		}
	}
};

/**
 * Display a color dialog.
 */
EditorUi.prototype.pickColor = function (color, apply) {
	var graph = this.editor.graph;
	var selState = graph.cellEditor.saveSelection();
	var h = 226 + ((Math.ceil(ColorDialog.prototype.presetColors.length / 12) +
		Math.ceil(ColorDialog.prototype.defaultColors.length / 12)) * 17);

	var dlg = new ColorDialog(this, color || 'none', function (color) {
		graph.cellEditor.restoreSelection(selState);
		apply(color);
	}, function () {
		graph.cellEditor.restoreSelection(selState);
	});
	this.showDialog(dlg.container, 230, h, true, false);
	dlg.init();
};

/**
 * Adds the label menu items to the given menu and parent.
 */
EditorUi.prototype.openFile = function () {
	// Closes dialog after open
	window.openFile = new OpenFile(mxUtils.bind(this, function (cancel) {
		this.hideDialog(cancel);
	}));

	// Removes openFile if dialog is closed
	this.showDialog(new OpenDialog(this).container, (Editor.useLocalStorage) ? 640 : 320,
		(Editor.useLocalStorage) ? 480 : 220, true, true, function () {
			window.openFile = null;
		});
};

/**
 * Extracs the graph model from the given HTML data from a data transfer event.
 */
EditorUi.prototype.extractGraphModelFromHtml = function (data) {
	var result = null;

	try {
		var idx = data.indexOf('&lt;mxGraphModel ');

		if (idx >= 0) {
			var idx2 = data.lastIndexOf('&lt;/mxGraphModel&gt;');

			if (idx2 > idx) {
				result = data.substring(idx, idx2 + 21).replace(/&gt;/g, '>').
					replace(/&lt;/g, '<').replace(/\\&quot;/g, '"').replace(/\n/g, '');
			}
		}
	}
	catch (e) {
		// ignore
	}

	return result;
};

/**
 * Opens the given files in the editor.
 */
EditorUi.prototype.extractGraphModelFromEvent = function (evt) {
	var result = null;
	var data = null;

	if (evt != null) {
		var provider = (evt.dataTransfer != null) ? evt.dataTransfer : evt.clipboardData;

		if (provider != null) {
			if (document.documentMode == 10 || document.documentMode == 11) {
				data = provider.getData('Text');
			}
			else {
				data = (mxUtils.indexOf(provider.types, 'text/html') >= 0) ? provider.getData('text/html') : null;

				if (mxUtils.indexOf(provider.types, 'text/plain' && (data == null || data.length == 0))) {
					data = provider.getData('text/plain');
				}
			}

			if (data != null) {
				data = Graph.zapGremlins(mxUtils.trim(data));

				// Tries parsing as HTML document with embedded XML
				var xml = this.extractGraphModelFromHtml(data);

				if (xml != null) {
					data = xml;
				}
			}
		}
	}

	if (data != null && this.isCompatibleString(data)) {
		result = data;
	}

	return result;
};

/**
 * Hook for subclassers to return true if event data is a supported format.
 * This implementation always returns false.
 */
EditorUi.prototype.isCompatibleString = function (data) {
	return false;
};

/**
 * Adds the label menu items to the given menu and parent.
 */
EditorUi.prototype.saveFile = function (forceDialog) {
	if (!forceDialog && this.editor.filename != null) {
		this.save(this.editor.getOrCreateFilename());
	}else if(!forceDialog && window.location.href.includes('processGraphModule')){
		this.save(name= 'Drawing1.xml');
	}
	else {
		var dlg = new FilenameDialog(this, this.editor.getOrCreateFilename(), mxResources.get('save'), mxUtils.bind(this, function (name) {
			this.save(name);
		}), null, mxUtils.bind(this, function (name) {
			if (name != null && name.length > 0) {
				return true;
			}

			mxUtils.confirm(mxResources.get('invalidName'));

			return false;
		}));
		this.showDialog(dlg.container, 300, 100, true, true);
		dlg.init();
	}
};

/**
 * Saves the current graph under the given filename.
 */


EditorUi.prototype.save = function (name) {
	var  THIS = this
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
		url: `/users/${app_code2}/${current_dev_mode2}/processGraphModule/`,
		data: {
		  'operation': "fetchDependencies",
		  'item_group_code':$('#graphContainerID').attr('data-process_code'),
		},
		type: "POST",
		dataType: "json",
		success: function (data) {
		  if (data.appDependency.length > 0) {
			$('#dependencyTable').empty()
			for(var i=0;i<data.appDependency.length;i++){
				$('#dependencyTable').append(`<tr><td style="font-weight:bold">${i+1}.</td><td style="font-weight:bold;text-align:start">&nbsp;&nbsp;${data.appDependency[i]}</td></tr>`)
			}
			if($('#dependencyChecker').attr("save") != "no"){
				$('#dependencyChecker').modal('show')
			}
			  $('#btn_dependencySave').off('click').on('click',function(){
				if (name != null) {
					if (THIS.editor.graph.isEditing()) {
						THIS.editor.graph.stopEditing();
					}

					var xml = mxUtils.getXml(THIS.editor.getGraphXml());
					parser = new DOMParser();
					var xmlDoc = parser.parseFromString(xml, "text/xml");
					var processCode=$('#graphContainerID').attr('data-process_code')
					var subprocessName=$('#graphContainerID').attr('data-sub_process_name')
					var subprocessCode=$('#graphContainerID').attr('data-subprocess_code')
					try {
						if (Editor.useLocalStorage) {
							if (localStorage.getItem(name) != null &&
								!mxUtils.confirm(mxResources.get('replaceIt', [name]))) {
								return;

							}

							localStorage.setItem(name, xml);
							THIS.editor.setStatus(mxUtils.htmlEntities(mxResources.get('saved')) + ' ' + new Date());
							var data = localstorage.getItem(name)
						}
						else {
							if (xml.length < MAX_REQUEST_SIZE) {
								// new mxXmlRequest(SAVE_URL, 'filename=' + encodeURIComponent(name) +
								// 	'&xml=' + encodeURIComponent(xml)).simulate(document, '_blank');
								new mxXmlRequest(SAVE_URL, 'filename=' + encodeURIComponent(name) +
									'&xml=' + xml+"&processCode="+processCode+"&subprocessName="+subprocessName+"&subprocessCode="+subprocessCode).simulate(document, '_self');
							}
							else {
								mxUtils.alert(mxResources.get('drawingTooLarge'));
								mxUtils.popup(xml);
								return;
							}
							var data = localstorage.getItem(name)
						}
						THIS.editor.setModified(false);
						THIS.editor.setFilename(name);
						THIS.updateDocumentTitle();
					}
					catch (e) {
						THIS.editor.setStatus(mxUtils.htmlEntities(mxResources.get('errorSavingFile')));
					}
				}
			})
		  } else {
			if (name != null) {
				if (THIS.editor.graph.isEditing()) {
					THIS.editor.graph.stopEditing();
				}

				var xml = mxUtils.getXml(THIS.editor.getGraphXml());
				parser = new DOMParser();
				var xmlDoc = parser.parseFromString(xml, "text/xml");
				var processCode=$('#graphContainerID').attr('data-process_code')
				var subprocessName=$('#graphContainerID').attr('data-sub_process_name')
				try {
					if (Editor.useLocalStorage) {
						if (localStorage.getItem(name) != null &&
							!mxUtils.confirm(mxResources.get('replaceIt', [name]))) {
							return;

						}
						localStorage.setItem(name, xml);
						THIS.editor.setStatus(mxUtils.htmlEntities(mxResources.get('saved')) + ' ' + new Date());
						var data = localstorage.getItem(name)
					}
					else {
						if (xml.length < MAX_REQUEST_SIZE) {
							// new mxXmlRequest(SAVE_URL, 'filename=' + encodeURIComponent(name) +
							// 	'&xml=' + encodeURIComponent(xml)).simulate(document, '_blank');
							new mxXmlRequest(SAVE_URL, 'filename=' + encodeURIComponent(name) +
								'&xml=' + xml+"&processCode="+processCode+"&subprocessName="+subprocessName).simulate(document, '_self');
						}
						else {
							mxUtils.alert(mxResources.get('drawingTooLarge'));
							mxUtils.popup(xml);
							return;
						}
						var data = localstorage.getItem(name)
					}
					THIS.editor.setModified(false);
					THIS.editor.setFilename(name);
					THIS.updateDocumentTitle();
				}
				catch (e) {
					THIS.editor.setStatus(mxUtils.htmlEntities(mxResources.get('errorSavingFile')));
				}
			}
		  }
		},
		error: function () {
		  alert("Error");
		}
	  });
	  xml_sent = mxUtils.getXml(THIS.editor.getGraphXml());

};



/**
 * Executes the given layout.
 */
EditorUi.prototype.executeLayout = function (exec, animate, post) {
	var graph = this.editor.graph;

	if (graph.isEnabled()) {
		graph.getModel().beginUpdate();
		try {
			exec();
		}
		catch (e) {
			throw e;
		}
		finally {
			// Animates the changes in the graph model except
			// for Camino, where animation is too slow
			if (this.allowAnimation && animate && (navigator.userAgent == null ||
				navigator.userAgent.indexOf('Camino') < 0)) {
				// New API for animating graph layout results asynchronously
				var morph = new mxMorphing(graph);
				morph.addListener(mxEvent.DONE, mxUtils.bind(this, function () {
					graph.getModel().endUpdate();

					if (post != null) {
						post();
					}
				}));

				morph.startAnimation();
			}
			else {
				graph.getModel().endUpdate();

				if (post != null) {
					post();
				}
			}
		}
	}
};

/**
 * Hides the current menu.
 */
EditorUi.prototype.showImageDialog = function (title, value, fn, ignoreExisting) {
	var cellEditor = this.editor.graph.cellEditor;
	var selState = cellEditor.saveSelection();
	var newValue = mxUtils.prompt(title, value);
	cellEditor.restoreSelection(selState);

	if (newValue != null && newValue.length > 0) {
		var img = new Image();

		img.onload = function () {
			fn(newValue, img.width, img.height);
		};
		img.onerror = function () {
			fn(null);
			mxUtils.alert(mxResources.get('fileNotFound'));
		};

		img.src = newValue;
	}
	else {
		fn(null);
	}
};

/**
 * Hides the current menu.
 */
EditorUi.prototype.showLinkDialog = function (value, btnLabel, fn) {
	var dlg = new LinkDialog(this, value, btnLabel, fn);
	this.showDialog(dlg.container, 420, 90, true, true);
	dlg.init();
};

/**
 * Hides the current menu.
 */
EditorUi.prototype.showDataDialog = function (cell) {
	if (cell != null) {
		var dlg = new EditDataDialog(this, cell);
		this.showDialog(dlg.container, 480, 420, true, false, null, false);
		dlg.init();
	}
};

/**
 * Hides the current menu.
 */
EditorUi.prototype.showBackgroundImageDialog = function (apply) {
	apply = (apply != null) ? apply : mxUtils.bind(this, function (image) {
		var change = new ChangePageSetup(this, null, image);
		change.ignoreColor = true;

		this.editor.graph.model.execute(change);
	});

	var newValue = mxUtils.prompt(mxResources.get('backgroundImage'), '');

	if (newValue != null && newValue.length > 0) {
		var img = new Image();

		img.onload = function () {
			apply(new mxImage(newValue, img.width, img.height));
		};
		img.onerror = function () {
			apply(null);
			mxUtils.alert(mxResources.get('fileNotFound'));
		};

		img.src = newValue;
	}
	else {
		apply(null);
	}
};

/**
 * Loads the stylesheet for this graph.
 */
EditorUi.prototype.setBackgroundImage = function (image) {
	this.editor.graph.setBackgroundImage(image);
	this.editor.graph.view.validateBackgroundImage();

	this.fireEvent(new mxEventObject('backgroundImageChanged'));
};

/**
 * Creates the keyboard event handler for the current graph and history.
 */
EditorUi.prototype.confirm = function (msg, okFn, cancelFn) {
	if (mxUtils.confirm(msg)) {
		if (okFn != null) {
			okFn();
		}
	}
	else if (cancelFn != null) {
		cancelFn();
	}
};

/**
 * Creates the keyboard event handler for the current graph and history.
 */
EditorUi.prototype.createOutline = function (wnd) {
	var outline = new mxOutline(this.editor.graph);
	outline.border = 20;

	mxEvent.addListener(window, 'resize', function () {
		outline.update();
	});

	this.addListener('pageFormatChanged', function () {
		outline.update();
	});

	return outline;
};

// Alt+Shift+Keycode mapping to action
EditorUi.prototype.altShiftActions = {
	67: 'clearWaypoints', // Alt+Shift+C
	65: 'connectionArrows', // Alt+Shift+A
	76: 'editLink', // Alt+Shift+L
	80: 'connectionPoints', // Alt+Shift+P
	84: 'editTooltip', // Alt+Shift+T
	86: 'pasteSize', // Alt+Shift+V
	88: 'copySize' // Alt+Shift+X
};

/**
 * Creates the keyboard event handler for the current graph and history.
 */
EditorUi.prototype.createKeyHandler = function (editor) {
	var editorUi = this;
	var graph = this.editor.graph;
	var keyHandler = new mxKeyHandler(graph);

	var isEventIgnored = keyHandler.isEventIgnored;
	keyHandler.isEventIgnored = function (evt) {
		// Handles undo/redo/ctrl+./,/u via action and allows ctrl+b/i
		// only if editing value is HTML (except for FF and Safari)
		return !(mxEvent.isShiftDown(evt) && evt.keyCode == 9) &&
			((!this.isControlDown(evt) || mxEvent.isShiftDown(evt) ||
				(evt.keyCode != 90 && evt.keyCode != 89 && evt.keyCode != 188 &&
					evt.keyCode != 190 && evt.keyCode != 85)) && ((evt.keyCode != 66 && evt.keyCode != 73) ||
						!this.isControlDown(evt) || (this.graph.cellEditor.isContentEditing() &&
							!mxClient.IS_FF && !mxClient.IS_SF)) && isEventIgnored.apply(this, arguments));
	};

	// Ignores graph enabled state but not chromeless state
	keyHandler.isEnabledForEvent = function (evt) {
		return (!mxEvent.isConsumed(evt) && this.isGraphEvent(evt) && this.isEnabled() &&
			(editorUi.dialogs == null || editorUi.dialogs.length == 0));
	};

	// Routes command-key to control-key on Mac
	keyHandler.isControlDown = function (evt) {
		return mxEvent.isControlDown(evt) || (mxClient.IS_MAC && evt.metaKey);
	};

	var queue = [];
	var thread = null;

	// Helper function to move cells with the cursor keys
	function nudge(keyCode, stepSize, resize) {
		queue.push(function () {
			if (!graph.isSelectionEmpty() && graph.isEnabled()) {
				stepSize = (stepSize != null) ? stepSize : 1;

				if (resize) {
					// Resizes all selected vertices
					graph.getModel().beginUpdate();
					try {
						var cells = graph.getSelectionCells();

						for (var i = 0; i < cells.length; i++) {
							if (graph.getModel().isVertex(cells[i]) && graph.isCellResizable(cells[i])) {
								var geo = graph.getCellGeometry(cells[i]);

								if (geo != null) {
									geo = geo.clone();

									if (keyCode == 37) {
										geo.width = Math.max(0, geo.width - stepSize);
									}
									else if (keyCode == 38) {
										geo.height = Math.max(0, geo.height - stepSize);
									}
									else if (keyCode == 39) {
										geo.width += stepSize;
									}
									else if (keyCode == 40) {
										geo.height += stepSize;
									}

									graph.getModel().setGeometry(cells[i], geo);
								}
							}
						}
					}
					finally {
						graph.getModel().endUpdate();
					}
				}
				else {
					// Moves vertices up/down in a stack layout
					var cell = graph.getSelectionCell();
					var parent = graph.model.getParent(cell);
					var layout = null;

					if (graph.getSelectionCount() == 1 && graph.model.isVertex(cell) &&
						graph.layoutManager != null && !graph.isCellLocked(cell)) {
						layout = graph.layoutManager.getLayout(parent);
					}

					if (layout != null && layout.constructor == mxStackLayout) {
						var index = parent.getIndex(cell);

						if (keyCode == 37 || keyCode == 38) {
							graph.model.add(parent, cell, Math.max(0, index - 1));
						}
						else if (keyCode == 39 || keyCode == 40) {
							graph.model.add(parent, cell, Math.min(graph.model.getChildCount(parent), index + 1));
						}
					}
					else {
						var cells = graph.getMovableCells(graph.getSelectionCells());
						var realCells = [];

						for (var i = 0; i < cells.length; i++) {
							// TODO: Use getCompositeParent
							var style = graph.getCurrentCellStyle(cells[i]);

							if (mxUtils.getValue(style, 'part', '0') == '1') {
								var parent = graph.model.getParent(cells[i]);

								if (graph.model.isVertex(parent) && mxUtils.indexOf(cells, parent) < 0) {
									realCells.push(parent);
								}
							}
							else {
								realCells.push(cells[i]);
							}
						}

						if (realCells.length > 0) {
							cells = realCells;
							var dx = 0;
							var dy = 0;

							if (keyCode == 37) {
								dx = -stepSize;
							}
							else if (keyCode == 38) {
								dy = -stepSize;
							}
							else if (keyCode == 39) {
								dx = stepSize;
							}
							else if (keyCode == 40) {
								dy = stepSize;
							}

							graph.moveCells(cells, dx, dy);
						}
					}
				}
			}
		});

		if (thread != null) {
			window.clearTimeout(thread);
		}

		thread = window.setTimeout(function () {
			if (queue.length > 0) {
				graph.getModel().beginUpdate();

				try {
					for (var i = 0; i < queue.length; i++) {
						queue[i]();
					}

					queue = [];
				}
				finally {
					graph.getModel().endUpdate();
				}
			}
		}, 200);
	};

	// Overridden to handle special alt+shift+cursor keyboard shortcuts
	var directions = {
		37: mxConstants.DIRECTION_WEST, 38: mxConstants.DIRECTION_NORTH,
		39: mxConstants.DIRECTION_EAST, 40: mxConstants.DIRECTION_SOUTH
	};

	var keyHandlerGetFunction = keyHandler.getFunction;

	mxKeyHandler.prototype.getFunction = function (evt) {
		if (graph.isEnabled()) {
			// TODO: Add alt modified state in core API, here are some specific cases
			if (mxEvent.isShiftDown(evt) && mxEvent.isAltDown(evt)) {
				var action = editorUi.actions.get(editorUi.altShiftActions[evt.keyCode]);

				if (action != null) {
					return action.funct;
				}
			}

			if (evt.keyCode == 9 && mxEvent.isAltDown(evt)) {
				if (graph.cellEditor.isContentEditing()) {
					// Alt+Shift+Tab while editing
					return function () {
						document.execCommand('outdent', false, null);
					};
				}
				else if (mxEvent.isShiftDown(evt)) {
					// Alt+Shift+Tab
					return function () {
						graph.selectParentCell();
					};
				}
				else {
					// Alt+Tab
					return function () {
						graph.selectChildCell();
					};
				}
			}
			else if (directions[evt.keyCode] != null && !graph.isSelectionEmpty()) {
				// On macOS, Control+Cursor is used by Expose so allow for Alt+Control to resize
				if (!this.isControlDown(evt) && mxEvent.isShiftDown(evt) && mxEvent.isAltDown(evt)) {
					if (graph.model.isVertex(graph.getSelectionCell())) {
						return function () {
							var cells = graph.connectVertex(graph.getSelectionCell(), directions[evt.keyCode],
								graph.defaultEdgeLength, evt, true);

							if (cells != null && cells.length > 0) {
								if (cells.length == 1 && graph.model.isEdge(cells[0])) {
									graph.setSelectionCell(graph.model.getTerminal(cells[0], false));
								}
								else {
									graph.setSelectionCell(cells[cells.length - 1]);
								}

								graph.scrollCellToVisible(graph.getSelectionCell());

								if (editorUi.hoverIcons != null) {
									editorUi.hoverIcons.update(graph.view.getState(graph.getSelectionCell()));
								}
							}
						};
					}
				}
				else {
					// Avoids consuming event if no vertex is selected by returning null below
					// Cursor keys move and resize (ctrl) cells
					if (this.isControlDown(evt)) {
						return function () {
							nudge(evt.keyCode, (mxEvent.isShiftDown(evt)) ? graph.gridSize : null, true);
						};
					}
					else {
						return function () {
							nudge(evt.keyCode, (mxEvent.isShiftDown(evt)) ? graph.gridSize : null);
						};
					}
				}
			}
		}

		return keyHandlerGetFunction.apply(this, arguments);
	};

	// Binds keystrokes to actions
	keyHandler.bindAction = mxUtils.bind(this, function (code, control, key, shift) {
		var action = this.actions.get(key);

		if (action != null) {
			var f = function () {
				if (action.isEnabled()) {
					action.funct();
				}
			};

			if (control) {
				if (shift) {
					keyHandler.bindControlShiftKey(code, f);
				}
				else {
					keyHandler.bindControlKey(code, f);
				}
			}
			else {
				if (shift) {
					keyHandler.bindShiftKey(code, f);
				}
				else {
					keyHandler.bindKey(code, f);
				}
			}
		}
	});

	var ui = this;
	var keyHandlerEscape = keyHandler.escape;
	keyHandler.escape = function (evt) {
		keyHandlerEscape.apply(this, arguments);
	};

	// Ignores enter keystroke. Remove this line if you want the
	// enter keystroke to stop editing. N, W, T are reserved.
	keyHandler.enter = function () { };

	keyHandler.bindControlShiftKey(36, function () { graph.exitGroup(); }); // Ctrl+Shift+Home
	keyHandler.bindControlShiftKey(35, function () { graph.enterGroup(); }); // Ctrl+Shift+End
	keyHandler.bindKey(36, function () { graph.home(); }); // Home
	keyHandler.bindKey(35, function () { graph.refresh(); }); // End
	keyHandler.bindAction(107, true, 'zoomIn'); // Ctrl+Plus
	keyHandler.bindAction(109, true, 'zoomOut'); // Ctrl+Minus
	keyHandler.bindAction(80, true, 'print'); // Ctrl+P
	keyHandler.bindAction(79, true, 'outline', true); // Ctrl+Shift+O

	if (!this.editor.chromeless || this.editor.editable) {
		keyHandler.bindControlKey(36, function () { if (graph.isEnabled()) { graph.foldCells(true); } }); // Ctrl+Home
		keyHandler.bindControlKey(35, function () { if (graph.isEnabled()) { graph.foldCells(false); } }); // Ctrl+End
		keyHandler.bindControlKey(13, function () {
			if (graph.isEnabled()) {
				try {
					graph.setSelectionCells(graph.duplicateCells(graph.getSelectionCells(), false));
				}
				catch (e) {
					ui.handleError(e);
				}
			}
		}); // Ctrl+Enter
		keyHandler.bindAction(8, false, 'delete'); // Backspace
		keyHandler.bindAction(8, true, 'deleteAll'); // Backspace
		keyHandler.bindAction(46, false, 'delete'); // Delete
		keyHandler.bindAction(46, true, 'deleteAll'); // Ctrl+Delete
		keyHandler.bindAction(72, true, 'resetView'); // Ctrl+H
		keyHandler.bindAction(72, true, 'fitWindow', true); // Ctrl+Shift+H
		keyHandler.bindAction(74, true, 'fitPage'); // Ctrl+J
		keyHandler.bindAction(74, true, 'fitTwoPages', true); // Ctrl+Shift+J
		keyHandler.bindAction(48, true, 'customZoom'); // Ctrl+0
		keyHandler.bindAction(82, true, 'turn'); // Ctrl+R
		keyHandler.bindAction(82, true, 'clearDefaultStyle', true); // Ctrl+Shift+R

		keyHandler.bindAction(83, true, 'save'); // Ctrl+S

		keyHandler.bindAction(83, true, 'saveAs', true); // Ctrl+Shift+S
		keyHandler.bindAction(65, true, 'selectAll'); // Ctrl+A
		keyHandler.bindAction(65, true, 'selectNone', true); // Ctrl+A
		keyHandler.bindAction(73, true, 'selectVertices', true); // Ctrl+Shift+I
		keyHandler.bindAction(69, true, 'selectEdges', true); // Ctrl+Shift+E
		keyHandler.bindAction(69, true, 'editStyle'); // Ctrl+E
		keyHandler.bindAction(66, true, 'bold'); // Ctrl+B
		keyHandler.bindAction(66, true, 'toBack', true); // Ctrl+Shift+B
		keyHandler.bindAction(70, true, 'toFront', true); // Ctrl+Shift+F
		keyHandler.bindAction(68, true, 'duplicate'); // Ctrl+D
		keyHandler.bindAction(68, true, 'setAsDefaultStyle', true); // Ctrl+Shift+D
		keyHandler.bindAction(90, true, 'undo'); // Ctrl+Z
		keyHandler.bindAction(89, true, 'autosize', true); // Ctrl+Shift+Y
		keyHandler.bindAction(88, true, 'cut'); // Ctrl+X
		keyHandler.bindAction(67, true, 'copy'); // Ctrl+C
		keyHandler.bindAction(86, true, 'paste'); // Ctrl+V
		keyHandler.bindAction(71, true, 'group'); // Ctrl+G
		keyHandler.bindAction(77, true, 'editData'); // Ctrl+M
		keyHandler.bindAction(71, true, 'grid', true); // Ctrl+Shift+G
		keyHandler.bindAction(73, true, 'italic'); // Ctrl+I
		keyHandler.bindAction(76, true, 'lockUnlock'); // Ctrl+L
		keyHandler.bindAction(76, true, 'layers', true); // Ctrl+Shift+L
		keyHandler.bindAction(80, true, 'formatPanel', true); // Ctrl+Shift+P
		keyHandler.bindAction(85, true, 'underline'); // Ctrl+U
		keyHandler.bindAction(85, true, 'ungroup', true); // Ctrl+Shift+U
		keyHandler.bindAction(190, true, 'superscript'); // Ctrl+.
		keyHandler.bindAction(188, true, 'subscript'); // Ctrl+,
		keyHandler.bindAction(9, false, 'indent', true); // Shift+Tab,
		keyHandler.bindKey(13, function () { if (graph.isEnabled()) { graph.startEditingAtCell(); } }); // Enter
		keyHandler.bindKey(113, function () { if (graph.isEnabled()) { graph.startEditingAtCell(); } }); // F2
	}

	if (!mxClient.IS_WIN) {
		keyHandler.bindAction(90, true, 'redo', true); // Ctrl+Shift+Z
	}
	else {
		keyHandler.bindAction(89, true, 'redo'); // Ctrl+Y
	}

	return keyHandler;
};


/**
 * Creates the keyboard event handler for the current graph and history.
 */
EditorUi.prototype.destroy = function () {
	if (this.editor != null) {
		this.editor.destroy();
		this.editor = null;
	}

	if (this.menubar != null) {
		this.menubar.destroy();
		this.menubar = null;
	}

	if (this.toolbar != null) {
		this.toolbar.destroy();
		this.toolbar = null;
	}

	if (this.sidebar != null) {
		this.sidebar.destroy();
		this.sidebar = null;
	}

	if (this.keyHandler != null) {
		this.keyHandler.destroy();
		this.keyHandler = null;
	}

	if (this.keydownHandler != null) {
		mxEvent.removeListener(document, 'keydown', this.keydownHandler);
		this.keydownHandler = null;
	}

	if (this.keyupHandler != null) {
		mxEvent.removeListener(document, 'keyup', this.keyupHandler);
		this.keyupHandler = null;
	}

	if (this.resizeHandler != null) {
		mxEvent.removeListener(window, 'resize', this.resizeHandler);
		this.resizeHandler = null;
	}

	if (this.gestureHandler != null) {
		mxEvent.removeGestureListeners(document, this.gestureHandler);
		this.gestureHandler = null;
	}

	if (this.orientationChangeHandler != null) {
		mxEvent.removeListener(window, 'orientationchange', this.orientationChangeHandler);
		this.orientationChangeHandler = null;
	}

	if (this.scrollHandler != null) {
		mxEvent.removeListener(window, 'scroll', this.scrollHandler);
		this.scrollHandler = null;
	}

	if (this.destroyFunctions != null) {
		for (var i = 0; i < this.destroyFunctions.length; i++) {
			this.destroyFunctions[i]();
		}

		this.destroyFunctions = null;
	}

	var c = [this.menubarContainer, this.toolbarContainer, this.sidebarContainer,
	this.formatContainer, this.diagramContainer, this.footerContainer,
	this.chromelessToolbar, this.hsplit, this.sidebarFooterContainer,
	this.layersDialog];

	for (var i = 0; i < c.length; i++) {
		if (c[i] != null && c[i].parentNode != null) {
			c[i].parentNode.removeChild(c[i]);
		}
	}
};
