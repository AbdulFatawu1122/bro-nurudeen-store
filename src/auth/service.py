#Basic imports
from dotenv import load_dotenv
import os
from passlib.context import CryptContext
from uuid import UUID, uuid4
from datetime import timedelta, datetime, timezone
from fastapi import HTTPException, status, Depends
from typing import Annotated


#from sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy import or_


#Security
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from jose import jwt, JWTError


# internal  imports
from src.entities.main_entites_home import Admin
from . import models


load_dotenv()


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRES_MINUTES = 60



#declare my authentication schema
oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/token")

#set password hasher, using bcrypt
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")


#verify a crypted password
def verify_password(plain_password: str, hashed_passord: str) -> bool:
    return pwd_context.verify(plain_password, hashed_passord)


#hashed a password
def get_password_hashed(password: str) -> str:
    return pwd_context.hash(password)



#Authenticate admin, by checking and verifying details
def auth_admin(email: str, password: str,  db:Session) -> Admin | bool:
    admin = db.query(Admin).filter(or_(
        Admin.email == email,
        Admin.phone == email,
        Admin.username == email,
    )).first()

    #if we verify the admin email is invalid and password entere is also incorrect
    if not admin:
        return False
    if not verify_password(password, admin.password_hashed):
        return False
    return admin



#Creating access token
def create_access_token(email: str, admin_id:UUID, expires_delta:timedelta) -> str:
    encode = {
        "sub": email,
        "id": str(admin_id),
        "exp": datetime.now(timezone.utc) + expires_delta
    }
    encoded_jwt = jwt.encode(encode, SECRET_KEY, ALGORITHM)

    return encoded_jwt


#verify a token
def verify_token(token: str) -> models.TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
        admin_id: str = payload.get("id")
        return models.TokenData(admin_id=admin_id)
    except JWTError:
        raise HTTPException(
            detail="Token Invalid or expired.", status_code=status.HTTP_403_FORBIDDEN
        )

#Register new admins
def register_admin(db: Session, admin:models.RegisterAdmin, current_admin:UUID):
    login_admin_admin = db.query(Admin).filter(Admin.admin_id == current_admin).first()
    if not login_admin_admin:
        raise HTTPException(
            status_code=404,
            detail="Only Admins can register new admins, contact the administrator to register you"
        )
    try:
        #firts hashed admin password
        hashed_password = get_password_hashed(admin.password)

        db_new_admin = Admin(
            admin_id=uuid4(),
            firstname=admin.firstname.lower(),
            lastname=admin.lastname.lower(),
            phone=admin.phone,
            email= admin.email.lower(),
            username=admin.username.lower(),
            password_hashed=hashed_password,
            position=admin.position.lower(),
        )

        #add the new admin
        db.add(db_new_admin)
        db.commit()
        db.refresh(db_new_admin)

        return {
            "message": "Account created Succefully",
            "details": {
                "name": db_new_admin.firstname,
                "position": db_new_admin.position
            }
        }
    except IntegrityError as e:
        error_msg = str(e.orig).lower()
        if "email" in error_msg:
            raise HTTPException(
                detail="This email is already in use by another admin.",
                status_code=status.HTTP_409_CONFLICT
            )
        elif "phone" in error_msg:
            raise HTTPException(
                detail="This phone number is already in use by another admin.",
                status_code=status.HTTP_409_CONFLICT
            )
        elif "username" in error_msg:
            raise HTTPException(
                detail="This username is already in use by another admin.",
                status_code=status.HTTP_409_CONFLICT
            )
        else:
            raise HTTPException(
                detail="A database integrity error occurred. Please check your inputs.",
                status_code=status.HTTP_409_CONFLICT
            )

#def get current admin
def get_current_admin(token:Annotated[str, Depends(oauth2_schema)]) -> models.TokenData:
    return verify_token(token=token)

CurrentAdmin = Annotated[models.TokenData, Depends(get_current_admin)]


#login for access token

def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session) -> models.Token:
    admin = auth_admin(email=form_data.username, password=form_data.password, db=db)
    
    if not admin:
        raise HTTPException(
            detail="Password or Email Invalid",
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    access_token_expires_in = timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)

    token = create_access_token(
        email=admin.email,
        admin_id=admin.admin_id,
        expires_delta=access_token_expires_in,
    )


    return models.Token(access_token=token, token_type="bearer")
