"""
Created on Thu Oct 29 15:51:40 2020

@author: AbhiJain
"""

import base64
from io import BytesIO
import pickle

from arch import arch_model
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats.distributions import chi2
from sklearn.metrics import mean_squared_error
import statsmodels.graphics.tsaplots as sgt
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.stats.stattools import jarque_bera
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import statsmodels.tsa.stattools as sts

### Tests Used ###

# Augmented Dickey Fuller Test for Stationarity - The Augmented Dickey Fuller Test (ADF) is unit root test for stationarity.The null hypothesis for this test is that there is a unit root.The alternate hypothesis is that the time series is stationary (or trend-stationary).
# LLR Test - The likelihood-ratio test assesses the goodness of fit of two competing statistical models based on the ratio of their likelihoods.
# Ljung and Box Test - The test determines whether or not residuals are white noise (i.e.iid) . The null hypothesis H0 is that the residuals of the fitted model form a white noise process. The alternate hypothesis H1 is that the residuals of the fitted model does not form a white noise process.
# Jarque-Bera Test - The Jarque-Bera test statistic tests the null hypothesis that the data is normally distributed against an alternative that the data follows some other distribution. The test statistic is based on two moments of the data, the skewness, and the kurtosis, and has an asymptotic chi-square distribution.
# AIC - The Akaike information criterion (AIC) is an estimator of in-sample prediction error and thereby relative quality of statistical models for a given set of data. When comparing two models , a model with lower AIC is preferred.
# BIC - The Bayesian information criterion (BIC) or Schwarz information criterion (also SIC, SBC, SBIC) is a criterion for model selection among a finite set of models; the model with the lowest BIC is preferred. It is based, in part, on the likelihood function and it is closely related to the Akaike information criterion (AIC).


### Log Likelihood Ratio Test
def LLR_Test_ARIMA(mod_1, mod_2, DF=1):
    L1 = mod_1.llf
    L2 = mod_2.llf
    LR = 2 * (L2 - L1)
    p = chi2.sf(LR, DF).round(3)
    return p


def LLR_Test_GARCH(mod_1, mod_2, DF=1):
    L1 = mod_1.loglikelihood
    L2 = mod_2.loglikelihood
    LR = 2 * (L2 - L1)
    p = chi2.sf(LR, DF).round(3)
    return p


### Modelling starts here


class Time_Series_Models:
    def data_stationarity_test(self, data_set, time_series):
        # ADF Test of Stationarity - Time series data
        p_value = sts.adfuller(data_set[time_series].dropna())[1]
        if p_value < 0.05:
            test_result = f"{time_series} records are stationary."
        else:
            test_result = f"{time_series} records are not stationary."
        return test_result, p_value

    def data_acf_pacf_analysis(self, data_set, time_series):
        # ACF and PACF - Time series data
        ## For GARCH Models use ACF to determine the ARCH order and PACF for the order of the lagged conditional varinaces
        # ACF plot
        fig, ax = plt.subplots(figsize=(10, 5))
        sgt.plot_acf(
            data_set[time_series].dropna(),
            ax=ax,
            zero=False,
            lags=40,
            color="var(--primary-color)",
            vlines_kwargs={"colors": "black"},
        )
        plt.title(f"ACF of {time_series}", size=20)
        ax.set_facecolor("white")
        ax.xaxis.label.set_size(15)
        plt.xticks(fontsize=13)
        plt.yticks(fontsize=13)
        figfile = BytesIO()
        plt.savefig(figfile, format="png", bbox_inches="tight", pad_inches=0.35)
        plt.close()
        figfile.seek(0)
        figdata_png = figfile.getvalue()
        figdata_png = base64.b64encode(figdata_png)
        acf_result = figdata_png.decode("utf8")
        # PACF plot
        fig, ax = plt.subplots(figsize=(10, 5))
        sgt.plot_pacf(
            data_set[time_series].dropna(),
            ax=ax,
            zero=False,
            lags=40,
            color="var(--primary-color)",
            vlines_kwargs={"colors": "black"},
        )
        plt.title(f"PACF of {time_series}", size=20)
        ax.set_facecolor("white")
        ax.xaxis.label.set_size(15)
        plt.xticks(fontsize=13)
        plt.yticks(fontsize=13)
        figfile = BytesIO()
        plt.savefig(figfile, format="png", bbox_inches="tight", pad_inches=0.35)
        plt.close()
        figfile.seek(0)
        figdata_png = figfile.getvalue()
        figdata_png = base64.b64encode(figdata_png)
        pacf_result = figdata_png.decode("utf8")
        return acf_result, pacf_result

    def ARIMA(self, time_series_data, p, d, q):
        ts_model_arima = ARIMA(time_series_data.dropna(), order=(p, d, q))
        results_arima_model = ts_model_arima.fit()
        ## Summary of the model
        summary = results_arima_model.summary().as_html()
        time_series_data["residuals"] = results_arima_model.resid
        return results_arima_model, summary, time_series_data

    def Diagnostic_Checks(self, residuals, p, d, q):
        # Plot of residuals
        fig, ax = plt.subplots(figsize=(10, 5))
        residuals.plot(ax=ax, color="var(--primary-color)")
        plt.title(f"Residuals", size=20)
        ax.set_facecolor("white")
        ax.xaxis.label.set_size(15)
        plt.xticks(fontsize=13)
        plt.yticks(fontsize=13)
        figfile = BytesIO()
        plt.savefig(figfile, format="png", bbox_inches="tight", pad_inches=0.35)
        plt.close()
        figfile.seek(0)
        figdata_png = figfile.getvalue()
        figdata_png = base64.b64encode(figdata_png)
        residuals_plot = figdata_png.decode("utf8")
        # ACF of residuals
        fig, ax = plt.subplots(figsize=(10, 5))
        sgt.plot_acf(
            residuals.dropna(),
            ax=ax,
            zero=False,
            lags=40,
            color="var(--primary-color)",
            vlines_kwargs={"colors": "black"},
        )
        plt.title(f"ACF of Residuals for ARIMA ({p},{d},{q})", size=20)
        ax.set_facecolor("white")
        ax.xaxis.label.set_size(15)
        plt.xticks(fontsize=13)
        plt.yticks(fontsize=13)
        figfile = BytesIO()
        plt.savefig(figfile, format="png", bbox_inches="tight", pad_inches=0.35)
        plt.close()
        figfile.seek(0)
        figdata_png = figfile.getvalue()
        figdata_png = base64.b64encode(figdata_png)
        acf_result = figdata_png.decode("utf8")
        # ADF Test of Stationarity - Residuals
        adf_p_value = sts.adfuller(residuals.dropna())[1]
        if adf_p_value < 0.05:
            adf_test_result = "Residuals are stationary."
        else:
            adf_test_result = "Residuals are not stationary."
        # Jarque-Bera Test - To determine if the residuals are normally distributed
        mean = residuals.mean()
        std = residuals.std()
        jb_p_value = jarque_bera(residuals.dropna(), axis=0)[1]
        if jb_p_value >= 0.05:
            jb_test_result = "Residuals are normally distributed."
        else:
            jb_test_result = "Residuals are not normally distributed."
        return residuals_plot, acf_result, adf_p_value, adf_test_result, mean, std, jb_p_value, jb_test_result

    def ARIMA_Evaluate_Performance(self, model_results, data_set_train, data_set_test, arima_order, method):
        test = data_set_test.iloc[:, 0].tolist()
        if method == "Simple Forecast":
            ## Simple Forecast Method
            if arima_order[1] > 0:
                # When the model is integrated i.e. d > 0.
                predictions = (
                    model_results.predict(
                        start=data_set_test.index[0], end=data_set_test.index[-1], typ="levels"
                    )
                ).tolist()
            else:
                predictions = (
                    model_results.predict(start=data_set_test.index[0], end=data_set_test.index[-1])
                ).tolist()

        if method == "Rolling Forecast":
            ## Rolling Forecast Method
            history = data_set_train.iloc[:, 0].tolist()
            # make predictions
            predictions = []
            for t in range(len(test)):
                model = ARIMA(history, order=arima_order)
                model_fit = model.fit(disp=0)
                yhat = model_fit.forecast()[0]
                predictions.append(yhat[0])
                history.append(test[t])
        # Calculate out of sample error
        mse = mean_squared_error(test, predictions)
        # Actual vs Predicted- Table
        predicted_vs_actual_table = {
            f"{data_set_test.index.name}": data_set_test.index.strftime("%Y-%m-%d").tolist(),
            "Actual": test,
            "Predicted": predictions,
        }
        predicted_vs_actual_table = pd.DataFrame(predicted_vs_actual_table)
        predicted_vs_actual_table["Actual"] = predicted_vs_actual_table["Actual"].round(4)
        predicted_vs_actual_table["Predicted"] = predicted_vs_actual_table["Predicted"].round(4)
        predicted_vs_actual_table = predicted_vs_actual_table.to_dict("list")
        # Actual vs Predicted - Plot
        fig, ax = plt.subplots(figsize=(10, 5))
        plt.plot(test, color="black", label="Actual")
        plt.plot(predictions, color="var(--primary-color)", label="Predicted")
        plt.title("Actual vs Predicted", size=20)
        plt.legend(loc="upper right")
        ax.set_facecolor("white")
        ax.xaxis.label.set_size(15)
        plt.xticks(fontsize=13)
        plt.yticks(fontsize=13)
        figfile = BytesIO()
        plt.savefig(figfile, format="png", bbox_inches="tight", pad_inches=0.35)
        plt.close()
        figfile.seek(0)
        figdata_png = figfile.getvalue()
        figdata_png = base64.b64encode(figdata_png)
        predicted_vs_actual_plot = figdata_png.decode("utf8")
        return mse, predicted_vs_actual_table, predicted_vs_actual_plot

    def ARIMA_Forecasting(self, order, method, data_set, steps=1):
        frequency = pd.infer_freq(data_set.index, warn=True)
        if method == "Simple Forecast":
            ## Simple Forecast Method
            ts_model_arima = ARIMA(data_set.dropna(), order=order)
            model_results = ts_model_arima.fit()
            forecasted_values = pd.Series(
                model_results.forecast(steps=steps)[0],
                name=data_set.iloc[:, 0].name + " - Forecasts",
                index=pd.date_range(data_set.index[-1], freq=frequency, periods=steps + 1)[1:],
            )
            forecasted_values.index.name = data_set.index.name
        if method == "Rolling Forecast":
            ## Rolling Forecast Method
            history = data_set.iloc[:, 0].dropna().tolist()
            # make predictions
            predictions = []
            for t in range(steps):
                model = ARIMA(history, order=order)
                model_fit = model.fit(disp=0)
                yhat = model_fit.forecast()[0]
                predictions.append(yhat[0])
                history.append(yhat)
            forecasted_values = pd.Series(
                predictions,
                name=data_set.iloc[:, 0].name + " - Forecasts",
                index=pd.date_range(data_set.index[-1], freq=frequency, periods=steps + 1)[1:],
            )
            forecasted_values.index.name = data_set.index.name
        ## Plot of predicted values
        fig, ax = plt.subplots(figsize=(10, 5))
        forecasted_values.plot(ax=ax, color="var(--primary-color)", label="Forecasts")
        plt.title(f"Forecasts for {steps} Period/s Ahead", fontsize="20")
        ax.set_facecolor("white")
        ax.xaxis.label.set_size(15)
        plt.xticks(fontsize=13)
        plt.yticks(fontsize=13)
        plt.legend(loc="upper right", prop={"size": 15})
        figfile = BytesIO()
        plt.savefig(figfile, format="png", bbox_inches="tight", pad_inches=0.35)
        plt.close()
        figfile.seek(0)
        figdata_png = figfile.getvalue()
        figdata_png = base64.b64encode(figdata_png)
        forecasts_plot = figdata_png.decode("utf8")
        return forecasted_values, forecasts_plot

    def GARCH(self, data_set, data_set_test, p, q, mean_model, lags=0):
        ## Model Fitting
        ts_model_garch = arch_model(
            data_set.iloc[:, 0].dropna(), mean=mean_model, lags=lags, vol="GARCH", p=p, q=q
        )
        res_garch = ts_model_garch.fit(update_freq=5, last_obs=data_set_test.index[0])
        ## Model Summary
        summary = res_garch.summary().as_html()
        data_set["standardised_residuals"] = res_garch.std_resid
        data_set["conditional_volatility"] = res_garch.conditional_volatility
        return res_garch, summary, data_set

    def GARCH_Diagnostic_Checks(self, res_garch, residuals, conditional_volatility, p, q):
        # Plot of standardised residuals
        fig, ax = plt.subplots(figsize=(10, 5))
        residuals.plot(ax=ax, color="var(--primary-color)")
        plt.title(f"Standardised Residuals", size=20)
        ax.set_facecolor("white")
        ax.xaxis.label.set_size(15)
        plt.xticks(fontsize=13)
        plt.yticks(fontsize=13)
        figfile = BytesIO()
        plt.savefig(figfile, format="png", bbox_inches="tight", pad_inches=0.35)
        plt.close()
        figfile.seek(0)
        figdata_png = figfile.getvalue()
        figdata_png = base64.b64encode(figdata_png)
        residuals_plot = figdata_png.decode("utf8")
        # ACF of standardised residuals
        fig, ax = plt.subplots(figsize=(10, 5))
        sgt.plot_acf(
            residuals.dropna(),
            ax=ax,
            zero=False,
            lags=40,
            color="var(--primary-color)",
            vlines_kwargs={"colors": "black"},
        )
        plt.title(f"ACF of Standardised Residuals for GARCH ({p},{q})", size=20)
        ax.set_facecolor("white")
        ax.xaxis.label.set_size(15)
        plt.xticks(fontsize=13)
        plt.yticks(fontsize=13)
        figfile = BytesIO()
        plt.savefig(figfile, format="png", bbox_inches="tight", pad_inches=0.35)
        plt.close()
        figfile.seek(0)
        figdata_png = figfile.getvalue()
        figdata_png = base64.b64encode(figdata_png)
        acf_result = figdata_png.decode("utf8")
        # Plot of conditional volatility
        fig, ax = plt.subplots(figsize=(10, 5))
        conditional_volatility.plot(ax=ax, color="var(--primary-color)")
        plt.title(f"Conditional Volatility", size=20)
        ax.set_facecolor("white")
        ax.xaxis.label.set_size(15)
        plt.xticks(fontsize=13)
        plt.yticks(fontsize=13)
        figfile = BytesIO()
        plt.savefig(figfile, format="png", bbox_inches="tight", pad_inches=0.35)
        plt.close()
        figfile.seek(0)
        figdata_png = figfile.getvalue()
        figdata_png = base64.b64encode(figdata_png)
        conditional_volatility_plot = figdata_png.decode("utf8")
        # ADF Test of Stationarity - Residuals
        adf_p_value = sts.adfuller(residuals.dropna())[1]
        if adf_p_value < 0.05:
            adf_test_result = "Standardised residuals are stationary."
        else:
            adf_test_result = "Standardised residuals are not stationary."
        # Jarque-Bera Test - To determine if the residuals are normally distributed
        mean = residuals.mean()
        std = residuals.std()
        jb_p_value = jarque_bera(residuals.dropna(), axis=0)[1]
        if jb_p_value >= 0.05:
            jb_test_result = "Standardised residuals are normally distributed."
        else:
            jb_test_result = "Standardised residuals are not normally distributed."
        return (
            residuals_plot,
            conditional_volatility_plot,
            acf_result,
            adf_p_value,
            adf_test_result,
            mean,
            std,
            jb_p_value,
            jb_test_result,
        )

    def GARCH_Evaluate_Performance(self, res_garch, data_set, data_set_test):
        ## Model Forecasting and Comparison with the Test Data Set
        pred_garch = res_garch.forecast(horizon=1, align="target")
        predicted_vs_actual = pd.DataFrame(index=data_set_test.index)
        predicted_vs_actual[f"{data_set.columns[0]} - Squared"] = data_set_test.iloc[:, 0] ** 2
        predicted_vs_actual["Predicted Volatility"] = pred_garch.residual_variance[data_set_test.index[0] :]
        ## Results
        fig, ax = plt.subplots(figsize=(10, 5))
        predicted_vs_actual["Predicted Volatility"].plot(ax=ax, color="black", zorder=2)
        predicted_vs_actual[f"{data_set.columns[0]} - Squared"].plot(
            ax=ax, color="var(--primary-color)", zorder=1
        )
        plt.title("Volatility Comparison", size=15)
        ax.set_facecolor("white")
        ax.xaxis.label.set_size(15)
        plt.xticks(fontsize=13)
        plt.yticks(fontsize=13)
        plt.legend(loc="upper right")
        figfile = BytesIO()
        plt.savefig(figfile, format="png", bbox_inches="tight", pad_inches=0.35)
        plt.close()
        figfile.seek(0)
        figdata_png = figfile.getvalue()
        figdata_png = base64.b64encode(figdata_png)
        predicted_vs_actual_plot = figdata_png.decode("utf8")
        return predicted_vs_actual, predicted_vs_actual_plot

    def GARCH_Volatility_Predictions(
        self, data_set, data_set_test, mean_model, p, q, no_of_steps_ahead, lags=0
    ):
        ## Model Fitting
        frequency = pd.infer_freq(data_set.index, warn=True)
        mod_garch = arch_model(
            data_set.iloc[:, 0].dropna(), mean=mean_model, lags=lags, vol="GARCH", p=p, q=q
        )
        res_garch = mod_garch.fit(last_obs=data_set_test.index[0])
        ## Model Forecasting
        forecasted_values = pd.Series(
            res_garch.forecast(horizon=no_of_steps_ahead, align="target")
            .residual_variance[-1:]
            .iloc[0]
            .tolist(),
            name=data_set.iloc[:, 0].name + " - Volatility Predictions",
            index=pd.date_range(data_set_test.index[-1], freq=frequency, periods=no_of_steps_ahead + 1)[1:],
        )
        forecasted_values.index.name = data_set.index.name
        ## Results
        fig, ax = plt.subplots(figsize=(10, 5))
        forecasted_values.plot(ax=ax, color="var(--primary-color)", label="Volatility")
        plt.title("Volatility Predictions", size=15)
        ax.set_facecolor("white")
        ax.xaxis.label.set_size(15)
        plt.xticks(fontsize=13)
        plt.yticks(fontsize=13)
        plt.legend(loc="upper right", prop={"size": 15})
        figfile = BytesIO()
        plt.savefig(figfile, format="png", bbox_inches="tight", pad_inches=0.35)
        plt.close()
        figfile.seek(0)
        figdata_png = figfile.getvalue()
        figdata_png = base64.b64encode(figdata_png)
        forecasts_plot = figdata_png.decode("utf8")
        return forecasted_values, forecasts_plot

    def Ljung_and_Box_Test(self, residuals, p, q):
        # Ljung and Box Test - To determine if the residuals form a white noise process
        p_values = acorr_ljungbox(residuals, lags=100)[1]
        return p_values

    def ARIMA_Model_Comparison(self, model_1, order_model_1, model_2, order_model_2):
        ## LLR Test - Goodness of fit test
        # LLR Test only works if the models are nested - Model 1 is nested in model 2 if it satisfies the following criteria
        p_1 = order_model_1[0]
        q_1 = order_model_1[2]
        p_2 = order_model_2[0]
        q_2 = order_model_2[2]
        llr_test_result = ""
        llr_p_value = ""
        comparison_outcome = ""
        if sum([p_2, q_2]) >= sum([p_1, q_1]):
            if p_2 >= p_1:
                if q_2 >= q_1:
                    degrees_of_freedom = sum([p_2, q_2]) - sum([p_1, q_1])
                    llr_p_value = LLR_Test_ARIMA(model_1, model_2, DF=degrees_of_freedom)
                    if llr_p_value >= 0.05:
                        llr_test_result = f"ARIMA {order_model_1} is a better fit than ARIMA {order_model_2}."
                    else:
                        llr_test_result = f"ARIMA {order_model_2} is a better fit than ARIMA {order_model_1}."

        ## AIC - Akaike Information Criterion
        aic_model_1 = model_1.aic
        aic_model_2 = model_2.aic
        aic_result1 = f"AIC of ARIMA {order_model_1} = " + str(aic_model_1)
        aic_result2 = f"AIC of ARIMA {order_model_2} = " + str(aic_model_2)

        ## BIC - Bayesian Information Criterion
        bic_model_1 = model_1.bic
        bic_model_2 = model_2.bic
        bic_result1 = f"BIC of ARIMA {order_model_1} = " + str(bic_model_1)
        bic_result2 = f"BIC of ARIMA {order_model_2} = " + str(bic_model_2)

        ## Log Likelihood
        llf_model_1 = model_1.llf
        llf_model_2 = model_2.llf
        llf_result1 = f"Log Likelihood of ARIMA {order_model_1} = " + str(llf_model_1)
        llf_result2 = f"Log Likelihood of ARIMA {order_model_2} = " + str(llf_model_2)

        if aic_model_1 < aic_model_2 and bic_model_1 < bic_model_2 and llf_model_1 > llf_model_2:
            comparison_outcome = f"ARIMA {order_model_1} is a better fit than ARIMA {order_model_2}."
        if aic_model_2 < aic_model_1 and bic_model_2 < bic_model_1 and llf_model_2 > llf_model_1:
            comparison_outcome = f"ARIMA {order_model_2} is a better fit than ARIMA {order_model_1}."

        return (
            llr_test_result,
            aic_result1,
            aic_result2,
            bic_result1,
            bic_result2,
            llf_result1,
            llf_result2,
            comparison_outcome,
        )

    def GARCH_Model_Comparison(self, model_1, order_model_1, model_2, order_model_2):
        ## LLR Test - Goodness of fit test
        # LLR Test only works if the models are nested - Model 1 is nested in model 2 if it satisfies the following criteria
        p_1 = order_model_1[0]
        q_1 = order_model_1[1]
        p_2 = order_model_2[0]
        q_2 = order_model_2[1]
        llr_test_result = ""
        llr_p_value = ""
        comparison_outcome = ""
        if sum([p_2, q_2]) >= sum([p_1, q_1]):
            if p_2 >= p_1:
                if q_2 >= q_1:
                    degrees_of_freedom = sum([p_2, q_2]) - sum([p_1, q_1])
                    llr_p_value = LLR_Test_GARCH(model_1, model_2, DF=degrees_of_freedom)
                    if llr_p_value >= 0.05:
                        llr_test_result = f"GARCH {order_model_1} is a better fit than GARCH {order_model_2}."
                    else:
                        llr_test_result = f"GARCH {order_model_2} is a better fit than GARCH {order_model_1}."

        ## AIC - Akaike Information Criterion
        aic_model_1 = model_1.aic
        aic_model_2 = model_2.aic
        aic_result1 = f"AIC of GARCH {order_model_1} = " + str(aic_model_1)
        aic_result2 = f"AIC of GARCH {order_model_2} = " + str(aic_model_2)

        ## BIC - Bayesian Information Criterion
        bic_model_1 = model_1.bic
        bic_model_2 = model_2.bic
        bic_result1 = f"BIC of GARCH {order_model_1} = " + str(bic_model_1)
        bic_result2 = f"BIC of GARCH {order_model_2} = " + str(bic_model_2)

        ## Log Likelihood
        llf_model_1 = model_1.loglikelihood
        llf_model_2 = model_2.loglikelihood
        llf_result1 = f"Log Likelihood of GARCH {order_model_1} = " + str(llf_model_1)
        llf_result2 = f"Log Likelihood of GARCH {order_model_2} = " + str(llf_model_2)

        if aic_model_1 < aic_model_2 and bic_model_1 < bic_model_2 and llf_model_1 > llf_model_2:
            comparison_outcome = f"GARCH {order_model_1} is a better fit than GARCH {order_model_2}."
        if aic_model_2 < aic_model_1 and bic_model_2 < bic_model_1 and llf_model_2 > llf_model_1:
            comparison_outcome = f"GARCH {order_model_2} is a better fit than GARCH {order_model_1}."
        return (
            llr_test_result,
            aic_result1,
            aic_result2,
            bic_result1,
            bic_result2,
            llf_result1,
            llf_result2,
            comparison_outcome,
        )

    def EWMA_HW(self, time_series_data, trend, seasonal, seasonal_periods):
        ts_model_ewma_hw = ExponentialSmoothing(
            time_series_data, trend=trend, seasonal=seasonal, seasonal_periods=seasonal_periods
        )
        results_model_ewma_hw = ts_model_ewma_hw.fit()
        summary = results_model_ewma_hw.summary().as_html()
        time_series_data["residuals"] = results_model_ewma_hw.resid
        return results_model_ewma_hw, summary, time_series_data

    # EWMA Eval
    def EWMA_HW_Evaluate_Performance(
        self, model_results, data_set_train, data_set_test, method, seasonal, seasonal_periods, trend
    ):
        test_data = data_set_test.iloc[:, 0].tolist()
        steps = len(data_set_test)
        if method == "Simple Forecast":
            ## Simple Forecast Method
            test_predictions = (model_results.forecast(steps=steps)).tolist()
        if method == "Rolling Forecast":
            ## Rolling Forecast Method
            history = data_set_train.iloc[:, 0].tolist()
            # make predictions
            test_predictions = []
            for t in range(len(test_data)):
                model = ExponentialSmoothing(
                    history, trend=trend, seasonal=seasonal, seasonal_periods=seasonal_periods
                )
                model_fit = model.fit()
                yhat = model_fit.forecast()[0]
                test_predictions.append(yhat)
                history.append(test_data[t])
        # Calculate out of sample error
        mse = mean_squared_error(test_data, test_predictions)
        # Actual vs Predicted- Table
        predicted_vs_actual_table = {
            f"{data_set_test.index.name}": data_set_test.index.strftime("%Y-%m-%d").tolist(),
            "Actual": test_data,
            "Predicted": test_predictions,
        }
        predicted_vs_actual_table = pd.DataFrame(predicted_vs_actual_table)
        predicted_vs_actual_table["Actual"] = predicted_vs_actual_table["Actual"].round(4)
        predicted_vs_actual_table["Predicted"] = predicted_vs_actual_table["Predicted"].round(4)
        predicted_vs_actual_table = predicted_vs_actual_table.to_dict("list")
        # Actual vs Predicted - Plot
        fig, ax = plt.subplots(figsize=(10, 5))
        plt.plot(test_data, color="black", label="Actual")
        plt.plot(test_predictions, color="var(--primary-color)", label="Predicted")
        plt.title("Actual vs Predicted", size=20)
        plt.legend(loc="upper right")
        ax.set_facecolor("white")
        ax.xaxis.label.set_size(15)
        plt.xticks(fontsize=13)
        plt.yticks(fontsize=13)
        figfile = BytesIO()
        plt.savefig(figfile, format="png", bbox_inches="tight", pad_inches=0.35)
        plt.close()
        figfile.seek(0)
        figdata_png = figfile.getvalue()
        figdata_png = base64.b64encode(figdata_png)
        predicted_vs_actual_plot = figdata_png.decode("utf8")
        return mse, predicted_vs_actual_table, predicted_vs_actual_plot

    # EWMA forecasting
    def EWMA_HW_Forecasting(
        self, data_set, time_series, frequency, seasonal, seasonal_periods, trend, span, steps=1
    ):
        ts_model_ewma_hw = ExponentialSmoothing(
            data_set.dropna(), trend=trend, seasonal=seasonal, seasonal_periods=seasonal_periods
        )
        model_results = ts_model_ewma_hw.fit()
        forecasted_values = pd.Series(
            model_results.forecast(steps=steps)[0],
            name=data_set.iloc[:, 0].name + " - Forecasts",
            index=pd.date_range(data_set.index[-1], freq=frequency, periods=steps + 1)[1:],
        )
        forecasted_values.index.name = data_set.index.Name
        ## Plot of predicted values
        fig, ax = plt.subplots(figsize=(10, 5))
        forecasted_values.plot(ax=ax, color="var(--primary-color)", label="Forecasts")
        plt.title(f"Forecasts for {steps} Period/s Ahead", fontsize="20")
        ax.set_facecolor("white")
        ax.xaxis.label.set_size(15)
        plt.xticks(fontsize=13)
        plt.yticks(fontsize=13)
        plt.legend(loc="upper right", prop={"size": 15})
        figfile = BytesIO()
        plt.savefig(figfile, format="png", bbox_inches="tight", pad_inches=0.35)
        plt.close()
        figfile.seek(0)
        figdata_png = figfile.getvalue()
        figdata_png = base64.b64encode(figdata_png)
        forecasts_plot = figdata_png.decode("utf8")
        return forecasted_values, forecasts_plot

    def EWMA_Diagnostic_Checks(self, residuals):
        # Plot of standardised residuals
        fig, ax = plt.subplots(figsize=(10, 5))
        residuals.plot(ax=ax, color="var(--primary-color)")
        plt.title(f"Residuals", size=20)
        ax.set_facecolor("white")
        ax.xaxis.label.set_size(15)
        plt.xticks(fontsize=13)
        plt.yticks(fontsize=13)
        figfile = BytesIO()
        plt.savefig(figfile, format="png", bbox_inches="tight", pad_inches=0.35)
        plt.close()
        figfile.seek(0)
        figdata_png = figfile.getvalue()
        figdata_png = base64.b64encode(figdata_png)
        residuals_plot = figdata_png.decode("utf8")
        # ACF of standardised residuals
        fig, ax = plt.subplots(figsize=(10, 5))
        sgt.plot_acf(
            residuals.dropna(),
            ax=ax,
            zero=False,
            lags=40,
            color="var(--primary-color)",
            vlines_kwargs={"colors": "black"},
        )
        plt.title(f"ACF of Residuals for EWMA", size=20)
        ax.set_facecolor("white")
        ax.xaxis.label.set_size(15)
        plt.xticks(fontsize=13)
        plt.yticks(fontsize=13)
        figfile = BytesIO()
        plt.savefig(figfile, format="png", bbox_inches="tight", pad_inches=0.35)
        plt.close()
        figfile.seek(0)
        figdata_png = figfile.getvalue()
        figdata_png = base64.b64encode(figdata_png)
        acf_result = figdata_png.decode("utf8")
        # ADF Test of Stationarity - Residuals
        adf_p_value = sts.adfuller(residuals.dropna())[1]
        if adf_p_value < 0.05:
            adf_test_result = "Residuals are stationary."
        else:
            adf_test_result = "Residuals are not stationary."
        # Jarque-Bera Test - To determine if the residuals are normally distributed
        mean = residuals.mean()
        std = residuals.std()
        jb_p_value = jarque_bera(residuals.dropna(), axis=0)[1]
        if jb_p_value >= 0.05:
            jb_test_result = "Residuals are normally distributed."
        else:
            jb_test_result = "Residuals are not normally distributed."
        return (
            residuals_plot,
            acf_result,
            adf_p_value,
            adf_test_result,
            mean,
            std,
            jb_p_value,
            jb_test_result,
        )


## Reads the input json and runs the model
def TS_Master_Function(config_dict, data_set, extra_argument=None):
    ts_base = Time_Series_Models()

    if config_dict["function"] == "Analyse Time Series Data":
        date_index = config_dict["inputs"]["Date_Index"]
        time_series = config_dict["inputs"]["Time_Series"]
        frequency = config_dict["inputs"]["Frequency"]
        # Setting the index
        data_set[date_index] = pd.to_datetime(data_set[date_index], dayfirst=True)
        data_set.set_index(date_index, inplace=True)
        # Setting the frequency of observations
        data_set = data_set.asfreq(frequency)
        # Filling missing values using front fill method (taking previous day's value) and removing extra columns
        data_set = data_set.fillna(method="ffill")
        data_set.drop(data_set.columns.difference([time_series]), 1, inplace=True)
        # Analysing the data
        stationarity_test_result, p_value = ts_base.data_stationarity_test(data_set, time_series)
        acf_result, pacf_result = ts_base.data_acf_pacf_analysis(data_set, time_series)
        return data_set, stationarity_test_result, p_value, acf_result, pacf_result

    if config_dict["function"] == "Train an ARIMA Model":
        ## Model Fitting
        p = config_dict["inputs"]["AR"]
        d = config_dict["inputs"]["I"]
        q = config_dict["inputs"]["MA"]
        train_percentage = config_dict["inputs"]["train_percentage"] / 100
        ### Train - Test Split
        if isinstance(data_set, dict):
            data_set = pd.DataFrame(data_set["element_data"])
            data_set = data_set.set_index(data_set.columns[0])
        size = int(len(data_set) * float(train_percentage))
        data_set_train = data_set.iloc[:size]
        data_set_test = data_set.iloc[size:]
        results_arima_model, summary, time_series_data = ts_base.ARIMA(data_set_train, p, d, q)
        # Residual Analysis
        residuals = time_series_data["residuals"]
        (
            residuals_plot,
            acf_result,
            adf_p_value,
            adf_test_result,
            mean,
            std,
            jb_p_value,
            jb_test_result,
        ) = ts_base.Diagnostic_Checks(residuals, p, d, q)
        # Model Performance
        forecasting_method = config_dict["inputs"]["forecasting_method"]
        arima_order = (p, d, q)
        frequency = pd.infer_freq(data_set.index, warn=True)
        ts_model_arima = ARIMA(data_set.dropna(), order=arima_order)
        model_results_all_data = ts_model_arima.fit()
        ts_column_name = data_set.iloc[:, 0].name
        last_date = data_set.index[-1]
        index_column_name = data_set.index.name
        mse, predicted_vs_actual_table, predicted_vs_actual_plot = ts_base.ARIMA_Evaluate_Performance(
            results_arima_model, data_set_train, data_set_test, arima_order, forecasting_method
        )
        return (
            results_arima_model,
            summary,
            data_set_train,
            data_set_test,
            residuals_plot,
            acf_result,
            adf_p_value,
            adf_test_result,
            mean,
            std,
            jb_p_value,
            jb_test_result,
            mse,
            predicted_vs_actual_table,
            predicted_vs_actual_plot,
            arima_order,
            frequency,
            pickle.dumps(model_results_all_data),
            ts_column_name,
            last_date,
            index_column_name,
        )

    if config_dict["function"] == "Train a GARCH Model":
        ## Model Fitting
        p = config_dict["inputs"]["lagged_residuals_order"]
        q = config_dict["inputs"]["lagged_variance_order"]
        train_percentage = config_dict["inputs"]["train_percentage"] / 100
        if isinstance(data_set, dict):
            data_set = pd.DataFrame(data_set["element_data"])
            data_set = data_set.set_index(data_set.columns[0])
        ### Train - Test Split
        size = int(len(data_set) * float(train_percentage))
        data_set_train = data_set.iloc[:size]
        data_set_test = data_set.iloc[size:]
        mean_model = config_dict["inputs"]["Mean_model"]
        ## Model Fitting
        if len(config_dict["inputs"]["AR_Order_GARCH"]) > 0:
            lags = int(config_dict["inputs"]["AR_Order_GARCH"])
            res_garch, summary, time_series_data = ts_base.GARCH(
                data_set, data_set_test, p, q, mean_model, lags
            )
        else:
            res_garch, summary, time_series_data = ts_base.GARCH(data_set, data_set_test, p, q, mean_model)
        ## Diagnostic checks
        residuals = time_series_data.iloc[:size]["standardised_residuals"]
        conditional_volatility = time_series_data.iloc[:size]["conditional_volatility"]
        (
            residuals_plot,
            conditional_volatility_plot,
            acf_result,
            adf_p_value,
            adf_test_result,
            mean,
            std,
            jb_p_value,
            jb_test_result,
        ) = ts_base.GARCH_Diagnostic_Checks(res_garch, residuals, conditional_volatility, p, q)
        ## Model Run - To get the predictions vs actual table and plot
        predicted_vs_actual_table, predicted_vs_actual_plot = ts_base.GARCH_Evaluate_Performance(
            res_garch, data_set, data_set_test
        )
        frequency = pd.infer_freq(data_set.index, warn=True)
        ts_column_name = data_set.iloc[:, 0].name
        last_date = data_set.index[-1]
        index_column_name = data_set.index.name
        return (
            summary,
            time_series_data,
            data_set_test,
            residuals_plot,
            conditional_volatility_plot,
            acf_result,
            adf_p_value,
            adf_test_result,
            mean,
            std,
            jb_p_value,
            jb_test_result,
            predicted_vs_actual_table,
            predicted_vs_actual_plot,
            frequency,
            pickle.dumps(res_garch),
            ts_column_name,
            last_date,
            index_column_name,
        )

    # EWMA using Holt Winters enhancements
    if config_dict["function"] == "Train an EWMA Model":
        seasonal = config_dict["inputs"]["seasonal"]
        seasonal_periods = config_dict["inputs"]["seasonal_period"]
        trend = config_dict["inputs"]["trend"]
        train_percentage = config_dict["inputs"]["train_percentage"] / 100
        method = config_dict["inputs"]["forecasting_method"]

        if isinstance(data_set, dict):
            data_set = pd.DataFrame(data_set["element_data"])
            data_set = data_set.set_index(data_set.columns[0])

        size = int(len(data_set) * float(train_percentage))
        data_set_train = data_set.iloc[:size]
        data_set_test = data_set.iloc[size:]
        # Setting the index
        # Setting the frequency of observations
        # Filling missing values using front fill method (taking previous day's value) and removing extra columns
        # ### Train - Test Split
        results_model_ewma_hw, summary, time_series_data = ts_base.EWMA_HW(
            data_set_train.dropna(),
            trend,
            seasonal,
            seasonal_periods,
        )
        # Residual Analysis
        residuals = time_series_data["residuals"]
        (
            residuals_plot,
            acf_result,
            adf_p_value,
            adf_test_result,
            mean,
            std,
            jb_p_value,
            jb_test_result,
        ) = ts_base.EWMA_Diagnostic_Checks(residuals)
        # Model Performance
        forecasting_method = config_dict["inputs"]["forecasting_method"]
        frequency = pd.infer_freq(data_set.index, warn=True)
        ts_model_ewma_hw = ExponentialSmoothing(
            data_set.dropna(), trend=trend, seasonal=seasonal, seasonal_periods=seasonal_periods
        ).fit()
        ts_column_name = data_set.iloc[:, 0].name
        last_date = data_set.index[-1]
        index_column_name = data_set.index.name
        mse, predicted_vs_actual_table, predicted_vs_actual_plot = ts_base.EWMA_HW_Evaluate_Performance(
            results_model_ewma_hw,
            data_set_train,
            data_set_test,
            method,
            seasonal,
            seasonal_periods,
            trend,
        )
        return (
            results_model_ewma_hw,
            summary,
            data_set_train,
            data_set_test,
            residuals_plot,
            acf_result,
            adf_p_value,
            adf_test_result,
            mean,
            std,
            jb_p_value,
            jb_test_result,
            mse,
            predicted_vs_actual_table,
            predicted_vs_actual_plot,
            frequency,
            pickle.dumps(ts_model_ewma_hw),
            ts_column_name,
            last_date,
            index_column_name,
        )


def arima_predict(explanatory_vars, dependent_var, model, no_of_steps, model_output):
    frequency = model_output["frequency"]
    last_date = pd.to_datetime(model_output["last_date"], dayfirst=True)
    forecasted_values = pd.Series(
        model.forecast(steps=no_of_steps)[0],
        name=dependent_var + " - Forecasts",
        index=pd.date_range(last_date, freq=frequency, periods=no_of_steps + 1)[1:],
    )
    forecasted_values.index.name = explanatory_vars[0]
    forecasted_values = forecasted_values.reset_index()
    forecasted_values[dependent_var + " - Forecasts"] = forecasted_values[
        dependent_var + " - Forecasts"
    ].round(4)
    return forecasted_values


def garch_predict(explanatory_vars, dependent_var, model, no_of_steps, model_output):
    frequency = model_output["frequency"]
    last_date = pd.to_datetime(model_output["last_date"], dayfirst=True)
    forecasted_values = pd.Series(
        model.forecast(horizon=no_of_steps, align="target").residual_variance[-1:].iloc[0].tolist(),
        name=dependent_var + " - Volatility Predictions",
        index=pd.date_range(last_date, freq=frequency, periods=no_of_steps + 1)[1:],
    )
    forecasted_values.index.name = explanatory_vars[0]
    forecasted_values = forecasted_values.reset_index()
    return forecasted_values


# EWMA Holt Winters
def EWMA_predict(explanatory_vars, dependent_var, model, no_of_steps, model_output):
    frequency = model_output["frequency"]
    last_date = pd.to_datetime(model_output["last_date"], dayfirst=True)
    forecasted_values = pd.Series(
        model.forecast(steps=no_of_steps),
        name=dependent_var + " - Forecasts",
        index=pd.date_range(last_date, freq=frequency, periods=no_of_steps + 1)[1:],
    )
    forecasted_values.index.name = explanatory_vars[0]
    forecasted_values = forecasted_values.reset_index()
    forecasted_values[dependent_var + " - Forecasts"] = forecasted_values[
        dependent_var + " - Forecasts"
    ].round(4)
    return forecasted_values
