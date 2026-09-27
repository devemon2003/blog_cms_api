from sqlalchemy import Column,String,Integer,Table,DateTime,ForeignKey,Text,Boolean,UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base



post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id",Integer,ForeignKey("posts.id"),primary_key=True),
    Column("tag_id",Integer,ForeignKey("tags.id"),primary_key=True)
)


#user model
class User(Base):
    __tablename__="users"

    id = Column(Integer,primary_key=True,index=True)
    email = Column(String,unique=True,index=True,nullable=False)
    hashed_password = Column(String,nullable=False)
    created_at = Column(DateTime(timezone=True),server_default=func.now())

    posts = relationship("Post",back_populates="owner",cascade="all, delete")
    comments = relationship("Comment",back_populates="owner",cascade="all, delete")
    likes = relationship("Like",back_populates="user",cascade="all, delete")


#post model
class Post(Base):
    __tablename__="posts"

    id = Column(Integer,primary_key=True,index=True)
    title = Column(String,nullable=False)
    content = Column(Text,nullable=False)
    thumbnail_url = Column(String,nullable=True)
    is_published = Column(Boolean,default=True)
    created_at = Column(DateTime(timezone=True),server_default=func.now())

    owner_id = Column(Integer,ForeignKey("users.id"))
    owner = relationship("User",back_populates="posts")

    comments = relationship("Comment",back_populates="post",cascade="all, delete")
    likes = relationship("Like",back_populates="post",cascade="all, delete")

    tags = relationship("Tag",secondary=post_tags,back_populates="posts")


#comment model
class Comment(Base):

    __tablename__="comments"

    id = Column(Integer,primary_key=True,index=True)
    content = Column(Text,nullable=False)
    created_at = Column(DateTime(timezone=True),server_default=func.now())

    post_id = Column(Integer,ForeignKey("posts.id"))
    post = relationship("Post",back_populates="comments")

    owner_id = Column(Integer,ForeignKey("users.id"))
    owner = relationship("User",back_populates="comments")


#like model
class Like(Base):

    __tablename__="likes"

    id = Column(Integer,primary_key=True,index=True)

    post_id = Column(Integer,ForeignKey("posts.id"))
    post = relationship("Post",back_populates="likes")

    user_id = Column(Integer,ForeignKey("users.id"))
    user = relationship("User",back_populates="likes")

    __table_args__ = (UniqueConstraint("post_id","user_id",name="unique_post_like"),)



class Tag(Base):

    __tablename__="tags"

    id = Column(Integer,primary_key=True,index=True)
    name = Column(String,unique=True,nullable=False,index=True)

    posts = relationship("Post",secondary=post_tags,back_populates="tags")

