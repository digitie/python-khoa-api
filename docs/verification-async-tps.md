# 비동기/TPS 전환 검증

- 독립 적대적 리뷰 2인: 구현 승인. 취소·FIFO·재시도·redirect 추가 송신과 인증 보존 확인.
- 오프라인: 69개 테스트 통과, Ruff/mypy/compileall 통과.
- live E2E: `vortex`, `roms` 모두 HTTP 403, `SERVICE_KEY_IS_NOT_REGISTERED_ERROR`
  (`returnReasonCode=30`). 실제 데이터 응답 검증은 완료하지 못했다.
- 2026-09-14 사용자가 두 API를 사용하지 않는다고 밝히고 위 오류를 제외한 머지를
  명시적으로 승인했다. 인증 실패를 테스트 성공으로 계산하지 않는다.
