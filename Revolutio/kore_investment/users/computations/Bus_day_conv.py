import datetime as dt

import numpy as np
import pandas as pd


def business_day(date, convention, holiday_list, business_days="1111100"):
    """
    Checks if a date is a business day and returns date after business day convention adjustments.
    date = input date to adjust for business day conventions
    convention = business day convention to be followed
    holiday_list = List of holidays to be considered. Expected format is list of datetime fields.
    """

    if type(holiday_list) == pd.core.series.Series:
        holiday_list = holiday_list.values.astype("datetime64[D]")

    # Following
    if convention == "Following":
        i = 0
        while np.busday_count(date, date + dt.timedelta(i), business_days, holiday_list) == 0:
            if np.busday_count(date, date + dt.timedelta(i + 1), business_days, holiday_list) != 0:
                return date + dt.timedelta(i)
            i += 1
    # Preceding
    if convention == "Preceding":
        if np.busday_count(date, date + dt.timedelta(1), business_days, holiday_list) != 0:
            return date
        else:
            i = 0
            while (
                np.busday_count(date - dt.timedelta(i), date + dt.timedelta(1), business_days, holiday_list)
                == 0
            ):
                if (
                    np.busday_count(
                        date - dt.timedelta(i + 1), date + dt.timedelta(1), business_days, holiday_list
                    )
                    != 0
                ):
                    return date - dt.timedelta(i + 1)
                i += 1

    # Modified Following
    if convention == "Modified Following":
        i = 0
        while np.busday_count(date, date + dt.timedelta(i), business_days, holiday_list) == 0:
            if np.busday_count(date, date + dt.timedelta(i + 1), business_days, holiday_list) != 0:
                if (date + dt.timedelta(i)).month == date.month:
                    return date + dt.timedelta(i)
                else:
                    if np.busday_count(date, date + dt.timedelta(1), business_days, holiday_list) != 0:
                        return date
                    else:
                        j = 0
                        while (
                            np.busday_count(
                                date - dt.timedelta(j), date + dt.timedelta(1), business_days, holiday_list
                            )
                            == 0
                        ):
                            if (
                                np.busday_count(
                                    date - dt.timedelta(j + 1),
                                    date + dt.timedelta(1),
                                    business_days,
                                    holiday_list,
                                )
                                != 0
                            ):
                                return date - dt.timedelta(j + 1)
                            j += 1
            i += 1

    # Modified Following bimonthly
    if convention == "Modified Following bimonthly":
        i = 0
        while np.busday_count(date, date + dt.timedelta(i), business_days, holiday_list) == 0:
            if np.busday_count(date, date + dt.timedelta(i + 1), business_days, holiday_list) != 0:
                if date <= dt.date(date.year, date.month, 15) < date + dt.timedelta(i):
                    if np.busday_count(date, date + dt.timedelta(1), business_days, holiday_list) != 0:
                        return date
                    else:
                        j = 0
                        while (
                            np.busday_count(
                                date - dt.timedelta(j), date + dt.timedelta(1), business_days, holiday_list
                            )
                            == 0
                        ):
                            if (
                                np.busday_count(
                                    date - dt.timedelta(j + 1),
                                    date + dt.timedelta(1),
                                    business_days,
                                    holiday_list,
                                )
                                != 0
                            ):
                                return date - dt.timedelta(j + 1)
                            j += 1
                elif (date + dt.timedelta(i)).month == date.month:
                    return date + dt.timedelta(i)

                else:
                    if np.busday_count(date, date + dt.timedelta(1), business_days, holiday_list) != 0:
                        return date
                    else:
                        j = 0
                        while (
                            np.busday_count(
                                date - dt.timedelta(j), date + dt.timedelta(1), business_days, holiday_list
                            )
                            == 0
                        ):
                            if (
                                np.busday_count(
                                    date - dt.timedelta(j + 1),
                                    date + dt.timedelta(1),
                                    business_days,
                                    holiday_list,
                                )
                                != 0
                            ):
                                return date - dt.timedelta(j + 1)
                            j += 1
            i += 1

    # End of the Month
    if convention == "End of the Month":
        if date.month != 12:
            return business_day(dt.date(date.year, date.month + 1, 1) - dt.timedelta(1), 2, holiday_list)
        else:
            return business_day(dt.date(date.year + 1, 1, 1) - dt.timedelta(1), 2, holiday_list)
