import os
import pandas as pd

from database.database import SessionLocal
from schemas.payment_schemas import PaymentCreateSchema
from database import db_utils


def get_db():
    try:
        db = SessionLocal()
    except Exception as error:
        print(f'ERROR: {error}')
    finally:
        db.close()
    return db

def get_files_names(directory: str):
    files = os.listdir(directory)
    files_names = []
    for file in files:
        if file.endswith('.xlsx') or file.endswith('xls'):
            files_names.append(file)
    return files_names

def validate_data(row):
    if all(pd.notnull(value) for value in row):
        if all(value != '' and value != 'nan' for value in row):
            # The data is validated, the execution of the function ends.
            return
    raise ValueError('There is an error on the values')

def validate_full_name(full_name: str):
    try:
        full_name.split(sep=" ")[1]
    except:
        return ValueError("There is no last_name")

def if_payment_exists(payment: PaymentCreateSchema, db, customer_id: int):
    payment_db = db_utils.find_payment(db, payment, customer_id)
    if payment_db:
        raise ValueError('This row allready exists')
    return False

def create_new_registers(file_path, db: SessionLocal, rows_added: int):
    file_dataframe = pd.read_excel(file_path)

    for row in file_dataframe.itertuples():
        try:
            # Validate data types of content and missing values
            validate_data(row)
            # We need to be sure of the name has a first_name and last_name
            validate_full_name(str(row.Cliente))
            # build all the necessary instances for register a new Payment
            customer = db_utils.get_or_create_customer_by_full_name(
                db=db, customer_fullname=row.Cliente
            )
            file_row_payment = PaymentCreateSchema(
                payment_date=row.Fecha.date(),
                amount=row.Monto,
                bank=row.Proveedor,
                customer_id=customer.id
            )
            # Check if the file allready exists in the database
            if_payment_exists(file_row_payment, db, customer.id)
            # Once the data is valid, writ the payment in the db
            db_utils.create_payment(db=db, payment=file_row_payment, customer_id=customer.id)
            # Incremet the counter for rows added when everithing finish whit success
            rows_added+=1
        except Exception as error:
            print(f'ERROR: {error}. RISED BY: Row#{row.Index} {row}. Trying with next row...')
            continue
    return rows_added

def main():
    print("---- IMPORTING PAYMENTS ----")
    EXCEL_FILES_PATH = './excel_files/'
    rows_added = 0

    # Set the data base session to create the new rows
    db = get_db()
    # Get a list of the files name whit .xlsx extension.
    files = get_files_names(EXCEL_FILES_PATH)

    # Iterate that list and try to add the rows in the Data Base
    for file_name in files:
        rows_added = create_new_registers(EXCEL_FILES_PATH+file_name, db=db, rows_added=rows_added)

    db.close()
    print(f'---- FINISH whit {rows_added} new registers ----')

if __name__ == "__main__":
    main()
