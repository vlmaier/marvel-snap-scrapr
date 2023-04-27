import re
import requests
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from threading import Thread
from datetime import datetime

CARDS_API_URL = "http://localhost:8080/v1/cards"
MARVELSNAPZONE_URL = 'https://marvelsnapzone.com/cards'


def scrap():
    print("[%s] %s" % (datetime.now(), "Starting scraping ..."))

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-gpu')
    browser = webdriver.Chrome(options=chrome_options)
    browser.get(MARVELSNAPZONE_URL)
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # Only look for link with a 'simple-card' class; those are the cards.
    links = soup.findAll('a', {'class': 'simple-card'})

    characters = []
    for link in links:
        character = {
            # Capitalize every word.
            'name': link['data-name'].title(),
            'cost': link['data-cost'],
            'power': link['data-power'],
            # Strip HTML tags and capitalize.
            'ability': capitalize(BeautifulSoup(link['data-ability'], 'html.parser').text),
            # Remove query string.
            'url': link['data-src'].split('?')[0],
            'status': link['data-status'],
            'source': link['data-source']
        }
        characters.append(character)
        print("[%s] %s" % (datetime.now(), f"Found {character['name']}"))

    # TODO: uncomment to download card images.
    image_urls = [character['url'] for character in characters]
    download_images(image_urls)

    return characters


def capitalize(text):
    punctuation_filter = re.compile('([.!?;:]\s*)')
    split_with_punctuation = punctuation_filter.split(text)
    for i, j in enumerate(split_with_punctuation):
        if len(j) > 1:
            split_with_punctuation[i] = j[0].upper() + j[1:]
    text = ''.join(split_with_punctuation)
    return text


def download_images(urls, dir_name='marvel-snap-cards'):
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
        print("[%s] %s" % (datetime.now(), f"Directory '{dir_name}' created."))
    else:
        print("[%s] %s" % (datetime.now(), f"Directory '{dir_name}' already exists."))

    threads = []
    for url in urls:
        threads.append(Thread(target=download_image, args=(url, dir_name)))
        threads[-1].start()
    for thread in threads:
        thread.join()

    print("[%s] %s" % (datetime.now(), f"Finished downloading. Check '{dir_name}' directory."))


def download_image(url, dir_name):
    print("[%s] %s" % (datetime.now(), f"Download image from {url}"))
    try:
        response = requests.get(url)
        response.raise_for_status()
        file_name = url.rsplit('/', 1)[-1]
        file_path = os.path.join(dir_name, file_name)
        with open(file_path, 'wb') as file:
            file.write(response.content)
    except requests.exceptions.RequestException as e:
        print("[%s] %s" % (datetime.now(), f"Error downloading image from URL '{url}': {e}"))


def create_cards(cards):
    for card in cards:
        if card["status"] != "released":
            return

        body = {
            "name": parse_name(card["name"]),
            "cost": card["cost"],
            "power": card["power"],
            "ability": parse_ability(card["name"], card["ability"]),
            "series": parse_source(card["source"]),
            "imageUrl": card["url"],
        }

        response = requests.post(CARDS_API_URL, json=body)
        if response.status_code == requests.codes.created:
            print("[%s] %s" % (datetime.now(), f"Created card: {card['name']}"))
        else:
            print("[%s] %s" % (datetime.now(), f"Failed to create card: {card['name']} - {response.text}"))


def parse_name(name):
    name = name.strip()

    name_mappings = {
        "Ant Man": "Ant-Man",
        "Jane Foster Mighty Thor": "Jane Foster The Mighty Thor",
        "Miles Morales": "Miles Morales: Spider-Man",
        "Super-Skrull": "Super Skrull",
    }

    return name_mappings.get(name, name)


def parse_ability(name, ability):
    ability = ability.strip()

    # Provide 'No ability' instead of empty string.
    if not ability:
        ability = "No ability"

    # The Collector ability manual fix.
    if name == "The Collector":
        ability = "When a card enters your hand from anywhere (except your deck), +1 power."

    # All following words should be shown in bold.
    bold_candidates = [
        "On Reveal",
        "Ongoing",
        "Widow's Bite",
        "Rock",
        "Rocks",
        "Doombot",
        "Squirrel",
        "Demon",
        "Drone",
        "Mjolnir",
        "Tiger",
        "Limbo",
        "No ability",
    ]

    for candidate in bold_candidates:
        if candidate.lower() in ability.lower():
            ability = re.sub(
                candidate.lower(),
                f"<span class='fw-bold'>{candidate}</span>",
                ability,
                flags=re.IGNORECASE,
            )

    for i in range(1, 10):
        # +[1-9] should be shown in bold and green color.
        # -[1-9] should be shown in bold and red color.
        ability = re.sub(
            fr"[+][{i}]",
            f"<span class='fw-bold' style='color: green;'>+{i}</span>",
            ability,
        )


def parse_source(source):
    series_map = {
        'Collection Level 1-14': 'Starter',
        'Starter Card': 'Starter',
        'Recruit Season': 'Starter',
        'Pool 1': 'Series 1',
        'Pool 2': 'Series 2',
        'Pool 3': 'Series 3',
        'Pool 4': 'Series 4',
        'Pool 5': 'Series 5',
        'Season Pass': 'Season Pass'
    }
    for key in series_map:
        if key in source:
            return series_map[key]
    return ''


if __name__ == '__main__':
    characters = scrap()
    # create_cards(characters)
