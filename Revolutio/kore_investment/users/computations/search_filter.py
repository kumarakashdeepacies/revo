from config.settings.base import engine
from kore_investment.users.computations.db_centralised_function import (
    application_database_details_extractor,
    read_data_func,
)


def ViewFilter(
    table_name,
    mode_type="",
    user_engine=engine,
    request="",
    db_type="MSSQL",
    if_app_db=True,
    original_verbose_name=False,
    master_mode="no",
):
    if if_app_db and request:
        app_code, db_connection_name, user_db_engine, db_type, tenant = (
            application_database_details_extractor(request)
        )
    else:
        pass
    column_verbose_dict = {}
    column_type_dict = {}
    rtf_field_list = []
    if if_app_db:
        tablename = "users_" + str(table_name).lower()
        if type(table_name) != str:
            if original_verbose_name:
                column_verbose_dict = {
                    field.name: field.verbose_name
                    for field in table_name.concrete_fields
                    if field.get_internal_type() != "FileField"
                }
            else:
                column_verbose_dict = {
                    field.name: field.verbose_name.title()
                    for field in table_name.concrete_fields
                    if field.get_internal_type() != "FileField"
                }
            rtf_field_list = [
                field.name for field in table_name.concrete_fields if field.get_internal_type() == "RTFField"
            ]
            column_type_dict = {field.name: field.get_internal_type() for field in table_name.concrete_fields}
    else:
        tablename = table_name

    tableList = (
        read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "Tables",
                    "Columns": ["tablename"],
                },
                "condition": [],
            },
        )
    ).tablename.tolist()

    col_type_filters = {
        "nvarchar": [
            "Starts with",
            "Ends with",
            "Contains",
            "Equal to",
            "Not Starts with",
            "Not Ends with",
            "Not Contains",
            "Not Equal to",
            "IN",
            "NOT IN",
        ],
        "varchar": [
            "Starts with",
            "Ends with",
            "Contains",
            "Equal to",
            "Not Starts with",
            "Not Ends with",
            "Not Contains",
            "Not Equal to",
            "IN",
            "NOT IN",
        ],
        "VARCHAR2(32676)": [
            "Starts with",
            "Ends with",
            "Contains",
            "Equal to",
            "Not Starts with",
            "Not Ends with",
            "Not Contains",
            "Not Equal to",
            "IN",
            "NOT IN",
        ],
        "VARCHAR2": [
            "Starts with",
            "Ends with",
            "Contains",
            "Equal to",
            "Not Starts with",
            "Not Ends with",
            "Not Contains",
            "Not Equal to",
            "IN",
            "NOT IN",
        ],
        "NVARCHAR2": [
            "Starts with",
            "Ends with",
            "Contains",
            "Equal to",
            "Not Starts with",
            "Not Ends with",
            "Not Contains",
            "Not Equal to",
            "IN",
            "NOT IN",
        ],
        "CHAR": [
            "Starts with",
            "Ends with",
            "Contains",
            "Equal to",
            "Not Starts with",
            "Not Ends with",
            "Not Contains",
            "Not Equal to",
            "IN",
            "NOT IN",
        ],
        "character varying": [
            "Starts with",
            "Ends with",
            "Contains",
            "Equal to",
            "Not Starts with",
            "Not Ends with",
            "Not Contains",
            "Not Equal to",
            "IN",
            "NOT IN",
        ],
        "ConcatenationField": [
            "Starts with",
            "Ends with",
            "Contains",
            "Equal to",
            "Not Starts with",
            "Not Ends with",
            "Not Contains",
            "Not Equal to",
            "IN",
            "NOT IN",
        ],
        "DateField": [
            "Equal to",
            "Greater than",
            "Smaller than",
            "Not Equal to",
            "IN",
            "Greater than equal to",
            "Smaller than equal to",
        ],
        "TIMESTAMP(0)": [
            "Equal to",
            "Greater than",
            "Smaller than",
            "Not Equal to",
            "IN",
            "Greater than equal to",
            "Smaller than equal to",
        ],
        "HierarchyField": [
            "Starts with",
            "Ends with",
            "Contains",
            "Equal to",
            "Not Starts with",
            "Not Ends with",
            "Not Contains",
            "Not Equal to",
        ],
        "TextField": [
            "Starts with",
            "Ends with",
            "Contains",
            "Equal to",
            "Not Starts with",
            "Not Ends with",
            "Not Contains",
            "Not Equal to",
            "IN",
            "NOT IN",
        ],
        "text": [
            "Starts with",
            "Ends with",
            "Contains",
            "Equal to",
            "Not Starts with",
            "Not Ends with",
            "Not Contains",
            "Not Equal to",
            "IN",
            "NOT IN",
        ],
        "BLOB": [
            "Starts with",
            "Ends with",
            "Contains",
            "Equal to",
            "Not Starts with",
            "Not Ends with",
            "Not Contains",
            "Not Equal to",
            "IN",
            "NOT IN",
        ],
        "date": [
            "Equal to",
            "Greater than",
            "Smaller than",
            "Not Equal to",
            "IN",
            "NOT IN",
            "Greater than equal to",
            "Smaller than equal to",
        ],
        "DATE": [
            "Equal to",
            "Greater than",
            "Smaller than",
            "Not Equal to",
            "IN",
            "NOT IN",
            "Greater than equal to",
            "Smaller than equal to",
        ],
        "datetime": [
            "Equal to",
            "Greater than",
            "Smaller than",
            "Not Equal to",
            "IN",
            "NOT IN",
            "Greater than equal to",
            "Smaller than equal to",
        ],
        "timestamp without time zone": [
            "Equal to",
            "Greater than",
            "Smaller than",
            "Not Equal to",
            "IN",
            "NOT IN",
            "Greater than equal to",
            "Smaller than equal to",
        ],
        "time without time zone": [
            "Equal to",
            "Greater than",
            "Smaller than",
            "Not Equal to",
            "IN",
            "NOT IN",
            "Greater than equal to",
            "Smaller than equal to",
        ],
        "datetime2": [
            "Equal to",
            "Greater than",
            "Smaller than",
            "Not Equal to",
            "IN",
            "NOT IN",
            "Greater than equal to",
            "Smaller than equal to",
        ],
        "TIMESTAMP(6)": [
            "Equal to",
            "Greater than",
            "Smaller than",
            "Not Equal to",
            "IN",
            "NOT IN",
            "Greater than equal to",
            "Smaller than equal to",
        ],
        "TIMESTAMP": [
            "Equal to",
            "Greater than",
            "Smaller than",
            "Not Equal to",
            "IN",
            "NOT IN",
            "Greater than equal to",
            "Smaller than equal to",
        ],
        "time": [
            "Equal to",
            "Greater than",
            "Smaller than",
            "Not Equal to",
            "IN",
            "NOT IN",
            "Greater than equal to",
            "Smaller than equal to",
        ],
        "Time": [
            "Equal to",
            "Greater than",
            "Smaller than",
            "Not Equal to",
            "IN",
            "NOT IN",
            "Greater than equal to",
            "Smaller than equal to",
        ],
        "float": [
            "Equal to",
            "Greater than",
            "Smaller than",
            "Not Equal to",
            "IN",
            "NOT IN",
            "Greater than equal to",
            "Smaller than equal to",
        ],
        "double precision": [
            "Equal to",
            "Greater than",
            "Smaller than",
            "Not Equal to",
            "IN",
            "NOT IN",
            "Greater than equal to",
            "Smaller than equal to",
        ],
        "int": [
            "Equal to",
            "Greater than",
            "Smaller than",
            "Not Equal to",
            "IN",
            "NOT IN",
            "Greater than equal to",
            "Smaller than equal to",
        ],
        "NUMBER(3)": [
            "Equal to",
            "Greater than",
            "Smaller than",
            "Not Equal to",
            "IN",
            "NOT IN",
            "Greater than equal to",
            "Smaller than equal to",
        ],
        "NUMBER(38)": [
            "Equal to",
            "Greater than",
            "Smaller than",
            "Not Equal to",
            "IN",
            "NOT IN",
            "Greater than equal to",
            "Smaller than equal to",
        ],
        "NUMBER": [
            "Equal to",
            "Greater than",
            "Smaller than",
            "Not Equal to",
            "IN",
            "NOT IN",
            "Greater than equal to",
            "Smaller than equal to",
        ],
        "FLOAT": [
            "Equal to",
            "Greater than",
            "Smaller than",
            "Not Equal to",
            "IN",
            "NOT IN",
            "Greater than equal to",
            "Smaller than equal to",
        ],
        "bigint": [
            "Equal to",
            "Greater than",
            "Smaller than",
            "Not Equal to",
            "IN",
            "NOT IN",
            "Greater than equal to",
            "Smaller than equal to",
        ],
        "integer": [
            "Equal to",
            "Greater than",
            "Smaller than",
            "Not Equal to",
            "IN",
            "NOT IN",
            "Greater than equal to",
            "Smaller than equal to",
        ],
        "Integer": [
            "Equal to",
            "Greater than",
            "Smaller than",
            "Not Equal to",
            "IN",
            "NOT IN",
            "Greater than equal to",
            "Smaller than equal to",
        ],
        "SMALLINT": [
            "Equal to",
            "Greater than",
            "Smaller than",
            "Not Equal to",
            "IN",
            "NOT IN",
            "Greater than equal to",
            "Smaller than equal to",
        ],
        "bit": ["Equal to", "Not Equal to", "IN", "NOT IN"],
        "boolean": ["Equal to", "Not Equal to"],
        "Boolean": ["Equal to", "Not Equal to"],
        "BOOLEAN": ["Equal to", "Not Equal to"],
        "AutoField": [
            "Equal to",
            "Greater than",
            "Smaller than",
            "Not Equal to",
            "IN",
            "NOT IN",
            "Greater than equal to",
            "Smaller than equal to",
        ],
        "ForeignKey": [
            "Equal to",
            "Greater than",
            "Smaller than",
            "Not Equal to",
            "IN",
            "NOT IN",
            "Greater than equal to",
            "Smaller than equal to",
        ],
    }
    if db_type == "Oracle":
        column_info = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "all_tab_columns",
                    "Columns": ["column_name", "data_type"],
                },
                "condition": [
                    {
                        "column_name": "table_name",
                        "condition": "Equal to",
                        "input_value": tablename.upper(),
                        "and_or": "",
                    }
                ],
            },
            engine2=user_engine,
            db_type=db_type,
            if_app_db=if_app_db,
        )
        if if_app_db:
            column_info.column_name = column_info.column_name.str.lower()
        else:
            pass
    else:
        column_info = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "information_schema.columns",
                    "Columns": ["column_name", "data_type"],
                },
                "condition": [
                    {
                        "column_name": "table_name",
                        "condition": "Equal to",
                        "input_value": tablename,
                        "and_or": "",
                    },
                ],
            },
            engine2=user_engine,
            db_type=db_type,
            if_app_db=if_app_db,
        )

    column_name_list = [
        columnname
        for columnname, datatype in zip(column_info["column_name"], column_info["data_type"])
        if datatype != "varbinary" and columnname not in rtf_field_list
    ]
    for col in column_name_list:
        if not column_verbose_dict.get(col):
            column_verbose_dict[col] = col
    column_type_list = [
        datatype
        for columnname, datatype in zip(column_info["column_name"], column_info["data_type"])
        if datatype != "varbinary" and columnname not in rtf_field_list
    ]
    label_columns = {}
    for col_name in column_name_list:
        if column_verbose_dict.get(col_name):
            label_columns[col_name] = column_verbose_dict.get(col_name)
        else:
            label_columns[col_name] = col_name

    search_filters = {}
    for col_name, col_type in zip(column_name_list, column_type_list):
        if col_type in col_type_filters:
            search_filters[col_name] = col_type_filters[col_type]
        else:
            search_filters[col_name] = col_type_filters["varchar"]

    for col_name, col_type in zip(column_name_list, column_type_list):
        if col_type in col_type_filters:
            search_filters[col_name] = col_type_filters[col_type]
        else:
            search_filters[col_name] = col_type_filters["varchar"]

    form_fields = {}
    form_fields1 = {}
    form_fields2 = {}

    STRING = ""
    STRING1 = ""
    STRING2 = ""

    for col_name, col_type in zip(column_name_list, column_type_list):
        if col_type not in col_type_filters:
            col_type = "varchar"
        else:
            pass
        if master_mode != "yes":
            STRING = f"""<tr style="border-bottom:0.2px solid #1112;"><td class="dt-center"><div class="" style="max-width:15em;"><a href="javascript:void(0)" class="remove_filter fa fa-times" style="color:var(--primary-color);">&nbsp;<b style="font-family:Arial;font-size:12px;font-weight:200;">{column_verbose_dict[col_name]}</b></a></div></td>"""
        else:
            STRING = f"""<tr class="master_filter"><td class="dt-center"><div class="" style="max-width:15em;"><a href="javascript:void(0)" class="remove_filter fa fa-times" style="color:var(--primary-color);">&nbsp;<b style="font-family:Arial;font-size:12px;font-weight:200;">{column_verbose_dict[col_name]}</b></a></div></td>"""
        if mode_type == "customValidation":
            if master_mode != "yes":
                STRING += f"""<td class="dt-center"><div  style="max-width:15em;"><input type="text" placeholder='Constraint Name' name='Constraint_name'  class="textinput textInput form-control" required=""></div></td><td class="dt-center"><div class="" style="max-width:15em;"><input type="text" placeholder='Rule Set'  name='Rule_set' class="textinput textInput form-control" required="" ></div></td> <td class="dt-center"><div class="" style="max-width:25em;"><select class="form-control select2bs4" onchange="InOperationTag.call(this)" name={col_name} data-verbose_name="{column_verbose_dict[col_name]}" data-dropdown_purpose="select_filter_condition">"""
            else:
                STRING += f"""<td class="dt-center"><div  style="max-width:15em;"><input type="text" placeholder='Constraint Name' name='Constraint_name'  class="textinput textInput form-control" required=""></div></td><td class="dt-center"><div class="" style="max-width:15em;"><input type="text" placeholder='Rule Set'  name='Rule_set' class="textinput textInput form-control" required="" ></div></td>"""
        else:
            STRING += f"""<td class="dt-center"><div class="" style="max-width:25em;"><select class="form-control select2bs4" onchange="InOperationTag.call(this)" name={col_name} data-verbose_name="{column_verbose_dict[col_name]}" data-dropdown_purpose="select_filter_condition">"""

        if master_mode != "yes":
            STRING2 = f"""<tr style="border-bottom:0.2px solid #1112;"><td class="dt-center"><div class="" style="max-width:15em;"><a href="javascript:void(0)" class="remove_filter fa fa-times" style="color:var(--primary-color);">&nbsp;<b style="font-family:Arial;font-size:12px;font-weight:200;">{column_verbose_dict[col_name]}</b></a></div></td><td class="dt-center"><div class="" style="max-width:25em;"><select class="form-control select2bs4" onchange="InOperationTag.call(this)" name={col_name} data-verbose_name="{column_verbose_dict[col_name]}" data-dropdown_purpose="select_filter_condition">"""
            STRING1 = f"""<br><select class="form-control select2bs4" onchange="InOperationTag.call(this)" name={col_name} data-verbose_name="{column_verbose_dict[col_name]}" data-dropdown_purpose="select_filter_condition">"""
            for val in col_type_filters[col_type]:
                STRING = STRING + f'<option value="{val}">{val}</option>'
                STRING1 = STRING1 + f'<option value="{val}">{val}</option>'
                STRING2 = STRING2 + f'<option value="{val}">{val}</option>'

            if col_type in [
                "nvarchar",
                "varchar",
                "text",
                "character varying",
                "ConcatenationField",
                "VARCHAR2",
                "TEXT",
            ]:
                STRING = (
                    STRING
                    + f"""</select></div></td><td class="dt-center"><div class="" style="max-width:25em;"><input type="text" placeholder='{col_name}' name={col_name} maxlength="100" class="textinput textInput form-control" required="" ></div></td>"""
                )
                STRING2 = (
                    STRING2
                    + f"""</select></div></td><td class="dt-center"><div class="" style="max-width:25em;"><input type="text" placeholder='{col_name}' maxlength="100" class="textinput textInput form-control" required="" ></div></td><td class="dt-center"><div class="" style="max-width:25em;"><select data-dropdown_purpose="select_logical_operator"><option selected value="">-----</option><option value="AND">AND</option><option value="OR">OR</option></select></div></td>"""
                )

                STRING1 = (
                    STRING1
                    + f"""</select><br><div class=""><input type="text" placeholder="{col_name}" maxlength="100" class="textinput textInput form-control" required="" ></div>"""
                )

            elif col_type in [
                "float",
                "int",
                "bigint",
                "AutoField",
                "ForeignKey",
                "integer",
                "double precision",
                "NUMBER",
                "NUMBER(3)",
                "NUMBER(38)",
                "FLOAT",
                "SMALLINT",
            ]:
                if col_name in column_type_dict.keys():
                    if column_type_dict[col_name] == "ForeignKey":
                        STRING = (
                            STRING
                            + f"""</select></td><td class="dt-center"><div class="" style="max-width:25em;"><input type="number" data-type='ForeignKey' data-tablename='{table_name}' placeholder='{col_name}' name={col_name} step="any" class="numberinput form-control" required=""></div></td>"""
                        )
                        STRING2 = (
                            STRING2
                            + f"""</select></td><td class="dt-center"><div class="" style="max-width:25em;"><input type="number" data-type='ForeignKey' data-tablename='{table_name}' placeholder='{col_name}' step="any" class="numberinput form-control" required=""></div></td><td class="dt-center"><div class="" style="max-width:25em;"><select data-dropdown_purpose="select_logical_operator"><option selected value="">-----</option><option value="AND">AND</option><option value="OR">OR</option></select></div></td>"""
                        )

                        STRING1 = (
                            STRING1
                            + f"""</select><br><div class=""><input type="number" placeholder="{col_name}" data-type='ForeignKey' data-tablename='{table_name}' step="any" class="numberinput form-control" required=""></div>"""
                        )
                    else:
                        STRING = (
                            STRING
                            + f"""</select></td><td class="dt-center"><div class="" style="max-width:25em;"><input type="number"  data-tablename='{table_name}' placeholder='{col_name}' name={col_name} step="any" class="numberinput form-control" required=""></div></td>"""
                        )
                        STRING2 = (
                            STRING2
                            + f"""</select></td><td class="dt-center"><div class="" style="max-width:25em;"><input type="number"  data-tablename='{table_name}' placeholder='{col_name}' step="any" class="numberinput form-control" required=""></div></td><td class="dt-center"><div class="" style="max-width:25em;"><select data-dropdown_purpose="select_logical_operator"><option selected value="">-----</option><option value="AND">AND</option><option value="OR">OR</option></select></div></td>"""
                        )

                        STRING1 = (
                            STRING1
                            + f"""</select><br><div class=""><input type="number" placeholder="{col_name}"  data-tablename='{table_name}' step="any" class="numberinput form-control" required=""></div>"""
                        )

                else:
                    STRING = (
                        STRING
                        + f"""</select></td><td class="dt-center"><div class="" style="max-width:25em;"><input type="number"  data-tablename='{table_name}' placeholder='{col_name}' name={col_name} step="any" class="numberinput form-control" required=""></div></td>"""
                    )
                    STRING2 = (
                        STRING2
                        + f"""</select></td><td class="dt-center"><div class="" style="max-width:25em;"><input type="number"  data-tablename='{table_name}' placeholder='{col_name}' step="any" class="numberinput form-control" required=""></div></td><td class="dt-center"><div class="" style="max-width:25em;"><select data-dropdown_purpose="select_logical_operator"><option selected value="">-----</option><option value="AND">AND</option><option value="OR">OR</option></select></div></td>"""
                    )

                    STRING1 = (
                        STRING1
                        + f"""</select><br><div class=""><input type="number" placeholder="{col_name}"  data-tablename='{table_name}' step="any" class="numberinput form-control" required=""></div>"""
                    )
            elif col_type in ["bit", "bool", "boolean", "BOOLEAN"]:
                STRING = (
                    STRING
                    + f"""</select></td><td class="dt-center"><div class="" style="max-width:25em;"><input type="text" placeholder='{col_name}' name={col_name} step="any" class="textinput form-control" value="True" readonly></div></td>"""
                )
                STRING2 = (
                    STRING2
                    + f"""</select></td><td class="dt-center"><div class="" style="max-width:25em;"><input type="text" placeholder='{col_name}' step="any" class="textinput form-control" value="True" readonly></div></td><td class="dt-center"><div class="" style="max-width:25em;"><select data-dropdown_purpose="select_logical_operator"><option selected value="">-----</option><option value="AND">AND</option><option value="OR">OR</option></select></div></td>"""
                )

                STRING1 = (
                    STRING1
                    + f"""</select><br><div class=""><input type="text" placeholder="{col_name}" step="any" class="textinput form-control" value="True" readonly></div>"""
                )

            elif col_type in ["time", "TIME"]:
                STRING = (
                    STRING
                    + """</select></td><td class="dt-center"><div class="input-group date" style="max-width:25em;"><input type="time" step=1 placeholder="HH:MM:SS" class="form-control datepickerinput form-control" required="" </div></td>"""
                )

                STRING2 = (
                    STRING2
                    + """</select></td><td class="dt-center"><div class="input-group date" style="max-width:25em;"><input type="time" step=1 placeholder="HH:MM:SS" class="form-control datepickerinput form-control" required="" </div></td>"""
                )

                STRING1 = (
                    STRING1
                    + """ </select><br><div class="input-group date"><input type="time" placeholder="HH:MM:SS" step=1 class="form-control datepickerinput form-control" required="" ></div>"""
                )

            elif col_type in [
                "datetime",
                "datetime2",
                "timestamp without time zone",
                "TIMESTAMP",
                "TIMESTAMP(0)",
                "TIMESTAMP(6)",
            ]:
                STRING = (
                    STRING
                    + """</select></td><td class="dt-center"><div class="input-group date" style="max-width:25em;"><input type="datetime-local" placeholder="YYYY-MM-DD HH:MM" class="form-control datepickerinput form-control" required="" dp_config="{&quot;id&quot;: &quot;dp_4&quot;, &quot;picker_type&quot;: &quot;DATE&quot;, &quot;linked_to&quot;: null, &quot;options&quot;: {&quot;showClose&quot;: true, &quot;showClear&quot;: true, &quot;showTodayButton&quot;: true, &quot;format&quot;: &quot;DD-MM-YYYY&quot;}}"><div class="input-group-addon input-group-append" data-target="#datetimepicker1" data-toggle="datetimepickerv"><div class="input-group-text"><i class="fa fa-clock"></i></div></div></div></td>"""
                )
                STRING2 = (
                    STRING2
                    + """</select></td><td class="dt-center"><div class="input-group date" style="max-width:25em;"><input type="datetime-local" placeholder="YYYY-MM-DD HH:MM" class="form-control datepickerinput form-control" required="" dp_config="{&quot;id&quot;: &quot;dp_4&quot;, &quot;picker_type&quot;: &quot;DATE&quot;, &quot;linked_to&quot;: null, &quot;options&quot;: {&quot;showClose&quot;: true, &quot;showClear&quot;: true, &quot;showTodayButton&quot;: true, &quot;format&quot;: &quot;DD-MM-YYYY&quot;}}"><div class="input-group-addon input-group-append" data-target="#datetimepicker1" data-toggle="datetimepickerv"><div class="input-group-text"><i class="fa fa-clock"></i></div></div></div></td><td class="dt-center"><div class="" style="max-width:25em;"><select data-dropdown_purpose="select_logical_operator"><option selected value="">-----</option><option value="AND">AND</option><option value="OR">OR</option></select></div></td>"""
                )
            else:
                STRING = (
                    STRING
                    + """</select></td><td class="dt-center"><div class="input-group date" style="max-width:25em;"><input type="date" placeholder="YYYY-MM-DD" class="form-control datepickerinput form-control" required="" dp_config="{&quot;id&quot;: &quot;dp_4&quot;, &quot;picker_type&quot;: &quot;DATE&quot;, &quot;linked_to&quot;: null, &quot;options&quot;: {&quot;showClose&quot;: true, &quot;showClear&quot;: true, &quot;showTodayButton&quot;: true, &quot;format&quot;: &quot;DD-MM-YYYY&quot;}}"><div class="input-group-addon input-group-append" data-target="#datetimepicker1" data-toggle="datetimepickerv"><div class="input-group-text"><i class="fa fa-calendar"></i></div></div></div></td>"""
                )
                STRING += """<td class="dt-center"><div class="" style="max-width:25em;"><select data-dropdown_purpose="select_logical_operator"><option selected value="">-----</option><option value="AND">AND</option><option value="OR">OR</option></select></div></td></tr>"""
                STRING2 = (
                    STRING
                    + """</select></td><td class="dt-center"><div class="input-group date" style="max-width:25em;"><input type="date" placeholder="YYYY-MM-DD" class="form-control datepickerinput form-control" required="" dp_config="{&quot;id&quot;: &quot;dp_4&quot;, &quot;picker_type&quot;: &quot;DATE&quot;, &quot;linked_to&quot;: null, &quot;options&quot;: {&quot;showClose&quot;: true, &quot;showClear&quot;: true, &quot;showTodayButton&quot;: true, &quot;format&quot;: &quot;DD-MM-YYYY&quot;}}"><div class="input-group-addon input-group-append" data-target="#datetimepicker1" data-toggle="datetimepickerv"><div class="input-group-text"><i class="fa fa-calendar"></i></div></div></div></td><td class="dt-center"><div class="" style="max-width:25em;"><select data-dropdown_purpose="select_logical_operator"><option selected value="">-----</option><option value="AND">AND</option><option value="OR">OR</option></select></div></td>"""
                )

                STRING1 = (
                    STRING1
                    + """</select><br><div class="input-group date"><input type="date" placeholder="YYYY-MM-DD" class="form-control datepickerinput form-control" required="" dp_config="{&quot;id&quot;: &quot;dp_4&quot;, &quot;picker_type&quot;: &quot;DATE&quot;, &quot;linked_to&quot;: null, &quot;options&quot;: {&quot;showClose&quot;: true, &quot;showClear&quot;: true, &quot;showTodayButton&quot;: true, &quot;format&quot;: &quot;DD-MM-YYYY&quot;}}"><div class="input-group-addon input-group-append" data-target="#datetimepicker1" data-toggle="datetimepickerv"><div class="input-group-text"><i class="fa fa-calendar"></i></div></div></div>"""
                )
        else:
            STRING = (
                STRING
                + f"""<td class="dt-center"><div class="" style="max-width:10em;"><select class="form-control select2bs4 master_col_table" onchange="fetchColVals.call(this)" name={col_name} data-verbose_name="{column_verbose_dict[col_name]}">"""
            )
            STRING = STRING + f'<option value="" selected disabled>Select Table</option>'
            for tab_name in tableList:
                STRING = STRING + f'<option value="{tab_name}">{tab_name}</option>'

            STRING = (
                STRING
                + f"""</select><td class="dt-center"><div class="" style="max-width:10em;"><select class="form-control select2bs4 master_column_vals" name={col_name} data-verbose_name="{column_verbose_dict[col_name]}"></select>"""
            )

        form_fields[col_name] = STRING
        form_fields1[col_name] = STRING1
        form_fields2[col_name] = STRING2

    return tablename, label_columns, search_filters, form_fields, form_fields1, form_fields2
