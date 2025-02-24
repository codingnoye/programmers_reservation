from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

# 유저 role enum
class UserRole(str, Enum):
    admin = 'admin'
    customer = 'customer'
    
# 유저 모델
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str
    username: str = Field(index=True, unique=True)
    role: UserRole = Field(default=UserRole.customer)

    reservations: List['Reservation'] = Relationship(back_populates='user')

# 예약 상태 enum
class ReservationStatus(str, Enum):
    pending = 'pending'
    confirmed = 'confirmed'

# 예약 모델
class Reservation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    user_id: int = Field(foreign_key='user.id')
    user: Optional[User] = Relationship(back_populates='reservations')
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    title: str
    description: str
    reserved_count: int
    status: ReservationStatus = Field(default=ReservationStatus.pending)
    
    # 시험 일시
    start_time: datetime
    end_time: datetime
    
