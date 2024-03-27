import pandas as pd

from . import Bus_day_conv, Date_utilities, Daycount_conv, Interpolation


def Fixed_Coupon_Bond(row, Val_Date, holidays_list, Disc_curve):

    Val_Date = Val_Date

    # Create an index of the principal payment dates

    prin_date = [
        Bus_day_conv.business_day(
            row["Maturity_date"].date(),
            row["Payment_business_day_conv"],
            holidays_list,
            business_days="1111100",
        )
    ]

    # Create an index of the coupon payment dates

    rng = Date_utilities.gen_date_range3(
        row["Next_coupon_date"],
        row["Issue_date"],
        row["Maturity_date"],
        row["Coupon_frequency"],
        row["Coupon_frequency_unit"],
    )
    rng = [x.date() for x in rng]
    rng2 = [
        Bus_day_conv.business_day(x, row["Coupon_business_day_conv"], holidays_list, business_days="1111100")
        for x in rng
    ]

    rng_strt = rng
    rng_strt.pop(-1)
    rng_strt.insert(0, row["Previous_coupon_date"].date())

    # Day count Convention for principal payments
    maturity_discount_count = Daycount_conv.Day_count(
        Val_Date, prin_date, row["Payment_daycount"], row["Maturity_date"]
    )
    maturity_count = Daycount_conv.Coup_count(
        prin_date, prin_date, row["Payment_daycount"], row["Maturity_date"]
    )

    # Day count Convention for coupon payments
    discount_count = Daycount_conv.Day_count(Val_Date, rng2, row["Coupon_daycount"], row["Maturity_date"])
    count = Daycount_conv.Coup_count(rng_strt, rng2, row["Coupon_daycount"], row["Maturity_date"])

    # Number of days

    Days = Date_utilities.number_of_days(rng2)

    # Create principal cashflow table

    table = pd.DataFrame(
        index=prin_date,
        columns=[
            "Position_ID",
            "Cashflow_date",
            "Cashflow_period_start",
            "Cashflow_period_end",
            "Days",
            "Coupon_period",
            "TTM",
            "Cashflow_amount",
            "Cashflow_type",
        ],
        dtype="float",
    )
    table.index.name = "CF_No"
    table["Position_ID"] = row["Position_ID"]
    table["Cashflow_date"] = prin_date
    table["Cashflow_period_start"] = prin_date
    table["Cashflow_period_end"] = prin_date
    table["Days"] = 0
    table["Coupon_period"] = maturity_count
    table["TTM"] = maturity_discount_count
    table["Cashflow_amount"] = row["Face_value"] * row["No_of_units_traded"]
    table["Cashflow_type"] = "Principal"

    # Create coupon cashflow table

    table1 = pd.DataFrame(
        index=rng2,
        columns=[
            "Position_ID",
            "Cashflow_date",
            "Cashflow_period_start",
            "Cashflow_period_end",
            "Days",
            "Cashflow_amount",
            "Cashflow_type",
        ],
        dtype="float",
    )
    table1.index.name = "CF_No"
    table1["Position_ID"] = row["Position_ID"]
    table1["Cashflow_date"] = rng2
    table1["Cashflow_period_start"] = rng_strt
    table1["Cashflow_period_end"] = rng2
    table1["Days"] = Days
    table1["Coupon_period"] = count
    table1["TTM"] = discount_count
    table1["Cashflow_amount"] = round(
        (row["Face_Value"] * row["No_of_units_traded"] * row["Coupon_rate"] * table1.Coupon_period), 4
    )
    table1["Cashflow_type"] = "Coupon"
    # Append cashflow table
    table = pd.concat([table, table1], ignore_index=True)

    IRC = Disc_curve[Disc_curve["Curve_ID"] == row["Discount_Curve_ID"]]
    IRC_TTM = Daycount_conv.Day_count(
        Val_Date, list(IRC["Maturity_date"]), row["Discount_Daycount_Convention"], row["Maturity_date"]
    )
    table["Discount_factor"] = [
        Interpolation.Curve_interpolation(list(IRC_TTM), list(IRC["Discounting_Factor"]), x, "Linear")
        for x in list(table["TTM"])
    ]
    table["Discounted_value"] = table["Discount_factor"] * table["Cashflow_amount"]
    Price = table.Discounted_value.sum() / row["No_of_units_traded"]

    # Return output
    table.reset_index(inplace=True)
    table.index += 1
    row["CF"] = table
    row["Price"] = Price

    return row
