from datetime import datetime, timedelta

import dateutil.parser as dp
import dateutil.rrule as dr
import pandas as pd

from .computations.db_centralised_function import read_data_func


def filtered_data_audit_trail_helper(daterange_list, col_name):
    condition = []
    Agg_Type = ""
    Order_Type = ""

    if daterange_list[1] == "Latest":
        if col_name != "logged_date":
            Agg_Type = "LIMIT 1"
            Order_Type = f"ORDER BY {col_name} DESC"
        elif col_name == "logged_date":
            Agg_Type = "LIMIT 1"
            Order_Type = """ORDER BY "id" DESC"""
        condition = []
    elif daterange_list[1] == "Last 7 Days":
        last_seven_days = datetime.now() + pd.DateOffset(days=-7)
        last_seven_days = last_seven_days.strftime("%Y-%m-%d %H:%M:%S")
        condition = [
            {
                "column_name": col_name,
                "condition": "Greater than",
                "input_value": last_seven_days,
                "and_or": "",
            }
        ]
    elif daterange_list[1] == "Today":
        condition = [
            {
                "column_name": col_name,
                "condition": "Greater than equal to",
                "input_value": datetime.now().strftime("%Y-%m-%d 00:00:00"),
                "and_or": "",
            }
        ]
    elif daterange_list[1] == "Yesterday":
        condition = [
            {
                "column_name": col_name,
                "condition": "Greater than equal to",
                "input_value": (datetime.now() + pd.DateOffset(days=-1)).strftime("%Y-%m-%d 00:00:00"),
                "and_or": "",
            }
        ]
    elif daterange_list[1] == "This Week":
        current_date = datetime.now()
        start_of_week = current_date - timedelta(days=current_date.weekday())
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0)
        end_of_week = start_of_week + timedelta(days=6)
        end_of_week = end_of_week.replace(hour=23, minute=59, second=59)
        condition = [
            {
                "column_name": col_name,
                "condition": "Greater than equal to",
                "input_value": start_of_week.strftime("%Y-%m-%d %H:%M:%S"),
                "and_or": "and",
            },
            {
                "column_name": col_name,
                "condition": "Smaller than equal to",
                "input_value": end_of_week.strftime("%Y-%m-%d %H:%M:%S"),
                "and_or": "",
            },
        ]
    elif daterange_list[1] == "This Month":
        current_date = datetime.now()
        currMonth = current_date.month
        dtFirstDay = datetime(current_date.year, currMonth, 1)
        next_month = current_date.replace(day=28) + timedelta(days=4)
        next_month = next_month - timedelta(days=next_month.day)
        next_month = next_month.replace(hour=23, minute=59, second=59)
        condition = [
            {
                "column_name": col_name,
                "condition": "Greater than equal to",
                "input_value": dtFirstDay.strftime("%Y-%m-%d %H:%M:%S"),
                "and_or": "and",
            },
            {
                "column_name": col_name,
                "condition": "Smaller than equal to",
                "input_value": next_month.strftime("%Y-%m-%d %H:%M:%S"),
                "and_or": "",
            },
        ]
    elif daterange_list[1] == "This Quarter":
        current_date = datetime.now()
        currQuarter = (current_date.month - 1) // 3 + 1
        dtFirstDay = datetime(current_date.year, 3 * currQuarter - 2, 1)
        dtLastDay = datetime(current_date.year, (3 * currQuarter) % 12 + 1, 1) + timedelta(days=-1)
        dtLastDay = dtLastDay.replace(hour=23, minute=59, second=59)
        condition = [
            {
                "column_name": col_name,
                "condition": "Greater than equal to",
                "input_value": dtFirstDay.strftime("%Y-%m-%d %H:%M:%S"),
                "and_or": "and",
            },
            {
                "column_name": col_name,
                "condition": "Smaller than equal to",
                "input_value": dtLastDay.strftime("%Y-%m-%d %H:%M:%S"),
                "and_or": "",
            },
        ]
    elif daterange_list[1] == "This Year":
        current_date = datetime.now()
        dtFirstDay = datetime(current_date.year, 1, 1)
        dtLastDay = datetime(current_date.year, 12, 31)
        dtLastDay = dtLastDay.replace(hour=23, minute=59, second=59)
        condition = [
            {
                "column_name": col_name,
                "condition": "Greater than equal to",
                "input_value": dtFirstDay.strftime("%Y-%m-%d %H:%M:%S"),
                "and_or": "and",
            },
            {
                "column_name": col_name,
                "condition": "Smaller than equal to",
                "input_value": dtLastDay.strftime("%Y-%m-%d %H:%M:%S"),
                "and_or": "",
            },
        ]
    elif daterange_list[1] == "Previous Week":
        current_date = datetime.now()
        start_date = current_date + timedelta(-current_date.weekday(), weeks=-1)
        end_date = current_date + timedelta(-current_date.weekday() - 1)
        start_date = start_date.replace(hour=0, minute=0, second=0)
        end_date = end_date.replace(hour=23, minute=59, second=59)
        condition = [
            {
                "column_name": col_name,
                "condition": "Greater than equal to",
                "input_value": start_date.strftime("%Y-%m-%d %H:%M:%S"),
                "and_or": "and",
            },
            {
                "column_name": col_name,
                "condition": "Smaller than equal to",
                "input_value": end_date.strftime("%Y-%m-%d %H:%M:%S"),
                "and_or": "",
            },
        ]
    elif daterange_list[1] == "Previous Month":
        current_date = datetime.now()
        last_day_of_prev_month = current_date.replace(day=1) - timedelta(days=1)
        start_day_of_prev_month = current_date.replace(day=1) - timedelta(days=last_day_of_prev_month.day)
        start_day_of_prev_month = start_day_of_prev_month.replace(hour=0, minute=0, second=0)
        last_day_of_prev_month = last_day_of_prev_month.replace(hour=23, minute=59, second=59)
        condition = [
            {
                "column_name": col_name,
                "condition": "Greater than equal to",
                "input_value": start_day_of_prev_month.strftime("%Y-%m-%d %H:%M:%S"),
                "and_or": "and",
            },
            {
                "column_name": col_name,
                "condition": "Smaller than equal to",
                "input_value": last_day_of_prev_month.strftime("%Y-%m-%d %H:%M:%S"),
                "and_or": "",
            },
        ]
    elif daterange_list[1] == "Previous Quarter":
        current_date = datetime.now()
        if current_date.month < 4:
            end_date = datetime(current_date.year - 1, 12, 31)
        elif current_date.month < 7:
            end_date = datetime(current_date.year, 3, 31)
        elif current_date.month < 10:
            end_date = datetime(current_date.year, 6, 30)
        else:
            end_date = datetime(current_date.year, 9, 30)

        start_date = (end_date + pd.DateOffset(months=-3)).replace(day=1)
        start_date = start_date.replace(hour=0, minute=0, second=0)
        end_date = end_date.replace(hour=23, minute=59, second=59)
        condition = [
            {
                "column_name": col_name,
                "condition": "Greater than equal to",
                "input_value": start_date.strftime("%Y-%m-%d %H:%M:%S"),
                "and_or": "and",
            },
            {
                "column_name": col_name,
                "condition": "Smaller than equal to",
                "input_value": end_date.strftime("%Y-%m-%d %H:%M:%S"),
                "and_or": "",
            },
        ]

    elif daterange_list[1] == "Previous Year":
        current_date = datetime.now()
        dtFirstDay = datetime(current_date.year - 1, 1, 1)
        dtLastDay = datetime(current_date.year - 1, 12, 31)
        dtFirstDay = dtFirstDay.replace(hour=0, minute=0, second=0)
        dtLastDay = dtLastDay.replace(hour=23, minute=59, second=59)
        condition = [
            {
                "column_name": col_name,
                "condition": "Greater than equal to",
                "input_value": dtFirstDay.strftime("%Y-%m-%d %H:%M:%S"),
                "and_or": "and",
            },
            {
                "column_name": col_name,
                "condition": "Smaller than equal to",
                "input_value": dtLastDay.strftime("%Y-%m-%d %H:%M:%S"),
                "and_or": "",
            },
        ]
    elif daterange_list[1] == "Custom":
        start_date = daterange_list[2].split(" - ")[0]
        end_date = daterange_list[2].split(" - ")[1]
        condition = [
            {
                "column_name": col_name,
                "condition": "Greater than equal to",
                "input_value": pd.to_datetime(start_date).strftime("%Y-%m-%d %H:%M:%S"),
                "and_or": "and",
            },
            {
                "column_name": col_name,
                "condition": "Smaller than equal to",
                "input_value": (pd.to_datetime(end_date) + pd.DateOffset(days=1)).strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "and_or": "",
            },
        ]

    elif daterange_list[1] == "Advanced":
        condition = []
        date_rec_list = []
        if len(daterange_list) == 4:
            skip = 1
        else:
            skip = 0
        week_day_rec = {
            "Monday": dr.MO,
            "Tuesday": dr.TU,
            "Wednesday": dr.WE,
            "Thursday": dr.TH,
            "Friday": dr.FR,
            "Saturday": dr.SA,
            "Sunday": dr.SU,
        }
        year_day_rec = {
            "Jan": 1,
            "Feb": 2,
            "Mar": 3,
            "Apr": 4,
            "May": 5,
            "Jun": 6,
            "Jul": 7,
            "Aug": 8,
            "Sept": 9,
            "Oct": 10,
            "Nov": 11,
            "Dec": 12,
        }
        start_date = dp.parse(daterange_list[2]["daterange"].split(" - ")[0])
        end_date = dp.parse(daterange_list[2]["daterange"].split(" - ")[1])

        if daterange_list[2]["type"] == "Daily":
            if daterange_list[2]["daily_day"] == "Everyday":
                if daterange_list[2]["end_no_occ"] == "end":
                    date_rec_list = list(
                        dr.rrule(
                            dr.DAILY,
                            interval=int(daterange_list[2]["rec_daily_days_no"]),
                            dtstart=start_date,
                            until=end_date,
                        )
                    )
                elif daterange_list[2]["end_no_occ"] != "end" and daterange_list[2]["end_no_occ"] != "":
                    date_rec_list = list(
                        dr.rrule(
                            dr.DAILY,
                            interval=int(daterange_list[2]["rec_daily_days_no"]),
                            count=int(daterange_list[2]["end_no_occ"]),
                            dtstart=start_date,
                        )
                    )
                else:
                    date_rec_list = list(
                        dr.rrule(
                            dr.DAILY,
                            interval=int(daterange_list[2]["rec_daily_days_no"]),
                            dtstart=start_date,
                            until=dp.parse("2099-12-31"),
                        )
                    )
            elif daterange_list[2]["daily_day"] == "Everyweekday":
                if daterange_list[2]["end_no_occ"] == "end":
                    date_rec_list = list(
                        dr.rrule(
                            dr.WEEKLY,
                            byweekday=(dr.MO, dr.TU, dr.WE, dr.TH, dr.FR),
                            dtstart=start_date,
                            until=end_date,
                        )
                    )
                elif daterange_list[2]["end_no_occ"] != "end" and daterange_list[2]["end_no_occ"] != "":
                    date_rec_list = list(
                        dr.rrule(
                            dr.WEEKLY,
                            byweekday=(dr.MO, dr.TU, dr.WE, dr.TH, dr.FR),
                            count=int(daterange_list[2]["end_no_occ"]),
                            dtstart=start_date,
                        )
                    )
                else:
                    date_rec_list = list(
                        dr.rrule(
                            dr.WEEKLY,
                            byweekday=(dr.MO, dr.TU, dr.WE, dr.TH, dr.FR),
                            dtstart=start_date,
                            until=dp.parse("2099-12-31"),
                        )
                    )

        elif daterange_list[2]["type"] == "Weekly":
            rec_weekly_days = daterange_list[2]["rec_weekly_days"]
            for i in range(len(rec_weekly_days)):
                rec_weekly_days[i] = week_day_rec[rec_weekly_days[i]]

            if daterange_list[2]["end_no_occ"] == "end":
                date_rec_list = list(
                    dr.rrule(
                        dr.WEEKLY,
                        wkst=dr.SU,
                        byweekday=rec_weekly_days,
                        interval=int(daterange_list[2]["rec_weekly_days_no"]),
                        dtstart=start_date,
                        until=end_date,
                    )
                )
            elif daterange_list[2]["end_no_occ"] != "end" and daterange_list[2]["end_no_occ"] != "":
                date_rec_list = list(
                    dr.rrule(
                        dr.WEEKLY,
                        wkst=dr.SU,
                        byweekday=rec_weekly_days,
                        interval=int(daterange_list[2]["rec_weekly_days_no"]),
                        count=int(daterange_list[2]["end_no_occ"]),
                        dtstart=start_date,
                        until=end_date,
                    )
                )
            else:
                date_rec_list = list(
                    dr.rrule(
                        dr.WEEKLY,
                        wkst=dr.SU,
                        byweekday=rec_weekly_days,
                        interval=int(daterange_list[2]["rec_weekly_days_no"]),
                        dtstart=start_date,
                        until=dp.parse("2099-12-31"),
                    )
                )

        elif daterange_list[2]["type"] == "Monthly":

            if daterange_list[2]["end_no_occ"] == "end":
                date_rec_list = list(
                    dr.rrule(
                        dr.MONTHLY,
                        interval=int(daterange_list[2]["rec_monthly_months_no"]),
                        bymonthday=(int(daterange_list[2]["rec_monthly_days_no"])),
                        dtstart=start_date,
                        until=end_date,
                    )
                )
            elif daterange_list[2]["end_no_occ"] != "end" and daterange_list[2]["end_no_occ"] != "":
                date_rec_list = list(
                    dr.rrule(
                        dr.MONTHLY,
                        interval=int(daterange_list[2]["rec_monthly_months_no"]),
                        bymonthday=(int(daterange_list[2]["rec_monthly_days_no"])),
                        dtstart=start_date,
                        count=int(daterange_list[2]["end_no_occ"]),
                    )
                )
            else:
                date_rec_list = list(
                    dr.rrule(
                        dr.MONTHLY,
                        interval=int(daterange_list[2]["rec_monthly_months_no"]),
                        bymonthday=(int(daterange_list[2]["rec_monthly_days_no"])),
                        dtstart=start_date,
                        until=dp.parse("2099-12-31"),
                    )
                )

        elif daterange_list[2]["type"] == "Yearly":

            if daterange_list[2]["end_no_occ"] == "end":
                date_rec_list = list(
                    dr.rrule(
                        dr.YEARLY,
                        bymonthday=(int(daterange_list[2]["rec_yearly_day_no"])),
                        bymonth=year_day_rec[daterange_list[2]["rec_yearly_month_no"]],
                        interval=int(daterange_list[2]["rec_yearly_year_no"]),
                        dtstart=start_date,
                        until=end_date,
                    )
                )
            elif daterange_list[2]["end_no_occ"] != "end" and daterange_list[2]["end_no_occ"] != "":
                date_rec_list = list(
                    dr.rrule(
                        dr.YEARLY,
                        bymonthday=(int(daterange_list[2]["rec_yearly_day_no"])),
                        bymonth=year_day_rec[daterange_list[2]["rec_yearly_month_no"]],
                        interval=int(daterange_list[2]["rec_yearly_year_no"]),
                        dtstart=start_date,
                        count=int(daterange_list[2]["end_no_occ"]),
                    )
                )
            else:
                date_rec_list = list(
                    dr.rrule(
                        dr.YEARLY,
                        bymonthday=(int(daterange_list[2]["rec_yearly_day_no"])),
                        bymonth=year_day_rec[daterange_list[2]["rec_yearly_month_no"]],
                        interval=int(daterange_list[2]["rec_yearly_year_no"]),
                        dtstart=start_date,
                        until=dp.parse("2099-12-31"),
                    )
                )

        for idx, i in enumerate(date_rec_list):
            if not skip:
                cond_dic = {
                    "column_name": f"""to_char("{col_name}",'YYYY-MM-DD')""",
                    "condition": "Starts with",
                    "input_value": f"{i.strftime('%Y-%m-%d')}",
                    "and_or": "or",
                }
            else:
                cond_dic = {
                    "column_name": f"""convert(VARCHAR(55),"{col_name}",126)""",
                    "condition": "Starts with",
                    "input_value": f"{i.strftime('%Y-%m-%d')}",
                    "and_or": "or",
                    "skip": 1,
                }

            condition.append(cond_dic)
        condition[-1]["and_or"] = ""
    else:
        pass

    return condition, Agg_Type, Order_Type


def user_login_default_view_handler(request, start, length, filter_cond=None):
    col_name = "time_logged_in"
    condition = []
    Agg_Type = ""
    rawdata = None
    r_len = None
    last_seven_days = datetime.now() + pd.DateOffset(days=-7)
    last_seven_days = last_seven_days.strftime("%Y-%m-%d %H:%M:%S")
    if filter_cond is not None:
        condition, Agg_Type, Order_Type = filtered_data_audit_trail_helper(filter_cond, col_name)
        if Agg_Type and (Agg_Type.startswith("TOP") or Agg_Type.startswith("LIMIT")):
            start = ""
            length = ""
        else:
            pass
    else:
        condition = [
            {
                "column_name": "time_logged_in",
                "condition": "Greater than",
                "input_value": last_seven_days,
                "and_or": "",
            }
        ]

    if request.POST.get("searchValue"):
        search_param = request.POST["searchValue"]

        def contains_only_integers(value):
            return all(char.isdigit() for char in str(value))

        if condition:
            condition[-1]["and_or"] = "AND"
        else:
            pass
        condition.extend(
            [
                {
                    "column_name": "user_name",
                    "condition": "Contains",
                    "input_value": search_param,
                    "and_or": "OR",
                    "constraintName": "C1",
                    "ruleSet": "R1",
                },
                {
                    "column_name": "session_id",
                    "condition": "Contains",
                    "input_value": search_param,
                    "and_or": "OR",
                    "constraintName": "C1",
                    "ruleSet": "R2",
                },
                {
                    "column_name": "logout_type",
                    "condition": "Contains",
                    "input_value": search_param,
                    "and_or": "OR",
                    "constraintName": "C1",
                    "ruleSet": "R3",
                },
                {
                    "column_name": "ip",
                    "condition": "Contains",
                    "input_value": search_param,
                    "and_or": "OR",
                    "constraintName": "C1",
                    "ruleSet": "R4",
                },
            ]
        )

        if contains_only_integers(search_param):
            condition.extend(
                [
                    {
                        "column_name": "id",
                        "condition": "Equal to",
                        "input_value": search_param,
                        "and_or": "OR",
                        "constraintName": "C1",
                        "ruleSet": "R5",
                    },
                ]
            )
    else:
        pass

    if length != -1:
        if start != "" and length != "":
            rawdata = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "login_trail",
                        "Agg_Type": Agg_Type,
                        "Order_Type": "ORDER BY id DESC",
                        "Columns": ["*"],
                        "Offset": start,
                        "Fetch_next": length,
                    },
                    "condition": condition,
                },
            )
            r_len = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "login_trail",
                        "Agg_Type": f"Count(id), Count(distinct user_name), Count(distinct ip)",
                        "Columns": [],
                    },
                    "condition": condition,
                },
            )
            unique_users = r_len.iloc[0, 1]
            unique_ips = r_len.iloc[0, 2]
            r_len = r_len.iloc[0, 0]
        else:
            rawdata = read_data_func(
                request,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "login_trail",
                        "Agg_Type": Agg_Type,
                        "Order_Type": "ORDER BY id DESC",
                        "Columns": ["*"],
                    },
                    "condition": condition,
                },
            )
            r_len = len(rawdata)
            unique_users = len(rawdata["user_name"].unique().tolist())
            unique_ips = len(rawdata["ip"].unique().tolist())
    else:
        rawdata = read_data_func(
            request,
            {
                "inputs": {
                    "Data_source": "Database",
                    "Table": "login_trail",
                    "Agg_Type": Agg_Type,
                    "Order_Type": "ORDER BY id DESC",
                    "Columns": ["*"],
                },
                "condition": condition,
            },
        )
        r_len = len(rawdata.index)
        unique_users = len(r_len["user_name"].unique().tolist())
        unique_ips = len(r_len["ip"].unique().tolist())

    if rawdata is not None:
        rawdata["time_logged_in"] = pd.to_datetime(rawdata.time_logged_in, format="%Y-%m-%d %H:%M:%S")
        rawdata["time_logged_in"] = rawdata["time_logged_in"].dt.strftime("%Y-%m-%d %H:%M:%S")
        rawdata["time_logged_out"] = pd.to_datetime(rawdata.time_logged_out, format="%Y-%m-%d %H:%M:%S")
        rawdata["time_logged_out"] = rawdata["time_logged_out"].dt.strftime("%Y-%m-%d %H:%M:%S")
    rawdata.fillna("-", inplace=True)

    rawdata = rawdata.to_dict("records")
    return rawdata, r_len, unique_users, unique_ips
