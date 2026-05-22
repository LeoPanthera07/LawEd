# ⚖️ LawEdAI — Pre-Filing Legal Case Builder & Courtroom Simulation

**LawEdAI** is a premium, multi-agent pre-filing legal case-building and courtroom simulation platform tailored for the modern Indian legal ecosystem. It helps citizens and law firms navigate raw grievances by translating them into structured, evidence-supported legal drafts mapped directly to the new Indian penal codes:
* **BNS** (Bharatiya Nyaya Sanhita) — Replacing the Indian Penal Code (IPC) for substantive offenses.
* **BNSS** (Bharatiya Nagarik Suraksha Sanhita) — Replacing the Code of Criminal Procedure (CrPC) for procedural routes.
* **BSA** (Bharatiya Sakshya Adhiniyam) — Replacing the Indian Evidence Act (IEA) for evidence admissibility.

---

## 🌟 Key Features

1. **Dual Workspace Personas**:
   * **Individual Mode**: Streamlined interface for citizens. Focuses on intake, evidence upload, statutory mapping, and outputs a ready-made **Case Preparation Package** to take to a law firm.
   * **Law Firm Mode**: Deep analytical portal. Unlocks the **LLM Court Simulation** showing an animated debate between a Plaintiff/Prosecution Lawyer Agent and a Defense Lawyer Agent, adjudicated by a Judge Agent. It compiles a rigorous **Adversarial Strength & Opponent Strategy Report** featuring a critical winning probability (%) and procedural warning triggers.
2. **Statutory Agentic RAG**:
   * Performs real-time retrieval-augmented reasoning against a curated database of BNS, BSA, and BNSS sections, mapping the complaint to exact offenses, punishments, procedural routes (e.g. Section 173 BNSS for FIRs), and evidence requirements (e.g. Section 63 BSA for electronic records).
3. **LLM Court Mock Trial Simulation**:
   * Simulates a mock trial where the prosecution and defense argue based on statutes, exposing exactly how the opposing side might leverage loopholes, culminating in an authoritative judicial ruling.
4. **Gorgeous Glassmorphic UX**:
   * A premium dark-glassmorphic SPA featuring mesh gradients, micro-animations, pulsing agent rings, a radial win probability dial, and a typewriter courtroom transcript log.
5. **BYOK (Bring Your Own Key)**:
   * Accessible out-of-the-box with a high-fidelity context-aware Mock Simulator, and connects instantly to real LLMs (Groq LLaMA or OpenAI GPT-4o) using user keys saved securely in the browser's local storage.

---

## 🚀 Quick Start Setup

### 1. Clone or Open Folder and Initialize Environment
```bash
cd LawEdAI

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 2. Configure Local Settings
```bash
cp .env.example .env
```

### 3. Launch Serving Gateway
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```
Open **`http://localhost:8000`** in your browser to experience LawEdAI!

---

## 🧪 Automated Testing
Run the comprehensive test suite verifying agents, statutory RAG, and REST endpoints:
```bash
PYTHONPATH=. pytest -v
```

---

## 📂 Repository Structure
```
LawEdAI/
├── backend/
│   ├── main.py            ← FastAPI entry point
│   ├── database.py        ← SQLite connection & engine
│   ├── models.py          ← Database models (SQLAlchemy)
│   ├── static_data/
│   │   └── statutes.json  ← seed statutory sections (BNS/BSA/BNSS)
│   └── agents/            ← Legal reasoning agents
│       ├── intake_agent.py
│       ├── evidence_agent.py
│       ├── legal_agent.py
│       ├── drafting_agent.py
│       ├── review_agent.py
│       ├── plaintiff_agent.py
│       ├── defense_agent.py
│       ├── judge_agent.py
│       └── orchestrator.py
└── frontend/
    ├── index.html         ← SPA UI Layout
    └── assets/
        ├── styles/
        │   └── index.css  ← Premium Glassmorphism CSS
        └── js/
            └── app.js     ← Client state & API connector
```

---

Developed under strict modern legal-safety, structural-traceability, and responsive-UX guidelines.
