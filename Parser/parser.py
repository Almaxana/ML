from selenium import webdriver
from selenium.webdriver.common.by import By
import re
import csv
from dataclasses import dataclass


@dataclass
class Hotel:
    hotel_kind: str
    review_number: int
    metro_distance: float
    center_distance: float
    rating: float
    city_name: str
    price: int
    url: str

    @classmethod
    def from_html(cls, card_element, city_name, hotel_kind, deep_card_driver):
        rating = cls.fetch_rating(card_element)
        center_distance, metro_distance = cls.fetch_distances(card_element)
        price = cls.fetch_price(card_element)
        url = cls.fetch_deep_card_url(card_element)
        if url is None:
            return None
        review_number = cls.fetch_review_number(deep_card_driver, url)

        if rating is None or center_distance is None or metro_distance is None or price is None or review_number is None:
            return None

        if hotel_kind == '':
            hotel_kind = 'hotel'
        else:
            hotel_kind = hotel_kind[1:-1]

        return Hotel(
            city_name=city_name,
            price=price,
            rating=rating,
            center_distance=center_distance,
            metro_distance=metro_distance,
            hotel_kind=hotel_kind,
            url=url,
            review_number=review_number
        )

    @staticmethod
    def fetch_price(card_element):
        try:
            price_text = card_element.find_element(By.CLASS_NAME, 'HotelCard_ratePriceValue__s3HvW').get_attribute(
                'textContent')
            return int(re.sub(r'\D', '', price_text))
        except:
            return None

    @staticmethod
    def fetch_rating(card_element):
        try:
            rating_text = card_element.find_element(By.CLASS_NAME, 'TotalRating_content__k5u6S').get_attribute(
                'textContent')
            return float(rating_text.replace(',', '.'))
        except:
            return None

    @staticmethod
    def fetch_distances(card_element):
        try:
            distances = [distance.get_attribute('textContent') for distance in
                         card_element.find_elements(By.CLASS_NAME, 'HotelCard_distanceValue__TbHp_')]
            if len(distances) < 2:
                return None, None
            center_distance = Hotel.get_float_distance(distances[0])
            metro_distance = Hotel.get_float_distance(distances[1])
            return center_distance, metro_distance
        except:
            return None

    @staticmethod
    def get_float_distance(distance_text):
        if distance_text.endswith('км'):
            return float(re.sub(r'[^0-9,.]', '', distance_text).replace(',', '.'))
        else:
            return float(re.sub(r'\D', '', distance_text)) / 1000

    @staticmethod
    def fetch_deep_card_url(card_element):
        try:
            return card_element.find_element(By.CLASS_NAME, 'HotelCard_title__cpfvk').find_element(By.TAG_NAME, 'a').get_attribute('href')
        except:
            return None

    @staticmethod
    def fetch_review_number(deep_card_driver, url):
        deep_card_driver.get(url)
        try:
            review_number_text = deep_card_driver.find_element(By.CLASS_NAME, 'Rating_totalReviews__Mpxdg').get_attribute('textContent')
            return int(re.sub(r'\D', '', review_number_text))
        except:
            return None

    def print_to_csv(self, writer):
        writer.writerow([self.price, self.city_name, self.rating, self.center_distance, self.metro_distance, self.review_number, self.hotel_kind])


driver = webdriver.Chrome()
deep_card_driver = webdriver.Chrome()

with open("cities_set.txt") as file:
    cities = [row.strip() for row in file]

with open("hotel_kinds_set.txt") as file:
    hotel_kinds = [row.strip() for row in file]

with open('config.txt') as file:
    lines = file.read().splitlines()
constants_dict = {}
for line in lines:
    key, value = line.split(' = ')
    constants_dict.update({key: value})
root_url = constants_dict['root_url']
pages_numer_to_parse = int(constants_dict['pages_numer_to_parse'])


with open('hotels_dataset.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Price', 'City', 'Rating', 'Center_distance_km', 'Metro_distance_km', 'Review_number',
                     'Hotel_kind'])

    i = 0
    for city in cities:
        for hotel_kind in hotel_kinds:
            driver.get(root_url + city + hotel_kind)

            last_page_number = int(driver.find_elements(By.CLASS_NAME, 'Pagination_item__lBv39')[-1].get_attribute('textContent'))
            for page_number in range(1, min(pages_numer_to_parse, last_page_number) + 1):
                driver.get(root_url + city + hotel_kind + '?page=' + str(page_number))

                all_cards = driver.find_elements(By.CLASS_NAME, 'HotelList_card__Gk2_O')
                for card in all_cards:

                    hotel = Hotel.from_html(card, city, hotel_kind, deep_card_driver)
                    if hotel is None:
                        continue

                    hotel.print_to_csv(writer)

deep_card_driver.quit()
driver.quit()

