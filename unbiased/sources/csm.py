from unbiased.sources.base import NewsSource

class CSM(NewsSource):

    name = 'Christian Science Monitor'
    shortname = 'csm'
    url = 'https://www.csmonitor.com/USA'

    bad_titles = ['Change Agent']
    bad_imgs = ['csm_logo']
    bad_urls = ['difference-maker']

    @classmethod
    def _fetch_urls(cls):
        soup = cls._fetch_content(cls.url)

        # get all headlines
        h = soup.find_all('div', class_='ezc-csm-story')
        h = [x.find('a')['href'] for x in h]

        # get primary headlines (first four)
        h1s = tuple(h[:4])

        # get secondary headlines (the rest)
        h2s = tuple(h[4:])

        return h1s, h2s, ()
