from bs4 import BeautifulSoup
import requests
import selenium
import time
import os

from selenium import webdriver
driver = webdriver.Chrome()

print("Starting scraper spider...")

BASE_URL = "https://www.bravobride.com"

# Load main page
primary_page = BASE_URL + "/wedding-categories/dresses"
driver.get(primary_page)

# Fetch the HTML source code
html = driver.page_source
# Make a nice bowl of soup
soup = BeautifulSoup(html, 'lxml')

print("Starting pagination...")

# Creat a list for all pagination pages
pagination_links = soup.find_all('div', {'class' : 'PaginationHolder'})
page_urls = set()

# Loop the pagination
for pagination_link in pagination_links:
    # Fetch each page link
    pagination_href = pagination_link.find_all('a', href=True)
    for pagination_href_link in pagination_href:
        page_href = pagination_href_link["href"]
        full_url = primary_page + page_href # print base_url
        page_urls.add(full_url)

time.sleep(2)

# Loop each page 
for page_url in page_urls:
    print(">>> Page URL:", page_url)
    driver.get(page_url)

    # Fetch the HTML source code
    html = driver.page_source

    # Make a nice bowl of soup
    soup = BeautifulSoup(html, 'lxml')

    # Fetch the product HTML boxes on the page
    product_detail_boxes = soup.find_all('div', {'class' : 'SearchResultsHolder'})

    # Loop the found products HTML code
    for product_html in product_detail_boxes:
        # Fetch the first a href link
        product_page_link = product_html.find_all('a', href=True)[0]
        print("  >", product_page_link["href"])
        product_urls.add(product_page_link["href"])

    time.sleep(5)
