import json
import logging

from config.settings.base import DATABASES
from kore_investment.users.computations.db_centralised_function import (
    db_engine_extractor,
    read_data_func,
    update_data_func,
)

connected_database = DATABASES.copy()
if len(connected_database) > 1:
    db_type = "MSSQL"
    for k, config in connected_database.items():
        try:
            if k != "default":
                user_db_engine, db_type = db_engine_extractor(k)
                columns = [
                    "application_code",
                    "description",
                    "app_icon",
                    "app_icon_color",
                    "app_card_color",
                    "app_text_color",
                ]
                app_data = read_data_func(
                    request="",
                    config_dict={
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "application",
                            "Columns": ["*"],
                        },
                        "condition": [],
                    },
                    engine2=user_db_engine,
                    db_type=db_type,
                    engine_override=True,
                )
                for ind, row in app_data.iterrows():
                    temp = {
                        "description": row["description"],
                        "app_icon": row["app_icon"],
                        "app_icon_color": row["app_icon_color"],
                        "app_card_color": row["app_card_color"],
                        "app_text_color": row["app_text_color"],
                    }

                    update_data_func(
                        request="",
                        config_dict={
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "application",
                                "Columns": [
                                    {
                                        "column_name": "app_ui_config",
                                        "input_value": json.dumps(temp),
                                        "separator": "",
                                    },
                                ],
                            },
                            "condition": [
                                {
                                    "column_name": "application_code",
                                    "condition": "Equal to",
                                    "input_value": row["application_code"],
                                    "and_or": "",
                                }
                            ],
                        },
                        engine2=user_db_engine,
                        db_type=db_type,
                        engine_override=True,
                    )

        except Exception as e:
            logging.warning(f"Following exception occured on post save - {e}")
