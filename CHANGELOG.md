# Changelog

이 프로젝트의 사용자 가시 변경 사항을 기록합니다. 형식은
[Keep a Changelog](https://keepachangelog.com/ko/1.0.0/)를 따릅니다.

## [Unreleased]

### Added

- `afetch_openapi_info()`, `afetch_observatory_list()`, `afetch_beach_observatories()`,
  `aenrich_observatory_addresses()`를 추가했습니다. KHOA 포털 관측소 목록 조회와 VWorld
  주소 보강을 `httpx.AsyncClient`/`AsyncVworldClient` 기반으로 완전히 비동기 실행할 수
  있습니다.

### Fixed

- `abeach_index()`, `asurfing_index()` 등 `a` 접두 typed helper에서 `include_address=True`와
  live VWorld 옵션을 함께 쓰면 동기 주소 보강 호출이 코루틴 안에서 그대로 실행되어
  호출자의 이벤트 루프를 막던 문제를 수정했습니다. 이제 `AsyncVworldClient`처럼 실제
  async 클라이언트를 `vworld_client`로 넘겨도 정상 동작합니다.
- `vworld_client`를 넘기지 않고 `python-vworld-api`가 `AsyncVworldClient`를 제공하지
  않는 구버전일 때, 불명확한 `AttributeError` 대신 안내 메시지가 있는
  `KhoaRequestError`를 던지도록 수정했습니다.

### Changed

- 문서 구조를 저장소 간 컨벤션(kor-travel-geo 기준)에 맞춰 정리했습니다.
  README에 배지, "제공 표면"/"먼저 읽을 문서" 표, 데이터·외부 API 출처, 디렉터리
  개요, 법적 고지를 추가하고, `AGENTS.md`에 다섯 개 표준 헤더(Think Before Coding /
  Simplicity First / Surgical Changes / Goal-Driven Execution / Practical Bias)와
  식별자 표를 추가했습니다. `CLAUDE.md`는 정본 문서로의 짧은 포인터로 정리했습니다.
- `docs/decisions.md`를 신설해 기존에 `CLAUDE.md`에 비공식으로만 남아 있던 구조적
  결정(문서 한글화, replay 기반 단위 테스트, `items.item` 정규화, 선행 0 식별자 보존,
  HTTPS-only 전송)을 정식 ADR로 승격했습니다.

### Added

- `LICENSE`(GPL-3.0-or-later 전문)를 추가했습니다.
