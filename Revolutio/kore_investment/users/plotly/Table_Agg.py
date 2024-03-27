import pandas as pd
from scipy.stats import kurtosis


def PivotData(data, levels, disp_cols, operation, modelName):
    """
    For a given JSON object containing the data, levels, display_columns
    Returns the Tree based grouped data JSON
    """
    operation2 = {}
    field_datatype_list = {
        field.verbose_name: field.get_internal_type() for field in modelName.concrete_fields
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
        if field_datatype_list[levels[0]] == "DateField":
            var_l1 = {"Category": pd.to_datetime(l1).strftime("%Y-%m-%d")}
        elif field_datatype_list[levels[0]] == "DateTimeField":
            var_l1 = {"Category": pd.to_datetime(l1).strftime("%Y-%m-%d %H:%M")}
        else:
            var_l1 = {"Category": l1}
        value_l1 = table_l1[table_l1.index == l1]
        for i in range(len(disp_cols)):
            if field_datatype_list[disp_cols[i]] not in [
                "IntegerField",
                "BigIntegerField",
                "FloatField",
                "AutoField",
            ]:
                var_l1.update({disp_cols[i]: str(value_l1[disp_cols[i]].values[0])})
            else:
                var_l1.update({disp_cols[i]: float(value_l1[disp_cols[i]])})
        var_l1["tabulator_table_column_name"] = levels[0]
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
                    if field_datatype_list[levels[1]] == "DateField":
                        var_l2 = {"Category": pd.to_datetime(l2).strftime("%Y-%m-%d")}
                    elif field_datatype_list[levels[1]] == "DateTimeField":
                        var_l2 = {"Category": pd.to_datetime(l2).strftime("%Y-%m-%d %H:%M")}
                    else:
                        var_l2 = {"Category": l2}
                    value_l2 = table_l2.loc[uniq_l2[0], uniq_l2[1]]
                    for i in range(len(disp_cols)):
                        if field_datatype_list[disp_cols[i]] not in [
                            "IntegerField",
                            "BigIntegerField",
                            "FloatField",
                            "AutoField",
                        ]:
                            var_l2.update({disp_cols[i]: str(value_l2[disp_cols[i]])})
                        else:
                            var_l2.update({disp_cols[i]: float(value_l2[disp_cols[i]])})
                        var_l2["tabulator_table_column_name"] = levels[1]
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
                                if field_datatype_list[levels[2]] == "DateField":
                                    var_l3 = {"Category": pd.to_datetime(l3).strftime("%Y-%m-%d")}
                                elif field_datatype_list[levels[2]] == "DateTimeField":
                                    var_l3 = {"Category": pd.to_datetime(l3).strftime("%Y-%m-%d %H:%M")}
                                else:
                                    var_l3 = {"Category": l3}
                                value_l3 = table_l3.loc[uniq_l3[0], uniq_l3[1], uniq_l3[2]]
                                for i in range(len(disp_cols)):
                                    if (
                                        field_datatype_list[disp_cols[i]] != "IntegerField"
                                        and field_datatype_list[disp_cols[i]] != "BigIntegerField"
                                        and field_datatype_list[disp_cols[i]] != "FloatField"
                                        and field_datatype_list[disp_cols[i]] != "AutoField"
                                    ):
                                        var_l3.update({disp_cols[i]: str(value_l3[disp_cols[i]])})
                                    else:
                                        var_l3.update({disp_cols[i]: float(value_l3[disp_cols[i]])})
                                var_l3["tabulator_table_column_name"] = levels[2]
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
                                            if field_datatype_list[levels[3]] == "DateField":
                                                var_l4 = {"Category": pd.to_datetime(l4).strftime("%Y-%m-%d")}
                                            elif field_datatype_list[levels[3]] == "DateTimeField":
                                                var_l4 = {
                                                    "Category": pd.to_datetime(l4).strftime("%Y-%m-%d %H:%M")
                                                }
                                            else:
                                                var_l4 = {"Category": l4}
                                            value_l4 = table_l4.loc[
                                                uniq_l4[0], uniq_l4[1], uniq_l4[2], uniq_l4[3]
                                            ]
                                            for i in range(len(disp_cols)):
                                                if (
                                                    field_datatype_list[disp_cols[i]] != "IntegerField"
                                                    and field_datatype_list[disp_cols[i]] != "BigIntegerField"
                                                    and field_datatype_list[disp_cols[i]] != "FloatField"
                                                    and field_datatype_list[disp_cols[i]] != "AutoField"
                                                ):
                                                    var_l4.update({disp_cols[i]: str(value_l4[disp_cols[i]])})
                                                else:
                                                    var_l4.update(
                                                        {disp_cols[i]: float(value_l4[disp_cols[i]])}
                                                    )
                                            var_l4["tabulator_table_column_name"] = levels[3]
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
                                                        if field_datatype_list[levels[4]] == "DateField":
                                                            var_l5 = {
                                                                "Category": pd.to_datetime(l5).strftime(
                                                                    "%Y-%m-%d"
                                                                )
                                                            }
                                                        elif (
                                                            field_datatype_list[levels[4]] == "DateTimeField"
                                                        ):
                                                            var_l5 = {
                                                                "Category": pd.to_datetime(l5).strftime(
                                                                    "%Y-%m-%d %H:%M"
                                                                )
                                                            }
                                                        else:
                                                            var_l5 = {"Category": l5}
                                                        value_l5 = table_l5.loc[
                                                            uniq_l5[0],
                                                            uniq_l5[1],
                                                            uniq_l5[2],
                                                            uniq_l5[3],
                                                            uniq_l5[4],
                                                        ]
                                                        for i in range(len(disp_cols)):
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
                                                        var_l5["tabulator_table_column_name"] = levels[4]
                                                        # Add child elements of l4 (l5) to the child_l4
                                                        child_l4.append(var_l5)
                                                # Add the "_children" key to l4 with childrens (l5) in it
                                                var_l4.update({"_children": child_l4[:]})
                                            # Add child elements of l3 (l4) to the child_l3
                                            child_l3.append(var_l4)
                                    # Add the "_children" key to l3 with childrens (l4) in it
                                    var_l3.update({"_children": child_l3[:]})
                                # Add child elements of l2 (l3) to the child_l2
                                child_l2.append(var_l3)
                        # Add the "_children" key to l2 with childrens (l3) in it
                        var_l2.update({"_children": child_l2[:]})
                    # Add child elements of l1 to the child_l1
                    child_l1.append(var_l2)
            # Add the "_children" key to l1 with childrens (l2) in it
            var_l1.update({"_children": child_l1[:]})
        # Add the level 1 elements to the parent list with all childrens init
        parent_list.append(var_l1)

    # Return the parent list with all children and g_childrens init
    result = parent_list
    return result
