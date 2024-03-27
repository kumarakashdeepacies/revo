import base64
from io import BytesIO
import pickle

from catboost import CatBoostClassifier, CatBoostRegressor, Pool
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from seaborn import distplot
from sklearn import metrics
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, cross_val_score


class Cat_Tree:
    def __init__(self, X_train, y_train, X_test, y_test):
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test

    def grid_search(self, param_grid, option, cat):
        if option == "cat_regression":
            classifier = CatBoostRegressor(cat_features=cat)
            grid_search = GridSearchCV(
                estimator=classifier, param_grid=param_grid, scoring="neg_mean_squared_error", cv=3, verbose=3
            )
        elif option == "cat_classification":
            classifier = CatBoostClassifier(cat_features=cat)
            grid_search = GridSearchCV(
                estimator=classifier, param_grid=param_grid, scoring="accuracy", cv=10, n_jobs=-1
            )

        grid_search.fit(self.X_train, self.y_train)
        best_tree = grid_search.best_estimator_
        return best_tree

    def random_search(self, param_grid, option, cat):
        if option == "cat_regression":
            classifier = CatBoostRegressor(cat_features=cat)
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
        elif option == "cat_classification":
            classifier = CatBoostClassifier(cat_features=cat)
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

    def grid_search_parameters(self, param_grid, option, cat):
        if option == "cat_regression":
            classifier = CatBoostRegressor(cat_features=cat)
            grid_search = GridSearchCV(
                estimator=classifier, param_grid=param_grid, scoring="neg_mean_squared_error", cv=3, verbose=3
            )
        elif option == "cat_classification":
            classifier = CatBoostClassifier(cat_features=cat)
            grid_search = GridSearchCV(
                estimator=classifier, param_grid=param_grid, scoring="accuracy", cv=10, n_jobs=-1
            )

        grid_search.fit(self.X_train, self.y_train)
        best_tree = grid_search.best_params_
        best_score = abs(grid_search.best_score_)
        return best_tree, best_score

    def random_search_parameters(self, param_grid, option, cat):
        if option == "cat_regression":
            classifier = CatBoostRegressor(cat_features=cat)
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
        elif option == "cat_classification":
            classifier = CatBoostClassifier(cat_features=cat)
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
        best_score = abs(rfr_random.best_score_)

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

    def plot_the_tree(self, tree, cat, feat):
        pool = Pool(self.X_train, self.y_train, cat_features=cat, feature_names=feat)
        li = tree.plot_tree(tree_idx=0, pool=pool)
        p = li.pipe(format="png")
        figdata_png = base64.b64encode(p)
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


def setup_grid_search(parameters, option, cat):
    d = {}
    if (
        parameters["iterations_max"] != ""
        and parameters["iterations_min"] != ""
        and parameters["iterations_step"] != ""
    ):
        d["iterations"] = []
        for i in range(
            int(parameters["iterations_min"]),
            int(parameters["iterations_max"]),
            int(parameters["iterations_step"]),
        ):
            d["iterations"].append(i)
    if (
        parameters["depth_cb_max"] != ""
        and parameters["depth_cb_min"] != ""
        and parameters["depth_cb_step"] != ""
    ):
        d["depth"] = []
        for i in range(
            int(parameters["depth_cb_min"]), int(parameters["depth_cb_max"]), int(parameters["depth_cb_step"])
        ):
            d["depth"].append(i)
    if (
        parameters["max_leaves_cb_max"] != ""
        and parameters["max_leaves_cb_min"] != ""
        and parameters["max_leaves_cb_step"] != ""
    ):
        d["max_leaves"] = []
        d["grow_policy"] = ["Lossguide"]
        for i in range(
            int(parameters["max_leaves_cb_min"]),
            int(parameters["max_leaves_cb_max"]),
            int(parameters["max_leaves_cb_step"]),
        ):
            d["max_leaves"].append(i)
    if (
        parameters["border_count_max"] != ""
        and parameters["border_count_min"] != ""
        and parameters["border_count_step"] != ""
    ):
        d["border_count"] = []
        for i in range(
            int(parameters["border_count_min"]),
            int(parameters["border_count_max"]),
            int(parameters["border_count_step"]),
        ):
            d["border_count"].append(i)
    if (
        parameters["ctr_border_count_max"] != ""
        and parameters["ctr_border_count_min"] != ""
        and parameters["ctr_border_count_step"] != ""
    ):
        d["ctr_border_count"] = []
        for i in range(
            int(parameters["ctr_border_count_min"]),
            int(parameters["ctr_border_count_max"]),
            int(parameters["ctr_border_count_step"]),
        ):
            d["ctr_border_count"].append(i)

    if (
        parameters["learning_rate_cb_max"] != ""
        and parameters["learning_rate_cb_min"] != ""
        and parameters["learning_rate_cb_step"] != ""
    ):
        d["learning_rate"] = np.arange(
            float(parameters["learning_rate_cb_min"]),
            float(parameters["learning_rate_cb_max"]),
            float(parameters["learning_rate_cb_step"]),
        )
    if (
        parameters["l2_leaf_reg_max"] != ""
        and parameters["l2_leaf_reg_min"] != ""
        and parameters["l2_leaf_reg_step"] != ""
    ):
        d["l2_leaf_reg"] = np.arange(
            float(parameters["l2_leaf_reg_min"]),
            float(parameters["l2_leaf_reg_max"]),
            float(parameters["l2_leaf_reg_step"]),
        )
    if (
        parameters["subsample_cb_max"] != ""
        and parameters["subsample_cb_min"] != ""
        and parameters["subsample_cb_step"] != ""
    ):
        d["subsample"] = np.arange(
            float(parameters["subsample_cb_min"]),
            float(parameters["subsample_cb_max"]),
            float(parameters["subsample_cb_step"]),
        )

    if len(parameters["loss_function_grid"]) != 0:
        d["loss_function"] = []
        for ele in parameters["loss_function_grid"]:
            d["loss_function"].append(ele)

    return d


def in_to_out(par, option, cat):
    d = {}
    d["cat_features"] = cat

    if par["depth_cb"] != "":
        d["depth"] = int(par["depth_cb"])
    if par["max_leaves_cb"] != "":
        d["max_leaves"] = int(par["max_leaves_cb"])
        d["grow_policy"] = "Lossguide"
    if par["iterations"] != "":
        d["iterations"] = int(par["iterations"])
    if par["border_count"] != "":
        d["border_count"] = int(par["border_count"])
    if par["ctr_border_count"] != "":
        d["ctr_border_count"] = int(par["ctr_border_count"])
    if par["learning_rate_cb"] != "":
        d["learning_rate"] = float(par["learning_rate_cb"])
    if par["l2_leaf_reg"] != "":
        d["l2_leaf_reg"] = float(par["l2_leaf_reg"])
    if par["subsample_cb"] != "":
        d["subsample"] = float(par["subsample_cb"])

    if par["loss_function"] != "Chose Loss Function":
        d["loss_function"] = par["loss_function"]

    if option == "cat_classification":
        tree = CatBoostClassifier()
        tree.set_params(**d)

    elif option == "cat_regression":
        tree = CatBoostRegressor()
        tree.set_params(**d)

    return tree


def dec_tree_side(data_train, data_test, configDict):

    exp_variables = configDict["inputs"]["regressors"]
    dep_variable = configDict["inputs"]["regressand"]
    X_train = data_train[exp_variables].values
    y_train = data_train[dep_variable].values

    X = data_train[exp_variables]
    X_test = data_test[exp_variables].values
    y_test = data_test[dep_variable].values
    categ_features = np.where(X.dtypes != float)[0]

    opt = configDict["inputs"]["opt"]
    chose = configDict["inputs"]["method2"]
    if chose == "1":
        return
    else:
        par = configDict["inputs"]["parameters1"]
        parameters = setup_grid_search(par, opt, categ_features)

    d_reg = Cat_Tree(X_train, y_train, X_test, y_test)
    if configDict["inputs"]["method2"] == "2":
        params, score = d_reg.grid_search_parameters(parameters, opt, categ_features)
    elif configDict["inputs"]["method2"] == "3":
        params, score = d_reg.random_search_parameters(parameters, opt, categ_features)
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
def cat_tree_main(data_train, data_test, configDict, data_mapping=None):

    exp_variables = configDict["inputs"]["regressors"]
    dep_variable = configDict["inputs"]["regressand"]
    X_train = data_train[exp_variables].values
    y_train = data_train[dep_variable].values

    X = data_train[exp_variables]
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

    categ_features = np.where(X.dtypes != float)[0]
    feat = list(X.columns)

    opt = configDict["inputs"]["opt"]
    chose = configDict["inputs"]["method2"]
    if chose == "1":
        par = configDict["inputs"]["parameters2"]
    else:
        par = configDict["inputs"]["parameters1"]
        parameters = setup_grid_search(par, opt, categ_features)

    d_reg = Cat_Tree(X_train, y_train, X_test, y_test)

    if configDict["inputs"]["method2"] == "2":
        tree = d_reg.grid_search(parameters, opt, categ_features)
        tree.fit(X_train, y_train)
    elif configDict["inputs"]["method2"] == "3":
        tree = d_reg.random_search(parameters, opt, categ_features)
        tree.fit(X_train, y_train)
    elif configDict["inputs"]["method2"] == "1":
        tree = in_to_out(par, opt, categ_features)
    elif configDict["inputs"]["method2"] == "4":
        if opt == "cat_classification":
            tree = CatBoostClassifier(cat_features=categ_features)
            tree.fit(X_train, y_train)
        elif opt == "cat_regression":
            tree = CatBoostRegressor(cat_features=categ_features)
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
            output_dict["plot_tree"] = d_reg.plot_the_tree(tree, categ_features, feat)
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
