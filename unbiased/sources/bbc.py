from unbiased.sources.base import NewsSource

class BBC(NewsSource):

    name = 'BBC News'
    shortname = 'bbc'
    url = 'http://www.bbc.com/news/world/us_and_canada'

    bad_images = ['bbc_news_logo.png']

    @classmethod
    def _fetch_urls(cls):
        soup = cls._fetch_content(cls.url)

        h1s = soup.find('div', class_='buzzard-item')\
                .find('a', class_='title-link')
        h1s = (h1s['href'],)

        h2s = soup.find_all('div', attrs={'class': 'pigeon__column', 'data-entityid': True})
        h2s = tuple(x.find('a', class_='title-link')['href'] for x in h2s)

        # get tertiary headlines
        h3s = soup.find_all('div', attrs={'class': 'macaw-item', 'data-entityid': True})
        h3s = tuple(x.find('a', class_='title-link')['href'] for x in h3s)

        return h1s, h2s, h3s

    @classmethod
    def _get_image(cls, soup):
        return soup.find('meta', property='og:image')['content'].replace('branded_news', 'cpsprodpb')
