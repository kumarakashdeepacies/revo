import base64
from io import BytesIO
import math
import re

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def linearinterp(x, y, independent_var_value):
    n = len(x)
    for j in range(1, n):
        if (x[j - 1]) <= independent_var_value <= (x[j]):
            return y[j] + ((y[j] - y[j - 1]) * (independent_var_value - x[j]) / (x[j] - x[j - 1]))


def num_tenor(df, tenor_col):
    tenors = []
    for i in df[tenor_col]:
        i = re.sub(r"\s+", "", i.lower(), flags=re.UNICODE)
        if i == "o/n":
            tenors.append(1 / 360)
        elif "d" in i:
            tenors.append(float(i.split("d")[0]) / 360)
        elif "m" in i:
            tenors.append(float(i.split("m")[0]) / 12)
        elif "y" in i:
            tenors.append(float(i.split("y")[0]))
    return tenors


def annualised(orig, cf):
    orig = list(orig)
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
        ytm_new = [100 * (math.exp(i / 100) - 1) for i in orig]
    return ytm_new


class Swap_Curve_Bootstrapping:
    def swap_curve(
        self,
        orig_df,
        all_tenors,
        all_rates,
        s_cf,
        st_tenor,
        m_instr,
        m_cf,
        mt_tenor,
        l_cf,
        m,
        output_cf,
        ext_date,
        sigma=None,
        a=None,
    ):
        s_df = orig_df["d1"][[all_tenors["s_tenor"], all_rates["s_rate"]]]
        s_df["t"] = num_tenor(s_df, all_tenors["s_tenor"])
        s_df = s_df[s_df["t"] <= st_tenor]
        m_df = orig_df["d2"][[all_tenors["m_tenor"], all_rates["m_rate"]]]
        m_df["t"] = num_tenor(m_df, all_tenors["m_tenor"])
        m_df = m_df[(m_df["t"] <= mt_tenor) & (m_df["t"] > st_tenor)]
        l_df = orig_df["d3"][[all_tenors["l_tenor"], all_rates["l_rate"]]]
        l_df["t"] = num_tenor(l_df, all_tenors["l_tenor"])
        l_df = l_df[l_df["t"] > mt_tenor]
        str_tenors = (
            [s_df[all_tenors["s_tenor"]][i] for i in s_df.index]
            + [m_df[all_tenors["m_tenor"]][i] for i in m_df.index]
            + [l_df[all_tenors["l_tenor"]][i] for i in l_df.index]
        )
        tenor = (
            [s_df["t"][i] for i in s_df.index]
            + [m_df["t"][i] for i in m_df.index]
            + [l_df["t"][i] for i in l_df.index]
        )
        rate = (
            [s_df[all_rates["s_rate"]][i] for i in s_df.index]
            + [m_df[all_rates["m_rate"]][i] for i in m_df.index]
            + [l_df[all_rates["l_rate"]][i] for i in l_df.index]
        )

        df = pd.DataFrame(list(zip(str_tenors, tenor, rate)), columns=["Tenor Point", "Tenor", "Rate"])
        tenors = list(df["Tenor"])
        rates = list(df["Rate"])
        i = mt_tenor
        idx = np.where(np.array(tenors) < mt_tenor)[0][-1]
        while i != tenors[-1]:
            if i not in tenors:
                rates.insert(idx + 1, linearinterp(np.array(tenors), np.array(rates), i))
                tenors.insert(idx + 1, i)
            idx = tenors.index(i)
            i += 1
        sti = np.where(np.array(tenors) <= st_tenor)[0][-1]
        mti = np.where(np.array(tenors) <= mt_tenor)[0][-1]

        zero_rates = [100 * math.log(1 + rates[i] / 100) for i in range(len(rates[: sti + 1]))]

        q_m_rate = [
            400 * (math.pow(1 + i / 100, 1 / 4) - 1) for i in annualised(rates[sti + 1 : mti + 1], m_cf)
        ]
        cc_m_rate = [
            100 * math.log(1 + rates[sti + 1 + i] / 100) for i in range(len(rates[sti + 1 : mti + 1]))
        ]
        a_l_rate = annualised(rates[mti + 1 :], l_cf)

        t1 = tenors[sti]
        for i in range(len(q_m_rate)):
            t2 = tenors[sti + 1 + i]
            if m_instr == "future":
                com = (1 - math.exp(-a * (t2 - t1))) / (a * (t2 - t1))
                con_adj = (
                    math.pow(sigma, 2)
                    / (4 * a)
                    * com
                    * (com * (1 - math.exp(-2 * a * t1)) + 2 * (1 - math.exp(-a * t1)) / t1)
                )
                q_adj_rate = q_m_rate[i] / 100 - con_adj
                cc = 100 * math.log(q_adj_rate + 1)
            else:
                cc = cc_m_rate[i]
            zero_rates.append((cc * (t2 - t1) + zero_rates[-1] * t1) / t2)
            t1 = t2

        zero_df = pd.DataFrame(
            list(zip(tenors[: mti + 1], rates[: mti + 1], zero_rates)), columns=["t", "Rate", "Zero Rate"]
        )

        for i in range(len(a_l_rate)):
            temp = zero_df[(zero_df["t"] >= m) & (zero_df["t"] <= (tenors[mti + 1 + i] - m))]
            s = np.sum([math.exp(-temp["t"][k] * temp["Zero Rate"][k] / 100) for k in temp.index])
            z = -100 / tenors[mti + 1 + i] * math.log((100 - s * a_l_rate[i] / m) / (100 + a_l_rate[i] / m))

            """period = df['Tenor'][mti+1+i]-df['Tenor'][mti+i]
            cash_flow = 100*(math.pow(1+a_l_rate[i]/100, period) - 1)
            z = hull_spot(annualised(zero_df['Zero Rate'], 'continuous'), mti+1+i, cash_flow, df['Tenor'], period)
            z = 100*(math.log(1+z/100)-1)"""

            df2 = {"t": tenors[mti + 1 + i], "Rate": rates[mti + 1 + i], "Zero Rate": z}
            zero_df = zero_df.append(df2, ignore_index=True)

        if output_cf in ["continuous", "Continuous"]:
            cf = "continuously"
        elif output_cf in ["quarterly", "Quarterly"]:
            zero_df["Zero Rate"] = [
                400 * (math.pow(1 + i / 100, 1 / 4) - 1)
                for i in annualised(zero_df["Zero Rate"], "continuous")
            ]
            cf = "quarterly"
        elif output_cf in ["monthly", "Monthly"]:
            zero_df["Zero Rate"] = [
                1200 * (math.pow(1 + i / 100, 1 / 12) - 1)
                for i in annualised(zero_df["Zero Rate"], "continuous")
            ]
            cf = "monthly"
        elif output_cf in ["semi-annualised", "Semi-Annual"]:
            zero_df["Zero Rate"] = [
                200 * (math.pow(1 + i / 100, 1 / 2) - 1)
                for i in annualised(zero_df["Zero Rate"], "continuous")
            ]
            cf = "semi-annually"
        elif output_cf in ["bi-annual", "Bi-Annual"]:
            zero_df["Zero Rate"] = [
                50 * (math.pow(1 + i / 100, 1 / 0.5) - 1)
                for i in annualised(zero_df["Zero Rate"], "continuous")
            ]
            cf = "bi-annually"
        else:
            zero_df["Zero Rate"] = annualised(zero_df["Zero Rate"], "continuous")
            cf = "annually"

        zero_df["Extraction Date"] = [ext_date for i in zero_df.index]
        zero_df["Zero Rate"] = np.round_(list(zero_df["Zero Rate"]), decimals=4)

        plt.xlabel("Time to Maturity")
        plt.ylabel("Spot Rate")
        plt.plot(zero_df["t"], zero_df["Rate"], color="var(--primary-color)", label="Rate")
        plt.plot(
            zero_df["t"], zero_df["Zero Rate"], color="black", label="Zero Rate p.a. (compounded " + cf + ")"
        )
        plt.legend(loc=4)
        figfile = BytesIO()
        plt.savefig(figfile, format="png")
        plt.close()
        figfile.seek(0)
        figdata_png = figfile.getvalue()
        figdata_png = base64.b64encode(figdata_png)
        resultplot = figdata_png.decode("utf8")

        for i in zero_df.index:
            if zero_df["t"][i] not in list(df["Tenor"]):
                zero_df.drop(i, axis=0, inplace=True)

        zero_df["Tenor"] = list(df["Tenor Point"])
        zero_df = zero_df[["Tenor", "Rate", "Zero Rate", "Extraction Date"]]
        zero_df["Extraction Date"] = zero_df["Extraction Date"].astype(str)
        output_data = {"Table": zero_df.to_dict("records"), "Plot": resultplot, "curve_name": "Swap Curve"}
        return output_data, zero_df


def swap(data, config_dict):
    swapc = Swap_Curve_Bootstrapping()
    option_config = config_dict["inputs"]["option_config"]
    tenor = {
        "s_tenor": option_config["s_tenor"],
        "m_tenor": option_config["m_tenor"],
        "l_tenor": option_config["l_tenor"],
    }
    rate = {
        "s_rate": option_config["s_rate"],
        "m_rate": option_config["m_rate"],
        "l_rate": option_config["l_rate"],
    }
    s_cf = option_config["Short CF"]
    m_cf = option_config["Medium CF"]
    l_cf = option_config["Long CF"]
    st_tenor = option_config["Short Term Tenor"]
    mt_tenor = option_config["Medium Term Tenor"]
    ext_date = option_config["Extraction Date"]
    output_cf = option_config["Output CF"]
    instr = option_config["Medium Instrument"]
    m = option_config["Swap Payment Frequency"]
    if "Sigma" in option_config.keys():
        sigma = option_config["Sigma"]
        a = option_config["A"]
        output_data, zero_df = swapc.swap_curve(
            data,
            tenor,
            rate,
            s_cf,
            float(st_tenor),
            instr,
            m_cf,
            float(mt_tenor),
            l_cf,
            float(m),
            output_cf,
            ext_date,
            float(sigma),
            float(a),
        )
    else:
        output_data, zero_df = swapc.swap_curve(
            data,
            tenor,
            rate,
            s_cf,
            float(st_tenor),
            instr,
            m_cf,
            float(mt_tenor),
            l_cf,
            float(m),
            output_cf,
            ext_date,
        )
    return output_data, zero_df
