from sqlalchemy import Column, Date, Integer, String, Float

from database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    date_payment = Column(Date)
    amount = Column(Float)
    bank = Column(String)
    customer_name = Column(String)