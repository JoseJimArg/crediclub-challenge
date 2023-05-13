import pandas as pd

from models import Payment
from database import SessionLocal

from schemas import PaymentCreateSchema
from utils import create_payment

def get_db():
    try:
        db = SessionLocal()
    except Exception as error:
        print(f'ERROR: {error}')
    return db

def get_dataframe(file_name: str):
    return pd.read_excel(file_name)

def main():
    db = get_db()

    # Get a list of the files name whit .xlsx extension.
    # Iterate that list and try to add the rows in the Data Base
    rows_added = 0

    file_dataframe = get_dataframe("./excel_files/Banamex.xlsx")
    
    for row in file_dataframe.head(1).itertuples():
        try:
            excel_payment = PaymentCreateSchema(
                date_payment=row.Fecha.date(),
                amount=float(row.Monto),
                bank=str(row.Proveedor),
                customer_name=str(row.Cliente)
            )
            new_payment = create_payment(db=db, payment=excel_payment)
            # Incremet the counter for rows added when everithing finish whit success
            print(new_payment)
            rows_added+=1
        except Exception as error:
            print(f'ERROR: {error}. RISED BY: {row} #{row.Index}. Trying with next row...')
            continue
    db.close()
    print(f'ROWS ADDED:{rows_added}')

if __name__ == "__main__":
    main()
