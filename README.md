# advisoryopinions
Federal Agency Advisory Opinion Scrapers

This repo should be considered an experimental work in progress.

These scrapers run daily in the morning, and commit their output json files automatically.

To create a new scraper: 
 1. Add a new python file in the advisoryopinions directory that scrapes
 2. Do an initial scrape to put the output into ./data
 3. Modify the github workflow to add it to the 'source' key of the job strategy matrix

```python
poetry install
poetry run scrape --help
```