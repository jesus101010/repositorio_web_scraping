import argparse
import logging
import re
logging.basicConfig(level=logging.INFO)

##texto
import news_page_objects as news
from common import config
from requests.exceptions import HTTPError
from urllib3.exceptions import MaxRetryError

is_well_formed_link = re.compile(r'^https?://.+/.+$')
is_root_path = re.compile(r'^/.+$')

logger = logging.getLogger(__name__)

def _news_scraper(news_site_vid):
    host = config()['news_sites'][news_site_vid]['url']

    logging.info(f'Beginning scrape for {host}')
    homepage = news.HomePage(news_site_vid, host)

    articles = []
    for link in homepage.article_links:
        article = _fetch_article(news_site_vid, host, link)

        if article:
            logger.info('Article fetched!!')
            articles.append(article)
            print(article.title)
    print(len(articles))

def _build_link(host, link):
    if is_well_formed_link.match(link):
        return link
    elif is_root_path.match(link):
        return f'{host}{link}'
    else:
        return f'{host}/{link}'

def _fetch_article(news_site_vid, host, link):
    logger.info(f'Start fetching article at {link}')

    article = None

    try:
        article = news.ArticlePages(news_site_vid, _build_link(host, link))
    except (HTTPError, MaxRetryError) as e:
        logger.warning('Error while fetching the article', exc_info=False)

    if article and not article.body:
        logger.warning('Invalid article, There is no body')
        return None
    return article

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    news_sites_choices = list(config() ['news_sites'].keys())
    parser.add_argument('news_site',
                        help ='The news sites that you want to scrape',
                        type=str,
                        choices=news_sites_choices)

    args = parser.parse_args()
    _news_scraper(args.news_site) 
