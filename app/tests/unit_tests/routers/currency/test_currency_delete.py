from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import CoinbaseCurrenciesPublicApiModel
from app.schemas.currency import CurrencyInput

TEST_FICTITIOUS_CURRENCY_CODE = "HURB"
TEST_COINBASE_CURRENCY_CODE = "BRL"


def test_found_in_db(
    client: TestClient, session: Session, create_hurb_currency: CurrencyInput
):
    """
    Try to delete a fictitious currency found in database
    """
    currency = CurrencyInput(**create_hurb_currency)
    res = client.delete(f"/currency/{currency.currency_code}")
    assert res.status_code == 204
    currency_db: CoinbaseCurrenciesPublicApiModel = (
        session.query(CoinbaseCurrenciesPublicApiModel)
        .filter(
            CoinbaseCurrenciesPublicApiModel.currency_code == currency.currency_code
        )
        .first()
    )
    assert currency_db is None


def test_not_found_in_db(client: TestClient, session: Session):
    """
    Try to delete a fictitious currency not found in database
    """
    res = client.delete(f"/currency/{TEST_FICTITIOUS_CURRENCY_CODE}")

    assert res.status_code == 404
    currency_db: CoinbaseCurrenciesPublicApiModel = (
        session.query(CoinbaseCurrenciesPublicApiModel)
        .filter(
            CoinbaseCurrenciesPublicApiModel.currency_code
            == TEST_FICTITIOUS_CURRENCY_CODE
        )
        .first()
    )
    assert currency_db is None
