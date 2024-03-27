from ast import literal_eval
import logging

import numpy as np
import pandas as pd

from kore_investment.users.computations import dynamic_model_create, standardised_functions


class DataTransformation:

    string_dict = {
        "Starts with": "data['{column_name}'].str.startswith('{value}')",
        "Ends with": "data['{column_name}'].str.endswith('{value}')",
        "Contains": "data['{column_name}'].str.contains('{value}')",
        "Not Starts with": "~data['{column_name}'].str.startswith('{value}')",
        "Not Ends with": "~data['{column_name}'].str.endswith('{value}')",
        "Not Contains": "~data['{column_name}'].str.contains('{value}')",
        "Equal to": "data['{column_name}'] == '{value}'",
        "Not Equal to": "data['{column_name}'] != '{value}'",
        "Greater than": "data['{column_name}'] > '{value}'",
        "Smaller than": "data['{column_name}'] < '{value}'",
        "IN": "data['{column_name}'].fillna('NULL').astype('str').isin({value})",
        "NOT IN": "~data['{column_name}'].fillna('NULL').astype('str').isin({value})",
        "Is null": "data['{column_name}'].isna()",
        "Not null": "data['{column_name}'].notna()",
    }
    num_dict = {
        "Equal to": "data['{column_name}'] == {value}",
        "Not Equal to": "data['{column_name}'] != {value}",
        "Greater than": "data['{column_name}'] > {value}",
        "Smaller than": "data['{column_name}'] < {value}",
        "IN": "data['{column_name}'].fillna('NULL').isin({value})",
        "NOT IN": "~data['{column_name}'].fillna('NULL').isin({value})",
        "Is null": "data['{column_name}'].isna()",
        "Not null": "data['{column_name}'].notna()",
    }
    num_dict_cond_merge = {
        "Equal to": "data['{column_name}'] == {value}",
        "Not Equal to": "data['{column_name}'] != {value}",
        "Greater than": "data['{column_name}'] < {value}",
        "Smaller than": "data['{column_name}'] > {value}",
        "IN": "data['{column_name}'].fillna('NULL').isin({value})",
        "NOT IN": "~data['{column_name}'].fillna('NULL').isin({value})",
        "Is null": "data['{column_name}'].isna()",
        "Not null": "data['{column_name}'].notna()",
    }
    date_dict = {
        "Equal to AND": "data['{column_name}'] == '{value}'",
        "Not Equal to AND": "data['{column_name}'] != '{value}'",
        "Greater than AND": "data['{column_name}'] > '{value}'",
        "Smaller than AND": "data['{column_name}'] < '{value}'",
        "Equal to OR": "data['{column_name}'] == '{value}'",
        "Not Equal to OR": "data['{column_name}'] != '{value}'",
        "Greater than OR": "data['{column_name}'] > '{value}'",
        "Smaller than OR": "data['{column_name}'] < '{value}'",
        "IN": "data['{column_name}'].fillna('NULL').astype('str').isin({value})",
        "NOT IN": "~data['{column_name}'].fillna('NULL').astype('str').isin({value})",
        "Is null": "data['{column_name}'].isna()",
        "Not null": "data['{column_name}'].notna()",
    }

    date_dict_cond_merge = {
        "Equal to": "data['{column_name}'] == '{value}'",
        "Not Equal to": "data['{column_name}'] != '{value}'",
        "Greater than": "data['{column_name}'] > '{value}'",
        "Smaller than": "data['{column_name}'] < '{value}'",
        "Equal to": "data['{column_name}'] == '{value}'",
        "Not Equal to": "data['{column_name}'] != '{value}'",
        "Greater than": "data['{column_name}'] > '{value}'",
        "Smaller than": "data['{column_name}'] < '{value}'",
        "IN": "data['{column_name}'].fillna('NULL').astype('str').isin({value})",
        "NOT IN": "~data['{column_name}'].fillna('NULL').astype('str').isin({value})",
        "Is null": "data['{column_name}'].isna()",
        "Not null": "data['{column_name}'].notna()",
    }

    def concat(self, data):
        """
        Concatenats data frame i.e column-wise join
        data: dataframes
        """
        new_data = pd.concat(data, axis=1)
        new_data = new_data.loc[:, ~new_data.columns.duplicated()]
        return new_data

    def append(self, data):
        """
        Appends two data frame i.e. row-wise join
        data: dataframes
        """
        new_data = pd.concat(data, ignore_index=True)
        return new_data

    def join(
        self,
        list1,
        col_rename,
        col_display,
        join_data,
        join_type,
        join_on,
    ):
        """
        Joins dataframes based on some common columns
        join_data: list of data frames
        join_type: Type of join i.e. 'inner', 'outer', 'left', 'right'
        join_on: column names from the dataframes to perform the join on
                "Must be in same order as df"
        """
        j_data = join_data.copy()

        display_list = []
        for j in range(len(j_data)):
            j_data[j] = j_data[j].loc[:, col_display[j]]
            display_list += col_display[j]

        for i in range(len(j_data) - 1):
            j_data[i + 1] = pd.merge(
                left=j_data[i],
                right=j_data[i + 1].rename(columns={join_on[i + 1]: join_on[i]}),
                how=join_type,
                left_on=join_on[i],
                right_on=join_on[i],
            )
        new_data = j_data[-1]
        for i in list(new_data.columns):
            if i not in display_list:
                new_data.drop(i, axis=1, inplace=True)
        new_data.rename(columns=col_rename, inplace=True)
        return new_data

    def join_eq(
        self,
        list1,
        col_rename,
        col_display,
        join_data,
        join_type,
        join_on,
        newly_created,
        request_user,
        table_name,
    ):
        j_data = join_data.copy()
        if newly_created:

            modelName = dynamic_model_create.get_model_class(newly_created, request_user)
            drop_cols_list = [
                "created_by",
                "modified_by",
                "created_date",
                "modified_date",
                "active_to",
                "active_from",
                "approved_by",
                "approval_status",
                modelName.pk.name,
                "id",
                "transaction_id",
                "is_active_flag",
            ]
            columns_list = []
            for field in modelName.concrete_fields:
                if field.name not in drop_cols_list:
                    columns_list.append(field.name)
            index = table_name.index(newly_created)
            col_display[index] = columns_list

        for i in range(len(j_data) - 1):
            num = 0
            display_list = []
            while num < len(col_display):
                j_data[num] = j_data[num].loc[:, col_display[num]]
                display_list = display_list + col_display[num]
                num += 1

            j_data[i + 1] = pd.merge(
                left=j_data[i],
                right=j_data[i + 1].rename(columns={join_on[i + 1]: join_on[i]}),
                how=join_type,
                left_on=join_on[i],
                right_on=join_on[i],
            )
        new_data = j_data[-1]
        if newly_created:
            if join_on[0] != join_on[1]:
                new_data[join_on[1]] = new_data[join_on[0]]
        for i in list(new_data.columns):
            if i not in display_list:
                new_data.drop(i, axis=1, inplace=True)
        new_data.rename(columns=col_rename, inplace=True)
        return new_data

    def conditional_merge(self, data_mapper, condition_dict, parent_data, child_data):
        child_data.reset_index(inplace=True, drop=True)
        string_dict = DataTransformation.string_dict
        num_dict = DataTransformation.num_dict_cond_merge
        date_dict = DataTransformation.date_dict_cond_merge

        field_type_child = child_data.dtypes.apply(lambda x: x.name).to_dict()
        field_type_parent = parent_data.dtypes.apply(lambda x: x.name).to_dict()
        data = parent_data
        eval_string = ""
        for condition, value in condition_dict.items():
            for rule_set, condition_list in value.items():
                condition_col_list = []
                eval_string = "data["
                for index, cond in enumerate(condition_list):
                    condition_col = cond["condition_col"]
                    new_col_name = cond["new_col_name"]
                    condition = cond["condition"]
                    parent_col = cond["parent_col"]
                    target_col = cond["target_col"]
                    basic_op = cond["basic_op"]
                    basic_op_val = cond["basic_op_val"]
                    condition_col_list.append(condition_col)
                    if field_type_child[condition_col] == "object":
                        if index == 0:
                            eval_string = (
                                eval_string
                                + "("
                                + (string_dict[condition].format(column_name=parent_col, value={}))
                                + ")"
                            )
                        else:
                            eval_string = (
                                eval_string
                                + " & ("
                                + (string_dict[condition].format(column_name=parent_col, value={}))
                                + ")"
                            )
                        if index == len(condition_list) - 1:
                            eval_string = eval_string + "]"
                        else:
                            continue
                        for i in range(len(child_data)):
                            value_string = ""
                            for ind, col_name in enumerate(condition_col_list):
                                req_value = child_data[col_name][i]
                                if ind == 0:
                                    if isinstance(req_value, str):
                                        value_string = value_string + "'" + str(req_value) + "'"
                                    else:
                                        value_string = value_string + str(req_value)
                                else:
                                    if isinstance(req_value, str):
                                        value_string = value_string + ", " + "'" + str(req_value) + "'"
                                    else:
                                        value_string = value_string + ", " + str(req_value)
                            req_string = (eval_string + ".")[:-1]
                            req_string = literal_eval("req_string.format(" + value_string + ")")
                            parent = pd.eval(req_string)
                            parent.reset_index(drop=True, inplace=True)

                            if field_type_parent[target_col] == "object":
                                if len(parent[target_col]) > 0:
                                    child_data.loc[i, new_col_name] = parent[target_col][0] + str(
                                        basic_op_val
                                    )

                            elif field_type_parent[target_col] in ["int64", "float64"]:
                                if basic_op == "Add":
                                    child_data.loc[i, new_col_name] = parent[target_col][0] + float(
                                        basic_op_val
                                    )
                                elif basic_op == "Subtract":
                                    child_data.loc[i, new_col_name] = parent[target_col][0] - float(
                                        basic_op_val
                                    )
                                elif basic_op == "Multiply":
                                    child_data.loc[i, new_col_name] = parent[target_col][0] * float(
                                        basic_op_val
                                    )
                                elif basic_op == "Divide":
                                    child_data.loc[i, new_col_name] = parent[target_col][0] / float(
                                        basic_op_val
                                    )
                                else:
                                    child_data.loc[i, new_col_name] = parent[target_col][0]

                            elif field_type_parent[target_col] in ["datetime64[ns]"]:

                                if basic_op == "Add":
                                    try:
                                        child_data.loc[i, new_col_name] = (
                                            pd.to_datetime(parent[target_col][0])
                                            + pd.to_timedelta(basic_op_val, unit="D")
                                        ).dt.strftime("%Y-%m-%d")
                                    except Exception as e:
                                        logging.warning(f"Following exception occured - {e}")
                                        child_data.loc[i, new_col_name] = parent[target_col][0]

                                elif basic_op == "Subtract":
                                    try:
                                        pd.to_datetime(basic_op_val)
                                    except Exception as e:
                                        logging.warning(f"Following exception occured - {e}")
                                        child_data.loc[i, new_col_name] = (
                                            pd.to_datetime(parent[target_col][0])
                                            - pd.to_timedelta(basic_op_val, unit="D")
                                        ).dt.strftime("%Y-%m-%d")
                                    else:
                                        child_data.loc[i, new_col_name] = (
                                            pd.to_datetime(parent[target_col][0])
                                            - pd.to_datetime(basic_op_val)
                                        ).dt.strftime("%Y-%m-%d")
                                else:
                                    child_data.loc[i, new_col_name] = pd.to_datetime(
                                        parent[target_col][0]
                                    )

                            else:
                                child_data.loc[i, new_col_name] = (
                                    str(parent[target_col][0]) + " " + str(basic_op_val)
                                )

                    elif field_type_child[condition_col] in ["int64", "float64"]:
                        if index == 0:
                            eval_string = (
                                eval_string
                                + "("
                                + (num_dict[condition].format(column_name=parent_col, value={}))
                                + ")"
                            )
                        else:
                            eval_string = (
                                eval_string
                                + " & ("
                                + (num_dict[condition].format(column_name=parent_col, value={}))
                                + ")"
                            )
                        if index == len(condition_list) - 1:
                            eval_string = eval_string + "]"
                        else:
                            continue
                        for i in range(len(child_data)):
                            value_string = ""
                            for ind, col_name in enumerate(condition_col_list):
                                req_value = child_data[col_name][i]
                                if type(req_value) == str:
                                    req_value = "'" + req_value + "'"
                                if ind == 0:
                                    value_string = value_string + str(req_value)
                                else:
                                    value_string = value_string + ", " + str(req_value)
                            req_string = (eval_string + ".")[:-1]
                            req_string = literal_eval("req_string.format(" + value_string + ")")
                            parent = pd.eval(req_string)
                            parent.reset_index(drop=True, inplace=True)

                            if field_type_parent[target_col] == "object":
                                child_data.loc[i, new_col_name] = parent[target_col][0] + str(basic_op_val)

                            elif field_type_parent[target_col] in ["int64", "float64"]:
                                if basic_op == "Add":
                                    child_data.loc[i, new_col_name] = parent[target_col][0] + float(
                                        basic_op_val
                                    )
                                elif basic_op == "Subtract":
                                    child_data.loc[i, new_col_name] = parent[target_col][0] - float(
                                        basic_op_val
                                    )
                                elif basic_op == "Multiply":
                                    child_data.loc[i, new_col_name] = parent[target_col][0] * float(
                                        basic_op_val
                                    )
                                elif basic_op == "Divide":
                                    child_data.loc[i, new_col_name] = parent[target_col][0] / float(
                                        basic_op_val
                                    )
                                else:
                                    child_data.loc[i, new_col_name] = parent[target_col][0]

                            elif field_type_parent[target_col] in ["datetime64[ns]"]:
                                if basic_op == "Add":
                                    try:
                                        child_data.loc[i, new_col_name] = (
                                            pd.to_datetime(parent[target_col][0])
                                            + pd.to_timedelta(basic_op_val, unit="D")
                                        ).dt.strftime("%Y-%m-%d")
                                    except Exception as e:
                                        logging.warning(f"Following exception occured - {e}")
                                        child_data.loc[i, new_col_name] = parent[target_col][0]

                                elif basic_op == "Subtract":
                                    try:
                                        pd.to_datetime(basic_op_val)
                                    except Exception as e:
                                        logging.warning(f"Following exception occured - {e}")
                                        child_data.loc[i, new_col_name] = (
                                            pd.to_datetime(parent[target_col][0])
                                            - pd.to_timedelta(basic_op_val, unit="D")
                                        ).dt.strftime("%Y-%m-%d")
                                    else:
                                        child_data.loc[i, new_col_name] = (
                                            pd.to_datetime(parent[target_col][0])
                                            - pd.to_datetime(basic_op_val)
                                        ).dt.strftime("%Y-%m-%d")
                                else:
                                    child_data.loc[i, new_col_name] = pd.to_datetime(
                                        parent[target_col][0]
                                    )

                            else:
                                child_data.loc[i, new_col_name] = (
                                    str(parent[target_col][0]) + " " + str(basic_op_val)
                                )

                    elif field_type_child[condition_col] in ["datetime64[ns]"]:
                        data[parent_col] = pd.to_datetime(data[parent_col])
                        if index == 0:
                            eval_string = (
                                eval_string
                                + "("
                                + (date_dict[condition].format(column_name=parent_col, value="{}"))
                                + ")"
                            )
                        else:
                            eval_string = (
                                eval_string
                                + " & ("
                                + (date_dict[condition].format(column_name=parent_col, value="{}"))
                                + ")"
                            )
                        if index == len(condition_list) - 1:
                            eval_string = eval_string + "]"
                        else:
                            continue
                        for i in range(len(child_data)):
                            value_string = ""
                            for ind, col_name in enumerate(condition_col_list):
                                req_value = child_data[col_name][i]
                                if ind == 0:
                                    value_string = value_string + "'" + str(req_value) + "'"
                                else:
                                    value_string = value_string + ", " + "'" + str(req_value) + "'"
                            req_string = (eval_string + ".")[:-1]
                            req_string = literal_eval("req_string.format(" + value_string + ")")
                            parent = pd.eval(req_string)
                            parent.reset_index(drop=True, inplace=True)
                            if field_type_parent[target_col] == "object":
                                child_data.loc[i, new_col_name] = parent[target_col][0] + str(basic_op_val)

                            elif field_type_parent[target_col] in ["int64", "float64"]:
                                if basic_op == "Add":
                                    child_data.loc[i, new_col_name] = parent[target_col][0] + float(
                                        basic_op_val
                                    )
                                elif basic_op == "Subtract":
                                    child_data.loc[i, new_col_name] = parent[target_col][0] - float(
                                        basic_op_val
                                    )
                                elif basic_op == "Multiply":
                                    child_data.loc[i, new_col_name] = parent[target_col][0] * float(
                                        basic_op_val
                                    )
                                elif basic_op == "Divide":
                                    child_data.loc[i, new_col_name] = parent[target_col][0] / float(
                                        basic_op_val
                                    )
                                else:
                                    child_data.loc[i, new_col_name] = parent[target_col][0]

                            elif field_type_parent[target_col] in ["datetime64[ns]"]:
                                if basic_op == "Add":
                                    try:
                                        child_data.loc[i, new_col_name] = (
                                            pd.to_datetime(parent[target_col][0])
                                            + pd.to_timedelta(basic_op_val, unit="D")
                                        ).dt.strftime("%Y-%m-%d")
                                    except Exception as e:
                                        logging.warning(f"Following exception occured - {e}")
                                        child_data.loc[i, new_col_name] = parent[target_col][0]

                                elif basic_op == "Subtract":
                                    try:
                                        pd.to_datetime(basic_op_val)
                                    except Exception as e:
                                        logging.warning(f"Following exception occured - {e}")
                                        child_data.loc[i, new_col_name] = (
                                            pd.to_datetime(parent[target_col][0])
                                            - pd.to_timedelta(basic_op_val, unit="D")
                                        ).dt.strftime("%Y-%m-%d")
                                    else:
                                        child_data.loc[i, new_col_name] = (
                                            pd.to_datetime(parent[target_col][0])
                                            - pd.to_datetime(basic_op_val)
                                        ).dt.strftime("%Y-%m-%d")
                                else:
                                    child_data.loc[i, new_col_name] = pd.to_datetime(
                                        parent[target_col][0]
                                    )

                            else:
                                child_data.loc[i, new_col_name] = (
                                    str(parent[target_col][0]) + " " + str(basic_op_val)
                                )

                    else:
                        child_data.loc[i, new_col_name] = parent[target_col][0]
        return child_data

    def where(self, data, condition_list, col_dtypes=None):
        string_dict = DataTransformation.string_dict
        num_dict = DataTransformation.num_dict
        date_dict = DataTransformation.date_dict
        field_type = data.dtypes.apply(lambda x: x.name).to_dict()
        if col_dtypes is not None:
            field_type = col_dtypes
        eval_string = ""
        date_special_columns = []
        for ind, cond in enumerate(condition_list):
            column = cond["column_name"]
            condition = cond["condition"]
            value = cond["input_value"]
            if field_type[column] in ["object"]:
                eval_string = (
                    eval_string + "(" + string_dict[condition].format(column_name=column, value=value) + ")"
                )
                if ind < (len(condition_list) - 1):
                    eval_string = eval_string + " & "
            elif field_type[column] in ["datetime64[ns]"]:
                if condition in date_dict.keys():
                    date_special_string = (
                        "(" + (date_dict[condition].format(column_name=column, value=value)) + ")"
                    )
                    if ind < (len(condition_list) - 1):
                        if condition.endswith("AND"):
                            date_special_string = date_special_string + " & "
                        else:
                            date_special_string = date_special_string + " | "
                    date_special_columns.append((column, date_special_string))
                elif bool(date_special_columns) & (column in (i[0] for i in date_special_columns)):
                    date_special_string = (
                        "(" + (string_dict[condition].format(column_name=column, value=value)) + ")"
                    )
                    date_special_columns.append((column, date_special_string))
                else:
                    eval_string = (
                        eval_string
                        + "("
                        + (string_dict[condition].format(column_name=column, value=value))
                        + ")"
                    )
                    if ind < (len(condition_list) - 1):
                        eval_string = eval_string + " & "
            elif field_type[column] in ["int64", "float64"]:
                if col_dtypes is not None:
                    if field_type[column] == "float64":
                        data[column] = data[column].astype(float)
                    elif field_type[column] == "int64":
                        data[column] = data[column].astype(int)
                if condition in ["IN", "NOT IN"]:
                    a = []
                    for item in value:
                        a.append(float(item))
                    value = a
                else:
                    value = float(value)
                eval_string = (
                    eval_string + "(" + (num_dict[condition].format(column_name=column, value=value)) + ")"
                )
                if ind < (len(condition_list) - 1):
                    eval_string = eval_string + " & "
            elif field_type[column] in ["bool"]:
                value = int(literal_eval(value))
                eval_string = (
                    eval_string + "(" + (num_dict[condition].format(column_name=column, value=value)) + ")"
                )
                if ind < (len(condition_list) - 1):
                    eval_string = eval_string + " & "
            else:
                pass

        if len(date_special_columns) > 1:
            uniq_cols = {i[0] for i in date_special_columns}
            for col_name in uniq_cols:
                col_date_str = "("
                for col, d_string in date_special_columns:
                    if col == col_name:
                        col_date_str = col_date_str + d_string
                col_date_str = col_date_str + ")"
                if eval_string.endswith(" & "):
                    eval_string = eval_string + col_date_str
                elif len(eval_string) > 0:
                    eval_string = eval_string + " & " + col_date_str
                else:
                    eval_string = eval_string + col_date_str

        elif len(date_special_columns) == 1:
            col, dt_string = date_special_columns[0]
            if dt_string.find(" & ") != -1:
                dt_string = dt_string.replace(" & ", "")
            elif dt_string.find(" | ") != -1:
                dt_string = dt_string.replace(" | ", "")
            if eval_string.endswith(" & "):
                eval_string = eval_string + dt_string
            elif len(eval_string) > 0:
                eval_string = eval_string + " & " + dt_string
            else:
                eval_string = eval_string + dt_string
        filter_ind = pd.eval(eval_string)
        filtered_data = data[filter_ind.fillna(False)]
        return filtered_data

    def group(self, data, g_cols, agg_func):
        """
        group by df's on the basis of some agg func
        """
        grouped_data = data.groupby(g_cols, dropna=False).agg(agg_func)
        grouped_data.reset_index(inplace=True)
        return grouped_data

    def cond_col(self, data, new_col_name, condition_list, add_type, field_model_type):
        """
        Adds a new column with values based on some conditional
        logic on existing column
        data: dataframe
        new_col_name: name of new column
        condition_list: list of all the condition dicts-
        [{"column", "condition", "conditional_value", "rep_value"}]
        """
        string_dict = DataTransformation.string_dict
        num_dict = DataTransformation.num_dict
        data[new_col_name] = np.nan

        field_type = data.dtypes.apply(lambda x: x.name).to_dict()
        for con in condition_list:
            column = con["column_name"]
            condition = con["condition"]
            value = con["condition_value"]
            repr_value = con["repr_value"]["repr_value"]
            if field_type[column] in ["object"]:
                mask = pd.eval(string_dict[condition].format(column_name=column, value=value))
            elif field_type[column] in ["datetime64[ns]"]:
                mask = pd.eval(string_dict[condition].format(column_name=column, value=value))
            elif field_type[column] in ["int64", "float64"]:
                value = float(value)
                mask = pd.eval(num_dict[condition].format(column_name=column, value=value))
            elif field_type[column] in ["bool"]:
                value = int(literal_eval(value))
                mask = pd.eval(num_dict[condition].format(column_name=column, value=value))
            if add_type == "static_add":
                data.loc[mask, new_col_name] = repr_value
            else:
                data.loc[mask, new_col_name] = data.loc[mask, repr_value]
        if field_model_type == "IntegerField":
            data[new_col_name] = data[new_col_name].astype(float).astype(int)
        elif field_model_type == "BigIntegerField":
            data[new_col_name] = data[new_col_name].astype(float).astype(int)
        elif field_model_type == "FloatField":
            data = data.astype({new_col_name: float})
        elif field_model_type == "DateField":
            data[new_col_name] = pd.to_datetime(data[new_col_name], errors="coerce")
        else:
            pass
        return data

    def sort(self, data, columns, ascend):
        """
        sort the data according to the column/s of the data
        """
        return data.sort_values(columns, ascending=ascend)

    def pivot(self, data, index, columns, values=[]):
        if len(values) > 0:
            output_data = pd.pivot_table(
                data, values=values, index=index, columns=columns, aggfunc=np.sum, fill_value=0
            )
            output_data.columns = output_data.columns.get_level_values(1)
        else:
            output_data = pd.pivot_table(data, index=index, columns=columns, aggfunc=np.sum, fill_value=0)
            output_data.columns = output_data.columns.get_level_values(1)
        output_data.reset_index(inplace=True)
        return output_data

    def transpose(self, data, index):
        data.set_index(index, inplace=True)
        output_data = data.transpose()
        return output_data

    def melt(self, data, id_vars, value_vars=[], var_name="variable", value_name="value"):
        if len(value_vars) > 0:
            output_data = data.melt(
                id_vars=id_vars, value_vars=value_vars, var_name=var_name, value_name=value_name
            )
        else:
            output_data = data.melt(id_vars=id_vars, var_name=var_name, value_name=value_name)

        return output_data

    def rename_column(self, data, rename_dict, drop_column):
        data.drop(columns=drop_column, inplace=True)
        data.rename(columns=rename_dict, inplace=True)
        return data

    def find_replace(self, data, fdict):
        find = fdict["find"]
        replace = fdict["replace"]
        column = fdict["columnName"]
        if fdict.get("replacecolumnName"):
            replaceColumn = fdict["replacecolumnName"]
        else:
            replaceColumn = column
        if data.dtypes[column] == np.float64:
            find = float(find)
        elif data.dtypes[column] == np.int64:
            find = int(float(find))
        if data.dtypes[replaceColumn] == np.float64:
            replace = float(replace)
        elif data.dtypes[replaceColumn] == np.int64:
            replace = int(float(replace))
        if not fdict["find"]:
            find = "NULL"
        if not fdict["replace"]:
            replace = None
        data = standardised_functions.find_and_replace(
            data, column, replaceColumn, find, replace, fdict["find_case"], False
        )
        return data


def merge_and_join(data_list, config_dict, request_user=""):
    trnsf = DataTransformation()
    option = config_dict["inputs"]["option"]

    if option == "concatenate":
        output_data = trnsf.concat(data_list)

    elif option == "append":
        output_data = trnsf.append(data_list)

    elif option == "join":
        col_show = config_dict["inputs"]["Col_show"]
        if config_dict["inputs"].get("Col_Rename"):
            col_rename = config_dict["inputs"]["Col_Rename"]
        else:
            col_rename = {}
        col_display = config_dict["inputs"]["col_display_list"]
        if config_dict.get("newly_created"):
            newly_created = config_dict["newly_created"]
            table_name = config_dict["inputs"]["table_name"]
        else:
            newly_created = ""
            table_name = ""
        j_type = config_dict["inputs"]["join_config"]["join_type"]
        join_on = list(config_dict["inputs"]["join_config"]["on"].values())
        if newly_created:
            output_data = trnsf.join_eq(
                list1=col_show,
                col_rename=col_rename,
                col_display=col_display,
                join_data=data_list,
                join_type=j_type,
                join_on=join_on,
                newly_created=newly_created,
                request_user=request_user,
                table_name=table_name,
            )
        else:
            output_data = trnsf.join(
                list1=col_show,
                col_rename=col_rename,
                col_display=col_display,
                join_data=data_list,
                join_type=j_type,
                join_on=join_on,
            )

    elif option == "cond_merge":
        data_mapper = config_dict["inputs"]["data_mapper"]
        condition_dict = config_dict["inputs"]["condition_list"]
        parent_data = config_dict["inputs"]["parent_data"]
        child_data = config_dict["inputs"]["child_data"]
        output_data = trnsf.conditional_merge(data_mapper, condition_dict, parent_data, child_data)

    return output_data


def groupby_and_sortby(new_data, config_dict):
    trnsf = DataTransformation()
    option = config_dict["inputs"]["option"]
    option_config = config_dict["inputs"]["option_config"]

    if option == "where":
        condition_list = option_config["condition"]
        new_data = trnsf.where(new_data, condition_list)

    elif option == "group":
        grp_cols = option_config["group_by"]
        agg_func = option_config["aggregate_func"]
        new_data = trnsf.group(new_data, grp_cols, agg_func)

    elif option == "addCondColumn":
        column_name = option_config["condition"]["new_column_name"]
        condition_list = option_config["condition"]["condition"]
        add_type = option_config["condition"]["add_type"]
        field_model_type = ""
        if "field_type" in option_config["condition"].keys():
            if option_config["condition"]["field_type"]:
                field_model_type = option_config["condition"]["field_type"]
            else:
                field_model_type = "CharField"
        else:
            field_model_type = "CharField"

        new_data = trnsf.cond_col(
            data=new_data,
            new_col_name=column_name,
            condition_list=condition_list,
            add_type=add_type,
            field_model_type=field_model_type,
        )

    if bool(config_dict.get("sort")):
        cols_by = list(config_dict["sort"].keys())
        ascending = list(config_dict["sort"].values())
        ascending = [literal_eval(i) for i in ascending]
        new_data = trnsf.sort(new_data, columns=cols_by, ascend=ascending)
    return new_data


def pivot_and_transpose(data, config_dict):
    trnsf = DataTransformation()
    option = config_dict["inputs"]["option"]
    option_config = config_dict["inputs"]["option_config"]

    if option == "pivot":
        index = option_config["index"]
        columns = option_config["columns"]
        values = option_config["values"]
        output_data = trnsf.pivot(data, index, columns, values)

    elif option == "transpose":
        index = option_config["index"]
        output_data = trnsf.transpose(data, index)

    elif option == "melt":
        id_vars = option_config["index"]
        value_vars = option_config["columns"]
        var_name = option_config["variable_column_name"]
        value_name = option_config["value_column_name"]
        output_data = trnsf.melt(data, id_vars, value_vars, var_name, value_name)

    return output_data
