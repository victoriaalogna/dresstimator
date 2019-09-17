from bs4 import BeautifulSoup
import requests
import selenium

from selenium import webdriver
driver = webdriver.Chrome()

print("Starting scraper spider...")

# Load main page
driver.get('https://www.vitaminshoppe.com/c/pre-workout/N-cp99jb')

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
    print(product_page_link["href"])
