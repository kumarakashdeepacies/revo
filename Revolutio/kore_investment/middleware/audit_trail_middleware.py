from datetime import datetime
from urllib.parse import urlparse

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import resolve
import pandas as pd

from kore_investment.users.computations.db_centralised_function import postgres_push, read_data_func
from kore_investment.users.computations.standardised_functions import current_app_db_extractor


class AuditMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code == 200:
            if not request.user.is_anonymous:
                path_info = resolve(request.path_info).app_names
                if path_info:
                    app_code = None
                    if path_info[0] == "users":
                        app_code = current_app_db_extractor(request)
                        app_code = app_code[0]
                    else:
                        pass
                    content_type = response.headers.get("Content-Type")
                    parsed = urlparse(request.META.get("HTTP_REFERER"))

                    if content_type == "text/html; charset=utf-8":
                        audit_screen = request.path[:-1].split("/").pop()
                        mode = request.path[1:-1].split("/")
                        if len(mode) >= 4:
                            mode = request.path[1:-1].split("/")[2]
                            if mode == "Build" and not request.user.is_superuser:
                                groups = list(request.user.groups.values_list("name", flat=True))
                                if groups:
                                    check = read_data_func(
                                        request,
                                        {
                                            "inputs": {
                                                "Data_source": "Database",
                                                "Table": "UserPermission_Master",
                                                "Columns": ["id"],
                                            },
                                            "condition": [
                                                {
                                                    "column_name": "usergroup",
                                                    "condition": "IN",
                                                    "input_value": groups,
                                                    "and_or": "AND",
                                                },
                                                {
                                                    "column_name": "application",
                                                    "condition": "Contains",
                                                    "input_value": f'"{app_code}": 1',
                                                    "and_or": "",
                                                },
                                            ],
                                        },
                                    )
                                    if check.empty:
                                        messages.error(
                                            request,
                                            f"Access Denied! You do not have developer mode access for this application.",
                                        )
                                        return HttpResponseRedirect("/users/selectApplication/")
                                    else:
                                        pass
                                else:
                                    pass
                            else:
                                pass
                        else:
                            pass
                        audit_prev_url = str(parsed.path)
                    else:
                        audit_screen = parsed.path[:-1].split("/").pop()
                        audit_prev_url = None

                    new_data = pd.DataFrame(
                        [
                            {
                                "session_id": request.session.session_key,
                                "ip": request.META.get("REMOTE_ADDR"),
                                "user_name": request.user.username,
                                "app_code": app_code,
                                "url_current": request.path,
                                "url_from": audit_prev_url,
                                "screen": audit_screen,
                                "logged_date": datetime.now().strftime("%Y-%m-%d"),
                                "logged_time": datetime.now().strftime("%H:%M:%S"),
                                "instance_id": request.user.instance_id,
                            }
                        ]
                    )
                    postgres_push(new_data, "users_audit_trail", "public")
                else:
                    pass
            else:
                pass
        else:
            pass
        return response
