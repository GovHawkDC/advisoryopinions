import dateutil.parser
import logging
import lxml.html
import requests
import json

from .ao import AdvisoryOpinion

logging.basicConfig(level=logging.INFO)


def scrape():
    page_url = "https://www.oge.gov/web/OGE.nsf/API.xsp/rest?dataSource=legal"
    logging.info(f"Fetching page {page_url}")
    response = requests.get(page_url).content
    page = json.loads(response)

    for row in page["data"]:
        if row["type"] not in [
            "Program Management Advisories",
            "Legal Advisories",
            "Education Advisories",
        ]:
            continue

        internal_id = row["citation"]

        html = lxml.html.fromstring(row["title"])
        html.make_links_absolute("https://www.oge.gov/")
        title = html.xpath("//a[1]/text()")[0]
        url = html.xpath("//a[1]/@href")[0]

        pubdate = row["docDate"]
        pubdate = dateutil.parser.parse(pubdate)

        internal_id = f"OGE-{internal_id}"

        summary = row["description"]

        if row["notes"]:
            summary = f"{summary} \n\nNotes: {row['notes']}"

        ao = AdvisoryOpinion(
            row["agency"],
            "OGE",
            pubdate,
            title,
            url,
            identifier=internal_id,
            summary=summary,
        )

        is_new = ao.save()
        if not is_new:
            logging.info(f"Seen {url} item, stopping scrape.")
            return False
