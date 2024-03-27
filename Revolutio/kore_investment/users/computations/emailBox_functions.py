from ast import literal_eval
from datetime import date, datetime
import json
import logging

import numpy as np
import pandas as pd
from rq_scheduler import Scheduler

from config.settings.base import MEDIA_ROOT, redis_instance_scheduler
from kore_investment.users.computations.db_centralised_function import (
    data_handling,
    delete_data_func,
    read_data_func,
    update_data_func,
)
from kore_investment.users.computations.multi_select_handler import (
    fk_id_to_value_converter,
    multi_select_id_to_value_converter,
)

from . import dynamic_model_create, standardised_functions


def value_test(tablename, request, column_name, condition_name, input_value, input_data):
    if tablename:
        model = dynamic_model_create.get_model_class(tablename, request)
        IntegerField_list = [
            field.name for field in model.concrete_fields if field.get_internal_type() == "IntegerField"
        ]
        BigIntegerField_list = [
            field.name for field in model.concrete_fields if field.get_internal_type() == "BigIntegerField"
        ]
        FloatField_list = [
            field.name for field in model.concrete_fields if field.get_internal_type() == "FloatField"
        ]
        DateTimeField_list = [
            field.name for field in model.concrete_fields if field.get_internal_type() == "DateTimeField"
        ]
        DateField_list = [
            field.name for field in model.concrete_fields if field.get_internal_type() == "DateField"
        ]
        TimeField_list = [
            field.name for field in model.concrete_fields if field.get_internal_type() == "TimeField"
        ]
        BooleanField_list = [
            field.name for field in model.concrete_fields if field.get_internal_type() == "BooleanField"
        ]
    else:
        IntegerField_list = input_data.select_dtypes(include=["int32"]).columns.to_list()
        BigIntegerField_list = input_data.select_dtypes(include=["int64"]).columns.to_list()
        FloatField_list = input_data.select_dtypes(include=["float64"]).columns.to_list()
        DateTimeField_list = input_data.select_dtypes(include=["datetime64[ns]"]).columns.to_list()
        DateField_list = input_data.select_dtypes(include=["datetime64[ns]"]).columns.to_list()
        TimeField_list = input_data.select_dtypes(include=["datetime64[ns]"]).columns.to_list()
        BooleanField_list = input_data.select_dtypes(include=["bool"]).columns.to_list()
    date_type = DateTimeField_list + TimeField_list + DateField_list
    bool_type = BooleanField_list

    final_string = ""

    if condition_name == "Greater than" or condition_name == "Greater than equal to":
        if column_name in IntegerField_list:
            if not input_value:
                input_value = "NULL"
                final_string = f'FinalData["{column_name}"].isna()'
            else:
                check_value = float(input_value)
                if condition_name == "Greater than":
                    final_string = (
                        f'pd.to_numeric(FinalData["{column_name}"], errors="coerce",).gt({check_value})'
                    )
                else:
                    final_string = (
                        f'pd.to_numeric(FinalData["{column_name}"], errors="coerce",).ge({check_value})'
                    )
        elif column_name in BigIntegerField_list:
            if not input_value:
                input_value = "NULL"
                final_string = f'FinalData["{column_name}"].isna()'
            else:
                check_value = float(input_value)
                if condition_name == "Greater than":
                    final_string = (
                        f'pd.to_numeric(FinalData["{column_name}"], errors="coerce",).gt({check_value})'
                    )
                else:
                    final_string = (
                        f'pd.to_numeric(FinalData["{column_name}"], errors="coerce",).ge({check_value})'
                    )

        elif column_name in FloatField_list:
            if not input_value:
                input_value = "NULL"
                final_string = f'FinalData["{column_name}"].isna()'
            else:
                check_value = float(input_value)
                if condition_name == "Greater than":
                    final_string = (
                        f'pd.to_numeric(FinalData["{column_name}"], errors="coerce",).gt({check_value})'
                    )
                else:
                    final_string = (
                        f'pd.to_numeric(FinalData["{column_name}"], errors="coerce",).ge({check_value})'
                    )

        elif column_name in date_type:
            if column_name in DateTimeField_list:
                try:
                    date_convert = datetime.strptime({input_value}, "%Y-%m-%dT%H:%M")
                    date_convert = f"""datetime.strptime("{input_value}", "%Y-%m-%dT%H:%M")"""
                except Exception as e:
                    logging.warning(f"Following exception occured - {e}")
                    date_convert = str(pd.NaT)

                if condition_name == "Greater than":
                    if str(date_convert) != str(pd.NaT):
                        final_string = f'pd.to_datetime(FinalData["{column_name}"], format="%Y-%m-%d %H:%M:%S", errors="coerce", dayfirst=True,).gt({date_convert})'
                        input_value = str(datetime.strptime({input_value}, "%Y-%m-%dT%H:%M"))
                    else:
                        final_string = f'pd.to_datetime(FinalData["{column_name}"], format="%Y-%m-%d %H:%M:%S", errors="coerce", dayfirst=True,).gt({date_convert})'
                        input_value = "NULL"
                else:
                    if str(date_convert) != str(pd.NaT):
                        final_string = f'pd.to_datetime(FinalData["{column_name}"], format="%Y-%m-%d %H:%M:%S", errors="coerce", dayfirst=True,).ge({date_convert})'
                        input_value = str(datetime.strptime({input_value}, "%Y-%m-%dT%H:%M"))
                    else:
                        final_string = f'pd.to_datetime(FinalData["{column_name}"], format="%Y-%m-%d %H:%M:%S", errors="coerce", dayfirst=True,).ge({date_convert})'
                        input_value = "NULL"

            elif column_name in DateField_list:
                try:
                    date_convert = datetime.strptime(input_value, "%Y-%m-%d")
                    date_convert = f"""datetime.strptime("{input_value}", "%Y-%m-%d")"""
                except Exception as e:
                    logging.warning(f"Following exception occured - {e}")
                    date_convert = pd.NaT

                if condition_name == "Greater than":
                    if str(date_convert) != str(pd.NaT):
                        final_string = f'pd.to_datetime(FinalData["{column_name}"], format="%Y-%m-%d", errors="coerce", dayfirst=True).gt({date_convert})'
                        input_value = str(datetime.strptime(input_value, "%Y-%m-%d").date())
                    else:
                        final_string = f'pd.to_datetime(FinalData["{column_name}"], format="%Y-%m-%d", errors="coerce", dayfirst=True).gt({date_convert})'
                        input_value = "NULL"
                else:
                    if str(date_convert) != str(pd.NaT):
                        final_string = f'pd.to_datetime(FinalData["{column_name}"], format="%Y-%m-%d", errors="coerce", dayfirst=True).ge({date_convert})'
                        input_value = str(datetime.strptime(input_value, "%Y-%m-%d").date())
                    else:
                        final_string = f'pd.to_datetime(FinalData["{column_name}"], format="%Y-%m-%d", errors="coerce", dayfirst=True).ge({date_convert})'
                        input_value = "NULL"
            else:

                try:
                    date_convert = datetime.strptime(input_value, "%H:%M:%S")
                    date_convert = f"""datetime.strptime("{input_value}", "%H:%M:%S")"""
                except Exception as e:
                    logging.warning(f"Following exception occured - {e}")
                    date_convert = pd.NaT

                if condition_name == "Greater than":
                    if str(date_convert) != str(pd.NaT):
                        final_string = f'pd.to_datetime(FinalData["{column_name}"], format="%H:%M:%S", errors="coerce", dayfirst=True).gt({date_convert})'

                        input_value = str(datetime.strptime(input_value, "%H:%M:%S").time())
                    else:
                        final_string = f'pd.to_datetime(FinalData["{column_name}"], format="%H:%M:%S", errors="coerce", dayfirst=True).gt({date_convert})'
                        input_value = "NULL"
                else:
                    if str(date_convert) != str(pd.NaT):
                        final_string = f'pd.to_datetime(FinalData["{column_name}"], format="%H:%M:%S", errors="coerce", dayfirst=True).ge({date_convert})'

                        input_value = str(datetime.strptime(input_value, "%H:%M:%S").time())
                    else:
                        final_string = f'pd.to_datetime(FinalData["{column_name}"], format="%H:%M:%S", errors="coerce", dayfirst=True).ge({date_convert})'
                        input_value = "NULL"

    if condition_name == "Smaller than" or condition_name == "Smaller than equal to":
        if column_name in IntegerField_list:
            if not input_value:
                check_value = "NULL"
                final_string = f'FinalData["{column_name}"].isna()'
            else:
                check_value = float(input_value)
                if condition_name == "Smaller than":
                    final_string = (
                        f'pd.to_numeric(FinalData["{column_name}"], errors="coerce",).lt({check_value})'
                    )
                else:
                    final_string = (
                        f'pd.to_numeric(FinalData["{column_name}"], errors="coerce",).le({check_value})'
                    )
        elif column_name in BigIntegerField_list:
            if not input_value:
                check_value = "NULL"
                final_string = f'FinalData["{column_name}"].isna()'
            else:
                check_value = float(input_value)
                if condition_name == "Smaller than":
                    final_string = (
                        f'pd.to_numeric(FinalData["{column_name}"], errors="coerce",).lt({check_value})'
                    )
                else:
                    final_string = (
                        f'pd.to_numeric(FinalData["{column_name}"], errors="coerce",).le({check_value})'
                    )
        elif column_name in FloatField_list:
            if not input_value:
                check_value = "NULL"
                final_string = f'FinalData["{column_name}"].isna()'
            else:
                check_value = float(input_value)
                if condition_name == "Smaller than":
                    final_string = (
                        f'pd.to_numeric(FinalData["{column_name}"], errors="coerce",).lt({check_value})'
                    )
                else:
                    final_string = (
                        f'pd.to_numeric(FinalData["{column_name}"], errors="coerce",).le({check_value})'
                    )
        elif column_name in date_type:
            if column_name in DateTimeField_list:
                try:
                    date_convert = datetime.strptime({input_value}, "%Y-%m-%dT%H:%M")
                    date_convert = f"""datetime.strptime("{input_value}", "%Y-%m-%dT%H:%M")"""
                except Exception as e:
                    logging.warning(f"Following exception occured - {e}")
                    date_convert = str(pd.NaT)

                if condition_name == "Smaller than":
                    if str(date_convert) != str(pd.NaT):
                        final_string = f'pd.to_datetime(FinalData["{column_name}"], format="%Y-%m-%dT%H:%M", errors="coerce", dayfirst=True,).lt({date_convert})'
                        input_value = str(datetime.strptime({input_value}, "%Y-%m-%dT%H:%M"))
                    else:
                        final_string = f'pd.to_datetime(FinalData["{column_name}"], format="%Y-%m-%dT%H:%M", errors="coerce", dayfirst=True,).lt({date_convert})'
                        input_value = "NULL"
                else:
                    if str(date_convert) != str(pd.NaT):
                        final_string = f'pd.to_datetime(FinalData["{column_name}"], format="%Y-%m-%dT%H:%M", errors="coerce", dayfirst=True,).le({date_convert})'
                        input_value = str(datetime.strptime({input_value}, "%Y-%m-%dT%H:%M"))
                    else:
                        final_string = f'pd.to_datetime(FinalData["{column_name}"], format="%Y-%m-%dT%H:%M", errors="coerce", dayfirst=True,).le({date_convert})'
                        input_value = "NULL"

            elif column_name in DateField_list:
                try:
                    date_convert = datetime.strptime(input_value, "%Y-%m-%d")
                    date_convert = f"""datetime.strptime("{input_value}", "%Y-%m-%d")"""
                except Exception as e:
                    logging.warning(f"Following exception occured - {e}")
                    date_convert = pd.NaT

                if condition_name == "Smaller than":
                    if str(date_convert) != str(pd.NaT):
                        final_string = f'pd.to_datetime(FinalData["{column_name}"], format="%Y-%m-%d", errors="coerce", dayfirst=True).lt({date_convert})'
                        input_value = str(datetime.strptime(input_value, "%Y-%m-%d").date())
                    else:
                        final_string = f'pd.to_datetime(FinalData["{column_name}"], format="%Y-%m-%d", errors="coerce", dayfirst=True).lt({date_convert})'
                        input_value = "NULL"
                else:
                    if str(date_convert) != str(pd.NaT):
                        final_string = f'pd.to_datetime(FinalData["{column_name}"], format="%Y-%m-%d", errors="coerce", dayfirst=True).le({date_convert})'
                        input_value = str(datetime.strptime(input_value, "%Y-%m-%d").date())
                    else:
                        final_string = f'pd.to_datetime(FinalData["{column_name}"], format="%Y-%m-%d", errors="coerce", dayfirst=True).le({date_convert})'
                        input_value = "NULL"
            else:
                try:
                    date_convert = datetime.strptime(input_value, "%H:%M:%S")
                    date_convert = f"""datetime.strptime("{input_value}", "%H:%M:%S")"""
                except Exception as e:
                    logging.warning(f"Following exception occured - {e}")
                    date_convert = pd.NaT

                if condition_name == "Smaller than":
                    if str(date_convert) != str(pd.NaT):
                        final_string = f'pd.to_datetime(FinalData["{column_name}"], format="%H:%M:%S", errors="coerce", dayfirst=True,).lt({date_convert})'

                        input_value = str(datetime.strptime(input_value, "%H:%M:%S").time())
                    else:
                        final_string = f'pd.to_datetime(FinalData["{column_name}"], format="%H:%M:%S", errors="coerce", dayfirst=True,).lt({date_convert})'
                        input_value = "NULL"
                else:
                    if str(date_convert) != str(pd.NaT):
                        final_string = f'pd.to_datetime(FinalData["{column_name}"], format="%H:%M:%S", errors="coerce", dayfirst=True,).le({date_convert})'

                        input_value = str(datetime.strptime(input_value, "%H:%M:%S").time())
                    else:
                        final_string = f'pd.to_datetime(FinalData["{column_name}"], format="%H:%M:%S", errors="coerce", dayfirst=True,).le({date_convert})'
                        input_value = "NULL"

    if condition_name == "Equal to":
        if column_name in IntegerField_list:
            if not input_value:
                input_value = "NULL"
                final_string = f'FinalData["{column_name}"].isna()'
            else:
                check_value = int(float(input_value))
                final_string = f'FinalData["{column_name}"].astype("Int64").eq({check_value})'
        elif column_name in BigIntegerField_list:
            if not input_value:
                input_value = "NULL"
                final_string = f'FinalData["{column_name}"].isna()'
            else:
                check_value = int(float(input_value))
                final_string = f'FinalData["{column_name}"].astype("Int64").eq({check_value})'
        elif column_name in FloatField_list:
            if not input_value:
                input_value = "NULL"
                final_string = f'FinalData["{column_name}"].isna()'
            else:
                check_value = float(input_value)
                final_string = f'FinalData["{column_name}"].astype("float").eq({check_value})'
        elif column_name in date_type:
            date_convert = ""
            if column_name in DateTimeField_list:
                try:
                    date_convert = datetime.strptime(input_value, "%Y-%m-%dT%H:%M")
                    date_convert = f"""datetime.strptime("{input_value}", "%Y-%m-%dT%H:%M")"""
                except Exception as e:
                    logging.warning(f"Following exception occured - {e}")
                    date_convert = str(pd.NaT)

                if date_convert == str(pd.NaT):
                    input_value = "NULL"
                    final_string = f'FinalData["{column_name}"].isna()'
                else:
                    input_value = str(datetime.strptime(input_value, "%Y-%m-%dT%H:%M"))
                    final_string = f'pd.to_datetime(FinalData["{column_name}"], format="%Y-%m-%d %H:%M:%S", errors="coerce", dayfirst=True).eq({date_convert})'

            elif column_name in DateField_list:
                try:
                    date_convert = datetime.strptime(input_value, "%Y-%m-%d")
                    date_convert = f"""datetime.strptime("{input_value}", "%Y-%m-%d")"""
                except Exception as e:
                    logging.warning(f"Following exception occured - {e}")
                    date_convert = str(pd.NaT)

                if date_convert == str(pd.NaT):
                    input_value = "NULL"
                    final_string = f'FinalData["{column_name}"].isna()'
                else:
                    final_string = f'pd.to_datetime(FinalData["{column_name}"], format="%Y-%m-%d", errors="coerce", dayfirst=True).eq({date_convert})'
                    input_value = str(datetime.strptime(input_value, "%Y-%m-%d").date())

            else:
                try:
                    date_convert = datetime.strptime(input_value, "%H:%M:%S")
                    date_convert = f"""datetime.strptime("{input_value}", "%H:%M:%S")"""
                except Exception as e:
                    logging.warning(f"Following exception occured - {e}")
                    date_convert = str(pd.NaT)

                if date_convert == str(pd.NaT):
                    input_value = "NULL"
                    final_string = f'FinalData["{column_name}"].isna()'
                else:
                    input_value = str(datetime.strptime(input_value, "%H:%M:%S").time())
                    final_string = f'pd.to_datetime(FinalData["{column_name}"], format="%H:%M:%S", errors="coerce", dayfirst=True).eq({date_convert})'

        elif column_name in bool_type:
            if input_value in ["True", 1, "1"]:
                final_string = f'FinalData["{column_name}"].astype("str").eq("1")'
            else:
                final_string = f'FinalData["{column_name}"].astype("str").eq("0")'
        else:
            if input_value and input_value != "NULL":
                final_string = f'FinalData["{column_name}"].astype("str").eq("{input_value}")'
            else:
                final_string = f'FinalData["{column_name}"].isna()'
                input_value = "NULL"

    if condition_name == "Not Equal to":
        if column_name in IntegerField_list:
            if not input_value:
                final_string = f'FinalData["{column_name}"].notnull()'
                input_value = "NULL"
            else:
                check_value = int(float(input_value))
                final_string = f'pd.to_numeric(FinalData["{column_name}"].fillna({check_value + 1}), errors="coerce",).ne({check_value})'
        elif column_name in BigIntegerField_list:
            if not input_value:
                final_string = f'FinalData["{column_name}"].notnull()'
                input_value = "NULL"
            else:
                check_value = int(float(input_value))
                final_string = f'pd.to_numeric(FinalData["{column_name}"].fillna({check_value + 1}), errors="coerce",).ne({check_value})'
        elif column_name in FloatField_list:
            if not input_value:
                final_string = f'FinalData["{column_name}"].notnull()'
                input_value = "NULL"
            else:
                check_value = float(input_value)
                final_string = f'pd.to_numeric(FinalData["{column_name}"].fillna({check_value + 1}), errors="coerce",).ne({check_value})'
        elif column_name in date_type:
            date_convert = ""
            if column_name in DateTimeField_list:
                try:
                    date_convert = datetime.strptime(input_value, "%Y-%m-%dT%H:%M")
                    date_convert = f"""datetime.strptime("{input_value}", "%Y-%m-%dT%H:%M")"""
                except Exception as e:
                    logging.warning(f"Following exception occured - {e}")
                    date_convert = str(pd.NaT)

                if date_convert == str(pd.NaT):
                    input_value = "NULL"
                    final_string = f'FinalData["{column_name}"].notnull()'
                else:
                    input_value = str(datetime.strptime(input_value, "%Y-%m-%dT%H:%M"))
                    final_string = f'pd.to_datetime(FinalData["{column_name}"], format="%Y-%m-%d %H:%M:%S", errors="coerce", dayfirst=True).ne({date_convert})'

            elif column_name in DateField_list:
                try:
                    date_convert = datetime.strptime(input_value, "%Y-%m-%d")
                    date_convert = f"""datetime.strptime("{input_value}", "%Y-%m-%d")"""

                except Exception as e:
                    logging.warning(f"Following exception occured - {e}")
                    date_convert = str(pd.NaT)

                if date_convert == str(pd.NaT):
                    input_value = "NULL"
                    final_string = f'FinalData["{column_name}"].notnull()'
                else:
                    final_string = f'pd.to_datetime(FinalData["{column_name}"], format="%Y-%m-%d", errors="coerce", dayfirst=True).ne({date_convert})'
                    input_value = str(datetime.strptime(input_value, "%Y-%m-%d").date())

            else:
                try:
                    date_convert = datetime.strptime(input_value, "%H:%M:%S")
                    date_convert = f"""datetime.strptime("{input_value}", "%H:%M:%S")"""
                except Exception as e:
                    logging.warning(f"Following exception occured - {e}")
                    date_convert = str(pd.NaT)

                if date_convert == str(pd.NaT):
                    input_value = "NULL"
                    final_string = f'FinalData["{column_name}"].notnull()'
                else:
                    input_value = str(datetime.strptime(input_value, "%H:%M:%S").time())
                    final_string = f'pd.to_datetime(FinalData["{column_name}"], format="%H:%M:%S", errors="coerce", dayfirst=True).ne({date_convert})'

        elif column_name in bool_type:
            if input_value in ["True", 1, "1"]:
                final_string = f'FinalData["{column_name}"].astype("str").ne("1")'
            else:
                final_string = f'FinalData["{column_name}"].astype("str").ne("0")'
        else:
            if input_value and input_value != "NULL":
                final_string = f'FinalData["{column_name}"].astype("str").ne("{input_value}")'
            else:
                final_string = f'FinalData["{column_name}"].notnull()'
                input_value = "NULL"

    if condition_name == "IN":
        if input_value:
            if "," in input_value:
                input_value = list(input_value.split(","))
                check_input = []
                for x in input_value:
                    if x:
                        check_input.append(x)
                    else:
                        check_input.append(str(np.nan))
            else:
                if column_name in date_type:
                    if column_name in DateTimeField_list:
                        try:
                            check_input = datetime.strptime(input_value, "%Y-%m-%dT%H:%M")
                        except Exception as e:
                            logging.warning(f"Following exception occured - {e}")
                            check_input = str(pd.NaT)
                    elif column_name in DateField_list:
                        try:
                            check_input = datetime.strptime(input_value, "%Y-%m-%d")
                            check_input = str(check_input.date())
                        except Exception as e:
                            logging.warning(f"Following exception occured - {e}")
                            check_input = str(pd.NaT)

                    else:
                        try:
                            check_input = datetime.strptime(input_value, "%H:%M:%S")
                            check_input = str(check_input.time())
                        except Exception as e:
                            logging.warning(f"Following exception occured - {e}")
                            check_input = str(pd.NaT)
                else:
                    check_input = str(input_value)
        else:
            check_input = str(np.nan)
        if type(input_value) == list:
            final_string = f'FinalData["{column_name}"].astype("str").str.contains("|".join({check_input}), case=True, regex=True)'
        else:
            final_string = f'FinalData["{column_name}"].astype("str").str.contains("{check_input}", case=True, regex=True, na=True)'

    if condition_name == "NOT IN":
        if input_value:
            if "," in input_value:
                input_value = list(input_value.split(","))
                check_input = []
                for x in input_value:
                    if x:
                        check_input.append(x)
                    else:
                        check_input.append(str(np.nan))
            else:
                if column_name in date_type:
                    if column_name in DateTimeField_list:
                        try:
                            check_input = datetime.strptime(input_value, "%Y-%m-%dT%H:%M")
                        except Exception as e:
                            logging.warning(f"Following exception occured - {e}")
                            check_input = str(pd.NaT)
                    elif column_name in DateField_list:
                        try:
                            check_input = datetime.strptime(input_value, "%Y-%m-%d")
                            check_input = str(check_input.date())
                        except Exception as e:
                            logging.warning(f"Following exception occured - {e}")
                            check_input = str(pd.NaT)
                    else:
                        try:
                            check_input = datetime.strptime(input_value, "%H:%M:%S")
                            check_input = str(check_input.time())
                        except Exception as e:
                            logging.warning(f"Following exception occured - {e}")
                            check_input = str(pd.NaT)
                else:
                    check_input = str(input_value)
        else:
            check_input = str(np.nan)
        if type(input_value) == list:
            final_string = f'~FinalData["{column_name}"].astype("str").str.contains("|".join({check_input}), case=True, regex=True)'
        else:
            final_string = f'~FinalData["{column_name}"].astype("str").str.contains("{check_input}", case=True, regex=True, na=False)'
    return final_string


def check_condition(constraint_dict, FinalData, tablename, request):
    constraint_string = ""
    for constraint_name, constraint_content in constraint_dict.items():
        final_evaluation_string = """("""
        for rule_name, rule_list in constraint_content.items():
            for r in range(len(rule_list)):
                condition_name = rule_list[r]["condition"]
                input_value = rule_list[r]["input_value"]

                if rule_list[r]["type"] == "group_based":
                    column_name = rule_list[r]["column_name"]
                    user_in_groups = list(request.user.groups.values_list("name", flat=True))
                    res = bool(set(user_in_groups) & set(rule_list[r]["input_value"]))
                    final_string = f"{res}"
                else:
                    column_name = rule_list[r]["column"]
                    final_string = value_test(
                        tablename, request, column_name, condition_name, input_value, FinalData
                    )

                if final_evaluation_string != """(""":
                    final_evaluation_string += f" & {final_string}"
                else:
                    final_evaluation_string += final_string
        final_evaluation_string += ")"
        constraint_string += final_evaluation_string + " | "

    if constraint_string.endswith(" | "):
        constraint_string = constraint_string.strip(" | ")

    condition_df = pd.DataFrame(columns=["Condition_Result"])
    condition_df["Condition_Result"] = pd.eval(
        constraint_string, parser="python", target=FinalData, engine="python"
    )

    if FinalData[condition_df["Condition_Result"]].empty:
        return False, pd.DataFrame()
    else:
        return True, FinalData[condition_df["Condition_Result"]]


def emailBox(request, child_element_id_email_box, action="", FinalData=[], tablename="", rtf_data_dict={}):

    if isinstance(request, dict):

        class AttrDict:
            def __init__(self, i_dict):
                for key, value in i_dict.items():
                    if key not in ["password", "last_login", "date_joined"]:
                        setattr(self, key, value)
                if i_dict.get("username"):
                    setattr(self, "is_anonymous", False)
                else:
                    setattr(self, "is_anonymous", True)

            def get_host(self):
                return self.host

        request["user"] = AttrDict(request["user"])
        request = AttrDict(request)

    condition_data_email_box = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "TabScreens",
                "Columns": ["tab_body_content"],
            },
            "condition": [
                {
                    "column_name": "element_id",
                    "condition": "Equal to",
                    "input_value": child_element_id_email_box,
                    "and_or": "",
                },
            ],
        },
    )

    cond_flag = True
    if child_element_id_email_box != "#" and len(condition_data_email_box) > 0:

        condition_data_email_box_config = json.loads(condition_data_email_box["tab_body_content"].iloc[0])

        if (
            condition_data_email_box_config["trigger_type"] == "trigger_based"
            or condition_data_email_box_config["trigger_type"] == "condition_based"
        ):

            if condition_data_email_box_config["config"].get("condition_based_config"):
                condition_based_config = condition_data_email_box_config["config"]["condition_based_config"]
            else:
                condition_based_config = []

            if condition_based_config:
                constraint_dict = {}
                for i in condition_based_config:
                    if i["constraint"] in constraint_dict:
                        constraint_dict[i["constraint"]].append(i)
                    else:
                        constraint_dict[i["constraint"]] = [i]

                constraint_dict_copy = constraint_dict.copy()

                for const, configgs in constraint_dict_copy.items():
                    ruleset_dict = {}
                    for jj in configgs:
                        if jj["rule_set"] in ruleset_dict:
                            ruleset_dict[jj["rule_set"]].append(jj)
                        else:
                            ruleset_dict[jj["rule_set"]] = [jj]
                    constraint_dict[const] = ruleset_dict
            else:
                constraint_dict = {}
                ruleset_dict = {}

            if constraint_dict:
                if len(FinalData):
                    try:
                        cond_flag, condition_df = check_condition(
                            constraint_dict, FinalData, tablename, request
                        )
                        if cond_flag:
                            FinalData = condition_df
                    except Exception as e:
                        logging.warning(f"Following exception occured - {e}")
                        cond_flag = False
                else:
                    cond_flag = False

            if (
                action in condition_data_email_box_config["config"]["trigger_email_for"]
                or len(condition_data_email_box_config["config"]["trigger_email_for"]) == 0
            ) and cond_flag:

                if tablename:
                    model_name1 = dynamic_model_create.get_model_class(tablename, request)
                else:
                    tablename = "comp"
                    model_name1 = ""

                final_data_json_email_box = {}

                if action == "comp" and len(FinalData):
                    for idx, row in FinalData.iterrows():
                        tdata = row.to_frame().T
                        date_field = []
                        num_field = tdata.dtypes.name in ["float", "float64", "float32"]

                        for ii in tdata.select_dtypes(include=["datetime64[ns]"]).columns:
                            try:
                                if ii in ["modified_date", "created_date"]:
                                    tdata[ii] = pd.to_datetime(tdata[ii]).dt.strftime("%Y-%m-%d %H:%M:%S")
                                else:
                                    tdata[ii] = pd.to_datetime(tdata[ii]).dt.strftime("%Y-%m-%d")
                            except Exception as e:
                                logging.warning(f"Following exception occured - {e}")

                        for ii in tdata.select_dtypes(
                            include=["float", "float64", "float32", "int", "int32", "int64"]
                        ).columns:
                            try:
                                tdata[ii] = pd.to_numeric(tdata[ii], errors="coerce").fillna(0)
                            except Exception as e:
                                logging.warning(f"Following exception occured - {e}")

                        approval_code = standardised_functions.random_generator("alphanum", 32)

                        if condition_data_email_box_config["config"].get("to_config"):
                            if (
                                condition_data_email_box_config["config"]["to_config"]["to_recipient_type"]
                                == "static"
                            ):
                                to_list = condition_data_email_box_config["config"]["to_config"][
                                    "to_recipient_list"
                                ]
                            elif (
                                condition_data_email_box_config["config"]["to_config"]["to_recipient_type"]
                                == "dynamic"
                            ):
                                t_tname = condition_data_email_box_config["config"]["to_config"][
                                    "to_recipient_dynamic_table"
                                ]
                                t_tcol = condition_data_email_box_config["config"]["to_config"][
                                    "to_recipient_dynamic_column"
                                ]

                                model_class = dynamic_model_create.get_model_class(t_tname, request)

                                interim_value = tdata[t_tcol].values[0]
                                if model_class.get_field(t_tcol).get_internal_type() == "MultiselectField":
                                    if (
                                        interim_value
                                        and interim_value
                                        not in ["nan", "NaT", pd.NaT, np.nan, "None", None, " ", "<NA>"]
                                        and not pd.isna(interim_value)
                                    ):
                                        field_multiselect_config = json.loads(
                                            model_class.get_field(t_tcol).mulsel_config
                                        )
                                        multi_select_table = field_multiselect_config["value"][0]
                                        multi_select_master_column = field_multiselect_config["masterColumn"][
                                            0
                                        ]
                                        interim_value = list(json.loads(interim_value).keys())
                                        converted_value = read_data_func(
                                            request,
                                            {
                                                "inputs": {
                                                    "Data_source": "Database",
                                                    "Table": multi_select_table,
                                                    "Columns": [multi_select_master_column],
                                                },
                                                "condition": [
                                                    {
                                                        "column_name": "id",
                                                        "condition": "IN",
                                                        "input_value": interim_value,
                                                        "and_or": "",
                                                    }
                                                ],
                                            },
                                        )[multi_select_master_column].tolist()
                                        to_list = converted_value
                                    else:
                                        to_list = []
                                else:
                                    if isinstance(tdata[t_tcol].iloc[0], list):
                                        to_list = tdata[t_tcol].iloc[0]
                                    else:
                                        to_list = tdata[t_tcol].tolist()
                            elif (
                                condition_data_email_box_config["config"]["to_config"]["to_recipient_type"]
                                == "dynamic_user"
                            ):
                                to_list = [request.user.email]
                            elif (
                                condition_data_email_box_config["config"]["to_config"]["to_recipient_type"]
                                == "static_user"
                            ):
                                user_list = condition_data_email_box_config["config"]["to_config"][
                                    "to_recipient_list"
                                ]
                                to_list = (
                                    read_data_func(
                                        request,
                                        {
                                            "inputs": {
                                                "Data_source": "Database",
                                                "Table": "User",
                                                "Columns": ["email"],
                                            },
                                            "condition": [
                                                {
                                                    "column_name": "username",
                                                    "condition": "IN",
                                                    "input_value": str(tuple(user_list)).replace(",)", ")"),
                                                    "and_or": "",
                                                }
                                            ],
                                        },
                                    )
                                ).email.tolist()
                            elif (
                                condition_data_email_box_config["config"]["to_config"]["to_recipient_type"]
                                == "static_groups"
                            ):
                                group_list = condition_data_email_box_config["config"]["to_config"][
                                    "to_recipient_list"
                                ]
                                group_id = (
                                    read_data_func(
                                        request,
                                        {
                                            "inputs": {
                                                "Data_source": "Database",
                                                "Table": "group_details",
                                                "Columns": ["id"],
                                            },
                                            "condition": [
                                                {
                                                    "column_name": "name",
                                                    "condition": "IN",
                                                    "input_value": str(tuple(group_list)).replace(",)", ")"),
                                                    "and_or": "",
                                                }
                                            ],
                                        },
                                    )
                                ).id.tolist()
                                if group_id:
                                    user_ids = (
                                        read_data_func(
                                            request,
                                            {
                                                "inputs": {
                                                    "Data_source": "Database",
                                                    "Table": "user_groups",
                                                    "Columns": ["user_id"],
                                                },
                                                "condition": [
                                                    {
                                                        "column_name": "group_id",
                                                        "condition": "IN",
                                                        "input_value": str(tuple(group_id)).replace(
                                                            ",)", ")"
                                                        ),
                                                        "and_or": "",
                                                    }
                                                ],
                                            },
                                        )
                                    ).user_id.tolist()
                                    if user_ids:
                                        to_list = (
                                            read_data_func(
                                                request,
                                                {
                                                    "inputs": {
                                                        "Data_source": "Database",
                                                        "Table": "User",
                                                        "Columns": ["email"],
                                                    },
                                                    "condition": [
                                                        {
                                                            "column_name": "id",
                                                            "condition": "IN",
                                                            "input_value": str(tuple(user_ids)).replace(
                                                                ",)", ")"
                                                            ),
                                                            "and_or": "",
                                                        }
                                                    ],
                                                },
                                            )
                                        ).email.tolist()
                                    else:
                                        to_list = []
                                else:
                                    to_list = []
                            else:
                                to_list = []
                        else:
                            to_list = []

                        if condition_data_email_box_config["config"].get("to_config_cc"):
                            if (
                                condition_data_email_box_config["config"]["to_config_cc"]["to_recipient_type"]
                                == "static"
                            ):
                                to_cc = condition_data_email_box_config["config"]["to_config_cc"][
                                    "to_recipient_list"
                                ]
                            elif (
                                condition_data_email_box_config["config"]["to_config_cc"]["to_recipient_type"]
                                == "dynamic"
                            ):
                                t_tname = condition_data_email_box_config["config"]["to_config_cc"][
                                    "to_recipient_dynamic_table"
                                ]
                                t_tcol = condition_data_email_box_config["config"]["to_config_cc"][
                                    "to_recipient_dynamic_column"
                                ]
                                model_class = dynamic_model_create.get_model_class(t_tname, request)

                                interim_value = tdata[t_tcol].values[0]
                                if model_class.get_field(t_tcol).get_internal_type() == "MultiselectField":
                                    if (
                                        interim_value
                                        and interim_value
                                        not in ["nan", "NaT", pd.NaT, np.nan, "None", None, " ", "<NA>"]
                                        and not pd.isna(interim_value)
                                    ):
                                        field_multiselect_config = json.loads(
                                            model_class.get_field(t_tcol).mulsel_config
                                        )
                                        multi_select_table = field_multiselect_config["value"][0]
                                        multi_select_master_column = field_multiselect_config["masterColumn"][
                                            0
                                        ]
                                        interim_value = list(json.loads(interim_value).keys())
                                        converted_value = read_data_func(
                                            request,
                                            {
                                                "inputs": {
                                                    "Data_source": "Database",
                                                    "Table": multi_select_table,
                                                    "Columns": [multi_select_master_column],
                                                },
                                                "condition": [
                                                    {
                                                        "column_name": "id",
                                                        "condition": "IN",
                                                        "input_value": interim_value,
                                                        "and_or": "",
                                                    }
                                                ],
                                            },
                                        )[multi_select_master_column].tolist()
                                        to_cc = converted_value
                                    else:
                                        to_cc = []
                                else:
                                    if isinstance(tdata[t_tcol].iloc[0], list):
                                        to_cc = tdata[t_tcol].iloc[0]
                                    else:
                                        to_cc = [tdata[t_tcol].iloc[0]]
                            elif (
                                condition_data_email_box_config["config"]["to_config_cc"]["to_recipient_type"]
                                == "dynamic_user"
                            ):
                                to_cc = [request.user.email]
                            elif (
                                condition_data_email_box_config["config"]["to_config_cc"]["to_recipient_type"]
                                == "static_user"
                            ):
                                user_list = condition_data_email_box_config["config"]["to_config_cc"][
                                    "to_recipient_list"
                                ]
                                to_cc = (
                                    read_data_func(
                                        request,
                                        {
                                            "inputs": {
                                                "Data_source": "Database",
                                                "Table": "User",
                                                "Columns": ["email"],
                                            },
                                            "condition": [
                                                {
                                                    "column_name": "username",
                                                    "condition": "IN",
                                                    "input_value": str(tuple(user_list)).replace(",)", ")"),
                                                    "and_or": "",
                                                }
                                            ],
                                        },
                                    )
                                ).email.tolist()
                            elif (
                                condition_data_email_box_config["config"]["to_config_cc"]["to_recipient_type"]
                                == "static_groups"
                            ):
                                group_list = condition_data_email_box_config["config"]["to_config_cc"][
                                    "to_recipient_list"
                                ]
                                group_id = (
                                    read_data_func(
                                        request,
                                        {
                                            "inputs": {
                                                "Data_source": "Database",
                                                "Table": "group_details",
                                                "Columns": ["id"],
                                            },
                                            "condition": [
                                                {
                                                    "column_name": "name",
                                                    "condition": "IN",
                                                    "input_value": str(tuple(group_list)).replace(",)", ")"),
                                                    "and_or": "",
                                                }
                                            ],
                                        },
                                    )
                                ).id.tolist()
                                if group_id:
                                    user_ids = (
                                        read_data_func(
                                            request,
                                            {
                                                "inputs": {
                                                    "Data_source": "Database",
                                                    "Table": "user_groups",
                                                    "Columns": ["user_id"],
                                                },
                                                "condition": [
                                                    {
                                                        "column_name": "group_id",
                                                        "condition": "IN",
                                                        "input_value": str(tuple(group_id)).replace(
                                                            ",)", ")"
                                                        ),
                                                        "and_or": "",
                                                    }
                                                ],
                                            },
                                        )
                                    ).user_id.tolist()
                                    if user_ids:
                                        to_cc = (
                                            read_data_func(
                                                request,
                                                {
                                                    "inputs": {
                                                        "Data_source": "Database",
                                                        "Table": "User",
                                                        "Columns": ["email"],
                                                    },
                                                    "condition": [
                                                        {
                                                            "column_name": "id",
                                                            "condition": "IN",
                                                            "input_value": str(tuple(user_ids)).replace(
                                                                ",)", ")"
                                                            ),
                                                            "and_or": "",
                                                        }
                                                    ],
                                                },
                                            )
                                        ).email.tolist()
                                    else:
                                        to_cc = []
                                else:
                                    to_cc = []
                            else:
                                to_cc = []
                        else:
                            to_cc = []

                        if condition_data_email_box_config["config"].get("to_config_bcc"):
                            if (
                                condition_data_email_box_config["config"]["to_config_bcc"][
                                    "to_recipient_type"
                                ]
                                == "static"
                            ):
                                to_bcc = condition_data_email_box_config["config"]["to_config_bcc"][
                                    "to_recipient_list"
                                ]
                            elif (
                                condition_data_email_box_config["config"]["to_config_bcc"][
                                    "to_recipient_type"
                                ]
                                == "dynamic"
                            ):
                                t_tname = condition_data_email_box_config["config"]["to_config_bcc"][
                                    "to_recipient_dynamic_table"
                                ]
                                t_tcol = condition_data_email_box_config["config"]["to_config_bcc"][
                                    "to_recipient_dynamic_column"
                                ]

                                model_class = dynamic_model_create.get_model_class(t_tname, request)

                                interim_value = tdata[t_tcol].values[0]
                                if model_class.get_field(t_tcol).get_internal_type() == "MultiselectField":
                                    if (
                                        interim_value
                                        and interim_value
                                        not in ["nan", "NaT", pd.NaT, np.nan, "None", None, " ", "<NA>"]
                                        and not pd.isna(interim_value)
                                    ):
                                        field_multiselect_config = json.loads(
                                            model_class.get_field(t_tcol).mulsel_config
                                        )
                                        multi_select_table = field_multiselect_config["value"][0]
                                        multi_select_master_column = field_multiselect_config["masterColumn"][
                                            0
                                        ]
                                        interim_value = list(json.loads(interim_value).keys())
                                        converted_value = read_data_func(
                                            request,
                                            {
                                                "inputs": {
                                                    "Data_source": "Database",
                                                    "Table": multi_select_table,
                                                    "Columns": [multi_select_master_column],
                                                },
                                                "condition": [
                                                    {
                                                        "column_name": "id",
                                                        "condition": "IN",
                                                        "input_value": interim_value,
                                                        "and_or": "",
                                                    }
                                                ],
                                            },
                                        )[multi_select_master_column].tolist()
                                        to_bcc = converted_value
                                    else:
                                        to_bcc = []
                                else:
                                    if isinstance(tdata[t_tcol].iloc[0], list):
                                        to_bcc = tdata[t_tcol].iloc[0]
                                    else:
                                        to_bcc = [tdata[t_tcol].iloc[0]]
                            elif (
                                condition_data_email_box_config["config"]["to_config_bcc"][
                                    "to_recipient_type"
                                ]
                                == "dynamic_user"
                            ):
                                to_bcc = [request.user.email]
                            elif (
                                condition_data_email_box_config["config"]["to_config_bcc"][
                                    "to_recipient_type"
                                ]
                                == "static_user"
                            ):
                                user_list = condition_data_email_box_config["config"]["to_config_bcc"][
                                    "to_recipient_list"
                                ]
                                to_bcc = (
                                    read_data_func(
                                        request,
                                        {
                                            "inputs": {
                                                "Data_source": "Database",
                                                "Table": "User",
                                                "Columns": ["email"],
                                            },
                                            "condition": [
                                                {
                                                    "column_name": "username",
                                                    "condition": "IN",
                                                    "input_value": str(tuple(user_list)).replace(",)", ")"),
                                                    "and_or": "",
                                                }
                                            ],
                                        },
                                    )
                                ).email.tolist()
                            elif (
                                condition_data_email_box_config["config"]["to_config_bcc"][
                                    "to_recipient_type"
                                ]
                                == "static_groups"
                            ):
                                group_list = condition_data_email_box_config["config"]["to_config_bcc"][
                                    "to_recipient_list"
                                ]
                                group_id = (
                                    read_data_func(
                                        request,
                                        {
                                            "inputs": {
                                                "Data_source": "Database",
                                                "Table": "group_details",
                                                "Columns": ["id"],
                                            },
                                            "condition": [
                                                {
                                                    "column_name": "name",
                                                    "condition": "IN",
                                                    "input_value": str(tuple(group_list)).replace(",)", ")"),
                                                    "and_or": "",
                                                }
                                            ],
                                        },
                                    )
                                ).id.tolist()
                                if group_id:
                                    user_ids = (
                                        read_data_func(
                                            request,
                                            {
                                                "inputs": {
                                                    "Data_source": "Database",
                                                    "Table": "user_groups",
                                                    "Columns": ["user_id"],
                                                },
                                                "condition": [
                                                    {
                                                        "column_name": "group_id",
                                                        "condition": "IN",
                                                        "input_value": str(tuple(group_id)).replace(
                                                            ",)", ")"
                                                        ),
                                                        "and_or": "",
                                                    }
                                                ],
                                            },
                                        )
                                    ).user_id.tolist()
                                    if user_ids:
                                        to_bcc = (
                                            read_data_func(
                                                request,
                                                {
                                                    "inputs": {
                                                        "Data_source": "Database",
                                                        "Table": "User",
                                                        "Columns": ["email"],
                                                    },
                                                    "condition": [
                                                        {
                                                            "column_name": "id",
                                                            "condition": "IN",
                                                            "input_value": str(tuple(user_ids)).replace(
                                                                ",)", ")"
                                                            ),
                                                            "and_or": "",
                                                        }
                                                    ],
                                                },
                                            )
                                        ).email.tolist()
                                    else:
                                        to_bcc = []
                                else:
                                    to_bcc = []
                            else:
                                to_bcc = []
                        else:
                            to_bcc = []

                        approval_notification_attachment_config = condition_data_email_box_config["config"][
                            "attachmentConfig"
                        ]

                        final_data_json_email_box[approval_code] = tdata.to_json(orient="records")

                        approval_notification_subject = condition_data_email_box_config["config"][
                            "subject_email"
                        ]
                        smtpConfigKey = condition_data_email_box_config["config"]["from_email"]
                        content = condition_data_email_box_config["config"]["text_email"]

                        transaction_data_dict = json.loads(tdata.to_json(orient="records"))[0]

                        if approval_notification_subject:
                            if "{TransactionCreatedBy}" in approval_notification_subject:
                                approval_notification_subject = approval_notification_subject.replace(
                                    "{TransactionCreatedBy}", request.user.username
                                )
                            else:
                                pass

                            if "{TransactionTime}" in approval_notification_subject:
                                approval_notification_subject = approval_notification_subject.replace(
                                    "{TransactionTime}", f"{datetime.now()}"
                                )
                            else:
                                pass

                            for field in transaction_data_dict:
                                if f"VerboseName-{field}" in approval_notification_subject:
                                    approval_notification_subject = approval_notification_subject.replace(
                                        f"{{VerboseName-{field}}}", field
                                    )
                                else:
                                    pass
                                if f"Value-{field}" in approval_notification_subject:
                                    if field in transaction_data_dict:
                                        approval_notification_subject = approval_notification_subject.replace(
                                            f"{{Value-{field}}}", str(transaction_data_dict[field])
                                        )
                                    else:
                                        approval_notification_subject = approval_notification_subject.replace(
                                            f"{{Value-{field}}}", " - "
                                        )
                                else:
                                    continue

                        if "{TransactionCreatedBy}" in content:
                            content = content.replace("{TransactionCreatedBy}", request.user.username)
                        else:
                            pass
                        if "{TransactionCreatedBy-Name}" in content:
                            content = content.replace(
                                "{TransactionCreatedBy-Name}",
                                f"{request.user.first_name} {request.user.last_name}",
                            )
                        else:
                            pass
                        if "{TransactionTime}" in content:
                            content = content.replace("{TransactionTime}", f"{datetime.now()}")
                        else:
                            pass

                        if "{domain}" in content:
                            domain = request.build_absolute_uri("/")[:-1]
                            if request.scheme == "https":
                                domain = domain.replace("http", "https")
                            else:
                                pass
                            content = content.replace("{domain}", f"{domain}")
                        else:
                            pass
                        if "{app_code}" in content:
                            url_string = request.path
                            f_occ = url_string.find("/", url_string.find("/") + 1)
                            s_occ = url_string.find("/", url_string.find("/") + f_occ + 1)
                            app_code = url_string[f_occ + 1 : s_occ]
                            content = content.replace("{app_code}", f"{app_code}")
                        else:
                            pass

                        for field in transaction_data_dict:
                            if f"VerboseName-{field}" in content:
                                content = content.replace(f"{{VerboseName-{field}}}", field)
                            else:
                                pass
                            if f"Value-{field}" in content:
                                if field in transaction_data_dict:
                                    content = content.replace(
                                        f"{{Value-{field}}}", str(transaction_data_dict[field])
                                    )
                                else:
                                    content = content.replace(f"{{Value-{field}}}", " - ")
                            else:
                                continue
                        standardised_functions.send_approval_mail(
                            request,
                            tablename,
                            final_data_json_email_box,
                            to_list,
                            content,
                            subject=approval_notification_subject,
                            in_system_approval=False,
                            to_cc=to_cc,
                            to_bcc=to_bcc,
                            attachments_config=approval_notification_attachment_config,
                            smtpConfigKey=smtpConfigKey,
                        )

                else:
                    if len(FinalData):
                        tdata = FinalData

                        date_field = []
                        num_field = []
                    else:
                        tdata = []

                    if model_name1 and len(FinalData):
                        for field in model_name1.concrete_fields:
                            if field.get_internal_type() in ["DateField", "DateTimeField"]:
                                date_field.append(field.name)
                            elif field.get_internal_type() in ["IntField", "FloatField"]:
                                num_field.append(field.name)

                        for ii in date_field:
                            try:
                                if ii in ["modified_date", "created_date"]:
                                    tdata[ii] = pd.to_datetime(tdata[ii]).dt.strftime("%Y-%m-%d %H:%M:%S")
                                else:
                                    tdata[ii] = pd.to_datetime(tdata[ii]).dt.strftime("%Y-%m-%d")
                            except Exception as e:
                                logging.warning(f"Following exception occured - {e}")

                        for ii in num_field:
                            try:
                                tdata[ii] = pd.to_numeric(tdata[ii], errors="coerce").fillna(0)
                            except Exception as e:
                                logging.warning(f"Following exception occured - {e}")

                    approval_code = standardised_functions.random_generator("alphanum", 32)

                    if model_name1:
                        columnRenameList = {
                            field.name: field.verbose_name for field in model_name1.concrete_fields
                        }
                    else:
                        columnRenameList = {}

                    if condition_data_email_box_config["config"].get("to_config"):
                        if (
                            condition_data_email_box_config["config"]["to_config"]["to_recipient_type"]
                            == "static"
                        ):
                            to_list = condition_data_email_box_config["config"]["to_config"][
                                "to_recipient_list"
                            ]
                        elif condition_data_email_box_config["config"]["to_config"][
                            "to_recipient_type"
                        ] == "dynamic" and len(FinalData):
                            t_tname = condition_data_email_box_config["config"]["to_config"][
                                "to_recipient_dynamic_table"
                            ]
                            t_tcol = condition_data_email_box_config["config"]["to_config"][
                                "to_recipient_dynamic_column"
                            ]

                            model_class = dynamic_model_create.get_model_class(t_tname, request)

                            interim_value = tdata[t_tcol].values[0]
                            if model_class.get_field(t_tcol).get_internal_type() == "MultiselectField":
                                if (
                                    interim_value
                                    and interim_value
                                    not in ["nan", "NaT", pd.NaT, np.nan, "None", None, " ", "<NA>"]
                                    and not pd.isna(interim_value)
                                ):
                                    field_multiselect_config = json.loads(
                                        model_class.get_field(t_tcol).mulsel_config
                                    )
                                    multi_select_table = field_multiselect_config["value"][0]
                                    multi_select_master_column = field_multiselect_config["masterColumn"][0]
                                    interim_value = list(json.loads(interim_value).keys())
                                    converted_value = read_data_func(
                                        request,
                                        {
                                            "inputs": {
                                                "Data_source": "Database",
                                                "Table": multi_select_table,
                                                "Columns": [multi_select_master_column],
                                            },
                                            "condition": [
                                                {
                                                    "column_name": "id",
                                                    "condition": "IN",
                                                    "input_value": interim_value,
                                                    "and_or": "",
                                                }
                                            ],
                                        },
                                    )[multi_select_master_column].tolist()
                                    to_list = converted_value
                                else:
                                    to_list = []
                            else:
                                if isinstance(tdata[t_tcol].iloc[0], list):
                                    to_list = tdata[t_tcol].iloc[0]
                                else:
                                    to_list = tdata[t_tcol].tolist()
                        elif (
                            condition_data_email_box_config["config"]["to_config"]["to_recipient_type"]
                            == "dynamic_user"
                        ):
                            to_list = [request.user.email]
                        elif (
                            condition_data_email_box_config["config"]["to_config"]["to_recipient_type"]
                            == "static_user"
                        ):
                            user_list = condition_data_email_box_config["config"]["to_config"][
                                "to_recipient_list"
                            ]
                            to_list = (
                                read_data_func(
                                    request,
                                    {
                                        "inputs": {
                                            "Data_source": "Database",
                                            "Table": "User",
                                            "Columns": ["email"],
                                        },
                                        "condition": [
                                            {
                                                "column_name": "username",
                                                "condition": "IN",
                                                "input_value": str(tuple(user_list)).replace(",)", ")"),
                                                "and_or": "",
                                            }
                                        ],
                                    },
                                )
                            ).email.tolist()
                        elif (
                            condition_data_email_box_config["config"]["to_config"]["to_recipient_type"]
                            == "static_groups"
                        ):
                            group_list = condition_data_email_box_config["config"]["to_config"][
                                "to_recipient_list"
                            ]
                            group_id = (
                                read_data_func(
                                    request,
                                    {
                                        "inputs": {
                                            "Data_source": "Database",
                                            "Table": "group_details",
                                            "Columns": ["id"],
                                        },
                                        "condition": [
                                            {
                                                "column_name": "name",
                                                "condition": "IN",
                                                "input_value": str(tuple(group_list)).replace(",)", ")"),
                                                "and_or": "",
                                            }
                                        ],
                                    },
                                )
                            ).id.tolist()
                            if group_id:
                                user_ids = (
                                    read_data_func(
                                        request,
                                        {
                                            "inputs": {
                                                "Data_source": "Database",
                                                "Table": "user_groups",
                                                "Columns": ["user_id"],
                                            },
                                            "condition": [
                                                {
                                                    "column_name": "group_id",
                                                    "condition": "IN",
                                                    "input_value": str(tuple(group_id)).replace(",)", ")"),
                                                    "and_or": "",
                                                }
                                            ],
                                        },
                                    )
                                ).user_id.tolist()
                                if user_ids:
                                    to_list = (
                                        read_data_func(
                                            request,
                                            {
                                                "inputs": {
                                                    "Data_source": "Database",
                                                    "Table": "User",
                                                    "Columns": ["email"],
                                                },
                                                "condition": [
                                                    {
                                                        "column_name": "id",
                                                        "condition": "IN",
                                                        "input_value": str(tuple(user_ids)).replace(
                                                            ",)", ")"
                                                        ),
                                                        "and_or": "",
                                                    }
                                                ],
                                            },
                                        )
                                    ).email.tolist()
                                else:
                                    to_list = []
                            else:
                                to_list = []
                        else:
                            to_list = []
                    else:
                        to_list = []

                    if condition_data_email_box_config["config"].get("to_config_cc"):
                        if (
                            condition_data_email_box_config["config"]["to_config_cc"]["to_recipient_type"]
                            == "static"
                        ):
                            to_cc = condition_data_email_box_config["config"]["to_config_cc"][
                                "to_recipient_list"
                            ]
                        elif condition_data_email_box_config["config"]["to_config_cc"][
                            "to_recipient_type"
                        ] == "dynamic" and len(FinalData):
                            t_tname = condition_data_email_box_config["config"]["to_config_cc"][
                                "to_recipient_dynamic_table"
                            ]
                            t_tcol = condition_data_email_box_config["config"]["to_config_cc"][
                                "to_recipient_dynamic_column"
                            ]
                            model_class = dynamic_model_create.get_model_class(t_tname, request)

                            interim_value = tdata[t_tcol].values[0]
                            if model_class.get_field(t_tcol).get_internal_type() == "MultiselectField":
                                if (
                                    interim_value
                                    and interim_value
                                    not in ["nan", "NaT", pd.NaT, np.nan, "None", None, " ", "<NA>"]
                                    and not pd.isna(interim_value)
                                ):
                                    field_multiselect_config = json.loads(
                                        model_class.get_field(t_tcol).mulsel_config
                                    )
                                    multi_select_table = field_multiselect_config["value"][0]
                                    multi_select_master_column = field_multiselect_config["masterColumn"][0]
                                    interim_value = list(json.loads(interim_value).keys())
                                    converted_value = read_data_func(
                                        request,
                                        {
                                            "inputs": {
                                                "Data_source": "Database",
                                                "Table": multi_select_table,
                                                "Columns": [multi_select_master_column],
                                            },
                                            "condition": [
                                                {
                                                    "column_name": "id",
                                                    "condition": "IN",
                                                    "input_value": interim_value,
                                                    "and_or": "",
                                                }
                                            ],
                                        },
                                    )[multi_select_master_column].tolist()
                                    to_cc = converted_value
                                else:
                                    to_cc = []
                            else:
                                if isinstance(tdata[t_tcol].iloc[0], list):
                                    to_cc = tdata[t_tcol].iloc[0]
                                else:
                                    to_cc = tdata[t_tcol].tolist()
                        elif (
                            condition_data_email_box_config["config"]["to_config_cc"]["to_recipient_type"]
                            == "dynamic_user"
                        ):
                            to_cc = [request.user.email]
                        elif (
                            condition_data_email_box_config["config"]["to_config_cc"]["to_recipient_type"]
                            == "static_user"
                        ):
                            user_list = condition_data_email_box_config["config"]["to_config_cc"][
                                "to_recipient_list"
                            ]
                            to_cc = (
                                read_data_func(
                                    request,
                                    {
                                        "inputs": {
                                            "Data_source": "Database",
                                            "Table": "User",
                                            "Columns": ["email"],
                                        },
                                        "condition": [
                                            {
                                                "column_name": "username",
                                                "condition": "IN",
                                                "input_value": str(tuple(user_list)).replace(",)", ")"),
                                                "and_or": "",
                                            }
                                        ],
                                    },
                                )
                            ).email.tolist()
                        elif (
                            condition_data_email_box_config["config"]["to_config_cc"]["to_recipient_type"]
                            == "static_groups"
                        ):
                            group_list = condition_data_email_box_config["config"]["to_config_cc"][
                                "to_recipient_list"
                            ]
                            group_id = (
                                read_data_func(
                                    request,
                                    {
                                        "inputs": {
                                            "Data_source": "Database",
                                            "Table": "group_details",
                                            "Columns": ["id"],
                                        },
                                        "condition": [
                                            {
                                                "column_name": "name",
                                                "condition": "IN",
                                                "input_value": str(tuple(group_list)).replace(",)", ")"),
                                                "and_or": "",
                                            }
                                        ],
                                    },
                                )
                            ).id.tolist()
                            if group_id:
                                user_ids = (
                                    read_data_func(
                                        request,
                                        {
                                            "inputs": {
                                                "Data_source": "Database",
                                                "Table": "user_groups",
                                                "Columns": ["user_id"],
                                            },
                                            "condition": [
                                                {
                                                    "column_name": "group_id",
                                                    "condition": "IN",
                                                    "input_value": str(tuple(group_id)).replace(",)", ")"),
                                                    "and_or": "",
                                                }
                                            ],
                                        },
                                    )
                                ).user_id.tolist()
                                if user_ids:
                                    to_cc = (
                                        read_data_func(
                                            request,
                                            {
                                                "inputs": {
                                                    "Data_source": "Database",
                                                    "Table": "User",
                                                    "Columns": ["email"],
                                                },
                                                "condition": [
                                                    {
                                                        "column_name": "id",
                                                        "condition": "IN",
                                                        "input_value": str(tuple(user_ids)).replace(
                                                            ",)", ")"
                                                        ),
                                                        "and_or": "",
                                                    }
                                                ],
                                            },
                                        )
                                    ).email.tolist()
                                else:
                                    to_cc = []
                            else:
                                to_cc = []
                        else:
                            to_cc = []
                    else:
                        to_cc = []

                    if condition_data_email_box_config["config"].get("to_config_bcc"):
                        if (
                            condition_data_email_box_config["config"]["to_config_bcc"]["to_recipient_type"]
                            == "static"
                        ):
                            to_bcc = condition_data_email_box_config["config"]["to_config_bcc"][
                                "to_recipient_list"
                            ]
                        elif condition_data_email_box_config["config"]["to_config_bcc"][
                            "to_recipient_type"
                        ] == "dynamic" and len(FinalData):
                            t_tname = condition_data_email_box_config["config"]["to_config_bcc"][
                                "to_recipient_dynamic_table"
                            ]
                            t_tcol = condition_data_email_box_config["config"]["to_config_bcc"][
                                "to_recipient_dynamic_column"
                            ]

                            model_class = dynamic_model_create.get_model_class(t_tname, request)

                            interim_value = tdata[t_tcol].values[0]
                            if model_class.get_field(t_tcol).get_internal_type() == "MultiselectField":
                                if (
                                    interim_value
                                    and interim_value
                                    not in ["nan", "NaT", pd.NaT, np.nan, "None", None, " ", "<NA>"]
                                    and not pd.isna(interim_value)
                                ):
                                    field_multiselect_config = json.loads(
                                        model_class.get_field(t_tcol).mulsel_config
                                    )
                                    multi_select_table = field_multiselect_config["value"][0]
                                    multi_select_master_column = field_multiselect_config["masterColumn"][0]
                                    interim_value = list(json.loads(interim_value).keys())
                                    converted_value = read_data_func(
                                        request,
                                        {
                                            "inputs": {
                                                "Data_source": "Database",
                                                "Table": multi_select_table,
                                                "Columns": [multi_select_master_column],
                                            },
                                            "condition": [
                                                {
                                                    "column_name": "id",
                                                    "condition": "IN",
                                                    "input_value": interim_value,
                                                    "and_or": "",
                                                }
                                            ],
                                        },
                                    )[multi_select_master_column].tolist()
                                    to_bcc = converted_value
                                else:
                                    to_bcc = []
                            else:
                                if isinstance(tdata[t_tcol].iloc[0], list):
                                    to_bcc = tdata[t_tcol].iloc[0]
                                else:
                                    to_bcc = tdata[t_tcol].tolist()
                        elif (
                            condition_data_email_box_config["config"]["to_config_bcc"]["to_recipient_type"]
                            == "dynamic_user"
                        ):
                            to_bcc = [request.user.email]
                        elif (
                            condition_data_email_box_config["config"]["to_config_bcc"]["to_recipient_type"]
                            == "static_user"
                        ):
                            user_list = condition_data_email_box_config["config"]["to_config_bcc"][
                                "to_recipient_list"
                            ]
                            to_bcc = (
                                read_data_func(
                                    request,
                                    {
                                        "inputs": {
                                            "Data_source": "Database",
                                            "Table": "User",
                                            "Columns": ["email"],
                                        },
                                        "condition": [
                                            {
                                                "column_name": "username",
                                                "condition": "IN",
                                                "input_value": str(tuple(user_list)).replace(",)", ")"),
                                                "and_or": "",
                                            }
                                        ],
                                    },
                                )
                            ).email.tolist()
                        elif (
                            condition_data_email_box_config["config"]["to_config_bcc"]["to_recipient_type"]
                            == "static_groups"
                        ):
                            group_list = condition_data_email_box_config["config"]["to_config_bcc"][
                                "to_recipient_list"
                            ]
                            group_id = (
                                read_data_func(
                                    request,
                                    {
                                        "inputs": {
                                            "Data_source": "Database",
                                            "Table": "group_details",
                                            "Columns": ["id"],
                                        },
                                        "condition": [
                                            {
                                                "column_name": "name",
                                                "condition": "IN",
                                                "input_value": str(tuple(group_list)).replace(",)", ")"),
                                                "and_or": "",
                                            }
                                        ],
                                    },
                                )
                            ).id.tolist()
                            if group_id:
                                user_ids = (
                                    read_data_func(
                                        request,
                                        {
                                            "inputs": {
                                                "Data_source": "Database",
                                                "Table": "user_groups",
                                                "Columns": ["user_id"],
                                            },
                                            "condition": [
                                                {
                                                    "column_name": "group_id",
                                                    "condition": "IN",
                                                    "input_value": str(tuple(group_id)).replace(",)", ")"),
                                                    "and_or": "",
                                                }
                                            ],
                                        },
                                    )
                                ).user_id.tolist()
                                if user_ids:
                                    to_bcc = (
                                        read_data_func(
                                            request,
                                            {
                                                "inputs": {
                                                    "Data_source": "Database",
                                                    "Table": "User",
                                                    "Columns": ["email"],
                                                },
                                                "condition": [
                                                    {
                                                        "column_name": "id",
                                                        "condition": "IN",
                                                        "input_value": str(tuple(user_ids)).replace(
                                                            ",)", ")"
                                                        ),
                                                        "and_or": "",
                                                    }
                                                ],
                                            },
                                        )
                                    ).email.tolist()
                                else:
                                    to_bcc = []
                            else:
                                to_bcc = []
                        else:
                            to_bcc = []
                    else:
                        to_bcc = []

                    approval_notification_attachment_config = condition_data_email_box_config["config"][
                        "attachmentConfig"
                    ]

                    if model_name1 and len(FinalData):
                        for field in model_name1.concrete_fields:
                            if field.name in tdata.columns and field.internal_type == "MultiselectField":
                                tdata = multi_select_id_to_value_converter(
                                    request, tdata, field.name, json.loads(field.mulsel_config)
                                )
                            elif (
                                field.name in tdata.columns
                                and field.internal_type == "FileField"
                                and str(tdata[field.name].iloc[0]) != "nan"
                                and approval_notification_attachment_config.get(
                                    "addUploadedFilesAsAttachment"
                                )
                                == "Yes"
                                and tdata[field.name].iloc[0] is not None
                            ):
                                file_names = tdata[field.name].iloc[0]
                                additional_attachment_file_names = {
                                    i: f"{MEDIA_ROOT}/uploaded_files/{i}" for i in file_names.split(", ")
                                }
                                approval_notification_attachment_config["additional_attachments"] = (
                                    additional_attachment_file_names
                                )
                            elif field.name in tdata.columns and field.internal_type == "ForeignKey":
                                tdata = fk_id_to_value_converter(request, tdata, field.name, field.parent)
                            elif field.name in tdata.columns and field.get_internal_type() == "RTFField":
                                if field.name in rtf_data_dict:
                                    tdata[field.name] = rtf_data_dict[field.name]
                            else:
                                continue

                    if len(FinalData):
                        if columnRenameList:
                            tdata2 = tdata.rename(columns=columnRenameList)
                            final_data_json_email_box[approval_code] = tdata2.to_json(orient="records")
                        else:
                            final_data_json_email_box[approval_code] = tdata.to_json(orient="records")
                    else:
                        final_data_json_email_box[approval_code] = "[]"

                    approval_notification_subject = condition_data_email_box_config["config"]["subject_email"]
                    smtpConfigKey = condition_data_email_box_config["config"]["from_email"]
                    content = condition_data_email_box_config["config"]["text_email"]

                    if len(FinalData):
                        transaction_data_dict = json.loads(tdata.to_json(orient="records"))[0]
                    else:
                        transaction_data_dict = {}

                    if approval_notification_subject:
                        if "{TransactionCreatedBy}" in approval_notification_subject:
                            approval_notification_subject = approval_notification_subject.replace(
                                "{TransactionCreatedBy}", request.user.username
                            )
                        else:
                            pass

                        if "{TransactionTime}" in approval_notification_subject:
                            approval_notification_subject = approval_notification_subject.replace(
                                "{TransactionTime}", f"{datetime.now()}"
                            )
                        else:
                            pass

                        if model_name1 and transaction_data_dict:
                            for field in model_name1.concrete_fields:
                                if f"VerboseName-{field.name}" in approval_notification_subject:
                                    approval_notification_subject = approval_notification_subject.replace(
                                        f"{{VerboseName-{field.name}}}", field.verbose_name
                                    )
                                else:
                                    pass
                                if f"Value-{field.name}" in approval_notification_subject:
                                    if field.name in transaction_data_dict:
                                        approval_notification_subject = approval_notification_subject.replace(
                                            f"{{Value-{field.name}}}", str(transaction_data_dict[field.name])
                                        )
                                    else:
                                        approval_notification_subject = approval_notification_subject.replace(
                                            f"{{Value-{field.name}}}", " - "
                                        )
                                else:
                                    continue

                    if "{TransactionCreatedBy}" in content:
                        content = content.replace("{TransactionCreatedBy}", request.user.username)
                    else:
                        pass
                    if "{TransactionCreatedBy-Name}" in content:
                        content = content.replace(
                            "{TransactionCreatedBy-Name}",
                            f"{request.user.first_name} {request.user.last_name}",
                        )
                    else:
                        pass
                    if "{TransactionTime}" in content:
                        content = content.replace("{TransactionTime}", f"{datetime.now()}")
                    else:
                        pass

                    if "{domain}" in content:
                        domain = request.build_absolute_uri("/")[:-1]
                        if request.scheme == "https":
                            domain = domain.replace("http", "https")
                        else:
                            pass
                        content = content.replace("{domain}", f"{domain}")
                    else:
                        pass
                    if "{app_code}" in content:
                        url_string = request.path
                        f_occ = url_string.find("/", url_string.find("/") + 1)
                        s_occ = url_string.find("/", url_string.find("/") + f_occ + 1)
                        app_code = url_string[f_occ + 1 : s_occ]
                        content = content.replace("{app_code}", f"{app_code}")
                    else:
                        pass

                    if model_name1:
                        for field in model_name1.concrete_fields:
                            if f"VerboseName-{field.name}" in content:
                                content = content.replace(f"{{VerboseName-{field.name}}}", field.verbose_name)
                            else:
                                pass
                            if f"Value-{field.name}" in content:
                                if field.name in transaction_data_dict:
                                    content = content.replace(
                                        f"{{Value-{field.name}}}", str(transaction_data_dict[field.name])
                                    )
                                else:
                                    content = content.replace(f"{{Value-{field.name}}}", " - ")
                            else:
                                continue

                    standardised_functions.send_approval_mail(
                        request,
                        tablename,
                        final_data_json_email_box,
                        to_list,
                        content,
                        subject=approval_notification_subject,
                        in_system_approval=False,
                        to_cc=to_cc,
                        to_bcc=to_bcc,
                        attachments_config=approval_notification_attachment_config,
                        smtpConfigKey=smtpConfigKey,
                    )

        elif condition_data_email_box_config["trigger_type"] == "schedule_based":

            scheduler_config = condition_data_email_box_config["config"]["scheduler_config"]
            final_data_json_email_box = {}

            approval_notification_attachment_config = condition_data_email_box_config["config"][
                "attachmentConfig"
            ]
            dynamic_user_filter = False
            dynamic_master_based_emails = False
            table_name = None
            table_cols = None
            table_cond = []
            underlying_table_name = None
            underlying_table_columns = None
            if approval_notification_attachment_config.get("additional_config"):
                if approval_notification_attachment_config["additional_config"].get("scheduler_data_config"):
                    table_name = approval_notification_attachment_config["additional_config"][
                        "scheduler_data_config"
                    ]["scheduler_table"]
                    table_cols = approval_notification_attachment_config["additional_config"][
                        "scheduler_data_config"
                    ]["scheduler_columns"]
                    if table_name == "ApprovalTable":
                        underlying_table_name = approval_notification_attachment_config["additional_config"][
                            "scheduler_data_config"
                        ]["scheduler_table_underlying"]
                        underlying_table_columns = approval_notification_attachment_config[
                            "additional_config"
                        ]["scheduler_data_config"]["scheduler_columns_underlying"]
                    else:
                        pass

                    if not table_cols:
                        table_cols = ["*"]
                    else:
                        if (
                            table_name == "ApprovalTable"
                            and underlying_table_name
                            and underlying_table_columns
                            and "json_data" not in table_cols
                        ):
                            table_cols.append("json_data")
                        else:
                            pass

                    if approval_notification_attachment_config["additional_config"][
                        "scheduler_data_config"
                    ].get("scheduler_filter"):
                        table_cond = approval_notification_attachment_config["additional_config"][
                            "scheduler_data_config"
                        ]["scheduler_filter"]
                        if table_cond:
                            for cond in table_cond:
                                if cond.get("table_name"):
                                    del cond["table_name"]
                                else:
                                    pass
                            for cond in table_cond:
                                if cond["current_value"] in ["curr_user", "curr_email"]:
                                    dynamic_user_filter = True
                                    break
                                else:
                                    continue
                        else:
                            pass
                    else:
                        table_cond = []

                    if condition_data_email_box_config["config"].get("to_config"):
                        if (
                            condition_data_email_box_config["config"]["to_config"]["to_recipient_type"]
                            == "dynamic_master_user"
                        ):
                            dynamic_master_based_emails = True
                        else:
                            pass
                    else:
                        pass

                    if not (dynamic_user_filter and dynamic_master_based_emails):
                        model_name1 = dynamic_model_create.get_model_class(table_name, request)
                        date_field = []
                        num_field = []

                        if table_cond:
                            FinalData = read_data_func(
                                request,
                                {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": table_name,
                                        "Columns": table_cols,
                                    },
                                    "condition": table_cond,
                                },
                            )
                        else:
                            FinalData = read_data_func(
                                request,
                                {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": table_name,
                                        "Columns": table_cols,
                                    },
                                    "condition": [],
                                },
                            )

                        if (
                            table_name == "ApprovalTable"
                            and "json_data" in FinalData.columns
                            and underlying_table_columns
                        ):
                            FinalData["json_data"] = FinalData["json_data"].apply(
                                lambda x: {
                                    i: v for i, v in json.loads(x)[0].items() if i in underlying_table_columns
                                }
                            )
                            underlying_table_data = FinalData["json_data"].tolist()
                            underlying_table_data = pd.DataFrame(underlying_table_data)
                            underlying_model_name = dynamic_model_create.get_model_class(
                                underlying_table_name, request
                            )
                            for field in underlying_model_name.concrete_fields:
                                if (
                                    field.name in underlying_table_data.columns
                                    and field.internal_type == "MultiselectField"
                                ):
                                    underlying_table_data = multi_select_id_to_value_converter(
                                        request,
                                        underlying_table_data,
                                        field.name,
                                        json.loads(field.mulsel_config),
                                    )
                                elif (
                                    field.name in underlying_table_data.columns
                                    and field.internal_type == "ForeignKey"
                                ):
                                    underlying_table_data = fk_id_to_value_converter(
                                        request, underlying_table_data, field.name, field.parent
                                    )
                                elif (
                                    field.name in underlying_table_data.columns
                                    and field.get_internal_type() == "RTFField"
                                ):
                                    if field.name in rtf_data_dict:
                                        underlying_table_data[field.name] = rtf_data_dict[field.name]
                                else:
                                    continue
                            FinalData.drop(columns=["json_data"], inplace=True)
                            FinalData = pd.concat([underlying_table_data, FinalData], axis=1)
                        else:
                            pass

                        tdata = FinalData

                        for field in model_name1.concrete_fields:
                            if field.get_internal_type() in ["DateField", "DateTimeField"]:
                                date_field.append(field.name)
                            elif field.get_internal_type() in ["IntField", "FloatField"]:
                                num_field.append(field.name)

                        for ii in date_field:
                            try:
                                if ii in ["modified_date", "created_date"]:
                                    tdata[ii] = pd.to_datetime(tdata[ii]).dt.strftime("%Y-%m-%d %H:%M:%S")
                                else:
                                    tdata[ii] = pd.to_datetime(tdata[ii]).dt.strftime("%Y-%m-%d")
                            except Exception as e:
                                logging.warning(f"Following exception occured - {e}")

                        for ii in num_field:
                            try:
                                tdata[ii] = pd.to_numeric(tdata[ii], errors="coerce").fillna(0)
                            except Exception as e:
                                logging.warning(f"Following exception occured - {e}")

                        if model_name1:
                            columnRenameList = {
                                field.name: field.verbose_name for field in model_name1.concrete_fields
                            }
                        else:
                            columnRenameList = {}

                        for field in model_name1.concrete_fields:
                            if field.name in tdata.columns and field.internal_type == "MultiselectField":
                                tdata = multi_select_id_to_value_converter(
                                    request, tdata, field.name, json.loads(field.mulsel_config)
                                )
                            elif (
                                field.name in tdata.columns
                                and field.internal_type == "FileField"
                                and str(tdata[field.name].iloc[0]) != "nan"
                                and approval_notification_attachment_config.get(
                                    "addUploadedFilesAsAttachment"
                                )
                                == "Yes"
                                and tdata[field.name].iloc[0] is not None
                            ):
                                file_names = tdata[field.name].iloc[0]
                                additional_attachment_file_names = {
                                    i: f"{MEDIA_ROOT}/uploaded_files/{i}" for i in file_names.split(", ")
                                }
                                approval_notification_attachment_config["additional_attachments"] = (
                                    additional_attachment_file_names
                                )
                            elif field.name in tdata.columns and field.internal_type == "ForeignKey":
                                tdata = fk_id_to_value_converter(request, tdata, field.name, field.parent)
                            elif field.name in tdata.columns and field.get_internal_type() == "RTFField":
                                if field.name in rtf_data_dict:
                                    tdata[field.name] = rtf_data_dict[field.name]
                            else:
                                continue
                    else:
                        FinalData = pd.DataFrame()
                else:
                    FinalData = pd.DataFrame()
            else:
                FinalData = pd.DataFrame()

            approval_code = standardised_functions.random_generator("alphanum", 32)

            if condition_data_email_box_config["config"].get("to_config"):
                if condition_data_email_box_config["config"]["to_config"]["to_recipient_type"] == "static":
                    to_list = condition_data_email_box_config["config"]["to_config"]["to_recipient_list"]
                elif condition_data_email_box_config["config"]["to_config"][
                    "to_recipient_type"
                ] == "dynamic" and len(FinalData):
                    t_tname = condition_data_email_box_config["config"]["to_config"][
                        "to_recipient_dynamic_table"
                    ]
                    t_tcol = condition_data_email_box_config["config"]["to_config"][
                        "to_recipient_dynamic_column"
                    ]

                    model_class = dynamic_model_create.get_model_class(t_tname, request)

                    interim_value = tdata[t_tcol].values[0]
                    if model_class.get_field(t_tcol).get_internal_type() == "MultiselectField":
                        if (
                            interim_value
                            and interim_value not in ["nan", "NaT", pd.NaT, np.nan, "None", None, " ", "<NA>"]
                            and not pd.isna(interim_value)
                        ):
                            field_multiselect_config = json.loads(model_class.get_field(t_tcol).mulsel_config)
                            multi_select_table = field_multiselect_config["value"][0]
                            multi_select_master_column = field_multiselect_config["masterColumn"][0]
                            interim_value = list(json.loads(interim_value).keys())
                            converted_value = read_data_func(
                                request,
                                {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": multi_select_table,
                                        "Columns": [multi_select_master_column],
                                    },
                                    "condition": [
                                        {
                                            "column_name": "id",
                                            "condition": "IN",
                                            "input_value": interim_value,
                                            "and_or": "",
                                        }
                                    ],
                                },
                            )[multi_select_master_column].tolist()
                            to_list = converted_value
                        else:
                            to_list = []
                    else:
                        if isinstance(tdata[t_tcol].iloc[0], list):
                            to_list = tdata[t_tcol].iloc[0]
                        else:
                            to_list = [tdata[t_tcol].iloc[0]]

                elif (
                    condition_data_email_box_config["config"]["to_config"]["to_recipient_type"]
                    == "dynamic_master_user"
                ):
                    t_tname = condition_data_email_box_config["config"]["to_config"][
                        "to_recipient_dynamic_table"
                    ]
                    t_tcol = condition_data_email_box_config["config"]["to_config"][
                        "to_recipient_dynamic_column"
                    ]

                    model_class = dynamic_model_create.get_model_class(t_tname, request)

                    interim_value = (
                        (
                            read_data_func(
                                request,
                                {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": t_tname,
                                        "Columns": [t_tcol],
                                        "Agg_Type": "DISTINCT",
                                    },
                                    "condition": [],
                                },
                            )
                        )
                        .dropna()[t_tcol]
                        .tolist()
                    )
                    if interim_value:
                        to_list = (
                            (
                                read_data_func(
                                    request,
                                    {
                                        "inputs": {
                                            "Data_source": "Database",
                                            "Table": "User",
                                            "Columns": ["username", "email"],
                                        },
                                        "condition": [
                                            {
                                                "column_name": "username",
                                                "condition": "IN",
                                                "input_value": interim_value,
                                                "and_or": "",
                                            }
                                        ],
                                    },
                                )
                            )
                            .set_index("username")["email"]
                            .to_dict()
                        )
                    else:
                        to_list = {}

                elif (
                    condition_data_email_box_config["config"]["to_config"]["to_recipient_type"]
                    == "dynamic_user"
                ):
                    to_list = [request.user.email]
                elif (
                    condition_data_email_box_config["config"]["to_config"]["to_recipient_type"]
                    == "static_user"
                ):
                    user_list = condition_data_email_box_config["config"]["to_config"]["to_recipient_list"]
                    to_list = (
                        read_data_func(
                            request,
                            {
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": "User",
                                    "Columns": ["email"],
                                },
                                "condition": [
                                    {
                                        "column_name": "username",
                                        "condition": "IN",
                                        "input_value": str(tuple(user_list)).replace(",)", ")"),
                                        "and_or": "",
                                    }
                                ],
                            },
                        )
                    ).email.tolist()
                elif (
                    condition_data_email_box_config["config"]["to_config"]["to_recipient_type"]
                    == "static_groups"
                ):
                    group_list = condition_data_email_box_config["config"]["to_config"]["to_recipient_list"]
                    group_id = (
                        read_data_func(
                            request,
                            {
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": "group_details",
                                    "Columns": ["id"],
                                },
                                "condition": [
                                    {
                                        "column_name": "name",
                                        "condition": "IN",
                                        "input_value": str(tuple(group_list)).replace(",)", ")"),
                                        "and_or": "",
                                    }
                                ],
                            },
                        )
                    ).id.tolist()
                    if group_id:
                        user_ids = (
                            read_data_func(
                                request,
                                {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": "user_groups",
                                        "Columns": ["user_id"],
                                    },
                                    "condition": [
                                        {
                                            "column_name": "group_id",
                                            "condition": "IN",
                                            "input_value": str(tuple(group_id)).replace(",)", ")"),
                                            "and_or": "",
                                        }
                                    ],
                                },
                            )
                        ).user_id.tolist()
                        if user_ids:
                            to_list = (
                                read_data_func(
                                    request,
                                    {
                                        "inputs": {
                                            "Data_source": "Database",
                                            "Table": "User",
                                            "Columns": ["email"],
                                        },
                                        "condition": [
                                            {
                                                "column_name": "id",
                                                "condition": "IN",
                                                "input_value": str(tuple(user_ids)).replace(",)", ")"),
                                                "and_or": "",
                                            }
                                        ],
                                    },
                                )
                            ).email.tolist()
                        else:
                            to_list = []
                    else:
                        to_list = []
                else:
                    to_list = []
            else:
                to_list = []

            if condition_data_email_box_config["config"].get("to_config_cc"):
                if condition_data_email_box_config["config"]["to_config_cc"]["to_recipient_type"] == "static":
                    to_cc = condition_data_email_box_config["config"]["to_config_cc"]["to_recipient_list"]
                elif condition_data_email_box_config["config"]["to_config_cc"][
                    "to_recipient_type"
                ] == "dynamic" and len(FinalData):
                    t_tname = condition_data_email_box_config["config"]["to_config_cc"][
                        "to_recipient_dynamic_table"
                    ]
                    t_tcol = condition_data_email_box_config["config"]["to_config_cc"][
                        "to_recipient_dynamic_column"
                    ]

                    model_class = dynamic_model_create.get_model_class(t_tname, request)

                    interim_value = tdata[t_tcol].values[0]
                    if model_class.get_field(t_tcol).get_internal_type() == "MultiselectField":
                        if (
                            interim_value
                            and interim_value not in ["nan", "NaT", pd.NaT, np.nan, "None", None, " ", "<NA>"]
                            and not pd.isna(interim_value)
                        ):
                            field_multiselect_config = json.loads(model_class.get_field(t_tcol).mulsel_config)
                            multi_select_table = field_multiselect_config["value"][0]
                            multi_select_master_column = field_multiselect_config["masterColumn"][0]
                            interim_value = list(json.loads(interim_value).keys())
                            converted_value = read_data_func(
                                request,
                                {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": multi_select_table,
                                        "Columns": [multi_select_master_column],
                                    },
                                    "condition": [
                                        {
                                            "column_name": "id",
                                            "condition": "IN",
                                            "input_value": interim_value,
                                            "and_or": "",
                                        }
                                    ],
                                },
                            )[multi_select_master_column].tolist()
                            to_cc = converted_value
                        else:
                            to_cc = []
                    else:
                        if isinstance(tdata[t_tcol].iloc[0], list):
                            to_cc = tdata[t_tcol].iloc[0]
                        else:
                            to_cc = [tdata[t_tcol].iloc[0]]
                elif (
                    condition_data_email_box_config["config"]["to_config_cc"]["to_recipient_type"]
                    == "dynamic_master_user"
                ):
                    t_tname = condition_data_email_box_config["config"]["to_config_cc"][
                        "to_recipient_dynamic_table"
                    ]
                    t_tcol = condition_data_email_box_config["config"]["to_config_cc"][
                        "to_recipient_dynamic_column"
                    ]

                    model_class = dynamic_model_create.get_model_class(t_tname, request)

                    interim_value = (
                        (
                            read_data_func(
                                request,
                                {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": t_tname,
                                        "Columns": [t_tcol],
                                        "Agg_Type": "DISTINCT",
                                    },
                                    "condition": [],
                                },
                            )
                        )
                        .dropna()[t_tcol]
                        .tolist()
                    )
                    if interim_value:
                        to_list_cc = (
                            read_data_func(
                                request,
                                {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": "User",
                                        "Columns": ["email"],
                                    },
                                    "condition": [
                                        {
                                            "column_name": "username",
                                            "condition": "IN",
                                            "input_value": interim_value,
                                            "and_or": "",
                                        }
                                    ],
                                },
                            )
                        )["email"].tolist()
                    else:
                        to_list_cc = {}

                elif (
                    condition_data_email_box_config["config"]["to_config_cc"]["to_recipient_type"]
                    == "dynamic_user"
                ):
                    to_cc = [request.user.email]
                elif (
                    condition_data_email_box_config["config"]["to_config_cc"]["to_recipient_type"]
                    == "static_user"
                ):
                    user_list = condition_data_email_box_config["config"]["to_config_cc"]["to_recipient_list"]
                    to_cc = (
                        read_data_func(
                            request,
                            {
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": "User",
                                    "Columns": ["email"],
                                },
                                "condition": [
                                    {
                                        "column_name": "username",
                                        "condition": "IN",
                                        "input_value": str(tuple(user_list)).replace(",)", ")"),
                                        "and_or": "",
                                    }
                                ],
                            },
                        )
                    ).email.tolist()
                elif (
                    condition_data_email_box_config["config"]["to_config_cc"]["to_recipient_type"]
                    == "static_groups"
                ):
                    group_list = condition_data_email_box_config["config"]["to_config_cc"][
                        "to_recipient_list"
                    ]
                    group_id = (
                        read_data_func(
                            request,
                            {
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": "group_details",
                                    "Columns": ["id"],
                                },
                                "condition": [
                                    {
                                        "column_name": "name",
                                        "condition": "IN",
                                        "input_value": str(tuple(group_list)).replace(",)", ")"),
                                        "and_or": "",
                                    }
                                ],
                            },
                        )
                    ).id.tolist()
                    if group_id:
                        user_ids = (
                            read_data_func(
                                request,
                                {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": "user_groups",
                                        "Columns": ["user_id"],
                                    },
                                    "condition": [
                                        {
                                            "column_name": "group_id",
                                            "condition": "IN",
                                            "input_value": str(tuple(group_id)).replace(",)", ")"),
                                            "and_or": "",
                                        }
                                    ],
                                },
                            )
                        ).user_id.tolist()
                        if user_ids:
                            to_cc = (
                                read_data_func(
                                    request,
                                    {
                                        "inputs": {
                                            "Data_source": "Database",
                                            "Table": "User",
                                            "Columns": ["email"],
                                        },
                                        "condition": [
                                            {
                                                "column_name": "id",
                                                "condition": "IN",
                                                "input_value": str(tuple(user_ids)).replace(",)", ")"),
                                                "and_or": "",
                                            }
                                        ],
                                    },
                                )
                            ).email.tolist()
                        else:
                            to_cc = []
                    else:
                        to_cc = []
                else:
                    to_cc = []
            else:
                to_cc = []

            if condition_data_email_box_config["config"].get("to_config_bcc"):
                if (
                    condition_data_email_box_config["config"]["to_config_bcc"]["to_recipient_type"]
                    == "static"
                ):
                    to_bcc = condition_data_email_box_config["config"]["to_config_bcc"]["to_recipient_list"]
                elif condition_data_email_box_config["config"]["to_config_bcc"][
                    "to_recipient_type"
                ] == "dynamic" and len(FinalData):
                    t_tname = condition_data_email_box_config["config"]["to_config_bcc"][
                        "to_recipient_dynamic_table"
                    ]
                    t_tcol = condition_data_email_box_config["config"]["to_config_bcc"][
                        "to_recipient_dynamic_column"
                    ]

                    model_class = dynamic_model_create.get_model_class(t_tname, request)

                    interim_value = tdata[t_tcol].values[0]
                    if model_class.get_field(t_tcol).get_internal_type() == "MultiselectField":
                        if (
                            interim_value
                            and interim_value not in ["nan", "NaT", pd.NaT, np.nan, "None", None, " ", "<NA>"]
                            and not pd.isna(interim_value)
                        ):
                            field_multiselect_config = json.loads(model_class.get_field(t_tcol).mulsel_config)
                            multi_select_table = field_multiselect_config["value"][0]
                            multi_select_master_column = field_multiselect_config["masterColumn"][0]
                            interim_value = list(json.loads(interim_value).keys())
                            converted_value = read_data_func(
                                request,
                                {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": multi_select_table,
                                        "Columns": [multi_select_master_column],
                                    },
                                    "condition": [
                                        {
                                            "column_name": "id",
                                            "condition": "IN",
                                            "input_value": interim_value,
                                            "and_or": "",
                                        }
                                    ],
                                },
                            )[multi_select_master_column].tolist()
                            to_bcc = converted_value
                        else:
                            to_bcc = []
                    else:
                        if isinstance(tdata[t_tcol].iloc[0], list):
                            to_bcc = tdata[t_tcol].iloc[0]
                        else:
                            to_bcc = [tdata[t_tcol].iloc[0]]
                elif (
                    condition_data_email_box_config["config"]["to_config_bcc"]["to_recipient_type"]
                    == "dynamic_master_user"
                ):
                    t_tname = condition_data_email_box_config["config"]["to_config_bcc"][
                        "to_recipient_dynamic_table"
                    ]
                    t_tcol = condition_data_email_box_config["config"]["to_config_bcc"][
                        "to_recipient_dynamic_column"
                    ]

                    model_class = dynamic_model_create.get_model_class(t_tname, request)

                    interim_value = (
                        (
                            read_data_func(
                                request,
                                {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": t_tname,
                                        "Columns": [t_tcol],
                                        "Agg_Type": "DISTINCT",
                                    },
                                    "condition": [],
                                },
                            )
                        )
                        .dropna()[t_tcol]
                        .tolist()
                    )
                    if interim_value:
                        to_list_bcc = (
                            read_data_func(
                                request,
                                {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": "User",
                                        "Columns": ["email"],
                                    },
                                    "condition": [
                                        {
                                            "column_name": "username",
                                            "condition": "IN",
                                            "input_value": interim_value,
                                            "and_or": "",
                                        }
                                    ],
                                },
                            )
                        )["email"].tolist()
                    else:
                        to_list_bcc = {}

                elif (
                    condition_data_email_box_config["config"]["to_config_bcc"]["to_recipient_type"]
                    == "dynamic_user"
                ):
                    to_bcc = [request.user.email]
                elif (
                    condition_data_email_box_config["config"]["to_config_bcc"]["to_recipient_type"]
                    == "static_user"
                ):
                    user_list = condition_data_email_box_config["config"]["to_config_bcc"][
                        "to_recipient_list"
                    ]
                    to_bcc = (
                        read_data_func(
                            request,
                            {
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": "User",
                                    "Columns": ["email"],
                                },
                                "condition": [
                                    {
                                        "column_name": "username",
                                        "condition": "IN",
                                        "input_value": str(tuple(user_list)).replace(",)", ")"),
                                        "and_or": "",
                                    }
                                ],
                            },
                        )
                    ).email.tolist()
                elif (
                    condition_data_email_box_config["config"]["to_config_bcc"]["to_recipient_type"]
                    == "static_groups"
                ):
                    group_list = condition_data_email_box_config["config"]["to_config_bcc"][
                        "to_recipient_list"
                    ]
                    group_id = (
                        read_data_func(
                            request,
                            {
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": "group_details",
                                    "Columns": ["id"],
                                },
                                "condition": [
                                    {
                                        "column_name": "name",
                                        "condition": "IN",
                                        "input_value": str(tuple(group_list)).replace(",)", ")"),
                                        "and_or": "",
                                    }
                                ],
                            },
                        )
                    ).id.tolist()
                    if group_id:
                        user_ids = (
                            read_data_func(
                                request,
                                {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": "user_groups",
                                        "Columns": ["user_id"],
                                    },
                                    "condition": [
                                        {
                                            "column_name": "group_id",
                                            "condition": "IN",
                                            "input_value": str(tuple(group_id)).replace(",)", ")"),
                                            "and_or": "",
                                        }
                                    ],
                                },
                            )
                        ).user_id.tolist()
                        if user_ids:
                            to_bcc = (
                                read_data_func(
                                    request,
                                    {
                                        "inputs": {
                                            "Data_source": "Database",
                                            "Table": "User",
                                            "Columns": ["email"],
                                        },
                                        "condition": [
                                            {
                                                "column_name": "id",
                                                "condition": "IN",
                                                "input_value": str(tuple(user_ids)).replace(",)", ")"),
                                                "and_or": "",
                                            }
                                        ],
                                    },
                                )
                            ).email.tolist()
                        else:
                            to_bcc = []
                    else:
                        to_bcc = []
                else:
                    to_bcc = []
            else:
                to_bcc = []

            if len(FinalData):
                if columnRenameList:
                    tdata2 = tdata.rename(columns=columnRenameList)
                    final_data_json_email_box[approval_code] = tdata2.to_json(orient="records")
                else:
                    final_data_json_email_box[approval_code] = tdata.to_json(orient="records")
            else:
                final_data_json_email_box[approval_code] = "[]"

            if len(FinalData):
                transaction_data_dict = json.loads(tdata.to_json(orient="records"))[0]
            else:
                transaction_data_dict = {}

            approval_notification_subject = condition_data_email_box_config["config"]["subject_email"]
            smtpConfigKey = condition_data_email_box_config["config"]["from_email"]
            content = condition_data_email_box_config["config"]["text_email"]

            skip_if_no_dynamic_data = condition_data_email_box_config["config"].get(
                "skip_if_no_dynamic_data", False
            )

            if approval_notification_subject:
                if (
                    condition_data_email_box_config["config"]["to_config"]["to_recipient_type"]
                    == "static_user"
                ):
                    user_list = condition_data_email_box_config["config"]["to_config"]["to_recipient_list"]
                    if "{RecipientOfMail}" in approval_notification_subject:
                        approval_notification_subject = approval_notification_subject.replace(
                            "{RecipientOfMail}", ", ".join(user_list)
                        )
                elif (
                    condition_data_email_box_config["config"]["to_config"]["to_recipient_type"]
                    == "static_groups"
                ):
                    group_list = condition_data_email_box_config["config"]["to_config"]["to_recipient_list"]
                    if "{RecipientOfMail}" in approval_notification_subject:
                        approval_notification_subject = approval_notification_subject.replace(
                            "{RecipientOfMail}", ", ".join(group_list)
                        )
                else:
                    if "{RecipientOfMail}" in approval_notification_subject:
                        approval_notification_subject = approval_notification_subject.replace(
                            "{RecipientOfMail}", request.user.username
                        )
                    else:
                        pass

                if "{TransactionTime}" in approval_notification_subject:
                    approval_notification_subject = approval_notification_subject.replace(
                        "{TransactionTime}", f"{datetime.now()}"
                    )
                else:
                    pass

            if condition_data_email_box_config["config"]["to_config"]["to_recipient_type"] == "static_user":
                user_list = condition_data_email_box_config["config"]["to_config"]["to_recipient_list"]
                if "{TransactionCreatedBy}" in content:
                    content = content.replace("{TransactionCreatedBy}", ", ".join(user_list))
            if condition_data_email_box_config["config"]["to_config"]["to_recipient_type"] == "static_groups":
                group_list = condition_data_email_box_config["config"]["to_config"]["to_recipient_list"]
                if "{TransactionCreatedBy}" in content:
                    content = content.replace("{TransactionCreatedBy}", ", ".join(group_list))
            if "{TransactionCreatedBy}" in content:
                content = content.replace("{TransactionCreatedBy}", request.user.username)
            else:
                pass
            if "{TransactionCreatedBy-Name}" in content:
                content = content.replace(
                    "{TransactionCreatedBy-Name}", f"{request.user.first_name} {request.user.last_name}"
                )
            else:
                pass
            if "{TransactionTime}" in content:
                content = content.replace("{TransactionTime}", f"{datetime.now()}")
            else:
                pass

            if transaction_data_dict:
                for field in model_name1.concrete_fields:
                    if f"VerboseName-{field.name}" in content:
                        content = content.replace(f"{{VerboseName-{field.name}}}", field.verbose_name)
                    else:
                        pass
                    if f"Value-{field.name}" in content:
                        if field.name in transaction_data_dict:
                            content = content.replace(
                                f"{{Value-{field.name}}}", str(transaction_data_dict[field.name])
                            )
                        else:
                            content = content.replace(f"{{Value-{field.name}}}", " - ")
                    else:
                        continue
            if isinstance(to_list, dict):
                for u_name, u_email in to_list.items():
                    if dynamic_user_filter and dynamic_master_based_emails:
                        condition_list = table_cond.copy()
                        for idx, cond in enumerate(condition_list):
                            if cond["current_value"] == "curr_user":
                                condition_list[idx]["input_value"] = u_name
                            elif cond["current_value"] == "curr_email":
                                condition_list[idx]["input_value"] = u_email
                            elif cond["current_value"] == "curr_date":
                                condition_list[idx]["input_value"] = date.today().strftime("%Y-%m-%d")
                            elif cond["current_value"] == "curr_datetime":
                                condition_list[idx]["input_value"] = datetime.now().strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                )
                            else:
                                continue
                        model_name1 = dynamic_model_create.get_model_class(table_name, request)
                        date_field = []
                        num_field = []
                        FinalData = read_data_func(
                            request,
                            {
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": table_name,
                                    "Columns": table_cols,
                                },
                                "condition": condition_list,
                            },
                        )

                        if not FinalData.empty:
                            if (
                                table_name == "ApprovalTable"
                                and "json_data" in FinalData.columns
                                and underlying_table_columns
                            ):
                                FinalData["json_data"] = FinalData["json_data"].apply(
                                    lambda x: {
                                        i: v
                                        for i, v in json.loads(x)[0].items()
                                        if i in underlying_table_columns
                                    }
                                )
                                underlying_table_data = FinalData["json_data"].tolist()
                                underlying_table_data = pd.DataFrame(underlying_table_data)
                                underlying_model_name = dynamic_model_create.get_model_class(
                                    underlying_table_name, request
                                )
                                for field in underlying_model_name.concrete_fields:
                                    if (
                                        field.name in underlying_table_data.columns
                                        and field.internal_type == "MultiselectField"
                                    ):
                                        underlying_table_data = multi_select_id_to_value_converter(
                                            request,
                                            underlying_table_data,
                                            field.name,
                                            json.loads(field.mulsel_config),
                                        )
                                    elif (
                                        field.name in underlying_table_data.columns
                                        and field.internal_type == "ForeignKey"
                                    ):
                                        underlying_table_data = fk_id_to_value_converter(
                                            request, underlying_table_data, field.name, field.parent
                                        )
                                    elif (
                                        field.name in underlying_table_data.columns
                                        and field.get_internal_type() == "RTFField"
                                    ):
                                        if field.name in rtf_data_dict:
                                            underlying_table_data[field.name] = rtf_data_dict[field.name]
                                    else:
                                        continue
                                FinalData.drop(columns=["json_data"], inplace=True)
                                FinalData = pd.concat([underlying_table_data, FinalData], axis=1)
                            else:
                                pass
                        else:
                            if skip_if_no_dynamic_data:
                                continue
                            else:
                                pass

                        tdata = FinalData

                        for field in model_name1.concrete_fields:
                            if field.get_internal_type() in ["DateField", "DateTimeField"]:
                                date_field.append(field.name)
                            elif field.get_internal_type() in ["IntField", "FloatField"]:
                                num_field.append(field.name)

                        for ii in date_field:
                            try:
                                if ii in ["modified_date", "created_date"]:
                                    tdata[ii] = pd.to_datetime(tdata[ii]).dt.strftime("%Y-%m-%d %H:%M:%S")
                                else:
                                    tdata[ii] = pd.to_datetime(tdata[ii]).dt.strftime("%Y-%m-%d")
                            except Exception as e:
                                logging.warning(f"Following exception occured - {e}")

                        for ii in num_field:
                            try:
                                tdata[ii] = pd.to_numeric(tdata[ii], errors="coerce").fillna(0)
                            except Exception as e:
                                logging.warning(f"Following exception occured - {e}")

                        if model_name1:
                            columnRenameList = {
                                field.name: field.verbose_name for field in model_name1.concrete_fields
                            }
                        else:
                            columnRenameList = {}

                        for field in model_name1.concrete_fields:
                            if field.name in tdata.columns and field.internal_type == "MultiselectField":
                                tdata = multi_select_id_to_value_converter(
                                    request, tdata, field.name, json.loads(field.mulsel_config)
                                )
                            elif (
                                field.name in tdata.columns
                                and field.internal_type == "FileField"
                                and str(tdata[field.name].iloc[0]) != "nan"
                                and approval_notification_attachment_config.get(
                                    "addUploadedFilesAsAttachment"
                                )
                                == "Yes"
                                and tdata[field.name].iloc[0] is not None
                            ):
                                file_names = tdata[field.name].iloc[0]
                                additional_attachment_file_names = {
                                    i: f"{MEDIA_ROOT}/uploaded_files/{i}" for i in file_names.split(", ")
                                }
                                approval_notification_attachment_config["additional_attachments"] = (
                                    additional_attachment_file_names
                                )
                            elif field.name in tdata.columns and field.internal_type == "ForeignKey":
                                tdata = fk_id_to_value_converter(request, tdata, field.name, field.parent)
                            elif field.name in tdata.columns and field.get_internal_type() == "RTFField":
                                if field.name in rtf_data_dict:
                                    tdata[field.name] = rtf_data_dict[field.name]
                            else:
                                continue
                        if len(FinalData):
                            if columnRenameList:
                                tdata2 = tdata.rename(columns=columnRenameList)
                                final_data_json_email_box[approval_code] = tdata2.to_json(orient="records")
                            else:
                                final_data_json_email_box[approval_code] = tdata.to_json(orient="records")
                        else:
                            final_data_json_email_box[approval_code] = "[]"
                    else:
                        pass

                    standardised_functions.send_approval_mail(
                        request,
                        tablename,
                        final_data_json_email_box,
                        [u_email],
                        content,
                        subject=approval_notification_subject,
                        in_system_approval=False,
                        to_cc=to_cc,
                        to_bcc=to_bcc,
                        attachments_config=approval_notification_attachment_config,
                        smtpConfigKey=smtpConfigKey,
                    )
            else:
                standardised_functions.send_approval_mail(
                    request,
                    tablename,
                    final_data_json_email_box,
                    to_list,
                    content,
                    subject=approval_notification_subject,
                    in_system_approval=False,
                    to_cc=to_cc,
                    to_bcc=to_bcc,
                    attachments_config=approval_notification_attachment_config,
                    smtpConfigKey=smtpConfigKey,
                )

        elif condition_data_email_box_config["trigger_type"] == "recurrence_based":
            if (
                action in condition_data_email_box_config["config"]["trigger_email_for"]
                or len(condition_data_email_box_config["config"]["trigger_email_for"]) == 0
            ):

                scheduler_config = condition_data_email_box_config["config"]["scheduler_config"]
                start_date = datetime.strptime(scheduler_config["start_date"], "%Y-%m-%d")
                duration = scheduler_config["duration"]
                if duration == "Monthly":
                    day = start_date.day
                    month = "*"
                    day_of_week = "*"
                elif duration == "Monthly/5th day":
                    day = "5"
                    month = "*"
                    day_of_week = "*"
                elif duration == "Quarterly":
                    day = start_date.day
                    month = "1,4,7,10"
                    day_of_week = "*"
                elif duration == "Pre-Quarterly":
                    day = "24"
                    month = "12,3,6,9"
                    day_of_week = "*"
                elif duration == "Weekly":
                    day_of_week = start_date.weekday()
                    month = "*"
                    day = "*"
                elif duration == "Daily":
                    month = "*"
                    day = "*"
                    day_of_week = "*"
                elif duration == "Yearly":
                    month = start_date.month
                    day = start_date.day
                    day_of_week = "*"
                time_var = scheduler_config["time_interval"]
                if time_var.split(":")[0][0] == "0":
                    hour = literal_eval(time_var.split(":")[0][1])
                else:
                    hour = literal_eval(time_var.split(":")[0])
                if time_var.split(":")[1][0] == "0":
                    minute = literal_eval(time_var.split(":")[1][1])
                else:
                    minute = literal_eval(time_var.split(":")[1])

                func = "recurrence_send_mail"
                job_id = (
                    child_element_id_email_box
                    + "-"
                    + standardised_functions.random_no_generator()
                    + "-recurrenceEmailBox-"
                    + tablename
                )

                scheduler = Scheduler(connection=redis_instance_scheduler)

                def request_to_dict(request):
                    user_dict = request.user.__class__.objects.filter(pk=request.user.id).values().first()
                    request2 = {"path": request.path, "host": request.get_host(), "user": user_dict}
                    return request2

                request = request_to_dict(request)
                scheduler.cancel(job_id)
                scheduler.cron(
                    f"{minute} {hour} {day} {month} {day_of_week}",
                    func=eval(func),
                    id=f"{job_id}",
                    args=[request, f"{job_id}", {}, "recurr_only"],
                    repeat=None,
                )

    return None


def recurrence_send_mail(request, elementID, transaction_dict, recurr_type, rtf_data_dict={}):
    if isinstance(request, dict):

        class AttrDict:
            def __init__(self, i_dict):
                for key, value in i_dict.items():
                    if key not in ["password", "last_login", "date_joined"]:
                        setattr(self, key, value)
                if i_dict.get("username"):
                    setattr(self, "is_anonymous", False)
                else:
                    setattr(self, "is_anonymous", True)

            def get_host(self):
                return self.host

        request["user"] = AttrDict(request["user"])
        request = AttrDict(request)

    elementID2 = elementID.split("-")[0]
    tablename = elementID.split("-")[-1]

    model_name1 = dynamic_model_create.get_model_class(tablename, request)

    transaction_data = pd.DataFrame([transaction_dict])
    condition_data_email_box = read_data_func(
        request,
        {
            "inputs": {
                "Data_source": "Database",
                "Table": "TabScreens",
                "Columns": ["tab_body_content"],
            },
            "condition": [
                {
                    "column_name": "element_id",
                    "condition": "Equal to",
                    "input_value": elementID2,
                    "and_or": "",
                },
            ],
        },
    )

    attachment_data = pd.DataFrame()

    if len(condition_data_email_box) > 0:
        condition_data_email_box_config = json.loads(condition_data_email_box["tab_body_content"].iloc[0])

        final_data_json_email_box = {}
        approval_notification_attachment_config = condition_data_email_box_config["config"][
            "attachmentConfig"
        ]

        if approval_notification_attachment_config.get("additional_config"):
            if approval_notification_attachment_config["additional_config"].get("scheduler_data_config"):
                table_name = approval_notification_attachment_config["additional_config"][
                    "scheduler_data_config"
                ]["scheduler_table"]
                table_cols = approval_notification_attachment_config["additional_config"][
                    "scheduler_data_config"
                ]["scheduler_columns"]
                if not table_cols:
                    table_cols = ["*"]
                if approval_notification_attachment_config["additional_config"]["scheduler_data_config"].get(
                    "scheduler_filter"
                ):
                    table_cond = approval_notification_attachment_config["additional_config"][
                        "scheduler_data_config"
                    ]["scheduler_filter"]
                else:
                    table_cond = []

                model_name_1 = dynamic_model_create.get_model_class(table_name, request)
                date_field = []
                num_field = []

                if table_cond:
                    FinalData = read_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": table_name,
                                "Columns": table_cols,
                            },
                            "condition": table_cond,
                        },
                    )
                else:
                    FinalData = read_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": table_name,
                                "Columns": table_cols,
                            },
                            "condition": [],
                        },
                    )

                if recurr_type == "recurr_only":
                    transaction_data = FinalData
                    attachment_data = FinalData
                else:
                    attachment_data = FinalData

                for field in model_name_1.concrete_fields:
                    if field.get_internal_type() in ["DateField", "DateTimeField"]:
                        date_field.append(field.name)
                    elif field.get_internal_type() in ["IntField", "FloatField"]:
                        num_field.append(field.name)

                for ii in date_field:
                    try:
                        if ii in ["modified_date", "created_date"]:
                            attachment_data[ii] = pd.to_datetime(attachment_data[ii]).dt.strftime(
                                "%Y-%m-%d %H:%M:%S"
                            )
                        else:
                            attachment_data[ii] = pd.to_datetime(attachment_data[ii]).dt.strftime("%Y-%m-%d")
                    except Exception as e:
                        logging.warning(f"Following exception occured - {e}")

                for ii in num_field:
                    try:
                        attachment_data[ii] = pd.to_numeric(attachment_data[ii], errors="coerce").fillna(0)
                    except Exception as e:
                        logging.warning(f"Following exception occured - {e}")

                if model_name_1:
                    columnRenameList = {
                        field.name: field.verbose_name for field in model_name_1.concrete_fields
                    }
                else:
                    columnRenameList = {}

                for field in model_name_1.concrete_fields:
                    if field.name in attachment_data.columns and field.internal_type == "MultiselectField":
                        attachment_data = multi_select_id_to_value_converter(
                            request, attachment_data, field.name, json.loads(field.mulsel_config)
                        )
                    elif (
                        field.name in attachment_data.columns
                        and field.internal_type == "FileField"
                        and str(attachment_data[field.name].iloc[0]) != "nan"
                        and approval_notification_attachment_config.get("addUploadedFilesAsAttachment")
                        == "Yes"
                        and attachment_data[field.name].iloc[0] is not None
                    ):
                        file_names = attachment_data[field.name].iloc[0]
                        additional_attachment_file_names = {
                            i: f"{MEDIA_ROOT}/uploaded_files/{i}" for i in file_names.split(", ")
                        }
                        approval_notification_attachment_config["additional_attachments"] = (
                            additional_attachment_file_names
                        )
                    elif field.name in attachment_data.columns and field.internal_type == "ForeignKey":
                        attachment_data = fk_id_to_value_converter(
                            request, attachment_data, field.name, field.parent
                        )
                    elif field.name in attachment_data.columns and field.get_internal_type() == "RTFField":
                        if field.name in rtf_data_dict:
                            attachment_data[field.name] = rtf_data_dict[field.name]
                    else:
                        continue
            else:
                FinalData = pd.DataFrame()
                if recurr_type == "recurr_only":
                    transaction_data = FinalData
                    attachment_data = FinalData
                else:
                    attachment_data = FinalData
        else:
            FinalData = pd.DataFrame()
            if recurr_type == "recurr_only":
                transaction_data = FinalData
                attachment_data = FinalData
            else:
                attachment_data = FinalData

        approval_code = standardised_functions.random_generator("alphanum", 32)

        if condition_data_email_box_config["config"].get("to_config"):
            if condition_data_email_box_config["config"]["to_config"]["to_recipient_type"] == "static":
                to_list = condition_data_email_box_config["config"]["to_config"]["to_recipient_list"]
            elif condition_data_email_box_config["config"]["to_config"][
                "to_recipient_type"
            ] == "dynamic" and len(transaction_data):
                t_tname = condition_data_email_box_config["config"]["to_config"]["to_recipient_dynamic_table"]
                t_tcol = condition_data_email_box_config["config"]["to_config"]["to_recipient_dynamic_column"]

                model_class = dynamic_model_create.get_model_class(t_tname, request)

                if recurr_type == "recurr_only":
                    interim_value = attachment_data[t_tcol].values[0]
                else:
                    interim_value = transaction_data[t_tcol].values[0]

                if model_class.get_field(t_tcol).get_internal_type() == "MultiselectField":
                    if recurr_type == "recurr_only":
                        if (
                            interim_value
                            and interim_value not in ["nan", "NaT", pd.NaT, np.nan, "None", None, " ", "<NA>"]
                            and not pd.isna(interim_value)
                        ):
                            field_multiselect_config = json.loads(model_class.get_field(t_tcol).mulsel_config)
                            multi_select_table = field_multiselect_config["value"][0]
                            multi_select_master_column = field_multiselect_config["masterColumn"][0]
                            interim_value = list(json.loads(interim_value).keys())
                            converted_value = read_data_func(
                                request,
                                {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": multi_select_table,
                                        "Columns": [multi_select_master_column],
                                    },
                                    "condition": [
                                        {
                                            "column_name": "id",
                                            "condition": "IN",
                                            "input_value": interim_value,
                                            "and_or": "",
                                        }
                                    ],
                                },
                            )[multi_select_master_column].tolist()
                            to_list = converted_value
                        else:
                            to_list = []
                    else:
                        to_list = interim_value
                else:
                    if recurr_type == "recurr_only":
                        if isinstance(attachment_data[t_tcol].iloc[0], list):
                            to_list = attachment_data[t_tcol].iloc[0]
                        else:
                            to_list = [attachment_data[t_tcol].iloc[0]]
                    else:
                        if isinstance(transaction_data[t_tcol].iloc[0], list):
                            to_list = transaction_data[t_tcol].iloc[0]
                        else:
                            to_list = [transaction_data[t_tcol].iloc[0]]

            elif (
                condition_data_email_box_config["config"]["to_config"]["to_recipient_type"] == "dynamic_user"
            ):
                to_list = [request.user.email]
            elif condition_data_email_box_config["config"]["to_config"]["to_recipient_type"] == "static_user":
                user_list = condition_data_email_box_config["config"]["to_config"]["to_recipient_list"]
                to_list = (
                    read_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "User",
                                "Columns": ["email"],
                            },
                            "condition": [
                                {
                                    "column_name": "username",
                                    "condition": "IN",
                                    "input_value": str(tuple(user_list)).replace(",)", ")"),
                                    "and_or": "",
                                }
                            ],
                        },
                    )
                ).email.tolist()
            elif (
                condition_data_email_box_config["config"]["to_config"]["to_recipient_type"] == "static_groups"
            ):
                group_list = condition_data_email_box_config["config"]["to_config"]["to_recipient_list"]
                group_id = (
                    read_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "group_details",
                                "Columns": ["id"],
                            },
                            "condition": [
                                {
                                    "column_name": "name",
                                    "condition": "IN",
                                    "input_value": str(tuple(group_list)).replace(",)", ")"),
                                    "and_or": "",
                                }
                            ],
                        },
                    )
                ).id.tolist()
                if group_id:
                    user_ids = (
                        read_data_func(
                            request,
                            {
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": "user_groups",
                                    "Columns": ["user_id"],
                                },
                                "condition": [
                                    {
                                        "column_name": "group_id",
                                        "condition": "IN",
                                        "input_value": str(tuple(group_id)).replace(",)", ")"),
                                        "and_or": "",
                                    }
                                ],
                            },
                        )
                    ).user_id.tolist()
                    if user_ids:
                        to_list = (
                            read_data_func(
                                request,
                                {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": "User",
                                        "Columns": ["email"],
                                    },
                                    "condition": [
                                        {
                                            "column_name": "id",
                                            "condition": "IN",
                                            "input_value": str(tuple(user_ids)).replace(",)", ")"),
                                            "and_or": "",
                                        }
                                    ],
                                },
                            )
                        ).email.tolist()
                    else:
                        to_list = []
                else:
                    to_list = []
            elif (
                condition_data_email_box_config["config"]["to_config"]["to_recipient_type"]
                == "dynamic_approver"
            ):
                approval_recipient_emails = read_data_func(
                    request,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "event_master",
                            "Columns": ["recipients_list"],
                        },
                        "condition": [
                            {
                                "column_name": "action_config",
                                "condition": "Contains",
                                "input_value": elementID,
                                "and_or": "",
                            }
                        ],
                    },
                )
                approval_recipient_emails = json.loads(approval_recipient_emails.iloc[0, 0])
                to_list = approval_recipient_emails
            else:
                to_list = []
        else:
            to_list = []

        if condition_data_email_box_config["config"].get("to_config_cc"):
            if condition_data_email_box_config["config"]["to_config_cc"]["to_recipient_type"] == "static":
                to_cc = condition_data_email_box_config["config"]["to_config_cc"]["to_recipient_list"]
            elif condition_data_email_box_config["config"]["to_config_cc"][
                "to_recipient_type"
            ] == "dynamic" and len(transaction_data):
                t_tname = condition_data_email_box_config["config"]["to_config_cc"][
                    "to_recipient_dynamic_table"
                ]
                t_tcol = condition_data_email_box_config["config"]["to_config_cc"][
                    "to_recipient_dynamic_column"
                ]

                model_class = dynamic_model_create.get_model_class(t_tname, request)

                if recurr_type == "recurr_only":
                    interim_value = attachment_data[t_tcol].values[0]
                else:
                    interim_value = transaction_data[t_tcol].values[0]

                if model_class.get_field(t_tcol).get_internal_type() == "MultiselectField":
                    if recurr_type == "recurr_only":
                        if (
                            interim_value
                            and interim_value not in ["nan", "NaT", pd.NaT, np.nan, "None", None, " ", "<NA>"]
                            and not pd.isna(interim_value)
                        ):
                            field_multiselect_config = json.loads(model_class.get_field(t_tcol).mulsel_config)
                            multi_select_table = field_multiselect_config["value"][0]
                            multi_select_master_column = field_multiselect_config["masterColumn"][0]
                            interim_value = list(json.loads(interim_value).keys())
                            converted_value = read_data_func(
                                request,
                                {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": multi_select_table,
                                        "Columns": [multi_select_master_column],
                                    },
                                    "condition": [
                                        {
                                            "column_name": "id",
                                            "condition": "IN",
                                            "input_value": interim_value,
                                            "and_or": "",
                                        }
                                    ],
                                },
                            )[multi_select_master_column].tolist()
                            to_cc = converted_value
                        else:
                            to_cc = []
                    else:
                        to_cc = interim_value
                else:
                    if recurr_type == "recurr_only":
                        if isinstance(attachment_data[t_tcol].iloc[0], list):
                            to_cc = attachment_data[t_tcol].iloc[0]
                        else:
                            to_cc = [attachment_data[t_tcol].iloc[0]]
                    else:
                        if isinstance(transaction_data[t_tcol].iloc[0], list):
                            to_cc = transaction_data[t_tcol].iloc[0]
                        else:
                            to_cc = [transaction_data[t_tcol].iloc[0]]
            elif (
                condition_data_email_box_config["config"]["to_config_cc"]["to_recipient_type"]
                == "dynamic_user"
            ):
                to_cc = [request.user.email]
            elif (
                condition_data_email_box_config["config"]["to_config_cc"]["to_recipient_type"]
                == "static_user"
            ):
                user_list = condition_data_email_box_config["config"]["to_config_cc"]["to_recipient_list"]
                to_cc = (
                    read_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "User",
                                "Columns": ["email"],
                            },
                            "condition": [
                                {
                                    "column_name": "username",
                                    "condition": "IN",
                                    "input_value": str(tuple(user_list)).replace(",)", ")"),
                                    "and_or": "",
                                }
                            ],
                        },
                    )
                ).email.tolist()
            elif (
                condition_data_email_box_config["config"]["to_config_cc"]["to_recipient_type"]
                == "static_groups"
            ):
                group_list = condition_data_email_box_config["config"]["to_config_cc"]["to_recipient_list"]
                group_id = (
                    read_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "group_details",
                                "Columns": ["id"],
                            },
                            "condition": [
                                {
                                    "column_name": "name",
                                    "condition": "IN",
                                    "input_value": str(tuple(group_list)).replace(",)", ")"),
                                    "and_or": "",
                                }
                            ],
                        },
                    )
                ).id.tolist()
                if group_id:
                    user_ids = (
                        read_data_func(
                            request,
                            {
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": "user_groups",
                                    "Columns": ["user_id"],
                                },
                                "condition": [
                                    {
                                        "column_name": "group_id",
                                        "condition": "IN",
                                        "input_value": str(tuple(group_id)).replace(",)", ")"),
                                        "and_or": "",
                                    }
                                ],
                            },
                        )
                    ).user_id.tolist()
                    if user_ids:
                        to_cc = (
                            read_data_func(
                                request,
                                {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": "User",
                                        "Columns": ["email"],
                                    },
                                    "condition": [
                                        {
                                            "column_name": "id",
                                            "condition": "IN",
                                            "input_value": str(tuple(user_ids)).replace(",)", ")"),
                                            "and_or": "",
                                        }
                                    ],
                                },
                            )
                        ).email.tolist()
                    else:
                        to_cc = []
                else:
                    to_cc = []
            else:
                to_cc = []
        else:
            to_cc = []

        if condition_data_email_box_config["config"].get("to_config_bcc"):
            if condition_data_email_box_config["config"]["to_config_bcc"]["to_recipient_type"] == "static":
                to_bcc = condition_data_email_box_config["config"]["to_config_bcc"]["to_recipient_list"]
            elif condition_data_email_box_config["config"]["to_config_bcc"][
                "to_recipient_type"
            ] == "dynamic" and len(transaction_data):
                t_tname = condition_data_email_box_config["config"]["to_config_bcc"][
                    "to_recipient_dynamic_table"
                ]
                t_tcol = condition_data_email_box_config["config"]["to_config_bcc"][
                    "to_recipient_dynamic_column"
                ]

                model_class = dynamic_model_create.get_model_class(t_tname, request)

                if recurr_type == "recurr_only":
                    interim_value = attachment_data[t_tcol].values[0]
                else:
                    interim_value = transaction_data[t_tcol].values[0]

                if model_class.get_field(t_tcol).get_internal_type() == "MultiselectField":
                    if recurr_type == "recurr_only":
                        if (
                            interim_value
                            and interim_value not in ["nan", "NaT", pd.NaT, np.nan, "None", None, " ", "<NA>"]
                            and not pd.isna(interim_value)
                        ):
                            field_multiselect_config = json.loads(model_class.get_field(t_tcol).mulsel_config)
                            multi_select_table = field_multiselect_config["value"][0]
                            multi_select_master_column = field_multiselect_config["masterColumn"][0]
                            interim_value = list(json.loads(interim_value).keys())
                            converted_value = read_data_func(
                                request,
                                {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": multi_select_table,
                                        "Columns": [multi_select_master_column],
                                    },
                                    "condition": [
                                        {
                                            "column_name": "id",
                                            "condition": "IN",
                                            "input_value": interim_value,
                                            "and_or": "",
                                        }
                                    ],
                                },
                            )[multi_select_master_column].tolist()
                            to_bcc = converted_value
                        else:
                            to_bcc = []
                    else:
                        to_bcc = interim_value
                else:
                    if recurr_type == "recurr_only":
                        if isinstance(attachment_data[t_tcol].iloc[0], list):
                            to_bcc = attachment_data[t_tcol].iloc[0]
                        else:
                            to_bcc = [attachment_data[t_tcol].iloc[0]]
                    else:
                        if isinstance(transaction_data[t_tcol].iloc[0], list):
                            to_bcc = transaction_data[t_tcol].iloc[0]
                        else:
                            to_bcc = [transaction_data[t_tcol].iloc[0]]
            elif (
                condition_data_email_box_config["config"]["to_config_bcc"]["to_recipient_type"]
                == "dynamic_user"
            ):
                to_bcc = [request.user.email]
            elif (
                condition_data_email_box_config["config"]["to_config_bcc"]["to_recipient_type"]
                == "static_user"
            ):
                user_list = condition_data_email_box_config["config"]["to_config_bcc"]["to_recipient_list"]
                to_bcc = (
                    read_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "User",
                                "Columns": ["email"],
                            },
                            "condition": [
                                {
                                    "column_name": "username",
                                    "condition": "IN",
                                    "input_value": str(tuple(user_list)).replace(",)", ")"),
                                    "and_or": "",
                                }
                            ],
                        },
                    )
                ).email.tolist()
            elif (
                condition_data_email_box_config["config"]["to_config_bcc"]["to_recipient_type"]
                == "static_groups"
            ):
                group_list = condition_data_email_box_config["config"]["to_config_bcc"]["to_recipient_list"]
                group_id = (
                    read_data_func(
                        request,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "group_details",
                                "Columns": ["id"],
                            },
                            "condition": [
                                {
                                    "column_name": "name",
                                    "condition": "IN",
                                    "input_value": str(tuple(group_list)).replace(",)", ")"),
                                    "and_or": "",
                                }
                            ],
                        },
                    )
                ).id.tolist()
                if group_id:
                    user_ids = (
                        read_data_func(
                            request,
                            {
                                "inputs": {
                                    "Data_source": "Database",
                                    "Table": "user_groups",
                                    "Columns": ["user_id"],
                                },
                                "condition": [
                                    {
                                        "column_name": "group_id",
                                        "condition": "IN",
                                        "input_value": str(tuple(group_id)).replace(",)", ")"),
                                        "and_or": "",
                                    }
                                ],
                            },
                        )
                    ).user_id.tolist()
                    if user_ids:
                        to_bcc = (
                            read_data_func(
                                request,
                                {
                                    "inputs": {
                                        "Data_source": "Database",
                                        "Table": "User",
                                        "Columns": ["email"],
                                    },
                                    "condition": [
                                        {
                                            "column_name": "id",
                                            "condition": "IN",
                                            "input_value": str(tuple(user_ids)).replace(",)", ")"),
                                            "and_or": "",
                                        }
                                    ],
                                },
                            )
                        ).email.tolist()
                    else:
                        to_bcc = []
                else:
                    to_bcc = []
            else:
                to_bcc = []
        else:
            to_bcc = []

        if len(attachment_data):
            if columnRenameList:
                tdata2 = attachment_data.rename(columns=columnRenameList)
                final_data_json_email_box[approval_code] = tdata2.to_json(orient="records")
            else:
                final_data_json_email_box[approval_code] = attachment_data.to_json(orient="records")
        else:
            final_data_json_email_box[approval_code] = "[]"

        if len(transaction_data):
            transaction_data_dict = json.loads(transaction_data.to_json(orient="records"))[0]
        else:
            transaction_data_dict = {}

        approval_notification_subject = condition_data_email_box_config["config"]["subject_email"]
        smtpConfigKey = condition_data_email_box_config["config"]["from_email"]
        content = condition_data_email_box_config["config"]["text_email"]

        if approval_notification_subject:
            if condition_data_email_box_config["config"]["to_config"]["to_recipient_type"] == "static_user":
                user_list = condition_data_email_box_config["config"]["to_config"]["to_recipient_list"]
                if "{RecipientOfMail}" in approval_notification_subject:
                    approval_notification_subject = approval_notification_subject.replace(
                        "{RecipientOfMail}", ", ".join(user_list)
                    )
            elif (
                condition_data_email_box_config["config"]["to_config"]["to_recipient_type"] == "static_groups"
            ):
                group_list = condition_data_email_box_config["config"]["to_config"]["to_recipient_list"]
                if "{RecipientOfMail}" in approval_notification_subject:
                    approval_notification_subject = approval_notification_subject.replace(
                        "{RecipientOfMail}", ", ".join(group_list)
                    )
            else:
                if "{RecipientOfMail}" in approval_notification_subject:
                    approval_notification_subject = approval_notification_subject.replace(
                        "{RecipientOfMail}", request.user.username
                    )
                else:
                    pass

            if "{TransactionTime}" in approval_notification_subject:
                approval_notification_subject = approval_notification_subject.replace(
                    "{TransactionTime}", f"{datetime.now()}"
                )
            else:
                pass

        if condition_data_email_box_config["config"]["to_config"]["to_recipient_type"] == "static_user":
            user_list = condition_data_email_box_config["config"]["to_config"]["to_recipient_list"]
            if "{TransactionCreatedBy}" in content:
                content = content.replace("{TransactionCreatedBy}", ", ".join(user_list))
        if condition_data_email_box_config["config"]["to_config"]["to_recipient_type"] == "static_groups":
            group_list = condition_data_email_box_config["config"]["to_config"]["to_recipient_list"]
            if "{TransactionCreatedBy}" in content:
                content = content.replace("{TransactionCreatedBy}", ", ".join(group_list))
        if "{TransactionCreatedBy}" in content:
            content = content.replace("{TransactionCreatedBy}", request.user.username)
        else:
            pass
        if "{TransactionCreatedBy-Name}" in content:
            content = content.replace(
                "{TransactionCreatedBy-Name}", f"{request.user.first_name} {request.user.last_name}"
            )
        else:
            pass
        if "{TransactionTime}" in content:
            content = content.replace("{TransactionTime}", f"{datetime.now()}")
        else:
            pass

        if transaction_data_dict:
            for field in model_name1.concrete_fields:
                if f"VerboseName-{field.name}" in content:
                    content = content.replace(f"{{VerboseName-{field.name}}}", field.verbose_name)
                else:
                    pass
                if f"Value-{field.name}" in content:
                    if field.name in transaction_data_dict:
                        content = content.replace(
                            f"{{Value-{field.name}}}", str(transaction_data_dict[field.name])
                        )
                    else:
                        content = content.replace(f"{{Value-{field.name}}}", " - ")
                else:
                    continue

        standardised_functions.send_approval_mail(
            request,
            tablename,
            final_data_json_email_box,
            to_list,
            content,
            subject=approval_notification_subject,
            in_system_approval=False,
            to_cc=to_cc,
            to_bcc=to_bcc,
            attachments_config=approval_notification_attachment_config,
            smtpConfigKey=smtpConfigKey,
        )
    return None


def trigger_recurring_action_emailbox(
    request,
    recurr_cond_actions,
    recurr_cond_action_config,
    decision_id,
    groups_user_app,
    approval_code,
    tablename,
    message_ele_id,
    transaction_dict,
    notApprovalWork=False,
    approval_recipients=[],
):

    job_id = (
        message_ele_id
        + "-"
        + standardised_functions.random_no_generator()
        + "-recurrenceEmailBox-"
        + tablename
    )
    action_config = {"type": "schedule_job", "action": "kill", "job_id": job_id}
    data_dict = [
        {
            "element_id": decision_id,
            "event": json.dumps(recurr_cond_actions),
            "performed_by": json.dumps(groups_user_app),
            "approval_code": approval_code,
            "recipients_list": json.dumps(approval_recipients),
        }
    ]
    if notApprovalWork:
        action_config["actions_conditions"] = recurr_cond_actions
        tabScreenDF = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "event_master",
                    "Columns": ["event", "element_id", "action_config"],
                },
                "condition": [
                    {
                        "column_name": "element_id",
                        "condition": "Equal to",
                        "input_value": decision_id,
                        "and_or": "",
                    },
                ],
            },
        )
        if len(tabScreenDF) > 0:
            scheduler = Scheduler(connection=redis_instance_scheduler)
            for i in tabScreenDF.to_dict("records"):
                if "action_config" in i:
                    if "job_id" in json.loads(i["action_config"]):
                        scheduler.cancel(json.loads(i["action_config"])["job_id"])
            update_data_func(
                request,
                config_dict={
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "event_master",
                        "Columns": [
                            {
                                "column_name": "status",
                                "input_value": "closed",
                                "separator": "",
                            },
                        ],
                    },
                    "condition": [
                        {
                            "column_name": "element_id",
                            "condition": "Equal to",
                            "input_value": decision_id,
                            "and_or": "",
                        },
                    ],
                },
            )
            data_dict[0]["status"] = "open"
    data_dict[0]["action_config"] = json.dumps(action_config)
    data = pd.DataFrame(data_dict)
    data_handling(
        request,
        data,
        "event_master",
    )

    scheduler_config = recurr_cond_action_config["config"]["scheduler_config"]
    start_date = datetime.strptime(scheduler_config["start_date"], "%Y-%m-%d")
    duration = scheduler_config["duration"]
    if duration == "Monthly":
        day = start_date.day
        month = "*"
        day_of_week = "*"
    elif duration == "Monthly/5th day":
        day = "5"
        month = "*"
        day_of_week = "*"
    elif duration == "Quarterly":
        day = start_date.day
        month = "1,4,7,10"
        day_of_week = "*"
    elif duration == "Pre-Quarterly":
        day = "24"
        month = "12,3,6,9"
        day_of_week = "*"
    elif duration == "Weekly":
        day_of_week = start_date.weekday()
        month = "*"
        day = "*"
    elif duration == "Daily":
        month = "*"
        day = "*"
        day_of_week = "*"
    elif duration == "Yearly":
        month = start_date.month
        day = start_date.day
        day_of_week = "*"
    elif duration == "Hourly":
        month = "*"
        day = "*"
        day_of_week = "*"
        hour = f"*/{scheduler_config['frequency']}"
    elif duration == "Every N Minutes":
        month = "*"
        day = "*"
        day_of_week = "*"
        hour = "*"
        minute = f"*/{scheduler_config['frequency']}"
    time_var = scheduler_config["time_interval"]
    if duration not in ["Hourly", "Every N Minutes"]:
        if time_var.split(":")[0][0] == "0":
            hour = literal_eval(time_var.split(":")[0][1])
        else:
            hour = literal_eval(time_var.split(":")[0])
    if duration != "Every N Minutes":
        if time_var.split(":")[1][0] == "0":
            minute = literal_eval(time_var.split(":")[1][1])
        else:
            minute = literal_eval(time_var.split(":")[1])

    func = "recurrence_send_mail"

    scheduler = Scheduler(connection=redis_instance_scheduler)

    def request_to_dict(request):
        user_dict = request.user.__class__.objects.filter(pk=request.user.id).values().first()
        request2 = {"path": request.path, "host": request.get_host(), "user": user_dict}
        return request2

    request = request_to_dict(request)
    scheduler.cancel(job_id)
    scheduler.cron(
        f"{minute} {hour} {day} {month} {day_of_week}",
        func=eval(func),
        id=f"{job_id}",
        args=[request, f"{job_id}", transaction_dict, "recurr_action"],
        repeat=None,
    )

    return None
