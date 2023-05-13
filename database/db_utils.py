from sqlalchemy.orm import Session
import pandas as pd

from models.payment_models import Payment
from schemas.payment_schemas import PaymentCreateSchema
from database.database import SessionLocal


# Data base Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as error:
        print(f'ERROR: {error}')
    finally:
        db.close()

def get_payments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Payment).offset(skip).limit(limit).all()

def get_payment(db: Session, payment_id: int):
    return db.query(Payment).filter(Payment.id == payment_id).first()

def create_payment(db: Session, payment: PaymentCreateSchema):
    db_payment = Payment(
        payment_date=payment.payment_date,
        amount=payment.amount,
        bank=payment.bank,
        customer_name=payment.customer_name
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

def generate_payments_data_frame(payments):
    payments_content = {
        "payment_date": [],
        "customer_name": [],
        "amount": [],
        "bank": []
    }
    for payment in payments:
        payments_content["payment_date"].append(payment.payment_date)
        payments_content["customer_name"].append(payment.customer_name)
        payments_content["amount"].append(payment.amount)
        payments_content["bank"].append(payment.bank)
    payments_dataframe = pd.DataFrame(payments_content)
    return payments_dataframe