from fastapi import APIRouter
from uuid import UUID


#internal import
from . import service, models
from ..database.core import DbSession
from ..auth.service import CurrentAdmin
from datetime import date



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
async def allSales(current_admin: CurrentAdmin, db:DbSession, days: int = 7, limit: int = 20, page: int = 1):
    return service.all_sales(db=db, current_admin=current_admin, days=days, limit=limit, page=page)

@router.get("/all-supplies")
async def allSupplies(current_admin: CurrentAdmin, db:DbSession, days: int = 7, limit: int = 20, page: int = 1):
    return service.all_supplies(db=db, current_admin=current_admin, days=days, limit=limit, page=page)

@router.post("/sale")
async def making_a_sale(db:DbSession, current_admin: CurrentAdmin, form_data: models.SaleMake):
    
    #go
    return service.saleMake(
        form_data=form_data,
        current_admin=current_admin.get_uuid(),
        db=db,
    )
    


@router.post("/new-supplier")
async def addNewSupplier(db: DbSession, input_data: models.Supplier, current_admin: CurrentAdmin):
    return service.add_supplier(form_data=input_data, db=db, current_admin=current_admin)


@router.post("/new-supply")
async def NewSupply(form_data: models.PurchaseMake, db: DbSession, current_admin:CurrentAdmin):
    return service.makingPurchaseOrNewSupplier(
        current_admin=current_admin.get_uuid(),
        db=db,
        form_data=form_data
    )

@router.delete("/delete-product")
async def DeleteProduct(product_id:UUID, current_admin:CurrentAdmin, db:DbSession):
    return service.delete_product(product_id=product_id, current_admin=current_admin, db=db)


@router.delete("/delete-supplier")
async def DeleteSupplier(supplier_id:UUID, current_admin:CurrentAdmin, db:DbSession):
    return service.delete_supplier(supplier_id=supplier_id, current_admin=current_admin, db=db)


@router.get("/depts")
async def Get_all_depts(db: DbSession, current_admin: CurrentAdmin, sort_by: bool):
    return service.get_all_deptors(
        db=db, 
        current_admin=current_admin,
        sort_by=sort_by
    )

@router.get("/update-dept")
async def update_dept(db: DbSession, current_admin: CurrentAdmin, sorted_by: bool, dept_id: UUID):
    return service.update_dept_status(
        db=db,
        sorted_by=sorted_by,
        current_admin=current_admin,
        dept_id=dept_id
    )

@router.get("/update-price")
async def update_product_price(new_price: float, product_id: UUID, db:DbSession, current_admin: CurrentAdmin):
    return service.update_product_price(
        new_price=new_price,
        product_id=product_id,
        db=db, current_admin=current_admin
    )


@router.delete("/delete-sale-history")
async def DeleteSaleHistory(sale_id: UUID, current_admin: CurrentAdmin, db: DbSession):
    return service.delete_sale_history(sale_id=sale_id, current_admin=current_admin, db=db)


@router.delete("/delete-supply-history")
async def DeleteSupplyHistory(supply_id: UUID, current_admin: CurrentAdmin, db: DbSession):
    return service.delete_supply_history(supply_id=supply_id, current_admin=current_admin, db=db)