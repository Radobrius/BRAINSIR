# BRAINSIR

Telegram Mini App — игра на общие знания.

## Возможности
- 50 вопросов в каждой игре, выбираются случайно из банка.
- 4 варианта ответа, один правильный.
- 15 секунд на ответ.
- Ошибка или тайм-аут завершают попытку.
- Личный рекорд и глобальный топ-5.
- SQLite, без платных API.

## Переменные Railway
- `BOT_TOKEN` — токен от BotFather.
- `WEBAPP_URL` — публичный HTTPS URL Railway-сервиса.
- `DATABASE_PATH` — необязательно; для постоянной базы укажи `/data/brainsir.db`, предварительно подключив Volume к `/data`.

## Локальный запуск
```bash
pip install -r requirements.txt
export BOT_TOKEN="токен"
export WEBAPP_URL="https://твой-домен"
python bot.py
```

Открой бота в Telegram и отправь `/start`.

## Важно
Веб-приложение проверяет Telegram initData на сервере. Не открывай Mini App обычной ссылкой в браузере: авторизация работает через Telegram.
