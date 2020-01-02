import asyncio
from bs4 import BeautifulSoup
import aiohttp

baseURL = 'https://ascii2d.net'


async def doSearch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'{baseURL}/search/url/{url}') as resp:
            color_url = str(resp.url)
            color_html = await resp.text()
        bovw_url = color_url.replace('/color/', '/bovw/')
        async with session.get(bovw_url) as resp:
            bovw_html = await resp.text()
        return {
            "color": 'ascii2d 色合検索\n' + getShareText(**getDetail(color_html)),
            "bovw": 'ascii2d 特徴検索\n' + getShareText(**getDetail(bovw_html)),
        }


def getDetail(html):
    """
    解析 ascii2d 网页结果
    :param str html: ascii2d HTML
    :return: 画像搜索结果
    """
    soup = BeautifulSoup(html, 'html5lib')
    # const $ = Cheerio.load(html, {
    #     decodeEntities: false,
    # })
    box = soup.find_all(class_='item-box')[1]
    detail = box.find_all(class_='detail-box')[0]
    link = detail.find_all('a')
    print(link)
    if len(link) < 2:
        return {
            "title": detail.select_one(".external").text.strip(),
            "author": "",
            "url": "",
            "author_url": "",
        }
    else:
        title = link[0]
        author = link[1]
        # let $box = $($('.item-box')[1])
        # let thumbnail = baseURL + $box.find('.image-box img').attr('src')
        # let $link = $box.find('.detail-box a')
        # let $title = $($link[0])
        # let $author = $($link[1])
        return {
            "title": title.text,
            "author": author.text,
            "url": title.get('href'),
            "author_url": author.get('href'),
        }
    # return {
    # thumbnail,
    # title: $title.html(),
    # author: $author.html(),
    # url: $title.attr('href'),
    # author_url: $author.attr('href'),
    # }


def getShareText(url, title, author, author_url):
    text = f"""「{title}」/「{author}」
{pixivShorten(url)}"""
    if author_url:
        text += f'\nAuthor: {pixivShorten(author_url)}'
    return text.strip()


def pixivShorten(url):
    """
    pixiv 短链接
    :param str url:
    :return:
    """
    import re
    pid_search = re.search('pixiv.+illust_id=([0-9]+)', url)
    if pid_search:
        return 'https://pixiv.net/i/' + pid_search[1]
    uid_search = re.search('pixiv.+member\\.php\\?id=([0-9]+)', url)
    if uid_search:
        return 'https://pixiv.net/u/' + uid_search[1]
    return url


if __name__ == '__main__':
    async def run():
        print(await doSearch(url))
    url = 'https://nalomu.tk/bg.jpg'
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
