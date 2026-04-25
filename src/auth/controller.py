from fastapi import APIRouter, status, Request, Depends
from ..database.core import DbSession
from . import models, service
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from ..auth.service import CurrentAdmin


router = APIRouter(
    prefix="/auth",
    tags=['Auth']
)



@router.post("/", status_code=status.HTTP_201_CREATED)
async def register_new_admin(request: Request, db:DbSession, admin: models.RegisterAdmin, current_admin: CurrentAdmin):
    service.register_admin(db=db, admin=admin, current_admin=current_admin.get_uuid())
    return {"message": "You are a new Admin"}

@router.post("/token", response_model=models.Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbSession):
    return service.login_for_access_token(form_data=form_data, db=db)



@router.post("/verify-token/{token}")
async def verify_token(token: str):
    service.verify_token(token=token)
    return {"message": "Token is a Valid Token"}

