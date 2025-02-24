from sqlmodel import SQLModel
from app.db.session import engine, get_session
from sqlmodel import Session
from app.model.models import User, Reservation

from app.utils.crypto import hash_password

def init_db():
    SQLModel.metadata.create_all(engine)
    
def generate_testusers():
    with Session(engine) as session:
        user1 = User(
            email="test1@test.com",
            hashed_password=hash_password("test1"),
            username="test1",
            role="customer"
        )
        session.add(user1)
        user2 = User(
            email="test2@test.com",
            hashed_password=hash_password("test2"),
            username="test2",
            role="customer"
        )
        session.add(user2)
        admin = User(
            email="admin@test.com",
            hashed_password=hash_password("admin"),
            username="admin",
            role="admin"
        )
        session.add(admin)
        session.commit()

def generate_testresvs():
    with Session(engine) as session:
        user1 = session.query(User).filter(User.username == "test1").first()
        user2 = session.query(User).filter(User.username == "test2").first()
        resv1 = Reservation(
            user_id=user1.id,
            title="9시간 시험",
            description="1시부터 9시간동안 시험입니다.",
            reserved_count=10000,
            start_time="2025-03-01 01:00:00",
            end_time="2025-03-01 10:00:00",
            status="confirmed"
        )
        session.add(resv1)
        resv2 = Reservation(
            user_id=user1.id,
            title="2시간 시험",
            description="4시부터 2시간 시험입니다.",
            reserved_count=10000,
            start_time="2025-03-01 04:00:00",
            end_time="2025-03-01 06:00:00",
            status="confirmed"
        )
        session.add(resv2)
        resv3 = Reservation(
            user_id=user2.id,
            title="3시간 시험",
            description="2시부터 3시간 시험입니다.",
            reserved_count=30000,
            start_time="2025-03-01 02:00:00",
            end_time="2025-03-01 05:00:00",
            status="confirmed"
        )
        session.add(resv3)
        resv4 = Reservation(
            user_id=user2.id,
            title="7시간 시험",
            description="확정되지 않은 시험입니다.",
            reserved_count=30000,
            start_time="2025-03-01 12:00:00",
            end_time="2025-03-01 19:00:00",
        )
        session.add(resv4)
        session.commit()