"""khoa가 사용자에게 반환하는 Pydantic 응답 모델."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from ._convert import strip_or_none, to_datetime_or_none, to_float_or_none, to_int_or_none

T = TypeVar("T")
RawRecord = Mapping[str, Any]


class KhoaModel(BaseModel):
    """khoa 응답 모델의 공통 불변 기반 클래스."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class ResponseContext(KhoaModel):
    """인증키를 노출하지 않는 KHOA API 호출 메타데이터."""

    provider: str = "data.go.kr"
    service_key: str
    service_title: str
    service_path: str
    operation: str
    endpoint: str
    request_url: str
    request_params: dict[str, Any] = Field(default_factory=dict)
    collected_at: datetime


class AddressFields(KhoaModel):
    """주소 보강 결과를 외부 모델 없이 직접 보존하는 공통 필드."""

    legal_dong_code: str | None = None
    road_address_code: str | None = None
    road_name_code: str | None = None
    parcel_address: str | None = None
    road_address: str | None = None
    detail_address: str | None = None
    zipcode: str | None = None
    address_latitude: float | None = None
    address_longitude: float | None = None
    address_distance_m: float | None = None
    address_match_type: str | None = None
    address_source: str | None = None


class RequiredLocationFields(AddressFields):
    """필수 WGS84 좌표를 float 필드로 보존하는 공통 모델."""

    latitude: float
    longitude: float

    @property
    def lat(self) -> float:
        """KHOA 포털 원문 필드명에 맞춘 위도 별칭."""

        return self.latitude

    @property
    def lon(self) -> float:
        """KHOA 포털 원문 필드명에 맞춘 경도 별칭."""

        return self.longitude


class OptionalLocationFields(AddressFields):
    """선택 WGS84 좌표를 float 필드로 보존하는 공통 모델."""

    latitude: float | None = None
    longitude: float | None = None

    @property
    def lat(self) -> float | None:
        """KHOA 포털 원문 필드명에 맞춘 위도 별칭."""

        return self.latitude

    @property
    def lon(self) -> float | None:
        """KHOA 포털 원문 필드명에 맞춘 경도 별칭."""

        return self.longitude


class Observatory(RequiredLocationFields):
    """KHOA 포털 관측소/지점 목록의 한 항목."""

    id: str
    name: str
    data_type: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_raw(cls, row: Mapping[str, Any]) -> Observatory:
        """KHOA 포털 관측소 원문 행을 모델로 변환합니다."""

        latitude, longitude = _coordinates_from_row(row)
        if latitude is None or longitude is None:
            raise ValueError("KHOA observatory row requires lat/lon")

        address_latitude, address_longitude = _address_coordinates_from_row(row)

        return cls(
            id=str(row["id"]),
            name=str(row["name"]),
            data_type=strip_or_none(row.get("data_type")),
            latitude=latitude,
            longitude=longitude,
            legal_dong_code=_address_text(row, "legal_dong_code", "legalDongCode", "bjdCode"),
            road_address_code=_address_text(row, "road_address_code", "roadAddressCode"),
            road_name_code=_address_text(row, "road_name_code", "roadNameCode", "rnMgtSn"),
            parcel_address=_address_text(row, "parcel_address", "parcelAddress"),
            road_address=_address_text(row, "road_address", "roadAddress"),
            detail_address=_address_text(row, "detail_address", "detailAddress"),
            zipcode=_address_text(row, "zipcode", "zip_code", "zipCode", "postal_code"),
            address_latitude=address_latitude,
            address_longitude=address_longitude,
            address_distance_m=to_float_or_none(row.get("address_distance_m")),
            address_match_type=_row_text(row, "address_match_type", "addressMatchType"),
            address_source=_row_text(row, "address_source", "addressSource"),
            raw=dict(row),
        )


class BeachIndexForecast(KhoaModel):
    """해수욕지수의 예보 슬롯 한 건."""

    predicted_on: date | None = None
    forecast_period: str | None = None
    max_wave_height_m: float | None = None
    average_water_temperature_c: float | None = None
    average_air_temperature_c: float | None = None
    max_wind_speed_m_s: float | None = None
    open_status: str | None = None
    total_index: int | None = None
    raw: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_raw(cls, row: Mapping[str, Any]) -> BeachIndexForecast:
        """KHOA 해수욕지수 원문 행에서 예보 슬롯을 변환합니다."""

        return cls(
            predicted_on=_to_date_or_none(row.get("predcYmd")),
            forecast_period=strip_or_none(row.get("predcNoonSeCd")),
            max_wave_height_m=to_float_or_none(row.get("maxWvhgt")),
            average_water_temperature_c=to_float_or_none(row.get("avgWtem")),
            average_air_temperature_c=to_float_or_none(row.get("avgArtmp")),
            max_wind_speed_m_s=to_float_or_none(row.get("maxWspd")),
            open_status=strip_or_none(row.get("opnStat")),
            total_index=to_int_or_none(row.get("totalIndex")),
            raw=dict(row),
        )


class OceanBeachInfo(KhoaModel):
    """해양수산부 해수욕장정보 서비스의 해수욕장 장소 행."""

    num: str | None = None
    sido_name: str
    gugun_name: str | None = None
    name: str
    beach_width_m: float | None = None
    beach_length_m: float | None = None
    beach_kind: str | None = None
    link_url: str | None = None
    link_name: str | None = None
    image_url: str | None = None
    emergency_contact: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    raw: dict[str, Any] = Field(default_factory=dict)

    @property
    def source_key(self) -> str:
        """TripMate feature natural key로 쓰기 좋은 provider 내 안정 키."""

        return "|".join((self.sido_name, self.gugun_name or "", self.name))

    @property
    def lat(self) -> float | None:
        """위도 별칭."""

        return self.latitude

    @property
    def lon(self) -> float | None:
        """경도 별칭."""

        return self.longitude

    @classmethod
    def from_raw(cls, row: Mapping[str, Any]) -> OceanBeachInfo:
        """공공데이터포털 해수욕장정보 원문 행을 typed DTO로 변환합니다.

        live 응답(2026-06 실측)은 snake_case 키(``sido_nm``/``sta_nm``/
        ``beach_wid`` …)를 쓰므로 camelCase와 함께 둘 다 받습니다 (#5).
        """

        sido_name = _required_row_text(row, "sidoNm", "SIDO_NM", "sido_name", "sido_nm")
        name = _required_row_text(row, "staNm", "beachName", "name", "sta_nm")
        latitude = to_float_or_none(row.get("lat"))
        longitude = to_float_or_none(row.get("lon"))
        return cls(
            num=_row_text(row, "num"),
            sido_name=sido_name,
            gugun_name=_row_text(row, "gugunNm", "gugun_name", "gugun_nm"),
            name=name,
            beach_width_m=to_float_or_none(_row_value(row, "beachWid", "beach_wid")),
            beach_length_m=to_float_or_none(_row_value(row, "beachLen", "beach_len")),
            beach_kind=_row_text(row, "beachKnd", "beach_knd"),
            link_url=_row_text(row, "linkAddr", "link_addr"),
            link_name=_row_text(row, "linkNm", "link_nm"),
            image_url=_row_text(row, "beachImg", "beach_img"),
            emergency_contact=_row_text(row, "linkTel", "link_tel"),
            latitude=latitude,
            longitude=longitude,
            raw=dict(row),
        )


class BeachIndexPlace(RequiredLocationFields):
    """해수욕장 하나와 그 장소에 속한 해수욕지수 예보 묶음."""

    id: str
    name: str
    forecasts: tuple[BeachIndexForecast, ...]
    raw: dict[str, Any] = Field(default_factory=dict)


class BeachSearchObservation(KhoaModel):
    """KHOA 해수욕장 검색 API의 최신 관측 행."""

    tide: float | None = None
    water_temperature_c: float | None = None
    wind_speed_m_s: float | None = None
    wind_direction: str | None = None
    observed_at: datetime | None = None
    raw: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_raw(cls, row: Mapping[str, Any]) -> BeachSearchObservation:
        """해수욕장 검색 원문 관측 행을 변환합니다."""

        return cls(
            tide=to_float_or_none(row.get("tide")),
            water_temperature_c=to_float_or_none(row.get("water_temp")),
            wind_speed_m_s=to_float_or_none(row.get("wind_speed")),
            wind_direction=strip_or_none(row.get("wind_direct")),
            observed_at=to_datetime_or_none(row.get("obs_time")),
            raw=dict(row),
        )


class BeachSearchResult(OptionalLocationFields):
    """KHOA `beach/search.do` 응답 DTO."""

    id: str
    name: str
    obs_post_name: str | None = None
    observations: tuple[BeachSearchObservation, ...]
    raw: dict[str, Any] = Field(default_factory=dict)


class MarineIndexForecast(KhoaModel):
    """해양 레저 지수의 예보 슬롯 한 건."""

    predicted_on: date | None = None
    forecast_period: str | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    target_name: str | None = None
    weather: str | None = None
    total_index: int | None = None
    metrics: dict[str, Any] = Field(default_factory=dict)
    raw: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_raw(
        cls,
        row: Mapping[str, Any],
        *,
        excluded_keys: tuple[str, ...],
    ) -> MarineIndexForecast:
        """서로 다른 레저 지수 원문 행에서 공통 예보 슬롯을 변환합니다."""

        excluded = set(excluded_keys)
        excluded.update(
            {
                "lat",
                "lot",
                "lon",
                "latitude",
                "longitude",
                "predcYmd",
                "predcDt",
                "predcNoonSeCd",
                "splocBgngDt",
                "splocEndDt",
                "mdftExprnBgngTm",
                "mdftExprnEndTm",
                "seafsTgfshNm",
                "vslNm",
                "weather",
                "totalIndex",
            }
        )
        metrics = {key: value for key, value in row.items() if key not in excluded}
        return cls(
            predicted_on=_to_date_or_none(row.get("predcYmd")),
            forecast_period=strip_or_none(row.get("predcNoonSeCd")),
            starts_at=to_datetime_or_none(
                row.get("splocBgngDt") or row.get("mdftExprnBgngTm") or row.get("predcDt")
            ),
            ends_at=to_datetime_or_none(row.get("splocEndDt") or row.get("mdftExprnEndTm")),
            target_name=strip_or_none(row.get("seafsTgfshNm") or row.get("vslNm")),
            weather=strip_or_none(row.get("weather")),
            total_index=to_int_or_none(row.get("totalIndex")),
            metrics=metrics,
            raw=dict(row),
        )


class MarineIndexPlace(RequiredLocationFields):
    """해양 레저 지수 장소 하나와 그 장소의 예보 묶음."""

    service_key: str
    id: str
    name: str
    forecasts: tuple[MarineIndexForecast, ...]
    raw: dict[str, Any] = Field(default_factory=dict)


class Page(KhoaModel, Generic[T]):
    """KHOA 페이지네이션 응답의 한 페이지."""

    items: tuple[T, ...]
    total_count: int = 0
    page_no: int = 1
    num_of_rows: int = 10
    raw: dict[str, Any] = Field(default_factory=dict)
    context: ResponseContext | None = None

    @property
    def has_next_page(self) -> bool:
        return self.page_no * self.num_of_rows < self.total_count

    @property
    def next_page_no(self) -> int | None:
        return self.page_no + 1 if self.has_next_page else None

    @property
    def endpoint(self) -> str | None:
        return self.context.endpoint if self.context else None

    @property
    def request_params(self) -> dict[str, Any]:
        return dict(self.context.request_params) if self.context else {}


class RomsPrediction(KhoaModel):
    """ROMS 수치예측 엔드포인트의 typed 행 모델."""

    predicted_at: datetime | None = None
    latitude: float | None = None
    longitude: float | None = None
    current_direction_deg: float | None = None
    current_speed_cm_s: float | None = None
    water_temperature_c: float | None = None
    raw: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_raw(cls, row: Mapping[str, Any]) -> RomsPrediction:
        return cls(
            predicted_at=to_datetime_or_none(row.get("predcDt")),
            latitude=to_float_or_none(row.get("lat")),
            longitude=to_float_or_none(row.get("lot")),
            current_direction_deg=to_float_or_none(row.get("crdir")),
            current_speed_cm_s=to_float_or_none(row.get("crsp")),
            water_temperature_c=to_float_or_none(row.get("wtem")),
            raw=dict(row),
        )


def _coordinates_from_row(row: Mapping[str, Any]) -> tuple[float | None, float | None]:
    coordinate = _mapping_or_none(row.get("coordinate"))
    if coordinate is not None:
        latitude = to_float_or_none(_first_value(coordinate, "lat", "latitude"))
        longitude = to_float_or_none(_first_value(coordinate, "lon", "longitude", "lot"))
        if latitude is not None or longitude is not None:
            return latitude, longitude
    return (
        to_float_or_none(_first_value(row, "lat", "latitude")),
        to_float_or_none(_first_value(row, "lon", "longitude", "lot")),
    )


def _address_coordinates_from_row(row: Mapping[str, Any]) -> tuple[float | None, float | None]:
    coordinate = _mapping_or_none(row.get("address_coordinate"))
    if coordinate is not None:
        latitude = to_float_or_none(_first_value(coordinate, "lat", "latitude"))
        longitude = to_float_or_none(_first_value(coordinate, "lon", "longitude", "lot"))
        if latitude is not None or longitude is not None:
            return latitude, longitude
    return (
        to_float_or_none(_first_value(row, "address_latitude", "addressLatitude")),
        to_float_or_none(_first_value(row, "address_longitude", "addressLongitude")),
    )


def _address_text(row: Mapping[str, Any], *keys: str) -> str | None:
    value = _row_text(row, *keys)
    if value is not None:
        return value

    address = _mapping_or_none(row.get("address"))
    if address is None:
        return None

    jibun = _mapping_or_none(address.get("jibun"))
    road_name = _mapping_or_none(address.get("road_name"))
    for key in keys:
        value = _text_from_value(address.get(key))
        if value is not None:
            return value
        if jibun is not None:
            value = _text_from_value(jibun.get(key))
            if value is not None:
                return value
        if road_name is not None:
            value = _text_from_value(road_name.get(key))
            if value is not None:
                return value

    lookup: dict[str, tuple[tuple[Mapping[str, Any] | None, str], ...]] = {
        "legal_dong_code": ((jibun, "legal_dong_code"), (address, "legal_dong_code")),
        "road_address_code": ((road_name, "road_name_address_code"),),
        "road_name_code": ((road_name, "road_name_code"),),
        "parcel_address": ((jibun, "address"),),
        "road_address": ((road_name, "address"),),
        "detail_address": ((address, "detail_address"), (road_name, "building_name")),
        "zipcode": (
            (address, "effective_postal_code"),
            (address, "postal_code"),
            (jibun, "postal_code"),
            (road_name, "postal_code"),
        ),
    }
    for key in keys:
        for mapping, nested_key in lookup.get(key, ()):
            value = _text_from_value(mapping.get(nested_key) if mapping is not None else None)
            if value is not None:
                return value
    return None


def _first_value(row: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return value
    return None


def _mapping_or_none(value: Any) -> Mapping[str, Any] | None:
    return value if isinstance(value, Mapping) else None


def _text_from_value(value: Any) -> str | None:
    if isinstance(value, Mapping):
        value = value.get("code") or value.get("value")
    return strip_or_none(value)


def _row_text(row: Mapping[str, Any], *keys: str) -> str | None:
    for key in keys:
        text = strip_or_none(row.get(key))
        if text is not None:
            return text
    return None


def _row_value(row: Mapping[str, Any], *keys: str) -> Any:
    """첫 번째 non-None 값을 반환합니다 (숫자 등 비-텍스트 필드 키 fallback용)."""
    for key in keys:
        value = row.get(key)
        if value is not None:
            return value
    return None


def _required_row_text(row: Mapping[str, Any], *keys: str) -> str:
    text = _row_text(row, *keys)
    if text is None:
        joined = ", ".join(keys)
        raise ValueError(f"row requires one of: {joined}")
    return text


def _to_date_or_none(value: object) -> date | None:
    text = strip_or_none(value)
    if text is None:
        return None
    for fmt in ("%Y-%m-%d", "%Y%m%d"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None
