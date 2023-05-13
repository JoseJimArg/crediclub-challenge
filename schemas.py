from pydantic import BaseModel

from datetime import date


class PaymentBaseSchema(BaseModel):
    date_payment: date
    amount: float
    bank: str
    customer_name: str

class PaymentCreateSchema(PaymentBaseSchema):
    pass

class PaymentSchema(PaymentBaseSchema):
    id: int

    class Config:
        orm_mode = True
