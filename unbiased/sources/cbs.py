from unbiased.sources.base import NewsSource

class CBS(NewsSource):

    name = 'CBS News'
    shortname = 'cbs'
    url = 'https://www.cbsnews.com/'

    bad_titles = ['60 Minutes']
    bad_descriptions = ['60 Minutes']
    bad_urls = ['whats-in-the-news-coverart']

    @classmethod
    def _fetch_urls(cls):
        soup = cls._fetch_content(cls.url)

        top = soup.find('section', id='component-latest-news')\
            .find_all('article')
        h1s = (top[0].find('a')['href'],)
        h2s = tuple([x.find('a')['href'] for x in top[1:]])

        more = soup.find('section', id='component-more-top-stories')\
            .find_all('article')
        h3s = tuple([x.find('a')['href'] for x in more])

        return h1s, h2s, h3s
