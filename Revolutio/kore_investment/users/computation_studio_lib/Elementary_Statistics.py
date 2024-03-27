from ast import literal_eval

import numpy as np
import pandas as pd
import scipy.stats as stats


class Summary_stats:
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
    }
    num_dict = {
        "Equal to": "data['{column_name}'] == {value}",
        "Not Equal to": "data['{column_name}'] != {value}",
        "Greater than": "data['{column_name}'] > {value}",
        "Smaller than": "data['{column_name}'] < {value}",
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
    }

    def where(self, data, condition_list):
        string_dict = Summary_stats.string_dict
        num_dict = Summary_stats.num_dict
        date_dict = Summary_stats.date_dict
        field_type = data.dtypes.apply(lambda x: x.name).to_dict()

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
        filtered_data = data[filter_ind]
        return filtered_data

    def sum_fn(self, dataframe, grpby_col_name, value_col_name):
        sub = dataframe.groupby(grpby_col_name)
        return sub[value_col_name].sum().reset_index()

    def count_fn(self, dataframe, grpby_col_name, value_col_name):
        sub = dataframe.groupby(grpby_col_name)
        return sub[value_col_name].count().reset_index()

    def average_fn(self, dataframe, grpby_col_name, value_col_name):
        sub = dataframe.groupby(grpby_col_name)
        return sub[value_col_name].mean().reset_index()

    def sumproduct_fn(self, dataframe, grpby_col_name, sum_product_col_name, new_column_name="Sum Product"):
        if new_column_name == "":
            new_column_name = "Sum Product"
        eval_string = "(dataframe.assign(col="
        for i in range(len(sum_product_col_name)):
            if i == range(len(sum_product_col_name))[-1]:
                eval_string = (
                    eval_string
                    + f"dataframe['{sum_product_col_name[i]}']).groupby(grpby_col_name, as_index=False).col.sum())"
                )
            else:
                eval_string = eval_string + f"dataframe['{sum_product_col_name[i]}'] * "
        output_df = pd.eval(eval_string)
        output_df = output_df.rename(columns={"col": new_column_name})
        return output_df

    def min_fn(self, dataframe, grpby_col_name, value_col_name):
        sub = dataframe.groupby(grpby_col_name)
        return sub[value_col_name].min().reset_index()

    def max_fn(self, dataframe, grpby_col_name, value_col_name):
        sub = dataframe.groupby(grpby_col_name)
        return sub[value_col_name].max().reset_index()

    def stddev_fn(self, dataframe, grpby_col_name, value_col_name):
        sub = dataframe.groupby(grpby_col_name)
        return sub[value_col_name].std(ddof=0).reset_index()

    def variance_fn(self, dataframe, grpby_col_name, value_col_name):
        sub = dataframe.groupby(grpby_col_name)
        return sub[value_col_name].var(ddof=0).reset_index()

    def skewness_fn(self, dataframe, grpby_col_name, value_col_name):
        sub = dataframe.groupby(grpby_col_name)
        return sub[value_col_name].skew().reset_index()

    def kurtosis_fn(self, dataframe, grpby_col_name, value_col_name):
        sub = dataframe.groupby(grpby_col_name).apply(pd.DataFrame.kurt)
        return sub[value_col_name]

    def median_fn(self, dataframe, grpby_col_name, value_col_name):
        sub = dataframe.groupby(grpby_col_name)
        return sub[value_col_name].median().reset_index()

    def mode_fn(self, dataframe, grpby_col_name, value_col_name):
        sub = dataframe.groupby(grpby_col_name)
        sub1 = sub[value_col_name].apply(stats.mode)
        sub1 = pd.DataFrame(sub1)
        sub1["Mode"] = np.NAN
        sub1["Repetition"] = np.NAN
        for i in range(len(sub1)):
            sub1["Mode"].iloc[i] = float(sub1[value_col_name][i].mode)
            sub1["Repetition"].iloc[i] = float(sub1[value_col_name][i].count)
        sub1.drop(columns=[value_col_name], inplace=True)
        return sub1

    def count_distinct_fn(self, dataframe, grpby_col_name, value_col_name):
        sub = dataframe.groupby(grpby_col_name)
        return sub[value_col_name].nunique().reset_index()

    def weighted_average_fn(
        self, dataframe, grpby_col_name, value_col_name, weights, new_column_name="Weighted Average"
    ):
        output_df = dataframe.groupby(grpby_col_name)
        # Performing pseudo Aggregation
        output_df = output_df[value_col_name].min().reset_index()
        weighted_average = dataframe.groupby(grpby_col_name).apply(
            lambda x: ((x[value_col_name] * x[weights]).sum()) / (x[weights].sum())
        )
        weighted_average.index = output_df.index
        output_df[value_col_name] = weighted_average
        output_df.rename(columns={value_col_name: new_column_name}, inplace=True)
        return output_df

    def top_n_fn(self, dataframe, grpby_col_name, value_col_name, top_n_rows):
        sub = dataframe.groupby(grpby_col_name)
        return sub[value_col_name].nlargest(n=top_n_rows)

    def bottom_n_fn(self, dataframe, grpby_col_name, value_col_name, bottom_n_rows):
        sub = dataframe.groupby(grpby_col_name)
        return sub[value_col_name].nsmallest(n=bottom_n_rows)

    def quantile_fn(self, dataframe, grpby_col_name, value_col_name, quantile_req):
        sub = dataframe.groupby(grpby_col_name)
        if quantile_req in [0.25, 0.5, 0.75]:
            sub_1 = sub[value_col_name].quantile(quantile_req).reset_index().to_dict()
            columns_list = []
            for col_name in grpby_col_name:
                columns_list.append(col_name)
            columns_list = columns_list + ["Quantile_value", "Values Greater than", "Values less"]
            sub_df = pd.DataFrame(columns=columns_list)
            for i in list(sub_1.values())[0]:
                eval_string = ""
                for j in range(len(grpby_col_name)):
                    if j == range(len(grpby_col_name))[-1]:
                        eval_string = (
                            eval_string
                            + f"(dataframe['{grpby_col_name[j]}'] == sub_1['{grpby_col_name[j]}'][i])"
                        )
                    else:
                        eval_string = (
                            eval_string
                            + f"(dataframe['{grpby_col_name[j]}'] == sub_1['{grpby_col_name[j]}'][i]) & "
                        )
                sub_2 = (dataframe[pd.eval(eval_string)][value_col_name] < sub_1[value_col_name][i]).sum()
                sub_3 = (dataframe[pd.eval(eval_string)][value_col_name] > sub_1[value_col_name][i]).sum()
                append_dict = {}
                for k in range(len(grpby_col_name)):
                    append_dict[grpby_col_name[k]] = sub_1[grpby_col_name[k]][i]
                append_dict["Quantile_value"] = sub_1[value_col_name][i]
                append_dict["Values Greater than"] = sub_3
                append_dict["Values less"] = sub_2
                append_dict_df = pd.DataFrame.from_dict([append_dict])
                sub_df = pd.concat([sub_df, append_dict_df], ignore_index=True)
            return sub_df

    def percentile_fn(self, dataframe, grpby_col_name, value_col_name, percentile_val):
        sub = dataframe.groupby(grpby_col_name)
        if percentile_val in np.arange(1, 100):
            sub_1 = sub[value_col_name].quantile(percentile_val / 100).reset_index().to_dict()
            columns_list = []
            for col_name in grpby_col_name:
                columns_list.append(col_name)
            columns_list = columns_list + ["Percentile_value", "Values Greater than", "Values less"]
            sub_df = pd.DataFrame(columns=columns_list)
            for i in list(sub_1.values())[0]:
                eval_string = ""
                for j in range(len(grpby_col_name)):
                    if j == range(len(grpby_col_name))[-1]:
                        eval_string = (
                            eval_string
                            + f"(dataframe['{grpby_col_name[j]}'] == sub_1['{grpby_col_name[j]}'][i])"
                        )
                    else:
                        eval_string = (
                            eval_string
                            + f"(dataframe['{grpby_col_name[j]}'] == sub_1['{grpby_col_name[j]}'][i]) & "
                        )
                sub_2 = (dataframe[pd.eval(eval_string)][value_col_name] < sub_1[value_col_name][i]).sum()
                sub_3 = (dataframe[pd.eval(eval_string)][value_col_name] > sub_1[value_col_name][i]).sum()
                append_dict = {}
                for k in range(len(grpby_col_name)):
                    append_dict[grpby_col_name[k]] = sub_1[grpby_col_name[k]][i]
                append_dict["Percentile_value"] = sub_1[value_col_name][i]
                append_dict["Values Greater than"] = sub_3
                append_dict["Values less"] = sub_2
                append_dict_df = pd.DataFrame.from_dict([append_dict])
                sub_df = pd.concat([sub_df, append_dict_df], ignore_index=True)
            return sub_df

    def sumif_fn(self, dataframe, grpby_col_name, value_col_name, condition_list):
        filtered_data = self.where(dataframe, condition_list)
        sub = filtered_data.groupby(grpby_col_name)
        return sub[value_col_name].sum().reset_index()

    def countif_fn(self, dataframe, grpby_col_name, value_col_name, condition_list):
        filtered_data = self.where(dataframe, condition_list)
        sub = filtered_data.groupby(grpby_col_name)
        return sub[value_col_name].count().reset_index()

    def averageif_fn(self, dataframe, grpby_col_name, value_col_name, condition_list):
        filtered_data = self.where(dataframe, condition_list)
        sub = filtered_data.groupby(grpby_col_name)
        return sub[value_col_name].mean()

    def productif_fn(self, dataframe, grpby_col_name, value_col_name, condition_list):
        filtered_data = self.where(dataframe, condition_list)
        sub = filtered_data.groupby(grpby_col_name)
        return sub[value_col_name].prod().reset_index()

    def sumproductif_fn(
        self, dataframe, grpby_col_name, sum_product_col_name, condition_list, new_column_name
    ):
        filtered_data = self.where(dataframe, condition_list)
        if new_column_name == "":
            new_column_name = "Sum Product"
        eval_string = "(filtered_data.assign(col="
        for i in range(len(sum_product_col_name)):
            if i == range(len(sum_product_col_name))[-1]:
                eval_string = (
                    eval_string
                    + f"filtered_data['{sum_product_col_name[i]}']).groupby(grpby_col_name, as_index=False).col.sum())"
                )
            else:
                eval_string = eval_string + f"filtered_data['{sum_product_col_name[i]}'] * "
        output_df = pd.eval(eval_string)
        output_df = output_df.rename(columns={"col": new_column_name})
        del filtered_data
        return output_df


def Compute_Elementary_Statistics(dataframe, config_dict):
    stats_func = Summary_stats()
    grpby_col_name = config_dict["inputs"]["Groupby_column"]
    agg_config = config_dict["inputs"]["agg_config"]

    output_list = []
    for agg in agg_config:
        aggregate = agg["Aggregate"]
        value_col_name = agg["Value_column"]
        sum_product_col_name = agg["Sum_product_column"]
        new_column_name = agg["new_column_name"]
        weights = agg["Weights"]

        if new_column_name == "":
            new_column_name = value_col_name

        if aggregate == "Sum":
            output_data = stats_func.sum_fn(dataframe, grpby_col_name, value_col_name)
            output_data = output_data.reset_index(drop=True).rename(columns={value_col_name: new_column_name})
            output_list.append(output_data)

        elif aggregate == "Count":
            output_data = stats_func.count_fn(dataframe, grpby_col_name, value_col_name)
            output_data = output_data.reset_index(drop=True).rename(columns={value_col_name: new_column_name})
            output_list.append(output_data)

        elif aggregate == "Average":
            output_data = stats_func.average_fn(dataframe, grpby_col_name, value_col_name)
            output_data = output_data.reset_index(drop=True).rename(columns={value_col_name: new_column_name})
            output_list.append(output_data)

        elif aggregate == "Sum Product":
            output_data = stats_func.sumproduct_fn(
                dataframe, grpby_col_name, sum_product_col_name, new_column_name
            )
            output_data.reset_index(inplace=True, drop=True)
            output_list.append(output_data)

        elif aggregate == "Min":
            output_data = stats_func.min_fn(dataframe, grpby_col_name, value_col_name)
            output_data = output_data.reset_index(drop=True).rename(columns={value_col_name: new_column_name})
            output_list.append(output_data)

        elif aggregate == "Max":
            output_data = stats_func.max_fn(dataframe, grpby_col_name, value_col_name)
            output_data = output_data.reset_index(drop=True).rename(columns={value_col_name: new_column_name})
            output_list.append(output_data)

        elif aggregate == "Standard Deviation":
            output_data = stats_func.stddev_fn(dataframe, grpby_col_name, value_col_name)
            output_data = output_data.reset_index(drop=True).rename(columns={value_col_name: new_column_name})
            output_list.append(output_data)

        elif aggregate == "Variance":
            output_data = stats_func.variance_fn(dataframe, grpby_col_name, value_col_name)
            output_data = output_data.reset_index(drop=True).rename(columns={value_col_name: new_column_name})
            output_list.append(output_data)

        elif aggregate == "Skewness":
            output_data = stats_func.skewness_fn(dataframe, grpby_col_name, value_col_name)
            output_data = output_data.reset_index(drop=True).rename(columns={value_col_name: new_column_name})
            output_list.append(output_data)

        elif aggregate == "Kurtosis":
            output_data = stats_func.kurtosis_fn(dataframe, grpby_col_name, value_col_name)
            output_data = output_data.reset_index().rename(columns={value_col_name: new_column_name})
            output_list.append(output_data)

        elif aggregate == "Median":
            output_data = stats_func.median_fn(dataframe, grpby_col_name, value_col_name)
            output_data = output_data.reset_index(drop=True).rename(columns={value_col_name: new_column_name})
            output_list.append(output_data)

        elif aggregate == "Mode":
            output_data = stats_func.mode_fn(dataframe, grpby_col_name, value_col_name)
            output_data = output_data.reset_index(drop=True).rename(columns={value_col_name: new_column_name})
            output_list.append(output_data)

        elif aggregate == "Count Distinct":
            output_data = stats_func.count_distinct_fn(dataframe, grpby_col_name, value_col_name)
            output_data = output_data.reset_index(drop=True).rename(columns={value_col_name: new_column_name})
            output_list.append(output_data)

        elif aggregate == "Weighted Average":
            output_data = stats_func.weighted_average_fn(
                dataframe, grpby_col_name, value_col_name, weights, new_column_name
            )
            output_list.append(output_data)

        elif aggregate == "Top":
            top_n_rows = int(agg["Conditional"]["Top_n_rows"])
            output_data = stats_func.top_n_fn(dataframe, grpby_col_name, value_col_name, top_n_rows)
            output_data.index = output_data.index.droplevel(-1)
            output_data = output_data.reset_index().rename(columns={value_col_name: new_column_name})
            output_list.append(output_data)

        elif aggregate == "Bottom":
            bottom_n_rows = int(agg["Conditional"]["Bottom_n_rows"])
            output_data = stats_func.bottom_n_fn(dataframe, grpby_col_name, value_col_name, bottom_n_rows)
            output_data.index = output_data.index.droplevel(-1)
            output_data = output_data.reset_index().rename(columns={value_col_name: new_column_name})
            output_list.append(output_data)

        elif aggregate == "Quantile":
            quantile_val = agg["Conditional"]["Quantile"]
            if quantile_val == "I":
                quantile = 0.25
            elif quantile_val == "II":
                quantile = 0.5
            elif quantile_val == "III":
                quantile = 0.75
            output_data = stats_func.quantile_fn(dataframe, grpby_col_name, value_col_name, quantile)
            output_data = output_data.reset_index(drop=True).rename(columns={value_col_name: new_column_name})
            output_list.append(output_data)

        elif aggregate == "Percentile":
            percentile_val = int(agg["Conditional"]["Percentile"])
            output_data = stats_func.percentile_fn(dataframe, grpby_col_name, value_col_name, percentile_val)
            output_data = output_data.reset_index(drop=True).rename(columns={value_col_name: new_column_name})
            output_list.append(output_data)

        elif aggregate == "Sumif":
            condition_list = agg["Conditional"]["If_condition"]
            output_data = stats_func.sumif_fn(dataframe, grpby_col_name, value_col_name, condition_list)
            output_data = output_data.reset_index(drop=True).rename(columns={value_col_name: new_column_name})
            output_list.append(output_data)

        elif aggregate == "Countif":
            condition_list = agg["Conditional"]["If_condition"]
            output_data = stats_func.countif_fn(dataframe, grpby_col_name, value_col_name, condition_list)
            output_data = output_data.reset_index(drop=True).rename(columns={value_col_name: new_column_name})
            output_list.append(output_data)

        elif aggregate == "Averageif":
            condition_list = agg["Conditional"]["If_condition"]
            output_data = stats_func.averageif_fn(dataframe, grpby_col_name, value_col_name, condition_list)
            output_data = output_data.reset_index().rename(columns={value_col_name: new_column_name})
            output_list.append(output_data)

        elif aggregate == "Productif":
            condition_list = agg["Conditional"]["If_condition"]
            output_data = stats_func.productif_fn(dataframe, grpby_col_name, value_col_name, condition_list)
            output_data = output_data.reset_index(drop=True).rename(columns={value_col_name: new_column_name})
            output_list.append(output_data)

        elif aggregate == "Sumproductif":
            condition_list = agg["Conditional"]["If_condition"]
            new_column_name = agg["new_column_name"]
            output_data = stats_func.sumproductif_fn(
                dataframe, grpby_col_name, sum_product_col_name, condition_list, new_column_name
            )
            output_data.reset_index(inplace=True, drop=True)
            output_list.append(output_data)

    final_data = output_list[0]
    if len(output_list) > 1:
        for data in output_list[1:]:
            if not data.empty:
                final_data = final_data.merge(data, on=grpby_col_name, how="outer")

    return final_data
