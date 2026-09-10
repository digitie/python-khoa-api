from __future__ import annotations

import pytest

from khoa import KhoaAuthError, KhoaParseError, KhoaRequestError

from .conftest import FakeResponse, khoa_payload


@pytest.mark.asyncio
async def test_http_status_auth_error(fake_client_factory):
    client, _session = fake_client_factory(
        FakeResponse({}, status_code=401, text="Unauthorized TEST_KEY")
    )

    with pytest.raises(KhoaAuthError, match=r"\[redacted\]"):
        await client.afetch("vortex")


@pytest.mark.asyncio
async def test_non_json_xml_error_is_mapped(fake_client_factory):
    xml = """
    <OpenAPI_ServiceResponse>
      <cmmMsgHeader>
        <returnReasonCode>30</returnReasonCode>
        <returnAuthMsg>SERVICE_KEY_IS_NOT_REGISTERED_ERROR</returnAuthMsg>
      </cmmMsgHeader>
    </OpenAPI_ServiceResponse>
    """
    client, _session = fake_client_factory(FakeResponse(ValueError("bad json"), text=xml))

    with pytest.raises(KhoaAuthError):
        await client.afetch("vortex")


@pytest.mark.asyncio
async def test_bad_envelope_raises_parse_error(fake_client_factory):
    client, _session = fake_client_factory(FakeResponse({"oops": {}}))

    with pytest.raises(KhoaParseError):
        await client.afetch("vortex")


@pytest.mark.asyncio
async def test_result_code_request_error(fake_client_factory):
    client, _session = fake_client_factory(
        FakeResponse(khoa_payload(None, result_code="10", result_msg="bad"))
    )

    with pytest.raises(KhoaRequestError):
        await client.afetch("vortex")
