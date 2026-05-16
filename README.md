# ⚡ Task Manager — FastAPI + HTML/JS

A full-stack Task Manager web application built with **FastAPI** (backend) and **vanilla HTML/CSS/JS** (frontend).

## 🌐 Live Demo

> **[https://your-deployment-link.onrender.com](https://your-deployment-link.onrender.com)**  
> API Docs: [https://your-deployment-link.onrender.com/docs](https://your-deployment-link.onrender.com/docs)

---

## ✨ Features

- 🔐 JWT-based Authentication (register & login)
- ✅ Full Task CRUD (create, view, complete, delete)
- 🔒 Users can only access their own tasks
- 📄 Pagination (`?page=1&page_size=10`)
- 🔍 Filter tasks by status (`?completed=true`)
- 🧪 Pytest test suite (11 test cases)
- 🐳 Docker support
- 📱 Responsive frontend

---

## 🏗 Project Structure

```
taskmanager/
├── main.py                  # FastAPI app entry point
├── requirements.txt
├── Dockerfile
├── .env.example
├── backend/
│   ├── core/
│   │   ├── security.py      # JWT, password hashing
│   │   └── dependencies.py  # get_current_user dependency
│   ├── db/
│   │   └── database.py      # SQLAlchemy engine, session, Base
│   ├── models/
│   │   ├── user.py          # User ORM model
│   │   └── task.py          # Task ORM model
│   ├── schemas/
│   │   ├── user.py          # Pydantic schemas for auth
│   │   └── task.py          # Pydantic schemas for tasks
│   └── routers/
│       ├── auth.py          # POST /register, POST /login
│       └── tasks.py         # Full CRUD /tasks endpoints
├── frontend/
│   └── index.html           # Single-page frontend
└── tests/
    └── test_api.py          # Pytest test cases
```

---

## 🚀 Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/task-manager.git
cd task-manager
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate       # Linux/macOS
venv\Scripts\activate          # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env with your values
```

### 5. Run the server

```bash
uvicorn main:app --reload
```

Open **http://localhost:8000** in your browser.  
API docs at **http://localhost:8000/docs**

---

## 🌍 Environment Variables

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | JWT signing secret | *required* |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime | `30` |
| `DATABASE_URL` | SQLAlchemy DB URL | `sqlite:///./taskmanager.db` |

---

## 📡 API Endpoints

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/register` | Register new user |
| `POST` | `/login` | Login, returns JWT token |

### Tasks (all require `Authorization: Bearer <token>`)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/tasks` | Create a task |
| `GET` | `/tasks` | List all tasks (paginated + filterable) |
| `GET` | `/tasks/{id}` | Get specific task |
| `PUT` | `/tasks/{id}` | Update task |
| `DELETE` | `/tasks/{id}` | Delete task |

**Query params for GET /tasks:**
- `?page=1` — page number
- `?page_size=10` — items per page (max 100)
- `?completed=true` — filter completed tasks
- `?completed=false` — filter pending tasks

---

## 🧪 Run Tests

```bash
pytest tests/ -v
```

---

## 🐳 Docker

```bash
docker build -t task-manager .
docker run -p 8000:8000 -e SECRET_KEY=your-secret task-manager
```

---

## ☁️ Deploy to Render

1. Push to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Add environment variables from `.env.example`
7. Deploy!

---

## 👨‍💻 Built by

**Karthikeyan S** — B.Sc Computer Science (Cyber Security), SRM Institute of Science and Technology
