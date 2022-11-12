from datetime import datetime
from typing import List, Optional, Union

from fastapi import HTTPException, status
from pydantic import BaseModel, validator
from sqlalchemy.orm import Query, Session

from app.models import CoinbaseCurrenciesPublicApiModel, FictitiousCoinModel
from app.schemas.currency import CurrencyDatabase


class CurrencyService(BaseModel):
    currency_code: Optional[str]
    rate: Optional[float]
    backed_by: Optional[str]
    updated_at: Optional[datetime]

    @validator("currency_code")
    def uppercase_currency_code(cls, currency_code: str):

        return currency_code.upper()

    def _query_coinbase_api_fictitious_union(self, db: Session) -> Query:

        coinbase_api_table_query = db.query(CoinbaseCurrenciesPublicApiModel).filter(
            CoinbaseCurrenciesPublicApiModel.currency_code == self.currency_code
        )
        fictitious_table_query = db.query(FictitiousCoinModel).filter(
            FictitiousCoinModel.currency_code == self.currency_code
        )
        return coinbase_api_table_query.union(fictitious_table_query)

    def _find_currency_in_db(self, db: Session) -> Union[CurrencyDatabase, None]:
        """If currency exists in `coinbase_api_currencies` or `fictitious_currencies` returns it else return `None`"""

        return self._query_coinbase_api_fictitious_union(db=db).first()

    def _find_backed_currency_in_db(self, db: Session) -> Union[CurrencyDatabase, None]:
        """If backed currency exists in `coinbase_api_currencies` returns it else returns `None`"""

        coinbase_api_table_query = db.query(CoinbaseCurrenciesPublicApiModel).filter(
            CoinbaseCurrenciesPublicApiModel.currency_code == self.backed_by
        )
        return coinbase_api_table_query.first()

    def read_all(self, db: Session) -> List:
        """Returns a list of currencies from `coinbase_api_currencies` and `fictitious_currencies` tables"""

        coinbase_api_table_query = db.query(
            CoinbaseCurrenciesPublicApiModel.currency_code.label("currency_code"),
            CoinbaseCurrenciesPublicApiModel.rate,
            CoinbaseCurrenciesPublicApiModel.backed_by,
            CoinbaseCurrenciesPublicApiModel.updated_at,
            CoinbaseCurrenciesPublicApiModel.currency_type,
        ).order_by(CoinbaseCurrenciesPublicApiModel.currency_code)

        fictitious_table_query = db.query(
            FictitiousCoinModel.currency_code.label("currency_code"),
            FictitiousCoinModel.rate,
            FictitiousCoinModel.backed_by,
            FictitiousCoinModel.updated_at,
            FictitiousCoinModel.currency_type,
        ).order_by(FictitiousCoinModel.currency_code)

        return (
            coinbase_api_table_query.union(fictitious_table_query)
            .order_by("currency_code")
            .all()
        )

    def read(self, db: Session) -> CurrencyDatabase:
        """If currency exists in `coinbase_api_currencies` or `fictitious_currencies` returns it else return `None`"""

        if currency := self._find_currency_in_db(db=db):
            return CurrencyDatabase.from_orm(currency)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Currency code {self.currency_code} not found",
            )

    def create(self, db: Session) -> CurrencyDatabase:
        """Creates a new currency in `fictitious_currencies` if not found in database"""

        # Raises an HTTP exception if currency already exists
        if self._find_currency_in_db(db=db):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Currency code {self.currency_code} already exists",
            )

        # Raises an HTTP exception if backed currency is not found
        if not self._find_backed_currency_in_db(db=db):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Backed currency code {self.backed_by} is not valid",
            )

        currency = FictitiousCoinModel(**self.dict())
        db.add(currency)
        db.commit()
        db.refresh(currency)
        return CurrencyDatabase.from_orm(currency)

    def update(self, db: Session, original_currency_code: str) -> CurrencyDatabase:
        """Updated currency in `fictitious_currencies` if found in database"""

        original_currency_code = original_currency_code.upper()
        if (
            original_currency_db_coinbase_api := db.query(
                CoinbaseCurrenciesPublicApiModel
            )
            .filter(
                CoinbaseCurrenciesPublicApiModel.currency_code == original_currency_code
            )
            .first()
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Currency code {original_currency_code} is an coinbase_api currency and cannot be changed",
            )

        # In case of currency code change
        if original_currency_code != self.currency_code:
            original_currency_code_in_db = (
                db.query(FictitiousCoinModel)
                .filter(FictitiousCoinModel.currency_code == original_currency_code)
                .first()
            )
            # Raises an HTTP exception if original currency code is not found
            if not original_currency_code_in_db:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Original currency code {original_currency_code} not found",
                )
            # Raises an HTTP exception if new currency code is not found
            if self._find_currency_in_db(db=db):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"New currency code {self.currency_code} already exists",
                )
        elif not self._find_currency_in_db(db=db):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Currency code {self.currency_code} not found",
            )

        # Raises an HTTP exception if backed currency is not found
        if not self._find_backed_currency_in_db(db=db):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Backed currency code {self.backed_by} not found",
            )

        if original_currency_code != self.currency_code:
            currency_code_db = original_currency_code
        else:
            currency_code_db = self.currency_code

        currency_db = db.query(FictitiousCoinModel).filter(
            FictitiousCoinModel.currency_code == currency_code_db
        )
        currency_db.update(self.dict())
        db.commit()

        updated_currency = self._find_currency_in_db(db=db)
        return CurrencyDatabase.from_orm(updated_currency)

    def delete(self, db: Session):
        """Delete currency from `fictitious_currencies` if found in database"""

        currency = self._find_currency_in_db(db=db)

        # Raises an HTTP exception if currency is not found
        if not currency:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Currency code {self.currency_code} not found",
            )

        # Raises an HTTP exception if currency is an coinbase_api currency
        if currency.currency_type == "coinbase_api":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Currency code {self.currency_code} is an coinbase_api currency and cannot be deleted",
            )

        currency_query = db.query(FictitiousCoinModel).filter(
            FictitiousCoinModel.currency_code == self.currency_code
        )
        currency_query.delete()
        db.commit()
        return {"message": f"Currency code {self.currency_code} deleted"}
