import calendar

from dateutil.relativedelta import relativedelta


def toTimestamp(d):
    return calendar.timegm(d.timetuple())


def gen_date(valdate, num, unit):

    if valdate.day == calendar.monthrange(valdate.year, valdate.month)[1]:
        if unit == "D":
            fdate = valdate + relativedelta(days=+num)
        elif unit == "M":
            fdate = (valdate + relativedelta(days=+1) + relativedelta(months=+num)) - relativedelta(days=+1)
        elif unit == "Y":
            fdate = (valdate + relativedelta(days=+1) + relativedelta(years=+num)) - relativedelta(days=+1)
    else:
        if unit == "D":
            fdate = valdate + relativedelta(days=+num)
        elif unit == "M":
            fdate = valdate + relativedelta(months=+num)
        elif unit == "Y":
            fdate = valdate + relativedelta(years=+num)

    return fdate


def gen_date_range3(Next_pmt_date, Date_of_issue, Maturity_date, freq_num, freq_unit):
    # for NCD
    dates_list = []
    dates_list.insert(0, Next_pmt_date)
    date1 = Next_pmt_date
    n = no_of_payments(Next_pmt_date, Maturity_date, freq_num, freq_unit)

    for i in range(int(n) - 1):
        date_next = gen_date(date1, freq_num, freq_unit)
        dates_list.append(date_next)
        date1 = date_next
    if dates_list[-1] >= Maturity_date:
        dates_list[-1] = Maturity_date
    return dates_list


def no_of_payments(period_strt_dt, period_end_dt, freq_num, freq_unit):
    if freq_unit == "D":
        n = period_end_dt - period_strt_dt
        n = round((n.days / freq_num), 0) + 1
    elif freq_unit == "W":
        n = period_end_dt - period_strt_dt
        n = round((n.days / (7 * freq_num)), 0) + 1
    elif freq_unit == "M":
        n = period_end_dt - period_strt_dt
        n = round((n.days / (freq_num * 30.412)), 0) + 1
    elif freq_unit == "Y":
        n = period_end_dt - period_strt_dt
        n = round((n.days / (freq_num * 365.25)), 0) + 1
    return n


def number_of_days(effective_dates):
    days_list = []
    Effective_date = effective_dates
    for i in range(len(Effective_date)):
        date_diff = max((Effective_date[i] - Effective_date[i - 1]).days, 0)
        days_list.append(date_diff)

    return days_list
