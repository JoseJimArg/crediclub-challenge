from pydantic import BaseModel


# Customer schemas
class CustomerBaseSchema(BaseModel):
    first_name = str
    last_name = str

class CustomerCreateSchema(CustomerBaseSchema):
    pass

class CustomerSchema(CustomerBaseSchema):
    id: int

    class Config:
        orm_mode = True