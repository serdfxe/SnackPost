from zenrows import ZenRowsClient
from urllib.parse import urljoin, urlparse
import json

from core.config import ZENROWS_TOKEN


class PageContentExtractor:
    def __init__(self, zenrows_token=ZENROWS_TOKEN):
        self.client = ZenRowsClient(zenrows_token)
        self.base_domain = None

    def _is_same_domain(self, url):
        if not url:
            return False
        parsed_url = urlparse(url)
        return parsed_url.netloc == self.base_domain.netloc

    def _normalize_url(self, url, base_url):
        if not url.startswith(("http://", "https://")):
            return urljoin(base_url, url)
        return url

    def _process_links(self, links_data, base_url):
        result = {}

        if (
            not links_data
            or "links_texts" not in links_data
            or "link_urls" not in links_data
        ):
            return result

        for text, url in zip(links_data["links_texts"], links_data["link_urls"]):
            if not url or not text:
                continue

            normalized_url = self._normalize_url(url, base_url)

            if not self._is_same_domain(normalized_url):
                continue

            if normalized_url in result:
                result[normalized_url] += " " + text.strip()
            else:
                result[normalized_url] = text.strip()

        return result

    def get_page_content(self, url, as_markdown=True):
        """Get full page content, optionally as markdown"""
        params = {
            "js_render": "true",
            "wait": "15000",
            "response_type": "markdown" if as_markdown else "html",
        }

        try:
            # First try without JS (faster)
            if not as_markdown:
                response = self.client.get(url)
                if (
                    response.status_code == 200 and len(response.text) > 15000
                ):  # Simple check if content is OK
                    return response.text

            # Fallback to JS render if needed
            response = self.client.get(url, params=params)
            return response.text

        except Exception as e:
            print(f"Failed to get page content: {e}")
            return None

    def extract_links(self, url):
        """Extract links from page with smart fallback"""
        self.base_domain = urlparse(url)

        # First try without JS rendering
        try:
            params = {
                "css_extractor": json.dumps(
                    {"links_texts": "a", "link_urls": "a @href"}
                )
            }
            response = self.client.get(url, params=params)
            links_data = json.loads(response.text)

            if (
                links_data and len(links_data.get("link_urls", [])) > 20
            ):  # Minimum links threshold
                return self._process_links(links_data, url)
        except Exception as e:
            print(f"Simple extraction failed, trying with JS render: {e}")

        print("\n\n!!!!!!!!!\n\n")

        # Fallback to JS rendering
        try:
            params = {
                "js_render": "true",
                "wait": "10000",
                "css_extractor": json.dumps(
                    {"links_texts": "a", "link_urls": "a @href"}
                ),
            }
            response = self.client.get(url, params=params)
            links_data = json.loads(response.text)
            return self._process_links(links_data, url)
        except Exception as e:
            print(f"Failed to extract links: {e}")
            return {}


if __name__ == "__main__":
    extractor = PageContentExtractor()
    markdown_content = extractor.extract_links("https://www.reforge.com/blog")
    print(f"\n\n{markdown_content}\n\n")
    print(f"\n\nLEN: {len(markdown_content)}\n\n")
