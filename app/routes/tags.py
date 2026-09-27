from fastapi import APIRouter,status,HTTPException,Depends
from sqlalchemy.orm import Session
from typing import List
from app.dependenics import get_current_user
from app.database import get_db
from app import models,schemas


router = APIRouter(prefix="/tags",tags=["tags"])


@router.get("/",response_model=List[schemas.TagResponse])
def get_all_tags(db:Session=Depends(get_db)):
    tags = db.query(models.Tag).order_by(models.Tag.name).all()
    return tags


@router.delete("/{tag_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id:int,db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):

    tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()

    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Tag not found.")

    db.delete(tag)
    db.commit()
    return None
