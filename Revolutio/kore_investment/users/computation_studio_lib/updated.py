def calculate_interest_schedule_vectorized(start_dates, end_dates, cashflow_dates, last_payment_date, interest_rate, principal, accrued_interest, valuation_date, discount_convention_code, custom_daycount_conventions, payout, model_code):
        # Calculate payout dates in a vectorized way
        is_payout_at_maturity = payout == 'Maturity'
        payout_dates = np.where(
            np.logical_or(
                np.logical_and(is_payout_at_maturity, np.arange(len(start_dates)) == len(start_dates) - 1),
                np.isin(end_dates, cashflow_dates) | (end_dates == last_payment_date)
            ),
            1, 0
        )

        # Determine if the model code is M046 and it's the first date
        is_first = np.arange(len(start_dates)) == 0
        is_model_M046 = model_code == 'M046'

        # Vectorize year fraction calculation
        year_frac_first = np.where(
            is_model_M046 & is_first,
            conventions.D_day_count(valuation_date, end_dates[0], discount_convention_code, custom_daycount_conventions),
            0
        )
        year_frac_rest = conventions.D_day_count(start_dates, end_dates, discount_convention_code, custom_daycount_conventions)
        year_frac = np.where(is_first, year_frac_first, year_frac_rest)

        # Vectorize accrual rate calculation
        accrual_rate = year_frac * interest_rate

        # Vectorize initial accrual factor calculation
        accrual_factor_first = np.where(
            is_model_M046 & is_first,
            1 + accrual_rate[0] + np.where(accrued_interest != 'None', accrued_interest / principal, 0),
            1 + accrual_rate[0]
        )
        accrual_factors = np.where(
            is_first,
            accrual_factor_first,
            np.cumprod(np.insert(accrual_rate[1:] + 1, 0, accrual_factor_first))
        )

        # Determine accrual factor payoff based on payout dates
        accrual_factor_payoff = np.where(payout_dates == 1, 1, accrual_factors)

        # Calculate outstanding balances and interest
        print("size of accrual_factor_payoff" , len(    accrual_factor_payoff))
        print("size of accrual_factors" , len(accrual_factors))
        print("size of accrual_factors" , len(principal))
        print("size of accrual_factors" , len(interest))
        
        outstanding_balance_before_payout = principal * accrual_factors
        outstanding_balance_after_payout = principal * accrual_factor_payoff
        interest = outstanding_balance_before_payout - principal

        # Prepare the final DataFrame
        compound_interest_schedule = pd.DataFrame({
            'accrual_start_date': start_dates,
            'date': end_dates,
            'payout_date': payout_dates,
            'year_frac': year_frac,
            'accrual_rate': accrual_rate,
            'accrual_factor': accrual_factors,
            'accrual_factor_payoff': accrual_factor_payoff,
            'outstanding_balance_before_payout': outstanding_balance_before_payout,
            'outstanding_balance_after_payout': outstanding_balance_after_payout,
            'interest': interest
        })

        return compound_interest_schedule

    compound_interest_schedule = calculate_interest_schedule_vectorized(
        Begining_Date_array, Ending_Date_array, cashflow_date, last_payment_date, 
        interest_rate, principal, accrued_interest, valuation_date, discount_convention_code, 
        custom_daycount_conventions, payout, model_code
    )