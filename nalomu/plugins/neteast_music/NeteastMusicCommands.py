try:
    import ujson as json
except ImportError:
    import json

import aiohttp
from nonebot import IntentCommand, logger

from nalomu.commands import BaseCommand, method_command, method_parser, method_nlp
from nalomu import NDict


class NeteastMusicCommands(BaseCommand):

    @method_command('nalomu_music', aliases=('点歌',), only_to_me=False)
    async def nalomu_music(self):
        music = self.get('music', prompt='要点什么？')
        try:
            res = await self.get_music(music)
            await self.send(res)
        except Exception as e:
            logger.error(e)
            await self.send('出错啦!')

    @nalomu_music.args_parser
    @method_parser
    async def _(self):
        self.parse_striped_text('music')

    @method_nlp(keywords={'点歌'}, only_to_me=False)
    async def _(self):
        stripped_msg = self.stripped_msg
        return IntentCommand(90.0, 'nalomu_music', current_arg=stripped_msg.replace('点歌', '') or '')

    @staticmethod
    async def get_music(q: str) -> str:
        api_url = "http://localhost:3000"
        url = f'{api_url}/search'
        song_url = f'{api_url}/song/url'
        album_url = f'{api_url}/album'
        info_url = "https://music.163.com/#/song?id={id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params={"limit": 1, "keywords": q}) as res:
                # print(res.status)
                # print(await res.text())
                text = await res.text()
                print(text)
                data = json.loads(text)
                print(data)
                song = data['result']['songs'].pop()
                artists = song['artists']
                artists_name = '/'.join([artist['name'] for artist in artists])
                name = song['name']
                music_id = song['id']
                info_url = info_url.format(id=music_id)
                # return '[CQ:music,type=163,id={}]'.format(song['id'])
            async with session.get(song_url, params={"id": music_id}) as resp:
                data = NDict(await resp.json())
                audio_url = data.data.pop()['url']
            async with session.get(album_url, params={"id": song['album']['id']}) as resp:
                data = NDict(await resp.json())
                image_url = data.album.picUrl
                return '[CQ:music,type=custom,url={url},audio={audio},title={title},content={content},image={image}]'.format(
                    url=info_url,
                    audio=audio_url,
                    title=name,
                    content=artists_name,
                    image=image_url
                )


__all__ = ['NeteastMusicCommands']
