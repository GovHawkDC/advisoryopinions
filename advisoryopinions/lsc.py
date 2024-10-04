import dateutil.parser
import logging
import lxml.html
import requests

from .ao import AdvisoryOpinion

logging.basicConfig(level=logging.INFO)


def scrape():
    page_url = (
        "https://www.lsc.gov/about-lsc/laws-regulations-and-guidance/advisory-opinions"
    )
    logging.info(f"Fetching page {page_url}")
    response = requests.get(page_url).content
    page = lxml.html.fromstring(response)
    page.make_links_absolute(page_url)

    for row in page.xpath(
        "//div[contains(@class,'field__item')]/div/div/table/tbody/tr"
    ):

        internal_id = row.xpath("td[1]/text()")[0]
        if "opinion" in internal_id.lower():  # header row, skip it
            continue

        link = row.xpath(".//td[3]/a")
        if not link:
            continue
        link = link[0]

        title = link.xpath("text()")[0]

        pubdate = row.xpath("td[2]/text()")[0]
        pubdate = dateutil.parser.parse(pubdate)

        url = link.xpath("@href")[0]
        internal_id = f"LSG-{internal_id}"

        ao = AdvisoryOpinion(
            "Legal Services Corporation",
            "LSC",
            pubdate,
            title,
            url,
            subagency="Office of Legal Affairs",
            identifier=internal_id,
        )

        is_new = ao.save()
        if not is_new:
            logging.info(f"Seen {url} item, stopping scrape.")
            return False
