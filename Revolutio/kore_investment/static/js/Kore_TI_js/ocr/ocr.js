/* eslint-disable comma-dangle */
// eslint-disable-next-line no-unused-vars,no-redeclare
/* global ocrIdList,FormData,jcrop_api */
for (const i in ocrIdList) {
	let url_string = windowLocation
	let f_occ = url_string.indexOf('/', url_string.indexOf('/') + 1)
	let s_occ = url_string.indexOf('/', url_string.indexOf('/') + f_occ +1)
	let t_occ = url_string.indexOf('/', url_string.indexOf('/') + s_occ +1)
	let app_code2 = url_string.substring(f_occ+1,s_occ)
	let current_dev_mode2 = url_string.substring(s_occ+1,t_occ)
	if(current_dev_mode2 != "Build" && current_dev_mode2 != "Edit"){
		current_dev_mode2 = "User"
	}
	$(`#selectOcrOperation_${ocrIdList[i]}`).on('select2:select', function () {
		if ($(this).val() === 'uploadNewTemplate') {
			$(`#ocrOutput_${ocrIdList[i]}`).css('display', 'none');
			$(`#uploadNewTemplateCard_${ocrIdList[i]}`).css('display', 'block');
			$(`#ocrFile_${ocrIdList[i]}`).on('change', function (event) {
				const c2 = $(this).val();
				if (String(c2) !== '') {
					$(`#maindiv_${ocrIdList[i]}`).css('display', 'block');
				} else {
					$(`#maindiv_${ocrIdList[i]}`).css('display', 'none');
				}
				const image = document.getElementById(`output_${ocrIdList[i]}`);
				image.src = URL.createObjectURL(event.target.files[0]);
				const roi = {};
				const tempName = $(`#newTemplateName_${ocrIdList[i]}`).val();
				const dictinfo = {};
				dictinfo[tempName] = roi;
				if ($(image).data('Jcrop')) {
					$(image).data('Jcrop').destroy();
				}
				$(image).Jcrop(
					{
						allowSelect: true,
						allowResize: true,
						boxWidth: 1000,
						boxHeight: 1400,
						onSelect: function (c) {
							$(`#addROI_${ocrIdList[i]}`)
								.off('click')
								.on('click', function () {
									const inviRoi = $(
										`#selectRegionOfInterest_${ocrIdList[i]}`
									).val();
									const temp = [[c.x, c.y], [c.x2, c.y2], 'text', inviRoi];
									const roiDict = dictinfo[tempName];
									roiDict[inviRoi] = temp;
									dictinfo[tempName] = roiDict;
									Swal.fire({icon: 'success',text: 'Region of interest saved successfully!'});
								});
						},

						// eslint-disable-next-line
		  }, function () { jcrop_api = this })

				$(`#saveTemplate_${ocrIdList[i]}`)
					.off('click')
					.on('click', function () {
						if (Object.keys(dictinfo[tempName]).length === 0) {
							Swal.fire({icon: 'warning',text:"Please configure the region of interests." });
						} else {
							const formData = new FormData(
								$(`#formdatainput_${ocrIdList[i]}`)[0]
							);
							formData.append('roiConfig', JSON.stringify(dictinfo));
							formData.append('template_name', tempName);
							formData.append(
								'table_name',
								$(`#tableName_${ocrIdList[i]}`).text()
							);
							formData.append('operation', 'create_new_template');
							$.ajax({
								url: `/users/${app_code2}/${current_dev_mode2}/ocr/`,
								data: formData,
								type: 'POST',
								cache: false,
								contentType: false,
								processData: false,
								// eslint-disable-next-line no-unused-vars
								success: function (data) {
									Swal.fire({icon: 'success',text: 'Template saved successfully!'});
									windowLocationAttr.reload();
								},
								error: () => {
									Swal.fire({icon: 'error',text: 'Error! Failure in saving the template. Please try again.'});
								},
							});
						}
					});
			});
		} else {
			$(`#ocrOutput_${ocrIdList[i]}`).css('display', 'none');
			$(`#uploadNewTemplateCard_${ocrIdList[i]}`).css('display', 'none');
			$(`#compareWithExisting_${ocrIdList[i]}`).modal({
				backdrop: 'static',
				keyboard: false,
			});
			$(`#compareWithExisting_${ocrIdList[i]}`).modal('show');
			$(`#selectTemplate_${ocrIdList[i]}`).val('').trigger('change');
			$(`#compareWithEContainer_${ocrIdList[i]}`).css('display', 'none');
			$(`#templateImage_${ocrIdList[i]}`).removeAttr('src');
			$.ajax({
				url: `/users/${app_code2}/${current_dev_mode2}/ocr/`,
				data: {
					operation: 'fetch_template_name',
					template_name: $(`#selectTemplate_${ocrIdList[i]}`).val(),
				},
				type: 'POST',
				dataType: 'json',
				success: function (data) {
					$(`#selectTemplate_${ocrIdList[i]}`).empty();
					$(`#selectTemplate_${ocrIdList[i]}`).append(
						'<option value="">Select template</option>'
					);
					for (let i = 0; i < data.template.length; i++) {
						$(`#selectTemplate_${ocrIdList[i]}`).append(
							`<option value="${data.template[i]}">${data.template[i]}</option>`
						);
					}
				},
				error: function () {
					Swal.fire({icon: 'error',text: 'Error! Please try again.'});
				},
			});
			$(`#selectTemplate_${ocrIdList[i]}`).on('select2:select', function () {
				$.ajax({
					url: `/users/${app_code2}/${current_dev_mode2}/ocr/`,
					data: {
						operation: 'fetch_template_image',
						template_name: $(`#selectTemplate_${ocrIdList[i]}`).val(),
					},
					type: 'POST',
					dataType: 'json',
					success: function (data) {
						$(`#templateImage_${ocrIdList[i]}`).attr(
							'src',
							`data:image/png;base64,${data.temp_image}`
						);
						$(`#compareWithEContainer_${ocrIdList[i]}`).css('display', 'block');
					},
					error: function () {
						Swal.fire({icon: 'error',text: 'Error! Please try again.'});
					},
				});

				$(`#compareOCRButton_${ocrIdList[i]}`)
					.off('click')
					.on('click', function () {
						const formData = new FormData(
							$(`#compareOCRForm_${ocrIdList[i]}`)[0]
						);
						formData.append(
							'template_name',
							$(`#selectTemplate_${ocrIdList[i]}`).val()
						);
						formData.append('operation', 'compare_with_existing');
						$.ajax({
							url: `/users/${app_code2}/${current_dev_mode2}/ocr/`,
							data: formData,
							type: 'POST',
							cache: false,
							contentType: false,
							processData: false,
							success: function (data) {
								$(`#ocrOutputContainer_${ocrIdList[i]}`).empty();
								const emptyResponse = [];
								$(`#ocrOutputContainer_${ocrIdList[i]}`).append(
									`<div class='row' id='outputContainer_${ocrIdList[i]}'></div>`
								);
								for (const [key, value] of Object.entries(data.output)) {
									$(`#outputContainer_${ocrIdList[i]}`).append(`
										<div class="form-group col-md-3">
											<label for="" class="">${key}<span class="asteriskField">*</span></label>
											<div>
												<input type="text" name="" value="${value}" class="textinput textInput form-control" required="">
											</div>
										</div>
									`);
									if (value === '' || value === null) {
										emptyResponse.push(key);
									}
								}
								$(`#compareWithExisting_${ocrIdList[i]}`).modal('hide');
								$(`#ocrOutput_${ocrIdList[i]}`).css('display', 'block');
								if (emptyResponse.length > 0) {
									let emptyText = JSON.stringify(emptyResponse);
									emptyText = emptyText.replace('[', '');
									emptyText = emptyText.replace(']', '');
									Swal.fire({icon: 'warning',text:`The image uploaded is of lower resolution. Values for ${emptyText} could not be extracted. Please upload the image with higher resolution.` });
								}
							},
							error: () => {
								Swal.fire({icon: 'error',text: 'Error! Please try again.'});
							},
						});
					});
			});
			$(`#saveUploadedData_${ocrIdList[i]}`)
				.off('click')
				.on('click', function () {
					const outputDict = {};
					$(`#outputContainer_${ocrIdList[i]}`)
						.find('div.form-group')
						.each(function () {
							const key = $(this).find('label').text().replace('*', '');
							const value = $(this).find('input').val();
							outputDict[key] = value;
						});
					$.ajax({
						url: `/users/${app_code2}/${current_dev_mode2}/ocr/`,
						data: {
							operation: 'save_uploaded_temp_data',
							table_name: $(`#tableName_${ocrIdList[i]}`).text(),
							output_dict: JSON.stringify(outputDict),
						},
						type: 'POST',
						dataType: 'json',
						// eslint-disable-next-line no-unused-vars
						success: function (data) {
							Swal.fire({icon: 'success',text: 'Data uploaded successfully!'});
							windowLocationAttr.reload();
						},
						error: function () {
							Swal.fire({icon: 'error',text: 'Error! Failure in uploading the data. Please try again.'});
						},
					});
				});
		}
	});
}
