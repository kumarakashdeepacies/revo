import pandas as pd

from config.settings.base import DATABASES, DISKSTORE_PATH
from kore_investment.users.computations.db_centralised_function import db_engine_extractor, update_data_func

connected_database = DATABASES.copy()
del connected_database["default"]

db_list_present = []
for key, value in connected_database.items():
    if "ENGINE" in value:
        if value["ENGINE"] == "sql_server.pyodbc":
            db_list_present.append(key)

db_list_present = list(set(db_list_present))

for db_connection_name in db_list_present:
    user_db_engine, db_type = db_engine_extractor(db_connection_name)

    df = pd.read_csv(f"{DISKSTORE_PATH}{db_connection_name}.csv")
    df.fillna("", inplace=True)

    for indx, row in df.iterrows():
        update_data_func(
            "",
            config_dict={
                "inputs": {
                    "Data_source": "Database",
                    "Table": "UserProfile",
                    "Columns": [
                        {
                            "column_name": "first_name",
                            "input_value": row["First_name"],
                            "separator": ",",
                        },
                        {
                            "column_name": "last_name",
                            "input_value": row["Last_name"],
                            "separator": ",",
                        },
                        {
                            "column_name": "bio",
                            "input_value": row["Bio"],
                            "separator": ",",
                        },
                        {
                            "column_name": "location",
                            "input_value": row["Location"],
                            "separator": "",
                        },
                    ],
                },
                "condition": [
                    {
                        "column_name": "id",
                        "condition": "Equal to",
                        "input_value": str(row["id"]),
                        "and_or": "AND",
                    },
                    {
                        "column_name": "username",
                        "condition": "Equal to",
                        "input_value": str(row["username"]),
                        "and_or": "",
                    },
                ],
            },
            engine2=user_db_engine,
            db_type=db_type,
            engine_override=True,
        )
