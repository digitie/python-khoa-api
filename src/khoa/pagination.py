"""KhoaClient/AsyncKhoaClient가 공유하는 페이지 순회 헬퍼.

여기 담긴 함수들은 특정 서비스나 KhoaClient 내부 상태에 의존하지 않는
순수한 페이지네이션 로직만 다룬다. 실제 HTTP 호출은 KhoaClient의 fetch
계열 메서드가 콜백(`fetch_page`)으로 넘겨주고, 이 모듈은 "다음 페이지를
계속 가져올지"와 `max_pages`/`max_items` 안전 제한만 책임진다.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Callable, Iterable, Iterator
from typing import TypeVar

from .models import Page

T = TypeVar("T")


def validate_page_params(page_no: int, num_of_rows: int) -> None:
    """page_no/num_of_rows 값이 KHOA API가 허용하는 범위인지 검증합니다."""

    if page_no < 1:
        raise ValueError("page_no must be >= 1")
    if not 1 <= num_of_rows <= 1000:
        raise ValueError("num_of_rows must be between 1 and 1000")


def paginate(
    fetch_page: Callable[[int], Page[T]],
    *,
    start_page: int,
    max_pages: int | None,
    max_items: int | None,
) -> Iterator[Page[T]]:
    """`fetch_page(page_no)`가 반환하는 페이지를 안전 제한과 함께 순회합니다."""

    next_page = start_page
    pages = 0
    yielded = 0
    while True:
        page = fetch_page(next_page)
        if not page.items:
            return
        yield page
        pages += 1
        yielded += len(page.items)
        if max_pages is not None and pages >= max_pages:
            return
        if max_items is not None and yielded >= max_items:
            return
        if not page.has_next_page:
            return
        next_page += 1


async def apaginate(
    fetch_page: Callable[[int], Awaitable[Page[T]]],
    *,
    start_page: int,
    max_pages: int | None,
    max_items: int | None,
) -> AsyncIterator[Page[T]]:
    """`fetch_page(page_no)`가 반환하는 페이지를 비동기로, 안전 제한과 함께 순회합니다."""

    next_page = start_page
    pages = 0
    yielded = 0
    while True:
        page = await fetch_page(next_page)
        if not page.items:
            return
        yield page
        pages += 1
        yielded += len(page.items)
        if max_pages is not None and pages >= max_pages:
            return
        if max_items is not None and yielded >= max_items:
            return
        if not page.has_next_page:
            return
        next_page += 1


def paginate_many(
    fetch_page_batches: Iterable[Callable[[int], Page[T]]],
    *,
    start_page: int,
    max_pages: int | None,
    max_items: int | None,
) -> Iterator[Page[T]]:
    """`fetch_page_batches`의 콜백들을 순서대로 순회합니다.

    각 콜백은 (예: 시/도 하나에 대한) 페이지 순회 하나를 담당하며, 빈 페이지를
    만나거나 다음 페이지가 없으면 그 콜백은 멈추고 다음 콜백으로 넘어갑니다.
    `max_pages`/`max_items` 제한은 개별 콜백이 아니라 전체 배치에 걸쳐
    누적 적용됩니다.
    """

    pages = 0
    yielded = 0
    for fetch_page in fetch_page_batches:
        next_page = start_page
        while True:
            page = fetch_page(next_page)
            if page.items:
                yield page
                pages += 1
                yielded += len(page.items)
            if max_pages is not None and pages >= max_pages:
                return
            if max_items is not None and yielded >= max_items:
                return
            if not page.items or not page.has_next_page:
                break
            next_page += 1


async def apaginate_many(
    fetch_page_batches: Iterable[Callable[[int], Awaitable[Page[T]]]],
    *,
    start_page: int,
    max_pages: int | None,
    max_items: int | None,
) -> AsyncIterator[Page[T]]:
    """`fetch_page_batches`의 콜백들을 순서대로, 비동기로 순회합니다.

    동작은 `paginate_many`와 동일하며 각 콜백이 코루틴을 반환한다는 점만
    다릅니다.
    """

    pages = 0
    yielded = 0
    for fetch_page in fetch_page_batches:
        next_page = start_page
        while True:
            page = await fetch_page(next_page)
            if page.items:
                yield page
                pages += 1
                yielded += len(page.items)
            if max_pages is not None and pages >= max_pages:
                return
            if max_items is not None and yielded >= max_items:
                return
            if not page.items or not page.has_next_page:
                break
            next_page += 1
