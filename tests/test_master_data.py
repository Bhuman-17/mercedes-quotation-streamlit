from pathlib import Path

from services.calculations import calculate_quotation
from services.master_data import enrich_inputs_from_master, load_master_data


ROOT = Path(__file__).resolve().parents[1]


def _model(master, name):
    return next(model for model in master["models"] if model["name"] == name)


def test_price_list_drives_model_and_ex_showroom():
    master = load_master_data()
    c220d = _model(master, "C 220d")
    assert c220d["powertrains"] == ["Diesel"]
    assert c220d["prices"]["Diesel"] == 6_120_000

    eqa = _model(master, "EQA 250+")
    assert eqa["powertrains"] == ["Electric"]
    assert eqa["prices"]["Electric"] == 6_720_000


def test_rv_lookup_diesel_and_electric_use_correct_grid_block():
    master = load_master_data()

    c220d = _model(master, "C 220d")
    # C Class (W206), Diesel, 10,000 Km, 4 years / 48 months.
    assert c220d["rvSource"]["Diesel"] == "C Class (W206)"
    assert c220d["rvRates"]["Diesel"]["10000"]["48"] == 0.63

    eqa = _model(master, "EQA 250+")
    # EQA is displayed as Electric but reads the single first RV block.
    assert eqa["rvSource"]["Electric"] == "EQA"
    assert eqa["rvRates"]["Electric"]["15000"]["48"] == 0.60


def test_server_enrichment_enforces_master_price_and_rv_rate():
    master = load_master_data()
    inputs = {
        "modelName": "C 220d",
        "powertrain": "Diesel",
        "exShowroomPrice": 1,
        "annualMileageAgility": 10_000,
        "termAgility": 48,
    }
    enriched = enrich_inputs_from_master(inputs, master)
    assert enriched["exShowroomPrice"] == 6_120_000
    assert enriched["rvPercentageAgility"] == 0.63


def test_buyback_is_rv_percent_times_net_ex_showroom():
    result = calculate_quotation(
        "individual",
        {
            "exShowroomPrice": 6_120_000,
            "monthlyOffers": 100_000,
            "welcomeBenefit": 100_000,
            "loyaltyOffer": 0,
            "otherOffer": 0,
            "rvPercentageAgility": 0.63,
        },
    )
    assert result["netExShowroom"] == 5_920_000
    assert result["buybackAgility"] == 3_729_600
