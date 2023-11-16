import dateutil.parser
import logging
import lxml.html
import re
import requests

from ao import AdvisoryOpinion

logging.basicConfig(level=logging.INFO)


def scrape_page(page_num: int) -> None:
    page_url = (
        f"https://www.justice.gov/olc/opinions?page={page_num}"
    )
    logging.info(f"Fetching page {page_num}, {page_url}")
    response = requests.get(page_url).content
    page = lxml.html.fromstring(response)
    page.make_links_absolute(page_url)

    if not page.xpath("//article[contains(@class,'node-opinion')]"):
        logging.info(f"No results on page {page_num}")
        return False

    for row in page.xpath(
        "//article[contains(@class,'node-opinion')]"
    ):
        pubdate = row.xpath(".//time/@datetime")[0]
        pubdate = dateutil.parser.parse(pubdate)
        link = row.xpath(".//h2[contains(@class,'opinion-title')]/a")[0]
        url = link.xpath("@href")[0]
        title = link.xpath("string(.)")

        ao = AdvisoryOpinion(
            "Department of Justice",
            "DOJ",
            pubdate,
            title,
            url,
        )

        ao.add_attachment(title, url, "application/pdf")

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


scrape()
