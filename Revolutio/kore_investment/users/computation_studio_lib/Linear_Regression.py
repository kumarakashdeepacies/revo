import base64
from io import BytesIO
import pickle

import matplotlib.pyplot as plt
import pandas as pd
from seaborn import distplot
from sklearn import metrics
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import statsmodels.api as sm
from statsmodels.stats.diagnostic import acorr_breusch_godfrey, het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.stattools import durbin_watson, jarque_bera, omni_normtest


class Linear_Reg:
    def __init__(self, X, Y, splitRatio):
        self.X = X
        self.Y = Y
        self.splitRatio = splitRatio
        self.X_train, self.X_test, self.Y_train, self.Y_test = train_test_split(
            X, Y, test_size=splitRatio, random_state=10
        )
        self.lm = LinearRegression()
        self.lm.fit(self.X_train, self.Y_train)

    def linear_reg_summary(self):
        x1 = sm.add_constant(self.X_train)
        model = sm.OLS(self.Y_train.astype(float), x1.astype(float))
        result = model.fit()
        return result.summary().as_html()

    def residuals(self):
        """
        Returns the residuals of the model
        """
        x1 = sm.add_constant(self.X_train)
        model = sm.OLS(self.Y_train, x1).fit()
        return model.resid

    def parameter_estimates(self):
        coeff = pd.DataFrame(self.lm.coef_.round(4), self.X.columns, columns=["Coefficient"])
        coeff.reset_index(inplace=True)
        coeff = coeff.to_dict("records")
        return coeff

    def intercept_estimate(self):
        interceptEstimate = round(self.lm.intercept_, 4)
        return interceptEstimate

    def coefficient_of_determination(self):
        r2_statistic = self.lm.score(self.X_train, self.Y_train).round(4)
        return r2_statistic

    def mean_abs_error(self):
        Y_pred = self.lm.predict(self.X_test)
        MAE = metrics.mean_absolute_error(self.Y_test, Y_pred)
        return round(MAE, 4)

    def mean_sq_error(self):
        Y_pred = self.lm.predict(self.X_test)
        MSE = metrics.mean_squared_error(self.Y_test, Y_pred)
        return round(MSE, 4)

    def quantile_plot(self):
        Y_pred = self.lm.predict(self.X_test)
        residuals = self.Y_test - Y_pred
        sm.qqplot(
            residuals,
            line="r",
        )
        figfile = BytesIO()
        plt.savefig(figfile, format="png")
        plt.close()
        figfile.seek(0)
        figdata_png = figfile.getvalue()
        figdata_png = base64.b64encode(figdata_png)
        resultplot = figdata_png.decode("utf8")
        return resultplot

    def actual_vs_fitted_plot(self):
        Y_pred = self.lm.predict(self.X_test)
        distplot(Y_pred, hist=False, color="var(--primary-color)", label="Predicted Values")
        distplot(self.Y_test, hist=False, color="black", label="Actual Values")
        plt.title("Actual vs Predicted Values", fontsize=16)
        plt.xlabel("Values", fontsize=12)
        plt.ylabel("Frequency", fontsize=12)
        plt.legend(loc="upper left", fontsize=13)
        figfile = BytesIO()
        plt.savefig(figfile, format="png")
        plt.close()
        figfile.seek(0)
        figdata_png = figfile.getvalue()
        figdata_png = base64.b64encode(figdata_png)
        resultplot = figdata_png.decode("utf8")
        return resultplot

    def actual_vs_fitted_data(self):
        Y_pred = self.lm.predict(self.X_test)
        output_data = pd.DataFrame(columns=["Actual", "Predicted"])
        output_data["Actual"] = self.Y_test
        output_data["Predicted"] = Y_pred
        return output_data.to_dict("records")

    # Diagnostic Checks
    def jb_test(self):
        """
        Jarque-Bera Test for Normality
        """
        residuals = self.residuals()
        null_hyp = "Residuals are normally distributed."
        alter_hyp = "Residuals are not normally distributed."
        jb_p_value = jarque_bera(residuals.dropna(), axis=0)[1]
        if jb_p_value >= 0.05:
            jb_test_result = null_hyp
        else:
            jb_test_result = alter_hyp
        return null_hyp, alter_hyp, jb_p_value, jb_test_result

    def bp_test(self):
        """
        Breusch-Pagan Test for Heteroskedasticity
        """
        residuals = self.residuals()
        null_hyp = "Residuals are Homoskedastic"
        alter_hyp = "Residuals are Heteroskedastic"
        bp_p_value = het_breuschpagan(residuals.dropna(), axis=0)[1]
        if bp_p_value >= 0.05:
            bp_test_result = null_hyp
        else:
            bp_test_result = alter_hyp
        return null_hyp, alter_hyp, bp_p_value, bp_test_result

    def dw_test(self):
        """
        Durbin-Watson Test for Auto-correlation of Residuals
        """
        residuals = self.residuals()
        null_hyp = "No autocorrelation between residuals"
        alter_hyp = "Autocorrelation between residuals"
        dw_p_value = durbin_watson(residuals.dropna(), axis=0)[1]
        if dw_p_value >= 0.05:
            dw_test_result = null_hyp
        else:
            dw_test_result = alter_hyp
        return null_hyp, alter_hyp, dw_p_value, dw_test_result

    def omnibus_test(self):
        """
        Omnibus Test for Normality of Residuals
        """
        residuals = self.residuals()
        null_hyp = "Residuals are normally distributed."
        alter_hyp = "Residuals are not normally distributed."
        omnibus_p_value = omni_normtest(residuals.dropna(), axis=0)[1]
        if omnibus_p_value >= 0.05:
            omnibus_test_result = null_hyp
        else:
            omnibus_test_result = alter_hyp
        return null_hyp, alter_hyp, omnibus_p_value, omnibus_test_result

    def bg_test(self):
        """
        Breusch-Godfrey Test for Residuals Correlation
        """
        residuals = self.residuals()
        null_hyp = "Residuals are correlated."
        alter_hyp = "Residuals are not correlated."
        bg_p_value = acorr_breusch_godfrey(residuals.dropna(), axis=0)[1]
        if bg_p_value >= 0.05:
            bg_test_result = null_hyp
        else:
            bg_test_result = alter_hyp
        return null_hyp, alter_hyp, bg_p_value, bg_test_result

    def vif(self):
        """
        Variance Inflation Factor for Multicollinearity
        """
        # VIF dataframe
        vif_data = pd.DataFrame()
        vif_data["feature"] = self.X.columns
        # calculating VIF for each feature
        vif_data["VIF"] = [variance_inflation_factor(self.X.values, i) for i in range(len(self.X.columns))]
        return vif_data


# Master Function
def linear_regression(new_data, configDict):
    X = new_data[configDict["inputs"]["regressors"]]
    Y = new_data[configDict["inputs"]["regressand"]]
    splitRatio = float(configDict["inputs"]["split_ratio"]) / 100
    lin_reg = Linear_Reg(X, Y, splitRatio)
    output_dict = {
        "explanatory_vars": configDict["inputs"]["regressors"],
        "dependent_var": configDict["inputs"]["regressand"],
    }

    for i in configDict["inputs"]["option"]:
        if i == "linear_reg_summary":
            output_dict["linear_reg_summary"] = lin_reg.linear_reg_summary()
        elif i == "parameter_estimates":
            output_dict["parameter_estimates"] = lin_reg.parameter_estimates()
        elif i == "intercept_estimate":
            output_dict["intercept_estimate"] = lin_reg.intercept_estimate()
        elif i == "coefficient_of_determination":
            output_dict["coefficient_of_determination"] = lin_reg.coefficient_of_determination()
        elif i == "mean_abs_error":
            output_dict["mean_abs_error"] = lin_reg.mean_abs_error()
        elif i == "mean_sq_error":
            output_dict["mean_sq_error"] = lin_reg.mean_sq_error()
        elif i == "quantile_plot":
            output_dict["quantile_plot"] = lin_reg.quantile_plot()
        elif i == "actual_vs_fitted_plot":
            output_dict["actual_vs_fitted_plot"] = lin_reg.actual_vs_fitted_plot()
        elif i == "actual_vs_fitted_data":
            output_dict["actual_vs_fitted_data"] = lin_reg.actual_vs_fitted_data()
        else:
            pass
    return output_dict, pickle.dumps(lin_reg.lm)


def lin_reg_predict(prediction_data, explanatory_vars, dependent_var, model):
    raw_col_uploaded_data = prediction_data.columns.tolist()
    extra_cols_data = prediction_data.copy().reindex(
        columns=[i for i in raw_col_uploaded_data if i not in explanatory_vars]
    )
    model_pred_data = prediction_data.reindex(
        columns=[i for i in raw_col_uploaded_data if i in explanatory_vars]
    )
    y_pred = model.predict(model_pred_data)
    output_data = model_pred_data.copy()
    output_data[dependent_var] = y_pred
    output_data = pd.concat([extra_cols_data, output_data], axis=1)
    return output_data
