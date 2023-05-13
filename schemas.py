from pydantic import BaseModel, validator

from datetime import date


class PaymentBaseSchema(BaseModel):
    payment_date: date
    amount: float
    bank: str
    customer_name: str

    # @validator('payment_date', 'amount', 'bank', 'customer_name')
    # def is_required(cls, v):
    #     if v == '' or v == None:
    #         raise ValueError('value is required')
    #     return v
class PaymentCreateSchema(PaymentBaseSchema):
    pass

class PaymentSchema(PaymentBaseSchema):
    id: int

    class Config:
        orm_mode = True
