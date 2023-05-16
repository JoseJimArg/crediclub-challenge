import pandas as pd
from sqlalchemy.orm import Session

from models.payment_models import Payment, Customer
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
    payments = db.query(Payment).offset(skip).limit(limit).all()
    return payments

def get_payment(db: Session, payment_id: int):
    return db.query(Payment).filter(Payment.id == payment_id).first()

def find_payment(db: Session, payment: PaymentCreateSchema, customer_id: int):
    return db.query(Payment).filter(
        Payment.payment_date == payment.payment_date,
        Payment.amount == payment.amount,
        Payment.bank == payment.bank,
        Payment.customer_id == customer_id
    ).first()

def is_payment_data_valid(payment: PaymentCreateSchema):
    # The others values are covered by the Schemas
    if payment.amount > 0 and payment.bank != "":
        return True
    return False

def create_payment(db: Session, payment: PaymentCreateSchema, customer_id: int):
    if is_payment_data_valid(payment):
        db_payment = Payment(
            payment_date=payment.payment_date,
            amount=payment.amount,
            bank=payment.bank,
            customer_id=customer_id
        )
        db.add(db_payment)
        db.commit()
        db.refresh(db_payment)
        return db_payment
    return ValueError("The Payment bank is empty or the amount is not valid")

def generate_payments_data_frame(payments):
    payments_content = {
        "payment_date": [],
        "customer": [],
        "amount": [],
        "bank": []
    }
    for payment in payments:
        payments_content["payment_date"].append(payment.payment_date)
        payments_content["customer"].append(
                payment.customer.first_name +
                " " +
                payment.customer.last_name
            ),
        payments_content["amount"].append(payment.amount)
        payments_content["bank"].append(payment.bank)
    payments_dataframe = pd.DataFrame(payments_content)
    return payments_dataframe

def get_or_create_customer_by_full_name(db: Session, customer_fullname: str):
    # The customer_fullname cant be empty
    if customer_fullname == "":
        return ValueError("The Customer name is empty")
    # If there is not allready a customer with that fullname, it must be created.
    try:
        incoming_first_name = customer_fullname.split(sep=" ")[0]
        incoming_last_name = customer_fullname.split(sep=" ")[1]
    except:
        return ValueError("There is no last_name")
    # Finds customer in the database
    actual_customer_db = db.query(Customer).filter(
        Customer.first_name == incoming_first_name,
        Customer.last_name == incoming_last_name
    ).first()
    if actual_customer_db:
        return actual_customer_db
    else:
        # Create a new one because it was not in the database
        new_customer = Customer(
            first_name = incoming_first_name,
            last_name = incoming_last_name
        )
        db.add(new_customer)
        db.commit()
        db.refresh(new_customer)
        return new_customer

def get_customer_by_fullname(db: Session, customer_fullname: str):
    incoming_first_name = customer_fullname.split(sep=" ")[0]
    incoming_last_name = customer_fullname.split(sep=" ")[1]
    # Finds customer in the database
    return db.query(Customer).filter(
        Customer.first_name == incoming_first_name,
        Customer.last_name == incoming_last_name
    ).first()