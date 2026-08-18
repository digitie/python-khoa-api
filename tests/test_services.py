from __future__ import annotations

import pytest

from khoa import DEFAULT_BASE_URL, SERVICE_DEFINITIONS, get_service


def test_catalog_contains_current_khoa_odmi_services():
    assert len(SERVICE_DEFINITIONS) == 46
    assert get_service("roms").operation == "GetRomsApiService"
    assert get_service("SV_AP_01_001").key == "roms"
    assert get_service("GetDTRecentApiService").key == "dt_recent"
    assert get_service("조위관측소 최신 관측데이터").key == "dt_recent"


def test_catalog_request_urls_use_https():
    assert DEFAULT_BASE_URL.startswith("https://")
    assert all(service.requested_url.startswith("https://") for service in SERVICE_DEFINITIONS)


def test_unknown_service_message_lists_known_keys():
    with pytest.raises(KeyError, match="unknown KHOA ODMI service"):
        get_service("missing")
