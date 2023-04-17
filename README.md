![](https://github.com/vlmaier/marvel-snap-scrapr/actions/workflows/build.yml/badge.svg)

# Marvel SNAP Scrapr

Scraper for https://marvelsnapzone.com to retrieve metadata of Marvel SNAP cards.

## How does it work?

The script uses the Beautiful Soup Python library, which pulls data out of HTML or XML files.
It scraps the website https://marvelsnapzone.com which is well-structured and provides all required metadata about Marvel SNAP cards.
Selenium web driver is required because of the dynamic loading on the website. Otherwise, the card links are not available when going for a static approach.
In the end, a list of dictionaries is created for all available cards. It can be used elsewhere to create a custom card database.

If you only want to download the images then uncomment the `download_images()` function call.
