from fastapi import APIRouter
from uuid import UUID


#internal import
from . import service, models
from ..database.core import DbSession
from ..auth.service import CurrentAdmin



router = APIRouter(
    prefix="/service",
    tags=['Services']
)



@router.post("/new-product")
async def addNewProduct(input_data: models.AddProduct, db: DbSession, current_admin: CurrentAdmin):
    return service.add_new_product(db=db, form_data=input_data, current_admin=current_admin)

@router.get("/all-products")
async def allProducts(current_admin: CurrentAdmin, db:DbSession):
    return service.all_products(current_admin=current_admin, db=db)


@router.get("/current-admin")
async def current_admin_incharge(current_admin: CurrentAdmin, db:DbSession):
    return service.get_current_admin(db=db, current_admin=current_admin.get_uuid())

@router.get("/all-suppliers")
async def allSuppliers(current_admin: CurrentAdmin, db:DbSession):
    return service.all_suppliers(db=db, current_admin=current_admin)

@router.get("/all-sales")
async def allSales(current_admin: CurrentAdmin, db:DbSession):
    return service.all_sales(db=db, current_admin=current_admin)

@router.get("/all-supplies")
async def allSupplies(current_admin: CurrentAdmin, db:DbSession):
    return service.all_supplies(db=db, current_admin=current_admin)

@router.post("/sale")
async def making_a_sale(
             customer_name:str,
             customer_number: str,
             amount: int,
             quantity_sold: int,
             product_id: UUID,
             db:DbSession,
             current_admin: CurrentAdmin):
    
    #go
    return service.saleMake(
        customer_name=customer_name,
        customer_number=customer_number,
        amount=amount,
        quantity_sold=quantity_sold,
        product_id=product_id,
        current_admin=current_admin,
        db=db
    )
    


@router.post("/new-supplier")
async def addNewSupplier(db: DbSession, input_data: models.Supplier, current_admin: CurrentAdmin):
    return service.add_supplier(form_data=input_data, db=db, current_admin=current_admin)


@router.post("/new-supply")
async def NewSupply(quantity: int,amount: int, supplier_id: UUID, product_id: UUID, db: DbSession, current_admin:CurrentAdmin):
    return service.makingPurchaseOrNewSupplier(
        quantity=quantity,
        amount=amount,
        supplier_id=supplier_id,
        product_id=product_id,
        db=db, 
        current_admin=current_admin
    )

@router.delete("/delete-product")
async def DeleteProduct(product_id:UUID, current_admin:CurrentAdmin, db:DbSession):
    return service.delete_product(product_id=product_id, current_admin=current_admin, db=db)


@router.delete("/delete-supplier")
async def DeleteSupplier(supplier_id:UUID, current_admin:CurrentAdmin, db:DbSession):
    return service.delete_supplier(supplier_id=supplier_id, current_admin=current_admin, db=db)
