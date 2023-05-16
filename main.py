from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import pandas as pd
from io import BytesIO

from schemas.payment_schemas import PaymentSchema, PaymentCustomerSchema
import database.db_utils as db_utils


# Initialize the app
app = FastAPI()

# Default / message
@app.get("/")
def read_root():
    return {"Hello": "Crediclub!!!"}

@app.get("/payments/", response_model=list[PaymentSchema])
async def read_payments(skip: int = 0, 
                        limit: int = 100, 
                        db: Session = Depends(db_utils.get_db)):
    """
    Returns: List of payments.
    """

    payments = db_utils.get_payments(db, skip=skip, limit=limit)
    return payments

@app.get("/payments/customers", response_model=list[PaymentCustomerSchema])
async def read_payments_whit_customers_name(skip: int = 0, 
                        limit: int = 100, 
                        db: Session = Depends(db_utils.get_db)):
    """
    Returns:
      List of payments whit Customer name insted of Customer id.

    """
    
    payments = db_utils.get_payments(db, skip=skip, limit=limit)
    payments_whit_clients = []
    for payment in payments:
        new_payment = PaymentCustomerSchema(
            payment_date = payment.payment_date,
            amount = payment.amount,
            bank = payment.bank,
            customer = str(payment.customer.first_name) + 
                " " + 
                str(payment.customer.last_name)
        )
        payments_whit_clients.append(new_payment)
    return payments_whit_clients

@app.get("/payments/download_csv", response_class=StreamingResponse)
async def read_payments_csv(skip: int = 0, 
                            limit: int = 100, 
                            db: Session = Depends(db_utils.get_db)):
    """
    Returns: File .csv whit a list of Payments.

    Includes Spanish headers:
        - Fecha
        - Cliente
        - Monto
        - Provedor

    The "Cliente" value is first_name + " " + last_name
    """

    payments = db_utils.get_payments(db, skip=skip, limit=limit)
    # generate the file from the DataFrame
    payments_dataframe = db_utils.generate_payments_data_frame(payments=payments)
    # Wrtite the new csv file whit the original headers
    headers = ["Fecha", "Cliente", "Monto", "Proveedor"]
    payments_csv_data = payments_dataframe.to_csv(index=False, header=headers)
    response = StreamingResponse(
        iter([payments_csv_data]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=payments.csv"
    return response

@app.get("/payments/download_xlsx", response_class=StreamingResponse)
async def read_payments_csv(skip: int = 0, 
                            limit: int = 100, 
                            db: Session = Depends(db_utils.get_db)):
    """
    Returns: File Excel file (.xlsx) whit a list of Payments.

    Includes Spanish headers:
        - Fecha
        - Cliente
        - Monto
        - Provedor

    The "Cliente" value is first_name + " " + last_name
    """
    payments = db_utils.get_payments(db, skip=skip, limit=limit)
    # generate the file from the DataFrame
    payments_dataframe = db_utils.generate_payments_data_frame(payments=payments)

    # List whit the original headers to persist the original format
    headers = ["Fecha", "Cliente", "Monto", "Proveedor"]
    excel_buffer = BytesIO()
    excel_writer = pd.ExcelWriter(excel_buffer, engine="xlsxwriter")
    payments_dataframe.to_excel(excel_writer=excel_writer, 
                                index=False, header=headers, 
                                sheet_name="Payments")
    excel_writer.close()

    # Save in a variable the file created whit the excel_writer
    # This variable will be returned by the API
    excel_file_data = excel_buffer.getvalue()
    excel_buffer.close()

    # Create response whit the file
    response = StreamingResponse(
        iter([excel_file_data]), 
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response.headers["Content-Disposition"] = "attachment; filename=payments.xlsx"
    return response

@app.get("/payments/total")
async def read_payments_total(skip: int = 0, 
                              limit: int = None, 
                              db: Session = Depends(db_utils.get_db)):
    """
    Returns: float number whit the total amount of the Payments.
    """

    payments = db_utils.get_payments(db, skip=skip, limit=limit)
    total = 0.0
    for payment in payments:
        total += float(payment.amount)
    data = {
        "payments_total": round(total, 2)
    }
    return data

@app.get("/payments/{payment_id}", response_model=PaymentSchema)
async def read_payment(payment_id: int, 
                       db: Session = Depends(db_utils.get_db)):
    """
    Returns: Payment by his identifier (id).
    """

    db_payment = db_utils.get_payment(db=db, payment_id=payment_id)
    if db_payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return db_payment

@app.post("/payments/", response_model=PaymentSchema)
def write_payment_customer_name(payment: PaymentCustomerSchema, 
                  db: Session = Depends(db_utils.get_db)):
    """
    Save a new record of Payment. Important, it takes the name of the customer
    instead of a identifier like an id. \n
    Checks if the customer allready exists, if is the case, only link the payment
    to the customer, otherwise, create a new customer whit the given name and link the payment.

    Returns: a new Payment record with the customer id assigned.
    """

    # Because we have customers and can not be payments whitout custmers
    #  we need to create a customer of the payments if it is not exists
    #  or link the new paymet whit an existing Customer.
    customer = db_utils.get_or_create_customer_by_full_name(
        db=db, customer_fullname=payment.customer
    ) 
    # Validates if the value exists
    if db_utils.check_payment(db=db, payment=payment, customer_id=customer.id):
        raise HTTPException(status_code=409, detail="Register allready exists")
    # Compare all the data and look if there are allready in the data base
    # This is because we don't have a identifier from the request
    return db_utils.create_payment(db=db, payment=payment, customer_id=customer.id)