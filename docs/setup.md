# 설정, 실행, 테스트 방법 문서

## 설정

1. Python 3.12.4버전을 설치하고 venv를 생성합니다.
    - `python3 -m venv venv`
    - `source venv/bin/activate`
2. PostgreSQL 서버는 설정되어 있다고 가정합니다.
3. PostgreSQL과 연결하기 위한 패키지 `psycopg2`를 설치합니다. pip로 설치가 가능하지만 환경에 따라 다른 설치가 필요할 수 있어 명시합니다.
    - pip를 최신으로 업데이트합니다.
    - `pip install --upgrade pip`
    - 두 가지 방법을 시도합니다.
    - `pip install psycopg2-binary`
    - `pip install psycopg2`
    - 환경에 따라 너무 다양한 에러가 발생할 수 있는 것으로 보여 모든 경우를 서술하지는 않습니다.
4. `requirements.txt`에 있는 패키지들을 설치한 후 터미널을 재시작합니다.
    - `pip install -r requirements.txt`
5. `.env.example` 파일을 복사하여 `.env` 파일을 생성하고 값들을 설정합니다.
    - DB에 맞게 정보를 설정합니다.
    - `SECRET_KEY`는 임의로 설정합니다.
    - 터미널 재시작이 필요할 수 있습니다.
6. 데이터베이스를 마이그레이션합니다. 프로젝트 루트에서 다음 명령어를 실행합니다.
    - `python scripts/init_db.py`: db를 초기화합니다.
    - `python scripts/test_setup.py`: 테스트 계정 및 테스트 데이터를 생성합니다.

## 실행

1. 프로젝트 루트에서 다음 명령어를 실행합니다.
    - `uvicorn app.main:app --reload`
2. 브라우저에서 `http://127.0.0.1:8000/docs`로 접속하여 API 문서를 확인합니다.
    - `swagger`를 사용하여 API 문서를 확인 및 테스트할 수 있습니다.

## 테스트

1. 기본적인 기능들을 테스트하기 위해 프로젝트 루트에서 다음 명령어를 실행합니다.
    - `python3 tests/tests.py`
    - 오류가 없다면 테스트가 성공적으로 완료된 것입니다.
    - 코드를 확인해보시면 어떤 테스트가 진행되었는지 확인할 수 있습니다.
2. API 문서를 통해 직접 테스트를 진행할 수 있습니다.
    - `http://127.0.0.1:8000/docs`로 접속하여 테스트를 진행합니다.
    - 우측 상단의 `Authorizate` 버튼을 누르고 `test1 / test1`로 로그인하여 토큰을 저장합니다.
    - API 문서에서 `Try it out` 버튼을 눌러 테스트를 진행합니다. 토큰은 자동으로 입력됩니다.

## 참고

- 계정은 고객 계정 `test1 / test1`, `test2 / test2`가 생성되어 있습니다.
- 어드민 계정은 `admin / admin`입니다.
- 테스트 데이터는 `app/db/migrate.py`에서 확인할 수 있습니다.
