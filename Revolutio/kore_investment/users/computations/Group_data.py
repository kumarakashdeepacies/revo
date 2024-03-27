from currency_symbols import CurrencySymbols
import pandas as pd
from scipy.stats import kurtosis


def groupData(
    data,
    levels,
    disp_cols,
    operation,
    modelName,
    formatter_config_checker,
    formatter_config,
    model_name,
    json_model_name,
):
    """
    For a given JSON object containing the data, levels, display_columns
    Returns the Tree based grouped data JSON
    """
    operation2 = {}
    field_datatype_list_json = {}
    field_datatype_list = {
        field.verbose_name: field.get_internal_type() for field in modelName.concrete_fields
    }
    field_verbose_name_list = {field.name: field.verbose_name for field in modelName.concrete_fields}
    if json_model_name != "":
        field_datatype_list_json = {
            field.verbose_name: field.get_internal_type() for field in json_model_name.concrete_fields
        }
    for j in range(len(operation)):
        if operation[j].lower() == "sum":
            operation2.update({disp_cols[j]: "sum"})
        elif operation[j].lower() == "count":
            operation2.update({disp_cols[j]: "count"})
        elif operation[j].lower() == "count distinct":
            operation2.update({disp_cols[j]: "nunique"})
        elif operation[j].lower() == "average":
            operation2.update({disp_cols[j]: "mean"})
        elif operation[j].lower() == "skewness":
            operation2.update({disp_cols[j]: "skew"})
        elif operation[j].lower() == "median":
            operation2.update({disp_cols[j]: "median"})
        elif operation[j].lower() == "variance":
            operation2.update({disp_cols[j]: "var"})
        elif operation[j].lower() == "standard deviation":
            operation2.update({disp_cols[j]: "std"})
        elif operation[j].lower() == "maximum":
            operation2.update({disp_cols[j]: "max"})
        elif operation[j].lower() == "minimum":
            operation2.update({disp_cols[j]: "min"})
        elif operation[j].lower() == "earliest":
            operation2.update({disp_cols[j]: "min"})
        elif operation[j].lower() == "latest":
            operation2.update({disp_cols[j]: "max"})
        elif operation[j].lower() == "kurtosis":
            operation2.update({disp_cols[j]: lambda x: kurtosis(x)})
        elif operation[j].lower() == "percentage of total":
            operation2.update({disp_cols[j]: lambda x: sum(x) / data[[disp_cols[j]]].sum()})
        elif operation[j].lower() == "first":
            operation2.update({disp_cols[j]: lambda x: x.iloc[0]})
        elif operation[j].lower() == "value":
            operation2.update({disp_cols[j]: lambda x: "" if len(x) > 1 else x.iloc[0]})
        elif operation[j].lower() == "last":
            operation2.update({disp_cols[j]: lambda x: x.iloc[-1]})
        elif operation[j].lower() == "earliest":
            operation2.update({disp_cols[j]: "min"})
        elif operation[j].lower() == "latest":
            operation2.update({disp_cols[j]: "max"})
        else:
            continue
    if disp_cols == ["all"]:
        disp_cols = list(data.select_dtypes("number").columns)
    else:
        disp_cols = disp_cols
    parent_list = []
    level_no = 1
    main_list = disp_cols.copy()
    for i in range(level_no):
        if levels[i] not in main_list:
            main_list.append(levels[i])
    table_l1 = (
        data.groupby([levels[i] for i in range(level_no)])[disp_cols].agg(operation2).fillna(0).round(4)
    )
    for l1 in data[levels[level_no - 1]].dropna().unique():
        if levels[0] in field_datatype_list:
            if field_datatype_list[levels[0]] == "DateField" and l1 != "-":
                var_l1 = {levels[0]: pd.to_datetime(l1).strftime("%Y-%m-%d")}
            elif field_datatype_list[levels[0]] == "DateTimeField" and l1 != "-":
                var_l1 = {levels[0]: pd.to_datetime(l1).strftime("%Y-%m-%d %H:%M")}
            else:
                var_l1 = {levels[0]: l1}
            for s in range(len(levels)):
                if s > 0:
                    var_l1.update({levels[s]: ""})
            value_l1 = table_l1[table_l1.index == l1]
            for i in range(len(disp_cols)):
                if disp_cols[i] in field_datatype_list:
                    if field_datatype_list[disp_cols[i]] not in [
                        "IntegerField",
                        "BigIntegerField",
                        "FloatField",
                        "AutoField",
                    ]:
                        var_l1.update({disp_cols[i]: str(value_l1[disp_cols[i]].values[0])})
                    else:
                        var_l1.update({disp_cols[i]: float(value_l1[disp_cols[i]])})
                else:
                    if field_datatype_list_json[disp_cols[i]] not in [
                        "IntegerField",
                        "BigIntegerField",
                        "FloatField",
                        "AutoField",
                    ]:
                        var_l1.update({disp_cols[i]: str(value_l1[disp_cols[i]].values[0])})
                    else:
                        var_l1.update({disp_cols[i]: float(value_l1[disp_cols[i]])})
        else:
            if field_datatype_list_json[levels[0]] == "DateField" and l1 != "-":
                var_l1 = {levels[0]: pd.to_datetime(l1).strftime("%Y-%m-%d")}
            elif field_datatype_list_json[levels[0]] == "DateTimeField" and l1 != "-":
                var_l1 = {levels[0]: pd.to_datetime(l1).strftime("%Y-%m-%d %H:%M")}
            else:
                var_l1 = {levels[0]: l1}
            for s in range(len(levels)):
                if s > 0:
                    var_l1.update({levels[s]: ""})
            value_l1 = table_l1[table_l1.index == l1]
            for i in range(len(disp_cols)):
                if disp_cols[i] in field_datatype_list:
                    if field_datatype_list[disp_cols[i]] not in [
                        "IntegerField",
                        "BigIntegerField",
                        "FloatField",
                        "AutoField",
                    ]:
                        var_l1.update({disp_cols[i]: str(value_l1[disp_cols[i]].values[0])})
                    else:
                        var_l1.update({disp_cols[i]: float(value_l1[disp_cols[i]])})
                else:
                    if field_datatype_list_json[disp_cols[i]] not in [
                        "IntegerField",
                        "BigIntegerField",
                        "FloatField",
                        "AutoField",
                    ]:
                        var_l1.update({disp_cols[i]: str(value_l1[disp_cols[i]].values[0])})
                    else:
                        var_l1.update({disp_cols[i]: float(value_l1[disp_cols[i]])})
        # If level 2 exists create child elements for level 1
        if len(levels) >= 2:
            level_no = 2
            # create an empty list for child elements of l1
            child_l1 = []
            main_list = disp_cols.copy()
            for i in range(level_no):
                if levels[i] not in main_list:
                    main_list.append(levels[i])
            table_l2 = (
                data.groupby([levels[i] for i in range(level_no)])[disp_cols]
                .agg(operation2)
                .fillna(0)
                .round(4)
            )
            # find and create the child elements of l1
            for l2 in data[levels[level_no - 1]].dropna().unique():
                uniq_l2 = tuple([l1, l2])
                if uniq_l2 in table_l2.index:
                    uniq_l2 = tuple([l1, l2])
                    if levels[1] in field_datatype_list:
                        if field_datatype_list[levels[1]] == "DateField" and l2 != "-":
                            var_l2 = {levels[1]: pd.to_datetime(l2).strftime("%Y-%m-%d")}
                        elif field_datatype_list[levels[1]] == "DateTimeField" and l2 != "-":
                            var_l2 = {levels[1]: pd.to_datetime(l2).strftime("%Y-%m-%d %H:%M")}
                        else:
                            var_l2 = {levels[1]: l2}
                        for s in range(len(levels)):
                            if s > 1:
                                var_l2.update({levels[s]: ""})
                            elif s == 1:
                                pass
                            else:
                                var_l2.update({levels[s]: var_l1[levels[s]]})
                        value_l2 = table_l2.loc[uniq_l2[0], uniq_l2[1]]
                        for i in range(len(disp_cols)):
                            if disp_cols[i] in field_datatype_list:
                                if field_datatype_list[disp_cols[i]] not in [
                                    "IntegerField",
                                    "BigIntegerField",
                                    "FloatField",
                                    "AutoField",
                                ]:
                                    var_l2.update({disp_cols[i]: str(value_l2[disp_cols[i]])})
                                else:
                                    var_l2.update({disp_cols[i]: float(value_l2[disp_cols[i]])})
                            else:
                                if field_datatype_list_json[disp_cols[i]] not in [
                                    "IntegerField",
                                    "BigIntegerField",
                                    "FloatField",
                                    "AutoField",
                                ]:
                                    var_l2.update({disp_cols[i]: str(value_l2[disp_cols[i]])})
                                else:
                                    var_l2.update({disp_cols[i]: float(value_l2[disp_cols[i]])})
                    else:
                        if field_datatype_list_json[levels[1]] == "DateField" and l2 != "-":
                            var_l2 = {levels[1]: pd.to_datetime(l2).strftime("%Y-%m-%d")}
                        elif field_datatype_list_json[levels[1]] == "DateTimeField" and l2 != "-":
                            var_l2 = {levels[1]: pd.to_datetime(l2).strftime("%Y-%m-%d %H:%M")}
                        else:
                            var_l2 = {levels[1]: l2}
                        for s in range(len(levels)):
                            if s > 1:
                                var_l2.update({levels[s]: ""})
                            elif s == 1:
                                pass
                            else:
                                var_l2.update({levels[s]: var_l1[levels[s]]})
                        value_l2 = table_l2.loc[uniq_l2[0], uniq_l2[1]]
                        for i in range(len(disp_cols)):
                            if disp_cols[i] in field_datatype_list:
                                if field_datatype_list[disp_cols[i]] not in [
                                    "IntegerField",
                                    "BigIntegerField",
                                    "FloatField",
                                    "AutoField",
                                ]:
                                    var_l2.update({disp_cols[i]: str(value_l2[disp_cols[i]])})
                                else:
                                    var_l2.update({disp_cols[i]: float(value_l2[disp_cols[i]])})
                            else:
                                if field_datatype_list_json[disp_cols[i]] not in [
                                    "IntegerField",
                                    "BigIntegerField",
                                    "FloatField",
                                    "AutoField",
                                ]:
                                    var_l2.update({disp_cols[i]: str(value_l2[disp_cols[i]])})
                                else:
                                    var_l2.update({disp_cols[i]: float(value_l2[disp_cols[i]])})
                    # If level 3 exists create child elements for level 2
                    if len(levels) >= 3:
                        level_no = 3
                        # create an empty list for child elements of l2
                        child_l2 = []
                        main_list = disp_cols.copy()
                        for i in range(level_no):
                            if levels[i] not in main_list:
                                main_list.append(levels[i])
                        table_l3 = (
                            data.groupby([levels[i] for i in range(level_no)])[disp_cols]
                            .agg(operation2)
                            .fillna(0)
                            .round(4)
                        )
                        for l3 in data[levels[level_no - 1]].dropna().unique():
                            uniq_l3 = tuple([l1, l2, l3])
                            if uniq_l3 in table_l3.index:
                                if levels[2] in field_datatype_list:
                                    if field_datatype_list[levels[2]] == "DateField" and l3 != "-":
                                        var_l3 = {levels[2]: pd.to_datetime(l3).strftime("%Y-%m-%d")}
                                    elif field_datatype_list[levels[2]] == "DateTimeField" and l3 != "-":
                                        var_l3 = {levels[2]: pd.to_datetime(l3).strftime("%Y-%m-%d %H:%M")}
                                    else:
                                        var_l3 = {levels[2]: l3}
                                    for s in range(len(levels)):
                                        if s > 2:
                                            var_l3.update({levels[s]: ""})
                                        elif s == 2:
                                            pass
                                        else:
                                            var_l3.update({levels[s]: var_l2[levels[s]]})
                                    value_l3 = table_l3.loc[uniq_l3[0], uniq_l3[1], uniq_l3[2]]
                                    for i in range(len(disp_cols)):
                                        if disp_cols[i] in field_datatype_list:
                                            if (
                                                field_datatype_list[disp_cols[i]] != "IntegerField"
                                                and field_datatype_list[disp_cols[i]] != "BigIntegerField"
                                                and field_datatype_list[disp_cols[i]] != "FloatField"
                                                and field_datatype_list[disp_cols[i]] != "AutoField"
                                            ):
                                                var_l3.update({disp_cols[i]: str(value_l3[disp_cols[i]])})
                                            else:
                                                var_l3.update({disp_cols[i]: float(value_l3[disp_cols[i]])})
                                        else:
                                            if (
                                                field_datatype_list_json[disp_cols[i]] != "IntegerField"
                                                and field_datatype_list_json[disp_cols[i]]
                                                != "BigIntegerField"
                                                and field_datatype_list_json[disp_cols[i]] != "FloatField"
                                                and field_datatype_list_json[disp_cols[i]] != "AutoField"
                                            ):
                                                var_l3.update({disp_cols[i]: str(value_l3[disp_cols[i]])})
                                            else:
                                                var_l3.update({disp_cols[i]: float(value_l3[disp_cols[i]])})
                                else:
                                    if field_datatype_list_json[levels[2]] == "DateField" and l3 != "-":
                                        var_l3 = {levels[2]: pd.to_datetime(l3).strftime("%Y-%m-%d")}
                                    elif field_datatype_list_json[levels[2]] == "DateTimeField" and l3 != "-":
                                        var_l3 = {levels[2]: pd.to_datetime(l3).strftime("%Y-%m-%d %H:%M")}
                                    else:
                                        var_l3 = {levels[2]: l3}
                                    for s in range(len(levels)):
                                        if s > 2:
                                            var_l3.update({levels[s]: ""})
                                        elif s == 2:
                                            pass
                                        else:
                                            var_l3.update({levels[s]: var_l2[levels[s]]})
                                    value_l3 = table_l3.loc[uniq_l3[0], uniq_l3[1], uniq_l3[2]]
                                    for i in range(len(disp_cols)):
                                        if disp_cols[i] in field_datatype_list:
                                            if (
                                                field_datatype_list[disp_cols[i]] != "IntegerField"
                                                and field_datatype_list[disp_cols[i]] != "BigIntegerField"
                                                and field_datatype_list[disp_cols[i]] != "FloatField"
                                                and field_datatype_list[disp_cols[i]] != "AutoField"
                                            ):
                                                var_l3.update({disp_cols[i]: str(value_l3[disp_cols[i]])})
                                            else:
                                                var_l3.update({disp_cols[i]: float(value_l3[disp_cols[i]])})
                                        else:
                                            if (
                                                field_datatype_list_json[disp_cols[i]] != "IntegerField"
                                                and field_datatype_list_json[disp_cols[i]]
                                                != "BigIntegerField"
                                                and field_datatype_list_json[disp_cols[i]] != "FloatField"
                                                and field_datatype_list_json[disp_cols[i]] != "AutoField"
                                            ):
                                                var_l3.update({disp_cols[i]: str(value_l3[disp_cols[i]])})
                                            else:
                                                var_l3.update({disp_cols[i]: float(value_l3[disp_cols[i]])})
                                # If level 4 exists create child elements for level 3
                                if len(levels) >= 4:
                                    level_no = 4
                                    # create an empty list for child elements of l3
                                    child_l3 = []
                                    main_list = disp_cols.copy()
                                    for i in range(level_no):
                                        if levels[i] not in main_list:
                                            main_list.append(levels[i])
                                    table_l4 = (
                                        data.groupby([levels[i] for i in range(level_no)])[disp_cols]
                                        .agg(operation2)
                                        .fillna(0)
                                        .round(4)
                                    )
                                    # find and create the child elements of l3
                                    for l4 in data[levels[level_no - 1]].dropna().unique():
                                        uniq_l4 = tuple([l1, l2, l3, l4])
                                        if uniq_l4 in table_l4.index:
                                            if levels[3] in field_datatype_list:
                                                if (
                                                    field_datatype_list[levels[3]] == "DateField"
                                                    and l4 != "-"
                                                ):
                                                    var_l4 = {
                                                        levels[3]: pd.to_datetime(l4).strftime("%Y-%m-%d")
                                                    }
                                                elif (
                                                    field_datatype_list[levels[3]] == "DateTimeField"
                                                    and l4 != "-"
                                                ):
                                                    var_l4 = {
                                                        levels[3]: pd.to_datetime(l4).strftime(
                                                            "%Y-%m-%d %H:%M"
                                                        )
                                                    }
                                                else:
                                                    var_l4 = {levels[3]: l4}
                                                for s in range(len(levels)):
                                                    if s > 3:
                                                        var_l4.update({levels[s]: ""})
                                                    elif s == 3:
                                                        pass
                                                    else:
                                                        var_l4.update({levels[s]: var_l3[levels[s]]})
                                                value_l4 = table_l4.loc[
                                                    uniq_l4[0], uniq_l4[1], uniq_l4[2], uniq_l4[3]
                                                ]
                                                for i in range(len(disp_cols)):
                                                    if disp_cols[i] in field_datatype_list:
                                                        if (
                                                            field_datatype_list[disp_cols[i]]
                                                            != "IntegerField"
                                                            and field_datatype_list[disp_cols[i]]
                                                            != "BigIntegerField"
                                                            and field_datatype_list[disp_cols[i]]
                                                            != "FloatField"
                                                            and field_datatype_list[disp_cols[i]]
                                                            != "AutoField"
                                                        ):
                                                            var_l4.update(
                                                                {disp_cols[i]: str(value_l4[disp_cols[i]])}
                                                            )
                                                        else:
                                                            var_l4.update(
                                                                {disp_cols[i]: float(value_l4[disp_cols[i]])}
                                                            )
                                                    else:
                                                        if (
                                                            field_datatype_list_json[disp_cols[i]]
                                                            != "IntegerField"
                                                            and field_datatype_list_json[disp_cols[i]]
                                                            != "BigIntegerField"
                                                            and field_datatype_list_json[disp_cols[i]]
                                                            != "FloatField"
                                                            and field_datatype_list_json[disp_cols[i]]
                                                            != "AutoField"
                                                        ):
                                                            var_l4.update(
                                                                {disp_cols[i]: str(value_l4[disp_cols[i]])}
                                                            )
                                                        else:
                                                            var_l4.update(
                                                                {disp_cols[i]: float(value_l4[disp_cols[i]])}
                                                            )
                                            else:
                                                if (
                                                    field_datatype_list_json[levels[3]] == "DateField"
                                                    and l4 != "-"
                                                ):
                                                    var_l4 = {
                                                        levels[3]: pd.to_datetime(l4).strftime("%Y-%m-%d")
                                                    }
                                                elif (
                                                    field_datatype_list_json[levels[3]] == "DateTimeField"
                                                    and l4 != "-"
                                                ):
                                                    var_l4 = {
                                                        levels[3]: pd.to_datetime(l4).strftime(
                                                            "%Y-%m-%d %H:%M"
                                                        )
                                                    }
                                                else:
                                                    var_l4 = {levels[3]: l4}
                                                for s in range(len(levels)):
                                                    if s > 3:
                                                        var_l4.update({levels[s]: ""})
                                                    elif s == 3:
                                                        pass
                                                    else:
                                                        var_l4.update({levels[s]: var_l3[levels[s]]})
                                                value_l4 = table_l4.loc[
                                                    uniq_l4[0], uniq_l4[1], uniq_l4[2], uniq_l4[3]
                                                ]
                                                for i in range(len(disp_cols)):
                                                    if disp_cols[i] in field_datatype_list:
                                                        if (
                                                            field_datatype_list[disp_cols[i]]
                                                            != "IntegerField"
                                                            and field_datatype_list[disp_cols[i]]
                                                            != "BigIntegerField"
                                                            and field_datatype_list[disp_cols[i]]
                                                            != "FloatField"
                                                            and field_datatype_list[disp_cols[i]]
                                                            != "AutoField"
                                                        ):
                                                            var_l4.update(
                                                                {disp_cols[i]: str(value_l4[disp_cols[i]])}
                                                            )
                                                        else:
                                                            var_l4.update(
                                                                {disp_cols[i]: float(value_l4[disp_cols[i]])}
                                                            )
                                                    else:
                                                        if (
                                                            field_datatype_list_json[disp_cols[i]]
                                                            != "IntegerField"
                                                            and field_datatype_list_json[disp_cols[i]]
                                                            != "BigIntegerField"
                                                            and field_datatype_list_json[disp_cols[i]]
                                                            != "FloatField"
                                                            and field_datatype_list_json[disp_cols[i]]
                                                            != "AutoField"
                                                        ):
                                                            var_l4.update(
                                                                {disp_cols[i]: str(value_l4[disp_cols[i]])}
                                                            )
                                                        else:
                                                            var_l4.update(
                                                                {disp_cols[i]: float(value_l4[disp_cols[i]])}
                                                            )
                                            # If level 5 exists create child elements for level 4
                                            if len(levels) >= 5:
                                                level_no = 5
                                                # create an empty list for child elements of l4
                                                child_l4 = []
                                                main_list = disp_cols.copy()
                                                for i in range(level_no):
                                                    if levels[i] not in main_list:
                                                        main_list.append(levels[i])
                                                table_l5 = (
                                                    data.groupby([levels[i] for i in range(level_no)])[
                                                        disp_cols
                                                    ]
                                                    .agg(operation2)
                                                    .fillna(0)
                                                    .round(4)
                                                )
                                                # find and create the child elements of l4
                                                for l5 in data[levels[level_no - 1]].dropna().unique():
                                                    uniq_l5 = tuple([l1, l2, l3, l4, l5])
                                                    if uniq_l5 in table_l5.index:
                                                        if levels[4] in field_datatype_list:
                                                            if (
                                                                field_datatype_list[levels[4]] == "DateField"
                                                                and l5 != "-"
                                                            ):
                                                                var_l5 = {
                                                                    levels[4]: pd.to_datetime(l5).strftime(
                                                                        "%Y-%m-%d"
                                                                    )
                                                                }
                                                            elif (
                                                                field_datatype_list[levels[4]]
                                                                == "DateTimeField"
                                                                and l5 != "-"
                                                            ):
                                                                var_l5 = {
                                                                    levels[4]: pd.to_datetime(l5).strftime(
                                                                        "%Y-%m-%d %H:%M"
                                                                    )
                                                                }
                                                            else:
                                                                var_l5 = {levels[4]: l5}
                                                            for s in range(len(levels)):
                                                                if s > 4:
                                                                    var_l5.update({levels[s]: ""})
                                                                elif s == 4:
                                                                    pass
                                                                else:
                                                                    var_l5.update(
                                                                        {levels[s]: var_l4[levels[s]]}
                                                                    )
                                                            value_l5 = table_l5.loc[
                                                                uniq_l5[0],
                                                                uniq_l5[1],
                                                                uniq_l5[2],
                                                                uniq_l5[3],
                                                                uniq_l5[4],
                                                            ]
                                                            for i in range(len(disp_cols)):
                                                                if disp_cols[i] in field_datatype_list:
                                                                    if (
                                                                        field_datatype_list[disp_cols[i]]
                                                                        != "IntegerField"
                                                                        and field_datatype_list[disp_cols[i]]
                                                                        != "BigIntegerField"
                                                                        and field_datatype_list[disp_cols[i]]
                                                                        != "FloatField"
                                                                        and field_datatype_list[disp_cols[i]]
                                                                        != "AutoField"
                                                                    ):
                                                                        var_l5.update(
                                                                            {
                                                                                disp_cols[i]: str(
                                                                                    value_l5[disp_cols[i]]
                                                                                )
                                                                            }
                                                                        )
                                                                    else:
                                                                        var_l5.update(
                                                                            {
                                                                                disp_cols[i]: float(
                                                                                    value_l5[disp_cols[i]]
                                                                                )
                                                                            }
                                                                        )
                                                                else:
                                                                    if (
                                                                        field_datatype_list_json[disp_cols[i]]
                                                                        != "IntegerField"
                                                                        and field_datatype_list_json[
                                                                            disp_cols[i]
                                                                        ]
                                                                        != "BigIntegerField"
                                                                        and field_datatype_list_json[
                                                                            disp_cols[i]
                                                                        ]
                                                                        != "FloatField"
                                                                        and field_datatype_list_json[
                                                                            disp_cols[i]
                                                                        ]
                                                                        != "AutoField"
                                                                    ):
                                                                        var_l5.update(
                                                                            {
                                                                                disp_cols[i]: str(
                                                                                    value_l5[disp_cols[i]]
                                                                                )
                                                                            }
                                                                        )
                                                                    else:
                                                                        var_l5.update(
                                                                            {
                                                                                disp_cols[i]: float(
                                                                                    value_l5[disp_cols[i]]
                                                                                )
                                                                            }
                                                                        )
                                                        else:
                                                            if (
                                                                field_datatype_list_json[levels[4]]
                                                                == "DateField"
                                                                and l5 != "-"
                                                            ):
                                                                var_l5 = {
                                                                    levels[4]: pd.to_datetime(l5).strftime(
                                                                        "%Y-%m-%d"
                                                                    )
                                                                }
                                                            elif (
                                                                field_datatype_list_json[levels[4]]
                                                                == "DateTimeField"
                                                                and l5 != "-"
                                                            ):
                                                                var_l5 = {
                                                                    levels[4]: pd.to_datetime(l5).strftime(
                                                                        "%Y-%m-%d %H:%M"
                                                                    )
                                                                }
                                                            else:
                                                                var_l5 = {levels[4]: l5}
                                                            for s in range(len(levels)):
                                                                if s > 4:
                                                                    var_l5.update({levels[s]: ""})
                                                                elif s == 4:
                                                                    pass
                                                                else:
                                                                    var_l5.update(
                                                                        {levels[s]: var_l4[levels[s]]}
                                                                    )
                                                            value_l5 = table_l5.loc[
                                                                uniq_l5[0],
                                                                uniq_l5[1],
                                                                uniq_l5[2],
                                                                uniq_l5[3],
                                                                uniq_l5[4],
                                                            ]
                                                            for i in range(len(disp_cols)):
                                                                if disp_cols[i] in field_datatype_list:
                                                                    if (
                                                                        field_datatype_list[disp_cols[i]]
                                                                        != "IntegerField"
                                                                        and field_datatype_list[disp_cols[i]]
                                                                        != "BigIntegerField"
                                                                        and field_datatype_list[disp_cols[i]]
                                                                        != "FloatField"
                                                                        and field_datatype_list[disp_cols[i]]
                                                                        != "AutoField"
                                                                    ):
                                                                        var_l5.update(
                                                                            {
                                                                                disp_cols[i]: str(
                                                                                    value_l5[disp_cols[i]]
                                                                                )
                                                                            }
                                                                        )
                                                                    else:
                                                                        var_l5.update(
                                                                            {
                                                                                disp_cols[i]: float(
                                                                                    value_l5[disp_cols[i]]
                                                                                )
                                                                            }
                                                                        )
                                                                else:
                                                                    if (
                                                                        field_datatype_list_json[disp_cols[i]]
                                                                        != "IntegerField"
                                                                        and field_datatype_list_json[
                                                                            disp_cols[i]
                                                                        ]
                                                                        != "BigIntegerField"
                                                                        and field_datatype_list_json[
                                                                            disp_cols[i]
                                                                        ]
                                                                        != "FloatField"
                                                                        and field_datatype_list_json[
                                                                            disp_cols[i]
                                                                        ]
                                                                        != "AutoField"
                                                                    ):
                                                                        var_l5.update(
                                                                            {
                                                                                disp_cols[i]: str(
                                                                                    value_l5[disp_cols[i]]
                                                                                )
                                                                            }
                                                                        )
                                                                    else:
                                                                        var_l5.update(
                                                                            {
                                                                                disp_cols[i]: float(
                                                                                    value_l5[disp_cols[i]]
                                                                                )
                                                                            }
                                                                        )
                                                        # Add child elements of l4 (l5) to the child_l4
                                                        var_l5 = formatting_check_config(
                                                            var_l5,
                                                            formatter_config_checker,
                                                            formatter_config,
                                                            model_name,
                                                            field_verbose_name_list,
                                                        )
                                                        child_l4.append(var_l5)
                                                # Add the "_children" key to l4 with childrens (l5) in it
                                                var_l4.update({"children": child_l4[:]})
                                            # Add child elements of l3 (l4) to the child_l3
                                            var_l4 = formatting_check_config(
                                                var_l4,
                                                formatter_config_checker,
                                                formatter_config,
                                                model_name,
                                                field_verbose_name_list,
                                            )
                                            child_l3.append(var_l4)
                                    # Add the "_children" key to l3 with childrens (l4) in it
                                    var_l3.update({"children": child_l3[:]})
                                # Add child elements of l2 (l3) to the child_l2
                                var_l3 = formatting_check_config(
                                    var_l3,
                                    formatter_config_checker,
                                    formatter_config,
                                    model_name,
                                    field_verbose_name_list,
                                )
                                child_l2.append(var_l3)
                        # Add the "_children" key to l2 with childrens (l3) in it
                        var_l2.update({"children": child_l2[:]})
                    # Add child elements of l1 to the child_l1
                    var_l2 = formatting_check_config(
                        var_l2,
                        formatter_config_checker,
                        formatter_config,
                        model_name,
                        field_verbose_name_list,
                    )
                    child_l1.append(var_l2)
            # Add the "_children" key to l1 with childrens (l2) in it
            var_l1.update({"children": child_l1[:]})
        # Add the level 1 elements to the parent list with all childrens init
        var_l1 = formatting_check_config(
            var_l1, formatter_config_checker, formatter_config, model_name, field_verbose_name_list
        )
        parent_list.append(var_l1)

    # Return the parent list with all children and g_childrens init
    result = parent_list
    return result


def formatting_check_config(
    row, formatter_config_checker, formatter_config, model_name, field_verbose_name_list
):
    temp_df = pd.DataFrame([row])
    if formatter_config_checker:
        for key, value in formatter_config.items():
            if model_name == key.split("-")[0]:
                for k, v in value.items():
                    if field_verbose_name_list[key.split("-")[1]] in temp_df:
                        if k == "decimal":
                            if v is not None:
                                decimals = int(v)
                                temp_df[field_verbose_name_list[key.split("-")[1]]] = temp_df[
                                    field_verbose_name_list[key.split("-")[1]]
                                ].apply(lambda x: round(x, decimals))
                        if k == "separator":
                            if v:
                                temp_df[field_verbose_name_list[key.split("-")[1]]] = temp_df[
                                    field_verbose_name_list[key.split("-")[1]]
                                ].apply("{:,}".format)
                        if k == "currency":
                            if v is not None:
                                temp_df[field_verbose_name_list[key.split("-")[1]]] = temp_df[
                                    field_verbose_name_list[key.split("-")[1]]
                                ].apply(lambda x: round(x, int(v["decimal"])))
                                temp_df[field_verbose_name_list[key.split("-")[1]]] = (
                                    CurrencySymbols.get_symbol(v["symbol"])
                                    + " "
                                    + temp_df[field_verbose_name_list[key.split("-")[1]]].astype(str)
                                )
                        if k == "scientific":
                            if v is not None:
                                temp_df[field_verbose_name_list[key.split("-")[1]]] = temp_df[
                                    field_verbose_name_list[key.split("-")[1]]
                                ].apply("{:.2e}".format)
                        if k == "percentage":
                            if v is not None:
                                temp_df[field_verbose_name_list[key.split("-")[1]]] = temp_df[
                                    field_verbose_name_list[key.split("-")[1]]
                                ].apply(lambda x: round(x, int(v["decimal"])))
                                temp_df[field_verbose_name_list[key.split("-")[1]]] = (
                                    temp_df[field_verbose_name_list[key.split("-")[1]]].astype(str) + "%"
                                )
                        if k == "date":
                            if v is not None:
                                temp_df[field_verbose_name_list[key.split("-")[1]]] = pd.to_datetime(
                                    temp_df[field_verbose_name_list[key.split("-")[1]]], format="%Y-%m-%d"
                                ).dt.strftime(v)
                        if k == "time":
                            if v is not None:
                                temp_df[field_verbose_name_list[key.split("-")[1]]] = pd.to_datetime(
                                    temp_df[field_verbose_name_list[key.split("-")[1]]], format="%H:%M:%S"
                                ).dt.strftime(v)
    return temp_df.to_dict("records")[0]
