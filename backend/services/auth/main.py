from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from backend.services.auth.database import get_db, Base, engine
from backend.services.auth.models import User
import hashlib

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LawEdAI Identity & Auth Service",
    description="Microservice providing authentication, signup, and login workflows (RBAC)."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

@app.post("/api/auth/signup")
def signup(payload: dict, db: Session = Depends(get_db)):
    email = payload.get("email", "").strip().lower()
    password = payload.get("password", "")
    full_name = payload.get("full_name", "").strip()
    user_type = payload.get("user_type", "citizen").strip().lower() # "citizen" or "lawfirm"
    court_name = payload.get("court_name", None)
    bar_council_id = payload.get("bar_council_id", None)

    if not email or not password or not full_name:
        raise HTTPException(status_code=400, detail="Missing required signup fields.")

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="A user with this email already exists.")

    user = User(
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
        user_type=user_type,
        court_name=court_name,
        bar_council_id=bar_council_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "status": "success",
        "message": "User registered successfully.",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "user_type": user.user_type,
            "court_name": user.court_name,
            "bar_council_id": user.bar_council_id
        }
    }

@app.post("/api/auth/login")
def login(payload: dict, db: Session = Depends(get_db)):
    email = payload.get("email", "").strip().lower()
    password = payload.get("password", "")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Missing email or password.")

    user = db.query(User).filter(User.email == email).first()
    if not user or user.hashed_password != hash_password(password):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    return {
        "status": "success",
        "token": f"session-{user.id}-{user.user_type}",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "user_type": user.user_type,
            "court_name": user.court_name,
            "bar_council_id": user.bar_council_id
        }
    }
