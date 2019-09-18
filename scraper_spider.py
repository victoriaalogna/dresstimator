from bs4 import BeautifulSoup
import requests
import selenium
import time
import os

from selenium import webdriver
driver = webdriver.Chrome()

print("Starting scraper spider...")

BASE_URL = "https://www.vitaminshoppe.com"

# Load main page
primary_page = BASE_URL + "/c/pre-workout/N-cp99jb"
driver.get(primary_page)

# Fetch the HTML source code
html = driver.page_source
# Make a nice bowl of soup
soup = BeautifulSoup(html, 'lxml')

print("Starting pagination...")

# Creat a list for all pagination pages
pagination_links = soup.find_all('div', {'class' : 'victory-pagination'})
page_urls = set()

# Loop the pagination
for pagination_link in pagination_links:
    # Fetch each page link
    pagination_href = pagination_link.find_all('a', href=True)
    for pagination_href_link in pagination_href:
        page_href = pagination_href_link["href"]
        full_url = BASE_URL + page_href
        page_urls.add(full_url)

time.sleep(2)

# Create a set for product URLs
product_urls = set()

# Loop each page 
for page_url in page_urls:
    print(">>> Page URL:", page_url)
    driver.get(page_url)

    # Fetch the HTML source code
    html = driver.page_source

    # Make a nice bowl of soup
    soup = BeautifulSoup(html, 'lxml')


    # Fetch the product HTML boxes on the page
    product_detail_boxes = soup.find_all('div', {'class' : 'product-detail-main'})

    # Loop the found products HTML code
    for product_html in product_detail_boxes:
        # Fetch the first a href link
        product_page_link = product_html.find_all('a', href=True)[0]
        print("  >", product_page_link["href"])
        product_urls.add(product_page_link["href"])

    time.sleep(5)

# Loop each product URL
for product_url in product_urls:
    print(">>> Extracting page source...", product_url)
    product_full_url = BASE_URL + product_url
    temp_list = product_url.split("/")
    product_code = temp_list[len(temp_list)-1]
    driver.get(product_full_url)

    # Fetch the HTML source code
    html = driver.page_source

    # Make a nice bowl of soup
    soup = BeautifulSoup(html, 'lxml')

    out_fi_name = product_code + ".html"
    out_fi_path = os.path.join("html", out_fi_name)
    with open(out_fi_path, "w") as f:
        f.write(html)

    time.sleep(5)



