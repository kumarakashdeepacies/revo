import io
import logging

import pandas as pd
from psycopg2 import sql

mssql_db_info_tables = [
    "information_schema.columns",
    "information_schema.tables",
    "auth_group",
    "auditlog_logentry",
    "django_apscheduler_djangojobexecution",
    "INFORMATION_SCHEMA.KEY_COLUMN_USAGE",
    "INFORMATION_SCHEMA.TABLE_CONSTRAINTS",
    "master.dbo.sysdatabases",
    "sys.default_constraints",
]

admin_tables = [
    "user",
    "User",
    "Profile",
    "auth_group",
    "user_groups",
    "configuration_parameter",
    "UserPermission_Master",
    "permissionaccess",
    "usergroup_approval",
    "user_approval",
    "allocated_licences",
    "user_model",
    "userpermission_interim",
    "group_details",
    "user_navbar",
    "failed_login_alerts",
    "dashboard_config",
    "login_trail",
    "audit_trail",
    "Instance",
    "notification_management",
    "applicationAccess",
]

sys_tables = [
    "Templates",
    "usergroup_approval",
    "CountryMaster",
    "CurrencyMaster",
    "Application",
    "Curve_Repository",
    "computation_model_configuration",
    "Profile",
    "Category_Subelement",
    "Hierarchy_table",
    "Curve_Data",
    "computation_model_flowchart",
    "jobs_scheduled",
    "group_config",
    "Draft_FormData",
    "Error_Master_Table",
    "Business_Models",
    "computation_model_run_history",
    "Users_urlMap",
    "Tasks_Planner",
    "Ocr_Template",
    "NavigationSideBar",
    "Holiday_Calendar_Repository",
    "Process_subprocess_flowchart",
    "UserPermission_Master",
    "Plan_Buckets",
    "permissionaccess",
    "TabScreens",
    "ApprovalTable",
    "Model_Repository",
    "Upload_Error_History",
    "summary_table",
    "DraftProcess",
    "user_approval",
    "configuration_parameter",
    "Tables",
    "allocated_licences",
    "Category_Subelement_Attributes",
    "UserConfig",
    "Plans",
    "computation_output_repository",
    "Hierarchy_levels",
    "data_mapping_error_report",
    "Hierarchy_groups",
    "userpermission_interim",
    "group_details",
    "ml_model_repository",
    "UserProfile",
    "ConfigTable",
    "Process_flow_model",
    "computation_function_repository",
    "computation_scenario_repository",
    "data_management_computed_fields_config",
    "data_management_computed_fields_flow",
    "application_theme",
    "template_theme",
    "flow_monitor_error_log",
    "alerts",
    "static_page_config",
    "audit_operation",
    "external_application_master",
    "system_management_table",
    "smtp_configuration",
    "event_master",
    "system_application_master",
]


class OracleSQLQueryGenerator:
    def __init__(
        self,
        request,
        config_dict,
        table,
        access_controller=True,
        fetch_all_entries=False,
        model_class=None,
        operation="read",
        if_app_db_call=True,
        schema="",
        data_type={},
        join_table_names=[],
        join_tables_model_classes={},
    ):
        self.db_info_tables = [
            "all_tables",
            "all_constraints",
            "all_tab_columns",
            "all_cons_columns",
            "user_constraints",
            "user_tables",
            "user_cons_columns",
        ]
        self.request = request
        self.config_dict = config_dict
        self.table = table
        self.schema = schema
        self.model_class = model_class
        self.operation = operation
        self.if_app_db_call = if_app_db_call
        self.sql_table_name = self.sql_table_name_identifier()
        self.data_type = data_type
        if self.operation == "read":
            self.access_controller = access_controller
            self.fetch_all_entries = fetch_all_entries
            self.columns_list = config_dict["inputs"]["Columns"]
            if bool(config_dict.get("condition")):
                for item in config_dict["condition"]:
                    if item["condition"] != "IN" and item["condition"] != "NOT IN":
                        if item.get("input_value"):
                            if type(item["input_value"]) is str:
                                self.input_validation_check(item["input_value"])
                            else:
                                pass
                        else:
                            continue
                    else:
                        pass

            if config_dict.get("aliases"):
                aliases = config_dict.get("aliases")
                alias_columnslist = []
                for field in self.columns_list:
                    if aliases.get(field, "") != "":
                        alias_columnslist.append(f'{field} AS "{aliases.get(field)}"')
                    else:
                        alias_columnslist.append(field)
                self.columns_string = ",".join(alias_columnslist)
            else:
                self.columns_string = ",".join(self.columns_list)
            if self.config_dict.get("apply_join"):
                self.join_table_names = join_table_names.copy()
                self.join_tables_model_classes = join_tables_model_classes.copy()
                self.sql_join_table_names = self.sql_join_table_name_identifier()
                self.join_columns, self.join_query = self.join_query_generator()

                if self.config_dict["join_table_data"].get("join_conditions"):
                    if not self.config_dict.get("condition"):
                        self.config_dict["condition"] = []
                    else:
                        if self.config_dict["condition"][-1]["and_or"] == ")":
                            self.config_dict["condition"][-1]["and_or"] = ") AND "
                        else:
                            self.config_dict["condition"][-1]["and_or"] = "AND"
                    for join_table in self.config_dict["join_table_data"]["join_conditions"]:
                        for condition in self.config_dict["join_table_data"]["join_conditions"][join_table]:
                            if "users_" + condition["table_name"] in self.sql_join_table_names:
                                condition["table_name"] = "users_" + condition["table_name"]
                            self.config_dict["condition"].append(condition)
                else:
                    pass
            if self.config_dict.get("group_by_configs"):
                self.join_table_group_by_select_columns = ""
                self.join_table_group_by_query = ""
                self.group_by_aggregations = {}
                self.group_by_columns = self.config_dict["group_by_configs"].get("group_by_columns", [])
                if self.group_by_columns:
                    if self.config_dict.get("apply_join"):
                        (
                            self.join_table_group_by_select_columns,
                            self.join_table_group_by_query,
                            self.group_by_aggregations,
                        ) = self.group_by_query_generator()
                        config_dict["inputs"]["group_by_aggregation"] = self.group_by_aggregations
                        config_dict["inputs"]["group_by"] = self.join_table_group_by_query.split(", ")
                        self.columns_string = self.join_table_group_by_select_columns
                        self.join_columns = self.join_table_group_by_select_columns
                    else:
                        if config_dict["group_by_configs"].get("aggregations"):
                            config_dict["inputs"]["group_by_aggregation"] = config_dict["group_by_configs"][
                                "aggregations"
                            ].get(table, {})
                        config_dict["inputs"]["group_by"] = self.group_by_columns.get(table).copy()
                        self.columns_string = ", ".join(self.group_by_columns.get(table).copy())
                else:
                    pass
            else:
                pass

            if self.config_dict.get("order_by_configs"):
                self.order_by_query_string = self.order_by_query_generator()

            self.agg_query, self.order_query, self.top_query = self.aggregation_function_handler()
            self.group_by_query = self.groupby_query_generator()
        elif self.operation == "update":
            self.update_columns = config_dict["inputs"]["Columns"]
            update_data_dict = config_dict["inputs"]["Columns"]
            for i in range(0, len(update_data_dict)):
                if update_data_dict[i].get("input_value"):
                    if (
                        update_data_dict[i]["input_value"] != "NULL"
                        and type(update_data_dict[i]["input_value"]) is str
                    ):
                        self.input_validation_check(update_data_dict[i]["input_value"])
                    else:
                        continue
                else:
                    continue
        else:
            pass

    def order_by_query_generator(self):
        order_by_configs = self.config_dict.get("order_by_configs")
        order_by_query = "ORDER BY "

        for column in order_by_configs:
            if "." in column:
                group_by_table, group_by_column = column.split(".").copy()
                group_by_table = self.sql_table_name_identifier(group_by_table)
                order_by_query += f"{group_by_table}.{group_by_column} {order_by_configs[column]}, "
            else:
                order_by_query += f'"{column}" {order_by_configs[column]}, '
        order_by_query = order_by_query[:-2]

        return order_by_query

    def sql_join_table_name_identifier(self):
        sql_join_table_names = []
        for table in self.join_table_names:
            if self.schema:
                schema_str = f"{self.schema}."
            else:
                schema_str = ""
            if self.if_app_db_call and table.lower() not in self.db_info_tables:
                sql_table_name = f"users_{table.lower()}"
            elif table.lower() in self.db_info_tables:
                sql_table_name = table
            else:
                sql_table_name = f"{schema_str}{table}"
            sql_join_table_names.append(sql_table_name)
        return sql_join_table_names

    def input_validation_check(self, input_value_check):
        input_value_check.replace(" ", "")
        exclusion_list = ["'+", "'and", "'or", "'%", "'--", "';", "Waitfor", "delay", "lag", "getdate()"]
        count_single_quote = input_value_check.count("'")
        if count_single_quote > 1:
            if any(item.lower() in input_value_check.lower() for item in exclusion_list):
                raise Exception("Attempt for SQL Injection! Request cannot be completed")
            else:
                pass
        return None

    def sql_table_name_identifier(self, table_name=""):
        if not table_name:
            if self.schema:
                schema_str = f"{self.schema}."
            else:
                schema_str = ""
            if self.if_app_db_call and self.table.lower() not in self.db_info_tables:
                sql_table_name = f"users_{self.table.lower()}"
            elif self.table.lower() in self.db_info_tables:
                sql_table_name = self.table
            else:
                sql_table_name = f"{schema_str}{self.table}"
        else:
            if self.schema:
                schema_str = f"{self.schema}."
            else:
                schema_str = ""
            if self.if_app_db_call and table_name.lower() not in self.db_info_tables:
                sql_table_name = f"users_{table_name.lower()}"
            elif table_name.lower() in self.db_info_tables:
                sql_table_name = table_name
            else:
                sql_table_name = f"{schema_str}{table_name}"

        return sql_table_name

    # Where clause query generator
    def where_clause_generator(
        self, cond_date_list, cond_datetime_list, numeric_type_columns, blob_type_columns
    ):
        """
        Generates the where clause query for OracleDB calls
        cond_date_list: List of date type columns
        cond_datetime_list: List of timestamp type columns
        """
        condition_query = ""
        condition_mapper = {
            "Greater than": "{field} > {value} {and_or} ",
            "Smaller than": "{field} < {value} {and_or} ",
            "Greater than equal to": "{field} >= {value} {and_or} ",
            "Smaller than equal to": "{field} <= {value} {and_or} ",
            "Equal to": "{field} = '{value}' {and_or} ",
            "Not Equal to": "{field} != '{value}' {and_or} ",
            "Greater than -date": "trunc({field}) > date '{value}' {and_or} ",
            "Smaller than -date": "trunc({field}) < date '{value}' {and_or} ",
            "Greater than equal to -date": "trunc({field}) >= date '{value}' {and_or} ",
            "Smaller than equal to -date": "trunc({field}) <= date '{value}' {and_or} ",
            "Equal to -date": "trunc({field}) = date '{value}' {and_or} ",
            "Not Equal to -date": "trunc({field}) != date '{value}' {and_or} ",
            "Greater than -datetime": "{field} > TO_DATE('{value}', 'YYYY-MM-DD HH24:MI:SS') {and_or} ",
            "Smaller than -datetime": "{field} < TO_DATE('{value}', 'YYYY-MM-DD HH24:MI:SS') {and_or} ",
            "Greater than equal to -datetime": "{field} >= TO_DATE('{value}', 'YYYY-MM-DD HH24:MI:SS') {and_or} ",
            "Smaller than equal to -datetime": "{field} <= TO_DATE('{value}', 'YYYY-MM-DD HH24:MI:SS') {and_or} ",
            "Equal to -datetime": "{field} = TO_DATE('{value}', 'YYYY-MM-DD HH24:MI:SS') {and_or} ",
            "Not Equal to -datetime": "{field} != TO_DATE('{value}', 'YYYY-MM-DD HH24:MI:SS') {and_or} ",
            "Equal to -numeric": "{field} = {value} {and_or} ",
            "Not Equal to -numeric": "{field} != {value} {and_or} ",
            "Between": "{field} BETWEEN {input_value_lower} AND {input_value_upper} {and_or} ",
            "IN": "{field} IN {value} {and_or} ",
            "NOT IN": "{field} NOT IN {value} {and_or} ",
            "Starts with": "{field} LIKE '{value}%' {and_or} ",
            "Not Starts with": "{field} NOT LIKE '{value}%' {and_or} ",
            "Ends with": "{field} LIKE '%{value}' {and_or} ",
            "Not Ends with": "{field} NOT LIKE '%{value}' {and_or} ",
            "Contains": "{field} LIKE '%{value}%' {and_or} ",
            "Not Contains": "{field} NOT LIKE '%{value}%' {and_or} ",
            "Equal to -blob": "dbms_lob.instr({field}, UTL_RAW.CAST_TO_RAW('{value}'), 1, 1) = 1 {and_or} ",
            "Not Equal to -blob": "dbms_lob.instr({field}, UTL_RAW.CAST_TO_RAW('{value}'), 1, 1) < 1 {and_or} ",
            "Starts with -blob": "dbms_lob.instr({field}, UTL_RAW.CAST_TO_RAW('{value}'), 1, 1) = 1 {and_or} ",
            "Not Starts with -blob": "dbms_lob.instr({field}, UTL_RAW.CAST_TO_RAW('{value}'), 1, 1) <> 1 {and_or} ",
            "Ends with -blob": "dbms_lob.instr({field}, UTL_RAW.CAST_TO_RAW('{value}'), 1, 1) > 0 {and_or} ",
            "Not Ends with -blob": "dbms_lob.instr({field}, UTL_RAW.CAST_TO_RAW('{value}'), 1, 1) > 0 {and_or} ",
            "Contains -blob": "dbms_lob.instr({field}, UTL_RAW.CAST_TO_RAW('{value}'), 1, 1) > 0 {and_or} ",
            "Not Contains -blob": "dbms_lob.instr({field}, UTL_RAW.CAST_TO_RAW('{value}'), 1, 1) = 0 {and_or} ",
        }

        if self.config_dict.get("condition"):
            new_condition_format = False
            if self.config_dict["condition"][0].get("constraintName") and self.config_dict["condition"][
                0
            ].get("ruleSet"):
                new_condition_format = True
            else:
                pass
            updated_condition_dict = {}
            if new_condition_format:
                for cond in self.config_dict["condition"]:
                    if not updated_condition_dict.get(cond["constraintName"]):
                        updated_condition_dict[cond["constraintName"]] = {}
                    else:
                        pass
                    existing_const = updated_condition_dict[cond["constraintName"]]
                    if existing_const.get(cond["ruleSet"]):
                        updated_condition_dict[cond["constraintName"]][cond["ruleSet"]].append(cond)
                    else:
                        updated_condition_dict[cond["constraintName"]][cond["ruleSet"]] = [cond]
                advance_condition_dict = {}
                if self.config_dict.get("adv_condition"):
                    advance_condition = self.config_dict["adv_condition"]
                    for cond in advance_condition:
                        constraint_name = cond["constraintName"]
                        rule_set = cond["ruleSet"]
                        adv_column_name = cond["column_name"]
                        adv_agg_condition = cond["agg_condition"]
                        if updated_condition_dict.get(constraint_name):
                            base_conditions = updated_condition_dict[constraint_name]
                            base_cons_condition = self.constraint_query_generator(
                                base_conditions,
                                condition_mapper,
                                cond_datetime_list,
                                cond_date_list,
                                numeric_type_columns,
                                blob_type_columns,
                            )
                            advance_condition_cons = " {field} = (SELECT {adv_agg_condition}({field}) FROM {sql_table_name} WHERE {base_cons_condition})".format(
                                field=adv_column_name,
                                adv_agg_condition=adv_agg_condition,
                                sql_table_name=self.sql_table_name,
                                base_cons_condition=base_cons_condition,
                            )
                        else:
                            advance_condition_cons = " {field} = (SELECT {adv_agg_condition}({field}) FROM {sql_table_name})".format(
                                field=adv_column_name,
                                adv_agg_condition=adv_agg_condition,
                                sql_table_name=self.sql_table_name,
                            )
                        if advance_condition_dict.get(constraint_name):
                            if advance_condition_dict[constraint_name].get(rule_set):
                                advance_condition_dict[constraint_name][rule_set] += " AND "
                                advance_condition_dict[constraint_name][rule_set] += advance_condition_cons
                            else:
                                advance_condition_dict[constraint_name][rule_set] = advance_condition_cons
                        else:
                            advance_condition_dict[constraint_name] = {rule_set: advance_condition_cons}
                else:
                    pass
                for const, const_conf in updated_condition_dict.items():
                    if advance_condition_dict.get(const):
                        cons_advance_dict = advance_condition_dict[const]
                    else:
                        cons_advance_dict = {}
                    constraint_condition_string = self.constraint_query_generator(
                        const_conf,
                        condition_mapper,
                        cond_datetime_list,
                        cond_date_list,
                        numeric_type_columns,
                        blob_type_columns,
                        advance_condition_dict=cons_advance_dict,
                    )
                    condition_query += constraint_condition_string
                    if (
                        list(updated_condition_dict.keys()).index(const)
                        != len(updated_condition_dict.keys()) - 1
                    ):
                        condition_query += " AND "
                    else:
                        pass
                for const, const_conf in advance_condition_dict.items():
                    if const not in updated_condition_dict:
                        condition_query += " AND "
                        condition_query += "("
                        for rule in const_conf.values():
                            condition_query += rule
                        condition_query += ")"
                    else:
                        continue
            else:
                for cond in self.config_dict["condition"]:
                    column_name = cond["column_name"]
                    and_or = cond["and_or"]
                    condition = cond["condition"]
                    if condition not in ["IN", "NOT IN", "Between"]:
                        input_value = cond["input_value"]
                        if input_value != "NULL":
                            if column_name in cond_datetime_list:
                                input_value = pd.to_datetime(input_value).strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                )
                            elif column_name in cond_date_list:
                                input_value = pd.to_datetime(input_value).strftime("%Y-%m-%d")
                            else:
                                pass
                            if column_name in numeric_type_columns and condition in [
                                "Equal to",
                                "Not Equal to",
                            ]:
                                condition += " -numeric"
                            else:
                                pass
                            if column_name in cond_date_list:
                                condition += " -date"
                            elif column_name in cond_datetime_list:
                                condition += " -datetime"
                            else:
                                pass
                            if column_name in blob_type_columns:
                                condition += " -blob"
                            else:
                                pass
                            cond_query = condition_mapper[condition].format(
                                field=column_name,
                                value=input_value,
                                and_or=and_or,
                            )
                        else:
                            if condition == "Equal to":
                                cond_query = "{field} is NULL {and_or} ".format(
                                    field=column_name, and_or=and_or
                                )
                            else:
                                cond_query = "{field} is NOT NULL {and_or} ".format(
                                    field=column_name, and_or=and_or
                                )
                    elif condition == "Between":
                        cond_query = condition_mapper[condition].format(
                            field=column_name,
                            input_value_lower=cond["input_value_lower"],
                            input_value_upper=cond["input_value_upper"],
                            and_or=and_or,
                        )
                    else:
                        input_value = cond["input_value"]
                        if type(input_value) in [list, tuple]:
                            input_value = str(tuple(input_value)).replace(",)", ")")
                        else:
                            pass
                        cond_query = condition_mapper[condition].format(
                            field=column_name,
                            value=input_value,
                            and_or=and_or,
                        )
                    condition_query += cond_query
        elif self.config_dict.get("adv_condition"):
            advance_condition = self.config_dict["adv_condition"]
            advance_condition_dict = {}
            for cond in advance_condition:
                constraint_name = cond["constraintName"]
                rule_set = cond["ruleSet"]
                adv_column_name = cond["column_name"]
                adv_agg_condition = cond["agg_condition"]
                advance_condition_cons = (
                    "{field} = (SELECT {adv_agg_condition}({field}) FROM {sql_table_name}) ".format(
                        field=adv_column_name,
                        adv_agg_condition=adv_agg_condition,
                        sql_table_name=self.sql_table_name,
                    )
                )
                if advance_condition_dict.get(constraint_name):
                    if advance_condition_dict[constraint_name].get(rule_set):
                        advance_condition_dict[constraint_name][rule_set].append(" AND ")
                        advance_condition_dict[constraint_name][rule_set].append(advance_condition_cons)
                    else:
                        advance_condition_dict[constraint_name][rule_set] = [advance_condition_cons]
                else:
                    advance_condition_dict[constraint_name] = {rule_set: [advance_condition_cons]}
            for const, rule in advance_condition_dict.items():
                condition_query += "("
                for rule_set, cond_list in rule.items():
                    rule_cond = " ".join([i for i in cond_list])
                    condition_query += rule_cond
                    if list(rule.keys()).index(rule_set) != len(rule) - 1:
                        condition_query += " OR "
                    else:
                        pass
                condition_query += ")"
                if list(advance_condition_dict.keys()).index(const) != len(advance_condition_dict) - 1:
                    condition_query += " AND "
                else:
                    pass
        else:
            pass
        return condition_query

    def constraint_query_generator(
        self,
        const_conf,
        condition_mapper,
        cond_datetime_list,
        cond_date_list,
        numeric_type_columns,
        blob_type_columns,
        advance_condition_dict={},
    ):
        constraint_condition_string = "("
        for rule_set, rule_conf in const_conf.items():
            rule_set_condition_string = "("
            for cond_index, cond in enumerate(rule_conf):

                prepend_table_name = False
                table_name = cond.get("table_name") or self.sql_table_name
                if cond.get("table_name"):
                    prepend_table_name = True
                elif self.sql_table_name:
                    flag = True
                    for sql_table in sys_tables + admin_tables + self.db_info_tables:
                        if sql_table == self.sql_table_name:
                            flag = False
                            prepend_table_name = False
                            break
                    if flag:
                        prepend_table_name = True

                if prepend_table_name:
                    field_name = ("{table}.{field}").format(table=table_name, field=cond["column_name"])
                else:
                    field_name = cond["column_name"]

                if cond_index == len(rule_conf) - 1:
                    and_or = ""
                else:
                    and_or = "AND"
                condition = cond["condition"]
                column_name = cond["column_name"]
                if condition not in ["IN", "NOT IN", "Between"]:
                    input_value = cond["input_value"]
                    if input_value != "NULL":
                        if column_name in cond_datetime_list:
                            input_value = pd.to_datetime(input_value).strftime(
                                "%Y-%m-%d %H:%M:%S"
                            )
                        elif column_name in cond_date_list:
                            input_value = pd.to_datetime(input_value).strftime("%Y-%m-%d")
                        else:
                            pass
                        if column_name in numeric_type_columns and condition in ["Equal to", "Not Equal to"]:
                            condition += " -numeric"
                        else:
                            pass
                        if column_name in cond_date_list:
                            condition += " -date"
                        elif column_name in cond_datetime_list:
                            condition += " -datetime"
                        else:
                            pass
                        if column_name in blob_type_columns:
                            condition += " -blob"
                        else:
                            pass
                        cond_query = condition_mapper[condition].format(
                            field=field_name,
                            value=input_value,
                            and_or=and_or,
                        )
                    else:
                        if condition == "Equal to":
                            cond_query = f"{field_name} is NULL {and_or} "
                        else:
                            cond_query = "{field} is NOT NULL {and_or} ".format(
                                field=field_name, and_or=and_or
                            )
                elif condition == "Between":
                    cond_query = condition_mapper[condition].format(
                        field=field_name,
                        input_value_lower=cond["input_value_lower"],
                        input_value_upper=cond["input_value_upper"],
                        and_or=and_or,
                    )
                else:
                    input_value = cond["input_value"]
                    if type(input_value) in [list, tuple]:
                        if column_name in cond_date_list:
                            input_value = ", ".join(
                                [f"TO_DATE('{val}', 'YYYY-MM-DD')" for val in input_value if len(val) == 10]
                            )
                        else:
                            input_value = str(tuple(input_value)).replace(",)", ")")
                    else:
                        pass
                    cond_query = condition_mapper[condition].format(
                        field=field_name,
                        value=input_value,
                        and_or=and_or,
                    )
                rule_set_condition_string += cond_query
            if advance_condition_dict.get(rule_set):
                rule_set_condition_string += " AND "
                rule_set_condition_string += advance_condition_dict[rule_set]
            else:
                pass
            rule_set_condition_string += ")"
            constraint_condition_string += rule_set_condition_string
            if list(const_conf.keys()).index(rule_set) != len(const_conf.keys()) - 1:
                constraint_condition_string += " OR "
            else:
                pass
        if advance_condition_dict:
            for rule, cond_string in advance_condition_dict.items():
                if rule not in const_conf:
                    constraint_condition_string += " OR "
                    constraint_condition_string += cond_string
                else:
                    continue
        else:
            pass
        constraint_condition_string += ")"
        return constraint_condition_string

    # Group by clause query generator
    def groupby_query_generator(self):
        if self.config_dict["inputs"].get("group_by_aggregation"):
            for agg_col, aggregation in self.config_dict["inputs"].get("group_by_aggregation").items():
                if type(aggregation) is list:
                    for item in aggregation:
                        aggregation_type = item.get("agg_type")
                        aggregation_alias = item.get("agg_alias")
                        if not aggregation_alias:
                            aggregation_alias = agg_col
                        if aggregation_type == "sum":
                            self.columns_string += f', SUM({agg_col}) AS "{aggregation_alias}"'
                        elif aggregation_type == "average":
                            self.columns_string += f', AVG({agg_col}) AS "{aggregation_alias}"'
                        elif aggregation_type == "variance":
                            self.columns_string += f', VARIANCE({agg_col}) AS "{aggregation_alias}"'
                        elif aggregation_type == "standard deviation":
                            self.columns_string += f', STDDEV({agg_col}) AS "{aggregation_alias}"'
                        elif aggregation_type == "count":
                            self.columns_string += f', COUNT({agg_col}) AS "{aggregation_alias}"'
                        elif aggregation_type == "count distinct":
                            self.columns_string += f', COUNT(DISTINCT {agg_col}) AS "{aggregation_alias}"'
                        elif aggregation_type == "maximum":
                            self.columns_string += f', MAX({agg_col}) AS "{aggregation_alias}"'
                        elif aggregation_type == "minimum":
                            self.columns_string += f', MIN({agg_col}) AS "{aggregation_alias}"'
                        elif aggregation_type == "percentage of total":
                            self.columns_string += (
                                f', SUM({agg_col}) / SUM(SUM({agg_col})) OVER() AS "{aggregation_alias}"'
                            )
                        else:
                            continue
                else:
                    if aggregation == "sum":
                        self.columns_string += f", SUM({agg_col}) AS {agg_col}"
                    elif aggregation == "average":
                        self.columns_string += f", AVG({agg_col}) AS {agg_col}"
                    elif aggregation == "variance":
                        self.columns_string += f", VARIANCE({agg_col}) AS {agg_col}"
                    elif aggregation == "standard deviation":
                        self.columns_string += f", STDDEV({agg_col}) AS {agg_col}"
                    elif aggregation == "count":
                        self.columns_string += f", COUNT({agg_col}) AS {agg_col}"
                    elif aggregation == "count distinct":
                        self.columns_string += f", COUNT(DISTINCT {agg_col}) AS {agg_col}"
                    elif aggregation == "maximum":
                        self.columns_string += f", MAX({agg_col}) AS {agg_col}"
                    elif aggregation == "minimum":
                        self.columns_string += f", MIN({agg_col}) AS {agg_col}"
                    elif aggregation == "percentage of total":
                        self.columns_string += f", SUM({agg_col}) / SUM(SUM({agg_col})) OVER() AS {agg_col}"
                    else:
                        continue
            self.columns_string = self.columns_string.lstrip(", ")
            if self.config_dict.get("apply_join"):
                self.join_columns = self.columns_string
        else:
            pass
        group_by_string = ""
        if self.config_dict["inputs"].get("group_by"):
            group_by_cols = ",".join(self.config_dict["inputs"]["group_by"])
            group_by_string = f"GROUP BY {group_by_cols}"
        else:
            pass
        return group_by_string

    # Aggregation function
    def aggregation_function_handler(self):
        config = self.config_dict["inputs"]
        agg_query = ""
        order_query = ""
        top_query = ""
        if "Agg_Type" in config:
            if config["Agg_Type"] != "":
                if config["Agg_Type"].startswith("TOP("):
                    n = config["Agg_Type"].replace("TOP(", "").replace(")", "")
                    top_query = f"FETCH FIRST {n} rows only"
                else:
                    agg_query = config["Agg_Type"]
            else:
                pass
        else:
            pass
        if "Order_Type" in config:
            if config["Order_Type"] != "":
                order_query = f"{config['Order_Type']}"
                if "Offset" in config:
                    order_query += f" OFFSET {config['Offset']} ROWS"
                    if "Fetch_next" in config:
                        order_query += f" FETCH NEXT {config['Fetch_next']} ROWS ONLY"
                    else:
                        pass
                else:
                    pass
            else:
                pass
        else:
            pass
        return agg_query, order_query, top_query

    def read_query_generator(self):
        date_type_columns = []
        datetime_type_columns = []
        numeric_type_columns = []
        blob_type_columns = []
        if self.table not in self.db_info_tables + admin_tables and self.if_app_db_call:
            field_list = {
                field.name: field.verbose_name.title() for field in self.model_class.concrete_fields
            }
            is_new_config_call = False
            if self.config_dict.get("condition"):
                if self.config_dict["condition"][0].get("constraintName"):
                    is_new_config_call = True
                else:
                    pass
            else:
                pass
            if self.access_controller:
                access_controls = self.model_class.get_access_controls()
                if access_controls and self.request:
                    if access_controls["access_type"] == "created_by_user":
                        if self.config_dict.get("condition"):
                            if self.config_dict["condition"][-1]["and_or"] == ")":
                                self.config_dict["condition"][-1]["and_or"] = ") AND "
                            else:
                                self.config_dict["condition"][-1]["and_or"] = "AND"
                        else:
                            pass
                        access_control_condition = {
                            "column_name": "created_by",
                            "condition": "Equal to",
                            "input_value": self.request.user.username,
                            "and_or": "OR",
                        }
                        access_control_condition1 = {
                            "column_name": "modified_by",
                            "condition": "Equal to",
                            "input_value": self.request.user.username,
                            "and_or": ")",
                        }
                        if is_new_config_call:
                            access_control_condition["constraintName"] = "access_control_constraint"
                            access_control_condition["ruleSet"] = "access_control_rule1"
                            access_control_condition1["constraintName"] = "access_control_constraint"
                            access_control_condition1["ruleSet"] = "access_control_rule2"
                            access_control_condition1["and_or"] = ""
                        else:
                            access_control_condition["column_name"] = (
                                f"({access_control_condition['column_name']}"
                            )
                            access_control_condition["and_or"] = "OR"
                        self.config_dict["condition"].append(access_control_condition)
                        self.config_dict["condition"].append(access_control_condition1)
                    elif access_controls["access_type"] == "custom":
                        if self.config_dict.get("condition"):
                            if self.config_dict["condition"][-1]["and_or"] == ")":
                                self.config_dict["condition"][-1]["and_or"] = ") AND "
                            else:
                                self.config_dict["condition"][-1]["and_or"] = "AND"
                        else:
                            pass
                        additional_config = access_controls["additional_config"]
                        control_measure = additional_config["controlMeasure"]
                        access_control_condition_list = []
                        for cust_acc_col in additional_config["fields"]:
                            if cust_acc_col in ["created_by", "modified_by"]:
                                access_control_condition_list.append(
                                    {
                                        "column_name": cust_acc_col,
                                        "condition": "Equal to",
                                        "input_value": self.request.user.username,
                                        "and_or": "",
                                    }
                                )
                            else:
                                if (
                                    self.model_class.get_field(cust_acc_col).get_internal_type()
                                    == "MultiselectField"
                                ):
                                    if control_measure in ["any_email", "all_email"]:
                                        input_value = self.request.user.email
                                    else:
                                        input_value = self.request.user.username

                                    #     pass
                                    access_control_condition_list.append(
                                        {
                                            "column_name": cust_acc_col,
                                            "condition": "Contains",
                                            "input_value": input_value,
                                            "and_or": "",
                                        }
                                    )
                                else:
                                    if control_measure in ["any_email", "all_email"]:
                                        input_value = self.request.user.email
                                    else:
                                        input_value = self.request.user.username
                                    access_control_condition_list.append(
                                        {
                                            "column_name": cust_acc_col,
                                            "condition": "Equal to",
                                            "input_value": input_value,
                                            "and_or": "",
                                        }
                                    )
                        if is_new_config_call:
                            for i in range(len(access_control_condition_list)):
                                access_control_condition_list[i][
                                    "constraintName"
                                ] = "access_control_constraint"
                                if control_measure in ["any", "any_email"]:
                                    access_control_condition_list[i]["ruleSet"] = f"access_control_rule{i}"
                                else:
                                    access_control_condition_list[i]["ruleSet"] = "access_control_rule"
                        else:
                            access_control_condition_list[0][
                                "column_name"
                            ] = f'({access_control_condition_list[0]["column_name"]}'
                            access_control_condition_list[-1]["and_or"] = ")"
                            for i in range(len(access_control_condition_list)):
                                if i != len(access_control_condition_list) - 1:
                                    if control_measure in ["any", "any_email"]:
                                        access_control_condition_list[i]["and_or"] = "OR"
                                    else:
                                        access_control_condition_list[i]["and_or"] = "AND"
                                else:
                                    continue
                        if access_control_condition_list:
                            self.config_dict["condition"] += access_control_condition_list
                        else:
                            pass
                    else:
                        pass
                else:
                    pass
            else:
                pass
            if not self.fetch_all_entries and "is_active_flag" in field_list:
                if self.config_dict.get("condition"):
                    if "is_active_flag" in self.config_dict["condition"][-1]["column_name"]:
                        self.config_dict["condition"][-1]["and_or"] = ") AND "
                    elif self.config_dict["condition"][-1]["and_or"] == ")":
                        self.config_dict["condition"][-1]["and_or"] = ") AND "
                    else:
                        self.config_dict["condition"][-1]["and_or"] = "AND"
                    is_active_condition1 = {
                        "condition": "Equal to",
                        "input_value": "NULL",
                        "and_or": "",
                    }
                    if is_new_config_call:
                        is_active_condition1["column_name"] = "is_active_flag"
                    else:
                        is_active_condition1["column_name"] = "(is_active_flag"
                    is_active_condition = {
                        "column_name": "is_active_flag",
                        "condition": "Not Equal to",
                        "input_value": "No",
                        "and_or": ")",
                    }
                    if is_new_config_call:
                        is_active_condition1["constraintName"] = "is_active_contraint"
                        is_active_condition1["ruleSet"] = "is_active_rule_set1"
                        is_active_condition["constraintName"] = "is_active_contraint"
                        is_active_condition["ruleSet"] = "is_active_rule_set2"
                        is_active_condition["and_or"] = ""
                    else:
                        is_active_condition1["and_or"] = "OR"

                    self.config_dict["condition"].append(is_active_condition1)
                    self.config_dict["condition"].append(is_active_condition)
                    if self.config_dict.get("apply_join"):
                        if is_new_config_call:
                            for i, table in enumerate(self.join_table_names):
                                if i == 0:
                                    continue
                                if table not in self.db_info_tables + admin_tables and self.if_app_db_call:
                                    field_list = {
                                        field.name: field.verbose_name.title()
                                        for field in self.join_tables_model_classes[table].concrete_fields
                                    }
                                    if not self.fetch_all_entries and "is_active_flag" in field_list:
                                        self.config_dict["condition"].append(
                                            {
                                                "table_name": self.sql_join_table_names[i],
                                                "column_name": "is_active_flag",
                                                "condition": "Equal to",
                                                "input_value": "NULL",
                                                "and_or": "",
                                                "constraintName": "is_active_contraint" + str(i),
                                                "ruleSet": "is_active_rule_set" + str(i + 1),
                                            }
                                        )
                                        self.config_dict["condition"].append(
                                            {
                                                "table_name": self.sql_join_table_names[i],
                                                "column_name": "is_active_flag",
                                                "condition": "Not Equal to",
                                                "input_value": "No",
                                                "and_or": "",
                                                "constraintName": "is_active_contraint" + str(i),
                                                "ruleSet": "is_active_rule_set" + str(i),
                                            }
                                        )
                                    else:
                                        pass
                                else:
                                    pass
                        else:
                            for i, table in enumerate(self.join_table_names):
                                if i == 0:
                                    continue
                                if table not in self.db_info_tables + admin_tables and self.if_app_db_call:
                                    field_list = {
                                        field.name: field.verbose_name.title()
                                        for field in self.join_tables_model_classes[table].concrete_fields
                                    }
                                    if not self.fetch_all_entries and "is_active_flag" in field_list:
                                        if (
                                            "is_active_flag"
                                            in self.config_dict["condition"][-1]["column_name"]
                                        ):
                                            self.config_dict["condition"][-1]["and_or"] = ") AND "
                                        elif self.config_dict["condition"][-1]["and_or"] == ")":
                                            self.config_dict["condition"][-1]["and_or"] = ") AND "
                                        else:
                                            self.config_dict["condition"][-1]["and_or"] = "AND"
                                        self.config_dict["condition"].append(
                                            {
                                                "table_name": self.sql_join_table_names[i],
                                                "column_name": "(is_active_flag",
                                                "condition": "Equal to",
                                                "input_value": "NULL",
                                                "and_or": "OR",
                                            }
                                        )
                                        self.config_dict["condition"].append(
                                            {
                                                "table_name": self.sql_join_table_names[i],
                                                "column_name": "is_active_flag",
                                                "condition": "Not Equal to",
                                                "input_value": "No",
                                                "and_or": ")",
                                            }
                                        )
                                    else:
                                        pass
                                else:
                                    pass
                    else:
                        pass
                else:
                    self.config_dict["condition"] = []
                    self.config_dict["condition"].append(
                        {
                            "column_name": "is_active_flag",
                            "condition": "Equal to",
                            "input_value": "NULL",
                            "and_or": "OR",
                            "constraintName": "is_active_contraint",
                            "ruleSet": "is_active_rule_set1",
                        }
                    )
                    self.config_dict["condition"].append(
                        {
                            "column_name": "is_active_flag",
                            "condition": "Not Equal to",
                            "input_value": "No",
                            "and_or": "",
                            "constraintName": "is_active_contraint",
                            "ruleSet": "is_active_rule_set",
                        }
                    )
                    if self.config_dict.get("apply_join"):
                        for i, table in enumerate(self.join_table_names):
                            if i == 0:
                                continue
                            if table not in self.db_info_tables + admin_tables and self.if_app_db_call:
                                field_list = {
                                    field.name: field.verbose_name.title()
                                    for field in self.join_tables_model_classes[table].concrete_fields
                                }
                                if not self.fetch_all_entries and "is_active_flag" in field_list:
                                    if self.config_dict["condition"][-1]["and_or"] == ")":
                                        self.config_dict["condition"][-1]["and_or"] = ") AND "
                                    self.config_dict["condition"].append(
                                        {
                                            "table_name": self.sql_join_table_names[i],
                                            "column_name": "is_active_flag",
                                            "condition": "Equal to",
                                            "input_value": "NULL",
                                            "and_or": "",
                                            "constraintName": "is_active_contraint" + str(i),
                                            "ruleSet": "is_active_rule_set" + str(i + 1),
                                        }
                                    )
                                    self.config_dict["condition"].append(
                                        {
                                            "table_name": self.sql_join_table_names[i],
                                            "column_name": "is_active_flag",
                                            "condition": "Not Equal to",
                                            "input_value": "No",
                                            "and_or": "",
                                            "constraintName": "is_active_contraint" + str(i),
                                            "ruleSet": "is_active_rule_set" + str(i + 2),
                                        }
                                    )
                                else:
                                    pass
                            else:
                                pass
                    else:
                        pass
            else:
                pass
            date_type_columns = [
                field.name
                for field in self.model_class.concrete_fields
                if field.get_internal_type() in ["DateField"]
            ]
            datetime_type_columns = [
                field.name
                for field in self.model_class.concrete_fields
                if field.get_internal_type() in ["DateTimeField"]
            ]
            numeric_type_columns = [
                field.name
                for field in self.model_class.concrete_fields
                if field.get_internal_type() in ["IntegerField", "BigIntegerField", "FloatField"]
            ]
            blob_type_columns = [
                field.name
                for field in self.model_class.concrete_fields
                if field.get_internal_type() in ["BinaryField"]
            ]
            if self.config_dict.get("apply_join"):
                for i, table in enumerate(self.join_table_names):
                    if i == 0:
                        continue
                    date_type_columns.extend(
                        [
                            field.name
                            for field in self.join_tables_model_classes[table].concrete_fields
                            if field.get_internal_type() in ["DateField"]
                        ]
                    )
                    datetime_type_columns.extend(
                        [
                            field.name
                            for field in self.join_tables_model_classes[table].concrete_fields
                            if field.get_internal_type() in ["DateTimeField"]
                        ]
                    )
                    numeric_type_columns.extend(
                        [
                            field.name
                            for field in self.join_tables_model_classes[table].concrete_fields
                            if field.get_internal_type() in ["IntegerField", "BigIntegerField", "FloatField"]
                        ]
                    )
                    blob_type_columns.extend(
                        [
                            field.name
                            for field in self.join_tables_model_classes[table].concrete_fields
                            if field.get_internal_type() in ["BinaryField"]
                        ]
                    )

        elif not self.if_app_db_call and self.config_dict.get("condition"):
            date_type_columns = [i for i, t in self.data_type.items() if t == "DATE"]
            datetime_type_columns = [i for i, t in self.data_type.items() if t.startswith("TIMESTAMP")]
            numeric_type_columns = [
                i for i, t in self.data_type.items() if t in ["NUMBER", "FLOAT", "NUMBER(37)"]
            ]
            blob_type_columns = [i for i, t in self.data_type.items() if t in ["BLOB"]]
        else:
            pass

        where_clause_query = self.where_clause_generator(
            date_type_columns, datetime_type_columns, numeric_type_columns, blob_type_columns
        )

        if where_clause_query:
            sql_query = f"select {self.agg_query} {self.columns_string} from {self.sql_table_name} where {where_clause_query} {self.order_query} {self.group_by_query} {self.top_query}"
        else:
            sql_query = f"select {self.agg_query} {self.columns_string} from {self.sql_table_name} {self.order_query} {self.group_by_query} {self.top_query}"

        if self.config_dict.get("apply_join"):
            if where_clause_query:
                sql_query = f"select {self.join_columns} from {self.sql_table_name} {self.join_query} where {where_clause_query} {self.group_by_query}"
                if (
                    self.config_dict.get("join_table_data")
                    .get("join_table_level_conditions", {})
                    .get(self.sql_table_name, {})
                ):
                    condition_sub_query = self.condition_sub_query_generator(
                        self.config_dict.get("join_table_data").get("join_table_level_conditions"),
                        self.sql_table_name,
                    )
                    sql_query = f"select {self.join_columns} from ({condition_sub_query}) {self.sql_table_name} {self.join_query} where {where_clause_query} {self.group_by_query}"
            else:
                sql_query = f"select {self.join_columns} from {self.sql_table_name} {self.join_query} {self.group_by_query}"
                if (
                    self.config_dict.get("join_table_data")
                    .get("join_table_level_conditions", {})
                    .get(self.sql_table_name, {})
                ):
                    condition_sub_query = self.condition_sub_query_generator(
                        self.config_dict.get("join_table_data").get("join_table_level_conditions"),
                        self.sql_table_name,
                    )
                    sql_query = f"select {self.join_columns} from ({condition_sub_query}) {self.sql_table_name} {self.join_query} {self.group_by_query}"

        if self.config_dict.get("order_by_configs"):
            sql_query += f" {self.order_by_query_string}"

        return sql_query

    def update_query_generator(self):
        if self.table not in self.db_info_tables + admin_tables and self.if_app_db_call:
            date_type_columns = [
                field.name
                for field in self.model_class.concrete_fields
                if field.get_internal_type() in ["DateField"]
            ]
            datetime_type_columns = [
                field.name
                for field in self.model_class.concrete_fields
                if field.get_internal_type() in ["DateTimeField"]
            ]
            numeric_type_columns = [
                field.name
                for field in self.model_class.concrete_fields
                if field.get_internal_type() in ["IntegerField", "BigIntegerField", "FloatField"]
            ]
            blob_type_columns = [
                field.name
                for field in self.model_class.concrete_fields
                if field.get_internal_type() in ["BinaryField"]
            ]
        elif not self.if_app_db_call and self.config_dict.get("condition"):
            date_type_columns = [i for i, t in self.data_type.items() if t == "DATE"]
            datetime_type_columns = [i for i, t in self.data_type.items() if t.startswith("TIMESTAMP")]
        else:
            date_type_columns = []
            datetime_type_columns = []
            numeric_type_columns = []
            blob_type_columns = []
        updated_value_string = ""
        parameter_dict = {}
        for update_conf in self.update_columns:
            column_name = update_conf["column_name"]
            input_value = update_conf["input_value"]
            separator = update_conf["separator"]
            if input_value != "NULL" and input_value:
                if column_name in date_type_columns:
                    input_value = pd.to_datetime(input_value).date()
                elif column_name in datetime_type_columns:
                    input_value = pd.to_datetime(input_value)
                elif column_name in blob_type_columns:
                    input_value = io.BytesIO(input_value.encode("utf-8")).getvalue()
                else:
                    pass
                updated_value_string += "{field} = :{field} {separator}".format(
                    field=column_name,
                    separator=separator,
                )
                parameter_dict[column_name] = input_value
            else:
                updated_value_string += "{field} = NULL {separator}".format(
                    field=column_name,
                    separator=separator,
                )

        where_clause_query = self.where_clause_generator(
            date_type_columns, datetime_type_columns, numeric_type_columns, blob_type_columns
        )
        if where_clause_query:
            update_query = "UPDATE {table} SET {updated_val} WHERE {where}".format(
                table=self.sql_table_name,
                updated_val=updated_value_string,
                where=where_clause_query,
            )
        else:
            update_query = "UPDATE {table} SET {updated_val}".format(
                table=self.sql_table_name,
                updated_val=updated_value_string,
            )
        return update_query, parameter_dict

    def delete_query_generator(self):
        date_type_columns = []
        datetime_type_columns = []
        numeric_type_columns = []
        blob_type_columns = []
        if self.table not in self.db_info_tables + admin_tables + sys_tables and self.if_app_db_call:
            date_type_columns = [
                field.name
                for field in self.model_class.concrete_fields
                if field.get_internal_type() in ["DateField"]
            ]
            datetime_type_columns = [
                field.name
                for field in self.model_class.concrete_fields
                if field.get_internal_type() in ["DateTimeField"]
            ]
            numeric_type_columns = [
                field.name
                for field in self.model_class.concrete_fields
                if field.get_internal_type() in ["IntegerField", "BigIntegerField", "FloatField"]
            ]
            blob_type_columns = [
                field.name
                for field in self.model_class.concrete_fields
                if field.get_internal_type() in ["BinaryField"]
            ]
        else:
            pass

        where_clause_query = self.where_clause_generator(
            date_type_columns, datetime_type_columns, numeric_type_columns, blob_type_columns
        )
        if where_clause_query:
            delete_query = "DELETE FROM {table} WHERE {where}".format(
                table=self.sql_table_name,
                where=where_clause_query,
            )
        else:
            delete_query = "DELETE FROM {table}".format(
                table=self.sql_table_name,
            )
        return delete_query

    def bulk_update_query_generator(self, upsert=False, data=None):
        if self.table not in self.db_info_tables + admin_tables and self.if_app_db_call:
            date_type_columns = [
                field.name
                for field in self.model_class.concrete_fields
                if field.get_internal_type() in ["DateField"]
            ]
            datetime_type_columns = [
                field.name
                for field in self.model_class.concrete_fields
                if field.get_internal_type() in ["DateTimeField"]
            ]
        elif not self.if_app_db_call:
            date_type_columns = [i for i, t in self.data_type.items() if t == "DATE"]
            datetime_type_columns = [i for i, t in self.data_type.items() if t.startswith("TIMESTAMP")]
        else:
            date_type_columns = []
            datetime_type_columns = []
        update_set_query = ""
        update_columns = self.config_dict["inputs"]["Columns"]
        for set_dic in update_columns:
            if set_dic.get("input_value"):
                if set_dic["input_value"] != "NULL":
                    set_dic["input_value"] = set_dic["input_value"].replace("'", "''")
                    if set_dic["column_name"] in date_type_columns:
                        update_set_query += (
                            " "
                            + set_dic["column_name"]
                            + "= "
                            + "TO_DATE('"
                            + set_dic["input_value"]
                            + "', 'YYYY-MM-DD')"
                            + set_dic["separator"]
                        )
                    elif set_dic["column_name"] in datetime_type_columns:
                        update_set_query += (
                            " "
                            + set_dic["column_name"]
                            + "= "
                            + "TO_DATE('"
                            + set_dic["input_value"]
                            + "', 'YYYY-MM-DD HH24:MI:SS')"
                            + set_dic["separator"]
                        )
                    else:
                        update_set_query += (
                            " "
                            + set_dic["column_name"]
                            + "="
                            + "'"
                            + set_dic["input_value"]
                            + "'"
                            + set_dic["separator"]
                        )
                else:
                    update_set_query += " " + set_dic["column_name"] + "=" + "NULL" + set_dic["separator"]
            else:
                if set_dic["column_name"] in date_type_columns:
                    update_set_query += (
                        " "
                        + set_dic["column_name"]
                        + "= "
                        + "TO_DATE("
                        + f':{set_dic["column_name"]}'
                        + ", 'YYYY-MM-DD')"
                        + set_dic["separator"]
                    )
                elif set_dic["column_name"] in datetime_type_columns:
                    update_set_query += (
                        " "
                        + set_dic["column_name"]
                        + "= "
                        + "TO_DATE("
                        + f':{set_dic["column_name"]}'
                        + ", 'YYYY-MM-DD HH24:MI:SS')"
                        + set_dic["separator"]
                    )
                else:
                    update_set_query += (
                        " "
                        + set_dic["column_name"]
                        + "="
                        + f':{set_dic["column_name"]}'
                        + set_dic["separator"]
                    )

        if self.config_dict.get("condition"):
            where_string = " AND ".join(
                f"{cond['column_name']} = :{cond['column_name']}" for cond in self.config_dict["condition"]
            )
        else:
            where_string = ""
        if not upsert:
            if where_string:
                update_query = f"UPDATE {self.sql_table_name} SET {update_set_query} WHERE {where_string}"
            else:
                update_query = f"UPDATE {self.sql_table_name} SET {update_set_query}"
        else:
            insert_cols = ", ".join(data.columns.tolist())
            values_string = ""
            for col in data.columns.tolist():
                if col in date_type_columns:
                    data[col] = pd.to_datetime(data[col]).dt.strftime("%Y-%m-%d")
                    values_string += f"TO_DATE(:{col}, 'YYYY-MM-DD'), "
                elif col in datetime_type_columns:
                    data[col] = pd.to_datetime(data[col]).dt.strftime("%Y-%m-%d %H:%M:%S")
                    values_string += f"TO_DATE(:{col}, 'YYYY-MM-DD HH24:MI:SS'), "
                else:
                    values_string += f":{col}, "
            values_string = values_string.rstrip(", ")
            if where_string:
                update_query = f"""BEGIN UPDATE {self.sql_table_name} SET {update_set_query} WHERE ({where_string}); IF sql%rowcount=0 THEN INSERT into {self.sql_table_name} ({insert_cols}) values ({values_string}); END IF; END;"""
            else:
                update_query = f"UPDATE {self.sql_table_name} SET {update_set_query}"

        return update_query

    def join_query_generator(self):
        join_table_data = self.config_dict.get("join_table_data").copy()
        apply_join = self.config_dict.get("apply_join")
        aliases_joins = self.config_dict.get("aliases")
        table_names = self.sql_join_table_names.copy()
        join_table_level_conditions = self.config_dict.get("join_table_data", {}).get(
            "join_table_level_conditions", {}
        )

        common_columns = self.config_dict.get("common_columns")
        type_of_join = self.config_dict.get("type_of_join")

        join_select_columns = ""
        columns_set = set()
        for table in join_table_data["tables"]:
            table_name = table
            if "users_" + table.lower() in table_names:
                table_name = "users_" + table_name.lower()
            else:
                pass
            columns_joins = join_table_data["tables"][table]
            for column in columns_joins:
                if aliases_joins and aliases_joins.get("join_table_aliases"):
                    if aliases_joins["join_table_aliases"].get(table):
                        alias = aliases_joins["join_table_aliases"][table].get(column, "")
                    else:
                        alias = ""
                else:
                    alias = ""
                if column not in columns_set:
                    if alias != "":
                        join_select_columns += f'{table_name}.{column} as "{alias}", '
                    if alias == "":
                        join_select_columns += f"{table_name}.{column}, "
                else:
                    if alias != "":
                        join_select_columns += f'{table_name}.{column} as "{alias}", '
                    if alias == "":
                        join_select_columns += f'{table_name}.{column} as "{table}.{column}", '
                columns_set.add(column)
        join_select_columns = join_select_columns[:-2]

        join_query = ""
        for i, table in enumerate(table_names):
            if i == 0:
                continue
            join_statement = f"{table}.{common_columns[i]} = {table_names[0]}.{common_columns[0]}"
            if join_table_level_conditions.get(table):
                join_sub_query = self.condition_sub_query_generator(join_table_level_conditions, table)
                join_query += f" {type_of_join} ({join_sub_query}) {table} ON {join_statement} "
            else:
                join_query += f" {type_of_join} {table} ON {join_statement}"

        return join_select_columns, join_query

    def condition_sub_query_generator(self, conditions, sql_table_name):
        table_name = conditions.get(sql_table_name)[0]["table"]
        for table_level_condition in conditions.get(sql_table_name):
            table_level_condition["table_name"] = sql_table_name
        config_conditons = None
        if self.config_dict.get("condition"):
            config_conditons = self.config_dict.get("condition").copy()
        self.config_dict["condition"] = conditions.get(sql_table_name)
        date_type_columns = [
            field.name
            for field in self.join_tables_model_classes[table_name].concrete_fields
            if field.get_internal_type() in ["DateField"]
        ]
        datetime_type_columns = [
            field.name
            for field in self.join_tables_model_classes[table_name].concrete_fields
            if field.get_internal_type() in ["DateTimeField"]
        ]
        numeric_type_columns = [
            field.name
            for field in self.join_tables_model_classes[table_name].concrete_fields
            if field.get_internal_type() in ["IntegerField", "BigIntegerField", "FloatField"]
        ]
        blob_type_columns = [
            field.name
            for field in self.join_tables_model_classes[table_name].concrete_fields
            if field.get_internal_type() in ["BinaryField"]
        ]
        where_clause_query = self.where_clause_generator(
            date_type_columns, datetime_type_columns, numeric_type_columns, blob_type_columns
        )
        sub_query = ("SELECT * FROM {sql_table_name} WHERE {where_clause_query}").format(
            sql_table_name=sql_table_name, where_clause_query=where_clause_query
        )
        if config_conditons:
            self.config_dict["condition"] = config_conditons
        else:
            self.config_dict["condition"] = []
        return sub_query

    def group_by_query_generator(self):
        aliases = self.config_dict.get("aliases")
        group_by_select_columns = ""
        group_by_query = ""
        group_by_aggregations = {}

        columns_set = set()
        for table in self.config_dict["group_by_configs"]["group_by_tables"]:

            sql_table_name = self.sql_table_name_identifier(table_name=table)
            for column in self.config_dict["group_by_configs"]["group_by_columns"][table]:
                if aliases and aliases.get("join_table_aliases"):
                    if aliases["join_table_aliases"].get(table):
                        alias = aliases["join_table_aliases"][table].get(column, "")
                    else:
                        alias = ""
                else:
                    alias = ""
                group_by_query += f"{sql_table_name}.{column}, "
                if column not in columns_set:
                    if alias != "":
                        group_by_select_columns += f'{sql_table_name}.{column} AS "{alias}", '
                    if alias == "":
                        group_by_select_columns += f"{sql_table_name}.{column}, "
                else:
                    if alias != "":
                        group_by_select_columns += f'{sql_table_name}.{column} AS "{alias}", '
                    if alias == "":
                        group_by_select_columns += (
                            f'{sql_table_name}.{column} AS "{sql_table_name}.{column}", '
                        )
                columns_set.add(column)
            if self.config_dict["group_by_configs"].get("aggregations"):
                aggregations = self.config_dict["group_by_configs"]["aggregations"].get(table)
                if aggregations:
                    for key, aggregations_list in aggregations.items():
                        group_by_aggregations[f"{sql_table_name}.{key}"] = aggregations_list
                else:
                    pass
            else:
                pass

        group_by_select_columns = group_by_select_columns[:-2]
        group_by_query = group_by_query[:-2]

        return group_by_select_columns, group_by_query, group_by_aggregations


# PostgreSQL where clause query generator
def postgres_condition_generator(config_dict, cond_date_list, cond_datetime_list, sql_table_name=""):
    """
    Generates the where clause query for PostgreSQL DB calls
    config_dict: List of condition dictionaries
    cond_date_list: List of date type columns
    cond_datetime_list: List of timestamp type columns
    """

    condition_string = ""
    condition_list = []
    # Condition check
    new_condition_format = False
    if config_dict.get("condition"):
        if config_dict["condition"][0].get("constraintName") and config_dict["condition"][0].get("ruleSet"):
            new_condition_format = True
        else:
            pass
        base_condition_exists = True
    else:
        base_condition_exists = False

    condition_string_mapping_dict = {
        "Greater than": "{field} > {value} {and_or}",
        "Smaller than": "{field} < {value} {and_or}",
        "Greater than equal to": "{field} >= {value} {and_or}",
        "Smaller than equal to": "{field} <= {value} {and_or}",
        "Equal to": "{field} = {value} {and_or}",
        "Not Equal to": "{field} != {value} {and_or}",
        "Between": "{field} BETWEEN {input_value_lower} AND {input_value_upper} {and_or}",
        "IN": "{field} IN {value} {and_or}",
        "NOT IN": "{field} NOT IN {value} {and_or}",
        "Starts with": "CAST({field} AS TEXT) ILIKE {value} {and_or}",
        "Not Starts with": "CAST({field} AS TEXT) NOT ILIKE {value} {and_or}",
        "Ends with": "CAST({field} AS TEXT) ILIKE {value} {and_or}",
        "Not Ends with": "CAST({field} AS TEXT) NOT ILIKE {value} {and_or}",
        "Contains": "CAST({field} AS TEXT) ILIKE {value} {and_or}",
        "Not Contains": "CAST({field} AS TEXT) NOT ILIKE {value} {and_or}",
    }

    if base_condition_exists:
        updated_condition_dict = {}
        if new_condition_format:
            for cond in config_dict["condition"]:
                if not updated_condition_dict.get(cond["constraintName"]):
                    updated_condition_dict[cond["constraintName"]] = {}
                else:
                    pass
                existing_const = updated_condition_dict[cond["constraintName"]]
                if existing_const.get(cond["ruleSet"]):
                    updated_condition_dict[cond["constraintName"]][cond["ruleSet"]].append(cond)
                else:
                    updated_condition_dict[cond["constraintName"]][cond["ruleSet"]] = [cond]
            advance_condition_dict = {}
            if config_dict.get("adv_condition"):
                advance_condition = config_dict["adv_condition"]
                for cond in advance_condition:
                    constraint_name = cond["constraintName"]
                    rule_set = cond["ruleSet"]
                    adv_column_name = cond["column_name"]
                    adv_agg_condition = cond["agg_condition"]
                    if updated_condition_dict.get(constraint_name):
                        base_conditions = updated_condition_dict[constraint_name]
                        base_cons_condition = constraint_query_generator(
                            base_conditions, cond_datetime_list, sql_table_name=sql_table_name
                        )
                        advance_condition_cons = sql.SQL(
                            "{field} = (SELECT {adv_agg_condition}({field}) FROM {sql_table_name} WHERE {base_cons_condition})"
                        ).format(
                            field=sql.Identifier(adv_column_name),
                            adv_agg_condition=sql.SQL(adv_agg_condition),
                            sql_table_name=sql_table_name,
                            base_cons_condition=base_cons_condition,
                        )
                    else:
                        advance_condition_cons = sql.SQL(
                            "{field} = (SELECT {adv_agg_condition}({field}) FROM {sql_table_name})"
                        ).format(
                            field=sql.Identifier(adv_column_name),
                            adv_agg_condition=sql.SQL(adv_agg_condition),
                            sql_table_name=sql_table_name,
                        )
                    if advance_condition_dict.get(constraint_name):
                        if advance_condition_dict[constraint_name].get(rule_set):
                            advance_condition_dict[constraint_name][rule_set].append(sql.SQL(" AND "))
                            advance_condition_dict[constraint_name][rule_set].append(advance_condition_cons)
                        else:
                            advance_condition_dict[constraint_name][rule_set] = [advance_condition_cons]
                    else:
                        advance_condition_dict[constraint_name] = {rule_set: [advance_condition_cons]}
            else:
                pass

            for const, const_conf in updated_condition_dict.items():
                if advance_condition_dict.get(const):
                    cons_advance_dict = advance_condition_dict[const]
                else:
                    cons_advance_dict = {}
                constraint_condition = constraint_query_generator(
                    const_conf, cond_datetime_list, cons_advance_dict, sql_table_name=sql_table_name
                )
                condition_list.append(constraint_condition)
                if list(updated_condition_dict.keys()).index(const) != len(updated_condition_dict.keys()) - 1:
                    condition_list.append(sql.SQL("AND"))
                else:
                    pass
            for const, const_conf in advance_condition_dict.items():
                if const not in updated_condition_dict:
                    condition_list.append(sql.SQL("AND"))
                    for rule in const_conf.values():
                        condition_list.extend(rule)
                else:
                    continue
        else:
            for i in range(0, len(config_dict["condition"])):
                if (
                    config_dict["condition"][i]["condition"] != "Between"
                    and config_dict["condition"][i]["condition"] != "IN"
                ):
                    if config_dict["condition"][i]["column_name"] in cond_date_list:
                        config_dict["condition"][i]["input_value"] = pd.to_datetime(
                            config_dict["condition"][i]["input_value"]
                        ).strftime("%Y-%m-%d")
                    elif config_dict["condition"][i]["column_name"] in cond_datetime_list:
                        config_dict["condition"][i]["input_value"] = pd.to_datetime(
                            config_dict["condition"][i]["input_value"]
                        ).strftime("%Y-%m-%d %H:%M:%S.%f")
                    else:
                        pass
                else:
                    if config_dict["condition"][i]["condition"] != "IN":
                        if config_dict["condition"][i]["column_name"] in cond_date_list:
                            config_dict["condition"][i]["input_value_lower"] = pd.to_datetime(
                                config_dict["condition"][i]["input_value_lower"]
                            ).strftime("%Y-%m-%d")
                            config_dict["condition"][i]["input_value_upper"] = pd.to_datetime(
                                config_dict["condition"][i]["input_value_upper"]
                            ).strftime("%Y-%m-%d")
                        elif config_dict["condition"][i]["column_name"] in cond_datetime_list:
                            config_dict["condition"][i]["input_value_lower"] = pd.to_datetime(
                                config_dict["condition"][i]["input_value_lower"]
                            ).strftime("%Y-%m-%d %H:%M:%S.%f")
                            config_dict["condition"][i]["input_value_upper"] = pd.to_datetime(
                                config_dict["condition"][i]["input_value_upper"]
                            ).strftime("%Y-%m-%d %H:%M:%S.%f")
                        else:
                            pass
                    else:
                        pass

                end_bracket_query = ""
                if config_dict["condition"][i]["column_name"].startswith("("):
                    config_dict["condition"][i]["column_name"] = config_dict["condition"][i]["column_name"][
                        1:
                    ]
                    condition_list.append(sql.SQL("("))
                else:
                    pass
                if config_dict["condition"][i]["and_or"].endswith(")"):
                    config_dict["condition"][i]["and_or"] = config_dict["condition"][i]["and_or"][:-1]
                    end_bracket_query = sql.SQL(")")
                else:
                    end_bracket_query = ""

                if config_dict["condition"][i]["condition"] == "Greater than":
                    try:
                        bool(float(config_dict["condition"][i]["input_value"]))
                    except Exception as e:
                        logging.warning(f"Following exception occured - {e}")
                        condition_list.append(
                            sql.SQL("{field} > {value} {and_or}").format(
                                field=sql.Identifier(config_dict["condition"][i]["column_name"].lower()),
                                value=sql.Literal(config_dict["condition"][i]["input_value"]),
                                and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                            )
                        )
                    else:
                        condition_list.append(
                            sql.SQL("{field} > {value} {and_or}").format(
                                field=sql.Identifier(config_dict["condition"][i]["column_name"].lower()),
                                value=sql.Literal(config_dict["condition"][i]["input_value"]),
                                and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                            )
                        )
                elif config_dict["condition"][i]["condition"] == "Smaller than":
                    try:
                        bool(float(config_dict["condition"][i]["input_value"]))
                    except Exception as e:
                        logging.warning(f"Following exception occured - {e}")
                        condition_list.append(
                            sql.SQL("{field} < {value} {and_or}").format(
                                field=sql.Identifier(config_dict["condition"][i]["column_name"].lower()),
                                value=sql.Literal(config_dict["condition"][i]["input_value"]),
                                and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                            )
                        )
                    else:
                        condition_list.append(
                            sql.SQL("{field} < {value} {and_or}").format(
                                field=sql.Identifier(config_dict["condition"][i]["column_name"].lower()),
                                value=sql.Literal(config_dict["condition"][i]["input_value"]),
                                and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                            )
                        )
                elif config_dict["condition"][i]["condition"] == "Smaller than equal to":
                    try:
                        bool(float(config_dict["condition"][i]["input_value"]))
                    except Exception as e:
                        logging.warning(f"Following exception occured - {e}")
                        condition_list.append(
                            sql.SQL("{field} <= {value} {and_or}").format(
                                field=sql.Identifier(config_dict["condition"][i]["column_name"].lower()),
                                value=sql.Literal(config_dict["condition"][i]["input_value"]),
                                and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                            )
                        )
                    else:
                        condition_list.append(
                            sql.SQL("{field} <= {value} {and_or}").format(
                                field=sql.Identifier(config_dict["condition"][i]["column_name"].lower()),
                                value=sql.Literal(config_dict["condition"][i]["input_value"]),
                                and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                            )
                        )
                elif config_dict["condition"][i]["condition"] == "Greater than equal to":
                    try:
                        bool(float(config_dict["condition"][i]["input_value"]))
                    except Exception as e:
                        logging.warning(f"Following exception occured - {e}")
                        condition_list.append(
                            sql.SQL("{field} >= {value} {and_or}").format(
                                field=sql.Identifier(config_dict["condition"][i]["column_name"].lower()),
                                value=sql.Literal(config_dict["condition"][i]["input_value"]),
                                and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                            )
                        )
                    else:
                        condition_list.append(
                            sql.SQL("{field} >= {value} {and_or}").format(
                                field=sql.Identifier(config_dict["condition"][i]["column_name"].lower()),
                                value=sql.Literal(config_dict["condition"][i]["input_value"]),
                                and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                            )
                        )
                elif config_dict["condition"][i]["condition"] == "Equal to":
                    if config_dict["condition"][i]["input_value"] != "NULL":
                        condition_list.append(
                            sql.SQL("{field} = {value} {and_or}").format(
                                field=sql.Identifier(config_dict["condition"][i]["column_name"].lower()),
                                value=sql.Literal(config_dict["condition"][i]["input_value"]),
                                and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                            )
                        )
                    else:
                        condition_list.append(
                            sql.SQL("{field} is NULL {and_or}").format(
                                field=sql.Identifier(config_dict["condition"][i]["column_name"].lower()),
                                and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                            )
                        )
                elif config_dict["condition"][i]["condition"] == "Between":
                    condition_list.append(
                        "{field} BETWEEN {input_value_lower} AND {input_value_upper} {and_or}".format(
                            field=sql.Identifier(config_dict["condition"][i]["column_name"].lower()),
                            input_value_lower=sql.Literal(config_dict["condition"][i]["input_value_lower"]),
                            input_value_upper=sql.Literal(config_dict["condition"][i]["input_value_upper"]),
                            and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                        )
                    )
                elif config_dict["condition"][i]["condition"] == "IN":
                    if type(config_dict["condition"][i]["input_value"]) != str:
                        config_dict["condition"][i]["input_value"] = str(
                            tuple(config_dict["condition"][i]["input_value"])
                        ).replace(",)", ")")
                    condition_list.append(
                        sql.SQL("{field} IN {value} {and_or}").format(
                            field=sql.Identifier(config_dict["condition"][i]["column_name"].lower()),
                            value=sql.SQL(config_dict["condition"][i]["input_value"]),
                            and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                        )
                    )
                elif config_dict["condition"][i]["condition"] == "NOT IN":
                    if type(config_dict["condition"][i]["input_value"]) != str:
                        config_dict["condition"][i]["input_value"] = str(
                            tuple(config_dict["condition"][i]["input_value"])
                        ).replace(",)", ")")
                    condition_list.append(
                        sql.SQL("{field} NOT IN {value} {and_or}").format(
                            field=sql.Identifier(config_dict["condition"][i]["column_name"].lower()),
                            value=sql.SQL(config_dict["condition"][i]["input_value"]),
                            and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                        )
                    )
                elif config_dict["condition"][i]["condition"] == "Not Equal to":
                    if config_dict["condition"][i]["input_value"] != "NULL":
                        condition_list.append(
                            sql.SQL("{field} != {value} {and_or}").format(
                                field=sql.Identifier(config_dict["condition"][i]["column_name"].lower()),
                                value=sql.Literal(config_dict["condition"][i]["input_value"]),
                                and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                            )
                        )
                    else:
                        condition_list.append(
                            sql.SQL("{field} is NOT NULL {and_or}").format(
                                field=sql.Identifier(config_dict["condition"][i]["column_name"].lower()),
                                and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                            )
                        )

                elif config_dict["condition"][i]["condition"] == "Starts with":
                    if "to_char" not in config_dict["condition"][i]["column_name"].lower():
                        condition_list.append(
                            sql.SQL("{field} LIKE {value} {and_or}").format(
                                field=sql.Identifier(config_dict["condition"][i]["column_name"].lower()),
                                value=sql.Literal(config_dict["condition"][i]["input_value"] + "%%"),
                                and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                            )
                        )
                    else:
                        condition_list.append(
                            sql.SQL("{field} LIKE {value} {and_or}").format(
                                field=sql.SQL(config_dict["condition"][i]["column_name"].lower()),
                                value=sql.Literal(config_dict["condition"][i]["input_value"] + "%%"),
                                and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                            )
                        )

                elif config_dict["condition"][i]["condition"] == "Ends with":
                    condition_list.append(
                        sql.SQL("{field} LIKE {value} {and_or}").format(
                            field=sql.Identifier(config_dict["condition"][i]["column_name"].lower()),
                            value=sql.Literal("%%" + config_dict["condition"][i]["input_value"]),
                            and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                        )
                    )
                elif config_dict["condition"][i]["condition"] == "Contains":
                    condition_list.append(
                        sql.SQL("{field} LIKE {value} {and_or}").format(
                            field=sql.Identifier(config_dict["condition"][i]["column_name"].lower()),
                            value=sql.Literal("%%" + config_dict["condition"][i]["input_value"] + "%%"),
                            and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                        )
                    )
                elif config_dict["condition"][i]["condition"] == "Not Starts with":
                    condition_list.append(
                        sql.SQL("{field} NOT LIKE {value} {and_or}").format(
                            field=sql.Identifier(config_dict["condition"][i]["column_name"].lower()),
                            value=sql.Literal(config_dict["condition"][i]["input_value"] + "%%"),
                            and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                        )
                    )
                elif config_dict["condition"][i]["condition"] == "Not Ends with":
                    condition_list.append(
                        sql.SQL("{field} NOT LIKE {value} {and_or}").format(
                            field=sql.Identifier(config_dict["condition"][i]["column_name"].lower()),
                            value=sql.Literal("%%" + config_dict["condition"][i]["input_value"]),
                            and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                        )
                    )
                elif config_dict["condition"][i]["condition"] == "Not Contains":
                    condition_list.append(
                        sql.SQL("{field} NOT LIKE {value} {and_or}").format(
                            field=sql.Identifier(config_dict["condition"][i]["column_name"].lower()),
                            value=sql.Literal("%%" + config_dict["condition"][i]["input_value"] + "%%"),
                            and_or=sql.SQL(config_dict["condition"][i]["and_or"]),
                        )
                    )
                else:
                    pass

                if end_bracket_query:
                    condition_list.append(end_bracket_query)
                else:
                    continue
    else:
        if config_dict.get("adv_condition"):
            advance_condition = config_dict["adv_condition"]
            advance_condition_dict = {}
            for cond in advance_condition:
                constraint_name = cond["constraintName"]
                rule_set = cond["ruleSet"]
                adv_column_name = cond["column_name"]
                adv_agg_condition = cond["agg_condition"]
                advance_condition_cons = sql.SQL(
                    "{field} = (SELECT {adv_agg_condition}({field}) FROM {sql_table_name})"
                ).format(
                    field=sql.Identifier(adv_column_name),
                    adv_agg_condition=sql.SQL(adv_agg_condition),
                    sql_table_name=sql_table_name,
                )
                if advance_condition_dict.get(constraint_name):
                    if advance_condition_dict[constraint_name].get(rule_set):
                        advance_condition_dict[constraint_name][rule_set].append(sql.SQL("AND"))
                        advance_condition_dict[constraint_name][rule_set].append(advance_condition_cons)
                    else:
                        advance_condition_dict[constraint_name][rule_set] = [advance_condition_cons]
                else:
                    advance_condition_dict[constraint_name] = {rule_set: [advance_condition_cons]}
            for const, rule in advance_condition_dict.items():
                condition_list = []
                condition_list.append(sql.SQL("("))
                for rule_set, cond_list in rule.items():
                    rule_cond = sql.SQL(" ").join([i for i in cond_list])
                    condition_list.append(rule_cond)
                    if list(rule.keys()).index(rule_set) != len(rule) - 1:
                        condition_list.append(sql.SQL("OR"))
                    else:
                        pass
                condition_list.append(sql.SQL(")"))
                if list(advance_condition_dict.keys()).index(const) != len(advance_condition_dict) - 1:
                    condition_list.append(sql.SQL("AND"))
                else:
                    pass
        else:
            pass
    condition_string = sql.SQL(" ").join([i for i in condition_list])
    return condition_string


def constraint_query_generator(const_conf, cond_datetime_list, advance_condition_dict={}, sql_table_name=""):
    condition_string_mapping_dict = {
        "Greater than": "{field} > {value} {and_or}",
        "Smaller than": "{field} < {value} {and_or}",
        "Greater than equal to": "{field} >= {value} {and_or}",
        "Smaller than equal to": "{field} <= {value} {and_or}",
        "Equal to": "{field} = {value} {and_or}",
        "Not Equal to": "{field} != {value} {and_or}",
        "Between": "{field} BETWEEN {input_value_lower} AND {input_value_upper} {and_or}",
        "IN": "{field} IN {value} {and_or}",
        "NOT IN": "{field} NOT IN {value} {and_or}",
        "Starts with": "CAST({field} AS TEXT) ILIKE {value} {and_or}",
        "Not Starts with": "CAST({field} AS TEXT) NOT ILIKE {value} {and_or}",
        "Ends with": "CAST({field} AS TEXT) ILIKE {value} {and_or}",
        "Not Ends with": "CAST({field} AS TEXT) NOT ILIKE {value} {and_or}",
        "Contains": "CAST({field} AS TEXT) ILIKE {value} {and_or}",
        "Not Contains": "CAST({field} AS TEXT) NOT ILIKE {value} {and_or}",
    }
    constraint_condition_list = [sql.SQL("(")]
    for rule_set, rule_conf in const_conf.items():
        rule_set_condition_list = []
        for cond_index, cond in enumerate(rule_conf):
            prepend_table_name = False
            table_name = sql_table_name
            if cond.get("table_name"):
                prepend_table_name = True
                table_name = sql.SQL(cond.get("table_name"))
            elif sql_table_name:
                flag = True
                for i in sys_tables + admin_tables + mssql_db_info_tables:
                    if sql.Identifier(i) == sql_table_name:
                        flag = False
                        prepend_table_name = False
                        break
                if flag:
                    prepend_table_name = True

            if prepend_table_name:
                field_identifier = sql.SQL("{table}.{field}").format(
                    table=table_name, field=sql.Identifier(cond["column_name"].lower())
                )
            else:
                field_identifier = sql.Identifier(cond["column_name"].lower())
            if cond_index == len(rule_conf) - 1:
                and_or = ""
            else:
                and_or = "AND"
            if cond["condition"] not in [
                "IN",
                "NOT IN",
                "Starts with",
                "Not Starts with",
                "Ends with",
                "Not Ends with",
                "Contains",
                "Not Contains",
            ]:
                if cond["condition"] != "Between" and cond.get("input_value"):
                    if cond["input_value"] != "NULL":
                        if cond["column_name"] in cond_datetime_list:
                            rule_set_condition_list.append(
                                sql.SQL(condition_string_mapping_dict[cond["condition"]]).format(
                                    field=field_identifier,
                                    value=sql.Literal(
                                        pd.to_datetime(cond["input_value"]).strftime(
                                            "%Y-%m-%d %H:%M:%S.%f"
                                        )
                                    ),
                                    and_or=sql.SQL(and_or),
                                )
                            )
                        else:
                            rule_set_condition_list.append(
                                sql.SQL(condition_string_mapping_dict[cond["condition"]]).format(
                                    field=field_identifier,
                                    value=sql.Literal(cond["input_value"]),
                                    and_or=sql.SQL(and_or),
                                )
                            )
                    else:
                        if cond["condition"] == "Equal to":
                            rule_set_condition_list.append(
                                sql.SQL("{field} is NULL {and_or}").format(
                                    field=field_identifier,
                                    and_or=sql.SQL(and_or),
                                )
                            )
                        else:
                            rule_set_condition_list.append(
                                sql.SQL("{field} is NOT NULL {and_or}").format(
                                    field=field_identifier,
                                    and_or=sql.SQL(and_or),
                                )
                            )
                elif cond["condition"] == "Between":
                    rule_set_condition_list.append(
                        sql.SQL(condition_string_mapping_dict[cond["condition"]]).format(
                            field=field_identifier,
                            input_value_lower=sql.Literal(cond["input_value_lower"]),
                            input_value_upper=sql.Literal(cond["input_value_upper"]),
                            and_or=sql.SQL(and_or),
                        )
                    )
                else:
                    pass
            elif cond["condition"] in ["Starts with", "Not Starts with"]:
                rule_set_condition_list.append(
                    sql.SQL(condition_string_mapping_dict[cond["condition"]]).format(
                        field=field_identifier,
                        value=sql.Literal(cond["input_value"] + "%%"),
                        and_or=sql.SQL(and_or),
                    )
                )
            elif cond["condition"] in ["Ends with", "Not Ends with"]:
                rule_set_condition_list.append(
                    sql.SQL(condition_string_mapping_dict[cond["condition"]]).format(
                        field=field_identifier,
                        value=sql.Literal("%%" + cond["input_value"]),
                        and_or=sql.SQL(and_or),
                    )
                )
            elif cond["condition"] in ["Contains", "Not Contains"]:
                rule_set_condition_list.append(
                    sql.SQL(condition_string_mapping_dict[cond["condition"]]).format(
                        field=field_identifier,
                        value=sql.Literal("%%" + cond["input_value"] + "%%"),
                        and_or=sql.SQL(and_or),
                    )
                )
            elif cond["condition"] in ["IN", "NOT IN"]:
                if type(cond["input_value"]) != str:
                    cond["input_value"] = str(tuple(cond["input_value"])).replace(",)", ")")
                rule_set_condition_list.append(
                    sql.SQL(condition_string_mapping_dict[cond["condition"]]).format(
                        field=field_identifier,
                        value=sql.SQL(cond["input_value"]),
                        and_or=sql.SQL(and_or),
                    )
                )
            else:
                pass
        if advance_condition_dict.get(rule_set):
            rule_set_condition_list.append(sql.SQL(" AND "))
            rule_set_condition_list.extend(advance_condition_dict[rule_set])
        else:
            pass
        rule_set_condition = sql.SQL(" ").join([i for i in rule_set_condition_list])
        constraint_condition_list.append(rule_set_condition)
        if list(const_conf.keys()).index(rule_set) != len(const_conf.keys()) - 1:
            constraint_condition_list.append(sql.SQL("OR"))
        else:
            pass
    if advance_condition_dict:
        for rule, cond_list in advance_condition_dict.items():
            if rule not in const_conf:
                constraint_condition_list.append(sql.SQL(" OR "))
                constraint_condition_list.extend(cond_list)
            else:
                continue
    else:
        pass
    constraint_condition_list.append(sql.SQL(")"))
    constraint_condition = sql.SQL(" ").join([i for i in constraint_condition_list])
    return constraint_condition
