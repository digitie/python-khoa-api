# CLAUDE.md — 프로젝트 컨텍스트

이 파일은 각 AI 에이전트 세션 시작 시 자동으로 탐색되어 컨텍스트 연속성을 보장한다.
프로젝트 규칙은 `AGENTS.md`에, 테스트 규칙은 `docs/testing.md`에 있으며, 이 파일은 **현재 개발 상황**과 **세션 간 동기화**에 집중한다.

## 프로젝트 현황 (2026-05-31)

국립해양조사원 KHOA 바다누리 ODMI OpenAPI의 비공식 Python 클라이언트. 패키지 이름은 `python-khoa-api`, import 패키지 이름은 `khoa`이다. data.go.kr을 통해 제공되는 KHOA ODMI 국가중점 OpenAPI를 호출하는 범용 호출 `KhoaClient.fetch()`와 안정된 Pydantic 모델 DTO, 지수별 helper들을 제공한다. 모든 문서는 한글로 작성된다 (AGENTS.md 문서 언어 정책).

### 현재 작업

- 각 에이전트 전용 Git Worktree (`python-khoa-api-*` prefix) 개설 및 CodeGraph 초기화 완료.
- 각 에이전트의 MCP `codegraph` `cwd` 설정을 개별 워크트리 경로로 자동 갱신 완료.

### 잔존 기술 부채

- (없음 — 신규 부채나 특이사항이 발견되면 `docs/repeated-mistakes.md`나 이슈/태스크 관리를 통해 정리한다.)

## 에이전트 worktree + CodeGraph

각 AI 에이전트(Codex, Claude Code, Antigravity 2.0)는 개별 Git Worktree 환경에서 독립적으로 작업한다. ChatGPT Codex는 `F:\dev\python-khoa-api-codex`, Claude Code는 `F:\dev\python-khoa-api-claude`, Google Antigravity는 `F:\dev\python-khoa-api-antigravity`를 사용한다. MCP 설정은 프로젝트 루트의 JSON 파일 및 `.gemini`, `.claude`, `.codex` 폴더 안에서 개별적으로 관리되며, 각 워크트리를 가리키도록 설정되어 있다. CodeGraph 색인은 worktree마다 1회 `codegraph init` 후 `codegraph sync`를 이용해 동기화 상태를 유지한다.

## 로컬 개발 환경

```
F:\dev\python-khoa-api\
├── src/                 # 소스 코드
│   └── khoa/
│       ├── client.py    # 사용자 API 진입점 및 typed helper
│       ├── models.py    # Pydantic 모델 DTO
│       ├── services.py  # OpenAPI 서비스 정의 카탈로그
│       ├── exceptions.py # 커스텀 예외 계층
│       ├── _http.py     # HTTP transport, retry, XML 오류 파싱
│       └── _convert.py  # 파라미터 변환 유틸리티
├── tests/               # pytest 테스트 수트
├── docs/                # OpenAPI 카탈로그, 테스트 안내, 디버그 가이드 등
└── pyproject.toml       # 패키징 설정 및 의존성, 툴링(ruff, mypy, pytest) 설정
```

Python 3.10+ 개발 환경. `pip install -e .[dev]` 후 `python -m pytest`로 실행.

## 빠른 검증 명령

PR을 요청하거나 main에 머지하기 전, 로컬 게이트웨이 품질 검증을 아래 명령어를 통해 반드시 확인한다.

```bash
# 코드 정적 컴파일 오류 검사
python -m compileall src/khoa tests

# 네트워크 없는 단위 테스트 실행
python -m pytest

# Ruff Lint 및 포맷 검사
python -m ruff check .

# MyPy 타입 체킹
python -m mypy src/khoa
```

실제 API 호출을 검증할 때는 승인된 서비스 키와 라이브 테스트 트리거 플래그를 넘겨 수행한다.
```bash
PYKHOA_RUN_LIVE=1 DATA_GO_KR_SERVICE_KEY=<approved service key> python -m pytest -m live
```

## 주요 결정 사항

1. **100% 한글 문서 정책**: 저장소 안의 모든 Markdown/RST 문서 및 내부 docstring은 한글로 작성함을 우선한다 (AGENTS.md 규칙).
2. **Replay 기반 단위 테스트**: 기본 테스트 환경에서는 실제 외부 포털이나 KHOA API를 호출하지 않고, 마스킹 처리된 오프라인 JSON fixture 데이터를 재현하여 검증한다.
3. **KHOA items.item 정규화**: KHOA의 response에서 `items.item`은 단일 객체(dict) 또는 리스트(list)로 들쭉날쭉할 수 있으므로, parser 단에서 항상 리스트로 정규화한다.
4. **선행 0 코드 및 식별자 보존**: 관측소 ID 등은 선행 0이 의미가 있으므로 `int`로 변환하지 않고 `str` 형태 그대로 유지한다.

## 작업 후 의무사항

1. `docs/repeated-mistakes.md` 파일에 이번 세션에서 겪었거나 회피한 실수 사례가 있다면 추가하여 기록을 보존한다.
2. `pyproject.toml`에 반영되지 않은 임시 패키지를 사용하지 않고, lock 상태를 유지한다.
3. PR 생성 전 `빠른 검증 명령`을 100% 로컬 통과 시킨다.
