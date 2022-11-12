from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.convert import ConvertModelResponse, InputConversionSchema
from app.services.convert import ConvertOperator

router = APIRouter(prefix="/convert", tags=["Convert"])


@router.get("/", status_code=status.HTTP_200_OK, response_model=ConvertModelResponse)
def convert(params: InputConversionSchema = Depends(), db: Session = Depends(get_db)):

    converter = ConvertOperator(**params.dict(), db=db)
    converter_result = converter.convert_currencies()
    return ConvertModelResponse(data=converter_result)
