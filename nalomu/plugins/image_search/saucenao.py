import json
import re

import aiohttp

from nalomu import NDict
from nalomu.config_loader import config
from . import get_source, exhentai

host = 'http://saucenao.com/search.php'
# hostsI = 0

snDB = {
    "all": 999,
    "pixiv": 5,
    "danbooru": 9,
    "book": 18,
    "anime": 21,
}

exts = {
    "j": 'jpg',
    "p": 'png',
    "g": 'gif',
}


async def doSearch(imgURL, db, dbmask=True):
    """
    saucenao搜索
:param {string} imgURL 图片地址
:param {string} db 搜索库
:param {boolean} [debug=false] 是否调试
:return Promise 返回消息、返回提示
    """
    # hostIndex = hostsI++ % hosts.length; # 决定当前使用的host
    warn_msg = ''  # 返回提示
    msg = '失败'  # 返回消息
    success = False
    low_acc = False
    excess = False

    data = NDict(await getSearchResult(host, imgURL, db, dbmask))
    # data = ret["data"]

    # 确保回应正确
    if data.results and len(data.results) > 0:
        result = NDict(data.results[0])
        header = data.header
        result = result.data

        (
            short_remaining,  # 短时剩余
            long_remaining,  # 长时剩余
            similarity,  # 相似度
        ) = (header.short_remaining,
             header.long_remaining,
             float(data.results[0]["header"]["similarity"]),)

        source = None
        if result.ext_urls:
            url = result.ext_urls[0]
            # 如果结果有多个，优先取danbooru
            for u in result.ext_urls:
                if u.find('danbooru') != -1:
                    url = u

            url = url.replace('http://', 'https://')
            # 若为danbooru则获取来源
            if url.find('danbooru') != -1:
                source = await get_source.danbooru(url)
            elif url.find('konachan') != -1:
                source = await get_source.konachan(url)
        else:
            url = ''

        (
            title,  # 标题
            member_name,  # 作者
            member_id,  # 可能 pixiv uid
            eng_name,  # 本子名
            jp_name,  # 本子名
        ) = (
            result.title,  # 标题
            result.member_name,  # 作者
            result.member_id,  # 可能 pixiv uid
            result.eng_name,  # 本子名
            result.jp_name,  # 本子名
        )
        if not title:
            title = '搜索结果' if url.find('anidb.net') == -1 else 'AniDB'

        book_name = jp_name or eng_name  # 本子名

        if member_name and len(member_name) > 0:
            title = f'「{title}」/「{member_name}」'

        # 剩余搜图次数
        if long_remaining < 20:
            warn_msg += f'saucenao：注意，24h内搜图次数仅剩{long_remaining}次\n'
        elif short_remaining < 5:
            warn_msg += f'saucenao：注意，30s内搜图次数仅剩{short_remaining}次\n'
        # 相似度
        if similarity < 60:
            low_acc = True
            warn_msg += f'相似度[{similarity}%]过低，如果这不是你要找的图，那么可能：确实找不到此图/图为原图的局部图/图清晰度太低/搜索引擎尚未同步新图\n'
            # if db == snDB["all"] or db == snDB["pixiv"]:
            #     warn_msg += '自动使用 ascii2d 进行搜索\n'

            # 回复的消息
        msg = await getShareText(**{
            "url": url,
            "title": f'[{similarity}%] {title}',
            "author_url": f'https://pixiv.net/u/{member_id}' if (
                    member_id and url.find('pixiv.net') >= 0) else None,
            "source": source,
        })

        success = True

        # 如果是本子
        if book_name:
            book_name = book_name.replace('(English)', '')
            book_name = re.sub('(\\(.+?\\)|\\[.+?\\]|)', '', book_name)
            book = await exhentai.get_result(book_name)
            # 有本子搜索结果的话
            if book:
                url = book['link']
                book_name = book['book_name']
            else:
                success = False
                warn_msg += '没有在exhentai找到对应的本子_(:3」∠)_\n或者可能是此query因bug而无法在exhentai中获得搜索结果\n'

            msg = await getShareText(**{
                'url': url,
                "title": f'[{similarity}%] {book_name}',
            })

        # 处理返回提示
        if len(warn_msg) > 0:
            warn_msg = warn_msg[0:warn_msg.find('\n')]
    elif "message" in data["header"].keys():
        if data["header"]['message'] == 'Specified file no longer exists on the remote server!':
            # case 'Specified file no longer exists on the remote server!':
            msg = '该图片已过期，请尝试二次截图后发送'
            # break;

        elif data["header"]['message'] == 'Problem with remote server...':
            msg = '远程服务器出现问题，请稍后尝试重试'

        else:
            msg = data["header"]['message']
    else:
        pass

    res = {
        "success": success,
        "msg": msg,
        "warn_msg": warn_msg,
        "low_acc": low_acc,
        "excess": excess,
    }
    print(res)
    return res


def pixivShorten(url):
    """
    pixiv 短链接
    :param str url:
    :return:
    """
    pid_search = re.search('pixiv.+illust_id=([0-9]+)', url)
    if pid_search:
        return 'https://pixiv.net/i/' + pid_search[1]
    return url


# async def confuseURL(url):
#     """
#     :param str url:
#     :return:
#     """
#     if re.search('danbooru\\.donmai\\.us|yande\\.re|konachan\\.com', url):
#         (result, path, error) = await shorten(url)
#         return result if error else f'https://j.loli.best/#{path}'
#
#     return pixivShorten(url)


async def getShareText(url, title, author_url=None, source=None):
    text = f"""{title}
{url}
    """
    # {await confuseURL(url)}"""
    if author_url:
        # text += f'\nAuthor: {await confuseURL(author_url)}'
        text += f'\nAuthor: {author_url}'
    if source:
        text += f'\nSource: {source}'
        # text += f'\nSource: {await confuseURL(source)}'
    return text.strip()


async def getSearchResult(host, imgURL, db=999, dbmask=True):
    """
    取得搜图结果
    :param bool dbmask: 是否使用掩码
    :param str host: 自定义saucenao的host
    :param str imgURL: 欲搜索的图片链接
    :param int db: 搜索库
    :return:
    """
    api_key = config.api.saucenao
    payload = {
        'output_type': 2,
        'numres': 2,
        # 'minsim': '50!',
        # 'dbmask': str(db_bitmask),
        'api_key': api_key,
        'url': imgURL,
    }
    if dbmask:
        payload.update({'dbmask': db, })
    else:
        payload.update({'db': db, })
    async with aiohttp.ClientSession() as session:
        async with session.post(host, params=payload) as resp:
            return json.loads(await resp.text())
