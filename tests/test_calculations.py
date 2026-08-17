from services.calculations import calculate_quotation


def sample_inputs():
    return {
        "exShowroomPrice": 6120000,
        "monthlyOffers": 100000,
        "welcomeBenefit": 100000,
        "loyaltyOffer": 0,
        "otherOffer": 0,
        "insurance": 136714,
        "roadTax": 1222776,
        "otherLevies": 12837,
        "handlingCharges": 0,
        "statutoryOffer": 0,
        "accessories": 0,
        "starEase": 0,
        "extendedWarranty": 0,
        "downpaymentAgility": 592000,
        "downpaymentFinance": 600000,
        "loanAgility": 5328000,
        "loanFinance": 5200000,
        "termAgility": 48,
        "termFinance": 60,
        "emiAgility": 70950,
        "emiFinance": 127518,
        "roiAgility": 0.095,
        "roiFinance": 0.0699,
        "buybackAgility": 3383100,
        "processingFeeAgility": 18450,
        "processingFeeFinance": 18450,
        "securityDepositFinance": 0,
        "currentVehicleValue": 400000,
        "fpSupport": 0,
        "bookingAmount": 150000,
    }


def test_individual_manual_finance_inputs():
    c = calculate_quotation("individual", sample_inputs())
    assert c["netExShowroom"] == 5920000
    assert c["tcs"] == 59200
    assert c["vehiclePriceA"] == 5979200
    assert c["statutoryB"] == 1372327
    assert c["totalOutflow"] == 7351527
    assert c["downpaymentAgility"] == 592000
    assert c["downpaymentFinance"] == 600000
    assert c["loanAgility"] == 5328000
    assert c["loanFinance"] == 5200000
    assert c["netDisbursementAgility"] == 5238600
    assert c["netDisbursementFinance"] == 5181550
    assert c["netOutflow"] == 6951527


def test_corporate_uses_manual_finance_inputs():
    data = sample_inputs()
    data.update({"downpaymentAgility": 1000000, "downpaymentFinance": 1100000, "loanAgility": 4500000, "loanFinance": 4400000})
    c = calculate_quotation("corporate", data)
    assert c["downpaymentAgility"] == 1000000
    assert c["downpaymentFinance"] == 1100000
    assert c["loanAgility"] == 4500000
    assert c["loanFinance"] == 4400000


def test_handling_charge_is_not_part_of_statutory_total():
    data = sample_inputs()
    data["handlingCharges"] = 999999
    c = calculate_quotation("individual", data)
    assert c["statutoryB"] == 1372327


def test_star_finance_security_deposit_is_always_zero():
    data = sample_inputs()
    data["securityDepositFinance"] = 999999
    c = calculate_quotation("individual", data)
    assert c["securityDepositFinance"] == 0
    assert c["netDisbursementFinance"] == 5181550


def test_leasing_has_no_finance_dependency():
    c = calculate_quotation("leasing", sample_inputs())
    assert c["balanceMb"] == 5829200
    assert c["balanceDealer"] == 1372327
