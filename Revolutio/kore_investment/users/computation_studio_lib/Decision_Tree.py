import base64
from io import BytesIO
import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from seaborn import distplot
from sklearn import metrics, tree as x
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, cross_val_score
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor


class Dec_Tree:
    def __init__(self, X_train, y_train, X_test, y_test, method):
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test

    def grid_search(self, param_grid, option):
        if option == "d_regression":
            classifier = DecisionTreeRegressor()
            grid_search = GridSearchCV(
                estimator=classifier,
                param_grid=param_grid,
                scoring="neg_mean_absolute_error",
                cv=3,
                verbose=3,
                n_jobs=-1,
            )
        elif option == "d_classification":
            classifier = DecisionTreeClassifier()
            grid_search = GridSearchCV(
                estimator=classifier, param_grid=param_grid, scoring="accuracy", cv=10, n_jobs=-1
            )
        elif option == "r_classification":
            classifier = RandomForestClassifier()
            grid_search = GridSearchCV(
                estimator=classifier, param_grid=param_grid, scoring="accuracy", cv=10, n_jobs=-1
            )
        else:
            classifier = RandomForestRegressor()
            grid_search = GridSearchCV(
                estimator=classifier,
                param_grid=param_grid,
                scoring="neg_mean_absolute_error",
                cv=3,
                verbose=3,
                n_jobs=-1,
            )

        grid_search.fit(self.X_train, self.y_train)
        best_tree = grid_search.best_estimator_
        return best_tree

    def random_search(self, param_grid, option):
        if option == "d_regression":
            classifier = DecisionTreeRegressor()
            score = "neg_mean_absolute_error"
            cv = 3
        elif option == "d_classification":
            classifier = DecisionTreeClassifier()
            score = "accuracy"
            cv = 10
        elif option == "r_classification":
            classifier = RandomForestClassifier()
            score = "accuracy"
            cv = 10
        else:
            classifier = RandomForestRegressor()
            score = "neg_mean_absolute_error"
            cv = 3
        rfr_random = RandomizedSearchCV(
            estimator=classifier,
            param_distributions=param_grid,
            n_iter=20,
            scoring=score,
            cv=cv,
            verbose=2,
            random_state=42,
            n_jobs=-1,
            return_train_score=True,
        )
        rfr_random.fit(self.X_train, self.y_train)
        return rfr_random.best_estimator_

    def grid_search_parameters(self, param_grid, option):
        if option == "d_regression":
            classifier = DecisionTreeRegressor()
            grid_search = GridSearchCV(
                estimator=classifier,
                param_grid=param_grid,
                scoring="neg_mean_absolute_error",
                cv=3,
                verbose=3,
                n_jobs=-1,
            )
        elif option == "d_classification":
            classifier = DecisionTreeClassifier()
            grid_search = GridSearchCV(
                estimator=classifier, param_grid=param_grid, scoring="accuracy", cv=10, n_jobs=-1
            )
        elif option == "r_classification":
            classifier = RandomForestClassifier()
            grid_search = GridSearchCV(
                estimator=classifier, param_grid=param_grid, scoring="accuracy", cv=10, n_jobs=-1
            )
        else:
            classifier = RandomForestRegressor()
            grid_search = GridSearchCV(
                estimator=classifier,
                param_grid=param_grid,
                scoring="neg_mean_absolute_error",
                cv=3,
                verbose=3,
                n_jobs=-1,
            )
        grid_search.fit(self.X_train, self.y_train)
        best_tree = grid_search.best_params_
        if option == "d_regression" or option == "r_regression":
            Y_pred = grid_search.predict(self.X_test)
            best_score = metrics.mean_absolute_error(self.y_test, Y_pred)
            return best_tree, abs(best_score)
        y_pred = grid_search.predict(self.X_test)
        best_score = metrics.accuracy_score(self.y_test, y_pred)
        return best_tree, best_score

    def random_search_parameters(self, param_grid, option):
        if option == "d_regression":
            classifier = DecisionTreeRegressor()
            rfr_random = RandomizedSearchCV(
                estimator=classifier,
                param_distributions=param_grid,
                n_iter=20,
                scoring="neg_mean_absolute_error",
                cv=3,
                verbose=2,
                random_state=42,
                n_jobs=-1,
                return_train_score=True,
            )
        elif option == "d_classification":
            classifier = DecisionTreeClassifier()
            rfr_random = RandomizedSearchCV(
                estimator=classifier,
                param_distributions=param_grid,
                n_iter=20,
                scoring="accuracy",
                cv=10,
                random_state=42,
                n_jobs=-1,
                return_train_score=True,
            )
        elif option == "r_classification":
            classifier = RandomForestClassifier()
            rfr_random = RandomizedSearchCV(
                estimator=classifier,
                param_distributions=param_grid,
                n_iter=20,
                scoring="accuracy",
                cv=10,
                random_state=42,
                n_jobs=-1,
                return_train_score=True,
            )
        else:
            classifier = RandomForestRegressor()
            rfr_random = RandomizedSearchCV(
                estimator=classifier,
                param_distributions=param_grid,
                n_iter=20,
                scoring="neg_mean_absolute_error",
                cv=3,
                verbose=2,
                random_state=42,
                n_jobs=-1,
                return_train_score=True,
            )
        rfr_random.fit(self.X_train, self.y_train)
        if option == "d_regression" or option == "r_regression":
            best_score = rfr_random.score(self.X_test, self.y_test)
        elif option == "d_classification" or option == "r_classification":
            y_pred = rfr_random.predict(self.X_test)
            best_score = metrics.accuracy_score(self.y_test, y_pred)

        return rfr_random.best_params_, abs(best_score)

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
        y_test = self.y_test
        conf_mat = pd.DataFrame(confusion_matrix(y_test, y_pred))
        conf_mat.index = [f"Actual - {str(i)}" for i in y_values]
        conf_mat.reset_index(inplace=True)
        conf_mat.columns = [" "] + [f"Predicted - {str(i)}" for i in y_values]
        conf_matrix = conf_mat.to_dict("records")
        return conf_matrix

    def plot_tree(self, tree, option, exp_variables, y_values):
        if option == "r_regression" or option == "r_classification":
            rf = tree
            t = rf.estimators_[0]
        else:
            t = tree

        t.fit(self.X_train, self.y_train)
        plt.figure()
        fig, ax = plt.subplots(figsize=(15, 7))
        if option in ["r_regression", "d_regression"]:
            out = x.plot_tree(
                t, filled=True, rounded=True, max_depth=5, proportion=True, feature_names=exp_variables
            )
        else:
            out = x.plot_tree(
                t,
                filled=True,
                rounded=True,
                proportion=True,
                feature_names=exp_variables,
                class_names=y_values,
            )
        for o in out:
            arrow = o.arrow_patch
            if arrow is not None:
                arrow.set_edgecolor("black")
                arrow.set_linewidth(2)
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
        fig, ax = plt.subplots(figsize=(10, 5))
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
        fig, ax = plt.subplots(figsize=(10, 5))
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
        parameters["max_depth_max"] != ""
        and parameters["max_depth_min"] != ""
        and parameters["max_depth_step"] != ""
    ):
        d["max_depth"] = []
        for i in range(
            int(parameters["max_depth_min"]),
            int(parameters["max_depth_max"]),
            int(parameters["max_depth_step"]),
        ):
            d["max_depth"].append(i)

    if (
        parameters["max_features_max"] != ""
        and parameters["max_features_min"] != ""
        and parameters["max_features_step"] != ""
    ):
        d["max_features"] = []
        for i in range(
            int(parameters["max_features_min"]),
            int(parameters["max_features_max"]),
            int(parameters["max_features_step"]),
        ):
            d["max_features"].append(i)
        if len(parameters["features"]) != 0:
            for ele in parameters["features"]:
                if ele != "blank":
                    d["max_features"].append(ele)

    else:
        if len(parameters["features"]) != 0:
            d["max_features"] = []
            for ele in parameters["features"]:
                if ele != "blank":
                    d["max_features"].append(ele)

    if option == "r_regression" or option == "r_classification":
        if (
            parameters["max_leaf_nodes_max"] != ""
            and parameters["max_leaf_nodes_min"] != ""
            and parameters["max_leaf_nodes_step"] != ""
        ):
            d["max_leaf_nodes"] = []
            for i in range(
                int(parameters["max_leaf_nodes_min"]),
                int(parameters["max_leaf_nodes_max"]),
                int(parameters["max_leaf_nodes_step"]),
            ):
                d["max_leaf_nodes"].append(i)
        if parameters["n_est_max"] != "" and parameters["n_est_min"] != "" and parameters["n_est_step"] != "":
            d["n_estimators"] = []
            for i in range(
                int(parameters["n_est_min"]), int(parameters["n_est_max"]), int(parameters["n_est_step"])
            ):
                d["n_estimators"].append(i)

        if len(parameters["bootstrap"]) != 0:
            d["bootstrap"] = []
            for ele in parameters["bootstrap"]:
                if ele == "true":
                    d["bootstrap"].append(True)
                elif ele == "false":
                    d["bootstrap"].append(False)
        if len(parameters["oob_score"]) != 0:
            d["oob_score"] = []
            for ele in parameters["oob_score"]:
                if ele == "true":
                    d["oob_score"].append(True)
                elif ele == "false":
                    d["oob_score"].append(False)

    if (
        parameters["min_samples_leaf_max"] != ""
        and parameters["min_samples_leaf_min"] != ""
        and parameters["min_samples_leaf_step"] != ""
    ):
        d["min_samples_leaf"] = np.arange(
            float(parameters["min_samples_leaf_min"]),
            float(parameters["min_samples_leaf_max"]),
            float(parameters["min_samples_leaf_step"]),
        )
    if (
        parameters["min_samples_split_max"] != ""
        and parameters["min_samples_split_min"] != ""
        and parameters["min_samples_split_step"] != ""
    ):
        d["min_samples_split"] = np.arange(
            float(parameters["min_samples_split_min"]),
            float(parameters["min_samples_split_max"]),
            float(parameters["min_samples_split_step"]),
        )
    if (
        parameters["min_impurity_decrease_max"] != ""
        and parameters["min_impurity_decrease_min"] != ""
        and parameters["min_impurity_decrease_step"] != ""
    ):
        d["min_impurity_decrease"] = np.arange(
            float(parameters["min_impurity_decrease_min"]),
            float(parameters["min_impurity_decrease_max"]),
            float(parameters["min_impurity_decrease_step"]),
        )

    if (
        parameters["min_weight_fraction_leaf_max"] != ""
        and parameters["min_weight_fraction_leaf_min"] != ""
        and parameters["min_weight_fraction_leaf_step"] != ""
    ):
        d["min_weight_fraction_leaf"] = np.arange(
            float(parameters["min_weight_fraction_leaf_min"]),
            float(parameters["min_weight_fraction_leaf_max"]),
            float(parameters["min_weight_fraction_leaf_step"]),
        )

    if len(parameters["criterion"]) != 0:
        d["criterion"] = []
        for ele in parameters["criterion"]:
            if ele == "blank":
                d["criterion"].append(None)
            else:
                d["criterion"].append(ele)

    if option != "r_regression" and option != "r_classification":
        if len(parameters["splitter"]) != 0:
            d["splitter"] = []
            for ele in parameters["splitter"]:
                if ele != "blank":
                    d["splitter"].append(ele)
    return d


def in_to_out(par, option):
    d = {}
    if par["max_depth_val"] != "":
        d["max_depth"] = int(par["max_depth_val"])

    if par["max_features"] == "auto":
        d["max_features"] = "auto"
    elif par["max_features"] == "sqrt":
        d["max_features"] = "sqrt"
    elif par["max_features"] == "log2":
        d["max_features"] = "log2"
    elif par["max_features"] != "":
        if type(par["max_features"] == int):
            d["max_features"] = int(par["max_features"])

    if option == "r_regression" or option == "r_classification":
        if par["n_est_val"] != "":
            d["n_estimators"] = int(par["n_est_val"])
        if par["max_leaf_nodes"] != "":
            d["max_leaf_nodes"] = int(par["max_leaf_nodes"])

        if par["bootstrap"] == "true":
            d["bootstrap"] = True
        elif par["bootstrap"] == "false":
            d["bootstrap"] = False

        elif par["oob_score"] == "true":
            d["oob_score"] = True
        elif par["bootstrap"] == "false":
            d["oob_score"] = False

    if par["min_samples_split_val"] != "":
        d["min_samples_split"] = float(par["min_samples_split_val"])

    if par["min_samples_leaf_val"] != "":
        d["min_samples_leaf"] = float(par["min_samples_leaf_val"])

    if par["min_weight_val"] != "":
        d["min_weight_fraction_leaf"] = float(par["min_weight_val"])

    if par["random_state_val"] != "":
        d["random_state"] = int(par["random_state_val"])

    if par["min_impurity_decrease_val"] != "":
        d["min_impurity_decrease"] = float(par["min_impurity_decrease_val"])

    if par["crit_val"] == "1":
        d["criterion"] = "gini"
    elif par["crit_val"] == "2":
        d["criterion"] = "entropy"
    elif par["crit_val"] == "3":
        d["criterion"] = "mse"
    elif par["crit_val"] == "4":
        d["criterion"] = "friedman_mse"
    elif par["crit_val"] == "5":
        d["criterion"] = "mae"
    elif par["crit_val"] == "6":
        d["criterion"] = "poisson"

    if option != "r_regression" and option != "r_classification":
        if par["split_val"] == "1":
            d["splitter"] = "best"
        elif par["split_val"] == "2":
            d["splitter"] = "random"

    if option == "d_classification":
        tree = DecisionTreeClassifier()
        tree.set_params(**d)

    elif option == "d_regression":
        tree = DecisionTreeRegressor()
        tree.set_params(**d)
    elif option == "r_classification":
        tree = RandomForestClassifier()
        tree.set_params(**d)
    elif option == "r_regression":
        tree = RandomForestRegressor()
        tree.set_params(**d)
    return tree


def dec_tree_side(data_train, data_test, configDict, data_mapping=None):
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

    d_reg = Dec_Tree(X_train, y_train, X_test, y_test, configDict["inputs"]["method2"])
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
def dec_tree_main(data_train, data_test, configDict, data_mapping=None):
    exp_variables = configDict["inputs"]["regressors"]
    dep_variable = configDict["inputs"]["regressand"]
    X_train = data_train[exp_variables].values
    y_train = data_train[dep_variable].values
    # y_map
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

    d_reg = Dec_Tree(X_train, y_train, X_test, y_test, configDict["inputs"]["method2"])

    if configDict["inputs"]["method2"] == "2":
        tree = d_reg.grid_search(parameters, opt)
    elif configDict["inputs"]["method2"] == "3":
        tree = d_reg.random_search(parameters, opt)
    elif configDict["inputs"]["method2"] == "1":
        tree = in_to_out(par, opt)
    elif configDict["inputs"]["method2"] == "4":
        if opt == "d_classification":
            tree = DecisionTreeClassifier(random_state=0)
        elif opt == "d_regression":
            tree = DecisionTreeRegressor()
            tree.fit(X_train, y_train)
        elif opt == "r_regression":
            tree = RandomForestRegressor()
        elif opt == "r_classification":
            tree = RandomForestClassifier()

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
            output_dict["plot_tree"] = d_reg.plot_tree(tree, opt, exp_variables, y_values)
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
