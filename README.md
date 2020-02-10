# Dresstimator - A price recommender for second hand wedding dresses

The following README documents the pipeline I created that uses eBay's historical data of sold second-hand wedding dresses to predict the average price of a wedding dress, given it's brand, silhouette, color, and the number of days by which the user wants to sell the dress:

## Motivation

The second-hand market is undergoing a revolution. In 2018, the second-hand market accounted for $28 billion (versus $35 for fast fashion) and is predicted to reach $64 billion by 2028. This fashion revolution is also impacting wedding dresses, with the search aggregator Lyst reporting a 93% increase in views of second-hand wedding dresses. Why is this happening? Well, weddings are expensive. One way to cut costs is to buy your wedding dress second-hand. Or, if you've already bought your dress, one way to recoup some losses is to sell your dress second-hand. But, women often don’t know the market value of their dresses, with prices for the same item varying by up to $5000. Furthermore, current price calculators don’t consider the time constraints that often motivate selling, such as moving or debt. Using ebay data, I authored a web application through with a user inputs features (e.g., designer, silhouette… and the time she wants to sell by) and is recommended multiple pricing options based on how quickly she wants to sell her dress. This product is generalizable to other second hand products, such as children’s clothes.

## Data Acquisiton and processing

Using the eBay API I extracted the details of all the sold second-hand wedding dresses during the last 90 days, roughly about 21 thousand entries. Category entries were pre-processed by removing spaces, dashes and converting to lower case. I extracted the relevant factors from the semi-structured and unstructured text by converting color and silhouette multi-class labels to binary labels and by using TF-IDF to extract the feature, brand, from the semi-structured text referencing designers or brands. I also used TF-IDF to convert the unstructured user-entered text descriptions to a matrix of TF-IDF features. I extracted the days for which it took the item to sell, by subtracting the date the item sold from the date it was listed. The target variable was the price the item sold for (Note: I excluded all items that sold for $0 (*n* = 3135) and log transformed price). I converted the resulting matrix to a sparse row format by stacking the arrays in sequence horizontally.

## Data Modeling and Validation

I chose to compare two ensemble methods, random forest and gradient boosted regression, because I could not assume obvious linearity between the features and the target variable (the vectorized output from NLP is unlikely to be linear). I chose mean absolute error because it is good for evaluating forecasting accuracy, because it is easily interpreted, and because it gives the same importance to each error and aims at the median. I used the standard deviation of the price of the sold dresses as the baseline to compare with the mean absolute error (Note: I took the exponent of the log transformed output for ease of interpretability). The gradient boosted regression performed better than the random forest on the testing set, with a mean absolute error of $68.31 compared to the baseline of $692.36.

## Web application

To demonstrate the results of this modeling I deployed a web app based on Flask on an EC2 AWS instance which can be found at [Dresstimator Web Application](http://dressappraiser.com) To see a presentation on this project, click [Dresstimator Presentation](https://docs.google.com/presentation/d/1wfMmhb5Js4nReAkyf4XRiZ2JlYkdJpPhDWRJquPTGYA/edit?usp=sharing)
