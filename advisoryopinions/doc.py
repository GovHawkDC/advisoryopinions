import dateutil.parser
import logging
import lxml.html
import requests

from .ao import AdvisoryOpinion

logging.basicConfig(level=logging.INFO)


def scrape() -> None:
    page_url = "https://www.bis.doc.gov/index.php/policy-guidance/advisory-opinions"
    logging.info(f"Fetching page {page_url}")
    response = requests.get(page_url).content
    page = lxml.html.fromstring(response)
    page.make_links_absolute(page_url)

    for row in page.xpath("//table[tbody]/tbody/tr")[1:]:

        pubdate = row.xpath("td[1]/text()")[0].strip()
        pubdate = dateutil.parser.parse(pubdate)

        if not row.xpath("td[2]//a"):
            item_text = row.xpath("string(td[2])")[0].strip()
            logging.info(f"No link for {item_text}, skipping row.")
            continue

        link = row.xpath("td[2]//a")[0]
        url = link.xpath("@href")[0]
        title = link.xpath("string(.)").strip()

        ao = AdvisoryOpinion(
            "Department of Commerce",
            "DOC",
            pubdate,
            title,
            url,
            subagency="Bureau of Industry and Security",
        )

        ao.add_attachment(title, url, "application/pdf")

        logging.info(ao)

        is_new = ao.save()
        if not is_new:
            logging.info("Seen item, stopping scrape.")
            return False

    return True
