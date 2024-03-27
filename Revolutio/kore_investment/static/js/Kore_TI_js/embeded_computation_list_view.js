import { initialise_table_results_5,
    displayTabularOutput,
     trainEWMARun,
     displayResultsBacktest,
     displayOutputCopulaFunc,
     portfolio_valuation_output,
     trainGARCHModel,
     trainARIMARun,
     analyseTSData,
     displayBootStrapOptimizer,
     initialise_table_results_4,
     displayResultsOptimizer,
     initialise_table_results_3,
     initialise_table_results_2,
     initialiseTableResults,
     displayResultsFinInstrument,
     displayOutputLogReg,
     displayOutputLinReg,
     displayOutputFitTest,
     displayOutputFitDiscrete,
     initialise_table,
     displayOutputDecTree,
     datatablesFuncAvsP,
     datatablesFunc,
     displayOutputAB } from './embeded_computation.min.js';
function listViewRunComputation(obj){
    var savedhtml = $(obj).html()
    if ($(obj).parent().find('select').val()==null){
        Swal.fire({icon: 'warning',text: "Select the Computation Model."});
    }else{
        var table = $(obj).parent().parent().parent().parent()
        var elementId = $(table).attr('id').replace('example1','')
        var lengthOfrow = $(table).find('thead').find('tr').find('th').children().length
        var attrData = $(obj).attr('data-list')
        if (attrData == ''|| attrData =='{}'){

        }else{
            var parsedAttrdata = JSON.parse(attrData)
            var computeModel = $(obj).parent().find('select').val()
            var compModelName = computeModel
            var listOfInputs = []
            var allOkFlag = 0
                for (let y in parsedAttrdata[computeModel]){
                    var tableName = y
                    for (let o in parsedAttrdata[computeModel][y][0]){
                        for (let k = 0; k < lengthOfrow; k++){
                            if  ($(table).find('thead').find('tr').find('th').children().eq(k).html().toLowerCase() == parsedAttrdata[computeModel][y][0][o].toLowerCase()){
                                listOfInputs.push({[k]:parsedAttrdata[computeModel][y][0][o]})
                                break;
                            }
                        }
                    }
                }
                var valuesDic = {}
                for (let l in listOfInputs){
                    if ($(obj).parent().parent().find('td').eq(parseInt(Object.keys(listOfInputs[l]).toString())).find('div').length > 0){
                        var value =  $(obj).parent().parent().find('td').eq(parseInt(Object.keys(listOfInputs[l]).toString())).find('div').text()
                    }else{
                        var value = $(obj).parent().parent().find('td').eq(parseInt(Object.keys(listOfInputs[l]).toString())).text()
                    }
                    var columnName = Object.values(listOfInputs[l]).toString()
                    if (value == '-'){

                        allOkFlag = 1
                    }else{
                        valuesDic[columnName] = value
                    }
                }
                if (allOkFlag == 0){
                    $(obj).html(`<i class="fa fa-circle-notch fa-spin"></i>`)
                    $.ajax({
                        url: `/users/${urlPath}/dynamicVal/`,
                        data: {
                        operation: `calculate_embeded_computation_list_view`,
                        values_dic: JSON.stringify(valuesDic),
                        table_name: JSON.stringify(tableName),
                        compModelName:JSON.stringify(compModelName),
                        target_dic:JSON.stringify(parsedAttrdata[computeModel][tableName][1]),
                        },
                        type: 'POST',
                        dataType: 'json',
                        success: function (output) {
                            var context = output['context']
                            var targetfields = output['target']

                                if (parsedAttrdata[computeModel][tableName][2] =='full_output'){
                                    if (context.error_msg =='no'){
                                        var data = context.data
                                        if (data.element_error_message == 'Success') {
                                            if (data.output_display_type === 'individual') {
                                                if (data.name != "Export Data") {
                                                    if (data.name === "Logistic Regression") {
                                                        $(`#embededComputationlistViewBody_${elementId}`).empty();
                                                        displayOutputLogReg(data.content,`#embededComputationlistViewBody_${elementId}`,`#embededComputationlistView_${elementId}`);
                                                        $(`#embededComputationlistView_${elementId}`).modal('show');
                                                    } else if (data.name === "Linear Regression") {
                                                        $(`#embededComputationlistViewBody_${elementId}`).empty();
                                                        displayOutputLinReg(data.content,`#embededComputationlistViewBody_${elementId}`,`#embededComputationlistView_${elementId}`);
                                                        $(`#embededComputationlistView_${elementId}`).modal('show');
                                                        initialise_table('#table_ActualVFittedLinReg');
                                                    } else if (data.name === "Goodness Of Fit Test") {
                                                        displayOutputFitTest(data.content,`#embededComputationlistViewBody_${elementId}`,0,`#embededComputationlistView_${elementId}`)
                                                        $(`#embededComputationlistView_${elementId}`).modal('show');
                                                    } else if(data.name == "Fit Discrete"){
                                                        displayOutputFitDiscrete(data.content,`#embededComputationlistViewBody_${elementId}`,0,`#embededComputationlistView_${elementId}`)
                                                        $(`#embededComputationlistView_${elementId}`).modal('show');
                                                    } else if (data.name === "CART" || data.name == "CART Algorithm") {
                                                        $(`#embededComputationlistViewBody_${elementId}`).css('height','640px');
                                                        $(`#embededComputationlistViewBody_${elementId}`).empty();
                                                        displayOutputDecTree(data.content,`#embededComputationlistViewBody_${elementId}`,`#embededComputationlistView_${elementId}`);
                                                        $(`#embededComputationlistView_${elementId}`).modal('show');
                                                        setTimeout(() => {
                                                            $('#actual_grid').DataTable().columns.adjust()
                                                            $('#table_confusionMatrixDecTree').DataTable().columns.adjust()
                                                            $('#table_classReportDecTree').DataTable().columns.adjust()
                                                            $('#tableParameters').DataTable().columns.adjust()
                                                        },500)
                                                    } else if (data.name == "Boosting Algorithm") {
                                                        $(`#embededComputationlistViewBody_${elementId}`).css('height','640px');
                                                        $(`#embededComputationlistViewBody_${elementId}`).empty();
                                                        displayOutputAB(data.content,true,`#embededComputationlistViewBody_${elementId}`,`#embededComputationlistView_${elementId}`);
                                                        $(`#embededComputationlistView_${elementId}`).modal('show');
                                                        setTimeout(() => {
                                                            $('#actual_grid_ba').DataTable().columns.adjust()
                                                            $('#actual_grid').DataTable().columns.adjust()
                                                            $('#table_confusionMatrixDecTree').DataTable().columns.adjust()
                                                            $('#table_classReportDecTree').DataTable().columns.adjust()
                                                            $('#tableParameters').DataTable().columns.adjust()
                                                        },500)
                                                    }
                                                    else if (data.name === "Interest Rate Products" || data.name === "Equities" || data.name === "Mutual Fund") {
                                                        displayResultsFinInstrument(data.content,`#embededComputationlistViewBody_${elementId}`,`#embededComputationlistView_${elementId}`);
                                                        $(`#embededComputationlistView_${elementId}`).modal('show');
                                                        initialiseTableResults()
                                                        initialise_table_results_2()
                                                        initialise_table_results_3()
                                                    } else if (data.name === "Optimiser") {
                                                        displayResultsOptimizer(data.content,`#embededComputationlistViewBody_${elementId}`,0,`#embededComputationlistView_${elementId}`);
                                                        $(`#embededComputationlistView_${elementId}`).modal('show');
                                                        initialiseTableResults()
                                                        initialise_table_results_2()
                                                        initialise_table_results_4()
                                                    }
                                                    else if (data.name === "IR Curve Bootstrapping") {
                                                        displayBootStrapOptimizer(data.content,`#embededComputationlistViewBody_${elementId}`,0,`#embededComputationlistView_${elementId}`);
                                                        $(`#embededComputationlistView_${elementId}`).modal('show');
                                                        initialiseTableResults()
                                                    }
                                                    else if (data.name == "Analyse Time Series Data"){
                                                        if(data.existing_configuration == "No"){
                                                            $(`#embededComputationlistViewBody_${elementId}`).empty()
                                                            $(`#embededComputationlistViewBody_${elementId}`).append(`
                                                            <p style="color:red;margin-left:0.5rem;">Run failed. Please save the configuration.</p>
                                                            `)
                                                            $(`#embededComputationlistView_${elementId}`).modal('show')
                                                        }
                                                        else{
                                                            analyseTSData(data.content,`#embededComputationlistViewBody_${elementId}`,`#embededComputationlistView_${elementId}`)
                                                        }
                                                    }
                                                    else if (data.name == "Train an ARIMA Model"){
                                                        if(data.content.existing_configuration == "No"){
                                                            $(`#embededComputationlistViewBody_${elementId}`).empty()
                                                            $(`#embededComputationlistViewBody_${elementId}`).append(`
                                                            <p style="color:red;margin-left:0.5rem;">Run failed. Please save the configuration.</p>
                                                            `)
                                                            $(`#embededComputationlistView_${elementId}`).modal('show')
                                                        }
                                                        else{
                                                            trainARIMARun(data.content,`#embededComputationlistViewBody_${elementId}`,`#embededComputationlistView_${elementId}`)
                                                        }
                                                    }
                                                    else if (data.name == "Train a GARCH Model"){
                                                        if(data.content.existing_configuration == "No"){
                                                            $(`#embededComputationlistViewBody_${elementId}`).empty()
                                                            $(`#embededComputationlistViewBody_${elementId}`).append(`
                                                            <p style="color:red;margin-left:0.5rem;">Run failed. Please save the configuration.</p>
                                                            `)
                                                            $(`#embededComputationlistView_${elementId}`).modal('show')
                                                        }
                                                        else{

                                                            trainGARCHModel(data.content,`#embededComputationlistViewBody_${elementId}`,`#embededComputationlistView_${elementId}`)
                                                        }
                                                    }
                                                    else if (data.name == "Portfolio Valuation"){
                                                        portfolio_valuation_output(data.content,`#embededComputationlistViewBody_${elementId}`,`#embededComputationlistView_${elementId}`)
                                                    }

                                                    else if (data.name === "Copula") {
                                                        displayOutputCopulaFunc(data.content,`#embededComputationlistViewBody_${elementId}`,0,`#embededComputationlistView_${elementId}`);
                                                        $(`#embededComputationlistView_${elementId}`).modal('show')
                                                    }
                                                    else if (data.name === "VaR Backtesting") {
                                                        displayResultsBacktest(data.content,`#embededComputationlistViewBody_${elementId}`,0,`#embededComputationlistView_${elementId}`)
                                                        $(`#embededComputationlistView_${elementId}`).modal('show')
                                                        initialiseTableResults()
                                                    }
                                                    else if (data.name == "Train an EWMA Model"){
                                                        if(data.content.existing_configuration == "No"){
                                                            $(`#embededComputationlistViewBody_${elementId}`).empty()
                                                            $(`#embededComputationlistViewBody_${elementId}`).append(`
                                                            <p style="color:red;margin-left:0.5rem;">Run failed. Please save the configuration.</p>
                                                            `)
                                                            $(`#embededComputationlistView_${elementId}`).modal('show')
                                                        }
                                                        else{
                                                            trainEWMARun(data.content,`#embededComputationlistViewBody_${elementId}`,`#embededComputationlistView_${elementId}`)
                                                        }
                                                    }
                                                    else {
                                                        displayTabularOutput(data.content,`#embededComputationlistViewBody_${elementId}`,`#embededComputationlistView_${elementId}`);
                                                    };
                                                }
                                            }
                                        } else {
                                            Swal.fire({icon: 'error',text: data.element_error_message});
                                        }
                                    }else{
                                        var error = context.e_list.slice(-1)
                                        Swal.fire({icon: 'error',text: error});

                                    }
                                }else{
                                    if (context.error_msg =='no'){
                                    var data = context.data.content
                                    var listOftarget = []
                                    for (let o in parsedAttrdata[computeModel][tableName][1]){
                                        for (let k = 0; k < lengthOfrow; k++){
                                            if  ($(table).find('thead').find('tr').find('th').children().eq(k).html().toLowerCase() == parsedAttrdata[computeModel][tableName][1][o].toLowerCase()){
                                                listOftarget.push({[k]:parsedAttrdata[computeModel][tableName][1][o]})
                                            }
                                        }

                                    }
                                    var final = {}
                                    for (let i in listOftarget){
                                        for (let k in listOftarget[i]){
                                            for (let y in targetfields){
                                                if (listOftarget[i][k]==targetfields[y]){
                                                    final[k] = y
                                                }
                                            }
                                        }
                                    }
                                    for (let i in final){
                                        for (let y in data[0]){
                                            if (final[i] == y){
                                                if ($(obj).closest('tr').find('td').eq(i).find('div').length>0){
                                                    $(obj).closest('tr').find('td').eq(i).find('div').html(data[0][y])
                                                }else{
                                                    $(obj).closest('tr').find('td').eq(i).html(data[0][y])
                                                }

                                            }
                                        }
                                    }

                                }else{
                                    var error = context.e_list.slice(-1)
                                    Swal.fire({icon: 'error',text: error});

                                }
                                }
                        $(obj).html(savedhtml)
                        },error: function () {
                            $(obj).html(savedhtml)
                            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                    },
                    })
                }else{
                    $(obj).html(savedhtml)
                    Swal.fire({icon: 'error',text: 'Error! Input fields are empty. Please try again.'});
                }
            }

    }
  }
  function listViewRunComputationMultiple(obj){
    var savedhtml = $(obj).html()
    if ($(obj).parent().find('select').val()==null){
        window.alert('Select the computation Model')
    }else{
        var table = $(obj).parent().parent().parent().parent()
        var elementId = $(table).attr('id').replace('example1','')
        var lengthOfrow = $(table).find('thead').find('tr').find('th').children().length
        var attrData = $(obj).attr('data-list')
        if (attrData == ''|| attrData =='{}'){

        }else{
            var parsedAttrdata = JSON.parse(attrData)
            var computeModel = $(obj).parent().find('select').val()
            var compModelName = computeModel
            var listOfInputs = []
            var allOkFlag = 0
            for (let i in parsedAttrdata){
                for (let y in parsedAttrdata[i][computeModel]){
                    var tableName = y
                    for (let o in parsedAttrdata[i][computeModel][y][0]){
                        for (let k = 0; k < lengthOfrow; k++){
                            if  ($(table).find('thead').find('tr').find('th').children().eq(k).html() == parsedAttrdata[i][computeModel][y][0][o]){
                                listOfInputs.push({[k]:parsedAttrdata[i][computeModel][y][0][o]})
                            }
                        }

                    }
                    var target_inputs = parsedAttrdata[i][computeModel][y][1]
                }
            }
                var valuesDic = {}
                for (let l in listOfInputs){
                    var value = $(obj).parent().parent().find('td').eq(parseInt(Object.keys(listOfInputs[l]).toString())).children().html()
                    var columnName = Object.values(listOfInputs[l]).toString()
                    if (value == '-'){

                        allOkFlag = 1
                    }else{
                        valuesDic[columnName] = value
                    }

                }
                if (allOkFlag == 0){
                    $(obj).html(`<i class="fa fa-circle-notch fa-spin"></i>`)
                    $.ajax({
                        url: `/users/${urlPath}/dynamicVal/`,
                        data: {
                        operation: `calculate_embeded_computation_list_view`,
                        values_dic: JSON.stringify(valuesDic),
                        table_name: JSON.stringify(tableName),
                        compModelName:JSON.stringify(compModelName),
                        target_dic:JSON.stringify(target_inputs),
                        },
                        type: 'POST',
                        dataType: 'json',
                        success: function (output) {
                            var context = output['context']
                            var targetfields = output['target']
                            for (let t in parsedAttrdata){
                                if (parsedAttrdata[t][computeModel] != undefined){
                                if (parsedAttrdata[t][computeModel][tableName][2] =='full_output'){
                                    if (context.error_msg =='no'){
                                        var data = context.data
                                        if (data.element_error_message == 'Success') {
                                            if (data.output_display_type === 'individual') {
                                                if (data.name != "Export Data") {
                                                    if (data.name === "Logistic Regression") {
                                                        $(`#embededComputationlistViewBodyMultiple_${elementId}`).empty();
                                                        displayOutputLogReg(data.content,`#embededComputationlistViewBodyMultiple_${elementId}`,`#embededComputationlistViewMultiple_${elementId}`);
                                                        $(`#embededComputationlistViewMultiple_${elementId}`).modal('show');
                                                    } else if (data.name === "Linear Regression") {
                                                        $(`#embededComputationlistViewBodyMultiple_${elementId}`).empty();
                                                        displayOutputLinReg(data.content,`#embededComputationlistViewBodyMultiple_${elementId}`,`#embededComputationlistViewMultiple_${elementId}`);
                                                        $(`#embededComputationlistViewMultiple_${elementId}`).modal('show');
                                                        initialise_table('#table_ActualVFittedLinReg');
                                                    } else if (data.name === "Goodness Of Fit Test") {
                                                        displayOutputFitTest(data.content,`#embededComputationlistViewBodyMultiple_${elementId}`,0,`#embededComputationlistViewMultiple_${elementId}`)
                                                        $(`#embededComputationlistViewMultiple_${elementId}`).modal('show');
                                                    } else if(data.name == "Fit Discrete"){
                                                        displayOutputFitDiscrete(data.content,`#embededComputationlistViewBodyMultiple_${elementId}`,0,`#embededComputationlistViewMultiple_${elementId}`)
                                                        $(`#embededComputationlistViewMultiple_${elementId}`).modal('show');
                                                    } else if (data.name === "CART" || data.name == "CART Algorithm") {
                                                        $(`#embededComputationlistViewBodyMultiple_${elementId}`).css('height','640px');
                                                        $(`#embededComputationlistViewBodyMultiple_${elementId}`).empty();
                                                        displayOutputDecTree(data.content,`#embededComputationlistViewBodyMultiple_${elementId}`,`#embededComputationlistViewMultiple_${elementId}`);
                                                        $(`#embededComputationlistViewMultiple_${elementId}`).modal('show');
                                                        setTimeout(() => {
                                                            $('#actual_grid').DataTable().columns.adjust()
                                                            $('#table_confusionMatrixDecTree').DataTable().columns.adjust()
                                                            $('#table_classReportDecTree').DataTable().columns.adjust()
                                                            $('#tableParameters').DataTable().columns.adjust()
                                                        },500)
                                                    } else if (data.name == "Boosting Algorithm") {
                                                        $(`#embededComputationlistViewBodyMultiple_${elementId}`).css('height','640px');
                                                        $(`#embededComputationlistViewBodyMultiple_${elementId}`).empty();
                                                        displayOutputAB(data.content,true,`#embededComputationlistViewBodyMultiple_${elementId}`,`#embededComputationlistViewMultiple_${elementId}`);
                                                        $(`#embededComputationlistViewMultiple_${elementId}`).modal('show');
                                                        setTimeout(() => {
                                                            $('#actual_grid_ba').DataTable().columns.adjust()
                                                            $('#actual_grid').DataTable().columns.adjust()
                                                            $('#table_confusionMatrixDecTree').DataTable().columns.adjust()
                                                            $('#table_classReportDecTree').DataTable().columns.adjust()
                                                            $('#tableParameters').DataTable().columns.adjust()
                                                        },500)
                                                    }
                                                    else if (data.name === "Interest Rate Products" || data.name === "Equities" || data.name === "Mutual Fund") {
                                                        displayResultsFinInstrument(data.content,`#embededComputationlistViewBodyMultiple_${elementId}`,`#embededComputationlistViewMultiple_${elementId}`);
                                                        $(`#embededComputationlistViewMultiple_${elementId}`).modal('show');
                                                        initialiseTableResults()
                                                        initialise_table_results_2()
                                                        initialise_table_results_3()
                                                    } else if (data.name === "Optimiser") {
                                                        displayResultsOptimizer(data.content,`#embededComputationlistViewBodyMultiple_${elementId}`,0,`#embededComputationlistViewMultiple_${elementId}`);
                                                        $(`#embededComputationlistViewMultiple_${elementId}`).modal('show');
                                                        initialiseTableResults()
                                                        initialise_table_results_2()
                                                        initialise_table_results_4()
                                                    }
                                                    else if (data.name === "IR Curve Bootstrapping") {
                                                        displayBootStrapOptimizer(data.content,`#embededComputationlistViewBodyMultiple_${elementId}`,0,`#embededComputationlistViewMultiple_${elementId}`);
                                                        $(`#embededComputationlistViewMultiple_${elementId}`).modal('show');
                                                        initialiseTableResults()
                                                    }
                                                    else if (data.name == "Analyse Time Series Data"){
                                                        if(data.existing_configuration == "No"){
                                                            $(`#embededComputationlistViewBodyMultiple_${elementId}`).empty()
                                                            $(`#embededComputationlistViewBodyMultiple_${elementId}`).append(`
                                                            <p style="color:red;margin-left:0.5rem;">Run failed. Please save the configuration.</p>
                                                            `)
                                                            $(`#embededComputationlistViewMultiple_${elementId}`).modal('show')
                                                        }
                                                        else{
                                                            analyseTSData(data.content,`#embededComputationlistViewBodyMultiple_${elementId}`,`#embededComputationlistViewMultiple_${elementId}`)
                                                        }
                                                    }
                                                    else if (data.name == "Train an ARIMA Model"){
                                                        if(data.content.existing_configuration == "No"){
                                                            $(`#embededComputationlistViewBodyMultiple_${elementId}`).empty()
                                                            $(`#embededComputationlistViewBodyMultiple_${elementId}`).append(`
                                                            <p style="color:red;margin-left:0.5rem;">Run failed. Please save the configuration.</p>
                                                            `)
                                                            $(`#embededComputationlistViewMultiple_${elementId}`).modal('show')
                                                        }
                                                        else{
                                                            trainARIMARun(data.content,`#embededComputationlistViewBodyMultiple_${elementId}`,`#embededComputationlistViewMultiple_${elementId}`)
                                                        }
                                                    }
                                                    else if (data.name == "Train a GARCH Model"){
                                                        if(data.content.existing_configuration == "No"){
                                                            $(`#embededComputationlistViewBodyMultiple_${elementId}`).empty()
                                                            $(`#embededComputationlistViewBodyMultiple_${elementId}`).append(`
                                                            <p style="color:red;margin-left:0.5rem;">Run failed. Please save the configuration.</p>
                                                            `)
                                                            $(`#embededComputationlistViewMultiple_${elementId}`).modal('show')
                                                        }
                                                        else{

                                                            trainGARCHModel(data.content,`#embededComputationlistViewBodyMultiple_${elementId}`,`#embededComputationlistViewMultiple_${elementId}`)
                                                        }
                                                    }
                                                    else if (data.name == "Portfolio Valuation"){
                                                        portfolio_valuation_output(data.content,`#embededComputationlistViewBodyMultiple_${elementId}`,`#embededComputationlistViewMultiple_${elementId}`)
                                                    }

                                                    else if (data.name === "Copula") {
                                                        displayOutputCopulaFunc(data.content,`#embededComputationlistViewBodyMultiple_${elementId}`,0,`#embededComputationlistViewMultiple_${elementId}`);
                                                        $(`#embededComputationlistViewMultiple_${elementId}`).modal('show')
                                                    }
                                                    else if (data.name === "VaR Backtesting") {
                                                        displayResultsBacktest(data.content,`#embededComputationlistViewBodyMultiple_${elementId}`,0,`#embededComputationlistViewMultiple_${elementId}`)
                                                        $(`#embededComputationlistViewMultiple_${elementId}`).modal('show')
                                                        initialiseTableResults()
                                                    }
                                                    else if (data.name == "Train an EWMA Model"){
                                                        if(data.content.existing_configuration == "No"){
                                                            $(`#embededComputationlistViewBodyMultiple_${elementId}`).empty()
                                                            $(`#embededComputationlistViewBodyMultiple_${elementId}`).append(`
                                                            <p style="color:red;margin-left:0.5rem;">Run failed. Please save the configuration.</p>
                                                            `)
                                                            $(`#embededComputationlistViewMultiple_${elementId}`).modal('show')
                                                        }
                                                        else{
                                                            trainEWMARun(data.content,`#embededComputationlistViewBodyMultiple_${elementId}`,`#embededComputationlistViewMultiple_${elementId}`)
                                                        }
                                                    }
                                                    else {
                                                        displayTabularOutput(data.content,`#embededComputationlistViewBodyMultiple_${elementId}`,`#embededComputationlistViewMultiple_${elementId}`);
                                                    };
                                                }
                                            }
                                        } else {
                                            alert(data.element_error_message);
                                        }
                                    }else{
                                        var error = context.e_list.slice(-1)
                                        window.alert(
                                        error
                                        )

                                    }
                                }else{
                                    if (context.error_msg =='no'){
                                    var data = context.data.content
                                    var listOftarget = []
                                    for (let o in parsedAttrdata[t][computeModel][tableName][1]){
                                        for (let k = 0; k < lengthOfrow; k++){
                                            if  ($(table).find('thead').find('tr').find('th').children().eq(k).html() == parsedAttrdata[t][computeModel][tableName][1][o]){
                                                listOftarget.push({[k]:parsedAttrdata[t][computeModel][tableName][1][o]})
                                            }
                                        }

                                    }
                                    var final = {}
                                    for (let i in listOftarget){
                                        for (let k in listOftarget[i]){
                                            for (let y in targetfields){
                                                if (listOftarget[i][k]==targetfields[y]){
                                                    final[k] = y
                                                }
                                            }
                                        }
                                    }
                                    for (let i in final){
                                        for (let y in data[0]){
                                            if (final[i] == y){
                                                if ($(obj).closest('tr').find('td').eq(i).find('div').length>0){
                                                    $(obj).closest('tr').find('td').eq(i).find('div').html(data[0][y])
                                                }else{
                                                    $(obj).closest('tr').find('td').eq(i).html(data[0][y])
                                                }
                                            }
                                        }
                                    }

                                }else{
                                    var error = context.e_list.slice(-1)
                                    window.alert(
                                    error
                                    )

                                }
                                }
                            }
                            }
                        $(obj).html(savedhtml)
                        },error: function () {
                            $(obj).html(savedhtml)
                    window.alert('Error')
                    },
                    })
                }else{
                    $(obj).html(savedhtml)
                    window.alert('Error Input fields are empty !')
                }
            }

    }
  }
  window.listViewRunComputation = listViewRunComputation;
  window.listViewRunComputationMultiple =listViewRunComputationMultiple;