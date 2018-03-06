from unbiased.sources.base import NewsSource

class Fox(NewsSource):

    name = 'Fox News'
    shortname = 'Fox'
    url = 'http://www.foxnews.com'

    bad_titles = ['O&#039;Reilly', 'Fox News', 'Brett Baier', 'Tucker']
    bad_descriptions = ['Sean Hannity']
    bad_authors = ['Bill O\'Reilly', 'Sean Hannity', 'Howard Kurtz']
    bad_imgs = ['http://www.foxnews.com/content/dam/fox-news/logo/og-fn-foxnews.jpg']
    bad_urls = ['http://www.foxnews.com/opinion', 'videos.foxnews.com']

    @classmethod
    def _fetch_urls(cls):
        """
        Returns three tuples of urls, one for each of
        the three tiers.
        """
        soup = cls._fetch_content(cls.url)

        primary = soup.find('div', class_='main-primary')\
                .find('div', class_='collection-spotlight')\
                .find_all('article', class_='article')
        h1s = (primary[0].find('header', class_='info-header').find('a')['href'],)
        h2s = tuple(x.find('header', class_='info-header').find('a')['href'] for x in primary[1:])

        h3s = soup.find('div', class_='main-primary')\
                .find('div', class_='collection-article-list')\
                .find_all('article', class_='article')
        h3s = tuple(x.find('header', class_='info-header').find('h2', class_='title').find('a')['href'] for x in h3s)

        return h1s, h2s, h3s
