import dateutil.parser
import logging
import lxml.html
import re
import requests

from ao import AdvisoryOpinion

logging.basicConfig(level=logging.INFO)


def scrape_page(page_num: int) -> None:
    page_url = (
        f"https://oig.hhs.gov/compliance/advisory-opinions/browse/?page={page_num}"
    )
    logging.info(f"Fetching page {page_num}, {page_url}")
    response = requests.get(page_url).content
    page = lxml.html.fromstring(response)
    page.make_links_absolute(page_url)

    for row in page.xpath("//li[contains(@class,'usa-card')]"):
        pubdate = row.xpath(".//span[contains(@class,'text-base-dark')]/text()")[0]
        pubdate = pubdate.replace("Posted ", "").replace("Updated ","")
        print(pubdate)
        pubdate = dateutil.parser.parse(pubdate)
        link = row.xpath(".//h2[contains(@class,'usa-card__heading')]/a")[0]
        url = link.xpath("@href")[0]
        title = link.xpath("text()")[0]
        internal_id = f"OIG-{title}"

        summary = row.xpath("string(.//div[contains(@class,'usa-card__body')])").strip()

        ao = AdvisoryOpinion(
            "Health and Human Sevices",
            "HHS",
            internal_id,
            pubdate,
            title,
            url,
            subagency="Office of the Inspector General",
            summary=summary,
        )

        child_page = requests.get(url).content
        child_page = lxml.html.fromstring(child_page)
        child_page.make_links_absolute(url)

        for doc in child_page.xpath("//a[contains(@class,'pep-document__link')]"):
            ao.add_attachment(
                doc.xpath("text()")[0].strip(),
                doc.xpath("@href")[0],
                "application/pdf"
            )

        logging.info(ao)

        is_new = ao.save()
        if not is_new:
            logging.info("Seen item, stopping scrape.")
            return False

    return True


def scrape():
    # scrape until we hit an item we've already seen
    for page in range(1, 50):
        all_new = scrape_page(page)
        if not all_new:
            return


scrape()
