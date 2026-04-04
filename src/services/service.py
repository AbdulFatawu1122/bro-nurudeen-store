from uuid import UUID


#internal imports
from src.auth.models import TokenData
from ..database.core import DbSession
from ..auth.service import CurrentAdmin
from src.entities.main_entites_home import Product, Supplier, Admin, Sale, Purchase, SaleHistory, PurchaseHistory
from sqlalchemy import asc, desc
import uuid

#module import
from . import models
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc


def all_products(current_admin: TokenData, db:Session):
    products = db.query(Product).all()[::-1]

    return {
        "data": products
    }

def all_suppliers(current_admin:TokenData, db: Session):
    suppliers = db.query(Supplier).all()[::-1]

    return {
        "data": suppliers
    }

def get_current_admin(current_admin:UUID, db: Session):
    admin = db.query(Admin).filter(Admin.admin_id == current_admin).first()

    return {
        "data": admin
    }

def add_new_product(form_data: models.AddProduct, current_admin:TokenData, db: Session):
    db_new_product = Product(
        name=form_data.name.lower(),
        quantityInStock= form_data.quantityInstock,
        pricePerUnit=form_data.pricePerUnit,
        productDetails=form_data.productDetails
    )

    db.add(db_new_product)
    db.commit()
    db.refresh(db_new_product)

    return {
        "message": "Product Add Succefully",
        "details": db_new_product
    }




def saleMake(customer_name:str,
             customer_number: str,
             amount: float,
             quantity_sold: int,
             product_id: UUID,
             payment_status: bool,
             current_admin:TokenData, db: Session):
    
    product =  db.query(Product).filter(Product.product_id == product_id).first()
    
    if quantity_sold <= 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The quantity to sold can not be zero or less than zero"
        )

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The product you are trying to sell does not exsit in your products. Add the Product Information Before you can sell it here"
        )

    if quantity_sold > product.quantityInStock:
        raise HTTPException(
            detail="You can not sell this product because the quantity in stock is less than what your are to sell!",
            status_code=status.HTTP_409_CONFLICT
        )
    
    product.quantityInStock -= quantity_sold

    db_new_sale = Sale(
        quantity_sold=quantity_sold,
        customer_name=customer_name,
        customer_number=customer_number,
        amount=amount,
        product_id=product_id,
        payment_status= payment_status,
        admin_id= current_admin.get_uuid()
    )

    admin_who_process = db.query(Admin).filter(Admin.admin_id == db_new_sale.admin_id).first()
    product_sell = db.query(Product).filter(Product.product_id == db_new_sale.product_id).first()


    db_new_saleHist = SaleHistory(
        salehistId=uuid.uuid4(),
        quantity_sold= db_new_sale.quantity_sold,
        customer_name=db_new_sale.customer_name,
        customer_number= db_new_sale.customer_number,
        date= db_new_sale.date,
        amount= db_new_sale.amount,
        current_method = "cash" if payment_status else "credit",
        first_payment_method= "cash" if payment_status else "credit",
        admin_name = f"{admin_who_process.firstname} {admin_who_process.lastname}" if admin_who_process else "N/A",
        product_name = product_sell.name if product else "N/A",
    )

    db.add(db_new_sale)
    db.add(db_new_saleHist)
    db.commit()
    db.refresh(db_new_sale)
    db.refresh(product)

    
    return {
        "message": "You have sold a product succefully",
        "data": product
    }
    

def add_supplier(form_data: models.Supplier, current_admin: TokenData, db: Session):
    supplier = db.query(Supplier).filter(Supplier.phone == form_data.phone).first()

    if supplier:
        raise HTTPException(
            detail="This Supplier wiht the same phone number already exist",
            status_code=status.HTTP_409_CONFLICT
        )
    db_new_supplier = Supplier(
        firstname= form_data.firstname.lower(),
        lastname= form_data.lastname.lower(),
        phone=form_data.phone,
        email=form_data.email,
    )
    db.add(db_new_supplier)
    db.commit()
    db.refresh(db_new_supplier)

    return {
        "message": f"Mr {db_new_supplier.firstname.capitalize()} is new supplier",
        "data":db_new_supplier
    }


def makingPurchaseOrNewSupplier(quantity: int,amount: int, supplier_id: UUID, product_id: UUID, current_admin:TokenData, payment_method: bool, db:Session):
    if quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A supply quantity can not be 0 or less"
        )
    product = db.query(Product).filter(Product.product_id ==  product_id).first()
    if not product:
        raise HTTPException(
            detail="Products to supply in does not exist in your products, add it to your products before suppling it",
            status_code=status.HTTP_404_NOT_FOUND
        )

    supplier = db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The supplie to supply is new person, add the supplier to your suppliers and try again"
        )
    

    product.quantityInStock += quantity
    db_new_supply = Purchase(
        quantity=quantity,
        amount=amount,
        supplier_id=supplier_id,
        product_id=product_id,
        payment_status= payment_method,
        admin_id=current_admin.get_uuid()
    )

    admin_who_process = db.query(Admin).filter(Admin.admin_id == db_new_supply.admin_id).first()

    product_buys = db.query(Product).filter(Product.product_id == db_new_supply.product_id).first()

    supplier_name = db.query(Supplier).filter(Supplier.supplier_id == db_new_supply.supplier_id).first()


    db_new_purchase_history = PurchaseHistory(
        purchaseHistId=uuid.uuid4(),
        quantity= db_new_supply.quantity,
        amount = db_new_supply.amount,
        current_method = "cash" if payment_method else "credit",
        first_payment_method= "cash" if payment_method else "credit",
        supplier_name= f"{supplier_name.firstname} {supplier_name.lastname}",
        product_name= product_buys.name,
        admin_name = f"{admin_who_process.firstname} {admin_who_process.lastname}"
    )
    db.add(db_new_supply)
    db.add(db_new_purchase_history)
    db.commit()
    db.refresh(db_new_supply)
    db.refresh(product)


    return {
        "message": "A supply has done succefully.",
        "data": {
            "purchase": db_new_supply,
            "product": product
        }
    }


def all_sales(current_admin:TokenData, db: Session):
    sales = db.query(SaleHistory).order_by(SaleHistory.date).all()

    return {
        "data": sales
    }

def all_supplies(current_admin:TokenData, db: Session):
    supplies = db.query(PurchaseHistory).order_by(PurchaseHistory.date).all()

    return {
        "data": supplies
    }


def update_product_price(product_id:UUID, current_admin:TokenData, db:Session, from_data:models.AddProduct):

    product = db.query(Product).filter(Product.product_id == product_id).first()

    if not product:
        raise HTTPException(
            detail="Product Does not Exist",
            status_code=status.HTTP_404_NOT_FOUND
        )


def delete_product(product_id:UUID, current_admin:TokenData, db:Session):

    product = db.query(Product).filter(Product.product_id == product_id).first()


    db.delete(product)
    db.commit()

    if not product:
        raise HTTPException(
            detail="Product Does not Exist",
            status_code=status.HTTP_404_NOT_FOUND
        )
    
def delete_supplier(supplier_id:UUID, current_admin:TokenData, db:Session):

    supplier = db.query(Supplier).filter(Supplier.supplier_id == supplier_id).first()

    if not supplier:
        raise HTTPException(
            detail="Supplier Does not Exist",
            status_code=status.HTTP_404_NOT_FOUND
        )


    db.delete(supplier)
    db.commit()

    return {
        "message": "Supplier  deleted succefully"
    }




def get_all_deptors(db: Session, current_admin: TokenData, sort_by: bool):

    #fetch all customers who owns you or all suppliers you own.
    #fetch by sorting, either 1 for customers or 2 for suppliers i own.

    if sort_by:
        #if 1 or true we sort using sales(customers)
        depts = db.query(SaleHistory).filter(SaleHistory.current_method == "credit").all()
    
    else:
        #if false or 0 sort by supplies(my depts)
        depts = db.query(PurchaseHistory).filter(PurchaseHistory.current_method == "credit").all()    

    return {
        "data":  depts
    }

def update_dept_status(db: Session, current_admin: TokenData, sorted_by: bool, dept_id: UUID):


    if sorted_by:
        dept = db.query(SaleHistory).filter(SaleHistory.salehistId == dept_id).first()
        if not dept:
            raise HTTPException(
                detail="No History found to update",
                status_code=status.HTTP_404_NOT_FOUND
            )
    
    else:
        dept = db.query(PurchaseHistory).filter(PurchaseHistory.purchaseHistId == dept_id).first()
        if not dept:
            raise HTTPException(
                detail="No History found to update",
                status_code=status.HTTP_404_NOT_FOUND
            )

    dept.current_method = "cash"

    db.commit()
    db.refresh(dept)

    return {
        "message": "Yoy have succefylly settle your dept",
        "data": dept
    }



def update_product_price(db: Session, current_admin: TokenData, new_price: float, product_id: UUID):
    product = db.query(Product).filter(Product.product_id == product_id).first()

    if not product:
        raise HTTPException(
            detail="Product does not Exist",
            status_code=status.HTTP_404_NOT_FOUND
        )

    product.pricePerUnit = new_price

    db.commit()
    db.refresh(product)

    return {
        "message": "Price of a product was succefully change",
        "data": product
    }
