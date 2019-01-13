import html
import re

from unbiased.sources.base import NewsSource

class TheGuardian(NewsSource):

    name = 'The Guardian'
    shortname = 'Guardian'
    url = 'https://www.theguardian.com/us'

    bad_authors = ['Tom McCarthy', 'Andy Hunter']
    bad_urls = ['https://www.theguardian.com/profile/ben-jacobs']

    _img_pat = re.compile('"srcsets":"(.*?)"')

    @classmethod
    def _fetch_urls(cls):
        soup = cls._fetch_content(cls.url)

        h = soup.find(id='headlines')\
            .find_all(class_='fc-item__link')
        h = [x['href'] for x in h]

        h1s = (h[0],)
        h2s = tuple(h[1:4])
        h3s = tuple(h[4:])

        return h1s, h2s, h3s

    @classmethod
    def _get_image(cls, soup):
        # the guardian watermarks the images in their <meta> tags,
        # and the <img> of the hero is a very small resolution,
        # but we can pull a hi-res image url out of the <script>
        # body inside of the page.
        try:
            script = soup.find('script', id='gu').text
            matches = cls._img_pat.search(script)
            if matches:
                srcsets = matches.group(1).split(',')
                srcsets = sorted([(int(y.strip('w')), x.strip()) for x, y in [x.rsplit(' ', 1) for x in srcsets]])
                return html.unescape(srcsets[-1][1])
        except Exception:
            pass

        # if that ugly, brittle shit fails, fall back on the low-res image
        if soup.find('img', class_='maxed'):
            img = soup.find('img', class_='maxed')['src']
        if soup.find('meta', itemprop='image'):
            img = soup.find('meta', itemprop='image')['content']
        if soup.find('img', class_='immersive-main-media__media'):
            img = soup.find('img', class_='immersive-main-media__media')['src']
        return html.unescape(img)
