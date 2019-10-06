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
import glob
import json
import collections


OUT_DIR_PATH = "extracted_items"
if not os.path.exists(OUT_DIR_PATH):
    os.makedirs(OUT_DIR_PATH)

CLEAN_DIR_PATH = "extracted_items_clean"
if not os.path.exists(CLEAN_DIR_PATH):
    os.makedirs(CLEAN_DIR_PATH)

ALL_EXTRACTED_ITEMS = glob.glob(OUT_DIR_PATH + "/*.json")

# Load the JSON schema
JSON_SCHEMA = dict()
JSON_SCHEMA_PATH = "dress_schema.json"
with open(JSON_SCHEMA_PATH) as f:
    JSON_SCHEMA = json.load(f)
    JSON_SCHEMA = JSON_SCHEMA['properties']

JSON_SCHEMA_KEYS = list()
for key in JSON_SCHEMA:
    JSON_SCHEMA_KEYS.append(key)

item_specific_properties = collections.defaultdict(int)


def main():
    """The main entry point for the program."""
    # Loop all JSON files
    for json_file_path in ALL_EXTRACTED_ITEMS:
        print(json_file_path)

        # Open the JSON file and load into dictionary
        with open(json_file_path) as f:
            item_data_dict = json.load(f)

        # Set a temp_dict for output
        temp_dict = dict()

        # Loop all possible keys in eBay API return
        for key in JSON_SCHEMA_KEYS:
            # Skip the ItemSpecifics key, will handle later
            if key == "ItemSpecifics":
                continue
            # Skip the ItemDetails_ key, will populate later
            if key == "ItemDetails_":
                continue

            # If there is an underscore, this represents a nested object
            if "_" in key:
                # Split key into primary and seconday key
                # For example: Seller_FeedbackScore
                # Primary key = Seller
                # Secondary key = FeebackScore
                primary_key = key.split("_")[0]
                secondary_key = key.split("_")[1]

                # Quick fix for _currencyID key, which starts with an underscore
                if secondary_key == "currencyID":
                    secondary_key = "_" + secondary_key

                # Set the key for the nested object, else set to None
                if item_data_dict.get(primary_key):
                    if item_data_dict.get(primary_key).get(secondary_key):
                        temp_dict[key] = item_data_dict[primary_key][secondary_key]
                    else:
                        temp_dict[key] = "None"
                else:
                    temp_dict[key] = "None"
                    # print("NOT FOUND:", key)

            # If there is no underscore, this must be a non-nested object
            else:
                # Set the key for the object, else set to None
                if item_data_dict.get(key):
                    temp_dict[key] = item_data_dict[key]
                else:
                    temp_dict[key] = "None"
                    # print("NOT FOUND:", key)

        # Finished processing base properties
        # Now process the ItemSpecifics key

        if item_data_dict.get("ItemSpecifics"):
            # Get the NameValueList nested object/list
            namevaluelist = item_data_dict["ItemSpecifics"]["NameValueList"]
            # print(namevaluelist)
            # print(type(namevaluelist))

            temp_dict["ItemSpecifics"] = list()
            temp_data = ""

            if isinstance(namevaluelist, list):
                # If the NameValueList is actually a list, append key/value pairs
                for prop_dict in namevaluelist:
                    # temp_dict["ItemSpecifics"].append(prop_dict)
                    temp_data = temp_data + prop_dict["Name"] + "::" + str(prop_dict["Value"]) + "::"
                    # temp_data = temp_data + prop333302180202_dict["Name"] + str(prop_dict["Value"])
                temp_dict["ItemSpecifics"] = temp_data
            else:
                # If the NameValueList is a single object, append key/value pair
                # temp_dict["ItemSpecifics"].append(namevaluelist)
                temp_data = temp_data + namevaluelist["Name"] + "::" + str(namevaluelist["Value"]) + "::"
                # temp_data = temp_data + namevaluelist["Name"] + str(namevaluelist["Value"])
                temp_dict["ItemSpecifics"] = temp_data
        else:
            # If there is no ItemSpecifics, just set the property to None
            temp_dict["ItemSpecifics"] = "None"

        for key in JSON_SCHEMA_KEYS:
            if not key.startswith("ItemDetails_"):
                continue

            # New code block to count ItemSpecific properties:
            if item_data_dict.get("ItemSpecifics"):
                # Get the NameValueList nested object/list
                namevaluelist = item_data_dict["ItemSpecifics"]["NameValueList"]

                if isinstance(namevaluelist, list):
                    # If the NameValueList is actually a list, append key/value pairs
                    for prop_dict in namevaluelist:
                        prop_name = prop_dict["Name"]
                        prop_value = prop_dict["Value"]
                        if isinstance(prop_value, list):
                            prop_value = ",".join(prop_value)
                        # Normalize propname
                        prop_name = prop_name.replace("(", "")
                        prop_name = prop_name.replace(")", "")
                        prop_name = prop_name.replace("'", "")
                        prop_name = prop_name.replace("/", "_")
                        prop_name = prop_name.replace(" ", "_")
                        prop_name = "ItemDetails_" + prop_name
                        temp_dict[prop_name] = prop_value

                else:
                    prop_name = namevaluelist["Name"]
                    prop_value = namevaluelist["Value"]
                    if isinstance(prop_value, list):
                        prop_value = ",".join(prop_value)
                    # Normalize propname
                    prop_name = prop_name.replace("(", "")
                    prop_name = prop_name.replace(")", "")
                    prop_name = prop_name.replace("'", "")
                    prop_name = prop_name.replace("/", "_")
                    prop_name = prop_name.replace(" ", "_")
                    prop_name = "ItemDetails_" + prop_name
                    temp_dict[prop_name] = prop_value

        temp_dict = collections.OrderedDict(sorted(temp_dict.items()))

        # Done with data cleaning, export the item dictionary as a JSON file
        out_fi_name = temp_dict["ItemID"] + ".json"
        out_fi_path = os.path.join(CLEAN_DIR_PATH, out_fi_name)
        with open(out_fi_path, "w") as f:
            json.dump(temp_dict, f, indent=4)


if __name__ == "__main__":
    main()
