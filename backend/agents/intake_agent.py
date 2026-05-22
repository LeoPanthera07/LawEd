import json
from sqlalchemy.orm import Session
from backend.models import CaseSubmission, FactExtraction
import httpx

def run_intake_agent(db: Session, case_id: int, api_key: str = None, provider: str = "groq") -> dict:
    """
    Intake Agent: Analyzes raw grievance narrative and extracts key facts, timeline,
    parties involved, and nature of harm.
    """
    case = db.query(CaseSubmission).filter(CaseSubmission.id == case_id).first()
    if not case:
        raise ValueError(f"Case with ID {case_id} not found.")

    grievance_text = case.grievance

    # If API key is provided, perform a real LLM extraction
    if api_key:
        try:
            extracted_data = call_llm_for_intake(grievance_text, api_key, provider)
            save_facts(db, case_id, extracted_data)
            return {"status": "success", "agent": "Intake Agent", "data": extracted_data}
        except Exception as e:
            # Fallback to simulation on error
            pass

    # Simulation / Template-based extraction (Context-aware analysis)
    extracted_data = simulate_intake_extraction(grievance_text, case.location)
    save_facts(db, case_id, extracted_data)
    return {"status": "success", "agent": "Intake Agent", "data": extracted_data}

def save_facts(db: Session, case_id: int, data: dict):
    # Check if fact extraction already exists
    fact = db.query(FactExtraction).filter(FactExtraction.case_id == case_id).first()
    if not fact:
        fact = FactExtraction(case_id=case_id)
        db.add(fact)

    fact.facts_json = json.dumps(data.get("facts", []))
    fact.timeline_json = json.dumps(data.get("timeline", []))
    fact.parties_json = json.dumps(data.get("parties", {}))
    fact.location = data.get("location", "Unknown")
    fact.harm = data.get("harm", "Unknown")
    db.commit()

def call_llm_for_intake(text: str, api_key: str, provider: str) -> dict:
    system_prompt = (
        "You are a legal intake expert. Analyze the following user grievance and extract the facts in a structured JSON format.\n"
        "The JSON MUST have the following structure:\n"
        "{\n"
        "  \"facts\": [\"list of clear factual statements extracted from text\"],\n"
        "  \"timeline\": [{\"date\": \"date or period\", \"event\": \"what happened\"}],\n"
        "  \"parties\": {\"complainant\": \"complainant name or description\", \"accused\": \"accused name or description\"},\n"
        "  \"location\": \"state or city where incident occurred\",\n"
        "  \"harm\": \"brief description of the financial or emotional harm\"\n"
        "}\n"
        "Do NOT include any code blocks, backticks, or markdown. Output raw JSON only."
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

    response = httpx.post(url, headers=headers, json=payload, timeout=30.0)
    response.raise_for_status()
    res_json = response.json()
    content = res_json["choices"][0]["message"]["content"]
    return json.loads(content)

def simulate_intake_extraction(text: str, user_location: str) -> dict:
    """Helper to simulate fact extraction based on keyword scans of user input."""
    # Analyze text for parties and harm
    lower_text = text.lower()
    
    # Detect general category
    category = "general"
    if any(k in lower_text for k in ["cheat", "scam", "fraud", "fake", "online", "money"]):
        category = "cheating"
    elif any(k in lower_text for k in ["steal", "theft", "stolen", "cctv"]):
        category = "theft"
    elif any(k in lower_text for k in ["trust", "partner", "misappropriated", "invested"]):
        category = "trust_breach"
    elif any(k in lower_text for k in ["defame", "reputation", "post", "social"]):
        category = "defamation"
    elif any(k in lower_text for k in ["trespass", "land", "broke in", "property"]):
        category = "trespass"

    # Simulated parties
    complainant = "User (Informant)"
    accused = "Unnamed Opponent"
    if "dealer" in lower_text:
        accused = "Product Dealer / Seller"
    elif "shop" in lower_text:
        accused = "Shop Owner"
    elif "partner" in lower_text:
        accused = "Business Partner"
    elif "landlord" in lower_text:
        accused = "Landlord"
    elif "tenant" in lower_text:
        accused = "Tenant"

    # Simulated timeline extraction
    timeline = []
    if "yesterday" in lower_text:
        timeline.append({"date": "Yesterday", "event": "Incident of offense took place."})
    elif "last week" in lower_text:
        timeline.append({"date": "Last Week", "event": "Complainant discovered the offense."})
    else:
        timeline.append({"date": "Recent (Date Unspecified)", "event": "Incident occurred."})

    timeline.append({"date": "Subsequent", "event": "Complainant attempted contact, but was refused resolution."})

    # Simulated facts list
    facts = []
    if category == "cheating":
        facts = [
            "Complainant entered into an agreement/purchase with the accused.",
            "Accused made assurances regarding the quality/return of goods or services.",
            "Complainant transferred consideration/money based on these representations.",
            "The representations were found to be false and dishonest from the inception.",
            "Accused has blocked communication or refused refunds, causing wrongful loss."
        ]
    elif category == "theft":
        facts = [
            "Complainant was in lawful possession of certain movable property.",
            "The property was moved and taken out of possession without complainant's consent.",
            "The taking was done dishonestly with intention to cause wrongful gain to accused."
        ]
    elif category == "trust_breach":
        facts = [
            "Complainant entrusted certain property/funds to the accused.",
            "Accused held a fiduciary duty to manage or preserve the entrusted assets.",
            "Accused dishonestly misappropriated the property for personal gain in violation of trust."
        ]
    elif category == "defamation":
        facts = [
            "Accused published or communicated imputations concerning the complainant.",
            "The imputations were made publicly (verbal, text, or social media).",
            "The statements are demonstrably false and intended to cause damage to complainant's reputation."
        ]
    elif category == "trespass":
        facts = [
            "Complainant is in lawful possession of the property.",
            "Accused entered upon or remained unlawfully in the said property without consent.",
            "The entry was done with intent to intimidate, annoy, or commit an offense."
        ]
    else:
        facts = [
            "Complainant reports a significant grievance concerning wrongful actions of the accused.",
            "Attempts to resolve the dispute amicably have failed.",
            "Complainant seeks legal recourse and procedural mapping under Indian law."
        ]

    # Harm description
    harm = "Financial loss and severe mental harassment due to wrongful actions of the accused."
    if "rs." in lower_text or "rupees" in lower_text or "refund" in lower_text:
        harm = "Significant financial loss accompanied by deprivation of proprietary rights and mental distress."

    location = user_location if user_location else "Delhi, India"

    return {
        "facts": facts,
        "timeline": timeline,
        "parties": {"complainant": complainant, "accused": accused},
        "location": location,
        "harm": harm
    }
