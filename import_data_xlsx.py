import os
import pandas as pd

from database.database import SessionLocal
from schemas.payment_schemas import PaymentCreateSchema
from database.db_utils import create_payment, check_payment


def get_db():
    try:
        db = SessionLocal()
    except Exception as error:
        print(f'ERROR: {error}')
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
            return
    raise ValueError('There is an error on the values')

def if_payment_exists(payment: PaymentCreateSchema, db):
    payment_db = check_payment(db, payment)
    if payment_db:
        raise ValueError('This row allready exists')
    return False

def create_new_registers(file_path, db: SessionLocal, rows_added: int):
    file_dataframe = pd.read_excel(file_path)

    for row in file_dataframe.itertuples():
        try:
            excel_payment = PaymentCreateSchema(
                payment_date=row.Fecha.date(),
                amount=row.Monto,
                bank=row.Proveedor,
                customer_name=row.Cliente
            )
            # Check if the file allready exists in the database
            if_payment_exists(excel_payment, db)
            # Validate data types of content and missing values
            validate_data(row)
            # Once the data is valid, writ the payment in the db
            create_payment(db=db, payment=excel_payment)
            # Incremet the counter for rows added when everithing finish whit success
            rows_added+=1
        except Exception as error:
            print(f'ERROR: {error}. RISED BY: Row#{row.Index} {row}. Trying with next row...')
            continue
    return rows_added

def main():
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
    print(f'FINISH whit {rows_added} new registers')

if __name__ == "__main__":
    main()
