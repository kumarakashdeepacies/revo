import base64
from io import BytesIO
import pickle

import matplotlib.pyplot as plt
import pandas as pd
from sklearn import metrics
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
from sklearn.model_selection import train_test_split
import statsmodels.api as sm


class Log_Reg:
    def __init__(self, X, Y, splitRatio):
        self.X = X
        self.Y = Y
        self.splitRatio = splitRatio
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.Y, test_size=splitRatio, random_state=0
        )
        self.lr = LogisticRegression(fit_intercept=True, C=1e12)
        self.lr.fit(self.X_train, self.y_train)

    def logit_reg_summary(self):
        x1 = sm.add_constant(self.X_train)
        reg_log = sm.Logit(self.y_train, x1)
        results_log = reg_log.fit()
        return results_log.summary2().as_html()

    def report(self):
        y_pred = self.lr.predict(self.X_test)
        result = classification_report(self.y_test, y_pred, output_dict=True)
        report_data = pd.DataFrame(result).transpose()
        report_data.reset_index(inplace=True)
        report_data.columns = [" ", "precision", "recall", "f1-score", "support"]
        for i in ["precision", "recall", "f1-score"]:
            report_data[i] = report_data[i].astype("float")
            report_data[i] = report_data[i].round(4)
        report_data.loc[2, ["f1-score", "recall", "support"]] = ""
        report_data = report_data.to_dict("records")
        return report_data

    def accuracy(self):
        y_pred = self.lr.predict(self.X_test)
        return round(metrics.accuracy_score(self.y_test, y_pred), 4)

    def precision(self):
        y_pred = self.lr.predict(self.X_test)
        return round(metrics.precision_score(self.y_test, y_pred), 4)

    def recall(self):
        y_pred = self.lr.predict(self.X_test)
        return round(metrics.recall_score(self.y_test, y_pred), 4)

    def f1_metric(self):
        y_pred = self.lr.predict(self.X_test)
        return round(metrics.f1_score(self.y_test, y_pred), 4)

    def conf_matrix(self):
        y_pred = self.lr.predict(self.X_test)
        conf_mat = pd.DataFrame(confusion_matrix(self.y_test, y_pred))
        conf_mat.columns = ["Predicted 0", "Predicted 1"]
        conf_mat = conf_mat.rename(index={0: "Actual 0", 1: "Actual 1"})
        conf_mat.reset_index(inplace=True)
        conf_mat.columns = [" ", "Predicted 0", "Predicted 1"]
        conf_matrix = conf_mat.to_dict("records")
        return conf_matrix

    def roc_curve(self):
        y_pred = self.lr.predict(self.X_test)
        logit_roc_auc = roc_auc_score(self.y_test, y_pred)
        fpr, tpr, thresholds = roc_curve(self.y_test, self.lr.predict_proba(self.X_test)[:, 1])
        plt.figure()
        plt.plot(fpr, tpr, label="Logistic Regression (area = %0.2f)" % logit_roc_auc, color="black")
        plt.plot([0, 1], [0, 1], "r--", color="var(--primary-color)")
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel("False Positive Rate")
        plt.ylabel("True Positive Rate")
        plt.title("Receiver operating characteristic")
        plt.legend(loc="lower right")
        figfile = BytesIO()
        plt.savefig(figfile, format="png")
        plt.close()
        figfile.seek(0)
        figdata_png = figfile.getvalue()
        figdata_png = base64.b64encode(figdata_png)
        resultplot = figdata_png.decode("utf8")
        return resultplot


# Master Function
def log_regression(new_data, configDict):
    X = new_data[configDict["inputs"]["regressors"]]
    Y = new_data[configDict["inputs"]["regressand"]]
    splitRatio = float(configDict["inputs"]["split_ratio"]) / 100
    l_reg = Log_Reg(X, Y, splitRatio)
    output_dict = {
        "explanatory_vars": configDict["inputs"]["regressors"],
        "dependent_var": configDict["inputs"]["regressand"],
    }
    for i in configDict["inputs"]["option"]:
        if i == "logit_reg_summary":
            output_dict["logit_reg_summary"] = l_reg.logit_reg_summary()
        elif i == "report":
            output_dict["report"] = l_reg.report()
        elif i == "accuracy":
            output_dict["accuracy"] = l_reg.accuracy()
        elif i == "precision":
            output_dict["precision"] = l_reg.precision()
        elif i == "recall":
            output_dict["recall"] = l_reg.recall()
        elif i == "f1_metric":
            output_dict["f1_metric"] = l_reg.f1_metric()
        elif i == "conf_matrix":
            output_dict["conf_matrix"] = l_reg.conf_matrix()
        elif i == "roc_curve":
            output_dict["roc_curve"] = l_reg.roc_curve()
        else:
            pass
    return output_dict, pickle.dumps(l_reg.lr)


def log_reg_predict(prediction_data, explanatory_vars, dependent_var, model):
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
