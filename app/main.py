from fastapi import FastAPI
from app.database import Base,engine
from app.routes import users,posts,comments,tags


Base.metadata.create_all(bind=engine)


app = FastAPI(title="Blog_cms Apis")

app.include_router(users.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(tags.router)



@app.get("/")
def root():
    return{"message":"Blog Api is running."}


