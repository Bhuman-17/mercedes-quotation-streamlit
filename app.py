from __future__ import annotations

import base64
import re
import uuid
from datetime import datetime
from typing import Any

import streamlit as st

from quotation_ui.component import render_quotation_ui
from services.calculations import calculate_quotation
from services.pdf_service import build_quotation_pdf
from services.master_data import enrich_inputs_from_master, load_master_data


st.set_page_config(
    page_title="Mercedes-Benz Proforma Quotation",
    page_icon="🚘",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
      #MainMenu,
      header,
      footer,
      [data-testid="stToolbar"],
      [data-testid="stDecoration"] {
          display: none !important;
      }

      .stApp {
          background: #f1f2f4;
      }

      .block-container {
          padding: 0 !important;
          max-width: 100% !important;
      }

      iframe[title="mercedes_quotation_ui"] {
          border: 0 !important;
          width: 100% !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


def ss_default(key: str, value: Any) -> None:
    if key not in st.session_state:
        st.session_state[key] = value


ss_default("page", "home")
ss_default("quotation_type", "individual")
ss_default("initial_inputs", None)
ss_default("status_message", None)
ss_default("status_kind", None)
ss_default("response_token", str(uuid.uuid4()))
ss_default("download_base64", None)
ss_default("download_filename", None)
ss_default("download_token", None)
ss_default("last_action_nonce", None)


try:
    MASTER_DATA = load_master_data()
    MASTER_DATA_ERROR = None
except Exception as exc:
    MASTER_DATA = {"models": [], "sourceFiles": {}}
    MASTER_DATA_ERROR = f"{type(exc).__name__}: {exc}"


def clear_download() -> None:
    st.session_state.download_base64 = None
    st.session_state.download_filename = None
    st.session_state.download_token = None


def set_response(message: str, kind: str = "success") -> None:
    st.session_state.status_message = message
    st.session_state.status_kind = kind
    st.session_state.response_token = str(uuid.uuid4())


def safe_filename(value: str, fallback: str) -> str:
    """
    Convert customer/FP/model values into a Windows-safe filename section.
    """

    value = str(value or "").strip()

    # Remove characters Windows does not permit in filenames.
    value = re.sub(r'[<>:"/\\|?*]', "", value)

    # Replace one or more spaces with underscore.
    value = re.sub(r"\s+", "_", value)

    # Remove unnecessary leading/trailing punctuation.
    value = value.strip("._- ")

    return value or fallback


def create_pdf_filename(inputs: dict[str, Any]) -> str:
    """
    Example:
    Bhuman_Wadekar_BU_Bhandari_C220D_Proforma_Quotation.pdf
    """

    customer_name = safe_filename(
        inputs.get("customerName", ""),
        "Customer",
    )

    fp_name = safe_filename(
        inputs.get("franchisePartnerName", ""),
        "FP",
    )

    model_name = safe_filename(
        inputs.get("modelName", ""),
        "Model",
    )

    return (
        f"{customer_name}_"
        f"{fp_name}_"
        f"{model_name}_"
        f"Proforma_Quotation.pdf"
    )


def handle_download(action: dict[str, Any]) -> None:
    quotation_type = str(
        action.get("quotation_type") or "individual"
    )

    inputs = dict(
        action.get("inputs") or {}
    )

    # Re-resolve master-controlled values on the server so the PDF always
    # uses the current pricing/RV workbook, even if a browser value is edited.
    inputs = enrich_inputs_from_master(inputs, MASTER_DATA)

    # Fixed business rules for Individual and Corporate quotations.
    if quotation_type in {"individual", "corporate"}:
        inputs["handlingCharges"] = 0
        inputs["securityDepositFinance"] = 0

    calculated = calculate_quotation(
        quotation_type,
        inputs,
    )

    generated_at = datetime.now()

    document_id = (
        f"PQ-{generated_at:%Y%m%d-%H%M%S}"
    )

    pdf_bytes = build_quotation_pdf(
        quotation_type=quotation_type,
        inputs=inputs,
        calc=calculated,
        quote_number=document_id,
        quote_date=generated_at.strftime(
            "%A, %B %d, %Y"
        ),
    )

    pdf_filename = create_pdf_filename(inputs)

    st.session_state.page = "quotation"
    st.session_state.quotation_type = quotation_type
    st.session_state.initial_inputs = inputs

    st.session_state.download_base64 = (
        base64.b64encode(pdf_bytes).decode("ascii")
    )

    st.session_state.download_filename = pdf_filename

    st.session_state.download_token = str(
        uuid.uuid4()
    )

    set_response(
        f"PDF prepared successfully: {pdf_filename}",
        "success",
    )


component_value = render_quotation_ui(
    page=st.session_state.page,
    quotation_type=st.session_state.quotation_type,
    initial_inputs=st.session_state.initial_inputs,
    status_message=st.session_state.status_message,
    status_kind=st.session_state.status_kind,
    response_token=st.session_state.response_token,
    download_base64=st.session_state.download_base64,
    download_filename=st.session_state.download_filename,
    download_token=st.session_state.download_token,
    master_data=MASTER_DATA,
    master_data_error=MASTER_DATA_ERROR,
    key="mercedes-quotation-main",
)


if isinstance(component_value, dict):
    nonce = component_value.get("nonce")

    if (
        nonce
        and nonce
        != st.session_state.last_action_nonce
    ):
        st.session_state.last_action_nonce = nonce

        action_name = component_value.get("action")

        try:
            if action_name == "download_pdf":
                handle_download(component_value)

            else:
                set_response(
                    "Unknown application action.",
                    "error",
                )

        except Exception as exc:
            clear_download()

            set_response(
                f"{type(exc).__name__}: {exc}",
                "error",
            )

        st.rerun()