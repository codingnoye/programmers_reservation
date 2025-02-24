# 모델 설명 문서

## User 모델

- 설명: 사용자 정보를 저장하는 모델입니다.
- 필드:
  - id: Optional[int] - Primary Key
  - email: str - 사용자 이메일 (고유)
  - hashed_password: str - 해시된 비밀번호
  - username: str - 사용자 이름 (고유)
  - role: UserRole - 사용자 역할 (default: customer)
- 관계:
  - reservations: List[Reservation] - 사용자가 생성한 예약 리스트 (1:N 관계)

## Reservation 모델

- 설명: 예약 정보를 저장하는 모델입니다.
- 필드:
  - id: Optional[int] - Primary Key
  - user_id: int - 예약을 생성한 사용자의 ID (Foreign Key)
  - created_at: datetime - 예약 생성 일시 (default: 현재 시간)
  - updated_at: datetime - 예약 정보 수정 일시 (default: 현재 시간)
  - title: str - 예약 제목
  - description: str - 예약 상세 설명
  - reserved_count: int - 예약 인원 수
  - status: ReservationStatus - 예약 상태 (default: pending)
  - start_time: datetime - 시험(예약) 시작 시간
  - end_time: datetime - 시험(예약) 종료 시간
- 관계:
  - user: Optional[User] - 예약을 생성한 사용자와의 관계

## Enum 설명

### UserRole

- customer: 일반 고객 (기본값)
- admin: 관리자 권한

### ReservationStatus

- pending: 예약 대기 상태 (기본값)
- confirmed: 예약 확정 상태
