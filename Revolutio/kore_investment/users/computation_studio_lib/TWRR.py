import datetime

import numpy as np
import pandas as pd


def weighted_average(
    position_data,
    cashflow_data,
    port_fund_column,
    port_date_column,
    port_value_column,
    cf_fund_column,
    cf_date_column,
    cf_amount_column,
    portfolio_fund,
    start_date,
    end_date,
    transaction_cashflows,
):
    message = "Success"
    fund_data = position_data[position_data[port_fund_column] == portfolio_fund]
    fund_data = (
        fund_data.groupby([port_fund_column, port_date_column]).agg("sum")[port_value_column].reset_index()
    )
    opening_value = fund_data[fund_data[port_date_column] == start_date][port_value_column]
    if len(opening_value):
        opening_value = opening_value[0]

    else:
        message = "Error value on start date not found for the fund selected"
        opening_value = 0
    ending_value = fund_data[fund_data[port_date_column] == end_date][port_value_column]
    if len(ending_value):
        ending_value = ending_value[ending_value.index[0]]
    else:
        message = "Error value on end date not found for the fund selected"
        ending_value = 0
    time_delta_days = (
        pd.to_datetime(end_date).date() - pd.to_datetime(start_date).date()
    )
    time_delta_days = np.timedelta64(time_delta_days, "D").astype(int) + 1
    if len(cashflow_data) > 0:
        if cashflow_data[cf_amount_column].dtype.name == "object":
            cashflow_data[cf_amount_column] = cashflow_data[cf_amount_column].str.replace(",", "")
            cashflow_data = cashflow_data.astype({cf_amount_column: "float"})
        fund_cashflow_data = cashflow_data[cashflow_data[cf_fund_column] == portfolio_fund]
        fund_cashflow_data = fund_cashflow_data[
            (fund_cashflow_data[cf_date_column] >= start_date)
            & (fund_cashflow_data[cf_date_column] <= end_date)
        ]
        fund_cashflow_data["time_deltas"] = pd.to_datetime(
            fund_cashflow_data[cf_date_column]
        ) - pd.to_datetime(start_date)
        fund_cashflow_data["time_deltas"] = [
            np.timedelta64(i, "D").astype(int) + 1 for i in fund_cashflow_data["time_deltas"]
        ]
        fund_cashflow_data["time_weights"] = (
            time_delta_days - fund_cashflow_data["time_deltas"]
        ) / time_delta_days
        net_inflows = fund_cashflow_data[cf_amount_column].sum()
        fund_cashflow_data["time_weighted_inflows"] = (
            fund_cashflow_data[cf_amount_column] * fund_cashflow_data["time_weights"]
        )
        total_tw_inflows = fund_cashflow_data["time_weighted_inflows"].sum()
    else:
        net_inflows = 0
        total_tw_inflows = 0
    if len(transaction_cashflows) > 0:
        transaction_cashflows = transaction_cashflows[transaction_cashflows["identifier"] == portfolio_fund]
        tran_columns = transaction_cashflows.columns.tolist()
        tran_columns.remove("transaction_date")
        tran_columns.remove("identifier")
        tran_columns.remove("cashflow_type")
        for tran_amt_col in tran_columns:
            if transaction_cashflows[tran_amt_col].dtype.name == "object":
                transaction_cashflows[tran_amt_col] = transaction_cashflows[tran_amt_col].str.replace(",", "")
                transaction_cashflows = transaction_cashflows.astype({tran_amt_col: "float"})
                transaction_cashflows[tran_amt_col].fillna(0, inplace=True)
        transaction_cashflows_opening = transaction_cashflows[
            transaction_cashflows["transaction_date"] == start_date
        ]
        transaction_cashflows_closing = transaction_cashflows[
            transaction_cashflows["transaction_date"] == end_date
        ]

        dividend_accrued = transaction_cashflows_closing.loc[
            transaction_cashflows_closing["cashflow_type"] == "dividend_accrued", "cashflow"
        ]
        net_broker_receivable_opening = transaction_cashflows_opening.loc[
            transaction_cashflows_opening["cashflow_type"] == "net_broker_receivable", "cashflow"
        ]
        net_broker_receivable_ending = transaction_cashflows_closing.loc[
            transaction_cashflows_closing["cashflow_type"] == "net_broker_receivable", "cashflow"
        ]
        net_broker_payable_opening = transaction_cashflows_opening.loc[
            transaction_cashflows_opening["cashflow_type"] == "net_broker_payable", "cashflow"
        ]
        net_broker_payable_ending = transaction_cashflows_closing.loc[
            transaction_cashflows_closing["cashflow_type"] == "net_broker_payable", "cashflow"
        ]
        cash_balance_opening = transaction_cashflows_opening.loc[
            transaction_cashflows_opening["cashflow_type"] == "cash_balance", "cashflow"
        ]
        cash_balance_ending = transaction_cashflows_closing.loc[
            transaction_cashflows_closing["cashflow_type"] == "cash_balance", "cashflow"
        ]
        interest_opening = transaction_cashflows_opening.loc[
            transaction_cashflows_opening["cashflow_type"] == "interest", "cashflow"
        ]
        interest_closing = transaction_cashflows_closing.loc[
            transaction_cashflows_closing["cashflow_type"] == "interest", "cashflow"
        ]

        net_inflows_before = net_inflows
        if not dividend_accrued.empty:
            net_inflows_before -= dividend_accrued.values[0]
        if not net_broker_receivable_opening.empty:
            net_inflows_before += net_broker_receivable_opening.values[0]
        if not net_broker_receivable_ending.empty:
            net_inflows_before -= net_broker_receivable_ending.values[0]
        if not net_broker_payable_opening.empty:
            net_inflows_before += net_broker_payable_opening.values[0]
        if not net_broker_payable_ending.empty:
            net_inflows_before -= net_broker_payable_ending.values[0]
        if not cash_balance_opening.empty:
            net_inflows_before += cash_balance_opening.values[0]
        if not cash_balance_ending.empty:
            net_inflows_before -= cash_balance_ending.values[0]
        if not interest_opening.empty:
            net_inflows_before += interest_opening.values[0]
        if not interest_closing.empty:
            net_inflows_before -= interest_closing.values[0]

    net_inflows = net_inflows_before
    numer = ending_value - (opening_value + net_inflows)
    denom = opening_value + total_tw_inflows
    twrr = numer / denom
    annualised_twrr = ((1 + twrr) ** (365.25 / time_delta_days)) - 1
    if isinstance(annualised_twrr, complex):
        annualised_twrr = annualised_twrr.real
    return opening_value, ending_value, net_inflows, annualised_twrr, message


def cummulative(
    position_data,
    cashflow_data,
    port_fund_column,
    port_date_column,
    port_value_column,
    cf_fund_column,
    cf_date_column,
    cf_amount_column,
    portfolio_fund,
    start_date,
    end_date,
):
    fund_data = position_data[position_data[port_fund_column] == portfolio_fund]
    fund_data = (
        fund_data.groupby([port_fund_column, port_date_column]).agg("sum")[port_value_column].reset_index()
    )

    opening_value = fund_data[fund_data[port_date_column] == start_date][port_value_column]
    if len(opening_value):
        opening_value = opening_value[0]
    else:
        opening_value = 0
    ending_value = fund_data[fund_data[port_date_column] == end_date].get(port_value_column)
    if len(ending_value):
        ending_value = ending_value[ending_value.index[0]]
    else:
        ending_value = 0
    if len(cashflow_data) > 0:
        if cashflow_data[cf_amount_column].dtype.name == "object":
            cashflow_data[cf_amount_column] = cashflow_data[cf_amount_column].str.replace(",", "")
            cashflow_data = cashflow_data.astype({cf_amount_column: "float"})
        fund_cashflow_data = cashflow_data[cashflow_data[cf_fund_column] == portfolio_fund]
        fund_cashflow_data = fund_cashflow_data[
            (fund_cashflow_data[cf_date_column] >= start_date)
            & (fund_cashflow_data[cf_date_column] <= end_date)
        ]
        fund_cashflow_data = (
            fund_cashflow_data.groupby([cf_fund_column, cf_date_column])
            .agg("sum")[cf_amount_column]
            .reset_index()
        )
        merged_data = pd.merge(
            fund_cashflow_data,
            fund_data,
            how="left",
            left_on=[cf_fund_column, cf_date_column],
            right_on=[port_fund_column, port_date_column],
        )
        merged_data["opening_value"] = np.nan
        merged_data["net_inflows"] = 0
        for i in range(1, len(fund_data)):
            if fund_data[port_date_column].iloc[i] == merged_data[cf_date_column].iloc[0]:
                merged_data["opening_value"].iloc[0] = fund_data[port_value_column].iloc[i - 1]
        for i in range(1, len(merged_data)):
            merged_data["opening_value"].iloc[i] = merged_data[port_value_column].iloc[i - 1]
        merged_data["ending_value"] = merged_data[port_value_column]
        merged_data["net_inflows"] = merged_data[cf_amount_column]
        merged_data.drop(columns=[cf_amount_column, port_date_column, port_value_column], inplace=True)
        net_inflows = merged_data["net_inflows"].sum()
        annualised_twrr = 0
        if all(
            merged_data[["opening_value", "ending_value"]][
                merged_data["transaction_date"] != start_date
            ].notna()
        ):
            merged_data["HP"] = (
                merged_data["ending_value"] - (merged_data["opening_value"] + merged_data["net_inflows"])
            ) / (merged_data["opening_value"] + merged_data["net_inflows"])
            merged_data["HP"] += 1
            twrr = merged_data["HP"].product() - 1
            time_delta_days = (
                pd.to_datetime(end_date).date()
                - pd.to_datetime(start_date).date()
            )
            time_delta_days = np.timedelta64(time_delta_days, "D").astype(int)
            time_delta_days = int(time_delta_days)
            twrr = float(twrr)
            annualised_twrr = ((1 + twrr) ** (365.25 / time_delta_days)) - 1
            if isinstance(annualised_twrr, complex):
                annualised_twrr = annualised_twrr.real
            message = "Success"
        else:
            message = (
                "Position data missing for all the transaction dates. Cummulative method cannot be performed."
            )
    else:
        net_inflows = 0
        annualised_twrr = 0
        message = "Transaction data missing for the fund. Cummulative method cannot be performed."

    return opening_value, ending_value, net_inflows, annualised_twrr, message


def twrr(position_data, cashflow_data, config_dict, transaction_data):
    method = config_dict["inputs"]["twrr_method"]
    position_fund_column = config_dict["inputs"]["position_fund_column"]
    position_date_column = config_dict["inputs"]["position_date_column"]
    position_amount_column = config_dict["inputs"]["position_amount_column"]
    cf_fund_column = config_dict["inputs"]["cf_fund_column"]
    cf_date_column = config_dict["inputs"]["cf_date_column"]
    cf_amount_column = config_dict["inputs"]["cf_amount_column"]
    fund = config_dict["inputs"]["fund"]
    start_date = config_dict["inputs"]["start_date"]
    end_date = config_dict["inputs"]["end_date"]
    run_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output = {
        "Run_date": pd.to_datetime(run_date),
        "TWRR_method": method,
        "Fund_code": fund,
        "Start_date": pd.to_datetime(start_date),
        "End_date": pd.to_datetime(end_date),
    }
    if method == "weighted_average":
        opening_value, ending_value, net_inflows, twrr, message = weighted_average(
            position_data,
            cashflow_data,
            position_fund_column,
            position_date_column,
            position_amount_column,
            cf_fund_column,
            cf_date_column,
            cf_amount_column,
            fund,
            start_date,
            end_date,
            transaction_data,
        )
        output["Opening_value"] = opening_value
        output["Ending_value"] = ending_value
        output["Net_inflows"] = net_inflows
        output["TWRR"] = twrr
        output = pd.DataFrame([output])
        return output, message
    elif method == "cummulative":
        opening_value, ending_value, net_inflows, twrr, message = cummulative(
            position_data,
            cashflow_data,
            position_fund_column,
            position_date_column,
            position_amount_column,
            cf_fund_column,
            cf_date_column,
            cf_amount_column,
            fund,
            start_date,
            end_date,
        )

        output["Opening_value"] = opening_value
        output["Ending_value"] = ending_value
        output["Net_inflows"] = net_inflows
        output["TWRR"] = twrr
        output = pd.DataFrame([output])
        return output, message
