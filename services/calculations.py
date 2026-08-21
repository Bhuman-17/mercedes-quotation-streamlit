from decimal import Decimal, ROUND_HALF_UP
from typing import Any


ZERO = Decimal("0")
TWO_DP = Decimal("0.01")


def d(value: Any) -> Decimal:
    if value in (None, "", "-"):
        return ZERO
    if isinstance(value, bool):
        return Decimal(int(value))
    try:
        return Decimal(str(value).replace(",", "").strip())
    except Exception:
        return ZERO


def money(value: Decimal) -> float:
    return float(value.quantize(TWO_DP, rounding=ROUND_HALF_UP))


def common_totals(inputs: dict[str, Any], corporate_like: bool = False) -> dict[str, float]:
    ex_showroom = d(inputs.get("exShowroomPrice"))
    monthly = d(inputs.get("monthlyOffers"))
    welcome = d(inputs.get("welcomeBenefit"))
    loyalty = d(inputs.get("loyaltyOffer"))
    other_offer = d(inputs.get("otherOffer"))

    net_ex_showroom = ex_showroom - monthly - welcome - loyalty - other_offer
    tcs = net_ex_showroom * Decimal("0.01")
    vehicle_price_a = net_ex_showroom + tcs

    insurance = d(inputs.get("insurance"))
    road_tax = d(inputs.get("roadTax"))
    other_levies = d(inputs.get("otherLevies"))
    statutory_offer = d(inputs.get("statutoryOffer"))

    # Deliberately mirrors the uploaded Excel workbook.
    # Handling Charges are displayed in the quotation but are NOT included in Part B formula.
    statutory_b = insurance + road_tax + other_levies - statutory_offer

    accessories = d(inputs.get("accessories"))
    star_ease = d(inputs.get("starEase"))
    extended_warranty = d(inputs.get("extendedWarranty"))
    optional_c = accessories + star_ease + extended_warranty

    total_outflow = vehicle_price_a + statutory_b + optional_c

    return {
        "netExShowroom": money(net_ex_showroom),
        "tcs": money(tcs),
        "vehiclePriceA": money(vehicle_price_a),
        "statutoryB": money(statutory_b),
        "optionalC": money(optional_c),
        "totalOutflow": money(total_outflow),
    }


def calculate_individual(inputs: dict[str, Any]) -> dict[str, Any]:
    result = common_totals(inputs)
    net = d(result["netExShowroom"])
    a = d(result["vehiclePriceA"])
    b = d(result["statutoryB"])
    c = d(result["optionalC"])
    total = d(result["totalOutflow"])
    rv_percentage_agility = d(inputs.get("rvPercentageAgility"))
    buyback_agility = net * rv_percentage_agility

    downpayment_agility = d(inputs.get("downpaymentAgility"))
    downpayment_finance = d(inputs.get("downpaymentFinance"))
    loan_agility = d(inputs.get("loanAgility"))
    loan_finance = d(inputs.get("loanFinance"))

    processing_agility = d(inputs.get("processingFeeAgility"))
    processing_finance = d(inputs.get("processingFeeFinance"))
    emi_agility = d(inputs.get("emiAgility"))
    security_agility = emi_agility
    security_finance = ZERO

    net_disb_agility = loan_agility - processing_agility - security_agility
    net_disb_finance = loan_finance - processing_finance - security_finance

    current_vehicle = d(inputs.get("currentVehicleValue"))
    fp_support = d(inputs.get("fpSupport"))
    adjustment_d = current_vehicle + fp_support
    net_outflow = total - adjustment_d

    booking = d(inputs.get("bookingAmount"))
    balance_mb_agility = a - booking - net_disb_agility
    balance_mb_finance = a - booking - net_disb_finance
    balance_dealer = b + c - adjustment_d

    result.update(
        {
            "downpaymentAgility": money(downpayment_agility),
            "downpaymentFinance": money(downpayment_finance),
            "loanAgility": money(loan_agility),
            "loanFinance": money(loan_finance),
            "rvPercentageAgility": money(rv_percentage_agility),
            "buybackAgility": money(buyback_agility),
            "securityDepositAgility": money(security_agility),
            "securityDepositFinance": money(security_finance),
            "netDisbursementAgility": money(net_disb_agility),
            "netDisbursementFinance": money(net_disb_finance),
            "adjustmentD": money(adjustment_d),
            "netOutflow": money(net_outflow),
            "balanceMbAgility": money(balance_mb_agility),
            "balanceMbFinance": money(balance_mb_finance),
            "balanceDealer": money(balance_dealer),
            "paidByFinancerAgility": money(net_disb_agility),
            "paidByFinancerFinance": money(net_disb_finance),
        }
    )
    return result


def calculate_corporate(inputs: dict[str, Any]) -> dict[str, Any]:
    result = common_totals(inputs, corporate_like=True)
    net = d(result["netExShowroom"])
    a = d(result["vehiclePriceA"])
    b = d(result["statutoryB"])
    c = d(result["optionalC"])
    total = d(result["totalOutflow"])
    rv_percentage_agility = d(inputs.get("rvPercentageAgility"))
    buyback_agility = net * rv_percentage_agility

    downpayment_agility = d(inputs.get("downpaymentAgility"))
    downpayment_finance = d(inputs.get("downpaymentFinance"))
    loan_agility = d(inputs.get("loanAgility"))
    loan_finance = d(inputs.get("loanFinance"))

    processing_agility = d(inputs.get("processingFeeAgility"))
    processing_finance = d(inputs.get("processingFeeFinance"))
    emi_agility = d(inputs.get("emiAgility"))
    security_agility = emi_agility
    security_finance = ZERO

    net_disb_agility = loan_agility - processing_agility - security_agility
    net_disb_finance = loan_finance - processing_finance - security_finance

    current_vehicle = d(inputs.get("currentVehicleValue"))
    fp_support = d(inputs.get("fpSupport"))
    adjustment_d = current_vehicle + fp_support
    net_outflow = total - adjustment_d

    booking = d(inputs.get("bookingAmount"))
    balance_mb_agility = a - booking - net_disb_agility
    balance_mb_finance = a - booking - net_disb_finance
    balance_dealer = b + c - adjustment_d

    result.update(
        {
            "downpaymentAgility": money(downpayment_agility),
            "downpaymentFinance": money(downpayment_finance),
            "loanAgility": money(loan_agility),
            "loanFinance": money(loan_finance),
            "rvPercentageAgility": money(rv_percentage_agility),
            "buybackAgility": money(buyback_agility),
            "securityDepositAgility": money(security_agility),
            "securityDepositFinance": money(security_finance),
            "netDisbursementAgility": money(net_disb_agility),
            "netDisbursementFinance": money(net_disb_finance),
            "adjustmentD": money(adjustment_d),
            "netOutflow": money(net_outflow),
            "balanceMbAgility": money(balance_mb_agility),
            "balanceMbFinance": money(balance_mb_finance),
            "balanceDealer": money(balance_dealer),
            # Uploaded Corporate sheet has one financer row linked to Star Finance only.
            "paidByFinancer": money(net_disb_finance),
        }
    )
    return result


def calculate_leasing(inputs: dict[str, Any]) -> dict[str, Any]:
    result = common_totals(inputs, corporate_like=True)
    a = d(result["vehiclePriceA"])
    b = d(result["statutoryB"])
    c = d(result["optionalC"])
    booking = d(inputs.get("bookingAmount"))

    result.update(
        {
            "balanceMb": money(a - booking),
            "balanceDealer": money(b + c),
        }
    )
    return result


def calculate_quotation(quotation_type: str, inputs: dict[str, Any]) -> dict[str, Any]:
    if quotation_type == "individual":
        return calculate_individual(inputs)
    if quotation_type == "corporate":
        return calculate_corporate(inputs)
    if quotation_type == "leasing":
        return calculate_leasing(inputs)
    raise ValueError(f"Unsupported quotation type: {quotation_type}")
