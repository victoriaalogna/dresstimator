#!/usr/bin/env python3

"""
Author:  Victoria Alogna
Email:   victoria.alogna@gmail.com

Copyright (c) 2019, Victoria Alogna

###############################################################################
This file is part of Dresstimator.

Dresstimator is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Dresstimator is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Dresstimator.  If not, see <https://www.gnu.org/licenses/>.
###############################################################################
"""

import json
from typing import Dict

from ebaysdk.finding import Connection


# Read in existing JSON file of item IDs
ALL_ITEM_IDS = dict()
with open("extracted_items.json") as f:
    ALL_ITEM_IDS = json.load(f)

# Setup the credentials for the API connection
API = Connection(config_file='ebay.yaml',
                 siteid="EBAY-US")


def execute_findCompleteItems_request(request_params) -> Dict:
    """Perform a single eBay Finding API request.

    :param request_params: A dictionary containing request paramaters.
    """
    try:
        response = API.execute('findCompletedItems', request_params)
    except ConnectionError as e:
        print(e)

    data_dict = response.dict()
    return data_dict


def execute_api_pagination_query(request_params, page_number):
    """Batch extract a category of sold items from the eBay Finding API.

    :param page_number: A pagination page value.
    """
    # Update the page count based on passed method paramter
    request_params["paginationInput"]["pageNumber"] = int(page_number)
    data_dict = execute_findCompleteItems_request(request_params)

    # Loop the results
    # print(data_dict.keys())
    # print(data_dict["errorMessage"])
    for item in data_dict["searchResult"]["item"]:
        item_id = item["itemId"]
        if item_id not in ALL_ITEM_IDS["items"]:
            ALL_ITEM_IDS["items"].append(item_id)


def determine_api_pagination_count(request_params) -> Dict:
    """Perform a single query to determine how many items in category.

    :param request_params: A dictionary containing request paramaters.
    "return: The number of items in the category.
    """
    data_dict = execute_findCompleteItems_request(request_params)
    pagination_dict = data_dict["paginationOutput"]
    return pagination_dict


def main():
    """The main entry point for the program."""
    # Start page count at 0
    page_number = 1

    # Initialize the base API parameters
    request_params = {
        'categoryId': '15720',
        'itemFilter': [
            {'name': 'Condition', 'value': 'New'}  # Can change to "Used"
        ],
        'paginationInput': {
            'entriesPerPage': 100,
            'pageNumber': int(page_number)
        }
    }

    # NOTE:
    # If over more than 100 pages are queried, it will return an error
    # Could stop loop at 99 instead of: total_pages + 1

    # Query to determine pargination count
    pagination_dict = determine_api_pagination_count(request_params)
    print(pagination_dict)
    total_pages = int(pagination_dict["totalPages"])
    if total_pages > 100:
        total_pages = 99

    for page_number in range(1, total_pages + 1):
        print(f"Processing page {page_number} of {total_pages}")
        execute_api_pagination_query(request_params, page_number)

    with open("extracted_items.json", "w") as f:
        json.dump(ALL_ITEM_IDS, f, indent=4)


if __name__ == "__main__":
    main()
