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


input_dir_path = "extracted_items_clean"


def main():
    """The main entry point for the program."""
    # # Initialize a list to populate with flattened dictionaries
    all_items = list()

    # Fetch all JSON files and loop them
    extracted_data_path = os.path.join(input_dir_path)
    print(f"Processing directory: {extracted_data_path}")
    all_json_files = glob.glob(extracted_data_path + "/*.json")
    for json_file in all_json_files:
        # # Open, then flatten the nested dictionary
        # # print(f"Processing: {json_file}")
        with open(str(json_file)) as f:
            original_dict = json.load(f)
            all_items.append(original_dict)

    with open("all_json_data.json", "w") as f:
        json.dump(all_items, f)


if __name__ == "__main__":
    main()
