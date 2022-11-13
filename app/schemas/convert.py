from datetime import datetime

from pydantic import BaseModel, validator


class InputConversionSchema(BaseModel):
    from_this: str
    to: str
    amount: float

    @validator("from_this")
    def do_uppercase_on_fromthis_field(cls, from_this: str):
        return from_this.upper()

    @validator("to")
    def do_uppercase_on_to_field(cls, to: str):
        return to.upper()


class OutputConversionSchema(InputConversionSchema):
    converted_value: float
    updated_at: datetime


class ConvertModelResponse(BaseModel):
    data: OutputConversionSchema
