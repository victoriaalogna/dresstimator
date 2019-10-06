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
import json
import pickle

import numpy as np
import pandas as pd
import lightgbm as lgb
from scipy.sparse import csr_matrix, hstack
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import LabelBinarizer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer


def run_model(data_dict, gbm):
    """Run the model based on user input and provided model.

    :param data_dict: The user supplied features.
    :param gbm: The loaded model.

    :return dresstimated_price: The price returned by the model.
    """
    print(">>> Converting user supplied dictionary to data frame...")
    user_input_df = pd.DataFrame([data_dict])

    # Load all pickles
    print(">>> Loading vocabularity pickles...")
    with open("../model/designer.pkl", "rb") as f:
        rawdata = f.read()
    designer_vocab = pickle.loads(rawdata)

    with open("../model/silhouette.pkl", "rb") as f:
        rawdata = f.read()
    silhouette_vocab = pickle.loads(rawdata)

    with open("../model/color.pkl", "rb") as f:
        rawdata = f.read()
    color_vocab = pickle.loads(rawdata)

    with open("../model/description.pkl", "rb") as f:
        rawdata = f.read()
    description_vocab = pickle.loads(rawdata)

    # Vector features...
    print(">>> Vectoring feautres...")
    cv = CountVectorizer(vocabulary=designer_vocab)
    X_designer = cv.fit_transform(user_input_df['designer'])
    print("X_designer:", X_designer)
    print(X_designer.toarray())

    cv = CountVectorizer(vocabulary=silhouette_vocab)
    X_silhouette = cv.fit_transform(user_input_df['silhouette'])
    print("X_silhouette:", X_silhouette)
    print(X_silhouette.toarray())

    cv = CountVectorizer(vocabulary=color_vocab)
    X_color = cv.fit_transform(user_input_df['color'])
    print("X_color:", X_color)
    print(X_color.toarray())

    cv = TfidfVectorizer(vocabulary=description_vocab)
    X_description = cv.fit_transform(user_input_df['description'])
    print("X_description:", X_description)
    print(X_description.toarray())

    # Setting dummies, then stacking array
    X_dummies = csr_matrix(pd.get_dummies(user_input_df[['days']], sparse=True).values)
    sparse_merge = hstack((X_dummies, X_description, X_designer, X_silhouette, X_color)).tocsr()

    sparse_merge.shape

    # Get non zero values, remove if Flase
    mask = np.array(np.clip(sparse_merge.getnnz(axis=0), 0, 1), dtype=bool)
    sparse_merge = sparse_merge[:, mask]

    sparse_merge.shape

    # Run user converted input against model
    X_new = sparse_merge
    # Make a prediction
    Y_new = gbm.predict(X_new)
    Y_new = np.exp(Y_new) - 1

    # Show the inputs and predicted outputs
    print(">>> X=%s" % X_new[0])
    print(">>> Predicted=%s" % Y_new[0])

    # Return the estimated cost of item
    return Y_new[0]
