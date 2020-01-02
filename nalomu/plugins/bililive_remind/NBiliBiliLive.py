from typing import Tuple, Any, Union, Dict

import aiohttp
import nonebot
from nonebot import logger

from nalomu import NDict


class NBiliBiliLive:
    _session: aiohttp.ClientSession = None

    def __init__(self, room_id: int):
        self.headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4,zh-TW;q=0.2',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/59.0.3071.115 Safari/537.36 '
        }
        self.print = nonebot.logger.info
        self.room_id = room_id
        self.print('{} 房间监听初始化'.format(room_id))

    def __await__(self):
        return self._init_corn().__await__()

    async def check(self):
        room_info = await self.get_room_info()
        if room_info['status']:
            info = '[ https://live.bilibili.com/{} ]-[{}] {} 开播了'.format(
                self.room_id, room_info["hostname"],
                room_info['roomname'])
            return info
        else:
            self.print('[{}]-[{}] 未开播'.format(self.room_id, room_info["hostname"]))
            return False

    async def check_room(self) -> Tuple[bool, Any]:
        room_info_url = 'https://api.live.bilibili.com/room/v1/Room/get_info'
        response = await self._session.get(room_info_url, params={'room_id': self.room_id})
        response = await response.json()
        if response['msg'] == 'ok':
            return True, response['data']['room_id']
        else:
            return False, response['msg']

    async def _init_corn(self):
        if not isinstance(self.__class__._session, aiohttp.ClientSession):
            self.__class__._session = aiohttp.ClientSession()
            await self.__class__._session.__aenter__()
        return self

    @classmethod
    async def close(cls):
        logger.info('nlive session close')
        await cls._session.__aexit__(None, None, None)

    async def get_room_info(self) -> Union[Dict, bool]:
        data = {}
        room_info_url = 'https://api.live.bilibili.com/room/v1/Room/get_info'
        user_info_url = 'https://api.live.bilibili.com/live_user/v1/UserInfo/get_anchor_in_room'
        response = await self._session.get(room_info_url, params={'room_id': self.room_id})
        response_json = NDict(await response.json())
        logger.debug(response_json)
        if response_json['msg'] == 'ok':
            data['roomname'] = response_json.data.title
            data['status'] = response_json.data.live_status == 1
            data['room_id'] = response_json.data.room_id
            response = await self._session.get(user_info_url, params={'roomid': data['room_id']})
            response_json = NDict(await response.json())
            data['hostname'] = response_json.data.info.uname
            return data
        else:
            return False
