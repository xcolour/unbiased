
from unbiased.sources.base import NewsSource

class TheHill(NewsSource):

    name = 'The Hill'
    shortname = 'Hill'
    url = 'http://thehill.com'

    bad_titles = ['THE MEMO']
    bad_authors = ['Matt Schlapp', 'Juan Williams', 'Judd Gregg']

    @classmethod
    def _fetch_urls(cls):
        soup = cls._fetch_content(cls.url)

        h1 = soup.find('h1', class_='top-story-headline')\
            .find('a')['href']
        h1s = (h1,)

        h23s = soup.find('div', class_='section-top-content')\
                  .find_all('div', class_='top-story-item')
        h2s = set([x.h4.a['href'] for x in h23s if 'small' not in x['class']])
        h2s = tuple(h2s)

        h3s = set([x.h4.a['href'] for x in h23s if 'small' in x['class']])
        h3s = tuple(h3s)

        return h1s, h2s, h3s

    @classmethod
    def _get_description(cls, soup):
        try:
            return NewsSource._get_description(soup)
        except Exception:
            # fall back on grabbing text from the article
            desc = soup.find('div', class_='field-items')
            return desc.text[:200].rsplit(' ', 1)[0]
