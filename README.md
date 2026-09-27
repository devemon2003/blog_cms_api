# 📝 Blog/CMS API

A production-ready RESTful API for a blogging platform, built with **FastAPI** and containerized with **Docker**. Supports full authentication, post management, comments, likes, tagging, and image uploads.

🔗 **Live Demo:** [https://blog-cms-api.onrender.com/docs](https://blog-cms-api.onrender.com/docs)

---

## 🚀 Features

- **JWT Authentication** — secure register/login with hashed passwords (bcrypt)
- **Post Management** — full CRUD with draft/published visibility control
- **Tags (Many-to-Many)** — auto-create tags, filter posts by tag
- **Comments** — nested under posts, with owner + post-owner moderation permissions
- **Likes** — one like per user per post, enforced at the database level
- **Image Upload** — thumbnail upload with automatic resizing (Pillow)
- **Search & Pagination** — filter posts by title/content, paginated results
- **Dockerized** — fully containerized for consistent deployment anywhere

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|-----------|
| Framework | FastAPI |
| Database | SQLAlchemy ORM + SQLite |
| Auth | JWT (python-jose) + bcrypt |
| Image Processing | Pillow |
| Containerization | Docker |
| Deployment | Render |

---

## 📂 Project Structure

app/
├── main.py # App entry point
├── database.py # DB connection setup
├── models.py # SQLAlchemy models (User, Post, Comment, Like, Tag)
├── schemas.py # Pydantic request/response schemas
├── auth.py # Password hashing + JWT logic
├── dependencies.py # Auth dependency (get_current_user)
└── routers/
├── users.py # Register/Login
├── posts.py # Post CRUD, likes, thumbnails
├── comments.py # Comment CRUD
└── tags.py # Tag listing/management


---

## 🔑 Key API Endpoints

| Method | Endpoint | Description |
|--------|----------|--------------|
| POST | `/users/register` | Create a new account |
| POST | `/users/login` | Login, receive JWT token |
| POST | `/posts/` | Create a post (with tags) |
| GET | `/posts/?tag=&search=&page=` | List posts (filter, search, paginate) |
| GET | `/posts/{id}` | Get single post with comments |
| PATCH | `/posts/{id}` | Update a post |
| DELETE | `/posts/{id}` | Delete a post |
| POST | `/posts/{id}/like` | Like a post |
| DELETE | `/posts/{id}/like` | Unlike a post |
| POST | `/posts/{id}/thumbnail` | Upload post thumbnail |
| POST | `/posts/{id}/comments/` | Add a comment |
| GET | `/tags/` | List all tags |

Full interactive documentation available at `/docs` (Swagger UI).

---

## ⚙️ Running Locally

### With Docker (recommended)

```bash
docker build -t blog-cms-api .
docker run -d -p 8000:8000 --env-file .env --name blog-cms-container blog-cms-api
```

### Without Docker

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Visit `http://127.0.0.1:8000/docs` to explore the API.

---

## 🔒 Environment Variables

Create a `.env` file with:

```env
DATABASE_URL=sqlite:///./blog_cms.db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## 👤 Author

Built as part of a backend development portfolio project series focused on FastAPI, database design, and containerized deployment.