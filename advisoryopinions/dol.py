import dateutil.parser
import logging
import lxml.html
import re
import requests

from ao import AdvisoryOpinion

logging.basicConfig(level=logging.INFO)


def scrape_page(page_num: int) -> None:
    page_url = f"https://www.dol.gov/agencies/ebsa/about-ebsa/our-activities/resource-center/advisory-opinions?page={page_num}"
    logging.info(f"Fetching page {page_num}, {page_url}")
    response = requests.get(page_url).content
    page = lxml.html.fromstring(response)
    page.make_links_absolute(page_url)

    if not page.xpath("//table[contains(@class,'dol-table')]"):
        return False

    # somtimes the first item on a page is a dupe, so keep a counter

    ct = 0
    for row in page.xpath("//table[contains(@class,'dol-table')]/tbody/tr"):
        ct += 1
        link = row.xpath(
            ".//td[contains(@class,'views-field-field-ebsa-document-number')]/div/a[1]"
        )[0]
        identifier = link.xpath("text()")[0]
        doc_url = link.xpath("@href")[0]

        pubdate = row.xpath(
            ".//td[contains(@class,'views-field-field-ebsa-document-number')]/div/text()"
        )[0]
        pubdate = dateutil.parser.parse(pubdate)

        recipient = row.xpath("string(.//td[2])").strip()
        desc = row.xpath("string(.//td[3])").strip()
        summary = f"{recipient}\n\n{desc}"

        ao = AdvisoryOpinion(
            "Department of Labor",
            "DOL",
            pubdate,
            recipient,
            doc_url,
            identifier=identifier,
            summary=summary,
        )

        ao.add_attachment(identifier, doc_url, "application/pdf")

        logging.info(ao)

        is_new = ao.save()
        if ct > 1 and not is_new:
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
