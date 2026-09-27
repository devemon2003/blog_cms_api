from fastapi import Depends,HTTPException,status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from app.auth import verify_token
from app import models
from app.database import get_db


oauth_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def get_current_user(token:str=Depends(oauth_scheme),db:Session=Depends(get_db)):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate":"Bearer"}
    )

    email = verify_token(token)

    if email is None:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.email == email).first()

    if user is None:
        raise credentials_exception

    return user



