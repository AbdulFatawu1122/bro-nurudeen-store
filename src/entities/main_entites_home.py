from sqlalchemy import Column, UUID, Integer, Float, String, Boolean, ForeignKey, Date, DateTime
from sqlalchemy.orm import relationship #relationship between entities
from datetime import timezone, date, datetime
import uuid

#import our Base from our Database
from ..database.core import Base

class Admin(Base):
    __tablename__ = "admins"
    admin_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firstname = Column(String, nullable=True)
    lastname = Column(String, nullable=True)
    phone = Column(String, nullable=True, unique=True)
    email = Column(String, nullable=True, unique=True)
    username = Column(String, nullable=True, unique=True)
    password_hashed = Column(String, nullable=True)
    position = Column(String, nullable=True)
    time_created = Column(DateTime(timezone=True), nullable=False, default=lambda : datetime.now(timezone.utc))

class Product(Base):
    __tablename__ = "products"

    product_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    quantityInStock = Column(Integer, nullable=False, default=0)
    pricePerUnit = Column(Integer, nullable=True)
    productDetails = Column(String, nullable=True)


class Sale(Base):
    __tablename__ = "sales"

    sale_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quantity_sold = Column(Integer, nullable=False, default=0)
    customer_name = Column(Integer, nullable=True)
    customer_number = Column(Integer, nullable=True)
    date = Column(Date, nullable=True, default=date.today())
    amount = Column(Float, nullable=True)

    payment_status = Column(Boolean, nullable=True) # 0/false for not payed(on credit) and 1/true means payed

    #foreign columns
    admin_id = Column(UUID(as_uuid=True), ForeignKey("admins.admin_id"))
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.product_id"))


class SaleHistory(Base):
    __tablename__ = "saleshist"

    salehistId = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    quantity_sold = Column(Integer, nullable=True)
    customer_name = Column(String, nullable=True)
    customer_number = Column(String, nullable=True)
    date = Column(Date, nullable=True, default=date.today())
    amount = Column(Float, nullable=True)
    current_method = Column(String, nullable=True) # On credit or on cash
    first_payment_method = Column(String, nullable=True)

    admin_name = Column(String, nullable=True)
    product_name = Column(String, nullable=True)




class Supplier(Base):
    __tablename__  = "suppliers"

    supplier_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    email = Column(String, nullable=True)


class Purchase(Base):
    __tablename__ = "purchases"

    purchase_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quantity = Column(Integer, nullable=False)
    date = Column(Date, nullable=False, default=date.today())
    amount = Column(Float, nullable=True)

    payment_status = Column(Boolean, nullable=True)


    #foreign keys
    supplier_id = Column(UUID(as_uuid=True), ForeignKey("suppliers.supplier_id"))
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.product_id"))
    admin_id = Column(UUID(as_uuid=True), ForeignKey("admins.admin_id"))


class PurchaseHistory(Base):
    __tablename__ = "purchasehist"

    purchaseHistId = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())

    quantity = Column(Integer, nullable=True)
    date = Column(Date, nullable=True, default=date.today())
    amount = Column(Float, nullable=True)

    current_method = Column(String, nullable=True) # On credit or on cash
    first_payment_method = Column(String, nullable=True)

    supplier_name = Column(String, nullable=True)
    product_name = Column(String, nullable=True)
    admin_name = Column(String, nullable=True)


