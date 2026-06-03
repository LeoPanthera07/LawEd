import math
import json
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from backend.services.rag.database import get_db, Base, engine, SessionLocal
from backend.services.rag.models import StatuteChunk
from backend.services.rag.indexer import build_rag_index, tokenize

# Create database tables
Base.metadata.create_all(bind=engine)

# Trigger statutory PDF indexing on startup
db_init = SessionLocal()
try:
    build_rag_index(db_init, force_reindex=False)
finally:
    db_init.close()

app = FastAPI(
    title="LawEdAI Statutory RAG & Vector Engine",
    description="Microservice providing offline-first PDF indexing and cosine-similarity searches."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/rag/status")
def status(db: Session = Depends(get_db)):
    """Returns indexing summary metrics."""
    chunk_count = db.query(StatuteChunk).count()
    bns_count = db.query(StatuteChunk).filter(StatuteChunk.act_type == "BNS").count()
    bnss_count = db.query(StatuteChunk).filter(StatuteChunk.act_type == "BNSS").count()
    bsa_count = db.query(StatuteChunk).filter(StatuteChunk.act_type == "BSA").count()
    
    return {
        "status": "active",
        "total_chunks": chunk_count,
        "act_breakdown": {
            "BNS": bns_count,
            "BNSS": bnss_count,
            "BSA": bsa_count
        }
    }

# Semantic expansion vocabulary to bridge vocabulary gap
SEMANTIC_THEMES = {
    "accident": ["rash", "driving", "negligent", "vehicle", "scooter", "bike", "motorcycle", "car", "hit", "speeding", "road", "public", "collision"],
    "cheating": ["cheat", "cheated", "scam", "scammed", "fraud", "fake", "online", "money", "paid", "refund", "whatsapp", "deceive", "dishonest", "induce"],
    "theft": ["theft", "steal", "stolen", "stole", "cctv", "robbed", "purse", "movable", "possession", "consent"],
    "trust": ["breach", "entrusted", "misappropriation", "fiduciary", "partner", "ledger", "office", "funds"],
    "defamation": ["defame", "defamed", "reputation", "post", "social", "libel", "slander", "false", "tweet", "publish", "harm"],
    "threat": ["threat", "threatened", "alarm", "intimidation", "kill", "abuse", "extort"],
    "hurt": ["hurt", "grievous", "injury", "fracture", "hospital", "pain", "beaten", "slapped", "punched", "assault"]
}

@app.post("/api/rag/query")
def query_statutes(payload: dict, db: Session = Depends(get_db)):
    """
    Executes a cosine-similarity TF-IDF query over statutory chunks in SQLite with query expansion.
    Expects json payload: {"query": "grievance string"}
    """
    query_str = payload.get("query", "").strip()
    if not query_str:
        return {"matches": []}

    query_tokens = tokenize(query_str)
    if not query_tokens:
        return {"matches": []}

    # Expand query tokens with semantic synonyms
    expanded_tokens = list(query_tokens)
    for theme, keywords in SEMANTIC_THEMES.items():
        if any(k in query_str.lower() for k in keywords):
            expanded_tokens.extend(keywords)
            
    query_tokens = list(set(expanded_tokens))

    total_chunks = db.query(StatuteChunk).count()
    if total_chunks == 0:
        return {"matches": []}

    # 1. Compute query token TF and dynamic document IDF
    query_tf = {}
    for t in query_tokens:
        query_tf[t] = query_tf.get(t, 0) + 1
    total_q_tokens = len(query_tokens)
    query_tf = {k: v / total_q_tokens for k, v in query_tf.items()}

    idf = {}
    candidate_ids = set()
    
    for token in set(query_tokens):
        # Query count of chunks containing this token
        chunks_with_token = db.query(StatuteChunk.id).filter(StatuteChunk.chunk_text.like(f"%{token}%")).count()
        # Compute TF-IDF IDF factor
        idf[token] = math.log((total_chunks + 1) / (chunks_with_token + 1)) + 1
        
        # Pull candidates containing this token
        rows = db.query(StatuteChunk.id).filter(StatuteChunk.chunk_text.like(f"%{token}%")).limit(200).all()
        for r in rows:
            candidate_ids.add(r[0])

    if not candidate_ids:
        return {"matches": []}

    # 2. Compute Query vector length
    query_vector_weights = {}
    query_len_sq = 0
    for t in query_tokens:
        weight = query_tf[t] * idf[t]
        query_vector_weights[t] = weight
        query_len_sq += weight ** 2
    query_len = math.sqrt(query_len_sq)

    # 3. Compute cosine similarities over candidates
    results = []
    candidates = db.query(StatuteChunk).filter(StatuteChunk.id.in_(list(candidate_ids))).all()

    for chunk in candidates:
        chunk_tf = json.loads(chunk.token_frequencies_json)
        
        # Calculate dot product
        dot_product = 0
        chunk_len_sq = 0
        
        for t, tf in chunk_tf.items():
            token_idf = idf.get(t, 1)
            w_chunk = tf * token_idf
            chunk_len_sq += w_chunk ** 2
            if t in query_vector_weights:
                dot_product += query_vector_weights[t] * w_chunk
                
        chunk_len = math.sqrt(chunk_len_sq)
        score = dot_product / (query_len * chunk_len) if query_len > 0 and chunk_len > 0 else 0

        if score > 0.01:
            results.append({
                "score": round(score, 4),
                "act_type": chunk.act_type,
                "section_number": chunk.section_number,
                "section_title": chunk.section_title,
                "text": chunk.chunk_text[:350] + "..." if len(chunk.chunk_text) > 350 else chunk.chunk_text
            })

    # Sort and return top 5
    results.sort(key=lambda x: x["score"], reverse=True)
    return {"matches": results[:5]}
