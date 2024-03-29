from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.currency import (CurrencyInput, CurrencyOut, CurrencyResponse,
                                  MultipleCurrencyResponse)
from app.services.currency import CurrencyService

router = APIRouter(prefix="/currency", tags=["Currency"])


@router.get(
    "/", status_code=status.HTTP_200_OK, response_model=MultipleCurrencyResponse
)
def read_all_currencies(db: Session = Depends(get_db)):
    """Return all currencies in both coinbase_api and fictitious tables"""

    currency = CurrencyService()
    currency_list = currency.read_all(db=db)
    return MultipleCurrencyResponse(data=currency_list)


@router.get(
    "/{currency_code}", status_code=status.HTTP_200_OK, response_model=CurrencyResponse
)
def read_currency(currency_code: str, db: Session = Depends(get_db)):
    """Return one specific currency information"""

    currency = CurrencyService(currency_code=currency_code)
    currency_db = currency.read(db=db)
    currency_output = CurrencyOut(**currency_db.dict())
    return CurrencyResponse(data=currency_output)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CurrencyResponse)
def create_currency(currency_data: CurrencyInput, db: Session = Depends(get_db)):
    """Create new currency in `fictitious_currencies` table"""

    currency = CurrencyService(**currency_data.dict(exclude_none=True))
    currency_db = currency.create(db=db)
    currency_output = CurrencyOut(**currency_db.dict())
    return CurrencyResponse(data=currency_output)


@router.put(
    "/{currency_code}", status_code=status.HTTP_200_OK, response_model=CurrencyResponse
)
def update_currency(
    currency_code: str, currency_data: CurrencyInput, db: Session = Depends(get_db)
):
    """Updates existing currency in `fictitious_currencies`"""

    currency = CurrencyService(**currency_data.dict(exclude_none=True))
    currency_db = currency.update(db=db, original_currency_code=currency_code)
    currency_output = CurrencyOut(**currency_db.dict())
    return CurrencyResponse(data=currency_output)


@router.delete("/{currency_code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_currency(currency_code: str, db: Session = Depends(get_db)):
    """Deletes existing currency from `fictitious_currencies` table"""

    currency = CurrencyService(currency_code=currency_code)
    return currency.delete(db=db)
