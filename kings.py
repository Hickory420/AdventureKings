#!/usr/bin/env python3

"""
kings.py

This module provides functionality for scraping product data from the
4WD Supacentre website. It allows retrieving product URLs from a CSV file
or scraping a single URL provided directly. Battery prices can also be scraped.

The main capabilities are:

- Send GraphQL requests to retrieve product data from the 4WD Supacentre API
- Read product URLs to scrape from a CSV file
- Scrape a single product URL provided as a command line argument
- Optionally scrape battery prices
- Print API responses to stdout
"""

import argparse
from lib import adventurekings


argparse.ArgumentParser(description='Scrape 4WD Supacentre website for URLs')
parser = argparse.ArgumentParser()

parser.add_argument('--url', '-u',
                    help='URL to scrape')

parser.add_argument('--file', '-f',
                    help='CSV file to read from',
                    default='urls.csv')

parser.add_argument('--batteries', '-b',
                    help='Scrape battery prices',
                    action='store_true')

args = parser.parse_args()


def main():
    """
    The main function that runs the key steps:

    1. Gets battery prices if --batteries flag is passed
    2. Gets product URLs and IDs from a CSV file
    3. Gets pricing info for each product
    4. Prints pricing info for each product

    """
    if args.file:
        csv_file: str = args.file
    else:
        csv_file: str = 'urls.csv'

    kings.prices_from_csv(csv_file)

    if args.batteries:
        kings.battery_prices()
        raise SystemExit(0)

if __name__ == "__main__":
    kings = adventurekings.KingsScraper()
    main()
else:
    raise SystemExit(2)
