from __future__ import annotations

from io import BytesIO
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    PageBreak,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


BLACK = colors.HexColor("#000000")
DARK_GREY = colors.HexColor("#8d8d8d")
LIGHT_GREY = colors.HexColor("#d9d9d9")
WHITE = colors.white


DISCLAIMER_A = (
    "[a]Part A disclaimer: The Net Ex-showroom price is determined by Mercedes-Benz India Private Limited "
    "(MB India) and is inclusive of standard sales measures and applicable offers. The Total Ex-showroom Price "
    "(Inclusive of Taxes) shall be payable to Mercedes-Benz India Private Limited as the Purchase Price of your "
    "Mercedes-Benz vehicle only. All other Additional Services are offered by the preferred Franchise Partner as "
    "selected by you and they do not form part of the standard product (i.e. Mercedes-Benz vehicle) offered by "
    "MB India. Any amount payable for these Additional Services shall be invoiced by the Franchise Partner in its "
    "independent capacity and payable to the Franchise Partner directly (along with applicable Taxes, if any). The "
    "Tax Collected at Source (TCS) has been calculated assuming that the Customer has fulfilled the conditions as "
    "stated in Section 206CCA, of the Income tax Act. In case the conditions provided in the said Section like filing "
    "of Income tax Returns for past 2 years, are not satisfied, the TCS at the higher rate i.e. 5% will be applicable. "
    "In case you fall in concessional tax category then the said concessions will be provided only if all the "
    "conditions for availing such concessions, as provided in the relevant law, are fulfilled. Provided that only "
    "such concessions as applicable on the date of invoice of the Vehicle will be available to the customer. The "
    "Purchase Price has been calculated as at the Order Date and the Order shall be valid for 14 calendar days from "
    "the Order Date (both days inclusive). The validity of the Order is non-extendable. Hence, the Order shall be "
    "finalized within the Validity Period by executing the Order Finalisation Form (Order Finalisation). The Taxes as "
    "applicable on the date of Invoice will be payable by the customer. Thus, Purchase Price may vary in case of "
    "change in GST/ CESS/ TCS/ other taxes or any other statutory dues after the Date of issue of this Order. "
    "Mercedes-Benz India Private Limited or its Franchise Partners will not be liable for any direct or indirect loss "
    "caused to the Customer on account of such change. The break-up of GST into various components like CGST, SGST/ "
    "UTGST or IGST shown as part of on-road price is just indicative. Actual components will be determined based on "
    "the location (State) of Agent/ Stock and address/ type of the customer at the time of Invoicing."
)

DISCLAIMER_B = (
    "[b]Part B disclaimer: The On-Road Price has been calculated as at Order Date and shall be valid for 14 calendar "
    "days from the Order Date (both days inclusive). The amount mentioned in Part B herein shall be payable directly "
    "to Franchise Partner as it would facilitate the payment of insurance, Road Tax and other Statutory levies for "
    "registration of the Vehicle. Road Tax specified in Part B is only indicative. More information on Road tax "
    "applicable to the Vehicle may be obtained from preferred Franchise Partner. Taxes and other levies as applicable "
    "on the date of registration shall be payable by the customer and Mercedes-Benz India Private Limited or its "
    "Franchise Partner shall not be responsible for any direct or indirect loss caused to the Customer on account of "
    "any change in such taxes or other levies. The Order shall be subject to submission of valid documents during the "
    "validity of the Order. The On-road Price may vary in case of change in taxes or any other statutory dues after the "
    "Order Date. Mercedes-Benz India Private Limited or its Franchise Partners shall not be held responsible for any "
    "direct or indirect loss caused to the Customer on account of any change in such taxes or other statutory dues."
)

DISCLAIMER_C = (
    "[c]Insurance Disclaimer: The insurance premium shown above is an indicative quotation for Purchaser’s convenience "
    "in arriving at the total cost of the Vehicle and that the Purchaser may independently reach out to any Franchise "
    "Partner/Motor Insurance Service Provider (MISP)/Insurance company for details of the premium and the terms and "
    "conditions of the insurance. The amount mentioned against ‘Insurance’ indicates the amount payable towards "
    "Insurance premium for Own Damage (OD) cover for one (01) year and add-on insurance covers, if any. The amount "
    "mentioned against ‘Other Statutory Levies’ indicates the amount payable towards Third Party (TP) insurance cover "
    "for three (03) years. The insurance premium has been calculated as per IRDAI guidelines. The Franchise Partner is "
    "the MISP of Mercedes-Benz Financial Services India Pvt. Ltd., holding valid Corporate agency license No CA0180, "
    "providing motor insurance services through it empaneled insurance companies namely IndusInd General Insurance "
    "Company Limited, ICICI Lombard General Insurance Company Limited, Bajaj General Insurance Limited and Tata AIG "
    "General Insurance Company Limited. MB India doesn’t represent nor does it solicit or sell insurance services and "
    "the Customer should use his judgement while choosing the insurer and the cover required by him/her."
)

DISCLAIMER_D = (
    "[d]The Road Tax above may be inclusive of an offer from MB India, further details on the same can be obtained from "
    "your preferred Franchise Partner."
)


styles = getSampleStyleSheet()
S_NORMAL = ParagraphStyle(
    "QuoteNormal", parent=styles["Normal"], fontName="Helvetica", fontSize=6.3, leading=7.2, spaceAfter=0
)
S_SMALL = ParagraphStyle(
    "QuoteSmall", parent=S_NORMAL, fontSize=4.35, leading=4.9
)
S_BOLD = ParagraphStyle(
    "QuoteBold", parent=S_NORMAL, fontName="Helvetica-Bold"
)
S_CENTER = ParagraphStyle(
    "QuoteCenter", parent=S_NORMAL, alignment=TA_CENTER
)
S_CENTER_BOLD = ParagraphStyle(
    "QuoteCenterBold", parent=S_BOLD, alignment=TA_CENTER
)
S_RIGHT = ParagraphStyle(
    "QuoteRight", parent=S_NORMAL, alignment=TA_RIGHT
)
S_WHITE_CENTER_BOLD = ParagraphStyle(
    "QuoteWhiteCenterBold", parent=S_CENTER_BOLD, textColor=WHITE
)
S_ITALIC = ParagraphStyle(
    "QuoteItalic", parent=S_NORMAL, fontName="Helvetica-Oblique", fontSize=4.5, leading=5.1
)


def p(value: Any, style: ParagraphStyle = S_NORMAL) -> Paragraph:
    text = "" if value is None else str(value)
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>")
    return Paragraph(text, style)


def _indian_group(integer_text: str) -> str:
    sign = ""
    if integer_text.startswith("-"):
        sign, integer_text = "-", integer_text[1:]
    if len(integer_text) <= 3:
        return sign + integer_text
    last3 = integer_text[-3:]
    lead = integer_text[:-3]
    groups = []
    while len(lead) > 2:
        groups.insert(0, lead[-2:])
        lead = lead[:-2]
    if lead:
        groups.insert(0, lead)
    return sign + ",".join(groups + [last3])


def fmt(value: Any) -> str:
    if value in (None, "", "-"):
        return "-"
    if isinstance(value, str):
        return value
    try:
        number = float(value)
        if abs(number - round(number)) < 0.000001:
            return _indian_group(str(int(round(number))))
        sign = "-" if number < 0 else ""
        whole, frac = f"{abs(number):.2f}".split(".")
        return sign + _indian_group(whole) + "." + frac
    except Exception:
        return str(value)


def section_header(title: str, width: float) -> Table:
    t = Table([[p(title, S_WHITE_CENTER_BOLD)]], colWidths=[width], rowHeights=[5.2 * mm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), BLACK),
                ("TEXTCOLOR", (0, 0), (-1, -1), WHITE),
                ("BOX", (0, 0), (-1, -1), 0.7, BLACK),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ]
        )
    )
    return t


def standard_rows_table(
    group: str,
    rows: list[tuple[str, Any, str, bool]],
    width: float,
    total_label: str | None = None,
    total_value: Any = None,
) -> Table:
    col_widths = [0.21 * width, 0.36 * width, 0.15 * width, 0.08 * width, 0.20 * width]
    data: list[list[Any]] = []
    for idx, (label, value, remark, calculated) in enumerate(rows):
        data.append(
            [
                p(group, S_CENTER_BOLD) if idx == 0 else "",
                p(label, S_BOLD if calculated else S_NORMAL),
                p(fmt(value), S_RIGHT),
                "",
                p(remark, S_NORMAL),
            ]
        )
    if total_label:
        data.append(["", p(total_label, S_CENTER_BOLD), p(fmt(total_value), S_RIGHT), "", ""])

    table = Table(data, colWidths=col_widths)
    style = [
        ("GRID", (0, 0), (-1, -1), 0.45, BLACK),
        ("SPAN", (0, 0), (0, max(0, len(rows) - 1))),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 1.3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.3),
    ]
    for i, row in enumerate(rows):
        if row[3]:
            style.append(("BACKGROUND", (1, i), (3, i), LIGHT_GREY))
        else:
            style.append(("BACKGROUND", (2, i), (3, i), LIGHT_GREY))
    if total_label:
        r = len(data) - 1
        style += [
            ("BACKGROUND", (1, r), (3, r), DARK_GREY),
            ("FONTNAME", (1, r), (2, r), "Helvetica-Bold"),
        ]
    table.setStyle(TableStyle(style))
    return table


def header_block(inputs: dict[str, Any], quotation_type: str, quote_date: str, width: float) -> Table:
    if quotation_type == "individual":
        left_lines = [
            "<b>Mercedes-Benz India Private Limited</b>",
            "E-3, MIDC Chakan - Phase III,",
            "Chakan Industrial Area,",
            "Kuruli &amp; Nighoje",
            "Tal: Khed",
            "Pune- 410501",
        ]
    else:
        left_lines = [
            "<b>Mercedes-Benz India Private Limited</b>",
            str(inputs.get("locationAddress") or "Address of respective location"),
            str(inputs.get("gstNumber") or "GST Number of Respective State"),
        ]

    left = Paragraph("<br/>".join(left_lines), S_NORMAL)
    customer = Paragraph(
        "<b>Customer Name:</b> " + str(inputs.get("customerName") or "")
        + "<br/><b>Customer Contact:</b> " + str(inputs.get("customerContact") or "")
        + "<br/><b>Franchise Partner Name:</b> " + str(inputs.get("franchisePartnerName") or "")
        + "<br/><br/><b><i>*This quote is valid till the end of this month</i></b>",
        S_NORMAL,
    )
    vehicle = Paragraph(
        f"<b>{quote_date}</b><br/><br/>"
        + "<b>Model Name:</b> " + str(inputs.get("modelName") or "C220D")
        + "<br/><b>Powertrain:</b> " + str(inputs.get("powertrain") or "")
        + "<br/><b>Colour:</b> " + str(inputs.get("colour") or ""),
        S_NORMAL,
    )
    t = Table([[left, customer, vehicle]], colWidths=[0.29 * width, 0.42 * width, 0.29 * width])
    t.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 0.65, BLACK),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return t


def column_header(width: float) -> Table:
    data = [[p("Purpose of Payment", S_CENTER_BOLD), "", p("Amount (INR)", S_CENTER_BOLD), "", p("Particulars/Remark", S_CENTER_BOLD)]]
    col_widths = [0.21 * width, 0.36 * width, 0.15 * width, 0.08 * width, 0.20 * width]
    t = Table(data, colWidths=col_widths)
    t.setStyle(
        TableStyle(
            [
                ("SPAN", (0, 0), (1, 0)),
                ("SPAN", (2, 0), (3, 0)),
                ("GRID", (0, 0), (-1, -1), 0.45, BLACK),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 1.5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
            ]
        )
    )
    return t


def finance_table(inputs: dict[str, Any], calc: dict[str, Any], quotation_type: str, width: float) -> Table:
    dp_label = "Downpayment"

    rows = [
        ("Select Plan:", "STAR AGILITY+", "STAR FINANCE"),
        (dp_label, inputs.get("downpaymentAgility"), inputs.get("downpaymentFinance")),
        ("Loan Amount", inputs.get("loanAgility"), inputs.get("loanFinance")),
        ("Term (Months)", inputs.get("termAgility"), inputs.get("termFinance")),
        ("EMI (Arrears)", inputs.get("emiAgility"), inputs.get("emiFinance")),
        ("Rate of Interest", f"{float(inputs.get('roiAgility') or 0)*100:.2f}%", f"{float(inputs.get('roiFinance') or 0)*100:.2f}%"),
        ("Buyback Value for 10K Per year for 4 years", inputs.get("buybackAgility"), "Not applicable"),
        ("Processing Fees & Stamp Duty", inputs.get("processingFeeAgility"), inputs.get("processingFeeFinance")),
        ("Security Deposit (if applicable)", calc["securityDepositAgility"], 0),
        ("Net Disbursement Amount", calc["netDisbursementAgility"], calc["netDisbursementFinance"]),
    ]
    data: list[list[Any]] = []
    for i, (label, ag, fin) in enumerate(rows):
        data.append(
            [
                p("Finance", S_CENTER_BOLD) if i == 0 else "",
                p(label, S_BOLD if i in (0, 9) else S_NORMAL),
                p(fmt(ag), S_CENTER_BOLD if i == 0 else S_RIGHT),
                p(fmt(fin), S_CENTER_BOLD if i == 0 else S_RIGHT),
                "",
            ]
        )
    t = Table(data, colWidths=[0.21 * width, 0.36 * width, 0.15 * width, 0.15 * width, 0.13 * width])
    style = [
        ("GRID", (0, 0), (-1, -1), 0.45, BLACK),
        ("SPAN", (0, 0), (0, len(data) - 1)),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 1.2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.2),
    ]
    for r in range(1, 9):
        style.append(("BACKGROUND", (2, r), (3, r), LIGHT_GREY))
    style.append(("BACKGROUND", (1, 9), (3, 9), DARK_GREY))
    t.setStyle(TableStyle(style))
    return t


def exchange_table(inputs: dict[str, Any], calc: dict[str, Any], width: float) -> Table:
    data = [
        [p("Exchange at MB Dealership", S_CENTER_BOLD), p("Value of current vehicle:", S_NORMAL), p(fmt(inputs.get("currentVehicleValue")), S_RIGHT), "", ""],
        ["", p("Special Support by FP Name", S_NORMAL), p(fmt(inputs.get("fpSupport")), S_RIGHT), "", ""],
        ["", p("Total Value to be adjusted for customer (D)", S_BOLD), p(fmt(calc["adjustmentD"]), S_RIGHT), "", ""],
        ["", p("Net Outflow (A) + (B) + (C) -(D)", S_BOLD), p(fmt(calc["netOutflow"]), S_RIGHT), "", ""],
    ]
    t = Table(data, colWidths=[0.21 * width, 0.36 * width, 0.15 * width, 0.15 * width, 0.13 * width])
    t.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.45, BLACK),
                ("SPAN", (0, 0), (0, 3)),
                ("BACKGROUND", (2, 0), (3, 1), LIGHT_GREY),
                ("BACKGROUND", (1, 2), (3, 3), DARK_GREY),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 1.2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1.2),
            ]
        )
    )
    return t


def payment_table(inputs: dict[str, Any], calc: dict[str, Any], quotation_type: str, width: float) -> Table:
    if quotation_type == "individual":
        rows = [
            ("Booking Amount", inputs.get("bookingAmount"), "", "NEFT/Credit Cards/Debit Cards/Cheque"),
            ("Balance Payment To MB India (A) -(DP) -Net Disbursement amount ( Star Agility+)", calc["balanceMbAgility"], "", "NEFT to unique Bank AC number OR\nCheque in the favour of Mercedes-Benz India Pvt. Ltd. OR\nCredit Card (up to INR 10 lakhs only)"),
            ("Balance Payment To MB India (A) -(DP) -Net Disbursement amount (Star Finance)", calc["balanceMbFinance"], "", "NEFT to unique Bank AC number OR\nCheque in the favour of Mercedes-Benz India Pvt. Ltd. OR\nCredit Card (up to INR 10 lakhs only)"),
            ("Balance Payment to Dealer (B) + (C) -(D)", "", calc["balanceDealer"], "NEFT/Credit Cards/Debit Cards/Cheque"),
            ("Paid to MB India by Financer (Star Agility+)", calc["paidByFinancerAgility"], "", ""),
            ("Paid to MB India by Financer (Star Finance)", calc["paidByFinancerFinance"], "", ""),
        ]
    elif quotation_type == "corporate":
        rows = [
            ("Booking Amount", inputs.get("bookingAmount"), "", "NEFT/Credit Cards/Debit Cards/Cheque"),
            ("Balance Payment To MB India (A) -(DP) -Net Disbursement amount ( Star Agility+)", calc["balanceMbAgility"], "", ""),
            ("Balance Payment To MB India (A) -(DP) -Net Disbursement amount (Star Finance)", calc["balanceMbFinance"], "", "NEFT to unique Bank AC number OR\nCheque in the favour of Mercedes-Benz India Pvt. Ltd. OR\nCredit Card (up to INR 10 lakhs only)"),
            ("Balance Payment to Dealer (B) + (C) -(D)", "", calc["balanceDealer"], "NEFT/Credit Cards/Debit Cards/Cheque"),
            ("Paid to MB India by Financer", calc["paidByFinancer"], "", ""),
        ]
    else:
        rows = [
            ("Booking Amount", inputs.get("bookingAmount"), "", "NEFT/Credit Cards/Debit Cards/Cheque"),
            ("Balance Payment To MB India (A) -(DP)", calc["balanceMb"], "", "NEFT to unique Bank AC number OR\nCheque in the favour of Mercedes-Benz India Pvt. Ltd. OR\nCredit Card (up to INR 10 lakhs only)"),
            ("Balance Payment to Dealer (B) + (C) -(D)", "", calc["balanceDealer"], "NEFT/Credit Cards/Debit Cards/Cheque"),
        ]

    data = [[p("Payment Options", S_BOLD), p("To Mercedes- Benz India", S_CENTER_BOLD), p("To FP Name", S_CENTER_BOLD), p("Mode", S_CENTER_BOLD)]]
    for label, mb, fp, mode in rows:
        data.append([p(label, S_NORMAL), p(fmt(mb), S_RIGHT), p(fmt(fp), S_RIGHT), p(mode, S_NORMAL)])
    t = Table(data, colWidths=[0.36 * width, 0.29 * width, 0.14 * width, 0.21 * width])
    t.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.45, BLACK),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 1.2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1.2),
            ]
        )
    )
    return t


def build_quotation_pdf(
    quotation_type: str,
    inputs: dict[str, Any],
    calc: dict[str, Any],
    quote_number: str,
    quote_date: str,
) -> bytes:
    buffer = BytesIO()
    page_size = landscape(A4)
    doc = SimpleDocTemplate(
        buffer,
        pagesize=page_size,
        leftMargin=6 * mm,
        rightMargin=6 * mm,
        topMargin=5 * mm,
        bottomMargin=5 * mm,
        title=f"{quote_number} - Proforma Quotation",
        author="Mercedes-Benz India Private Limited",
    )
    width = page_size[0] - doc.leftMargin - doc.rightMargin
    story: list[Any] = []

    title = Table([[p("PROFORMA QUOTATION", ParagraphStyle("title", parent=S_CENTER_BOLD, fontSize=10, leading=11))]], colWidths=[width])
    title.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.8, BLACK), ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
    story += [title, header_block(inputs, quotation_type, quote_date, width), column_header(width)]

    vehicle_rows = [
        ("Ex-Showroom Price", inputs.get("exShowroomPrice"), "", False),
        ("Monthly Offers  (if applicable)", inputs.get("monthlyOffers"), "Dream Days Campaign", False),
        ("Welcome Benefit (if applicable)", inputs.get("welcomeBenefit"), "Exchange support from MB India for your new car", False),
        ("Loyalty Offer (if applicable)", inputs.get("loyaltyOffer"), "As you are already a customer of Mercedes-Benz", False),
        ("Any other offer  (if applicable)", inputs.get("otherOffer"), inputs.get("otherOfferRemark") or "", False),
        ("Net Ex-Showroom Price", calc["netExShowroom"], "", True),
    ]
    if quotation_type in ("corporate", "leasing"):
        vehicle_rows += [
            ("Ex Factory Price", inputs.get("exFactoryPrice"), "", False),
            ("CGST / SGST OR IGST", inputs.get("gstComponent"), "", False),
        ]
    vehicle_rows += [
        ("TCS @1%", calc["tcs"], "Will be credited to your tax account", True),
    ]

    story += [
        section_header("Vehicle Price", width),
        standard_rows_table("Vehicle Price", vehicle_rows, width, "Total Vehicle Price payment (A)", calc["vehiclePriceA"]),
        section_header("Other Statutory requirements", width),
        standard_rows_table(
            "Registration & Insurance",
            [
                ("Insurance Star Protect Gold", inputs.get("insurance"), "Zero Dep, Engine Protector, Rodent Bite Cover", False),
                ("Road Tax/ Registration Charges", inputs.get("roadTax"), "", False),
                ("Other Levies", inputs.get("otherLevies"), "", False),
                ("Handling Charges", 0 if quotation_type in ("individual", "corporate") else inputs.get("handlingCharges"), "No handling charges are levied on customers by MB India", True if quotation_type in ("individual", "corporate") else False),
                ("Less: Any other offers   (If applicable)", inputs.get("statutoryOffer"), "Special limited time offer by MB India", False),
            ],
            width,
            "Total Statutory Payment (B)",
            calc["statutoryB"],
        ),
        Spacer(1, 2 * mm),
        section_header("Other Optional Extras", width),
        standard_rows_table(
            "OPTIONAL EXTRAS",
            [
                ("Accessories", inputs.get("accessories"), "", False),
                ("Star Ease - Service Packages", inputs.get("starEase"), "", False),
                ("Advance Assurance - Extended Warranty Packages", inputs.get("extendedWarranty"), "", False),
            ],
            width,
            "Total Optional Extras (C)",
            calc["optionalC"],
        ),
    ]

    total_table = Table([["", p("Total Outflow (A) + (B) + (C)", S_BOLD), p(fmt(calc["totalOutflow"]), S_RIGHT), "", ""]], colWidths=[0.21*width,0.36*width,0.15*width,0.08*width,0.20*width])
    total_table.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 0.45, BLACK), ("BACKGROUND", (1,0),(3,0), DARK_GREY)]))
    story += [total_table, PageBreak()]

    if quotation_type in ("individual", "corporate"):
        story += [KeepTogether([section_header("Finance plan", width), finance_table(inputs, calc, quotation_type, width)]), exchange_table(inputs, calc, width), Spacer(1, 4 * mm)]

    story += [payment_table(inputs, calc, quotation_type, width), Spacer(1, 3 * mm)]

    issued = Table([["", ""], ["", p("Issued by: Franchise Partner", S_CENTER)]], colWidths=[0.63 * width, 0.37 * width], rowHeights=[9 * mm, 4 * mm])
    issued.setStyle(TableStyle([("BOX", (1,0),(1,0),0.7,BLACK), ("VALIGN", (0,0),(-1,-1),"MIDDLE")]))
    story += [issued, Spacer(1, 2 * mm)]
    disclaimer_data = [
        [p(DISCLAIMER_A, S_SMALL), p(DISCLAIMER_B + "\n\n" + DISCLAIMER_C + "\n\n" + DISCLAIMER_D, S_SMALL)],
    ]
    disclaimer = Table(disclaimer_data, colWidths=[0.49 * width, 0.49 * width], hAlign="LEFT")
    disclaimer.setStyle(TableStyle([("VALIGN", (0,0),(-1,-1),"TOP"), ("LEFTPADDING",(0,0),(-1,-1),2), ("RIGHTPADDING",(0,0),(-1,-1),6)]))
    story += [disclaimer, Spacer(1, 2 * mm)]
    story += [p("Accessories, colours and fitments shown may not be part of standard specification. The Vehicles are tested for performance and quality under specific conditions and/or standard lab conditions. The performance may vary depending on the usage, driving, maintenance, fuel quality, road and terrain conditions.", S_ITALIC)]
    story += [Spacer(1, 1.5 * mm), p("This pricing is valid till the end of the month in which the quote is issued.", S_ITALIC)]

    doc.build(story)
    return buffer.getvalue()
