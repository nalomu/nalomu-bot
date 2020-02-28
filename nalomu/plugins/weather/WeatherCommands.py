from nalomu import NDict

try:
    import ujson as json
except ImportError:
    import json
import re

import aiohttp
from jieba import posseg
from nonebot import IntentCommand
from nalomu.config_loader import config as local_config

from config import DATA_ROOT
from nalomu.commands import method_command, method_parser, method_nlp, ImageCommand
from .data_source import get_weather_of_city


class WeatherCommands(ImageCommand):
    plugin_name = "天气"

    @method_command('weather', aliases=('天气',))
    async def weather(self):
        """
weather/天气 [城市] [TYPE=now]
    TYPE: 3 3天天气
          now 今天
    或者直接发送地点看看能不能试别出来
        """
        city = self.get('city', prompt='你想查询哪个城市的天气呢？')
        tday = self.get('3day', prompt='现在的还是3天的？')
        tdays = False if re.search('3', tday) else True
        await self.send('查询中...', no_delay=True)
        try:
            weather = await get_weather_of_city(city, tdays)
            if weather:
                await self.send(self.render_image('weather',
                                                  weather=weather,
                                                  width=1000,
                                                  data_root=DATA_ROOT),
                                no_delay=True)
            else:
                await self.send('没有查到结果;w;，是不是手滑输错城市了？')
        except Exception as e:
            await self.send('出错啦!', no_delay=True)
            raise e

    @method_command('air_quality', aliases=('空气质量',))
    async def air_quality(self):
        """
air_quality/空气质量 [城市]
        """
        city = self.get('city', prompt='你想查询哪个城市的空气质量呢？')
        air_quality = await self.get_air_quality(city)
        if air_quality:
            params = dict(
                air_quality=air_quality,
                data_root=DATA_ROOT
            )
            await self.send(self.render_image('air_quality',
                                              width=1000,
                                              **params), no_delay=True)
        else:
            await self.send('没有查到结果;w;，是不是手滑输错城市了？')

    @air_quality.args_parser
    @method_parser
    async def _(self):
        self.parse_striped_text('city')

    @weather.args_parser
    @method_parser
    async def _(self):
        stripped_arg = self.stripped_msg
        # 第一次运行
        if self.session.is_first_run:
            args = stripped_arg.split(' ')
            # 不是从on_natural_language进来的
            if len(args) != 2:
                if args[0]:
                    self.session.state['city'] = args[0]
                return
            # 是从on_natural_language进来的
            if args[0] != 'None':
                self.session.state['city'] = args[0]
            self.session.state['3day'] = args[1]
            return

        if not stripped_arg:
            self.session.pause('要查询的城市名称不能为空呢，请重新输入')

        self.session.state[self.session.current_key] = stripped_arg

    @method_nlp()
    async def _(self):
        # 去掉消息首尾的空白符
        stripped_msg = self.stripped_msg

        # 对消息进行分词和词性标注
        words = posseg.lcut(stripped_msg)

        city = None
        # 遍历 posseg.lcut 返回的列表
        for word in words:
            # 每个元素是一个 pair 对象，包含 word 和 flag 两个属性，分别表示词和词性
            if word.flag == 'ns':
                # ns 词性表示地名
                city = word.word

        if city:
            # 返回意图命令，前两个参数必填，分别表示置信度和意图命令名
            tdays = '3day' if re.search('3', stripped_msg) else 'now'
            # 返回意图命令，前两个参数必填，分别表示置信度和意图命令名
            return IntentCommand(75.0, 'weather', current_arg=city + ' ' + tdays or f'None {tdays}')

    @staticmethod
    async def get_air_quality(city):
        url = "https://free-api.heweather.net/s6/air/now"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params={"location": city, "key": local_config.api.weather}) as resp:
                data = json.loads(await resp.text())
                data = NDict(data['HeWeather6'].pop())
                if data.status != 'ok':
                    return False
                return data


__all__ = ['WeatherCommands']
