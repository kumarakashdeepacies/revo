import copy

from kore_investment.users.computations.db_centralised_function import read_data_func

from . import dynamic_model_create


def data_chunking(
    table_name,
    request,
    start,
    length,
    conditions=[],
    columns=[],
    data_cond_adv_list=[],
    reportingViewColumns_unique_indentfier_flag=False,
):
    modelName = dynamic_model_create.get_model_class(table_name, request)

    if len(conditions) > 0:
        if conditions[-1]["and_or"] != ")":
            conditions[-1]["and_or"] = ""
    if reportingViewColumns_unique_indentfier_flag:
        import_conditions = copy.deepcopy(conditions)
        rawData = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": table_name,
                    "Columns": columns,
                    "Order_Type": f"ORDER BY {modelName.pk.name}",
                },
                "condition": import_conditions,
                "adv_condition": data_cond_adv_list,
            },
        )
        r_len = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": table_name,
                    "Agg_Type": f"Count({modelName.pk.name})",
                    "Columns": [],
                },
                "condition": conditions,
                "adv_condition": data_cond_adv_list,
            },
        ).iloc[0, 0]
    else:
        if length != "-1":
            import_conditions = copy.deepcopy(conditions)
            rawData = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": table_name,
                        "Columns": columns,
                        "Order_Type": f"ORDER BY {modelName.pk.name}",
                        "Offset": start,
                        "Fetch_next": length,
                    },
                    "condition": import_conditions,
                    "adv_condition": data_cond_adv_list,
                },
            )
            r_len = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": table_name,
                        "Agg_Type": f"Count({modelName.pk.name})",
                        "Columns": [],
                    },
                    "condition": conditions,
                    "adv_condition": data_cond_adv_list,
                },
            ).iloc[0, 0]
        else:
            rawData = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": table_name,
                        "Columns": columns,
                    },
                    "condition": conditions,
                    "adv_condition": data_cond_adv_list,
                },
            )
            r_len = len(rawData.index)

    return rawData, r_len
