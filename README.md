# Vectara Web Crawler
This is a Web Crawler for [Vectara](https://vectara.com)

## About
The web crawler currently has 2 modes of operation:
1. Single URL
2. Sitemap

For the former, provide the crawler with a URL and it will ingest it into
Vectara.  For the latter, provide the crawler with a root page, and it will
retrieve the sitemap(s) and index all links from the sitemap.

## Setup
This crawler has a minimum set of python dependencies, as outlined in
[requirements.txt](requirements.txt).  It uses `pyhtml2pdf` which in turn uses
headless Chrome via [Selenium](https://www.selenium.dev/) so you will need to
install a Chromium-based browser (or modify code!) before using this utility.

## Usage
`python3 crawler.py [parameters]`

Parameters are:
- *--url* (Required): The starting URL
- *--appclient-id* (Required): OAuth2 client ID to index content
- *--appclient-secret* (Required): OAuth2 client secret to index content
- *--customer-id* (Required): Your Vectara customer ID
- *--corpus-id* (Required): Your Vectara corpus ID that you want to index contents into
- *--crawl-type*: Can be "single-page" to grab a single page or "sitemap" to
get all contents of a sitemap.  In the future, "recursive" will also be
supported
- *--crawl-id*: Added to the metadata in Vectara so you can filter crawl
results by a particular crawl.  If you want to use this feature, make sure to
add `crawl_id` as a filterable attribute in Vectara
- *--indexing-endpoint*: The Vectara indexing endpoint.  Defaults to
`indexing.vectara.io`
- *--auth-url*: OAuth2 authentication URL.  Only required for accounts with
custom authentication

## License
This code is licensed Apache 2.0.  For more details, see the [license file](LICENSE)