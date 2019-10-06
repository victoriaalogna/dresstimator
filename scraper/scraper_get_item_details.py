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

import os
import json
import glob
import itertools
from typing import Dict

from ebaysdk.shopping import Connection


# Read in existing JSON file of item IDs
ALL_ITEM_IDS = dict()
with open("extracted_items.json") as f:
    ALL_ITEM_IDS = json.load(f)

# Setup the credentials for the API connection
API = Connection(config_file='ebay.yaml',
                 siteid="EBAY-US")

OUT_DIR_PATH = "extracted_items"
if not os.path.exists(OUT_DIR_PATH):
    os.makedirs(OUT_DIR_PATH)

ALL_EXTRACTED_ITEMS = glob.glob(OUT_DIR_PATH + "/*.json")
ALL_EXTRACTED_ITEMS = [os.path.basename(x) for x in ALL_EXTRACTED_ITEMS]
ALL_EXTRACTED_ITEMS = [os.path.splitext(x)[0] for x in ALL_EXTRACTED_ITEMS]

# Initialize the base API parameters
request_params = {
    'ItemID': None,
    'IncludeSelector': 'Details,ItemSpecifics,TextDescription'
}


def execute_GetMultipleItems_request(request_params) -> Dict:
    """Perform a multi-item eBay get item API request.

    :param request_params: A dictionary containing request paramaters.
    """
    try:
        response = API.execute('GetMultipleItems', request_params)
    except ConnectionError as e:
        print(e)

    data_dict = response.dict()
    return data_dict


def main():
    """The main entry point for the program."""
    # Initialize a list of items to process
    all_item_ids_to_process = list()

    # Fetch all loaded item IDs and loop them
    for item_id in ALL_ITEM_IDS["items"]:
        # Check if the item has already been processed
        if item_id not in ALL_EXTRACTED_ITEMS:
            all_item_ids_to_process.append(item_id)

    # Setup processing stats
    total_queries_to_perform = len(all_item_ids_to_process)/20
    current_queries_done = 1

    # Loop 20 item IDs at a time, and fetch full item details
    for item_ids in itertools.zip_longest(*[iter(all_item_ids_to_process)] * 20):
        print(f"Processing {current_queries_done} out of {total_queries_to_perform}")
        # Remore any None entries from list
        item_ids = list(filter(None, item_ids))
        # Set the ItemID request paramater (20 items)
        request_params["ItemID"] = item_ids
        # Make the query
        out_dict = execute_GetMultipleItems_request(request_params)
        # Loop the 20 items results
        for item in out_dict["Item"]:
            # Save the JSON to a file
            out_fi_name = item["ItemID"] + ".json"
            out_fi_path = os.path.join(OUT_DIR_PATH, out_fi_name)
            with open(out_fi_path, "w") as f:
                json.dump(item, f, indent=4)

        current_queries_done += 1


if __name__ == "__main__":
    main()
