# dresstimator - scraper

This package contains the code to scrape (extract) information from the eBay Developers API. Specifically, the Finding API is used to extract data for completed sales of wedding dresses.

## Quick Start

The instructions below summarize how to use the scraper tools to extract item data from the eBay API:

```
# Create the virtual environment
virtualenv venv-scraper

# Enable the virtual environment
source venv-scraper/bin/activate

# Install the required Python packages
pip3 install -r requirements.txt
```

## Configuring the `ebaysdk` Package

This project uses the [Python `ebaysdk`](https://github.com/timotheus/ebaysdk-python) to provide a programmatic interface into the eBay APIs. To use this package, and the eBay API, you must have an eBay Developer account, and an API key. The API key information needs to be added to the `ebay.yaml` file for both the Finding API (`svcs.ebay.com`) and the Shopping API (`open.api.ebay.com`). This package includes the default file from the Python `ebaysdk` for convenience.

## Summary of Programs

There is a selection of scripts required to extract data effectively and efficiently from the eBay API:

- `scraper_find_complete_items.py`: This script queries the eBay Finding API for all auctions that have officially been _completed_ using the `findCompletedItems()` API endpoint. Since this query does not fetch all item details, only the eBay `ItemID` number is saved for another future query. This query can extract 100 items at a time, resulting in minimizing API calls. The item ID numbers are saved to the `extracted_items.json` file.
- `scraper_get_item_details.py`: This script uses the extracted item ID numbers and performs a full item lookup using the eBay Shopping API endpoint named `GetMultipleItems()`. This query returns the full auction details as well as the `ItemSpecifics` and `TextDescription`. This query can extract 20 items at a time. For each item, the JSON is exported to the `extracted_items` folder. If an item has been extracted in a past data dump, it is not processed again.
- `scraper_clean_data.py`: This script cleans the data, flattens the nested JSON structure and extracts the `ItemSpecifics` and puts them is a new JSON property. All cleaned item JSON files are saved in the `extracted_items_clean` folder.
- `scraper_combine_JSON.py`: This script combines all extracted and cleaned items into a single JSON file (`all_json_data.json`) for testing.

## Data Update Process

If new data needs to be added, simply run the following scripts:

```
python3 scraper_find_complete_items.py
python3 scraper_get_item_details.py
python3 scraper_clean_data.py
```

## Example of Raw Data Output

A reference example of the raw output from the eBay API is provided below:

```
{
    "BestOfferEnabled":"true",
    "Description":"Wedding Dress A-line with a halter strap neckline. Floor length. Has beading and applique. Ivory in color Fits 14/16 Womens Excellent condition. No rips. No snags. Needs to be cleaned and pressed.",
    "ItemID":"111757387725",
    "EndTime":"2019-09-13T03:29:24.000Z",
    "StartTime":"2015-08-29T18:04:25.000Z",
    "ViewItemURLForNaturalSearch":"https://www.ebay.com/itm/Wedding-Dress-Gown-/111757387725",
    "ListingType":"FixedPriceItem",
    "Location":"Modesto, California",
    "PaymentMethods":"PayPal",
    "GalleryURL":"https://thumbs2.ebaystatic.com/pict/1117573877258080_2.jpg",
    "PictureURL":[
        "https://i.ebayimg.com/00/s/MTU5OFg4NDk=/z/h~wAAOSw7a9c0f2P/$_12.JPG?set_id=880000500F",
        "https://i.ebayimg.com/00/s/MTU5OVg4MDc=/z/xFEAAOSwikNc0f2c/$_12.JPG?set_id=880000500F",
        "https://i.ebayimg.com/00/s/MTU5OVg4NDg=/z/OJEAAOSwcgNc0f2s/$_12.JPG?set_id=880000500F",
        "https://i.ebayimg.com/00/s/MTYwMFg3MTE=/z/PPEAAOSw6fBc0f26/$_12.JPG?set_id=880000500F"
    ],
    "PostalCode":"95350",
    "PrimaryCategoryID":"15720",
    "PrimaryCategoryName":"Clothing, Shoes & Accessories:Wedding & Formal Occasion:Wedding Dresses",
    "Quantity":"1",
    "Seller":{
        "UserID":"norris72",
        "FeedbackRatingStar":"None",
        "FeedbackScore":"3",
        "PositiveFeedbackPercent":"100.0"
    },
    "BidCount":"0",
    "ConvertedCurrentPrice":{
        "_currencyID":"USD",
        "value":"45.0"
    },
    "CurrentPrice":{
        "_currencyID":"USD",
        "value":"45.0"
    },
    "HighBidder":{
        "UserID":"i***o",
        "FeedbackPrivate":"false",
        "FeedbackRatingStar":"None",
        "FeedbackScore":"0"
    },
    "ListingStatus":"Completed",
    "QuantitySold":"1",
    "ShipToLocations":[
        "US"
    ],
    "Site":"US",
    "TimeLeft":"PT0S",
    "Title":"Wedding Dress / Gown",
    "ItemSpecifics":{
        "NameValueList":[
            {
                "Name":"Size Type",
                "Value":"womens"
            },
            {
                "Name":"Size (Women's)",
                "Value":"16W"
            },
            {
                "Name":"Detailing",
                "Value":[
                    "Beading",
                    "Sequin"
                ]
            },
            {
                "Name":"Sleeve Style",
                "Value":"Sleeveless"
            },
            {
                "Name":"Neckline",
                "Value":"Halter Neck"
            },
            {
                "Name":"Dress Length",
                "Value":"Full-Length"
            },
            {
                "Name":"Color",
                "Value":"Ivory"
            }
        ]
    },
    "HitCount":"317",
    "PrimaryCategoryIDPath":"11450:3259:15720",
    "Country":"US",
    "ReturnPolicy":{
        "ReturnsAccepted":"ReturnsNotAccepted"
    },
    "AutoPay":"true",
    "IntegratedMerchantCreditCardEnabled":"false",
    "HandlingTime":"3",
    "ConditionID":"3000",
    "ConditionDisplayName":"Pre-owned",
    "GlobalShipping":"false",
    "ConditionDescription":"Excellent condition. No rips, no snags. Needs to be cleaned and pressed.",
    "QuantitySoldByPickupInStore":"0",
    "NewBestOffer":"false"
}
```

## Example of Cleaned Data Output

A reference example of the cleaned output is provided below:

```
{
    "AutoPay": "true",
    "AvailableForPickupDropOff": "None",
    "BestOfferEnabled": "true",
    "BidCount": "0",
    "BuyItNowAvailable": "None",
    "BuyItNowPrice_currencyID": "None",
    "BuyItNowPrice_value": "None",
    "Charity_CharityID": "None",
    "Charity_CharityName": "None",
    "Charity_CharityNumber": "None",
    "Charity_DonationPercent": "None",
    "Charity_LogoURL": "None",
    "Charity_Mission": "None",
    "Charity_Status": "None",
    "ConditionDescription": "Excellent condition. No rips, no snags. Needs to be cleaned and pressed.",
    "ConditionDisplayName": "Pre-owned",
    "ConditionID": "3000",
    "ConvertedBuyItNowPrice_currencyID": "None",
    "ConvertedBuyItNowPrice_value": "None",
    "ConvertedCurrentPrice_currencyID": "USD",
    "ConvertedCurrentPrice_value": "45.0",
    "Country": "US",
    "CurrentPrice_currencyID": "USD",
    "CurrentPrice_value": "45.0",
    "Description": "Wedding Dress A-line with a halter strap neckline. Floor length. Has beading and applique. Ivory in color Fits 14/16 Womens Excellent condition. No rips. No snags. Needs to be cleaned and pressed.",
    "EligibleForPickupDropOff": "None",
    "EndTime": "2019-09-13T03:29:24.000Z",
    "ExcludeShipToLocation": "None",
    "GalleryURL": "https://thumbs2.ebaystatic.com/pict/1117573877258080_2.jpg",
    "GlobalShipping": "false",
    "HandlingTime": "3",
    "HighBidder_FeedbackPrivate": "false",
    "HighBidder_FeedbackRatingStar": "None",
    "HighBidder_FeedbackScore": "0",
    "HighBidder_UserAnonymized": "None",
    "HighBidder_UserID": "i***o",
    "HitCount": "317",
    "IntegratedMerchantCreditCardEnabled": "false",
    "ItemDetails_Back_Closure": "None",
    "ItemDetails_Color": "Ivory",
    "ItemDetails_Designer_Brand": "None",
    "ItemDetails_Detailing": "Beading,Sequin",
    "ItemDetails_Dress_Length": "Full-Length",
    "ItemDetails_Material": "None",
    "ItemDetails_Neckline": "Halter Neck",
    "ItemDetails_Silhouette": "None",
    "ItemDetails_Size_Type": "womens",
    "ItemDetails_Size_Womens": "16W",
    "ItemDetails_Sleeve_Style": "Sleeveless",
    "ItemDetails_Style": "None",
    "ItemID": "111757387725",
    "ItemSpecifics": "Size Type::womens::Size (Women's)::16W::Detailing::['Beading', 'Sequin']::Sleeve Style::Sleeveless::Neckline::Halter Neck::Dress Length::Full-Length::Color::Ivory::",
    "ListingStatus": "Completed",
    "ListingType": "FixedPriceItem",
    "Location": "Modesto, California",
    "LotSize": "None",
    "MinimumToBid_currencyID": "None",
    "MinimumToBid_value": "None",
    "PaymentAllowedSite": "None",
    "PaymentMethods": "PayPal",
    "PictureURL": [
        "https://i.ebayimg.com/00/s/MTU5OFg4NDk=/z/h~wAAOSw7a9c0f2P/$_12.JPG?set_id=880000500F",
        "https://i.ebayimg.com/00/s/MTU5OVg4MDc=/z/xFEAAOSwikNc0f2c/$_12.JPG?set_id=880000500F",
        "https://i.ebayimg.com/00/s/MTU5OVg4NDg=/z/OJEAAOSwcgNc0f2s/$_12.JPG?set_id=880000500F",
        "https://i.ebayimg.com/00/s/MTYwMFg3MTE=/z/PPEAAOSw6fBc0f26/$_12.JPG?set_id=880000500F"
    ],
    "PostalCode": "95350",
    "PrimaryCategoryID": "15720",
    "PrimaryCategoryIDPath": "11450:3259:15720",
    "PrimaryCategoryName": "Clothing, Shoes & Accessories:Wedding & Formal Occasion:Wedding Dresses",
    "Quantity": "1",
    "QuantityAvailableHint": "None",
    "QuantitySold": "1",
    "QuantitySoldByPickupInStore": "0",
    "QuantityThreshold": "None",
    "ReserveMet": "None",
    "ReturnPolicy_Description": "None",
    "ReturnPolicy_InternationalRefund": "None",
    "ReturnPolicy_InternationalReturnsAccepted": "None",
    "ReturnPolicy_InternationalReturnsWithin": "None",
    "ReturnPolicy_InternationalShippingCostPaidBy": "None",
    "ReturnPolicy_Refund": "None",
    "ReturnPolicy_ReturnsAccepted": "ReturnsNotAccepted",
    "ReturnPolicy_ReturnsWithin": "None",
    "ReturnPolicy_ShippingCostPaidBy": "None",
    "SecondaryCategoryID": "None",
    "SecondaryCategoryIDPath": "None",
    "SecondaryCategoryName": "None",
    "Seller_FeedbackRatingStar": "None",
    "Seller_FeedbackScore": "3",
    "Seller_PositiveFeedbackPercent": "100.0",
    "Seller_TopRatedSeller": "None",
    "Seller_UserID": "norris72",
    "ShipToLocations": [
        "US"
    ],
    "Site": "US",
    "StartTime": "2015-08-29T18:04:25.000Z",
    "Storefront_StoreName": "None",
    "Storefront_StoreURL": "None",
    "Subtitle": "None",
    "TimeLeft": "PT0S",
    "Title": "Wedding Dress / Gown",
    "ViewItemURLForNaturalSearch": "https://www.ebay.com/itm/Wedding-Dress-Gown-/111757387725"
}
```
