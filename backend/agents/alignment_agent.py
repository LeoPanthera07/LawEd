import os
import json
import re
import httpx

# Pre-defined category BNS mappings to support fallback alignment
CATEGORY_BNS_MAP = {
    "cheating": ["318", "319", "61"],
    "theft": ["303", "61"],
    "trust_breach": ["316", "61"],
    "defamation": ["356"],
    "trespass": ["329"],
    "accident": ["281", "115", "117"],
    "hurt": ["115", "117"],
    "forgery": ["336", "61"],
    "threat": ["351"]
}

def classify_grievance_category(text: str) -> str:
    """Classifies the grievance text into a primary category based on keywords."""
    lower_text = text.lower()
    if any(k in lower_text for k in ["cheat", "scam", "fraud", "fake", "online", "money", "cheated", "lured", "payment"]):
        return "cheating"
    elif any(k in lower_text for k in ["steal", "theft", "stolen", "stole", "cctv", "robbed"]):
        return "theft"
    elif any(k in lower_text for k in ["trust", "partner", "misappropriated", "invested", "fiduciary", "ledger"]):
        return "trust_breach"
    elif any(k in lower_text for k in ["defame", "reputation", "post", "social", "libel", "slander"]):
        return "defamation"
    elif any(k in lower_text for k in ["trespass", "land", "broke in", "property", "entered", "encroach"]):
        return "trespass"
    elif any(k in lower_text for k in ["accident", "rash", "driving", "scooter", "bike", "motorcycle", "hit", "speeding", "negligent"]):
        return "accident"
    elif any(k in lower_text for k in ["hurt", "pain", "beaten", "slapped", "punched", "injury", "assault"]):
        return "hurt"
    elif any(k in lower_text for k in ["forged", "forgery", "fake document", "signature", "alter"]):
        return "forgery"
    elif any(k in lower_text for k in ["threat", "threatened", "alarm", "intimidated"]):
        return "threat"
    return "general"

def decide_statute_alignment(grievance: str, act_type: str, section_number: str, section_title: str, description: str, api_key: str = None, provider: str = "groq") -> bool:
    """
    Alignment Agent: Evaluates whether a statutory section (BNS/BNSS/BSA) 
    conceptually aligns with the facts of the citizen's grievance.
    Uses a cognitive LLM query when api_key is available, 
    otherwise falls back to category-based matching.
    """
    category = classify_grievance_category(grievance)
    
    if api_key:
        try:
            system_prompt = (
                "You are an expert Indian statutory alignment auditor. "
                "Determine whether the user's grievance narrative aligns with the legal definition and elements of the given statutory section.\n"
                "Return a JSON object with a single key \"aligned\" set to true or false.\n"
                "Only return true if the grievance contains facts that could reasonably fall under or relate to this section's legal description.\n"
                "Do NOT include any explanation or markdown. Return raw JSON only."
            )
            
            section_info = (
                f"Act: {act_type}\n"
                f"Section: {section_number}\n"
                f"Title: {section_title}\n"
                f"Description: {description}"
            )
            
            user_prompt = (
                f"Grievance Narrative:\n{grievance}\n\n"
                f"Statutory Section details:\n{section_info}"
            )
            
            if provider == "groq":
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                payload = {
                    "model": "llama-3.1-70b-versatile",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.0,
                    "response_format": {"type": "json_object"}
                }
            else:
                url = "https://api.openai.com/v1/chat/completions"
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                payload = {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.0,
                    "response_format": {"type": "json_object"}
                }
                
            r = httpx.post(url, headers=headers, json=payload, timeout=6.0)
            if r.status_code == 200:
                res_data = r.json()
                content = res_data["choices"][0]["message"]["content"]
                data = json.loads(content)
                return bool(data.get("aligned", False))
        except Exception as e:
            print(f"[Alignment Agent] LLM alignment check failed, using fallback: {e}")
            
    # Fallback heuristic rules
    if act_type == "BNS":
        # Substantive offences MUST align with the classified category to avoid false-positive RAG matches
        if category in CATEGORY_BNS_MAP:
            return section_number in CATEGORY_BNS_MAP[category]
        return False
        
    elif act_type == "BNSS":
        # Procedural matching
        if section_number == "173":  # FIR for cognizable cases
            return category in ["cheating", "theft", "trust_breach", "accident", "hurt", "forgery", "threat"]
        elif section_number == "223":  # Magistrate complaint (defamation, trespass, nuisance)
            return category in ["defamation", "trespass", "general"]
        elif section_number == "283":  # Summary trial
            return category in ["theft", "hurt", "trespass"]
        return True
        
    elif act_type == "BSA":
        # Evidentiary relevancy matching
        if section_number == "63":  # Electronic records admissibility
            has_digital = any(k in grievance.lower() for k in ["screenshot", "whatsapp", "email", "online", "chat", "message", "sms", "phone", "pdf", "bank", "ledger"])
            return has_digital
        return True
        
    return True
