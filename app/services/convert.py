from sqlalchemy.orm import Session

from app.models import CoinbaseCurrenciesPublicApiModel
from app.schemas.convert import OutputConversionSchema
from app.services.currency import CurrencyService


class ConvertOperator:
    """Handle the conversion operation between two currencies"""

    def __init__(self, from_this: str, to: str, amount: float, db: Session) -> None:
        self.from_this = CurrencyService(currency_code=from_this).read(db=db)
        self.to = CurrencyService(currency_code=to).read(db=db)
        self.amount = amount
        self.db = db

    def _convert_to_usd(self, currency: CoinbaseCurrenciesPublicApiModel) -> None:
        if currency.backed_by != "USD":
            backed_currency = CurrencyService(currency_code=currency.backed_by).read(
                db=self.db
            )
            currency.rate = currency.rate * backed_currency.rate
            currency.backed_by = "USD"

    def convert_currencies(self) -> OutputConversionSchema:
        if self.from_this.backed_by != self.to.backed_by:
            self._convert_to_usd(currency=self.from_this)
            self._convert_to_usd(currency=self.to)

        amount_in_usd = self.amount / self.from_this.rate
        converted_value = amount_in_usd * self.to.rate

        return OutputConversionSchema(
            from_this=self.from_this.currency_code,
            to=self.to.currency_code,
            amount=self.amount,
            converted_value=round(converted_value, 2),
            updated_at=self.from_this.updated_at,
        )
