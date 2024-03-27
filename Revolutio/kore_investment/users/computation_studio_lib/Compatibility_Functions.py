import math

import numpy as np
import scipy.stats as stats
from scipy.stats import beta


class StatOperations:

    def beta_dist(self, dataframe, x_col, alpha_col, beta_col, x_min, x_max, cumulative):
        dataframe[x_col] = dataframe[x_col].astype(float)
        dataframe[alpha_col] = dataframe[alpha_col].astype(float)
        dataframe[beta_col] = dataframe[beta_col].astype(float)
        if x_min == x_max:
            dataframe["Beta Distribution Value"] = np.nan
        else:
            dataframe["x_min"] = x_min
            dataframe["x_max"] = x_max
            if cumulative == "True":
                dist_func = stats.beta.cdf
            else:
                dist_func = beta.pdf
            x_beta_dist = dist_func(
                (dataframe[x_col] - dataframe["x_min"]) / (dataframe["x_max"] - dataframe["x_min"]),
                dataframe[alpha_col],
                dataframe[beta_col],
            )
            dataframe["Beta Distribution Value"] = x_beta_dist
            dataframe.drop(["x_max", "x_min"], axis=1, inplace=True)
        return dataframe

    def binom_dist(self, dataframe, x_col, alpha_col, beta_col, cumulative):
        dataframe[x_col] = dataframe[x_col].astype(int)
        dataframe[alpha_col] = dataframe[alpha_col].astype(int)
        dataframe[beta_col] = dataframe[beta_col].astype(float)
        if cumulative == "True":
            distribution = stats.binom.cdf(dataframe[x_col], dataframe[alpha_col], dataframe[beta_col])
        else:
            distribution = stats.binom.pmf(dataframe[x_col], dataframe[alpha_col], dataframe[beta_col])
        dataframe["Binomial Distribution Value"] = distribution
        return dataframe

    def chisq_dist(self, dataframe, x_col, alpha_col, cumulative):
        dataframe[x_col] = dataframe[x_col].astype(float)
        dataframe[alpha_col] = dataframe[alpha_col].astype(int)
        if cumulative == "True":
            result = stats.chi2.cdf(dataframe[x_col], dataframe[alpha_col])
        else:
            result = stats.chi2.pdf(dataframe[x_col], dataframe[alpha_col])
        dataframe["Chi-Squared Distribution Value"] = result
        return dataframe

    def expon_dist(self, dataframe, x_col, alpha_col, cumulative):
        dataframe[x_col] = dataframe[x_col].astype(float)
        dataframe[alpha_col] = dataframe[alpha_col].astype(float)
        if cumulative == "True":
            distribution = stats.expon.cdf(dataframe[x_col], scale=1 / dataframe[alpha_col])
            label = "Exponential CDF"
        else:
            distribution = stats.expon.pdf(dataframe[x_col], scale=1 / dataframe[alpha_col])
            label = "Exponential PDF"
        dataframe[label] = distribution
        return dataframe

    def f_dist(self, dataframe, x_col, alpha_col, beta_col, cumulative):
        dataframe[x_col] = dataframe[x_col].astype(float)
        dataframe[alpha_col] = dataframe[alpha_col].astype(int)
        dataframe[beta_col] = dataframe[beta_col].astype(int)
        if cumulative == "True":
            distribution = stats.f.cdf(dataframe[x_col], dataframe[alpha_col], dataframe[beta_col])
            label = "F Distribution CDF"
        else:
            distribution = stats.f.pdf(dataframe[x_col], dataframe[alpha_col], dataframe[beta_col])
            label = "F Distribution PDF"
        dataframe[label] = distribution
        return dataframe

    def gamma_dist(self, dataframe, x_col, alpha_col, beta_col, cumulative):
        dataframe[x_col] = dataframe[x_col].astype(float)
        dataframe[alpha_col] = dataframe[alpha_col].astype(float)
        dataframe[beta_col] = dataframe[beta_col].astype(float)
        if cumulative == "True":
            distribution = stats.gamma.cdf(dataframe[x_col], dataframe[alpha_col], scale=dataframe[beta_col])
        else:
            distribution = stats.gamma.pdf(dataframe[x_col], dataframe[alpha_col], scale=dataframe[beta_col])

        dataframe["GAMMA Distribution"] = distribution
        return dataframe

    def hypgeom_dist(self, dataframe, x_col, alpha_col, beta_col, pop_col, cumulative):
        dataframe[x_col] = dataframe[x_col].astype(int)
        dataframe[alpha_col] = dataframe[alpha_col].astype(int)
        dataframe[beta_col] = dataframe[beta_col].astype(int)
        dataframe[pop_col] = dataframe[pop_col].astype(int)
        if cumulative == "True":
            distribution = stats.hypergeom.cdf(
                dataframe[x_col], dataframe[pop_col], dataframe[beta_col], dataframe[alpha_col]
            )
        else:
            distribution = stats.hypergeom.pmf(
                dataframe[x_col], dataframe[pop_col], dataframe[beta_col], dataframe[alpha_col]
            )
        dataframe["HYPGEOM Distribution"] = distribution
        return dataframe

    def log_dist(self, dataframe, x_col, alpha_col, beta_col, cumulative):
        dataframe[x_col] = dataframe[x_col].astype(float)
        dataframe[alpha_col] = dataframe[alpha_col].astype(float)
        dataframe[beta_col] = dataframe[beta_col].astype(float)
        if cumulative == "True":
            logdist = stats.lognorm.cdf(
                dataframe[x_col], dataframe[beta_col], scale=np.exp(dataframe[alpha_col])
            )
        else:
            logdist = stats.lognorm.pdf(
                dataframe[x_col], s=dataframe[beta_col], scale=np.exp(dataframe[alpha_col])
            )
        dataframe["LOG Distribution"] = logdist
        return dataframe

    def norm_dist(self, dataframe, x_col, alpha_col, beta_col, cumulative):
        dataframe[x_col] = dataframe[x_col].astype(float)
        dataframe[alpha_col] = dataframe[alpha_col].astype(float)
        dataframe[beta_col] = dataframe[beta_col].astype(float)
        if cumulative == "True":
            normdist = stats.norm.cdf(dataframe[x_col], dataframe[alpha_col], scale=dataframe[beta_col])
        else:
            normdist = stats.norm.pdf(dataframe[x_col], dataframe[alpha_col], scale=dataframe[beta_col])
        dataframe["Normal Distribution"] = normdist
        return dataframe

    def negbinom_dist(self, dataframe, x_col, alpha_col, beta_col, cumulative):
        dataframe[x_col] = dataframe[x_col].astype(float)
        dataframe[alpha_col] = dataframe[alpha_col].astype(float)
        dataframe[beta_col] = dataframe[beta_col].astype(float)
        if cumulative == "True":
            distribution = stats.nbinom.cdf(dataframe[x_col], dataframe[alpha_col], dataframe[beta_col])
        else:
            distribution = stats.nbinom.pmf(dataframe[x_col], dataframe[alpha_col], dataframe[beta_col])
        dataframe["Negative Binomial Distributon"] = distribution
        return dataframe

    def norms_dist(self, dataframe, x_col, cumulative):
        dataframe[x_col] = dataframe[x_col].astype(float)
        m = 0
        s = 1
        if cumulative == "True":
            normdist = stats.norm.cdf(dataframe[x_col], m, scale=s)
        else:
            normdist = stats.norm.pdf(dataframe[x_col], m, scale=s)
        dataframe[" Standard Normal Distribution"] = normdist
        return dataframe

    def poisson_dist(self, dataframe, x_col, alpha_col, cumulative):
        dataframe[x_col] = dataframe[x_col].astype(int)
        dataframe[alpha_col] = dataframe[alpha_col].astype(float)
        if cumulative == "True":
            distribution = stats.poisson.cdf(dataframe[x_col], dataframe[alpha_col])
        else:
            distribution = stats.poisson.pmf(dataframe[x_col], dataframe[alpha_col])
        dataframe["Poisson Distribution"] = distribution
        return dataframe

    def tdist(self, dataframe, x_col, alpha_col, tails):
        dataframe[x_col] = dataframe[x_col].astype(float)
        dataframe[alpha_col] = dataframe[alpha_col].astype(int)
        tails = int(tails)
        if tails == 1:
            p = stats.t.sf(abs(dataframe[x_col]), dataframe[alpha_col])
        else:
            p = stats.t.sf(abs(dataframe[x_col]), dataframe[alpha_col]) * 2
        dataframe["TDIST"] = p
        return dataframe

    def weibull_dist(self, dataframe, x_col, alpha_col, beta_col, cumulative):
        dataframe[x_col] = dataframe[x_col].astype(float)
        dataframe[alpha_col] = dataframe[alpha_col].astype(float)
        dataframe[beta_col] = dataframe[beta_col].astype(float)
        if cumulative == "True":
            distribution = stats.weibull_min.cdf(
                dataframe[x_col], dataframe[alpha_col], scale=dataframe[beta_col]
            )
        else:
            distribution = stats.weibull_min.pdf(
                dataframe[x_col], dataframe[alpha_col], scale=dataframe[beta_col]
            )
        dataframe["Weibull Distribution"] = distribution
        return dataframe

    def beta_inv(self, dataframe, x_col, alpha_col, beta_col, x_min, x_max):
        dataframe[x_col] = dataframe[x_col].astype(float)
        dataframe[alpha_col] = dataframe[alpha_col].astype(float)
        dataframe[beta_col] = dataframe[beta_col].astype(float)
        x_inv_beta_dist = stats.beta.ppf(
            dataframe[x_col], dataframe[alpha_col], dataframe[beta_col], loc=x_min, scale=(x_max) - (x_min)
        )
        dataframe["BETA Inverse Value"] = x_inv_beta_dist
        return dataframe

    def chisq_inv(self, dataframe, x_col, alpha_col):
        dataframe[x_col] = dataframe[x_col].astype(float)
        dataframe[alpha_col] = dataframe[alpha_col].astype(int)
        result = stats.chi2.ppf(dataframe[x_col], dataframe[alpha_col])
        dataframe["Chi-Squared Inverse Value"] = result
        return dataframe

    def f_inv(self, dataframe, x_col, alpha_col, beta_col):
        dataframe[x_col] = dataframe[x_col].astype(float)
        dataframe[alpha_col] = dataframe[alpha_col].astype(int)
        dataframe[beta_col] = dataframe[beta_col].astype(int)
        distribution = stats.f.ppf(dataframe[x_col], dataframe[alpha_col], dataframe[beta_col])
        dataframe["F Inverse Value"] = distribution
        return dataframe

    def binom_inv(self, dataframe, x_col, alpha_col, beta_col):
        dataframe[x_col] = dataframe[x_col].astype(float)
        dataframe[alpha_col] = dataframe[alpha_col].astype(float)
        dataframe[beta_col] = dataframe[beta_col].astype(float)
        k_crit = stats.binom.ppf(q=dataframe[beta_col], n=dataframe[x_col], p=dataframe[alpha_col])
        dataframe["Binomial Inverse Value"] = k_crit
        return dataframe

    def gamma_inv(self, dataframe, x_col, alpha_col, beta_col):
        dataframe[x_col] = dataframe[x_col].astype(float)
        dataframe[alpha_col] = dataframe[alpha_col].astype(float)
        dataframe[beta_col] = dataframe[beta_col].astype(float)
        distribution = stats.gamma.ppf(dataframe[x_col], dataframe[alpha_col], scale=dataframe[beta_col])
        dataframe["GAMMA Inverse Value"] = distribution
        return dataframe

    def log_inv(self, dataframe, x_col, alpha_col, beta_col):
        dataframe[x_col] = dataframe[x_col].astype(float)
        dataframe[alpha_col] = dataframe[alpha_col].astype(float)
        dataframe[beta_col] = dataframe[beta_col].astype(float)
        loginverse = stats.lognorm.ppf(
            dataframe[x_col], dataframe[beta_col], loc=0, scale=np.exp(dataframe[alpha_col])
        )
        dataframe["LOG Inverse Value"] = loginverse
        return dataframe

    def norm_inv(self, dataframe, x_col, alpha_col, beta_col):
        dataframe[x_col] = dataframe[x_col].astype(float)
        dataframe[alpha_col] = dataframe[alpha_col].astype(float)
        dataframe[beta_col] = dataframe[beta_col].astype(float)
        norminv = stats.norm.ppf(dataframe[x_col], dataframe[alpha_col], scale=dataframe[beta_col])
        dataframe["Normal Inverse Distribution Value"] = norminv
        return dataframe

    def norms_inv(self, dataframe, x_col):
        dataframe[x_col] = dataframe[x_col].astype(float)
        m = 0
        s = 1
        normsinv = stats.norm.ppf(dataframe[x_col], m, scale=s)
        dataframe["Standard Normal Inverse Distribution Value"] = normsinv
        return dataframe

    def tinv(self, dataframe, x_col, alpha_col):
        dataframe[x_col] = dataframe[x_col].astype(float)
        dataframe[alpha_col] = dataframe[alpha_col].astype(int)
        t_val = stats.t.ppf(1 - (dataframe[x_col]) / 2, dataframe[alpha_col])
        dataframe["TINV"] = t_val
        return dataframe

    def chitest(self, dataframe, act_col, expected_col):
        observed_counts = dataframe[act_col].values
        expected_counts = dataframe[expected_col].values
        chi_sq = np.sum((observed_counts - expected_counts) ** 2 / expected_counts)
        pval = 1 - (stats.chi2.cdf(chi_sq, len(observed_counts) - 1))
        dataframe["Chi Test Value"] = pval
        return dataframe

    def ftest(self, dataframe, x_col, alpha_col):
        var1 = np.var(dataframe[x_col])
        var2 = np.var(dataframe[alpha_col])
        if var1 > var2:
            f = var1 / var2
        else:
            f = var2 / var1
        pval = 2 * (1 - stats.f.cdf(f, len(dataframe[x_col]) - 1, len(dataframe[alpha_col]) - 1))
        dataframe["F Test Value"] = pval
        return dataframe

    def t_test(self, dataframe, x_col, alpha_col, tails, types):
        if types == "Equal":
            _, p_val = stats.ttest_ind(dataframe[x_col], dataframe[alpha_col], equal_var=True)
        elif types == "Unequal":
            _, p_val = stats.ttest_ind(dataframe[x_col], dataframe[alpha_col], equal_var=False)
        else:
            pass
        if tails == 1:
            p_val /= 2
        dataframe["T Test Value"] = p_val
        return dataframe

    def z_test(self, dataframe, x_col, x, sigma, tails):
        n = len(dataframe[x_col])
        mean = dataframe[x_col].mean()
        std = dataframe[x_col].std(ddof=1)
        if sigma == None:
            z_stat = (mean - x) / (std / (n**0.5))
        else:
            z_stat = (mean - x) / (sigma / (n**0.5))
        if tails == 1:
            p_val = 1 - stats.norm.cdf(z_stat)
        else:
            p_val = stats.norm.sf(abs(z_stat)) * 2
        dataframe["Z Test Value"] = p_val
        return dataframe

    def confidence_norm(self, dataframe, x_col, alpha_col, beta_col):
        z_score = stats.norm.ppf(1 - (dataframe[x_col]) / 2)
        dataframe["Standard Error"] = dataframe[alpha_col] / np.sqrt(dataframe[beta_col])
        dataframe["Margin of Error"] = z_score * dataframe["Standard Error"]
        return dataframe

    def covariance_p(self, dataframe, x_col, alpha_col):
        cov_matrix = dataframe[[x_col, alpha_col]].cov(ddof=0)
        cov_xy = cov_matrix.iloc[0, 1]
        dataframe["Covariance"] = cov_xy
        return dataframe

    def floor(self, dataframe, act_col, factor_col):
        for col in act_col:
            dataframe[col] = dataframe[col].astype(float)
            result = np.floor(dataframe[col] / factor_col) * factor_col
            dataframe[f"FLOOR {col}"] = result
        return dataframe

    def mode_sngl(self, dataframe, act_col):
        for col in act_col:
            dataframe[col] = dataframe[col].astype(float)
            mode_1 = st.mode(dataframe[col])
            dataframe[f"Mode {col}"] = mode_1
        return dataframe

    def percentile_inv(self, dataframe, act_col, percentile):
        for col in act_col:
            data = dataframe[col].values
            percentile_val = np.percentile(data, percentile, interpolation="linear")
            col_name = f"Percentile {col}"
            dataframe[col_name] = percentile_val
        return dataframe

    def percentrank(self, dataframe, act_col, percentile, sigma):
        for col in act_col:
            data = dataframe[col].values.flatten()
            n = len(data)
            count_below = np.sum(data < percentile)
            count_equal = np.sum(data == percentile)
            percentile_below = count_below / (n - 1)
            if percentile in data:
                percentile_rounded = round(percentile_below * 100, sigma)
            else:
                idx = np.argsort(np.abs(data - percentile))[0]
                x_nearest = data[idx]
                if percentile < x_nearest:
                    x_above = x_nearest
                    x_below = data[idx - 1]
                else:
                    x_above = data[idx + 1]
                    x_below = x_nearest
                count_above = np.sum(data > percentile)
                count_equal = np.sum(data == percentile)
                count_below = np.sum(data < percentile)
                percentile_above = count_below / (n - 1)
                percentile_below = 1 - (count_above / (n - 1))
                percentile_rounded = round(
                    percentile_below
                    + (
                        ((percentile - x_below) / (x_above - x_below)) * (percentile_above - percentile_below)
                    ),
                    sigma,
                )
            dataframe[f"Percent Rank_{col}"] = percentile_rounded
        return dataframe

    def quartile_exc(self, dataframe, act_col, percentile):
        for col in act_col:
            dataframe[col] = dataframe[col].dropna()
            arr = np.sort(dataframe[col].values)
            n = len(arr)
            if n == 0:
                q_val = np.nan
            elif n == 1:
                q_val = arr[0]
            else:
                q_val = np.percentile(arr, percentile * 100, interpolation="lower")
            dataframe[f"{col} Quartile"] = q_val
        return dataframe

    def calculate_rank(self, dataframe, act_col):
        for col in act_col:
            dataframe[f"Rank_{col}"] = dataframe[col].rank(method="min")
        return dataframe

    def stdev(self, dataframe, act_col):
        for col in act_col:
            dataframe[f"STDEV {col}"] = dataframe[col].std(ddof=1)
        return dataframe

    def stdev_p(self, dataframe, act_col):
        for col in act_col:
            dataframe[f"STDEV POPULATION {col}"] = dataframe[col].std(ddof=0)
        return dataframe

    def var_p(self, dataframe, act_col):
        for col in act_col:
            dataframe[f"VARIANCE POPULATION {col}"] = dataframe[col].var(ddof=0)
        return dataframe

    def var_s(self, dataframe, act_col):
        for col in act_col:
            dataframe[f"VARIANCE {col}"] = dataframe[col].var(ddof=1)
        return dataframe

    def ceiling(self, dataframe, act_col, factor_col):
        s = factor_col
        scalar_ceil = np.vectorize(lambda x: math.ceil(x))
        for col in act_col:
            n = dataframe[col].to_numpy()
            dataframe[col + "_Ceiling"] = scalar_ceil(n / s) * s
        return dataframe


def Compatibility_Func(dataframe, config_dict):
    StatFunc = StatOperations()
    sub_operation = config_dict["inputs"]["Sub_Op"]
    operation = config_dict["inputs"]["Operation"]

    if operation == "Distribution Function":
        x_col = config_dict["inputs"]["Other_Inputs"]["X_Col"]
        alpha_col = config_dict["inputs"]["Other_Inputs"]["Alpha_Col"]
        beta_col = config_dict["inputs"]["Other_Inputs"]["Beta_Col"]
        pop_col = config_dict["inputs"]["Other_Inputs"]["Pop_Col"]
        x_min = config_dict["inputs"]["Other_Inputs"]["X_Min"]
        x_max = config_dict["inputs"]["Other_Inputs"]["X_Max"]
        tails = config_dict["inputs"]["Other_Inputs"]["Tails"]
        cumulative = config_dict["inputs"]["Other_Inputs"]["Cumulative"]

        if sub_operation == "BETADIST":
            output_data = StatFunc.beta_dist(dataframe, x_col, alpha_col, beta_col, x_min, x_max, cumulative)
            return output_data

        elif sub_operation == "BINOMDIST":
            output_data = StatFunc.binom_dist(dataframe, x_col, alpha_col, beta_col, cumulative)
            return output_data

        elif sub_operation == "CHIDIST":
            output_data = StatFunc.chisq_dist(dataframe, x_col, alpha_col, cumulative)
            return output_data

        elif sub_operation == "EXPONDIST":
            output_data = StatFunc.expon_dist(dataframe, x_col, alpha_col, cumulative)
            return output_data

        elif sub_operation == "FDIST":
            output_data = StatFunc.f_dist(dataframe, x_col, alpha_col, beta_col, cumulative)
            return output_data

        elif sub_operation == "GAMMADIST":
            output_data = StatFunc.gamma_dist(dataframe, x_col, alpha_col, beta_col, cumulative)
            return output_data

        elif sub_operation == "HYPGEOMDIST":
            output_data = StatFunc.hypgeom_dist(dataframe, x_col, alpha_col, beta_col, pop_col, cumulative)
            return output_data

        elif sub_operation == "LOGNORMDIST":
            output_data = StatFunc.log_dist(dataframe, x_col, alpha_col, beta_col, cumulative)
            return output_data

        elif sub_operation == "NORMDIST":
            output_data = StatFunc.norm_dist(dataframe, x_col, alpha_col, beta_col, cumulative)
            return output_data

        elif sub_operation == "NEGBINOMDIST":
            output_data = StatFunc.negbinom_dist(dataframe, x_col, alpha_col, beta_col, cumulative)
            return output_data

        elif sub_operation == "NORMSDIST":
            output_data = StatFunc.norms_dist(dataframe, x_col, cumulative)
            return output_data

        elif sub_operation == "POISSONDIST":
            output_data = StatFunc.poisson_dist(dataframe, x_col, alpha_col, cumulative)
            return output_data

        elif sub_operation == "TDIST":
            output_data = StatFunc.tdist(dataframe, x_col, alpha_col, tails)
            return output_data

        elif sub_operation == "WEIBULLDIST":
            output_data = StatFunc.weibull_dist(dataframe, x_col, alpha_col, beta_col, cumulative)
            return output_data

    elif operation == "Inverse Functions":
        x_col = config_dict["inputs"]["Other_Inputs"]["X_Col"]
        alpha_col = config_dict["inputs"]["Other_Inputs"]["Alpha_Col"]
        beta_col = config_dict["inputs"]["Other_Inputs"]["Beta_Col"]
        pop_col = config_dict["inputs"]["Other_Inputs"]["Pop_Col"]
        x_min = config_dict["inputs"]["Other_Inputs"]["X_Min"]
        x_max = config_dict["inputs"]["Other_Inputs"]["X_Max"]
        if sub_operation == "BETAINV":
            output_data = StatFunc.beta_inv(dataframe, x_col, alpha_col, beta_col, x_min, x_max)
            return output_data

        elif sub_operation == "CHIINV":
            output_data = StatFunc.chisq_inv(dataframe, x_col, alpha_col)
            return output_data

        elif sub_operation == "ComV":
            output_data = StatFunc.f_inv(dataframe, x_col, alpha_col, beta_col)
            return output_data

        elif sub_operation == "CRITBINOM":
            output_data = StatFunc.binom_inv(dataframe, x_col, alpha_col, beta_col)
            return output_data

        elif sub_operation == "GAMMAINV":
            output_data = StatFunc.gamma_inv(dataframe, x_col, alpha_col, beta_col)
            return output_data

        elif sub_operation == "LOGINV":
            output_data = StatFunc.log_inv(dataframe, x_col, alpha_col, beta_col)
            return output_data

        elif sub_operation == "NORMINV":
            output_data = StatFunc.norm_inv(dataframe, x_col, alpha_col, beta_col)
            return output_data

        elif sub_operation == "NORMSINV":
            output_data = StatFunc.norms_inv(dataframe, x_col)
            return output_data

        elif sub_operation == "TINV":
            output_data = StatFunc.tinv(dataframe, x_col, alpha_col)
            return output_data

    elif operation == "Test Functions":
        act_col = config_dict["inputs"]["Other_Inputs"]["Actual_Value"]
        expected_col = config_dict["inputs"]["Other_Inputs"]["Expected_Value"]
        x_col = config_dict["inputs"]["Other_Inputs"]["X_Col"]
        alpha_col = config_dict["inputs"]["Other_Inputs"]["Alpha_Col"]
        tails = config_dict["inputs"]["Other_Inputs"]["Tails"]
        types = config_dict["inputs"]["Other_Inputs"]["Equal"]
        x = config_dict["inputs"]["Other_Inputs"]["X_Min"]
        sigma = config_dict["inputs"]["Other_Inputs"]["X_Max"]

        if sub_operation == "CHITEST":
            output_data = StatFunc.chitest(dataframe, act_col, expected_col)
            return output_data

        elif sub_operation == "FTEST":
            output_data = StatFunc.ftest(dataframe, x_col, alpha_col)
            return output_data

        elif sub_operation == "TTEST":
            output_data = StatFunc.t_test(dataframe, x_col, alpha_col, tails, types)
            return output_data

        elif sub_operation == "ZTEST":
            output_data = StatFunc.z_test(dataframe, x_col, x, sigma, tails)
            return output_data

    elif operation == "Miscellaneous Functions":
        x_col = config_dict["inputs"]["Other_Inputs"]["X_Col"]
        alpha_col = config_dict["inputs"]["Other_Inputs"]["Alpha_Col"]
        beta_col = config_dict["inputs"]["Other_Inputs"]["Beta_Col"]
        factor_col = config_dict["inputs"]["Other_Inputs"]["X_Min"]
        act_col = config_dict["inputs"]["Other_Inputs"]["Actual_Value"]
        percentile = config_dict["inputs"]["Other_Inputs"]["X_Max"]
        sigma = config_dict["inputs"]["Other_Inputs"]["Sigma"]

        if sub_operation == "CONFIDENCE":
            output_data = StatFunc.confidence_norm(dataframe, x_col, alpha_col, beta_col)
            return output_data

        elif sub_operation == "COVAR":
            output_data = StatFunc.covariance_p(dataframe, x_col, alpha_col)
            return output_data

        elif sub_operation == "FLOOR":
            output_data = StatFunc.floor(dataframe, act_col, factor_col)
            return output_data

        elif sub_operation == "MODE":
            output_data = StatFunc.mode_sngl(dataframe, act_col)
            return output_data

        elif sub_operation == "PERCENTILE":
            output_data = StatFunc.percentile_inv(dataframe, act_col, percentile)
            return output_data

        elif sub_operation == "PERCENTRANK":
            output_data = StatFunc.percentrank(dataframe, act_col, percentile, sigma)
            return output_data

        elif sub_operation == "QUARTILE":
            output_data = StatFunc.quartile_exc(dataframe, act_col, percentile)
            return output_data

        elif sub_operation == "RANK":
            output_data = StatFunc.calculate_rank(dataframe, act_col)
            return output_data

        elif sub_operation == "STDEV":
            output_data = StatFunc.stdev(dataframe, act_col)
            return output_data

        elif sub_operation == "STDEVP":
            output_data = StatFunc.stdev_p(dataframe, act_col)
            return output_data

        elif sub_operation == "VAR":
            output_data = StatFunc.var_s(dataframe, act_col)
            return output_data

        elif sub_operation == "VARP":
            output_data = StatFunc.var_p(dataframe, act_col)
            return output_data

        elif sub_operation == "CEILING":
            output_data = StatFunc.ceiling(dataframe, act_col, factor_col)
            return output_data
