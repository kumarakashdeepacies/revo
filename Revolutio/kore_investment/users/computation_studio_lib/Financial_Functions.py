import calendar
from datetime import date, datetime, timedelta
import math

import QuantLib as ql
import numpy as np
import numpy_financial as npf
import pandas as pd
from scipy import optimize


class Other_func:
    def A_day_count(self, Settlement_date, Maturity_date, Convention, couponfreq=1, Next_coupon_date="none"):
        # 30/360 US
        if Convention == 1:
            if (
                (Settlement_date + timedelta(1)).month == 3
                and ((Settlement_date + timedelta(1)).day == 1)
                and ((Maturity_date + timedelta(1)).month == 3)
                and ((Maturity_date + timedelta(1)).day == 1)
            ):
                x = 30
            elif Maturity_date.day == 31 and (Settlement_date.day == 30 or Settlement_date.day == 31):
                x = 30
            else:
                x = Maturity_date.day
            if ((Settlement_date + timedelta(1)).month == 3) and ((Settlement_date + timedelta(1)).day == 1):
                y = 30
            elif Settlement_date.day == 31:
                y = 30
            else:
                y = Settlement_date.day
            return (
                (Maturity_date.year - Settlement_date.year) * 360
                + (Maturity_date.month - Settlement_date.month) * 30
                + (x - y)
            ) / 360

        # Act/360
        if Convention == 2:
            return (Maturity_date - Settlement_date).days / 360

        # Act/365
        if Convention == 3:
            return (Maturity_date - Settlement_date).days / 365

        # Act/Act-ISDA
        if Convention == 4:
            if Settlement_date == Maturity_date:
                return 0.0
            else:
                Settlement_date = datetime.combine(Settlement_date, datetime.min.time())
                Maturity_date = datetime.combine(Maturity_date, datetime.min.time())
                start_year = Settlement_date.year
                end_year = Maturity_date.year
                year_1_diff = 366 if calendar.isleap(start_year) else 365
                year_2_diff = 366 if calendar.isleap(end_year) else 365

                total_sum = end_year - start_year - 1
                diff_first = datetime(start_year + 1, 1, 1) - Settlement_date
                total_sum += diff_first.days / year_1_diff
                diff_second = Maturity_date - datetime(end_year, 1, 1)
                total_sum += diff_second.days / year_2_diff
                return total_sum

        # 30/360 Bond Basis
        if Convention == 5:
            if Maturity_date.day == 31 and (Settlement_date.day == 30 or Settlement_date.day == 31):
                x = 30
            else:
                x = Maturity_date.day
            if Settlement_date.day == 31:
                y = 30
            else:
                y = Settlement_date.day
            return (
                (Maturity_date.year - Settlement_date.year) * 360
                + (Maturity_date.month - Settlement_date.month) * 30
                + (x - y)
            ) / 360

    def frequency_fn(self, frequency):
        if frequency == "Monthly":
            m = 1
            n = 12
        elif frequency == "Semi_Annually":
            m = 6
            n = 2
        elif frequency == "Quarterly":
            m = 3
            n = 4
        elif frequency == "Annually":
            m = 12
            n = 1
        return m, n

    def basis_fn(self, basis):
        if basis == "US(NASD) 30/360":
            b = 1
        elif basis == "Actual/360":
            b = 2
        elif basis == "Actual/365":
            b = 3
        elif basis == "Actual/Actual":
            b = 4
        elif basis == "European 30/360":
            b = 5
        return b

    def prev_coup_date_fn(self, set_date, mat_date, frequency, dataframe=""):
        frequency_ql = Other_func.frequency_fn(self, frequency)[0]
        ql_set_date = ql.Date(set_date.day, set_date.month, set_date.year)
        ql_mat_date = ql.Date(mat_date.day, mat_date.month, mat_date.year)
        while ql_mat_date > ql_set_date:
            ql_mat_date -= ql.Period(frequency_ql, ql.Months)
        prev_coup_date = ql_mat_date
        return prev_coup_date.to_date()

    def next_coup_date_fn(self, set_date, mat_date, frequency, dataframe=""):
        frequency_ql = Other_func.frequency_fn(self, frequency)[0]
        ql_set_date = ql.Date(set_date.day, set_date.month, set_date.year)
        ql_mat_date = ql.Date(mat_date.day, mat_date.month, mat_date.year)
        while ql_mat_date > ql_set_date:
            ql_mat_date -= ql.Period(frequency_ql, ql.Months)
        next_coup_date = ql_mat_date + ql.Period(frequency_ql, ql.Months)
        return next_coup_date.to_date()

    def pricemat(self, setl, mat, issue, rate, yld, basis, df=""):
        if len(df) > 0:
            df["PRICEMAT"] = df.apply(
                lambda x: (
                    (
                        100
                        + (
                            Other_func.A_day_count(self, x[issue], x[mat], Other_func.basis_fn(self, basis))
                            * x[rate]
                            * 100
                        )
                    )
                    / (1 + (Other_func.A_day_count(x[setl], x[mat], Other_func.basis_fn(basis)) * x[yld]))
                )
                - (Other_func.A_day_count(x[issue], x[setl], Other_func.basis_fn(basis)) * (x[rate] * 100)),
                axis=1,
            )
            return df
        else:
            output = (
                (
                    100
                    + (
                        Other_func.A_day_count(self, issue, mat, Other_func.basis_fn(self, basis))
                        * rate
                        * 100
                    )
                )
                / (1 + (Other_func.A_day_count(self, setl, mat, Other_func.basis_fn(self, basis)) * yld))
            ) - (Other_func.A_day_count(self, issue, setl, Other_func.basis_fn(self, basis)) * rate * 100)
            return output

    def no_of_coupons_fn(self, set_date, mat_date, frequency, dataframe=""):
        if len(dataframe) > 0:
            dataframe["Number of Coupons"] = ""

            for i in range(len(dataframe)):
                if dataframe[frequency][i] == "Monthly":
                    frequency_ql = 1

                elif dataframe[frequency][i] == "Quarterly":
                    frequency_ql = 3

                elif dataframe[frequency][i] == "Semiannually":
                    frequency_ql = 6

                elif dataframe[frequency][i] == "Annually":
                    frequency_ql = 12

                set_date = dataframe.set_date[i]
                mat_date = dataframe.mat_date[i]
                ql_set_date = ql.Date(set_date.day, set_date.month, set_date.year)
                ql_mat_date = ql.Date(mat_date.day, mat_date.month, mat_date.year)
                count = 0
                while ql_mat_date > ql_set_date:
                    ql_mat_date -= ql.Period(frequency_ql, ql.Months)
                    count += 1
                dataframe["Number of Coupons"][i] = count
            return dataframe
        else:
            frequency_ql = Other_func.frequency_fn(self, frequency)[0]
            ql_set_date = ql.Date(set_date.day, set_date.month, set_date.year)
            ql_mat_date = ql.Date(mat_date.day, mat_date.month, mat_date.year)
            count = 0
            while ql_mat_date > ql_set_date:
                ql_mat_date -= ql.Period(frequency_ql, ql.Months)
                count += 1
            return count

    def no_of_coupon_fn(self, set_date, mat_date, frequency, dataframe=""):
        if len(dataframe) > 0:
            dataframe["Number of Coupons"] = ""
            set_date = dataframe[set_date]
            mat_date = dataframe[mat_date]
            for i in range(len(dataframe)):
                if dataframe[frequency][i] == "Monthly":
                    frequency_ql = 1

                elif dataframe[frequency][i] == "Quarterly":
                    frequency_ql = 3

                elif dataframe[frequency][i] == "Semiannually":
                    frequency_ql = 6

                elif dataframe[frequency][i] == "Annually":
                    frequency_ql = 12

                ql_set_date = ql.Date(set_date[i].day, set_date[i].month, set_date[i].year)
                ql_mat_date = ql.Date(mat_date[i].day, mat_date[i].month, mat_date[i].year)
                count = 0
                while ql_mat_date > ql_set_date:
                    ql_mat_date -= ql.Period(frequency_ql, ql.Months)
                    count += 1
                dataframe["Number of Coupons"][i] = count
            return dataframe
        else:
            frequency_ql = Other_func.frequency_fn(self, frequency)[0]
            ql_set_date = ql.Date(set_date.day, set_date.month, set_date.year)
            ql_mat_date = ql.Date(mat_date.day, mat_date.month, mat_date.year)
            count = 0
            while ql_mat_date > ql_set_date:
                ql_mat_date -= ql.Period(frequency_ql, ql.Months)
                count += 1
            return count

    def no_of_coupon_fn(self, set_date, mat_date, frequency, dataframe=""):
        if len(dataframe) > 0:
            dataframe["Number of Coupons"] = ""
            set_date = dataframe[set_date]
            mat_date = dataframe[mat_date]
            for i in range(len(dataframe)):
                if dataframe[frequency][i] == "Monthly":
                    frequency_ql = 1
                elif dataframe[frequency][i] == "Quarterly":
                    frequency_ql = 3
                elif dataframe[frequency][i] == "Semiannually":
                    frequency_ql = 6
                elif dataframe[frequency][i] == "Annually":
                    frequency_ql = 12
                ql_set_date = ql.Date(set_date[i].day, set_date[i].month, set_date[i].year)
                ql_mat_date = ql.Date(mat_date[i].day, mat_date[i].month, mat_date[i].year)
                count = 0
                while ql_mat_date > ql_set_date:
                    ql_mat_date -= ql.Period(frequency_ql, ql.Months)
                    count += 1
                dataframe["Number of Coupons"][i] = count
            return dataframe
        else:
            frequency_ql = Other_func.frequency_fn(self, frequency)[0]
            ql_set_date = ql.Date(set_date.day, set_date.month, set_date.year)
            ql_mat_date = ql.Date(mat_date.day, mat_date.month, mat_date.year)
            count = 0
            while ql_mat_date > ql_set_date:
                ql_mat_date -= ql.Period(frequency_ql, ql.Months)
                count += 1
            return count

    def price(self, settlement, maturity, rate, yld, red, freq, basis, df=""):
        if len(df) > 0:
            df["PRICE"] = ""
            for i in range(len(df)):

                setl = df[settlement][i]
                mat = df[maturity][i]
                setl_date = date(setl.year, setl.month, setl.day)

                f = Other_func.frequency_fn(self, df[freq][i][1])
                n = Other_func.no_of_coupons_fn(self, setl, mat, df[freq][i])
                nxt_coupdate = Other_func.next_coup_date_fn(self, setl, mat, df[freq][i])
                prev_coupdate = Other_func.prev_coup_date_fn(self, setl, mat, df[freq][i])
                dsc = Other_func.A_day_count(self, setl_date, nxt_coupdate, Other_func.basis_fn(self, basis))
                e = Other_func.A_day_count(
                    self, prev_coupdate, nxt_coupdate, Other_func.basis_fn(self, basis)
                )
                a = Other_func.A_day_count(self, prev_coupdate, setl_date, Other_func.basis_fn(self, basis))
                dsc_e = dsc / e
                a_e = a / e

                if n > 1:
                    part_a = (df[red][i]) / ((1 + ((df[yld][i]) / (f))) ** (n - 1 + dsc_e)) - (
                        100 * a_e * ((df[rate][i]) / f)
                    )
                    part_b = 0
                    for j in range(n):
                        b = (100 * (df[rate][i]) / (f)) / ((1 + ((df[yld][i]) / f)) ** (j + dsc_e))
                        part_b = part_b + b

                    df["PRICE"][i] = part_a + part_b

                else:
                    dsr = a - e
                    dsr_e = dsr / e
                    t1 = 100 * ((df[rate][i]) / f) + df[red][i]
                    t2 = 1 + dsr_e * ((df[yld][i]) / (f))
                    t3 = 100 * ((df[rate][i]) / f) * a_e
                    df["PRICE"][i] = ((t1) / (t2)) - t3

            return df
        else:
            setl = settlement
            mat = maturity
            setl_date = date(setl.year, setl.month, setl.day)

            f = Other_func.frequency_fn(self, freq)[1]
            n = Other_func.no_of_coupons_fn(self, setl, mat, freq)
            nxt_coupdate = Other_func.next_coup_date_fn(self, setl, mat, freq)
            prev_coupdate = Other_func.prev_coup_date_fn(self, setl, mat, freq)
            dsc = Other_func.A_day_count(self, setl_date, nxt_coupdate, Other_func.basis_fn(self, basis))
            e = Other_func.A_day_count(self, prev_coupdate, nxt_coupdate, Other_func.basis_fn(self, basis))
            a = Other_func.A_day_count(self, prev_coupdate, setl_date, Other_func.basis_fn(self, basis))
            dsc_e = dsc / e
            a_e = a / e
            if n > 1:
                part_a = (red) / ((1 + ((yld) / (f))) ** (n - 1 + dsc_e)) - (100 * a_e * ((rate) / f))
                part_b = 0
                for j in range(n):
                    b = (100 * (rate) / (f)) / ((1 + ((yld) / f)) ** (j + dsc_e))
                    part_b = part_b + b
                    price = part_a + part_b
                return price
            else:
                dsr = a - e
                dsr_e = dsr / e
                t1 = 100 * ((rate) / f) + red
                t2 = 1 + dsr_e * ((yld) / (f))
                t3 = 100 * ((rate) / f) * a_e
                price = ((t1) / (t2)) - t3
                return price

    def oddfprice_fn(
        self,
        Settlement_date,
        Maturity_date,
        Issue_date,
        Coupon_date,
        rate,
        yld,
        red,
        frequency,
        basis,
        dataframe="",
    ):
        otherFunctions = Other_func()
        if len(dataframe) > 0:
            dataframe["settlement_ql"] = ""
            dataframe["coupon_ql"] = ""
            dataframe["couponfreq"] = ""
            dataframe["mql"] = ""
            dataframe["settlement_ql"] = ""
            dataframe["coupon_ql"] = ""
            dataframe["prev_coup_date"] = ""
            dataframe["ip"] = ""
            dataframe["ipbyp"] = ""
            dataframe["n"] = ""
            dataframe["power"] = ""
            dataframe["v"] = ""
            dataframe["vp"] = ""
            dataframe["apn"] = ""
            dataframe["Price"] = ""

            set_date_column = pd.to_datetime(dataframe[Settlement_date])
            mat_date_column = pd.to_datetime(dataframe[Maturity_date])
            iss_date_column = pd.to_datetime(dataframe[Issue_date])
            coup_date_column = pd.to_datetime(dataframe[Coupon_date])

            for i in range(len(dataframe)):
                Settlement_date = set_date_column[i]
                set_date_date = date(Settlement_date.year, Settlement_date.month, Settlement_date.day)
                Maturity_date = mat_date_column[i]
                maturity_date_date = date(Maturity_date.year, Maturity_date.month, Maturity_date.day)
                Issue_date = iss_date_column[i]
                Coupon_date = coup_date_column[i]
                coupon_date_date = date(Coupon_date.year, Coupon_date.month, Coupon_date.day)

                dataframe["couponfreq"][i] = Other_func.frequency_fn(self, dataframe[frequency][i])[1]
                dataframe["mql"][i] = otherFunctions.frequency_fn(dataframe[frequency][i])[0]

                dataframe["prev_coup_date"][i] = otherFunctions.prev_coup_date_fn(
                    set_date_date, coupon_date_date, dataframe[frequency][i]
                )

                dataframe["ip"][i] = dataframe.couponfreq[i] * (
                    (1 + dataframe[yld][i]) ** (1 / dataframe.couponfreq[i]) - 1
                )
                dataframe["ipbyp"][i] = dataframe.ip[i] / dataframe.couponfreq[i]
                dataframe["v"][i] = 1 / (1 + dataframe[yld][i])
                dataframe["vp"][i] = 1 / (1 + dataframe.ipbyp[i])

                dataframe["power"][i] = otherFunctions.A_day_count(
                    set_date_date, coupon_date_date, otherFunctions.basis_fn(basis)
                ) / otherFunctions.A_day_count(
                    dataframe.prev_coup_date[i], coupon_date_date, otherFunctions.basis_fn(basis)
                )
                dataframe["n"][i] = maturity_date_date.year - coupon_date_date.year

                dataframe["apn"][i] = (
                    1 - dataframe.vp[i] ** (dataframe.n[i] * dataframe.couponfreq[i])
                ) / dataframe.ipbyp[i]

                if dataframe["n"][i] == 0:
                    dataframe["apn"][i] = (
                        1
                        - dataframe.vp[i]
                        ** (
                            (
                                otherFunctions.A_day_count(
                                    set_date_date, maturity_date_date, otherFunctions.basis_fn(basis)
                                )
                                // otherFunctions.A_day_count(
                                    dataframe.prev_coup_date[i],
                                    coupon_date_date,
                                    otherFunctions.basis_fn(basis),
                                )
                            )
                            + 1
                        )
                    ) / dataframe.ipbyp[i]
                    dataframe["Price"][i] = dataframe[red][i] * dataframe.v[i] ** (
                        otherFunctions.A_day_count(
                            set_date_date, maturity_date_date, otherFunctions.basis_fn(basis)
                        )
                    ) + 100 * (dataframe.rate[i] / dataframe.couponfreq[i]) * dataframe.apn[i] * (
                        dataframe.vp[i] ** dataframe.power[i]
                    )

                elif dataframe["n"][i] > 0:
                    dataframe["Price"][i] = dataframe[red][i] * dataframe.v[i] ** (dataframe.n[i]) * (
                        dataframe.vp[i] ** dataframe.power[i]
                    ) + 100 * (dataframe.rate[i] / dataframe.couponfreq[i]) * dataframe.apn[i] * (
                        dataframe.vp[i] ** dataframe.power[i]
                    )
            dataframe.drop(
                columns=[
                    "settlement_ql",
                    "coupon_ql",
                    "couponfreq",
                    "mql",
                    "settlement_ql",
                    "coupon_ql",
                    "prev_coup_date",
                    "ip",
                    "ipbyp",
                    "n",
                    "power",
                    "v",
                    "vp",
                    "apn",
                ],
                inplace=True,
            )
            return dataframe

        else:
            set_date_date = date(Settlement_date.year, Settlement_date.month, Settlement_date.day)
            maturity_date_date = date(Maturity_date.year, Maturity_date.month, Maturity_date.day)
            coupon_date_date = date(Coupon_date.year, Coupon_date.month, Coupon_date.day)

            basis = otherFunctions.basis_fn(basis)
            couponfreq = otherFunctions.frequency_fn(frequency)[1]

            prev_coup_date = otherFunctions.prev_coup_date_fn(set_date_date, coupon_date_date, frequency)
            ip = couponfreq * ((1 + yld) ** (1 / couponfreq) - 1)
            ipbyp = ip / couponfreq
            v = 1 / (1 + yld)
            vp = 1 / (1 + ipbyp)

            power = otherFunctions.A_day_count(
                set_date_date, coupon_date_date, basis
            ) / otherFunctions.A_day_count(prev_coup_date, coupon_date_date, basis)
            n = maturity_date_date.year - coupon_date_date.year

            apn = (1 - vp ** (n * couponfreq)) / ipbyp
            if n == 0:
                apn = (
                    1
                    - vp
                    ** (
                        (
                            otherFunctions.A_day_count(set_date_date, maturity_date_date, basis)
                            // otherFunctions.A_day_count(prev_coup_date, coupon_date_date, basis)
                        )
                        + 1
                    )
                ) / ipbyp
                price = red * v ** (
                    otherFunctions.A_day_count(set_date_date, maturity_date_date, basis)
                ) + 100 * (rate / couponfreq) * apn * (vp**power)

            elif n > 0:
                price = red * v ** (n) * (vp**power) + 100 * (rate / couponfreq) * apn * (vp**power)

            return price


class Financial_Func:
    def pv_fn(self, rate, nper, pmt, fv, when, dataframe=""):
        if len(dataframe) > 0:
            dataframe["Present Value"] = npf.pv(
                dataframe[rate], dataframe[nper], dataframe[pmt], dataframe[fv], when
            )
            return dataframe
        else:
            sub_df = pd.DataFrame(columns=["Present Value"])
            sub_df.loc[0] = npf.pv(float(rate), float(nper), float(pmt), float(fv), when)
            return sub_df

    def fv_fn(self, rate, nper, pmt, pv, when, dataframe=""):
        if len(dataframe) > 0:
            dataframe["Future Value"] = npf.fv(
                dataframe[rate], dataframe[nper], dataframe[pmt], dataframe[pv], when
            )
            return dataframe
        else:
            sub_df = pd.DataFrame(columns=["Future Value"])
            sub_df.loc[0] = npf.fv(float(rate), float(nper), float(pmt), float(pv), when)
            return sub_df

    def pmt_fn(self, rate, nper, pv, fv, when, dataframe=""):
        if len(dataframe) > 0:
            dataframe["Payment"] = npf.pmt(
                dataframe[rate], dataframe[nper], dataframe[pv], dataframe[fv], when
            )
            return dataframe
        else:
            sub_df = pd.DataFrame(columns=["Payment"])
            sub_df.loc[0] = npf.pmt(float(rate), float(nper), float(pv), float(fv), when)
            return sub_df

    def nper_fn(self, rate, pmt, pv, fv, when, dataframe=""):
        if len(dataframe) > 0:
            dataframe["No of Periods"] = npf.nper(
                dataframe[rate], dataframe[pmt], dataframe[pv], dataframe[fv], when
            )
            return dataframe
        else:
            sub_df = pd.DataFrame(columns=["No of Periods"])
            sub_df.loc[0] = npf.nper(float(rate), float(pmt), float(pv), float(fv), when)
            return sub_df

    def rate_fn(self, nper, pmt, pv, fv, when, dataframe=""):
        if len(dataframe) > 0:
            dataframe["Rate"] = npf.rate(dataframe[nper], dataframe[pmt], dataframe[pv], dataframe[fv], when)
            return dataframe
        else:
            sub_df = pd.DataFrame(columns=["Rate"])
            sub_df.loc[0] = npf.rate(float(nper), float(pmt), float(pv), float(fv), when)
            return sub_df

    def npv_fn(self, dataframe, cf_col, rate):
        sub_df = pd.DataFrame(columns=["Net Present Value"])
        sub_df.loc[0] = (dataframe[cf_col] / (1 + rate) ** np.arange(1, len(dataframe[cf_col]) + 1)).sum(
            axis=0
        )
        return sub_df

    def irr_fn(self, dataframe, cf_col):
        sub_df = pd.DataFrame(columns=["Internal Rate of Return"])
        sub_df.loc[0] = npf.irr(dataframe[cf_col])
        return sub_df

    def mirr_fn(self, dataframe, cf_col, finance_rate, reinvest_rate):
        sub_df = pd.DataFrame(columns=["Modified Internal Rate of Return"])
        sub_df.loc[0] = npf.mirr(dataframe[cf_col], finance_rate, reinvest_rate)
        return sub_df

    def xnpv_fn(self, dataframe, rate, cf_col, cf_dates_col):
        cf_tup = []
        for i in range(len(dataframe[cf_col])):
            sub = [dataframe[cf_dates_col][i], dataframe[cf_col][i]]
            cf_tup.append(tuple(sub))

        t0 = min(cf_tup, key=lambda t: t[0])[0]

        sub_df = pd.DataFrame(columns=["NPV of Irregular Cashflows"])
        sub_df.loc[0] = sum([cf / (1 + rate) ** ((t - t0).days / 365.0) for (t, cf) in cf_tup])
        return sub_df

    def xirr_fn(self, dataframe, cf_col, cf_dates_col, guess=0.1):

        cf_tup = []
        for i in range(len(dataframe[cf_col])):
            sub = [dataframe[cf_dates_col][i], dataframe[cf_col][i]]
            cf_tup.append(tuple(sub))

        def xnpv(rate, cf_tup):
            t0 = min(cf_tup, key=lambda t: t[0])[0]
            return sum([cf / (1 + rate) ** ((t - t0).days / 365.0) for (t, cf) in cf_tup])

        try:
            outc = optimize.newton(lambda r: xnpv(r, cf_tup), guess, maxiter=100)
            if outc.imag == 0:
                irr_val = outc
            else:
                raise
        except (RuntimeError, OverflowError):
            try:
                outc = optimize.newton(lambda r: xnpv(r, cf_tup), -guess, maxiter=100)
                if outc.imag == 0:
                    irr_val = outc
                else:
                    raise
            except (RuntimeError, OverflowError):
                return float("NaN")

        sub_df = pd.DataFrame(columns=["IRR of Irregular Cashflows"])
        sub_df.loc[0] = irr_val
        return sub_df

    def ipmt_fn(self, rate, period, nper, m, loan, fv, when):
        sub_df = pd.DataFrame(columns=["Interest Payment"])
        sub_df.loc[0] = float(npf.ipmt(rate / m, period, nper * m, loan, fv, when))
        return sub_df

    def ppmt_fn(self, rate, period, nper, m, loan, fv, when):
        sub_df = pd.DataFrame(columns=["Principal Payment"])
        sub_df.loc[0] = float(npf.ppmt(rate / m, period, nper * m, loan, fv, when))
        return sub_df

    def ispmt_fn(self, rate, period, nper, m, pv):
        sub_df = pd.DataFrame(columns=["Interest Payment for a Specific Period"])
        rate = rate / (m * 100)
        nper = nper * m
        principal = pv / nper
        balance = [pv]
        i = 0
        while i < nper:
            red_bal = balance[i] - principal
            balance.append(red_bal)
            i += 1
        ispmt = []
        i = 0
        for i in range(len(balance)):
            fn = balance[i] * rate
            ispmt.append(fn)
            i += 1
        sub_df.loc[0] = ispmt[period - 1]
        return sub_df

    def cumipmt_fn(self, rate, period, nper, m, loan, fv, when, start_period, end_period):
        sub_df = pd.DataFrame(columns=["Cumulative Interest Payment"])
        ipmt_list = []
        for i in range(start_period, end_period + 1):
            ipmt_list.append(npf.ipmt(rate / m, i, nper * m, loan, fv, when))

        sub_df.loc[0] = sum(ipmt_list)
        return sub_df

    def cumprinc_fn(self, rate, period, nper, m, loan, fv, when, start_period, end_period):
        sub_df = pd.DataFrame(columns=["Cumulative Principal Payment"])
        ipmt_list = []
        for i in range(start_period, end_period + 1):
            ipmt_list.append(npf.ppmt(rate / m, i, nper * m, loan, fv, when))

        sub_df.loc[0] = sum(ipmt_list)
        return sub_df

    def amortisation_table_fn(self, rate, nper, m, loan, fv, when):
        sub_df = pd.DataFrame(
            columns=[
                "Time Period",
                "Loan O/S at Start",
                "Periodic Installment",
                "Principal",
                "Interest",
                "Loan O/S at End",
            ]
        )
        time_list = []
        loan_start_list = []
        princ_list = []
        int_list = []
        emi_list = []
        loan_end_list = []

        for i in range(1, nper * m + 1):
            time_list.append(i)

            ppmt = float(npf.ppmt(rate / m, i, nper * m, loan, -fv, when))
            princ_list.append(ppmt)

            ipmt = float(npf.ipmt(rate / m, i, nper * m, loan, -fv, when))
            int_list.append(ipmt)

            emi_list.append(ipmt + ppmt)

        sub_df["Time Period"] = time_list
        sub_df["Principal"] = princ_list
        sub_df["Interest"] = int_list
        sub_df["Periodic Installment"] = emi_list

        loan_end_list.append(loan + sub_df.loc[0, "Principal"])
        loan_start_list.append(loan)

        for i in range(1, nper * m):
            loan_end_list.append(loan_end_list[i - 1] + princ_list[i])
            loan_start_list.append(loan_end_list[i - 1])

        sub_df["Loan O/S at Start"] = loan_start_list
        sub_df["Loan O/S at End"] = loan_end_list

        for i in sub_df.columns:
            sub_df[i] = np.round(sub_df[i], 4)

        return sub_df

    def dollarde(self, fractional_dollar, fraction, dataframe=""):
        if len(dataframe) > 0:
            dataframe["Dollar Decimal"] = dataframe.apply(
                lambda x: (
                    int(x[fractional_dollar])
                    + (x[fractional_dollar] - int(x[fractional_dollar]))
                    / ((int(x[fraction])) / pow(10, (len(str(x[fraction])) - 2)))
                ),
                axis=1,
            )
            return dataframe
        else:
            sub_df = pd.DataFrame(columns=["Dollar Decimal"])
            sub_df.loc[0] = int(fractional_dollar) + (
                (fractional_dollar - int(fractional_dollar))
                * 100
                / (int(fraction) / pow(10, (len(str(int(fraction))) - 2)))
            )
            return sub_df

    def dollarfr(self, decimal_dollar, fraction, dataframe=""):
        if len(dataframe) > 0:
            dataframe["Dollar Fraction"] = dataframe.apply(
                lambda x: (
                    int(x[decimal_dollar])
                    + (x[decimal_dollar] - int(x[decimal_dollar]))
                    * (int(x[fraction]) / pow(10, (len(str(x[fraction]))) - 2))
                ),
                axis=1,
            )
            return dataframe
        else:
            sub_df = pd.DataFrame(columns=["Dollar Fraction"])
            sub_df.loc[0] = int(decimal_dollar) + (
                (decimal_dollar - int(decimal_dollar))
                * (int(fraction) / (pow(10, (len(str(int(fraction)))))))
            )
            return sub_df

    def received(self, setl, mat, invst, disc, basis, dataframe=""):
        otherFunctions = Other_func()
        if len(dataframe) > 0:
            dataframe["Received"] = dataframe.apply(
                lambda x: (
                    (x[invst])
                    / (
                        1
                        - x[disc]
                        * (otherFunctions.A_day_count(x[setl], x[mat], otherFunctions.basis_fn(basis)))
                    )
                ),
                axis=1,
            )
            return dataframe
        else:
            sub_df = pd.DataFrame(columns=["Received"])
            sub_df.loc[0] = invst / (
                1 - (disc * otherFunctions.A_day_count(setl, mat, otherFunctions.basis_fn(basis)))
            )
            return sub_df

    def pricedisc(self, setl, mat, disc, red, basis, df=""):
        otherFunctions = Other_func()
        if len(df) > 0:
            df["Price Discount"] = df.apply(
                lambda x: (
                    (x[red])
                    - (
                        (x[red])
                        * (x[disc])
                        * (otherFunctions.A_day_count(x[setl], x[mat], otherFunctions.basis_fn(basis)))
                    )
                ),
                axis=1,
            )
            return df
        else:
            sub_df = pd.DataFrame(columns=["Price Discount"])
            sub_df.loc[0] = (red) - (
                (red) * (disc) * (otherFunctions.A_day_count(setl, mat, otherFunctions.basis_fn(basis)))
            )
            return sub_df

    def pricemat(self, setl, mat, issue, rate, yld, basis, df=""):
        otherFunctions = Other_func()
        if len(df) > 0:
            df["Price Maturity"] = df.apply(
                lambda x: (
                    (
                        100
                        + (
                            otherFunctions.A_day_count(x[issue], x[mat], otherFunctions.basis_fn(basis))
                            * x[rate]
                            * 100
                        )
                    )
                    / (
                        1
                        + (
                            otherFunctions.A_day_count(x[setl], x[mat], otherFunctions.basis_fn(basis))
                            * x[yld]
                        )
                    )
                )
                - (
                    otherFunctions.A_day_count(x[issue], x[setl], otherFunctions.basis_fn(basis))
                    * (x[rate] * 100)
                ),
                axis=1,
            )
            return df
        else:
            sub_df = pd.DataFrame(columns=["Price Maturity"])
            sub_df.loc[0] = (
                (100 + (otherFunctions.A_day_count(issue, mat, otherFunctions.basis_fn(basis)) * rate * 100))
                / (1 + (otherFunctions.A_day_count(setl, mat, otherFunctions.basis_fn(basis)) * yld))
            ) - (otherFunctions.A_day_count(issue, setl, otherFunctions.basis_fn(basis)) * rate * 100)
            return sub_df

    def disc(self, setl, mat, pr, red, basis, df=""):
        otherFunctions = Other_func()
        if len(df) > 0:
            df["Discount"] = df.apply(
                lambda x: (
                    ((x[red] - x[pr]) / x[red])
                    * (1 / otherFunctions.A_day_count(x[setl], x[mat], otherFunctions.basis_fn(basis)))
                ),
                axis=1,
            )
            return df
        else:
            sub_df = pd.DataFrame(columns=["Discount"])
            sub_df.loc[0] = ((red - pr) / red) * (
                1 / otherFunctions.A_day_count(setl, mat, otherFunctions.basis_fn(basis))
            )
            return sub_df

    def price(self, settlement, maturity, rate, yld, red, freq, basis, df=""):
        otherFunctions = Other_func()
        if len(df) > 0:
            df["Price"] = ""
            for i in range(len(df)):

                setl = df[settlement][i]
                mat = df[maturity][i]
                setl_date = date(setl.year, setl.month, setl.day)

                f = otherFunctions.frequency_fn(df[freq][i])[1]
                n = otherFunctions.no_of_coupons_fn(setl, mat, df[freq][i])
                nxt_coupdate = otherFunctions.next_coup_date_fn(setl, mat, df[freq][i])
                prev_coupdate = otherFunctions.prev_coup_date_fn(setl, mat, df[freq][i])
                dsc = otherFunctions.A_day_count(setl_date, nxt_coupdate, otherFunctions.basis_fn(basis))
                e = otherFunctions.A_day_count(prev_coupdate, nxt_coupdate, otherFunctions.basis_fn(basis))
                a = otherFunctions.A_day_count(prev_coupdate, setl_date, otherFunctions.basis_fn(basis))
                dsc_e = dsc / e
                a_e = a / e

                if n > 1:
                    part_a = (df[red][i]) / ((1 + ((df[yld][i]) / (f))) ** (n - 1 + dsc_e)) - (
                        100 * a_e * ((df[rate][i]) / f)
                    )
                    part_b = 0
                    for j in range(n):
                        b = (100 * (df[rate][i]) / (f)) / ((1 + ((df[yld][i]) / f)) ** (j + dsc_e))
                        part_b = part_b + b

                    df["Price"][i] = part_a + part_b

                else:
                    dsr = a - e
                    dsr_e = dsr / e
                    t1 = 100 * ((df[rate][i]) / f) + df[red][i]
                    t2 = 1 + dsr_e * ((df[yld][i]) / (f))
                    t3 = 100 * ((df[rate][i]) / f) * a_e
                    df["Price"][i] = ((t1) / (t2)) - t3

            return df
        else:
            setl = settlement
            mat = maturity
            setl_date = date(setl.year, setl.month, setl.day)

            f = otherFunctions.frequency_fn(freq)[1]
            n = otherFunctions.no_of_coupons_fn(setl, mat, freq)
            nxt_coupdate = otherFunctions.next_coup_date_fn(setl, mat, freq)
            prev_coupdate = otherFunctions.prev_coup_date_fn(setl, mat, freq)
            dsc = otherFunctions.A_day_count(setl_date, nxt_coupdate, otherFunctions.basis_fn(basis))
            e = otherFunctions.A_day_count(prev_coupdate, nxt_coupdate, otherFunctions.basis_fn(basis))
            a = otherFunctions.A_day_count(prev_coupdate, setl_date, otherFunctions.basis_fn(basis))
            dsc_e = dsc / e
            a_e = a / e
            if n > 1:
                sub_df = pd.DataFrame(columns=["Price"])
                part_a = (red) / ((1 + ((yld) / (f))) ** (n - 1 + dsc_e)) - (100 * a_e * ((rate) / f))
                part_b = 0
                for j in range(n):
                    b = (100 * (rate) / (f)) / ((1 + ((yld) / f)) ** (j + dsc_e))
                    part_b = part_b + b

                sub_df.loc[0] = part_a + part_b
                return sub_df
            else:
                sub_df = pd.DataFrame(columns=["Price"])
                dsr = a - e
                dsr_e = dsr / e
                t1 = 100 * ((rate) / f) + red
                t2 = 1 + dsr_e * ((yld) / (f))
                t3 = 100 * ((rate) / f) * a_e
                sub_df.loc[0] = ((t1) / (t2)) - t3
                return sub_df

    def fvschedule(self, principal, schedule, dataframe=""):
        factor = 1
        for i in range(len(dataframe)):
            factor = factor * (1 + dataframe[schedule][i])
        sub_df = pd.DataFrame(columns=["FV Schedule"])
        sub_df.loc[0] = principal * factor
        return sub_df

    def oddfprice_fn(
        self,
        Settlement_date,
        Maturity_date,
        Issue_date,
        Coupon_date,
        rate,
        yld,
        red,
        frequency,
        basis,
        dataframe="",
    ):
        otherFunctions = Other_func()
        if len(dataframe) > 0:
            dataframe["settlement_ql"] = ""
            dataframe["coupon_ql"] = ""
            dataframe["couponfreq"] = ""
            dataframe["mql"] = ""
            dataframe["settlement_ql"] = ""
            dataframe["coupon_ql"] = ""
            dataframe["prev_coup_date"] = ""
            dataframe["ip"] = ""
            dataframe["ipbyp"] = ""
            dataframe["n"] = ""
            dataframe["power"] = ""
            dataframe["v"] = ""
            dataframe["vp"] = ""
            dataframe["apn"] = ""
            dataframe["Price"] = ""

            set_date_column = pd.to_datetime(dataframe[Settlement_date])
            mat_date_column = pd.to_datetime(dataframe[Maturity_date])
            iss_date_column = pd.to_datetime(dataframe[Issue_date])
            coup_date_column = pd.to_datetime(dataframe[Coupon_date])

            for i in range(len(dataframe)):
                Settlement_date = set_date_column[i]
                set_date_date = date(Settlement_date.year, Settlement_date.month, Settlement_date.day)
                Maturity_date = mat_date_column[i]
                maturity_date_date = date(Maturity_date.year, Maturity_date.month, Maturity_date.day)
                Issue_date = iss_date_column[i]
                Coupon_date = coup_date_column[i]
                coupon_date_date = date(Coupon_date.year, Coupon_date.month, Coupon_date.day)

                dataframe["couponfreq"][i] = Other_func.frequency_fn(self, dataframe[frequency][i])[1]
                dataframe["mql"][i] = otherFunctions.frequency_fn(dataframe[frequency][i])[0]

                dataframe["prev_coup_date"][i] = otherFunctions.prev_coup_date_fn(
                    set_date_date, coupon_date_date, dataframe[frequency][i]
                )

                dataframe["ip"][i] = dataframe.couponfreq[i] * (
                    (1 + dataframe[yld][i]) ** (1 / dataframe.couponfreq[i]) - 1
                )
                dataframe["ipbyp"][i] = dataframe.ip[i] / dataframe.couponfreq[i]
                dataframe["v"][i] = 1 / (1 + dataframe[yld][i])
                dataframe["vp"][i] = 1 / (1 + dataframe.ipbyp[i])

                dataframe["power"][i] = otherFunctions.A_day_count(
                    set_date_date, coupon_date_date, otherFunctions.basis_fn(basis)
                ) / otherFunctions.A_day_count(
                    dataframe.prev_coup_date[i], coupon_date_date, otherFunctions.basis_fn(basis)
                )
                dataframe["n"][i] = maturity_date_date.year - coupon_date_date.year

                dataframe["apn"][i] = (
                    1 - dataframe.vp[i] ** (dataframe.n[i] * dataframe.couponfreq[i])
                ) / dataframe.ipbyp[i]

                if dataframe["n"][i] == 0:
                    dataframe["apn"][i] = (
                        1
                        - dataframe.vp[i]
                        ** (
                            (
                                otherFunctions.A_day_count(
                                    set_date_date, maturity_date_date, otherFunctions.basis_fn(basis)
                                )
                                // otherFunctions.A_day_count(
                                    dataframe.prev_coup_date[i],
                                    coupon_date_date,
                                    otherFunctions.basis_fn(basis),
                                )
                            )
                            + 1
                        )
                    ) / dataframe.ipbyp[i]
                    dataframe["Price"][i] = dataframe[red][i] * dataframe.v[i] ** (
                        otherFunctions.A_day_count(
                            set_date_date, maturity_date_date, otherFunctions.basis_fn(basis)
                        )
                    ) + 100 * (dataframe.rate[i] / dataframe.couponfreq[i]) * dataframe.apn[i] * (
                        dataframe.vp[i] ** dataframe.power[i]
                    )

                elif dataframe["n"][i] > 0:
                    dataframe["Price"][i] = dataframe[red][i] * dataframe.v[i] ** (dataframe.n[i]) * (
                        dataframe.vp[i] ** dataframe.power[i]
                    ) + 100 * (dataframe.rate[i] / dataframe.couponfreq[i]) * dataframe.apn[i] * (
                        dataframe.vp[i] ** dataframe.power[i]
                    )
            dataframe.drop(
                columns=[
                    "settlement_ql",
                    "coupon_ql",
                    "couponfreq",
                    "mql",
                    "settlement_ql",
                    "coupon_ql",
                    "prev_coup_date",
                    "ip",
                    "ipbyp",
                    "n",
                    "power",
                    "v",
                    "vp",
                    "apn",
                ],
                inplace=True,
            )
            return dataframe

        else:
            set_date_date = date(Settlement_date.year, Settlement_date.month, Settlement_date.day)
            maturity_date_date = date(Maturity_date.year, Maturity_date.month, Maturity_date.day)
            coupon_date_date = date(Coupon_date.year, Coupon_date.month, Coupon_date.day)

            basis = otherFunctions.basis_fn(basis)
            couponfreq = otherFunctions.frequency_fn(frequency)[1]

            prev_coup_date = otherFunctions.prev_coup_date_fn(set_date_date, coupon_date_date, frequency)
            ip = couponfreq * ((1 + yld) ** (1 / couponfreq) - 1)
            ipbyp = ip / couponfreq
            v = 1 / (1 + yld)
            vp = 1 / (1 + ipbyp)

            power = otherFunctions.A_day_count(
                set_date_date, coupon_date_date, basis
            ) / otherFunctions.A_day_count(prev_coup_date, coupon_date_date, basis)
            n = maturity_date_date.year - coupon_date_date.year

            apn = (1 - vp ** (n * couponfreq)) / ipbyp
            if n == 0:
                apn = (
                    1
                    - vp
                    ** (
                        (
                            otherFunctions.A_day_count(set_date_date, maturity_date_date, basis)
                            // otherFunctions.A_day_count(prev_coup_date, coupon_date_date, basis)
                        )
                        + 1
                    )
                ) / ipbyp
                price = red * v ** (
                    otherFunctions.A_day_count(set_date_date, maturity_date_date, basis)
                ) + 100 * (rate / couponfreq) * apn * (vp**power)

            elif n > 0:
                price = red * v ** (n) * (vp**power) + 100 * (rate / couponfreq) * apn * (vp**power)

            sub_df = pd.DataFrame(columns=["Price"])
            sub_df.loc[0] = price
            return sub_df

    def oddfyield_fn(
        self,
        Settlement_date,
        Maturity_date,
        Issue_date,
        Coupon_date,
        rate,
        price,
        red,
        frequency,
        basis,
        dataframe="",
        guess=0.09,
    ):
        otherFunctions = Other_func()
        if len(dataframe) > 0:
            dataframe["Newyld"] = ""
            dataframe["couponfreq"] = ""
            dataframe["mql"] = ""
            for i in range(len(dataframe)):
                dataframe["couponfreq"][i] = otherFunctions.frequency_fn(dataframe.frequency[i])[1]
                dataframe["mql"][i] = otherFunctions.frequency_fn(dataframe.frequency[i])[0]
                dataframe["Newyld"][i] = optimize.newton(
                    lambda yld: otherFunctions.oddfprice_fn(
                        dataframe[Settlement_date][i],
                        dataframe[Maturity_date][i],
                        dataframe[Issue_date][i],
                        dataframe[Coupon_date][i],
                        dataframe[rate][i],
                        yld,
                        dataframe[red][i],
                        dataframe[frequency][i],
                        basis,
                    )
                    - dataframe[price][i],
                    guess,
                )
            dataframe.rename(columns={"Newyld": "Yield"}, inplace=True)
            dataframe.drop(columns=["couponfreq", "mql"], inplace=True)
            return dataframe

        else:

            newyld = optimize.newton(
                lambda yld: otherFunctions.oddfprice_fn(
                    Settlement_date, Maturity_date, Issue_date, Coupon_date, rate, yld, red, frequency, basis
                )
                - price,
                guess,
            )
            sub_df = pd.DataFrame(columns=["Yield"])
            sub_df.loc[0] = newyld
            return sub_df

    def nominal(self, effect_rate, npery, dataframe=""):
        if len(dataframe) > 0:
            dataframe["Nominal Rate"] = (
                ((1 + dataframe[effect_rate]) ** (1 / dataframe[npery])) - 1
            ) * dataframe[npery]
            return dataframe
        else:
            sub_df = pd.DataFrame(columns=["Nominal Rate"])
            sub_df.loc[0] = (((1 + effect_rate) ** (1 / npery)) - 1) * npery
            return sub_df

    def effect(self, nominal_rate, npery, dataframe=""):
        if len(dataframe) > 0:
            dataframe["Effective Rate"] = (
                (1 + (dataframe[nominal_rate] / dataframe[npery])) ** (dataframe[npery])
            ) - 1
            return dataframe
        else:
            sub_df = pd.DataFrame(columns=["Effective Rate"])
            sub_df.loc[0] = ((1 + (nominal_rate / npery)) ** (npery)) - 1
            return sub_df

    def intrate(self, Settlement_date, Maturity_date, Investment, Redemption, basis, dataframe=""):
        if len(dataframe) > 0:
            dataframe["Rate of Interest"] = ""
            for i in range(len(dataframe)):
                dataframe["Rate of Interest"][i] = (
                    (dataframe[Redemption][i] - dataframe[Investment][i]) / dataframe[Investment][i]
                ) * (
                    1
                    / Other_func.A_day_count(
                        self,
                        dataframe[Settlement_date][i],
                        dataframe[Maturity_date][i],
                        Other_func.basis_fn(self, basis),
                    )
                )
            return dataframe
        else:
            sub_df = pd.DataFrame(columns=["Rate of Interest"])
            sub_df.loc[0] = ((Redemption - Investment) / Investment) * (
                1
                / Other_func.A_day_count(
                    self, Settlement_date, Maturity_date, Other_func.basis_fn(self, basis)
                )
            )
            return sub_df

    def yielddisc(self, Settlement_date, Maturity_date, price, redemption, basis, dataframe=""):
        if len(dataframe) > 0:
            dataframe["Yield Discount"] = ""
            for i in range(len(dataframe)):
                dataframe["Yield Discount"][i] = (
                    (dataframe[redemption][i] - dataframe[price][i]) / dataframe[price][i]
                ) * (
                    1
                    / Other_func.A_day_count(
                        self,
                        dataframe[Settlement_date][i],
                        dataframe[Maturity_date][i],
                        Other_func.basis_fn(self, basis),
                    )
                )
            return dataframe
        else:
            sub_df = pd.DataFrame(columns=["Yield Discount"])
            sub_df.loc[0] = ((redemption - price) / price) * (
                1
                / Other_func.A_day_count(
                    self, Settlement_date, Maturity_date, Other_func.basis_fn(self, basis)
                )
            )
            return sub_df

    def yieldmat(
        self, Settlement_date, Maturity_date, Issue_date, rate, price, basis, dataframe="", guess=0.09
    ):
        if len(dataframe) > 0:
            dataframe["Yield Maturity"] = ""
            for i in range(len(dataframe)):
                dataframe["Yield Maturity"][i] = optimize.newton(
                    lambda yld: Other_func.pricemat(
                        self,
                        dataframe[Settlement_date][i],
                        dataframe[Maturity_date][i],
                        dataframe[Issue_date][i],
                        dataframe[rate][i],
                        yld,
                        basis,
                    )
                    - dataframe[price][i],
                    guess,
                )
            return dataframe
        else:
            sub_df = pd.DataFrame(columns=["Yield Maturity"])
            sub_df.loc[0] = optimize.newton(
                lambda yld: Other_func.pricemat(
                    self, Settlement_date, Maturity_date, Issue_date, rate, yld, basis
                )
                - price,
                guess,
            )
            return sub_df

    def Yield_fn(self, settlement, maturity, rate, newprice, red, freq, basis, dataframe="", guess=0.09):
        if len(dataframe) > 0:
            dataframe["Yield"] = ""
            for i in range(len(dataframe)):
                dataframe["Yield"][i] = optimize.newton(
                    lambda yld: Other_func.price(
                        self,
                        dataframe[settlement][i],
                        dataframe[maturity][i],
                        dataframe[rate][i],
                        yld,
                        dataframe[red][i],
                        dataframe[freq][i],
                        basis,
                    )
                    - dataframe[newprice][i],
                    guess,
                )
            return dataframe
        else:
            sub_df = pd.DataFrame(columns=["Yield"])
            sub_df.loc[0] = optimize.newton(
                lambda yld: Other_func.price(self, settlement, maturity, rate, yld, red, freq, basis)
                - newprice,
                guess,
            )
            return sub_df

    def sln_fn(self, cost, salvage, life, dataframe=""):
        if len(dataframe) > 0:
            dataframe["Depreciation Amount"] = (dataframe[cost] - dataframe[salvage]) / dataframe[life]
            return dataframe
        else:
            sub_df = pd.DataFrame(columns=["Depreciation Amount"])
            sub_df.loc[0] = (cost - salvage) / life
            return sub_df

    def slntable_fn(self, cost, salvage, life, security_iden="", dataframe=""):
        if len(dataframe) > 0:
            sub_df2 = pd.DataFrame(
                columns=["Security Identifier", "Year", "Cost", "Depreciation Amount", "Asset Value"]
            )
            for i in range(len(dataframe)):
                sub_df = pd.DataFrame(
                    columns=["Security Identifier", "Year", "Cost", "Depreciation Amount", "Asset Value"]
                )
                for j in range(1, int(dataframe.loc[i, life]) + 1):
                    sub_df.loc[j, "Depreciation Amount"] = (
                        dataframe.loc[i, cost] - dataframe.loc[i, salvage]
                    ) / dataframe.loc[i, life]
                    sub_df.loc[j, "Year"] = j
                    sub_df.loc[j, "Security Identifier"] = dataframe.loc[i, security_iden]
                    sub_df.iloc[0, 2] = dataframe.loc[i, cost]
                    sub_df.loc[j + 1, "Cost"] = sub_df.loc[j, "Cost"] - sub_df.loc[j, "Depreciation Amount"]
                    sub_df.loc[j, "Asset Value"] = (
                        sub_df.loc[j, "Cost"] - sub_df.loc[j, "Depreciation Amount"]
                    )
                sub_df = sub_df[:-1]
                sub_df2 = pd.concat([sub_df2, sub_df], ignore_index=True)
            return sub_df2
        else:
            sub_df = pd.DataFrame(columns=["Year", "Cost", "Depreciation Amount", "Asset Value"])
            for i in range(1, int(life) + 1):
                sub_df.loc[i, "Depreciation Amount"] = (cost - salvage) / life
                sub_df.loc[i, "Year"] = i
                sub_df.iloc[0, 1] = cost
                sub_df.loc[i + 1, "Cost"] = sub_df.loc[i, "Cost"] - sub_df.loc[i, "Depreciation Amount"]
                sub_df.loc[i, "Asset Value"] = sub_df.loc[i, "Cost"] - sub_df.loc[i, "Depreciation Amount"]
            sub_df = sub_df[:-1]
            return sub_df

    def sydtable_fn(self, cost, salvage, life):
        sub_df = pd.DataFrame(columns=["Year", "Cost", "Depreciation Amount", "Asset Value"])
        total = 0
        remaining_life = life
        for i in range(1, int(life) + 1):
            total += remaining_life
            remaining_life = remaining_life - 1

        remaining_life = life
        for i in range(1, int(life) + 1):
            depreciation = (cost - salvage) * remaining_life / total
            remaining_life = remaining_life - 1
            sub_df.loc[i, "Depreciation Amount"] = depreciation
            sub_df.loc[i, "Year"] = i
            sub_df.iloc[0, 1] = cost
            sub_df.loc[i + 1, "Cost"] = sub_df.loc[i, "Cost"] - sub_df.loc[i, "Depreciation Amount"]
            sub_df.loc[i, "Asset Value"] = sub_df.loc[i, "Cost"] - sub_df.loc[i, "Depreciation Amount"]
        sub_df = sub_df[:-1]
        return sub_df

    def wdvtable_fn(self, cost, life, rate, security_iden="", dataframe=""):
        if len(dataframe) > 0:
            sub_df2 = pd.DataFrame(
                columns=["Security Identifier", "Year", "Cost", "Depreciation Amount", "Asset Value"]
            )
            for i in range(len(dataframe)):
                sub_df = pd.DataFrame(
                    columns=["Security Identifier", "Year", "Cost", "Depreciation Amount", "Asset Value"]
                )
                for j in range(1, int(dataframe.loc[i, life]) + 1):
                    sub_df.loc[1, "Depreciation Amount"] = dataframe.loc[i, cost] * dataframe.loc[i, rate]
                    sub_df.loc[j, "Year"] = j
                    sub_df.loc[j, "Security Identifier"] = dataframe.loc[i, security_iden]
                    sub_df.iloc[0, 2] = dataframe.loc[i, cost]
                    sub_df.loc[j + 1, "Cost"] = sub_df.loc[j, "Cost"] - sub_df.loc[j, "Depreciation Amount"]
                    sub_df.loc[j, "Asset Value"] = (
                        sub_df.loc[j, "Cost"] - sub_df.loc[j, "Depreciation Amount"]
                    )
                    sub_df.loc[j + 1, "Depreciation Amount"] = (
                        dataframe.loc[i, rate] * sub_df.loc[j, "Asset Value"]
                    )
                sub_df = sub_df[:-1]
                sub_df2 = pd.concat([sub_df2, sub_df], ignore_index=True)
            return sub_df2
        else:
            sub_df = pd.DataFrame(columns=["Year", "Cost", "Depreciation Amount", "Asset Value"])
            for i in range(1, int(life) + 1):
                sub_df.loc[1, "Depreciation Amount"] = cost * rate
                sub_df.loc[i, "Year"] = i
                sub_df.iloc[0, 1] = cost
                sub_df.loc[i + 1, "Cost"] = sub_df.loc[i, "Cost"] - sub_df.loc[i, "Depreciation Amount"]
                sub_df.loc[i, "Asset Value"] = sub_df.loc[i, "Cost"] - sub_df.loc[i, "Depreciation Amount"]
                sub_df.loc[i + 1, "Depreciation Amount"] = rate * sub_df.loc[i, "Asset Value"]
            sub_df = sub_df[:-1]
            return sub_df

    def syd_fn(self, cost, salvage, life, period, dataframe=""):
        if len(dataframe) > 0:
            dataframe["Depreciation Amount"] = (
                (dataframe[cost] - dataframe[salvage]) * (dataframe[life] - dataframe[period] + 1) * 2
            ) / (dataframe[life] * ((dataframe[life]) + 1))
            return dataframe
        else:
            sub_df = pd.DataFrame(columns=["Depreciation Amount"])
            sub_df.loc[0] = ((cost - salvage) * (life - period + 1) * 2) / (life * (life + 1))
            return sub_df

    def db_fn(self, cost, salvage, life, period, month, dataframe=""):
        if len(dataframe) > 0:
            dataframe["rate"] = ""
            dataframe["depn"] = ""
            dataframe["totaldepn"] = ""
            for i in range(len(dataframe)):
                dataframe.rate[i] = round(
                    (1 - ((dataframe[salvage][i] / dataframe[cost][i]) ** (1 / dataframe[life][i]))), 3
                )
                if dataframe[period][i] == 1:
                    dataframe.depn[i] = dataframe[cost][i] * dataframe.rate[i] * dataframe[month][i] / 12
                    dataframe.totaldepn[i] = dataframe.depn[i]

                else:
                    dataframe.depn[i] = dataframe[cost][i] * dataframe.rate[i] * dataframe[month][i] / 12
                    dataframe.totaldepn[i] = dataframe.depn[i]
                    for j in range(int(dataframe[period][i]) - 1):
                        dataframe.depn[i] = round(
                            ((dataframe[cost][i] - dataframe.totaldepn[i]) * dataframe.rate[i]), 2
                        )
                        dataframe.totaldepn[i] += dataframe.depn[i]
            dataframe.rename(columns={"depn": "Depreciation"}, inplace=True)
            dataframe.drop(columns=["rate", "totaldepn"], inplace=True)
            return dataframe
        else:
            rate = round((1 - ((salvage / cost) ** (1 / life))), 3)
            if period == 1:
                depn = cost * rate * month / 12
                totaldepn = depn

            else:
                depn = cost * rate * month / 12
                totaldepn = depn
                for i in range(int(period) - 1):
                    depn = round(((cost - totaldepn) * rate), 2)
                    totaldepn += depn
            sub_df = pd.DataFrame(columns=["Depreciation Amount"])
            sub_df.loc[0] = depn
            return sub_df

    def amorlinc_fn(self, cost, Settlement_date, Maturity_date, salvage, period, rate, basis, dataframe=""):
        if len(dataframe) > 0:
            dataframe["depn"] = ""
            for i in range(len(dataframe)):
                if dataframe.rate[i] < 0 or dataframe.cost[i] < dataframe.salvage[i]:
                    dataframe.depn[i] = "#NUM!"
                    continue
                if basis == "Actual/360":
                    return "#NUM!"
                if dataframe.period[i] == 0:
                    dataframe.depn[i] = (
                        dataframe.cost[i]
                        * dataframe.rate[i]
                        * Other_func.A_day_count(
                            self,
                            dataframe[Settlement_date][i],
                            dataframe[Maturity_date][i],
                            Other_func.basis_fn(self, basis),
                        )
                    )
                    if dataframe.salvage[i] > dataframe.cost[i] - dataframe.depn[i]:
                        dataframe.depn[i] = dataframe.cost[i] - dataframe.salvage[i]
                    else:
                        pass
                elif (
                    10 - dataframe.period[i]
                    == (dataframe[Maturity_date][i] - dataframe[Settlement_date][i]).days // 365
                ):
                    dataframe.depn[i] = dataframe.cost[i] * (
                        dataframe.rate[i]
                        - (
                            dataframe.rate[i]
                            * (
                                Other_func.A_day_count(
                                    self,
                                    dataframe[Settlement_date][i],
                                    dataframe[Maturity_date][i],
                                    Other_func.basis_fn(self, basis),
                                )
                            )
                        )
                    )
                    if dataframe.salvage[i] > dataframe.cost[i] - dataframe.depn[i]:
                        dataframe.depn[i] = dataframe.cost[i] - dataframe.salvage[i]
                    else:
                        pass
                elif (
                    dataframe.period[i]
                    > 10 - (dataframe[Maturity_date][i] - dataframe[Settlement_date][i]).days // 365
                ):
                    dataframe.depn[i] = 0
                elif (
                    0
                    < dataframe.period[i]
                    < 10 - (dataframe[Maturity_date][i] - dataframe[Settlement_date][i]).days // 365
                ):
                    dataframe.depn[i] = dataframe.cost[i] * dataframe.rate[i]
                    if dataframe.salvage[i] > dataframe.cost[i] - dataframe.depn[i]:
                        dataframe.depn[i] = 0
                    else:
                        pass
            dataframe.rename(columns={"depn": "Depreciation"}, inplace=True)
            return dataframe
        else:
            basis = Other_func.A_day_count(
                self, Settlement_date, Maturity_date, Other_func.basis_fn(self, basis)
            )
            diff = (Maturity_date - Settlement_date).days
            if rate < 0 or cost <= salvage:
                return "#NUM!"
            if basis == "Actual/360":
                pass
            else:
                if period == 0:
                    depn = cost * rate * basis
                    if salvage > cost - depn:
                        sub_df = pd.DataFrame(columns=["Depreciation Amount"])
                        sub_df.loc[0] = cost - salvage
                        return sub_df
                    else:
                        sub_df = pd.DataFrame(columns=["Depreciation Amount"])
                        sub_df.loc[0] = depn
                        return sub_df
                elif 10 - period == diff // 365:
                    depn = cost * (rate - rate * (basis))
                    if salvage > cost - depn:
                        sub_df = pd.DataFrame(columns=["Depreciation Amount"])
                        sub_df.loc[0] = cost - salvage
                        return sub_df
                    else:
                        sub_df = pd.DataFrame(columns=["Depreciation Amount"])
                        sub_df.loc[0] = depn
                        return sub_df
                elif period > 10 - diff // 365:
                    return 0
                elif 0 < period < 10 - diff // 365:
                    depn = cost * rate
                    if salvage > cost - depn:
                        return 0
                    else:
                        sub_df = pd.DataFrame(columns=["Depreciation Amount"])
                        sub_df.loc[0] = depn
                        return sub_df

    def amordegrc_fn(self, cost, Settlement_date, Maturity_date, salvage, period, rate, basis, dataframe=""):
        if len(dataframe) > 0:
            dataframe["depn"] = ""
            dataframe["life"] = ""
            dataframe["coeff"] = ""
            dataframe["totaldepn"] = 0
            dataframe["dep"] = ""
            dataframe["balance"] = dataframe.cost
            for i in range(len(dataframe)):
                dataframe.life[i] = 1 / dataframe.rate[i]
                if 3 <= dataframe.life[i] <= 4:
                    dataframe.coeff[i] = 1.5
                elif 5 <= dataframe.life[i] <= 6:
                    dataframe.coeff[i] = 2
                elif dataframe.life[i] >= 6:
                    dataframe.coeff[i] = 2.5
                else:
                    dataframe.coeff[i] = 0
                if basis == "Actual/360":
                    return "#NUM!"
                else:
                    dataframe.depn[i] = (
                        dataframe.cost[i]
                        * dataframe.rate[i]
                        * dataframe.coeff[i]
                        * Other_func.A_day_count(
                            self,
                            dataframe[Settlement_date][i],
                            dataframe[Maturity_date][i],
                            Other_func.basis_fn(self, basis),
                        )
                    )
                    for j in range(dataframe.period[i]):
                        dataframe.totaldepn[i] = dataframe.depn[i]
                        dataframe.cost[i] = dataframe.cost[i] - dataframe.depn[i]
                        dataframe.depn[i] = dataframe.cost[i] * dataframe.rate[i] * dataframe.coeff[i]
                    dataframe.cost[i] = dataframe.cost[i] + dataframe.totaldepn[i] + dataframe.depn[i]
                    if dataframe.totaldepn[i] > (dataframe.cost[i] - dataframe.salvage[i]):
                        dataframe.depn[i] = 0
                    if dataframe.depn[i] < 0:
                        dataframe.depn[i] = 0
                    if dataframe.period[i] == dataframe.life[i]:
                        dataframe.depn[i] = 0
                    dataframe.depn[i] = np.floor(dataframe.depn[i])
            dataframe.rename(columns={"depn": "Depreciation"}, inplace=True)
            dataframe.drop(columns=["life", "coeff", "balance", "totaldepn", "dep"], inplace=True)
            return dataframe
        else:
            life = 1 / rate
            coeff = 0
            if 3 <= life <= 4:
                coeff = 1.5
            elif 5 <= life <= 6:
                coeff = 2
            elif life >= 6:
                coeff = 2.5
            else:
                return "#NUM!"
            if basis == "Actual/360":
                return "#NUM!"
            else:
                basis = Other_func.A_day_count(
                    self, Settlement_date, Maturity_date, Other_func.basis_fn(self, basis)
                )
                totaldepn = 0
                if period == life:
                    depn = 0
                else:
                    for i in range(int(period) + 1):
                        depn = cost * rate * coeff * basis
                        if i == life - 2:
                            rate = 0.5
                            depn = cost * rate
                            totaldepn += depn
                            cost = cost - depn
                        elif i == life - 1:
                            rate = 1
                            depn = cost * rate
                            totaldepn += depn
                            cost = cost - depn
                        else:
                            basis = 1
                            totaldepn += depn
                            cost = cost - depn
                if depn < 0:
                    return 0
                else:
                    sub_df = pd.DataFrame(columns=["Depreciation Amount"])
                    sub_df.loc[0] = np.floor(depn)
                    return sub_df

    def prev_coup_date_fn(self, set_date, mat_date, frequency, dataframe=""):
        if len(dataframe) > 0:
            dataframe["Previous Coupon Date"] = ""
            set_date_column = pd.to_datetime(dataframe[set_date])
            mat_date_column = pd.to_datetime(dataframe[mat_date])
            for i in range(len(dataframe)):
                frequency_ql = Other_func.frequency_fn(self, dataframe[frequency][i])[0]
                set_date = set_date_column[i]
                mat_date = mat_date_column[i]
                ql_set_date = ql.Date(set_date.day, set_date.month, set_date.year)
                ql_mat_date = ql.Date(mat_date.day, mat_date.month, mat_date.year)
                while ql_mat_date > ql_set_date:
                    ql_mat_date -= ql.Period(frequency_ql, ql.Months)
                prev_coup_date = ql_mat_date
                dataframe["Previous Coupon Date"][i] = prev_coup_date.to_date()
            return dataframe
        else:
            sub_df = pd.DataFrame(columns=["Previous Coupon Date"])
            frequency_ql = Other_func.frequency_fn(self, frequency)[0]
            ql_set_date = ql.Date(set_date.day, set_date.month, set_date.year)
            ql_mat_date = ql.Date(mat_date.day, mat_date.month, mat_date.year)
            while ql_mat_date > ql_set_date:
                ql_mat_date -= ql.Period(frequency_ql, ql.Months)
            prev_coup_date = ql_mat_date
            sub_df.loc[0] = prev_coup_date.to_date()
            return sub_df

    def next_coup_date_fn(self, set_date, mat_date, frequency, dataframe=""):
        if len(dataframe) > 0:
            dataframe["Next Coupon Date"] = ""
            set_date_column = pd.to_datetime(dataframe[set_date])
            mat_date_column = pd.to_datetime(dataframe[mat_date])

            for i in range(len(dataframe)):
                frequency_ql = Other_func.frequency_fn(self, dataframe[frequency][i])[0]
                set_date = set_date_column[i]
                mat_date = mat_date_column[i]
                ql_set_date = ql.Date(set_date.day, set_date.month, set_date.year)
                ql_mat_date = ql.Date(mat_date.day, mat_date.month, mat_date.year)
                while ql_mat_date > ql_set_date:
                    ql_mat_date -= ql.Period(frequency_ql, ql.Months)
                next_coup_date = ql_mat_date + ql.Period(frequency_ql, ql.Months)
                dataframe["Next Coupon Date"][i] = next_coup_date.to_date()
            return dataframe
        else:
            sub_df = pd.DataFrame(columns=["Next Coupon Date"])
            frequency_ql = Other_func.frequency_fn(self, frequency)[0]
            ql_set_date = ql.Date(set_date.day, set_date.month, set_date.year)
            ql_mat_date = ql.Date(mat_date.day, mat_date.month, mat_date.year)
            while ql_mat_date > ql_set_date:
                ql_mat_date -= ql.Period(frequency_ql, ql.Months)
            next_coup_date = ql_mat_date + ql.Period(frequency_ql, ql.Months)
            sub_df.loc[0] = next_coup_date.to_date()
            return sub_df

    def no_of_coupons_fn(self, set_date, mat_date, frequency, dataframe=""):
        if len(dataframe) > 0:
            dataframe["Number of Coupons"] = ""
            set_date_column = pd.to_datetime(dataframe[set_date])
            mat_date_column = pd.to_datetime(dataframe[mat_date])

            for i in range(len(dataframe)):
                frequency_ql = Other_func.frequency_fn(self, dataframe[frequency][i])[0]
                set_date = set_date_column[i]
                mat_date = mat_date_column[i]
                ql_set_date = ql.Date(set_date.day, set_date.month, set_date.year)
                ql_mat_date = ql.Date(mat_date.day, mat_date.month, mat_date.year)
                count = 0
                while ql_mat_date > ql_set_date:
                    ql_mat_date -= ql.Period(frequency_ql, ql.Months)
                    count += 1
                dataframe["Number of Coupons"][i] = count
            return dataframe
        else:
            sub_df = pd.DataFrame(columns=["Number of Coupons"])
            frequency_ql = Other_func.frequency_fn(self, frequency)[0]
            ql_set_date = ql.Date(set_date.day, set_date.month, set_date.year)
            ql_mat_date = ql.Date(mat_date.day, mat_date.month, mat_date.year)
            count = 0
            while ql_mat_date > ql_set_date:
                ql_mat_date -= ql.Period(frequency_ql, ql.Months)
                count += 1
            sub_df.loc[0] = count
            return sub_df

    def coupdaysbs_fn(self, set_date, mat_date, frequency, basis, dataframe=""):
        if len(dataframe) > 0:
            dataframe["Days Before Settlement"] = ""
            b = Other_func.basis_fn(self, basis)
            set_date_column = pd.to_datetime(dataframe[set_date])
            mat_date_column = pd.to_datetime(dataframe[mat_date])

            for i in range(len(dataframe)):
                set_date_count = set_date_column[i]
                set_date_date = date(set_date_count.year, set_date_count.month, set_date_count.day)

                prev_coup = Other_func.prev_coup_date_fn(
                    self, set_date_column[i], mat_date_column[i], dataframe[frequency][i]
                )
                diff_days = Other_func.A_day_count(self, prev_coup, set_date_date, b)
                day_count_dummy = pd.to_datetime(set_date_date) + pd.DateOffset(days=1)
                day_count_dummy_date = date(day_count_dummy.year, day_count_dummy.month, day_count_dummy.day)
                diff_days1 = Other_func.A_day_count(self, set_date_date, day_count_dummy_date, b)
                days = round(diff_days / diff_days1)
                dataframe["Days Before Settlement"][i] = days
            return dataframe
        else:
            sub_df = pd.DataFrame(columns=["Days Before Settlement"])
            b = Other_func.basis_fn(self, basis)
            set_date_date = date(set_date.year, set_date.month, set_date.day)

            prev_coup = Other_func.prev_coup_date_fn(self, set_date, mat_date, frequency)
            diff_days = Other_func.A_day_count(self, prev_coup, set_date_date, b)
            day_count_dummy = pd.to_datetime(set_date_date) + pd.DateOffset(days=1)
            day_count_dummy_date = date(day_count_dummy.year, day_count_dummy.month, day_count_dummy.day)
            diff_days1 = Other_func.A_day_count(self, set_date_date, day_count_dummy_date, b)
            days = round(diff_days / diff_days1)
            sub_df.loc[0] = days
            return sub_df

    def coupdaysnc_fn(self, set_date, mat_date, frequency, basis, dataframe=""):
        if len(dataframe) > 0:
            dataframe["Days until Next Coupon"] = ""
            b = Other_func.basis_fn(self, basis)
            set_date_column = pd.to_datetime(dataframe[set_date])
            mat_date_column = pd.to_datetime(dataframe[mat_date])

            for i in range(len(dataframe)):
                set_date_count = set_date_column[i]
                set_date_date = date(set_date_count.year, set_date_count.month, set_date_count.day)

                next_coup = Other_func.next_coup_date_fn(
                    self, set_date_column[i], mat_date_column[i], dataframe[frequency][i]
                )
                diff_days = Other_func.A_day_count(self, set_date_date, next_coup, b)
                day_count_dummy = pd.to_datetime(set_date_date) + pd.DateOffset(days=1)
                day_count_dummy_date = date(day_count_dummy.year, day_count_dummy.month, day_count_dummy.day)
                diff_days1 = Other_func.A_day_count(self, set_date_date, day_count_dummy_date, b)
                days = round(diff_days / diff_days1)
                dataframe["Days until Next Coupon"][i] = days
            return dataframe

        else:
            sub_df = pd.DataFrame(columns=["Days Until Next Coupon"])
            b = Other_func.basis_fn(self, basis)
            set_date_date = date(set_date.year, set_date.month, set_date.day)

            next_coup = Other_func.next_coup_date_fn(self, set_date, mat_date, frequency)
            diff_days = Other_func.A_day_count(self, set_date_date, next_coup, b)
            day_count_dummy = pd.to_datetime(set_date_date) + pd.DateOffset(days=1)
            day_count_dummy_date = date(day_count_dummy.year, day_count_dummy.month, day_count_dummy.day)
            diff_days1 = Other_func.A_day_count(self, set_date_date, day_count_dummy_date, b)
            days = round(diff_days / diff_days1)
            sub_df.loc[0] = days
            return sub_df

    def coupdays_fn(self, set_date, mat_date, frequency, basis, dataframe=""):
        if len(dataframe) > 0:
            dataframe["Days Between Coupon Payments"] = ""
            b = Other_func.basis_fn(self, basis)
            set_date_column = pd.to_datetime(dataframe[set_date])
            mat_date_column = pd.to_datetime(dataframe[mat_date])

            for i in range(len(dataframe)):
                set_date_count = set_date_column[i]

                set_date_date = date(set_date_count.year, set_date_count.month, set_date_count.day)

                prev_coup = Other_func.prev_coup_date_fn(
                    self, set_date_column[i], mat_date_column[i], dataframe[frequency][i]
                )
                next_coup = Other_func.next_coup_date_fn(
                    self, set_date_column[i], mat_date_column[i], dataframe[frequency][i]
                )
                diff_days = Other_func.A_day_count(self, prev_coup, next_coup, b)
                day_count_dummy = pd.to_datetime(set_date_date) + pd.DateOffset(days=1)
                day_count_dummy_date = date(day_count_dummy.year, day_count_dummy.month, day_count_dummy.day)
                diff_days1 = Other_func.A_day_count(self, set_date_date, day_count_dummy_date, b)
                days = round(diff_days / diff_days1)
                dataframe["Days Between Coupon Payments"][i] = days
            return dataframe

        else:
            sub_df = pd.DataFrame(columns=["Days Between Coupon Payments"])
            b = Other_func.basis_fn(self, basis)
            set_date_date = date(set_date.year, set_date.month, set_date.day)
            next_coup = Other_func.next_coup_date_fn(self, set_date, mat_date, frequency)
            prev_coup = Other_func.prev_coup_date_fn(self, set_date, mat_date, frequency)
            diff_days = Other_func.A_day_count(self, prev_coup, next_coup, b)
            day_count_dummy = pd.to_datetime(set_date_date) + pd.DateOffset(days=1)
            day_count_dummy_date = date(day_count_dummy.year, day_count_dummy.month, day_count_dummy.day)
            diff_days1 = Other_func.A_day_count(self, set_date_date, day_count_dummy_date, b)
            days = round(diff_days / diff_days1)
            sub_df.loc[0] = days
            return sub_df

    def tbilleq(self, set_date, mat_date, rate, dataframe=""):
        if len(dataframe) > 0:
            dataframe[[set_date, mat_date]] = dataframe[[set_date, mat_date]].apply(pd.to_datetime)
            dataframe["Days"] = (dataframe[mat_date] - dataframe[set_date]).dt.days
            for i in range(len(dataframe)):
                if dataframe.loc[i, "Days"] <= 365:
                    rate = (dataframe.loc[i, rate]) / 100
                    days = dataframe.loc[i, "Days"]
                    dataframe.loc[i, "Bond Equivalent Yield"] = (365 * rate) / (360 - (rate * days))
            dataframe.drop(columns=["Days"], inplace=True)
            return dataframe
        else:
            sub_df = pd.DataFrame(columns=["Bond Equivalent Yield"])
            set_date = pd.to_datetime(set_date)
            mat_date = pd.to_datetime(mat_date)
            set_date_date = date(set_date.year, set_date.month, set_date.day)
            mat_date_date = date(mat_date.year, mat_date.month, mat_date.day)
            days = (mat_date_date - set_date_date).days
            rate = rate / 100
            if days <= 365:
                tbilleq = (365 * rate) / (360 - (rate * days))
                sub_df.loc[0] = tbilleq
            return sub_df

    def tbillyield(self, set_date, mat_date, price, dataframe=""):
        if len(dataframe) > 0:
            dataframe[[set_date, mat_date]] = dataframe[[set_date, mat_date]].apply(pd.to_datetime)
            dataframe["Days"] = (dataframe[mat_date] - dataframe[set_date]).dt.days
            for i in range(len(dataframe)):
                if dataframe.loc[i, "Days"] <= 365:
                    price = dataframe.loc[i, price]
                    days = dataframe.loc[i, "Days"]
                    dataframe.loc[i, "Yield"] = ((100 - price) / (price)) * (360 / days)
            dataframe.drop(columns=["Days"], inplace=True)
            return dataframe
        else:
            sub_df = pd.DataFrame(columns=["Yield"])
            set_date = datetime.strptime(set_date, "%Y-%m-%d")
            mat_date = datetime.strptime(mat_date, "%Y-%m-%d")
            days = (mat_date - set_date).days
            if days <= 365:
                tbillyield = ((100 - price) / (price)) * (360 / days)
                sub_df.loc[0] = tbillyield
            return sub_df

    def tbillprice(self, set_date, mat_date, discount, dataframe=""):
        if len(dataframe) > 0:
            dataframe[[set_date, mat_date]] = dataframe[[set_date, mat_date]].apply(pd.to_datetime)
            dataframe["Days"] = (dataframe[mat_date] - dataframe[set_date]).dt.days
            for i in range(len(dataframe)):
                if dataframe.loc[i, "Days"] <= 365:
                    discount = dataframe.loc[i, discount] / 100
                    days = dataframe.loc[i, "Days"]
                    tbillprice = 100 * (1 - ((discount * days) / 360))
                    dataframe.loc[i, "Price"] = tbillprice
            dataframe.drop(columns=["Days"], inplace=True)
            return dataframe
        else:
            sub_df = pd.DataFrame(columns=["Price"])
            set_date = datetime.strptime(set_date, "%Y-%m-%d")
            mat_date = datetime.strptime(mat_date, "%Y-%m-%d")
            days = (mat_date - set_date).days
            if days <= 365:
                discount = discount / 100
                tbillprice = 100 * (1 - ((discount * days) / 360))
                sub_df.loc[0] = tbillprice
            return sub_df

    def durationfn(self, set_date, mat_date, rate, yield_rate, frequency, basis, dataframe=""):
        if len(dataframe) > 0:
            calc_df = Other_func.no_of_coupon_fn(self, set_date, mat_date, frequency, dataframe)
            days_df = Financial_Func.coupdaysbs_fn(self, set_date, mat_date, frequency, basis, dataframe)
            day_df = Financial_Func.coupdays_fn(self, set_date, mat_date, frequency, basis, dataframe)
            for i in range(len(dataframe)):
                n = calc_df.loc[i, "Number of Coupons"]
                t = days_df.loc[i, "Days Before Settlement"]
                T = day_df.loc[i, "Days Between Coupon Payments"]
                m = t / T
                c = dataframe.loc[i, rate]
                y = (dataframe.loc[i, yield_rate]) / 100
                if dataframe.loc[i, frequency] == "Annually":
                    u = 1
                elif dataframe.loc[i, frequency] == "Semi_Annually":
                    u = 2
                else:
                    u = 4
                cash_flow = []
                discount_factor = []
                val = 1
                while val < n:
                    cash_flow.append(c / u)
                    val += 1
                cash_flow.append((c / u) + 100)
                val = 1
                while val <= n:
                    disc = 1 / (1 + (y / u)) ** (val - m)
                    discount_factor.append(disc)
                    val += 1
                pv = []
                for j in range(len(cash_flow)):
                    pv.append(cash_flow[j] * discount_factor[j])
                present_value = sum(pv)
                weight = []
                for cf in pv:
                    b = cf / present_value
                    weight.append(b)
                weighted_avg = []
                number = list(range(1, n + 1))
                for j in range(len(number)):
                    weighted_avg.append((weight[j]) * (number[j] - m))
                final_weight = sum(weighted_avg)
                dataframe.loc[i, "Macaulay Duration"] = final_weight / u
            dataframe.drop(
                columns=["Number of Coupons", "Days Before Settlement", "Days Between Coupon Payments"],
                inplace=True,
            )
            return dataframe
        else:
            if frequency == "Annually":
                u = 1
            elif frequency == "Semi_Annually":
                u = 2
            else:
                u = 4
            sub_df = pd.DataFrame(columns=["Macaulay Duration"])
            set_date = pd.to_datetime(set_date)
            mat_date = pd.to_datetime(mat_date)
            set_date_date = date(set_date.year, set_date.month, set_date.day)
            mat_date_date = date(mat_date.year, mat_date.month, mat_date.day)
            day_df = Financial_Func.coupdays_fn(self, set_date_date, mat_date_date, frequency, basis)
            days_df = Financial_Func.coupdaysbs_fn(self, set_date_date, mat_date_date, frequency, basis)
            n = Other_func.no_of_coupon_fn(self, set_date_date, mat_date_date, frequency)
            t = days_df.loc[0, "Days Before Settlement"]
            T = day_df.loc[0, "Days Between Coupon Payments"]
            m = t / T
            y = float(yield_rate) / 100
            cash_flow = []
            discount_factor = []
            val = 1
            rate = float(rate)
            while val < n:
                cash_flow.append(rate / u)
                val += 1
            cash_flow.append((rate / u) + 100)
            val = 1
            while val <= n:
                disc = 1 / ((1 + (y / u)) ** (val - m))
                discount_factor.append(disc)
                val += 1
            pv = []
            for j in range(len(cash_flow)):
                pv.append(cash_flow[j] * discount_factor[j])
            present_value = sum(pv)
            weight = []
            for cf in pv:
                b = cf / present_value
                weight.append(b)
            weighted_avg = []
            number = list(range(1, n + 1))
            for j in range(len(number)):
                weighted_avg.append((weight[j]) * (number[j] - m))
            final_weight = sum(weighted_avg)
            sub_df.loc[0, "Macaulay Duration"] = final_weight / u
            return sub_df

    def rrifn(self, nper, pv, fv, dataframe=""):
        if len(dataframe) > 0:
            dataframe["RRI"] = ((dataframe[fv] / dataframe[pv]) ** (1 / dataframe[nper])) - 1
            return dataframe
        else:
            sub_df = pd.DataFrame(columns=["RRI"])
            rri = ((fv / pv) ** (1 / nper)) - 1
            sub_df.loc[0] = rri
            return sub_df

    def accrintm_fn(self, issue, settlement, rate, par, basis, dataframe=""):
        if len(dataframe) > 0:
            dataframe["Accrued Interest at Maturity"] = np.nan
            dataframe["Number of Days"] = np.nan
            dataframe[issue] = pd.to_datetime(dataframe[issue], errors="coerce")
            dataframe[settlement] = pd.to_datetime(dataframe[settlement], errors="coerce")
            dataframe["Days"] = (dataframe[settlement] - dataframe[issue]).dt.days
            for i in range(len(dataframe)):
                if dataframe.loc[i, "Days"] > 0:
                    dataframe["Number of Days"][i] = Other_func.A_day_count(
                        self, dataframe[issue][i], dataframe[settlement][i], Other_func.basis_fn(self, basis)
                    )
            dataframe["Accrued Interest at Maturity"] = (
                (dataframe[par].astype(float))
                * (dataframe[rate].astype(float) / 100)
                * dataframe["Number of Days"]
            )
            dataframe.drop(columns=["Days", "Number of Days"], inplace=True)
            return dataframe
        else:
            sub_df = pd.DataFrame(columns=["Accrued Interest at Maturity"])
            issue_date = date(issue.year, issue.month, issue.day)
            settlement_date = date(settlement.year, settlement.month, settlement.day)
            day_count = Other_func.A_day_count(
                self, issue_date, settlement_date, Other_func.basis_fn(self, basis)
            )
            if settlement_date > issue_date:
                accrintm = par * (rate / 100) * day_count
                sub_df.loc[0] = accrintm
            else:
                sub_df.loc[0] = ""
            return sub_df

    def accrint_fn(self, issue, first_interest, settlement, rate, par, frequency, basis, dataframe=""):
        if len(dataframe) > 0:
            dataframe["Accrued Interest"] = np.nan
            dataframe["Days"] = (dataframe[settlement] - dataframe[first_interest]).dt.days
            dataframe["Day"] = (dataframe[first_interest] - dataframe[issue]).dt.days
            calc_df = Financial_Func.coupdays_fn(
                self, first_interest, settlement, frequency, basis, dataframe
            )
            for i in range(len(dataframe)):
                if dataframe.loc[i, frequency] == "Annually":
                    f = 1
                elif dataframe.loc[i, frequency] == "Semi_Annually":
                    f = 2
                elif dataframe.loc[i, frequency] == "Quarterly":
                    f = 4
                else:
                    pass
                if dataframe.loc[i, "Days"] > 0:
                    y = calc_df.loc[i, "Days Between Coupon Payments"]
                    dataframe.loc[i, "Number of coupons"] = Other_func.no_of_coupons_fn(
                        self, dataframe[issue][i], dataframe[settlement][i], dataframe[frequency][i]
                    )
                    n = dataframe.loc[i, "Number of coupons"]
                    d = dataframe.loc[i, "Day"]
                    b = dataframe.loc[i, par]
                    a = dataframe.loc[i, rate]
                    if d > 0:
                        accrint = b * ((a / 100) / f) * ((n - 1) + (d / y))
                    elif d == 0:
                        accrint = b * ((a / 100) / f) * (n)
                    else:
                        accrint = b * ((a / 100) / f) * (n - (d / y))
                dataframe.loc[i, "Accrued Interest"] = accrint
            dataframe.drop(
                columns=["Days", "Day", "Number of coupons", "Days Between Coupon Payments"], inplace=True
            )
            return dataframe
        else:
            if frequency == "Annually":
                f = 1
            elif frequency == "Semi Annually":
                f = 2
            else:
                f = 4
            sub_df = pd.DataFrame(columns=["Accrued Interest"])
            issue_date = date(issue.year, issue.month, issue.day)
            settlement_date = date(settlement.year, settlement.month, settlement.day)
            first_interest_date = date(first_interest.year, first_interest.month, first_interest.day)
            d = (first_interest_date - issue_date).days
            a = rate
            b = par
            calc_df = Financial_Func.coupdays_fn(self, first_interest_date, settlement_date, frequency, basis)
            y = calc_df.loc[0, "Days Between Coupon Payments"]
            y = float(y)
            n = Other_func.no_of_coupons_fn(self, issue_date, settlement_date, frequency)
            if settlement_date > first_interest_date:
                if first_interest_date > issue_date:
                    accrint = b * ((a / 100) / f) * ((n - 1) + (d / y))
                elif first_interest_date == issue_date:
                    accrint = b * ((a / 100) / f) * n
                else:
                    accrint = b * ((a / 100) / f) * (n + (d / y))
                sub_df.loc[0] = accrint
            else:
                sub_df.loc[0] = ""
            return sub_df

    def DDB(self, cost, salvage, life, period, unit, depr_factor, dataframe=""):
        if len(dataframe) > 0:
            dataframe["Total depr from past"] = 0
            for i in range(len(dataframe)):
                if dataframe.loc[i, unit] == "Yearly":
                    u = 1
                elif dataframe.loc[i, unit] == "Monthly":
                    u = 12
                else:
                    u = 365
                n = dataframe.loc[i, period]
                m = n
                dataframe["Depr_Rate"] = dataframe[depr_factor] * (1 / (u * dataframe.loc[i, life]))
                while n > 0:
                    x = dataframe.loc[i, cost]
                    y = dataframe.loc[i, salvage]
                    a = dataframe.loc[i, "Total depr from past"]
                    z = dataframe.loc[i, "Depr_Rate"]
                    ddb1 = (x - a) * z
                    ddb2 = x - y - a
                    c = int(m - n + 1)
                    if ddb1 < ddb2:
                        dataframe.loc[i, f"Period {c}"] = round(ddb1, 2)
                        dataframe.loc[i, "Total depr from past"] += ddb1
                    else:
                        dataframe.loc[i, f"Period {c}"] = round(ddb2, 2)
                        dataframe.loc[i, "Total depr from past"] += ddb2
                    n = n - 1
            dataframe.drop(columns=["Total depr from past", "Depr_Rate"], inplace=True)
            return dataframe
        else:
            sub_df = pd.DataFrame()
            if unit == "Yearly":
                u = 1
            elif unit == "Monthly":
                u = 12
            else:
                u = 365
            rate_per = depr_factor * (1 / (u * life))
            n = period
            prior_depr = 0
            while period > 0:
                ddb1 = (cost - prior_depr) * rate_per
                ddb2 = cost - salvage - prior_depr
                if ddb1 < ddb2:
                    sub_df.loc[0, f"Period {n-period+1}"] = ddb1
                    prior_depr += ddb1
                else:
                    sub_df.loc[0, f"Period {n-period+1}"] = ddb2
                    prior_depr += ddb2
                period -= 1
            return sub_df

    def VDB(
        self, cost, salvage, life, unit, depr_factor, start_period, end_period, calc_method, dataframe=""
    ):
        if len(dataframe) > 0:
            if calc_method == "Variable Declining Method":
                dataframe["Total depr from past"] = 0
                dataframe["Past Rate"] = dataframe[cost]
                for i in range(len(dataframe)):
                    if dataframe.loc[i, unit] == "Yearly":
                        u = 1
                    elif dataframe.loc[i, unit] == "Monthly":
                        u = 12
                    else:
                        u = 365
                    dataframe.loc[i, "Depr_Rate_DDB"] = dataframe.loc[i, depr_factor] / (
                        u * dataframe.loc[i, life]
                    )
                    dataframe.loc[i, "Depr_Rate_SLN"] = (
                        dataframe.loc[i, cost] - dataframe.loc[i, salvage]
                    ) / (u * dataframe.loc[i, life])
                    n = dataframe.loc[i, end_period]
                    m = n
                    while n > 0:
                        x = dataframe.loc[i, cost]
                        y = dataframe.loc[i, salvage]
                        a = dataframe.loc[i, "Total depr from past"]
                        z = dataframe.loc[i, "Depr_Rate_DDB"]
                        ddb1 = (x - a) * z
                        ddb2 = x - y - a
                        c = int(m - n + 1)
                        if ddb1 < ddb2:
                            dataframe.loc[i, f"Period {c} DDB"] = round(ddb1, 2)
                            dataframe.loc[i, "Total depr from past"] += ddb1
                        else:
                            dataframe.loc[i, f"Period {c} DDB"] = round(ddb2, 2)
                            dataframe.loc[i, "Total depr from past"] += ddb2
                        n -= 1
                    n = dataframe.loc[i, end_period]
                    m = n
                    while n > 0:
                        c = int(m - n + 1)
                        sln = dataframe.loc[i, "Past Rate"] - dataframe.loc[i, "Depr_Rate_SLN"]
                        dataframe.loc[i, f"Period {c} SLN"] = round(sln, 2)
                        dataframe.loc[i, "Past Rate"] = sln
                        n -= 1
                    n = dataframe.loc[i, end_period]
                    m = n
                    while n > 0:
                        c = int(m - n + 1)
                        if dataframe.loc[i, f"Period {c} DDB"] < dataframe.loc[i, f"Period {c} SLN"]:
                            dataframe.loc[i, f"{c}"] = dataframe.loc[i, f"Period {c} DDB"]
                        else:
                            dataframe.loc[i, f"{c}"] = dataframe.loc[i, f"Period {c} SLN"]
                        n -= 1
                    n = dataframe.loc[i, end_period]
                    m = n
                    depr_value = 0
                    while n > 0:
                        c = int(m - n + 1)
                        if c > dataframe.loc[i, start_period] and c <= dataframe.loc[i, end_period]:
                            depr_value += dataframe.loc[i, f"{c}"]
                        n -= 1
                    dataframe.loc[i, "Depreciated Value"] = depr_value
                dataframe.drop(
                    columns=["Total depr from past", "Depr_Rate_DDB", "Depr_Rate_SLN", "Past Rate"],
                    inplace=True,
                )
                n = dataframe.loc[i, end_period]
                m = n
                while n > 0:
                    c = int(m - n + 1)
                    del dataframe[f"{c}"]
                    n -= 1
                for col in dataframe.columns:
                    if "DDB" in col:
                        del dataframe[col]
                    elif "SLN" in col:
                        del dataframe[col]
                    else:
                        pass
            elif calc_method == "Double Declining Method":
                dataframe["Total depr from past"] = 0
                for i in range(len(dataframe)):
                    if dataframe.loc[i, unit] == "Yearly":
                        u = 1
                    elif dataframe.loc[i, unit] == "Monthly":
                        u = 12
                    else:
                        u = 365
                    n = dataframe.loc[i, end_period]
                    m = n
                    dataframe["Depr_Rate"] = dataframe[depr_factor] * (1 / (u * dataframe.loc[i, life]))
                    while n > 0:
                        x = dataframe.loc[i, cost]
                        y = dataframe.loc[i, salvage]
                        a = dataframe.loc[i, "Total depr from past"]
                        z = dataframe.loc[i, "Depr_Rate"]
                        ddb1 = (x - a) * z
                        ddb2 = x - y - a
                        c = int(m - n + 1)
                        if ddb1 < ddb2:
                            dataframe.loc[i, f"{c}"] = round(ddb1, 2)
                            dataframe.loc[i, "Total depr from past"] += ddb1
                        else:
                            dataframe.loc[i, f"{c}"] = round(ddb2, 2)
                            dataframe.loc[i, "Total depr from past"] += ddb2
                        n -= 1
                    n = dataframe.loc[i, end_period]
                    m = n
                    depr_value = 0
                    while n > 0:
                        c = int(m - n + 1)
                        if c > dataframe.loc[i, start_period] and c <= dataframe.loc[i, end_period]:
                            depr_value += dataframe.loc[i, f"{c}"]
                        n -= 1
                    dataframe.loc[i, "Depreciated Value"] = depr_value
                dataframe.drop(columns=["Total depr from past", "Depr_Rate"], inplace=True)
                n = dataframe.loc[i, end_period]
                m = n
                while n > 0:
                    c = int(m - n + 1)
                    del dataframe[f"{c}"]
                    n -= 1
            return dataframe
        else:
            sub_df = pd.DataFrame()
            if calc_method == "Double Declining Method":
                if unit == "Yearly":
                    u = 1
                elif unit == "Monthly":
                    u = 12
                else:
                    u = 365
                rate_per = depr_factor * (1 / (u * life))
                n = end_period
                m = end_period
                prior_depr = 0
                while m > 0:
                    c = int(n - m + 1)
                    ddb1 = (cost - prior_depr) * rate_per
                    ddb2 = cost - salvage - prior_depr
                    if ddb1 < ddb2:
                        sub_df.loc[0, f"{c}"] = ddb1
                        prior_depr += ddb1
                    else:
                        sub_df.loc[0, f"{c}"] = ddb2
                        prior_depr += ddb2
                    m -= 1
                n = end_period
                m = end_period
                depr_value = 0
                while m > 0:
                    c = int(n - m + 1)
                    if c > start_period and c <= end_period:
                        depr_value += sub_df.loc[0, f"{c}"]
                    m -= 1
                sub_df.loc[0, "Depreciated Value"] = depr_value
                n = end_period
                m = end_period
                while m > 0:
                    c = int(n - m + 1)
                    del sub_df[f"{c}"]
                    m -= 1
            elif calc_method == "Variable Declining Method":
                if unit == "Yearly":
                    u = 1
                elif unit == "Monthly":
                    u = 12
                else:
                    u = 365
                rate_per = depr_factor * (1 / (u * life))
                rate_per_sln = (cost - salvage) / (u * life)
                temp_cost = cost
                n = end_period
                m = end_period
                prior_depr = 0
                while m > 0:
                    c = int(n - m + 1)
                    ddb1 = (cost - prior_depr) * rate_per
                    ddb2 = cost - salvage - prior_depr
                    if ddb1 < ddb2:
                        sub_df.loc[0, f"Period {c} DDB"] = ddb1
                        prior_depr += ddb1
                    else:
                        sub_df.loc[0, f"Period {c} DDB"] = ddb2
                        prior_depr += ddb2
                    m -= 1
                n = end_period
                m = end_period
                while m > 0:
                    c = int(n - m + 1)
                    sln = temp_cost - rate_per_sln
                    sub_df.loc[0, f"Period {c} SLN"] = sln
                    temp_cost = sln
                    m -= 1
                n = end_period
                m = end_period
                while m > 0:
                    c = int(n - m + 1)
                    if sub_df.loc[0, f"Period {c} DDB"] < sub_df.loc[0, f"Period {c} SLN"]:
                        sub_df.loc[0, f"{c}"] = sub_df.loc[0, f"Period {c} DDB"]
                    else:
                        sub_df.loc[0, f"{c}"] = sub_df.loc[0, f"Period {c} SLN"]
                    m -= 1
                n = end_period
                m = end_period
                depr_value = 0
                while m > 0:
                    c = int(n - m + 1)
                    if c > start_period and c <= end_period:
                        depr_value += sub_df.loc[0, f"{c}"]
                    m -= 1
                sub_df.loc[0, "Depreciated Value"] = depr_value
                n = end_period
                m = end_period
                while m > 0:
                    c = int(n - m + 1)
                    del sub_df[f"{c}"]
                    m -= 1
                for col in sub_df.columns:
                    if "DDB" in col:
                        del sub_df[col]
                    elif "SLN" in col:
                        del sub_df[col]
            return sub_df

    def pduration(self, rate, pv, fv, frequency, dataframe=""):
        if len(dataframe) > 0:
            for i in range(len(dataframe)):
                if dataframe.loc[i, frequency] == "Annually":
                    u = 1
                elif dataframe.loc[i, frequency] == "Semi_Annually":
                    u = 2
                elif dataframe.loc[i, frequency] == "Quarterly":
                    u = 4
                dataframe.loc[i, "PDuration"] = (
                    math.log10(dataframe.loc[i, fv]) - math.log10(dataframe.loc[i, pv])
                ) / (math.log10(1 + (dataframe.loc[i, rate] / (100 * u))))
            return dataframe
        else:
            sub_df = pd.DataFrame(columns=["PDuration"])
            if frequency == "Annually":
                u = 1
            elif frequency == "Semi_Annually":
                u = 6
            elif frequency == "Quarterly":
                u = 4
            pdur = (math.log10(fv) - math.log10(pv)) / (math.log10(1 + (rate / (100 * u))))
            sub_df.loc[0] = pdur
            return sub_df

    def oddlyield_fn(
        self, set_date, mat_date, last_interest_date, rate, price, redemption, frequency, basis, dataframe=""
    ):
        if len(dataframe) > 0:
            dataframe[set_date] = pd.to_datetime(dataframe[set_date])
            dataframe[mat_date] = pd.to_datetime(dataframe[mat_date])
            dataframe[last_interest_date] = pd.to_datetime(dataframe[last_interest_date])

            def oy(basis, set_date, mat_date, last_interest_date, r, par, red, frequency):
                if frequency == "Annually":
                    f = 1
                elif frequency == "Semi_Annually":
                    f = 2
                elif frequency == "Quarterly":
                    f = 4
                else:
                    pass
                calc_df = Financial_Func.coupdays_fn(self, set_date, mat_date, frequency, basis)
                y = calc_df.loc[0, "Days Between Coupon Payments"]
                prev_date = Other_func.prev_coup_date_fn(self, set_date, mat_date, frequency)
                prev_date = np.datetime64(prev_date)
                n = Other_func.no_of_coupons_fn(self, set_date, mat_date, frequency)
                d = (set_date - prev_date).days
                ds = (set_date - last_interest_date).days
                day = (last_interest_date - prev_date).days
                sum1 = par + ((n - 1) + (day / y)) * (r / f)
                sum2 = red + ((n - 1) + d / y) * (r / f)
                sum3 = (f) / ((n - 1) + ds / y)
                oddlyield = ((sum2 - sum1) / sum1) * sum3
                return oddlyield

            dataframe["Yield"] = dataframe.apply(
                lambda x: oy(
                    basis,
                    set_date=x[set_date],
                    mat_date=x[mat_date],
                    last_interest_date=x[last_interest_date],
                    r=x[rate],
                    par=x[price],
                    red=x[redemption],
                    frequency=x[frequency],
                ),
                axis=1,
            )
            return dataframe
        else:
            sub_df = pd.DataFrame(columns=["Yield"])
            if frequency == "Annually":
                f = 1
            elif frequency == "Semi_Annually":
                f = 2
            else:
                f = 4
            set_date_date = date(set_date.year, set_date.month, set_date.day)
            mat_date_date = date(mat_date.year, mat_date.month, mat_date.day)
            last_interest_date = date(
                last_interest_date.year, last_interest_date.month, last_interest_date.day
            )
            prev_coup_date = Other_func.prev_coup_date_fn(self, set_date_date, mat_date_date, frequency)
            n = Other_func.no_of_coupons_fn(self, set_date_date, mat_date_date, frequency)
            d1 = (set_date_date - last_interest_date).days
            d2 = (set_date_date - prev_coup_date).days
            d3 = (last_interest_date - prev_coup_date).days
            calc_df = Financial_Func.coupdays_fn(self, set_date_date, mat_date_date, frequency, basis)
            y = calc_df.loc[0, "Days Between Coupon Payments"]
            sum1 = price + ((n - 1) + (d3 / y)) * (rate / f)
            sum2 = redemption + ((n - 1) + (d2 / y)) * (rate / f)
            sum3 = f / (d1 / y)
            oddlyield = ((sum2 - sum1) / sum1) * sum3
            sub_df.loc[0, "Yield"] = oddlyield
            return sub_df

    def oddlprice_fn(
        self,
        set_date,
        mat_date,
        last_interest_date,
        rate,
        yield_rate,
        redemption,
        frequency,
        basis,
        dataframe="",
    ):
        if len(dataframe) > 0:
            dataframe[set_date] = pd.to_datetime(dataframe[set_date])
            dataframe[mat_date] = pd.to_datetime(dataframe[mat_date])
            dataframe[last_interest_date] = pd.to_datetime(dataframe[last_interest_date])

            def op(basis, set_date, mat_date, last_interest_date, r1, yield_rate, red, frequency):
                if frequency == "Annually":
                    f = 1
                elif frequency == "Semi_Annually":
                    f = 2
                elif frequency == "Quarterly":
                    f = 4
                else:
                    pass
                calc_df = Financial_Func.coupdays_fn(self, set_date, mat_date, frequency, basis)
                y = calc_df.loc[0, "Days Between Coupon Payments"]
                prev_date = Other_func.prev_coup_date_fn(self, set_date, mat_date, frequency)
                prev_date = np.datetime64(prev_date)
                n = Other_func.no_of_coupons_fn(self, set_date, mat_date, frequency)
                d = (set_date - prev_date).days
                ds = (set_date - last_interest_date).days
                day = (last_interest_date - prev_date).days
                r = (yield_rate) / 100
                x1 = red + ((n - 1) + d / y) * (r1 / f)
                x2 = ((n - 1) + (day / y)) * (r1 / f)
                x3 = (f) / ((n - 1) + ds / y)
                price = (x1 / (1 + x3 * r)) - x2
                return price

            dataframe["Price"] = dataframe.apply(
                lambda x: op(
                    basis,
                    set_date=x[set_date],
                    mat_date=x[mat_date],
                    last_interest_date=x[last_interest_date],
                    r1=x[rate],
                    yield_rate=x[yield_rate],
                    red=x[redemption],
                    frequency=x[frequency],
                ),
                axis=1,
            )
            return dataframe
        else:
            sub_df = pd.DataFrame(columns=["Price"])
            if frequency == "Annually":
                f = 1
            elif frequency == "Semi_Annually":
                f = 2
            else:
                f = 4
            set_date_date = date(set_date.year, set_date.month, set_date.day)
            mat_date_date = date(mat_date.year, mat_date.month, mat_date.day)
            last_interest_date = date(
                last_interest_date.year, last_interest_date.month, last_interest_date.day
            )
            prev_coup_date = Other_func.prev_coup_date_fn(self, set_date_date, mat_date_date, frequency)
            n = Other_func.no_of_coupons_fn(self, set_date_date, mat_date_date, frequency)
            d1 = (set_date_date - last_interest_date).days
            d2 = (set_date_date - prev_coup_date).days
            d3 = (last_interest_date - prev_coup_date).days
            calc_df = Financial_Func.coupdays_fn(self, set_date_date, mat_date_date, frequency, basis)
            y = calc_df.loc[0, "Days Between Coupon Payments"]
            r = yield_rate / 100
            x1 = redemption + ((n - 1) + (d2 / y)) * (rate / f)
            x2 = ((n - 1) + (d3 / y)) * (rate / f)
            x3 = f / (d1 / y)
            price = (x1 / (1 + x3 * r)) - x2
            sub_df.loc[0, "Price"] = price
            return sub_df

    def mdurationfn(self, set_date, mat_date, rate, yield_rate, frequency, basis, dataframe=""):
        if len(dataframe) > 0:
            duration_df = Financial_Func.durationfn(
                self, set_date, mat_date, rate, yield_rate, frequency, basis, dataframe
            )
            duration_df["F"] = duration_df[frequency].replace("Annually", "1")
            duration_df["F"] = duration_df[frequency].replace("Semi_Annually", "2")
            duration_df["F"] = duration_df[frequency].replace("Quarterly", "4")
            duration_df["F"] = duration_df["F"].astype(float)
            duration_df["Factor"] = 1 / (1 + ((duration_df[yield_rate] / 100) / duration_df["F"]))
            duration_df["Modified Duration"] = duration_df["Macaulay Duration"] * duration_df["Factor"]
            dataframe = duration_df
            dataframe.drop(
                columns=[
                    "Number of Coupons",
                    "Days Before Settlement",
                    "Days Between Coupon Payments",
                    "F",
                    "Factor",
                    "Macaulay Duration",
                ],
                inplace=True,
            )
            return dataframe
        else:
            if frequency == "Annually":
                u = 1
            elif frequency == "Semi_Annually":
                u = 2
            else:
                u = 4
            sub_df = pd.DataFrame(columns=["Modified Duration"])
            duration_df = Financial_Func.durationfn(
                self, set_date, mat_date, rate, yield_rate, frequency, basis
            )
            mac_dur = duration_df.loc[0, "Macaulay Duration"]
            y = float(yield_rate) / 100
            factor = 1 / (1 + (y / u))
            sub_df.loc[0, "Modified Duration"] = mac_dur * factor
            return sub_df


def Financial_Functions(dataframe, configDict):
    fin_func = Financial_Func()
    sub_operation = configDict["inputs"]["Sub_Op"]
    operation = configDict["inputs"]["Operation"]

    if operation == "Bond Valuations":
        fv = configDict["inputs"]["Other_Inputs"]["FV"]
        rate = configDict["inputs"]["Other_Inputs"]["Rate"]
        pv = configDict["inputs"]["Other_Inputs"]["PV"]
        pmt = configDict["inputs"]["Other_Inputs"]["PMT"]
        nper = configDict["inputs"]["Other_Inputs"]["Nper"]
        if "When" in configDict["inputs"]["Other_Inputs"]:
            when = configDict["inputs"]["Other_Inputs"]["When"]
        set_date = configDict["inputs"]["Other_Inputs"]["Settlement"]
        mat_date = configDict["inputs"]["Other_Inputs"]["Maturity"]
        frequency = configDict["inputs"]["Other_Inputs"]["Frequency"]
        basis = configDict["inputs"]["Other_Inputs"]["Basis"]
        yield_rate = configDict["inputs"]["Other_Inputs"]["Yield"]
        data_choice = configDict["inputs"]["Data_Choice"]

        if sub_operation == "FV":
            if data_choice == "Custom_input":
                output_data = fin_func.fv_fn(rate, nper, pmt, pv, when)
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.fv_fn(rate, nper, pmt, pv, when, dataframe)
                return output_data

        if sub_operation == "Rate":
            if data_choice == "Custom_input":
                output_data = fin_func.rate_fn(nper, pmt, pv, fv, when)
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.rate_fn(nper, pmt, pv, fv, when, dataframe)
                return output_data

        if sub_operation == "PV":
            if data_choice == "Custom_input":
                output_data = fin_func.pv_fn(rate, nper, pmt, fv, when)
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.pv_fn(rate, nper, pmt, fv, when, dataframe)
                return output_data

        if sub_operation == "PMT":
            if data_choice == "Custom_input":
                output_data = fin_func.pmt_fn(rate, nper, pv, fv, when)
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.pmt_fn(rate, nper, pv, fv, when, dataframe)
                return output_data

        if sub_operation == "Nper":
            if data_choice == "Custom_input":
                output_data = fin_func.nper_fn(rate, pmt, pv, fv, when)
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.nper_fn(rate, pmt, pv, fv, when, dataframe)
                return output_data

    elif operation == "Project Appraisal":
        cf_col = configDict["inputs"]["Other_Inputs"]["Cashflows"]
        cf_dates_col = configDict["inputs"]["Other_Inputs"]["Cf_Dates"]

        if sub_operation == "NPV":
            rate = float(configDict["inputs"]["Other_Inputs"]["Rate"])
            output_data = fin_func.npv_fn(dataframe, cf_col, rate)
            return output_data

        if sub_operation == "IRR":
            output_data = fin_func.irr_fn(dataframe, cf_col)
            return output_data

        if sub_operation == "XNPV":
            rate = float(configDict["inputs"]["Other_Inputs"]["Rate"])
            output_data = fin_func.xnpv_fn(dataframe, rate, cf_col, cf_dates_col)
            return output_data

        if sub_operation == "XIRR":
            output_data = fin_func.xirr_fn(dataframe, cf_col, cf_dates_col)
            return output_data

        if sub_operation == "MIRR":
            finance_rate = float(configDict["inputs"]["Other_Inputs"]["Finance_Rate"])
            reinvest_rate = float(configDict["inputs"]["Other_Inputs"]["Reinvest_Rate"])
            output_data = fin_func.mirr_fn(dataframe, cf_col, finance_rate, reinvest_rate)
            return output_data

    elif operation == "Amortization Schedule":
        rate = float(configDict["inputs"]["Other_Inputs"]["Rate"])
        period = configDict["inputs"]["Other_Inputs"]["Period"]
        nper = int(configDict["inputs"]["Other_Inputs"]["Nper"])
        if "Loan_amt" in configDict["inputs"]["Other_Inputs"]:
            loan = configDict["inputs"]["Other_Inputs"]["Loan_amt"]
            if loan:
                loan = float(loan)
            else:
                loan = 0.0
        period_freq = configDict["inputs"]["Other_Inputs"]["Period_freq"]
        if "When" in configDict["inputs"]["Other_Inputs"]:
            when = configDict["inputs"]["Other_Inputs"]["When"]
        if "FV" in configDict["inputs"]["Other_Inputs"]:
            fv = configDict["inputs"]["Other_Inputs"]["FV"]
            if fv:
                fv = float(fv)
            else:
                fv = 0.0
        if "PV" in configDict["inputs"]["Other_Inputs"]:
            pv = configDict["inputs"]["Other_Inputs"]["PV"]
            if pv:
                pv = float(pv)
            else:
                pv = 0.0

        if period_freq == "Daily":
            m = 365
        elif period_freq == "Monthly":
            m = 12
        elif period_freq == "Quarterly":
            m = 4
        elif period_freq == "Semi_Annually":
            m = 2
        elif period_freq == "Annually":
            m = 1

        if sub_operation == "PPMT":
            output_data = fin_func.ppmt_fn(rate, int(period), nper, m, loan, fv, when)
            return output_data

        if sub_operation == "IPMT":
            output_data = fin_func.ipmt_fn(rate, int(period), nper, m, loan, fv, when)
            return output_data

        if sub_operation == "ISPMT":
            output_data = fin_func.ispmt_fn(rate, int(period), nper, m, pv)
            return output_data

        if sub_operation == "CUMIPMT":
            start_period = int(configDict["inputs"]["Other_Inputs"]["Start_period"])
            end_period = int(configDict["inputs"]["Other_Inputs"]["End_period"])
            output_data = fin_func.cumipmt_fn(rate, period, nper, m, loan, fv, when, start_period, end_period)
            return output_data

        if sub_operation == "CUMPRINC":
            start_period = int(configDict["inputs"]["Other_Inputs"]["Start_period"])
            end_period = int(configDict["inputs"]["Other_Inputs"]["End_period"])
            output_data = fin_func.cumprinc_fn(
                rate, period, nper, m, loan, fv, when, start_period, end_period
            )
            return output_data

        if sub_operation == "Amortization_Table":
            output_data = fin_func.amortisation_table_fn(rate, nper, m, loan, fv, when)
            return output_data

    elif operation == "Coupon Functions":
        data_choice = configDict["inputs"]["Data_Choice"]

        if sub_operation == "Previous_Coupon_Date":
            set_date = configDict["inputs"]["Other_Inputs"]["set_date"]
            mat_date = configDict["inputs"]["Other_Inputs"]["mat_date"]
            frequency = configDict["inputs"]["Other_Inputs"]["frequency"]

            if data_choice == "Custom_input":
                output_data = fin_func.prev_coup_date_fn(
                    pd.to_datetime(set_date), pd.to_datetime(mat_date), frequency
                )
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.prev_coup_date_fn(set_date, mat_date, frequency, dataframe)
                return output_data

        if sub_operation == "Next_Coupon_Date":
            set_date = configDict["inputs"]["Other_Inputs"]["set_date"]
            mat_date = configDict["inputs"]["Other_Inputs"]["mat_date"]
            frequency = configDict["inputs"]["Other_Inputs"]["frequency"]

            if data_choice == "Custom_input":
                output_data = fin_func.next_coup_date_fn(
                    pd.to_datetime(set_date), pd.to_datetime(mat_date), frequency
                )
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.next_coup_date_fn(set_date, mat_date, frequency, dataframe)
                return output_data

        if sub_operation == "Number_of_Coupons":
            set_date = configDict["inputs"]["Other_Inputs"]["set_date"]
            mat_date = configDict["inputs"]["Other_Inputs"]["mat_date"]
            frequency = configDict["inputs"]["Other_Inputs"]["frequency"]

            if data_choice == "Custom_input":
                output_data = fin_func.no_of_coupons_fn(
                    pd.to_datetime(set_date), pd.to_datetime(mat_date), frequency
                )
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.no_of_coupons_fn(set_date, mat_date, frequency, dataframe)
                return output_data

        if sub_operation == "CoupDays_bs":
            set_date = configDict["inputs"]["Other_Inputs"]["set_date"]
            mat_date = configDict["inputs"]["Other_Inputs"]["mat_date"]
            frequency = configDict["inputs"]["Other_Inputs"]["frequency"]
            basis = configDict["inputs"]["Other_Inputs"]["basis"]

            if data_choice == "Custom_input":
                output_data = fin_func.coupdaysbs_fn(
                    pd.to_datetime(set_date), pd.to_datetime(mat_date), frequency, basis
                )
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.coupdaysbs_fn(set_date, mat_date, frequency, basis, dataframe)
                return output_data

        if sub_operation == "CoupDays_nc":
            set_date = configDict["inputs"]["Other_Inputs"]["set_date"]
            mat_date = configDict["inputs"]["Other_Inputs"]["mat_date"]
            frequency = configDict["inputs"]["Other_Inputs"]["frequency"]
            basis = configDict["inputs"]["Other_Inputs"]["basis"]

            if data_choice == "Custom_input":
                output_data = fin_func.coupdaysnc_fn(
                    pd.to_datetime(set_date), pd.to_datetime(mat_date), frequency, basis
                )
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.coupdaysnc_fn(set_date, mat_date, frequency, basis, dataframe)
                return output_data

        if sub_operation == "CoupDays":
            set_date = configDict["inputs"]["Other_Inputs"]["set_date"]
            mat_date = configDict["inputs"]["Other_Inputs"]["mat_date"]
            frequency = configDict["inputs"]["Other_Inputs"]["frequency"]
            basis = configDict["inputs"]["Other_Inputs"]["basis"]

            if data_choice == "Custom_input":
                output_data = fin_func.coupdays_fn(
                    pd.to_datetime(set_date), pd.to_datetime(mat_date), frequency, basis
                )
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.coupdays_fn(set_date, mat_date, frequency, basis, dataframe)
                return output_data

    elif operation == "Miscellaneous Functions":
        if configDict["inputs"].get("Data_Choice"):
            data_choice = configDict["inputs"]["Data_Choice"]
        else:
            data_choice = ""

        if sub_operation == "DOLLARDE":
            fractional_dollar = configDict["inputs"]["Other_Inputs"]["fractional_dollar"]
            fraction = configDict["inputs"]["Other_Inputs"]["fraction"]
            if data_choice == "Custom_input":
                output_data = fin_func.dollarde(float(fractional_dollar), float(fraction))
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.dollarde(fractional_dollar, fraction, dataframe)
                return output_data

        if sub_operation == "PDURATION":
            rate = configDict["inputs"]["Other_Inputs"]["rate"]
            pv = configDict["inputs"]["Other_Inputs"]["pv"]
            fv = configDict["inputs"]["Other_Inputs"]["fv"]
            frequency = configDict["inputs"]["Other_Inputs"]["frequency"]
            if data_choice == "Custom_input":
                output_data = fin_func.pduration(float(rate), float(pv), float(fv), frequency)
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.pduration(rate, pv, fv, frequency, dataframe)
                return output_data

        elif sub_operation == "DOLLARFR":
            decimal_dollar = configDict["inputs"]["Other_Inputs"]["decimal_dollar"]
            fraction = configDict["inputs"]["Other_Inputs"]["fraction"]
            if data_choice == "Custom_input":
                output_data = fin_func.dollarfr(float(decimal_dollar), float(fraction))
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.dollarfr(decimal_dollar, fraction, dataframe)
                return output_data

        elif sub_operation == "Received":
            settlement_date = configDict["inputs"]["Other_Inputs"]["Settlement_Date"]
            maturity_date = configDict["inputs"]["Other_Inputs"]["Maturity_Date"]
            investment = configDict["inputs"]["Other_Inputs"]["Investment"]
            discount = configDict["inputs"]["Other_Inputs"]["Discount"]
            basis = configDict["inputs"]["Other_Inputs"]["Basis"]
            if data_choice == "Custom_input":
                output_data = fin_func.received(
                    pd.to_datetime(settlement_date),
                    pd.to_datetime(maturity_date),
                    float(investment),
                    float(discount),
                    basis,
                )
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.received(
                    settlement_date, maturity_date, investment, discount, basis, dataframe
                )
                return output_data

        elif sub_operation == "Pricedisc":
            settlement_date = configDict["inputs"]["Other_Inputs"]["Settlement_Date"]
            maturity_date = configDict["inputs"]["Other_Inputs"]["Maturity_Date"]
            discount = configDict["inputs"]["Other_Inputs"]["Discount"]
            redemption = configDict["inputs"]["Other_Inputs"]["Redemption"]
            basis = configDict["inputs"]["Other_Inputs"]["Basis"]
            if data_choice == "Custom_input":
                output_data = fin_func.pricedisc(
                    pd.to_datetime(settlement_date),
                    pd.to_datetime(maturity_date),
                    float(discount),
                    float(redemption),
                    basis,
                )
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.pricedisc(
                    settlement_date, maturity_date, discount, redemption, basis, dataframe
                )
                return output_data

        elif sub_operation == "Pricemat":
            settlement_date = configDict["inputs"]["Other_Inputs"]["Settlement_Date"]
            maturity_date = configDict["inputs"]["Other_Inputs"]["Maturity_Date"]
            issue_date = configDict["inputs"]["Other_Inputs"]["Issue_Date"]
            rate = configDict["inputs"]["Other_Inputs"]["Rate"]
            yld = configDict["inputs"]["Other_Inputs"]["Yield"]
            basis = configDict["inputs"]["Other_Inputs"]["Basis"]
            if data_choice == "Custom_input":
                output_data = fin_func.pricemat(
                    pd.to_datetime(settlement_date),
                    pd.to_datetime(maturity_date),
                    pd.to_datetime(issue_date),
                    float(rate),
                    float(yld),
                    basis,
                )
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.pricemat(
                    settlement_date, maturity_date, issue_date, rate, yld, basis, dataframe
                )
                return output_data

        elif sub_operation == "Disc":
            settlement_date = configDict["inputs"]["Other_Inputs"]["Settlement_Date"]
            maturity_date = configDict["inputs"]["Other_Inputs"]["Maturity_Date"]
            price = configDict["inputs"]["Other_Inputs"]["Price"]
            redemption = configDict["inputs"]["Other_Inputs"]["Redemption"]
            basis = configDict["inputs"]["Other_Inputs"]["Basis"]
            if data_choice == "Custom_input":
                output_data = fin_func.disc(
                    pd.to_datetime(settlement_date),
                    pd.to_datetime(maturity_date),
                    float(price),
                    float(redemption),
                    basis,
                )
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.disc(
                    settlement_date, maturity_date, price, redemption, basis, dataframe
                )
                return output_data

        elif sub_operation == "Price":
            settlement_date = configDict["inputs"]["Other_Inputs"]["Settlement_Date"]
            maturity_date = configDict["inputs"]["Other_Inputs"]["Maturity_Date"]
            rate = configDict["inputs"]["Other_Inputs"]["Rate"]
            yld = configDict["inputs"]["Other_Inputs"]["Yield"]
            redemption = configDict["inputs"]["Other_Inputs"]["Redemption"]
            basis = configDict["inputs"]["Other_Inputs"]["Basis"]
            frequency = configDict["inputs"]["Other_Inputs"]["Frequency"]
            if data_choice == "Custom_input":
                output_data = fin_func.price(
                    pd.to_datetime(settlement_date),
                    pd.to_datetime(maturity_date),
                    float(rate),
                    float(yld),
                    float(redemption),
                    frequency,
                    basis,
                )
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.price(
                    settlement_date, maturity_date, rate, yld, redemption, frequency, basis, dataframe
                )
                return output_data

        elif sub_operation == "Fvschedule":
            principal = configDict["inputs"]["Other_Inputs"]["Principal"]
            schedule = configDict["inputs"]["Other_Inputs"]["Schedule"]
            output_data = fin_func.fvschedule(float(principal), schedule, dataframe)
            return output_data

        elif sub_operation == "OddFPrice":
            Settlement_date = configDict["inputs"]["Other_Inputs"]["Settlement_Date"]
            Maturity_date = configDict["inputs"]["Other_Inputs"]["Maturity_Date"]
            Issue_date = configDict["inputs"]["Other_Inputs"]["Issue_Date"]
            Coupon_date = configDict["inputs"]["Other_Inputs"]["Coupon_Date"]
            rate = configDict["inputs"]["Other_Inputs"]["Rate"]
            yld = configDict["inputs"]["Other_Inputs"]["Yield"]
            red = configDict["inputs"]["Other_Inputs"]["Redemption"]
            frequency = configDict["inputs"]["Other_Inputs"]["Frequency"]
            basis = configDict["inputs"]["Other_Inputs"]["Basis"]
            if data_choice == "Custom_input":
                output_data = fin_func.oddfprice_fn(
                    pd.to_datetime(Settlement_date),
                    pd.to_datetime(Maturity_date),
                    pd.to_datetime(Issue_date),
                    pd.to_datetime(Coupon_date),
                    float(rate),
                    float(yld),
                    float(red),
                    (frequency),
                    basis,
                )
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.oddfprice_fn(
                    Settlement_date,
                    Maturity_date,
                    Issue_date,
                    Coupon_date,
                    rate,
                    yld,
                    red,
                    frequency,
                    basis,
                    dataframe,
                )
                return output_data

        elif sub_operation == "OddFYield":
            Settlement_date = configDict["inputs"]["Other_Inputs"]["Settlement_Date"]
            Maturity_date = configDict["inputs"]["Other_Inputs"]["Maturity_Date"]
            Issue_date = configDict["inputs"]["Other_Inputs"]["Issue_Date"]
            Coupon_date = configDict["inputs"]["Other_Inputs"]["Coupon_Date"]
            rate = configDict["inputs"]["Other_Inputs"]["Rate"]
            price = configDict["inputs"]["Other_Inputs"]["Price"]
            red = configDict["inputs"]["Other_Inputs"]["Redemption"]
            frequency = configDict["inputs"]["Other_Inputs"]["Frequency"]
            basis = configDict["inputs"]["Other_Inputs"]["Basis"]
            if data_choice == "Custom_input":
                output_data = fin_func.oddfyield_fn(
                    pd.to_datetime(Settlement_date),
                    pd.to_datetime(Maturity_date),
                    pd.to_datetime(Issue_date),
                    pd.to_datetime(Coupon_date),
                    float(rate),
                    float(price),
                    float(red),
                    frequency,
                    basis,
                    guess=0.09,
                )
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.oddfyield_fn(
                    Settlement_date,
                    Maturity_date,
                    Issue_date,
                    Coupon_date,
                    rate,
                    price,
                    red,
                    frequency,
                    basis,
                    dataframe,
                    guess=0.09,
                )
                return output_data

        elif sub_operation == "OddLYield":
            set_date = configDict["inputs"]["Other_Inputs"]["Settlement_Date"]
            mat_date = configDict["inputs"]["Other_Inputs"]["Maturity_Date"]
            last_interest_date = configDict["inputs"]["Other_Inputs"]["Last_Date"]
            rate = configDict["inputs"]["Other_Inputs"]["Rate"]
            price = configDict["inputs"]["Other_Inputs"]["Price"]
            redemption = configDict["inputs"]["Other_Inputs"]["Redemption"]
            frequency = configDict["inputs"]["Other_Inputs"]["Frequency"]
            basis = configDict["inputs"]["Other_Inputs"]["Basis"]
            if data_choice == "Custom_input":
                output_data = fin_func.oddlyield_fn(
                    pd.to_datetime(set_date),
                    pd.to_datetime(mat_date),
                    pd.to_datetime(last_interest_date),
                    float(rate),
                    float(price),
                    float(redemption),
                    frequency,
                    basis,
                )
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.oddlyield_fn(
                    set_date,
                    mat_date,
                    last_interest_date,
                    rate,
                    price,
                    redemption,
                    frequency,
                    basis,
                    dataframe,
                )
                return output_data
        elif sub_operation == "OddLPrice":
            set_date = configDict["inputs"]["Other_Inputs"]["Settlement_Date"]
            mat_date = configDict["inputs"]["Other_Inputs"]["Maturity_Date"]
            last_interest_date = configDict["inputs"]["Other_Inputs"]["Last_Date"]
            rate = configDict["inputs"]["Other_Inputs"]["Rate"]
            yield_rate = configDict["inputs"]["Other_Inputs"]["Yield"]
            redemption = configDict["inputs"]["Other_Inputs"]["Redemption"]
            frequency = configDict["inputs"]["Other_Inputs"]["Frequency"]
            basis = configDict["inputs"]["Other_Inputs"]["Basis"]
            if data_choice == "Custom_input":
                output_data = fin_func.oddlprice_fn(
                    pd.to_datetime(set_date),
                    pd.to_datetime(mat_date),
                    pd.to_datetime(last_interest_date),
                    float(rate),
                    float(yield_rate),
                    float(redemption),
                    frequency,
                    basis,
                )
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.oddlprice_fn(
                    set_date,
                    mat_date,
                    last_interest_date,
                    rate,
                    yield_rate,
                    redemption,
                    frequency,
                    basis,
                    dataframe,
                )
                return output_data

    elif operation == "Interest Rates":
        data_choice = configDict["inputs"]["Data_Choice"]
        if sub_operation == "Nominal":
            rate = configDict["inputs"]["Other_Inputs"]["Rate"]
            nper = configDict["inputs"]["Other_Inputs"]["Nper"]
            if data_choice == "Custom_input":
                output_data = fin_func.nominal(float(rate), float(nper))
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.nominal(rate, nper, dataframe)
                return output_data

        if sub_operation == "Effect":
            rate = configDict["inputs"]["Other_Inputs"]["Rate"]
            nper = configDict["inputs"]["Other_Inputs"]["Nper"]
            if data_choice == "Custom_input":
                output_data = fin_func.effect(float(rate), float(nper))
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.effect(rate, nper, dataframe)
                return output_data

        if sub_operation == "Intrate":
            settlement_date = configDict["inputs"]["Other_Inputs"]["Settlement_date"]
            maturity_date = configDict["inputs"]["Other_Inputs"]["Maturity_date"]
            investment = configDict["inputs"]["Other_Inputs"]["Investment"]
            redemption = configDict["inputs"]["Other_Inputs"]["Redemption"]
            basis = configDict["inputs"]["Other_Inputs"]["Basis"]
            if data_choice == "Custom_input":
                output_data = fin_func.intrate(
                    pd.to_datetime(settlement_date),
                    pd.to_datetime(maturity_date),
                    float(investment),
                    float(redemption),
                    str(basis),
                )
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.intrate(
                    settlement_date, maturity_date, investment, redemption, basis, dataframe
                )
                return output_data

        if sub_operation == "Accrintm":
            issue = configDict["inputs"]["Other_Inputs"]["Issue"]
            settlement = configDict["inputs"]["Other_Inputs"]["Settlement"]
            rate = configDict["inputs"]["Other_Inputs"]["Rate"]
            par = configDict["inputs"]["Other_Inputs"]["Par"]
            basis = configDict["inputs"]["Other_Inputs"]["Basis"]
            if data_choice == "Custom_input":
                output_data = fin_func.accrintm_fn(
                    pd.to_datetime(issue),
                    pd.to_datetime(settlement),
                    float(rate),
                    float(par),
                    str(basis),
                )
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.accrintm_fn(issue, settlement, rate, par, basis, dataframe)
                return output_data

        if sub_operation == "Accrint":
            issue = configDict["inputs"]["Other_Inputs"]["Issue"]
            settlement = configDict["inputs"]["Other_Inputs"]["Settlement"]
            first_interest = configDict["inputs"]["Other_Inputs"]["First_Interest"]
            rate = configDict["inputs"]["Other_Inputs"]["Rate"]
            par = configDict["inputs"]["Other_Inputs"]["Par"]
            basis = configDict["inputs"]["Other_Inputs"]["Basis"]
            frequency = configDict["inputs"]["Other_Inputs"]["Frequency"]
            if data_choice == "Custom_input":
                output_data = fin_func.accrint_fn(
                    pd.to_datetime(issue),
                    pd.to_datetime(first_interest),
                    pd.to_datetime(settlement),
                    float(rate),
                    float(par),
                    str(frequency),
                    str(basis),
                )
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.accrint_fn(
                    issue, first_interest, settlement, rate, par, frequency, basis, dataframe
                )
                return output_data

        if sub_operation == "RRI":
            nper = configDict["inputs"]["Other_Inputs"]["Nper"]
            pv = configDict["inputs"]["Other_Inputs"]["PV"]
            fv = configDict["inputs"]["Other_Inputs"]["FV"]
            if data_choice == "Custom_input":
                output_data = fin_func.rrifn(float(nper), float(pv), float(fv))
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.rrifn(nper, pv, fv, dataframe)
                return output_data

    elif operation == "Yield Functions":
        settlement_date = configDict["inputs"]["Other_Inputs"]["Settlement_date"]
        maturity_date = configDict["inputs"]["Other_Inputs"]["Maturity_date"]
        newprice = configDict["inputs"]["Other_Inputs"]["Price"]
        data_choice = configDict["inputs"]["Data_Choice"]
        basis = configDict["inputs"]["Other_Inputs"]["Basis"]

        if sub_operation == "Yielddisc":
            redemption = configDict["inputs"]["Other_Inputs"]["Redemption"]
            if data_choice == "Custom_input":
                output_data = fin_func.yielddisc(
                    pd.to_datetime(settlement_date),
                    pd.to_datetime(maturity_date),
                    float(newprice),
                    float(redemption),
                    str(basis),
                )
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.yielddisc(
                    settlement_date, maturity_date, newprice, redemption, basis, dataframe
                )
                return output_data

        if sub_operation == "Yieldmat":
            issue_date = configDict["inputs"]["Other_Inputs"]["Issue_date"]
            rate = configDict["inputs"]["Other_Inputs"]["Rate"]
            if data_choice == "Custom_input":
                output_data = fin_func.yieldmat(
                    pd.to_datetime(settlement_date),
                    pd.to_datetime(maturity_date),
                    pd.to_datetime(issue_date),
                    float(rate),
                    float(newprice),
                    str(basis),
                    guess=0.09,
                )
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.yieldmat(
                    settlement_date, maturity_date, issue_date, rate, newprice, basis, dataframe, guess=0.09
                )
                return output_data

        if sub_operation == "Yield":
            redemption = configDict["inputs"]["Other_Inputs"]["Redemption"]
            rate = configDict["inputs"]["Other_Inputs"]["Rate"]
            frequency = configDict["inputs"]["Other_Inputs"]["Frequency"]
            if data_choice == "Custom_input":
                output_data = fin_func.Yield_fn(
                    pd.to_datetime(settlement_date),
                    pd.to_datetime(maturity_date),
                    float(rate),
                    float(newprice),
                    float(redemption),
                    str(frequency),
                    str(basis),
                    guess=0.09,
                )
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.Yield_fn(
                    settlement_date,
                    maturity_date,
                    rate,
                    newprice,
                    redemption,
                    frequency,
                    basis,
                    dataframe,
                    guess=0.09,
                )
                return output_data

    elif operation == "Depreciation Functions":
        if configDict["inputs"].get("Data_Choice"):
            data_choice = configDict["inputs"]["Data_Choice"]
        else:
            data_choice = ""

        if sub_operation == "SLN":
            cost = configDict["inputs"]["Other_Inputs"]["Cost"]
            salvage = configDict["inputs"]["Other_Inputs"]["Salvage"]
            life = configDict["inputs"]["Other_Inputs"]["Life"]
            if data_choice == "Custom_input":
                output_data = fin_func.sln_fn(float(cost), float(salvage), float(life))
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.sln_fn(cost, salvage, life, dataframe)
                return output_data

        elif sub_operation == "SLN_Table":
            cost = configDict["inputs"]["Other_Inputs"]["Cost"]
            salvage = configDict["inputs"]["Other_Inputs"]["Salvage"]
            life = configDict["inputs"]["Other_Inputs"]["Life"]
            if data_choice == "Custom_input":
                output_data = fin_func.slntable_fn(float(cost), float(salvage), float(life))
                return output_data
            elif data_choice == "Dataframe_input":
                security_iden = configDict["inputs"]["Other_Inputs"]["sec_iden"]
                output_data = fin_func.slntable_fn(cost, salvage, life, security_iden, dataframe)
                return output_data

        elif sub_operation == "SYD_Table":
            cost = configDict["inputs"]["Other_Inputs"]["Cost"]
            salvage = configDict["inputs"]["Other_Inputs"]["Salvage"]
            life = configDict["inputs"]["Other_Inputs"]["Life"]
            output_data = fin_func.sydtable_fn(float(cost), float(salvage), int(life))
            return output_data

        elif sub_operation == "WDV_Table":
            cost = configDict["inputs"]["Other_Inputs"]["Cost"]
            life = configDict["inputs"]["Other_Inputs"]["Life"]
            rate = configDict["inputs"]["Other_Inputs"]["Rate"]
            if data_choice == "Custom_input":
                output_data = fin_func.wdvtable_fn(float(cost), int(life), float(rate))
                return output_data
            elif data_choice == "Dataframe_input":
                security_iden = configDict["inputs"]["Other_Inputs"]["sec_iden"]
                output_data = fin_func.wdvtable_fn(cost, life, rate, security_iden, dataframe)
                return output_data

        elif sub_operation == "SYD":
            cost = configDict["inputs"]["Other_Inputs"]["Cost"]
            salvage = configDict["inputs"]["Other_Inputs"]["Salvage"]
            life = configDict["inputs"]["Other_Inputs"]["Life"]
            period = configDict["inputs"]["Other_Inputs"]["Period"]
            if data_choice == "Custom_input":
                output_data = fin_func.syd_fn(float(cost), float(salvage), float(life), float(period))
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.syd_fn(cost, salvage, life, period, dataframe)
                return output_data

        elif sub_operation == "DB":
            cost = configDict["inputs"]["Other_Inputs"]["Cost"]
            salvage = configDict["inputs"]["Other_Inputs"]["Salvage"]
            life = configDict["inputs"]["Other_Inputs"]["Life"]
            month = configDict["inputs"]["Other_Inputs"]["Month"]
            period = configDict["inputs"]["Other_Inputs"]["Period"]
            if data_choice == "Custom_input":
                output_data = fin_func.db_fn(
                    float(cost), float(salvage), float(life), int(period), float(month)
                )
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.db_fn(cost, salvage, life, period, month, dataframe)
                return output_data

        elif sub_operation == "DDB":
            cost = configDict["inputs"]["Other_Inputs"]["Cost"]
            salvage = configDict["inputs"]["Other_Inputs"]["Salvage"]
            life = configDict["inputs"]["Other_Inputs"]["Life"]
            period = configDict["inputs"]["Other_Inputs"]["Period"]
            unit = configDict["inputs"]["Other_Inputs"]["Unit"]
            depr_factor = configDict["inputs"]["Other_Inputs"]["Depreciation_Factor"]
            if data_choice == "Custom_input":
                output_data = fin_func.DDB(
                    float(cost), float(salvage), float(life), int(period), str(unit), float(depr_factor)
                )
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.DDB(cost, salvage, life, period, unit, depr_factor, dataframe)
                return output_data
        elif sub_operation == "VDB":
            cost = configDict["inputs"]["Other_Inputs"]["Cost"]
            salvage = configDict["inputs"]["Other_Inputs"]["Salvage"]
            life = configDict["inputs"]["Other_Inputs"]["Life"]
            unit = configDict["inputs"]["Other_Inputs"]["Unit"]
            depr_factor = configDict["inputs"]["Other_Inputs"]["Depreciation_Factor"]
            start_period = configDict["inputs"]["Other_Inputs"]["Start_Period"]
            end_period = configDict["inputs"]["Other_Inputs"]["End_Period"]
            calc_method = configDict["inputs"]["Other_Inputs"]["Calculation_Method"]
            if data_choice == "Custom_input":
                output_data = fin_func.VDB(
                    float(cost),
                    float(salvage),
                    float(life),
                    str(unit),
                    float(depr_factor),
                    float(start_period),
                    float(end_period),
                    str(calc_method),
                )
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.VDB(
                    cost, salvage, life, unit, depr_factor, start_period, end_period, calc_method, dataframe
                )
                return output_data

        elif sub_operation == "Amorlinc":
            cost = configDict["inputs"]["Other_Inputs"]["Cost"]
            salvage = configDict["inputs"]["Other_Inputs"]["Salvage"]
            life = configDict["inputs"]["Other_Inputs"]["Life"]
            period = configDict["inputs"]["Other_Inputs"]["Period"]
            rate = configDict["inputs"]["Other_Inputs"]["Rate"]
            Settlement_date = configDict["inputs"]["Other_Inputs"]["Settlement_Date"]
            Maturity_date = configDict["inputs"]["Other_Inputs"]["Maturity_Date"]
            basis = configDict["inputs"]["Other_Inputs"]["Basis"]
            if data_choice == "Custom_input":
                output_data = fin_func.amorlinc_fn(
                    float(cost),
                    pd.to_datetime(Settlement_date),
                    pd.to_datetime(Maturity_date),
                    float(salvage),
                    float(period),
                    float(rate),
                    basis,
                )
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.amorlinc_fn(
                    cost, Settlement_date, Maturity_date, salvage, period, rate, basis, dataframe
                )
                return output_data

        elif sub_operation == "Amordegrc":
            cost = configDict["inputs"]["Other_Inputs"]["Cost"]
            salvage = configDict["inputs"]["Other_Inputs"]["Salvage"]
            life = configDict["inputs"]["Other_Inputs"]["Life"]
            period = configDict["inputs"]["Other_Inputs"]["Period"]
            rate = configDict["inputs"]["Other_Inputs"]["Rate"]
            Settlement_date = configDict["inputs"]["Other_Inputs"]["Settlement_Date"]
            Maturity_date = configDict["inputs"]["Other_Inputs"]["Maturity_Date"]
            basis = configDict["inputs"]["Other_Inputs"]["Basis"]
            if data_choice == "Custom_input":
                output_data = fin_func.amordegrc_fn(
                    float(cost),
                    pd.to_datetime(Settlement_date),
                    pd.to_datetime(Maturity_date),
                    float(salvage),
                    int(period),
                    float(rate),
                    basis,
                )
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.amordegrc_fn(
                    cost, Settlement_date, Maturity_date, salvage, period, rate, basis, dataframe
                )
                return output_data

    elif operation == "Treasury Functions":
        if configDict["inputs"].get("Data_Choice"):
            data_choice = configDict["inputs"]["Data_Choice"]

        if sub_operation == "TBILLPRICE":
            set_date = configDict["inputs"]["Other_Inputs"]["Settlement_date"]
            mat_date = configDict["inputs"]["Other_Inputs"]["Maturity_date"]
            discount = configDict["inputs"]["Other_Inputs"]["Discount"]
            if data_choice == "Custom_input":
                output_data = fin_func.tbillprice(set_date, mat_date, float(discount))
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.tbillprice(set_date, mat_date, discount, dataframe)
                return output_data
        elif sub_operation == "TBILLYIELD":
            set_date = configDict["inputs"]["Other_Inputs"]["Settlement_date"]
            mat_date = configDict["inputs"]["Other_Inputs"]["Maturity_date"]
            price = configDict["inputs"]["Other_Inputs"]["Price"]
            if data_choice == "Custom_input":
                output_data = fin_func.tbillyield(set_date, mat_date, float(price))
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.tbillyield(set_date, mat_date, price, dataframe)
                return output_data
        elif sub_operation == "TBILLEQ":
            set_date = configDict["inputs"]["Other_Inputs"]["Settlement_date"]
            mat_date = configDict["inputs"]["Other_Inputs"]["Maturity_date"]
            rate = configDict["inputs"]["Other_Inputs"]["Rate"]
            if data_choice == "Custom_input":
                output_data = fin_func.tbilleq(set_date, mat_date, float(rate))
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.tbilleq(set_date, mat_date, rate, dataframe)
                return output_data

    elif operation == "Sensitivity Analysis":
        fv = configDict["inputs"]["Other_Inputs"]["FV"]
        rate = configDict["inputs"]["Other_Inputs"]["Rate"]
        pv = configDict["inputs"]["Other_Inputs"]["PV"]
        set_date = configDict["inputs"]["Other_Inputs"]["Settlement_date"]
        mat_date = configDict["inputs"]["Other_Inputs"]["Maturity_date"]
        frequency = configDict["inputs"]["Other_Inputs"]["Frequency"]
        basis = configDict["inputs"]["Other_Inputs"]["Basis"]
        yield_rate = configDict["inputs"]["Other_Inputs"]["Yield"]
        data_choice = configDict["inputs"]["Data_Choice"]
        if sub_operation == "Mduration":
            if data_choice == "Custom_input":
                output_data = fin_func.mdurationfn(set_date, mat_date, rate, yield_rate, frequency, basis)
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.mdurationfn(
                    set_date, mat_date, rate, yield_rate, frequency, basis, dataframe
                )
            return output_data

        elif sub_operation == "Duration":
            if data_choice == "Custom_input":
                output_data = fin_func.durationfn(set_date, mat_date, rate, yield_rate, frequency, basis)
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.durationfn(
                    set_date, mat_date, rate, yield_rate, frequency, basis, dataframe
                )
                return output_data

        elif sub_operation == "PDURATION":
            if data_choice == "Custom_input":
                output_data = fin_func.pduration(float(rate), float(pv), float(fv), frequency)
                return output_data
            elif data_choice == "Dataframe_input":
                output_data = fin_func.pduration(rate, pv, fv, frequency, dataframe)
                return output_data
