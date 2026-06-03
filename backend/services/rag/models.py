from sqlalchemy import Column, Integer, String, Text
from backend.services.rag.database import Base

class StatuteChunk(Base):
    __tablename__ = "statute_chunks"

    id = Column(Integer, primary_key=True, index=True)
    act_type = Column(String, index=True, nullable=False) # "BNS", "BNSS", or "BSA"
    section_number = Column(String, index=True, nullable=False)
    section_title = Column(String, nullable=False)
    chunk_text = Column(Text, nullable=False)
    token_frequencies_json = Column(Text, nullable=False) # JSON token frequency dictionary for TF-IDF
