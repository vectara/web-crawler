# Vectara Web Crawler
This is a Web Crawler for [Vectara](https://vectara.com)

## About
The web crawler currently has 4 modes of operation:
1. Single URL
2. Sitemap
3. RSS
4. Recursive

For the former, provide the crawler with a URL and it will ingest it into
Vectara.  For the latter, provide the crawler with a root page, and it will
retrieve the sitemap(s) and index all links from the sitemap.

## Dependencies
This crawler has a minimum set of python dependencies, as outlined in
[requirements.txt](requirements.txt).

If you're using a fresh MacOS laptop, you'll likely need to install the following:
```
pip3 install requests
pip3 install feedparser
pip3 install bloom_filter
pip3 install selenium
pip3 install webdriver_manager
pip3 install pyhtml2pdf
pip3 install usp
pip3 install ultimate_sitemap_parser
pip3 install authlib
```

## Setup and Requirements
The crawler generates PDFs for each page to upload to Vectara's
[file upload API](https://docs.vectara.com/docs/indexing-apis/file-upload).
The crawler relies on [headless browsers](https://en.wikipedia.org/wiki/Headless_browser)
to both extract links and to generate these PDFs.  This allows for realistic text
rendering, even of javascript-heavy websites.  Chrome/Chromium is required for
link extraction, and there are currently 2 supported headless browsers for PDF
generation, each with their own tradeoffs:

1. `pyhtml2pdf` which in turn uses headless Chrome for rendering.  You will
either need to install Chrome locally or keep a copy of
[chromedriver](https://chromedriver.chromium.org/downloads) in your `PATH`.
2. `wkhtmltopdf` which uses Qt WebKit for rendering.  It's highly recommended
that you download a [precompiled wkhtmltopdf binary](https://wkhtmltopdf.org/downloads.html)
and add it to your `PATH` (as opposed to trying to install wkhtmltopdf via a
package manager)

Unfortunately no website PDF rendering system is perfect, though for the
purposes of neural search, it generally doesn't need to be: you just need to make
sure the right text is rendered in roughly the right order.

`wkhtmltopdf` tends to do a pretty good job of this task but doesn't handle URL
fragments (things after `#` in the URL), so crawls using `wkhtmltopdf` will
remove any URL fragment from the document ID when submitted to Vectara.
`wkhtmltopdf` also can be insecure, so either keep the process sandboxed or
only run it on sites that you trust.

`pyhtml2pdf` (and Chrome) generally produce more accurate colors and
positioning of rendering than `wkhtmltopdf` though for the purposes of neural
text search these generally do not matter.  Unfortunately, the _visual_
accuracy can sometimes yield _programmatic_ inaccuracies where certain elements
of the PDF blocks are located in the wrong place.

In general, if you have full access to the content and/or have the ability to
do more bespoke content extraction, it will yield better results than a generic
web crawler, and Vectara maintains [a full text/metadata indexing API](https://docs.vectara.com/docs/indexing-apis/indexing)
as well for those users.

## Usage
`python3 crawler.py [parameters]`

Parameters are:

| Parameter                  | Required? | Description                                                      | Default
|:--------------------------:|:---------:|:----------------------------------------------------------------:|:-------:
| url                        | Yes       | The starting URL, domain, or homepage                            | N/A
| crawl-type                 | No        | single-page, rss, sitemap, or recursive                          | single-page
| pdf-driver                 | No        | What to convert pages to PDFs. chrome or wkhtmltopdf             | chrome
| (no-)install-chrome-driver | No        | Whether or not to install the Chrome driver for extracting links | --install-chrome-driver
| depth                      | No        | Maximum depth to discover and crawl links                        | 3
| crawl-pattern              | No        | Optional regular expression to stick the crawl to                | .* (all URLs)
| customer-id                | Yes       | Your Vectara customer ID                                         | N/A
| corpus-id                  | Yes       | Your Vectara corpus ID                                           | N/A
| appclient-id               | Yes       | OAuth 2.0 client ID to index content                             | N/A
| appclient-secret           | Yes       | OAuth 2.0 client ID to secret content                            | N/A
| customer-id                | Yes       | Your Vectara customer ID                                         | N/A
| auth-url                   | No        | OAuth2 authentication URL                                        | Defined by your account
| indexing-endpoint          | No        | OAuth2 authentication URL                                        | api.vectara.com

### With staging
To index documents on the staging server, you'll need to set these parameters:

```sh
--auth-url https://vectara-prod-{CUSTOMER_ID}.auth.us-west-2.amazoncognito.com --indexing-endpoint h.indexing.vectara.dev
```

## License
This code is licensed Apache 2.0.  For more details, see the [license file](LICENSE)
