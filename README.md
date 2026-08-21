# Mercedes-Benz India Proforma Quotation - Streamlit

Streamlit application with a custom HTML/CSS quotation UI matching the supplied Mercedes-Benz India quotation layout.

## Quotation types
- Individual
- Corporate / Company
- Leasing

## Dynamic reference masters
The app reads these files from the `reference` folder at runtime:

- `Price List Compilation.xlsx`
- `RV Grid.xlsx`

Do not hardcode prices or RV rates in the application. To update business data, replace either workbook using the SAME filename, then restart locally or push the updated reference file to GitHub so Streamlit Cloud redeploys.

### What comes from the pricing workbook
- Model dropdown (only models with a valid value in the latest/right-most Ex-Showroom column)
- Powertrain classification: Petrol / Diesel / Electric
- Ex-Showroom Price

### Star Agility+ RV logic
- Tenure: 12 / 24 / 36 / 48 / 60 months
- Annual Mileage: 10,000 / 15,000 / 20,000 Km
- RV Grid Percentage: looked up from `RV Grid.xlsx`
- Buyback Value = RV Grid Percentage x Net Ex-Showroom Price
- Electric/BEV models display `Electric` in the quotation. Their RV lookup uses the single primary rate block in the supplied RV grid (the block positioned under the Petrol-side columns).
- Star Finance is not driven by this RV grid.

If a selected model/mileage/tenure combination has no RV rate in the workbook, the UI shows `N/A` rather than inventing a value.

## Existing business rules
- Individual and Corporate Handling Charges are fixed at 0 and locked.
- Star Finance Security Deposit is fixed at 0 and locked.
- Individual and Corporate Downpayment and Loan Amount remain manual inputs.
- Star Finance tenure remains available up to 84 months.
- No database connection is used.
- Print and Download PDF buttons appear below the completed quotation.
- PDF output remains compacted to two landscape A4 pages.

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

When a reference workbook changes:
```powershell
git add reference/
git commit -m "Update quotation master data"
git push origin main
```

Streamlit Community Cloud will redeploy using the latest reference files.
