# BeachIndexPlace 원문 재해석

```python
from khoa import Observatory, parse_beach_index_place

anchor = Observatory(id="001", name="선택한 해수욕장", latitude=36.31, longitude=126.513)
place = parse_beach_index_place(anchor, saved_rows)
```

입력은 `observatory: Observatory`와 같은 장소의 `rows: list[RawRecord]`다.
호출자가 선택한 장소의 식별자·이름·좌표·주소를 그대로 사용하고 forecasts와raw.rows는
기존BeachIndexForecast.from_raw 변환으로 만든다. 함수는 행을 장소별로 다시 묶거나
각 행이 선택한anchor와 일치하는지 확인하지 않는다. 호출자가 그 일치를 먼저 검증한다.
유효하지 않은 날짜의None 처리와 기존 숫자 변환의 예외 의미를 유지한다.

## 원문 재해석의 신뢰 경계

이 API는 이미 확보한 provider record를 같은 SDK DTO로 다시 해석하는 로컬 함수다.
네트워크·인증키·현재 시각·원천 재조회 없이 기존 파서와 같은 변환을 사용한다.
HTTP header/resultCode, 전체 items 형태·byte/count 상한, 전국 집합의 완결성·신선도는
이 단일 행/장소만으로 검증하지 않는다. 호출자는 원문 확보 때의 응답 검증·출처·수집 시각과
대상 identity를 따로 보존해야 하며, 빈 결과를 전국 정상0건의 근거로 사용하면 안 된다.
