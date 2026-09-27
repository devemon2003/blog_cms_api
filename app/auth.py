from  datetime import datetime,timedelta,timezone
from typing import Optional
from jose import JWTError,jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
import os


load_dotenv()


SECRECT_KEY=os.getenv("SECRECT_KEY")
ALOGORITHM = os.getenv("ALOGORITHM")
ACCESS_TOKEN_EXPIRES=int(os.getenv("ACCESS_TOKEN_EXPIRES"))

pwd_context = CryptContext(schemes=["bcrypt"],deprecated="auto")


def hash_password(password:str) -> str:
    password = password[:72]
    hash_password = pwd_context.hash(password)
    return hash_password

def verify_hash_password(plain_password:str,password:str) -> bool:
    plain_password = plain_password[:72]
    return pwd_context.verify(plain_password,password)


def create_access_token(data:dict,expires_delta:Optional[timedelta] = None):

    to_encoded = data.copy()

    if expires_delta:
        expires = datetime.now(timezone.utc) + expires_delta

    else:
        expires = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRES)

    to_encoded.update({"exp":expires})

    encoded_jwt = jwt.encode(to_encoded,SECRECT_KEY,algorithm=ALOGORITHM)

    return encoded_jwt


def verify_token(token:str):

    try:
        payload = jwt.decode(token,SECRECT_KEY,algorithms=ALOGORITHM)
        email : str = payload.get("sub")
        if email is None:
            return None
        return email
    except JWTError:
        return None
