import pandas as pd

from kore_investment.users.computations.db_centralised_function import read_data_func


def products_model_validation_check(request, data=None):
    product_to_model_mapper_data = data["product_to_model_data"]
    product_master = data["products_data"]
    positions_table = data["positions_data"]
    products_list = (positions_table["product_variant_name"].unique()).tolist()

    model_repository = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "Model_Repository",
                "Columns": ["model_code"],
            },
            "condition": [],
        },
    )
    product_to_model_mapper_data = pd.merge(
        product_to_model_mapper_data,
        product_master,
        on="product_variant_name",
        how="left",
    )
    product_to_model_mapper_data = pd.merge(
        product_to_model_mapper_data, model_repository, on="model_code", how="left"
    )

    product_to_model_mapping_final = {}
    model_name_list = []
    error_msg_list_final = []
    for i in range(len(products_list)):
        if products_list[i] in product_to_model_mapper_data["product_variant_name"].tolist():
            product_to_model_mapping_final[products_list[i]] = product_to_model_mapper_data.loc[
                product_to_model_mapper_data["product_variant_name"] == products_list[i], "model_code"
            ].iloc[0]
        else:
            model_name_list.append(products_list[i])
            error_msg_list_final.append("Product is not mapped to a model")

    df_error = pd.DataFrame({"Product Type": model_name_list, "Validation Issue": error_msg_list_final})
    return df_error
