from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.openapi.models import Contact

from sqlalchemy.orm import Session
from io import BytesIO
from schemas.payment_schemas import PaymentSchema, PaymentCustomerSchema

import pandas as pd
import database.db_utils as db_utils


# Initialize the app
app = FastAPI(
    title = "CrediClub Technical Test API",
    description = "API for interact with Payments, Customers an Banks.",
    contact = Contact(
        name = "Jose de Jesus Jimenez Arguelles",
        email = "jose.jimenez.dev@gmail.com"
    )
)

# Default / message
@app.get("/")
def get_root():
    """
    # Hello!
    """
    return {"Hello": "Crediclub!!!"}

@app.get("/payments/", response_model=list[PaymentSchema])
async def get_payments(skip: int = 0, 
                        limit: int = 100, 
                        db: Session = Depends(db_utils.get_db)):
    """
    ## Parameters
        - skip: This parameter indicates the number of elements to skip or omit when performing an operation. The default value is 0, which means no elements will be skipped at the beginning.
        - limit: This parameter sets the maximum limit of elements to be returned in an operation. The default value is 100, which means up to 100 elements will be returned at most.

    ## Returns
        - json list of Payments with the customer specified by id.
            - The id number is assingned by the back end when a Customer is registered.
    """

    payments = db_utils.get_payments(db, skip=skip, limit=limit)
    return payments

@app.get("/payments/customers", response_model=list[PaymentCustomerSchema])
async def get_payments_whit_customers_name(skip: int = 0, 
                        limit: int = 100, 
                        db: Session = Depends(db_utils.get_db)):
    """
    ## Parameters
        - skip: This parameter indicates the number of elements to skip or omit when performing an operation. The default value is 0, which means no elements will be skipped at the beginning.
        - limit: This parameter sets the maximum limit of elements to be returned in an operation. The default value is 100, which means up to 100 elements will be returned at most.

    ## Returns
        - json list of Payments with the customer specified by **full name**. 
            - Full name consist of "first_name" + " " + "last_name".

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
async def get_payments_in_csv(skip: int = 0, 
                            limit: int = 100, 
                            db: Session = Depends(db_utils.get_db)):
    """
    ## Parameters
        - skip: This parameter indicates the number of elements to skip or omit when performing an operation. The default value is 0, which means no elements will be skipped at the beginning.
        - limit: This parameter sets the maximum limit of elements to be returned in an operation. The default value is 100, which means up to 100 elements will be returned at most.

    ## Returns 
    - File .csv whit a list of Payments.

    Includes Spanish headers:
        - Fecha
        - Cliente
        - Monto
        - Provedor

    The "Cliente" column is first_name + " " + last_name
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
async def get_payments_excel_file(skip: int = 0, 
                            limit: int = 100, 
                            db: Session = Depends(db_utils.get_db)):
    """
    ## Parameters
        - skip: This parameter indicates the number of elements to skip or omit when performing an operation. The default value is 0, which means no elements will be skipped at the beginning.
        - limit: This parameter sets the maximum limit of elements to be returned in an operation. The default value is 100, which means up to 100 elements will be returned at most.

    ## Returns 
    - Excel file (xlsx) whit a list of Payments.

    Includes Spanish headers:
        - Fecha
        - Cliente
        - Monto
        - Provedor

    The "Cliente" column is first_name + " " + last_name
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
async def get_total_payments(skip: int = 0, 
                              limit: int = None, 
                              db: Session = Depends(db_utils.get_db)):
    """
    ## Parameters
        - skip: This parameter indicates the number of elements to skip or omit when performing an operation. The default value is 0, which means no elements will be skipped at the beginning.
        - limit: This parameter sets the maximum limit of elements to be returned in an operation. The default value is 100, which means up to 100 elements will be returned at most.

    ## Returns 
    - json response with the total amount of the sum of all payments.
    - It can be limited by the request parameters.
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
async def get_payment_by_id(payment_id: int, 
                       db: Session = Depends(db_utils.get_db)):
    """
    ## Parameters
        - payment_id: Integer who indentify a unique payment.

    ## Returns 
    - Payment information with the Customer identified by id.
    """

    db_payment = db_utils.get_payment(db=db, payment_id=payment_id)
    if db_payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return db_payment

@app.post("/payments/", response_model=PaymentSchema)
def post_payment_with_customer_name(payment: PaymentCustomerSchema, 
                  db: Session = Depends(db_utils.get_db)):
    """
    ## Summary
    Save a new record of Payment. Important, it takes the name of the customer
    instead of a identifier like an id. \n
    Checks if the customer allready exists, if is the case, only link the payment
    to the customer, otherwise, create a new customer whit the given name and link the payment.

    ## Return
        - success: New payment instance with the id assingned.
    """

    # Because we have customers and can not be payments whitout custmers
    #  we need to create a customer of the payments if it is not exists
    #  or link the new paymet whit an existing Customer.
    customer = db_utils.get_or_create_customer_by_full_name(
        db=db, customer_fullname=payment.customer
    )
    if isinstance(customer, ValueError):
        raise HTTPException(status_code=400, detail=f"There was an error with the Customer name: {customer}")
    # Validates if the value exists
    if db_utils.find_payment(db=db, payment=payment, customer_id=customer.id):
        raise HTTPException(status_code=409, detail="Register allready exists")
    # Compare all the data and look if there are allready in the data base
    # This is because we don't have a identifier from the request

    db_payment = db_utils.create_payment(db=db, payment=payment, customer_id=customer.id)
    if isinstance(db_payment, ValueError):
        raise HTTPException(status_code=400, detail=f"There was an error: {db_payment}")
    return db_payment
