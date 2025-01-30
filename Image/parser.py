import requests
import csv
import string
from selenium import webdriver
from bs4 import BeautifulSoup
import time


page_urls = ['https://tadance.ru/Competition/Album/5676/',
             'https://tadance.ru/Competition/Album/7330/',
             'https://tadance.ru/Competition/Album/7335/'] # St

# page_urls = ['https://tadance.ru/Competition/Album/7332/',
#              'https://tadance.ru/Competition/Album/7267/',
#              'https://tadance.ru/Competition/Album/7267/'] # La


headers = {
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}

img_num = 1763
for root_page_url in page_urls:
    for i in range(1, 10):
        page_url = f"{root_page_url}{i}"
        print(page_url)

        page_response = requests.get(page_url, headers=headers)
        if page_response.status_code != 200:
            print(f"Failed to fetch: {page_url}, {page_response.status_code}")
            break

        soup = BeautifulSoup(page_response.text, 'html.parser')

        imgs = soup.find_all('img')
        for img in imgs:
            try:
                img_url = img['data-image']
                img_num += 1
            except:
                continue

            with open('imgs_dataset/St/' + str(img_num) + '.jpg', "wb") as f:
                f.write(requests.get(img_url).content)
