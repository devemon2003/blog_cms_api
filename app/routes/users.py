from fastapi import APIRouter,Depends,HTTPException,status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app import models,schemas,auth
from app.database import get_db



router = APIRouter(prefix="/users",tags=["user"])


@router.post("/register",response_model=schemas.UserResponse,status_code=status.HTTP_201_CREATED)
def register(user:schemas.UserCreate,db:Session=Depends(get_db)):

    existing_user = db.query(models.User).filter(models.User.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Email already registerd.")

    hash_password = auth.hash_password(user.password)
    new_user = models.User(email=user.email,hashed_password=hash_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login",response_model=schemas.Token)
def login(db:Session=Depends(get_db),form_data:OAuth2PasswordRequestForm=Depends()):

    user = db.query(models.User).filter(models.User.email == form_data.username).first()

    if not user or not auth.verify_hash_password(form_data.password,user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate":"Bearer"}
        )

    access_token = auth.create_access_token(data={"sub":user.email},expires_delta=timedelta(minutes=30))

    return {
        "access_token":access_token,
        "token_type":"Bearer"
    }






