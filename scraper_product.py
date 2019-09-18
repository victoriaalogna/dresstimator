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
primary_page = BASE_URL + "/p/b-nox-reloaded-power-punch-14-1-oz-powder/u3-1132"
driver.get(primary_page)

# Fetch the HTML source code
html = driver.page_source
# Make a nice bowl of soup
soup = BeautifulSoup(html, 'lxml')

print("Starting extracting product reviews, images, ingredient etc...")

# Creat a list for all pagination pages
reviews_data = soup.find_all('div', {'class' : 'TTreviews'})
# HINT: TTreviews

# Loop the pagination
for reviews in reviews_data:
    print(reviews_data)
    # Fetch each page link
    # pagination_href = pagination_link.find_all('a', href=True)
    # for pagination_href_link in pagination_href:
    #     page_href = pagination_href_link["href"]
    #     full_url = BASE_URL + page_href
    #     page_urls.add(full_url)