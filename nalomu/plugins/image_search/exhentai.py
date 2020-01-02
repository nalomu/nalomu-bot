# coding=utf8
from bs4 import BeautifulSoup
import aiohttp

from nalomu.config_loader import config

cookies = config.excookie
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
}


async def http_get(url):
    async with aiohttp.ClientSession(cookies=cookies, headers=headers) as session:
        async with session.get(url) as resp:
            text = await resp.text()
            return text


async def get_result(kw):
    html = await http_get('https://exhentai.org?f_search=' + kw)
    print(html)
    soup = BeautifulSoup(html, 'html5lib')
    res = soup.find(class_='itg gld')
    if not res:
        return False
    res = res.find(class_='gl1t') \
        .find('a')
    return {
        'link': res['href'],
        'book_name': res.text
    }
