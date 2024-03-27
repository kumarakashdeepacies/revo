import numpy as np
import pandas as pd
import scipy
from scipy.stats import mvn, norm


class Black_Scholes:
    """
    This class contains option pricing and greeks of the European call and put options
    """

    def __init__(self, S, K, T, r, div, sigma):
        """
        Args:
            S - spot price
            K - strike price
            T - time to maturity
            r - risk-free rate
            div - rate of continuous dividend
            sigma - volatility

            #Only for delta, rho and phi:
            put_call_type - 'call' or 'put'
        Returns the option price estimated by the black-scholes model and the options greeks
        """
        self.S = S
        self.K = K
        self.T = T
        self.r = r
        self.div = div
        self.sigma = sigma
        self.d1 = (np.log(self.S / self.K) + (self.r - self.div + 0.5 * self.sigma**2) * self.T) / (
            self.sigma * np.sqrt(self.T)
        )
        self.d2 = (np.log(self.S / self.K) + (self.r - self.div - 0.5 * self.sigma**2) * self.T) / (
            self.sigma * np.sqrt(self.T)
        )

    def call(self):
        result = self.S * np.exp(-self.div * self.T) * norm.cdf(self.d1, 0.0, 1.0) - self.K * np.exp(
            -self.r * self.T
        ) * norm.cdf(self.d2, 0.0, 1.0)
        return result

    def put(self):
        result = -self.S * np.exp(-self.div * self.T) * norm.cdf(-self.d1, 0.0, 1.0) + self.K * np.exp(
            -self.r * (self.T)
        ) * norm.cdf(-self.d2)
        return result

    # put_call_type - 'call' or 'put'

    def delta(self, put_call_type):

        if put_call_type == ("call"):
            return np.exp(-self.div * self.T) * norm.cdf(self.d1, 0.0, 1.0)

        elif put_call_type == ("put"):
            return np.exp(-self.div * self.T) * (norm.cdf(self.d1, 0.0, 1.0) - 1)

    def gamma(self):
        return (
            1
            / (self.S * self.sigma * np.sqrt(self.T))
            * norm.pdf(self.d1, 0.0, 1.0)
            * np.exp(-self.div * self.T)
        )

    def vega(self):
        return self.S * norm.pdf(self.d1, 0.0, 1.0) * np.sqrt(self.T) * np.exp(-self.div * self.T)

    def rho(self, put_call_type):
        if put_call_type == ("call"):
            return self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(self.d2, 0.0, 1.0)

        elif put_call_type == ("put"):
            return -self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(-self.d2, 0.0, 1.0)

    def vanna(self):
        return (
            np.sqrt(self.T)
            * norm.pdf(self.d1, 0.0, 1.0)
            * (self.d2 / self.sigma)
            * np.exp(-self.div * self.T)
        )

    def phi(self, put_call_type):
        if put_call_type == ("call"):
            return -self.T * np.exp(-self.div * self.T) * self.S * norm.cdf(self.d1, 0.0, 1.0)
        if put_call_type == ("put"):
            return self.T * np.exp(-self.div * self.T) * self.S * norm.cdf(-self.d1, 0.0, 1.0)


class Binomial_Tree:
    """
    This class contains option pricing and greeks of the American call and put options
    """

    def __init__(self, n, S, K, T, r, q, sigma):
        """
        Args:
            n - number of steps
            S - spot price
            K - strike price
            T - time to maturity
            r - risk-free rate
            q - dividend yield
            sigma - volatility

            put_call_type - 'call' or 'put'
        Returns the option price estimated by the binomial tree model and the options greeks
        """
        self.n = n
        self.S = S
        self.K = K
        self.T = T
        self.r = r
        self.q = q
        self.sigma = sigma
        self.dt = self.T / self.n
        self.u = np.exp(self.sigma * np.sqrt(self.dt))
        self.d = 1.0 / self.u
        self.p = (np.exp((self.r - self.q) * self.dt) - self.d) / (self.u - self.d)
        self.d1 = (np.log(self.S / self.K) + (self.r - self.q + 0.5 * self.sigma**2) * self.T) / (
            self.sigma * np.sqrt(self.T)
        )
        self.d2 = (np.log(self.S / self.K) + (self.r - self.q - 0.5 * self.sigma**2) * self.T) / (
            self.sigma * np.sqrt(self.T)
        )

    def binomial(self, put_call_type):
        # put_call_type - 'call' or 'put'
        stockvalue = np.zeros((self.n + 1, self.n + 1))
        stockvalue[0, 0] = self.S
        for i in range(1, self.n + 1):
            stockvalue[i, 0] = stockvalue[i - 1, 0] * self.u
            for j in range(1, i + 1):
                stockvalue[i, j] = stockvalue[i - 1, j - 1] * self.d
        optionvalue = np.zeros((self.n + 1, self.n + 1))
        for j in range(self.n + 1):
            if put_call_type == "call":
                optionvalue[self.n, j] = max(0, stockvalue[self.n, j] - self.K)
            elif put_call_type == "put":
                optionvalue[self.n, j] = max(0, self.K - stockvalue[self.n, j])
        for i in range(self.n - 1, -1, -1):
            for j in range(i + 1):
                if put_call_type == "put":
                    optionvalue[i, j] = max(
                        0,
                        self.K - stockvalue[i, j],
                        np.exp(-self.r * self.dt)
                        * (self.p * optionvalue[i + 1, j] + (1 - self.p) * optionvalue[i + 1, j + 1]),
                    )
                elif put_call_type == "call":
                    optionvalue[i, j] = max(
                        0,
                        stockvalue[i, j] - self.K,
                        np.exp(-self.r * self.dt)
                        * (self.p * optionvalue[i + 1, j] + (1 - self.p) * optionvalue[i + 1, j + 1]),
                    )
        return optionvalue[0, 0]

    def delta(self, put_call_type):

        if put_call_type == ("call"):
            return norm.cdf(self.d1, 0.0, 1.0)

        elif put_call_type == ("put"):
            return norm.cdf(self.d1, 0.0, 1.0) - 1

    def gamma(self):
        return 1 / (self.S * self.sigma * np.sqrt(self.T)) * norm.pdf(self.d1, 0.0, 1.0)

    def vega(self):
        return self.S * norm.pdf(self.d1, 0.0, 1.0) * np.sqrt(self.T)

    def rho(self, put_call_type):
        if put_call_type == ("call"):
            return self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(self.d2, 0.0, 1.0)

        elif put_call_type == ("put"):
            return -self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(-self.d2, 0.0, 1.0)

    def vanna(self):
        return np.sqrt(self.T) * norm.pdf(self.d1, 0.0, 1.0) * (self.d2 / self.sigma)

    def phi(self, put_call_type):
        if put_call_type == ("call"):
            return -self.T * self.S * norm.cdf(self.d1, 0.0, 1.0)
        if put_call_type == ("put"):
            return self.T * self.S * norm.cdf(-self.d1, 0.0, 1.0)


class Barrier_Option:
    """
    This class contains option pricing and greeks of the Barrier (Knock-in/Knock-out) call and put options
    """

    def __init__(self, S, K, T, r, div, sigma, barrier, barrier_hit_status="No", rebate=0):
        """
        Args:
            S - spot price
            K - strike price
            T - time to maturity
            r - risk-free rate
            div - continuous dividend payout
            sigma - volatility
            barrier - barrier price
            barrier_hit_status - whether the barrier level has already been breached
            rebate - rebate of barrier option (default=0 as in no rebate provision)
            put_call_type - 'call' or 'put'
        Returns the option price estimated by the modified Black-Scholes model and the options greeks
        """
        self.S = S
        self.K = K
        self.r = r
        self.Z = barrier
        self.T = T
        self.sigma = sigma
        self.div = div
        self.barrier_hit_status = barrier_hit_status
        self.R = rebate

        self.d1 = (np.log(self.S / self.K) + (self.r - self.div + 0.5 * self.sigma**2) * self.T) / (
            self.sigma * np.sqrt(self.T)
        )
        self.d2 = (np.log(self.S / self.K) + (self.r - self.div - 0.5 * self.sigma**2) * self.T) / (
            self.sigma * np.sqrt(self.T)
        )
        self._mu = self._mean()

    def _mean(self):
        mu = (self.r - self.div - self.sigma * self.sigma * 0.5) / (self.sigma**2)
        return mu

    def _x2val(self):
        x = np.log(self.S / self.Z) / (self.sigma * np.sqrt(self.T)) + (self._mu + 1) * self.sigma * np.sqrt(
            self.T
        )
        return x

    def _x1val(self):
        x = np.log(self.S / self.K) / (self.sigma * np.sqrt(self.T)) + (self._mu + 1) * self.sigma * np.sqrt(
            self.T
        )
        return x

    def _y2val(self):
        y = np.log(self.Z / self.S) / (self.sigma * np.sqrt(self.T)) + (self._mu + 1) * self.sigma * np.sqrt(
            self.T
        )
        return y

    def _y1val(self):
        y = np.log(np.square(self.Z) / (self.S * self.K)) / (self.sigma * np.sqrt(self.T)) + (
            self._mu + 1
        ) * self.sigma * np.sqrt(self.T)
        return y

    def _zval(self):
        z = np.log(self.Z / self.S) / (self.sigma * np.sqrt(self.T)) + self._lambda() * self.sigma * np.sqrt(
            self.T
        )
        return z

    def _lambda(self):
        l = np.sqrt(self._mu**2 + ((2 * self.r) / (self.sigma * self.sigma)))
        return l

    def _I1(self, alpha: int, beta: int):
        xval = self._x1val()
        partial = alpha * self.S * np.exp(-self.div * self.T) * norm.cdf(
            alpha * xval
        ) - alpha * self.K * np.exp(-1 * self.r * self.T) * norm.cdf(
            alpha * xval - alpha * self.sigma * np.sqrt(self.T)
        )
        return partial

    def _I2(self, alpha: int, beta: int):
        xval = self._x2val()
        partial = alpha * self.S * np.exp(-self.div * self.T) * norm.cdf(
            alpha * xval
        ) - alpha * self.K * np.exp(-1 * self.r * self.T) * norm.cdf(
            alpha * xval - alpha * self.sigma * np.sqrt(self.T)
        )
        return partial

    def _I3(self, alpha: int, beta: int):
        yval = self._y1val()
        partial = alpha * self.S * np.exp(-self.div * self.T) * np.power(
            self.Z / self.S, 2 * (self._mu + 1)
        ) * norm.cdf(beta * yval) - alpha * self.K * np.exp(-1 * self.r * self.T) * np.power(
            self.Z / self.S, 2 * self._mu
        ) * norm.cdf(
            beta * yval - beta * self.sigma * np.sqrt(self.T)
        )
        return partial

    def _I4(self, alpha: int, beta: int):
        yval = self._y2val()
        partial = alpha * self.S * np.exp(-self.div * self.T) * np.power(
            self.Z / self.S, 2 * (self._mu + 1)
        ) * norm.cdf(beta * yval) - alpha * self.K * np.exp(-1 * self.r * self.T) * np.power(
            self.Z / self.S, 2 * self._mu
        ) * norm.cdf(
            beta * yval - beta * self.sigma * np.sqrt(self.T)
        )
        return partial

    def _I5(self, beta: int):
        x = self._x2val()
        y = self._y2val()
        partial = (
            self.R
            * np.exp(-1 * self.r * self.T)
            * (
                norm.cdf(beta * x - beta * self.sigma * np.sqrt(self.T))
                - np.power(self.Z / self.S, 2 * self._mu)
                * norm.cdf(beta * y - beta * self.sigma * np.sqrt(self.T))
            )
        )
        return partial

    def _I6(self, beta: int):
        l = self._lambda()
        z = self._zval()
        partial = self.R * (
            np.power(self.Z / self.S, self._mu + l) * norm.cdf(beta * z)
            + np.power(self.Z / self.S, self._mu - l)
            * norm.cdf(beta * z - 2 * beta * l * self.sigma * np.sqrt(self.T))
        )
        return partial

    def vanilla_call(self):
        result = self.S * np.exp(-self.div * self.T) * norm.cdf(self.d1, 0.0, 1.0) - self.K * np.exp(
            -self.r * self.T
        ) * norm.cdf(self.d2, 0.0, 1.0)
        return result

    def vanilla_put(self):
        result = -self.S * np.exp(-self.div * self.T) * norm.cdf(-self.d1, 0.0, 1.0) + self.K * np.exp(
            -self.r * (self.T)
        ) * norm.cdf(-self.d2)
        return result

    def down_out_put(self):
        a = -1
        b = 1

        if self.S <= self.Z or self.barrier_hit_status == "Yes":
            price = self.R * np.exp(-self.r * (self.T))
        elif self.K > self.Z and self.S > self.Z:
            price = self._I1(a, b) - self._I2(a, b) + self._I3(a, b) - self._I4(a, b) + self._I6(b)
        elif self.K < self.Z and self.S > self.Z:
            price = self._I6(b)
        else:
            price = 0.0
        return max(price, 0.0)

    def down_out_call(self):
        a = 1
        b = 1

        if self.S <= self.Z or self.barrier_hit_status == "Yes":
            price = self.R * np.exp(-self.r * (self.T))
        elif self.K > self.Z and self.S > self.Z:
            price = self._I1(a, b) - self._I3(a, b) + self._I6(b)
        elif self.K < self.Z and self.S > self.Z:
            price = self._I2(a, b) - self._I4(a, b) + self._I6(b)
        else:
            price = 0.0
        return max(price, 0.0)

    def up_out_call(self):
        a = 1
        b = -1

        if self.S >= self.Z or self.barrier_hit_status == "Yes":
            price = self.R * np.exp(-self.r * (self.T))
        elif self.K < self.Z and self.S < self.Z:
            price = self._I1(a, b) - self._I2(a, b) + self._I3(a, b) - self._I4(a, b) + self._I6(b)
        elif self.K > self.Z and self.S < self.Z:
            price = self._I6(b)
        else:
            price = 0.0
        return max(price, 0.0)

    def up_out_put(self):
        a = -1
        b = -1

        if self.S >= self.Z or self.barrier_hit_status == "Yes":
            price = self.R * np.exp(-self.r * (self.T))
        elif self.K < self.Z and self.S < self.Z:
            price = self._I1(a, b) - self._I3(a, b) + self._I6(b)
        elif self.K > self.Z and self.S < self.Z:
            price = self._I2(a, b) - self._I4(a, b) + self._I6(b)
        else:
            price = 0.0
        return max(price, 0.0)

    def down_in_call(self):
        a = 1
        b = 1

        if self.S <= self.Z or self.barrier_hit_status == "Yes":
            price = self.vanilla_call()
        elif self.K > self.Z:
            price = self._I3(a, b) + self._I5(b)
        elif self.K < self.Z:
            price = self._I1(a, b) - self._I2(a, b) + self._I4(a, b) + self._I5(b)
        else:
            price = 0.0
        return max(price, 0.0)

    def down_in_put(self):
        a = -1
        b = 1

        if self.S <= self.Z or self.barrier_hit_status == "Yes":
            price = self.vanilla_put()
        elif self.K > self.Z:
            price = self._I2(a, b) - self._I3(a, b) + self._I4(a, b) + self._I5(b)
        elif self.K < self.Z:
            price = self._I1(a, b) + self._I5(b)
        else:
            price = 0.0
        return max(price, 0.0)

    def up_in_call(self):
        a = 1
        b = -1

        if self.S >= self.Z or self.barrier_hit_status == "Yes":
            price = self.vanilla_call()
        elif self.K > self.Z:
            price = self._I1(a, b) + self._I5(b)
        elif self.K < self.Z:
            price = self._I2(a, b) - self._I3(a, b) + self._I4(a, b) + self._I5(b)
        else:
            price = 0.0
        return max(price, 0.0)

    def up_in_put(self):
        a = -1
        b = -1

        if self.S >= self.Z or self.barrier_hit_status == "Yes":
            price = self.vanilla_put()
        elif self.K > self.Z:
            price = self._I1(a, b) - self._I2(a, b) + self._I4(a, b) + self._I5(b)
        elif self.K < self.Z:
            price = self._I3(a, b) + self._I5(b)
        else:
            price = 0.0
        return max(price, 0.0)

    def delta(self, put_call_type):

        if put_call_type == ("call"):
            return norm.cdf(self.d1, 0.0, 1.0)

        elif put_call_type == ("put"):
            return norm.cdf(self.d1, 0.0, 1.0) - 1

    def gamma(self):
        return 1 / (self.S * self.sigma * np.sqrt(self.T)) * norm.pdf(self.d1, 0.0, 1.0)

    def vega(self):
        return self.S * norm.pdf(self.d1, 0.0, 1.0) * np.sqrt(self.T)

    def rho(self, put_call_type):
        if put_call_type == ("call"):
            return self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(self.d2, 0.0, 1.0)

        elif put_call_type == ("put"):
            return -self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(-self.d2, 0.0, 1.0)

    def vanna(self):
        return np.sqrt(self.T) * norm.pdf(self.d1, 0.0, 1.0) * (self.d2 / self.sigma)

    def phi(self, put_call_type):
        if put_call_type == ("call"):
            return -self.T * self.S * norm.cdf(self.d1, 0.0, 1.0)
        if put_call_type == ("put"):
            return self.T * self.S * norm.cdf(-self.d1, 0.0, 1.0)


class Digital_Option:
    """
    This class contains option pricing and greeks of the Digital call and put options
    """

    def __init__(self, S, K, T, r, div, sigma, nominal_val=1):
        """
        Args:
            S - spot price
            K - strike price
            T - time to maturity
            r - risk-free rate
            div - rate of continuous dividend
            sigma - volatility
            nominal_val - Cash amount payable if the option expires in the money

            #Only for delta, rho and phi:
            put_call_type - 'call' or 'put'
            Returns the option price estimated by the modified black-scholes model and the options greeks
        """
        self.S = S
        self.K = K
        self.T = T
        self.r = r
        self.div = div
        self.sigma = sigma
        self.d1 = (np.log(self.S / self.K) + (self.r - self.div + 0.5 * self.sigma**2) * self.T) / (
            self.sigma * np.sqrt(self.T)
        )
        self.d2 = (np.log(self.S / self.K) + (self.r - self.div - 0.5 * self.sigma**2) * self.T) / (
            self.sigma * np.sqrt(self.T)
        )
        self.nominal_val = nominal_val

    def call(self):
        if (self.K / self.S) > 0 and (self.sigma * self.T**0.5) != 0:
            return np.exp(-1 * self.r * self.T) * norm.cdf(self.d2) * self.nominal_val
        else:
            return 0

    def put(self):
        if (self.K / self.S) > 0 and (self.sigma * self.T**0.5) != 0:
            return np.exp(-1 * self.r * self.T) * norm.cdf(-self.d2) * self.nominal_val
        else:
            return 0

    def delta(self, put_call_type):
        if put_call_type == ("call"):
            return np.exp(-self.div * self.T) * norm.cdf(self.d1, 0.0, 1.0)

        elif put_call_type == ("put"):
            return np.exp(-self.div * self.T) * (norm.cdf(self.d1, 0.0, 1.0) - 1)

    def gamma(self):
        return (
            1
            / (self.S * self.sigma * np.sqrt(self.T))
            * norm.pdf(self.d1, 0.0, 1.0)
            * np.exp(-self.div * self.T)
        )

    def vega(self):
        return self.S * norm.pdf(self.d1, 0.0, 1.0) * np.sqrt(self.T) * np.exp(-self.div * self.T)

    def rho(self, put_call_type):
        if put_call_type == ("call"):
            return self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(self.d2, 0.0, 1.0)

        elif put_call_type == ("put"):
            return -self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(-self.d2, 0.0, 1.0)

    def vanna(self):
        return (
            np.sqrt(self.T)
            * norm.pdf(self.d1, 0.0, 1.0)
            * (self.d2 / self.sigma)
            * np.exp(-self.div * self.T)
        )

    def phi(self, put_call_type):
        if put_call_type == ("call"):
            return -self.T * np.exp(-self.div * self.T) * self.S * norm.cdf(self.d1, 0.0, 1.0)
        if put_call_type == ("put"):
            return self.T * np.exp(-self.div * self.T) * self.S * norm.cdf(-self.d1, 0.0, 1.0)


class Asian_Option:
    """
    This class contains option pricing and greeks of the Asian call and put options
    """

    def __init__(self, S, K, T, r, sigma, Nt, div=0):
        """
        Args:
            S - spot price
            K - strike price
            T - time to maturity
            r - risk-free rate
            sigma - volatility
            Nt - time intervals (T*252 or T*365 depending on discount_daycount_convention)
            div - rate of continuous dividend (default = 0)

            #Only for price_estimate, delta, rho and phi:
            put_call_type - 'call' or 'put'
            Returns the option price estimated by the modified black-scholes model and the options greeks
        """
        self.S = S
        self.K = K
        self.T = T
        self.r = r
        self.div = div
        self.sigma = sigma
        self.Nt = Nt
        self.d1 = (np.log(self.S / self.K) + (self.r - self.div + 0.5 * self.sigma**2) * self.T) / (
            self.sigma * np.sqrt(self.T)
        )
        self.d2 = (np.log(self.S / self.K) + (self.r - self.div - 0.5 * self.sigma**2) * self.T) / (
            self.sigma * np.sqrt(self.T)
        )

    def price_estimate(self, put_call_type):

        adj_sigma = self.sigma * np.sqrt((2 * self.Nt + 1) / (6 * (self.Nt + 1)))
        rho = 0.5 * (self.r - (self.sigma**2) * 0.5 + adj_sigma**2)
        d1 = (np.log(self.S / self.K) + (rho + 0.5 * adj_sigma**2) * self.T) / (adj_sigma * np.sqrt(self.T))
        d2 = (np.log(self.S / self.K) + (rho - 0.5 * adj_sigma**2) * self.T) / (adj_sigma * np.sqrt(self.T))
        if put_call_type == "call":
            price = np.exp(-self.r * self.T) * (
                self.S * np.exp(rho * self.T) * norm.cdf(d1) - self.K * norm.cdf(d2)
            )
        elif put_call_type == "put":
            price = np.exp(-self.r * self.T) * (
                self.K * norm.cdf(-d2) - self.S * np.exp(rho * self.T) * norm.cdf(-d1)
            )
        return price

    def delta(self, put_call_type):

        if put_call_type == ("call"):
            return np.exp(-self.div * self.T) * norm.cdf(self.d1, 0.0, 1.0)

        elif put_call_type == ("put"):
            return np.exp(-self.div * self.T) * (norm.cdf(self.d1, 0.0, 1.0) - 1)

    def gamma(self):
        return (
            1
            / (self.S * self.sigma * np.sqrt(self.T))
            * norm.pdf(self.d1, 0.0, 1.0)
            * np.exp(-self.div * self.T)
        )

    def vega(self):
        return self.S * norm.pdf(self.d1, 0.0, 1.0) * np.sqrt(self.T) * np.exp(-self.div * self.T)

    def rho(self, put_call_type):
        if put_call_type == ("call"):
            return self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(self.d2, 0.0, 1.0)

        elif put_call_type == ("put"):
            return -self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(-self.d2, 0.0, 1.0)

    def vanna(self):
        return (
            np.sqrt(self.T)
            * norm.pdf(self.d1, 0.0, 1.0)
            * (self.d2 / self.sigma)
            * np.exp(-self.div * self.T)
        )

    def phi(self, put_call_type):
        if put_call_type == ("call"):
            return -self.T * np.exp(-self.div * self.T) * self.S * norm.cdf(self.d1, 0.0, 1.0)
        if put_call_type == ("put"):
            return self.T * np.exp(-self.div * self.T) * self.S * norm.cdf(-self.d1, 0.0, 1.0)


class Chooser_Option:
    """
    This class contains option pricing and greeks of the Chooser call and put options
    """

    def __init__(self, S, K, T, r, sigma, tao, div=0):
        """
        Args:
            S - spot price
            K - strike price
            T - time to maturity
            r - risk-free rate
            sigma - volatility
            tao - time to choose (when user will have to make decision regarding type of option : call/put)
            div - rate of continuous dividend (default = 0)

            #Only for delta, rho and phi:
            put_call_type - 'call' or 'put'

        Returns the option price estimated by Rubenstein's formula (modified black scholes model) and the options greeks
        """
        self.S = S
        self.K = K
        self.T = T
        self.r = r
        self.div = div
        self.sigma = sigma
        self.tao = tao

        self.d1 = (np.log(self.S / self.K) + (self.r - self.div + 0.5 * self.sigma**2) * self.T) / (
            self.sigma * np.sqrt(self.T)
        )
        self.d2 = self.d1 - self.sigma * np.sqrt(self.T)
        self.d1_star = (
            np.log(self.S / self.K) + ((self.r - self.div) * self.T) + ((0.5 * self.sigma**2) * self.tao)
        ) / (self.sigma * np.sqrt(self.tao))
        self.d2_star = self.d1_star - self.sigma * np.sqrt(self.tao)

    def price(self):

        w = (
            self.S * np.exp(-self.div * self.T) * norm.cdf(self.d1)
            - self.K * np.exp(-self.r * self.T) * norm.cdf(self.d2)
            + self.K * np.exp(-self.r * self.T) * norm.cdf(-self.d2_star)
            - self.S * np.exp(-self.div * self.T) * norm.cdf(-self.d1_star)
        )

        return w

    def delta(self):
        return np.exp(-self.div * self.T) * (norm.cdf(self.d1) - norm.cdf(-self.d1_star))

    def gamma(self):
        return (
            (np.exp(-self.div * self.T) * norm.pdf(self.d1)) / (self.S * self.sigma * np.sqrt(self.T))
        ) + ((np.exp(-self.div * self.T) * norm.pdf(self.d1_star)) / (self.S * self.sigma * np.sqrt(self.T)))

    def vega(self):
        temp = self.S * np.exp(-self.div * self.T) * np.sqrt(self.T) * norm.pdf(self.d1)
        return temp + self.S * np.exp(-self.div * self.T) * np.sqrt(self.tao) * norm.pdf(self.d1_star)

    def rho(self):
        temp = self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(self.d1)
        return temp - self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(-self.d2_star)


class Basket_Option:
    """
    This class contains option pricing and greeks of the Basket call and put options
    """

    def __init__(self, S, K, T, r, put_call_type, cov, n_asset, sigma, weight=None, div=0):
        """
        Args:
            S - spot price
            K - strike price
            T - time to maturity
            r - risk-free rate
            div - rate of continuous dividend
            sigma - volatility
            put_call_type - 1 for 'call' and -1 for 'put'
            cor - correlation
            weight - asset weights, If None, equally weighted as 1/n_asset
                If scalar, equal weights of the value
                If 1-D array, used as it is

        Returns the option price estimated by the closed form approach of
        log-normal approximation of Levy & Turnbull (1992) and the options greeks
        """
        self.sigma = sigma
        self.r = r
        self.T = T
        self.K = K
        self.S = S
        self.n_asset = n_asset
        self.div = div
        self.put_call_type = put_call_type
        self.cov = cov
        self.d1 = (
            np.log(np.array(self.S) / self.K) + (self.r - self.div + 0.5 * np.array(self.sigma) ** 2) * self.T
        ) / (np.array(self.sigma) * np.sqrt(self.T))
        self.d2 = (
            np.log(np.array(self.S) / self.K) + (self.r - self.div - 0.5 * np.array(self.sigma) ** 2) * self.T
        ) / (np.array(self.sigma) * np.sqrt(self.T))

        if weight is None:
            self.weight = np.ones(self.n_asset) / self.n_asset
        elif np.isscalar(weight):
            self.weight = np.ones(self.n_asset) * weight
        else:
            assert len(weight) == self.n_asset
            self.weight = np.array(weight)

    def price(self):
        df_temp = np.exp((self.r - self.div) * self.T)
        fwd_temp = np.array(self.S) * df_temp
        assert fwd_temp.shape[-1] == self.n_asset
        spot_len = len(self.S)
        fwd_basket = fwd_temp * self.weight
        m1_temp = 0
        for i in range(0, len(fwd_basket)):
            m1_temp += float(fwd_basket[i])
        k = 0
        m2_temp = 0
        m2_temp = float(m2_temp)
        for i in range(0, spot_len - 1):
            for j in range(1, spot_len):
                if i != j:
                    m2_temp += (
                        float(fwd_basket[i]) * np.exp(float(self.cov[k] * self.T)) * float(fwd_basket[j])
                    )
                    k += 1
        sig = np.sqrt(np.log(m2_temp / m1_temp))
        price = price_formula(self.K, m1_temp, m2_temp, sig, self.T, self.put_call_type, self.r)
        return price

    def delta(self, pc):

        if pc == ("call"):
            return np.exp(-self.div * self.T) * norm.cdf(self.d1, 0.0, 1.0)

        elif pc == ("put"):
            return np.exp(-self.div * self.T) * (norm.cdf(self.d1, 0.0, 1.0) - 1)

    def gamma(self):
        return (
            1
            / (np.array(self.S) * np.array(self.sigma) * np.sqrt(self.T))
            * norm.pdf(self.d1, 0.0, 1.0)
            * np.exp(-self.div * self.T)
        )

    def vega(self):
        return np.array(self.S) * norm.pdf(self.d1, 0.0, 1.0) * np.sqrt(self.T) * np.exp(-self.div * self.T)

    def rho(self, pc):
        if pc == ("call"):
            return self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(self.d2, 0.0, 1.0)

        elif pc == ("put"):
            return -self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(-self.d2, 0.0, 1.0)

    def vanna(self):
        return (
            np.sqrt(self.T)
            * norm.pdf(self.d1, 0.0, 1.0)
            * (self.d2 / np.array(self.sigma))
            * np.exp(-self.div * self.T)
        )

    def phi(self, pc):
        if pc == ("call"):
            return -self.T * np.exp(-self.div * self.T) * np.array(self.S) * norm.cdf(self.d1, 0.0, 1.0)
        if pc == ("put"):
            return self.T * np.exp(-self.div * self.T) * np.array(self.S) * norm.cdf(-self.d1, 0.0, 1.0)


class Compound_Option:
    """
    This class contains option pricing and greeks of the compound options
    For option price estimation, refer to: https://www.math.ust.hk/~maykwok/piblications/Articles/comp%20option.pdf
    For greeks estimation, refer to: https://mathfinance.com/wp-content/uploads/2017/06/greeks.pdf
    """

    def __init__(self, time, S, K1, K2, T1, T2, r, sigma, div=0):
        """
        Args:
            S - spot price
            K1 - first strike price
            K2 - second strike price
            T1 - time to maturity for first expiration date
            T2 - time to maturity for second expiration date
            r - risk-free rate
            sigma - volatility
            div - rate of continuous dividend (default = 0)
            time - time to maturity in days for first expiration date

            #For functions in class: price, delta, gamma, vega and rho_greek:
            u_type - 'call' or 'put' (option type of the underlying option)
            c_type - 'call' or 'put' (option type of the compound option)
            Returns the option price estimated by the modified black-scholes model and the options greeks
        """
        self.S = S
        self.K1 = K1
        self.K2 = K2
        self.T1 = T1
        self.T2 = T2
        self.r = r
        self.div = div
        self.sigma = sigma
        self.time = time

        self.b1 = (np.log(self.S / self.K2) + (self.r - self.div + (0.5 * (self.sigma**2))) * self.T2) / (
            self.sigma * np.sqrt(self.T2)
        )
        self.b2 = self.b1 - self.sigma * np.sqrt(self.T2)

        # First I simulated stock price using geometric brownian motion and obtained a stock price estimate for time T1
        x = simulate_prices(self.time, self.S, self.r, self.sigma)
        y = x[-1]
        self.tau = self.T2 - self.T1
        # Then I used the GBM simulated stock price that was predicted and obtained above as an intial estimate for S*
        # I used newton-raphson's method to find root (S*) for the following equation: c(S*, T2 − T1; X2) = X1 (as given in reference paper)
        # Referred to this for idea on how to solve for root in any equation: https://stackoverflow.com/a/46265977/16635530
        self.S_star = scipy.optimize.newton(
            bs_try,
            y,
            args=(
                self.K2,
                self.tau,
                self.r,
                self.sigma,
                self.K1,
                self.div,
            ),
            tol=10 ** (-1),
            maxiter=1000000,
        )

        self.a1 = (
            np.log(self.S / self.S_star) + (self.r - self.div + (0.5 * (self.sigma**2))) * self.T1
        ) / (self.sigma * np.sqrt(self.T1))
        self.a2 = self.a1 - self.sigma * np.sqrt(self.T1)

        self.dt1 = (
            np.log(self.S_star / self.K2)
            + (self.r - self.div + (0.5 * (self.sigma**2))) * (self.T2 - self.T1)
        ) / (self.sigma * np.sqrt(self.T2 - self.T1))
        self.dt2 = self.dt1 - self.sigma * np.sqrt(self.T2 - self.T1)

        self.rho = np.sqrt(self.T1 / self.T2)
        self.low = np.array([-10000, -10000])
        self.mu = np.array([0, 0])
        """
        Since python doesn't have any direct way to calculate bivariate standard normal cdf,
        I used multivariate_normal from scipy.stats by following the below links:
        refer to : https://stackoverflow.com/a/34504720
        can also refer to: https://stackoverflow.com/a/41618495/16635530"""

    def price(self, u_type, comp_type):

        if u_type == "call" and comp_type == "call":
            cov = np.array([[1, self.rho], [self.rho, 1]])
            upp1 = np.array([self.a1, self.b1])
            upp2 = np.array([self.a2, self.b2])
            p1, i = mvn.mvnun(self.low, upp1, self.mu, cov)
            p2, i = mvn.mvnun(self.low, upp2, self.mu, cov)
            result = (
                (self.S * np.exp(-self.div * self.T2) * p1)
                - (self.K2 * np.exp(-self.r * self.T2) * p2)
                - (self.K1 * np.exp(-self.r * self.T1) * norm.cdf(self.a2))
            )
            if result < 0:
                return 0
            else:
                return result

        if u_type == "call" and comp_type == "put":
            cov = np.array([[1, -self.rho], [-self.rho, 1]])
            upp1 = np.array([-self.a2, self.b2])
            upp2 = np.array([-self.a1, self.b1])
            p1, i = mvn.mvnun(self.low, upp1, self.mu, cov)
            p2, i = mvn.mvnun(self.low, upp2, self.mu, cov)
            result = (
                (self.K2 * np.exp(-self.r * self.T2) * p1)
                - (self.S * np.exp(-self.div * self.T2) * p2)
                + (self.K1 * np.exp(-self.r * self.T1) * norm.cdf(-self.a2))
            )

            if result < 0:
                return 0
            else:
                return result

        if u_type == "put" and comp_type == "call":
            cov = np.array([[1, self.rho], [self.rho, 1]])
            upp1 = np.array([-self.a2, -self.b2])
            upp2 = np.array([-self.a1, -self.b1])
            p1, i = mvn.mvnun(self.low, upp1, self.mu, cov)
            p2, i = mvn.mvnun(self.low, upp2, self.mu, cov)
            result = (
                (self.K2 * np.exp(-self.r * self.T2) * p1)
                - (self.S * np.exp(-self.div * self.T2) * p2)
                - (self.K1 * np.exp(-self.r * self.T1) * norm.cdf(-self.a2))
            )

            if result < 0:
                return 0
            else:
                return result

        if u_type == "put" and comp_type == "put":
            cov = np.array([[1, -self.rho], [-self.rho, 1]])
            upp1 = np.array([self.a1, -self.b1])
            upp2 = np.array([self.a2, -self.b2])
            p1, i = mvn.mvnun(self.low, upp1, self.mu, cov)
            p2, i = mvn.mvnun(self.low, upp2, self.mu, cov)
            result = (
                (self.S * np.exp(-self.div * self.T2) * p1)
                - (self.K2 * np.exp(-self.r * self.T2) * p2)
                + (self.K1 * np.exp(-self.r * self.T1) * norm.cdf(self.a2))
            )

            if result < 0:
                return 0
            else:
                return result

    def delta(self, u_type, comp_type):
        if u_type == "call":
            utype_val = 1
        else:
            utype_val = -1
        if comp_type == "call":
            ctype_val = 1
        else:
            ctype_val = -1
        cov = np.array([[1, ctype_val * self.rho], [ctype_val * self.rho, 1]])
        upp = np.array([-utype_val * ctype_val * self.a1, utype_val * self.b1])
        p, i = mvn.mvnun(self.low, upp, self.mu, cov)
        return utype_val * ctype_val * np.exp(self.div * self.T2) * p

    def gamma(self, u_type, comp_type):
        if u_type == "call":
            utype_val = 1
        else:
            utype_val = -1
        if comp_type == "call":
            ctype_val = 1
        else:
            ctype_val = -1
        e = ((self.a2 * np.sqrt(self.T2)) + self.b2 * np.sqrt(self.T1)) / np.sqrt(self.T2 - self.T1)

        return ((np.exp(-self.div * self.T2)) / (self.sigma * self.S)) * (
            ((1 / self.T1) * norm.pdf(self.a1) * norm.cdf(utype_val * self.dt1))
            + ((ctype_val / (np.sqrt(self.T2))) * norm.pdf(self.a1) * norm.cdf(-utype_val * ctype_val * e))
        )

    def vega(self, u_type, comp_type):
        if u_type == "call":
            utype_val = 1
        else:
            utype_val = -1
        if comp_type == "call":
            ctype_val = 1
        else:
            ctype_val = -1
        e = ((self.a2 * np.sqrt(self.T2)) + self.b2 * np.sqrt(self.T1)) / np.sqrt(self.T2 - self.T1)
        return (
            self.S
            * np.exp(-self.div * self.T2)
            * (
                (self.T1 * norm.pdf(self.a1) * norm.cdf(utype_val * self.dt1))
                + (ctype_val * self.T2 * norm.pdf(self.b1) * norm.pdf(-utype_val * ctype_val * e))
            )
        )

    def rho_greek(self, u_type, comp_type):
        if u_type == "call":
            utype_val = 1
        else:
            utype_val = -1
        if comp_type == "call":
            ctype_val = 1
        else:
            ctype_val = -1
        cov = np.array([[1, ctype_val * self.rho], [ctype_val * self.rho, 1]])
        upp = np.array([-utype_val * ctype_val * self.a2, utype_val * self.b2])
        p, i = mvn.mvnun(self.low, upp, self.mu, cov)
        return (utype_val * ctype_val * self.T2 * self.K2 * np.exp(-self.r * self.T2) * p) + (
            ctype_val
            * self.T1
            * self.K1
            * np.exp(-self.r * self.T1)
            * norm.cdf(-utype_val * ctype_val * self.a2)
        )


def simulate_prices(time, S_0, r, sigma):
    """
    Function to simulate price movement of underlying prices using Brownian random process.
    Refer to: https://www.math.univ-paris13.fr/~kebaier/Lecture4.pdf
    Can also refer to: https://en.wikipedia.org/wiki/Geometric_Brownian_motion
    """
    np.random.seed(20)
    num_steps = time
    n = 20000  # number of simulations
    dt = 1.0 / 252.0
    St = S_0
    for _ in range(1, num_steps):
        # Random values to simulate Brownian motion (Gaussian distibution)
        Z = np.random.standard_normal(n)
        dW = np.sqrt(dt) * Z  # Wiener process or brownian motion

        St *= np.exp((r - 0.5 * sigma**2) * dt + sigma * dW)

    return St


def bs_try(S, K2, tau, r, sigma, K1, div):
    """
    Function to calculate critical spot price at time T1
    As given in the reference paper: c(S, T2 − T1; X2) = X1
    So trying to optimize and get the S for when c(S, T2 − T1; X2) - X1 = 0
    Refer to: https://www.math.ust.hk/~maykwok/piblications/Articles/comp%20option.pdf
    """
    d1 = (np.log(S / K2) + (r - div + 0.5 * sigma**2) * tau) / (sigma * np.sqrt(tau))
    d2 = S - sigma * np.sqrt(tau)

    c = S * np.exp(-div * tau) * norm.cdf(d1) - K2 * np.exp(-r * tau) * norm.cdf(d2)
    res = c - K1
    return res


class Cliquet_Option:
    """
    This class contains option pricing and greeks of the cliquet options
    For option price estimation, refer to:  The Complete Guide to Option Pricing Formulas by Haug et al, Page 124
    """

    def __init__(self, S, t1, t2, r, sigma, alpha, div=0):
        """
        Args:
            S - spot price
            T1 - array of time to the forward start or strike fixing
            T2 - array of time to maturity of the forward starting option
            r - risk-free rate
            sigma - volatility
            div - rate of continuous dividend (default = 0)
            alpha - strike is set equal to a positive constant α (alpha) times the asset price S
            For functions in class:
                price:
                    put_call_type = 'call' or 'put'
                    Returns the option price estimated by the modified black-scholes model and the options greeks
        """
        self.S = S
        self.t1 = t1
        self.t2 = t2
        self.r = r
        self.div = div
        self.sigma = sigma
        self.alpha = alpha
        self.b = self.r - self.div

    def price(self, put_call_type):
        result = 0
        d1 = []
        d2 = []
        for i in range(0, len(self.t2)):
            d1.append(
                (np.log(1 / self.alpha) + (self.b + (0.5 * self.sigma**2)) * (self.t2[i] - self.t1[i]))
                / (self.sigma * (np.sqrt(self.t2[i] - self.t1[i])))
            )
            d2.append(d1[i] - self.sigma * np.sqrt(self.t2[i] - self.t1[i]))

        if put_call_type == "call":
            for i in range(0, len(self.t2)):
                result += (
                    self.S
                    * np.exp((self.b - self.r) * self.t1[i])
                    * (
                        (np.exp((self.b - self.r) * (self.t2[i] - self.t1[i])) * norm.cdf(d1[i]))
                        - (self.alpha * np.exp((-self.r) * (self.t2[i] - self.t1[i])) * norm.cdf(d2[i]))
                    )
                )

        else:
            for i in range(0, len(self.t2)):
                result += (
                    self.S
                    * np.exp((self.b - self.r) * self.t1[i])
                    * (
                        (self.alpha * np.exp((-self.r) * (self.t2[i] - self.t1[i])) * norm.cdf(-d2[i]))
                        - (np.exp((self.b - self.r) * (self.t2[i] - self.t1[i])) * norm.cdf(-d1[i]))
                    )
                )

        return result


def price_formula(K, M, V, sigma, T, pc=1, r=0.0, div=0.0):
    disc_fac = np.exp(-T * r)
    m = np.log((M**2) / V)
    d1 = (m - np.log(K) + (sigma**2)) / sigma
    d2 = d1 - sigma
    pc = np.array(pc)
    price = M * norm.cdf(pc * d1) - np.array(K) * norm.cdf(pc * d2)
    price *= pc * disc_fac
    return price


def unnesting(df, explode):
    idx = df.index.repeat(df[explode[0]].str.len())
    df1 = pd.concat([pd.DataFrame({x: np.concatenate(df[x].values)}) for x in explode], axis=1)
    df1.index = idx

    return df1.join(df.drop(explode, 1), how="left")


def master_val(data, vix_data, config_dict):
    r_rate = config_dict["inputs"]["option_config"]["r_rate"]
    n_step = config_dict["inputs"]["option_config"]["n_step"]
    n_step = int(n_step)
    val_date = config_dict["inputs"]["option_config"]["val_date"]
    # Calculations
    rf = float(float(r_rate) / 100)

    start_time = pd.to_datetime(data["reporting_date"])
    data["new_date"] = pd.to_datetime(data["reporting_date"])
    maturity_time = pd.to_datetime(data["maturity_date"])

    time_to_maturity = []
    time_intervals = []
    for i in range(0, len(data)):
        if data.loc[i, "discount_daycount_convention"] == "Actual/365":
            time_to_maturity.append(abs((maturity_time[i] - start_time[i]).days) / 365)
            time_intervals.append(time_to_maturity[i] * 365)
        else:
            time_to_maturity.append(abs((maturity_time[i] - start_time[i]).days) / 252)
            time_intervals.append(time_to_maturity[i] * 252)

    vix_data["new_date"] = pd.to_datetime(vix_data["Date"])

    data = pd.merge(data, vix_data, on=["new_date"], how="left")
    data = data.drop(["new_date"], axis=1)
    data["sigma"] = np.sqrt(data["vix"]) / 100
    spot_price_list = data["spot_price"]
    strike_price_list = data["strike_price"]
    sigma_list = data["sigma"]
    if "barrier_price" in data:
        barrier_price_list = data["barrier_price"]
    else:
        data["barrier_price"] = 1.0
        barrier_price_list = data["barrier_price"]

    list_delta = []
    list_estimates = []
    list_gamma = []
    list_rho = []
    list_vega = []
    list_vanna = []
    list_phi = []

    for x in range(0, len(data)):
        try:
            if data.loc[x, "product_variant_name"] == "European Option":
                if data.loc[x, "put_call_type"] == "call":
                    value_option = Black_Scholes(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                    ).call()
                    list_estimates.append(value_option)

                    delta_val = Black_Scholes(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                    ).delta("call")
                    list_delta.append(delta_val)

                    gamma_val = Black_Scholes(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                    ).gamma()
                    list_gamma.append(gamma_val)

                    rho_val = Black_Scholes(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                    ).rho("call")
                    list_rho.append(rho_val)

                    phi_val = Black_Scholes(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                    ).phi("call")
                    list_phi.append(phi_val)

                    vanna_val = Black_Scholes(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                    ).vanna()
                    list_vanna.append(vanna_val)

                    vega_val = Black_Scholes(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                    ).vega()
                    list_vega.append(vega_val)

                else:
                    value_option = Black_Scholes(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                    ).put()
                    list_estimates.append(value_option)

                    delta_val = Black_Scholes(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                    ).delta("put")
                    list_delta.append(delta_val)

                    gamma_val = Black_Scholes(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                    ).gamma()
                    list_gamma.append(gamma_val)

                    rho_val = Black_Scholes(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                    ).rho("put")
                    list_rho.append(rho_val)

                    phi_val = Black_Scholes(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                    ).phi("put")
                    list_phi.append(phi_val)

                    vanna_val = Black_Scholes(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                    ).vanna()
                    list_vanna.append(vanna_val)

                    vega_val = Black_Scholes(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                    ).vega()
                    list_vega.append(vega_val)

            elif data.loc[x, "product_variant_name"] == "American Option":
                if data.loc[x, "put_call_type"] == "call":
                    value_option = Binomial_Tree(
                        n=n_step,
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        sigma=sigma_list[x],
                    ).binomial("call")
                    list_estimates.append(value_option)

                    delta_val = Binomial_Tree(
                        n=n_step,
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        sigma=sigma_list[x],
                    ).delta("call")
                    list_delta.append(delta_val)

                    gamma_val = Binomial_Tree(
                        n=n_step,
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        sigma=sigma_list[x],
                    ).gamma()
                    list_gamma.append(gamma_val)

                    rho_val = Binomial_Tree(
                        n=n_step,
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        sigma=sigma_list[x],
                    ).rho("call")
                    list_rho.append(rho_val)

                    phi_val = Binomial_Tree(
                        n=n_step,
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        sigma=sigma_list[x],
                    ).phi("call")
                    list_phi.append(phi_val)

                    vanna_val = Binomial_Tree(
                        n=n_step,
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        sigma=sigma_list[x],
                    ).vanna()
                    list_vanna.append(vanna_val)

                    vega_val = Binomial_Tree(
                        n=n_step,
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        sigma=sigma_list[x],
                    ).vega()
                    list_vega.append(vega_val)

                else:
                    value_option = Binomial_Tree(
                        n=n_step,
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        sigma=sigma_list[x],
                    ).binomial("put")
                    list_estimates.append(value_option)

                    delta_val = Binomial_Tree(
                        n=n_step,
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        sigma=sigma_list[x],
                    ).delta("put")
                    list_delta.append(delta_val)

                    gamma_val = Binomial_Tree(
                        n=n_step,
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        sigma=sigma_list[x],
                    ).gamma()
                    list_gamma.append(gamma_val)

                    rho_val = Binomial_Tree(
                        n=n_step,
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        sigma=sigma_list[x],
                    ).rho("put")
                    list_rho.append(rho_val)

                    phi_val = Binomial_Tree(
                        n=n_step,
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        sigma=sigma_list[x],
                    ).phi("put")
                    list_phi.append(phi_val)

                    vanna_val = Binomial_Tree(
                        n=n_step,
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        sigma=sigma_list[x],
                    ).vanna()
                    list_vanna.append(vanna_val)

                    vega_val = Binomial_Tree(
                        n=n_step,
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        sigma=sigma_list[x],
                    ).vega()
                    list_vega.append(vega_val)

            elif data.loc[x, "product_variant_name"] == "Barrier Option":
                if data.loc[x, "put_call_type"] == "call" and data.loc[x, "option_type"] == "down and out":
                    value_option = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).down_out_call()
                    list_estimates.append(value_option)

                    delta_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).delta("call")
                    list_delta.append(delta_val)

                    gamma_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).gamma()
                    list_gamma.append(gamma_val)

                    rho_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).rho("call")
                    list_rho.append(rho_val)

                    phi_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).phi("call")
                    list_phi.append(phi_val)

                    vanna_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).vanna()
                    list_vanna.append(vanna_val)

                    vega_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).vega()
                    list_vega.append(vega_val)

                elif data.loc[x, "put_call_type"] == "call" and data.loc[x, "option_type"] == "up and out":
                    value_option = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).up_out_call()
                    list_estimates.append(value_option)

                    delta_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).delta("call")
                    list_delta.append(delta_val)

                    gamma_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).gamma()
                    list_gamma.append(gamma_val)

                    rho_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).rho("call")
                    list_rho.append(rho_val)

                    phi_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).phi("call")
                    list_phi.append(phi_val)

                    vanna_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).vanna()
                    list_vanna.append(vanna_val)

                    vega_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).vega()
                    list_vega.append(vega_val)

                elif data.loc[x, "put_call_type"] == "call" and data.loc[x, "option_type"] == "down and in":
                    value_option = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).down_in_call()
                    list_estimates.append(value_option)

                    delta_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).delta("call")
                    list_delta.append(delta_val)

                    gamma_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).gamma()
                    list_gamma.append(gamma_val)

                    rho_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).rho("call")
                    list_rho.append(rho_val)

                    phi_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).phi("call")
                    list_phi.append(phi_val)

                    vanna_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).vanna()
                    list_vanna.append(vanna_val)

                    vega_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).vega()
                    list_vega.append(vega_val)

                elif data.loc[x, "put_call_type"] == "call" and data.loc[x, "option_type"] == "up and in":
                    value_option = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).up_in_call()
                    list_estimates.append(value_option)

                    delta_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).delta("call")
                    list_delta.append(delta_val)

                    gamma_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).gamma()
                    list_gamma.append(gamma_val)

                    rho_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).rho("call")
                    list_rho.append(rho_val)

                    phi_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).phi("call")
                    list_phi.append(phi_val)

                    vanna_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).vanna()
                    list_vanna.append(vanna_val)

                    vega_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).vega()
                    list_vega.append(vega_val)

                elif data.loc[x, "put_call_type"] == "put" and data.loc[x, "option_type"] == "down and out":
                    value_option = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).down_out_put()
                    list_estimates.append(value_option)

                    delta_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).delta("put")
                    list_delta.append(delta_val)

                    gamma_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).gamma()
                    list_gamma.append(gamma_val)

                    rho_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).rho("put")
                    list_rho.append(rho_val)

                    phi_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).phi("put")
                    list_phi.append(phi_val)

                    vanna_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).vanna()
                    list_vanna.append(vanna_val)

                    vega_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).vega()
                    list_vega.append(vega_val)

                elif data.loc[x, "put_call_type"] == "put" and data.loc[x, "option_type"] == "up and out":
                    value_option = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).up_out_put()
                    list_estimates.append(value_option)

                    delta_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).delta("put")
                    list_delta.append(delta_val)

                    gamma_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).gamma()
                    list_gamma.append(gamma_val)

                    rho_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).rho("put")
                    list_rho.append(rho_val)

                    phi_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).phi("put")
                    list_phi.append(phi_val)

                    vanna_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).vanna()
                    list_vanna.append(vanna_val)

                    vega_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).vega()
                    list_vega.append(vega_val)

                elif data.loc[x, "put_call_type"] == "put" and data.loc[x, "option_type"] == "down and in":
                    value_option = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).down_in_put()
                    list_estimates.append(value_option)

                    delta_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).delta("put")
                    list_delta.append(delta_val)

                    gamma_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).gamma()
                    list_gamma.append(gamma_val)

                    rho_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).rho("put")
                    list_rho.append(rho_val)

                    phi_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).phi("put")
                    list_phi.append(phi_val)

                    vanna_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).vanna()
                    list_vanna.append(vanna_val)

                    vega_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).vega()
                    list_vega.append(vega_val)

                elif data.loc[x, "put_call_type"] == "put" and data.loc[x, "option_type"] == "up and in":
                    value_option = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).up_in_put()
                    list_estimates.append(value_option)

                    delta_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).delta("put")
                    list_delta.append(delta_val)

                    gamma_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).gamma()
                    list_gamma.append(gamma_val)

                    rho_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).rho("put")
                    list_rho.append(rho_val)

                    phi_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).phi("put")
                    list_phi.append(phi_val)

                    vanna_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).vanna()
                    list_vanna.append(vanna_val)

                    vega_val = Barrier_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                        barrier=barrier_price_list[x],
                    ).vega()
                    list_vega.append(vega_val)

            elif data.loc[x, "product_variant_name"] == "Digital Option":
                if data.loc[x, "put_call_type"] == "call":
                    value_option = Digital_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                    ).call()
                    list_estimates.append(value_option)

                    delta_val = Digital_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                    ).delta("call")
                    list_delta.append(delta_val)

                    gamma_val = Digital_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                    ).gamma()
                    list_gamma.append(gamma_val)

                    rho_val = Digital_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                    ).rho("call")
                    list_rho.append(rho_val)

                    phi_val = Digital_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                    ).phi("call")
                    list_phi.append(phi_val)

                    vanna_val = Digital_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                    ).vanna()
                    list_vanna.append(vanna_val)

                    vega_val = Digital_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                    ).vega()
                    list_vega.append(vega_val)

                else:
                    value_option = Digital_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                    ).put()
                    list_estimates.append(value_option)

                    delta_val = Digital_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                    ).delta("put")
                    list_delta.append(delta_val)

                    gamma_val = Digital_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                    ).gamma()
                    list_gamma.append(gamma_val)

                    rho_val = Digital_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                    ).rho("put")
                    list_rho.append(rho_val)

                    phi_val = Digital_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                    ).phi("put")
                    list_phi.append(phi_val)

                    vanna_val = Digital_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                    ).vanna()
                    list_vanna.append(vanna_val)

                    vega_val = Digital_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        div=0,
                        sigma=sigma_list[x],
                    ).vega()
                    list_vega.append(vega_val)

            elif data.loc[x, "product_variant_name"] == "Asian Option":
                if data.loc[x, "put_call_type"] == "call":
                    value_option = Asian_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        sigma=sigma_list[x],
                        Nt=time_intervals[x],
                        div=0,
                    ).price_estimate("call")
                    list_estimates.append(value_option)

                    delta_val = Asian_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        sigma=sigma_list[x],
                        Nt=time_intervals[x],
                        div=0,
                    ).delta("call")
                    list_delta.append(delta_val)

                    gamma_val = Asian_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        sigma=sigma_list[x],
                        Nt=time_intervals[x],
                        div=0,
                    ).gamma()
                    list_gamma.append(gamma_val)

                    rho_val = Asian_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        sigma=sigma_list[x],
                        Nt=time_intervals[x],
                        div=0,
                    ).rho("call")
                    list_rho.append(rho_val)

                    phi_val = Asian_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        sigma=sigma_list[x],
                        Nt=time_intervals[x],
                        div=0,
                    ).phi("call")
                    list_phi.append(phi_val)

                    vanna_val = Asian_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        sigma=sigma_list[x],
                        Nt=time_intervals[x],
                        div=0,
                    ).vanna()
                    list_vanna.append(vanna_val)

                    vega_val = Asian_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        sigma=sigma_list[x],
                        Nt=time_intervals[x],
                        div=0,
                    ).vega()
                    list_vega.append(vega_val)

                else:
                    value_option = Asian_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        sigma=sigma_list[x],
                        Nt=time_intervals[x],
                        div=0,
                    ).price_estimate("put")
                    list_estimates.append(value_option)

                    delta_val = Asian_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        sigma=sigma_list[x],
                        Nt=time_intervals[x],
                        div=0,
                    ).delta("put")
                    list_delta.append(delta_val)

                    gamma_val = Asian_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        sigma=sigma_list[x],
                        Nt=time_intervals[x],
                        div=0,
                    ).gamma()
                    list_gamma.append(gamma_val)

                    rho_val = Asian_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        sigma=sigma_list[x],
                        Nt=time_intervals[x],
                        div=0,
                    ).rho("put")
                    list_rho.append(rho_val)

                    phi_val = Asian_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        sigma=sigma_list[x],
                        Nt=time_intervals[x],
                        div=0,
                    ).phi("put")
                    list_phi.append(phi_val)

                    vanna_val = Asian_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        sigma=sigma_list[x],
                        Nt=time_intervals[x],
                        div=0,
                    ).vanna()
                    list_vanna.append(vanna_val)

                    vega_val = Asian_Option(
                        S=spot_price_list[x],
                        K=strike_price_list[x],
                        T=time_to_maturity[x],
                        r=rf,
                        sigma=sigma_list[x],
                        Nt=time_intervals[x],
                        div=0,
                    ).vega()
                    list_vega.append(vega_val)

        except KeyError:
            continue

    data["Valuation_Date"] = val_date
    data = data[["Valuation_Date", "unique_reference_id", "product_variant_name"]]
    data["price_estimate"] = [round(num, 4) for num in list_estimates]

    data["delta"] = [round(num, 4) for num in list_delta]
    data["gamma"] = [round(num, 4) for num in list_gamma]
    data["rho"] = [round(num, 4) for num in list_rho]
    data["vega"] = [round(num, 4) for num in list_vega]
    data["vanna"] = [round(num, 4) for num in list_vanna]
    data["phi"] = [round(num, 4) for num in list_phi]

    return data
