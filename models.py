from sqlalchemy import Column, Date, Integer, String, Float

from database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    payment_date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    bank = Column(String, nullable=False)
    customer_name = Column(String, nullable=False)