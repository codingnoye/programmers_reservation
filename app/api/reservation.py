from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from datetime import datetime, timedelta
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from jose import jwt, JWTError

from app.db.session import get_session
from app.model.models import Reservation, User, UserRole

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/token")

# 현재 유저를 가져오는 의존성
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="잘못되었거나 만료된 토큰입니다.")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="잘못되었거나 만료된 토큰입니다.")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="잘못되었거나 만료된 토큰입니다.")
    return user

# 예약 가능 인원수 확인
# 시작일시, 종료일시 -> 해당 일시 내의 모든 확정된 예약을 가져와서
# 각 시간 선분마다 몇 명의 예약이 있는지 확인 (겹치기 고려)
# 즉 00:00 ~ 24:00로 쿼리했다면
# [(00:00, 01:30, 0), (01:30, 02:00, 20000), (02:00, 04:00, 50000), (04:00, 04:30, 30000), (04:30, 24:00, 0)]
# 이런 식으로 반환
def check_schedule(start_time: datetime, end_time: datetime, db: Session) -> list:
    # 변수를 offset-naive로 변환
    start_time = start_time.replace(tzinfo=None)
    end_time = end_time.replace(tzinfo=None)
    
    # 겹치는 예약 모두 조회
    reservations = db.query(Reservation).filter(
        start_time < Reservation.end_time,
        Reservation.start_time < end_time,
        Reservation.status == "confirmed"
    ).all()
    
    events = []
    for r in reservations:
        # 각 예약의 시작/종료 시간도 naive로 변환
        r_start = r.start_time.replace(tzinfo=None)
        r_end = r.end_time.replace(tzinfo=None)
        events.append((r_start, r.reserved_count))
        events.append((r_end, -r.reserved_count))
    # 시간 순으로 정렬, 시간이 같은 경우 종료가 먼저
    events.sort()
    
    # 시구간별 인원 반환
    result = []
    current_time = start_time
    current_count = 0
    for event in events:
        if event[0] > current_time:
            result.append((current_time, event[0], current_count))
            current_time = event[0]
        current_count += event[1]
    if current_time < end_time:
        result.append((current_time, end_time, current_count))
    elif len(result) > 0:
        result[-1] = (result[-1][0], end_time, result[-1][2])
    else:
        result.append((start_time, end_time, 0))
    return result

# 예약 일정 요청 모델
class ReservationScheduleRequest(BaseModel):
    start_time: datetime
    end_time: datetime
    
@router.post("/schedule")
async def get_schedule(
    schedule: ReservationScheduleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    return check_schedule(schedule.start_time, schedule.end_time, db)

# 예약 생성
class ReservationCreate(BaseModel):
    title: str
    description: str
    reserved_count: int
    start_time: datetime
    end_time: datetime

@router.post("/", status_code=201)
async def create_reservation(
    reservation: ReservationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    if current_user.role != UserRole.customer:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="고객이 아닙니다.")
    
    # 시작 3일 전까지만 예약 가능
    if reservation.start_time.replace(tzinfo=None) < datetime.utcnow().replace(tzinfo=None) + timedelta(days=3):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="3일 전까지만 예약 가능합니다.")
    
    # 예약 가능 인원 확인
    schedule = check_schedule(reservation.start_time, reservation.end_time, db)
    max_reserved = max([s[2] for s in schedule])
    if max_reserved + reservation.reserved_count > 50000:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="예약 가능 인원을 초과해 신청에 실패했습니다.")

    new_reservation = Reservation(
        user_id=current_user.id,
        title=reservation.title,
        description=reservation.description,
        reserved_count=reservation.reserved_count,
        start_time=reservation.start_time,
        end_time=reservation.end_time,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(new_reservation)
    db.commit()
    db.refresh(new_reservation)
    return new_reservation

# 예약 수정
class ReservationUpdate(BaseModel):
    title: str
    description: str
    reserved_count: int
    start_time: datetime
    end_time: datetime

@router.put("/{reservation_id}")
def update_reservation(
    reservation_id: int,
    reservation: ReservationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    db_reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not db_reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="예약을 찾을 수 없습니다.")
    if db_reservation.user_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="수정 권한이 없습니다.")
    if db_reservation.status == "confirmed" and current_user.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="확정된 예약은 수정할 수 없습니다.")
    
    # 시작 3일 전까지만 예약 가능
    if reservation.start_time.replace(tzinfo=None) < datetime.utcnow().replace(tzinfo=None) + timedelta(days=3):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="3일 전까지만 예약 수정 가능합니다.")
    
    # 예약 가능 인원 확인
    schedule = check_schedule(reservation.start_time, reservation.end_time, db)
    max_reserved = max([s[2] for s in schedule])
    if max_reserved + reservation.reserved_count - db_reservation.reserved_count > 50000:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="예약 가능 인원을 초과해 수정에 실패했습니다.")
    
    db_reservation.title = reservation.title
    db_reservation.description = reservation.description
    db_reservation.reserved_count = reservation.reserved_count
    db_reservation.start_time = reservation.start_time
    db_reservation.end_time = reservation.end_time
    db_reservation.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_reservation)
    return db_reservation

# 예약 확정
@router.put("/{reservation_id}/confirm")
def confirm_reservation(
    reservation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    db_reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not db_reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="예약을 찾을 수 없습니다.")
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="확정 권한이 없습니다.")
    db_reservation.status = "confirmed"
    db.commit()
    db.refresh(db_reservation)
    return db_reservation

# 예약 삭제
@router.delete("/{reservation_id}")
def delete_reservation(
    reservation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    db_reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not db_reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="예약을 찾을 수 없습니다.")
    if db_reservation.user_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="삭제 권한이 없습니다.")
    if db_reservation.status == "confirmed" and current_user.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="확정된 예약은 삭제할 수 없습니다.")
    db.delete(db_reservation)
    db.commit()
    return {"message": "예약이 삭제되었습니다."}

@router.get("/my")
async def get_my_reservations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    if current_user.role != UserRole.customer:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="권한이 없습니다.")
    reservations = db.query(Reservation).filter(Reservation.user_id == current_user.id).all()
    return reservations

@router.get("/all")
async def get_all_reservations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="어드민만이 확인 가능합니다.")
    reservations = db.query(Reservation).all()
    return reservations
