#!/usr/bin/env python3
import argparse
import json
import csv
import os
import requests
from urllib.parse import urlparse


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


def ping_website():
    url = 'https://sc-prod.4wdsc.com/graphql'
    headers = {
        'authority': 'sc-prod.4wdsc.com',
        'accept': '*/*',
        'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8,es-419;q=0.7,es;q=0.6',
        'authorization': 'Bearer 1',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'dnt': '1',
        'origin': 'https://www.4wdsupacentre.com.au',
        'pragma': 'no-cache',
        'referer': 'https://www.4wdsupacentre.com.au/',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'store': 'supacentre',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }

    data = {
        'operationName': 'urlResolver',
        'variables': {},
        'query': 'query urlResolver {'
                'urlResolver(url: "/") {'
                '    entity_uid'
                '    __typename'
                '}'
        }
    

    response = requests.post(url, headers=headers, json=data)

    # Print the response
    print(response.text)

def send_request(payload):

    url = 'https://sc-prod.4wdsc.com/graphql'
    headers = {
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

    response = requests.post(url, headers=headers, json=payload)
    result = json.loads(response.text)
    return result

def get_product(id: int, urlKey: str) -> tuple[dict[str, int], str, str, str]:

    data = {
        "operationName": "productDetail",
        "variables": {
            "onServer": False,
            "urlKey": urlKey,
            "id": id
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
    result = send_request(data)
    
    name: str = result['data']['productDetail']['items'][0]['name']
    custom_robbon: str = result['data']['productDetail']['items'][0]['custom_ribbon']
    meta_description: str = result['data']['productDetail']['items'][0]['meta_description']
    # Yes, the regular price is the special price and the special price is the regular price.
    # Thanks for that Kings...
    special_price: int = result['data']['productDetail']['items'][0]['special_price']
    current_price: int = result['data']['productDetail']['items'][0]['price']['regularPrice']['amount']['value']
    min_fin: int = result['data']['productDetail']['items'][0]['price_range']['minimum_price']['final_price']['value']
    max_fin: int = result['data']['productDetail']['items'][0]['price_range']['maximum_price']['final_price']['value']
    min_reg: int = result['data']['productDetail']['items'][0]['price_range']['minimum_price']['regular_price']['value']
    max_reg: int = result['data']['productDetail']['items'][0]['price_range']['maximum_price']['regular_price']['value']
   
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

def get_battery_prices():
    def price_per_Ah(price: dict[str, int], capacity: int):
        cost = price.get('current_price', 0)
        cost_per_Ah = cost / capacity
        return f'${cost_per_Ah:.3f}/Ah'

    batteries: dict[int, tuple[int, str]] = {
        12: (40698, '12ah-lithium-portable-power-pack'),
        24: (40695, '24ah-lithium-portable-power-pack'),
        60: (40833, '60ah-lithium-lite-battery'),
        100: (41598, '100ah-slimline-lithium-battery'),
        120: (20328, 'kings-120ah-lithium-lifepo4-battery-quality-integrated-bms-2000-plus-cycles-long-life'),
        200: (20331, 'kings-200ah-lithium-lifepo4-battery-quality-integrated-bms-2000-plus-cycles-long-life'),
        300: (38319, '300ah-lithium-battery')
    }

    for battery in batteries:
        id = batteries[battery][0]
        urlKey = batteries[battery][1]
        battery_price = get_product(id, urlKey)
        
        amp_hour_price = price_per_Ah(battery_price[0], battery)
        print_prices(f'{battery}Ah battery\t{amp_hour_price}', battery_price[0]['special_price'], battery_price[0]['current_price'], battery_price[3])

def print_prices(product, rrp, sale, custom_robbon):
    print(f'{product}\tRRP:${rrp}\tSale: ${sale}\t{custom_robbon}')

def get_product_id(webpage: str) -> int:
    url = webpage.replace('https://www.4wdsupacentre.com.au', '').replace(' ','')
    payload = {
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

    result = send_request(payload)
    if result['data']['urlResolver'] is None:
        print(f'Product not found: {webpage}')
        return int()
    return result['data']['urlResolver']['id']

def extract_urlKey(url) -> str:
    parsed_url = urlparse(url)
    urlKey = os.path.basename(parsed_url.path)
    return urlKey

def get_urls_from_csv() -> list[tuple[str, int, str]]:
    result: list[tuple[str, int, str]] = []
    with open(args.file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            urlKey = extract_urlKey(row[1])
            id = get_product_id(urlKey)
            result.append((row[0], id, urlKey))

        return result

def main():
    if args.batteries:
        get_battery_prices()
    
    csv_result = get_urls_from_csv()
    for row in csv_result:
        if row[1]:
            result = get_product(row[1], row[2])
            print_prices(row[0], result[0]["special_price"], result[0]["current_price"], result[3])

if __name__ == "__main__":
    main()