import importlib
import argparse

def scrape() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "agency", type=str, help="Agency to scrape."
    )
    args = parser.parse_args()

    module = importlib.import_module(f".{args.agency}", package="advisoryopinions")
    module.scrape()