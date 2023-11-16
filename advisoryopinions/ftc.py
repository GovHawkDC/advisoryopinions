import dateutil.parser
import logging
import lxml.html
import re
import requests

from .ao import AdvisoryOpinion

logging.basicConfig(level=logging.INFO)


def scrape_page(page_num: int) -> None:
    page_url = (
        f"https://www.ftc.gov/legal-library/browse/advisory-opinions?page={page_num}"
    )
    logging.info(f"Fetching page {page_num}, {page_url}")
    response = requests.get(page_url).content
    page = lxml.html.fromstring(response)
    page.make_links_absolute(page_url)

    if not page.xpath("//article[contains(@class,'node node--type-advisory-opinion')]"):
        logging.info(f"No results on page {page_num}")
        return False

    for row in page.xpath(
        "//article[contains(@class,'node node--type-advisory-opinion')]"
    ):
        pubdate = row.xpath(".//time/@datetime")[0]
        pubdate = dateutil.parser.parse(pubdate)
        link = row.xpath(".//h3[contains(@class,'node-title')]/a")[0]
        url = link.xpath("@href")[0]
        title = link.xpath("text()")[0]
        internal_id = ""

        ao = AdvisoryOpinion(
            "Federal Trade Commission",
            "FTC",
            pubdate,
            title,
            url,
            identifier=internal_id,
        )

        file_links = row.xpath(".//div[contains(@class,'file')]/a")
        for file_link in file_links:
            link = file_link.xpath("@href")[0]
            file_name = file_link.xpath("text()")[0]
            ao.add_attachment(file_name, link, "application/pdf")

        opinion_check = re.findall(
            r"opinion ((\d+)\-(\d+))", title, flags=re.IGNORECASE
        )
        if opinion_check:
            internal_id = f"opinon-number-{opinion_check[0][0]}"
            ao.internal_id = internal_id

        logging.info(ao)

        is_new = ao.save()
        if not is_new:
            logging.info("Seen item, stopping scrape.")
            return False

    return True


def scrape():
    # scrape until we hit an item we've already seen
    for page in range(0, 50):
        all_new = scrape_page(page)
        if not all_new:
            return