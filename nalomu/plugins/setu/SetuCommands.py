import random
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List

try:
    import ujson as json
except ImportError:
    import json
from os import path

import aiohttp

from nalomu import NDict
from nalomu.commands import BaseCommand, method_command, method_parser, method_nlp
from nalomu.util import is_number

random_pixiv_file = path.join(path.abspath(path.dirname(__file__)), 'random.json')
last_request = defaultdict(list)


class SetuConstruct:
    def __init__(self, user_id, request_time):
        self.user_id = user_id
        self.request_time = request_time


class SetuCommands(BaseCommand):
    @method_command('setu', aliases=('瑟图', '色图'))
    async def setu(self):
        # await self.send('暂时关闭')
        if self.group_id:
            requests_users: List[SetuConstruct] = last_request[self.group_id]
            user: SetuConstruct = next((user for user in requests_users if user.user_id == self.user_id), None)
            if user:
                if datetime.now() - user.request_time < timedelta(hours=1):
                    await self.send('你冲的太多啦！稍微休息一个小时吧')
                    return
                else:
                    user.request_time = datetime.now()
            else:
                requests_users.append(SetuConstruct(self.user_id, datetime.now()))

        num = int(self.get('num', required=False) or 1)
        if not is_number(num) or num < 1 or num > 3:
            num = 1
        with open(random_pixiv_file) as f:
            random_pixiv_ids = json.load(f)
        images = random.choices(random_pixiv_ids, k=num)
        for index, image_id in enumerate(images):
            while not await self.check_image(image_id):
                image_id = random.choice(random_pixiv_ids)
                images[index] = image_id
        for image_id in images:
            await self.send_image(f'https://pixiv.cat/{image_id}.jpg')

    @setu.args_parser
    @method_parser
    async def _(self):
        self.parse_striped_text('num')

    @staticmethod
    async def check_image(image_id):
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://pixiv.cat/{image_id}.jpg') as resp:
                return resp.status == 200


__all__ = ['SetuCommands']
