import os
from setuptools import setup

buildnum = os.environ.get('TRAVIS_BUILD_NUMBER')
if buildnum is None:
    version = '0.dev0'
else:
    version = buildnum
gitrev = os.environ.get('TRAVIS_COMMIT')
if gitrev is not None:
    version = '{}+{}'.format(version, gitrev)

setup(
    name="unbiased",
    version=version,
    packages=['unbiased', 'unbiased.sources'],
    package_data={
        'unbiased': [
            'html_template/*.html',
            'html_template/*.css',
            'html_template/*.ico',
            'html_template/*.png',
        ],
    },
    install_requires=[
        'jinja2',
        'Pillow',
        'requests',
        'lxml',
        'beautifulsoup4',
    ],
    entry_points={
        'console_scripts': [
            'unbiased = unbiased.main:main',
        ],
    },
)
