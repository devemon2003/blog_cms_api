from fastapi import APIRouter,Depends,HTTPException,status,Query,UploadFile,File
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List,Optional

from app.database import get_db
from app.dependenics import get_current_user
from app import models,schemas

from PIL import Image
import os
import uuid


router = APIRouter(prefix="/posts",tags=["posts"])


def get_or_create_tags(db:Session,tag_names:List[str]) -> List[models.Tag]:
    tags = []

    for name in tag_names:
        name = name.strip().lower()
        if not name:
            continue

        tag = db.query(models.Tag).filter(models.Tag.name == name).first()

        if not tag:
            tag = models.Tag(name=name)
            db.add(tag)
            db.flush()

        tags.append(tag)

    return tags


def build_post_response(post:models.Post,response_class=schemas.PostResponse):
    return response_class(
        id=post.id,
        title=post.title,
        content=post.content,
        thumbnail_url=post.thumbnail_url,
        is_published=post.is_published,
        created_at=post.created_at,
        owner=post.owner,
        tags=post.tags,
        like_count=len(post.likes),
        comment_count=len(post.comments),
        comments = post.comments if response_class == schemas.PostDetailResponse else None
    )




@router.post("/",response_model=schemas.PostResponse,status_code=status.HTTP_201_CREATED)
def create_post(post:schemas.PostCreate,db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):

    tags = get_or_create_tags(db,post.tag_names)

    new_post = models.Post(
        title = post.title,
        content = post.content,
        is_published = post.is_published,
        owner_id = current_user.id,
        tags = tags
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return build_post_response(new_post)


@router.get("/",response_model=List[schemas.PostResponse])
def get_all_post(db:Session=Depends(get_db),
                 current_user:models.User=Depends(get_current_user),
                 tag : Optional[str] = Query(None),
                 search : Optional[str] = Query(None),
                 page: int = Query(1,ge=1),
                 limit: int = Query(10,ge=1,le=100)
                 ):

    query = db.query(models.Post).filter(
        or_(
            models.Post.owner_id == current_user.id,
            models.Post.is_published == True
        )
    )

    if tag:
        query = query.join(models.Post.tags).filter(models.Tag.name == tag.lower())

    if search:
        query = query.filter(
            or_(
                models.Post.title.ilike(f"%{search}%"),
                models.Post.content.ilike(f"%{search}%")
            )
        )

    offset = (page - 1) * limit
    posts = query.offset(offset).limit(limit).all()

    return [build_post_response(p) for p in posts]


@router.get("/{post_id}",response_model=schemas.PostDetailResponse)
def get_single_post(post_id:int,db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):

    post =  db.query(models.Post).filter(models.Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Post not found.")


    if not post.is_published and post.owner_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Post not found.")

    return build_post_response(post,response_class=schemas.PostDetailResponse)


@router.patch("/{post_id}",response_model=schemas.PostResponse)
def update_post(post_id:int,post_update:schemas.PostUpdate,db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):

    post = db.query(models.Post).filter(models.Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Post not found.")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not authorized to edit this post")

    update_data = post_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(post,key,value)

    db.commit()
    db.refresh(post)

    return build_post_response(post)


@router.delete("/{post_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id:int,db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):

    post = db.query(models.Post).filter(models.Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Post not found.")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not authorized to edit this post")

    db.delete(post)
    db.commit()

    return None


@router.post("/{post_id}/like",status_code=status.HTTP_201_CREATED)
def create_like(post_id:int,db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):

    post = db.query(models.Post).filter(models.Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Post not found.")

    if not post.is_published and not post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Post not found.")

    existing_like = db.query(models.Like).filter(
        models.Like.post_id == post_id,
        models.Like.user_id == current_user.id
    ).first()

    if existing_like:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="You already like the post.")

    new_like = models.Like(
        post_id = post_id,
        user_id = current_user.id
    )

    db.add(new_like)
    db.commit()
    return {"message":"Post liked successfully."}


@router.delete("/{post_id}/like",status_code=status.HTTP_204_NO_CONTENT)
def delete_like(post_id:int,db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):

    like = db.query(models.Like).filter(
        models.Like.post_id == post_id,
        models.Like.user_id == current_user.id
    ).first()

    if not like:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="You haven't like this post.")

    db.delete(like)
    db.commit()
    return None



UPLOAD_DIR="app/static/uploads"


@router.post("/{post_id}/thumbnail",response_model=schemas.PostResponse)
def upload_thumbnail(post_id:int,file:UploadFile=File(...),db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):

    post = db.query(models.Post).filter(models.Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Post not found.")

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not authorized")


    allowed_types = ["image/jpge","image/png","image/webp"]

    if file.content_type not in allowed_types:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Only JPEG, PNG, WEBP allowed")

    file_extension = file.filename.split(".")[-1]
    unique_file_name = f"{uuid.uuid4()}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIR,unique_file_name)

    image = Image.open(file.file)
    image = image.convert("RGB")
    image.thumbnail((800,800))
    image.save(file_path,quality=85,optimize=True)


    if post.thumbnail_url:
        old_path = post.thumbnail_url.lstrip("/")
        if os.path.exists(old_path):
            os.remove(old_path)

    post.thumbnail_url = f"/{file_path}"
    db.commit()
    db.refresh(post)
    return build_post_response(post)