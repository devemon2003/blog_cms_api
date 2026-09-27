from pydantic import BaseModel,EmailStr,ConfigDict
from datetime import datetime
from typing import Optional,List


class UserCreate(BaseModel):
    email : EmailStr
    password : str


class UserResponse(BaseModel):
    id : int
    email : EmailStr
    created_at : datetime

    model_config = ConfigDict(from_attributes=True)


class UserBasic(BaseModel):
    id : int
    email : EmailStr

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token : str
    token_type : str

class TokenData(BaseModel):
    email : Optional[str] = None


class Tag(BaseModel):
    name : str

class TagResponse(BaseModel):
    id : int
    name : str

    model_config = ConfigDict(from_attributes=True)


class Comment(BaseModel):
    content : str


class CommentResponse(BaseModel):
    id : int
    content : str
    created_at : datetime
    owner : UserBasic

    model_config = ConfigDict(from_attributes=True)


class PostCreate(BaseModel):
    title : str
    content : str
    is_published : bool = True
    tag_names : Optional[list[str]] = []


class PostUpdate(BaseModel):
    title : Optional[str] = None
    content : Optional[str] = None
    is_published : Optional[bool] = None


class PostResponse(BaseModel):
    id : int
    title : str
    content : str
    thumbnail_url : Optional[str]
    is_published : bool
    created_at : datetime
    owner : UserBasic
    tags : List[TagResponse] = []
    like_count : int = 0
    comment_count : int = 0

    model_config = ConfigDict(from_attributes=True)


class PostDetailResponse(PostResponse):
    
    comments : List[CommentResponse] = []



    
