import json
import logging
import requests
import os
import argparse
import time
import feedparser

from pyhtml2pdf import converter
from usp.tree import sitemap_tree_for_homepage
from authlib.integrations.requests_client import OAuth2Session

token = None
appclient_id = None
appclient_secret = None

def _get_jwt_token(auth_url: str, appclient_id: str, appclient_secret: str):
    """Connect to the server and get a JWT token."""
    token_endpoint = f"{auth_url}/oauth2/token"
    session = OAuth2Session(
        appclient_id, appclient_secret, scope="")
    token = session.fetch_token(token_endpoint, grant_type="client_credentials")
    return token["access_token"]

def crawl_url(url: str, crawl_id: str, customer_id: int, corpus_id: int, idx_address: str, retry: bool = False, prefetched_filename: str = None):
    global token, appclient_id, appclient_secret
    
    filename = str(time.time()) + ".pdf"
    if retry == False or prefetched_filename != None:
        logging.info("Grabbing %s", url)
        r = requests.get(url)
        converter.convert(url, filename)
    else:
        filename = prefetched_filename

    post_headers = {
        "Authorization": f"Bearer {token}"
    }
    files = {
        "file": (f"{crawl_id}-{url}", open(filename, 'rb'), 'application/pdf'),
    }
    response = requests.post(
        f"https://h.{idx_address}/upload?c={customer_id}&o={corpus_id}",
        files=files,
        verify=True,
        headers=post_headers)

    if response.status_code == 401 and retry == False:
        token = _get_jwt_token(auth_url, appclient_id, appclient_secret)
        crawl_url(url, crawl_id, customer_id, corpus_id, idx_address, True, filename)
    elif response.status_code != 200:
        logging.error("REST upload failed with code %d, reason %s, text %s",
                    response.status_code,
                    response.reason,
                    response.text)
        return response, False
    os.remove(filename)
    return response, True

def crawl_rss(feed_url: str, crawl_id: str, customer_id: int, corpus_id: int, idx_address: str):
    feed = feedparser.parse(feed_url)
    for entry in feed['entries']:
        try:
            crawl_url(entry.link, crawl_id, customer_id, corpus_id, idx_address)
        except KeyboardInterrupt:
            raise
        except:
            logging.error("Error crawling %s", entry.link)
    return

def crawl_sitemap(homepage: str, crawl_id: str, customer_id: int, corpus_id: int, idx_address: str):
    tree = sitemap_tree_for_homepage(homepage)
    for page in tree.all_pages():
        try:
            crawl_url(page.url, crawl_id, customer_id, corpus_id, idx_address)
        except KeyboardInterrupt:
            raise
        except:
            logging.error("Error crawling %s", page.url)
    return

if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s", level=logging.INFO)

    parser = argparse.ArgumentParser(description="Vectara web crawler example")

    parser.add_argument("--url", help="The base URL to start crawling from.", required=True)
    parser.add_argument("--crawl-type", help="Can be one of: single-page, sitemap, or recursive.", default="sitemap")

    parser.add_argument("--depth", type=int, help="Maximum depth of pages to crawl", default=1)

    parser.add_argument("--crawl-id", help="ID for the crawl for filtering", default="")

    parser.add_argument("--customer-id", type=int, help="Unique customer ID in Vectara platform.", required=True)
    parser.add_argument("--corpus-id", 
                        type=int, 
                        required=True,
                        help="Corpus ID to which data will be indexed and queried from.")

    parser.add_argument("--indexing-endpoint", help="The endpoint of indexing server.",
                        default="indexing.vectara.io")

    parser.add_argument("--appclient-id", required=True, help="This appclient should have enough rights.")
    parser.add_argument("--appclient-secret", required=True)
    parser.add_argument("--auth-url", help="The auth url for this customer.",
                        default="")

    args = parser.parse_args()

    if args:
        auth_url = args.auth_url
        if auth_url == "":
            auth_url = f"https://vectara-prod-{args.customer_id}.auth.us-west-2.amazoncognito.com"

        appclient_id = args.appclient_id
        appclient_secret = args.appclient_secret
        token = _get_jwt_token(auth_url, appclient_id, appclient_secret)
        
        if token:
            if args.crawl_type == 'single-page':
                error, status = crawl_url(args.url,
                                  args.crawl_id,
                                  args.corpus_id,
                                  args.indexing_endpoint)
            elif args.crawl_type == 'sitemap':
                error, status = crawl_sitemap(args.url,
                                  args.crawl_id,
                                  args.customer_id,
                                  args.corpus_id,
                                  args.indexing_endpoint)
            elif args.crawl_type == 'rss':
                error, status = crawl_rss(args.url,
                                  args.crawl_id,
                                  args.customer_id,
                                  args.corpus_id,
                                  args.indexing_endpoint)
            elif args.crawl_type == 'recursive':
                logging.error("Not yet implemented")
            else:
                logging.error("Provided crawl type is incorrect")

        else:
            logging.error("Could not generate an auth token. Please check your credentials.")
