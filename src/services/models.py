from pydantic import BaseModel
from uuid import UUID
from datetime import date

class AddProduct(BaseModel):
    name: str
    pricePerUnit: float
    productDetails: str
    quantityInstock: int

class ProductAddedResponse(AddProduct):
    id: UUID

    class Config:
        from_attributes=True


class SaleMake(BaseModel):
    quantity_sold: int
    customer_name: str | None = None
    customer_number: str
    amount: float
    payment_status: bool
    date: date

    product_id: UUID

class Supplier(BaseModel):
    firstname: str
    lastname: str
    phone: str
    email: str


class PurchaseMake(BaseModel):
    quantity: int
    amount: float
    payment_status: bool
    date: date

    supplier_id: UUID
    product_id: UUID
    admin_id: UUID


class  Sales_History(BaseModel):
    quantity_sold: int
    customer_name: str
    customer_number: str
    date: date
    amount: float
    payment_method: bool
    admin_name: str
    product_name: str

class Purchases_History(BaseModel):
    quantity: int
    date: date
    amount: float
    payement_method: str
    supplier_name: str
    product_name: str
    admin_name: str


    

