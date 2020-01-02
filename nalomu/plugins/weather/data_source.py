from typing import Dict, Union, List

import aiohttp

from nalomu import NDict

try:
    import ujson as json
except ImportError:
    import json
from nalomu.config_loader import config

api = 'https://free-api.heweather.net/s6/weather/'
key = config.api.weather


async def get_weather_of_city(city: str, now_w=True) -> Union[Dict, List[Dict], bool]:
    url = f'{api}?location={city}&key={key}'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            # print(res.status)
            # print(await res.text())
            text = json.loads(await res.text())
            data = text['HeWeather6'][0]
            if data['status'] == 'unknown location':
                return False
            # 城市
            city = data['basic']['location']
            # 现在
            now: dict = data['now']

            daily_forecast = []
            for day in data['daily_forecast']:
                daily_forecast.append(NDict({
                    'city': city,  # 城市
                    'date': day['date'],  # 日期
                    'cond_txt_d': day['cond_txt_d'],  # 白天天气状况描述
                    'cond_txt_n': day['cond_txt_n'],  # 晚间天气状况描述
                    'wind_dir': day['wind_dir'],  # 风向
                    'wind_sc': day['wind_sc'],  # 风力
                    'tmp_max': day['tmp_max'],  # 最高温度
                    'tmp_min': day['tmp_min'],  # 最低温度
                }))
            print(daily_forecast)
    if now_w:
        now.update({'city': city})
        return NDict(now)
    else:
        return daily_forecast


weather_types = {'now', 'forecast', 'hourly', 'lifestyle'}
