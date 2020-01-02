# import aiohttp
try:
    import ujson as json
except ImportError:
    import json

from aiohttp import ClientSession
from bs4 import BeautifulSoup


class Pixiv:
    session: ClientSession = None

    def __await__(self):
        return self._async_init().__await__()

    async def login(self):
        data = {
            ""
        }
        async with self.session.get('https://accounts.pixiv.net/login') as resp:
            html = await resp.text()
            soup = BeautifulSoup(html, 'html5lib')
            init_data = json.loads(soup.select_one('#init-config').value)
            postKey = init_data['pixivAccount.postKey']

    async def _async_init(self):
        self.__class__.session = ClientSession()
        await self.__class__.session.__aenter__()
        return self
