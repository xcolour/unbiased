import re

from unbiased.sources.base import NewsSource

class NBC(NewsSource):

    name = 'NBC News'
    shortname = 'nbc'
    url = 'https://www.nbcnews.com/'

    bad_urls = ['/opinion/']

    @classmethod
    def _fetch_urls(cls):
        soup = cls._fetch_content(cls.url)

        articles = soup.find_all('article', class_='teaseCard')
        article_links = [x.find('a', class_=re.compile('pictureLink__.*')) for x in articles]
        article_links = [x['href'] for x in article_links if x is not None]

        h1s = tuple(article_links[:3])
        h2s = tuple(article_links[3:])

        pancake_headlines = soup.find('section', class_='pancake')\
                .find_all('h3')

        h3s = tuple([x.find('a')['href'] for x in pancake_headlines])

        return h1s, h2s, h3s
