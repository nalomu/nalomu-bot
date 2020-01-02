import re

from aiohttp import ClientSession
from bs4 import BeautifulSoup


async def danbooru(url):
    """
    获取danbooru来源
    :param str url: danbooru URL
    :return: 来源URL
    """
    async with ClientSession() as session:
        async with session.get(url) as resp:
            text = await resp.text()
    soup = BeautifulSoup(text)
    return soup.find_one(id='image-container')['data-normalized-source']


async def konachan(url):
    """
    获取konachan来源
    :param str url: konachan URL
    :return: 来源URL
    """
    async with ClientSession() as session:
        async with session.get(url) as resp:
            text = await resp.text()
    soup = BeautifulSoup(text)
    source = None
    li_list = soup.find_one(id='stats').find_all('li')
    for li in li_list:
        if re.search('^Source:', li.text):
            source = li.find_one('a')['href']
    return source
