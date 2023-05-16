from sqlalchemy import ForeignKey, Column, Date, Integer, String, Float
from sqlalchemy.orm import relationship, registry

from database.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    payments = relationship("Payment", back_populates="customer")

    def __str__(self):
        return self.first_name + " " + self.last_name

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    payment_date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    bank = Column(String, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"))

    customer = relationship("Customer", back_populates="payments")
