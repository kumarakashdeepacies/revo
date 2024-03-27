import base64
from io import BytesIO
import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from seaborn import distplot
from sklearn import metrics
from sklearn.decomposition import PCA
from sklearn.ensemble import AdaBoostClassifier, AdaBoostRegressor
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, cross_val_score
from sklearn.preprocessing import StandardScaler


class Ada_Tree:
    def __init__(self, X_train, y_train, X_test, y_test):
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test

    def grid_search(self, param_grid, option):
        if option == "ada_regression":
            classifier = AdaBoostRegressor()
            grid_search = GridSearchCV(
                estimator=classifier, param_grid=param_grid, scoring="neg_mean_squared_error", cv=3, verbose=3
            )
        elif option == "ada_classification":
            classifier = AdaBoostClassifier()
            grid_search = GridSearchCV(
                estimator=classifier, param_grid=param_grid, scoring="accuracy", cv=10, n_jobs=-1
            )

        grid_search.fit(self.X_train, self.y_train)
        best_tree = grid_search.best_estimator_
        return best_tree

    def random_search(self, param_grid, option):
        if option == "ada_regression":
            classifier = AdaBoostRegressor()
            rfr_random = RandomizedSearchCV(
                estimator=classifier,
                param_distributions=param_grid,
                n_iter=20,
                scoring="neg_mean_squared_error",
                cv=3,
                verbose=2,
                random_state=42,
                n_jobs=-1,
                return_train_score=True,
            )
        elif option == "ada_classification":
            classifier = AdaBoostClassifier()
            rfr_random = RandomizedSearchCV(
                estimator=classifier,
                param_distributions=param_grid,
                n_iter=20,
                scoring="accuracy",
                cv=3,
                verbose=2,
                random_state=42,
                n_jobs=-1,
                return_train_score=True,
            )
        rfr_random.fit(self.X_train, self.y_train)
        return rfr_random.best_estimator_

    def grid_search_parameters(self, param_grid, option):
        if option == "ada_regression":
            classifier = AdaBoostRegressor()
            grid_search = GridSearchCV(
                estimator=classifier, param_grid=param_grid, scoring="neg_mean_squared_error", cv=3, verbose=3
            )
        elif option == "ada_classification":
            classifier = AdaBoostClassifier()
            grid_search = GridSearchCV(
                estimator=classifier, param_grid=param_grid, scoring="accuracy", cv=10, n_jobs=-1
            )

        grid_search.fit(self.X_train, self.y_train)
        best_tree = grid_search.best_params_
        best_score = grid_search.best_score_
        return best_tree, best_score

    def random_search_parameters(self, param_grid, option):
        if option == "ada_regression":
            classifier = AdaBoostRegressor()
            rfr_random = RandomizedSearchCV(
                estimator=classifier,
                param_distributions=param_grid,
                n_iter=20,
                scoring="neg_mean_squared_error",
                cv=3,
                verbose=2,
                random_state=42,
                n_jobs=-1,
                return_train_score=True,
            )
        elif option == "ada_classification":
            classifier = AdaBoostClassifier()
            rfr_random = RandomizedSearchCV(
                estimator=classifier,
                param_distributions=param_grid,
                n_iter=20,
                scoring="accuracy",
                cv=3,
                verbose=2,
                random_state=42,
                n_jobs=-1,
                return_train_score=True,
            )
        rfr_random.fit(self.X_train, self.y_train)
        best_score = rfr_random.best_score_

        return rfr_random.best_params_, best_score

    def dec_reg_summary(self, tree):
        results_dec = tree.fit(self.X_train, self.y_train)
        return results_dec.summary2().as_html()

    def cross_val(self, tree):
        accuracies = cross_val_score(estimator=tree, X=self.X_train, y=self.y_train)
        return format(accuracies.mean() * 100)

    def prediction(self, pred_data, tree):
        lr = tree
        lr.fit(self.X_train, self.y_train)
        y_pred = lr.predict(pred_data)
        Y = pd.DataFrame(self.Y)
        y_col_name = Y.columns[0]
        output_data = pred_data.copy()
        output_data[f"Predicted {y_col_name}"] = y_pred
        return output_data

    def report(self, tree):
        lr = tree
        lr.fit(self.X_train, self.y_train)
        y_pred = lr.predict(self.X_test)
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

    def accuracy(self, tree):
        lr = tree
        lr.fit(self.X_train, self.y_train)
        y_pred = lr.predict(self.X_test)
        return round(metrics.accuracy_score(self.y_test, y_pred), 4)

    def precision(self, tree):
        lr = tree
        lr.fit(self.X_train, self.y_train)
        y_pred = lr.predict(self.X_test)
        return round(metrics.precision_score(self.y_test, y_pred), 4)

    def recall(self, tree):
        lr = tree
        lr.fit(self.X_train, self.y_train)
        y_pred = lr.predict(self.X_test)
        return round(metrics.recall_score(self.y_test, y_pred), 4)

    def f1_metric(self, tree):
        lr = tree
        lr.fit(self.X_train, self.y_train)
        y_pred = lr.predict(self.X_test)
        return round(metrics.f1_score(self.y_test, y_pred), 4)

    def conf_matrix(self, tree, y_values):
        lr = tree
        lr.fit(self.X_train, self.y_train)
        y_pred = lr.predict(self.X_test)
        conf_mat = pd.DataFrame(confusion_matrix(self.y_test, y_pred))
        conf_mat.index = [f"Actual - {str(i)}" for i in y_values]
        conf_mat.reset_index(inplace=True)
        conf_mat.columns = [" "] + [f"Predicted - {str(i)}" for i in y_values]
        conf_matrix = conf_mat.to_dict("records")
        return conf_matrix

    def plot_tree(self, tree):
        pca = PCA(2)
        df = pca.fit_transform(self.X_train)
        sc = StandardScaler()
        df = sc.fit_transform(df)
        min1, max1 = df[:, 0].min() - 1, df[:, 0].max() + 1
        min2, max2 = df[:, 1].min() - 1, df[:, 1].max() + 1
        x1grid = np.arange(min1, max1, 0.2)
        x2grid = np.arange(min2, max2, 0.2)

        # create all of the lines and rows of the grid

        xx, yy = np.meshgrid(x1grid, x2grid)
        r1, r2 = xx.flatten(), yy.flatten()
        r1, r2 = r1.reshape((len(r1), 1)), r2.reshape((len(r2), 1))

        # horizontal stack vectors to create x1,x2 input for the model

        grid = np.hstack((r1, r2))
        model = tree
        model.fit(df, self.y_train)
        yhat = model.predict(grid)

        # reshape the predictions back into a grid

        zz = yhat.reshape(xx.shape)
        plt.figure()

        # plot the grid of x, y and z values as a surface

        plt.contourf(xx, yy, zz, colors=["#000000", "whitesmoke", "white"], extend="both")

        # create scatter plot for samples from each class

        for class_value in range(2):
            row_ix = np.where(self.y_train == class_value)

        # create scatter of these samples

        plt.scatter(df[row_ix, 0], df[row_ix, 1], s=50, color="var(--primary-color)")
        plt.title("Decision surface")
        plt.xlabel("X1")
        plt.ylabel("X2")
        figfile = BytesIO()
        plt.savefig(figfile, format="png")
        plt.close()
        figfile.seek(0)
        figdata_png = figfile.getvalue()
        figdata_png = base64.b64encode(figdata_png)
        resultplot = figdata_png.decode("utf8")
        return resultplot

    def roc_curve(self, tree):
        lr = tree
        lr.fit(self.X_train, self.y_train)
        y_pred = lr.predict(self.X_test)
        logit_roc_auc = roc_auc_score(self.y_test, y_pred)
        fpr, tpr, thresholds = roc_curve(self.y_test, lr.predict_proba(self.X_test)[:, 1])
        plt.figure()
        plt.plot(fpr, tpr, label="Decision Tree (area = %0.2f)" % logit_roc_auc)
        plt.plot([0, 1], [0, 1], "r--")
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

    def mean_abs_error(self, tree):
        lm = tree
        lm.fit(self.X_train, self.y_train)
        Y_pred = lm.predict(self.X_test)
        MAE = metrics.mean_absolute_error(self.y_test, Y_pred)
        return round(MAE, 4)

    def coefficient_of_determination(self, tree):
        lm = tree
        model = lm.fit(self.X_train, self.y_train)
        r2_statistic = model.score(self.X_train, self.y_train).round(4)
        return r2_statistic

    def mean_sq_error(self, tree):
        lm = tree
        lm.fit(self.X_train, self.y_train)
        Y_pred = lm.predict(self.X_test)
        MSE = metrics.mean_squared_error(self.y_test, Y_pred)
        return round(MSE, 4)

    def actual_vs_fitted_plot(self, tree):
        lm = tree
        lm.fit(self.X_train, self.y_train)
        Y_pred = lm.predict(self.X_test)
        distplot(Y_pred, hist=False, color="r", label="Predicted Values")
        distplot(self.y_test, hist=False, color="b", label="Actual Values")
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

    def pred(self, tree):
        lm = tree
        lm.fit(self.X_train, self.y_train)
        Y_pred = lm.predict(self.X_test)
        ti = list(self.y_test)
        a = []
        for ele in ti:
            a.append(str(ele))
        li = list(Y_pred)
        si = []
        for x1 in li:
            si.append(str(x1))
        return si, a


def setup_grid_search(parameters, option):
    d = {}
    if (
        parameters["n_est_ab_max"] != ""
        and parameters["n_est_ab_min"] != ""
        and parameters["n_est_ab_step"] != ""
    ):
        d["n_estimators"] = []
        for i in range(
            int(parameters["n_est_ab_min"]), int(parameters["n_est_ab_max"]), int(parameters["n_est_ab_step"])
        ):
            d["n_estimators"].append(i)

    if (
        parameters["learning_rate_ab_max"] != ""
        and parameters["learning_rate_ab_min"] != ""
        and parameters["learning_rate_ab_step"] != ""
    ):
        d["learning_rate"] = np.arange(
            float(parameters["learning_rate_ab_min"]),
            float(parameters["learning_rate_ab_max"]),
            float(parameters["learning_rate_ab_step"]),
        )

    if option == "ada_classification":
        if len(parameters["algorithm_grid"]) != 0:
            d["algorithm"] = []
            for ele in parameters["algorithm_grid"]:
                d["algorithm"].append(ele)
    if option == "ada_regression":
        if len(parameters["loss_grid"]) != 0:
            d["loss"] = []
            for ele in parameters["loss_grid"]:
                d["loss"].append(ele)

    return d


def in_to_out(par, option):
    d = {}
    if par["n_est_ab"] != "":
        d["n_estimators"] = int(par["n_est_ab"])
    if par["learning_rate_ab"] != "":
        d["learning_rate"] = float(par["learning_rate_ab"])

    if option == "ada_classification":
        if par["algorithm"] == "SAMME":
            d["algorithm"] = "SAMME"
        elif par["algorithm"] == "SAMME.R":
            d["algorithm"] = "SAMME.R"

    if option == "ada_regression":
        if par["loss"] == "linear":
            d["loss"] = "linear"
        elif par["loss"] == "square":
            d["loss"] = "square"
        elif par["loss"] == "exponential":
            d["loss"] = "exponential"

    if option == "ada_classification":
        tree = AdaBoostClassifier()
        tree.set_params(**d)

    elif option == "ada_regression":
        tree = AdaBoostRegressor()
        tree.set_params(**d)

    return tree


def dec_tree_side(data_train, data_test, configDict):

    exp_variables = configDict["inputs"]["regressors"]
    dep_variable = configDict["inputs"]["regressand"]
    X_train = data_train[exp_variables].values
    y_train = data_train[dep_variable].values

    X_test = data_test[exp_variables].values
    y_test = data_test[dep_variable].values

    opt = configDict["inputs"]["opt"]
    chose = configDict["inputs"]["method2"]
    if chose == "1":
        return
    else:
        par = configDict["inputs"]["parameters1"]
        parameters = setup_grid_search(par, opt)

    d_reg = Ada_Tree(X_train, y_train, X_test, y_test)
    if configDict["inputs"]["method2"] == "2":
        params, score = d_reg.grid_search_parameters(parameters, opt)
    elif configDict["inputs"]["method2"] == "3":
        params, score = d_reg.random_search_parameters(parameters, opt)
    li = []
    si = []
    for key in params:
        li.append(key)
        si.append(params[key])
    output_dict = {
        "params": li,
        "values": si,
        "score": score,
    }
    return output_dict


# Master Function
def ada_tree_main(data_train, data_test, configDict, data_mapping=None):

    exp_variables = configDict["inputs"]["regressors"]
    dep_variable = configDict["inputs"]["regressand"]
    X_train = data_train[exp_variables].values
    y_train = data_train[dep_variable].values
    if str(data_mapping) != "None":
        y_values_raw = data_train[dep_variable].unique().tolist()
        y_values = []
        for i in y_values_raw:
            actual_value = data_mapping.loc[data_mapping["encoded_value"] == i, "actual_value"].iloc[0]
            y_values.append(actual_value)
    else:
        y_values = data_train[dep_variable].astype(str).unique().tolist()

    X_test = data_test[exp_variables].values
    y_test = data_test[dep_variable].values

    opt = configDict["inputs"]["opt"]
    chose = configDict["inputs"]["method2"]
    if chose == "1":
        par = configDict["inputs"]["parameters2"]
    else:
        par = configDict["inputs"]["parameters1"]
        parameters = setup_grid_search(par, opt)

    d_reg = Ada_Tree(X_train, y_train, X_test, y_test)

    if configDict["inputs"]["method2"] == "2":
        tree = d_reg.grid_search(parameters, opt)
    elif configDict["inputs"]["method2"] == "3":
        tree = d_reg.random_search(parameters, opt)
    elif configDict["inputs"]["method2"] == "1":
        tree = in_to_out(par, opt)
    elif configDict["inputs"]["method2"] == "4":
        if opt == "ada_classification":
            tree = AdaBoostClassifier()
            tree.fit(X_train, y_train)
        elif opt == "ada_regression":
            tree = AdaBoostRegressor()
            tree.fit(X_train, y_train)

    output_dict = {
        "data_X_train": pd.DataFrame(X_train).to_dict("records"),
        "data_y_train": pd.DataFrame(y_train).to_dict("records"),
    }

    for i in configDict["inputs"]["option"]:
        if i == "dec_reg_summary":
            output_dict["dec_reg_summary"] = d_reg.dec_reg_summary(tree)
        elif i == "cross_val":
            output_dict["cross_val"] = d_reg.cross_val(tree)
        elif i == "report":
            output_dict["report"] = d_reg.report(tree)
        elif i == "accuracy":
            output_dict["accuracy"] = d_reg.accuracy(tree)
        elif i == "precision":
            output_dict["precision"] = d_reg.precision(tree)
        elif i == "recall":
            output_dict["recall"] = d_reg.recall(tree)
        elif i == "f1_metric":
            output_dict["f1_metric"] = d_reg.f1_metric(tree)
        elif i == "conf_matrix":
            output_dict["conf_matrix"] = d_reg.conf_matrix(tree, y_values)
        elif i == "plot_tree":
            output_dict["plot_tree"] = d_reg.plot_tree(tree)
        elif i == "roc_curve":
            output_dict["roc_curve"] = d_reg.roc_curve(tree)
        elif i == "actplot":
            output_dict["actplot"] = d_reg.actual_vs_fitted_plot(tree)
            output_dict["predict"], output_dict["actual"] = d_reg.pred(tree)
        elif i == "r_square":
            output_dict["r_square"] = d_reg.coefficient_of_determination(tree)
        elif i == "m_sq_error":
            output_dict["mean_sq_error"] = d_reg.mean_sq_error(tree)
        elif i == "mean_abs_error":
            output_dict["mean_abs_error"] = d_reg.mean_abs_error(tree)
        else:
            pass
    return output_dict, pickle.dumps(tree.fit(X_train, y_train))


def cart_predict(prediction_data, explanatory_vars, dependent_var, model, target_column_data_mapper):
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
    if len(target_column_data_mapper) > 0:
        target_mapper = dict(
            zip(target_column_data_mapper["encoded_value"], target_column_data_mapper["actual_value"])
        )
        output_data[dependent_var].replace(target_mapper, inplace=True)
    return output_data
