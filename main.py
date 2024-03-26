import sys
import time

import configparser
import logging
import os
import telegram.error
import traceback
from requests import get
from rss_parser import Parser
from telegram import Update
from telegram.ext import Application
from bs4 import BeautifulSoup

sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
                    )
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

config = configparser.RawConfigParser()
config.sections()
config.read(os.path.join(os.path.dirname(__file__), 'config.ini'), encoding="utf-8")

def strip_html(html_text: str):
    soup = BeautifulSoup(html_text, "html.parser")
    return soup.get_text()

async def news(context):
    this_rss = int(config['MAIN']['last_rss']) + 1
    while (config['MAIN'].get(f'rss_{this_rss}_link') is None or len(config['MAIN'].get(f'rss_{this_rss}_link')) == 0
           or this_rss > 5):
        this_rss += 1
        if this_rss > 5:
            this_rss = 1

    config.set('MAIN', f'last_rss', this_rss)
    with open("config.ini", "w+") as configfile:
        config.write(configfile)

    try:
        rss = get(config['MAIN'][f'rss_{this_rss}_link'])
        rss = Parser.parse(rss.text)

        new_news = list()

        for item in rss.channel.items:
            if item.link.content == config['MAIN'][f'rss_{this_rss}_lastpost']:
                break
            new_news.append(item)

        new_news = list(reversed(new_news))

        if len(new_news) > 0:
            config.set('MAIN', f'rss_{this_rss}_lastpost', new_news[len(new_news) - 1].link.content)
            with open("config.ini", "w+") as configfile:
                config.write(configfile)

            for item in new_news:
                info = f'<b>{item.title.content}</b>\n'
                if item.description is not None and len(item.description.content) != 0:
                    info = info + '\n' + item.description.content + '\n'
                info = info + '\n' + item.link.content

                info = strip_html(info)

                try:
                    pass
                    await application.bot.send_message(config['MAIN']['channel_id'], info, parse_mode='html', disable_web_page_preview=True)
                except telegram.error.RetryAfter as e:
                    print(f'[ANTIFLOOD] Ожидаю {e.retry_after} секунд.')

                    time.sleep(e.retry_after)

                    await application.bot.send_message(config['MAIN']['channel_id'], info, parse_mode='html', disable_web_page_preview=True)
                except telegram.error.BadRequest as e:
                    print(e)

                    info = info[slice(len(info) // 3)] + "..." + "\n\n" + item.link.content

                    try:
                        pass
                        await application.bot.send_message(config['MAIN']['channel_id'], info, parse_mode='html', disable_web_page_preview=True)
                    except telegram.error.RetryAfter as e:
                        print(f'[ANTIFLOOD] Ожидаю {e.retry_after} секунд.')

                        time.sleep(e.retry_after)

                        await application.bot.send_message(config['MAIN']['channel_id'], info, parse_mode='html', disable_web_page_preview=True)
                    except telegram.error.BadRequest as e:
                        print(e)
    except Exception as e:
        print('ОШИБКА')
        traceback.print_exc(e)


if __name__ == "__main__":
    application = (Application.builder().token(config['MAIN']['bot_token']).
                   write_timeout(360).read_timeout(360).build())

    job_queue = application.job_queue
    job_minute = job_queue.run_repeating(news, interval=int(config['MAIN']['interval']), first=1)

    application.run_polling(allowed_updates=Update.ALL_TYPES)

    print('Бот выключен.')
