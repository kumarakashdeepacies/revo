import base64
from io import BytesIO
import math

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import optimize


def calc_spot(spot_rates, i, cash_flow, period):
    known_pv = 0
    for j in range(i):
        known_pv += cash_flow / math.pow((1 + spot_rates[j] * period / 100), j + 1)

    def spot_func(s):
        return known_pv + (cash_flow + 100) / math.pow((1 + s * period / 100), i + 1) - 100

    return optimize.newton(spot_func, 0)


def annualised(orig, cf):
    if cf in ["monthly", "Monthly"]:
        ytm_new = [100 * (math.pow(1 + i / 1200, 12) - 1) for i in orig]
    elif cf in ["quarterly", "Quarterly"]:
        ytm_new = [100 * (math.pow(1 + i / 400, 4) - 1) for i in orig]
    elif cf in ["semi-annualised", "Semi-Annual"]:
        ytm_new = [100 * (math.pow(1 + i / 200, 2) - 1) for i in orig]
    elif cf in ["bi-annual", "Bi-Annual"]:
        ytm_new = [100 * (math.pow(1 + i / 50, 0.5) - 1) for i in orig]
    elif cf in ["annualised", "Annual"]:
        ytm_new = orig
    else:
        ytm_new = [100 * (math.exp(1 + i / 100) - 1) for i in orig]
    if isinstance(ytm_new, list):
        return ytm_new
    else:
        return ytm_new.to_list()


class Single_Curve:
    def spot_curve(self, df, tenor_col, ytm_col, par_lim_tenor, ext_date, output_cf, annual="annualised"):
        ytm_new = annualised(list(df[ytm_col]), annual)
        spot_rates = []
        lim = int(np.where(df[tenor_col] == par_lim_tenor)[0])
        spot_rates = [ytm_new[i] for i in range(lim + 1)]
        for i in range(lim + 1, len(df.index)):
            period = df[tenor_col][i] - df[tenor_col][i - 1]
            ytm = ytm_new[i]
            cash_flow = ytm * period  # taking 100 as face value
            spot_rates.append(calc_spot(spot_rates, i, cash_flow, period))

        ext = [ext_date for i in range(len(ytm_new))]

        if output_cf in ["continuous", "Continuous"]:
            spot_rates = [100 * math.log(i / 100 + 1) for i in spot_rates]
            cf = "continuously"
        elif output_cf in ["quarterly", "Quarterly"]:
            spot_rates = [400 * (math.pow(1 + i / 100, 1 / 4) - 1) for i in spot_rates]
            cf = "quarterly"
        elif output_cf in ["monthly", "Monthly"]:
            spot_rates = [1200 * (math.pow(1 + i / 100, 1 / 12) - 1) for i in spot_rates]
            cf = "monthly"
        elif output_cf in ["semi-annualised", "Semi-Annual"]:
            spot_rates = [200 * (math.pow(1 + i / 100, 1 / 2) - 1) for i in spot_rates]
            cf = "semi-annually"
        elif output_cf in ["bi-annual", "Bi-Annual"]:
            spot_rates = [50 * (math.pow(1 + i / 100, 1 / 0.5) - 1) for i in spot_rates]
            cf = "bi-annually"
        else:
            spot_rates = spot_rates
            cf = "annually"

        spot_rates = np.round_(spot_rates, decimals=4)
        spot_df = pd.DataFrame(
            list(zip(df[tenor_col], df[ytm_col], spot_rates, ext)),
            columns=[tenor_col, ytm_col, "Zero Rate p.a. (compounded " + cf + ")", "Extraction Date"],
        )
        spot_df["Extraction Date"] = spot_df["Extraction Date"].astype(str)
        plt.xlabel(tenor_col)
        plt.ylabel("Rate (%)")
        plt.plot(df[tenor_col], df[ytm_col], color="var(--primary-color)", label=ytm_col)
        plt.plot(df[tenor_col], spot_rates, color="black", label="Zero Rate p.a. (compounded " + cf + ")")
        plt.legend(loc=4)
        figfile = BytesIO()
        plt.savefig(figfile, format="png")
        plt.close()
        figfile.seek(0)
        figdata_png = figfile.getvalue()
        figdata_png = base64.b64encode(figdata_png)
        resultplot = figdata_png.decode("utf8")
        output_data = {"Table": spot_df.to_dict("records"), "Plot": resultplot, "curve_name": "GSEC Curve"}
        return output_data, spot_df


def singlecurve(data, config_dict):
    if "market_data" in data.keys():
        data = data["market_data"].reset_index()
    sc = Single_Curve()
    option_config = config_dict["inputs"]["option_config"]
    tenor = option_config["Tenor"]
    ytm = option_config["YTM"]
    par_lim_tenor = option_config["Par Lim Tenor"]
    annual = option_config["Annual"]
    ext_date = option_config["Extraction Date"]
    output_cf = option_config["Output CF"]
    output_data, spot_df = sc.spot_curve(data, tenor, ytm, int(par_lim_tenor), ext_date, output_cf, annual)
    return [output_data], spot_df
