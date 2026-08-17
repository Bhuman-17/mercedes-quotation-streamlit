(() => {
  const root = document.getElementById("root");

  let args = {};
  let page = "home";
  let type = "individual";
  let inputs = null;
  let quoteNumber = null;
  let busy = null;

  let lastResponseToken = null;
  let lastDownloadToken = null;

  let latestPdfUrl = null;
  let latestPdfFilename = null;

  /* =========================================================
     HELPERS
     ========================================================= */

  const ESC = (value) =>
    String(value ?? "").replace(
      /[&<>"']/g,
      (ch) =>
        ({
          "&": "&amp;",
          "<": "&lt;",
          ">": "&gt;",
          '"': "&quot;",
          "'": "&#39;",
        })[ch]
    );

  const fmt = (value) => {
    if (value === undefined || value === null) return "-";

    const number = Number(value || 0);

    if (Math.abs(number) < 0.000001) return "0";

    return new Intl.NumberFormat("en-IN", {
      maximumFractionDigits: 2,
    }).format(number);
  };

  const fmtInput = (value, decimals = 0) =>
    new Intl.NumberFormat("en-IN", {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(Number(value || 0));

  const displayDate = () =>
    new Intl.DateTimeFormat("en-US", {
      weekday: "long",
      month: "long",
      day: "numeric",
      year: "numeric",
    }).format(new Date());

  /* =========================================================
     STREAMLIT COMMUNICATION
     ========================================================= */

  function sendMessage(typeName, data) {
    window.parent.postMessage(
      {
        isStreamlitMessage: true,
        type: typeName,
        ...(data || {}),
      },
      "*"
    );
  }

  function sendData(data) {
    sendMessage("streamlit:setComponentValue", {
      value: data,
      dataType: "json",
    });
  }

  function setFrameHeight(height) {
    sendMessage("streamlit:setFrameHeight", {
      height: Math.max(300, Math.ceil(height)),
    });
  }

  function setDynamicHeight() {
    window.requestAnimationFrame(() => {
      const height = Math.max(
        document.body.scrollHeight,
        document.documentElement.scrollHeight,
        root ? root.scrollHeight : 0
      );

      setFrameHeight(height + 10);
    });
  }

  function init() {
    sendMessage("streamlit:componentReady", {
      apiVersion: 1,
    });
  }

  /* =========================================================
     DEFAULT VALUES
     ========================================================= */

  const commonDefaults = {
    customerName: "",
    customerContact: "",
    franchisePartnerName: "",

    modelName: "C220D",
    powertrain: "",
    colour: "",

    locationAddress: "",
    gstNumber: "",

    exShowroomPrice: 6120000,
    monthlyOffers: 100000,
    welcomeBenefit: 100000,
    loyaltyOffer: 0,
    otherOffer: 0,
    otherOfferRemark: "",

    exFactoryPrice: 0,
    gstComponent: 0,

    insurance: 136714,
    roadTax: 1222776,
    otherLevies: 12837,
    handlingCharges: 0,
    statutoryOffer: 0,

    accessories: 0,
    starEase: 0,
    extendedWarranty: 0,

    termAgility: 48,
    termFinance: 48,

    emiAgility: 70950,
    emiFinance: 127518,

    roiAgility: 0.095,
    roiFinance: 0.0699,

    buybackAgility: 3383100,

    processingFeeAgility: 18450,
    processingFeeFinance: 18450,

    securityDepositFinance: 0,

    currentVehicleValue: 400000,
    fpSupport: 0,

    bookingAmount: 150000,

    downpaymentAgility: 592000,
    downpaymentFinance: 592000,

    loanAgility: 5328000,
    loanFinance: 5328000,
  };

  function defaults(quotationType) {
    if (quotationType === "corporate") {
      return {
        ...commonDefaults,

        locationAddress: "Enter Address of respective location",
        gstNumber: "Enter GST Number of Respective State",

        emiAgility: 50600,
        emiFinance: 102105,

        roiAgility: 0.095,
        roiFinance: 0.0661,

        currentVehicleValue: 500000,

        downpaymentAgility: 1184000,
        downpaymentFinance: 1184000,

        loanAgility: 4736000,
        loanFinance: 4736000,
      };
    }

    if (quotationType === "leasing") {
      return {
        ...commonDefaults,

        locationAddress: "Address of respective location",
        gstNumber: "GST Number of Respective State",

        currentVehicleValue: 0,
      };
    }

    return { ...commonDefaults };
  }

  /* =========================================================
     CALCULATION LOGIC
     ========================================================= */

  function calc(quotationType, data) {
    const n = (key) => Number(data[key] || 0);

    const roundValue = (value) =>
      Math.round((value + Number.EPSILON) * 100) / 100;

    const netExShowroom =
      n("exShowroomPrice") -
      n("monthlyOffers") -
      n("welcomeBenefit") -
      n("loyaltyOffer") -
      n("otherOffer");

    const tcs = netExShowroom * 0.01;

    const vehiclePriceA = netExShowroom + tcs;

    /*
      Handling Charges deliberately not included.
      It is locked at 0 for Individual/Corporate.
    */
    const statutoryB =
      n("insurance") +
      n("roadTax") +
      n("otherLevies") -
      n("statutoryOffer");

    const optionalC =
      n("accessories") +
      n("starEase") +
      n("extendedWarranty");

    const totalOutflow =
      vehiclePriceA + statutoryB + optionalC;

    const common = {
      netExShowroom: roundValue(netExShowroom),
      tcs: roundValue(tcs),
      vehiclePriceA: roundValue(vehiclePriceA),
      statutoryB: roundValue(statutoryB),
      optionalC: roundValue(optionalC),
      totalOutflow: roundValue(totalOutflow),
      balanceDealer: 0,
    };

    /* LEASING */

    if (quotationType === "leasing") {
      return {
        ...common,

        balanceMb: roundValue(
          vehiclePriceA - n("bookingAmount")
        ),

        balanceDealer: roundValue(
          statutoryB + optionalC
        ),
      };
    }

    /* INDIVIDUAL / CORPORATE */

    const downpaymentAgility = n("downpaymentAgility");
    const downpaymentFinance = n("downpaymentFinance");

    const loanAgility = n("loanAgility");
    const loanFinance = n("loanFinance");

    const securityDepositAgility = n("emiAgility");
    // Star Finance security deposit is fixed at zero.
    const securityDepositFinance = 0;

    const netDisbursementAgility =
      loanAgility -
      n("processingFeeAgility") -
      securityDepositAgility;

    const netDisbursementFinance =
      loanFinance -
      n("processingFeeFinance") -
      securityDepositFinance;

    const adjustmentD =
      n("currentVehicleValue") +
      n("fpSupport");

    const result = {
      ...common,

      downpaymentAgility:
        roundValue(downpaymentAgility),

      downpaymentFinance:
        roundValue(downpaymentFinance),

      loanAgility:
        roundValue(loanAgility),

      loanFinance:
        roundValue(loanFinance),

      securityDepositAgility:
        roundValue(securityDepositAgility),

      securityDepositFinance:
        roundValue(securityDepositFinance),

      netDisbursementAgility:
        roundValue(netDisbursementAgility),

      netDisbursementFinance:
        roundValue(netDisbursementFinance),

      adjustmentD:
        roundValue(adjustmentD),

      netOutflow:
        roundValue(totalOutflow - adjustmentD),

      balanceMbAgility:
        roundValue(
          vehiclePriceA -
            n("bookingAmount") -
            netDisbursementAgility
        ),

      balanceMbFinance:
        roundValue(
          vehiclePriceA -
            n("bookingAmount") -
            netDisbursementFinance
        ),

      balanceDealer:
        roundValue(
          statutoryB +
            optionalC -
            adjustmentD
        ),
    };

    if (quotationType === "individual") {
      result.paidByFinancerAgility =
        roundValue(netDisbursementAgility);

      result.paidByFinancerFinance =
        roundValue(netDisbursementFinance);
    } else {
      result.paidByFinancer =
        roundValue(netDisbursementFinance);
    }

    return result;
  }

  /* =========================================================
     DISCLAIMERS
     ========================================================= */

  const DISCLAIMER_A = `[a]Part A disclaimer: The Net Ex-showroom price is determined by Mercedes-Benz India Private Limited (MB India) and is inclusive of standard sales measures and applicable offers. The Total Ex-showroom Price (Inclusive of Taxes) shall be payable to Mercedes-Benz India Private Limited as the Purchase Price of your Mercedes-Benz vehicle only. All other Additional Services are offered by the preferred Franchise Partner as selected by you and they do not form part of the standard product (i.e. Mercedes-Benz vehicle) offered by MB India. Any amount payable for these Additional Services shall be invoiced by the Franchise Partner in its independent capacity and payable to the Franchise Partner directly (along with applicable Taxes, if any). The Tax Collected at Source (TCS) has been calculated assuming that the Customer has fulfilled the conditions as stated in Section 206CCA, of the Income tax Act. In case the conditions provided in the said Section like filing of Income tax Returns for past 2 years, are not satisfied, the TCS at the higher rate i.e. 5% will be applicable. In case you fall in concessional tax category then the said concessions will be provided only if all the conditions for availing such concessions, as provided in the relevant law, are fulfilled. Provided that only such concessions as applicable on the date of invoice of the Vehicle will be available to the customer.`;

  const DISCLAIMER_B = `[b]Part B disclaimer: The On-Road Price has been calculated as at Order Date and shall be valid for 14 calendar days from the Order Date (both days inclusive). The amount mentioned in Part B herein shall be payable directly to Franchise Partner as it would facilitate the payment of insurance, Road Tax and other Statutory levies for registration of the Vehicle. Road Tax specified in Part B is only indicative. More information on Road tax applicable to the Vehicle may be obtained from preferred Franchise Partner.`;

  const DISCLAIMER_C = `[c]Insurance Disclaimer: The insurance premium shown above is an indicative quotation for Purchaser’s convenience in arriving at the total cost of the Vehicle and that the Purchaser may independently reach out to any Franchise Partner/Motor Insurance Service Provider (MISP)/Insurance company for details of the premium and the terms and conditions of the insurance.`;

  const DISCLAIMER_D = `[d]The Road Tax above may be inclusive of an offer from MB India, further details on the same can be obtained from your preferred Franchise Partner.`;

  /* =========================================================
     INPUT HELPERS
     ========================================================= */

  const textInput = (key) => `
    <input
      type="text"
      class="cell-input"
      data-key="${key}"
      value="${ESC(inputs[key])}"
    />
  `;

  const numberInput = (key, decimals = 0) => `
    <input
      type="text"
      class="cell-input numeric"
      data-key="${key}"
      data-number="1"
      data-decimals="${decimals}"
      value="${fmtInput(inputs[key], decimals)}"
      inputmode="decimal"
    />
  `;

  const percentInput = (key) => `
    <div class="percent-input-wrap">

      <input
        type="text"
        class="cell-input numeric"
        data-key="${key}"
        data-percent="1"
        data-decimals="2"
        value="${(
          Number(inputs[key] || 0) * 100
        ).toFixed(2)}"
        inputmode="decimal"
      />

      <span>%</span>

    </div>
  `;

  const tenureSelect = (key, maxMonths) => {
    const options = [12, 24, 36, 48, 60, 72, 84].filter(
      (month) => month <= maxMonths
    );

    return `
      <select
        class="cell-input tenure-select"
        data-key="${key}"
      >
        ${options
          .map(
            (month) => `
              <option
                value="${month}"
                ${Number(inputs[key]) === month ? "selected" : ""}
              >
                ${month}
              </option>
            `
          )
          .join("")}
      </select>
    `;
  };

  const calcSpan = (key) => `
    <span data-calc="${key}">
      ${fmt(calc(type, inputs)[key])}
    </span>
  `;

  /* =========================================================
     PRICE ROW
     ========================================================= */

  function priceRow({
    label,
    value,
    remark = "",
    category = "",
    categoryRows = 0,
    calculated = false,
    total = false,
  }) {
    return `
      <tr class="${
        total
          ? "total-row"
          : calculated
          ? "calculated-row"
          : ""
      }">

        ${
          category
            ? `
              <td
                rowspan="${categoryRows}"
                class="category-cell"
              >
                ${category}
              </td>
            `
            : ""
        }

        <td class="label-cell ${
          calculated || total ? "strong" : ""
        }">
          ${label}
        </td>

        <td class="amount-cell">
          ${value}
        </td>

        <td class="shade-cell"></td>

        <td class="remark-cell">
          ${remark}
        </td>

      </tr>
    `;
  }

  /* =========================================================
     HEADER
     ========================================================= */

  function header() {
    const corporateLike =
      type !== "individual";

    return `
      <div class="proforma-title">
        PROFORMA QUOTATION
      </div>

      <div class="quote-header">

        <div
          class="company-address ${
            corporateLike
              ? "editable-company"
              : ""
          }"
        >

          <strong>
            Mercedes-Benz India Private Limited
          </strong>

          ${
            corporateLike
              ? `
                ${textInput("locationAddress")}
                ${textInput("gstNumber")}
              `
              : `
                <div>E-3, MIDC Chakan - Phase III,</div>
                <div>Chakan Industrial Area,</div>
                <div>Kuruli &amp; Nighoje</div>
                <div>Tal: Khed</div>
                <div>Pune- 410501</div>
              `
          }

        </div>

        <div class="customer-details">

          <div class="customer-field-line">

            <strong class="field-label">
              Customer Name:
            </strong>

            <div class="field-input-wrap">
              ${textInput("customerName")}
            </div>

          </div>

          <div class="customer-field-line">

            <strong class="field-label">
              Customer Contact:
            </strong>

            <div class="field-input-wrap">
              ${textInput("customerContact")}
            </div>

          </div>

          <div class="customer-field-line">

            <strong class="field-label">
              Franchise Partner Name:
            </strong>

            <div class="field-input-wrap">
              ${textInput("franchisePartnerName")}
            </div>

          </div>

          <div class="validity">
            *This quote is valid till the end of this month
          </div>

        </div>

        <div class="vehicle-details">

          <div class="quote-date">
            ${displayDate()}
          </div>

          <div class="field-line">

            <strong>
              Model Name:
            </strong>

            ${textInput("modelName")}

          </div>

          <div class="field-line">

            <strong>
              Powertrain:
            </strong>

            ${textInput("powertrain")}

          </div>

          <div class="field-line">

            <strong>
              Colour:
            </strong>

            ${textInput("colour")}

          </div>

        </div>

      </div>
    `;
  }

  /* =========================================================
     MAIN PRICING
     ========================================================= */

  function mainPricing() {
    const corporateLike =
      type !== "individual";

    const vehicleRows =
      corporateLike ? 10 : 8;

    let html = `
      <table class="quote-table">
        <tbody>

          <tr class="column-headings">

            <th colspan="2">
              Purpose of Payment
            </th>

            <th colspan="2">
              Amount (INR)
            </th>

            <th>
              Particulars/Remark
            </th>

          </tr>

          <tr>

            <td
              colspan="5"
              class="section-cell"
            >
              Vehicle Price
            </td>

          </tr>
    `;

    html += priceRow({
      category: "Vehicle Price",
      categoryRows: vehicleRows,
      label: "Ex-Showroom Price",
      value:
        numberInput("exShowroomPrice"),
    });

    html += priceRow({
      label:
        "Monthly Offers (if applicable)",
      value:
        numberInput("monthlyOffers"),
      remark:
        "Dream Days Campaign",
    });

    html += priceRow({
      label:
        "Welcome Benefit (if applicable)",
      value:
        numberInput("welcomeBenefit"),
      remark:
        "Exchange support from MB India for your new car",
    });

    html += priceRow({
      label:
        "Loyalty Offer (if applicable)",
      value:
        numberInput("loyaltyOffer"),
      remark:
        "As you are already a customer of Mercedes-Benz",
    });

    html += priceRow({
      label:
        "Any other offer (if applicable)",
      value:
        numberInput("otherOffer"),
      remark:
        textInput("otherOfferRemark"),
    });

    html += priceRow({
      label:
        "Net Ex-Showroom Price",
      value:
        calcSpan("netExShowroom"),
      calculated: true,
    });

    if (corporateLike) {
      html += priceRow({
        label: "Ex Factory Price",
        value:
          numberInput("exFactoryPrice"),
      });

      html += priceRow({
        label:
          "CGST / SGST OR IGST",
        value:
          numberInput("gstComponent"),
      });
    }

    html += priceRow({
      label: "TCS @1%",
      value: calcSpan("tcs"),
      remark:
        "Will be credited to your tax account",
      calculated: true,
    });

    html += priceRow({
      label:
        "Total Vehicle Price payment (A)",
      value:
        calcSpan("vehiclePriceA"),
      total: true,
    });

    html += `
      <tr>
        <td
          colspan="5"
          class="section-cell"
        >
          Other Statutory requirements
        </td>
      </tr>
    `;

    html += priceRow({
      category:
        "Registration & Insurance",
      categoryRows: 6,
      label:
        "Insurance Star Protect Gold",
      value:
        numberInput("insurance"),
      remark:
        "Zero Dep, Engine Protector, Rodent Bite Cover",
    });

    html += priceRow({
      label:
        "Road Tax/ Registration Charges",
      value:
        numberInput("roadTax"),
    });

    html += priceRow({
      label: "Other Levies",
      value:
        numberInput("otherLevies"),
    });

    html += priceRow({
      label: "Handling Charges",

      value:
        type === "individual" ||
        type === "corporate"
          ? `<span class="locked-zero">0</span>`
          : numberInput("handlingCharges"),

      remark:
        "No handling charges are levied on customers by MB India",

      calculated:
        type === "individual" ||
        type === "corporate",
    });

    html += priceRow({
      label:
        "Less: Any other offers (If applicable)",
      value:
        numberInput("statutoryOffer"),
      remark:
        "Special limited time offer by MB India",
    });

    html += priceRow({
      label:
        "Total Statutory Payment (B)",
      value:
        calcSpan("statutoryB"),
      total: true,
    });

    html += `
      <tr class="spacer-row">
        <td colspan="5"></td>
      </tr>

      <tr>
        <td
          colspan="5"
          class="section-cell"
        >
          Other Optional Extras
        </td>
      </tr>
    `;

    html += priceRow({
      category:
        "OPTIONAL EXTRAS",
      categoryRows: 5,
      label:
        "Accessories",
      value:
        numberInput("accessories"),
    });

    html += priceRow({
      label:
        "Star Ease - Service Packages",
      value:
        numberInput("starEase"),
    });

    html += priceRow({
      label:
        "Advance Assurance - Extended Warranty Packages",
      value:
        numberInput("extendedWarranty"),
    });

    html += priceRow({
      label:
        "Total Optional Extras (C)",
      value:
        calcSpan("optionalC"),
      total: true,
    });

    html += priceRow({
      label:
        "Total Outflow (A) + (B) + (C)",
      value:
        calcSpan("totalOutflow"),
      total: true,
    });

    html += `
        </tbody>
      </table>
    `;

    return html;
  }

  /* =========================================================
     FINANCE
     ========================================================= */

  function finance() {
    if (type === "leasing") {
      return "";
    }

    return `
      <div class="section-title">
        Finance plan
      </div>

      <table class="finance-table">

        <tbody>

          <tr>

            <td
              rowspan="10"
              class="category-cell finance-category"
            >
              Finance
            </td>

            <td>
              Select Plan:
            </td>

            <th>
              STAR AGILITY+
            </th>

            <th>
              STAR FINANCE
            </th>

            <td class="finance-blank"></td>

          </tr>

          <tr>

            <td>
              Downpayment
            </td>

            <td>
              ${numberInput(
                "downpaymentAgility"
              )}
            </td>

            <td>
              ${numberInput(
                "downpaymentFinance"
              )}
            </td>

            <td></td>

          </tr>

          <tr>

            <td>
              Loan Amount
            </td>

            <td>
              ${numberInput("loanAgility")}
            </td>

            <td>
              ${numberInput("loanFinance")}
            </td>

            <td></td>

          </tr>

          <tr>

            <td>
              Term (Months)
            </td>

            <td>
              ${tenureSelect("termAgility", 60)}
            </td>

            <td>
              ${tenureSelect("termFinance", 84)}
            </td>

            <td></td>

          </tr>

          <tr>

            <td>
              EMI (Arrears)
            </td>

            <td>
              ${numberInput("emiAgility")}
            </td>

            <td>
              ${numberInput("emiFinance")}
            </td>

            <td></td>

          </tr>

          <tr>

            <td>
              Rate of Interest
            </td>

            <td>
              ${percentInput("roiAgility")}
            </td>

            <td>
              ${percentInput("roiFinance")}
            </td>

            <td></td>

          </tr>

          <tr>

            <td>
              Buyback Value for 10K Per year for 4 years
            </td>

            <td>
              ${numberInput(
                "buybackAgility"
              )}
            </td>

            <td class="na-cell">
              Not applicable
            </td>

            <td></td>

          </tr>

          <tr>

            <td>
              Processing Fees &amp; Stamp Duty
            </td>

            <td>
              ${numberInput(
                "processingFeeAgility"
              )}
            </td>

            <td>
              ${numberInput(
                "processingFeeFinance"
              )}
            </td>

            <td></td>

          </tr>

          <tr>

            <td>
              Security Deposit (if applicable)
            </td>

            <td class="calculated-amount finance-right">
              ${calcSpan(
                "securityDepositAgility"
              )}
            </td>

            <td class="calculated-amount finance-right">
              <span class="locked-zero">0</span>
            </td>

            <td></td>

          </tr>

          <tr class="finance-total">

            <td>
              Net Disbursement Amount
            </td>

            <td class="finance-right">
              ${calcSpan(
                "netDisbursementAgility"
              )}
            </td>

            <td class="finance-right">
              ${calcSpan(
                "netDisbursementFinance"
              )}
            </td>

            <td></td>

          </tr>

          <tr>

            <td
              rowspan="4"
              class="category-cell finance-category"
            >
              Exchange at MB Dealership
            </td>

            <td>
              Value of current vehicle:
            </td>

            <td>
              ${numberInput(
                "currentVehicleValue"
              )}
            </td>

            <td></td>
            <td></td>

          </tr>

          <tr>

            <td>
              Special Support by FP Name
            </td>

            <td>
              ${numberInput("fpSupport")}
            </td>

            <td></td>
            <td></td>

          </tr>

          <tr class="finance-total">

            <td>
              Total Value to be adjusted for customer (D)
            </td>

            <td>
              ${calcSpan("adjustmentD")}
            </td>

            <td></td>
            <td></td>

          </tr>

          <tr class="finance-total">

            <td>
              Net Outflow (A) + (B) + (C) -(D)
            </td>

            <td>
              ${calcSpan("netOutflow")}
            </td>

            <td></td>
            <td></td>

          </tr>

        </tbody>

      </table>
    `;
  }

  /* =========================================================
     PAYMENT
     ========================================================= */

  function payment() {
    let rows = `
      <tr>

        <td>
          Booking Amount
        </td>

        <td>
          ${numberInput("bookingAmount")}
        </td>

        <td></td>

        <td>
          NEFT/Credit Cards/Debit Cards/Cheque
        </td>

      </tr>
    `;

    if (type === "leasing") {
      rows += `
        <tr>

          <td>
            Balance Payment To MB India (A) -(DP)
          </td>

          <td class="payment-calc">
            ${calcSpan("balanceMb")}
          </td>

          <td></td>

          <td class="mode-long">
            NEFT to unique Bank AC number <b>OR</b>
            <br/>
            Cheque in the favour of Mercedes-Benz India Pvt. Ltd.
            <b>OR</b>
            <br/>
            Credit Card (up to INR 10 lakhs only)
          </td>

        </tr>

        <tr>

          <td>
            Balance Payment to Dealer (B) + (C) -(D)
          </td>

          <td></td>

          <td class="payment-calc">
            ${calcSpan("balanceDealer")}
          </td>

          <td>
            NEFT/Credit Cards/Debit Cards/Cheque
          </td>

        </tr>
      `;
    } else if (type === "individual") {
      rows += `
        <tr>

          <td>
            Balance Payment To MB India (A) -(DP) -Net Disbursement amount (Star Agility+)
          </td>

          <td class="payment-calc">
            ${calcSpan(
              "balanceMbAgility"
            )}
          </td>

          <td></td>

          <td class="mode-long">
            NEFT to unique Bank AC number <b>OR</b>
            <br/>
            Cheque in the favour of Mercedes-Benz India Pvt. Ltd.
            <b>OR</b>
            <br/>
            Credit Card (up to INR 10 lakhs only)
          </td>

        </tr>

        <tr>

          <td>
            Balance Payment To MB India (A) -(DP) -Net Disbursement amount (Star Finance)
          </td>

          <td class="payment-calc">
            ${calcSpan(
              "balanceMbFinance"
            )}
          </td>

          <td></td>

          <td class="mode-long">
            NEFT to unique Bank AC number <b>OR</b>
            <br/>
            Cheque in the favour of Mercedes-Benz India Pvt. Ltd.
            <b>OR</b>
            <br/>
            Credit Card (up to INR 10 lakhs only)
          </td>

        </tr>

        <tr>

          <td>
            Balance Payment to Dealer (B) + (C) -(D)
          </td>

          <td></td>

          <td class="payment-calc">
            ${calcSpan("balanceDealer")}
          </td>

          <td>
            NEFT/Credit Cards/Debit Cards/Cheque
          </td>

        </tr>

        <tr>

          <td>
            Paid to MB India by Financer (Star Agility+)
          </td>

          <td class="payment-calc">
            ${calcSpan(
              "paidByFinancerAgility"
            )}
          </td>

          <td></td>
          <td></td>

        </tr>

        <tr>

          <td>
            Paid to MB India by Financer (Star Finance)
          </td>

          <td class="payment-calc">
            ${calcSpan(
              "paidByFinancerFinance"
            )}
          </td>

          <td></td>
          <td></td>

        </tr>
      `;
    } else {
      rows += `
        <tr>

          <td>
            Balance Payment To MB India (A) -(DP) -Net Disbursement amount (Star Agility+)
          </td>

          <td class="payment-calc">
            ${calcSpan(
              "balanceMbAgility"
            )}
          </td>

          <td></td>
          <td></td>

        </tr>

        <tr>

          <td>
            Balance Payment To MB India (A) -(DP) -Net Disbursement amount (Star Finance)
          </td>

          <td class="payment-calc">
            ${calcSpan(
              "balanceMbFinance"
            )}
          </td>

          <td></td>

          <td class="mode-long">
            NEFT to unique Bank AC number <b>OR</b>
            <br/>
            Cheque in the favour of Mercedes-Benz India Pvt. Ltd.
            <b>OR</b>
            <br/>
            Credit Card (up to INR 10 lakhs only)
          </td>

        </tr>

        <tr>

          <td>
            Balance Payment to Dealer (B) + (C) -(D)
          </td>

          <td></td>

          <td class="payment-calc">
            ${calcSpan("balanceDealer")}
          </td>

          <td>
            NEFT/Credit Cards/Debit Cards/Cheque
          </td>

        </tr>

        <tr>

          <td>
            Paid to MB India by Financer
          </td>

          <td class="payment-calc">
            ${calcSpan("paidByFinancer")}
          </td>

          <td></td>
          <td></td>

        </tr>
      `;
    }

    return `
      <table class="payment-table">

        <thead>

          <tr>

            <th>
              Payment Options
            </th>

            <th>
              To Mercedes-Benz India
            </th>

            <th>
              To FP Name
            </th>

            <th>
              Mode
            </th>

          </tr>

        </thead>

        <tbody>
          ${rows}
        </tbody>

      </table>
    `;
  }

  /* =========================================================
     DISCLAIMERS
     ========================================================= */

  function disclaimers() {
    return `
      <div class="issued-wrapper">

        <div class="signature-box"></div>

        <div>
          Issued by:
          <em>
            Franchise Partner
          </em>
        </div>

      </div>

      <div class="disclaimers">

        <div>
          ${DISCLAIMER_A}
        </div>

        <div>

          ${DISCLAIMER_B}

          <br/><br/>

          ${DISCLAIMER_C}

          <br/><br/>

          ${DISCLAIMER_D}

        </div>

        <div class="disclaimer-foot">
          Accessories, colours and fitments shown may not be part of standard specification.
          The Vehicles are tested for performance and quality under specific conditions
          and/or standard lab conditions.
        </div>

        <div class="disclaimer-foot">
          This pricing is valid till the end of the month in which the quote is issued.
        </div>

      </div>
    `;
  }

  /* =========================================================
     PDF CACHE
     ========================================================= */

  function clearCachedPdf() {
    if (latestPdfUrl) {
      URL.revokeObjectURL(
        latestPdfUrl
      );
    }

    latestPdfUrl = null;
    latestPdfFilename = null;
  }

  /* =========================================================
     QUOTATION PAGE
     ========================================================= */

  function renderQuotation() {
    if (!inputs) {
      inputs = defaults(type);
    }

    /*
      Ensure fixed Handling Charge.
    */
    if (
      type === "individual" ||
      type === "corporate"
    ) {
      inputs.handlingCharges = 0;
    }

    const label =
      type === "corporate"
        ? "Corporate / Company"
        : type.charAt(0).toUpperCase() +
          type.slice(1);

    root.innerHTML = `
      <main class="editor-page component-editor-page">

        <div class="editor-topbar">

          <div>

            <button
              type="button"
              id="backBtn"
              class="back-link back-button"
            >
              ← Back
            </button>

            <strong>
              ${label} Quotation
            </strong>

          </div>

        </div>

        <div class="quotation-scroll">

          <div class="quotation-sheet">

            ${header()}

            ${mainPricing()}

            ${finance()}

            <div class="payment-gap"></div>

            ${payment()}

            ${disclaimers()}

          </div>

        </div>

        <div class="quotation-actions">

          <button
            type="button"
            id="printBtn"
            class="secondary-button"
          >
            Print
          </button>

          <button
            type="button"
            id="downloadBtn"
            class="primary-button"
            ${busy ? "disabled" : ""}
          >
            ${
              busy === "download"
                ? "Preparing PDF…"
                : "Download PDF"
            }
          </button>

        </div>

        ${
          args.status_message
            ? `
              <div
                class="status-message ${
                  args.status_kind ||
                  "info"
                }"
              >
                ${ESC(
                  args.status_message
                )}
              </div>
            `
            : ""
        }

      </main>
    `;

    bindQuotation();

    updateCalculated();

    /*
      Allow browser to fully build the long quotation
      before telling Streamlit its height.
    */
    window.requestAnimationFrame(() => {
      window.requestAnimationFrame(() => {
        setDynamicHeight();
      });
    });
  }

  /* =========================================================
     HOME PAGE
     ========================================================= */

  function renderHome() {
    page = "home";
    busy = null;

    /*
      First shrink the Streamlit iframe immediately.
      This prevents the previous long quotation height
      affecting the home page's layout.
    */
    setFrameHeight(900);

    const cards = [
      {
        key: "individual",
        number: "01",
        title: "Individual",
        description:
          "Create a proforma quotation for an individual customer.",
      },

      {
        key: "corporate",
        number: "02",
        title: "Corporate / Company",
        description:
          "Create the corporate or company quotation variant.",
      },

      {
        key: "leasing",
        number: "03",
        title: "Leasing",
        description:
          "Create the leasing quotation variant.",
      },
    ];

    const cardHtml = cards
      .map(
        (card) => `
          <button
            type="button"
            class="type-card type-card-button"
            data-create="${card.key}"
          >

            <div class="type-card-icon">
              ${card.number}
            </div>

            <h2>
              ${card.title}
            </h2>

            <p>
              ${card.description}
            </p>

            <span>
              Create quotation →
            </span>

          </button>
        `
      )
      .join("");

    root.innerHTML = `
      <main class="home-page">

        <div class="home-overlay">

          <section class="home-hero">

            <div class="brand-kicker">
              Mercedes-Benz India
            </div>

            <h1>
              Proforma Quotation
            </h1>

            <p>
              Select the quotation type to begin.
            </p>

          </section>

          <section class="quotation-type-grid">
            ${cardHtml}
          </section>

        </div>

      </main>
    `;

    /*
      IMPORTANT:
      Bind after root.innerHTML has been created.
    */
    const createButtons =
      root.querySelectorAll(
        "[data-create]"
      );

    createButtons.forEach(
      (button) => {
        button.addEventListener(
          "click",
          (event) => {
            event.preventDefault();
            event.stopPropagation();

            const selectedType =
              button.getAttribute(
                "data-create"
              );

            if (
              !selectedType ||
              ![
                "individual",
                "corporate",
                "leasing",
              ].includes(selectedType)
            ) {
              return;
            }

            /*
              Set the application state BEFORE
              rendering the quotation.
            */
            type = selectedType;

            inputs =
              defaults(selectedType);

            quoteNumber = null;

            busy = null;

            clearCachedPdf();

            page = "quotation";

            /*
              Reset inner iframe scroll.
            */
            window.scrollTo(0, 0);

            /*
              Render selected quotation.
            */
            renderQuotation();
          }
        );
      }
    );

    /*
      Keep home iframe fixed to a sensible height.
      Do NOT use dynamic quotation height here.
    */
    window.requestAnimationFrame(() => {
      window.requestAnimationFrame(() => {
        const home =
          root.querySelector(
            ".home-page"
          );

        const homeHeight =
          home
            ? Math.max(
                820,
                Math.min(
                  1000,
                  home.scrollHeight
                )
              )
            : 900;

        setFrameHeight(homeHeight);
      });
    });
  }

  /* =========================================================
     NUMERIC INPUT
     ========================================================= */

  function parseNumeric(element) {
    const raw = String(
      element.value || ""
    )
      .replace(/,/g, "")
      .replace(
        /[^0-9.-]/g,
        ""
      );

    const value = Number(raw);

    return Number.isFinite(value)
      ? value
      : 0;
  }

  /* =========================================================
     QUOTATION EVENTS
     ========================================================= */

  function bindQuotation() {
    const backBtn =
      document.getElementById(
        "backBtn"
      );

    const printBtn =
      document.getElementById(
        "printBtn"
      );

    const downloadBtn =
      document.getElementById(
        "downloadBtn"
      );

    /* BACK */

    if (backBtn) {
      backBtn.addEventListener(
        "click",
        (event) => {
          event.preventDefault();
          event.stopPropagation();

          /*
            Reset iframe before switching page.
          */
          setFrameHeight(900);

          window.scrollTo(
            0,
            0
          );

          renderHome();
        }
      );
    }

    /* PRINT */

    if (printBtn) {
      printBtn.addEventListener(
        "click",
        (event) => {
          event.preventDefault();

          window.print();
        }
      );
    }

    /* DOWNLOAD */

    if (downloadBtn) {
      downloadBtn.addEventListener(
        "click",
        (event) => {
          event.preventDefault();

          /*
            Re-download generated PDF if no values changed.
          */
          if (latestPdfUrl) {
            const link =
              document.createElement(
                "a"
              );

            link.href =
              latestPdfUrl;

            link.download =
              latestPdfFilename ||
              "Proforma_Quotation.pdf";

            document.body.appendChild(
              link
            );

            link.click();

            link.remove();

            return;
          }

          busy = "download";

          /*
            Don't rerender unnecessarily before sending
            values because it can disturb current input focus.
          */
          downloadBtn.disabled = true;

          downloadBtn.textContent =
            "Preparing PDF…";

          sendData({
            action:
              "download_pdf",

            quotation_type:
              type,

            inputs:
              { ...inputs },

            quote_number:
              quoteNumber,

            nonce:
              `${Date.now()}-${Math.random()}`,
          });
        }
      );
    }

    /* INPUTS */

    root
      .querySelectorAll(
        "input[data-key]"
      )
      .forEach(
        (element) => {
          element.addEventListener(
            "focus",
            () => {
              if (
                element.dataset.number ===
                "1"
              ) {
                element.value =
                  String(
                    inputs[
                      element.dataset.key
                    ] ?? 0
                  );
              }
            }
          );

          element.addEventListener(
            "input",
            () => {
              clearCachedPdf();

              const key =
                element.dataset.key;

              if (
                element.dataset.percent ===
                "1"
              ) {
                inputs[key] =
                  parseNumeric(
                    element
                  ) / 100;
              } else if (
                element.dataset.number ===
                "1"
              ) {
                inputs[key] =
                  parseNumeric(
                    element
                  );
              } else {
                inputs[key] =
                  element.value;
              }

              updateCalculated();
            }
          );

          element.addEventListener(
            "blur",
            () => {
              const key =
                element.dataset.key;

              if (
                element.dataset.percent ===
                "1"
              ) {
                element.value =
                  (
                    Number(
                      inputs[key] || 0
                    ) * 100
                  ).toFixed(2);
              } else if (
                element.dataset.number ===
                "1"
              ) {
                element.value =
                  fmtInput(
                    inputs[key],
                    Number(
                      element.dataset.decimals ||
                        0
                    )
                  );
              }
            }
          );
        }
      );

    /* DROPDOWNS */

    root
      .querySelectorAll(
        "select[data-key]"
      )
      .forEach(
        (element) => {
          element.addEventListener(
            "change",
            () => {
              inputs[
                element.dataset.key
              ] = Number(
                element.value
              );

              clearCachedPdf();

              updateCalculated();
            }
          );
        }
      );
  }

  /* =========================================================
     CALCULATED VALUES
     ========================================================= */

  function updateCalculated() {
    if (!inputs) return;

    const calculation =
      calc(type, inputs);

    root
      .querySelectorAll(
        "[data-calc]"
      )
      .forEach(
        (element) => {
          element.textContent =
            fmt(
              calculation[
                element.dataset.calc
              ]
            );
        }
      );
  }

  /* =========================================================
     DOWNLOAD GENERATED PDF
     ========================================================= */

  function triggerDownload() {
    if (
      !args.download_base64 ||
      !args.download_filename ||
      !args.download_token ||
      args.download_token ===
        lastDownloadToken
    ) {
      return;
    }

    lastDownloadToken =
      args.download_token;

    const binary =
      atob(
        args.download_base64
      );

    const bytes =
      new Uint8Array(
        binary.length
      );

    for (
      let index = 0;
      index < binary.length;
      index++
    ) {
      bytes[index] =
        binary.charCodeAt(index);
    }

    const blob =
      new Blob(
        [bytes],
        {
          type: "application/pdf",
        }
      );

    const url =
      URL.createObjectURL(blob);

    if (latestPdfUrl) {
      URL.revokeObjectURL(
        latestPdfUrl
      );
    }

    latestPdfUrl = url;

    latestPdfFilename =
      args.download_filename;

    const link =
      document.createElement("a");

    link.href = url;

    link.download =
      args.download_filename;

    document.body.appendChild(
      link
    );

    link.click();

    link.remove();

    const downloadButton =
      document.getElementById(
        "downloadBtn"
      );

    if (downloadButton) {
      downloadButton.disabled = false;

      downloadButton.textContent =
        "Download PDF";
    }

    busy = null;
  }

  /* =========================================================
     STREAMLIT RENDER
     ========================================================= */

  function onRender(event) {
    if (
      !event.data ||
      event.data.type !==
        "streamlit:render"
    ) {
      return;
    }

    args =
      event.data.args || {};

    /*
      Initial / Python-triggered state update.
    */
    if (
      args.response_token !==
      lastResponseToken
    ) {
      lastResponseToken =
        args.response_token;

      /*
        Only use Python's page value on initial rendering
        or after Python actually sends a new response token.

        Local Create quotation / Back navigation continues
        to work without waiting for Python.
      */
      if (args.page) {
        page = args.page;
      }

      if (
        args.quotation_type
      ) {
        type =
          args.quotation_type;
      }

      if (
        args.initial_inputs
      ) {
        inputs = {
          ...args.initial_inputs,
        };
      }

      /*
        Critical:
        Don't recreate default input values if local
        quotation already exists.
      */
      if (
        page === "quotation" &&
        !inputs
      ) {
        inputs =
          defaults(type);
      }

      busy = null;

      if (page === "quotation") {
        renderQuotation();
      } else {
        renderHome();
      }
    }

    /*
      Do NOT rerender the Home page on every Streamlit render.
      That was capable of replacing the clickable buttons
      after their event handlers were attached.
    */

    triggerDownload();

    if (page === "quotation") {
      setDynamicHeight();
    }
  }

  /* =========================================================
     START
     ========================================================= */

  window.addEventListener(
    "message",
    onRender
  );

  window.addEventListener(
    "load",
    () => {
      if (page === "home") {
        setFrameHeight(900);
      } else {
        setDynamicHeight();
      }
    }
  );

  /*
    Only use ResizeObserver for quotation pages.
    Otherwise the old long iframe can influence Home.
  */
  if (window.ResizeObserver) {
    new ResizeObserver(() => {
      if (
        page === "quotation"
      ) {
        setDynamicHeight();
      }
    }).observe(
      document.body
    );
  }

  init();
})();