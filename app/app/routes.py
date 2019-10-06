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

import re
import pickle
import collections

import numpy as np
import pandas as pd
from flask import request
from flask import redirect
from flask import url_for
from flask import render_template
from pymongo import MongoClient

from app import app
from app.run_model import run_model


######### Create a connections to the MongoDB
client = MongoClient('mongodb://NOTTHEACTUALUSER:NOTTHEACTUALPASSWORD@localhost:27017/dresstimator')
# Select the 'dresstimator' database, and the 'items' collection
db = client['dresstimator']
collection = db['items']

######### Load the ML model
with open('../model/trained_model.pkl', 'rb') as f:
    gbm = pickle.load(f)

######### Set the web app menus based on database contents
def generate_menu_dicts(values_list):
    temp_list = list()
    for i, value in enumerate(values_list):
        if i == 0:
            temp_dict = {"value": value, "Selected": True}
        else:
            temp_dict = {"value": value, "Selected": False}
        temp_list.append(temp_dict)
    return temp_list


# Set the designers menu entries selector menu (top 20) entries
all_designers = collections.defaultdict(int)
for x in collection.find():
    all_designers[x["ItemDetails_Designer_Brand"]] += 1
select_designer_values = [x for x in all_designers if all_designers[x] > 150]
select_designer_options = generate_menu_dicts(select_designer_values)

# Set the silhouette menu entries selector menu (top 20) entries
all_silhouettes = collections.defaultdict(int)
for x in collection.find():
    all_silhouettes[x["ItemDetails_Silhouette"]] += 1
select_silhouette_values = [x for x in all_silhouettes if all_silhouettes[x] > 60]  # Was 100
select_silhouette_values_set = set()
for value in select_silhouette_values:
    values = value.split(",")
    for v in values:
        select_silhouette_values_set.add(v)
select_silhouette_values = list(select_silhouette_values_set)
select_silhouette_options = generate_menu_dicts(select_silhouette_values)

# Set the color menu entries selector menu (top 20) entries
all_colors = collections.defaultdict(int)
for x in collection.find():
    all_colors[x["ItemDetails_Color"]] += 1
select_color_values = [x for x in all_colors if all_colors[x] > 100]  # Was 130
select_color_values_set = set()
for value in select_color_values:
    values = value.split(",")
    for v in values:
        if "custom" in v.lower():
            continue
        select_color_values_set.add(v)
select_color_values = list(select_color_values_set)
select_color_options = generate_menu_dicts(select_color_values)

# Set the days menu entries selector menu (top 20) entries
all_days = collections.defaultdict(int)
select_days_options = [str(x) for x in range(1, 20)]
select_days_options = generate_menu_dicts(select_days_options)

dresstimated_price = None


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', 
                           dresstimated_price=dresstimated_price,
                           select_designer_options=select_designer_options,
                           select_silhouette_options=select_silhouette_options,
                           select_color_options=select_color_options,
                           select_days_options=select_days_options)


@app.route('/submitted', methods=['POST'])
def submitted():
    print(">>> Starting dresstimation processing...")
    
    # Get the user input from web app
    designer = request.form.get('select-designer')
    silhouette = request.form.get('select-silhouette')
    color = request.form.get('select-color')
    days = request.form.get('select-days')
    description = request.form.get('text-description')

    # Put user input into a dictionary
    data_dict = {
        "designer": designer,
        "silhouette": silhouette,
        "color": color,
        "days": days,
        "description": description
    }

    print(">>> Fetched the following user input from web app:")
    print(data_dict)

    dresstimated_price = run_model(data_dict, gbm)

    # Finally, set the price for the dress to display on the web app
    dresstimated_price = "{:.2f}".format(dresstimated_price)

    # Reload the index.html page with the price
    return render_template('index.html', 
                           dresstimated_price=dresstimated_price,
                           select_designer_options=select_designer_options,
                           select_silhouette_options=select_silhouette_options,
                           select_color_options=select_color_options,
                           select_days_options=select_days_options)
