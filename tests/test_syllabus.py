"""The published syllabus page, and the link the game uses to reach it.

The page is generated, one file, and self-contained: what is checked here is
that it renders, that its contents links land on real headings, that nothing
it loads leaves the origin it was served from, and that the game's Roadmap
points at it instead of at a page in a personal account.
"""

from __future__ import annotations

from collections.abc import Iterator
from urllib.parse import urlsplit

import pytest
from playwright.sync_api import Browser, Page

from tests.conftest import OUT, ROOT, GamePage

PAGE_PATH = "/docs/site/syllabus.html"
SOURCE = ROOT / "docs" / "site" / "syllabus.html"


@pytest.fixture
def syllabus(chromium: Browser, server: str) -> Iterator[tuple[Page, list[str]]]:
    """The page at laptop size, with its console errors and its requests kept."""
    context = chromium.new_context(viewport={"width": 1440, "height": 900})
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
    page.on(
        "console",
        lambda m: errors.append(m.text) if m.type == "error" else None,
    )
    page.goto(server + PAGE_PATH, wait_until="load")
    yield page, errors
    context.close()


def test_the_page_exists_and_is_one_file() -> None:
    """No build step on the runner: pages.yml copies what the generator wrote."""
    text = SOURCE.read_text(encoding="utf-8")
    assert text.startswith("<!doctype html>")
    assert "<script" not in text, "the syllabus needs no script"
    style = text.split("<style>")[1].split("</style>")[0]
    assert "url(" not in style and "@import" not in style, "it fetches nothing"


def test_it_renders_with_its_headings_and_tables(
    syllabus: tuple[Page, list[str]],
) -> None:
    page, errors = syllabus
    assert page.title() == "Vibe Code Camp: the syllabus"
    assert page.locator("h1").inner_text().strip().startswith("Vibe Code Camp")
    # The generated blocks are tables, so their absence is a stale page.
    assert page.locator("table").count() >= 5
    assert page.locator("h2").count() >= 15
    page.screenshot(path=str(OUT / "syllabus-desktop.png"), full_page=False)
    assert errors == [], errors


def test_every_contents_link_lands_on_a_heading(
    syllabus: tuple[Page, list[str]],
) -> None:
    page, _ = syllabus
    hrefs = page.eval_on_selector_all(
        "nav.toc a", "els => els.map(a => a.getAttribute('href'))"
    )
    assert len(hrefs) >= 20, "the contents is the way around a long page"
    missing = [h for h in hrefs if page.locator(f"main [id='{h[1:]}']").count() != 1]
    assert missing == [], missing


def test_the_contents_is_sticky_on_a_wide_screen_and_gone_on_a_phone(
    chromium: Browser, server: str
) -> None:
    context = chromium.new_context(viewport={"width": 1440, "height": 900})
    page = context.new_page()
    page.goto(server + PAGE_PATH, wait_until="load")
    assert page.eval_on_selector("nav.toc", "el => getComputedStyle(el).position") == (
        "sticky"
    )
    # Scrolled far down a long page, the contents is still on screen.
    page.evaluate("window.scrollTo(0, 4000)")
    top = page.eval_on_selector("nav.toc", "el => el.getBoundingClientRect().top")
    assert 0 <= top < 900, top
    page.screenshot(path=str(OUT / "syllabus-scrolled.png"))
    context.close()

    phone = chromium.new_context(viewport={"width": 390, "height": 844})
    p2 = phone.new_page()
    p2.goto(server + PAGE_PATH, wait_until="load")
    assert (
        p2.eval_on_selector("nav.toc", "el => getComputedStyle(el).display") == "none"
    )
    # No horizontal page scroll: a table scrolls inside its own box instead.
    assert p2.evaluate("document.documentElement.scrollWidth") <= 390
    p2.screenshot(path=str(OUT / "syllabus-phone.png"), full_page=False)
    phone.close()


def test_it_reads_in_the_dark_and_on_paper(chromium: Browser, server: str) -> None:
    dark = chromium.new_context(
        viewport={"width": 1440, "height": 900}, color_scheme="dark"
    )
    page = dark.new_page()
    page.goto(server + PAGE_PATH, wait_until="load")
    background = page.eval_on_selector("body", "el => getComputedStyle(el).background")
    assert "rgb(0, 0, 0)" in background, background
    page.screenshot(path=str(OUT / "syllabus-dark.png"))
    page.emulate_media(media="print")
    assert page.eval_on_selector("nav.toc", "el => getComputedStyle(el).display") == (
        "none"
    )
    assert "rgb(255, 255, 255)" in page.eval_on_selector(
        "body", "el => getComputedStyle(el).background"
    )
    page.screenshot(path=str(OUT / "syllabus-print.png"), full_page=False)
    dark.close()


def test_nothing_it_loads_leaves_the_origin(chromium: Browser, server: str) -> None:
    """No CDN, no font service, no analytics: the page is the whole delivery."""
    context = chromium.new_context(viewport={"width": 1440, "height": 900})
    page = context.new_page()
    seen: list[str] = []
    page.on("request", lambda r: seen.append(r.url))
    page.goto(server + PAGE_PATH, wait_until="load")
    page.wait_for_timeout(0)
    origin = urlsplit(server).netloc
    foreign = [u for u in seen if urlsplit(u).netloc not in ("", origin)]
    assert foreign == [], foreign
    context.close()


def test_the_game_links_to_the_syllabus_and_not_to_an_artifact(
    game_desktop: GamePage,
) -> None:
    """The link resolves through one helper, so a camp never gets a dead one."""
    page = game_desktop.goto().page
    href = page.get_attribute("#syllabuslink", "href")
    assert href is not None
    assert "claude.ai" not in href
    # Served from anywhere but the product's own site, the link is absolute.
    assert href == "https://tpetedb.github.io/vibe-map/syllabus.html"
    # On the site itself the same helper gives the neighbour, which is what a
    # preview deployment and an offline copy of the site both need.
    assert (
        page.evaluate(
            "window.__siteDoc('syllabus.html', 'https://tpetedb.github.io/vibe-map/')"
        )
        == "syllabus.html"
    )
    game_desktop.assert_clean()
