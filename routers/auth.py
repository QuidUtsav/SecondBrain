# routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import select

from database import get_db
from models.account import Account
from schemas.account import AccountCreate, AccountResponse
from auth.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=AccountResponse)
def signup(account: AccountCreate, db: Session = Depends(get_db)):
    existing = db.execute(
        select(Account).where(Account.email == account.email)
    ).scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_account = Account(
        name=account.name,
        email=account.email,
        hashed_password=hash_password(account.password),
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    account = db.execute(
        select(Account).where(Account.email == form_data.username)
    ).scalar_one_or_none()

    if not account or not verify_password(form_data.password, account.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(account.id)})
    return {"access_token": access_token, "token_type": "bearer"}