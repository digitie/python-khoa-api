"""async-only 세션과 재시도별 TPS 과금을 검증한다."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest

from khoa import AsyncTokenBucket, KhoaClient, afetch_observatory_list, afetch_openapi_info
from khoa._http import KhoaHttp

from .conftest import FakeResponse, khoa_payload
from .test_observatories import FakePortalResponse

pytestmark = pytest.mark.asyncio


async def test_sync_session_is_rejected_before_network_call():
    def get(*args, **kwargs):
        raise AssertionError("sync network must not run")

    with pytest.raises(TypeError, match="must be async"):
        KhoaClient("TEST_KEY", session=SimpleNamespace(get=get))


async def test_sync_portal_is_rejected_before_network_call():
    def post(*args, **kwargs):
        raise AssertionError("sync network must not run")

    with pytest.raises(TypeError, match="must be async"):
        await afetch_openapi_info(36, session=SimpleNamespace(post=post))


async def test_odmi_retry_charges_each_http_attempt(monkeypatch):
    session = SimpleNamespace(
        get=AsyncMock(
            side_effect=[
                FakeResponse({}, status_code=503),
                FakeResponse({"response": "ok"}),
            ]
        )
    )
    client = KhoaHttp("TEST_KEY", session=session, retries=1)
    acquire = AsyncMock(wraps=client._bucket.acquire)
    monkeypatch.setattr(client._bucket, "acquire", acquire)
    await client.aget_url("https://apis.data.go.kr/test", {}, endpoint="test")
    assert acquire.await_count == session.get.await_count == 2


async def test_portal_retry_and_followup_share_budget():
    bucket = AsyncTokenBucket()
    acquire = AsyncMock(wraps=bucket.acquire)
    bucket.acquire = acquire
    session = SimpleNamespace(
        post=AsyncMock(
            side_effect=[
                FakePortalResponse({}, status_code=503),
                FakePortalResponse({"observatoryList": []}),
                FakePortalResponse({"observatoryList": []}),
            ]
        )
    )
    assert await afetch_openapi_info(36, session=session, rate_limiter=bucket) == {
        "observatoryList": []
    }
    assert await afetch_observatory_list(session=session, rate_limiter=bucket) == ()
    assert acquire.await_count == session.post.await_count == 3


async def test_public_client_redirect_takes_another_token(monkeypatch):
    acquisitions = []

    async def handler(request):
        acquisitions.append(acquire.await_count)
        if len(acquisitions) == 1:
            return httpx.Response(302, headers={"location": "/final"})
        return httpx.Response(200, json=khoa_payload([]))

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler), follow_redirects=True
    ) as session:
        client = KhoaClient("TEST_KEY", session=session, max_rps=1000)
        acquire = AsyncMock(wraps=client._http._bucket.acquire)
        monkeypatch.setattr(client._http._bucket, "acquire", acquire)
        page = await client.afetch("vortex", num_of_rows=1)
        assert page.total_count == 0
    assert acquisitions == [1, 2]


async def test_portal_redirect_changes_post_to_get_and_takes_token(monkeypatch):
    acquisitions = []
    methods = []
    bucket = AsyncTokenBucket(1000)
    acquire = AsyncMock(wraps=bucket.acquire)
    monkeypatch.setattr(bucket, "acquire", acquire)

    async def handler(request):
        acquisitions.append(acquire.await_count)
        methods.append(request.method)
        if len(acquisitions) == 1:
            return httpx.Response(303, headers={"location": "/final"})
        return httpx.Response(200, json={"observatoryList": []})

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(handler), follow_redirects=True
    ) as session:
        assert await afetch_openapi_info(36, session=session, rate_limiter=bucket) == {
            "observatoryList": []
        }
    assert methods == ["POST", "GET"]
    assert acquisitions == [1, 2]
