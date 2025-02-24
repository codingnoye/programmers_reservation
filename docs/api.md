# API 문서

## 개요

아래 API 문서의 내용들은, 서버 실행 후 `127.0.0.1:8000/docs`에 접속하여 Swagger에서 Try it out 기능을 통해 직접 간단히 요청해볼 수 있습니다.  
생성하거나 수정하는 경우 해당 객체가 반환되며, 에러가 발생하면 HTTP 에러와 함께 에러 원인이 반환됩니다.  
삭제 시에는 결과 메시지가 반환됩니다.

## User API

### POST /api/user/token

- 설명: 유저 로그인 후 JWT 액세스 토큰을 발급합니다. 계정 생성 기능은 구현하지 않았으며, 테스트 계정으로 로그인이 가능합니다.
- 요청 (Form 데이터):
  - username: 사용자명
  - password: 비밀번호
- 응답 예시:
  {
    "access_token": "발급된 토큰",
    "token_type": "bearer"
  }

### GET /api/user/me

- 설명: 현재 액세스 토큰에 해당하는 사용자의 정보를 조회합니다.
- 헤더:
  - Authorization: Bearer {토큰}
- 응답 예시:
  {
    "username": "test1"
  }

## Reservation API

### POST /api/reservation/schedule

- 설명: 특정 기간 내 예약 가능 인원수를 시간대별로 확인합니다.
- 헤더:
  - Authorization: Bearer {토큰} (고객 또는 어드민)
- 요청 (JSON Body):
  - start_time: 시작 시간 (datetime)
  - end_time: 종료 시간 (datetime)
- 응답: 시간 구간별 예약 인원 리스트  
  예) [(시작, 종료, 예약 인원), …]

### POST /api/reservation/

- 설명: 고객이 예약을 생성합니다. 시작시간 기준 3일 이상의 여유가 있는 일자로만 생성 가능하며 5만 명 제한을 확인합니다.
- 헤더:
  - Authorization: Bearer {토큰} (고객)
- 요청 (JSON Body):
  - title: 시험 제목
  - description: 시험 설명
  - reserved_count: 예약 인원 수
  - start_time: 시험 시작 시간 (datetime)
  - end_time: 시험 종료 시간 (datetime)
- 응답: 생성된 예약 객체

### PUT /api/reservation/{reservation_id}

- 설명: 예약을 수정합니다. 시작시간 기준 3일 이상의 여유가 있는 일자로만 수정 가능하며 5만 명 제한을 확인합니다.
- 헤더:
  - Authorization: Bearer {토큰} (예약을 생성한 고객 또는 어드민)
- 요청 (JSON Body):
  - title, description, reserved_count, start_time, end_time
- 응답: 수정된 예약 객체

### PUT /api/reservation/{reservation_id}/confirm

- 설명: 관리자가 예약을 확정합니다.
- 헤더:
  - Authorization: Bearer {토큰} (어드민)
- 응답: 확정된 예약 객체

### DELETE /api/reservation/{reservation_id}

- 설명: 예약을 삭제합니다. 고객이 삭제하는 경우, 확정되기 전에만 삭제 가능합니다.
- 헤더:
  - Authorization: Bearer {토큰} (예약을 생성한 고객 또는 어드민)
- 응답: 삭제 결과 메시지

### GET /api/reservation/my

- 설명: 고객이 자신의 모든 예약 목록을 조회합니다.
- 헤더:
  - Authorization: Bearer {토큰} (고객 권한 필요)
- 응답: 고객의 예약 목록

### GET /api/reservation/all

- 설명: 관리자가 모든 사용자의 예약 목록을 조회합니다.
- 헤더:
  - Authorization: Bearer {토큰} (관리자 권한 필요)
- 응답: 전체 예약 목록
