from pydantic import BaseModel
from datetime import date

from schemas import schema_examples


# Payment schemas
class PaymentBaseSchema(BaseModel):
    payment_date: date
    amount: float
    bank: str

class PaymentCreateSchema(PaymentBaseSchema):
    customer_id: int

class PaymentCustomerSchema(PaymentBaseSchema):
    customer: str

    class Config:
        schema_extra = schema_examples.example_payment_customer_eschema

class PaymentSchema(PaymentBaseSchema):
    id: int
    customer_id: int

    class Config:
        orm_mode = True
        schema_extra = schema_examples.example_payment_eschema
