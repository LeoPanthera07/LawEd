import os
import json
from sqlalchemy.orm import Session
from backend.models import CaseSubmission, LegalReference, PrecedentMatch
import httpx

def run_legal_agent(db: Session, case_id: int, api_key: str = None, provider: str = "groq") -> dict:
    """
    Legal Agent: Executes statutory and case law RAG.
    Identifies relevant BNS (penal), BSA (evidence), and BNSS (procedural) legal sections,
    and matches relevant Supreme Court of India precedents (1950-2025 AWS Open Data).
    Supports live LLM dynamic RAG search or high-value offline database matching.
    """
    case = db.query(CaseSubmission).filter(CaseSubmission.id == case_id).first()
    if not case:
        raise ValueError(f"Case with ID {case_id} not found.")

    grievance_text = case.grievance

    # If API Key is provided, execute a real dynamic LLM RAG statutory + case law search
    if api_key:
        try:
            rag_results = call_llm_for_rag(grievance_text, api_key, provider)
            
            matched_statutes = rag_results.get("statutes", [])
            save_legal_references(db, case_id, matched_statutes)
            
            matched_precedents = rag_results.get("precedents", [])
            save_precedent_matches(db, case_id, matched_precedents)
            
            return {
                "status": "success",
                "agent": "Legal Agent",
                "matched_count": len(matched_statutes),
                "precedents_count": len(matched_precedents),
                "statutes": [s["section_number"] + " " + s["act_title"] for s in matched_statutes]
            }
        except Exception as e:
            # Fallback to simulation/offline mode on error
            pass

    # Read statutes and past judgments databases
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    STATUTES_PATH = os.path.join(BASE_DIR, "static_data", "statutes.json")
    with open(STATUTES_PATH, "r", encoding="utf-8") as f:
        statutes = json.load(f)

    SCRAPED_STATUTES_PATH = os.path.join(BASE_DIR, "static_data", "scraped_statutes.json")
    scraped_statutes = {}
    if os.path.exists(SCRAPED_STATUTES_PATH):
        try:
            with open(SCRAPED_STATUTES_PATH, "r", encoding="utf-8") as f:
                scraped_statutes = json.load(f)
        except Exception as e:
            print(f"Error loading scraped statutes: {e}")

    PRECEDENTS_PATH = os.path.join(BASE_DIR, "static_data", "past_judgments.json")
    with open(PRECEDENTS_PATH, "r", encoding="utf-8") as f:
        past_judgments = json.load(f)

    lower_text = grievance_text.lower()
    from backend.agents.alignment_agent import decide_statute_alignment, classify_grievance_category
    category = classify_grievance_category(grievance_text)

    # 1. Query the offline-first statutory PDF RAG Microservice!
    pdf_rag_statutes = []
    try:
        # Query on local RAG microservice port 8002
        rag_service_url = "http://localhost:8002/api/rag/query"
        r = httpx.post(rag_service_url, json={"query": grievance_text}, timeout=5.0)
        if r.status_code == 200:
            rag_data = r.json()
            matches = rag_data.get("matches", [])
            for m in matches:
                act = m["act_type"]
                sec_num = m["section_number"]

                # Pull rich statutory definition details from statutes.json if present
                found_stat = None
                for s in statutes.get(act, []):
                    if s["section_number"] == sec_num:
                        found_stat = s.copy()
                        break
                
                # Fallback to scraped_statutes.json for clean text
                if not found_stat and act in scraped_statutes:
                    for s in scraped_statutes[act]:
                        if s["section_number"] == sec_num:
                            found_stat = {
                                "section_number": s["section_number"],
                                "section_title": s["section_title"],
                                "act_title": s["act_title"],
                                "description": s["content"],
                                "punishment": "As defined under the substantive provisions of the Act.",
                                "procedural_route": "Filing under standard judicial channels."
                            }
                            break

                if not found_stat:
                    act_full = "Bharatiya Nyaya Sanhita, 2023" if act == "BNS" else ("Bharatiya Nagarik Suraksha Sanhita, 2023" if act == "BNSS" else "Bharatiya Sakshya Adhiniyam, 2023")
                    found_stat = {
                        "section_number": sec_num,
                        "section_title": m["section_title"],
                        "act_title": act_full,
                        "description": m["text"],
                        "punishment": "As defined under the substantive provisions of the Act.",
                        "procedural_route": "Filing under standard judicial channels."
                    }

                # Evaluate alignment using Alignment Agent
                is_aligned = decide_statute_alignment(
                    grievance_text, act, sec_num, found_stat["section_title"], found_stat["description"],
                    api_key=api_key, provider=provider
                )
                if is_aligned:
                    pdf_rag_statutes.append(found_stat)
    except Exception as e:
        print(f"Local Statutory PDF RAG Service connection bypassed or offline: {e}")

    # 2. Match BNS substantive offenses via keywords/rules to ensure core offenses are never missed
    bns_matches = []
    for section in statutes.get("BNS", []):
        sec_num = section["section_number"]
        keywords = []
        if sec_num == "318": # Cheating
            keywords = ["cheat", "scam", "fraud", "fake", "online", "money", "paid", "refund", "cheated", "lured", "payment"]
            if any(k in lower_text for k in keywords):
                bns_matches.append(section)
        elif sec_num == "303": # Theft
            keywords = ["steal", "theft", "stolen", "stole", "cctv", "robbed", "housebreaker", "missing property", "laptop stolen", "purse stolen"]
            if any(k in lower_text for k in keywords):
                bns_matches.append(section)
        elif sec_num == "316": # Breach of trust
            keywords = ["trust", "partner", "misappropriated", "invested", "fiduciary", "breach", "entrusted", "office funds"]
            if any(k in lower_text for k in keywords):
                bns_matches.append(section)
        elif sec_num == "356": # Defamation
            keywords = ["defame", "reputation", "post", "social", "libel", "slander", "abused", "false tweet", "twitter"]
            if any(k in lower_text for k in keywords):
                bns_matches.append(section)
        elif sec_num == "329": # Trespass
            keywords = ["trespass", "land", "broke in", "property", "entered", "encroach", "tenant", "landlord", "flat"]
            if any(k in lower_text for k in keywords):
                bns_matches.append(section)
        elif sec_num == "115": # Simple Hurt
            keywords = ["hurt", "pain", "beaten", "slapped", "punched", "injury", "assault", "hit me"]
            if any(k in lower_text for k in keywords):
                bns_matches.append(section)
        elif sec_num == "117": # Grievous Hurt
            keywords = ["grievous", "fracture", "hospital", "broken bone", "severely beaten", "blinded", "permanent injury", "fractured"]
            if any(k in lower_text for k in keywords):
                bns_matches.append(section)
        elif sec_num == "336": # Forgery
            keywords = ["forged", "forgery", "fake document", "altered", "signature check", "fake contract", "fabricate", "fake id"]
            if any(k in lower_text for k in keywords):
                bns_matches.append(section)
        elif sec_num == "61": # Criminal Conspiracy
            keywords = ["conspiracy", "conspired", "planned together", "nexus", "group of people", "joint plan", "accomplice"]
            if any(k in lower_text for k in keywords):
                bns_matches.append(section)
        elif sec_num == "351": # Criminal Intimidation
            keywords = ["threat", "threatened", "alarm", "intimidated", "kill you", "extort threat", "abuse threat"]
            if any(k in lower_text for k in keywords):
                bns_matches.append(section)
        elif sec_num == "319": # Cheating by Personation
            keywords = ["personation", "pretended", "impersonate", "fake profile", "assumed identity", "impersonated"]
            if any(k in lower_text for k in keywords):
                bns_matches.append(section)
        elif sec_num == "270": # Public Nuisance
            keywords = ["nuisance", "pollution", "blocked", "garbage", "loudspeaker", "obstructed public"]
            if any(k in lower_text for k in keywords):
                bns_matches.append(section)

    # Fallback to general category default if no matches found at all
    if not bns_matches and not any(s.get("act_title") == "Bharatiya Nyaya Sanhita, 2023" or "BNS" in s.get("act_title", "") for s in pdf_rag_statutes):
        if "steal" in lower_text or "theft" in lower_text:
            bns_matches.append([s for s in statutes.get("BNS", []) if s["section_number"] == "303"][0])
        else:
            bns_matches.append([s for s in statutes.get("BNS", []) if s["section_number"] == "318"][0])

    if ("they" in lower_text or "dealers" in lower_text or "accomplices" in lower_text) and not any(s["section_number"] == "61" for s in bns_matches):
        conspiracy_sec = [s for s in statutes.get("BNS", []) if s["section_number"] == "61"]
        if conspiracy_sec:
            bns_matches.append(conspiracy_sec[0])

    # Run alignment check on fallback BNS matches
    aligned_bns_matches = []
    for s in bns_matches:
        if decide_statute_alignment(grievance_text, "BNS", s["section_number"], s["section_title"], s["description"], api_key=api_key, provider=provider):
            aligned_bns_matches.append(s)

    # Merge RAG BNS matches and fallback BNS matches safely
    final_bns = []
    seen_bns = set()
    
    # Add RAG matches first
    for s in pdf_rag_statutes:
        if "BNS" in s.get("act_title", "") or "Nyaya" in s.get("act_title", ""):
            if s["section_number"] not in seen_bns:
                final_bns.append(s)
                seen_bns.add(s["section_number"])
                
    # Add fallback matches
    for s in aligned_bns_matches:
        if s["section_number"] not in seen_bns:
            final_bns.append(s)
            seen_bns.add(s["section_number"])

    # 3. Always apply BNSS Procedural routes
    bnss_matches = []
    is_private_complaint = any(s["section_number"] in ["356", "329", "270"] for s in final_bns)
    
    for section in statutes.get("BNSS", []):
        if is_private_complaint and section["section_number"] == "223":
            bnss_matches.append(section)
        elif not is_private_complaint and section["section_number"] == "173":
            bnss_matches.append(section)
        
        if any(s["section_number"] in ["303", "329", "115"] for s in final_bns) and section["section_number"] == "283":
            bnss_matches.append(section)

    if not bnss_matches:
        bnss_matches.append(statutes.get("BNSS", [])[0])

    # 4. Always apply BSA Evidence rules
    bsa_matches = []
    has_digital = any(k in lower_text for k in ["screenshot", "whatsapp", "email", "online", "chat", "message", "sms", "phone", "pdf", "bank", "ledger"])
    
    for section in statutes.get("BSA", []):
        if section["section_number"] == "4":
            bsa_matches.append(section)
        if has_digital and section["section_number"] == "63":
            bsa_matches.append(section)
        if section["section_number"] == "104":
            bsa_matches.append(section)

    # Combine BNS, BNSS, BSA into matched_statutes
    matched_statutes = final_bns + bnss_matches + bsa_matches

    # Save legal references to DB
    save_legal_references(db, case_id, matched_statutes)
    
    # 4. Map Past Supreme Court Judgments
    matched_precedents = []
    for case_law in past_judgments:
        # Match based on offense category
        if case_law["category"] == category:
            matched_precedents.append(case_law)
        elif case_law["category"] == "general" and len(matched_precedents) < 2:
            matched_precedents.append(case_law)

    # Always ensure at least 2 relevant precedents are matched
    if len(matched_precedents) < 2:
        matched_precedents.extend(past_judgments[:2])
    
    # Save precedents to DB
    save_precedent_matches(db, case_id, matched_precedents[:3])

    return {
        "status": "success", 
        "agent": "Legal Agent", 
        "matched_count": len(matched_statutes), 
        "precedents_count": len(matched_precedents[:3]),
        "statutes": [s["section_number"] + " " + s["act_title"] for s in matched_statutes]
    }

def save_legal_references(db: Session, case_id: int, matched_statutes: list):
    db.query(LegalReference).filter(LegalReference.case_id == case_id).delete()
    for item in matched_statutes:
        ref = LegalReference(
            case_id=case_id,
            code_type="BNS" if "Nyaya" in item.get("act_title", "") or "BNS" in item.get("act_title", "") else ("BNSS" if "Nagarik" in item.get("act_title", "") or "BNSS" in item.get("act_title", "") else "BSA"),
            section_number=item["section_number"],
            section_title=item["section_title"],
            act_title=item["act_title"],
            description=item["description"],
            punishment=item.get("punishment"),
            procedural_route=item.get("procedural_route") or item.get("evidence_rule")
        )
        db.add(ref)
    db.commit()

def save_precedent_matches(db: Session, case_id: int, matched_precedents: list):
    db.query(PrecedentMatch).filter(PrecedentMatch.case_id == case_id).delete()
    for item in matched_precedents:
        pm = PrecedentMatch(
            case_id=case_id,
            citation=item["citation"],
            case_name=item["case_name"],
            year=item.get("year"),
            court=item.get("court") or "Supreme Court of India",
            summary=item["summary"],
            relevance=item["relevance"]
        )
        db.add(pm)
    db.commit()

def call_llm_for_rag(text: str, api_key: str, provider: str) -> dict:
    """Invokes the live LLM statutory & precedent RAG to extract sections and case law citations."""
    system_prompt = (
        "You are an expert Indian statutory & case law RAG engine. Identify all relevant sections from BNS (Bharatiya Nyaya Sanhita, 2023), BNSS (Bharatiya Nagarik Suraksha Sanhita, 2023), and BSA (Bharatiya Sakshya Adhiniyam, 2023) that apply to the user's grievance.\n"
        "Additionally, search your comprehensive knowledge base to retrieve exactly 2 to 3 landmark judgments delivered by the Supreme Court of India between 1950 and 2025 (representing the AWS Open Data sponsors registry) that are relevant to this grievance.\n"
        "Return your response ONLY as a JSON object with the exact keys \"statutes\" (list of section objects) and \"precedents\" (list of judgment objects).\n"
        "Statute objects must contain: \"section_number\", \"section_title\", \"act_title\", \"description\", \"punishment\", \"evidence_required\", \"procedural_route\".\n"
        "Precedent objects must contain: \"citation\" (e.g. 'AIR 2002 SC 2201'), \"case_name\" (e.g. 'S.W. Palanitkar v. State of Bihar'), \"year\" (integer), \"court\" (e.g. 'Supreme Court of India'), \"summary\", \"relevance\" explaining how it applies.\n"
        "Do NOT include any markdown formatting, backticks, or intro text. Return raw JSON only."
    )

    if provider == "groq":
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "llama-3.1-70b-versatile",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }
    else:  # openai
        url = "https://api.openai.com/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"}
        }

    response = httpx.post(url, headers=headers, json=payload, timeout=28.0)
    response.raise_for_status()
    res = response.json()
    content = res["choices"][0]["message"]["content"]
    return json.loads(content)
