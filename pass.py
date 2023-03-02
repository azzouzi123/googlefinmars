import pytest
import numpy as np
from your_swap_class import YourSwapClass
import QuantLib as ql

@pytest.fixture(scope="module")
def swap(request):
    notional = request.param[0]
    fixed_rate = request.param[1]
    discount_rate = request.param[2]

    # Define other parameters of your vanilla swap
    start_date = ql.Date(1, 3, 2023)
    maturity_date = ql.Date(1, 3, 2028)
    fixed_leg_tenor = ql.Period("6M")
    float_leg_tenor = ql.Period("6M")
    float_spread = 0.0
    fixed_leg_daycount = ql.Actual360()
    float_leg_daycount = ql.Actual360()

    # Create instances of your swap class and QuantLib's vanilla swap class
    your_swap = YourSwapClass(
        notional,
        start_date,
        maturity_date,
        fixed_rate,
        fixed_leg_tenor,
        float_leg_tenor,
        float_spread,
        fixed_leg_daycount,
        float_leg_daycount,
        discount_rate,
    )

    ql.Settings.instance().evaluationDate = start_date
    ql.IndexManager.instance().clearHistories()

    float_index = ql.Euribor6M()
    ql.Settings.instance().evaluationDate = start_date
    ql.IndexManager.instance().clearHistories()

    ql_schedule = ql.Schedule(
        start_date,
        maturity_date,
        float_leg_tenor,
        ql.TARGET(),
        ql.ModifiedFollowing,
        ql.ModifiedFollowing,
        ql.DateGeneration.Forward,
        False,
    )

    ql_float_leg = ql.IborLeg(
        [notional],
        ql_schedule,
        float_index,
        ql.Actual360(),
        ql.PaymentConvention.ModifiedFollowing,
        float_spread,
    )

    ql_fixed_leg = ql.FixedRateLeg(
        ql_schedule,
        ql.Thirty360(),
        [notional],
        [fixed_rate],
        ql.PaymentConvention.ModifiedFollowing,
    )

    ql_swap = ql.Swap(ql_fixed_leg, ql_float_leg)

    return your_swap, ql_swap


@pytest.mark.parametrize(
    "notional, fixed_rate, discount_rate, tol",
    [
        (1000000, 0.05, 0.03, 1e-03),
        (5000000, 0.02, 0.01, 1e-03),
        (2000000, 0.03, 0.02, 1e-03),
    ],
)
def test_swap_price(swap, tol):
    your_swap, ql_swap = swap
    your_price = your_swap.price()
    ql_price = ql_swap.NPV()

    assert np.allclose(your_price, ql_price, rtol=tol)
