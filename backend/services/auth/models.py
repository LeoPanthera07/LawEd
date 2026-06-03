import datetime
from sqlalchemy import Column, Integer, String, DateTime
from backend.services.auth.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    user_type = Column(String, nullable=False)  # "citizen" or "lawfirm"
    court_name = Column(String, nullable=True)   # For law firms
    bar_council_id = Column(String, nullable=True) # For law firms
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
