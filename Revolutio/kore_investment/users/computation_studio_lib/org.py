def calculate_interest_parameters(start_dates, end_dates, cashflow_dates, last_payment_date, interest_rate, principal, accrued_interest, valuation_date, discount_convention_code, custom_daycount_conventions, payout, model_code):
        start_dates = np.array(start_dates)
        end_dates = np.array(end_dates)
        cashflow_dates = np.array(cashflow_dates)
        len_dates = len(start_dates)
        is_model_M046 = model_code == 'M046'
        is_payout_at_maturity = payout == 'Maturity'

        # Initialize the payout_dates with zeros fixing size can improve speed
        payout_dates = np.zeros(len_dates, dtype=int)
        
        for i in range(len_dates):
            if is_payout_at_maturity and i == len_dates - 1:
                payout_dates[i] = 1
            elif end_dates[i] in cashflow_dates or end_dates[i] == last_payment_date:
                payout_dates[i] = 1

        if is_model_M046:
            year_frac = np.zeros(len_dates)
            year_frac[0] = conventions.D_day_count(valuation_date, end_dates[0], discount_convention_code, custom_daycount_conventions)
            for i in range(1, len_dates):
                year_frac[i] = conventions.D_day_count(start_dates[i], end_dates[i], discount_convention_code, custom_daycount_conventions)
        else:
            year_frac = np.array([conventions.D_day_count(start, end, discount_convention_code, custom_daycount_conventions) for start, end in zip(start_dates, end_dates)])

        accrual_rate = year_frac * interest_rate

        accrual_factors = np.zeros(len_dates)
        accrual_factor_payoff = np.zeros(len_dates)
        for i in range(len_dates):
            if i == 0:
                if is_model_M046 and str(accrued_interest) != 'None':
                    accrual_factors[i] = 1 + accrual_rate[i] + accrued_interest / principal
                else:
                    accrual_factors[i] = 1 + accrual_rate[i]
            else:
                accrual_factors[i] = accrual_factors[i-1] * (1 + accrual_rate[i])

            if payout_dates[i] == 1:
                accrual_factor_payoff[i] = 1
            else:
                accrual_factor_payoff[i] = accrual_factors[i]

        compound_interest_schedule = pd.DataFrame({
            'accrual_start_date': start_dates,
            'date': end_dates,
            'payout_date': payout_dates,
            'year_frac': year_frac,
            'accrual_rate': accrual_rate,
            'accrual_factor': accrual_factors,
            'accrual_factor_payoff': accrual_factor_payoff
        })

        return compound_interest_schedule


    start2 = time.time()
    compound_interest_schedule = calculate_interest_parameters(
            Begining_Date_array,  
            Ending_Date_array,  
            cashflow_date,  
            last_payment_date,  
            interest_rate,  
            principal[0],  
            accrued_interest,  
            valuation_date,  
            discount_convention_code,  
            custom_daycount_conventions,  
            payout,  
            model_code
    )
    end2 = time.time()
    #raise Exception (start2 - end2)

    compound_interest_schedule = pd.DataFrame(compound_interest_schedule)

    # Outstanding balance and interest calculation
    compound_interest_schedule["outstanding_balance_before_payout"] = (
        principal[0] * compound_interest_schedule["accrual_factor"]
    )

    compound_interest_schedule["outstanding_balance_after_payout"] = principal[0] * (
        compound_interest_schedule["accrual_factor_payoff"]
    )
    
    # compound_interest_schedule["outstanding_balance_after_payout"] = principal[0] * np.where(
    #         compound_interest_schedule["payout_date"] == 0, 
    #         compound_interest_schedule["accrual_factor"], 
    #         1
    # )

    compound_interest_schedule["interest"] = (
        compound_interest_schedule["outstanding_balance_before_payout"] - principal[0]
    )