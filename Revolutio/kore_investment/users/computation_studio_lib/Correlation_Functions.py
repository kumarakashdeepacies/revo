import pandas as pd
from scipy.stats import kendalltau, pearsonr, spearmanr


class Correlation_Func:
    def pearson(self, data1, data2, dataframe):
        sub_df = pd.DataFrame(columns=["Pearson's R"])
        corr = pearsonr(dataframe[data1], dataframe[data2])
        sub_df.loc[0] = corr[0]
        return sub_df

    def spearman(self, data1, data2, dataframe):
        sub_df = pd.DataFrame(columns=["Spearman's Rho"])
        coef, _ = spearmanr(dataframe[data1], dataframe[data2])
        sub_df.loc[0] = coef
        return sub_df

    def kendall(self, data1, data2, dataframe):
        sub_df = pd.DataFrame(columns=["Kendall's Tau"])
        kendall, _ = kendalltau(dataframe[data1], dataframe[data2])
        sub_df.loc[0] = kendall
        return sub_df


def Correlation_Functions(dataframe, configDict):
    corr_func = Correlation_Func()
    operation = configDict["inputs"]["Operation"]

    if operation == "Pearson's R":
        data1_col = configDict["inputs"]["Other_Inputs"]["Data1"]
        data2_col = configDict["inputs"]["Other_Inputs"]["Data2"]

        output_data = corr_func.pearson(data1_col, data2_col, dataframe)
        return output_data

    if operation == "Kendall's Tau":
        data1_col = configDict["inputs"]["Other_Inputs"]["Data1"]
        data2_col = configDict["inputs"]["Other_Inputs"]["Data2"]

        output_data = corr_func.kendall(data1_col, data2_col, dataframe)
        return output_data

    if operation == "Spearman's Rho":
        data1_col = configDict["inputs"]["Other_Inputs"]["Data1"]
        data2_col = configDict["inputs"]["Other_Inputs"]["Data2"]

        output_data = corr_func.spearman(data1_col, data2_col, dataframe)
        return output_data
