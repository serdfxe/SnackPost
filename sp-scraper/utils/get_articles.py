from .page_content_extractor import PageContentExtractor
from .extract_and_filter_articles import process_links


async def get_articles(url: str, existing: dict[str, str]) -> list[dict[str, str]]:
    scraper = PageContentExtractor()

    raw = scraper.extract_links(url)

    data = process_links(raw, existing)

    return [{"link": k, "title": d} for k, d in data.items()]


async def get_links(url: str) -> dict[str, str]:
    """return {"url": "title", ...}"""
    scraper = PageContentExtractor()

    return scraper.extract_links(url)
