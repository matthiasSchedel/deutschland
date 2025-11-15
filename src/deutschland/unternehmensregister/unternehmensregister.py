import hashlib
import json
import re
import time
from typing import Dict, List, Optional
from urllib.parse import quote_plus, urlencode

import dateparser
import requests
from bs4 import BeautifulSoup

from deutschland.config import Config, module_config


class Report:
    __slots__ = ["date", "name", "content_url", "company", "report", "raw_report", "publication_type"]

    def __init__(self, date, name, content_url, company, report=None, raw_report=None, publication_type=None):
        self.date = date
        self.name = name
        self.content_url = content_url
        self.company = company
        self.report = report
        self.raw_report = raw_report
        self.publication_type = publication_type

    def to_dict(self):
        return {
            "date": self.date,
            "name": self.name,
            "company": self.company,
            "report": self.report,
            "raw_report": self.raw_report,
            "publication_type": self.publication_type,
        }

    def to_hash(self):
        """MD5 hash of a the report."""
        dhash = hashlib.md5()

        entry = {
            "date": self.date.isoformat() if self.date else None,
            "name": self.name,
            "company": self.company,
            "report": self.report,
        }

        encoded = json.dumps(entry, sort_keys=True).encode("utf-8")
        dhash.update(encoded)

        return dhash.hexdigest()


class Unternehmensregister:
    """
    Client for accessing German company registry data from unternehmensregister.de.

    This is a replacement for the old Bundesanzeiger API, compatible with the new
    unternehmensregister.de website structure.

    Note: unternehmensregister.de is a Next.js/React application without an official API.
    This implementation uses web scraping techniques to extract data.
    """

    BASE_URL = "https://www.unternehmensregister.de"

    __slots__ = ["session", "_config"]

    def __init__(self, config: Config = None):
        if config is None:
            self._config = module_config
        else:
            self._config = config

        self.session = requests.Session()
        if self._config.proxy_config is not None:
            self.session.proxies.update(self._config.proxy_config)

        # Set headers to mimic a real browser
        self.session.headers.update({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "DNT": "1",
            "Pragma": "no-cache",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        })

    def __get_response(self, url: str) -> requests.Response:
        """Send a request to a URL and validate the response"""
        response = self.session.get(url, timeout=30, allow_redirects=True)
        if not response.ok:
            raise ConnectionError(
                f"There was an error while connecting to '{response.url}'. Got status code {response.status_code} - {response.reason}"
            )
        return response

    def __post_response(self, url: str, data: dict) -> requests.Response:
        """Send a POST request to a URL and validate the response"""
        response = self.session.post(url, json=data, timeout=30)
        if not response.ok:
            raise ConnectionError(
                f"There was an error while connecting to '{response.url}'. Got status code {response.status_code} - {response.reason}"
            )
        return response

    def __find_search_token(self, response_text: str) -> Optional[str]:
        """
        Try to extract search token from the page.
        The new site may use tokens in the search URL.
        """
        # Look for search tokens in the HTML
        # Pattern: searchToken=...
        match = re.search(r'searchToken[=:][\"\']?([a-zA-Z0-9_-]+)', response_text)
        if match:
            return match.group(1)
        return None

    def __extract_next_data(self, html: str) -> Optional[dict]:
        """Extract Next.js data from the page if available"""
        soup = BeautifulSoup(html, "html.parser")

        # Next.js apps often include data in a script tag with id="__NEXT_DATA__"
        next_data_script = soup.find("script", {"id": "__NEXT_DATA__"})
        if next_data_script and next_data_script.string:
            try:
                return json.loads(next_data_script.string)
            except (json.JSONDecodeError, TypeError):
                pass

        return None

    def __parse_search_results(self, html: str) -> List[Report]:
        """
        Parse search results from the HTML page.

        Since the site is heavily client-side rendered, we may need to extract
        data from script tags or make additional API calls.
        """
        soup = BeautifulSoup(html, "html.parser")
        reports = []

        # Try to extract Next.js data
        next_data = self.__extract_next_data(html)
        if next_data:
            # Process Next.js data structure
            # This will need to be adjusted based on actual data structure
            try:
                # Example structure - adjust based on actual response
                props = next_data.get("props", {})
                page_props = props.get("pageProps", {})
                results = page_props.get("results", [])

                for result in results:
                    report = self.__create_report_from_data(result)
                    if report:
                        reports.append(report)
            except (KeyError, TypeError) as e:
                # If structure is different, fall back to HTML parsing
                pass

        # Fallback: Parse HTML for result elements
        # Look for common result container patterns
        result_containers = soup.find_all("div", class_=re.compile(r"result|search.*item|company.*card", re.I))

        for container in result_containers:
            report = self.__parse_result_container(container)
            if report:
                reports.append(report)

        return reports

    def __create_report_from_data(self, data: dict) -> Optional[Report]:
        """Create a Report object from structured data"""
        try:
            company_name = data.get("companyName") or data.get("name") or data.get("company")
            date_str = data.get("date") or data.get("publicationDate") or data.get("publishDate")
            title = data.get("title") or data.get("name")
            url = data.get("url") or data.get("link") or data.get("contentUrl")
            pub_type = data.get("type") or data.get("publicationType")

            if not company_name:
                return None

            date = dateparser.parse(date_str, languages=["de"]) if date_str else None

            return Report(
                date=date,
                name=title or "",
                content_url=url or "",
                company=company_name,
                publication_type=pub_type
            )
        except Exception:
            return None

    def __parse_result_container(self, container) -> Optional[Report]:
        """Parse a single result container from HTML"""
        try:
            # Try to find company name
            company_elem = container.find(["h1", "h2", "h3", "h4"], class_=re.compile(r"company|name|title", re.I))
            if not company_elem:
                company_elem = container.find("a")

            if not company_elem:
                return None

            company_name = company_elem.get_text(strip=True)

            # Try to find link
            link_elem = container.find("a")
            content_url = link_elem.get("href", "") if link_elem else ""

            # Make URL absolute if it's relative
            if content_url and not content_url.startswith("http"):
                content_url = self.BASE_URL + content_url

            # Try to find date
            date_elem = container.find(class_=re.compile(r"date|time|published", re.I))
            date = None
            if date_elem:
                date_text = date_elem.get_text(strip=True)
                date = dateparser.parse(date_text, languages=["de"])

            # Try to find publication type
            type_elem = container.find(class_=re.compile(r"type|category", re.I))
            pub_type = type_elem.get_text(strip=True) if type_elem else None

            title = company_elem.get_text(strip=True)

            return Report(
                date=date,
                name=title,
                content_url=content_url,
                company=company_name,
                publication_type=pub_type
            )
        except Exception:
            return None

    def __fetch_report_content(self, report: Report) -> None:
        """Fetch the full content of a report"""
        if not report.content_url:
            return

        try:
            response = self.__get_response(report.content_url)
            soup = BeautifulSoup(response.text, "html.parser")

            # Look for content container
            # Common patterns for publication containers
            content_elem = (
                soup.find("div", class_=re.compile(r"publication|content|document|report", re.I)) or
                soup.find("main") or
                soup.find("article")
            )

            if content_elem:
                report.report = content_elem.get_text(strip=True, separator="\n")
                report.raw_report = content_elem.prettify()
        except Exception:
            # If we can't fetch content, leave it empty
            pass

    def get_reports(
        self,
        company_name: str,
        *,
        page_limit: int = 1,
        fetch_content: bool = False,
        areas: str = "all"
    ) -> Dict[str, dict]:
        """
        Fetch all reports for this company name from unternehmensregister.de

        :param company_name: The company name to search for
        :param page_limit: Maximum number of pages to fetch (default: 1). Each page typically has 10-20 reports.
            Pass float('inf') to fetch all pages (this might take a while).
        :param fetch_content: Whether to fetch the full content of each report (default: False).
            This will make additional requests and may be slower.
        :param areas: Search areas - "all", "Bekanntmachungen", "Jahresabschluss", etc. (default: "all")
        :return: Dict of all reports, keyed by report hash
        """
        results = {}

        # First, visit the home page to establish session and get cookies
        try:
            home_response = self.__get_response(f"{self.BASE_URL}/de")
            # Give some time for cookies to be set
            time.sleep(0.5)
        except Exception as e:
            # Continue even if home page fails, but log it
            print(f"Warning: Could not access homepage: {e}")

        # Perform search
        search_params = {
            "companyName": company_name,
            "areas": areas
        }

        search_url = f"{self.BASE_URL}/de/suche?{urlencode(search_params)}"

        pages = 0
        current_url = search_url

        while current_url and pages < page_limit:
            try:
                response = self.__get_response(current_url)

                # Parse results from this page
                reports = self.__parse_search_results(response.text)

                # Fetch full content if requested
                if fetch_content:
                    for report in reports:
                        self.__fetch_report_content(report)
                        # Small delay to avoid overwhelming the server
                        time.sleep(0.5)

                # Add reports to results
                for report in reports:
                    report_hash = report.to_hash()
                    results[report_hash] = report.to_dict()

                # Look for next page link
                # This will need to be adjusted based on actual pagination structure
                current_url = None  # For now, only fetch first page
                # TODO: Implement pagination when we can see the actual structure

                pages += 1

                # Small delay between pages
                if current_url:
                    time.sleep(1)

            except Exception as e:
                # Log error but continue
                print(f"Error fetching page: {e}")
                break

        return results


if __name__ == "__main__":
    ur = Unternehmensregister()
    reports = ur.get_reports("Deutsche Bahn AG")
    print(f"Found {len(reports)} reports")
    for report_hash, report in reports.items():
        print(f"- {report['company']}: {report['name']} ({report['date']})")
