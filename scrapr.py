from concurrent.futures import ThreadPoolExecutor
import requests
import os
from datetime import datetime
from PIL import Image

CARDS_API_URL = 'https://marvelsnapzone.com/getinfo/?searchtype=cards&searchcardstype=true'
LOCATIONS_API_URL = 'https://marvelsnapzone.com/getinfo/?searchtype=locations&searchcardstype=true'
ROOT_DIR = 'marvel-snap'
CARDS_DIR = 'cards'
VARIANTS_DIR = 'variants'
LOCATIONS_DIR = 'locations'


def get_cards(url: str = CARDS_API_URL):
    """
    Retrieves a list of cards from the Marvel SNAP Zone API.

    Returns:
        A list of cards, where each card is represented as a dictionary.
    """
    print("[%s] %s" %
          (datetime.now(), f"Starting retrieving cards from {url}"))
    response = requests.get(url)

    if response.status_code == 200:
        json_data = response.json()
        success = json_data.get("success", {})
        print("[%s] %s" % (datetime.now(), "Finished retrieving cards."))
        return success.get("cards", [])
    else:
        print(f"Error: Request failed with status code {response.status_code}")


def download_images(urls, dir: str = ROOT_DIR):
    """
    Downloads images from the given URLs and stores them in the given directory.

    Args:
        urls: A list of URLs to download images from.
        dir: The directory to store the images in.
    """

    def download_image(url, dir: str = ROOT_DIR):
        try:
            file_name = url.rsplit('/', 1)[-1].rsplit('?', 1)[0]
            file_path = os.path.join(dir, file_name)
            png_file_path = os.path.splitext(file_path)[0] + ".png"

            if os.path.exists(png_file_path):
                print(
                    f"File {png_file_path} already exists. Skipping download.")
                return

            temp_file_path = file_path + ".webp"
            with open(temp_file_path, 'wb') as file:
                print("[%s] %s" %
                      (datetime.now(), f"Download image from {url}"))
                response = requests.get(url)
                response.raise_for_status()
                file.write(response.content)

            image = Image.open(temp_file_path)
            image.save(png_file_path, "PNG")

        except requests.exceptions.RequestException as e:
            print("[%s] %s" % (datetime.now(),
                  f"Error downloading image from URL '{url}': {e}"))

        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    with ThreadPoolExecutor(max_workers=5) as executor:
        for url in urls:
            executor.submit(download_image, url, dir)
        print("[%s] %s" %
                  (datetime.now(), f"Finished downloading. Check '{dir}' directory."))


def create_directories():
    """
    Creates the directories for the card images.

    ROOT_DIR
    ├── CARDS_DIR
    ├── LOCATIONS_DIR
    └── VARIANTS_DIR

    """
    if not os.path.exists(ROOT_DIR):
        os.mkdir(ROOT_DIR)

    directories = [CARDS_DIR, VARIANTS_DIR, LOCATIONS_DIR]

    for directory in directories:
        path = os.path.join(ROOT_DIR, directory)
        if not os.path.exists(path):
            os.mkdir(path)


if __name__ == '__main__':
    cards = get_cards()
    card_image_urls = [card['art'] for card in cards]
    variant_image_urls = [variant['art']
                          for card in cards for variant in card.get('variants', [])]

    locations = get_cards(LOCATIONS_API_URL)
    location_image_urls = [location['art'] for location in locations]

    create_directories()

    download_images(card_image_urls, os.path.join(ROOT_DIR, CARDS_DIR))
    download_images(variant_image_urls, os.path.join(ROOT_DIR, VARIANTS_DIR))
    download_images(location_image_urls, os.path.join(ROOT_DIR, LOCATIONS_DIR))
