from random import random

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import shutil
import requests
from PIL import Image
import io

target_dir = 'bus'


def load_img(url, directory):
    response = requests.get(url, stream=True)
    if url.split('.')[-1] in ['jpg', 'jpeg', 'png']:
        with open(f"{directory}/{time.time_ns()}.{url.split('.')[-1]}", 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
    else:
        image = Image.open(io.BytesIO(response.content))
        image.save(f"{directory}/{time.time_ns()}.png", "PNG")

    del response


def load_current(browser, source):
    # source = browser.page_source
    soup = BeautifulSoup(source, 'lxml')
    previews = ['https://yandex.ru' + x['href'] for x in soup.find_all('a', {'class': 'serp-item__link'})]
    print(len(previews))
    for preview in previews:
        try:
            browser.get(preview)
            p = browser.page_source
            s = BeautifulSoup(p, 'lxml')
            img_src = s.find('img', {'class': 'MMImage-Origin'})['src']
            if img_src.startswith('//'):
                img_src = 'https:' + img_src
            print(img_src)
            load_img(img_src, 'bus')
        except:
            print('error loading ' + preview)


def load_for_city(city):
    browser = webdriver.Edge()
    browser.set_window_size(1024, 768)

    url = 'https://yandex.ru/images/search?text=автобусы ' + city

    browser.get(url)
    time.sleep(1)
    prev_body = None
    save_link = ''
    prev = ''
    new = ''
    no_result_scroll_in_row = 0
    element = ''
    while True:
        # индикатор загрузки новой страницы
        if element != browser.find_element(By.TAG_NAME, 'body') and prev_body:
            load_current(browser, prev_body)
            browser.get(save_link)
        # print(element == browser.find_element(By.TAG_NAME, 'body'))
        element = browser.find_element(By.TAG_NAME, 'body')
        element.send_keys(Keys.PAGE_DOWN)
        time.sleep(1 * random() + 1)
        new = browser.page_source
        if prev == new:
            no_result_scroll_in_row += 1
        else:
            no_result_scroll_in_row = 0

        prev = new

        if browser.find_elements(By.CLASS_NAME, 'button2__text')[-1].text == 'Ещё картинки':
            save_link = browser.find_elements(By.CLASS_NAME, 'button2_type_link')[-1].get_attribute('href')
            print(save_link)
            prev_body = browser.page_source
            browser.get(save_link)
            time.sleep(2)
        else:
            if not (no_result_scroll_in_row == 10):
                continue
            load_current(browser, browser.page_source)
            print('Всё!')
            break  # к новому городу


def main():
    cities = ['Москва', 'Санкт-Петербург', 'Казань', 'Владивосток', 'Владимир', 'Нижний Новгород', 'Самара', 'Пермь',
              'Ярославль', "Якутск"]
    for city in cities:
        load_for_city(city)


main()
