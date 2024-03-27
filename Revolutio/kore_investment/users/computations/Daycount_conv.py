import calendar
from datetime import datetime

import numpy as np
import pandas as pd


def number_of_days(effective_dates):
    days_list = []
    Effective_date = effective_dates
    for i in range(len(Effective_date)):
        date_diff = max((Effective_date[i] - Effective_date[i - 1]).days, 0)
        days_list.append(date_diff)

    return days_list


def Day_count(
    Val_date,
    Coupon_date_list,
    Convention,
    Maturity_date="none",
    couponfreq=1,
    Next_coupon_date_list=[],
    holiday_list=[],
):
    # 30/360 Bond Basis
    if Convention == "30/360":
        day_count_list = []

        n = len(Coupon_date_list)
        for j in range(0, n):
            if Coupon_date_list[j].day == 31 and (Val_date.day == 30 or Val_date.day == 31):
                x = 30
            else:
                x = Coupon_date_list[j].day
            if Val_date.day == 31:
                y = 30
            else:
                y = Val_date.day
            day_count_list.append(
                (
                    (Coupon_date_list[j].year - Val_date.year) * 360
                    + (Coupon_date_list[j].month - Val_date.month) * 30
                    + (x - y)
                )
                / 360
            )
        j = j + 1
        return day_count_list

    # 30/360 US
    if Convention == "30/360 US":

        day_count_list = []
        n = len(Coupon_date_list)
        for j in range(0, n):
            if (
                (Val_date + datetime.timedelta(1)).month == 3
                and ((Val_date + datetime.timedelta(1)).day == 1)
                and ((Coupon_date_list[j] + datetime.timedelta(1)).month == 3)
                and ((Coupon_date_list[j] + datetime.timedelta(1)).day == 1)
            ):
                x = 30
            elif Coupon_date_list[j].day == 31 and (Val_date.day == 30 or Val_date.day == 31):
                x = 30
            else:
                x = Coupon_date_list[j].day

            if ((Val_date + datetime.timedelta(1)).month == 3) and (
                (Val_date + datetime.timedelta(1)).day == 1
            ):
                y = 30
            elif Val_date.day == 31:
                y = 30
            else:
                y = Val_date.day
            day_count_list.append(
                (
                    (Coupon_date_list[j].year - Val_date.year) * 360
                    + (Coupon_date_list[j].month - Val_date.month) * 30
                    + (x - y)
                )
                / 360
            )
        return day_count_list

    # 30E/360
    if Convention == "30E/360":
        day_count_list = []
        n = len(Coupon_date_list)
        for j in range(0, n):
            if Coupon_date_list[j].day == 31:
                x = 30
            else:
                x = Coupon_date_list[j].day
            if Val_date.day == 31:
                y = 30
            else:
                y = Val_date.day
            day_count_list.append(
                (
                    (Coupon_date_list[j].year - Val_date.year) * 360
                    + (Coupon_date_list[j].month - Val_date.month) * 30
                    + (x - y)
                )
                / 360
            )
        return day_count_list

    # 30E/360 ISDA
    if Convention == "30E/360":
        day_count_list = []
        n = len(Coupon_date_list)
        for j in range(0, n):
            if Coupon_date_list[j].day == 31:
                x = 30
            elif (
                ((Coupon_date_list[j] + datetime.timedelta(1)).month == 3)
                and ((Coupon_date_list[j] + datetime.timedelta(1)).day == 1)
                and (Coupon_date_list[j] != pd.to_datetime(Maturity_date))
            ):
                x = 30
            else:
                x = Coupon_date_list[j].day
            if Val_date.day == 31:
                y = 30
            elif ((Val_date + datetime.timedelta(1)).month == 3) and (
                (Val_date + datetime.timedelta(1)).day == 1
            ):
                y = 30
            else:
                y = Val_date.day
            day_count_list.append(
                (
                    (Coupon_date_list[j].year - Val_date.year) * 360
                    + (Coupon_date_list[j].month - Val_date.month) * 30
                    + (x - y)
                )
                / 360
            )
        return day_count_list

    # 30E+/360 ISDA
    if Convention == "30E+/360":
        day_count_list = []
        n = len(Coupon_date_list)
        R_Coupon_date_list = [0] * n
        for j in range(0, n):
            if (Coupon_date_list[j].day) == 31:
                R_Coupon_date_list[j] = Coupon_date_list[j] + datetime.timedelta(1)
                x = R_Coupon_date_list[j].day
            else:
                R_Coupon_date_list[j] = Coupon_date_list[j]
                x = R_Coupon_date_list[j].day
            if Val_date.day == 31:
                y = 30
            else:
                y = Val_date.day
            day_count_list.append(
                (
                    (R_Coupon_date_list[j].year - Val_date.year) * 360
                    + (R_Coupon_date_list[j].month - Val_date.month) * 30
                    + (x - y)
                )
                / 360
            )
        return day_count_list

    # Act/360
    if Convention == "Act/360":
        day_count_list = []
        if type(Coupon_date_list) == pd.core.series.Series:
            Val_date = pd.to_datetime(Val_date)
        n = len(Coupon_date_list)
        for j in range(0, n):
            day_count_list.append((Coupon_date_list[j] - Val_date).days / 360)
        return day_count_list

    # Act/365
    if Convention == "Act/365":
        day_count_list = []
        if type(Coupon_date_list) == pd.core.series.Series:
            Val_date = pd.to_datetime(Val_date)
        n = len(Coupon_date_list)
        for j in range(0, n):
            day_count_list.append((Coupon_date_list[j] - Val_date).days / 365)
        return day_count_list

    # Act/365L
    if Convention == "Act/365L":
        day_count_list = []
        if type(Coupon_date_list) == pd.core.series.Series:
            Val_date = pd.to_datetime(Val_date)
        n = len(Coupon_date_list)
        for j in range(0, n):
            if couponfreq == 1 and (Coupon_date_list[j].year - Val_date.year) >= 4:
                day_count_list.append((Coupon_date_list[j] - Val_date).days / 366)

            elif calendar.isleap(Val_date.year) is True and couponfreq == 1:
                if (
                    pd.to_datetime(Val_date)
                    < pd.to_datetime(datetime.date(Val_date.year, 2, 29))
                    <= Coupon_date_list[j]
                ):
                    day_count_list.append((Coupon_date_list[j] - Val_date).days / 366)
                elif (
                    pd.to_datetime(Val_date)
                    < pd.to_datetime(datetime.date(Val_date.year + 4, 2, 29))
                    <= Coupon_date_list[j]
                ):
                    day_count_list.append((Coupon_date_list[j] - Val_date).days / 366)
                else:
                    day_count_list.append((Coupon_date_list[j] - Val_date).days / 365)
            elif calendar.isleap(Val_date.year + 1) is True and couponfreq == 1:
                if (
                    pd.to_datetime(Val_date)
                    < pd.to_datetime(datetime.date(Val_date.year + 1, 2, 29))
                    <= Coupon_date_list[j]
                ):
                    day_count_list.append((Coupon_date_list[j] - Val_date).days / 366)
                else:
                    day_count_list.append((Coupon_date_list[j] - Val_date).days / 365)
            elif calendar.isleap(Val_date.year + 2) is True and couponfreq == 1:
                if (
                    pd.to_datetime(Val_date)
                    < pd.to_datetime(datetime.date(Val_date.year + 2, 2, 29))
                    <= Coupon_date_list[j]
                ):
                    day_count_list.append((Coupon_date_list[j] - Val_date).days / 366)
                else:
                    day_count_list.append((Coupon_date_list[j] - Val_date).days / 365)
            elif calendar.isleap(Val_date.year + 3) is True and couponfreq == 1:
                if (
                    pd.to_datetime(Val_date)
                    < pd.to_datetime(datetime.date(Val_date.year + 3, 2, 29))
                    <= Coupon_date_list[j]
                ):
                    day_count_list.append((Coupon_date_list[j] - Val_date).days / 366)
                else:
                    day_count_list.append((Coupon_date_list[j] - Val_date).days / 365)
            elif couponfreq == 1:
                day_count_list.append((Coupon_date_list[j] - Val_date).days / 365)
            elif calendar.isleap(Coupon_date_list[j].year) is True:
                day_count_list.append((Coupon_date_list[j] - Val_date).days / 366)
            else:
                day_count_list.append((Coupon_date_list[j] - Val_date).days / 365)

        return day_count_list

    # Act/365A
    if Convention == "Act/365A":
        day_count_list = []
        if type(Coupon_date_list) == pd.core.series.Series:
            Val_date = pd.to_datetime(Val_date)
        n = len(Coupon_date_list)
        for j in range(0, n):
            if (Coupon_date_list[j].year - Val_date.year) >= 4:
                day_count_list.append((Coupon_date_list[j] - Val_date).days / 366)

            elif calendar.isleap(Val_date.year) is True:
                if (
                    pd.to_datetime(Val_date)
                    <= pd.to_datetime(datetime.date(Val_date.year, 2, 29))
                    < Coupon_date_list[j]
                ):
                    day_count_list.append((Coupon_date_list[j] - Val_date).days / 366)
                elif (
                    pd.to_datetime(Val_date)
                    <= pd.to_datetime(datetime.date(Val_date.year + 4, 2, 29))
                    < Coupon_date_list[j]
                ):
                    day_count_list.append((Coupon_date_list[j] - Val_date).days / 366)
                else:
                    day_count_list.append((Coupon_date_list[j] - Val_date).days / 365)
            elif calendar.isleap(Val_date.year + 1) is True:
                if (
                    pd.to_datetime(Val_date)
                    <= pd.to_datetime(datetime.date(Val_date.year + 1, 2, 29))
                    < Coupon_date_list[j]
                ):
                    day_count_list.append((Coupon_date_list[j] - Val_date).days / 366)
                else:
                    day_count_list.append((Coupon_date_list[j] - Val_date).days / 365)
            elif calendar.isleap(Val_date.year + 2) is True:
                if (
                    pd.to_datetime(Val_date)
                    <= pd.to_datetime(datetime.date(Val_date.year + 2, 2, 29))
                    < Coupon_date_list[j]
                ):
                    day_count_list.append((Coupon_date_list[j] - Val_date).days / 366)
                else:
                    day_count_list.append((Coupon_date_list[j] - Val_date).days / 365)
            elif calendar.isleap(Val_date.year + 3) is True:
                if (
                    pd.to_datetime(Val_date)
                    <= pd.to_datetime(datetime.date(Val_date.year + 3, 2, 29))
                    < Coupon_date_list[j]
                ):
                    day_count_list.append((Coupon_date_list[j] - Val_date).days / 366)
                else:
                    day_count_list.append((Coupon_date_list[j] - Val_date).days / 365)

        return day_count_list

    # NL/365
    if Convention == "NL/365":
        day_count_list = []
        if type(Coupon_date_list) == pd.core.series.Series:
            Val_date = pd.to_datetime(Val_date)
        n = len(Coupon_date_list)
        for j in range(0, n):
            if (Coupon_date_list[j].year - Val_date.year) >= 4:
                day_count_list.append((Coupon_date_list[j] - Val_date).days / 366)

            elif calendar.isleap(Val_date.year) is True:
                if (Val_date) < pd.to_datetime(datetime.date(Val_date.year, 2, 29)) < Coupon_date_list[j]:
                    day_count_list.append((Coupon_date_list[j] - Val_date).days / 365)
                elif (
                    (Val_date) < pd.to_datetime(datetime.date(Val_date.year + 4, 2, 29)) < Coupon_date_list[j]
                ):
                    day_count_list.append((Coupon_date_list[j] - Val_date).days / 365)
                else:
                    day_count_list.append((Coupon_date_list[j] - Val_date - datetime.timedelta(1)).days / 365)
            elif calendar.isleap(Val_date.year + 1) is True:
                if (Val_date) < pd.to_datetime(datetime.date(Val_date.year + 1, 2, 29)) < Coupon_date_list[j]:
                    day_count_list.append((Coupon_date_list[j] - Val_date).days / 365)
                else:
                    day_count_list.append((Coupon_date_list[j] - Val_date - datetime.timedelta(1)).days / 365)
            elif calendar.isleap(Val_date.year + 2) is True:
                if (Val_date) < pd.to_datetime(datetime.date(Val_date.year + 2, 2, 29)) < Coupon_date_list[j]:
                    day_count_list.append((Coupon_date_list[j] - Val_date).days / 365)
                else:
                    day_count_list.append((Coupon_date_list[j] - Val_date - datetime.timedelta(1)).days / 365)
            elif calendar.isleap(Val_date.year + 3) is True:
                if (Val_date) < pd.to_datetime(datetime.date(Val_date.year + 3, 2, 29)) < Coupon_date_list[j]:
                    day_count_list.append((Coupon_date_list[j] - Val_date).days / 365)
                else:
                    day_count_list.append((Coupon_date_list[j] - Val_date - datetime.timedelta(1)).days / 365)

        return day_count_list

    # Act/Act-ISDA
    if Convention == "Act/Act-ISDA":
        day_count_list = []
        n = len(Coupon_date_list)
        end_year = [0] * n
        year_2_diff = [0] * n
        diff_second = [0] * n
        total_sum = [0] * n
        for j in range(0, n):
            if Val_date == Coupon_date_list[j]:
                return 0.0
            else:
                Val_date = datetime.datetime.combine(Val_date, datetime.datetime.min.time())
                Coupon_date_list[j] = datetime.datetime.combine(
                    Coupon_date_list[j], datetime.datetime.min.time()
                )

                start_year = Val_date.year
                end_year[j] = Coupon_date_list[j].year
                year_1_diff = 366 if calendar.isleap(start_year) else 365
                year_2_diff[j] = 366 if calendar.isleap(end_year[j]) else 365

                total_sum[j] = end_year[j] - start_year - 1
                diff_first = datetime.datetime(start_year + 1, 1, 1) - Val_date
                total_sum[j] += diff_first.days / year_1_diff
                diff_second[j] = Coupon_date_list[j] - datetime.datetime(end_year[j], 1, 1)
                total_sum[j] += diff_second[j].days / year_2_diff[j]
                day_count_list.append(total_sum[j])
        return day_count_list

    # Act/Act_ICMA
    if Convention == "Act/Act_ICMA":
        day_count_list = []
        if type(Coupon_date_list) == pd.core.series.Series:
            Val_date = pd.to_datetime(Val_date)
        n = len(Coupon_date_list)
        for j in range(0, n):
            day_count_list.append(
                (Coupon_date_list[j] - Val_date).days
                / (((Next_coupon_date_list[j] - Val_date).days) * couponfreq)
            )
        return day_count_list

    # Business / 252
    if Convention == "Business/252":
        day_count_list = []
        if type(Coupon_date_list) == pd.core.series.Series:
            Coupon_date_list = Coupon_date_list.values.astype("datetime64[D]")
        if type(holiday_list) == pd.core.series.Series:
            holiday_list = holiday_list.values.astype("datetime64[D]")
        n = len(Coupon_date_list)
        for j in range(0, n):
            day_count_list.append(
                (np.busday_count(Val_date, Coupon_date_list[j], "1111100", holiday_list)) / 252
            )
        return day_count_list


def Coup_count(
    Start_date_list,
    Coupon_date_list,
    Convention,
    Maturity_date="none",
    couponfreq=1,
    Next_coupon_date_list=[],
    holiday_list=[],
):
    # 30/360 Bond Basis
    if Convention == "30/360":
        day_count_list = []
        n = len(Coupon_date_list)
        for j in range(0, n):
            if Coupon_date_list[j].day == 31 and (
                Start_date_list[j].day == 30 or Start_date_list[j].day == 31
            ):
                x = 30
            else:
                x = Coupon_date_list[j].day
            if Start_date_list[j].day == 31:
                y = 30
            else:
                y = Start_date_list[j].day
            day_count_list.append(
                (
                    (Coupon_date_list[j].year - Start_date_list[j].year) * 360
                    + (Coupon_date_list[j].month - Start_date_list[j].month) * 30
                    + (x - y)
                )
                / 360
            )
        j = j + 1
        return day_count_list

    # 30/360 US
    if Convention == "30/360 US":
        day_count_list = []
        n = len(Coupon_date_list)
        for j in range(0, n):
            if (
                (Start_date_list[j] + datetime.timedelta(1)).month == 3
                and ((Start_date_list[j] + datetime.timedelta(1)).day == 1)
                and ((Coupon_date_list[j] + datetime.timedelta(1)).month == 3)
                and ((Coupon_date_list[j] + datetime.timedelta(1)).day == 1)
            ):
                x = 30
            elif Coupon_date_list[j].day == 31 and (
                Start_date_list[j].day == 30 or Start_date_list[j].day == 31
            ):
                x = 30
            else:
                x = Coupon_date_list[j].day

            if ((Start_date_list[j] + datetime.timedelta(1)).month == 3) and (
                (Start_date_list[j] + datetime.timedelta(1)).day == 1
            ):
                y = 30
            elif Start_date_list[j].day == 31:
                y = 30
            else:
                y = Start_date_list[j].day
            day_count_list.append(
                (
                    (Coupon_date_list[j].year - Start_date_list[j].year) * 360
                    + (Coupon_date_list[j].month - Start_date_list[j].month) * 30
                    + (x - y)
                )
                / 360
            )
        return day_count_list

    # 30E/360
    if Convention == "30E/360":
        day_count_list = []
        n = len(Coupon_date_list)
        for j in range(0, n):
            if Coupon_date_list[j].day == 31:
                x = 30
            else:
                x = Coupon_date_list[j].day
            if Start_date_list[j].day == 31:
                y = 30
            else:
                y = Start_date_list[j].day
            day_count_list.append(
                (
                    (Coupon_date_list[j].year - Start_date_list[j].year) * 360
                    + (Coupon_date_list[j].month - Start_date_list[j].month) * 30
                    + (x - y)
                )
                / 360
            )
        return day_count_list

    # 30E/360 ISDA
    if Convention == "30E/360":
        day_count_list = []
        n = len(Coupon_date_list)
        for j in range(0, n):
            if Coupon_date_list[j].day == 31:
                x = 30
            elif (
                ((Coupon_date_list[j] + datetime.timedelta(1)).month == 3)
                and ((Coupon_date_list[j] + datetime.timedelta(1)).day == 1)
                and (Coupon_date_list[j] != pd.to_datetime(Maturity_date))
            ):
                x = 30
            else:
                x = Coupon_date_list[j].day
            if Start_date_list[j].day == 31:
                y = 30
            elif ((Start_date_list[j] + datetime.timedelta(1)).month == 3) and (
                (Start_date_list[j] + datetime.timedelta(1)).day == 1
            ):
                y = 30
            else:
                y = Start_date_list[j].day
            day_count_list.append(
                (
                    (Coupon_date_list[j].year - Start_date_list[j].year) * 360
                    + (Coupon_date_list[j].month - Start_date_list[j].month) * 30
                    + (x - y)
                )
                / 360
            )
        return day_count_list

    # 30E+/360 ISDA
    if Convention == "30E+/360":
        day_count_list = []
        n = len(Coupon_date_list)
        R_Coupon_date_list = [0] * n
        for j in range(0, n):
            if (Coupon_date_list[j].day) == 31:
                R_Coupon_date_list[j] = Coupon_date_list[j] + datetime.timedelta(1)
                x = R_Coupon_date_list[j].day
            else:
                R_Coupon_date_list[j] = Coupon_date_list[j]
                x = R_Coupon_date_list[j].day
            if Start_date_list[j].day == 31:
                y = 30
            else:
                y = Start_date_list[j].day
            day_count_list.append(
                (
                    (R_Coupon_date_list[j].year - Start_date_list[j].year) * 360
                    + (R_Coupon_date_list[j].month - Start_date_list[j].month) * 30
                    + (x - y)
                )
                / 360
            )
        return day_count_list

    # Act/360
    if Convention == "Act/360":
        day_count_list = []
        if type(Coupon_date_list) == pd.core.series.Series:
            Coupon_date_list = pd.to_datetime(Coupon_date_list)
        n = len(Coupon_date_list)
        for j in range(0, n):
            day_count_list.append((Coupon_date_list[j] - Start_date_list[j]).days / 360)
        return day_count_list

    # Act/365
    if Convention == "Act/365":
        day_count_list = []
        if type(Coupon_date_list) == pd.core.series.Series:
            Coupon_date_list = pd.to_datetime(Coupon_date_list)
        n = len(Coupon_date_list)
        for j in range(0, n):
            day_count_list.append((Coupon_date_list[j] - Start_date_list[j]).days / 365)
        return day_count_list

    # Act/365L
    if Convention == "Act/365L":
        day_count_list = []
        if type(Coupon_date_list) == pd.core.series.Series:
            Coupon_date_list = pd.to_datetime(Coupon_date_list)
        n = len(Coupon_date_list)
        for j in range(0, n):
            if couponfreq == 1 and (Coupon_date_list[j].year - Start_date_list[j].year) >= 4:
                day_count_list.append((Coupon_date_list[j] - Start_date_list[j]).days / 366)

            elif calendar.isleap(Start_date_list[j].year) is True and couponfreq == 1:
                if (
                    pd.to_datetime(Start_date_list[j])
                    < pd.to_datetime(datetime.date(Start_date_list[j].year, 2, 29))
                    <= Coupon_date_list[j]
                ):
                    day_count_list.append((Coupon_date_list[j] - Start_date_list[j]).days / 366)
                elif (
                    pd.to_datetime(Start_date_list[j])
                    < pd.to_datetime(datetime.date(Start_date_list[j].year + 4, 2, 29))
                    <= Coupon_date_list[j]
                ):
                    day_count_list.append((Coupon_date_list[j] - Start_date_list[j]).days / 366)
                else:
                    day_count_list.append((Coupon_date_list[j] - Start_date_list[j]).days / 365)
            elif calendar.isleap(Start_date_list[j].year + 1) is True and couponfreq == 1:
                if (
                    pd.to_datetime(Start_date_list[j])
                    < pd.to_datetime(datetime.date(Start_date_list[j].year + 1, 2, 29))
                    <= Coupon_date_list[j]
                ):
                    day_count_list.append((Coupon_date_list[j] - Start_date_list[j]).days / 366)
                else:
                    day_count_list.append((Coupon_date_list[j] - Start_date_list[j]).days / 365)
            elif calendar.isleap(Start_date_list[j].year + 2) is True and couponfreq == 1:
                if (
                    pd.to_datetime(Start_date_list[j])
                    < pd.to_datetime(datetime.date(Start_date_list[j].year + 2, 2, 29))
                    <= Coupon_date_list[j]
                ):
                    day_count_list.append((Coupon_date_list[j] - Start_date_list[j]).days / 366)
                else:
                    day_count_list.append((Coupon_date_list[j] - Start_date_list[j]).days / 365)
            elif calendar.isleap(Start_date_list[j].year + 3) is True and couponfreq == 1:
                if (
                    pd.to_datetime(Start_date_list[j])
                    < pd.to_datetime(datetime.date(Start_date_list[j].year + 3, 2, 29))
                    <= Coupon_date_list[j]
                ):
                    day_count_list.append((Coupon_date_list[j] - Start_date_list[j]).days / 366)
                else:
                    day_count_list.append((Coupon_date_list[j] - Start_date_list[j]).days / 365)
            elif couponfreq == 1:
                day_count_list.append((Coupon_date_list[j] - Start_date_list[j]).days / 365)
            elif calendar.isleap(Coupon_date_list[j].year) is True:
                day_count_list.append((Coupon_date_list[j] - Start_date_list[j]).days / 366)
            else:
                day_count_list.append((Coupon_date_list[j] - Start_date_list[j]).days / 365)

        return day_count_list

    # Act/365A
    if Convention == "Act/365A":
        day_count_list = []
        if type(Coupon_date_list) == pd.core.series.Series:
            Coupon_date_list = pd.to_datetime(Coupon_date_list)
        n = len(Coupon_date_list)
        for j in range(0, n):
            if (Coupon_date_list[j].year - Start_date_list[j].year) >= 4:
                day_count_list.append((Coupon_date_list[j] - Start_date_list[j]).days / 366)

            elif calendar.isleap(Start_date_list[j].year) is True:
                if (
                    pd.to_datetime(Start_date_list[j])
                    <= pd.to_datetime(datetime.date(Start_date_list[j].year, 2, 29))
                    < Coupon_date_list[j]
                ):
                    day_count_list.append((Coupon_date_list[j] - Start_date_list[j]).days / 366)
                elif (
                    pd.to_datetime(Start_date_list[j])
                    <= pd.to_datetime(datetime.date(Start_date_list[j].year + 4, 2, 29))
                    < Coupon_date_list[j]
                ):
                    day_count_list.append((Coupon_date_list[j] - Start_date_list[j]).days / 366)
                else:
                    day_count_list.append((Coupon_date_list[j] - Start_date_list[j]).days / 365)
            elif calendar.isleap(Start_date_list[j].year + 1) is True:
                if (
                    pd.to_datetime(Start_date_list[j])
                    <= pd.to_datetime(datetime.date(Start_date_list[j].year + 1, 2, 29))
                    < Coupon_date_list[j]
                ):
                    day_count_list.append((Coupon_date_list[j] - Start_date_list[j]).days / 366)
                else:
                    day_count_list.append((Coupon_date_list[j] - Start_date_list[j]).days / 365)
            elif calendar.isleap(Start_date_list[j].year + 2) is True:
                if (
                    pd.to_datetime(Start_date_list[j])
                    <= pd.to_datetime(datetime.date(Start_date_list[j].year + 2, 2, 29))
                    < Coupon_date_list[j]
                ):
                    day_count_list.append((Coupon_date_list[j] - Start_date_list[j]).days / 366)
                else:
                    day_count_list.append((Coupon_date_list[j] - Start_date_list[j]).days / 365)
            elif calendar.isleap(Start_date_list[j].year + 3) is True:
                if (
                    pd.to_datetime(Start_date_list[j])
                    <= pd.to_datetime(datetime.date(Start_date_list[j].year + 3, 2, 29))
                    < Coupon_date_list[j]
                ):
                    day_count_list.append((Coupon_date_list[j] - Start_date_list[j]).days / 366)
                else:
                    day_count_list.append((Coupon_date_list[j] - Start_date_list[j]).days / 365)

        return day_count_list

    # NL/365
    if Convention == "NL/365":
        day_count_list = []
        if type(Coupon_date_list) == pd.core.series.Series:
            Coupon_date_list = pd.to_datetime(Coupon_date_list)
        n = len(Coupon_date_list)
        for j in range(0, n):
            if (Coupon_date_list[j].year - Start_date_list[j].year) >= 4:
                day_count_list.append((Coupon_date_list[j] - Start_date_list[j]).days / 366)

            elif calendar.isleap(Start_date_list[j].year) is True:
                if (
                    (Start_date_list[j])
                    < pd.to_datetime(datetime.date(Start_date_list[j].year, 2, 29))
                    < Coupon_date_list[j]
                ):
                    day_count_list.append((Coupon_date_list[j] - Start_date_list[j]).days / 365)
                elif (
                    (Start_date_list[j])
                    < pd.to_datetime(datetime.date(Start_date_list[j].year + 4, 2, 29))
                    < Coupon_date_list[j]
                ):
                    day_count_list.append((Coupon_date_list[j] - Start_date_list[j]).days / 365)
                else:
                    day_count_list.append(
                        (Coupon_date_list[j] - Start_date_list[j] - datetime.timedelta(1)).days / 365
                    )
            elif calendar.isleap(Start_date_list[j].year + 1) is True:
                if (
                    (Start_date_list[j])
                    < pd.to_datetime(datetime.date(Start_date_list[j].year + 1, 2, 29))
                    < Coupon_date_list[j]
                ):
                    day_count_list.append((Coupon_date_list[j] - Start_date_list[j]).days / 365)
                else:
                    day_count_list.append(
                        (Coupon_date_list[j] - Start_date_list[j] - datetime.timedelta(1)).days / 365
                    )
            elif calendar.isleap(Start_date_list[j].year + 2) is True:
                if (
                    (Start_date_list[j])
                    < pd.to_datetime(datetime.date(Start_date_list[j].year + 2, 2, 29))
                    < Coupon_date_list[j]
                ):
                    day_count_list.append((Coupon_date_list[j] - Start_date_list[j]).days / 365)
                else:
                    day_count_list.append(
                        (Coupon_date_list[j] - Start_date_list[j] - datetime.timedelta(1)).days / 365
                    )
            elif calendar.isleap(Start_date_list[j].year + 3) is True:
                if (
                    (Start_date_list[j])
                    < pd.to_datetime(datetime.date(Start_date_list[j].year + 3, 2, 29))
                    < Coupon_date_list[j]
                ):
                    day_count_list.append((Coupon_date_list[j] - Start_date_list[j]).days / 365)
                else:
                    day_count_list.append(
                        (Coupon_date_list[j] - Start_date_list[j] - datetime.timedelta(1)).days / 365
                    )

        return day_count_list

    # Act/Act-ISDA
    if Convention == "Act/Act-ISDA":
        day_count_list = []
        n = len(Coupon_date_list)
        end_year = [0] * n
        year_2_diff = [0] * n
        diff_second = [0] * n
        total_sum = [0] * n
        for j in range(0, n):
            if Start_date_list[j] == Coupon_date_list[j]:
                return 0.0
            else:
                Start_date_list[j] = datetime.datetime.combine(
                    Start_date_list[j], datetime.datetime.min.time()
                )
                Coupon_date_list[j] = datetime.datetime.combine(
                    Coupon_date_list[j], datetime.datetime.min.time()
                )

                start_year = Start_date_list[j].year
                end_year[j] = Coupon_date_list[j].year
                year_1_diff = 366 if calendar.isleap(start_year) else 365
                year_2_diff[j] = 366 if calendar.isleap(end_year[j]) else 365

                total_sum[j] = end_year[j] - start_year - 1
                diff_first = datetime.datetime(start_year + 1, 1, 1) - Start_date_list[j]
                total_sum[j] += diff_first.days / year_1_diff
                diff_second[j] = Coupon_date_list[j] - datetime.datetime(end_year[j], 1, 1)
                total_sum[j] += diff_second[j].days / year_2_diff[j]
                day_count_list.append(total_sum[j])
        return day_count_list

    # Act/Act_ICMA
    if Convention == "Act/Act_ICMA":
        day_count_list = []
        if type(Coupon_date_list) == pd.core.series.Series:
            Coupon_date_list = pd.to_datetime(Coupon_date_list)
        n = len(Coupon_date_list)
        for j in range(0, n):
            day_count_list.append(
                (Coupon_date_list[j] - Start_date_list[j]).days
                / (((Next_coupon_date_list[j] - Start_date_list[j]).days) * couponfreq)
            )
        return day_count_list

    # Business / 252
    if Convention == "Business/252":
        day_count_list = []
        if type(Coupon_date_list) == pd.core.series.Series:
            Coupon_date_list = Coupon_date_list.values.astype("datetime64[D]")
        if type(holiday_list) == pd.core.series.Series:
            holiday_list = holiday_list.values.astype("datetime64[D]")
        n = len(Coupon_date_list)
        for j in range(0, n):
            day_count_list.append(
                (np.busday_count(Start_date_list[j], Coupon_date_list[j], "1111100", holiday_list)) / 252
            )
        return day_count_list
