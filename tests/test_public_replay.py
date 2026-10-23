"""선택한 해수욕장의 원문 행을 공개 API로 다시 해석한다."""

from copy import deepcopy
from datetime import date

import pytest

from khoa import Observatory, parse_beach_index_place
from tests.conftest import FakeResponse, khoa_payload


@pytest.mark.asyncio
async def test_replay_matches_http_place_and_preserves_rows_without_request(fake_client_factory):
    rows = [{
        "bbchNm": "대천해수욕장", "lat": 36.31, "lot": 126.513,
        "predcYmd": "2026-10-23", "predcNoonSeCd": slot,
        "maxWvhgt": "0.7", "avgArtmp": "17.2", "providerExtra": "original",
    } for slot in ("오전", "오후")]
    before = deepcopy(rows)
    client, session = fake_client_factory(FakeResponse(khoa_payload(rows)))
    original = (await client.abeach_index(num_of_rows=2)).items[0]
    anchor = Observatory(
        id=original.id, name=original.name,
        latitude=original.latitude, longitude=original.longitude,
    )
    count = len(session.calls)
    replay = parse_beach_index_place(anchor, rows)
    assert replay == original and replay.raw == {"rows": before} and rows == before
    assert replay.forecasts[0].predicted_on == date(2026, 10, 23)
    assert [item.forecast_period for item in replay.forecasts] == ["오전", "오후"]
    assert len(session.calls) == count


def test_caller_context_and_existing_missing_date_semantics_are_preserved():
    anchor = Observatory(
        id="001", name="선택한 장소", latitude=36.31, longitude=126.513,
        legal_dong_code="0012345678", road_address="원문 도로 주소", zipcode="00123",
    )
    rows = [{"predcYmd": "bad-date", "predcNoonSeCd": "오전", "avgArtmp": "-"}]
    replay = parse_beach_index_place(anchor, rows)
    assert replay.id == "001" and replay.name == anchor.name
    assert replay.legal_dong_code == "0012345678" and replay.zipcode == "00123"
    assert replay.road_address == anchor.road_address
    assert replay.forecasts[0].predicted_on is None
    assert replay.forecasts[0].average_air_temperature_c is None
    assert parse_beach_index_place(anchor, []).forecasts == ()
