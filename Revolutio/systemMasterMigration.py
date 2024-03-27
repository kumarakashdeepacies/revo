import json
import logging

from config.settings.base import PLATFORM_FILE_PATH
from kore_investment.users.computations.db_centralised_function import (
    db_engine_extractor,
    raw_query_executor,
    read_data_func,
)
from kore_investment.users.computations.dynamic_model_create import delete_model

with open(f"{PLATFORM_FILE_PATH}user_databases.json") as json_file:
    db_data = json.load(json_file)
    json_file.close()
connected_database = db_data
for k, config in connected_database.items():
    logging.warning(k)
    try:
        if k != "default":
            db_engine, db_type = db_engine_extractor(k)
            app_data = read_data_func(
                request="",
                config_dict={
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "Tables",
                        "Columns": ["tablename"],
                    },
                    "condition": [],
                },
                engine2=db_engine,
                db_type=db_type,
                engine_override=True,
            ).tablename.tolist()
            if "CurrencyMaster" in app_data:
                delete_model("CurrencyMaster", "", k)
            logging.warning("executed 1")
            if "CountryMaster" in app_data:
                delete_model("CountryMaster", "", k)
            logging.warning("executed 2")
    except Exception as e:
        logging.warning(f"Following exception occured on migrating system master change in {k} - {e}")
