from pydantic import BaseModel
from typing import Optional

from datetime import date


# Payment schemas
class PaymentBaseSchema(BaseModel):
    payment_date: date
    amount: float
    bank: str

class PaymentCreateSchema(PaymentBaseSchema):
    customer_id: int

class PaymentCustomerSchema(PaymentBaseSchema):
    customer: str

class PaymentSchema(PaymentBaseSchema):
    id: int
    customer_id: int

    class Config:
        orm_mode = True

# Customer schemas
class CustomerBaseSchema(BaseModel):
    first_name = str
    last_name = str

class CustomerCreateSchema(CustomerBaseSchema):
    pass

class CustomerSchema(CustomerBaseSchema):
    id: int

    class Config:
        orm_mode = True