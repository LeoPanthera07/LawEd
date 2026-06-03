# ⚖️ LawEdAI — Pre-Filing Legal Case Builder & Courtroom Simulation (Microservices Version)

**LawEdAI** is a premium, multi-agent pre-filing legal case-building and courtroom simulation platform tailored for the modern Indian legal ecosystem. It helps citizens and law firms navigate raw grievances by translating them into structured, evidence-supported legal drafts mapped directly to the new Indian penal codes:
* **BNS** (Bharatiya Nyaya Sanhita) — Replacing the Indian Penal Code (IPC) for substantive offenses.
* **BNSS** (Bharatiya Nagarik Suraksha Sanhita) — Replacing the Code of Criminal Procedure (CrPC) for procedural routes.
* **BSA** (Bharatiya Sakshya Adhiniyam) — Replacing the Indian Evidence Act (IEA) for evidence admissibility.

---

## 🌟 Key Features

1. **Dual Workspace Personas**:
   * **Individual Mode**: Streamlined interface for citizens. Focuses on intake, evidence upload, statutory mapping, and outputs a ready-made **Case Preparation Package** (Complaint Brief) to take to a law firm.
   * **Law Firm Mode**: Deep analytical portal. Unlocks the **LLM Court Simulation** showing an animated debate between a Plaintiff/Prosecution Lawyer Agent and a Defense Lawyer Agent, adjudicated by a Judge Agent. It compiles a rigorous **Adversarial Strength & Opponent Strategy Report** featuring a critical winning probability (%) and procedural warning triggers.
2. **Microservices Architecture**:
   * Configured as 4 independent, high-performance services coordinated via a central API Gateway:
     * **Auth Service** (Port `8001`): Standardizes login, signup, session control, and Role-Based Access Control (RBAC).
     * **RAG Service** (Port `8002`): Handles statutory PDF parsing, TF-IDF corpus token indexing, and semantic similarity searching.
     * **Courtroom Service** (Port `8003`): Operates courtroom agent mock trial simulations, objections handling, and verdict generation.
     * **Gateway Service** (Port `8000`): Serves the frontend web app and acts as a central proxy router.
3. **Statutory Alignment Agent & RAG**:
   * Leverages `backend/agents/alignment_agent.py` to audit keyword and semantic statutes mappings against scraped sections in `scraped_statutes.json`.
4. **Mock Trial Courtroom Objections**:
   * Features interactive courtroom objection handling (e.g. Objections under Section 63 BSA for electronic proof), allowing users to proceed or review objections before writeup formulation.
5. **Posh & Luxurious Serif UI**:
   * Styled in high-contrast light mode with elegant serif typography ('Playfair Display' and 'Lora'), interactive statutory pills, unique-ID docket tracking, a visual radial win probability dial, and a smooth collapsible history sidebar.
6. **Premium Golden Progress Loader**:
   * Replaced technical console debug log views with a clean golden-gradient progress bar and step-by-step progress descriptions, hiding low-level agent trackers from end users.

---

## 🚀 Quick Start Setup

### 1. Clone & Initialize Environment
```bash
git clone https://github.com/LeoPanthera07/LawEd.git
cd LawEd

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

### 3. Parse and Index Statutory PDFs
Before running simulations, scrape and index the text definitions from official BNS, BSA, and BNSS PDF files:
```bash
python backend/static_data/scrape_statutes.py
```

### 4. Boot Up all Microservices
Launch all 4 microservices simultaneously using the master bootloader:
```bash
python run_services.py
```
Open **`http://localhost:8000`** in your browser to experience LawEdAI!

---

## 🧪 Automated Testing
Run the comprehensive test suite verifying agents, statutory RAG indexers, and microservices REST endpoints:
```bash
PYTHONPATH=. pytest -v
```

---

## 📂 Repository Structure
```
LawEdAI/
├── Source/                 ← Raw Statutory PDFs (BNS, BSA, BNSS)
├── backend/
│   ├── database.py         ← Global SQLite connection & engine
│   ├── models.py           ← Shared database models (SQLAlchemy)
│   ├── static_data/
│   │   ├── scrape_statutes.py    ← PDF scraping controller
│   │   └── scraped_statutes.json ← Unified parsed statutory JSON database
│   ├── agents/             ← Legal reasoning agents
│   │   ├── alignment_agent.py    ← Auditing RAG semantic targets
│   │   ├── intake_agent.py
│   │   ├── legal_agent.py
│   │   ├── judge_agent.py
│   │   └── orchestrator.py
│   └── services/           ← Microservices
│       ├── auth/           ← Session management (Port 8001)
│       ├── rag/            ← Statutory vector retrieval (Port 8002)
│       ├── courtroom/      ← Mock trial orchestration (Port 8003)
│       └── gateway/        ← Central routing & UI hosting (Port 8000)
└── frontend/
    ├── index.html          ← SPA UI Layout
    └── assets/
        ├── styles/
        │   └── index.css   ← Premium light-mode serif styling
        └── js/
            └── app.js      ← Client-side state manager
```

---

Developed under strict Indian legal-safety, microservice scalability, and responsive-UX design tokens.
