# ![build](https://github.com/vlmaier/marvel-snap-scrapr/actions/workflows/build.yml/badge.svg)

## Marvel SNAP Scrapr

Scraper for <https://marvelsnapzone.com> to retrieve metadata of Marvel SNAP cards.

### How does it work?

The origin version used to scrap the website and pull out the card metadata from the HTML page including the image URL.

The new version uses the [API endpoint](https://marvelsnapzone.com/getinfo/?searchtype=cards&searchcardstype=true) (found by [@mlilback](https://github.com/mlilback)) to retrieve the data in JSON format. The API endpoint is used by the website to retrieve the data as well. Since JSON is already structured data, it is much easier to parse and extract the data.
