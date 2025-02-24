import os
import sys
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.main import app

# warning은 무시
import warnings
warnings.filterwarnings("ignore")

client = TestClient(app)

def test_user_login_and_token():
    response = client.post("/api/user/token", data={"username": "test1", "password": "test1"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    globals()["customer_token"] = data["access_token"]

def test_get_schedule():
    headers = {"Authorization": f"Bearer {globals()['customer_token']}"}
    response = client.post("/api/reservation/schedule", headers=headers, json={
        "start_time": "2025-03-01T00:00:00",
        "end_time": "2025-03-02T00:00:00"
    })
    assert response.status_code == 200

def test_list_my_reservations():
    headers = {"Authorization": f"Bearer {globals()['customer_token']}"}
    response = client.get("/api/reservation/my", headers=headers)
    assert response.status_code == 200

def test_create_reservation_invalid_date():
    headers = {"Authorization": f"Bearer {globals()['customer_token']}"}
    # 3일 조건 테스트 (실패해야 함)
    response = client.post("/api/reservation/", headers=headers, json={
        "title": "예약 테스트",
        "description": "시험 예약",
        "reserved_count": 100,
        "start_time": datetime.utcnow().isoformat(),
        "end_time": datetime.utcnow().isoformat()
    })
    assert response.status_code == 400

def test_create_future_reservation():
    headers = {"Authorization": f"Bearer {globals()['customer_token']}"}
    future_start = (datetime.utcnow().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=5)).isoformat()
    future_end = (datetime.utcnow().replace(hour=11, minute=0, second=0, microsecond=0) + timedelta(days=5)).isoformat()
    response = client.post("/api/reservation/", headers=headers, json={
        "title": "미래 예약",
        "description": "테스트 예약",
        "reserved_count": 200,
        "start_time": future_start,
        "end_time": future_end
    })
    assert response.status_code == 201
    globals()["pending_id"] = response.json()["id"]

def test_delete_pending_reservation():
    headers = {"Authorization": f"Bearer {globals()['customer_token']}"}
    response = client.delete(f"/api/reservation/{globals()['pending_id']}", headers=headers)
    assert response.status_code == 200

def test_create_pending_reservation_for_confirm():
    headers = {"Authorization": f"Bearer {globals()['customer_token']}"}
    future_start = (datetime.utcnow().replace(hour=12, minute=0, second=0, microsecond=0) + timedelta(days=5)).isoformat()
    future_end = (datetime.utcnow().replace(hour=14, minute=0, second=0, microsecond=0) + timedelta(days=5)).isoformat()
    response = client.post("/api/reservation/", headers=headers, json={
        "title": "확정 테스트",
        "description": "대기중 예약",
        "reserved_count": 500,
        "start_time": future_start,
        "end_time": future_end
    })
    assert response.status_code == 201
    globals()["pending_for_confirm_id"] = response.json()["id"]

def test_create_congested_reservation():
    headers = {"Authorization": f"Bearer {globals()['customer_token']}"}
    response = client.post("/api/reservation/", headers=headers, json={
        "title": "혼잡 시간 예약",
        "description": "혼잡 시간 예약 시도",
        "reserved_count": 10000, # 이미 확정된 인원 50000명과 겹쳐 실패해야 함
        "start_time": "2025-03-01T03:00:00",
        "end_time": "2025-03-01T06:00:00"
    })
    assert response.status_code == 400

def test_try_delete_confirmed_reservation():
    # 관리자로 pending 예약 확정
    admin_res = client.post("/api/user/token", data={"username": "admin", "password": "admin"})
    admin_token = admin_res.json()["access_token"]
    headers_admin = {"Authorization": f"Bearer {admin_token}"}
    confirm_res = client.put(f"/api/reservation/{globals()['pending_for_confirm_id']}/confirm", headers=headers_admin)
    assert confirm_res.status_code == 200

    # 고객이 확정된 예약 삭제 시도 -> 실패
    headers_customer = {"Authorization": f"Bearer {globals()['customer_token']}"}
    response = client.delete(f"/api/reservation/{globals()['pending_for_confirm_id']}", headers=headers_customer)
    assert response.status_code == 400

def test_admin_manage():
    admin_res = client.post("/api/user/token", data={"username": "admin", "password": "admin"})
    admin_token = admin_res.json()["access_token"]
    headers_admin = {"Authorization": f"Bearer {admin_token}"}

    # 전체 예약 조회
    r = client.get("/api/reservation/all", headers=headers_admin)
    assert r.status_code == 200

    # 관리자는 예약 삭제 가능 (확정 예약 삭제)
    delete_res = client.delete(f"/api/reservation/{globals()['pending_for_confirm_id']}", headers=headers_admin)
    assert delete_res.status_code == 200

if __name__ == "__main__":
    test_user_login_and_token()
    test_get_schedule()
    test_list_my_reservations()
    test_create_reservation_invalid_date()
    test_create_future_reservation()
    test_delete_pending_reservation()
    test_create_pending_reservation_for_confirm()
    test_create_congested_reservation()
    test_try_delete_confirmed_reservation()
    test_admin_manage()
    print("All tests passed!")