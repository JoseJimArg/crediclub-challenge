from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from schemas import PaymentSchema, PaymentCreateSchema
from database import SessionLocal
import utils

# Initialize the app
app = FastAPI()

# Data base Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as error:
        print(f'ERROR: {error}')
    finally:
        db.close()

# Default / message
@app.get("/")
def read_root():
    return {"Hello": "Crediclub"}

@app.get("/payments/", response_model=list[PaymentSchema])
def read_payments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    payments = utils.get_payments(db, skip=skip, limit=limit)
    return payments

@app.get("/payments/{payment_id}", response_model=PaymentSchema)
def read_payment(payment_id: int, db: Session = Depends(get_db)):
    db_payment = utils.get_payment(db=db, payment_id=payment_id)
    if db_payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return db_payment

@app.post("/payments/", response_model=PaymentSchema)
def write_payment(payment: PaymentCreateSchema, db: Session = Depends(get_db)):
    # TO-DO Validates if the value exists
    # code here
    # Compare all the data and look if there are allready in the data base
    # This is because we don't have a identifier from the request
    return utils.create_payment(db=db, payment=payment)