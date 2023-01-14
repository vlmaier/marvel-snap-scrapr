import re
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
            # strip html tags and capitalize
            'ability': capitalize(BeautifulSoup(link['data-ability'], 'html.parser').text),
            # remove query string
            'url': link['data-src'].split('?')[0],
            'status': link['data-status'],
            'source': link['data-source']
        }
        characters.append(character)
        # print(character)

    image_urls = []
    for character in characters:
        image_urls.append(character['url'])

    # download_images(image_urls)

    return characters


def capitalize(text):
    punc_filter = re.compile('([.!?;:]\s*)')
    split_with_punctuation = punc_filter.split(text)
    for i, j in enumerate(split_with_punctuation):
        if len(j) > 1:
            split_with_punctuation[i] = j[0].upper() + j[1:]
    text = ''.join(split_with_punctuation)
    return text


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


def create_cards(cards):
    url = 'http://localhost:8080/v1/cards'
    for card in cards:
        if card['status'] == 'released':
            body = {
                'name': parse_name(card['name']),
                'cost': card['cost'],
                'power': card['power'],
                'ability': parse_ability(card['name'], card['ability']),
                'series': parse_source(card['source']),
                'imageUrl': card['url']
            }
            requests.post(url, json=body)
            print(body)
            # print(card['name'] + ' created.')


def parse_name(name):
    # character name manual fix
    if name == 'Ant Man':
        return 'Ant-Man'
    elif name == 'Jane Foster Mighty Thor':
        return 'Jane Foster The Mighty Thor'
    elif name == 'Miles Morales':
        return 'Miles Morales: Spider-Man'
    elif name == 'Super-Skrull':
        return 'Super Skrull'
    return name


def parse_ability(name, ability):
    # provide 'No ability' instead of empty string
    if ability == '':
        ability = 'No ability'
    # The Collector ability manual fix
    if name == 'The Collector':
        ability = 'When a card enters your hand from anywhere (except your deck), +1 power.'
    # all following words should be shown in bold
    bold_candidates = ["On Reveal", "Ongoing", "Widow's Bite", "Rock", "Rocks", "Doombot", "Squirrel", "Demon", "Drone",
                       "Mjolnir", "Tiger", "Limbo", "No ability"]
    for candidate in bold_candidates:
        if ability.lower().__contains__(candidate.lower()):
            ability = re.sub(candidate.lower(), "<span class='fw-bold'>" + candidate + "</span>", ability,
                             flags=re.IGNORECASE)
    for i in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
        # +[1-9] should be shown in bold and green color
        ability = re.sub("[+][" + i + "]", "<span class='fw-bold' style='color: green;'>+" + i + "</span>", ability)
        # -[1-9] should be shown in bold and red color
        ability = re.sub("[-][" + i + "]", "<span class='fw-bold' style='color: red;'>-" + i + "</span>", ability)
    return ability


def parse_source(source):
    if source.__contains__('Collection Level 1-14') or source.__contains__('Starter Card') or source.__contains__('Recruit Season'):
        return 'Starter'
    elif source.__contains__('Pool 1'):
        return 'Series 1'
    elif source.__contains__('Pool 2'):
        return 'Series 2'
    elif source.__contains__('Pool 3'):
        return 'Series 3'
    elif source.__contains__('Pool 4'):
        return 'Series 4'
    elif source.__contains__('Pool 5'):
        return 'Series 5'
    elif source.__contains__('Season Pass'):
        return 'Season Pass'
    else:
        return ''


if __name__ == '__main__':
    characters = scrap()
    # create_cards(characters)
