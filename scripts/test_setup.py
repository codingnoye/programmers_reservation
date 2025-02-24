import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.db.migrate import generate_testusers, generate_testresvs

if __name__ == "__main__":
    generate_testusers()
    print("테스트 유저 생성 완료")
    generate_testresvs()
    print("테스트 일정 생성 완료")