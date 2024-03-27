from datetime import datetime, timedelta
import logging

import numpy as np
import pandas as pd
from pandas.tseries.offsets import MonthEnd
from workdays import workday
import yearfrac as yf


class Apply_TimeSeries:
    def days_add(self, dataframe, col_name, new_col_name, days):
        dataframe[new_col_name] = dataframe[col_name] + pd.DateOffset(days=int(days))
        return dataframe

    def months_add(self, dataframe, col_name, new_col_name, months):
        dataframe[new_col_name] = dataframe[col_name] + pd.DateOffset(months=int(months))
        return dataframe

    def years_add(self, dataframe, col_name, new_col_name, years):
        dataframe[new_col_name] = dataframe[col_name] + pd.DateOffset(years=int(years))
        return dataframe

    def day(self, dataframe, colname, date):
        dataframe[colname] = dataframe[date].dt.day
        return dataframe

    def days(self, dataframe, colname, start_date, end_date):
        dataframe[[start_date, end_date]] = dataframe[[start_date, end_date]].apply(pd.to_datetime)
        dataframe[colname] = (dataframe[end_date] - dataframe[start_date]).dt.days
        return dataframe

    def week(self, dataframe, colname, date):
        mask = dataframe[date].isnull()
        dataframe.loc[mask, date] = datetime(1990, 1, 1)
        dataframe[colname] = dataframe[date].dt.isocalendar().week
        dataframe.loc[mask, date] = "-"
        dataframe[colname] = dataframe[colname].astype("object")
        dataframe.loc[mask, colname] = "-"
        return dataframe

    def date(self, dataframe, colname, year, month, day):
        dataframe[year] = pd.to_numeric(dataframe[year], downcast="integer", errors="coerce")
        dataframe[month] = pd.to_numeric(dataframe[month], downcast="integer", errors="coerce")
        dataframe[day] = pd.to_numeric(dataframe[day], downcast="integer", errors="coerce")

        df2 = dataframe[[year, month, day]].copy()
        df2.columns = ["year", "month", "day"]
        dataframe[colname] = pd.to_datetime(df2, errors="coerce")
        return dataframe

    def weekday(self, dataframe, colname, date, method):
        mask = dataframe[date].isnull()
        dataframe.loc[mask, date] = datetime(1990, 1, 1)
        dataframe[colname] = dataframe[date].dt.weekday
        for i in range(len(dataframe)):
            if method == "1":
                num = int(dataframe.loc[i, colname])
                num += 2
                if num > 7:
                    num = 0
                dataframe.loc[i, colname] = num
            elif method == "2":
                dataframe.loc[i, colname] = int(dataframe.loc[i, colname]) + 1
        dataframe.loc[mask, colname] = np.nan
        dataframe.loc[mask, date] = np.nan
        return dataframe

    def today(self, dataframe, colname):
        if len(dataframe) > 0:
            dataframe[colname] = pd.to_datetime("today")
            dataframe[colname] = dataframe[colname].dt.date
        else:
            dataframe = pd.DataFrame(columns=[colname])
            dataframe[colname] = [pd.to_datetime("today")]
            dataframe[colname] = dataframe[colname].dt.date
        return dataframe

    def day(self, dataframe, colname, date):
        dataframe[colname] = dataframe[date].dt.day
        return dataframe

    def days(self, dataframe, colname, start_date, end_date):
        dataframe[[start_date, end_date]] = dataframe[[start_date, end_date]].apply(pd.to_datetime)
        dataframe[colname] = (dataframe[end_date] - dataframe[start_date]).dt.days
        return dataframe

    def second(self, dataframe, colname, date):
        dataframe[colname] = dataframe[date].dt.second
        return dataframe

    def time(self, dataframe, colname, hour, minute, second):
        dataframe["year"] = 1990
        dataframe["month"] = 1
        dataframe["day"] = 1

        dataframe[hour] = pd.to_numeric(dataframe[hour], downcast="integer", errors="coerce")
        dataframe[minute] = pd.to_numeric(dataframe[minute], downcast="integer", errors="coerce")
        dataframe[second] = pd.to_numeric(dataframe[second], downcast="integer", errors="coerce")

        df2 = dataframe[["year", "month", "day", hour, minute, second]].copy()
        df2.columns = ["year", "month", "day", "hour", "minute", "second"]
        dataframe[colname] = pd.to_datetime(df2, errors="coerce")
        dataframe[colname] = dataframe[colname].dt.time
        dataframe.drop(["year", "month", "day"], axis=1, inplace=True)
        return dataframe

    def now(self, dataframe, colname):
        if len(dataframe) > 0:
            dataframe[colname] = pd.to_datetime("today")
        else:
            dataframe = pd.DataFrame(columns=[colname])
            dataframe[colname] = [pd.to_datetime("today")]
        return dataframe

    def month(self, dataframe, colname, date):
        dataframe[colname] = dataframe[date].dt.month
        return dataframe

    def days360(self, dataframe, colname, start_date, end_date, method):
        for i in range(len(dataframe)):
            start_day = dataframe.loc[i, start_date].day
            start_month = dataframe.loc[i, start_date].month
            start_year = dataframe.loc[i, start_date].year
            end_day = dataframe.loc[i, end_date].day
            end_month = dataframe.loc[i, end_date].month
            end_year = dataframe.loc[i, end_date].year

            if start_day == 31 or (
                method is False
                and start_month == 2
                and (
                    start_day == 29
                    or (start_day == 28 and dataframe.loc[i, start_date].is_leap_year is False)
                )
            ):
                start_day = 30

            if end_day == 31:
                if method is False and start_day != 30:
                    end_day = 1

                    if end_month == 12:
                        end_year += 1
                        end_month = 1
                    else:
                        end_month += 1
                else:
                    end_day = 30

            dataframe.loc[i, colname] = (
                end_day + end_month * 30 + end_year * 360 - start_day - start_month * 30 - start_year * 360
            )
        return dataframe

    def weeknum(self, dataframe, colname, date, method):
        mask = dataframe[date].isnull()
        dataframe.loc[mask, date] = datetime(1990, 1, 1)
        if method == "1":
            dataframe[colname] = dataframe[date].dt.week
        elif method == "2":
            dataframe[colname] = (dataframe[date] + pd.DateOffset(days=1)).dt.week
        dataframe.loc[mask, colname] = np.nan
        dataframe.loc[mask, date] = np.nan
        return dataframe

    def eomonth(self, dataframe, start_date, colname, months):
        dataframe[colname] = pd.to_datetime(dataframe[start_date], errors="coerce") + MonthEnd(int(months))
        return dataframe

    def hour(self, dataframe, colname, date):
        dataframe[colname] = dataframe[date].dt.hour
        return dataframe

    def year(self, dataframe, colname, date):
        dataframe[colname] = dataframe[date].dt.year
        return dataframe

    def minute(self, dataframe, colname, date):
        dataframe[colname] = dataframe[date].dt.minute
        return dataframe

    def yearfrac(self, dataframe, colname, start_date, end_date, basis):
        mask1 = dataframe[start_date].isnull()
        dataframe.loc[mask1, start_date] = datetime(1990, 1, 1)

        mask2 = dataframe[end_date].isnull()
        dataframe.loc[mask2, end_date] = datetime(2990, 1, 1)

        if basis == "1":
            for i in range(len(dataframe)):
                dataframe.loc[i, colname] = round(
                    yf.yearfrac(dataframe.loc[i, start_date], dataframe.loc[i, end_date]), 4
                )
        elif basis == "2":
            for i in range(len(dataframe)):
                dataframe.loc[i, colname] = round(
                    yf.yearfrac(dataframe.loc[i, start_date], dataframe.loc[i, end_date], "act_isda"), 4
                )
        elif basis == "3":
            for i in range(len(dataframe)):
                dataframe.loc[i, colname] = round(
                    yf.yearfrac(dataframe.loc[i, start_date], dataframe.loc[i, end_date], "30e360"), 4
                )
        elif basis == "4":
            for i in range(len(dataframe)):
                dataframe.loc[i, colname] = round(
                    yf.yearfrac(dataframe.loc[i, start_date], dataframe.loc[i, end_date], "30365"), 4
                )

        dataframe.loc[mask1, colname] = np.nan
        dataframe.loc[mask2, colname] = np.nan
        dataframe.loc[mask1, start_date] = np.nan
        dataframe.loc[mask2, end_date] = np.nan
        return dataframe

    def workdays(self, pos_data, hol_data, start_date, holiday, colname, days):
        if holiday:
            if len(hol_data) > 0:
                holidays = np.array(pd.to_datetime(hol_data[holiday], dayfirst=True))
                holidays = holidays.astype("datetime64[D]")
                holidays = holidays.tolist()
        else:
            holidays = []

        for i in range(len(pos_data)):
            if len(hol_data) > 0:
                pos_data.loc[i, colname] = workday(pos_data.loc[i, start_date].date(), int(days), holidays)
            else:
                pos_data.loc[i, colname] = workday(pos_data.loc[i, start_date].date(), int(days))

        return pos_data

    def workdayWE(self, start_date, days, holidays, weekends):
        def cmpWE(a, b):
            return (a > b) - (a < b)

        def _in_betweenWE(a, b, x):
            return a <= x <= b or b <= x <= a

        if days == 0:
            return start_date
        if days > 0 and start_date.weekday() in weekends:  #
            while start_date.weekday() in weekends:
                start_date -= timedelta(days=1)
        elif days < 0:
            while start_date.weekday() in weekends:
                start_date += timedelta(days=1)
        full_weeks, extra_days = divmod(days, 7 - len(weekends))
        new_date = start_date + timedelta(weeks=full_weeks)
        for i in range(extra_days):
            new_date += timedelta(days=1)
            while new_date.weekday() in weekends:
                new_date += timedelta(days=1)
        # to account for days=0 case
        while new_date.weekday() in weekends:
            new_date += timedelta(days=1)

        # avoid this if no holidays
        if holidays:
            delta = timedelta(days=1 * cmpWE(days, 0))
            # skip holidays that fall on weekends
            holidays = [x for x in holidays if x.weekday() not in weekends]
            holidays = [x for x in holidays if x != start_date]
            for d in sorted(holidays, reverse=(days < 0)):
                # if d in between start and current push it out one working day
                if _in_betweenWE(start_date, new_date, d):
                    new_date += delta
                    while new_date.weekday() in weekends:
                        new_date += delta
        return new_date

    def workdaysi(self, pos_data, hol_data, start_date, holiday, colname, days, weekend):
        if holiday:
            if len(hol_data) > 0:
                holidays = np.array(pd.to_datetime(hol_data[holiday], dayfirst=True))
                holidays = holidays.astype("datetime64[D]")
                holidays = holidays.tolist()
        else:
            holidays = []

        if len(weekend) == 0:
            weekend = [5, 6]
        pos_data.reset_index(drop=True, inplace=True)
        for i in range(len(pos_data)):
            if len(hol_data) > 0:
                pos_data.loc[i, colname] = self.workdayWE(
                    start_date=pos_data.loc[i, start_date].date(),
                    days=int(days),
                    holidays=holidays,
                    weekends=weekend,
                )
            else:
                pos_data.loc[i, colname] = self.workdayWE(
                    pos_data.loc[i, start_date].date(), int(days), [], weekend
                )

        return pos_data

    def networkdays(self, pos_data, hol_data, start_date, end_date, holiday, colname):
        mask1 = pos_data[start_date].isnull()
        mask2 = pos_data[end_date].isnull()

        pos_data.loc[mask1, start_date] = datetime(1990, 1, 1)
        pos_data.loc[mask2, end_date] = datetime(1990, 1, 1)

        pos_data[start_date] = pd.to_datetime(pos_data[start_date]).astype("datetime64[D]")
        pos_data[end_date] = pd.to_datetime(pos_data[end_date]).astype("datetime64[D]")

        if holiday:
            holidays = np.array(pd.to_datetime(hol_data[holiday], dayfirst=True))
            holidays = holidays.astype("datetime64[D]")
        else:
            holidays = []

        for i in range(len(pos_data)):
            pos_data.loc[i, colname] = np.busday_count(
                pos_data.loc[i, start_date].date(),
                pos_data.loc[i, end_date].date() + timedelta(days=1),
                holidays=holidays,
            )

        pos_data.loc[mask1, start_date] = np.nan
        pos_data.loc[mask2, end_date] = np.nan
        pos_data.loc[mask1, colname] = np.nan
        pos_data.loc[mask2, colname] = np.nan
        return pos_data

    def networkdaysi(self, pos_data, hol_data, start_date, end_date, holiday, colname, weekend):
        mask1 = pos_data[start_date].isnull()
        mask2 = pos_data[end_date].isnull()

        pos_data.loc[mask1, start_date] = datetime(1990, 1, 1)
        pos_data.loc[mask2, end_date] = datetime(1990, 1, 1)

        pos_data[start_date] = pd.to_datetime(pos_data[start_date]).astype("datetime64[D]")
        pos_data[end_date] = pd.to_datetime(pos_data[end_date]).astype("datetime64[D]")

        if holiday:
            if len(hol_data) > 0:
                holidays = np.array(pd.to_datetime(hol_data[holiday], dayfirst=True))
                holidays = holidays.astype("datetime64[D]")
        else:
            holiday = []

        if weekend == "":
            weekend = "1111100"

        for i in range(len(pos_data)):
            if len(hol_data) > 0:
                pos_data.loc[i, colname] = np.busday_count(
                    pos_data.loc[i, start_date].date(),
                    pos_data.loc[i, end_date].date() + timedelta(days=1),
                    holidays=holidays,
                    weekmask=weekend,
                )
            else:
                pos_data.loc[i, colname] = np.busday_count(
                    pos_data.loc[i, start_date].date(),
                    pos_data.loc[i, end_date].date() + timedelta(days=1),
                    weekmask=weekend,
                )

        pos_data.loc[mask1, start_date] = np.nan
        pos_data.loc[mask2, end_date] = np.nan
        pos_data.loc[mask1, colname] = np.nan
        pos_data.loc[mask2, colname] = np.nan
        return pos_data


def Time_Periods_Func(dataframe, config_dict):
    Ops_Func = Apply_TimeSeries()
    if config_dict["function"] == "Add Time Periods":
        if config_dict["inputs"]["Days"] != "":
            col_name = config_dict["inputs"]["Column_1"]
            new_col_name = config_dict["inputs"]["Column_name"]
            days = config_dict["inputs"]["Days"]
            output_data = Ops_Func.days_add(dataframe, col_name, new_col_name, days)
        elif config_dict["inputs"]["Months"] != "":
            col_name = config_dict["inputs"]["Column_1"]
            new_col_name = config_dict["inputs"]["Column_name"]
            months = config_dict["inputs"]["Months"]
            output_data = Ops_Func.months_add(dataframe, col_name, new_col_name, months)
        elif config_dict["inputs"]["Years"] != "":
            col_name = config_dict["inputs"]["Column_1"]
            new_col_name = config_dict["inputs"]["Column_name"]
            years = config_dict["inputs"]["Years"]
            output_data = Ops_Func.years_add(dataframe, col_name, new_col_name, years)
        return output_data
    elif config_dict["function"] == "Date":
        colname = config_dict["inputs"]["colname"]
        year = config_dict["inputs"]["year"]
        month = config_dict["inputs"]["month"]
        day = config_dict["inputs"]["day"]
        output_data = Ops_Func.date(dataframe, colname, year, month, day)
        return output_data
    elif config_dict["function"] == "Day":
        colname = config_dict["inputs"]["colname"]
        date = config_dict["inputs"]["date"]
        output_data = Ops_Func.day(dataframe, colname, date)
        return output_data
    elif config_dict["function"] == "Days":
        colname = config_dict["inputs"]["colname"]
        start_date = config_dict["inputs"]["start_date"]
        end_date = config_dict["inputs"]["end_date"]
        output_data = Ops_Func.days(dataframe, colname, start_date, end_date)
        return output_data
    elif config_dict["function"] == "Time":
        colname = config_dict["inputs"]["colname"]
        hour = config_dict["inputs"]["hour"]
        minute = config_dict["inputs"]["minute"]
        second = config_dict["inputs"]["second"]
        output_data = Ops_Func.time(dataframe, colname, hour, minute, second)
        return output_data
    elif config_dict["function"] == "Second":
        colname = config_dict["inputs"]["colname"]
        date = config_dict["inputs"]["date"]
        output_data = Ops_Func.second(dataframe, colname, date)
        return output_data
    elif config_dict["function"] == "Now":
        colname = config_dict["inputs"]["colname"]
        output_data = Ops_Func.now(dataframe, colname)
        return output_data
    elif config_dict["function"] == "Minute":
        colname = config_dict["inputs"]["colname"]
        date = config_dict["inputs"]["date"]
        output_data = Ops_Func.minute(dataframe, colname, date)
        return output_data
    elif config_dict["function"] == "Isoweeknum":
        colname = config_dict["inputs"]["colname"]
        date = config_dict["inputs"]["date"]
        output_data = Ops_Func.week(dataframe, colname, date)
        return output_data
    elif config_dict["function"] == "Eomonth":
        start_date = config_dict["inputs"]["start_date"]
        months = config_dict["inputs"]["months"]
        colname = config_dict["inputs"]["colname"]
        output_data = Ops_Func.eomonth(dataframe, start_date, colname, months)
        return output_data
    elif config_dict["function"] == "Days360":
        colname = config_dict["inputs"]["colname"]
        start_date = config_dict["inputs"]["start_date"]
        end_date = config_dict["inputs"]["end_date"]
        method = config_dict["inputs"]["method"]
        if method == "US":
            method = True
        else:
            method = False
        output_data = Ops_Func.days360(dataframe, colname, start_date, end_date, method)
        return output_data
    elif config_dict["function"] == "Edate":
        start_date = config_dict["inputs"]["start_date"]
        months = config_dict["inputs"]["months"]
        colname = config_dict["inputs"]["colname"]
        output_data = Ops_Func.months_add(dataframe, start_date, colname, months)
        return output_data
    elif config_dict["function"] == "Weeknum":
        colname = config_dict["inputs"]["colname"]
        date = config_dict["inputs"]["date"]
        method = config_dict["inputs"]["method"]
        output_data = Ops_Func.weeknum(dataframe, colname, date, method)
        return output_data
    elif config_dict["function"] == "Weekday":
        colname = config_dict["inputs"]["colname"]
        date = config_dict["inputs"]["date"]
        method = config_dict["inputs"]["method"]
        output_data = Ops_Func.weekday(dataframe, colname, date, method)
        return output_data
    elif config_dict["function"] == "Today":
        colname = config_dict["inputs"]["colname"]
        output_data = Ops_Func.today(dataframe, colname)
        return output_data
    elif config_dict["function"] == "Hour":
        colname = config_dict["inputs"]["colname"]
        date = config_dict["inputs"]["date"]
        output_data = Ops_Func.hour(dataframe, colname, date)
        return output_data
    elif config_dict["function"] == "Year":
        colname = config_dict["inputs"]["colname"]
        date = config_dict["inputs"]["date"]
        output_data = Ops_Func.year(dataframe, colname, date)
        return output_data
    elif config_dict["function"] == "Month":
        colname = config_dict["inputs"]["colname"]
        date = config_dict["inputs"]["date"]
        output_data = Ops_Func.month(dataframe, colname, date)
        return output_data
    elif config_dict["function"] == "Networkdays":
        colname = config_dict["inputs"]["colname"]
        start_date = config_dict["inputs"]["start_date"]
        end_date = config_dict["inputs"]["end_date"]
        holiday = config_dict["inputs"]["holiday"]
        pos_data = dataframe["pos_data"]
        hol_data = dataframe["hol_data"]
        output_data = Ops_Func.networkdays(pos_data, hol_data, start_date, end_date, holiday, colname)
        return output_data
    elif config_dict["function"] == "Yearfrac":
        colname = config_dict["inputs"]["colname"]
        start_date = config_dict["inputs"]["start_date"]
        end_date = config_dict["inputs"]["end_date"]
        basis = config_dict["inputs"]["basis"]
        output_data = Ops_Func.yearfrac(dataframe, colname, start_date, end_date, basis)
        return output_data
    elif config_dict["function"] == "Workdays":
        colname = config_dict["inputs"]["colname"]
        start_date = config_dict["inputs"]["start_date"]
        holiday = config_dict["inputs"]["holiday"]
        pos_data = dataframe["pos_data"]
        hol_data = dataframe["hol_data"]
        days = config_dict["inputs"]["days"]
        output_data = Ops_Func.workdays(pos_data, hol_data, start_date, holiday, colname, days)
        return output_data
    elif config_dict["function"] == "Workdays.Intl":
        colname = config_dict["inputs"]["colname"]
        start_date = config_dict["inputs"]["start_date"]
        holiday = config_dict["inputs"]["holiday"]
        pos_data = dataframe["pos_data"]
        hol_data = dataframe["hol_data"]
        days = config_dict["inputs"]["days"]
        weekend = config_dict["inputs"]["weekend"]
        w = []
        for i in weekend:
            w.append(int(i))
        output_data = Ops_Func.workdaysi(pos_data, hol_data, start_date, holiday, colname, days, w)
        return output_data
    elif config_dict["function"] == "Networkdays.Intl":
        colname = config_dict["inputs"]["colname"]
        start_date = config_dict["inputs"]["start_date"]
        end_date = config_dict["inputs"]["end_date"]
        holiday = config_dict["inputs"]["holiday"]
        pos_data = dataframe["pos_data"]
        hol_data = dataframe["hol_data"]
        weekend = config_dict["inputs"]["weekend"]
        output_data = Ops_Func.networkdaysi(
            pos_data, hol_data, start_date, end_date, holiday, colname, weekend
        )
        return output_data
