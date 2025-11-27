# AI Music Gen - 음악 소셜 공유 플랫폼

AI가 생성한 음악을 업로드, 스트리밍, 공유하고 발견할 수 있는 소셜 음악 플랫폼입니다.

## 프로젝트 개요

**AI Music Gen**은 사용자들이 AI로 생성된 음악 트랙을 업로드하고, 스트리밍하며, 공유하고, 발견할 수 있는 종합적인 음악 소셜 플랫폼입니다.

### 기술 스택

**Backend** (`team_2_music_back/`)
- FastAPI 0.122.0 with Uvicorn
- SQLAlchemy 2.1.2 (ORM)
- Alembic 1.14.1 (Database Migrations)
- PostgreSQL/SQLite (Database)
- Redis 6.1.0 (Caching - optional in dev)
- AWS S3 (File Storage with Presigned URLs)
- JWT RS256 Authentication (with external Auth Server)
- Python 3.10+

**Frontend** (`team_2_music_front/`)
- Static HTML5
- Tailwind CSS v3 (CDN)
- Material Symbols Icons
- Responsive Design (Mobile-first)

## 백엔드 API 구현 현황

### ✅ 구현 완료된 모듈 (8개)

#### 1. User Profile API (4 endpoints)
사용자 프로필 관리 시스템
- `GET /api/v1/users/me` - 현재 사용자 프로필 조회
- `PATCH /api/v1/users/me` - 프로필 업데이트
- `GET /api/v1/users/{user_id}` - 특정 사용자 조회
- `POST /api/v1/users/` - 신규 사용자 생성

**주요 기능:**
- 사용자 프로필 정보 관리 (username, email, display_name, bio, avatar_url)
- 소셜 통계 자동 업데이트 (follower_count, following_count, track_count)

---

#### 2. Track API (6 endpoints)
음악 트랙 업로드 및 관리 시스템
- `GET /api/v1/tracks/` - 트랙 목록 조회 (페이지네이션)
- `GET /api/v1/tracks/{track_id}` - 트랙 상세 조회
- `POST /api/v1/tracks/upload/initiate` - 업로드 시작 (Presigned URL 생성)
- `POST /api/v1/tracks/upload/finalize` - 업로드 완료 (DB 기록)
- `PATCH /api/v1/tracks/{track_id}` - 트랙 정보 수정
- `DELETE /api/v1/tracks/{track_id}` - 트랙 소프트 삭제

**주요 기능:**
- 3-Stage Upload Flow (Initiate → S3 Direct Upload → Finalize)
- S3 Presigned URL을 통한 직접 업로드
- 자동 메타데이터 관리 (play_count, like_count, comment_count, trending_score)
- 트랙 상태 관리 (PROCESSING, READY, FAILED)

---

#### 3. Follow System API (5 endpoints)
팔로우/팔로잉 소셜 네트워크 시스템
- `POST /api/v1/users/{user_id}/follow` - 사용자 팔로우
- `DELETE /api/v1/users/{user_id}/follow` - 언팔로우
- `GET /api/v1/users/{user_id}/followers` - 팔로워 목록
- `GET /api/v1/users/{user_id}/following` - 팔로잉 목록
- `GET /api/v1/users/{user_id}/follow/status` - 팔로우 상태 확인

**주요 기능:**
- 양방향 팔로우 관계 관리
- follower_count/following_count 자동 증감
- 중복 팔로우 방지
- 페이지네이션 지원

---

#### 4. Interaction API (7 endpoints)
좋아요 및 댓글 상호작용 시스템
- `POST /api/v1/tracks/{track_id}/like` - 좋아요 추가
- `DELETE /api/v1/tracks/{track_id}/like` - 좋아요 취소
- `GET /api/v1/tracks/{track_id}/likes` - 좋아요 목록
- `POST /api/v1/tracks/{track_id}/comments` - 댓글 작성
- `GET /api/v1/tracks/{track_id}/comments` - 댓글 목록
- `PATCH /api/v1/tracks/comments/{comment_id}` - 댓글 수정
- `DELETE /api/v1/tracks/comments/{comment_id}` - 댓글 삭제

**주요 기능:**
- like_count, comment_count 자동 증감
- 중복 좋아요 방지
- 댓글 작성자 정보 포함
- 계층형 댓글 지원 (parent_id)

---

#### 5. Playlist API (8 endpoints)
플레이리스트 생성 및 관리 시스템
- `POST /api/v1/playlists/` - 플레이리스트 생성
- `GET /api/v1/playlists/{playlist_id}` - 플레이리스트 상세 (트랙 포함)
- `GET /api/v1/playlists/user/{user_id}` - 사용자 플레이리스트 목록
- `PATCH /api/v1/playlists/{playlist_id}` - 플레이리스트 수정
- `DELETE /api/v1/playlists/{playlist_id}` - 플레이리스트 삭제
- `POST /api/v1/playlists/{playlist_id}/tracks/{track_id}` - 트랙 추가
- `DELETE /api/v1/playlists/{playlist_id}/tracks/{track_id}` - 트랙 제거
- `GET /api/v1/playlists/{playlist_id}/tracks` - 플레이리스트 트랙 목록

**주요 기능:**
- 공개/비공개 플레이리스트
- track_count 자동 관리
- 트랙 순서 관리 (position)
- 소유자 권한 검증

---

#### 6. Tag/Search/Discovery API (14 endpoints)
태그 기반 검색 및 발견 시스템

**Tag Management:**
- `GET /api/v1/tags/` - 태그 목록
- `GET /api/v1/tags/{tag_id}` - 태그 상세
- `POST /api/v1/tags/` - 태그 생성
- `PATCH /api/v1/tags/{tag_id}` - 태그 수정
- `DELETE /api/v1/tags/{tag_id}` - 태그 삭제

**Track-Tag Management:**
- `POST /api/v1/tracks/{track_id}/tags` - 트랙에 태그 추가
- `DELETE /api/v1/tracks/{track_id}/tags/{tag_id}` - 트랙에서 태그 제거
- `GET /api/v1/tracks/{track_id}/tags` - 트랙의 태그 조회

**Search & Discovery:**
- `GET /api/v1/search/tracks` - 고급 검색 (텍스트, 태그, 필터)
- `GET /api/v1/discover/trending` - 트렌딩 트랙
- `GET /api/v1/discover/by-tag/{tag_name}` - 태그별 트랙 발견

**주요 기능:**
- 태그 카테고리 분류 (genre, mood, instrument 등)
- usage_count 자동 증감
- 다중 필터 검색 (태그, 카테고리, duration, BPM, 공개여부)
- 트렌딩 기간별 필터링 (day, week, month, all_time)
- 정렬 및 페이지네이션

---

#### 7. Play History Tracking API (5 endpoints)
재생 기록 추적 및 통계 시스템
- `POST /api/v1/play-history` - 재생 이벤트 기록
- `GET /api/v1/play-history/me` - 사용자 재생 기록
- `GET /api/v1/play-history/recently-played` - 최근 재생 트랙
- `GET /api/v1/play-history/stats/me` - 사용자 재생 통계
- `GET /api/v1/tracks/{track_id}/play-stats` - 트랙 재생 통계

**주요 기능:**
- play_count 자동 증가
- trending_score 자동 계산 (play_count * 0.5 + like_count * 1.5)
- 재생 시간 및 완료 여부 추적
- 고유 리스너 수 계산
- 평균 완료율 통계

---

#### 8. Notification System API (6 endpoints)
사용자 알림 관리 시스템
- `GET /api/v1/notifications/me` - 사용자 알림 목록
- `GET /api/v1/notifications/{notification_id}` - 특정 알림 조회
- `POST /api/v1/notifications/` - 알림 생성
- `PATCH /api/v1/notifications/mark-read` - 읽음 표시
- `DELETE /api/v1/notifications/{notification_id}` - 알림 삭제
- `GET /api/v1/notifications/stats/me` - 알림 통계

**주요 기능:**
- 다양한 알림 타입 (like, comment, follow, track_upload 등)
- Actor 정보 자동 조회 (username, display_name, avatar_url)
- 읽음/안읽음 상태 관리
- 타입별/읽음별 필터링
- 선택적/전체 읽음 표시

---

### 📊 구현 통계

- **총 API 엔드포인트**: 62개
- **데이터베이스 테이블**: 12개
  - user_profiles
  - tracks
  - likes
  - comments
  - follows
  - playlists
  - playlist_tracks
  - tags
  - track_tags
  - play_history
  - notifications
- **Pydantic 스키마**: 50+ 개
- **주요 기능**:
  - ✅ 3-Stage S3 Upload Flow
  - ✅ Soft Delete Pattern
  - ✅ Auto-increment Counts (denormalized)
  - ✅ Pagination (page, page_size, has_more)
  - ✅ Advanced Filtering & Search
  - ✅ Real-time Statistics

---

## ⏳ 남은 백엔드 기능

### 1. Recommendation System (추천 시스템)
사용자 기반 및 콘텐츠 기반 음악 추천
- 재생 기록 기반 추천
- 팔로우한 아티스트의 신곡 추천
- 유사 태그/장르 기반 추천
- 인기 트랙 추천

### 2. Admin Moderation (관리자 모더레이션)
콘텐츠 관리 및 모더레이션 도구
- 트랙 승인/거부
- 사용자 정지/차단
- 신고 관리
- 통계 대시보드

---

## 프로젝트 구조

```
team_2_music_back/
├── alembic/                    # Database migrations
├── app/
│   ├── core/                   # Core configuration
│   │   ├── config.py          # Settings
│   │   ├── database.py        # Database connection
│   │   └── redis.py           # Redis connection
│   ├── models/                 # SQLAlchemy models
│   │   ├── user.py
│   │   ├── track.py
│   │   ├── interaction.py     # Like, Comment
│   │   ├── follow.py
│   │   ├── playlist.py
│   │   ├── tag.py
│   │   ├── history.py         # PlayHistory
│   │   └── notification.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── user.py
│   │   ├── track.py
│   │   ├── interaction.py
│   │   ├── follow.py
│   │   ├── playlist.py
│   │   ├── tag.py
│   │   ├── history.py
│   │   └── notification.py
│   └── routes/                 # API endpoints
│       ├── users.py
│       ├── tracks.py
│       ├── follows.py
│       ├── interactions.py
│       ├── playlists.py
│       ├── tags.py
│       ├── history.py
│       └── notifications.py
├── main.py                     # FastAPI application
├── requirements.txt            # Python dependencies
└── .env                        # Environment variables

team_2_music_front/
└── stitch_/                    # Static HTML pages
    ├── 홈페이지/탐색/code.html
    ├── 음악_상세_페이지/code.html
    ├── 음악_업로드/code.html
    └── 내_음악/프로필/code.html
```

---

## 시작하기

### 사전 요구사항

- Python 3.10+
- PostgreSQL (또는 SQLite for dev)
- Redis (optional in development)

### 설치 및 실행

1. **의존성 설치**
   ```bash
   cd team_2_music_back
   pip install -r requirements.txt
   ```

2. **환경 변수 설정**
   ```bash
   cp .env.example .env
   # .env 파일 편집
   ```

3. **데이터베이스 마이그레이션**
   ```bash
   alembic upgrade head
   ```

4. **개발 서버 실행**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **API 문서 확인**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   - Health Check: http://localhost:8000/health

### 프론트엔드 실행

```bash
cd team_2_music_front/stitch_
python -m http.server 8080
```

브라우저에서 http://localhost:8080 접속

---

## API 문서

### 인증 (TODO)

현재는 JWT 인증이 TODO 상태로, 모든 엔드포인트는 첫 번째 사용자로 동작합니다.

향후 구현 예정:
- JWT RS256 토큰 검증
- Authorization: Bearer <token> 헤더
- 외부 Auth Server와 연동

### 주요 API 플로우

#### 1. 음악 업로드 플로우

```
1. POST /api/v1/tracks/upload/initiate
   → { upload_id, presigned_url, s3_key }

2. PUT to presigned_url (S3 직접 업로드)
   → 파일 업로드

3. POST /api/v1/tracks/upload/finalize
   → 트랙 메타데이터 저장
```

#### 2. 재생 플로우

```
1. GET /api/v1/tracks/{track_id}
   → 트랙 정보 및 스트리밍 URL

2. POST /api/v1/play-history
   → 재생 이벤트 기록
   → play_count 자동 증가
   → trending_score 자동 업데이트
```

#### 3. 소셜 인터랙션 플로우

```
1. POST /api/v1/tracks/{track_id}/like
   → like_count 자동 증가

2. POST /api/v1/tracks/{track_id}/comments
   → comment_count 자동 증가

3. POST /api/v1/users/{user_id}/follow
   → follower_count/following_count 자동 증가

→ Notification 자동 생성 (향후 구현)
```

---

## 데이터베이스 스키마

### 주요 테이블 관계

```
UserProfile (1) ──< (N) Track
UserProfile (1) ──< (N) Playlist
UserProfile (N) ──< (N) Follow (self-referential)

Track (1) ──< (N) Like
Track (1) ──< (N) Comment
Track (1) ──< (N) PlayHistory
Track (N) ──< (N) Tag (via TrackTag)

Playlist (N) ──< (N) Track (via PlaylistTrack)

Notification (N) ─> (1) UserProfile (actor)
Notification (N) ─> (1) UserProfile (recipient)
```

### 인덱스 최적화

모든 리스트 쿼리는 다음 필드에 인덱스 적용:
- `created_at` (DESC 정렬용)
- `is_active` (소프트 삭제 필터링)
- Foreign Keys (조인 성능)
- `is_read` (Notification 필터링)
- `played_at` (PlayHistory 정렬)

---

## 기술적 특징

### 1. Soft Delete Pattern
모든 리소스는 물리적 삭제 대신 `is_active = False`로 표시

### 2. Denormalized Counts
성능 최적화를 위한 카운트 비정규화:
- `follower_count`, `following_count`, `track_count` (UserProfile)
- `play_count`, `like_count`, `comment_count` (Track)
- `usage_count` (Tag)
- `track_count` (Playlist)

### 3. Presigned URL Pattern
대용량 파일은 백엔드를 거치지 않고 S3 직접 업로드

### 4. Pagination Pattern
모든 리스트 API는 일관된 페이지네이션:
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "has_more": true
}
```

### 5. Auto-increment Pattern
관련 리소스 생성/삭제 시 카운트 자동 증감

---

## 테스트

### 수동 테스트 (완료)

모든 엔드포인트는 curl을 통해 수동 테스트 완료:
- ✅ User Profile API
- ✅ Track API (3-stage upload)
- ✅ Follow System
- ✅ Interactions (Like/Comment)
- ✅ Playlist Management
- ✅ Tag/Search/Discovery
- ✅ Play History
- ✅ Notifications

### 자동화 테스트 (TODO)

```bash
pytest tests/
```

---

## 배포 (TODO)

### 인프라

- AWS EC2 (Backend)
- AWS RDS (PostgreSQL)
- AWS S3 (File Storage)
- AWS CloudFront (CDN)
- Nginx (Reverse Proxy)
- GitHub Actions (CI/CD)

---

## 개발 가이드

### 새 엔드포인트 추가

1. **모델 정의** (`app/models/`)
2. **스키마 정의** (`app/schemas/`)
3. **라우트 구현** (`app/routes/`)
4. **라우터 등록** (`main.py`)
5. **마이그레이션 생성** (`alembic revision --autogenerate`)
6. **테스트** (curl 또는 pytest)

### 코드 스타일

- Black formatter
- isort for imports
- Type hints 사용
- Docstrings (Google style)

---

## 참고 문서

- [CLAUDE.md](CLAUDE.md) - Claude Code 작업 가이드
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

## 라이선스

MIT License

---

## 기여자

Team 2 - Like Lion Python Course

---

**Last Updated**: 2025-11-27

**API Version**: v1

**Status**: 🚧 In Development - Core Features Complete, Recommendation System and Admin Moderation Pending
