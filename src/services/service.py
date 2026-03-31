from uuid import UUID


#internal imports
from src.auth.models import TokenData
from ..database.core import DbSession
from ..auth.service import CurrentAdmin
from src.entities.main_entites_home import Product, Supplier, Admin, Sale, Purchase


#module import
from . import models
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_


def all_products(current_admin: TokenData, db:Session):
    products = db.query(Product).all()

    return {
        "data": products
    }

def all_suppliers(current_admin:TokenData, db: Session):
    suppliers = db.query(Supplier).all()

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
             amount: int,
             quantity_sold: int,
             product_id: UUID,
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
        admin_id= current_admin.get_uuid()
    )

    db.add(db_new_sale)
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


def makingPurchaseOrNewSupplier(quantity: int,amount: int, supplier_id: UUID, product_id: UUID, current_admin:TokenData, db:Session):
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
        admin_id=current_admin.get_uuid()
    )

    db.add(db_new_supply)
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
    sales = db.query(Sale).all()

    return {
        "data": sales
    }

def all_supplies(current_admin:TokenData, db: Session):
    supplies = db.query(Purchase).all()

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


