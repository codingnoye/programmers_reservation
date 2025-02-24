import os, sys
# 프로젝트 루트를 sys.path 최상단에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_login_token():
    # 테스트 유저의 이메일과 비밀번호를 이용하여 로그인 요청 (OAuth2PasswordRequestForm 필드 'username'에 이메일을 사용)
    response = client.post(
        "/api/user/token", 
        data={"username": "test1", "password": "test1"}
    )
    try:
        assert response.status_code == 200
        json_data = response.json()
        assert "access_token" in json_data
        print(response.json())
    except:
        print(response.json())
        raise

if __name__ == "__main__":
    print("테스트1: 로그인 토큰 테스트")
    test_login_token()