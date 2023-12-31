#!/usr/bin/env python3

import json
import csv
import os
from urllib.parse import urlparse
import requests

class KingsScraper:
    def __init__(self):
        self.csv_file = 'urls.csv'
        self.url = 'https://sc-prod.4wdsc.com/graphql'
        self.headers: dict[str, str] = {
            'authority': 'sc-prod.4wdsc.com',
            'accept': '*/*',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'dnt': '1',
            'origin': 'https://www.4wdsupacentre.com.au',
            'pragma': 'no-cache',
            'referer': 'https://www.4wdsupacentre.com.au/',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'store': 'supacentre',
            'user-agent': 'Mozilla/5.0'
        }
        self.ping_website()

    def ping_website(self):
        # data: The GraphQL query and variables.
        data = {
            'operationName': 'urlResolver',
            'variables': {},
            'query': 'query urlResolver {'
                    '    urlResolver(url: "/") {'
                    '        entity_uid'
                    '        __typename'
                    '    }'
                    '}'
        }

        response = requests.post(self.url, headers=self.headers, json=data, timeout=60)

        # Print the response
        print(response.text)

    def send_request(self, payload):
        """Sends a GraphQL request to the API.

        Args:
            payload (dict): The GraphQL query and variables

        Returns:
            dict: The API response parsed from JSON
        """

        # data: The GraphQL query and variables.
        #
        response = requests.post(self.url, headers=self.headers, json=payload, timeout=60)

        # Parse the response
        #
        result = json.loads(response.text)

        # Return the result
        #
        return result

    def get_product(self, prodict_id: int, urlkey: str) -> tuple[dict[str, int], str, str, str]:
        """Get product details from API.

        Args:
            prodict_id (int): The product ID
            urlkey (str): The product URL key

        Returns:
            tuple[dict, str, str, str]: A tuple containing:
                - dict: The product price info
                - str: The product name
                - str: The meta description
                - str: The custom ribbon
        """

        data = {
            "operationName": "productDetail",
            "variables": {
                "onServer": False,
                "urlKey": urlkey,
                "id": prodict_id
            },
            "query": """
                query productDetail($urlKey: String!, $id: Int!, $onServer: Boolean!) {
                    productDetail: products(filter: {url_key: {eq: $urlKey}}, id: $id) {
                        items {
                            __typename
                            brand
                            in_store_only
                            special_deal
                            deal_categories
                            deal_skus
                            deal_timer
                            deal_timer_colour
                            deal_timer_background_colour
                            id
                            exclude_shipping_offer
                            emg_free_shipping
                            price_including_delivery
                            custom_ribbon
                            flatfreight
                            flatrate_express
                            fittings
                            stock_status
                            stock_status_online
                            pre_order_date
                            in_the_box
                            downloads_manuals
                            marketing_highlight
                            new_product
                            meta_title @include(if: $onServer)
                            meta_keyword @include(if: $onServer)
                            meta_description
                            name
                            special_price
                            price {
                                regularPrice {
                                    amount {
                                        currency
                                        value
                                        __typename
                                    }
                                    __typename
                                }
                                __typename
                            }
                            price_range {
                                minimum_price {
                                    final_price {
                                        currency
                                        value
                                        __typename
                                    }
                                    regular_price {
                                        currency
                                        value
                                        __typename
                                    }
                                    __typename
                                }
                                maximum_price {
                                    final_price {
                                        currency
                                        value
                                        __typename
                                    }
                                    regular_price {
                                        currency
                                        value
                                        __typename
                                    }
                                    __typename
                                }
                                __typename
                            }
                            sku
                            small_image {
                                url
                                __typename
                            }
                            url_key
                            url_suffix
                            warehouse_despatch_days
                            page_layout
                            display_store_locations {
                                location_code
                                availability
                                fittings
                                name
                                phone
                                city
                                description
                                postcode
                                street
                                state
                                __typename
                            }
                        }
                        __typename
                    }
                }
            """
        }
        result = self.send_request(data)

        name: str = result['data']['productDetail']['items'][0]['name']
        custom_robbon: str = result['data']['productDetail']['items'][0]['custom_ribbon']
        meta_description: str = result['data']['productDetail']['items'][0]['meta_description']
        # Yes, the regular price is the special price and the special price is the regular price.
        # Thanks for that Kings...
        special_price: int = result['data']['productDetail']['items'][0]['special_price']
        current_price: int = result['data']['productDetail']['items'][0]['price']\
            ['regularPrice']['amount']['value']
        min_fin = result['data']['productDetail']['items'][0]\
            ['price_range']['minimum_price']['final_price']['value']
        max_fin = result['data']['productDetail']['items'][0]\
            ['price_range']['maximum_price']['final_price']['value']
        min_reg = result['data']['productDetail']['items'][0]\
            ['price_range']['minimum_price']['regular_price']['value']
        max_reg = result['data']['productDetail']['items'][0]\
            ['price_range']['maximum_price']['regular_price']['value']


        if min_fin == max_fin == min_reg == max_reg == current_price:
            return {
                'current_price': current_price,
                'special_price': special_price
                }, name, meta_description, custom_robbon
        return {
            'current_price': current_price,
            'special_price': special_price,
            'min_fin': min_fin,
            'max_fin': max_fin,
            'min_reg': min_reg,
            'max_reg': max_reg
            }, name, meta_description, custom_robbon

    def battery_prices(self):
        """
        Get battery prices and calculate price per amp-hour.

        Loops through a dictionary of batteries and their product IDs.
        Gets the price data for each battery from the API.
        Calculates the price per amp-hour and prints the prices.

        Returns:
            None
        """

        def price_per_amp_hour(price: dict[str, int], capacity: int):
            """
            Calculate price per amp hour (Ah) for a battery.

            Given a dictionary containing price info and an integer capacity in Ah,
            this calculates the cost per Ah based on the 'current_price' in the
            price dictionary.

            Args:
                price (dict[str, int]): Dictionary containing price info, expected to have a 'current_price' key
                capacity (int): Battery capacity in amp hours

            Returns:
                str: Price per Ah formatted as a string, e.g. '$0.123/Ah'

            Raises:
                KeyError: If 'current_price' not found in price dict
            """

            cost = price.get('current_price', 0)
            cost_per_amp_hour = cost / capacity
            return f'${cost_per_amp_hour:.3f}/Ah'

        batteries: dict[int, tuple[int, str]] = {
            12: (
                    40698,
                    '12ah-lithium-portable-power-pack'
                ),
            24: (
                    40695,
                    '24ah-lithium-portable-power-pack'
                ),
            60: (
                    40833,
                    '60ah-lithium-lite-battery'
                ),
            100: (
                    41598,
                    '100ah-slimline-lithium-battery'
                ),
            120: (
                    20328,
                    'kings-120ah-lithium-lifepo4-battery-quality-integrated-bms-2000-plus-cycles-long-life'
                ),
            200: (
                    20331,
                    'kings-200ah-lithium-lifepo4-battery-quality-integrated-bms-2000-plus-cycles-long-life'
                ),
            300: (
                    38319,
                    '300ah-lithium-battery'
                )
        }

        for battery, details in batteries.items():
            product_id = details[0]
            urlkey = details[1]
            battery_price = self.get_product(product_id, urlkey)

            amp_hour_price = price_per_amp_hour(battery_price[0], battery)
            self.print_prices(f'{battery}Ah battery\t{amp_hour_price}', battery_price[0]['special_price'], battery_price[0]['current_price'], battery_price[3])

    def print_prices(self, product, rrp, sale, custom_robbon):
        """
        Print product name, RRP, sale price and custom ribbon text.

        Args:
            product (str): Product name
            rrp (float): Original recommended retail price
            sale (float): Current discounted sale price
            custom_robbon (str): Custom text to display, e.g. 'Best Seller!'

        Prints:
            A formatted string with product, RRP, sale price and custom text.

        Example:
            >>> print_prices('Acme Battery', 99.99, 79.99, 'Best Seller!')
            Acme Battery   RRP:$99.99   Sale: $79.99   Best Seller!
        """
        print(f'{product}\tRRP:${rrp}\tSale: ${sale}\t{custom_robbon}')

    def get_product_id(self, webpage: str) -> int:
        """
        Given a product webpage URL, extracts the product ID by:

        1. Removing the base URL and whitespace to get a clean relative URL
        2. Sending a GraphQL query with the relative URL to the urlResolver endpoint
        3. Extracting the 'id' field from the result

        Args:
            webpage (str): The full product webpage URL

        Returns:
            int: The extracted Magento product ID

        Raises:
            ValueError: If no product is found for the given URL

        Examples:
            >>> get_product_id('https://www.4wdsupacentre.com.au/arb-air-compressor-12v')
            40637
        """
        url = webpage.replace('https://www.4wdsupacentre.com.au', '').replace(' ','')
        payload: dict[str, str] = {
            "query": f"""
                {{
                    urlResolver(url: "{url}")
                    {{
                        type
                        id
                        relative_url
                        redirectCode
                    }}
                }}
            """
        }

        result = self.send_request(payload)
        if result['data']['urlResolver'] is None:
            print(f'Product not found: {webpage}')
            return int()
        return result['data']['urlResolver']['id']

    def extract_urlkey(self, url) -> str:
        """Extracts the urlKey from a full URL by parsing it and returning the basename of the path.

        Args:
            url (str): The full URL to extract the urlKey from.

        Returns:
            str: The extracted urlKey portion of the URL.
        """
        parsed_url = urlparse(url)
        urlkey = os.path.basename(parsed_url.path)
        return urlkey

    def prices_from_csv(self, csv_file: str) -> None:
        def get_urls_from_csv(csv_file) -> list[tuple[str, int, str]]:
            """Reads a CSV file and extracts the urlKey and product ID for each row.

            The CSV file should contain the product name in the first column, 
            and the product URL in the second column.

            This function extracts the urlKey portion from the URL and looks up the
            Magento product ID for that urlKey.

            It returns a list of tuples containing:
                - Product name
                - Product ID
                - urlKey

            Returns:
                list[tuple[str, int, str]]: A list of tuples containing the product
                    name, ID, and urlKey for each row in the CSV file.
            """
            result: list[tuple[str, int, str]] = []

            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    urlkey = self.extract_urlkey(row[1])
                    product_id = self.get_product_id(urlkey)
                    result.append((row[0], product_id, urlkey))

                return result
        csv_result = get_urls_from_csv(csv_file)
        for row in csv_result:
            if row[1]:
                result = self.get_product(row[1], row[2])
                self.print_prices(row[0], result[0]["special_price"], result[0]["current_price"], result[3])
