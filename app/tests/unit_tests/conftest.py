import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine, get_db
from app.main import app
from app.models import CoinbaseCurrenciesPublicApiModel, FictitiousCoinModel
from app.schemas.currency import Currency
from app.tests.stubs import CURRENCY_VALUES_TEST_DATA

client = TestClient(app)

# Establishing database connection
@pytest.fixture
def session():
    # Reset database from previous test result
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def insert_test_data(session: Session):
    """Updates `CoinbaseCurrenciesPublicApiModels` table with test data rates"""
    db = SessionLocal()

    response = CURRENCY_VALUES_TEST_DATA
    currencies = response["data"]["rates"]
    for currency_code, rate in currencies.items():
        currency = Currency(currency_code=currency_code, rate=rate)
        currency_db = CoinbaseCurrenciesPublicApiModel(
            currency_code=currency.currency_code, rate=currency.rate
        )
        db.add(currency_db)
    db.commit()
    db.close()


@pytest.fixture
def client(session: Session, insert_test_data):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    # Change get_db dependency to override_get_db in order to manipulate test database
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture
def coinbase_currencies_public_api_dummy_data() -> dict:
    return {"currency_code": "BRL"}


@pytest.fixture
def fictitious_dummy_data() -> dict:
    return {"currency_code": "HURB"}


@pytest.fixture
def fictitious_currency_data_hurb() -> dict:
    return {"currency_code": "HURB", "rate": 4.0, "backed_by": "BRL"}


@pytest.fixture
def fictitious_currency_data_test():
    return {"currency_code": "TEST", "rate": 0.4, "backed_by": "BRL"}


@pytest.fixture
def create_hurb_currency(
    client: TestClient, session: Session, fictitious_currency_data_hurb: dict
) -> dict:
    currency_db = FictitiousCoinModel(**fictitious_currency_data_hurb)
    session.add(currency_db)
    session.commit()
    return fictitious_currency_data_hurb


@pytest.fixture
def create_test_currency(
    client: TestClient, session: Session, fictitious_currency_data_test: dict
) -> dict:
    currency_db = FictitiousCoinModel(**fictitious_currency_data_test)
    session.add(currency_db)
    session.commit()
    return fictitious_currency_data_test
