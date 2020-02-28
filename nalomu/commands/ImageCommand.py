import re
from os import path

import imgkit
from bs4 import BeautifulSoup
from mako.lookup import TemplateLookup
from mako.template import Template
from nonebot import logger
from nonebot.session import BaseSession

from nalomu.plugins import call_on_api_available
from nalomu.commands import BaseCommand
from nalomu.config_loader import config as file_config

class ImageCommand(BaseCommand):
    image_available = False

    def __init__(self, session: BaseSession):
        super().__init__(session)
        from config import TEMPLATES_ROOT
        self.template_lookup = TemplateLookup(directories=[TEMPLATES_ROOT],
                                              module_directory='/tmp/mako_modules',
                                              input_encoding='utf-8',
                                              output_encoding='utf-8',
                                              default_filters=['decode.utf_8'])

    def render_image(self, view='', bg=False, width=500, **kwargs):
        from config import TEMPLATES_ROOT, DATA_ROOT, DATA_URL
        # files and url
        tpl_file = path.join(TEMPLATES_ROOT, f'{view}.mako')
        img_file = path.join(DATA_ROOT, f'{view}.jpg')
        css_file = path.join(TEMPLATES_ROOT, 'css/bootstrap.min.css')
        img_url = DATA_URL + f'/{view}.jpg'
        # render template
        view = Template(filename=tpl_file, input_encoding='utf-8', output_encoding='utf-8', lookup=self.template_lookup)
        kwargs.update({'data_url': DATA_URL, 'cover': bg})
        html_str = view.render(**kwargs).decode('utf-8')
        logger.debug(f"image_available: {self.image_available}")
        if self.image_available:
            # output

            config = imgkit.config(wkhtmltoimage=file_config.wkhtmltoimage_path)
            # imgkit.from_string(html_string, output_file, config=config)
            imgkit.from_string(html_str,
                               output_path=img_file,
                               css=css_file,
                               options={'crop-w': width},
                               config=config)
            # return cq code
            return f'[CQ:image,cache=0,file={img_url}]'
        else:
            soup = BeautifulSoup(html_str, 'html5lib')
            msg = re.sub(r'\n+', '\n', soup.body.text.strip().replace(' ', ''))
            return msg


@call_on_api_available
async def _():
    from nonebot import get_bot
    data = await get_bot().can_send_image()
    logger.info(f"can_send_image:{data}")
    ImageCommand.image_available = data['yes']
