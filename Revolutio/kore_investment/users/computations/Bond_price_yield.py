def bond_price(par, ytm, N, DSC, E, A, coup, freq=2):
    """
    Bond pricer based on quoted yield
    par = par value of the Bond
    ytm = yield to maturity of the Bond
    E = number of days in coupon period in which the settlement date falls
    A = accrual period for the bond transaction (number of days from beginning of coupon period to settlement date)
    coup = annual coupon rate of the Bond
    DSC = number of days from settlement to next coupon date
    freq = frequency of coupon payment
    """
    if N > 1:
        freq = float(freq)
        ytm = ytm / 100
        coup = coup / 100
        Redemption = par / (1 + (ytm) / freq) ** (N - 1 + DSC / E)
        dt = [(i) / 1 for i in range(1, int(N + 1))]
        middle = sum([(100 * (coup) / freq) / ((1 + (ytm) / freq) ** (t - 1 + DSC / E)) for t in dt])
        price = Redemption + middle - (100 * coup / freq * A / E)

    elif N == 1:
        DSR = E - A
        freq = float(freq)
        ytm = ytm / 100
        coup = coup / 100
        T1 = (100 * coup / freq) + par
        T2 = (ytm / freq * DSR / E) + 1
        T3 = 100 * coup / freq * A / E
        price = (T1 / T2) - T3
    else:
        pass

    return price
