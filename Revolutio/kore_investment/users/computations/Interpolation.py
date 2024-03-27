from math import exp, log


def Curve_interpolation(x, y, independent_var_value, interpolation_convention):
    if interpolation_convention == "Linear":
        n = len(x)
        if type(independent_var_value) == float or type(independent_var_value) == int:
            for j in range(1, n):
                if (x[j - 1]) < independent_var_value < (x[j]):
                    return y[j - 1] + (
                        (y[j] - y[j - 1]) * (independent_var_value - x[j - 1]) / (x[j] - x[j - 1])
                    )
                elif independent_var_value <= 0:
                    return 0
                elif independent_var_value <= x[0]:
                    return y[0]
                elif independent_var_value >= x[-1]:
                    return y[-1]
        else:
            return "invalid input"

    # Exponential Interpolation
    if interpolation_convention == "Exponential":
        n = len(x)
        if type(independent_var_value) == float or type(independent_var_value) == int:
            for j in range(1, n):
                if (x[j - 1]) < independent_var_value < (x[j]):
                    return exp(
                        log(y[j - 1])
                        + (
                            (log(y[j]) - log(y[j - 1]))
                            * (independent_var_value - x[j - 1])
                            / (x[j] - x[j - 1])
                        )
                    )
        else:
            return "invalid input"
