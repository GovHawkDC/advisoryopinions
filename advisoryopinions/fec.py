import dateutil.parser
import json
import logging
import os
import requests

from .ao import AdvisoryOpinion

logging.basicConfig(level=logging.INFO)


def scrape_page(page_num: int) -> None:
    from_hit = page_num * 100
    # Key available from https://api.open.fec.gov/developers/
    api_key = os.environ["FEC_API_KEY"]

    page_url = f"https://api.open.fec.gov/v1/legal/search?api_key={api_key}&type=advisory_opinions&ao_category=F&from_hit={from_hit}&hits_returned=100"
    log_url = page_url.replace(api_key, "API_KEY_HERE")
    logging.info(f"Fetching page {page_num}, {log_url}")
    
    response = requests.get(page_url).content
    rows = json.loads(response)

    if len(rows["advisory_opinions"]) == 0:
        return False

    for row in rows["advisory_opinions"]:
        url = f"https://www.fec.gov/data/legal/advisory-opinions/{row['ao_no']}/"
        ao = AdvisoryOpinion(
            "Federal Election Commission",
            "FEC",
            dateutil.parser.parse(row["issue_date"]),
            row["name"],
            url,
            identifier=row["ao_no"],
            summary=row["summary"],
        )

        for doc in row["documents"]:
            doc_url = f"https://www.fec.gov{doc['url']}"
            ao.add_attachment(doc["description"], doc_url, "application/pdf")

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
