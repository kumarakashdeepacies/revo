# Packages used
import pandas as pd
from scipy import stats


class PortfolioMetrics:

    # Function to calculate simple daily returns

    def simp_ret(self, df):
        simple_returns = pd.DataFrame()
        simple_returns["Rp"] = df["Portfolio"].pct_change()

        if "Rm" in df.columns.to_list():
            simple_returns["Rm"] = df["Rm"].pct_change()

        if "Rf" in df.columns.to_list():
            simple_returns["Rf"] = df["Rf"]
            simple_returns["Rp-Rf"] = simple_returns["Rp"] - simple_returns["Rf"]

        simple_returns.dropna(axis=0, inplace=True)
        return simple_returns

    # Functions for calculating Portfolio Metrics

    def sharpe_ratio(self, df):
        t = len(df["Portfolio"])
        simple_returns = self.simp_ret(df)
        simple_returns.index = pd.RangeIndex(0, 0 + len(simple_returns))

        port_ret = (df["Portfolio"][len(df) - 1] - df["Portfolio"][0]) / df["Portfolio"][0]
        port_ret_ann = pow(1 + port_ret, 252 / t) - 1
        Rp = port_ret_ann

        Rf = simple_returns["Rf"][0]

        st_dev = simple_returns["Rp"].std() * pow(252 / t, 0.5)
        return (Rp - Rf) / st_dev

    def sortino_ratio(self, df):
        t = len(df["Portfolio"])
        simple_returns = self.simp_ret(df)
        simple_returns.index = pd.RangeIndex(0, 0 + len(simple_returns))

        port_ret = (df["Portfolio"][len(df) - 1] - df["Portfolio"][0]) / df["Portfolio"][0]
        port_ret_ann = pow(1 + port_ret, 252 / t) - 1
        Rp = port_ret_ann

        Rf = simple_returns["Rf"][0]

        mean = simple_returns["Rp"].mean()
        semi_dev = simple_returns["Rp"][simple_returns["Rp"] < mean].std() * pow(252 / t, 0.5)
        return (Rp - Rf) / semi_dev

    def info_ratio(self, df):
        t = len(df["Portfolio"])
        simple_returns = self.simp_ret(df)
        simple_returns.index = pd.RangeIndex(0, 0 + len(simple_returns))

        port_ret = (df["Portfolio"][len(df) - 1] - df["Portfolio"][0]) / df["Portfolio"][0]
        port_ret_ann = pow(1 + port_ret, 252 / t) - 1
        Rp = port_ret_ann

        Rf = simple_returns["Rf"][0]
        tracking_error = simple_returns["Rp-Rf"].std() * pow(252 / t, 0.5)
        return (Rp - Rf) / tracking_error

    def jensen_alpha(self, df):
        t = len(df["Portfolio"])
        simple_returns = self.simp_ret(df)
        simple_returns.index = pd.RangeIndex(0, 0 + len(simple_returns))

        port_ret = (df["Portfolio"][len(df) - 1] - df["Portfolio"][0]) / df["Portfolio"][0]
        port_ret_ann = pow(1 + port_ret, 252 / t) - 1
        Rp = port_ret_ann

        Rf = simple_returns["Rf"][0]

        market_ret = (df["Rm"][len(df) - 1] - df["Rm"][0]) / df["Rm"][0]
        market_ret_ann = pow(1 + market_ret, 252 / t) - 1
        Rm = market_ret_ann

        beta = stats.linregress(simple_returns["Rm"], simple_returns["Rp"])[0]
        return Rp - (Rf + beta * (Rm - Rf))

    def correl(self, df):
        simple_returns = self.simp_ret(df)
        simple_returns.index = pd.RangeIndex(0, 0 + len(simple_returns))
        output = simple_returns["Rp"].corr(simple_returns["Rf"])
        return output

    def beta(self, df):
        simple_returns = self.simp_ret(df)
        simple_returns.index = pd.RangeIndex(0, 0 + len(simple_returns))
        output = stats.linregress(simple_returns["Rm"], simple_returns["Rp"])[0]
        return output

    def treynorRatio(self, df):
        t = len(df["Portfolio"])
        simple_returns = self.simp_ret(df)
        simple_returns.index = pd.RangeIndex(0, 0 + len(simple_returns))

        port_ret = (df["Portfolio"][len(df) - 1] - df["Portfolio"][0]) / df["Portfolio"][0]
        port_ret_ann = pow(1 + port_ret, 252 / t) - 1
        Rp = port_ret_ann

        Rf = simple_returns["Rf"][0]

        beta = stats.linregress(simple_returns["Rm"], simple_returns["Rp"])[0]
        return (Rp - Rf) / beta

    def maxDD(self, df):
        # Define the number of trading days as window, ie 252 days
        window = 252

        Roll_Max = df["Portfolio"].rolling(window, min_periods=1).max()
        Daily_Drawdown = df["Portfolio"] / Roll_Max - 1.0

        mdd = Daily_Drawdown.min()
        return mdd

    def maxDDApprox(self, df):
        # Define the maxDDApprox

        trough = min(df["Portfolio"])
        peak = max(df["Portfolio"])

        mdd = (trough - peak) / peak
        return mdd

    # Function for calling subsequent functions based on the value of metric

    def compute_portfolio_metrics(
        self,
        metric,
        start_date,
        end_date,
        portfolioPositions,
        portfolio_date,
        portfolio_fund_code,
        portfolio_mtm,
        portfolio_unique_id,
        riskfree=None,
        riskfree_date=None,
        riskfree_value=None,
        market=None,
        market_date=None,
        market_value=None,
    ):

        # typecasting date column into date type
        position = pd.DataFrame()
        position["Date"] = pd.to_datetime(portfolioPositions[portfolio_date])
        position[portfolio_fund_code] = portfolioPositions[portfolio_fund_code]
        position[portfolio_unique_id] = portfolioPositions[portfolio_unique_id]
        position[portfolio_mtm] = portfolioPositions[portfolio_mtm]

        if riskfree is not None:
            riskfree_data = pd.DataFrame()
            riskfree_data["Date"] = pd.to_datetime(riskfree[riskfree_date])
            riskfree_data["Rf"] = riskfree[riskfree_value]

        if market is not None:
            market["Date"] = pd.to_datetime(market[market_date])
            market_data = pd.DataFrame()
            market_data["Date"] = market["Date"]
            market_data["Rm"] = market[market_value]

        # setting position dataframe between start_date and end_date
        after_start_date = position["Date"] >= start_date
        before_end_date = position["Date"] <= end_date
        between_two_dates = after_start_date & before_end_date
        filtered_dates = position.loc[between_two_dates]

        # Listing the unique fund codes
        fund_codes = filtered_dates[portfolio_fund_code].unique()
        gb = filtered_dates.groupby(portfolio_fund_code)

        # Initialising output Data Frame
        output_df = pd.DataFrame(columns=["Fund_Code"])

        for code in fund_codes:
            df = gb.get_group(code)
            port = df.groupby("Date").agg({portfolio_mtm: "sum"}).rename(columns={portfolio_mtm: "Portfolio"})

            df = port
            reset = df.index
            if market is not None:
                df = df.merge(market_data, how="left", left_index=True, right_on="Date")
                df.index = reset
            if riskfree is not None:
                df = df.merge(riskfree_data, how="left", left_index=True, right_on="Date")
                df.index = reset

            df.index = reset

            # forward filling the N/A s in the riskfree and market columns
            df = df.ffill().bfill()
            df.index = pd.RangeIndex(0, 0 + len(df))

            # appending the output dictionary with all the values
            if metric == "sharpeRatio":
                output_dict = {"Fund_Code": code, "Sharpe_Ratio": self.sharpe_ratio(df)}
                output_dict_df1 = pd.DataFrame.from_dict([output_dict])
                output_df = pd.concat([output_df, output_dict_df1], ignore_index=True)

            elif metric == "sortinoRatio":
                output_dict = {"Fund_Code": code, "Sortino_Ratio": self.sortino_ratio(df)}
                output_dict_df1 = pd.DataFrame.from_dict([output_dict])
                output_df = pd.concat([output_df, output_dict_df1], ignore_index=True)
            elif metric == "informationRatio":
                output_dict = {"Fund_Code": code, "Information_Ratio": self.info_ratio(df)}
                output_dict_df1 = pd.DataFrame.from_dict([output_dict])
                output_df = pd.concat([output_df, output_dict_df1], ignore_index=True)

            elif metric == "jensensAlpha":
                output_dict = {"Fund_Code": code, "Jensens_Alpha": self.jensen_alpha(df)}
                output_dict_df1 = pd.DataFrame.from_dict([output_dict])
                output_df = pd.concat([output_df, output_dict_df1], ignore_index=True)

            elif metric == "correlation":
                output_dict = {"Fund_Code": code, "Correlation": self.correl(df)}
                output_dict_df1 = pd.DataFrame.from_dict([output_dict])
                output_df = pd.concat([output_df, output_dict_df1], ignore_index=True)

            elif metric == "beta":
                output_dict = {"Fund_Code": code, "Beta": self.beta(df)}
                output_dict_df1 = pd.DataFrame.from_dict([output_dict])
                output_df = pd.concat([output_df, output_dict_df1], ignore_index=True)

            elif metric == "treynorRatio":
                output_dict = {"Fund_Code": code, "Treynor Ratio": self.treynorRatio(df)}
                output_dict_df1 = pd.DataFrame.from_dict([output_dict])
                output_df = pd.concat([output_df, output_dict_df1], ignore_index=True)

            elif metric == "maxDD":
                output_dict = {"Fund_Code": code, "Max Drawdown": self.maxDD(df)}
                output_dict_df1 = pd.DataFrame.from_dict([output_dict])
                output_df = pd.concat([output_df, output_dict_df1], ignore_index=True)

            elif metric == "maxDDApprox":
                output_dict = {"Fund_Code": code, "Max Drawdown (approx)": self.maxDDApprox(df)}
                output_dict_df1 = pd.DataFrame.from_dict([output_dict])
                output_df = pd.concat([output_df, output_dict_df1], ignore_index=True)
        return output_df

    # Function to unwrap config and call the required functions

    def unwrap_config(self, portfolio_data, config_dict, riskfree_data=None, market_data=None):

        metric = config_dict["inputs"]["option_config"]["metric"]
        start_date = config_dict["inputs"]["option_config"]["start_date"]
        end_date = config_dict["inputs"]["option_config"]["end_date"]
        portfolio_date = config_dict["inputs"]["option_config"]["portfolio_date"]
        portfolio_fund_code = config_dict["inputs"]["option_config"]["portfolio_fund_code"]
        portfolio_mtm = config_dict["inputs"]["option_config"]["portfolio_mtm"]
        portfolio_unique_id = config_dict["inputs"]["option_config"]["portfolio_unique_id"]

        if riskfree_data is not None:
            riskfree_date = config_dict["inputs"]["option_config"]["riskfree_date"]
            riskfree_value = config_dict["inputs"]["option_config"]["riskfree_value"]
        else:
            riskfree_date = None
            riskfree_value = None

        if market_data is not None:
            market_date = config_dict["inputs"]["option_config"]["market_date"]
            market_value = config_dict["inputs"]["option_config"]["market_value"]
        else:
            market_date = None
            market_value = None

        output = self.compute_portfolio_metrics(
            metric,
            start_date,
            end_date,
            portfolio_data,
            portfolio_date,
            portfolio_fund_code,
            portfolio_mtm,
            portfolio_unique_id,
            riskfree_data,
            riskfree_date,
            riskfree_value,
            market_data,
            market_date,
            market_value,
        )
        return output
