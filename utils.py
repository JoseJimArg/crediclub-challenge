from sqlalchemy.orm import Session

from models import Payment
from schemas import PaymentCreateSchema

def get_payments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Payment).offset(skip).limit(limit).all()

def get_payment(db: Session, payment_id: int):
    return db.query(Payment).filter(Payment.id == payment_id).first()

def create_payment(db: Session, payment: PaymentCreateSchema):
    db_payment = Payment(
        date_payment=payment.date_payment,
        amount=payment.amount,
        bank=payment.bank,
        customer_name=payment.customer_name
    )
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment