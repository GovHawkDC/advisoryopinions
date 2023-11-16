import dateutil.parser
import logging
import lxml.html
import re
import requests

from ao import AdvisoryOpinion

logging.basicConfig(level=logging.INFO)


def scrape_opinions() -> None:
    page_url = f"https://www.consumerfinance.gov/compliance/advisory-opinion-program/"
    logging.info(f"Fetching page {page_url}")
    response = requests.get(page_url).content
    page = lxml.html.fromstring(response)
    page.make_links_absolute(page_url)

    for row in page.xpath(
        "//main//div[@class='block'][1]//p[a[contains(@class,'link__icon')]]"
    )[1:]:
        if not row.xpath("text()"):
            continue
        pubdate = row.xpath("text()")[0].strip()
        pubdate = pubdate.replace("–", "").strip()
        pubdate = dateutil.parser.parse(pubdate)

        link = row.xpath("a")[0]
        url = link.xpath("@href")[0]
        title = link.xpath("span[1]/text()")[0]

        ao = AdvisoryOpinion(
            "Consumer Financial Protection Bureau",
            "CFPB",
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
    scrape_opinions()


scrape()
