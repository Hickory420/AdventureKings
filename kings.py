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

parser.add_argument('--search', '-s',
                    help='Search for products',
                    type=str)

parser.add_argument('--deals', '-d',
                    help='Show Daily Deals',
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

    if args.batteries:
        battery_data = kings.battery_prices()
        kings.print_prices(battery_data, batteries=True)
        raise SystemExit(0)

    if args.search:
        search_data = kings.search(args.search)
        kings.print_prices(search_data)
        raise SystemExit(0)

    if args.deals:
        deals_data = kings.daily_deals()
        kings.print_prices(deals_data)
        raise SystemExit(0)

    csv_data = kings.prices_from_csv(csv_file)
    kings.print_prices(csv_data)


if __name__ == "__main__":
    kings = adventurekings.KingsScraper()
    main()
else:
    raise SystemExit(2)
