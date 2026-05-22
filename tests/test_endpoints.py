import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.main import app, get_db
from backend.database import Base
from backend.models import CaseSubmission

# Create a shared SQLite DB for endpoint testing
TEST_DB_URL = "sqlite:///test_endpoints.db"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(test_db):
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

def test_create_case_endpoint(client):
    # 1. Post request to create case
    response = client.post(
        "/api/cases",
        data={
            "grievance": "Test grievance online transaction cheating.",
            "location": "Mumbai",
            "user_persona": "individual"
        }
    )
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "success"
    assert res_data["case_id"] is not None
    assert res_data["persona"] == "individual"

def test_upload_evidence_endpoint(client):
    # 1. Create a case
    create_res = client.post(
        "/api/cases",
        data={"grievance": "Test cheating case.", "location": "Delhi", "user_persona": "individual"}
    )
    case_id = create_res.json()["case_id"]

    # 2. Upload dummy files
    dummy_file_1 = ("receipt.png", b"dummy image contents", "image/png")
    dummy_file_2 = ("contract.pdf", b"dummy pdf contents", "application/pdf")
    
    response = client.post(
        f"/api/cases/{case_id}/evidence",
        files=[("files", dummy_file_1), ("files", dummy_file_2)]
    )
    
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "success"
    assert len(res_data["uploaded_evidence"]) == 2
    assert res_data["uploaded_evidence"][0]["filename"] == "receipt.png"

def test_case_list_and_delete_endpoints(client):
    # 1. Create cases
    client.post("/api/cases", data={"grievance": "Grievance 1", "user_persona": "individual"})
    client.post("/api/cases", data={"grievance": "Grievance 2", "user_persona": "lawfirm"})

    # 2. List cases
    list_res = client.get("/api/cases")
    assert list_res.status_code == 200
    cases = list_res.json()
    assert len(cases) >= 2
    
    case_ids = [c["id"] for c in cases]
    target_id = case_ids[0]

    # 3. Delete case
    del_res = client.delete(f"/api/cases/{target_id}")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "success"

    # 4. List again to confirm deletion
    list_res2 = client.get("/api/cases")
    cases2 = list_res2.json()
    case_ids2 = [c["id"] for c in cases2]
    assert target_id not in case_ids2

def test_full_analysis_and_dashboard_retrieval(client):
    # 1. Create a lawfirm case
    create_res = client.post(
        "/api/cases",
        data={
            "grievance": "WhatsApp threat and cheated Rs 50,000 in Mumbai.",
            "location": "Mumbai",
            "user_persona": "lawfirm"
        }
    )
    case_id = create_res.json()["case_id"]

    # 2. Trigger pipeline analysis (BYOK headers omitted to run in simulated mode)
    analyze_res = client.post(f"/api/cases/{case_id}/analyze")
    assert analyze_res.status_code == 200
    analyze_data = analyze_res.json()
    assert analyze_data["status"] == "success"
    assert analyze_data["persona"] == "lawfirm"

    # 3. Fetch Case Dashboard parameters
    dash_res = client.get(f"/api/cases/{case_id}/dashboard")
    assert dash_res.status_code == 200
    dash_data = dash_res.json()

    assert dash_data["case_id"] == case_id
    assert dash_data["user_persona"] == "lawfirm"
    assert dash_data["win_probability"] is not None
    assert dash_data["judge_verdict"] is not None
    assert "Mumbai" in dash_data["location"]
    
    # Assert debate logs were written
    assert len(dash_data["debate_logs"]) > 0
    # Assert RAG statutes matched
    assert len(dash_data["statutes"]) > 0
    # Mapped sections
    section_numbers = [s["section_number"] for s in dash_data["statutes"]]
    assert "318" in section_numbers or "303" in section_numbers
