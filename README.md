# advisoryopinions
Federal Agency Advisory Opinion Scrapers

This repo should be considered an experimental work in progress.

These scrapers run daily in the morning, and commit their output json files automatically.

To create a new scraper: 
 1. Add a new python file in the advisoryopinions directory that scrapes
 2. Do an initial scrape to put the output into ./data
 3. Modify the github workflow to add the cron job, then set the source env based on the cron time.

```python
poetry install
poetry run scrape --help
```