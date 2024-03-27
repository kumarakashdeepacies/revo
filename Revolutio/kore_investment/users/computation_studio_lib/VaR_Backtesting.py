from datetime import date
import multiprocessing

from joblib import Parallel, delayed
import numpy as np
import pandas as pd


def fastvarpnl(measures_df, df, i, pnlorhyp):
    port = df.Portfolio[i]
    var_date = df.Valuation_Date[i - 1]
    pnl_date = df.Valuation_Date[i]
    v_df = measures_df[
        (measures_df.portfolio == port)
        & (measures_df.valuation_date == var_date)
        & (measures_df.measure_type == "Portfolio Historical Simulation VaR - Diversified")
    ]
    var = sum(v_df.measure_value)
    pl_df = measures_df[
        (measures_df.portfolio == port)
        & (measures_df.valuation_date == pnl_date)
        & (measures_df.measure_type == "Fair Value")
    ]
    ps_df = measures_df[
        (measures_df.portfolio == port)
        & (measures_df.valuation_date == var_date)
        & (measures_df.measure_type == "Fair Value")
    ]
    a_df = measures_df[
        (measures_df.portfolio == port)
        & (measures_df.valuation_date == pnl_date)
        & (measures_df.measure_type == pnlorhyp)
    ]
    pnl = sum(pl_df.measure_value) - sum(ps_df.measure_value) + sum(a_df.measure_value)
    if pnl < var:
        breach = "Breach"
    else:
        breach = "No Breach"
    return var, pnl, breach


def actual_var_pnl(actual_df, measures_df):
    var, pnl, breach = zip(
        *Parallel(n_jobs=multiprocessing.cpu_count())(
            delayed(fastvarpnl)(measures_df, actual_df, i, "PNL") for i in range(1, len(actual_df.index))
        )
    )
    var, pnl, breach = list(var), list(pnl), list(breach)
    var.insert(0, np.nan)
    pnl.insert(0, np.nan)
    breach.insert(0, np.nan)
    actual_df["Portfolio Historical Simulation VaR - Diversified"] = var
    actual_df["PNL"] = pnl
    actual_df["Breach_indicator"] = breach
    return actual_df


def hyp_var_pnl(hyp_df, measures_df):
    var, pnl, breach = zip(
        *Parallel(n_jobs=multiprocessing.cpu_count())(
            delayed(fastvarpnl)(measures_df, hyp_df, i, "Hypothetical_Fair Value")
            for i in range(1, len(hyp_df.index))
        )
    )
    var, pnl, breach = list(var), list(pnl), list(breach)
    var.insert(0, np.nan)
    pnl.insert(0, np.nan)
    breach.insert(0, np.nan)
    hyp_df["Portfolio Historical Simulation VaR - Diversified"] = var
    hyp_df["PNL"] = pnl
    hyp_df["Breach_indicator"] = breach
    return hyp_df


def bt_conclusion(df, med_risk, high_risk):
    if med_risk <= len(np.where(df.Breach_indicator == "Breach")[0]) < high_risk:
        risk = "Medium Risk"
    elif len(np.where(df.Breach_indicator == "Breach")[0]) >= high_risk:
        risk = "High Risk"
    else:
        risk = "Low Risk"
    data = pd.DataFrame(
        [
            ["Backtesting Run Date", date.today()],
            ["Count of breaches", len(np.where(df.Breach_indicator == "Breach")[0])],
            ["Model Risk", risk],
        ]
    )
    data.columns = ["Backtesting Summary", ""]
    return data


class Backtesting:
    def backtesting(self, measures_df, med_risk, high_risk):
        bt_df = pd.DataFrame(columns=["Valuation_Date", "Portfolio"])
        for p in measures_df.portfolio.unique():
            m_df = measures_df[measures_df.portfolio == p]
            m_df = m_df.loc[:, ["valuation_date", "portfolio"]]
            m_df.columns = bt_df.columns
            bt_df = pd.concat([bt_df, m_df], ignore_index=True)
        bt_df["Backtesting Run Date"] = [date.today() for i in bt_df.index]
        bt_df.insert(0, "Backtesting Run Date", bt_df.pop("Backtesting Run Date"))
        actual_df, hyp_df = actual_var_pnl(bt_df, measures_df), hyp_var_pnl(bt_df, measures_df)
        actual_results = bt_conclusion(actual_df, med_risk, high_risk)
        hyp_results = bt_conclusion(hyp_df, med_risk, high_risk)
        output_data = {
            "Actual_D": actual_df,
            "Hyp_D": hyp_df,
            "Actual_R": actual_results,
            "Hyp_R": hyp_results,
        }
        return output_data


def backrun(data, config_dict):
    b = Backtesting()
    option_config = config_dict["inputs"]["option_config"]
    med_risk = int(option_config["Medium Risk"])
    high_risk = int(option_config["High Risk"])
    output_data = b.backtesting(data, med_risk, high_risk)
    return output_data
