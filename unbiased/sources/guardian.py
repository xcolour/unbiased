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

        url_groups = []
        for htag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            hblocks = soup.find('section', id='headlines').find_all(htag)
            urls = [x.a['href'] for x in hblocks]
            url_groups.append(urls)
        url_groups = [x for x in url_groups if len(url_groups) > 0]
        if len(url_groups) < 3:
            raise Exception('not enough article groups on Guardian home page!')

        return tuple(url_groups[0]), tuple(url_groups[1]), tuple(url_groups[2])

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
