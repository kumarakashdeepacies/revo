import logging

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import resolve

from config.settings.base import database_engine_dict
from kore_investment.users.computations.db_centralised_function import (
    app_engine_generator,
    current_app_db_extractor,
    execute_read_query,
    sql_engine_gen,
)


class db_connection_middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        apps = resolve(request.path_info).app_names
        if apps:
            if apps[0] == "users":
                app_code = ""
                db_connection_name = ""
                try:
                    app_code, db_connection_name = current_app_db_extractor(request)
                    if app_code:
                        sql_engine, db_type, schema = app_engine_generator(request)
                        if db_type == "Oracle":
                            query = "select 'test' as mytest from dual"
                        else:
                            query = "Select 1"
                        if sql_engine != ["", None]:
                            row = execute_read_query(query, sql_engine, db_type)
                            if len(row):
                                return response
                            else:
                                raise Exception
                        else:
                            raise Exception
                    else:
                        return response
                except Exception as e:
                    logging.warning(f"Following exception occurred - {e}")
                    if db_connection_name in database_engine_dict:
                        del database_engine_dict[db_connection_name]
                    messages.error(
                        request,
                        f"Lost connection to the database! Please reconnect the database from Management Console.",
                    )
                    return HttpResponseRedirect("/users/selectApplication/")
        return response
