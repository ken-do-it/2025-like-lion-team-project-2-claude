# AI Music Gen - Backend API

음악 공유 SNS 플랫폼의 백엔드 API 서버입니다.

## Tech Stack

- **Framework**: FastAPI 0.116.1
- **Database**: PostgreSQL + SQLAlchemy 2.1.2
- **Cache**: Redis 6.1.0
- **Storage**: AWS S3 (Boto3 1.35.40)
- **Authentication**: JWT (RS256) via external Auth Server
- **Background Tasks**: Celery 5.4.0

## Project Structure

```
team_2_music_back/
├── app/
│   ├── core/           # 핵심 설정 (config, database, redis)
│   ├── models/         # SQLAlchemy 모델
│   ├── schemas/        # Pydantic 스키마
│   ├── routes/         # API 엔드포인트
│   ├── middleware/     # 미들웨어 (JWT 검증 등)
│   ├── services/       # 비즈니스 로직
│   └── utils/          # 유틸리티 함수
├── tests/              # 테스트 코드
├── main.py             # 애플리케이션 진입점
├── requirements.txt    # Python 의존성
└── .env.example        # 환경 변수 예시
```

## Setup

### 1. Python 가상환경 생성 및 활성화

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

```bash
# .env.example을 .env로 복사하고 값 수정
cp .env.example .env
```

### 4. 데이터베이스 마이그레이션 (추후 추가)

```bash
alembic upgrade head
```

### 5. 서버 실행

```bash
# 개발 모드 (hot reload)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 프로덕션 모드
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development Status

- [x] 프로젝트 구조 생성
- [x] 의존성 정의 (requirements.txt)
- [x] 환경 변수 템플릿 (.env.example)
- [ ] 데이터베이스 모델 구현
- [ ] JWT 인증 미들웨어
- [ ] 기본 API 엔드포인트
- [ ] S3 업로드 기능
- [ ] 스트리밍 기능

## Architecture

전체 아키텍처 및 설계 문서는 `.claude/skills/Music-Social-Sharing-Platform-process/SKILL.md`를 참고하세요.

## Testing

```bash
# 전체 테스트 실행
pytest

# 커버리지 포함
pytest --cov=app tests/

# 특정 테스트 파일
pytest tests/test_auth.py -v
```

## Code Quality

```bash
# 코드 포맷팅
black app/ tests/

# 린팅
flake8 app/ tests/

# 타입 체크
mypy app/
```
