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
from datetime import datetime

import numpy as np
import pandas as pd
import lightgbm as lgb
from scipy.sparse import csr_matrix, hstack
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import LabelBinarizer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer


def handle_missing_inplace(df): 
    df['designer'].fillna(value='none', inplace=True)
    df['silhouette_main'].fillna(value='none', inplace=True) 
    df['color_main'].fillna(value='none', inplace=True) 
    df['description'].fillna(value='none', inplace=True)
    return df


def cutting(df):
    # Select number of brands, silhouettes and colors to include
    number_of_designers = 500
    number_of_silhouettes = 100
    number_of_colors = 100
    pop_designer = df['designer'].value_counts().loc[lambda x: x.index != 'none'].index[:number_of_designers]
    df.loc[~df['designer'].isin(pop_designer), 'designer'] = 'none'
    pop_silhouette = df['silhouette_main'].value_counts().loc[lambda x: x.index != 'none'].index[:number_of_silhouettes]
    df.loc[~df['silhouette_main'].isin(pop_silhouette), 'silhouette_main'] = 'none'
    pop_color = df['color_main'].value_counts().loc[lambda x: x.index != 'none'].index[:number_of_colors]
    df.loc[~df['color_main'].isin(pop_color), 'color_main'] = 'none'
    return df


def to_categorical(df):
    df['designer'] = df['designer'].astype('category')
    df['silhouette_main'] = df['silhouette_main'].astype('category')
    df['color_main'] = df['color_main'].astype('category')
    return df


def ngrams(input_str, n=3):
    ngrams = zip(*[input_str[i:] for i in range(n)])
    return ["".join(ngram) for ngram in ngrams]


def transform_color_name(color_name):
    if isinstance(color_name, float):
        # Color is NAN, just return NANs
        return np.nan, np.nan, np.nan
    list_of_colors = re.split(',|/', color_name)
    main_color = None
    sub1_color = None
    sub2_color = None
    try:
        main_color = list_of_colors[1]
    except:
        main_color = np.nan
    try:
        sub1_color = list_of_colors[1]
    except:
        sub1_color = np.nan
    try:
        sub2_color = list_of_colors[1]
    except:
        sub2_color = np.nan
    return main_color, sub1_color, sub2_color


# Make silhouette_main
def transform_silhouette_name(silhouette_name):
    if isinstance(silhouette_name, float):
        # silhouette is NAN, just return NANs
        return np.nan, np.nan, np.nan
    list_of_silhouettes = re.split(',|/', silhouette_name)
    main_silhouette = None
    sub1_silhouette = None
    sub2_silhouette = None
    try:
        main_silhouette = list_of_silhouettes[1]
    except:
        main_silhouette = np.nan
    try:
        sub1_silhouette = list_of_silhouettes[1]
    except:
        sub1_silhouette = np.nan
    try:
        sub2_silhouette = list_of_silhouettes[1]
    except:
        sub2_silhouette = np.nan
    return main_silhouette, sub1_silhouette, sub2_silhouette


def run_model(db_data, user_data):
    """Run the model based on user input and provided model.

    :param db_data: The user supplied features.
    :param user_data: The loaded database contents.

    :return dresstimated_price: The price returned by the model.
    """
    print(">>> Converting user supplied dictionary to data frame...")
    # Load original eBay data as a Pandas data frame
    df = pd.DataFrame(db_data)

    # STAGE ONE: CLEAN ORIGINAL DATA...

    df['price'] = df['ConvertedCurrentPrice_value'].replace(to_replace='None', value=0)
    df['price'] = df['price'].astype('float64')

    # Process ItemDetails_Designer_Brand: Convert to lowercase, remove punctuation
    df['designer'] = df['ItemDetails_Designer_Brand'].map(lambda x: x.lower())
    df['designer'] = df['designer'].map(lambda x: re.sub(r'[,\.!?-]', '', x))
    df['designer'].replace('none', np.nan, inplace=True)

    # Process ItemDetails_Silhouette: Convert to lowercase, remove punctuation
    df['silhouette'] = df['ItemDetails_Silhouette'].map(lambda x: x.lower())
    df['silhouette'] = df['silhouette'].map(lambda x: re.sub(r'[\.!?-]', '', x))
    df['silhouette'].replace('none', np.nan, inplace=True)

    # Process ItemDetails_Color: Convert to lowercase, remove punctuation
    df['color'] = df['ItemDetails_Color'].map(lambda x: x.lower())
    df['color'] = df['color'].map(lambda x: re.sub(r'[\. !?-]', '', x))
    df['color'].replace('none', np.nan, inplace=True)

    # Process Description: Convert to lowercase, remove punctuation
    df['description'] = df['Description'].map(lambda x: x.lower())
    df['description'] = df['description'].map(lambda x: re.sub(r'[,\.!?-]', '', x))

    df['end_time'] = df['EndTime'].apply(lambda x: datetime.strptime(x[:-5], '%Y-%m-%d'+'T'+'%H:%M:%S'))
    df['start_time'] = df['StartTime'].apply(lambda x: datetime.strptime(x[:-5], '%Y-%m-%d'+'T'+'%H:%M:%S'))
    df['days'] = df['end_time'] - df['start_time']
    df['days'] = df['days'].dt.days
    df['days'] = df['days'].astype('str')

    # Make color_main... then silhouette main
    df['color_main'], df['color_sub1'], df['color_sub2'] = zip(*df['color'].apply(transform_color_name))
    df['silhouette_main'], df['silhouette_sub1'], df['silhouette_sub2'] = zip(*df['silhouette'].apply(transform_silhouette_name))

    print(">>> Processing data set...")

    # Create a new data frame from the raw data
    df = df[['designer',
            'silhouette_main',
            'color_main',
            'description',
            'price',
            'days'
        ]]

    # Create train and test datasets from the cleaned datasets
    msk = np.random.rand(len(df)) < 0.8
    train = df[msk]
    test = df[~msk]
    test_new = test.drop('price', axis=1)
    y_test = np.log1p(test["price"])
    # y_test = test["price"]
    train = train[train.price != 0].reset_index(drop=True)

    nrow_train = train.shape[0]
    y = np.log1p(train["price"])
    # y = train["price"]
    df: pd.DataFrame = pd.concat([train, test_new])

    df = handle_missing_inplace(df)
    df = cutting(df)
    df = to_categorical(df)

    print(">>> Generating vectors...")

    # DESIGNER
    tv = TfidfVectorizer(min_df=0.01,
                        analyzer=ngrams,
                        dtype=np.float32)
    X_designer = tv.fit_transform(df['designer'])
    designer_vocab = tv.vocabulary_

    # SILHOUETTE
    lb = LabelBinarizer(sparse_output=True)
    X_silhouette = lb.fit_transform(df['silhouette_main'])

    # COLOR
    lb = LabelBinarizer(sparse_output=True)
    X_color = lb.fit_transform(df['color_main'])

    # DESCRIPTION
    tv = TfidfVectorizer(max_features=50000, 
                         ngram_range=(1, 3),
                         dtype=np.float32)
    X_description = tv.fit_transform(df['description'])
    description_vocab = tv.vocabulary_

    # Make dummies and merge
    X_dummies = csr_matrix(pd.get_dummies(df[['days']], sparse=True).values)
    sparse_merge = hstack((X_dummies, X_designer, X_silhouette, X_color, X_description)).tocsr()

    mask = np.array(np.clip(sparse_merge.getnnz(axis=0) - 1, 0, 1), dtype=bool)
    sparse_merge = sparse_merge[:, mask]

    # Split merged data
    X = sparse_merge[:nrow_train]
    X_test = sparse_merge[nrow_train:]

    train_X = lgb.Dataset(X, label=y)

    # Set LGB parameters
    params = {
            'learning_rate': 0.75,
            'application': 'regression',
            'max_depth': 3,
            'num_leaves': 100,
            'verbosity': -1,
            'metric': 'RMSE',
        }

    print(">>> Initiating GBM model...")
    gbm = lgb.train(params, train_set=train_X, num_boost_round=3200, verbose_eval=100)

    print(">>> Predicting...")
    y_pred = gbm.predict(X_test, num_iteration=gbm.best_iteration)

    print('  > The rmse of prediction is:', mean_squared_error(y_test, y_pred) ** 0.5)

    final_mse=mean_squared_error(y_test, y_pred)
    final_rmse=np.sqrt(final_mse)
    final_rmse
    final_rmse.std()

    print("  > Mean:\t\t ", final_rmse.mean(), "\nStandard Deviation:", final_rmse.std())

    # STAGE TWO: User input processing starts here

    u_df = pd.DataFrame([user_data])

    print("Converted user input to dataframe...")
    print(u_df)

    # u_df['price'] = u_df['price'].replace(to_replace='None', value=0)
    # u_df['price'] = u_df['price'].astype('float64')

    # Process designer: Convert to lowercase, remove punctuation
    u_df['designer'] = u_df['designer'].map(lambda x: x.lower())
    u_df['designer'] = u_df['designer'].map(lambda x: re.sub(r'[,\.!?-]', '', x))
    # u_df['designer'].replace('none', np.nan, inplace=True)

    # Process ItemDetails_Silhouette: Convert to lowercase, remove punctuation
    u_df['silhouette'] = u_df['silhouette'].map(lambda x: x.lower())
    u_df['silhouette'] = u_df['silhouette'].map(lambda x: re.sub(r'[\.!?-]', '', x))
    # u_df['silhouette'].replace('none', np.nan, inplace=True)

    # Process color: Convert to lowercase, remove punctuation
    u_df['color'] = u_df['color'].map(lambda x: x.lower())
    u_df['color'] = u_df['color'].map(lambda x: re.sub(r'[\. !?-]', '', x))
    # u_df['color'].replace('none', np.nan, inplace=True)

    # Process Description: Convert to lowercase, remove punctuation
    # u_df['days'] = u_df['days'].dt.days
    u_df['days'] = u_df['days'].astype('str')

    # Make color_main... then silhouette main
    u_df['color_main'], u_df['color_sub1'], u_df['color_sub2'] = zip(*u_df['color'].apply(transform_color_name))
    u_df['silhouette_main'], u_df['silhouette_sub1'], u_df['silhouette_sub2'] = zip(*u_df['silhouette'].apply(transform_silhouette_name))

    u_df = handle_missing_inplace(u_df)
    u_df = cutting(u_df)
    u_df = to_categorical(u_df)

    print("Cleaned data frame...")
    print(u_df)

    # DESIGNER
    tv = TfidfVectorizer(min_df=0.01,
                        analyzer=ngrams,
                        dtype=np.float32,
                        vocabulary=designer_vocab)
    X_designer = tv.fit_transform(u_df['designer'])
    designer_vocab = tv.vocabulary_

    # SILHOUETTE
    lb = LabelBinarizer(sparse_output=True)
    X_silhouette = lb.fit_transform(u_df['silhouette_main'])

    # COLOR
    lb = LabelBinarizer(sparse_output=True)
    X_color = lb.fit_transform(u_df['color_main'])

    # DESCRIPTION
    tv = TfidfVectorizer(max_features=50000, 
                         ngram_range=(1, 3),
                         dtype=np.float32,
                         vocabulary=description_vocab)
    X_description = tv.fit_transform(u_df['description'])

    X_dummies = csr_matrix(pd.get_dummies(u_df[['days']], sparse=True).values)
    sparse_merge = hstack((X_dummies, X_designer, X_silhouette, X_color, X_description)).tocsr()

    mask = np.array(np.clip(sparse_merge.getnnz(axis=0) - 1, 0, 1), dtype=bool)

    sparse_merge = sparse_merge[:, mask]

    Xnew = sparse_merge
    # make a prediction
    ynew = gbm.predict(Xnew)
    ynew = np.exp(ynew) - 1
    # show the inputs and predicted outputs
    print("    X=%s, Predicted=%s" % (Xnew[0], ynew[0]))

    # Return the estimated cost of item
    return ynew[0]
