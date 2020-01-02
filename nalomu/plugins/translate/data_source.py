import asyncio
import operator
import re
from functools import reduce

import aiohttp
import time
import random
from hashlib import md5
import json

from nalomu.plugins.usage import chunks


class YoudaoFanyi(object):
    def __init__(self):
        self.headers = {
            'Pragma': "no-cache",
            'Origin': "http://fanyi.youdao.com",
            'Accept-Encoding': "gzip, deflate",
            'Accept-Language': "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
            'Content-Type': "application/x-www-form-urlencoded; charset=UTF-8",
            'Accept': "application/json, text/javascript, */*; q=0.01",
            'Cache-Control': "no-cache",
            'X-Requested-With': "XMLHttpRequest",
            'Connection': "keep-alive",
            'Referer': "http://fanyi.youdao.com/",
            'Cookie': "OUTFOX_SEARCH_USER_ID=-{0}@{1}.{2}.{3}.{4}; ".format(str(random.randint(100000000, 999999999)),
                                                                            str(random.randint(10, 241)),
                                                                            str(random.randint(10, 241)),
                                                                            str(random.randint(10, 241)),
                                                                            str(random.randint(10, 241))),
        }

    async def fanyi(self, text):
        if len(text) < 2000:
            if isinstance(text, str):
                data = await self._fanyi(text)
                return data
            elif isinstance(text, list):
                tasks = [self._fanyi(re.sub("\\s*\n+", "\n", "".join(l)))
                         for l in chunks(text, 30)]
                data = await asyncio.gather(*tasks)
                return reduce(operator.add, data)

        else:
            pass
            # lines = text.split('\n')
            # data = []
            # for l in chunks(lines, 30):
            #     i = "".join([re.sub("^\\n$", "", s) for s in l])
            #     data += self._fanyi(i)
            # return data

    async def _fanyi(self, text):
        url = "http://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule"

        # 有两个参数需要解析
        # salt
        # sign
        # ===源码===
        # var t = "" + ((new Date).getTime() + parseInt(10 * Math.random(), 10));
        # return {
        #     salt: t,
        #     sign: n.md5("fanyideskweb" + e + t + "sr_3(QOHT)L2dx#uuGR@r")
        # }
        t = int(time.time() * 1000) + random.randint(0, 11)

        # e就是查询的关键字
        sign_str = ("fanyideskweb" + text + str(t) + "n%A-rKaT5fb[Gy?;N5@Tj").encode("utf-8")

        sign = md5(sign_str).hexdigest()

        data = {
            "i": text,
            "from": "AUTO",
            "to": "AUTO",
            "smartresult": "dict",
            "client": "fanyideskweb",
            "salt": str(t),
            "sign": sign,
            "doctype": "json",
            "version": "2.1",
            "keyfrom": "fanyi.web",
            "action": "FY_BY_REALTIME",
            "typoResult": "false"
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    url=url,
                    data=data,
                    headers=self.headers) as resp:
                jsonres = json.loads(await resp.text())
                data = []
                if jsonres['errorCode'] != 50:
                    for res in jsonres["translateResult"]:
                        src = ""
                        tgt = ""
                        for _ in res:
                            src += _["src"]
                            tgt += _["tgt"]
                        if not src: continue
                        data.append({"src": src, "tgt": tgt})
                return data
