# decisions.md — 의사결정 기록

이 문서는 이 프로젝트의 구조적 결정을 결정 시점 순서로 누적한다.
결정이 뒤집힐 때는 새 항목을 추가하고, 옛 항목은 지우지 않은 채
(supersedes: 위 항목)으로 표시한다.

## D-001: 모든 문서는 한글로 작성한다

- 상태: accepted
- 날짜: 2026-05-24

### 컨텍스트

Codex, Claude Code, Antigravity 등 여러 AI 에이전트가 같은 저장소를 오가며 작업한다.
문서 언어가 에이전트마다 섞이면 한국어 사용자·유지보수자가 읽기 어렵고, 검색과 리뷰도
일관성이 떨어진다.

### 결정

이 저장소의 모든 Markdown/RST 문서와 Python 내부 docstring(모듈·클래스·함수·메서드)은
한글로 작성한다. 공식 API 필드명, 코드 식별자, 명령어, URL, provider 원문처럼 그대로
보존해야 하는 값만 예외로 영어를 유지한다.

### 근거

이 라이브러리가 감싸는 KHOA ODMI OpenAPI 자체가 한국 정부 제공 API이고, 실사용자와
유지보수자도 한국어 기반이다. 코드 식별자까지 번역하면 KHOA/data.go.kr 원문 문서와
대조하기 어려워지므로 그 부분만 예외로 둔다.

### 결과

`AGENTS.md`의 "문서 언어 정책" 절, `docs/repeated-mistakes.md`의 관련 체크리스트로 반영됨.

---

## D-002: 기본 테스트는 저장된 fixture를 replay하며 네트워크를 호출하지 않는다

- 상태: accepted
- 날짜: 2026-05-24

### 컨텍스트

KHOA ODMI 서비스는 승인된 `DATA_GO_KR_SERVICE_KEY`가 있어야 호출할 수 있고, 서비스별로
활용신청/승인 상태가 다르다. CI나 다른 개발자 환경에서 매번 실 API를 호출하면 키 없이는
테스트가 아예 돌아가지 않고, 키가 있어도 승인되지 않은 서비스에서 403이 발생해 실패한다.

### 결정

`KhoaClient.debug_fetch()`로 만든 요청/응답을 `save_fixture()`로
`tests/fixtures/{function}/{case}.json`에 저장해 두고, `tests/test_generated_fixtures.py`가
이 fixture를 자동으로 읽어 parser/processor에 다시 넣는 replay 테스트로 기본 검증을
수행한다. 실 API 호출 테스트는 `PYKHOA_RUN_LIVE=1`과 `DATA_GO_KR_SERVICE_KEY`가 모두
있을 때만 `-m live`로 별도 실행한다.

### 근거

fixture 저장 전 `serviceKey`, `api_key`, `Authorization`, token 값은 `redact_sensitive()`로
자동 마스킹되므로 인증키 유출 위험 없이 실제 응답 구조를 재현할 수 있다. 네트워크 의존을
없애면 CI가 안정적으로 돌고, live test 실패(권한 미승인)와 로직 회귀를 구분할 수 있다.

### 결과

`docs/debug-fixtures.md`, `docs/testing.md`에 절차 문서화. `pyproject.toml`의
`pytest.ini_options.markers`에 `live` 마커 등록.

---

## D-003: KHOA 응답의 `items.item`은 항상 리스트로 정규화한다

- 상태: accepted
- 날짜: 2026-05-24

### 컨텍스트

KHOA/data.go.kr 응답은 결과 건수가 1건이면 `items.item`이 단일 object(dict)로, 2건
이상이면 list로 내려온다. 클라이언트가 이를 그대로 다루면 건수에 따라 파싱 코드가
갈라지거나, 단일 응답을 누락시키는 버그가 생긴다.

### 결정

`client.py`의 파서 경계(`response.body.items.item`을 다루는 지점)에서 dict/list 여부를
확인해 항상 튜플/리스트로 정규화한 뒤 상위 로직에 넘긴다. object도 list도 아니면
명시적으로 예외를 던진다(`"KHOA response.body.items.item was not an object or list"`,
`"data.go.kr response.body.items.item was not an object or list"`).

### 근거

파서 경계 한 곳에서만 정규화하면 이후의 모델 변환·typed helper·DTO 그룹핑 코드는
"list"라는 단일 계약만 신뢰하면 되어 건수 분기 버그를 구조적으로 막는다.

### 결과

`AGENTS.md`의 "반드시 지킬 것"·DO NOT 목록, `docs/repeated-mistakes.md`의
"응답 형태" 절에 반영됨.

---

## D-004: 선행 0이 있는 코드/식별자는 `int`로 변환하지 않는다

- 상태: accepted
- 날짜: 2026-05-24

### 컨텍스트

관측소 코드나 지수 코드(예: `BCH001`, `DT_0001`)는 선행 0이 의미를 가지는 식별자다.
숫자처럼 보인다고 `int()`로 캐스팅하면 선행 0이 사라져 원래 코드와 달라지고, KHOA
API에 다시 넘길 때 거부되거나 다른 대상을 가리키게 된다.

### 결정

선행 0이 의미 있는 코드와 관측소 식별자는 어떤 변환 단계에서도 `int`로 캐스팅하지
않고 문자열 그대로 유지한다.

### 근거

식별자는 값이 아니라 이름이다. 숫자로 캐스팅해서 얻는 이점(정렬, 산술 연산)이 전혀
없는 반면, 손실은 되돌릴 수 없다.

### 결과

`AGENTS.md` DO NOT 목록 4번, `docs/repeated-mistakes.md`에 반영. 관련 회귀 테스트를
`tests/`에 유지.

---

## D-005: 인증키가 포함된 요청은 항상 HTTPS로만 전송한다

- 상태: accepted
- 날짜: 2026-08-18

### 컨텍스트

`serviceKey`를 URL 쿼리 파라미터로 전달하는 data.go.kr 방식 특성상, HTTP로 요청하면
인증키가 평문으로 네트워크에 노출된다. data.go.kr 게이트웨이가 HTTP를 HTTPS로 항상
자동 리다이렉트한다고 가정할 수 없다(PR #8, `fix: serviceKey 요청 URL을 HTTPS로 전환`).

### 결정

`serviceKey`를 포함하는 data.go.kr 기본 게이트웨이 URL과 KHOA 직접 endpoint(해수욕장
검색, 관측소 목록) URL은 모두 `https://`로 하드코딩한다
(`services.py`의 `DEFAULT_BASE_URL`, `client.py`의 `KHOA_BEACH_SEARCH_URL`,
`observatories.py`의 `KHOA_OPENAPI_INFO_URL` 등).

### 근거

인증키 평문 노출은 되돌릴 수 없는 보안 사고로 이어질 수 있으므로, 게이트웨이의
리다이렉트 동작에 기대지 않고 클라이언트 쪽에서 프로토콜을 강제하는 편이 안전하다.

### 결과

회귀 테스트로 요청 URL이 `https://`로 시작하는지 검증한다. `docs/repeated-mistakes.md`
"API 키와 live test" 절에 반영.

---

## D-006: 관측소 목록/주소 보강 경로를 asyncio 기반으로 전환한다

- 상태: accepted
- 날짜: 2026-09-11

### 컨텍스트

`src/khoa/client.py`의 `afetch()`, `abeach_search()`, `aoceans_beach_info()`는
이미 `httpx.AsyncClient`로 완전히 비동기였지만, `src/khoa/observatories.py`의
`fetch_openapi_info()`(KHOA 포털 AJAX 호출)와 `enrich_observatory_addresses()`
(VWorld 역지오코딩 호출)는 `requests`와 동기 VWorld 클라이언트만 사용했다.
`abeach_index()`와 바다 지수류 typed helper(`asurfing_index()` 등)는
`include_address=True`와 live VWorld 옵션이 있을 때 이 동기 함수를 코루틴
안에서 그대로 호출했으므로, 자체 이벤트 루프를 가진 애플리케이션(FastAPI 등)에서
호출하면 그 루프 전체가 VWorld 응답을 기다리는 동안 멈췄다. 게다가 async
VWorld 클라이언트(`AsyncVworldClient`)를 `vworld_client`로 넘기면 코루틴
객체를 dict로 다루려다 그대로 실패했다.

### 결정

`observatories.py`에 `afetch_openapi_info()`, `afetch_observatory_list()`,
`afetch_beach_observatories()`, `aenrich_observatory_addresses()`를 추가해
포털 POST와 VWorld 역지오코딩 호출을 `httpx.AsyncClient`/`AsyncVworldClient`
기반으로 다시 구현했다. 기존 동기 함수는 얇은 `run_async()` 래퍼로 바꿔 단일
구현만 유지한다. `PortalSessionLike.post()`와 `VworldReverseGeocoderLike.
reverse_geocode_latlon()`은 `_http.py`의 `SessionLike.get()`과 같은 방식으로
반환값이 결과 또는 결과의 Awaitable일 수 있게 해, 기존 동기 fake session/client도
그대로 동작한다. `client.py`의 `abeach_index()`와 `a*_index()`(바다 지수류)는
더 이상 동기 주소 보강 함수를 코루틴에서 직접 호출하지 않고, 새 async 버전을
`await`하는 `_abeach_index_place_page()`/`_amarine_index_place_page()`를
사용한다.

### 근거

`_http.py`가 이미 검증한 "동기/async 겸용 프로토콜 + `run_async()` 위임" 패턴을
그대로 재사용하면 중복 구현 없이 동기 API 호환성을 깨지 않고 실제 논블로킹
async 경로를 만들 수 있다. `python-vworld-api`가 이미 `AsyncVworldClient`를
제공하므로 새 wrapper 없이 그 구현을 직접 사용한다(`AGENTS.md`의 구현 방향).

### 결과

`src/khoa/__init__.py`가 새 async 함수들을 내보내고, `README.md`에 async 사용
예시를 추가했다. `tests/test_observatories.py`, `tests/test_client.py`에
async fake portal session/VWorld client를 이용한 회귀 테스트를 추가했다.

### 알려진 제약

`_http.py`의 `run_async()`는 이미 실행 중인 이벤트 루프가 있으면 새 스레드에서
별도 `asyncio.run()`을 돌린다. 그 안에서 호출자가 이미 만들어 둔 `AsyncVworldClient`
(또는 다른 async 리소스)를 sync facade에 넘기면, 그 리소스가 원래 바인딩된 루프와
다른 루프에서 쓰이게 되어 "Future attached to a different loop"류의 오류가 날 수
있다. 반대로 동기 세션/클라이언트를 async facade(`afetch_*`, `a*_index`)에 넘기면
그 블로킹 호출이 코루틴 안에서 그대로 실행되어 호출자의 이벤트 루프를 막는다. 두
경우 모두 `README.md`에 "동기 facade에는 동기 객체를, async facade에는 async
객체를"이라는 경고로 문서화했다. 런타임 가드는 추가하지 않았다 — `_http.py`의
`SessionLike`도 동일한 계약을 가정할 뿐 강제하지 않으며, 이 프로젝트의 다른 어떤
경계에서도 이런 오용까지 감지하지는 않는다.
