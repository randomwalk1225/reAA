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

## 현재 배포 설정: Dockerfile

Nixpacks + uv 조합 실패로 Dockerfile 사용

```dockerfile
FROM python:3.12-slim
WORKDIR /app
RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY . .
CMD uv run python manage.py migrate && uv run gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000}
```

**장점:**
- 빌드/런타임 환경 동일
- 디버깅 용이
- uv sync + uv run 정상 동작

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

### 2024-12-20: Nixpacks + uv 조합 배포 실패 분석

**문제 요약:**
Railway Nixpacks 환경에서 uv로 패키지 설치 시, 빌드는 성공하나 런타임에서 `ModuleNotFoundError: No module named 'django'` 발생

**시도한 방법들:**

| # | 방법 | 결과 | 실패 원인 |
|---|------|------|----------|
| 1 | `uv sync` + `uv run python` | ❌ | .venv 경로를 런타임에서 못 찾음 |
| 2 | `uv pip install --system` | ❌ | Nix 파일시스템 읽기 전용 |
| 3 | `uv venv /app/.venv` + `/app/.venv/bin/python` | ❌ | venv가 런타임에 없음 |
| 4 | `VIRTUAL_ENV=/app/.venv uv pip install` | ❌ | 동일 |
| 5 | `uv pip install --target /app/vendor` + `PYTHONPATH` | ❌ | vendor 폴더가 런타임에 없음 |

**근본 원인 추정:**
1. Nixpacks 빌드 phase와 런타임 phase의 파일시스템 상태가 다름
2. 빌드 시 작업 디렉토리가 `/app`이 아닐 수 있음
3. Docker 레이어 캐싱 문제로 설치된 파일이 최종 이미지에 포함 안 됨

**해결책:**
- Nixpacks 포기 → Dockerfile 직접 작성
- Dockerfile은 빌드/런타임이 동일 이미지에서 실행되어 문제 없음

**교훈:**
1. Nixpacks는 자동화가 편하지만 디버깅이 어려움
2. uv + Nixpacks 조합은 검증되지 않은 조합
3. 문제 발생 시 Build Logs를 먼저 분석해야 함
4. 여러 방법 시도 전에 원인 파악이 우선

---

### 2024-12-20: externally managed environment 에러

**증상:**
```
error: The interpreter at /nix/store/...python3-3.12.7 is externally managed
This command has been disabled as it tries to modify the immutable `/nix/store` filesystem.
"uv pip install --system -r pyproject.toml" did not complete successfully: exit code: 2
```

**원인:**
- Nixpacks의 Python은 `/nix/store/`에 설치됨 (읽기 전용)
- `--system` 옵션은 시스템 Python에 직접 설치 시도
- Nix 파일시스템은 immutable이라 쓰기 불가

**해결:**
- 쓰기 가능한 `/app/` 경로에 가상환경 생성
- 명시적 경로로 실행

```toml
[phases.install]
cmds = ["uv venv /app/.venv && uv pip install -r pyproject.toml"]

[start]
cmd = "/app/.venv/bin/python manage.py migrate && /app/.venv/bin/gunicorn config.wsgi:application --bind 0.0.0.0:$PORT"
```

**핵심 교훈:**
- Nixpacks 환경에서 `--system` 설치 불가
- 반드시 쓰기 가능한 경로(`/app/`)에 venv 생성 필요

---

## uv 배포 핵심 원리

### Django import 에러가 나는 3가지 원인

1. **pyproject.toml에 Django 선언 누락**
   - uv는 `pyproject.toml`의 dependencies를 보고 설치
   - requirements.txt만 있고 pyproject.toml에 없으면 설치 안 됨

2. **uv sync가 안 돌아감**
   - Railway Nixpacks가 자동 빌드할 때 `pip install`로 가거나 설치 커맨드 누락
   - Build Command를 명시적으로 설정해야 함

3. **실행이 시스템 Python으로 돌아감**
   - `uv sync`는 `.venv/`에 설치
   - `python manage.py`는 시스템 Python 사용 → Django 못 찾음
   - `uv run python manage.py` 또는 `--system` 설치 필요

### 로컬 자가진단

```bash
# 프로젝트 루트에서 실행
uv sync
uv run python -c "import django; print(django.get_version())"
```

- 로컬 OK + 배포 실패 → 빌드에서 uv sync 안 돌고 있음
- 로컬도 실패 → pyproject.toml 확인 필요

### 해결 방법 (Nixpacks 환경)

**❌ 실패하는 방법들:**

1. `uv sync` + `uv run` → .venv 경로 문제
2. `uv pip install --system` → Nix 파일시스템 읽기 전용

**✅ 정답: /app/에 venv 생성 + 명시적 경로**
```toml
[phases.install]
cmds = ["uv venv /app/.venv && uv pip install -r pyproject.toml"]

[start]
cmd = "/app/.venv/bin/python manage.py migrate && /app/.venv/bin/gunicorn ..."
```

**핵심:**
- `/nix/store/`는 읽기 전용 → `--system` 불가
- `/app/`은 쓰기 가능 → 여기에 venv 생성
- 실행 시 `/app/.venv/bin/` 경로 명시

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

### 2025-12-20: railway.json이 Dockerfile을 무시함

**증상:**
```
ModuleNotFoundError: No module named 'django'
```
Dockerfile이 있는데도 동일한 에러 반복 발생

**원인:**
- `railway.json`에 `"builder": "NIXPACKS"` 명시적 설정
- Railway는 railway.json 설정을 최우선으로 사용
- Dockerfile이 있어도 NIXPACKS 빌더가 강제됨

**해결:**
```json
// railway.json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  }
}
```

**추가 조치:**
- `.dockerignore` 파일 생성 (로컬 .venv 복사 방지)

**핵심 교훈:**
1. railway.json 설정이 자동 감지보다 우선함
2. Dockerfile을 사용하려면 railway.json에 명시적으로 DOCKERFILE 빌더 지정
3. .dockerignore 없으면 로컬 파일이 빌드에 영향 줄 수 있음

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
