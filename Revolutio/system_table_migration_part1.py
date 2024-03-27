from config.settings.base import DATABASES, DISKSTORE_PATH
from kore_investment.users.computations.db_centralised_function import db_engine_extractor, read_data_func

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

    application_data = read_data_func(
        "",
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "UserProfile",
                "Columns": ["*"],
            },
            "condition": [],
        },
        engine2=user_db_engine,
        db_type=db_type,
        engine_override=True,
    )

    application_data.to_csv(f"{DISKSTORE_PATH}{db_connection_name}.csv", encoding="utf-8", index=False)
