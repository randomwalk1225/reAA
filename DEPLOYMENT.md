# 배포 가이드 및 에러 기록

## 환경 정보
- **플랫폼**: Railway
- **패키지 관리**: uv (pyproject.toml + uv.lock)
- **Python**: 3.12
- **프레임워크**: Django 6.0

---

## 배포 전 체크리스트

- [ ] 로컬에서 `uv run python manage.py runserver` 정상 동작 확인
- [ ] 로컬에서 `uv run python manage.py check` 에러 없음
- [ ] 새 패키지 추가 시 `uv lock` 실행 확인
- [ ] `uv.lock` 파일 커밋 여부 확인
- [ ] 환경변수 필요 시 Railway 대시보드에 추가 확인

---

## 현재 nixpacks.toml 설정

```toml
[phases.setup]
nixPkgs = ["python312", "uv"]

[phases.install]
cmds = ["uv pip install --system -r pyproject.toml"]

[start]
cmd = "python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT"
```

---

## 에러 기록

### 2024-12-20: ModuleNotFoundError: No module named 'django'

**증상:**
```
Starting Container
Traceback (most recent call last):
  File "/app/manage.py", line 11, in main
    from django.core.management import execute_from_command_line
ModuleNotFoundError: No module named 'django'
```

**원인:**
- `uv sync --frozen`은 `.venv/` 디렉토리에 패키지 설치
- Railway의 build phase와 start phase가 다른 환경에서 실행
- start phase에서 `.venv/`를 찾지 못함

**시도한 방법들:**
1. ❌ `uv sync --frozen --no-dev` + `python manage.py ...`
   - 실패: .venv가 start phase에 없음
2. ❌ `uv sync --frozen --no-dev` + `uv run python manage.py ...`
   - 실패: uv run도 .venv를 찾지 못함
3. ✅ `uv pip install --system -r pyproject.toml` + `python manage.py ...`
   - 성공: 시스템 Python에 직접 설치

**해결:**
```toml
[phases.install]
cmds = ["uv pip install --system -r pyproject.toml"]

[start]
cmd = "python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT"
```

---

### 2024-12-20: ModuleNotFoundError: No module named 'jwt' / 'cryptography'

**증상:**
```
ModuleNotFoundError: No module named 'jwt'
ModuleNotFoundError: No module named 'cryptography'
```

**원인:**
- django-allauth가 PyJWT와 cryptography에 의존
- pyproject.toml에 명시적으로 추가되지 않음

**해결:**
```toml
# pyproject.toml dependencies에 추가
"PyJWT>=2.8",
"cryptography>=42.0",
```

---

### Nixpacks gcc/gfortran 충돌 (scipy 빌드)

**증상:**
```
error: multiple packages provide /nix/store/.../bin/gcc
collision between gcc and gfortran
```

**원인:**
- scipy를 소스에서 빌드할 때 gcc와 gfortran 충돌
- pip로 빌드하면 발생

**해결:**
- uv 사용 (wheel 패키지 우선 설치)
- nixpacks.toml로 uv 강제 사용

---

## Railway 환경변수 목록

| 변수명 | 설명 | 필수 |
|--------|------|------|
| `SECRET_KEY` | Django secret key | O |
| `DEBUG` | 디버그 모드 (False) | O |
| `DATABASE_URL` | PostgreSQL 연결 문자열 | O |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | - |
| `GOOGLE_CLIENT_SECRET` | Google OAuth secret | - |
| `GITHUB_CLIENT_ID` | GitHub OAuth client ID | - |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth secret | - |

---

## 유용한 명령어

```bash
# 로컬 테스트
uv run python manage.py runserver
uv run python manage.py check
uv run python manage.py migrate

# 패키지 관리
uv add <package>           # 패키지 추가
uv lock                    # lock 파일 갱신
uv sync                    # 의존성 동기화

# Git 배포
git add -A && git commit -m "message" && git push origin master
```

---

## 로그 확인 방법

1. Railway 대시보드 → Deployments → View logs
2. Build logs: 빌드 과정 확인
3. Deploy logs: 런타임 에러 확인

---

## 새 에러 기록 템플릿

```markdown
### YYYY-MM-DD: 에러 제목

**증상:**
\`\`\`
에러 메시지
\`\`\`

**원인:**
- 원인 설명

**해결:**
- 해결 방법
```
