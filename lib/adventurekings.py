#!/usr/bin/env python3

"""Docstring for kings.py. """
import json
import csv
import os
from datetime import datetime, timezone
from urllib.parse import urlparse
from typing import Any
from prettytable import PrettyTable
import requests

class KingsScraper:
    """Docstring for KingsScraper. """
    def __init__(self):
        self.table = PrettyTable()
        self.session = requests.Session()
        self.table.align = 'l'
        self.csv_file = 'urls.csv'
        self.graphql_url = 'https://sc-prod.4wdsc.com/graphql'
        self.search_url = 'https://ng7rlxc3b9-dsn.algolia.net/1/indexes/*/queries'
        self.headers: dict[str, str] = {
            'authority': 'sc-prod.4wdsc.com',
            'accept': '*/*',
            'content-type': 'application/json',
            'dnt': '1',
            'referer': 'https://www.4wdsupacentre.com.au/',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'store': 'supacentre',
            'user-agent': 'Mozilla/5.0',
        }
        self.ping_website()

    def close_session(self):
        self.session.close()

    def ping_website(self):
        """Docstring for ping_website. """
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

        response = requests.post(self.graphql_url, headers=self.headers, json=data, timeout=60)

        # Print the response
        print(response.text)

    def send_request(self, payload, params=None, search=False):
        """Sends a GraphQL request to the API.

        Args:
            payload (dict): The GraphQL query and variables

        Returns:
            dict: The API response parsed from JSON
        """

        # data: The GraphQL query and variables.
        #
        # If search is True, then the query is a search query.
        if search:
            url = self.search_url
            self.headers.update({'content-type': 'application/x-www-form-urlencoded'})
        else:
            url = self.graphql_url
        response = self.session.post(url, params=params ,headers=self.headers, json=payload, timeout=60)

        # Parse the response
        #
        result: dict[str, Any] = json.loads(response.text)

        # Return the result
        #
        return result

    def normalize_price(self, data: dict[str, Any]) -> dict[str, Any]:
        """Normalizes the price data."""
        assert isinstance(data, dict), "data must be a dictionary"
        def convert_to_number(price: str|int|float|None) -> Any:
            if price is not None and price != '':
                if isinstance(price, str):
                    try:
                        return int(price)
                    except ValueError:
                        return float(price)
                return price
            return price

        if convert_to_number(data['current_price']) == convert_to_number(data['special_price']):
            data['special_price'] = str()

        if data['current_price'] is None:
            data['current_price'] = data['special_price']
            data['special_price'] = str()

        if data['special_price'] is None:
            data['special_price'] = str()

        if data['notes'] is None:
            data['notes'] = str()


        return data

    def search(self, query: str) -> list[dict[str, Any]]:
        """Search for products."""
        page = 0
        hits_per_page = 9999
        # result: list[dict[str, Any]] = []
        payload: dict[str, list[dict[str, str]]] = {
            'requests': [
                {
                    'indexName': 'magento2_prod_supacentre_products',
                    'params': f'hitsPerPage={hits_per_page}&page={page}&query={query}&facets=[]&tagFilters='
                }
            ]
        }
        params: dict[str, str] = {
            'x-algolia-api-key': '6ce617c383a7722031a27ebc6bff6927',
            'x-algolia-application-id': 'NG7RLXC3B9'
        }

        data = self.send_request(payload, params=params, search=True)
        products = data['results'][0]['hits']
        product: dict[str, dict[str, dict[str, str]]] = {}
        result_list: list[dict[str, Any]] = []
        result_dict: dict[str, Any] = {}
        for product in products:
            result_dict = {
                'name': product.get('name', str()),
                'url': product.get('url', str()),
                'current_price': product.get('special_price', str()),
                'notes': product.get('notes', str()),
                'deal_timer': deal_ends_in(product.get('deal_timer', str())),
                'special_price': product.get('price', {}).get('AUD', {}).get('default', str()),
                'product_id': product.get('product_id', str()),
            }
            # if result_dict['product_id']:
            #     product_details = self.get_product(result_dict['product_id'], self.extract_urlkey(result_dict['url']))
            #     result_dict.update(
            #         {
            #             'deal_timer': product_details['deal_timer'],
            #             'notes': product_details['notes']
            #         }
            #     )
            result_dict = self.normalize_price(result_dict)
            result_list.append(result_dict)

        # return_result: list[dict[str, Any]] = []
        # for items in result_list:
        #     if items['product_id']:
        #         items.update(
        #             {
        #                 'deal_timer': product_details['deal_timer']
        #             }
        #         )
        #     return_result.append(items)
        self.close_session()
        return result_list

    def get_product(self, product_id: int, urlkey: str) -> dict[str, int|str]:
        """Get product details from API."""

        result: dict[str, Any] = {}
        data = {
            "operationName": "productDetail",
            "variables": {
                "onServer": False,
                "urlKey": urlkey,
                "id": product_id
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

        items: dict[str, Any] = result['data']['productDetail']['items'][0]

        # Yes, the regular price is the special price and the special price is the regular price.
        # Thanks for that Kings...
        price_data: dict[str, Any] = {
            'current_price': items['special_price'],
            'special_price': items['price']['regularPrice']['amount']['value'],
            'min_fin': items['price_range']['minimum_price']['final_price']['value'],
            'max_fin': items['price_range']['maximum_price']['final_price']['value'],
            'min_reg': items['price_range']['minimum_price']['regular_price']['value'],
            'max_reg': items['price_range']['maximum_price']['regular_price']['value'],
            'name': items['name'],
            'meta': items['meta_description'],
            'notes': items['custom_ribbon'],
            'deal_timer': deal_ends_in(items['deal_timer'])
        }
        result = self.normalize_price(price_data)

        # if min_fin == max_fin == min_reg == max_reg == current_price:
        #     print('DIFFERENT MIN MAX VARS')
        #     print(min_fin, max_fin, min_reg, max_reg, current_price, name, meta_description, custom_robbon)
        # self.close_session()
        return result

    def daily_deals(self) -> list[dict[str, Any]]:
        """Get daily deals."""
        data = {
            "operationName": "category",
            "variables": {
                "currentPage": 1,
                "filters": {
                    "category_id": {
                        "eq": "5229"
                    }
                },
                "sort": {
                    "position": "ASC"
                },
                "pageSize": 999,
                "id": 5229,
                "onServer": False
            },
            "query": """
            query category(
                $id: Int!, 
                $pageSize: Int!, 
                $currentPage: Int!, 
                $onServer: Boolean!, 
                $filters: ProductAttributeFilterInput!, 
                $sort: ProductAttributeSortInput
            ) {
                category(id: $id) {
                    id
                    image
                    description
                    display_mode
                    cms_block {
                        content
                        __typename
                    }
                    name
                    product_count
                    meta_title
                    meta_keywords @include(if: $onServer)
                    meta_description
                    seo_json_data
                    robots_data
                    page_layout
                    url_key
                    __typename
                }
                products(pageSize: $pageSize, currentPage: $currentPage, filter: $filters, sort: $sort) {
                    items {
                        __typename
                        sku
                        id
                        in_store_only
                        emg_free_shipping
                        exclude_shipping_offer
                        price_including_delivery
                        stock_status
                        deal_timer
                        custom_ribbon
                        flatfreight
                        new_product
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
                        small_image {
                            url
                            __typename
                        }
                        url_key
                        url_suffix
                        ... on ConfigurableProduct {
                            configurable_options {
                                attribute_code
                                attribute_id
                                id
                                label
                                values {
                                    default_label
                                    label
                                    store_label
                                    use_default_value
                                    value_index
                                    __typename
                                }
                                __typename
                            }
                            variants {
                                attributes {
                                    code
                                    value_index
                                    __typename
                                }
                                product {
                                    id
                                    media_gallery_entries {
                                        id
                                        disabled
                                        file
                                        label
                                        position
                                        __typename
                                    }
                                    sku
                                    stock_status
                                    __typename
                                }
                                __typename
                            }
                            __typename
                        }
                        ... on BundleProduct {
                            base_price {
                                value
                                currency
                                __typename
                            }
                            dynamic_sku
                            dynamic_price
                            dynamic_weight
                            price_view
                            ship_bundle_items
                            base_price {
                                value
                                currency
                                __typename
                            }
                            items {
                                title
                                sku
                                option_id
                                type
                                position
                                required
                                options {
                                    id
                                    position
                                    can_change_quantity
                                    is_default
                                    quantity
                                    price
                                    price_type
                                    label
                                    product {
                                        id
                                        name
                                        sku
                                        status
                                        stock_status
                                        emg_free_shipping
                                        price_including_delivery
                                        flatfreight
                                        in_store_only
                                        special_price
                                        price {
                                            regularPrice {
                                                amount {
                                                    value
                                                    __typename
                                                }
                                                __typename
                                            }
                                            __typename
                                        }
                                        __typename
                                    }
                                    __typename
                                }
                                __typename
                            }
                            __typename
                        }
                        ... on GiftCardProduct {
                            giftcard_amounts {
                                value
                                __typename
                            }
                            allow_open_amount
                            open_amount_min
                            open_amount_max
                            __typename
                        }
                    }
                    page_info {
                        total_pages
                        __typename
                    }
                    total_count
                    __typename
                }
            }
            """
        }
        result = self.send_request(data)
        return_result: list[dict[str,Any]] = []
        dict_result: dict[str,Any] = {}
        item: list[dict[str,Any]]= result['data']['products']['items']
        for product in item:
            dict_result = {
                'notes': product['custom_ribbon'],
                'name': product['name'],
                'deal_timer': product['deal_timer'],
                'special_price': product['price']['regularPrice']['amount']['value'],
                'current_price': product['special_price']
            }
            # if product['id']:
            #     product_details = self.get_product(product['id'], product['url_key'])
            #     dict_result.update(
            #         {
            #             'deal_timer': product_details['deal_timer']
            #         }
            #     )
            # return_result.append(product)

            dict_result = self.normalize_price(dict_result)
            return_result.append(dict_result)
        self.close_session()
        return return_result

    def battery_prices(self) -> list[dict[str, int | str]]:
        """
        Get battery prices and calculate price per amp-hour.

        Loops through a dictionary of batteries and their product IDs.
        Gets the price data for each battery from the API.
        Calculates the price per amp-hour and prints the prices.
        """

        def price_per_amp_hour(price: dict[str, int|str], capacity: int):
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
            cost_per_amp_hour = int(cost) / capacity
            return f'{cost_per_amp_hour:.3f}'

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
        result: list[dict[str, int|str]] = []
        for battery, details in batteries.items():
            product_id = details[0]
            urlkey = details[1]
            battery_price = self.get_product(product_id, urlkey)

            amp_hour_price = price_per_amp_hour(battery_price, battery)
            # if battery_price[0]['current_price'] == battery_price[0]['special_price']:
            #     battery_price[0].update({'current_price': 0})
            result.append({
                'battery': battery,
                'cost_per_Ah': amp_hour_price,
                'current_price': battery_price['current_price'],
                'special_price': battery_price['special_price'],
                'deal_timer': battery_price['deal_timer'],
                'notes': battery_price['notes']
            })
        return result

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

    def prices_from_csv(self, csv_file: str):
        """ Print prices from a CSV file"""
        # def get_urls_from_csv(csv_file) -> list[tuple[str, int, str]]:
        def get_urls_from_csv(csv_file):
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
            csv_result = []

            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for column in reader:
                    urlkey = self.extract_urlkey(column[1])
                    product_id = self.get_product_id(urlkey)
                    csv_result.append((column[0], product_id, urlkey))
            self.close_session()
            return csv_result

        product_result = []
        csv_result = get_urls_from_csv(csv_file)
        for column in csv_result:
            if column[1]:
                product = self.get_product(column[1], column[2])
                product_result.append(
                    {
                        'name': column[0],
                        'special_price': product['special_price'],
                        'current_price': product['current_price'],
                        'notes': product['notes'],
                        'deal_timer': product['deal_timer']
                    }
                )
        return product_result

    def print_prices(self, data: list[dict[str, Any]], batteries=False):
        """
        Print product name, RRP, sale price and custom ribbon text.
        """

        if batteries:
            self.table.field_names = ["AH", "$/Ah", "RRP", "Sale", "Notes", "Deal ends in H:M"]
            for battery in data:
                self.table.add_row(row=
                    [
                        battery["battery"],
                        battery["cost_per_Ah"],
                        battery["current_price"],
                        battery["special_price"],
                        battery["notes"],
                        battery["deal_timer"]
                    ]
                )
        else:
            sorted_data = sorted(data, key=lambda k: k['name'])
            self.table.field_names = ["Product", "RRP", "Sale", "Notes", "Deal ends in H:M"]
            for product in sorted_data:
                self.table.add_row(row=
                    [
                        product["name"],
                        product["current_price"],
                        product["special_price"],
                        product["notes"],
                        product["deal_timer"]
                    ]
                )
        print(self.table)


def deal_ends_in(end_time):
    """Docstring for deal_ends_in. """
    if isinstance(end_time, str) and end_time != '':
        deal_time = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
        current_time = datetime.now(timezone.utc)
        time_remaining = deal_time - current_time
        return str(time_remaining)
    return ''
