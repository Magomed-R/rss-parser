# Парсер RSS-лент

Это парсер rss-лент для последующего постинга в Telegram через Bot API. Написан на языке Python и библиотеке python-telegram-bot

## Настройка

Перед запуском необходимо настроить config.ini:

1. Получить токен бота у https://t.me/botFather и вставить в поле `bot_token`
2. Получить id группы\канала у https://t.me/getmyid_bot, переслав ему сообщение из нужной группы\канала (будет находиться в Forwarded from) и вставить в `channel_id`
3. Можно поменять интервал постинга сообщений через поле `interval`
4. Вставить ссылки на RSS-ленты в поля `rss_$_link`

Всё, что ниже rss_5_link, не трогать

## Запуск

Можно запустить двумя способами - вручную и через docker.

### Чтобы запустить вручную:

1. Создать среду разработки:

```
python -m venv rss-parser
```

2. Запустите среду разработки:

```
source rss-parser/bin/activate
```

3. Установите зависимости:

```
pip install -r requirements.txt
```

4. Запустите парсер:

```
py main.py
# или
python main.py
```

5. После всех необходимых действий, деактивируйте среду разработки:

```
deactivate
```

### Чтобы запустить через docker:

1. Соберите образ:

```
docker build -t rss-parser:latest .
```

2. Запустите парсер:

```
docker run --name rss-parser rss-parser:latest
```
