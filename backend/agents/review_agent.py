from sqlalchemy.orm import Session
from backend.models import CaseSubmission, FactExtraction, LegalReference, EvidenceItem, ReviewFlag

def run_review_agent(db: Session, case_id: int, api_key: str = None, provider: str = "groq") -> dict:
    """
    Review Agent: Inspects the facts, evidence logs, and legal codes to evaluate
    completeness, warn against weak assertions, and insert vital procedural safety guards.
    """
    case = db.query(CaseSubmission).filter(CaseSubmission.id == case_id).first()
    if not case:
        raise ValueError(f"Case with ID {case_id} not found.")

    facts = db.query(FactExtraction).filter(FactExtraction.case_id == case_id).first()
    legal_refs = db.query(LegalReference).filter(LegalReference.case_id == case_id).all()
    evidence = db.query(EvidenceItem).filter(EvidenceItem.case_id == case_id).all()

    # Clear old review flags
    db.query(ReviewFlag).filter(ReviewFlag.case_id == case_id).delete()

    flags = []

    # 1. Check for basic representation disclaimer (Mandatory Constraint in NexCourt PRD)
    disclaimer_flag = ReviewFlag(
        case_id=case_id,
        flag_type="procedural_hurdle",
        flag_title="Safety Guard: Not Legal Representation",
        message="This Case Brief is prepared automatically as pre-filing guidance. It does NOT constitute legal representation or binding judicial action. Please consult a qualified advocate to file this formally.",
        severity="Medium"
    )
    db.add(disclaimer_flag)
    flags.append(disclaimer_flag)

    # 2. Check for missing evidence (Fact vs. Evidence check)
    if not evidence:
        evidence_flag = ReviewFlag(
            case_id=case_id,
            flag_type="missing_evidence",
            flag_title="Zero Corroborating Evidence Uploaded",
            message="No physical evidence documents, receipts, or screenshots have been attached. Courts require primary or corroborating records to sustain a charge under BNS. Upload relevant screenshots/PDFs to strengthen this case.",
            severity="High"
        )
        db.add(evidence_flag)
        flags.append(evidence_flag)
    else:
        # Check if there's digital evidence without BSA Sec 63 certification warning
        has_digital = any("png" in e.filename.lower() or "jpg" in e.filename.lower() or "pdf" in e.filename.lower() or "screenshot" in e.filename.lower() for e in evidence)
        has_bsa_63 = any(ref.section_number == "63" and ref.code_type == "BSA" for ref in legal_refs)
        
        if has_digital and has_bsa_63:
            digital_cert_flag = ReviewFlag(
                case_id=case_id,
                flag_type="procedural_hurdle",
                flag_title="Digital Evidence Certification Mandated",
                message="Your electronic evidence (whatsapp logs, emails, receipts) requires a signed Digital Evidence Certificate under Section 63 BSA (formerly 65B Certificate) to be legally admissible. Failing this, the court can dismiss the digital proof.",
                severity="High"
            )
            db.add(digital_cert_flag)
            flags.append(digital_cert_flag)

    # 3. Check for specific substantive charges
    has_cheating = any(ref.section_number == "318" and ref.code_type == "BNS" for ref in legal_refs)
    if has_cheating:
        # Cheating requires proving "deceptive intent at the inception"
        intent_flag = ReviewFlag(
            case_id=case_id,
            flag_type="legal_risk",
            flag_title="Mens Rea / Dishonest Intention Requirement",
            message="To successfully establish cheating under Section 318 BNS, you must prove that the Accused had a dishonest or deceptive intention AT THE TIME the agreement/payment was made, and not just a subsequent breach of promise. Provide communication records showing prior deception if available.",
            severity="Medium"
        )
        db.add(intent_flag)
        flags.append(intent_flag)

    db.commit()

    return {
        "status": "success",
        "agent": "Review Agent",
        "flags_raised": len(flags),
        "flags": [f.flag_title for f in flags]
    }
