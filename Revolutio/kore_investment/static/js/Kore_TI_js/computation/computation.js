function masterComputeExecutionHandler(computeElementIdArray) {
  for (const elementId of computeElementIdArray) {
    computationRunModelHandler(elementId);
  }
}

function populateCascades(varName="",columnName=""){ 
  let gdependent_columns_dict = JSON.parse($(this).parent().parent().attr('gdependent_columns_dict'))
  let tab_element_id = $('.gVarDropDown:first').parent().parent().parent().attr('id').slice(16)

  if(gdependent_columns_dict){
    if(gdependent_columns_dict.hasOwnProperty(varName) && gdependent_columns_dict[varName].length>0){
        gdependent_columns_dict[varName].forEach((d_var,i) => {
          let globalVariableID = $(this).closest('.form-row').attr('data-parent_element_id');
          let target = ".gVarDropDown[name="+"gVar_"+d_var+"_"+globalVariableID+"]"
          let dependencies = JSON.parse($(target).attr('dependencies'))
          let multi_dependencies = JSON.parse($(target).attr('multi_dependencies'))
          if(multi_dependencies.includes(varName)){
            let cascade_options = {}
            if(dependencies){
              dependencies.forEach(item =>{
                let temp = ".gVarDropDown[name="+"gVar_"+item+"_"+globalVariableID+"] select"
                let value = $(temp).val()
                let column = $(temp).parent().parent().attr('column')
                if(value.length>0){
                  cascade_options[item]= [value,column]
                  }
              })
            }
            if(!cascade_options.hasOwnProperty(varName) && multi_dependencies.length<=1){
              $(target).find('select').empty();
              $(target).find('select').append('<option value="">---------</option>');
              return
            }
            if(Object.keys(multi_dependencies).length>1 && Object.keys(cascade_options).length==0){
              $(target).find('select').empty();
              $(target).find('select').append('<option value="">---------</option>');
              return
            }
            
            $.ajax({
              url:`/users/${urlPath}/dynamicVal/`,
              data: {
                'operation':'GetCascadeOptions',
                'element_id_list': globalVariableID,
                'has_process_level_filters': $(target).attr('has_process_level_filters'),
                'tab_element_id': tab_element_id,
                'cascade_options': JSON.stringify(cascade_options),
                'cascade_dropdown_name': d_var
              },
              type: 'POST',
              dataType: "json",
              success: function (data) {
                let idGV = d_var + "_" +globalVariableID
                let listGV = data[idGV]
                
                $(target).find('select').empty();
                $(target).find('select').append('<option value="">---------</option>');
                for(let i = 0; i < listGV.length; i++) {
                  $(target).find('select').append(`<option value="${listGV[i]}">${listGV[i]}</option>`);
                }
              },
              error: ()=>{
                Swal.fire({icon: 'error',text: 'Error! Please try again.'});
              }
            });
          }else{
            $(target).find('select').empty();
            $(target).find('select').append('<option value="">---------</option>');
          }
        });
    }else{
      return
    }
  }
}

function masterComputePreviousRunDisplayHandler(
  previousRunComputeElementIdArray
) {
  for (const elementId of previousRunComputeElementIdArray) {
    previousRunOutputHandler(elementId);
  }
}

function computationRunModelHandler(computationElementId) {
  $(`#runModel_${computationElementId}`).on("click", function (event) {
    var sub_process_name = $(this).attr("data-subprocess_name");
    var computationElementId = $(this).attr("id").replace("runModel_", "");
    $(`#run_model_in_progress_${computationElementId}`).modal("show");
    setTimeout(function() {
      $(`#run_model_in_progress_${computationElementId}`).modal('hide');
    }, 5000);
    var computationRunModelButtonText = $(this).html();
    event.preventDefault();
    // Extract input variables
    var variableList = [];
    $(`#runModelCard_${computationElementId}`)
      .find(".no_run_message")
      .css("display", "none");
    var elementIDGVar;
    $(`#computationForm_${computationElementId}`)
      .find("div.form-row")
      .each(function () {
        elementIDGVar = $(this).attr("data-parent_element_id");
        $(this)
          .find("div.form-group")
          .each(function () {
            if ($(this).find("select").length === 0) {
              if ($(this).find('input[type="file"]').length != 0) {
                var varDict = {
                  varName: $(this).find("input").attr("data-var_name"),
                  inputValue: $(this).find(`input`).val(),
                };
              } else {
                var varDict = {
                  varName: $(this)
                    .find("label")
                    .text()
                    .replaceAll(" *", "")
                    .trim(),
                  inputValue: $(this).find(`input`).val(),
                };
              }
            } else {
              var varDict = {
                varName: $(this)
                  .find("label")
                  .text()
                  .replaceAll(" *", "")
                  .trim(),
                inputValue: $(this).find(`select`).val(),
              };
            }
            variableList.push(varDict);
          });
      });
    variableList_scenario = variableList;
    $(`#computationForm_${computationElementId}`)
      .find("div.form-row")
      .each(function () {
        elementIDGVar = $(this).attr("data-parent_element_id");
        $(this)
          .find("div.form-group")
          .each(function () {
            if (
              $(this).find(`input[name=gVarFileRM]`).attr("type") === "file"
            ) {
              let formData = new FormData(
                $(this).find(`form.gVarFileInput`)[0]
              );
              formData.append("operation", "gVarFileRunModel");
              formData.append(
                "gVarName",
                $(this)
                  .find("label.gVarNameLabel")
                  .text()
                  .replaceAll(" *", "")
                  .trim()
              );
              formData.append("elementID", elementIDGVar);

              $.ajax({
                url: `/users/${urlPath}/computationModule/upload-handler/`,
                data: formData,
                type: "POST",
                cache: false,
                contentType: false,
                processData: false,
                success: function (data) {},
                error: () => {
                  Swal.fire({
                    icon: "error",
                    text: "Error! Please try again.",
                  });
                },
              });
            }
          });
      });
    var globalFuncList = [];
    $(`#computationForm_${computationElementId}`)
      .find("section.globalFunction")
      .each(function () {
        elementName = $(this).attr("data-element_name");
        elementID = $(this).attr("data-computeElementId");
        if (elementName === "Interest Rate Products") {
          var config_dict = {};
          var sub_op = $(
            `#select_intRatesCF_val_${computationElementId}`
          ).val();
          var model_code = $(
            `#select_intRatesCF_val_${computationElementId} option:selected`
          ).attr("data-model_code");
          var valuation_method = $(
            `.finInstrumentsCF_valuation_method_button_${computationElementId}:checked`
          ).val();
          var outputdict = {
            Cashflows: "No",
            Valuation: "No",
            Sensitivity_Analysis: "No",
          };

          if ($(`#cftable1_${computationElementId}`)[0].checked) {
            outputdict["Cashflows"] = "Yes";
          }
          if ($(`#cftable2_${computationElementId}`)[0].checked) {
            outputdict["Valuation"] = "Yes";
          }
          if ($(`#cftable3_${computationElementId}`)[0].checked) {
            outputdict["Sensitivity_Analysis"] = "Yes";
          }
          if (model_code === "M003") {
            var uniqRefId = $(
              `#select_unique_reference_id_cf_${computationElementId}`
            ).val();
            var positionId = $(
              `#select_position_id_cf_${computationElementId}`
            ).val();
            var productVariant = $(
              `#select_product_variant_cf_${computationElementId}`
            ).val();
            var productVariantName = $(
              `#select_product_variant_name_cf_${computationElementId}`
            ).val();
            var counterparty = $(
              `#select_counterparty_cf_${computationElementId}`
            ).val();
            var positionDirection = $(
              `#select_position_direction_cf_${computationElementId}`
            ).val();
            var pp = $(
              `#select_purchase_price_cf_${computationElementId}`
            ).val();
            var cp = $(`#select_spot_price_cf_${computationElementId}`).val();
            var red = $(
              `#select_redemption_amount_cf_${computationElementId}`
            ).val();
            var nv = $(
              `#select_nominal_value_cf_${computationElementId}`
            ).val();
            var primary_currency = $(
              `#select_primary_currency_cf_${computationElementId}`
            ).val();
            var val_date = $(
              `#select_reporting_date_cf_${computationElementId}`
            ).val();
            var issue_date = $(
              `#select_issue_date_cf_${computationElementId}`
            ).val();
            var mat_date = $(
              `#select_maturity_date_cf_${computationElementId}`
            ).val();
            var sett_date = $(
              `#select_settlement_date_cf_${computationElementId}`
            ).val();
            var last_coupdate = $(
              `#select_last_payment_date_cf_${computationElementId}`
            ).val();
            var frequency = $(
              `#select_payment_frequency_cf_${computationElementId}`
            ).val();
            var coupon_frequency_unit = $(
              `#select_payment_frequency_units_cf_${computationElementId}`
            ).val();
            var issuer = $(`#select_issuer_cf_${computationElementId}`).val();
            var a_basis = $(
              `#select_accrual_daycount_convention_cf_${computationElementId}`
            ).val();
            var d_basis = $(
              `#select_discount_daycount_convention_cf_${computationElementId}`
            ).val();
            var principal_frequency = $(
              `#select_principal_payment_frequency_cf_${computationElementId}`
            ).val();
            var principal_frequency_unit = $(
              `#select_principal_payment_frequency_units_cf_${computationElementId}`
            ).val();
            var discount_curve = $(
              `#select_discounting_curve_cf_${computationElementId}`
            ).val();
            var bus_day_basis = $(
              `#select_business_convention_cf_${computationElementId}`
            ).val();
            var benchmark_curve = $(
              `#select_forward_benchmark_curve_cf_${computationElementId}`
            ).val();
            var spread_over_benchmark = $(
              `#select_spread_over_benchmark_cf_${computationElementId}`
            ).val();
            var next_repricing_date = $(
              `#select_next_reset_date_cf_${computationElementId}`
            ).val();
            var last_repricing_date = $(
              `#select_last_reset_date_cf_${computationElementId}`
            ).val();
            var repricing_frequency = $(
              `#select_reset_frequency_cf_${computationElementId}`
            ).val();
            var repricing_frequency_unit = $(
              `#select_reset_frequency_unit_cf_${computationElementId}`
            ).val();
            var fixed_floatFlag = $(
              `#select_fixed_or_float_flag_cf_${computationElementId}`
            ).val();
            var internalRating = $(
              `#select_internal_rating_cf_${computationElementId}`
            ).val();
            var externalRating = $(
              `#select_external_rating_cf_${computationElementId}`
            ).val();
            var quantity = $(
              `#select_quantity_cf_${computationElementId}`
            ).val();
            var holiday_cal = $(
              `#select_holiday_calendar_cf_${computationElementId}`
            ).val();
            var margin = $(`#select_margin_cf_${computationElementId}`).val();
            var base_rate = $(
              `#select_base_rate_cf_${computationElementId}`
            ).val();

            var configDict = {
              function: "Interest Rate Products",
              outputs: outputdict,
              inputs: {
                Data_Choice: "Custom_input",
                Operation: "Interest Rates",
                parent_element_id: "#",
                data: {},
                Sub_Op: sub_op,
                model_code: model_code,
                Valuation_Method: valuation_method,
                Unique_Reference_Id: uniqRefId,
                Position_Id: positionId,
                Product_Variant: productVariant,
                Product_Variant_Name: productVariantName,
                Issuer: issuer,
                Counterparty: counterparty,
                Position_Direction: positionDirection,
                Face_Value: nv,
                Purchase_Price: pp,
                Redemption_Amount: red,
                Spot_Price: cp,
                Valuation_date: val_date,
                Issue_Date: issue_date,
                Maturity_Date: mat_date,
                Settlement_Date: sett_date,
                Last_coupon_date: last_coupdate,
                Coupon_frequency: frequency,
                Coupon_frequency_unit: coupon_frequency_unit,
                internal_rating: internalRating,
                Accrual_daycount_convention: a_basis,
                Discount_daycount_convention: d_basis,
                Discount_Curve: discount_curve,
                Business_day_convention: bus_day_basis,
                Benchmark_Curve: benchmark_curve,
                Spread_Over_Benchmark: spread_over_benchmark,
                Principal_frequency: principal_frequency,
                Principal_frequency_unit: principal_frequency_unit,
                Next_Repricing_Date: next_repricing_date,
                Last_Repricing_Date: last_repricing_date,
                Holiday_Calendar: holiday_cal,
                Repricing_Frequency: repricing_frequency,
                Repricing_Frequency_unit: repricing_frequency_unit,
                fixed_or_float_flag: fixed_floatFlag,
                Quantity: quantity,
                External_Rating: externalRating,
                Primary_Currency: primary_currency,
                Margin: margin,
                Base_Rate: base_rate,
              },
            };
          } else if (model_code === "M007") {
            var uniqRefId = $(
              `#select_unique_reference_id_cf_${computationElementId}`
            ).val();
            var positionId = $(
              `#select_position_id_cf_${computationElementId}`
            ).val();
            var productVariant = $(
              `#select_product_variant_cf_${computationElementId}`
            ).val();
            var productVariantName = $(
              `#select_product_variant_name_cf_${computationElementId}`
            ).val();
            var counterparty = $(
              `#select_counterparty_cf_${computationElementId}`
            ).val();
            var positionDirection = $(
              `#select_position_direction_cf_${computationElementId}`
            ).val();
            var pp = $(
              `#select_purchase_price_cf_${computationElementId}`
            ).val();
            var cp = $(`#select_spot_price_cf_${computationElementId}`).val();
            var red = $(
              `#select_redemption_amount_cf_${computationElementId}`
            ).val();
            var nv = $(
              `#select_nominal_value_cf_${computationElementId}`
            ).val();
            var primary_currency = $(
              `#select_primary_currency_cf_${computationElementId}`
            ).val();
            var val_date = $(
              `#select_reporting_date_cf_${computationElementId}`
            ).val();
            var issue_date = $(
              `#select_issue_date_cf_${computationElementId}`
            ).val();
            var mat_date = $(
              `#select_maturity_date_cf_${computationElementId}`
            ).val();
            var sett_date = $(
              `#select_settlement_date_cf_${computationElementId}`
            ).val();
            var last_coupdate = $(
              `#select_last_payment_date_cf_${computationElementId}`
            ).val();
            var frequency = $(
              `#select_payment_frequency_cf_${computationElementId}`
            ).val();
            var coupon_frequency_unit = $(
              `#select_payment_frequency_units_cf_${computationElementId}`
            ).val();
            var issuer = $(`#select_issuer_cf_${computationElementId}`).val();
            var a_basis = $(
              `#select_accrual_daycount_convention_cf_${computationElementId}`
            ).val();
            var d_basis = $(
              `#select_discount_daycount_convention_cf_${computationElementId}`
            ).val();
            var principal_frequency = $(
              `#select_principal_payment_frequency_cf_${computationElementId}`
            ).val();
            var principal_frequency_unit = $(
              `#select_principal_payment_frequency_units_cf_${computationElementId}`
            ).val();
            var discount_curve = $(
              `#select_discounting_curve_cf_${computationElementId}`
            ).val();
            var bus_day_basis = $(
              `#select_business_convention_cf_${computationElementId}`
            ).val();
            var benchmark_curve = $(
              `#select_forward_benchmark_curve_cf_${computationElementId}`
            ).val();
            var spread_over_benchmark = $(
              `#select_spread_over_benchmark_cf_${computationElementId}`
            ).val();
            var next_repricing_date = $(
              `#select_next_reset_date_cf_${computationElementId}`
            ).val();
            var last_repricing_date = $(
              `#select_last_reset_date_cf_${computationElementId}`
            ).val();
            var repricing_frequency = $(
              `#select_reset_frequency_cf_${computationElementId}`
            ).val();
            var repricing_frequency_unit = $(
              `#select_reset_frequency_unit_cf_${computationElementId}`
            ).val();
            var fixed_floatFlag = $(
              `#select_fixed_or_float_flag_cf_${computationElementId}`
            ).val();
            var internalRating = $(
              `#select_internal_rating_cf_${computationElementId}`
            ).val();
            var externalRating = $(
              `#select_external_rating_cf_${computationElementId}`
            ).val();
            var quantity = $(
              `#select_quantity_cf_${computationElementId}`
            ).val();
            var holiday_cal = $(
              `#select_holiday_calendar_cf_${computationElementId}`
            ).val();
            var margin = $(`#select_margin_cf_${computationElementId}`).val();
            var base_rate = $(
              `#select_base_rate_cf_${computationElementId}`
            ).val();
            var credit_spread_curve = $(
              `#select_credit_spread_curve_cf_${computationElementId}`
            ).val();
            var credit_spread_rate = $(
              `#select_credit_spread_rate_cf_${computationElementId}`
            ).val();

            var configDict = {
              function: "Interest Rate Products",
              outputs: outputdict,
              inputs: {
                Data_Choice: "Custom_input",
                Operation: "Interest Rates",
                parent_element_id: "#",
                data: {},
                Sub_Op: sub_op,
                model_code: model_code,
                Valuation_Method: valuation_method,
                Unique_Reference_Id: uniqRefId,
                Position_Id: positionId,
                Product_Variant: productVariant,
                Product_Variant_Name: productVariantName,
                Issuer: issuer,
                Counterparty: counterparty,
                Position_Direction: positionDirection,
                Face_Value: nv,
                Purchase_Price: pp,
                Redemption_Amount: red,
                Spot_Price: cp,
                Valuation_date: val_date,
                Issue_Date: issue_date,
                Maturity_Date: mat_date,
                Settlement_Date: sett_date,
                Last_coupon_date: last_coupdate,
                Coupon_frequency: frequency,
                Coupon_frequency_unit: coupon_frequency_unit,
                internal_rating: internalRating,
                Accrual_daycount_convention: a_basis,
                Discount_daycount_convention: d_basis,
                Discount_Curve: discount_curve,
                Business_day_convention: bus_day_basis,
                Benchmark_Curve: benchmark_curve,
                Spread_Over_Benchmark: spread_over_benchmark,
                Principal_frequency: principal_frequency,
                Principal_frequency_unit: principal_frequency_unit,
                Next_Repricing_Date: next_repricing_date,
                Last_Repricing_Date: last_repricing_date,
                Holiday_Calendar: holiday_cal,
                Repricing_Frequency: repricing_frequency,
                Repricing_Frequency_unit: repricing_frequency_unit,
                fixed_or_float_flag: fixed_floatFlag,
                Quantity: quantity,
                External_Rating: externalRating,
                Primary_Currency: primary_currency,
                Margin: margin,
                Base_Rate: base_rate,
                Credit_Spread_Rate: credit_spread_rate,
                Credit_Spread_Curve: credit_spread_curve,
              },
            };
          } else if (model_code === "M005") {
            var uniqRefId = $(
              `#select_unique_reference_id_cf_${computationElementId}`
            ).val();
            var positionId = $(
              `#select_position_id_cf_${computationElementId}`
            ).val();
            var productVariant = $(
              `#select_product_variant_cf_${computationElementId}`
            ).val();
            var productVariantName = $(
              `#select_product_variant_name_cf_${computationElementId}`
            ).val();
            var counterparty = $(
              `#select_counterparty_cf_${computationElementId}`
            ).val();
            var positionDirection = $(
              `#select_position_direction_cf_${computationElementId}`
            ).val();
            var val_date = $(
              `#select_reporting_date_cf_${computationElementId}`
            ).val();
            var issue_date = $(
              `#select_issue_date_cf_${computationElementId}`
            ).val();
            var mat_date = $(
              `#select_maturity_date_cf_${computationElementId}`
            ).val();
            var sett_date = $(
              `#select_settlement_date_cf_${computationElementId}`
            ).val();
            var pp = $(
              `#select_purchase_price_cf_${computationElementId}`
            ).val();
            var cp = $(`#select_spot_price_cf_${computationElementId}`).val();
            var red = $(
              `#select_redemption_amount_cf_${computationElementId}`
            ).val();
            var nv = $(
              `#select_nominal_value_cf_${computationElementId}`
            ).val();
            var primary_currency = $(
              `#select_primary_currency_cf_${computationElementId}`
            ).val();
            var issuer = $(`#select_issuer_cf_${computationElementId}`).val();
            var a_basis = $(
              `#select_accrual_daycount_convention_cf_${computationElementId}`
            ).val();
            var d_basis = $(
              `#select_discount_daycount_convention_cf_${computationElementId}`
            ).val();
            var principal_frequency = $(
              `#select_principal_payment_frequency_cf_${computationElementId}`
            ).val();
            var principal_frequency_unit = $(
              `#select_principal_payment_frequency_units_cf_${computationElementId}`
            ).val();
            var last_princ_date = $(
              `#select_last_principal_payment_date_cf_${computationElementId}`
            ).val();
            var discount_curve = $(
              `#select_discounting_curve_cf_${computationElementId}`
            ).val();
            var bus_day_basis = $(
              `#select_business_convention_cf_${computationElementId}`
            ).val();
            var benchmark_curve = $(
              `#select_forward_benchmark_curve_cf_${computationElementId}`
            ).val();
            var internalRating = $(
              `#select_internal_rating_cf_${computationElementId}`
            ).val();
            var externalRating = $(
              `#select_external_rating_cf_${computationElementId}`
            ).val();
            var quantity = $(
              `#select_quantity_cf_${computationElementId}`
            ).val();
            var holiday_cal = $(
              `#select_holiday_calendar_cf_${computationElementId}`
            ).val();
            var credit_spread_curve = $(
              `#select_credit_spread_curve_cf_${computationElementId}`
            ).val();
            var credit_spread_rate = $(
              `#select_credit_spread_rate_cf_${computationElementId}`
            ).val();

            var configDict = {
              function: "Interest Rate Products",
              outputs: outputdict,
              inputs: {
                Data_Choice: "Custom_input",
                Operation: "Interest Rates",
                parent_element_id: "#",
                data: {},
                Sub_Op: sub_op,
                model_code: model_code,
                Valuation_Method: valuation_method,
                Unique_Reference_Id: uniqRefId,
                Position_Id: positionId,
                Product_Variant: productVariant,
                Product_Variant_Name: productVariantName,
                Issuer: issuer,
                Counterparty: counterparty,
                Position_Direction: positionDirection,
                Face_Value: nv,
                Purchase_Price: pp,
                Redemption_Amount: red,
                Spot_Price: cp,
                Valuation_date: val_date,
                Issue_Date: issue_date,
                Maturity_Date: mat_date,
                Settlement_Date: sett_date,
                internal_rating: internalRating,
                Accrual_daycount_convention: a_basis,
                Discount_daycount_convention: d_basis,
                Discount_Curve: discount_curve,
                Business_day_convention: bus_day_basis,
                Benchmark_Curve: benchmark_curve,
                Principal_frequency: principal_frequency,
                Principal_frequency_unit: principal_frequency_unit,
                Last_Principal_Payment_Date: last_princ_date,
                Holiday_Calendar: holiday_cal,
                Quantity: quantity,
                External_Rating: externalRating,
                Primary_Currency: primary_currency,
                Credit_Spread_Rate: credit_spread_rate,
                Credit_Spread_Curve: credit_spread_curve,
              },
            };
          } else if (model_code === "M008") {
            var uniqRefId = $(
              `#select_unique_reference_id_cf_${computationElementId}`
            ).val();
            var positionId = $(
              `#select_position_id_cf_${computationElementId}`
            ).val();
            var productVariant = $(
              `#select_product_variant_cf_${computationElementId}`
            ).val();
            var productVariantName = $(
              `#select_product_variant_name_cf_${computationElementId}`
            ).val();
            var counterparty = $(
              `#select_counterparty_cf_${computationElementId}`
            ).val();
            var positionDirection = $(
              `#select_position_direction_cf_${computationElementId}`
            ).val();
            var val_date = $(
              `#select_reporting_date_cf_${computationElementId}`
            ).val();
            var issue_date = $(
              `#select_issue_date_cf_${computationElementId}`
            ).val();
            var mat_date = $(
              `#select_maturity_date_cf_${computationElementId}`
            ).val();
            var sett_date = $(
              `#select_settlement_date_cf_${computationElementId}`
            ).val();
            var start_date = $(
              `#select_start_date_cf_${computationElementId}`
            ).val();
            var pp = $(
              `#select_purchase_price_cf_${computationElementId}`
            ).val();
            var cp = $(`#select_spot_price_cf_${computationElementId}`).val();
            var red = $(
              `#select_redemption_amount_cf_${computationElementId}`
            ).val();
            var nv = $(
              `#select_nominal_value_cf_${computationElementId}`
            ).val();
            var primary_currency = $(
              `#select_primary_currency_cf_${computationElementId}`
            ).val();
            var issuer = $(`#select_issuer_cf_${computationElementId}`).val();
            var a_basis = $(
              `#select_accrual_daycount_convention_cf_${computationElementId}`
            ).val();
            var d_basis = $(
              `#select_discount_daycount_convention_cf_${computationElementId}`
            ).val();
            var principal_frequency = $(
              `#select_principal_payment_frequency_cf_${computationElementId}`
            ).val();
            var principal_frequency_unit = $(
              `#select_principal_payment_frequency_units_cf_${computationElementId}`
            ).val();
            var last_princ_date = $(
              `#select_last_principal_payment_date_cf_${computationElementId}`
            ).val();
            var discount_curve = $(
              `#select_discounting_curve_cf_${computationElementId}`
            ).val();
            var bus_day_basis = $(
              `#select_business_convention_cf_${computationElementId}`
            ).val();
            var benchmark_curve = $(
              `#select_forward_benchmark_curve_cf_${computationElementId}`
            ).val();
            var quantity = $(
              `#select_quantity_cf_${computationElementId}`
            ).val();
            var holiday_cal = $(
              `#select_holiday_calendar_cf_${computationElementId}`
            ).val();
            var credit_spread_curve = $(
              `#select_credit_spread_curve_cf_${computationElementId}`
            ).val();
            var credit_spread_rate = $(
              `#select_credit_spread_rate_cf_${computationElementId}`
            ).val();
            var base_rate = $(
              `#select_base_rate_cf_${computationElementId}`
            ).val();
            var underlyingMaturityDate = $(
              `#select_underlying_maturity_date_cf_${computationElementId}`
            ).val();
            var underlyingPaymentFrequency = $(
              `#select_underlying_payment_frequency_cf_${computationElementId}`
            ).val();
            var underlyingFV = $(
              `#select_face_value_underlying_cf_${computationElementId}`
            ).val();
            var initial_amount = $(
              `#select_initial_amount_cf_${computationElementId}`
            ).val();
            var salePrice = $(
              `#select_sale_price_cf_${computationElementId}`
            ).val();
            var underlying_rate = $(
              `#select_rate_underlying_cf_${computationElementId}`
            ).val();

            var configDict = {
              function: "Interest Rate Products",
              outputs: outputdict,
              inputs: {
                Data_Choice: "Custom_input",
                Operation: "Interest Rates",
                parent_element_id: "#",
                data: {},
                Sub_Op: sub_op,
                model_code: model_code,
                Valuation_Method: valuation_method,
                Unique_Reference_Id: uniqRefId,
                Position_Id: positionId,
                Product_Variant: productVariant,
                Product_Variant_Name: productVariantName,
                Issuer: issuer,
                Counterparty: counterparty,
                Position_Direction: positionDirection,
                Face_Value: nv,
                Purchase_Price: pp,
                Spot_Price: cp,
                Valuation_date: val_date,
                Issue_Date: issue_date,
                Maturity_Date: mat_date,
                Settlement_Date: sett_date,
                Start_Date: start_date,
                Accrual_daycount_convention: a_basis,
                Discount_daycount_convention: d_basis,
                Discount_Curve: discount_curve,
                Business_day_convention: bus_day_basis,
                Benchmark_Curve: benchmark_curve,
                Principal_frequency: principal_frequency,
                Principal_frequency_unit: principal_frequency_unit,
                Last_Principal_Payment_Date: last_princ_date,
                Holiday_Calendar: holiday_cal,
                Quantity: quantity,
                Base_Rate: base_rate,
                Primary_Currency: primary_currency,
                Credit_Spread_Rate: credit_spread_rate,
                Credit_Spread_Curve: credit_spread_curve,
                Sale_Price: salePrice,
                Initial_Amount: initial_amount,
                Underlying_Maturity_Date: underlyingMaturityDate,
                Underlying_Rate: underlying_rate,
                Underlying_Face_Value: underlyingFV,
              },
            };
          } else if (model_code === "M006") {
            var uniqRefId = $(
              `#select_unique_reference_id_cf_${computationElementId}`
            ).val();
            var positionId = $(
              `#select_position_id_cf_${computationElementId}`
            ).val();
            var productVariant = $(
              `#select_product_variant_cf_${computationElementId}`
            ).val();
            var productVariantName = $(
              `#select_product_variant_name_cf_${computationElementId}`
            ).val();
            var counterparty = $(
              `#select_counterparty_cf_${computationElementId}`
            ).val();
            var positionDirection = $(
              `#select_position_direction_cf_${computationElementId}`
            ).val();
            var pp = $(
              `#select_purchase_price_cf_${computationElementId}`
            ).val();
            var cp = $(`#select_spot_price_cf_${computationElementId}`).val();
            var red = $(
              `#select_redemption_amount_cf_${computationElementId}`
            ).val();
            var nv = $(
              `#select_nominal_value_cf_${computationElementId}`
            ).val();
            var primary_currency = $(
              `#select_primary_currency_cf_${computationElementId}`
            ).val();
            var val_date = $(
              `#select_reporting_date_cf_${computationElementId}`
            ).val();
            var issue_date = $(
              `#select_issue_date_cf_${computationElementId}`
            ).val();
            var mat_date = $(
              `#select_maturity_date_cf_${computationElementId}`
            ).val();
            var sett_date = $(
              `#select_settlement_date_cf_${computationElementId}`
            ).val();
            var last_coupdate = $(
              `#select_last_payment_date_cf_${computationElementId}`
            ).val();
            var frequency = $(
              `#select_payment_frequency_cf_${computationElementId}`
            ).val();
            var coupon_frequency_unit = $(
              `#select_payment_frequency_units_cf_${computationElementId}`
            ).val();
            var issuer = $(`#select_issuer_cf_${computationElementId}`).val();
            var a_basis = $(
              `#select_accrual_daycount_convention_cf_${computationElementId}`
            ).val();
            var d_basis = $(
              `#select_discount_daycount_convention_cf_${computationElementId}`
            ).val();
            var principal_frequency = $(
              `#select_principal_payment_frequency_cf_${computationElementId}`
            ).val();
            var principal_frequency_unit = $(
              `#select_principal_payment_frequency_units_cf_${computationElementId}`
            ).val();
            var discount_curve = $(
              `#select_discounting_curve_cf_${computationElementId}`
            ).val();
            var bus_day_basis = $(
              `#select_business_convention_cf_${computationElementId}`
            ).val();
            var fixed_floatFlag = $(
              `#select_fixed_or_float_flag_cf_${computationElementId}`
            ).val();
            var internalRating = $(
              `#select_internal_rating_cf_${computationElementId}`
            ).val();
            var externalRating = $(
              `#select_external_rating_cf_${computationElementId}`
            ).val();
            var quantity = $(
              `#select_quantity_cf_${computationElementId}`
            ).val();
            var holiday_cal = $(
              `#select_holiday_calendar_cf_${computationElementId}`
            ).val();
            var margin = $(`#select_margin_cf_${computationElementId}`).val();
            var base_rate = $(
              `#select_base_rate_cf_${computationElementId}`
            ).val();
            var credit_spread_curve = $(
              `#select_credit_spread_curve_cf_${computationElementId}`
            ).val();
            var credit_spread_rate = $(
              `#select_credit_spread_rate_cf_${computationElementId}`
            ).val();

            var configDict = {
              function: "Interest Rate Products",
              outputs: outputdict,
              inputs: {
                Data_Choice: "Custom_input",
                Operation: "Interest Rates",
                parent_element_id: "#",
                data: {},
                Sub_Op: sub_op,
                model_code: model_code,
                Valuation_Method: valuation_method,
                Unique_Reference_Id: uniqRefId,
                Position_Id: positionId,
                Product_Variant: productVariant,
                Product_Variant_Name: productVariantName,
                Issuer: issuer,
                Counterparty: counterparty,
                Position_Direction: positionDirection,
                Face_Value: nv,
                Purchase_Price: pp,
                Redemption_Amount: red,
                Spot_Price: cp,
                Valuation_date: val_date,
                Issue_Date: issue_date,
                Maturity_Date: mat_date,
                Settlement_Date: sett_date,
                Last_coupon_date: last_coupdate,
                Coupon_frequency: frequency,
                Coupon_frequency_unit: coupon_frequency_unit,
                internal_rating: internalRating,
                Accrual_daycount_convention: a_basis,
                Discount_daycount_convention: d_basis,
                Discount_Curve: discount_curve,
                Business_day_convention: bus_day_basis,
                Principal_frequency: principal_frequency,
                Principal_frequency_unit: principal_frequency_unit,
                Holiday_Calendar: holiday_cal,
                fixed_or_float_flag: fixed_floatFlag,
                Quantity: quantity,
                External_Rating: externalRating,
                Primary_Currency: primary_currency,
                Margin: margin,
                Base_Rate: base_rate,
                Credit_Spread_Rate: credit_spread_rate,
                Credit_Spread_Curve: credit_spread_curve,
              },
            };
          } else if (model_code === "M002") {
            var uniqRefId = $(
              `#select_unique_reference_id_cf_${computationElementId}`
            ).val();
            var positionId = $(
              `#select_position_id_cf_${computationElementId}`
            ).val();
            var productVariant = $(
              `#select_product_variant_cf_${computationElementId}`
            ).val();
            var productVariantName = $(
              `#select_product_variant_name_cf_${computationElementId}`
            ).val();
            var counterparty = $(
              `#select_counterparty_cf_${computationElementId}`
            ).val();
            var positionDirection = $(
              `#select_position_direction_cf_${computationElementId}`
            ).val();
            var pp = $(
              `#select_purchase_price_cf_${computationElementId}`
            ).val();
            var cp = $(`#select_spot_price_cf_${computationElementId}`).val();
            var red = $(
              `#select_redemption_amount_cf_${computationElementId}`
            ).val();
            var nv = $(
              `#select_nominal_value_cf_${computationElementId}`
            ).val();
            var primary_currency = $(
              `#select_primary_currency_cf_${computationElementId}`
            ).val();
            var val_date = $(
              `#select_reporting_date_cf_${computationElementId}`
            ).val();
            var issue_date = $(
              `#select_issue_date_cf_${computationElementId}`
            ).val();
            var mat_date = $(
              `#select_maturity_date_cf_${computationElementId}`
            ).val();
            var sett_date = $(
              `#select_settlement_date_cf_${computationElementId}`
            ).val();
            var last_coupdate = $(
              `#select_last_payment_date_cf_${computationElementId}`
            ).val();
            var frequency = $(
              `#select_payment_frequency_cf_${computationElementId}`
            ).val();
            var coupon_frequency_unit = $(
              `#select_payment_frequency_units_cf_${computationElementId}`
            ).val();
            var issuer = $(`#select_issuer_cf_${computationElementId}`).val();
            var a_basis = $(
              `#select_accrual_daycount_convention_cf_${computationElementId}`
            ).val();
            var d_basis = $(
              `#select_discount_daycount_convention_cf_${computationElementId}`
            ).val();
            var principal_frequency = $(
              `#select_principal_payment_frequency_cf_${computationElementId}`
            ).val();
            var principal_frequency_unit = $(
              `#select_principal_payment_frequency_units_cf_${computationElementId}`
            ).val();
            var discount_curve = $(
              `#select_discounting_curve_cf_${computationElementId}`
            ).val();
            var bus_day_basis = $(
              `#select_business_convention_cf_${computationElementId}`
            ).val();
            var fixed_floatFlag = $(
              `#select_fixed_or_float_flag_cf_${computationElementId}`
            ).val();
            var internalRating = $(
              `#select_internal_rating_cf_${computationElementId}`
            ).val();
            var externalRating = $(
              `#select_external_rating_cf_${computationElementId}`
            ).val();
            var quantity = $(
              `#select_quantity_cf_${computationElementId}`
            ).val();
            var holiday_cal = $(
              `#select_holiday_calendar_cf_${computationElementId}`
            ).val();
            var margin = $(`#select_margin_cf_${computationElementId}`).val();
            var base_rate = $(
              `#select_base_rate_cf_${computationElementId}`
            ).val();

            var configDict = {
              function: "Interest Rate Products",
              outputs: outputdict,
              inputs: {
                Data_Choice: "Custom_input",
                Operation: "Interest Rates",
                parent_element_id: "#",
                data: {},
                Sub_Op: sub_op,
                model_code: model_code,
                Valuation_Method: valuation_method,
                Unique_Reference_Id: uniqRefId,
                Position_Id: positionId,
                Product_Variant: productVariant,
                Product_Variant_Name: productVariantName,
                Issuer: issuer,
                Counterparty: counterparty,
                Position_Direction: positionDirection,
                Face_Value: nv,
                Purchase_Price: pp,
                Redemption_Amount: red,
                Spot_Price: cp,
                Valuation_date: val_date,
                Issue_Date: issue_date,
                Maturity_Date: mat_date,
                Settlement_Date: sett_date,
                Last_coupon_date: last_coupdate,
                Coupon_frequency: frequency,
                Coupon_frequency_unit: coupon_frequency_unit,
                internal_rating: internalRating,
                Accrual_daycount_convention: a_basis,
                Discount_daycount_convention: d_basis,
                Discount_Curve: discount_curve,
                Business_day_convention: bus_day_basis,
                Principal_frequency: principal_frequency,
                Principal_frequency_unit: principal_frequency_unit,
                Holiday_Calendar: holiday_cal,
                fixed_or_float_flag: fixed_floatFlag,
                Quantity: quantity,
                External_Rating: externalRating,
                Primary_Currency: primary_currency,
                Margin: margin,
                Base_Rate: base_rate,
              },
            };
          } else if (model_code === "M001") {
            var uniqRefId = $(
              `#select_unique_reference_id_cf_${computationElementId}`
            ).val();
            var positionId = $(
              `#select_position_id_cf_${computationElementId}`
            ).val();
            var productVariant = $(
              `#select_product_variant_cf_${computationElementId}`
            ).val();
            var productVariantName = $(
              `#select_product_variant_name_cf_${computationElementId}`
            ).val();
            var counterparty = $(
              `#select_counterparty_cf_${computationElementId}`
            ).val();
            var positionDirection = $(
              `#select_position_direction_cf_${computationElementId}`
            ).val();
            var val_date = $(
              `#select_reporting_date_cf_${computationElementId}`
            ).val();
            var issue_date = $(
              `#select_issue_date_cf_${computationElementId}`
            ).val();
            var mat_date = $(
              `#select_maturity_date_cf_${computationElementId}`
            ).val();
            var sett_date = $(
              `#select_settlement_date_cf_${computationElementId}`
            ).val();
            var pp = $(
              `#select_purchase_price_cf_${computationElementId}`
            ).val();
            var cp = $(`#select_spot_price_cf_${computationElementId}`).val();
            var red = $(
              `#select_redemption_amount_cf_${computationElementId}`
            ).val();
            var nv = $(
              `#select_nominal_value_cf_${computationElementId}`
            ).val();
            var primary_currency = $(
              `#select_primary_currency_cf_${computationElementId}`
            ).val();
            var issuer = $(`#select_issuer_cf_${computationElementId}`).val();
            var a_basis = $(
              `#select_accrual_daycount_convention_cf_${computationElementId}`
            ).val();
            var d_basis = $(
              `#select_discount_daycount_convention_cf_${computationElementId}`
            ).val();
            var principal_frequency = $(
              `#select_principal_payment_frequency_cf_${computationElementId}`
            ).val();
            var principal_frequency_unit = $(
              `#select_principal_payment_frequency_units_cf_${computationElementId}`
            ).val();
            var last_princ_date = $(
              `#select_last_principal_payment_date_cf_${computationElementId}`
            ).val();
            var discount_curve = $(
              `#select_discounting_curve_cf_${computationElementId}`
            ).val();
            var bus_day_basis = $(
              `#select_business_convention_cf_${computationElementId}`
            ).val();
            var benchmark_curve = $(
              `#select_forward_benchmark_curve_cf_${computationElementId}`
            ).val();
            var internalRating = $(
              `#select_internal_rating_cf_${computationElementId}`
            ).val();
            var externalRating = $(
              `#select_external_rating_cf_${computationElementId}`
            ).val();
            var quantity = $(
              `#select_quantity_cf_${computationElementId}`
            ).val();
            var holiday_cal = $(
              `#select_holiday_calendar_cf_${computationElementId}`
            ).val();

            var configDict = {
              function: "Interest Rate Products",
              outputs: outputdict,
              inputs: {
                Data_Choice: "Custom_input",
                Operation: "Interest Rates",
                parent_element_id: "#",
                data: {},
                Sub_Op: sub_op,
                model_code: model_code,
                Valuation_Method: valuation_method,
                Unique_Reference_Id: uniqRefId,
                Position_Id: positionId,
                Product_Variant: productVariant,
                Product_Variant_Name: productVariantName,
                Issuer: issuer,
                Counterparty: counterparty,
                Position_Direction: positionDirection,
                Face_Value: nv,
                Purchase_Price: pp,
                Redemption_Amount: red,
                Spot_Price: cp,
                Valuation_date: val_date,
                Issue_Date: issue_date,
                Maturity_Date: mat_date,
                Settlement_Date: sett_date,
                internal_rating: internalRating,
                Accrual_daycount_convention: a_basis,
                Discount_daycount_convention: d_basis,
                Discount_Curve: discount_curve,
                Business_day_convention: bus_day_basis,
                Benchmark_Curve: benchmark_curve,
                Principal_frequency: principal_frequency,
                Principal_frequency_unit: principal_frequency_unit,
                Last_Principal_Payment_Date: last_princ_date,
                Holiday_Calendar: holiday_cal,
                Quantity: quantity,
                External_Rating: externalRating,
                Primary_Currency: primary_currency,
              },
            };
          } else {
            var configDict = {};
          }
        } else if (elementName === "Equities") {
          var config_dict = {};
          var sub_op = $(
            `#select_equitiesCF_val_${computationElementId}`
          ).val();
          var model_code = $(
            `#select_equitiesCF_val_${computationElementId} option:selected`
          ).attr("data-model_code");
          var valuation_method = $(
            `.finInstrumentsCF_valuation_method_button_${computationElementId}:checked`
          ).val();
          var outputdict = {
            Cashflows: "No",
            Valuation: "No",
            Sensitivity_Analysis: "No",
          };

          if ($(`#cftable1_${computationElementId}`)[0].checked) {
            outputdict["Cashflows"] = "Yes";
          }
          if ($(`#cftable2_${computationElementId}`)[0].checked) {
            outputdict["Valuation"] = "Yes";
          }
          if ($(`#cftable3_${computationElementId}`)[0].checked) {
            outputdict["Sensitivity_Analysis"] = "Yes";
          }
          if (model_code === "M009") {
            var uniqRefId = $(
              `#select_unique_reference_id_cf_${computationElementId}`
            ).val();
            var positionId = $(
              `#select_position_id_cf_${computationElementId}`
            ).val();
            var productVariant = $(
              `#select_product_variant_cf_${computationElementId}`
            ).val();
            var productVariantName = $(
              `#select_product_variant_name_cf_${computationElementId}`
            ).val();
            var issuer = $(`#select_issuer_cf_${computationElementId}`).val();
            var counterparty = $(
              `#select_counterparty_cf_${computationElementId}`
            ).val();
            var counterpartyId = $(
              `#select_counterparty_id_cf_${computationElementId}`
            ).val();
            var positionDirection = $(
              `#select_position_direction_cf_${computationElementId}`
            ).val();
            var val_date = $(
              `#select_reporting_date_cf_${computationElementId}`
            ).val();
            var issue_date = $(
              `#select_issue_date_cf_${computationElementId}`
            ).val();
            var start_date = $(
              `#select_start_date_cf_${computationElementId}`
            ).val();
            var mat_date = $(
              `#select_maturity_date_cf_${computationElementId}`
            ).val();
            var sett_date = $(
              `#select_settlement_date_cf_${computationElementId}`
            ).val();
            var pp = $(
              `#select_purchase_price_cf_${computationElementId}`
            ).val();
            var cp = $(`#select_spot_price_cf_${computationElementId}`).val();
            var nv = $(
              `#select_nominal_value_cf_${computationElementId}`
            ).val();
            var primary_currency = $(
              `#select_primary_currency_cf_${computationElementId}`
            ).val();
            var base_rate = $(
              `#select_base_rate_cf_${computationElementId}`
            ).val();
            var a_basis = $(
              `#select_accrual_daycount_convention_cf_${computationElementId}`
            ).val();
            var d_basis = $(
              `#select_discount_daycount_convention_cf_${computationElementId}`
            ).val();
            var discount_curve = $(
              `#select_discounting_curve_cf_${computationElementId}`
            ).val();
            var bus_day_basis = $(
              `#select_business_convention_cf_${computationElementId}`
            ).val();
            var holiday_cal = $(
              `#select_holiday_calendar_cf_${computationElementId}`
            ).val();
            var frequency = $(
              `#select_payment_frequency_cf_${computationElementId}`
            ).val();
            var principal_frequency = $(
              `#select_principal_payment_frequency_cf_${computationElementId}`
            ).val();
            var principal_frequency_unit = $(
              `#select_principal_payment_frequency_unit_cf_${computationElementId}`
            ).val();
            var sector = $(`#select_sector_cf_${computationElementId}`).val();
            var quantity = $(
              `#select_quantity_cf_${computationElementId}`
            ).val();
            var continuous_growth_rate = $(
              `#select_continous_growth_rate_cf_${computationElementId}`
            ).val();
            var cost_of_equity_capital = $(
              `#select_cost_of_equity_capital_cf_${computationElementId}`
            ).val();
            var payment_frequency = $(
              `#select_payment_frequency_cf_${computationElementId}`
            ).val();
            var last_payment_date = $(
              `#select_last_payment_date_cf_${computationElementId}`
            ).val();
            var payment_frequency_unit = $(
              `#select_payment_frequency_units_cf_${computationElementId}`
            ).val();
            var last_princdate = $(
              `#select_last_principal_payment_date_cf_${computationElementId}`
            ).val();

            var configDict = {
              function: "Equities",
              outputs: outputdict,
              inputs: {
                Data_Choice: "Custom_input",
                Operation: "Interest Rates",
                Valuation_Method: valuation_method,
                parent_element_id: "#",
                data: {},
                Sub_Op: sub_op,
                model_code: model_code,
                Unique_Reference_Id: uniqRefId,
                Position_Id: positionId,
                Product_Variant: productVariant,
                Product_Variant_Name: productVariantName,
                Issuer: issuer,
                Counterparty: counterparty,
                Position_Direction: positionDirection,
                Face_Value: nv,
                Purchase_Price: pp,
                Spot_Price: cp,
                Valuation_date: val_date,
                Start_Date: start_date,
                Settlement_Date: sett_date,
                Last_principal_date: last_princdate,
                Principal_frequency: principal_frequency,
                Principal_frequency_unit: principal_frequency_unit,
                Accrual_daycount_convention: a_basis,
                Discount_daycount_convention: d_basis,
                Discount_Curve: discount_curve,
                Business_day_convention: bus_day_basis,
                Sector: sector,
                Primary_Currency: primary_currency,
                Base_Rate: base_rate,
                Holiday_Calendar: holiday_cal,
                External_Rating: externalRating,
                Quantity: quantity,
                Cost_of_Equity_Capital: cost_of_equity_capital,
                Continuous_Growth_Rate: continuous_growth_rate,
                Payment_Frequency: payment_frequency,
                Last_Payment_Date: last_payment_date,
                Payment_Frequency_Unit: payment_frequency_unit,
              },
            };
          } else {
            var configDict = {};
          }
        } else if (elementName === "Mutual Fund") {
          var config_dict = {};
          var sub_op = $(`#select_mfCF_val_${computationElementId}`).val();
          var model_code = $(
            `#select_mfCF_val_${computationElementId} option:selected`
          ).attr("data-model_code");
          var valuation_method = $(
            `.finInstrumentsCF_valuation_method_button_${computationElementId}:checked`
          ).val();
          var outputdict = {
            Cashflows: "No",
            Valuation: "No",
            Sensitivity_Analysis: "No",
          };

          if ($(`#cftable1_${computationElementId}`)[0].checked) {
            outputdict["Cashflows"] = "Yes";
          }
          if ($(`#cftable2_${computationElementId}`)[0].checked) {
            outputdict["Valuation"] = "Yes";
          }
          if ($(`#cftable3_${computationElementId}`)[0].checked) {
            outputdict["Sensitivity_Analysis"] = "Yes";
          }
          if (model_code === "M009") {
            var uniqRefId = $(
              `#select_unique_reference_id_cf_${computationElementId}`
            ).val();
            var positionId = $(
              `#select_position_id_cf_${computationElementId}`
            ).val();
            var productVariant = $(
              `#select_product_variant_cf_${computationElementId}`
            ).val();
            var productVariantName = $(
              `#select_product_variant_name_cf_${computationElementId}`
            ).val();
            var issuer = $(`#select_issuer_cf_${computationElementId}`).val();
            var counterparty = $(
              `#select_counterparty_cf_${computationElementId}`
            ).val();
            var counterpartyId = $(
              `#select_counterparty_id_cf_${computationElementId}`
            ).val();
            var positionDirection = $(
              `#select_position_direction_cf_${computationElementId}`
            ).val();
            var val_date = $(
              `#select_reporting_date_cf_${computationElementId}`
            ).val();
            var issue_date = $(
              `#select_issue_date_cf_${computationElementId}`
            ).val();
            var start_date = $(
              `#select_start_date_cf_${computationElementId}`
            ).val();
            var mat_date = $(
              `#select_maturity_date_cf_${computationElementId}`
            ).val();
            var sett_date = $(
              `#select_settlement_date_cf_${computationElementId}`
            ).val();
            var pp = $(
              `#select_purchase_price_cf_${computationElementId}`
            ).val();
            var cp = $(`#select_spot_price_cf_${computationElementId}`).val();
            var nv = $(
              `#select_nominal_value_cf_${computationElementId}`
            ).val();
            var primary_currency = $(
              `#select_primary_currency_cf_${computationElementId}`
            ).val();
            var base_rate = $(
              `#select_base_rate_cf_${computationElementId}`
            ).val();
            var a_basis = $(
              `#select_accrual_daycount_convention_cf_${computationElementId}`
            ).val();
            var d_basis = $(
              `#select_discount_daycount_convention_cf_${computationElementId}`
            ).val();
            var discount_curve = $(
              `#select_discounting_curve_cf_${computationElementId}`
            ).val();
            var bus_day_basis = $(
              `#select_business_convention_cf_${computationElementId}`
            ).val();
            var holiday_cal = $(
              `#select_holiday_calendar_cf_${computationElementId}`
            ).val();
            var frequency = $(
              `#select_payment_frequency_cf_${computationElementId}`
            ).val();
            var principal_frequency = $(
              `#select_principal_payment_frequency_cf_${computationElementId}`
            ).val();
            var principal_frequency_unit = $(
              `#select_principal_payment_frequency_unit_cf_${computationElementId}`
            ).val();
            var sector = $(`#select_sector_cf_${computationElementId}`).val();
            var quantity = $(
              `#select_quantity_cf_${computationElementId}`
            ).val();
            var continuous_growth_rate = $(
              `#select_continous_growth_rate_cf_${computationElementId}`
            ).val();
            var cost_of_equity_capital = $(
              `#select_cost_of_equity_capital_cf_${computationElementId}`
            ).val();
            var payment_frequency = $(
              `#select_payment_frequency_cf_${computationElementId}`
            ).val();
            var last_payment_date = $(
              `#select_last_payment_date_cf_${computationElementId}`
            ).val();
            var payment_frequency_unit = $(
              `#select_payment_frequency_units_cf_${computationElementId}`
            ).val();
            var last_princdate = $(
              `#select_last_principal_payment_date_cf_${computationElementId}`
            ).val();

            var configDict = {
              function: "Mutual Fund",
              outputs: outputdict,
              inputs: {
                Data_Choice: "Custom_input",
                Operation: "Interest Rates",
                Valuation_Method: valuation_method,
                parent_element_id: "#",
                data: {},
                Sub_Op: sub_op,
                model_code: model_code,
                Unique_Reference_Id: uniqRefId,
                Position_Id: positionId,
                Product_Variant: productVariant,
                Product_Variant_Name: productVariantName,
                Issuer: issuer,
                Counterparty: counterparty,
                Position_Direction: positionDirection,
                Face_Value: nv,
                Purchase_Price: pp,
                Spot_Price: cp,
                Valuation_date: val_date,
                Start_Date: start_date,
                Settlement_Date: sett_date,
                Last_principal_date: last_princdate,
                Principal_frequency: principal_frequency,
                Principal_frequency_unit: principal_frequency_unit,
                Accrual_daycount_convention: a_basis,
                Discount_daycount_convention: d_basis,
                Discount_Curve: discount_curve,
                Business_day_convention: bus_day_basis,
                Sector: sector,
                Primary_Currency: primary_currency,
                Base_Rate: base_rate,
                Holiday_Calendar: holiday_cal,
                External_Rating: externalRating,
                Quantity: quantity,
                Cost_of_Equity_Capital: cost_of_equity_capital,
                Continuous_Growth_Rate: continuous_growth_rate,
                Payment_Frequency: payment_frequency,
                Last_Payment_Date: last_payment_date,
                Payment_Frequency_Unit: payment_frequency_unit,
              },
            };
          } else {
            var configDict = {};
          }
        }

        var functionConfig = {
          elementID: elementID,
          elementConfig: configDict,
        };
        globalFuncList.push(functionConfig);
      });
    globalFuncList_scenario = globalFuncList;
    if ($(this).attr("data-scenario_part") != "yes") {
      $(`#runModel_${computationElementId}`)
        .closest("body")
        .css("pointer-events", "none");
      setTimeout(() => {
        $(`#runModel_${computationElementId}`).empty();
        $(`#runModel_${computationElementId}`).append(
          `<i class="fa fa-circle-notch fa-spin"></i> Loading`
        );
        $.ajax({
          url: `/users/${urlPath}/computationModule/`,
          data: {
            config: JSON.stringify({
              model: $(`#modelName_${computationElementId}`).attr(
                "data-model_name"
              ),
              configGlobalDict: variableList,
              configGlobalFunc: globalFuncList,
            }),
            operation: "computationRunModel",
            element_id: computationElementId,
            pr_code: windowLocation.split("/")[4],
            sub_process_name: sub_process_name,
          },
          type: "POST",
          dataType: "json",
          success: function (data) {
            $(`#runModel_${computationElementId}`)
              .closest("body")
              .css("pointer-events", "auto");
            var computationModelElementId = data.element_id;
            if (data.rq_job == "True") {
              var jobId = data.job_id;
              let websocketUrlPrefix = "ws://";
              if (window.location.protocol === "https:") {
                websocketUrlPrefix = "wss://";
              }
              var jobConnection = new WebSocket(
                websocketUrlPrefix +
                  window.location.host +
                  `/ws/queued_job_output/${jobId}/`
              );

              jobConnection.onmessage = function (event) {
                flowTabChange();
                $(`#runModel_${computationModelElementId}`).empty();
                $(`#runModel_${computationModelElementId}`).append(
                  computationRunModelButtonText
                );
                $(".standard_button_click").prop("disabled", false);
                bta_apply();

                var data = JSON.parse(event.data);
                if (data.status !== "failed") {
                  $(`#runModel_date_${computationModelElementId}`).html(
                    data.datetime
                  );
                  if (data.run_type == "individual") {
                    if (
                      Object.keys(data).includes(
                        "inter_output_export_message_list"
                      )
                    ) {
                      for (let i of data.inter_output_export_message_list) {
                        if (i) {
                          Swal.fire({ icon: "info", text: i });
                        }
                      }
                    }

                    if (data.element_error_message == "Success") {
                      if (data.output_display_type === "individual") {
                        $(
                          `#runModelContainer_${computationModelElementId}`
                        ).empty();
                        $(
                          `#condition_dropdown_run${computationModelElementId}`
                        ).empty();
                        $(
                          `#multiRunOutputModal_${computationModelElementId}`
                        ).css("display", "none");
                        let outputContainer = `runModelContainer_${computationModelElementId}`;
                        $(`#${outputContainer}`).css("display", "block");
                        if (Object.keys(data).length > 0) {
                          let elementToShow = $(
                            `#runModelCard_${computationModelElementId}`
                          );
                          let elementToHide = $(
                            `#previousRunCard_${computationModelElementId}`
                          );
                          displayModelOutput(
                            data,
                            computationModelElementId,
                            outputContainer,
                            elementToShow,
                            elementToHide,
                            (run = ""),
                            (prevRun = false)
                          );
                        }
                      } else {
                        $(
                          `#MultiRunCarouselInn_${computationModelElementId}`
                        ).empty();
                        $(`#progress_bar_MRM_${computationModelElementId}`)
                          .parent()
                          .css("display", `none`);
                        $(
                          `#statusMessageMRM_${computationModelElementId}`
                        ).text(`Model run complete`);
                        $(`#runModelCard_${computationModelElementId}`).css(
                          "display",
                          "block"
                        );
                        $(
                          `#multiRunOutputModal_${computationModelElementId}`
                        ).css("display", "block");
                        for (otpEle in data.output_elements) {
                          var elementOutputObject =
                            data.output_elements[otpEle];
                          var elementID = elementOutputObject.last_element_id;
                          var label = elementOutputObject.name;
                          var run = elementID;
                          if (data.extra_config) {
                            elementOutputObject["extra_config"] =
                              data.extra_config[otpEle];
                          }
                          var modelStatus = "Run complete...";
                          $(
                            `#MultiRunCarouselInn_${computationModelElementId}`
                          ).append(
                            `<div class="carousel-item" id="outputContainer_${computationModelElementId}${run}">
                                                            <div class='card'>
                                                                <div class='card-header' style="font-size: medium; font-weight: bold;padding:0.4rem;">${label}: <span id="run_${run}_statusMessage_${computationModelElementId}">${modelStatus}</span></div>
                                                                <div class='card-body' style="display:none;max-height: 27rem; overflow:scroll;overflow-x-:hidden;">
                                                                    <div class="card" id="filterRunCard_computation${computationModelElementId}${run}" style="display: none;">
                                                                        <div class="card-body">
                                                                            <button type="button" class="btn btn-tool" id="close_filterRuncard${computationModelElementId}${run}" style="float:right;"><i class="fas fa-remove"></i></button>
                                                                            <div class="btn-group">
                                                                                <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown">
                                                                                {{_("Add Filter")}} for Iteration ${run}
                                                                                <span class="caret"></span>
                                                                                </button>
                                                                                <ul class="dropdown-menu" id="condition_dropdown_run${computationModelElementId}${run}">
                                                                                </ul>
                                                                            </div>
                                                                            <div class="row">
                                                                                <table class="table" id="filter-table_RunModel${computationModelElementId}${run}">
                                                                                </table>
                                                                            </div>
                                                                            <div>
                                                                            <button type="button" id="btnSearchRun${computationModelElementId}${run}" class="btn btn-primary btn-md mx-2 rounded px-2" >Filter <i class="fa fa-filter fa-lg pl-1"></i></button>
                                                                            </div>
                                                                        </div>
                                                                    </div>

                                                                    <div class="modal fade" id="freezeRunCard_computation${computationModelElementId}${run}" role="dialog">
                                                                    <div class="modal-dialog modal-dialog-center" style="left:71px;">
                                                                    <div class="modal-content" style="width:20rem">
                                                                    <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
                                                                    <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Freeze Panes</span>
                                                                    <button type="button" class="close" data-dismiss="modal" id="freeze_pane_close_${computationModelElementId}${run}" aria-label="Close">
                                                                    <span aria-hidden="true">&times;</span>
                                                                    </button>
                                                                    </div>
                                                                    <div class="modal-body" id="freeze_pane_runbody_${computationModelElementId}${run}" style="max-height:26rem;overflow:auto">

                                                                    <label style="text-align: center;">Choose from which side :</label>
                                                                    <div style="display: flex;flex-direction: row;align-content: space-between;justify-content: space-around;align-items: center;margin-top: 33px;">
                                                                    <div class="custom-control custom-checkbox">
                                                                            <input type="checkbox" id="freezerunsec_left_${computationModelElementId}${run}" name="leftrunsec_${computationModelElementId}${run}"  class="freezerunCheckbox checkboxinput custom-control-input" value="left">
                                                                            <label for="freezerunsec_left_${computationModelElementId}${run}" class="custom-control-label"> Left </label><br>
                                                                    </div>
                                                                    <div class="custom-control custom-checkbox">
                                                                            <input type="checkbox" id="freezerunsec_right_${computationModelElementId}${run}" name="rightrunsec_${computationModelElementId}${run}" class="freezerunCheckbox checkboxinput custom-control-input" value="right">
                                                                            <label for="freezerunsec_right_${computationModelElementId}${run}" class="custom-control-label"> Right </label><br>
                                                                    </div>
                                                                    </div>

                                                                    </div>
                                                                    <div class="modal-footer">
                                                                        <button type="button" id="btnFreezePaneRunsec${computationModelElementId}${run}" onclick="unfreezeRunscecardPane(this)" class="btn btn-primary btn-md rounded px-2">Unfreeze</button>
                                                                        <button type="button" id="btnFreezePaneRunsec${computationModelElementId}${run}" onclick="freezeRunscecardPane(this)" class="btn btn-primary btn-md rounded px-2">Freeze</button>
                                                                    </div>
                                                                    </div>
                                                                    </div>
                                                                    </div>
                                                                    <table class="row-border" id="runModelTable_${computationModelElementId}${run}">
                                                                        <thead id="runModelTable_head_${computationModelElementId}${run}">
                                                                            <tr></tr>
                                                                        </thead>
                                                                        <tfoot>
                                                                            <tr></tr>
                                                                        </tfoot>
                                                                        <tbody id="runModelTable_body_${computationModelElementId}${run}">
                                                                        </tbody>
                                                                    </table>
                                                                </div>
                                                            </div>
                                                        </div>`
                          );
                          $(`#MultiRunCarouselInn_${computationModelElementId}`)
                            .find(".carousel-item")
                            .removeClass("active");
                          $(
                            `#run_${run}_carousel_${computationModelElementId}`
                          ).addClass("active");
                          $(
                            `#MultiRunCarouselInn_${computationModelElementId}`
                          ).css("display", "block");
                          if (
                            elementOutputObject.element_error_message ==
                            "Success"
                          ) {
                            $(
                              `#run_${run}_statusMessage_${computationModelElementId}`
                            ).text("Output");
                            let outputContainer = `outputContainer_${computationModelElementId}${run} > .card > .card-body`;
                            let elementToShow = $(
                              `#outputContainer_${computationModelElementId}${run}`
                            )
                              .find(".card")
                              .find(".card-body");
                            let elementToHide = $(
                              `#previousRunCard_${computationModelElementId}`
                            );
                            displayModelOutput(
                              elementOutputObject,
                              computationModelElementId,
                              outputContainer,
                              elementToShow,
                              elementToHide,
                              (run = run),
                              (prevRun = false)
                            );
                            $(
                              `#outputContainer_${computationModelElementId}${run}`
                            ).addClass("active");
                          } else {
                            $(
                              `#run_${run}_statusMessage_${computationModelElementId}`
                            ).text(elementOutputObject.element_error_message);
                          }
                        }
                      }
                    } else {
                      Swal.fire({
                        icon: "error",
                        text: data.element_error_message,
                      });
                    }
                  } else if (data.run_type == "scenario_run") {
                    var model_name = $(
                      `#modelName_${computationModelElementId}`
                    ).attr("data-model_name");
                    $(
                      `#MultiRunCarouselInn_${computationModelElementId}`
                    ).empty();
                    $(`#progress_bar_MRM_${computationModelElementId}`)
                      .parent()
                      .css("display", `none`);
                    $(`#statusMessageMRM_${computationModelElementId}`).text(
                      `Model run complete`
                    );
                    $(`#runModelCard_${computationModelElementId}`).css(
                      "display",
                      "block"
                    );
                    $(`#multiRunOutputModal_${computationModelElementId}`).css(
                      "display",
                      "block"
                    );
                    $(`#runModelContainer_${computationModelElementId}`).css(
                      "display",
                      "none"
                    );
                    var baseModelOutput = data["base_model_output"];
                    var elementID = "base_model_output";
                    var label = "Base Model";
                    var run = elementID;
                    var modelStatus = "Run complete...";
                    $(
                      `#MultiRunCarouselInn_${computationModelElementId}`
                    ).append(
                      `<div class="carousel-item" id="outputContainer_${computationModelElementId}${run}">
                                                <div class='card'>
                                                    <div class='card-header' style="font-size: medium; font-weight: bold;padding:0.4rem;">${label}: <span id="run_${run}_statusMessage_${computationModelElementId}">${modelStatus}</span></div>
                                                    <div class='card-body' style="display:none;max-height: 27rem; overflow:scroll;overflow-x-:hidden;">
                                                        <div class="card" id="filterRunCard_computation${computationModelElementId}${run}" style="display: none;">
                                                            <div class="card-body">
                                                                <button type="button" class="btn btn-tool" id="close_filterRuncard${computationModelElementId}${run}" style="float:right;"><i class="fas fa-remove"></i></button>
                                                                <div class="btn-group">
                                                                    <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown">
                                                                    {{_("Add Filter")}} for Iteration ${run}
                                                                    <span class="caret"></span>
                                                                    </button>
                                                                    <ul class="dropdown-menu" id="condition_dropdown_run${computationModelElementId}${run}">
                                                                    </ul>
                                                                </div>
                                                                <div class="row">
                                                                    <table class="table" id="filter-table_RunModel${computationModelElementId}${run}">
                                                                    </table>
                                                                </div>
                                                                <div>
                                                                <button type="button" id="btnSearchRun${computationModelElementId}${run}" class="btn btn-primary btn-md mx-2 rounded px-2" >Filter <i class="fa fa-filter fa-lg pl-1"></i></button>
                                                                </div>
                                                            </div>
                                                        </div>

                                                        <div class="modal fade" id="freezeRunCard_computation${computationModelElementId}${run}" role="dialog">
                                                        <div class="modal-dialog modal-dialog-center" style="left:71px;">
                                                        <div class="modal-content" style="width:20rem">
                                                        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
                                                        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Freeze Panes</span>
                                                        <button type="button" class="close" data-dismiss="modal" id="freeze_pane_close_${computationModelElementId}${run}" aria-label="Close">
                                                        <span aria-hidden="true">&times;</span>
                                                        </button>
                                                        </div>
                                                        <div class="modal-body" id="freeze_pane_runbody_${computationModelElementId}${run}" style="max-height:26rem;overflow:auto">

                                                        <label style="text-align: center;">Choose from which side :</label>
                                                        <div style="display: flex;flex-direction: row;align-content: space-between;justify-content: space-around;align-items: center;margin-top: 33px;">
                                                        <div class="custom-control custom-checkbox">
                                                                <input type="checkbox" id="freezerunsec_left_${computationModelElementId}${run}" name="leftrunsec_${computationModelElementId}${run}"  class="freezerunCheckbox checkboxinput custom-control-input" value="left">
                                                                <label for="freezerunsec_left_${computationModelElementId}${run}" class="custom-control-label"> Left </label><br>
                                                        </div>
                                                        <div class="custom-control custom-checkbox">
                                                                <input type="checkbox" id="freezerunsec_right_${computationModelElementId}${run}" name="rightrunsec_${computationModelElementId}${run}" class="freezerunCheckbox checkboxinput custom-control-input" value="right">
                                                                <label for="freezerunsec_right_${computationModelElementId}${run}" class="custom-control-label"> Right </label><br>
                                                        </div>
                                                        </div>

                                                        </div>
                                                        <div class="modal-footer">
                                                            <button type="button" id="btnFreezePaneRunsec${computationModelElementId}${run}" onclick="unfreezeRunscecardPane(this)" class="btn btn-primary btn-md rounded px-2">Unfreeze</button>
                                                            <button type="button" id="btnFreezePaneRunsec${computationModelElementId}${run}" onclick="freezeRunscecardPane(this)" class="btn btn-primary btn-md rounded px-2">Freeze</button>
                                                        </div>
                                                        </div>
                                                        </div>
                                                        </div>
                                                        <table class="row-border" id="runModelTable_${computationModelElementId}${run}">
                                                            <thead id="runModelTable_head_${computationModelElementId}${run}">
                                                                <tr></tr>
                                                            </thead>
                                                            <tfoot>
                                                                <tr></tr>
                                                            </tfoot>
                                                            <tbody id="runModelTable_body_${computationModelElementId}${run}">
                                                            </tbody>
                                                        </table>
                                                    </div>
                                                </div>
                                            </div>`
                    );
                    $(`#MultiRunCarouselInn_${computationModelElementId}`)
                      .find(".carousel-item")
                      .removeClass("active");
                    $(
                      `#run_${run}_carousel_${computationModelElementId}`
                    ).addClass("active");
                    $(`#MultiRunCarouselInn_${computationModelElementId}`).css(
                      "display",
                      "block"
                    );
                    if (baseModelOutput.element_error_message == "Success") {
                      $(
                        `#run_${run}_statusMessage_${computationModelElementId}`
                      ).text("Output");
                      let outputContainer = `outputContainer_${computationModelElementId}${run} > .card > .card-body`;
                      let elementToShow = $(
                        `#outputContainer_${computationModelElementId}${run}`
                      )
                        .find(".card")
                        .find(".card-body");
                      let elementToHide = $(
                        `#previousRunCard_${computationModelElementId}`
                      );
                      displayModelOutput(
                        baseModelOutput,
                        computationModelElementId,
                        outputContainer,
                        elementToShow,
                        elementToHide,
                        (run = run),
                        (prevRun = false)
                      );
                      $(
                        `#outputContainer_${computationModelElementId}${run}`
                      ).addClass("active");
                    } else {
                      $(
                        `#run_${run}_statusMessage_${computationModelElementId}`
                      ).text(baseModelOutput.element_error_message);
                    }
                    var scenario_output = data["scenario_output"];
                    for (let [key, value] of Object.entries(scenario_output)) {
                      var elementOutputObject = value;
                      var elementID = key;
                      var label = elementOutputObject.name;
                      var run = elementID;
                      var modelStatus = "Run complete...";
                      $(
                        `#MultiRunCarouselInn_${computationModelElementId}`
                      ).append(
                        `<div class="carousel-item" id="outputContainer_${computationModelElementId}${run}">
                                                    <div class='card'>
                                                        <div class='card-header' style="font-size: medium; font-weight: bold;padding:0.4rem;">${label}: <span id="run_${run}_statusMessage_${computationModelElementId}">${modelStatus}</span></div>
                                                        <div class='card-body' style="display:none;max-height: 27rem; overflow:scroll;overflow-x-:hidden;">
                                                            <div class="card" id="filterRunCard_computation${computationModelElementId}${run}" style="display: none;">
                                                                <div class="card-body">
                                                                    <button type="button" class="btn btn-tool" id="close_filterRuncard${computationModelElementId}${run}" style="float:right;"><i class="fas fa-remove"></i></button>
                                                                    <div class="btn-group">
                                                                        <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown">
                                                                        {{_("Add Filter")}} for Iteration ${run}
                                                                        <span class="caret"></span>
                                                                        </button>
                                                                        <ul class="dropdown-menu" id="condition_dropdown_run${computationModelElementId}${run}">
                                                                        </ul>
                                                                    </div>
                                                                    <div class="row">
                                                                        <table class="table" id="filter-table_RunModel${computationModelElementId}${run}">
                                                                        </table>
                                                                    </div>
                                                                    <div>
                                                                    <button type="button" id="btnSearchRun${computationModelElementId}${run}" class="btn btn-primary btn-md mx-2 rounded px-2" >Filter <i class="fa fa-filter fa-lg pl-1"></i></button>
                                                                    </div>
                                                                </div>
                                                            </div>

                                                            <div class="modal fade" id="freezeRunCard_computation${computationModelElementId}${run}" role="dialog">
                                                            <div class="modal-dialog modal-dialog-center" style="left:71px;">
                                                            <div class="modal-content" style="width:20rem">
                                                            <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
                                                            <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Freeze Panes</span>
                                                            <button type="button" class="close" data-dismiss="modal" id="freeze_pane_close_${computationModelElementId}${run}" aria-label="Close">
                                                            <span aria-hidden="true">&times;</span>
                                                            </button>
                                                            </div>
                                                            <div class="modal-body" id="freeze_pane_runbody_${computationModelElementId}${run}" style="max-height:26rem;overflow:auto">

                                                            <label style="text-align: center;">Choose from which side :</label>
                                                            <div style="display: flex;flex-direction: row;align-content: space-between;justify-content: space-around;align-items: center;margin-top: 33px;">
                                                            <div class="custom-control custom-checkbox">
                                                                    <input type="checkbox" id="freezerunsec_left_${computationModelElementId}${run}" name="leftrunsec_${computationModelElementId}${run}"  class="freezerunCheckbox checkboxinput custom-control-input" value="left">
                                                                    <label for="freezerunsec_left_${computationModelElementId}${run}" class="custom-control-label"> Left </label><br>
                                                            </div>
                                                            <div class="custom-control custom-checkbox">
                                                                    <input type="checkbox" id="freezerunsec_right_${computationModelElementId}${run}" name="rightrunsec_${computationModelElementId}${run}" class="freezerunCheckbox checkboxinput custom-control-input" value="right">
                                                                    <label for="freezerunsec_right_${computationModelElementId}${run}" class="custom-control-label"> Right </label><br>
                                                            </div>
                                                            </div>

                                                            </div>
                                                            <div class="modal-footer">
                                                                <button type="button" id="btnFreezePaneRunsec${computationModelElementId}${run}" onclick="unfreezeRunscecardPane(this)" class="btn btn-primary btn-md rounded px-2">Unfreeze</button>
                                                                <button type="button" id="btnFreezePaneRunsec${computationModelElementId}${run}" onclick="freezeRunscecardPane(this)" class="btn btn-primary btn-md rounded px-2">Freeze</button>
                                                            </div>
                                                            </div>
                                                            </div>
                                                            </div>
                                                            <table class="row-border" id="runModelTable_${computationModelElementId}${run}">
                                                                <thead id="runModelTable_head_${computationModelElementId}${run}">
                                                                    <tr></tr>
                                                                </thead>
                                                                <tfoot>
                                                                    <tr></tr>
                                                                </tfoot>
                                                                <tbody id="runModelTable_body_${computationModelElementId}${run}">
                                                                </tbody>
                                                            </table>
                                                        </div>
                                                    </div>
                                                </div>`
                      );
                      $(`#MultiRunCarouselInn_${computationModelElementId}`)
                        .find(".carousel-item")
                        .removeClass("active");
                      $(
                        `#run_${run}_carousel_${computationModelElementId}`
                      ).addClass("active");
                      $(
                        `#MultiRunCarouselInn_${computationModelElementId}`
                      ).css("display", "block");
                      if (
                        elementOutputObject.element_error_message == "Success"
                      ) {
                        $(
                          `#run_${run}_statusMessage_${computationModelElementId}`
                        ).text("Output");
                        let outputContainer = `outputContainer_${computationModelElementId}${run} > .card > .card-body`;
                        let elementToShow = $(
                          `#outputContainer_${computationModelElementId}${run}`
                        )
                          .find(".card")
                          .find(".card-body");
                        let elementToHide = $(
                          `#previousRunCard_${computationModelElementId}`
                        );
                        displayModelOutput(
                          elementOutputObject,
                          computationModelElementId,
                          outputContainer,
                          elementToShow,
                          elementToHide,
                          (run = run),
                          (prevRun = false)
                        );
                        $(
                          `#outputContainer_${computationModelElementId}${run}`
                        ).addClass("active");
                      } else {
                        $(
                          `#run_${run}_statusMessage_${computationModelElementId}`
                        ).text(elementOutputObject.element_error_message);
                      }
                    }
                  }
                } else {
                  jobConnection.close(1000);
                  $(`#runModel_${computationElementId}`).text(
                    computationRunModelButtonText
                  );
                  Swal.fire({
                    icon: "error",
                    text: "Error! Failure in executing the Computation Model. Please check your Model and try again.",
                  });
                }
              };
              jobConnection.onerror = function () {
                jobConnection.close(1000);
                $(`#runModel_${computationElementId}`).text(
                  computationRunModelButtonText
                );
                Swal.fire({
                  icon: "error",
                  text: "Error! Failure in executing the Computation Model. Please check your Model and try again.",
                });
              };
            } else {
              $(`#runModel_${computationElementId}`).empty();
              $(`#runModel_${computationElementId}`).append(
                computationRunModelButtonText
              );
              $(".standard_button_click").prop("disabled", false);
              bta_apply();
              $(`#runModel_date_${computationElementId}`).html(data.datetime);

              var model_name = $(`#modelName_${computationElementId}`).attr(
                "data-model_name"
              );
              $(`#MultiRunCarouselInn_${computationElementId}`).empty();
              $(`#progress_bar_MRM_${computationElementId}`)
                .parent()
                .parent()
                .css("display", "block");
              $(`#progress_bar_MRM_${computationElementId}`)
                .css("width", `0%`)
                .attr("aria-valuenow", 0);
              $(`#runModelCard_${computationElementId}`).css(
                "display",
                "block"
              );
              $(`#multiRunOutputModal_${computationElementId}`).css(
                "display",
                "block"
              );
              $(`#statusMessageMRM_${computationElementId}`)
                .text("Run in progress....")
                .trigger("change");

              let websocketUrlPrefix = "ws://";
              if (window.location.protocol === "https:") {
                websocketUrlPrefix = "wss://";
              }
              var intermediate_event_source = new WebSocket(
                websocketUrlPrefix +
                  window.location.host +
                  `/ws/run_model_multi_run_inter/${model_name}/`
              );

              intermediate_event_source.onopen = function (event) {
                intermediate_event_source.send(
                  JSON.stringify({ path: windowLocation })
                );
              };

              var new_event_source = new WebSocket(
                websocketUrlPrefix +
                  window.location.host +
                  `/ws/run_model_multi_run/${model_name}/`
              );

              new_event_source.onopen = function (event) {
                new_event_source.send(JSON.stringify({ path: windowLocation }));
              };

              $(`#quitMRM_${computationElementId}`)
                .off("click")
                .on("click", function () {
                  new_event_source.close();
                  intermediate_event_source.close();
                });

              intermediate_event_source.onmessage = function (event) {
                var inter_output = JSON.parse(event.data);
                comp_per = inter_output.comp_per;
                $(`#statusMessageMRM_${computationElementId}`).text(
                  inter_output.message
                );
                $(`#progress_bar_MRM_${computationElementId}`)
                  .parent()
                  .parent()
                  .css("display", "block");
                $(`#progress_bar_MRM_${computationElementId}`)
                  .css("width", `${comp_per}%`)
                  .attr("aria-valuenow", comp_per);
                var inter_output_export_message_list =
                  inter_output["inter_output_export_message_list"];
                if (comp_per == 100) {
                  intermediate_event_source.close();
                }
                for (let i of inter_output_export_message_list) {
                  if (i) {
                    Swal.fire({ icon: "info", text: i });
                  }
                }
              };
              new_event_source.onmessage = function (event) {
                var output = JSON.parse(event.data);
                let runMessage = output.message;
                var comp_per = output.main_comp_per;
                $(`#progress_bar_MRM_${computationModelElementId}`)
                  .parent()
                  .parent()
                  .css("display", "block");
                $(`#progress_bar_MRM_${computationModelElementId}`)
                  .css("width", `${comp_per}%`)
                  .attr("aria-valuenow", comp_per);
                var data = output.content;
                var run = output.run;
                $(`#statusMessageMRM_${computationModelElementId}`)
                  .text("Run complete....")
                  .trigger("change");
                $(`#statusMessageMRM_${computationModelElementId}`)
                  .text(`Loading run ${run} data...`)
                  .trigger("change");
                $(`#MultiRunCarouselInn_${computationModelElementId}`).append(
                  `<div class="carousel-item multi-run-data-output" id="outputContainer_${computationModelElementId}${run}">
                                        <div class='card'>
                                            <div class='card-header' style="font-size: medium; font-weight: bold;padding:0.4rem;">Iteration ${run}: <span id="run_${run}_statusMessage_${computationModelElementId}">Run complete...</span></div>
                                            <div class='card-body' style="display:none;max-height: 27rem; overflow:scroll;overflow-x-:hidden;">
                                                <div class="card" id="filterRunCard_computation${computationModelElementId}${run}" style="display: none;">
                                                    <div class="card-body">
                                                        <button type="button" class="btn btn-tool" id="close_filterRuncard${computationModelElementId}${run}" style="float:right;"><i class="fas fa-remove"></i></button>
                                                        <div class="btn-group">
                                                            <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown">
                                                            {{_("Add Filter")}} for Iteration ${run}
                                                            <span class="caret"></span>
                                                            </button>
                                                            <ul class="dropdown-menu" id="condition_dropdown_run${computationModelElementId}${run}">
                                                            </ul>
                                                        </div>
                                                        <div class="row">
                                                            <table class="table" id="filter-table_RunModel${computationModelElementId}${run}">
                                                            </table>
                                                        </div>
                                                        <div>
                                                        <button type="button" id="btnSearchRun${computationModelElementId}${run}" class="btn btn-primary btn-md mx-2 rounded px-2" >Filter <i class="fa fa-filter fa-lg pl-1"></i></button>
                                                        </div>
                                                    </div>
                                                </div>

                                                <div class="modal fade" id="freezeRunCard_computation${computationModelElementId}${run}" role="dialog">
                                                <div class="modal-dialog modal-dialog-center" style="left:71px;">
                                                <div class="modal-content" style="width:20rem">
                                                <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
                                                <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Freeze Panes</span>
                                                <button type="button" class="close" data-dismiss="modal" id="freeze_pane_close_${computationModelElementId}${run}" aria-label="Close">
                                                <span aria-hidden="true">&times;</span>
                                                </button>
                                                </div>
                                                <div class="modal-body" id="freeze_pane_runbody_${computationModelElementId}${run}" style="max-height:26rem;overflow:auto">

                                                <label style="text-align: center;">Choose from which side :</label>
                                                <div style="display: flex;flex-direction: row;align-content: space-between;justify-content: space-around;align-items: center;margin-top: 33px;">
                                                <div class="custom-control custom-checkbox">
                                                        <input type="checkbox" id="freezerunsec_left_${computationModelElementId}${run}" name="leftrunsec_${computationModelElementId}${run}"  class="freezerunCheckbox checkboxinput custom-control-input" value="left">
                                                        <label for="freezerunsec_left_${computationModelElementId}${run}" class="custom-control-label"> Left </label><br>
                                                </div>
                                                <div class="custom-control custom-checkbox">
                                                        <input type="checkbox" id="freezerunsec_right_${computationModelElementId}${run}" name="rightrunsec_${computationModelElementId}${run}" class="freezerunCheckbox checkboxinput custom-control-input" value="right">
                                                        <label for="freezerunsec_right_${computationModelElementId}${run}" class="custom-control-label"> Right </label><br>
                                                </div>
                                                </div>

                                                </div>
                                                <div class="modal-footer">
                                                    <button type="button" id="btnFreezePaneRunsec${computationModelElementId}${run}" onclick="unfreezeRunscecardPane(this)" class="btn btn-primary btn-md rounded px-2">Unfreeze</button>
                                                    <button type="button" id="btnFreezePaneRunsec${computationModelElementId}${run}" onclick="freezeRunscecardPane(this)" class="btn btn-primary btn-md rounded px-2">Freeze</button>
                                                </div>
                                                </div>
                                                </div>
                                                </div>
                                                <table class="row-border" id="runModelTable_${computationModelElementId}${run}">
                                                    <thead id="runModelTable_head_${computationModelElementId}${run}">
                                                        <tr></tr>
                                                    </thead>
                                                    <tfoot>
                                                        <tr></tr>
                                                    </tfoot>
                                                    <tbody id="runModelTable_body_${computationModelElementId}${run}">
                                                    </tbody>
                                                </table>
                                            </div>
                                        </div>
                                    </div>`
                );
                $(`#MultiRunCarouselInn_${computationModelElementId}`)
                  .find(".carousel-item")
                  .removeClass("active");
                $(`#run_${run}_carousel_${computationModelElementId}`).addClass(
                  "active"
                );
                $(`#MultiRunCarouselInn_${computationModelElementId}`).css(
                  "display",
                  "block"
                );
                $(`#previousRunCard_${computationModelElementId}`).css(
                  "display",
                  "none"
                );
                if (runMessage == "Run_successfull") {
                  if (data.element_error_message == "Success") {
                    $(
                      `#run_${run}_statusMessage_${computationModelElementId}`
                    ).text("Output");
                    let outputContainer = `outputContainer_${computationModelElementId}${run} > .card > .card-body`;
                    let elementToShow = $(
                      `#outputContainer_${computationModelElementId}${run}`
                    )
                      .find(".card")
                      .find(".card-body");
                    let elementToHide = $(
                      `#previousRunCard_${computationModelElementId}`
                    );
                    displayModelOutput(
                      data,
                      computationModelElementId,
                      outputContainer,
                      elementToShow,
                      elementToHide,
                      (run = run),
                      (prevRun = false)
                    );
                    $(
                      `#outputContainer_${computationModelElementId}${run}`
                    ).addClass("active");
                  } else {
                    $(`#statusMessageMRM_${computationModelElementId}`).text(
                      `Error performing run ${run}.`
                    );
                    if (data.element_error_message !== "Success") {
                      $(
                        `#run_${run}_statusMessage_${computationModelElementId}`
                      ).text(data.element_error_message);
                    }
                  }
                } else {
                  $(
                    `#run_${run}_statusMessage_${computationModelElementId}`
                  ).text(runMessage);
                }
                $(`#statusMessageMRM_${computationModelElementId}`).text(
                  `Run ${Number(run) + 1} in progress...`
                );
                if (comp_per == 100) {
                  new_event_source.close();
                  intermediate_event_source.close();
                  $(`#statusMessageMRM_${computationModelElementId}`).text(
                    "Model run complete."
                  );
                }
              };

              new_event_source.onerror = function () {
                new_event_source.close();
                intermediate_event_source.close();
              };
              intermediate_event_source.onerror = function () {
                new_event_source.close();
                intermediate_event_source.close();
              };
            }
            $(".breadcrumb-holder").attr("data-reload", "yes");
            flowTabChange();
          },
          error: function () {
            Swal.fire({ icon: "error", text: "Error! Please try again." });
            $(".standard_button_click").prop("disabled", false);
            $(`#runModel_${computationElementId}`).empty();
            $(`#runModel_${computationElementId}`).append(
              computationRunModelButtonText
            );
            bta_apply();
          },
        });
      }, 1000);
    }
  });
}

function previousRunOutputHandler(computationElementId) {
  $.ajax({
    url: `/users/${urlPath}/computationModule/`,
    data: {
      model: $(`#modelName_${computationElementId}`).attr("data-model_name"),
      operation: "computationPreviousRun",
      element_id: computationElementId,
    },
    type: "POST",
    dataType: "json",
    success: function (data) {
      bta_apply();

      $(`#previousRunContainer_${computationElementId}`).empty();
      $(`#runModelContainer_${computationElementId}`).empty();
      $(`#condition_dropdown_prev_run${computationElementId}`).empty();

      $(`#previousRunDate_${computationElementId}`).text("");
      if (Object.keys(data).length > 0) {
        $(`#previousRunDate_${computationElementId}`).text(data.prev_run_date);
        let outputContainer = `previousRunContainer_${computationElementId}`;
        if (data.output_type !== "multi-output-display") {
          if (data.output_type === "multi-output-finInstrument") {
            data.content["last_element_name"] = "Interest Rate Products";
          } else if (data.output_type === "Boosting Algorithm") {
            data.content["last_element_name"] = "Boosting Algorithm";
          } else if (data.output_type === "multi-output-optimiser") {
            data.content["last_element_name"] = "Optimiser";
          } else if (data.output_type === "multi-output-bootstrap") {
            data.content["last_element_name"] = "VaR Backtesting";
          } else if (
            data.output_type === "CART" ||
            data.output_type === "CART Algorithm"
          ) {
            data.content["last_element_name"] = data.output_type;
          } else if (data.output_type === "multi-output-linearRegression") {
            data.content["last_element_name"] = "Linear Regression";
          } else if (data.output_type === "multi-output-logisticRegression") {
            data.content["last_element_name"] = "Logistic Regression";
          } else if (data.output_type === "multi-output-analyseTSData") {
            data.content["last_element_name"] = "Analyse Time Series Data";
          } else if (data.output_type === "multi-output-trainARIMA") {
            data.content["last_element_name"] = "Train an ARIMA Model";
          } else if (data.output_type === "multi-output-trainGARCH") {
            data.content["last_element_name"] = "Train an EWMA Model";
          } else if (data.output_type === "multi-output-trainEWMA") {
            data.content["last_element_name"] = "Train a GARCH Model";
          } else if (data.output_type === "Goodness Fit Test") {
            data.content["last_element_name"] = "Goodness Of Fit Test";
          } else if (data.output_type === "Fit Discrete Distribution") {
            data.content["last_element_name"] = "Fit Discrete Distribution";
          } else if (data.output_type === "Copula") {
            data.content["last_element_name"] = "Copula";
          } else if (data.output_type === "Portfolio_Valuation_Output") {
            data.content["last_element_name"] = "Portfolio Valuation";
          } else if (data.output_type === "Backtesting") {
            data.content["last_element_name"] = "VaR Backtesting";
          }
          let elementToShow = $(`#previousRunCard_${computationElementId}`);
          let elementToHide = $(`#runModelCard_${computationElementId}`);
          displayModelOutput(
            data.content,
            computationElementId,
            outputContainer,
            elementToShow,
            elementToHide,
            (run = "prev"),
            (prevRun = true)
          );
        } else {
          $(`#runModel_date_${computationElementId}`).html(data.prev_run_date);
          $(`#runModelCard_${computationElementId}`)
            .find(".no_run_message")
            .css("display", "none");
          $(`#MultiRunCarouselInn_${computationElementId}`).empty();
          $(`#progress_bar_MRM_${computationElementId}`)
            .parent()
            .css("display", `none`);
          $(`#statusMessageMRM_${computationElementId}`).text(
            `Last run's output`
          );
          $(`#previousRunCard_${computationElementId}`).css("display", "none");
          $(`#runModelCard_${computationElementId}`).css("display", "block");
          $(`#multiRunOutputModal_${computationElementId}`).css(
            "display",
            "block"
          );
          for (otpEle in data.content) {
            var elementOutputObject = data.content[otpEle];
            var elementID = elementOutputObject.last_element_id;
            var label = elementOutputObject.name;
            var run = elementID;
            var modelStatus = "Run complete...";
            $(`#MultiRunCarouselInn_${computationElementId}`).append(
              `<div class="carousel-item" id="outputContainer_${computationElementId}${run}">
                                <div class='card'>
                                    <div class='card-header' style="font-size: medium; font-weight: bold;padding:0.4rem;">${label}: <span id="run_${run}_statusMessage_${computationElementId}">${modelStatus}</span></div>
                                    <div class='card-body' style="display:none;max-height: 27rem; overflow:scroll;overflow-x-:hidden;">
                                        <div class="card" id="filterRunCard_computation${computationElementId}${run}" style="display: none;">
                                            <div class="card-body">
                                                <button type="button" class="btn btn-tool" id="close_filterRuncard${computationElementId}${run}" style="float:right;"><i class="fas fa-remove"></i></button>
                                                <div class="btn-group">
                                                    <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown">
                                                    {{_("Add Filter")}} for Iteration ${run}
                                                    <span class="caret"></span>
                                                    </button>
                                                    <ul class="dropdown-menu" id="condition_dropdown_run${computationElementId}${run}">
                                                    </ul>
                                                </div>
                                                <div class="row">
                                                    <table class="table" id="filter-table_RunModel${computationElementId}${run}">
                                                    </table>
                                                </div>
                                                <div>
                                                <button type="button" id="btnSearchRun${computationElementId}${run}" class="btn btn-primary btn-md mx-2 rounded px-2" >Filter <i class="fa fa-filter fa-lg pl-1"></i></button>
                                                </div>
                                            </div>
                                        </div>

                                        <div class="modal fade" id="freezeRunCard_computation${computationElementId}${run}" role="dialog">
                                        <div class="modal-dialog modal-dialog-center" style="left:71px;">
                                        <div class="modal-content" style="width:20rem">
                                        <div class="modal-header" style="background:#565a5e; color:white; text-align:center;padding-bottom:2%;padding-top:3%;">
                                        <span class="modal-title w-100" id="myModalLabel" style="font-size:1.2rem">Freeze Panes</span>
                                        <button type="button" class="close" data-dismiss="modal" id="freeze_pane_close_${computationElementId}${run}" aria-label="Close">
                                        <span aria-hidden="true">&times;</span>
                                        </button>
                                        </div>
                                        <div class="modal-body" id="freeze_pane_runbody_${computationElementId}${run}" style="max-height:26rem;overflow:auto">

                                        <label style="text-align: center;">Choose from which side :</label>
                                        <div style="display: flex;flex-direction: row;align-content: space-between;justify-content: space-around;align-items: center;margin-top: 33px;">
                                        <div class="custom-control custom-checkbox">
                                                <input type="checkbox" id="freezerunsec_left_${computationElementId}${run}" name="leftrunsec_${computationElementId}${run}"  class="freezerunCheckbox checkboxinput custom-control-input" value="left">
                                                <label for="freezerunsec_left_${computationElementId}${run}" class="custom-control-label"> Left </label><br>
                                        </div>
                                        <div class="custom-control custom-checkbox">
                                                <input type="checkbox" id="freezerunsec_right_${computationElementId}${run}" name="rightrunsec_${computationElementId}${run}" class="freezerunCheckbox checkboxinput custom-control-input" value="right">
                                                <label for="freezerunsec_right_${computationElementId}${run}" class="custom-control-label"> Right </label><br>
                                        </div>
                                        </div>

                                        </div>
                                        <div class="modal-footer">
                                            <button type="button" id="btnFreezePaneRunsec${computationElementId}${run}" onclick="unfreezeRunscecardPane(this)" class="btn btn-primary btn-md rounded px-2">Unfreeze</button>
                                            <button type="button" id="btnFreezePaneRunsec${computationElementId}${run}" onclick="freezeRunscecardPane(this)" class="btn btn-primary btn-md rounded px-2">Freeze</button>
                                        </div>
                                        </div>
                                        </div>
                                        </div>
                                        <table class="row-border" id="runModelTable_${computationElementId}${run}">
                                            <thead id="runModelTable_head_${computationElementId}${run}">
                                                <tr></tr>
                                            </thead>
                                            <tfoot>
                                                <tr></tr>
                                            </tfoot>
                                            <tbody id="runModelTable_body_${computationElementId}${run}">
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>`
            );
            $(`#MultiRunCarouselInn_${computationElementId}`)
              .find(".carousel-item")
              .removeClass("active");
            $(`#run_${run}_carousel_${computationElementId}`).addClass(
              "active"
            );
            $(`#MultiRunCarouselInn_${computationElementId}`).css(
              "display",
              "block"
            );
            $(`#run_${run}_statusMessage_${computationElementId}`).text(
              "Output"
            );
            let outputContainer = `outputContainer_${computationElementId}${run} > .card > .card-body`;
            let elementToShow = $(
              `#outputContainer_${computationElementId}${run}`
            )
              .find(".card")
              .find(".card-body");
            let elementToHide = $(`#previousRunCard_${computationElementId}`);
            displayModelOutput(
              elementOutputObject,
              computationElementId,
              outputContainer,
              elementToShow,
              elementToHide,
              (run = run),
              (prevRun = true)
            );
            $(`#outputContainer_${computationElementId}${run}`).addClass(
              "active"
            );
          }
        }
      }
    },
    error: function () {
      Swal.fire({ icon: "error", text: "Error! Please try again." });
      $(".standard_button_click").prop("disabled", false);
      bta_apply();
    },
  });
}

function initialiseDataTable(tableId, scroll_y = "40vh") {
  $(`#${tableId}`)
    .DataTable({
      autoWidth: true,
      scrollY: scroll_y,
      scrollCollapse: true,
      scrollX: true,
      orderCellsTop: true,
      responsive: true,
      deferRender: true,
      paging: true,
      searching: false,
      info: true,
      stripeClasses: false,
      pageLength: 50,
      dom: "lfBrtip",
      sScrollX: "100%",
      scrollX: true,
      buttons: [
        {
          extend: "collection",
          text: "Export",
          buttons: [
            {
              extend: "copy",
              filename: "Revolutio",
              title: "",
              exportOptions: {},
            },
            {
              extend: "excel",
              filename: "Revolutio",
              title: "",
              exportOptions: {},
            },
            {
              extend: "csv",
              filename: "Revolutio",
              title: "",
              exportOptions: {},
            },
            {
              extend: "pdf",
              filename: "Revolutio",
              title: "",
              exportOptions: {},
            },
          ],
        },
      ],
      columnDefs: [
        {
          targets: "_all",
          className: "dt-center allColumnClass all",
        },
        {
          targets: 0,
          width: "20%",
          className: "noVis",
        },
      ],
    })
    .columns.adjust();
}

function filterExtractor(computationModelElementId) {
  var filterTable = $(`#filter-table_RunModel${computationModelElementId}`);
  var filterArray = new Array();
  filterTable.find("tr").each(function (i, el) {
    var config = {
      column_name: $(this).find("select").eq(0).attr("name"),
      condition: $(this).find("select").eq(0).val(),
    };
    if ($(this).find("input").attr("type") == "number") {
      config["input_value"] = Number($(this).find("input").val());
    } else {
      config["input_value"] = $(this).find("input").val();
    }
    filterArray.push(config);
  });
  return JSON.stringify(filterArray);
}

function initialiseServerSideDataTable(
  tableId,
  computeElementId,
  source,
  columnsArray,
  filterFormField,
  scrollY = "60vh",
  scrollX = 300,
  hideFirstColumn = true
) {
  var runModelTable = $(`#${tableId}`)
    .DataTable({
      autoWidth: true,
      scrollY: scrollY,
      scrollX: scrollX,
      scrollCollapse: true,
      sScrollXInner: "100%",
      ordering: false,
      serverSide: true,
      orderCellsTop: true,
      responsive: true,
      colReorder: {
        fixedColumnsLeft: 1,
      },
      deferRender: true,
      paging: true,
      stripeClasses: false,
      bLengthChange: false,
      pageLength: 50,
      dom: "lfBrtip",
      ajax: {
        url: source,
        type: "POST",
        data: function (d, settings) {
          d.filters = filterExtractor(computeElementId);
          return d;
        },
      },
      columns: columnsArray,
      buttons: [
        {
          extend: "collection",
          text: "Export",
          buttons: [
            {
              extend: "copy",
              filename: "Revolutio",
              title: "",
              exportOptions: {
                columns: ":visible",
              },
            },
            {
              extend: "excel",
              filename: "Revolutio",
              title: "",
              exportOptions: {
                columns: ":visible",
              },
            },
            {
              extend: "csv",
              filename: "Revolutio",
              title: "",
              exportOptions: {
                columns: ":visible",
              },
            },
            {
              extend: "pdfHtml5",
              title: "",
              customize: function (doc, config) {
                let tableNode;
                for (let i = 0; i < doc.content.length; ++i) {
                  if (String(doc.content[i].table) !== "undefined") {
                    tableNode = doc.content[i];
                    break;
                  }
                }

                const rowIndex = 0;
                const tableColumnCount = tableNode.table.body[rowIndex].length;

                if (tableColumnCount > 5) {
                  doc.pageOrientation = "landscape";
                }
                if (tableColumnCount <= 15) {
                  doc.pageSize = "A4";
                }

                if (tableColumnCount > 15 && tableColumnCount <= 25) {
                  doc.pageSize = "B3";
                }

                if (tableColumnCount > 25 && tableColumnCount <= 40) {
                  doc.pageSize = "A1";
                }

                if (tableColumnCount > 40) {
                  doc.pageSize = "A0";
                }
              },
            },
            {
              text: "XML",
              attr: {
                id: tableId,
              },
              exportOptions: { columns: ":visible:not(.noVis)" },
              action: function (e, dt, type, indexes) {
                node_data = dt.nodes()[0];
                table_data_id = $(node_data).attr("id");
                $("#" + table_data_id).tableExport({ type: "xml" });
              },
            },
          ],
        },
        {
          extend: "colvis",
          className: "scroller",
        },
      ],
      columnDefs: [
        {
          targets: "_all",
          className: "dt-center allColumnClass all",
        },
        {
          targets: 0,
          width: "20%",
          className: "noVis",
        },
      ],
      initComplete: function () {
        var freeze_e_id = $(this).closest("table").attr("id");

        var table1 = $(`#${freeze_e_id}`).DataTable();
        $(`#${freeze_e_id}`).on("click", "td", function () {
          cellColLen4 = table1.columns(":visible").nodes().length;
          cellIndex2 = table1.cell(this).index().column;

          $(this).click(function () {
            $(this).toggleClass("cell_highlighted");
            $(this).toggleClass("cell_selected");
          });
        });

        this.api()
          .columns()
          .every(function () {
            var column = this;
            var title = $(this).text();
            var select = $(
              `<input type="text" data-inputid='inputtext' value="" data-input_value="" style="text-align:center;border-bottom:none;border:1px solid #ced4da;border-radius:0.5em;height:2rem;max-width:130px;"placeholder="Search ` +
                title +
                `" />`
            )
              .appendTo($(column.footer()).empty())
              .on("change", function () {
                if (column.search() !== this.value || this.value == "") {
                  val = this.value;
                  if (this.value !== "") {
                    column.search(val).draw();
                  } else if (this.value == "") {
                    column.search(this.value).draw();
                  }
                }
              });
          });

        $(`#${tableId}`).DataTable().columns.adjust();
      },
    })
    .columns.adjust();
  if (hideFirstColumn) {
    runModelTable.column(0).visible(false);
  }
  $(`#${tableId}_length`).css("display", "inline-block");
  $(`#${tableId}_length`).css("float", "none");
  $(`#${tableId}_filter`).css("display", "none");
  $(`#${tableId}_wrapper .dataTables_scroll`).css("position", "relative");
  $(`#${tableId}_wrapper .dataTables_scrollHead`).css("margin-bottom", "3em");
  $(`#${tableId}_wrapper .dataTables_scrollFoot`).css("position", "absolute");
  $(`#${tableId}_wrapper .dataTables_scrollFoot`).css("top", "3.5em");

  runModelTable.buttons().container().css("display", "none");
  $(`#exData_comp_modal${computeElementId} .modal-footer`)
    .find(".buttons-excel")
    .off("click")
    .on("click", function () {
      $(`#${tableId}`).DataTable().button(".buttons-excel").trigger();
    });
  $(`#exData_comp_modal${computeElementId} .modal-footer`)
    .find(".buttons-pdf")
    .off("click")
    .on("click", function () {
      $(`#${tableId}`).DataTable().button(".buttons-pdf").trigger();
    });
  $(`#exData_comp_modal${computeElementId} .modal-footer`)
    .find(".buttons-xml")
    .off("click")
    .on("click", function () {
      $(`#${tableId}`).DataTable().button(".buttons-xml").trigger();
    });
  $(`#exData_comp_modal${computeElementId} .modal-footer`)
    .find(".buttons-copy")
    .off("click")
    .on("click", function () {
      $(`#${tableId}`).DataTable().button(".buttons-copy").trigger();
    });

  dataTableColumnsArray = runModelTable.settings().init().columns;
  $(`#columnVisibilityDropdown${computeElementId}`).empty();
  for (let p in dataTableColumnsArray) {
    $(`#columnVisibilityDropdown${computeElementId}`).append(
      `<div class="dropdown-item" data-column_index="${p}">${dataTableColumnsArray[p]["data"]}</div><div class="dropdown-divider" style="margin:0"></div>`
    );
  }
  $(`#columnVisibilityDropdown${computeElementId}`)
    .find(".dropdown-item")
    .each(function () {
      $(this)
        .off("click")
        .on("click", function (e) {
          e.stopPropagation();
          $(this).toggleClass("hide");
          if ($(this).hasClass("hide")) {
            runModelTable
              .column(parseInt($(this).attr("data-column_index")))
              .visible(false);
          } else {
            runModelTable
              .column(parseInt($(this).attr("data-column_index")))
              .visible(true);
          }
        });
    });

  $(`#showEntries${computeElementId}`)
    .off("select2:select")
    .on("select2:select", function () {
      runModelTable.page.len(parseInt($(this).val())).draw();
    });

  $(`#filter_button_run_computation${computeElementId}`)
    .off("click")
    .on("click", function () {
      $(`#filterRunCard_computation${computeElementId}`).css(
        "display",
        "block"
      );
    });

  var filterHTMLS = filterFormField;
  $(`.filter_btnRunModel${computeElementId}`).click(function () {
    var name = $(this).attr("name");
    var conditionHTML = filterHTMLS[name];
    $(`#filter-table_RunModel${computeElementId}`).append(conditionHTML);
    $(`#filter-table_RunModel${computeElementId}`)
      .find("tr")
      .eq(-1)
      .find("td")
      .eq(3)
      .remove();
    $(`#filter-table_RunModel${computeElementId}`)
      .find("tr")
      .eq(-1)
      .find("td")
      .eq(4)
      .remove();
    $(`#filter-table_RunModel${computeElementId}:last-child`)
      .find("select")
      .each(function () {
        parent = $(this).parent();
        $(this).select2({ dropdownParent: parent });
      });
  });

  $(`#btnSearchRun${computeElementId}`)
    .off("click")
    .on("click", function () {
      $(`#${tableId}`).DataTable().draw();
    });

  $(`#close_filterRuncard${computeElementId}`).click(function () {
    $(`#filterRunCard_computation${computeElementId}`).css("display", "none");
    $(`#filter-table_RunModel${computeElementId}`).empty();
    $(`#${tableId}`).DataTable().draw();
  });
}

function displayOutputAB(data, computeElementId, tree = true) {
  $(`#actual_grid${computeElementId}_wrapper`).remove();
  $(`#actual_grid${computeElementId}`).remove();
  $(`#table_confusionMatrixDecTree${computeElementId}_wrapper`).remove();
  $(`#table_confusionMatrixDecTree${computeElementId}`).remove();
  $(`#table_classReportDecTree${computeElementId}_wrapper`).remove();
  $(`#table_classReportDecTree${computeElementId}`).remove();
  $(`#tableParameters${computeElementId}_wrapper`).remove();
  $(`#tableParameters${computeElementId}`).remove();
  const roc_curveHTML = `
        <img
        src="data:image/png;base64,${data.roc_curve}"
        width="95%"
        height="100%"
        alt="ROC Curve"
        style="border:2px solid black;margin:auto;"
        title="ROC Curve"
        />
    `;
  const fit_curveHTML = `
        <img
        src="data:image/png;base64,${data.actplot}"
        width="100%"
        height="100%"
        alt="Actual vs fitted curve"
        style="border:2px solid black;margin:auto;"
        title="Actual vs fitted curve"
        />
    `;
  const fit_curve_table = `
        <table id = 'actual_grid${computeElementId}' class="table table-bordered" style="width:100%;">
            <thead>
            <tr>
                <th scope="col">Actual value</th>
                <th scope="col">Predicted value</th>
            </tr>
            </thead>
            <tbody>
            </tbody>
        </table>
    `;
  const plot_curveHTML = `
        <div class="card-body" style="padding:0.rem;">
            <div class="row">
                <img
                src="data:image/png;base64,${data.plot_tree}"
                width="90%"
                height="70%"
                alt="Plot Curve"
                style="border:4px solid black;margin:auto;"
                title="Tree"
                />
            </div>
        </div>
    `;
  const outputHTML = {
    accuracy: [data.accuracy, "Accuracy"],
    r_square: [data.r_square, "Coefficient of determination"],
    mean_sq_error: [data.mean_sq_error, "Mean squared error"],
    mean_abs_error: [data.mean_abs_error, "Mean absolute error"],
    precision: [data.precision, "Precision"],
    cross_val: [data.cross_val, "Cross validation"],
    recall: [data.recall, "Recall"],
    f1_metric: [data.f1_metric, "F1 metric"],
    conf_matrix: [
      `<table id='table_confusionMatrixDecTree${computeElementId}' class='table table-bordered' style="width:100%; margin-bottom:5px;">
            <thead>
                <tr>
                </tr>
            </thead>
            <tbody>

            </tbody>
            </table>`,
      "Confusion matrix",
    ],
    report: [
      `<table id='table_classReportDecTree${computeElementId}' class='table table-bordered' style="width:100%;margin-bottom:5px;">
            <thead>
                <tr>
                </tr>
            </thead>
            <tbody>

            </tbody>
            </table>`,
      "Classification report",
    ],
  };
  $(`#viewDT${computeElementId}`).append(
    `<div class="row" id='DecTreeResults${computeElementId}'></div>`
  );
  if ("dec_reg_summary" in data) {
    $(`#DecTreeResults${computeElementId}`).append(
      `
            <div class="card col-7" style="width:100%;">
                <div class="card-header" style="padding:0px">
                    <h4 class="mb-3" style="text-align:center;">
                        Decision Tree Summary
                    </h4>
                </div>
                <div class="card-body" style="padding:0.5rem;">
                    ${data.dec_reg_summary}
                </div>
            </div>
            `
    );
    $(".simpletable").each(function () {
      $(this).attr("class", "table table-bordered table-sm");
      $(this)
        .find("th")
        .each(function () {
          $(this).css("text-align", "center");
        });
      $(this)
        .find("td")
        .each(function () {
          $(this).css("text-align", "center");
        });
    });
  }
  var title;
  if (tree) {
    title = "Plot";
  } else {
    title = "Decision Surface";
  }
  $(`#DecTreeResults${computeElementId}`).append(`
    <div class="row1" id='rightContainerDT${computeElementId}' style="width:99%;margin:auto">
        <div class="row card">
            <div class="card-header" style="padding-bottom:0px; background:whitesmoke;">
                <h5 class="mb-3" style="text-align:center;background:whitesmoke;">
                    ${title}
                </h5>
            </div>
            <div class="col-12" id='plotContainerDecTree${computeElementId}' style="display: none;">

            </div>
        </div>
        <div class="row card">
            <div class="card-header" style=" padding-bottom:0px; background:whitesmoke;">
                <h5 class="mb-3" style="text-align:center;">
                    Model summary
                </h5>
            </div>
            <div class="card-body row">
                <div class="col-6" id='plotContainerDecTree2${computeElementId}' style="display: none; margin-bottom:10px; height:46vh;">

                </div>
                <div class="col-6" id='plotContainerDecTree3${computeElementId}' style="display: none; margin-bottom:10px; height:46vh;">

                </div>
                <div class="col-6" id='plotContainerDecTree4${computeElementId}' style="display: none; margin-bottom:10px;">

                </div>
                <div class="col-6" id='scoreSpaceDecTree${computeElementId}' style="display: none; margin-left: 0%; flex-wrap:wrap">
                    <p style="font-weight:bold; margin-top:20px">Scores:</p>
                    <table id='tableParameters${computeElementId}' class='table table-bordered' style="width:100%;margin-bottom:20px;">
                        <thead>
                            <tr></tr>
                        </thead>
                        <tbody>
                            <tr></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    `);
  let htmlHead, htmlBody;
  for (const key in data) {
    if (data.hasOwnProperty(key)) {
      if (key === "plot_tree") {
        $(`#plotContainerDecTree${computeElementId}`).css("display", "block");
        let htmlString = plot_curveHTML;
        $(`#plotContainerDecTree${computeElementId}`).append(htmlString);
      } else if (key === "roc_curve") {
        $(`#plotContainerDecTree2${computeElementId}`).css("display", "flex");
        let htmlString = roc_curveHTML;
        $(`#plotContainerDecTree2${computeElementId}`).append(htmlString);
      } else if (key === "actplot") {
        $(`#plotContainerDecTree3${computeElementId}`).css("display", "flex");
        let htmlString = fit_curveHTML;
        $(`#plotContainerDecTree3${computeElementId}`).append(htmlString);
        $(`#plotContainerDecTree4${computeElementId}`).css("display", "block");
        $(`#plotContainerDecTree4${computeElementId}`).append(fit_curve_table);
      } else if (key in outputHTML) {
        $(`#scoreSpaceDecTree${computeElementId}`).css("display", "block");
        let htmlString = outputHTML[key];
        if (key === "report") {
          $(`#scoreSpaceDecTree${computeElementId}`).prepend(htmlString[0]);
          $(`#scoreSpaceDecTree${computeElementId}`).prepend(
            `<p style="font-weight:bold;">${htmlString[1]}:</p>`
          );
          $(`#table_classReportDecTree${computeElementId} tbody`).empty();
          $(`#table_classReportDecTree${computeElementId} thead tr`).empty();
          for (let [key, value] of Object.entries(data.report[0])) {
            $(`#table_classReportDecTree${computeElementId}`)
              .find("thead tr")
              .eq(0)
              .append(`<th style="text-align:center;">${key}</th>`);
          }
          for (var i = 0; i < data.report.length; i++) {
            string = `<tr>`;
            for (let [key, value] of Object.entries(data.report[i])) {
              string += `<td style="text-align:center;">${value}</td>`;
            }
            string += `</tr>`;
            $(`#table_classReportDecTree${computeElementId}`)
              .find("tbody")
              .append(string);
          }
        } else if (key === "conf_matrix") {
          $(`#scoreSpaceDecTree${computeElementId}`).prepend(htmlString[0]);
          $(`#scoreSpaceDecTree${computeElementId}`).prepend(
            `<p style="font-weight:bold;">${htmlString[1]}:</p>`
          );
          $(`#table_confusionMatrixDecTree${computeElementId} tbody`).empty();
          $(
            `#table_confusionMatrixDecTree${computeElementId} thead tr`
          ).empty();
          for (let [key, value] of Object.entries(data.conf_matrix[0])) {
            $(`#table_confusionMatrixDecTree${computeElementId}`)
              .find("thead tr")
              .eq(0)
              .append(`<th style="text-align:center;">${key}</th>`);
          }
          for (var i = 0; i < data.conf_matrix.length; i++) {
            string = `<tr>`;
            for (let [key, value] of Object.entries(data.conf_matrix[i])) {
              string += `<td style="text-align:center;">${value}</td>`;
            }
            string += `</tr>`;
            $(`#table_confusionMatrixDecTree${computeElementId}`)
              .find("tbody")
              .append(string);
          }
        } else {
          htmlHead = `<th>` + outputHTML[key][1] + `</th>`;
          htmlBody = `<td>` + outputHTML[key][0] + `</td>`;
          $(`#scoreSpaceDecTree${computeElementId}`)
            .find(`#tableParameters${computeElementId}`)
            .find("thead")
            .find("tr")
            .append(htmlHead);
          $(`#scoreSpaceDecTree${computeElementId}`)
            .find(`#tableParameters${computeElementId}`)
            .find("tbody")
            .find("tr")
            .append(htmlBody);
        }
      }
    }
  }

  $(`#plotContainerDecTree${computeElementId}`)
    .closest(".card")
    .css("display", "none");

  if ("actual" in data) {
    for (var i = 0; i < data.actual.length; i++) {
      string = `<tr>`;
      string += `<td>${data.actual[i]}</td>`;
      string += `<td>${data.predict[i]}</td>`;
      string += `</tr>`;
      $(`#actual_grid${computeElementId}`).find("tbody").append(string);
    }
  }
  initialiseDataTable(`actual_grid${computeElementId}`, (scroll_y = "25vh"));
  initialiseDataTable(`table_confusionMatrixDecTree${computeElementId}`);
  initialiseDataTable(`table_classReportDecTree${computeElementId}`);
  initialiseDataTable(`tableParameters${computeElementId}`);
  $(".dt-buttons").css("margin-left", "3px");
}

function displayOutputDecTree(data, computeElementId) {
  $(`#actual_grid${computeElementId}_wrapper`).remove();
  $(`#actual_grid${computeElementId}`).remove();
  $(`#table_confusionMatrixDecTree${computeElementId}_wrapper`).remove();
  $(`#table_confusionMatrixDecTree${computeElementId}`).remove();
  $(`#table_classReportDecTree${computeElementId}_wrapper`).remove();
  $(`#table_classReportDecTree${computeElementId}`).remove();
  $(`#tableParameters${computeElementId}_wrapper`).remove();
  $(`#tableParameters${computeElementId}`).remove();
  const roc_curveHTML = `
        <img
        src="data:image/png;base64,${data.roc_curve}"
        width="100%"
        height="100%"
        alt="ROC Curve"
        style="border:2px solid black;margin:auto;"
        title="ROC Curve"
        />
    `;
  const fit_curveHTML = `
    <img
    src="data:image/png;base64,${data.actplot}"
    width="100%"
    height="100%"
    alt="Actual vs fitted curve"
    style="border:2px solid black;margin:auto;"
    title="Actual vs fitted curve"
    />
    `;
  const fit_curve_table = `
    <table id = "actual_grid${computeElementId}" class="table table-bordered" style="width:100%;">
        <thead>
            <tr>
            <th scope="col">Actual value</th>
            <th scope="col">Predicted value</th>
            </tr>
        </thead>
        <tbody>
        </tbody>
    </table>
    `;
  const plot_curveHTML = `
    <div class="card-body" style="padding:0.rem;">
        <div class="row">
            <img
            src="data:image/png;base64,${data.plot_tree}"
            width="90%"
            height="70%"
            alt="Tree"
            style="border:4px solid black;margin:auto;"
            title="Tree"
            />
        </div>
    </div>
    `;
  const outputHTML = {
    accuracy: [data.accuracy, "Accuracy"],
    r_square: [data.r_square, "Coefficient of determination"],
    mean_sq_error: [data.mean_sq_error, "Mean square error"],
    mean_abs_error: [data.mean_abs_error, "Mean absolute error"],
    precision: [data.precision, "Precision"],
    cross_val: [data.cross_val, "Cross validation"],
    recall: [data.recall, "Recall"],
    f1_metric: [data.f1_metric, "F1 metric"],
    conf_matrix: [
      `<table id='table_confusionMatrixDecTree${computeElementId}' class='table table-bordered' style="width:100%; margin-bottom:5px;">
            <thead>
            <tr>

            </tr>
            </thead>
            <tbody>

            </tbody>
            </table>`,
      "Confusion matrix",
    ],
    report: [
      ` <table id='table_classReportDecTree${computeElementId}' class='table table-bordered' style="width:100%;margin-bottom:5px;">
            <thead>
            <tr>

            </tr>
            </thead>
            <tbody>

            </tbody>
            </table>`,
      "Classification report",
    ],
  };
  $(`#viewDT${computeElementId}`).append(
    `<div class="row" id='DecTreeResults${computeElementId}'></div>`
  );
  if ("dec_reg_summary" in data) {
    $(`#DecTreeResults${computeElementId}`).append(
      `
            <div class="card col-7" style="width:100%;">
                <div class="card-header" style="padding:0px">
                    <h4 class="mb-3" style="text-align:center;">
                    Decision Tree Summary
                    </h4>
                </div>
                <div class="card-body" style="padding:0.5rem;">
                ${data.dec_reg_summary}
                </div>
            </div>
            `
    );
    $(".simpletable").each(function () {
      $(this).attr("class", "table table-bordered table-sm");
      $(this)
        .find("th")
        .each(function () {
          $(this).css("text-align", "center");
        });
      $(this)
        .find("td")
        .each(function () {
          $(this).css("text-align", "center");
        });
    });
  }

  $(`#DecTreeResults${computeElementId}`).append(`
    <div class="row1" id='rightContainerDT${computeElementId}' style="width:99%;margin:auto">
        <div class="row card">
            <div class="card-header" style="padding-bottom:0px; background:whitesmoke;">
                <h5 class="mb-3" style="text-align:center;background:whitesmoke;">
                Plot
                </h5>
            </div>
            <div class="col-12" id='plotContainerDecTree${computeElementId}' style="display: none;">

            </div>
        </div>
        <div class="row card">
            <div class="card-header" style=" padding-bottom:0px; background:whitesmoke;">
                <h5 class="mb-3" style="text-align:center;">
                Model summary
                </h5>
            </div>
            <div class="card-body row">
                <div class="col-6" id='plotContainerDecTree2${computeElementId}' style="display: none; margin-bottom:10px; height:46vh;">

                </div>
                <div class="col-6" id='plotContainerDecTree3${computeElementId}' style="display: none; margin-bottom:10px; height:46vh;">

                </div>
                <div class="col-6" id='plotContainerDecTree4${computeElementId}' style="display: none; margin-bottom:10px;">

                </div>
                <div class="col-6" id='scoreSpaceDecTree${computeElementId}' style="display: none; margin-left: 0%; flex-wrap:wrap">
                <p style="font-weight:bold; margin-top:20px">Scores:</p>
                    <table id='tableParameters${computeElementId}' class='table table-bordered' style="width:100%;margin-bottom:20px;">
                        <thead>
                            <tr></tr>
                        </thead>
                        <tbody>
                            <tr></tr>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
    `);
  let htmlHead, htmlBody;
  for (const key in data) {
    if (data.hasOwnProperty(key)) {
      if (key === "plot_tree") {
        $(`#plotContainerDecTree${computeElementId}`).css("display", "block");
        let htmlString = plot_curveHTML;
        $(`#plotContainerDecTree${computeElementId}`).append(htmlString);
      } else if (key === "roc_curve") {
        $(`#plotContainerDecTree2${computeElementId}`).css("display", "flex");
        let htmlString = roc_curveHTML;
        $(`#plotContainerDecTree2${computeElementId}`).append(htmlString);
      } else if (key === "actplot") {
        $(`#plotContainerDecTree3${computeElementId}`).css("display", "flex");
        let htmlString = fit_curveHTML;
        $(`#plotContainerDecTree3${computeElementId}`).append(htmlString);
        $(`#plotContainerDecTree4${computeElementId}`).css("display", "block");
        $(`#plotContainerDecTree4${computeElementId}`).append(fit_curve_table);
      } else if (key in outputHTML) {
        $(`#scoreSpaceDecTree${computeElementId}`).css("display", "block");
        let htmlString = outputHTML[key];
        if (key === "report") {
          $(`#scoreSpaceDecTree${computeElementId}`).prepend(htmlString[0]);
          $(`#scoreSpaceDecTree${computeElementId}`).prepend(
            `<p style="font-weight:bold;">${htmlString[1]}:</p>`
          );
          $(`#table_classReportDecTree${computeElementId} tbody`).empty();
          $(`#table_classReportDecTree${computeElementId} thead tr`).empty();
          for (let [key, value] of Object.entries(data.report[0])) {
            $(`#table_classReportDecTree${computeElementId}`)
              .find("thead tr")
              .eq(0)
              .append(`<th style="text-align:center;">${key}</th>`);
          }
          for (var i = 0; i < data.report.length; i++) {
            string = `<tr>`;
            for (let [key, value] of Object.entries(data.report[i])) {
              string += `<td style="text-align:center;">${value}</td>`;
            }
            string += `</tr>`;
            $(`#table_classReportDecTree${computeElementId}`)
              .find("tbody")
              .append(string);
          }
        } else if (key === "conf_matrix") {
          $(`#scoreSpaceDecTree${computeElementId}`).prepend(htmlString[0]);
          $(`#scoreSpaceDecTree${computeElementId}`).prepend(
            `<p style="font-weight:bold;">${htmlString[1]}:</p>`
          );
          $(`#table_confusionMatrixDecTree${computeElementId} tbody`).empty();
          $(
            `#table_confusionMatrixDecTree${computeElementId} thead tr`
          ).empty();
          for (let [key, value] of Object.entries(data.conf_matrix[0])) {
            $(`#table_confusionMatrixDecTree${computeElementId}`)
              .find("thead tr")
              .eq(0)
              .append(`<th style="text-align:center;">${key}</th>`);
          }
          for (var i = 0; i < data.conf_matrix.length; i++) {
            string = `<tr>`;
            for (let [key, value] of Object.entries(data.conf_matrix[i])) {
              string += `<td style="text-align:center;">${value}</td>`;
            }
            string += `</tr>`;
            $(`#table_confusionMatrixDecTree${computeElementId}`)
              .find("tbody")
              .append(string);
          }
        } else {
          htmlHead = `<th>` + outputHTML[key][1] + `</th>`;
          htmlBody = `<td>` + outputHTML[key][0] + `</td>`;
          $(`#scoreSpaceDecTree${computeElementId}`)
            .find(`#tableParameters${computeElementId}`)
            .find("thead")
            .find("tr")
            .append(htmlHead);
          $(`#scoreSpaceDecTree${computeElementId}`)
            .find(`#tableParameters${computeElementId}`)
            .find("tbody")
            .find("tr")
            .append(htmlBody);
        }
      }
    }
  }

  if ("actual" in data) {
    for (var i = 0; i < data.actual.length; i++) {
      string = `<tr>`;
      string += `<td>${data.actual[i]}</td>`;
      string += `<td>${data.predict[i]}</td>`;
      string += `</tr>`;
      $(`#actual_grid${computeElementId}`).find("tbody").append(string);
    }
  }
  initialiseDataTable(`actual_grid${computeElementId}`, (scroll_y = "25vh"));
  initialiseDataTable(`table_confusionMatrixDecTree${computeElementId}`);
  initialiseDataTable(`table_classReportDecTree${computeElementId}`);
  initialiseDataTable(`tableParameters${computeElementId}`);
}

function displayOutputLinReg(data, container, computeElementId, run = 0) {
  if (run === 0) {
    var parameterEstTableId = `table_parameterEstLinReg_${computeElementId}`;
    var linRegResultsContainerId = `linRegResults_${computeElementId}`;
    var summayContainerLinRegID = `summayContainerLinReg_${computeElementId}`;
    var plotContainerLinRegId = `plotContainerLinReg_${computeElementId}`;
    var scoreContainerLinRegId = `scoreContainerLinReg_${computeElementId}`;
    var scoreSpaceLinRegId = `scoreSpaceLinReg_${computeElementId}`;
    var table_ActualVFittedId = `table_ActualVFittedLinReg_${computeElementId}`;
  } else {
    var parameterEstTableId = `table_parameterEstLinReg_${run}_${computeElementId}`;
    var linRegResultsContainerId = `linRegResults_${run}_${computeElementId}`;
    var summayContainerLinRegID = `summayContainerLinReg_${run}_${computeElementId}`;
    var plotContainerLinRegId = `plotContainerLinReg_${run}_${computeElementId}`;
    var scoreContainerLinRegId = `scoreContainerLinReg_${run}_${computeElementId}`;
    var scoreSpaceLinRegId = `scoreSpaceLinReg_${run}_${computeElementId}`;
    var table_ActualVFittedId = `table_ActualVFittedLinReg_${run}_${computeElementId}`;
  }
  const actual_vs_fitted_plot_HTML = `
        <div class="card">
            <div class="card-header" style="padding:0.3rem">
                <h5 class="mb-0" style="text-align:center;">
                    Actual v/s Fitted Plot
                </h5>
            </div>
            <div class="card-body" style="padding:0.3rem;height:50vh;">
                <div class="row" style="height:50vh;">
                    <img
                    src="data:image/png;base64,${data.actual_vs_fitted_plot}"
                    alt="Actual v/s Fitted Plot"
                    style="border:2px solid black;margin:auto;height:95%;width:95%;"
                    title="Actual v/s Fitted Plot"
                    />
                </div>
            </div>
        </div>
    `;
  const qq_plotHTML = `
        <div class="card">
            <div class="card-header" style="padding:0.3rem">
                <h5 class="mb-0" style="text-align:center;">
                    Quantile Plot
                </h5>
            </div>
            <div class="card-body" style="padding:0.3rem;height:50vh;">
                <div class="row" style="height:50vh;">
                    <img
                    src="data:image/png;base64,${data.quantile_plot}"
                    width="95%"
                    height="95%"
                    alt="Quantile Plot"
                    style="border:2px solid black;margin:auto;"
                    title="Quantile Plot"
                    />
                </div>
            </div>
        </div>
    `;
  const outputHTML = {
    mean_abs_error: `
            <div>
                <h5 class="d-inline">Mean Absolute Error : </h5> &nbsp;${data.mean_abs_error}
            </div><br>
        `,
    intercept_estimate: `
            <div>
                <h5 class="d-inline">Intercept Estimate : </h5> &nbsp;${data.intercept_estimate}
            </div><br>
        `,
    mean_sq_error: `
            <div>
                <h5 class="d-inline">Mean Squared Error : </h5> &nbsp;${data.mean_sq_error}
            </div><br>
        `,
    coefficient_of_determination: `
            <div>
                <h5 class="d-inline">Coefficient of Determination : </h5> &nbsp;${data.coefficient_of_determination}
            </div><br>
        `,
    parameter_estimates: `
            <div>
                <hr style="margin:0.5%;">
                <h5 class="text-primary" style="text-align:center;">Paremeter Estimates</h5>
                <hr style="margin:0.5%;">
                <table id="${parameterEstTableId}">
                    <thead>
                        <tr>

                        </tr>
                    </thead>
                    <tbody>

                    </tbody>
                </table>
            </div><br>
        `,
  };

  $(`#${container}`).append(
    `
        <div class="row" id="${linRegResultsContainerId}">

        </div>
    `
  );

  if ("linear_reg_summary" in data) {
    $(`#${linRegResultsContainerId}`).append(
      `
            <div class="col-7" id='${summayContainerLinRegID}'>
                <div class="card" style="width:100%;">
                    <div class="card-header" style="padding:0.3rem">
                        <h5 class="mb-0" style="text-align:center;">
                            Linear Regression Summary
                        </h5>
                    </div>
                    <div class="card-body" style="padding:0.5rem;">
                        ${data.linear_reg_summary}
                    </div>
                </div>
            </div>
        `
    );
    $(".simpletable").each(function () {
      $(this).attr("class", "table table-bordered table-sm");
      $(this)
        .find("th")
        .each(function () {
          $(this).css("text-align", "center");
        });
      $(this)
        .find("td")
        .each(function () {
          $(this).css("text-align", "center");
        });
    });
  }

  $(`#${linRegResultsContainerId}`).append(`
        <div class="col-5">
            <div class="row" id="${plotContainerLinRegId}" style="display: none;">
            </div>
            <div class="row" id="${scoreContainerLinRegId}" style="display: none;">
                <div class="card">
                    <div class="card-header" style="padding:0.3rem">
                        <h5 class="mb-0" style="text-align:center;">
                            Scores
                        </h5>
                    </div>
                    <div class="card-body" id="${scoreSpaceLinRegId}">
                    </div>
                </div>
            </div>
        </div>
    `);
  for (const key in data) {
    if (data.hasOwnProperty(key)) {
      if (key === "actual_vs_fitted_plot") {
        $(`#${plotContainerLinRegId}`).css("display", "block");
        let htmlString = actual_vs_fitted_plot_HTML;
        $(`#${plotContainerLinRegId}`).append(htmlString);
      } else if (key === "quantile_plot") {
        $(`#${plotContainerLinRegId}`).css("display", "block");
        let htmlString = qq_plotHTML;
        $(`#${plotContainerLinRegId}`).append(htmlString);
      } else if (key in outputHTML) {
        $(`#${scoreContainerLinRegId}`).css("display", "block");
        let htmlString = outputHTML[key];
        $(`#${scoreSpaceLinRegId}`).append(htmlString);
        if (key === "parameter_estimates") {
          $(`#${parameterEstTableId} tbody`).empty();
          $(`#${parameterEstTableId} thead tr`).empty();
          for (let [key, value] of Object.entries(
            data.parameter_estimates[0]
          )) {
            $(`#${parameterEstTableId}`)
              .find("thead tr")
              .eq(0)
              .append(`<th>${key}</th>`);
          }
          for (var i = 0; i < data.parameter_estimates.length; i++) {
            string = `<tr>`;
            for (let [key, value] of Object.entries(
              data.parameter_estimates[i]
            )) {
              string += `<td>${value}</td>`;
            }
            string += `</tr>`;
            $(`#${parameterEstTableId}`).find("tbody").append(string);
          }
        }
      }
    }
  }
  if ("actual_vs_fitted_data" in data) {
    $(`#${summayContainerLinRegID}`).append(`
            <div class="card">
                <div class="card-header" style="padding:0.3rem">
                    <h5 class="mb-0" style="text-align:center;">
                        Actual v/s Fitted
                    </h5>
                </div>
                <div class="card-body" style="padding:0.5rem;">
                    <table id="${table_ActualVFittedId}">
                        <thead>
                            <tr>

                            </tr>
                        </thead>
                        <tbody>

                        </tbody>
                    </table>
                </div>
            </div>
        `);
    $(`#${table_ActualVFittedId} tbody`).empty();
    $(`#${table_ActualVFittedId} thead tr`).empty();
    for (let [key, value] of Object.entries(data.actual_vs_fitted_data[0])) {
      $(`#${table_ActualVFittedId}`)
        .find("thead tr")
        .eq(0)
        .append(`<th>${key}</th>`);
    }
    for (var i = 0; i < data.actual_vs_fitted_data.length; i++) {
      string = `<tr>`;
      for (let [key, value] of Object.entries(data.actual_vs_fitted_data[i])) {
        string += `<td>${value}</td>`;
      }
      string += `</tr>`;
      $(`#${table_ActualVFittedId}`).find("tbody").append(string);
    }
  }
}

function displayOutputLogReg(data, container, computeElementId, run = 0) {
  if (run === 0) {
    var confusionMatrixTableId = `table_confusionMatrixLogReg_${computeElementId}`;
    var logRegResultsContainerId = `logRegResults_${computeElementId}`;
    var table_classReportLogRegId = `table_classReportLogReg_${computeElementId}`;
    var plotContainerLogRegId = `plotContainerLogReg_${computeElementId}`;
    var scoreContainerLogRegId = `scoreContainerLogReg_${computeElementId}`;
    var scoreSpaceLogRegId = `scoreSpaceLogReg_${computeElementId}`;
  } else {
    var confusionMatrixTableId = `table_confusionMatrixLogReg_${run}_${computeElementId}`;
    var logRegResultsContainerId = `logRegResults_${run}_${computeElementId}`;
    var table_classReportLogRegId = `table_classReportLogReg_${run}_${computeElementId}`;
    var plotContainerLogRegId = `plotContainerLogReg_${run}_${computeElementId}`;
    var scoreContainerLogRegId = `scoreContainerLogReg_${run}_${computeElementId}`;
    var scoreSpaceLogRegId = `scoreSpaceLogReg_${run}_${computeElementId}`;
  }
  const roc_curveHTML = `
        <div class="card">
            <div class="card-header" style="padding:0.3rem">
                <h5 class="mb-0" style="text-align:center;">
                    ROC Curve
                </h5>
            </div>
            <div class="card-body" style="padding:0.3rem;height:50vh;">
                <div class="row" style="height:50vh;">
                    <img
                    src="data:image/png;base64,${data.roc_curve}"
                    width="95%"
                    height="95%"
                    alt="ROC Curve"
                    style="border:2px solid black;margin:auto;"
                    title="ROC Curve"
                    />
                </div>
            </div>
        </div>
    `;
  const outputHTML = {
    accuracy: `
            <div>
                <h5 style="display:inline"> Accuracy : </h5> &nbsp;${data.accuracy}
            </div><br>
        `,
    precision: `
            <div>
                <h5 style="display:inline"> Precision : </h5> &nbsp;${data.precision}
            </div><br>
        `,
    recall: `
            <div>
                <h5 style="display:inline"> Recall : </h5> &nbsp;${data.recall}
            </div><br>
        `,
    f1_metric: `
            <div>
                <h5 style="display:inline"> F1 Score : </h5> &nbsp;${data.f1_metric}
            </div><br>
        `,
    conf_matrix: `
            <div>
                <hr style="margin:0.5%;">
                <h5 class="text-primary" style="text-align:center;">Confusion Matrix</h5>
                <hr style="margin:0.5%;">
                <table id="${confusionMatrixTableId}">
                    <thead>
                        <tr>

                        </tr>
                    </thead>
                    <tbody>

                    </tbody>
                </table>
            </div><br>
        `,
    report: `
            <div>
                <hr style="margin:0.5%;">
                <h5 class="text-primary" style="text-align:center;">Classification Report</h5>
                <hr style="margin:0.5%;">
                <table id="${table_classReportLogRegId}">
                    <thead>
                        <tr>

                        </tr>
                    </thead>
                    <tbody>

                    </tbody>
                </table>
            </div><br>
        `,
  };
  $(`#${container}`).append(
    `
        <div class="row" id="${logRegResultsContainerId}">

        </div>
    `
  );
  if ("logit_reg_summary" in data) {
    $(`#${logRegResultsContainerId}`).append(
      `
              <div class="card col-7" style="width:100%;">
                  <div class="card-header" style="padding:0.3rem">
                      <h5 class="mb-0" style="text-align:center;">
                          Logistic Regression Summary
                      </h5>
                  </div>
                  <div class="card-body" style="padding:0.5rem;">
                      ${data.logit_reg_summary}
                  </div>
              </div>
          `
    );
    $(".simpletable").each(function () {
      $(this).attr("class", "table table-bordered table-sm");
      $(this)
        .find("th")
        .each(function () {
          $(this).css("text-align", "center");
        });
      $(this)
        .find("td")
        .each(function () {
          $(this).css("text-align", "center");
        });
    });
  }

  $(`#${logRegResultsContainerId}`).append(`
          <div class="col-5">
              <div class="row" id="${plotContainerLogRegId}" style="display: none;">
              </div>
              <div class="row" id="${scoreContainerLogRegId}" style="display: none;">
                  <div class="card">
                      <div class="card-header" style="padding:0.3rem">
                          <h5 class="mb-0" style="text-align:center;">
                              Scores
                          </h5>
                      </div>
                      <div class="card-body" id="${scoreSpaceLogRegId}">
                      </div>
                  </div>
              </div>
          </div>
      `);
  for (const key in data) {
    if (data.hasOwnProperty(key)) {
      if (key === "roc_curve") {
        $(`#${plotContainerLogRegId}`).css("display", "block");
        let htmlString = roc_curveHTML;
        $(`#${plotContainerLogRegId}`).append(htmlString);
      } else if (key in outputHTML) {
        $(`#${scoreContainerLogRegId}`).css("display", "block");
        let htmlString = outputHTML[key];
        $(`#${scoreSpaceLogRegId}`).append(htmlString);
        if (key === "report") {
          $(`#${table_classReportLogRegId} tbody`).empty();
          $(`#${table_classReportLogRegId} thead tr`).empty();
          for (let [key, value] of Object.entries(data.report[0])) {
            $(`#${table_classReportLogRegId}`)
              .find("thead tr")
              .eq(0)
              .append(`<th>${key}</th>`);
          }
          for (var i = 0; i < data.report.length; i++) {
            string = `<tr>`;
            for (let [key, value] of Object.entries(data.report[i])) {
              string += `<td>${value}</td>`;
            }
            string += `</tr>`;
            $(`#${table_classReportLogRegId}`).find("tbody").append(string);
          }
        } else if (key === "conf_matrix") {
          $(`#${confusionMatrixTableId} tbody`).empty();
          $(`#${confusionMatrixTableId} thead tr`).empty();
          for (let [key, value] of Object.entries(data.conf_matrix[0])) {
            $(`#${confusionMatrixTableId}`)
              .find("thead tr")
              .eq(0)
              .append(`<th>${key}</th>`);
          }
          for (var i = 0; i < data.conf_matrix.length; i++) {
            string = `<tr>`;
            for (let [key, value] of Object.entries(data.conf_matrix[i])) {
              string += `<td>${value}</td>`;
            }
            string += `</tr>`;
            $(`#${confusionMatrixTableId}`).find("tbody").append(string);
          }
        }
      }
    }
  }
}

function analyseTSData(data, container) {
  $(`#${container}`).append(
    `<div class="card">
        <div class="card-header" style="padding:0.3rem;background:whitesmoke;">
            <h5 class="mb-0" style="text-align:center;">
                ACF and PACF
            </h5>
        </div>
        <div class="card-body">
            <div class = "row">
                <div class = "col-6">
                    <img
                    src="data:image/png;base64,${data.acf_plot}"
                    height="100%"
                    width="100%"
                    alt="ACF Plot"
                    style="border:2px solid black;"
                    title="ACF Plot"
                    />
                </div>
                <div class = "col-6">
                    <img
                    src="data:image/png;base64,${data.pacf_plot}"
                    height="100%"
                    width="100%"
                    alt="PACF Plot"
                    style="border:2px solid black;"
                    title="PACF Plot"
                    />
                </div>
            </div>
        </div>
    </div>
    <div class="card">
        <div class="card-header" style="padding:0.3rem;background:whitesmoke;">
            <h5 class="mb-0" style="text-align:center;">
                Augmented Dickey Fuller Test For Stationarity
            </h5>
        </div>
        <div class="card-body">
            <div class = "row" style="background:whitesmoke;">
                <div class="col-2"></div>
                <div class = "col-5">
                        <span style="font-weight:bold;"> H0 : </span> The time series has a unit root and is not stationary.
                </div>
                <div class = "col-5">
                    <span style="font-weight:bold;"> H1 :  </span> The time series is stationary.
                </div>
            </div>
            <br>
            <div class = "row" style="margin-left:43%;">
                <span style="font-weight:bold;"> P-value : </span> &nbsp;${data.p_value}
            </div><br>
            <div class = "row" style="margin-left:41%;">
                <span style="font-weight:bold;"> Conclusion : </span>&nbsp;${data.test_result}
            </div>
        </div>
    </div>
    `
  );
}

function trainARIMARun(data, container, computeElementId, run = 0) {
  if (run === 0) {
    var actual_vs_predicted_table_id = `exampledataResults_${computeElementId}`;
  } else {
    var actual_vs_predicted_table_id = `exampledataResults_${run}_${computeElementId}`;
  }
  $(`#${container}`).append(
    `<div class="row">
            <div class="col-6">
                <div class="card">
                    ${data.summary}
                </div>
                <div class="card">
                    <div class="card-header" style="padding:0.3rem;background:whitesmoke;">
                        <h5 class="mb-0" style="text-align:center;">
                        Actual vs Predicted - Table
                        </h5>
                    </div>
                    <div class="card-body" style="padding:0.9rem;">
                        <table id="${actual_vs_predicted_table_id}" class="display compact" style="width:100%;">
                            <thead>
                                <tr></tr>
                            </thead>
                            <tbody>
                            </tbody>
                        </table>
                    </div>
                </div>
                <div class="card">
                    <div class="card-header" style="padding:0.3rem;background:whitesmoke">
                        <h5 class="mb-0" style="text-align:center;">
                            Augmented Dickey Fuller Test For Stationarity
                        </h5>
                    </div>
                    <div class="card-body">
                        <div class = "row" style="background:whitesmoke;">
                            <div class = "col-6">
                                <span style="font-weight:bold;"> H0 : </span > The time series has a unit root and is not stationary.
                            </div>
                            <div class = "col-6">
                                <span style="font-weight:bold;"> H1 :  </span > The time series is stationary.
                            </div>
                        </div>
                        <br>
                        <div class = "row" style="margin-left:0.25%">
                            <span style="font-weight:bold;"> P-value : </span > &nbsp;${data.adf_p_value}
                        </div><br>
                        <div class = "row" style="margin-left:0.25%">
                            <span style="font-weight:bold;"> Conclusion : </span >&nbsp;${data.adf_test_result}
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-6">
                <div class="card">
                    <div class="card-header" style="padding:0.3rem;background:whitesmoke">
                        <h5 class="mb-0" style="text-align:center;">
                            Model Analysis
                        </h5>
                    </div>
                    <div class="card-body" style="padding:0.5rem;">
                        <div class = "row">
                            <img
                            src="data:image/png;base64,${data.residuals_plot}"
                            width="98%"
                            height="70%"
                            alt="Residuals Plot"
                            style="border:2px solid black;margin-left:0.3rem"
                            title="Residuals Plot"
                            />
                        </div>
                        <br>
                        <div class = "row">
                            <img
                            src="data:image/png;base64,${data.acf_result}"
                            width="98%"
                            height="70%"
                            alt="ACF of Residuals"
                            style="border:2px solid black;margin-left:0.3rem"
                            title="ACF of Residuals"
                            />
                        </div>
                        <br>
                        <div class="row">
                            <img
                                src="data:image/png;base64,${data.plot}"
                                width="98%"
                                height="70%"
                                alt="Actual vs Predicted"
                                style="border:2px solid black;margin-left:0.3rem"
                                title="Actual vs Predicted"
                            />
                        </div>
                        <br>
                        <div class="row">
                            <p style="margin-left:22.5%"><span style="font-weight:bold;">Mean Squared Error (MSE) </span > = ${data.mse}.</p>
                        </div>
                    </div>
                </div>
                <div class="card">
                    <div class="card-header" style="padding:0.3rem;background:whitesmoke">
                        <h5 class="mb-0" style="text-align:center;">
                            Jarque-Bera Test For Normality
                        </h5>
                    </div>
                    <div class="card-body">
                        <div class = "row" style="background:whitesmoke;">
                            <div class = "col-6">
                                <span style="font-weight:bold;"> H0 : </span > The time series is normally distributed.
                            </div>
                            <div class = "col-6">
                                <span style="font-weight:bold;"> H1 :  </span > The time series follows some other statistical distribution.
                            </div>
                        </div>
                        <br>
                        <br>
                        <div class = "row" >
                            <div class="col-6">
                                <span style="font-weight:bold;"> Mean of residuals : </span > &nbsp;${data.mean}
                            </div>
                            <div class="col-6">
                                <span style="font-weight:bold;"> SD of residuals : </span > &nbsp;${data.std}
                            </div>
                        </div>
                        <br>
                        <div class = "row"  >
                            <div class="col-12">
                                <span style="font-weight:bold;"> P-value : </span > &nbsp;${data.jb_p_value}
                            </div>
                        </div>
                        <br>
                        <div class = "row" >
                            <div class="col-12">
                                <span style="font-weight:bold;"> Conclusion : </span >&nbsp;${data.jb_test_result}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>`
  );
  $(".simpletable").each(function () {
    $(this).attr("class", "table table-bordered table-sm");
    $(this)
      .find("th")
      .each(function () {
        $(this).css("text-align", "center");
      });
    $(this)
      .find("td")
      .each(function () {
        $(this).css("text-align", "center");
      });
  });
  for (var i = 0; i < data.table[data.table_headers[0]].length; i++) {
    string = `<tr>`;
    for (j in data.table_headers) {
      string += `<td style="text-align:center;">${
        data.table[data.table_headers[j]][i]
      }</td>`;
    }
    string += `</tr>`;
    $(`#${actual_vs_predicted_table_id}`).find("tbody").append(string);
  }

  $(`#${actual_vs_predicted_table_id} thead tr`).empty();
  for (j in data.table_headers) {
    $(`#${actual_vs_predicted_table_id}`)
      .find("thead tr")
      .eq(0)
      .append(`<th style="text-align:center;">${data.table_headers[j]}</th>`);
  }
}

function trainGARCHModel(data, container, computeElementId, run = 0) {
  if (run === 0) {
    var actual_vs_predicted_table_id = `exampledataResults_${computeElementId}`;
  } else {
    var actual_vs_predicted_table_id = `exampledataResults_${run}_${computeElementId}`;
  }
  $(`#${container}`).append(
    `<div class="row">
          <div class="col-6">
              <div class="card">
                  ${data.summary}
              </div>
              <div class="card">
                  <div class="card-header" style="padding:0.3rem;background:whitesmoke;">
                      <h5 class="mb-0 timeSeriesHeaders" style="text-align:center;">
                      Actual vs Predicted - Table
                      </h5>
                  </div>
                  <div class="card-body" style="padding:0.9rem;">
                      <table id="${actual_vs_predicted_table_id}" class="display compact" style="width:100%;">
                          <thead>
                              <tr></tr>
                          </thead>
                          <tbody>
                          </tbody>
                      </table>
                  </div>
              </div>
              <div class="card">
                  <div class="card-header" style="padding:0.3rem;background:whitesmoke">
                      <h5 class="mb-0 timeSeriesHeaders" style="text-align:center;">
                          Augmented Dickey Fuller Test For Stationarity
                      </h5>
                  </div>
                  <div class="card-body">
                      <div class = "row" style="background:whitesmoke;">
                          <div class = "col-6">
                              <strong> H0 : </strong> The time series has a unit root and is not stationary.
                          </div>
                          <div class = "col-6">
                              <strong> H1 :  </strong> The time series is stationary.
                          </div>
                      </div>
                      <br>
                      <div class = "row" >
                          <strong> P-value : </strong> &nbsp;${data.adf_p_value}
                      </div><br>
                      <div class = "row" >
                          <strong> Conclusion : </strong>&nbsp;${data.adf_test_result}
                      </div>
                  </div>
              </div>
              <div class="card">
                  <div class="card-header" style="padding:0.3rem;background:whitesmoke">
                      <h5 class="mb-0 timeSeriesHeaders" style="text-align:center;">
                          Jarque-Bera Test For Normality
                      </h5>
                  </div>
                  <div class="card-body">
                      <div class = "row" style="background:whitesmoke;">
                          <div class = "col-6">
                              <strong> H0 : </strong> The time series is normally distributed.
                          </div>
                          <div class = "col-6">
                              <strong> H1 :  </strong> The time series follows some other statistical distribution.
                          </div>
                      </div>
                      <br>
                      <br>
                      <div class = "row" >
                          <div class="col-6">
                              <strong> Mean of residuals : </strong> &nbsp;${data.mean}
                          </div>
                          <div class="col-6">
                              <strong> SD of residuals : </strong> &nbsp;${data.std}
                          </div>
                      </div>
                      <br>
                      <div class = "row"  >
                          <div class="col-12">
                              <strong> P-value : </strong> &nbsp;${data.jb_p_value}
                          </div>
                      </div>
                      <br>
                      <div class = "row" >
                          <div class="col-12">
                              <strong> Conclusion : </strong>&nbsp;${data.jb_test_result}
                          </div>
                      </div>
                  </div>
              </div>
          </div>
          <div class="col-6">
              <div class="card">
                  <div class="card-header" style="padding:0.3rem;background:whitesmoke">
                      <h5 class="mb-0 timeSeriesHeaders" style="text-align:center;">
                          Model Analysis
                      </h5>
                  </div>
                  <div class="card-body" style="padding:0.5rem;">
                      <div class = "row">
                          <img
                              src="data:image/png;base64,${data.residuals_plot}"
                              width="98%"
                              height="70%"
                              alt="Standardised Residuals Plot"
                              style="border:2px solid black;margin-left:0.2rem"
                              title="Standardised Residuals Plot"
                              />
                      </div>
                      <br>
                      <div class = "row">
                          <img
                              src="data:image/png;base64,${data.acf_result}"
                              width="98%"
                              height="70%"
                              alt="ACF of Standardised Residuals"
                              style="border:2px solid black;margin-left:0.2rem"
                              title="ACF of Standardised Residuals"
                              />
                      </div>
                      <br>
                      <div class="row">
                          <img
                              src="data:image/png;base64,${data.plot}"
                              width="98%"
                              height="70%"
                              alt="Actual vs Predicted"
                              style="border:2px solid black;margin-left:0.3rem"
                              title="Actual vs Predicted"
                          />
                      </div>
                      <br>
                      <div class = "row">
                          <img
                              src="data:image/png;base64,${data.conditional_volatility_plot}"
                              alt="Condition Volatility"
                              width="100%"
                              height="96%"
                              style="border:2px solid black;"
                              title="Condition Volatility"
                              />
                      </div>
                      </div>
                  </div>
              </div>

          </div>
      </div>`
  );
  $(".simpletable").each(function () {
    $(this).attr("class", "table table-bordered table-sm");
    $(this)
      .find("th")
      .each(function () {
        $(this).css("text-align", "center");
      });
    $(this)
      .find("td")
      .each(function () {
        $(this).css("text-align", "center");
      });
  });
  for (var i = 0; i < data.table[data.table_headers[0]].length; i++) {
    string = `<tr>`;
    for (j in data.table_headers) {
      string += `<td style="text-align:center;">${
        data.table[data.table_headers[j]][i]
      }</td>`;
    }
    string += `</tr>`;
    $(`#${actual_vs_predicted_table_id}`).find("tbody").append(string);
  }

  $(`#${actual_vs_predicted_table_id} thead tr`).empty();
  for (j in data.table_headers) {
    $(`#${actual_vs_predicted_table_id}`)
      .find("thead tr")
      .eq(0)
      .append(`<th style="text-align:center;">${data.table_headers[j]}</th>`);
  }
}

function trainEWMARun(data, container, computeElementId, run = 0) {
  if (run === 0) {
    var actual_vs_predicted_table_id = `exampledataResults_${computeElementId}`;
  } else {
    var actual_vs_predicted_table_id = `exampledataResults_${run}_${computeElementId}`;
  }
  $(`#${container}`).append(
    `<div class="row">
            <div class="col-6">
                <div class="card">
                    ${data.summary}
                </div>
                <div class="card">
                    <div class="card-header" style="padding:0.3rem;background:whitesmoke;">
                        <h5 class="mb-0" style="text-align:center;">
                        Actual vs Predicted - Table
                        </h5>
                    </div>
                    <div class="card-body" style="padding:0.9rem;">
                        <table id="${actual_vs_predicted_table_id}" class="display compact" style="width:100%;">
                            <thead>
                                <tr></tr>
                            </thead>
                            <tbody>
                            </tbody>
                        </table>
                    </div>
                </div>
                <div class="card">
                    <div class="card-header" style="padding:0.3rem;background:whitesmoke">
                        <h5 class="mb-0" style="text-align:center;">
                            Augmented Dickey Fuller Test For Stationarity
                        </h5>
                    </div>
                    <div class="card-body">
                        <div class = "row" style="background:whitesmoke;">
                            <div class = "col-6">
                                <span style="font-weight:bold;"> H0 : </span > The time series has a unit root and is not stationary.
                            </div>
                            <div class = "col-6">
                                <span style="font-weight:bold;"> H1 :  </span > The time series is stationary.
                            </div>
                        </div>
                        <br>
                        <div class = "row" style="margin-left:0.25%">
                            <span style="font-weight:bold;"> P-value : </span > &nbsp;${data.adf_p_value}
                        </div><br>
                        <div class = "row" style="margin-left:0.25%">
                            <span style="font-weight:bold;"> Conclusion : </span >&nbsp;${data.adf_test_result}
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-6">
                <div class="card">
                    <div class="card-header" style="padding:0.3rem;background:whitesmoke">
                        <h5 class="mb-0" style="text-align:center;">
                            Model Analysis
                        </h5>
                    </div>
                    <div class="card-body" style="padding:0.5rem;">
                        <div class = "row">
                            <img
                            src="data:image/png;base64,${data.residuals_plot}"
                            width="98%"
                            height="70%"
                            alt="Residuals Plot"
                            style="border:2px solid black;margin-left:0.3rem"
                            title="Residuals Plot"
                            />
                        </div>
                        <br>
                        <div class = "row">
                            <img
                            src="data:image/png;base64,${data.acf_result}"
                            width="98%"
                            height="70%"
                            alt="ACF of Residuals"
                            style="border:2px solid black;margin-left:0.3rem"
                            title="ACF of Residuals"
                            />
                        </div>
                        <br>
                        <div class="row">
                            <img
                                src="data:image/png;base64,${data.plot}"
                                width="98%"
                                height="70%"
                                alt="Actual vs Predicted"
                                style="border:2px solid black;margin-left:0.3rem"
                                title="Actual vs Predicted"
                            />
                        </div>
                        <br>
                        <div class="row">
                            <p style="margin-left:22.5%"><span style="font-weight:bold;">Mean Squared Error (MSE) </span > = ${data.mse}.</p>
                        </div>
                    </div>
                </div>
                <div class="card">
                    <div class="card-header" style="padding:0.3rem;background:whitesmoke">
                        <h5 class="mb-0" style="text-align:center;">
                            Jarque-Bera Test For Normality
                        </h5>
                    </div>
                    <div class="card-body">
                        <div class = "row" style="background:whitesmoke;">
                            <div class = "col-6">
                                <span style="font-weight:bold;"> H0 : </span > The time series is normally distributed.
                            </div>
                            <div class = "col-6">
                                <span style="font-weight:bold;"> H1 :  </span > The time series follows some other statistical distribution.
                            </div>
                        </div>
                        <br>
                        <br>
                        <div class = "row" >
                            <div class="col-6">
                                <span style="font-weight:bold;"> Mean of residuals : </span > &nbsp;${data.mean}
                            </div>
                            <div class="col-6">
                                <span style="font-weight:bold;"> SD of residuals : </span > &nbsp;${data.std}
                            </div>
                        </div>
                        <br>
                        <div class = "row"  >
                            <div class="col-12">
                                <span style="font-weight:bold;"> P-value : </span > &nbsp;${data.jb_p_value}
                            </div>
                        </div>
                        <br>
                        <div class = "row" >
                            <div class="col-12">
                                <span style="font-weight:bold;"> Conclusion : </span >&nbsp;${data.jb_test_result}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>`
  );
  $(".simpletable").each(function () {
    $(this).attr("class", "table table-bordered table-sm");
    $(this)
      .find("th")
      .each(function () {
        $(this).css("text-align", "center");
      });
    $(this)
      .find("td")
      .each(function () {
        $(this).css("text-align", "center");
      });
  });
  for (var i = 0; i < data.table[data.table_headers[0]].length; i++) {
    string = `<tr>`;
    for (j in data.table_headers) {
      string += `<td style="text-align:center;">${
        data.table[data.table_headers[j]][i]
      }</td>`;
    }
    string += `</tr>`;
    $(`#${actual_vs_predicted_table_id}`).find("tbody").append(string);
  }

  $(`#${actual_vs_predicted_table_id} thead tr`).empty();
  for (j in data.table_headers) {
    $(`#${actual_vs_predicted_table_id}`)
      .find("thead tr")
      .eq(0)
      .append(`<th style="text-align:center;">${data.table_headers[j]}</th>`);
  }
}

function displayPortfolioValuationOutput(
  data,
  container,
  computeElementId,
  run = 0
) {
  if (run === 0) {
    var portfolio_valuation_table = `exampledataResults3_${computeElementId}`;
  } else {
    var portfolio_valuation_table = `exampledataResults3_${run}_${computeElementId}`;
  }
  var string_0 = `<div class="col-12">
                <div class="card">
                    <div class="card-header" style="padding:0.3rem;background:whitesmoke;">
                        <h5 class="mb-0" style="text-align:center;">
                            Portfolio Valuation
                        </h5>
                    </div>
                    <div class="card-body" style="padding:0.3rem;">
                        <table id="${portfolio_valuation_table}" class="display compact" style="width:100%;">
                            <thead>
                                <tr></tr>
                            </thead>
                            <tbody>
                            </tbody>
                        </table>
                    </div>
                </div>
        </div>`;
  if (data.var_plot && data.var_plot != "") {
    string_0 += `<div class="card">
                        <div class="card-header" style="padding:0.3rem;background:whitesmoke;">
                            <h5 class="mb-0" style="text-align:center;">
                                Portfolio Value at Risk (VaR)
                            </h5>
                        </div>
                        <div class="card-body" style="padding:0.3rem;">
                            <img
                                src="data:image/png;base64,${data.var_plot}"
                                style="border:2px solid black;margin:auto;"
                                height=100%,
                                width=100%,
                                alt="VaR"
                                title="Value at Risk"
                                />
                        </div>
                    </div>`;
  }

  $(`#${container}`).append(string_0);

  $(`#${portfolio_valuation_table} thead tr`).empty();

  function cf_results(computeElementId) {
    $(`.view_cf_results_${computeElementId}`)
      .off("click")
      .on("click", function () {
        var data1 = eval(JSON.parse($(this).attr("data-output")));
        $(`#viewResults_${computeElementId}`).empty();
        $(`#viewResults_${computeElementId}`).append(`
            <div class="col-12">
                    <div class="card">
                        <div class="card-header" style="padding:0.3rem;background:whitesmoke;">
                            <h5 class="mb-0" style="text-align:center;">
                            Cashflow Table
                            </h5>
                        </div>
                        <div class="card-body" style="padding:0.9rem;">
                            <table id="exampledataResults_${computeElementId}" class="display compact" style="width:100%;">
                                <thead>
                                    <tr></tr>
                                </thead>
                                <tbody>
                                </tbody>
                            </table>
                        </div>
                    </div>
            </div>
            `);
        for (var i = 0; i < data1.length; i++) {
          string = `<tr>`;
          for ([key, value] of Object.entries(data1[i])) {
            string += `<td style="text-align:center;">${value}</td>`;
          }
          string += `</tr>`;
          $(`#exampledataResults_${computeElementId}`)
            .find("tbody")
            .append(string);
        }

        $(`#exampledataResults_${computeElementId} thead tr`).empty();
        for ([key, value] of Object.entries(data1[0])) {
          $(`#exampledataResults_${computeElementId}`)
            .find("thead tr")
            .eq(0)
            .append(`<th style="text-align:center;">${key}</th>`);
        }

        $(`#PF_Val_modal_${computeElementId}`).modal("show");
        initialiseDataTable(`exampledataResults_${computeElementId}`);
      });
  }

  function sensitivity_results(computeElementId) {
    $(`.view_sensitivity_results_${computeElementId}`)
      .off("click")
      .on("click", function () {
        var data1 = eval(JSON.parse($(this).attr("data-output")));
        $(`#viewResults_${computeElementId}`).empty();
        $(`#viewResults_${computeElementId}`).append(`
            <div class="col-12">
                    <div class="card">
                        <div class="card-header" style="padding:0.3rem;background:whitesmoke;">
                            <h5 class="mb-0" style="text-align:center;">
                            Sensitivity Analysis
                            </h5>
                        </div>
                        <div class="card-body" style="padding:0.9rem;">
                            <table id="exampledataResults_${computeElementId}" class="display compact" style="width:100%;">
                                <thead>
                                    <tr></tr>
                                </thead>
                                <tbody>
                                </tbody>
                            </table>
                        </div>
                    </div>
            </div>

            `);

        for (var i = 0; i < data1.length; i++) {
          string = `<tr>`;
          for (j in Object.keys(data1[0])) {
            string += `<td style="text-align:center;">${
              data1[i][Object.keys(data1[i])[j]]
            }</td>`;
          }
          string += `</tr>`;
          $(`#exampledataResults_${computeElementId}`)
            .find("tbody")
            .append(string);
        }
        $(`#exampledataResults_${computeElementId} thead tr`).empty();
        for (j in Object.keys(data1[0])) {
          $(`#exampledataResults_${computeElementId}`)
            .find("thead tr")
            .eq(0)
            .append(
              `<th style="text-align:center;">${Object.keys(data1[0])[j]}</th>`
            );
        }

        $(`#PF_Val_modal_${computeElementId}`).modal("show");
        initialiseDataTable(`exampledataResults_${computeElementId}`);
      });
  }

  if (Object.keys(data).includes("output_source_file")) {
    const ColumnNamesArray = [];
    for (let key of data.columns_list) {
      $(`#${portfolio_valuation_table}`)
        .find("thead tr")
        .eq(0)
        .append(`<th style="text-align:center;">${key}</th>`);
      ColumnNamesArray.push({ data: key });
    }
    let sourceOutputCode = data["output_source_file"];
    var runModelTable = $(`#${portfolio_valuation_table}`).DataTable({
      autoWidth: true,
      scrollY: "60vh",
      scrollX: 300,
      scrollCollapse: true,
      sScrollXInner: "100%",
      ordering: false,
      serverSide: true,
      orderCellsTop: true,
      responsive: true,
      colReorder: {
        fixedColumnsLeft: 1,
      },
      deferRender: true,
      paging: true,
      lengthMenu: [
        [1, 5, 50, -1],
        [1, 5, 50, "All"],
      ],
      stripeClasses: false,
      pageLength: 50,
      dom: "lfBrtip",
      ajax: {
        url:
          window.location.pathname +
          "computation-server-side/" +
          sourceOutputCode +
          "--portfolioValuation",
        type: "POST",
        data: function (d, settings) {
          d.filters = JSON.stringify([]);
          return d;
        },
      },
      columns: ColumnNamesArray,
      buttons: [
        {
          extend: "collection",
          text: "Export",
          buttons: [
            {
              extend: "copy",
              filename: "Revolutio",
              title: "",
              exportOptions: {
                columns: ":visible",
              },
            },
            {
              extend: "excel",
              filename: "Revolutio",
              title: "",
              exportOptions: {
                columns: ":visible",
              },
            },
            {
              extend: "csv",
              filename: "Revolutio",
              title: "",
              exportOptions: {
                columns: ":visible",
              },
            },
            {
              extend: "pdf",
              filename: "Revolutio",
              title: "",
              exportOptions: {
                columns: ":visible",
              },
            },
            {
              text: "XML",
              attr: {
                id: portfolio_valuation_table,
              },
              exportOptions: { columns: ":visible:not(.noVis)" },
              action: function (e, dt, type, indexes) {
                node_data = dt.nodes()[0];
                table_data_id = $(node_data).attr("id");
                $("#" + table_data_id).tableExport({ type: "xml" });
              },
            },
          ],
        },
        {
          extend: "colvis",
          className: "scroller",
        },
      ],
      columnDefs: [
        {
          render: function (data, type, full, meta) {
            if (typeof data === "string" || data instanceof String) {
              if (data.includes("<td>")) {
                return data;
              } else {
                return (
                  "<div style='white-space: normal;width: 100%;'>" +
                  data +
                  "</div>"
                );
              }
            } else {
              return data;
            }
          },
          targets: "_all",

          className: "dt-center allColumnClass all",
        },
        {
          targets: 0,
          width: "20%",
          className: "noVis",
        },
        //{ 'visible': false, 'targets': [1,3] }
      ],
      initComplete: function () {
        var freeze_e_id = $(this).closest("table").attr("id");

        var table1 = $(`#${freeze_e_id}`).DataTable();
        $(`#${freeze_e_id}`).on("click", "td", function () {
          cellColLen4 = table1.columns(":visible").nodes().length;
          cellIndex2 = table1.cell(this).index().column;

          $(this).click(function () {
            $(this).toggleClass("cell_highlighted");
            $(this).toggleClass("cell_selected");
          });
        });
        cf_results(computeElementId);
        sensitivity_results(computeElementId);

        this.api()
          .columns()
          .every(function () {
            var column = this;
            var title = $(this).text();
            var select = $(
              `<input type="text" data-inputid='inputtext' value="" data-input_value="" style="text-align:center;border-bottom:none;border:1px solid #ced4da;max-width:130px;"placeholder="Search ` +
                title +
                `" />`
            )
              .appendTo($(column.footer()).empty())
              .on("change", function () {
                if (column.search() !== this.value || this.value == "") {
                  val = this.value;
                  if (this.value !== "") {
                    column.search(val).draw();
                  } else if (this.value == "") {
                    column.search(this.value).draw();
                  }
                }
              });
          });
      },
    });
  }
}

function displayOutputCopula(data, container, computeElementId, run = 0) {
  var container = $(`#${container}`);
  container.empty();
  let simulated_val = `simulated_val_${computeElementId}`;
  let correlation_matrix = `correlation_matrix_${computeElementId}`;
  let varTable = `varTable_${computeElementId}`;
  let data_dict = JSON.parse(data.content);
  let data_corr = data_dict.Correlation_matrix;
  let data_sim = data_dict.Simulated_data;
  let data_var = data_dict.VaR_data;

  container.append(`
      <div class='row' style='display:flex;height:45vh;overflow:auto;'>
          <div class="card col-6" style='padding:5px;'>
              <div class="card-header" style="padding:0.3rem;background:whitesmoke;">
                  <h4 class="mb-0" style="text-align:center;">
                      Correlation Matrix
                  </h4>
              </div>
              <div class="card-body" style="padding:0.3rem;">
                  <table id="${correlation_matrix}" class="display compact">
                      <thead>
                          <tr></tr>
                      </thead>
                      <tbody>
                      </tbody>
                  </table>
              </div>
          </div>
          <div class="card col-6" style='padding:5px;'>
              <div class="card-header" style="padding:0.3rem;background:whitesmoke;">
                  <h4 class="mb-0" style="text-align:center;">
                      Simulated value
                  </h4>
              </div>
              <div class="card-body" style="padding:0.3rem;">
                  <table id="${simulated_val}" class="display compact">
                      <thead>
                          <tr></tr>
                      </thead>
                      <tbody>
                      </tbody>
                  </table>
              </div>
          </div>
      </div>
      `);

  $(`#${correlation_matrix} thead tr`).empty();
  for (let [key, value] of Object.entries(data_corr[0])) {
    $(`#${correlation_matrix}`)
      .find("thead tr")
      .eq(0)
      .append(`<th style="text-align:center;">${key}</th>`);
  }
  for (var i = 0; i < data_corr.length; i++) {
    string = `<tr>`;
    for (let [key, value] of Object.entries(data_corr[i])) {
      string += `<td style="text-align:center;">${value}</td>`;
    }
    string += `</tr>`;
    $(`#${correlation_matrix}`).find("tbody").append(string);
  }

  $(`#${simulated_val} thead tr`).empty();
  for (let [key, value] of Object.entries(data_sim[0])) {
    $(`#${simulated_val}`)
      .find("thead tr")
      .eq(0)
      .append(`<th style="text-align:center;">${key}</th>`);
  }
  for (var i = 0; i < data_sim.length; i++) {
    string = `<tr>`;
    for (let [key, value] of Object.entries(data_sim[i])) {
      string += `<td style="text-align:center;">${value}</td>`;
    }
    string += `</tr>`;
    $(`#${simulated_val}`).find("tbody").append(string);
  }

  container.append(`
      <div class='row'>
          <div class="card col-6">
              <div class="card-header" style="padding:0.3rem;background:whitesmoke;">
                  <h4 class="mb-0" style="text-align:center;">
                      VaR Plot
                  </h4>
              </div>
              <div class="card-body">
                  <div class='row'>
                      <img
                      src="data:image/png;base64,${data_dict.VaR_plot}"
                      style="border:2px solid black;margin:auto;height: 25rem;object-fit: contain;alt:'Varplot'"
                      />
                  </div>
              </div>
          </div>
          <div class="card col-6" style='display: flex;height: 30rem;overflow:auto;'>
              <div class="card-header" style="padding:0.3rem;background:whitesmoke;">
                  <h4 class="mb-0" style="text-align:center;">
                      VaR Table
                  </h4>
              </div>
              <div class="card-body" style="padding:0.3rem;">
                  <table id="${varTable}" class="display compact" style="width:100%;">
                      <thead>
                          <tr></tr>
                      </thead>
                      <tbody>
                      </tbody>
                  </table>
              </div>
          </div>

      </div>
      `);

  $(`#${varTable} thead tr`).empty();
  for (let [key, value] of Object.entries(data_var[0])) {
    $(`#${varTable}`)
      .find("thead tr")
      .eq(0)
      .append(`<th style="text-align:center;">${key}</th>`);
  }
  for (var i = 0; i < data_var.length; i++) {
    string = `<tr>`;
    for (let [key, value] of Object.entries(data_var[i])) {
      string += `<td style="text-align:center;">${value}</td>`;
    }
    string += `</tr>`;
    $(`#${varTable}`).find("tbody").append(string);
  }
  return [simulated_val, correlation_matrix, varTable];
}

function displayResultsBacktest(data, container, computeElementId, run = 0) {
  var container = $(`#${container}`);
  container.empty();
  if (run === 0) {
    var acttable = `acttable_${computeElementId}`;
    var hyptable = `hyptable_${computeElementId}`;
    var actdf = `actdf_${computeElementId}`;
    var hypdf = `hypdf_${computeElementId}`;
  } else {
    var acttable = `acttable_${run}_${computeElementId}`;
    var hyptable = `hyptable_${run}_${computeElementId}`;
    var actdf = `actdf_${run}_${computeElementId}`;
    var hypdf = `hypdf_${run}_${computeElementId}`;
  }

  container.append(`
    <div class='row'>
      <div class="col-6">
              <div class="card" style='height:400px;width:100%;'>
                  <div class="card-header" style="padding:0.3rem;background:whitesmoke;">
                      <h2 class="mb-0" style="text-align:center;">
                      Actual Backtesting Scenarios
                      </h2>
                  </div>
                  <div class="card-body" style="padding:0.9rem;overflow:auto;">
                      <table class="display compact" id="${actdf}" style="width:auto;height:auto;border-spacing:15px;">
                          <thead>
                              <tr></tr>
                          </thead>
                          <tbody>
                          </tbody>
                      </table>
                  </div>
              </div>
              <div class="card">
                  <div class="card-header" style="padding:0.3rem;background:whitesmoke;">
                      <h2 class="mb-0" style="text-align:center;">
                      Actual Backtesting Summary
                      </h2>
                  </div>
                  <div class="card-body" style="padding:0.9rem;">
                      <table class="display compact" id="${acttable}" style="width:100%;">
                          <thead>
                              <tr></tr>
                          </thead>
                          <tbody>
                          </tbody>
                      </table>
                  </div>
              </div>
      </div>
      <div class="col-6">
              <div class="card" style='height:400px;width:100%;'>
                  <div class="card-header" style="padding:0.3rem;background:whitesmoke;">
                      <h2 class="mb-0" style="text-align:center;">
                      Hypothetical Backtesting Scenarios
                      </h2>
                  </div>
                  <div class="card-body" style="padding:0.9rem;overflow:auto;">
                      <table class="display compact" id="${hypdf}" style="width:auto;height:auto;border-spacing:15px;">
                          <thead>
                              <tr></tr>
                          </thead>
                          <tbody>
                          </tbody>
                      </table>
                  </div>
              </div>
              <div class="card">
                  <div class="card-header" style="padding:0.3rem;background:whitesmoke;">
                      <h2 class="mb-0" style="text-align:center;">
                      Hypothetical Backtesting Summary
                      </h2>
                  </div>
                  <div class="card-body" style="padding:0.9rem;">
                      <table class="display compact" id="${hyptable}" style="width:100%;">
                          <thead>
                              <tr></tr>
                          </thead>
                          <tbody>
                          </tbody>
                      </table>
                  </div>
              </div>
      </div>
    </div>
    `);

  for (var i = 0; i < data.Actual_D.length; i++) {
    string = `<tr>`;
    for (let [key, value] of Object.entries(data.Actual_D[i])) {
      string += `<td style="text-align:center;padding:5px;">${value}</td>`;
    }
    string += `</tr>`;
    $(`#${actdf}`).find("tbody").append(string);
  }
  $(`#${actdf} thead tr`).empty();
  for (let [key, value] of Object.entries(data.Actual_D[0])) {
    $(`#${actdf}`)
      .find("thead tr")
      .eq(0)
      .append(`<th style="text-align:center;padding:5px;">${key}</th>`);
  }

  for (var i = 0; i < data.Hyp_D.length; i++) {
    string = `<tr>`;
    for (let [key, value] of Object.entries(data.Hyp_D[i])) {
      string += `<td style="text-align:center;padding:5px;">${value}</td>`;
    }
    string += `</tr>`;
    $(`#${hypdf}`).find("tbody").append(string);
  }
  $(`#${hypdf} thead tr`).empty();
  for (let [key, value] of Object.entries(data.Hyp_D[0])) {
    $(`#${hypdf}`)
      .find("thead tr")
      .eq(0)
      .append(`<th style="text-align:center;padding:5px;">${key}</th>`);
  }

  for (var i = 0; i < data.Actual_R.length; i++) {
    string = `<tr>`;
    for (let [key, value] of Object.entries(data.Actual_R[i])) {
      if (value === "Low Risk") {
        string += `<td style="text-align:center;background-color:#98FB98">${value}</td>`;
      } else if (value === "Medium Risk") {
        string += `<td style="text-align:center; background-color:#F0E68C">${value}</td>`;
      } else if (value === "High Risk") {
        string += `<td style="text-align:center; background-color:#FA8072">${value}</td>`;
      } else {
        string += `<td style="text-align:center;">${value}</td>`;
      }
    }
    string += `</tr>`;
    $(`#${acttable}`).find("tbody").append(string);
  }

  for (var i = 0; i < data.Hyp_R.length; i++) {
    string = `<tr>`;
    for (let [key, value] of Object.entries(data.Hyp_R[i])) {
      if (value === "Low Risk") {
        string += `<td style="text-align:center; background-color:#98FB98">${value}</td>`;
      } else if (value === "Medium Risk") {
        string += `<td style="text-align:center; background-color:#F0E68C">${value}</td>`;
      } else if (value === "High Risk") {
        string += `<td style="text-align:center; background-color:#FA8072">${value}</td>`;
      } else {
        string += `<td style="text-align:center;">${value}</td>`;
      }
    }
    string += `</tr>`;
    $(`#${hyptable}`).find("tbody").append(string);
  }
  return acttable, hyptable;
}

function displayOutputFitDiscrete(data, container, element_id, run = 0) {
  var data_dict = JSON.parse(data.content);
  let data_info = JSON.parse(data.info_dict);
  let discrete_element_id = data_info.element_id;
  let element_name = data_info.element_name;
  let model_name = data_info.model_name;
  let result_usecase = data_info.use_case;
  let graph_image = "";
  let auto_save_config = false;
  if (data.var_plot) {
    graph_image = `data:image/png;base64,${data.var_plot}`;
  }
  if (data_info.hasOwnProperty("auto_save")) {
    if (data_info.auto_save) {
      auto_save_config = true;
    }
  }

  if (run === 0) {
    var fitDiscrete_table = `fitDiscrete_table_${element_id}`;
    var fitDiscrete_table_section = `fitDiscrete_table_section_${element_id}`;
    var saveFitDiscrete = `saveFitDiscrete_${element_id}`;
  } else {
    var fitDiscrete_table = `fitDiscrete_table_${run}_${element_id}`;
    var fitDiscrete_table_section = `fitDiscrete_table_section_${run}_${element_id}`;
    var saveFitDiscrete = `saveFitDiscrete_${run}_${element_id}`;
  }

  var string_0 = `<div class="row" style='display:flex;'>`;
  string_0 += `<div class="card col-5" style='margin-left:10px'>
                        <div class="card-header" style="padding:0.3rem;background:whitesmoke;">
                            <h4 class="mb-0" style="text-align:center;">
                               Distribution Graph
                            </h4>
                        </div>
                        <div class="card-body" style="height:360px;overflow:auto">
                            <img
                                src="${graph_image}"
                                width="100%"
                                alt="Distribution Graph"
                                style="height:20rem"
                                title="Distribution Graph"
                                />
                        </div>
                    </div>`;
  string_0 += ` <div class="card col-6" style='margin-left:auto;margin-right:10px;height:24rem;'>
                            <div class="card-header" style="padding:0.3rem;background:whitesmoke;">
                                <h4 class="mb-0" style="text-align:center;">
                                  Distribution Parameters Table
                                </h4>
                            </div>
                            <div class="card-body" id='${fitDiscrete_table_section}'  style="height:400px;overflow:auto;">
                                <table id = "${fitDiscrete_table}" class="table table-bordered" style="width:100%;">
                                    <thead>
                                        <tr>
                                            <th></th>
                                            <th></th>
                                        </tr>
                                        </thead>
                                        <tbody>
                                    </tbody>
                                    </table>
                            </div>
                            <div class="card-footer" style="background:whitesmoke;text-align:end">
                                <button type="button" id="${saveFitDiscrete}" class="btn btn-primary rounded px-2 ml-auto"  style="color:white;">Save Configuration</button>
                            </div>
                        </div>`;
  string_0 += `</div>`;

  $(`#${container}`).append(string_0);
  $(`#${fitDiscrete_table}` + "_wrapper").remove();
  $(`#${fitDiscrete_table}`).remove();

  $(`#${fitDiscrete_table_section}`).append(`
    <table id = "${fitDiscrete_table}" class="table table-bordered" style="width:100%;">
        <thead>
            <tr>
            </tr>
            </thead>
            <tbody>
        </tbody>
        </table>
    `);
  $(`#${fitDiscrete_table} thead tr`).empty();
  $(`#${fitDiscrete_table}`)
    .find("thead tr")
    .eq(0)
    .append(
      `<th style="text-align:center;text-transform:capitalize;">Distribution Type</th><th style="text-align:center;">Parameters</th>`
    );

  if (Object.keys(data_dict).length > 0) {
    $(`#${fitDiscrete_table}`)
      .find("tbody")
      .append(
        `<tr data-method-name='${
          Object.keys(data_dict)[0]
        }'><td style="text-align:center;text-transform:capitalize;">${
          Object.keys(data_dict)[0]
        }</td><td style="text-align:center;">${
          data_dict["poisson"]["lambda"]
        }</td></tr>`
      );
  }

  initialiseDataTable(fitDiscrete_table);
  setTimeout(function () {
    $(`#${fitDiscrete_table}`).DataTable().columns.adjust();
  }, 500);
  if (auto_save_config) {
    $(`#${saveFitDiscrete}`).remove();
  }

  $(`#${saveFitDiscrete}`)
    .off("click")
    .on("click", function () {
      if (Object.keys(data_dict).length > 0) {
        $(`#${saveFitDiscrete}`).empty();
        $(`#${saveFitDiscrete}`).append(
          `<i class="fa fa-circle-notch fa-spin"></i> Saving`
        );

        $.ajax({
          url: `/users/${urlPath}/computationModule/`,
          data: {
            element_id: discrete_element_id,
            element_name: element_name,
            model_name: model_name,
            output_fit_config: JSON.stringify(data_dict),
            use_case: result_usecase,
            operation: "save_fit_discrete_configuration",
          },
          type: "POST",
          dataType: "json",
          success: function (data) {
            Swal.fire({
              icon: "success",
              text: "Fit Discrete Distribution Configuration saved successfully!",
            });
            $(`#${saveFitDiscrete}`).parent().find("i").remove();
            $(`#${saveFitDiscrete}`).text("Save Configuration");
          },
          error: function () {
            Swal.fire({
              icon: "error",
              text: "Error! Failure in saving the Fit Discrete Distribution configuration.  Please check your configuration and try again.",
            });
          },
        });
      } else {
        Swal.fire({
          icon: "warning",
          text: "Fit Discrete Distribution values have not been generated.",
        });
      }
    });
}

// Goodness of Fit Test
function displayOutputFitTest(data, container, element_id, run = 0) {
  var data_dict = JSON.parse(data.content);
  let best_fit = JSON.parse(data.best_fit);
  let data_info = JSON.parse(data.info_dict);
  let fit_element_id = data_info.element_id;
  let element_name = data_info.element_name;
  let model_name = data_info.model_name;
  let result_usecase = data_info.use_case;
  let graph_image = "";
  let auto_save_config = false;
  if (data_info.hasOwnProperty("auto_save")) {
    if (data_info.auto_save) {
      auto_save_config = true;
    }
  }
  if (run === 0) {
    var fittest_table = `fittest_table${element_id}`;
    var fittest_table_section = `fittest_table_section${element_id}`;
    var saveGoodnessBestFit = `saveGoodnessBestFit${element_id}`;
  } else {
    var fittest_table = `fittest_table_${element_id}${run}`;
    var fittest_table_section = `fittest_table_section_${element_id}${run}`;
    var saveGoodnessBestFit = `saveGoodnessBestFit_${element_id}${run}`;
  }
  if (data.var_plot) {
    graph_image = `data:image/png;base64,${data.var_plot}`;
  }
  var string_0 = `<div id='FitTestDiv_${element_id}'  class="row" style='height:100%;'>`;
  string_0 += `<div class="card col-5" style='margin-left:10px'>
                      <div class="card-header" style="padding:0.3rem;background:whitesmoke;">
                          <h4 class="mb-0" style="text-align:center;">
                              Best Fit Graph
                          </h4>
                      </div>
                      <div class="card-body" style="height:460px;overflow:auto">
                          <img
                              src="${graph_image}"
                              width="100%"
                              alt="GoodnessFitTest"
                              style="height:350px;"
                              title="Best Fit Test"
                              />
                      </div>
                  </div>`;
  string_0 += ` <div class="card col-6" style='margin-left:auto;margin-right:10px;height:67vh;overflow:auto;'>
          <div class="card-header" style="padding:0.3rem;background:whitesmoke;">
              <h4 class="mb-0" style="text-align:center;">
                  Goodness of Fit Table
              </h4>
          </div>
          <div class="card-body " id='${fittest_table_section}' style="height:100%">
              <table id = "${fittest_table}" class="table" style="width:100%;">
                  <thead>
                      <tr>
                          <th></th>
                          <th></th>
                      </tr>
                      </thead>
                      <tbody>
                  </tbody>
                  </table>
          </div>
          <div class="card-footer" style="background:whitesmoke;text-align:end">
              <button type="button" id="${saveGoodnessBestFit}" class="btn btn-primary rounded px-2 ml-auto"  style="color:white;">Save Best Fit</button>
          </div>
      </div>`;
  string_0 += `</div>`;

  $(`#${fittest_table}_wrapper`).remove();
  $(`#${fittest_table}`).remove();
  $(`#${fittest_table_section}`).append(`
  <table id = "${fittest_table}" class="table" style="width:100%;">
      <thead>
          <tr>
          </tr>
          </thead>
          <tbody>
      </tbody>
      </table>
  `);
  $(`#${container}`).append(string_0);
  $(`#${fittest_table} thead tr`).empty();
  for (let [key, value] of Object.entries(data_dict[0])) {
    $(`#${fittest_table}`)
      .find("thead tr")
      .eq(0)
      .append(`<th style="text-align:center;">${key}</th>`);
  }

  if (Object.keys(data_dict).length > 0) {
    for (var i = 0; i < data_dict.length; i++) {
      string = `<tr data-method-name='${data_dict[i]["Distribution"]}'>`;
      for (let [key, value] of Object.entries(data_dict[i])) {
        if (data_dict[i]["Distribution"] in best_fit) {
          string += `<td style="text-align:center;background-color:lightgrey;">${value}</td>`;
        } else {
          string += `<td style="text-align:center;">${value}</td>`;
        }
      }
      string += `</tr>`;
      $(`#${fittest_table}`).find("tbody").append(string);
    }
  }

  if (auto_save_config) {
    $(`#${saveGoodnessBestFit}`).remove();
  }
  $(`#${saveGoodnessBestFit}`)
    .off("click")
    .on("click", function () {
      if (Object.keys(best_fit).length > 0) {
        $(`#${saveGoodnessBestFit}`).empty();
        $(`#${saveGoodnessBestFit}`).append(
          `<i class="fa fa-circle-notch fa-spin"></i> Saving`
        );

        $.ajax({
          url: `/users/${urlPath}/computationModule/`,
          data: {
            element_id: fit_element_id,
            element_name: element_name,
            model_name: model_name,
            output_fit_config: JSON.stringify(best_fit),
            use_case: result_usecase,
            operation: "save_best_fit_configuration",
          },
          type: "POST",
          dataType: "json",
          success: function (data) {
            Swal.fire({
              icon: "success",
              text: "Best Fit Configuration saved successfully!",
            });
            $(`#${saveGoodnessBestFit}`).parent().find("i").remove();
            $(`#${saveGoodnessBestFit}`).text("Save Best Fit");
          },
          error: function () {
            Swal.fire({
              icon: "error",
              text: "Error! Failure in saving the Best Fit configuration. Please check your configuration and try again.",
            });
          },
        });
      } else {
        Swal.fire({
          icon: "warning",
          text: "Best Fit values have not been generated.",
        });
      }
    });
}

function displayModelOutput(
  data,
  computationModelElementId,
  outputContainer,
  elementToShow,
  elementToHide,
  run = "",
  prevRun = false
) {
  computationModelElementId += run;
  if (
    data.last_element_name == "Interest Rate Products" ||
    data.last_element_name == "Equities" ||
    data.last_element_name == "Mutual Fund"
  ) {
    $(`#${outputContainer}`).append(`
        <div class="col-12">
                <div class="card">
                    <div class="card-header" style="padding:0.3rem;background:whitesmoke;">
                        <h5 class="mb-0" style="text-align:center;">
                        Cashflow Table
                        </h5>
                    </div>
                    <div class="card-body" style="padding:0.9rem;">
                        <table  id="exampledataResults_${computationModelElementId}" class="display compact" style="width:100%;">
                            <thead>
                                <tr></tr>
                            </thead>
                            <tbody>
                            </tbody>
                        </table>
                    </div>
                </div>
        </div>
        <div class="row">
            <div class = "col-6">
                <div class="card">
                    <div class="card-header" style="padding:0.3rem;background:whitesmoke;">
                        <h5 class="mb-0" style="text-align:center;">
                        Valuation Results
                        </h5>
                    </div>
                    <div class="card-body" style="padding:0.9rem;">
                        <table id="exampledataResults2_${computationModelElementId}" class="display compact" style="width:100%;">
                            <thead>
                                <tr></tr>
                            </thead>
                            <tbody>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            <div class = "col-6">
                <div class="card">
                    <div class="card-header" style="padding:0.3rem;background:whitesmoke;">
                        <h5 class="mb-0" style="text-align:center;">
                        Sensitivity Analysis
                        </h5>
                    </div>
                    <div class="card-body" style="padding:0.9rem;">
                        <table id="exampledataResults3_${computationModelElementId}" class="display compact" style="width:100%;">
                            <thead>
                                <tr></tr>
                            </thead>
                            <tbody>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
        `);
    for (
      var i = 0;
      i <
      data.content.cashflow_model_results[
        data.content.cashflow_model_results_headers[0]
      ].length;
      i++
    ) {
      string = `<tr>`;
      for (j in data.content.cashflow_model_results_headers) {
        string += `<td style="text-align:center;">${
          data.content.cashflow_model_results[
            data.content.cashflow_model_results_headers[j]
          ][i]
        }</td>`;
      }
      string += `</tr>`;
      $(`#exampledataResults_${computationModelElementId}`)
        .find("tbody")
        .append(string);
    }

    $(`#exampledataResults_${computationModelElementId} thead tr`).empty();
    for (j in data.content.cashflow_model_results_headers) {
      $(`#exampledataResults_${computationModelElementId}`)
        .find("thead tr")
        .eq(0)
        .append(
          `<th style="text-align:center;">${data.content.cashflow_model_results_headers[j]}</th>`
        );
    }
    for (var i = 0; i < data.content.valuation_results.length; i++) {
      string = `<tr>`;
      for (j in data.content.valuation_headers) {
        string += `<td style="text-align:center;">${
          data.content.valuation_results[i][data.content.valuation_headers[j]]
        }</td>`;
      }
      string += `</tr>`;
      $(`#exampledataResults2_${computationModelElementId}`)
        .find("tbody")
        .append(string);
    }

    $(`#exampledataResults2_${computationModelElementId} thead tr`).empty();
    for (j in data.content.valuation_headers) {
      $(`#exampledataResults2_${computationModelElementId}`)
        .find("thead tr")
        .eq(0)
        .append(
          `<th style="text-align:center;">${data.content.valuation_headers[j]}</th>`
        );
    }
    for (var i = 0; i < data.content.sensitivity_analysis.length; i++) {
      string = `<tr>`;
      for (j in data.content.sensitivity_analysis_headers) {
        string += `<td style="text-align:center;">${
          data.content.sensitivity_analysis[i][
            data.content.sensitivity_analysis_headers[j]
          ]
        }</td>`;
      }
      string += `</tr>`;
      $(`#exampledataResults3_${computationModelElementId}`)
        .find("tbody")
        .append(string);
    }
    $(`#exampledataResults3_${computationModelElementId} thead tr`).empty();
    for (j in data.content.sensitivity_analysis_headers) {
      $(`#exampledataResults3_${computationModelElementId}`)
        .find("thead tr")
        .eq(0)
        .append(
          `<th style="text-align:center;">${data.content.sensitivity_analysis_headers[j]}</th>`
        );
    }
    if (data.content.cashflow_model_results_headers.length > 0) {
      initialiseDataTable(`exampledataResults${computationModelElementId}`);
    }
    if (data.content.sensitivity_analysis.length > 0) {
      initialiseDataTable(`exampledataResults3${computationModelElementId}`);
    }
    if (data.content.valuation_headers.length > 0) {
      initialiseDataTable(`exampledataResults2${computationModelElementId}`);
    }

    elementToShow.css("display", "block");
    elementToHide.css("display", "none");
    if (data.content.cashflow_model_results_headers.length > 0) {
      $(`#exampledataResults_${computationModelElementId}`)
        .DataTable()
        .columns.adjust();
    }
    if (data.content.sensitivity_analysis.length > 0) {
      $(`#exampledataResults3_${computationModelElementId}`)
        .DataTable()
        .columns.adjust();
    }
    if (data.content.valuation_headers.length > 0) {
      $(`#exampledataResults2_${computationModelElementId}`)
        .DataTable()
        .columns.adjust();
    }
  } else if (data.last_element_name == "Optimiser") {
    $(`#${outputContainer}`).empty();
    $(`#${outputContainer}`).append(`
        <div class="col-12">
                <div class="card">
                    <div class="card-header" style="padding:0.3rem;background:whitesmoke;">
                        <h4 class="mb-0" style="text-align:center;">
                        Model Portfolio Allocation
                        </h4>
                    </div>
                    <div class="card-body" style="padding:0.9rem;">
                        <table id="exampledataResults_${computationModelElementId}" class="display compact" style="width:100%;">
                            <thead>
                                <tr></tr>
                            </thead>
                            <tbody>
                            </tbody>
                        </table>
                    </div>
                </div>
        </div>
        <div class="row" id="additionOutputOptimizer">
        </div>
        <div class="col-12">
            <div class="card">
            <div class="card-header" style="padding:0.3rem;background:whitesmoke;">
                <h4 class="mb-0" style="text-align:center;">
                    Security Allocation
                </h4>
            </div>
            <div class="card-body" style="padding:0.3rem;">
                <br>
                <div class = "row" style="margin-left:0.5rem;"><h6><span class="text-primary">Investment: </span><span style="background:whitesmoke;">₹ ${data.content.investment_amount}</span><h6></div>
                <div class = "row" style="margin-left:0.5rem;"><h6><span class="text-primary">Unallocated Investment: </span><span style="background:whitesmoke;">₹ ${data.content.unallocated_investment_amount}</span></h6></div>
                <br>
                <table id="exampledataResults4_${computationModelElementId}" class="display compact" style="width:100%;margin-left:0.5rem;">
                    <thead>
                        <tr></tr>
                    </thead>
                    <tbody>
                    </tbody>
                </table>
            </div>
            </div>
        </div>
        `);
    if (Object.keys(data.content).includes("constraint_report")) {
      $("#additionOutputOptimizer").append(`
            <div class = "col-7">
                <div class="card">
                    <div class="card-header" style="padding:0.3rem;background:whitesmoke;">
                        <h4 class="mb-0" style="text-align:center;">
                        Constraint Report
                        </h4>
                    </div>
                    <div class="card-body" style="padding:0.9rem;">
                        <table id="exampledataResults2_${computationModelElementId}" class="display compact" style="width:80%;">
                            <thead>
                                <tr></tr>
                            </thead>
                            <tbody>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            `);
    }
    if (Object.keys(data.content).includes("efficient_frontier")) {
      $("#additionOutputOptimizer").append(`
            <div class = "col-5">
                <div class="card">
                    <div class="card-header" style="padding:0.3rem;background:whitesmoke;">
                        <h4 class="mb-0" style="text-align:center;">
                        Efficient Frontier Curve
                        </h4>
                    </div>
                    <div class="card-body" style="padding:0.9rem;" id="optimizerEffContainer${computationModelElementId}">

                    </div>
                </div>
            </div>
            `);
    }
    for (var i = 0; i < data.content.portfolio_allocation.length; i++) {
      string = `<tr>`;
      for (let [key, value] of Object.entries(
        data.content.portfolio_allocation[i]
      )) {
        string += `<td style="text-align:center;">${value}</td>`;
      }
      string += `</tr>`;
      $(`#exampledataResults_${computationModelElementId}`)
        .find("tbody")
        .append(string);
    }
    $(`#exampledataResults_${computationModelElementId} thead tr`).empty();
    for (let [key, value] of Object.entries(
      data.content.portfolio_allocation[0]
    )) {
      $(`#exampledataResults_${computationModelElementId}`)
        .find("thead tr")
        .eq(0)
        .append(`<th style="text-align:center;">${key}</th>`);
    }
    for (
      var i = 0;
      i <
      data.content.security_allocation_output[
        data.content.security_allocation_output_headers[0]
      ].length;
      i++
    ) {
      string = `<tr>`;
      for (j in data.content.security_allocation_output_headers) {
        string += `<td style="text-align:center;">${
          data.content.security_allocation_output[
            data.content.security_allocation_output_headers[j]
          ][i]
        }</td>`;
      }
      string += `</tr>`;
      $(`#exampledataResults4_${computationModelElementId}`)
        .find("tbody")
        .append(string);
    }
    $(`#exampledataResults4_${computationModelElementId} thead tr`).empty();
    for (j in data.content.security_allocation_output_headers) {
      $(`#exampledataResults4_${computationModelElementId}`)
        .find("thead tr")
        .eq(0)
        .append(
          `<th style="text-align:center;">${data.content.security_allocation_output_headers[j]}</th>`
        );
    }
    if (Object.keys(data.content).includes("constraint_report")) {
      for (var i = 0; i < data.content.constraint_report.length; i++) {
        string = `<tr>`;
        for (let [key, value] of Object.entries(
          data.content.constraint_report[i]
        )) {
          string += `<td style="text-align:center;">${value}</td>`;
        }
        string += `</tr>`;
        $(`#exampledataResults2_${computationModelElementId}`)
          .find("tbody")
          .append(string);
      }
      $(`#exampledataResults2_${computationModelElementId} thead tr`).empty();
      for (let [key, value] of Object.entries(
        data.content.constraint_report[0]
      )) {
        $(`#exampledataResults2_${computationModelElementId}`)
          .find("thead tr")
          .eq(0)
          .append(`<th style="text-align:center;">${key}</th>`);
      }
    }

    if (Object.keys(data.content).includes("efficient_frontier")) {
      $(`#optimizerEffContainer${computationModelElementId}`).append(`
                <div class="row">
                    <img
                    src="data:image/png;base64,${data.content.efficient_frontier}"
                    width="100%"
                    height="100%"
                    alt="Efficient Frontier"
                    style="border:2px solid black;margin:auto;"
                    title="Efficient Frontier"
                    />
                </div>
            `);
    }
    elementToShow.css("display", "block");
    elementToHide.css("display", "none");
    initialiseDataTable(`exampledataResults${computationModelElementId}`);
    initialiseDataTable(`exampledataResults2${computationModelElementId}`);
    initialiseDataTable(`exampledataResults4${computationModelElementId}`);
  } else if (data.last_element_name == "IR Curve Bootstrapping") {
    $(`#${outputContainer}`).empty();
    var table1Id = "exampledataResults";
    var table2Id = "exampledataResults2";
    var singlecurvetable = "singlecurvetable";
    var singlecurveplot = "singlecurveplot";
    var data_og = data.content;
    for (i in data_og) {
      data = data_og[i];
      table1Id += `_${i}`;
      table2Id += `_${i}`;
      singlecurvetable += `_${i}`;
      singlecurveplot += `_${i}`;
      $(`#${outputContainer}`).append(`
            <div class='row'>
            <div class="col-6">
                    <div class="card">
                        <div class="card-header" style="padding:0.3rem;background:whitesmoke;">
                            <h2 class="mb-0" style="text-align:center;">
                            ${data.curve_name} - Spot Rates
                            </h2>
                        </div>
                        <div class="card-body" style="padding:0.9rem;">
                            <table id='${table1Id}_${computationModelElementId}' style="width:100%;" class="display compact">
                                <thead>
                                    <tr></tr>
                                </thead>
                                <tbody>
                                </tbody>
                            </table>
                        </div>
                    </div>
            </div>
            <div class="col-6" id="${singlecurvetable}">
            </div>
            </div>
            `);

      if (Object.keys(data).includes("Plot")) {
        $(`#${singlecurvetable}`).append(`
                    <div class="card">
                        <div class="card-header" style="padding:0.3rem;background:whitesmoke;">
                            <h2 class="mb-0" style="text-align:center;">
                            ${data.curve_name} - Spot Curve
                            </h2>
                        </div>
                        <div class="card-body" style="padding:0.9rem;" id="${singlecurveplot}">

                        </div>
                    </div>
                `);
      }
      for (var i = 0; i < data.Table.length; i++) {
        string = `<tr>`;
        for (let [key, value] of Object.entries(data.Table[i])) {
          string += `<td style="text-align:center;">${value}</td>`;
        }
        string += `</tr>`;
        $(`#${table1Id}_${computationModelElementId}`)
          .find("tbody")
          .append(string);
      }
      $(`#${table1Id}_${computationModelElementId} thead tr`).empty();
      for (let [key, value] of Object.entries(data.Table[0])) {
        $(`#${table1Id}_${computationModelElementId}`)
          .find("thead tr")
          .eq(0)
          .append(`<th style="text-align:center;">${key}</th>`);
      }

      if (Object.keys(data).includes("Plot")) {
        $(`#${singlecurveplot}`).append(`
                    <div class="row">
                        <img
                        src="data:image/png;base64,${data.Plot}"
                        width="95%"
                        height="95%"
                        alt="Spot Curve"
                        style="border:2px solid black;margin:auto;"
                        title="Spot Curve"
                        />
                    </div>
                `);
      }
      elementToShow.css("display", "block");
      elementToHide.css("display", "none");
      initialiseDataTable(`${table1Id}_${computationModelElementId}`);
    }
  } else if (data.last_element_name === "Boosting Algorithm") {
    $(`#${outputContainer}`).empty();
    $(`#${outputContainer}`).append(`
        <div id="viewDT${computationModelElementId}"></div>
        `);
    displayOutputAB(data.content, computationModelElementId);
    elementToShow.css("display", "block");
    elementToHide.css("display", "none");
    setTimeout(() => {
      $(`#actual_grid${computationModelElementId}`)
        .DataTable()
        .columns.adjust();
      $(`#table_confusionMatrixDecTree${computationModelElementId}`)
        .DataTable()
        .columns.adjust();
      $(`#table_classReportDecTree${computationModelElementId}`)
        .DataTable()
        .columns.adjust();
      $(`#tableParameters${computationModelElementId}`)
        .DataTable()
        .columns.adjust();
    }, 500);
  } else if (
    data.last_element_name === "CART" ||
    data.last_element_name === "CART Algorithm"
  ) {
    $(`#${outputContainer}`).empty();
    $(`#${outputContainer}`).append(`
        <div class="" id="viewDT${computationModelElementId}"></div>
        `);
    displayOutputDecTree(data.content, computationModelElementId);
    elementToShow.css("display", "block");
    elementToHide.css("display", "none");
    setTimeout(() => {
      $(`#actual_grid${computationModelElementId}`)
        .DataTable()
        .columns.adjust();
      $(`#table_confusionMatrixDecTree${computationModelElementId}`)
        .DataTable()
        .columns.adjust();
      $(`#table_classReportDecTree${computationModelElementId}`)
        .DataTable()
        .columns.adjust();
      $(`#tableParameters${computationModelElementId}`)
        .DataTable()
        .columns.adjust();
    }, 500);
  } else if (data.last_element_name == "Linear Regression") {
    $(`#${outputContainer}`).empty();
    displayOutputLinReg(
      data.content,
      (container = `${outputContainer}`),
      computationModelElementId
    );

    elementToShow.css("display", "block");
    elementToHide.css("display", "none");
    initialiseDataTable(
      `table_ActualVFittedLinReg${computationModelElementId}`
    );
    initialiseDataTable(`table_parameterEstLinReg${computationModelElementId}`);
  } else if (data.last_element_name == "Logistic Regression") {
    $(`#${outputContainer}`).empty();
    displayOutputLogReg(
      data.content,
      (container = `${outputContainer}`),
      computationModelElementId
    );
    elementToShow.css("display", "block");
    elementToHide.css("display", "none");
    initialiseDataTable(
      `table_confusionMatrixLogReg${computationModelElementId}`
    );
    initialiseDataTable(`table_classReportLogReg${computationModelElementId}`);
  } else if (data.last_element_name == "Analyse Time Series Data") {
    $(`#${outputContainer}`).empty();
    analyseTSData(data.content, (container = `${outputContainer}`));
    elementToShow.css("display", "block");
    elementToHide.css("display", "none");
  } else if (data.last_element_name == "Train an ARIMA Model") {
    $(`#${outputContainer}`).empty();
    trainARIMARun(
      data.content,
      (container = `${outputContainer}`),
      computationModelElementId
    );
    elementToShow.css("display", "block");
    elementToHide.css("display", "none");
    initialiseDataTable(`exampledataResults${computationModelElementId}`);
  } else if (data.last_element_name == "Train an EWMA Model") {
    $(`#${outputContainer}`).empty();
    trainEWMARun(
      data.content,
      (container = `${outputContainer}`),
      computationModelElementId
    );
    elementToShow.css("display", "block");
    elementToHide.css("display", "none");
    initialiseDataTable(`exampledataResults${computationModelElementId}`);
  } else if (data.last_element_name == "Train a GARCH Model") {
    $(`#${outputContainer}`).empty();
    trainGARCHModel(
      data.content,
      (container = `${outputContainer}`),
      computationModelElementId
    );
    elementToShow.css("display", "block");
    elementToHide.css("display", "none");
    initialiseDataTable(`exampledataResults${computationModelElementId}`);
  } else if (data.last_element_name == "Portfolio Valuation") {
    $(`#${outputContainer}`).empty();
    displayPortfolioValuationOutput(
      data.content,
      (container = `${outputContainer}`),
      computationModelElementId
    );
    elementToShow.css("display", "block");
    elementToHide.css("display", "none");
  } else if (data.last_element_name == "Copula") {
    $(`#${outputContainer}`).empty();
    if (prevRun) {
      var tableIds = displayOutputCopula(
        data,
        (container = `${outputContainer}`),
        computationModelElementId
      );
    } else {
      var tableIds = displayOutputCopula(
        data.content,
        (container = `${outputContainer}`),
        computationModelElementId
      );
    }
    elementToShow.css("display", "block");
    elementToHide.css("display", "none");
    initialiseDataTable(tableIds[0]);
    initialiseDataTable(tableIds[1]);
    initialiseDataTable(tableIds[2]);
  } else if (data.last_element_name == "VaR Backtesting") {
    $(`#${outputContainer}`).empty();
    let acttable,
      hyptable = displayResultsBacktest(
        data.content,
        (container = `${outputContainer}`),
        computationModelElementId
      );
    elementToShow.css("display", "block");
    elementToHide.css("display", "none");
    initialiseDataTable(acttable);
    initialiseDataTable(hyptable);
  } else if (data.last_element_name == "Fit Discrete Distribution") {
    $(`#${outputContainer}`).empty();
    if (prevRun) {
      displayOutputFitDiscrete(
        data,
        (container = outputContainer),
        computationModelElementId,
        (run = run)
      );
    } else {
      displayOutputFitDiscrete(
        data.content,
        (container = outputContainer),
        computationModelElementId,
        (run = run)
      );
    }
    elementToShow.css("display", "block");
    elementToHide.css("display", "none");
  } else if (data.last_element_name == "Goodness Of Fit Test") {
    $(`#${outputContainer}`).empty();
    if (prevRun) {
      displayOutputFitTest(
        data,
        (container = outputContainer),
        computationModelElementId,
        (run = ``)
      );
    } else {
      displayOutputFitTest(
        data.content,
        (container = outputContainer),
        computationModelElementId,
        (run = ``)
      );
    }
    elementToShow.css("display", "block");
    elementToHide.css("display", "none");
    initialiseDataTable(`fittest_table_${computationModelElementId}`);
  } else {
    let redis_col = [];
    var dataContainingColumnNamesRunModel = [];

    elementToShow.css("display", "block");
    elementToHide.css("display", "none");

    $(`#${outputContainer}`).prepend(`
            <div class="form-inline col-5" style="flex-flow:row !important">
                <label for='showEntries${computationModelElementId}' style='top:unset;margin-bottom:unset;margin-right: 0.5rem;'>Show</label>
                <select name='showEntries${computationModelElementId}' id='showEntries${computationModelElementId}' class='select2 form-control' data-elementid='${computationModelElementId}' style='height: 1.5rem !important;min-width:20%;max-width:50%;'>
                    <option value="" selected disabled></option>
                    <option value="5">5</option>
                    <option value="10">10</option>
                    <option value="25">25</option>
                    <option value="50" selected>50</option>
                    <option value="100">100</option>
                    <option value="-1">All</option>
                </select>
                <label style="top:unset;margin-bottom:unset;margin-left: 0.5rem;">entries</label>
            </div>
        `);
    $(`#showEntries${computationModelElementId}`).select2();
    $(
      `#showEntries${computationModelElementId} + .select2-container--default`
    ).css({ width: "4rem !important", margin: " 0 12px !important" });
    $(
      `#showEntries${computationModelElementId} + .select2-container--default .select2-selection--single`
    ).css({ height: "1.8rem !important" });
    $(
      `#showEntries${computationModelElementId} + .select2-container .select2-selection__rendered`
    ).css({
      "line-height": "1.8rem !important",
      "text-overflow": "unset !important",
      "padding-left": "8% !important",
      "padding-right": "8% !important",
    });
    $(
      `#showEntries${computationModelElementId} + .select2-container--default .select2-selection--single .select2-selection__arrow`
    ).css({ height: "1.8rem !important", "padding-left": " 1.5rem" });

    $(`#${outputContainer}`).prepend(
      `<div>
                <button id='filter_button_run_computation${computationModelElementId}' data-elementID='${computationModelElementId}' class='btn btn-primary btn-md rounded'>Filter</button>
                <button id='freeze_button_run_computation${computationModelElementId}' data-elementID='${computationModelElementId}' class='btn btn-primary btn-md rounded' style='margin-left:10px;'>Freeze Panes</button>
                <button id='extractData_run_computation${computationModelElementId}' data-elementID='${computationModelElementId}' class='btn btn-primary btn-md rounded' style='margin-left:10px;'>Extract Data</button>
                <button id='columnVisibility_${computationModelElementId}' data-elementID='${computationModelElementId}' data-toggle='dropdown' class='btn btn-primary btn-md rounded' style='margin-left:10px;'>Column Visibility<i class='fa-solid fa-caret-down'></i></button>
                <div id='columnVisibilityDropdown${computationModelElementId}' class='dropdown-menu dropdown-menu-lg dropdown-menu-left data-table-column-visibility-dropdown' style='max-height: 30rem; min-width: 10em; border-radius: 1rem; overflow-y: auto; margin: 0px !important; padding-top: 0px !important; position: absolute; will-change: transform; top: 0px; left: 0px; transform: translate3d(1410px, 43px, 0px);' x-placement='bottom-start'>
                </div>
            </div>
            <br>`
    );

    $(`#${outputContainer}`).append(
      `<table class="row-border" id="runModelTable_${computationModelElementId}"><thead id="runModelTable_head_${computationModelElementId}"><tr></tr></thead><tfoot><tr></tr></tfoot><tbody id="runModelTable_body_${computationModelElementId}"></tbody></table>`
    );

    for (let key of data.columns_list) {
      $(`#runModelTable_${computationModelElementId}`)
        .find("thead tr")
        .eq(0)
        .append(`<th style="text-align:center;">${key}</th>`);
      $(`#runModelTable_${computationModelElementId}`)
        .find("tfoot tr")
        .eq(0)
        .append(
          `<th style="text-align:center; background-color:white;">${key}</th>`
        );
      $(`#condition_dropdown_run${computationModelElementId}`).append(
        `<li class="dropdown-item filter_btnRunModel${computationModelElementId}" name='${key}'>${key}</li>`
      );
      dataContainingColumnNamesRunModel.push({ data: key });
      redis_col.push(key);
    }

    $(`#extractData_run_computation${computationModelElementId}`).attr(
      "data-redis_cols",
      JSON.stringify(redis_col)
    );

    if (data.output_type === "Optimiser-output") {
      $(`#${outputContainer}`).empty();
      $(`#${outputContainer}`).append(`
                <div class="col-12">
                        <div class="card">
                            <div class="card-header" style="padding:0.3rem;background:whitesmoke;">
                                <h4 class="mb-0" style="text-align:center;">
                                Model Portfolio Allocation
                                </h4>
                            </div>
                            <div class="card-body" style="padding:0.9rem;">
                                <table id="exampledataResults_${computationModelElementId}" class="display compact" style="width:100%;">
                                    <thead>
                                        <tr></tr>
                                    </thead>
                                    <tbody>
                                    </tbody>
                                </table>
                            </div>
                        </div>
                </div>
                <div class="row" id="additionOutputOptimizer">
                </div>
                <div class="col-12">
                    <div class="card">
                        <div class="card-header" style="padding:0.3rem;background:whitesmoke;">
                            <h4 class="mb-0" style="text-align:center;">
                                Security Allocation
                            </h4>
                        </div>
                        <div class="card-body" style="padding:0.3rem;">
                            <br>
                            <div class = "row" style="margin-left:0.5rem;"><h6><span class="text-primary">Investment: </span><span style="background:whitesmoke;">₹ ${data.optimiser_output.investment_amount}</span><h6></div>
                            <div class = "row" style="margin-left:0.5rem;"><h6><span class="text-primary">Unallocated Investment: </span><span style="background:whitesmoke;">₹ ${data.optimiser_output.unallocated_investment_amount}</span></h6></div>
                            <br>
                            <table id="exampledataResults4_${computationModelElementId}" class="display compact" style="width:100%;margin-left:0.5rem;">
                                <thead>
                                    <tr></tr>
                                </thead>
                                <tbody>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            `);
      if (Object.keys(data.optimiser_output).includes("constraint_report")) {
        $("#additionOutputOptimizer").append(`
                <div class = "col-7">
                    <div class="card">
                        <div class="card-header" style="padding:0.3rem;background:whitesmoke;">
                            <h4 class="mb-0" style="text-align:center;">
                            Constraint Report
                            </h4>
                        </div>
                        <div class="card-body" style="padding:0.9rem;">
                            <table id="exampledataResults2_${computationModelElementId}" class="display compact" style="width:80%;">
                                <thead>
                                    <tr></tr>
                                </thead>
                                <tbody>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
                `);
      }
      if (Object.keys(data.optimiser_output).includes("efficient_frontier")) {
        $("#additionOutputOptimizer").append(`
                <div class = "col-5">
                    <div class="card">
                        <div class="card-header" style="padding:0.3rem;background:whitesmoke;">
                            <h4 class="mb-0" style="text-align:center;">
                            Efficient Frontier Curve
                            </h4>
                        </div>
                        <div class="card-body" style="padding:0.9rem;" id="optimizerEffContainer">

                        </div>
                    </div>
                </div>
                `);
      }
      for (
        var i = 0;
        i < data.optimiser_output.portfolio_allocation.length;
        i++
      ) {
        string = `<tr>`;
        for (let [key, value] of Object.entries(
          data.optimiser_output.portfolio_allocation[i]
        )) {
          string += `<td style="text-align:center;">${value}</td>`;
        }
        string += `</tr>`;
        $(`#exampledataResults_${computationModelElementId}`)
          .find("tbody")
          .append(string);
      }
      $(`#exampledataResults_${computationModelElementId} thead tr`).empty();
      for (let [key, value] of Object.entries(
        data.optimiser_output.portfolio_allocation[0]
      )) {
        $(`#exampledataResults_${computationModelElementId}`)
          .find("thead tr")
          .eq(0)
          .append(`<th style="text-align:center;">${key}</th>`);
      }
      for (
        var i = 0;
        i <
        data.optimiser_output.security_allocation_output[
          data.optimiser_output.security_allocation_output_headers[0]
        ].length;
        i++
      ) {
        string = `<tr>`;
        for (j in data.optimiser_output.security_allocation_output_headers) {
          string += `<td style="text-align:center;">${
            data.optimiser_output.security_allocation_output[
              data.optimiser_output.security_allocation_output_headers[j]
            ][i]
          }</td>`;
        }
        string += `</tr>`;
        $(`#exampledataResults4_${computationModelElementId}`)
          .find("tbody")
          .append(string);
      }
      $(`#exampledataResults4_${computationModelElementId} thead tr`).empty();
      for (j in data.optimiser_output.security_allocation_output_headers) {
        $(`#exampledataResults4_${computationModelElementId}`)
          .find("thead tr")
          .eq(0)
          .append(
            `<th style="text-align:center;">${data.optimiser_output.security_allocation_output_headers[j]}</th>`
          );
      }
      if (Object.keys(data.optimiser_output).includes("constraint_report")) {
        for (
          var i = 0;
          i < data.optimiser_output.constraint_report.length;
          i++
        ) {
          string = `<tr>`;
          for (let [key, value] of Object.entries(
            data.optimiser_output.constraint_report[i]
          )) {
            string += `<td style="text-align:center;">${value}</td>`;
          }
          string += `</tr>`;
          $(`#exampledataResults2_${computationModelElementId}`)
            .find("tbody")
            .append(string);
        }
        $(`#exampledataResults2_${computationModelElementId} thead tr`).empty();
        for (let [key, value] of Object.entries(
          data.optimiser_output.constraint_report[0]
        )) {
          $(`#exampledataResults2_${computationModelElementId}`)
            .find("thead tr")
            .eq(0)
            .append(`<th style="text-align:center;">${key}</th>`);
        }
      }

      if (Object.keys(data.optimiser_output).includes("efficient_frontier")) {
        $("#optimizerEffContainer").append(`
                    <div class="row">
                        <img
                        src="data:image/png;base64,${data.optimiser_output.efficient_frontier}"
                        width="450"
                        height="280"
                        alt="Efficient Frontier"
                        style="border:2px solid black;margin:auto;"
                        title="Efficient Frontier"
                        />
                    </div>
                `);
      }
      elementToShow.css("display", "block");
      elementToHide.css("display", "none");
      initialiseDataTable(`exampledataResults${computationModelElementId}`);
      initialiseDataTable(`exampledataResults2${computationModelElementId}`);
      initialiseDataTable(`exampledataResults4${computationModelElementId}`);
    }

    if (Object.keys(data).includes("output_source_file")) {
      let sourceOutputCode = data["output_source_file"];
      $(`#extractData_run_computation${computationModelElementId}`).attr(
        "data-elementid_redis",
        sourceOutputCode
      );
      let ajaxSource =
        window.location.pathname +
        "computation-server-side/" +
        sourceOutputCode +
        "--default";
      let tableId = `runModelTable_${computationModelElementId}`;
      let filterFormFields = data.form_fields;
      initialiseServerSideDataTable(
        tableId,
        computationModelElementId,
        ajaxSource,
        dataContainingColumnNamesRunModel,
        filterFormFields
      );
    }

    if (data.last_element_name === "Export Data") {
      let output_msg = "";
      if (data.extra_config) {
        for (let ii = 0; ii < data.extra_config.length; ii++) {
          for (let [key, value] of Object.entries(data.extra_config[ii])) {
            output_msg = output_msg + ". " + value.output_msg;
          }
        }
      }
      if (output_msg) {
        Swal.fire({ icon: "info", text: output_msg });
      }
    }
    $(`#freeze_button_run_computation${computationModelElementId}`)
      .off("click")
      .on("click", function () {
        $(".freezerunCheckbox").prop("checked", false);
        $(`#freezeRunCard_computation${computationModelElementId}`).modal(
          "show"
        );
      });
    $(`#extractData_run_computation${computationModelElementId}`)
      .off("click")
      .on("click", function () {
        let elementID = $(this).attr("data-elementid_redis");
        let redis_cols = $(this).attr("data-redis_cols");
        if (redis_cols != undefined) {
          redis_cols = JSON.parse(redis_cols);
        } else {
          redis_cols = [];
        }
        $(`#btn_exDataDownload${computationModelElementId}`).attr(
          "data-elementid_redis",
          elementID
        );
        $(`#exDataColumn1${computationModelElementId}`)
          .val("")
          .trigger("change");

        $(`#exDataColumn1${computationModelElementId}`).empty();
        for (let i = 0; i < redis_cols.length; i++) {
          if (redis_cols[i] != "index") {
            $(`#exDataColumn1${computationModelElementId}`).append(
              new Option(redis_cols[i], redis_cols[i])
            );
          }
        }
        $(`#exData_comp_modal${computationModelElementId}`).modal("show");
      });
  }
}
