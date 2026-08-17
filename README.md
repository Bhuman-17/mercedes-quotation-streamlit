# Mercedes-Benz India Proforma Quotation — Streamlit

Streamlit application with a custom HTML/CSS quotation UI matching the supplied Mercedes-Benz India quotation layout.

## Quotation types
- Individual
- Corporate / Company
- Leasing

## Current rules
- Individual and Corporate Handling Charges are fixed at 0 and locked.
- Individual and Corporate Downpayment and Loan Amount are manual inputs for each finance plan.
- Finance tenure is selected from 12, 24, 36, 48, 60, 72 or 84 months.
- No database connection is used.
- Print and Download PDF buttons appear below the completed quotation.
- The supplied Mercedes-Benz image is used as the home-page background.

## Run locally
```powershell
uv sync
uv run streamlit run app.py
```

or on Windows:
```powershell
.\setup.ps1
.\run.ps1
```

## Streamlit Community Cloud
Deploy the GitHub repository with `app.py` as the main file. No database secrets are required.
