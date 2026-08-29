# Changelog

이 프로젝트의 사용자 가시 변경 사항을 기록합니다. 형식은
[Keep a Changelog](https://keepachangelog.com/ko/1.0.0/)를 따릅니다.

## [Unreleased]

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
