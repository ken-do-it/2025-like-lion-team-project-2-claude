# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AI Music Gen** - A music social sharing platform where users can upload, stream, share, and discover AI-generated music tracks. Built with FastAPI backend and static HTML/Tailwind CSS frontend.

## Tech Stack

**Backend** (team_2_music_back/):
- FastAPI with Uvicorn
- PostgreSQL database
- Redis for caching
- AWS S3 for file storage (presigned URLs)
- Celery for async tasks
- JWT (RS256) authentication with external Auth Server
- Docker & Docker Compose

**Frontend** (team_2_music_front/):
- Static HTML5 with Tailwind CSS v3 (CDN)
- Material Symbols Icons
- Responsive design with mobile-first approach
- No build process required

**Infrastructure**:
- AWS EC2, RDS, S3, CloudFront
- Nginx reverse proxy
- GitHub Actions for CI/CD

## Commands

### Backend Development

```bash
# Install dependencies (when requirements.txt is created)
pip install -r team_2_music_back/requirements.txt

# Run development server
cd team_2_music_back
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run with Docker Compose (when configured)
docker-compose up -d

# Database migrations (when using Alembic)
alembic upgrade head

# Run tests (when test suite is created)
pytest tests/
pytest tests/test_specific.py -v  # Single test file with verbose output
```

### Frontend Development

```bash
# Serve frontend locally (no build needed)
cd team_2_music_front/stitch_
python -m http.server 8080

# Or use any static file server
npx serve .
```

## Architecture

### Modular "Skills" Backend Design

The backend is organized into 12 independent domain modules (see team_2_music_back/.claude/skills/Music-Social-Sharing-Platform-process/SKILL.md for full specification):

1. **auth-jwt-verify** - JWT validation middleware (RS256 with public key from Auth Server)
2. **user-profile** - User profile management (GET/PATCH /api/v1/users/me)
3. **user-follow-system** - Follow/unfollow logic
4. **music-upload** - 3-stage presigned S3 upload flow (initiate → S3 direct upload → finalize)
5. **music-streaming-basic** - Track metadata and S3 presigned download URLs
6. **interaction-like-comment** - Likes and comments on tracks
7. **tag-search-discovery** - Search, filtering by tags/mood, trending
8. **recommendation-basic** - Basic recommendation engine
9. **playlist-management** - Playlist CRUD and track management
10. **play-history-tracking** - Play count tracking and history
11. **notification-system** - User notifications (likes, comments, follows)
12. **admin-moderation** - Content moderation tools

### Frontend Pages

Four main pages located in `team_2_music_front/stitch_/`:

1. **홈페이지/탐색/code.html** - Home/Explore page with trending, latest uploads, recommendations
2. **음악_상세_페이지/code.html** - Track detail page with player, comments, related tracks
3. **음악_업로드/code.html** - Music upload page with drag-and-drop interface
4. **내_음악/프로필/code.html** - Creator studio/profile with track management and statistics

### Key Architectural Patterns

**3-Stage Music Upload Flow:**
```
1. POST /api/v1/tracks/upload/initiate
   → Returns upload_id and presigned S3 URL
2. Client uploads directly to S3 (PUT to presigned URL)
3. POST /api/v1/tracks/upload/finalize
   → Creates Track record, triggers async processing (duration, BPM, waveform)
```

**JWT Authentication Flow:**
- External Auth Server issues access/refresh tokens
- Backend validates JWT signature using cached public key (Redis, 1hr TTL)
- All protected endpoints require `Authorization: Bearer <token>` header

**Caching Strategy (Redis):**
- JWKS public keys: 1 hour TTL
- Track metadata: 5 minutes TTL
- User profiles: 10 minutes TTL
- Trending feeds: 1 minute TTL
- Graceful degradation if Redis unavailable

**Database Schema:**
- `UserProfile` → owns many `Track`
- `Track` → has many `Like`, `Comment`, `PlayHistory`, `TrackTag`
- `Follow` → self-referential N:N between users (follower_id, following_id)
- `Playlist` → N:N with `Track` via `PlaylistTrack` junction table
- All list queries use indexes on created_at DESC for performance

## Project Status

- **Backend**: Architecture fully designed in SKILL.md, main.py is currently empty (implementation pending)
- **Frontend**: Four complete responsive HTML pages with Tailwind styling
- **Documentation**: Comprehensive specification in team_2_music_back/.claude/skills/Music-Social-Sharing-Platform-process/SKILL.md
- **Reference**: UI mockup images in team_2_music_back/reference/reference_images/

## Important Implementation Notes

### When implementing backend endpoints:

1. **Always validate JWT** - Use auth middleware on all protected routes
2. **Verify ownership** - Check user_id matches resource owner before allowing edits/deletes
3. **Use presigned URLs** - Never proxy large files through backend; generate S3 presigned URLs
4. **Return standard error format**:
   ```json
   {
     "error_code": "RESOURCE_NOT_FOUND",
     "message": "Human-readable message",
     "status_code": 404,
     "timestamp": "2024-11-25T12:00:00Z"
   }
   ```
5. **Apply rate limiting** - 60 requests/minute per user
6. **Enable CORS** - Only for approved frontend domains
7. **Use async processing** - Audio analysis (BPM, duration, waveform) via Celery
8. **Implement soft deletes** - Mark users/tracks as inactive rather than hard delete

### Frontend color scheme:
- Primary: `#8c2bee` (purple) or `#E02494` (pink)
- Dark background: `#191022` or `#121212`
- Use Material Symbols Outlined icons (48 variations)
- Fonts: Space Grotesk (headings), Noto Sans KR (Korean support)

### API Versioning:
- All endpoints use `/api/v1/` prefix
- Breaking changes require new version (`/api/v2/`)
- OpenAPI docs available at `/docs`

### Security Requirements:
- RS256 JWT only (no HS256)
- Private S3 buckets with presigned URL access only
- HTTPS enforced via Nginx
- No sensitive data in logs
- Security groups follow least privilege principle

## Reference Documentation

The most comprehensive architectural specification is located at:
`team_2_music_back/.claude/skills/Music-Social-Sharing-Platform-process/SKILL.md`

This document includes:
- Complete API endpoint specifications
- Database schema with indexes
- Error handling patterns
- Security checklist
- Development phases (1-5)
- Deployment architecture diagrams

Always consult SKILL.md when implementing new features or endpoints.
