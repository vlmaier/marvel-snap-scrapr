import requests
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def scrap():
    url = 'https://marvelsnapzone.com/cards'

    chrome_options = Options()
    chrome_options.headless = True
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-gpu')
    browser = webdriver.Chrome(options=chrome_options)
    browser.get(url)
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')
    # only look for link with a 'simple-card' class; those are the cards
    links = soup.findAll('a', {'class': 'simple-card'})

    characters = []
    for link in links:
        character = {
            # capitalize every word
            'name': link['data-name'].title(),
            'cost': link['data-cost'],
            'power': link['data-power'],
            'ability': link['data-ability'],
            # remove query string
            'url': link['data-src'].split('?')[0],
            'status': link['data-status'],
            'source': link['data-source']
        }
        characters.append(character)

    image_urls = []
    for character in characters:
        image_urls.append(character['url'])

    # download_images(image_urls)


def download_images(urls, dir_name='marvel-snap-cards'):
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
        print("Directory '", dir_name, "' created ")
    else:
        print("Directory '", dir_name, "' already exists")

    for url in urls:
        response = requests.get(url)
        if response.status_code:
            # take the last part of the URL as file name
            fp = open(dir_name + '/' + url.rsplit('/', 1)[-1], 'wb')
            fp.write(response.content)
            fp.close()


if __name__ == '__main__':
    scrap()
