import hashlib
import hmac
import json
import os
import random
import sqlite3
import time
import uuid
from urllib.parse import parse_qsl
from aiohttp import web
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from question_bank import QUESTION_ADDITIONS

BOT_TOKEN = os.environ["BOT_TOKEN"]
DB_PATH = os.environ.get("DATABASE_PATH", "brainsir.db")

# Формат: вопрос, четыре варианта, индекс правильного ответа, тема.
QUESTIONS = [
("Какая планета самая большая в Солнечной системе?", ["Земля","Юпитер","Сатурн","Нептун"], 1,"Космос"),
("Сколько сторон у шестиугольника?", ["5","6","7","8"], 1,"Наука"),
("Столица Австралии?", ["Сидней","Мельбурн","Канберра","Перт"], 2,"География"),
("Кто написал роман «Война и мир»?", ["Фёдор Достоевский","Лев Толстой","Антон Чехов","Иван Тургенев"], 1,"Культура"),
("Какой химический символ у золота?", ["Ag","Fe","Au","Go"], 2,"Наука"),
("Сколько минут в двух часах?", ["100","110","120","130"], 2,"Математика"),
("Какая река протекает через Египет?", ["Амазонка","Нил","Дунай","Ганг"], 1,"География"),
("Какая звезда ближе всего к Земле?", ["Сириус","Вега","Солнце","Полярная"], 2,"Космос"),
("В каком году человек впервые ступил на Луну?", ["1959","1969","1979","1989"], 1,"История"),
("Какой океан самый большой?", ["Атлантический","Индийский","Северный Ледовитый","Тихий"], 3,"География"),
("Сколько будет 9 × 8?", ["70","72","81","64"], 1,"Математика"),
("Какой газ растения поглощают при фотосинтезе?", ["Кислород","Азот","Углекислый газ","Водород"], 2,"Наука"),
("Кто создал картину «Мона Лиза»?", ["Ван Гог","Пикассо","Леонардо да Винчи","Клод Моне"], 2,"Культура"),
("В какой стране появилась пицца?", ["Франция","Италия","Греция","Испания"], 1,"Культура"),
("Сколько игроков одной футбольной команды на поле?", ["9","10","11","12"], 2,"Спорт"),
("Какой орган перекачивает кровь?", ["Лёгкие","Печень","Сердце","Почки"], 2,"Наука"),
("Какая гора самая высокая над уровнем моря?", ["К2","Эверест","Килиманджаро","Эльбрус"], 1,"География"),
("Какой язык программирования назван в честь комедийного шоу?", ["Java","Python","Ruby","Pascal"], 1,"Технологии"),
("Сколько хромосом обычно у человека?", ["23","44","46","48"], 2,"Наука"),
("Какой металл жидкий при комнатной температуре?", ["Железо","Ртуть","Медь","Алюминий"], 1,"Наука"),
("Кто был первым космонавтом?", ["Юрий Гагарин","Нил Армстронг","Алексей Леонов","Герман Титов"], 0,"История"),
("Столица Японии?", ["Киото","Осака","Токио","Нагоя"], 2,"География"),
("Сколько градусов в прямом угле?", ["45","90","180","360"], 1,"Математика"),
("Самое быстрое наземное животное?", ["Лев","Гепард","Антилопа","Страус"], 1,"Природа"),
("Самый холодный материк?", ["Европа","Азия","Антарктида","Северная Америка"], 2,"География"),
("Как называется превращение воды в пар?", ["Конденсация","Замерзание","Испарение","Плавление"], 2,"Наука"),
("Кто написал «Маленького принца»?", ["Жюль Верн","Антуан де Сент-Экзюпери","Виктор Гюго","Альбер Камю"], 1,"Культура"),
("Какой материк пересекают экватор и нулевой меридиан?", ["Африка","Австралия","Южная Америка","Европа"], 0,"География"),
("Сколько костей примерно у взрослого человека?", ["106","206","306","406"], 1,"Наука"),
("Кто написал «Звёздную ночь»?", ["Рембрандт","Ван Гог","Моне","Дали"], 1,"Культура"),
("Наименьшая частица химического элемента?", ["Молекула","Атом","Клетка","Кристалл"], 1,"Наука"),
("Мадагаскар — это…", ["Регион Кении","Часть Танзании","Отдельное государство","Часть Мозамбика"], 2,"География"),
("Сколько колец в олимпийском символе?", ["4","5","6","7"], 1,"Спорт"),
("Какой прибор измеряет атмосферное давление?", ["Термометр","Барометр","Гигрометр","Анемометр"], 1,"Наука"),
("Столица Канады?", ["Торонто","Ванкувер","Оттава","Монреаль"], 2,"География"),
("Какое число простое?", ["21","27","29","33"], 2,"Математика"),
("Какой витамин вырабатывается под действием солнечного света?", ["A","B12","C","D"], 3,"Наука"),
("Кто открыл пенициллин?", ["Мария Кюри","Александр Флеминг","Луи Пастер","Исаак Ньютон"], 1,"История"),
("Самая длинная кость человека?", ["Большеберцовая","Плечевая","Бедренная","Лучевая"], 2,"Наука"),
("Какой город называют Вечным городом?", ["Афины","Рим","Стамбул","Иерусалим"], 1,"География"),
("Сколько планет в Солнечной системе?", ["7","8","9","10"], 1,"Космос"),
("Кто создал Шерлока Холмса?", ["Агата Кристи","Артур Конан Дойл","Эдгар По","Чарльз Диккенс"], 1,"Культура"),
("Переход вещества из твёрдого состояния в жидкое?", ["Плавление","Кипение","Сублимация","Конденсация"], 0,"Наука"),
("В какой стране находится Самарканд?", ["Казахстан","Таджикистан","Узбекистан","Кыргызстан"], 2,"География"),
("Какой океан омывает восточное побережье США?", ["Тихий","Индийский","Атлантический","Южный"], 2,"География"),
("Сколько будет 15 в квадрате?", ["125","200","225","250"], 2,"Математика"),
("Какое яйцекладущее млекопитающее существует?", ["Кенгуру","Утконос","Дельфин","Коала"], 1,"Природа"),
("Столица Турции?", ["Стамбул","Анкара","Измир","Бурса"], 1,"География"),
("Какой газ преобладает в атмосфере Земли?", ["Кислород","Углекислый газ","Азот","Аргон"], 2,"Наука"),
("Сколько дней в високосном году?", ["365","366","367","364"], 1,"Математика"),
]


QUESTIONS.extend(QUESTION_ADDITIONS)
TOTAL_QUESTIONS = 500
if len(QUESTIONS) != TOTAL_QUESTIONS:
    raise RuntimeError(f"В банке должно быть {TOTAL_QUESTIONS} вопросов, найдено {len(QUESTIONS)}")
CHANNEL_BOT = None
CHANNEL_WEBAPP_URL = None
CHANNEL_ID = None
BOT_USERNAME = os.environ.get("BOT_USERNAME", "Brainsir_bot")

def configure_channel(bot, webapp_url, channel_id):
    global CHANNEL_BOT, CHANNEL_WEBAPP_URL, CHANNEL_ID
    CHANNEL_BOT = bot
    CHANNEL_WEBAPP_URL = webapp_url.rstrip("/")
    CHANNEL_ID = channel_id

def channel_text(player_count):
    return (
        "<b>🧠 BRAINSIR — ИНТЕЛЛЕКТУАЛЬНАЯ ИГРА</b>\n\n"
        "500 вопросов. 15 секунд на каждый. Одна ошибка — и игра окончена.\n\n"
        "Проверь свою эрудицию и попробуй попасть в ТОП-10!\n\n"
        f"<b>👥 Всего игроков: {player_count:,}</b>".replace(",", " ")
    )

async def update_channel_post():
    if CHANNEL_BOT is None or not CHANNEL_ID:
        return
    try:
        with connect() as c:
            count = c.execute("SELECT COUNT(*) FROM players").fetchone()[0]
            row = c.execute("SELECT value FROM app_settings WHERE key='channel_post_id'").fetchone()
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(
            f"🎮 ИГРАТЬ", url=f"https://t.me/{BOT_USERNAME}?startapp")]])
        text = channel_text(count)
        if row:
            try:
                await CHANNEL_BOT.edit_message_text(
                    chat_id=CHANNEL_ID, message_id=int(row["value"]),
                    text=text, reply_markup=keyboard, parse_mode="HTML")
                return
            except Exception as exc:
                if "message is not modified" in str(exc).lower():
                    return
        message = await CHANNEL_BOT.send_message(
            chat_id=CHANNEL_ID, text=text, reply_markup=keyboard, parse_mode="HTML")
        with connect() as c:
            c.execute("INSERT INTO app_settings(key,value) VALUES('channel_post_id',?) "
                      "ON CONFLICT(key) DO UPDATE SET value=excluded.value", (str(message.message_id),))
            c.commit()
    except Exception as exc:
        import logging
        logging.getLogger("brainsir").warning("Не удалось обновить пост канала: %s", exc)

def connect():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c

async def init_db():
    with connect() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS players(
            user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT,
            best_score INTEGER NOT NULL DEFAULT 0, games INTEGER NOT NULL DEFAULT 0)""")
        c.execute("CREATE TABLE IF NOT EXISTS app_settings(key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        c.execute("""CREATE TABLE IF NOT EXISTS sessions(
            session_id TEXT PRIMARY KEY, user_id INTEGER NOT NULL, questions_json TEXT NOT NULL,
            position INTEGER NOT NULL, score INTEGER NOT NULL, status TEXT NOT NULL,
            question_started REAL NOT NULL, created_at REAL NOT NULL)""")
        # Старые рекорды из 50-вопросной версии ранее ошибочно умножались на 10.
        # Возвращаем исходные значения один раз: например, 500 -> 50.
        # Это безопасно для текущей базы: после обновления никто ещё не играл новую игру.
        scaled_v2 = c.execute("SELECT value FROM app_settings WHERE key='score_scale_v2'").fetchone()
        corrected_v3 = c.execute("SELECT value FROM app_settings WHERE key='score_scale_v3_corrected'").fetchone()
        if scaled_v2 and not corrected_v3:
            c.execute("UPDATE players SET best_score=CAST(best_score / 10 AS INTEGER)")
            c.execute("INSERT INTO app_settings(key,value) VALUES('score_scale_v3_corrected','1')")
        # Старые незавершённые партии содержали только 50 вопросов.
        c.execute("UPDATE sessions SET status='interrupted' WHERE status='playing'")
        c.commit()

def telegram_user(request):
    raw = request.headers.get("X-Telegram-Init-Data", "")
    if not raw:
        return None
    try:
        data = dict(parse_qsl(raw, keep_blank_values=True))
        received_hash = data.pop("hash")
        check = "\n".join(f"{k}={v}" for k,v in sorted(data.items()))
        secret = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
        calculated = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(calculated, received_hash):
            return None
        if time.time() - int(data.get("auth_date", "0")) > 86400:
            return None
        return json.loads(data["user"])
    except Exception:
        return None

def require_user(request):
    user = telegram_user(request)
    if not user:
        raise web.HTTPUnauthorized(text="Открой игру через Telegram")
    return user

def view(q, pos, score):
    return {"position":pos+1,"total":TOTAL_QUESTIONS,"score":score,"topic":q["topic"],
            "question":q["question"],"options":q["options"],"seconds":15}

async def api_start(request):
    user = require_user(request)
    ids = list(range(len(QUESTIONS)))
    random.shuffle(ids)
    chosen = []
    for i in ids[:TOTAL_QUESTIONS]:
        question, opts, correct, topic = QUESTIONS[i]
        order = list(range(4))
        random.shuffle(order)
        chosen.append({"question":question,"options":[opts[x] for x in order],
                       "correct":order.index(correct),"topic":topic})
    sid, now = uuid.uuid4().hex, time.time()
    with connect() as c:
        inserted = c.execute("INSERT OR IGNORE INTO players(user_id,username,first_name) VALUES(?,?,?)",
            (int(user["id"]),user.get("username",""),user.get("first_name","Игрок"))).rowcount == 1
        c.execute("UPDATE players SET username=?,first_name=? WHERE user_id=?",
            (user.get("username",""),user.get("first_name","Игрок"),int(user["id"])))
        c.execute("INSERT INTO sessions VALUES(?,?,?,?,?,?,?,?)",
                  (sid,int(user["id"]),json.dumps(chosen,ensure_ascii=False),0,0,"playing",now,now))
        c.commit()
    if inserted:
        await update_channel_post()
    return web.json_response({"session_id":sid,"question":view(chosen[0],0,0)})

async def api_answer(request):
    user = require_user(request)
    try:
        body = await request.json()
        sid, answer = str(body["session_id"]), int(body["answer"])
        timed_out = bool(body.get("timeout", False))
    except Exception:
        raise web.HTTPBadRequest(text="Некорректный запрос")
    uid = int(user["id"])
    with connect() as c:
        row = c.execute("SELECT * FROM sessions WHERE session_id=? AND user_id=?",(sid,uid)).fetchone()
        if not row or row["status"] != "playing":
            raise web.HTTPBadRequest(text="Игра уже завершена или не найдена")
        questions = json.loads(row["questions_json"])
        pos, score = row["position"], row["score"]
        correct_index = questions[pos]["correct"]
        if timed_out or time.time() - row["question_started"] > 15.5:
            status = "timeout"
        elif answer == correct_index:
            score += 1
            status = "won" if pos == TOTAL_QUESTIONS - 1 else "playing"
        else:
            status = "wrong"
        if status == "playing":
            pos += 1
            # Даём клиенту время показать зелёный правильный ответ.
            c.execute("UPDATE sessions SET position=?,score=?,question_started=? WHERE session_id=?",
                      (pos,score,time.time()+0.85,sid))
            c.commit()
            return web.json_response({"status":"playing","correct_index":correct_index,
                                      "question":view(questions[pos],pos,score)})
        c.execute("UPDATE sessions SET score=?,status=? WHERE session_id=?",(score,status,sid))
        c.execute("UPDATE players SET games=games+1,best_score=MAX(best_score,?) WHERE user_id=?",(score,uid))
        best=c.execute("SELECT best_score FROM players WHERE user_id=?",(uid,)).fetchone()["best_score"]
        c.commit()
        return web.json_response({"status":status,"correct_index":correct_index,
                                  "score":score,"total":TOTAL_QUESTIONS,"best_score":best})

async def api_me(request):
    user = require_user(request)
    with connect() as c:
        row=c.execute("SELECT best_score,games FROM players WHERE user_id=?",(int(user["id"]),)).fetchone()
    return web.json_response({"best_score":row["best_score"] if row else 0,
                              "games":row["games"] if row else 0})

async def api_leaderboard(request):
    require_user(request)
    with connect() as c:
        total_players = c.execute(
            "SELECT COUNT(*) FROM players"
        ).fetchone()[0]

        rows = c.execute(
            "SELECT username,first_name,best_score FROM players WHERE games>0 "
            "ORDER BY best_score DESC, games ASC, user_id ASC LIMIT 10"
        ).fetchall()

    return web.json_response({
        "total_players": total_players,
        "leaders": [{
            "rank": i + 1,
            "name": ("@" + r["username"]) if r["username"] else (r["first_name"] or "Игрок"),
            "score": r["best_score"]
        } for i, r in enumerate(rows)]
    })
