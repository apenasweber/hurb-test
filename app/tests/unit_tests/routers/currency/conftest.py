import pytest


@pytest.fixture
def real_currency_data_brl() -> dict:
    return {"currency_code": "BRL", "backed_by": "USD", "rate": 5.59}


@pytest.fixture
def fictitious_currency_data_test() -> dict:
    return {"currency_code": "TEST", "backed_by": "USD", "rate": 5.59}


@pytest.fixture
def fictitious_currency_data_hurb_alternative_input() -> dict:
    return {
        "currency_code": "HURB",
        "backed_by": "BRL",
        "amount": 12.0,
        "backed_currency_amount": 3.0,
    }


@pytest.fixture
def fictitious_currency_data_hurb_missing_field_input() -> dict:
    return {"currency_code": "HURB", "backed_by": "BRL", "amount": 12.0}


@pytest.fixture
def fictitious_currency_data_hurb_all_fields_input() -> dict:
    return {
        "currency_code": "HURB",
        "backed_by": "BRL",
        "rate": 4.0,
        "amount": 12.0,
        "backed_currency_amount": 3.0,
    }
