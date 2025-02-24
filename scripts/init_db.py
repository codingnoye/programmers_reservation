import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.db.migrate import init_db

if __name__ == "__main__":
    init_db()
    print('DB 초기화 완료')