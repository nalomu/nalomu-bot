import asyncio

from nalomu.commands import BaseCommand, method_command, method_parser
from . import saucenao, ascii2d


class ImageSearchCommands(BaseCommand):

    @method_command('image_search', aliases=('搜图',))
    async def image_search(self):
        images = self.images
        first_search_done = self.has_arg('first_search_done')
        if not images:
            images = self.get('images', prompt='请发送要搜索的图片')

        if self.has_arg('ascii2d'):
            for image in images:
                try:
                    res = await ascii2d.doSearch(image)
                except Exception as e:
                    await self.send("出错啦")
                    print(e)
                    return
                await self.send(res["color"], no_delay=True)
                await asyncio.sleep(0.8)
                await self.send(res["bovw"], no_delay=True)
            return
        elif self.has_arg('book'):
            if self.group_id:
                await self.send('仅私聊可用')
                return
            for image in images:
                res = await saucenao.doSearch(image, 999, dbmask=False)
                await self.send(res["msg"])
                if res['warn_msg']:
                    await self.send(res['warn_msg'])
            return

        if not first_search_done:
            res = await saucenao.doSearch(images[0], 5 + 9 + 21)
            await self.send(res["msg"], no_delay=True)
            await self.send(res["warn_msg"], no_delay=True)
            self.session.state["first_search_done"] = True
        else:
            res = self.get('res', required=False)
        if res["low_acc"]:
            self.session.state['res'] = res
            reascii2d = self.get('_ascii2d', prompt=f'是否尝试使用ascii2d搜索一次(y/n)')
            if reascii2d == 'y':
                for image in images:
                    try:
                        ret = await ascii2d.doSearch(image)
                    except Exception as e:
                        await self.send("出错啦！")
                        print(e)
                        return
                    await self.send(ret["color"], no_delay=True)
                    await asyncio.sleep(0.8)
                    await self.send(ret["bovw"], no_delay=True)
            else:
                await self.send('放弃搜索')
            return

    @image_search.args_parser
    @method_parser
    async def _(self):
        images = self.images
        text = self.stripped_msg

        if self.session.is_first_run:
            if images:
                print(images)
                self.session.state['images'] = images
            if text.lower() == '-a' or text.lower() == '--ascii2d':
                self.session.state['ascii2d'] = True
            if text.lower() == '-b' or text.lower() == '--book':
                self.session.state['book'] = True
            return

        if self.session.current_key == 'images':
            if not images:
                self.session.pause('请发送要搜索的图片')
            self.session.state[self.session.current_key] = images
        else:
            self.session.state[self.session.current_key] = text


__all__ = ['ImageSearchCommands']
