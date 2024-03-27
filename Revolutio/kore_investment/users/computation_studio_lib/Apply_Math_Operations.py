import math

from numba import guvectorize, int64
import numpy as np
import pandas as pd


class Apply_MathOps:
    def add_fn(self, dataframe, col_list, col_name, number=""):
        df = pd.DataFrame(dataframe.loc[:, col_list])
        if len(df.select_dtypes(include=["datetime64[ns]"]).columns.tolist()) > 0:
            if number or number == 0:
                dataframe[col_name] = pd.to_datetime(dataframe[col_list]) + pd.to_timedelta(
                    number, unit="D"
                )
            else:
                if df[col_list[1]].dtypes in ["datetime64[ns]"] and df[col_list[0]].dtypes not in [
                    "datetime64[ns]"
                ]:
                    sub1 = "pd.to_timedelta(df[col_list[0]], unit='D')"
                else:
                    sub1 = "dataframe[col_list[0]]"
                for i in range(1, len(col_list)):
                    if df[col_list[i - 1]].dtypes in ["datetime64[ns]"]:
                        sub2 = f".add(pd.to_timedelta(dataframe[col_list[{i}]],unit='D'))"
                    else:
                        sub2 = f".add(dataframe[col_list[{i}]])"
                    sub1 = sub1 + sub2
                dataframe[col_name] = pd.eval(sub1, target=dataframe)
        else:
            if number or number == 0:
                dataframe[col_name] = dataframe[col_list] + number
            else:
                sub1 = "dataframe[col_list[0]]"
                for i in range(1, len(col_list)):
                    sub2 = f".add(dataframe[col_list[{i}]])"
                    sub1 = sub1 + sub2
                dataframe[col_name] = pd.eval(sub1, target=dataframe)
        return dataframe

    def add_fn_eq(
        self,
        dataframe,
        col_list,
        col_name,
        sum_type,
        number="",
        Cell_11="",
        Cell_12="",
        Cell_21="",
        Cell_22="",
        Target_1="",
        Target_2="",
    ):
        if sum_type == "Column_Sum":
            df = pd.DataFrame(dataframe.loc[:, col_list])
            if len(df.select_dtypes(include=["datetime64[ns]"]).columns.tolist()) > 0:
                if number or number == 0:
                    dataframe[col_name] = pd.to_datetime(
                        dataframe[col_list]
                    ) + pd.to_timedelta(number, unit="D")
                else:
                    if df[col_list[1]].dtypes in ["datetime64[ns]"] and df[col_list[0]].dtypes not in [
                        "datetime64[ns]"
                    ]:
                        sub1 = "pd.to_timedelta(df[col_list[0]], unit='D')"
                    else:
                        sub1 = "dataframe[col_list[0]]"
                    for i in range(1, len(col_list)):
                        if df[col_list[i - 1]].dtypes in ["datetime64[ns]"]:
                            sub2 = f".add(pd.to_timedelta(dataframe[col_list[{i}]],unit='D'))"
                        else:
                            sub2 = f".add(dataframe[col_list[{i}]])"
                        sub1 = sub1 + sub2
                    dataframe[col_name] = pd.eval(sub1, target=dataframe)
            else:
                if number or number == 0:
                    dataframe[col_name] = dataframe[col_list] + number
                else:
                    sub1 = "dataframe[col_list[0]]"
                    for i in range(1, len(col_list)):
                        sub2 = f".add(dataframe[col_list[{i}]])"
                        sub1 = sub1 + sub2
                    dataframe[col_name] = pd.eval(sub1, target=dataframe)
            return dataframe

        elif sum_type == "Row_Sum":
            if number or number == 0:
                dataframe2 = dataframe.copy()
                dataframe2 = dataframe2.loc[col_list, :] + number
                dataframe3 = pd.concat([dataframe, dataframe2], ignore_index=True)
                dataframe3.reset_index(drop=True, inplace=True)
                dataframe = dataframe3.copy()
            else:
                dataframe2 = dataframe.copy()
                dataframe2 = dataframe.loc[col_list, :]
                dataframe2.loc[col_name, :] = dataframe2.sum(axis=0)
                dataframe2.reset_index(drop=True, inplace=True)
                dataframe.loc[len(dataframe.index)] = dataframe2.loc[len(dataframe2.index) - 1, :]

            return dataframe

        elif sum_type == "Cell_Sum":
            if number or number == 0:
                dataframe.at[Target_1, Target_2] = dataframe.at[Cell_11, Cell_12] + number
                return dataframe
            else:
                dataframe.at[Target_1, Target_2] = (
                    dataframe.at[Cell_11, Cell_12] + dataframe.at[Cell_21, Cell_22]
                )
                return dataframe

    def subtract_fn(self, dataframe, col_list, col_name, number=""):
        if (
            len(
                pd.DataFrame(dataframe.loc[:, col_list])
                .select_dtypes(include=["datetime64[ns]"])
                .columns.tolist()
            )
            > 0
        ):
            if number or number == 0:
                dataframe[col_name] = pd.to_datetime(dataframe[col_list]) - pd.to_timedelta(
                    number, unit="D"
                )

            else:
                dataframe[col_list[0]] = pd.to_datetime(dataframe[col_list[0]])
                sub1 = "dataframe[col_list[0]]"
                for i in range(1, len(col_list)):
                    dataframe[col_list[i]] = pd.to_datetime(dataframe[col_list[i]])
                    sub2 = f".sub(dataframe[col_list[{i}]])"
                    sub1 = sub1 + sub2
                dataframe[col_name] = (pd.eval(sub1, target=dataframe)).dt.days
        else:
            if number or number == 0:
                dataframe[col_name] = dataframe[col_list] - number
            else:
                sub1 = "dataframe[col_list[0]]"
                for i in range(1, len(col_list)):
                    sub2 = f".sub(dataframe[col_list[{i}]])"
                    sub1 = sub1 + sub2
                dataframe[col_name] = pd.eval(sub1, target=dataframe)
        return dataframe

    def subtract_fn_eq(
        self,
        dataframe,
        col_list,
        col_name,
        sum_type,
        number="",
        Cell_11="",
        Cell_12="",
        Cell_21="",
        Cell_22="",
        Target_1="",
        Target_2="",
    ):
        if sum_type == "Column_Sum":
            if (
                len(
                    pd.DataFrame(dataframe.loc[:, col_list])
                    .select_dtypes(include=["datetime64[ns]"])
                    .columns.tolist()
                )
                > 0
            ):
                if number or number == 0:
                    dataframe[col_name] = pd.to_datetime(
                        dataframe[col_list]
                    ) - pd.to_timedelta(number, unit="D")

                else:
                    dataframe[col_list[0]] = pd.to_datetime(dataframe[col_list[0]])
                    sub1 = "dataframe[col_list[0]]"
                    for i in range(1, len(col_list)):
                        dataframe[col_list[i]] = pd.to_datetime(dataframe[col_list[i]])
                        sub2 = f".sub(dataframe[col_list[{i}]])"
                        sub1 = sub1 + sub2
                    dataframe[col_name] = (pd.eval(sub1, target=dataframe)).dt.days
            else:
                if number or number == 0:
                    dataframe[col_name] = dataframe[col_list] - number
                else:
                    sub1 = "dataframe[col_list[0]]"
                    for i in range(1, len(col_list)):
                        sub2 = f".sub(dataframe[col_list[{i}]])"
                        sub1 = sub1 + sub2
                    dataframe[col_name] = pd.eval(sub1, target=dataframe)
            return dataframe

        elif sum_type == "Row_Sum":
            if number or number == 0:
                dataframe.loc[col_name] = dataframe.loc[col_list[0]] - number
            else:
                sub1 = "dataframe.loc[col_list[0]]"
                for i in range(1, len(col_list)):
                    sub2 = f" - dataframe.loc[col_list[{i}]]"
                    sub1 = sub1 + sub2
                    dataframe.loc[col_name] = pd.eval(sub1, target=dataframe)
            return dataframe

        elif sum_type == "Cell_Sum":
            if number or number == 0:
                dataframe.at[Target_1, Target_2] = dataframe.at[Cell_11, Cell_12] - number
                return dataframe
            else:
                dataframe.at[Target_1, Target_2] = (
                    dataframe.at[Cell_11, Cell_12] - dataframe.at[Cell_21, Cell_22]
                )
                return dataframe

    def multiply_fn(self, dataframe, col_list, col_name, number=""):
        if number or number == 0:
            dataframe[col_name] = dataframe[col_list] * number
        else:
            sub1 = "dataframe[col_list[0]]"
            for i in range(1, len(col_list)):
                sub2 = f".mul(dataframe[col_list[{i}]])"
                sub1 = sub1 + sub2
            dataframe[col_name] = pd.eval(sub1, target=dataframe)
        return dataframe

    def multiply_fn_eq(
        self,
        dataframe,
        col_list,
        col_name,
        sum_type,
        number="",
        Cell_11="",
        Cell_12="",
        Cell_21="",
        Cell_22="",
        Target_1="",
        Target_2="",
    ):
        if sum_type == "Column_Sum":
            if number or number == 0:
                dataframe[col_name] = dataframe[col_list] * number
            else:
                sub1 = "dataframe[col_list[0]]"
                for i in range(1, len(col_list)):
                    sub2 = f".mul(dataframe[col_list[{i}]])"
                    sub1 = sub1 + sub2
                dataframe[col_name] = pd.eval(sub1, target=dataframe)
            return dataframe

        elif sum_type == "Row_Sum":
            if number or number == 0:
                dataframe.loc[col_name] = dataframe.loc[col_list[0]] * number
            else:
                sub1 = "dataframe.loc[col_list[0]]"
                for i in range(1, len(col_list)):
                    sub2 = f" * dataframe.loc[col_list[{i}]]"
                    sub1 = sub1 + sub2
                    dataframe.loc[col_name] = pd.eval(sub1, target=dataframe)
            return dataframe

        elif sum_type == "Cell_Sum":
            if number or number == 0:
                dataframe.at[Target_1, Target_2] = dataframe.at[Cell_11, Cell_12] * number
                return dataframe
            else:
                dataframe.at[Target_1, Target_2] = (
                    dataframe.at[Cell_11, Cell_12] * dataframe.at[Cell_21, Cell_22]
                )
                return dataframe

    def division_fn(self, dataframe, col_list, col_name, number=""):
        if number or number == 0:
            dataframe[col_name] = dataframe[col_list] / number
        else:
            sub1 = dataframe[col_list[0]].div(dataframe[col_list[1]])
            dataframe[col_name] = sub1
        return dataframe

    def division_fn_eq(
        self,
        dataframe,
        col_list,
        col_name,
        sum_type,
        number="",
        Cell_11="",
        Cell_12="",
        Cell_21="",
        Cell_22="",
        Target_1="",
        Target_2="",
    ):
        if sum_type == "Column_Sum":
            if number or number == 0:
                dataframe[col_name] = dataframe[col_list] / number
            else:
                sub1 = "dataframe[col_list[0]]"
                for i in range(1, len(col_list)):
                    sub2 = f".div(dataframe[col_list[{i}]])"
                    sub1 = sub1 + sub2
                dataframe[col_name] = pd.eval(sub1, target=dataframe)
            return dataframe

        elif sum_type == "Row_Sum":
            if number or number == 0:
                dataframe.loc[col_name] = dataframe.loc[col_list[0]] / number
            else:
                sub1 = "dataframe.loc[col_list[0]]"
                for i in range(1, len(col_list)):
                    sub2 = f" / dataframe.loc[col_list[{i}]]"
                    sub1 = sub1 + sub2
                    dataframe.loc[col_name] = pd.eval(sub1, target=dataframe)
            return dataframe

        elif sum_type == "Cell_Sum":
            if number or number == 0:
                dataframe.at[Target_1, Target_2] = dataframe.at[Cell_11, Cell_12] / number
                return dataframe
            else:
                dataframe.at[Target_1, Target_2] = (
                    dataframe.at[Cell_11, Cell_12] / dataframe.at[Cell_21, Cell_22]
                )
                return dataframe

    def sumproduct_fn(self, dataframe, col_list):
        sub1 = "dataframe[col_list[0]]"
        for i in range(1, len(col_list)):
            sub2 = f".mul(dataframe[col_list[{i}]])"
            sub1 = sub1 + sub2
        dataframe["product"] = pd.eval(sub1, target=dataframe)
        sub_df = pd.DataFrame(columns=["Sumproduct"])
        sub_df.loc[0] = sum(dataframe["product"])
        return sub_df

    def floor_fn(self, dataframe, col1, col_name, multiple):
        dataframe[col_name] = dataframe[col1] - (dataframe[col1] % multiple)
        return dataframe

    @guvectorize([(int64[:], int64, int64[:])], "(n),()->(n)")
    def floor_fn_nb(col1, multiple, col_output):
        col_output[:] = col1 - (col1 % multiple)

    def ceil_fn(self, dataframe, col1, col_name, multiple):
        ceil_list = []
        for i in range(len(dataframe)):
            num = dataframe[col1][i]
            sub = num + (multiple - 1)
            ceil_list.append(sub - (sub % multiple))
        dataframe[col_name] = ceil_list
        return dataframe

    @guvectorize([(int64[:], int64, int64[:])], "(n),()->(n)")
    def ceil_fn_nb(col1, multiple, output):
        ceil_list = []
        for i in range(len(col1)):
            num = col1[i]
            sub = num + (multiple - 1)
            ceil_list.append(sub - (sub % multiple))
        output[:] = ceil_list

    def round_odd_fn(self, dataframe, col1, output_choice, col_name=0):
        if output_choice == "Yes_replace":
            roundodd_list = []
            for i in range(len(dataframe)):
                roundodd_list.append(int(dataframe[col1][i]) // 2 * 2 + 1)
            dataframe[col1] = roundodd_list
        else:
            roundodd_list = []
            for i in range(len(dataframe)):
                roundodd_list.append(int(dataframe[col1][i]) // 2 * 2 + 1)
            dataframe[col_name] = roundodd_list
        return dataframe

    def round_even_fn(self, dataframe, col1, output_choice, col_name=0):
        if output_choice == "Yes_replace":
            roundeven_list = []
            for i in range(len(dataframe)):
                num = dataframe[col1][i]
                answer = round(num)
                if not answer % 2:
                    even_ans = answer
                elif abs(answer + 1 - num) < abs(answer - 1 - num):
                    even_ans = answer + 1
                else:
                    even_ans = answer - 1
                roundeven_list.append(even_ans)
            dataframe[col1] = roundeven_list
        else:
            roundeven_list = []
            for i in range(len(dataframe)):
                num = dataframe[col1][i]
                answer = round(num)
                if not answer % 2:
                    even_ans = answer
                elif abs(answer + 1 - num) < abs(answer - 1 - num):
                    even_ans = answer + 1
                else:
                    even_ans = answer - 1
                roundeven_list.append(even_ans)
            dataframe[col_name] = roundeven_list
        return dataframe

    def round_fn(self, dataframe, col1, decimal, output_choice, col_name=0):
        if output_choice == "Yes_replace":
            dataframe[col1] = round(dataframe[col1], decimal)
        else:
            dataframe[col_name] = round(dataframe[col1], decimal)
        return dataframe

    def roundup_fn(self, dataframe, col1, output_choice, col_name=0):
        if output_choice == "Yes_replace":
            roundup_list = []
            for i in range(len(dataframe)):
                roundup_list.append(math.ceil(dataframe[col1][i]))
            dataframe[col1] = roundup_list
        else:
            roundup_list = []
            for i in range(len(dataframe)):
                roundup_list.append(math.ceil(dataframe[col1][i]))
            dataframe[col_name] = roundup_list
        return dataframe

    def rounddown_fn(self, dataframe, col1, output_choice, col_name=0):
        if output_choice == "Yes_replace":
            rounddown_list = []
            for i in range(len(dataframe)):
                rounddown_list.append(math.floor(dataframe[col1][i]))
            dataframe[col1] = rounddown_list
        else:
            rounddown_list = []
            for i in range(len(dataframe)):
                rounddown_list.append(math.floor(dataframe[col1][i]))
            dataframe[col_name] = rounddown_list
        return dataframe

    def truncate_fn(self, dataframe, col1, output_choice, col_name=0):
        if output_choice == "Yes_replace":
            trunc_list = []
            for i in range(len(dataframe)):
                trunc_list.append(np.trunc(dataframe[col1][i]))
            dataframe[col1] = trunc_list
        else:
            trunc_list = []
            for i in range(len(dataframe)):
                trunc_list.append(np.trunc(dataframe[col1][i]))
            dataframe[col_name] = trunc_list
        return dataframe

    def log_natural_fn(self, dataframe, col1, col_name):
        dataframe[col_name] = np.log(dataframe[col1])
        return dataframe

    @guvectorize([(int64[:], int64[:])], "(n)->(n)")
    def log_natural_fn_nb(col1, col_output):
        col_output[:] = np.log(col1)

    def exponential_fn(self, dataframe, col1, col_name):
        dataframe[col_name] = np.exp(dataframe[col1])
        return dataframe

    def log_fn(self, dataframe, col1, base, col_name):
        log_val = []
        for i in range(len(dataframe[col1])):
            try:
                log_val.append(math.log(dataframe[col1][i], base))
            except ValueError:
                log_val.append(dataframe[col1][i])
        dataframe[col_name] = log_val
        return dataframe

    def power_fn(self, dataframe, col1, power_val, col_name):
        powers = np.power(dataframe[col1], power_val)
        dataframe[col_name] = powers
        return dataframe

    def square_root_fn(self, dataframe, col1, col_name):
        dataframe[col_name] = np.sqrt(dataframe[col1])
        return dataframe

    @guvectorize([(int64[:], int64[:])], "(n)->(n)")
    def square_root_fn_nb(col1, col_output):
        col_output[:] = np.sqrt(col1)

    def square_root_pi_fn(self, dataframe, col1, col_name):
        dataframe[col_name] = np.sqrt(dataframe[col1]) * math.pi
        return dataframe

    @guvectorize([(int64[:], int64[:])], "(n)->(n)")
    def square_root_pi_fn_nb(col1, col_output):
        col_output[:] = np.sqrt(col1) * math.pi

    def rand_fn(self, dataframe, col_name):
        random_col = []
        for i in range(len(dataframe)):
            random_col.append(np.random.rand())
        dataframe[col_name] = random_col
        return dataframe

    def rand_between_fn(self, dataframe, lower_lim, upper_lim, col_name):
        random_col = []
        for i in range(len(dataframe)):
            random_col.append(np.random.randint(lower_lim, upper_lim))
        dataframe[col_name] = random_col
        return dataframe

    def sum_squares_fn(self, dataframe, col1, col2, col_name):
        sum_sq = np.square(dataframe[col1]) + np.square(dataframe[col2])
        dataframe[col_name] = sum_sq
        return dataframe

    @guvectorize([(int64[:], int64[:], int64[:])], "(n),(n)->(n)")
    def sum_squares_fn_nb(col1, col2, sum_sq):
        sum_sq[:] = np.square(col1) + np.square(col2)

    def sumx2py2_fn(self, dataframe, col1, col2):
        sum_sq = np.square(dataframe[col1]) + np.square(dataframe[col2])
        sub_df = pd.DataFrame(columns=["Total Sum of the Sum of Squared Numbers"])
        sub_df.loc[0] = sum_sq.sum()
        return sub_df

    @guvectorize([(int64[:], int64[:], int64[:])], "(n),(n)->()")
    def sumx2py2_fn_nb(col1, col2, sub_df):
        sum_sq = np.square(col1) + np.square(col2)
        sub_df[:] = sum_sq.sum()

    def sumx2my2_fn(self, dataframe, col1, col2):
        sum_sq = np.square(dataframe[col1]) - np.square(dataframe[col2])
        sub_df = pd.DataFrame(columns=["Total Sum of the Difference of Squared Numbers"])
        sub_df.loc[0] = sum_sq.sum()
        return sub_df

    @guvectorize([(int64[:], int64[:], int64[:])], "(n),(n)->()")
    def sumx2my2_fn_nb(col1, col2, sub_df):
        sum_sq = np.square(col1) - np.square(col2)
        sub_df[:] = sum_sq.sum()

    def sumxmy2_fn(self, dataframe, col1, col2):
        sum_sq = np.square(dataframe[col1] - dataframe[col2])
        sub_df = pd.DataFrame(columns=["Sum of Squared Differences"])
        sub_df.loc[0] = sum_sq.sum()
        return sub_df

    @guvectorize([(int64[:], int64[:], int64[:])], "(n),(n)->()")
    def sumxmy2_fn_nb(col1, col2, sub_df):
        sum_sq = np.square(col1 - col2)
        sub_df[:] = sum_sq.sum()

    def matrix_determinant(self, dataframe):
        sub = np.asmatrix(dataframe)
        sub_df = pd.DataFrame(columns=["Matrix Determinant"])
        sub_df.loc[0] = np.linalg.det(sub)
        return sub_df

    @guvectorize([(int64[:, :], int64[:])], "(n,n)->()", forceobj=True)
    def matrix_determinant_nb(sub, sub_df):
        sub_df[:] = np.linalg.det(sub)

    def matrix_identity(self, matrix_size):
        sub = np.identity(matrix_size, dtype=int)
        return pd.DataFrame(sub)

    def matrix_mul(self, dataframe1, dataframe2):
        m1 = np.asmatrix(dataframe1)
        m2 = np.asmatrix(dataframe2)
        mul_matrix = np.dot(m1, m2)
        return pd.DataFrame(mul_matrix)

    @guvectorize([(int64[:, :], int64[:, :], int64[:, :])], "(n,m),(m,p)->(n,p)", forceobj=True)
    def matrix_mul_nb(m1, m2, mul_matrix):
        mul_matrix[:] = np.dot(m1, m2)

    def matrix_inverse(self, dataframe):
        sub = np.asmatrix(dataframe)
        inverse = np.linalg.inv(sub)
        return pd.DataFrame(inverse)

    @guvectorize([(int64[:, :], int64[:, :])], "(n,m)->(n,m)", forceobj=True)
    def matrix_inverse_nb(sub, inverse):
        inverse[:] = np.linalg.inv(sub)

    def absolute_fn(self, dataframe, col1):
        dataframe[col1] = abs(dataframe[col1])
        return dataframe

    @guvectorize([(int64[:], int64[:])], "(n)->(n)")
    def absolute_fn_nb(col1, col_output):
        col_output[:] = [abs(i) for i in col1]

    def factorial_fn(self, dataframe, col1, col_name):
        factorial_col = []
        for i in range(len(dataframe[col1])):
            factorial_col.append(math.factorial(int(dataframe[col1][i])))
        dataframe[col_name] = factorial_col
        return dataframe

    def sign_fn(self, dataframe, col1, col_name):
        dataframe[col_name] = np.sign(dataframe[col1])
        return dataframe

    @guvectorize([(int64[:], int64[:])], "(n)->(n)")
    def sign_fn_nb(col1, col_output):
        col_output[:] = np.sign(col1)

    def mod_fn(self, dataframe, col1, divisor, col_name):
        dataframe[col_name] = dataframe[col1] % divisor
        return dataframe

    @guvectorize([(int64[:], int64, int64[:])], "(n),()->(n)")
    def mod_fn_nb(col1, divisor, col_output):
        col_output[:] = col1 % divisor

    def quotient_fn(self, dataframe, col1, divisor, col_name):
        dataframe[col_name] = (dataframe[col1] - dataframe[col1] % divisor) / divisor
        return dataframe

    @guvectorize([(int64[:], int64, int64[:])], "(n),()->(n)")
    def quotient_fn_nb(col1, divisor, col_output):
        col_output[:] = (col1 - col1 % divisor) / divisor


def Apply_Math_Operation_Func(dataframe, config_dict):
    mathOps_Func = Apply_MathOps()
    sub_operation = config_dict["inputs"]["Sub_Op"]
    col1 = config_dict["inputs"]["Column_1"]
    col2 = config_dict["inputs"]["Column_2"]
    if config_dict["inputs"].get("Data_choice"):
        data_choice = config_dict["inputs"].get("Data_choice")
    else:
        data_choice = "Custom_input"
    additional_cols = config_dict["inputs"]["Additional_Colns"]
    col_list = [col1, col2]
    col_list.extend(additional_cols)
    if config_dict["inputs"].get("Column_name"):
        col_name = config_dict["inputs"]["Column_name"]
    else:
        col_name = ""

    if config_dict.get("method_parameter"):
        method_parameter = config_dict["method_parameter"]
    else:
        method_parameter = "Pandas"

    if sub_operation == "Addition":
        if data_choice == "Custom_input":
            number = float(config_dict["inputs"]["Number"])
            output_data = mathOps_Func.add_fn(dataframe, col1, col_name, number)
        elif data_choice == "Dataframe_input":
            output_data = mathOps_Func.add_fn(dataframe, col_list, col_name)
        return output_data

    if sub_operation == "Column sum" or sub_operation == "Row sum" or sub_operation == "Cell sum":
        sum_type = config_dict["inputs"]["Other_Inputs"]["Type_choice"]

        if config_dict["inputs"]["Other_Inputs"].get("Cell_11"):
            Cell_11 = config_dict["inputs"]["Other_Inputs"]["Cell_11"][0]
        else:
            Cell_11 = ""

        if config_dict["inputs"]["Other_Inputs"].get("Cell_12"):
            Cell_12 = config_dict["inputs"]["Other_Inputs"]["Cell_12"][0]
        else:
            Cell_12 = ""

        if config_dict["inputs"]["Other_Inputs"].get("Cell_21"):
            Cell_21 = config_dict["inputs"]["Other_Inputs"]["Cell_21"][0]
        else:
            Cell_21 = ""

        if config_dict["inputs"]["Other_Inputs"].get("Cell_22"):
            Cell_22 = config_dict["inputs"]["Other_Inputs"]["Cell_22"][0]
        else:
            Cell_22 = ""

        if config_dict["inputs"]["Other_Inputs"].get("Target_1"):
            Target_1 = config_dict["inputs"]["Other_Inputs"]["Target_1"][0]
        else:
            Target_1 = ""

        if config_dict["inputs"]["Other_Inputs"].get("Target_2"):
            Target_2 = config_dict["inputs"]["Other_Inputs"]["Target_2"][0]
        else:
            Target_2 = ""

        if sum_type == "Column_Sum" or sum_type == "Row_Sum":
            col_list_new = config_dict["inputs"]["Column_1"]
        else:
            col_list_new = ""

        number = config_dict["inputs"]["Number"]
        if data_choice == "Custom_input":
            if sum_type == "Column_Sum" or sum_type == "Row_Sum":
                output_data = mathOps_Func.add_fn_eq(dataframe, col_list_new, col_name, sum_type, number)
            else:
                output_data = mathOps_Func.add_fn_eq(
                    dataframe,
                    col_list_new,
                    col_name,
                    sum_type,
                    number,
                    Cell_11,
                    Cell_12,
                    Cell_21,
                    Cell_22,
                    Target_1,
                    Target_2,
                )
        elif data_choice == "Dataframe_input":
            if sum_type == "Column_Sum" or sum_type == "Row_Sum":
                output_data = mathOps_Func.add_fn_eq(dataframe, col_list_new, col_name, sum_type)
            else:
                output_data = mathOps_Func.add_fn_eq(
                    dataframe,
                    col_list_new,
                    col_name,
                    sum_type,
                    number,
                    Cell_11,
                    Cell_12,
                    Cell_21,
                    Cell_22,
                    Target_1,
                    Target_2,
                )

        return output_data

    if sub_operation == "Subtraction":
        if data_choice == "Custom_input":
            number = float(config_dict["inputs"]["Number"])
            output_data = mathOps_Func.subtract_fn(dataframe, col1, col_name, number)
        elif data_choice == "Dataframe_input":
            output_data = mathOps_Func.subtract_fn(dataframe, col_list, col_name)
        return output_data

    if (
        sub_operation == "Column subtraction"
        or sub_operation == "Row subtraction"
        or sub_operation == "Cell subtraction"
    ):
        sum_type = config_dict["inputs"]["Other_Inputs"]["Type_choice"]

        if config_dict["inputs"]["Other_Inputs"].get("Cell_11"):
            Cell_11 = config_dict["inputs"]["Other_Inputs"]["Cell_11"][0]
        else:
            Cell_11 = ""

        if config_dict["inputs"]["Other_Inputs"].get("Cell_12"):
            Cell_12 = config_dict["inputs"]["Other_Inputs"]["Cell_12"][0]
        else:
            Cell_12 = ""

        if config_dict["inputs"]["Other_Inputs"].get("Cell_21"):
            Cell_21 = config_dict["inputs"]["Other_Inputs"]["Cell_21"][0]
        else:
            Cell_21 = ""

        if config_dict["inputs"]["Other_Inputs"].get("Cell_22"):
            Cell_22 = config_dict["inputs"]["Other_Inputs"]["Cell_22"][0]
        else:
            Cell_22 = ""

        if config_dict["inputs"]["Other_Inputs"].get("Target_1"):
            Target_1 = config_dict["inputs"]["Other_Inputs"]["Target_1"][0]
        else:
            Target_1 = ""

        if config_dict["inputs"]["Other_Inputs"].get("Target_2"):
            Target_2 = config_dict["inputs"]["Other_Inputs"]["Target_2"][0]
        else:
            Target_2 = ""

        if sum_type == "Column_Sum" or sum_type == "Row_Sum":
            col_list_new = config_dict["inputs"]["Column_1"]
        else:
            col_list_new = ""

        number = config_dict["inputs"]["Number"]
        if data_choice == "Custom_input":
            if sum_type == "Column_Sum" or sum_type == "Row_Sum":
                output_data = mathOps_Func.subtract_fn_eq(dataframe, col_list_new, col_name, sum_type, number)
            else:
                output_data = mathOps_Func.subtract_fn_eq(
                    dataframe,
                    col_list_new,
                    col_name,
                    sum_type,
                    number,
                    Cell_11,
                    Cell_12,
                    Cell_21,
                    Cell_22,
                    Target_1,
                    Target_2,
                )
        elif data_choice == "Dataframe_input":
            if sum_type == "Column_Sum" or sum_type == "Row_Sum":
                output_data = mathOps_Func.subtract_fn_eq(dataframe, col_list_new, col_name, sum_type)
            else:
                output_data = mathOps_Func.subtract_fn_eq(
                    dataframe,
                    col_list_new,
                    col_name,
                    sum_type,
                    number,
                    Cell_11,
                    Cell_12,
                    Cell_21,
                    Cell_22,
                    Target_1,
                    Target_2,
                )
        return output_data

    if sub_operation == "Multiplication":
        if data_choice == "Custom_input":
            number = float(config_dict["inputs"]["Number"])
            output_data = mathOps_Func.multiply_fn(dataframe, col1, col_name, number)
        elif data_choice == "Dataframe_input":
            output_data = mathOps_Func.multiply_fn(dataframe, col_list, col_name)
        return output_data

    if (
        sub_operation == "Column multiplication"
        or sub_operation == "Row multiplication"
        or sub_operation == "Cell multiplication"
    ):
        sum_type = config_dict["inputs"]["Other_Inputs"]["Type_choice"]

        if config_dict["inputs"]["Other_Inputs"].get("Cell_11"):
            Cell_11 = config_dict["inputs"]["Other_Inputs"]["Cell_11"][0]
        else:
            Cell_11 = ""

        if config_dict["inputs"]["Other_Inputs"].get("Cell_12"):
            Cell_12 = config_dict["inputs"]["Other_Inputs"]["Cell_12"][0]
        else:
            Cell_12 = ""

        if config_dict["inputs"]["Other_Inputs"].get("Cell_21"):
            Cell_21 = config_dict["inputs"]["Other_Inputs"]["Cell_21"][0]
        else:
            Cell_21 = ""

        if config_dict["inputs"]["Other_Inputs"].get("Cell_22"):
            Cell_22 = config_dict["inputs"]["Other_Inputs"]["Cell_22"][0]
        else:
            Cell_22 = ""

        if config_dict["inputs"]["Other_Inputs"].get("Target_1"):
            Target_1 = config_dict["inputs"]["Other_Inputs"]["Target_1"][0]
        else:
            Target_1 = ""

        if config_dict["inputs"]["Other_Inputs"].get("Target_2"):
            Target_2 = config_dict["inputs"]["Other_Inputs"]["Target_2"][0]
        else:
            Target_2 = ""

        if sum_type == "Column_Sum" or sum_type == "Row_Sum":
            col_list_new = config_dict["inputs"]["Column_1"]
        else:
            col_list_new = ""

        number = config_dict["inputs"]["Number"]
        if data_choice == "Custom_input":
            if sum_type == "Column_Sum" or sum_type == "Row_Sum":
                output_data = mathOps_Func.multiply_fn_eq(dataframe, col_list_new, col_name, sum_type, number)
            else:
                output_data = mathOps_Func.multiply_fn_eq(
                    dataframe,
                    col_list_new,
                    col_name,
                    sum_type,
                    number,
                    Cell_11,
                    Cell_12,
                    Cell_21,
                    Cell_22,
                    Target_1,
                    Target_2,
                )
        elif data_choice == "Dataframe_input":
            if sum_type == "Column_Sum" or sum_type == "Row_Sum":
                output_data = mathOps_Func.multiply_fn_eq(dataframe, col_list_new, col_name, sum_type)
            else:
                output_data = mathOps_Func.multiply_fn_eq(
                    dataframe,
                    col_list_new,
                    col_name,
                    sum_type,
                    number,
                    Cell_11,
                    Cell_12,
                    Cell_21,
                    Cell_22,
                    Target_1,
                    Target_2,
                )
        return output_data

    if sub_operation == "Division":
        if data_choice == "Custom_input":
            number = float(config_dict["inputs"]["Number"])
            output_data = mathOps_Func.division_fn(dataframe, col1, col_name, number)
        elif data_choice == "Dataframe_input":
            output_data = mathOps_Func.division_fn(dataframe, col_list, col_name)
        return output_data

    if (
        sub_operation == "Column division"
        or sub_operation == "Row division"
        or sub_operation == "Cell division"
    ):
        sum_type = config_dict["inputs"]["Other_Inputs"]["Type_choice"]

        if config_dict["inputs"]["Other_Inputs"].get("Cell_11"):
            Cell_11 = config_dict["inputs"]["Other_Inputs"]["Cell_11"][0]
        else:
            Cell_11 = ""

        if config_dict["inputs"]["Other_Inputs"].get("Cell_12"):
            Cell_12 = config_dict["inputs"]["Other_Inputs"]["Cell_12"][0]
        else:
            Cell_12 = ""

        if config_dict["inputs"]["Other_Inputs"].get("Cell_21"):
            Cell_21 = config_dict["inputs"]["Other_Inputs"]["Cell_21"][0]
        else:
            Cell_21 = ""

        if config_dict["inputs"]["Other_Inputs"].get("Cell_22"):
            Cell_22 = config_dict["inputs"]["Other_Inputs"]["Cell_22"][0]
        else:
            Cell_22 = ""

        if config_dict["inputs"]["Other_Inputs"].get("Target_1"):
            Target_1 = config_dict["inputs"]["Other_Inputs"]["Target_1"][0]
        else:
            Target_1 = ""

        if config_dict["inputs"]["Other_Inputs"].get("Target_2"):
            Target_2 = config_dict["inputs"]["Other_Inputs"]["Target_2"][0]
        else:
            Target_2 = ""

        if sum_type == "Column_Sum" or sum_type == "Row_Sum":
            col_list_new = config_dict["inputs"]["Column_1"]
        else:
            col_list_new = ""

        number = config_dict["inputs"]["Number"]
        if data_choice == "Custom_input":
            if sum_type == "Column_Sum" or sum_type == "Row_Sum":
                output_data = mathOps_Func.division_fn_eq(dataframe, col_list_new, col_name, sum_type, number)
            else:
                output_data = mathOps_Func.division_fn_eq(
                    dataframe,
                    col_list_new,
                    col_name,
                    sum_type,
                    number,
                    Cell_11,
                    Cell_12,
                    Cell_21,
                    Cell_22,
                    Target_1,
                    Target_2,
                )
        elif data_choice == "Dataframe_input":
            if sum_type == "Column_Sum" or sum_type == "Row_Sum":
                output_data = mathOps_Func.division_fn_eq(dataframe, col_list_new, col_name, sum_type)
            else:
                output_data = mathOps_Func.division_fn_eq(
                    dataframe,
                    col_list_new,
                    col_name,
                    sum_type,
                    number,
                    Cell_11,
                    Cell_12,
                    Cell_21,
                    Cell_22,
                    Target_1,
                    Target_2,
                )
        return output_data

    if sub_operation == "Sum_Product":
        output_data = mathOps_Func.sumproduct_fn(dataframe, col_list)
        return output_data

    if sub_operation == "Ceiling":
        if method_parameter == "Pandas":
            multiple = config_dict["inputs"]["Other_Inputs"]["Signif_Multiple"]
            output_data = mathOps_Func.ceil_fn(dataframe, col1, col_name, int(multiple))
            return output_data
        elif method_parameter == "Numba":
            col1 = dataframe[col1].to_numpy()
            data = mathOps_Func.ceil_fn_nb(col1, int(multiple))
            dataframe[str(col_name)] = data
            output_data = dataframe
            return output_data

    if sub_operation == "Floor":
        if method_parameter == "Pandas":
            multiple = config_dict["inputs"]["Other_Inputs"]["Signif_Multiple"]
            output_data = mathOps_Func.floor_fn(dataframe, col1, col_name, int(multiple))
            return output_data
        elif method_parameter == "Numba":
            multiple = config_dict["inputs"]["Other_Inputs"]["Signif_Multiple"]
            col1 = dataframe[col1].to_numpy()
            data = mathOps_Func.floor_fn_nb(col1, int(multiple))
            dataframe[str(col_name)] = data
            output_data = dataframe
            return output_data

    if sub_operation == "Odd":
        output_choice = config_dict["inputs"]["Other_Inputs"]["Output_choice"]
        if output_choice == "Yes_replace":
            output_data = mathOps_Func.round_odd_fn(dataframe, col1, output_choice)
        else:
            output_data = mathOps_Func.round_odd_fn(dataframe, col1, output_choice, col_name)
        return output_data

    if sub_operation == "Even":
        output_choice = config_dict["inputs"]["Other_Inputs"]["Output_choice"]
        if output_choice == "Yes_replace":
            output_data = mathOps_Func.round_even_fn(dataframe, col1, output_choice)
        else:
            output_data = mathOps_Func.round_even_fn(dataframe, col1, output_choice, col_name)
        return output_data

    if sub_operation == "Round":
        output_choice = config_dict["inputs"]["Other_Inputs"]["Output_choice"]
        decimal = config_dict["inputs"]["Other_Inputs"]["Decimal"]
        if output_choice == "Yes_replace":
            output_data = mathOps_Func.round_fn(dataframe, col1, int(decimal), output_choice)
        else:
            output_data = mathOps_Func.round_fn(dataframe, col1, int(decimal), output_choice, col_name)
        return output_data

    if sub_operation == "Round_Up":
        output_choice = config_dict["inputs"]["Other_Inputs"]["Output_choice"]
        if output_choice == "Yes_replace":
            output_data = mathOps_Func.roundup_fn(dataframe, col1, output_choice)
        else:
            output_data = mathOps_Func.roundup_fn(dataframe, col1, output_choice, col_name)
        return output_data

    if sub_operation == "Round_Down":
        output_choice = config_dict["inputs"]["Other_Inputs"]["Output_choice"]
        if output_choice == "Yes_replace":
            output_data = mathOps_Func.rounddown_fn(dataframe, col1, output_choice)
        else:
            output_data = mathOps_Func.rounddown_fn(dataframe, col1, output_choice, col_name)
        return output_data

    if sub_operation == "Truncate":
        output_choice = config_dict["inputs"]["Other_Inputs"]["Output_choice"]
        if output_choice == "Yes_replace":
            output_data = mathOps_Func.truncate_fn(dataframe, col1, output_choice)
        else:
            output_data = mathOps_Func.truncate_fn(dataframe, col1, output_choice, col_name)
        return output_data

    if sub_operation == "Natural_Log":
        if method_parameter == "Pandas":
            output_data = mathOps_Func.log_natural_fn(dataframe, col1, col_name)
            return output_data

        elif method_parameter == "Numba":
            col1 = dataframe[col1].to_numpy()
            data = mathOps_Func.log_natural_fn_nb(col1)
            dataframe[str(col_name)] = data
            output_data = dataframe
            return output_data

    if sub_operation == "Log_base":
        base = config_dict["inputs"]["Other_Inputs"]["Log_Base"]
        output_data = mathOps_Func.log_fn(dataframe, col1, int(base), col_name)
        return output_data

    if sub_operation == "Exponential":
        output_data = mathOps_Func.exponential_fn(dataframe, col1, col_name)
        return output_data

    if sub_operation == "Power":
        power_val = config_dict["inputs"]["Other_Inputs"]["Power"]
        output_data = mathOps_Func.power_fn(dataframe, col1, float(power_val), col_name)
        return output_data

    if sub_operation == "Square_Root":
        if method_parameter == "Pandas":
            output_data = mathOps_Func.square_root_fn(dataframe, col1, col_name)
            return output_data

        elif method_parameter == "Numba":
            col1 = dataframe[col1].to_numpy()
            data = mathOps_Func.square_root_fn_nb(col1)
            dataframe[str(col_name)] = data
            output_data = dataframe
            return output_data

    if sub_operation == "Square_Root_Pi":
        if method_parameter == "Pandas":
            output_data = mathOps_Func.square_root_pi_fn(dataframe, col1, col_name)
            return output_data

        elif method_parameter == "Numba":
            col1 = dataframe[col1].to_numpy()
            data = mathOps_Func.square_root_pi_fn_nb(col1)
            dataframe[str(col_name)] = data
            output_data = dataframe
            return output_data

    if sub_operation == "Random":
        output_data = mathOps_Func.rand_fn(dataframe, col_name)
        return output_data

    if sub_operation == "Random_Between":
        lower_lim = config_dict["inputs"]["Other_Inputs"]["Rand_Lower_Limit"]
        upper_lim = config_dict["inputs"]["Other_Inputs"]["Rand_Up_Limit"]
        output_data = mathOps_Func.rand_between_fn(dataframe, lower_lim, upper_lim, col_name)
        return output_data

    if sub_operation == "SUMSQ":
        if method_parameter == "Pandas":
            output_data = mathOps_Func.sum_squares_fn(dataframe, col1, col2, col_name)
            return output_data
        elif method_parameter == "Numba":
            col1 = dataframe[col1].to_numpy()
            col2 = dataframe[col2].to_numpy()
            data = mathOps_Func.sum_squares_fn_nb(col1, col2)
            dataframe[str(col_name)] = data
            output_data = dataframe
            return output_data

    if sub_operation == "SUMX2MY2":
        if method_parameter == "Pandas":
            output_data = mathOps_Func.sumx2my2_fn(dataframe, col1, col2)
            return output_data
        elif method_parameter == "Numba":
            col1 = dataframe[col1].to_numpy()
            col2 = dataframe[col2].to_numpy()
            data = mathOps_Func.sumx2my2_fn_nb(col1, col2)
            output_data = pd.DataFrame([data], columns=["Total Sum of the Difference of Squared Numbers"])
            return output_data

    if sub_operation == "SUMX2PY2":
        if method_parameter == "Pandas":
            output_data = mathOps_Func.sumx2py2_fn(dataframe, col1, col2)
            return output_data

        elif method_parameter == "Numba":
            col1 = dataframe[col1].to_numpy()
            col2 = dataframe[col2].to_numpy()
            data = mathOps_Func.sumx2py2_fn_nb(col1, col2)
            output_data = pd.DataFrame([data], columns=["Total Sum of the Sum of Squared Numbers"])
            return output_data

    if sub_operation == "SUMXMY2":
        if method_parameter == "Pandas":
            output_data = mathOps_Func.sumxmy2_fn(dataframe, col1, col2)
            return output_data

        elif method_parameter == "Numba":
            col1 = dataframe[col1].to_numpy()
            col2 = dataframe[col2].to_numpy()
            data = mathOps_Func.sumxmy2_fn_nb(col1, col2)
            output_data = pd.DataFrame([data], columns=["Sum of Squared Differences"])
            return output_data

    if sub_operation == "MDETERM":
        if method_parameter == "Pandas":
            output_data = mathOps_Func.matrix_determinant(dataframe)
            return output_data

        elif method_parameter == "Numba":
            sub = np.asmatrix(dataframe)
            data = mathOps_Func.matrix_determinant_nb(sub)
            output_data = pd.DataFrame(data, columns=["Matrix Determinant"])
            return output_data

    if sub_operation == "MINVERSE":
        if method_parameter == "Pandas":
            output_data = mathOps_Func.matrix_inverse(dataframe)
            return output_data

        elif method_parameter == "Numba":
            sub = np.asmatrix(dataframe)
            data = mathOps_Func.matrix_inverse_nb(sub)
            output_data = pd.DataFrame(data)
            return output_data

    if sub_operation == "MMULT":
        if method_parameter == "Pandas":
            dataframe1 = dataframe[0]
            dataframe2 = dataframe[1]
            output_data = mathOps_Func.matrix_mul(dataframe1, dataframe2)
            return output_data
        elif method_parameter == "Numba":
            dataframe1 = dataframe[0]
            dataframe2 = dataframe[1]
            m1 = np.asmatrix(dataframe1)
            m2 = np.asmatrix(dataframe2)
            data = mathOps_Func.matrix_mul_nb(m1, m2)
            output_data = pd.DataFrame(data)
            return output_data

    if sub_operation == "MUNIT":
        matrix_size = config_dict["inputs"]["Other_Inputs"]["Matrix_Size"]
        output_data = mathOps_Func.matrix_identity(int(matrix_size))
        return output_data

    if sub_operation == "Absolute":
        if method_parameter == "Pandas":
            output_data = mathOps_Func.absolute_fn(dataframe, col1)
            return output_data

        elif method_parameter == "Numba":
            a = str(col1)
            col1 = dataframe[col1].to_numpy()
            data = mathOps_Func.absolute_fn_nb(col1)
            dataframe[a] = data
            output_data = dataframe
            return output_data

    if sub_operation == "Factorial":
        output_data = mathOps_Func.factorial_fn(dataframe, col1, col_name)
        return output_data

    if sub_operation == "Sign":
        if method_parameter == "Pandas":
            output_data = mathOps_Func.sign_fn(dataframe, col1, col_name)
            return output_data

        elif method_parameter == "Numba":
            col1 = dataframe[col1].to_numpy()
            data = mathOps_Func.sign_fn_nb(col1)
            dataframe[str(col_name)] = data
            output_data = dataframe
            return output_data

    if sub_operation == "Mod":
        if method_parameter == "Pandas":
            divisor = config_dict["inputs"]["Other_Inputs"]["Divisor"]
            output_data = mathOps_Func.mod_fn(dataframe, col1, int(divisor), col_name)
            return output_data

        elif method_parameter == "Numba":
            divisor = config_dict["inputs"]["Other_Inputs"]["Divisor"]
            col1 = dataframe[col1].to_numpy()
            data = mathOps_Func.mod_fn_nb(col1, int(divisor))
            dataframe[str(col_name)] = data
            output_data = dataframe
            return output_data

    if sub_operation == "Quotient":
        if method_parameter == "Pandas":
            divisor = config_dict["inputs"]["Other_Inputs"]["Divisor"]
            output_data = mathOps_Func.quotient_fn(dataframe, col1, int(divisor), col_name)
            return output_data

        elif method_parameter == "Numba":
            divisor = config_dict["inputs"]["Other_Inputs"]["Divisor"]
            col1 = dataframe[col1].to_numpy()
            data = mathOps_Func.quotient_fn_nb(col1, int(divisor))
            dataframe[str(col_name)] = data
            output_data = dataframe
            return output_data
