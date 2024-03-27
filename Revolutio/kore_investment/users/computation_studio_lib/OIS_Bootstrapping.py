import base64
from datetime import date, datetime
from io import BytesIO
import json
import math
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import optimize

from kore_investment.users.computations import standardised_functions
from kore_investment.users.computations.db_centralised_function import data_handling, read_data_func


def fbil_spot(d, t):
    def spot_func(s):
        return math.pow(1 / d, 1 / t) - 1 - s

    return 100 * optimize.newton(spot_func, 0)


def hull_spot(spot_rates, i, cash_flow, tenor, period):
    known_pv = cash_flow / math.pow((1 + spot_rates[i - 1] / 100), tenor[i - 1])
    mrt = tenor[i - 1]
    for j in range(i - 2, -1, -1):
        if (mrt - tenor[j]) == period:
            mrt = tenor[j]
            known_pv += cash_flow / math.pow((1 + spot_rates[j] / 100), tenor[j])

    def spot_func(s):
        return known_pv + (cash_flow + 100) / math.pow((1 + s / 100), tenor[i]) - 100

    return optimize.newton(spot_func, 0)


def annualised(orig, cf):
    if cf in ["monthly", "Monthly"]:
        ytm_new = [100 * (math.pow(1 + i / 1200, 12) - 1) for i in orig]
    elif cf in ["Quarterly", "quarterly"]:
        ytm_new = [100 * (math.pow(1 + i / 400, 4) - 1) for i in orig]
    elif cf in ["semi-annualised", "Semi-Annual"]:
        ytm_new = [100 * (math.pow(1 + i / 200, 2) - 1) for i in orig]
    elif cf in ["bi-annual", "Bi-Annual"]:
        ytm_new = [100 * (math.pow(1 + i / 50, 0.5) - 1) for i in orig]
    elif cf in ["annualised", "Annual"]:
        ytm_new = orig
    else:
        ytm_new = [100 * (math.exp(i / 100) - 1) for i in orig]
    return ytm_new


def linearinterp(x, y, independent_var_value):
    n = len(x)
    for j in range(1, n):
        if (x[j - 1]) <= independent_var_value <= (x[j]):
            return y[j] + ((y[j] - y[j - 1]) * (independent_var_value - x[j]) / (x[j] - x[j - 1]))


class OIS_Bootstrapping:
    def spot_curve(
        self,
        df,
        tenor_col,
        ytm_col,
        ext_date,
        st_tenor,
        method,
        fs=0,
        output_cf="annualised",
        cf_pre_st="annualised",
        cf_post_st="semi-annualised",
        curve_name="OIS Curve",
        curve_data="No",  ## For saving curve configuration
        curve_quote_data="No",  ## For saving curve quotes
        request_user=None,
        currency="INR",
        interpolation_algorithm="Linear",
        extrapolation_algorithm="Linear",
        configuration_date=date.today(),
    ):
        # changing string tenors to year fraction
        tenors = []
        for i in df[tenor_col]:
            if isinstance(i, str):
                i = re.sub(r"\s+", "", i.lower(), flags=re.UNICODE)
                if i == "o/n":
                    tenors.append(1 / 365)
                elif "d" in i:
                    tenors.append(float(i.split("d")[0]) / 365)
                elif "m" in i:
                    tenors.append(float(i.split("m")[0]) / 12)
                elif "y" in i:
                    tenors.append(float(i.split("y")[0]))
            else:
                tenors.append(i)

        df[ytm_col] = df[ytm_col].astype(float)
        # ois flat --> ois flat + funding spread
        ytms = list(df[ytm_col] + fs / 100)

        # linear interpolation
        lim = tenors.index(st_tenor)
        i = st_tenor
        idx = None
        while i != tenors[-1]:
            if i not in tenors:
                ytms.insert(idx + 1, linearinterp(np.array(tenors), np.array(ytms), i))
                tenors.insert(idx + 1, i)
            idx = tenors.index(i)
            i += 0.5

        # annualising all rates according to CF input
        pre_ytm_new = annualised(list(ytms[: lim + 1]), cf_pre_st)
        post_ytm_new = annualised(list(ytms[lim + 1 :]), cf_post_st)
        ytm_new = pre_ytm_new
        for y in post_ytm_new:
            ytm_new.append(y)
        # FBIL method
        if method == "fbil":
            dt = [tenors[0]]
            dft = [1 / math.pow(1 + ytm_new[0] / 100, dt[0])]
            qt_1 = [0]
            zero_rates = [fbil_spot(dft[0], tenors[0])]
            for i in range(1, len(ytms)):
                dt.append(tenors[i] - tenors[i - 1])
                prod = [dt[j] * dft[j] for j in range(i)]
                qt_1.append(np.sum(prod))
                dft.append((1 - qt_1[i] * ytm_new[i] / 100) / (1 + dt[i] * ytm_new[i] / 100))
                zero_rates.append(fbil_spot(dft[i], tenors[i]))

        # Hull method
        else:
            zero_rates = list(ytm_new[: lim + 1])
            for i in range(lim + 1, len(ytms)):
                period = tenors[i] - tenors[i - 1]  # 1.5-1=0.5
                cash_flow = 100 * (math.pow(1 + ytm_new[i] / 100, period) - 1)
                zero_rates.append(hull_spot(zero_rates, i, cash_flow, tenors, period))

        ext = [ext_date for i in range(len(ytms))]
        if output_cf in ["continuous", "Continuous"]:
            zero_rates = [100 * math.log(i / 100 + 1) for i in zero_rates]
            cf = "continuously"
        elif output_cf in ["quarterly", "Quarterly"]:
            zero_rates = [400 * (math.pow(1 + i / 100, 1 / 4) - 1) for i in zero_rates]
            cf = "quarterly"
        elif output_cf in ["monthly", "Monthly"]:
            zero_rates = [1200 * (math.pow(1 + i / 100, 1 / 12) - 1) for i in zero_rates]
            cf = "monthly"
        elif output_cf in ["semi-annualised", "Semi-Annual"]:
            zero_rates = [200 * (math.pow(1 + i / 100, 1 / 2) - 1) for i in zero_rates]
            cf = "semi-annually"
        elif output_cf in ["bi-annual", "Bi-Annual"]:
            zero_rates = [50 * (math.pow(1 + i / 100, 1 / 0.5) - 1) for i in zero_rates]
            cf = "bi-annually"
        else:
            zero_rates = zero_rates
            cf = "annually"

        # changing nuumerical tenors to string eqs
        if isinstance(i, str):
            str_tenors = list(df[tenor_col][: lim + 1])
            for t in tenors[lim + 1 :]:
                str_tenors.append(df[tenor_col][lim].replace(df[tenor_col][lim].split("y")[0], str(t)))
        else:
            str_tenors = tenors

        # outputs
        zero_rates = np.round_(zero_rates, decimals=4)
        ytms = np.round_(ytms, decimals=4)
        spot_df = pd.DataFrame(
            list(zip(str_tenors, ytms, zero_rates, ext)),
            columns=[
                tenor_col,
                ytm_col + " + Funding Spread",
                "Zero Rate p.a. (compounded " + cf + ")",
                "Extraction Date",
            ],
        )
        spot_df["Curve Name"] = curve_name
        spot_df["Extraction Date"] = spot_df["Extraction Date"].astype(str)
        spot_df_columns = ["Curve Name"] + spot_df.drop("Curve Name", 1).columns.tolist()
        spot_df = spot_df.loc[:, spot_df_columns]
        zero_curve_quotes = spot_df[
            ["Extraction Date", "Curve Name", "Zero Rate p.a. (compounded " + cf + ")"]
        ].rename(
            columns={
                "Extraction Date": "extract_date",
                "Curve Name": "security_identifier",
                "Zero Rate p.a. (compounded " + cf + ")": "quoted_price",
            }
        )
        zero_curve_quotes["extract_date"] = pd.to_datetime(zero_curve_quotes["extract_date"])
        zero_curve_quotes["tenor"] = tenors
        zero_curve_quotes["quoted_price"] = zero_curve_quotes["quoted_price"] / 100
        zero_curve_quotes["yield"] = zero_curve_quotes["quoted_price"] / 100
        zero_curve_quotes["security_identifier"] = (
            zero_curve_quotes["security_identifier"].replace(" ", "_", regex=True)
            + "_"
            + zero_curve_quotes["tenor"].round(4).astype(str)
            + "Y_Zero"
        )
        if curve_data == "Yes":
            zero_curve_components = (zero_curve_quotes[["security_identifier", "tenor"]]).rename(
                columns={"security_identifier": "curve_component", "tenor": "tenor_value"}
            )
            zero_curve_components["tenor_unit"] = "Y"
            zero_curve_components["tenor"] = (
                zero_curve_components["tenor_value"].round(4).astype(str)
                + zero_curve_components["tenor_unit"]
            )
            zero_curve_components["compounding"] = "Annual"
            curve_components_existing_data = (
                read_data_func(
                    request_user,
                    {
                        "inputs": {
                            "Data_source": "Database",
                            "Table": "ir_curve_components",
                            "Columns": [
                                "curve_component",
                            ],
                        },
                        "condition": [],
                    },
                )
            ).curve_component.tolist()
            final_curve_components_data = zero_curve_components.loc[
                ~zero_curve_components["curve_component"].isin(curve_components_existing_data)
            ]
            if len(final_curve_components_data) > 0:
                final_curve_components_data["created_by"] = request_user.user.username
                final_curve_components_data["modified_by"] = request_user.user.username
                final_curve_components_data["created_date"] = datetime.now()
                final_curve_components_data["modified_date"] = datetime.now()
                data_handling(request_user, final_curve_components_data, "ir_curve_components")
            curve_repo_data = read_data_func(
                request_user,
                {
                    "inputs": {
                        "Data_source": "Database",
                        "Table": "ir_curve_repository",
                        "Columns": ["id", "configuration_date", "curve_components"],
                    },
                    "condition": [
                        {
                            "column_name": "configuration_date",
                            "condition": "Equal to",
                            "input_value": configuration_date,
                            "and_or": "and",
                        },
                        {
                            "column_name": "curve_name",
                            "condition": "Equal to",
                            "input_value": curve_name + " Zero",
                            "and_or": "",
                        },
                    ],
                },
            )
            curve_repo_existing_data = curve_repo_data.loc[
                curve_repo_data["configuration_date"] == configuration_date
            ]

            if len(curve_repo_existing_data) == 0:
                final_curve_components_json = (
                    read_data_func(
                        request_user,
                        {
                            "inputs": {
                                "Data_source": "Database",
                                "Table": "ir_curve_components",
                                "Columns": ["id"],
                            },
                            "condition": [
                                {
                                    "column_name": "curve_component",
                                    "condition": "IN",
                                    "input_value": zero_curve_components["curve_component"].tolist(),
                                    "and_or": "",
                                },
                            ],
                        },
                    )
                ).id.tolist()
                final_curve_components_json = json.dumps({i: "" for i in final_curve_components_json})
                curve_repo_existing_data = curve_repo_data.loc[
                    curve_repo_data["curve_components"] == final_curve_components_json
                ]
                if len(curve_repo_existing_data) == 0:
                    final_curve_data = pd.DataFrame(
                        [
                            {
                                "configuration_date": configuration_date,
                                "curve_id": "IR" + standardised_functions.random_no_generator(),
                                "curve_name": curve_name + " Zero",
                                "curve_components": final_curve_components_json,
                                "quote_type": "zero",
                                "currency": currency,
                                "compounding_frequency_output": cf,
                                "interpolation_algorithm": interpolation_algorithm,
                                "extrapolation_algorithm": extrapolation_algorithm,
                            }
                        ]
                    )
                    final_curve_data["created_by"] = request_user.user.username
                    final_curve_data["modified_by"] = request_user.user.username
                    final_curve_data["created_date"] = datetime.now()
                    final_curve_data["modified_date"] = datetime.now()

                    data_handling(request_user, final_curve_data, "ir_curve_repository")
        zero_curve_quotes.drop(columns=["tenor"], inplace=True)
        zero_curve_quotes["modified_duration"] = None
        zero_curve_quotes["volatility"] = None
        zero_curve_quotes["z_spread"] = None

        if curve_quote_data == "Yes":
            zero_curve_quotes["created_by"] = request_user.user.username
            zero_curve_quotes["modified_by"] = request_user.user.username
            zero_curve_quotes["created_date"] = datetime.now()
            zero_curve_quotes["modified_date"] = datetime.now()
            data_handling(request_user, zero_curve_quotes, "quoted_security_data")
        plt.xlabel("Time to Maturity")
        plt.ylabel("Spot Rate")
        plt.plot(tenors, ytms, color="var(--primary-color)", label=ytm_col + " + Funding Spread")
        plt.plot(tenors, zero_rates, color="black", label="Zero Rate p.a. (compounded " + cf + ")")
        plt.legend(loc=4)
        figfile = BytesIO()
        plt.savefig(figfile, format="png")
        plt.close()
        figfile.seek(0)
        figdata_png = figfile.getvalue()
        figdata_png = base64.b64encode(figdata_png)
        resultplot = figdata_png.decode("utf8")
        output_data = {"Table": spot_df.to_dict("records"), "Plot": resultplot, "curve_name": curve_name}
        return output_data, zero_curve_quotes


def ois(data, config_dict):
    if "market_data" in data.keys():
        data = data["market_data"].reset_index()
    oisb = OIS_Bootstrapping()
    option_config = config_dict["inputs"]["option_config"]
    tenor = option_config["Tenor"]
    ytm = option_config["YTM"]
    ext_date = option_config["Extraction Date"]
    st_tenor = option_config["Par Lim Tenor"]
    cf_pre_st = option_config["CF Till st_tenor"]
    cf_post_st = option_config["CF After st_tenor"]
    output_cf = option_config["Output CF"]
    fs = option_config["Funding Spread"]
    method = option_config["Method"]
    output_data, zero_curve_quotes = oisb.spot_curve(
        data, tenor, ytm, ext_date, float(st_tenor), method, float(fs), output_cf, cf_pre_st, cf_post_st
    )
    return [output_data], zero_curve_quotes
