function initialise_table_results_5(tableID){
    var data_table = $(`#${tableID}`).DataTable({
    "autoWidth": false,
    "scrollY": "35vh",
    "scrollX": "100%",
    "scrollCollapse": true,
    "sScrollXInner": "100%",
    "ordering":false,
    orderCellsTop: true,
    responsive: true,
    colReorder: {
    fixedColumnsLeft: 1
    },
    stateSave: true,
    "deferRender": true,
    "paging": true,
    "lengthMenu": [[1, 5, 50, -1], [1, 5, 50, "All"]],
    stripeClasses: false,
    "pageLength": 50,
    dom: 'lfBrtip',
    buttons: [
        {
            extend: 'collection',
            text: 'Export',
            buttons: [
                {
                extend: 'copy', title: '', exportOptions: {
                    columns: ':visible:not(.noVis)'
                }
                },
                {
                extend: 'excel', title: '', exportOptions: {
                    columns: ':visible:not(.noVis)'
                }
                },
                {
                extend: 'csv', title: '', exportOptions: {
                    columns: ':visible:not(.noVis)'
                }
                },
                {
                extend: 'pdf', title: '', exportOptions: {
                    columns: ':visible:not(.noVis)'
                }
                },
            ],
        },
        {
            extend: 'colvis',
            className: "scroller",
        }
    ],
    columnDefs: [
        {
            targets: "_all",
            className: 'dt-center allColumnClass all'
        },
    ],
    });
}

function displayTabularOutput(data,body,modal) {
    $(body).empty();
    $(body).append(
        `
        <table id="exampledata" class="display compact" style="width:100%;" data-parent_group_no="g3">
            <thead>
                <tr>
                </tr>
            </thead>
            <tbody>
            </tbody>
        </table>
        `
    )

    for (var i = 0; i < data.length; i++) {
        var string=`<tr>`
        for(let [key,value] of Object.entries(data[i]) ){
            string+=`<td>${value}</td>`
            }
        string+=`</tr>`
        $('#exampledata').find('tbody').append(string)
    }
    for(let [key,value] of Object.entries(data[0]) ){
        $(`#exampledata`).find('thead tr').eq(0).append(`<th>${key}</th>`)
    }
    $(modal).modal("show");
    initialise_table_results_5("exampledata");
}


function trainEWMARun(data,body,modal){
    $(body).empty()
    $(body).append(
        `<div class="row">
            <div class="col-6">
                <div class="card">
                    ${data.summary}
                </div>
                <div class="card">
                    <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke;">
                        <h2 class="mb-0 timeSeriesHeaders" style="text-align:center;">
                        Actual vs Predicted - Table
                        </h2>
                    </div>
                    <div class="card-body" style="padding:0.9rem;">
                        <table id="exampledataResults" class="display compact" style="width:100%;">
                            <thead>
                                <tr></tr>
                            </thead>
                            <tbody>
                            </tbody>
                        </table>
                    </div>
                </div>
                <div class="card">
                    <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke">
                        <h2 class="mb-0 timeSeriesHeaders" style="text-align:center;">
                            Augmented Dickey Fuller Test For Stationarity
                        </h2>
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
            </div>
            <div class="col-6">
                <div class="card">
                    <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke">
                        <h2 class="mb-0 timeSeriesHeaders" style="text-align:center;">
                            Model Analysis
                        </h2>
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
                            <p style="margin-left:22.5%"><strong>Mean Squared Error (MSE) </strong> = ${data.mse}.</p>
                        </div>
                    </div>
                </div>
                <div class="card">
                    <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke">
                        <h2 class="mb-0 timeSeriesHeaders" style="text-align:center;">
                            Jarque-Bera Test For Normality
                        </h2>
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
        </div>`
    )
    $('.simpletable').each(function(){
        $(this).attr('class','table table-bordered table-sm')
        $(this).find("th").each(function(){
            $(this).css('text-align','center')
        })
        $(this).find("td").each(function(){
            $(this).css('text-align','center')
        })
    })
    for (var i = 0; i < data.table[data.table_headers[0]].length; i++) {
        var string=`<tr>`
        for(j in data.table_headers){
            string+=`<td style="text-align:center;">${data.table[data.table_headers[j]][i]}</td>`
        }
        string+=`</tr>`
        $('#exampledataResults').find('tbody').append(string)
        }

    $("#exampledataResults thead tr").empty()
    $("#thid").css("display","none")
    for(j in data.table_headers){
        $(`#exampledataResults`).find('thead tr').eq(0).append(`<th style="text-align:center;">${data.table_headers[j]}</th>`)
    }
    $(modal).modal('show')
    initialiseTableResults()
}



function displayResultsBacktest(data, body, run,modal) {
    $(body).empty()
    if (run===0) {
        var acttable = "acttable";
        var hyptable = "hyptable";
        var actdf = 'actdf';
        var hypdf = 'hypdf';
    } else {
        var acttable = `acttable_${run}`;
        var hyptable = `hyptable_${run}`;
        var actdf = `actdf_${run}`;
        var hypdf = `hypdf_${run}`;
    }

    $(body).append(`
    <div class='row'>
      <div class="col-6">
              <div class="card" style='height:400px;width:100%;'>
                  <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke;">
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
                  <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke;">
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
                  <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke;">
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
                  <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke;">
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
    `)

    for (var i = 0; i < data.Actual_D.length; i++) {
        var string=`<tr>`
        for(let [key,value] of Object.entries(data.Actual_D[i]) ){
          string+=`<td style="text-align:center;padding:5px;">${value}</td>`
          }
        string+=`</tr>`
        $(`#${actdf}`).find('tbody').append(string)
    }
    $(`#${actdf} thead tr`).empty()
    for(let [key,value] of Object.entries(data.Actual_D[0]) ){
        $(`#${actdf}`).find('thead tr').eq(0).append(`<th style="text-align:center;padding:5px;">${key}</th>`)
    }

    for (var i = 0; i < data.Hyp_D.length; i++) {
        var string=`<tr>`
        for(let [key,value] of Object.entries(data.Hyp_D[i]) ){
          string+=`<td style="text-align:center;padding:5px;">${value}</td>`
          }
        string+=`</tr>`
        $(`#${hypdf}`).find('tbody').append(string)
    }
    $(`#${hypdf} thead tr`).empty()
    for(let [key,value] of Object.entries(data.Hyp_D[0]) ){
        $(`#${hypdf}`).find('thead tr').eq(0).append(`<th style="text-align:center;padding:5px;">${key}</th>`)
    }

    for (var i = 0; i < data.Actual_R.length; i++) {
        var string=`<tr>`
        for(let [key,value] of Object.entries(data.Actual_R[i]) ){
            if (value === 'Low Risk'){
              string+=`<td style="text-align:center;background-color:#98FB98">${value}</td>`
            }
            else if (value === 'Medium Risk') {
              string+=`<td style="text-align:center; background-color:#F0E68C">${value}</td>`
            }
            else if (value === 'High Risk') {
              string+=`<td style="text-align:center; background-color:#FA8072">${value}</td>`
            }
            else {
              string+=`<td style="text-align:center;">${value}</td>`
            }
          }
        string+=`</tr>`
        $(`#${acttable}`).find('tbody').append(string)
    }

    for (var i = 0; i < data.Hyp_R.length; i++) {
        var string=`<tr>`
        for(let [key,value] of Object.entries(data.Hyp_R[i]) ){
            if (value === 'Low Risk'){
              string+=`<td style="text-align:center; background-color:#98FB98">${value}</td>`
            }
            else if (value === 'Medium Risk') {
              string+=`<td style="text-align:center; background-color:#F0E68C">${value}</td>`
            }
            else if (value === 'High Risk') {
              string+=`<td style="text-align:center; background-color:#FA8072">${value}</td>`
            }
            else {
              string+=`<td style="text-align:center;">${value}</td>`
            }
          }
        string+=`</tr>`
        $(`#${hyptable}`).find('tbody').append(string)
    }
}


function displayOutputCopulaFunc(data,body, run,modal){
    $(body).empty()
    if (run===0) {
        var simulated_val = "simulated_val";
        var correlation_matrix = "correlation_matrix";
        var varTable = "varTable";
    } else {
        var simulated_val = `simulated_val_${run}`;
        var correlation_matrix = `correlation_matrix_${run}`;
        var varTable = `varTable_${run}`;
    }
    let data_dict = JSON.parse(data.content)

    let data_corr = data_dict.Correlation_matrix
    let  data_sim =data_dict.Simulated_data
    let data_var = data_dict.VaR_data

    $(body).append(`
    <div class='row' style='display:flex;height:30rem;'>
        <div class="card col-6" style='padding:5px;'>
            <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke;">
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
            <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke;">
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
    `)

    $(`#${correlation_matrix} thead tr`).empty()
    for(let [key,value] of Object.entries(data_corr[0]) ){
        $(`#${correlation_matrix}`).find('thead tr').eq(0).append(`<th style="text-align:center;">${key}</th>`)
    }
    for (var i = 0; i < data_corr.length; i++) {
        var string=`<tr>`
        for(let [key,value] of Object.entries(data_corr[i]) ){
            string+=`<td style="text-align:center;">${value}</td>`
            }
        string+=`</tr>`
        $(`#${correlation_matrix}`).find('tbody').append(string)
    }

    $(`#${simulated_val} thead tr`).empty()
    for(let [key,value] of Object.entries(data_sim[0]) ){
        $(`#${simulated_val}`).find('thead tr').eq(0).append(`<th style="text-align:center;">${key}</th>`)
    }
    for (var i = 0; i < data_sim.length; i++) {
        var string=`<tr>`
        for(let [key,value] of Object.entries(data_sim[i]) ){
            string+=`<td style="text-align:center;">${value}</td>`
            }
        string+=`</tr>`
        $(`#${simulated_val}`).find('tbody').append(string)
    }

    $(body).append(`
    <div class='row'>
        <div class="card col-6">
            <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke;">
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
        <div class="card col-6" style='display: flex;height: 30rem;'>
            <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke;">
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

    $(`#${varTable} thead tr`).empty()
    for(let [key,value] of Object.entries(data_var[0]) ){
        $(`#${varTable}`).find('thead tr').eq(0).append(`<th style="text-align:center;">${key}</th>`)
    }
    for (var i = 0; i < data_var.length; i++) {
        var string=`<tr>`
        for(let [key,value] of Object.entries(data_var[i]) ){
            string+=`<td style="text-align:center;">${value}</td>`
            }
        string+=`</tr>`
        $(`#${varTable}`).find('tbody').append(string)
    }
   $(modal).modal('show')

initialise_table(`#${varTable}`);

initialise_table(`#${correlation_matrix}`);

initialise_table(`#${simulated_val}`);
}

function portfolio_valuation_output(data,body,modal){
    data.output = JSON.parse(data.output)
    $(body).empty()
    var string_0 = `<div class="col-12">
                <div class="card">
                    <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke;">
                        <h1 class="mb-0" style="text-align:center;">
                            Portfolio Valuation
                        </h1>
                    </div>
                    <div class="card-body" style="padding:0.3rem;">
                        <table id="exampledataResults3" class="display compact" style="width:100%;">
                            <thead>
                                <tr></tr>
                            </thead>
                            <tbody>
                            </tbody>
                        </table>
                    </div>
                </div>
        </div>`
    if(data.var_plot!=""){
        string_0 += `<div class="card">
                        <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke;">
                            <h1 class="mb-0" style="text-align:center;">
                                Portfolio Value at Risk (VaR)
                            </h1>
                        </div>
                        <div class="card-body" style="padding:0.3rem;">
                            <img
                                src="data:image/png;base64,${data.var_plot}"
                                height="97%"
                                width="100%"
                                alt="VaR"
                                style="border:2px solid black;"
                                title="Value at Risk"
                                />
                        </div>
                    </div>`
    }

    $(body).append(string_0)
    for (var i = 0; i < data.output[0].length; i++) {
        var string=`<tr>`
        string+=`<td style="text-align:center;">${data.output[0][i].Unique_Reference_ID}</td>`
        string+=`<td style="text-align:center;">${data.output[0][i].Position_Id}</td>`
        string+=`<td style="text-align:center;">${data.output[0][i].Product_Variant_Name}</td>`
        string+=`<td style="text-align:center;">${data.output[0][i].Valuation_Date}</td>`

        if (Object.keys(data.output[0][i].Cashflow_Result).length >0 ){
            string+=`<td class="view_cf_results" data-output = ${i} style="text-align:center;">View Details</td>`
        } else {
            string+=`<td style="text-align:center;">No Detail</td>`
        }

        string+=`<td style="text-align:center;">${data.output[0][i].Fair_Value_Per_Unit}</td>`
        string+=`<td style="text-align:center;">${data.output[0][i].Quantity}</td>`
        string+=`<td style="text-align:center;">${data.output[0][i].Total_Holding}</td>`

        if (data.output[0][i].Sensitivity.length >0 ){
            string+=`<td class="view_sensitivity_results" data-output = ${i} style="text-align:center;">View Details</td>`
        } else {
            string+=`<td style="text-align:center;">No Detail</td>`
        }
        if("Security VaR" in data.output[0][i]){
            string += `<td style="text-align:center;">${data.output[0][i]["Security VaR"]}</td>`
        }
        if("Portfolio - Undiversified VaR" in data.output[0][i]){
            string += `<td style="text-align:center;">${data.output[0][i]["Portfolio - Undiversified VaR"]}</td>`
        }
        if("Portfolio - Diversified VaR" in data.output[0][i]){
            string += `<td style="text-align:center;">${data.output[0][i]["Portfolio - Diversified VaR"]}</td>`
        }
        string+=`</tr>`
        $('#exampledataResults3').find('tbody').append(string)
    }

    $("#exampledataResults3 thead tr").empty()

    for(let [key,value] of Object.entries(data.output[0][0]) ){
        $(`#exampledataResults3`).find('thead tr').eq(0).append(`<th style="text-align:center;">${key}</th>`)
    }

    $(modal).modal('show')
    initialise_table_results_3()

    function cf_results(){
        $('.view_cf_results').off('click').on('click',function(){
            var data1 = data.output[0][$(this).attr('data-output')].Cashflow_Result
            $('#view_cf_sens_Results').empty()
            $('#view_cf_sens_Results').append(`
            <div class="col-12">
                    <div class="card">
                        <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke;">
                            <h2 class="mb-0" style="text-align:center;">
                            Cashflow Table
                            </h2>
                        </div>
                        <div class="card-body" style="padding:0.9rem;">
                            <table id="exampledataResults" class="display compact" style="width:100%;">
                                <thead>
                                    <tr></tr>
                                </thead>
                                <tbody>
                                </tbody>
                            </table>
                        </div>
                    </div>
            </div>

            `)
            for (var i = 0; i < data1.length; i++) {
                var string=`<tr>`
                for([key, value] of Object.entries(data1[i])){
                    string+=`<td style="text-align:center;">${value}</td>`
                }
                string+=`</tr>`
                $('#exampledataResults').find('tbody').append(string)
            }

            $("#exampledataResults thead tr").empty()
            for([key, value] of Object.entries(data1[0])){
                $(`#exampledataResults`).find('thead tr').eq(0).append(`<th style="text-align:center;">${key}</th>`)
            }

            $('#cf_sens_output_Modal').modal('show')
            initialiseTableResults()
        })
    }

    function sensitivity_results(){
        $('.view_sensitivity_results').off('click').on('click',function(){
            var data1 = data.output[0][$(this).attr('data-output')].Sensitivity
            $('#view_cf_sens_Results').empty()
            $('#view_cf_sens_Results').append(`
            <div class="col-12">
                    <div class="card">
                        <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke;">
                            <h2 class="mb-0" style="text-align:center;">
                            Sensitivity Analysis
                            </h2>
                        </div>
                        <div class="card-body" style="padding:0.9rem;">
                            <table id="exampledataResults" class="display compact" style="width:100%;">
                                <thead>
                                    <tr></tr>
                                </thead>
                                <tbody>
                                </tbody>
                            </table>
                        </div>
                    </div>
            </div>

            `)

            for (var i = 0; i < data1.length; i++) {
                var string=`<tr>`
                for(j in Object.keys(data1[0])){
                    string+=`<td style="text-align:center;">${data1[i][Object.keys(data1[i])[j]]}</td>`
                }
                string+=`</tr>`
                $('#exampledataResults').find('tbody').append(string)
            }
            $("#exampledataResults thead tr").empty()
            for(j in Object.keys(data1[0])){
                $(`#exampledataResults`).find('thead tr').eq(0).append(`<th style="text-align:center;">${Object.keys(data1[0])[j]}</th>`)
            }

            $('#cf_sens_output_Modal').modal('show')
            initialiseTableResults()
        })
    }

    cf_results()
    sensitivity_results()

    $('#exampledataResults3_paginate').on('click',function() {
        cf_results()
        sensitivity_results()
    })
}

function trainGARCHModel(data,body,modal){
    $(body).empty()
    $(body).append(
        `<div class="row">
            <div class="col-6">
                <div class="card">
                    ${data.summary}
                </div>
                <div class="card">
                    <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke;">
                        <h2 class="mb-0 timeSeriesHeaders" style="text-align:center;">
                        Actual vs Predicted - Table
                        </h2>
                    </div>
                    <div class="card-body" style="padding:0.9rem;">
                        <table id="exampledataResults" class="display compact" style="width:100%;">
                            <thead>
                                <tr></tr>
                            </thead>
                            <tbody>
                            </tbody>
                        </table>
                    </div>
                </div>
                <div class="card">
                    <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke">
                        <h2 class="mb-0 timeSeriesHeaders" style="text-align:center;">
                            Augmented Dickey Fuller Test For Stationarity
                        </h2>
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
                    <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke">
                        <h2 class="mb-0 timeSeriesHeaders" style="text-align:center;">
                            Jarque-Bera Test For Normality
                        </h2>
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
                    <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke">
                        <h2 class="mb-0 timeSeriesHeaders" style="text-align:center;">
                            Model Analysis
                        </h2>
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
    )
    $('.simpletable').each(function(){
        $(this).attr('class','table table-bordered table-sm')
        $(this).find("th").each(function(){
            $(this).css('text-align','center')
        })
        $(this).find("td").each(function(){
            $(this).css('text-align','center')
        })
    })
    for (var i = 0; i < data.table[data.table_headers[0]].length; i++) {
        var string=`<tr>`
        for(j in data.table_headers){
            string+=`<td style="text-align:center;">${data.table[data.table_headers[j]][i]}</td>`
        }
        string+=`</tr>`
        $('#exampledataResults').find('tbody').append(string)
        }

    $("#exampledataResults thead tr").empty()
    $("#thid").css("display","none")
    for(j in data.table_headers){
        $(`#exampledataResults`).find('thead tr').eq(0).append(`<th style="text-align:center;">${data.table_headers[j]}</th>`)
    }
    $(modal).modal('show')
    initialiseTableResults()
}

function trainARIMARun(data,body,modal){
    $(body).empty()
    $(body).append(
        `<div class="row">
            <div class="col-6">
                <div class="card">
                    ${data.summary}
                </div>
                <div class="card">
                    <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke;">
                        <h2 class="mb-0 timeSeriesHeaders" style="text-align:center;">
                        Actual vs Predicted - Table
                        </h2>
                    </div>
                    <div class="card-body" style="padding:0.9rem;">
                        <table id="exampledataResults" class="display compact" style="width:100%;">
                            <thead>
                                <tr></tr>
                            </thead>
                            <tbody>
                            </tbody>
                        </table>
                    </div>
                </div>
                <div class="card">
                    <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke">
                        <h2 class="mb-0 timeSeriesHeaders" style="text-align:center;">
                            Augmented Dickey Fuller Test For Stationarity
                        </h2>
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
            </div>
            <div class="col-6">
                <div class="card">
                    <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke">
                        <h2 class="mb-0 timeSeriesHeaders" style="text-align:center;">
                            Model Analysis
                        </h2>
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
                            <p style="margin-left:22.5%"><strong>Mean Squared Error (MSE) </strong> = ${data.mse}.</p>
                        </div>
                    </div>
                </div>
                <div class="card">
                    <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke">
                        <h2 class="mb-0 timeSeriesHeaders" style="text-align:center;">
                            Jarque-Bera Test For Normality
                        </h2>
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
        </div>`
    )
    $('.simpletable').each(function(){
        $(this).attr('class','table table-bordered table-sm')
        $(this).find("th").each(function(){
            $(this).css('text-align','center')
        })
        $(this).find("td").each(function(){
            $(this).css('text-align','center')
        })
    })
    for (var i = 0; i < data.table[data.table_headers[0]].length; i++) {
        var string=`<tr>`
        for(j in data.table_headers){
            string+=`<td style="text-align:center;">${data.table[data.table_headers[j]][i]}</td>`
        }
        string+=`</tr>`
        $('#exampledataResults').find('tbody').append(string)
        }

    $("#exampledataResults thead tr").empty()
    $("#thid").css("display","none")
    for(j in data.table_headers){
        $(`#exampledataResults`).find('thead tr').eq(0).append(`<th style="text-align:center;">${data.table_headers[j]}</th>`)
    }
    $(modal).modal('show')
    initialiseTableResults()
}

function analyseTSData(data,body,modal){
    $(body).empty()
    $(body).append(
    `<div class="card">
        <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke;">
            <h2 class="mb-0" style="text-align:center;">
                ACF and PACF
            </h2>
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
        <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke;">
            <h2 class="mb-0" style="text-align:center;">
                Augmented Dickey Fuller Test For Stationarity
            </h2>
        </div>
        <div class="card-body">
            <div class = "row" style="background:whitesmoke;">
                <div class="col-2"></div>
                <div class = "col-5">
                        <strong> H0 : </strong> The time series has a unit root and is not stationary.
                </div>
                <div class = "col-5">
                    <strong> H1 :  </strong> The time series is stationary.
                </div>
            </div>
            <br>
            <div class = "row" style="margin-left:28rem;">
                <strong> P-value : </strong> &nbsp;${data.p_value}
            </div><br>
            <div class = "row" style="margin-left:26rem;">
                <strong> Conclusion : </strong>&nbsp;${data.test_result}
            </div>
        </div>
    </div>
    `)
    $(modal).modal('show')
}
function displayBootStrapOptimizer(data_og, body,run,modal) {
    $(body).empty()
    if (run===0) {
    var table1Id = "exampledataResults";
    var table2Id = "exampledataResults2";
    var singlecurvetable = "singlecurvetable";
    var singlecurveplot = "singlecurveplot";
    } else {
        var table1Id = `exampledataResults_${run}`;
        var table2Id = `exampledataResults2_${run}`;
        var singlecurvetable = `singlecurvetable_${run}`;
        var singlecurveplot = `singlecurveplot_${run}`;
    }

    for(i in data_og){
        var data = data_og[i]
        table1Id += `_${i}`
        table2Id += `_${i}`
        singlecurvetable += `_${i}`
        singlecurveplot += `_${i}`
        $(body).append(`
        <div class='row'>
        <div class="col-6">
                <div class="card">
                    <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke;">
                        <h2 class="mb-0" style="text-align:center;">
                        ${data.curve_name} - Spot Rates
                        </h2>
                    </div>
                    <div class="card-body" style="padding:0.9rem;">
                        <table id="${table1Id}" style="width:100%;" class="display compact">
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
        `)

        if (Object.keys(data).includes("Plot")) {
            $(`#${singlecurvetable}`).append(`
                <div class="card">
                    <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke;">
                        <h2 class="mb-0" style="text-align:center;">
                            ${data.curve_name} - Spot Curve
                        </h2>
                    </div>
                    <div class="card-body" style="padding:0.9rem;" id="${singlecurveplot}">

                    </div>
                </div>
            `)
        }
        for (var i = 0; i < data.Table.length; i++) {
            var string=`<tr>`
            for(let [key,value] of Object.entries(data.Table[i]) ){
                string+=`<td style="text-align:center;">${value}</td>`
                }
            string+=`</tr>`
            $(`#${table1Id}`).find('tbody').append(string)
        }
        $(`#${table1Id} thead tr`).empty()
        for(let [key,value] of Object.entries(data.Table[0]) ){
            $(`#${table1Id}`).find('thead tr').eq(0).append(`<th style="text-align:center;">${key}</th>`)
        }

        if (Object.keys(data).includes("Plot")) {
            $(`#${singlecurveplot}`).append(`
                <div class="row">
                    <img
                    src="data:image/png;base64,${data.Plot}"
                    width="100%"
                    height="100%"
                    alt="Spot Curve"
                    style="border:2px solid black;margin:auto;"
                    title="Spot Curve"
                    />
                </div>
            `)
        }
        initialise_table_results_5(table1Id)
        $(`#${table1Id}`).DataTable().columns.adjust()
    }

}

function initialise_table_results_4(){
    var data_table_1 = $('#exampledataResults4').DataTable({
    "autoWidth": false,
    "scrollY": 200,
    "scrollX": 500,
    "scrollCollapse": true,
    "sScrollXInner": "100%",
    "ordering":false,
    orderCellsTop: true,
    responsive: true,
    colReorder: {
    fixedColumnsLeft: 1
    },
    stateSave: true,
    "deferRender": true,
    "paging": true,
    "lengthMenu": [[1, 5, 50, -1], [1, 5, 50, "All"]],
    stripeClasses: false,
    "pageLength": 50,
    dom: 'lfBrtip',
    buttons: [
        {
        extend: 'collection',
        text: 'Export',
        buttons: [
            {
            extend: 'copy', title: '', exportOptions: {
                columns: ':visible:not(.noVis)'
            }
            },
            {
            extend: 'excel', title: '', exportOptions: {
                columns: ':visible:not(.noVis)'
            }
            },
            {
            extend: 'csv', title: '', exportOptions: {
                columns: ':visible:not(.noVis)'
            }
            },
            {
            extend: 'pdf', title: '', exportOptions: {
                columns: ':visible:not(.noVis)'
            }
            },
        ],
        },
        {
        extend: 'colvis',
        className: "scroller",
        }
        ],
        columnDefs: [
    {
        targets: "_all",
        className: 'dt-center allColumnClass all'
    },
    //{ 'visible': false, 'targets': [1,3] }
    ],
    });
}


function displayResultsOptimizer(data, body, run,modal) {
    $(body).empty()
    if (run===0) {
        var table1Id = "exampledataResults";
        var table2Id = "exampledataResults2";
        var table3Id =  "exampledataResults4";
        var additionOutputOptimizer = "additionOutputOptimizer";
        var optimizerEffContainer = "optimizerEffContainer";
    } else {
        var table1Id = `exampledataResults_${run}`;
        var table2Id = `exampledataResults2_${run}`;
        var table3Id =  `exampledataResults4_${run}`;
        var additionOutputOptimizer = `additionOutputOptimizer_${run}`;
        var optimizerEffContainer = `optimizerEffContainer_${run}`;
    }
    $(body).append(`
    <div class="col-12">
            <div class="card">
                <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke;">
                    <h2 class="mb-0" style="text-align:center;">
                    Model Portfolio Allocation
                    </h2>
                </div>
                <div class="card-body" style="padding:0.9rem;">
                    <table id="${table1Id}" class="display compact" style="width:100%;">
                        <thead>
                            <tr></tr>
                        </thead>
                        <tbody>
                        </tbody>
                    </table>
                </div>
            </div>
    </div>
    <div class="row" id="${additionOutputOptimizer}">
    </div>
    <div class="col-12">
            <div class="card">
                <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke;">
                    <h2 class="mb-0" style="text-align:center;">
                        Security Allocation
                    </h2>
                </div>
                <div class="card-body" style="padding:0.3rem;">
                    <br>
                    <div class = "row" style="margin-left:0.5rem;"><h6><span style="color:var(--primary-color)">Investment: </span><span style="background:whitesmoke;">₹ ${data.investment_amount}</span><h6></div>
                    <div class = "row" style="margin-left:0.5rem;"><h6><span style="color:var(--primary-color)">Unallocated Investment: </span><span style="background:whitesmoke;">₹ ${data.unallocated_investment_amount}</span></h6></div>
                    <br>
                    <table id="${table3Id}" class="display compact" style="width:100%;margin-left:0.5rem;">
                        <thead>
                            <tr></tr>
                        </thead>
                        <tbody>
                        </tbody>
                    </table>
                </div>
            </div>
    </div>
    `)
    if (Object.keys(data).includes("constraint_report")) {
        $(`#${additionOutputOptimizer}`).append(`
        <div class = "col-7">
            <div class="card">
                <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke;">
                    <h2 class="mb-0" style="text-align:center;">
                    Constraint Report
                    </h2>
                </div>
                <div class="card-body" style="padding:0.9rem;">
                    <table id="${table2Id}" class="display compact" style="width:80%;">
                        <thead>
                            <tr></tr>
                        </thead>
                        <tbody>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        `)
    }
    if (Object.keys(data).includes("efficient_frontier")) {
        $(`#${additionOutputOptimizer}`).append(`
        <div class = "col-5">
            <div class="card">
                <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke;">
                    <h2 class="mb-0" style="text-align:center;">
                    Efficient Frontier Curve
                    </h2>
                </div>
                <div class="card-body" style="padding:0.9rem;" id="${optimizerEffContainer}">

                </div>
            </div>
        </div>
        `)
    }
    for (var i = 0; i < data.portfolio_allocation.length; i++) {
        var string=`<tr>`
        for(let [key,value] of Object.entries(data.portfolio_allocation[i]) ){
            string+=`<td style="text-align:center;">${value}</td>`
            }
        string+=`</tr>`
        $(`#${table1Id}`).find('tbody').append(string)
    }
    $(`#${table1Id} thead tr`).empty()
    for(let [key,value] of Object.entries(data.portfolio_allocation[0]) ){
        $(`#${table1Id}`).find('thead tr').eq(0).append(`<th style="text-align:center;">${key}</th>`)
    }
    for (var i = 0; i < data.security_allocation_output[data.security_allocation_output_headers[0]].length; i++) {
        var string=`<tr>`
        for(j in data.security_allocation_output_headers){
           string+=`<td style="text-align:center;">${data.security_allocation_output[data.security_allocation_output_headers[j]][i]}</td>`
        }
        string+=`</tr>`
        $(`#${table3Id}`).find('tbody').append(string)
    }
    $(`#${table3Id} thead tr`).empty()
    for(j in data.security_allocation_output_headers){
        $(`#${table3Id}`).find('thead tr').eq(0).append(`<th style="text-align:center;">${data.security_allocation_output_headers[j]}</th>`)
    }
    if (Object.keys(data).includes("constraint_report")) {
        for (var i = 0; i < data.constraint_report.length; i++) {
            var string=`<tr>`
            for(let [key,value] of Object.entries(data.constraint_report[i]) ){
                if(["constraint_parameter","constraint_parameter_value"].includes(key)){
                    string+=`<td style="white-space:normal;width:200px;">${value}</td>`
                }
                else{
                    string+=`<td style="text-align:center;">${value}</td>`
                }
                }
            string+=`</tr>`
            $(`#${table2Id}`).find('tbody').append(string)
        }
        $(`#${table2Id} thead tr`).empty()
        for(let [key,value] of Object.entries(data.constraint_report[0]) ){
            $(`#${table2Id}`).find('thead tr').eq(0).append(`<th style="text-align:center;">${key}</th>`)
        }
    }

    if (Object.keys(data).includes("efficient_frontier")) {
        $(`#${optimizerEffContainer}`).append(`
            <div class="row">
                <img
                src="data:image/png;base64,${data.efficient_frontier}"
                width="100%"
                height="100%"
                alt="Efficient Frontier"
                style="border:2px solid black;margin:auto;"
                title="Efficient Frontier"
                />
            </div>
        `)
    }

}

function initialise_table_results_3(){
    var data_table = $('#exampledataResults3').DataTable({
    "autoWidth": false,
    "scrollY": 200,
    "scrollX": 500,
    "scrollCollapse": true,
    "sScrollXInner": "100%",
    "ordering":false,
    orderCellsTop: true,
    responsive: true,
    colReorder: {
    fixedColumnsLeft: 1
    },
    stateSave: true,
    "deferRender": true,
    "paging": true,
    "lengthMenu": [[1, 5, 50, -1], [1, 5, 50, "All"]],
    stripeClasses: false,
    "pageLength": 50,
    dom: 'lfBrtip',
    buttons: [
        {
        extend: 'collection',
        text: 'Export',
        buttons: [
            {
            extend: 'copy', title: '', exportOptions: {
                columns: ':visible:not(.noVis)'
            }
            },
            {
            extend: 'excel', title: '', exportOptions: {
                columns: ':visible:not(.noVis)'
            }
            },
            {
            extend: 'csv', title: '', exportOptions: {
                columns: ':visible:not(.noVis)'
            }
            },
            {
            extend: 'pdf', title: '', exportOptions: {
                columns: ':visible:not(.noVis)'
            }
            },
        ],
        },
        {
        extend: 'colvis',
        className: "scroller",
        }
        ],
        columnDefs: [
    {
        targets: "_all",
        className: 'dt-center allColumnClass all'
    },
    //{ 'visible': false, 'targets': [1,3] }
    ],
    });
}
function initialise_table_results_2(){
    var data_table_2 = $('#exampledataResults2').DataTable({
    "autoWidth": false,
    "scrollY": 200,
    "scrollX": 500,
    "scrollCollapse": true,
    "sScrollXInner": "100%",
    "ordering":false,
    orderCellsTop: true,
    responsive: true,
    colReorder: {
    fixedColumnsLeft: 1
    },
    stateSave: true,
    "deferRender": true,
    "paging": true,
    "lengthMenu": [[1, 5, 50, -1], [1, 5, 50, "All"]],
    stripeClasses: false,
    "pageLength": 50,
    dom: 'lfBrtip',
    buttons: [
        {
        extend: 'collection',
        text: 'Export',
        buttons: [
            {
            extend: 'copy', title: '', exportOptions: {
                columns: ':visible:not(.noVis)'
            }
            },
            {
            extend: 'excel', title: '', exportOptions: {
                columns: ':visible:not(.noVis)'
            }
            },
            {
            extend: 'csv', title: '', exportOptions: {
                columns: ':visible:not(.noVis)'
            }
            },
            {
            extend: 'pdf', title: '', exportOptions: {
                columns: ':visible:not(.noVis)'
            }
            },
        ],
        },
        // {
        // extend: 'colvis',
        // className: "scroller",
        // }
        ],
        columnDefs: [
    {
        targets: "_all",
        className: 'dt-center allColumnClass all'
    },
    //{ 'visible': false, 'targets': [1,3] }
    ],
    });
}

function initialiseTableResults(){
    var data_table_1 = $('#exampledataResults').DataTable({
    "autoWidth": false,
    "scrollY": 200,
    "scrollX": 500,
    "scrollCollapse": true,
    "sScrollXInner": "100%",
    "ordering":false,
    orderCellsTop: true,
    responsive: true,
    colReorder: {
    fixedColumnsLeft: 1
    },
    stateSave: true,
    "deferRender": true,
    "paging": true,
    "lengthMenu": [[1, 5, 50, -1], [1, 5, 50, "All"]],
    stripeClasses: false,
    "pageLength": 50,
    dom: 'lfBrtip',
    buttons: [
        {
        extend: 'collection',
        text: 'Export',
        buttons: [
            {
            extend: 'copy', title: '', exportOptions: {
                columns: ':visible:not(.noVis)'
            }
            },
            {
            extend: 'excel', title: '', exportOptions: {
                columns: ':visible:not(.noVis)'
            }
            },
            {
            extend: 'csv', title: '', exportOptions: {
                columns: ':visible:not(.noVis)'
            }
            },
            {
            extend: 'pdf', title: '', exportOptions: {
                columns: ':visible:not(.noVis)'
            }
            },
        ],
        },
        {
        extend: 'colvis',
        className: "scroller",
        }
        ],
        columnDefs: [
    {
        targets: "_all",
        className: 'dt-center allColumnClass all'
    },
    //{ 'visible': false, 'targets': [1,3] }
    ],
    }).columns.adjust();
}


function displayResultsFinInstrument(data, body,modal) {
    $(body).empty()
    $(body).append(`
    <div class="col-12">
            <div class="card">
                <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke;">
                    <h2 class="mb-0" style="text-align:center;">
                    Cashflow Table
                    </h2>
                </div>
                <div class="card-body" style="padding:0.9rem;">
                    <table id="exampledataResults" class="display compact" style="width:100%;">
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
        <div class = "col-5">
            <div class="card">
                <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke;">
                    <h2 class="mb-0" style="text-align:center;">
                    Valuation Results
                    </h2>
                </div>
                <div class="card-body" style="padding:0.9rem;">
                    <table id="exampledataResults2" class="display compact" style="width:80%;">
                        <thead>
                            <tr></tr>
                        </thead>
                        <tbody>
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        <div class = "col-7">
            <div class="card">
                <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke;">
                    <h2 class="mb-0" style="text-align:center;">
                    Sensitivity Analysis
                    </h2>
                </div>
                <div class="card-body" style="padding:0.9rem;">
                    <table id="exampledataResults3" class="display compact" style="width:100%;">
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

    `)
    for (var i = 0; i < data.cashflow_model_results[data.cashflow_model_results_headers[0]].length; i++) {
        var string=`<tr>`
        for(j in data.cashflow_model_results_headers){
            string+=`<td style="text-align:center;">${data.cashflow_model_results[data.cashflow_model_results_headers[j]][i]}</td>`
        }
        string+=`</tr>`
        $('#exampledataResults').find('tbody').append(string)
    }

    $("#exampledataResults thead tr").empty()
    for(j in data.cashflow_model_results_headers){
        $(`#exampledataResults`).find('thead tr').eq(0).append(`<th style="text-align:center;">${data.cashflow_model_results_headers[j]}</th>`)
    }
    for (var i = 0; i < data.valuation_results.length; i++) {
        var string=`<tr>`
        for(j in data.valuation_headers){
            string+=`<td style="text-align:center;">${data.valuation_results[i][data.valuation_headers[j]]}</td>`
        }
        string+=`</tr>`
        $('#exampledataResults2').find('tbody').append(string)
    }

    $("#exampledataResults2 thead tr").empty()
    for(j in data.valuation_headers){
        $(`#exampledataResults2`).find('thead tr').eq(0).append(`<th style="text-align:center;">${data.valuation_headers[j]}</th>`)
    }
    for (var i = 0; i < data.sensitivity_analysis.length; i++) {
        var string=`<tr>`
        for(j in data.sensitivity_analysis_headers){
            string+=`<td style="text-align:center;">${data.sensitivity_analysis[i][data.sensitivity_analysis_headers[j]]}</td>`
        }
        string+=`</tr>`
        $('#exampledataResults3').find('tbody').append(string)
    }
    $("#exampledataResults3 thead tr").empty()
    for(j in data.sensitivity_analysis_headers){
        $(`#exampledataResults3`).find('thead tr').eq(0).append(`<th style="text-align:center;">${data.sensitivity_analysis_headers[j]}</th>`)
    }
    // $('#tsModal').modal('show');
    // initialiseTableResults()
    // initialise_table_results_2()
    // initialise_table_results_3()

}

function displayOutputLogReg(data,body,modal) {
    const roc_curveHTML = `
        <div class="card" style="width:100%;">
            <div class="card-header" style="color:var(--primary-color);padding:0.3rem">
                <h2 class="mb-0" style="text-align:center;">
                    ROC Curve
                </h2>
            </div>
            <div class="card-body" style="padding:0.3rem;">
                <div class="row">
                    <img
                    src="data:image/png;base64,${data.roc_curve}"
                    width="450"
                    height="280"
                    alt="ROC Curve"
                    style="border:2px solid black;margin:auto;"
                    title="ROC Curve"
                    />
                </div>
            </div>
        </div>
    `;
    const outputHTML = {
        'accuracy': `
            <div class = "row" >
                <p><b> Accuracy : </b> &nbsp;${data.accuracy}</p>
            </div><br>
        `,
        'precision': `
            <div class = "row" >
                <p><b> Precision : </b> &nbsp;${data.precision}</p>
            </div><br>
        `,
        'recall': `
            <div class = "row" >
                <p><b> Recall : </b> &nbsp;${data.recall}</p>
            </div><br>
        `,
        'f1_metric': `
            <div class = "row" >
                <p><b> F1 Score : </b> &nbsp;${data.f1_metric}</p>
            </div><br>
        `,
        'conf_matrix': `
            <div class = "row" >
                <p><b> Confusion Matrix : </b></p>
                <table id="table_confusionMatrixLogReg" class='table table-bordered table-sm'>
                    <thead>
                        <tr>

                        </tr>
                    </thead>
                    <tbody>

                    </tbody>
                </table>
            </div><br>
        `,
        'report': `
            <div class = "row" >
                <p><b> Classification Report : </b></p>
                <table id="table_classReportLogReg" class='table table-bordered table-sm'>
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
    $(body).append(
        `
        <div class="row" id="logRegResults">

        </div>
    `
    );
    if ('logit_reg_summary' in data) {
        $('#logRegResults').append(
            `
            <div class="card col-7" style="width:100%;">
                <div class="card-header" style="color:var(--primary-color);padding:0.3rem">
                    <h2 class="mb-0" style="text-align:center;">
                        Logistic Regression Summary
                    </h2>
                </div>
                <div class="card-body" style="padding:0.5rem;">
                    ${data.logit_reg_summary}
                </div>
            </div>
        `
        );
        $('.simpletable').each(function(){
            $(this).attr('class','table table-bordered table-sm')
            $(this).find("th").each(function(){
                $(this).css('text-align','center')
            });
            $(this).find("td").each(function(){
                $(this).css('text-align','center')
            });
        });
    };

    $('#logRegResults').append(`
        <div class="col-5" id="rightContainerLR">
            <div class="row" id="plotContainerLogReg" style="display: none;">
            </div>
            <div class="row" id="scoreContainerLogReg" style="display: none;">
                <div class="card">
                    <div class="card-header" style="color:var(--primary-color);padding:0.3rem">
                        <h2 class="mb-0" style="text-align:center;">
                            Scores
                        </h2>
                    </div>
                    <div class="card-body" id="scoreSpaceLogReg">
                    </div>
                </div>
            </div>
        </div>
    `)
    for (const key in data) {
        if (data.hasOwnProperty(key)) {
            if (key === 'roc_curve') {
                $("#plotContainerLogReg").css('display', 'block');
                let htmlString = roc_curveHTML;
                $('#plotContainerLogReg').append(htmlString);
            } else if (key in outputHTML) {
                $("#scoreContainerLogReg").css('display', 'block');
                let htmlString = outputHTML[key];
                $('#scoreSpaceLogReg').append(htmlString);
                if (key === 'report') {
                    $("#table_classReportLogReg tbody").empty();
                    $("#table_classReportLogReg thead tr").empty()
                    for(let [key,value] of Object.entries(data.report[0]) ){
                        $(`#table_classReportLogReg`).find('thead tr').eq(0).append(`<th style="text-align:center;">${key}</th>`)
                    };
                    for (var i = 0; i < data.report.length; i++) {
                        var string=`<tr>`
                        for(let [key,value] of Object.entries(data.report[i]) ){
                            string+=`<td style="text-align:center;">${value}</td>`
                            }
                        string+=`</tr>`
                        $('#table_classReportLogReg').find('tbody').append(string)
                    };
                } else if (key === 'conf_matrix') {
                    $("#table_confusionMatrixLogReg tbody").empty();
                    $("#table_confusionMatrixLogReg thead tr").empty()
                    for(let [key,value] of Object.entries(data.conf_matrix[0]) ){
                        $(`#table_confusionMatrixLogReg`).find('thead tr').eq(0).append(`<th style="text-align:center;">${key}</th>`)
                    };
                    for (var i = 0; i < data.conf_matrix.length; i++) {
                        var string=`<tr>`
                        for(let [key,value] of Object.entries(data.conf_matrix[i]) ){
                            string+=`<td style="text-align:center;">${value}</td>`
                            }
                        string+=`</tr>`
                        $('#table_confusionMatrixLogReg').find('tbody').append(string)
                    };

                }
            };
        };
    };
}


function displayOutputLinReg(data,body,modal) {
    const actual_vs_fitted_plot_HTML = `
        <div class="card" style="width:100%;">
            <div class="card-header" style="color:var(--primary-color);padding:0.3rem">
                <h2 class="mb-0" style="text-align:center;">
                    Actual v/s Fitted Plot
                </h2>
            </div>
            <div class="card-body" style="padding:0.3rem;">
                <div class="row">
                    <img
                    src="data:image/png;base64,${data.actual_vs_fitted_plot}"
                    width="450"
                    height="280"
                    alt="Actual v/s Fitted Plot"
                    style="border:2px solid black;margin:auto;"
                    title="Actual v/s Fitted Plot"
                    />
                </div>
            </div>
        </div>
    `;
    const qq_plotHTML = `
        <div class="card" style="width:100%;">
            <div class="card-header" style="color:var(--primary-color);padding:0.3rem">
                <h2 class="mb-0" style="text-align:center;">
                    Quantile Plot
                </h2>
            </div>
            <div class="card-body" style="padding:0.3rem;">
                <div class="row">
                    <img
                    src="data:image/png;base64,${data.quantile_plot}"
                    width="450"
                    height="280"
                    alt="Quantile Plot"
                    style="border:2px solid black;margin:auto;"
                    title="Quantile Plot"
                    />
                </div>
            </div>
        </div>
    `;
    const outputHTML = {
        'mean_abs_error': `
            <div class = "row" >
                <p><b>Mean Absolute Error : </b> &nbsp;${data.mean_abs_error}</p>
            </div><br>
        `,
        'intercept_estimate': `
            <div class = "row" >
                <p><b> Intercept Estimate : </b> &nbsp;${data.intercept_estimate}</p>
            </div><br>
        `,
        'mean_sq_error': `
            <div class = "row" >
                <p><b> Mean Squared Error : </b> &nbsp;${data.mean_sq_error}</p>
            </div><br>
        `,
        'coefficient_of_determination': `
            <div class = "row" >
                <p><b> Coefficient of Determination : </b> &nbsp;${data.coefficient_of_determination}</p>
            </div><br>
        `,
        'parameter_estimates': `
            <div class = "row" >
                <p><b> Paremeter Estimates : </b></p>
                <table id="table_parameterEstLinReg" class='table table-bordered table-sm'>
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

    $(body).append(
        `
        <div class="row" id="linRegResults">

        </div>
    `
    );

    if ('linear_reg_summary' in data) {
        $('#linRegResults').append(
            `
            <div class="col-7" id='summayContainerLinReg'>
                <div class="card" style="width:100%;">
                    <div class="card-header" style="color:var(--primary-color);padding:0.3rem">
                        <h2 class="mb-0" style="text-align:center;">
                            Linear Regression Summary
                        </h2>
                    </div>
                    <div class="card-body" style="padding:0.5rem;">
                        ${data.linear_reg_summary}
                    </div>
                </div>
            </div>
        `
        );
        $('.simpletable').each(function(){
            $(this).attr('class','table table-bordered table-sm')
            $(this).find("th").each(function(){
                $(this).css('text-align','center')
            });
            $(this).find("td").each(function(){
                $(this).css('text-align','center')
            });
        });
    };


    $('#linRegResults').append(`
        <div class="col-5" id="rightContainerLR">
            <div class="row" id="plotContainerLinReg" style="display: none;">
            </div>
            <div class="row" id="scoreContainerLinReg" style="display: none;">
                <div class="card">
                    <div class="card-header" style="color:var(--primary-color);padding:0.3rem">
                        <h2 class="mb-0" style="text-align:center;">
                            Scores
                        </h2>
                    </div>
                    <div class="card-body" id="scoreSpaceLinReg">
                    </div>
                </div>
            </div>
        </div>
    `)
    for (const key in data) {
        if (data.hasOwnProperty(key)) {
            if (key === 'actual_vs_fitted_plot') {
                $("#plotContainerLinReg").css('display', 'block');
                let htmlString = actual_vs_fitted_plot_HTML;
                $('#plotContainerLinReg').append(htmlString);
            } else if (key === 'quantile_plot') {
                $("#plotContainerLinReg").css('display', 'block');
                let htmlString = qq_plotHTML;
                $('#plotContainerLinReg').append(htmlString);
            } else if (key in outputHTML) {
                $("#scoreContainerLinReg").css('display', 'block');
                let htmlString = outputHTML[key];
                $('#scoreSpaceLinReg').append(htmlString);
                if (key === 'parameter_estimates') {
                    $("#table_parameterEstLinReg tbody").empty();
                    $("#table_parameterEstLinReg thead tr").empty()
                    for(let [key,value] of Object.entries(data.parameter_estimates[0]) ){
                        $(`#table_parameterEstLinReg`).find('thead tr').eq(0).append(`<th style="text-align:center;">${key}</th>`)
                    };
                    for (var i = 0; i < data.parameter_estimates.length; i++) {
                        var string=`<tr>`
                        for(let [key,value] of Object.entries(data.parameter_estimates[i]) ){
                            string+=`<td style="text-align:center;">${value}</td>`
                            }
                        string+=`</tr>`
                        $('#table_parameterEstLinReg').find('tbody').append(string)
                    };
                }
            };
        };
    };
    if ('actual_vs_fitted_data' in data) {
        $('#summayContainerLinReg').append(`
            <div class="card">
                <div class="card-header" style="color:var(--primary-color);padding:0.3rem">
                    <h2 class="mb-0" style="text-align:center;">
                        Actual v/s Fitted
                    </h2>
                </div>
                <div class="card-body" style="padding:0.5rem;">
                    <table id="table_ActualVFittedLinReg">
                        <thead>
                            <tr>

                            </tr>
                        </thead>
                        <tbody>

                        </tbody>
                    </table>
                </div>
            </div>
        `)
        $("#table_ActualVFittedLinReg tbody").empty();
        $("#table_ActualVFittedLinReg thead tr").empty()
        for(let [key,value] of Object.entries(data.actual_vs_fitted_data[0]) ){
            $(`#table_ActualVFittedLinReg`).find('thead tr').eq(0).append(`<th>${key}</th>`)
        };
        for (var i = 0; i < data.actual_vs_fitted_data.length; i++) {
            var string=`<tr>`
            for(let [key,value] of Object.entries(data.actual_vs_fitted_data[i]) ){
                string+=`<td>${value}</td>`
                }
            string+=`</tr>`
            $('#table_ActualVFittedLinReg').find('tbody').append(string)
        };
    }
}

function displayOutputFitTest(data,body, run,modal){
    $(body).empty()
    $(body).css('height','73vh')
    if (run===0) {
        var fittest_table = "fittest_table"
        var fittest_table_section  = "fittest_table_section"
        var saveGoodnessBestFit = "saveGoodnessBestFit"
    } else {
        var fittest_table = `fittest_table_${run}`;
        var fittest_table_section  =  `fittest_table_section_${run}`
        var saveGoodnessBestFit = `saveGoodnessBestFit_${run}`
    }
    var data_dict = JSON.parse(data.content)
    let best_fit =  JSON.parse(data.best_fit)
    let data_info = JSON.parse(data.info_dict)
    let fit_element_id = data_info.element_id
    let element_name = data_info.element_name
    let model_name = data_info.model_name
    let result_usecase = data_info.use_case
    let auto_save_config = false
    if(data_info.hasOwnProperty('auto_save')){
        if(data_info.auto_save){
            auto_save_config = true
        }
    }
    let graph_image = ""
    if(data.var_plot){
        graph_image =  `data:image/png;base64,${data.var_plot}`
    }

    var string_0 = `<div class="row" >`
        string_0 += `<div class="card col-5" style='margin-left:20px'>
                        <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke;">
                            <h1 class="mb-0" style="text-align:center;">
                                Best Fit Graph
                            </h1>
                        </div>
                        <div class="card-body" style="height:460px;overflow:auto;padding-left: 5px;">
                            <img
                                src="${graph_image}"
                                width="100%"
                                alt="GoodnessFitTest"
                                style="height: 50vh;width: 28.5vw;object-fit: contain;"
                                title="Goodness of Fit Test"
                                />
                        </div>
                    </div>`
    string_0 += ` <div class="card col-6" style='margin-left:auto;margin-right:20px;height:66vh'>
                            <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke;">
                                <h1 class="mb-0" style="text-align:center;">
                                    Goodness of Fit Table
                                </h1>
                            </div>
                            <div class="card-body fittest_table_section" id='${fittest_table_section}'  style="height:100%;">
                                <table id = "${fittest_table}" class="table " style="width:100%;">
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
                            <div class="card-footer" style="color:var(--primary-color);background:whitesmoke;text-align:end">
                                <button type="button" id="${saveGoodnessBestFit}" class="btn btn-primary rounded px-2 ml-auto"  style="color:white;">Save Best Fit</button>
                            </div>
                        </div>`
    string_0 += `</div>`


    $(body).append(string_0)
    $(`#${fittest_table}`+'_wrapper').remove()
    $(`#${fittest_table}`).remove()

    $(`#${fittest_table_section}`).append(`
    <table id = "${fittest_table}" class="table" style="width:100%;">
        <thead>
            <tr>
            </tr>
            </thead>
            <tbody>
        </tbody>
        </table>
    `)
    $(`#${fittest_table} thead tr`).empty()

    for(let [key,value] of Object.entries(data_dict[0])){
        $(`#${fittest_table}`).find('thead tr').eq(0).append(`<th style="text-align:center;">${key}</th>`)
    }

    if(Object.keys(data_dict).length > 0){
        for (var i = 0; i < data_dict.length; i++) {
        var string=`<tr data-method-name='${data_dict[i]['Distribution']}'>`
        for(let [key,value] of Object.entries(data_dict[i]) ){
          if (data_dict[i]["Distribution"] in best_fit) {
            string+=`<td style="text-align:center;background-color:lightgrey;">${value}</td>`
          } else {
            string+=`<td style="text-align:center;">${value}</td>`
          }
        }
        string+=`</tr>`
        $(`#${fittest_table}`).find('tbody').append(string)
      };
    }

    setTimeout(function(){
        $(`#${fittest_table}`).DataTable().columns.adjust()
    },500)
    if(auto_save_config){
        $(`#${saveGoodnessBestFit}`).remove()
    }
    $(`#${saveGoodnessBestFit}`).on('click',function(){
        $(`#${saveGoodnessBestFit}`).empty()
        $(`#${saveGoodnessBestFit}`).append(`<i class="fa fa-circle-notch fa-spin"></i> Saving`)
        if(Object.keys(best_fit).length>0){
            $(`#${saveGoodnessBestFit}`)
            $.ajax({
                url: window.location.pathname,
                data: {
                    'element_id':fit_element_id,
                    'element_name':element_name,
                    'model_name':model_name,
                    'output_fit_config':JSON.stringify(best_fit),
                    'use_case':result_usecase,
                    'operation': 'save_best_fit_configuration',
                },
                type: "POST",
                dataType: "json",
                success: function (data) {
                    Swal.fire({icon: 'success',text: 'Best Fit configuration saved successfully!'});
                    $(`#${saveGoodnessBestFit}`).parent().find('i').remove()
                    $(`#${saveGoodnessBestFit}`).text('Save Best Fit')
                },
                error:function(){
                    Swal.fire({icon: 'error',text: 'Error! Failure in saving Best Fit configuration .Please check your configuration and try again.'});
                }
            })
        }else{
            Swal.fire({icon: 'error',text: 'Error! Failure in generating Best Fit configuration. Please try again.'});
        }
    })


}

function displayOutputFitDiscrete(data,body, run,modal){
    $(body).empty()
    $(body).css('height','480px')
    if (run===0) {
        var fitDiscrete_table = "fitDiscrete_table"
        var fitDiscrete_table_section  = "fitDiscrete_table_section"
        var saveFitDiscrete = "saveFitDiscrete"
    } else {
        var fitDiscrete_table = `fitDiscrete_table_${run}`;
        var fitDiscrete_table_section  =  `fitDiscrete_table_section_${run}`
        var saveFitDiscrete = `saveFitDiscrete_${run}`
    }

  var data_dict = JSON.parse(data.content)
  let data_info = JSON.parse(data.info_dict)
  let discrete_element_id = data_info.element_id
  let element_name = data_info.element_name
  let model_name = data_info.model_name
  let result_usecase = data_info.use_case
  let graph_image = ""
  if(data.var_plot){
      graph_image =  `data:image/png;base64,${data.var_plot}`
  }
  let auto_save_config = false
  if(data_info.hasOwnProperty('auto_save')){
      if(data_info.auto_save){
        auto_save_config = true
        }
    }
  var string_0 = `<div class="row">`
      string_0 += `<div class="card col-5" style='margin-left:20px'>
                      <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke;">
                          <h1 class="mb-0" style="text-align:center;">
                            Distribution Graph
                          </h1>
                      </div>
                      <div class="card-body" style="height:360px;">
                          <img
                              src="${graph_image}"
                              width="100%"
                              alt="Distribution Graph"
                              style="width: 25vw;object-fit: contain;"
                              title="Distribution Graph"
                              />
                      </div>
                  </div>`
  string_0 += ` <div class="card col-6" style='margin-left:auto;margin-right:20px;height:52vh;'>
                          <div class="card-header" style="color:var(--primary-color);padding:0.3rem;background:whitesmoke;">
                              <h1 class="mb-0" style="text-align:center;">
                                Distribution Parameters Table
                              </h1>
                          </div>
                          <div class="card-body" id='${fitDiscrete_table_section}'  "style="height:300px;>
                              <table id = "${fitDiscrete_table}" class="table" style="width:100%;">
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
                          <div class="card-footer" style="color:var(--primary-color);background:whitesmoke;text-align:end">
                              <button type="button" id="${saveFitDiscrete}" class="btn btn-primary rounded px-2 ml-auto"  style="color:white;">Save Configuration</button>
                          </div>
                      </div>`
  string_0 += `</div>`


  $(body).append(string_0)
  $(`#${fitDiscrete_table}`+'_wrapper').remove()
  $(`#${fitDiscrete_table}`).remove()

  $(`#${fitDiscrete_table_section}`).append(`
  <table id = "${fitDiscrete_table}" class="table" style="width:100%;">
      <thead>
          <tr>
          </tr>
          </thead>
          <tbody>
      </tbody>
      </table>
  `)
  $(`#${fitDiscrete_table} thead tr`).empty()
$(`#${fitDiscrete_table}`).find('thead tr').eq(0).append(`<th style="text-align:center;text-transform:capitalize;">Distribution Type</th><th style="text-align:center;">Parameters</th>`)

  if(Object.keys(data_dict).length > 0){
      $(`#${fitDiscrete_table}`).find('tbody').append(`<tr data-method-name='${Object.keys(data_dict)[0]}'><td style="text-align:center;text-transform:capitalize;">${Object.keys(data_dict)[0]}</td><td style="text-align:center;">${data_dict['poisson']['lambda']}</td></tr>`)
    }

  initialise_table_results_5(tableID= `${fitDiscrete_table}`)
  setTimeout(function(){
      $(`#${fitDiscrete_table}`).DataTable().columns.adjust()
  },500)
  if(auto_save_config){

  $(`#${saveFitDiscrete}`).remove()
  }

  $(`#${saveFitDiscrete}`).off('click').on('click',function(){
      if(Object.keys(data_dict).length>0){
        $(`#${saveFitDiscrete}`).empty()
        $(`#${saveFitDiscrete}`).append(`<i class="fa fa-circle-notch fa-spin"></i> Saving`)
          $.ajax({
              url: window.location.pathname,
              data: {
                  'element_id':discrete_element_id,
                  'element_name':element_name,
                  'model_name':model_name,
                  'output_fit_config':JSON.stringify(data_dict),
                  'use_case':result_usecase,
                  'operation': 'save_fit_discrete_configuration',
              },
              type: "POST",
              dataType: "json",
              success: function (data) {
                Swal.fire({icon: 'success',text: 'Fit Discrete Distribution configuration Saved successfully'});

                  $(`#${saveFitDiscrete}`).parent().find('i').remove()
                  $(`#${saveFitDiscrete}`).text('Save Configuration')
              },
              error:function(){
                Swal.fire({icon: 'error',text: 'Error! Failure in saving Fit Discrete Distribution configuration. Please check your configuration and try again.'});
              }
          })
      }else{
        Swal.fire({icon: 'error',text: 'Error! Failure in generating Fit Discrete Distribution values.  Please try again.'});
      }
  })

}

function initialise_table(id){
    var initialised_data_table = $(id).DataTable({
    "autoWidth": false,
    "scrollY": 200,
    "scrollX": 500,
    "scrollCollapse": true,
    "sScrollXInner": "100%",
    "ordering":false,
    orderCellsTop: true,
    responsive: true,
    colReorder: {
    fixedColumnsLeft: 1
    },
    stateSave: true,
    "deferRender": true,
    "paging": true,
    "lengthMenu": [[1, 5, 50, -1], [1, 5, 50, "All"]],
    stripeClasses: false,
    "pageLength": 50,
    dom: 'lfBrtip',
    buttons: [
        {
        extend: 'collection',
        text: 'Export',
        buttons: [
            {
            extend: 'copy', title: '', exportOptions: {
                columns: ':visible:not(.noVis)'
            }
            },
            {
            extend: 'excel', title: '', exportOptions: {
                columns: ':visible:not(.noVis)'
            }
            },
            {
            extend: 'csv', title: '', exportOptions: {
                columns: ':visible:not(.noVis)'
            }
            },
            {
            extend: 'pdf', title: '', exportOptions: {
                columns: ':visible:not(.noVis)'
            }
            },
        ],
        },
        {
        extend: 'colvis',
        className: "scroller",
        }
        ],
        columnDefs: [
        {
            targets: "_all",
            className: 'dt-center allColumnClass all'
        },
        ],
    });
}

function displayOutputDecTree(data,body,modal) {
    $('#actual_grid_wrapper').remove()
    $('#actual_grid').remove()
    $('#table_confusionMatrixDecTree_wrapper').remove()
    $('#table_confusionMatrixDecTree').remove()
    $('#table_classReportDecTree_wrapper').remove()
    $('#table_classReportDecTree').remove()
    $('#tableParameters_wrapper').remove()
    $('#tableParameters').remove()
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
        <table id = "actual_grid" class="table table-bordered" style="width:100%;">
        <thead>
            <tr>
            <th scope="col">Actual value</th>
            <th scope="col">Predicted value</th>
            </tr>



            </thead>
            <tbody>



        </tbody>
        </table>
    `
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
        'accuracy': [data.accuracy,'Accuracy'],
        'r_square': [data.r_square,'Coefficient of determination'],
        'mean_sq_error': [data.mean_sq_error,'Mean squared error'],
        'mean_abs_error': [data.mean_abs_error,'Mean absolute error'],
        'precision': [data.precision, 'Precision'],
        'cross_val': [data.cross_val,'Cross validation'],
        'recall': [data.recall,'Recall'],
        'f1_metric': [data.f1_metric,'F1 metric'],
        'conf_matrix': [`<table id="table_confusionMatrixDecTree" class='table table-bordered' style="width:100%; margin-bottom:5px;">
                <thead>
                    <tr>

                        </tr>
                </thead>
                <tbody>

                </tbody>
                </table>`,'Confusion matrix'],
        'report': [` <table id="table_classReportDecTree" class='table table-bordered' style="width:100%;margin-bottom:5px;">
                <thead>
                    <tr>

                    </tr>
                </thead>
                <tbody>

                </tbody>
            </table>`,'Classification report'],
    };
    $(body).append(
        `
        <div class="row" id="DecTreeResults">

        </div>
    `
    );
    if ('dec_reg_summary' in data) {
        $('#DecTreeResults').append(
            `
            <div class="card col-7" style="width:100%;">
                <div class="card-header" style="color:var(--primary-color);padding:0px">
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
        $('.simpletable').each(function(){
            $(this).attr('class','table table-bordered table-sm')
            $(this).find("th").each(function(){
                $(this).css('text-align','center')
            });
            $(this).find("td").each(function(){
                $(this).css('text-align','center')
            });
        });
    };

    $('#DecTreeResults').append(`
    <div class="row1" id="rightContainerDT" style="width:99%;margin:auto">
        <div class="row card">
            <div class="card-header" style="color:var(--primary-color);padding-bottom:0px; background:whitesmoke;">
                <h5 class="mb-3" style="text-align:center;background:whitesmoke;">
                    Plot
                </h5>
            </div>
            <div class="col-12" id="plotContainerDecTree" style="display: none;">

            </div>
        </div>
        <div class="row card">
            <div class="card-header" style="color:var(--primary-color); padding-bottom:0px; background:whitesmoke;">
                <h5 class="mb-3" style="text-align:center;">
                    Model summary
                </h5>
            </div>
            <div class="card-body row">
                <div class="col-6" id="plotContainerDecTree2" style="display: none; margin-bottom:10px; height:46vh;">

                </div>
                <div class="col-6" id="plotContainerDecTree3" style="display: none; margin-bottom:10px; height:46vh;">

                </div>
                <div class="col-6" id="plotContainerDecTree4" style="display: none; margin-bottom:10px;">

                </div>
                <div class="col-6" id="scoreSpaceDecTree" style="display: none; margin-left: 0%; flex-wrap:wrap">
                    <p style="font-weight:bold; margin-top:20px">Scores:</p>
                    <table id="tableParameters" class='table table-bordered' style="width:100%;margin-bottom:20px;">
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
    `)
    let htmlHead, htmlBody
    for (const key in data) {
        if (data.hasOwnProperty(key)) {
            if (key === 'plot_tree') {
                $("#plotContainerDecTree").css('display', 'block');
                let htmlString = plot_curveHTML;
                $('#plotContainerDecTree').append(htmlString);
            } else if (key === 'roc_curve') {
                $("#plotContainerDecTree2").css('display', 'flex');
                let htmlString = roc_curveHTML;
                $('#plotContainerDecTree2').append(htmlString);
            } else if (key === 'actplot'){
                $("#plotContainerDecTree3").css('display', 'flex');
                let htmlString = fit_curveHTML;
                $('#plotContainerDecTree3').append(htmlString);
                $("#plotContainerDecTree4").css('display', 'block');
                $('#plotContainerDecTree4').append(fit_curve_table);

            } else if (key in outputHTML) {
                $("#scoreSpaceDecTree").css('display', 'block');
                let htmlString = outputHTML[key];
                if (key === 'report') {
                    $('#scoreSpaceDecTree').prepend(htmlString[0]);
                    $('#scoreSpaceDecTree').prepend(`<p style="font-weight:bold;">${htmlString[1]}:</p>`)
                    $("#table_classReportDecTree tbody").empty();
                    $("#table_classReportDecTree thead tr").empty()
                    for(let [key,value] of Object.entries(data.report[0]) ){
                        $(`#table_classReportDecTree`).find('thead tr').eq(0).append(`<th style="text-align:center;">${key}</th>`)
                    };
                    for (var i = 0; i < data.report.length; i++) {
                        var string=`<tr>`
                            for(let [key,value] of Object.entries(data.report[i]) ){
                                string+=`<td style="text-align:center;">${value}</td>`
                            }
                            string+=`</tr>`
                            $('#table_classReportDecTree').find('tbody').append(string)
                        };
                    } else if (key === 'conf_matrix') {
                        $('#scoreSpaceDecTree').prepend(htmlString[0]);
                        $('#scoreSpaceDecTree').prepend(`<p style="font-weight:bold;">${htmlString[1]}:</p>`)
                        $("#table_confusionMatrixDecTree tbody").empty();
                        $("#table_confusionMatrixDecTree thead tr").empty()
                        for(let [key,value] of Object.entries(data.conf_matrix[0]) ){
                            $(`#table_confusionMatrixDecTree`).find('thead tr').eq(0).append(`<th style="text-align:center;">${key}</th>`)
                        };
                        for (var i = 0; i < data.conf_matrix.length; i++) {
                            var string=`<tr>`
                                for(let [key,value] of Object.entries(data.conf_matrix[i]) ){
                                    string+=`<td style="text-align:center;">${value}</td>`
                                }
                                string+=`</tr>`
                                $('#table_confusionMatrixDecTree').find('tbody').append(string)
                            };

                        } else {

                                    htmlHead = `<th>`+ outputHTML[key][1] + `</th>`;
                                    htmlBody =  `<td>` + outputHTML[key][0] + `</td>`;
                                    $('#scoreSpaceDecTree').find('#tableParameters').find('thead').find('tr').append(htmlHead);
                                    $('#scoreSpaceDecTree').find('#tableParameters').find('tbody').find('tr').append(htmlBody);

                            }
            };
        };
    };


    if ('actual' in data){
        for (var i = 0; i < data.actual.length; i++) {
            var string=`<tr>`
            string+=`<td>${data.actual[i]}</td>`
            string+=`<td>${data.predict[i]}</td>`



            string+=`</tr>`
            $('#actual_grid').find('tbody').append(string)
        };
    }
    datatablesFuncAvsP('actual_grid');
    datatablesFunc('table_confusionMatrixDecTree')
    datatablesFunc('table_classReportDecTree')
    datatablesFunc('tableParameters')
    $('.dt-buttons').css('margin-left','3px');
}

function datatablesFuncAvsP(id) {
    $('#'+id).DataTable( {
      "autoWidth": true,
      "scrollY": "25vh",
      "scrollCollapse": true,
      "order":[[ 0, 'asc' ]],
      // "serverSide":true,
      orderCellsTop: true,
      //fixedHeader: true,
      responsive: true,
      // stateSave: true,
      "deferRender": true,
      "paging": true,
      "searching": false,
      "info": true,
      "lengthMenu": [[1, 5, 50, -1], [1, 5, 50, "All"]],
      "stripeClasses": false,
      "pageLength": 50,
      dom: 'lfBrtip',
      buttons: [
            {
                extend: 'collection',
                text: 'Export',
                buttons: [
                {
                    extend: 'copy', title: '', exportOptions: {
                    }
                },
                {
                    extend: 'excel', title: '', exportOptions: {
                    }
                },
                {
                    extend: 'csv', title: '', exportOptions: {
                    }
                },
                {
                    extend: 'pdf', title: '', exportOptions: {
                    }
                },
                ],
            },
          ],
          columnDefs: [
          {
              targets: "_all",
              className: 'dt-center allColumnClass all'
          },
          {
              targets: 0,
              width: "20%",
              className: 'noVis'
          }
      ],

      }).columns.adjust();
    }

function datatablesFunc(id) {
    $('#'+id).DataTable( {
        "autoWidth": true,
        "scrollY": "40vh",
        "scrollCollapse": true,
        "order":[[ 0, 'asc' ]],
        "scrollX": true,
        // "serverSide":true,
        orderCellsTop: true,
        //fixedHeader: true,
        responsive: true,
        // stateSave: true,
        "deferRender": true,
        "paging": false,
        "searching": false,
        "info": false,
        //"lengthMenu": [[1, 5, 50, -1], [1, 5, 50, "All"]],
        "stripeClasses": false,
        //"pageLength": 50,
        dom: 'lfBrtip',
        "sScrollX": "100%",
        "scrollX": true,
        buttons: [
            {
                extend: 'collection',
                text: 'Export',
                buttons: [
                {
                    extend: 'copy', title: '', exportOptions: {
                    }
                },
                {
                    extend: 'excel', title: '', exportOptions: {
                    }
                },
                {
                    extend: 'csv', title: '', exportOptions: {
                    }
                },
                {
                    extend: 'pdf', title: '', exportOptions: {
                    }
                },
                ],
            },

            ],
            columnDefs: [
            {
                targets: "_all",
                className: 'dt-center allColumnClass all'
            },
            {
                targets: 0,
                width: "20%",
                className: 'noVis'
            }
        ],

        }).columns.adjust();
    }


function displayOutputAB(data,tree,body,modal) {
    $('#actual_grid_wrapper').remove()
    $('#actual_grid').remove()
    $('#table_confusionMatrixDecTree_wrapper').remove()
    $('#table_confusionMatrixDecTree').remove()
    $('#table_classReportDecTree_wrapper').remove()
    $('#table_classReportDecTree').remove()
    $('#tableParameters_wrapper').remove()
    $('#tableParameters').remove()
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
        <table id = "actual_grid" class="table table-bordered" style="width:100%;">
        <thead>
            <tr>
            <th scope="col">Actual value</th>
            <th scope="col">Predicted value</th>
            </tr>



            </thead>
            <tbody>



        </tbody>
        </table>
    `
    const plot_curveHTML = `
        <div class="card-body" style="padding:0.rem;">
            <div class="row" style="height:520px;">
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
        'accuracy': [data.accuracy,'Accuracy'],
        'r_square': [data.r_square,'Coefficient of determination'],
        'mean_sq_error': [data.mean_sq_error,'Mean squared error'],
        'mean_abs_error': [data.mean_abs_error,'Mean absolute error'],
        'precision': [data.precision, 'Precision'],
        'cross_val': [data.cross_val,'Cross validation'],
        'recall': [data.recall,'Recall'],
        'f1_metric': [data.f1_metric,'F1 metric'],
        'conf_matrix': [`<table id="table_confusionMatrixDecTree" class='table table-bordered' style="width:100%; margin-bottom:5px;">
                <thead>
                    <tr>

                        </tr>
                </thead>
                <tbody>

                </tbody>
                </table>`,'Confusion matrix'],
        'report': [` <table id="table_classReportDecTree" class='table table-bordered' style="width:100%;margin-bottom:5px;">
                <thead>
                    <tr>

                    </tr>
                </thead>
                <tbody>

                </tbody>
            </table>`,'Classification report'],
    };
    $(body).append(
        `
        <div class="row" id="DecTreeResults">

        </div>
    `
    );
    if ('dec_reg_summary' in data) {
        $('#DecTreeResults').append(
            `
            <div class="card col-7" style="width:100%;">
                <div class="card-header" style="color:var(--primary-color);padding:0px">
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
        $('.simpletable').each(function(){
            $(this).attr('class','table table-bordered table-sm')
            $(this).find("th").each(function(){
                $(this).css('text-align','center')
            });
            $(this).find("td").each(function(){
                $(this).css('text-align','center')
            });
        });
    };
    var title
    if (tree) {
        title = "Plot"
    } else {
        title = "Plot"
    }
    $('#DecTreeResults').append(`
    <div class="row1" id="rightContainerDT" style="width:99%;margin:auto">
        <div class="row card">
            <div class="card-header" style="color:var(--primary-color);padding-bottom:0px; background:whitesmoke;">
                <h5 class="mb-3" style="text-align:center;background:whitesmoke;">
                    ${title}
                </h5>
            </div>
            <div class="col-12" id="plotContainerDecTree" style="display: none;height:450px">

            </div>
        </div>
        <div class="row card">
            <div class="card-header" style="color:var(--primary-color); padding-bottom:0px; background:whitesmoke;">
                <h5 class="mb-3" style="text-align:center;">
                    Model summary
                </h5>
            </div>
            <div class="card-body row">
                <div class="col-6" id="plotContainerDecTree2" style="display: none; margin-bottom:10px; height:46vh;">

                </div>
                <div class="col-6" id="plotContainerDecTree3" style="display: none; margin-bottom:10px; height:46vh;">

                </div>
                <div class="col-6" id="plotContainerDecTree4" style="display: none; margin-bottom:10px;">

                </div>
                <div class="col-6" id="scoreSpaceDecTree" style="display: none; margin-left: 0%; flex-wrap:wrap">
                    <p style="font-weight:bold; margin-top:20px">Scores:</p>
                    <table id="tableParameters" class='table table-bordered' style="width:100%;margin-bottom:20px;">
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
    `)
    let htmlHead, htmlBody
    for (const key in data) {
        if (data.hasOwnProperty(key)) {
            if (key === 'plot_tree') {
                $("#plotContainerDecTree").css('display', 'block');
                let htmlString = plot_curveHTML;
                $('#plotContainerDecTree').append(htmlString);
            } else if (key === 'roc_curve') {
                $("#plotContainerDecTree2").css('display', 'flex');
                let htmlString = roc_curveHTML;
                $('#plotContainerDecTree2').append(htmlString);
            } else if (key === 'actplot'){
                $("#plotContainerDecTree3").css('display', 'flex');
                let htmlString = fit_curveHTML;
                $('#plotContainerDecTree3').append(htmlString);
                $("#plotContainerDecTree4").css('display', 'block');
                $('#plotContainerDecTree4').append(fit_curve_table);

            } else if (key in outputHTML) {
                $("#scoreSpaceDecTree").css('display', 'block');
                let htmlString = outputHTML[key];
                if (key === 'report') {
                    $('#scoreSpaceDecTree').prepend(htmlString[0]);
                    $('#scoreSpaceDecTree').prepend(`<p style="font-weight:bold;">${htmlString[1]}:</p>`)
                    $("#table_classReportDecTree tbody").empty();
                    $("#table_classReportDecTree thead tr").empty()
                    for(let [key,value] of Object.entries(data.report[0]) ){
                        $(`#table_classReportDecTree`).find('thead tr').eq(0).append(`<th style="text-align:center;">${key}</th>`)
                    };
                    for (var i = 0; i < data.report.length; i++) {
                        var string=`<tr>`
                            for(let [key,value] of Object.entries(data.report[i]) ){
                                string+=`<td style="text-align:center;">${value}</td>`
                            }
                            string+=`</tr>`
                            $('#table_classReportDecTree').find('tbody').append(string)
                        };
                    } else if (key === 'conf_matrix') {
                        $('#scoreSpaceDecTree').prepend(htmlString[0]);
                        $('#scoreSpaceDecTree').prepend(`<p style="font-weight:bold;">${htmlString[1]}:</p>`)
                        $("#table_confusionMatrixDecTree tbody").empty();
                        $("#table_confusionMatrixDecTree thead tr").empty()
                        for(let [key,value] of Object.entries(data.conf_matrix[0]) ){
                            $(`#table_confusionMatrixDecTree`).find('thead tr').eq(0).append(`<th style="text-align:center;">${key}</th>`)
                        };
                        for (var i = 0; i < data.conf_matrix.length; i++) {
                            var string=`<tr>`
                                for(let [key,value] of Object.entries(data.conf_matrix[i]) ){
                                    string+=`<td style="text-align:center;">${value}</td>`
                                }
                                string+=`</tr>`
                                $('#table_confusionMatrixDecTree').find('tbody').append(string)
                            };

                        } else {


                                    htmlHead = `<th>`+ outputHTML[key][1] + `</th>`;
                                    htmlBody =  `<td>` + outputHTML[key][0] + `</td>`;
                                    $('#scoreSpaceDecTree').find('#tableParameters').find('thead').find('tr').append(htmlHead);
                                    $('#scoreSpaceDecTree').find('#tableParameters').find('tbody').find('tr').append(htmlBody);

                            }
            };
        };
    };
    $('#plotContainerDecTree').closest(".card").css('display','none');


    if ('actual' in data){
        for (var i = 0; i < data.actual.length; i++) {
            var string=`<tr>`
            string+=`<td>${data.actual[i]}</td>`
            string+=`<td>${data.predict[i]}</td>`



            string+=`</tr>`
            $('#actual_grid').find('tbody').append(string)
        };
    }
    datatablesFuncAvsP('actual_grid');
    datatablesFunc('table_confusionMatrixDecTree')
    datatablesFunc('table_classReportDecTree')
    datatablesFunc('tableParameters')
    $('.dt-buttons').css('margin-left','3px');
}

for (let i = 0; i < createViewIdList.length; i++){
    var embededComputationBtn = $(
          `#${createViewIdList[i]}_tab_content`
    ).find(`#calval_embededComputation_${createViewIdList[i]}`)
    var compjs = $(`#${createViewIdList[i]}_tab_content`).find('.compjs')
    if (embededComputationBtn.length > 0){
      var attrdata = $(embededComputationBtn).attr('data-list')
      const elementId = $(embededComputationBtn).attr('data-elementid')
      if (attrdata != '' ||attrdata != '{}'){
        let compModelName = ''
        let parsedAttrData = JSON.parse(attrdata)
        let allOkFlag = 1
        let allok = ''
        for (let y in parsedAttrData){
          compModelName = y
          for (let j in parsedAttrData[y]){
            if (parsedAttrData[y][j][2] == 'auto_trigger'){
            let tableName = j
            let valuesDic = {}
            let listOfInputs = []
            let datatypeList = []
            let compDatatype = ""
            listOfInputs.push(...parsedAttrData[y][j][0])
            let lastInput = listOfInputs.slice(-1)
            let okay = 'no'
            for (let g in listOfInputs){
                okay = 'no'
                $(`#id_${listOfInputs[g]}_${elementId}`).on('change dp.change',function(){
                    okay = 'no'
                    for (let r in listOfInputs){
                        allok = 'no'
                        if  ($(`#id_${listOfInputs[r]}_${elementId}`).val() == '' || $(`#id_${listOfInputs[r]}_${elementId}`).val() == null){
                            allok = 'no'
                        }else{
                            allok = 'yes'
                        }
                    }
                    if (allok == 'yes'){
                        okay = 'yes'
                    }else{
                        okay = 'no'
                    }
                    if (okay == 'yes'){
                        for (let i in listOfInputs){
                          allOkFlag = 1
                        let compCol = $(`#id_${listOfInputs[i]}_${elementId}`)
                        .attr('id')
                        .replace('id_', '')
                        .replace('_' + elementId, '')

                        let compVal = $(`#id_${listOfInputs[i]}_${elementId}`).val()
                        if (compVal == '' || compVal == null){
                            allOkFlag = 0
                            break
                        }
                        compDatatype = $(`#id_${listOfInputs[i]}_${elementId}`).attr('datatype')
                        if (compDatatype == 'IntegerField' || compDatatype == 'BigIntegerField'){
                          valuesDic[compCol] = parseInt(compVal)
                        }else if(compDatatype == 'FloatField'){
                          valuesDic[compCol] = parseFloat(compVal)
                        }else{
                          valuesDic[compCol] = compVal
                        }
                      }
                        datatypeList.push(compDatatype)
                        if (allOkFlag == 1){

                        $.ajax({
                          url: `/users/${urlPath}/dynamicVal/`,
                          data: {
                            element_id: elementId,
                            operation: `calculate_embeded_computation`,
                            values_dic: JSON.stringify(valuesDic),
                            datatype_list: JSON.stringify(datatypeList),
                            table_name: JSON.stringify(tableName),
                            compModelName:JSON.stringify(compModelName),
                          },
                          type: 'POST',
                          dataType: 'json',
                          success: function (context) {
                                if (parsedAttrData[y][j][3] == 'full_output'){
                                  if (context.error_msg =='no'){
                                  let data = context.data
                                  if (data.element_error_message == 'Success') {
                                    if (data.output_display_type === 'individual') {
                                        if (data.name != "Export Data") {
                                            if (data.name === "Logistic Regression") {
                                                $(`#embededComputationCreateViewBody_${elementId}`).empty();
                                                displayOutputLogReg(data.content,`#embededComputationCreateViewBody_${elementId}`,`#embededComputationCreateView_${elementId}`);
                                                $(`#embededComputationCreateView_${elementId}`).modal('show');
                                            } else if (data.name === "Linear Regression") {
                                                $(`#embededComputationCreateViewBody_${elementId}`).empty();
                                                displayOutputLinReg(data.content,`#embededComputationCreateViewBody_${elementId}`,`#embededComputationCreateView_${elementId}`);
                                                $(`#embededComputationCreateView_${elementId}`).modal('show');
                                                initialise_table('#table_ActualVFittedLinReg');
                                            } else if (data.name === "Goodness Of Fit Test") {
                                                displayOutputFitTest(data.content,`#embededComputationCreateViewBody_${elementId}`,0,`#embededComputationCreateView_${elementId}`)
                                                $(`#embededComputationCreateView_${elementId}`).modal('show');
                                            } else if(data.name == "Fit Discrete"){
                                                displayOutputFitDiscrete(data.content,`#embededComputationCreateViewBody_${elementId}`,0,`#embededComputationCreateView_${elementId}`)
                                                $(`#embededComputationCreateView_${elementId}`).modal('show');
                                            } else if (data.name === "CART" || data.name == "CART Algorithm") {
                                                $(`#embededComputationCreateViewBody_${elementId}`).css('height','640px');
                                                $(`#embededComputationCreateViewBody_${elementId}`).empty();
                                                displayOutputDecTree(data.content,`#embededComputationCreateViewBody_${elementId}`,`#embededComputationCreateView_${elementId}`);
                                                $(`#embededComputationCreateView_${elementId}`).modal('show');
                                                setTimeout(() => {
                                                    $('#actual_grid').DataTable().columns.adjust()
                                                    $('#table_confusionMatrixDecTree').DataTable().columns.adjust()
                                                    $('#table_classReportDecTree').DataTable().columns.adjust()
                                                    $('#tableParameters').DataTable().columns.adjust()
                                                },500)
                                            } else if (data.name == "Boosting Algorithm") {
                                                $(`#embededComputationCreateViewBody_${elementId}`).css('height','640px');
                                                $(`#embededComputationCreateViewBody_${elementId}`).empty();
                                                displayOutputAB(data.content,true,`#embededComputationCreateViewBody_${elementId}`,`#embededComputationCreateView_${elementId}`);
                                                $(`#embededComputationCreateView_${elementId}`).modal('show');
                                                setTimeout(() => {
                                                    $('#actual_grid_ba').DataTable().columns.adjust()
                                                    $('#actual_grid').DataTable().columns.adjust()
                                                    $('#table_confusionMatrixDecTree').DataTable().columns.adjust()
                                                    $('#table_classReportDecTree').DataTable().columns.adjust()
                                                    $('#tableParameters').DataTable().columns.adjust()
                                                },500)
                                            }
                                            else if (data.name === "Interest Rate Products" || data.name === "Equities" || data.name === "Mutual Fund") {
                                                displayResultsFinInstrument(data.content,`#embededComputationCreateViewBody_${elementId}`,`#embededComputationCreateView_${elementId}`);
                                                $(`#embededComputationCreateView_${elementId}`).modal('show');
                                                initialiseTableResults()
                                                initialise_table_results_2()
                                                initialise_table_results_3()
                                            } else if (data.name === "Optimiser") {
                                                displayResultsOptimizer(data.content,`#embededComputationCreateViewBody_${elementId}`,0,`#embededComputationCreateView_${elementId}`);
                                                $(`#embededComputationCreateView_${elementId}`).modal('show');
                                                initialiseTableResults()
                                                initialise_table_results_2()
                                                initialise_table_results_4()
                                            }
                                            else if (data.name === "IR Curve Bootstrapping") {
                                                displayBootStrapOptimizer(data.content,`#embededComputationCreateViewBody_${elementId}`,0,`#embededComputationCreateView_${elementId}`);
                                                $(`#embededComputationCreateView_${elementId}`).modal('show');
                                                initialiseTableResults()
                                            }
                                            else if (data.name == "Analyse Time Series Data"){
                                                if(data.existing_configuration == "No"){
                                                    $(`#embededComputationCreateViewBody_${elementId}`).empty()
                                                    $(`#embededComputationCreateViewBody_${elementId}`).append(`
                                                    <p style="color:red;margin-left:0.5rem;">Run failed. Please save the configuration.</p>
                                                    `)
                                                    $(`#embededComputationCreateView_${elementId}`).modal('show')
                                                }
                                                else{
                                                    analyseTSData(data.content,`#embededComputationCreateViewBody_${elementId}`,`#embededComputationCreateView_${elementId}`)
                                                }
                                            }
                                            else if (data.name == "Train an ARIMA Model"){
                                                if(data.content.existing_configuration == "No"){
                                                    $(`#embededComputationCreateViewBody_${elementId}`).empty()
                                                    $(`#embededComputationCreateViewBody_${elementId}`).append(`
                                                    <p style="color:red;margin-left:0.5rem;">Run failed. Please save the configuration.</p>
                                                    `)
                                                    $(`#embededComputationCreateView_${elementId}`).modal('show')
                                                }
                                                else{
                                                    trainARIMARun(data.content,`#embededComputationCreateViewBody_${elementId}`,`#embededComputationCreateView_${elementId}`)
                                                }
                                            }
                                            else if (data.name == "Train a GARCH Model"){
                                                if(data.content.existing_configuration == "No"){
                                                    $(`#embededComputationCreateViewBody_${elementId}`).empty()
                                                    $(`#embededComputationCreateViewBody_${elementId}`).append(`
                                                    <p style="color:red;margin-left:0.5rem;">Run failed. Please save the configuration.</p>
                                                    `)
                                                    $(`#embededComputationCreateView_${elementId}`).modal('show')
                                                }
                                                else{

                                                    trainGARCHModel(data.content,`#embededComputationCreateViewBody_${elementId}`,`#embededComputationCreateView_${elementId}`)
                                                }
                                            }
                                            else if (data.name == "Portfolio Valuation"){
                                                portfolio_valuation_output(data.content,`#embededComputationCreateViewBody_${elementId}`,`#embededComputationCreateView_${elementId}`)
                                            }

                                            else if (data.name === "Copula") {
                                                displayOutputCopulaFunc(data.content,`#embededComputationCreateViewBody_${elementId}`,0,`#embededComputationCreateView_${elementId}`);
                                                $(`#embededComputationCreateView_${elementId}`).modal('show')
                                            }
                                            else if (data.name === "VaR Backtesting") {
                                                displayResultsBacktest(data.content,`#embededComputationCreateViewBody_${elementId}`,0,`#embededComputationCreateView_${elementId}`)
                                                $(`#embededComputationCreateView_${elementId}`).modal('show')
                                                initialiseTableResults()
                                            }
                                            else if (data.name == "Train an EWMA Model"){
                                                if(data.content.existing_configuration == "No"){
                                                    $(`#embededComputationCreateViewBody_${elementId}`).empty()
                                                    $(`#embededComputationCreateViewBody_${elementId}`).append(`
                                                    <p style="color:red;margin-left:0.5rem;">Run failed. Please save the configuration.</p>
                                                    `)
                                                    $(`#embededComputationCreateView_${elementId}`).modal('show')
                                                }
                                                else{
                                                    trainEWMARun(data.content,`#embededComputationCreateViewBody_${elementId}`,`#embededComputationCreateView_${elementId}`)
                                                }
                                            }
                                            else {
                                                displayTabularOutput(data.content,`#embededComputationCreateViewBody_${elementId}`,`#embededComputationCreateView_${elementId}`);
                                            };
                                        }
                                    }
                                  } else {
                                    Swal.fire({icon: 'error',text: data.element_error_message});
                                  }
                              }else{
                                  let error = context.e_list.slice(-1)
                                  Swal.fire({icon: 'error',text: error});
                              }
                                }
                                  else{
                                if (context.error_msg =='no'){
                                    for (let k in parsedAttrData[y][j][1]){
                                      for (let l in context.data.content[0]){
                                        if (parsedAttrData[y][j][1][k] == l){
                                          let targetColumnDataType =  $(`#id_${parsedAttrData[y][j][1][k]}_${elementId}`).attr('datatype')
                                          if (targetColumnDataType == 'IntegerField' || targetColumnDataType == 'BigIntegerField'){
                                            $(`#id_${parsedAttrData[y][j][1][k]}_${elementId}`).val(parseInt(context.data.content[0][l])).trigger('change')
                                          }else if (targetColumnDataType == 'FloatField'){
                                            $(`#id_${parsedAttrData[y][j][1][k]}_${elementId}`).val(parseFloat(context.data.content[0][l])).trigger('change')
                                          }else{
                                            $(`#id_${parsedAttrData[y][j][1][k]}_${elementId}`).val(context.data.content[0][l]).trigger('change')
                                          }
                                        }
                                      }






                                    }


                                }else{
                                  let error = context.e_list.slice(-1)
                                  Swal.fire({icon: 'error',text: error});

                              }
                          }
                          },
                          error: function () {
                            Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                          },
                        })
                      }
                      }
                })

            }



          }
          }
        }
      }
    }
    if(compjs.length > 0){
      for(let i=0;i<compjs.length;i++){
        let attrdata = $(compjs).attr('data-jsattr')
        const elementId = $(compjs).attr('id').split('_').pop()
        if (attrdata != '' ||attrdata != '[]'){
            let compModelName = ''
            let parsedAttrData = JSON.parse(attrdata)
            let allOkFlag = 1
            let allok = ''
            for (let y in parsedAttrData){
                if(parsedAttrData[y]["parentvalue"] == "Validation based message"){

                    let tableName = parsedAttrData[y]["table"]
                    let msg_txt = parsedAttrData[y]["msg_text"]
                    let condition = parsedAttrData[y]["finaljsattr"][0][0]["condition"]["styleValidation"]
                    let normal_txt_color = parsedAttrData[y]["finaljsattr"][0][0]["text_color"]
                    let regex = /\{(\w+)\}/g;
                    let result = [];
                    let match = []
                    let valuesDic = {}
                    let datatypeList = []
                    let compDatatype = ""
                    let eq_model_name = parsedAttrData[y]["eqid"]
                    let curr_col = parsedAttrData[y]["finaljsattr"][0][0]["table_column"]
                    while (match = regex.exec(msg_txt))
                    {
                        result.push(match[1]);
                    }
                    let set = new Set(result);
                    result = Array.from(set);

                    let listOfInputs = []
                    listOfInputs.push(...parsedAttrData[y]["compute_fields"])
                    let okay = 'no'
                    for (let g in listOfInputs){
                        okay = 'no'
                        $(`#id_${listOfInputs[g]}_${elementId}`).on('change',function(){
                            okay = 'no'
                            for (let r in listOfInputs){
                                allok = 'no'
                                if  ($(`#id_${listOfInputs[r]}_${elementId}`).val() == '' || $(`#id_${listOfInputs[r]}_${elementId}`).val() == null){
                                    allok = 'no'
                                }else{
                                    allok = 'yes'
                                }
                            }
                            if (allok == 'yes'){
                                okay = 'yes'
                            }else{
                                okay = 'no'
                            }
                            if (okay == 'yes'){
                                for (let i in listOfInputs){
                                allOkFlag = 1
                                let compCol = $(`#id_${listOfInputs[i]}_${elementId}`)
                                .attr('id')
                                .replace('id_', '')
                                .replace('_' + elementId, '')

                                let compVal = $(`#id_${listOfInputs[i]}_${elementId}`).val()
                                if (compVal == '' || compVal == null){
                                    allOkFlag = 0
                                    break
                                }

                                compDatatype = $(`#id_${listOfInputs[i]}_${elementId}`).attr('datatype')

                                valuesDic[compCol] = compVal

                                datatypeList.push(compDatatype)
                            }
                                if (allOkFlag == 1){

                                    $.ajax({
                                    url: `/users/${urlPath}/dynamicVal/`,
                                    data: {
                                        element_id: elementId,
                                        operation: 'computation_js_execute_model',
                                        column: curr_col,
                                        table_name: tableName,
                                        msg_col: JSON.stringify(result),
                                        msg_txt: msg_txt,
                                        condition: JSON.stringify(condition),
                                        eq_model_name: eq_model_name,
                                        valuesDic: JSON.stringify(valuesDic),
                                        datatypeList: JSON.stringify(datatypeList)
                                    },
                                    type: 'POST',
                                    dataType: 'json',
                                    success: function (data) {
                                        if(data.error_msg == "Success"){
                                            if(data.final_msg){
                                                $(`#id_${data.column}_${data.element_id}`).parent().find('small').remove()
                                                $(`#id_${data.column}_${data.element_id}`).parent().append(`<small style='color:${normal_txt_color}'>${data.final_msg}</small>`)
                                            }else{
                                                $(`#id_${data.column}_${data.element_id}`).parent().find('small').remove()
                                                $(`#id_${data.column}_${data.element_id}`).parent().append(`<small style='color:${normal_txt_color}'>No data found for selected inputs</small>`)
                                            }
                                        }else{
                                            $(`#id_${data.column}_${data.element_id}`).parent().find('small').remove()
                                        }
                                    },
                                    error: function () {
                                        Swal.fire({icon: 'error',text: 'Error! Please try again.'});
                                    },
                                    })

                                }
                            }
                        })

                    }
                }
            }
        }
      }
    }
  }
  function embededComputation(obj){
    const elementId = $(obj).attr('data-elementid')
    let attrData = $(obj).attr('data-list')
    let savedhtml = $(obj).html()
    $(obj).html(`<i class="fa fa-circle-notch fa-spin"></i>`)
    let allOkFlag = 1
    if (attrData != ''){
      let parsedAttrData = JSON.parse(attrData)
      let compModelName = ''
      for (let y in parsedAttrData){
        compModelName = y
        for (let j in parsedAttrData[y]){
          let tableName = j
          let valuesDic = {}
          let datatypeList = []
          let listOfInputs = []
          listOfInputs.push(...parsedAttrData[y][j][0])
          if (parsedAttrData[y][j][0] == ['']){
            allOkFlag = 1
          }
          for (let o in listOfInputs){
            allOkFlag = 1
            let compCol = $(`#id_${listOfInputs[o]}_${elementId}`)
            .attr('id')
            .replace('id_', '')
            .replace('_' + elementId, '')
            let compVal = $(`#id_${listOfInputs[o]}_${elementId}`).val()
            if (compVal == '' || compVal == null){
                Swal.fire({icon: 'info',text: `Empty Input ${listOfInputs[o]}`});
                  allOkFlag = 0
                  break

              }
            let compDatatype = $(`#id_${listOfInputs[o]}_${elementId}`).attr('datatype')
            if (compDatatype == 'IntegerField' || compDatatype == 'BigIntegerField'){
              valuesDic[compCol] = parseInt(compVal)
            }else if(compDatatype == 'FloatField'){
              valuesDic[compCol] = parseFloat(compVal)
            }else{
              valuesDic[compCol] = compVal
            }

            datatypeList.push(compDatatype)
          }
          if (allOkFlag == 1){

          $.ajax({
            url: `/users/${urlPath}/dynamicVal/`,
            data: {
              element_id: elementId,
              operation: `calculate_embeded_computation`,
              values_dic: JSON.stringify(valuesDic),
              datatype_list: JSON.stringify(datatypeList),
              table_name: JSON.stringify(tableName),
              compModelName:JSON.stringify(compModelName),
            },
            type: 'POST',
            dataType: 'json',
            success: function (context) {
                $(obj).html(savedhtml)
              if (parsedAttrData[y][j][3] == 'full_output'){
                if (context.error_msg =='no'){
                let data = context.data
                if (data.element_error_message == 'Success') {
                    if (data.output_display_type === 'individual') {
                        if (data.name != "Export Data") {
                            if (data.name === "Logistic Regression") {
                                $(`#embededComputationCreateViewBody_${elementId}`).empty();
                                displayOutputLogReg(data.content,`#embededComputationCreateViewBody_${elementId}`,`#embededComputationCreateView_${elementId}`);
                                $(`#embededComputationCreateView_${elementId}`).modal('show');
                            } else if (data.name === "Linear Regression") {
                                $(`#embededComputationCreateViewBody_${elementId}`).empty();
                                displayOutputLinReg(data.content,`#embededComputationCreateViewBody_${elementId}`,`#embededComputationCreateView_${elementId}`);
                                $(`#embededComputationCreateView_${elementId}`).modal('show');
                                initialise_table('#table_ActualVFittedLinReg');
                            } else if (data.name === "Goodness Of Fit Test") {
                                displayOutputFitTest(data.content,`#embededComputationCreateViewBody_${elementId}`,0,`#embededComputationCreateView_${elementId}`)
                                $(`#embededComputationCreateView_${elementId}`).modal('show');
                            } else if(data.name == "Fit Discrete"){
                                displayOutputFitDiscrete(data.content,`#embededComputationCreateViewBody_${elementId}`,0,`#embededComputationCreateView_${elementId}`)
                                $(`#embededComputationCreateView_${elementId}`).modal('show');
                            } else if (data.name === "CART" || data.name == "CART Algorithm") {
                                $(`#embededComputationCreateViewBody_${elementId}`).css('height','640px');
                                $(`#embededComputationCreateViewBody_${elementId}`).empty();
                                displayOutputDecTree(data.content,`#embededComputationCreateViewBody_${elementId}`,`#embededComputationCreateView_${elementId}`);
                                $(`#embededComputationCreateView_${elementId}`).modal('show');
                                setTimeout(() => {
                                    $('#actual_grid').DataTable().columns.adjust()
                                    $('#table_confusionMatrixDecTree').DataTable().columns.adjust()
                                    $('#table_classReportDecTree').DataTable().columns.adjust()
                                    $('#tableParameters').DataTable().columns.adjust()
                                },500)
                            } else if (data.name == "Boosting Algorithm") {
                                $(`#embededComputationCreateViewBody_${elementId}`).css('height','640px');
                                $(`#embededComputationCreateViewBody_${elementId}`).empty();
                                displayOutputAB(data.content,true,`#embededComputationCreateViewBody_${elementId}`,`#embededComputationCreateView_${elementId}`);
                                $(`#embededComputationCreateView_${elementId}`).modal('show');
                                setTimeout(() => {
                                    $('#actual_grid_ba').DataTable().columns.adjust()
                                    $('#actual_grid').DataTable().columns.adjust()
                                    $('#table_confusionMatrixDecTree').DataTable().columns.adjust()
                                    $('#table_classReportDecTree').DataTable().columns.adjust()
                                    $('#tableParameters').DataTable().columns.adjust()
                                },500)
                            }
                            else if (data.name === "Interest Rate Products" || data.name === "Equities" || data.name === "Mutual Fund") {
                                displayResultsFinInstrument(data.content,`#embededComputationCreateViewBody_${elementId}`,`#embededComputationCreateView_${elementId}`);
                                $(`#embededComputationCreateView_${elementId}`).modal('show');
                                initialiseTableResults()
                                initialise_table_results_2()
                                initialise_table_results_3()
                            } else if (data.name === "Optimiser") {
                                displayResultsOptimizer(data.content,`#embededComputationCreateViewBody_${elementId}`,0,`#embededComputationCreateView_${elementId}`);
                                $(`#embededComputationCreateView_${elementId}`).modal('show');
                                initialiseTableResults()
                                initialise_table_results_2()
                                initialise_table_results_4()
                            }
                            else if (data.name === "IR Curve Bootstrapping") {
                                displayBootStrapOptimizer(data.content,`#embededComputationCreateViewBody_${elementId}`,0,`#embededComputationCreateView_${elementId}`);
                                $(`#embededComputationCreateView_${elementId}`).modal('show');
                                initialiseTableResults()
                            }
                            else if (data.name == "Analyse Time Series Data"){
                                if(data.existing_configuration == "No"){
                                    $(`#embededComputationCreateViewBody_${elementId}`).empty()
                                    $(`#embededComputationCreateViewBody_${elementId}`).append(`
                                    <p style="color:red;margin-left:0.5rem;">Run failed. Please save the configuration.</p>
                                    `)
                                    $(`#embededComputationCreateView_${elementId}`).modal('show')
                                }
                                else{
                                    analyseTSData(data.content,`#embededComputationCreateViewBody_${elementId}`,`#embededComputationCreateView_${elementId}`)
                                }
                            }
                            else if (data.name == "Train an ARIMA Model"){
                                if(data.content.existing_configuration == "No"){
                                    $(`#embededComputationCreateViewBody_${elementId}`).empty()
                                    $(`#embededComputationCreateViewBody_${elementId}`).append(`
                                    <p style="color:red;margin-left:0.5rem;">Run failed. Please save the configuration.</p>
                                    `)
                                    $(`#embededComputationCreateView_${elementId}`).modal('show')
                                }
                                else{
                                    trainARIMARun(data.content,`#embededComputationCreateViewBody_${elementId}`,`#embededComputationCreateView_${elementId}`)
                                }
                            }
                            else if (data.name == "Train a GARCH Model"){
                                if(data.content.existing_configuration == "No"){
                                    $(`#embededComputationCreateViewBody_${elementId}`).empty()
                                    $(`#embededComputationCreateViewBody_${elementId}`).append(`
                                    <p style="color:red;margin-left:0.5rem;">Run failed. Please save the configuration.</p>
                                    `)
                                    $(`#embededComputationCreateView_${elementId}`).modal('show')
                                }
                                else{

                                    trainGARCHModel(data.content,`#embededComputationCreateViewBody_${elementId}`,`#embededComputationCreateView_${elementId}`)
                                }
                            }
                            else if (data.name == "Portfolio Valuation"){
                                portfolio_valuation_output(data.content,`#embededComputationCreateViewBody_${elementId}`,`#embededComputationCreateView_${elementId}`)
                            }

                            else if (data.name === "Copula") {
                                displayOutputCopulaFunc(data.content,`#embededComputationCreateViewBody_${elementId}`,0,`#embededComputationCreateView_${elementId}`);
                                $(`#embededComputationCreateView_${elementId}`).modal('show')
                            }
                            else if (data.name === "VaR Backtesting") {
                                displayResultsBacktest(data.content,`#embededComputationCreateViewBody_${elementId}`,0,`#embededComputationCreateView_${elementId}`)
                                $(`#embededComputationCreateView_${elementId}`).modal('show')
                                initialiseTableResults()
                            }
                            else if (data.name == "Train an EWMA Model"){
                                if(data.content.existing_configuration == "No"){
                                    $(`#embededComputationCreateViewBody_${elementId}`).empty()
                                    $(`#embededComputationCreateViewBody_${elementId}`).append(`
                                    <p style="color:red;margin-left:0.5rem;">Run failed. Please save the configuration.</p>
                                    `)
                                    $(`#embededComputationCreateView_${elementId}`).modal('show')
                                }
                                else{
                                    trainEWMARun(data.content,`#embededComputationCreateViewBody_${elementId}`,`#embededComputationCreateView_${elementId}`)
                                }
                            }
                            else {
                                displayTabularOutput(data.content,`#embededComputationCreateViewBody_${elementId}`,`#embededComputationCreateView_${elementId}`);
                            };
                        }
                    }
                } else {
                    Swal.fire({icon: 'error',text: data.element_error_message});
                }
            }else{
                let error = context.e_list.slice(-1)
                Swal.fire({icon: 'error',text: error});

            }
              }
                else{
              if (context.error_msg =='no'){
                  for (let k in parsedAttrData[y][j][1]){
                    for (let l in context.data.content[0]){
                      if (parsedAttrData[y][j][1][k] == l){
                        let targetColumnDataType =  $(`#id_${parsedAttrData[y][j][1][k]}_${elementId}`).attr('datatype')
                        if (targetColumnDataType == 'IntegerField' || targetColumnDataType == 'BigIntegerField'){
                          $(`#id_${parsedAttrData[y][j][1][k]}_${elementId}`).val(parseInt(context.data.content[0][l])).trigger('change')
                        }else if (targetColumnDataType == 'FloatField'){
                          $(`#id_${parsedAttrData[y][j][1][k]}_${elementId}`).val(parseFloat(context.data.content[0][l])).trigger('change')
                        }else{
                          $(`#id_${parsedAttrData[y][j][1][k]}_${elementId}`).val(context.data.content[0][l]).trigger('change')
                        }
                      }
                    }






                  }


              }else{
                let error = context.e_list.slice(-1)
                Swal.fire({icon: 'error',text: error});


            }
        }
        $(obj).html(savedhtml)
            },
            error: function () {
                Swal.fire({icon: 'error',text: 'Error! Please try again.'});
              $(obj).html(savedhtml)
            },
          })
        }
        }
      }
    }






  }
  window.embededComputation = embededComputation
  window.createViewIdList = createViewIdList
  export { initialise_table_results_5,
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
      displayOutputAB
    }
