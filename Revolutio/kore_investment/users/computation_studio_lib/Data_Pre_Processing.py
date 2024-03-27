import json
import logging

import numpy as np
import pandas as pd
import scipy.stats as st
from sklearn.model_selection import train_test_split


class Missing_values_Func:
    def fill_previous(self, data, dataframe):
        dataframe[data].ffill(inplace=True)
        return dataframe

    def fill_next(self, data, dataframe):
        dataframe[data].bfill(inplace=True)
        return dataframe

    def fill_mean(self, data, dataframe):
        dataframe[data] = dataframe[data].astype("float")
        dataframe[data].fillna(dataframe[data].mean(skipna=True), inplace=True)
        return dataframe

    def fill_mode(self, data, dataframe):
        dataframe[data].fillna(dataframe[data].mode()[0], inplace=True)
        return dataframe

    def fill_custom(self, data, dataframe, custom_value=None):
        data_type = dataframe[data].dtypes.name
        if data_type in ["int", "int64", "int32"]:
            custom_value = int(custom_value)
        elif data_type in ["float", "float32", "float64"]:
            custom_value = float(custom_value)
        elif data_type in ["datetime64[ns]"]:
            custom_value = pd.to_datetime(custom_value)
        dataframe[data].fillna(custom_value, inplace=True)
        dataframe[data].astype(data_type)
        return dataframe

    def min_max(self, data, dataframe):
        a = dataframe[data].min()
        b = dataframe[data].max()
        for i in range(len(dataframe)):
            dataframe[data][i] = (dataframe[data][i] - a) / (b - a)
        return dataframe

    def standardized(self, data, dataframe):
        a = dataframe[data].mean()
        b = dataframe[data].std()
        for i in range(len(dataframe)):
            dataframe[data][i] = (dataframe[data][i] - a) / b
        return dataframe

    def robust(self, data, dataframe):
        q3, q1 = np.percentile(dataframe[data], [75, 25])
        iqr = q3 - q1
        a = dataframe[data].median()
        for i in range(len(dataframe)):
            dataframe[data][i] = (dataframe[data][i] - a) / iqr
        return dataframe

    def CI_outlier_mean(self, data, Alpha, dataframe):
        a = st.norm.interval(alpha=(1 - Alpha), loc=dataframe[data].mean(), scale=dataframe[data].sem())
        b = dataframe[data].mean()
        lower_bound = a[0]
        upper_bound = a[1]
        outliers1 = [x for x in dataframe[data] if x <= lower_bound]
        outliers2 = [x for x in dataframe[data] if x >= upper_bound]
        dataframe.loc[dataframe[data] < lower_bound, data] = b
        dataframe.loc[dataframe[data] > upper_bound, data] = b
        sub_df = pd.DataFrame(columns=["Lower Bound", "Upper Bound", "Lower Outliers", "Upper Outliers"])
        sub_df.loc[0, "Lower Outliers"] = len(outliers1)
        sub_df.loc[0, "Upper Outliers"] = len(outliers2)
        sub_df.loc[0, "Lower Bound"] = lower_bound
        sub_df.loc[0, "Upper Bound"] = upper_bound
        return dataframe, sub_df

    def CI_outlier_mode(self, data, Alpha, dataframe):
        a = st.norm.interval(alpha=(1 - Alpha), loc=dataframe[data].mean(), scale=dataframe[data].sem())
        b = dataframe[data].mode()[0]
        lower_bound = a[0]
        upper_bound = a[1]
        outliers1 = [x for x in dataframe[data] if x <= lower_bound]
        outliers2 = [x for x in dataframe[data] if x >= upper_bound]
        dataframe.loc[dataframe[data] < lower_bound, data] = b
        dataframe.loc[dataframe[data] > upper_bound, data] = b
        sub_df = pd.DataFrame(columns=["Lower Bound", "Upper Bound", "Lower Outliers", "Upper Outliers"])
        sub_df.loc[0, "Lower Outliers"] = len(outliers1)
        sub_df.loc[0, "Upper Outliers"] = len(outliers2)
        sub_df.loc[0, "Lower Bound"] = lower_bound
        sub_df.loc[0, "Upper Bound"] = upper_bound
        return dataframe, sub_df

    def CI_outlier_bounds(self, data, Alpha, dataframe):
        a = st.norm.interval(alpha=(1 - Alpha), loc=dataframe[data].mean(), scale=dataframe[data].sem())
        lower_bound = a[0]
        upper_bound = a[1]
        outliers1 = [x for x in dataframe[data] if x <= lower_bound]
        outliers2 = [x for x in dataframe[data] if x >= upper_bound]
        dataframe.loc[dataframe[data] < lower_bound, data] = lower_bound
        dataframe.loc[dataframe[data] > upper_bound, data] = upper_bound
        sub_df = pd.DataFrame(columns=["Lower Bound", "Upper Bound", "Lower Outliers", "Upper Outliers"])
        sub_df.loc[0, "Lower Outliers"] = len(outliers1)
        sub_df.loc[0, "Upper Outliers"] = len(outliers2)
        sub_df.loc[0, "Lower Bound"] = lower_bound
        sub_df.loc[0, "Upper Bound"] = upper_bound
        return dataframe, sub_df

    def CI_outlier_custom(self, data, Alpha, custom, dataframe):
        a = st.norm.interval(alpha=(1 - Alpha), loc=dataframe[data].mean(), scale=dataframe[data].sem())
        lower_bound = a[0]
        upper_bound = a[1]
        outliers1 = [x for x in dataframe[data] if x <= lower_bound]
        outliers2 = [x for x in dataframe[data] if x >= upper_bound]
        dataframe.loc[dataframe[data] < lower_bound, data] = custom
        dataframe.loc[dataframe[data] > upper_bound, data] = custom
        sub_df = pd.DataFrame(columns=["Lower Bound", "Upper Bound", "Lower Outliers", "Upper Outliers"])
        sub_df.loc[0, "Lower Outliers"] = len(outliers1)
        sub_df.loc[0, "Upper Outliers"] = len(outliers2)
        sub_df.loc[0, "Lower Bound"] = lower_bound
        sub_df.loc[0, "Upper Bound"] = upper_bound
        return dataframe, sub_df

    def CI_outlier_remove(self, data, Alpha, dataframe):
        a = st.norm.interval(alpha=(1 - Alpha), loc=dataframe[data].mean(), scale=dataframe[data].sem())
        lower_bound = a[0]
        upper_bound = a[1]
        outliers1 = [x for x in dataframe[data] if x <= lower_bound]
        outliers2 = [x for x in dataframe[data] if x >= upper_bound]
        outliers1 = [x for x in dataframe[data] if x <= lower_bound]
        outliers2 = [x for x in dataframe[data] if x >= upper_bound]
        dataframe.loc[dataframe[data] < lower_bound, data] = np.nan
        dataframe.loc[dataframe[data] > upper_bound, data] = np.nan
        dataframe.dropna(axis=0, inplace=True)
        sub_df = pd.DataFrame(columns=["Lower Bound", "Upper Bound", "Lower Outliers", "Upper Outliers"])
        sub_df.loc[0, "Lower Outliers"] = len(outliers1)
        sub_df.loc[0, "Upper Outliers"] = len(outliers2)
        sub_df.loc[0, "Lower Bound"] = lower_bound
        sub_df.loc[0, "Upper Bound"] = upper_bound
        return dataframe, sub_df

    def z_outlier_mean(self, data, z, dataframe):
        lower_bound = dataframe[data].mean() - (z * dataframe[data].sem())
        upper_bound = dataframe[data].mean() + (z * dataframe[data].sem())
        b = dataframe[data].mean()
        outliers1 = [x for x in dataframe[data] if x <= lower_bound]
        outliers2 = [x for x in dataframe[data] if x >= upper_bound]
        dataframe.loc[dataframe[data] < lower_bound, data] = b
        dataframe.loc[dataframe[data] > upper_bound, data] = b
        sub_df = pd.DataFrame(columns=["Lower Bound", "Upper Bound", "Lower Outliers", "Upper Outliers"])
        sub_df.loc[0, "Lower Outliers"] = len(outliers1)
        sub_df.loc[0, "Upper Outliers"] = len(outliers2)
        sub_df.loc[0, "Lower Bound"] = lower_bound
        sub_df.loc[0, "Upper Bound"] = upper_bound
        return dataframe, sub_df

    def z_outlier_mode(self, data, z, dataframe):
        lower_bound = dataframe[data].mean() - (z * dataframe[data].sem())
        upper_bound = dataframe[data].mean() + (z * dataframe[data].sem())
        b = dataframe[data].mode()[0]
        outliers1 = [x for x in dataframe[data] if x <= lower_bound]
        outliers2 = [x for x in dataframe[data] if x >= upper_bound]
        dataframe.loc[dataframe[data] < lower_bound, data] = b
        dataframe.loc[dataframe[data] > upper_bound, data] = b
        sub_df = pd.DataFrame(columns=["Lower Bound", "Upper Bound", "Lower Outliers", "Upper Outliers"])
        sub_df.loc[0, "Lower Outliers"] = len(outliers1)
        sub_df.loc[0, "Upper Outliers"] = len(outliers2)
        sub_df.loc[0, "Lower Bound"] = lower_bound
        sub_df.loc[0, "Upper Bound"] = upper_bound
        return dataframe, sub_df

    def z_outlier_bounds(self, data, z, dataframe):
        lower_bound = dataframe[data].mean() - (z * dataframe[data].sem())
        upper_bound = dataframe[data].mean() + (z * dataframe[data].sem())
        outliers1 = [x for x in dataframe[data] if x <= lower_bound]
        outliers2 = [x for x in dataframe[data] if x >= upper_bound]
        dataframe.loc[dataframe[data] < lower_bound, data] = lower_bound
        dataframe.loc[dataframe[data] > upper_bound, data] = upper_bound
        sub_df = pd.DataFrame(columns=["Lower Bound", "Upper Bound", "Lower Outliers", "Upper Outliers"])
        sub_df.loc[0, "Lower Outliers"] = len(outliers1)
        sub_df.loc[0, "Upper Outliers"] = len(outliers2)
        sub_df.loc[0, "Lower Bound"] = lower_bound
        sub_df.loc[0, "Upper Bound"] = upper_bound
        return dataframe, sub_df

    def z_outlier_custom(self, data, z, custom, dataframe):
        lower_bound = dataframe[data].mean() - (z * dataframe[data].sem())
        upper_bound = dataframe[data].mean() + (z * dataframe[data].sem())
        outliers1 = [x for x in dataframe[data] if x <= lower_bound]
        outliers2 = [x for x in dataframe[data] if x >= upper_bound]
        dataframe.loc[dataframe[data] < lower_bound, data] = custom
        dataframe.loc[dataframe[data] > upper_bound, data] = custom
        sub_df = pd.DataFrame(columns=["Lower Bound", "Upper Bound", "Lower Outliers", "Upper Outliers"])
        sub_df.loc[0, "Lower Outliers"] = len(outliers1)
        sub_df.loc[0, "Upper Outliers"] = len(outliers2)
        sub_df.loc[0, "Lower Bound"] = lower_bound
        sub_df.loc[0, "Upper Bound"] = upper_bound
        return dataframe, sub_df

    def z_outlier_remove(self, data, z, dataframe):
        lower_bound = dataframe[data].mean() - (z * dataframe[data].sem())
        upper_bound = dataframe[data].mean() + (z * dataframe[data].sem())
        outliers1 = [x for x in dataframe[data] if x <= lower_bound]
        outliers2 = [x for x in dataframe[data] if x >= upper_bound]
        dataframe.loc[dataframe[data] < lower_bound, data] = np.nan
        dataframe.loc[dataframe[data] > upper_bound, data] = np.nan
        dataframe.dropna(axis=0, inplace=True)
        sub_df = pd.DataFrame(columns=["Lower Bound", "Upper Bound", "Lower Outliers", "Upper Outliers"])
        sub_df.loc[0, "Lower Outliers"] = len(outliers1)
        sub_df.loc[0, "Upper Outliers"] = len(outliers2)
        sub_df.loc[0, "Lower Bound"] = lower_bound
        sub_df.loc[0, "Upper Bound"] = upper_bound
        return dataframe, sub_df

    def std_outlier_mean(self, data, std, dataframe):

        a = st.norm.interval(alpha=std, loc=dataframe[data].mean(), scale=dataframe[data].sem())
        lower_bound = a[0]
        upper_bound = a[1]
        d = dataframe[data].mean()
        outliers1 = [x for x in dataframe[data] if x <= lower_bound]
        outliers2 = [x for x in dataframe[data] if x >= upper_bound]
        dataframe.loc[dataframe[data] < lower_bound, data] = d
        dataframe.loc[dataframe[data] > upper_bound, data] = d
        sub_df = pd.DataFrame(columns=["Lower Bound", "Upper Bound", "Lower Outliers", "Upper Outliers"])
        sub_df.loc[0, "Lower Outliers"] = len(outliers1)
        sub_df.loc[0, "Upper Outliers"] = len(outliers2)
        sub_df.loc[0, "Lower Bound"] = lower_bound
        sub_df.loc[0, "Upper Bound"] = upper_bound
        return dataframe, sub_df

    def std_outlier_mode(self, data, std, dataframe):

        a = st.norm.interval(alpha=std, loc=dataframe[data].mean(), scale=dataframe[data].sem())
        lower_bound = a[0]
        upper_bound = a[1]
        d = dataframe[data].mode()[0]
        outliers1 = [x for x in dataframe[data] if x <= lower_bound]
        outliers2 = [x for x in dataframe[data] if x >= upper_bound]
        dataframe.loc[dataframe[data] < lower_bound, data] = d
        dataframe.loc[dataframe[data] > upper_bound, data] = d
        sub_df = pd.DataFrame(columns=["Lower Bound", "Upper Bound", "Lower Outliers", "Upper Outliers"])
        sub_df.loc[0, "Lower Outliers"] = len(outliers1)
        sub_df.loc[0, "Upper Outliers"] = len(outliers2)
        sub_df.loc[0, "Lower Bound"] = lower_bound
        sub_df.loc[0, "Upper Bound"] = upper_bound
        return dataframe, sub_df

    def std_outlier_bounds(self, data, std, dataframe):

        a = st.norm.interval(alpha=std, loc=dataframe[data].mean(), scale=dataframe[data].sem())
        lower_bound = a[0]
        upper_bound = a[1]
        outliers1 = [x for x in dataframe[data] if x <= lower_bound]
        outliers2 = [x for x in dataframe[data] if x >= upper_bound]
        dataframe.loc[dataframe[data] < lower_bound, data] = lower_bound
        dataframe.loc[dataframe[data] > upper_bound, data] = upper_bound
        sub_df = pd.DataFrame(columns=["Lower Bound", "Upper Bound", "Lower Outliers", "Upper Outliers"])
        sub_df.loc[0, "Lower Outliers"] = len(outliers1)
        sub_df.loc[0, "Upper Outliers"] = len(outliers2)
        sub_df.loc[0, "Lower Bound"] = lower_bound
        sub_df.loc[0, "Upper Bound"] = upper_bound
        return dataframe, sub_df

    def std_outlier_custom(self, data, std, custom, dataframe):

        a = st.norm.interval(alpha=std, loc=dataframe[data].mean(), scale=dataframe[data].sem())
        lower_bound = a[0]
        upper_bound = a[1]
        outliers1 = [x for x in dataframe[data] if x <= lower_bound]
        outliers2 = [x for x in dataframe[data] if x >= upper_bound]
        dataframe.loc[dataframe[data] < lower_bound, data] = custom
        dataframe.loc[dataframe[data] > upper_bound, data] = custom
        sub_df = pd.DataFrame(columns=["Lower Bound", "Upper Bound", "Lower Outliers", "Upper Outliers"])
        sub_df.loc[0, "Lower Outliers"] = len(outliers1)
        sub_df.loc[0, "Upper Outliers"] = len(outliers2)
        sub_df.loc[0, "Lower Bound"] = lower_bound
        sub_df.loc[0, "Upper Bound"] = upper_bound
        return dataframe, sub_df

    def std_outlier_remove(self, data, std, dataframe):

        a = st.norm.interval(alpha=std, loc=dataframe[data].mean(), scale=dataframe[data].sem())
        lower_bound = a[0]
        upper_bound = a[1]
        outliers1 = [x for x in dataframe[data] if x <= lower_bound]
        outliers2 = [x for x in dataframe[data] if x >= upper_bound]
        dataframe.loc[dataframe[data] < lower_bound, data] = np.nan
        dataframe.loc[dataframe[data] > upper_bound, data] = np.nan
        dataframe.dropna(axis=0, inplace=True)
        sub_df = pd.DataFrame(columns=["Lower Bound", "Upper Bound", "Lower Outliers", "Upper Outliers"])
        sub_df.loc[0, "Lower Outliers"] = len(outliers1)
        sub_df.loc[0, "Upper Outliers"] = len(outliers2)
        sub_df.loc[0, "Lower Bound"] = lower_bound
        sub_df.loc[0, "Upper Bound"] = upper_bound
        return dataframe, sub_df

    def IQR_outlier_mean(self, data, ratio, dataframe):
        q1, q3 = np.percentile(dataframe[data], [25, 75])
        iqr = q3 - q1
        lower_bound = q1 - (ratio * iqr)
        upper_bound = q3 + (ratio * iqr)
        b = dataframe[data].mean()
        outliers1 = [x for x in dataframe[data] if x <= lower_bound]
        outliers2 = [x for x in dataframe[data] if x >= upper_bound]
        dataframe.loc[dataframe[data] < lower_bound, data] = b
        dataframe.loc[dataframe[data] > upper_bound, data] = b
        sub_df = pd.DataFrame(columns=["Lower Bound", "Upper Bound", "Lower Outliers", "Upper Outliers"])
        sub_df.loc[0, "Lower Outliers"] = len(outliers1)
        sub_df.loc[0, "Upper Outliers"] = len(outliers2)
        sub_df.loc[0, "Lower Bound"] = lower_bound
        sub_df.loc[0, "Upper Bound"] = upper_bound
        return dataframe, sub_df

    def IQR_outlier_mode(self, data, ratio, dataframe):
        q1, q3 = np.percentile(dataframe[data], [25, 75])
        iqr = q3 - q1
        lower_bound = q1 - (ratio * iqr)
        upper_bound = q3 + (ratio * iqr)
        b = dataframe[data].mode()[0]
        outliers1 = [x for x in dataframe[data] if x <= lower_bound]
        outliers2 = [x for x in dataframe[data] if x >= upper_bound]
        dataframe.loc[dataframe[data] < lower_bound, data] = b
        dataframe.loc[dataframe[data] > upper_bound, data] = b
        sub_df = pd.DataFrame(columns=["Lower Bound", "Upper Bound", "Lower Outliers", "Upper Outliers"])
        sub_df.loc[0, "Lower Outliers"] = len(outliers1)
        sub_df.loc[0, "Upper Outliers"] = len(outliers2)
        sub_df.loc[0, "Lower Bound"] = lower_bound
        sub_df.loc[0, "Upper Bound"] = upper_bound
        return dataframe, sub_df

    def IQR_outlier_bounds(self, data, ratio, dataframe):
        q1, q3 = np.percentile(dataframe[data], [25, 75])
        iqr = q3 - q1
        lower_bound = q1 - (ratio * iqr)
        upper_bound = q3 + (ratio * iqr)
        outliers1 = [x for x in dataframe[data] if x <= lower_bound]
        outliers2 = [x for x in dataframe[data] if x >= upper_bound]
        dataframe.loc[dataframe[data] < lower_bound, data] = lower_bound
        dataframe.loc[dataframe[data] > upper_bound, data] = upper_bound
        sub_df = pd.DataFrame(columns=["Lower Bound", "Upper Bound", "Lower Outliers", "Upper Outliers"])
        sub_df.loc[0, "Lower Outliers"] = len(outliers1)
        sub_df.loc[0, "Upper Outliers"] = len(outliers2)
        sub_df.loc[0, "Lower Bound"] = lower_bound
        sub_df.loc[0, "Upper Bound"] = upper_bound
        return dataframe, sub_df

    def IQR_outlier_custom(self, data, ratio, custom, dataframe):
        q1, q3 = np.percentile(dataframe[data], [25, 75])
        iqr = q3 - q1
        lower_bound = q1 - (ratio * iqr)
        upper_bound = q3 + (ratio * iqr)
        outliers1 = [x for x in dataframe[data] if x <= lower_bound]
        outliers2 = [x for x in dataframe[data] if x >= upper_bound]
        dataframe.loc[dataframe[data] < lower_bound, data] = custom
        dataframe.loc[dataframe[data] > upper_bound, data] = custom
        sub_df = pd.DataFrame(columns=["Lower Bound", "Upper Bound", "Lower Outliers", "Upper Outliers"])
        sub_df.loc[0, "Lower Outliers"] = len(outliers1)
        sub_df.loc[0, "Upper Outliers"] = len(outliers2)
        sub_df.loc[0, "Lower Bound"] = lower_bound
        sub_df.loc[0, "Upper Bound"] = upper_bound
        return dataframe, sub_df

    def IQR_outlier_remove(self, data, ratio, dataframe):
        q1, q3 = np.percentile(dataframe[data], [25, 75])
        iqr = q3 - q1
        lower_bound = q1 - (ratio * iqr)
        upper_bound = q3 + (ratio * iqr)
        outliers1 = [x for x in dataframe[data] if x <= lower_bound]
        outliers2 = [x for x in dataframe[data] if x >= upper_bound]
        dataframe.loc[dataframe[data] < lower_bound, data] = np.nan
        dataframe.loc[dataframe[data] > upper_bound, data] = np.nan
        dataframe.dropna(axis=0, inplace=True)
        sub_df = pd.DataFrame(columns=["Lower Bound", "Upper Bound", "Lower Outliers", "Upper Outliers"])
        sub_df.loc[0, "Lower Outliers"] = len(outliers1)
        sub_df.loc[0, "Upper Outliers"] = len(outliers2)
        sub_df.loc[0, "Lower Bound"] = lower_bound
        sub_df.loc[0, "Upper Bound"] = upper_bound
        return dataframe, sub_df

    def difference(self, data, interval, dataframe):
        dataframe["differenced data"] = ""
        for i in range(interval, len(dataframe)):
            dataframe["differenced data"][i] = dataframe[data][i] - dataframe[data][i - interval]
        dataframe[data] = dataframe["differenced data"].values
        dataframe = dataframe.drop("differenced data", axis=1)
        return dataframe

    def train_test_train(self, split, dataframe):
        sub_df1, sub_df2 = train_test_split(dataframe, train_size=split, test_size=(1 - split))
        output = {"train": pd.DataFrame(sub_df1), "test": pd.DataFrame(sub_df2)}
        return output

    def binning1(self, data, no_of_bins, dataframe):
        binn1 = pd.cut(dataframe[data], no_of_bins)
        dataframe[data] = binn1.cat.codes
        return dataframe

    def binning2(self, data, step_size, dataframe):
        binn2_range = list(range(int(min(dataframe[data])), int(max(dataframe[data]) + 1), step_size))
        binn2 = pd.cut(dataframe[data], bins=binn2_range)
        dataframe[data] = binn2.cat.codes
        return dataframe

    def cat_binning(self, data, dataframe):
        for i in data:
            dataframe[i] = dataframe[i].astype("category").cat.codes
        return dataframe

    def ordinal_binning(self, data, list_un, list_rank, dataframe):
        dictionary = {k: v for k, v in zip(list_un, list_rank)}
        dataframe[data] = dataframe[data].replace(dictionary)
        return dataframe


def Missing_Values(dataframe, configDict):
    missing_func = Missing_values_Func()
    sub_operation = configDict["inputs"]["Sub_Op"]
    data = configDict["inputs"]["Other_Inputs"]["Data"]

    if sub_operation == "previous":
        output_data = missing_func.fill_previous(data, dataframe)
        return output_data

    if sub_operation == "next":
        output_data = missing_func.fill_next(data, dataframe)
        return output_data

    if sub_operation == "average":
        output_data = missing_func.fill_mean(data, dataframe)
        return output_data

    if sub_operation == "mode":
        output_data = missing_func.fill_mode(data, dataframe)
        return output_data

    if sub_operation == "custom":
        custom_value = configDict["inputs"]["Other_Inputs"]["subOpConfig"]
        output_data = missing_func.fill_custom(data, dataframe, custom_value=custom_value)
        return output_data


def Feature_Scaling(dataframe, configDict):
    missing_func = Missing_values_Func()
    sub_operation = configDict["inputs"]["Sub_Op"]
    data = configDict["inputs"]["Other_Inputs"]["Data"]

    if sub_operation == "minmax":
        output_data = missing_func.min_max(data, dataframe)
        return output_data

    if sub_operation == "standard":
        output_data = missing_func.standardized(data, dataframe)
        return output_data

    if sub_operation == "robust":
        output_data = missing_func.robust(data, dataframe)
        return output_data


def Outlier_Check(dataframe, configDict):
    missing_func = Missing_values_Func()
    sub_operation = configDict["inputs"]["Sub_Op"]
    data = configDict["inputs"]["Other_Inputs"]["Data"]
    action = configDict["inputs"]["Other_Inputs"]["Action"]

    if sub_operation == "123std":
        std = float(configDict["inputs"]["Other_Inputs"]["Std"])
        if action == "rwmean":
            output_data = missing_func.std_outlier_mean(data, std, dataframe)
            return output_data
        elif action == "rwmode":
            output_data = missing_func.std_outlier_mode(data, std, dataframe)
            return output_data
        elif action == "rwbounds":
            output_data = missing_func.std_outlier_bounds(data, std, dataframe)
            return output_data
        elif action == "rwcustom":
            out_custom = float(configDict["inputs"]["Other_Inputs"]["Out_custom"])
            output_data = missing_func.std_outlier_custom(data, std, out_custom, dataframe)
            return output_data
        elif action == "rwremove":
            output_data = missing_func.std_outlier_remove(data, std, dataframe)
            return output_data

    if sub_operation == "ci":
        alpha = float(configDict["inputs"]["Other_Inputs"]["Alpha"])
        if action == "rwmean":
            output_data = missing_func.CI_outlier_mean(data, alpha, dataframe)
            return output_data
        elif action == "rwmode":
            output_data = missing_func.CI_outlier_mode(data, alpha, dataframe)
            return output_data
        elif action == "rwbounds":
            output_data = missing_func.CI_outlier_bounds(data, alpha, dataframe)
            return output_data
        elif action == "rwcustom":
            out_custom = float(configDict["inputs"]["Other_Inputs"]["Out_custom"])
            output_data = missing_func.CI_outlier_custom(data, alpha, out_custom, dataframe)
            return output_data
        elif action == "rwremove":
            output_data = missing_func.CI_outlier_remove(data, alpha, dataframe)
            return output_data

    if sub_operation == "iqr":
        ratio = float(configDict["inputs"]["Other_Inputs"]["Ratio"])
        if action == "rwmean":
            output_data = missing_func.IQR_outlier_mean(data, ratio, dataframe)
            return output_data
        elif action == "rwmode":
            output_data = missing_func.IQR_outlier_mode(data, ratio, dataframe)
            return output_data
        elif action == "rwbounds":
            output_data = missing_func.IQR_outlier_bounds(data, ratio, dataframe)
            return output_data
        elif action == "rwcustom":
            out_custom = float(configDict["inputs"]["Other_Inputs"]["Out_custom"])
            output_data = missing_func.IQR_outlier_custom(data, ratio, out_custom, dataframe)
            return output_data
        elif action == "rwremove":
            output_data = missing_func.IQR_outlier_remove(data, ratio, dataframe)
            return output_data

    if sub_operation == "zscores":
        z = float(configDict["inputs"]["Other_Inputs"]["Z"])
        if action == "rwmean":
            output_data = missing_func.z_outlier_mean(data, z, dataframe)
            return output_data
        elif action == "rwmode":
            output_data = missing_func.z_outlier_mode(data, z, dataframe)
            return output_data
        elif action == "rwbounds":
            output_data = missing_func.z_outlier_bounds(data, z, dataframe)
            return output_data
        elif action == "rwcustom":
            out_custom = float(configDict["inputs"]["Other_Inputs"]["Out_custom"])
            output_data = missing_func.z_outlier_custom(data, z, out_custom, dataframe)
            return output_data
        elif action == "rwremove":
            output_data = missing_func.z_outlier_remove(data, z, dataframe)
            return output_data


def Differencing(dataframe, configDict):
    missing_func = Missing_values_Func()
    data = configDict["inputs"]["Other_Inputs"]["Data"]
    interval = int(configDict["inputs"]["Other_Inputs"]["Interval"])

    output_data = missing_func.difference(data, interval, dataframe)
    return output_data


def Splitting_Datasets(dataframe, configDict):
    missing_func = Missing_values_Func()
    split = float(configDict["inputs"]["Other_Inputs"]["Split"])

    output_data = missing_func.train_test_train(split, dataframe)
    return output_data


def Binning(dataframe, configDict):
    missing_func = Missing_values_Func()
    sub_operation = configDict["inputs"]["Sub_Op"]
    data = configDict["inputs"]["Other_Inputs"]["Data"]

    if sub_operation == "numerical":
        numerical_sub = configDict["inputs"]["Other_Inputs"]["Numerical_Sub"]
        if numerical_sub == "nno_of_bins":
            no_of_bins = int(configDict["inputs"]["Other_Inputs"]["No_of_bins"])
            output_data = missing_func.binning1(data, no_of_bins, dataframe)
            return output_data

        elif numerical_sub == "nstepsize":
            stepsize = int(configDict["inputs"]["Other_Inputs"]["StepSize"])
            output_data = missing_func.binning2(data, stepsize, dataframe)
            return output_data

    if sub_operation == "categorical":
        categorical_sub = configDict["inputs"]["Other_Inputs"]["Categorical_Sub"]
        if categorical_sub == "cnominal":
            output_data = missing_func.cat_binning(data, dataframe)
            return output_data

        if categorical_sub == "cordinal":
            list1 = configDict["inputs"]["Other_Inputs"]["List"]
            list2 = configDict["inputs"]["Other_Inputs"]["Rank"]
            output_data = missing_func.ordinal_binning(data, list1, list2, dataframe)
            return output_data


def Data_Summary(dataframe, configDict):
    columns_list = configDict["inputs"]["cols_ds_list"]
    if len(columns_list) == 0:
        columns_list = dataframe.columns.tolist()

    data2 = dataframe[columns_list].describe(include="all", datetime_is_numeric=False)
    b = data2.index.to_list()
    data2["Field"] = b
    data2.reset_index(inplace=True, drop=True)

    data_type_mapper = {
        "object": "Character",
        "float64": "Float",
        "int64": "Integer",
        "bool": "Boolean",
        "datetime64[ns]": "Datetime",
    }
    new_data = [data_type_mapper[str(v)] for v in dataframe[columns_list].dtypes.tolist()]
    new_data.append("Field type")
    data2.loc[len(data2.index)] = new_data

    n2 = []
    n2 = dataframe[columns_list].isna().sum().tolist()
    n2.append("Missing values count")
    data2.loc[len(data2.index)] = n2

    data2 = data2.set_index("Field").T
    data2["Field"] = data2.index

    col_reorder = data2.columns.tolist()
    col_reorder = col_reorder[-1:] + col_reorder[:-1]
    data2 = data2[col_reorder]
    if "top" in data2.columns:
        data2["top"] = data2["top"].astype(str)
    else:
        pass
    data2.reset_index(drop=True, inplace=True)
    return data2


def Data_Mapping(config_dict, base_data, mapping_ruleset):
    base_data = base_data
    mapping_ruleset = mapping_ruleset
    data_error = ""
    try:
        ideal_type = {
            "use_case": "object",
            "constraint_name": "object",
            "rule_set": "object",
            "constraint_parameter": "object",
            "constraint_type": "object",
            "condition_datatype": "object",
            "condition": "object",
            "threshold": "object",
        }
        field_type = mapping_ruleset.dtypes.apply(lambda x: x.name).to_dict()
        for col, d_type in ideal_type.items():
            if field_type[col] != d_type:
                mapping_ruleset[col] = mapping_ruleset[col].astype(d_type)
    except Exception as e:
        logging.warning(f"Following exception occured - {e}")
        data_error = f"Data validation error in Mapping ruleset data in {col} column! {str(e)}"
        return [], data_error
    mapping_ruleset["unique_code"] = (
        mapping_ruleset["use_case"].astype("str") + "_" + mapping_ruleset["rule_set"].astype("str")
    )
    unique_rulesets = mapping_ruleset["unique_code"].unique().tolist()
    column_name = config_dict["inputs"]["new_column_name"]
    base_data[column_name] = ""
    for i in unique_rulesets:
        rule_set_dict = mapping_ruleset.loc[mapping_ruleset["unique_code"] == i].to_dict("records")
        string_cond = ""
        mapped_data = rule_set_dict[0]["use_case"]
        for j in rule_set_dict:
            if j["condition"] == "Equal to":
                if j["condition_datatype"] == "Numeric":
                    string_cond += (
                        "(base_data"
                        + "["
                        + "'"
                        + j["constraint_parameter"]
                        + "'"
                        + "]"
                        + "=="
                        + j["threshold"]
                        + ")"
                    )
                else:
                    string_cond += (
                        "(base_data"
                        + "["
                        + "'"
                        + j["constraint_parameter"]
                        + "'"
                        + "]"
                        + "=="
                        + "'"
                        + j["threshold"]
                        + "'"
                        + ")"
                    )
            if j["condition"] == "Greater than":
                if j["condition_datatype"] == "Numeric":
                    string_cond += (
                        "(base_data"
                        + "["
                        + "'"
                        + j["constraint_parameter"]
                        + "'"
                        + "]"
                        + ">"
                        + j["threshold"]
                        + ")"
                    )
                else:
                    string_cond += (
                        "(base_data"
                        + "["
                        + "'"
                        + j["constraint_parameter"]
                        + "'"
                        + "]"
                        + ">"
                        + "'"
                        + j["threshold"]
                        + "'"
                        + ")"
                    )
            if j["condition"] == "Greater than equal to":
                if j["condition_datatype"] == "Numeric":
                    string_cond += (
                        "(base_data"
                        + "["
                        + "'"
                        + j["constraint_parameter"]
                        + "'"
                        + "]"
                        + ">="
                        + j["threshold"]
                        + ")"
                    )
                else:
                    string_cond += (
                        "(base_data"
                        + "["
                        + "'"
                        + j["constraint_parameter"]
                        + "'"
                        + "]"
                        + ">="
                        + "'"
                        + j["threshold"]
                        + "'"
                        + ")"
                    )
            if j["condition"] == "Smaller than equal to":
                if j["condition_datatype"] == "Numeric":
                    string_cond += (
                        "(base_data"
                        + "["
                        + "'"
                        + j["constraint_parameter"]
                        + "'"
                        + "]"
                        + "<="
                        + j["threshold"]
                        + ")"
                    )
                else:
                    string_cond += (
                        "(base_data"
                        + "["
                        + "'"
                        + j["constraint_parameter"]
                        + "'"
                        + "]"
                        + "<="
                        + "'"
                        + j["threshold"]
                        + "'"
                        + ")"
                    )
            if j["condition"] == "Smaller than":
                if j["condition_datatype"] == "Numeric":
                    string_cond += (
                        "(base_data"
                        + "["
                        + "'"
                        + j["constraint_parameter"]
                        + "'"
                        + "]"
                        + "<"
                        + j["threshold"]
                        + ")"
                    )
                else:
                    string_cond += (
                        "(base_data"
                        + "["
                        + "'"
                        + j["constraint_parameter"]
                        + "'"
                        + "]"
                        + "<"
                        + "'"
                        + j["threshold"]
                        + "'"
                        + ")"
                    )
            if j["condition"] == "Not Equal to":
                if j["condition_datatype"] == "Numeric":
                    string_cond += (
                        "(base_data"
                        + "["
                        + "'"
                        + j["constraint_parameter"]
                        + "'"
                        + "]"
                        + "!="
                        + j["threshold"]
                        + ")"
                    )
                else:
                    string_cond += (
                        "(base_data"
                        + "["
                        + "'"
                        + j["constraint_parameter"]
                        + "'"
                        + "]"
                        + "!="
                        + "'"
                        + j["threshold"]
                        + "'"
                        + ")"
                    )
            if j["condition"] == "Contains":
                j["threshold"] = list(json.loads(j["threshold"]).keys())
                string_cond += (
                    "(base_data"
                    + "["
                    + "'"
                    + j["constraint_parameter"]
                    + "'"
                    + "]"
                    + ".isin("
                    + str(j["threshold"])
                    + ")"
                    + ")"
                )
            if rule_set_dict.index(j) != len(rule_set_dict) - 1:
                string_cond += " & "
        base_data.loc[pd.eval(string_cond, target=base_data), column_name] = mapped_data
    return base_data, data_error


def one_hot_encoder(data, config_dict):
    encode_columns = config_dict["inputs"]["encode_columns"]
    drop_first = config_dict["inputs"]["drop_first"]
    if len(encode_columns) == 0:
        encode_columns = data.select_dtypes(include=["object"]).columns.tolist()

    encoded_data = pd.get_dummies(data[encode_columns], drop_first=drop_first)
    data.drop(columns=encode_columns, inplace=True)
    data = pd.concat([data, encoded_data], axis=1)
    return data


def Delimit_values(data, config_dict):
    column = config_dict["inputs"]["column"]
    separator = config_dict["inputs"]["separator"]
    data = data.assign(column=data[column].str.split(separator)).explode("column").reset_index(drop=True)
    data.drop(column, axis=1, inplace=True)
    data.rename(columns={"column": column}, inplace=True)
    return data
