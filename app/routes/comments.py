from fastapi import APIRouter,HTTPException,status,Depends
from sqlalchemy.orm import Session
from app import models,schemas
from app.dependenics import get_current_user
from app.database import get_db



router = APIRouter(prefix="/post/{post_id}/comments",tags=["comments"])


@router.post("/",response_model=schemas.CommentResponse)
def create_comment(post_id:int,comment:schemas.Comment,db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):

    post = db.query(models.Post).filter(models.Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Post not found.")

    if not post.is_published and post.owner_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Post not found.")

    new_comment = models.Comment(
        content = comment.content,
        post_id = post_id,
        owner_id = current_user.id
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)

    return new_comment


@router.get("/",response_model=list[schemas.CommentResponse])
def get_comments(post_id:int,db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):

    post = db.query(models.Post).filter(models.Post.id == post_id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Post not found.")

    comments = db.query(models.Comment).filter(models.Comment.post_id == post_id).all()
    return comments


@router.delete("/{comment_id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(post_id:int,comment_id:int,db:Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):

    comment = db.query(models.Comment).filter(models.Comment.id == comment_id,models.Comment.post_id == post_id).first()

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Comment not found.")

    post = db.query(models.Post).filter(models.Post.id == post_id).first()

    if comment.owner_id != current_user.id and post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not authorized to delete this comment")

    db.delete(comment)
    db.commit()
    return None

